# -*- coding: utf-8 -*-
"""
dunia.py - latar (set) gaya stikman: pastel datar + garis tepi hitam, lantai di y=0.

Tiap set = (belakang, depan):
  belakang(c, t, o) digambar SEBELUM tokoh; depan(c, t, o) SESUDAH tokoh (meja, selimut, semak depan).
o = opsi adegan: waktu (pagi|siang|sore|malam), jam, papan, warna, ...
Lapisan: c.set_depth(d) -> d<1 jauh (bergeser lebih sedikit saat kamera bergerak), d>1 dekat (foreground).
"""
import math, random
from PIL import Image, ImageFilter
from stik import *

OW = 4.0
X0, X1 = -3200, 3200

LANGIT = {
    "pagi":  ((104, 164, 212), (242, 232, 206)),
    "siang": ((82, 156, 208), (216, 236, 244)),
    "sore":  ((196, 122, 118), (248, 208, 158)),
    "malam": ((26, 36, 76), (68, 82, 134)),
}
TINT = {"pagi": ((255, 220, 150), 22), "siang": ((255, 255, 255), 0), "sore": ((255, 140, 80), 46), "malam": ((16, 24, 100), 112)}
TINT_FG = {"pagi": 0.6, "siang": 0, "sore": 0.7, "malam": 0.5}


def waktu_of(o):
    return o.get("waktu", "siang")


def tint(c, o, fg=False):
    w = waktu_of(o)
    col, a = TINT.get(w, TINT["siang"])
    if fg:
        a = int(a * TINT_FG.get(w, 0))
    if a > 0:
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=col + (a,))


def langit(c, o, sun=True, horizon=0.78, t=0.0):
    w = waktu_of(o)
    top, bot = LANGIT.get(w, LANGIT["siang"])
    c.gradient(top, bot, 0, horizon + 0.2)
    c.set_depth(0.15)
    if w == "malam":
        for i in range(40):
            x = ((i * 397) % 2800) - 1400
            y = -((i * 211) % 720) - 360
            tw = 0.65 + 0.35 * math.sin(t * 2.4 + i * 1.7)
            r = (2.5 + (i % 3)) * tw
            c.ell(x, y, r, r, (255, 250, 224))
        c.ell(560, -720, 120, 120, (255, 244, 190, 28))
        c.ell(560, -720, 74, 74, (255, 244, 190), OW * .8, OUT)
        c.ell(594, -740, 62, 62, (24, 32, 86))     # sabit bulan
        c.ell(560, -720, 74, 74, None, OW * .8, OUT)
    elif sun:
        sx, sy = {"pagi": (-520, -640), "siang": (560, -860), "sore": (-300, -340)}.get(w, (560, -860))
        col = (255, 214, 96) if w != "sore" else (255, 134, 76)
        # pendaran matahari berlapis + sunbeams diagonal lembut
        c.ell(sx, sy, 230, 230, col + (28,))
        c.ell(sx, sy, 145, 145, col + (52,))
        c.ell(sx, sy, 74, 74, col, OW * .7, OUT)
        if w in ("pagi", "sore"):
            dir_s = 1 if sx < 0 else -1
            for b in range(3):
                bx = sx + dir_s * (120 + b * 240)
                c.poly([(sx, sy), (sx + dir_s * 60, sy + 20),
                        (bx + dir_s * 620, 120), (bx + dir_s * 420, 120)],
                       col + (22,))
    c.set_depth(1.0)


def awan(c, x, y, s=1.0, col=(255, 255, 255), menjulang=False, gaya=None):
    """4 variasi awan soft Ghibli tanpa outline: 'kumulus', 'tipis', 'gumpal_lebar', 'puncak_jauh'."""
    if gaya is None:
        gaya = "kumulus" if menjulang else "gumpal_lebar"
    sh_deep = mix(col, (148, 178, 212), 0.36)
    sh_mid = mix(col, (192, 214, 234), 0.22)
    cream = mix(col, (254, 250, 238), 0.50)

    if gaya == "tipis":
        puffs = [(-145, 6, 72, 14), (-64, -4, 88, 18), (26, 2, 92, 16), (118, -2, 74, 14), (186, 6, 48, 11)]
        for dx, dy, rx, ry in puffs:
            c.ell(x + dx * s, y + (dy + 4) * s, rx * s, ry * s, sh_mid + (135,))
            c.ell(x + (dx - 6) * s, y + dy * s, rx * 0.88 * s, ry * 0.78 * s, cream + (185,))
        return

    if gaya == "puncak_jauh":
        puffs = [(-160, 26, 86, 42), (-74, 6, 96, 58), (24, -12, 108, 66), (118, 10, 88, 50), (190, 28, 70, 38)]
    elif gaya == "kumulus":
        puffs = [
            (-118, 42, 72, 54), (-52, 52, 86, 56), (34, 48, 92, 58), (114, 38, 74, 52),
            (-92, -16, 78, 66), (-18, -32, 98, 84), (66, -18, 82, 68),
            (-48, -98, 76, 72), (24, -108, 84, 78), (82, -74, 58, 54),
            (-8, -168, 68, 66), (42, -154, 50, 48), (6, -214, 44, 42),
        ]
    else:
        puffs = [
            (-116, 16, 64, 30), (-42, 20, 78, 34), (42, 18, 76, 32), (114, 14, 58, 28),
            (-68, -14, 64, 40), (4, -26, 82, 48), (74, -12, 60, 38),
            (-18, -52, 54, 34), (36, -44, 46, 30),
        ]
    for dx, dy, rx, ry in puffs:
        c.ell(x + (dx + 8) * s, y + (dy + 11) * s, rx * s, ry * s, sh_deep)
    for dx, dy, rx, ry in puffs:
        c.ell(x + (dx + 2) * s, y + (dy + 4) * s, rx * 0.94 * s, ry * 0.90 * s, sh_mid)
    for dx, dy, rx, ry in puffs:
        if dy < 32:
            c.ell(x + (dx - 6) * s, y + (dy - 5) * s, rx * 0.84 * s, ry * 0.80 * s, cream)
    for dx, dy, rx, ry in puffs:
        if dy < -12:
            c.ell(x + (dx - 11) * s, y + (dy - 11) * s, rx * 0.62 * s, ry * 0.54 * s, col)


def bukit_berlapis(c, o, y0=0):
    """3 lapis pegunungan & bukit bervolume (jauh pudar -> tengah -> dekat hangat)."""
    w = waktu_of(o)
    if w == "malam":
        c1, c2, c3 = (40, 48, 98), (32, 44, 86), (28, 52, 74)
    elif w == "sore":
        c1, c2, c3 = (196, 138, 152), (168, 118, 126), (126, 136, 96)
    elif w == "pagi":
        c1, c2, c3 = (164, 198, 224), (138, 186, 196), (124, 182, 136)
    else:
        c1, c2, c3 = (154, 196, 230), (122, 182, 194), (116, 184, 132)
    # lapis 1: pegunungan jauh
    c.set_depth(0.28)
    c.blob([(-2200, y0 + 20), (-1650, y0 - 290), (-1050, y0 - 170), (-420, y0 - 340),
            (240, y0 - 180), (920, y0 - 310), (1580, y0 - 190), (2200, y0 + 20)], c1, 0)
    # lapis 2: bukit tengah bervolume (highlight sisi kiri puncak)
    c.set_depth(0.42)
    c.blob([(-2200, y0 + 20), (-1500, y0 - 200), (-820, y0 - 110), (-140, y0 - 220),
            (540, y0 - 120), (1240, y0 - 210), (1950, y0 - 90), (2200, y0 + 20)], c2, 0)
    # lapis 3: bukit dekat hangat
    c.set_depth(0.58)
    c.blob([(-2200, y0 + 20), (-1350, y0 - 120), (-620, y0 - 68), (80, y0 - 135),
            (840, y0 - 72), (1560, y0 - 125), (2200, y0 + 20)], c3, 0)
    c.set_depth(1.0)


def awan_set(c, o, n=6, t=0.0):
    w = waktu_of(o)
    if w == "malam":
        return
    c.set_depth(0.18)
    col = (254, 252, 246) if w != "sore" else (252, 224, 196)
    drift = t * 11.0
    specs = [
        (-860, -290, 1.35, "puncak_jauh"),
        (560, -360, 1.55, "kumulus"),
        (-240, -680, 1.05, "tipis"),
        (1180, -640, 0.95, "gumpal_lebar"),
        (-1380, -740, 0.92, "gumpal_lebar"),
        (120, -820, 1.15, "tipis"),
    ]
    for idx, (ax0, ay0, sc, gy) in enumerate(specs[:max(4, n)]):
        spd = 0.55 if gy in ("kumulus", "puncak_jauh") else 1.0
        ax = ((ax0 + drift * spd + 2200) % 4400) - 2200
        awan(c, ax, ay0, sc, col, gaya=gy)
    haze = (224, 240, 246, 85) if w != "sore" else (250, 212, 174, 92)
    c.rect(X0, -180, X1, 40, haze)
    c.set_depth(0.24)
    bcol = (248, 250, 252) if w == "siang" else ((118, 134, 158) if w == "pagi" else (126, 84, 88))
    for bi in range(3):
        bx = ((-420 + bi * 95 + t * (42 + bi * 4) + 1800) % 3600) - 1800
        by = -620 - bi * 32 + math.sin(t * 2.2 + bi) * 10
        flap = math.sin(t * 7.5 + bi * 1.9) * 6.5
        c.curve([(bx - 14, by - flap), (bx - 3, by - 3), (bx, by + 2)], bcol, 2.5)
        c.curve([(bx, by + 2), (bx + 3, by - 3), (bx + 14, by - flap)], bcol, 2.5)
    c.set_depth(1.0)


def lantai(c, col, y1=1400, garis=None, step=0):
    c.rect(X0, 0, X1, y1, col)
    # sedikit bayangan halus di sepanjang batas lantai-dinding
    c.rect(X0, 0, X1, 22, gelap(col, 0.08))
    c.line([(X0, 0), (X1, 0)], OUT, OW)
    if garis:
        for i in range(1, 14):
            yy = i * i * 6 + 14
            if yy < y1:
                c.line([(X0, yy), (X1, yy)], garis, 2.4, False)


def dinding(c, col, atas=-1700):
    c.rect(X0, atas, X1, 0, col)


def papan_nama(c, x, y, w, h, teks, col=(255, 226, 130), size=64):
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, col, OW, OUT, r=10)
    c.text(x, y + 2, teks, size, (54, 60, 86), "judul")


def _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t):
    """Kanopi lukisan gouache Ghibli: TANPA outline hitam kaku, ratusan sapuan daun organik bertingkat 5 nada."""
    rng = random.Random(int(abs(x * 13 + cy * 7)) + len(lobes) * 97)
    # 5 nada warna khas Ghibli: deep blue-teal shadow -> forest shadow -> midtone -> warm sunlit -> yellow-lime rim
    deep_c = mix(gelap(wc, 0.48), (22, 62, 82), 0.42)
    sh_c = mix(gelap(wc, 0.24), (34, 86, 78), 0.26)
    mid_c = wc
    sun_c = terang(mix(wc, (232, 240, 118), 0.34), 0.10)
    rim_c = terang(mix(wc, (254, 248, 162), 0.50), 0.22)

    # lapis 1: massa bayangan dalam bergerigi organik (daun-daun tepi menggantikan outline vektor kaku!)
    for dx_, dy_, rx_, ry_ in lobes:
        cx_ = x + dx_ * s + sway
        cy_ = cy + dy_ * s
        c.ell(cx_, cy_, rx_ * s, ry_ * s, deep_c)
        # tepi daun organik di sekeliling setiap klaster (silhouette leafy brush dabs)
        n_dabs = 7 if far else 11
        for k in range(n_dabs):
            ang = (k / n_dabs) * math.tau + rng.uniform(-0.22, 0.22)
            rr = rng.uniform(0.76, 1.04)
            bx = cx_ + math.cos(ang) * rx_ * rr * s
            by = cy_ + math.sin(ang) * ry_ * rr * s
            dr = rng.uniform(14, 24) * s * (rx_ / 72.0)
            c.ell(bx, by, dr, dr * rng.uniform(0.68, 0.95), deep_c)

    # lapis 2: klaster bayangan hutan (sedikit bergeser ke kiri-atas)
    for dx_, dy_, rx_, ry_ in lobes:
        cx_ = x + (dx_ - 4) * s + sway
        cy_ = cy + (dy_ - 9) * s
        c.ell(cx_, cy_, rx_ * 0.90 * s, ry_ * 0.86 * s, sh_c)
        for k in range(5 if far else 8):
            ang = rng.uniform(0, math.tau)
            bx = cx_ + math.cos(ang) * rx_ * rng.uniform(0.35, 0.85) * s
            by = cy_ + math.sin(ang) * ry_ * rng.uniform(0.35, 0.80) * s
            dr = rng.uniform(13, 22) * s * (rx_ / 72.0)
            c.ell(bx, by, dr, dr * 0.78, sh_c)

    # lapis 3: massa daun utama (midtone)
    for dx_, dy_, rx_, ry_ in lobes:
        if dy_ <= 24 or dx_ <= 45:
            cx_ = x + (dx_ - 9) * s + sway
            cy_ = cy + (dy_ - 17) * s
            c.ell(cx_, cy_, rx_ * 0.76 * s, ry_ * 0.70 * s, mid_c)
            for k in range(4 if far else 7):
                ang = rng.uniform(math.pi * 0.8, math.pi * 2.15)
                bx = cx_ + math.cos(ang) * rx_ * rng.uniform(0.25, 0.75) * s
                by = cy_ + math.sin(ang) * ry_ * rng.uniform(0.20, 0.70) * s
                dr = rng.uniform(11, 19) * s * (rx_ / 72.0)
                c.ell(bx, by, dr, dr * 0.76, mid_c)

    # lapis 4 & 5: klaster daun tersinari matahari hangat + highlight puncak (dappled foliage dabs)
    for dx_, dy_, rx_, ry_ in lobes:
        if dy_ < 6 or dx_ < 10:
            cx_ = x + (dx_ - 14) * s + sway
            cy_ = cy + (dy_ - 24) * s
            for k in range(4 if far else 7):
                ang = rng.uniform(math.pi * 0.95, math.pi * 2.05)
                bx = cx_ + math.cos(ang) * rx_ * rng.uniform(0.10, 0.62) * s
                by = cy_ + math.sin(ang) * ry_ * rng.uniform(0.08, 0.52) * s
                dr = rng.uniform(9, 17) * s * (rx_ / 72.0)
                c.ell(bx, by, dr, dr * 0.72, sun_c)
            if dy_ < -14:
                for k in range(2 if far else 4):
                    bx = cx_ + rng.uniform(-rx_ * 0.42, rx_ * 0.22) * s
                    by = cy_ + rng.uniform(-ry_ * 0.42, -ry_ * 0.05) * s
                    dr = rng.uniform(7, 13) * s * (rx_ / 72.0)
                    c.ell(bx, by, dr, dr * 0.66, rim_c)


def pohon(c, x, s=1.0, warna=HIJAU, batang=COKLAT, tinggi=300, gaya=None, t=0.0):
    """7 spesies pohon organik bergaya Ghibli dengan siluet yang benar-benar berbeda satu sama lain."""
    if gaya is None:
        gaya = ("rimbun", "bulat_tinggi", "cemara", "sakura", "palem", "gugur", "beringin")[abs(int(round(x / 137))) % 7]
    if gaya == "sakura":
        warna = (244, 168, 196)
    elif gaya == "gugur":
        warna = (232, 134, 62)
    elif gaya == "beringin":
        warna = (74, 150, 92)
    elif gaya == "cemara" and warna == HIJAU:
        warna = (58, 136, 98)
    elif gaya == "rimbun" and warna == HIJAU:
        warna = (92, 174, 96)
    elif gaya == "bulat_tinggi" and warna == HIJAU:
        warna = (104, 184, 102)

    far = getattr(c, "depth", 1.0) < 0.85
    fog = (182, 212, 232)
    wc = mix(warna, fog, 0.34) if far else warna
    bc = mix(batang, fog, 0.30) if far else batang
    oc = mix(OUT, fog, 0.55) if far else OUT
    ow_t = (OW * 0.42 if far else OW * 0.75) * s
    h = tinggi * s
    sway = math.sin(t * 1.5 + x * 0.013) * 5.0 * s

    # bayangan jatuh organik 2 lapis di tanah
    c.ell(x + 24 * s, 8 * s, 126 * s, 24 * s, (24, 52, 42, 22 if far else 38))
    c.ell(x + 12 * s, 5 * s, 72 * s, 13 * s, (20, 44, 36, 18 if far else 30))

    if gaya == "cemara":
        # PINUS GHIBLI: cabang organik bergelombang & klaster jarum asimetris (bukan segitiga kaku!)
        c.poly([(x - 20 * s, 0), (x + 20 * s, 0), (x + 9 * s, -h * 0.65), (x - 9 * s, -h * 0.65)], bc, ow_t, oc)
        c.poly([(x + 2 * s, 0), (x + 18 * s, 0), (x + 8 * s, -h * 0.65), (x + 1 * s, -h * 0.65)], gelap(bc, 0.24))
        cy = -h * 0.52
        lobes = [
            # tingkat bawah lebar menjuntai asimetris
            (-96, 62, 54, 34), (-38, 66, 62, 36), (34, 68, 60, 34), (92, 60, 50, 32),
            # tingkat 2
            (-76, 8, 52, 34), (-16, 12, 58, 36), (48, 14, 54, 34), (78, 4, 42, 30),
            # tingkat 3
            (-52, -46, 46, 34), (8, -42, 50, 34), (50, -48, 40, 30),
            # tingkat 4 meruncing ke puncak
            (-24, -96, 36, 32), (20, -94, 34, 30), (0, -140, 28, 34), (-4, -172, 16, 24),
        ]
        _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)
        return

    if gaya == "palem":
        # PALEM TROPIS RIMBUN: batang melengkung + 9 pelepah daun panjang berlekuk
        bend = 42 * s * (1 if int(abs(x)) % 2 == 0 else -1)
        top_x, top_y = x + bend + sway, -h * 1.18
        pts_l = bezier((x - 20 * s, 0), (x + bend * 0.45 - 13 * s, -h * 0.6), (top_x - 8 * s, top_y), 8)
        pts_r = list(reversed(bezier((x + 20 * s, 0), (x + bend * 0.45 + 13 * s, -h * 0.6), (top_x + 8 * s, top_y), 8)))
        c.poly(pts_l + pts_r, bc, ow_t, oc)
        for k in range(1, 9):
            p = k / 9.0
            rx = lerp(x, top_x, p) + math.sin(p * math.pi) * bend * 0.12
            ry = lerp(0, top_y, p)
            rw = lerp(17, 8, p) * s
            c.line([(rx - rw, ry), (rx + rw, ry - 4 * s)], gelap(bc, 0.25), 2.8 * s)
        fronds = [
            (-1, 168, 52, -26), (-1, 152, 14, -56), (-1, 126, -34, -84), (-1, 86, -68, -94),
            (1, 86, -68, -94), (1, 126, -34, -84), (1, 152, 14, -56), (1, 168, 52, -26), (1, 118, 76, -8)
        ]
        for sg_f, lx_, fy_off, my_off in fronds:
            fx = top_x + sg_f * lx_ * s + sway * 0.45
            fy = top_y + fy_off * s
            mx = top_x + sg_f * lx_ * 0.55 * s
            my = top_y + my_off * s
            fc = gelap(wc, 0.16) if fy_off > 30 else (terang(wc, 0.16) if fy_off < -40 else wc)
            # pelepah lebar melengkung + helai daun menjuntai di sisi bawah
            top_edge = bezier((top_x, top_y), (mx, my - 12 * s), (fx, fy), 7)
            bot_edge = list(reversed(bezier((top_x, top_y), (mx, my + 24 * s), (fx, fy), 7)))
            c.poly(top_edge + bot_edge, fc, ow_t * 0.72, oc)
            c.curve([(top_x, top_y), (mx, my), (fx, fy)], gelap(fc, 0.24), 2.5 * s)
        for cx_, cy_ in ((-10, 12), (10, 14), (0, 18)):
            c.ell(top_x + cx_ * s, top_y + cy_ * s, 11 * s, 12 * s, gelap(bc, 0.26), ow_t * 0.6, oc)
        return

    if gaya == "sakura":
        # WEEPING SAKURA: batang miring melengkung anggun + cabang menjuntai berderai bunga pink
        lean = 32 * s
        trunk_h = h * 0.90
        pts_l = bezier((x - 26 * s, 0), (x - 10 * s, -trunk_h * 0.5), (x + lean - 12 * s, -trunk_h), 7)
        pts_r = list(reversed(bezier((x + 26 * s, 0), (x + 18 * s, -trunk_h * 0.5), (x + lean + 12 * s, -trunk_h), 7)))
        c.poly(pts_l + pts_r, gelap(bc, 0.14), ow_t, oc)
        c.line([(x + lean * 0.5, -trunk_h * 0.62), (x - 86 * s, -trunk_h * 1.05)], gelap(bc, 0.14), 14 * s)
        c.line([(x + lean * 0.7, -trunk_h * 0.76), (x + 92 * s, -trunk_h * 1.02)], gelap(bc, 0.14), 12 * s)
        cy = -trunk_h - 32 * s
        # siluet sakura melengkung lebar & menjuntai (bukan bulat simetris!)
        lobes = [
            (-128, 34, 48, 56), (-92, -6, 68, 52), (-36, -42, 78, 56),
            (32, -48, 82, 58), (96, -12, 72, 54), (132, 32, 46, 58),
            (-64, 38, 44, 48), (68, 36, 46, 50), (0, -8, 76, 46),
        ]
        _ghibli_canopy(c, x + lean * 0.35, cy, lobes, wc, s, sway, far, oc, ow_t)
        # kelopak sakura lembut melayang
        for ki in range(5):
            px_ = x + (-110 + ki * 56) * s + math.sin(t * 2.1 + ki * 1.7) * 20 * s
            py_ = cy + (78 + ((t * 34 + ki * 38) % 145)) * s
            c.ell(px_, py_, 6 * s, 3.8 * s, (255, 228, 240))
        return

    if gaya == "gugur":
        # MAPLE / GUGUR BERTINGKAT: 3 gugusan kanopi terpisah bertumpu di dahan bercabang lebar (gaya bonsai/maple)
        trunk_h = h * 0.96
        c.poly([(x - 24 * s, 0), (x + 24 * s, 0), (x + 11 * s, -trunk_h * 0.72), (x - 11 * s, -trunk_h * 0.72)], bc, ow_t, oc)
        c.poly([(x + 2 * s, 0), (x + 22 * s, 0), (x + 10 * s, -trunk_h * 0.72), (x + 1 * s, -trunk_h * 0.72)], gelap(bc, 0.22))
        # 3 cabang utama menyebar jelas
        c.line([(x - 4 * s, -trunk_h * 0.56), (x - 92 * s, -trunk_h * 0.88)], bc, 14 * s)
        c.line([(x + 4 * s, -trunk_h * 0.62), (x + 98 * s, -trunk_h * 0.96)], bc, 13 * s)
        c.line([(x, -trunk_h * 0.68), (x - 8 * s, -trunk_h * 1.24)], bc, 12 * s)
        # 3 klaster awan daun terpisah (kiri bawah, kanan tengah, puncak atas) -> siluet benar-benar unik!
        _ghibli_canopy(c, x - 94 * s, -trunk_h * 0.92, [(-38, 8, 46, 30), (4, -10, 56, 36), (42, 6, 44, 28)], wc, s, sway * 0.7, far, oc, ow_t)
        _ghibli_canopy(c, x + 98 * s, -trunk_h * 1.02, [(-40, 10, 48, 32), (8, -12, 60, 38), (48, 8, 46, 30)], terang(wc, 0.08), s, sway * 0.85, far, oc, ow_t)
        _ghibli_canopy(c, x - 6 * s, -trunk_h * 1.32, [(-56, 12, 54, 34), (0, -14, 72, 44), (58, 10, 52, 34)], terang(wc, 0.14), s, sway, far, oc, ow_t)
        for ki in range(4):
            px_ = x + (-95 + ki * 64) * s + math.sin(t * 1.9 + ki * 2.2) * 22 * s
            py_ = -trunk_h * 0.7 + ((t * 38 + ki * 42) % 165) * s
            c.ell(px_, py_, 6.5 * s, 4 * s, (255, 206, 86))
        return

    if gaya == "bulat_tinggi":
        # POPLAR / CYPRESS TAMAN: tinggi menjulang ramping berombak seperti obor (bukan bulat melebar!)
        trunk_h = h * 0.82
        c.poly([(x - 18 * s, 0), (x + 18 * s, 0), (x + 10 * s, -trunk_h), (x - 10 * s, -trunk_h)], bc, ow_t, oc)
        c.poly([(x + 2 * s, 0), (x + 16 * s, 0), (x + 9 * s, -trunk_h), (x + 1 * s, -trunk_h)], gelap(bc, 0.22))
        cy = -trunk_h - 110 * s
        lobes = [
            (-40, 92, 46, 48), (42, 94, 44, 46), (0, 82, 56, 52),
            (-44, 34, 52, 56), (46, 38, 48, 52), (0, 18, 60, 62),
            (-32, -32, 46, 56), (34, -26, 44, 52), (0, -56, 52, 64),
            (-12, -108, 36, 48), (12, -102, 32, 44), (0, -138, 26, 36),
        ]
        _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)
        return

    if gaya == "beringin":
        # BERINGIN RAKSASA: payung sangat lebar + batang tebal berakar + akar gantung rimbun
        trunk_h = h * 0.82
        trunk_pts = [(x - 42 * s, 0), (x + 42 * s, 0), (x + 24 * s, -trunk_h * 0.34),
                     (x + 20 * s, -trunk_h), (x - 20 * s, -trunk_h), (x - 24 * s, -trunk_h * 0.34)]
        c.poly(trunk_pts, bc, ow_t, oc)
        c.poly([(x + 4 * s, 0), (x + 40 * s, 0), (x + 22 * s, -trunk_h * 0.34),
                (x + 19 * s, -trunk_h), (x + 3 * s, -trunk_h)], gelap(bc, 0.24))
        for rx_ in (-124, -92, -62, 66, 98, 128):
            c.curve([(x + rx_ * s + sway * 0.5, -trunk_h - 8 * s),
                     (x + (rx_ + 6) * s, -trunk_h * 0.48),
                     (x + (rx_ - 4) * s, -6 * s)], gelap(bc, 0.18), 4.0 * s)
        cy = -trunk_h - 36 * s
        lobes = [
            (-156, 22, 68, 44), (-98, -14, 82, 56), (-32, -46, 94, 62),
            (40, -42, 92, 60), (108, -10, 82, 54), (158, 24, 66, 42),
            (-64, 24, 76, 42), (68, 24, 76, 42), (0, 14, 86, 44),
        ]
        _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)
        return

    # RIMBUN (OAK GHIBLI): kanopi organik asimetris condong lembut + klaster daun penuh
    trunk_h = h * 0.94
    trunk_pts = [(x - 28 * s, 0), (x + 28 * s, 0), (x + 17 * s, -trunk_h * 0.3),
                 (x + 14 * s, -trunk_h), (x - 14 * s, -trunk_h), (x - 17 * s, -trunk_h * 0.3)]
    c.poly(trunk_pts, bc, ow_t, oc)
    c.poly([(x + 3 * s, 0), (x + 26 * s, 0), (x + 15 * s, -trunk_h * 0.3),
            (x + 13 * s, -trunk_h), (x + 2 * s, -trunk_h)], gelap(bc, 0.22))
    c.line([(x - 4 * s, -trunk_h * 0.68), (x - 66 * s, -trunk_h * 1.02)], bc, 15 * s)
    c.line([(x + 4 * s, -trunk_h * 0.74), (x + 54 * s, -trunk_h * 1.06)], bc, 13 * s)
    cy = -trunk_h - 52 * s
    lobes = [
        (-112, 26, 68, 52), (-68, -28, 78, 66), (-14, -66, 86, 68),
        (54, -44, 76, 62), (104, 10, 68, 54), (62, 34, 62, 46),
        (-36, 26, 70, 48), (18, -6, 74, 54),
    ]
    _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)


def semak(c, x, w=220, h=110, warna=HIJAU_TUA, y=0):
    """Semak belukar painterly Ghibli: 5 nada sapuan daun organik tanpa outline kaku + bayangan jatuh + bunga kecil."""
    far = getattr(c, "depth", 1.0) < 0.85
    wc = mix(warna, (182, 212, 232), 0.30) if far else warna
    # bayangan jatuh lembut di tanah
    c.ell(x + w * 0.06, y + 6, w * 0.56, h * 0.16, (22, 54, 42, 34 if far else 54))
    # klaster asimetris organik (bukan 4 bola polos bergaris hitam!)
    lobes = [
        (-w * 0.34, -h * 0.24, w * 0.22, h * 0.32),
        (-w * 0.14, -h * 0.44, w * 0.28, h * 0.44),
        (w * 0.12, -h * 0.40, w * 0.26, h * 0.40),
        (w * 0.34, -h * 0.22, w * 0.22, h * 0.30),
        (0.0, -h * 0.20, w * 0.32, h * 0.28),
    ]
    _ghibli_canopy(c, x, y, lobes, wc, 1.0, 0.0, far, OUT, 0.0)
    # 3-4 bintik bunga mungil di permukaan semak agar hidup & detail
    if not far:
        rng = random.Random(int(abs(x * 17 + w)))
        bcols = ((255, 250, 230), (255, 214, 102), (255, 188, 208))
        for k in range(4):
            bx = x + rng.uniform(-w * 0.34, w * 0.34)
            by = y - rng.uniform(h * 0.22, h * 0.62)
            c.ell(bx, by, 5.2, 4.4, bcols[k % len(bcols)])
            c.ell(bx, by, 2.0, 2.0, (255, 206, 68))


def bunga_detail(c, x, y, s=1.0, warna=PINK, jenis="daisy", t=0.0):
    """Bunga 2D detail dengan tangkai melengkung, daun pangkal, dan kelopak berlapis (daisy / tulip / liar)."""
    sway = math.sin(t * 2.1 + x * 0.03) * 3.5 * s
    stem_h = 46.0 * s
    tx, ty = x + sway, y - stem_h
    mx, my = x + sway * 0.45 + (4.0 if int(abs(x)) % 2 == 0 else -4.0) * s, y - stem_h * 0.52
    leaf_c = (74, 154, 78)
    leaf_sh = (48, 114, 62)
    oc = mix(OUT, leaf_sh, 0.45)

    # bayangan kecil di pangkal tangkai
    c.ell(x + 2 * s, y + 2 * s, 14 * s, 4 * s, (24, 58, 42, 42))
    # 2 daun pangkal melengkung kiri & kanan
    for sg in (-1, 1):
        lx0, ly0 = x, y - 4 * s
        lx1, ly1 = x + sg * 20 * s, y - 20 * s
        lmx, lmy = x + sg * 11 * s, y - 18 * s
        lpts = bezier((lx0, ly0), (lmx, lmy - 5 * s), (lx1, ly1), 5) + list(reversed(bezier((lx0, ly0), (lmx, lmy + 5 * s), (lx1, ly1), 5)))
        c.poly(lpts, leaf_sh if sg > 0 else leaf_c, 1.8 * s, oc)
    # tangkai melengkung halus
    c.curve([(x, y), (mx, my), (tx, ty)], leaf_sh, 3.2 * s)

    if jenis == "tulip":
        # kelopak tulip 3 lapis (belakang gelap -> kiri/kanan -> depan terang)
        c.ell(tx, ty - 6 * s, 10 * s, 14 * s, gelap(warna, 0.20), 1.6 * s, oc)
        c.poly([(tx - 12 * s, ty - 14 * s), (tx - 13 * s, ty + 2 * s), (tx - 2 * s, ty + 6 * s), (tx - 2 * s, ty - 8 * s)],
               warna, 1.6 * s, oc)
        c.poly([(tx + 12 * s, ty - 14 * s), (tx + 13 * s, ty + 2 * s), (tx + 2 * s, ty + 6 * s), (tx + 2 * s, ty - 8 * s)],
               gelap(warna, 0.08), 1.6 * s, oc)
        c.ell(tx, ty - 3 * s, 7.5 * s, 11 * s, terang(warna, 0.16), 1.4 * s, oc)
    else:
        # daisy / cosmos 6 kelopak memancar + putik emas hangat
        n_pet = 6
        for k in range(n_pet):
            ang = math.radians(k * (360.0 / n_pet) + 18)
            px = tx + math.cos(ang) * 10.5 * s
            py = ty + math.sin(ang) * 9.0 * s
            pcol = gelap(warna, 0.08) if math.sin(ang) > 0.2 else warna
            c.ell(px, py, 7.2 * s, 5.6 * s, pcol, 1.5 * s, oc)
            c.ell(px - 1.2 * s, py - 1.2 * s, 3.6 * s, 2.8 * s, terang(warna, 0.24))
        # putik tengah kuning hangat + titik kilau
        c.ell(tx, ty, 5.6 * s, 5.0 * s, (246, 192, 54), 1.4 * s, oc)
        c.ell(tx - 1.4 * s, ty - 1.4 * s, 2.2 * s, 1.8 * s, (255, 242, 168))


def _rumpun_ghibli(c, gx, gy, sc, sh_c, deep_c, sun_c, sway):
    """Satu rumpun rumput Ghibli padat (7 helai 2-nada: bayangan belakang + pucuk terang tersinari)."""
    # helai belakang (lebih gelap, melengkung alami)
    for ax, hh, w in ((-18, 20, 3.2), (-9, 28, 3.6), (2, 32, 3.8), (11, 26, 3.4), (20, 18, 3.0)):
        c.curve([(gx + ax * 0.25 * sc, gy),
                 (gx + ax * 0.65 * sc, gy - hh * 0.55 * sc),
                 (gx + (ax + sway) * sc, gy - hh * sc)], deep_c, w * sc)
    # helai depan (lebih terang & hangat, menonjolkan volume)
    for ax, hh, w in ((-12, 22, 2.8), (-2, 27, 3.0), (8, 21, 2.6)):
        c.curve([(gx + ax * 0.2 * sc, gy + 1.5 * sc),
                 (gx + ax * 0.6 * sc, gy - hh * 0.52 * sc),
                 (gx + (ax + sway * 1.1) * sc, gy - hh * sc)], sun_c, w * sc)


def rumput(c, y1=1400, warna=HIJAU_MUDA, t=0.0):
    """Padang rumput bergaya Studio Ghibli: gelombang bukit, hamparan rumpun rumput padat 2-nada, & bunga detail."""
    base_c = mix(warna, (124, 192, 96), 0.42)
    sun_c = terang(mix(base_c, (238, 244, 134), 0.40), 0.14)
    sh_c = mix(gelap(base_c, 0.22), (42, 94, 68), 0.26)
    deep_c = mix(gelap(base_c, 0.36), (28, 72, 56), 0.34)
    blade_sun = terang(mix(base_c, (220, 238, 120), 0.35), 0.08)

    c.rect(X0, 0, X1, y1, base_c)
    # 3 gelombang lereng rumput lembut (rolling painterly swells)
    c.blob([(-2800, 14), (-1900, -10), (-950, 18), (0, -6), (980, 20), (1950, -8), (2800, 14),
            (2800, 220), (-2800, 220)], sun_c, 0, n=6)
    c.blob([(-2800, 88), (-1800, 52), (-800, 102), (180, 58), (1180, 106), (2100, 64), (2800, 90),
            (2800, 380), (-2800, 380)], base_c, 0, n=6)
    c.blob([(-2800, 195), (-1650, 155), (-550, 210), (480, 162), (1550, 218), (2800, 170),
            (2800, y1), (-2800, y1)], sh_c, 0, n=6)
    # sapuan bercak cahaya matahari hangat (painterly patches)
    for i in range(-10, 11):
        px = i * 250 + (i * 73 % 90)
        py = 42 + abs(i * 61) % 160
        c.ell(px, py, 125 + (abs(i) % 3) * 34, 18 + (abs(i) % 2) * 8, sun_c + (115,))

    # tepi horizon rumput bertekstur (tidak berupa 1 garis lurus hitam kaku!)
    sway = math.sin(t * 2.0) * 3.8
    for i in range(-28, 29):
        hx = i * 74 + (i * 29 % 24)
        hh = 11 + (abs(i * 17) % 11)
        c.curve([(hx, 3), (hx + 2, -hh * 0.5), (hx + 4 + sway * 0.5, -hh)], sh_c, 3.0)
        c.curve([(hx + 10, 3), (hx + 8, -hh * 0.6), (hx + 6 + sway * 0.5, -hh * 0.85)], base_c, 2.4)
    c.line([(X0, 2), (X1, 2)], mix(deep_c, OUT, 0.30), 2.4)

    # hamparan rumpun rumput padat (3 lapis kedalaman: jauh -> tengah -> dekat)
    for i in range(-22, 23):
        gx = i * 105 + (i * 41 % 55)
        gy = 24 + (abs(i * 53) % 58)
        _rumpun_ghibli(c, gx, gy, 0.58 + (abs(i) % 3) * 0.08, sh_c, sh_c, blade_sun, sway * 0.7)
    for i in range(-18, 19):
        gx = i * 132 + (i * 67 % 68)
        gy = 86 + (abs(i * 79) % 105)
        _rumpun_ghibli(c, gx, gy, 0.82 + (abs(i) % 3) * 0.10, sh_c, deep_c, blade_sun, sway)
    for i in range(-14, 15):
        gx = i * 175 + (i * 83 % 80)
        gy = 195 + (abs(i * 43) % 140)
        _rumpun_ghibli(c, gx, gy, 1.08 + (abs(i) % 3) * 0.12, sh_c, deep_c, blade_sun, sway * 1.2)

    # klaster bunga liar berkelopak 5-kelopak (tersebar alami di rumput, bukan titik asal-asalan)
    fl_cols = ((255, 250, 234), (255, 214, 96), (252, 174, 198), (196, 224, 255))
    for i in range(-12, 13):
        fx = i * 195 + (i * 59 % 70)
        fy = 56 + (abs(i * 97) % 165)
        sc = 0.55 + (fy / 260.0) * 0.35
        bunga_detail(c, fx, fy, sc, fl_cols[abs(i) % len(fl_cols)], "daisy" if i % 3 else "tulip", t=t)


def jendela(c, x, y, w, h, o, tirai=False):
    wk = waktu_of(o)
    top, bot = LANGIT.get(wk, LANGIT["siang"])
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, KAYU_TUA, OW * 1.4, OUT, r=8)
    x0, x1, y0, y1 = x - w / 2 + 16, x + w / 2 - 16, y - h / 2 + 16, y + h / 2 - 16
    c.rect(x0, y0, x1, y1, mix(top, bot, .5), OW, OUT)
    if wk == "malam":
        c.ell(x + w * .18, y - h * .12, w * .12, w * .12, (255, 244, 190), 3, OUT)
        for i in range(5):
            c.ell(x - w * .3 + i * w * .13, y - h * .3 + (i % 2) * 30, 3, 3, (255, 250, 220))
    else:
        c.ell(x + w * .16, y - h * .1, w * .13, w * .13, (255, 206, 60) if wk != "sore" else (255, 120, 70), 3, OUT)
        awan(c, x - w * .2, y + h * .18, w / 460, (255, 255, 255))
    # pantulan kaca diagonal lembut
    c.poly([(x0 + 18, y1 - 8), (x0 + 54, y1 - 8), (x1 - 22, y0 + 8), (x1 - 56, y0 + 8)], (255, 255, 255, 42))
    c.line([((x0 + x1) / 2, y0), ((x0 + x1) / 2, y1)], OUT, OW)
    c.line([(x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)], OUT, OW)
    c.rect(x0 - 12, y1 + 6, x1 + 12, y1 + 24, KAYU, OW, OUT, r=6)
    # berkas cahaya lembut jatuh masuk dari jendela (pagi/siang/sore)
    if wk != "malam":
        scol = (255, 236, 178, 26) if wk != "sore" else (255, 174, 118, 32)
        c.poly([(x0, y0), (x1, y0), (x1 - w * 0.55, 220), (x0 - w * 0.75, 220)], scol)


def tanaman(c, x, y=0, s=1.0, pot=ORANYE):
    c.poly([(x - 34 * s, y - 70 * s), (x + 34 * s, y - 70 * s), (x + 26 * s, y), (x - 26 * s, y)], pot, OW * s, OUT)
    for a, l in ((-42, 120), (-16, 150), (14, 140), (40, 112), (0, 170)):
        r = math.radians(a - 90)
        tx, ty = x + math.cos(r) * l * s, y - 70 * s + math.sin(r) * l * s
        c.blob([(x, y - 70 * s), (x + math.cos(r + .45) * l * .5 * s, y - 70 * s + math.sin(r + .45) * l * .5 * s), (tx, ty),
                (x + math.cos(r - .45) * l * .5 * s, y - 70 * s + math.sin(r - .45) * l * .5 * s)], HIJAU, OW * .8 * s, OUT, n=5)


def rak_buku(c, x, y, w=300, h=520, rows=4, seed=0):
    c.rect(x - w / 2, y - h, x + w / 2, y, KAYU_TUA, OW, OUT, r=6)
    c.rect(x - w / 2 + 14, y - h + 14, x + w / 2 - 14, y - 14, (206, 156, 108), 0)
    cols = [MERAH, BIRU, KUNING, HIJAU, UNGU, ORANYE, PINK, (80, 150, 170)]
    rh = (h - 28) / rows
    for r in range(rows):
        by = y - 14 - r * rh
        c.line([(x - w / 2 + 14, by), (x + w / 2 - 14, by)], OUT, 4)
        xx = x - w / 2 + 24
        i = 0
        while xx < x + w / 2 - 40:
            bw = 22 + ((i + r + seed) * 7 % 3) * 7
            bh = rh * (.6 + ((i * 5 + r + seed) % 4) * .09)
            col = cols[(i * 3 + r * 5 + seed) % len(cols)]
            c.rect(xx, by - bh, xx + bw, by - 3, col, 3, OUT)
            xx += bw + 6
            i += 1


def lukisan(c, x, y, w=150, h=110, col=BIRU_MUDA):
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, KAYU, OW, OUT)
    c.rect(x - w / 2 + 12, y - h / 2 + 12, x + w / 2 - 12, y + h / 2 - 12, col, 0)
    c.poly([(x - w / 2 + 12, y + h / 2 - 12), (x - 14, y - 6), (x + 18, y + h / 2 - 12)], HIJAU, 3, OUT)
    c.ell(x + w * .2, y - h * .15, 11, 11, KUNING)


def karpet(c, x, w=620, col=PINK_MUDA, y=60):
    c.ell(x, y, w / 2, 40, col, OW, OUT)
    c.ell(x, y, w / 2 - 50, 24, None, 3, terang(col, -0.0) if False else mix(col, (255, 255, 255), .5))


def glow(c, x, y, r, col=(255, 214, 120), a=70, n=7):
    for i in range(n):
        k = 1 - i / n
        c.ell(x, y, r * (.35 + .65 * k), r * (.35 + .65 * k) * .9, col + (int(a * (1 - k) * .55 + 6),))


# ================================================================= KAMAR
def kamar_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (255, 236, 220) if wk != "malam" else (60, 72, 150))
    c.rect(X0, -300, X1, 0, mix((255, 236, 220), (240, 200, 180), .5) if wk != "malam" else (52, 62, 134))   # lis dinding bawah
    c.line([(X0, -300), (X1, -300)], OUT, 3)
    lantai(c, KAYU if wk != "malam" else (150, 112, 100), garis=KAYU_TUA if wk != "malam" else (120, 90, 90))
    jendela(c, 520, -520, 320, 300, o)
    # tirai
    c.poly([(330, -690), (400, -690), (386, -300), (330, -300)], (255, 150, 170), OW, OUT)
    c.poly([(640, -690), (710, -690), (710, -300), (654, -300)], (255, 150, 170), OW, OUT)
    # tempat tidur (kepala di kiri)
    c.rect(-640, -430, -590, 0, COKLAT, OW, OUT, r=8)
    c.rect(-640, -470, -560, -410, COKLAT, OW, OUT, r=18)
    c.rect(-600, -150, 40, -40, (236, 200, 168), OW, OUT, r=12)    # rangka
    c.rect(-596, -180, 36, -110, (250, 244, 250), OW, OUT, r=26)     # kasur
    c.rect(-596, -80, 36, 0, COKLAT, OW, OUT, r=8)
    c.rect(-560, -250, -420, -150, (250, 214, 232) if wk != "malam" else (190, 190, 240), OW, OUT, r=28)    # bantal
    # boneka kelinci
    bx, by = -290, -190
    for sg in (-1, 1):
        c.blob([(bx + sg * 12, by - 70), (bx + sg * 26, by - 130), (bx + sg * 40, by - 112), (bx + sg * 32, by - 66)], (255, 244, 238), OW * .8, OUT)
    c.ell(bx, by - 30, 50, 44, (255, 244, 238), OW * .8, OUT)
    c.ell(bx - 16, by - 34, 4, 5, OUT); c.ell(bx + 16, by - 34, 4, 5, OUT)
    c.ell(bx, by - 22, 4, 3, PINK_TUA)
    # nakas + jam digital
    c.rect(70, -170, 300, 0, COKLAT, OW, OUT, r=6)
    c.rect(78, -160, 292, -90, KAYU, 3, OUT)
    c.ell(185, -125, 6, 6, OUT)
    benda_jam(c, 185, -214, o, t)
    # rak
    c.rect(-980, -520, -760, -496, KAYU_TUA, OW, OUT, r=4)
    tanaman(c, -910, -496, .55)
    for i, col in enumerate((MERAH, BIRU, KUNING)):
        c.rect(-840 + i * 22, -586 + (i % 2) * 8, -820 + i * 22, -498, col, 3, OUT)
    lukisan(c, -250, -600, 190, 140)
    lukisan(c, 880, -600, 130, 100, (255, 214, 190))
    karpet(c, 160, 700, PINK_MUDA if wk != "malam" else (120, 110, 200), 150)
    if wk == "malam":
        glow(c, 185, -300, 260, (255, 210, 120), 90)
    tint(c, o)


def benda_jam(c, x, y, o, t):
    import benda
    benda.weker(c, benda._T(x, y, 1, 0), 1.0, t, jam=o.get("jam", "07:00"), on=bool(o.get("alarm")))


def kamar_f(c, t, o):
    # selimut menutupi badan (hanya bila ada tokoh di tempat tidur: opsi selimut)
    if o.get("selimut", True):
        col = o.get("selimut_warna", PINK)
        if o.get("selimut_warna") is None:
            col = PINK if waktu_of(o) != "malam" else (240, 150, 190)
        c.blob([(-400, -196), (-300, -224), (-120, -206), (30, -172), (54, -40), (-400, -40)], col, OW, OUT, n=7)
        c.curve([(-340, -150), (-200, -170), (-60, -146)], gelap(col, .12), 4)
    tint(c, o, True)


# ================================================================= SEKOLAH LUAR
def sekolah_luar_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    # bukit jauh
    c.set_depth(0.45)
    c.blob([(-1800, 0), (-1400, -150), (-900, -90), (-500, -190), (-100, -80), (400, -160), (900, -70), (1500, -170), (2000, 0)], mix(HIJAU_MUDA, (170, 215, 235), .45), 0)
    c.set_depth(0.8)
    pohon(c, -980, .9, HIJAU_TUA)
    pohon(c, 1300, .85, HIJAU_TUA)
    c.set_depth(1.0)
    rumput(c, warna=(150, 214, 126))
    c.poly([(-150, 0), (150, 0), (360, 420), (-360, 420)], (240, 226, 200), OW, OUT)   # jalan masuk
    # gedung
    bx = 260
    c.rect(bx - 560, -430, bx + 560, 0, (252, 238, 212), OW, OUT)
    c.poly([(bx - 600, -430), (bx + 600, -430), (bx + 520, -520), (bx - 520, -520)], (238, 124, 100), OW, OUT)
    c.rect(bx - 640, -450, bx + 640, -425, (222, 100, 84), OW, OUT)
    for sx in (-1, 1):
        for i in range(2):
            wx = bx + sx * (250 + i * 150) + (0 if sx > 0 else 0)
            c.rect(wx - 52, -340, wx + 52, -150, (178, 212, 250), OW, OUT)
            c.line([(wx, -340), (wx, -150)], OUT, 3.4)
            c.line([(wx - 52, -245), (wx + 52, -245)], OUT, 3.4)
    # pintu
    c.rect(bx - 130, -330, bx + 130, 0, (60, 110, 200), OW, OUT)
    c.line([(bx, -330), (bx, 0)], OUT, OW)
    for sx in (-1, 1):
        c.rect(bx + sx * 100 - 36 if sx < 0 else bx + 24, -290, bx + sx * 100 + 36 if sx > 0 else bx - 24, -170, (150, 196, 248), 3, OUT)
    c.rect(bx - 170, -360, bx + 170, -330, (240, 226, 196), OW, OUT)
    papan_nama(c, bx, -420, 330, 96, o.get("papan", "SMP"), (255, 226, 130), 66)
    for i in range(4):
        c.rect(bx - 190 + i * 8, -i * 14, bx + 190 - i * 8, -i * 14 + 14, (232, 224, 208), 3, OUT)
    # tiang bendera
    c.line([(-600, 0), (-600, -700)], OUT, 8)
    c.poly([(-596, -700), (-440, -700 + 10 * math.sin(t * 3)), (-440, -640 + 10 * math.sin(t * 3 + 1)), (-596, -640)], MERAH, 3.4, OUT)
    c.poly([(-596, -640), (-440, -640 + 10 * math.sin(t * 3 + 1)), (-440, -590 + 10 * math.sin(t * 3)), (-596, -590)], PUTIH, 3.4, OUT)
    semak(c, -200, 240, 100)
    semak(c, 760, 300, 110)
    tint(c, o)


def sekolah_luar_f(c, t, o):
    c.set_depth(1.25)
    semak(c, -900, 380, 190, HIJAU, y=120)
    semak(c, 1000, 380, 190, HIJAU, y=140)
    c.set_depth(1.0)
    tint(c, o, True)


def _pagar_kayu(c, x0, y0, x1, y1, n_posts=4, s=1.0):
    """Pagar kayu pedesaan Ghibli dengan tiang bertekstur, palang ganda, tali ikat & bayangan jatuh."""
    wood = (162, 118, 86)
    wood_sh = (108, 76, 62)
    wood_hl = (212, 168, 128)
    oc = (66, 48, 44)
    # bayangan jatuh lembut di tanah
    c.poly([(x0 - 12 * s, y0 + 18 * s), (x1 + 18 * s, y1 + 22 * s),
            (x1 + 36 * s, y1 + 36 * s), (x0 + 10 * s, y0 + 34 * s)], (44, 78, 56, 70))
    # palang horizontal atas & bawah
    for h_off in (-72, -36):
        c.line([(x0, y0 + h_off * s), (x1, y1 + h_off * s)], oc, 16 * s)
        c.line([(x0, y0 + h_off * s), (x1, y1 + h_off * s)], wood, 12 * s)
        c.line([(x0, y0 + (h_off - 3) * s), (x1, y1 + (h_off - 3) * s)], wood_hl, 3.5 * s)
    # tiang vertikal
    for k in range(n_posts):
        p = k / max(1, n_posts - 1)
        px, py = lerp(x0, x1, p), lerp(y0, y1, p)
        c.rect(px - 11 * s, py - 98 * s, px + 11 * s, py + 4 * s, wood, 2.2 * s, oc, r=3)
        c.rect(px + 2 * s, py - 96 * s, px + 10 * s, py + 2 * s, wood_sh)
        c.line([(px - 6 * s, py - 92 * s), (px - 6 * s, py - 4 * s)], wood_hl, 2.5 * s)


def _batu_taman(c, x, y, rx, ry):
    """Batu kali bergaya Ghibli (bayangan biru-abu bawah + highlight krem atas + rumput pangkal)."""
    base = (156, 164, 162)
    sh = (96, 110, 118)
    hl = (216, 218, 206)
    oc = (62, 72, 74)
    pts = [(x - rx, y + ry * 0.25), (x - rx * 0.78, y - ry * 0.62), (x - rx * 0.12, y - ry),
           (x + rx * 0.65, y - ry * 0.72), (x + rx, y + ry * 0.15), (x + rx * 0.55, y + ry * 0.42),
           (x - rx * 0.58, y + ry * 0.42)]
    c.ell(x + rx * 0.18, y + ry * 0.36, rx * 1.05, ry * 0.34, (36, 68, 52, 65))
    c.blob(pts, sh, 2.2, oc, n=5)
    c.blob([(x - rx * 0.85, y - ry * 0.05), (x - rx * 0.65, y - ry * 0.60), (x - rx * 0.08, y - ry * 0.94),
            (x + rx * 0.54, y - ry * 0.64), (x + rx * 0.45, y - ry * 0.02), (x - rx * 0.35, y + ry * 0.08)], base, 0, n=5)
    c.ell(x - rx * 0.24, y - ry * 0.55, rx * 0.36, ry * 0.22, hl)


def _jalan_setapak_ghibli(c, y_top=0, y_bot=460):
    """Jalan tanah berliku Ghibli tanpa outline hitam kaku, dengan cast shadow, batu pinggir & rumput melingkup."""
    sand = (232, 204, 158)
    sand_hl = (248, 232, 194)
    sand_sh = (182, 146, 114)
    # kurva S lembut jalan tanah melebar ke depan kamera
    left_pts, right_pts = [], []
    steps = 16
    for i in range(steps + 1):
        p = i / steps
        yy = lerp(y_top, y_bot, p)
        cx = math.sin(p * math.pi * 1.15) * 95.0 - 24.0 * p
        hw = lerp(68.0, 255.0, p ** 1.15)
        left_pts.append((cx - hw, yy))
        right_pts.append((cx + hw, yy))
    path_pts = left_pts + list(reversed(right_pts))
    c.poly(path_pts, sand)
    # sapuan terang di tengah jalan tanah
    mid_l = [(lerp(l[0], r[0], 0.22), l[1]) for l, r in zip(left_pts, right_pts)]
    mid_r = [(lerp(l[0], r[0], 0.76), l[1]) for l, r in zip(left_pts, right_pts)]
    c.poly(mid_l + list(reversed(mid_r)), sand_hl)
    # bayangan pohon/pagar menyilang diagonal di atas jalan tanah (cast shadows khas Ghibli!)
    for sy, sh_h in ((58, 34), (175, 48), (310, 60)):
        p = clamp((sy - y_top) / max(1, y_bot - y_top))
        cx = math.sin(p * math.pi * 1.15) * 95.0 - 24.0 * p
        hw = lerp(68.0, 255.0, p ** 1.15)
        c.ell(cx + 12, sy, hw * 0.92, sh_h * 0.55, (112, 104, 128, 62))
    # kerikil kecil & jejak tanah organik
    rng = random.Random(42)
    for _ in range(28):
        p = rng.uniform(0.05, 0.95)
        yy = lerp(y_top, y_bot, p)
        cx = math.sin(p * math.pi * 1.15) * 95.0 - 24.0 * p
        hw = lerp(68.0, 255.0, p ** 1.15)
        px = cx + rng.uniform(-hw * 0.85, hw * 0.85)
        c.ell(px, yy, rng.uniform(5, 16) * (0.6 + p), rng.uniform(2.5, 6) * (0.6 + p), sand_sh + (120,))
    # rumput-rumput melingkup menutupi tepi kiri & kanan jalan tanah (tidak ada garis potong lurus!)
    for i in range(0, steps + 1, 1):
        lx, ly = left_pts[i]
        rx, ry = right_pts[i]
        sc = 0.65 + (i / steps) * 0.75
        _rumpun_ghibli(c, lx - 6 * sc, ly + 4, sc, (64, 128, 68), (38, 86, 56), (176, 214, 102), 2.0)
        _rumpun_ghibli(c, rx + 6 * sc, ry + 4, sc, (64, 128, 68), (38, 86, 56), (176, 214, 102), 2.0)


# ================================================================= TAMAN
def taman_b(c, t, o):
    langit(c, o, t=t)
    awan_set(c, o, t=t)
    bukit_berlapis(c, o, 0)
    c.set_depth(0.72)
    for i, (x, g) in enumerate(((-1420, "cemara"), (-780, "rimbun"), (640, "cemara"), (1360, "gugur"))):
        pohon(c, x, .86 + (i % 2) * .12, HIJAU_TUA if i % 2 else HIJAU, gaya=g, t=t)
    c.set_depth(1.0)
    rumput(c, warna=(142, 210, 120), t=t)
    _jalan_setapak_ghibli(c, 0, 440)
    # rumah pedesaan Jepang (Minka Ghibli) di kanan-belakang
    rumah(c, 560, 320, 215, (250, 242, 224), (212, 102, 84), gaya="jepang", t=t)
    pohon(c, -470, 1.14, HIJAU, gaya="rimbun", t=t)
    pohon(c, 880, 1.04, (118, 196, 100), gaya="sakura", t=t)
    # pagar kayu pedesaan & batu kali di tepi jalan
    _pagar_kayu(c, -740, 125, -245, 78, n_posts=4, s=0.95)
    _batu_taman(c, 280, 82, 46, 28)
    _batu_taman(c, 336, 96, 30, 19)
    # taman bunga detail organik di dekat pagar & batu (menyatu dengan rumput!)
    bunga_set = [
        (-280, 102, 0.85, PUTIH, "daisy"), (-335, 122, 0.92, (164, 208, 252), "daisy"),
        (-410, 118, 0.88, KUNING, "tulip"), (-475, 138, 0.95, PINK, "daisy"),
        (260, 112, 0.86, KUNING, "daisy"), (318, 126, 0.92, PUTIH, "daisy"),
        (385, 110, 0.84, (168, 210, 252), "daisy"),
    ]
    for fx, fy, fs, fc, fj in bunga_set:
        bunga_detail(c, fx, fy, fs, fc, fj, t=t)
    semak(c, -860, 320, 115)
    semak(c, 420, 240, 95, HIJAU)
    tint(c, o)


def taman_f(c, t, o):
    # foreground framing bawah: rumput & bunga rimbun dekat lensa (tanpa daun melayang di langit)
    c.set_depth(1.28)
    for gx, gy, sc in ((-960, 260, 1.55), (-820, 278, 1.45), (-680, 290, 1.30),
                       (940, 265, 1.55), (790, 282, 1.40), (660, 295, 1.25)):
        _rumpun_ghibli(c, gx, gy, sc, (48, 106, 60), (26, 68, 48), (168, 212, 98), math.sin(t * 2.0) * 5.0)
    for fx, fy, fc in ((-860, 252, PUTIH), (-770, 268, KUNING), (-710, 260, PINK),
                       (840, 258, (172, 214, 255)), (750, 272, PUTIH)):
        bunga_detail(c, fx, fy, 1.08, fc, "daisy", t=t)
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= KELAS
def kelas_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (255, 247, 226))
    c.rect(X0, -260, X1, 0, (244, 226, 190), 0)
    c.line([(X0, -260), (X1, -260)], OUT, 3)
    lantai(c, (226, 190, 150), garis=(200, 160, 120))
    # papan tulis
    c.rect(-520, -620, 220, -240, (190, 140, 96), OW * 1.3, OUT, r=8)
    c.rect(-500, -600, 200, -260, (52, 112, 96), OW, OUT)
    tx = o.get("papan_tulis", "")
    if tx:
        c.text(-150, -430, tx, 62, (240, 248, 240), "bulat")
    else:
        for i, (w, y) in enumerate(((300, -540), (420, -490), (240, -440), (380, -390))):
            c.curve([(-460, y), (-460 + w * .5, y - 8), (-460 + w, y + 4)], (236, 244, 236), 5)
        c.curve([(-70, -340), (-20, -330), (40, -344)], (255, 226, 130), 5)
    c.rect(-480, -250, 180, -232, (150, 100, 64), OW, OUT)
    c.rect(-100, -262, -30, -244, (240, 240, 240), 3, OUT)
    # jendela kanan
    jendela(c, 620, -480, 320, 300, o)
    jendela(c, 1100, -480, 280, 300, o)
    # jam dinding
    c.ell(-760, -620, 56, 56, PUTIH, OW, OUT)
    ang = (t * 0.2) % (2 * math.pi)
    c.line([(-760, -620), (-760 + math.sin(ang) * 36, -620 - math.cos(ang) * 36)], OUT, 4)
    c.line([(-760, -620), (-760 + 28, -620 + 6)], OUT, 5)
    # poster
    lukisan(c, -900, -450, 120, 150, (200, 230, 255))
    # meja guru
    c.rect(300, -190, 700, -164, COKLAT, OW, OUT, r=4)
    c.rect(318, -164, 682, 0, KAYU, OW, OUT)
    tanaman(c, 380, -190, .42)
    tint(c, o)


def kelas_f(c, t, o):
    # barisan meja siswa di depan
    if o.get("meja_depan", True):
        c.set_depth(1.15)
        for x in (-860, 900):
            c.rect(x - 150, 150, x + 150, 190, KAYU, OW, OUT, r=4)
            c.rect(x - 120, 190, x - 100, 330, (90, 96, 116), OW, OUT)
            c.rect(x + 100, 190, x + 120, 330, (90, 96, 116), OW, OUT)
        c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= RUANG BELAJAR
def ruang_belajar_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (255, 232, 202) if wk != "malam" else (86, 76, 120))
    lantai(c, KAYU, garis=KAYU_TUA)
    rak_buku(c, -640, 0, 360, 760, 5)
    jendela(c, 700, -560, 280, 300, o)
    # papan gabus + sticky notes
    c.rect(-100, -740, 360, -480, (206, 150, 96), OW, OUT, r=6)
    for i, (x, y, col) in enumerate(((-60, -700, KUNING_MUDA), (50, -690, PINK_MUDA), (160, -706, BIRU_MUDA), (270, -690, HIJAU_MUDA), (-20, -580, PINK_MUDA), (150, -590, KUNING_MUDA), (270, -560, BIRU_MUDA))):
        c.rect(x - 38, y - 36, x + 38, y + 36, col, 3, OUT)
        c.line([(x - 22, y - 12), (x + 22, y - 12)], ABU_TUA, 3, False)
        c.line([(x - 22, y + 8), (x + 10, y + 8)], ABU_TUA, 3, False)
    # kursi (sandaran di belakang tokoh)
    kx = o.get("kursi_x", 230)
    c.rect(kx - 80, -340, kx + 80, -120, (96, 102, 140), OW, OUT, r=18)
    c.line([(kx, -120), (kx, 0)], OUT, 12)
    # lampu meja
    lx = o.get("lampu_x", 560)
    c.line([(lx, -132), (lx - 10, -250), (lx + 70, -340)], (60, 66, 96), 11)
    c.poly([(lx + 40, -350), (lx + 130, -330), (lx + 100, -288), (lx + 24, -308)], (46, 52, 86), OW, OUT)
    if wk == "malam" or o.get("lampu_nyala", True):
        glow(c, lx + 80, -290, 340, (255, 220, 140), 120)
    tint(c, o)
    if wk == "malam" or o.get("lampu_nyala", True):
        glow(c, lx + 80, -290, 380, (255, 214, 130), 70)


def ruang_belajar_f(c, t, o):
    # meja di depan tokoh (permukaan y=-132)
    c.rect(-60, -134, 760, -102, KAYU, OW, OUT, r=6)
    c.rect(-40, -102, 740, 0, (214, 160, 108), OW, OUT)
    c.rect(150, -102, 430, -30, (196, 142, 96), OW, OUT)
    c.ell(290, -66, 8, 8, OUT)
    for i, (w, col) in enumerate(((190, BIRU), (170, MERAH), (150, HIJAU))):
        c.rect(590 - w / 2, -134 - (i + 1) * 30, 590 + w / 2 + (i % 2) * 10, -134 - i * 30, col, OW * .8, OUT, r=3)
    c.rect(-20, -200, 40, -134, PINK, OW, OUT, r=8)
    for i, col in enumerate((BIRU, KUNING, MERAH)):
        c.line([(-10 + i * 18, -200), (-16 + i * 22, -252)], col, 8)
    tint(c, o, True)


# ================================================================= RUANG TAMU
def ruang_tamu_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (224, 238, 250) if wk != "malam" else (70, 84, 150))
    c.rect(X0, -240, X1, 0, (206, 224, 242) if wk != "malam" else (60, 72, 136), 0)
    c.line([(X0, -240), (X1, -240)], OUT, 3)
    lantai(c, (232, 196, 158), garis=(208, 170, 132))
    karpet(c, -120, 900, (255, 186, 190), 190)
    # sofa
    sx = o.get("sofa_x", -200)
    sc = (118, 142, 214)
    c.rect(sx - 330, -330, sx + 330, -90, gelap(sc, .08), OW, OUT, r=48)
    c.rect(sx - 380, -210, sx - 300, 0, sc, OW, OUT, r=30)
    c.rect(sx + 300, -210, sx + 380, 0, sc, OW, OUT, r=30)
    c.rect(sx - 300, -100, sx + 300, 0, terang(sc, .12), OW, OUT, r=26)
    c.line([(sx, -100), (sx, -16)], OUT, 3)
    c.rect(sx - 280, -310, sx - 170, -190, PINK, OW, OUT, r=22)
    c.rect(sx + 170, -300, sx + 280, -190, KUNING, OW, OUT, r=22)
    # kucing oranye di kanan
    kx, ky = sx + 340, -212
    c.ell(kx, ky - 30, 70, 38, ORANYE, OW, OUT)
    c.ell(kx - 54, ky - 54, 34, 30, ORANYE, OW, OUT)
    for sg in (-1, 1):
        c.poly([(kx - 54 + sg * 12, ky - 76), (kx - 54 + sg * 30, ky - 100), (kx - 54 + sg * 32, ky - 70)], ORANYE, 3, OUT)
    c.line([(kx - 64, ky - 54), (kx - 58, ky - 52)], OUT, 3); c.line([(kx - 48, ky - 54), (kx - 42, ky - 52)], OUT, 3)
    c.curve([(kx + 66, ky - 26), (kx + 112, ky - 34 + 10 * math.sin(t * 2.4)), (kx + 130, ky - 70 + 14 * math.sin(t * 2.4))], ORANYE, 12)
    # TV & tanaman
    c.rect(560, -420, 1000, -170, (40, 44, 60), OW, OUT, r=10)
    c.rect(576, -404, 984, -186, (120, 196, 250) if wk != "malam" else (140, 160, 250), 0)
    c.rect(520, -170, 1040, 0, KAYU, OW, OUT)
    tanaman(c, -760, 0, 1.2, PINK_TUA)
    jendela(c, -760, -560, 260, 260, o) if False else lukisan(c, -700, -520, 220, 150, (255, 214, 190))
    lukisan(c, 240, -560, 240, 160)
    tint(c, o)


def ruang_tamu_f(c, t, o):
    tint(c, o, True)


# ================================================================= JALAN KAMPUNG / KOMPLEK
def rumah(c, x, w=360, h=280, tembok=(250, 238, 216), atap=(212, 102, 84), gaya=None, t=0.0):
    """Rumah detail bergaya anime Jepang / Ghibli ('jepang' Minka atau 'cottage' pondok cerobong asap)."""
    if gaya is None:
        gaya = "jepang" if int(abs(x)) % 2 == 0 else "cottage"
    far = getattr(c, "depth", 1.0) < 0.85
    fog = (182, 212, 232)
    tc = mix(tembok, fog, 0.25) if far else tembok
    ac = mix(atap, fog, 0.25) if far else atap
    wood = mix((136, 98, 72), fog, 0.24) if far else (136, 98, 72)
    wood_d = gelap(wood, 0.28)
    wood_l = terang(wood, 0.18)
    oc = mix((58, 48, 44), fog, 0.45) if far else (58, 48, 44)
    ow_r = OW * (0.48 if far else 0.65)
    # bayangan jatuh rumah ke tanah
    c.ell(x + w * 0.08, 6, w * 0.62, 18, (28, 56, 46, 42 if far else 64))

    if gaya == "cottage":
        # PONDOK GHIBLI (gambar 1): dinding krem + batu sudut + gable kayu silang + cerobong asap + sayap samping
        # sayap teras/gudang kecil di kiri
        sx0, sx1 = x - w * 0.64, x - w * 0.44
        c.rect(sx0, -h * 0.56, sx1, 0, gelap(wood, 0.08), ow_r, oc)
        c.poly([(sx0 - 12, -h * 0.54), (sx1 + 4, -h * 0.72), (sx1 + 4, -h * 0.62), (sx0 - 12, -h * 0.46)], gelap(ac, 0.12), ow_r, oc)
        c.rect(sx0 + 12, -h * 0.36, sx1 - 6, 0, (56, 46, 42))
        # badan utama pondok + shading kanan
        c.rect(x - w * 0.46, -h * 0.76, x + w * 0.46, 0, tc, ow_r, oc)
        c.rect(x + w * 0.18, -h * 0.76, x + w * 0.46 - 2, -2, gelap(tc, 0.13))
        # tekstur batu sudut kiri & kanan
        stone_c = mix((168, 162, 148), fog, 0.25) if far else (168, 162, 148)
        for k in range(5):
            sy = -k * (h * 0.14) - 10
            sw_ = 16 + (k % 2) * 8
            c.rect(x - w * 0.46, sy - 14, x - w * 0.46 + sw_, sy, stone_c, ow_r * .5, oc, r=2)
            c.rect(x + w * 0.46 - sw_, sy - 14, x + w * 0.46, sy, gelap(stone_c, 0.14), ow_r * .5, oc, r=2)
        # cerobong batu + asap putih lembut mengepul ke langit
        ch_x = x + w * 0.26
        ch_top = -h * 1.38
        c.rect(ch_x - 16, ch_top, ch_x + 16, -h * 0.92, stone_c, ow_r, oc)
        c.rect(ch_x - 20, ch_top - 8, ch_x + 20, ch_top + 4, gelap(stone_c, 0.16), ow_r * .8, oc, r=2)
        for si in range(5):
            sp = (si + (t * 0.45 % 1.0)) / 5.0
            smx = ch_x + sp * 78 + math.sin(t * 1.8 + si) * 10
            smy = ch_top - 14 - sp * 95
            sr = 10 + sp * 26
            c.ell(smx, smy, sr, sr * 0.78, (255, 253, 248, int(130 * (1.0 - sp))))
        # atap pelana tinggi + segitiga gable kayu silang (half-timber)
        peak_y = -h * 1.32
        eave_y = -h * 0.74
        c.poly([(x - w * 0.56, eave_y + 10), (x, peak_y), (x + w * 0.56, eave_y + 10),
                (x + w * 0.50, eave_y + 22), (x, peak_y + 18), (x - w * 0.50, eave_y + 22)], wood_d, ow_r, oc)
        roof_poly = [(x - w * 0.56, eave_y + 4), (x, peak_y - 8), (x + w * 0.56, eave_y + 4),
                     (x + w * 0.52, eave_y + 14), (x, peak_y + 8), (x - w * 0.52, eave_y + 14)]
        c.poly(roof_poly, ac, ow_r, oc)
        # segitiga dinding gable + rangka kayu silang
        gable = [(x - w * 0.42, eave_y + 4), (x, peak_y + 14), (x + w * 0.42, eave_y + 4)]
        c.poly(gable, tc, ow_r * .8, oc)
        c.line([(x - w * 0.42, eave_y + 4), (x + w * 0.42, eave_y + 4)], wood, 6)
        c.line([(x, peak_y + 14), (x, eave_y + 4)], wood, 5)
        c.line([(x - w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48)), (x + w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48))], wood, 4.5)
        c.line([(x - w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48)), (x - w * 0.34, eave_y + 4)], wood, 4.0)
        c.line([(x + w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48)), (x + w * 0.34, eave_y + 4)], wood, 4.0)
        # jendela loteng kecil
        c.rect(x - 13, peak_y + 34, x + 13, peak_y + 62, (148, 194, 224), ow_r * .7, oc, r=3)
        c.line([(x, peak_y + 34), (x, peak_y + 62)], wood_d, 2.0)
        # bayangan atap jatuh di dinding
        c.rect(x - w * 0.45, eave_y + 4, x + w * 0.45, eave_y + 22, (58, 52, 68, 58))
        # pintu kayu melengkung + kanopi kecil
        dw, dh = w * 0.11, h * 0.52
        c.rect(x - dw, -dh, x + dw, 0, wood, ow_r, oc, r=4)
        c.line([(x - dw * 0.35, -dh + 4), (x - dw * 0.35, -2)], wood_d, 2.0)
        c.line([(x + dw * 0.35, -dh + 4), (x + dw * 0.35, -2)], wood_d, 2.0)
        c.rect(x - dw - 8, -dh - 10, x + dw + 8, -dh, wood_d, ow_r * .7, oc, r=2)
        c.ell(x + dw * 0.6, -dh * 0.48, 3.8, 3.8, KUNING)
        # jendela berkisi-kisi (4 panel) + bunga kecil di bawahnya
        for jx in (x - w * 0.28, x + w * 0.28):
            jw, jy0, jy1 = w * 0.11, -h * 0.56, -h * 0.30
            c.rect(jx - jw, jy0, jx + jw, jy1, (142, 190, 218), ow_r * .8, oc, r=3)
            c.poly([(jx - jw + 4, jy1 - 3), (jx - jw + 14, jy1 - 3), (jx + jw - 4, jy0 + 3), (jx + jw - 14, jy0 + 3)], (255, 255, 255, 70))
            c.line([(jx, jy0), (jx, jy1)], wood_d, 2.4)
            c.line([(jx - jw, (jy0 + jy1) / 2), (jx + jw, (jy0 + jy1) / 2)], wood_d, 2.4)
            c.rect(jx - jw - 4, jy1, jx + jw + 4, jy1 + 8, wood, ow_r * .6, oc, r=2)
        return

    # RUMAH PEDESAAN JEPANG / MINKA GHIBLI (seperti gambar 3):
    # pondasi batu kali + beranda kayu (engawa) + dinding 2 lapis (kayu bawah + plester atas) + pintu geser shoji + atap pelana lebar
    base_h = h * 0.14
    # pondasi batu kali di bawah rumah
    c.rect(x - w * 0.48, -base_h, x + w * 0.48, 0, (132, 138, 140), ow_r * .8, oc)
    for k in range(8):
        bx = x - w * 0.44 + k * (w * 0.118)
        c.ell(bx, -base_h * 0.5 + (k % 2) * 3, w * 0.06, base_h * 0.48, (164, 170, 168) if k % 2 == 0 else (112, 120, 126), ow_r * .45, oc)
    # dinding utama: plester putih-krem atas + papan kayu vertikal bawah
    wall_top = -h * 0.78
    mid_y = -h * 0.42
    c.rect(x - w * 0.47, wall_top, x + w * 0.47, -base_h, tc, ow_r, oc)
    c.rect(x - w * 0.47, mid_y, x + w * 0.47, -base_h, wood_l, ow_r * .7, oc)
    # garis papan kayu vertikal
    for k in range(1, 14):
        vx = x - w * 0.47 + k * (w * 0.94 / 14)
        c.line([(vx, mid_y), (vx, -base_h)], gelap(wood_l, 0.18), 1.6)
    # bayangan dalam atap (deep eaves shadow khas anime Jepang!)
    c.rect(x - w * 0.47, wall_top, x + w * 0.47, wall_top + h * 0.18, (46, 52, 72, 85))
    # rangka balok kayu tradisional (tiang kiri, tengah, kanan + balok horizontal)
    for tx in (x - w * 0.46, x - w * 0.14, x + w * 0.18, x + w * 0.46):
        c.rect(tx - 4.5, wall_top, tx + 4.5, -base_h, wood_d)
    c.rect(x - w * 0.48, mid_y - 4, x + w * 0.48, mid_y + 4, wood_d)
    # pintu geser shoji (kisi-kisi kertas putih hangat & kaca)
    sh_x0, sh_x1 = x - w * 0.42, x + w * 0.14
    sh_y0, sh_y1 = -h * 0.62, -base_h - 10
    c.rect(sh_x0, sh_y0, sh_x1, sh_y1, (238, 240, 236), ow_r * .8, wood_d)
    # kaca pantulan di panel kiri
    c.rect(sh_x0 + 4, sh_y0 + 4, lerp(sh_x0, sh_x1, 0.48), sh_y1 - 4, (132, 168, 192))
    # kisi-kisi kayu vertikal & horizontal halus
    for k in range(1, 7):
        kx = lerp(sh_x0, sh_x1, k / 7.0)
        c.line([(kx, sh_y0), (kx, sh_y1)], wood_d, 2.0)
    for k in range(1, 4):
        ky = lerp(sh_y0, sh_y1, k / 4.0)
        c.line([(sh_x0, ky), (sh_x1, ky)], wood_d, 1.8)
    # beranda kayu (engawa) menonjol di depan pintu + anak tangga
    c.rect(x - w * 0.50, -base_h - 10, x + w * 0.50, -base_h + 2, wood_l, ow_r * .8, oc, r=2)
    c.rect(x - w * 0.50, -base_h + 2, x + w * 0.50, -base_h + 8, wood_d)
    # atap genteng Jepang lebar dengan sudut overhang menonjol & garis genteng rapat
    rh = h * 0.46
    roof_pts = [(x - w * 0.60, wall_top + 10), (x + w * 0.60, wall_top + 10),
                (x + w * 0.36, wall_top - rh), (x - w * 0.36, wall_top - rh)]
    # bayangan kasau bawah atap
    c.poly([(x - w * 0.58, wall_top + 18), (x + w * 0.58, wall_top + 18),
            (x + w * 0.60, wall_top + 8), (x - w * 0.60, wall_top + 8)], wood_d, ow_r * .7, oc)
    c.poly(roof_pts, ac, ow_r, oc)
    # cel shadow sisi kanan atap + garis-garis genteng horizontal & vertikal halus
    c.poly([(x + w * 0.14, wall_top + 10), (x + w * 0.59, wall_top + 10),
            (x + w * 0.35, wall_top - rh + 2), (x + w * 0.08, wall_top - rh + 2)], gelap(ac, 0.18))
    for k in range(1, 5):
        p = k / 5.0
        gy = lerp(wall_top + 10, wall_top - rh, p)
        gx0 = lerp(x - w * 0.59, x - w * 0.36, p)
        gx1 = lerp(x + w * 0.59, x + w * 0.36, p)
        c.line([(gx0, gy), (gx1, gy)], gelap(ac, 0.24), 1.8)
    for k in range(1, 9):
        p = k / 9.0
        c.line([(lerp(x - w * 0.58, x + w * 0.58, p), wall_top + 10),
                (lerp(x - w * 0.35, x + w * 0.35, p), wall_top - rh)], gelap(ac, 0.18), 1.5)
    # bubungan atap tebal di puncak
    c.rect(x - w * 0.38, wall_top - rh - 10, x + w * 0.38, wall_top - rh + 4, gelap(ac, 0.28), ow_r * .8, oc, r=3)
    c.poly(roof_pts, None, ow_r, oc)


def ruko_kafe(c, x, w=340, h=320, tembok=(228, 236, 238), awning=(48, 146, 98)):
    """Toko/ruko Jepang 2 lantai bergaya Ghibli (gambar 4): genteng kawara, jendela kayu berkisi, AC, kanopi kain & etalase."""
    far = getattr(c, "depth", 1.0) < 0.85
    fog = (182, 212, 232)
    tc = mix(tembok, fog, 0.25) if far else tembok
    ac = mix(awning, fog, 0.25) if far else awning
    wood = mix((168, 112, 68), fog, 0.25) if far else (168, 112, 68)
    oc = mix((52, 48, 46), fog, 0.50) if far else (52, 48, 46)
    ow_r = OW * (0.48 if far else 0.72)
    c.rect(x - w / 2, -h, x + w / 2, 0, tc, ow_r, oc)
    c.rect(x + w * 0.26, -h + 2, x + w / 2 - 2, -2, gelap(tc, 0.10))
    # bayangan lembut di bawah atap
    c.rect(x - w / 2 + 2, -h + 2, x + w / 2 - 2, -h + 26, (54, 68, 80, 65))
    # atap genteng lengkung Jepang (kawara)
    tile_c = mix((96, 152, 158), fog, 0.25) if far else (96, 152, 158)
    c.rect(x - w / 2 - 14, -h - 26, x + w / 2 + 14, -h, tile_c, ow_r, oc, r=4)
    for k in range(11):
        kx = x - w / 2 - 8 + k * ((w + 16) / 11)
        c.ell(kx + 12, -h - 3, 14, 7, gelap(tile_c, 0.22), ow_r * .5, oc)
    # 2 jendela kayu berkisi di lantai 2 + penutup jendela kayu samping
    for jx in (x - w * 0.22, x + w * 0.18):
        c.rect(jx - 48, -h + 36, jx + 48, -h + 114, (116, 168, 188), ow_r * .8, oc, r=3)
        c.rect(jx - 48, -h + 36, jx + 48, -h + 52, (46, 78, 96, 70))
        for k in range(1, 4):
            kx = lerp(jx - 48, jx + 48, k / 4.0)
            c.line([(kx, -h + 36), (kx, -h + 114)], wood, 3.0)
        c.rect(jx - 52, -h + 32, jx + 52, -h + 40, wood, ow_r * .6, oc)
        c.rect(jx - 52, -h + 112, jx + 52, -h + 120, wood, ow_r * .6, oc)
    # 2 unit AC outdoor kecil di bawah jendela (detail ikonik toko Jepang!)
    for ax in (x - w * 0.34, x + w * 0.32):
        c.rect(ax - 22, -196, ax + 22, -166, (226, 224, 214), ow_r * .7, oc, r=3)
        c.ell(ax - 5, -181, 10, 10, (92, 98, 102), ow_r * .5, oc)
    # kanopi kain (awning) hijau bergelombang + lipatan bayangan
    aw_y0, aw_y1 = -164, -122
    c.poly([(x - w / 2 - 8, aw_y0), (x + w / 2 + 8, aw_y0), (x + w / 2 + 14, aw_y1), (x - w / 2 - 14, aw_y1)], ac, ow_r, oc)
    for k in range(1, 8):
        kx = lerp(x - w / 2 - 6, x + w / 2 + 6, k / 8.0)
        c.line([(kx, aw_y0 + 2), (kx + (kx - x) * 0.04, aw_y1 - 2)], gelap(ac, 0.22), 2.2)
    c.rect(x - w / 2 - 12, aw_y1, x + w / 2 + 12, aw_y1 + 10, gelap(ac, 0.20), ow_r * .6, oc)
    # etalase toko hangat di lantai 1 + rak warna-warni + pintu kayu
    c.rect(x - w / 2 + 18, -110, x + w / 2 - 18, 0, (62, 68, 78), ow_r * .8, oc)
    for ry, rc in ((-88, (238, 186, 86)), (-58, (132, 188, 114)), (-30, (236, 134, 88))):
        c.rect(x - w / 2 + 26, ry, x - 10, ry + 18, rc, ow_r * .4, oc, r=2)
    c.rect(x + 18, -104, x + w / 2 - 26, 0, wood, ow_r * .8, oc)
    c.rect(x + 28, -94, x + w / 2 - 36, -44, (242, 224, 184), ow_r * .5, oc)


def jalan_b(c, t, o):
    langit(c, o, t=t)
    awan_set(c, o, 8, t=t)
    bukit_berlapis(c, o, 0)
    c.set_depth(0.72)
    x0, x1, _, _ = c.visible(500)
    per = 640
    for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
        mod = abs(i) % 4
        if mod == 0:
            gaya_p = ("rimbun", "palem", "sakura", "cemara", "gugur", "beringin")[abs(i) % 6]
            pohon(c, i * per + 110, .82 + (abs(i) % 3) * .08, HIJAU if i % 4 else HIJAU_TUA, gaya=gaya_p, t=t)
        elif mod == 2:
            ruko_kafe(c, i * per, 330, 310, [(248, 234, 212), (222, 238, 246), (252, 224, 218)][abs(i) % 3],
                      [(218, 86, 76), (62, 148, 134), (226, 152, 68)][abs(i) % 3])
        else:
            rumah(c, i * per, 340, 235, [(255, 232, 200), (212, 236, 250), (255, 214, 214), (226, 244, 214)][i % 4], [(236, 120, 96), (120, 150, 210), (220, 150, 90)][i % 3])
    c.set_depth(1.0)
    # trotoar + jalan
    c.rect(X0, 0, X1, 120, (218, 216, 212), OW, OUT)
    c.rect(X0, 102, X1, 120, (186, 184, 180))   # bibir trotoar
    c.rect(X0, 120, X1, 1400, (92, 96, 112))
    c.line([(X0, 120), (X1, 120)], OUT, OW)
    x0, x1, _, _ = c.visible(300)
    for i in range(int(math.floor(x0 / 180)) - 1, int(math.ceil(x1 / 180)) + 2):
        c.line([(i * 180, 0), (i * 180 - 24, 120)], (188, 186, 182), 3)
    for i in range(int(math.floor(x0 / 320)) - 1, int(math.ceil(x1 / 320)) + 2):
        c.rect(i * 320, 325, i * 320 + 190, 346, (250, 246, 224), 0)
    # tiang lampu jalan
    per = 1050
    for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
        px = i * per + 420
        c.rect(px - 7, -420, px + 7, 0, (70, 76, 96), OW * .8, OUT)
        c.line([(px, -420), (px + 70, -440)], (70, 76, 96), 9)
        c.ell(px + 76, -436, 20, 14, (255, 236, 150), 3, OUT)
        if waktu_of(o) == "malam":
            glow(c, px + 76, -420, 260, (255, 226, 130), 110)
    tint(c, o)


def jalan_f(c, t, o):
    # foreground parallax: siluet semak/tiang lembut di pinggir bawah dekat lensa (kedalaman 2D sinematik)
    c.set_depth(1.38)
    x0, x1, _, _ = c.visible(600)
    per = 1500
    for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
        fx = i * per + 650
        c.ell(fx, 240, 180, 95, (48, 72, 62, 165))
        c.ell(fx + 95, 255, 130, 80, (38, 60, 52, 150))
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= KANTIN
def kantin_b(c, t, o):
    dinding(c, (255, 240, 214))
    lantai(c, (214, 200, 180), garis=(190, 176, 156))
    # kios dengan atap garis-garis
    c.rect(-300, -380, 700, -40, (255, 226, 160), OW, OUT)
    c.rect(-340, -120, 740, -80, KAYU_TUA, OW, OUT)
    c.rect(-340, -80, 740, 0, COKLAT, OW, OUT)
    for i in range(10):
        col = MERAH if i % 2 == 0 else PUTIH
        x = -340 + i * 108
        c.poly([(x, -470), (x + 108, -470), (x + 120, -380), (x - 12, -380)], col, OW * .8, OUT)
    papan_nama(c, 200, -520, 360, 70, o.get("papan", "KANTIN"), (255, 255, 255), 48)
    # menu & makanan
    for i, (x, col) in enumerate(((-180, ORANYE), (20, KUNING), (220, PINK), (420, HIJAU_MUDA))):
        c.ell(x, -150, 70, 22, PUTIH, OW * .8, OUT)
        c.blob([(x - 52, -160), (x, -210), (x + 52, -160)], col, OW * .8, OUT)
    # meja + bangku
    for tx in (-980, 1000):
        c.rect(tx - 170, -180, tx + 170, -150, KAYU, OW, OUT, r=4)
        c.rect(tx - 10, -150, tx + 10, 0, (90, 96, 116), OW, OUT)
        for sg in (-1, 1):
            c.rect(tx + sg * 190 - 50, -90, tx + sg * 190 + 50, -66, COKLAT, OW, OUT, r=4)
            c.rect(tx + sg * 190 - 6, -66, tx + sg * 190 + 6, 0, (90, 96, 116), OW * .8, OUT)
    tint(c, o)


def kantin_f(c, t, o):
    tint(c, o, True)


# ================================================================= LAPANGAN
def lapangan_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    c.set_depth(0.5)
    c.rect(-2400, -120, 2400, 0, (170, 190, 170), 0)
    for i in range(-14, 15):
        c.rect(i * 160 - 4, -120, i * 160 + 4, 0, (110, 130, 120), 0)
    c.set_depth(0.7)
    for i, x in enumerate((-1400, -500, 900, 1700)):
        pohon(c, x, .7 + (i % 2) * .1, HIJAU_TUA)
    c.set_depth(1.0)
    c.rect(X0, 0, X1, 1400, (118, 200, 108))
    for i in range(-8, 9):
        if i % 2 == 0:
            c.rect(i * 260, 0, i * 260 + 260, 1400, (108, 190, 98), 0)
    c.line([(X0, 0), (X1, 0)], OUT, OW)
    c.line([(-1600, 260), (1600, 260)], PUTIH, 8)
    c.ell(0, 260, 220, 90, None, 8, PUTIH)
    # gawang
    for gx, sg in ((-1050, 1), (1050, -1)):
        c.line([(gx, 0), (gx, -250)], PUTIH, 12)
        c.line([(gx, -250), (gx + sg * 150, -230), (gx + sg * 150, 0)], PUTIH, 10)
        for i in range(1, 6):
            c.line([(gx + sg * 150 * i / 6, -240 + 10 * i / 6), (gx + sg * 150 * i / 6, 0)], (255, 255, 255, 130), 3, False)
    tint(c, o)


def lapangan_f(c, t, o):
    tint(c, o, True)


# ================================================================= RUMAH DEPAN
def rumah_depan_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    c.set_depth(0.75)
    pohon(c, -1100, .9, HIJAU_TUA)
    pohon(c, 1250, .8, HIJAU)
    c.set_depth(1.0)
    rumput(c, warna=(150, 214, 126))
    rumah(c, 0, 900, 380, (255, 236, 206), (232, 112, 92))
    c.rect(-72, -250, 72, 0, (168, 112, 70), OW, OUT)
    c.ell(46, -120, 7, 7, KUNING, 3, OUT)
    c.rect(-380, -300, -230, -170, (178, 212, 250), OW, OUT)
    c.rect(230, -300, 380, -170, (178, 212, 250), OW, OUT)
    c.line([(-305, -300), (-305, -170)], OUT, 3.4); c.line([(305, -300), (305, -170)], OUT, 3.4)
    c.poly([(-120, 0), (120, 0), (260, 420), (-260, 420)], (238, 224, 196), OW, OUT)
    for i in range(-9, 10):
        if abs(i * 56) > 230 or True:
            c.rect(i * 56 - 16, 40 if i % 2 == 0 else 46, i * 56 + 16, 150, PUTIH, 3.4, OUT) if abs(i * 56) > 300 else None
    c.line([(-1100, 70), (-300, 70)], OUT, 4); c.line([(300, 70), (1100, 70)], OUT, 4)
    tint(c, o)


def rumah_depan_f(c, t, o):
    tint(c, o, True)


# ================================================================= MEJA MAKAN / DAPUR (GHIBLI INTERIOR STYLE)
def _pot_tanaman_ghibli(c, x, y, s=1.0, sunlit=True):
    """Pot terakota hangat + rimbunan daun organik menyala terkena sinar jendela Ghibli."""
    oc = (66, 52, 44)
    pot_c = (196, 114, 72)
    c.poly([(x - 32 * s, y - 54 * s), (x + 32 * s, y - 54 * s), (x + 24 * s, y), (x - 24 * s, y)], pot_c, 2.4 * s, oc)
    c.rect(x - 36 * s, y - 62 * s, x + 36 * s, y - 50 * s, terang(pot_c, 0.14), 2.2 * s, oc, r=4)
    c.poly([(x + 4 * s, y - 50 * s), (x + 30 * s, y - 50 * s), (x + 23 * s, y - 2 * s), (x + 4 * s, y - 2 * s)], gelap(pot_c, 0.22))
    leaf_c = (128, 178, 92) if sunlit else (74, 124, 84)
    lobes = [(-38, -22, 34, 24), (36, -18, 32, 22), (-14, -42, 36, 26), (18, -36, 32, 24), (0, -16, 38, 22)]
    _ghibli_canopy(c, x, y - 56 * s, lobes, leaf_c, s * 0.85, 0.0, False, oc, 0.0)


def meja_makan_b(c, t, o):
    """Interior dapur/ruang makan bergaya Ghibli: dinding teal-sage bergradasi, balok kayu, cahaya jendela keemasan & bayangan diagonal."""
    wk = waktu_of(o)
    oc = (62, 50, 44)
    # 1) Dinding teal-sage bergradasi lembut (sudut atas-kiri sejuk gelap -> kanan dekat jendela hangat terang)
    wall_top = (68, 112, 118) if wk != "malam" else (34, 52, 74)
    wall_bot = (132, 168, 158) if wk != "malam" else (58, 76, 98)
    c.gradient(wall_top, wall_bot, 0.0, 0.85)
    # sudut dinding kiri (perspektif sudut ruangan seperti referensi gambar 3!)
    c.poly([(-2200, -1200), (-340, -1200), (-340, 0), (-2200, 0)],
           (82, 128, 132) if wk != "malam" else (42, 60, 82))
    c.line([(-340, -1200), (-340, 0)], (52, 86, 92), 3.0)
    # pendaran cahaya hangat matahari masuk dari jendela kanan ke dinding
    if wk != "malam":
        sun_col = (255, 224, 152) if wk != "sore" else (255, 178, 116)
        c.poly([(560, -760), (1100, -760), (260, 40), (-420, 40)], sun_col + (42,))
        c.poly([(620, -680), (1050, -680), (420, 40), (-80, 40)], sun_col + (34,))

    # 2) Balok kayu plafon atas (posisi pas untuk kamera medium/normal agar karakter tampil besar & jelas!)
    beam_c = (128, 88, 60)
    c.rect(X0, -680, X1, -595, gelap(beam_c, 0.25), 3.0, oc)
    c.poly([(-380, -595), (-250, -595), (-160, -680), (-320, -680)], beam_c, 2.5, oc)
    c.poly([(180, -595), (310, -595), (440, -680), (280, -680)], beam_c, 2.5, oc)

    # 3) Counter dapur kayu hangat + kabinet teal-pudar di bawah (proporsi normal sejajar pinggang karakter)
    wood_c = (198, 134, 78) if wk != "malam" else (126, 86, 54)
    cab_c = (104, 152, 152) if wk != "malam" else (58, 86, 96)
    c.rect(X0, -172, X1, -144, wood_c, 3.0, oc)
    c.rect(X0, -144, X1, 0, cab_c, 3.0, oc)
    for lx in (-740, -480, -220, 80, 360, 620):
        c.rect(lx, -132, lx + 210, -14, gelap(cab_c, 0.08), 2.4, oc, r=4)
        c.ell(lx + 105, -104, 5.5, 5.5, (226, 214, 186), 1.8, oc)
    lantai(c, (176, 126, 84) if wk != "malam" else (96, 72, 54), garis=(142, 98, 64))

    # 4) Jendela kayu tinggi di kanan (masuk frame kamera normal z=0.85..1.0!)
    jx0, jx1, jy0, jy1 = 360, 680, -560, -192
    c.rect(jx0 - 18, jy0 - 18, jx1 + 18, jy1 + 18, (158, 102, 62), 3.4, oc, r=6)
    top_s, bot_s = LANGIT.get(wk, LANGIT["siang"])
    c.rect(jx0, jy0, jx1, jy1, mix(top_s, (255, 236, 184), 0.45) if wk != "malam" else top_s, 2.6, oc)
    if wk != "malam":
        c.ell(jx1 - 52, jy0 + 78, 72, 72, (255, 242, 194, 120))
    for ky in (-440, -316):
        c.rect(jx0, ky - 7, jx1, ky + 7, (176, 118, 72), 2.2, oc)
    c.rect((jx0 + jx1) / 2 - 7, jy0, (jx0 + jx1) / 2 + 7, jy1, (176, 118, 72), 2.2, oc)
    _pot_tanaman_ghibli(c, 460, -188, 0.62, sunlit=(wk != "malam"))
    _pot_tanaman_ghibli(c, 588, -188, 0.54, sunlit=(wk != "malam"))

    # 5) Rak kayu dinding kiri & tengah (masuk frame kamera normal!)
    for rx0, rx1, ry in ((-640, -290, -475), (-640, -310, -330), (-120, 220, -405)):
        c.poly([(rx0, ry + 18), (rx1, ry + 18), (rx1 - 68, ry + 92), (rx0 - 68, ry + 92)], (42, 74, 82, 62))
        c.rect(rx0, ry, rx1, ry + 18, wood_c, 2.6, oc, r=4)
        c.poly([(rx0 + 22, ry + 18), (rx0 + 42, ry + 18), (rx0 + 22, ry + 52)], gelap(wood_c, 0.20), 2.0, oc)
        c.poly([(rx1 - 42, ry + 18), (rx1 - 22, ry + 18), (rx1 - 22, ry + 52)], gelap(wood_c, 0.20), 2.0, oc)
    for tx, col in ((-585, (162, 198, 178)), (-505, (226, 198, 146)), (-425, (214, 134, 96)), (-345, (172, 194, 206))):
        c.rect(tx - 22, -536, tx + 22, -475, col, 2.2, oc, r=8)
        c.rect(tx - 16, -548, tx + 16, -534, (238, 228, 208), 2.0, oc, r=4)
    for tx, col in ((-560, (206, 118, 72)), (-455, (232, 224, 206)), (-365, (148, 184, 152))):
        c.ell(tx, -354, 28, 23, col, 2.2, oc)
    _pot_tanaman_ghibli(c, 15, -405, 0.72, sunlit=(wk != "malam"))
    _pot_tanaman_ghibli(c, 135, -405, 0.58, sunlit=(wk != "malam"))
    c.rect(195, -228, 298, -172, (232, 226, 212), 2.4, oc, r=8)
    c.ell(246, -228, 52, 10, (216, 208, 194), 2.0, oc)
    c.ell(246, -238, 10, 7, (186, 178, 164), 1.8, oc)
    tint(c, o)


def meja_makan_f(c, t, o):
    """Meja kayu hangat foreground bergaya Ghibli (rendah di pinggir bawah agar karakter tetap besar & jelas)."""
    wk = waktu_of(o)
    oc = (62, 50, 44)
    wood_top = (224, 156, 92) if wk != "malam" else (142, 98, 62)
    wood_side = (176, 112, 66) if wk != "malam" else (106, 70, 44)
    c.set_depth(1.10)
    c.poly([(-680, 12), (680, 12), (820, 170), (-820, 170)], wood_top, 3.0, oc)
    c.rect(-820, 162, 820, 210, wood_side, 2.8, oc)
    c.ell(385, 58, 92, 18, (112, 68, 48, 68))
    c.ell(105, 66, 86, 16, (112, 68, 48, 62))
    c.ell(435, 16, 48, 40, (124, 178, 116), 2.6, oc)
    c.ell(418, 2, 18, 11, terang((124, 178, 116), 0.25))
    c.rect(412, -26, 458, -14, (148, 198, 136), 2.2, oc, r=5)
    c.ell(142, 32, 60, 28, (198, 124, 72), 2.6, oc)
    c.ell(142, 22, 56, 16, (238, 194, 118), 2.0, oc)
    _pot_tanaman_ghibli(c, -485, 74, 0.72, sunlit=(wk != "malam"))
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= PADANG / POLOS
def padang_b(c, t, o):
    langit(c, o)
    awan_set(c, o)
    c.set_depth(0.4)
    c.blob([(-2400, 0), (-1700, -280), (-900, -120), (-200, -330), (700, -140), (1500, -300), (2400, 0)], (150, 212, 150), 0)
    c.set_depth(0.7)
    c.blob([(-2400, 40), (-1500, -150), (-400, -40), (600, -180), (1800, -60), (2400, 40)], (118, 196, 118), 0)
    pohon(c, 900, .8, HIJAU_TUA)
    c.set_depth(1.0)
    rumput(c, warna=(132, 206, 112))
    for i in range(-10, 11):
        fx = i * 150 + (i * 37 % 60)
        c.line([(fx, 160 + (i % 3) * 60), (fx, 120 + (i % 3) * 60)], HIJAU_TUA, 4)
        c.ell(fx, 112 + (i % 3) * 60, 10, 10, [PINK, KUNING, PUTIH][i % 3], 3, OUT)
    tint(c, o)


def padang_f(c, t, o):
    tint(c, o, True)


def polos_b(c, t, o):
    col = o.get("warna", "krem")
    from tokoh import warna as _w
    base = _w(col, (255, 243, 226)) if isinstance(col, str) else tuple(col)
    c.gradient(terang(base, .35), base)
    # lingkaran lembut saja (TANPA partikel/konfeti kecil di latar: permintaan user, latar harus bersih)
    c.set_depth(0.5)
    c.ell(220, -330, 520, 520, mix(base, (255, 255, 255), .5))
    c.ell(-760, -520, 190, 190, mix(base, (255, 255, 255), .35))
    c.set_depth(1.0)
    c.rect(X0, 0, X1, 1400, mix(base, (255, 255, 255), .25) if not o.get("lantai") else (240, 223, 195))
    c.line([(X0, 0), (X1, 0)], OUT, 3)


def polos_f(c, t, o):
    pass


# ================================================================= RUANG OTAK & DALAM TUBUH
def ruang_otak_b(c, t, o):
    """Ruang kendali tubuh milik Sang Otak (layar ECG, status, suhu, kabel saraf menyala)."""
    if "istirahat_t" in o and t >= float(o["istirahat_t"]):
        bahaya, mode = False, "istirahat"
    elif "bahaya_t" in o:
        bahaya = t >= float(o["bahaya_t"])
        mode = "bahaya" if bahaya else o.get("mode", "normal")
    else:
        bahaya = bool(o.get("bahaya"))
        mode = o.get("mode", "bahaya" if bahaya else "normal")
    bg_top = (92, 34, 48) if bahaya else ((38, 60, 104) if mode == "istirahat" else (46, 54, 96))
    bg_bot = (138, 56, 68) if bahaya else ((68, 96, 148) if mode == "istirahat" else (78, 88, 142))
    c.gradient(bg_top, bg_bot, 0, 0.85)
    # jalur saraf di dinding belakang (parallax lembut)
    c.set_depth(0.6)
    nc = (255, 120, 120) if bahaya else ((130, 210, 255) if mode == "istirahat" else (126, 224, 240))
    for sy in (-760, -610, -450):
        c.curve([(-2200, sy), (-1100, sy - 60), (0, sy + 20), (1100, sy - 50), (2200, sy)], nc + (120,), 8)
    # pulsa sinyal besar berjalan di kabel saraf
    for i in range(4):
        px = -1400 + ((t * 260 + i * 760) % 2800)
        py = -760 + (i % 3) * 155
        c.ell(px, py, 14, 14, nc, 3, OUT)
    c.set_depth(1.0)
    # lantai logam pastel
    lantai(c, (96, 106, 144) if not bahaya else (112, 72, 84), garis=(74, 82, 118))
    # ---- Monitor Kiri: ECG Detak Jantung
    c.rect(-820, -660, -340, -370, (32, 38, 62), OW, OUT, r=18)
    c.rect(-800, -640, -360, -390, (18, 28, 42))
    ecg_c = (255, 86, 86) if bahaya else (88, 240, 152)
    pts = []
    speed = 5.5 if bahaya else (1.8 if mode == "istirahat" else 3.2)
    for k in range(32):
        xx = -790 + k * 13.5
        ph = (k * 0.42 - t * speed) % 3.2
        yy = -515
        if 1.2 < ph < 1.45:
            yy -= 78
        elif 1.45 <= ph < 1.7:
            yy += 46
        elif 0.8 < ph <= 1.2:
            yy -= 16
        pts.append((xx, yy))
    c.line(pts, ecg_c, 6, False)
    c.text(-580, -612, "DETAK JANTUNG", 22, (190, 210, 236), "teks")
    # ---- Monitor Tengah: Status Utama
    c.rect(-290, -700, 290, -370, (32, 38, 62), OW, OUT, r=20)
    scr_c = (74, 20, 28) if bahaya else ((20, 44, 72) if mode == "istirahat" else (20, 44, 58))
    c.rect(-270, -680, 270, -390, scr_c)
    if bahaya:
        blink = 0.55 + 0.45 * math.sin(t * 10)
        c.text(0, -565, "BAHAYA!", 56, (255, int(90 * blink + 50), 90), "seru")
        c.text(0, -490, "VIRUS TERDETEKSI", 28, (255, 206, 130), "judul")
    elif mode == "istirahat":
        c.text(0, -565, "MODE ISTIRAHAT", 38, (140, 224, 255), "judul")
        c.text(0, -495, "PEMULIHAN TUBUH", 26, (210, 240, 255), "teks")
    else:
        c.text(0, -565, "TUBUH NORMAL", 42, (110, 244, 174), "judul")
        c.text(0, -495, "SEMUA KENDALI AKTIF", 24, (190, 232, 245), "teks")
    # ---- Monitor Kanan: Suhu Tubuh
    c.rect(340, -660, 820, -370, (32, 38, 62), OW, OUT, r=18)
    c.rect(360, -640, 800, -390, (18, 28, 42))
    c.text(580, -612, "SUHU TUBUH", 22, (190, 210, 236), "teks")
    suhu_txt = "39.2 C" if bahaya else ("37.4 C" if mode == "istirahat" else "36.6 C")
    suhu_col = (255, 92, 92) if bahaya else ((255, 206, 92) if mode == "istirahat" else (106, 238, 166))
    c.text(580, -525, suhu_txt, 54, suhu_col, "seru")
    # bar suhu
    c.rect(410, -455, 750, -425, (44, 52, 74), 3, OUT, r=10)
    fill_w = 320 if bahaya else (210 if mode == "istirahat" else 160)
    c.rect(414, -451, 414 + fill_w, -429, suhu_col, 0, OUT, r=8)
    # lampu sirene bahaya di sudut atas
    if bahaya:
        al = int(40 + 35 * (0.5 + 0.5 * math.sin(t * 9)))
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=(255, 40, 40, al))


def ruang_otak_f(c, t, o):
    if o.get("konsol", True):
        # meja konsol rendah di depan kaki agar tokoh & tangan tetap terlihat jelas
        c.poly([(-460, -140), (460, -140), (520, 0), (-520, 0)], (118, 130, 170), OW, OUT)
        c.poly([(-460, -140), (460, -140), (480, -104), (-480, -104)], (152, 166, 208), OW, OUT)
        for i, col in enumerate((HIJAU, KUNING, BIRU_MUDA, MERAH, HIJAU, KUNING)):
            bx = -300 + i * 120
            c.ell(bx, -122, 22, 10, col, 3, OUT)


def dalam_tubuh_b(c, t, o):
    """Latar di dalam tubuh/pembuluh darah (pastel merah muda; memerah hangat saat demam)."""
    demam = bool(o.get("demam"))
    top = (214, 62, 54) if demam else (214, 96, 118)
    bot = (252, 132, 86) if demam else (252, 178, 186)
    c.gradient(top, bot, 0, 0.9)
    # dinding terowongan pembuluh darah melengkung di kejauhan (parallax)
    c.set_depth(0.45)
    wall_c = (182, 48, 44) if demam else (186, 74, 98)
    c.blob([(-2600, -1200), (-2600, -680), (-1400, -610), (-300, -700), (800, -600), (1900, -690), (2600, -620), (2600, -1200)], wall_c, OW, OUT, n=6)
    # sel darah merah mengambang lembut (objek besar bersih, bukan partikel kecil)
    rbc_c = (232, 54, 62) if not demam else (246, 86, 44)
    for i in range(6):
        rx = -1500 + ((i * 580 + t * (95 if demam else 55)) % 3000)
        ry = -540 + (i % 3) * 145 + math.sin(t * 2.0 + i) * 14
        c.ell(rx, ry, 58, 34, rbc_c, 3.6, OUT)
        c.ell(rx, ry, 28, 14, gelap(rbc_c, 0.22))
    c.set_depth(1.0)
    # lantai pembuluh darah lembut
    lantai(c, (226, 98, 76) if demam else (232, 134, 150), garis=(198, 74, 60) if demam else (204, 108, 126))
    if demam:
        # indikator panas/termometer besar di sisi kanan latar
        c.rect(520, -640, 620, -240, (255, 240, 232), OW, OUT, r=42)
        c.ell(570, -220, 66, 66, (255, 240, 232), OW, OUT)
        lvl = 0.72 + 0.16 * (0.5 + 0.5 * math.sin(t * 4.0))
        top_y = lerp(-240, -600, lvl)
        c.rect(546, top_y, 594, -210, MERAH, 0, OUT, r=18)
        c.ell(570, -220, 44, 44, MERAH)
        c.text(570, -685, "39.2 C", 44, KUNING_MUDA, "seru", stroke=4)
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=(255, 80, 40, 38))


def dalam_tubuh_f(c, t, o):
    # lekukan jaringan foreground lembut di pinggir bawah
    c.set_depth(1.15)
    fc = (176, 48, 42) if o.get("demam") else (188, 82, 106)
    c.ell(-1050, 90, 240, 120, fc, OW, OUT)
    c.ell(1050, 90, 240, 120, fc, OW, OUT)
    c.set_depth(1.0)


# ================================================================= KAFE COZY
def kafe_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (244, 224, 198) if wk != "malam" else (68, 56, 78))
    c.rect(X0, -240, X1, 0, (176, 126, 86) if wk != "malam" else (78, 56, 48))
    c.line([(X0, -240), (X1, -240)], OUT, OW)
    lantai(c, (196, 150, 108) if wk != "malam" else (112, 86, 68), garis=(168, 122, 84))
    # jendela kafe lebar + pemandangan luar
    jendela(c, -480, -490, 440, 320, o)
    # papan menu kapur hitam + rak kopi
    c.rect(140, -640, 560, -340, (44, 48, 56), OW * 1.2, OUT, r=12)
    c.text(350, -585, o.get("papan", "KOPI & CERITA"), 34, (255, 226, 146), "judul")
    for ly in (-520, -470, -420):
        c.line([(200, ly), (490, ly)], (220, 226, 230), 4)
    # 3 lampu gantung hangat berpendar
    for lx in (-260, 180, 620):
        c.line([(lx, -900), (lx, -640)], OUT, 4)
        c.poly([(lx - 42, -600), (lx + 42, -600), (lx + 24, -645), (lx - 24, -645)], (58, 64, 78), OW, OUT)
        glow(c, lx, -580, 220, (255, 216, 130), 85 if wk == "malam" else 42)
    # meja bar belakang + tanaman
    c.rect(680, -210, 1060, 0, (142, 96, 66), OW, OUT)
    c.rect(660, -230, 1080, -206, (198, 146, 98), OW, OUT, r=4)
    tanaman(c, -860, 0, 1.05, (214, 118, 86))
    tint(c, o)


def kafe_f(c, t, o):
    # meja kayu kecil foreground + cangkir kopi mengepul
    c.set_depth(1.18)
    c.rect(-1040, 80, -680, 120, KAYU, OW, OUT, r=6)
    c.rect(-960, 120, -930, 300, (70, 74, 86), OW, OUT)
    c.rect(-820, 24, -764, 80, PUTIH, OW * .8, OUT, r=8)
    for sx in (-802, -782):
        c.curve([(sx, 14), (sx + 6 * math.sin(t * 3 + sx), -16), (sx - 6 * math.sin(t * 3), -44)], (255, 255, 255, 160), 4)
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= KOTA MODERN
def kota_b(c, t, o):
    wk = waktu_of(o)
    langit(c, o, t=t)
    awan_set(c, o, 6, t=t)
    # skyline gedung jauh berlapis (atmospheric depth)
    c.set_depth(0.32)
    for i in range(-6, 7):
        bx = i * 320
        bh = 340 + (abs(i * 73) % 5) * 95
        bc = (132, 162, 198) if wk != "malam" else (34, 42, 82)
        c.rect(bx - 125, -bh, bx + 125, 0, bc)
        c.rect(bx + 45, -bh, bx + 125, 0, gelap(bc, 0.14))
        if wk == "malam":
            for wy in range(-bh + 36, -40, 44):
                for wx in (bx - 80, bx - 25, bx + 30):
                    if (wx + wy + i) % 3 != 0:
                        c.rect(wx, wy, wx + 28, wy + 22, (255, 224, 128))
    # lapisan tengah: ruko + pohon kota variatif
    c.set_depth(0.72)
    for i in range(-4, 5):
        if i % 2 == 0:
            ruko_kafe(c, i * 520, 340, 330, [(240, 232, 220), (218, 232, 244), (246, 226, 220)][abs(i) % 3],
                      [(56, 134, 152), (214, 88, 76), (222, 156, 68)][abs(i) % 3])
        else:
            pohon(c, i * 520, 0.88, HIJAU, gaya=("bulat_tinggi", "sakura", "palem")[abs(i) % 3], t=t)
    c.set_depth(1.0)
    # trotoar kota + zebra cross + aspal
    c.rect(X0, 0, X1, 130, (208, 212, 218), OW, OUT)
    c.rect(X0, 112, X1, 130, (176, 180, 188))
    c.rect(X0, 130, X1, 1400, (78, 84, 98))
    for i in range(-4, 5):
        c.rect(i * 340, 280, i * 340 + 180, 304, (248, 244, 224))
    tint(c, o)


def kota_f(c, t, o):
    c.set_depth(1.36)
    c.rect(-1080, -680, -1010, 240, (44, 52, 68, 175))
    c.rect(1020, -680, 1090, 240, (44, 52, 68, 175))
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= PANTAI TROPIS
def pantai_b(c, t, o):
    wk = waktu_of(o)
    langit(c, o, t=t)
    awan_set(c, o, 7, t=t)
    # laut bergradasi + ombak bergerak lembut
    c.set_depth(0.45)
    sea_top = (64, 156, 216) if wk != "sore" else (186, 116, 132)
    sea_bot = (102, 198, 226) if wk != "sore" else (238, 156, 126)
    if wk == "malam":
        sea_top, sea_bot = (24, 46, 94), (36, 72, 122)
    c.rect(X0, -190, X1, -20, sea_top)
    c.rect(X0, -110, X1, -20, sea_bot)
    for i in range(-6, 7):
        ox = i * 380 + math.sin(t * 1.8 + i) * 28
        c.curve([(ox - 90, -130), (ox, -142), (ox + 90, -130)], (255, 255, 255, 130), 4.5)
        c.curve([(ox - 110, -56), (ox, -68), (ox + 110, -56)], (255, 255, 255, 170), 5.5)
    c.set_depth(1.0)
    # pasir pantai hangat bervolume
    c.rect(X0, -24, X1, 1400, (246, 224, 178))
    c.rect(X0, 160, X1, 1400, (236, 210, 158))
    c.line([(X0, -24), (X1, -24)], (255, 255, 255), 8.0)
    pohon(c, -620, 1.12, (92, 180, 96), gaya="palem", t=t)
    pohon(c, 740, 1.04, (84, 172, 92), gaya="palem", t=t)
    # payung pantai garis-garis
    ux = 360
    c.line([(ux, 0), (ux + 24, -260)], KAYU_TUA, 10)
    c.poly([(ux - 140, -220), (ux + 24, -305), (ux + 188, -220)], MERAH, OW, OUT)
    c.poly([(ux - 48, -220), (ux + 24, -305), (ux + 96, -220)], PUTIH, OW * .8, OUT)
    tint(c, o)


def pantai_f(c, t, o):
    c.set_depth(1.28)
    c.ell(-1060, 200, 260, 90, (226, 196, 142))
    c.ell(1080, 210, 240, 85, (226, 196, 142))
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= KENDARAAN SOFT GHIBLI (MOBIL, KERETA, BUS, SEPEDA)
def mobil_ghibli(c, x, y=0, s=1.0, warna=(212, 116, 98), arah=1, t=0.0):
    """Mobil retro Jepang / Ghibli membulat lucu dengan bodi 2-tone, kaca berpantulan, lampu bundar & roda berputar."""
    oc = (62, 52, 48)
    d = 1 if arah >= 0 else -1
    bob = math.sin(t * 14.0) * 1.8 * s
    yy = y + bob
    # bayangan di aspal
    c.ell(x, y + 6 * s, 148 * s, 16 * s, (38, 44, 56, 78))
    # bodi bawah & kabin atas membulat
    body = [(x - 134 * s * d, yy - 24 * s), (x - 138 * s * d, yy - 68 * s), (x - 94 * s * d, yy - 78 * s),
            (x - 66 * s * d, yy - 134 * s), (x + 48 * s * d, yy - 134 * s), (x + 86 * s * d, yy - 82 * s),
            (x + 136 * s * d, yy - 68 * s), (x + 134 * s * d, yy - 24 * s)]
    c.poly(body, warna, 3.2 * s, oc)
    # cel shadow bawah bodi & atap krem lembut (gaya 2-tone retro!)
    c.poly([(x - 132 * s * d, yy - 46 * s), (x + 132 * s * d, yy - 46 * s),
            (x + 132 * s * d, yy - 24 * s), (x - 132 * s * d, yy - 24 * s)], gelap(warna, 0.16))
    c.poly([(x - 62 * s * d, yy - 134 * s), (x + 46 * s * d, yy - 134 * s),
            (x + 56 * s * d, yy - 118 * s), (x - 70 * s * d, yy - 118 * s)], (246, 240, 224), 2.4 * s, oc)
    # jendela depan & belakang dengan pantulan kaca diagonal
    for wx0, wx1 in ((-60, -6), (6, 72)):
        c.poly([(x + wx0 * s * d, yy - 84 * s), (x + wx0 * s * d, yy - 116 * s),
                (x + wx1 * s * d, yy - 116 * s), (x + (wx1 + 6) * s * d, yy - 84 * s)], (152, 198, 222), 2.4 * s, oc)
        c.line([(x + (wx0 + 10) * s * d, yy - 88 * s), (x + (wx0 + 28) * s * d, yy - 112 * s)], (255, 255, 255, 130), 5 * s)
    # lampu depan & bemper krom
    c.ell(x + 130 * s * d, yy - 54 * s, 10 * s, 14 * s, (255, 236, 152), 2.2 * s, oc)
    c.ell(x - 130 * s * d, yy - 54 * s, 8 * s, 12 * s, (226, 88, 78), 2.0 * s, oc)
    c.rect(x - 144 * s, yy - 32 * s, x + 144 * s, yy - 20 * s, (214, 218, 222), 2.2 * s, oc, r=5)
    # 2 roda berputar
    ang = t * 9.0 * d
    for rx in (-82, 82):
        cx_w, cy_w = x + rx * s * d, y - 24 * s
        c.ell(cx_w, cy_w, 28 * s, 28 * s, (54, 58, 66), 2.8 * s, oc)
        c.ell(cx_w, cy_w, 15 * s, 15 * s, (226, 224, 214), 2.0 * s, oc)
        c.line([(cx_w - math.cos(ang) * 11 * s, cy_w - math.sin(ang) * 11 * s),
                (cx_w + math.cos(ang) * 11 * s, cy_w + math.sin(ang) * 11 * s)], oc, 2.2 * s)


def kereta_ghibli(c, x, y=0, s=1.0, gerbong=3, warna=(88, 146, 152), t=0.0):
    """Kereta api komuter/pedesaan Jepang bergaya Ghibli (rel, pantograf, garis krem-merah, jendela berjajar)."""
    oc = (58, 50, 48)
    # rel kereta & bantalan kayu di bawah
    c.rect(x - 1800 * s, y - 10 * s, x + 1800 * s, y + 6 * s, (124, 118, 114))
    for i in range(-18, 19):
        rx = x + i * 70 * s
        c.rect(rx - 14 * s, y - 4 * s, rx + 14 * s, y + 10 * s, (112, 84, 62), 1.6 * s, oc)
    c.line([(x - 1800 * s, y - 8 * s), (x + 1800 * s, y - 8 * s)], (82, 86, 96), 4.5 * s)
    car_w = 340 * s
    gap = 18 * s
    for g in range(gerbong):
        cx = x - g * (car_w + gap)
        x0, x1 = cx - car_w / 2, cx + car_w / 2
        # bodi gerbong
        c.rect(x0, y - 156 * s, x1, y - 24 * s, warna, 3.0 * s, oc, r=14 * s)
        # pita krem hangat & garis merah tipis khas kereta Jepang
        c.rect(x0 + 3 * s, y - 122 * s, x1 - 3 * s, y - 62 * s, (244, 238, 222))
        c.rect(x0 + 3 * s, y - 64 * s, x1 - 3 * s, y - 54 * s, (206, 92, 78))
        # atap abu lembut + pantograf listrik pada gerbong pertama
        c.rect(x0 + 6 * s, y - 168 * s, x1 - 6 * s, y - 154 * s, (186, 192, 198), 2.4 * s, oc, r=6 * s)
        if g == 0:
            px = cx - 40 * s
            c.line([(px - 22 * s, y - 168 * s), (px, y - 208 * s), (px + 22 * s, y - 168 * s)], oc, 3.2 * s)
            c.line([(px - 36 * s, y - 208 * s), (px + 36 * s, y - 208 * s)], oc, 4.2 * s)
            # lampu depan bulat khas kereta retro
            c.ell(x1 - 6 * s, y - 50 * s, 9 * s, 11 * s, (255, 238, 162), 2.0 * s, oc)
        # 5 jendela berjajar dengan pantulan kaca
        for j in range(5):
            jx = x0 + 26 * s + j * 60 * s
            c.rect(jx, y - 116 * s, jx + 44 * s, y - 70 * s, (148, 194, 218), 2.2 * s, oc, r=4 * s)
            c.line([(jx + 8 * s, y - 74 * s), (jx + 26 * s, y - 112 * s)], (255, 255, 255, 115), 4 * s)
        # bogie & 4 roda besi
        for bx in (x0 + 68 * s, x1 - 68 * s):
            c.rect(bx - 42 * s, y - 28 * s, bx + 42 * s, y - 14 * s, (64, 68, 78), 2.0 * s, oc, r=4 * s)
            for wx in (-24, 24):
                c.ell(bx + wx * s, y - 16 * s, 14 * s, 14 * s, (52, 56, 64), 2.0 * s, oc)
        # sambungan antar gerbong
        if g > 0:
            c.rect(x1, y - 134 * s, x1 + gap, y - 34 * s, (72, 76, 86), 2.0 * s, oc)


def bus_ghibli(c, x, y=0, s=1.0, warna=(226, 178, 92), arah=1, t=0.0):
    """Bus kota retro Ghibli (bodi 2-tone krem-kuning, jendela panjang, papan tujuan & roda berputar)."""
    oc = (60, 50, 46)
    d = 1 if arah >= 0 else -1
    yy = y + math.sin(t * 12.0) * 1.6 * s
    c.ell(x, y + 6 * s, 195 * s, 18 * s, (38, 44, 56, 75))
    c.rect(x - 186 * s, yy - 162 * s, x + 186 * s, yy - 26 * s, warna, 3.2 * s, oc, r=18 * s)
    c.rect(x - 182 * s, yy - 156 * s, x + 182 * s, yy - 86 * s, (246, 240, 224))
    c.rect(x - 182 * s, yy - 88 * s, x + 182 * s, yy - 76 * s, gelap(warna, 0.22))
    for j in range(5):
        jx = x - 162 * s + j * 66 * s
        c.rect(jx, yy - 142 * s, jx + 52 * s, yy - 94 * s, (152, 198, 222), 2.2 * s, oc, r=4 * s)
    c.ell(x + 178 * s * d, yy - 54 * s, 9 * s, 11 * s, (255, 238, 162), 2.0 * s, oc)
    for rx in (-112, 112):
        c.ell(x + rx * s, y - 26 * s, 28 * s, 28 * s, (54, 58, 66), 2.8 * s, oc)
        c.ell(x + rx * s, y - 26 * s, 14 * s, 14 * s, (226, 224, 214), 2.0 * s, oc)


def sepeda_ghibli(c, x, y=0, s=1.0, warna=(198, 118, 76)):
    """Sepeda keranjang retro Jepang (seperti referensi toko Jepang gambar 4)."""
    oc = (58, 48, 44)
    for wx in (-44, 44):
        c.ell(x + wx * s, y - 28 * s, 28 * s, 28 * s, None, 4.5 * s, oc)
        c.ell(x + wx * s, y - 28 * s, 22 * s, 22 * s, None, 1.8 * s, (186, 190, 194))
        c.ell(x + wx * s, y - 28 * s, 5 * s, 5 * s, oc)
    # rangka sepeda
    c.line([(x - 44 * s, y - 28 * s), (x - 4 * s, y - 28 * s), (x + 26 * s, y - 66 * s),
            (x - 24 * s, y - 64 * s), (x - 44 * s, y - 28 * s)], warna, 4.5 * s)
    c.line([(x + 44 * s, y - 28 * s), (x + 22 * s, y - 82 * s), (x + 10 * s, y - 86 * s)], warna, 4.5 * s)
    # sadel & keranjang depan
    c.ell(x - 26 * s, y - 70 * s, 13 * s, 5 * s, (112, 78, 54), 2.0 * s, oc)
    c.poly([(x + 26 * s, y - 76 * s), (x + 56 * s, y - 76 * s), (x + 50 * s, y - 54 * s), (x + 28 * s, y - 54 * s)],
           (168, 134, 96), 2.2 * s, oc)


SET = {
    "kamar": (kamar_b, kamar_f), "sekolah_luar": (sekolah_luar_b, sekolah_luar_f), "sekolah": (sekolah_luar_b, sekolah_luar_f),
    "taman": (taman_b, taman_f), "kelas": (kelas_b, kelas_f), "ruang_belajar": (ruang_belajar_b, ruang_belajar_f),
    "ruang_tamu": (ruang_tamu_b, ruang_tamu_f), "jalan": (jalan_b, jalan_f), "kantin": (kantin_b, kantin_f),
    "lapangan": (lapangan_b, lapangan_f), "rumah_depan": (rumah_depan_b, rumah_depan_f), "meja_makan": (meja_makan_b, meja_makan_f),
    "padang": (padang_b, padang_f), "polos": (polos_b, polos_f),
    "ruang_otak": (ruang_otak_b, ruang_otak_f), "dalam_tubuh": (dalam_tubuh_b, dalam_tubuh_f),
    "kafe": (kafe_b, kafe_f), "kota": (kota_b, kota_f), "pantai": (pantai_b, pantai_f),
}
ALIAS = {"kamar_tidur": "kamar", "gerbang_sekolah": "sekolah_luar", "halaman_sekolah": "taman", "dapur": "meja_makan",
         "ruang_keluarga": "ruang_tamu", "meja_belajar": "ruang_belajar", "komplek": "jalan", "kampung": "jalan", "luar": "padang",
         "kedai": "kafe", "coffee": "kafe", "perkotaan": "kota", "laut": "pantai"}


def set_of(name):
    name = ALIAS.get(name, name)
    return SET.get(name, SET["polos"])
