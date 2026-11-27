# -*- coding: utf-8 -*-
"""
aset_global/cutaway_runner.py
Runner proyek JSON + generator proyek baru + audio mux bersama untuk 3 skill cutaway
pure-Python (strata3d, hydro3d, mechlab3d), sehingga ketiganya langsung bisa dipanggil
via `python render.py baru|qc|render|audio|periksa` di CPU lokal tanpa install Blender.
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

from .sinematografi import SinematografiRig, apply_cinematic_modifiers, terapkan_sinemaskop
from .studio_cutaway import (
    CutawayScene,
    _e3d,
    build_style_air,
    build_style_mesin,
    build_style_tanah,
    render_style_preview,
)
from .transisi import blend_transisi, norm_transisi

STYLE_MAP = {
    "strata3d": "tanah",
    "hydro3d": "air",
    "mechlab3d": "mesin",
}

DEFAULT_CAM = {
    "tanah": {"pos": [0.0, 0.45, 7.6], "target": [0.0, -0.25, -0.2], "fov": 42.0},
    "air": {"pos": [0.25, 1.05, 7.8], "target": [0.18, 0.05, -0.2], "fov": 42.0},
    "mesin": {"pos": [2.55, 3.05, 7.7], "target": [0.10, 1.55, -0.15], "fov": 40.0},
}


def _lerp(a, b, u):
    return a + (b - a) * u


def _lerp3(a, b, u):
    return [_lerp(a[i], b[i], u) for i in range(3)]


def render_scene_frame(proj, adegan, t_local, W, H, skill_name, aa=1.5):
    style = STYLE_MAP.get(skill_name, "mesin")
    sc = CutawayScene(style=style)
    if style == "tanah":
        build_style_tanah(sc, t=t_local)
    elif style == "air":
        build_style_air(sc, t=t_local)
    else:
        build_style_mesin(sc, t=t_local)

    # Override HUD / subtitle jika dispesifikasikan di adegan proyek.json
    if "hud_override" in adegan or "sub" in adegan or "subtitle" in adegan:
        if adegan.get("hapus_hud_default"):
            sc.hud_items = []
        sub_txt = adegan.get("subtitle", adegan.get("sub"))
        if sub_txt is not None:
            sc.hud_items = [x for x in sc.hud_items if x["kind"] != "subtitle"]
            gaya_sub = adegan.get("gaya_subtitle") or proj.get("gaya_subtitle") or (
                "cards" if style == "air" else "phrases"
            )
            sc.add_subtitle(sub_txt, gaya=gaya_sub, sorot=bool(adegan.get("sorot", False)))
        for h in adegan.get("hud") or []:
            k = h.get("jenis", "callout")
            if k == "gauge":
                sc.add_hud_gauge(h.get("pos", [0.2, 0.14]), nilai=h.get("nilai", 0.65),
                                 teks_nilai=str(h.get("teks_nilai", "2,2")),
                                 satuan=h.get("satuan", "BAR"), judul=h.get("judul", "TEKANAN"),
                                 size_frac=float(h.get("ukuran", 0.24)))
            elif k == "badge":
                sc.add_hud_badge(h.get("pos", [0.7, 0.12]), h.get("judul", "DATA"),
                                 sub=h.get("sub", ""), bg=tuple(h.get("bg", [24, 34, 58])),
                                 accent=tuple(h.get("aksen", [248, 198, 48])))
            elif k == "callout":
                sc.add_hud_callout(h.get("pos", [0.5, 0.35]), h.get("teks", "LABEL"),
                                   bg=tuple(h.get("bg", [214, 52, 46])), size=int(h.get("ukuran", 26)))

    # Sinematografi global (mendukung kamera.shot, kamera.gerak, orbit/spiral/crane/dolly_zoom, maupun awal->akhir)
    dcam = DEFAULT_CAM[style]
    kam = adegan.get("kamera") or {}
    dur = max(0.1, float(adegan.get("durasi", 4.0)))

    def _when(obj, key="t", default=0.0):
        if isinstance(obj, (int, float)):
            return float(obj)
        return float(obj[key]) if key in obj else float(default)

    def _resolve_tgt(spec, _t):
        return tuple(float(v) for v in spec.get("target", dcam["target"]))

    def _pose_spec(spec, prev=None, _t=0.0):
        if prev is None:
            pos = np.array(dcam["pos"], dtype=np.float32)
            tgt = np.array(dcam["target"], dtype=np.float32)
            fov, roll, blur = float(dcam["fov"]), 0.0, 0.0
        else:
            pos, tgt = np.array(prev[0], dtype=np.float32), np.array(prev[1], dtype=np.float32)
            fov, roll, blur = float(prev[2]), float(prev[3]), float(prev[4])
        if prev is None or "pos" in spec:
            roll, blur = 0.0, 0.0
        if "target" in spec:
            tgt = np.array(spec["target"], dtype=np.float32)
        return apply_cinematic_modifiers(pos, tgt, fov, roll, blur, spec)

    rig = SinematografiRig(kam, dur, _when, _pose_spec, _resolve_tgt)
    pos, tgt, fov, roll, blur = rig.eval(t_local)
    cam = _e3d.Cam3D(pos=tuple(pos), target=tuple(tgt), fov=fov, roll=roll, blur=blur)
    img = sc.render_frame(cam, W, H, t=t_local, aa=aa)
    if adegan.get("sinemaskop") or proj.get("sinemaskop"):
        img = terapkan_sinemaskop(img)
    return img


def make_new_project(skill_name, projdir, rasio="9:16", judul="Proyek Cutaway"):
    os.makedirs(os.path.join(projdir, "out"), exist_ok=True)
    style = STYLE_MAP.get(skill_name, "mesin")
    dcam = DEFAULT_CAM[style]
    pj = {
        "mesin": skill_name,
        "judul": judul,
        "rasio": rasio,
        "fps": 30,
        "gaya_subtitle": "cards" if style == "air" else "phrases",
        "adegan": [
            {
                "id": "S01",
                "durasi": 4.0,
                "subtitle": judul,
                "kamera": {
                    "awal": dcam,
                    "akhir": {
                        "pos": [dcam["pos"][0], dcam["pos"][1] + 0.08, dcam["pos"][2] - 0.35],
                        "target": dcam["target"],
                        "fov": dcam["fov"],
                    },
                },
            }
        ],
    }
    p_path = os.path.join(projdir, "proyek.json")
    with open(p_path, "w", encoding="utf-8") as fp:
        json.dump(pj, fp, indent=2, ensure_ascii=False)
        fp.write("\n")
    print(f"[OK] Proyek {skill_name} dibuat di {p_path}")


def cli_render(skill_name, argv=None):
    ap = argparse.ArgumentParser(description=f"Renderer pure-Python {skill_name}")
    ap.add_argument("proyek", help="Folder proyek berisi proyek.json")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--stills", default=None)
    ap.add_argument("--strip", default=None)
    ap.add_argument("--ulang", action="store_true")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--anggaran", type=float, default=None)
    args = ap.parse_args(argv)

    projdir = os.path.abspath(args.proyek)
    with open(os.path.join(projdir, "proyek.json"), encoding="utf-8") as fp:
        proj = json.load(fp)

    rasio = str(proj.get("rasio", "9:16"))
    if rasio == "16:9":
        W, H = (640, 360) if args.draft else (1280, 720)
    else:
        W, H = (540, 960) if args.draft else (1080, 1920)
    fps = int(proj.get("fps", 30))
    adegan_list = proj.get("adegan") or []
    out_dir = os.path.join(projdir, "out")
    os.makedirs(out_dir, exist_ok=True)

    if args.stills is not None:
        st_dir = os.path.join(out_dir, "stills")
        os.makedirs(st_dir, exist_ok=True)
        for i, ad in enumerate(adegan_list, 1):
            dur = float(ad.get("durasi", 3.0))
            im = render_scene_frame(proj, ad, dur * 0.5, W, H, skill_name, aa=1.25 if args.draft else 1.5)
            p_out = os.path.join(st_dir, f"S{i:02d}.png")
            im.save(p_out)
            print("[STILL]", p_out)
        return

    # Render animasi + transisi global antar adegan ke ffmpeg pipe -> video.mp4
    mp4_out = os.path.join(out_dir, "video.mp4")
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    cmd = [
        ffmpeg, "-y", "-f", "rawvideo", "-vcodec", "rawvideo",
        "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20" if not args.draft else "24",
        "-movflags", "+faststart", mp4_out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    spans = []
    cur_t = 0.0
    for ad in adegan_list:
        dur = max(0.1, float(ad.get("durasi", 3.0)))
        spans.append((cur_t, cur_t + dur, ad))
        cur_t += dur
    total_f = max(1, int(round(cur_t * fps)))
    aa_val = 1.25 if args.draft else 1.5
    for f_idx in range(total_f):
        T = f_idx / float(fps)
        si = 0
        while si + 1 < len(spans) and T >= spans[si + 1][0]:
            si += 1
        s0, _, ad_cur = spans[si]
        im = None
        if si + 1 < len(spans):
            nxt_s0, _, ad_nxt = spans[si + 1]
            tr = norm_transisi(ad_nxt.get("transisi", "potong"))
            if tr["dur"] > 0 and T >= nxt_s0 - tr["dur"] * 0.5:
                p = max(0.0, min(1.0, (T - (nxt_s0 - tr["dur"] * 0.5)) / tr["dur"]))
                A = render_scene_frame(proj, ad_cur, T - s0, W, H, skill_name, aa=aa_val)
                B = render_scene_frame(proj, ad_nxt, max(0.0, T - nxt_s0), W, H, skill_name, aa=aa_val)
                im = blend_transisi(A, B, p, tr)
        if im is None and si > 0:
            prev_s0, prev_s1, ad_prev = spans[si - 1]
            tr = norm_transisi(ad_cur.get("transisi", "potong"))
            if tr["dur"] > 0 and T < s0 + tr["dur"] * 0.5:
                p = max(0.0, min(1.0, (T - (s0 - tr["dur"] * 0.5)) / tr["dur"]))
                A = render_scene_frame(proj, ad_prev, min(prev_s1 - prev_s0, T - prev_s0), W, H, skill_name, aa=aa_val)
                B = render_scene_frame(proj, ad_cur, T - s0, W, H, skill_name, aa=aa_val)
                im = blend_transisi(A, B, p, tr)
        if im is None:
            im = render_scene_frame(proj, ad_cur, T - s0, W, H, skill_name, aa=aa_val)
        proc.stdin.write(im.tobytes())
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise SystemExit(f"[ERROR] ffmpeg gagal dengan kode {rc}")
    print(f"[OK] Render selesai ({total_f} frame) -> {mp4_out}")


def cli_audio(skill_name, argv=None):
    ap = argparse.ArgumentParser(description=f"Audio mux {skill_name}")
    ap.add_argument("proyek")
    ap.add_argument("--musik", default=None)
    ap.add_argument("--tanpa-sfx", action="store_true")
    args = ap.parse_args(argv)
    projdir = os.path.abspath(args.proyek)
    out_dir = os.path.join(projdir, "out")
    vid = os.path.join(out_dir, "video.mp4")
    final = os.path.join(out_dir, "final.mp4")
    if not os.path.exists(vid):
        raise SystemExit(f"[ERROR] {vid} belum ada. Jalankan render.py dulu.")
    vo = None
    for cand in ("vo.wav", "vo.mp3", "vo_proc.wav", os.path.join("audio", "vo.wav"), os.path.join("audio", "vo.mp3")):
        p = os.path.join(projdir, cand)
        if os.path.exists(p):
            vo = p
            break
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    if vo:
        subprocess.run([
            ffmpeg, "-y", "-i", vid, "-i", vo,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final,
        ], check=True)
    else:
        shutil.copy2(vid, final)
    print(f"[OK] Audio/Final -> {final}")


def cli_galeri(skill_name, argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default=None)
    args = ap.parse_args(argv)
    style = STYLE_MAP.get(skill_name, "mesin")
    out = args.output or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        skill_name, "assets", f"preview-{skill_name}.png",
    )
    render_style_preview(style, out, W=540, H=960)
    print(f"[OK] Preview {skill_name} -> {out}")
