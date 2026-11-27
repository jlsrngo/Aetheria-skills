# -*- coding: utf-8 -*-
"""
aset_global/gerak.py
Kurva gerak, easing, dan kinematika prosedural GLOBAL yang dipakai bersama
oleh seluruh skill (/3D-stickman, /voxelverse, /paperworld, /stikman-cerita, dll).
"""
import math
import numpy as np


def clamp(x, a=0.0, b=1.0):
    return a if x < a else (b if x > b else x)


def smoothstep(u):
    u = clamp(u, 0.0, 1.0)
    return u * u * (3.0 - 2.0 * u)


def ease_io(u):
    u = clamp(u, 0.0, 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * u)


def ease_out_cubic(u):
    u = clamp(u, 0.0, 1.0)
    return 1.0 - (1.0 - u) ** 3


def pop_scale(t, t0=0.0, dur=0.28, over=1.12):
    """Kurva pop-in elastis dengan overshoot halus (untuk tag, panah, komponen muncul)."""
    if t <= t0:
        return 0.0
    p = clamp((t - t0) / max(dur, 1e-4), 0.0, 1.0)
    if p < 0.72:
        u = p / 0.72
        return over * (1.0 - (1.0 - u) ** 3)
    u = (p - 0.72) / 0.28
    return over + (1.0 - over) * smoothstep(u)


def pulse_scale(t, period=0.55, amp=0.12):
    """Skala berdenyut halus untuk penekanan komponen kunci."""
    return 1.0 + amp * 0.5 * (1.0 - math.cos(math.tau * t / max(period, 0.1)))


def spring_overshoot(u, freq=2.2, damp=5.0):
    """Pegas teredam dari 0 -> 1 dengan pantulan lembut."""
    u = clamp(u, 0.0, 1.0)
    if u <= 0.0:
        return 0.0
    if u >= 1.0:
        return 1.0
    return 1.0 - math.exp(-damp * u) * math.cos(math.tau * freq * u)


def bob_offset(t, amp=0.045, freq=0.8, phase=0.0):
    """Gerak mengambang naik-turun untuk ikon atau label melayang."""
    return amp * math.sin(math.tau * freq * t + phase)


def shake_offset(t, amp=0.03, freq=26.0):
    """Getaran ringan (mesin hidup, gempa, benturan)."""
    return (
        amp * math.sin(t * freq * 1.13),
        amp * 0.7 * math.cos(t * freq * 1.47),
    )


def flow_positions(pts, t=0.0, speed=1.4, gap=0.38, min_dots=2):
    """
    Hitung posisi 3D/2D partikel aliran yang meluncur dan looping mulus
    sepanjang polyline `pts`. Mengembalikan list np.ndarray float32.
    """
    P = [np.array(p, dtype=np.float32) for p in pts]
    if len(P) < 2:
        return []
    segs = [float(np.linalg.norm(P[i + 1] - P[i])) for i in range(len(P) - 1)]
    L_tot = sum(segs)
    if L_tot < 1e-4:
        return []
    n_dots = max(int(min_dots), int(round(L_tot / max(gap, 0.08))))
    out = []
    for k in range(n_dots):
        dist = (t * speed + k * (L_tot / n_dots)) % L_tot
        acc = 0.0
        pos = P[-1]
        for i, sl in enumerate(segs):
            if dist <= acc + sl or i == len(segs) - 1:
                u = clamp((dist - acc) / max(sl, 1e-5), 0.0, 1.0)
                pos = P[i] * (1.0 - u) + P[i + 1] * u
                break
            acc += sl
        out.append(pos)
    return out


def piston_kinematics(t, n_cyl=4, rpm_vis=1.8, crank_r=0.13, rod_l=0.34):
    """
    Kinematika eksak poros engkol + setang + piston bolak-balik.
    Mengembalikan list dict per silinder:
      {index, theta, pin_x, pin_y, piston_y, tdc_glow (0..1)}
    """
    phases = [0.0, math.pi, math.pi, 0.0] if n_cyl == 4 else [
        k * math.tau / max(1, n_cyl) for k in range(n_cyl)
    ]
    res = []
    for i in range(n_cyl):
        th = t * rpm_vis * math.tau + phases[i % len(phases)]
        px = math.sin(th) * crank_r
        py = math.cos(th) * crank_r
        pist_y = py + math.sqrt(max(1e-5, rod_l * rod_l - px * px))
        cos_th = math.cos(th)
        glow = ((cos_th - 0.72) / 0.28) if cos_th > 0.72 else 0.0
        res.append({
            "index": i,
            "theta": th,
            "pin_x": px,
            "pin_y": py,
            "piston_y": pist_y,
            "tdc_glow": clamp(glow, 0.0, 1.0),
        })
    return res


def wall_quad_y(x, y, z, w, h, rot_y=0.0):
    """4 sudut quad 3D yang menghadap +Z dan bisa diputar di sumbu Y."""
    a = math.radians(rot_y)
    ca, sa = math.cos(a), math.sin(a)
    hw, hh = w * 0.5, h * 0.5
    return [
        (x - hw * ca, y + hh, z + hw * sa),
        (x + hw * ca, y + hh, z - hw * sa),
        (x + hw * ca, y - hh, z - hw * sa),
        (x - hw * ca, y - hh, z + hw * sa),
    ]
