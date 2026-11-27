# -*- coding: utf-8 -*-
"""
aset_global/engineering_3d.py
Pustaka aset & animasi 3D Engineering GLOBAL yang adaptif untuk SEMUA engine 3D
di repo Aetheria:
  - /3D-stickman  (Scene3D Z-buffer: tapered_limb, cylinder, sphere, part, outline)
  - /voxelverse   (Scene3D Voxel: beam, box, rbox, textured_quad)
  - /paperworld   (ScenePaper: beam, box, rbox, textured_quad)

Jenis aset yang didukung:
  panah_3d · aliran_pipa · dial_gauge · tag_callout · tangki_air · piston_3d
"""
from contextlib import nullcontext
import math
import numpy as np

from .gerak import clamp, flow_positions, piston_kinematics, pop_scale, pulse_scale, wall_quad_y
from .tekstur import tex_dial_gauge, tex_tag_callout

KUNING = (248, 206, 56)
NAVY = (26, 44, 82)
PUTIH = (255, 255, 255)

JENIS_ENGINEERING = (
    "panah_3d",
    "aliran_pipa",
    "dial_gauge",
    "tag_callout",
    "tangki_air",
    "piston_3d",
)


# ------------------------------------------------------------------ Engine Adapter Ringan
def _is_stickman3d(sc):
    return hasattr(sc, "tapered_limb") and hasattr(sc, "cylinder") and hasattr(sc, "sphere")


def _part(sc):
    return sc.part() if hasattr(sc, "part") else nullcontext()


def _box(sc, center, size, color, alpha=1.0, emissive=0.0, specular=0.0, outline=False, outline_w=0.012):
    if _is_stickman3d(sc):
        sc.box(center, size, color, alpha=alpha, emissive=emissive, specular=specular,
               outline=outline, outline_w=outline_w)
    else:
        kw = {"alpha": alpha, "emissive": emissive}
        if hasattr(sc, "drop_shadow"):  # VoxelVerse supports specular
            kw["specular"] = specular
        sc.box(center, size, color, **kw)


def _limb(sc, p0, p1, r0, r1, color, emissive=0.0, specular=0.04, outline=True, outline_w=0.010, seg_u=14):
    if _is_stickman3d(sc):
        sc.tapered_limb(p0, p1, r0, r1, color, seg_u=seg_u, outline=outline, outline_w=outline_w,
                        emissive=emissive, specular=specular, caps=True)
    elif hasattr(sc, "beam"):
        r_avg = max(0.008, (float(r0) + float(r1)) * 0.5)
        sc.beam(p0, p1, r_avg, color, emissive=emissive)
    else:
        a = np.array(p0, dtype=np.float32)
        b = np.array(p1, dtype=np.float32)
        c = (a + b) * 0.5
        d = np.abs(b - a)
        r_avg = max(0.012, (float(r0) + float(r1)) * 0.5)
        sc.box(c, (max(d[0], r_avg * 2), max(d[1], r_avg * 2), max(d[2], r_avg * 2)), color, emissive=emissive)


def _sphere(sc, center, radius, color, emissive=0.0, outline=True, outline_w=0.009):
    if _is_stickman3d(sc):
        sc.sphere(center, radius, color, seg_u=12, seg_v=8, emissive=emissive,
                  outline=outline, outline_w=outline_w)
    else:
        d = float(radius) * 1.9
        sc.box(center, (d, d, d), color, emissive=emissive)


def _cyl(sc, center, radius, height, color, emissive=0.0, alpha=1.0, specular=0.15, outline=True, outline_w=0.012):
    if _is_stickman3d(sc):
        sc.cylinder(center, radius, height, color, seg_u=16, alpha=alpha, emissive=emissive,
                    specular=specular, outline=outline, outline_w=outline_w)
    else:
        d = float(radius) * 1.95
        _box(sc, center, (d, float(height), d), color, alpha=alpha, emissive=emissive, specular=specular)


def _quad_y(sc, x, y, z, w, h, rot_y=0.0):
    pts = wall_quad_y(x, y, z, w, h, rot_y)
    # 3D-stickman textured_quad mengharapkan urutan [BL, BR, TR, TL]
    if _is_stickman3d(sc):
        return [pts[3], pts[2], pts[1], pts[0]]
    return pts


def _tex_quad(sc, pts, pil_rgba, emissive=0.45):
    sc.textured_quad(pts, pil_rgba, emissive=emissive)


# ------------------------------------------------------------------ 6 Aset Engineering 3D
def draw_arrow_3d(sc, tail, head, r=0.045, col=KUNING, t=0.0, pulsa=False, emissive=0.55):
    """Panah 3D bercahaya dari `tail` ke `head` dengan opsi denyut (`pulsa`)."""
    a = np.array(tail, dtype=np.float32)
    b = np.array(head, dtype=np.float32)
    d = b - a
    L = float(np.linalg.norm(d))
    if L < 0.02:
        return
    mul = pulse_scale(t) if pulsa else 1.0
    rr = float(r) * mul
    u = d / L
    head_len = min(L * 0.42, rr * 3.4)
    neck = b - u * head_len
    with _part(sc):
        _limb(sc, a, neck, rr, rr, col, emissive=emissive, outline_w=0.012)
        if _is_stickman3d(sc):
            _limb(sc, neck, b, rr * 2.35, 0.004, col, emissive=emissive, outline_w=0.012)
        else:
            # Kepala panah bertingkat untuk engine voxel/paper
            mid = neck + u * (head_len * 0.45)
            _limb(sc, neck, mid, rr * 2.1, rr * 1.4, col, emissive=emissive)
            _limb(sc, mid, b, rr * 1.1, rr * 0.35, col, emissive=emissive)


def draw_pipe_flow(sc, pts, t=0.0, r_pipe=0.075, r_dot=0.042, speed=1.4, gap=0.38,
                   pipe_col=(145, 162, 182), dot_col=(72, 206, 255), cutaway=True):
    """Pipa 3D cutaway + partikel fluida yang mengalir & looping mulus sepanjang polyline."""
    P = [np.array(p, dtype=np.float32) for p in pts]
    if len(P) < 2:
        return
    z_off = np.array([0.0, 0.0, -r_pipe * 0.55 if cutaway else 0.0], dtype=np.float32)
    with _part(sc):
        for i in range(len(P) - 1):
            _limb(sc, P[i] + z_off, P[i + 1] + z_off, r_pipe, r_pipe, pipe_col,
                  specular=0.16, outline_w=0.012)
            if i > 0:
                _sphere(sc, P[i] + z_off, r_pipe * 1.02, pipe_col, outline_w=0.012)
    z_dot = np.array([0.0, 0.0, r_pipe * 0.45 if cutaway else 0.0], dtype=np.float32)
    for pos in flow_positions(P, t=t, speed=speed, gap=gap, min_dots=2):
        _sphere(sc, pos + z_dot, r_dot, dot_col, emissive=0.75, outline_w=0.009)


def draw_dial_gauge(sc, pos, judul="TEKANAN", satuan="BAR", nilai=0.65, teks_nilai="2.2", s=0.58, rot_y=0.0):
    """Gauge instrumen berjarum 3D untuk visualisasi RPM, tekanan BAR, atau suhu."""
    x, y, z = pos
    frac_q = round(clamp(float(nilai), 0.0, 1.0) * 40.0) / 40.0
    _tex_quad(sc, _quad_y(sc, x, y, z, s, s, rot_y),
              tex_dial_gauge(judul, satuan, frac_q, teks_nilai), emissive=0.45)


def draw_tag_callout(sc, pos, target=None, judul="LABEL", sub="", bg=NAVY, s=1.0, rot_y=0.0):
    """Label callout teknik + garis penunjuk 3D ke titik komponen `target`."""
    x, y, z = pos
    if target is not None:
        a = np.array([x, y - 0.12 * s, z], dtype=np.float32)
        b = np.array(target, dtype=np.float32)
        _limb(sc, a, b, 0.012 * s, 0.012 * s, PUTIH, emissive=0.5, outline_w=0.008 * s, seg_u=8)
        _sphere(sc, b, 0.032 * s, KUNING, emissive=0.7, outline_w=0.008 * s)
    _tex_quad(sc, _quad_y(sc, x, y, z, 0.78 * s, 0.24 * s, rot_y),
              tex_tag_callout(judul, sub, tuple(bg)), emissive=0.35)


def draw_water_tank(sc, pos, w=1.25, h=0.85, d=0.72, level=0.65, water_col=(58, 174, 236),
                    wall_col=(186, 196, 208), t=0.0):
    """Tangki / kolam cutaway 3D dengan permukaan air naik-turun + warna fluida dinamis."""
    x, y, z = pos
    lvl = clamp(float(level), 0.05, 0.94)
    with _part(sc):
        _box(sc, (x, y + 0.03, z), (w, 0.06, d), wall_col, outline=True, outline_w=0.012)
        _box(sc, (x, y + h * 0.5, z - d * 0.48), (w, h, 0.05), wall_col, outline=True, outline_w=0.012)
        _box(sc, (x - w * 0.48, y + h * 0.5, z), (0.05, h, d), wall_col, outline=True, outline_w=0.012)
        _box(sc, (x + w * 0.48, y + h * 0.5, z), (0.05, h, d), wall_col, outline=True, outline_w=0.012)
    wh = max(0.04, (h - 0.08) * lvl + math.sin(t * 4.5) * 0.012)
    _box(sc, (x, y + 0.06 + wh * 0.5, z + 0.01), (w - 0.12, wh, d - 0.10), water_col,
         alpha=0.82, specular=0.30, outline=False)


def draw_piston_engine(sc, pos, t=0.0, s=1.0, n_cyl=4, rpm_vis=1.8, crank_r=0.13, rod_l=0.34, block_col=(218, 176, 58)):
    """Blok mesin cutaway 3D + poros engkol + setang + piston bolak-balik + kilat pembakaran."""
    ox, oy, oz = pos
    pitch = 0.28 * s
    r_c = crank_r * s
    L_r = rod_l * s
    w_blk = (n_cyl * pitch) + 0.24 * s
    crank_y = oy + 0.24 * s
    with _part(sc):
        _box(sc, (ox, oy + 0.04 * s, oz), (w_blk + 0.16 * s, 0.07 * s, 0.42 * s),
             (54, 96, 152), outline=True, outline_w=0.012 * s)
        _box(sc, (ox, crank_y + L_r * 0.72, oz - 0.14 * s), (w_blk, L_r * 1.55, 0.12 * s),
             block_col, outline=True, outline_w=0.014 * s)
    _limb(sc, (ox - w_blk * 0.52, crank_y, oz), (ox + w_blk * 0.52, crank_y, oz),
          0.040 * s, 0.040 * s, (78, 84, 96), outline_w=0.010 * s)
    for st in piston_kinematics(t, n_cyl=n_cyl, rpm_vis=rpm_vis, crank_r=r_c, rod_l=L_r):
        i = st["index"]
        cx = ox + (i - (n_cyl - 1) * 0.5) * pitch
        pin = np.array([cx, crank_y + st["pin_y"], oz + st["pin_x"] * 0.35], dtype=np.float32)
        piston_c = np.array([cx, crank_y + st["piston_y"], oz], dtype=np.float32)
        with _part(sc):
            _limb(sc, (cx, crank_y, oz), pin, 0.028 * s, 0.028 * s, (96, 102, 114),
                  outline_w=0.008 * s, seg_u=10)
            _limb(sc, pin, piston_c, 0.026 * s, 0.024 * s, (132, 138, 150),
                  outline_w=0.008 * s, seg_u=10)
        with _part(sc):
            _cyl(sc, piston_c + np.array([0.0, 0.07 * s, 0.0], dtype=np.float32),
                 0.105 * s, 0.16 * s, (168, 174, 186), specular=0.22, outline_w=0.012 * s)
        if st["tdc_glow"] > 0.0:
            _cyl(sc, (cx, crank_y + r_c + L_r + 0.17 * s, oz), 0.098 * s,
                 0.07 * s * (0.4 + 0.6 * st["tdc_glow"]), (255, 142, 42),
                 emissive=1.1, alpha=0.85, outline=False)


# ------------------------------------------------------------------ Dispatcher Tunggal 3D
def draw_engineering_3d(sc, jenis, pos=(0.0, 0.0, 0.0), s=1.0, rot_y=0.0, t=0.0, spec=None):
    """
    Gambar salah satu dari 6 aset 3D engineering ke Scene3D / ScenePaper manapun.
    Mengembalikan True jika `jenis` dikenali dan digambar, False jika bukan aset engineering.
    """
    if jenis not in JENIS_ENGINEERING:
        return False
    sp = spec or {}
    pos = tuple(float(v) for v in pos)
    s = float(s)
    ry = float(rot_y)

    if jenis == "panah_3d":
        awal = sp.get("awal", sp.get("dari", pos))
        akhir = sp.get("akhir", sp.get("ke", (pos[0] + 0.6 * s, pos[1], pos[2])))
        draw_arrow_3d(
            sc, awal, akhir,
            r=float(sp.get("tebal", sp.get("r", 0.042))) * s,
            col=tuple(sp.get("warna", KUNING)),
            t=t,
            pulsa=bool(sp.get("pulsa", sp.get("pulse", True))),
        )
    elif jenis == "aliran_pipa":
        pts = sp.get("jalur", sp.get("titik", [pos, (pos[0] + 1.0 * s, pos[1], pos[2])]))
        draw_pipe_flow(
            sc, pts, t=t,
            r_pipe=float(sp.get("r_pipa", sp.get("r", 0.07))) * s,
            r_dot=float(sp.get("r_dot", 0.04)) * s,
            speed=float(sp.get("kecepatan", 1.4)),
            gap=float(sp.get("jarak", 0.36)),
            dot_col=tuple(sp.get("warna", sp.get("warna_aliran", (72, 206, 255)))),
            cutaway=bool(sp.get("cutaway", True)),
        )
    elif jenis == "dial_gauge":
        v0 = float(sp.get("nilai_awal", sp.get("nilai", 0.3)))
        v1 = float(sp.get("nilai_akhir", v0))
        dur = max(0.2, float(sp.get("dur", 3.0)))
        val = v0 + (v1 - v0) * clamp(t / dur, 0.0, 1.0)
        lbl_val = sp.get("teks_nilai") or f"{val * float(sp.get('maks', 10.0)):.1f}"
        draw_dial_gauge(
            sc, pos,
            sp.get("judul", "TEKANAN"),
            sp.get("satuan", sp.get("label", "BAR")),
            val, lbl_val, s=0.62 * s, rot_y=ry,
        )
    elif jenis == "tag_callout":
        pop = pop_scale(t, float(sp.get("muncul", sp.get("t0", 0.0))), 0.28)
        if pop > 0.05:
            draw_tag_callout(
                sc, pos,
                target=sp.get("target"),
                judul=sp.get("judul", sp.get("teks", "KOMPONEN")),
                sub=sp.get("sub", ""),
                bg=tuple(sp.get("warna", NAVY)),
                s=s * pop, rot_y=ry,
            )
    elif jenis == "tangki_air":
        l0 = float(sp.get("level_awal", sp.get("level", 0.65)))
        l1 = float(sp.get("level_akhir", l0))
        dur = max(0.2, float(sp.get("dur", 3.0)))
        u = clamp(t / dur, 0.0, 1.0)
        c0 = tuple(sp.get("warna_awal", sp.get("warna_air", (58, 174, 236))))
        c1 = tuple(sp.get("warna_akhir", c0))
        wcol = tuple(int(round(c0[k] + (c1[k] - c0[k]) * u)) for k in range(3))
        draw_water_tank(sc, pos, w=1.25 * s, h=0.85 * s, d=0.72 * s,
                        level=l0 + (l1 - l0) * u, water_col=wcol, t=t)
    elif jenis == "piston_3d":
        draw_piston_engine(
            sc, pos, t=t, s=s,
            n_cyl=int(sp.get("silinder", 4)),
            rpm_vis=float(sp.get("rpm", 1.8)),
            block_col=tuple(sp.get("warna", (218, 176, 58))),
        )
    return True
