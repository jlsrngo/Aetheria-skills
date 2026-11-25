# Format `proyek.json` & Koreografi Adegan — PaperWorld

Berkas proyek utama adalah `proyek.json` pada akar direktori proyek.

## Struktur Top-Level `proyek.json`

```json
{
  "judul": "Judul Film PaperWorld",
  "ukuran": [1080, 1920],
  "fps": 30,
  "vo": "input/vo.m4a",
  "ekor": 0.25,
  "musik": "auto",
  "mood_musik": "kertas",
  "sfx": true,
  "subtitle": true,
  "gaya_subtitle": "kertas",
  "tokoh": {
    "luna": "luna",
    "kribo": "kribo",
    "nadia": "nadia",
    "kucing": "kucing"
  },
  "adegan": [ ... ]
}
```

### Parameter Top-Level
- `ukuran`: `[1080, 1920]` untuk vertikal (`9:16`, Reels/Shorts/TikTok) atau `[1920, 1080]` untuk lanskap (`16:9`).
- `fps`: `30` (standar).
- `vo`: path relatif ke berkas audio narasi, atau `null`.
- `ekor`: jeda tambahan sesudah narasi selesai dalam detik (default `0.9`; setel `0.02` jika `vo` berisi master audio berdurasi pas).
- `musik`: `"auto"`, path file audio, atau `"none"`.
- `mood_musik`: salah satu mood di `audio.py` (`kertas`, `akustik`, `ceria`, `santai`, `hangat`, `sedih`, `tegang`, `semangat`, `lucu`, `misteri`, `malam`).
- `gaya_subtitle`: `"kertas"` (kartu karton putih bersudut bulat & bayangan drop), `"pil"`, atau `"komik"`.

## Struktur Setiap Objek `adegan`

```json
{
  "id": "pintu_5_menit",
  "latar": "meja_hp",
  "mulai": 0.0,
  "durasi": 3.15,
  "waktu": "siang",
  "jam": 9.0,
  "transisi": "potong",
  "narasi": "Cuma lima menit saja...",
  "opsi": { "mode_pintu": false, "buka_pintu": 0.0 },
  "animasi_opsi": [
    { "t": 0.90, "dur": 0.05, "mode_pintu": true, "buka_pintu": 0.0 },
    { "t": 1.15, "dur": 1.10, "buka_pintu": 1.0, "ease": "pental" }
  ],
  "tokoh": [ ... ],
  "benda": [ ... ],
  "kamera": { ... },
  "balon": [ ... ],
  "teks": [ ... ],
  "efek": [ ... ],
  "sfx": [ { "t": 1.15, "jenis": "pintu" } ]
}
```

### Penjadwalan Waktu (`mulai` / `durasi`)
- Bila seluruh adegan mencantumkan `"mulai"` eksplisit dalam detik, `timing.jadwal` memakai timestamp absolut tersebut (sangat disarankan saat menyelaraskan ketukan video referensi atau musik VO tetap).
- Tanpa `"mulai"`, durasi otomatis dibagi proporsional mengikuti jumlah kata `narasi` dan panjang file `vo`, atau nilai `"durasi"` masing-masing adegan.

### `opsi` & `animasi_opsi` (Mekanisme Pop-Up Set)
Properti set diteruskan ke fungsi pembangun diorama `dunia.py` setiap frame. Gunakan `animasi_opsi` untuk menganimasikan kunci numerik/boolean sepanjang adegan:
- `t`: waktu relatif adegan (detik) atau `"kata:<teks>"`.
- `dur`: lama transisi nilai ke target baru.
- `ease`: `"halus"`, `"linear"`, `"pental"`, `"cepat"`, `"lambat"`.
- Kunci yang dapat dianimasikan bergantung set:
  - `meja_hp`: `mode_pintu` (`bool`), `buka_pintu` (`0..1`)
  - `kota_jam`: `pop_jam` (`0..1`), `buka_pintu_kanan` (`0..1`)
  - `ruang_pintu`: `buka_pintu` (`0..1`)
  - `labirin_pintu`: `pintu_tengah_pop` (`0..1`), `pintu_buka_semua` (`0..1`)
  - `lipat_meja`: `pop_notif` (`0..1`)

### Elemen Overlay 2D (`balon`, `teks`, `efek`) & `sfx`
- `balon`: `{"tokoh": "luna", "t": 0.5, "dur": 2.0, "teks": "...", "gaya": "bicara"|"pikir"|"teriak"}`
- `teks`: `{"t": 0.2, "dur": 2.0, "teks": "...", "pos": "atas"|"tengah"|"bawah", "ukuran": 52}`
- `efek`: `{"t": 1.2, "dur": 0.8, "jenis": "kaget"|"kilau"|"hati"|"marah"|"tanya", "tokoh": "luna"}`
- `sfx`: `{"t": 1.1, "jenis": "pintu"|"lipat"|"notif"|"pop"|"ding"}`

### Panel Komik (`tipe: "komik"`)
Setel `"tipe": "komik"` pada adegan untuk merender komposisi grid panel komik datar 2–4 kotak dalam satu layar bergaya kolase kertas.
