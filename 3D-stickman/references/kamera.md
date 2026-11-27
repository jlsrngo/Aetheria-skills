# Kamera 3D — 3D-stickman

## Ukuran Bidikan (`kamera.awal.ukuran`)

| Nama | Jarak relatif | Keterangan |
|---|---|---|
| `ekstrem_dekat` | super rapat | Fokus mata/mulut untuk momen syok atau plot twist |
| `sangat_dekat` | sangat rapat | Fokus ekspresi wajah & kacamata |
| `dekat` | close-up | Kepala + bahu + dasi/kerah |
| `sedang` | medium shot | Pinggang ke atas (ideal untuk explainer) |
| `penuh` | full body | Seluruh tubuh + lantai + properti sekitar |
| `lebar` | wide shot | Ruangan & beberapa tokoh sekaligus |
| `sangat_lebar` | establishing | Panorama set ruangan penuh |
| `panorama` | ultra wide | Memamerkan skala penuh 20 set dunia 3D |

### Parameter Komposisi (`kamera.awal` / `ke`)

- `fokus`: ID tokoh (mis. `"kribo"`), daftar ID (`["kribo", "sari"]`), atau `target: [x, y, z]`.
- `sudut`: sudut azimut kamera dalam derajat (`0` tepat dari depan, `12`–`25` sedikit serong agar 3D berdimensi).
- `angle`: preset sudut vertikal (`"normal"`, `"bawah"` / low angle, `"atas"` / high angle, `"burung"` / bird's eye, `"dutch"` / horizon miring).
- `sudut_v`: offset ketinggian kamera manual (satuan meter).
- `bahu`: komposisi *over-the-shoulder* di belakang bahu tokoh A menghadap `fokus` tokoh B (opsional `sisi_bahu: 1.38`).
- `kamera.gaya`: gaya getar/nafas kamera (`"tripod"` diam total, `"halus"` default, `"handheld"` kasual, `"tegang"` bergetar cepat).

## Gerak Kamera (`kamera.gerak`)

- `push`: zoom/maju mendekat (`zoom`, `faktor`, `dur`, `t`/`kata`).
- `pull`: mundur menjauh (`zoom`, `faktor`, `dur`).
- `punch_in`: zoom-in super cepat (`faktor`, `zoom`, `dur: 0.2`) untuk penekanan komedi/poin penting.
- `hentak`: impact zoom singkat lalu memantul balik (`kuat`, `dur: 0.25`).
- `dolly_zoom`: efek Vertigo (mundur sambil menyempitkan FOV, `faktor: 1.65`, `dur`).
- `orbit`: memutar mengelilingi target (`derajat`, `naik`, `dur`).
- `spiral`: gabungan `orbit` + `push`/`pull` + `crane` (`derajat`, `faktor`, `naik`, `zoom`, `dur`).
- `crane`: naik/turun + maju (`naik`, `maju`, `ke`, `dur`).
- `truck`: geser sejajar ke samping/atas (`x`, `y`, `z`, `dur`).
- `pan`: kamera diam di tempat, target menoleh (`derajat`, `naik`, `dur`).
- `pindah_fokus`: geser target ke tokoh/objek lain dengan blur singkat (`fokus`/`target`, `blur`, `dur`).
- `terbang`: jalur 3D mulus dengan `jalur: [[x,y,z], ...]` + `fokus`.
- `ikut`: mengikuti tokoh bergerak (`fokus`, `offset`).
- `whip`: geser cepat + blur (`ke`, `dur`).
- `goyang`: getar kamera singkat saat momen kaget/hentakan (`kuat`, `dur`).
- `potong`: pindah bidikan instan tanpa transisi (`ke`).

### Contoh Penggunaan di `proyek.json`

```json
"kamera": {
  "gaya": "handheld",
  "awal": { "ukuran": "sedang", "fokus": "bos", "sudut": 14, "angle": "bawah" },
  "gerak": [
    { "kata": "ternyata", "jenis": "punch_in", "faktor": 0.62, "dur": 0.18 },
    { "kata": "semua", "jenis": "dolly_zoom", "faktor": 1.7, "dur": 1.2 },
    { "kata": "lihat", "jenis": "pindah_fokus", "fokus": "kribo", "dur": 0.6 }
  ]
}
```
