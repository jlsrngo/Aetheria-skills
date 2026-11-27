# Aetheria Skills — Studio Video Animasi Prosedural 100% Lokal

Satu repositori terpadu berisi **8 skill 100% lokal** (tanpa GPU cloud berbayar / Higgsfield, langsung aktif otomatis via [`.agents/skills.json`](.agents/skills.json) begitu di-`clone` / `pull`), **pustaka aset, font & mesin cutaway global (`aset_global/`)**, dan **1 renderer & utilitas global (`render.py`)**:

| Perintah Slash | Jenis & Gaya | Kebutuhan Lokal |
|---|---|---|
| `/stikman-cerita` | Animasi 2D kartun chibi + kamera parallax + lipsync VO | Pure Python + NumPy + Pillow + ffmpeg |
| `/3D-stickman` | Animasi 3D Chibi/Stickman Z-Buffer Cel-Shaded + Outline Tipis + Subtitle 1–2 Kata | Pure Python + NumPy + Pillow + ffmpeg |
| `/paperworld` | Diorama 3D Pop-Up Paper Craft (3D Shadow Map + SSAO + engsel lipat buku) | Pure Python + NumPy + Pillow + ffmpeg |
| `/voxelverse` | Diorama 3D Voxel / Low-Poly (PointLight + bloom + hujan/salju + percikan) | Pure Python + NumPy + Pillow + ffmpeg |
| `/strata3d` | 3D Penampang Tanah & Infrastruktur Cutaway (lapisan tanah, rumah, sumur/septik, maskot) | Pure Python (opsional Blender `bpy`) |
| `/hydro3d` | 3D Sirkulasi Air, Kolam & Filter Cutaway (air transparan, pompa/filter, kamera kontinu, `cards`) | Pure Python (opsional Blender `bpy`) |
| `/mechlab3d` | 3D Studio Mekanik & Mesin Logam Cutaway (bengkel navy, logam, cutaway amber, HUD gauge) | Pure Python (opsional Blender `bpy`) |
| `/bedah-referensi` | Bedah video referensi otomatis (`probe`, `sheets`, `motion`, `audio` LUFS/jeda/pitch, budget naskah, opsi OCR) | Pure Python + NumPy + Pillow + ffmpeg |

---

## Cara Pakai Setelah `git clone` / `git pull` (Tanpa Instalasi Tambahan!)

1. **Clone atau pull repositori ini** lalu buka foldernya sebagai workspace:
   ```bash
   git clone https://github.com/jlsrngo/Aetheria-skills.git
   # atau untuk update:
   git pull origin main
   ```
2. Semua 8 skill di [`.agents/skills.json`](.agents/skills.json) **langsung aktif otomatis** — tinggal ketik di chat:
   - `/3D-stickman buatkan video ...`
   - `/paperworld buatkan video ...`
   - `/stikman-cerita buatkan video ...`
   - `/voxelverse buatkan video ...`
   - `/strata3d buatkan video ...` (penampang tanah & infrastruktur)
   - `/hydro3d buatkan video ...` (kolam, air & filtrasi)
   - `/mechlab3d buatkan video ...` (mesin & mekanik gaya CR-V)
   - `/bedah-referensi` (lampirkan video referensi untuk dibedah sebelum produksi)

---

## Renderer & Utilitas Global (`render.py`) — Satu Perintah untuk Semua Skill

Gunakan **`render.py`** di root repo — otomatis mendeteksi mesin (`3D-stickman`, `paperworld`, `stikman-cerita`, `voxelverse`) dari `proyek.json` dan menyegarkan PATH `ffmpeg` di Windows:

```bash
# Cek Python, NumPy, Pillow, ffmpeg, dan status semua 6 skill lokal
python render.py cek

# Bedah video referensi (contact sheet, hard-cut, motion, audio LUFS & jeda)
python render.py bedah referensi.mp4 out_bedah --fps 1

# Rapikan jeda panjang VO mentah + normalisasi loudness -14 LUFS
python render.py rapikan-vo vo_raw.mp3 vo_rapi.wav --target 30

# Buat proyek baru untuk gaya mana saja
python render.py baru proyek-saya --gaya 3D-stickman --rasio 9:16 --judul "Judul"
python render.py baru proyek-saya --gaya paperworld
python render.py baru proyek-saya --gaya stikman-cerita
python render.py baru proyek-saya --gaya voxelverse

# Pre-render QA proyek.json (cek durasi, VO, lompatan kamera, + QA MP4 final jika ada)
python render.py periksa proyek-saya

# Render stills QC otomatis (deteksi mesin otomatis)
python render.py qc proyek-saya --draft

# Render penuh + mix audio (VO, musik, SFX, subtitle) sampai MP4 final
python render.py render proyek-saya           # kualitas penuh
python render.py render proyek-saya --draft   # render cepat
# Shorthand juga bisa:
python render.py proyek-saya --draft
```

---

## Pustaka Aset & Movement Global (`aset_global/`) — Lintas Semua Skill

Agar aset prosedural, kurva gerak, dan tekstur tajam tidak terkunci di satu skill saja, seluruh komponen bersama disimpan di root **[`aset_global/`](aset_global/)**:
- [`aset_global/gerak.py`](aset_global/gerak.py) — kurva animasi & kinematika global (`pop_scale`, `pulse_scale`, `spring_overshoot`, `bob_offset`, `shake_offset`, `flow_positions`, `piston_kinematics`, `smoothstep`, `ease_io`).
- [`aset_global/sinematografi.py`](aset_global/sinematografi.py) — mesin **Sinematografi Multi-Shot Global** (`SinematografiRig`, `kamera.shot`, 16 gerak kamera film termasuk `tracking`, `orbit`, `spiral`, `crane`, `dolly_zoom`, Over-the-Shoulder `bahu`, `geser_x` Rule of Thirds, dan bar `sinemaskop`) untuk seluruh skill visual.
- [`aset_global/transisi.py`](aset_global/transisi.py) — pustaka **22 Transisi Global** (`fade`, `fade_hitam`, `flash`, `kedip`, `iris`, `geser`, `whip`, `zoom`, `zoom_out`, `wipe`, `wipe_diagonal`, `wipe_tiang`, `putar`, `belah`, `tirai`, `luma`, `blur_cross`, `glitch`, `kotak`, `halaman`, `cahaya`) + panduan lengkap di [`aset_global/SINEMATOGRAFI-DAN-TRANSISI.md`](aset_global/SINEMATOGRAFI-DAN-TRANSISI.md).
- [`aset_global/tekstur.py`](aset_global/tekstur.py) — generator tekstur HD PIL yang di-cache (`tex_dial_gauge`, `tex_tag_callout`, `get_font`).
- [`aset_global/fonts/`](aset_global/fonts/) — 1 koleksi font bersama (`Baloo2`, `Bungee`, `Fredoka`, `Nunito` + lisensi OFL) yang dipakai otomatis oleh seluruh 4 skill visual tanpa duplikasi.
- [`aset_global/engineering_3d.py`](aset_global/engineering_3d.py) — 6 aset engineering 3D adaptif (`panah_3d`, `aliran_pipa`, `dial_gauge`, `tag_callout`, `tangki_air`, `piston_3d`) yang otomatis menyesuaikan engine `/3D-stickman`, `/voxelverse`, maupun `/paperworld`.
- [`aset_global/engineering_2d.py`](aset_global/engineering_2d.py) — versi 2D kartun dari 6 aset engineering yang sama untuk `/stikman-cerita`.
- [`aset_global/studio_cutaway.py`](aset_global/studio_cutaway.py) & [`aset_global/cutaway_runner.py`](aset_global/cutaway_runner.py) — mesin render 3D cutaway PBR-lite murni Python untuk `/strata3d`, `/hydro3d`, dan `/mechlab3d`.
- [`aset_global/blender_kit/`](aset_global/blender_kit/) — kit Blender `bpy` opsional bersama jika ingin merender dengan Blender lokal.

Semua 4 skill visual (`3D-stickman`, `voxelverse`, `paperworld`, `stikman-cerita`) sudah terhubung otomatis ke `aset_global/` melalui `benda.py` masing-masing.

---

## Lisensi & Kredit
- Skill inti pure-Python (`stikman-cerita`, `3D-stickman`, `paperworld`, `voxelverse`, `bedah-referensi`, `render.py`, `tools_global.py`) merupakan bagian dari repositori **Aetheria Skills**.
- Skill `3d-engineering-video` diadaptasi dari [`davidalfasunarna/3d-engineering-video-claude-skills`](https://github.com/davidalfasunarna/3d-engineering-video-claude-skills) ke struktur standar lokal (`assets/`, `references/`, `scripts/`, `templates/`) tanpa Higgsfield.
