# Kamera 3D Sinematik — Panduan VoxelVerse

Mesin VoxelVerse memakai **kamera perspektif 3D penuh** (`pos`, `target`, `fov`, `roll`, `blur`), sehingga perubahan sudut seperti `orbit`, `terbang` melewati jendela, `bahu_kiri`, hingga `crane` di atas kota benar-benar mengubah perspektif ruang dan pantulan lantai.

> Dunia: lantai `y = 0.0`, atas = `+Y`, depan = `+Z`, kanan = `+X`. Tinggi tokoh dewasa/chibi voxel ±`1.75` m.

---

## 1. Ukuran & Sudut Bidikan (`kamera.awal` / `ke`)

| `ukuran` | jarak / sudut | kegunaan |
|---|---|---|
| `sangat_lebar` | `7.8m`, FOV `50°` | Memperkenalkan skala kota, taman, atau gedung |
| `lebar` | `4.5m`, FOV `45°` | Default adegan bercerita, jalan kaki, 2–3 tokoh |
| `penuh` | `3.2m`, FOV `44°` | Aksi tubuh penuh (lompat, peregangan, sorak) |
| `sedang` | `2.15m`, FOV `40°` | Dialog meja, ekspresi + gestur tangan |
| `dekat` | `1.42m`, FOV `36°` | Momen emosi, reaksi wajah, kacamata & mata |
| `sangat_dekat` | `0.94m`, FOV `32°` | Klimaks dramatis, fokus mata/benda kecil |
| `luar_jendela` | luar (`z=3.65`) menembus jendela bata `studio_kode` | Pembuka atmosferik hujan melihat ke dalam studio hangat |
| `bahu_kiri` / `bahu_kanan` | *over-the-shoulder* menatap monitor kode & kota di luar | Menunjukkan layar kode + karakter + robo + latar hujan |
| `balik_wajah` | dari sisi monitor berbalik menatap wajah karakter + rak buku | Reaksi karakter saat tersenyum, berpikir, atau peregangan |
| `aerial` | tinggi (`+11m`) menatap ke bawah | Penutup epik di atas `kota_hujan` |

Bidik manual penuh juga didukung kapan saja: `"pos": [x, y, z], "target": [tx, ty, tz], "fov": 42`.
`fokus` menerima id tokoh (`"kribo"`, `"arka"`, `"robo"`), daftar `["kribo","nadia"]`, `"monitor"`, `"jendela"`, atau `"tram"`.

---

## 2. Katalog Gerakan 3D (`kamera.gerak[]`)

Setiap gerakan: `{"jenis": ..., "t"|"kata": ..., "dur": 1.5, "ease": "io", "ke": {...}}`.

| `jenis` | efek 3D | parameter | pemakaian |
|---|---|---|---|
| `pindah` | interpolasi halus ke pose kamera baru | `ke`, `dur` | Serbaguna |
| `push` / `mendekat` | dolly mendekati `target` | `kali` (default `1.55`) atau `ke` | Fokus emosi, ketegangan, detail layar |
| `pull` / `menjauh` / `reveal` | dolly mundur membuka ruang | `kali` (default `1.65`) atau `ke` | Reveal lokasi, rasa lega, penutup |
| `orbit` | kamera mengitari `target` secara horizontal | `sudut` (derajat, mis. `35` / `-25`), `dy` | Menunjukkan kedalaman diorama 3D & rak buku |
| `terbang` / `fly_through` | jalur kurva 3D melengkung melewati rintangan | `ke`, `via: [[x,y,z], ...]` | Terbang dari monitor menembus jendela ke tiang listrik |
| `crane` | naik tinggi sambil menunduk (`dy`, `dz`) | `ke: {dy, dz, target_dy}` | Penutup sinematik di atas jalan kota / sekolah |
| `ikut` | **tracking 3D** mengikuti tokoh berjalan atau `tram` | `fokus`, `offset: [dx,dy,dz]`, `lag`, `sampai` | Adegan jalan kaki, tram melaju di hujan |
| `pan` / `tilt` | menoleh kiri-kanan / atas-bawah | `dx` / `dy` / `ke.target` | Mengikuti pandangan atau pindah fokus |
| `potong` | jump cut instan 1 frame | `ke` | Ritme cepat, pergantian sudut tegas |
| `zoom_cepat` | snap FOV/posisi cepat (`0.25s`) | `ke` | Kejutan, punchline |
| `whip` | sapuan cepat + blur gerak | `ke`, `dur` (`0.38s`) | Pindah lokasi/karakter dengan energi tinggi |

### Overlay Kamera Hidup (bisa ditumpuk)
- `punch`: hentakan zoom singkat (`kuat`: `0.08–0.22`) + bunyi *thud*
- `goyang`: guncangan kamera (`kuat`: `4–14`, `dur`)
- `miring`: dutch angle (`r`: derajat `2–6`)
- `fokus`: rack focus DOF blur (`blur`: `4–8`)
- `ayun`: goyang lembut melayang (`kuat`, `periode`, `sampai`)

---

## 3. Transisi Antar Adegan (`transisi`)

`potong`, `fade`, `flash`, `whip`, `geser`, `iris`, `zoom`, `kedip`, `wipe`.
Jika `latar` atau `waktu` berbeda dan `transisi` tidak ditulis, mesin otomatis memilih `fade` (`0.45s`).
