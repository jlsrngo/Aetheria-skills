# Dunia & Benda — PaperWorld

Tersedia **12 set diorama 3D** pada `dunia.py` dan **11 prop karton 3D** pada `benda.py`.

## Daftar 12 Set Diorama & Landmark Koordinat

### A. 6 Set Utama Bergaya Referensi Pop-Up
1. **`meja_hp`** (Meja kerajinan hangat + jam weker + ponsel bertumpuk + pintu `"5 MENIT"`)
   - Jam weker raksasa: `(-2.15, 0.0, -0.65)`
   - Tumpukan HP kertas: `(0.25, 0.0, 0.25)` (permukaan atas `y = 0.24`)
   - Pintu pop-up `"5 MENIT"`: `(0.25, 0.25, 0.0)` menghadap `+Z`
   - Opsi: `mode_pintu` (`bool`), `buka_pintu` (`0..1`)
2. **`kota_jam`** (Alun-alun cerah + Menara Jam `"1 JAM"` + koridor pintu kanan)
   - Bundaran kuning depan: `(0.0, 0.015, 3.8)`
   - Menara jam biru: `(0.0, 0.0, -9.2)`, papan `"1 JAM"` di `(0.0, 5.85, -8.3)`
   - Pintu hero kanan (koral): `(2.95, 0.0, 1.2)` menghadap `-X` (plus pintu mint di `z=-1.6`, biru di `z=-4.2`)
   - Opsi: `pop_jam` (`0..1`), `buka_pintu_kanan` (`0..1`)
3. **`ruang_pintu`** (Kamar pastel mint bergaris + karpet salmon + lukisan gunung + pintu `"SATU PINTU lagi"`)
   - Pintu biru jendela bulat: `(0.0, 0.0, -2.30)` pada dinding lengkung terbuka di `z = -2.4`
   - Lukisan gunung di dinding kiri: `(-3.0, 2.15, -0.5)`
   - Opsi: `buka_pintu` (`0..1`)
4. **`panggung_kertas`** (3 zona diorama berdampingan sepanjang sumbu `X`)
   - **Zona 1 (`x = -4.5`)**: dinding polkadot kuning + podium drum kuning (`[-4.5, 0.36, -0.35]` tempat `kucing` berdiri melambai)
   - **Zona 2 (`x = 0.0`)**: latar malam biru tua bertabur bintang, bulan sabit, bukit hijau, ikan biru, pintu cahaya dengan siluet bertanduk (`rusa`) di `(0.0, 0.0, -0.95)`
   - **Zona 3 (`x = +4.5`)**: dinding garis jingga hangat + pintu cahaya bermahkota sinar matahari (*sunburst*) di `(4.5, 0.0, -0.95)`
5. **`labirin_pintu`** (Koridor tengah + dinding labirin spiral + puluhan pintu terbuka serentak)
   - Koridor utama: `x = -1.3..+1.3, z = -8.2..+4.2`
   - Pintu tengah pop-up: `(0.0, 0.0, -1.6)`
   - Jaringan labirin spiral: `x = -6.0..+6.0, z = -10.8..+5.8`
   - Opsi: `pintu_tengah_pop` (`0..1`), `pintu_buka_semua` (`0..1`)
6. **`lipat_meja`** (Brosur lipat 6 panel + pensil raksasa + jam weker + HP notifikasi `"1"`)
   - Brosur lipat mint 6 panel: `z = 2.6..4.4`
   - Pensil kuning & biru: `z = 5.2, 5.9`
   - Jam weker kiri: `(-3.1, 0.0, -1.4)`
   - HP raksasa: `(0.2, 0.0, -1.6)` dengan kartu Play merah + lencana `"1"` (posisi aman tokoh: `[0.95, 0.25, -0.25]`)
   - Opsi: `pop_notif` (`0..1`)

### B. 6 Set Cerita Tambahan
7. **`kamar_kertas`** (`kamar`) — Kamar tidur diorama (kasur, jendela, meja belajar, rak buku)
8. **`sekolah_kertas`** (`sekolah`) — Gerbang & halaman gedung sekolah karton pastel
9. **`kelas_kertas`** (`kelas`) — Papan tulis hijau kapur & deretan meja belajar karton
10. **`taman_kertas`** (`taman`) — Bangku taman, lampu jalan, pohon kertas berlapis
11. **`kafe_kertas`** (`kafe`, `kantin`) — Meja bundar, cangkir, etalase kafe hangat
12. **`polos`** — Latar studio kertas netral bersih (untuk demonstrasi produk/karakter)

## 11 Prop 3D (`benda[]` di Adegan)
Tambahkan prop tambahan lewat array `benda` pada `adegan`:
`pintu_kertas`, `kartu_pita`, `hp_kertas`, `jam_weker_kertas`, `menara_jam`, `pensil_kertas`, `pohon_kertas`, `lampu_taman_kertas`, `buku`, `kado`, `payung`.

```json
"benda": [
  { "jenis": "kado", "pos": [1.1, 0.0, 0.6], "rot": [0, 20, 0], "skala": 1.1 }
]
```
