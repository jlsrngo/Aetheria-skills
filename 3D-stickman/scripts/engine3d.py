# -*- coding: utf-8 -*-
"""
engine3d.py - Mesin render 3D Cel-Shaded + Toon Ink Outline murni Python (NumPy + Pillow)
untuk skill 3D-stickman.

Sistem koordinat (tangan-kanan, +Y ke atas):
  * y = 0.0 -> lantai dunia
  * x = 0.0 -> tengah panggung; +X ke kanan
  * z = 0.0 -> tengah panggung; +Z menuju kamera depan default

Fitur inti:
  * Primitif halus: sphere, capsule, cylinder, rbox, box, limb (antar 2 titik sendi)
  * Inverted-hull toon ink outline bebas retak (zero-crack) di sekeliling tokoh & properti
  * Pencahayaan stylized 3D toon + hemisphere + matahari + PointLight + kabut jarak + bloom
  * Textured quad perspektif tajam untuk wajah 2D ekspresif, kalender, poster, peta, papan tulis
"""
import math, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
_LOCAL_FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "assets", "fonts"))
_GLOBAL_FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "aset_global", "fonts"))
FONT_DIR = _GLOBAL_FONT_DIR if os.path.isdir(_GLOBAL_FONT_DIR) else _LOCAL_FONT_DIR

# ------------------------------------------------------------------ palet warna 3D-stickman
OUT = (22, 20, 26)
PUTIH = (255, 255, 255)
KRIM = (246, 238, 224)
HITAM = (30, 32, 38)
MERAH = (218, 66, 62)
MERAH_TUA = (158, 40, 42)
PIPI = (244, 152, 158)
BIRU = (58, 122, 212)
BIRU_TUA = (34, 66, 138)
BIRU_MUDA = (164, 208, 246)
TEAL = (76, 126, 132)
TEAL_TUA = (48, 86, 92)
TOSKA = (46, 168, 128)
PINK = (238, 142, 172)
KUNING = (248, 204, 68)
ORANYE = (232, 124, 52)
HIJAU = (74, 174, 112)
HIJAU_TUA = (46, 118, 70)
COKLAT = (152, 98, 62)
COKLAT_TUA = (98, 60, 38)
KAYU = (204, 156, 108)
KAYU_TUA = (148, 106, 70)
UNGU = (138, 112, 204)
NAVY = (36, 48, 88)
ABU = (196, 202, 212)
ABU_TUA = (96, 102, 116)
KULIT = (240, 202, 168)
BATA = (166, 78, 56)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gelap(c, t=0.22):
    return mix(c, (0, 0, 0), t)


def terang(c, t=0.28):
    return mix(c, (255, 255, 255), t)


# ------------------------------------------------------------------ easing & kurva
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, a, b):
    return clamp((t - a) / max(1e-6, b - a))


def e_io(p):
    p = clamp(p)
    return p * p * p * (p * (p * 6 - 15) + 10)


def e_out(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3


def e_in(p):
    p = clamp(p)
    return p ** 3


def e_back(p, s=1.70158):
    p = clamp(p)
    return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2


def e_spring(p):
    p = clamp(p)
    if p >= 1:
        return 1.0
    return 1 - math.exp(-6.5 * p) * math.cos(10.5 * p)


def e_lin(p):
    return clamp(p)


def e_snap(p):
    p = clamp(p)
    return 1 - (1 - p) ** 5


EASE = {
    "io": e_io, "out": e_out, "in": e_in, "back": e_back,
    "spring": e_spring, "lin": e_lin, "snap": e_snap,
}


def lerp(a, b, t):
    return a + (b - a) * t


def lerp3(a, b, t):
    return (lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t))


def catmull_rom(pts, u):
    n = len(pts)
    if n == 0:
        return (0.0, 0.0, 0.0)
    if n == 1:
        return tuple(pts[0])
    u = clamp(u, 0.0, 1.0)
    if u >= 1.0:
        return tuple(pts[-1])
    seg_f = u * (n - 1)
    i = min(n - 2, int(seg_f))
    t = seg_f - i
    p0 = pts[max(0, i - 1)]
    p1 = pts[i]
    p2 = pts[i + 1]
    p3 = pts[min(n - 1, i + 2)]
    t2, t3 = t * t, t * t * t
    out = []
    for k in range(3):
        v = 0.5 * (
            (2.0 * p1[k])
            + (-p0[k] + p2[k]) * t
            + (2.0 * p0[k] - 5.0 * p1[k] + 4.0 * p2[k] - p3[k]) * t2
            + (-p0[k] + 3.0 * p1[k] - 3.0 * p2[k] + p3[k]) * t3
        )
        out.append(v)
    return tuple(out)


# ------------------------------------------------------------------ font
@functools.lru_cache(maxsize=256)
def font(name, size):
    """name: 'judul' (Fredoka), 'teks' (Nunito), 'bulat' (Baloo 2), 'seru' (Bungee), 'kode'."""
    if name == "kode":
        for cand in (
            "C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/consola.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            os.path.join(FONT_DIR, "Nunito-Var.ttf"),
        ):
            if os.path.exists(cand):
                return ImageFont.truetype(cand, max(6, int(size)))
    files = {
        "judul": ("Fredoka-Var.ttf", 700),
        "teks": ("Nunito-Var.ttf", 800),
        "bulat": ("Baloo2-Var.ttf", 800),
        "seru": ("Bungee-Regular.ttf", None),
    }
    fn, wt = files.get(name, files["judul"])
    path = os.path.join(FONT_DIR, fn)
    if not os.path.exists(path):
        for fb in ("C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            if os.path.exists(fb):
                path = fb
                wt = None
                break
    f = ImageFont.truetype(path, max(4, int(size)))
    if wt:
        try:
            axes = f.get_variation_axes()
            vals = []
            for a in axes:
                nm = a["name"].decode() if isinstance(a["name"], bytes) else a["name"]
                vals.append(min(a["maximum"], max(a["minimum"], wt)) if nm == "Weight" else a["default"])
            f.set_variation_by_axes(vals)
        except Exception:
            pass
    return f


# ------------------------------------------------------------------ transform 3D
def rot_x(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]], dtype=np.float32)


def rot_y(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0.0, s], [0.0, 1.0, 0.0], [-s, 0.0, c]], dtype=np.float32)


def rot_z(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]], dtype=np.float32)


def euler_mat(rx=0.0, ry=0.0, rz=0.0):
    m = np.eye(3, dtype=np.float32)
    if ry:
        m = m @ rot_y(ry)
    if rx:
        m = m @ rot_x(rx)
    if rz:
        m = m @ rot_z(rz)
    return m


# ------------------------------------------------------------------ unit primitives (outward normals)
_CUBE_V = np.array([
    [-0.5, -0.5, -0.5], [+0.5, -0.5, -0.5], [+0.5, +0.5, -0.5], [-0.5, +0.5, -0.5],
    [-0.5, -0.5, +0.5], [+0.5, -0.5, +0.5], [+0.5, +0.5, +0.5], [-0.5, +0.5, +0.5],
], dtype=np.float32)

_CUBE_F = np.array([
    [4, 5, 6, 7], [1, 0, 3, 2], [5, 1, 2, 6], [0, 4, 7, 3], [7, 6, 2, 3], [0, 1, 5, 4],
], dtype=np.int32)

_FACE_CORNERS = _CUBE_V[_CUBE_F]


@functools.lru_cache(maxsize=64)
def _sphere_template(seg_u=18, seg_v=12, hemi=False):
    """Unit sphere (atau top-hemisphere jika hemi=True) + smooth outward vertex normals."""
    us = np.linspace(0.0, 2.0 * math.pi, seg_u + 1, dtype=np.float32)
    v0 = 0.0 if hemi else -0.4985 * math.pi
    vs = np.linspace(v0, 0.4985 * math.pi, seg_v + 1, dtype=np.float32)
    U, V = np.meshgrid(us, vs, indexing="ij")
    X = np.cos(V) * np.sin(U)
    Y = np.sin(V)
    Z = np.cos(V) * np.cos(U)
    G = np.stack([X, Y, Z], axis=-1)
    q = np.stack([G[:-1, :-1], G[1:, :-1], G[1:, 1:], G[:-1, 1:]], axis=2)
    verts = q.reshape(-1, 4, 3).astype(np.float32)
    return verts, verts


@functools.lru_cache(maxsize=128)
def _capsule_template(r, h_cyl, seg_u=16, seg_cap=5, n_mid=1):
    """Kapsul vertikal + smooth vertex normals."""
    half = h_cyl * 0.5
    us = np.linspace(0.0, 2.0 * math.pi, seg_u + 1, dtype=np.float32)
    bot_v = np.linspace(-0.5 * math.pi, 0.0, seg_cap + 1, dtype=np.float32)
    top_v = np.linspace(0.0, 0.5 * math.pi, seg_cap + 1, dtype=np.float32)
    rings_y, rings_r, rings_ny, rings_nr = [], [], [], []
    for v in bot_v:
        sv, cv = math.sin(float(v)), math.cos(float(v))
        rings_y.append(-half + r * sv); rings_r.append(r * cv)
        rings_ny.append(sv); rings_nr.append(cv)
    if n_mid > 1:
        for my in np.linspace(-half, +half, n_mid + 1)[1:-1]:
            rings_y.append(float(my)); rings_r.append(r)
            rings_ny.append(0.0); rings_nr.append(1.0)
    for v in top_v:
        sv, cv = math.sin(float(v)), math.cos(float(v))
        rings_y.append(+half + r * sv); rings_r.append(r * cv)
        rings_ny.append(sv); rings_nr.append(cv)
    ry = np.array(rings_y, dtype=np.float32)[None, :]
    rr = np.array(rings_r, dtype=np.float32)[None, :]
    rny = np.array(rings_ny, dtype=np.float32)[None, :]
    rnr = np.array(rings_nr, dtype=np.float32)[None, :]
    U = us[:, None]
    su, cu = np.sin(U), np.cos(U)
    G = np.stack([rr * su, np.broadcast_to(ry, (seg_u + 1, len(rings_y))), rr * cu], axis=-1)
    N = np.stack([rnr * su, np.broadcast_to(rny, (seg_u + 1, len(rings_y))), rnr * cu], axis=-1)
    q = np.stack([G[:-1, :-1], G[1:, :-1], G[1:, 1:], G[:-1, 1:]], axis=2).reshape(-1, 4, 3).astype(np.float32)
    qn = np.stack([N[:-1, :-1], N[1:, :-1], N[1:, 1:], N[:-1, 1:]], axis=2).reshape(-1, 4, 3).astype(np.float32)
    return q, qn


@functools.lru_cache(maxsize=64)
def _cylinder_template(seg_u=12):
    """Silinder unit radius=1, y in [-0.5, +0.5], sisi smooth + tutup atas/bawah."""
    us = np.linspace(0.0, 2.0 * math.pi, seg_u + 1, dtype=np.float32)
    cx, cz = np.sin(us), np.cos(us)
    quads, norms = [], []
    for i in range(seg_u):
        x0, z0, x1, z1 = float(cx[i]), float(cz[i]), float(cx[i + 1]), float(cz[i + 1])
        quads.append([[x0, -0.5, z0], [x1, -0.5, z1], [x1, +0.5, z1], [x0, +0.5, z0]])
        norms.append([[x0, 0.0, z0], [x1, 0.0, z1], [x1, 0.0, z1], [x0, 0.0, z0]])
        quads.append([[0.0, +0.5, 0.0], [x0, +0.5, z0], [x1, +0.5, z1], [x1, +0.5, z1]])
        norms.append([[0.0, 1.0, 0.0]] * 4)
        quads.append([[0.0, -0.5, 0.0], [x1, -0.5, z1], [x0, -0.5, z0], [x0, -0.5, z0]])
        norms.append([[0.0, -1.0, 0.0]] * 4)
    return np.array(quads, dtype=np.float32), np.array(norms, dtype=np.float32)


@functools.lru_cache(maxsize=64)
def _frustum_template(r_bottom, r_top, height, seg_u=28, caps=True):
    """Kerucut terpotong (alas & tutup opsional), y in [-h/2, +h/2], sisi smooth."""
    rb, rt, h = float(r_bottom), float(r_top), float(height)
    us = np.linspace(0.0, 2.0 * math.pi, seg_u + 1, dtype=np.float32)
    cx, cz = np.sin(us), np.cos(us)
    dr = (rt - rb) / max(h, 1e-5)
    nr = 1.0 / math.sqrt(1.0 + dr * dr)
    ny = -dr * nr
    half = h * 0.5
    quads, norms = [], []
    for i in range(seg_u):
        x0, z0, x1, z1 = float(cx[i]), float(cz[i]), float(cx[i + 1]), float(cz[i + 1])
        quads.append([[x0 * rb, -half, z0 * rb], [x1 * rb, -half, z1 * rb],
                      [x1 * rt, +half, z1 * rt], [x0 * rt, +half, z0 * rt]])
        norms.append([[x0 * nr, ny, z0 * nr], [x1 * nr, ny, z1 * nr],
                      [x1 * nr, ny, z1 * nr], [x0 * nr, ny, z0 * nr]])
        if caps:
            quads.append([[0.0, -half, 0.0], [x1 * rb, -half, z1 * rb],
                          [x0 * rb, -half, z0 * rb], [x0 * rb, -half, z0 * rb]])
            norms.append([[0.0, -1.0, 0.0]] * 4)
            quads.append([[0.0, +half, 0.0], [x0 * rt, +half, z0 * rt],
                          [x1 * rt, +half, z1 * rt], [x1 * rt, +half, z1 * rt]])
            norms.append([[0.0, 1.0, 0.0]] * 4)
    return np.array(quads, dtype=np.float32), np.array(norms, dtype=np.float32)


@functools.lru_cache(maxsize=256)
def _rbox_template(sx, sy, sz, roundness, seg):
    hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
    r = clamp(roundness, 0.04, 0.96) * min(hx, hy, hz)

    def knots(h):
        ang = np.linspace(0.0, math.pi * 0.5, seg + 1, dtype=np.float32)
        left = -(h - r) - r * np.cos(ang)
        right = (h - r) + r * np.sin(ang)
        return np.concatenate([left, right])

    kx, ky, kz = knots(hx), knots(hy), knots(hz)

    def face_grid(u_arr, v_arr, const_val, axis_order, flip_u=False, flip_v=False):
        U, V = np.meshgrid(u_arr, v_arr, indexing="ij")
        if flip_u:
            U = U[::-1, :]
            V = V[::-1, :]
        if flip_v:
            U = U[:, ::-1]
            V = V[:, ::-1]
        C = np.full_like(U, const_val)
        coords = [None, None, None]
        coords[axis_order[0]] = U
        coords[axis_order[1]] = V
        coords[axis_order[2]] = C
        G = np.stack(coords, axis=-1)
        q = np.stack([G[:-1, :-1], G[1:, :-1], G[1:, 1:], G[:-1, 1:]], axis=2)
        return q.reshape(-1, 4, 3)

    faces = np.concatenate([
        face_grid(kx, ky, +hz, (0, 1, 2)),
        face_grid(kx, ky, -hz, (0, 1, 2), flip_u=True),
        face_grid(kz, ky, +hx, (2, 1, 0), flip_u=True),
        face_grid(kz, ky, -hx, (2, 1, 0)),
        face_grid(kx, kz, +hy, (0, 2, 1), flip_v=True),
        face_grid(kx, kz, -hy, (0, 2, 1)),
    ], axis=0)

    inner_lim = np.array([max(0.0, hx - r), max(0.0, hy - r), max(0.0, hz - r)], dtype=np.float32)
    inner = np.clip(faces, -inner_lim, inner_lim)
    delta = faces - inner
    dnorm = np.linalg.norm(delta, axis=-1, keepdims=True)
    v_round = np.where(dnorm > 1e-6, inner + delta / np.maximum(dnorm, 1e-6) * r, faces)
    fn = np.cross(v_round[:, 1] - v_round[:, 0], v_round[:, 2] - v_round[:, 0])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-6)
    fn_b = np.broadcast_to(fn[:, None, :], v_round.shape)
    vnorms = np.where(dnorm > 1e-6, delta / np.maximum(dnorm, 1e-6), fn_b)
    return v_round.astype(np.float32), vnorms.astype(np.float32)


def _verify_primitives():
    for name, vr in (
        ("cube", _FACE_CORNERS),
        ("sphere", _sphere_template(10, 6)[0]),
        ("capsule", _capsule_template(0.3, 0.4, 10, 3)[0]),
        ("cyl", _cylinder_template(10)[0]),
        ("rbox", _rbox_template(1.0, 1.0, 1.0, 0.35, 1)[0]),
    ):
        centers = vr.mean(axis=1)
        normals = np.cross(vr[:, 1] - vr[:, 0], vr[:, 2] - vr[:, 0])
        nlen = np.linalg.norm(normals, axis=1, keepdims=True)
        ok = nlen[:, 0] > 1e-7
        normals = normals[ok] / nlen[ok]
        assert np.all(np.sum(normals * centers[ok], axis=1) > 0.05), f"{name} normals must point outward!"


_verify_primitives()


# ------------------------------------------------------------------ Cam3D
class Cam3D:
    def __init__(self, pos=(0.0, 1.45, 4.2), target=(0.0, 0.95, 0.0), fov=45.0, roll=0.0, blur=0.0):
        self.pos = np.array(pos, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.fov = float(fov)
        self.roll = float(roll)
        self.blur = float(blur)

    def basis(self):
        fwd = self.target - self.pos
        n = float(np.linalg.norm(fwd))
        fwd = np.array([0.0, 0.0, -1.0], dtype=np.float32) if n < 1e-6 else fwd / n
        up_hint = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        if abs(float(fwd[1])) > 0.995:
            up_hint = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        right = np.cross(fwd, up_hint)
        right = right / max(float(np.linalg.norm(right)), 1e-6)
        up = np.cross(right, fwd)
        if abs(self.roll) > 1e-4:
            a = math.radians(self.roll)
            c, s = math.cos(a), math.sin(a)
            right, up = right * c + up * s, -right * s + up * c
        return right, up, fwd

    def project_point(self, p, W, H):
        right, up, fwd = self.basis()
        rel = np.array(p, dtype=np.float32) - self.pos
        zc = float(np.dot(rel, fwd))
        if zc <= 0.15:
            return None
        xc = float(np.dot(rel, right))
        yc = float(np.dot(rel, up))
        focal = (H * 0.5) / math.tan(math.radians(clamp(self.fov, 15.0, 110.0) * 0.5))
        return (W * 0.5 + (xc / zc) * focal, H * 0.5 - (yc / zc) * focal, zc, focal)


# ------------------------------------------------------------------ Near-plane & perspective
def _clip_poly_z(poly, zmin=0.18):
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da, db = a[2] - zmin, b[2] - zmin
        if da >= 0 and db >= 0:
            out.append(b)
        elif da >= 0 and db < 0:
            out.append(a + (da / (da - db)) * (b - a))
        elif da < 0 and db >= 0:
            out.append(a + (da / (da - db)) * (b - a))
            out.append(b)
    return out


def _persp_coeffs(dst_pts, src_pts):
    A = []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A = np.array(A, dtype=np.float64)
    B = np.array([c for uv in src_pts for c in uv], dtype=np.float64)
    return np.linalg.solve(A, B)


@functools.lru_cache(maxsize=8)
def _shadow_tex(size=64):
    xs = np.linspace(-1.0, 1.0, size, dtype=np.float32)
    X, Y = np.meshgrid(xs, xs)
    r = np.sqrt(X * X + Y * Y)
    a = np.clip(1.0 - r, 0.0, 1.0)
    a = (a * a * (3.0 - 2.0 * a)) * 0.42
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    arr[:, :, 0] = 16
    arr[:, :, 1] = 18
    arr[:, :, 2] = 28
    arr[:, :, 3] = np.clip(a * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


def _paste_tex_quad(img, bloom_buf, pts2, pil_rgba, emissive, W, H, bw, bh, z_px=None, z_test=None, part_map=None, is_shadow=False):
    xs = [p[0] for p in pts2]
    ys = [p[1] for p in pts2]
    x0 = max(0, int(math.floor(min(xs))))
    y0 = max(0, int(math.floor(min(ys))))
    x1 = min(W, int(math.ceil(max(xs))))
    y1 = min(H, int(math.ceil(max(ys))))
    if x1 <= x0 + 1 or y1 <= y0 + 1:
        return
    tw, th = pil_rgba.size
    dst_local = [(p[0] - x0, p[1] - y0) for p in pts2]
    # pts2 = [BL, BR, TR, TL] -> PIL top-down y=0 at top: TL=(0,0), TR=(tw,0), BR=(tw,th), BL=(0,th)
    src_pts = [(0.0, float(th)), (float(tw), float(th)), (float(tw), 0.0), (0.0, 0.0)]
    try:
        coeffs = _persp_coeffs(dst_local, src_pts)
    except np.linalg.LinAlgError:
        return
    warped = pil_rgba.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, coeffs, Image.BILINEAR)
    if is_shadow and part_map is not None:
        occ = part_map[y0:y1, x0:x1] > 0
        if np.all(occ):
            return
        if np.any(occ):
            wa = np.asarray(warped, dtype=np.uint8).copy()
            wa[occ, 3] = 0
            warped = Image.fromarray(wa, "RGBA")
    elif z_px is not None and z_test is not None:
        z_sub = z_px[y0:y1, x0:x1]
        occ = z_sub < z_test
        if np.all(occ):
            return
        if np.any(occ):
            wa = np.asarray(warped, dtype=np.uint8).copy()
            wa[occ, 3] = 0
            warped = Image.fromarray(wa, "RGBA")
    img.paste(warped, (x0, y0), warped)
    if bloom_buf is not None and emissive > 0.25:
        bx0, by0 = int(x0 * 0.25), int(y0 * 0.25)
        bx1, by1 = max(bx0 + 1, int(x1 * 0.25)), max(by0 + 1, int(y1 * 0.25))
        small = warped.resize((bx1 - bx0, by1 - by0), Image.BILINEAR).convert("RGB")
        bloom_buf.paste(small, (bx0, by0))


class PointLight:
    def __init__(self, pos, color=(255, 210, 140), intensity=1.4, radius=4.5, halo=0.0):
        self.pos = np.array(pos, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32) / 255.0
        self.intensity = float(intensity)
        self.radius = float(radius)
        self.halo = float(halo)


class _PartCtx:
    def __init__(self, sc, pid):
        self.sc = sc
        self.pid = pid
        self.prev = 0

    def __enter__(self):
        self.prev = self.sc._cur_part
        self.sc._cur_part = self.pid
        return self.pid

    def __exit__(self, *exc):
        self.sc._cur_part = self.prev


# ------------------------------------------------------------------ Scene3D
class Scene3D:
    def __init__(self):
        self.quad_batches = []
        self.vnorm_batches = []
        self.smooth_batches = []
        self.col_batches = []
        self.alpha_batches = []
        self.emiss_batches = []
        self.spec_batches = []
        self.two_batches = []
        self.bias_batches = []
        self.part_batches = []
        self.ol_batches = []
        self.ol_col_batches = []
        self._cur_part = 0
        self._next_part = 1
        self.lights = []
        self.tex_quads = []

        # Default daylight 3D toon studio (semi-smooth 3D volume + soft rim light + sleek anti-aliased ink)
        self.sky_top = (232, 234, 240)
        self.sky_bot = (242, 244, 248)
        self.amb_sky = (0.76, 0.78, 0.82)
        self.amb_ground = (0.54, 0.52, 0.56)
        self.sun_dir = np.array([0.58, 0.54, 0.61], dtype=np.float32)
        self.sun_dir /= np.linalg.norm(self.sun_dir)
        self.sun_col = np.array([1.0, 0.99, 0.96], dtype=np.float32)
        self.sun_int = 0.52
        self.fog_col = (234, 236, 242)
        self.fog_start = 24.0
        self.fog_density = 0.015
        self.bloom_strength = 0.10
        self.cel_strength = 0.32  # semi-smooth 3D shading (68% smooth volume + 32% subtle toon band)
        self.rim_strength = 0.18
        self.rim_col = np.array([1.0, 0.98, 0.95], dtype=np.float32)
        self.grade_tint = None
        self.ink_scale = 0.82

    def part(self):
        """Kelompokkan beberapa primitif 3D menjadi satu bagian tubuh utuh (1 siluet outline mulus tanpa garis dalam)."""
        pid = self._next_part
        self._next_part += 1
        return _PartCtx(self, pid)

    def set_sky(self, top, bot, amb_sky=None, amb_ground=None, sun_dir=None, sun_col=None, sun_int=None, fog_col=None, fog_start=None, fog_density=None):
        self.sky_top = tuple(top)
        self.sky_bot = tuple(bot)
        if amb_sky is not None:
            self.amb_sky = tuple(amb_sky)
        if amb_ground is not None:
            self.amb_ground = tuple(amb_ground)
        if sun_dir is not None:
            v = np.array(sun_dir, dtype=np.float32)
            self.sun_dir = v / max(float(np.linalg.norm(v)), 1e-6)
        if sun_col is not None:
            self.sun_col = np.array(sun_col, dtype=np.float32)
        if sun_int is not None:
            self.sun_int = float(sun_int)
        if fog_col is not None:
            self.fog_col = tuple(fog_col)
        if fog_start is not None:
            self.fog_start = float(fog_start)
        if fog_density is not None:
            self.fog_density = float(fog_density)

    def add_light(self, pos, color=(255, 204, 130), intensity=1.4, radius=4.5, halo=0.0):
        self.lights.append(PointLight(pos, color, intensity, radius, halo))

    def _alloc_part(self, outline):
        if self._cur_part > 0:
            return self._cur_part
        if outline:
            pid = self._next_part
            self._next_part += 1
            return pid
        return 0

    def _push(self, verts, colors, alphas=1.0, emissive=0.0, specular=0.0, two_sided=False, bias=0.0,
              vnormals=None, smooth=False, outline=False, outline_w=0.0, outline_col=OUT, part_id=None):
        n = len(verts)
        if n == 0:
            return
        self.quad_batches.append(verts.astype(np.float32, copy=False))
        if vnormals is not None:
            self.vnorm_batches.append(vnormals.astype(np.float32, copy=False))
        else:
            self.vnorm_batches.append(np.zeros((n, 4, 3), dtype=np.float32))
        self.smooth_batches.append(np.full(n, bool(smooth), dtype=bool))
        c = np.asarray(colors, dtype=np.float32)
        c = np.broadcast_to(c / 255.0, (n, 3)).copy() if c.ndim == 1 else c / 255.0
        self.col_batches.append(c)
        self.alpha_batches.append(np.full(n, alphas, dtype=np.float32) if np.isscalar(alphas) else np.asarray(alphas, dtype=np.float32))
        self.emiss_batches.append(np.full(n, emissive, dtype=np.float32) if np.isscalar(emissive) else np.asarray(emissive, dtype=np.float32))
        self.spec_batches.append(np.full(n, specular, dtype=np.float32) if np.isscalar(specular) else np.asarray(specular, dtype=np.float32))
        self.two_batches.append(np.full(n, two_sided, dtype=bool) if isinstance(two_sided, bool) else np.asarray(two_sided, dtype=bool))
        self.bias_batches.append(np.full(n, bias, dtype=np.float32) if np.isscalar(bias) else np.asarray(bias, dtype=np.float32))
        pid = self._alloc_part(outline) if part_id is None else int(part_id)
        self.part_batches.append(np.full(n, pid, dtype=np.int32))
        ol_val = float(outline_w) if outline else 0.0
        self.ol_batches.append(np.full(n, ol_val, dtype=np.float32))
        self.ol_col_batches.append(np.broadcast_to(np.array(outline_col, dtype=np.uint8), (n, 3)).copy())

    def _xform(self, verts, center, rot=None, mat=None):
        if mat is not None:
            verts = verts @ mat.T
        elif rot is not None:
            rx, ry, rz = rot
            if rx or ry or rz:
                verts = verts @ euler_mat(rx, ry, rz).T
        return verts + np.array(center, dtype=np.float32)

    def _xform_n(self, norms, rot=None, mat=None):
        if mat is not None:
            norms = norms @ mat.T
        elif rot is not None:
            rx, ry, rz = rot
            if rx or ry or rz:
                norms = norms @ euler_mat(rx, ry, rz).T
        return norms / np.maximum(np.linalg.norm(norms, axis=-1, keepdims=True), 1e-6)

    def _push_hull(self, verts_out, outline_col=OUT, bias=0.04):
        """Legacy helper dipertahankan untuk kompatibilitas (outline kini ditangani Z-buffer screen-space)."""
        return

    def quad(self, pts, color, alpha=1.0, emissive=0.0, specular=0.0, two_sided=True, bias=0.0):
        self._push(np.array([pts], dtype=np.float32), np.array(color, dtype=np.float32), alpha, emissive, specular, two_sided, bias)

    def textured_quad(self, pts, pil_rgba, emissive=0.85, bias=-0.03, shadow=False):
        self.tex_quads.append((np.array(pts, dtype=np.float32), pil_rgba, float(emissive), float(bias), bool(shadow)))

    def sphere(self, center, radius, color, seg_u=18, seg_v=12, rot=None, mat=None, alpha=1.0,
               emissive=0.0, specular=0.10, bias=0.0, outline=False, outline_w=0.016, outline_col=OUT, hemi=False):
        if isinstance(radius, (tuple, list)):
            rx, ry, rz = [float(v) for v in radius]
        else:
            rx = ry = rz = float(radius)
        if rx <= 0 or ry <= 0 or rz <= 0:
            return
        tpl, tn = _sphere_template(seg_u, seg_v, hemi=hemi)
        verts = self._xform(tpl * np.array([rx, ry, rz], dtype=np.float32), center, rot, mat)
        vn = self._xform_n(tn / np.array([rx, ry, rz], dtype=np.float32), rot, mat)
        self._push(verts, np.array(color, dtype=np.float32), alpha, emissive, specular, False, bias,
                   vnormals=vn, smooth=True, outline=(outline and alpha >= 0.99), outline_w=outline_w, outline_col=outline_col)

    def capsule(self, center, radius, height, color, seg_u=16, seg_cap=5, rot=None, mat=None, alpha=1.0,
                emissive=0.0, specular=0.06, bias=0.0, outline=False, outline_w=0.015, outline_col=OUT, scale_xz=(1.0, 1.0),
                color_bot=None, split_y=0.0):
        r = float(radius)
        h_cyl = max(0.02, float(height) - 2.0 * r)
        sx, sz = float(scale_xz[0]), float(scale_xz[1])
        n_mid = 8 if color_bot is not None else 1
        tpl, tn = _capsule_template(round(r, 4), round(h_cyl, 4), seg_u, seg_cap, n_mid=n_mid)
        verts = self._xform(tpl * np.array([sx, 1.0, sz], dtype=np.float32), center, rot, mat)
        vn = self._xform_n(tn / np.array([sx, 1.0, sz], dtype=np.float32), rot, mat)
        if color_bot is not None:
            bot_mask = (tpl[:, :, 1].mean(axis=1) < float(split_y))[:, None]
            cols = np.where(bot_mask, np.array(color_bot, dtype=np.float32), np.array(color, dtype=np.float32))
        else:
            cols = np.array(color, dtype=np.float32)
        self._push(verts, cols, alpha, emissive, specular, False, bias,
                   vnormals=vn, smooth=True, outline=(outline and alpha >= 0.99), outline_w=outline_w, outline_col=outline_col)

    def cylinder(self, center, radius, height, color, seg_u=12, rot=None, mat=None, alpha=1.0,
                 emissive=0.0, specular=0.05, bias=0.0, outline=False, outline_w=0.012, outline_col=OUT, outline_end=True):
        r, h = float(radius), float(height)
        if r <= 0 or h <= 0:
            return
        tpl, tn = _cylinder_template(seg_u)
        verts = self._xform(tpl * np.array([r, h, r], dtype=np.float32), center, rot, mat)
        vn = self._xform_n(tn, rot, mat)
        self._push(verts, np.array(color, dtype=np.float32), alpha, emissive, specular, False, bias,
                   vnormals=vn, smooth=True, outline=(outline and alpha >= 0.99), outline_w=outline_w, outline_col=outline_col)

    def frustum(self, center, r_bottom, r_top, height, color, seg_u=28, rot=None, mat=None, alpha=1.0,
                emissive=0.0, specular=0.05, bias=0.0, outline=False, outline_w=0.012, outline_col=OUT,
                scale_xz=(1.0, 1.0), outline_end=True, caps=True):
        """Kerucut terpotong vertikal (untuk rok A-line, torso jas, lengan mengerucut)."""
        rb, rt, h = float(r_bottom), float(r_top), float(height)
        if rb <= 0 or rt <= 0 or h <= 0:
            return
        tpl, tn = _frustum_template(round(rb, 4), round(rt, 4), round(h, 4), int(seg_u), caps=bool(caps))
        sx, sz = float(scale_xz[0]), float(scale_xz[1])
        verts = self._xform(tpl * np.array([sx, 1.0, sz], dtype=np.float32), center, rot, mat)
        vn = self._xform_n(tn / np.array([sx, 1.0, sz], dtype=np.float32), rot, mat)
        self._push(verts, np.array(color, dtype=np.float32), alpha, emissive, specular, False, bias,
                   vnormals=vn, smooth=True, outline=(outline and alpha >= 0.99), outline_w=outline_w, outline_col=outline_col)

    def limb(self, p0, p1, radius, color, seg_u=10, outline=True, outline_w=0.012, outline_col=OUT, alpha=1.0, emissive=0.0):
        """Batang silinder 3D halus antar dua titik sendi (lengan/kaki stickman)."""
        self.tapered_limb(p0, p1, radius, radius, color, seg_u=seg_u, outline=outline, outline_w=outline_w,
                          outline_col=outline_col, alpha=alpha, emissive=emissive, caps=False)

    def tapered_limb(self, p0, p1, r0, r1, color, seg_u=16, outline=True, outline_w=0.018, outline_col=OUT,
                     alpha=1.0, emissive=0.0, specular=0.04, outline_end=False, bias=0.0, caps=False):
        """Batang frustum 3D mengerucut halus antar dua sendi (lengan jas/celana kartun chibi)."""
        a = np.array(p0, dtype=np.float32)
        b = np.array(p1, dtype=np.float32)
        d = b - a
        L = float(np.linalg.norm(d))
        if L < 1e-4:
            return
        u = d / L
        hint = np.array([0.0, 0.0, 1.0], dtype=np.float32) if abs(float(u[1])) > 0.95 else np.array([0.0, 1.0, 0.0], dtype=np.float32)
        s1 = np.cross(u, hint); s1 /= max(float(np.linalg.norm(s1)), 1e-6)
        s2 = np.cross(s1, u)
        mat = np.column_stack([s1, u, s2])
        mid = (a + b) * 0.5
        self.frustum(mid, r0, r1, L, color, seg_u=seg_u, mat=mat, alpha=alpha, emissive=emissive,
                     specular=specular, bias=bias, outline=outline, outline_w=outline_w,
                     outline_col=outline_col, outline_end=outline_end, caps=caps)

    def box(self, center, size, color, rot=None, mat=None, alpha=1.0, emissive=0.0, specular=0.0, bias=0.0, outline=False, outline_w=0.014, outline_col=OUT):
        sx, sy, sz = [float(v) for v in size]
        if sx <= 0 or sy <= 0 or sz <= 0:
            return
        verts = self._xform(_FACE_CORNERS * np.array([sx, sy, sz], dtype=np.float32), center, rot, mat)
        c = np.array(color, dtype=np.float32)
        cols = np.broadcast_to(c, (6, 3)).copy() * np.array([[1.0], [0.94], [0.97], [0.97], [1.03], [0.86]], dtype=np.float32)
        self._push(verts, np.clip(cols, 0, 255), alpha, emissive, specular, False, bias,
                   outline=(outline and alpha >= 0.99), outline_w=outline_w, outline_col=outline_col)

    def box_bounds(self, x0, y0, z0, x1, y1, z1, color, **kw):
        self.box(((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), color, **kw)

    def rbox(self, center, size, color, roundness=0.45, seg=2, rot=None, mat=None, alpha=1.0, emissive=0.0, specular=0.05, bias=0.0, outline=False, outline_w=0.014, outline_col=OUT):
        sx, sy, sz = [float(v) for v in size]
        if sx <= 0 or sy <= 0 or sz <= 0:
            return
        tpl, tn = _rbox_template(round(sx, 4), round(sy, 4), round(sz, 4), round(float(roundness), 3), int(seg))
        verts = self._xform(tpl, center, rot, mat)
        vn = self._xform_n(tn, rot, mat)
        self._push(verts, np.array(color, dtype=np.float32), alpha, emissive, specular, False, bias,
                   vnormals=vn, smooth=True, outline=(outline and alpha >= 0.99), outline_w=outline_w, outline_col=outline_col)

    def tiled_plane(self, x0, z0, x1, z1, y, color, tile=1.6, alpha=1.0, emissive=0.0, specular=0.0, bias=0.0, checker=None):
        nx = max(1, int(math.ceil(abs(x1 - x0) / tile)))
        nz = max(1, int(math.ceil(abs(z1 - z0) / tile)))
        xs = np.linspace(min(x0, x1), max(x0, x1), nx + 1, dtype=np.float32)
        zs = np.linspace(min(z0, z1), max(z0, z1), nz + 1, dtype=np.float32)
        X0, Z0 = np.meshgrid(xs[:-1], zs[:-1], indexing="ij")
        X1, Z1 = np.meshgrid(xs[1:], zs[1:], indexing="ij")
        n = nx * nz
        verts = np.empty((n, 4, 3), dtype=np.float32)
        verts[:, 0, 0], verts[:, 0, 1], verts[:, 0, 2] = X0.ravel(), y, Z1.ravel()
        verts[:, 1, 0], verts[:, 1, 1], verts[:, 1, 2] = X1.ravel(), y, Z1.ravel()
        verts[:, 2, 0], verts[:, 2, 1], verts[:, 2, 2] = X1.ravel(), y, Z0.ravel()
        verts[:, 3, 0], verts[:, 3, 1], verts[:, 3, 2] = X0.ravel(), y, Z0.ravel()
        cols = np.broadcast_to(np.array(color, dtype=np.float32), (n, 3)).copy()
        if checker is not None:
            ix, iz = np.meshgrid(np.arange(nx), np.arange(nz), indexing="ij")
            cols[((ix + iz) % 2 == 1).ravel()] = np.array(checker, dtype=np.float32)
        floor_bias = bias + (8.0 - float(y) * 2.0 if y <= 0.1 else 0.0)
        self._push(verts, cols, alpha, emissive, specular, False, floor_bias)

    def tiled_wall_z(self, x0, y0, x1, y1, z, color, normal_z=1, tile=1.5, specular=0.0, bias=0.0):
        nx = max(1, int(math.ceil(abs(x1 - x0) / tile)))
        ny = max(1, int(math.ceil(abs(y1 - y0) / tile)))
        xs = np.linspace(min(x0, x1), max(x0, x1), nx + 1, dtype=np.float32)
        ys = np.linspace(min(y0, y1), max(y0, y1), ny + 1, dtype=np.float32)
        X0, Y0 = np.meshgrid(xs[:-1], ys[:-1], indexing="ij")
        X1, Y1 = np.meshgrid(xs[1:], ys[1:], indexing="ij")
        n = nx * ny
        verts = np.empty((n, 4, 3), dtype=np.float32)
        if normal_z >= 0:
            verts[:, 0] = np.stack([X0.ravel(), Y0.ravel(), np.full(n, z)], 1)
            verts[:, 1] = np.stack([X1.ravel(), Y0.ravel(), np.full(n, z)], 1)
            verts[:, 2] = np.stack([X1.ravel(), Y1.ravel(), np.full(n, z)], 1)
            verts[:, 3] = np.stack([X0.ravel(), Y1.ravel(), np.full(n, z)], 1)
        else:
            verts[:, 0] = np.stack([X1.ravel(), Y0.ravel(), np.full(n, z)], 1)
            verts[:, 1] = np.stack([X0.ravel(), Y0.ravel(), np.full(n, z)], 1)
            verts[:, 2] = np.stack([X0.ravel(), Y1.ravel(), np.full(n, z)], 1)
            verts[:, 3] = np.stack([X1.ravel(), Y1.ravel(), np.full(n, z)], 1)
        self._push(verts, np.array(color, dtype=np.float32), 1.0, 0.0, specular, False, bias)

    def tiled_wall_x(self, z0, y0, z1, y1, x, color, normal_x=1, tile=1.5, specular=0.0, bias=0.0):
        nz = max(1, int(math.ceil(abs(z1 - z0) / tile)))
        ny = max(1, int(math.ceil(abs(y1 - y0) / tile)))
        zs = np.linspace(min(z0, z1), max(z0, z1), nz + 1, dtype=np.float32)
        ys = np.linspace(min(y0, y1), max(y0, y1), ny + 1, dtype=np.float32)
        Z0, Y0 = np.meshgrid(zs[:-1], ys[:-1], indexing="ij")
        Z1, Y1 = np.meshgrid(zs[1:], ys[1:], indexing="ij")
        n = nz * ny
        verts = np.empty((n, 4, 3), dtype=np.float32)
        if normal_x >= 0:
            verts[:, 0] = np.stack([np.full(n, x), Y0.ravel(), Z1.ravel()], 1)
            verts[:, 1] = np.stack([np.full(n, x), Y0.ravel(), Z0.ravel()], 1)
            verts[:, 2] = np.stack([np.full(n, x), Y1.ravel(), Z0.ravel()], 1)
            verts[:, 3] = np.stack([np.full(n, x), Y1.ravel(), Z1.ravel()], 1)
        else:
            verts[:, 0] = np.stack([np.full(n, x), Y0.ravel(), Z0.ravel()], 1)
            verts[:, 1] = np.stack([np.full(n, x), Y0.ravel(), Z1.ravel()], 1)
            verts[:, 2] = np.stack([np.full(n, x), Y1.ravel(), Z1.ravel()], 1)
            verts[:, 3] = np.stack([np.full(n, x), Y1.ravel(), Z0.ravel()], 1)
        self._push(verts, np.array(color, dtype=np.float32), 1.0, 0.0, specular, False, bias)

    def drop_shadow(self, x, y, z, rx=0.35, rz=0.28, alpha=0.28):
        pts = [(x - rx, y + 0.008, z + rz), (x + rx, y + 0.008, z + rz),
               (x + rx, y + 0.008, z - rz), (x - rx, y + 0.008, z - rz)]
        sh_bias = (6.0 - float(y) * 2.0) if y <= 0.08 else -0.02
        self.textured_quad(pts, _shadow_tex(64), emissive=0.0, bias=sh_bias, shadow=True)

    # -------------------------------------------------------------- render
    def _sky_image(self, W, H, cam):
        _, _, fwd = cam.basis()
        pitch_off = float(fwd[1]) * 0.35
        t = np.clip(np.linspace(0.0, 1.0, H, dtype=np.float32) + pitch_off, 0.0, 1.0)[:, None, None]
        top = np.array(self.sky_top, dtype=np.float32)[None, None, :]
        bot = np.array(self.sky_bot, dtype=np.float32)[None, None, :]
        arr = (top * (1.0 - t) + bot * t).astype(np.uint8)
        return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).copy(), "RGB")

    def render(self, cam, W, H, t=0.0, aa=1.5):
        aa = float(aa) if aa else 1.0
        rW = int(round(W * aa)) if aa > 1.01 else W
        rH = int(round(H * aa)) if aa > 1.01 else H
        img = self._sky_image(rW, rH, cam)
        if not self.quad_batches and not self.tex_quads:
            return img.resize((W, H), Image.LANCZOS) if (rW, rH) != (W, H) else img

        verts = np.concatenate(self.quad_batches, axis=0) if self.quad_batches else np.zeros((0, 4, 3), np.float32)
        vnorms = np.concatenate(self.vnorm_batches, axis=0) if self.vnorm_batches else np.zeros((0, 4, 3), np.float32)
        smooths = np.concatenate(self.smooth_batches, axis=0) if self.smooth_batches else np.zeros((0,), bool)
        cols = np.concatenate(self.col_batches, axis=0) if self.col_batches else np.zeros((0, 3), np.float32)
        alphas = np.concatenate(self.alpha_batches, axis=0) if self.alpha_batches else np.zeros((0,), np.float32)
        emiss = np.concatenate(self.emiss_batches, axis=0) if self.emiss_batches else np.zeros((0,), np.float32)
        specs = np.concatenate(self.spec_batches, axis=0) if self.spec_batches else np.zeros((0,), np.float32)
        twos = np.concatenate(self.two_batches, axis=0) if self.two_batches else np.zeros((0,), bool)
        biases = np.concatenate(self.bias_batches, axis=0) if self.bias_batches else np.zeros((0,), np.float32)
        parts = np.concatenate(self.part_batches, axis=0) if self.part_batches else np.zeros((0,), np.int32)
        ols = np.concatenate(self.ol_batches, axis=0) if self.ol_batches else np.zeros((0,), np.float32)
        ol_cols = np.concatenate(self.ol_col_batches, axis=0) if self.ol_col_batches else np.zeros((0, 3), np.uint8)

        right, up, fwd = cam.basis()
        basis = np.column_stack([right, up, fwd])
        rel = verts - cam.pos[None, None, :]
        v_cam = rel @ basis
        vis = v_cam[:, :, 2].max(axis=1) > 0.18

        centers = verts.mean(axis=1)
        normals = np.cross(verts[:, 1] - verts[:, 0], verts[:, 2] - verts[:, 0])
        normals = normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-6)

        to_cam = cam.pos[None, :] - centers
        facing = np.sum(normals * to_cam, axis=1)
        vis &= (twos | (facing > -1e-4))
        flip_n = twos & (facing < 0)
        if np.any(flip_n):
            normals[flip_n] = -normals[flip_n]

        focal = (rH * 0.5) / math.tan(math.radians(clamp(cam.fov, 15.0, 110.0) * 0.5))
        half_w_ndc = (rW * 0.54) / focal
        half_h_ndc = (rH * 0.54) / focal
        z_all_ok = v_cam[:, :, 2].min(axis=1) >= 0.18
        if np.any(vis & z_all_ok):
            idx_ok = np.where(vis & z_all_ok)[0]
            zc = v_cam[idx_ok, :, 2]
            xn = v_cam[idx_ok, :, 0] / zc
            yn = v_cam[idx_ok, :, 1] / zc
            out_f = (
                (xn.max(axis=1) < -half_w_ndc) | (xn.min(axis=1) > half_w_ndc) |
                (yn.max(axis=1) < -half_h_ndc) | (yn.min(axis=1) > half_h_ndc)
            )
            vis[idx_ok[out_f]] = False

        idx = np.where(vis)[0]
        bw, bh = max(8, rW // 4), max(8, rH // 4)
        bloom_buf = Image.new("RGB", (bw, bh), (0, 0, 0)) if self.bloom_strength > 0.01 else None
        bd = ImageDraw.Draw(bloom_buf) if bloom_buf else None

        z_px_full = None
        part_map = None
        ol_w_map = None
        ol_c_map = None

        if len(idx) > 0:
            vw = verts[idx]
            vn_q = vnorms[idx]
            sm_q = smooths[idx]
            vc = v_cam[idx]
            cc = cols[idx]
            aa_arr = alphas[idx]
            ee = emiss[idx]
            ss = specs[idx]
            bb = biases[idx]
            pp = parts[idx]
            oo = ols[idx]
            oc = ol_cols[idx]
            ct = centers[idx]
            nn = normals[idx]

            def _shade(n_arr, pos_arr, c_arr, e_arr, s_arr):
                sky_w = (n_arr[:, 1] * 0.5 + 0.5)[:, None]
                amb = np.array(self.amb_ground, np.float32)[None, :] * (1.0 - sky_w) + np.array(self.amb_sky, np.float32)[None, :] * sky_w
                raw_dot = n_arr @ self.sun_dir
                wrap = np.clip((raw_dot + 0.35) / 1.35, 0.0, 1.0)
                wrap = wrap * wrap * (3.0 - 2.0 * wrap)

                tc_v = cam.pos[None, :] - pos_arr
                dist_v = np.maximum(np.linalg.norm(tc_v, axis=1, keepdims=True), 1e-6)
                vdir = tc_v / dist_v

                if self.cel_strength > 0.01:
                    t_cel = np.clip((raw_dot - 0.10) / 0.09, 0.0, 1.0)
                    t_cel = t_cel * t_cel * (3.0 - 2.0 * t_cel)
                    base_amb = np.array(self.amb_sky, np.float32) * 0.65 + np.array(self.amb_ground, np.float32) * 0.35
                    lit_hi = np.clip(base_amb + self.sun_col * self.sun_int * 0.88, 0.38, 1.02)
                    lit_lo = lit_hi * np.array([0.81, 0.77, 0.79], dtype=np.float32)
                    cel_lit = lit_lo[None, :] * (1.0 - t_cel[:, None]) + lit_hi[None, :] * t_cel[:, None]
                    if np.any(s_arr > 0.02):
                        sh_vec = self.sun_dir[None, :] + vdir
                        sh_vec /= np.maximum(np.linalg.norm(sh_vec, axis=1, keepdims=True), 1e-6)
                        ndoth_c = np.maximum(0.0, np.sum(n_arr * sh_vec, axis=1))
                        hi_c = np.clip((ndoth_c - 0.86) / 0.07, 0.0, 1.0)
                        hi_c = hi_c * hi_c * (3.0 - 2.0 * hi_c) * np.minimum(s_arr, 0.28) * 0.38
                        cel_lit = cel_lit + hi_c[:, None] * self.sun_col[None, :]
                    if self.cel_strength >= 0.99:
                        lit = cel_lit
                    else:
                        smooth_lit = amb + wrap[:, None] * self.sun_col[None, :] * self.sun_int
                        lit = smooth_lit * (1.0 - self.cel_strength) + cel_lit * self.cel_strength
                else:
                    lit = amb + wrap[:, None] * self.sun_col[None, :] * self.sun_int

                if self.rim_strength > 0.01:
                    ndotv = np.clip(np.sum(n_arr * vdir, axis=1), 0.0, 1.0)
                    rim = ((1.0 - ndotv) ** 2.6) * self.rim_strength * (0.35 + 0.65 * wrap)
                    lit += rim[:, None] * self.rim_col[None, :]
                if self.cel_strength < 0.9 and np.any(s_arr > 0.01):
                    sh_vec = self.sun_dir[None, :] + vdir
                    sh_vec /= np.maximum(np.linalg.norm(sh_vec, axis=1, keepdims=True), 1e-6)
                    ndoth_sun = np.maximum(0.0, np.sum(n_arr * sh_vec, axis=1))
                    sp_sun = (ndoth_sun ** 26) * s_arr * self.sun_int * 0.60
                    lit += sp_sun[:, None] * self.sun_col[None, :]

                # Mode PBR Studio Metallic (aktif hanya jika cel_strength <= 0.05, mis. CutawayScene / MechLab3D)
                metal_blend = None
                metal_rgb = None
                if self.cel_strength <= 0.05 and np.any(s_arr > 0.32):
                    ndotv = np.clip(np.sum(n_arr * vdir, axis=1), 0.0, 1.0)
                    refl = 2.0 * ndotv[:, None] * n_arr - vdir
                    rx, ry, rz = refl[:, 0], refl[:, 1], refl[:, 2]
                    # Studio environment map prosedural (langit softbox atas + strip lampu kiri/kanan + horizon navy + lantai abu)
                    up_t = np.clip(ry * 0.5 + 0.5, 0.0, 1.0)
                    env_sky = np.array([0.88, 0.92, 0.98], dtype=np.float32)
                    env_hor = np.array([0.14, 0.18, 0.28], dtype=np.float32)
                    env_flr = np.array([0.42, 0.44, 0.48], dtype=np.float32)
                    env = np.where(
                        (ry >= 0.0)[:, None],
                        env_hor[None, :] * (1.0 - (ry.clip(0.0, 1.0) ** 0.65)[:, None]) + env_sky[None, :] * (ry.clip(0.0, 1.0) ** 0.65)[:, None],
                        env_hor[None, :] * (1.0 - ((-ry).clip(0.0, 1.0) ** 0.8)[:, None]) + env_flr[None, :] * ((-ry).clip(0.0, 1.0) ** 0.8)[:, None],
                    )
                    # 2 softbox strip vertikal kiri & kanan (memberi kilap silinder krom/aluminium khas studio!)
                    strip1 = np.exp(-((rx - 0.52) / 0.16) ** 2) * np.exp(-((ry - 0.25) / 0.55) ** 2)
                    strip2 = np.exp(-((rx + 0.62) / 0.22) ** 2) * np.exp(-((ry - 0.15) / 0.65) ** 2)
                    top_box = np.clip((ry - 0.62) / 0.28, 0.0, 1.0) ** 1.5
                    env = env + (strip1 * 0.95 + strip2 * 0.55 + top_box * 0.65)[:, None] * np.array([1.0, 0.99, 0.97], dtype=np.float32)[None, :]
                    # Fresnel + sharp specular highlight
                    fres = 0.22 + 0.78 * ((1.0 - ndotv) ** 3.2)
                    sh_vec = self.sun_dir[None, :] + vdir
                    sh_vec /= np.maximum(np.linalg.norm(sh_vec, axis=1, keepdims=True), 1e-6)
                    spec_sharp = (np.maximum(0.0, np.sum(n_arr * sh_vec, axis=1)) ** 54) * 1.15
                    metalness = np.clip((s_arr - 0.30) / 0.42, 0.0, 1.0)
                    # Warna logam memantulkan env yang di-tint oleh base color (F0) + highlight putih tajam
                    metal_rgb = c_arr * (0.28 * lit + env * (0.78 + 0.38 * fres[:, None])) + (spec_sharp * metalness)[:, None] * self.sun_col[None, :]
                    metal_blend = metalness[:, None]

                if self.lights:
                    l_scale = 0.28 if self.cel_strength >= 0.9 else 1.0
                    for L in self.lights:
                        dvec = L.pos[None, :] - pos_arr
                        d2 = np.sum(dvec * dvec, axis=1)
                        near = d2 < (L.radius * 3.2) ** 2
                        if not np.any(near):
                            continue
                        dn = np.sqrt(np.maximum(d2[near], 1e-5))
                        ldir = dvec[near] / dn[:, None]
                        ndotl = np.maximum(0.0, np.sum(n_arr[near] * ldir, axis=1))
                        att = L.intensity * l_scale / (1.0 + d2[near] / max(L.radius * L.radius, 0.1))
                        lit[near] += (att * ndotl)[:, None] * L.color[None, :]
                        if self.cel_strength < 0.9 and np.any(s_arr[near] > 0.01):
                            hvec = ldir + vdir[near]
                            hvec /= np.maximum(np.linalg.norm(hvec, axis=1, keepdims=True), 1e-6)
                            ndoth = np.maximum(0.0, np.sum(n_arr[near] * hvec, axis=1))
                            sp = (ndoth ** 22) * s_arr[near] * att * 0.55
                            lit[near] += sp[:, None] * L.color[None, :]

                over_l = np.maximum(0.0, lit - 0.98)
                lit = np.where(lit > 0.98, 0.98 + 0.16 * over_l / (over_l + 0.35), lit)
                shaded = c_arr * lit
                if metal_blend is not None:
                    shaded = shaded * (1.0 - metal_blend) + metal_rgb * metal_blend
                    over_m = np.maximum(0.0, shaded - 0.96)
                    shaded = np.where(shaded > 0.96, 0.96 + 0.14 * over_m / (over_m + 0.35), shaded)
                if np.any(e_arr > 0.0):
                    ew = np.clip(e_arr, 0.0, 1.0)[:, None]
                    em_col = c_arr * (1.0 + np.maximum(0.0, np.minimum(e_arr, 1.5) - 1.0)[:, None] * 0.35)
                    shaded = shaded * (1.0 - ew) + em_col * ew

                fog_amt = np.clip(1.0 - np.exp(-np.maximum(0.0, dist_v[:, 0] - self.fog_start) * self.fog_density), 0.0, 0.88)[:, None]
                fog_c = np.array(self.fog_col, dtype=np.float32)[None, :] / 255.0
                return np.clip((shaded * (1.0 - fog_amt) + fog_c * fog_amt) * 255.0, 0, 255).astype(np.uint8)

            # --- TRUE PER-PIXEL Z-BUFFER RASTERIZER (100% bebas crack / campur-campur antar mesh) ---
            half_w_s, half_h_s = rW * 0.5, rH * 0.5
            z_min_v = vc[:, :, 2].min(axis=1)
            fast_mask = z_min_v >= 0.18
            op_fast = fast_mask & (aa_arr >= 0.99)
            op_clip = (~fast_mask) & (aa_arr >= 0.99)
            trans_mask = aa_arr < 0.99

            tri_x_list, tri_y_list, tri_z_list = [], [], []
            tri_w_list, tri_n_list, tri_q_list = [], [], []

            if np.any(op_fast):
                q_idx = np.where(op_fast)[0]
                v_f = vc[q_idx]
                zf = v_f[:, :, 2]
                sxf = half_w_s + (v_f[:, :, 0] / zf) * focal
                syf = half_h_s - (v_f[:, :, 1] / zf) * focal
                vw_f = vw[q_idx]
                vn_f = np.where(sm_q[q_idx][:, None, None], vn_q[q_idx], nn[q_idx][:, None, :])
                for v0, v1, v2 in ((0, 1, 2), (0, 2, 3)):
                    tri_x_list.append(sxf[:, [v0, v1, v2]])
                    tri_y_list.append(syf[:, [v0, v1, v2]])
                    tri_z_list.append(zf[:, [v0, v1, v2]])
                    tri_w_list.append(vw_f[:, [v0, v1, v2], :])
                    tri_n_list.append(vn_f[:, [v0, v1, v2], :])
                    tri_q_list.append(q_idx)

            if np.any(op_clip):
                clip_tx, clip_ty, clip_tz, clip_tw, clip_tn, clip_tq = [], [], [], [], [], []
                for qi in np.where(op_clip)[0]:
                    clipped = _clip_poly_z(vc[qi], 0.18)
                    if len(clipped) < 3:
                        continue
                    c_arr_p = np.asarray(clipped, dtype=np.float32)
                    c_world = c_arr_p @ basis.T + cam.pos[None, :]
                    c_sx = half_w_s + (c_arr_p[:, 0] / c_arr_p[:, 2]) * focal
                    c_sy = half_h_s - (c_arr_p[:, 1] / c_arr_p[:, 2]) * focal
                    c_sz = c_arr_p[:, 2]
                    n_flat = nn[qi]
                    for k in range(1, len(clipped) - 1):
                        sel = [0, k, k + 1]
                        clip_tx.append(c_sx[sel]); clip_ty.append(c_sy[sel]); clip_tz.append(c_sz[sel])
                        clip_tw.append(c_world[sel])
                        clip_tn.append(np.stack([n_flat, n_flat, n_flat], axis=0))
                        clip_tq.append(qi)
                if clip_tx:
                    tri_x_list.append(np.array(clip_tx, dtype=np.float32))
                    tri_y_list.append(np.array(clip_ty, dtype=np.float32))
                    tri_z_list.append(np.array(clip_tz, dtype=np.float32))
                    tri_w_list.append(np.array(clip_tw, dtype=np.float32))
                    tri_n_list.append(np.array(clip_tn, dtype=np.float32))
                    tri_q_list.append(np.array(clip_tq, dtype=np.int32))

            if tri_x_list:
                tx = np.concatenate(tri_x_list, axis=0)
                ty = np.concatenate(tri_y_list, axis=0)
                tz = np.concatenate(tri_z_list, axis=0)
                tw = np.concatenate(tri_w_list, axis=0)
                tn = np.concatenate(tri_n_list, axis=0)
                t_q = np.concatenate(tri_q_list, axis=0)

                area = (tx[:, 1] - tx[:, 0]) * (ty[:, 2] - ty[:, 0]) - (ty[:, 1] - ty[:, 0]) * (tx[:, 2] - tx[:, 0])
                valid = np.abs(area) > 0.15
                if np.any(valid):
                    tx, ty, tz, tw, tn, t_q, area = (
                        tx[valid], ty[valid], tz[valid], tw[valid], tn[valid], t_q[valid], area[valid]
                    )
                    # Pastikan orientasi area > 0 agar uji tepi konsisten
                    neg = area < 0.0
                    if np.any(neg):
                        tx[neg] = tx[neg][:, [0, 2, 1]]
                        ty[neg] = ty[neg][:, [0, 2, 1]]
                        tz[neg] = tz[neg][:, [0, 2, 1]]
                        tw[neg] = tw[neg][:, [0, 2, 1], :]
                        tn[neg] = tn[neg][:, [0, 2, 1], :]
                        area[neg] = -area[neg]

                    # Bias mikro khusus tie-breaking coplanar (tanpa merusak Z-buffer nyata)
                    tb_micro = np.clip(bb[t_q], -0.08, 0.08) * 0.18
                    inv_z = 1.0 / np.maximum(tz + tb_micro[:, None], 0.14)
                    inv_a = 1.0 / area

                    bx0 = np.clip(np.floor(tx.min(axis=1)).astype(np.int32), 0, rW - 1)
                    bx1 = np.clip(np.ceil(tx.max(axis=1)).astype(np.int32), 0, rW - 1)
                    by0 = np.clip(np.floor(ty.min(axis=1)).astype(np.int32), 0, rH - 1)
                    by1 = np.clip(np.ceil(ty.max(axis=1)).astype(np.int32), 0, rH - 1)

                    iz_buf = np.zeros((rH, rW), dtype=np.float32)
                    tid_buf = np.full((rH, rW), -1, dtype=np.int32)
                    all_gx = np.arange(rW, dtype=np.float32) + 0.5
                    all_gy = np.arange(rH, dtype=np.float32) + 0.5

                    bx0_l, bx1_l, by0_l, by1_l = bx0.tolist(), bx1.tolist(), by0.tolist(), by1.tolist()
                    x0_l, x1_l, x2_l = tx[:, 0].tolist(), tx[:, 1].tolist(), tx[:, 2].tolist()
                    y0_l, y1_l, y2_l = ty[:, 0].tolist(), ty[:, 1].tolist(), ty[:, 2].tolist()
                    iz0_l, iz1_l, iz2_l = inv_z[:, 0].tolist(), inv_z[:, 1].tolist(), inv_z[:, 2].tolist()
                    ia_l = inv_a.tolist()

                    for ti in range(len(t_q)):
                        x0i, x1i, y0i, y1i = bx0_l[ti], bx1_l[ti], by0_l[ti], by1_l[ti]
                        if x1i < x0i or y1i < y0i:
                            continue
                        gx = all_gx[x0i:x1i + 1]
                        gy = all_gy[y0i:y1i + 1]
                        ax, ay = x0_l[ti], y0_l[ti]
                        bx, by = x1_l[ti], y1_l[ti]
                        cx, cy = x2_l[ti], y2_l[ti]
                        e0 = (cx - bx) * (gy - by)[:, None] - (cy - by) * (gx - bx)[None, :]
                        e1 = (ax - cx) * (gy - cy)[:, None] - (ay - cy) * (gx - cx)[None, :]
                        e2 = (bx - ax) * (gy - ay)[:, None] - (by - ay) * (gx - ax)[None, :]
                        m = (e0 >= -1e-3) & (e1 >= -1e-3) & (e2 >= -1e-3)
                        if not m.any():
                            continue
                        ia = ia_l[ti]
                        iz_p = (e0 * iz0_l[ti] + e1 * iz1_l[ti] + e2 * iz2_l[ti]) * ia
                        sub_iz = iz_buf[y0i:y1i + 1, x0i:x1i + 1]
                        win = m & (iz_p > sub_iz)
                        if win.any():
                            sub_iz[win] = iz_p[win]
                            tid_buf[y0i:y1i + 1, x0i:x1i + 1][win] = ti

                    py, px = np.nonzero(tid_buf >= 0)
                    if len(py) > 0:
                        ti_hit = tid_buf[py, px]
                        gx_p = px.astype(np.float32) + 0.5
                        gy_p = py.astype(np.float32) + 0.5
                        ax_p, bx_p, cx_p = tx[ti_hit, 0], tx[ti_hit, 1], tx[ti_hit, 2]
                        ay_p, by_p, cy_p = ty[ti_hit, 0], ty[ti_hit, 1], ty[ti_hit, 2]
                        ia_p = inv_a[ti_hit]
                        w0 = np.clip(((cx_p - bx_p) * (gy_p - by_p) - (cy_p - by_p) * (gx_p - bx_p)) * ia_p, 0.0, 1.0)
                        w1 = np.clip(((ax_p - cx_p) * (gy_p - cy_p) - (ay_p - cy_p) * (gx_p - cx_p)) * ia_p, 0.0, 1.0)
                        w2 = np.clip(1.0 - w0 - w1, 0.0, 1.0)
                        u0 = w0 / np.maximum(tz[ti_hit, 0], 0.18)
                        u1 = w1 / np.maximum(tz[ti_hit, 1], 0.18)
                        u2 = w2 / np.maximum(tz[ti_hit, 2], 0.18)
                        usum = np.maximum(u0 + u1 + u2, 1e-6)
                        b0 = (u0 / usum)[:, None]
                        b1 = (u1 / usum)[:, None]
                        b2 = (u2 / usum)[:, None]

                        n_px = b0 * tn[ti_hit, 0] + b1 * tn[ti_hit, 1] + b2 * tn[ti_hit, 2]
                        n_px /= np.maximum(np.linalg.norm(n_px, axis=1, keepdims=True), 1e-6)
                        p_px = b0 * tw[ti_hit, 0] + b1 * tw[ti_hit, 1] + b2 * tw[ti_hit, 2]
                        q_ti = t_q[ti_hit]
                        px_rgb = _shade(n_px, p_px, cc[q_ti], ee[q_ti], ss[q_ti])

                        img_arr = np.asarray(img, dtype=np.uint8).copy()
                        img_arr[py, px] = px_rgb
                        img = Image.fromarray(img_arr, "RGB")

                        z_px_full = np.full((rH, rW), np.inf, dtype=np.float32)
                        z_px_full[py, px] = 1.0 / usum
                        part_map = np.zeros((rH, rW), dtype=np.int32)
                        part_map[py, px] = pp[q_ti]
                        ol_w_map = np.zeros((rH, rW), dtype=np.float32)
                        ol_w_map[py, px] = oo[q_ti]
                        ol_c_map = np.zeros((rH, rW, 3), dtype=np.uint8)
                        ol_c_map[py, px] = oc[q_ti]

                        if bloom_buf is not None:
                            em_hit = (ee[q_ti] > 0.15) & (ee[q_ti] < 0.99)
                            if np.any(em_hit):
                                em_arr = np.zeros((rH, rW, 3), dtype=np.uint8)
                                em_v = np.minimum(1.0, ee[q_ti[em_hit]])[:, None]
                                em_arr[py[em_hit], px[em_hit]] = np.clip(px_rgb[em_hit].astype(np.float32) * em_v, 0, 255).astype(np.uint8)
                                em_sm = Image.fromarray(em_arr, "RGB").resize((bw, bh), Image.BILINEAR)
                                bloom_buf = Image.fromarray(np.clip(np.asarray(bloom_buf, np.uint16) + np.asarray(em_sm, np.uint16), 0, 255).astype(np.uint8), "RGB")
                                bd = ImageDraw.Draw(bloom_buf)

            # --- Textured quads (drop shadow, wajah 2D, jas/dasi 2D, poster) dengan uji oklusi Z-buffer ---
            tex_items = []
            for tpts, tpimg, tem, tbi, is_sh in self.tex_quads:
                tvc = (tpts - cam.pos[None, :]) @ basis
                if tvc[:, 2].min() < 0.18:
                    continue
                td = float(tvc[:, 2].mean()) + tbi
                z_test_t = float(tvc[:, 2].mean()) + 0.06 if is_sh else float(tvc[:, 2].min()) - 0.032
                sx = half_w_s + (tvc[:, 0] / tvc[:, 2]) * focal
                sy = half_h_s - (tvc[:, 1] / tvc[:, 2]) * focal
                tex_items.append((td, z_test_t, list(zip(sx.tolist(), sy.tolist())), tpimg, tem, is_sh))
            tex_items.sort(key=lambda x: -x[0])
            for _, z_test_t, dpts, tpimg, tem, is_sh in tex_items:
                _paste_tex_quad(img, bloom_buf, dpts, tpimg, tem, rW, rH, bw, bh,
                                z_px=z_px_full, z_test=z_test_t if z_px_full is not None else None,
                                part_map=part_map, is_shadow=is_sh)

            # --- UNIFIED SCREEN-SPACE COMIC INK OUTLINE (tipis-rapi, seragam, 0 crack; ink_scale=0 untuk tanpa garis) ---
            if self.ink_scale > 0.01 and part_map is not None and ol_w_map is not None and np.any(ol_w_map > 0.001):
                has_ol = ol_w_map > 0.001
                edge = np.zeros((rH, rW), dtype=bool)
                # 1. Batas 1-piksel antar part_id (tipis presisi, bukan 2-piksel gemuk)
                p_r = part_map[:, :-1] != part_map[:, 1:]
                o_r = has_ol[:, :-1] | has_ol[:, 1:]
                edge[:, :-1] |= (p_r & o_r)

                p_d = part_map[:-1, :] != part_map[1:, :]
                o_d = has_ol[:-1, :] | has_ol[1:, :]
                edge[:-1, :] |= (p_d & o_d)

                # 2. Lipatan kedalaman besar dalam part yang sama (mis. lengan melipat di depan badan)
                if z_px_full is not None:
                    z_ok = np.isfinite(z_px_full)
                    z_fin = np.where(z_ok, z_px_full, 0.0)
                    dz_r = np.abs(z_fin[:, :-1] - z_fin[:, 1:]) > 0.115
                    edge[:, :-1] |= ((~p_r) & has_ol[:, :-1] & has_ol[:, 1:] & z_ok[:, :-1] & z_ok[:, 1:] & dz_r)

                    dz_d = np.abs(z_fin[:-1, :] - z_fin[1:, :]) > 0.115
                    edge[:-1, :] |= ((~p_d) & has_ol[:-1, :] & has_ol[1:, :] & z_ok[:-1, :] & z_ok[1:, :] & dz_d)

                if np.any(edge):
                    # Pisahkan siluet luar (tegas rapi) vs garis dalam antar-part (lebih tipis & lembut)
                    bg_r = (part_map[:, :-1] == 0) ^ (part_map[:, 1:] == 0)
                    bg_d = (part_map[:-1, :] == 0) ^ (part_map[1:, :] == 0)
                    sil_edge = np.zeros((rH, rW), dtype=bool)
                    sil_edge[:, :-1] |= (edge[:, :-1] & bg_r)
                    sil_edge[:-1, :] |= (edge[:-1, :] & bg_d)
                    in_edge = edge & (~sil_edge)

                    ey, ex = np.nonzero(edge & has_ol)
                    if len(ey) > 0:
                        px_rad_arr = (ol_w_map[ey, ex] * focal / np.maximum(z_px_full[ey, ex], 0.25)) * float(self.ink_scale) * 0.30
                        rad_f = float(np.clip(np.median(px_rad_arr), 0.65, max(1.25, rH * 0.0020)))
                    else:
                        rad_f = max(0.75, rH * 0.0014)

                    # Dilasi halus untuk siluet luar (1px tambahan hanya jika rad_f >= 1.15)
                    def _dilate(mask_in, r_val):
                        ri = int(math.floor(r_val))
                        if ri < 1:
                            return mask_in
                        out_d = np.zeros((rH, rW), dtype=bool)
                        r2_lim = (r_val - 0.12) ** 2
                        for dy in range(-ri, ri + 1):
                            for dx in range(-ri, ri + 1):
                                if dx * dx + dy * dy > r2_lim:
                                    continue
                                sy0, sy1 = max(0, dy), rH + min(0, dy)
                                sx0, sx1 = max(0, dx), rW + min(0, dx)
                                ty0, ty1 = max(0, -dy), rH + min(0, -dy)
                                tx0, tx1 = max(0, -dx), rW + min(0, -dx)
                                out_d[sy0:sy1, sx0:sx1] |= mask_in[ty0:ty1, tx0:tx1]
                        return out_d

                    sil_d = _dilate(sil_edge, rad_f)
                    in_d = _dilate(in_edge, max(0.5, rad_f * 0.68))

                    # Anti-aliasing halus tanpa tangga piksel (soft stroke seperti vektor)
                    sil_a = np.asarray(
                        Image.fromarray((sil_d.astype(np.uint8) * 255), "L").filter(ImageFilter.GaussianBlur(radius=0.72)),
                        dtype=np.float32,
                    ) / 255.0
                    in_a = np.asarray(
                        Image.fromarray((in_d.astype(np.uint8) * 255), "L").filter(ImageFilter.GaussianBlur(radius=0.68)),
                        dtype=np.float32,
                    ) / 255.0
                    ma = np.maximum(
                        np.clip((sil_a - 0.06) / 0.78, 0.0, 1.0) * 0.84,
                        np.clip((in_a - 0.08) / 0.80, 0.0, 1.0) * 0.56,
                    )[:, :, None]
                    ink_rgb = np.array((36, 34, 44), dtype=np.float32)[None, None, :]
                    img_f = np.asarray(img, dtype=np.float32)
                    img = Image.fromarray(np.clip(img_f * (1.0 - ma) + ink_rgb * ma, 0, 255).astype(np.uint8), "RGB")

            # --- Poligon transparan (kaca, partikel, efek alpha) ---
            if np.any(trans_mask):
                t_idx = np.where(trans_mask)[0]
                t_rgb = _shade(nn[t_idx], ct[t_idx], cc[t_idx], ee[t_idx], ss[t_idx])
                t_a = np.clip(aa_arr[t_idx] * 255.0, 0, 255).astype(np.uint8)
                t_depths = vc[t_idx, :, 2].mean(axis=1) + bb[t_idx]
                draw_rgb = ImageDraw.Draw(img, "RGBA")
                for k in np.argsort(-t_depths):
                    qi = t_idx[k]
                    if fast_mask[qi]:
                        zc_q = vc[qi, :, 2]
                        xs_q = half_w_s + (vc[qi, :, 0] / zc_q) * focal
                        ys_q = half_h_s - (vc[qi, :, 1] / zc_q) * focal
                        pts2 = [(float(xs_q[j]), float(ys_q[j])) for j in range(4)]
                    else:
                        clipped = _clip_poly_z(vc[qi], 0.18)
                        if len(clipped) < 3:
                            continue
                        pts2 = [(half_w_s + (p[0] / p[2]) * focal, half_h_s - (p[1] / p[2]) * focal) for p in clipped]
                    r, g, b = int(t_rgb[k, 0]), int(t_rgb[k, 1]), int(t_rgb[k, 2])
                    al = int(t_a[k])
                    draw_rgb.polygon(pts2, fill=(r, g, b, al))
                    if bd is not None and 0.15 < float(ee[qi]) < 0.99:
                        em_v = min(1.0, float(ee[qi]) * (al / 255.0))
                        br, bg, bb_c = int(r * em_v), int(g * em_v), int(b * em_v)
                        if br + bg + bb_c > 24:
                            bd.polygon([(x * 0.25, y * 0.25) for x, y in pts2], fill=(br, bg, bb_c))

        if bd is not None:
            for L in self.lights:
                if L.halo <= 0.01:
                    continue
                pr = cam.project_point(L.pos, rW, rH)
                if pr is None:
                    continue
                lx, ly, lz, lf = pr
                rad_px = (L.halo / lz) * lf * 0.25
                if rad_px < 1.0:
                    continue
                cx, cy = lx * 0.25, ly * 0.25
                lc = tuple(int(clamp(c * 255.0 * min(1.4, L.intensity * 0.5), 0, 255)) for c in L.color)
                bd.ellipse([cx - rad_px, cy - rad_px, cx + rad_px, cy + rad_px], fill=lc)

        if (rW, rH) != (W, H):
            img = img.resize((W, H), Image.LANCZOS)

        if bloom_buf is not None and self.bloom_strength > 0.01:
            glow = bloom_buf.filter(ImageFilter.GaussianBlur(radius=max(3, int(W * 0.011))))
            glow = glow.resize((W, H), Image.BILINEAR)
            arr_i = np.asarray(img, dtype=np.float32)
            arr_g = np.asarray(glow, dtype=np.float32) * self.bloom_strength
            img = Image.fromarray(np.clip(arr_i + arr_g, 0, 255).astype(np.uint8), "RGB")

        if self.grade_tint is not None:
            tcol, ta = self.grade_tint
            arr = np.asarray(img, dtype=np.float32)
            tc_arr = np.array(tcol, dtype=np.float32)[None, None, :]
            img = Image.fromarray(np.clip(arr * (1.0 - ta) + tc_arr * ta, 0, 255).astype(np.uint8), "RGB")

        if cam.blur > 0.15:
            img = img.filter(ImageFilter.GaussianBlur(radius=min(12.0, cam.blur)))

        return img
