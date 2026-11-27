---
name: paperworld
description: Gaya 3D Pop-Up Paper Craft (kertas berlapis, buku lipat, shadow map). Untuk video cerita & diorama kertas karton 3D pure-Python dengan pintu pop-up, tekstur kertas hangat, kamera 3D bebas, serta tokoh Luna, Kribo, Nadia, dan Kucing Kertas.
---

# PaperWorld — Sutradara Video Animasi 3D Pop-Up Paper Craft

Skill ini menghasilkan video animasi **3D Pop-Up Paper Craft** yang utuh hanya dengan **Python (NumPy + Pillow) + ffmpeg** — tanpa Blender, Unity, atau GPU renderer eksternal. Seluruh set diorama, pintu melengkung 3D, menara jam, furnitur, prop meja kerajinan, dan tokoh dibuat dari **kepingan karton berlapis (*layered paper cutout*)** bersudut tepi putih tipis, pencahayaan studio hangat matte, tekstur serat kertas halus, bayangan datar pada lantai/dinding, dan mekanisme engsel *pop-up* (`lipat` / `buka_pintu` / `pop_up`).

> [!IMPORTANT]
> Gunakan kamera 3D nyata (`orbit`, `crane`, `terbang`, `push`, `pull`, `ikut`) + engsel animasi `animasi_opsi` (`mode_pintu`, `buka_pintu`, `buka_pintu_kanan`, `pop_jam`, `pintu_tengah_pop`, `pintu_buka_semua`, `pop_notif`) serta pemeriksaan visual `--stills auto` via `read_file` **sebelum** render penuh.

## Prasyarat Lingkungan

Jalankan pengecekan sekali pada lingkungan kerja:

```bash
bash scripts/check_env.sh
```

Di Windows dengan Git Bash, jalankan `"C:\Program Files\Git\bin\bash.exe" scripts/check_env.sh`. Kebutuhan minimum:
- **Python 3.9+**, **NumPy**, **Pillow** (`PIL`)
- **ffmpeg** + **ffprobe** dengan encoder `libx264`, `aac`, serta filter `sidechaincompress`
- **Font** sudah terpasang di [assets/fonts/](assets/fonts/)

## Tiga Jalur Masuk (Standar Produksi)

| Yang Diberikan User | Langkah Awal |
|---|---|
| **A. VO + Naskah** | Langsung buat proyek & render utuh (default 9:16 untuk Reels/TikTok/Shorts; 16:9 untuk lanskap). |
| **B. Video Referensi** | Bedah dulu dengan `/bedah-referensi` (`python ../render.py bedah <video> out_bedah`) untuk mengukur durasi, cut, gerakan kamera, & tempo. Ikuti hanya grammar formatnya; jangan salin mentah footage/audio/naskah pihak lain. |
| **C. Hanya Ide/Topik** | Tulis naskah dengan anggaran durasi (**Indonesia: durasi × 6.3 suku kata**; **Inggris: durasi × 2.7 kata**), cek fakta bila edukatif, lalu minta VO atau buat draf bisu sesuai permintaan. |

## Alur Kerja 6 Tahap (Renderer Global `../render.py`)

> **Renderer Global Terpadu:** Gunakan `python ../render.py` di root repositori (otomatis mendeteksi mesin `paperworld`, menyegarkan PATH `ffmpeg`, dan menjalankan render + audio sekaligus). Jika skill dipakai berdiri sendiri, gunakan `scripts/render.py` & `scripts/audio.py`.

### 1. Cek Lingkungan & Buat Folder Proyek Baru
```bash
python ../render.py cek
python ../render.py baru <nama-proyek> --gaya paperworld
```
Menghasilkan folder proyek lengkap (`proyek.json` dengan `"mesin": "paperworld"`, `input/`, `out/`) dengan cast bawaan `luna`, `kribo`, `nadia`, dan `kucing`. Atau salin salah satu template:
- [templates/contoh-satu-pintu-lagi/proyek.json](templates/contoh-satu-pintu-lagi/proyek.json) — vertikal `9:16` bergaya galeri motion pop-up (`meja_hp` → `kota_jam` → `ruang_pintu` → `panggung_kertas` → `labirin_pintu` → `lipat_meja`).
- [templates/contoh-cerita-kribo/proyek.json](templates/contoh-cerita-kribo/proyek.json) — horizontal `16:9` kisah Kribo, Nadia, dan Luna melintasi pintu-pintu ajaib.

### 2. Siapkan Voice-Over (Opsional)
Letakkan berkas suara `input/vo.mp3` atau `input/vo.m4a` (bisa dirapikan jeda & loudness `-14 LUFS` lewat `python ../render.py rapikan-vo <vo_raw> input/vo.wav`) lalu isi `"vo": "input/vo.wav"` pada `proyek.json`. Jika `"vo": null`, durasi tiap adegan mengikuti `"durasi"` atau panjang narasi (`~135 wpm`).

### 3. Susun Naskah, Koreografi & Pre-Render Gate
Baca panduan referensi sesuai kebutuhan:
- [cerita-dan-naskah.md](references/cerita-dan-naskah.md) — struktur naratif, pembagian adegan, aturan `ekor`, subtitle `kertas`, dan VO.
- [format-adegan.md](references/format-adegan.md) — skema lengkap `proyek.json`, `animasi_opsi`, `benda`, `balon`, `teks`, `efek`, dan `sfx`.
- [karakter-dan-aksi.md](references/karakter-dan-aksi.md) — 13 preset tokoh (`luna`, `kribo`, `nadia`, `kucing`, dll.), 21 ekspresi, 25 pose, serta animasi masuk `dari: "lipat"`.
- [dunia-dan-benda.md](references/dunia-dan-benda.md) — 12 set diorama 3D PaperWorld beserta koordinat landmark, 11 prop 3D, dan opsi animasinya.
- [kamera.md](references/kamera.md) — gerakan kamera 3D (`push`, `pull`, `orbit`, `crane`, `terbang`, `ikut`, `potong`, `whip`), ukuran bidikan, dan transisi.

Setelah `proyek.json` ditulis, wajib jalankan **pre-render QA tanpa render**:
```bash
python ../render.py periksa <folder-proyek>
```

### 4. Uji Komposisi & Lembar QC (Wajib Lihat Gambar)
Render frame sampel cepat terlebih dahulu:
```bash
python ../render.py qc <folder-proyek> --stills auto --draft
# Untuk aksi pintu/lipatan cepat, cek juga motion strip:
python ../render.py qc <folder-proyek> --strip 1 --draft
```
Periksa `out/qc/sheet.jpg` dengan `read_file`! Pastikan tidak ada tokoh terpotong tepi, terhalang dinding pintu, melayang di luar pijakan, atau kartu teks bertabrakan dengan kamera.

### 5. Render Penuh, Verifikasi Final & Laporan Jujur
```bash
python ../render.py render <folder-proyek> --ulang
# atau mode cepat:
python ../render.py render <folder-proyek> --draft --ulang
# cek QA MP4 final (codec, FPS, sync audio-video, LUFS):
python ../render.py periksa <folder-proyek>
```
Atau gunakan `--musik none --tanpa-sfx` bila memakai audio master yang sudah lengkap di `input/vo.*`.
Pastikan tercetak **`FINAL OK`**, inspeksi 3–4 frame dari MP4 final, lalu sampaikan laporan ringkas dan jujur (termasuk bahwa agen tidak mendengarkan audio/menonton gerak langsung).

## Galeri Karakter
Untuk merender ulang lembar referensi tokoh ([assets/galeri-karakter.png](assets/galeri-karakter.png)):
```bash
python ../render.py galeri paperworld paperworld/assets/galeri-karakter.png
```
