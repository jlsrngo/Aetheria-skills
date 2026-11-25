# -*- coding: utf-8 -*-
"""
voxel.py - inti mesin gambar 3D Voxel / Low-Poly Diorama untuk VoxelVerse.

Sistem koordinat (tangan-kanan, +Y ke atas):
  * y = 0.0 -> lantai dunia (kaki tokoh berdiri di y=0; +Y ke atas)
  * x = 0.0 -> tengah panggung; +X ke kanan
  * z = 0.0 -> tengah panggung; +Z menuju kamera depan default

Semua rendering dilakukan murni dengan NumPy + Pillow (tanpa WebGL/GPU eksternal):
  * Cam3D     : kamera perspektif penuh (pos, target, fov, roll, blur/DOF)
  * Scene3D   : batching quad 3D, backface + frustum culling, near-plane clipping,
                pencahayaan hemisphere + matahari + PointLight dinamis + specular + kabut,
                refleksi jalan basah (wet_ground), textured quad perspektif, bloom glow,
                hujan/salju 3D, serta efek layar sinematik.
"""
import math, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "assets", "fonts"))

# ------------------------------------------------------------------ palet dasar
OUT = (24, 24, 34)
PUTIH = (255, 255, 255)
KRIM = (248, 238, 222)
HITAM = (28, 30, 38)
MERAH = (224, 68, 68)
MERAH_TUA = (164, 42, 48)
PIPI = (248, 152, 160)
BIRU = (54, 118, 214)
BIRU_TUA = (32, 62, 138)
BIRU_MUDA = (162, 206, 245)
TEAL = (64, 128, 136)
TEAL_TUA = (42, 88, 96)
PINK = (240, 142, 174)
PINK_TUA = (204, 98, 136)
KUNING = (255, 208, 72)
ORANYE = (232, 118, 48)
HIJAU = (88, 178, 102)
HIJAU_TUA = (50, 118, 66)
COKLAT = (156, 102, 64)
COKLAT_TUA = (104, 66, 42)
KAYU = (204, 156, 110)
KAYU_TUA = (154, 112, 74)
UNGU = (138, 114, 212)
UNGU_TUA = (84, 68, 142)
NAVY = (36, 48, 96)
ABU = (192, 198, 210)
ABU_TUA = (98, 104, 120)
KULIT = (255, 222, 194)
BATA = (166, 76, 54)
BATA_TUA = (122, 54, 40)


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
    """Interpolasi kurva 3D halus melalui daftar titik [(x,y,z), ...], u in [0, 1]."""
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
    """name: 'judul' (Fredoka), 'teks' (Nunito), 'bulat' (Baloo 2), 'seru' (Bungee), 'kode' (monospace)."""
    if name == "kode":
        for cand in (
            os.path.join(FONT_DIR, "JetBrainsMono-Bold.ttf"),
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
    """Matriks rotasi lokal->dunia (urut Z lalu X lalu Y)."""
    m = np.eye(3, dtype=np.float32)
    if ry:
        m = m @ rot_y(ry)
    if rx:
        m = m @ rot_x(rx)
    if rz:
        m = m @ rot_z(rz)
    return m


# ------------------------------------------------------------------ unit cube (strict outward normals)
_CUBE_V = np.array([
    [-0.5, -0.5, -0.5],  # 0
    [+0.5, -0.5, -0.5],  # 1
    [+0.5, +0.5, -0.5],  # 2
    [-0.5, +0.5, -0.5],  # 3
    [-0.5, -0.5, +0.5],  # 4
    [+0.5, -0.5, +0.5],  # 5
    [+0.5, +0.5, +0.5],  # 6
    [-0.5, +0.5, +0.5],  # 7
], dtype=np.float32)

# 6 faces: front(+Z), back(-Z), right(+X), left(-X), top(+Y), bottom(-Y)
_CUBE_F = np.array([
    [4, 5, 6, 7],
    [1, 0, 3, 2],
    [5, 1, 2, 6],
    [0, 4, 7, 3],
    [7, 6, 2, 3],
    [0, 1, 5, 4],
], dtype=np.int32)

_FACE_CORNERS = _CUBE_V[_CUBE_F]  # (6, 4, 3)

# Self-check outward normals on load
def _verify_cube_normals():
    centers = _FACE_CORNERS.mean(axis=1)
    normals = np.cross(_FACE_CORNERS[:, 1] - _FACE_CORNERS[:, 0], _FACE_CORNERS[:, 2] - _FACE_CORNERS[:, 0])
    assert np.all(np.sum(normals * centers, axis=1) > 0.1), "Unit cube normals must point outward!"


_verify_cube_normals()


@functools.lru_cache(maxsize=512)
def _rbox_template(sx, sy, sz, roundness, seg):
    """Bangun quad grid balok bersudut tumpul/chamfer halus dengan normal keluar yang terjamin."""
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
        face_grid(kx, ky, +hz, (0, 1, 2)),                # +Z
        face_grid(kx, ky, -hz, (0, 1, 2), flip_u=True),   # -Z
        face_grid(kz, ky, +hx, (2, 1, 0), flip_u=True),   # +X
        face_grid(kz, ky, -hx, (2, 1, 0)),                # -X
        face_grid(kx, kz, +hy, (0, 2, 1), flip_v=True),   # +Y
        face_grid(kx, kz, -hy, (0, 2, 1)),                # -Y
    ], axis=0)

    inner_lim = np.array([max(0.0, hx - r), max(0.0, hy - r), max(0.0, hz - r)], dtype=np.float32)
    inner = np.clip(faces, -inner_lim, inner_lim)
    delta = faces - inner
    dnorm = np.linalg.norm(delta, axis=-1, keepdims=True)
    v_round = np.where(dnorm > 1e-6, inner + delta / np.maximum(dnorm, 1e-6) * r, faces)
    return v_round.astype(np.float32)


def _verify_rbox_normals():
    for sg in (1, 2):
        vr = _rbox_template(1.0, 1.0, 1.0, 0.35, sg)
        centers = vr.mean(axis=1)
        normals = np.cross(vr[:, 1] - vr[:, 0], vr[:, 2] - vr[:, 0])
        normals = normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-8)
        assert np.all(np.sum(normals * centers, axis=1) > 0.1), f"rbox seg={sg} normals must point outward!"


_verify_rbox_normals()


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
        if n < 1e-6:
            fwd = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        else:
            fwd = fwd / n
        up_hint = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        if abs(float(fwd[1])) > 0.995:
            up_hint = np.array([0.0, 0.0, -1.0], dtype=np.float32)
        right = np.cross(fwd, up_hint)
        rn = float(np.linalg.norm(right))
        right = right / max(rn, 1e-6)
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


# ------------------------------------------------------------------ Near-plane & perspective helpers
def _clip_poly_z(poly, zmin=0.18):
    """Sutherland-Hodgman clip 3D polygon in camera space against z >= zmin."""
    out = []
    n = len(poly)
    for i in range(n):
        a = poly[i]
        b = poly[(i + 1) % n]
        da = a[2] - zmin
        db = b[2] - zmin
        if da >= 0 and db >= 0:
            out.append(b)
        elif da >= 0 and db < 0:
            t = da / (da - db)
            out.append(a + t * (b - a))
        elif da < 0 and db >= 0:
            t = da / (da - db)
            out.append(a + t * (b - a))
            out.append(b)
    return out


def _persp_coeffs(dst_pts, src_pts):
    """Koefisien transformasi perspektif PIL (8 angka) dari src ke dst."""
    A = []
    for (x, y), (u, v) in zip(dst_pts, src_pts):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    A = np.array(A, dtype=np.float64)
    B = np.array([c for uv in src_pts for c in uv], dtype=np.float64)
    return np.linalg.solve(A, B)


# ------------------------------------------------------------------ PointLight
class PointLight:
    def __init__(self, pos, color=(255, 200, 120), intensity=1.6, radius=4.5, halo=0.0):
        self.pos = np.array(pos, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32) / 255.0
        self.intensity = float(intensity)
        self.radius = float(radius)
        self.halo = float(halo)


# ------------------------------------------------------------------ Scene3D
class Scene3D:
    def __init__(self):
        self.quad_batches = []   # list of (N, 4, 3) arrays
        self.col_batches = []    # list of (N, 3) float32 0..1
        self.alpha_batches = []  # list of (N,) float32
        self.emiss_batches = []  # list of (N,) float32
        self.spec_batches = []   # list of (N,) float32
        self.two_batches = []    # list of (N,) bool
        self.bias_batches = []   # list of (N,) float32
        self.refl_batches = []   # list of (N,) bool
        self.lights = []
        self.tex_quads = []      # list of (pts4x3, pil_rgba, emissive, bias)

        # Lingkungan & pencahayaan default
        self.sky_top = (122, 190, 248)
        self.sky_bot = (204, 232, 252)
        self.amb_sky = (0.42, 0.48, 0.56)
        self.amb_ground = (0.24, 0.22, 0.22)
        self.sun_dir = np.array([0.45, 0.80, 0.38], dtype=np.float32)
        self.sun_dir /= np.linalg.norm(self.sun_dir)
        self.sun_col = np.array([1.0, 0.96, 0.88], dtype=np.float32)
        self.sun_int = 0.65
        self.fog_col = (195, 220, 242)
        self.fog_start = 18.0
        self.fog_density = 0.032
        self.wet_ground = False
        self.wet_strength = 0.24
        self.bloom_strength = 0.40
        self.grade_tint = None   # (col, alpha 0..1)

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

    def add_light(self, pos, color=(255, 196, 115), intensity=1.5, radius=4.5, halo=0.0):
        self.lights.append(PointLight(pos, color, intensity, radius, halo))

    def _push(self, verts, colors, alphas=1.0, emissive=0.0, specular=0.0, two_sided=False, bias=0.0, cast_refl=False):
        n = len(verts)
        if n == 0:
            return
        self.quad_batches.append(verts.astype(np.float32, copy=False))
        c = np.asarray(colors, dtype=np.float32)
        if c.ndim == 1:
            c = np.broadcast_to(c / 255.0, (n, 3)).copy()
        else:
            c = c / 255.0
        self.col_batches.append(c)
        self.alpha_batches.append(np.full(n, alphas, dtype=np.float32) if np.isscalar(alphas) else np.asarray(alphas, dtype=np.float32))
        self.emiss_batches.append(np.full(n, emissive, dtype=np.float32) if np.isscalar(emissive) else np.asarray(emissive, dtype=np.float32))
        self.spec_batches.append(np.full(n, specular, dtype=np.float32) if np.isscalar(specular) else np.asarray(specular, dtype=np.float32))
        self.two_batches.append(np.full(n, two_sided, dtype=bool) if isinstance(two_sided, bool) else np.asarray(two_sided, dtype=bool))
        self.bias_batches.append(np.full(n, bias, dtype=np.float32) if np.isscalar(bias) else np.asarray(bias, dtype=np.float32))
        self.refl_batches.append(np.full(n, cast_refl, dtype=bool) if isinstance(cast_refl, bool) else np.asarray(cast_refl, dtype=bool))

    def quad(self, pts, color, alpha=1.0, emissive=0.0, specular=0.0, two_sided=True, bias=0.0, cast_refl=False):
        v = np.array([pts], dtype=np.float32)
        self._push(v, np.array(color, dtype=np.float32), alpha, emissive, specular, two_sided, bias, cast_refl)

    def textured_quad(self, pts, pil_rgba, emissive=1.0, bias=-0.03):
        self.tex_quads.append((np.array(pts, dtype=np.float32), pil_rgba, float(emissive), float(bias)))

    def box(self, center, size, color, rot=None, mat=None, alpha=1.0, emissive=0.0, specular=0.0, bias=0.0, cast_refl=False, face_shade=None):
        """Tambah balok 3D berpusat di `center`, ukuran `(sx, sy, sz)`."""
        sx, sy, sz = size
        if sx <= 0 or sy <= 0 or sz <= 0:
            return
        verts = _FACE_CORNERS * np.array([sx, sy, sz], dtype=np.float32)
        if mat is not None:
            verts = verts @ mat.T
        elif rot is not None:
            rx, ry, rz = rot
            if rx or ry or rz:
                verts = verts @ euler_mat(rx, ry, rz).T
        verts = verts + np.array(center, dtype=np.float32)
        c = np.array(color, dtype=np.float32)
        cols = np.broadcast_to(c, (6, 3)).copy()
        if face_shade is not None:
            cols *= np.asarray(face_shade, dtype=np.float32)[:, None]
        else:
            # Variasi halus sisi balok voxel agar siluet langsung terbaca
            cols *= np.array([[1.0], [0.92], [0.96], [0.96], [1.04], [0.85]], dtype=np.float32)
        cols = np.clip(cols, 0, 255)
        self._push(verts, cols, alpha, emissive, specular, False, bias, cast_refl)

    def box_bounds(self, x0, y0, z0, x1, y1, z1, color, **kw):
        self.box(((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5), (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), color, **kw)

    def rbox(self, center, size, color, roundness=0.45, seg=2, rot=None, mat=None, alpha=1.0, emissive=0.0, specular=0.0, bias=0.0, cast_refl=False):
        """Tambah balok 3D bersudut membulat halus berpusat di `center`, ukuran `(sx, sy, sz)`."""
        sx, sy, sz = float(size[0]), float(size[1]), float(size[2])
        if sx <= 0 or sy <= 0 or sz <= 0:
            return
        verts = _rbox_template(round(sx, 4), round(sy, 4), round(sz, 4), round(float(roundness), 3), int(seg))
        if mat is not None:
            verts = verts @ mat.T
        elif rot is not None:
            rx, ry, rz = rot
            if rx or ry or rz:
                verts = verts @ euler_mat(rx, ry, rz).T
        verts = verts + np.array(center, dtype=np.float32)
        self._push(verts, np.array(color, dtype=np.float32), alpha, emissive, specular, False, bias, cast_refl)

    def ngon_3d(self, pts_list, color, alpha=1.0, emissive=0.0, specular=0.0, two_sided=False, bias=0.0):
        """Pecah poligon 3D cembung N-sisi menjadi batch quad untuk mata oval, pipi, senyum, dan lensa."""
        n = len(pts_list)
        if n < 3:
            return
        p0 = pts_list[0]
        quads = []
        i = 1
        while i + 1 < n:
            if i + 2 < n:
                quads.append([p0, pts_list[i], pts_list[i + 1], pts_list[i + 2]])
                i += 2
            else:
                quads.append([p0, pts_list[i], pts_list[i + 1], pts_list[i + 1]])
                i += 1
        if quads:
            self._push(np.array(quads, dtype=np.float32), np.array(color, dtype=np.float32), alpha, emissive, specular, two_sided, bias, False)

    def tiled_plane(self, x0, z0, x1, z1, y, color, tile=1.6, alpha=1.0, emissive=0.0, specular=0.0, bias=0.0, checker=None):
        """Bidang horizontal terbagi tile agar Painter's sort rapi tanpa tumpang tindih."""
        nx = max(1, int(math.ceil(abs(x1 - x0) / tile)))
        nz = max(1, int(math.ceil(abs(z1 - z0) / tile)))
        xs = np.linspace(min(x0, x1), max(x0, x1), nx + 1, dtype=np.float32)
        zs = np.linspace(min(z0, z1), max(z0, z1), nz + 1, dtype=np.float32)
        X0, Z0 = np.meshgrid(xs[:-1], zs[:-1], indexing="ij")
        X1, Z1 = np.meshgrid(xs[1:], zs[1:], indexing="ij")
        n = nx * nz
        verts = np.empty((n, 4, 3), dtype=np.float32)
        # Normal menghadap +Y: (x0,y,z1) -> (x1,y,z1) -> (x1,y,z0) -> (x0,y,z0)
        verts[:, 0, 0], verts[:, 0, 1], verts[:, 0, 2] = X0.ravel(), y, Z1.ravel()
        verts[:, 1, 0], verts[:, 1, 1], verts[:, 1, 2] = X1.ravel(), y, Z1.ravel()
        verts[:, 2, 0], verts[:, 2, 1], verts[:, 2, 2] = X1.ravel(), y, Z0.ravel()
        verts[:, 3, 0], verts[:, 3, 1], verts[:, 3, 2] = X0.ravel(), y, Z0.ravel()
        cols = np.broadcast_to(np.array(color, dtype=np.float32), (n, 3)).copy()
        if checker is not None:
            ix, iz = np.meshgrid(np.arange(nx), np.arange(nz), indexing="ij")
            mask = ((ix + iz) % 2 == 1).ravel()
            cols[mask] = np.array(checker, dtype=np.float32)
        self._push(verts, cols, alpha, emissive, specular, False, bias, False)

    def tiled_wall_z(self, x0, y0, x1, y1, z, color, normal_z=1, tile=1.5, specular=0.0, bias=0.0, cast_refl=False):
        """Dinding vertikal sepanjang bidang XY pada Z tetap (terbagi tile)."""
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
        self._push(verts, np.array(color, dtype=np.float32), 1.0, 0.0, specular, False, bias, cast_refl)

    def tiled_wall_x(self, z0, y0, z1, y1, x, color, normal_x=1, tile=1.5, specular=0.0, bias=0.0, cast_refl=False):
        """Dinding vertikal sepanjang bidang ZY pada X tetap (terbagi tile)."""
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
        self._push(verts, np.array(color, dtype=np.float32), 1.0, 0.0, specular, False, bias, cast_refl)

    def drop_shadow(self, x, y, z, rx=0.35, rz=0.28, alpha=0.30):
        c = (x, y + 0.008, z)
        pts = [(x - rx, y + 0.008, z + rz), (x + rx, y + 0.008, z + rz),
               (x + rx, y + 0.008, z - rz), (x - rx, y + 0.008, z - rz)]
        self.quad(pts, (12, 14, 22), alpha=alpha, two_sided=False, bias=-0.02)

    def beam(self, p0, p1, radius, color, emissive=1.4, alpha=1.0):
        """Gambar kabel/batang/percikan 3D tipis antara p0 dan p1."""
        a = np.array(p0, dtype=np.float32)
        b = np.array(p1, dtype=np.float32)
        d = b - a
        L = float(np.linalg.norm(d))
        if L < 1e-5:
            return
        u = d / L
        hint = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        if abs(float(u[1])) > 0.95:
            hint = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        s1 = np.cross(u, hint); s1 /= max(float(np.linalg.norm(s1)), 1e-6)
        s2 = np.cross(u, s1)
        mid = (a + b) * 0.5
        mat = np.column_stack([s1, u, s2])
        self.box(mid, (radius * 2, L, radius * 2), color, mat=mat, alpha=alpha, emissive=emissive)

    # -------------------------------------------------------------- render
    def _sky_image(self, W, H, cam):
        """Langit gradien vertikal yang merespons pitch kamera."""
        _, _, fwd = cam.basis()
        pitch_off = float(fwd[1]) * 0.35
        t = np.clip(np.linspace(0.0, 1.0, H, dtype=np.float32) + pitch_off, 0.0, 1.0)[:, None, None]
        top = np.array(self.sky_top, dtype=np.float32)[None, None, :]
        bot = np.array(self.sky_bot, dtype=np.float32)[None, None, :]
        arr = (top * (1.0 - t) + bot * t).astype(np.uint8)
        arr = np.broadcast_to(arr, (H, W, 3)).copy()
        return Image.fromarray(arr, "RGB")

    def render(self, cam, W, H, t=0.0, weather=None):
        img = self._sky_image(W, H, cam)
        if not self.quad_batches and not self.tex_quads:
            return img

        verts = np.concatenate(self.quad_batches, axis=0) if self.quad_batches else np.zeros((0, 4, 3), np.float32)
        cols = np.concatenate(self.col_batches, axis=0) if self.col_batches else np.zeros((0, 3), np.float32)
        alphas = np.concatenate(self.alpha_batches, axis=0) if self.alpha_batches else np.zeros((0,), np.float32)
        emiss = np.concatenate(self.emiss_batches, axis=0) if self.emiss_batches else np.zeros((0,), np.float32)
        specs = np.concatenate(self.spec_batches, axis=0) if self.spec_batches else np.zeros((0,), np.float32)
        twos = np.concatenate(self.two_batches, axis=0) if self.two_batches else np.zeros((0,), bool)
        biases = np.concatenate(self.bias_batches, axis=0) if self.bias_batches else np.zeros((0,), np.float32)
        refls = np.concatenate(self.refl_batches, axis=0) if self.refl_batches else np.zeros((0,), bool)

        # Planar reflection across y=0 if wet_ground is enabled
        if self.wet_ground and np.any(refls) and cam.pos[1] > 0.05:
            rmask = refls
            rv = verts[rmask].copy()
            rv[:, :, 1] = -rv[:, :, 1]
            rv = rv[:, [0, 3, 2, 1], :]   # balik urutan verteks agar normal tetap akurat
            rc = cols[rmask] * 0.72
            ra = alphas[rmask] * self.wet_strength
            re = emiss[rmask] * 0.65
            rs = np.zeros_like(specs[rmask])
            rt = twos[rmask]
            rb = biases[rmask] + 6.0       # selalu digambar di belakang objek nyata
            verts = np.concatenate([verts, rv], axis=0)
            cols = np.concatenate([cols, rc], axis=0)
            alphas = np.concatenate([alphas, ra], axis=0)
            emiss = np.concatenate([emiss, re], axis=0)
            specs = np.concatenate([specs, rs], axis=0)
            twos = np.concatenate([twos, rt], axis=0)
            biases = np.concatenate([biases, rb], axis=0)

        M = len(verts)
        right, up, fwd = cam.basis()
        basis = np.column_stack([right, up, fwd])  # (3, 3)

        # Transform ke ruang kamera terlebih dahulu agar culling sangat cepat
        rel = verts - cam.pos[None, None, :]
        v_cam = rel @ basis                        # (M, 4, 3): x_cam, y_cam, z_cam
        z_max = v_cam[:, :, 2].max(axis=1)
        vis = z_max > 0.18

        # Hitung pusat & normal dunia
        centers = verts.mean(axis=1)
        normals = np.cross(verts[:, 1] - verts[:, 0], verts[:, 2] - verts[:, 0])
        nlen = np.linalg.norm(normals, axis=1, keepdims=True)
        normals = normals / np.maximum(nlen, 1e-6)

        # Backface culling
        to_cam = cam.pos[None, :] - centers
        facing = np.sum(normals * to_cam, axis=1)
        vis &= (twos | (facing > -1e-4))
        # Jika two_sided & menghadap belakang, balik normal untuk pencahayaan yang benar
        flip_n = twos & (facing < 0)
        if np.any(flip_n):
            normals[flip_n] = -normals[flip_n]

        # Frustum culling kasar untuk quad yang sepenuhnya di depan z >= 0.18
        focal = (H * 0.5) / math.tan(math.radians(clamp(cam.fov, 15.0, 110.0) * 0.5))
        half_w_ndc = (W * 0.52) / focal
        half_h_ndc = (H * 0.52) / focal
        z_all_ok = v_cam[:, :, 2].min(axis=1) >= 0.18
        if np.any(vis & z_all_ok):
            idx_ok = np.where(vis & z_all_ok)[0]
            zc = v_cam[idx_ok, :, 2]
            xn = v_cam[idx_ok, :, 0] / zc
            yn = v_cam[idx_ok, :, 1] / zc
            out_frustum = (
                (xn.max(axis=1) < -half_w_ndc) | (xn.min(axis=1) > half_w_ndc) |
                (yn.max(axis=1) < -half_h_ndc) | (yn.min(axis=1) > half_h_ndc)
            )
            vis[idx_ok[out_frustum]] = False

        idx = np.where(vis)[0]
        if len(idx) > 0:
            vc = v_cam[idx]
            cc = cols[idx]
            aa = alphas[idx]
            ee = emiss[idx]
            ss = specs[idx]
            bb = biases[idx]
            ct = centers[idx]
            nn = normals[idx]
            tc = to_cam[idx]

            # Pencahayaan vektor NumPy
            sky_w = (nn[:, 1] * 0.5 + 0.5)[:, None]
            amb = np.array(self.amb_ground)[None, :] * (1.0 - sky_w) + np.array(self.amb_sky)[None, :] * sky_w
            sun_d = np.maximum(0.0, nn @ self.sun_dir)[:, None]
            lit = amb + sun_d * self.sun_col[None, :] * self.sun_int

            if self.lights:
                vdir = tc / np.maximum(np.linalg.norm(tc, axis=1, keepdims=True), 1e-6)
                for L in self.lights:
                    dvec = L.pos[None, :] - ct
                    d2 = np.sum(dvec * dvec, axis=1)
                    max_r2 = (L.radius * 3.2) ** 2
                    near = d2 < max_r2
                    if not np.any(near):
                        continue
                    dn = np.sqrt(np.maximum(d2[near], 1e-5))
                    ldir = dvec[near] / dn[:, None]
                    ndotl = np.maximum(0.0, np.sum(nn[near] * ldir, axis=1))
                    att = L.intensity / (1.0 + d2[near] / max(L.radius * L.radius, 0.1))
                    lit[near] += (att * ndotl)[:, None] * L.color[None, :]
                    if np.any(ss[near] > 0.01):
                        hvec = ldir + vdir[near]
                        hvec /= np.maximum(np.linalg.norm(hvec, axis=1, keepdims=True), 1e-6)
                        ndoth = np.maximum(0.0, np.sum(nn[near] * hvec, axis=1))
                        sp = (ndoth ** 24) * ss[near] * att * 0.65
                        lit[near] += sp[:, None] * L.color[None, :]

            # Warna ber-cahaya + emissive
            shaded = cc * lit
            if np.any(ee > 0.0):
                ew = np.clip(ee, 0.0, 1.0)[:, None]
                em_col = cc * (1.0 + np.minimum(ee, 1.5)[:, None] * 0.35)
                shaded = shaded * (1.0 - ew) + em_col * ew

            # Kabut jarak
            dist = np.linalg.norm(tc, axis=1)
            fog_amt = np.clip(1.0 - np.exp(-np.maximum(0.0, dist - self.fog_start) * self.fog_density), 0.0, 0.92)[:, None]
            fog_c = np.array(self.fog_col, dtype=np.float32)[None, :] / 255.0
            final_rgb = np.clip((shaded * (1.0 - fog_amt) + fog_c * fog_amt) * 255.0, 0, 255).astype(np.uint8)
            final_a = np.clip(aa * 255.0, 0, 255).astype(np.uint8)

            # Proyeksi cepat untuk yang seluruh sudutnya >= 0.18
            z_min_v = vc[:, :, 2].min(axis=1)
            depths = vc[:, :, 2].mean(axis=1) + bb
            order = np.argsort(-depths)

            bw, bh = max(8, W // 4), max(8, H // 4)
            bloom_buf = Image.new("RGB", (bw, bh), (0, 0, 0)) if self.bloom_strength > 0.01 else None
            bd = ImageDraw.Draw(bloom_buf) if bloom_buf else None

            draw_rgb = ImageDraw.Draw(img, "RGBA")

            # Precompute textured quads projections
            tex_items = []
            for tpts, tpimg, tem, tbi in self.tex_quads:
                tvc = (tpts - cam.pos[None, :]) @ basis
                if tvc[:, 2].min() < 0.18:
                    continue
                td = float(tvc[:, 2].mean()) + tbi
                sx = W * 0.5 + (tvc[:, 0] / tvc[:, 2]) * focal
                sy = H * 0.5 - (tvc[:, 1] / tvc[:, 2]) * focal
                tex_items.append((td, list(zip(sx.tolist(), sy.tolist())), tpimg, tem))
            tex_items.sort(key=lambda x: -x[0])
            tex_ptr = 0

            # Pre-project fast quads
            fast_mask = z_min_v >= 0.18
            fast_sx = np.empty((len(idx), 4), dtype=np.float32)
            fast_sy = np.empty((len(idx), 4), dtype=np.float32)
            if np.any(fast_mask):
                zc = vc[fast_mask, :, 2]
                fast_sx[fast_mask] = W * 0.5 + (vc[fast_mask, :, 0] / zc) * focal
                fast_sy[fast_mask] = H * 0.5 - (vc[fast_mask, :, 1] / zc) * focal

            half_w_s = W * 0.5
            half_h_s = H * 0.5
            sx_all = fast_sx.tolist()
            sy_all = fast_sy.tolist()
            rgb_list = final_rgb.tolist()
            a_list = final_a.tolist()
            em_list = ee.tolist()
            fast_list = fast_mask.tolist()
            depth_list = depths.tolist()

            for oi in order:
                di = depth_list[oi]
                while tex_ptr < len(tex_items) and tex_items[tex_ptr][0] >= di:
                    _, dpts, tpimg, tem = tex_items[tex_ptr]
                    _paste_tex_quad(img, bloom_buf, dpts, tpimg, tem, W, H, bw, bh)
                    tex_ptr += 1

                if fast_list[oi]:
                    xs = sx_all[oi]
                    ys = sy_all[oi]
                    pts2 = [(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2]), (xs[3], ys[3])]
                else:
                    clipped = _clip_poly_z(vc[oi], 0.18)
                    if len(clipped) < 3:
                        continue
                    pts2 = [(half_w_s + (p[0] / p[2]) * focal, half_h_s - (p[1] / p[2]) * focal) for p in clipped]

                r, g, b = rgb_list[oi]
                al = a_list[oi]
                draw_rgb.polygon(pts2, fill=(r, g, b, al))
                if bd is not None and em_list[oi] > 0.15:
                    em_v = min(1.0, em_list[oi] * (al / 255.0))
                    br = int(r * em_v)
                    bg = int(g * em_v)
                    bb_c = int(b * em_v)
                    if br + bg + bb_c > 18:
                        bd.polygon([(x * 0.25, y * 0.25) for x, y in pts2], fill=(br, bg, bb_c))

            while tex_ptr < len(tex_items):
                _, dpts, tpimg, tem = tex_items[tex_ptr]
                _paste_tex_quad(img, bloom_buf, dpts, tpimg, tem, W, H, bw, bh)
                tex_ptr += 1

            # Tambah halo PointLight ke bloom buffer
            if bd is not None:
                for L in self.lights:
                    if L.halo <= 0.01:
                        continue
                    pr = cam.project_point(L.pos, W, H)
                    if pr is None:
                        continue
                    lx, ly, lz, lf = pr
                    rad_px = (L.halo / lz) * lf * 0.25
                    if rad_px < 1.0:
                        continue
                    cx, cy = lx * 0.25, ly * 0.25
                    lc = tuple(int(clamp(c * 255.0 * min(1.5, L.intensity * 0.55), 0, 255)) for c in L.color)
                    bd.ellipse([cx - rad_px, cy - rad_px, cx + rad_px, cy + rad_px], fill=lc)

            if bloom_buf is not None and self.bloom_strength > 0.01:
                b1 = bloom_buf.filter(ImageFilter.GaussianBlur(4))
                b2 = bloom_buf.filter(ImageFilter.GaussianBlur(14))
                ba = (np.asarray(b1, dtype=np.float32) * 0.55 + np.asarray(b2, dtype=np.float32) * 0.85) * self.bloom_strength
                ba_img = Image.fromarray(np.clip(ba, 0, 255).astype(np.uint8), "RGB").resize((W, H), Image.BILINEAR)
                arr = np.asarray(img, dtype=np.uint16) + np.asarray(ba_img, dtype=np.uint16)
                img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

        # Hujan / salju 3D
        if weather in ("hujan", "gerimis", "salju"):
            img = _draw_weather_3d(img, cam, W, H, t, weather)

        # Color grading tipis
        if self.grade_tint is not None:
            gc, ga = self.grade_tint
            if ga > 0.005:
                ov = Image.new("RGB", (W, H), tuple(gc))
                img = Image.blend(img, ov, clamp(ga, 0.0, 0.6))

        # Rack focus / blur kamera
        if cam.blur > 0.2:
            img = img.filter(ImageFilter.GaussianBlur(min(12.0, cam.blur)))

        return img


def _paste_tex_quad(img, bloom_buf, dpts, tpimg, tem, W, H, bw, bh):
    xs = [p[0] for p in dpts]
    ys = [p[1] for p in dpts]
    x0, y0 = max(0, int(math.floor(min(xs)))), max(0, int(math.floor(min(ys))))
    x1, y1 = min(W, int(math.ceil(max(xs)))), min(H, int(math.ceil(max(ys))))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return
    tw, th = tpimg.size
    local_dst = [(px - x0, py - y0) for px, py in dpts]
    src_pts = [(0, 0), (tw, 0), (tw, th), (0, th)]
    try:
        coeffs = _persp_coeffs(local_dst, src_pts)
    except np.linalg.LinAlgError:
        return
    warped = tpimg.transform((x1 - x0, y1 - y0), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BILINEAR)
    img.paste(warped, (x0, y0), warped if warped.mode == "RGBA" else None)
    if bloom_buf is not None and tem > 0.15:
        bd = ImageDraw.Draw(bloom_buf)
        bd.polygon([(x * 0.25, y * 0.25) for x, y in dpts], fill=(40, 75, 95))


def _draw_weather_3d(img, cam, W, H, t, weather):
    d = ImageDraw.Draw(img, "RGBA")
    right, up, fwd = cam.basis()
    focal = (H * 0.5) / math.tan(math.radians(clamp(cam.fov, 15.0, 110.0) * 0.5))
    rng = np.random.default_rng(42)
    count = 135 if weather == "hujan" else 70 if weather == "gerimis" else 90
    xs = rng.uniform(-7.0, 7.0, count)
    ys = rng.uniform(-2.0, 9.0, count)
    zs = rng.uniform(-7.0, 7.0, count)
    if weather == "salju":
        yc = (ys - t * 1.4) % 9.0 - 1.5
        xc = xs + np.sin(t * 1.8 + zs) * 0.35
        for i in range(count):
            p = cam.target + np.array([xc[i], yc[i] - cam.target[1] * 0.2, zs[i]], dtype=np.float32)
            rel = p - cam.pos
            zc = float(np.dot(rel, fwd))
            if 0.6 < zc < 22.0:
                sx = W * 0.5 + (float(np.dot(rel, right)) / zc) * focal
                sy = H * 0.5 - (float(np.dot(rel, up)) / zc) * focal
                r = max(1.5, 0.045 / zc * focal)
                if -20 <= sx <= W + 20 and -20 <= sy <= H + 20:
                    d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(245, 250, 255, 190))
    else:
        speed = 11.5 if weather == "hujan" else 8.5
        streak = 0.42 if weather == "hujan" else 0.28
        yc = 7.5 - ((ys + t * speed) % 9.5)
        drift = 0.06
        for i in range(count):
            base = np.array([cam.pos[0] + xs[i], cam.pos[1] * 0.6 + yc[i], cam.pos[2] + zs[i]], dtype=np.float32)
            # Wrap around target/cam forward zone
            p0 = cam.target * 0.45 + cam.pos * 0.55 + np.array([xs[i], yc[i] - 2.0, zs[i]], dtype=np.float32)
            p1 = p0 + np.array([drift, -streak, 0.0], dtype=np.float32)
            r0, r1 = p0 - cam.pos, p1 - cam.pos
            z0, z1 = float(np.dot(r0, fwd)), float(np.dot(r1, fwd))
            if 0.7 < z0 < 18.0 and 0.7 < z1 < 18.0:
                x0 = W * 0.5 + (float(np.dot(r0, right)) / z0) * focal
                y0 = H * 0.5 - (float(np.dot(r0, up)) / z0) * focal
                x1 = W * 0.5 + (float(np.dot(r1, right)) / z1) * focal
                y1 = H * 0.5 - (float(np.dot(r1, up)) / z1) * focal
                if -40 <= x0 <= W + 40 and -40 <= y0 <= H + 40:
                    alpha = int(clamp(165 - z0 * 6, 45, 165))
                    w_px = max(1, int(clamp(3.2 - z0 * 0.14, 1, 3)))
                    d.line([(x0, y0), (x1, y1)], fill=(215, 232, 248, alpha), width=w_px)
    return img
