# AGENTS.md — Aturan Produksi & Penggunaan Skill Aetheria

Dokumen ini menjadi pedoman wajib bagi setiap agen AI yang bekerja di repositori **Aetheria Skills** (`e:\stikman-cerita`).

---

## 1. Prinsip Umum & Komunikasi

- Seluruh komunikasi dengan user memakai **Bahasa Indonesia** yang ringkas, jelas, dan jujur.
- Seluruh alur produksi berjalan **100% lokal di CPU** (Python + NumPy + Pillow + ffmpeg) **tanpa** layanan cloud/GPU berbayar (seperti Higgsfield).
- Gunakan CLI global **[`render.py`](render.py)** di root repositori untuk seluruh operasi (`cek`, `baru`, `qc`, `render`, `audio`, `bedah`, `rapikan-vo`, `periksa`, `galeri`).
- Jangan menjalankan `git commit` atau `git push` tanpa permintaan eksplisit dari user.

---

## 2. Daftar 8 Skill Resmi & Kapan Menggunakannya

Seluruh skill aktif otomatis melalui [`.agents/skills.json`](.agents/skills.json) dan berbagi aset, font, kurva gerak, serta mesin cutaway bersama di **[`aset_global/`](aset_global/)**.

| Skill | Gaya Visual & Kegunaan |
|---|---|
| `/stikman-cerita` | Animasi 2D **Ghibli Studio Art Style** (lukisan cat air/gouache hangat, tokoh chibi ekspresif bermata besar & outline halus, 20 gaya awan, rumput bervolume, kamera parallax, lipsync VO) |
| `/3D-stickman` | Animasi 3D Stickman/Chibi semi-smooth + outline halus anti-aliased (tokoh utama **Kribo** & 17+ pemeran, 21 set diorama, 39 ekspresi) |
| `/paperworld` | Diorama 3D Pop-Up Paper Craft (Shadow Map, SSAO, engsel lipat buku) |
| `/voxelverse` | Diorama 3D Voxel / Low-Poly (PointLight, bloom, hujan/salju, percikan) |
| `/strata3d` | 3D Penampang Tanah & Infrastruktur Cutaway (lapisan tanah, rumah, sumur/septik, maskot pekerja, hard-cut, subtitle `phrases`) |
| `/hydro3d` | 3D Sirkulasi Air, Kolam & Filter Cutaway (air transparan biru↔hijau, pompa & filter pasir, kamera kontinu, subtitle `cards`) |
| `/mechlab3d` | 3D Studio Mekanik & Mesin Logam Cutaway PBR (bengkel navy, *stand* biru, logam mengkilap, cutaway kuning amber, piston/katup/turbo, strip HUD gauge BAR/RPM) |
| `/bedah-referensi` | Bedah video referensi otomatis (`probe`, `sheets`, `motion`, `audio` LUFS/jeda, budget naskah, opsi OCR) |

**Aturan pemilihan skill:**
1. Selalu baca `SKILL.md` milik skill terkait sebelum membuat proyek atau merender.
2. Jika user melampirkan **video referensi**, **WAJIB** jalankan `/bedah-referensi` (`python render.py bedah <video> out_bedah`) terlebih dahulu untuk mengukur ritme, kamera, audio, dan gaya subtitle sebelum menyusun naskah/adegan.
3. Gunakan aset, font, sinematografi multi-shot (`aset_global/sinematografi.py`), dan 22 transisi global (`aset_global/transisi.py`) dari `aset_global/` (jangan menduplikasi font atau aset engineering ke dalam folder skill; baca [`aset_global/SINEMATOGRAFI-DAN-TRANSISI.md`](aset_global/SINEMATOGRAFI-DAN-TRANSISI.md)).

---

## 3. Standar Visual Wajib `/stikman-cerita` — Ghibli Studio Art Style (Termasuk Elemen Baru)

Seluruh produksi video `/stikman-cerita` — baik latar, properti, tokoh, maupun **elemen baru yang belum tersedia** — **WAJIB** mematuhi kriteria **Ghibli Studio Art Style** berikut:

- **Hand-painted 2D anime illustration:** tampilan lukisan tangan 2D animasi Jepang klasik berkualitas tinggi, bukan bentuk vektor polos atau kotak datar.
- **Soft, warm, and natural color palette:** palet warna lembut, hangat, alami, dan teduh (*earth-tone*, krem hangat, hijau zaitun/hutan, biru cerulean langit); hindari warna neon mencolok atau tampilan futuristik dingin.
- **Beautiful watercolor-like background textures:** tekstur cat air / *gouache* halus pada dinding, langit, tanah, pasir, jalan, dan permukaan latar (tidak datar polos).
- **Detailed and expressive character designs & large, expressive eyes:** desain tokoh chibi berkarakter dengan mata besar ekspresif, ekspresi wajah alami, dan rambut bervolume/bertekstur halus.
- **Soft and clean character outlines:** garis tepi bersih dan lembut bernada coklat-hangat (`G_OC`), bukan garis hitam tebal kaku.
- **Smooth cel shading with subtle gradients:** bayangan *cel shading* lembut bergradasi halus dengan sorotan cahaya hangat.
- **Warm sunlight with cinematic lighting & gentle shadows:** sinar matahari hangat sinematik (*sunbeams*, *dappled sunlight*), cahaya ambien lembut, dan bayangan jatuh sejuk yang halus; ruangan malam tetap hangat bercahaya lampu teduh.
- **Fluffy clouds and vibrant blue skies:** langit biru cerah bergradasi dengan awan lembut mengembang yang bervariasi antar-adegan (gunakan variasi 20 gaya awan, jangan sama di tiap scene).
- **Lush green trees, grass, detailed flowers & natural environments:** pepohonan rimbun bervolume (tinggi proporsional menjulang di atas tokoh), rumput meruncing berlapis, bunga liar/tanaman detail, dan atmosfer pedesaan yang magis, damai, dan penuh nostalgia.
- **Rich environmental details & organic shapes:** detail lingkungan hidup (jendela dengan pemandangan luar & tirai, bingkai foto berisi ilustrasi nyata, peralatan retro analog hangat bila ada ruang kendali/studio), bentuk organik tanpa pengulangan kembar dalam satu adegan.
- **Natural living ambient motion (tidak pasif & tidak lebay):** setiap adegan selalu memiliki gerakan alami halus yang mengikuti waktu `t` — awan melayang pelan, pohon/rumput/tirai bergoyang lembut, hewan kecil melintas santai (kupu-kupu, burung jauh, kucing berjalan), uap makanan/teh hangat, asap cerobong tipis, riak ombak/perahu jauh, atau jam/gulungan pita bergerak — tanpa efek norak/berlebihan.

> **ATURAN WAJIB PEMBUATAN ELEMEN BARU:**
> Apabila agen diminta membuat video `/stikman-cerita` dan terdapat elemen yang **belum ada** di pustaka (latar/set baru, bangunan, kendaraan, properti/benda baru, ruangan khusus, tanaman, atau tokoh baru), agen **WAJIB merancang dan membuat elemen baru tersebut 100% mengikuti seluruh kriteria Ghibli Studio Art Style di atas**. Dilarang membuat elemen baru bergaya kotak datar, polos tanpa tekstur/bayangan, atau bergaya modern/neon yang bertabrakan dengan estetika Ghibli.

---

## 4. Rasio Video — Default `9:16`, Wajib Bertanya Dulu

- **Rasio default** untuk semua video adalah **`9:16`** (vertikal `1080×1920`, cocok untuk TikTok / Reels / YouTube Shorts).
- **WAJIB bertanya terlebih dahulu** kepada user sebelum membuat proyek atau merender:
  > *"Rasio videonya mau pakai **9:16** (default vertikal) atau **16:9** (landscape)?"*
- Pengecualian: hanya boleh melewati pertanyaan ini jika user **sudah menyebutkan rasio secara eksplisit** di prompt awalnya (misalnya *"buatkan video 16:9..."* atau *"format shorts 9:16..."*).

---

## 5. Wajib Sheet Preview Sebelum Render (Tanpa Render Penuh Otomatis)

Setiap produksi video **WAJIB** melewati tahap preview visual terlebih dahulu:

1. **Siapkan proyek & naskah:**
   - Jika ada VO mentah, rapikan jeda panjang & normalisasi `-14 LUFS` dengan `python render.py rapikan-vo <in> <out.wav> [--target <detik>]`.
   - Susun `proyek.json` dan jalankan pemeriksaan pra-render:
     ```bash
     python render.py periksa <proyek>
     ```
2. **Buat Sheet Preview (WAJIB, TANPA render video penuh):**
   - Jalankan render preview stills / contact sheet saja:
     ```bash
     python render.py qc <proyek> --draft
     ```
   - Jika hasil `qc` berupa beberapa file stills terpisah, gabungkan menjadi satu **lembar *contact sheet* preview** yang rapi (diberi label ID adegan & detik).
3. **Inspeksi mandiri oleh agen:**
   - Agen **WAJIB membuka dan mengecek sendiri** gambar *sheet preview* dengan `read_file` untuk memastikan komposisi, karakter, teks/subtitle, dan framing tidak ada yang terpotong atau glitch.
   - Jika ada cacat visual, perbaiki dulu lalu regenerasi *sheet preview*.
4. **Presentasikan Sheet Preview ke user & BERHENTI:**
   - Tunjukkan link *sheet preview* ke user, rangkum durasi/jumlah adegan/rasio, lalu **tunggu konfirmasi user**.

---

## 6. Hanya Lakukan Render Penuh Jika Diminta User

- **DILARANG KERAS** menjalankan render penuh (`python render.py render <proyek>`) secara otomatis tanpa izin/permintaan user.
- Render penuh (MP4 video + mix audio VO/musik/SFX) **HANYA** boleh dijalankan setelah:
  - User menyetujui *sheet preview* dan meminta render (mis. *"oke lanjut render"*, *"gas render penuh"*), **ATAU**
  - User sejak awal secara eksplisit memerintahkan langsung render penuh tanpa menunggu approval preview.
- Setelah render penuh selesai, jalankan QA akhir (`python render.py periksa <proyek> --video <mp4_final>`) dan laporkan hasil secara jujur (durasi, resolusi, FPS, loudness LUFS, dan lokasi file).

---

## 7. Auto-Upload ke Google Drive Jika Terkoneksi

Setiap kali **render MP4 final selesai**:

1. **Cek koneksi Google Drive** yang aktif di lingkungan saat itu (plugin/MCP Google Drive yang sudah login via `list_plugin_accounts` atau CLI lokal seperti `rclone` / `gdrive` yang sudah terkonfigurasi).
2. **Jika terkoneksi:**
   - **Otomatis upload** file MP4 final (dan *sheet preview* bila membantu) ke folder tujuan di Google Drive.
   - Laporkan status upload beserta **link / nama folder Google Drive** kepada user bersama path file lokalnya.
3. **Jika belum terkoneksi:**
   - Jangan memblokir penyelesaian tugas dan jangan menginstal tool pihak ketiga tanpa izin.
   - Laporkan path file MP4 lokal dengan jelas, lalu beri catatan singkat bahwa **auto-upload Google Drive dilewati karena akun/integrasi Google Drive belum terhubung**.

---

## 8. Catatan Teknis Lingkungan Lokal (Windows)

- Shell default adalah **Windows PowerShell 5.1**: hindari operator `&&` di perintah PowerShell; gunakan `; if ($LASTEXITCODE -eq 0) { ... }`.
- Saat menjalankan beberapa impor NumPy dalam satu sesi, gunakan `$env:OPENBLAS_NUM_THREADS='1'` untuk mencegah kegagalan alokasi memori thread OpenBLAS di Windows.
- Pastikan semua tautan file dalam respon ke user memakai format clickable `file:///` dengan *forward slash* (`/`).
