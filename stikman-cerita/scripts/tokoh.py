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

HEAD_R = 100.0
HEAD_Y = -345.0          # pusat kepala (berdiri)
SHOULDER_Y = -246.0
HIP_Y = -150.0
SIT_DROP = 70.0
UP_ARM = 66.0
FORE_ARM = 62.0
SHOULDER_X = 40.0

# ------------------------------------------------------------------ casting
# Semua field opsional. rambut: afro jambul keriting rapi botak kuncir bob uban
PRESET = {
    "kribo":  dict(nama="Kribo", rambut="afro", rambut_warna=HITAM, kulit=(255, 224, 196),
                   kacamata="kotak", wajah_maskulin=True, kemeja=(84, 124, 128), krah=False, kancing=False,
                   dasi=None, dasi_kupu=True, lengan_tebal=True, sepatu_sneaker=True,
                   badan_lebar=2.05, pinggul_lebar=1.8, bahu_x=76.0, lengan_besar=1.25,
                   hip_y=-105.0, kaki_tebal=2.4, kaki_lebar=1.7, sepatu_besar=1.25, tangan_besar=1.22,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "raka":   dict(nama="Raka", rambut="jambul", rambut_warna=HITAM, kemeja=PUTIH, dasi=BIRU,
                   badan_lebar=1.85, pinggul_lebar=1.68, bahu_x=73.0, lengan_besar=1.18,
                   hip_y=-112.0, kaki_tebal=2.15, kaki_lebar=1.55, sepatu_besar=1.2, tangan_besar=1.16,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "nadia":  dict(nama="Nadia", hijab=(32, 32, 40), hijab_tua=(76, 78, 92), hijab_gaya="modern",
                   kulit=(255, 224, 196), kacamata="bulat", mata_chibi=True, bulu_mata=False,
                   kemeja=(224, 194, 154), kemeja_dalam=PUTIH, blazer=True, krah=False, kancing=False, dasi=None,
                   lengan_tebal=True, lengan_panjang=True,
                   badan_lebar=1.74, pinggul_lebar=1.64, bahu_x=68.0, lengan_besar=1.14,
                   hip_y=-114.0, kaki_tebal=2.0, kaki_lebar=1.48, sepatu_besar=1.18, tangan_besar=1.12,
                   bawah="rok", bawah_warna=(44, 44, 52), sepatu=(68, 52, 46)),
    "bimo":   dict(nama="Bimo", rambut="keriting", rambut_warna=(62, 40, 34), kemeja=PUTIH, dasi=BIRU,
                   badan_lebar=1.85, pinggul_lebar=1.68, bahu_x=73.0, lengan_besar=1.18,
                   hip_y=-112.0, kaki_tebal=2.15, kaki_lebar=1.55, sepatu_besar=1.2, tangan_besar=1.16,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "dimas":  dict(nama="Dimas", rambut="rapi", rambut_warna=HITAM, kacamata=True, kemeja=PUTIH, dasi=BIRU,
                   badan_lebar=1.85, pinggul_lebar=1.68, bahu_x=73.0, lengan_besar=1.18,
                   hip_y=-112.0, kaki_tebal=2.15, kaki_lebar=1.55, sepatu_besar=1.2, tangan_besar=1.16,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "sari":   dict(nama="Sari", hijab=(250, 250, 252), hijab_tua=ABU, kemeja=PUTIH, dasi=MERAH,
                   badan_lebar=1.74, pinggul_lebar=1.64, bahu_x=68.0, lengan_besar=1.14,
                   hip_y=-114.0, kaki_tebal=2.0, kaki_lebar=1.48, sepatu_besar=1.18, tangan_besar=1.12,
                   bawah="rok", bawah_warna=(44, 44, 52), bulu_mata=True),
    "tika":   dict(nama="Tika", rambut="kuncir", rambut_warna=HITAM, kemeja=PUTIH, dasi=MERAH,
                   badan_lebar=1.74, pinggul_lebar=1.64, bahu_x=68.0, lengan_besar=1.14,
                   hip_y=-114.0, kaki_tebal=2.0, kaki_lebar=1.48, sepatu_besar=1.18, tangan_besar=1.12,
                   bawah="rok", bawah_warna=(44, 44, 52), bulu_mata=True),
    "ayah":   dict(nama="Ayah", rambut="rapi", rambut_warna=(70, 70, 80), kumis=True, kemeja=(200, 224, 250), dasi=None,
                   badan_lebar=1.92, pinggul_lebar=1.74, bahu_x=75.0, lengan_besar=1.2,
                   hip_y=-110.0, kaki_tebal=2.2, kaki_lebar=1.6, sepatu_besar=1.2, tangan_besar=1.18,
                   bawah="celana", bawah_warna=NAVY, skala=1.08),
    "ibu":    dict(nama="Ibu", hijab=HIJAU, hijab_tua=HIJAU_TUA, kemeja=(250, 236, 214), dasi=None,
                   badan_lebar=1.76, pinggul_lebar=1.66, bahu_x=68.0, lengan_besar=1.14,
                   hip_y=-114.0, kaki_tebal=2.0, kaki_lebar=1.48, sepatu_besar=1.18, tangan_besar=1.12,
                   bawah="rok", bawah_warna=COKLAT_TUA, bulu_mata=True, skala=1.04),
    "guru":   dict(nama="Pak Guru", rambut="uban", rambut_warna=(205, 205, 212), kacamata=True, kumis=True, kemeja=(236, 232, 214), dasi=MERAH_TUA,
                   badan_lebar=1.92, pinggul_lebar=1.74, bahu_x=75.0, lengan_besar=1.2,
                   hip_y=-110.0, kaki_tebal=2.2, kaki_lebar=1.6, sepatu_besar=1.2, tangan_besar=1.18,
                   bawah="celana", bawah_warna=NAVY, skala=1.06),
    "bu_guru": dict(nama="Bu Guru", hijab=UNGU, hijab_tua=UNGU_TUA, kacamata=True, kemeja=(240, 232, 250), dasi=None,
                    badan_lebar=1.76, pinggul_lebar=1.66, bahu_x=68.0, lengan_besar=1.14,
                    hip_y=-114.0, kaki_tebal=2.0, kaki_lebar=1.48, sepatu_besar=1.18, tangan_besar=1.12,
                    bawah="rok", bawah_warna=UNGU_TUA, bulu_mata=True, skala=1.04),
    "kakek":  dict(nama="Kakek", rambut="botak", peci=True, kumis=True, jenggot=True, kemeja=(250, 250, 250), dasi=None,
                   badan_lebar=1.88, pinggul_lebar=1.7, bahu_x=73.0, lengan_besar=1.18,
                   hip_y=-112.0, kaki_tebal=2.15, kaki_lebar=1.55, sepatu_besar=1.18, tangan_besar=1.16,
                   bawah="celana", bawah_warna=(90, 70, 60), skala=0.98, uban=True),
    "adik":   dict(nama="Adik", rambut="bob", rambut_warna=HITAM, kemeja=(255, 226, 120), dasi=None,
                   badan_lebar=1.72, pinggul_lebar=1.62, bahu_x=67.0, lengan_besar=1.12,
                   hip_y=-114.0, kaki_tebal=1.95, kaki_lebar=1.45, sepatu_besar=1.16, tangan_besar=1.12,
                   bawah="rok", bawah_warna=PINK_TUA, bulu_mata=True, skala=0.8),
    "otak":   dict(nama="Sang Otak", kepala="otak", kulit=(250, 174, 198), mata_chibi=True, bulu_mata=False,
                   kemeja=(242, 248, 255), krah=True, kancing=True, dasi=(66, 178, 232),
                   lengan_tebal=True, lengan_panjang=True, sepatu_sneaker=True,
                   badan_lebar=1.82, pinggul_lebar=1.68, bahu_x=72.0, lengan_besar=1.16,
                   hip_y=-112.0, kaki_tebal=2.1, kaki_lebar=1.52, sepatu_besar=1.2, tangan_besar=1.15,
                   bawah="celana", bawah_warna=(54, 68, 96), sepatu=(52, 62, 86)),
    "virus":  dict(nama="Virus", kepala="virus", kulit=(112, 204, 88), wajah_maskulin=True, bulu_mata=False,
                   kemeja=(66, 138, 64), krah=False, kancing=False, dasi=None,
                   lengan_tebal=True, lengan_besar=1.12, badan_lebar=1.76, pinggul_lebar=1.62, bahu_x=68.0,
                   hip_y=-114.0, kaki_tebal=2.0, kaki_lebar=1.48, sepatu_besar=1.16, tangan_besar=1.12,
                   bawah="celana", bawah_warna=(44, 86, 48), sepatu=(36, 62, 40), skala=0.84),
    "sel_imun": dict(nama="Sel Imun", kepala="sel_imun", kulit=(236, 248, 255), mata_chibi=True, bulu_mata=False,
                     kemeja=(78, 172, 242), krah=False, kancing=False, dasi=None, perisai_dada=True,
                     lengan_tebal=True, lengan_panjang=True, sepatu_sneaker=True,
                     badan_lebar=1.84, pinggul_lebar=1.7, bahu_x=72.0, lengan_besar=1.16,
                     hip_y=-112.0, kaki_tebal=2.1, kaki_lebar=1.52, sepatu_besar=1.2, tangan_besar=1.15,
                     bawah="celana", bawah_warna=(52, 108, 176), sepatu=(44, 86, 148), skala=0.94),
    "bos": dict(nama="Bos", rambut="botak", telinga=True, kacamata="bulat", mata_sclera=True,
                kulit=(248, 214, 194), kemeja=(48, 52, 64), kemeja_dalam=PUTIH, blazer=True, dasi=MERAH,
                lengan_tebal=True, lengan_panjang=True,
                badan_lebar=1.95, pinggul_lebar=1.75, bahu_x=76.0, lengan_besar=1.22,
                hip_y=-108.0, kaki_tebal=2.25, kaki_lebar=1.62, sepatu_besar=1.22, tangan_besar=1.2,
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
    base.setdefault("badan_lebar", 1.82)
    base.setdefault("pinggul_lebar", 1.66)
    base.setdefault("bahu_x", 68.0)
    base.setdefault("lengan_besar", 1.18)
    base.setdefault("tangan_besar", 1.16)
    base.setdefault("hip_y", -114.0)
    base.setdefault("kaki_tebal", 2.15)
    base.setdefault("kaki_lebar", 1.55)
    base.setdefault("sepatu_besar", 1.2)
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

        ow = 4.6 * s           # tebal garis tepi (satuan dunia)
        kemeja = warna(p.get("kemeja"), PUTIH)
        kulit = warna(p.get("kulit"), PUTIH)
        dasi = warna(p.get("dasi"))
        bawah_c = warna(p.get("bawah_warna"), HITAM)
        sepatu = warna(p.get("sepatu"), HITAM)
        # proporsi badan: seluruh tokoh memakai gaya chibi berisi & garis tepi seragam
        bw = float(p.get("badan_lebar", 1.82))
        hipb = float(p.get("pinggul_lebar", bw))
        hy = float(p.get("hip_y", -114.0))
        kt = float(p.get("kaki_tebal", 2.15))
        sm = float(p.get("sepatu_besar", 1.2))

        # ransel (bagian belakang)
        if st.get("ransel"):
            rc = warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU
            rw = max(1.0, bw * 0.62)
            c.blob(TT([(-70 * rw, -258), (-84 * rw, -230), (-80 * rw, -176), (-52 * rw, -150),
                       (52 * rw, -150), (80 * rw, -176), (84 * rw, -230), (70 * rw, -258), (0, -270)]),
                   rc, ow, OUT)
            c.ell(*T(-74 * rw, -214), 14 * s, 26 * s, gelap(rc, 0.18), ow * .85)
            c.ell(*T(74 * rw, -214), 14 * s, 26 * s, gelap(rc, 0.18), ow * .85)

        # ---- kaki
        hipy = hy + dy
        hip = [T(-20, hy), T(20, hy)]
        feet, knees, hip = self._legs(st, T, sit)
        skirt = p.get("bawah") == "rok"
        legw = (12.8 if skirt else 15.0) * kt
        legc = (60, 58, 70) if (skirt and (p.get("hijab") or bawah_c == HITAM)) else (gelap(bawah_c, .42) if skirt else bawah_c)
        legoc = OUT
        for i in (0, 1):
            ax, ay = hip[i]
            kx, ky = knees[i]
            fx, fy = feet[i]
            c.line([(ax, ay), (kx, ky), (fx, fy)], legoc, (legw + 2 * 4.2) * s)
            c.line([(ax, ay), (kx, ky), (fx, fy)], legc, legw * s)
            if p.get("sepatu_sneaker"):
                toe = -1 if i == 0 else 1          # ujung sepatu menghadap keluar -> simetris
                shoe_x, shoe_y = fx + toe * fl * 7 * s * sm, fy - 4 * s * sm
                c.ell(shoe_x, shoe_y, 27 * s * sm, 13 * s * sm, sepatu, ow * .82, OUT)
                c.ell(fx + toe * fl * 16 * s * sm, shoe_y, 10.5 * s * sm, 9.5 * s * sm, PUTIH, ow * .65, OUT)
                c.line([(fx - toe * fl * 21 * s * sm, fy + 6 * s * sm),
                        (fx + toe * fl * 22 * s * sm, fy + 6 * s * sm)], PUTIH, 4.2 * s * sm)
            else:
                toe = (-1 if i == 0 else 1) if bw > 1.2 else 1
                c.ell(fx + toe * fl * 7 * s * sm, fy - 4 * s * sm, 27 * s * sm, 13 * s * sm, sepatu, ow * .82, OUT)
        if skirt:
            hem = hy + 64 + dy * 0.9
            sw = max(1.0, hipb * 0.94)
            c.poly(TT([(-36 * sw, hy - 12), (36 * sw, hy - 12), (60 * sw, hem - 4)] + bezier((60 * sw, hem - 4), (0, hem + 22), (-60 * sw, hem - 4), 10)[1:-1] + [(-60 * sw, hem - 4)]),
                   bawah_c, ow, OUT)
        if not skirt and bw > 1.2:
            c.poly(TT([(-34 * hipb, hy - 14), (34 * hipb, hy - 14),
                       (34 * hipb, hy + 22), (-34 * hipb, hy + 22)]), bawah_c, ow, OUT)
        elif not skirt and p.get("blazer"):
            px_w = max(26.0 * hipb, 20.0 * float(p.get("kaki_lebar", 1.0)) + 7.5 * kt)
            c.poly(TT([(-px_w, hy - 14), (px_w, hy - 14), (px_w, hy + 6), (-px_w, hy + 6)]), bawah_c, ow, OUT)
            for i in (0, 1):
                c.line([hip[i], knees[i]], legc, legw * s)
        # ---- torso
        if p.get("blazer"):
            inner_c = warna(p.get("kemeja_dalam"), PUTIH)
            lum = 0.299 * kemeja[0] + 0.587 * kemeja[1] + 0.114 * kemeja[2]
            lap_c = gelap(kemeja, 0.14) if lum > 180 else terang(kemeja, 0.08)
            btn_y = min(hy - 26, SHOULDER_Y + 66)
            nx = min(19 * bw, 22.0)
            c.poly(TT([(-nx - 6, SHOULDER_Y), (nx + 6, SHOULDER_Y),
                       (8, btn_y + 8), (-8, btn_y + 8)]), inner_c, ow * .78, OUT)
            if p.get("krah", True) and not p.get("dasi_kupu"):
                c.poly(TT([(-4, SHOULDER_Y - 2), (-20, SHOULDER_Y - 1), (-13, SHOULDER_Y + 19)]), inner_c, ow * .8, OUT)
                c.poly(TT([(4, SHOULDER_Y - 2), (20, SHOULDER_Y - 1), (13, SHOULDER_Y + 19)]), inner_c, ow * .8, OUT)
            if dasi and not p.get("dasi_kupu"):
                c.poly(TT([(-4.5, SHOULDER_Y + 18), (4.5, SHOULDER_Y + 18),
                           (10.5, SHOULDER_Y + 52), (0, SHOULDER_Y + 66), (-10.5, SHOULDER_Y + 52)]), dasi, ow * .8, OUT)
                c.poly(TT([(-7, SHOULDER_Y + 8), (7, SHOULDER_Y + 8),
                           (5, SHOULDER_Y + 18), (-5, SHOULDER_Y + 18)]), dasi, ow * .8, OUT)
            for sg in (-1, 1):
                c.poly(TT([
                    (sg * nx, SHOULDER_Y - 1),
                    (sg * 31 * bw, SHOULDER_Y - 3),
                    (sg * 43 * bw, SHOULDER_Y + 6),
                    (sg * 41 * bw, SHOULDER_Y + 34),
                    (sg * 38 * hipb, hy - 38),
                    (sg * 35 * hipb, hy - 12),
                    (sg * 22 * hipb, hy - 9),
                    (sg * 2, hy - 10),
                    (0, btn_y),
                ]), kemeja, ow, OUT)
                c.poly(TT([
                    (sg * (nx - 1), SHOULDER_Y - 1),
                    (sg * (nx + 13 * bw * 0.72), SHOULDER_Y + 13),
                    (sg * (nx + 8 * bw * 0.72), SHOULDER_Y + 23),
                    (sg * (nx + 14 * bw * 0.72), SHOULDER_Y + 32),
                    (sg * 1.5, btn_y),
                    (sg * (nx - 4), SHOULDER_Y + 19),
                ]), lap_c, ow * .78, OUT)
                c.line(TT([(sg * (nx + 8 * bw * 0.72), SHOULDER_Y + 23), (sg * (nx - 4), SHOULDER_Y + 18)]), OUT, ow * .62)
            c.ell(*T(0, btn_y + 6), 3.3 * s, 3.3 * s, OUT)
            if hy - btn_y > 32:
                c.ell(*T(0, btn_y + 20), 3.1 * s, 3.1 * s, OUT)
        else:
            c.blob(TT([(-43 * bw, SHOULDER_Y + 6), (-30 * bw, SHOULDER_Y - 3), (30 * bw, SHOULDER_Y - 3),
                       (43 * bw, SHOULDER_Y + 6), (38 * hipb, hy - 44), (35 * hipb, hy - 12),
                       (0, hy - 7), (-35 * hipb, hy - 12), (-38 * hipb, hy - 44)]),
                   kemeja, ow, OUT, n=5)
        if p.get("kemeja_garis"):
            gc = warna(p["kemeja_garis"], BIRU)
            for yy in (-215, -192, -170):
                if yy < hy - 14:
                    c.line(TT([(-36 * bw, yy), (36 * bw, yy)]), gc, 6 * s, False)
        if p.get("perisai_dada"):
            # lencana perisai putih-biru di dada sel imun
            by = SHOULDER_Y + 46
            c.poly(TT([(0, by - 22), (22, by - 14), (18, by + 10), (0, by + 24), (-18, by + 10), (-22, by - 14)]), PUTIH, ow * .8, OUT)
            c.line(TT([(0, by - 10), (0, by + 10)]), BIRU, 5.5 * s, False)
            c.line(TT([(-10, by), (10, by)]), BIRU, 5.5 * s, False)
        # krah + dasi (dasi kupu-kupu menggantikan krah/dasi biasa)
        if not p.get("blazer"):
            if p.get("krah", True) and not p.get("dasi_kupu"):
                c.poly(TT([(-4, SHOULDER_Y - 2), (-20, SHOULDER_Y - 1), (-13, SHOULDER_Y + 19)]), PUTIH, ow * .82, OUT)
                c.poly(TT([(4, SHOULDER_Y - 2), (20, SHOULDER_Y - 1), (13, SHOULDER_Y + 19)]), PUTIH, ow * .82, OUT)
            if p.get("dasi_kupu"):
                bc = warna(p.get("dasi"), HITAM)
                by = SHOULDER_Y + 12
                boww = 18
                c.poly(TT([(0, by), (-boww, by - 10), (-boww, by + 10)]), bc, ow * .82, OUT)
                c.poly(TT([(0, by), (boww, by - 10), (boww, by + 10)]), bc, ow * .82, OUT)
                c.poly(TT([(-6, by - 7), (6, by - 7), (6, by + 7), (-6, by + 7)]), gelap(bc, .12), ow * .8, OUT)
            elif dasi:
                c.poly(TT([(-4.5, SHOULDER_Y + 18), (4.5, SHOULDER_Y + 18),
                           (10.5, SHOULDER_Y + 52), (0, SHOULDER_Y + 66), (-10.5, SHOULDER_Y + 52)]), dasi, ow * .82, OUT)
                c.poly(TT([(-7, SHOULDER_Y + 8), (7, SHOULDER_Y + 8),
                           (5, SHOULDER_Y + 18), (-5, SHOULDER_Y + 18)]), dasi, ow * .82, OUT)
            elif p.get("kancing", True):
                for yy in (-222, -200, -178):
                    if yy < hy - 16:
                        c.ell(*T(0, yy), 3.4 * s, 3.4 * s, OUT)
        elif p.get("dasi_kupu"):
            bc = warna(p.get("dasi"), HITAM)
            by = SHOULDER_Y + 12
            boww = 18
            c.poly(TT([(0, by), (-boww, by - 10), (-boww, by + 10)]), bc, ow * .82, OUT)
            c.poly(TT([(0, by), (boww, by - 10), (boww, by + 10)]), bc, ow * .82, OUT)
            c.poly(TT([(-6, by - 7), (6, by - 7), (6, by + 7), (-6, by + 7)]), gelap(bc, .12), ow * .8, OUT)
        if st.get("tali_ransel"):
            for sgn in (-1, 1):
                c.line(TT([(sgn * 26 * bw, SHOULDER_Y), (sgn * 26 * bw, hy - 14)]), warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU, 9.5 * s, False)

        # ---- hijab: drape di bawah dagu
        if p.get("hijab"):
            hj, hjd = warna(p["hijab"]), warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
            if p.get("hijab_gaya") == "modern":
                # selendang hijab modern: melilit leher & jatuh lembut di dada atas agar bahu blazer tetap tampak
                c.blob(TT([(-100, -328), (-110, -268), (-94, -222), (-54, -206), (0, -184),
                           (54, -206), (94, -222), (110, -268), (100, -328), (0, -388)]),
                       hj, ow, OUT, n=7)
                c.curve(TT([(-82, -236), (-38, -214), (0, -200), (38, -214), (82, -236)]), hjd, 4.0 * s)
                c.curve(TT([(-58, -212), (-18, -196), (22, -200)]), hjd, 3.4 * s)
                c.curve(TT([(-94, -264), (-66, -238)]), hjd, 3.2 * s)
                c.curve(TT([(94, -264), (66, -238)]), hjd, 3.2 * s)
            else:
                c.blob(TT([(-112, -336), (-122, -276), (-104, -222), (-52, -190), (0, -178), (52, -190), (104, -222), (122, -276), (112, -336), (0, -380)]),
                       hj, ow, OUT, n=7)
                c.curve(TT([(-70, -230), (-30, -214), (0, -204)]), hjd, 5 * s)
                c.curve(TT([(70, -230), (30, -214), (0, -204)]), hjd, 5 * s)
                c.curve(TT([(-96, -262), (-60, -236)]), hjd, 4 * s)
                c.curve(TT([(96, -262), (60, -236)]), hjd, 4 * s)
            # dasi tampak di bawah drape
            if dasi and not p.get("dasi_kupu"):
                c.poly(TT([(-4, -180), (4, -180), (9, -152), (0, -140), (-9, -152)]), dasi, ow * .7, OUT)
                c.poly(TT([(-6, -190), (6, -190), (4.5, -180), (-4.5, -180)]), dasi, ow * .7, OUT)

        # ---- lengan (bawah di depan badan; yang terangkat/ke wajah digambar setelah kepala agar tidak tertelan kepala/afro)
        arms = st["arms"]
        hands = {}
        front_arms = []
        for side, key in (("L", -1), ("R", 1)):
            a, e, hk = arms[side]
            ar, br = math.radians(a), math.radians(a + e)
            hd_y = SHOULDER_Y + 4 + math.cos(ar) * UP_ARM + math.cos(br) * FORE_ARM
            if hd_y < SHOULDER_Y - 52:
                front_arms.append((side, key, a, e, hk))
            else:
                hands[side] = self._arm(c, T, s, key, a, e, hk, kemeja, ow, dy)

        # ---- kepala
        self._head(c, st, T, s, fl, ow)

        # ---- lengan terangkat / dekat wajah (di depan kepala & rambut)
        for side, key, a, e, hk in front_arms:
            hands[side] = self._arm(c, T, s, key, a, e, hk, kemeja, ow, dy)

        # ---- benda di tangan
        return hands

    # ------------------------------------------------------------ kaki
    def _legs(self, st, T, sit):
        stance = st.get("legs", "stand")
        ph, amp = st.get("phase", 0.0), st.get("amp", 0.0)
        kl = float(self.p.get("kaki_lebar", 1.55))
        hy = float(self.p.get("hip_y", -114.0))
        feet, knees, hips = [], [], []
        for sgn in (-1, 1):
            hx = sgn * 20 * kl
            fx, fy = sgn * 26 * kl, 0.0
            if stance == "walk" and amp > 0.01:
                q = ph + (0 if sgn < 0 else math.pi)
                hx = sgn * 20 * kl * (1 - 0.7 * min(1.0, amp))     # pinggul merapat -> kaki membentuk huruf A
                fx = hx + math.sin(math.sin(q) * 0.5 * amp) * 150
                fy = -max(0.0, -math.cos(q)) * 18 * amp
            elif stance == "wide":
                fx = sgn * 54 * kl
            hipw = T(hx, hy)
            f_stand, f_sit = T(fx, fy, True), T(hx + 96, 0.0, True)
            foot = (lerp(f_stand[0], f_sit[0], sit), lerp(f_stand[1], f_sit[1], sit))
            mid = ((hipw[0] + foot[0]) / 2, (hipw[1] + foot[1]) / 2)
            k_sit = T(hx + 88, hy + SIT_DROP, True)
            knee = (lerp(mid[0], k_sit[0], sit), lerp(mid[1], k_sit[1], sit))
            feet.append(foot)
            knees.append(knee)
            hips.append(hipw)
        return feet, knees, hips

    # ------------------------------------------------------------ lengan
    def _arm(self, c, T, s, sgn, a, e, hk, sleeve, ow, dy):
        ar, br = math.radians(a), math.radians(a + e)
        bahu = float(self.p.get("bahu_x", 68.0))
        sh = (sgn * bahu, SHOULDER_Y + 4)
        el = (sh[0] + sgn * math.sin(ar) * UP_ARM, sh[1] + math.cos(ar) * UP_ARM)
        hd = (el[0] + sgn * math.sin(br) * FORE_ARM, el[1] + math.cos(br) * FORE_ARM)
        S, E, H = T(*sh), T(*el), T(*hd)
        tebal = bool(self.p.get("lengan_tebal", True))
        lb = float(self.p.get("lengan_besar", 1.18)) if tebal else 1.0
        tb = float(self.p.get("tangan_besar", 1.16))
        skin = warna(self.p.get("kulit"), PUTIH)
        arm_ow = 4.2 * s
        # lengan kartun berisi (tube kulit / lengan panjang blazer)
        if self.p.get("lengan_panjang"):
            arm_w = 19 * lb
            if self.p.get("manset") or self.p.get("blazer"):
                dx, dy_ = H[0] - E[0], H[1] - E[1]
                dl = max(1e-5, math.hypot(dx, dy_))
                ux, uy = dx / dl, dy_ / dl
                r_hand = 17.5 * tb * s
                c0 = (H[0] - ux * (r_hand + 13.0 * s), H[1] - uy * (r_hand + 13.0 * s))
                c1 = (H[0] - ux * (r_hand + 1.5 * s), H[1] - uy * (r_hand + 1.5 * s))
                c.tube(c0, c1, (arm_w - 3.5) * s, PUTIH, 3.8 * s, OUT)
                H_slv = (H[0] - ux * (r_hand + 19.5 * s), H[1] - uy * (r_hand + 19.5 * s))
                c.line([S, E, H_slv], OUT, (arm_w + 2 * 4.2) * s)
                c.line([S, E, H_slv], sleeve, arm_w * s)
            else:
                c.line([S, E, H], OUT, (arm_w + 2 * 4.2) * s)
                c.line([S, E, H], sleeve, arm_w * s)
        else:
            if tebal:
                arm_w = 16 * lb
                c.line([S, E, H], OUT, (arm_w + 2 * 4.2) * s)
                c.line([S, E, H], skin, arm_w * s)
            else:
                c.line([S, E, H], OUT, 6.5 * s)
            sl = (sh[0] + (el[0] - sh[0]) * 0.46, sh[1] + (el[1] - sh[1]) * 0.46)
            c.tube(S, T(*sl), (22 * lb if tebal else 19) * s, sleeve, arm_ow)
        # tangan
        dirv = (H[0] - E[0], H[1] - E[1])
        ang = math.atan2(dirv[1], dirv[0])
        r = 17.5 * tb * s
        if hk == "p":
            fe = (H[0] + math.cos(ang) * 30 * s * tb, H[1] + math.sin(ang) * 30 * s * tb)
            c.tube(H, fe, 9 * tb * s, skin, 3.8 * s)
        if hk == "t":
            c.tube((H[0], H[1] - 6 * s), (H[0] + sgn * 2 * s, H[1] - 24 * s * tb), 10 * tb * s, skin, 3.8 * s)
        rr = r * (0.92 if hk == "f" else 1.0)
        c.ell(H[0], H[1], rr, rr, skin, 4.2 * s, OUT)
        return {"pos": H, "ang": ang, "elbow": E}

    # ------------------------------------------------------------ kepala
    def _head(self, c, st, T, s, fl, ow):
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
        cx, cy = 0.0, HEAD_Y
        face_rx, face_ry = (84.0, 90.0) if hij else (HEAD_R, HEAD_R)
        fcy = cy + (14 if hij else 0)

        def H(lx, ly):
            lx, ly = lx, ly
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
                # kubah hijab bundar halus (mirip referensi chibi) mengalir lembut ke bahu
                outer = HH([
                    (-108, -10), (-96, -78), (-56, -118), (0, -130),
                    (56, -118), (96, -78), (108, -10),
                    (112, 46), (82, 86), (0, 96), (-82, 86), (-112, 46),
                ])
                c.blob(outer, hj, ow, OUT, n=7)
                c.curve(HH([(-86, -58), (-52, -100), (0, -112)]), hjd, 3.0 * s)
                c.curve(HH([(86, -58), (52, -100), (0, -112)]), hjd, 3.0 * s)
            else:
                outer = HH(_ellpts(0, -14, 112, 114))
                c.poly(outer, hj, ow, OUT)
        if r in ("kuncir",) and not hij:
            c.ell(*H(-92, -64), 30 * s, 30 * s, hair_c, ow, OUT)
            c.ell(*H(92, -64), 30 * s, 30 * s, hair_c, ow, OUT)
        if r == "keriting" and not hij:
            for i, a in enumerate(range(188, 353, 15)):
                rr = 94 + (6 if i % 2 else 0)
                c.ell(*H(math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr), 30 * s, 30 * s, hair_c, ow * .9, OUT)
        if r == "afro" and not hij:
            # afro besar & mengembang (2-pass: outline luar dulu lalu isi padat agar siluet awan keriting bersih)
            af_cy = -46
            puffs = []
            dr_pat = (0, 7, -2, 8, 2, 7, -1, 8, 5, 8, -1, 7, 2, 8, -2, 7, 0)
            pr_pat = (26, 32, 30, 35, 31, 36, 32, 36, 35, 36, 32, 36, 31, 35, 30, 32, 26)
            for i, a in enumerate(range(142, 399, 16)):
                rad_a = math.radians(a)
                px = math.cos(rad_a) * (124 + dr_pat[i])
                py = af_cy + math.sin(rad_a) * (108 + dr_pat[i])
                puffs.append((px, py, pr_pat[i]))
            c.ell(*H(0, af_cy), 120 * s + ow, 102 * s + ow, OUT)
            for px, py, pr in puffs:
                c.ell(*H(px, py), pr * s + ow, pr * s + ow, OUT)
            c.ell(*H(0, af_cy), 120 * s, 102 * s, hair_c)
            for px, py, pr in puffs:
                c.ell(*H(px, py), pr * s, pr * s, hair_c)
        # wajah
        kepala = p.get("kepala")
        if kepala == "otak":
            # kepala otak pink chibi berlekuk-lekuk (2-pass: outline luar dulu lalu isi pink + lekukan sulkus)
            bc = warna(p.get("kulit"), (250, 174, 198))
            lip = gelap(bc, 0.25)
            lobes = [
                (-84, 34, 42), (-96, -12, 46), (-82, -56, 46), (-42, -82, 46),
                (42, -82, 46), (82, -56, 46), (96, -12, 46), (84, 34, 42),
                (-46, 62, 42), (0, 68, 44), (46, 62, 42),
            ]
            c.ell(*H(0, -6), 104 * s + ow, 88 * s + ow, OUT)
            for lx, ly, lr in lobes:
                c.ell(*H(lx, ly), lr * s + ow, lr * s + ow, OUT)
            c.ell(*H(0, -6), 104 * s, 88 * s, bc)
            for lx, ly, lr in lobes:
                c.ell(*H(lx, ly), lr * s, lr * s, bc)
            # belahan tengah dahi atas & garis lekukan otak (tidak menutupi mata/mulut)
            c.curve(HH([(0, -112), (-3, -84), (2, -56)]), lip, 4.8 * s)
            c.curve(HH([(-90, -48), (-66, -66), (-42, -52)]), lip, 4.2 * s)
            c.curve(HH([(90, -48), (66, -66), (42, -52)]), lip, 4.2 * s)
            c.curve(HH([(-108, -12), (-86, -24), (-74, -4)]), lip, 3.8 * s)
            c.curve(HH([(108, -12), (86, -24), (74, -4)]), lip, 3.8 * s)
            c.curve(HH([(-98, 28), (-78, 16), (-68, 36)]), lip, 3.6 * s)
            c.curve(HH([(98, 28), (78, 16), (68, 36)]), lip, 3.6 * s)
            c.ell(*H(-46, -86), 14 * s, 7 * s, (255, 255, 255, 130))
        elif kepala == "virus":
            # kepala virus hijau berduri mahkota (2-pass)
            vc = warna(p.get("kulit"), (112, 204, 88))
            spikes = []
            for i in range(10):
                a = math.radians(i * 36 + 18)
                ca, sa = math.cos(a), math.sin(a)
                spikes.append(((ca * 92, sa * 92), (ca * 128, sa * 128)))
            for p0, p1 in spikes:
                c.line(HH([p0, p1]), OUT, 22 * s)
                c.ell(*H(*p1), 17 * s + ow, 17 * s + ow, OUT)
            c.ell(*H(0, 0), 96 * s + ow, 96 * s + ow, OUT)
            for p0, p1 in spikes:
                c.line(HH([p0, p1]), vc, 12 * s)
                c.ell(*H(*p1), 15.5 * s, 15.5 * s, terang(vc, 0.22))
            c.ell(*H(0, 0), 96 * s, 96 * s, vc)
            for bx, by, br in ((-56, -46, 12), (58, -38, 10), (-60, 44, 10), (54, 48, 12)):
                c.ell(*H(bx, by), br * s, br * s, gelap(vc, 0.20))
        elif kepala == "sel_imun":
            # kepala sel darah putih berpendar biru muda (2-pass awan lembut)
            ic = warna(p.get("kulit"), (236, 248, 255))
            c.ell(*H(0, 0), 124 * s, 124 * s, (120, 204, 252, 70))
            bumps = [(math.cos(math.radians(i * 45)) * 74, math.sin(math.radians(i * 45)) * 74, 46) for i in range(8)]
            c.ell(*H(0, 0), 92 * s + ow, 92 * s + ow, OUT)
            for bx, by, br in bumps:
                c.ell(*H(bx, by), br * s + ow, br * s + ow, OUT)
            c.ell(*H(0, 0), 92 * s, 92 * s, ic)
            for bx, by, br in bumps:
                c.ell(*H(bx, by), br * s, br * s, ic)
            c.ell(*H(-42, -56), 16 * s, 10 * s, (255, 255, 255, 190))
        elif hij and p.get("hijab_gaya") == "modern":
            face_pts = [
                (0, -76), (38, -60), (68, -32), (82, 4),
                (78, 42), (54, 72), (24, 84), (0, 86),
                (-24, 84), (-54, 72), (-78, 42), (-82, 4),
                (-68, -32), (-38, -60),
            ]
            c.blob(HH(face_pts), warna(p.get("kulit"), PUTIH), ow, OUT, n=5)
            hjd2 = warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
            c.curve(HH([(-74, -14), (-44, -56), (0, -76), (44, -56), (74, -14)]), hjd2, 3.0 * s)
        else:
            if p.get("telinga") and not hij and kepala not in ("otak", "virus", "sel_imun"):
                skin_c = warna(p.get("kulit"), PUTIH)
                for sg in (-1, 1):
                    c.ell(*H(sg * face_rx, 6), 15 * s, 19 * s, skin_c, ow, OUT)
            face = HH(_ellpts(0, 0, face_rx, face_ry, 34))
            c.poly(face, warna(p.get("kulit"), PUTIH), ow, OUT)
            # rambut depan
            if not hij:
                self._hair_front(c, H, HH, s, ow, r, hair_c, p)
            else:
                hjd2 = warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
                c.curve(HH(arc_pts(0, 2, face_rx + 1, face_ry + 1, 200, 340, 12)), hjd2, 4.2 * s)
        # topi/peci
        if p.get("peci"):
            c.poly(HH([(-70, -78), (-62, -118), (0, -128), (62, -118), (70, -78), (0, -62)]), HITAM, ow, OUT)
        if p.get("topi"):
            tc = warna(p["topi"] if not isinstance(p["topi"], bool) else "merah", MERAH)
            c.blob(HH([(-86, -52), (-78, -112), (0, -134), (78, -112), (86, -52), (0, -46)]), tc, ow, OUT)
            c.poly(HH([(40, -56), (130, -48), (130, -36), (40, -42)]), gelap(tc, .15), ow * .8, OUT)

        # fitur wajah
        lx_, ly_ = look
        fs = 0.92 if hij else 1.0
        chibi_eye = bool(p.get("mata_chibi"))
        fx0, fy0 = lx_ * 15, ly_ * 8
        eyes = ex["eyes"]
        blink = st.get("blink", 0.0)
        ec = (-35 * fs, 35 * fs) if chibi_eye else (-34 * fs, 34 * fs)
        eye_y = (10 if chibi_eye else -4) * fs + fy0
        ew = 11.5 * (0.88 if mask else 1.0)
        eh = 17.5 * (1.12 if fem else (0.82 if mask else 1.0))
        hlk = ex.get("hl", 1.0) * (0.72 if mask else 1.0)
        # lensa kacamata digambar SEBELUM mata agar tidak menutupi mata/kilau
        hw, hh_g, rad_g = 29 * fs, 21 * fs, 7 * fs
        r_bulat = 29 * fs
        if p.get("kacamata") == "kotak":
            for ex_ in ec:
                gx, gy = ex_ + fx0, eye_y + 2
                frame = _rectpts(gx - hw, gy - hh_g, gx + hw, gy + hh_g, rad_g, 5)
                c.poly(HH(frame), (255, 255, 255, 235))
        elif p.get("kacamata") == "bulat":
            for ex_ in ec:
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, r_bulat, r_bulat, 26)), (255, 255, 255, 52))

        for i, ex_ in enumerate(ec):
            ex_ = ex_ + fx0
            if eyes in ("oval", "wide", "spark", "dot", "half", "wink") and not (eyes == "wink" and i == 1):
                if mask and eyes in ("oval", "wide", "spark", "dot"):
                    # mata titik hitam simpel tanpa kilau (gaya chibi maskulin)
                    sc = 1.15 if eyes == "wide" else 1.0
                    hh = 8.5 * sc * (1 - 0.9 * blink)
                    c.poly(HH(_ellpts(ex_, eye_y + 2, 6.5 * sc, max(1.5, hh), 14)), OUT)
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
            for ex_ in ec:
                gx, gy = ex_ + fx0, eye_y + 2
                frame = _rectpts(gx - hw, gy - hh_g, gx + hw, gy + hh_g, rad_g, 5)
                c.poly(HH(frame), None, 5.2 * s, OUT)
            c.line(HH([(ec[0] + fx0 + hw, eye_y - 2), (ec[1] + fx0 - hw, eye_y - 2)]), OUT, 5.2 * s)
            for sg in (-1, 1):
                gx = ec[0 if sg < 0 else 1] + fx0 + sg * hw
                c.line(HH([(gx, eye_y - 4), (gx + sg * 12 * fs, eye_y - 8)]), OUT, 4.2 * s)
        elif p.get("kacamata") == "bulat":
            for ex_ in ec:
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, r_bulat, r_bulat, 26)), None, 4.4 * s, OUT)
            c.curve(HH([(ec[0] + fx0 + r_bulat, eye_y + 1), (fx0, eye_y - 3),
                        (ec[1] + fx0 - r_bulat, eye_y + 1)]), OUT, 4.2 * s, n=6)
            for sg in (-1, 1):
                gx = ec[0 if sg < 0 else 1] + fx0 + sg * r_bulat
                tx = sg * (face_rx - 1) if p.get("telinga") else (gx + sg * 11 * fs)
                ty = 2 if p.get("telinga") else (eye_y - 5)
                c.line(HH([(gx, eye_y - 1), (tx, ty)]), OUT, 4.0 * s)
        elif p.get("kacamata"):
            for ex_ in ec:
                c.poly(HH(_ellpts(ex_ + fx0, eye_y, 30, 30, 22)), (255, 255, 255, 70), ow * .95, OUT)
            c.line(HH([(ec[0] + 30 + fx0, eye_y - 4), (ec[1] - 30 + fx0, eye_y - 4)]), OUT, 4.6 * s)

        # alis
        br = ex.get("brow")
        if br:
            lift, tl, tr = br
            for i, (bx, tv) in enumerate(((ec[0], tl), (ec[1], tr))):
                sg = -1 if i == 0 else 1
                by = eye_y - 30 * fs - lift - (6 if p.get("kacamata") in ("kotak", "bulat") else 0)
                outer = (bx + fx0 + sg * 17, by + tv * 11)
                inner = (bx + fx0 - sg * 17, by - tv * 11)
                mid = (bx + fx0, by - 4 + (4 if abs(tv) > .5 else 0) + (-6 if lift > 6 else 0))
                c.curve(HH([outer, mid, inner]), OUT, (6.0 if mask else (4.4 if chibi_eye else 5.6)) * s)
        elif mask:
            # alis tipis & pendek tepat di atas kacamata
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 34
                c.line(HH([(bx + fx0 + sg * 14, by), (bx + fx0 - sg * 14, by + 2)]), OUT, 5.2 * s)
        elif chibi_eye or p.get("mata_sclera"):
            # alis melengkung lembut di atas kacamata bulat
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 34 * fs
                c.curve(HH([(bx + fx0 + sg * 14, by + 3), (bx + fx0, by - 2),
                            (bx + fx0 - sg * 13, by + 2)]), OUT, 3.8 * s)

        # pipi (hilangkan blush pink lebar pada mode maskulin kecuali saat sangat malu)
        bl = ex.get("blush", 0.0)
        if mask:
            bl = 0.45 if bl >= 0.95 else 0.0
        elif chibi_eye and bl > 0.02:
            bl = max(bl, 0.55)
        if bl > 0.02:
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
        if r == "afro":
            # poni & jambang keriting menyatu mulus ke massa afro belakang (2-pass)
            bangs = [
                (-100, -10, 21), (-90, -38, 23), (-72, -64, 24),
                (-42, -82, 24), (0, -88, 25), (42, -82, 24),
                (72, -64, 24), (90, -38, 23), (100, -10, 21),
            ]
            for bx, by, br in bangs:
                c.ell(*H(bx, by), br * s + ow * .75, br * s + ow * .75, OUT)
            cap_top = arc_pts(0, -18, 108, 108, 174, 366, 18)
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
        mx, my = fx0 * .6, (50 if self.p.get("mata_chibi") else 44) * fs + fy0 * .4
        k = ex.get("small", 1.0) * (0.76 if self.p.get("mata_chibi") and talk is None and kind == "open" else 1.0)

        def D(w, d):
            top = [(mx - w, my - 1), (mx - w * .5, my - 4), (mx + w * .5, my - 4), (mx + w, my - 1)]
            bot = arc_pts(mx, my - 1, w, d, 0, 180, 14)
            c.poly(HH(top + bot), MERAH_TUA, ow * .85, OUT)
            if d > 14:
                c.poly(HH(_ellpts(mx, my + d * .62, w * .5, d * .32, 14)), LIDAH)
            return
        if kind == "open":
            D(23 * k, lerp(5, 30, op))
        elif kind == "grin":
            D(31, lerp(14, 38, op))
        elif kind == "smile":
            c.curve(HH(arc_pts(mx, my - 14, 25, 22, 28, 152, 10)), OUT, 4.8 * s)
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
