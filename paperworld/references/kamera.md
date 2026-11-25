# Kamera 3D & Transisi — PaperWorld

Mesin `Cam3D` memproyeksikan diorama kertas 3D menggunakan proyeksi perspektif dengan dukungan FOV dinamis, lintasan lengkung *Catmull-Rom* (`terbang`), pembingkaian otomatis berbasis `fokus` + `sudut`, dan efek mekanis kamera (`punch`, `goyang`, `miring`, `ayun`).

## Konfigurasi Dasar `kamera` dalam Adegan

```json
"kamera": {
  "awal": {
    "fokus": "luna",
    "ukuran": "sedang",
    "sudut": "serong_kanan",
    "fov": 42
  },
  "gerak": [
    { "t": 0.4, "dur": 1.6, "jenis": "push", "ke": { "ukuran": "dekat" }, "ease": "io" },
    { "t": 2.1, "dur": 1.4, "jenis": "orbit", "sudut": -28, "dy": 0.25 }
  ]
}
```

Alternatif eksplisit dengan koordinat absolut `(x, y, z)` (ideal untuk masuk melewati ambang pintu atau menyapu meja diorama):

```json
"kamera": {
  "awal": { "pos": [0.25, 1.55, 4.1], "target": [0.0, 1.05, 0.0], "fov": 44 },
  "gerak": [
    {
      "t": 0.2,
      "dur": 2.2,
      "jenis": "pindah",
      "ke": { "pos": [0.25, 1.22, 0.45], "target": [0.25, 1.15, -2.5], "fov": 42 },
      "ease": "io"
    }
  ]
}
```

## Preset `ukuran` & `sudut`

| Preset `ukuran` | Jarak (m) | Tinggi Tambahan | FOV Bawaan | Kegunaan |
| :--- | :---: | :---: | :---: | :--- |
| `sangat_lebar` | `8.2` | `+2.2` | `50` | Panorama kota jam / labirin dari atas |
| `lebar` | `4.6` | `+0.85` | `45` | Seluruh ruangan / meja lipat penuh |
| `penuh` | `3.3` | `+0.45` | `44` | Tubuh penuh + sekitar pintu |
| `sedang` | `2.2` | `+0.35` | `40` | Pinggang ke atas / dua tokoh |
| `dekat` | `1.45` | `+0.22` | `36` | Ekspresi wajah / reaksi |
| `sangat_dekat` | `0.95` | `+0.12` | `32` | Close-up detail / mata kaget |
| `aerial` | `+12.0` atas | `+8.5` Z | `48` | Tampak burung penuh dari ketinggian |

Pilihan `sudut`: `depan`, `kanan`, `kiri`, `belakang`, `serong_kanan`, `serong_kiri`.
Pilihan `ease`: `io`, `linear`, `in`, `out`, `back`, `snap`.

## Jenis Gerakan (`gerak[].jenis`)

| Jenis | Parameter Utama | Efek |
| :--- | :--- | :--- |
| `pindah` | `ke: {pos, target, fov}` | Interpolasi posisi, titik lihat, dan FOV kamera |
| `push` / `mendekat` | `kali` atau `ke: {ukuran}` | Maju mendekat ke subjek / masuk ambang pintu |
| `pull` / `menjauh` | `kali` atau `ke: {ukuran}` | Mundur memperlihatkan konteks set yang lebih luas |
| `orbit` | `sudut` (derajat), `dy` | Mengitari titik target di bidang horizontal |
| `terbang` | `via: [[x,y,z], ...]`, `ke: {pos, target}` | Lintasan lengkung Catmull-Rom melewati *waypoint* |
| `crane` | `ke: {dx, dy, dz, target_dy}` atau `ke: {pos, target}` | Naik-turun dramatis (mis. menjauh ke atas `labirin_pintu`) |
| `ikut` | `fokus`, `lag`, `offset` | Mengikuti langkah tokoh secara dinamis |
| `pan` | `dx` atau `ke: {target, fokus}` | Menolehkan pandangan horizontal |
| `tilt` | `dy` atau `ke: {target}` | Mendongak atau menunduk |
| `potong` | `ke: {pos, target, fov}` | *Jump-cut* instan di tengah adegan |
| `zoom_cepat` | `ke: {ukuran, fov}` | *Crash zoom* cepat |
| `whip` | `ke: {pos, target}` | Putaran/geser kamera cepat |
| `punch` | `kuat`, `dur` | Sentakan FOV sesaat saat kejutan/notifikasi |
| `goyang` | `kuat`, `dur` | Getaran kamera organik |
| `miring` | `r` / `roll` | Memiringkan cakrawala kamera |
| `fokus` | `blur` | Efek *depth-of-field* lembut |
| `ayun` | `periode`, `kuat` | Ayunan ambien lembut |

## Transisi Antar-Adegan (`transisi`)

Atur pada level objek adegan (`"transisi": "potong"` atau `"transisi": {"jenis": "...", "dur": 0.4}`):
- `potong` — potong langsung (*hard cut*), paling cocok mengikuti ketukan musik/VO cepat.
- `fade` — memudar halus.
- `flash` — kilatan kertas putih saat portal pintu terbuka terang.
- `iris` — bukaan lingkaran dari tengah frame.
- `geser` — geser horizontal halaman.
- `whip` — sapuan gerak cepat antar-adegan.
- `wipe` — sapuan tirai kertas bersih.
