# Format `proyek.json` — 3D-stickman

```json
{
  "mesin": "3D-stickman",
  "judul": "Judul Video",
  "ukuran": [1080, 1920],
  "fps": 30,
  "vo": "input/vo.mp3",
  "musik": "auto",
  "mood_musik": "ceria",
  "subtitle": true,
  "gaya_subtitle": "kata",
  "tokoh": {
    "kribo": "kribo",
    "sari": "sari"
  },
  "adegan": [ ... ]
}
```

- `gaya_subtitle`: `"kata"` (1–2 kata besar putih beroutline hitam di tengah bawah, default 3D-stickman), `"komik"`, `"sinematik"`, atau `"pil"`.
- `mood_musik`: `ceria`, `sinematik`, `lofi`, `santai`, `hangat`, `sedih`, `tegang`, `semangat`, `lucu`, `misteri`, `malam`.

## Field per adegan

- `latar`: nama set dari `dunia-dan-benda.md` (21 set: `kamar_belajar`, `ruang_kerja`, `warung`, `hanggar`, `gedung_sidang`, `kampus`, `kelas`, `bank_kas`, `jalan_kota`, `polos`, `taman_kota`, `kafe`, `studio_berita`, `rumah_sakit`, `kantor_startup`, `laboratorium`, `stasiun`, `pantai`, `perpustakaan`, `pengadilan`, `halte_bus`).
- `waktu`: `"pagi"`, `"siang"`, `"sore"`, atau `"malam"`.
- `narasi`: teks VO adegan ini.
- `durasi`: detik (dipakai jika `vo: null`).
- `opsi` (atau langsung di root adegan): `tahun`, `bulan`, `sub_kalender`, `banner`, `judul`, `baris1`, `baris2`, `harga`, `kiri_lbl`, `kiri_val`, `kanan_lbl`, `kanan_val`, `judul_poster`, `bus`, `bus_x`.
- `tokoh`: daftar aktor di adegan.
  - `id`, `dasar`, `pos` `[x, y, z]` (atau `x`, `y`, `z`), `skala`, `pose`, `ekspresi`, `hadap` (`depan`, `serong_kanan`, `serong_kiri`, `kanan`, `kiri`, `belakang`, atau sudut derajat angka), `gerak` (`"aktif"` default, `"ekspresif"`, `"tenang"`, `"kaku"`), `bawa` (`buku_terbuka`, `pesawat_mini`, `kopi`, `hp`), `bicara` (`true` atau `[[t0, t1]]`).
  - `aksi`: daftar event berurutan `{"kata": "...", "pose": "...", "ekspresi": "...", "hadap": "...", "durasi_putar": 0.6, "durasi_pose": 0.4, "efek": "ide", "ke_pos": [x,y,z], "durasi": 1.6, "gaya": "jalan"|"jalan_santai"|"mengendap"|"mundur"|"lari"|"lompat"|"geser", "hadap_akhir": "depan"}` (bisa pakai `t` detik jika tanpa VO). Perubahan `hadap` otomatis berputar mulus (tidak patah).
  - `jalur`: daftar waypoint berjalan berurutan `[{"ke_pos": [x,y,z], "durasi": 1.8, "gaya": "jalan_santai", "jeda": 0.4}, ...]`.
  - `mondar_mandir`: gerak patroli otomatis `{"jarak": 0.7, "sumbu": "x"|"z", "siklus": 4.5, "gaya": "jalan_santai"}`.
  - `masuk` / `keluar`: `{"dari": "kiri", "gaya": "jalan", "dur": 0.9, "hadap_akhir": "depan"}` / `{"ke": "kanan", "gaya": "jalan_santai", "dur": 1.2}`.
- `benda`: properti tambahan `{"jenis": "kalender"|"poster"|"peta"|"papan_tulis"|"layar_led"|"pesawat"|"karung"|"bendera"|"podium"|"buku"|"laptop"|"kopi", "pos": [x,y,z], ...}`.
- `kamera`: `{"awal": {"ukuran": "sedang", "fokus": "kribo", "sudut": 10}, "gerak": [...]}`.
- `balon`: `[{"tokoh": "kribo", "teks": "Halo!", "t": 0.2, "sampai": 2.5}]`.
- `teks`: `[{"teks": "FAKTA #1", "gaya": "seru", "pos": [0.5, 0.14], "t": 0.1, "sampai": 2.2}]`.
- `efek`: `[{"jenis": "flash"|"vinyet"|"garis_kecepatan", "t": 0.0, "sampai": 1.5}]`.
- `transisi`: `"auto"`, `"potong"`, `{"jenis": "fade"|"whip"|"geser"|"flash"|"iris"|"zoom"|"wipe"|"kedip"|"putar"|"belah", "dur": 0.35}`.
