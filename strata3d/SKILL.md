---
name: strata3d
description: Gaya 3D Cutaway Tanah & Infrastruktur (lapisan tanah, rumah, sumur, septik). Untuk video explainer penampang tanah, pipa bawah tanah, fondasi, drainase, & maskot pekerja dengan hard-cut cepat dan subtitle frasa (pure-Python CPU + opsional Blender).
---

# Strata3D (`/strata3d`) — 3D Penampang Tanah & Infrastruktur

Skill khusus video explainer **penampang melintang tanah & infrastruktur sipil 3D** (septik, sumur & air tanah, fondasi bangunan, kabel/pipa bawah tanah, drainase, tambang, geologi).

## Ciri Khas Gaya Visual
- **Diorama potongan tanah berlapis** (rumput hijau → tanah coklat hangat → tanah dalam gelap) dengan latar langit cerah & pohon *low-poly*.
- **Bangunan/tangki cutaway** menampilkan isi lapisan di dalam (mis. buih/scum, air jernih, lumpur/sludge, aliran pipa).
- **Maskot pekerja** (helm kuning, rompi oranye reflektif), papan tanda putih (`DAY 5`, `WELL`), & kotak label kontras (navy/merah).
- **Pola kamera:** *hard-cut* tegas antar beat + subtitle gaya `phrases` putih bersih di bawah.

## Dua Mode Render (100% Lokal, Tanpa GPU Cloud)
1. **Pure-Python CPU (Default, Instan, Tanpa Blender):**
   ```bash
   python render.py baru proyek-tanah --gaya strata3d --rasio 9:16 --judul "Cara Kerja Septik"
   python render.py qc proyek-tanah --draft
   python render.py render proyek-tanah
   ```
   Menggunakan mesin bersama `aset_global/studio_cutaway.py` (True Z-Buffer pure-Python + HUD + subtitle).
2. **Blender Lokal (`bpy` / EEVEE / Cycles — Opsional):**
   Gunakan template [templates/video01-septic-system-en/septic_video.py](templates/video01-septic-system-en/septic_video.py) bersama kit bersama di `aset_global/blender_kit/` dan panduan `references/GUIDE.md`.

## Alur Kerja Standar
1. **Jalur Masuk:** (A) Naskah + VO → rapikan via `python render.py rapikan-vo`; (B) Video referensi → bedah dulu via `/bedah-referensi`; (C) Hanya topik → susun naskah (budget ID: `durasi × 6,3 suku kata`) & verifikasi fakta.
2. **Buat Proyek & QC Stills:** buat `proyek.json` (atau skrip Blender), jalankan `python render.py periksa <proyek>` & `python render.py qc <proyek> --draft`, lalu inspeksi gambarnya dengan `read_file`.
3. **Render Penuh & Mix Audio:** `python render.py render <proyek>` → MP4 H.264 + AAC 30 fps.
