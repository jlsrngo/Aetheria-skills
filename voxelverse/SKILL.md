---
name: voxelverse
description: Pembuat video CERITA & MOTION 3D Voxel / Low-Poly Diorama murni Python (NumPy + Pillow + ffmpeg, tanpa browser/WebGL eksternal). Mendukung karakter 3D Voxel artikulasi penuh termasuk "kribo" (afro hitam penuh, kacamata kotak, kaos teal + dasi kupu-kupu, sneaker hitam-putih), "arka" (coder hoodie teal berkacamata), "robo" (robot lampu meja oranye bercahaya), dan "nadia" (hijab hitam modern, blazer krem), plus 12 set diorama 3D (studio_kode, kota_hujan dengan pantulan aspal basah & tram, kamar, sekolah_luar, kelas, kafe, taman, atap_kota, dll). Kamera 3D sinematik (orbit, crane, fly_through/terbang, tracking/ikut, bahu_kiri, luar_jendela, balik_wajah, punch, goyang, rack focus), pencahayaan PointLight dinamis + bloom, percikan listrik 3D di kabel, hujan/salju 3D, lipsync VO, musik orisinal sinematik/lofi + hujan, dan subtitle per kata. Keluaran MP4 H.264+AAC 30 fps (16:9 atau 9:16). Gunakan setiap kali user ingin membuat animasi 3D voxel, diorama kota hujan, video coding seperti game/Remotion versi Python, atau cerita 3D VoxelVerse dengan Kribo, Arka, Robo, atau Nadia. Seluruh komunikasi dengan user memakai Bahasa Indonesia.
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

## Dua mode masuk

**A. Zero-prompt:** user melampirkan VO (`.mp3/.wav/.m4a`) + naskah (`.txt/.md` atau ditempel) lalu memanggil `/voxelverse`. Itu izin penuh membuat satu video utuh: langsung pilih rasio (default 16:9; 9:16 jika disebut Reels/TikTok/Shorts/vertikal).
**B. Hanya ide/topik:** tulis naskah cerita singkat/sinematik, tampilkan, dan dalam pesan yang sama minta **satu kali** file VO + rasio. Boleh langsung membuat **draf bisu** (`"vo": null`) bila user meminta.

## Alur produksi

> **Renderer Global Terpadu:** Gunakan `python ../render.py` di root repositori (otomatis mendeteksi mesin `voxelverse`, menyegarkan PATH `ffmpeg`, dan menjalankan render + audio sekaligus). Jika skill dipakai berdiri sendiri, gunakan `$S/render.py` & `$S/audio.py`.

1. **Cek lingkungan** — `python ../render.py cek` (atau `bash $S/check_env.sh`). Jika ada `[GAGAL]`, laporkan jujur dan berhenti.
2. **Proyek baru** — `python ../render.py baru <folder>/<topik> --gaya voxelverse --vo <file> --naskah <file> --rasio 16:9 --judul "<Judul>"`.
3. **Baca referensi** — baca `kamera.md`, `format-adegan.md`, dan `dunia-dan-benda.md`.
4. **Rencana adegan** — susun alur adegan: hook 3 detik pertama, variasi sudut kamera 3D (minimal 4 jenis gerak berbeda untuk video ≥ 30 detik), pencahayaan & cuaca.
5. **Tulis `proyek.json`** — gunakan acuan `templates/contoh-dunia-kecil/proyek.json` atau `templates/contoh-cerita-kribo/proyek.json`.
6. **QC visual dan kamera**:
   - `python ../render.py qc <proyek> --stills auto --draft` → **lihat** `out/qc/sheet.jpg`.
   - Untuk adegan gerak kamera kompleks (`terbang`, `orbit`, `crane`): `python ../render.py qc <proyek> --strip N --draft` → lihat `out/qc/strip_NN.jpg`.
   - Periksa dan perbaiki semua baris `[PERIKSA]`, tokoh terpotong, atau sudut kamera menembus dinding.
7. **Render penuh & Audio (1 perintah global)** — `python ../render.py render <proyek>` (otomatis render paralel + `audio.py` musik/SFX/hujan/ducking −16 LUFS; tambah `--draft` untuk cepat). Jika di lingkungan terbatas waktu dan tercetak `BELUM SELESAI nn%`, jalankan perintah yang sama persis untuk melanjutkan dari potongan terakhir.
8. **Mix ulang audio saja (opsional)** — `python ../render.py audio <proyek>`.
9. **Verifikasi akhir** — pastikan tercetak `FINAL OK`, lalu inspeksi 3–4 frame dari MP4 final sebelum mengirim ke user.
10. **Bicara ke user** — Bahasa Indonesia ramah, singkat, jujur (jangan klaim sudah mendengar audio), akhiri dengan ringkasan judul, durasi, rasio, dan jumlah adegan.
