# -*- coding: utf-8 -*-
"""
tokoh.py - rig tokoh: kepala besar chibi, badan kecil, gambar penuh lewat Python/Pillow.

Satuan lokal (skala 1): kaki di y=0, tinggi total ±470, jari-jari kepala 100.
Gaya bawaan tetap: kepala tebal-bergaris, mata oval hitam, mulut D merah, seragam SMP,
tangan bulatan, sepatu hitam. Preset utama "kribo" memakai rambut afro, kacamata kotak,
kaos teal + dasi kupu-kupu, lengan berisi kulit, dan sneaker hitam-putih.
Semua varian memakai rig prosedural yang sama (lipsync/kedip/ekspresi/pose tidak berubah).
"""
import math
from stik import *
import benda

HEAD_R = 96.0
HEAD_Y = -352.0          # pusat kepala (berdiri, proporsi chibi Ghibli hangat)
SHOULDER_Y = -254.0
HIP_Y = -142.0
SIT_DROP = 64.0
UP_ARM = 56.0
FORE_ARM = 52.0
SHOULDER_X = 40.0

# ------------------------------------------------------------------ casting
# Semua field opsional. rambut: afro jambul keriting rapi botak kuncir bob uban panjang
PRESET = {
    "kribo":  dict(nama="Kribo", rambut="kribo_chibi", rambut_warna=(24, 20, 22), kulit=(254, 232, 214),
                   kacamata="pintar_kotak", wajah_chibi_ref=True, telinga=True,
                   iris=(24, 24, 28), outline_hangat=True, kaos_chibi=True,
                   kemeja=(44, 46, 52), krah=False, kancing=False,
                   dasi=(68, 138, 144), dasi_kupu=True, lengan_tebal=True, lengan_panjang=False,
                   sepatu_chunky=True, celana_jogger=True, tangan_saku=True,
                   badan_lebar=1.56, pinggul_lebar=1.68, bahu_x=52.0, lengan_besar=1.28,
                   hip_y=-146.0, kaki_tebal=2.35, kaki_lebar=1.24, sepatu_besar=1.34, tangan_besar=0.92,
                   bawah="celana", bawah_warna=(164, 168, 174), sepatu=(42, 44, 50)),
    "raka":   dict(nama="Raka", rambut="jambul", rambut_warna=HITAM, kemeja=PUTIH, dasi=BIRU,
                   badan_lebar=1.72, pinggul_lebar=1.58, bahu_x=58.0, lengan_besar=1.18,
                   hip_y=-136.0, kaki_tebal=1.82, kaki_lebar=1.28, sepatu_besar=1.08, tangan_besar=1.0,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "nadia":  dict(nama="Nadia", hijab=(216, 174, 168), hijab_tua=(178, 134, 130), hijab_gaya="modern",
                   kulit=(248, 218, 188), kacamata="bulat", mata_chibi=True, bulu_mata=True,
                   outline_hangat=True,
                   kemeja=(236, 224, 202), kemeja_dalam=PUTIH, blazer=True, krah=False, kancing=False, dasi=None,
                   lengan_tebal=True, lengan_panjang=True,
                   badan_lebar=1.74, pinggul_lebar=1.62, bahu_x=58.0, lengan_besar=1.22,
                   hip_y=-136.0, kaki_tebal=1.84, kaki_lebar=1.24, sepatu_besar=1.08, tangan_besar=1.0,
                   bawah="rok", bawah_warna=(116, 98, 92), sepatu=(128, 92, 66)),
    "hana":   dict(nama="Hana", rambut="panjang_naa", rambut_warna=(94, 74, 56), kulit=(250, 220, 188),
                   wajah_naa=True, telinga=True, iris=(58, 128, 126), pipi_garis=True,
                   outline_hangat=True, bulu_mata=True,
                   kemeja=(106, 126, 146), kemeja_dalam=(54, 62, 70), coat_naa=True, turtleneck=True,
                   krah=False, kancing=False, dasi=None,
                   lengan_tebal=True, lengan_panjang=True,
                   badan_lebar=1.82, pinggul_lebar=1.74, bahu_x=58.0, lengan_besar=1.34,
                   hip_y=-132.0, kaki_tebal=2.04, kaki_lebar=1.24, sepatu_besar=1.14, tangan_besar=1.0,
                   bawah="celana", bawah_warna=(56, 64, 74), sepatu=(132, 94, 64)),
    "arka":   dict(nama="Arka", rambut="comma", rambut_warna=(68, 72, 92), kulit=(252, 226, 206),
                   kacamata="browline", wajah_arka=True, telinga=True, iris=(118, 122, 144),
                   outline_hangat=True, alis_tebal=True,
                   kemeja=(198, 224, 246), krah=True, kancing=False, saku_dada=True,
                   dasi=(48, 52, 66), dasi_klip=True, sabuk=(72, 62, 66), lengan_gulung=True,
                   lengan_tebal=True, lengan_panjang=False, sepatu_sneaker=False,
                   badan_lebar=1.86, pinggul_lebar=1.76, bahu_x=60.0, lengan_besar=1.34,
                   hip_y=-132.0, kaki_tebal=2.14, kaki_lebar=1.26, sepatu_besar=1.14, tangan_besar=1.02,
                   bawah="celana", bawah_warna=(58, 62, 74), sepatu=(46, 50, 62)),
    "bimo":   dict(nama="Bimo", rambut="keriting", rambut_warna=(62, 40, 34), kemeja=PUTIH, dasi=BIRU,
                   badan_lebar=1.52, pinggul_lebar=1.38, bahu_x=54.0, lengan_besar=1.02,
                   hip_y=-144.0, kaki_tebal=1.58, kaki_lebar=1.22, sepatu_besar=1.02, tangan_besar=0.96,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "dimas":  dict(nama="Dimas", rambut="rapi", rambut_warna=HITAM, kacamata=True, kemeja=PUTIH, dasi=BIRU,
                   badan_lebar=1.52, pinggul_lebar=1.38, bahu_x=54.0, lengan_besar=1.02,
                   hip_y=-144.0, kaki_tebal=1.58, kaki_lebar=1.22, sepatu_besar=1.02, tangan_besar=0.96,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "sari":   dict(nama="Sari", hijab=(250, 250, 252), hijab_tua=ABU, kemeja=PUTIH, dasi=MERAH,
                   badan_lebar=1.44, pinggul_lebar=1.36, bahu_x=52.0, lengan_besar=0.98,
                   hip_y=-145.0, kaki_tebal=1.48, kaki_lebar=1.16, sepatu_besar=1.0, tangan_besar=0.94,
                   bawah="rok", bawah_warna=(44, 44, 52), bulu_mata=True),
    "tika":   dict(nama="Tika", rambut="kuncir", rambut_warna=HITAM, kemeja=PUTIH, dasi=MERAH,
                   badan_lebar=1.44, pinggul_lebar=1.36, bahu_x=52.0, lengan_besar=0.98,
                   hip_y=-145.0, kaki_tebal=1.48, kaki_lebar=1.16, sepatu_besar=1.0, tangan_besar=0.94,
                   bawah="rok", bawah_warna=(44, 44, 52), bulu_mata=True),
    "ayah":   dict(nama="Ayah", rambut="rapi", rambut_warna=(70, 70, 80), kumis=True, kemeja=(200, 224, 250), dasi=None,
                   badan_lebar=1.60, pinggul_lebar=1.46, bahu_x=58.0, lengan_besar=1.06,
                   hip_y=-140.0, kaki_tebal=1.64, kaki_lebar=1.26, sepatu_besar=1.04, tangan_besar=0.98,
                   bawah="celana", bawah_warna=NAVY, skala=1.08),
    "ibu":    dict(nama="Ibu", hijab=HIJAU, hijab_tua=HIJAU_TUA, kemeja=(250, 236, 214), dasi=None,
                   badan_lebar=1.46, pinggul_lebar=1.38, bahu_x=52.0, lengan_besar=0.98,
                   hip_y=-144.0, kaki_tebal=1.50, kaki_lebar=1.18, sepatu_besar=1.0, tangan_besar=0.94,
                   bawah="rok", bawah_warna=COKLAT_TUA, bulu_mata=True, skala=1.04),
    "guru":   dict(nama="Pak Guru", rambut="uban", rambut_warna=(205, 205, 212), kacamata=True, kumis=True, kemeja=(236, 232, 214), dasi=MERAH_TUA,
                   badan_lebar=1.60, pinggul_lebar=1.46, bahu_x=58.0, lengan_besar=1.06,
                   hip_y=-140.0, kaki_tebal=1.64, kaki_lebar=1.26, sepatu_besar=1.04, tangan_besar=0.98,
                   bawah="celana", bawah_warna=NAVY, skala=1.06),
    "bu_guru": dict(nama="Bu Guru", hijab=UNGU, hijab_tua=UNGU_TUA, kacamata=True, kemeja=(240, 232, 250), dasi=None,
                    badan_lebar=1.46, pinggul_lebar=1.38, bahu_x=52.0, lengan_besar=0.98,
                    hip_y=-144.0, kaki_tebal=1.50, kaki_lebar=1.18, sepatu_besar=1.0, tangan_besar=0.94,
                    bawah="rok", bawah_warna=UNGU_TUA, bulu_mata=True, skala=1.04),
    "kakek":  dict(nama="Kakek", rambut="botak", peci=True, kumis=True, jenggot=True, kemeja=(250, 250, 250), dasi=None,
                   badan_lebar=1.52, pinggul_lebar=1.38, bahu_x=54.0, lengan_besar=1.00,
                   hip_y=-142.0, kaki_tebal=1.56, kaki_lebar=1.22, sepatu_besar=1.02, tangan_besar=0.96,
                   bawah="celana", bawah_warna=(90, 70, 60), skala=0.98, uban=True),
    "adik":   dict(nama="Adik", rambut="bob", rambut_warna=HITAM, kemeja=(255, 226, 120), dasi=None,
                   badan_lebar=1.40, pinggul_lebar=1.32, bahu_x=50.0, lengan_besar=0.94,
                   hip_y=-146.0, kaki_tebal=1.44, kaki_lebar=1.14, sepatu_besar=0.98, tangan_besar=0.92,
                   bawah="rok", bawah_warna=PINK_TUA, bulu_mata=True, skala=0.8),
    "otak":   dict(nama="Sang Otak", kepala="otak", kulit=(250, 174, 198), mata_chibi=True, bulu_mata=False,
                   kemeja=(242, 248, 255), krah=True, kancing=True, dasi=(66, 178, 232),
                   lengan_tebal=True, lengan_panjang=True, sepatu_sneaker=True,
                   badan_lebar=1.50, pinggul_lebar=1.38, bahu_x=54.0, lengan_besar=1.00,
                   hip_y=-144.0, kaki_tebal=1.56, kaki_lebar=1.20, sepatu_besar=1.02, tangan_besar=0.94,
                   bawah="celana", bawah_warna=(54, 68, 96), sepatu=(52, 62, 86)),
    "virus":  dict(nama="Virus", kepala="virus", kulit=(112, 204, 88), wajah_maskulin=True, bulu_mata=False,
                   kemeja=(66, 138, 64), krah=False, kancing=False, dasi=None,
                   lengan_tebal=True, lengan_besar=0.98, badan_lebar=1.44, pinggul_lebar=1.32, bahu_x=52.0,
                   hip_y=-144.0, kaki_tebal=1.50, kaki_lebar=1.18, sepatu_besar=0.98, tangan_besar=0.92,
                   bawah="celana", bawah_warna=(44, 86, 48), sepatu=(36, 62, 40), skala=0.84),
    "sel_imun": dict(nama="Sel Imun", kepala="sel_imun", kulit=(236, 248, 255), mata_chibi=True, bulu_mata=False,
                     kemeja=(78, 172, 242), krah=False, kancing=False, dasi=None, perisai_dada=True,
                     lengan_tebal=True, lengan_panjang=True, sepatu_sneaker=True,
                     badan_lebar=1.52, pinggul_lebar=1.40, bahu_x=54.0, lengan_besar=1.00,
                     hip_y=-144.0, kaki_tebal=1.56, kaki_lebar=1.20, sepatu_besar=1.02, tangan_besar=0.94,
                     bawah="celana", bawah_warna=(52, 108, 176), sepatu=(44, 86, 148), skala=0.94),
    "bos": dict(nama="Bos", rambut="botak", telinga=True, kacamata="bulat", mata_sclera=True,
                kulit=(248, 214, 194), kemeja=(48, 52, 64), kemeja_dalam=PUTIH, blazer=True, dasi=MERAH,
                lengan_tebal=True, lengan_panjang=True,
                badan_lebar=1.60, pinggul_lebar=1.46, bahu_x=58.0, lengan_besar=1.06,
                hip_y=-140.0, kaki_tebal=1.66, kaki_lebar=1.26, sepatu_besar=1.04, tangan_besar=0.98,
                bawah="celana", bawah_warna=(44, 46, 56), sepatu=HITAM),
}
PRESET["formal"] = dict(PRESET["bos"])


def casting(spec):
    """spec = nama preset (str) atau dict {'dasar': 'kribo', ...override}. Default = kribo."""
    if isinstance(spec, str):
        spec = {"dasar": spec}
    base = dict(PRESET.get(spec.get("dasar", "kribo"), PRESET["kribo"]))
    base.update({k: (tuple(v) if isinstance(v, list) and len(v) == 3 and all(isinstance(i, int) for i in v) else v)
                 for k, v in spec.items() if k != "dasar"})
    base.setdefault("skala", 1.0)
    base.setdefault("lengan_tebal", True)
    base.setdefault("badan_lebar", 1.52)
    base.setdefault("pinggul_lebar", 1.38)
    base.setdefault("bahu_x", 54.0)
    base.setdefault("lengan_besar", 1.02)
    base.setdefault("tangan_besar", 0.96)
    base.setdefault("hip_y", -144.0)
    base.setdefault("kaki_tebal", 1.58)
    base.setdefault("kaki_lebar", 1.22)
    base.setdefault("sepatu_besar", 1.02)
    return base


WARNA = {"putih": PUTIH, "hitam": HITAM, "merah": MERAH, "biru": BIRU, "biru_tua": BIRU_TUA, "pink": PINK, "kuning": KUNING,
         "hijau": HIJAU, "ungu": UNGU, "oranye": ORANYE, "coklat": COKLAT, "abu": ABU, "navy": NAVY, "krem": KRIM,
         "biru_muda": BIRU_MUDA, "pink_muda": PINK_MUDA, "hijau_muda": HIJAU_MUDA, "merah_tua": MERAH_TUA}


def warna(v, default=None):
    if v is None:
        return default
    if isinstance(v, str):
        return WARNA.get(v, default)
    return tuple(v)


# ------------------------------------------------------------------ ekspresi
# eyes: oval arc_up arc_dn half wide spark wink dot | mouth: open smile o frown flat wave smirk grin pout yawn
EKSPRESI = {
    "senang":   dict(eyes="oval", mouth="open", open=0.62, blush=0.55),
    "tenang":   dict(eyes="oval", mouth="smile", blush=0.35),
    "tertawa":  dict(eyes="arc_up", mouth="grin", open=1.0, blush=0.9),
    "kaget":    dict(eyes="wide", mouth="o", brow=(14, 0, 0), blush=0.0),
    "marah":    dict(eyes="oval", mouth="gigit", brow=(-4, -1.0, -1.0), blush=0.0, vein=True, small=0.9),
    "mikir":    dict(eyes="oval", mouth="flat_miring", brow=(0, 0.2, 1.2), blush=0.0, look=(0.35, -0.5)),
    "sedih":    dict(eyes="oval", mouth="frown", brow=(0, 0.9, 0.9), blush=0.0, tear=True, hl=1.3),
    "malu":     dict(eyes="arc_up", mouth="wave", blush=1.0, sweat=True, small=0.8),
    "ngantuk":  dict(eyes="half", mouth="flat", blush=0.0),
    "menguap":  dict(eyes="arc_dn", mouth="yawn", blush=0.0),
    "tidur":    dict(eyes="arc_dn", mouth="smile", blush=0.4),
    "semangat": dict(eyes="spark", mouth="grin", open=0.9, blush=0.8),
    "panik":    dict(eyes="dot", mouth="wave_o", brow=(8, 0.8, 0.8), blush=0.0, sweat=True),
    "bangga":   dict(eyes="half", mouth="smirk", blush=0.4, brow=(0, -0.3, -0.3)),
    "jahil":    dict(eyes="wink", mouth="smirk", blush=0.5),
    "cemberut": dict(eyes="oval", mouth="pout", blush=0.9, brow=(-2, -0.5, -0.5)),
    "cemas":    dict(eyes="oval", mouth="wave", brow=(2, 0.9, 0.9), blush=0.0, sweat=True),
    "lega":     dict(eyes="arc_dn", mouth="open", open=0.35, blush=0.5, sweat=True),
    "terpana":  dict(eyes="spark", mouth="o", brow=(10, 0, 0), blush=0.6),
    "datar":    dict(eyes="dot", mouth="flat", blush=0.0),
}
ALIAS_EKS = {"senyum": "tenang", "kecewa": "sedih", "bingung": "mikir", "gembira": "senang", "ketawa": "tertawa",
             "heran": "kaget", "kesal": "cemberut", "takut": "panik", "ngakak": "tertawa", "ceria": "senang"}


def eks(name):
    name = ALIAS_EKS.get(name, name)
    return EKSPRESI.get(name, EKSPRESI["senang"])


# ------------------------------------------------------------------ pose
# lengan: (a, e, tangan) a=bahu (0 turun,90 samping,180 atas) e=siku (+ terus keluar/atas, - melipat). tangan: m p t f
def _P(L, R, **k):
    d = dict(L=L, R=R, legs="stand", sit=0.0, lean=0.0, tilt=0.0)
    d.update(k)
    return d


POSE = {
    "diam":        _P((14, 10, "m"), (14, 10, "m")),
    "santai":      _P((10, 6, "m"), (10, 6, "m")),
    "lambai":      _P((14, 10, "m"), (116, 18, "m"), wave="R"),
    "lambai2":     _P((116, 18, "m"), (116, 18, "m"), wave="LR"),
    "tunjuk":      _P((26, -80, "m"), (84, -6, "p"), tilt=-2),
    "tunjuk_kiri": _P((84, -6, "p"), (26, -80, "m"), tilt=2),
    "tunjuk_atas": _P((26, -86, "m"), (124, 26, "p")),
    "ide":         _P((26, -86, "m"), (122, 26, "p"), tilt=-3),
    "pinggang":    _P((46, -112, "m"), (46, -112, "m")),
    "jempol":      _P((46, -112, "m"), (92, 46, "t")),
    "silang":      _P((28, -128, "m"), (28, -128, "m")),
    "sorak":       _P((132, 18, "m"), (132, 18, "m"), lean=-3),
    "peregangan":  _P((138, 14, "m"), (138, 14, "m"), lean=-5, tilt=-4),
    "garuk":       _P((164, 36, "m"), (14, 10, "m"), tilt=6),
    "mikir":       _P((24, -150, "m"), (50, -150, "m"), tilt=-6),
    "dagu":        _P((14, 10, "m"), (56, -158, "m"), tilt=7),
    "kaget":       _P((100, 24, "m"), (100, 24, "m"), lean=-5),
    "sedih":       _P((6, 4, "m"), (6, 4, "m"), lean=3, tilt=8),
    "pusing":      _P((128, 88, "m"), (128, 88, "m"), lean=3, tilt=6),
    "marah":       _P((40, -108, "f"), (40, -108, "f"), lean=3),
    "kepal":       _P((16, -110, "f"), (16, -110, "f")),
    "menyerahkan": _P((62, -14, "m"), (62, -14, "m")),
    "angkat_tangan": _P((14, 10, "m"), (132, 24, "m")),
    "angkat_bahu": _P((52, -104, "m"), (52, -104, "m"), tilt=-4),
    "tepuk":       _P((42, -118, "m"), (42, -118, "m")),
    "menguap":     _P((14, 10, "m"), (30, -150, "m"), tilt=-3),
    "pegang_dada": _P((14, 10, "m"), (30, -138, "m")),
    "hormat":      _P((14, 10, "m"), (150, -112, "m")),
    "jalan":       _P((14, 10, "m"), (14, 10, "m"), legs="walk", swing=1.0),
    "lari":        _P((38, -80, "m"), (38, -80, "m"), legs="walk", swing=1.9, lean=9),
    "berjinjit":   _P((14, 10, "m"), (14, 10, "m"), legs="walk", swing=0.5),
    "duduk":       _P((26, -92, "m"), (26, -92, "m"), legs="stand", sit=1.0),
    "duduk_santai": _P((18, -40, "m"), (18, -40, "m"), sit=1.0, lean=-4),
    "duduk_hp":    _P((34, -128, "m"), (34, -128, "m"), sit=1.0, tilt=10, lean=3),
    "duduk_nulis": _P((30, -70, "m"), (40, -112, "m"), sit=1.0, tilt=12, lean=10),
    "duduk_game":  _P((36, -118, "m"), (36, -118, "m"), sit=1.0, tilt=4, lean=-3),
    "duduk_sorak": _P((132, 18, "m"), (132, 18, "m"), sit=1.0, lean=-4),
    "pegang_hp":   _P((34, -128, "m"), (34, -128, "m"), tilt=8),
    "pegang_buku": _P((34, -122, "m"), (34, -122, "m")),
    "menulis":     _P((30, -70, "m"), (40, -112, "m"), tilt=10, lean=6),
    "membungkuk":  _P((22, 4, "m"), (22, 4, "m"), lean=22, tilt=6),
    "bersandar":   _P((14, 10, "m"), (14, 10, "m"), lean=-8),
    "memeluk":     _P((30, -142, "m"), (30, -142, "m")),
    "tidur":       _P((8, 6, "m"), (8, 6, "m"), lean=-82),
    "tidur_kanan": _P((8, 6, "m"), (8, 6, "m"), lean=82),
    "hormat_bendera": _P((14, 10, "m"), (150, -118, "m")),
}
ALIAS_POSE = {"berdiri": "diam", "salam": "lambai", "nunjuk": "tunjuk", "cheer": "sorak", "jongkok": "duduk"}


def pose_def(name):
    return POSE.get(ALIAS_POSE.get(name, name), POSE["diam"])


# ------------------------------------------------------------------ tokoh
def _rot(p, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def _ellpts(cx, cy, rx, ry, n=44):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _wavy_ring(cx, cy, rx, ry, a0, a1, n, amps, steps=9):
    """Siluet rambut ikal lembut: deretan helai bergelombang yang ujungnya mengait ke bawah-luar."""
    def g(v):
        # helai ikal tak beraturan: naik landai membulat lalu ujungnya mengait (tidak simetris, tidak runcing)
        return math.sin(math.pi * (v ** 0.62)) ** 0.75
    pts = []
    for k in range(n):
        ta = a0 + (a1 - a0) * k / n
        tb = a0 + (a1 - a0) * (k + 1) / n
        A = amps[k % len(amps)]
        right = math.cos(math.radians((ta + tb) / 2)) >= 0
        for j in range(steps):
            u = j / steps
            v = u if right else 1.0 - u
            off = A * g(v)
            ang = math.radians(ta + (tb - ta) * u)
            pts.append((cx + (rx + off) * math.cos(ang), cy + (ry + off) * math.sin(ang)))
    ang = math.radians(a1)
    pts.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
    return pts


def _crescent(p0, pm, p1, w, n=10):
    """Helai bulan sabit meruncing di kedua ujung (tekstur ikal rambut)."""
    up = bezier(p0, pm, p1, n)
    out, inn = [], []
    for i, (x, y) in enumerate(up):
        t = i / n
        j, k = min(n, i + 1), max(0, i - 1)
        dx, dy = up[j][0] - up[k][0], up[j][1] - up[k][1]
        l = max(1e-6, math.hypot(dx, dy))
        nx, ny = -dy / l, dx / l
        h = w * math.sin(math.pi * t) * 0.5
        out.append((x + nx * h, y + ny * h))
        inn.append((x - nx * h, y - ny * h))
    return out + inn[::-1]


def _rectpts(x0, y0, x1, y1, r=0.0, n=5):
    """Persegi panjang bersudut tumpul, searah jarum jam dari sudut kiri-atas."""
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0),
                       (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += arc_pts(cx, cy, r, r, a0, a0 + 90, n)[:-1]
    return pts


class Tokoh:
    def __init__(self, spec):
        self.p = casting(spec)

    # st: x y s flip lean tilt sit look expr talk blink arms legs phase amp bob squash bawa
    def draw(self, c, st):
        p = self.p
        s = st["s"] * p["skala"]
        fl = st["flip"]
        sx, sy = st.get("squash", (1.0, 1.0))
        lean = math.radians(st.get("lean", 0))
        sit = st.get("sit", 0.0)
        dy = SIT_DROP * sit
        X0, Y0 = st["x"], st["y"] + st.get("hop", 0)
        cl, sl = math.cos(lean), math.sin(lean)

        def T(lx, ly, nodrop=False):
            if not nodrop:
                ly = ly + dy                      # badan turun saat duduk
            lx = lx * fl
            rx, ry = lx * cl - ly * sl, lx * sl + ly * cl
            return (X0 + rx * s * sx, Y0 + ry * s * sy)

        def TT(pts):
            return [T(*q) for q in pts]

        ow = 4.0 * s           # tebal garis tepi halus & modern (satuan dunia)
        kemeja = warna(p.get("kemeja"), PUTIH)
        kulit = warna(p.get("kulit"), PUTIH)
        dasi = warna(p.get("dasi"))
        bawah_c = warna(p.get("bawah_warna"), HITAM)
        sepatu = warna(p.get("sepatu"), HITAM)
        # arah hadap: "depan" (0.0), "miring"/"3/4" (0.55), "samping" (0.92) atau float 0..1
        # otomatis pakai side-profile ("samping") saat berjalan/berlari kecuali user eksplisit meminta hadap="depan"
        stance_cur = st.get("legs", "stand")
        walking = stance_cur == "walk" and st.get("amp", 0.0) > 0.01
        hadap_raw = st.get("hadap", st.get("miring", None))
        if hadap_raw is None:
            turn = 0.92 if stance_cur == "walk" else 0.0
        elif isinstance(hadap_raw, str):
            turn = {"depan": 0.0, "miring": 0.55, "3/4": 0.55, "tiga_perempat": 0.55, "samping": 0.92, "side": 0.92}.get(hadap_raw.lower(), 0.0)
        elif isinstance(hadap_raw, bool):
            turn = 0.55 if hadap_raw else 0.0
        else:
            turn = clamp(float(hadap_raw), 0.0, 1.0)
        side_prof = turn >= 0.80
        # proporsi badan: berisi seimbang (tidak terlalu kurus di depan, 3/4, maupun side-profile)
        bw_base = float(p.get("badan_lebar", 1.52))
        hipb_base = float(p.get("pinggul_lebar", bw_base * 0.92))
        w_scale = (0.76 if side_prof else (1.0 - 0.14 * turn))
        bw = bw_base * w_scale
        hipb = hipb_base * w_scale
        hy = float(p.get("hip_y", -144.0))
        kt = float(p.get("kaki_tebal", 1.44))
        sm = float(p.get("sepatu_besar", 1.0))
        cx_t = (24.0 * bw if side_prof else 13.0 * turn)     # pergeseran garis tengah dada ke depan saat miring/samping

        # ransel (bagian belakang)
        if st.get("ransel"):
            rc = warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU
            rw = max(0.75, bw * 0.72)
            rx_off = -26.0 * turn
            c.blob(TT([(rx_off - 54 * rw, -256), (rx_off - 66 * rw, -230), (rx_off - 62 * rw, -176), (rx_off - 40 * rw, -152),
                       (rx_off + 40 * rw, -152), (rx_off + 62 * rw, -176), (rx_off + 66 * rw, -230), (rx_off + 54 * rw, -256), (rx_off, -268)]),
                   rc, ow, OUT)
            c.ell(*T(rx_off - 56 * rw, -214), 12 * s, 22 * s, gelap(rc, 0.18), ow * .85)
            c.ell(*T(rx_off + 56 * rw, -214), 12 * s, 22 * s, gelap(rc, 0.18), ow * .85)

        # ---- lengan belakang (saat hadap miring/samping, lengan sisi jauh digambar di belakang torso)
        arms = st["arms"]
        hands = {}
        front_arms = []
        mid_arms = []
        ph_w = st.get("phase", 0.0)
        amp_w = st.get("amp", 0.0)
        sw_w = st.get("swing", 1.0)
        for side, key in (("L", -1), ("R", 1)):
            a, e, hk = arms[side]
            if side_prof and walking:
                # ayunan lengan maju-mundur natural berlawanan fase dengan kaki (tampak samping)
                swing_ang = math.sin(ph_w + (0.0 if side == "R" else math.pi)) * 34.0 * min(1.3, amp_w) * sw_w
                a = swing_ang
                e = max(12.0, 22.0 + swing_ang * 0.35)   # siku menekuk lembut ke depan (+x)
            ar, br = math.radians(a), math.radians(a + e)
            hd_y = SHOULDER_Y + 12 + math.cos(ar) * UP_ARM + math.cos(br) * FORE_ARM
            if turn >= 0.25 and side == "L" and hd_y >= SHOULDER_Y - 52:
                # sisi belakang (L) berada di belakang torso saat miring/samping
                hands[side] = self._arm(c, T, s, fl, key, a, e, hk, kemeja, ow, dy, turn)
            elif hd_y < SHOULDER_Y - 52:
                front_arms.append((side, key, a, e, hk))
            else:
                mid_arms.append((side, key, a, e, hk))

        # ---- kaki
        hipy = hy + dy
        hip = [T(-18, hy), T(18, hy)]
        feet, knees, hip = self._legs(st, T, sit, turn)
        skirt = p.get("bawah") == "rok"
        legw = (11.5 if skirt else 13.6) * kt
        legc = (56, 56, 68) if (skirt and (p.get("hijab") or bawah_c == HITAM)) else (gelap(bawah_c, .36) if skirt else bawah_c)
        legoc = OUT
        jog_mode = bool(p.get("celana_jogger")) and not skirt
        if jog_mode:
            # ===== 1) KAKI CELANA JOGGER LONGGAR DULU (agar sepatu & lidah sepatu tampil utuh 3D di depan manset!) =====
            cxw = T(0, hy)[0]
            wk_s = 0.80 if side_prof else 1.0

            def _nrm(p0, p1):
                ddx, ddy = p1[0] - p0[0], p1[1] - p0[1]
                ll = max(1e-6, math.hypot(ddx, ddy))
                return (-ddy / ll, ddx / ll)
            for i in (0, 1):
                A, K, F = hip[i], knees[i], feet[i]
                N_ = (F[0], F[1] - 22.0 * s * sm)
                n1, n2 = _nrm(A, K), _nrm(K, N_)
                nk = ((n1[0] + n2[0]) * 0.5, (n1[1] + n2[1]) * 0.5)
                ext = 1.0 if abs(A[0] + n1[0] - cxw) >= abs(A[0] - n1[0] - cxw) else -1.0
                Wo = (29.5 * s * wk_s, 33.0 * s * wk_s, 21.0 * s)
                Wi = (18.5 * s * wk_s, 20.0 * s * wk_s, 14.5 * s)

                def LP(t, f, A=A, K=K, N_=N_, n1=n1, n2=n2, nk=nk, ext=ext, Wo=Wo, Wi=Wi):
                    W_use = Wo if f >= 0 else Wi
                    if t <= 0.58:
                        u = t / 0.58
                        P = (lerp(A[0], K[0], u), lerp(A[1], K[1], u))
                        nn = (lerp(n1[0], nk[0], u), lerp(n1[1], nk[1], u))
                        w = lerp(W_use[0], W_use[1], math.sin(u * math.pi / 2))
                    else:
                        u = (t - 0.58) / 0.42
                        P = (lerp(K[0], N_[0], u), lerp(K[1], N_[1], u))
                        nn = (lerp(nk[0], n2[0], u), lerp(nk[1], n2[1], u))
                        w = lerp(W_use[1], W_use[2], u ** 1.6)
                    return (P[0] + nn[0] * w * f * ext, P[1] + nn[1] * w * f * ext)
                ts = [k / 10.0 for k in range(11)]
                leg_fill = gelap(legc, 0.12) if ((turn >= 0.25 or walking) and i == 0) else legc
                outline = [LP(t, 1.0) for t in ts] + [LP(t, -1.0) for t in reversed(ts)]
                c.poly(outline, leg_fill)
                # bayangan sisi dalam & bawah lutut
                c.poly([LP(t, -0.98) for t in ts[:10]] + [LP(t, -0.38) for t in reversed(ts[:10])], gelap(leg_fill, 0.12))
                # strip sporty putih (paha) + hitam (betis) di sisi luar kaki kanan
                if i == 1 and not side_prof:
                    tw = [0.04 + 0.50 * k / 6 for k in range(7)]
                    tb_ = [0.54 + 0.38 * k / 6 for k in range(7)]
                    c.poly([LP(t, 0.96) for t in tw] + [LP(t, 0.54) for t in reversed(tw)], PUTIH)
                    c.poly([LP(t, 0.96) for t in tb_] + [LP(t, 0.54) for t in reversed(tb_)], (42, 44, 50))
                    c.line([LP(t, 0.54) for t in tw + tb_], gelap(leg_fill, 0.32), 1.8 * s)
                # lipatan kain jogger organik
                c.curve([LP(0.42, -0.68), LP(0.48, -0.15), LP(0.45, 0.28)], gelap(leg_fill, 0.22), 1.9 * s)
                c.curve([LP(0.75, -0.65), LP(0.82, -0.05), LP(0.78, 0.42)], gelap(leg_fill, 0.25), 2.1 * s)
                c.poly(outline, None, 2.8 * s, OUT)
                # manset karet pergelangan kaki
                cb = LP(1.0, 0.92), LP(1.0, -0.92)
                cuff = [LP(0.90, -0.94), LP(0.90, 0.94), (cb[0][0], cb[0][1] + 4 * s), (cb[1][0], cb[1][1] + 4 * s)]
                c.blob(cuff, gelap(leg_fill, 0.08), 2.6 * s, OUT, n=3)
                # sedikit pergelangan kaki mengintip di bawah manset sebelum masuk sepatu (persis referensi!)
                c.poly([(cb[1][0] + 4 * s, cb[1][1] + 2 * s), (cb[0][0] - 4 * s, cb[0][1] + 2 * s),
                        (cb[0][0] - 5 * s, cb[0][1] + 10 * s), (cb[1][0] + 5 * s, cb[1][1] + 10 * s)],
                       gelap(kulit, 0.08), 2.0 * s, OUT)
            # ===== 2) dudukan pinggul + jahitan fly + pinggang karet berkerut =====
            pw = 50.0 * (0.62 if side_prof else 1.0 - 0.12 * turn)
            seat = [(-pw, hy - 22), (pw, hy - 22), (pw + 2, hy - 2), (pw * 0.58, hy + 15),
                    (0, hy + 17), (-pw * 0.58, hy + 15), (-pw - 2, hy - 2)]
            c.poly(TT(seat), bawah_c)
            c.line(TT([(-pw, hy - 22), (-pw - 2, hy - 2)]), OUT, 2.8 * s)
            c.line(TT([(pw, hy - 22), (pw + 2, hy - 2)]), OUT, 2.8 * s)
            if not side_prof:
                c.curve(TT([(0, hy - 6), (-1, hy + 8), (2, hy + 17)]), gelap(bawah_c, 0.30), 2.2 * s)
                c.curve(TT([(3, hy - 6), (5, hy + 6), (1, hy + 13)]), gelap(bawah_c, 0.22), 1.6 * s)
                c.line(TT([(-18, hy - 5), (-25, hy + 14)]), gelap(bawah_c, 0.24), 1.8 * s)
                c.line(TT([(18, hy - 5), (25, hy + 14)]), gelap(bawah_c, 0.24), 1.8 * s)
            c.poly(TT([(-pw - 1, hy - 26), (pw + 1, hy - 26), (pw + 2, hy - 6), (-pw - 2, hy - 6)]),
                   gelap(bawah_c, 0.05), 2.6 * s, OUT)
            for kx in (-0.76, -0.46, -0.18, 0.12, 0.42, 0.72):
                c.line(TT([(pw * kx, hy - 24), (pw * kx + 1.5, hy - 8)]), gelap(bawah_c, 0.26), 1.6 * s)
            # ===== 3) SEPATU SNEAKER CHUNKY 3/4 DI DEPAN MANSET (persis referensi: 1 bodi bulat-tinggi utuh + pita sol tebal + lidah tinggi!) =====
            S_sh = s * sm
            for i in (0, 1):
                fx, fy = feet[i]
                dx_ = (1.0 if (turn >= 0.25 or walking) else (-1.0 if i == 0 else -0.82)) * fl
                fx_s = fx + (-2.0 * s if i == 0 else 0.0) * fl
                fy_s = fy + (3.0 * s if i == 1 else 0.0)
                shoe_col = (44, 46, 52) if i == 1 else (40, 42, 48)
                sole_col = (24, 26, 30)
                mid_col = (68, 72, 80)

                def SP(u, v, fx_s=fx_s, fy_s=fy_s, dx_=dx_):
                    return (fx_s + dx_ * u * S_sh, fy_s + v * S_sh)

                # 1) siluet penuh sepatu chunky 3/4 (tumit kanan-atas, lidah tinggi di tengah-atas, moncong bulat tebal di kiri-bawah)
                full_shoe = [
                    SP(-16, -6), SP(-17, -18), SP(-11, -22), SP(-4, -20),
                    SP(0, -29), SP(8, -29), SP(13, -21),
                    SP(23, -14), SP(29, -6), SP(27, 3),
                    SP(14, 6), SP(2, 2), SP(-6, 0), SP(-14, 0),
                ]
                c.blob(full_shoe, shoe_col, 3.0 * s, OUT, n=5)
                # 2) pita sol karet tebal mengikuti bagian bawah sepatu (dengan lekukan arch di SP(-2, 0))
                sole_band = [
                    SP(-16, -6), SP(-6, -4), SP(2, -3), SP(14, 1), SP(28, -2),
                    SP(27, 3), SP(14, 6), SP(2, 2), SP(-6, 0), SP(-14, 0),
                ]
                c.blob(sole_band, sole_col, 2.4 * s, OUT, n=4)
                c.curve([SP(-15, -5.5), SP(-2, -3), SP(14, 1), SP(27, -1.5)], mid_col, 2.2 * s)
                # 3) lubang collar gelap & jahitan lidah sepatu membulat
                c.poly([SP(-12, -19), SP(-4, -18), SP(-3, -21), SP(-10, -21)], (20, 22, 26), 1.6 * s, OUT)
                c.curve([SP(-2, -19), SP(1, -27), SP(7, -27), SP(11, -19)], gelap(shoe_col, 0.28), 1.8 * s)
                # 4) garis jahitan quarter/toe-box & highlight bulat lembut di moncong depan
                c.curve([SP(-4, -5), SP(2, -15), SP(14, -15), SP(23, -6)], gelap(shoe_col, 0.34), 1.8 * s)
                c.ell(*SP(18, -6), 6.2 * S_sh, 3.6 * S_sh, terang(shoe_col, 0.16))
                # 5) 3 strip tali sepatu tebal rapi di punggung sepatu
                for lu, lv in ((3, -22), (8, -19), (13, -16)):
                    c.line([SP(lu, lv), SP(lu + 5.5, lv - 1.5)], terang(shoe_col, 0.32), 2.3 * s)
        for i in ((0, 1) if not jog_mode else ()):
            ax, ay = hip[i]
            kx, ky = knees[i]
            fx, fy = feet[i]
            # pergelangan berhenti di dalam bagian atas sepatu agar cap bulat kaki tidak tembus ke bawah sol
            ank_y = fy - max(14.0 * s * sm, legw * 0.50 * s)
            leg_fill = gelap(legc, 0.16) if ((turn >= 0.25 or walking) and i == 0) else legc
            if p.get("celana_jogger") and not skirt:
                # CELANA JOGGER LONGGAR BERISI MERUNCING DI PERGELANGAN (persis gambar referensi!)
                sg_l = -1 if i == 0 else 1
                w_hip = 22.0 * s * (0.78 if side_prof else 1.0)
                w_mid = 24.5 * s * (0.82 if side_prof else 1.0)
                w_ank = 13.5 * s
                jog_pts = [
                    (ax - w_hip, ay - 6 * s), (ax + w_hip, ay - 6 * s),
                    (kx + w_mid, ky), (fx + w_ank, ank_y),
                    (fx - w_ank, ank_y), (kx - w_mid, ky),
                ]
                c.poly(jog_pts, leg_fill, 3.0 * s, OUT)
                # strip sporty putih-hitam di sisi luar kaki kanan (seperti referensi!)
                if not side_prof and i == 1:
                    c.poly([(kx + w_mid * 0.45, ky - 22 * s), (kx + w_mid * 0.92, ky - 22 * s),
                            (fx + w_ank * 0.90, ank_y - 26 * s), (fx + w_ank * 0.35, ank_y - 26 * s)], PUTIH)
                    c.poly([(fx + w_ank * 0.35, ank_y - 26 * s), (fx + w_ank * 0.90, ank_y - 26 * s),
                            (fx + w_ank * 0.95, ank_y - 2 * s), (fx + w_ank * 0.35, ank_y - 2 * s)], (44, 46, 52))
                # lipatan kain jogger & manset pergelangan kaki
                c.line([(kx - sg_l * 6 * s, ky - 8 * s), (kx + sg_l * 10 * s, ky + 6 * s)], gelap(leg_fill, 0.22), 2.2 * s)
                c.poly([(fx - w_ank * 0.92, ank_y - 8 * s), (fx + w_ank * 0.92, ank_y - 8 * s),
                        (fx + w_ank * 0.85, ank_y + 2 * s), (fx - w_ank * 0.85, ank_y + 2 * s)], gelap(leg_fill, 0.14), 2.2 * s, OUT)
                c.poly(jog_pts, None, 3.0 * s, OUT)
            else:
                c.line([(ax, ay), (kx, ky), (fx, ank_y)], legoc, (legw + 2 * 3.8) * s)
                c.line([(ax, ay), (kx, ky), (fx, ank_y)], leg_fill, legw * s)
            # sepatu
            toe = 1 if (turn >= 0.25 or walking) else (-1 if i == 0 else 1)
            dir_x = toe * fl
            shoe_col = gelap(sepatu, 0.16) if ((turn >= 0.25 or walking) and i == 0) else sepatu
            if p.get("sepatu_chunky"):
                # SEPATU SNEAKER CHUNKY MEMBULAT BERVOLUME (persis gambar referensi!)
                sx_c = fx + dir_x * 9.0 * s * sm
                sy_c = fy - 11.0 * s * sm
                # sol chunky bawah
                c.ell(sx_c, fy - 4.5 * s * sm, 26.5 * s * sm, 8.5 * s * sm, gelap(shoe_col, 0.25), 2.8 * s, OUT)
                # bodi atas sneaker membulat penuh
                c.ell(sx_c, sy_c, 24.5 * s * sm, 13.5 * s * sm, shoe_col, 2.8 * s, OUT)
                # highlight lembut & 2 garis tali sepatu
                c.ell(sx_c + dir_x * 6 * s * sm, sy_c - 3.5 * s * sm, 10 * s * sm, 4.5 * s * sm, terang(shoe_col, 0.18))
                for lk in (-2, 4):
                    c.line([(sx_c + dir_x * lk * s * sm, sy_c - 6 * s * sm),
                            (sx_c + dir_x * (lk + 5) * s * sm, sy_c - 2 * s * sm)], terang(shoe_col, 0.28), 2.2 * s)
            else:
                heel_x = fx - dir_x * 11.5 * s * sm
                front_x = fx + dir_x * 26.5 * s * sm
                top_y = fy - 18.5 * s * sm
                mid_y = fy - 15.5 * s * sm
                sole_y = fy - 4.8 * s * sm
                bot_y = fy
                shoe_poly = [
                    (heel_x, bot_y),
                    (heel_x - dir_x * 1.5 * s * sm, fy - 7.5 * s * sm),
                    (heel_x + dir_x * 2.0 * s * sm, top_y),
                    (fx + dir_x * 4.0 * s * sm, top_y - 1.0 * s * sm),
                    (fx + dir_x * 16.0 * s * sm, mid_y + 1.5 * s * sm),
                    (front_x, fy - 6.5 * s * sm),
                    (front_x - dir_x * 1.5 * s * sm, bot_y),
                ]
                if p.get("sepatu_sneaker"):
                    c.poly(shoe_poly, shoe_col, ow * .82, OUT)
                    cap_poly = [
                        (fx + dir_x * 16.5 * s * sm, sole_y),
                        (fx + dir_x * 17.5 * s * sm, mid_y + 2.8 * s * sm),
                        (front_x - dir_x * 1.2 * s * sm, fy - 7.0 * s * sm),
                        (front_x - dir_x * 0.6 * s * sm, sole_y),
                    ]
                    c.poly(cap_poly, PUTIH)
                    sole_poly = [
                        (heel_x, bot_y),
                        (heel_x - dir_x * 0.6 * s * sm, sole_y),
                        (front_x - dir_x * 0.5 * s * sm, sole_y),
                        (front_x - dir_x * 1.5 * s * sm, bot_y),
                    ]
                    c.poly(sole_poly, PUTIH, ow * .55, OUT)
                    c.poly(shoe_poly, None, ow * .82, OUT)
                else:
                    c.poly(shoe_poly, shoe_col, ow * .82, OUT)
                    c.line([(fx + dir_x * 1.0 * s * sm, top_y + 4.0 * s * sm),
                            (fx + dir_x * 11.0 * s * sm, mid_y + 4.5 * s * sm)],
                           terang(shoe_col, 0.24), 3.0 * s * sm)
        if skirt:
            hem = hy + 56 + dy * 0.85
            sw = max(0.70 if side_prof else 0.90, hipb * 0.96)
            skirt_pts = [(-33 * sw, hy - 12), (33 * sw, hy - 12), (50 * sw, hem - 4)] + bezier((50 * sw, hem - 4), (0, hem + 16), (-50 * sw, hem - 4), 10)[1:-1] + [(-50 * sw, hem - 4)]
            c.poly(TT(skirt_pts), bawah_c, ow, OUT)
            if turn >= 0.25:
                c.poly(TT([(-31 * sw, hy - 10), (-6 * sw, hy - 10), (-16 * sw, hem + 4), (-46 * sw, hem - 5)]),
                       gelap(bawah_c, 0.16))
            else:
                c.poly(TT([(10 * sw, hy - 10), (31 * sw, hy - 10), (46 * sw, hem - 5), (22 * sw, hem + 4)]),
                       gelap(bawah_c, 0.16))
        elif not jog_mode:
            if side_prof:
                # pinggul celana side-profile ramping sejajar paha depan-belakang (tidak terpotong/melebar)
                px_w = max(21.0 * hipb, legw * 0.62)
                c.poly(TT([(-px_w, hy - 14), (px_w, hy - 14),
                           (px_w * 0.94, hy + 10), (0, hy + 16), (-px_w * 0.94, hy + 10)]), bawah_c, ow, OUT)
                # gambar ulang pangkal paha depan agar menyatu mulus ke pinggul
                c.line([hip[1], knees[1]], legc, legw * s)
            else:
                kl_p = float(p.get("kaki_lebar", 1.15)) * (1.0 - 0.22 * turn)
                walk_k = (1.0 - 0.18 * min(1.0, st.get("amp", 0.0))) if walking else 1.0
                px_w = max(25.0 * hipb, 17.5 * kl_p * walk_k + legw * 0.50)
                c.poly(TT([(-px_w, hy - 14), (px_w, hy - 14),
                           (px_w * 0.94, hy + 10), (0, hy + 16), (-px_w * 0.94, hy + 10)]), bawah_c, ow, OUT)
                for i in (0, 1):
                    leg_fill = gelap(legc, 0.16) if ((turn >= 0.25 or walking) and i == 0) else legc
                    c.line([hip[i], knees[i]], leg_fill, legw * s)
        # ---- torso
        if p.get("kaos_chibi"):
            self._kaos_chibi(c, TT, s, kemeja, kulit, hy, turn, side_prof)
        elif False:
            # KAOS A-LINE / OVERSIZED BAHU MELENGKUNG TURUN (persis gambar referensi, BUKAN kotak persegi panjang!)
            y_top = SHOULDER_Y - 4.0
            y_bot = hy - 4.0
            tw_n = 18.0 * (0.75 if side_prof else 1.0)
            tw_s = 46.0 * bw * (0.68 if side_prof else 1.0)
            bw_b = 34.0 * hipb * (0.74 if side_prof else 1.0)
            # siluet bahu melengkung miring alami ke bawah & hem bawah membulat lembut
            kaos_pts = [
                (-tw_n, y_top), (0, y_top + 6), (tw_n, y_top),
                (tw_s * 0.72, y_top + 8), (tw_s, y_top + 28),
                (bw_b * 1.06, y_bot - 22), (bw_b, y_bot - 4),
                (0, y_bot + 6), (-bw_b, y_bot - 4),
                (-bw_b * 1.06, y_bot - 22), (-tw_s, y_top + 28), (-tw_s * 0.72, y_top + 8),
            ]
            c.blob(TT(kaos_pts), kemeja, 3.2 * s, OUT, n=5)
            # cel shading lembut di sisi kanan & lipatan bawah kaos
            c.poly(TT([(tw_n * 0.5, y_top + 8), (tw_s * 0.92, y_top + 26),
                       (bw_b * 0.96, y_bot - 4), (bw_b * 0.30, y_bot + 2)]), gelap(kemeja, 0.16))
            c.curve(TT([(-bw_b * 0.72, y_bot - 6), (0, y_bot + 2), (bw_b * 0.72, y_bot - 6)]), gelap(kemeja, 0.28), 2.6 * s)
            c.blob(TT(kaos_pts), None, 3.2 * s, OUT, n=5)
            # pita pinggang jogger berkerut di bawah hem kaos
            if p.get("celana_jogger"):
                c.poly(TT([(-bw_b * 0.94, y_bot + 2), (bw_b * 0.94, y_bot + 2),
                           (bw_b * 0.96, y_bot + 16), (-bw_b * 0.96, y_bot + 16)]), bawah_c, 2.6 * s, OUT)
                for kx in (-0.55, -0.22, 0.22, 0.55):
                    c.line(TT([(bw_b * kx, y_bot + 4), (bw_b * kx, y_bot + 14)]), gelap(bawah_c, 0.24), 1.8 * s)
        elif p.get("coat_naa"):
            # coat/blazer panjang terbuka persis gaya cewek @naa (turtleneck gelap + coat slate-blue panjang + badge + saku)
            inner_c = warna(p.get("kemeja_dalam"), (54, 62, 70))
            top_w = 34.0 * bw
            bot_w = 37.0 * hipb
            y_top = SHOULDER_Y - 2.0
            y_bot = hy + 34.0    # coat panjang jatuh sampai paha atas!
            # inner turtleneck gelap
            c.poly(TT([(-top_w * 0.68, y_top), (top_w * 0.68, y_top),
                       (bot_w * 0.65, hy + 4), (-bot_w * 0.65, hy + 4)]), inner_c, ow * .78, OUT)
            # kerah turtleneck memeluk leher
            c.poly(TT([(cx_t - 18, y_top - 14), (cx_t + 18, y_top - 14),
                       (cx_t + 20, y_top + 6), (cx_t - 20, y_top + 6)]), inner_c, ow * .76, OUT)
            if side_prof:
                c.poly(TT([(-top_w, y_top + 10), (-top_w * 0.68, y_top - 2), (cx_t - 2, y_top + 2),
                           (cx_t + 4, y_bot), (-bot_w * 0.94, y_bot), (-bot_w, hy - 8)]), kemeja, ow, OUT)
            else:
                for sg in (-1, 1):
                    cc = gelap(kemeja, 0.09) if (sg < 0 if turn >= 0.25 else sg > 0) else kemeja
                    in_t = cx_t + sg * 16.0
                    in_b = cx_t + sg * 24.0
                    c.poly(TT([
                        (in_t, y_top), (sg * top_w * 0.72, y_top - 2), (sg * top_w, y_top + 12),
                        (sg * bot_w, y_bot - 4), (in_b, y_bot + 4), (in_t, y_top + 32),
                    ]), cc, ow, OUT)
                    # lapel kecil
                    c.poly(TT([(in_t, y_top), (in_t + sg * 14, y_top + 18), (in_t + sg * 6, y_top + 28),
                               (in_t + sg * 14, y_top + 38), (in_t, y_top + 48)]), terang(kemeja, 0.06), ow * .72, OUT)
                # badge coklat kecil di dada kanan + kantong kotak bawah kanan (persis gambar 1!)
                c.poly(TT([(cx_t + 24, y_top + 46), (cx_t + 44, y_top + 46), (cx_t + 44, y_top + 56), (cx_t + 24, y_top + 56)]),
                       (182, 144, 96), ow * .6, OUT)
                c.poly(TT([(cx_t + 26, hy - 14), (cx_t + 54, hy - 14), (cx_t + 58, y_bot - 8), (cx_t + 28, y_bot - 8)]),
                       gelap(kemeja, 0.06), ow * .68, OUT)
        elif p.get("jaket"):
            # jaket bomber/kasual terbuka (gaya chibi Ghibli gambar 1: inner putih + jaket kiri-kanan + saku + sabuk)
            inner_c = warna(p.get("kemeja_dalam"), (242, 240, 234))
            top_w = 34.0 * bw
            bot_w = 33.5 * hipb
            y_top = SHOULDER_Y - 2.0
            y_bot = hy - 8.0
            # kaos dalaman putih-krem
            c.poly(TT([(-top_w * 0.72, y_top), (top_w * 0.72, y_top),
                       (bot_w * 0.72, y_bot + 2), (-bot_w * 0.72, y_bot + 2)]), inner_c, ow * .78, OUT)
            # sabuk coklat + gesper emas di pinggang
            if p.get("sabuk"):
                sbc = warna(p["sabuk"], (136, 98, 66))
                c.poly(TT([(-bot_w * 0.76, y_bot - 12), (bot_w * 0.76, y_bot - 12),
                           (bot_w * 0.76, y_bot + 2), (-bot_w * 0.76, y_bot + 2)]), sbc, ow * .72, OUT)
                c.poly(TT([(cx_t - 9, y_bot - 13), (cx_t + 9, y_bot - 13),
                           (cx_t + 9, y_bot + 3), (cx_t - 9, y_bot + 3)]), (218, 178, 96), ow * .68, OUT)
            # panel kiri & kanan jaket terbuka + kerah rib & saku miring
            if side_prof:
                # saat side-profile: jaket membungkus punggung hingga dekat dada depan (kaos putih mengintip di depan)
                c.poly(TT([
                    (-top_w, y_top + 10), (-top_w * 0.72, y_top - 2), (cx_t - 4, y_top + 2),
                    (cx_t - 4, y_bot + 4), (-bot_w * 0.88, y_bot + 4), (-bot_w, y_bot - 6),
                ]), kemeja, ow, OUT)
                c.line(TT([(-bot_w * 0.94, y_bot - 8), (cx_t - 4, y_bot - 8)]), gelap(kemeja, 0.24), 3.0 * s)
            else:
                gap = 12.0
                for sg in (-1, 1):
                    jc = gelap(kemeja, 0.11) if (sg < 0 if turn >= 0.25 else sg > 0) else kemeja
                    in_x = cx_t + sg * gap
                    out_t = sg * top_w
                    out_b = sg * bot_w
                    c.poly(TT([
                        (in_x, y_top + 2), (out_t * 0.75, y_top - 2), (out_t, y_top + 12),
                        (out_b, y_bot - 6), (out_b * 0.88, y_bot + 4), (in_x, y_bot + 4),
                    ]), jc, ow, OUT)
                    c.line(TT([(in_x, y_bot - 8), (out_b * 0.94, y_bot - 8)]), gelap(kemeja, 0.24), 3.0 * s)
                    c.line(TT([(lerp(in_x, out_b, 0.42), y_bot - 22), (lerp(in_x, out_b, 0.80), y_bot - 36)]), gelap(kemeja, 0.26), 3.2 * s)
        elif p.get("blazer"):
            inner_c = warna(p.get("kemeja_dalam"), PUTIH)
            lum = 0.299 * kemeja[0] + 0.587 * kemeja[1] + 0.114 * kemeja[2]
            lap_c = gelap(kemeja, 0.14) if lum > 180 else terang(kemeja, 0.08)
            btn_y = min(hy - 20, SHOULDER_Y + 62)
            nx = min(17.5 * bw, 20.5)
            c.poly(TT([(cx_t - nx - 5, SHOULDER_Y), (cx_t + nx + 5, SHOULDER_Y),
                       (cx_t + 7, btn_y + 8), (cx_t - 7, btn_y + 8)]), inner_c, ow * .78, OUT)
            if p.get("krah", True) and not p.get("dasi_kupu"):
                c.poly(TT([(cx_t - 3.5, SHOULDER_Y - 2), (cx_t - 18, SHOULDER_Y - 1), (cx_t - 11.5, SHOULDER_Y + 17)]), inner_c, ow * .78, OUT)
                c.poly(TT([(cx_t + 3.5, SHOULDER_Y - 2), (cx_t + 18, SHOULDER_Y - 1), (cx_t + 11.5, SHOULDER_Y + 17)]), inner_c, ow * .78, OUT)
            if dasi and not p.get("dasi_kupu"):
                c.poly(TT([(cx_t - 4.0, SHOULDER_Y + 16), (cx_t + 4.0, SHOULDER_Y + 16),
                           (cx_t + 9.5, SHOULDER_Y + 48), (cx_t, SHOULDER_Y + 61), (cx_t - 9.5, SHOULDER_Y + 48)]), dasi, ow * .78, OUT)
                c.poly(TT([(cx_t - 6.2, SHOULDER_Y + 7), (cx_t + 6.2, SHOULDER_Y + 7),
                           (cx_t + 4.4, SHOULDER_Y + 16), (cx_t - 4.4, SHOULDER_Y + 16)]), dasi, ow * .78, OUT)
            for sg in (-1, 1):
                panel_c = gelap(kemeja, 0.10) if (sg < 0 if turn >= 0.25 else sg > 0) else kemeja
                outer_m = (1.0 - 0.18 * turn) if sg > 0 else (1.0 + 0.08 * turn)
                c.poly(TT([
                    (cx_t + sg * nx * outer_m, SHOULDER_Y - 1),
                    (sg * 31 * bw, SHOULDER_Y - 3),
                    (sg * 41 * bw, SHOULDER_Y + 6),
                    (sg * 38 * bw, SHOULDER_Y + 38),
                    (sg * 35 * hipb, hy - 34),
                    (sg * 33 * hipb, hy - 10),
                    (sg * 20 * hipb, hy - 8),
                    (cx_t + sg * 2, hy - 9),
                    (cx_t, btn_y),
                ]), panel_c, ow, OUT)
                c.poly(TT([
                    (cx_t + sg * (nx - 1) * outer_m, SHOULDER_Y - 1),
                    (cx_t + sg * (nx + 12 * bw * 0.72) * outer_m, SHOULDER_Y + 12),
                    (cx_t + sg * (nx + 7.5 * bw * 0.72) * outer_m, SHOULDER_Y + 22),
                    (cx_t + sg * (nx + 13 * bw * 0.72) * outer_m, SHOULDER_Y + 30),
                    (cx_t + sg * 1.5, btn_y),
                    (cx_t + sg * (nx - 3.5) * outer_m, SHOULDER_Y + 18),
                ]), lap_c, ow * .75, OUT)
                c.line(TT([(cx_t + sg * (nx + 7.5 * bw * 0.72) * outer_m, SHOULDER_Y + 22),
                           (cx_t + sg * (nx - 3.5) * outer_m, SHOULDER_Y + 17)]), OUT, ow * .58)
            c.ell(*T(cx_t, btn_y + 6), 3.0 * s, 3.0 * s, OUT)
            if hy - btn_y > 28:
                c.ell(*T(cx_t, btn_y + 19), 2.8 * s, 2.8 * s, OUT)
        else:
            # torso kapsul/trapezoid halus tanpa cekungan pinggang bergelombang
            top_w = 34.0 * bw
            bot_w = 33.0 * hipb
            rad_t = 14.0
            rad_b = 9.0
            y_top = SHOULDER_Y - 2.0
            y_bot = hy - 8.0
            torso_pts = (
                arc_pts(-top_w + rad_t, y_top + rad_t, rad_t, rad_t, 180, 270, 6) +
                arc_pts(top_w - rad_t, y_top + rad_t, rad_t, rad_t, 270, 360, 6) +
                arc_pts(bot_w - rad_b, y_bot - rad_b, rad_b, rad_b, 0, 90, 5) +
                arc_pts(-bot_w + rad_b, y_bot - rad_b, rad_b, rad_b, 90, 180, 5)
            )
            c.poly(TT(torso_pts), kemeja, ow, OUT)
            # 2-band cel shading bersih (di sisi belakang saat miring, atau kanan saat depan)
            if turn >= 0.25:
                c.poly(TT([
                    (-top_w + 2, y_top + rad_t), (-top_w + rad_t * 0.4, y_top + 3),
                    (-top_w * 0.22, y_top + 2), (-bot_w * 0.18, y_bot - 2),
                    (-bot_w + rad_b * 0.4, y_bot - 2), (-bot_w + 2, y_bot - rad_b),
                ]), gelap(kemeja, 0.11))
            else:
                c.poly(TT([
                    (top_w * 0.42, y_top + 2), (top_w - rad_t * 0.4, y_top + 3),
                    (top_w - 2, y_top + rad_t), (bot_w - 2, y_bot - rad_b),
                    (bot_w - rad_b * 0.4, y_bot - 2), (bot_w * 0.38, y_bot - 2),
                ]), gelap(kemeja, 0.10))
            c.poly(TT(torso_pts), None, ow, OUT)
        if p.get("kemeja_garis"):
            gc = warna(p["kemeja_garis"], BIRU)
            for yy in (-220, -198, -176):
                if yy < hy - 14:
                    c.line(TT([(-33 * bw, yy), (33 * bw, yy)]), gc, 5.2 * s, False)
        if p.get("saku_dada") and not side_prof:
            # saku kemeja kiri (persis gambar 2 Arka)
            sx0, sx1, sy0, sy1 = cx_t + 16, cx_t + 42, SHOULDER_Y + 34, SHOULDER_Y + 62
            c.poly(TT([(sx0, sy0), (sx1, sy0), (sx1, sy1 - 5), ((sx0 + sx1) / 2, sy1), (sx0, sy1 - 5)]),
                   terang(kemeja, 0.08), ow * .65, OUT)
        if p.get("sabuk") and not p.get("jaket"):
            sbc = warna(p["sabuk"], (72, 62, 66))
            bot_w = 33.0 * hipb
            c.poly(TT([(-bot_w * 0.94, hy - 16), (bot_w * 0.94, hy - 16),
                       (bot_w * 0.94, hy - 2), (-bot_w * 0.94, hy - 2)]), sbc, ow * .72, OUT)
            c.poly(TT([(cx_t - 9, hy - 17), (cx_t + 9, hy - 17),
                       (cx_t + 9, hy - 1), (cx_t - 9, hy - 1)]), (196, 202, 214), ow * .68, OUT)
        if p.get("perisai_dada"):
            by = SHOULDER_Y + 46
            c.poly(TT([(cx_t, by - 20), (cx_t + 20, by - 12), (cx_t + 16, by + 9), (cx_t, by + 22), (cx_t - 16, by + 9), (cx_t - 20, by - 12)]), PUTIH, ow * .8, OUT)
            c.line(TT([(cx_t, by - 9), (cx_t, by + 9)]), BIRU, 5.0 * s, False)
            c.line(TT([(cx_t - 9, by), (cx_t + 9, by)]), BIRU, 5.0 * s, False)
        # ---- leher (pendek & rapi di antara bahu dan dagu, memberi proporsi mirip 3D-stickman)
        if not p.get("hijab") and not p.get("kaos_chibi"):
            neck_c = kulit
            nx_c = 4.0 * turn
            c.poly(TT([(nx_c - 13.5, SHOULDER_Y - 24), (nx_c + 13.5, SHOULDER_Y - 24),
                       (nx_c + 14.5, SHOULDER_Y + 6), (nx_c, SHOULDER_Y + 10), (nx_c - 14.5, SHOULDER_Y + 6)]),
                   neck_c, ow * .82, OUT)
            c.poly(TT([(nx_c - 12.5, SHOULDER_Y - 22), (nx_c + 12.5, SHOULDER_Y - 22),
                       (nx_c + 12.5, SHOULDER_Y - 8), (nx_c - 12.5, SHOULDER_Y - 12)]),
                   gelap(neck_c, 0.14))
        # krah + dasi (dasi kupu-kupu menggantikan krah/dasi biasa)
        def _draw_bowtie(bc):
            by = SHOULDER_Y + (14 if p.get("kaos_chibi") else 11)
            k_bt = 1.38 if p.get("kaos_chibi") else 1.15
            lw_b = 19.0 * k_bt * (1.0 - 0.10 * turn)
            rw_b = 19.0 * k_bt * (1.0 - 0.22 * turn)
            hh_b = 10.0 * k_bt
            c.blob(TT([(cx_t - 3, by - 3), (cx_t - lw_b, by - hh_b), (cx_t - lw_b - 2.5, by), (cx_t - lw_b, by + hh_b), (cx_t - 3, by + 3)]), bc, ow * .78, OUT, n=4)
            c.blob(TT([(cx_t + 3, by - 3), (cx_t + rw_b, by - hh_b), (cx_t + rw_b + 2.5, by), (cx_t + rw_b, by + hh_b), (cx_t + 3, by + 3)]), gelap(bc, .10), ow * .78, OUT, n=4)
            c.ell(*T(cx_t, by), 7.8 * s, 7.8 * s, gelap(bc, .16), ow * .75, OUT)

        if not p.get("blazer"):
            # tampilkan kerah kemeja putih di bawah dasi kupu bila krah=True (gaya smart student Ghibli)
            if p.get("krah", True):
                c.poly(TT([(cx_t - 4, SHOULDER_Y - 2), (cx_t - 22, SHOULDER_Y - 1), (cx_t - 13, SHOULDER_Y + 20)]), PUTIH, ow * .78, OUT)
                c.poly(TT([(cx_t + 4, SHOULDER_Y - 2), (cx_t + 22, SHOULDER_Y - 1), (cx_t + 13, SHOULDER_Y + 20)]), PUTIH, ow * .78, OUT)
            if p.get("dasi_kupu"):
                _draw_bowtie(warna(p.get("dasi"), HITAM))
            elif dasi:
                c.poly(TT([(cx_t - 4.5, SHOULDER_Y + 17), (cx_t + 4.5, SHOULDER_Y + 17),
                           (cx_t + 10.5, SHOULDER_Y + 58), (cx_t, SHOULDER_Y + 74), (cx_t - 10.5, SHOULDER_Y + 58)]), dasi, ow * .8, OUT)
                c.poly(TT([(cx_t - 7.0, SHOULDER_Y + 8), (cx_t + 7.0, SHOULDER_Y + 8),
                           (cx_t + 5.0, SHOULDER_Y + 17), (cx_t - 5.0, SHOULDER_Y + 17)]), dasi, ow * .8, OUT)
                if p.get("dasi_klip"):
                    c.line(TT([(cx_t - 7.5, SHOULDER_Y + 46), (cx_t + 7.5, SHOULDER_Y + 46)]), (192, 198, 214), 4.0 * s)
            elif p.get("kancing", True):
                for yy in (-224, -202, -180):
                    if yy < hy - 16:
                        c.ell(*T(cx_t, yy), 3.1 * s, 3.1 * s, OUT)
        elif p.get("dasi_kupu"):
            _draw_bowtie(warna(p.get("dasi"), HITAM))
        if st.get("tali_ransel"):
            for sgn in (-1, 1):
                c.line(TT([(sgn * 25 * bw, SHOULDER_Y), (sgn * 25 * bw, hy - 12)]), warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU, 8.5 * s, False)

        # ---- hijab: drape di bawah dagu
        if p.get("hijab"):
            hj, hjd = warna(p["hijab"]), warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
            hx_sh = -6.0 * turn
            if p.get("hijab_gaya") == "modern":
                c.blob(TT([(hx_sh - 86, -338), (hx_sh - 94, -282), (hx_sh - 76, -244), (hx_sh - 42, -226), (cx_t * 0.4, -210),
                           (hx_sh + 42, -226), (hx_sh + 76, -244), (hx_sh + 94, -282), (hx_sh + 86, -338), (hx_sh, -398)]),
                       hj, ow, OUT, n=7)
                c.curve(TT([(hx_sh - 66, -254), (hx_sh - 30, -236), (cx_t * 0.4, -224), (hx_sh + 30, -236), (hx_sh + 66, -254)]), hjd, 3.4 * s)
                c.curve(TT([(hx_sh - 46, -234), (hx_sh - 14, -220), (hx_sh + 18, -224)]), hjd, 2.8 * s)
                c.curve(TT([(hx_sh - 78, -278), (hx_sh - 54, -256)]), hjd, 2.6 * s)
                c.curve(TT([(hx_sh + 78, -278), (hx_sh + 54, -256)]), hjd, 2.6 * s)
            else:
                c.blob(TT([(hx_sh - 98, -346), (hx_sh - 106, -288), (hx_sh - 88, -236), (hx_sh - 46, -206), (cx_t * 0.4, -194), (hx_sh + 46, -206), (hx_sh + 88, -236), (hx_sh + 106, -288), (hx_sh + 98, -346), (hx_sh, -394)]),
                       hj, ow, OUT, n=7)
                c.curve(TT([(hx_sh - 62, -244), (hx_sh - 26, -228), (cx_t * 0.4, -218)]), hjd, 4.4 * s)
                c.curve(TT([(hx_sh + 62, -244), (hx_sh + 26, -228), (cx_t * 0.4, -218)]), hjd, 4.4 * s)
                c.curve(TT([(hx_sh - 84, -274), (hx_sh - 52, -250)]), hjd, 3.6 * s)
                c.curve(TT([(hx_sh + 84, -274), (hx_sh + 52, -250)]), hjd, 3.6 * s)
            if dasi and not p.get("dasi_kupu"):
                c.poly(TT([(cx_t - 3.8, -196), (cx_t + 3.8, -196), (cx_t + 8.5, -168), (cx_t, -156), (cx_t - 8.5, -168)]), dasi, ow * .7, OUT)
                c.poly(TT([(cx_t - 5.5, -206), (cx_t + 5.5, -206), (cx_t + 4.0, -196), (cx_t - 4.0, -196)]), dasi, ow * .7, OUT)

        # ---- lengan depan / normal (di depan torso)
        for side, key, a, e, hk in mid_arms:
            hands[side] = self._arm(c, T, s, fl, key, a, e, hk, kemeja, ow, dy, turn)

        # ---- kepala
        self._head(c, st, T, s, fl, ow, turn)

        # ---- lengan terangkat / dekat wajah (di depan kepala & rambut)
        for side, key, a, e, hk in front_arms:
            hands[side] = self._arm(c, T, s, fl, key, a, e, hk, kemeja, ow, dy, turn)

        # ---- benda di tangan
        return hands

    # ------------------------------------------------------------ kaki
    def _legs(self, st, T, sit, turn=0.0):
        stance = st.get("legs", "stand")
        ph, amp = st.get("phase", 0.0), st.get("amp", 0.0)
        side_prof = turn >= 0.80
        kl = float(self.p.get("kaki_lebar", 1.15)) * (0.28 if side_prof else (1.0 - 0.24 * turn))
        hy = float(self.p.get("hip_y", -144.0))
        feet, knees, hips = [], [], []
        for sgn in (-1, 1):
            hx = sgn * (3.5 if side_prof else 17.5 * kl)
            fx, fy = sgn * (10.0 if side_prof else 20.5 * kl), (-4.5 * turn if sgn < 0 else 0.0)
            knee_bend = 0.0
            if stance == "walk" and amp > 0.01:
                q = ph + (0 if sgn < 0 else math.pi)
                if side_prof:
                    # langkah samping sejati: pinggul sejajar, kaki ayun maju-mundur + lutut menekuk ke depan (+x)
                    hx = sgn * 3.0
                    stride = math.sin(q) * 0.48 * amp
                    fx = hx + math.sin(stride) * 105.0
                    lift = max(0.0, -math.cos(q)) * 18.0 * amp
                    fy = -lift + (-3.0 if sgn < 0 else 0.0)
                    knee_bend = (14.0 + 16.0 * max(0.0, math.sin(q))) * min(1.0, amp)
                else:
                    hx = sgn * 17.5 * kl * (1.0 - 0.18 * min(1.0, amp))
                    stride = math.sin(q) * 0.42 * amp
                    fx = hx + math.sin(stride) * 118.0
                    fy = -max(0.0, -math.cos(q)) * 16.0 * amp
            elif stance == "wide":
                fx = sgn * 48 * kl
            hipw = T(hx, hy)
            f_stand, f_sit = T(fx, fy, True), T(hx + 92, 0.0, True)
            foot = (lerp(f_stand[0], f_sit[0], sit), lerp(f_stand[1], f_sit[1], sit))
            # lutut sedikit menekuk ke arah maju (+x lokal) saat side-profile berjalan agar langkah alami
            kx_stand = (hx + fx) * 0.5 + knee_bend
            ky_stand = (hy + fy) * 0.5
            k_stand = T(kx_stand, ky_stand)
            k_sit = T(hx + 84, hy + SIT_DROP, True)
            knee = (lerp(k_stand[0], k_sit[0], sit), lerp(k_stand[1], k_sit[1], sit))
            feet.append(foot)
            knees.append(knee)
            hips.append(hipw)
        return feet, knees, hips

    # ------------------------------------------------------------ lengan
    def _arm(self, c, T, s, fl, sgn, a, e, hk, sleeve, ow, dy, turn=0.0):
        ar, br = math.radians(a), math.radians(a + e)
        # tangan masuk saku celana saat pose diam/santai (persis gaya referensi chibi)
        saku = bool(self.p.get("tangan_saku")) and hk == "m" and turn < 0.25 and a <= 22 and -5 <= e <= 20
        if saku:
            a, e = 10.0, -26.0
            ar, br = math.radians(a), math.radians(a + e)
        bahu = float(self.p.get("bahu_x", 47.0)) - 3.5
        side_prof = turn >= 0.80
        if side_prof:
            # side-profile: kedua bahu berada di dekat sumbu tengah tubuh, lengan ayun maju-mundur (+x/-x)
            bahu_x = -3.0 if sgn < 0 else 2.0
            sh = (bahu_x, SHOULDER_Y + 13)
            el = (sh[0] + math.sin(ar) * UP_ARM, sh[1] + math.cos(ar) * UP_ARM)
            hd = (el[0] + math.sin(br) * FORE_ARM, el[1] + math.cos(br) * FORE_ARM)
        else:
            if turn >= 0.25:
                bahu_x = sgn * bahu * (0.62 if sgn < 0 else 0.72) + (6.0 * turn if sgn > 0 else 10.0 * turn)
                a_eff = a if sgn > 0 else (a + 6.0 * turn)
                ar, br = math.radians(a_eff), math.radians(a_eff + e)
            else:
                bahu_x = sgn * bahu
            sh = (bahu_x, SHOULDER_Y + 12)
            el = (sh[0] + sgn * math.sin(ar) * UP_ARM, sh[1] + math.cos(ar) * UP_ARM)
            hd = (el[0] + sgn * math.sin(br) * FORE_ARM, el[1] + math.cos(br) * FORE_ARM)
        S, E, H = T(*sh), T(*el), T(*hd)
        tebal = bool(self.p.get("lengan_tebal", True))
        lb = float(self.p.get("lengan_besar", 0.94)) if tebal else 1.0
        tb = float(self.p.get("tangan_besar", 0.94))
        skin = warna(self.p.get("kulit"), PUTIH)
        slv_c = gelap(sleeve, 0.12) if (turn >= 0.25 and sgn < 0) else sleeve
        skin_c = gelap(skin, 0.08) if (turn >= 0.25 and sgn < 0) else skin
        arm_ow = 3.8 * s
        # lengan kartun ramping & halus (tube kulit / lengan panjang blazer)
        if self.p.get("lengan_panjang"):
            arm_w = 16.8 * lb
            if self.p.get("manset") or self.p.get("blazer"):
                dx, dy_ = H[0] - E[0], H[1] - E[1]
                dl = max(1e-5, math.hypot(dx, dy_))
                ux, uy = dx / dl, dy_ / dl
                r_hand = 14.0 * tb * s
                c0 = (H[0] - ux * (r_hand + 11.5 * s), H[1] - uy * (r_hand + 11.5 * s))
                c1 = (H[0] - ux * (r_hand + 1.5 * s), H[1] - uy * (r_hand + 1.5 * s))
                c.tube(c0, c1, (arm_w - 3.2) * s, PUTIH, 3.4 * s, OUT)
                H_slv = (H[0] - ux * (r_hand + 17.5 * s), H[1] - uy * (r_hand + 17.5 * s))
                c.line([S, E, H_slv], OUT, (arm_w + 2 * 3.8) * s)
                c.line([S, E, H_slv], slv_c, arm_w * s)
            else:
                c.line([S, E, H], OUT, (arm_w + 2 * 3.8) * s)
                c.line([S, E, H], slv_c, arm_w * s)
        else:
            if tebal:
                arm_w = 14.2 * lb
                S_arm = T(sh[0] + (el[0] - sh[0]) * 0.24, sh[1] + (el[1] - sh[1]) * 0.24) if self.p.get("kaos_chibi") else S
                if saku:
                    c.curve([S_arm, E, H], OUT, (arm_w + 2 * 3.8) * s, n=6)
                    c.curve([S_arm, E, H], skin_c, arm_w * s, n=6)
                else:
                    c.line([S_arm, E, H], OUT, (arm_w + 2 * 3.8) * s)
                    c.line([S_arm, E, H], skin_c, arm_w * s)
            else:
                c.line([S, E, H], OUT, 6.0 * s)
            # lengan kaos pendek / lengan kemeja digulung sampai siku (gaya Arka gambar 2)
            sl_k = 0.72 if self.p.get("lengan_gulung") else 0.42
            sl = (sh[0] + (el[0] - sh[0]) * sl_k, sh[1] + (el[1] - sh[1]) * sl_k)
            slv_w = (19.5 * lb if self.p.get("lengan_gulung") else (17.5 * lb if tebal else 16.0)) * s
            if self.p.get("kaos_chibi") and not self.p.get("lengan_gulung"):
                self._sleeve_chibi(c, T, s, sh, el, slv_c, arm_ow)
            else:
                c.tube(S, T(*sl), slv_w, slv_c, arm_ow)
            if self.p.get("lengan_gulung"):
                # lipatan manset gulung di ujung lengan siku
                sl2 = (sh[0] + (el[0] - sh[0]) * (sl_k + 0.14), sh[1] + (el[1] - sh[1]) * (sl_k + 0.14))
                c.tube(T(*sl), T(*sl2), slv_w * 1.08, terang(slv_c, 0.10), arm_ow * .85)
        # tangan berjari kartun 2D rapi (2-pass outline menyatu antara telapak & jari)
        dirv = (H[0] - E[0], H[1] - E[1])
        ang = math.atan2(dirv[1], dirv[0])
        if saku:
            # pergelangan masuk ke saku celana: tutup tangan dengan kain + garis bukaan saku miring
            bc = warna(self.p.get("bawah_warna"), (160, 164, 170))
            hx_, hy_ = hd
            pk = [(hx_ - sgn * 11, hy_ - 4), (hx_ + sgn * 11, hy_ - 10), (hx_ + sgn * 10, hy_ + 9), (hx_ - sgn * 10, hy_ + 9)]
            c.blob([T(*q) for q in pk], bc, 0, n=3)
            c.curve([T(hx_ - sgn * 13, hy_ - 2), T(hx_, hy_ - 8), T(hx_ + sgn * 13, hy_ - 11)], OUT, 2.8 * s)
        else:
            self._hand(c, H, ang, s, tb, sgn, fl, hk, skin_c)
        return {"pos": H, "ang": ang, "elbow": E}

    def _sleeve_chibi(self, c, T, s, sh, el, col, ow_):
        """Lengan kaos pendek rapi lurus-halus (tidak ketekuk saat lengan turun maupun saat menunjuk!)."""
        dx, dy = el[0] - sh[0], el[1] - sh[1]
        l = max(1e-6, math.hypot(dx, dy))
        ux, uy = dx / l, dy / l
        nx, ny = -uy, ux
        if abs(sh[0] + nx) < abs(sh[0] - nx):
            nx, ny = -nx, -ny
        # pangkal lengan kaos membulat rapi di bahu, turun lurus ke manset tanpa garis tekukan di dada
        b_in = (sh[0] - ux * 8 - nx * 11, sh[1] - uy * 8 - ny * 8)
        b_out = (sh[0] - ux * 4 + nx * 12, sh[1] - uy * 4 + ny * 11)
        cf_out = (sh[0] + ux * 34 + nx * 17, sh[1] + uy * 34 + ny * 17)
        cf_in = (sh[0] + ux * 33 - nx * 11, sh[1] + uy * 33 - ny * 11)
        P = [T(*q) for q in (b_in, b_out, cf_out, cf_in)]
        c.poly(P, col)
        # tutup pangkal bahu dengan elips warna kaos agar sambungan bahu selalu bulat-rapi di segala sudut pose!
        c.ell(*T(sh[0] - ux * 3, sh[1] - uy * 2), 13.5 * s, 13.5 * s, col)
        c.line([P[1], P[2], P[3]], OUT, ow_)
        c.line([P[3], T(sh[0] + ux * 18 - nx * 11, sh[1] + uy * 18 - ny * 11)], OUT, ow_ * 0.85)
        lum = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
        hem_c = terang(col, 0.15) if lum < 90 else gelap(col, 0.20)
        c.line([T(cf_out[0] - ux * 4.5, cf_out[1] - uy * 4.5),
                T(cf_in[0] - ux * 4.5, cf_in[1] - uy * 4.5)], hem_c, 1.8 * s)

    def _kaos_chibi(self, c, TT, s, kemeja, kulit, hy, turn, side_prof):
        """Kaos rapi bersih tanpa garis ketekuk di dada/pinggang + leher pendek mungil."""
        k = 0.70 if side_prof else (1.0 - 0.10 * turn)
        yb = hy - 18.0
        oc_f = (74, 52, 46)
        # leher pendek mungil dengan bayangan dagu hangat
        neck_pts = [(-14.0, -274), (14.0, -274), (15.0, -250), (0, -245), (-15.0, -250)]
        c.poly(TT(neck_pts), kulit, 2.6 * s, oc_f)
        c.poly(TT([(-13.5, -272), (13.5, -272), (14.0, -257), (-2, -259), (-13.5, -262)]), (228, 160, 146))
        # bodi kaos bersih-rapi: bahu mulus dan sisi badan lurus-halus (TIDAK melekuk/ketekuk!)
        pts = [
            (-19 * k, -256), (0, -247), (19 * k, -256),
            (44 * k, -251), (52 * k, -238), (52 * k, -206),
            (52 * k, yb - 4), (32 * k, yb + 2),
            (0, yb + 3), (-32 * k, yb + 2), (-52 * k, yb - 4),
            (-52 * k, -206), (-52 * k, -238), (-44 * k, -251),
        ]
        c.blob(TT(pts), kemeja, 3.2 * s, OUT, n=6)
        # shading cel halus di sisi kanan kaos (tanpa garis lipatan ketekuk di dada!)
        c.poly(TT([(26 * k, -253), (44 * k, -250), (51 * k, -237), (51 * k, yb - 5),
                   (36 * k, yb + 1), (34 * k, -200)]), gelap(kemeja, 0.18))
        lum = 0.299 * kemeja[0] + 0.587 * kemeja[1] + 0.114 * kemeja[2]
        rib = terang(kemeja, 0.16) if lum < 90 else gelap(kemeja, 0.18)
        c.curve(TT([(-20 * k, -255), (0, -244), (20 * k, -255)]), rib, 2.8 * s)
        c.blob(TT(pts), None, 3.2 * s, OUT, n=6)

    def _hair_back_ref(self, c, HH, s, hc, sh):
        """Kembalikan bentuk rambut terbaik pilihan user (af_cy=-44, ikal bulat mengembang & sulur helai lepas)."""
        oc_h = (16, 12, 14)
        ow_h = 2.6 * s
        af_cy = -44
        c_deep = (14, 10, 12)
        c_mid = (78, 54, 46)
        c_bright = (128, 94, 80)
        c_fine = (168, 130, 114)
        outer_puffs = []
        dr_pat = (0, 8, -1, 10, 3, 11, 0, 9, 5, 12, 1, 10, 4, 12, 0, 9, 5, 11, 1, 10, 3, 9, -1, 6)
        pr_pat = (21, 25, 21, 26, 23, 27, 22, 26, 24, 27, 22, 26, 24, 27, 22, 26, 24, 27, 23, 26, 21, 25, 21, 20)
        for i in range(24):
            a = 142 + (398 - 142) * i / 23.0
            rad_a = math.radians(a)
            px = sh + math.cos(rad_a) * (136 + dr_pat[i])
            py = af_cy + math.sin(rad_a) * (114 + dr_pat[i])
            outer_puffs.append((px, py, pr_pat[i], a))

        # pass 1: sulur-sulur helai ikal lepas mencuat di luar tepi afro
        for i in range(22):
            a = 144 + (396 - 144) * i / 21.0
            rad_a = math.radians(a)
            dist_w = 152 + (8 if i % 2 == 0 else 2)
            wx = sh + math.cos(rad_a) * dist_w
            wy = af_cy + math.sin(rad_a) * (dist_w * 0.85)
            wr = 11.5 + (3.5 if i % 3 == 0 else 0.0)
            a_start = int(a - 125) if i % 2 == 0 else int(a - 35)
            loop_pts = arc_pts(wx, wy, wr, wr * 0.92, a_start, a_start + 245, 12)
            c.line(HH(loop_pts), oc_h, 2.6 * s)
            c.line(HH(loop_pts[2:-2]), c_bright, 1.4 * s)

        # pass 2: outline dasar afro + gumpalan ikal tepi
        c.ell(*HH([(sh, af_cy)])[0], 136 * s + ow_h, 114 * s + ow_h, oc_h)
        for px, py, pr, _ in outer_puffs:
            c.ell(*HH([(px, py)])[0], pr * s + ow_h, pr * s + ow_h, oc_h)

        # pass 3: isi warna dasar rambut hitam-espresso pekat + helai spiral di tepi luar
        c.ell(*HH([(sh, af_cy)])[0], 136 * s, 114 * s, hc)
        for px, py, pr, a in outer_puffs:
            c.ell(*HH([(px, py)])[0], pr * s, pr * s, hc)
            sa = int(a + 25)
            p_arc = arc_pts(px, py, pr * 0.78, pr * 0.76, sa, sa + 210, 11)
            c.line(HH(p_arc), c_mid, 2.4 * s)
            c.line(HH(p_arc[2:-2]), c_bright, 1.4 * s)

        # pass 4: cincin ikal luar di belakang telinga
        for k in range(19):
            ang_d = 144 + (396 - 144) * k / 18.0
            rad = math.radians(ang_d)
            cx_c = sh + math.cos(rad) * 120
            cy_c = af_cy + math.sin(rad) * 100
            cr = 18.5
            c.ell(*HH([(cx_c, cy_c)])[0], (cr + 1.5) * s, (cr + 1.5) * s, c_deep)
            c.ell(*HH([(cx_c, cy_c)])[0], cr * s, cr * s, hc)
            sa = int(ang_d + (k * 47) % 120 - 60)
            arc1 = arc_pts(cx_c, cy_c, cr * 0.84, cr * 0.80, sa, sa + 205, 12)
            arc2 = arc_pts(cx_c, cy_c, cr * 0.60, cr * 0.58, sa + 35, sa + 215, 10)
            c.line(HH(arc1), c_mid, 2.6 * s)
            c.line(HH(arc1[2:-2]), c_bright, 1.6 * s)
            c.line(HH(arc2), c_mid, 1.9 * s)
            if k % 2 == 0:
                arc3 = arc_pts(cx_c, cy_c, cr * 0.88, cr * 0.84, sa + 40, sa + 145, 8)
                c.line(HH(arc3), c_fine, 1.2 * s)

    def _hair_front_ref(self, c, HH, s, hc):
        """Kembalikan rambut depan persis gambar pilihan user (media_1795797796870_ad975d11.png)."""
        oc_h = (16, 12, 14)
        af_cy = -44
        c_deep = (14, 10, 12)
        c_mid = (78, 54, 46)
        c_bright = (128, 94, 80)
        c_fine = (168, 130, 114)

        cap_outer = arc_pts(0, -42, 124, 104, 174, 366, 24)
        forehead_arch = list(reversed(arc_pts(0, -14, 80, 38, 186, 354, 16)))
        c.poly(HH(cap_outer + forehead_arch), hc)

        fringe_curls = [
            (-82, -16, 17), (-74, -34, 19), (-56, -46, 20),
            (-32, -52, 20), (-6, -50, 20), (20, -52, 20),
            (46, -48, 20), (68, -36, 19), (80, -18, 17),
        ]
        for bx, by, br in fringe_curls:
            c.ell(*HH([(bx, by + 5)])[0], br * 0.88 * s, br * 0.70 * s, (226, 182, 160, 115))
        for bx, by, br in fringe_curls:
            c.ell(*HH([(bx, by)])[0], br * s, br * 0.90 * s, hc, 2.0 * s, oc_h)

        rings = [
            (96, 80, 13, 17.5, 170, 370, 11),
            (68, 56, 9, 16.5, 178, 362, 23),
        ]
        for idx_r, (rx_r, ry_r, n_c, cr, a0_r, a1_r, ph_r) in enumerate(rings):
            for k in range(n_c):
                ang_d = a0_r + (a1_r - a0_r) * k / max(1, n_c - 1) + ((k % 2) * 4 - 2)
                rad = math.radians(ang_d)
                cx_c = math.cos(rad) * rx_r
                cy_c = af_cy + math.sin(rad) * ry_r
                c.ell(*HH([(cx_c, cy_c)])[0], (cr + 1.5) * s, (cr + 1.5) * s, c_deep)
                c.ell(*HH([(cx_c, cy_c)])[0], cr * s, cr * s, hc)
                sa = int(ang_d + ph_r + (k * 47) % 120 - 60)
                arc1 = arc_pts(cx_c, cy_c, cr * 0.84, cr * 0.80, sa, sa + 205, 12)
                arc2 = arc_pts(cx_c, cy_c, cr * 0.62, cr * 0.60, sa + 35, sa + 215, 10)
                c.line(HH(arc1), c_mid, 2.6 * s)
                c.line(HH(arc1[2:-2]), c_bright, 1.6 * s)
                c.line(HH(arc2), c_mid, 1.9 * s)
                if (k + idx_r) % 2 == 0:
                    arc3 = arc_pts(cx_c, cy_c, cr * 0.88, cr * 0.84, sa + 40, sa + 145, 8)
                    c.line(HH(arc3), c_fine, 1.2 * s)

        for idx_f, (bx, by, br) in enumerate(fringe_curls):
            sa = 20 + (idx_f * 53) % 140
            f_arc1 = arc_pts(bx, by, br * 0.78, br * 0.76, sa, sa + 210, 11)
            f_arc2 = arc_pts(bx, by, br * 0.52, br * 0.52, sa + 50, sa + 220, 9)
            c.line(HH(f_arc1), c_mid, 2.4 * s)
            c.line(HH(f_arc1[2:-2]), c_bright, 1.4 * s)
            c.line(HH(f_arc2), c_deep, 2.0 * s)

        forehead_wisps = [
            (-64, -30, 10, 15, 225), (-38, -40, 11, 5, 215), (-10, -40, 12, -15, 205),
            (16, -40, 11, -25, 195), (44, -38, 10, -10, 210), (-76, -12, 9, 30, 230), (76, -12, 9, -50, 150),
        ]
        for wx, wy, wr, a0_w, a1_w in forehead_wisps:
            w_pts = arc_pts(wx, wy, wr, wr * 0.9, a0_w, a1_w, 11)
            c.line(HH(w_pts), oc_h, 2.1 * s)
            c.line(HH(w_pts[1:-1]), c_bright, 1.15 * s)

    def _eye_ref(self, c, HH, s, ex_, eye_y, i, eyes, blink, turn, lx_, ly_):
        """Mata Chibi Cowok Maskulin Hitam-Tajam: proporsi horizontal tegas (half-lidded sharp male eye), iris hitam-obsidian pekat, kilau tajam."""
        sc = 1.10 if eyes == "wide" else 1.0
        ew = 19.2 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
        eh = (13.4 * 0.50 if eyes == "half" else 13.4 * sc) * (1.0 - 0.92 * blink)
        cy = eye_y + 2.0
        sg = -1 if i == 0 else 1
        line_c = (20, 16, 18)
        if eh > 2.6:
            # bentuk mata cowok maskulin (sudut poligonal tegas, atas agak mendatar-menukik ke dalam, bukan bulat cewek!)
            p_in = (ex_ - sg * ew, cy + 1.2)
            p_top_in = (ex_ - sg * ew * 0.52, cy - eh * 0.78)
            p_top_out = (ex_ + sg * ew * 0.48, cy - eh * 0.96)
            p_out = (ex_ + sg * ew, cy - 1.2)
            p_bot_out = (ex_ + sg * ew * 0.56, cy + eh * 0.92)
            p_bot_in = (ex_ - sg * ew * 0.50, cy + eh * 0.92)
            eye_poly = [p_in, p_top_in, p_top_out, p_out, p_bot_out, p_bot_in]
            c.poly(HH(eye_poly), (250, 250, 248))

            # iris HITAM-OBSIDIAN maskulin pekat (bagian atas hitam pekat, sabit bawah charcoal-steel gelap)
            ir_w = 12.8 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
            ir_h = min(eh * 0.96, 12.8 * sc)
            ix = ex_ + lx_ * 4.0 + 2.0 * turn
            iy = cy + ly_ * 1.5
            c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 20)), (22, 22, 26), 1.2 * s, line_c)
            # sabit bawah abu-charcoal dingin (memberi dimensi mata hitam anime tanpa terkesan imut/cewek)
            c.poly(HH(_ellpts(ix, iy + ir_h * 0.30, ir_w * 0.72, ir_h * 0.46, 16)), (72, 76, 86))
            # pupil inti hitam legam
            c.poly(HH(_ellpts(ix, iy - ir_h * 0.05, ir_w * 0.48, ir_h * 0.48, 14)), (8, 8, 10))
            # bayangan sklera & puncak iris di bawah kelopak atas (memberi tatapan cowok tajam/fokus!)
            c.poly(HH([
                p_in, p_top_in, p_top_out, p_out,
                (ex_ + sg * ew * 0.85, cy - eh * 0.38),
                (ex_ - sg * ew * 0.85, cy - eh * 0.28),
            ]), (18, 18, 22, 115))
            # kilau putih kecil-tajam (bukan bulatan besar shoujo!)
            c.poly(HH(_ellpts(ix - ir_w * 0.36, iy - ir_h * 0.24, 2.8, 2.3, 10)), PUTIH)
            c.poly(HH(_ellpts(ix + ir_w * 0.34, iy + ir_h * 0.32, 1.3, 1.3, 8)), (235, 240, 248))
            # tutup bersih area di atas garis kelopak miring dengan warna kulit
            c.poly(HH([
                (ex_ - sg * (ew + 2), cy - eh * 0.32),
                (ex_ - sg * (ew + 2), cy - eh * 1.25),
                (ex_ + sg * (ew + 2), cy - eh * 1.25),
                p_top_out, p_top_in,
            ]), warna(self.p.get("kulit"), (254, 232, 214)))
            # garis kelopak bawah tipis tegas di tengah-luar
            c.line(HH([p_bot_in, p_bot_out, p_out]), (96, 76, 68), 1.6 * s)

        # kelopak mata atas hitam-tegas lurus-miring (sudut dalam rendah, sudut luar naik tajam)
        lid_pts = [
            (ex_ - sg * (ew + 0.8), cy + 0.5),
            (ex_ - sg * ew * 0.50, cy - eh * 0.78),
            (ex_ + sg * ew * 0.48, cy - eh * 0.96),
            (ex_ + sg * (ew + 1.8), cy - 1.5),
        ]
        c.line(HH(lid_pts), line_c, 3.5 * s)
        if eh > 5.0:
            # garis lipatan kelopak atas (double-eyelid crease) lurus maskulin
            c.line(HH([
                (ex_ - sg * ew * 0.52, cy - eh * 0.98),
                (ex_ + sg * ew * 0.46, cy - eh * 1.16),
            ]), (116, 86, 76), 1.5 * s)

    def _hand(self, c, H, ang, s, tb, sgn, fl, hk, skin):
        """Tangan kartun berjari-jari rapi: 'm' terbuka (4 jari), 'p' menunjuk, 't' jempol, 'f' mengepal."""
        sc = s * tb
        hx, hy = H
        ux, uy = math.cos(ang), math.sin(ang)
        # sisi dalam (arah jempol): menghadap ke arah tubuh / wajah secara alami
        ts = -sgn * fl
        vx, vy = -uy * ts, ux * ts

        def pt(fwd, side):
            return (hx + ux * fwd * sc + vx * side * sc, hy + uy * fwd * sc + vy * side * sc)

        how = 3.2 * s
        if hk == "p":
            # telunjuk lurus memanjang + jempol terbuka ringan + 2 jari lain terlipat
            palm_c = pt(3.5, -1.0)
            idx_a, idx_b = pt(6.0, 2.2), pt(24.5, 2.8)
            th_a, th_b = pt(2.0, 6.5), pt(10.5, 13.0)
            curl_pts = [pt(9.5, -3.5), pt(8.0, -8.5)]
            # pass 1: outline
            c.ell(palm_c[0], palm_c[1], 11.2 * sc + how, 10.2 * sc + how, OUT)
            c.line([idx_a, idx_b], OUT, 7.6 * sc + 2 * how)
            c.line([th_a, th_b], OUT, 6.8 * sc + 2 * how)
            for cp in curl_pts:
                c.ell(cp[0], cp[1], 4.6 * sc + how, 4.6 * sc + how, OUT)
            # pass 2: isi kulit
            c.ell(palm_c[0], palm_c[1], 11.2 * sc, 10.2 * sc, skin)
            c.line([idx_a, idx_b], skin, 7.6 * sc)
            c.line([th_a, th_b], skin, 6.8 * sc)
            for cp in curl_pts:
                c.ell(cp[0], cp[1], 4.6 * sc, 4.6 * sc, skin, how * 0.65, OUT)
        elif hk == "t":
            # jempol ke atas (thumbs up) + kepalan 3 jari terlipat rapi
            palm_c = pt(4.0, 0.0)
            th_a = (hx, hy - 4.0 * sc)
            th_b = (hx + sgn * fl * 1.5 * sc, hy - 22.5 * sc)
            # pass 1: outline
            c.ell(palm_c[0], palm_c[1], 12.0 * sc + how, 11.0 * sc + how, OUT)
            c.line([th_a, th_b], OUT, 8.2 * sc + 2 * how)
            # pass 2: isi kulit
            c.ell(palm_c[0], palm_c[1], 12.0 * sc, 11.0 * sc, skin)
            c.line([th_a, th_b], skin, 8.2 * sc)
            # 2 garis ruas jari terlipat di sisi depan kepalan
            for k in (-3.5, 2.5):
                c.line([pt(6.0, k - 2.0), pt(13.5, k - 2.0)], OUT, 2.2 * s)
        elif hk == "f":
            # kepalan tangan rapi dengan ruas jari & jempol melintang
            palm_c = pt(4.0, 0.0)
            c.ell(palm_c[0], palm_c[1], 12.4 * sc, 11.2 * sc, skin, how, OUT)
            for k in (-4.8, 0.0, 4.8):
                c.line([pt(5.5, k), pt(13.0, k)], OUT, 2.1 * s)
            c.line([pt(0.0, 8.5), pt(8.5, 4.5)], OUT, 2.6 * s)
        else:
            # tangan terbuka santai: telapak + jempol + 3 jari kartun halus menyatu mulus (2-pass)
            palm_c = pt(3.2, -0.5)
            fingers = [
                # (pangkal_fwd, pangkal_side, ujung_fwd, ujung_side, tebal)
                (1.5,  6.2,  9.5,  13.8, 6.2),   # jempol
                (7.5,  4.8, 19.2,   7.0, 6.0),   # telunjuk
                (8.5,  0.0, 21.2,   0.2, 6.2),   # jari tengah
                (7.0, -5.0, 17.8,  -6.8, 5.8),   # jari manis/kelingking
            ]
            # pass 1: outline luar menyatu
            c.ell(palm_c[0], palm_c[1], 10.6 * sc + how, 9.8 * sc + how, OUT)
            for f0, s0, f1, s1, fw in fingers:
                c.line([pt(f0, s0), pt(f1, s1)], OUT, fw * sc + 2 * how)
            # pass 2: isi kulit menyatu bersih
            c.ell(palm_c[0], palm_c[1], 10.6 * sc, 9.8 * sc, skin)
            for f0, s0, f1, s1, fw in fingers:
                c.line([pt(f0, s0), pt(f1, s1)], skin, fw * sc)
            # garis sekat halus di sela antar jari agar jari-jari tetap terbaca jelas
            for sep_s in (3.4, -2.5):
                c.line([pt(9.8, sep_s), pt(14.2, sep_s * 1.15)], OUT, 1.9 * s)

    # ------------------------------------------------------------ kepala
    def _head(self, c, st, T, s, fl, ow, turn=0.0):
        p = self.p
        ex = eks(st.get("expr", "senang"))
        tilt = math.radians(st.get("tilt", 0) * (fl if False else 1))
        look = st.get("look", (0.0, 0.0))
        lk = ex.get("look")
        if lk and abs(look[0]) < .01 and abs(look[1]) < .01:
            look = lk
        fem = bool(p.get("hijab")) or p.get("bulu_mata")
        mask = bool(p.get("wajah_maskulin"))
        hij = bool(p.get("hijab"))
        cx, cy = 4.0 * turn, HEAD_Y
        face_rx, face_ry = (78.0, 84.0) if hij else (HEAD_R, HEAD_R)
        fcy = cy + (12 if hij else (-2 if p.get("wajah_chibi_ref") else 0))
        yaw_x = 22.0 * turn     # pergeseran fitur wajah ke arah hadap 3/4 (+x lokal)
        hair_sh = -10.0 * turn  # massa rambut/hijab sedikit bergeser ke belakang saat miring

        def H(lx, ly):
            rx, ry = _rot((lx, ly), tilt * fl)
            return T(cx + rx, fcy + ry)

        def HH(pts):
            return [H(*q) for q in pts]

        # belakang rambut
        hair_c = warna(p.get("rambut_warna"), HITAM)
        r = p.get("rambut")
        if hij:
            hj, hjd = warna(p["hijab"]), warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
            if p.get("hijab_gaya") == "modern":
                outer = HH([
                    (hair_sh - 98, -8), (hair_sh - 88, -72), (hair_sh - 52, -108), (hair_sh, -118),
                    (hair_sh + 52, -108), (hair_sh + 88, -72), (hair_sh + 98, -8),
                    (hair_sh + 100, 42), (hair_sh + 74, 78), (hair_sh, 88), (hair_sh - 74, 78), (hair_sh - 100, 42),
                ])
                c.blob(outer, hj, ow, OUT, n=7)
                c.curve(HH([(hair_sh - 74, -54), (hair_sh - 44, -90), (hair_sh - 4, -102)]), terang(hj, 0.14), 4.0 * s)
                c.curve(HH([(hair_sh + 78, -52), (hair_sh + 46, -90), (hair_sh + 4, -102)]), hjd, 2.8 * s)
            else:
                outer = HH(_ellpts(hair_sh, -12, 102, 104))
                c.poly(outer, hj, ow, OUT)
                c.curve(HH([(hair_sh - 70, -54), (hair_sh - 40, -88), (hair_sh, -96)]), terang(hj, 0.14), 3.6 * s)
        if r in ("kuncir",) and not hij:
            c.ell(*H(hair_sh - 86, -58), 27 * s, 27 * s, hair_c, ow, OUT)
            if turn < 0.75:
                c.ell(*H(hair_sh + 86, -58), 27 * s * (1.0 - 0.35 * turn), 27 * s, hair_c, ow, OUT)
        if r == "keriting" and not hij:
            for i, a in enumerate(range(188, 353, 15)):
                rr = 86 + (5 if i % 2 else 0)
                c.ell(*H(hair_sh + math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr), 27 * s, 27 * s, hair_c, ow * .9, OUT)
        if r == "kribo_chibi" and not hij:
            self._hair_back_ref(c, HH, s, hair_c, hair_sh)
        if False:
            # RAMBUT KRIBO ANIME BERLAYER MELENGKUNG (persis siluet referensi: ikal melengkung organik, BUKAN brokoli bulat!)
            oc_h = (28, 24, 30)
            ow_h = 2.6 * s
            # massa dasar asimetris sedikit melebar di atas & merapat ke pipi
            base_pts = [
                (hair_sh - 114, 14), (hair_sh - 134, -22), (hair_sh - 132, -74), (hair_sh - 96, -122),
                (hair_sh - 34, -148), (hair_sh + 34, -146), (hair_sh + 98, -118), (hair_sh + 134, -68),
                (hair_sh + 130, -18), (hair_sh + 112, 16), (hair_sh + 86, 26), (hair_sh - 86, 26),
            ]
            # 12 helai ikal melengkung lebar-organik di sekeliling siluet (persis gambar referensi!)
            locks_out = [
                ((-126, 6), (-148, -2), (-154, -18), (-124, -22)),
                ((-134, -34), (-160, -48), (-166, -66), (-126, -68)),
                ((-124, -80), (-146, -104), (-142, -124), (-102, -108)),
                ((-92, -118), (-98, -146), (-82, -158), (-58, -132)),
                ((-36, -142), (-18, -168), (8, -174), (16, -142)),
                ((34, -142), (66, -162), (86, -154), (68, -126)),
                ((94, -116), (126, -128), (138, -112), (112, -88)),
                ((126, -72), (154, -76), (160, -58), (128, -46)),
                ((130, -28), (156, -24), (156, -6), (122, -6)),
                ((116, 6), (134, 22), (122, 34), (102, 18)),
                ((-116, 6), (-134, 22), (-122, 34), (-102, 18)),
            ]
            # pass 1: outline
            c.blob(HH(base_pts), oc_h, ow_h * 1.4, oc_h, n=6)
            for p0, pm, tip, p1 in locks_out:
                e1 = bezier((hair_sh + p0[0], p0[1]), (hair_sh + pm[0], pm[1]), (hair_sh + tip[0], tip[1]), 6)
                e2 = list(reversed(bezier((hair_sh + p1[0], p1[1]), (hair_sh + (pm[0] + p1[0]) * 0.5, (pm[1] + tip[1]) * 0.5), (hair_sh + tip[0], tip[1]), 6)))
                c.poly(HH(e1 + e2), oc_h, ow_h * 1.5, oc_h)
            # pass 2: isi warna hitam arang hangat menyatu
            c.blob(HH(base_pts), hair_c, 0, n=6)
            for p0, pm, tip, p1 in locks_out:
                e1 = bezier((hair_sh + p0[0], p0[1]), (hair_sh + pm[0], pm[1]), (hair_sh + tip[0], tip[1]), 6)
                e2 = list(reversed(bezier((hair_sh + p1[0], p1[1]), (hair_sh + (pm[0] + p1[0]) * 0.5, (pm[1] + tip[1]) * 0.5), (hair_sh + tip[0], tip[1]), 6)))
                c.poly(HH(e1 + e2), hair_c)
            # pass 3: 3-tone tekstur ikal berlapis (bayangan dalam + highlight lembut + lekukan C-curl organik)
            sh_c = gelap(hair_c, 0.34)
            hl_c = terang(hair_c, 0.20)
            for cx_, cy_, rx_, ry_ in ((-74, -96, 30, 18), (-12, -120, 34, 20), (54, -104, 30, 18), (94, -62, 24, 16)):
                c.ell(*H(hair_sh + cx_, cy_), rx_ * s, ry_ * s, hl_c)
            # garis lengkung ikal berlapis (seperti goresan kuas ikal pada referensi!)
            for (x0_, y0_, xm_, ym_, x1_, y1_) in (
                (-102, -62, -82, -96, -54, -84), (-64, -108, -32, -132, -4, -108),
                (-12, -124, 22, -134, 48, -104), (42, -116, 78, -112, 96, -80),
                (-94, -36, -68, -62, -42, -46), (-38, -82, -6, -98, 24, -78),
                (22, -86, 56, -88, 80, -58), (74, -46, 102, -44, 108, -18),
            ):
                c.curve(HH([(hair_sh + x0_, y0_), (hair_sh + xm_, ym_), (hair_sh + x1_, y1_)]), sh_c, 2.6 * s)
        if r == "panjang_naa" and not hij:
            # rambut belakang panjang halus menjuntai melewati bahu (ujung helai lembut, bukan zig-zag leher!)
            oc_h = (64, 50, 42)
            ow_h = 2.8 * s
            c.blob(HH([
                (hair_sh - 108, -12), (hair_sh - 106, -68), (hair_sh - 74, -108), (hair_sh, -120),
                (hair_sh + 74, -108), (hair_sh + 106, -68), (hair_sh + 108, -12),
                (hair_sh + 120, 96), (hair_sh + 106, 152), (hair_sh + 68, 140), (hair_sh + 34, 156),
                (hair_sh, 144), (hair_sh - 34, 156), (hair_sh - 68, 140), (hair_sh - 106, 152), (hair_sh - 120, 96),
            ]), hair_c, ow_h, oc_h, n=7)
            # helai ujung rambut luar melengkung tipis keluar (kiri & kanan)
            for sg in (-1, 1):
                p_out = bezier((hair_sh + sg * 102, 34), (hair_sh + sg * 124, 98), (hair_sh + sg * 144, 146), 7)
                p_in = list(reversed(bezier((hair_sh + sg * 88, 52), (hair_sh + sg * 106, 108), (hair_sh + sg * 144, 146), 7)))
                c.poly(HH(p_out + p_in), hair_c, ow_h * 0.85, oc_h)
            # shading lembut di bagian bawah rambut belakang
            c.poly(HH([(hair_sh - 96, 82), (hair_sh + 96, 82), (hair_sh + 104, 148), (hair_sh - 104, 148)]), gelap(hair_c, 0.14))
        if r == "comma" and not hij:
            # rambut belakang bergelombang asimetris bervolume ala cowok kacamata gambar 2 (bukan helm mangkok!)
            oc_h = (46, 46, 62)
            ow_h = 2.8 * s
            c.blob(HH([
                (hair_sh - 114, 16), (hair_sh - 122, -40), (hair_sh - 104, -96), (hair_sh - 56, -128),
                (hair_sh - 8, -142), (hair_sh + 46, -134), (hair_sh + 98, -104), (hair_sh + 122, -46),
                (hair_sh + 112, 16), (hair_sh + 92, 32), (hair_sh - 92, 32),
            ]), hair_c, ow_h, oc_h, n=7)
            # 3 jambul ujung bergelombang lembut di tepi rambut (meruncing halus)
            for (x0_, y0_, xm_, ym_, xt_, yt_, x1_, y1_) in (
                (-110, -28, -132, -32, -140, -18, -106, -6),
                (108, -42, 134, -36, 142, -20, 104, -14),
                (-38, -128, -18, -152, 8, -156, 20, -130),
            ):
                p1 = bezier((hair_sh + x0_, y0_), (hair_sh + xm_, ym_), (hair_sh + xt_, yt_), 5)
                p2 = list(reversed(bezier((hair_sh + x1_, y1_), (hair_sh + xm_ * 0.9, ym_ + 8), (hair_sh + xt_, yt_), 5)))
                c.poly(HH(p1 + p2), hair_c, ow_h * 0.85, oc_h)
        if r == "panjang" and not hij:
            # rambut panjang coklat lembut berlapis (gaya chibi cewek Ghibli gambar 2)
            c.blob(HH([
                (hair_sh - 104, 10), (hair_sh - 102, -56), (hair_sh - 72, -102), (hair_sh, -116),
                (hair_sh + 72, -102), (hair_sh + 102, -56), (hair_sh + 104, 10),
                (hair_sh + 116, 104), (hair_sh + 86, 134), (hair_sh + 42, 118),
                (hair_sh, 126), (hair_sh - 42, 118), (hair_sh - 86, 134), (hair_sh - 116, 104),
            ]), hair_c, ow * .88, OUT, n=6)
        if r == "afro" and not hij:
            # afro kribo organik bergaya chibi Ghibli: massa afro mengembang + jambul-jambul ikal melengkung!
            af_cy = -44
            puffs = []
            dr_pat = (2, 10, -2, 12, 3, 10, -1, 13, 6, 13, -1, 10, 3, 12, -2, 10, 2)
            pr_pat = (25, 31, 28, 34, 30, 35, 31, 35, 34, 35, 31, 35, 30, 34, 28, 31, 25)
            for i, a in enumerate(range(144, 397, 16)):
                rad_a = math.radians(a)
                px = hair_sh + math.cos(rad_a) * (112 + dr_pat[i])
                py = af_cy + math.sin(rad_a) * (98 + dr_pat[i])
                puffs.append((px, py, pr_pat[i]))
            # helaian ujung ikal organik mencuat lembut di tepi afro (membuat siluet kribo berkarakter seperti gambar 1!)
            curls = [
                (-124, -68, -148, -90, -112, -88), (-96, -124, -112, -158, -72, -138),
                (-28, -146, -18, -178, 12, -148), (48, -140, 74, -170, 82, -130),
                (112, -96, 144, -116, 124, -70), (126, -34, 152, -40, 124, -12),
                (-126, -24, -150, -28, -120, -4),
            ]
            # pass 1: outline
            c.ell(*H(hair_sh, af_cy), 108 * s + ow, 94 * s + ow, OUT)
            for px, py, pr in puffs:
                c.ell(*H(px, py), pr * s + ow, pr * s + ow, OUT)
            for x0_, y0_, xt_, yt_, x1_, y1_ in curls:
                c.poly(HH([(hair_sh + x0_, y0_), (hair_sh + xt_, yt_), (hair_sh + x1_, y1_)]), OUT, ow * 1.4, OUT)
            # pass 2: isi warna rambut hangat + tekstur ikal berlapis (cel shadow + pusaran ikal + highlight)
            c.ell(*H(hair_sh, af_cy), 108 * s, 94 * s, hair_c)
            for px, py, pr in puffs:
                c.ell(*H(px, py), pr * s, pr * s, hair_c)
            for x0_, y0_, xt_, yt_, x1_, y1_ in curls:
                c.poly(HH([(hair_sh + x0_, y0_), (hair_sh + xt_, yt_), (hair_sh + x1_, y1_)]), hair_c)
            # bayangan cel bawah-kanan di dalam afro (memberi volume 3D lembut)
            sh_h = gelap(hair_c, 0.24)
            for sx_, sy_, sr_ in ((74, -26, 36), (48, -12, 34), (-78, -22, 32), (86, -64, 30)):
                c.ell(*H(hair_sh + sx_, sy_), sr_ * s, sr_ * 0.82 * s, sh_h)
            # highlight hangat di klaster atas-kiri afro
            hl_c = terang(hair_c, 0.16)
            for hx_, hy_, hr in ((hair_sh - 58, -114, 24), (hair_sh - 16, -128, 28), (hair_sh + 32, -116, 22), (hair_sh - 86, -78, 18)):
                c.ell(*H(hx_, hy_), hr * s, hr * 0.68 * s, hl_c)
            # tekstur pusaran & helai ikal kribo organik tersebar di seluruh volume rambut!
            curl_c = gelap(hair_c, 0.34)
            curl_hl = terang(hair_c, 0.22)
            swirls = [
                (-82, -78, 18, 1), (-46, -104, 20, -1), (4, -116, 22, 1), (52, -102, 20, -1), (86, -72, 18, 1),
                (-66, -48, 16, -1), (-24, -76, 19, 1), (26, -78, 19, -1), (68, -46, 16, 1), (0, -90, 17, 1),
            ]
            for cx_, cy_, cr_, dir_ in swirls:
                c.curve(HH([(hair_sh + cx_ - cr_, cy_ + 5 * dir_), (hair_sh + cx_, cy_ - cr_ * 0.55),
                            (hair_sh + cx_ + cr_, cy_ + 3 * dir_)]), curl_c, 3.0 * s)
                c.curve(HH([(hair_sh + cx_ - cr_ * 0.6, cy_ - 2), (hair_sh + cx_, cy_ - cr_ * 0.38),
                            (hair_sh + cx_ + cr_ * 0.5, cy_ - 1)]), curl_hl, 1.8 * s)
        # wajah
        kepala = p.get("kepala")
        if kepala == "otak":
            # kepala otak pink chibi berlekuk-lekuk (2-pass: outline luar dulu lalu isi pink + lekukan sulkus)
            bc = warna(p.get("kulit"), (250, 174, 198))
            lip = gelap(bc, 0.25)
            lobes = [
                (-78, 30, 38), (-88, -12, 42), (-76, -52, 42), (-38, -76, 42),
                (38, -76, 42), (76, -52, 42), (88, -12, 42), (78, 30, 38),
                (-42, 58, 38), (0, 64, 40), (42, 58, 38),
            ]
            c.ell(*H(0, -6), 96 * s + ow, 82 * s + ow, OUT)
            for lx, ly, lr in lobes:
                c.ell(*H(lx, ly), lr * s + ow, lr * s + ow, OUT)
            c.ell(*H(0, -6), 96 * s, 82 * s, bc)
            for lx, ly, lr in lobes:
                c.ell(*H(lx, ly), lr * s, lr * s, bc)
            c.curve(HH([(0, -104), (-3, -78), (2, -52)]), lip, 4.4 * s)
            c.curve(HH([(-84, -44), (-62, -62), (-38, -48)]), lip, 3.8 * s)
            c.curve(HH([(84, -44), (62, -62), (38, -48)]), lip, 3.8 * s)
            c.curve(HH([(-100, -12), (-80, -22), (-68, -4)]), lip, 3.6 * s)
            c.curve(HH([(100, -12), (80, -22), (68, -4)]), lip, 3.6 * s)
            c.curve(HH([(-90, 26), (-72, 14), (-62, 34)]), lip, 3.4 * s)
            c.curve(HH([(90, 26), (72, 14), (62, 34)]), lip, 3.4 * s)
            c.ell(*H(-42, -80), 13 * s, 6.5 * s, (255, 255, 255, 130))
        elif kepala == "virus":
            vc = warna(p.get("kulit"), (112, 204, 88))
            spikes = []
            for i in range(10):
                a = math.radians(i * 36 + 18)
                ca, sa = math.cos(a), math.sin(a)
                spikes.append(((ca * 84, sa * 84), (ca * 118, sa * 118)))
            for p0, p1 in spikes:
                c.line(HH([p0, p1]), OUT, 20 * s)
                c.ell(*H(*p1), 15.5 * s + ow, 15.5 * s + ow, OUT)
            c.ell(*H(0, 0), 88 * s + ow, 88 * s + ow, OUT)
            for p0, p1 in spikes:
                c.line(HH([p0, p1]), vc, 11 * s)
                c.ell(*H(*p1), 14 * s, 14 * s, terang(vc, 0.22))
            c.ell(*H(0, 0), 88 * s, 88 * s, vc)
            for bx, by, br in ((-52, -42, 11), (54, -34, 9.5), (-56, 40, 9.5), (50, 44, 11)):
                c.ell(*H(bx, by), br * s, br * s, gelap(vc, 0.20))
        elif kepala == "sel_imun":
            ic = warna(p.get("kulit"), (236, 248, 255))
            c.ell(*H(0, 0), 114 * s, 114 * s, (120, 204, 252, 70))
            bumps = [(math.cos(math.radians(i * 45)) * 68, math.sin(math.radians(i * 45)) * 68, 42) for i in range(8)]
            c.ell(*H(0, 0), 84 * s + ow, 84 * s + ow, OUT)
            for bx, by, br in bumps:
                c.ell(*H(bx, by), br * s + ow, br * s + ow, OUT)
            c.ell(*H(0, 0), 84 * s, 84 * s, ic)
            for bx, by, br in bumps:
                c.ell(*H(bx, by), br * s, br * s, ic)
            c.ell(*H(-38, -52), 15 * s, 9 * s, (255, 255, 255, 190))
        elif hij and p.get("hijab_gaya") == "modern":
            skin_c = warna(p.get("kulit"), PUTIH)
            face_pts = [
                (0, -70), (35, -56), (63, -29), (76, 4),
                (72, 39), (50, 66), (22, 78), (0, 80),
                (-22, 78), (-50, 66), (-72, 39), (-76, 4),
                (-63, -29), (-35, -56),
            ]
            c.blob(HH(face_pts), skin_c, ow, OUT, n=5)
            # cel shading lembut di sisi kanan-bawah pipi
            c.curve(HH([(64, 16), (48, 56), (12, 72)]), gelap(skin_c, 0.08), 8.0 * s)
            hjd2 = warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
            c.curve(HH([(-68, -12), (-40, -52), (0, -70), (40, -52), (68, -12)]), hjd2, 2.8 * s)
        else:
            skin_c = warna(p.get("kulit"), PUTIH)
            pintar = bool(p.get("wajah_pintar")) or bool(p.get("wajah_naa")) or bool(p.get("wajah_arka"))
            is_arka = bool(p.get("wajah_arka"))
            is_naa = bool(p.get("wajah_naa"))
            is_chibi_ref = bool(p.get("wajah_chibi_ref"))
            oc_f = (62, 48, 44) if is_chibi_ref else ((64, 52, 46) if p.get("outline_hangat") else OUT)
            if p.get("telinga") and not hij and kepala not in ("otak", "virus", "sel_imun"):
                for sg in (-1, 1):
                    if turn >= 0.70 and sg > 0:
                        continue
                    ex_ear = sg * ((78 if is_chibi_ref else face_rx + (-2 if is_arka else (-4 if pintar else 0)))) - (6.0 * turn if sg < 0 else 0.0)
                    erx = (16.5 if is_chibi_ref else (18.5 if is_arka else 13.5)) * s
                    ery = (19.5 if (is_arka or is_chibi_ref) else 18.0) * s
                    ey_ear = 14 if is_chibi_ref else (14 if is_arka else (10 if pintar else 6))
                    c.ell(*H(ex_ear, ey_ear), erx, ery, skin_c, 2.6 * s if is_chibi_ref else ow * .82, oc_f)
                    if is_chibi_ref:
                        c.ell(*H(ex_ear - sg * 2, ey_ear + 1), erx * 0.48, ery * 0.45, gelap(skin_c, 0.14))
                        c.curve(HH([(ex_ear - sg * 4, ey_ear - 4), (ex_ear + sg * 4, ey_ear + 1), (ex_ear - sg * 2, ey_ear + 8)]), oc_f, 2.0 * s)
                    elif pintar:
                        c.curve(HH([(ex_ear - sg * 4, 5), (ex_ear + sg * 5, 14), (ex_ear - sg * 3, 22)]), gelap(skin_c, 0.22), 2.4 * s)
            if is_chibi_ref:
                # WAJAH COWOK MASKULIN TIRUS BERKARAKTER: rahang tegas (jawline angle di y=44) meruncing ke dagu cowok tegas (tanpa blush pink cewek!)
                jx = 8.0 * turn
                face_pts = [
                    (0, -84), (52, -74), (77, -38),
                    (79, -4), (77, 20), (71 + jx * 0.2, 44),
                    (46 + jx * 0.4, 68), (18 + jx * 0.6, 82), (jx, 84),
                    (-18 + jx * 0.4, 82), (-46, 68),
                    (-71, 44), (-77, 20), (-79, -4),
                    (-77, -38), (-52, -74),
                ]
                c.blob(HH(face_pts), skin_c, 2.8 * s, oc_f, n=5)
                # shading cel maskulin tipis di rahang kanan-bawah (tanpa blush pink bulat cewek!)
                c.poly(HH([(75, 18), (70, 44), (45, 68), (16, 82), (4, 83), (38, 64), (62, 40), (70, 18)]), gelap(skin_c, 0.08))
                c.blob(HH(face_pts), None, 2.8 * s, oc_f, n=5)
            elif is_naa or is_arka:
                # wajah chibi lembut pipi tembam manis & dagu bundar halus (persis gambar 1 & 2!)
                jx = 8.0 * turn
                w_k = 1.04 if is_arka else 1.02
                face_pts = [
                    (0, -face_ry * 0.96), (face_rx * 0.60 * w_k, -face_ry * 0.84), (face_rx * 0.96 * w_k, -face_ry * 0.32),
                    (face_rx * 1.00 * w_k, face_ry * 0.22), (face_rx * 0.84 * w_k + jx * 0.3, face_ry * 0.68),
                    (face_rx * 0.42 * w_k + jx * 0.6, face_ry * 0.94), (jx, face_ry * 1.00),
                    (-face_rx * 0.42 * w_k + jx * 0.4, face_ry * 0.94), (-face_rx * 0.84 * w_k, face_ry * 0.68),
                    (-face_rx * 1.00 * w_k, face_ry * 0.22), (-face_rx * 0.96 * w_k, -face_ry * 0.32),
                    (-face_rx * 0.60 * w_k, -face_ry * 0.84),
                ]
                c.blob(HH(face_pts), skin_c, ow * .82, OUT, n=6)
                c.curve(HH([(face_rx * 0.82, face_ry * 0.36), (face_rx * 0.56, face_ry * 0.78), (jx, face_ry * 0.94)]),
                        gelap(skin_c, 0.08), 8.0 * s)
                c.blob(HH(face_pts), None, ow * .82, OUT, n=6)
            elif pintar:
                # bentuk wajah anime Ghibli: pipi lembut meruncing ke dagu berkarakter (bukan lingkaran bola polos!)
                jx = 8.0 * turn
                face_pts = [
                    (0, -face_ry), (face_rx * 0.56, -face_ry * 0.86), (face_rx * 0.94, -face_ry * 0.36),
                    (face_rx * 0.96, face_ry * 0.14), (face_rx * 0.78 + jx * 0.3, face_ry * 0.62),
                    (face_rx * 0.34 + jx * 0.7, face_ry * 0.94), (jx, face_ry * 1.02),
                    (-face_rx * 0.34 + jx * 0.5, face_ry * 0.94), (-face_rx * 0.78, face_ry * 0.62),
                    (-face_rx * 0.96, face_ry * 0.14), (-face_rx * 0.94, -face_ry * 0.36),
                    (-face_rx * 0.56, -face_ry * 0.86),
                ]
                c.blob(HH(face_pts), skin_c, ow * .88, OUT, n=6)
                # bayangan lembut di pipi & bawah dagu (dimensi karakter anime Ghibli)
                c.curve(HH([(face_rx * 0.80, face_ry * 0.26), (face_rx * 0.56, face_ry * 0.72), (jx, face_ry * 0.94)]),
                        gelap(skin_c, 0.09), 9.0 * s)
                c.blob(HH(face_pts), None, ow * .88, OUT, n=6)
            else:
                face = HH(_ellpts(0, 0, face_rx, face_ry, 36))
                c.poly(face, skin_c, ow, OUT)
                shade_outer = arc_pts(0, 0, face_rx - 1.5, face_ry - 1.5, -15, 115, 20)
                shade_inner = []
                for k in range(20, -1, -1):
                    t_a = k / 20.0
                    ang = math.radians(-15 + 130 * t_a)
                    thick = 11.5 * math.sin(math.pi * t_a)
                    shade_inner.append((math.cos(ang) * (face_rx - 1.5 - thick),
                                        math.sin(ang) * (face_ry - 1.5 - thick)))
                c.poly(HH(shade_outer + shade_inner), gelap(skin_c, 0.075))
                c.poly(face, None, ow, OUT)
            # rambut depan
            if not hij:
                self._hair_front(c, H, HH, s, ow, r, hair_c, p)
            else:
                hjd2 = warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
                c.curve(HH(arc_pts(0, 2, face_rx + 1, face_ry + 1, 200, 340, 12)), hjd2, 3.8 * s)
        # topi/peci
        if p.get("peci"):
            c.poly(HH([(-65, -72), (-58, -110), (0, -118), (58, -110), (65, -72), (0, -58)]), HITAM, ow, OUT)
        if p.get("topi"):
            tc = warna(p["topi"] if not isinstance(p["topi"], bool) else "merah", MERAH)
            c.blob(HH([(-80, -48), (-72, -104), (0, -124), (72, -104), (80, -48), (0, -42)]), tc, ow, OUT)
            c.poly(HH([(38, -52), (120, -44), (120, -34), (38, -39)]), gelap(tc, .15), ow * .8, OUT)

        # fitur wajah (bergeser natural ke kanan +x lokal saat hadap miring 3/4)
        lx_, ly_ = look
        fs = 0.90 if hij else 0.94
        chibi_eye = bool(p.get("mata_chibi"))
        is_naa_f = bool(p.get("wajah_naa"))
        is_arka_f = bool(p.get("wajah_arka"))
        is_chibi_ref_f = bool(p.get("wajah_chibi_ref"))
        fx0, fy0 = lx_ * 14 + yaw_x, ly_ * 7.5
        eyes = ex["eyes"]
        blink = st.get("blink", 0.0)
        # jarak antar mata lebar & posisi sedikit lebih rendah untuk karakter chibi anime agar tidak berdesakan!
        if is_chibi_ref_f:
            eye_sep = 37.5 * (1.0 - 0.16 * turn)
            eye_y = 12.0 + fy0
        elif is_naa_f:
            eye_sep = 43.0 * (1.0 - 0.16 * turn)
            eye_y = 12.0 + fy0
        elif is_arka_f:
            eye_sep = 42.0 * (1.0 - 0.16 * turn)
            eye_y = 12.0 + fy0
        else:
            eye_sep = (33 if chibi_eye else 32) * fs * (1.0 - 0.16 * turn)
            eye_y = (9 if chibi_eye else -3) * fs + fy0
        # mata depan (i=1) lebih dekat tepi depan, mata belakang (i=0) sedikit lebih dekat tengah
        ec = (-eye_sep * (1.0 + 0.06 * turn), eye_sep * (1.0 - 0.08 * turn))
        ew = 11.2 * (0.94 if mask else 1.0)
        eh = 16.5 * (1.10 if fem else (0.92 if mask else 1.0))
        hlk = ex.get("hl", 1.0) * (0.88 if mask else 1.0)
        # lensa kacamata digambar SEBELUM mata agar tidak menutupi mata/kilau
        hw, hh_g, rad_g = 27.5 * fs * (1.0 - 0.12 * turn), 20.5 * fs, 8.5 * fs
        r_bulat = 27.5 * fs * (1.0 - 0.10 * turn)
        if p.get("kacamata") == "kotak":
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = hw * (1.0 - 0.14 * turn if i == 1 else 1.0)
                frame = _rectpts(gx - hw_i, gy - hh_g, gx + hw_i, gy + hh_g, rad_g, 6)
                c.poly(HH(frame), (255, 255, 255, 225))
        elif p.get("kacamata") == "browline":
            # lensa bening lebar browline (gambar 2 Arka)
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 4
                rx_p = 35.5 * (1.0 - 0.14 * turn if i == 1 else 1.0)
                ry_p = 27.0
                c.poly(HH(_ellpts(gx, gy, rx_p, ry_p, 28)), (242, 248, 255, 58))
                c.line(HH([(gx - rx_p * 0.48, gy - ry_p * 0.30), (gx - rx_p * 0.12, gy - ry_p * 0.62)]), (255, 255, 255, 130), 2.8 * s)
        elif p.get("kacamata") == "pintar_kotak":
            # kacamata kotak-membulat tipis elegan khas Kribo (tidak menutupi ekspresi mata!)
            big_g = 1.06 if p.get("wajah_chibi_ref") else 1.0
            big_h = 1.08 if p.get("wajah_chibi_ref") else 1.0
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = (28.5 * big_g * fs) * (1.0 - 0.14 * turn if i == 1 else 1.0)
                hh_i = 22.0 * big_h * fs
                frame = _rectpts(gx - hw_i, gy - hh_i, gx + hw_i, gy + hh_i, 10.5 * fs, 6)
                c.poly(HH(frame), (236, 248, 255, 36))
                c.line(HH([(gx - hw_i * 0.55, gy - hh_i * 0.32), (gx - hw_i * 0.14, gy - hh_i * 0.64)]), (255, 255, 255, 115), 2.6 * s)
        elif p.get("kacamata") == "pintar":
            # kacamata pintar Ghibli: lensa kaca bening tipis + pantulan kilau diagonal halus (mata tetap hidup!)
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                rx_p = (27.0 * fs) * (1.0 - 0.14 * turn if i == 1 else 1.0)
                ry_p = 22.5 * fs
                c.poly(HH(_ellpts(gx, gy, rx_p, ry_p, 26)), (236, 248, 255, 62))
                c.line(HH([(gx - rx_p * 0.48, gy - ry_p * 0.36), (gx - rx_p * 0.12, gy - ry_p * 0.62)]), (255, 255, 255, 130), 3.0 * s)
        elif p.get("kacamata") == "bulat":
            for i, ex_ in enumerate(ec):
                rx_b = r_bulat * (1.0 - 0.14 * turn if i == 1 else 1.0)
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, rx_b, r_bulat, 26)), (255, 255, 255, 58))

        for i, ex_ in enumerate(ec):
            ex_ = ex_ + fx0
            if eyes in ("oval", "wide", "spark", "dot", "half", "wink") and not (eyes == "wink" and i == 1):
                if p.get("wajah_chibi_ref") and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    self._eye_ref(c, HH, s, ex_, eye_y, i, eyes, blink, turn, lx_, ly_)
                elif False:
                    # MATA CHIBI REFERENSI: besar bulat hangat, kelopak atas tebal lembut, iris 2-tone coklat/hazel + kilau besar!
                    sc = 1.10 if eyes == "wide" else 1.0
                    ew_r = 22.5 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
                    eh_r = (24.0 * 0.52 if eyes == "half" else 24.0 * sc) * (1.0 - 0.9 * blink)
                    iris_c = warna(p.get("iris"), (96, 68, 52))
                    iris_lt = terang(mix(iris_c, (216, 174, 128), 0.48), 0.18)
                    line_c = (66, 44, 38)
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_r, max(1.8, eh_r), 22)), PUTIH)
                    if eh_r > 5.5:
                        ir_w = 16.5 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
                        ir_h = min(eh_r * 0.92, 18.8 * sc)
                        ix = ex_ + lx_ * 4.5 + (2.5 * turn)
                        iy = eye_y + 3.0 + ly_ * 2.5
                        # iris 2-tone coklat-hangat (gelap atas -> terang lembut bawah)
                        c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 20)), gelap(iris_c, 0.25), 1.6 * s, line_c)
                        c.poly(HH(_ellpts(ix, iy + ir_h * 0.24, ir_w * 0.80, ir_h * 0.56, 16)), iris_lt)
                        c.poly(HH(_ellpts(ix, iy - ir_h * 0.06, ir_w * 0.48, ir_h * 0.48, 14)), (48, 34, 28))
                        # 2 kilau putih jernih (1 besar kiri-atas, 1 kecil kanan-bawah)
                        c.poly(HH(_ellpts(ix - ir_w * 0.36, iy - ir_h * 0.36, 5.4, 5.4, 12)), PUTIH)
                        c.poly(HH(_ellpts(ix + ir_w * 0.34, iy + ir_h * 0.34, 2.4, 2.4, 8)), PUTIH)
                    # kelopak atas tebal melengkung lembut + garis lipatan tipis di atasnya
                    c.curve(HH(arc_pts(ex_, eye_y + 2, ew_r + 1.2, max(2.2, eh_r + 1.0), 192, 348, 16)), line_c, 5.8 * s)
                    if eh_r > 6.0:
                        c.curve(HH(arc_pts(ex_, eye_y + 2, ew_r * 0.82, eh_r, 30, 150, 8)), (128, 96, 86), 1.8 * s)
                elif p.get("wajah_arka") and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    # MATA MASKULIN TENANG & CERDAS (persis cowok gambar 2: kelopak atas agak lurus, iris abu-ungu lembut!)
                    sc = 1.12 if eyes == "wide" else 1.0
                    ew_a = 18.5 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
                    eh_a = (13.5 * 0.56 if eyes == "half" else 13.5 * sc) * (1.0 - 0.9 * blink)
                    iris_c = warna(p.get("iris"), (118, 122, 144))
                    iris_lt = terang(iris_c, 0.34)
                    line_c = (56, 50, 58)
                    c.poly(HH(_ellpts(ex_, eye_y + 4, ew_a, max(1.6, eh_a), 20)), PUTIH)
                    if eh_a > 4.5:
                        ir_w = 11.2 * (1.0 - 0.12 * turn if i == 1 else 1.0)
                        ir_h = min(eh_a * 0.92, 11.5)
                        ix = ex_ + lx_ * 4.5 + (2.5 * turn)
                        iy = eye_y + 4.5 + ly_ * 2.5
                        c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 18)), gelap(iris_c, 0.16), 1.4 * s, line_c)
                        c.poly(HH(_ellpts(ix, iy + ir_h * 0.22, ir_w * 0.78, ir_h * 0.54, 14)), iris_lt)
                        c.poly(HH(_ellpts(ix, iy - ir_h * 0.08, ir_w * 0.44, ir_h * 0.44, 12)), (54, 54, 68))
                        c.poly(HH(_ellpts(ix - ir_w * 0.38, iy - ir_h * 0.28, 3.8, 3.6, 10)), PUTIH)
                    # kelopak atas datar-tegas + lipatan kelopak atas tipis
                    c.curve(HH([(ex_ - ew_a - 1, eye_y + 2), (ex_, eye_y - eh_a + 3), (ex_ + ew_a + 1, eye_y + 2)]), line_c, 4.6 * s)
                    c.curve(HH([(ex_ - ew_a * 0.75, eye_y - eh_a - 4), (ex_, eye_y - eh_a - 7), (ex_ + ew_a * 0.75, eye_y - eh_a - 4)]), (126, 108, 104), 2.0 * s)
                elif (p.get("wajah_pintar") or p.get("wajah_naa")) and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    # MATA CHIBI GHIBLI SOFT (gambar 1 @naa: bulat besar berbinar + iris 2-tone teal bercahaya)
                    sc = 1.12 if eyes == "wide" else 1.0
                    big = 1.14 if p.get("wajah_naa") else 1.0
                    ew_p = 17.5 * big * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
                    eh_p = (19.5 * big * 0.52 if eyes == "half" else 19.5 * big * sc) * (1.0 - 0.9 * blink)
                    iris_c = warna(p.get("iris"), (62, 122, 124))
                    iris_lt = terang(mix(iris_c, (172, 232, 224), 0.45), 0.18)
                    line_c = (62, 50, 44) if p.get("outline_hangat") else OUT
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_p, max(1.8, eh_p), 22)), PUTIH)
                    if eh_p > 5.0:
                        ir_w = (10.5 if eyes == "wide" else 12.2) * big * (1.0 - 0.12 * turn if i == 1 else 1.0)
                        ir_h = min(eh_p * 0.90, 14.8 * big)
                        ix = ex_ + lx_ * 4.5 + (2.5 * turn)
                        iy = eye_y + 2.5 + ly_ * 2.5
                        c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 18)), gelap(iris_c, 0.22), 1.6 * s, line_c)
                        c.poly(HH(_ellpts(ix, iy + ir_h * 0.24, ir_w * 0.78, ir_h * 0.56, 14)), iris_lt)
                        c.poly(HH(_ellpts(ix, iy - ir_h * 0.06, ir_w * 0.48, ir_h * 0.48, 12)), (42, 46, 52))
                        c.poly(HH(_ellpts(ix - ir_w * 0.36, iy - ir_h * 0.34, 4.4, 4.4, 10)), PUTIH)
                        c.poly(HH(_ellpts(ix + ir_w * 0.32, iy + ir_h * 0.34, 2.2, 2.2, 8)), PUTIH)
                    c.curve(HH(arc_pts(ex_, eye_y + 1.5, ew_p + 1.0, max(2.0, eh_p + 0.8), 192, 348, 14)), line_c, 4.8 * s)
                    if eh_p > 5.5:
                        c.curve(HH(arc_pts(ex_, eye_y + 2, ew_p * 0.85, eh_p, 26, 154, 8)), (110, 92, 82), 1.8 * s)
                    if p.get("bulu_mata") and eh_p > 5.5:
                        sg_e = -1 if i == 0 else 1
                        c.line(HH([(ex_ + sg_e * (ew_p - 1), eye_y - 3), (ex_ + sg_e * (ew_p + 7), eye_y - 10)]), line_c, 3.8 * s)
                elif mask and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    # mata ekspresif berkilau (mengikuti uji-kribo 3D-stickman versi 2D)
                    sc = 1.15 if eyes == "wide" else 1.0
                    ew_m = 9.4 * sc
                    hh = (12.2 * 0.52 if eyes == "half" else 12.2 * sc) * (1 - 0.9 * blink)
                    if eyes == "dot":
                        c.poly(HH(_ellpts(ex_, eye_y + 2, 11.5, 11.5, 16)), PUTIH, ow * .75, OUT)
                        c.poly(HH(_ellpts(ex_ + lx_ * 3, eye_y + 2, 4.2, 4.2, 10)), OUT)
                    else:
                        c.poly(HH(_ellpts(ex_, eye_y + 2, ew_m, max(1.6, hh), 18)), OUT)
                        if hh > 5.0:
                            c.poly(HH(_ellpts(ex_ - 3.0, eye_y + 2 - hh * .32, 3.6 * hlk, 3.6 * hlk, 10)), PUTIH)
                            c.poly(HH(_ellpts(ex_ + 3.0, eye_y + 2 + hh * .28, 1.7, 1.7, 8)), PUTIH)
                        if eyes == "half":
                            c.line(HH([(ex_ - ew_m - 2.5, eye_y + 2 - hh * .42), (ex_ + ew_m + 2.5, eye_y + 2 - hh * .42)]), OUT, 4.2 * s)
                elif chibi_eye and eyes in ("oval", "wide", "spark", "half", "wink"):
                    # mata bulat besar berkilau (gaya chibi anime imut)
                    sc = 1.15 if eyes == "wide" else 1.0
                    ew_c = 16.0 * sc
                    hh = 18.8 * sc * (1 - 0.9 * blink)
                    if eyes == "half":
                        hh = 18.8 * 0.52
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_c, max(1.8, hh), 20)), OUT)
                    if hh > 6:
                        c.curve(HH(arc_pts(ex_, eye_y + 1, ew_c + 1.4, hh + 1.0, 200, 340, 10)), OUT, 4.0 * s)
                        c.poly(HH(_ellpts(ex_ - 5.2, eye_y + 2 - hh * .30, 5.8 * hlk, 5.8 * hlk, 12)), PUTIH)
                        c.poly(HH(_ellpts(ex_ + 5.0, eye_y + 2 + hh * .32, 2.6, 2.6, 10)), PUTIH)
                    if eyes == "spark" and hh > 6:
                        c.poly(HH(_ellpts(ex_ - 4.5, eye_y + 2 + hh * .36, 2.4, 2.4, 8)), PUTIH)
                    if eyes == "half":
                        c.line(HH([(ex_ - ew_c - 3, eye_y + 2 - hh * .4), (ex_ + ew_c + 3, eye_y + 2 - hh * .4)]), OUT, 4.6 * s)
                elif p.get("mata_sclera") and eyes in ("oval", "wide", "spark", "half", "wink"):
                    sc = 1.18 if eyes == "wide" else 1.0
                    ew_s = 14.5 * sc
                    eh_s = 16.5 * sc * (1 - 0.9 * blink)
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_s, max(1.8, eh_s), 20)), PUTIH, 3.8 * s, OUT)
                    pr = (5.0 if eyes == "wide" else 6.2) * (1.0 if blink < 0.5 else 0.4)
                    px_, py_ = ex_ + lx_ * 4.5, eye_y + 2 + ly_ * 3.0
                    c.poly(HH(_ellpts(px_, py_, pr, pr * (1 - 0.85 * blink), 14)), OUT)
                    if eh_s > 6 and blink < 0.5:
                        c.poly(HH(_ellpts(px_ - 2.0, py_ - 2.2, 2.2, 2.2, 8)), PUTIH)
                    if eyes == "half" and blink < 0.5:
                        lid_top = arc_pts(ex_, eye_y + 2, ew_s + 0.5, eh_s + 0.5, 185, 355, 12)
                        c.poly(HH(lid_top + [(ex_ + ew_s + 0.5, eye_y + 1), (ex_ - ew_s - 0.5, eye_y + 1)]),
                               warna(p.get("kulit"), PUTIH))
                        c.poly(HH(_ellpts(ex_, eye_y + 2, ew_s, eh_s, 20)), None, 3.8 * s, OUT)
                        c.line(HH([(ex_ - ew_s - 2, eye_y + 1), (ex_ + ew_s + 2, eye_y + 1)]), OUT, 4.0 * s)
                else:
                    sc = 1.3 if eyes == "wide" else 1.0
                    hh = eh * sc * (1 - 0.9 * blink)
                    if eyes == "half":
                        hh = eh * 0.52
                    if eyes == "dot":
                        c.poly(HH(_ellpts(ex_, eye_y, 13, 13, 16)), PUTIH, ow * .8, OUT)
                        c.poly(HH(_ellpts(ex_ + lx_ * 3, eye_y, 4.5, 4.5, 10)), OUT)
                    else:
                        c.poly(HH(_ellpts(ex_, eye_y, ew * sc, hh, 18)), OUT)
                        if hh > 6 and eyes != "wide":
                            c.poly(HH(_ellpts(ex_ - 3.5, eye_y - hh * .38, 4.6 * hlk, 4.6 * hlk, 10)), PUTIH)
                        if eyes == "wide" and hh > 6:
                            c.poly(HH(_ellpts(ex_ - 3, eye_y - hh * .3, 4, 4, 10)), PUTIH)
                    if eyes == "spark":
                        c.poly(HH(_ellpts(ex_ + 4, eye_y + 6, 3.6, 3.6, 8)), PUTIH)
                    if eyes == "half":
                        c.line(HH([(ex_ - ew - 3, eye_y - hh * .4), (ex_ + ew + 3, eye_y - hh * .4)]), OUT, 5 * s)
            if eyes == "arc_up" or (eyes == "wink" and i == 1):      # ^ ^
                c.curve(HH(arc_pts(ex_, eye_y + 8, 15, 15, 200, 340, 10)), OUT, 5.2 * s)
            if eyes == "arc_dn":                                       # ⌣ ⌣
                c.curve(HH(arc_pts(ex_, eye_y - 4, 15, 12, 20, 160, 10)), OUT, 5.2 * s)
            if fem and p.get("bulu_mata", True) and eyes in ("oval", "wide", "spark", "half", "wink", "dot"):
                sg = -1 if i == 0 else 1
                for k in (0, 1):
                    c.line(HH([(ex_ + sg * 11, eye_y - 10 + k * 7), (ex_ + sg * (19 + k * 2), eye_y - 18 + k * 8)]), OUT, 3.6 * s)

        # bingkai kacamata (di atas mata)
        if p.get("kacamata") == "kotak":
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = hw * (1.0 - 0.14 * turn if i == 1 else 1.0)
                frame = _rectpts(gx - hw_i, gy - hh_g, gx + hw_i, gy + hh_g, rad_g, 6)
                c.poly(HH(frame), None, 4.8 * s, OUT)
            hw0, hw1 = hw, hw * (1.0 - 0.14 * turn)
            c.line(HH([(ec[0] + fx0 + hw0, eye_y - 1), (ec[1] + fx0 - hw1, eye_y - 1)]), OUT, 4.8 * s)
            # tangkai kacamata: saat miring, tangkai sisi belakang (-1) memanjang ke telinga, sisi depan (+1) sangat pendek
            gx_l = ec[0] + fx0 - hw0
            c.line(HH([(gx_l, eye_y - 2), (-face_rx + 2, eye_y - 6)]), OUT, 4.0 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + hw1
                c.line(HH([(gx_r, eye_y - 2), (min(face_rx - 2, gx_r + 12 * (1.0 - turn)), eye_y - 6)]), OUT, 4.0 * s)
        elif p.get("kacamata") == "browline":
            # kacamata browline lebar & elegan (persis gambar 2 Arka: atas tebal gelap, bawah tipis)
            fr_c = (62, 54, 62)
            rx_l = 35.5
            rx_r = 35.5 * (1.0 - 0.14 * turn)
            ry_p = 27.0
            for i, ex_ in enumerate(ec):
                rx_i = rx_r if i == 1 else rx_l
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 4, rx_i, ry_p, 28)), None, 2.6 * s, fr_c)
                c.curve(HH(arc_pts(ex_ + fx0, eye_y + 4, rx_i, ry_p, 192, 348, 14)), fr_c, 5.4 * s)
            c.curve(HH([(ec[0] + fx0 + rx_l, eye_y + 1), (fx0, eye_y - 6), (ec[1] + fx0 - rx_r, eye_y + 1)]), fr_c, 3.6 * s, n=6)
            gx_l = ec[0] + fx0 - rx_l
            c.line(HH([(gx_l, eye_y - 1), (-face_rx + 2, eye_y + 3)]), fr_c, 3.8 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + rx_r
                c.line(HH([(gx_r, eye_y - 1), (min(face_rx - 2, gx_r + 12 * (1.0 - turn)), eye_y + 3)]), fr_c, 3.8 * s)
        elif p.get("kacamata") == "pintar_kotak":
            # bingkai kacamata kotak tipis-elegan khas Kribo
            fr_c = (68, 48, 44) if p.get("wajah_chibi_ref") else (48, 44, 46)
            big_g = 1.06 if p.get("wajah_chibi_ref") else 1.0
            big_h = 1.08 if p.get("wajah_chibi_ref") else 1.0
            hw0 = 28.5 * big_g * fs
            hw1 = (28.5 * big_g * fs) * (1.0 - 0.14 * turn)
            hh_i = 22.0 * big_h * fs
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = hw1 if i == 1 else hw0
                frame = _rectpts(gx - hw_i, gy - hh_i, gx + hw_i, gy + hh_i, 10.5 * fs, 6)
                c.poly(HH(frame), None, 2.2 * s, fr_c)
            c.line(HH([(ec[0] + fx0 + hw0, eye_y - 1), (ec[1] + fx0 - hw1, eye_y - 1)]), fr_c, 2.2 * s)
            gx_l = ec[0] + fx0 - hw0
            c.line(HH([(gx_l, eye_y - 1), (-78.0, eye_y + 3)]), fr_c, 2.0 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + hw1
                c.line(HH([(gx_r, eye_y - 1), (min(78.0, gx_r + 12 * (1.0 - turn)), eye_y + 3)]), fr_c, 2.0 * s)
        elif p.get("kacamata") == "pintar":
            # bingkai kacamata kawat tipis-elegan ala karakter pintar Ghibli
            fr_c = (44, 42, 48)
            rx_l = 27.0 * fs
            rx_r = (27.0 * fs) * (1.0 - 0.14 * turn)
            ry_p = 22.5 * fs
            for i, ex_ in enumerate(ec):
                rx_i = rx_r if i == 1 else rx_l
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, rx_i, ry_p, 28)), None, 3.2 * s, fr_c)
            # bridge melengkung halus di pangkal hidung
            c.curve(HH([(ec[0] + fx0 + rx_l, eye_y + 1), (fx0, eye_y - 4),
                        (ec[1] + fx0 - rx_r, eye_y + 1)]), fr_c, 3.0 * s, n=6)
            # tangkai kawat halus ke telinga
            gx_l = ec[0] + fx0 - rx_l
            c.line(HH([(gx_l, eye_y - 1), (-face_rx + 3, eye_y + 2)]), fr_c, 2.8 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + rx_r
                c.line(HH([(gx_r, eye_y - 1), (min(face_rx - 3, gx_r + 12 * (1.0 - turn)), eye_y + 2)]), fr_c, 2.8 * s)
        elif p.get("kacamata") == "bulat":
            for i, ex_ in enumerate(ec):
                rx_b = r_bulat * (1.0 - 0.14 * turn if i == 1 else 1.0)
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, rx_b, r_bulat, 26)), None, 4.0 * s, OUT)
            rx_r = r_bulat * (1.0 - 0.14 * turn)
            c.curve(HH([(ec[0] + fx0 + r_bulat, eye_y + 1), (fx0, eye_y - 3),
                        (ec[1] + fx0 - rx_r, eye_y + 1)]), OUT, 3.8 * s, n=6)
            gx_l = ec[0] + fx0 - r_bulat
            c.line(HH([(gx_l, eye_y - 1), (-face_rx + 1 if p.get("telinga") else gx_l - 10 * fs, 2 if p.get("telinga") else eye_y - 5)]), OUT, 3.6 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + rx_r
                c.line(HH([(gx_r, eye_y - 1), (min(face_rx - 1, gx_r + 10 * fs * (1.0 - turn)), eye_y - 5)]), OUT, 3.6 * s)
        elif p.get("kacamata"):
            for ex_ in ec:
                c.poly(HH(_ellpts(ex_ + fx0, eye_y, 27 * (1.0 - 0.12 * turn), 27, 22)), (255, 255, 255, 70), ow * .95, OUT)
            c.line(HH([(ec[0] + 27 * (1.0 - 0.12 * turn) + fx0, eye_y - 3), (ec[1] - 27 * (1.0 - 0.12 * turn) + fx0, eye_y - 3)]), OUT, 4.2 * s)
        # hidung mungil (aktif saat hadap miring 3/4, atau hidung tipis halus pada wajah_pintar)
        if turn >= 0.28:
            nx_n = fx0 + 6.0 * turn
            ny_n = eye_y + 24.0 * fs
            c.curve(HH([(nx_n - 2.0, ny_n - 5.0), (nx_n + 5.5 * turn, ny_n + 1.0), (nx_n - 1.0, ny_n + 5.5)]), OUT, 3.2 * s)
        elif p.get("wajah_chibi_ref"):
            # hidung cowok tegas minimalis: garis batang + sudut hidung kecil (bukan titik bulat imut)
            nx_n = fx0 + 1.5
            ny_n = eye_y + 23.0
            c.line(HH([(nx_n - 0.5, ny_n - 6.0), (nx_n + 2.0, ny_n + 1.0), (nx_n - 2.0, ny_n + 3.0)]), (136, 98, 84), 2.1 * s)
        elif p.get("wajah_pintar"):
            nx_n = fx0 + 1.5
            ny_n = eye_y + 23.0 * fs
            c.curve(HH([(nx_n - 1.0, ny_n - 3.5), (nx_n + 2.5, ny_n + 1.5), (nx_n - 1.5, ny_n + 3.5)]), (136, 98, 82), 2.4 * s)
        # freckles tipis khas karakter pintar Ghibli di pipi kiri & kanan
        if p.get("freckles"):
            fc_dot = (176, 128, 104, 150)
            for sg in (-1, 1):
                if turn >= 0.72 and sg > 0:
                    continue
                bx_f = fx0 + sg * 38 * fs * (1.0 - 0.16 * turn)
                by_f = eye_y + 25 * fs
                for dx_, dy_ in ((-6, 0), (0, 3), (6, -1)):
                    c.ell(*H(bx_f + dx_, by_f + dy_), 1.8 * s, 1.5 * s, fc_dot)

        # alis
        br = ex.get("brow")
        if br:
            lift, tl, tr = br
            for i, (bx, tv) in enumerate(((ec[0], tl), (ec[1], tr))):
                sg = -1 if i == 0 else 1
                by = eye_y - 29 * fs - lift - (5 if p.get("kacamata") in ("kotak", "bulat") else 0)
                outer = (bx + fx0 + sg * 16, by + tv * 10)
                inner = (bx + fx0 - sg * 16, by - tv * 10)
                mid = (bx + fx0, by - 4 + (4 if abs(tv) > .5 else 0) + (-5 if lift > 6 else 0))
                c.curve(HH([outer, mid, inner]), OUT, (5.2 if mask else (4.2 if chibi_eye else 5.0)) * s)
        elif p.get("wajah_chibi_ref"):
            # alis cowok hitam-arang tebal & garang: dekat di atas mata, menukik tajam ke arah pangkal hidung!
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 21.5
                c.poly(HH([
                    (bx + fx0 - sg * 17, by + 4.5),
                    (bx + fx0 - sg * 15, by - 1.5),
                    (bx + fx0 + sg * 6, by - 6.0),
                    (bx + fx0 + sg * 20, by - 2.0),
                    (bx + fx0 + sg * 17, by + 1.5),
                    (bx + fx0 + sg * 4, by - 1.2),
                ]), (24, 20, 22))
                # garis kerutan halus pangkal alis (brow ridge) menambah kesan cowok garang/fokus
                c.line(HH([(bx + fx0 - sg * 15, by + 5.5), (bx + fx0 - sg * 12, by + 8.0)]), (148, 110, 96), 1.4 * s)
        elif p.get("alis_tebal"):
            # alis tebal maskulin meruncing lembut di ujung luar (bukan kotak kaku!)
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 26
                c.poly(HH([
                    (bx + fx0 - sg * 20, by + 3), (bx + fx0 - sg * 18, by - 6),
                    (bx + fx0 + sg * 8, by - 7), (bx + fx0 + sg * 22, by - 1),
                    (bx + fx0 + sg * 18, by + 3), (bx + fx0 - sg * 10, by + 4),
                ]), (58, 56, 68))
        elif p.get("wajah_naa"):
            # alis melengkung tipis manis di atas mata besar (persis cewek @naa gambar 1!)
            for i, bx in enumerate(ec):
                by = eye_y - 31
                c.curve(HH([(bx + fx0 - 15, by + 3), (bx + fx0, by - 4), (bx + fx0 + 15, by + 3)]), (72, 56, 46), 3.0 * s)
        elif mask:
            # alis melengkung halus di atas kacamata (gaya uji-kribo 3D-stickman)
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 31 * fs
                c.curve(HH([(bx + fx0 + sg * 14, by + 2.5), (bx + fx0, by - 2.5),
                            (bx + fx0 - sg * 13, by + 1.5)]), OUT, 4.6 * s)
        elif chibi_eye or p.get("mata_sclera"):
            # alis melengkung lembut di atas kacamata bulat
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 34 * fs
                c.curve(HH([(bx + fx0 + sg * 14, by + 3), (bx + fx0, by - 2),
                            (bx + fx0 - sg * 13, by + 2)]), OUT, 3.8 * s)

        # pipi blush hangat + 3 garis miring kecil /// (khas chibi Ghibli gambar 1 & 2)
        if p.get("pipi_garis"):
            for sg in (-1, 1):
                if turn >= 0.72 and sg > 0:
                    continue
                bx_p = fx0 + sg * 48 * fs * (1.0 - 0.16 * turn)
                by_p = eye_y + 28 * fs
                c.poly(HH(_ellpts(bx_p, by_p, 16, 9.5, 14)), (242, 166, 134, 92))
                for k in (-5.5, 0.0, 5.5):
                    c.line(HH([(bx_p + k + 2.5, by_p - 4.5), (bx_p + k - 2.5, by_p + 4.5)]), (214, 134, 108), 2.0 * s)
        # pipi (hilangkan blush pink lebar pada mode maskulin kecuali saat sangat malu)
        bl = ex.get("blush", 0.0)
        if mask:
            bl = 0.45 if bl >= 0.95 else 0.0
        elif chibi_eye and bl > 0.02:
            bl = max(bl, 0.55)
        if bl > 0.02 and not p.get("wajah_chibi_ref"):
            bx_off = 48 if chibi_eye else 58
            by_off = (eye_y + 24 * fs) if chibi_eye else (28 * fs + fy0 * .4)
            for sg in (-1, 1):
                c.poly(HH(_ellpts(sg * bx_off * fs + fx0 * .6, by_off, 17, 10.5, 16)), (255, 140, 160, int(150 * bl)))
        # mulut
        self._mouth(c, st, ex, HH, s, ow, fs, fx0, fy0)
        # kumis jenggot
        if p.get("kumis"):
            uc = hair_c if p.get("rambut") != "botak" else (220, 220, 224)
            c.blob(HH([(-40, 28), (-18, 20), (0, 24), (18, 20), (40, 28), (20, 36), (0, 30), (-20, 36)]), uc, ow * .8, OUT)
        if p.get("jenggot"):
            c.blob(HH([(-60, 52), (-30, 82), (0, 100), (30, 82), (60, 52), (40, 70), (0, 76), (-40, 70)]), (224, 224, 228), ow * .8, OUT)
        # tetes keringat / air mata / urat marah
        if ex.get("sweat"):
            sx, sy = 72, -52
            c.poly(HH([(sx, sy - 24), (sx + 12, sy), (sx + 8, sy + 14), (sx - 8, sy + 14), (sx - 12, sy)]), BIRU_MUDA, ow * .7, OUT)
        if ex.get("tear"):
            for sg in (-1, 1):
                c.poly(HH([(sg * 40, 22), (sg * 40 + 8, 46), (sg * 40, 56), (sg * 40 - 8, 46)]), BIRU_MUDA, ow * .6, OUT)
        if ex.get("vein"):
            vx, vy = 58, -76
            for ang in (0, 90):
                a = math.radians(ang)
                for sg in (-1, 1):
                    pts = [(vx + sg * 4 * math.cos(a), vy + sg * 4 * math.sin(a)), (vx + sg * 13 * math.cos(a), vy + sg * 13 * math.sin(a))]
                c.curve(HH(arc_pts(vx - 7, vy - 7, 9, 9, 90, 0, 6)), MERAH, 4.4 * s)
                c.curve(HH(arc_pts(vx + 7, vy - 7, 9, 9, 180, 90, 6)), MERAH, 4.4 * s)
                c.curve(HH(arc_pts(vx - 7, vy + 7, 9, 9, 0, -90, 6)), MERAH, 4.4 * s)
                c.curve(HH(arc_pts(vx + 7, vy + 7, 9, 9, -90, -180, 6)), MERAH, 4.4 * s)
                break

    def _hair_front(self, c, H, HH, s, ow, r, hc, p):
        if r in (None, "botak"):
            return
        if r == "kribo_chibi":
            self._hair_front_ref(c, HH, s, hc)
        elif False:
            # PONI IKAL LEBAR MELENGKUNG LEMBUT (BUKAN gigi hiu tajam!) — persis gaya poni ikal referensi
            oc_h = (28, 24, 30)
            ow_h = 2.2 * s
            # tutup penuh dahi atas menyatu mulus ke rambut atas
            cap_top = arc_pts(0, -18, 114, 96, 178, 362, 20)
            c.poly(HH(cap_top + [(108, -18), (64, -44), (0, -52), (-64, -44), (-108, -18)]), hc)
            # 5 helai poni ikal lebar & melengkung lembut (tengah lebih tebal melengkung ke kiri-kanan)
            bang_curls = [
                ((-108, -32), (-112, 0), (-96, 26), (-82, -26)),      # jambang kiri
                ((-84, -48), (-82, -14), (-60, 0), (-42, -44)),       # poni kiri lebar melengkung
                ((-42, -56), (-36, -14), (-6, 4), (10, -48)),         # poni tengah besar melengkung lembut!
                ((8, -56), (26, -16), (48, 2), (56, -46)),            # poni kanan melengkung
                ((58, -46), (82, -14), (96, 26), (94, -24)),          # jambang kanan
            ]
            for p0, pm, tip, p1 in bang_curls:
                e1 = bezier(p0, pm, tip, 6)
                e2 = list(reversed(bezier(p1, ((pm[0] + p1[0]) * 0.52, (pm[1] + tip[1]) * 0.55), tip, 6)))
                c.poly(HH(e1 + e2), hc, ow_h, oc_h)
            # haluskan pangkal poni & tambah 2 goresan ikal halus
            c.poly(HH(cap_top + [(104, -36), (62, -52), (0, -58), (-62, -52), (-104, -36)]), hc)
            sh_c = gelap(hc, 0.34)
            for cx_, cy_ in ((-46, -46), (4, -52), (50, -44)):
                c.curve(HH([(cx_ - 18, cy_ + 4), (cx_, cy_ - 10), (cx_ + 18, cy_ + 3)]), sh_c, 2.2 * s)
        elif r == "afro":
            # poni & jambang keriting menyatu mulus ke massa afro belakang (proporsional untuk HEAD_R=92)
            bangs = [
                (-92, -8, 19), (-82, -34, 21), (-65, -58, 22),
                (-38, -74, 22), (0, -80, 23), (38, -74, 22),
                (65, -58, 22), (82, -34, 21), (92, -8, 19),
            ]
            for bx, by, br in bangs:
                c.ell(*H(bx, by), br * s + ow * .72, br * s + ow * .72, OUT)
            cap_top = arc_pts(0, -16, 98, 98, 174, 366, 18)
            cap_bot = [(bx, by) for bx, by, _ in reversed(bangs)]
            c.poly(HH(cap_top + cap_bot), hc)
            for bx, by, br in bangs:
                c.ell(*H(bx, by), br * s, br * s, hc)
        elif r == "jambul":
            outer, inner = [], []
            n = 8
            for i in range(n * 2 + 1):
                a = 196 + (344 - 196) * i / (n * 2)
                rr = HEAD_R + (36 if i % 2 else 6) + (10 if 5 <= i <= 11 and i % 2 else 0)
                outer.append((math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr))
            for i in range(14, -1, -1):
                a = 196 + (344 - 196) * i / 14
                rr = HEAD_R * (0.74 + 0.08 * math.sin(i * 1.7))
                inner.append((math.cos(math.radians(a)) * rr * 1.0, math.sin(math.radians(a)) * rr * 1.0 + 6))
            c.poly(HH(outer + inner), hc, ow * .9, OUT)
        elif r == "keriting":
            for i, a in enumerate(range(200, 345, 18)):
                rr = HEAD_R * 0.8
                c.ell(*H(math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr + 4), 26 * s, 26 * s, hc, ow * .9, OUT)
        elif r in ("rapi", "uban"):
            top = arc_pts(0, 0, HEAD_R + 5, HEAD_R + 5, 188, 352, 20)
            fringe = [(70, -50), (40, -62), (10, -48), (-18, -60), (-48, -46), (-72, -52)]
            c.poly(HH(top + fringe), hc, ow * .9, OUT)
        elif r == "bob":
            top = arc_pts(0, 0, HEAD_R + 6, HEAD_R + 6, 176, 364, 22)
            fr = [(88, 4), (80, -48), (40, -58), (0, -48), (-40, -58), (-80, -48), (-88, 4)]
            c.poly(HH(top + fr), hc, ow * .9, OUT)
        elif r == "panjang_naa":
            # poni lembut berhelai panjang melengkung (tapered bezier locks, bukan gergaji!) persis cewek @naa gambar 1
            oc_h = (64, 50, 42)
            ow_h = 2.6 * s
            top = arc_pts(0, -10, HEAD_R + 8, HEAD_R + 8, 178, 362, 24)
            # base dahi rambut halus
            c.poly(HH(top + [(98, -14), (66, -54), (16, -68), (-34, -64), (-78, -42), (-100, -10)]), hc, ow_h, oc_h)
            # 5 helai poni melengkung lembut jatuh asimetris melewati dahi (meruncing halus di ujung!)
            locks = [
                ((-84, -46), (-98, 2), (-90, 62), (-74, -18)),     # sisi kiri pipi
                ((-58, -60), (-72, -24), (-64, 6), (-42, -34)),    # poni kiri
                ((-22, -68), (-34, -30), (-36, 4), (-6, -42)),     # poni tengah-kiri
                ((14, -70), (2, -32), (-8, 2), (28, -46)),         # poni tengah-kanan melengkung kiri
                ((56, -60), (74, -16), (86, 62), (76, -24)),       # sisi kanan pipi
            ]
            for p0, pm, tip, p1 in locks:
                e1 = bezier(p0, pm, tip, 6)
                e2 = list(reversed(bezier(p1, ((pm[0] + p1[0]) * 0.5, (pm[1] + tip[1]) * 0.5), tip, 6)))
                c.poly(HH(e1 + e2), hc, ow_h * 0.8, oc_h)
            # highlight rambut coklat muda hangat di puncak kepala
            hl_h = terang(hc, 0.28)
            for hx_, hy_, rx_, ry_ in ((-54, -72, 13, 6), (-18, -84, 16, 6), (26, -82, 14, 6), (58, -70, 11, 5)):
                c.ell(*H(hx_, hy_), rx_ * s, ry_ * s, hl_h)
        elif r == "comma":
            # rambut atas bervolume + 2 helai poni comma meruncing elegan (poligon bezier halus, bukan garis cacing!)
            oc_h = (46, 46, 62)
            ow_h = 2.6 * s
            # massa rambut belah samping-tengah bervolume (membuka dahi secara alami seperti gambar 2!)
            c.blob(HH([
                (-104, -12), (-106, -54), (-84, -96), (-36, -122), (-4, -100),
                (-18, -72), (-52, -62), (-82, -36), (-94, -4),
            ]), hc, ow_h, oc_h, n=5)
            c.blob(HH([
                (-6, -104), (36, -124), (84, -98), (108, -54), (104, -12),
                (94, -4), (80, -38), (46, -64), (12, -74),
            ]), hc, ow_h, oc_h, n=5)
            # 2 helai poni comma tipis meruncing lembut melengkung di samping dahi (persis gambar 2!)
            for (p0, pm, tip, p1) in (
                ((-24, -84), (-52, -56), (-38, -22), (-14, -76)),
                ((16, -82), (42, -54), (28, -22), (8, -74)),
            ):
                e1 = bezier(p0, pm, tip, 6)
                e2 = list(reversed(bezier(p1, (pm[0] * 0.84, pm[1] + 4), tip, 6)))
                c.poly(HH(e1 + e2), hc, ow_h * 0.72, oc_h)
            # highlight biru-ungu lembut di gelombang rambut
            hl_c = terang(mix(hc, (150, 158, 194), 0.35), 0.24)
            for hx_, hy_, rx_, ry_ in ((-48, -90, 18, 7), (20, -96, 22, 8), (62, -80, 14, 6)):
                c.ell(*H(hx_, hy_), rx_ * s, ry_ * s, hl_c)
        elif r == "panjang":
            # poni lembut berhelai + highlight oval hangat di rambut cewek (gambar 2)
            top = arc_pts(0, -4, HEAD_R + 6, HEAD_R + 4, 184, 356, 22)
            fringe = [
                (86, 12), (76, -34), (56, -18), (44, -48),
                (18, -22), (8, -56), (-18, -24), (-36, -54),
                (-60, -24), (-78, -42), (-88, 12),
            ]
            c.poly(HH(top + fringe), hc, ow * .85, OUT)
            # highlight rambut hangat di sisi atas (khas chibi Ghibli gambar 2)
            hl_h = terang(hc, 0.24)
            for hx_, hy_, rx_, ry_ in ((-46, -68, 11, 6), (-14, -76, 14, 6), (26, -74, 12, 6), (56, -64, 9, 5)):
                c.ell(*H(hx_, hy_), rx_ * s, ry_ * s, hl_h)
        elif r == "kuncir":
            top = arc_pts(0, 0, HEAD_R + 4, HEAD_R + 4, 190, 350, 18)
            fr = [(74, -46), (44, -64), (14, -50), (-14, -66), (-48, -50), (-76, -50)]
            c.poly(HH(top + fr), hc, ow * .9, OUT)
            c.ell(*H(0, -HEAD_R - 22), 24 * s, 24 * s, hc, ow * .9, OUT)

    def _mouth(self, c, st, ex, HH, s, ow, fs, fx0, fy0):
        kind = ex.get("mouth", "open")
        talk = st.get("talk")
        op = ex.get("open", 0.6)
        if talk is not None:
            if kind in ("o", "yawn"):
                op = 0.5 + 0.5 * talk
            else:
                kind = "open"
                op = 0.12 + 0.88 * talk
        mx, my = fx0 * .6, (49 if self.p.get("wajah_chibi_ref") else (50 if self.p.get("mata_chibi") else 44)) * fs + fy0 * .4
        k = ex.get("small", 1.0) * (0.76 if self.p.get("mata_chibi") and talk is None and kind == "open" else 1.0)

        def D(w, d):
            m_col = (206, 126, 102) if self.p.get("outline_hangat") else MERAH_TUA
            t_col = (232, 160, 134) if self.p.get("outline_hangat") else LIDAH
            oc_m = (64, 52, 46) if self.p.get("outline_hangat") else OUT
            top = [(mx - w, my - 1), (mx - w * .5, my - 4), (mx + w * .5, my - 4), (mx + w, my - 1)]
            bot = arc_pts(mx, my - 1, w, d, 0, 180, 14)
            c.poly(HH(top + bot), m_col, ow * .82, oc_m)
            if d > 14:
                c.poly(HH(_ellpts(mx, my + d * .62, w * .5, d * .32, 14)), t_col)
            return
        if kind == "open":
            D(23 * k, lerp(5, 30, op))
        elif kind == "grin":
            D(31, lerp(14, 38, op))
        elif kind == "smile":
            if self.p.get("wajah_arka") or self.p.get("wajah_chibi_ref"):
                # mulut senyum halus melengkung lembut persis gambar referensi (bukan V lancip!)
                c.line(HH([(mx - 13, my + 2.0), (mx + 2, my + 2.5), (mx + 15, my - 1.2)]), (86, 54, 48), 2.7 * s)
            else:
                c.curve(HH(arc_pts(mx, my - 14, 25, 22, 28, 152, 10)), (64, 52, 46) if self.p.get("outline_hangat") else OUT, 4.4 * s)
        elif kind == "o":
            c.poly(HH(_ellpts(mx, my + 6, 12 + 4 * (op - 0.6), 15 + 6 * (op - 0.6), 16)), MERAH_TUA, ow * .85, OUT)
        elif kind == "yawn":
            c.poly(HH(_ellpts(mx, my + 8, 21, 28 * (0.7 + 0.3 * op), 18)), MERAH_TUA, ow * .85, OUT)
            c.poly(HH(_ellpts(mx, my + 20, 12, 8, 12)), LIDAH)
        elif kind == "frown":
            c.curve(HH(arc_pts(mx, my + 22, 22, 15, 205, 335, 10)), OUT, 4.8 * s)
        elif kind == "flat":
            c.line(HH([(mx - 15, my + 4), (mx + 15, my + 4)]), OUT, 4.8 * s)
        elif kind == "flat_miring":
            c.line(HH([(mx - 14, my + 8), (mx + 16, my)]), OUT, 4.8 * s)
        elif kind == "gigit":     # marah menggeram
            c.poly(HH([(mx - 26, my + 2), (mx + 26, my + 2), (mx + 22, my + 20), (mx - 22, my + 20)]), PUTIH, ow * .8, OUT)
            for xx in (-12, 0, 12):
                c.line(HH([(mx + xx, my + 2), (mx + xx, my + 20)]), OUT, 2.8 * s)
        elif kind == "wave":
            pts = [(mx - 22 + i * 4.4, my + 6 + 4.2 * math.sin(i * 1.6)) for i in range(11)]
            c.line(HH(pts), OUT, 4.4 * s)
        elif kind == "wave_o":
            c.poly(HH(_ellpts(mx, my + 8, 14, 12, 14)), MERAH_TUA, ow * .85, OUT)
        elif kind == "smirk":
            c.curve(HH([(mx - 20, my + 2), (mx + 4, my + 10), (mx + 24, my - 8)]), OUT, 4.8 * s)
        elif kind == "pout":
            c.curve(HH(arc_pts(mx, my + 14, 13, 8, 205, 335, 8)), OUT, 4.8 * s)


def pose_state(name, t=0.0):
    """Nama pose -> dict lengan/kaki/duduk/miring pada waktu t (animasi lambai dsb. ikut t)."""
    d = pose_def(name)
    L, R = list(d["L"]), list(d["R"])
    w = d.get("wave", "")
    if "R" in w:
        R[1] += 24 * math.sin(t * 9.0)
        R[0] += 4 * math.sin(t * 4.5)
    if "L" in w:
        L[1] += 24 * math.sin(t * 9.0 + 1.3)
    return dict(arms={"L": tuple(L), "R": tuple(R)}, legs=d["legs"], sit=d["sit"], lean=d["lean"], tilt=d["tilt"],
                swing=d.get("swing", 1.0))


def blink_at(t, seed=0.0):
    """0..1 kedip: sekali tiap ±3.3 detik."""
    q = (t + seed * 1.7) % 3.3
    return 1.0 - abs(q - 3.22) / 0.08 if 3.14 < q < 3.30 else 0.0


def state(pose="diam", expr="senang", x=0, y=0, s=1.0, flip=1, t=0.0, **over):
    st = dict(x=x, y=y, s=s, flip=flip, expr=expr, look=(0.0, 0.0), blink=0.0, phase=0.0, amp=0.0)
    ps = pose_state(pose, t)
    st.update(ps)
    st.update(over)
    return st
