# -*- coding: utf-8 -*-
"""
tokoh.py - Rig karakter 3D Stickman Cel-Shaded + Toon Ink Outline untuk 3D-stickman.

Tokoh utama wajib (`kribo`):
  * Kepala bola 3D halus bergaris tinta hitam + rambut afro hitam 3D berlapis
  * Wajah 2D ekspresif (terbungkus melengkung di depan bola kepala) + kacamata kotak bingkai tebal
  * Badan kapsul kaos teal (76,126,132) + dasi kupu-kupu hitam 3D + celana gelap
  * Lengan & kaki stickman 3D tipis bersendi (siku & lutut) + tangan bola + sneaker hitam-putih

Satuan lokal (skala 1): kaki di y=0.0, tinggi total ±1.72 m, menghadap +Z.
"""
import functools, math
import numpy as np
from PIL import Image, ImageDraw
from engine3d import (
    OUT, PUTIH, KRIM, HITAM, MERAH, MERAH_TUA, PIPI, BIRU, BIRU_TUA, BIRU_MUDA,
    TEAL, TEAL_TUA, PINK, KUNING, ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA,
    KAYU, UNGU, NAVY, ABU, ABU_TUA, KULIT, clamp, lerp, euler_mat, mix, gelap, terang,
)
import benda as BD

WARNA = {
    "putih": PUTIH, "hitam": HITAM, "merah": MERAH, "merah_tua": MERAH_TUA,
    "biru": BIRU, "biru_tua": BIRU_TUA, "biru_muda": BIRU_MUDA, "teal": TEAL,
    "pink": PINK, "kuning": KUNING, "oranye": ORANYE, "hijau": HIJAU,
    "ungu": UNGU, "coklat": COKLAT, "abu": ABU, "navy": NAVY, "krem": KRIM,
    "kulit": KULIT,
}


def warna(v, default=None):
    if v is None:
        return default
    if isinstance(v, str):
        return WARNA.get(v.lower(), default)
    return tuple(v)


# ------------------------------------------------------------------ preset pemeran
PRESET = {
    "kribo": dict(
        nama="Kribo", rambut="afro", rambut_warna=(40, 40, 50), telinga=False,
        kulit=(250, 218, 192), kacamata="kotak", kemeja=(72, 138, 144),
        dasi_kupu=True, dasi=None, lengan_pendek=True,
        bawah="celana", bawah_warna=(42, 44, 52), sepatu_sneaker=True,
    ),
    "habibie": dict(
        nama="Prof. Habibie", rambut="rapi", rambut_warna=(204, 208, 216), telinga=True,
        kulit=(248, 216, 190), kacamata="tipis", kumis=True, kumis_warna=(220, 224, 232),
        kemeja=(48, 54, 72), kemeja_dalam=PUTIH, dasi=(212, 54, 48), jas=True, peci=False,
        bawah="celana", bawah_warna=(42, 44, 54), sepatu=(48, 50, 58),
    ),
    "presiden": dict(
        nama="Presiden", rambut="rapi", rambut_warna=(192, 196, 206), telinga=True,
        kulit=(248, 216, 190), kacamata="tipis", kumis=True, kumis_warna=(210, 214, 224),
        kemeja=(44, 50, 68), kemeja_dalam=PUTIH, dasi=(212, 54, 48), jas=True, peci=True,
        bawah="celana", bawah_warna=(40, 42, 50), sepatu=(46, 48, 56),
    ),
    "bos": dict(
        nama="Bos", rambut="botak", telinga=True, outline=True,
        kulit=(252, 224, 200), kacamata="bulat",
        kemeja=(56, 60, 76), kemeja_dalam=PUTIH, dasi=(214, 52, 46), jas=True,
        bawah="celana", bawah_warna=(42, 44, 52), sepatu=(54, 56, 66),
    ),
    "nenek": dict(
        nama="Ibu Warung", rambut="sanggul", rambut_warna=(228, 230, 236), telinga=True,
        kulit=(248, 216, 190), kacamata="bulat", bulu_mata=True,
        kemeja=(152, 92, 168), bawah="rok", bawah_warna=(64, 52, 72), sepatu=(80, 62, 58),
    ),
    "raka": dict(
        nama="Raka", rambut="jambul", rambut_warna=(54, 38, 28), telinga=True,
        kulit=(248, 216, 190), kemeja=(56, 168, 128), lengan_pendek=True,
        bawah="celana", bawah_warna=(48, 56, 68), sepatu=(238, 238, 242),
    ),
    "bimo": dict(
        nama="Bimo", rambut="keriting", rambut_warna=(66, 42, 34), telinga=True,
        kulit=(244, 208, 178), kemeja=ORANYE, lengan_pendek=True,
        bawah="celana", bawah_warna=NAVY, sepatu=(236, 236, 240),
    ),
    "dimas": dict(
        nama="Dimas", rambut="rapi", rambut_warna=HITAM, telinga=True,
        kulit=(248, 216, 190), kacamata="kotak", kemeja=PUTIH, dasi=BIRU,
        bawah="celana", bawah_warna=NAVY, sepatu=(50, 52, 60),
    ),
    "sari": dict(
        nama="Sari", hijab=(244, 244, 248), hijab_tua=ABU,
        kulit=(250, 220, 194), bulu_mata=True, kemeja=(72, 168, 128),
        bawah="rok", bawah_warna=NAVY, sepatu=(68, 54, 52),
    ),
    "tika": dict(
        nama="Tika", rambut="kuncir", rambut_warna=HITAM, telinga=True,
        kulit=(250, 220, 194), bulu_mata=True, kemeja=(242, 182, 74), lengan_pendek=True,
        bawah="rok", bawah_warna=NAVY, sepatu=(236, 236, 240),
    ),
    "pejabat": dict(
        nama="Pejabat", rambut="rapi", rambut_warna=(48, 50, 58), telinga=True,
        kulit=(248, 216, 190), kemeja=(52, 56, 70), kemeja_dalam=PUTIH, dasi=BIRU_TUA, jas=True,
        bawah="celana", bawah_warna=(44, 48, 60), sepatu=(48, 50, 58),
    ),
    "mahasiswa": dict(
        nama="Mahasiswa", rambut="belah", rambut_warna=(42, 34, 30), telinga=True,
        kulit=(248, 216, 190), kemeja=(78, 168, 178), lengan_pendek=True,
        bawah="celana", bawah_warna=(46, 52, 62), sepatu=(236, 236, 240),
    ),
    "pedagang": dict(
        nama="Pedagang", rambut="koki", rambut_warna=(44, 42, 44), telinga=True,
        kulit=(248, 216, 190), kumis=True, kemeja=PUTIH, lengan_pendek=True,
        bawah="celana", bawah_warna=(42, 44, 52), sepatu=(50, 50, 58),
    ),
    "guru": dict(
        nama="Pak Guru", rambut="uban", rambut_warna=(202, 206, 214), telinga=True,
        kulit=(248, 216, 190), kacamata="kotak", kumis=True,
        kemeja=(232, 224, 204), dasi=MERAH_TUA, bawah="celana", bawah_warna=NAVY,
    ),
    "detektif": dict(
        nama="Detektif Arya", rambut="fedora", rambut_warna=(44, 42, 48), topi_warna=(68, 72, 84), telinga=True,
        kulit=(248, 216, 190), kacamata="tipis", kemeja=(176, 150, 112), kemeja_dalam=PUTIH,
        dasi=MERAH_TUA, jas=True, bawah="celana", bawah_warna=(46, 46, 52), sepatu=(46, 46, 52),
    ),
    "insinyur": dict(
        nama="Bang Teknik", rambut="helm_proyek", rambut_warna=(44, 40, 36), topi_warna=(248, 198, 48), telinga=True,
        kulit=(244, 208, 178), kumis=True, kumis_warna=(44, 38, 34),
        kemeja=(72, 80, 94), rompi=(242, 122, 34), lengan_pendek=True,
        bawah="celana", bawah_warna=(48, 58, 76), sepatu=(102, 68, 44),
    ),
    "zaki": dict(
        nama="Zaki", rambut="jabrik", rambut_warna=(44, 142, 236), telinga=True,
        kulit=(248, 218, 192), kemeja=(110, 68, 176), lengan_pendek=True,
        bawah="celana", bawah_warna=(40, 42, 50), sepatu_sneaker=True,
    ),
    "maya": dict(
        nama="Maya", rambut="bob", rambut_warna=(122, 52, 40), bando=(246, 202, 66),
        kulit=(252, 222, 198), bulu_mata=True, kemeja=(226, 94, 120), kemeja_dalam=PUTIH,
        blazer=True, bawah="rok", bawah_warna=NAVY, sepatu=(54, 46, 54),
    ),
    "dodi": dict(
        nama="Dodi", rambut="topi_terbalik", rambut_warna=(36, 34, 38), topi_warna=(216, 52, 52), telinga=True,
        kulit=(244, 208, 178), kacamata="hitam", kemeja=(54, 116, 202), kalung=True,
        lengan_pendek=True, bawah="celana", bawah_warna=(46, 54, 76), sepatu_sneaker=True,
    ),
}
PRESET["formal"] = dict(PRESET["bos"])


def casting(spec):
    if isinstance(spec, str):
        spec = {"dasar": spec}
    base = dict(PRESET.get(spec.get("dasar", "kribo"), PRESET["kribo"]))
    for k, v in spec.items():
        if k == "dasar":
            continue
        if isinstance(v, list) and len(v) == 3 and all(isinstance(i, (int, float)) for i in v):
            base[k] = tuple(int(c) for c in v)
        else:
            base[k] = v
    base.setdefault("skala", 1.0)
    return base


# ------------------------------------------------------------------ 30 ekspresi wajah
EKSPRESI = {
    "senang":   dict(eyes="oval", mouth="open", open=0.58, blush=0.55),
    "tenang":   dict(eyes="oval", mouth="smile", blush=0.35),
    "fokus":    dict(eyes="oval", mouth="flat", brow=(-2, -0.35, -0.35), blush=0.2),
    "tertawa":  dict(eyes="arc_up", mouth="grin", open=1.0, blush=0.8),
    "kaget":    dict(eyes="wide", mouth="o", brow=(5, 0.2, 0.2), blush=0.15),
    "marah":    dict(eyes="oval", mouth="gigit", brow=(-4, -1.0, -1.0), blush=0.0, vein=True),
    "mikir":    dict(eyes="half_asym", mouth="flat", brow=(2, 0.3, -0.8), blush=0.15, look=(0.35, 0.25)),
    "sedih":    dict(eyes="oval", mouth="frown", brow=(1, 0.9, 0.9), blush=0.0, tear=True),
    "malu":     dict(eyes="arc_up", mouth="wave", blush=1.0, sweat=True),
    "ngantuk":  dict(eyes="half", mouth="flat", blush=0.1),
    "menguap":  dict(eyes="arc_dn", mouth="yawn", blush=0.1),
    "tidur":    dict(eyes="arc_dn", mouth="smile", blush=0.4),
    "semangat": dict(eyes="spark", mouth="grin", open=0.85, blush=0.75),
    "panik":    dict(eyes="wide", mouth="o", brow=(5, 0.9, 0.9), blush=0.0, sweat=True),
    "bangga":   dict(eyes="half", mouth="smirk", blush=0.45, brow=(0, -0.3, -0.3)),
    "jahil":    dict(eyes="wink", mouth="smirk", blush=0.5),
    "cemberut": dict(eyes="oval", mouth="frown", blush=0.65, brow=(-2, -0.5, -0.5)),
    "cemas":    dict(eyes="oval", mouth="wave", brow=(1, 0.9, 0.9), blush=0.1, sweat=True),
    "lega":     dict(eyes="arc_dn", mouth="open", open=0.35, blush=0.5, sweat=True),
    "terpana":  dict(eyes="spark", mouth="o", brow=(5, 0.1, 0.1), blush=0.6),
    "datar":    dict(eyes="oval", mouth="flat", blush=0.05),
    "kagum":    dict(eyes="wide", mouth="open", open=0.45, brow=(4, 0.2, 0.2), blush=0.65),
    "cinta":    dict(eyes="heart", mouth="w_smile", blush=0.95),
    "pusing":   dict(eyes="dizzy", mouth="wave", brow=(2, 0.5, -0.5), blush=0.1, sweat=True),
    "licik":    dict(eyes="half", mouth="smirk", brow=(-3, -0.8, 0.5), blush=0.25, look=(0.45, 0.15)),
    "melet":    dict(eyes="wink", mouth="tongue", blush=0.7),
    "syok":     dict(eyes="tiny_pupil", mouth="o", brow=(6, 0.4, 0.4), blush=0.0, sweat=True),
    "tersipu":  dict(eyes="oval", mouth="w_smile", blush=1.0, look=(-0.3, -0.1)),
    "sinis":    dict(eyes="half", mouth="flat", brow=(-2, -0.6, 0.2), blush=0.0, look=(0.55, 0.1)),
    "menangis": dict(eyes="cry_shut", mouth="cry_open", brow=(2, 0.95, 0.95), blush=0.25, tear_stream=True),
    "meratap":  dict(eyes="flat_shut", mouth="frown", brow=(1, 0.7, 0.7), blush=0.0, tear_stream=True),
    "ngakak":   dict(eyes="cry_shut", mouth="grin", open=1.0, brow=(3, 0.3, 0.3), blush=0.6),
    "murka":    dict(eyes="glare", mouth="roar", brow=(1, 0.95, 0.95), blush=0.0, vein=True),
    "bengong":  dict(eyes="dot", mouth="flat", brow=(0, 0.0, 0.0), blush=0.0),
    "gugup":    dict(eyes="tall_dot", mouth="jagged", brow=(2, -0.5, -0.5), blush=0.0, sweat=True),
    "kewalahan": dict(eyes="cry_shut", mouth="cry_open", brow=(2, -0.8, -0.8), blush=0.0, sweat=2, tear_stream=True),
    "murung":   dict(eyes="half", mouth="frown", brow=(1, -0.5, -0.5), blush=0.0, gloom=True),
    "bosan":    dict(eyes="half", mouth="frown", brow=(-1, -0.2, -0.2), blush=0.0, look=(0.35, -0.2)),
    "pede":     dict(eyes="arc_dn", mouth="smile", brow=(1, 0.1, 0.1), blush=0.2),
}
EKSPRESI_ALIAS = {
    "senyum": "tenang", "kecewa": "sedih", "bingung": "mikir", "skeptis": "sinis",
    "ketawa": "tertawa", "heran": "kaget", "kesal": "cemberut", "takut": "panik",
    "takjub": "terpana", "serius": "fokus", "nangis": "menangis", "jatuh_cinta": "cinta",
    "mabuk": "pusing", "iseng": "melet", "euforia": "ngakak", "heboh": "ngakak",
    "menang": "ngakak", "mengamuk": "murka", "geram": "murka", "hampa": "bengong",
    "gemetar": "gugup", "stres": "kewalahan", "depresi": "murung", "down": "murung",
    "malas": "bosan", "bete": "bosan", "puas": "pede", "nangis_diam": "meratap",
    "sedih_berat": "meratap",
}


def get_expr(name):
    return EKSPRESI.get(EKSPRESI_ALIAS.get(name, name), EKSPRESI["senang"])


# ------------------------------------------------------------------ 50+ pose & siklus gerak stickman 3D
POSE = {
    "diam":             dict(l_arm=(6, 0, -20), r_arm=(6, 0, 20), l_leg=(0, 0, -9.5), r_leg=(0, 0, 9.5)),
    "semangat":         dict(l_arm=(6, 0, -24), r_arm=(-32, 0, 64), r_fore=(-84,), l_leg=(0, 0, -10.0), r_leg=(0, 0, 10.0), head=(6, -6, 8), energy=1.0),
    "santai":           dict(l_arm=(10, 0, -14), r_arm=(-16, 0, 18), r_fore=(-35,), body=(0, 6, 0)),
    "lambai":           dict(l_arm=(8, 0, -12), r_arm=(-136, 0, 32), r_fore=(-26,), wave_r=1),
    "lambai2":          dict(l_arm=(-136, 0, -32), r_arm=(-136, 0, 32), l_fore=(-26,), r_fore=(-26,), wave_r=1, wave_l=1),
    "tunjuk":           dict(l_arm=(10, 0, -12), r_arm=(-88, -14, 10), r_fore=(-6,), body=(0, -10, 0), point_r=1),
    "tunjuk_kiri":      dict(l_arm=(-88, 14, -10), r_arm=(10, 0, 12), l_fore=(-6,), body=(0, 10, 0), point_l=1),
    "tunjuk_atas":      dict(l_arm=(8, 0, -10), r_arm=(-152, 0, 16), r_fore=(-10,), head=(10, 0, 0), point_r=1),
    "ide":              dict(l_arm=(-18, 0, -18), r_arm=(-134, 10, 16), r_fore=(-45,), head=(8, -6, 4), energy=0.7),
    "pinggang":         dict(l_arm=(-16, 0, -48), r_arm=(-16, 0, 48), l_fore=(-56,), r_fore=(-56,)),
    "jempol":           dict(l_arm=(10, 0, -12), r_arm=(-82, -14, 18), r_fore=(-36,)),
    "silang":           dict(l_arm=(-48, 35, -10), r_arm=(-48, -35, 10), l_fore=(-55,), r_fore=(-55,)),
    "sorak":            dict(l_arm=(-154, 0, -26), r_arm=(-154, 0, 26), l_fore=(-16,), r_fore=(-16,), cheer=1),
    "peregangan":       dict(l_arm=(-166, 0, -18), r_arm=(-166, 0, 18), l_fore=(-10,), r_fore=(-10,), head=(8, 0, 0)),
    "garuk":            dict(l_arm=(8, 0, -10), r_arm=(-126, -18, 22), r_fore=(-85,), head=(-4, 8, -6), scratch=1),
    "mikir":            dict(l_arm=(-26, 20, -20), r_arm=(-74, -25, 12), r_fore=(-86,), head=(-6, 10, -5), scan=0.45),
    "dagu":             dict(l_arm=(-40, 24, -18), r_arm=(-76, -24, 10), r_fore=(-90,), scan=0.55),
    "kaget":            dict(l_arm=(-108, 0, -34), r_arm=(-108, 0, 34), l_fore=(-35,), r_fore=(-35,), body=(-8, 0, 0), shiver=0.45),
    "sedih":            dict(l_arm=(14, 0, -6), r_arm=(14, 0, 6), body=(12, 0, 0), head=(-16, 0, 0)),
    "marah":            dict(l_arm=(-35, 0, -24), r_arm=(-35, 0, 24), l_fore=(-45,), r_fore=(-45,), body=(8, 0, 0), tense=1.0),
    "kepal":            dict(l_arm=(-55, 0, -18), r_arm=(-55, 0, 18), l_fore=(-55,), r_fore=(-55,), tense=0.65),
    "menyerahkan":      dict(l_arm=(-68, 14, -8), r_arm=(-68, -14, 8), l_fore=(-18,), r_fore=(-18,), body=(8, 0, 0)),
    "angkat_tangan":    dict(l_arm=(8, 0, -10), r_arm=(-160, 0, 12), wave_r=0.35),
    "angkat_bahu":      dict(l_arm=(-38, 0, -42), r_arm=(-38, 0, 42), l_fore=(-62,), r_fore=(-62,), head=(0, 0, 6)),
    "tepuk":            dict(l_arm=(-65, 28, -10), r_arm=(-65, -28, 10), l_fore=(-45,), r_fore=(-45,), clap=1),
    "menguap":          dict(l_arm=(8, 0, -10), r_arm=(-96, -25, 10), r_fore=(-85,), head=(10, 0, 0)),
    "pegang_dada":      dict(l_arm=(10, 0, -10), r_arm=(-58, -32, 12), r_fore=(-75,)),
    "hormat":           dict(l_arm=(6, 0, -8), r_arm=(-122, -16, 22), r_fore=(-95,), body=(8, 0, 0)),
    "membungkuk":       dict(l_arm=(22, 0, -8), r_arm=(22, 0, 8), body=(28, 0, 0), head=(-12, 0, 0)),
    "pegang_hp":        dict(l_arm=(-50, 18, -12), r_arm=(-64, -20, 12), r_fore=(-42,)),
    "pegang_buku":      dict(l_arm=(-60, 20, -10), r_arm=(-60, -20, 10), l_fore=(-38,), r_fore=(-38,)),
    "pegang_pesawat":   dict(l_arm=(-52, 22, -10), r_arm=(-62, -18, 10), l_fore=(-36,), r_fore=(-42,)),
    "pegang_kopi":      dict(l_arm=(10, 0, -12), r_arm=(-62, -16, 12), r_fore=(-56,)),
    "pidato":           dict(l_arm=(-48, 10, -18), r_arm=(-108, -10, 22), l_fore=(-30,), r_fore=(-30,), head=(4, 0, 0), talk_g=0.9),
    # --- Siklus & pose gerak aktif (berjalan, mengendap, gesture, reaksi dramatis) ---
    "jalan":            dict(walk=1),
    "jalan_santai":     dict(walk=0.72, body=(-2, 0, 0)),
    "mengendap":        dict(sneak=1, body=(14, 0, 0), head=(-6, 0, 0)),
    "mundur":           dict(backwalk=1, l_arm=(-34, 0, -22), r_arm=(-34, 0, 22), l_fore=(-42,), r_fore=(-42,), body=(-6, 0, 0)),
    "lari":             dict(run=1),
    "bicara_aktif":     dict(l_arm=(-44, 14, -20), r_arm=(-58, -14, 22), l_fore=(-52,), r_fore=(-56,), talk_g=1.25),
    "mengamati":        dict(l_arm=(-36, 22, -18), r_arm=(-78, -24, 12), r_fore=(-92,), body=(4, -6, 0), scan=1.0),
    "gelisah":          dict(l_arm=(-24, 12, -18), r_arm=(-28, -12, 18), l_fore=(-36,), r_fore=(-42,), scan=1.1, shiver=0.35),
    "mengancam":        dict(l_arm=(-38, 0, -24), r_arm=(-92, -10, 14), l_fore=(-48,), r_fore=(-14,), body=(10, -12, 0), head=(-4, 10, 0), tense=0.95, point_r=1.0),
    "terkejut_mundur":  dict(l_arm=(-96, 14, -28), r_arm=(-96, -14, 28), l_fore=(-46,), r_fore=(-46,), body=(-12, 0, 0), head=(6, 0, 0), shiver=0.55),
    "gemetar":          dict(l_arm=(-42, 26, -12), r_arm=(-42, -26, 12), l_fore=(-72,), r_fore=(-72,), body=(10, 0, 0), head=(-10, 0, 0), shiver=1.0),
    "menoleh":          dict(l_arm=(8, 0, -16), r_arm=(-14, 0, 16), r_fore=(-24,), body=(0, 16, 0), head=(0, 28, -4), scan=0.45),
    "angguk":           dict(l_arm=(8, 0, -16), r_arm=(-24, 0, 18), r_fore=(-36,), nod=1.0),
    "geleng":           dict(l_arm=(-18, 0, -22), r_arm=(-18, 0, 22), l_fore=(-30,), r_fore=(-30,), shake=1.0),
    "duduk":            dict(sit=1, l_arm=(-24, 0, -10), r_arm=(-24, 0, 10), l_fore=(-30,), r_fore=(-30,)),
    "duduk_santai":     dict(sit=1, l_arm=(-18, 0, -18), r_arm=(-32, 0, 16), body=(-8, 0, 0)),
    "duduk_ketik":      dict(sit=1, type=1, body=(8, 0, 0), head=(-10, 0, 0)),
    "duduk_nulis":      dict(sit=1, l_arm=(-54, 15, -10), r_arm=(-64, -15, 10), l_fore=(-38,), r_fore=(-38,), body=(10, 0, 0), head=(-12, 0, 0)),
    "duduk_kopi":       dict(sit=1, l_arm=(-24, 0, -10), r_arm=(-68, -14, 10), r_fore=(-52,)),
    "duduk_sorak":      dict(sit=1, l_arm=(-154, 0, -24), r_arm=(-154, 0, 24), cheer=0.8),
    "tidur":            dict(lie=1, l_arm=(8, 0, -14), r_arm=(8, 0, 14)),
}


def state(**kw):
    st = dict(
        pose="diam", pose2=None, mix=0.0, expr="senang", hadap="depan",
        lihat=(0.0, 0.0), blink=0.0, open_amt=0.0, bawa=None, ransel=False,
        t=0.0, phase=0.0, amp=0.0, seed=0.0, gerak="aktif", bicara=False,
    )
    st.update(kw)
    return st


_POSE_FLAGS = (
    "sit", "lie", "walk", "run", "sneak", "backwalk", "type",
    "wave_r", "wave_l", "point_r", "point_l", "talk_g",
    "scan", "shiver", "tense", "cheer", "clap", "scratch",
    "nod", "shake", "energy",
)


def _interp_pose(p1, p2, m):
    out = {}
    for k in ("l_arm", "r_arm", "l_leg", "r_leg", "body", "head"):
        a, b = p1.get(k, (0.0, 0.0, 0.0)), p2.get(k, (0.0, 0.0, 0.0))
        out[k] = tuple(lerp(a[i] if i < len(a) else 0.0, b[i] if i < len(b) else 0.0, m) for i in range(3))
    for k in ("l_fore", "r_fore"):
        out[k] = lerp(p1.get(k, (0.0,))[0], p2.get(k, (0.0,))[0], m)
    for k in _POSE_FLAGS:
        out[k] = lerp(float(p1.get(k, 0.0)), float(p2.get(k, 0.0)), m)
    return out


_GERAK_MULT = {
    "kaku": 0.0,
    "tenang": 0.55,
    "aktif": 1.0,
    "ekspresif": 1.45,
}


def _pose_angles(st):
    p1 = POSE.get(st["pose"], POSE["diam"])
    p2 = POSE.get(st["pose2"], p1) if st.get("pose2") else p1
    p = _interp_pose(p1, p2, float(st.get("mix", 0.0)))
    t = float(st.get("t", 0.0))
    ph = float(st.get("phase", 0.0))
    amp = float(st.get("amp", 0.0))
    seed = float(st.get("seed", 0.0))
    g_raw = st.get("gerak", "aktif")
    g_mult = float(g_raw) if isinstance(g_raw, (int, float)) else _GERAK_MULT.get(str(g_raw).lower(), 1.0)
    ts = t + seed * 1.37
    has_prop = bool(st.get("bawa"))

    l_arm, r_arm = list(p["l_arm"]), list(p["r_arm"])
    l_leg, r_leg = list(p["l_leg"]), list(p["r_leg"])
    l_fore, r_fore = p["l_fore"], p["r_fore"]
    body, head = list(p["body"]), list(p["head"])
    hip_drop = 0.0
    l_knee, r_knee = 0.0, 0.0

    # --- 1. Siklus gerak kaki-tangan: jalan, jalan_santai, mengendap, mundur, lari ---
    loco = max(p["walk"], p["run"], p["sneak"], p["backwalk"])
    if loco > 0.05:
        is_run = p["run"] > 0.15
        is_sneak = p["sneak"] > 0.15
        is_back = p["backwalk"] > 0.15
        dir_s = -1.0 if is_back else 1.0
        r_mult = 1.48 if is_run else (0.78 if is_sneak else (0.76 if is_back else 1.0))
        stride = (0.58 + 0.42 * amp) * loco * r_mult
        s = math.sin(ph) * stride * dir_s
        c = math.cos(ph) * stride

        # Ayunan paha berlawanan + tekuk lutut per-kaki yang alami (kaki melangkah menekuk!)
        l_leg[0] += s * 34.0
        r_leg[0] -= s * 34.0
        if is_sneak:
            l_leg[0] -= 18.0 * p["sneak"]
            r_leg[0] -= 18.0 * p["sneak"]
            l_knee += (28.0 + max(0.0, math.cos(ph)) * 28.0) * p["sneak"]
            r_knee += (28.0 + max(0.0, -math.cos(ph)) * 28.0) * p["sneak"]
            hip_drop -= (0.065 + abs(math.cos(ph)) * 0.025) * p["sneak"]
        else:
            knee_amp = 54.0 if is_run else (30.0 if is_back else 38.0)
            l_knee += max(0.0, math.cos(ph) * dir_s) * knee_amp * stride
            r_knee += max(0.0, -math.cos(ph) * dir_s) * knee_amp * stride
            hip_drop -= (0.015 + abs(math.cos(ph)) * (0.042 if is_run else 0.026)) * loco

        # Kaki sedikit membuka saat melangkah agar tidak bertabrakan
        l_leg[2] = lerp(l_leg[2], -5.5, loco)
        r_leg[2] = lerp(r_leg[2], +5.5, loco)

        # Counter-twist torso & sway bahu/pinggul organik
        body[1] += -s * (10.5 if is_run else 7.5)
        body[2] += math.sin(ph) * (3.6 if is_run else 2.6) * loco
        body[0] += (10.0 * p["run"]) + (3.2 * p["walk"]) + abs(c) * 1.8 * loco
        head[1] += s * 3.8
        head[0] += math.sin(ph * 2.0) * 1.8 * loco

        # Ayunan lengan alami (tidak menimpa pose mundur defensif atau tangan pembawa properti)
        if not is_back:
            arm_amp = 42.0 if is_run else (22.0 if is_sneak else 34.0)
            l_arm[0] -= s * arm_amp
            l_arm[2] = lerp(l_arm[2], -14.0, loco)
            l_fore -= (14.0 + max(0.0, -s) * 24.0) * (1.35 if is_run else 1.0) * loco
            if not has_prop:
                r_arm[0] += s * arm_amp
                r_arm[2] = lerp(r_arm[2], +14.0, loco)
                r_fore -= (14.0 + max(0.0, s) * 24.0) * (1.35 if is_run else 1.0) * loco
        else:
            l_arm[0] += math.sin(ph) * 8.0 * loco
            r_arm[0] -= math.sin(ph) * 8.0 * loco

    # --- 2. Duduk & mengetik ---
    if p["sit"] > 0.05:
        m = p["sit"]
        l_leg[0] = lerp(l_leg[0], -86.0, m)
        r_leg[0] = lerp(r_leg[0], -86.0, m)
        l_knee = lerp(l_knee, 86.0, m)
        r_knee = lerp(r_knee, 86.0, m)
        hip_drop -= 0.05 * m

    if p["type"] > 0.05:
        m = p["type"]
        l_arm = [lerp(l_arm[0], -56.0, m), lerp(l_arm[1], 14.0, m), lerp(l_arm[2], -8.0, m)]
        r_arm = [lerp(r_arm[0], -56.0, m), lerp(r_arm[1], -14.0, m), lerp(r_arm[2], 8.0, m)]
        l_fore = lerp(l_fore, -48.0 + math.sin(t * 22.0) * 10.0, m)
        r_fore = lerp(r_fore, -48.0 + math.cos(t * 22.0) * 10.0, m)

    # --- 3. Siklus ekspresi tubuh (melambai, menunjuk, tepuk, sorak, garuk, gelisah, gemetar, angguk, geleng) ---
    if p["wave_r"] > 0.05:
        r_arm[2] += math.sin(t * 10.5) * 18.0 * p["wave_r"]
        r_fore += math.sin(t * 10.5 + 0.6) * 14.0 * p["wave_r"]
    if p["wave_l"] > 0.05:
        l_arm[2] -= math.sin(t * 10.5 + 0.4) * 18.0 * p["wave_l"]
        l_fore += math.sin(t * 10.5 + 1.0) * 14.0 * p["wave_l"]
    if p["point_r"] > 0.05 and not has_prop:
        r_arm[0] += math.sin(ts * 4.2) * 5.5 * p["point_r"]
        r_fore += math.sin(ts * 4.2 - 0.5) * 4.5 * p["point_r"]
    if p["point_l"] > 0.05:
        l_arm[0] += math.sin(ts * 4.2) * 5.5 * p["point_l"]
        l_fore += math.sin(ts * 4.2 - 0.5) * 4.5 * p["point_l"]
    if p["talk_g"] > 0.05 and loco < 0.35:
        tg = p["talk_g"] * max(0.55, g_mult)
        l_arm[0] += math.sin(ts * 3.4) * 14.0 * tg
        l_arm[2] -= abs(math.sin(ts * 2.1)) * 7.5 * tg
        l_fore += math.sin(ts * 3.4 - 0.7) * 16.0 * tg
        if not has_prop:
            r_arm[0] += math.cos(ts * 3.1 + 0.5) * 15.0 * tg
            r_arm[2] += abs(math.cos(ts * 2.3)) * 7.5 * tg
            r_fore += math.cos(ts * 3.1 - 0.3) * 16.0 * tg
        body[1] += math.sin(ts * 1.9) * 5.0 * tg
        head[0] += math.sin(ts * 4.4) * 4.0 * tg
    if p["scan"] > 0.05:
        sc_m = p["scan"]
        head[1] += math.sin(ts * 1.45) * 17.0 * sc_m
        head[2] += math.cos(ts * 1.1) * 4.5 * sc_m
        body[1] += math.sin(ts * 1.45 - 0.4) * 5.5 * sc_m
    if p["shiver"] > 0.05:
        sh = p["shiver"]
        body[2] += math.sin(t * 24.0) * 2.4 * sh
        head[2] += math.cos(t * 26.0) * 2.8 * sh
        l_arm[2] += math.sin(t * 22.0) * 3.2 * sh
        r_arm[2] -= math.sin(t * 22.0) * 3.2 * sh
    if p["tense"] > 0.05:
        tn = p["tense"]
        body[0] += math.sin(ts * 3.8) * 3.2 * tn
        l_arm[0] += math.sin(ts * 4.6) * 6.0 * tn
        if not has_prop:
            r_arm[0] += math.cos(ts * 4.6) * 6.0 * tn
        head[0] += math.sin(ts * 3.8) * 2.5 * tn
    if p["cheer"] > 0.05:
        ch = p["cheer"]
        bounce = abs(math.sin(ts * 6.2))
        hip_drop += bounce * 0.055 * ch
        l_arm[2] -= bounce * 10.0 * ch
        r_arm[2] += bounce * 10.0 * ch
        head[0] += math.sin(ts * 6.2) * 5.0 * ch
    if p["clap"] > 0.05:
        cl = abs(math.sin(t * 9.5)) * p["clap"]
        l_arm[1] += (1.0 - cl) * 16.0
        r_arm[1] -= (1.0 - cl) * 16.0
        l_fore -= cl * 10.0
        r_fore -= cl * 10.0
    if p["scratch"] > 0.05:
        r_fore += math.sin(t * 11.0) * 12.0 * p["scratch"]
        head[2] += math.sin(t * 5.5) * 3.5 * p["scratch"]
    if p["nod"] > 0.05:
        head[0] += math.sin(ts * 5.2) * 11.0 * p["nod"]
        body[0] += math.sin(ts * 5.2 - 0.3) * 3.2 * p["nod"]
    if p["shake"] > 0.05:
        head[1] += math.sin(ts * 6.8) * 16.0 * p["shake"]
        body[1] += math.sin(ts * 6.8 - 0.4) * 3.5 * p["shake"]
    if p["energy"] > 0.05:
        en = p["energy"]
        hip_drop += math.sin(ts * 4.2) * 0.015 * en
        body[2] += math.sin(ts * 2.6) * 3.2 * en

    # --- 4. Gesture bicara otomatis saat lipsync/bicara aktif ---
    open_amt = float(st.get("open_amt", 0.0))
    is_talking = bool(st.get("bicara", False)) or open_amt > 0.12
    if is_talking and p["lie"] < 0.5 and g_mult > 0.05:
        t_amp = max(0.35, min(1.0, open_amt * 1.4)) * g_mult
        head[0] += math.sin(ts * 5.8) * 3.6 * t_amp
        head[1] += math.sin(ts * 2.5) * 4.5 * t_amp
        head[2] += math.sin(ts * 3.7) * 2.6 * t_amp
        if loco < 0.25 and p["talk_g"] < 0.4:
            # Lengan kiri (dan kanan jika tidak pegang properti) ikut ber-gesture ringan
            l_arm[0] -= (6.0 + math.sin(ts * 3.6) * 10.0) * t_amp * 0.65
            l_fore -= (8.0 + math.sin(ts * 3.6 - 0.5) * 10.0) * t_amp * 0.65
            if not has_prop and p["wave_r"] < 0.2 and p["point_r"] < 0.2:
                r_arm[0] -= (5.0 + math.cos(ts * 3.2) * 9.0) * t_amp * 0.60
                r_fore -= (7.0 + math.cos(ts * 3.2 - 0.4) * 9.0) * t_amp * 0.60
            body[0] += math.sin(ts * 2.9) * 2.2 * t_amp

    # --- 5. Gerak idle organik otomatis (pernapasan + weight shift + micro-gesture anti-patung!) ---
    if p["lie"] < 0.5 and g_mult > 0.01:
        breath = math.sin(ts * 2.05)
        sway = math.sin(ts * 0.92)
        look_drift = math.sin(ts * 0.68 + 0.9)
        if loco < 0.25:
            hip_drop += breath * 0.012 * g_mult
            body[0] += breath * 1.8 * g_mult
            body[1] += sway * 4.2 * g_mult
            body[2] += sway * 2.4 * g_mult
            # Bahu & lengan sedikit bernapas dan ikut ayunan berat badan
            l_arm[2] -= (breath * 2.4 + sway * 1.5) * g_mult
            l_arm[0] += sway * 3.0 * g_mult
            l_fore -= abs(breath) * 2.8 * g_mult
            if not has_prop:
                r_arm[2] += (breath * 2.4 - sway * 1.5) * g_mult
                r_arm[0] -= sway * 3.0 * g_mult
                r_fore -= abs(breath) * 2.8 * g_mult
            if p["sit"] < 0.2:
                # Shifting berat badan tipis di lutut & paha
                l_knee += max(0.0, sway) * 4.5 * g_mult
                r_knee += max(0.0, -sway) * 4.5 * g_mult
        # Kepala selalu punya gerak hidup lembut
        head[0] += breath * 2.0 * g_mult
        head[1] += look_drift * 5.2 * g_mult
        head[2] += math.sin(ts * 1.15 + 0.5) * 2.6 * g_mult

    if p["sit"] < 0.1 and p["lie"] < 0.1 and loco < 0.1:
        if abs(l_leg[2]) < 1.0 and abs(r_leg[2]) < 1.0:
            l_leg[2] = -9.5
            r_leg[2] = +9.5

    return dict(
        l_arm=tuple(l_arm), r_arm=tuple(r_arm),
        l_leg=tuple(l_leg), r_leg=tuple(r_leg),
        l_fore=l_fore, r_fore=r_fore,
        body=tuple(body), head=tuple(head),
        hip_drop=hip_drop, knee_bend=max(l_knee, r_knee),
        l_knee=l_knee, r_knee=r_knee, lie=p["lie"],
    )


# ------------------------------------------------------------------ face 2D decal generator (512x512 super crisp)
@functools.lru_cache(maxsize=512)
def _face_decal_rgba(expr_name, open_q, blink_b, look_q, kacamata, bulu_mata, kumis, kumis_col, skin_col=(252, 224, 200), mata_sclera=False, maskulin=False):
    """Gambar ekspresi wajah + kacamata di kanvas 512x512 RGBA super mulus ala kartun chibi bold-outline."""
    S = 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ex = get_expr(expr_name)
    lx, ly = look_q[0] * 12.0, -look_q[1] * 8.0
    blush = ex.get("blush", 0.3)
    ink = (24, 22, 28)

    def rline(pts, col, w):
        d.line(pts, fill=col, width=w, joint="curve")
        r = w * 0.5
        for px0, py0 in (pts[0], pts[-1]):
            d.ellipse([px0 - r, py0 - r, px0 + r, py0 + r], fill=col)

    def arc_smooth(cx, cy, rx, ry, a0_deg, a1_deg, col, w, steps=20):
        pts = []
        for k in range(steps + 1):
            ang = math.radians(lerp(a0_deg, a1_deg, k / steps))
            pts.append((cx + math.cos(ang) * rx, cy + math.sin(ang) * ry))
        rline(pts, col, w)

    # Blush pipi halus hanya saat emosi tinggi (biar wajah default tetap bersih seperti referensi)
    if blush >= 0.72 or expr_name in ("malu", "tersipu", "cinta", "tertawa"):
        a_b = int(clamp((blush - 0.35) * 1.15, 0.15, 0.75) * 115)
        d.ellipse([54, 276, 140, 316], fill=(246, 146, 146, a_b // 2))
        d.ellipse([66, 282, 128, 310], fill=(246, 146, 146, a_b))
        d.ellipse([372, 276, 458, 316], fill=(246, 146, 146, a_b // 2))
        d.ellipse([384, 282, 446, 310], fill=(246, 146, 146, a_b))
        if expr_name in ("malu", "tersipu", "cinta"):
            for bx in (80, 102, 400, 422):
                rline([(bx, 288), (bx - 9, 306)], (238, 106, 116, 165), 5)

    # Mata (kiri x=174, kanan x=338, y=214)
    eyes = ex.get("eyes", "oval")
    if maskulin and expr_name == "mikir":
        eyes = "half"
    eye_positions = [(174, 214, 0), (338, 214, 1)]

    # Lensa kacamata super bening (hanya kilap tipis pada kotak)
    if kacamata == "kotak":
        for gx in (174, 338):
            d.rounded_rectangle([gx - 82, 134, gx + 82, 272], radius=24, fill=(255, 255, 255, 18))
            rline([(gx - 48, 156), (gx - 14, 190)], (255, 255, 255, 72), 11)

    def draw_eye(cx, cy, side):
        if blink_b or eyes == "arc_dn":
            arc_smooth(cx, cy - 6, 36, 24, 18, 162, ink + (255,), 16)
            return
        if eyes == "arc_up":
            # Mata lengkung ceria tebal mulus (^ ^) persis gaya kartun referensi
            arc_smooth(cx, cy + 16, 36, 34, 196, 344, ink + (255,), 18)
            return
        if eyes == "wink" and side == 1:
            arc_smooth(cx, cy + 14, 36, 30, 196, 344, ink + (255,), 17)
            return
        if eyes == "cry_shut":
            if side == 0:
                rline([(cx - 32, cy - 20), (cx + 24, cy), (cx - 32, cy + 20)], ink + (255,), 14)
            else:
                rline([(cx + 32, cy - 20), (cx - 24, cy), (cx + 32, cy + 20)], ink + (255,), 14)
            return
        if eyes == "flat_shut":
            rline([(cx - 36, cy + 6), (cx + 36, cy + 6)], ink + (255,), 15)
            return
        if eyes == "dizzy":
            pts = []
            for a_i in range(0, 760, 20):
                ang = math.radians(a_i)
                rr = 4.0 + (a_i / 760.0) * 34.0
                pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
            rline(pts, ink + (255,), 10)
            return
        if eyes == "heart":
            hr = 25
            d.ellipse([cx - hr - 10, cy - hr, cx + 4, cy + 6], fill=MERAH + (255,))
            d.ellipse([cx - 4, cy - hr, cx + hr + 10, cy + 6], fill=MERAH + (255,))
            d.polygon([(cx - hr - 9, cy - 4), (cx + hr + 9, cy - 4), (cx, cy + 38)], fill=MERAH + (255,))
            d.ellipse([cx - 16, cy - 15, cx - 3, cy - 3], fill=PUTIH + (235,))
            return
        if eyes == "spark":
            pts = []
            for k in range(10):
                ang = math.radians(-90 + k * 36)
                rr = 48 if k % 2 == 0 else 22
                pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
            d.polygon(pts, fill=KUNING + (255,), outline=ink + (255,), width=7)
            d.ellipse([cx - 10, cy - 12, cx + 8, cy + 6], fill=PUTIH + (245,))
            return

        if eyes in ("wide", "tiny_pupil", "dot", "tall_dot", "glare"):
            rw = 32 if eyes == "tall_dot" else (38 if eyes == "dot" else 45)
            rh = 44 if eyes == "tall_dot" else (42 if eyes == "dot" else 50)
            if eyes == "glare":
                rw, rh = 44, 42
            d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=PUTIH + (255,), outline=ink + (255,), width=9)
            px, py = cx + lx, cy + ly
            if eyes == "tall_dot":
                d.ellipse([px - 7, py - 15, px + 7, py + 15], fill=ink + (255,))
            else:
                pr = 10 if eyes in ("tiny_pupil", "dot", "glare") else 18
                d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=ink + (255,))
                if eyes == "wide":
                    d.ellipse([px - 4, py - 14, px + 10, py], fill=PUTIH + (255,))
            if eyes == "glare":
                if side == 0:
                    d.polygon([(cx - 50, cy - 52), (cx + 50, cy - 52), (cx + 50, cy - 8), (cx - 50, cy - 28)], fill=skin_col + (255,))
                    rline([(cx - 46, cy - 26), (cx + 46, cy - 8)], ink + (255,), 12)
                else:
                    d.polygon([(cx - 50, cy - 52), (cx + 50, cy - 52), (cx + 50, cy - 28), (cx - 50, cy - 8)], fill=skin_col + (255,))
                    rline([(cx - 46, cy - 8), (cx + 46, cy - 26)], ink + (255,), 12)
        elif mata_sclera:
            rw, rh = 38, 42
            d.ellipse([cx - rw, cy - rh, cx + rw, cy + rh], fill=PUTIH + (255,), outline=ink + (255,), width=8)
            pr = 24
            px, py = cx + lx * 0.8, cy + ly * 0.8
            d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=ink + (255,))
            d.ellipse([px - 12, py - 14, px - 2, py - 4], fill=PUTIH + (255,))
        else:
            # Mata chibi glossy bersih & ekspresif (bulat-oval tegas + kilap putih tajam)
            rw, rh = 30, 38
            px, py = cx + lx, cy + ly
            d.ellipse([px - rw, py - rh, px + rw, py + rh], fill=ink + (255,))
            d.ellipse([px - 17, py - 22, px - 1, py - 6], fill=PUTIH + (255,))
            d.ellipse([px + 6, py + 10, px + 14, py + 18], fill=PUTIH + (225,))

        if eyes == "half" or (eyes == "half_asym" and side == 0):
            d.chord([cx - 46, cy - 50, cx + 46, cy + 48], 180, 360, fill=skin_col + (255,))
            rline([(cx - 44, cy - 2), (cx + 44, cy - 2)], ink + (255,), 11)

        if bulu_mata:
            sx_m = -1 if side == 0 else 1
            rline([(cx + sx_m * 26, cy - 28), (cx + sx_m * 48, cy - 42)], ink + (255,), 9)
            rline([(cx + sx_m * 30, cy - 14), (cx + sx_m * 50, cy - 22)], ink + (255,), 8)

    for cx, cy, sd in eye_positions:
        draw_eye(cx, cy, sd)

    # Air mata (tetesan kecil atau aliran deras mengalir ke pipi)
    if ex.get("tear_stream"):
        for cx_t in (172, 340):
            pts_l = [(cx_t - 11, 224), (cx_t + 11, 224), (cx_t + 16, 330), (cx_t - 16, 330)]
            d.polygon(pts_l, fill=(116, 198, 248, 220))
            d.ellipse([cx_t - 16, 316, cx_t + 16, 342], fill=(116, 198, 248, 225), outline=(56, 142, 220, 230), width=4)
            d.line([(cx_t - 11, 226), (cx_t - 16, 326)], fill=(56, 142, 220, 230), width=4)
            d.line([(cx_t + 11, 226), (cx_t + 16, 326)], fill=(56, 142, 220, 230), width=4)
            d.line([(cx_t - 3, 236), (cx_t - 5, 322)], fill=(244, 252, 255, 220), width=5)
            d.ellipse([cx_t + 2, 324, cx_t + 10, 333], fill=(244, 252, 255, 220))
    elif ex.get("tear"):
        for tx in (144, 338):
            d.ellipse([tx, 256, tx + 30, 310], fill=BIRU_MUDA + (235,), outline=BIRU + (255,), width=4)
            d.ellipse([tx + 8, 266, tx + 16, 280], fill=PUTIH + (220,))

    # Bayangan suram dahi atas (untuk ekspresi murung / putus asa)
    if ex.get("gloom"):
        for gx_s in range(118, 396, 18):
            dist_c = abs(gx_s - 256) / 145.0
            h_g = int(96 * max(0.2, 1.0 - dist_c * 0.65))
            d.line([(gx_s, 36), (gx_s, 36 + h_g)], fill=(42, 48, 70, 95), width=5)

    # Alis chibi tebal melengkung rapi di atas kacamata (persis gaya kartun referensi)
    brow_spec = ex.get("brow", (0, 0, 0))
    brow_y = 98 + brow_spec[0] * 5.0
    bl_tilt = brow_spec[1] * 18.0
    br_tilt = brow_spec[2] * 18.0
    rline([(128, brow_y - bl_tilt + 9), (168, brow_y - 6), (212, brow_y + bl_tilt + 4)], ink + (255,), 18)
    rline([(300, brow_y + br_tilt + 4), (344, brow_y - 6), (384, brow_y - br_tilt + 9)], ink + (255,), 18)

    # Kacamata bersih & tajam (frame di atas mata, tangkai tipis menyambung ke arah telinga)
    fr_col = (34, 30, 36, 255)
    wire_col = (92, 82, 84, 235)
    if kacamata == "kotak":
        for gx in (174, 338):
            d.rounded_rectangle([gx - 82, 134, gx + 82, 272], radius=24, fill=None, outline=fr_col, width=16)
        rline([(252, 192), (260, 192)], fr_col, 16)
        rline([(14, 186), (92, 192)], fr_col, 11)
        rline([(420, 192), (498, 186)], fr_col, 11)
    elif kacamata == "bulat":
        for gx in (174, 338):
            d.ellipse([gx - 76, 138, gx + 76, 290], fill=None, outline=fr_col, width=10)
        rline([(250, 212), (256, 208), (262, 212)], fr_col, 9)
        rline([(4, 240), (98, 214)], wire_col, 5)
        rline([(414, 214), (508, 240)], wire_col, 5)
    elif kacamata == "tipis":
        for gx in (174, 338):
            d.ellipse([gx - 72, 142, gx + 72, 284], fill=None, outline=(46, 44, 52, 255), width=8)
        rline([(246, 210), (256, 206), (266, 210)], (46, 44, 52, 255), 8)
        rline([(6, 238), (102, 212)], wire_col, 4)
        rline([(410, 212), (506, 238)], wire_col, 4)
    elif kacamata == "hitam":
        for gx in (174, 338):
            d.rounded_rectangle([gx - 78, 138, gx + 78, 268], radius=26, fill=(24, 26, 34, 248), outline=fr_col, width=13)
            rline([(gx - 48, 160), (gx - 10, 202)], PUTIH + (195,), 10)
        rline([(248, 188), (264, 188)], fr_col, 14)
        rline([(12, 184), (96, 190)], fr_col, 11)
        rline([(416, 190), (500, 184)], fr_col, 11)

    # Kumis rapi 1 kurva mulus (melengkung lembut mengikuti bibir atas, tanpa garis belah tengah)
    if kumis:
        m_pts = [
            (184, 326), (194, 306), (218, 294), (244, 296), (256, 302),
            (268, 296), (294, 294), (318, 306), (328, 326),
            (306, 320), (282, 316), (256, 320), (230, 316), (206, 320),
        ]
        d.polygon(m_pts, fill=kumis_col + (255,))
        rline(m_pts + [m_pts[0]], ink + (255,), 6)

    # Mulut ekspresif + lipsync VO (gaya kartun chibi bold-outline dengan lidah merah coral)
    my = 362 if kumis else 338
    mtype = ex.get("mouth", "open")
    amt = max(open_q, ex.get("open", 0.0) if open_q == 0.0 else open_q)
    if mtype in ("open", "grin") or open_q > 0.12:
        mh = int(28 + 48 * clamp(amt, 0.30, 1.0))
        mw = 68 if mtype == "grin" else 56
        # Bibir atas melengkung senyum ceria + rongga dalam maroon hangat + lidah merah koral
        top_pts = []
        bot_pts = []
        for k in range(17):
            u = k / 16.0
            tx = lerp(256 - mw, 256 + mw, u)
            sag = math.sin(u * math.pi) * (10.0 if mtype == "grin" else 7.0)
            top_pts.append((tx, my - 4 + sag))
        for k in range(17):
            u = 1.0 - k / 16.0
            ang = lerp(0.0, math.pi, u)
            bx = 256 + math.cos(ang) * mw
            by = my - 4 + math.sin(ang) * (mh + 6)
            bot_pts.append((bx, by))
        mouth_poly = top_pts + bot_pts
        d.polygon(mouth_poly, fill=(84, 30, 38, 255))
        if mh >= 32:
            # Lidah merah koral di bagian bawah rongga mulut
            tw = mw * 0.68
            t_top = my + mh * 0.34
            t_pts = []
            for k in range(13):
                u = k / 12.0
                ang = lerp(math.pi, 2.0 * math.pi, u)
                t_pts.append((256 + math.cos(ang) * tw, t_top + math.sin(ang) * (mh * 0.24)))
            for k in range(13):
                u = 1.0 - k / 12.0
                ang = lerp(0.18 * math.pi, 0.82 * math.pi, u)
                t_pts.append((256 + math.cos(ang) * (mw * 0.90), my - 4 + math.sin(ang) * (mh + 3)))
            d.polygon(t_pts, fill=(228, 76, 66, 255))
            rline(t_pts[:13], (52, 20, 26, 255), 6)
        rline(mouth_poly + [mouth_poly[0]], ink + (255,), 13)
    elif mtype == "tongue":
        # Lidah menempel mulus tepat di bawah garis senyum (tidak mengambang terpisah)
        d.rounded_rectangle([226, my + 12, 286, my + 62], radius=26, fill=(238, 96, 108, 255), outline=ink + (255,), width=10)
        rline([(256, my + 24), (256, my + 48)], (168, 52, 64, 255), 6)
        arc_smooth(256, my - 6, 52, 24, 15, 165, ink + (255,), 13)
    elif mtype == "cry_open":
        d.rounded_rectangle([206, my - 16, 306, my + 50], radius=24, fill=(96, 32, 40, 255), outline=ink + (255,), width=12)
        d.pieslice([226, my + 18, 286, my + 52], 180, 360, fill=(232, 92, 92, 255))
    elif mtype == "roar":
        d.chord([194, my - 18, 318, my + 78], 180, 360, fill=(96, 30, 38, 255), outline=ink + (255,), width=12)
        d.pieslice([222, my + 12, 290, my + 50], 180, 360, fill=(232, 86, 86, 255))
        rline([(196, my + 30), (316, my + 30)], ink + (255,), 12)
    elif mtype == "jagged":
        pts_j = [(192 + k * 18, my + (-9 if k % 2 == 0 else 9)) for k in range(8)]
        rline(pts_j, ink + (255,), 12)
    elif mtype == "w_smile":
        arc_smooth(232, my + 4, 24, 18, 10, 170, ink + (255,), 13)
        arc_smooth(280, my + 4, 24, 18, 10, 170, ink + (255,), 13)
    elif mtype == "o" or mtype == "yawn":
        rr = 28 if mtype == "o" else 36
        d.ellipse([256 - rr, my - rr + 12, 256 + rr, my + rr + 12], fill=(96, 32, 40, 255), outline=ink + (255,), width=12)
    elif mtype == "smile":
        arc_smooth(256, my - 4, 52, 32, 18, 162, ink + (255,), 14)
    elif mtype == "frown":
        arc_smooth(256, my + 34, 48, 28, 198, 342, ink + (255,), 14)
    elif mtype == "smirk":
        arc_smooth(258, my - 2, 48, 26, 15, 130, ink + (255,), 14)
    elif mtype == "gigit":
        d.rounded_rectangle([188, my - 20, 324, my + 32], radius=16, fill=PUTIH + (255,), outline=ink + (255,), width=12)
        rline([(188, my + 6), (324, my + 6)], ink + (255,), 9)
    elif mtype == "wave":
        rline([(200, my + 8), (228, my - 8), (256, my + 8), (284, my - 8), (312, my + 8)], ink + (255,), 13)
    else:
        rline([(210, my + 8), (302, my + 8)], ink + (255,), 14)

    # Keringat / urat marah
    sw = ex.get("sweat")
    if sw:
        drops = [(408, 96), (68, 96), (440, 124)] if sw == 2 else [(408, 96)]
        for sx_d, sy_d in drops:
            d.ellipse([sx_d, sy_d, sx_d + 34, sy_d + 48], fill=BIRU_MUDA + (240,), outline=BIRU + (255,), width=7)
            d.ellipse([sx_d + 8, sy_d + 10, sx_d + 18, sy_d + 24], fill=PUTIH + (225,))
    if ex.get("vein"):
        rline([(396, 84), (420, 108)], MERAH + (255,), 10)
        rline([(420, 84), (396, 108)], MERAH + (255,), 10)

    return im


@functools.lru_cache(maxsize=8)
def _hijab_frame_rgba(col=(244, 244, 248)):
    """Bingkai bukaan wajah hijab: putih mulus dengan oval transparan di tengah (anti jagged)."""
    S, SS = 512, 1024
    im = Image.new("RGBA", (SS, SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # Tepi luar lembut (memudar) agar menyatu dengan tudung 3D di belakangnya
    for rad, a in ((512, 0), (510, 120), (506, 210), (500, 255)):
        d.ellipse([SS // 2 - rad, SS // 2 - rad, SS // 2 + rad, SS // 2 + rad], fill=col + (a,))
    # Potong bukaan wajah (oval, terbuka ke bawah mengikuti dagu)
    mask = im.getchannel("A")
    md = ImageDraw.Draw(mask)
    md.ellipse([112, 110, 912, 950], fill=0)
    im.putalpha(mask)
    return im.resize((S, S), Image.LANCZOS)


@functools.lru_cache(maxsize=128)
def _suit_decal_rgba(shirt_col, in_col, tie_col):
    """Gambar jas terbuka, kemeja putih penuh, kerah runcing, lapel bertakik, dan dasi tegas bergaris tinta."""
    S = 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ink = (22, 20, 26, 255)
    lap_col = terang(shirt_col, 0.04) if shirt_col != PUTIH else ABU
    sh_in = gelap(in_col, 0.08)

    # 1. Kemeja dalaman putih terbuka sampai bawah jas + bayangan cel halus di sisi kiri
    shirt_v = [(146, 0), (366, 0), (344, 510), (168, 510)]
    d.polygon(shirt_v, fill=in_col + (255,))
    d.polygon([(146, 0), (222, 0), (228, 510), (168, 510)], fill=sh_in + (255,))

    # 2. Dasi lebar & tegas dengan simpul jelas + bayangan sisi kiri
    if tie_col is not None:
        blade = [(232, 92), (280, 92), (312, 412), (256, 486), (200, 412)]
        d.polygon(blade, fill=tie_col + (255,))
        # Bayangan cel sisi kiri dasi
        d.polygon([(232, 92), (256, 92), (256, 486), (200, 412)], fill=gelap(tie_col, 0.14) + (255,))
        d.polygon(blade, fill=None, outline=ink, width=12)
        knot = [(218, 38), (294, 38), (280, 100), (232, 100)]
        d.polygon(knot, fill=gelap(tie_col, 0.08) + (255,), outline=ink, width=11)

    # 3. Kerah kemeja putih runcing mengapit simpul dasi
    col_l = [(144, 0), (256, 46), (200, 114), (138, 42)]
    col_r = [(368, 0), (256, 46), (312, 114), (374, 42)]
    d.polygon(col_l, fill=in_col + (255,), outline=ink, width=11)
    d.polygon(col_r, fill=in_col + (255,), outline=ink, width=11)

    # 4. Lipatan kerah jas bertakik (notch lapel) + tepi bukaan jas vertikal tegas
    lap_l = [(142, 0), (74, 128), (118, 156), (78, 198), (170, 510), (186, 510), (182, 232)]
    lap_r = [(370, 0), (438, 128), (394, 156), (434, 198), (342, 510), (326, 510), (330, 232)]
    d.polygon(lap_l, fill=lap_col + (255,), outline=ink, width=13)
    d.polygon(lap_r, fill=lap_col + (255,), outline=ink, width=13)

    # Garis lipatan dalam jas ke hem bawah
    d.line([(174, 230), (168, 510)], fill=ink, width=13)
    d.line([(338, 230), (344, 510)], fill=ink, width=13)

    return im


# ------------------------------------------------------------------ Kelas TokohStick3D
class TokohStick3D:
    def __init__(self, spec):
        self.p = casting(spec)

    def _xform(self, local_pt, root_pos, root_mat, s):
        return tuple(np.array(root_pos, dtype=np.float32) + (root_mat @ (np.array(local_pt, dtype=np.float32) * s)))

    def head_anchor(self, pos, s=1.0, pose="diam"):
        dy = 1.62 if POSE.get(pose, {}).get("sit", 0) == 0 else 1.38
        return (pos[0], pos[1] + dy * s, pos[2])

    def _draw_hair(self, sc, head_c, head_mat, s):
        p = self.p
        ol = bool(p.get("outline", True))
        ow = 0.019 * s
        hcol = warna(p.get("rambut_warna"), (30, 30, 38))
        tcol = warna(p.get("topi_warna"), (68, 72, 84))
        if p.get("hijab"):
            hij = warna(p["hijab"], (32, 34, 44))
            sc.sphere(head_c + head_mat @ np.array([0.0, 0.025 * s, -0.095 * s]),
                      (0.378 * s, 0.376 * s, 0.305 * s), hij, seg_u=44, seg_v=28, mat=head_mat,
                      outline=ol, outline_w=ow, specular=0.05)
            sc.sphere(head_c + head_mat @ np.array([0.0, 0.205 * s, -0.012 * s]),
                      (0.358 * s, 0.138 * s, 0.340 * s), hij, seg_u=40, seg_v=14,
                      mat=head_mat @ euler_mat(-6, 0, 0), outline=False, specular=0.05, hemi=True)
            for sx in (-1, 1):
                sc.capsule(head_c + head_mat @ np.array([sx * 0.314 * s, 0.005 * s, -0.058 * s]),
                           0.098 * s, 0.36 * s, hij, seg_u=20, seg_cap=6,
                           mat=head_mat @ euler_mat(8, 0, sx * -8), specular=0.0, bias=+0.004)
            sc.sphere(head_c + head_mat @ np.array([0.0, -0.285 * s, -0.012 * s]),
                      (0.248 * s, 0.132 * s, 0.228 * s), hij, seg_u=28, seg_v=16, mat=head_mat,
                      outline=False, specular=0.0)
            self._draw_hijab_frame(sc, head_c, head_mat, s, hij)
            return

        rm = p.get("rambut", "afro")
        if rm == "afro":
            # Afro 3D gembang halus & seragam (1 warna murni agar zero tambal-sulam di perpotongan bola,
            # segmen tinggi + specular wol lembut agar tampak halus seperti render 3D Pixar/Blender)
            puffs = [
                # Inti dalam penutup kepala (belakang, tidak menembus dahi)
                (0.00, 0.28, -0.15, 0.34),
                (-0.22, 0.16, -0.18, 0.30), (+0.22, 0.16, -0.18, 0.30),
                (0.00, 0.10, -0.30, 0.32),
                # Mahkota depan-atas (maju di atas alis agar tampak samping penuh tanpa jidat lebar)
                (0.00, 0.44, +0.18, 0.175),
                (-0.15, 0.42, +0.16, 0.170), (+0.15, 0.42, +0.16, 0.170),
                (-0.28, 0.34, +0.10, 0.170), (+0.28, 0.34, +0.10, 0.170),
                # Baris poni gembang halus (tepat di atas alis, membingkai pelipis)
                (0.00, 0.39, +0.25, 0.115),
                (-0.12, 0.38, +0.23, 0.115), (+0.12, 0.38, +0.23, 0.115),
                (-0.23, 0.32, +0.18, 0.120), (+0.23, 0.32, +0.18, 0.120),
                (-0.33, 0.18, +0.10, 0.135), (+0.33, 0.18, +0.10, 0.135),
                (-0.35, 0.02, +0.04, 0.135), (+0.35, 0.02, +0.04, 0.135),
                # Mahkota atas & lingkar gembang melingkar mulus
                (0.00, 0.54, +0.03, 0.225),
                (-0.19, 0.50, +0.02, 0.210), (+0.19, 0.50, +0.02, 0.210),
                (-0.34, 0.39, -0.04, 0.210), (+0.34, 0.39, -0.04, 0.210),
                (-0.43, 0.21, -0.08, 0.215), (+0.43, 0.21, -0.08, 0.215),
                (-0.44, 0.03, -0.10, 0.205), (+0.44, 0.03, -0.10, 0.205),
                (-0.36, -0.11, -0.12, 0.185), (+0.36, -0.11, -0.12, 0.185),
                (-0.24, 0.26, -0.25, 0.250), (+0.24, 0.26, -0.25, 0.250),
                (-0.22, -0.05, -0.26, 0.210), (+0.22, -0.05, -0.26, 0.210),
            ]
            with sc.part():
                for px, py, pz, pr in puffs:
                    c = head_c + head_mat @ (np.array([px, py, pz], dtype=np.float32) * s)
                    sc.sphere(c, pr * s, hcol, seg_u=24, seg_v=16, mat=head_mat,
                              outline=ol, outline_w=ow, specular=0.06)
        elif rm == "jambul":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.090 * s, -0.105 * s]),
                          (0.374 * s, 0.350 * s, 0.302 * s), hcol, seg_u=24, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
                sc.sphere(head_c + head_mat @ np.array([0.04 * s, 0.355 * s, 0.06 * s]),
                          (0.17 * s, 0.135 * s, 0.195 * s), hcol, seg_u=18, seg_v=12, mat=head_mat, outline=ol, outline_w=ow)
        elif rm == "keriting":
            with sc.part():
                for px, py, pz, pr in [(0, 0.30, -0.04, 0.21), (-0.22, 0.23, -0.06, 0.19), (0.22, 0.23, -0.06, 0.19),
                                       (-0.28, 0.06, -0.09, 0.17), (0.28, 0.06, -0.09, 0.17), (0, 0.12, -0.24, 0.23)]:
                    c = head_c + head_mat @ (np.array([px, py, pz], dtype=np.float32) * s)
                    sc.sphere(c, pr * s, hcol, seg_u=18, seg_v=12, mat=head_mat, outline=ol, outline_w=ow)
        elif rm == "sanggul":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.090 * s, -0.105 * s]),
                          (0.374 * s, 0.350 * s, 0.302 * s), hcol, seg_u=24, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.385 * s, -0.10 * s]),
                          0.128 * s, hcol, seg_u=18, seg_v=12, mat=head_mat, outline=ol, outline_w=ow)
        elif rm == "kuncir":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.090 * s, -0.105 * s]),
                          (0.374 * s, 0.350 * s, 0.302 * s), hcol, seg_u=24, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
                for sx in (-1, 1):
                    sc.capsule(head_c + head_mat @ np.array([sx * 0.36 * s, 0.04 * s, -0.10 * s]),
                               0.090 * s, 0.27 * s, hcol, seg_u=16, seg_cap=5, mat=head_mat, outline=ol, outline_w=ow)
        elif rm == "koki":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.090 * s, -0.105 * s]),
                          (0.372 * s, 0.348 * s, 0.300 * s), hcol, seg_u=22, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
            with sc.part():
                sc.cylinder(head_c + head_mat @ np.array([0.0, 0.385 * s, 0.0]), 0.22 * s, 0.16 * s, PUTIH, seg_u=22, mat=head_mat, outline=ol, outline_w=ow)
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.485 * s, 0.0]), (0.26 * s, 0.135 * s, 0.26 * s), PUTIH, seg_u=20, seg_v=12, mat=head_mat, outline=ol, outline_w=ow)
        elif rm == "fedora":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.088 * s, -0.105 * s]),
                          (0.372 * s, 0.348 * s, 0.300 * s), hcol, seg_u=22, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
            hat_m = head_mat @ euler_mat(-8.0, 0.0, 4.0)
            with sc.part():
                sc.cylinder(head_c + head_mat @ np.array([0.0, 0.288 * s, -0.015 * s]), 0.48 * s, 0.036 * s, tcol,
                            seg_u=26, mat=hat_m, outline=ol, outline_w=ow, specular=0.10)
                sc.cylinder(head_c + head_mat @ np.array([0.0, 0.330 * s, -0.015 * s]), 0.285 * s, 0.062 * s, (28, 30, 36),
                            seg_u=22, mat=hat_m, outline=ol, outline_w=ow)
                sc.capsule(head_c + head_mat @ np.array([0.0, 0.415 * s, -0.015 * s]), 0.255 * s, 0.26 * s, tcol,
                           seg_u=22, seg_cap=6, mat=hat_m, outline=ol, outline_w=ow, scale_xz=(0.95, 1.08), specular=0.10)
        elif rm == "helm_proyek":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.088 * s, -0.115 * s]),
                          (0.372 * s, 0.348 * s, 0.290 * s), hcol, seg_u=22, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.175 * s, -0.01 * s]),
                          (0.386 * s, 0.258 * s, 0.370 * s), tcol, seg_u=24, seg_v=12, mat=head_mat,
                          outline=ol, outline_w=ow, specular=0.22, hemi=True)
                sc.cylinder(head_c + head_mat @ np.array([0.0, 0.172 * s, -0.01 * s]), 0.388 * s, 0.032 * s, tcol,
                            seg_u=24, mat=head_mat, outline=ol, outline_w=ow, specular=0.16)
                sc.capsule(head_c + head_mat @ np.array([0.0, 0.412 * s, -0.01 * s]),
                           0.048 * s, 0.31 * s, terang(tcol, 0.14), seg_u=14, seg_cap=5,
                           mat=head_mat @ euler_mat(90, 0, 0), outline=ol, outline_w=ow, specular=0.12)
                sc.rbox(head_c + head_mat @ np.array([0.0, 0.172 * s, 0.315 * s]),
                        (0.36 * s, 0.034 * s, 0.17 * s), tcol, roundness=0.55, seg=2,
                        mat=head_mat @ euler_mat(10, 0, 0), outline=ol, outline_w=ow, specular=0.20)
        elif rm == "jabrik":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.090 * s, -0.105 * s]),
                          (0.372 * s, 0.348 * s, 0.302 * s), hcol, seg_u=24, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
                for py, pz, tilt, rad, len_s in [
                    (0.375, 0.12, 24, 0.080, 0.26),
                    (0.450, 0.00, 8,  0.088, 0.30),
                    (0.438, -0.13, -12, 0.084, 0.28),
                    (0.355, -0.24, -32, 0.076, 0.24),
                    (0.230, -0.33, -52, 0.068, 0.21),
                ]:
                    sp_c = head_c + head_mat @ np.array([0.0, py * s, pz * s], dtype=np.float32)
                    sc.capsule(sp_c, rad * s, len_s * s, hcol, seg_u=14, seg_cap=5,
                               mat=head_mat @ euler_mat(tilt, 0, 0), outline=ol, outline_w=ow, specular=0.12)
        elif rm == "bob":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.090 * s, -0.115 * s]),
                          (0.382 * s, 0.352 * s, 0.292 * s), hcol, seg_u=24, seg_v=14, mat=head_mat,
                          outline=ol, outline_w=ow, specular=0.08)
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.215 * s, -0.010 * s]),
                          (0.366 * s, 0.195 * s, 0.346 * s), hcol, seg_u=24, seg_v=12, mat=head_mat,
                          outline=ol, outline_w=ow, specular=0.08)
                for sx in (-1, 1):
                    sc.capsule(head_c + head_mat @ np.array([sx * 0.316 * s, -0.055 * s, -0.04 * s]),
                               0.112 * s, 0.37 * s, hcol, seg_u=16, seg_cap=5,
                               mat=head_mat @ euler_mat(0, 0, sx * -10), outline=ol, outline_w=ow, specular=0.08)
            if p.get("bando"):
                bcol = warna(p["bando"], KUNING)
                with sc.part():
                    for ang_z in (-54, -36, -18, 0, 18, 36, 54):
                        bm = head_mat @ euler_mat(18, 0, ang_z)
                        bp = head_c + bm @ np.array([0.0, 0.398 * s, 0.085 * s], dtype=np.float32)
                        sc.capsule(bp, 0.030 * s, 0.130 * s, bcol, seg_u=10, seg_cap=4,
                                   mat=bm @ euler_mat(0, 0, 90), outline=ol, outline_w=0.014 * s, specular=0.18)
        elif rm == "topi_terbalik":
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.088 * s, -0.105 * s]),
                          (0.372 * s, 0.348 * s, 0.300 * s), hcol, seg_u=22, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.215 * s, 0.182 * s]),
                          (0.172 * s, 0.072 * s, 0.130 * s), hcol, seg_u=14, seg_v=10,
                          mat=head_mat @ euler_mat(-12, 0, 0), outline=ol, outline_w=ow)
            cap_m = head_mat @ euler_mat(-6, 0, 0)
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.205 * s, -0.015 * s]),
                          (0.380 * s, 0.258 * s, 0.366 * s), tcol, seg_u=24, seg_v=12, mat=cap_m,
                          outline=ol, outline_w=ow, specular=0.14, hemi=True)
                sc.cylinder(head_c + head_mat @ np.array([0.0, 0.202 * s, -0.015 * s]), 0.378 * s, 0.030 * s, tcol,
                            seg_u=24, mat=cap_m, outline=ol, outline_w=ow, specular=0.10)
                sc.sphere(head_c + cap_m @ np.array([0.0, 0.460 * s, -0.015 * s]),
                          0.034 * s, PUTIH, seg_u=10, seg_v=8, mat=cap_m, outline=ol, outline_w=ow)
                sc.rbox(head_c + cap_m @ np.array([0.0, 0.195 * s, -0.380 * s]),
                        (0.34 * s, 0.034 * s, 0.25 * s), tcol, roundness=0.55, seg=2,
                        mat=cap_m @ euler_mat(-12, 0, 0), outline=ol, outline_w=ow, specular=0.12)
        elif rm == "botak":
            return
        else:  # rapi / uban / belah
            with sc.part():
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.090 * s, -0.105 * s]),
                          (0.374 * s, 0.350 * s, 0.302 * s), hcol, seg_u=24, seg_v=14, mat=head_mat, outline=ol, outline_w=ow)
                sc.sphere(head_c + head_mat @ np.array([0.0, 0.255 * s, -0.015 * s]),
                          (0.332 * s, 0.132 * s, 0.288 * s), hcol, seg_u=22, seg_v=12, mat=head_mat, outline=ol, outline_w=ow)

        if p.get("peci"):
            with sc.part():
                sc.cylinder(head_c + head_mat @ np.array([0.0, 0.340 * s, 0.0]), 0.26 * s, 0.19 * s, HITAM,
                            seg_u=22, mat=head_mat, outline=ol, outline_w=ow)

    def _draw_face_curved(self, sc, head_c, head_mat, st, s):
        """Tempelkan wajah 2D 512x512 ekspresif terbungkus 8-panel melengkung mulus di bola kepala."""
        p = self.p
        open_q = round(clamp(float(st.get("open_amt", 0.0)), 0.0, 1.0) * 6.0) / 6.0
        blink_b = bool(float(st.get("blink", 0.0)) > 0.5)
        lk = st.get("lihat", (0.0, 0.0))
        look_q = (round(float(lk[0]), 1), round(float(lk[1]), 1))
        km = p.get("kacamata")
        bm = bool(p.get("bulu_mata", False))
        kum = bool(p.get("kumis", False))
        kcol = warna(p.get("kumis_warna"), (220, 224, 232))
        skin_col = warna(p.get("kulit"), (252, 224, 200))
        ms = bool(p.get("mata_sclera", False))
        mk = bool(p.get("maskulin", False))
        face_im = _face_decal_rgba(st.get("expr", "senang"), open_q, blink_b, look_q, km, bm, kum, kcol, skin_col, mata_sclera=ms, maskulin=mk)

        rx = 0.362 * s
        rz = 0.340 * s
        w_half = 0.326 * s
        y_bot, y_top = -0.258 * s, +0.264 * s
        n_strips = 8
        xs = [lerp(-w_half, +w_half, k / n_strips) for k in range(n_strips + 1)]
        zs = [rz * math.sqrt(max(0.02, 1.0 - (x / rx) ** 2)) for x in xs]
        u_cuts = [int(round(512 * k / n_strips)) for k in range(n_strips + 1)]
        for i in range(n_strips):
            strip = face_im.crop((u_cuts[i], 0, u_cuts[i + 1], 512))
            p0 = head_c + head_mat @ np.array([xs[i], y_bot, zs[i]], dtype=np.float32)
            p1 = head_c + head_mat @ np.array([xs[i + 1], y_bot, zs[i + 1]], dtype=np.float32)
            p2 = head_c + head_mat @ np.array([xs[i + 1], y_top, zs[i + 1]], dtype=np.float32)
            p3 = head_c + head_mat @ np.array([xs[i], y_top, zs[i]], dtype=np.float32)
            sc.textured_quad([p0, p1, p2, p3], strip, emissive=0.0, bias=-0.05)

    def _draw_hijab_frame(self, sc, head_c, head_mat, s, hij):
        """Bingkai bukaan wajah hijab melengkung 10-panel: menutup sambungan 3D yang bergerigi."""
        frame_im = _hijab_frame_rgba(tuple(int(v) for v in hij))
        rx, rz = 0.372 * s, 0.354 * s
        w_half = 0.320 * s
        y_bot, y_top = -0.266 * s, +0.266 * s
        n_strips = 10
        xs = [lerp(-w_half, +w_half, k / n_strips) for k in range(n_strips + 1)]
        zs = [rz * math.sqrt(max(0.02, 1.0 - (x / rx) ** 2)) for x in xs]
        u_cuts = [int(round(512 * k / n_strips)) for k in range(n_strips + 1)]
        for i in range(n_strips):
            strip = frame_im.crop((u_cuts[i], 0, u_cuts[i + 1], 512))
            p0 = head_c + head_mat @ np.array([xs[i], y_bot, zs[i]], dtype=np.float32)
            p1 = head_c + head_mat @ np.array([xs[i + 1], y_bot, zs[i + 1]], dtype=np.float32)
            p2 = head_c + head_mat @ np.array([xs[i + 1], y_top, zs[i + 1]], dtype=np.float32)
            p3 = head_c + head_mat @ np.array([xs[i], y_top, zs[i]], dtype=np.float32)
            sc.textured_quad([p0, p1, p2, p3], strip, emissive=0.0, bias=-0.035)

    def _draw_suit_front(self, sc, jacket_c, body_mat, s, shirt, in_col, tie_col):
        """Tempelkan decal jas/kerah/dasi 2D melengkung 6-strip mengikuti kontur frustum jas A-line."""
        suit_im = _suit_decal_rgba(shirt, in_col, tie_col)
        y_bot, y_top = -0.200 * s, +0.208 * s
        sx, sz = 1.08, 0.64
        rt, rb = 0.156 * s, 0.194 * s
        n_strips = 6
        ang_max = math.radians(52.0)
        angs = [lerp(-ang_max, +ang_max, k / n_strips) for k in range(n_strips + 1)]
        u_cuts = [int(round(512 * k / n_strips)) for k in range(n_strips + 1)]
        z_pad = 0.011 * s
        for i in range(n_strips):
            a0, a1 = angs[i], angs[i + 1]
            strip = suit_im.crop((u_cuts[i], 0, u_cuts[i + 1], 512))
            p0 = jacket_c + body_mat @ np.array([math.sin(a0) * rb * sx, y_bot, math.cos(a0) * rb * sz + z_pad], dtype=np.float32)
            p1 = jacket_c + body_mat @ np.array([math.sin(a1) * rb * sx, y_bot, math.cos(a1) * rb * sz + z_pad], dtype=np.float32)
            p2 = jacket_c + body_mat @ np.array([math.sin(a1) * rt * sx, y_top, math.cos(a1) * rt * sz + z_pad], dtype=np.float32)
            p3 = jacket_c + body_mat @ np.array([math.sin(a0) * rt * sx, y_top, math.cos(a0) * rt * sz + z_pad], dtype=np.float32)
            sc.textured_quad([p0, p1, p2, p3], strip, emissive=0.0, bias=-0.04)

    def _draw_skirt(self, sc, root_pos, root_mat, body_mat, hip_y, s, pants, ol):
        """Rok A-line bersih: satu frustum melebar ke bawah dengan garis tinta tegas."""
        top_y = hip_y + 0.180 * s
        bottom_y = hip_y - 0.175 * s
        h = max(0.12 * s, top_y - bottom_y)
        c = root_pos + root_mat @ np.array([0.0, (top_y + bottom_y) * 0.5, 0.0], dtype=np.float32)
        sc.frustum(c, 0.240 * s, 0.184 * s, h, pants, seg_u=36, mat=body_mat,
                   outline=ol, outline_w=0.020 * s, specular=0.04,
                   scale_xz=(1.08, 0.72), outline_end=True)

    def _draw_hand(self, sc, wri, f_mat, sign, s, skin, ol, own_part=True):
        """Kepalan tangan chibi bulat chunky + ibu jari tegas (bebas seam)."""
        hand_c = wri + f_mat @ np.array([0.0, -0.028 * s, 0.010 * s], dtype=np.float32)
        if own_part:
            with sc.part():
                sc.rbox(hand_c, (0.142 * s, 0.136 * s, 0.126 * s), skin, roundness=0.78, seg=3,
                        mat=f_mat, outline=ol, outline_w=0.018 * s, specular=0.06)
                thumb_c = hand_c + f_mat @ np.array([-sign * 0.056 * s, 0.018 * s, 0.040 * s], dtype=np.float32)
                sc.sphere(thumb_c, (0.042 * s, 0.046 * s, 0.040 * s), skin, seg_u=16, seg_v=12,
                          mat=f_mat, outline=ol, outline_w=0.018 * s, specular=0.06)
        else:
            sc.rbox(hand_c, (0.142 * s, 0.136 * s, 0.126 * s), skin, roundness=0.78, seg=3,
                    mat=f_mat, outline=ol, outline_w=0.018 * s, specular=0.06)
            thumb_c = hand_c + f_mat @ np.array([-sign * 0.056 * s, 0.018 * s, 0.040 * s], dtype=np.float32)
            sc.sphere(thumb_c, (0.042 * s, 0.046 * s, 0.040 * s), skin, seg_u=16, seg_v=12,
                      mat=f_mat, outline=ol, outline_w=0.018 * s, specular=0.06)

    def _draw_shoe(self, sc, ank, c_mat, sign, s, shoe_c, is_sneaker, ol):
        """Sepatu kartun chibi bulat membulat halus (1 part utuh per sepatu, bebas crack)."""
        s_mat = c_mat @ euler_mat(0.0, sign * 14.0, 0.0)
        base_p = ank + c_mat @ np.array([sign * 0.014 * s, -0.014 * s, 0.056 * s], dtype=np.float32)
        with sc.part():
            if is_sneaker:
                sole_p = base_p + s_mat @ np.array([0.0, -0.022 * s, 0.004 * s], dtype=np.float32)
                sc.capsule(sole_p, 0.072 * s, 0.224 * s, PUTIH, seg_u=22, seg_cap=6,
                           mat=s_mat @ euler_mat(90, 0, 0), scale_xz=(1.12, 0.46),
                           outline=ol, outline_w=0.018 * s, specular=0.04)
                up_p = base_p + s_mat @ np.array([0.0, 0.014 * s, -0.008 * s], dtype=np.float32)
                sc.capsule(up_p, 0.068 * s, 0.194 * s, (34, 36, 44), seg_u=22, seg_cap=6,
                           mat=s_mat @ euler_mat(90, 0, 0), scale_xz=(1.08, 0.84),
                           outline=ol, outline_w=0.018 * s, specular=0.14)
                toe_p = base_p + s_mat @ np.array([0.0, 0.004 * s, 0.078 * s], dtype=np.float32)
                sc.sphere(toe_p, (0.064 * s, 0.048 * s, 0.060 * s), PUTIH, seg_u=18, seg_v=12,
                          mat=s_mat, outline=ol, outline_w=0.018 * s, specular=0.06)
            else:
                sole_p = base_p + s_mat @ np.array([0.0, -0.024 * s, 0.002 * s], dtype=np.float32)
                sc.capsule(sole_p, 0.074 * s, 0.228 * s, gelap(shoe_c, 0.32), seg_u=22, seg_cap=6,
                           mat=s_mat @ euler_mat(90, 0, 0), scale_xz=(1.14, 0.42),
                           outline=ol, outline_w=0.018 * s, specular=0.04)
                up_p = base_p + s_mat @ np.array([0.0, 0.012 * s, -0.004 * s], dtype=np.float32)
                sc.capsule(up_p, 0.074 * s, 0.214 * s, shoe_c, seg_u=24, seg_cap=6,
                           mat=s_mat @ euler_mat(90, 0, 0), scale_xz=(1.14, 0.82),
                           outline=ol, outline_w=0.018 * s, specular=0.18)

    def draw(self, sc, pos, st, skala=None):
        p = self.p
        s = float(skala if skala is not None else p.get("skala", 1.0))
        ang = _pose_angles(st)

        hadap = st.get("hadap", "depan")
        yaw = {
            "depan": 0.0, "serong_kanan": 24.0, "serong_kiri": -24.0,
            "kanan": 78.0, "kiri": -78.0, "belakang": 180.0,
        }.get(hadap, float(hadap) if isinstance(hadap, (int, float)) else 0.0)

        root_pos = np.array(pos, dtype=np.float32)
        if ang["lie"] > 0.5:
            root_mat = euler_mat(-86.0, yaw, 0.0)
            root_pos = root_pos + np.array([0.0, 0.22 * s, 0.0], dtype=np.float32)
        else:
            root_mat = euler_mat(0.0, yaw, 0.0)

        sc.drop_shadow(float(pos[0]), float(pos[1]), float(pos[2]), 0.38 * s, 0.24 * s, 0.26)

        ol = bool(p.get("outline", True))
        ow_body = 0.020 * s
        ow_limb = 0.018 * s
        skin = warna(p.get("kulit"), (252, 224, 200))
        shirt = warna(p.get("kemeja"), TEAL)
        pants = warna(p.get("bawah_warna"), (42, 44, 52))
        shoe_c = warna(p.get("sepatu"), (54, 56, 66))

        hip_y = (0.51 + ang["hip_drop"] * 0.85) * s
        body_mat = root_mat @ euler_mat(*ang["body"])

        # --- Badan A-line tailored chibi (1 part utuh torso -> bahu & hem super mulus) ---
        has_rompi = bool(p.get("rompi"))
        is_rok = (p.get("bawah") == "rok")
        is_jas = bool(p.get("jas") or p.get("blazer")) and not p.get("hijab") and not has_rompi
        torso_c = root_pos + root_mat @ np.array([0.0, hip_y, 0.0], dtype=np.float32) + body_mat @ np.array([0.0, 0.258 * s, 0.0], dtype=np.float32)
        jacket_c = torso_c + body_mat @ np.array([0.0, 0.032 * s, 0.0], dtype=np.float32)

        with sc.part() as torso_pid:
            if is_jas:
                in_col = warna(p.get("kemeja_dalam"), PUTIH)
                tie_col = warna(p.get("dasi")) if p.get("dasi") else None
                sc.frustum(jacket_c, 0.194 * s, 0.156 * s, 0.398 * s, shirt, seg_u=28, mat=body_mat,
                           outline=ol, outline_w=ow_body, scale_xz=(1.08, 0.64), specular=0.04)
                sh_cap = jacket_c + body_mat @ np.array([0.0, 0.188 * s, 0.0], dtype=np.float32)
                sc.sphere(sh_cap, (0.168 * s, 0.056 * s, 0.100 * s), shirt, seg_u=22, seg_v=10,
                          mat=body_mat, outline=ol, outline_w=ow_body, specular=0.04)
                self._draw_suit_front(sc, jacket_c, body_mat, s, shirt, in_col, tie_col)
            elif has_rompi:
                vcol = warna(p["rompi"], ORANYE)
                sc.frustum(jacket_c, 0.198 * s, 0.162 * s, 0.394 * s, vcol, seg_u=28, mat=body_mat,
                           outline=ol, outline_w=ow_body, scale_xz=(1.08, 0.66), specular=0.04)
                sh_cap = jacket_c + body_mat @ np.array([0.0, 0.186 * s, 0.0], dtype=np.float32)
                sc.sphere(sh_cap, (0.168 * s, 0.056 * s, 0.105 * s), shirt, seg_u=18, seg_v=10,
                          mat=body_mat, outline=ol, outline_w=ow_body, specular=0.02)
                for sx in (-1, 1):
                    sc.rbox(jacket_c + body_mat @ np.array([sx * 0.090 * s, 0.00 * s, 0.132 * s]),
                            (0.038 * s, 0.24 * s, 0.016 * s), (235, 245, 95), roundness=0.35, seg=2,
                            mat=body_mat, outline=ol, outline_w=ow_body, emissive=0.10, specular=0.0)
            else:
                sc.frustum(jacket_c, 0.194 * s, 0.158 * s, 0.392 * s, shirt, seg_u=28, mat=body_mat,
                           outline=ol, outline_w=ow_body, scale_xz=(1.08, 0.66), specular=0.04)
                sh_cap = jacket_c + body_mat @ np.array([0.0, 0.184 * s, 0.0], dtype=np.float32)
                sc.sphere(sh_cap, (0.170 * s, 0.056 * s, 0.104 * s), shirt, seg_u=22, seg_v=10,
                          mat=body_mat, outline=ol, outline_w=ow_body, specular=0.04)

        # Aksesori dada non-is_jas: blazer berhijab, dasi kupu-kupu, dasi biasa, kalung
        if (p.get("jas") or p.get("blazer")) and not is_jas:
            lap_col = terang(shirt, 0.10) if shirt != PUTIH else ABU
            for sx in (-1, 1):
                lap_p = jacket_c + body_mat @ np.array([sx * 0.058 * s, 0.088 * s, 0.124 * s], dtype=np.float32)
                sc.rbox(lap_p, (0.036 * s, 0.175 * s, 0.018 * s), lap_col, roundness=0.3, seg=2,
                        mat=body_mat @ euler_mat(0, 0, sx * -16), outline=ol, outline_w=0.014 * s, specular=0.0)
            for by in (0.01, -0.05):
                btn_p = jacket_c + body_mat @ np.array([0.0, by * s, 0.132 * s], dtype=np.float32)
                sc.sphere(btn_p, 0.015 * s, gelap(shirt, 0.35), seg_u=10, seg_v=8, mat=body_mat, specular=0.0)

        if p.get("hijab"):
            hij = warna(p["hijab"], (32, 34, 44))
            with sc.part():
                sc.sphere(jacket_c + body_mat @ np.array([0.0, 0.175 * s, 0.015 * s]),
                          (0.246 * s, 0.128 * s, 0.178 * s), hij, seg_u=24, seg_v=14, mat=body_mat,
                          outline=ol, outline_w=ow_limb, specular=0.0)

        if p.get("dasi_kupu"):
            bow_c = jacket_c + body_mat @ np.array([0.0, 0.178 * s, 0.132 * s], dtype=np.float32)
            with sc.part():
                sc.capsule(bow_c + body_mat @ np.array([-0.056 * s, 0.0, 0.0]), 0.038 * s, 0.098 * s, (30, 30, 38),
                           seg_u=16, seg_cap=5, mat=body_mat @ euler_mat(0, 0, 76), scale_xz=(1.0, 0.52),
                           outline=ol, outline_w=0.014 * s, specular=0.06)
                sc.capsule(bow_c + body_mat @ np.array([+0.056 * s, 0.0, 0.0]), 0.038 * s, 0.098 * s, (30, 30, 38),
                           seg_u=16, seg_cap=5, mat=body_mat @ euler_mat(0, 0, -76), scale_xz=(1.0, 0.52),
                           outline=ol, outline_w=0.014 * s, specular=0.06)
                sc.sphere(bow_c + body_mat @ np.array([0.0, 0.0, 0.014 * s]), 0.030 * s, (24, 24, 30), seg_u=14, seg_v=10, mat=body_mat,
                          outline=ol, outline_w=0.014 * s, specular=0.08)
        elif p.get("dasi") and not is_jas:
            dcol = warna(p["dasi"], MERAH)
            with sc.part():
                knot_p = jacket_c + body_mat @ np.array([0.0, 0.168 * s, 0.118 * s], dtype=np.float32)
                sc.sphere(knot_p, (0.028 * s, 0.026 * s, 0.018 * s), gelap(dcol, 0.10),
                          seg_u=14, seg_v=10, mat=body_mat, outline=ol, outline_w=0.014 * s, specular=0.0)
                blade_p = jacket_c + body_mat @ np.array([0.0, 0.072 * s, 0.128 * s], dtype=np.float32)
                sc.rbox(blade_p, (0.042 * s, 0.155 * s, 0.016 * s), dcol, roundness=0.22, seg=2,
                        mat=body_mat, outline=ol, outline_w=0.014 * s, specular=0.0)
                tip_p = jacket_c + body_mat @ np.array([0.0, -0.010 * s, 0.132 * s], dtype=np.float32)
                sc.rbox(tip_p, (0.030 * s, 0.030 * s, 0.015 * s), dcol, roundness=0.15, seg=2,
                        mat=body_mat @ euler_mat(0, 0, 45), outline=ol, outline_w=0.014 * s, specular=0.0)
        if p.get("kalung"):
            gold = (244, 198, 58)
            with sc.part():
                for k in range(-3, 4):
                    ka = math.radians(k * 18)
                    kp = jacket_c + body_mat @ np.array([math.sin(ka) * 0.098 * s, (0.158 - abs(k) * 0.016) * s, math.cos(ka) * 0.118 * s], dtype=np.float32)
                    sc.sphere(kp, 0.015 * s, gold, seg_u=10, seg_v=6, mat=body_mat, outline=ol, outline_w=0.012 * s, specular=0.12)
                sc.sphere(jacket_c + body_mat @ np.array([0.0, 0.102 * s, 0.128 * s]), 0.028 * s, gold,
                          seg_u=14, seg_v=10, mat=body_mat, outline=ol, outline_w=0.012 * s, specular=0.16)

        # --- Leher tegas + Kepala bulat chibi besar + telinga menyatu 1 part + rambut + wajah ---
        head_mat = body_mat @ euler_mat(*ang["head"])
        neck_c = jacket_c + body_mat @ np.array([0.0, 0.236 * s, 0.0], dtype=np.float32)
        with sc.part():
            sc.capsule(neck_c, 0.070 * s, 0.165 * s, skin, seg_u=16, seg_cap=5, mat=body_mat,
                       outline=ol, outline_w=ow_limb, specular=0.0)
        head_c = neck_c + head_mat @ np.array([0.0, 0.344 * s, 0.0], dtype=np.float32)
        head_r = (0.358 * s, 0.342 * s, 0.332 * s)
        ear_x = 0.338 * s
        with sc.part():
            sc.sphere(head_c, head_r, skin, seg_u=36, seg_v=24, mat=head_mat,
                      outline=ol, outline_w=ow_body, specular=0.12)
            if p.get("telinga"):
                for sx in (-1, 1):
                    ear_c = head_c + head_mat @ np.array([sx * ear_x, -0.042 * s, -0.006 * s], dtype=np.float32)
                    sc.sphere(ear_c, (0.068 * s, 0.080 * s, 0.052 * s), skin,
                              seg_u=16, seg_v=12, mat=head_mat, outline=ol, outline_w=ow_body, specular=0.04)
        self._draw_hair(sc, head_c, head_mat, s)
        self._draw_face_curved(sc, head_c, head_mat, st, s)

        # --- Lengan mengerucut mulus (1 part per lengan -> 0 seam siku!) + manset putih + kepalan chunky ---
        is_stick_arm = bool(p.get("lengan_stick"))
        stick_col = warna(p.get("lengan_warna"), (32, 34, 40))
        for side, sign, arm_deg, fore_deg in (
            ("l", -1.0, ang["l_arm"], ang["l_fore"]),
            ("r", +1.0, ang["r_arm"], ang["r_fore"]),
        ):
            sh = jacket_c + body_mat @ np.array([sign * 0.162 * s, 0.140 * s, 0.0], dtype=np.float32)
            u_mat = body_mat @ euler_mat(*arm_deg)
            f_mat = u_mat @ euler_mat(fore_deg, 0.0, 0.0)
            elb = sh + u_mat @ np.array([0.0, -0.195 * s, 0.0], dtype=np.float32)
            wri = elb + f_mat @ np.array([0.0, -0.185 * s, 0.0], dtype=np.float32)

            if is_stick_arm:
                with sc.part():
                    sc.sphere(sh, 0.048 * s, stick_col, seg_u=14, seg_v=10, mat=u_mat, outline=ol, outline_w=ow_limb, specular=0.0)
                    sc.tapered_limb(sh, elb, 0.046 * s, 0.046 * s, stick_col, seg_u=14, outline=ol, outline_w=ow_limb)
                    sc.sphere(elb, 0.046 * s, stick_col, seg_u=14, seg_v=10, mat=u_mat, outline=ol, outline_w=ow_limb, specular=0.0)
                    sc.tapered_limb(elb, wri, 0.046 * s, 0.044 * s, stick_col, seg_u=14, outline=ol, outline_w=ow_limb)
                self._draw_hand(sc, wri, f_mat, sign, s, skin, ol)
            else:
                if p.get("lengan_pendek"):
                    # Lengan kaos menyatu part_id dengan torso -> 0 garis potong kaku di bahu/ketiak!
                    _prev_p = sc._cur_part
                    sc._cur_part = torso_pid
                    try:
                        sc.sphere(sh, 0.064 * s, shirt, seg_u=18, seg_v=12, mat=u_mat, outline=ol, outline_w=ow_limb, specular=0.04)
                        sl_end = sh + u_mat @ np.array([0.0, -0.125 * s, 0.0], dtype=np.float32)
                        sc.tapered_limb(sh, sl_end, 0.062 * s, 0.072 * s, shirt, seg_u=20, outline=ol, outline_w=ow_limb, caps=True)
                    finally:
                        sc._cur_part = _prev_p
                    # Lengan kulit + kepalan tangan dalam 1 part utuh -> tidak ada garis gelang hitam di pergelangan!
                    with sc.part():
                        arm_start = sh + u_mat @ np.array([0.0, -0.105 * s, 0.0], dtype=np.float32)
                        sc.tapered_limb(arm_start, elb, 0.050 * s, 0.050 * s, skin, seg_u=18, outline=ol, outline_w=ow_limb)
                        sc.sphere(elb, 0.050 * s, skin, seg_u=16, seg_v=12, mat=u_mat, outline=ol, outline_w=ow_limb, specular=0.04)
                        sc.tapered_limb(elb, wri, 0.050 * s, 0.048 * s, skin, seg_u=18, outline=ol, outline_w=ow_limb)
                        self._draw_hand(sc, wri, f_mat, sign, s, skin, ol, own_part=False)
                else:
                    sh_r = 0.062 * s
                    elb_r = 0.062 * s
                    cuff_r = 0.068 * s
                    # Lengan baju/jas menyatu part_id dengan torso -> bahu mulus tanpa garis belah!
                    _prev_p = sc._cur_part
                    sc._cur_part = torso_pid
                    try:
                        sc.sphere(sh, sh_r, shirt, seg_u=18, seg_v=12, mat=u_mat, outline=ol, outline_w=ow_limb, specular=0.04)
                        sc.tapered_limb(sh, elb, sh_r, elb_r, shirt, seg_u=20, outline=ol, outline_w=ow_limb)
                        sc.sphere(elb, elb_r, shirt, seg_u=18, seg_v=12, mat=u_mat, outline=ol, outline_w=ow_limb, specular=0.04)
                        if is_jas or p.get("jas") or p.get("blazer"):
                            cuff_start = elb + (wri - elb) * 0.68
                            sc.tapered_limb(elb, cuff_start, elb_r, cuff_r, shirt, seg_u=20, outline=ol, outline_w=ow_limb, caps=True)
                        else:
                            sc.tapered_limb(elb, wri, elb_r, cuff_r, shirt, seg_u=20, outline=ol, outline_w=ow_limb, caps=True)
                    finally:
                        sc._cur_part = _prev_p
                    if is_jas or p.get("jas") or p.get("blazer"):
                        cuff_start = elb + (wri - elb) * 0.68
                        cuff_end = elb + (wri - elb) * 0.96
                        with sc.part():
                            sc.tapered_limb(cuff_start, cuff_end, cuff_r * 0.92, cuff_r * 0.90, warna(p.get("kemeja_dalam"), PUTIH),
                                            seg_u=16, outline=ol, outline_w=0.015 * s, caps=True)
                    self._draw_hand(sc, wri, f_mat, sign, s, skin, ol, own_part=True)

            if side == "r" and st.get("bawa"):
                bawa = st["bawa"]
                if bawa == "buku_terbuka":
                    BD.draw_open_book(
                        sc,
                        wri + f_mat @ np.array([-0.12 * s, 0.02 * s, 0.10 * s]),
                        s=s,
                        kiri=st.get("buku_kiri", "CATATAN"),
                        kanan=st.get("buku_kanan", "BAB 1"),
                        isi=st.get("buku_isi", "FAKTA|PENTING|HARI INI"),
                    )
                elif bawa == "pesawat_mini":
                    BD.draw_airplane_mini(sc, wri + f_mat @ np.array([-0.08 * s, 0.06 * s, 0.08 * s]), s=0.65 * s)
                elif bawa == "kopi":
                    BD.draw_mug(sc, wri + f_mat @ np.array([0.0, -0.02 * s, 0.04 * s]), s=s)
                elif bawa == "hp":
                    sc.rbox(wri + f_mat @ np.array([0.0, 0.02 * s, 0.03 * s]), (0.08 * s, 0.15 * s, 0.02 * s), HITAM,
                            roundness=0.35, seg=2, mat=f_mat, outline=ol, outline_w=0.014 * s)

        # --- Celana / Rok & Kaki A-stance (1 part utuh celana -> 0 seam paha/pinggul/lutut!) ---
        if is_stick_arm:
            leg_col = stick_col
            leg_r_up, leg_r_kn, leg_r_dn = 0.052 * s, 0.050 * s, 0.048 * s
        elif p.get("bawah") == "rok":
            leg_col = skin
            leg_r_up, leg_r_kn, leg_r_dn = 0.054 * s, 0.052 * s, 0.049 * s
        else:
            leg_col = pants
            leg_r_up, leg_r_kn, leg_r_dn = 0.074 * s, 0.072 * s, 0.068 * s

        if is_rok:
            with sc.part():
                self._draw_skirt(sc, root_pos, root_mat, body_mat, hip_y, s, pants, ol)
            for sign, leg_deg, kb in ((-1.0, ang["l_leg"], ang.get("l_knee", ang["knee_bend"])), (+1.0, ang["r_leg"], ang.get("r_knee", ang["knee_bend"]))):
                hp = root_pos + root_mat @ np.array([sign * 0.102 * s, hip_y + 0.012 * s, 0.0], dtype=np.float32)
                t_mat = root_mat @ euler_mat(*leg_deg)
                c_mat = t_mat @ euler_mat(kb, 0.0, 0.0)
                knee = hp + t_mat @ np.array([0.0, -0.232 * s, 0.0], dtype=np.float32)
                ank = knee + c_mat @ np.array([0.0, -0.236 * s, 0.0], dtype=np.float32)
                with sc.part():
                    sc.tapered_limb(hp, knee, leg_r_up, leg_r_kn, leg_col, seg_u=16, outline=ol, outline_w=ow_limb)
                    sc.sphere(knee, leg_r_kn, leg_col, seg_u=14, seg_v=10, mat=t_mat, outline=ol, outline_w=ow_limb, specular=0.02)
                    sc.tapered_limb(knee, ank, leg_r_kn, leg_r_dn, leg_col, seg_u=16, outline=ol, outline_w=ow_limb)
                self._draw_shoe(sc, ank, c_mat, sign, s, shoe_c, bool(p.get("sepatu_sneaker")), ol)
        else:
            # Pelvis kapsul halus + kedua kaki dalam 1 part celana utuh -> transisi pinggul-paha-lutut 100% mulus!
            ank_list = []
            with sc.part():
                pelv_c = root_pos + root_mat @ np.array([0.0, hip_y + 0.032 * s, 0.0], dtype=np.float32)
                sc.capsule(pelv_c, 0.088 * s, 0.340 * s, pants, seg_u=18, seg_cap=6,
                           mat=body_mat @ euler_mat(0, 0, 90), scale_xz=(1.0, 0.88),
                           outline=ol, outline_w=ow_limb, specular=0.02)
                for sign, leg_deg, kb in ((-1.0, ang["l_leg"], ang.get("l_knee", ang["knee_bend"])), (+1.0, ang["r_leg"], ang.get("r_knee", ang["knee_bend"]))):
                    hp = root_pos + root_mat @ np.array([sign * 0.102 * s, hip_y + 0.018 * s, 0.0], dtype=np.float32)
                    t_mat = root_mat @ euler_mat(*leg_deg)
                    c_mat = t_mat @ euler_mat(kb, 0.0, 0.0)
                    knee = hp + t_mat @ np.array([0.0, -0.236 * s, 0.0], dtype=np.float32)
                    ank = knee + c_mat @ np.array([0.0, -0.236 * s, 0.0], dtype=np.float32)
                    sc.tapered_limb(hp, knee, leg_r_up, leg_r_kn, leg_col, seg_u=18, outline=ol, outline_w=ow_limb)
                    sc.sphere(knee, leg_r_kn, leg_col, seg_u=16, seg_v=10, mat=t_mat, outline=ol, outline_w=ow_limb, specular=0.02)
                    sc.tapered_limb(knee, ank, leg_r_kn, leg_r_dn, leg_col, seg_u=18, outline=ol, outline_w=ow_limb)
                    ank_list.append((ank, c_mat, sign))
            for ank, c_mat, sign in ank_list:
                self._draw_shoe(sc, ank, c_mat, sign, s, shoe_c, bool(p.get("sepatu_sneaker")), ol)
