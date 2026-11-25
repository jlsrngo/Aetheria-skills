# Dunia Diorama 3D & Properti Voxel

Semua dunia menggunakan koordinat meter 3D (`y = 0` lantai, `+Y` atas, `+Z` depan).

## Daftar 13 Set Diorama (`latar`)

| `latar` | deskripsi | posisi penting untuk tokoh / kamera |
|---|---|---|
| `studio_kode` | Ruang kerja coding hangat berdinding rak buku belakang, jendela bata besar + tanaman luar, monitor kode menyala, lampu gantung, pemandangan kota hujan di luar jendela | Kursi kerja: `[0.08, 0.0, 0.36]`, `hadap: "depan"`. Meja atas untuk `robo`: `[0.64, 0.775, 1.05]` |
| `kota_hujan` | Jalan aspal basah memantul, trotoar, rel tram, tram krem-teal melaju, gedung bata dengan jendela hangat & balkon, tiang listrik + kabel udara, lampu jalan | Trotoar kiri: `x = -5.1, y = 0.10`. Kabel listrik kiri: `x = -4.35, y = 4.45..4.82` |
| `kamar` | Kasur + bantal + selimut, nakas + jam weker digital, jendela langit | Kasur: `[-1.35, 0.56, -1.55]` (`pose: "tidur"` atau `"duduk_sorak"`) |
| `ruang_belajar` | Meja kayu, laptop, buku, kursi, lampu meja hangat | Kursi: `[0.0, 0.0, -0.42]`, `hadap: "belakang"` |
| `ruang_tamu` | Sofa biru empuk, karpet, meja kopi, lampu lantai hangat | Sofa: `[0.0, 0.0, -1.35]` |
| `sekolah_luar` | Gedung sekolah bertuliskan `papan` (default `"SMP VOXEL"`), tiang bendera, halaman rumput & pohon | Halaman depan: `x = -3..3, z = 0..4` |
| `kelas` | Papan tulis (`papan_tulis`), 6 set meja-kursi siswa | Tengah depan papan: `[0.0, 0.0, -2.0]` |
| `taman` | Bangku kayu taman, jalan setapak, lampu jalan, pohon rindang | Jalan setapak: `x = -1..1, z = -4..4` |
| `kafe` | Konter kayu hangat, dua meja bundar + cangkir kopi uap, lampu gantung | Samping meja kiri/kanan: `x = ±0.55, z = 0.6` |
| `atap_kota` | Atap gedung berpagar besi dengan latar gedung bertingkat menyala | Tengah atap: `x = -2..2, z = -2..2` |
| `halte` | Halte beratap teal di pinggir `kota_hujan` beraspal basah | Trotoar halte: `[4.35, 0.10, 0.0]` |
| `padang` | Bukit hijau bertingkat & pepohonan voxel | Tengah padang: `x = -4..4, z = -4..4` |
| `polos` | Panggung studio bersih berwarna (`warna`) untuk judul/penjelasan | Tengah: `[0.0, 0.0, 0.0]` |

## Properti 3D (`benda[]` / `bawa`)
`monitor_kode`, `keyboard`, `mug_kopi`, `kursi_kerja`, `lampu_gantung`, `lampu_jalan`, `tram`, `jam_weker`, `laptop`, `hp`, `buku`, `stik`, `bola`, `kado`, `payung`, `pensil`.
