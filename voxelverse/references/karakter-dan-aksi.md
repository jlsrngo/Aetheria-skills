# Karakter 3D Voxel, Ekspresi, & Pose

Semua tokoh dibangun dari rig balok 3D artikulasi penuh (`tokoh.py`) dengan skala lokal `1.0 ≈ 1.75 meter` (kaki di `y = 0.0`, menghadap `+Z` secara default).

## Pemeran Bawaan (`PRESET`)

| id | deskripsi |
|---|---|
| `kribo` | **Wajib ada — Chibi 3D berambut afro hitam penuh**, kacamata kotak bingkai tebal, kulit peach, kaos teal + dasi kupu-kupu hitam, celana gelap, sneaker hitam-putih |
| `arka` | Developer gaya video referensi: rambut blok hitam berjambul, kacamata kotak, hoodie teal bertali putih, celana gelap |
| `robo` | Robot pendamping/lampu meja oranye-teal dengan layar wajah bercahaya (`PointLight` aktif) & antena (gunakan `pos: [0.64, 0.775, 1.05]` di atas meja `studio_kode`) |
| `nadia` | Chibi hijab hitam modern 3D, kacamata bulat, blazer krem di atas kemeja putih, rok gelap |
| `raka` | Siswa rambut jambul, seragam putih + dasi biru |
| `bimo` | Siswa rambut keriting, seragam putih + dasi biru |
| `dimas` | Siswa berkacamata kotak, seragam putih + dasi biru |
| `sari` | Siswi berhijab putih, dasi merah, rok gelap |
| `tika` | Siswi rambut kuncir, dasi merah, rok gelap |
| `ayah` | Kemeja biru muda, berkumis, celana navy |
| `ibu` | Hijab hijau, blus krem, rok coklat |
| `guru` | Rambut beruban, berkacamata, berkumis, dasi merah tua |
| `bu_guru` | Hijab ungu, berkacamata bulat, blus lavender |
| `kakek` | Peci hitam, berkumis & berjenggot |
| `adik` | Anak perempuan rambut bob, baju kuning (`skala: 0.8`) |
| `kucing` | Kucing voxel oranye dengan ekor bergoyang |

## 21 Ekspresi (`ekspresi`)
`senang` · `tenang` · `fokus` · `tertawa` · `kaget` · `marah` · `mikir` · `sedih` · `malu` · `ngantuk` · `menguap` · `tidur` · `semangat` · `panik` · `bangga` · `jahil` · `cemberut` · `cemas` · `lega` · `terpana` · `datar`
(Alias: `senyum`, `kecewa`, `bingung`, `ketawa`, `heran`, `kesal`, `takut`).

## Pose 3D (`pose`)
- **Berdiri & gestur:** `diam`, `santai`, `lambai`, `lambai2`, `tunjuk`, `tunjuk_kiri`, `tunjuk_atas`, `ide`, `pinggang`, `jempol`, `silang`, `sorak`, `peregangan`, `garuk`, `mikir`, `dagu`, `kaget`, `sedih`, `marah`, `kepal`, `menyerahkan`, `angkat_tangan`, `angkat_bahu`, `tepuk`, `menguap`, `pegang_dada`, `hormat`, `membungkuk`, `lihat_jendela`, `pegang_hp`, `pegang_buku`, `menulis`.
- **Gerak:** `jalan`, `lari`, `berjinjit` (otomatis aktif saat ada `ke_pos` / `ke_x` / `ke_z`).
- **Duduk:** `duduk`, `duduk_santai`, `duduk_ketik` (atau `ketik`, kedua tangan mengetik dinamis!), `duduk_peregangan` (merentangkan kedua tangan ke atas sambil duduk), `duduk_nulis`, `duduk_game`, `duduk_hp`, `duduk_kopi`, `duduk_sorak`.
- **Rebah:** `tidur`.

## Ikon Emosi 3D (`aksi[].efek`)
`bohlam` (memancarkan cahaya `PointLight`!), `tanda_seru`, `tanya`, `hati`, `bintang`, `kilau`, `zzz`, `centang`, `silang`, `keringat`, `not`.
