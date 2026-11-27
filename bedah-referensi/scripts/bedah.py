# -*- coding: utf-8 -*-
"""
bedah.py - Alat bedah video referensi lokal (100% Python + NumPy + Pillow + ffmpeg).

Mengukur angka teknis dari video referensi tanpa perlu memutar video:
  * probe   : resolusi, codec, fps, durasi, stream audio
  * sheets  : ekstrak contact sheet berlabel detik (fps & grid kustom)
  * motion  : perubahan piksel/frame, deteksi hard-cut, frame duplikat, burst gerakan cepat
  * audio   : loudness (LUFS/LRA), jumlah jeda hening, stereo mid/side, indikasi musik latar, pitch suara
  * ringkas : jalankan semua (probe + sheets + motion + audio) -> simpan laporan.json & ringkasan.txt

Contoh pakai:
  python bedah.py ringkas ref.mp4 out_bedah --fps 1 --cols 5 --rows 4
  python bedah.py motion ref.mp4
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import wave
import numpy as np
from PIL import Image, ImageDraw


def _env_with_ffmpeg():
    env = os.environ.copy()
    if os.name == "nt":
        try:
            import winreg
            parts = []
            for root, sub in (
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                (winreg.HKEY_CURRENT_USER, r"Environment"),
            ):
                try:
                    with winreg.OpenKey(root, sub) as k:
                        val, _ = winreg.QueryValueEx(k, "Path")
                        if val:
                            parts.append(val)
                except OSError:
                    pass
            merged = ";".join([env.get("PATH", "")] + parts)
            seen, clean = set(), []
            for p in merged.split(";"):
                p = p.strip()
                if p and p.lower() not in seen:
                    seen.add(p.lower())
                    clean.append(p)
            env["PATH"] = ";".join(clean)
        except Exception:
            pass
    return env


def _run(cmd, env=None, text=True):
    return subprocess.run(cmd, capture_output=True, text=text, env=env or _env_with_ffmpeg())


def probe_video(video, env=None):
    env = env or _env_with_ffmpeg()
    res = _run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video], env=env)
    if res.returncode != 0:
        raise SystemExit(f"[ERROR] ffprobe gagal pada {video}: {res.stderr.strip()}")
    info = json.loads(res.stdout)
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        raise SystemExit(f"[ERROR] Stream video tidak ditemukan di {video}")
    num, den = v.get("r_frame_rate", "30/1").split("/")
    fps = float(num) / max(float(den), 1e-6)
    dur = float(info.get("format", {}).get("duration", v.get("duration", 0.0)))
    out = {
        "file": os.path.basename(video),
        "bytes": int(info.get("format", {}).get("size", 0)),
        "width": int(v["width"]),
        "height": int(v["height"]),
        "codec": v.get("codec_name", "?"),
        "fps": round(fps, 3),
        "duration_s": round(dur, 3),
        "nb_frames": int(v["nb_frames"]) if str(v.get("nb_frames", "")).isdigit() else int(round(dur * fps)),
        "audio": {
            "codec": a.get("codec_name", "?"),
            "sample_rate": int(a.get("sample_rate", 0)),
            "channels": int(a.get("channels", 0)),
        } if a else None,
    }
    return out


def make_sheets(video, out_dir, fps=1.0, cols=5, rows=4, width_tile=240, env=None):
    env = env or _env_with_ffmpeg()
    os.makedirs(out_dir, exist_ok=True)
    for old in glob.glob(os.path.join(out_dir, "s_*.jpg")) + glob.glob(os.path.join(out_dir, "sheet_*.jpg")):
        try:
            os.remove(old)
        except OSError:
            pass
    res = _run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", video,
        "-vf", f"fps={fps},scale={int(width_tile)}:-2",
        "-q:v", "3", os.path.join(out_dir, "s_%04d.jpg"),
    ], env=env)
    if res.returncode != 0:
        raise SystemExit(f"[ERROR] ffmpeg sheets gagal: {res.stderr.strip()}")
    files = sorted(glob.glob(os.path.join(out_dir, "s_*.jpg")))
    if not files:
        return {"frames": 0, "fps": fps, "sheets": []}
    per = max(1, int(cols) * int(rows))
    sheet_paths = []
    for n in range(0, len(files), per):
        tiles = [Image.open(f) for f in files[n:n + per]]
        tw, th = tiles[0].size
        sheet = Image.new("RGB", (cols * tw, rows * th), (18, 20, 26))
        dr = ImageDraw.Draw(sheet)
        for i, im in enumerate(tiles):
            x, y = (i % cols) * tw, (i // cols) * th
            sheet.paste(im, (x, y))
            label = f"{(n + i) / fps:.1f}s" if fps != 1.0 else f"{int(round((n + i) / fps))}s"
            dr.rectangle([x + 3, y + 3, x + 54, y + 20], fill=(16, 18, 24))
            dr.text((x + 7, y + 5), label, fill=(255, 224, 72))
            im.close()
        sp = os.path.join(out_dir, f"sheet_{n // per + 1:02d}.jpg")
        sheet.save(sp, quality=88)
        sheet_paths.append(sp)
    return {"frames": len(files), "fps": fps, "sheets": sheet_paths}


def analyze_motion(video, env=None):
    env = env or _env_with_ffmpeg()
    pr = probe_video(video, env=env)
    fps = float(pr["fps"])
    w_s = 90 if pr["height"] >= pr["width"] else 160
    h_s = 160 if pr["height"] >= pr["width"] else 90
    raw = _run([
        "ffmpeg", "-loglevel", "error", "-i", video,
        "-vf", f"scale={w_s}:{h_s},format=gray", "-f", "rawvideo", "-",
    ], env=env, text=False).stdout
    frame_sz = w_s * h_s
    n_f = len(raw) // frame_sz
    if n_f < 2:
        return {"frames": n_f, "fps": fps, "hard_cuts_s": [], "fast_moves": []}
    arr = np.frombuffer(raw[:n_f * frame_sz], dtype=np.uint8).reshape(n_f, h_s, w_s).astype(np.float32)
    diff = np.abs(arr[1:] - arr[:-1]).mean(axis=(1, 2))
    dup_pct = float(100.0 * (diff < 0.05).mean())
    spikes = [
        round((i + 1) / fps, 2)
        for i in range(1, len(diff) - 1)
        if diff[i] > 12.0 and diff[i] > 3.0 * max(float(diff[i - 1]), float(diff[i + 1]))
    ]
    smooth = np.convolve(diff, np.ones(9, dtype=np.float32) / 9.0, mode="same")
    hot = smooth > 3.0
    eps, i = [], 0
    while i < len(hot):
        if hot[i]:
            j = i
            while j < len(hot) and hot[j]:
                j += 1
            if (j - i) >= max(2, fps / 10.0):
                eps.append({"start_s": round(i / fps, 2), "dur_s": round((j - i) / fps, 2)})
            i = j
        else:
            i += 1
    return {
        "frames": int(n_f),
        "fps": round(fps, 2),
        "diff_median": round(float(np.median(diff)), 2),
        "diff_p95": round(float(np.percentile(diff, 95)), 2),
        "near_duplicate_pct": round(dup_pct, 1),
        "hard_cuts_s": spikes,
        "fast_moves_count": len(eps),
        "fast_moves": eps[:24],
        "split_pct": {
            "fast": round(float(100.0 * hot.mean()), 1),
            "drift": round(float(100.0 * ((smooth >= 0.6) & (~hot)).mean()), 1),
            "still": round(float(100.0 * (smooth < 0.6).mean()), 1),
        },
    }


def analyze_audio(video, env=None):
    env = env or _env_with_ffmpeg()
    pr = probe_video(video, env=env)
    if not pr.get("audio"):
        return {"has_audio": False}
    fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        _run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-ac", "2", "-ar", "22050", tmp_wav], env=env)
        eb = _run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-af", "ebur128", "-f", "null", "-"], env=env).stderr
        lufs_m = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", eb)
        lra_m = re.findall(r"LRA:\s+(-?[\d.]+)\s+LU", eb)
        sil_log = _run([
            "ffmpeg", "-hide_banner", "-nostats", "-i", video,
            "-af", "silencedetect=noise=-38dB:d=0.18", "-f", "null", "-",
        ], env=env).stderr
        pauses_n = sil_log.count("silence_end")
        with wave.open(tmp_wav, "rb") as w:
            sr = w.getframerate()
            x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(np.float64) / 32768.0
    finally:
        if os.path.exists(tmp_wav):
            try:
                os.remove(tmp_wav)
            except OSError:
                pass
    mid = (x[:, 0] + x[:, 1]) * 0.5
    side = (x[:, 0] - x[:, 1]) * 0.5
    db = lambda v: float(20.0 * np.log10(np.sqrt(np.mean(v * v)) + 1e-9))
    hop = max(1, int(sr * 0.05))
    e = np.array([db(mid[i:i + hop]) for i in range(0, max(1, len(mid) - hop), hop)], dtype=np.float64)
    pcts = {str(p): round(float(np.percentile(e, p)), 1) for p in (5, 25, 50, 90)}
    floors = [round(float(e[i:i + 40].min()), 1) for i in range(0, max(1, len(e) - 40), 40)]
    has_music_hint = (pauses_n == 0 and float(np.percentile(e, 5)) > -44.0) or (len(floors) >= 3 and float(np.median(floors)) > -42.0)

    loud_idx = np.where(e > np.percentile(e, 50))[0]
    f0 = []
    for idx in loud_idx[::3]:
        seg = mid[idx * hop:idx * hop + 2048]
        if len(seg) < 2048:
            continue
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, mode="full")[2047:]
        lo, hi = int(sr / 320), int(sr / 70)
        if hi < len(ac) and ac[0] > 1e-9:
            k = lo + int(np.argmax(ac[lo:hi]))
            if ac[k] > 0.35 * ac[0]:
                f0.append(sr / k)
    return {
        "has_audio": True,
        "lufs": float(lufs_m[-1]) if lufs_m else None,
        "lra_lu": float(lra_m[-1]) if lra_m else None,
        "pauses_ge_180ms": int(pauses_n),
        "mid_db": round(db(mid), 1),
        "side_db": round(db(side), 1),
        "level_percentiles_db": pcts,
        "window_floors_db": floors[:20],
        "music_bed_likely": bool(has_music_hint),
        "voice_pitch_median_hz": round(float(np.median(f0)), 1) if f0 else None,
    }


def ringkas_video(video, out_dir, fps=1.0, cols=5, rows=4):
    env = _env_with_ffmpeg()
    os.makedirs(out_dir, exist_ok=True)
    rep = {
        "probe": probe_video(video, env=env),
        "sheets": make_sheets(video, out_dir, fps=fps, cols=cols, rows=rows, env=env),
        "motion": analyze_motion(video, env=env),
        "audio": analyze_audio(video, env=env),
    }
    json_path = os.path.join(out_dir, "laporan.json")
    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(rep, fp, indent=2, ensure_ascii=False)

    p, m, a, s = rep["probe"], rep["motion"], rep["audio"], rep["sheets"]
    lines = [
        f"=== BEDAH REFERENSI: {p['file']} ===",
        f"Video   : {p['codec']} {p['width']}x{p['height']} | {p['fps']} fps | {p['duration_s']}s ({p['nb_frames']} frame)",
        f"Sheets  : {s['frames']} frame @ {s['fps']} fps -> {len(s['sheets'])} lembar ({', '.join(os.path.basename(x) for x in s['sheets'])})",
        f"Motion  : median diff {m['diff_median']} | p95 {m['diff_p95']} | duplikat {m['near_duplicate_pct']}%",
        f"Split   : cepat {m['split_pct']['fast']}% | drift {m['split_pct']['drift']}% | diam {m['split_pct']['still']}%",
        f"Cut (s) : {m['hard_cuts_s'] or 'tidak ada (kamera menerus)'}",
        f"Burst   : {m['fast_moves_count']} gerakan cepat -> {[x['start_s'] for x in m['fast_moves'][:12]]}",
    ]
    if a.get("has_audio"):
        lines += [
            f"Audio   : {a['lufs']} LUFS (LRA {a['lra_lu']} LU) | jeda>=0.18s: {a['pauses_ge_180ms']} | musik latar: {'YA (terindikasi)' if a['music_bed_likely'] else 'minim/hening'}",
            f"Suara   : mid {a['mid_db']} dB / side {a['side_db']} dB | pitch median {a['voice_pitch_median_hz']} Hz",
        ]
    else:
        lines.append("Audio   : tidak ada track audio")
    lines.append(f"Laporan : {json_path}")
    summary = "\n".join(lines)
    txt_path = os.path.join(out_dir, "ringkasan.txt")
    with open(txt_path, "w", encoding="utf-8") as fp:
        fp.write(summary + "\n")
    print(summary)
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(prog="bedah.py", description="Bedah video referensi lokal (probe, sheets, motion, audio, ringkas)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_p = sub.add_parser("probe", help="Tampilkan info teknis video")
    p_p.add_argument("video")

    p_s = sub.add_parser("sheets", help="Ekstrak contact sheet berlabel waktu")
    p_s.add_argument("video")
    p_s.add_argument("out_dir")
    p_s.add_argument("--fps", type=float, default=1.0)
    p_s.add_argument("--cols", type=int, default=5)
    p_s.add_argument("--rows", type=int, default=4)

    p_m = sub.add_parser("motion", help="Analisis hard-cut, frame duplikat, dan burst gerakan")
    p_m.add_argument("video")

    p_a = sub.add_parser("audio", help="Analisis loudness LUFS, jeda, musik latar, dan pitch")
    p_a.add_argument("video")

    p_r = sub.add_parser("ringkas", help="Jalankan semua analisis sekaligus + simpan laporan.json")
    p_r.add_argument("video")
    p_r.add_argument("out_dir", nargs="?", default=None)
    p_r.add_argument("--fps", type=float, default=1.0)
    p_r.add_argument("--cols", type=int, default=5)
    p_r.add_argument("--rows", type=int, default=4)

    args = ap.parse_args(argv)
    if args.cmd == "probe":
        print(json.dumps(probe_video(args.video), indent=2, ensure_ascii=False))
    elif args.cmd == "sheets":
        print(json.dumps(make_sheets(args.video, args.out_dir, args.fps, args.cols, args.rows), indent=2, ensure_ascii=False))
    elif args.cmd == "motion":
        print(json.dumps(analyze_motion(args.video), indent=2, ensure_ascii=False))
    elif args.cmd == "audio":
        print(json.dumps(analyze_audio(args.video), indent=2, ensure_ascii=False))
    elif args.cmd == "ringkas":
        out_dir = args.out_dir or (os.path.splitext(os.path.abspath(args.video))[0] + "_bedah")
        ringkas_video(args.video, out_dir, args.fps, args.cols, args.rows)


if __name__ == "__main__":
    main()
