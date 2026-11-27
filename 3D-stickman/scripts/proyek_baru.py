# -*- coding: utf-8 -*-
"""
proyek_baru.py - siapkan folder proyek baru 3D-stickman (tidak pernah menimpa folder berisi).

  python3 proyek_baru.py <folder> [--vo file.mp3] [--naskah file.txt] [--rasio 9:16|16:9] [--judul "Judul"]
"""
import os, sys, json, re, shutil, argparse, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("folder")
ap.add_argument("--vo")
ap.add_argument("--naskah")
ap.add_argument("--rasio", default="9:16")
ap.add_argument("--judul", default="Cerita 3D Stickman Kribo")
ap.add_argument("--fps", type=int, default=30)
a = ap.parse_args()

if os.path.exists(a.folder) and os.listdir(a.folder):
    sys.exit(f"[GAGAL] {a.folder} sudah berisi file. Pilih folder baru.")
os.makedirs(os.path.join(a.folder, "input"), exist_ok=True)
vo = None
if a.vo:
    ext = os.path.splitext(a.vo)[1].lower() or ".mp3"
    vo = os.path.join("input", "vo" + ext).replace("\\", "/")
    shutil.copy(a.vo, os.path.join(a.folder, vo))
if a.naskah:
    raw = open(a.naskah, encoding="utf-8", errors="ignore").read()
    clean = re.sub(r"\[[^\]]{1,40}\]", "", raw)
    clean = re.sub(r"[ \t]+", " ", clean)
    open(os.path.join(a.folder, "input", "naskah.bersih.txt"), "w", encoding="utf-8").write(clean.strip() + "\n")
size = [1080, 1920] if a.rasio in ("9:16", "portrait", "vertikal") else [1920, 1080]
proj = {
    "mesin": "3D-stickman",
    "judul": a.judul,
    "ukuran": size,
    "fps": a.fps,
    "vo": vo,
    "musik": "auto",
    "mood_musik": "ceria",
    "subtitle": True,
    "gaya_subtitle": "kata",
    "tokoh": {"kribo": "kribo", "sari": "sari"},
    "adegan": [],
}
json.dump(proj, open(os.path.join(a.folder, "proyek.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("PROYEK", os.path.abspath(a.folder))
if vo:
    d = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", os.path.join(a.folder, vo)],
        capture_output=True, text=True,
    ).stdout.strip()
    print("DURASI_VO", d)
