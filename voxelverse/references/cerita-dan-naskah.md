# Dari Naskah ke Video Diorama 3D VoxelVerse

## A. Hanya Ide / Topik
1. Tulis naskah ringkas, ber-ritme lisan (kalimat 6–15 kata per adegan), dengan **hook visual di 0–3 detik pertama**.
2. Tampilkan naskah ke user dan minta **satu kali** file VO + rasio (`16:9` atau `9:16`). Jika user ingin preview tanpa suara, buat draf bisu (`"vo": null`).

## B. Ada VO + Naskah (Zero-Prompt)
1. Jalankan `proyek_baru.py` untuk mendapatkan `DURASI_VO`.
2. Pecah naskah menjadi adegan berurutan tanpa ada kata yang terlewat.
3. Tentukan untuk tiap adegan:
   - Lokasi (`latar`), waktu (`pagi`/`siang`/`sore`/`malam`), dan cuaca (`cerah`/`hujan`/`salju`).
   - Pemeran & aksi (pastikan pose & ekspresi berubah mengikuti kalimat; karakter tidak berdiri kaku > 4 detik).
   - Sudut & gerak kamera 3D (kombinasikan minimal 4 jenis: `luar_jendela`, `bahu_kiri`, `orbit`, `terbang`, `ikut`, `crane`, `push`, `pull`).
   - Cahaya & efek (`percikan` di kabel, `bohlam`, `flash`, `vinyet`).

## C. Prinsip Sutradara 3D
- **Manfaatkan kedalaman 3D:** letakkan elemen latar depan (kusen jendela, pot tanaman, tiang lampu) agar saat kamera bergerak terasa efek paralaks ruang yang nyata.
- **Cahaya bercerita:** di adegan `malam` atau `sore` berhujan, gunakan `robo`, `monitor_kode`, `lampu_gantung`, atau `tram` untuk menciptakan titik cahaya hangat kontras dengan birunya hujan.
- **Jangan tabrakan dinding:** saat mengatur `pos` kamera di dalam ruangan (`studio_kode`, `kamar`, `kafe`), jaga agar `pos` berada di dalam batas dinding atau sengaja di luar jendela (`luar_jendela`).
- **Verifikasi visual wajib:** selalu periksa `out/qc/sheet.jpg` dan `strip_NN.jpg` sebelum render penuh.
