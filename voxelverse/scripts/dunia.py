# -*- coding: utf-8 -*-
"""
dunia.py - 13 set diorama 3D Voxel untuk VoxelVerse + 4 waktu + cuaca.

Set utama:
  studio_kode · kota_hujan · kamar · ruang_belajar · ruang_tamu · sekolah_luar
  kelas · taman · kafe · atap_kota · halte · padang · polos
"""
import math
import numpy as np
from voxel import (
    OUT, PUTIH, KRIM, HITAM, MERAH, BIRU, BIRU_TUA, BIRU_MUDA, TEAL,
    PINK, KUNING, ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA,
    KAYU, KAYU_TUA, UNGU, NAVY, ABU, ABU_TUA, BATA, BATA_TUA,
    clamp, catmull_rom, font, mix, gelap, terang,
)
import benda as BD
from PIL import Image, ImageDraw

LATAR_ALIAS = {
    "ruang_kerja": "studio_kode", "meja_kode": "studio_kode", "kantor": "studio_kode",
    "jalan_kota": "kota_hujan", "jalan_tram": "kota_hujan", "jalan": "kota_hujan",
    "meja_belajar": "ruang_belajar", "ruang_keluarga": "ruang_tamu",
    "sekolah": "sekolah_luar", "halaman_sekolah": "taman", "kantin": "kafe",
    "rooftop": "atap_kota", "stasiun": "halte", "bukit": "padang", "luar": "padang",
    "panggung": "polos",
}

SKY_PRESET = {
    "pagi":  ((196, 224, 248), (255, 228, 186), (0.55, 0.56, 0.58), (0.30, 0.26, 0.24), [0.5, 0.7, 0.4], [1.0, 0.94, 0.82], 0.72, (236, 224, 206)),
    "siang": ((104, 178, 246), (204, 232, 254), (0.56, 0.62, 0.70), (0.30, 0.30, 0.30), [0.4, 0.9, 0.35], [1.0, 0.98, 0.94], 0.82, (196, 224, 248)),
    "sore":  ((84, 72, 108),   (232, 150, 104), (0.44, 0.36, 0.36), (0.22, 0.18, 0.16), [-0.5, 0.45, 0.5], [1.0, 0.74, 0.50], 0.68, (152, 118, 108)),
    "malam": ((18, 24, 48),    (46, 54, 78),    (0.24, 0.26, 0.34), (0.14, 0.14, 0.18), [0.3, 0.8, -0.4], [0.55, 0.66, 0.92], 0.26, (34, 40, 56)),
}


def configure_sky(sc, o):
    w = o.get("waktu", "siang")
    cuaca = o.get("cuaca", "cerah")
    top, bot, asky, agrd, sdir, scol, sint, fog = SKY_PRESET.get(w, SKY_PRESET["siang"])
    if cuaca in ("hujan", "gerimis") and w != "malam":
        top = tuple(int(c * 0.68) for c in top)
        bot = tuple(int(c * 0.74) for c in bot)
        sint *= 0.55
        fog = (88, 96, 108) if w == "sore" else (120, 132, 146)
    sc.set_sky(top, bot, asky, agrd, sdir, scol, sint, fog, fog_start=14.0, fog_density=0.036 if cuaca in ("hujan", "gerimis") else 0.022)


def _pohon(sc, x, y, z, s=1.0, col=HIJAU):
    sc.drop_shadow(x, y, z, 0.45 * s, 0.45 * s, 0.25)
    sc.box((x, y + 0.55 * s, z), (0.28 * s, 1.1 * s, 0.28 * s), COKLAT, cast_refl=True)
    sc.box((x, y + 1.45 * s, z), (1.05 * s, 0.85 * s, 1.05 * s), col, cast_refl=True)
    sc.box((x, y + 2.02 * s, z), (0.72 * s, 0.46 * s, 0.72 * s), HIJAU_TUA)


def _building_facade(sc, bx, bz, w, h, d, wall_col, lit_seed=1, with_balcony=True, side=1):
    """Gedung voxel bertingkat dengan jendela hangat menyala & balkon tangga darurat."""
    sc.box((bx, h * 0.5, bz), (w, h, d), wall_col, cast_refl=True)
    sc.box((bx, h + 0.14, bz), (w + 0.18, 0.28, d + 0.18), gelap(wall_col, 0.28))
    face_x = bx - side * (w * 0.5 + 0.02)
    cols = max(2, int(d / 1.5))
    floors = max(2, int(h / 1.85))
    for fl in range(floors):
        wy = 1.35 + fl * 1.75
        if wy > h - 0.9:
            continue
        for c in range(cols):
            wz = bz - d * 0.34 + c * (d * 0.68 / max(1, cols - 1))
            lit = ((fl * 7 + c * 13 + lit_seed) % 5) != 0
            wcol = (244, 192, 114) if lit else (38, 46, 58)
            em = 0.68 if lit else 0.0
            sc.box((face_x, wy, wz), (0.06, 0.82, 0.66), (34, 38, 46), bias=-0.01)
            sc.box((face_x - side * 0.02, wy, wz), (0.04, 0.70, 0.54), wcol, emissive=em, bias=-0.02, cast_refl=lit)
            # Daun jendela hijau/teal di beberapa lantai
            if (fl + c + lit_seed) % 3 == 0:
                sc.box((face_x - side * 0.03, wy, wz - 0.36), (0.06, 0.76, 0.14), TEAL)
                sc.box((face_x - side * 0.03, wy, wz + 0.36), (0.06, 0.76, 0.14), TEAL)
    if with_balcony and h >= 5.0:
        for fl in range(1, floors):
            wy = 0.88 + fl * 1.75
            if wy > h - 1.2:
                continue
            sc.box((face_x - side * 0.26, wy, bz), (0.52, 0.08, d * 0.45), (36, 40, 48))
            sc.box((face_x - side * 0.49, wy + 0.24, bz), (0.05, 0.40, d * 0.45), (36, 40, 48))


def _sign_texture(teks, bg=(255, 226, 130), fg=(44, 48, 64)):
    im = Image.new("RGBA", (240, 88), bg + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 236, 84], outline=OUT + (255,), width=4)
    d.text((120, 44), str(teks), font=font("judul", 38), fill=fg + (255,), anchor="mm")
    return im


# ================================================================== 1. STUDIO KODE
def set_studio_kode(sc, t, o):
    """Studio coding hangat di malam hujan dengan jendela bata besar menghadap kota."""
    configure_sky(sc, o)
    if o.get("waktu") == "malam":
        sc.amb_sky = (0.20, 0.22, 0.28)
        sc.amb_ground = (0.14, 0.12, 0.12)
        sc.sun_int = 0.18
    # Lantai studio & karpet bergaris
    sc.tiled_plane(-3.0, -3.0, 3.0, 1.9, 0.0, (124, 92, 68), tile=1.2)
    sc.tiled_plane(-1.4, -1.6, 1.4, 0.8, 0.01, (226, 214, 192), tile=0.7, checker=(78, 128, 134), bias=-0.01)
    # Dinding belakang (rak buku) & dinding samping
    sc.tiled_wall_z(-3.0, 0.0, 3.0, 3.2, -2.9, (228, 220, 206), normal_z=1, tile=1.2)
    sc.tiled_wall_z(-3.0, 0.0, 3.0, 3.2, -2.9, (228, 220, 206), normal_z=1, tile=1.2)
    sc.tiled_wall_x(-3.0, 0.0, 1.9, 3.2, -2.95, (212, 204, 190), normal_x=1, tile=1.2)
    sc.tiled_wall_x(-3.0, 0.0, 1.9, 3.2, 2.95, (212, 204, 190), normal_x=-1, tile=1.2)
    sc.tiled_plane(-3.0, -3.0, 3.0, 1.9, 3.2, (196, 188, 174), tile=1.5)
    # List teal bawah dinding
    sc.box((0.0, 0.44, -2.84), (5.8, 0.88, 0.12), (56, 108, 114))

    # Rak buku di dinding belakang (terlihat saat reverse-shot wajah karakter!)
    sc.box((0.0, 1.95, -2.74), (3.8, 1.35, 0.28), KAYU_TUA)
    book_cols = [MERAH, TEAL, KUNING, BIRU, ORANYE, KRIM, HIJAU, BATA]
    for sh in (1.42, 1.88, 2.34):
        sc.box((0.0, sh, -2.68), (3.6, 0.06, 0.28), KAYU)
        for bi in range(14):
            bx = -1.55 + bi * 0.24 + ((bi % 2) * 0.02)
            bh = 0.24 + ((bi * 3 + int(sh * 10)) % 4) * 0.04
            sc.box((bx, sh + bh * 0.5 + 0.03, -2.66), (0.14, bh, 0.20), book_cols[(bi + int(sh * 3)) % len(book_cols)])

    # Dinding jendela depan (z = +1.85) — bata di luar, terbuka lebar di tengah!
    # Bawah jendela (bata)
    sc.box((0.0, 0.44, 1.86), (6.0, 0.88, 0.24), BATA)
    for bi in range(-7, 8):
        sc.box((bi * 0.40, 0.72, 1.99), (0.34, 0.14, 0.05), BATA_TUA)
    # Atas & kiri-kanan jendela
    sc.box((0.0, 2.86, 1.86), (6.0, 0.72, 0.24), BATA)
    sc.box((-2.35, 1.69, 1.86), (1.3, 1.64, 0.24), BATA)
    sc.box((2.35, 1.69, 1.86), (1.3, 1.64, 0.24), BATA)
    # Kusen jendela gelap & palang tengah + ambang luar + pot tanaman
    sc.box((0.0, 0.90, 1.92), (3.44, 0.08, 0.34), (42, 46, 52))
    sc.box((0.0, 2.48, 1.86), (3.44, 0.08, 0.28), (42, 46, 52))
    sc.box((0.0, 1.69, 1.86), (0.06, 1.56, 0.10), (42, 46, 52))
    sc.box((0.0, 1.72, 1.86), (3.36, 0.06, 0.10), (42, 46, 52))
    # Kaca jendela sangat tipis agar bagian dalam tetap jernih
    sc.quad([(-1.66, 0.92, 1.86), (1.66, 0.92, 1.86), (1.66, 2.46, 1.86), (-1.66, 2.46, 1.86)], (185, 215, 235), alpha=0.08, specular=0.75, two_sided=True)
    # Pot tanaman voxel di ambang luar jendela
    sc.box((-0.92, 1.02, 2.08), (0.76, 0.22, 0.26), COKLAT)
    for px_off, ph in ((-0.20, 0.22), (0.0, 0.30), (0.20, 0.20)):
        sc.box((-0.92 + px_off, 1.15 + ph * 0.5, 2.08), (0.16, ph, 0.16), HIJAU)
        sc.box((-0.92 + px_off, 1.24 + ph, 2.08), (0.22, 0.08, 0.22), HIJAU_TUA)

    # Meja kerja menghadap jendela (z = +1.16) + kursi kerja (x = +0.08, z = +0.36)
    sc.box((0.0, 0.74, 1.16), (2.40, 0.07, 0.84), KAYU)
    for lx in (-1.08, 1.08):
        for lz in (0.80, 1.50):
            sc.box((lx, 0.36, lz), (0.08, 0.72, 0.08), (46, 48, 56))
    BD.draw_prop(sc, "kursi_kerja", (0.08, 0.0, 0.36), rot=(0.0, 0.0, 0.0), s=1.02)
    BD.draw_prop(sc, "monitor_kode", (-0.32, 0.775, 1.22), rot=(0.0, 162.0, 0.0), s=1.02, t=t,
                 progres=o.get("ketik_progres", 0.92), spark=bool(o.get("spark_layar", False)), build=bool(o.get("build_layar", False)))
    BD.draw_prop(sc, "keyboard", (0.04, 0.775, 0.88), rot=(0.0, 174.0, 0.0), s=1.0, t=t)
    BD.draw_prop(sc, "mug_kopi", (-0.82, 0.775, 0.98), s=0.95, t=t)

    # Lampu gantung hangat di atas meja
    BD.draw_prop(sc, "lampu_gantung", (0.10, 2.52, 0.65), s=1.1, intensitas=1.8)

    # Pemandangan kota hujan di luar jendela (z = +5..+14)
    sc.tiled_plane(-12.0, 2.2, 12.0, 16.0, 0.0, (44, 48, 56), tile=2.5)
    _building_facade(sc, -3.5, 9.5, 3.6, 8.2, 3.6, BATA, lit_seed=2, with_balcony=False, side=-1)
    _building_facade(sc, 3.2, 10.5, 3.8, 9.0, 3.8, (206, 152, 118), lit_seed=5, with_balcony=False, side=-1)
    _building_facade(sc, 0.0, 13.5, 4.4, 10.5, 3.0, (92, 102, 116), lit_seed=9, with_balcony=False, side=-1)
    # Tiang listrik & kabel terlihat dari jendela
    sc.box((1.55, 1.8, 4.6), (0.18, 3.8, 0.18), COKLAT_TUA)
    sc.box((1.55, 2.9, 4.6), (1.1, 0.10, 0.10), COKLAT_TUA)
    sc.beam((-3.0, 2.9, 5.2), (1.55, 2.9, 4.6), 0.02, OUT, emissive=0.0)
    sc.beam((1.55, 2.9, 4.6), (6.0, 2.8, 5.6), 0.02, OUT, emissive=0.0)


# ================================================================== 2. KOTA HUJAN
def set_kota_hujan(sc, t, o):
    """Jalan kota basah memantul dengan bangunan bata, tiang kabel, lampu jalan, dan tram."""
    configure_sky(sc, o)
    sc.wet_ground = (o.get("cuaca", "hujan") in ("hujan", "gerimis")) or bool(o.get("basah", True))
    sc.wet_strength = 0.28

    # Aspal jalan basah + trotoar kiri-kanan + rel tram + zebra cross
    sc.tiled_plane(-4.2, -26.0, 4.2, 26.0, 0.0, (38, 42, 50), tile=2.2, specular=0.85)
    sc.tiled_plane(-6.8, -26.0, -4.2, 26.0, 0.10, (124, 128, 136), tile=2.2)
    sc.tiled_plane(4.2, -26.0, 6.8, 26.0, 0.10, (124, 128, 136), tile=2.2)
    # Rel tram
    for rx in (-0.75, 0.75):
        sc.box((rx, 0.012, 0.0), (0.09, 0.02, 50.0), (96, 102, 114), bias=-0.02)
    # Zebra cross
    for zz in (-4.0, 8.0):
        for sx in np.linspace(-3.2, 3.2, 6):
            sc.box((float(sx), 0.012, zz), (0.52, 0.015, 1.8), (224, 228, 232), bias=-0.02)

    # Deretan gedung kota di kiri & kanan jalan (gedung studio bata di kiri z=0 punya jendela lantai 2 terbuka)
    b_cols = [BATA, (216, 146, 116), (178, 192, 198), (194, 124, 96)]
    for i, bz in enumerate((-18.0, -11.5, -5.5, 5.5, 12.0, 18.5)):
        _building_facade(sc, -8.8, bz, 4.4, 7.8 + (i % 3) * 1.8, 5.0, b_cols[i % 4], lit_seed=i + 1, side=-1)
    for i, bz in enumerate(range(-18, 22, 7)):
        _building_facade(sc, 8.8, bz + 1.5, 4.4, 8.4 + ((i + 1) % 3) * 1.6, 5.8, b_cols[(i + 2) % 4], lit_seed=i + 4, side=1)

    # Gedung studio lantai 2 terbuka di kiri jalan (z = -2.6..+2.6, fasad x = -6.6)
    sc.box((-8.8, 1.2, 0.0), (4.4, 2.4, 5.0), (132, 62, 48), cast_refl=True)
    sc.box((-6.58, 1.15, 0.0), (0.08, 1.7, 3.2), (242, 186, 108), emissive=0.65, cast_refl=True)
    # Ruang studio lantai 2 terbuka (y = 2.4..4.3)
    sc.box((-7.6, 2.4, 0.0), (2.2, 0.14, 3.6), KAYU_TUA)
    sc.box((-7.6, 4.35, 0.0), (2.2, 0.14, 3.6), (144, 148, 144))
    sc.box((-8.7, 3.38, 0.0), (0.18, 2.0, 3.8), (156, 174, 170))
    sc.box((-7.6, 3.38, -1.8), (2.2, 2.0, 0.16), (156, 170, 168))
    sc.box((-7.6, 3.38, 1.8), (2.2, 2.0, 0.16), (156, 170, 168))
    # Dinding bata fasad dengan jendela besar menghadap jalan
    sc.box((-6.6, 2.65, 0.0), (0.22, 0.50, 5.0), BATA, cast_refl=True)
    sc.box((-6.6, 4.32, 0.0), (0.22, 0.38, 5.0), BATA)
    sc.box((-6.6, 3.48, -2.0), (0.22, 1.32, 1.0), BATA)
    sc.box((-6.6, 3.48, 2.0), (0.22, 1.32, 1.0), BATA)
    sc.box((-8.8, 5.65, 0.0), (4.4, 2.3, 5.0), BATA)
    sc.box((-6.55, 2.92, 0.0), (0.28, 0.08, 3.1), (42, 46, 52))
    sc.box((-6.55, 3.48, 0.0), (0.10, 1.25, 0.06), (42, 46, 52))
    sc.box((-6.40, 3.04, -0.55), (0.24, 0.20, 0.72), COKLAT)
    for pz_o in (-0.75, -0.55, -0.35):
        sc.box((-6.40, 3.22, pz_o), (0.14, 0.18, 0.14), HIJAU)
    # Meja, monitor & lampu hangat lantai 2
    sc.box((-7.05, 3.02, 0.0), (0.62, 0.06, 1.6), KAYU)
    sc.box((-6.95, 3.30, 0.45), (0.06, 0.40, 0.62), (28, 34, 44))
    sc.add_light((-7.35, 3.92, 0.0), color=(255, 196, 118), intensity=0.65, radius=3.0, halo=0.12)
    if o.get("jendela_studio"):
        import tokoh as TK
        TK.TokohVoxel("arka").draw(sc, (-7.55, 2.46, 0.12), TK.state(pose="duduk_ketik", expr="fokus", hadap="kanan", t=t))
        TK.TokohVoxel("robo").draw(sc, (-7.05, 3.05, -0.45), TK.state(pose="diam", expr="senang", hadap="kanan", t=t))

    # Tiang listrik, kotak gardu putih, & kabel udara catenary + lampu jalan
    pole_zs = [-14.0, -4.0, 6.0, 16.0]
    for i, pz in enumerate(pole_zs):
        sc.box((-4.45, 2.7, pz), (0.18, 5.4, 0.18), COKLAT_TUA, cast_refl=True)
        sc.box((-4.05, 4.8, pz), (1.1, 0.10, 0.10), COKLAT_TUA)
        if abs(pz - (-4.0)) < 0.1:
            sc.box((-4.45, 3.85, pz), (0.40, 0.54, 0.30), (222, 226, 232), cast_refl=True)
            sc.box((-4.22, 3.85, pz), (0.06, 0.34, 0.22), ABU_TUA)
        BD.draw_prop(sc, "lampu_jalan", (4.5, 0.10, pz + 1.5), rot=(0.0, 180.0, 0.0), s=1.0)
        if i + 1 < len(pole_zs):
            nz = pole_zs[i + 1]
            for wx in (-4.35, -3.65):
                pts = [(wx, 4.82, pz), (wx, 4.45, (pz + nz) * 0.5), (wx, 4.82, nz)]
                for k in range(8):
                    p0 = catmull_rom(pts, k / 8.0)
                    p1 = catmull_rom(pts, (k + 1) / 8.0)
                    sc.beam(p0, p1, 0.022, OUT, emissive=0.0)
    # Kabel melintang jalan
    for pz in (-4.0, 6.0):
        sc.beam((-4.4, 4.8, pz), (4.4, 4.6, pz), 0.022, OUT, emissive=0.0)

    # Tram bergerak mulus sepanjang rel (bisa dikendalikan dengan o["tram_z"])
    tz = o.get("tram_z")
    if tz is None:
        tz = -10.0 + (t * 1.9) % 24.0
    BD.draw_prop(sc, "tram", (0.0, 0.02, float(tz)), rot=(0.0, 0.0, 0.0), s=1.05, t=t)

    # Pohon kota di trotoar
    for pz in (-9.5, 1.0, 11.5):
        _pohon(sc, -5.2, 0.10, pz, s=0.9, col=HIJAU_TUA)


# ================================================================== 3. KAMAR
def set_kamar(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-3.2, -3.2, 3.2, 3.2, 0.0, KAYU, tile=1.4)
    sc.tiled_plane(-1.1, -0.6, 1.3, 1.4, 0.01, (216, 228, 240), tile=0.8, bias=-0.01)
    sc.tiled_wall_z(-3.2, 0.0, 3.2, 3.2, -2.8, (242, 232, 214), normal_z=1, tile=1.4)
    sc.tiled_wall_x(-3.2, 0.0, 3.2, 3.2, -3.0, (230, 218, 200), normal_x=1, tile=1.4)
    # Kasur + bantal + selimut
    sc.box((-1.35, 0.26, -1.65), (1.7, 0.44, 2.1), KAYU_TUA)
    sc.box((-1.35, 0.48, -2.58), (1.7, 0.72, 0.16), KAYU_TUA)
    sc.box((-1.35, 0.54, -1.65), (1.56, 0.20, 1.92), PUTIH)
    sc.box((-1.35, 0.68, -2.25), (0.88, 0.14, 0.42), KRIM)
    if o.get("selimut", True):
        sc.box((-1.35, 0.65, -1.32), (1.60, 0.18, 1.28), (118, 174, 214))
    # Nakas + jam weker + lampu tidur
    sc.box((0.25, 0.36, -2.25), (0.64, 0.72, 0.56), KAYU_TUA)
    BD.draw_prop(sc, "jam_weker", (0.25, 0.72, -2.20), s=0.95, t=t, jam=o.get("jam", "07:00"))
    # Jendela di dinding belakang kanan
    sc.box((1.55, 1.75, -2.74), (1.28, 1.18, 0.12), (44, 48, 56))
    w_sky = (46, 62, 112) if o.get("waktu") == "malam" else (164, 216, 250)
    sc.box((1.55, 1.75, -2.70), (1.12, 1.02, 0.08), w_sky, emissive=0.75)
    sc.add_light((1.55, 1.75, -2.1), color=w_sky, intensity=0.9, radius=3.5)
    if o.get("waktu") == "malam":
        sc.add_light((0.25, 1.15, -2.0), color=(255, 200, 118), intensity=1.4, radius=3.2, halo=0.18)


# ================================================================== 4. RUANG BELAJAR
def set_ruang_belajar(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-3.2, -3.2, 3.2, 3.2, 0.0, KAYU, tile=1.4)
    sc.tiled_wall_z(-3.2, 0.0, 3.2, 3.2, -2.4, (238, 228, 210), normal_z=1, tile=1.4)
    sc.box((0.0, 0.74, -1.15), (2.2, 0.08, 0.85), KAYU_TUA)
    for lx in (-0.98, 0.98):
        sc.box((lx, 0.36, -1.15), (0.10, 0.72, 0.72), (52, 56, 64))
    BD.draw_prop(sc, "kursi_kerja", (0.0, 0.0, -0.42), rot=(0.0, 180.0, 0.0))
    BD.draw_prop(sc, "laptop", (-0.15, 0.78, -1.15), rot=(0.0, 0.0, 0.0))
    BD.draw_prop(sc, "buku", (0.68, 0.81, -1.15), rot=(90.0, 0.0, 0.0), warna=MERAH)
    # Lampu meja hangat
    sc.box((0.86, 0.96, -1.35), (0.06, 0.38, 0.06), ABU_TUA)
    sc.box((0.78, 1.16, -1.30), (0.20, 0.14, 0.20), (255, 214, 130), emissive=1.3)
    sc.add_light((0.74, 1.05, -1.15), color=(255, 204, 120), intensity=1.8, radius=3.6, halo=0.25)


# ================================================================== 5. RUANG TAMU
def set_ruang_tamu(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-3.6, -3.4, 3.6, 3.4, 0.0, (194, 152, 114), tile=1.5)
    sc.tiled_plane(-1.4, -0.8, 1.4, 1.4, 0.01, (226, 216, 198), tile=0.8, bias=-0.01)
    sc.tiled_wall_z(-3.6, 0.0, 3.6, 3.2, -2.5, (236, 228, 214), normal_z=1, tile=1.5)
    # Sofa biru
    sc.box((0.0, 0.28, -1.45), (2.2, 0.42, 0.92), BIRU)
    sc.box((0.0, 0.66, -1.80), (2.2, 0.56, 0.22), BIRU_TUA)
    sc.box((-1.02, 0.50, -1.45), (0.22, 0.46, 0.92), BIRU_TUA)
    sc.box((1.02, 0.50, -1.45), (0.22, 0.46, 0.92), BIRU_TUA)
    # Meja kopi & lampu lantai
    sc.box((0.0, 0.24, 0.25), (1.15, 0.08, 0.68), KAYU_TUA)
    sc.box((-1.85, 0.75, -1.75), (0.08, 1.5, 0.08), (48, 52, 60))
    sc.box((-1.85, 1.55, -1.75), (0.36, 0.26, 0.36), (255, 224, 152), emissive=1.1)
    sc.add_light((-1.85, 1.48, -1.6), color=(255, 212, 138), intensity=1.7, radius=4.2, halo=0.28)


# ================================================================== 6. SEKOLAH LUAR
def set_sekolah_luar(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-12.0, -8.0, 12.0, 12.0, 0.0, (112, 186, 108), tile=2.4)
    sc.tiled_plane(-2.2, -2.5, 2.2, 12.0, 0.015, (206, 198, 182), tile=1.5, bias=-0.01)
    # Gedung sekolah utama
    sc.box((0.0, 2.2, -5.2), (8.6, 4.4, 3.4), (242, 232, 210), cast_refl=True)
    sc.box((0.0, 4.58, -5.2), (9.0, 0.44, 3.8), BATA)
    sc.box((0.0, 1.15, -3.45), (1.45, 2.2, 0.14), BIRU)
    for wx in (-2.6, -1.4, 1.4, 2.6):
        sc.box((wx, 2.4, -3.45), (0.76, 0.95, 0.10), BIRU_MUDA, emissive=0.35)
    # Papan nama sekolah (kustom lewat o["papan"])
    pts = [(-1.3, 4.15, -3.42), (1.3, 4.15, -3.42), (1.3, 3.25, -3.42), (-1.3, 3.25, -3.42)]
    sc.textured_quad(pts, _sign_texture(o.get("papan", "SMP VOXEL")), emissive=0.2, bias=-0.03)
    # Tiang bendera & pohon
    sc.box((-4.8, 2.6, -1.6), (0.09, 5.2, 0.09), ABU)
    sc.box((-4.28, 4.85, -1.6), (0.95, 0.30, 0.03), MERAH)
    sc.box((-4.28, 4.55, -1.6), (0.95, 0.30, 0.03), PUTIH)
    for px, pz in ((-6.0, 1.5), (5.6, 1.2), (-5.8, -2.5), (6.0, -2.8)):
        _pohon(sc, px, 0.0, pz, s=1.05)


# ================================================================== 7. KELAS
def set_kelas(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-4.5, -4.5, 4.5, 4.5, 0.0, (218, 198, 166), tile=1.5)
    sc.tiled_wall_z(-4.5, 0.0, 4.5, 3.4, -3.2, (242, 236, 224), normal_z=1, tile=1.5)
    # Papan tulis
    sc.box((0.0, 1.85, -3.10), (3.4, 1.45, 0.10), KAYU_TUA)
    sc.box((0.0, 1.85, -3.04), (3.16, 1.24, 0.06), (36, 86, 62))
    if o.get("papan_tulis"):
        im = Image.new("RGBA", (320, 130), (36, 86, 62, 255))
        d = ImageDraw.Draw(im)
        d.text((160, 65), str(o["papan_tulis"]), font=font("judul", 30), fill=PUTIH + (255,), anchor="mm")
        sc.textured_quad([(-1.5, 2.42, -3.00), (1.5, 2.42, -3.00), (1.5, 1.28, -3.00), (-1.5, 1.28, -3.00)], im, emissive=0.1, bias=-0.03)
    # Meja & kursi siswa
    for mx in (-1.4, 0.0, 1.4):
        for mz in (-0.6, 1.3):
            sc.box((mx, 0.72, mz), (0.96, 0.07, 0.56), KAYU)
            sc.box((mx - 0.40, 0.36, mz), (0.06, 0.70, 0.46), ABU_TUA)
            sc.box((mx + 0.40, 0.36, mz), (0.06, 0.70, 0.46), ABU_TUA)
            sc.box((mx, 0.42, mz + 0.52), (0.46, 0.06, 0.44), TEAL)


# ================================================================== 8. TAMAN
def set_taman(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-12.0, -12.0, 12.0, 12.0, 0.0, HIJAU, tile=2.4)
    sc.tiled_plane(-1.4, -12.0, 1.4, 12.0, 0.015, (214, 204, 186), tile=1.8, bias=-0.01)
    # Bangku taman
    sc.box((-2.2, 0.44, -0.8), (1.7, 0.08, 0.56), KAYU_TUA)
    sc.box((-2.2, 0.78, -1.04), (1.7, 0.46, 0.08), KAYU_TUA)
    sc.box((-2.9, 0.22, -0.8), (0.10, 0.44, 0.50), (44, 48, 56))
    sc.box((-1.5, 0.22, -0.8), (0.10, 0.44, 0.50), (44, 48, 56))
    for px, pz in ((-4.2, -3.5), (3.8, -2.5), (-4.5, 3.2), (4.2, 4.0)):
        _pohon(sc, px, 0.0, pz, s=1.15)
    BD.draw_prop(sc, "lampu_jalan", (2.1, 0.0, -2.2), rot=(0.0, 180.0, 0.0), s=0.95)


# ================================================================== 9. KAFE
def set_kafe(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-4.2, -4.2, 4.2, 4.2, 0.0, (164, 120, 86), tile=1.5)
    sc.tiled_wall_z(-4.2, 0.0, 4.2, 3.4, -3.2, (238, 224, 202), normal_z=1, tile=1.5)
    # Konter kafe
    sc.box((0.0, 0.52, -2.1), (4.6, 1.04, 0.92), KAYU_TUA)
    sc.box((0.0, 1.06, -2.1), (4.7, 0.08, 1.0), KRIM)
    # Meja & kursi bundar kotak
    for mx in (-1.3, 1.3):
        sc.box((mx, 0.72, 0.6), (0.95, 0.07, 0.95), KAYU)
        sc.box((mx, 0.36, 0.6), (0.14, 0.72, 0.14), (44, 48, 56))
        BD.draw_prop(sc, "mug_kopi", (mx - 0.18, 0.76, 0.6), t=t)
    BD.draw_prop(sc, "lampu_gantung", (-1.3, 2.55, 0.6), s=1.0, intensitas=1.6)
    BD.draw_prop(sc, "lampu_gantung", (1.3, 2.55, 0.6), s=1.0, intensitas=1.6)


# ================================================================== 10. ATAP KOTA
def set_atap_kota(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-5.5, -5.5, 5.5, 5.5, 0.0, (108, 114, 124), tile=2.0)
    sc.box((0.0, 0.45, -5.3), (11.0, 0.90, 0.24), (72, 76, 88))
    sc.box((-5.3, 0.45, 0.0), (0.24, 0.90, 10.6), (72, 76, 88))
    sc.box((5.3, 0.45, 0.0), (0.24, 0.90, 10.6), (72, 76, 88))
    # Unit AC & skyline gedung belakang
    sc.box((-3.2, 0.45, -3.5), (1.1, 0.90, 0.76), ABU)
    for i, bx in enumerate((-9.0, -4.5, 0.5, 5.5, 10.0)):
        _building_facade(sc, bx, -12.5 - (i % 2) * 3.0, 3.6, 7.5 + (i % 3) * 2.5, 3.6, (54, 62, 82), lit_seed=i + 3, with_balcony=False, side=-1)
    sc.add_light((0.0, 2.4, 0.0), color=(255, 210, 140), intensity=1.4, radius=6.0, halo=0.25)


# ================================================================== 11. HALTE
def set_halte(sc, t, o):
    set_kota_hujan(sc, t, o)
    # Halte beratap kaca di trotoar kanan
    sc.box((4.65, 1.35, 0.0), (0.14, 2.7, 3.4), TEAL)
    sc.box((4.25, 2.68, 0.0), (1.35, 0.14, 3.6), (52, 58, 70))
    sc.box((4.35, 0.46, 0.0), (0.52, 0.10, 2.2), KAYU)
    sc.add_light((4.2, 2.45, 0.0), color=(255, 224, 155), intensity=1.5, radius=3.5, halo=0.2)


# ================================================================== 12. PADANG
def set_padang(sc, t, o):
    configure_sky(sc, o)
    sc.tiled_plane(-14.0, -14.0, 14.0, 14.0, 0.0, HIJAU, tile=2.6)
    sc.box((-6.5, 0.8, -8.5), (8.0, 1.6, 5.0), HIJAU_TUA)
    sc.box((6.5, 1.1, -9.5), (9.0, 2.2, 5.5), (72, 160, 88))
    for px, pz in ((-4.2, -3.8), (3.8, -4.4), (5.5, 1.5), (-5.5, 2.2)):
        _pohon(sc, px, 0.0, pz, s=1.2)


# ================================================================== 13. POLOS
def set_polos(sc, t, o):
    configure_sky(sc, o)
    col = o.get("warna", (236, 232, 224))
    sc.set_sky(col, tuple(max(0, c - 24) for c in col), (0.58, 0.60, 0.64), (0.34, 0.34, 0.36), [0.4, 0.85, 0.4], [1.0, 0.98, 0.94], 0.78, col)
    sc.tiled_plane(-4.5, -4.5, 4.5, 4.5, 0.0, tuple(max(0, c - 14) for c in col), tile=1.5)


SET = {
    "studio_kode": set_studio_kode,
    "kota_hujan": set_kota_hujan,
    "kamar": set_kamar,
    "ruang_belajar": set_ruang_belajar,
    "ruang_tamu": set_ruang_tamu,
    "sekolah_luar": set_sekolah_luar,
    "kelas": set_kelas,
    "taman": set_taman,
    "kafe": set_kafe,
    "atap_kota": set_atap_kota,
    "halte": set_halte,
    "padang": set_padang,
    "polos": set_polos,
}


def build_world(sc, latar, t, opsi):
    name = LATAR_ALIAS.get(latar, latar)
    fn = SET.get(name, set_studio_kode)
    fn(sc, t, opsi)
