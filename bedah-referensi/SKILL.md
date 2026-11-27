---
name: bedah-referensi
description: Tool Bedah Video Referensi (contact sheet, hard-cut, motion, audio LUFS). Mengukur ritme, durasi, budget naskah ID/EN, gaya subtitle, dan pola kamera video referensi 100% lokal sebelum produksi.
---

# Bedah Referensi (`/bedah-referensi`)

Skill ini mengukur angka-angka teknis dari video referensi secara objektif **sebelum** menulis naskah atau membuat animasi di skill mana pun (`stikman-cerita`, `3D-stickman`, `paperworld`, `voxelverse`, `3d-engineering-video`).

## Cara Pakai Cepat (Global via `render.py` atau Langsung)

Jalankan dari root repositori:

```bash
# 1. Bedah lengkap sekali jalan (probe + sheets + motion + audio -> laporan.json & sheet_*.jpg)
python render.py bedah video_referensi.mp4 out_bedah

# Dengan fps contact sheet lebih rapat (misal 2 fps atau 5 fps untuk aksi cepat):
python render.py bedah video_referensi.mp4 out_bedah --fps 2 --cols 5 --rows 4

# Atau panggil skrip langsung untuk sub-perintah tertentu:
python bedah-referensi/scripts/bedah.py probe  video_referensi.mp4
python bedah-referensi/scripts/bedah.py sheets video_referensi.mp4 out_bedah --fps 1 --cols 5 --rows 4
python bedah-referensi/scripts/bedah.py motion video_referensi.mp4
python bedah-referensi/scripts/bedah.py audio  video_referensi.mp4
```

### Opsi OCR Caption (jika `tesseract` + `pytesseract` terpasang lokal)
Untuk mengekstrak teks subtitle *burned-in* dan mengukur kecepatan bicara (`kata/detik`) dari pita caption tertentu (`top_px`, `height_px`), bisa memakai helper lokal yang sudah terbundel di `aset_global/blender_kit/ref_teardown.py`:

```bash
python aset_global/blender_kit/ref_teardown.py captions video_referensi.mp4 out_bedah/cap <top_px> <height_px> 15
python aset_global/blender_kit/ref_teardown.py pace     out_bedah/cap/ocr_words.json transcript.txt
```

## Alur Kerja Agen Saat User Memberi Video Referensi

1. **Jalankan `python render.py bedah <video> <folder_keluar>`** terlebih dahulu (otomatis mendeteksi `ffmpeg`/`ffprobe` di Windows).
2. **Baca `laporan.json`** untuk angka pasti:
   - Resolusi, FPS asli vs duplikat, durasi total.
   - **Deteksi kamera (`motion`):** daftar detik *hard cut*, burst gerakan cepat, dan persentase diam vs gerak. Jika `hard cut = 0`, artinya video memakai **gerakan kamera kontinu satu tarikan** (temuan penting, bukan kegagalan deteksi).
   - **Analisis audio (`audio`):** loudness (LUFS), jumlah jeda hening, pitch suara, dan estimasi musik latar. Jika tidak ditemukan jeda hening dan *noise floor* tetap tinggi (sekitar `-33 dB`), artinya ada musik latar atau SFX terus-menerus di bawah narasi.
3. **Buka contact sheet (`sheet_01.jpg`, dst.)** dan periksa 6–8 *keyframe* penting menggunakan `read_file` untuk membaca bahasa visual: set/latar, sudut kamera, palet warna, karakter, cara callout/tag muncul, gaya subtitle, dan struktur beat (hook → masalah → solusi/penjelasan → fakta mengejutkan → penutup).
4. **Jika perlu membedah gerakan mikro** di segmen tertentu (misalnya detik 0–5), ekstrak ulang dengan `--fps 5` agar setiap perubahan pose/kamera terlihat jelas.
5. **Hitung implikasi produksi siap pakai:**
   - **Budget panjang naskah** dari durasi target:
     - **Bahasa Indonesia:** `durasi (detik) × 6,3 suku kata`
     - **Bahasa Inggris:** `durasi (detik) × 2,7 kata`
   - **Gaya subtitle (`CAPTION_STYLE`):** `cards` (1–2 kata besar per kartu, ala `/3D-stickman` gaya `"kata"`) atau `phrases` (frasa utuh per baris).
   - **Pola kamera:** *hard cut* antar adegan atau gerakan kamera kontinu (*continuous tracking/orbit*).
   - **Struktur beat:** tabel detik mulai–selesai, estimasi kata, fungsi beat, dan aksi visual/kamera.
6. **Lanjutkan ke skill produksi** (`/3D-stickman`, `/paperworld`, `/stikman-cerita`, `/voxelverse`, atau `/3d-engineering-video`) menggunakan angka pacing, kamera, audio, dan beat dari hasil bedah ini.
