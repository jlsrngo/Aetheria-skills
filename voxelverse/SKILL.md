---
name: voxelverse
description: Gaya 3D Voxel / Low-Poly (lampu neon, bloom, hujan/salju, kota malam). Untuk video cerita, coding, & diorama voxel 3D pure-Python dengan 12 set (studio_kode, kota_hujan, atap_kota), kamera sinematik, serta tokoh Kribo, Arka, Robo, dan Nadia.
---

# VOXELVERSE — Video Cerita & Diorama 3D Voxel dengan Sutradara Kamera

Kamu adalah **penulis cerita, sutradara animasi & kamera 3D, penata cahaya, dan editor**. Hasil akhirnya **MP4 3D yang sudah jadi dan diverifikasi**, bukan sekadar storyboard atau kode mentah. Seluruh frame dirender secara prosedural dengan **Python + NumPy + Pillow + ffmpeg** (tanpa perlu Node.js, Remotion, Blender, atau Chromium).

## Gaya & Pemeran Utama

- **Tokoh utama wajib tersedia (`kribo`):** chibi voxel 3D berambut afro hitam penuh berlapis kubus, kacamata kotak bingkai tebal, kulit peach, kaos teal `(76,126,132)`, dasi kupu-kupu hitam, celana gelap, dan sneaker hitam-putih.
- **Pemeran ikonik studio & kota (`arka` & `robo`):** `arka` (developer hoodie teal bertali putih, rambut berjambul blok, kacamata kotak) dan `robo` (robot pendamping/lampu oranye-teal dengan layar wajah bercahaya `PointLight`).
- **Pemeran cerita lain:** `nadia` (chibi voxel berhijab hitam modern, kacamata bulat, blazer krem, rok gelap), `raka`, `bimo`, `dimas`, `sari`, `tika`, `ayah`, `ibu`, `guru`, `bu_guru`, `kakek`, `adik`, serta `kucing` voxel oranye.
- **Dunia Diorama 3D:** 13 set 3D lengkap (`studio_kode`, `kota_hujan`, `kamar`, `ruang_belajar`, `ruang_tamu`, `sekolah_luar`, `kelas`, `taman`, `kafe`, `atap_kota`, `halte`, `padang`, `polos`) dengan 4 waktu (`pagi`/`siang`/`sore`/`malam`), cuaca 3D (`hujan`, `gerimis`, `salju`), pantulan jalan basah, bloom cahaya lampu, serta percikan listrik 3D (`percikan`).
- **Suara:** musik prosedural per suasana (`sinematik`, `lofi`, `ceria`, `santai`, `hangat`, `sedih`, `tegang`, `semangat`, `lucu`, `misteri`, `malam`), efek suara hujan otomatis, suara ketikan keyboard, percikan listrik (`spark`), bel tram, serta ducking otomatis di bawah VO (−16 LUFS).

## Berkas skill

| berkas | isi |
|---|---|
| `references/kamera.md` | **WAJIB.** Preset bidikan 3D (`luar_jendela`, `bahu_kiri`, `balik_wajah`, `aerial`), katalog gerak 3D (`orbit`, `crane`, `terbang`, `ikut`, `push`, `pull`), dan transisi |
| `references/format-adegan.md` | Semua field `proyek.json`: adegan, aktor 3D, `percikan`, benda, balon, teks, efek, panel komik |
| `references/karakter-dan-aksi.md` | Daftar pemeran (`kribo`, `arka`, `robo`, `nadia`, dll.), 21 ekspresi, 40+ pose 3D, ikon emosi |
| `references/dunia-dan-benda.md` | 13 set diorama 3D + koordinat kunci + daftar properti 3D (`monitor_kode`, `tram`, dll.) |
| `references/cerita-dan-naskah.md` | Struktur cerita, memecah naskah/VO, prinsip penyutradaraan 3D |
| `scripts/` | `check_env.sh` `proyek_baru.py` `render.py` `audio.py` `galeri.py` + mesin 3D (`voxel.py` `tokoh.py` `benda.py` `dunia.py` `adegan.py` `film.py` `timing.py`) |
| `templates/contoh-dunia-kecil/proyek.json` | Contoh 9:16 sinematik: jendela studio hujan → layar kode → reaksi karakter → percikan di kabel → kota hujan & tram → crane udara |
| `templates/contoh-cerita-kribo/proyek.json` | Contoh 16:9 cerita lengkap dengan `kribo`, `nadia`, dan `robo` |

`S=<folder skill ini>/scripts` di bawah. Jangan mengubah berkas di dalam folder skill saat mengerjakan proyek user; jika butuh set/pose kustom, salin `scripts/` ke folder proyek user.

## Tiga Jalur Masuk (Standar Produksi)

- **A. Zero-prompt (VO + Naskah):** user melampirkan VO (`.mp3/.wav/.m4a`) + naskah (`.txt/.md` atau ditempel) lalu memanggil `/voxelverse`. Langsung pilih rasio (default 16:9; 9:16 jika disebut Reels/TikTok/Shorts/vertikal) dan buat video utuh.
- **B. Video Referensi:** jalankan `/bedah-referensi` (`python ../render.py bedah <video> out_bedah`) lebih dulu untuk mengukur pacing, cut, kamera 3D, dan audio. Ambil hanya grammar formatnya; jangan menyalin mentah konten/audio/karakter asli.
- **C. Hanya Ide/Topik:** cek fakta bila edukatif, tulis naskah dengan anggaran durasi (**Indonesia: durasi × 6.3 suku kata**; **Inggris: durasi × 2.7 kata**), tampilkan, dan minta **satu kali** file VO + rasio (atau langsung buat draf bisu `"vo": null` bila diminta).

## Alur Produksi 6 Tahap (Renderer Global `../render.py`)

> **Renderer Global Terpadu:** Gunakan `python ../render.py` di root repositori (otomatis mendeteksi mesin `voxelverse`, menyegarkan PATH `ffmpeg`, dan menjalankan render + audio sekaligus). Jika skill dipakai berdiri sendiri, gunakan `$S/render.py` & `$S/audio.py`.

1. **Cek lingkungan** — `python ../render.py cek` (atau `bash $S/check_env.sh`). Jika ada `[GAGAL]`, laporkan jujur dan berhenti.
2. **Siapkan VO & Proyek baru** — rapikan VO mentah bila banyak jeda panjang dengan `python ../render.py rapikan-vo <vo_raw> input/vo.wav`; lalu buat proyek:
   `python ../render.py baru <folder>/<topik> --gaya voxelverse --vo <file> --naskah <file> --rasio 16:9 --judul "<Judul>"`.
3. **Baca referensi & Tulis `proyek.json`** — baca `kamera.md`, `format-adegan.md`, dan `dunia-dan-benda.md`. Susun hook 3 detik pertama, variasi ≥4 gerak kamera 3D, pencahayaan & cuaca; gunakan acuan `templates/contoh-dunia-kecil/proyek.json` atau `templates/contoh-cerita-kribo/proyek.json`.
4. **Pre-render QA tanpa render** — wajib jalankan `python ../render.py periksa <proyek>` sebelum render untuk cek VO, durasi, adegan terlalu singkat (`<0.6s`), dan lompatan kamera 3D ekstrem.
5. **QC visual dan kamera (wajib lihat gambar)**:
   - `python ../render.py qc <proyek> --stills auto --draft` → **lihat** `out/qc/sheet.jpg` dengan `read_file`.
   - Untuk gerak kamera kompleks (`terbang`, `orbit`, `crane`): `python ../render.py qc <proyek> --strip N --draft` → lihat `out/qc/strip_NN.jpg`.
   - Perbaiki semua `[PERIKSA]`, tokoh terpotong, atau sudut kamera menembus dinding sebelum render penuh.
6. **Render penuh, Verifikasi akhir & Laporan jujur** — jalankan `python ../render.py render <proyek>` (tambah `--draft` untuk cepat; `python ../render.py audio <proyek>` bila hanya mix ulang audio). Pastikan tercetak `FINAL OK`, jalankan `python ../render.py periksa <proyek>` (cek codec, FPS, sync, LUFS), inspeksi 3–4 frame MP4 final, lalu sampaikan ringkasan ramah dalam Bahasa Indonesia (judul, durasi, rasio, jumlah adegan) tanpa mengklaim telah mendengar audio/menonton gerak langsung.
