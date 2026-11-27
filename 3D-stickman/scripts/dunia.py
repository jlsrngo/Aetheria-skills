# -*- coding: utf-8 -*-
"""
dunia.py - 21 set diorama 3D skala luas untuk skill 3D-stickman + 4 waktu (pagi/siang/sore/malam).

Set tersedia:
  kamar_belajar · ruang_kerja · warung · hanggar · gedung_sidang
  kampus · kelas · bank_kas · jalan_kota · polos
  taman_kota · kafe · studio_berita · rumah_sakit · kantor_startup
  laboratorium · stasiun · pantai · perpustakaan · pengadilan · halte_bus
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from engine3d import (
    OUT, PUTIH, KRIM, HITAM, MERAH, MERAH_TUA, BIRU, BIRU_TUA, BIRU_MUDA,
    TEAL, TEAL_TUA, PINK, KUNING, ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA,
    KAYU, KAYU_TUA, UNGU, NAVY, ABU, ABU_TUA, BATA, font, mix, gelap, terang, euler_mat,
)
import benda as BD

LATAR_ALIAS = {
    "kamar": "kamar_belajar", "ruang_belajar": "kamar_belajar",
    "istana": "ruang_kerja", "kantor": "ruang_kerja", "ruang_tamu": "ruang_kerja",
    "pasar": "warung", "toko": "warung", "kelontong": "warung",
    "pabrik": "hanggar", "bandara": "hanggar", "lab": "hanggar",
    "sidang": "gedung_sidang", "podium": "gedung_sidang", "dpr": "gedung_sidang",
    "sekolah": "kampus", "universitas": "kampus",
    "ruang_kelas": "kelas",
    "bank": "bank_kas", "loket": "bank_kas", "kas_negara": "bank_kas",
    "jalan": "jalan_kota", "kota": "jalan_kota",
    "panggung": "polos", "studio": "polos",
    "taman": "taman_kota", "alun_alun": "taman_kota", "halaman": "taman_kota",
    "kopi": "kafe", "kedai": "kafe", "restoran": "kafe", "warkop": "kafe",
    "tv": "studio_berita", "podcast": "studio_berita", "berita": "studio_berita",
    "rs": "rumah_sakit", "klinik": "rumah_sakit", "igd": "rumah_sakit",
    "startup": "kantor_startup", "coworking": "kantor_startup", "meeting": "kantor_startup",
    "lab_sains": "laboratorium", "riset": "laboratorium", "kimia": "laboratorium",
    "kereta": "stasiun", "peron": "stasiun", "terminal": "stasiun",
    "halte_bus": "halte_bus", "halte": "halte_bus", "bus": "halte_bus", "bus_stop": "halte_bus",
    "laut": "pantai", "pulau": "pantai", "pesisir": "pantai",
    "perpus": "perpustakaan", "arsip": "perpustakaan",
    "hukum": "pengadilan", "hakim": "pengadilan", "ruang_sidang": "pengadilan",
}

SKY_PRESET = {
    "pagi":  ((172, 212, 246), (252, 232, 198), (0.56, 0.58, 0.62), (0.32, 0.28, 0.26), [0.5, 0.75, 0.4], [1.0, 0.95, 0.86], 0.72, (232, 226, 214)),
    "siang": ((108, 180, 244), (206, 234, 252), (0.58, 0.62, 0.68), (0.32, 0.32, 0.32), [0.42, 0.88, 0.38], [1.0, 0.98, 0.94], 0.78, (198, 224, 246)),
    "sore":  ((96, 84, 122),   (238, 162, 114), (0.46, 0.38, 0.38), (0.24, 0.20, 0.18), [-0.5, 0.45, 0.5], [1.0, 0.78, 0.54], 0.68, (166, 130, 116)),
    "malam": ((24, 30, 56),    (52, 60, 86),    (0.28, 0.30, 0.38), (0.16, 0.16, 0.20), [0.3, 0.8, -0.3], [0.65, 0.74, 0.95], 0.34, (40, 46, 66)),
}


def configure_sky(sc, o):
    w = o.get("waktu", "siang")
    top, bot, asky, agrd, sdir, scol, sint, fog = SKY_PRESET.get(w, SKY_PRESET["siang"])
    sc.set_sky(top, bot, asky, agrd, sdir, scol, sint, fog, fog_start=24.0, fog_density=0.014)


def _banner_tex(teks, bg=PUTIH, fg=HITAM, border=OUT):
    im = Image.new("RGBA", (440, 90), bg + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 436, 86], outline=border + (255,), width=5)
    d.text((220, 45), str(teks), font=font("judul", 30), fill=fg + (255,), anchor="mm")
    return im


# ------------------------------------------------------------------ komponen lingkungan reusable
def _awan_3d(sc, x, y, z, s=1.0):
    for dx, dy, r in ((-0.58, -0.06, 0.44), (0.0, 0.14, 0.58), (0.60, -0.04, 0.42)):
        sc.sphere((x + dx * s, y + dy * s, z), r * s, PUTIH, seg_u=10, seg_v=7, emissive=0.28)


def _langit_awan(sc, t=0.0):
    drift = math.sin(t * 0.15) * 0.4
    for cx, cy, cz, cs in (
        (-7.5, 6.2, -16.0, 2.2), (-2.0, 5.4, -14.0, 1.8),
        (3.8, 6.5, -17.5, 2.5), (9.2, 5.6, -15.0, 2.0),
    ):
        _awan_3d(sc, cx + drift, cy, cz, s=cs)


def _bukit_horizon(sc, y=0.0, z=-18.5, col=(102, 166, 98)):
    for bx, rx, ry in ((-13.0, 7.5, 3.2), (-4.5, 6.8, 2.8), (4.5, 7.2, 3.4), (13.5, 7.8, 3.0)):
        sc.sphere((bx, y - 0.6, z), (rx, ry, 4.5), col, seg_u=14, seg_v=8, hemi=True)


def _pohon_3d(sc, x, y, z, s=1.0, leaf_col=HIJAU):
    sc.drop_shadow(x, y, z, 0.46 * s, 0.46 * s, 0.24)
    sc.cylinder((x, y + 0.58 * s, z), 0.13 * s, 1.16 * s, COKLAT, outline=True, outline_w=0.01 * s)
    for dx, dy, dz, r in ((0.0, 1.42, 0.0, 0.56), (-0.30, 1.20, 0.12, 0.38), (0.30, 1.22, -0.10, 0.37)):
        sc.sphere((x + dx * s, y + dy * s, z + dz * s), r * s, leaf_col, seg_u=12, seg_v=8, outline=True, outline_w=0.012 * s)


def _tanaman_pot(sc, pos, y=None, z=None, s=1.0):
    if y is None and z is None:
        x, y, z = pos
    else:
        x = pos
    sc.drop_shadow(x, y, z, 0.24 * s, 0.24 * s, 0.20)
    sc.cylinder((x, y + 0.18 * s, z), 0.18 * s, 0.36 * s, BATA, seg_u=12, outline=True, outline_w=0.008 * s)
    for dx, dy, dz, r in ((0.0, 0.56, 0.0, 0.24), (-0.14, 0.48, 0.08, 0.17), (0.14, 0.50, -0.06, 0.17)):
        sc.sphere((x + dx * s, y + dy * s, z + dz * s), r * s, HIJAU, seg_u=10, seg_v=7, outline=True, outline_w=0.008 * s)


def _lampu_jalan(sc, x, y, z, arah=1, waktu="siang"):
    sc.drop_shadow(x, y, z, 0.22, 0.22, 0.22)
    sc.cylinder((x, y + 1.85, z), 0.055, 3.7, ABU_TUA, seg_u=10, outline=True, outline_w=0.008)
    sc.box((x + arah * 0.38, y + 3.65, z), (0.76, 0.08, 0.08), ABU_TUA, outline=True, outline_w=0.006)
    nyala = waktu in ("sore", "malam")
    sc.sphere((x + arah * 0.72, y + 3.55, z), 0.14, KUNING if nyala else PUTIH, emissive=0.95 if nyala else 0.15, outline=True, outline_w=0.008)
    if nyala:
        sc.add_light((x + arah * 0.72, y + 3.35, z), color=(255, 214, 130), intensity=1.35, radius=5.5, halo=0.26)


def _mobil_3d(sc, x, y, z, col=MERAH, rot_y=0.0, s=1.0):
    sc.drop_shadow(x, y, z, 0.95 * s, 0.55 * s, 0.26)
    sc.rbox((x, y + 0.36 * s, z), (1.75 * s, 0.44 * s, 0.88 * s), col, roundness=0.30, seg=2, rot=(0, rot_y, 0), outline=True, outline_w=0.01 * s)
    sc.rbox((x, y + 0.72 * s, z), (0.98 * s, 0.36 * s, 0.78 * s), BIRU_MUDA, roundness=0.28, seg=2, rot=(0, rot_y, 0), outline=True, outline_w=0.009 * s)
    for lx in (-0.54, 0.54):
        for lz in (-0.44, 0.44):
            rad = math.radians(rot_y)
            wx = x + (lx * math.cos(rad) + lz * math.sin(rad)) * s
            wz = z + (-lx * math.sin(rad) + lz * math.cos(rad)) * s
            sc.cylinder((wx, y + 0.17 * s, wz), 0.17 * s, 0.10 * s, HITAM, seg_u=12, rot=(90, rot_y, 0), outline=True, outline_w=0.006 * s)


def _bus_3d(sc, x, y, z, col=BIRU, rot_y=0.0, s=1.0):
    m = euler_mat(0, rot_y, 0)
    def wp(dx, dy, dz):
        v = m @ np.array([dx * s, dy * s, dz * s], dtype=np.float32)
        return (x + float(v[0]), y + float(v[1]), z + float(v[2]))
    sc.drop_shadow(x, y, z, 2.45 * s, 0.95 * s, 0.28)
    sc.rbox(wp(0.0, 1.04, 0.0), (4.8 * s, 1.56 * s, 1.78 * s), col, roundness=0.22, seg=2, mat=m, outline=True, outline_w=0.014 * s)
    sc.box(wp(0.0, 0.62, 0.0), (4.84 * s, 0.20 * s, 1.80 * s), KUNING, mat=m, bias=-0.08)
    # Kaca samping (kiri & kanan) + pintu depan
    for sz in (-0.90, +0.90):
        for wx in (-1.45, -0.45, +0.55):
            sc.box(wp(wx, 1.24, sz), (0.82 * s, 0.54 * s, 0.04 * s), BIRU_MUDA, mat=m, outline=True, outline_w=0.007 * s, bias=-0.12)
        sc.box(wp(+1.55, 1.00, sz), (0.66 * s, 1.02 * s, 0.04 * s), (150, 210, 240), mat=m, outline=True, outline_w=0.008 * s, bias=-0.12)
    # Kaca depan + papan rute + lampu depan/belakang
    sc.box(wp(+2.40, 1.22, 0.0), (0.05 * s, 0.64 * s, 1.46 * s), BIRU_MUDA, mat=m, outline=True, outline_w=0.008 * s, bias=-0.12)
    sc.box(wp(+2.41, 1.64, 0.0), (0.05 * s, 0.16 * s, 1.12 * s), HITAM, mat=m, bias=-0.14)
    for lz in (-0.56, +0.56):
        sc.sphere(wp(+2.40, 0.48, lz), 0.11 * s, KUNING, emissive=0.85, outline=True, outline_w=0.007 * s)
        sc.sphere(wp(-2.40, 0.52, lz), 0.10 * s, MERAH, emissive=0.65, outline=True, outline_w=0.007 * s)
    # Roda bus
    for lx in (-1.42, +1.42):
        for lz in (-0.86, +0.86):
            sc.cylinder(wp(lx, 0.28, lz), 0.28 * s, 0.16 * s, HITAM, seg_u=14, mat=m @ euler_mat(90, 0, 0), outline=True, outline_w=0.007 * s)
            sc.cylinder(wp(lx, 0.28, lz * 1.03), 0.14 * s, 0.15 * s, ABU, seg_u=12, mat=m @ euler_mat(90, 0, 0))


def _gedung_latar(sc, x, z, w, h, d, col=KRIM, waktu="siang"):
    sc.box((x, h * 0.5, z), (w, h, d), col, outline=True, outline_w=0.015)
    sc.box((x, h + 0.14, z), (w + 0.22, 0.28, d + 0.22), gelap(col, 0.22), outline=True, outline_w=0.012)
    win_col = KUNING if waktu == "malam" else BIRU_MUDA
    em = 0.75 if waktu == "malam" else 0.05
    cols_n = max(2, int(w // 1.1))
    rows_n = max(2, int(h // 1.45))
    for ix in range(cols_n):
        wx = x - (w * 0.34) + (ix / max(1, cols_n - 1)) * (w * 0.68)
        for iy in range(rows_n):
            wy = 1.2 + iy * ((h - 1.7) / max(1, rows_n - 1))
            sc.box((wx, wy, z + d * 0.5 + 0.03), (0.52, 0.66, 0.05), win_col, emissive=em, outline=True, outline_w=0.006)


def _jendela_dinding(sc, x, y, z, w=1.5, h=1.4, rot_y=0.0, waktu="siang"):
    sky_c = (38, 48, 86) if waktu == "malam" else (246, 182, 134) if waktu == "sore" else BIRU_MUDA
    sc.box((x, y, z), (w + 0.14, h + 0.14, 0.08), PUTIH, rot=(0, rot_y, 0), outline=True, outline_w=0.009)
    off = 0.05 if rot_y == 0 else 0.0
    off_x = 0.05 if rot_y == 90 else (-0.05 if rot_y == -90 else 0.0)
    sc.box((x + off_x, y, z + off), (w - 0.06, h - 0.06, 0.03), sky_c, rot=(0, rot_y, 0), emissive=0.35)
    sc.box((x + off_x * 1.3, y, z + off * 1.3), (0.06, h, 0.05), PUTIH, rot=(0, rot_y, 0))
    sc.box((x + off_x * 1.3, y, z + off * 1.3), (w, 0.06, 0.05), PUTIH, rot=(0, rot_y, 0))


def _ruang_dasar(sc, wall_col=(214, 206, 186), floor_col=(186, 140, 96), trim_col=COKLAT_TUA,
                 w=7.5, d_back=-4.8, d_front=6.5, h=5.8, checker=None, floor_bias=0.0):
    """Ruangan 3D skala luas (aman untuk kamera lebar, crane, & orbit)."""
    sc.tiled_plane(-w, d_back, w, d_front, 0.0, floor_col, tile=2.0, checker=checker, bias=floor_bias)
    sc.tiled_wall_z(-w, 0.0, w, h, d_back, wall_col, normal_z=1, tile=2.0, bias=0.6)
    sc.tiled_wall_x(d_back, 0.0, d_front, h, -w, gelap(wall_col, 0.08), normal_x=1, tile=2.0, bias=0.6)
    sc.tiled_wall_x(d_back, 0.0, d_front, h, +w, gelap(wall_col, 0.08), normal_x=-1, tile=2.0, bias=0.6)
    sc.box((0.0, 0.08, d_back + 0.04), (w * 2.0, 0.16, 0.06), trim_col, bias=0.2)
    sc.box((0.0, 1.15, d_back + 0.04), (w * 2.0, 0.10, 0.05), trim_col, bias=0.2)


# ================================================================== 1. KAMAR BELAJAR
def set_kamar_belajar(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    sc.add_light((0.0, 3.6, -1.6), color=(255, 224, 162), intensity=1.2, radius=8.5)
    _ruang_dasar(sc, wall_col=(204, 196, 174), floor_col=(188, 138, 92), w=7.2, d_back=-4.2, d_front=6.0, h=5.8)

    for i in range(13):
        lx = -3.6 + i * 0.6
        ly = 3.35 - math.sin((i / 12.0) * math.pi) * 0.28
        sc.sphere((lx, ly, -4.10), 0.06, KUNING, emissive=0.95)
    sc.limb((-3.8, 3.35, -4.12), (3.8, 3.35, -4.12), 0.012, HITAM, outline=False)

    _jendela_dinding(sc, -7.12, 2.35, -1.2, w=2.0, h=1.6, rot_y=90, waktu=w)
    _jendela_dinding(sc, 4.2, 2.35, -4.15, w=1.8, h=1.5, rot_y=0, waktu=w)

    BD.draw_kalender(sc, (-0.2, 2.35, -4.12), o.get("bulan", "JANUARI"), o.get("tahun", "2008"), o.get("sub_kalender", "SELAMAT PAGI"))
    BD.draw_poster(sc, (1.45, 2.15, -4.12), o.get("judul_poster", "TERBANG PERDANA"), "10 AGUSTUS", "1995", w=0.84, h=1.04)

    sc.box((-3.2, 1.45, -3.75), (1.35, 2.6, 0.50), KAYU_TUA, outline=True, outline_w=0.012)
    for sh in (0.68, 1.35, 2.02):
        sc.box((-3.2, sh, -3.70), (1.28, 0.05, 0.46), KAYU)
        for bi, bc in enumerate((MERAH, BIRU, HIJAU, KUNING, TEAL, ORANYE, UNGU)):
            sc.box((-3.68 + bi * 0.15, sh + 0.17, -3.68), (0.11, 0.30, 0.28), bc, outline=True, outline_w=0.005)

    sc.box((-5.2, 0.32, -2.1), (2.2, 0.44, 1.35), KAYU_TUA, outline=True, outline_w=0.012)
    sc.rbox((-5.2, 0.62, -2.1), (2.08, 0.24, 1.25), BIRU_MUDA, roundness=0.25, seg=2, outline=True, outline_w=0.01)
    sc.rbox((-5.9, 0.80, -2.1), (0.45, 0.18, 0.88), PUTIH, roundness=0.4, seg=2, outline=True, outline_w=0.008)

    BD.draw_desk(sc, (2.25, 0.0, -2.35), w=1.75, d=0.82)
    BD.draw_chair(sc, (2.25, 0.0, -1.65), rot_y=180)
    sc.cylinder((2.85, 0.80, -2.45), 0.11, 0.05, TEAL, outline=True)
    sc.limb((2.85, 0.82, -2.45), (2.74, 1.20, -2.38), 0.018, TEAL)
    sc.sphere((2.72, 1.22, -2.35), 0.11, KUNING, emissive=0.75, outline=True)
    _tanaman_pot(sc, (4.8, 0.0, -3.3), s=1.2)
    _tanaman_pot(sc, (-4.5, 0.0, -3.6), s=1.1)


# ================================================================== 2. RUANG KERJA / ISTANA
def set_ruang_kerja(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    sc.add_light((0.0, 3.8, -1.0), color=(255, 224, 168), intensity=1.25, radius=9.0)
    _ruang_dasar(sc, wall_col=(222, 212, 192), floor_col=(142, 92, 58), trim_col=(118, 76, 44), w=8.0, d_back=-4.8, d_front=6.5, h=5.8, floor_bias=4.0)
    sc.tiled_plane(-3.2, -3.2, 3.2, 2.8, 0.02, MERAH_TUA, tile=1.6, bias=0.0)

    for px in (-4.8, 4.8):
        sc.cylinder((px, 2.9, -4.55), 0.28, 5.8, KRIM, seg_u=14, outline=True, outline_w=0.012)
    _jendela_dinding(sc, -6.2, 2.6, -4.72, w=1.6, h=2.4, waktu=w)
    _jendela_dinding(sc, +6.2, 2.6, -4.72, w=1.6, h=2.4, waktu=w)

    BD.draw_peta(sc, (-0.35, 2.55, -4.72), "INDONESIA", w=2.2, h=1.22)
    BD.draw_kalender(sc, (2.05, 2.45, -4.72), o.get("bulan", "MEI"), o.get("tahun", "1998"), "", w=0.68, h=0.84)

    BD.draw_flag_id(sc, (3.45, 0.0, -3.65), h=2.65)
    sc.box((-3.55, 1.35, -4.25), (1.5, 2.7, 0.55), COKLAT_TUA, outline=True, outline_w=0.012)

    BD.draw_desk(sc, (0.0, 0.0, -2.05), w=2.35, d=0.98, h=0.80, top_col=COKLAT, leg_col=COKLAT_TUA)
    BD.draw_chair(sc, (0.0, 0.0, -2.85), col=(68, 42, 34))
    sc.box((-0.72, 0.86, -1.98), (0.38, 0.06, 0.26), PUTIH, outline=True, outline_w=0.006)
    BD.draw_mug(sc, (0.76, 0.83, -1.95), col=PUTIH)
    _tanaman_pot(sc, (-5.6, 0.0, -3.6), s=1.35)
    _tanaman_pot(sc, (5.6, 0.0, -3.6), s=1.35)


# ================================================================== 3. WARUNG / PASAR
def set_warung(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    _langit_awan(sc, t)
    sc.add_light((0.0, 3.2, 0.2), color=(255, 232, 186), intensity=1.2, radius=8.5)
    sc.tiled_plane(-12.0, -7.0, 12.0, 9.0, 0.0, (208, 212, 216), tile=2.2, checker=(194, 198, 204), bias=4.0)
    sc.tiled_plane(-12.0, 3.2, 12.0, 9.0, 0.02, (90, 94, 102), tile=2.5, bias=0.0)
    sc.tiled_wall_z(-7.5, 0.0, 7.5, 5.4, -3.8, (34, 72, 118), normal_z=1, tile=2.2, bias=0.6)

    sc.box((0.0, 0.45, -1.85), (5.8, 0.90, 0.90), (46, 102, 168), outline=True, outline_w=0.012)
    sc.box((0.0, 0.93, -1.85), (6.0, 0.08, 1.02), COKLAT, outline=True, outline_w=0.01)

    for i in range(15):
        col = (46, 92, 152) if i % 2 == 0 else KRIM
        sc.box((-4.2 + i * 0.6, 3.15, -1.05), (0.60, 0.14, 3.4), col, rot=(14, 0, 0))

    sachet_cols = [MERAH, KUNING, BIRU, HIJAU, PINK, ORANYE]
    for sx in (-2.4, -1.1, 0.65, 2.25):
        sc.limb((sx, 2.90, -0.75), (sx, 1.80, -0.75), 0.01, HITAM, outline=False)
        for k, sc_c in enumerate(sachet_cols):
            sc.box((sx, 2.72 - k * 0.17, -0.75), (0.14, 0.13, 0.04), sc_c, outline=True, outline_w=0.006)

    BD.draw_kalender(sc, (-1.45, 2.28, -3.72), o.get("bulan", "MEI 1998"), o.get("tahun", "1"), "MINGGU 1", w=0.70, h=0.86)
    sc.textured_quad(BD._wall_quad(0.15, 1.48, -1.82, 0.82, 0.46),
                     BD._tex_papan("HARGA", o.get("harga", "Rp12.000"), "NAIK!", bg=PUTIH, fg=MERAH, border=MERAH))

    BD.draw_karung(sc, (1.45, 0.0, -0.55), "BERAS", s=1.0)
    BD.draw_karung(sc, (2.15, 0.0, -0.45), "BERAS", s=0.95)
    BD.draw_karung(sc, (-2.35, 0.0, -0.50), "GULA", s=0.95)
    for jx in (0.65, 1.05, 1.45, 1.85):
        sc.cylinder((jx, 1.07, -1.62), 0.08, 0.18, HIJAU, outline=True, outline_w=0.007)
    _pohon_3d(sc, -5.8, 0.0, -1.2, s=1.15)
    _pohon_3d(sc, +5.8, 0.0, -1.4, s=1.10)
    _lampu_jalan(sc, 4.6, 0.0, 2.6, arah=-1, waktu=w)


# ================================================================== 4. HANGGAR PESAWAT / PABRIK
def set_hanggar(sc, t, o):
    configure_sky(sc, o)
    sc.add_light((0.0, 4.6, 0.0), color=(238, 246, 255), intensity=1.35, radius=12.0)
    sc.tiled_plane(-12.0, -10.0, 12.0, 9.0, 0.0, (148, 154, 162), tile=2.5)
    sc.tiled_wall_z(-12.0, 0.0, 12.0, 6.8, -6.5, (162, 168, 174), normal_z=1, tile=2.5, bias=0.6)
    sc.tiled_wall_x(-6.5, 0.0, 9.0, 6.8, -11.5, (148, 154, 162), normal_x=1, tile=2.5, bias=0.6)
    sc.tiled_wall_x(-6.5, 0.0, 9.0, 6.8, +11.5, (148, 154, 162), normal_x=-1, tile=2.5, bias=0.6)

    for rx in (-6.0, -2.0, 2.0, 6.0):
        sc.box((rx, 3.4, -6.35), (0.32, 6.8, 0.32), ABU_TUA, outline=True, outline_w=0.01)

    for i in range(-8, 9):
        sc.box((i * 1.1, 0.015, -1.2), (0.55, 0.02, 0.18), KUNING if i % 2 == 0 else HITAM)

    BD.draw_poster(sc, (2.2, 2.45, -6.38), "TERBANG PERDANA", "10 AGUSTUS", "1995", w=1.15, h=1.42)
    sc.textured_quad(BD._wall_quad(-1.6, 3.65, -6.38, 3.2, 0.68),
                     _banner_tex(o.get("banner", "HANGGAR N250 - BANDUNG"), bg=NAVY, fg=PUTIH))

    sc.box((3.2, 0.60, -4.0), (1.85, 1.20, 0.85), HIJAU_TUA, outline=True, outline_w=0.012)
    BD.draw_airplane_mini(sc, (3.2, 1.48, -3.95), s=1.45, rot_y=-25)
    BD.draw_airplane_mini(sc, (-4.8, 1.25, -4.4), s=2.2, rot_y=28)
    BD.draw_desk(sc, (-2.15, 0.0, -2.45), w=1.95, d=0.85, top_col=ABU, leg_col=KUNING)


# ================================================================== 5. GEDUNG SIDANG / PODIUM
def set_gedung_sidang(sc, t, o):
    configure_sky(sc, o)
    sc.add_light((0.0, 4.4, 0.2), color=(255, 228, 184), intensity=1.25, radius=11.0)
    sc.tiled_plane(-10.0, -8.5, 10.0, 8.0, 0.0, (152, 44, 52), tile=2.4)
    sc.tiled_wall_z(-10.0, 0.0, 10.0, 6.4, -5.8, (148, 112, 78), normal_z=1, tile=2.4, bias=0.6)
    sc.tiled_wall_x(-5.8, 0.0, 8.0, 6.4, -9.8, (132, 98, 66), normal_x=1, tile=2.4, bias=0.6)
    sc.tiled_wall_x(-5.8, 0.0, 8.0, 6.4, +9.8, (132, 98, 66), normal_x=-1, tile=2.4, bias=0.6)

    for tx in (-6.2, -5.7, -5.2, 5.2, 5.7, 6.2):
        sc.cylinder((tx, 3.1, -5.55), 0.24, 6.2, (158, 34, 42))

    sc.box((0.0, 0.16, -2.55), (7.6, 0.32, 2.8), COKLAT_TUA, outline=True, outline_w=0.012)
    BD.draw_podium(sc, (-0.95, 0.32, -1.85), s=1.05)
    BD.draw_flag_id(sc, (2.65, 0.32, -2.85), h=2.55)
    BD.draw_flag_id(sc, (-2.85, 0.32, -2.85), h=2.55)

    BD.draw_layar_led(sc, (-1.6, 3.05, -5.68), "HASIL PEMUNGUTAN SUARA",
                      o.get("kiri_lbl", "MENOLAK"), o.get("kiri_val", "355"),
                      o.get("kanan_lbl", "MENERIMA"), o.get("kanan_val", "322"), w=2.8, h=1.35)
    BD.draw_kalender(sc, (1.85, 2.45, -5.68), "SIDANG UMUM", o.get("tahun", "1998"), "", w=0.82, h=1.02)

    for sx in (-4.8, 4.8):
        BD.draw_desk(sc, (sx, 0.0, 0.6), w=2.2, d=0.72, h=0.74, top_col=COKLAT, leg_col=COKLAT_TUA)

    sc.box((1.35, 1.15, 1.05), (0.36, 0.22, 0.50), HITAM, rot=(0, -24, 0), outline=True, outline_w=0.009)
    for lx in (-0.20, 0.0, 0.20):
        sc.limb((1.35, 1.04, 1.05), (1.35 + lx, 0.0, 1.05 + abs(lx) * 0.6), 0.018, ABU_TUA, outline=False)


# ================================================================== 6. KAMPUS / JALAN SEKOLAH
def set_kampus(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    _langit_awan(sc, t)
    _bukit_horizon(sc, y=0.0, z=-22.0)

    sc.tiled_plane(-20.0, -20.0, 20.0, 12.0, -0.02, (108, 168, 92), tile=4.0, bias=5.0)
    sc.tiled_plane(-4.2, -14.0, 4.2, 12.0, 0.0, (82, 86, 94), tile=2.5, bias=1.5)
    sc.tiled_plane(-8.5, -14.0, -4.2, 12.0, 0.05, (192, 194, 198), tile=2.5, bias=0.0)
    sc.tiled_plane(+4.2, -14.0, +8.5, 12.0, 0.05, (192, 194, 198), tile=2.5, bias=0.0)

    for zx in (-2.4, -1.4, -0.4, 0.6, 1.6, 2.6):
        sc.box((zx, 0.01, 1.4), (0.55, 0.015, 1.15), PUTIH)

    sc.box((-3.8, 1.85, -4.8), (0.62, 3.7, 0.62), KRIM, outline=True)
    sc.box((+3.8, 1.85, -4.8), (0.62, 3.7, 0.62), KRIM, outline=True)
    sc.box((0.0, 3.75, -4.8), (8.6, 0.55, 0.68), MERAH_TUA, outline=True)
    sc.textured_quad(BD._wall_quad(0.0, 3.82, -4.44, 5.2, 0.72),
                     _banner_tex(o.get("banner", "SELAMAT DATANG MAHASISWA"), bg=PUTIH, fg=HITAM))

    _gedung_latar(sc, 0.0, -11.5, 10.5, 5.6, 3.2, KRIM, waktu=w)
    _gedung_latar(sc, -10.5, -10.5, 6.2, 4.4, 2.8, (226, 214, 196), waktu=w)
    _gedung_latar(sc, +10.5, -10.5, 6.2, 4.8, 2.8, (212, 222, 232), waktu=w)

    sc.box((-4.8, 0.72, -1.5), (1.05, 0.85, 0.65), HIJAU, outline=True)
    sc.box((-4.8, 1.80, -1.5), (1.18, 0.10, 0.78), KUNING, outline=True)
    sc.textured_quad(BD._wall_quad(-4.8, 0.78, -1.16, 0.68, 0.26), _banner_tex("BAKSO", bg=PUTIH, fg=MERAH, border=MERAH))
    sc.box((-5.2, 0.45, 1.4), (1.35, 0.08, 0.52), KAYU, outline=True)
    for px, pz, ps in ((5.4, -2.5, 1.25), (6.4, 2.2, 1.15), (-6.4, -3.2, 1.3), (-7.2, 2.8, 1.1)):
        _pohon_3d(sc, px, 0.05, pz, s=ps)
    _lampu_jalan(sc, 4.6, 0.05, -0.5, arah=-1, waktu=w)
    _lampu_jalan(sc, -4.6, 0.05, 3.2, arah=+1, waktu=w)


# ================================================================== 7. KELAS
def set_kelas(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    sc.add_light((0.0, 3.8, 0.0), color=(255, 240, 206), intensity=1.2, radius=9.5)
    _ruang_dasar(sc, wall_col=(234, 224, 198), floor_col=(188, 152, 108), trim_col=KAYU_TUA, w=7.5, d_back=-4.5, d_front=6.5, h=5.8)

    BD.draw_papan_tulis(sc, (0.0, 2.15, -4.42), o.get("judul", "RUMUS PENTING"),
                        o.get("baris1", "F = m · a"), o.get("baris2", "L = 1/2 · ρ · v²"), w=3.2, h=1.55)
    sc.cylinder((2.65, 2.95, -4.42), 0.28, 0.06, PUTIH, rot=(90, 0, 0), outline=True)
    _jendela_dinding(sc, -7.42, 2.35, -1.8, w=2.2, h=1.6, rot_y=90, waktu=w)
    _jendela_dinding(sc, -7.42, 2.35, +1.6, w=2.2, h=1.6, rot_y=90, waktu=w)

    BD.draw_desk(sc, (3.4, 0.0, -3.1), w=1.45, d=0.72, h=0.76, top_col=COKLAT, leg_col=COKLAT_TUA)
    for mz in (0.6, 2.5):
        for mx in (-3.2, -1.1, 1.1, 3.2):
            BD.draw_desk(sc, (mx, 0.0, mz), w=1.05, d=0.60, h=0.68)
            BD.draw_chair(sc, (mx, 0.0, mz + 0.52), rot_y=180)
    _tanaman_pot(sc, (-5.8, 0.0, -3.8), s=1.2)


# ================================================================== 8. BANK / LOKET KAS
def set_bank_kas(sc, t, o):
    configure_sky(sc, o)
    sc.add_light((0.0, 3.8, 0.2), color=(255, 236, 196), intensity=1.25, radius=9.0)
    _ruang_dasar(sc, wall_col=(214, 218, 224), floor_col=(188, 192, 198), trim_col=NAVY,
                 w=8.0, d_back=-4.8, d_front=6.5, h=5.8, checker=(176, 180, 188))

    BD.draw_layar_led(sc, (0.0, 2.65, -4.70), o.get("judul", "PENUKARAN UANG"),
                      o.get("kiri_lbl", "KURS USD"), o.get("kiri_val", "RP2.500"), w=2.6, h=1.18)
    sc.box((0.0, 0.55, -2.05), (6.4, 1.10, 0.80), TEAL_TUA, outline=True)
    sc.box((0.0, 1.14, -2.05), (6.6, 0.08, 0.92), KRIM, outline=True)
    sc.cylinder((-4.6, 1.55, -4.62), 1.05, 0.28, ABU_TUA, rot=(90, 0, 0), outline=True)
    sc.cylinder((-4.6, 1.55, -4.44), 0.65, 0.16, ABU, rot=(90, 0, 0), outline=True)
    for cz in (-0.2, 1.2):
        BD.draw_chair(sc, (5.2, 0.0, cz), col=NAVY, rot_y=-90)
    _tanaman_pot(sc, (4.8, 0.0, -3.8), s=1.3)


# ================================================================== 9. JALAN KOTA
def set_jalan_kota(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    _langit_awan(sc, t)
    _bukit_horizon(sc, y=0.0, z=-24.0, col=(94, 128, 118))

    sc.tiled_plane(-20.0, -22.0, 20.0, 14.0, 0.0, (76, 80, 90), tile=3.0, bias=4.0)
    sc.tiled_plane(-20.0, -22.0, -4.2, 14.0, 0.07, (186, 190, 196), tile=3.0, bias=0.0)
    sc.tiled_plane(+4.2, -22.0, +20.0, 14.0, 0.07, (186, 190, 196), tile=3.0, bias=0.0)
    for mz in range(-18, 12, 3):
        sc.box((0.0, 0.012, float(mz)), (0.22, 0.015, 1.35), KUNING)

    for bx, bz, bw, bh, bd, col in (
        (-7.6, -12.0, 4.2, 7.6, 4.0, KRIM),
        (-7.4, -5.5,  3.8, 5.8, 3.6, (198, 212, 224)),
        (-7.6, +1.5,  3.8, 4.8, 3.4, (226, 210, 192)),
        (+7.6, -12.5, 4.4, 8.2, 4.0, (214, 196, 178)),
        (+7.4, -5.2,  3.8, 6.2, 3.6, KRIM),
        (+7.6, +1.8,  3.8, 5.0, 3.4, (194, 208, 220)),
        (-3.2, -18.5, 4.5, 9.5, 3.8, (182, 194, 212)),
        (+3.4, -19.0, 4.8, 8.6, 3.8, (206, 202, 196)),
    ):
        _gedung_latar(sc, bx, bz, bw, bh, bd, col, waktu=w)

    for px, pz in ((-5.0, -1.8), (-5.0, 4.2), (5.0, -2.6), (5.0, 3.6)):
        _pohon_3d(sc, px, 0.07, pz, s=1.15)
    for lz in (-8.0, -1.0, 5.5):
        _lampu_jalan(sc, -4.5, 0.07, lz, arah=+1, waktu=w)
        _lampu_jalan(sc, +4.5, 0.07, lz, arah=-1, waktu=w)
    _mobil_3d(sc, -2.0, 0.0, -6.5, col=MERAH, rot_y=90, s=1.05)
    _mobil_3d(sc, +2.1, 0.0, -11.5, col=BIRU, rot_y=-90, s=1.05)


# ================================================================== 10. POLOS / PANGGUNG EXPLAINER
def set_polos(sc, t, o):
    configure_sky(sc, o)
    sc.set_sky((238, 244, 250), (218, 228, 240), (0.62, 0.64, 0.68), (0.36, 0.36, 0.38),
               [0.45, 0.85, 0.45], [1.0, 0.98, 0.95], 0.72, (226, 234, 244), fog_start=22.0, fog_density=0.015)
    sc.tiled_plane(-18.0, -18.0, 18.0, 18.0, 0.0, (228, 234, 242), tile=3.0)


# ================================================================== 11. TAMAN KOTA
def set_taman_kota(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    _langit_awan(sc, t)
    _bukit_horizon(sc, y=0.0, z=-22.0, col=(92, 162, 96))

    sc.tiled_plane(-20.0, -20.0, 20.0, 14.0, 0.0, (106, 174, 94), tile=3.5, bias=4.5)
    sc.tiled_plane(-2.4, -18.0, 2.4, 14.0, 0.02, (206, 198, 182), tile=2.4, bias=0.0)

    sc.cylinder((0.0, 0.24, -7.2), 2.1, 0.48, ABU, seg_u=20, outline=True, outline_w=0.012)
    sc.cylinder((0.0, 0.42, -7.2), 1.82, 0.14, BIRU_MUDA, seg_u=20, emissive=0.15)
    sc.cylinder((0.0, 0.95, -7.2), 0.24, 1.1, ABU, seg_u=14, outline=True)

    for bx, bz, rot in ((-3.4, -1.8, 20), (3.4, -2.2, -20), (-3.8, 2.8, 15)):
        sc.box((bx, 0.44, bz), (1.45, 0.09, 0.52), KAYU, rot=(0, rot, 0), outline=True)
        sc.box((bx, 0.78, bz - 0.22), (1.45, 0.36, 0.08), KAYU_TUA, rot=(0, rot, 0), outline=True)
    for px, pz, ps in ((-6.2, -4.5, 1.45), (-7.5, 1.2, 1.3), (6.0, -4.0, 1.4), (7.2, 1.8, 1.25), (-4.2, -10.5, 1.6), (4.5, -10.8, 1.55)):
        _pohon_3d(sc, px, 0.0, pz, s=ps)
    _lampu_jalan(sc, -2.8, 0.0, -4.5, arah=+1, waktu=w)
    _lampu_jalan(sc, +2.8, 0.0, +1.5, arah=-1, waktu=w)


# ================================================================== 12. KAFE / KEDAI KOPI
def set_kafe(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    sc.add_light((0.0, 3.6, -0.8), color=(255, 214, 152), intensity=1.25, radius=9.5)
    _ruang_dasar(sc, wall_col=(188, 128, 92), floor_col=(156, 114, 78), trim_col=COKLAT_TUA, w=8.0, d_back=-4.8, d_front=6.5, h=5.8)

    sc.box((0.0, 0.52, -2.8), (5.4, 1.04, 0.85), COKLAT_TUA, outline=True, outline_w=0.012)
    sc.box((0.0, 1.08, -2.8), (5.6, 0.09, 0.98), KAYU, outline=True, outline_w=0.01)
    BD.draw_papan_tulis(sc, (0.0, 2.65, -4.72), o.get("judul", "MENU KOPI"),
                        o.get("baris1", "KOPI SUSU · 18K"), o.get("baris2", "AMERICANO · 15K"), w=2.8, h=1.35)
    _jendela_dinding(sc, -7.92, 2.35, -1.2, w=2.4, h=1.8, rot_y=90, waktu=w)

    for mx, mz in ((-3.8, -0.4), (3.8, -0.4), (-3.8, 2.2), (3.8, 2.2)):
        sc.cylinder((mx, 0.36, mz), 0.06, 0.72, HITAM, outline=True)
        sc.cylinder((mx, 0.74, mz), 0.55, 0.06, KAYU, seg_u=16, outline=True)
        BD.draw_mug(sc, (mx + 0.14, 0.77, mz), col=PUTIH)
    _tanaman_pot(sc, (-5.8, 0.0, -3.8), s=1.3)
    _tanaman_pot(sc, (+5.8, 0.0, -3.8), s=1.3)


# ================================================================== 13. STUDIO BERITA / PODCAST
def set_studio_berita(sc, t, o):
    configure_sky(sc, o)
    sc.add_light((0.0, 4.0, 0.5), color=(226, 240, 255), intensity=1.35, radius=10.0)
    _ruang_dasar(sc, wall_col=(36, 46, 76), floor_col=(48, 56, 74), trim_col=BIRU,
                 w=8.5, d_back=-5.0, d_front=6.5, h=5.8, checker=(42, 50, 68))

    BD.draw_layar_led(sc, (0.0, 2.55, -4.88), o.get("judul", "BREAKING NEWS"),
                      o.get("kiri_lbl", "TOPIK UTAMA"), o.get("kiri_val", "LIVE"), w=4.6, h=2.1)
    for sx in (-4.2, 4.2):
        sc.box((sx, 2.4, -4.92), (0.14, 4.2, 0.06), BIRU_MUDA, emissive=0.9)
    sc.box((0.0, 0.44, -1.65), (3.2, 0.88, 0.82), NAVY, outline=True, outline_w=0.012)
    sc.box((0.0, 0.90, -1.65), (3.35, 0.08, 0.92), PUTIH, outline=True, outline_w=0.01)


# ================================================================== 14. RUMAH SAKIT / KLINIK
def set_rumah_sakit(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    sc.add_light((0.0, 3.9, 0.0), color=(244, 250, 255), intensity=1.3, radius=10.0)
    _ruang_dasar(sc, wall_col=(236, 244, 248), floor_col=(208, 222, 228), trim_col=TEAL, w=7.8, d_back=-4.8, d_front=6.5, h=5.8)

    sc.box((0.0, 2.95, -4.74), (1.10, 1.10, 0.04), PUTIH, outline=True, outline_w=0.008)
    sc.box((0.0, 2.95, -4.71), (0.85, 0.24, 0.05), MERAH, outline=False, bias=-0.04)
    sc.box((0.0, 2.95, -4.70), (0.24, 0.85, 0.05), MERAH, outline=False, bias=-0.06)
    _jendela_dinding(sc, 3.8, 2.45, -4.72, w=2.0, h=1.6, waktu=w)

    sc.box((-3.8, 0.42, -2.4), (2.2, 0.48, 1.1), PUTIH, outline=True, outline_w=0.012)
    sc.rbox((-3.8, 0.72, -2.4), (2.05, 0.20, 1.0), BIRU_MUDA, roundness=0.25, seg=2, outline=True)
    BD.draw_desk(sc, (3.2, 0.0, -2.2), w=1.65, d=0.78, h=0.76, top_col=PUTIH, leg_col=TEAL)
    BD.draw_chair(sc, (3.2, 0.0, -1.5), col=TEAL, rot_y=180)
    _tanaman_pot(sc, (-5.8, 0.0, -3.8), s=1.2)


# ================================================================== 15. KANTOR STARTUP
def set_kantor_startup(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    sc.add_light((0.0, 3.8, -0.5), color=(238, 246, 255), intensity=1.25, radius=10.0)
    _ruang_dasar(sc, wall_col=(236, 240, 246), floor_col=(182, 162, 138), trim_col=ABU_TUA, w=8.5, d_back=-5.0, d_front=6.5, h=5.8)

    _jendela_dinding(sc, -3.6, 2.5, -4.92, w=3.2, h=2.2, waktu=w)
    BD.draw_papan_tulis(sc, (2.2, 2.35, -4.92), o.get("judul", "SPRINT BOARD"),
                        o.get("baris1", "TODO · DOING · DONE"), o.get("baris2", "TARGET Q4"), w=2.8, h=1.45)

    for mx in (-3.6, 3.6):
        BD.draw_desk(sc, (mx, 0.0, -2.1), w=2.1, d=0.85, h=0.76, top_col=PUTIH, leg_col=HITAM)
        BD.draw_chair(sc, (mx, 0.0, -1.35), col=BIRU, rot_y=180)
        for dx in (-0.42, 0.42):
            sc.box((mx + dx, 1.04, -2.28), (0.68, 0.42, 0.04), HITAM, outline=True, outline_w=0.007)
            sc.box((mx + dx, 1.04, -2.25), (0.60, 0.34, 0.02), BIRU_MUDA, emissive=0.45)
            sc.cylinder((mx + dx, 0.82, -2.28), 0.04, 0.12, ABU_TUA)
    _tanaman_pot(sc, (-6.4, 0.0, -3.9), s=1.35)
    _tanaman_pot(sc, (+6.4, 0.0, -3.9), s=1.35)


# ================================================================== 16. LABORATORIUM
def set_laboratorium(sc, t, o):
    configure_sky(sc, o)
    sc.add_light((0.0, 4.0, 0.0), color=(232, 248, 255), intensity=1.35, radius=10.5)
    _ruang_dasar(sc, wall_col=(228, 238, 244), floor_col=(198, 208, 216), trim_col=TEAL_TUA,
                 w=8.2, d_back=-5.0, d_front=6.5, h=5.8, checker=(188, 198, 206))

    BD.draw_layar_led(sc, (0.0, 2.55, -4.90), o.get("judul", "DATA EKSPERIMEN"),
                      o.get("kiri_lbl", "SUHU"), o.get("kiri_val", "24°C"),
                      o.get("kanan_lbl", "STATUS"), o.get("kanan_val", "AMAN"), w=3.2, h=1.35)

    for mx in (-3.6, 3.6):
        sc.box((mx, 0.45, -2.4), (2.4, 0.90, 0.95), PUTIH, outline=True, outline_w=0.012)
        sc.box((mx, 0.94, -2.4), (2.5, 0.08, 1.05), (42, 48, 56), outline=True, outline_w=0.01)
        for ti, tc in enumerate((HIJAU, BIRU_MUDA, ORANYE, UNGU)):
            tx = mx - 0.65 + ti * 0.42
            sc.cylinder((tx, 1.14, -2.35), 0.07, 0.30, tc, seg_u=12, emissive=0.35, outline=True, outline_w=0.006)
    sc.box((-6.2, 1.45, -4.3), (1.4, 2.9, 0.65), ABU, outline=True, outline_w=0.012)


# ================================================================== 17. STASIUN KERETA
def set_stasiun(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    _langit_awan(sc, t)
    sc.add_light((0.0, 4.2, 0.0), color=(248, 244, 230), intensity=1.2, radius=11.0)

    sc.tiled_plane(-18.0, -3.5, 18.0, 12.0, 0.0, (186, 190, 196), tile=3.0)
    sc.tiled_plane(-18.0, -14.0, 18.0, -3.5, -0.55, (72, 68, 66), tile=3.0)
    sc.box((0.0, 0.02, -3.15), (32.0, 0.03, 0.32), KUNING)

    for rz in (-5.0, -6.4):
        sc.box((0.0, -0.48, rz), (32.0, 0.08, 0.10), ABU_TUA)

    for kx in (-6.5, 0.5, 7.5):
        sc.rbox((kx, 1.15, -5.7), (6.4, 2.35, 2.1), PUTIH, roundness=0.18, seg=2, outline=True, outline_w=0.014)
        sc.box((kx, 0.55, -4.60), (6.20, 0.34, 0.05), BIRU, bias=-0.25)
        for wx in (-2.1, -0.7, 0.7, 2.1):
            sc.box((kx + wx, 1.42, -4.60), (0.95, 0.72, 0.05), BIRU_MUDA, outline=True, outline_w=0.006, bias=-0.25)

    for px in (-6.5, 0.0, 6.5):
        sc.cylinder((px, 2.4, -1.6), 0.16, 4.8, ABU_TUA, outline=True)
    sc.box((0.0, 4.85, -1.4), (18.0, 0.24, 5.2), NAVY, outline=True)
    BD.draw_layar_led(sc, (0.0, 3.35, -1.2), o.get("judul", "JADWAL KERETA"),
                      o.get("kiri_lbl", "JALUR 1"), o.get("kiri_val", "08:15"),
                      o.get("kanan_lbl", "TUJUAN"), o.get("kanan_val", "KOTA"), w=3.0, h=1.05)
    _lampu_jalan(sc, -5.2, 0.0, 2.8, arah=+1, waktu=w)


# ================================================================== 18. PANTAI
def set_pantai(sc, t, o):
    configure_sky(sc, o)
    _langit_awan(sc, t)

    sc.tiled_plane(-22.0, -6.5, 22.0, 14.0, 0.0, (242, 218, 166), tile=3.5)
    sc.tiled_plane(-24.0, -24.0, 24.0, -6.5, -0.05, (46, 148, 214), tile=4.0)
    sc.box((0.0, 0.01, -6.4), (40.0, 0.02, 0.55), PUTIH, emissive=0.25)

    for ux, uz, col in ((-4.2, -2.2, MERAH), (4.6, -2.8, BIRU)):
        sc.cylinder((ux, 1.35, uz), 0.05, 2.7, PUTIH, outline=True)
        sc.sphere((ux, 2.55, uz), (1.35, 0.48, 1.35), col, seg_u=14, seg_v=7, hemi=True, outline=True, outline_w=0.012)
        sc.box((ux + 0.5, 0.22, uz + 0.4), (0.85, 0.10, 1.65), PUTIH, rot=(0, 18, 0), outline=True)

    for px, pz, tilt in ((-7.2, -4.5, 10), (-9.0, -1.0, 14), (7.5, -4.2, -12), (9.2, -0.8, -8)):
        sc.cylinder((px, 1.9, pz), 0.16, 3.8, COKLAT, rot=(0, 0, tilt), outline=True)
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            sc.rbox((px + math.cos(rad) * 0.9, 3.7, pz + math.sin(rad) * 0.9),
                    (1.4, 0.14, 0.42), HIJAU, roundness=0.4, seg=2, rot=(0, -ang, 18), outline=True, outline_w=0.008)


# ================================================================== 19. PERPUSTAKAAN
def set_perpustakaan(sc, t, o):
    configure_sky(sc, o)
    sc.add_light((0.0, 3.8, -0.5), color=(255, 226, 174), intensity=1.2, radius=10.0)
    _ruang_dasar(sc, wall_col=(214, 202, 180), floor_col=(148, 104, 68), trim_col=COKLAT_TUA, w=8.5, d_back=-5.2, d_front=6.5, h=5.8)

    book_cols = (MERAH, BIRU, HIJAU, KUNING, UNGU, TEAL, ORANYE)
    for rx in (-5.2, -2.6, 0.0, 2.6, 5.2):
        sc.box((rx, 1.85, -4.85), (2.1, 3.7, 0.52), COKLAT_TUA, outline=True, outline_w=0.012)
        for sh in (0.7, 1.45, 2.2, 2.95):
            sc.box((rx, sh, -4.80), (2.0, 0.05, 0.48), KAYU)
            for bi in range(7):
                sc.box((rx - 0.78 + bi * 0.26, sh + 0.22, -4.78), (0.18, 0.38, 0.32), book_cols[(bi + int(abs(rx))) % len(book_cols)], outline=True, outline_w=0.005)

    for mx in (-3.8, 3.8):
        BD.draw_desk(sc, (mx, 0.0, -1.2), w=2.2, d=0.95, h=0.76, top_col=KAYU, leg_col=COKLAT_TUA)
        BD.draw_chair(sc, (mx - 0.5, 0.0, -0.45), rot_y=180)
        BD.draw_chair(sc, (mx + 0.5, 0.0, -0.45), rot_y=180)
        sc.cylinder((mx, 0.86, -1.2), 0.05, 0.20, KUNING, outline=True)
        sc.sphere((mx, 1.02, -1.2), (0.18, 0.10, 0.12), HIJAU_TUA, emissive=0.45, outline=True)


# ================================================================== 20. PENGADILAN
def set_pengadilan(sc, t, o):
    configure_sky(sc, o)
    sc.add_light((0.0, 4.0, 0.0), color=(255, 230, 188), intensity=1.25, radius=10.0)
    _ruang_dasar(sc, wall_col=(156, 114, 78), floor_col=(132, 92, 60), trim_col=COKLAT_TUA, w=8.5, d_back=-5.2, d_front=6.5, h=5.8)

    sc.box((0.0, 2.4, -5.12), (4.6, 3.6, 0.08), COKLAT_TUA, outline=True, outline_w=0.012)
    sc.sphere((0.0, 3.2, -5.04), (0.45, 0.52, 0.08), KUNING, outline=True, outline_w=0.01)

    sc.box((0.0, 0.18, -3.2), (4.8, 0.36, 1.8), COKLAT_TUA, outline=True, outline_w=0.012)
    sc.box((0.0, 0.85, -2.55), (3.6, 1.05, 0.72), COKLAT, outline=True, outline_w=0.012)
    sc.box((0.0, 1.40, -2.55), (3.8, 0.08, 0.84), KAYU, outline=True, outline_w=0.01)

    BD.draw_flag_id(sc, (3.2, 0.0, -3.8), h=2.55)
    BD.draw_desk(sc, (-3.4, 0.0, -0.4), w=1.8, d=0.82, h=0.76, top_col=COKLAT, leg_col=COKLAT_TUA)
    BD.draw_desk(sc, (+3.4, 0.0, -0.4), w=1.8, d=0.82, h=0.76, top_col=COKLAT, leg_col=COKLAT_TUA)
    sc.box((0.0, 0.55, 2.2), (10.0, 0.10, 0.12), COKLAT_TUA, outline=True)
    for px in (-4.5, -1.5, 1.5, 4.5):
        sc.box((px, 0.28, 2.2), (0.12, 0.56, 0.12), COKLAT_TUA)


# ================================================================== 21. HALTE BUS KOTA
def set_halte_bus(sc, t, o):
    configure_sky(sc, o)
    w = o.get("waktu", "siang")
    _langit_awan(sc, t)
    _bukit_horizon(sc, y=0.0, z=-25.0, col=(94, 134, 118))

    # Trotoar utama (y=0.0 agar tokoh berdiri & duduk akurat) + jalan aspal di belakang (z < -2.2)
    sc.tiled_plane(-20.0, -2.2, 20.0, 14.0, 0.0, (190, 194, 200), tile=2.6, bias=0.0)
    sc.tiled_plane(-20.0, -14.0, 20.0, -2.2, -0.10, (74, 78, 88), tile=3.0, bias=3.5)
    sc.box((0.0, -0.04, -2.18), (40.0, 0.10, 0.16), (160, 164, 172), outline=True, outline_w=0.008)
    for mx in range(-16, 18, 4):
        sc.box((float(mx), -0.085, -6.2), (1.75, 0.02, 0.22), KUNING)
    for zx in range(-4, 5):
        sc.box((5.2, -0.085, -3.2 - zx * 0.85), (1.35, 0.02, 0.42), PUTIH)

    # Gedung kota latar & pepohonan & lampu jalan
    for bx, bz, bw, bh, bd, col in (
        (-9.5, -13.5, 4.4, 7.6, 3.8, KRIM),
        (-4.0, -14.2, 4.6, 9.0, 3.8, (198, 212, 224)),
        (+2.2, -13.8, 4.4, 7.2, 3.8, (226, 210, 192)),
        (+8.4, -13.4, 4.6, 8.4, 3.8, (194, 208, 220)),
    ):
        _gedung_latar(sc, bx, bz, bw, bh, bd, col, waktu=w)
    for px, pz, ps in ((-5.8, -0.8, 1.25), (6.6, -1.0, 1.20), (-8.5, 3.2, 1.15), (8.2, 3.4, 1.15)):
        _pohon_3d(sc, px, 0.0, pz, s=ps)
    _lampu_jalan(sc, -3.9, 0.0, -1.85, arah=+1, waktu=w)
    _lampu_jalan(sc, +4.2, 0.0, -1.85, arah=-1, waktu=w)

    # Shelter Halte Bus terbuka (di belakang tokoh, agar bus di jalan tetap terlihat)
    sc.box((-0.6, 0.015, -1.35), (4.2, 0.03, 1.65), (168, 174, 182), outline=True, outline_w=0.008)
    for px in (-2.45, -0.60, +1.25):
        sc.cylinder((px, 1.25, -1.96), 0.065, 2.50, NAVY, outline=True, outline_w=0.009)
    # Rangka sandaran halte terbuka (rel atas & tengah agar bus di jalan tetap terlihat jelas)
    sc.box((-0.6, 0.62, -1.96), (3.70, 0.08, 0.06), TEAL_TUA, outline=True)
    sc.box((-0.6, 1.84, -1.96), (3.70, 0.08, 0.06), TEAL_TUA, outline=True)
    for rx in (-1.52, +0.32):
        sc.box((rx, 1.23, -1.96), (0.06, 1.22, 0.06), NAVY, outline=True)
    sc.box((-2.48, 1.25, -1.35), (0.06, 2.30, 1.22), NAVY, outline=True, outline_w=0.009)
    # Kanopi atap halte + papan nama "HALTE BUS KOTA"
    sc.rbox((-0.6, 2.54, -1.32), (4.45, 0.16, 1.68), TEAL_TUA, roundness=0.18, seg=2, outline=True, outline_w=0.012)
    sc.textured_quad(BD._wall_quad(-0.6, 2.54, -0.47, 2.45, 0.28),
                     _banner_tex(o.get("banner", "HALTE BUS KOTA"), bg=NAVY, fg=KUNING, border=PUTIH))

    # Bangku halte (dudukan pas di y=0.42 untuk pose duduk)
    sc.box((-0.6, 0.40, -1.48), (2.25, 0.08, 0.46), ORANYE, outline=True, outline_w=0.009)
    for lx in (-1.52, -0.60, +0.32):
        sc.box((lx, 0.20, -1.48), (0.08, 0.40, 0.36), ABU_TUA, outline=True)

    # Papan LED jadwal kedatangan bus + tiang rambu halte + tempat sampah
    BD.draw_layar_led(sc, (+2.15, 1.62, -1.75), o.get("judul", "JADWAL BUS"),
                      o.get("kiri_lbl", "BUS 01"), o.get("kiri_val", "2 MNT"),
                      o.get("kanan_lbl", ""), o.get("kanan_val", ""), w=1.58, h=0.80)
    sc.cylinder((+2.15, 0.62, -1.75), 0.055, 1.24, ABU_TUA, outline=True)
    sc.cylinder((+3.18, 1.38, -1.80), 0.048, 2.76, ABU_TUA, outline=True)
    sc.textured_quad(BD._wall_quad(+3.18, 2.46, -1.73, 0.62, 0.34),
                     _banner_tex("HALTE", bg=BIRU, fg=PUTIH, border=PUTIH))
    sc.cylinder((-2.85, 0.38, -1.45), 0.22, 0.76, HIJAU_TUA, outline=True, outline_w=0.009)

    # Mobil lewat di lajur jauh agar jalan kota terasa hidup
    car_x = ((t * 4.2) % 28.0) - 14.0
    _mobil_3d(sc, car_x, -0.10, -8.2, col=MERAH, rot_y=0.0, s=1.05)

    # Bus kota 3D (mode: "datang" | "diam" | "pergi" | "lewat" | "tidak")
    bus_mode = o.get("bus", "datang")
    if o.get("bus_x") is not None:
        _bus_3d(sc, float(o["bus_x"]), -0.10, -4.15, col=BIRU, rot_y=0.0, s=1.05)
    elif bus_mode == "datang":
        p = min(1.0, max(0.0, t / 2.6))
        ease_p = 1.0 - (1.0 - p) ** 3
        bx = -13.5 + 13.3 * ease_p
        _bus_3d(sc, bx, -0.10, -4.15, col=BIRU, rot_y=0.0, s=1.05)
    elif bus_mode == "diam":
        _bus_3d(sc, -0.2, -0.10, -4.15, col=BIRU, rot_y=0.0, s=1.05)
    elif bus_mode == "pergi":
        p = min(1.0, max(0.0, t / 2.6))
        bx = -0.2 + 15.0 * (p ** 2)
        _bus_3d(sc, bx, -0.10, -4.15, col=BIRU, rot_y=0.0, s=1.05)
    elif bus_mode == "lewat":
        bx = -14.0 + t * 5.6
        _bus_3d(sc, bx, -0.10, -4.15, col=BIRU, rot_y=0.0, s=1.05)


SETS = {
    "kamar_belajar": set_kamar_belajar,
    "ruang_kerja": set_ruang_kerja,
    "warung": set_warung,
    "hanggar": set_hanggar,
    "gedung_sidang": set_gedung_sidang,
    "kampus": set_kampus,
    "kelas": set_kelas,
    "bank_kas": set_bank_kas,
    "jalan_kota": set_jalan_kota,
    "polos": set_polos,
    "taman_kota": set_taman_kota,
    "kafe": set_kafe,
    "studio_berita": set_studio_berita,
    "rumah_sakit": set_rumah_sakit,
    "kantor_startup": set_kantor_startup,
    "laboratorium": set_laboratorium,
    "stasiun": set_stasiun,
    "pantai": set_pantai,
    "perpustakaan": set_perpustakaan,
    "pengadilan": set_pengadilan,
    "halte_bus": set_halte_bus,
}


def build_set(sc, name, t, opsi):
    key = LATAR_ALIAS.get(name, name)
    fn = SETS.get(key, set_kamar_belajar)
    fn(sc, t, opsi)
