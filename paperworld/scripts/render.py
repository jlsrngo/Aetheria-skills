# -*- coding: utf-8 -*-
"""
render.py - render video bisu 3D PaperWorld (paralel, bisa dilanjutkan) atau stills QC.
"""
import os, sys, json, math, time, subprocess, argparse
from multiprocessing import get_context
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from film import Film
from paper import font, apply_paper_finish

_FILM = None
_OUT_W = None
_OUT_H = None
CHUNK = 90


def _init(projdir, rw, rh, ow, oh):
    global _FILM, _OUT_W, _OUT_H
    _FILM = Film(projdir, ukuran=(rw, rh))
    _OUT_W, _OUT_H = ow, oh


def _chunk(args):
    a, b, path = args
    F = _FILM
    tmp = path + ".tmp.mp4"
    cmd = [
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{_OUT_W}x{_OUT_H}", "-r", str(F.fps), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-pix_fmt", "yuv420p", "-r", str(F.fps), tmp,
    ]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(a, b):
        im = F.frame(f, finish=False).convert("RGB")
        if im.size != (_OUT_W, _OUT_H):
            im = im.resize((_OUT_W, _OUT_H), Image.Resampling.BILINEAR)
        im = apply_paper_finish(im)
        p.stdin.write(im.tobytes())
    p.stdin.close()
    p.wait()
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg chunk {path} gagal dengan kode {p.returncode}")
    os.replace(tmp, path)
    return path, b - a


def lembar(F, ims, labels, out, cols=None):
    cols = cols or (3 if F.W >= F.H else 4)
    tw = 640 if F.W >= F.H else 330
    th = int(tw * F.H / F.W)
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 8, rows * (th + 24) + (rows + 1) * 8), (32, 30, 28))
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x, y = 8 + c * (tw + 8), 8 + r * (th + 32)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y + 22))
        d.text((x + 4, y + 2), labels[i], font=font("teks", 18), fill=(255, 252, 246))
    sheet.save(out, quality=90)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("proyek")
    ap.add_argument("--stills")
    ap.add_argument("--strip", type=int)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--jobs", type=int, default=max(1, min(8, os.cpu_count() or 2)))
    ap.add_argument("--anggaran", type=int, default=0)
    ap.add_argument("--ulang", action="store_true")
    a = ap.parse_args()

    projdir = os.path.abspath(a.proyek)
    out = os.path.join(projdir, "out")
    os.makedirs(out, exist_ok=True)
    proj = json.load(open(os.path.join(projdir, "proyek.json"), encoding="utf-8"))
    ow, oh = [int(v) for v in proj.get("ukuran", [1920, 1080])]
    ss = 0.65 if a.draft else float(proj.get("supersample", 1.65))
    rw, rh = int(ow * ss) // 2 * 2, int(oh * ss) // 2 * 2

    F = Film(projdir, ukuran=(rw, rh))
    for w in F.warnings:
        print("[PERIKSA]", w)

    if a.stills or a.strip:
        qc = os.path.join(out, "qc")
        os.makedirs(qc, exist_ok=True)
        if a.strip:
            s = F.scenes[a.strip - 1]
            n = 9
            ts = [s.start + s.dur * (i / (n - 1)) * 0.97 for i in range(n)]
            ims = [F.frame(int(t * F.fps)) for t in ts]
            lembar(F, ims, [f"adegan {a.strip}  t={t:.2f}" for t in ts], os.path.join(qc, f"strip_{a.strip:02d}.jpg"), 3)
            print("STRIP", os.path.join(qc, f"strip_{a.strip:02d}.jpg"))
            return
        if a.stills == "auto":
            times = []
            for s in F.scenes:
                times += [s.start + 0.25, s.start + s.dur * 0.52, max(s.start, s.end - 0.30)]
        else:
            times = [float(x) for x in a.stills.split(",")]
        ims = [F.frame(min(F.N - 1, int(t * F.fps))) for t in times]
        for t, im in zip(times, ims):
            im.save(os.path.join(qc, f"t{t:06.2f}.jpg"), quality=88)
        lembar(F, ims, [f"{t:.2f}s" for t in times], os.path.join(qc, "sheet.jpg"))
        print("STILLS", os.path.join(qc, "sheet.jpg"))
        for i, s in enumerate(F.scenes):
            print(f"  adegan {i + 1:2d} {s.start:6.2f}-{s.end:6.2f}  {s.s.get('latar', s.s.get('tipe', ''))}")
        return

    t0 = time.time()
    json.dump(
        {"durasi": F.total, "fps": F.fps, "ukuran": [ow, oh], "vo": F.vo,
         "adegan": [{"mulai": round(s.start, 3), "selesai": round(s.end, 3), "latar": s.s.get("latar"), "musik": s.s.get("musik")} for s in F.scenes]},
        open(os.path.join(out, "timeline.json"), "w", encoding="utf-8"), indent=1,
    )
    json.dump([[round(t, 3), k, g] for t, k, g in F.events()], open(os.path.join(out, "events.json"), "w", encoding="utf-8"))

    wd = os.path.join(out, "work")
    if a.ulang and os.path.isdir(wd):
        import shutil
        shutil.rmtree(wd)
    os.makedirs(wd, exist_ok=True)
    jobs = [(i, min(F.N, i + CHUNK), os.path.join(wd, f"c{i // CHUNK:04d}.mp4")) for i in range(0, F.N, CHUNK)]
    todo = [j for j in jobs if not os.path.exists(j[2])]
    budget = a.anggaran or (150 if os.path.isdir("/mnt/user-data/outputs") else 0)
    print(f"render {F.N} frame ({F.total:.1f} dtk) {ow}x{oh}@{F.fps} | sisa {len(todo)}/{len(jobs)} potongan | {a.jobs} proses", flush=True)
    if todo:
        ctx = get_context("spawn")
        pool = ctx.Pool(min(a.jobs, len(todo)), initializer=_init, initargs=(projdir, rw, rh, ow, oh))
        it = pool.imap_unordered(_chunk, todo)
        done = 0
        try:
            while done < len(todo):
                if budget and time.time() - t0 > budget:
                    pool.terminate()
                    left = len([j for j in jobs if not os.path.exists(j[2])])
                    print(f"BELUM SELESAI {int(100 * (len(jobs) - left) / len(jobs))}% | sisa {left} potongan | jalankan perintah yang sama lagi")
                    sys.exit(2)
                try:
                    path, _ = it.next(timeout=5)
                    done += 1
                    print("  selesai", os.path.basename(path), flush=True)
                except Exception as e:
                    if e.__class__.__name__ == "TimeoutError":
                        continue
                    raise
        finally:
            pool.close()
    lst = os.path.join(wd, "list.txt")
    with open(lst, "w", encoding="utf-8") as fp:
        for j in jobs:
            fp.write(f"file '{j[2].replace(chr(92), '/')}'\n")
    dst = os.path.join(out, "video_bisu.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", dst], check=True)
    print(f"VIDEO_BISU {dst}  ({time.time() - t0:.0f} dtk)")


if __name__ == "__main__":
    main()
