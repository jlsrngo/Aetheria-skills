# Sinematografi & Transisi Global — Aetheria Skills (`aset_global/`)

Seluruh **7 skill visual** (`/3D-stickman`, `/paperworld`, `/voxelverse`, `/stikman-cerita`, `/strata3d`, `/hydro3d`, `/mechlab3d`) berbagi mesin **Sinematografi Multi-Shot** ([`sinematografi.py`](sinematografi.py)) dan **22 Transisi Global** ([`transisi.py`](transisi.py)) secara seragam.

---

## 1. Sinematografi Multi-Shot Global (`kamera.shot`)

Jangan menggunakan 1 sudut kamera statis sepanjang adegan `> 4 detik`. Semua skill 3D mendukung array `kamera.shot` (auto-reset `roll`/`blur` setiap pindah shot):

```json
"sinemaskop": true,
"kamera": {
  "gaya": "halus",
  "shot": [
    {
      "t": 0.0,
      "ukuran": "lebar",
      "fokus": ["kribo", "pedagang"],
      "sudut": -24,
      "angle": "atas",
      "gerak": { "jenis": "crane", "naik": -0.75, "maju": -0.5 }
    },
    {
      "t": 2.5,
      "bahu": "pedagang",
      "fokus": "kribo",
      "sisi_bahu": 1.08,
      "geser_x": -0.18,
      "gaya": "handheld",
      "gerak": { "jenis": "push", "faktor": 0.88, "zoom": 4 }
    },
    {
      "t": 5.0,
      "ukuran": "dekat",
      "fokus": "kribo",
      "sudut": -22,
      "angle": "rendah",
      "gerak": { "jenis": "spiral", "derajat": 65, "faktor": 0.88, "naik": 0.45 }
    }
  ]
}
```

### Parameter Komposisi Global
- `angle`: `"normal"`, `"bawah"` (low hero), `"rendah"` (worm's-eye), `"atas"` (high), `"burung"` (bird's-eye), `"dutch"` (+9°), `"dutch_kiri"` (-9°).
- `geser_x`: *Rule of Thirds* / *lead room* lateral relatif sumbu kamera (mis. `±0.18`).
- `bahu`: *Over-the-Shoulder* (OTS) di belakang tokoh A menghadap `fokus` tokoh B (`sisi_bahu: ±1.08`, `jarak_bahu: 1.62` — gunakan tanda berlawanan untuk *reverse-shot* agar patuh **180-Degree Rule**).
- `gaya`: `"tripod"`, `"halus"`, `"napas_film"`, `"handheld"`, `"tegang"`.
- `sinemaskop: true`: bar letterbox film 2.35:1 (tersedia di seluruh 7 skill, termasuk 2D `/stikman-cerita`).

### 16 Gerak Kamera Global (`gerak.jenis`)
| Gerak | Kegunaan |
|---|---|
| `push` / `pull` | Mendekat / menjauh halus (`faktor`, `zoom`, `ke`) |
| `punch_in` / `hentak` | Zoom-in cepat / impact zoom memantul (`faktor`, `kuat`) |
| `dolly_zoom` | Efek Vertigo (jarak berubah + FOV mengompensasi) |
| `orbit` / `spiral` | Memutar mengelilingi target (`derajat`, `naik`, `faktor`, `zoom`) |
| `crane` | Naik/turun + maju (`naik`, `maju`, `ke`) |
| `truck` / `pan` | Geser sejajar (`x`, `y`, `z`) / menoleh di tempat (`derajat`, `naik`) |
| `ikut` / `tracking` | Mengikuti tokoh berjalan (ideal untuk **side tracking melewati tiang foreground**, `jarak`, `sudut`, `derajat`, `tinggi`) |
| `terbang` | Jalur spline Catmull-Rom 3D (`jalur: [[x,y,z], ...]`) |
| `pindah_fokus` | Rack focus ke target lain (`fokus`, `blur`) |
| `whip` / `goyang` / `miring` / `potong` | Geser cepat ber-blur / getaran / roll / hard-cut |

---

## 2. 22 Transisi Global (`adegan[].transisi`)

Bisa ditulis sebagai string singkat (`"transisi": "wipe_tiang"`) atau objek (`"transisi": {"jenis": "whip", "arah": "kiri", "dur": 0.35}`):

| Nama (`jenis`) | Alias | Efek Visual | Opsi Utama |
|---|---|---|---|
| `potong` | `cut` | Hard cut instan (0 dtk) | — |
| `fade` | `dissolve` | Cross-dissolve lembut | `dur` |
| `fade_hitam` | `dip_hitam`, `dip_black` | Dip ke hitam lalu masuk adegan baru | `dur`, `warna` |
| `flash` | `dip_putih`, `kilat` | Kilatan putih cepat (plot twist / reveal) | `dur`, `warna` |
| `kedip` | `blink` | Kelopak hitam menutup lalu membuka | `dur` |
| `iris` | — | Lingkaran iris membuka (`keluar: true` untuk iris-out → iris-in) | `x`, `y`, `keluar`, `garis` |
| `geser` | `slide`, `push_slide` | Dorong layar searah | `arah` (`kiri`/`kanan`/`atas`/`bawah`) |
| `whip` | `whip_pan` | Whip-pan cepat ber-motion-blur | `arah`, `dur` |
| `zoom` | `zoom_in` | Zoom-in cepat dengan motion blur lembut | `dur` |
| `zoom_out` | — | Zoom-out menarik keluar ke adegan baru | `dur` |
| `wipe` | — | Sapuan lurus bersih | `arah`, `garis` |
| `wipe_diagonal` | `diagonal` | Sapuan garis miring 45° dinamis | `garis` |
| `wipe_tiang` | `pillar_wipe`, `foreground_wipe`, `tiang` | **Siluet tiang/pilar gelap melintas di depan lensa** menyembunyikan cut | `arah`, `lebar`, `warna` |
| `putar` | `spin` | Spin-whip 180° ber-blur | `arah` (`kanan`/`kiri`) |
| `belah` | `split`, `tirai_belah` | Layar terbelah 2 membuka adegan baru | `arah` (`horizontal`/`vertikal`) |
| `tirai` | `blinds`, `venetian` | Bilah tirai bergantian menyapu layar | `jumlah` (default `8`), `arah` |
| `luma` | `burn`, `film_burn`, `light_leak` | Kilau cahaya hangat *film burn* menyapu layar | `dur` |
| `blur_cross` | `defocus`, `rack_focus` | Defocus keluar lalu fokus ke adegan baru | `dur` |
| `glitch` | `rgb_split` | RGB channel split + pita glitch horizontal | `dur` |
| `kotak` | `pixelate`, `mosaic` | Mozaik piksel membesar lalu kembali tajam | `besar`, `dur` |
| `halaman` | `page_turn`, `lipat` | Membalik halaman kertas dengan bayangan lipatan | `dur` |
| `cahaya` | `radial_flash`, `flare` | Ledakan lens flare lembut dari pusat layar | `dur` |

---

## 3. Mesin Variasi Sutradara & Anti-Pasif Antar Video (`variasi.py`)

Agar **Video 1 dan Video 2 tidak terasa kembar / gitu-gitu aja**, seluruh 7 skill visual otomatis memakai [`aset_global/variasi.py`](variasi.py):

- **Auto-Seed Deterministik per Video:** dihitung otomatis dari hash `judul` + `narasi` + `latar` (atau dapat diatur manual lewat `"seed": 2026` di root `proyek.json`). Video berbeda otomatis mendapat variasi berbeda, namun render ulang proyek yang sama tetap 100% konsisten.
- **6 Profil Sutradara (`"gaya_sutradara"` di root `proyek.json`, default otomatis):**
  - `dinamis_film` *(handheld, wipe_tiang/whip/luma, low-angle/crane/spiral, karakter ekspresif)*
  - `dokumenter_halus` *(halus, fade/geser/iris/tirai, push/pull/orbit lembut)*
  - `komik_enerjik` *(handheld, whip/wipe_diagonal/belah/flash/halaman, punch_in/hentak)*
  - `misteri_tegang` *(tegang, fade_hitam/kedip/glitch, dutch/rendah/dolly_zoom)*
  - `hangat_ghibli` *(napas_film, luma radial/cahaya/halaman/wipe_tiang, crane/orbit lembut)*
  - `retro_kreatif` *(halus, glitch/kotak/putar/belah, spiral/truck/dolly_zoom)*
- **Transisi Anti-Repetisi:** saat `"transisi": "auto"` (atau kosong), transisi dipilih kontekstual sesuai profil & seed video dan tidak pernah mengulang jenis non-potong 2× berturut-turut.
- **Auto-Variasi Kamera:** jika adegan belum menentukan `kamera.gerak` / `kamera.shot`, sudut, `angle`, `geser_x`, gerak kamera, hingga 2-shot OTS (untuk adegan `>= 4,8 dtk` dengan `>= 2` tokoh) digenerate otomatis unik per video (tanpa menimpa pengaturan kamera manual user).
- **Auto-Koreografi Karakter Anti-Pasif:** jika aktor berdiri hanya diberi `pose: "diam"` / `"santai"` tanpa `aksi`/`masuk`/`keluar`, mesin otomatis menyisipkan langkah berjalan pendek, perubahan pose gestur, & perubahan hadap 3/4/serong yang berbeda tiap video + gerak *idle* organik (matikan per aktor dengan `"gerak": "kaku"`).
