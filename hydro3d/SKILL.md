---
name: hydro3d
description: Gaya 3D Cutaway Air, Kolam & Filter (air transparan, pompa, subtitle cards). Untuk video explainer kolam renang, sirkulasi fluida, filter pasir/RO, & aliran pipa dengan kamera kontinu satu tarikan (pure-Python CPU + opsional Blender).
---

# Hydro3D (`/hydro3d`) — 3D Sirkulasi Air, Kolam & Filter

Skill khusus video explainer **sistem air, fluida, kolam, pompa, dan filtrasi 3D** (kolam renang, filter pasir/RO, akuarium, bendungan/PLTA, radiator, irigasi, pengolahan limbah cair).

## Ciri Khas Gaya Visual
- **Diorama halaman rumah tropis** + **kolam/tangki cutaway transparan** dengan warna air yang dapat berubah dinamis (biru jernih ↔ hijau keruh/alga) dan permukaan air naik-turun.
- **Tabung filter & pompa cutaway** berisi media pasir/batu + partikel aliran fluida yang meluncur mulus di sepanjang pipa.
- **Pola kamera:** **gerakan kontinu satu tarikan** (meluncur dari wide halaman → close-up kolam → filter & pompa, dengan opsi pergantian pencahayaan siang ke senja).
- **Gaya subtitle:** **`cards`** (1–2 kata besar beroutline tebal, kata kunci disorot kuning emas).

## Dua Mode Render (100% Lokal, Tanpa GPU Cloud)
1. **Pure-Python CPU (Default, Instan, Tanpa Blender):**
   ```bash
   python render.py baru proyek-air --gaya hydro3d --rasio 9:16 --judul "Cara Kerja Filter Kolam"
   python render.py qc proyek-air --draft
   python render.py render proyek-air
   ```
   Menggunakan mesin bersama `aset_global/studio_cutaway.py` (True Z-Buffer pure-Python + HUD + subtitle `cards`).
2. **Blender Lokal (`bpy` / EEVEE / Cycles — Opsional):**
   Gunakan template [templates/video02-swimming-pool-id/pool_video.py](templates/video02-swimming-pool-id/pool_video.py) bersama kit bersama di `aset_global/blender_kit/` dan panduan `references/GUIDE.md`.

## Alur Kerja Standar
1. **Jalur Masuk:** (A) Naskah + VO → rapikan via `python render.py rapikan-vo`; (B) Video referensi → bedah dulu via `/bedah-referensi`; (C) Hanya topik → susun naskah (budget ID: `durasi × 6,3 suku kata`) & daftar kata kunci sorotan kuning.
2. **Buat Proyek & QC Stills:** buat `proyek.json` (atau skrip Blender), jalankan `python render.py periksa <proyek>` & `python render.py qc <proyek> --draft`, lalu inspeksi gambarnya dengan `read_file`.
3. **Render Penuh & Mix Audio:** `python render.py render <proyek>` → MP4 H.264 + AAC 30 fps.
