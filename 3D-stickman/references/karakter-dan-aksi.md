# Karakter, Ekspresi, Pose & Ikon — 3D-stickman

## Pemeran Bawaan (`PRESET`)

| ID | Ciri Utama |
|---|---|
| `kribo` | **Tokoh utama wajib.** Kepala bola + rambut afro hitam 3D penuh, kacamata kotak tebal, kaos teal, dasi kupu-kupu hitam, celana gelap, sneaker hitam-putih. |
| `bos` | Botak berkacamata bulat, mata kartun putih ber-outline, jas gelap + dasi merah runcing. |
| `habibie` | Jas gelap, dasi merah, kacamata tipis, kumis putih, rambut rapi abu-putih. |
| `presiden` | Jas gelap, dasi merah, kacamata tipis, kumis putih, peci hitam. |
| `nenek` | Ibu warung berambut sanggul putih, kacamata bulat, baju ungu. |
| `raka` | Rambut jambul coklat, kaos hijau toska. |
| `bimo` | Rambut keriting coklat, kaos oranye. |
| `dimas` | Rambut rapi hitam, kacamata kotak, kemeja putih + dasi biru. |
| `sari` | Hijab putih, kemeja hijau toska, rok navy. |
| `tika` | Rambut kuncir dua hitam, kaos kuning. |
| `pejabat` | Jas gelap, dasi biru tua. |
| `mahasiswa` | Rambut belah tengah, kaos biru muda. |
| `pedagang` | Topi koki putih, kumis, kaos putih. |
| `guru` | Rambut uban, kacamata kotak, kumis, kemeja krem + dasi merah tua. |
| `detektif` | Gaya noir: topi fedora, trench coat abu-coklat, kemeja putih + dasi gelap, celana gelap. |
| `insinyur` | Helm proyek kuning mengilap, rompi safety oranye dengan strip reflektor, kemeja biru. |
| `zaki` | Gaya punk/anak motor: rambut jabrik biru terang, kaos ungu lengan pendek, celana gelap, sneaker. |
| `maya` | Reporter modis: rambut bob coklat + bando kuning, blazer coral/merah muda, bulu mata, rok gelap. |
| `dodi` | Gaya street: topi baseball terbalik merah + poni, kacamata hitam mengilap, kaos biru, kalung emas, sneaker. |

## 39 Ekspresi Wajah

`senang`, `tenang`, `fokus`, `tertawa`, `kaget`, `marah`, `mikir`, `sedih`, `malu`, `ngantuk`, `menguap`, `tidur`, `semangat`, `panik`, `bangga`, `jahil`, `cemberut`, `cemas`, `lega`, `terpana` (mata bintang emas), `datar`, `kagum`, `cinta` (mata hati), `pusing` (mata spiral), `licik`, `melet` (julur lidah), `syok` (pupil mengecil), `tersipu`, `sinis`, `menangis` (air mata mengalir), `meratap` (mata terpejam + air mata mengalir), `ngakak` (mata `> <` + tawa lebar), `murka` (melotot marah menganga), `bengong` (mata kecil datar), `gugup` (mulut zig-zag gemetar), `kewalahan` (keringat + air mata mengalir), `murung` (bayangan suram dahi), `bosan`, `pede`.

Alias yang didukung: `senyum`, `kecewa`, `bingung`, `skeptis`, `ketawa`, `heran`, `kesal`, `takut`, `takjub`, `serius`, `nangis`, `jatuh_cinta`, `mabuk`, `iseng`, `euforia`, `heboh`, `menang`, `mengamuk`, `geram`, `hampa`, `gemetar`, `stres`, `depresi`, `down`, `malas`, `bete`, `puas`, `nangis_diam`, `sedih_berat`.

## Pose & Siklus Gerak 3D Stickman (55+ Pose)

- **Pose berdiri & ekspresi:** `diam`, `semangat`, `santai`, `lambai`, `lambai2`, `tunjuk`, `tunjuk_kiri`, `tunjuk_atas`, `ide`, `pinggang`, `jempol`, `silang`, `sorak`, `peregangan`, `garuk`, `mikir`, `dagu`, `kaget`, `sedih`, `marah`, `kepal`, `menyerahkan`, `angkat_tangan`, `angkat_bahu`, `tepuk`, `menguap`, `pegang_dada`, `hormat`, `membungkuk`, `pegang_hp`, `pegang_buku`, `pegang_pesawat`, `pegang_kopi`, `pidato`.
- **Siklus & pose gerak aktif (anti-kaku):**
  - **Lokomosi (tekuk lutut per-kaki + torso counter-twist):** `jalan`, `jalan_santai`, `mengendap`, `mundur`, `lari`.
  - **Gesture & reaksi dinamis:** `bicara_aktif` (tangan bergantian menjelaskan), `mengamati` (menyapu pandangan sambil pegang dagu), `gelisah` (menoleh kiri-kanan waspada), `mengancam` (condong maju menunjuk tegas), `terkejut_mundur` (tersentak defensif), `gemetar` (gemetar takut/dingin), `menoleh` (menengok curiga), `angguk` (mengangguk setuju), `geleng` (menggeleng menolak).
- **Pose duduk & tidur:** `duduk`, `duduk_santai`, `duduk_ketik`, `duduk_nulis`, `duduk_kopi`, `duduk_sorak`, `tidur`.

## Tingkat Keluwesan Gerak (`gerak` per aktor)

| Nilai `gerak` | Efek |
|---|---|
| `"aktif"` *(default)* | Pernapasan, ayunan berat badan, gerak kepala alami & gesture bicara otomatis |
| `"ekspresif"` | Gerak tubuh, kepala & ayunan gesture lebih tegas (cocok untuk presenter/antagonis dramatis) |
| `"tenang"` | Gerak idle lembut & halus |
| `"kaku"` | Matikan gerak idle otomatis (hanya pose murni) |

## Ikon Emosi 3D (`efek` pada aksi tokoh)

`ide` (lampu menyala + PointLight), `tanda_tanya`, `seru`, `hati`, `bintang`, `marah`, `zzz`, `uang`.
