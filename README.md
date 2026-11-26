# Aetheria Skills — Studio Video Animasi Prosedural (Pure Python)

Satu repositori berisi **3 skill animasi prosedural lengkap** (100% Python + NumPy + Pillow + ffmpeg, tanpa Blender/Unity/GPU) dan **1 renderer global terpadu (`render.py`)**:

| Perintah Slash | Gaya Animasi | Tokoh Utama |
|---|---|---|
| `/stikman-cerita` | Animasi 2D kartun chibi + kamera parallax + lipsync VO | `kribo`, `nadia`, `otak`, `virus`, `sel_imun`, dll. |
| `/paperworld` | Diorama 3D Pop-Up Paper Craft (3D Shadow Map + SSAO + engsel lipat buku) | `luna`, `kribo`, `nadia`, `kucing`, dll. |
| `/voxelverse` | Diorama 3D Voxel / Low-Poly (PointLight + bloom + hujan/salju + percikan) | `kribo`, `arka`, `robo`, `nadia`, dll. |

---

## Cara Pakai Setelah `git clone` / `git pull` (Tanpa Instalasi Tambahan!)

1. **Clone atau pull repositori ini** lalu buka foldernya sebagai workspace di Antigravity:
   ```bash
   git clone https://github.com/jlsrngo/Aetheria-skills.git
   # atau untuk update:
   git pull origin main
   ```
2. Karena sudah ada [`.agents/skills.json`](.agents/skills.json), ketiga skill **langsung aktif otomatis** begitu foldernya dibuka — langsung ketik di chat:
   - `/paperworld buatkan video ...`
   - `/stikman-cerita buatkan video ...`
   - `/voxelverse buatkan video ...`

*(Opsional: jika ingin `/paperworld`, `/stikman-cerita`, `/voxelverse` juga bisa dipanggil dari workspace/folder lain di luar repo ini, cukup tambahkan path folder repo ini sekali saja ke `~/.gemini/config/skills.json`.)*

---

## Renderer Global (`render.py`) — Satu Perintah untuk Semua Skill

Tidak perlu memanggil `scripts/render.py` masing-masing skill. Cukup gunakan **`render.py`** di root repo — otomatis mendeteksi mesin (`paperworld`, `stikman-cerita`, atau `voxelverse`) dari `proyek.json` dan menjalankan render + audio sekaligus:

```bash
# Cek lingkungan (Python, NumPy, Pillow, ffmpeg, & 3 skill)
python render.py cek

# Buat proyek baru untuk skill mana saja
python render.py baru proyek-saya --gaya paperworld
python render.py baru proyek-saya --gaya stikman-cerita --rasio 9:16 --judul "Judul"
python render.py baru proyek-saya --gaya voxelverse

# Render stills QC otomatis (deteksi mesin otomatis)
python render.py qc proyek-saya --draft

# Render penuh + mix audio (VO, musik, SFX, subtitle) sampai MP4 final
python render.py render proyek-saya           # kualitas penuh
python render.py render proyek-saya --draft   # render cepat
# Shorthand juga bisa:
python render.py proyek-saya --draft
```
