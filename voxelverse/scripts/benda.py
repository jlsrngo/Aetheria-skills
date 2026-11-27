# -*- coding: utf-8 -*-
"""
benda.py - properti 3D Voxel (monitor kode, keyboard, tram, lampu, mug, gadget)
           serta ikon emosi komik 3D (bohlam, tanda seru, hati, zzz, ...).
"""
import math, os, sys
from PIL import Image, ImageDraw
from voxel import (
    OUT, PUTIH, KRIM, HITAM, MERAH, MERAH_TUA, BIRU, BIRU_TUA, BIRU_MUDA, TEAL,
    PINK, KUNING, ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA, UNGU, UNGU_TUA, NAVY, ABU, ABU_TUA,
    clamp, euler_mat, font,
)
import numpy as np

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from aset_global import draw_engineering_3d  # noqa: E402


def _code_texture(progress=1.0, spark=False, build_mode=False):
    """Buat gambar layar editor/terminal beresolusi 320x200 untuk ditempel ke monitor 3D."""
    W, H = 320, 200
    im = Image.new("RGBA", (W, H), (14, 22, 32, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 24], fill=(22, 34, 46, 255))
    d.rectangle([10, 0, 22, 6], fill=(244, 152, 54, 255))
    f_tab = font("kode", 11)
    f_ln = font("kode", 11 if build_mode else 12)
    if build_mode:
        d.text((16, 6), "small_world.ts", font=f_tab, fill=(170, 205, 220, 255))
        d.line([(166, 24), (166, H)], fill=(38, 54, 70, 255), width=2)
        left_lines = [
            ('import { World }', (130, 195, 255)),
            ('city = new World()', (255, 208, 110)),
            ('city.build(lamps)', (136, 224, 168)),
            ('city.wire(poles)', (136, 224, 168)),
            ('spark.from(cursor)', (255, 172, 112)),
        ]
        for i, (txt, col) in enumerate(left_lines):
            y = 38 + i * 24
            d.text((10, y), txt, font=f_ln, fill=col + (255,))
        right_lines = [
            ("$ run small_world", (190, 220, 235)),
            ("✓ built", (110, 224, 155)),
            ("0 errors · 60 fps", (160, 190, 210)),
        ]
        for i, (txt, col) in enumerate(right_lines):
            y = 38 + i * 26
            d.text((176, y), txt, font=f_ln, fill=col + (255,))
        cur_x, cur_y = 180, 122
        if spark:
            d.ellipse([cur_x - 16, cur_y - 16, cur_x + 24, cur_y + 24], fill=(255, 226, 130, 225))
            d.ellipse([cur_x - 7, cur_y - 7, cur_x + 15, cur_y + 15], fill=(255, 255, 240, 255))
        else:
            d.rectangle([cur_x, cur_y, cur_x + 8, cur_y + 15], fill=(255, 198, 86, 255))
        return im

    d.text((16, 6), "small_world.ts", font=f_tab, fill=(170, 205, 220, 255))
    lines = [
        ('import { World } from "./tiny";', (130, 195, 255)),
        ('', (200, 200, 200)),
        ('const city = new World({ rain: 0.4 });', (255, 208, 110)),
        ('city.build(streets, lamps, tram);', (136, 224, 168)),
        ('city.wire(poles, windows);', (136, 224, 168)),
        ('', (200, 200, 200)),
        ('spark.from(cursor).run(city)', (255, 172, 112)),
    ]
    total_chars = sum(len(s) for s, _ in lines)
    shown = int(total_chars * clamp(progress, 0.08, 1.0))
    cur_x, cur_y = 28, 42
    used = 0
    for i, (txt, col) in enumerate(lines):
        y = 36 + i * 21
        d.text((10, y), str(i + 1), font=f_ln, fill=(70, 92, 112, 255))
        if used < shown and txt:
            take = min(len(txt), shown - used)
            sub = txt[:take]
            d.text((28, y), sub, font=f_ln, fill=col + (255,))
            cur_x = 28 + int(d.textlength(sub, font=f_ln)) + 3
            cur_y = y
        used += len(txt)
    if spark:
        d.ellipse([cur_x - 14, cur_y - 10, cur_x + 18, cur_y + 22], fill=(255, 230, 145, 230))
        d.ellipse([cur_x - 6, cur_y - 2, cur_x + 10, cur_y + 14], fill=(255, 255, 240, 255))
    else:
        d.rectangle([cur_x, cur_y + 1, cur_x + 7, cur_y + 15], fill=(255, 198, 86, 255))
    return im
    return im


def _clock_texture(jam="07:00"):
    im = Image.new("RGBA", (160, 72), (24, 24, 32, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, 156, 68], outline=(60, 64, 82, 255), width=3)
    d.text((80, 36), str(jam), font=font("seru", 34), fill=(255, 96, 84, 255), anchor="mm")
    return im


def _world_quad(pos, mat, local_pts):
    o = np.array(pos, dtype=np.float32)
    return [tuple((o + mat @ np.array(p, dtype=np.float32)).tolist()) for p in local_pts]


def _box_local(sc, pos, mat, lc, sz, col, **kw):
    c = np.array(pos, dtype=np.float32) + mat @ np.array(lc, dtype=np.float32)
    sc.box(c, sz, col, mat=mat, **kw)


def draw_prop(sc, jenis, pos, rot=(0.0, 0.0, 0.0), s=1.0, t=0.0, **opsi):
    mat = euler_mat(*rot)
    if jenis == "monitor_kode":
        # Monitor lebar modern + sticky note oranye di sudut kiri atas
        _box_local(sc, pos, mat, (0.0, 0.02 * s, 0.0), (0.34 * s, 0.03 * s, 0.24 * s), (42, 46, 56))
        _box_local(sc, pos, mat, (0.0, 0.16 * s, -0.05 * s), (0.08 * s, 0.24 * s, 0.06 * s), (36, 40, 50))
        _box_local(sc, pos, mat, (0.0, 0.36 * s, 0.0), (0.86 * s, 0.54 * s, 0.06 * s), (26, 30, 38), specular=0.45, cast_refl=True)
        # Sticky note kecil
        _box_local(sc, pos, mat, (-0.36 * s, 0.61 * s, 0.02 * s), (0.10 * s, 0.08 * s, 0.015 * s), (238, 152, 54), emissive=0.2)
        _box_local(sc, pos, mat, (0.38 * s, 0.14 * s, 0.032 * s), (0.08 * s, 0.08 * s, 0.012 * s), (240, 218, 112), emissive=0.2)
        # Layar kode
        prog_v = opsi.get("progres", clamp(0.35 + (t % 6.0) / 5.5, 0.35, 1.0))
        tex = _code_texture(prog_v, spark=bool(opsi.get("spark", False)), build_mode=bool(opsi.get("build", False)))
        pts = _world_quad(pos, mat, [
            (-0.40 * s, 0.60 * s, 0.033 * s),
            (0.40 * s, 0.60 * s, 0.033 * s),
            (0.40 * s, 0.12 * s, 0.033 * s),
            (-0.40 * s, 0.12 * s, 0.033 * s),
        ])
        sc.textured_quad(pts, tex, emissive=1.0, bias=-0.03)
        lpos = np.array(pos, dtype=np.float32) + mat @ np.array([0.0, 0.36 * s, 0.42 * s], dtype=np.float32)
        sc.add_light(lpos, color=(120, 196, 235), intensity=1.15 * s, radius=2.2, halo=0.12 if opsi.get("spark") else 0.0)

    elif jenis == "keyboard":
        _box_local(sc, pos, mat, (0.0, 0.015 * s, 0.0), (0.44 * s, 0.03 * s, 0.16 * s), (62, 68, 78))
        for r in range(3):
            for c in range(7):
                kx = (-0.165 + c * 0.055) * s
                kz = (-0.045 + r * 0.045) * s
                _box_local(sc, pos, mat, (kx, 0.036 * s, kz), (0.042 * s, 0.018 * s, 0.032 * s), (218, 222, 230), bias=-0.02)

    elif jenis == "mug_kopi":
        _box_local(sc, pos, mat, (0.0, 0.065 * s, 0.0), (0.11 * s, 0.13 * s, 0.11 * s), (244, 240, 232))
        _box_local(sc, pos, mat, (0.0, 0.125 * s, 0.0), (0.085 * s, 0.012 * s, 0.085 * s), (68, 42, 28), bias=-0.01)
        _box_local(sc, pos, mat, (0.07 * s, 0.065 * s, 0.0), (0.04 * s, 0.08 * s, 0.03 * s), (232, 228, 220))
        # Uap kopi melayang
        for i in range(2):
            yy = ((t * 0.25 + i * 0.5) % 1.0) * 0.16 * s
            _box_local(sc, pos, mat, ((i - 0.5) * 0.03 * s, 0.16 * s + yy, 0.0), (0.026 * s, 0.026 * s, 0.026 * s), PUTIH, alpha=0.45)

    elif jenis == "kursi_kerja":
        col = opsi.get("warna", TEAL)
        _box_local(sc, pos, mat, (0.0, 0.03 * s, 0.0), (0.44 * s, 0.05 * s, 0.44 * s), (44, 48, 56))
        _box_local(sc, pos, mat, (0.0, 0.22 * s, 0.0), (0.08 * s, 0.36 * s, 0.08 * s), (44, 48, 56))
        sc.rbox(np.array(pos, np.float32) + mat @ np.array((0.0, 0.44 * s, 0.0), np.float32), (0.52 * s, 0.12 * s, 0.50 * s), col, roundness=0.45, seg=1, mat=mat, cast_refl=True)
        sc.rbox(np.array(pos, np.float32) + mat @ np.array((0.0, 0.80 * s, -0.20 * s), np.float32), (0.50 * s, 0.66 * s, 0.12 * s), col, roundness=0.42, seg=1, mat=mat, cast_refl=True)

    elif jenis == "lampu_gantung":
        col = opsi.get("cahaya", (255, 206, 128))
        _box_local(sc, pos, mat, (0.0, 0.28 * s, 0.0), (0.03 * s, 0.56 * s, 0.03 * s), (36, 36, 44))
        _box_local(sc, pos, mat, (0.0, 0.0, 0.0), (0.34 * s, 0.16 * s, 0.34 * s), (222, 146, 86), emissive=0.45)
        _box_local(sc, pos, mat, (0.0, -0.09 * s, 0.0), (0.14 * s, 0.10 * s, 0.14 * s), col, emissive=1.5)
        sc.add_light(np.array(pos, np.float32) + np.array([0.0, -0.15 * s, 0.0]), color=col, intensity=float(opsi.get("intensitas", 2.0)), radius=4.2, halo=0.42 * s)

    elif jenis == "lampu_jalan":
        col = opsi.get("cahaya", (255, 202, 118))
        _box_local(sc, pos, mat, (0.0, 1.9 * s, 0.0), (0.12 * s, 3.8 * s, 0.12 * s), (48, 52, 62), cast_refl=True)
        _box_local(sc, pos, mat, (0.35 * s, 3.75 * s, 0.0), (0.76 * s, 0.10 * s, 0.10 * s), (48, 52, 62))
        _box_local(sc, pos, mat, (0.68 * s, 3.64 * s, 0.0), (0.28 * s, 0.14 * s, 0.24 * s), col, emissive=1.5, cast_refl=True)
        lp = np.array(pos, np.float32) + mat @ np.array([0.68 * s, 3.50 * s, 0.0], np.float32)
        sc.add_light(lp, color=col, intensity=2.1, radius=5.8, halo=0.55 * s)

    elif jenis == "tram":
        # Tram kota klasik krem-teal + jendela hangat + dua lampu depan (sangat ikonik di video referensi!)
        L, W_t, H_t = 4.6 * s, 1.56 * s, 2.25 * s
        # Roda & rangka bawah
        _box_local(sc, pos, mat, (0.0, 0.24 * s, 0.0), (W_t * 0.92, 0.42 * s, L * 0.94), (36, 40, 48), cast_refl=True)
        # Bodi bawah teal
        _box_local(sc, pos, mat, (0.0, 0.80 * s, 0.0), (W_t, 0.72 * s, L), (64, 128, 134), specular=0.35, cast_refl=True)
        # Sabuk tengah & bodi atas krem
        _box_local(sc, pos, mat, (0.0, 1.60 * s, 0.0), (W_t * 0.98, 0.90 * s, L * 0.98), (242, 232, 208), cast_refl=True)
        # Atap & pantograf
        _box_local(sc, pos, mat, (0.0, 2.12 * s, 0.0), (W_t * 0.86, 0.18 * s, L * 0.88), (112, 118, 128))
        _box_local(sc, pos, mat, (0.0, 2.42 * s, 0.0), (0.10 * s, 0.48 * s, 0.60 * s), (44, 48, 56))
        _box_local(sc, pos, mat, (0.0, 2.66 * s, 0.0), (0.90 * s, 0.05 * s, 0.08 * s), (44, 48, 56))
        # Jendela samping hangat menyala
        for kz in (-1.45, -0.50, 0.50, 1.45):
            _box_local(sc, pos, mat, (-W_t * 0.495, 1.58 * s, kz * s), (0.03 * s, 0.56 * s, 0.68 * s), (242, 194, 112), emissive=0.58, bias=-0.02, cast_refl=True)
            _box_local(sc, pos, mat, (W_t * 0.495, 1.58 * s, kz * s), (0.03 * s, 0.56 * s, 0.68 * s), (242, 194, 112), emissive=0.58, bias=-0.02, cast_refl=True)
        # Kaca depan & belakang + lampu depan menyala
        for fz in (-1, 1):
            _box_local(sc, pos, mat, (0.0, 1.58 * s, fz * L * 0.495), (W_t * 0.78, 0.54 * s, 0.04 * s), (242, 200, 122), emissive=0.55, bias=-0.02)
            for lx in (-0.48 * s, 0.48 * s):
                _box_local(sc, pos, mat, (lx, 0.72 * s, fz * L * 0.505), (0.16 * s, 0.14 * s, 0.04 * s), (255, 236, 175), emissive=1.1, bias=-0.03)
        # PointLight di ujung depan (+Z) tram
        hl = np.array(pos, np.float32) + mat @ np.array([0.0, 0.85 * s, L * 0.58], np.float32)
        sc.add_light(hl, color=(255, 224, 155), intensity=1.6, radius=5.5, halo=0.28 * s)

    elif jenis in ("jam_weker", "weker", "jam"):
        _box_local(sc, pos, mat, (0.0, 0.10 * s, 0.0), (0.34 * s, 0.20 * s, 0.14 * s), (44, 48, 58))
        pts = _world_quad(pos, mat, [
            (-0.14 * s, 0.18 * s, 0.075 * s),
            (0.14 * s, 0.18 * s, 0.075 * s),
            (0.14 * s, 0.02 * s, 0.075 * s),
            (-0.14 * s, 0.02 * s, 0.075 * s),
        ])
        sc.textured_quad(pts, _clock_texture(opsi.get("jam", "07:00")), emissive=1.1, bias=-0.03)
        sc.add_light(np.array(pos, np.float32) + mat @ np.array([0.0, 0.10 * s, 0.15 * s]), color=(255, 100, 90), intensity=0.5, radius=1.2)

    elif jenis == "laptop":
        _box_local(sc, pos, mat, (0.0, 0.015 * s, 0.05 * s), (0.38 * s, 0.03 * s, 0.26 * s), ABU_TUA)
        lmat = mat @ euler_mat(-18.0, 0.0, 0.0)
        _box_local(sc, np.array(pos) + mat @ np.array([0.0, 0.03 * s, -0.08 * s]), lmat, (0.0, 0.13 * s, 0.0), (0.38 * s, 0.25 * s, 0.025 * s), (38, 42, 52))
        _box_local(sc, np.array(pos) + mat @ np.array([0.0, 0.03 * s, -0.08 * s]), lmat, (0.0, 0.13 * s, 0.015 * s), (0.33 * s, 0.20 * s, 0.01 * s), BIRU_MUDA, emissive=0.9, bias=-0.02)

    elif jenis == "hp":
        _box_local(sc, pos, mat, (0.0, 0.0, 0.0), (0.10 * s, 0.18 * s, 0.024 * s), (30, 34, 42))
        _box_local(sc, pos, mat, (0.0, 0.0, 0.014 * s), (0.08 * s, 0.14 * s, 0.008 * s), BIRU_MUDA, emissive=0.85, bias=-0.02)

    elif jenis == "buku":
        col = opsi.get("warna", BIRU)
        _box_local(sc, pos, mat, (0.0, 0.0, 0.0), (0.20 * s, 0.26 * s, 0.06 * s), col)
        _box_local(sc, pos, mat, (0.01 * s, 0.0, 0.0), (0.17 * s, 0.24 * s, 0.064 * s), PUTIH, bias=-0.01)

    elif jenis == "stik":
        _box_local(sc, pos, mat, (0.0, 0.0, 0.0), (0.24 * s, 0.12 * s, 0.06 * s), (48, 52, 66))
        _box_local(sc, pos, mat, (0.06 * s, 0.02 * s, 0.035 * s), (0.03 * s, 0.03 * s, 0.012 * s), MERAH, bias=-0.02)
        _box_local(sc, pos, mat, (0.09 * s, 0.0, 0.035 * s), (0.03 * s, 0.03 * s, 0.012 * s), HIJAU, bias=-0.02)

    elif jenis == "bola":
        _box_local(sc, pos, mat, (0.0, 0.0, 0.0), (0.22 * s, 0.22 * s, 0.22 * s), PUTIH)
        _box_local(sc, pos, mat, (0.0, 0.0, 0.0), (0.23 * s, 0.08 * s, 0.08 * s), HITAM, bias=-0.01)

    elif jenis == "kado":
        col = opsi.get("warna", PINK)
        _box_local(sc, pos, mat, (0.0, 0.12 * s, 0.0), (0.26 * s, 0.24 * s, 0.26 * s), col)
        _box_local(sc, pos, mat, (0.0, 0.12 * s, 0.0), (0.27 * s, 0.25 * s, 0.05 * s), KUNING, bias=-0.01)
        _box_local(sc, pos, mat, (0.0, 0.12 * s, 0.0), (0.05 * s, 0.25 * s, 0.27 * s), KUNING, bias=-0.01)

    elif jenis == "payung":
        _box_local(sc, pos, mat, (0.0, 0.42 * s, 0.0), (0.04 * s, 0.84 * s, 0.04 * s), OUT)
        _box_local(sc, pos, mat, (0.0, 0.86 * s, 0.0), (0.86 * s, 0.18 * s, 0.86 * s), opsi.get("warna", MERAH))

    elif jenis == "pensil":
        _box_local(sc, pos, mat, (0.0, 0.06 * s, 0.0), (0.03 * s, 0.22 * s, 0.03 * s), KUNING)
        _box_local(sc, pos, mat, (0.0, 0.19 * s, 0.0), (0.032 * s, 0.04 * s, 0.032 * s), PINK)

    else:
        draw_engineering_3d(sc, jenis, pos=pos, s=s, rot_y=rot[1] if len(rot) > 1 else 0.0, t=t, spec=opsi)


# ------------------------------------------------------------------ ikon emosi 3D
def draw_icon_3d(sc, kind, pos, t=0.0, s=1.0):
    px, py, pz = pos
    bob = math.sin(t * 5.0) * 0.045 * s
    py += bob
    if kind == "bohlam":
        sc.box((px, py + 0.14 * s, pz), (0.22 * s, 0.24 * s, 0.22 * s), KUNING, emissive=1.4)
        sc.box((px, py - 0.02 * s, pz), (0.12 * s, 0.09 * s, 0.12 * s), ABU_TUA)
        sc.add_light((px, py + 0.14 * s, pz), color=KUNING, intensity=1.6, radius=2.4, halo=0.32 * s)
    elif kind == "tanda_seru":
        sc.box((px, py + 0.18 * s, pz), (0.09 * s, 0.26 * s, 0.09 * s), MERAH, emissive=0.7)
        sc.box((px, py - 0.02 * s, pz), (0.09 * s, 0.08 * s, 0.09 * s), MERAH, emissive=0.7)
    elif kind == "tanya":
        sc.box((px, py + 0.24 * s, pz), (0.20 * s, 0.08 * s, 0.08 * s), BIRU, emissive=0.6)
        sc.box((px + 0.06 * s, py + 0.15 * s, pz), (0.08 * s, 0.12 * s, 0.08 * s), BIRU, emissive=0.6)
        sc.box((px, py - 0.01 * s, pz), (0.08 * s, 0.08 * s, 0.08 * s), BIRU, emissive=0.6)
    elif kind == "hati":
        sc.box((px - 0.07 * s, py + 0.14 * s, pz), (0.12 * s, 0.12 * s, 0.09 * s), MERAH, emissive=0.8)
        sc.box((px + 0.07 * s, py + 0.14 * s, pz), (0.12 * s, 0.12 * s, 0.09 * s), MERAH, emissive=0.8)
        sc.box((px, py + 0.06 * s, pz), (0.16 * s, 0.14 * s, 0.09 * s), MERAH, emissive=0.8)
    elif kind in ("bintang", "kilau"):
        rot = (0.0, t * 80.0, 0.0)
        sc.box((px, py + 0.12 * s, pz), (0.22 * s, 0.09 * s, 0.09 * s), KUNING, rot=rot, emissive=1.2)
        sc.box((px, py + 0.12 * s, pz), (0.09 * s, 0.22 * s, 0.09 * s), KUNING, rot=rot, emissive=1.2)
    elif kind == "zzz":
        for i in range(3):
            u = ((t * 0.6 + i * 0.33) % 1.0)
            sc.box((px + i * 0.09 * s, py + u * 0.36 * s, pz), ((0.08 + i * 0.02) * s, 0.08 * s, 0.04 * s), BIRU_MUDA, emissive=0.6, alpha=1.0 - u * 0.6)
    elif kind == "centang":
        sc.box((px - 0.05 * s, py + 0.06 * s, pz), (0.08 * s, 0.16 * s, 0.07 * s), HIJAU, rot=(0, 0, 42), emissive=0.6)
        sc.box((px + 0.06 * s, py + 0.12 * s, pz), (0.08 * s, 0.26 * s, 0.07 * s), HIJAU, rot=(0, 0, -40), emissive=0.6)
    elif kind == "silang":
        sc.box((px, py + 0.12 * s, pz), (0.26 * s, 0.08 * s, 0.07 * s), MERAH, rot=(0, 0, 45), emissive=0.6)
        sc.box((px, py + 0.12 * s, pz), (0.26 * s, 0.08 * s, 0.07 * s), MERAH, rot=(0, 0, -45), emissive=0.6)
    elif kind == "keringat":
        sc.box((px + 0.18 * s, py + 0.05 * s, pz), (0.08 * s, 0.16 * s, 0.08 * s), BIRU_MUDA, emissive=0.4)
    elif kind == "not":
        sc.box((px, py + 0.16 * s, pz), (0.06 * s, 0.24 * s, 0.06 * s), UNGU, emissive=0.7)
        sc.box((px - 0.05 * s, py + 0.04 * s, pz), (0.12 * s, 0.09 * s, 0.06 * s), UNGU, emissive=0.7)
