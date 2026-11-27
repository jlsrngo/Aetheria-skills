# Laporan Perbaikan Visual, Karakter, Transisi, dan Gerak (`stikman-cerita`)

Dokumen ini merangkum akar masalah visual & animasi pada skill 2D **`stikman-cerita`** beserta arsitektur perbaikan yang telah diterapkan pada [`tokoh.py`](scripts/tokoh.py), [`dunia.py`](scripts/dunia.py), [`film.py`](scripts/film.py), dan [`adegan.py`](scripts/adegan.py).

---

## 1. Perbaikan Karakter Utama (`Kribo`) & Anatomi Maskulin (`scripts/tokoh.py`)

### A. Akar Masalah Sebelumnya
1. **Wajah terlalu bulat & terkesan feminin/cewek**:
   - Rasio tinggi-lebar mata terlalu bulat (`eh ≈ ew`), kelopak mata atas melengkung tinggi seperti busur boneka, warna iris coklat-kuning terang dengan kilau bulat besar (*puppy eyes*), ditambah *blush* pink di pipi dan alis melengkung tipis.
2. **Rambut terlihat kaku / runcing atau tidak bertekstur**:
   - Bentuk awal terlalu menyerupai bola brokoli polos atau duri tentakel lancip, tanpa tekstur helai ikal berlapis.
3. **Badan & baju kotak / tampak terpotong / ketekuk**:
   - Torso berbentuk persegi panjang kaku; titik pangkal lengan kulit (`cap=True`) menyembul di atas bahu kaos; serta terdapat garis lipatan dada yang membuat kaos tampak tertekuk saat karakter menunjuk.
4. **Celana & sepatu datar**:
   - Kaki hanya berupa 1 garis tebal lurus (`c.line`) dan sepatu pipih menghadap samping luar (`<- ->`).

### B. Cara Perbaikan yang Diterapkan
1. **Mata Hitam-Obsidian Tajam & Wajah Maskulin Tirus (`_eye_ref` & `wajah_chibi_ref`)**:
   - **Proporsi Mata Cowok (*Half-Lidded Sharp Male Eye*)**: Lebar horizontal `ew = 19.2`, tinggi vertikal diperpendek ke `eh = 13.4` dengan bentuk poligonal tegas.
   - **Kelopak Atas Miring Menukik**: Garis kelopak atas dibuat lurus-menukik tajam ke arah pangkal hidung (sudut dalam lebih rendah daripada sudut luar) dan memotong sedikit bagian atas iris, menghasilkan tatapan fokus/garang khas karakter cowok anime.
   - **Iris Hitam-Obsidian (`(22, 22, 26)`)**: Inti pupil hitam legam (`(8, 8, 10)`), sabit bawah *charcoal-steel* gelap (`(72, 76, 86)`), bayangan *sclera* atas di bawah kelopak (`(18, 18, 22, 115)`), dan kilau putih kecil-tajam (`2.8 × 2.3`).
   - **Alis Tebal Menukik & Garis Pangkal Alis (*Brow Ridge*)**: Alis poligon hitam-arang (`(24, 20, 22)`) didekatkan ke mata (`eye_y - 21.5`) dengan kemiringan tajam ke arah tengah + garis *brow ridge* tipis.
   - **Kontur Rahang Tirus Maskulin**: Pipi meramping dari `x = ±79` ke sudut rahang tegas (`jawline angle` di `y = +44, x = ±71`) lalu meruncing ke dagu cowok tanpa *blush* pink.
2. **Rambut Kribo Ikal Berhelai 3-Tone (`_hair_back_ref` & `_hair_front_ref`)**:
   - Menggunakan warna dasar hitam-espresso pekat (`(24, 20, 22)`), 24 gumpalan ikal tepi, 22 sulur helai ikal lepas (*loose curly wisps*) di tepi luar, serta cincin konsentris ratusan busur helai ikal (`arc_pts`) 3-nada (`(14, 10, 12)`, `(78, 54, 46)`, `(128, 94, 80)`).
3. **Kaos A-Line Rapi, Dasi Kupu Besar, Celana Jogger & Sepatu 3/4 (`_kaos_chibi`, `_sleeve_chibi`, `jog_mode`)**:
   - Menghapus garis lipatan dada yang membuat baju tampak tertekuk; menutup pangkal bahu lengan kaos dengan elips bahu mulus; memperbesar dasi kupu-kupu **1.38×**.
   - Celana *jogger* longgar bervolume dengan jahitan *fly*, strip putih-hitam di sisi luar kaki kanan, manset karet pergelangan kaki, serta **sepatu sneaker chunky perspektif 3/4** (lengkap dengan lidah sepatu tinggi, 3 strip tali sepatu, highlight *toe-box*, dan pita sol karet tebal berlekuk).

---

## 2. Perbaikan Gaya Latar & Kendaraan Studio Ghibli Soft (`scripts/dunia.py`)

### A. Akar Masalah Sebelumnya
- Warna latar terlalu kontras/tajam, rumput hanya blok hijau datar, awan seragam, pohon bulat polos, dan interior terlalu sempit dengan perabot menempel ke atap.

### B. Cara Perbaikan yang Diterapkan
1. **Palet Ghibli Soft Desaturated (`LANGIT`, `bukit_berlapis`, `rumput`)**:
   - Gradasi langit *cerulean-cream* hangat, bukit jauh *atmospheric haze*, padang rumput bergelombang (*rolling swells*) dengan rumpun rumput 2-nada (`_rumpun_ghibli`) dan bunga detail (`bunga_detail` *daisy* 6 kelopak & *tulip* 3 lapis).
2. **4 Varian Awan & 7 Spesies Pohon Painterly (`_ghibli_canopy`)**:
   - Awan `kumulus`, `tipis`, `gumpal_lebar`, dan `puncak_jauh` dengan *warm cream highlight* & *mauve-blue belly shadow* tanpa garis tepi hitam kasar.
   - 7 pohon Ghibli (`rimbun`, `bulat_tinggi`, `cemara`, `sakura`, `palem`, `gugur`, `beringin`) menggunakan teknik 5-lapis tumpukan dedaunan *painterly*.
3. **Interior Ghibli (`meja_makan` / `dapur`) & 4 Kendaraan Ghibli**:
   - Dinding *teal-sage* bergradasi hangat, balok kayu langit-langit, berkas sinar matahari diagonal (*sunbeams*) dari jendela kanan, bayangan rak diagonal, dan tanaman pot *terracotta*.
   - Penambahan fungsi kendaraan: `mobil_ghibli`, `kereta_ghibli`, `bus_ghibli`, dan `sepeda_ghibli`.

---

## 3. Perbaikan Transisi Monoton -> Smart Contextual Auto-Transition (`scripts/film.py`)

### A. Akar Masalah Sebelumnya
Pada [`film.py`](scripts/film.py) baris 140–142 lama:
```python
if tr is None or tr == "auto":
    same = prev.s.get("latar") == sc.s.get("latar") and prev.s.get("waktu") == sc.s.get("waktu")
    tr = {"jenis": "potong"} if same else {"jenis": "geser", "dur": 0.5}
```
Akibatnya, seluruh video yang memakai `"transisi": "auto"` (atau tidak menulis field `transisi`) hanya mengulang **`"potong"`** dan **`"geser"`**, padahal [`aset_global/transisi.py`](../aset_global/transisi.py) memiliki **22 transisi sinematik**.

### B. Cara Perbaikan yang Diterapkan (`Film.trans_of`)
Fungsi `trans_of(self, j)` di [`film.py`](scripts/film.py#L135-L192) kini memilih transisi secara cerdas berdasarkan konteks perubahan adegan:
1. **Adegan Panel Komik (`tipe == "komik"`)**:
   - Otomatis memakai `{"jenis": "halaman", "arah": "kiri", "dur": 0.60}` (*page-curl*).
2. **Lokasi Sama, Waktu Berubah (`siang` -> `sore` / `malam` = *Time-Lapse*)**:
   - Rotasi antara `luma` (*radial*), `blur_cross`, dan `silang` (`dur: 0.60–0.65s`).
3. **Lokasi Sama & Waktu Sama (Dialog / Aksi Berkelanjutan)**:
   - Mayoritas tetap memakai *hard-cut* (`potong`) agar ritme dialog tajam, namun **setiap adegan ke-3 (`j % 3 == 0`)** otomatis diselingi `blur_cross` (`0.38s`) atau `whip` (`0.32s`) agar pergantian shot tidak kaku.
4. **Pindah Lokasi (`latar` Berbeda)**:
   - **Latar Outdoor** (`jalan`, `taman`, `kota`, `pantai`, `hutan`, `sawah`, dll.): rotasi antara `wipe_tiang` (*foreground pillar wipe* khas anime), `whip` (*fast pan*), `wipe_diagonal`, `geser`, dan `zoom`.
   - **Latar Indoor** (`kamar`, `kelas`, `meja_makan`, `kafe`, `kantor`, dll.): rotasi antara `iris`, `tirai`, `luma` (*horizontal*), `halaman`, dan `blur_cross`.

---

## 4. Perbaikan Gerak Monoton & Arah Hadap 3/4 / Samping (`scripts/adegan.py` & `scripts/tokoh.py`)

### A. Akar Masalah Sebelumnya
1. **`st["hadap"]` terputus di `adegan.py`**:
   - Pada `Aktor.state()` lama di [`adegan.py`](scripts/adegan.py), field `hadap` dari JSON hanya dipakai untuk membalik `flip = -1 / 1`, tetapi **tidak pernah dimasukkan ke dictionary `st["hadap"]`** yang dikirim ke `Tokoh.draw(c, st)`.
   - Akibatnya, karakter selalu digambar menghadap lurus ke depan kamera (`turn = 0.0`) seperti patung kertas.
2. **Karakter mematung kaku saat berbicara panjang**:
   - Saat `pose="diam"` dan karakter berbicara (`bicara: true`), hanya mulut yang bergerak (*lipsync*), sedangkan kepala, badan, dan tangan diam kaku.
3. **Berjalan tampak depan (*crab-walk*)**:
   - Saat berjalan ke kiri/kanan, badan tetap menghadap penonton sementara kaki bergeser menyamping.

### B. Cara Perbaikan yang Diterapkan
1. **Integrasi Penuh `hadap` (`"depan"`, `"miring"` 3/4, `"samping"` Side-Profile) di `Aktor.state()` ([`adegan.py`](scripts/adegan.py#L206-L285))**:
   - `"hadap": "kanan"` / `"kiri"` / `"miring"` / `"3/4"` -> otomatis mengaktifkan **mode 3/4 (`hadap_mode = "miring"`, `turn = 0.55`)** beserta `flip` yang sesuai, sehingga karakter yang berdialog saling berhadapan serong 3/4 secara natural.
   - `"hadap": "samping"` / `"samping_kiri"` / `"samping_kanan"` -> mengaktifkan **mode profil samping (`hadap_mode = "samping"`, `turn = 0.92`)**.
   - **Auto Side-Profile Saat Jalan/Lari**: Saat `walking` (`gaya in ("jalan", "lari")`), `hadap_mode` otomatis berpindah ke `"samping"` (`turn = 0.92`) dengan ayunan lengan maju-mundur berlawanan fase kaki, tekukan lutut ke arah jalan (`knee_bend`), dan kedua sepatu menghadap searah langkah.
2. **Micro-Gesture Otomatis Saat Berbicara (`Aktor.state()` di [`adegan.py`](scripts/adegan.py#L266-L279))**:
   - Ketika `talk_level(t)` aktif pada pose `"diam"` / `"santai"`, karakter otomatis melakukan gerakan hidup yang halus:
     - Anggukan kepala ritmis mengikuti intensitas suara (`tilt += sin(t * 3.1) * 2.4 * (0.4 + 0.6 * talk)`).
     - Goyangan tumpuan tubuh lembut (`lean += sin(t * 1.8) * 1.2`).
     - Gerakan tangan kanan ekspresif ringan saat menekankan kata (`lift_t` mengikuti amplop suara VO).
