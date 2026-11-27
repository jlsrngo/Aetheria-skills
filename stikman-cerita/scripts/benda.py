# -*- coding: utf-8 -*-
"""
benda.py - benda genggam, properti bebas, dan ikon komik (tanda seru, zzz, bohlam, hati, ...).

gambar(c, jenis, x, y, s=1, rot=0, t=0, **opsi)
  (x, y) = titik pegang / pusat benda di koordinat dunia, rot = derajat searah jarum jam.
"""
import math, os, sys
from stik import *

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from aset_global import draw_engineering_2d  # noqa: E402

OW = 4.0


def _T(x, y, s, rot):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)

    def f(lx, ly):
        return (x + s * (lx * ca - ly * sa), y + s * (lx * sa + ly * ca))
    return f


def _P(f, pts):
    return [f(*p) for p in pts]


# ----------------------------------------------------------------- benda genggam
def hp(c, f, s, t, layar=(120, 182, 255), warna=(34, 34, 44), **k):
    c.rect(*f(-21, -38), *f(21, 38), warna, OW * s, OUT, r=9 * s) if False else None
    pts = _P(f, [(-21, -38), (21, -38), (21, 38), (-21, 38)])
    c.blob(_P(f, [(-21, -38), (0, -40), (21, -38), (23, 0), (21, 38), (0, 40), (-21, 38), (-23, 0)]), warna, OW * s, OUT, n=5)
    c.poly(_P(f, [(-16, -31), (16, -31), (16, 31), (-16, 31)]), layar)
    if k.get("play"):
        c.poly(_P(f, [(-6, -9), (9, 0), (-6, 9)]), PUTIH)
    c.ell(*f(0, -34), 2.2 * s, 2.2 * s, OUT)


def buku(c, f, s, t, warna=BIRU, buka=False, **k):
    if buka:
        c.poly(_P(f, [(-62, -34), (0, -28), (0, 40), (-62, 46)]), PUTIH, OW * s, OUT)
        c.poly(_P(f, [(62, -34), (0, -28), (0, 40), (62, 46)]), (250, 250, 244), OW * s, OUT)
        for i in range(4):
            c.line(_P(f, [(-52, -14 + i * 14), (-10, -8 + i * 14)]), ABU, 2.6 * s, False)
            c.line(_P(f, [(52, -14 + i * 14), (10, -8 + i * 14)]), ABU, 2.6 * s, False)
    else:
        c.poly(_P(f, [(-34, -46), (34, -46), (34, 46), (-34, 46)]), warna, OW * s, OUT)
        c.poly(_P(f, [(30, -42), (36, -42), (36, 42), (30, 42)]), PUTIH, 2.6 * s, OUT)
        c.rect(*f(-20, -28), *f(14, -6), PUTIH, 2.4 * s, OUT, r=3 * s) if False else c.poly(_P(f, [(-22, -28), (14, -28), (14, -8), (-22, -8)]), terang(warna, .75), 2.4 * s, OUT)


def pensil(c, f, s, t, **k):
    c.poly(_P(f, [(-6, -46), (6, -46), (6, 28), (0, 42), (-6, 28)]), KUNING, OW * .8 * s, OUT)
    c.poly(_P(f, [(-6, 28), (6, 28), (0, 42)]), KAYU, 2.4 * s, OUT)
    c.poly(_P(f, [(-6, -46), (6, -46), (6, -58), (-6, -58)]), PINK, OW * .8 * s, OUT)
    c.line(_P(f, [(-6, -38), (6, -38)]), ABU, 3 * s, False)


def stik(c, f, s, t, warna=(52, 56, 74), **k):
    c.blob(_P(f, [(-48, -4), (-40, -22), (-16, -24), (16, -24), (40, -22), (48, -4), (50, 18), (36, 24), (26, 12), (-26, 12), (-36, 24), (-50, 18)]), warna, OW * s, OUT, n=5)
    c.line(_P(f, [(-34, -10), (-18, -10)]), PUTIH, 4 * s, False)
    c.line(_P(f, [(-26, -18), (-26, -2)]), PUTIH, 4 * s, False)
    for (bx, by, col) in ((30, -14, MERAH), (40, -6, HIJAU), (30, 2, BIRU), (20, -6, KUNING)):
        c.ell(*f(bx, by), 3.8 * s, 3.8 * s, col)


def bola(c, f, s, t, **k):
    c.ell(*f(0, 0), 38 * s, 38 * s, PUTIH, OW * s, OUT)
    c.poly(_P(f, [(0, -14), (13, -4), (8, 12), (-8, 12), (-13, -4)]), OUT)
    for a in range(0, 360, 72):
        ca, sa = math.cos(math.radians(a - 90)), math.sin(math.radians(a - 90))
        c.line(_P(f, [(ca * 14, sa * 14), (ca * 28, sa * 28)]), OUT, 3 * s, False)


def kertas(c, f, s, t, **k):
    c.poly(_P(f, [(-36, -46), (36, -46), (36, 46), (-36, 46)]), PUTIH, OW * s, OUT)
    for i in range(6):
        c.line(_P(f, [(-26, -32 + i * 13), (26 if i % 3 else 10, -32 + i * 13)]), ABU, 3 * s, False)


def gelas(c, f, s, t, isi=BIRU_MUDA, **k):
    c.poly(_P(f, [(-22, -34), (22, -34), (17, 34), (-17, 34)]), (240, 248, 255), OW * s, OUT)
    c.poly(_P(f, [(-20, -8), (20, -8), (17, 32), (-17, 32)]), isi)
    c.poly(_P(f, [(-22, -34), (22, -34), (17, 34), (-17, 34)]), None, OW * s, OUT)


def payung(c, f, s, t, warna=MERAH, **k):
    c.line(_P(f, [(0, -10), (0, 96)]), OUT, 6 * s)
    c.curve(_P(f, [(0, 96), (10, 108), (22, 98)]), OUT, 6 * s)
    arc = [(-96 * math.cos(math.radians(a)), -96 * math.sin(math.radians(a)) * .75) for a in range(0, 181, 15)]
    c.poly(_P(f, [(x, y - 14) for x, y in arc] + [(-96, -14), (96, -14)][:0]), warna, OW * s, OUT)


def kado(c, f, s, t, warna=PINK, pita=KUNING, **k):
    c.poly(_P(f, [(-40, -22), (40, -22), (40, 38), (-40, 38)]), warna, OW * s, OUT)
    c.poly(_P(f, [(-44, -36), (44, -36), (44, -18), (-44, -18)]), terang(warna, .2), OW * s, OUT)
    c.poly(_P(f, [(-6, -36), (6, -36), (6, 38), (-6, 38)]), pita, 2.6 * s, OUT)
    c.blob(_P(f, [(0, -38), (-26, -62), (-14, -66), (0, -42)]), pita, 3 * s, OUT)
    c.blob(_P(f, [(0, -38), (26, -62), (14, -66), (0, -42)]), pita, 3 * s, OUT)


def bunga(c, f, s, t, warna=PINK, **k):
    c.line(_P(f, [(0, 0), (0, 70)]), HIJAU_TUA, 6 * s)
    for i in range(6):
        a = math.radians(i * 60)
        c.ell(*f(math.cos(a) * 20, math.sin(a) * 20 - 6), 15 * s, 15 * s, warna, 3 * s, OUT)
    c.ell(*f(0, -6), 11 * s, 11 * s, KUNING, 3 * s, OUT)


def uang(c, f, s, t, **k):
    c.poly(_P(f, [(-50, -26), (50, -26), (50, 26), (-50, 26)]), HIJAU_MUDA, OW * s, OUT)
    c.ell(*f(0, 0), 15 * s, 15 * s, HIJAU, 3 * s, OUT)
    c.text(*f(0, 0), "Rp", 15 * s, OUT, "judul") if False else None


def laptop(c, f, s, t, layar=(36, 44, 70), **k):
    c.poly(_P(f, [(-70, -50), (70, -50), (64, 24), (-64, 24)]), (210, 214, 226), OW * s, OUT)
    c.poly(_P(f, [(-60, -42), (60, -42), (56, 18), (-56, 18)]), layar)
    for i, w in enumerate((70, 48, 84, 40)):
        c.line(_P(f, [(-48, -28 + i * 12), (-48 + w, -28 + i * 12)]), (120, 220, 170) if i % 2 == 0 else (250, 200, 90), 3.4 * s, False)
    c.poly(_P(f, [(-84, 24), (84, 24), (96, 42), (-96, 42)]), (180, 186, 202), OW * s, OUT)


def weker(c, f, s, t, jam="07:00", on=False, **k):
    sh = math.sin(t * 60) * 3 * s if on else 0
    ff = _T(f(0, 0)[0] + sh, f(0, 0)[1], 1.0, 0)
    c.poly(_P(ff, [(-70 * s, -36 * s), (70 * s, -36 * s), (70 * s, 36 * s), (-70 * s, 36 * s)]), (40, 40, 52), OW * s, OUT)
    c.poly(_P(ff, [(-60 * s, -26 * s), (60 * s, -26 * s), (60 * s, 26 * s), (-60 * s, 26 * s)]), (18, 18, 24))
    c.text(*ff(0, 0), jam, 38 * s, (255, 70, 70), "seru")


def jam_digital(c, f, s, t, jam="07:00", **k):
    weker(c, f, s, t, jam=jam)


def otak(c, f, s, t, warna=(250, 174, 198), **k):
    """Ikon/properti otak pink berlekuk-lekuk gaya komik chibi."""
    wob = 1.0 + 0.03 * math.sin(t * 4.5)
    ss = s * wob
    lip = gelap(warna, 0.24)
    lobes = [(-38, -6, 22), (-24, -26, 24), (-4, -30, 22), (16, -28, 23), (36, -12, 22),
             (40, 12, 21), (20, 26, 20), (-2, 24, 18), (-24, 24, 21), (-40, 12, 20)]
    for lx, ly, lr in lobes:
        c.ell(*f(lx, ly), lr * ss + OW * s, lr * ss + OW * s, OUT)
    c.ell(*f(0, 0), 42 * ss + OW * s, 28 * ss + OW * s, OUT)
    c.ell(*f(0, 0), 42 * ss, 28 * ss, warna)
    for lx, ly, lr in lobes:
        c.ell(*f(lx, ly), lr * ss, lr * ss, warna)
    # belahan tengah & lekukan sulkus
    c.curve(_P(f, [(0, -34), (-2, -8), (2, 16), (0, 30)]), lip, 3.6 * s)
    c.curve(_P(f, [(-34, -8), (-18, -14), (-10, -2)]), lip, 3.2 * s)
    c.curve(_P(f, [(-32, 12), (-16, 6), (-12, 18)]), lip, 3.2 * s)
    c.curve(_P(f, [(34, -8), (18, -14), (10, -2)]), lip, 3.2 * s)
    c.curve(_P(f, [(32, 12), (16, 6), (12, 18)]), lip, 3.2 * s)
    c.ell(*f(-18, -22), 7 * ss, 4 * ss, (255, 255, 255, 150))


def virus(c, f, s, t, warna=(112, 204, 88), mata=True, **k):
    """Properti virus hijau berduri mahkota dengan ekspresi nakal."""
    wob = 1.0 + 0.05 * math.sin(t * 7.0)
    ss = s * wob
    r = 30.0
    spikes = []
    for i in range(10):
        a = math.radians(i * 36 + math.sin(t * 2.5) * 6)
        ca, sa = math.cos(a), math.sin(a)
        spikes.append(((ca * (r - 2), sa * (r - 2)), (ca * (r + 15), sa * (r + 15))))
    # pass 1: outline
    for p0, p1 in spikes:
        c.line(_P(f, [p0, p1]), OUT, 13 * ss)
        c.ell(*f(*p1), 9.5 * ss + OW * .8 * s, 9.5 * ss + OW * .8 * s, OUT)
    c.ell(*f(0, 0), r * ss + OW * s, r * ss + OW * s, OUT)
    # pass 2: isi
    for p0, p1 in spikes:
        c.line(_P(f, [p0, p1]), warna, 6.5 * ss)
        c.ell(*f(*p1), 8.2 * ss, 8.2 * ss, terang(warna, 0.22))
    c.ell(*f(0, 0), r * ss, r * ss, warna)
    c.ell(*f(-14, 12), 5.5 * ss, 4.5 * ss, gelap(warna, 0.22))
    c.ell(*f(16, -12), 4.5 * ss, 4.5 * ss, gelap(warna, 0.22))
    if mata:
        for sg in (-1, 1):
            c.ell(*f(sg * 10, -3), 5.2 * ss, 6.0 * ss, OUT)
            c.ell(*f(sg * 10 - 1.5, -5), 2.0 * ss, 2.0 * ss, PUTIH)
            c.line(_P(f, [(sg * 16, -11), (sg * 4, -7)]), OUT, 3.2 * s)
        c.curve(_P(f, [(-10, 10), (0, 16), (10, 10)]), OUT, 3.0 * s)


def sel_imun(c, f, s, t, warna=(236, 248, 255), **k):
    """Properti sel darah putih (sistem imun) berpendar biru muda."""
    wob = 1.0 + 0.04 * math.sin(t * 5.0)
    ss = s * wob
    c.ell(*f(0, 0), 40 * ss, 40 * ss, (120, 204, 252, 85))
    bumps = [(math.cos(math.radians(i * 45)) * 22, math.sin(math.radians(i * 45)) * 22, 16) for i in range(8)]
    for bx, by, br in bumps:
        c.ell(*f(bx, by), br * ss + OW * .9 * s, br * ss + OW * .9 * s, OUT)
    c.ell(*f(0, 0), 28 * ss, 28 * ss, warna)
    for bx, by, br in bumps:
        c.ell(*f(bx, by), br * ss, br * ss, warna)
    c.ell(*f(0, 0), 16 * ss, 16 * ss, (170, 224, 255, 160))


def termometer(c, f, s, t, suhu=0.85, **k):
    """Termometer komik dengan raksa merah naik saat demam."""
    lvl = clamp(suhu + 0.04 * math.sin(t * 5.0), 0.15, 0.96)
    c.line(_P(f, [(0, -64), (0, 28)]), OUT, 28 * s)
    c.ell(*f(0, 38), 24 * s + OW * s, 24 * s + OW * s, OUT)
    c.line(_P(f, [(0, -64), (0, 28)]), (242, 248, 255), 20 * s)
    c.ell(*f(0, 38), 24 * s, 24 * s, (242, 248, 255))
    top_y = lerp(24, -56, lvl)
    col = MERAH if lvl > 0.6 else ORANYE if lvl > 0.4 else HIJAU
    c.line(_P(f, [(0, top_y), (0, 34)]), col, 11 * s)
    c.ell(*f(0, 38), 16 * s, 16 * s, col)
    c.ell(*f(-5, 33), 4.5 * s, 4.5 * s, (255, 255, 255, 180))
    for yy in (-48, -32, -16, 0, 16):
        c.line(_P(f, [(10, yy), (18, yy)]), OUT, 2.8 * s, False)


BENDA = {"hp": hp, "buku": buku, "pensil": pensil, "stik": stik, "bola": bola, "kertas": kertas, "gelas": gelas,
         "payung": payung, "kado": kado, "bunga": bunga, "uang": uang, "laptop": laptop, "weker": weker, "jam": jam_digital,
         "otak": otak, "virus": virus, "sel_imun": sel_imun, "termometer": termometer}


# ----------------------------------------------------------------- ikon komik
def tanda_seru(c, f, s, t, warna=MERAH, **k):
    c.poly(_P(f, [(-14, -50), (14, -50), (9, 14), (-9, 14)]), warna, OW * s, OUT)
    c.ell(*f(0, 34), 10 * s, 10 * s, warna, OW * s, OUT)


def tanya(c, f, s, t, warna=BIRU, **k):
    pts = arc_pts(0, -26, 22, 22, 180, 400, 16)
    c.line(_P(f, pts + [(0, 14)]), OUT, 20 * s)
    c.line(_P(f, pts + [(0, 14)]), warna, 12 * s)
    c.ell(*f(0, 38), 10 * s, 10 * s, warna, OW * s, OUT)


def hati(c, f, s, t, warna=MERAH, **k):
    pts = [(0, 34), (-40, -4), (-36, -30), (-16, -38), (0, -22), (16, -38), (36, -30), (40, -4)]
    c.blob(_P(f, pts), warna, OW * s, OUT, n=6)
    c.ell(*f(-18, -24), 5 * s, 4 * s, (255, 255, 255, 160))


def bintang(c, f, s, t, warna=KUNING, **k):
    pts = []
    for i in range(10):
        r = 40 if i % 2 == 0 else 17
        a = math.radians(-90 + i * 36)
        pts.append((r * math.cos(a), r * math.sin(a)))
    c.poly(_P(f, pts), warna, OW * s, OUT)


def kilau(c, f, s, t, warna=KUNING, **k):
    r = 30 * (1 + 0.15 * math.sin(t * 10))
    pts = [(0, -r), (6, -6), (r, 0), (6, 6), (0, r), (-6, 6), (-r, 0), (-6, -6)]
    c.poly(_P(f, pts), warna, 3 * s, OUT)


def zzz(c, f, s, t, **k):
    for i, (dx, dy, sz) in enumerate(((0, 0, 26), (26, -34, 34), (60, -76, 44))):
        wob = math.sin(t * 3 + i) * 3
        c.text(*f(dx, dy + wob), "Z", sz * s, PUTIH, "seru", stroke=4 * s)


def bohlam(c, f, s, t, **k):
    for i in range(7):
        a = math.radians(-160 + i * 22)
        c.line(_P(f, [(math.cos(a) * 58, math.sin(a) * 58 - 8), (math.cos(a) * 80, math.sin(a) * 80 - 8)]), KUNING_MUDA if False else ORANYE, 5 * s)
    c.ell(*f(0, -8), 36 * s, 36 * s, KUNING_MUDA, OW * s, OUT)
    c.poly(_P(f, [(-16, 22), (16, 22), (12, 42), (-12, 42)]), ABU, OW * s, OUT)
    c.line(_P(f, [(-8, 4), (-4, -12), (4, 4), (8, -12)]), ORANYE, 4 * s)


def not_musik(c, f, s, t, warna=BIRU_TUA, **k):
    c.ell(*f(-8, 24), 14 * s, 10 * s, warna, OW * .8 * s, OUT)
    c.line(_P(f, [(2, 22), (2, -34)]), OUT, 6 * s)
    c.poly(_P(f, [(2, -34), (24, -22), (24, -12), (2, -24)]), OUT)


def keringat(c, f, s, t, **k):
    c.poly(_P(f, [(0, -30), (14, 0), (10, 16), (-10, 16), (-14, 0)]), BIRU_MUDA, OW * .8 * s, OUT)


def centang(c, f, s, t, warna=HIJAU, **k):
    c.ell(*f(0, 0), 34 * s, 34 * s, warna, OW * s, OUT)
    c.line(_P(f, [(-16, 2), (-4, 14), (18, -12)]), PUTIH, 9 * s)


def silang(c, f, s, t, warna=MERAH, **k):
    c.ell(*f(0, 0), 34 * s, 34 * s, warna, OW * s, OUT)
    c.line(_P(f, [(-14, -14), (14, 14)]), PUTIH, 9 * s)
    c.line(_P(f, [(14, -14), (-14, 14)]), PUTIH, 9 * s)


def koin(c, f, s, t, **k):
    c.ell(*f(0, 0), 30 * s, 30 * s, KUNING, OW * s, OUT)
    c.ell(*f(0, 0), 20 * s, 20 * s, None, 3 * s, ORANYE)
    c.text(*f(0, 1), "$" if False else "Rp", 18 * s, ORANYE, "seru")


def debu(c, f, s, t, **k):
    for (dx, dy, r) in ((-18, 0, 14), (0, -8, 18), (20, 0, 14)):
        c.ell(*f(dx, dy), r * s, r * s, (255, 255, 255, 220), 3 * s, OUT)


def gelombang(c, f, s, t, **k):   # garis gerak
    for i in range(3):
        c.line(_P(f, [(0, i * 16 - 16), (-40 - i * 10, i * 16 - 16)]), OUT, 4 * s)


def awan_pikir(c, f, s, t, **k):
    for (dx, dy, r) in ((-30, 10, 26), (0, -4, 34), (34, 8, 28), (8, 22, 26)):
        c.ell(*f(dx, dy), r * s, r * s, PUTIH, OW * s, OUT)
    for (dx, dy, r) in ((-30, 10, 26), (0, -4, 34), (34, 8, 28), (8, 22, 26)):
        c.ell(*f(dx, dy), r * s - OW * s * .5, r * s - OW * s * .5, PUTIH)


def awan(c, f, s, t, **k):
    for (dx, dy, r) in ((-40, 6, 30), (0, -10, 42), (44, 4, 32), (4, 14, 30)):
        c.ell(*f(dx, dy), r * s, r * s, PUTIH, 0)


def pusing(c, f, s, t, warna=KUNING, **k):
    """Lingkaran pusing berputar + 3 bintang kecil tepat di atas kepala."""
    # lintasan elips putar
    ring = [(math.cos(math.radians(a)) * 86, math.sin(math.radians(a)) * 24) for a in range(0, 361, 15)]
    c.curve(_P(f, ring), OUT, 4.2 * s)
    ring2 = [(math.cos(math.radians(a)) * 58, math.sin(math.radians(a)) * 15 - 10) for a in range(0, 361, 18)]
    c.curve(_P(f, ring2), OUT, 3.2 * s)
    # 3 bintang berputar mengikuti elips
    for i in range(3):
        ang = t * 4.2 + i * (2 * math.pi / 3)
        sx, sy = math.cos(ang) * 86, math.sin(ang) * 24
        sc = 0.42 + 0.12 * math.sin(ang)
        pts = []
        for j in range(10):
            rr = (38 if j % 2 == 0 else 16) * sc
            aa = math.radians(-90 + j * 36)
            pts.append((sx + rr * math.cos(aa), sy + rr * math.sin(aa)))
        c.poly(_P(f, pts), warna, 3.0 * s, OUT)


IKON = {"tanda_seru": tanda_seru, "seru": tanda_seru, "tanya": tanya, "hati": hati, "bintang": bintang, "kilau": kilau,
        "zzz": zzz, "bohlam": bohlam, "ide": bohlam, "not": not_musik, "musik": not_musik, "keringat": keringat,
        "centang": centang, "silang": silang, "koin": koin, "debu": debu, "gerak": gelombang, "awan_pikir": awan_pikir,
        "awan": awan, "pusing": pusing}


def gambar(c, jenis, x, y, s=1.0, rot=0.0, t=0.0, **opsi):
    if draw_engineering_2d(c, jenis, x, y, s=s, rot=rot, t=t, **opsi):
        return True
    fn = BENDA.get(jenis) or IKON.get(jenis)
    if fn is None:
        return False
    fn(c, _T(x, y, s, rot), s, t, **opsi)
    return True
