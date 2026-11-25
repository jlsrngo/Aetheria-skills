# Panduan Cerita, Naskah, & Subtitle — PaperWorld

Bahasa visual PaperWorld adalah **metafora lipatan dan pintu kertas**: setiap transisi pikiran atau perpindahan masalah direpresentasikan dengan **membuka pintu**, **menyingkap halaman lipat**, atau **munculnya kartu teks 3D fisik** di dalam diorama.

## Kaidah Penulisan Adegan PaperWorld
1. **Gunakan metafora fisik kertas**:
   - Batasi waktu atau distraksi → set `meja_hp` + pintu `"5 MENIT"` terbuka dari layar ponsel.
   - Tekanan jam & rutinitas → set `kota_jam` dengan Menara Jam `"1 JAM"` dan koridor banyak pintu.
   - Keraguan / satu percobaan lagi → set `ruang_pintu` bertajuk `"SATU PINTU lagi"`.
   - Dunia imajinasi / emosi dalam → tiga zona `panggung_kertas` (kucing polkadot, malam bintang & bayangan rusa, fajar matahari).
   - Kebuntuan / banyak pilihan → `labirin_pintu` dengan gerakan `crane` menarik kamera tinggi memperlihatkan labirin penuh pintu.
   - Kembali ke realitas → `lipat_meja` berakhir di notif ponsel `"1"` dan wajah kaget.
2. **Durasi shot singkat & dinamis**:
   - Rata-rata `1.5–3.5 detik` per ketukan visual agar ritme *pop-up* terasa hidup.
   - Selalu berikan pergerakan kamera (`push`, `pull`, `crane`, `orbit`, `pindah`) atau animasi set (`animasi_opsi`) agar tidak ada adegan statis kaku.
3. **Kontrol `ekor` dan Audio**:
   - Jika tidak memakai `vo` atau memakai generator musik internal, biarkan `"ekor": 0.9`, `"musik": "auto"`, `"sfx": true`, `"subtitle": true`.
   - Jika menyelaraskan persis dengan berkas rekaman audio/VO berdurasi tetap yang sudah lengkap dengan musik/SFX (`vo: "input/vo.m4a"`), gunakan `"ekor": 0.02`, `"musik": "none"`, `"sfx": false`, `"subtitle": false`.

## Gaya Subtitle `"kertas"`
Gaya bawaan `"kertas"` menampilkan kata-kata narasi pada kartu karton krem-putih bersudut membulat tipis dengan warna sorot aktif (`KORAL`) dan bayangan jatuh halus, menyatu dengan estetika buku cerita *pop-up*.

## Checklist Sebelum Render Final
1. Jalankan `python scripts/render.py <proyek> --stills auto --draft`.
2. Buka `out/qc/sheet.jpg` via `read_file` dan periksa:
   - Posisi kaki karakter menapak bidang (`y = 0.0`, `y = 0.25` di atas `hp_kertas`, `y = 0.36` di atas podium `kucing`).
   - Karakter tidak tertembus daun pintu atau dinding.
   - Kartu papan (`"5 MENIT"`, `"1 JAM"`, `"SATU PINTU lagi"`) terbaca jelas dan tidak terpotong batas rasio `9:16` / `16:9`.
3. Jalankan render akhir `python scripts/render.py <proyek> --ulang` lalu `python scripts/audio.py <proyek>` dan cek status **`FINAL OK`**.
