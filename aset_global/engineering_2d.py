# -*- coding: utf-8 -*-
"""
aset_global/engineering_2d.py
Versi 2D kartun bersih dari 6 aset engineering global (panah_3d, aliran_pipa,
dial_gauge, tag_callout, tangki_air, piston_3d) untuk kanvas 2D `/stikman-cerita`.
"""
import math
from .gerak import clamp, flow_positions, piston_kinematics, pop_scale, pulse_scale

OUT = (28, 28, 34)
PUTIH = (255, 255, 255)
KUNING = (248, 206, 56)
NAVY = (26, 44, 82)

JENIS_ENGINEERING_2D = (
    "panah_3d",
    "aliran_pipa",
    "dial_gauge",
    "tag_callout",
    "tangki_air",
    "piston_3d",
)


def _T(x, y, s, rot):
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)

    def f(lx, ly):
        return (x + s * (lx * ca - ly * sa), y + s * (lx * sa + ly * ca))
    return f


def _P(f, pts):
    return [f(*p) for p in pts]


def draw_engineering_2d(c, jenis, x, y, s=1.0, rot=0.0, t=0.0, **opsi):
    """
    Gambar salah satu dari 6 aset engineering di kanvas 2D `stikman-cerita`.
    Mengembalikan True jika dikenali, False jika bukan aset engineering.
    """
    if jenis not in JENIS_ENGINEERING_2D:
        return False
    ow = max(2.2, 3.6 * s)
    f = _T(x, y, s, rot)

    if jenis == "panah_3d":
        col = tuple(opsi.get("warna", KUNING))
        mul = pulse_scale(t) if opsi.get("pulsa", opsi.get("pulse", True)) else 1.0
        L = float(opsi.get("panjang", 130.0)) * mul
        w = float(opsi.get("tebal", 22.0)) * mul
        pts = _P(f, [
            (-L * 0.5, -w * 0.5),
            (L * 0.12, -w * 0.5),
            (L * 0.12, -w * 1.15),
            (L * 0.5, 0.0),
            (L * 0.12, w * 1.15),
            (L * 0.12, w * 0.5),
            (-L * 0.5, w * 0.5),
        ])
        c.poly(pts, col, ow, OUT)

    elif jenis == "aliran_pipa":
        pts_raw = opsi.get("jalur", opsi.get("titik", [(-140, 0), (0, 0), (0, 70), (140, 70)]))
        pts_w = [f(p[0], p[1]) for p in pts_raw]
        r_p = float(opsi.get("r_pipa", 18.0)) * s
        pipe_col = tuple(opsi.get("warna_pipa", (145, 162, 182)))
        dot_col = tuple(opsi.get("warna", opsi.get("warna_aliran", (72, 206, 255))))
        c.line(pts_w, OUT, r_p * 2.0 + ow * 1.4)
        c.line(pts_w, pipe_col, r_p * 1.75)
        for p in flow_positions(pts_w, t=t, speed=float(opsi.get("kecepatan", 95.0)) * s,
                                gap=float(opsi.get("jarak", 56.0)) * s):
            c.ell(float(p[0]), float(p[1]), r_p * 0.52, r_p * 0.52, dot_col, max(1.8, ow * 0.65), OUT)

    elif jenis == "dial_gauge":
        v0 = float(opsi.get("nilai_awal", opsi.get("nilai", 0.65)))
        v1 = float(opsi.get("nilai_akhir", v0))
        dur = max(0.2, float(opsi.get("dur", 3.0)))
        val = clamp(v0 + (v1 - v0) * clamp(t / dur, 0.0, 1.0), 0.0, 1.0)
        R = 68.0 * s
        c.ell(x, y, R, R, (28, 32, 42), max(4.0, 6.0 * s), (235, 198, 56))
        for i in range(11):
            ang = math.radians(140.0 + i * 26.0)
            r0 = R * (0.62 if i % 2 == 0 else 0.70)
            r1 = R * 0.84
            tc = (242, 82, 74) if i >= 8 else (232, 236, 244)
            c.line([(x + math.cos(ang) * r0, y + math.sin(ang) * r0),
                    (x + math.cos(ang) * r1, y + math.sin(ang) * r1)], tc, max(2.0, 3.2 * s), False)
        n_ang = math.radians(140.0 + val * 260.0)
        c.line([(x, y), (x + math.cos(n_ang) * R * 0.66, y + math.sin(n_ang) * R * 0.66)],
               (252, 206, 62), max(3.0, 5.2 * s))
        c.ell(x, y, 8 * s, 8 * s, PUTIH, 2.2 * s, OUT)
        lbl = opsi.get("teks_nilai") or f"{val * float(opsi.get('maks', 10.0)):.1f}"
        c.text(x, y + R * 0.42, str(lbl), max(12, 18 * s), (255, 226, 84), "judul")
        c.text(x, y + R * 0.66, str(opsi.get("satuan", opsi.get("label", "BAR"))), max(10, 12 * s), (200, 208, 224), "teks")

    elif jenis == "tag_callout":
        pop = pop_scale(t, float(opsi.get("muncul", opsi.get("t0", 0.0))), 0.28)
        if pop <= 0.05:
            return True
        ps = s * pop
        bg = tuple(opsi.get("warna", NAVY))
        if opsi.get("target") is not None:
            tx, ty = opsi["target"]
            c.line([(x, y + 26 * ps), (tx, ty)], OUT, max(3.5, 5.5 * ps))
            c.line([(x, y + 26 * ps), (tx, ty)], PUTIH, max(2.0, 3.2 * ps))
            c.ell(tx, ty, 7.5 * ps, 7.5 * ps, KUNING, 2.5 * ps, OUT)
        hw, hh = 96 * ps, 30 * ps
        c.poly([(x - hw, y - hh), (x + hw, y - hh), (x + hw, y + hh), (x - hw, y + hh)], bg, max(2.5, 4.0 * ps), OUT)
        judul = str(opsi.get("judul", opsi.get("teks", "KOMPONEN"))).upper()
        sub = str(opsi.get("sub", ""))
        if sub:
            c.text(x, y - 9 * ps, judul, max(12, 17 * ps), PUTIH, "judul")
            c.text(x, y + 13 * ps, sub, max(10, 13 * ps), (255, 236, 140), "teks")
        else:
            c.text(x, y + 1 * ps, judul, max(12, 19 * ps), PUTIH, "judul")

    elif jenis == "tangki_air":
        l0 = float(opsi.get("level_awal", opsi.get("level", 0.65)))
        l1 = float(opsi.get("level_akhir", l0))
        dur = max(0.2, float(opsi.get("dur", 3.0)))
        u = clamp(t / dur, 0.0, 1.0)
        lvl = clamp(l0 + (l1 - l0) * u, 0.05, 0.94)
        c0 = tuple(opsi.get("warna_awal", opsi.get("warna_air", (58, 174, 236))))
        c1 = tuple(opsi.get("warna_akhir", c0))
        wcol = tuple(int(round(c0[k] + (c1[k] - c0[k]) * u)) for k in range(3))
        w, h = 150.0, 105.0
        # Dinding belakang + air + bingkai cutaway
        c.poly(_P(f, [(-w * 0.5, -h), (w * 0.5, -h), (w * 0.5, 0), (-w * 0.5, 0)]), (210, 218, 228), ow, OUT)
        wh = max(8.0, (h - 10.0) * lvl + math.sin(t * 4.5) * 2.5)
        c.poly(_P(f, [(-w * 0.46, -wh), (w * 0.46, -wh), (w * 0.46, -4), (-w * 0.46, -4)]), wcol)
        c.line(_P(f, [(-w * 0.5, -h), (-w * 0.5, 0), (w * 0.5, 0), (w * 0.5, -h)]), OUT, ow * 1.4)

    elif jenis == "piston_3d":
        n_cyl = int(opsi.get("silinder", 4))
        rpm = float(opsi.get("rpm", 1.8))
        block_col = tuple(opsi.get("warna", (218, 176, 58)))
        pitch = 42.0
        r_c = 16.0
        L_r = 42.0
        w_blk = n_cyl * pitch + 26.0
        # Blok kuning + alas biru
        c.poly(_P(f, [(-w_blk * 0.5, -108), (w_blk * 0.5, -108), (w_blk * 0.5, -24), (-w_blk * 0.5, -24)]),
               block_col, ow, OUT)
        c.poly(_P(f, [(-w_blk * 0.56, -18), (w_blk * 0.56, -18), (w_blk * 0.56, 0), (-w_blk * 0.56, 0)]),
               (54, 96, 152), ow, OUT)
        # Poros engkol
        c.line(_P(f, [(-w_blk * 0.52, -32), (w_blk * 0.52, -32)]), OUT, 14 * s)
        c.line(_P(f, [(-w_blk * 0.52, -32), (w_blk * 0.52, -32)]), (84, 92, 106), 9 * s)
        for st in piston_kinematics(t, n_cyl=n_cyl, rpm_vis=rpm, crank_r=r_c, rod_l=L_r):
            cx = (st["index"] - (n_cyl - 1) * 0.5) * pitch
            pin_y = -32.0 - st["pin_y"]
            pist_y = -32.0 - st["piston_y"]
            c.line(_P(f, [(cx, pin_y), (cx, pist_y)]), OUT, 10 * s)
            c.line(_P(f, [(cx, pin_y), (cx, pist_y)]), (136, 142, 156), 6 * s)
            c.poly(_P(f, [(cx - 14, pist_y - 22), (cx + 14, pist_y - 22), (cx + 14, pist_y), (cx - 14, pist_y)]),
                   (172, 178, 192), ow * 0.8, OUT)
            if st["tdc_glow"] > 0.0:
                c.ell(*f(cx, -32.0 - r_c - L_r - 24), 14 * s, 7 * s, (255, 142, 42))

    return True
