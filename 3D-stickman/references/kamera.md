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

### Parameter Komposisi (`kamera.awal` / `ke` / item di `kamera.shot`)

- `fokus`: ID tokoh (mis. `"kribo"`), daftar ID (`["kribo", "sari"]`), atau `target: [x, y, z]`.
- `sudut`: sudut azimut kamera dalam derajat (`0` tepat dari depan, `±15`–`±35` serong berdimensi, `±70` profil samping).
- `angle`: preset sudut vertikal (`"normal"`, `"bawah"` / low angle, `"rendah"` / dramatic worm's-eye, `"atas"` / high angle, `"burung"` / bird's eye, `"dutch"` / miring kanan, `"dutch_kiri"` / miring kiri).
- `sudut_v`: offset ketinggian kamera manual (satuan meter).
- `geser_x`: *Rule of Thirds* / *lead room* horizontal relatif sumbu kamera (mis. `-0.18` atau `+0.18` agar subjek tidak selalu mati di tengah).
- `bahu`: komposisi *over-the-shoulder* (OTS) profesional di belakang bahu tokoh A menghadap `fokus` tokoh B (opsional `sisi_bahu: ±1.08`, `jarak_bahu: 1.62`, `tinggi_bahu: 1.38`, `tinggi_fokus: 0.16` — disesuaikan dengan proporsi kepala chibi agar wajah lawan 100% jelas). Gunakan tanda `sisi_bahu` berlawanan untuk *reverse-shot* agar mematuhi **180-Degree Rule**.
- `kamera.gaya`: gaya getar/nafas kamera (`"tripod"` diam total, `"halus"` default, `"handheld"` kasual, `"tegang"` bergetar cepat).
- `sinemaskop: true` *(opsional di root proyek atau adegan)*: menambahkan bar letterbox sinematik 2.35:1.

## Multi-Shot Sinematik dalam 1 Adegan (`kamera.shot`) — Standar Profesional

**Jangan menaruh 1 sudut kamera statis sepanjang adegan > 4 detik!** Gunakan array `"shot"` di dalam `"kamera"` untuk merangkai multi-angle (Establishing Crane → Over-the-Shoulder A → Reverse-Shot OTS B → Close-Up Reaksi → Wide Pull-Out) secara langsung dalam satu adegan tanpa memecah aksi/dialog:

```json
"kamera": {
  "gaya": "halus",
  "shot": [
    { "t": 0.0, "ukuran": "lebar", "target": [0, 1.05, 0.3], "sudut": -24, "angle": "atas",
      "gerak": { "jenis": "crane", "naik": -0.75, "maju": -0.5 } },
    { "t": 2.4, "bahu": "pedagang", "fokus": "kribo", "sisi_bahu": 0.62, "geser_x": -0.14,
      "gerak": { "jenis": "push", "faktor": 0.88, "zoom": 4 } },
    { "t": 4.7, "bahu": "kribo", "fokus": "pedagang", "sisi_bahu": -0.62, "geser_x": 0.14,
      "gerak": { "jenis": "push", "faktor": 0.86, "zoom": 4 } },
    { "t": 7.1, "ukuran": "dekat", "fokus": "kribo", "sudut": -20, "angle": "bawah",
      "gerak": { "jenis": "orbit", "derajat": 16, "naik": 0.12 } },
    { "t": 8.5, "ukuran": "penuh", "fokus": ["kribo", "pedagang"], "sudut": 26,
      "gerak": { "jenis": "pull", "faktor": 1.24, "zoom": -4 } }
  ]
}
```

> Tiap item di `shot` otomatis me-reset `roll`/`blur` shot sebelumnya dan mendukung `"t"` atau `"kata"`, `gaya` kamera per shot, serta `"gerak"` tunggal maupun daftar gerak.

## Gerak Kamera (`kamera.gerak` / `shot[].gerak`)

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
- `ikut` / `tracking`: mengikuti tokoh bergerak secara dinamis (`fokus`, `jarak`, `sudut`, `derajat`, `tinggi` atau `offset`).
- `whip`: geser cepat + blur (`ke`, `dur`).
- `goyang`: getar kamera singkat saat momen kaget/hentakan (`kuat`, `dur`).
- `potong`: pindah bidikan instan tanpa transisi (`ke`, `dur: 0.01`).

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
