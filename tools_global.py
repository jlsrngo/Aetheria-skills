# -*- coding: utf-8 -*-
"""
tools_global.py - Utilitas QA & VO global lintas semua skill Aetheria.

Fitur:
  1. rapikan_vo()     : rapikan jeda panjang VO (crossfade 4ms bebas klik), sesuaikan tempo halus (<=1.10x),
                        normalisasi loudness -14 LUFS + peak limiter 0.85 (standar YouTube Shorts/Reels).
  2. periksa_proyek() : cek proyek.json TANPA render (durasi, VO, adegan terlalu singkat/flash, lompatan
                        kamera mendadak, narasi kosong) + opsional QA video MP4 final (codec, FPS,
                        BT.709, LUFS, sinkronisasi audio-video).
"""
import glob
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import numpy as np


def _sh(cmd, env=None, text=True):
    return subprocess.run(cmd, capture_output=True, text=text, env=env)


def _ffprobe_json(path, env=None):
    res = _sh(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path], env=env)
    if res.returncode != 0:
        return None
    return json.loads(res.stdout)


def _measure_lufs(path, env=None):
    res = _sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128", "-f", "null", "-"], env=env)
    m = re.findall(r"I:\s+(-?[\d.]+)\s+LUFS", res.stderr)
    return float(m[-1]) if m else None


def rapikan_vo(in_path, out_wav, target_s=None, max_pause=0.30, env=None):
    """Rapikan VO mentah -> WAV 48kHz mono, jeda panjang dikompres halus, -14 LUFS."""
    sr = 48000
    hop = sr // 100  # 10 ms frame
    raw = _sh(["ffmpeg", "-loglevel", "error", "-i", in_path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], env=env, text=False).stdout
    if not raw:
        raise SystemExit(f"[ERROR] Gagal membaca audio VO: {in_path}")
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    n = len(x) // hop
    if n < 5:
        raise SystemExit(f"[ERROR] Durasi VO terlalu pendek: {in_path}")
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1))
    e = 20.0 * np.log10(rms + 1e-9)
    act = e > (np.percentile(e, 95) - 38.0)

    def _runs(a):
        out, i = [], 0
        while i < len(a):
            j = i
            while j < len(a) and a[j] == a[i]:
                j += 1
            out.append([bool(a[i]), i, j])
            i = j
        return out

    # Buang blip noise < 30ms & tutup celah < 60ms
    for v, i, j in _runs(act):
        if v and (j - i) < 3:
            act[i:j] = False
    for v, i, j in _runs(act):
        if (not v) and (j - i) < 6 and i > 0 and j < len(act):
            act[i:j] = True

    rr = _runs(act)
    voiced = [r for r in rr if r[0]]
    if not voiced:
        raise SystemExit(f"[ERROR] Tidak ada suara terdeteksi di: {in_path}")
    first, last = voiced[0][1], voiced[-1][2]

    pieces = []
    fade = int(sr * 0.004)
    n_pauses, raw_pause_s, new_pause_s = 0, 0.0, 0.0
    for v, i, j in rr:
        if j <= first or i >= last:
            continue
        if v:
            pieces.append(x[i * hop:j * hop])
            continue
        L = (j - i) / 100.0
        new_L = L if L <= 0.14 else min(float(max_pause), 0.14 + 0.24 * (L - 0.14))
        n_pauses += 1
        raw_pause_s += L
        new_pause_s += new_L
        k = int(new_L * sr * 0.5)
        a_seg = x[i * hop:i * hop + k].copy()
        b_seg = x[j * hop - k:j * hop].copy()
        if k > fade:
            a_seg[-fade:] *= np.linspace(1.0, 0.0, fade)
            b_seg[:fade] *= np.linspace(0.0, 1.0, fade)
        pieces.extend([a_seg, b_seg])

    y = np.concatenate([np.zeros(int(sr * 0.03))] + pieces + [np.zeros(int(sr * 0.12))])
    os.makedirs(os.path.dirname(os.path.abspath(out_wav)), exist_ok=True)
    fd1, tmp_tight = tempfile.mkstemp(suffix=".wav")
    fd2, tmp_tempo = tempfile.mkstemp(suffix=".wav")
    os.close(fd1)
    os.close(fd2)
    try:
        p = subprocess.Popen(
            ["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", tmp_tight],
            stdin=subprocess.PIPE, env=env,
        )
        p.communicate(y.astype(np.float32).tobytes())
        dur_tight = len(y) / sr
        tempo = 1.0
        if target_s and float(target_s) > 1.0:
            tempo = min(1.10, max(1.0, dur_tight / float(target_s)))
        _sh(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_tight, "-af", f"atempo={tempo:.4f}", "-ar", str(sr), tmp_tempo], env=env)
        cur_lufs = _measure_lufs(tmp_tempo, env=env) or -18.0
        gain_db = -13.2 - cur_lufs
        _sh([
            "ffmpeg", "-y", "-loglevel", "error", "-i", tmp_tempo,
            "-af", f"volume={gain_db:.2f}dB,alimiter=limit=0.85:attack=5:release=50:level=false",
            "-ar", str(sr), "-c:a", "pcm_s16le", out_wav,
        ], env=env)
        out_lufs = _measure_lufs(out_wav, env=env)
        info_out = _ffprobe_json(out_wav, env=env)
        dur_out = float(info_out["format"]["duration"]) if info_out else dur_tight / tempo
    finally:
        for f in (tmp_tight, tmp_tempo):
            if os.path.exists(f):
                try:
                    os.remove(f)
                except OSError:
                    pass

    rep = {
        "input": os.path.basename(in_path),
        "output": out_wav,
        "dur_raw_s": round(len(x) / sr, 2),
        "dur_tight_s": round(dur_tight, 2),
        "dur_out_s": round(dur_out, 2),
        "pauses_compressed": n_pauses,
        "pause_saved_s": round(raw_pause_s - new_pause_s, 2),
        "tempo": round(tempo, 4),
        "gain_db": round(gain_db, 2),
        "lufs_out": out_lufs,
    }
    print(json.dumps(rep, indent=2, ensure_ascii=False))
    return rep


def periksa_proyek(projdir, engine, video_path=None, env=None):
    """Pre-flight QA tanpa render untuk proyek.json + opsional pemeriksaan MP4 final."""
    pj_path = os.path.join(projdir, "proyek.json")
    if not os.path.exists(pj_path):
        raise SystemExit(f"[ERROR] proyek.json tidak ditemukan di: {projdir}")
    with open(pj_path, encoding="utf-8") as fp:
        proj = json.load(fp)

    warns, errs = [], []
    adegan = proj.get("adegan") or []
    fps = int(proj.get("fps", 30))
    rasio = proj.get("rasio", "16:9")
    vo_rel = proj.get("vo")
    vo_dur = None
    if vo_rel:
        vo_abs = vo_rel if os.path.isabs(vo_rel) else os.path.join(projdir, vo_rel)
        if not os.path.exists(vo_abs):
            errs.append(f"File VO tidak ditemukan: {vo_abs}")
        else:
            vi = _ffprobe_json(vo_abs, env=env)
            if vi:
                vo_dur = float(vi.get("format", {}).get("duration", 0.0))

    if not adegan:
        errs.append("Daftar `adegan` kosong!")

    prev_t = 0.0
    tot_est = 0.0
    for idx, sc in enumerate(adegan, 1):
        if not isinstance(sc, dict):
            errs.append(f"Adegan #{idx} bukan objek JSON")
            continue
        if not sc.get("latar"):
            warns.append(f"Adegan #{idx}: field `latar` kosong")
        nar = (sc.get("narasi") or "").strip()
        dur = sc.get("durasi")
        if dur is not None:
            d = float(dur)
            if d < 0.6:
                warns.append(f"Adegan #{idx}: durasi sangat singkat ({d:.2f}s) — cek risiko flash")
            tot_est += d
        else:
            words = len(re.findall(r"\S+", re.sub(r"\[[^\]]*\]", "", nar)))
            tot_est += max(2.6, words / 2.8 + 0.5)
        if "mulai" in sc:
            m = float(sc["mulai"])
            if idx > 1 and m < prev_t:
                errs.append(f"Adegan #{idx}: `mulai` ({m}s) mundur dari adegan sebelumnya ({prev_t}s)")
            prev_t = m
        # Cek lompatan posisi kamera ekstrem di dalam 1 adegan
        kam = sc.get("kamera") or {}
        if isinstance(kam, dict) and isinstance(kam.get("awal"), dict) and isinstance(kam.get("akhir"), dict):
            p0 = kam["awal"].get("pos")
            p1 = kam["akhir"].get("pos")
            if isinstance(p0, list) and isinstance(p1, list) and len(p0) == 3 and len(p1) == 3:
                dist = math.sqrt(sum((float(p1[k]) - float(p0[k])) ** 2 for k in range(3)))
                if dist > 14.0:
                    warns.append(f"Adegan #{idx}: perpindahan kamera sangat jauh ({dist:.1f} m) dalam 1 adegan")

    est_dur = vo_dur + float(proj.get("tail", 0.8)) if vo_dur else tot_est
    est_frames = int(math.ceil(est_dur * fps))

    print(f"=== PERIKSA PROYEK (PRE-RENDER QA) ===")
    print(f"Proyek   : {projdir}")
    print(f"Mesin    : {engine} | Rasio: {rasio} | FPS: {fps}")
    print(f"Adegan   : {len(adegan)} | VO: {f'{vo_dur:.2f}s' if vo_dur else 'tanpa VO'} | Estimasi total: ~{est_dur:.1f}s ({est_frames} frame)")
    if errs:
        print(f"ERROR ({len(errs)}):")
        for e in errs:
            print("  [X]", e)
    if warns:
        print(f"PERINGATAN ({len(warns)}):")
        for w in warns:
            print("  [!]", w)
    if not errs and not warns:
        print("Status   : OK — proyek.json siap dirender!")

    # Cek video MP4 final jika diminta atau ditemukan di out/
    if video_path is None:
        mp4s = sorted(glob.glob(os.path.join(projdir, "out", "*.mp4")), key=os.path.getmtime, reverse=True)
        mp4s = [m for m in mp4s if not os.path.basename(m).startswith("video_bisu")]
        video_path = mp4s[0] if mp4s else None

    if video_path and os.path.exists(video_path):
        info = _ffprobe_json(video_path, env=env)
        if info:
            v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
            a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), None)
            vdur = float(v.get("duration", info["format"].get("duration", 0.0))) if v else 0.0
            adur = float(a.get("duration", 0.0)) if a else 0.0
            sync_diff = abs(vdur - adur) if (v and a) else 0.0
            lufs = _measure_lufs(video_path, env=env) if a else None
            print(f"\n=== QA VIDEO FINAL: {os.path.basename(video_path)} ===")
            if v:
                num, den = v.get("r_frame_rate", "30/1").split("/")
                vfps = float(num) / max(float(den), 1e-6)
                print(f"Video    : {v.get('codec_name')} {v.get('width')}x{v.get('height')} | {vfps:.2f} fps | {vdur:.2f}s | pix={v.get('pix_fmt')} | color={v.get('color_space', 'unspecified')}")
            if a:
                print(f"Audio    : {a.get('codec_name')} {a.get('sample_rate')} Hz | {adur:.2f}s | sync diff: {sync_diff:.3f}s | loudness: {lufs} LUFS")
                if sync_diff > 0.25:
                    print(f"  [!] Selisih durasi audio-video cukup besar ({sync_diff:.2f}s)")
                if lufs is not None and (lufs < -22.0 or lufs > -9.0):
                    print(f"  [!] Loudness di luar rentang ideal Shorts/YouTube (-16 s/d -12 LUFS): {lufs} LUFS")
            else:
                print("Audio    : tidak ada stream audio")

    if errs:
        sys.exit(1)
