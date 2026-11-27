---
name: mechlab3d
description: Gaya 3D Cutaway Mesin & Logam PBR (bengkel navy, piston, turbo, HUD gauge). Untuk video explainer mesin otomotif, mekanika, & alat teknik bergaya CR-V Engine dengan cutaway kuning amber dan strip HUD BAR/RPM (pure-Python CPU + opsional Blender).
---

# MechLab3D (`/mechlab3d`) — 3D Studio Mekanik & Mesin Logam

Skill khusus video explainer **mesin, otomotif, dan mekanika teknik 3D** bergaya CR-V Engine (mesin 4-silinder, turbo, transmisi, rem, pompa hidrolik, turbin pesawat, motor listrik, jam mekanik).

## Ciri Khas Gaya Visual
- **Studio bengkel navy gelap + lantai abu + garis kuning horisontal**, dengan mesin/komponen diletakkan di atas *stand* baja biru.
- **Material logam mengkilap** (aluminium, baja tempa, krom, besi gelap) dipadukan dengan **bibir potongan cutaway warna kuning amber** agar setiap celah internal terbaca jelas.
- **Animasi mekanik presisi:** poros engkol (*crankshaft*), *conrod*, piston beralur ring, batang & per katup, turbo, serta kilatan api pembakaran oranye saat TDC — seluruhnya bergerak dari satu kurva sudut yang konsisten.
- **Strip HUD atas (8–25% dari atas):** `dial_gauge` (BAR / RPM / °C) di kiri atas + kartu judul (`MUSUH 1: TEKANAN`) di kanan atas + callout merah (`RETAK`, `BENGKOK`, `2,2 BAR`) + subtitle putih tegas.

## Dua Mode Render (100% Lokal, Tanpa GPU Cloud)
1. **Pure-Python CPU (Default, Instan, Tanpa Blender):**
   ```bash
   python render.py baru proyek-mesin --gaya mechlab3d --rasio 9:16 --judul "Cara Kerja Mesin Turbo"
   python render.py qc proyek-mesin --draft
   python render.py render proyek-mesin
   ```
   Menggunakan mesin bersama `aset_global/studio_cutaway.py` (True Z-Buffer pure-Python mode `studio_metal` tanpa outline kartun + HUD gauge & callout tajam).
2. **Blender Lokal (`bpy` / EEVEE / Cycles — Opsional):**
   Gunakan template [templates/video03-crv-engine-id/engine_video.py](templates/video03-crv-engine-id/engine_video.py) bersama kit bersama di `aset_global/blender_kit/` (cek sebelum render dengan `scene_check.py`) dan panduan `references/GUIDE.md`.

## Alur Kerja Standar
1. **Jalur Masuk:** (A) Naskah + VO → rapikan via `python render.py rapikan-vo`; (B) Video referensi → bedah dulu via `/bedah-referensi`; (C) Hanya topik → susun tabel fakta angka (RPM, BAR, suhu) + naskah (budget ID: `durasi × 6,3 suku kata`).
2. **Buat Proyek & QC Stills:** buat `proyek.json` (atau skrip Blender), jalankan `python render.py periksa <proyek>` & `python render.py qc <proyek> --draft`, lalu inspeksi gambarnya dengan `read_file`.
3. **Render Penuh & Mix Audio:** `python render.py render <proyek>` → MP4 H.264 + AAC 30 fps.
