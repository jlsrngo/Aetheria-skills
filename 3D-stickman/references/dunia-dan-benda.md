# Dunia & Properti 3D — 3D-stickman

## 21 Set Diorama 3D Skala Luas

| Set (`latar`) | Cocok untuk | Opsi khusus |
|---|---|---|
| `kamar_belajar` | Pembuka, belajar, cerita Kribo di kamar, lampu hias hangat, jendela, tempat tidur, kalender & poster pesawat, rak buku, meja belajar | `bulan`, `tahun`, `sub_kalender`, `judul_poster` |
| `ruang_kerja` | Ruang kerja/istana, karpet merah, pilar, jendela, peta Indonesia, kalender, bendera Merah Putih, meja kerja besar | `bulan`, `tahun` |
| `warung` | Warung kelontong luas, kanopi belang biru-krem, rentengan sachet, papan harga, karung BERAS/GULA, jalan depan | `bulan`, `tahun`, `harga` |
| `hanggar` | Hanggar pesawat/pabrik luas, rangka baja, poster Terbang Perdana, banner hanggar, model pesawat | `banner` |
| `gedung_sidang` | Panggung podium luas, tirai merah, bendera Merah Putih, layar LED skor/voting, kamera TV tripod | `tahun`, `kiri_lbl`, `kiri_val`, `kanan_lbl`, `kanan_val` |
| `kampus` | Kompleks gerbang kampus/sekolah, zebra cross, 3 gedung bertingkat, gerobak bakso, lampu jalan, pohon | `banner` |
| `kelas` | Papan tulis hijau lebar, jam dinding, jendela samping, meja guru & barisan meja murid | `judul`, `baris1`, `baris2` |
| `bank_kas` | Loket bank/penukaran uang, lantai kotak-kotak, layar LED kurs, pintu brankas baja | `judul`, `kiri_lbl`, `kiri_val` |
| `jalan_kota` | Jalan raya kota lebar, marka jalan, 8 gedung skyline, lampu jalan otomatis malam/sore, 2 mobil 3D, pohon, awan | — |
| `polos` | Panggung studio terang bersih berskala luas untuk explainer fokus penuh ke tokoh/properti | — |
| `taman_kota` | Taman terbuka dengan jalan setapak, kolam air mancur, bangku taman, lampu jalan, pohon, awan | — |
| `kafe` | Kedai kopi hangat dengan meja bar, papan menu, meja bundar, cangkir kopi, jendela | `judul`, `baris1`, `baris2` |
| `studio_berita` | Studio TV/podcast modern dengan layar LED raksasa, strip neon, dan meja presenter | `judul`, `kiri_lbl`, `kiri_val` |
| `rumah_sakit` | Ruang klinik/rumah sakit dengan simbol palang medis, ranjang pasien, dan meja dokter | — |
| `kantor_startup` | Kantor modern dengan jendela besar, *sprint board*, dan meja monitor ganda | `judul`, `baris1`, `baris2` |
| `laboratorium` | Ruang riset sains dengan layar data LED, meja lab, dan tabung reaksi berwarna | `judul`, `kiri_lbl`, `kiri_val`, `kanan_lbl`, `kanan_val` |
| `stasiun` | Peron stasiun kereta dengan rel ganda, gerbong kereta 3D, atap peron, papan jadwal LED | `judul`, `kiri_lbl`, `kiri_val`, `kanan_lbl`, `kanan_val` |
| `pantai` | Hamparan pasir pantai, laut biru dengan buih ombak, payung pantai, kursi santai, dan pohon kelapa | — |
| `perpustakaan` | Ruang perpustakaan dengan 5 rak buku tinggi, meja baca panjang, dan lampu baca klasik | — |
| `pengadilan` | Ruang sidang hukum dengan mimbar hakim bertingkat, meja jaksa/pengacara, bendera, dan pagar pengunjung | — |
| `halte_bus` (alias `halte`, `bus`, `bus_stop`) | Halte bus kota: trotoar luas, shelter beratap dengan bangku duduk, papan nama HALTE BUS KOTA, layar LED jadwal kedatangan, tiang rambu, tempat sampah, gedung kota, lampu jalan, mobil lewat, dan bus kota 3D beroda | `banner`, `judul`, `kiri_lbl`, `kiri_val`, `kanan_lbl`, `kanan_val`, `bus`, `bus_x` |

### Opsi `halte_bus`

- `bus`: `"datang"` (bus meluncur masuk & berhenti, 2,6 dtk), `"diam"` (bus berhenti di halte), `"pergi"` (bus menjauh), `"lewat"` (bus melintas), atau `"tidak"` (tanpa bus).
- `bus_x`: posisi bus manual pada sumbu X (mis. `-7.6` agar bus terlihat di kejauhan), menimpa `bus`.
- Layar LED memakai `judul`, `kiri_lbl`, `kiri_val`, `kanan_lbl`, `kanan_val`. Kosongkan `kanan_lbl` untuk tampilan satu kolom (mis. `kiri_lbl: "BUS 01 · RUTE KOTA"`, `kiri_val: "BERANGKAT"`).

## Properti 3D (`benda`)

### Properti Cerita & Diorama Umum
`kalender`, `poster`, `peta`, `papan_tulis`, `layar_led`, `pesawat`, `karung`, `bendera`, `podium`, `buku`, `laptop`, `kopi`.

### Properti & Animasi 3D Engineering (Portingan `explainer_kit` — Full Lokal CPU)
Dapat dipanggil langsung di daftar `benda` pada `proyek.json` (seluruh animasi berjalan otomatis mengikuti waktu adegan `t`):

| Jenis (`jenis`) | Deskripsi & Gerakan | Opsi utama |
|---|---|---|
| `panah_3d` | Panah 3D bercahaya (batang + kerucut ujung) dengan denyut halus (`pulse_scale`) untuk menunjuk arah aliran/gaya | `awal` `[x,y,z]`, `akhir` `[x,y,z]`, `warna`, `tebal`, `pulsa` (`true`/`false`) |
| `aliran_pipa` | Pipa 3D cutaway mengikuti jalur *polyline* + partikel tetes fluida yang mengalir berulang (*looping*) di dalam pipa | `jalur` (`[[x,y,z], ...]`), `r_pipa`, `r_dot`, `warna`, `kecepatan`, `jarak`, `cutaway` |
| `dial_gauge` | Meteran/jarum penunjuk mekanik 3D (RPM / BAR / °C) dengan zona merah berbahaya & jarum bergerak dinamis | `x`, `y`, `z`, `nilai_awal`, `nilai_akhir`, `dur`, `maks`, `satuan`, `skala`, `rot_y` |
| `tag_callout` | Label teknis melayang 3D + garis *leader* menunjuk titik target + efek muncul *pop-in overshoot* (`pop_scale`) | `judul`, `sub`, `x`, `y`, `z`, `target` `[x,y,z]`, `muncul`, `warna` |
| `tangki_air` | Tangki fluida 3D cutaway transparan-depan dengan permukaan air naik-turun & tint warna dinamis | `x`, `y`, `z`, `level_awal`, `level_akhir`, `dur`, `warna_awal`, `warna_akhir`, `skala` |
| `piston_3d` | Mesin 4-silinder 3D animasi penuh: *crankshaft* berputar, batang *conrod*, 4 piston naik-turun sesuai fase (0-180-180-0°), dan kilatan pembakaran oranye saat TDC | `x`, `y`, `z`, `rpm`, `silinder`, `skala` |
