---
name: paperworld
description: Memproduksi video animasi 3D Pop-Up Paper Craft / diorama karton berlapis (paper cutout 3D, pintu pop-up, buku lipat, karakter karton berlapis, kamera 3D bebas) dengan rendering NumPy + Pillow + ffmpeg murni dalam Python. Gunakan saat pengguna meminta video animasi gaya paper craft 3D, buku pop-up, diorama kertas berlapis, atau alur cerita dengan tokoh karton 3D seperti Luna, Kribo, Nadia, dan Kucing Kertas.
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

## Alur Kerja Lengkap (Pakai Renderer Global `../render.py`)

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
Letakkan berkas suara `input/vo.mp3` atau `input/vo.m4a` dan isi `"vo": "input/vo.m4a"` pada `proyek.json`. Jika `"vo": null`, durasi tiap adegan mengikuti `"durasi"` atau panjang narasi (`~135 wpm`).

### 3. Susun Naskah & Koreografi `proyek.json`
Baca panduan referensi sesuai kebutuhan:
- [cerita-dan-naskah.md](references/cerita-dan-naskah.md) — struktur naratif, pembagian adegan, aturan `ekor`, subtitle `kertas`, dan VO.
- [format-adegan.md](references/format-adegan.md) — skema lengkap `proyek.json`, `animasi_opsi`, `benda`, `balon`, `teks`, `efek`, dan `sfx`.
- [karakter-dan-aksi.md](references/karakter-dan-aksi.md) — 13 preset tokoh (`luna`, `kribo`, `nadia`, `kucing`, dll.), 21 ekspresi, 25 pose, serta animasi masuk `dari: "lipat"`.
- [dunia-dan-benda.md](references/dunia-dan-benda.md) — 12 set diorama 3D PaperWorld beserta koordinat landmark, 11 prop 3D, dan opsi animasinya.
- [kamera.md](references/kamera.md) — gerakan kamera 3D (`push`, `pull`, `orbit`, `crane`, `terbang`, `ikut`, `potong`, `whip`), ukuran bidikan, dan transisi.

### 4. Uji Komposisi & Lembar QC (Wajib)
Render frame sampel cepat terlebih dahulu:
```bash
python ../render.py qc <folder-proyek> --stills auto --draft
```
Periksa `out/qc/sheet.jpg` dengan `read_file`! Pastikan tidak ada tokoh terpotong tepi, terhalang dinding pintu, melayang di luar pijakan, atau kartu teks bertabrakan dengan kamera.

### 5. Render Penuh & Mixing Audio (1 Perintah Global)
```bash
python ../render.py render <folder-proyek> --ulang
# atau mode cepat:
python ../render.py render <folder-proyek> --draft --ulang
```
Atau gunakan `--musik none --tanpa-sfx` bila memakai audio master yang sudah lengkap di `input/vo.*`.
Skrip akan mencetak **`FINAL OK`** beserta ringkasan resolusi, fps, codec, dan durasi akhir di `out/`.

## Galeri Karakter
Untuk merender ulang lembar referensi tokoh ([assets/galeri-karakter.png](assets/galeri-karakter.png)):
```bash
python ../render.py galeri paperworld paperworld/assets/galeri-karakter.png
```
