# Format `proyek.json` — VoxelVerse

```json
{
  "judul": "Dunia Kecil VoxelVerse",
  "ukuran": [1080, 1920],
  "fps": 30,
  "vo": "input/vo.mp3",
  "musik": "auto",
  "mood_musik": "sinematik",
  "vol_musik": 0.17,
  "subtitle": true,
  "gaya_subtitle": "sinematik",
  "fade_masuk": 0.5,
  "fade_keluar": 0.8,
  "sfx": true,
  "tokoh": {
    "kribo": "kribo",
    "arka": "arka",
    "robo": "robo",
    "nadia": "nadia"
  },
  "adegan": [ ... ]
}
```

## Field per Adegan

| field | isi |
|---|---|
| `latar` | `studio_kode` `kota_hujan` `kamar` `ruang_belajar` `ruang_tamu` `sekolah_luar` `kelas` `taman` `kafe` `atap_kota` `halte` `padang` `polos` |
| `waktu` | `pagi` `siang` `sore` `malam` |
| `cuaca` | `cerah` (default) · `hujan` · `gerimis` · `salju` (partikel 3D + suara hujan otomatis di `audio.py`) |
| `basah` | `true/false` — pantulan cahaya jendela, lampu jalan, dan tram di atas aspal `kota_hujan` |
| `narasi` | Potongan naskah persis untuk jadwal adegan, subtitle, dan pemicu `"kata"` |
| `musik` | `sinematik lofi ceria santai hangat sedih tegang semangat lucu misteri malam` |
| `tokoh` | Daftar aktor 3D (`pos: [x,y,z]`, `hadap`, `pose`, `ekspresi`, `aksi`, `masuk`, `keluar`, `bicara`) |
| `kamera` | `{"awal": ..., "gerak": [...]}` |
| `percikan` | Efek percikan listrik 3D menyala sepanjang jalur koordinat: `[{"t"|"kata": .., "dur": 1.8, "jalur": [[x,y,z], ...], "warna": [255,224,130], "kuat": 2.8}]` |
| `benda` | Properti bebas 3D: `[{"jenis": "mug_kopi", "pos": [x,y,z], "rot": [rx,ry,rz], "skala": 1.0}]` |
| `balon` | Gelembung dialog di atas kepala tokoh 3D: `[{"oleh": "nadia", "teks": "...", "t": 0.8, "sampai": 4.0}]` |
| `teks` | Overlay layar: `judul`, `kapsul`, `seru`, `kata_besar` |
| `efek` | Efek layar penuh: `flash`, `gelap`, `vinyet`, `garis_kecepatan`, `bar` |
| `sfx` | Efek suara tambahan: `[{"t"|"kata": .., "jenis": "spark|ketik|tram|ding|pop|whoosh|thud|alarm|kilat", "gain": 1}]` |
| `transisi` | Transisi masuk adegan: `potong`, `fade`, `flash`, `whip`, `geser`, `iris`, `zoom`, `kedip`, `wipe` |
| `opsi` / langsung | `jam` (`"07:00"`), `alarm` (`true`), `papan` (`"SMP VOXEL"`), `papan_tulis`, `selimut`, `tram_z`, `ketik_progres`, `spark_layar`, `build_layar` |

## Mode Panel Komik 3D (`"tipe": "komik"`)
Sama seperti `stikman-cerita`: `"grid": [3, 2]`, `"panel": [{"muncul": ..., "latar": ..., "tokoh": [...], "kamera": ...}]`, dengan opsi `"zoom": {"panel": 3, "t": ..., "dur": 1.2}`.
