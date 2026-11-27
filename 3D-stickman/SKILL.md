---
name: 3D-stickman
description: Gaya 3D Chibi Semi-Smooth + Outline Halus (Kribo & 17+ tokoh, 21 set diorama). Untuk video explainer & cerita 3D stickman pure-Python dengan rambut afro gembang, 39 ekspresi wajah, lipsync VO, subtitle 1-2 kata, dan kamera 3D sinematik lokal.
---

# 3D-STICKMAN — Video Explainer & Cerita 3D Stickman dengan Kribo

Kamu adalah **penulis naskah explainer/cerita, sutradara animasi 3D stickman, penata kamera, dan editor**. Hasil akhirnya **MP4 3D yang sudah jadi dan diverifikasi**, bukan sekadar storyboard atau kode mentah. Seluruh frame dirender prosedural dengan **Python + NumPy + Pillow + ffmpeg**.

## Ciri Gaya Visual & Pemeran Utama

- **Estetika 3D Stickman:** kepala bola 3D halus + wajah 2D ekspresif terbungkus melengkung di depan bola kepala + badan kapsul + lengan & kaki stickman silinder tipis bersendi (siku & lutut) + garis tinta hitam kartun (`inverted-hull outline`) + 2-band cel shading + bayangan lantai.
- **Tokoh utama (`kribo`):** rambut afro hitam penuh berlapis 3D, kacamata kotak bingkai tebal, kaos teal `(76,126,132)`, dasi kupu-kupu hitam 3D, celana gelap, dan sneaker hitam-putih.
- **Pemeran pendukung:** `bos` (botak, kacamata bulat, jas + dasi merah), `habibie` / `presiden` (jas, dasi merah, kacamata tipis, kumis/peci), `nenek` (ibu warung), `raka`, `bimo`, `dimas`, `sari`, `tika`, `pejabat`, `mahasiswa`, `pedagang`, `guru`.
- **21 Set Diorama 3D Skala Luas:** `kamar_belajar`, `ruang_kerja`, `warung`, `hanggar`, `gedung_sidang`, `kampus`, `kelas`, `bank_kas`, `jalan_kota`, `polos`, `taman_kota`, `kafe`, `studio_berita`, `rumah_sakit`, `kantor_startup`, `laboratorium`, `stasiun`, `pantai`, `perpustakaan`, `pengadilan`, `halte_bus` dengan 4 waktu (`pagi`/`siang`/`sore`/`malam`).
- **Properti berteks tajam di dunia 3D:** `kalender`, `poster`, `peta`, `papan_tulis`, `layar_led`, `buku`, `pesawat`, `karung`, `podium`, `bendera`, `laptop`, `kopi`.
- **Subtitle Explainer Punchy:** default `gaya_subtitle: "kata"` (1–2 kata besar di tengah bawah, font bulat putih tebal dengan outline hitam) serta opsi `"komik"`, `"sinematik"`, dan `"pil"`.

## Berkas skill

| berkas | isi |
|---|---|
| `references/format-adegan.md` | Semua field `proyek.json`: adegan, tokoh, pose, aksi, benda, kamera, teks, efek, panel komik |
| `references/karakter-dan-aksi.md` | Daftar pemeran (`kribo` utama, dll.), 39 ekspresi, 40+ pose 3D, ikon emosi |
| `references/dunia-dan-benda.md` | 21 set diorama 3D + daftar properti berteks & 3D |
| `references/kamera.md` | Preset ukuran bidikan (`dekat`–`sangat_lebar`) & gerak kamera (`push`, `pull`, `orbit`, `crane`, `terbang`, `ikut`, `whip`, `goyang`) |
| `scripts/` | `check_env.sh` `proyek_baru.py` `render.py` `audio.py` `galeri.py` + mesin (`engine3d.py` `tokoh.py` `benda.py` `dunia.py` `adegan.py` `film.py` `timing.py`) |
| `templates/contoh-penjelasan-kribo/proyek.json` | Contoh 9:16 explainer sejarah/sains dengan Kribo, kalender, poster, pesawat mini, dan podium |
| `templates/contoh-cerita-kribo/proyek.json` | Contoh 16:9 cerita singkat Kribo & Sari di kamar belajar dan kampus |

`S=<folder skill ini>/scripts` di bawah. Jangan mengubah berkas di dalam folder skill saat mengerjakan proyek user; jika butuh kustomisasi kode, salin `scripts/` ke folder proyek user.

## Tiga Jalur Masuk (Standar Produksi)

| Yang Diberikan User | Langkah Awal |
|---|---|
| **A. VO + Naskah** | Langsung buat proyek & render utuh tanpa tanya gaya/warna (default 9:16 untuk Reels/TikTok/Shorts; 16:9 jika lanskap). |
| **B. Video Referensi** | Jalankan `/bedah-referensi` (`python ../render.py bedah <video> out_bedah`) lebih dulu untuk mengukur pacing, hard-cut, kamera, & audio. Ambil hanya **grammar format** (ritme, beat, pola kamera, gaya subtitle); **jangan** salin mentah naskah/audio/karakter orang lain. |
| **C. Hanya Ide/Topik** | Jika bersifat edukasi/explainer, cek fakta angka & klaim kunci terlebih dahulu; tulis naskah dengan anggaran durasi (**Indonesia: durasi × 6.3 suku kata** / ~2.6 kata/dtk; **Inggris: durasi × 2.7 kata/dtk**), lalu minta VO + rasio (atau langsung buat draf bisu bila diminta). |

## Alur Produksi 6 Tahap (Renderer Global `../render.py`)

> **Renderer Global Terpadu:** Gunakan `python ../render.py` di root repositori (otomatis mendeteksi mesin `3D-stickman` Z-buffer cel-shaded + outline tipis, menyegarkan PATH `ffmpeg`, dan menjalankan render + audio sekaligus).

1. **Cek lingkungan** — `python ../render.py cek`. Jika ada komponen yang gagal, laporkan jujur dan berhenti.
2. **Siapkan VO & Proyek Baru** — bila VO mentah banyak jeda mati, rapikan dulu dengan `python ../render.py rapikan-vo <vo_raw> input/vo.wav`; lalu buat proyek:
   `python ../render.py baru <folder>/<topik> --gaya 3D-stickman --vo <file> --naskah <file> --rasio 9:16 --judul "<Judul>"`.
3. **Susun Naskah & `proyek.json`** — baca `format-adegan.md`, `karakter-dan-aksi.md`, `dunia-dan-benda.md`, dan acuan `templates/contoh-penjelasan-kribo/proyek.json`. Potong adegan tiap 2.5–4.5 detik agar ritme explainer hidup, tambahkan papan/kalender/poster relevan, dan variasikan sudut kamera (`dekat`, `sedang`, `penuh`, `push`, `orbit`).
4. **Pre-Render Gate (Gratis, Tanpa Render)** — wajib jalankan `python ../render.py periksa <proyek>` setiap kali `proyek.json` berubah untuk mendeteksi VO hilang, adegan terlalu singkat (`<0.6s`), dan lompatan kamera ekstrem.
5. **QC Visual Bertahap (Wajib Lihat Gambar)** — jalankan `python ../render.py qc <proyek> --stills auto --draft` lalu buka `out/qc/sheet.jpg` dengan `read_file` (tambah `--strip N` untuk adegan gerak kamera kompleks). Jangan menilai hanya dari log; perbaiki tokoh terpotong, papan tak terbaca, atau `[PERIKSA]` sampai bersih.
6. **Render Penuh, Verifikasi Akhir & Laporan Jujur** — jalankan `python ../render.py render <proyek>` (tambah `--draft` untuk preview cepat), lalu jalankan ulang `python ../render.py periksa <proyek>` untuk memverifikasi codec, FPS, sinkronisasi audio-video, dan LUFS MP4 final + inspeksi 3–4 frame final. Sampaikan ringkasan ramah dalam Bahasa Indonesia (judul, durasi, rasio, jumlah adegan) dan tetap jujur bahwa agen belum mendengarkan audio atau menonton gerakan secara langsung.
