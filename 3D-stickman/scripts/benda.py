# -*- coding: utf-8 -*-
"""
benda.py - Properti 3D, poster/kalender/papan teks tajam, pesawat, podium, gerobak, dan ikon emosi 3D-stickman.
"""
import functools, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from engine3d import (
    OUT, PUTIH, KRIM, HITAM, MERAH, MERAH_TUA, BIRU, BIRU_TUA, BIRU_MUDA,
    TEAL, KUNING, ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA,
    KAYU, KAYU_TUA, ABU, ABU_TUA, NAVY, PINK, font, euler_mat, clamp,
)

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from aset_global import (  # noqa: E402
    pop_scale, pulse_scale, draw_arrow_3d, draw_pipe_flow, draw_dial_gauge,
    draw_tag_callout, draw_water_tank, draw_piston_engine, draw_engineering_3d,
)


# ------------------------------------------------------------------ tekstur papan / kalender / poster (cached)
@functools.lru_cache(maxsize=128)
def _tex_kalender(bulan, tahun, sub):
    im = Image.new("RGBA", (280, 340), PUTIH + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 280, 74], fill=MERAH + (255,))
    d.rectangle([4, 4, 276, 336], outline=OUT + (255,), width=5)
    d.text((140, 38), str(bulan).upper(), font=font("judul", 30), fill=PUTIH + (255,), anchor="mm")
    d.text((140, 110), "TAHUN", font=font("teks", 20), fill=ABU_TUA + (255,), anchor="mm")
    d.text((140, 198), str(tahun), font=font("judul", 84), fill=HITAM + (255,), anchor="mm")
    if sub:
        d.text((140, 294), str(sub), font=font("teks", 20), fill=ABU_TUA + (255,), anchor="mm")
    return im


@functools.lru_cache(maxsize=128)
def _tex_poster_pesawat(judul, tanggal, sub):
    im = Image.new("RGBA", (300, 380), KRIM + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 300, 62], fill=MERAH + (255,))
    d.text((150, 32), str(judul), font=font("judul", 26), fill=PUTIH + (255,), anchor="mm")
    d.rectangle([24, 78, 276, 232], fill=BIRU_MUDA + (255,), outline=OUT + (255,), width=4)
    # Awan & bukit
    d.chord([24, 195, 276, 260], 180, 360, fill=HIJAU + (255,))
    # Siluet pesawat N250
    d.polygon([(68, 152), (235, 162), (255, 174), (195, 178), (74, 168)], fill=PUTIH + (255,), outline=OUT + (255,), width=3)
    d.polygon([(64, 154), (56, 112), (82, 112), (96, 154)], fill=PUTIH + (255,), outline=OUT + (255,), width=3)
    d.rectangle([58, 112, 82, 126], fill=MERAH + (255,))
    d.line([95, 166, 228, 170], fill=MERAH + (255,), width=4)
    d.text((150, 268), str(tanggal), font=font("judul", 24), fill=HITAM + (255,), anchor="mm")
    d.text((150, 316), str(sub), font=font("judul", 46), fill=MERAH + (255,), anchor="mm")
    d.rectangle([4, 4, 296, 376], outline=COKLAT_TUA + (255,), width=8)
    return im


@functools.lru_cache(maxsize=64)
def _tex_peta_indonesia(judul="INDONESIA"):
    im = Image.new("RGBA", (420, 240), (222, 236, 212, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([6, 6, 414, 234], outline=COKLAT_TUA + (255,), width=8)
    d.text((210, 28), str(judul), font=font("judul", 22), fill=HITAM + (255,), anchor="mm")
    islands = [
        [(36, 86), (92, 136), (110, 162), (84, 170), (28, 108)],            # Sumatra
        [(114, 168), (196, 172), (198, 188), (112, 184)],                   # Jawa
        [(142, 74), (206, 68), (218, 126), (168, 134), (138, 112)],         # Kalimantan
        [(238, 86), (282, 88), (274, 140), (242, 138), (254, 112)],         # Sulawesi
        [(312, 102), (392, 122), (396, 164), (344, 158), (314, 132)],       # Papua
    ]
    for poly in islands:
        d.polygon(poly, fill=(134, 184, 92, 255), outline=HIJAU_TUA + (255,), width=3)
    return im


@functools.lru_cache(maxsize=128)
def _tex_papan(judul, baris1, baris2="", bg=(36, 66, 48), fg=PUTIH, border=KAYU_TUA):
    im = Image.new("RGBA", (420, 240), bg + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 416, 236], outline=border + (255,), width=10)
    if judul:
        d.text((210, 46), str(judul), font=font("judul", 28), fill=KUNING + (255,), anchor="mm")
    d.text((210, 120), str(baris1), font=font("judul", 36), fill=fg + (255,), anchor="mm")
    if baris2:
        d.text((210, 178), str(baris2), font=font("teks", 24), fill=fg + (255,), anchor="mm")
    return im


@functools.lru_cache(maxsize=64)
def _tex_layar_led(judul, kiri_lbl, kiri_val, kanan_lbl="", kanan_val=""):
    im = Image.new("RGBA", (440, 220), (24, 28, 34, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 436, 216], outline=(58, 64, 78, 255), width=6)
    d.rectangle([6, 6, 434, 44], fill=(42, 48, 60, 255))
    d.text((220, 25), str(judul), font=font("judul", 20), fill=PUTIH + (255,), anchor="mm")
    if kanan_lbl:
        def _fit(txt, max_w, base):
            f = base
            while f > 18:
                bb = d.textbbox((0, 0), str(txt), font=font("judul", f))
                if bb[2] - bb[0] <= max_w:
                    break
                f -= 4
            return f
        fs_l = _fit(kiri_val, 156, 62 if len(str(kiri_val)) <= 4 else 34)
        fs_r = _fit(kanan_val, 156, 62 if len(str(kanan_val)) <= 4 else 34)
        d.rectangle([28, 60, 200, 92], fill=MERAH + (255,))
        d.text((114, 76), str(kiri_lbl), font=font("teks", 18), fill=PUTIH + (255,), anchor="mm")
        d.text((114, 150), str(kiri_val), font=font("judul", fs_l), fill=KUNING + (255,), anchor="mm")
        d.rectangle([240, 60, 412, 92], fill=HIJAU + (255,))
        d.text((326, 76), str(kanan_lbl), font=font("teks", 18), fill=PUTIH + (255,), anchor="mm")
        d.text((326, 150), str(kanan_val), font=font("judul", fs_r), fill=KUNING + (255,), anchor="mm")
    else:
        d.text((220, 86), str(kiri_lbl), font=font("teks", 24), fill=BIRU_MUDA + (255,), anchor="mm")
        d.text((220, 152), str(kiri_val), font=font("judul", 58), fill=KUNING + (255,), anchor="mm")
    return im


@functools.lru_cache(maxsize=64)
def _tex_buku_terbuka(kiri_judul, kanan_judul, kanan_isi):
    im = Image.new("RGBA", (320, 200), KRIM + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 316, 196], outline=COKLAT_TUA + (255,), width=6)
    d.line([160, 6, 160, 194], fill=COKLAT + (255,), width=4)
    d.text((82, 28), str(kiri_judul), font=font("judul", 18), fill=HITAM + (255,), anchor="mm")
    d.ellipse([54, 54, 110, 102], fill=(242, 206, 174, 255), outline=OUT + (255,), width=3)
    d.ellipse([50, 102, 114, 156], fill=BIRU + (255,), outline=OUT + (255,), width=3)
    d.text((238, 28), str(kanan_judul), font=font("judul", 18), fill=HITAM + (255,), anchor="mm")
    for idx, line in enumerate(str(kanan_isi).split("|")[:3]):
        col = MERAH if idx == 2 else HITAM
        d.text((238, 74 + idx * 36), line.strip(), font=font("judul", 18), fill=col + (255,), anchor="mm")
    return im


@functools.lru_cache(maxsize=64)
def _tex_label_teks(teks, bg=PUTIH, fg=HITAM, border=OUT):
    im = Image.new("RGBA", (280, 100), bg + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 276, 96], outline=border + (255,), width=5)
    d.text((140, 50), str(teks), font=font("judul", 34), fill=fg + (255,), anchor="mm")
    return im


# ------------------------------------------------------------------ helper quad papan
def _wall_quad(cx, cy, cz, w, h, rot_y=0.0):
    hw, hh = w * 0.5, h * 0.5
    local = np.array([[-hw, -hh, 0.0], [+hw, -hh, 0.0], [+hw, +hh, 0.0], [-hw, +hh, 0.0]], dtype=np.float32)
    if rot_y:
        local = local @ euler_mat(0.0, rot_y, 0.0).T
    return local + np.array([cx, cy, cz], dtype=np.float32)


def draw_kalender(sc, pos, bulan="JANUARI", tahun="2008", sub="SELAMAT PAGI", w=0.72, h=0.88, rot_y=0.0):
    x, y, z = pos
    sc.box((x, y, z), (w + 0.06, h + 0.06, 0.04), COKLAT_TUA, rot=(0, rot_y, 0), outline=True, outline_w=0.008)
    m = euler_mat(0, rot_y, 0)
    off = m @ np.array([0.0, 0.0, 0.028], dtype=np.float32)
    sc.textured_quad(_wall_quad(x + off[0], y + off[1], z + off[2], w, h, rot_y), _tex_kalender(bulan, tahun, sub))


def draw_poster(sc, pos, judul="TERBANG PERDANA", tanggal="10 AGUSTUS", sub="1995", w=0.82, h=1.02, rot_y=0.0):
    x, y, z = pos
    sc.box((x, y, z), (w + 0.05, h + 0.05, 0.04), COKLAT_TUA, rot=(0, rot_y, 0), outline=True, outline_w=0.008)
    off = euler_mat(0, rot_y, 0) @ np.array([0.0, 0.0, 0.026], dtype=np.float32)
    sc.textured_quad(_wall_quad(x + off[0], y + off[1], z + off[2], w, h, rot_y), _tex_poster_pesawat(judul, tanggal, sub))


def draw_peta(sc, pos, judul="INDONESIA", w=1.45, h=0.84, rot_y=0.0):
    x, y, z = pos
    sc.box((x, y, z), (w + 0.06, h + 0.06, 0.04), COKLAT_TUA, rot=(0, rot_y, 0), outline=True, outline_w=0.008)
    off = euler_mat(0, rot_y, 0) @ np.array([0.0, 0.0, 0.026], dtype=np.float32)
    sc.textured_quad(_wall_quad(x + off[0], y + off[1], z + off[2], w, h, rot_y), _tex_peta_indonesia(judul))


def draw_papan_tulis(sc, pos, judul="CATATAN PENTING", baris1="F = m · a", baris2="", w=2.2, h=1.25, rot_y=0.0):
    x, y, z = pos
    sc.box((x, y, z), (w + 0.08, h + 0.08, 0.05), KAYU_TUA, rot=(0, rot_y, 0), outline=True, outline_w=0.01)
    off = euler_mat(0, rot_y, 0) @ np.array([0.0, 0.0, 0.032], dtype=np.float32)
    sc.textured_quad(_wall_quad(x + off[0], y + off[1], z + off[2], w, h, rot_y), _tex_papan(judul, baris1, baris2))


def draw_layar_led(sc, pos, judul="BERITA HARI INI", kiri_lbl="KURS", kiri_val="RP2.500", kanan_lbl="", kanan_val="", w=1.6, h=0.82, rot_y=0.0):
    x, y, z = pos
    sc.box((x, y, z), (w + 0.08, h + 0.08, 0.08), (38, 42, 52), rot=(0, rot_y, 0), outline=True, outline_w=0.01)
    off = euler_mat(0, rot_y, 0) @ np.array([0.0, 0.0, 0.046], dtype=np.float32)
    sc.textured_quad(_wall_quad(x + off[0], y + off[1], z + off[2], w, h, rot_y),
                     _tex_layar_led(judul, kiri_lbl, kiri_val, kanan_lbl, kanan_val), emissive=0.75)


def draw_open_book(sc, pos, s=1.0, kiri="PRESIDEN KE-3", kanan="MASA JABATAN", isi="21 MEI 1998|sampai|20 OKT 1999"):
    x, y, z = pos
    sc.box((x, y, z), (0.62 * s, 0.38 * s, 0.03 * s), COKLAT_TUA, rot=(-16, 0, 0), outline=True, outline_w=0.008 * s)
    pts = _wall_quad(0.0, 0.0, 0.02 * s, 0.58 * s, 0.35 * s, 0.0) @ euler_mat(-16, 0, 0).T + np.array([x, y, z], dtype=np.float32)
    sc.textured_quad(pts, _tex_buku_terbuka(kiri, kanan, isi))


def draw_airplane_mini(sc, pos, s=1.0, rot_y=0.0):
    x, y, z = pos
    m = euler_mat(0, rot_y, 0)
    def p(dx, dy, dz):
        return (x + float((m @ np.array([dx, dy, dz]))[0]) * s,
                y + float((m @ np.array([dx, dy, dz]))[1]) * s,
                z + float((m @ np.array([dx, dy, dz]))[2]) * s)
    # Badan pesawat
    sc.capsule(p(0, 0, 0), 0.075 * s, 0.72 * s, PUTIH, seg_u=12, seg_cap=4,
               mat=m @ euler_mat(90, 0, 0), outline=True, outline_w=0.010 * s)
    # Sayap utama & ekor
    sc.box(p(0, 0.03 * s, 0.02 * s), (0.95 * s, 0.025 * s, 0.18 * s), PUTIH, mat=m, outline=True, outline_w=0.008 * s)
    sc.box(p(0, 0.14 * s, -0.32 * s), (0.03 * s, 0.22 * s, 0.12 * s), MERAH, mat=m, outline=True, outline_w=0.008 * s)
    sc.box(p(0, 0.23 * s, -0.32 * s), (0.34 * s, 0.022 * s, 0.09 * s), PUTIH, mat=m, outline=True, outline_w=0.007 * s)
    # Baling-baling
    for sx in (-0.22, +0.22):
        sc.cylinder(p(sx * s, 0.01 * s, 0.12 * s), 0.026 * s, 0.12 * s, MERAH, mat=m @ euler_mat(90, 0, 0), outline=True, outline_w=0.006 * s)
        sc.box(p(sx * s, 0.01 * s, 0.19 * s), (0.14 * s, 0.018 * s, 0.014 * s), HITAM, mat=m)
        sc.box(p(sx * s, 0.01 * s, 0.19 * s), (0.018 * s, 0.14 * s, 0.014 * s), HITAM, mat=m)


def draw_mug(sc, pos, s=1.0, col=BIRU):
    x, y, z = pos
    sc.cylinder((x, y + 0.05 * s, z), 0.048 * s, 0.10 * s, col, seg_u=12, outline=True, outline_w=0.008 * s)


def draw_flag_id(sc, pos, h=2.1, s=1.0):
    x, y, z = pos
    sc.drop_shadow(x, y, z, 0.16 * s, 0.16 * s, 0.22)
    sc.cylinder((x, y + 0.04 * s, z), 0.14 * s, 0.08 * s, (186, 148, 54), outline=True, outline_w=0.008 * s)
    sc.cylinder((x, y + h * 0.5 * s, z), 0.022 * s, h * s, (214, 174, 72), outline=True, outline_w=0.007 * s)
    sc.sphere((x, y + h * s + 0.03 * s, z), 0.04 * s, KUNING, outline=True, outline_w=0.007 * s)
    sc.box((x + 0.42 * s, y + (h - 0.16) * s, z), (0.80 * s, 0.26 * s, 0.025 * s), MERAH, outline=True, outline_w=0.007 * s)
    sc.box((x + 0.42 * s, y + (h - 0.42) * s, z), (0.80 * s, 0.26 * s, 0.025 * s), PUTIH, outline=True, outline_w=0.007 * s)


def draw_podium(sc, pos, s=1.0):
    x, y, z = pos
    sc.drop_shadow(x, y, z, 0.42 * s, 0.34 * s, 0.28)
    sc.box((x, y + 0.52 * s, z), (0.76 * s, 1.04 * s, 0.52 * s), COKLAT_TUA, outline=True, outline_w=0.012 * s)
    sc.box((x, y + 1.07 * s, z), (0.86 * s, 0.08 * s, 0.60 * s), COKLAT, outline=True, outline_w=0.011 * s)
    sc.sphere((x, y + 0.62 * s, z + 0.27 * s), (0.14 * s, 0.14 * s, 0.04 * s), KUNING, outline=True, outline_w=0.007 * s)
    for mx in (-0.18, +0.18):
        sc.limb((x + mx * s, y + 1.11 * s, z + 0.16 * s), (x + mx * s * 0.7, y + 1.28 * s, z + 0.04 * s), 0.012 * s, HITAM, outline=False)


def draw_karung(sc, pos, label="BERAS", s=1.0):
    x, y, z = pos
    sc.drop_shadow(x, y, z, 0.26 * s, 0.24 * s, 0.24)
    sc.capsule((x, y + 0.28 * s, z), 0.24 * s, 0.56 * s, KRIM, seg_u=14, seg_cap=4, outline=True, outline_w=0.012 * s)
    sc.cylinder((x, y + 0.55 * s, z), 0.18 * s, 0.06 * s, PUTIH, outline=True, outline_w=0.009 * s)
    sc.textured_quad(_wall_quad(x, y + 0.24 * s, z + 0.25 * s, 0.34 * s, 0.14 * s),
                     _tex_label_teks(label, bg=KRIM, fg=MERAH, border=KRIM))


def draw_desk(sc, pos, w=1.45, d=0.72, h=0.76, top_col=KAYU, leg_col=COKLAT_TUA):
    x, y, z = pos
    sc.drop_shadow(x, y, z, w * 0.48, d * 0.46, 0.24)
    sc.box((x, y + h, z), (w, 0.06, d), top_col, outline=True, outline_w=0.01)
    for lx in (-w * 0.44, w * 0.44):
        for lz in (-d * 0.40, d * 0.40):
            sc.box((x + lx, y + h * 0.48, z + lz), (0.06, h * 0.96, 0.06), leg_col, outline=True, outline_w=0.008)


def draw_chair(sc, pos, col=COKLAT_TUA, rot_y=0.0):
    x, y, z = pos
    m = euler_mat(0, rot_y, 0)
    def wp(dx, dy, dz):
        return tuple(np.array([x, y, z], np.float32) + m @ np.array([dx, dy, dz], np.float32))
    sc.box(wp(0, 0.44, 0), (0.46, 0.06, 0.46), col, mat=m, outline=True, outline_w=0.008)
    sc.box(wp(0, 0.76, -0.20), (0.46, 0.60, 0.06), col, mat=m, outline=True, outline_w=0.008)
    for lx in (-0.19, 0.19):
        for lz in (-0.19, 0.19):
            sc.box(wp(lx, 0.22, lz), (0.05, 0.44, 0.05), col, mat=m)


def draw_prop(sc, spec, t=0.0):
    jenis = spec.get("jenis", "buku")
    pos = tuple(float(v) for v in spec.get("pos", [spec.get("x", 0.0), spec.get("y", 0.0), spec.get("z", 0.0)]))
    s = float(spec.get("skala", 1.0))
    ry = float(spec.get("rot_y", 0.0))
    if draw_engineering_3d(sc, jenis, pos=pos, s=s, rot_y=ry, t=t, spec=spec):
        return
    if jenis == "kalender":
        draw_kalender(sc, pos, spec.get("bulan", "JANUARI"), spec.get("tahun", "2008"), spec.get("sub", ""), 0.72 * s, 0.88 * s, ry)
    elif jenis == "poster":
        draw_poster(sc, pos, spec.get("judul", "TERBANG PERDANA"), spec.get("tanggal", "10 AGUSTUS"), spec.get("sub", "1995"), 0.82 * s, 1.02 * s, ry)
    elif jenis == "peta":
        draw_peta(sc, pos, spec.get("judul", "INDONESIA"), 1.45 * s, 0.84 * s, ry)
    elif jenis == "papan_tulis":
        draw_papan_tulis(sc, pos, spec.get("judul", "CATATAN"), spec.get("baris1", ""), spec.get("baris2", ""), 2.2 * s, 1.25 * s, ry)
    elif jenis == "layar_led":
        draw_layar_led(sc, pos, spec.get("judul", "DATA"), spec.get("kiri_lbl", ""), spec.get("kiri_val", ""),
                       spec.get("kanan_lbl", ""), spec.get("kanan_val", ""), 1.6 * s, 0.82 * s, ry)
    elif jenis == "pesawat":
        draw_airplane_mini(sc, pos, s * 1.4, ry)
    elif jenis == "karung":
        draw_karung(sc, pos, spec.get("teks", "BERAS"), s)
    elif jenis == "bendera":
        draw_flag_id(sc, pos, s=s)
    elif jenis == "podium":
        draw_podium(sc, pos, s=s)
    elif jenis == "buku":
        draw_open_book(sc, pos, s=s, kiri=spec.get("kiri", "BAB 1"), kanan=spec.get("kanan", "FAKTA"), isi=spec.get("isi", ""))
    elif jenis == "laptop":
        sc.box(pos, (0.44 * s, 0.03 * s, 0.30 * s), ABU_TUA, rot=(0, ry, 0), outline=True, outline_w=0.008 * s)
        sc.box((pos[0], pos[1] + 0.14 * s, pos[2] - 0.13 * s), (0.44 * s, 0.28 * s, 0.025 * s), HITAM, rot=(-18, ry, 0), outline=True, outline_w=0.008 * s)
    elif jenis == "kopi":
        draw_mug(sc, pos, s=s)


# ------------------------------------------------------------------ ikon emosi 3D di atas kepala
def draw_icon_3d(sc, kind, pos, t=0.0, s=1.0):
    x, y, z = pos
    bob = math.sin(t * 7.0) * 0.04 * s
    yc = y + bob
    if kind in ("ide", "lampu"):
        sc.add_light((x, yc, z + 0.1), color=(255, 224, 96), intensity=1.1, radius=2.2, halo=0.22)
        sc.sphere((x, yc, z), 0.13 * s, KUNING, emissive=0.85, outline=True, outline_w=0.012 * s)
        sc.cylinder((x, yc - 0.14 * s, z), 0.06 * s, 0.08 * s, ABU_TUA, outline=True, outline_w=0.008 * s)
    elif kind == "tanda_tanya":
        sc.rbox((x, yc + 0.06 * s, z), (0.14 * s, 0.22 * s, 0.06 * s), KUNING, emissive=0.4, outline=True, outline_w=0.01 * s)
        sc.sphere((x, yc - 0.11 * s, z), 0.045 * s, KUNING, emissive=0.4, outline=True, outline_w=0.009 * s)
    elif kind in ("seru", "kaget"):
        sc.capsule((x, yc + 0.06 * s, z), 0.05 * s, 0.22 * s, MERAH, emissive=0.4, outline=True, outline_w=0.01 * s)
        sc.sphere((x, yc - 0.12 * s, z), 0.048 * s, MERAH, emissive=0.4, outline=True, outline_w=0.01 * s)
    elif kind == "hati":
        sc.sphere((x - 0.07 * s, yc + 0.04 * s, z), 0.085 * s, MERAH, emissive=0.35, outline=True, outline_w=0.01 * s)
        sc.sphere((x + 0.07 * s, yc + 0.04 * s, z), 0.085 * s, MERAH, emissive=0.35, outline=True, outline_w=0.01 * s)
        sc.box((x, yc - 0.02 * s, z), (0.15 * s, 0.15 * s, 0.08 * s), MERAH, rot=(0, 0, 45), emissive=0.35, outline=True, outline_w=0.009 * s)
    elif kind in ("bintang", "kilau"):
        sc.box((x, yc, z), (0.18 * s, 0.18 * s, 0.06 * s), KUNING, rot=(0, t * 80.0, 45), emissive=0.75, outline=True, outline_w=0.01 * s)
        sc.box((x, yc, z), (0.18 * s, 0.18 * s, 0.06 * s), KUNING, rot=(0, t * 80.0, 0), emissive=0.75, outline=True, outline_w=0.01 * s)
    elif kind == "marah":
        sc.box((x, yc, z), (0.22 * s, 0.05 * s, 0.05 * s), MERAH, rot=(0, 0, 45), emissive=0.45, outline=True, outline_w=0.008 * s)
        sc.box((x, yc, z), (0.22 * s, 0.05 * s, 0.05 * s), MERAH, rot=(0, 0, -45), emissive=0.45, outline=True, outline_w=0.008 * s)
    elif kind == "zzz":
        for i in range(3):
            yy = yc + (i * 0.14 + (t * 0.4) % 0.12) * s
            xx = x + (i - 1) * 0.10 * s
            sc.box((xx, yy, z), (0.09 * s, 0.09 * s, 0.04 * s), BIRU_MUDA, emissive=0.5, outline=True, outline_w=0.007 * s)
    elif kind in ("uang", "koin"):
        sc.cylinder((x, yc, z), 0.14 * s, 0.04 * s, KUNING, rot=(90, t * 90.0, 0), emissive=0.4, outline=True, outline_w=0.01 * s)
