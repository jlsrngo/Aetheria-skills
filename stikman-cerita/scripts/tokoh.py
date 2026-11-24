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
                   badan_lebar=1.55, pinggul_lebar=1.45, bahu_x=58.0, lengan_besar=1.05,
                   hip_y=-135.0, kaki_tebal=1.85, kaki_lebar=1.45, sepatu_besar=1.25, tangan_besar=1.05,
                   bawah="celana", bawah_warna=(46, 46, 52)),
    "raka":   dict(nama="Raka", rambut="jambul", rambut_warna=HITAM, kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=HITAM),
    "nadia":  dict(nama="Nadia", hijab=PINK, hijab_tua=PINK_TUA, kemeja=PUTIH, dasi=MERAH, bawah="rok", bawah_warna=HITAM, bulu_mata=True),
    "bimo":   dict(nama="Bimo", rambut="keriting", rambut_warna=(62, 40, 34), kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=HITAM),
    "dimas":  dict(nama="Dimas", rambut="rapi", rambut_warna=HITAM, kacamata=True, kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=HITAM),
    "sari":   dict(nama="Sari", hijab=(250, 250, 252), hijab_tua=ABU, kemeja=PUTIH, dasi=MERAH, bawah="rok", bawah_warna=HITAM, bulu_mata=True),
    "tika":   dict(nama="Tika", rambut="kuncir", rambut_warna=HITAM, kemeja=PUTIH, dasi=MERAH, bawah="rok", bawah_warna=HITAM, bulu_mata=True),
    "ayah":   dict(nama="Ayah", rambut="rapi", rambut_warna=(70, 70, 80), kumis=True, kemeja=(200, 224, 250), dasi=None, bawah="celana", bawah_warna=NAVY, skala=1.08),
    "ibu":    dict(nama="Ibu", hijab=HIJAU, hijab_tua=HIJAU_TUA, kemeja=(250, 236, 214), dasi=None, bawah="rok", bawah_warna=COKLAT_TUA, bulu_mata=True, skala=1.04),
    "guru":   dict(nama="Pak Guru", rambut="uban", rambut_warna=(205, 205, 212), kacamata=True, kumis=True, kemeja=(236, 232, 214), dasi=MERAH_TUA, bawah="celana", bawah_warna=NAVY, skala=1.06),
    "bu_guru": dict(nama="Bu Guru", hijab=UNGU, hijab_tua=UNGU_TUA, kacamata=True, kemeja=(240, 232, 250), dasi=None, bawah="rok", bawah_warna=UNGU_TUA, bulu_mata=True, skala=1.04),
    "kakek":  dict(nama="Kakek", rambut="botak", peci=True, kumis=True, jenggot=True, kemeja=(250, 250, 250), dasi=None, bawah="celana", bawah_warna=(90, 70, 60), skala=0.98, uban=True),
    "adik":   dict(nama="Adik", rambut="bob", rambut_warna=HITAM, kemeja=(255, 226, 120), dasi=None, bawah="rok", bawah_warna=PINK_TUA, bulu_mata=True, skala=0.8),
}


def casting(spec):
    """spec = nama preset (str) atau dict {'dasar': 'kribo', ...override}. Default = kribo."""
    if isinstance(spec, str):
        spec = {"dasar": spec}
    base = dict(PRESET.get(spec.get("dasar", "kribo"), PRESET["kribo"]))
    base.update({k: (tuple(v) if isinstance(v, list) and len(v) == 3 and all(isinstance(i, int) for i in v) else v)
                 for k, v in spec.items() if k != "dasar"})
    base.setdefault("skala", 1.0)
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

        ow = 4.2 * s           # tebal garis tepi (satuan dunia)
        kemeja = warna(p.get("kemeja"), PUTIH)
        kulit = warna(p.get("kulit"), PUTIH)
        dasi = warna(p.get("dasi"))
        bawah_c = warna(p.get("bawah_warna"), HITAM)
        sepatu = warna(p.get("sepatu"), HITAM)
        # proporsi badan: preset chibi kekar (kribo) memakai torso/hip/kaki lebih lebar
        bw = float(p.get("badan_lebar", 1.0))
        hipb = float(p.get("pinggul_lebar", bw))
        hy = float(p.get("hip_y", HIP_Y))
        kt = float(p.get("kaki_tebal", 1.0))
        sm = float(p.get("sepatu_besar", 1.0))

        # ransel (bagian belakang)
        if st.get("ransel"):
            rc = warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU
            c.blob(TT([(-70, -258), (-84, -230), (-80, -176), (-52, -150), (52, -150), (80, -176), (84, -230), (70, -258), (0, -270)]),
                   rc, ow, OUT)
            c.ell(*T(-74, -214), 14 * s, 26 * s, gelap(rc, 0.18), ow * .8)
            c.ell(*T(74, -214), 14 * s, 26 * s, gelap(rc, 0.18), ow * .8)

        # ---- kaki
        hipy = hy + dy
        hip = [T(-20, hy), T(20, hy)]
        feet, knees, hip = self._legs(st, T, sit)
        skirt = p.get("bawah") == "rok"
        legw = (9.5 if skirt else 15) * kt
        legc = HITAM if skirt else bawah_c
        legoc = OUT
        for i in (0, 1):
            ax, ay = hip[i]
            kx, ky = knees[i]
            fx, fy = feet[i]
            if skirt:
                c.line([(ax, ay), (kx, ky), (fx, fy)], HITAM if bawah_c == HITAM else gelap(bawah_c, .55), legw * s, True)
            else:
                c.line([(ax, ay), (kx, ky), (fx, fy)], legoc, (legw + 2 * 4.0) * s)
                c.line([(ax, ay), (kx, ky), (fx, fy)], legc, legw * s)
            if p.get("sepatu_sneaker"):
                toe = -1 if i == 0 else 1          # ujung sepatu menghadap keluar -> simetris
                shoe_x, shoe_y = fx + toe * fl * 7 * s * sm, fy - 4 * s * sm
                c.ell(shoe_x, shoe_y, 27 * s * sm, 13 * s * sm, sepatu, ow * .6, OUT)
                c.ell(fx + toe * fl * 16 * s * sm, shoe_y, 10.5 * s * sm, 9.5 * s * sm, PUTIH, ow * .45, OUT)
                c.line([(fx - toe * fl * 21 * s * sm, fy + 6 * s * sm),
                        (fx + toe * fl * 22 * s * sm, fy + 6 * s * sm)], PUTIH, 3.8 * s * sm)
            else:
                c.ell(fx + fl * 7 * s, fy - 4 * s, 27 * s, 13 * s, sepatu, ow * .6, OUT)
        if skirt:
            hem = hy + 74 + dy * 0.9
            c.poly(TT([(-36, hy - 12), (36, hy - 12), (60, hem - 4)] + bezier((60, hem - 4), (0, hem + 22), (-60, hem - 4), 10)[1:-1] + [(-60, hem - 4)]),
                   bawah_c, ow, OUT)
        if not skirt and bw > 1.2:
            c.poly(TT([(-34 * hipb, hy - 14), (34 * hipb, hy - 14),
                       (34 * hipb, hy + 22), (-34 * hipb, hy + 22)]), bawah_c, ow, OUT)
        # ---- torso
        c.blob(TT([(-43 * bw, SHOULDER_Y + 6), (-30 * bw, SHOULDER_Y - 3), (30 * bw, SHOULDER_Y - 3),
                   (43 * bw, SHOULDER_Y + 6), (38 * hipb, hy - 44), (35 * hipb, hy - 12),
                   (0, hy - 7), (-35 * hipb, hy - 12), (-38 * hipb, hy - 44)]),
               kemeja, ow, OUT, n=5)
        if p.get("kemeja_garis"):
            gc = warna(p["kemeja_garis"], BIRU)
            for yy in (-215, -192, -170):
                c.line(TT([(-38, yy), (38, yy)]), gc, 6 * s, False)
        # krah + dasi (dasi kupu-kupu menggantikan krah/dasi biasa)
        if p.get("krah", True) and not p.get("dasi_kupu"):
            c.poly(TT([(0, SHOULDER_Y + 24), (-22, SHOULDER_Y - 2), (-4, SHOULDER_Y - 2)]), PUTIH, ow * .7, OUT)
            c.poly(TT([(0, SHOULDER_Y + 24), (22, SHOULDER_Y - 2), (4, SHOULDER_Y - 2)]), PUTIH, ow * .7, OUT)
        if p.get("dasi_kupu"):
            bc = warna(p.get("dasi"), HITAM)
            by = SHOULDER_Y + 12
            boww = 18
            c.poly(TT([(0, by), (-boww, by - 10), (-boww, by + 10)]), bc, ow * .75, OUT)
            c.poly(TT([(0, by), (boww, by - 10), (boww, by + 10)]), bc, ow * .75, OUT)
            c.poly(TT([(-6, by - 7), (6, by - 7), (6, by + 7), (-6, by + 7)]), gelap(bc, .12), ow * .7, OUT)
        elif dasi:
            c.poly(TT([(-8, SHOULDER_Y + 10), (8, SHOULDER_Y + 10), (6, SHOULDER_Y + 22), (-6, SHOULDER_Y + 22)]), dasi, ow * .7, OUT)
            c.poly(TT([(-6, SHOULDER_Y + 22), (6, SHOULDER_Y + 22), (11, SHOULDER_Y + 52), (0, SHOULDER_Y + 66), (-11, SHOULDER_Y + 52)]), dasi, ow * .7, OUT)
        elif p.get("kancing", True):
            for yy in (-222, -200, -178):
                c.ell(*T(0, yy), 3.2 * s, 3.2 * s, OUT)
        if st.get("tali_ransel"):
            for sgn in (-1, 1):
                c.line(TT([(sgn * 30, SHOULDER_Y), (sgn * 30, hy - 14)]), warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU, 9 * s, False)

        # ---- hijab: drape di bawah dagu
        if p.get("hijab"):
            hj, hjd = warna(p["hijab"]), warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
            c.blob(TT([(-112, -336), (-122, -276), (-104, -222), (-52, -190), (0, -178), (52, -190), (104, -222), (122, -276), (112, -336), (0, -380)]),
                   hj, ow, OUT, n=7)
            c.curve(TT([(-70, -230), (-30, -214), (0, -204)]), hjd, 5 * s)
            c.curve(TT([(70, -230), (30, -214), (0, -204)]), hjd, 5 * s)
            c.curve(TT([(-96, -262), (-60, -236)]), hjd, 4 * s)
            c.curve(TT([(96, -262), (60, -236)]), hjd, 4 * s)
            # dasi tampak di bawah drape
            if dasi and not p.get("dasi_kupu"):
                c.poly(TT([(-7, -190), (7, -190), (5, -178), (-5, -178)]), dasi, ow * .7, OUT)
                c.poly(TT([(-5, -178), (5, -178), (10, -150), (0, -138), (-10, -150)]), dasi, ow * .7, OUT)

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
        kl = float(self.p.get("kaki_lebar", 1.0))
        hy = float(self.p.get("hip_y", HIP_Y))
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
        bahu = float(self.p.get("bahu_x", SHOULDER_X))
        sh = (sgn * bahu, SHOULDER_Y + 4)
        el = (sh[0] + sgn * math.sin(ar) * UP_ARM, sh[1] + math.cos(ar) * UP_ARM)
        hd = (el[0] + sgn * math.sin(br) * FORE_ARM, el[1] + math.cos(br) * FORE_ARM)
        S, E, H = T(*sh), T(*el), T(*hd)
        tebal = bool(self.p.get("lengan_tebal"))
        lb = float(self.p.get("lengan_besar", 1.0)) if tebal else 1.0
        tb = float(self.p.get("tangan_besar", 1.0))
        skin = warna(self.p.get("kulit"), PUTIH)
        # lengan kartun berisi (tube kulit) atau lengan garis tipis seperti preset lama
        if tebal:
            arm_w = 16 * lb
            c.line([S, E, H], OUT, (arm_w + 2 * 3.4) * s)
            c.line([S, E, H], skin, arm_w * s)
        else:
            c.line([S, E, H], OUT, 6.5 * s)
        sl = (sh[0] + (el[0] - sh[0]) * 0.46, sh[1] + (el[1] - sh[1]) * 0.46)
        c.tube(S, T(*sl), (24 * lb if tebal else 19) * s, sleeve, 3.4 * s)
        # tangan
        dirv = (H[0] - E[0], H[1] - E[1])
        ang = math.atan2(dirv[1], dirv[0])
        r = 17.5 * tb * s
        if hk == "p":
            fe = (H[0] + math.cos(ang) * 30 * s * tb, H[1] + math.sin(ang) * 30 * s * tb)
            c.tube(H, fe, 9 * tb * s, skin, 3.2 * s)
        if hk == "t":
            c.tube((H[0], H[1] - 6 * s), (H[0] + sgn * 2 * s, H[1] - 24 * s * tb), 10 * tb * s, skin, 3.2 * s)
        rr = r * (0.92 if hk == "f" else 1.0)
        c.ell(H[0], H[1], rr, rr, skin, 3.6 * s, OUT)
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
        fx0, fy0 = lx_ * 15, ly_ * 8
        eyes = ex["eyes"]
        blink = st.get("blink", 0.0)
        ec = (-34 * fs, 34 * fs)
        eye_y = -4 * fs + fy0
        ew = 11.5 * (0.88 if mask else 1.0)
        eh = 17.5 * (1.12 if fem else (0.82 if mask else 1.0))
        hlk = ex.get("hl", 1.0) * (0.72 if mask else 1.0)
        # lensa kacamata kotak digambar SEBELUM mata agar putih pekat tidak menutupi mata
        hw, hh_g, rad_g = 29 * fs, 21 * fs, 7 * fs
        if p.get("kacamata") == "kotak":
            for ex_ in ec:
                gx, gy = ex_ + fx0, eye_y + 2
                frame = _rectpts(gx - hw, gy - hh_g, gx + hw, gy + hh_g, rad_g, 5)
                c.poly(HH(frame), (255, 255, 255, 235))

        for i, ex_ in enumerate(ec):
            ex_ = ex_ + fx0
            if eyes in ("oval", "wide", "spark", "dot", "half", "wink") and not (eyes == "wink" and i == 1):
                if mask and eyes in ("oval", "wide", "spark", "dot"):
                    # mata titik hitam simpel tanpa kilau (gaya chibi maskulin)
                    sc = 1.15 if eyes == "wide" else 1.0
                    hh = 8.5 * sc * (1 - 0.9 * blink)
                    c.poly(HH(_ellpts(ex_, eye_y + 2, 6.5 * sc, max(1.5, hh), 14)), OUT)
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

        # bingkai kacamata kotak (di atas mata)
        if p.get("kacamata") == "kotak":
            for ex_ in ec:
                gx, gy = ex_ + fx0, eye_y + 2
                frame = _rectpts(gx - hw, gy - hh_g, gx + hw, gy + hh_g, rad_g, 5)
                c.poly(HH(frame), None, 5.2 * s, OUT)
            c.line(HH([(ec[0] + fx0 + hw, eye_y - 2), (ec[1] + fx0 - hw, eye_y - 2)]), OUT, 5.2 * s)
            for sg in (-1, 1):
                gx = ec[0 if sg < 0 else 1] + fx0 + sg * hw
                c.line(HH([(gx, eye_y - 4), (gx + sg * 12 * fs, eye_y - 8)]), OUT, 4.2 * s)
        elif p.get("kacamata"):
            for ex_ in ec:
                c.poly(HH(_ellpts(ex_ + fx0, eye_y, 30, 30, 22)), (255, 255, 255, 70), ow * .9, OUT)
            c.line(HH([(ec[0] + 30 + fx0, eye_y - 4), (ec[1] - 30 + fx0, eye_y - 4)]), OUT, 4 * s)

        # alis
        br = ex.get("brow")
        if br:
            lift, tl, tr = br
            for i, (bx, tv) in enumerate(((ec[0], tl), (ec[1], tr))):
                sg = -1 if i == 0 else 1
                by = eye_y - 30 * fs - lift - (6 if p.get("kacamata") == "kotak" else 0)
                outer = (bx + fx0 + sg * 17, by + tv * 11)
                inner = (bx + fx0 - sg * 17, by - tv * 11)
                mid = (bx + fx0, by - 4 + (4 if abs(tv) > .5 else 0) + (-6 if lift > 6 else 0))
                c.curve(HH([outer, mid, inner]), OUT, (6.0 if mask else 5.6) * s)
        elif mask:
            # alis tipis & pendek tepat di atas kacamata
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 34
                c.line(HH([(bx + fx0 + sg * 14, by), (bx + fx0 - sg * 14, by + 2)]), OUT, 5.2 * s)

        # pipi (hilangkan blush pink lebar pada mode maskulin kecuali saat sangat malu)
        bl = ex.get("blush", 0.0)
        if mask:
            bl = 0.45 if bl >= 0.95 else 0.0
        if bl > 0.02:
            for sg in (-1, 1):
                c.poly(HH(_ellpts(sg * 58 * fs + fx0 * .6, 28 * fs + fy0 * .4, 17, 10.5, 16)), (255, 140, 160, int(150 * bl)))
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
            c.poly(HH(outer + inner), hc, ow * .8, OUT)
        elif r == "keriting":
            for i, a in enumerate(range(200, 345, 18)):
                rr = HEAD_R * 0.8
                c.ell(*H(math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr + 4), 26 * s, 26 * s, hc, ow * .8, OUT)
        elif r in ("rapi", "uban"):
            top = arc_pts(0, 0, HEAD_R + 5, HEAD_R + 5, 188, 352, 20)
            fringe = [(70, -50), (40, -62), (10, -48), (-18, -60), (-48, -46), (-72, -52)]
            c.poly(HH(top + fringe), hc, ow * .8, OUT)
        elif r == "bob":
            top = arc_pts(0, 0, HEAD_R + 6, HEAD_R + 6, 176, 364, 22)
            fr = [(88, 4), (80, -48), (40, -58), (0, -48), (-40, -58), (-80, -48), (-88, 4)]
            c.poly(HH(top + fr), hc, ow * .8, OUT)
        elif r == "kuncir":
            top = arc_pts(0, 0, HEAD_R + 4, HEAD_R + 4, 190, 350, 18)
            fr = [(74, -46), (44, -64), (14, -50), (-14, -66), (-48, -50), (-76, -50)]
            c.poly(HH(top + fr), hc, ow * .8, OUT)
            c.ell(*H(0, -HEAD_R - 22), 24 * s, 24 * s, hc, ow * .8, OUT)

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
        mx, my = fx0 * .6, 44 * fs + fy0 * .4
        k = ex.get("small", 1.0)

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
