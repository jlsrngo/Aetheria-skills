# -*- coding: utf-8 -*-
"""
aset_global/sinematografi.py
Mesin Sinematografi 3D & Overlay Film GLOBAL untuk seluruh skill Aetheria
(/3D-stickman, /paperworld, /voxelverse, /strata3d, /hydro3d, /mechlab3d,
plus helper letterbox/vignette untuk /stikman-cerita).

Mendukung secara seragam di semua skill:
  - Multi-shot dalam 1 adegan (`kamera.shot` / `kamera.shots`) dengan auto-reset roll/blur
  - 16 gerak kamera profesional (`push`, `pull`, `punch_in`, `hentak`, `dolly_zoom`,
    `orbit`, `spiral`, `crane`, `truck`, `pan`, `pindah_fokus`, `terbang`,
    `ikut`/`tracking`, `whip`, `goyang`, `potong`)
  - Over-the-Shoulder (`bahu`) terkalibrasi + 180-Degree Rule
  - Rule of Thirds (`geser_x`), preset sudut vertikal (`bawah`, `rendah`, `atas`,
    `burung`, `dutch`, `dutch_kiri`), gaya drift/handheld, & bar letterbox `sinemaskop`
"""
import math
import numpy as np
from PIL import Image, ImageDraw

from .gerak import clamp, ease_io, ease_out_cubic


ANGLE_PRESET = {
    "normal":     (0.0,   0.0),
    "bawah":      (-0.52, 0.0),   # low angle (hero shot)
    "rendah":     (-0.78, 0.0),   # dramatic worm's-eye low angle
    "atas":       (+1.05, 0.0),   # high angle
    "burung":     (+3.20, 0.0),   # bird's eye
    "dutch":      (0.0,   9.0),   # horizon miring tegang (kanan)
    "dutch_kiri": (0.0,  -9.0),   # horizon miring tegang (kiri)
}

GAYA_DRIFT = {
    "tripod":     (0.0,   0.0,   0.0),
    "halus":      (0.015, 0.010, 0.85),
    "napas_film": (0.022, 0.014, 0.65),
    "handheld":   (0.042, 0.032, 1.85),
    "tegang":     (0.028, 0.024, 6.50),
}


def _prog(t, t0, t1):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0), 0.0, 1.0)


def _lerp(a, b, u):
    return a + (b - a) * u


def _lerp3(a, b, u):
    return (
        float(a[0]) + (float(b[0]) - float(a[0])) * u,
        float(a[1]) + (float(b[1]) - float(a[1])) * u,
        float(a[2]) + (float(b[2]) - float(a[2])) * u,
    )


def _ease_in(u):
    u = clamp(u)
    return u * u


def _ease_snap(u):
    u = clamp(u)
    return 1.0 - (1.0 - u) ** 4


def _ease_back(u, s=1.70158):
    u = clamp(u) - 1.0
    return 1.0 + (s + 1.0) * (u ** 3) + s * (u ** 2)


EASE_MAP = {
    "lin": lambda u: clamp(u),
    "linear": lambda u: clamp(u),
    "io": ease_io,
    "out": ease_out_cubic,
    "in": _ease_in,
    "snap": _ease_snap,
    "back": _ease_back,
}


def catmull_rom_3d(pts, u):
    """Interpolasi spline Catmull-Rom 3D mulus untuk jalur kamera `terbang`."""
    if not pts:
        return (0.0, 1.4, 4.2)
    if len(pts) == 1:
        return tuple(float(v) for v in pts[0])
    u = clamp(float(u), 0.0, 1.0)
    n = len(pts) - 1
    seg = min(n - 1, int(u * n))
    t = u * n - seg
    p0 = pts[max(0, seg - 1)]
    p1 = pts[seg]
    p2 = pts[min(n, seg + 1)]
    p3 = pts[min(n, seg + 2)]
    t2, t3 = t * t, t * t * t
    out = []
    for k in range(3):
        v = 0.5 * (
            (2.0 * p1[k])
            + (-p0[k] + p2[k]) * t
            + (2.0 * p0[k] - 5.0 * p1[k] + 4.0 * p2[k] - p3[k]) * t2
            + (-p0[k] + 3.0 * p1[k] - 3.0 * p2[k] + p3[k]) * t3
        )
        out.append(float(v))
    return tuple(out)


def calc_ots_pose(p_bahu, p_tgt, spec, portrait=False):
    """Hitung pose kamera Over-The-Shoulder (OTS) terkalibrasi (patuh 180-Degree Rule)."""
    pb = np.array(p_bahu, dtype=np.float32)
    pt = np.array(p_tgt, dtype=np.float32)
    d_vec = np.array([pb[0] - pt[0], 0.0, pb[2] - pt[2]], dtype=np.float32)
    d_len = float(np.linalg.norm(d_vec))
    d_dir = d_vec / d_len if d_len > 1e-4 else np.array([0.0, 0.0, 1.0], dtype=np.float32)
    side_val = float(spec.get("sisi_bahu", 1.08))
    back_val = float(spec.get("jarak_bahu", 1.62))
    if portrait:
        back_val *= 1.32
        side_val *= 0.88
    side = np.array([-d_dir[2], 0.0, d_dir[0]], dtype=np.float32) * side_val
    pos = pb + d_dir * back_val + side + np.array([0.0, float(spec.get("tinggi_bahu", 1.38)), 0.0], dtype=np.float32)
    tgt = pt + np.array([0.0, float(spec.get("tinggi_fokus", 0.16)), 0.0], dtype=np.float32)
    fov = float(spec.get("fov", 38.0))
    return pos, tgt, fov


def apply_cinematic_modifiers(pos, tgt, fov, roll, blur, spec):
    """Terapkan preset angle vertikal, sudut_v, geser_x (Rule of Thirds), pos/fov/roll/blur."""
    pos = np.array(pos, dtype=np.float32)
    tgt = np.array(tgt, dtype=np.float32)

    ang_name = spec.get("angle")
    if ang_name in ANGLE_PRESET:
        ady, aroll = ANGLE_PRESET[ang_name]
        pos = pos + np.array([0.0, ady, 0.0], dtype=np.float32)
        if "roll" not in spec and "miring" not in spec:
            roll = aroll
    if "sudut_v" in spec:
        pos = pos + np.array([0.0, float(spec["sudut_v"]), 0.0], dtype=np.float32)

    if "geser_x" in spec:
        fwd = tgt - pos
        right = np.array([fwd[2], 0.0, -fwd[0]], dtype=np.float32)
        rlen = float(np.linalg.norm(right))
        if rlen > 1e-4:
            tgt = tgt + (right / rlen) * float(spec["geser_x"])

    if "pos" in spec:
        pos = np.array(spec["pos"], dtype=np.float32)
    if "fov" in spec:
        fov = float(spec["fov"])
    if "roll" in spec or "miring" in spec:
        roll = float(spec.get("roll", spec.get("miring", 0.0)))
    if "blur" in spec:
        blur = float(spec["blur"])
    return pos, tgt, float(fov), float(roll), float(blur)


def eval_camera_move(g, start_pose, t, p, t1, resolve_target, resolve_actor_pos=None, pose_from_spec=None):
    """Evaluasi 16 jenis gerak kamera film secara seragam di semua skill 3D."""
    jn = str(g.get("jenis", "push")).lower()
    e = EASE_MAP.get(str(g.get("ease", "io")).lower(), ease_io)(p)
    p0, tgt0, f0, r0, b0 = start_pose
    p0 = np.array(p0, dtype=np.float32)
    tgt0 = np.array(tgt0, dtype=np.float32)

    if jn == "orbit":
        d_vec = p0 - tgt0
        rad = math.hypot(float(d_vec[0]), float(d_vec[2]))
        a0 = math.atan2(float(d_vec[0]), float(d_vec[2]))
        da = math.radians(float(g.get("derajat", 45.0))) * e
        dh = float(g.get("naik", 0.0)) * e
        tgt = np.array(resolve_target(g, t), dtype=np.float32) if ("fokus" in g or "target" in g) else tgt0
        pos = tgt + np.array([math.sin(a0 + da) * rad, float(d_vec[1]) + dh, math.cos(a0 + da) * rad], dtype=np.float32)
        return pos, tgt, f0, r0, b0

    if jn == "spiral":
        d_vec = p0 - tgt0
        rad = math.hypot(float(d_vec[0]), float(d_vec[2])) * _lerp(1.0, float(g.get("faktor", 0.72)), e)
        a0 = math.atan2(float(d_vec[0]), float(d_vec[2]))
        da = math.radians(float(g.get("derajat", 60.0))) * e
        dh = float(g.get("naik", 0.65)) * e
        tgt = np.array(resolve_target(g, t), dtype=np.float32) if ("fokus" in g or "target" in g) else tgt0
        pos = tgt + np.array([math.sin(a0 + da) * rad, float(d_vec[1]) + dh, math.cos(a0 + da) * rad], dtype=np.float32)
        fov = clamp(_lerp(f0, f0 - float(g.get("zoom", 4.0)), e), 18.0, 85.0)
        return pos, tgt, fov, r0, b0

    if jn == "crane":
        end_pose = pose_from_spec(g.get("ke", g), start_pose, t1) if pose_from_spec else start_pose
        p1, tgt1, f1, r1, b1 = end_pose
        if "naik" in g and "pos" not in g.get("ke", {}):
            p1 = p0 + np.array([0.0, float(g["naik"]), float(g.get("maju", 0.0))], dtype=np.float32)
        return (
            np.array(_lerp3(p0, p1, e), dtype=np.float32),
            np.array(_lerp3(tgt0, tgt1, e), dtype=np.float32),
            _lerp(f0, f1, e), _lerp(r0, r1, e), _lerp(b0, b1, e),
        )

    if jn == "terbang" and "jalur" in g:
        pts = [tuple(float(v) for v in pt) for pt in g["jalur"]]
        pos = np.array(catmull_rom_3d(pts, e), dtype=np.float32)
        tgt = np.array(resolve_target(g, t), dtype=np.float32)
        return pos, tgt, f0, r0, b0

    if jn in ("ikut", "tracking"):
        ap = resolve_actor_pos(g.get("fokus"), t) if resolve_actor_pos else None
        if ap is not None:
            if "offset" in g:
                off = np.array(g["offset"], dtype=np.float32)
            else:
                dist = float(g.get("jarak", 2.9))
                yaw = math.radians(float(g.get("sudut", 24.0)) + float(g.get("derajat", 0.0)) * e)
                dy = float(g.get("tinggi", 1.35))
                off = np.array([math.sin(yaw) * dist, dy, math.cos(yaw) * dist], dtype=np.float32)
            tgt = np.array([ap[0], ap[1] + float(g.get("tinggi_fokus", 1.10)), ap[2]], dtype=np.float32)
            pos = np.array([ap[0] + off[0], ap[1] + off[1], ap[2] + off[2]], dtype=np.float32)
            return pos, tgt, float(g.get("fov", f0)), r0, b0
        return start_pose

    if jn == "punch_in":
        es = _ease_snap(p)
        faktor = float(g.get("faktor", 0.58))
        pos = np.array(_lerp3(p0, tgt0 + (p0 - tgt0) * faktor, es), dtype=np.float32)
        fov = _lerp(f0, max(24.0, f0 - float(g.get("zoom", 10.0))), es)
        return pos, tgt0, fov, r0, b0

    if jn == "hentak":
        pulse = math.sin(math.pi * clamp(p)) * float(g.get("kuat", 0.16))
        pos = tgt0 + (p0 - tgt0) * (1.0 - pulse)
        fov = max(22.0, f0 - pulse * 18.0)
        return pos, tgt0, fov, r0, b0

    if jn == "dolly_zoom":
        faktor = float(g.get("faktor", 1.65))
        dist_scale = _lerp(1.0, faktor, e)
        pos = tgt0 + (p0 - tgt0) * dist_scale
        half_rad = math.atan(math.tan(math.radians(f0 * 0.5)) / max(0.35, dist_scale))
        fov = clamp(math.degrees(half_rad * 2.0), 18.0, 85.0)
        return pos, tgt0, fov, r0, b0

    if jn == "truck":
        delta = np.array([float(g.get("x", 1.2)), float(g.get("y", 0.0)), float(g.get("z", 0.0))], dtype=np.float32) * e
        return p0 + delta, tgt0 + delta, f0, r0, b0

    if jn == "pan":
        v = tgt0 - p0
        da = math.radians(float(g.get("derajat", 30.0))) * e
        c_a, s_a = math.cos(da), math.sin(da)
        nv = np.array([v[0] * c_a + v[2] * s_a, v[1] + float(g.get("naik", 0.0)) * e, -v[0] * s_a + v[2] * c_a], dtype=np.float32)
        return p0, p0 + nv, f0, r0, b0

    if jn == "pindah_fokus":
        tgt1 = np.array(resolve_target(g, t), dtype=np.float32)
        tgt = np.array(_lerp3(tgt0, tgt1, e), dtype=np.float32)
        blur = max(b0, float(g.get("blur", 1.6)) * math.sin(math.pi * p))
        return p0, tgt, f0, r0, blur

    if jn in ("push", "pull", "terbang", "miring", "whip", "potong"):
        end_pose = pose_from_spec(g.get("ke", g), start_pose, t1) if pose_from_spec else start_pose
        p1, tgt1, f1, r1, b1 = end_pose
        if jn == "push" and "ke" not in g:
            f1 = max(26.0, f0 - float(g.get("zoom", 8.0)))
            p1 = tgt0 + (p0 - tgt0) * float(g.get("faktor", 0.78))
        elif jn == "pull" and "ke" not in g:
            f1 = min(64.0, f0 + float(g.get("zoom", 8.0)))
            p1 = tgt0 + (p0 - tgt0) * float(g.get("faktor", 1.32))
        u = 1.0 if jn == "potong" else e
        blur = _lerp(b0, b1, u)
        if jn == "whip" and 0.1 < p < 0.9:
            blur = max(blur, 3.0 * math.sin(math.pi * p))
        return (
            np.array(_lerp3(p0, p1, u), dtype=np.float32),
            np.array(_lerp3(tgt0, tgt1, u), dtype=np.float32),
            _lerp(f0, f1, u), _lerp(r0, r1, u), blur,
        )

    return start_pose


class SinematografiRig:
    """Sutradara kamera multi-shot global untuk semua skill 3D (mendukung `shot`, `gerak`, & `awal`/`akhir`)."""

    def __init__(self, cam_spec, dur, when_fn, pose_from_spec, resolve_target, resolve_actor_pos=None):
        self.cam_spec = cam_spec or {}
        self.dur = max(0.1, float(dur))
        self.when = when_fn
        self.pose_from_spec = pose_from_spec
        self.resolve_target = resolve_target
        self.resolve_actor_pos = resolve_actor_pos
        self.shots = []
        self.moves = []
        self.base_pose = None
        self._build()

    def _build(self):
        cam = self.cam_spec
        shots_raw = cam.get("shot") or cam.get("shots")
        if isinstance(shots_raw, list) and shots_raw:
            ordered = sorted(shots_raw, key=lambda x: self.when(x))
            for idx_s, sh in enumerate(ordered):
                t0 = self.when(sh)
                t1 = self.when(ordered[idx_s + 1]) if idx_s + 1 < len(ordered) else self.dur
                base_s = self.pose_from_spec(sh, None, t0)
                sub_moves = []
                g_spec = sh.get("gerak")
                g_list = g_spec if isinstance(g_spec, list) else ([g_spec] if isinstance(g_spec, dict) else [])
                cur_b = base_s
                for g in g_list:
                    gt0 = t0 + float(g.get("t", 0.0))
                    gdur = float(g.get("dur", max(0.15, t1 - gt0)))
                    gt1 = gt0 + gdur
                    sub_moves.append((gt0, gt1, g, cur_b))
                    if str(g.get("jenis", "")).lower() not in ("goyang", "hentak"):
                        cur_b = eval_camera_move(
                            g, cur_b, gt1, 1.0, gt1,
                            self.resolve_target, self.resolve_actor_pos, self.pose_from_spec,
                        )
                self.shots.append((t0, t1, sh, base_s, sub_moves))
            return

        # Mode kompatibel: awal + gerak[], atau awal -> akhir (cutaway)
        awal = cam.get("awal", {"ukuran": "penuh"})
        base = self.pose_from_spec(awal, None, 0.0)
        self.base_pose = base
        gerak_list = list(cam.get("gerak", []))
        if not gerak_list and "akhir" in cam:
            gerak_list = [{"t": 0.0, "dur": self.dur, "jenis": "push", "ke": cam["akhir"]}]
        for g in sorted(gerak_list, key=lambda x: self.when(x)):
            t0 = self.when(g)
            jn = str(g.get("jenis", "push")).lower()
            default_dur = 0.01 if jn == "potong" else (0.22 if jn in ("punch_in", "hentak") else 1.2)
            dur_g = float(g.get("dur", default_dur))
            t1 = t0 + dur_g
            self.moves.append((t0, t1, g, base))
            if jn not in ("goyang", "hentak"):
                base = eval_camera_move(
                    g, base, t1, 1.0, t1,
                    self.resolve_target, self.resolve_actor_pos, self.pose_from_spec,
                )

    def eval(self, t):
        """Kembalikan tuple (pos, tgt, fov, roll, blur) siap dimasukkan ke Cam3D."""
        shake = np.zeros(3, dtype=np.float32)
        gaya_cam = self.cam_spec.get("gaya", "halus")

        if self.shots:
            active = self.shots[0]
            for sh_item in self.shots:
                if t >= sh_item[0] - 1e-4:
                    active = sh_item
            _, _, sh_spec, base_s, sub_moves = active
            pose = base_s
            gaya_cam = sh_spec.get("gaya", gaya_cam)
            for gt0, gt1, g, start_pose in sub_moves:
                if t < gt0:
                    continue
                p = _prog(t, gt0, gt1)
                if str(g.get("jenis", "")).lower() == "goyang":
                    kuat = float(g.get("kuat", 0.06)) * (1.0 - p)
                    shake += np.array([math.sin(t * 48.0) * kuat, math.cos(t * 55.0) * kuat * 0.7, 0.0], dtype=np.float32)
                else:
                    pose = eval_camera_move(
                        g, start_pose, t, p, gt1,
                        self.resolve_target, self.resolve_actor_pos, self.pose_from_spec,
                    )
        else:
            pose = self.base_pose
            for t0, t1, g, start_pose in self.moves:
                if t < t0:
                    continue
                p = _prog(t, t0, t1)
                if str(g.get("jenis", "")).lower() == "goyang":
                    kuat = float(g.get("kuat", 0.06)) * (1.0 - p)
                    shake += np.array([math.sin(t * 48.0) * kuat, math.cos(t * 55.0) * kuat * 0.7, 0.0], dtype=np.float32)
                else:
                    pose = eval_camera_move(
                        g, start_pose, t, p, t1,
                        self.resolve_target, self.resolve_actor_pos, self.pose_from_spec,
                    )

        pos, tgt, fov, roll, blur = pose
        dx_a, dy_a, freq = GAYA_DRIFT.get(str(gaya_cam).lower(), GAYA_DRIFT["halus"])
        drift = np.array([math.sin(t * freq) * dx_a, math.cos(t * freq * 0.76) * dy_a, 0.0], dtype=np.float32) if freq > 0 else np.zeros(3, dtype=np.float32)
        return (pos + shake + drift, tgt + shake * 0.35, float(fov), float(roll), float(blur))

    def sfx_events(self, scene_start=0.0):
        ev = []
        all_m = list(self.moves)
        for _, _, _, _, sub_m in self.shots:
            all_m.extend(sub_m)
        for t0, _, g, _ in all_m:
            jn = str(g.get("jenis", "")).lower()
            if jn in ("whip", "terbang", "crane", "orbit", "spiral", "dolly_zoom"):
                ev.append((scene_start + t0, "whoosh", jn))
            elif jn in ("goyang", "punch_in", "hentak"):
                ev.append((scene_start + t0, "punch", jn))
        return ev


# ------------------------------------------------------------------ Overlay Film Global
def terapkan_sinemaskop(img, rasio_bar=None, warna=(10, 12, 16)):
    """Tambahkan bar letterbox film 2.35:1 secara bersih di atas & bawah frame."""
    W, H = img.size
    frac = float(rasio_bar) if rasio_bar is not None else (0.085 if W >= H else 0.06)
    bar_h = max(1, int(H * frac))
    out = img.copy()
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, W, bar_h], fill=warna)
    d.rectangle([0, H - bar_h, W, H], fill=warna)
    return out


def terapkan_vinyet_halus(img, kuat=0.32):
    """Tambahkan vignette radial lembut ala lensa film (bukan bingkai kotak kasar)."""
    arr = np.asarray(img, dtype=np.float32)
    H, W = arr.shape[:2]
    xs = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
    ys = np.linspace(-1.0, 1.0, H, dtype=np.float32)[:, None]
    r2 = xs * xs + ys * ys
    mask = 1.0 - clamp(float(kuat), 0.0, 0.85) * np.clip((r2 - 0.35) / 1.15, 0.0, 1.0)
    out = np.clip(arr * mask[:, :, None], 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out)
