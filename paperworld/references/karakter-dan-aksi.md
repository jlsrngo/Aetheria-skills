# Karakter & Aksi — PaperWorld

Seluruh tokoh di `tokoh.py` dibuat oleh kelas `TokohKertas` dari potongan karton berlapis (*paper cutout* dengan tebal fisik, warna tepi karton krem `KERTAS_TEPI`, dan lipatan engsel *pop-up*).

## 13 Preset Tokoh Bawaan

| ID Preset | Ciri Khas Desain Karton 3D | Kegunaan Umum |
| :--- | :--- | :--- |
| `luna` | Rambut bob coklat + jambul melengkung (*ahoge*), syal kuning berumbai, mantel koral berkancing kuning, kaki biru | Pemeran utama referensi PaperWorld |
| `kribo` | Rambut afro awan hitam bergelombang, kacamata kotak, baju teal, dasi kupu-kupu hitam, *sneaker* | Pemeran wajib ekosistem Aetheria-Skills |
| `nadia` | Hijab hitam modern, kacamata bulat, blazer krem di atas kemeja putih, rok gelap | Sahabat / partner cerita kribo |
| `kucing` | Kucing kuning karton berlapis, telinga tajam, pita leher merah, kaki membulat | Maskot pop-up lucu di atas drum kuning |
| `raka` | Rambut jambul hitam, seragam putih berdasi biru, celana navy | Murid / tokoh pria muda |
| `bimo` | Rambut keriting coklat tua, seragam putih berdasi biru | Teman sekolah |
| `dimas` | Rambut rapi, kacamata kotak, seragam putih berdasi biru | Tokoh kutu buku |
| `sari` | Hijab putih bersih, dasi merah, rok navy | Murid perempuan |
| `tika` | Rambut kuncir hitam, dasi merah, rok navy | Tokoh aktif / ceria |
| `ayah` | Rambut kelabu-tua rapi, berkumis, kemeja biru muda, skala `1.06` | Tokoh orang tua |
| `ibu` | Hijab hijau, blus krem hangat, rok coklat tua, skala `1.02` | Tokoh ibu |
| `guru` | Rambut beruban, berkumis & kacamata kotak, dasi merah tua, skala `1.05` | Guru / mentor |
| `adik` | Rambut bob, atasan kuning, rok pink, skala `0.82` | Adik kecil |

### Kustomisasi Tokoh di `proyek.json`
```json
"tokoh": {
  "hero": { "dasar": "kribo", "kemeja": "koral", "kacamata": "bulat" },
  "luna": "luna"
}
```
Warna menerima string preset (`putih`, `hitam`, `merah`, `koral`, `biru`, `biru_muda`, `teal`, `pink`, `kuning`, `oranye`, `hijau`, `ungu`, `coklat`, `abu`, `navy`, `krem`, `kulit`) maupun `[R, G, B]`.

## Arah Hadap (`hadap`)
- `"depan"` (`+Z`), `"belakang"` (`-Z`), `"kiri"` (`-X`), `"kanan"` (`+X`), atau sudut derajat langsung.

## 21 Ekspresi (`ekspresi`)
- **Netral & Ceria**: `tenang`, `senang`, `tertawa`, `semangat`, `bangga`, `malu`, `lega`, `jahil`
- **Fokus & Penasaran**: `fokus`, `mikir`, `datar`
- **Kaget & Emosi Kuat**: `kaget`, `terpana`, `panik`, `marah`, `cemberut`
- **Lelah & Emosi Lembut**: `sedih`, `cemas`, `ngantuk`, `menguap`, `tidur`
- **Alias yang Didukung**: `senyum`, `senyum_kecil`, `ceria`, `penasaran`, `kecewa`, `bingung`, `ketawa`, `heran`, `kesal`, `takut`

## 25 Pose (`pose`)
- **Berdiri & Ekspresif**: `diam`, `santai`, `mikir`, `kaget`, `sedih`, `marah`, `angkat_bahu`, `silang`, `pinggang`, `jempol`
- **Tangan & Interaksi**: `lambai`, `lambai2`, `tunjuk`, `tunjuk_kiri`, `tunjuk_atas`, `buka_pintu`, `ide`, `sorak`, `peregangan`, `garuk`
- **Gerak & Istirahat**: `jalan`, `lari`, `duduk`, `duduk_sorak`, `tidur`
- **Alias yang Didukung**: `angkattangan`, `tepuk`, `menari`, `pikir`

## Masuk & Keluar Lipatan Pop-Up (`masuk` / `keluar`) & `aksi`

Khusus PaperWorld, karakter dapat muncul melipat tegak dari permukaan datar (`"dari": "lipat"`) atau berjalan masuk dari samping/belakang:

```json
{
  "id": "luna",
  "pos": [0.45, 0.25, 1.35],
  "hadap": "belakang",
  "pose": "diam",
  "ekspresi": "tenang",
  "masuk": { "t": 0.0, "dur": 0.6, "dari": "lipat" },
  "aksi": [
    { "t": 0.1, "ke_pos": [0.25, 0.25, 0.55], "durasi": 0.9, "gaya": "jalan" },
    { "t": 1.0, "pose": "buka_pintu", "ekspresi": "penasaran" }
  ]
}
```
Parameter pergerakan karakter dalam `aksi[]`:
- `t`: waktu relatif adegan atau `"kata:<teks>"`
- `ke_pos`: koordinat tujuan `[x, y, z]` dengan `durasi` dan `gaya` (`"jalan"` atau `"lari"`)
- `pose`, `ekspresi`, `hadap`, `bicara` (`true`/`false`), `bawa`, `lihat`, `skala`, `pop_up` (`0.0..1.0`)
- `ikon`: munculkan ikon reaksi 3D (`hati`, `kaget`, `tanya`, `lampu`, `bintang`) di atas kepala.
