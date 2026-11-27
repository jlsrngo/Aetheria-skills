# -*- coding: utf-8 -*-
"""
paper.py - inti mesin gambar 3D Pop-Up Paper Craft / Diorama Kertas untuk PaperWorld.

Sistem koordinat (tangan-kanan, +Y ke atas):
  * y = 0.0 -> permukaan meja / lantai kertas
  * x = 0.0 -> tengah panggung; +X ke kanan
  * z = 0.0 -> tengah panggung; +Z menuju kamera depan default

Fitur khas dunia kertas:
  * Kontur 2D CCW + triangulasi ear-clipping + ekstrusi karton berlapis (`extrude_2d`)
    dengan warna depan, belakang, dan tepi potong kertas (`edge_col`).
  * Dinding berlubang pintu lengkung nyata (`arch_wall`) yang dapat dilewati kamera & tokoh.
  * Bayangan datar seragam proyeksi matahari (`cast_shadow` & `cast_wall_shadow`)
    tanpa penumpukan ganda (single-pass opaque shadow plane).
  * Pencahayaan studio hangat matte + serat kertas halus + bloom lembut opsional untuk pintu bercahaya.
"""
import math, os, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
_LOCAL_FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "assets", "fonts"))
_GLOBAL_FONT_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "aset_global", "fonts"))
FONT_DIR = _GLOBAL_FONT_DIR if os.path.isdir(_GLOBAL_FONT_DIR) else _LOCAL_FONT_DIR

# ------------------------------------------------------------------ palet kertas pastel & hangat
OUT = (38, 32, 30)
KERTAS_TEPI = (244, 234, 216)
PUTIH = (248, 243, 232)
KRIM = (238, 220, 190)
MEJA = (224, 200, 166)
HITAM = (34, 34, 42)
COKLAT_RAMBUT = (86, 46, 22)
KORAL = (218, 88, 66)
MERAH = (212, 68, 52)
MERAH_TUA = (158, 46, 38)
PIPI = (224, 124, 108)
BIRU = (60, 104, 184)
BIRU_TUA = (40, 68, 138)
BIRU_MUDA = (158, 198, 232)
BIRU_MALAM = (34, 58, 118)
MINT = (168, 214, 194)
MINT_MUDA = (204, 232, 216)
TEAL = (72, 130, 134)
PINK = (234, 148, 162)
SALMON = (228, 138, 118)
KUNING = (236, 182, 48)
KUNING_MUDA = (248, 220, 122)
ORANYE = (232, 132, 58)
HIJAU = (88, 168, 104)
HIJAU_TUA = (50, 116, 72)
COKLAT = (142, 90, 54)
COKLAT_TUA = (90, 54, 30)
UNGU = (138, 116, 200)
NAVY = (36, 48, 98)
ABU = (192, 194, 202)
ABU_TUA = (104, 106, 118)
KULIT = (246, 222, 192)


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def gelap(c, t=0.22):
    return mix(c, (42, 34, 28), t)


def terang(c, t=0.28):
    return mix(c, (255, 252, 245), t)


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
    p0, p1, p2, p3 = pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(n - 1, i + 2)]
    t2, t3 = t * t, t * t * t
    return tuple(
        0.5 * (
            (2.0 * p1[k])
            + (-p0[k] + p2[k]) * t
            + (2.0 * p0[k] - 5.0 * p1[k] + 4.0 * p2[k] - p3[k]) * t2
            + (-p0[k] + 3.0 * p1[k] - 3.0 * p2[k] + p3[k]) * t3
        )
        for k in range(3)
    )


# ------------------------------------------------------------------ font
@functools.lru_cache(maxsize=256)
def font(name, size):
    """name: 'judul' (Fredoka), 'teks' (Nunito), 'bulat' (Baloo 2), 'seru' (Bungee)."""
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


# ------------------------------------------------------------------ unit cube & rbox
_CUBE_V = np.array([
    [-0.5, -0.5, -0.5], [0.5, -0.5, -0.5], [0.5, 0.5, -0.5], [-0.5, 0.5, -0.5],
    [-0.5, -0.5, 0.5],  [0.5, -0.5, 0.5],  [0.5, 0.5, 0.5],  [-0.5, 0.5, 0.5],
], dtype=np.float32)
_CUBE_F = np.array([
    [4, 5, 6, 7], [1, 0, 3, 2], [5, 1, 2, 6], [0, 4, 7, 3], [7, 6, 2, 3], [0, 1, 5, 4],
], dtype=np.int32)
_FACE_CORNERS = _CUBE_V[_CUBE_F]


@functools.lru_cache(maxsize=256)
def _rbox_template(sx, sy, sz, roundness, seg):
    hx, hy, hz = sx * 0.5, sy * 0.5, sz * 0.5
    r = clamp(roundness, 0.04, 0.96) * min(hx, hy, hz)

    def knots(h):
        ang = np.linspace(0.0, math.pi * 0.5, seg + 1, dtype=np.float32)
        return np.concatenate([-(h - r) - r * np.cos(ang), (h - r) + r * np.sin(ang)])

    kx, ky, kz = knots(hx), knots(hy), knots(hz)

    def face_grid(u_arr, v_arr, const_val, axis_order, flip_u=False, flip_v=False):
        U, V = np.meshgrid(u_arr, v_arr, indexing="ij")
        if flip_u:
            U, V = U[::-1, :], V[::-1, :]
        if flip_v:
            U, V = U[:, ::-1], V[:, ::-1]
        C = np.full_like(U, const_val)
        coords = [None, None, None]
        coords[axis_order[0]], coords[axis_order[1]], coords[axis_order[2]] = U, V, C
        G = np.stack(coords, axis=-1)
        return np.stack([G[:-1, :-1], G[1:, :-1], G[1:, 1:], G[:-1, 1:]], axis=2).reshape(-1, 4, 3)

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
    return np.where(dnorm > 1e-6, inner + delta / np.maximum(dnorm, 1e-6) * r, faces).astype(np.float32)


# ------------------------------------------------------------------ 2D paper silhouettes & ear-clipping
def circle_2d(cx=0.0, cy=0.0, rx=0.5, ry=None, n=32):
    ry = rx if ry is None else ry
    return tuple((round(cx + rx * math.cos(2 * math.pi * i / n), 5), round(cy + ry * math.sin(2 * math.pi * i / n), 5)) for i in range(n))


def rrect_2d(cx, cy, w, h, r=0.05, n_corner=3):
    hx, hy = w * 0.5, h * 0.5
    r = clamp(r, 0.002, min(hx, hy) * 0.95)
    pts = []
    corners = [
        (cx + hx - r, cy + hy - r, 0.0, math.pi * 0.5),
        (cx - hx + r, cy + hy - r, math.pi * 0.5, math.pi),
        (cx - hx + r, cy - hy + r, math.pi, math.pi * 1.5),
        (cx + hx - r, cy - hy + r, math.pi * 1.5, math.pi * 2.0),
    ]
    for ox, oy, a0, a1 in corners:
        for k in range(n_corner + 1):
            a = lerp(a0, a1, k / n_corner)
            pts.append((round(ox + r * math.cos(a), 5), round(oy + r * math.sin(a), 5)))
    return tuple(pts)


def arch_2d(w, h, n_arc=28):
    """Pintu / lengkungan kertas datar di y=0 sampai puncak y=h."""
    r = w * 0.5
    cy = max(0.02, h - r)
    pts = [(-r, 0.0), (r, 0.0)]
    for i in range(n_arc + 1):
        a = math.pi * (i / n_arc)
        pts.append((round(r * math.cos(a), 5), round(cy + r * math.sin(a), 5)))
    return tuple(pts)


def coat_2d(w_top, w_bot, h, r=0.04):
    ht, hb = w_top * 0.5, w_bot * 0.5
    return (
        (-hb + r, 0.0), (hb - r, 0.0), (hb, r),
        (ht, h - r), (ht - r, h), (-ht + r, h), (-ht, h - r), (-hb, r),
    )


def star_2d(r_out=0.28, r_in=0.12, points=5):
    pts = []
    for i in range(points * 2):
        r = r_out if i % 2 == 0 else r_in
        a = math.pi * 0.5 + i * math.pi / points
        pts.append((round(r * math.cos(a), 5), round(r * math.sin(a), 5)))
    return tuple(pts)


def crescent_2d(r=0.45, offset=0.42, n=22):
    """Bulan sabit CCW mulus berbentuk C (perut di kiri, tanduk menghadap kanan) tanpa self-intersection."""
    d = r * clamp(offset, 0.18, 0.72)
    r_in = r * 0.84
    # Titik potong tepat lingkaran luar (0,0,r) dan lingkaran pemotong (+d,0,r_in)
    x_int = (r * r + d * d - r_in * r_in) / (2.0 * d)
    x_int = clamp(x_int, -r * 0.96, r * 0.96)
    y_int = math.sqrt(max(1e-6, r * r - x_int * x_int))
    a_out = math.atan2(y_int, x_int)
    a_in = math.atan2(y_int, x_int - d)
    pts = []
    # Busur luar CCW dari +a_out memutar lewat kiri (pi) ke (2*pi - a_out)
    for i in range(n + 1):
        a = lerp(a_out, 2.0 * math.pi - a_out, i / n)
        pts.append((round(r * math.cos(a), 5), round(r * math.sin(a), 5)))
    # Busur dalam kembali dari (2*pi - a_in) lewat kiri (pi) ke +a_in (tanpa duplikasi ujung)
    for i in range(1, n):
        a = lerp(2.0 * math.pi - a_in, a_in, i / n)
        pts.append((round(d + r_in * math.cos(a), 5), round(r_in * math.sin(a), 5)))
    return tuple(pts)


def cloud_afro_2d(rx=0.35, ry=0.28, lobes=9, n=54):
    """Siluet afro kertas bergelombang halus (CCW tanpa self-intersection)."""
    pts = []
    for i in range(n):
        th = 2.0 * math.pi * i / n
        bump = 1.0 + 0.13 * abs(math.sin(lobes * th * 0.5))
        pts.append((round(rx * bump * math.cos(th), 5), round(ry * bump * math.sin(th), 5)))
    return tuple(pts)


def bob_hair_2d(w=0.66, h=0.62, n_top=28):
    """Siluet rambut bob melengkung halus (dome bulat di atas, melebar lembut ke bawah, pojok membulat)."""
    r_top = w * 0.46
    r_bot = w * 0.51
    cr = r_bot * 0.16
    y_bot = -h * 0.44
    cy = h * 0.50 - r_top
    pts = []
    # Pojok bawah kiri & kanan membulat lembut
    for k in range(5):
        a = math.pi + math.pi * 0.5 * (k / 4.0)
        pts.append((round(-r_bot + cr + cr * math.cos(a), 5), round(y_bot + cr + cr * math.sin(a), 5)))
    for k in range(5):
        a = math.pi * 1.5 + math.pi * 0.5 * (k / 4.0)
        pts.append((round(r_bot - cr + cr * math.cos(a), 5), round(y_bot + cr + cr * math.sin(a), 5)))
    # Sisi kanan sedikit mengecil lembut ke kubah kepala
    pts.append((round(r_bot * 0.985, 5), round(lerp(y_bot + cr, cy, 0.52), 5)))
    # Kubah atas setengah lingkaran mulus
    for i in range(n_top + 1):
        a = math.pi * (i / n_top)
        pts.append((round(r_top * math.cos(a), 5), round(cy + r_top * 0.98 * math.sin(a), 5)))
    pts.append((round(-r_bot * 0.985, 5), round(lerp(y_bot + cr, cy, 0.52), 5)))
    return tuple(pts)


def spiral_ahoge_2d(s=1.0):
    """Jambul pita melengkung halus khas Luna di puncak kepala (CCW tanpa self-intersection)."""
    return (
        (-0.018 * s, 0.0), (0.024 * s, 0.0),
        (0.020 * s, 0.052 * s), (0.042 * s, 0.105 * s),
        (0.075 * s, 0.142 * s), (0.115 * s, 0.148 * s),
        (0.130 * s, 0.126 * s), (0.120 * s, 0.105 * s),
        (0.142 * s, 0.095 * s), (0.164 * s, 0.118 * s),
        (0.160 * s, 0.158 * s), (0.120 * s, 0.182 * s),
        (0.056 * s, 0.166 * s), (0.004 * s, 0.116 * s),
        (-0.020 * s, 0.055 * s),
    )


def cat_silhouette_2d(s=1.0):
    return (
        (-0.26 * s, 0.0), (0.26 * s, 0.0), (0.28 * s, 0.36 * s),
        (0.22 * s, 0.52 * s), (0.25 * s, 0.84 * s), (0.10 * s, 0.72 * s),
        (-0.10 * s, 0.72 * s), (-0.25 * s, 0.84 * s), (-0.22 * s, 0.52 * s),
        (-0.28 * s, 0.36 * s),
    )


def _signed_area(pts):
    a = 0.0
    n = len(pts)
    for i in range(n):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % n]
        a += x0 * y1 - x1 * y0
    return a * 0.5


def _pt_in_tri(p, a, b, c):
    def sgn(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = sgn(p, a, b), sgn(p, b, c), sgn(p, c, a)
    has_neg = (d1 < -1e-7) or (d2 < -1e-7) or (d3 < -1e-7)
    has_pos = (d1 > 1e-7) or (d2 > 1e-7) or (d3 > 1e-7)
    return not (has_neg and has_pos)


@functools.lru_cache(maxsize=512)
def triangulate_2d(pts_tuple):
    """Ear-clipping poligon 2D menjadi daftar indeks segitiga CCW."""
    pts = list(pts_tuple)
    # Hapus titik duplikat berurutan
    clean = []
    for p in pts:
        if not clean or math.hypot(p[0] - clean[-1][0], p[1] - clean[-1][1]) > 1e-6:
            clean.append(p)
    if len(clean) > 2 and math.hypot(clean[0][0] - clean[-1][0], clean[0][1] - clean[-1][1]) < 1e-6:
        clean.pop()
    n = len(clean)
    if n < 3:
        return tuple(clean), ()
    if _signed_area(clean) < 0:
        clean.reverse()
    idx = list(range(n))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < n * n + 10:
        guard += 1
        clipped = False
        m = len(idx)
        for i in range(m):
            ia, ib, ic = idx[(i - 1) % m], idx[i], idx[(i + 1) % m]
            a, b, c = clean[ia], clean[ib], clean[ic]
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if cross <= 1e-8:
                continue
            if any(_pt_in_tri(clean[k], a, b, c) for k in idx if k not in (ia, ib, ic)):
                continue
            tris.append((ia, ib, ic))
            idx.pop(i)
            clipped = True
            break
        if not clipped:
            break
    if len(idx) == 3:
        tris.append((idx[0], idx[1], idx[2]))
    elif len(idx) > 3:
        for i in range(1, len(idx) - 1):
            tris.append((idx[0], idx[i], idx[i + 1]))
    return tuple(clean), tuple(tris)


def _verify_contours():
    for pts in (arch_2d(1.0, 2.0), star_2d(), crescent_2d(), cloud_afro_2d(), bob_hair_2d(), spiral_ahoge_2d(), cat_silhouette_2d()):
        c, t = triangulate_2d(pts)
        assert len(t) >= len(c) - 2, "Ear-clipping failed on paper contour!"


_verify_contours()


# ------------------------------------------------------------------ fine matte art-carton finish (cached)
@functools.lru_cache(maxsize=4)
def _paper_maps(W, H):
    rng = np.random.default_rng(2026)
    mw, mh = max(8, W // 8), max(8, H // 8)
    m_raw = (rng.normal(0.0, 1.0, (mh, mw)) * 22.0 + 128.0).clip(0, 255).astype(np.uint8)
    r_m = max(4, min(W, H) // 75)
    m_img = Image.fromarray(m_raw, "L").resize((W, H), Image.Resampling.BILINEAR).filter(ImageFilter.GaussianBlur(r_m))
    m_arr = np.asarray(m_img, dtype=np.float32) - float(np.mean(np.asarray(m_img, dtype=np.float32)))
    m_std = max(1e-3, float(np.std(m_arr)))
    mottle = (m_arr / m_std) * 1.15

    # Serat halus art-carton (tanpa bercak kotor / garis moire)
    h_raw = (rng.normal(0.0, 1.0, (H, W)) * 24.0 + 128.0).clip(0, 255).astype(np.uint8)
    h_img = Image.fromarray(h_raw, "L").filter(ImageFilter.GaussianBlur(1.2))
    h_arr = np.asarray(h_img, dtype=np.float32)
    emb_core = h_arr[:-2, :-2] - h_arr[2:, 2:]
    emb = np.pad(emb_core, ((1, 1), (1, 1)), mode="edge")
    emb_std = max(1e-3, float(np.std(emb)))
    emboss = (emb / emb_std) * 1.35

    yy = np.linspace(-1.0, 1.0, H, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
    vig = 1.0 - 0.088 * np.clip((xx * xx + yy * yy - 0.36) / 1.40, 0.0, 1.0)

    delta = np.empty((H, W, 3), dtype=np.float32)
    delta[:, :, 0] = emboss + mottle * 1.00
    delta[:, :, 1] = emboss + mottle * 0.92
    delta[:, :, 2] = emboss + mottle * 0.72
    return delta, vig[:, :, None]


def apply_paper_finish(img, strength=1.0):
    W, H = img.size
    delta, vig = _paper_maps(W, H)
    arr = np.asarray(img, dtype=np.float32) * vig + delta * float(strength)
    return Image.fromarray(np.clip(arr, 0.0, 255.0).astype(np.uint8), "RGB")


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
        if zc <= 0.14:
            return None
        xc, yc = float(np.dot(rel, right)), float(np.dot(rel, up))
        focal = (H * 0.5) / math.tan(math.radians(clamp(self.fov, 15.0, 110.0) * 0.5))
        return (W * 0.5 + (xc / zc) * focal, H * 0.5 - (yc / zc) * focal, zc, focal)


def _clip_poly_z(poly, zmin=0.14):
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
    return np.linalg.solve(np.array(A, np.float64), np.array([c for uv in src_pts for c in uv], np.float64))


class PointLight:
    def __init__(self, pos, color=(255, 224, 150), intensity=1.2, radius=4.0, halo=0.0):
        self.pos = np.array(pos, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32) / 255.0
        self.intensity = float(intensity)
        self.radius = float(radius)
        self.halo = float(halo)


# ------------------------------------------------------------------ ScenePaper
class ScenePaper:
    def __init__(self):
        self.quad_batches = []
        self.col_batches = []
        self.alpha_batches = []
        self.emiss_batches = []
        self.two_batches = []
        self.bias_batches = []
        self.shad_batches = []
        self.wshad_batches = []
        self.unlit_batches = []
        self.anchor_batches = []
        self.has_anchor_batches = []
        self.lights = []
        self.tex_quads = []

        # Pencahayaan studio miniatur diorama kertas hangat (warm key + soft shadow map 3D + SSAO)
        self.sky_top = (240, 228, 206)
        self.sky_bot = (230, 215, 190)
        self.amb_sky = (0.62, 0.60, 0.56)
        self.amb_ground = (0.46, 0.41, 0.35)
        self.sun_dir = np.array([-0.64, 0.60, 0.48], dtype=np.float32)
        self.sun_dir /= np.linalg.norm(self.sun_dir)
        self.sun_col = np.array([1.08, 0.99, 0.86], dtype=np.float32)
        self.sun_int = 0.56
        self.fog_col = (234, 220, 196)
        self.fog_start = 24.0
        self.fog_density = 0.014
        self.shadow_floor_y = 0.0
        self.floor_shadow_col = (176, 156, 128)
        self.shadow_wall_z = None
        self.wall_shadow_col = (14, 22, 48)
        self.use_shadow_map = True
        self.shadow_map_res = 512
        self.shadow_strength = 1.0
        self.shadow_tint = (0.28, 0.31, 0.36)
        self.shadow_blur = 1.6
        self.use_ssao = True
        self.ssao_strength = 0.38
        self.ssao_radius = 0.52
        self.bloom_strength = 0.44
        self.paper_grain = True
        self.grade_tint = None

    def set_sky(self, top, bot, amb_sky=None, amb_ground=None, sun_dir=None, sun_col=None, sun_int=None, fog_col=None, fog_start=None, fog_density=None):
        self.sky_top, self.sky_bot = tuple(top), tuple(bot)
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

    def add_light(self, pos, color=(255, 220, 140), intensity=1.2, radius=4.0, halo=0.0):
        self.lights.append(PointLight(pos, color, intensity, radius, halo))

    def _push(self, verts, colors, alphas=1.0, emissive=0.0, two_sided=False, bias=0.0, cast_shadow=True, cast_wall_shadow=False, unlit=False, sort_anchor=None):
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
        self.alpha_batches.append(np.full(n, alphas, np.float32) if np.isscalar(alphas) else np.asarray(alphas, np.float32))
        self.emiss_batches.append(np.full(n, emissive, np.float32) if np.isscalar(emissive) else np.asarray(emissive, np.float32))
        self.two_batches.append(np.full(n, two_sided, bool) if isinstance(two_sided, bool) else np.asarray(two_sided, bool))
        self.bias_batches.append(np.full(n, bias, np.float32) if np.isscalar(bias) else np.asarray(bias, np.float32))
        self.shad_batches.append(np.full(n, cast_shadow, bool) if isinstance(cast_shadow, bool) else np.asarray(cast_shadow, bool))
        self.wshad_batches.append(np.full(n, cast_wall_shadow, bool) if isinstance(cast_wall_shadow, bool) else np.asarray(cast_wall_shadow, bool))
        self.unlit_batches.append(np.full(n, unlit, bool) if isinstance(unlit, bool) else np.asarray(unlit, bool))
        if sort_anchor is None:
            self.anchor_batches.append(np.zeros((n, 3), np.float32))
            self.has_anchor_batches.append(np.zeros(n, bool))
        else:
            self.anchor_batches.append(np.broadcast_to(np.asarray(sort_anchor, np.float32), (n, 3)).copy())
            self.has_anchor_batches.append(np.ones(n, bool))

    def quad(self, pts, color, alpha=1.0, emissive=0.0, two_sided=True, bias=0.0, cast_shadow=False, cast_wall_shadow=False, unlit=False):
        self._push(np.array([pts], np.float32), np.array(color, np.float32), alpha, emissive, two_sided, bias, cast_shadow, cast_wall_shadow, unlit)

    def textured_quad(self, pts, pil_rgba, emissive=0.0, bias=-0.03):
        self.tex_quads.append((np.array(pts, dtype=np.float32), pil_rgba, float(emissive), float(bias)))

    def box(self, center, size, color, rot=None, mat=None, alpha=1.0, emissive=0.0, bias=0.0, cast_shadow=True, cast_wall_shadow=False, unlit=False):
        sx, sy, sz = size
        if sx <= 0 or sy <= 0 or sz <= 0:
            return
        verts = _FACE_CORNERS * np.array([sx, sy, sz], dtype=np.float32)
        if mat is not None:
            verts = verts @ mat.T
        elif rot is not None and any(rot):
            verts = verts @ euler_mat(*rot).T
        verts = verts + np.array(center, dtype=np.float32)
        self._push(verts, np.array(color, np.float32), alpha, emissive, False, bias, cast_shadow, cast_wall_shadow, unlit)

    def rbox(self, center, size, color, roundness=0.35, seg=1, rot=None, mat=None, alpha=1.0, emissive=0.0, bias=0.0, cast_shadow=True, sort_anchor=None):
        sx, sy, sz = float(size[0]), float(size[1]), float(size[2])
        if sx <= 0 or sy <= 0 or sz <= 0:
            return
        verts = _rbox_template(round(sx, 4), round(sy, 4), round(sz, 4), round(float(roundness), 3), int(seg))
        if mat is not None:
            verts = verts @ mat.T
        elif rot is not None and any(rot):
            verts = verts @ euler_mat(*rot).T
        verts = verts + np.array(center, dtype=np.float32)
        self._push(verts, np.array(color, np.float32), alpha, emissive, False, bias, cast_shadow, False, False, sort_anchor=sort_anchor)

    def extrude_2d(self, pts_2d, thickness=0.042, front_col=KRIM, back_col=None, edge_col=None,
                   origin=(0.0, 0.0, 0.0), rot=None, mat=None, pivot=(0.0, 0.0, 0.0),
                   bias=0.0, cast_shadow=True, cast_wall_shadow=False, emissive=0.0, alpha=1.0,
                   sort_anchor=None, drop_shadow=0.0):
        """Ekstrusi siluet kertas 2D menjadi potongan karton 3D nyata dengan tepi sewarna & bayangan kontak opsional."""
        clean, tris = triangulate_2d(tuple(pts_2d))
        if not tris:
            return
        hz = float(thickness) * 0.5
        n_v = len(clean)
        fc = np.array(front_col, dtype=np.float32)
        bc = np.array(back_col if back_col is not None else front_col, dtype=np.float32)
        ec_tup = edge_col if edge_col is not None else mix(front_col, KERTAS_TEPI, 0.68)
        ec = np.array(ec_tup, dtype=np.float32)

        q_rim, c_rim = [], []
        for i in range(n_v):
            x0, y0 = clean[i]
            x1, y1 = clean[(i + 1) % n_v]
            q_rim.append([[x0, y0, -hz], [x1, y1, -hz], [x1, y1, +hz], [x0, y0, +hz]])
            c_rim.append(ec)

        q_fb, c_fb = [], []
        for ia, ib, ic in tris:
            ax, ay = clean[ia]
            bx, by = clean[ib]
            cx, cy = clean[ic]
            q_fb.append([[ax, ay, +hz], [bx, by, +hz], [cx, cy, +hz], [cx, cy, +hz]])
            c_fb.append(fc)
            q_fb.append([[ax, ay, -hz], [cx, cy, -hz], [bx, by, -hz], [bx, by, -hz]])
            c_fb.append(bc)

        piv = np.array(pivot, dtype=np.float32)
        orig = np.array(origin, dtype=np.float32)
        m_use = mat if mat is not None else (euler_mat(*rot) if rot is not None and any(rot) else None)

        def _xform(arr):
            v = np.array(arr, dtype=np.float32)
            if m_use is not None:
                v = (v - piv) @ m_use.T + piv
            return v + orig

        ds_a = 0.22 if drop_shadow is True else float(drop_shadow or 0.0)
        if ds_a > 0.005:
            q_sh = []
            sz = -hz - 0.004
            for ia, ib, ic in tris:
                ax, ay = clean[ia]
                bx, by = clean[ib]
                cx, cy = clean[ic]
                q_sh.append([[ax + 0.016, ay - 0.022, sz], [bx + 0.016, by - 0.022, sz], [cx + 0.016, cy - 0.022, sz], [cx + 0.016, cy - 0.022, sz]])
            anc_sh = None
            if sort_anchor is not None:
                fwd_l = m_use[:, 2] if m_use is not None else np.array([0.0, 0.0, 1.0], dtype=np.float32)
                anc_sh = np.asarray(sort_anchor, dtype=np.float32) - fwd_l * 0.006
            self._push(_xform(q_sh), np.array((24, 16, 12), dtype=np.float32), ds_a, 0.0, False, bias + 0.012, False, False, True, sort_anchor=anc_sh)

        self._push(_xform(q_rim), np.array(c_rim, dtype=np.float32), alpha, emissive, False, bias + 0.005, cast_shadow, cast_wall_shadow, False, sort_anchor=sort_anchor)
        self._push(_xform(q_fb), np.array(c_fb, dtype=np.float32), alpha, emissive, False, bias, cast_shadow, cast_wall_shadow, False, sort_anchor=sort_anchor)

    def extrude_ring_arch(self, r_in, r_out, cy, thickness=0.04, col=BIRU, edge_col=None,
                          n_arc=32, origin=(0.0, 0.0, 0.0), rot=None, mat=None,
                          bias=0.0, cast_shadow=True, sort_anchor=None, drop_shadow=0.0):
        """Bangun cincin busur melengkung mulus dari quad konveks radial tanpa triangulasi ear-clipping."""
        hz = float(thickness) * 0.5
        fc = np.array(col, dtype=np.float32)
        ec_tup = edge_col if edge_col is not None else mix(col, KERTAS_TEPI, 0.68)
        ec = np.array(ec_tup, dtype=np.float32)

        pts_in, pts_out = [], []
        for i in range(n_arc + 1):
            a = math.pi * (i / n_arc)
            ca, sa = math.cos(a), math.sin(a)
            pts_in.append((r_in * ca, cy + r_in * sa))
            pts_out.append((r_out * ca, cy + r_out * sa))

        q_rim, c_rim, q_fb, c_fb = [], [], [], []
        for i in range(n_arc):
            ix0, iy0 = pts_in[i]
            ix1, iy1 = pts_in[i + 1]
            ox0, oy0 = pts_out[i]
            ox1, oy1 = pts_out[i + 1]
            q_fb.append([[ix0, iy0, +hz], [ox0, oy0, +hz], [ox1, oy1, +hz], [ix1, iy1, +hz]])
            c_fb.append(fc)
            q_fb.append([[ix0, iy0, -hz], [ix1, iy1, -hz], [ox1, oy1, -hz], [ox0, oy0, -hz]])
            c_fb.append(fc)
            q_rim.append([[ox0, oy0, -hz], [ox1, oy1, -hz], [ox1, oy1, +hz], [ox0, oy0, +hz]])
            c_rim.append(ec)
            q_rim.append([[ix1, iy1, -hz], [ix0, iy0, -hz], [ix0, iy0, +hz], [ix1, iy1, +hz]])
            c_rim.append(ec)

        orig = np.array(origin, dtype=np.float32)
        m_use = mat if mat is not None else (euler_mat(*rot) if rot is not None and any(rot) else None)

        def _xform(arr):
            v = np.array(arr, dtype=np.float32)
            if m_use is not None:
                v = v @ m_use.T
            return v + orig

        ds_a = 0.22 if drop_shadow is True else float(drop_shadow or 0.0)
        if ds_a > 0.005:
            q_sh = []
            sz = -hz - 0.004
            for i in range(n_arc):
                ix0, iy0 = pts_in[i]
                ix1, iy1 = pts_in[i + 1]
                ox0, oy0 = pts_out[i]
                ox1, oy1 = pts_out[i + 1]
                q_sh.append([[ix0 + 0.016, iy0 - 0.022, sz], [ox0 + 0.016, oy0 - 0.022, sz], [ox1 + 0.016, oy1 - 0.022, sz], [ix1 + 0.016, iy1 - 0.022, sz]])
            anc_sh = None
            if sort_anchor is not None:
                fwd_l = m_use[:, 2] if m_use is not None else np.array([0.0, 0.0, 1.0], dtype=np.float32)
                anc_sh = np.asarray(sort_anchor, dtype=np.float32) - fwd_l * 0.006
            self._push(_xform(q_sh), np.array((24, 16, 12), dtype=np.float32), ds_a, 0.0, False, bias + 0.012, False, False, True, sort_anchor=anc_sh)

        self._push(_xform(q_rim), np.array(c_rim, dtype=np.float32), 1.0, 0.0, False, bias + 0.005, cast_shadow, False, False, sort_anchor=sort_anchor)
        self._push(_xform(q_fb), np.array(c_fb, dtype=np.float32), 1.0, 0.0, False, bias, cast_shadow, False, False, sort_anchor=sort_anchor)

    def arch_wall(self, origin, wall_w, wall_h, door_w, door_h, thickness=0.14,
                  wall_col=PUTIH, trim_col=None, edge_col=None, rot=None, mat=None, cast_shadow=True, bias=0.45):
        """Dinding kertas dengan lubang pintu lengkung nyata yang bisa dilewati tokoh & kamera."""
        hw = wall_w * 0.5
        dw = door_w * 0.5
        m_use = mat if mat is not None else (euler_mat(*rot) if rot and any(rot) else np.eye(3, dtype=np.float32))
        if hw > dw + 0.01:
            side_w = hw - dw
            for sgn in (-1.0, 1.0):
                p_side = [(-side_w * 0.5, 0.0), (side_w * 0.5, 0.0), (side_w * 0.5, wall_h), (-side_w * 0.5, wall_h)]
                off = np.array([sgn * (dw + side_w * 0.5), 0.0, 0.0], dtype=np.float32)
                self.extrude_2d(p_side, thickness, wall_col, wall_col, edge_col, origin=np.array(origin) + m_use @ off, mat=m_use, bias=bias, cast_shadow=cast_shadow)
        n_arc = 32
        r = dw
        cy = max(0.05, door_h - r)
        sp_pts = [(dw, wall_h), (-dw, wall_h)]
        for i in range(n_arc + 1):
            a = math.pi - math.pi * (i / n_arc)
            sp_pts.append((round(r * math.cos(a), 5), round(cy + r * math.sin(a), 5)))
        self.extrude_2d(sp_pts, thickness, wall_col, wall_col, edge_col, origin=origin, mat=m_use, bias=bias, cast_shadow=cast_shadow)
        if trim_col is not None:
            tw = 0.09
            for z_off in (thickness * 0.5 + 0.015, -thickness * 0.5 - 0.015):
                for sgn in (-1.0, 1.0):
                    p_jamb = [(-tw * 0.5, 0.0), (tw * 0.5, 0.0), (tw * 0.5, cy), (-tw * 0.5, cy)]
                    off = np.array([sgn * (dw + tw * 0.35), 0.0, z_off], dtype=np.float32)
                    self.extrude_2d(p_jamb, 0.032, trim_col, trim_col, edge_col, origin=np.array(origin) + m_use @ off, mat=m_use, bias=-0.04, cast_shadow=False)
                off_z = np.array([0.0, 0.0, z_off], dtype=np.float32)
                self.extrude_ring_arch(r, r + tw * 0.85, cy, 0.032, trim_col, edge_col=edge_col, n_arc=n_arc, origin=np.array(origin) + m_use @ off_z, mat=m_use, bias=-0.04, cast_shadow=False)

    def tiled_plane(self, x0, z0, x1, z1, y, color, tile=1.8, alpha=1.0, bias=1.4, checker=None):
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
        self._push(verts, cols, alpha, 0.0, False, bias, False, False, False)

    def beam(self, p0, p1, radius, color, emissive=0.0):
        a, b = np.array(p0, np.float32), np.array(p1, np.float32)
        d = b - a
        L = float(np.linalg.norm(d))
        if L < 1e-5:
            return
        u = d / L
        hint = np.array([0.0, 1.0, 0.0], np.float32) if abs(float(u[1])) <= 0.95 else np.array([1.0, 0.0, 0.0], np.float32)
        s1 = np.cross(u, hint); s1 /= max(float(np.linalg.norm(s1)), 1e-6)
        s2 = np.cross(u, s1)
        self.box((a + b) * 0.5, (radius * 2, L, radius * 2), color, mat=np.column_stack([s1, u, s2]), emissive=emissive, cast_shadow=False)

    # -------------------------------------------------------------- render
    def _sky_image(self, W, H, cam):
        _, _, fwd = cam.basis()
        pitch_off = float(fwd[1]) * 0.35
        t = np.clip(np.linspace(0.0, 1.0, H, dtype=np.float32) + pitch_off, 0.0, 1.0)[:, None, None]
        top = np.array(self.sky_top, dtype=np.float32)[None, None, :]
        bot = np.array(self.sky_bot, dtype=np.float32)[None, None, :]
        arr = (top * (1.0 - t) + bot * t).astype(np.uint8)
        return Image.fromarray(np.broadcast_to(arr, (H, W, 3)).copy(), "RGB")

    def render(self, cam, W, H, t=0.0, finish=True):
        img = self._sky_image(W, H, cam)
        if not self.quad_batches and not self.tex_quads:
            return apply_paper_finish(img) if (self.paper_grain and finish) else img

        verts = np.concatenate(self.quad_batches, axis=0)
        cols = np.concatenate(self.col_batches, axis=0)
        alphas = np.concatenate(self.alpha_batches, axis=0)
        emiss = np.concatenate(self.emiss_batches, axis=0)
        twos = np.concatenate(self.two_batches, axis=0)
        biases = np.concatenate(self.bias_batches, axis=0)
        shads = np.concatenate(self.shad_batches, axis=0)
        wshads = np.concatenate(self.wshad_batches, axis=0)
        unlits = np.concatenate(self.unlit_batches, axis=0)
        ancs = np.concatenate(self.anchor_batches, axis=0)
        hancs = np.concatenate(self.has_anchor_batches, axis=0)

        right, up, fwd = cam.basis()
        basis = np.column_stack([right, up, fwd])
        focal = (H * 0.5) / math.tan(math.radians(clamp(cam.fov, 15.0, 110.0) * 0.5))

        use_smap = bool(self.use_shadow_map)
        # Fallback proyeksi lantai/dinding lama hanya dipakai jika shadow map 3D dimatikan eksplisit
        floor_sv_cam = None
        if (not use_smap) and self.shadow_floor_y is not None and np.any(shads):
            fy = float(self.shadow_floor_y)
            sv = verts[shads]
            above = sv[:, :, 1].max(axis=1) > fy + 0.02
            if np.any(above):
                sv = sv[above].copy()
                sy_clamp = np.maximum(sv[:, :, 1], fy)
                t_hit = np.minimum(12.0, (sy_clamp - fy) / max(float(self.sun_dir[1]), 0.25))
                sv[:, :, 0] -= t_hit * float(self.sun_dir[0])
                sv[:, :, 2] -= t_hit * float(self.sun_dir[2])
                sv[:, :, 1] = fy + 0.003
                sv_cam = (sv - cam.pos[None, None, :]) @ basis
                sv_vis = sv_cam[:, :, 2].max(axis=1) > 0.14
                if np.any(sv_vis):
                    floor_sv_cam = sv_cam[sv_vis]

        wall_sv_cam = None
        if (not use_smap) and self.shadow_wall_z is not None and np.any(wshads):
            wz = float(self.shadow_wall_z)
            wv = verts[wshads]
            in_front = wv[:, :, 2].max(axis=1) > wz + 0.02
            if np.any(in_front):
                wv = wv[in_front].copy()
                sz_c = np.maximum(wv[:, :, 2], wz)
                t_hit = np.minimum(5.0, (sz_c - wz) / max(abs(float(self.sun_dir[2])), 0.28))
                wv[:, :, 0] -= t_hit * float(self.sun_dir[0]) * 0.72
                wv[:, :, 1] -= t_hit * float(self.sun_dir[1]) * 0.48
                wv[:, :, 2] = wz + 0.012
                wv_cam = (wv - cam.pos[None, None, :]) @ basis
                wv_vis = wv_cam[:, :, 2].max(axis=1) > 0.14
                if np.any(wv_vis):
                    wall_sv_cam = wv_cam[wv_vis]

        rel = verts - cam.pos[None, None, :]
        v_cam = rel @ basis
        vis = v_cam[:, :, 2].max(axis=1) > 0.14

        centers = verts.mean(axis=1)
        normals = np.cross(verts[:, 1] - verts[:, 0], verts[:, 2] - verts[:, 0])
        normals = normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-6)
        to_cam = cam.pos[None, :] - centers
        facing = np.sum(normals * to_cam, axis=1)
        vis &= (twos | (facing > -1e-4))
        flip_n = twos & (facing < 0)
        if np.any(flip_n):
            normals[flip_n] = -normals[flip_n]

        hw_ndc, hh_ndc = (W * 0.52) / focal, (H * 0.52) / focal
        z_all_ok = v_cam[:, :, 2].min(axis=1) >= 0.14
        if np.any(vis & z_all_ok):
            idx_ok = np.where(vis & z_all_ok)[0]
            zc = v_cam[idx_ok, :, 2]
            xn, yn = v_cam[idx_ok, :, 0] / zc, v_cam[idx_ok, :, 1] / zc
            vis[idx_ok[(xn.max(axis=1) < -hw_ndc) | (xn.min(axis=1) > hw_ndc) | (yn.max(axis=1) < -hh_ndc) | (yn.min(axis=1) > hh_ndc)]] = False

        idx = np.where(vis)[0]
        if len(idx) > 0:
            vc, cc, aa, ee, bb, uu = v_cam[idx], cols[idx], alphas[idx], emiss[idx], biases[idx], unlits[idx]
            ct, nn, tc = centers[idx], normals[idx], to_cam[idx]

            sky_w = (nn[:, 1] * 0.5 + 0.5)[:, None]
            amb = np.array(self.amb_ground)[None, :] * (1.0 - sky_w) + np.array(self.amb_sky)[None, :] * sky_w
            sun_d = np.maximum(0.0, nn @ self.sun_dir)[:, None]
            # Cahaya pantul hangat halus dari permukaan meja (warm bounce light) + kontras key light
            bounce = np.maximum(0.0, -nn[:, 0] * self.sun_dir[0] * 0.35 + (1.0 - np.abs(nn[:, 1])) * 0.12)[:, None]
            lit = amb + sun_d * self.sun_col[None, :] * self.sun_int + bounce * np.array([0.11, 0.09, 0.07], np.float32)[None, :]
            # Ambient occlusion halus di dasar pertemuan dinding/objek dengan lantai
            if self.shadow_floor_y is not None:
                h_above = np.maximum(0.0, ct[:, 1] - float(self.shadow_floor_y))
                is_vert = (np.abs(nn[:, 1]) < 0.72) & (h_above < 0.36)
                if np.any(is_vert):
                    ao_k = np.where(is_vert, 0.90 + 0.10 * np.clip(h_above / 0.36, 0.0, 1.0), 1.0)[:, None]
                    lit = lit * ao_k

            if self.lights:
                for L in self.lights:
                    dvec = L.pos[None, :] - ct
                    d2 = np.sum(dvec * dvec, axis=1)
                    near = d2 < (L.radius * 3.0) ** 2
                    if not np.any(near):
                        continue
                    dn = np.sqrt(np.maximum(d2[near], 1e-5))
                    ldir = dvec[near] / dn[:, None]
                    ndotl = np.maximum(0.0, np.sum(nn[near] * ldir, axis=1))
                    att = L.intensity / (1.0 + d2[near] / max(L.radius * L.radius, 0.1))
                    lit[near] += (att * ndotl)[:, None] * L.color[None, :]

            shaded = np.where(uu[:, None], cc, cc * lit)
            if np.any(ee > 0.0):
                ew = np.clip(ee, 0.0, 1.0)[:, None]
                shaded = shaded * (1.0 - ew) + (cc * (1.0 + np.minimum(ee, 1.5)[:, None] * 0.28)) * ew

            dist = np.linalg.norm(tc, axis=1)
            fog_amt = np.clip(1.0 - np.exp(-np.maximum(0.0, dist - self.fog_start) * self.fog_density), 0.0, 0.85)[:, None]
            fog_amt = np.where(uu[:, None], fog_amt * 0.4, fog_amt)
            fog_c = np.array(self.fog_col, np.float32)[None, :] / 255.0
            final_rgb = np.clip((shaded * (1.0 - fog_amt) + fog_c * fog_amt) * 255.0, 0, 255).astype(np.uint8)
            final_a = np.clip(aa * 255.0, 0, 255).astype(np.uint8)

            z_min_v = vc[:, :, 2].min(axis=1)
            anc_idx = ancs[idx]
            hanc_idx = hancs[idx]
            anc_z = np.sum((anc_idx - cam.pos[None, :]) * fwd[None, :], axis=1)
            depths = np.where(hanc_idx, anc_z, vc[:, :, 2].mean(axis=1)) + bb
            order = np.argsort(-depths, kind="stable")

            has_bloom = self.bloom_strength > 0.01 and (np.any(ee > 0.25) or any(L.halo > 0.01 for L in self.lights))
            bw, bh = max(8, W // 4), max(8, H // 4)
            bloom_buf = Image.new("RGB", (bw, bh), (0, 0, 0)) if has_bloom else None
            bd = ImageDraw.Draw(bloom_buf) if bloom_buf else None

            tex_items = []
            for tpts, tpimg, tem, tbi in self.tex_quads:
                tvc = (tpts - cam.pos[None, :]) @ basis
                if tvc[:, 2].min() < 0.14:
                    continue
                td = float(tvc[:, 2].mean()) + tbi
                sx = W * 0.5 + (tvc[:, 0] / tvc[:, 2]) * focal
                sy = H * 0.5 - (tvc[:, 1] / tvc[:, 2]) * focal
                tex_items.append((td, list(zip(sx.tolist(), sy.tolist())), tpimg, tem))
            tex_items.sort(key=lambda x: -x[0])
            tex_ptr = 0

            fast_mask = z_min_v >= 0.14
            fast_sx = np.empty((len(idx), 4), np.float32)
            fast_sy = np.empty((len(idx), 4), np.float32)
            if np.any(fast_mask):
                zc = vc[fast_mask, :, 2]
                fast_sx[fast_mask] = W * 0.5 + (vc[fast_mask, :, 0] / zc) * focal
                fast_sy[fast_mask] = H * 0.5 - (vc[fast_mask, :, 1] / zc) * focal

            half_w_s, half_h_s = W * 0.5, H * 0.5
            sx_all, sy_all = fast_sx.tolist(), fast_sy.tolist()
            rgb_list, a_list, em_list = final_rgb.tolist(), final_a.tolist(), ee.tolist()
            fast_list, depth_list = fast_mask.tolist(), depths.tolist()

            if self.shadow_floor_y is not None:
                fy = float(self.shadow_floor_y)
                is_gnd = (~hanc_idx) & (verts[idx][:, :, 1].max(axis=1) <= fy + 0.048)
                gnd_order = [oi for oi in order if is_gnd[oi]]
                up_order = [oi for oi in order if not is_gnd[oi]]
            else:
                gnd_order = []
                up_order = list(order)

            draw_rgb = ImageDraw.Draw(img, "RGBA")
            for oi in gnd_order:
                if fast_list[oi]:
                    xs, ys = sx_all[oi], sy_all[oi]
                    pts2 = [(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2]), (xs[3], ys[3])]
                else:
                    clipped = _clip_poly_z(vc[oi], 0.14)
                    if len(clipped) < 3:
                        continue
                    pts2 = [(half_w_s + (p[0] / p[2]) * focal, half_h_s - (p[1] / p[2]) * focal) for p in clipped]
                r, g, b = rgb_list[oi]
                draw_rgb.polygon(pts2, fill=(r, g, b, a_list[oi]))

            # Bayangan area-light lembut di atas lantai & karpet (zero double-darkening!)
            if floor_sv_cam is not None:
                sw_h, sh_h = max(8, W // 2), max(8, H // 2)
                smask = Image.new("L", (sw_h, sh_h), 0)
                sd = ImageDraw.Draw(smask)
                f_h = focal * 0.5
                hw_h, hh_h = sw_h * 0.5, sh_h * 0.5
                s_zmin = floor_sv_cam[:, :, 2].min(axis=1)
                s_fast = s_zmin >= 0.14
                if np.any(s_fast):
                    sf = floor_sv_cam[s_fast]
                    szf = sf[:, :, 2]
                    sfx = (hw_h + (sf[:, :, 0] / szf) * f_h).tolist()
                    sfy = (hh_h - (sf[:, :, 1] / szf) * f_h).tolist()
                    for xs, ys in zip(sfx, sfy):
                        sd.polygon([(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2]), (xs[3], ys[3])], fill=255)
                for p3 in floor_sv_cam[~s_fast]:
                    clipped = _clip_poly_z(p3, 0.14)
                    if len(clipped) >= 3:
                        sd.polygon([(hw_h + (p[0] / p[2]) * f_h, hh_h - (p[1] / p[2]) * f_h) for p in clipped], fill=255)
                smask = smask.filter(ImageFilter.GaussianBlur(5.5)).resize((W, H), Image.Resampling.BILINEAR)
                ma = (np.asarray(smask, dtype=np.float32) / 255.0)[:, :, None]
                sh_tint = np.array([0.26, 0.29, 0.34], dtype=np.float32)[None, None, :]
                arr_g = np.asarray(img, dtype=np.float32) * (1.0 - ma * sh_tint)
                img = Image.fromarray(np.clip(arr_g, 0.0, 255.0).astype(np.uint8), "RGB")
                draw_rgb = ImageDraw.Draw(img, "RGBA")

            wall_shadow_done = wall_sv_cam is None
            wz_cam_thresh = None
            if not wall_shadow_done:
                wz_cam_thresh = float(np.dot(np.array([cam.pos[0], cam.pos[1], float(self.shadow_wall_z)], np.float32) - cam.pos, fwd)) - 0.05

            for oi in up_order:
                di = depth_list[oi]
                if not wall_shadow_done and di < wz_cam_thresh:
                    # Terapkan bayangan dinding lembut tepat setelah dinding belakang tergambar!
                    sw_h, sh_h = max(8, W // 2), max(8, H // 2)
                    wmask = Image.new("L", (sw_h, sh_h), 0)
                    wd = ImageDraw.Draw(wmask)
                    f_h = focal * 0.5
                    hw_h, hh_h = sw_h * 0.5, sh_h * 0.5
                    w_zmin = wall_sv_cam[:, :, 2].min(axis=1)
                    w_fast = w_zmin >= 0.14
                    if np.any(w_fast):
                        wf = wall_sv_cam[w_fast]
                        wzf = wf[:, :, 2]
                        wfx = (hw_h + (wf[:, :, 0] / wzf) * f_h).tolist()
                        wfy = (hh_h - (wf[:, :, 1] / wzf) * f_h).tolist()
                        for xs, ys in zip(wfx, wfy):
                            wd.polygon([(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2]), (xs[3], ys[3])], fill=255)
                    for p3 in wall_sv_cam[~w_fast]:
                        clipped = _clip_poly_z(p3, 0.14)
                        if len(clipped) >= 3:
                            wd.polygon([(hw_h + (p[0] / p[2]) * f_h, hh_h - (p[1] / p[2]) * f_h) for p in clipped], fill=255)
                    wmask = wmask.filter(ImageFilter.GaussianBlur(4.2)).resize((W, H), Image.Resampling.BILINEAR)
                    wma = (np.asarray(wmask, dtype=np.float32) / 255.0)[:, :, None]
                    wtint = np.array([0.42, 0.40, 0.34], dtype=np.float32)[None, None, :]
                    arr_w = np.asarray(img, dtype=np.float32) * (1.0 - wma * wtint)
                    img = Image.fromarray(np.clip(arr_w, 0.0, 255.0).astype(np.uint8), "RGB")
                    draw_rgb = ImageDraw.Draw(img, "RGBA")
                    wall_shadow_done = True

                while tex_ptr < len(tex_items) and tex_items[tex_ptr][0] >= di:
                    _, dpts, tpimg, tem = tex_items[tex_ptr]
                    _paste_tex_quad(img, bloom_buf, dpts, tpimg, tem, W, H)
                    tex_ptr += 1

                if fast_list[oi]:
                    xs, ys = sx_all[oi], sy_all[oi]
                    pts2 = [(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2]), (xs[3], ys[3])]
                else:
                    clipped = _clip_poly_z(vc[oi], 0.14)
                    if len(clipped) < 3:
                        continue
                    pts2 = [(half_w_s + (p[0] / p[2]) * focal, half_h_s - (p[1] / p[2]) * focal) for p in clipped]

                r, g, b = rgb_list[oi]
                al = a_list[oi]
                draw_rgb.polygon(pts2, fill=(r, g, b, al))
                if bd is not None and em_list[oi] > 0.25:
                    em_v = min(1.0, em_list[oi] * (al / 255.0))
                    bd.polygon([(x * 0.25, y * 0.25) for x, y in pts2], fill=(int(r * em_v), int(g * em_v), int(b * em_v)))

            while tex_ptr < len(tex_items):
                _, dpts, tpimg, tem = tex_items[tex_ptr]
                _paste_tex_quad(img, bloom_buf, dpts, tpimg, tem, W, H)
                tex_ptr += 1

            # --- TRUE 3D DIRECTIONAL SHADOW MAP + WORLD-SPACE ALCHEMY SSAO (100% Pure Python/NumPy/PIL) ---
            if use_smap or self.use_ssao:
                img = self._apply_3d_shadow_and_ssao(
                    img, cam, basis, focal, W, H,
                    verts, alphas, unlits, shads, wshads,
                    idx, vc, nn, ee, aa, uu,
                    gnd_order, up_order, fast_list, sx_all, sy_all,
                )

            if bloom_buf is not None:
                for L in self.lights:
                    if L.halo <= 0.01:
                        continue
                    pr = cam.project_point(L.pos, W, H)
                    if pr is not None:
                        lx, ly, lz, lf = pr
                        rp = (L.halo / lz) * lf * 0.25
                        if rp >= 1.0:
                            cx, cy = lx * 0.25, ly * 0.25
                            lc = tuple(int(clamp(c * 255.0 * min(1.3, L.intensity * 0.65), 0, 255)) for c in L.color)
                            bd.ellipse([cx - rp, cy - rp, cx + rp, cy + rp], fill=lc)
                b1 = bloom_buf.filter(ImageFilter.GaussianBlur(6))
                b2 = bloom_buf.filter(ImageFilter.GaussianBlur(18))
                b3 = bloom_buf.filter(ImageFilter.GaussianBlur(38))
                ba = (np.asarray(b1, np.float32) * 0.42 + np.asarray(b2, np.float32) * 0.68 + np.asarray(b3, np.float32) * 0.85) * self.bloom_strength
                ba_img = Image.fromarray(np.clip(ba, 0, 255).astype(np.uint8), "RGB").resize((W, H), Image.BILINEAR)
                arr = np.asarray(img, np.uint16) + np.asarray(ba_img, np.uint16)
                img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")

        if self.paper_grain and finish:
            img = apply_paper_finish(img)

        if self.grade_tint is not None:
            gc, ga = self.grade_tint
            if ga > 0.005:
                img = Image.blend(img, Image.new("RGB", (W, H), tuple(gc)), clamp(ga, 0.0, 0.6))

        if cam.blur > 0.2:
            img = img.filter(ImageFilter.GaussianBlur(min(12.0, cam.blur)))
        return img

    def _apply_3d_shadow_and_ssao(
        self, img, cam, basis, focal, W, H,
        verts, alphas, unlits, shads, wshads,
        idx, vc, nn, ee, aa, uu,
        gnd_order, up_order, fast_list, sx_all, sy_all,
    ):
        """Shadow Map 3D ortografis (PCF 3x3) + World-Space Alchemy SSAO 100% pure Python/NumPy/PIL."""
        scale_s = min(0.5, 360.0 / max(1, W))
        SW, SH = max(32, int(round(W * scale_s))), max(32, int(round(H * scale_s)))
        sx_sc = SW / float(W)
        sy_sc = SH / float(H)
        focal_s = focal * sy_sc
        hw_s, hh_s = SW * 0.5, SH * 0.5

        # 1. Pass Face-ID kamera (C-speed PIL Painter's Order) untuk posisi dunia 3D eksak per piksel
        id_img = Image.new("I", (SW, SH), 0)
        id_draw = ImageDraw.Draw(id_img)
        opaque_flag = ((aa >= 0.99) & (~uu)).tolist()

        for order_grp in (gnd_order, up_order):
            for oi in order_grp:
                if not opaque_flag[oi]:
                    continue
                if fast_list[oi]:
                    xs, ys = sx_all[oi], sy_all[oi]
                    pts2 = [(xs[0] * sx_sc, ys[0] * sy_sc), (xs[1] * sx_sc, ys[1] * sy_sc),
                            (xs[2] * sx_sc, ys[2] * sy_sc), (xs[3] * sx_sc, ys[3] * sy_sc)]
                else:
                    clipped = _clip_poly_z(vc[oi], 0.14)
                    if len(clipped) < 3:
                        continue
                    pts2 = [(hw_s + (p[0] / p[2]) * focal_s, hh_s - (p[1] / p[2]) * focal_s) for p in clipped]
                id_draw.polygon(pts2, fill=int(oi) + 1)

        ids = np.asarray(id_img, dtype=np.int32)
        mask = ids > 0
        if not np.any(mask):
            return img

        # Rekonstruksi posisi 3D dunia (P_world) dan normal (N_world) eksak via interseksi ray-plane
        yy_g, xx_g = np.mgrid[0:SH, 0:SW].astype(np.float32)
        fi = ids[mask] - 1

        p0_c = vc[:, 0, :]
        n_c = nn @ basis
        plane_d = np.sum(p0_c * n_c, axis=1)
        z_fmin = np.maximum(0.14, vc[:, :, 2].min(axis=1) - 0.04)
        z_fmax = vc[:, :, 2].max(axis=1) + 0.04
        z_fmean = vc[:, :, 2].mean(axis=1)

        rx = (xx_g[mask] + 0.5 - hw_s) / focal_s
        ry = -(yy_g[mask] + 0.5 - hh_s) / focal_s
        ray_c = np.stack([rx, ry, np.ones_like(rx)], axis=-1)
        nc_pix = n_c[fi]
        denom = np.sum(ray_c * nc_pix, axis=-1)
        safe_d = np.where(np.abs(denom) > 0.035, denom, 1.0)
        t_raw = np.where(np.abs(denom) > 0.035, plane_d[fi] / safe_d, z_fmean[fi])
        t_hit = np.clip(t_raw, z_fmin[fi], z_fmax[fi])

        P_cam = ray_c * t_hit[:, None]
        P_world = P_cam @ basis.T + cam.pos[None, :]
        N_world = nn[fi]
        E_pix = ee[fi]
        em_damp = np.clip(1.0 - E_pix * 2.2, 0.0, 1.0)

        # 2. Directional 3D Shadow Map (ortografis dari matahari + 3x3 PCF)
        sh_grid = None
        if self.use_shadow_map and self.shadow_strength > 0.01:
            caster_mask = (shads | wshads) & (alphas >= 0.99) & (~unlits)
            if np.any(caster_mask):
                l_fwd = (-self.sun_dir).astype(np.float32)
                l_fwd /= max(float(np.linalg.norm(l_fwd)), 1e-6)
                up_h = np.array([0.0, 1.0, 0.0], np.float32) if abs(float(l_fwd[1])) < 0.96 else np.array([0.0, 0.0, 1.0], np.float32)
                l_right = np.cross(l_fwd, up_h)
                l_right /= max(float(np.linalg.norm(l_right)), 1e-6)
                l_up = np.cross(l_right, l_fwd)
                l_basis = np.column_stack([l_right, l_up, l_fwd])

                pw_l = P_world @ l_basis
                # Fokuskan frustum shadow map tepat pada area kamera yang terlihat (abaikan outlier jauh > 26u)
                near_cam = t_hit < 26.0
                pw_fit = pw_l[near_cam] if np.any(near_cam) else pw_l
                lx_min = float(np.percentile(pw_fit[:, 0], 0.3)) - 1.2
                lx_max = float(np.percentile(pw_fit[:, 0], 99.7)) + 1.2
                ly_min = float(np.percentile(pw_fit[:, 1], 0.3)) - 1.2
                ly_max = float(np.percentile(pw_fit[:, 1], 99.7)) + 1.2
                # Pastikan aspek persegi agar resolusi texel seragam di kedua sumbu
                span = max(2.0, lx_max - lx_min, ly_max - ly_min)
                cx_l, cy_l = 0.5 * (lx_min + lx_max), 0.5 * (ly_min + ly_max)
                lx_min, lx_max = cx_l - span * 0.5, cx_l + span * 0.5
                ly_min, ly_max = cy_l - span * 0.5, cy_l + span * 0.5

                LM = int(self.shadow_map_res)
                inv_span = LM / span
                texel_w = span / LM

                c_verts = verts[caster_mask]
                vl = c_verts @ l_basis
                # Cull caster yang di luar frustum shadow map
                in_box = (
                    (vl[:, :, 0].max(axis=1) >= lx_min) & (vl[:, :, 0].min(axis=1) <= lx_max) &
                    (vl[:, :, 1].max(axis=1) >= ly_min) & (vl[:, :, 1].min(axis=1) <= ly_max)
                )
                if np.any(in_box):
                    vl = vl[in_box]
                    c_verts = c_verts[in_box]
                    c_n = np.cross(c_verts[:, 1] - c_verts[:, 0], c_verts[:, 2] - c_verts[:, 0])
                    c_n /= np.maximum(np.linalg.norm(c_n, axis=1, keepdims=True), 1e-6)
                    nl = c_n @ l_basis
                    lz_mean = vl[:, :, 2].mean(axis=1)
                    # Painter order dari terjauh dari matahari (lz besar) ke terdekat matahari (lz kecil)
                    s_order = np.argsort(-lz_mean, kind="stable")

                    sx_l = ((vl[:, :, 0] - lx_min) * inv_span).tolist()
                    sy_l = ((ly_max - vl[:, :, 1]) * inv_span).tolist()

                    l_id_img = Image.new("I", (LM, LM), 0)
                    ld = ImageDraw.Draw(l_id_img)
                    for si in s_order:
                        xs, ys = sx_l[si], sy_l[si]
                        ld.polygon([(xs[0], ys[0]), (xs[1], ys[1]), (xs[2], ys[2]), (xs[3], ys[3])], fill=int(si) + 1)

                    l_ids = np.asarray(l_id_img, dtype=np.int32)
                    l_mask = l_ids > 0
                    lz_map = np.full((LM, LM), 1e9, dtype=np.float32)
                    if np.any(l_mask):
                        sfi = l_ids[l_mask] - 1
                        lyy, lxx = np.where(l_mask)
                        lx_c = lx_min + (lxx.astype(np.float32) + 0.5) * texel_w
                        ly_c = ly_max - (lyy.astype(np.float32) + 0.5) * texel_w
                        lp0 = vl[:, 0, :]
                        l_pd = np.sum(lp0 * nl, axis=1)
                        lz_fmin = vl[:, :, 2].min(axis=1)
                        lz_fmax = vl[:, :, 2].max(axis=1)
                        nl_s = nl[sfi]
                        nz_s = nl_s[:, 2]
                        ok_nz = np.abs(nz_s) > 0.08
                        safe_nz = np.where(ok_nz, nz_s, 1.0)
                        lz_exact = np.where(ok_nz, (l_pd[sfi] - lx_c * nl_s[:, 0] - ly_c * nl_s[:, 1]) / safe_nz, lz_fmin[sfi])
                        lz_map[l_mask] = np.clip(lz_exact, lz_fmin[sfi] - 0.015, lz_fmax[sfi] + 0.015)

                    # Proyeksi titik kamera (dengan normal-offset bias) ke ruang cahaya + 3x3 PCF
                    n_bias = max(0.016, texel_w * 0.90)
                    d_bias = max(0.026, texel_w * 1.25)
                    p_bias_l = (P_world + N_world * n_bias) @ l_basis
                    su_f = (p_bias_l[:, 0] - lx_min) * inv_span - 0.5
                    sv_f = (ly_max - p_bias_l[:, 1]) * inv_span - 0.5
                    plz = p_bias_l[:, 2] - d_bias

                    in_sm = (su_f >= 1.5) & (su_f < LM - 2.5) & (sv_f >= 1.5) & (sv_f < LM - 2.5)
                    sh_val = np.zeros(len(fi), dtype=np.float32)
                    if np.any(in_sm):
                        su0 = np.rint(su_f[in_sm]).astype(np.int32)
                        sv0 = np.rint(sv_f[in_sm]).astype(np.int32)
                        pz_in = plz[in_sm]
                        acc = np.zeros(len(su0), dtype=np.float32)
                        for dv in (-1, 0, 1):
                            for du in (-1, 0, 1):
                                acc += (pz_in > lz_map[sv0 + dv, su0 + du]).astype(np.float32)
                        sh_val[in_sm] = acc / 9.0

                    # Redam halus pada bidang yang memang membelakangi matahari (bebas shadow acne!)
                    ndotl = N_world @ self.sun_dir
                    facing_sun = np.clip((ndotl - 0.02) / 0.14, 0.0, 1.0)
                    sh_val = sh_val * facing_sun * em_damp * float(self.shadow_strength)

                    sh_grid = np.zeros((SH, SW), dtype=np.float32)
                    sh_grid[mask] = sh_val

        # 3. World-Space Alchemy SSAO (12 tap pada 2 cincin — zero flat-plane self-occlusion!)
        ao_grid = None
        if self.use_ssao and self.ssao_strength > 0.01:
            P_full = np.zeros((SH, SW, 3), dtype=np.float32)
            N_full = np.zeros((SH, SW, 3), dtype=np.float32)
            P_full[mask] = P_world
            N_full[mask] = N_world
            # Downsample 2x untuk kecepatan tinggi (~180x320) lalu blur lembut
            P_ao = P_full[::2, ::2]
            N_ao = N_full[::2, ::2]
            V_ao = mask[::2, ::2]
            E_ao = np.ones((SH, SW), dtype=np.float32)
            E_ao[mask] = em_damp
            E_ao = E_ao[::2, ::2]
            ha, wa = V_ao.shape
            r_ao = float(self.ssao_radius)
            occ = np.zeros((ha, wa), dtype=np.float32)
            # 12 tap: cincin ketat (lipatan kertas/sudut) + cincin sedang (sudut ruangan/lantai)
            taps = (
                (-2, 0), (2, 0), (0, -2), (0, 2),
                (-2, -2), (2, 2), (-2, 2), (2, -2),
                (-5, -2), (5, 2), (-2, 5), (2, -5),
            )
            for dy, dx in taps:
                y0s, y1s = max(0, dy), ha + min(0, dy)
                x0s, x1s = max(0, dx), wa + min(0, dx)
                y0d, y1d = max(0, -dy), ha + min(0, -dy)
                x0d, x1d = max(0, -dx), wa + min(0, -dx)
                valid_pair = V_ao[y0d:y1d, x0d:x1d] & V_ao[y0s:y1s, x0s:x1s]
                diff = P_ao[y0s:y1s, x0s:x1s] - P_ao[y0d:y1d, x0d:x1d]
                dist2 = np.sum(diff * diff, axis=-1)
                dist = np.sqrt(dist2 + 1e-6)
                h = np.sum(diff * N_ao[y0d:y1d, x0d:x1d], axis=-1)
                tap_v = np.where(
                    valid_pair & (dist < r_ao) & (h > 0.022),
                    np.clip((h - 0.022) / (dist + 0.075), 0.0, 1.0) * (1.0 - dist / r_ao),
                    0.0,
                )
                occ[y0d:y1d, x0d:x1d] += tap_v
            ao_raw = np.clip((occ / len(taps)) * (float(self.ssao_strength) * 2.85), 0.0, 0.62) * E_ao
            ao_img = Image.fromarray((ao_raw * 255.0).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(1.5)).resize((W, H), Image.Resampling.BILINEAR)
            ao_grid = np.asarray(ao_img, dtype=np.float32) / 255.0

        # 4. Gabungkan Shadow Map + SSAO ke gambar resolusi penuh dengan warna bayangan diorama hangat
        arr = np.asarray(img, dtype=np.float32)
        if sh_grid is not None:
            sh_img = Image.fromarray((np.clip(sh_grid, 0.0, 1.0) * 255.0).astype(np.uint8), "L")
            if self.shadow_blur > 0.1:
                sh_img = sh_img.filter(ImageFilter.GaussianBlur(float(self.shadow_blur)))
            sh_up = (np.asarray(sh_img.resize((W, H), Image.Resampling.BILINEAR), dtype=np.float32) / 255.0)[:, :, None]
            stint = np.array(self.shadow_tint, dtype=np.float32)[None, None, :]
            arr = arr * (1.0 - sh_up * stint)
        if ao_grid is not None:
            ao_tint = np.array([0.88, 0.94, 1.02], dtype=np.float32)[None, None, :]
            arr = arr * (1.0 - ao_grid[:, :, None] * ao_tint)
        return Image.fromarray(np.clip(arr, 0.0, 255.0).astype(np.uint8), "RGB")


def _paste_tex_quad(img, bloom_buf, dpts, tpimg, tem, W, H):
    xs, ys = [p[0] for p in dpts], [p[1] for p in dpts]
    x0, y0 = max(0, int(math.floor(min(xs)))), max(0, int(math.floor(min(ys))))
    x1, y1 = min(W, int(math.ceil(max(xs)))), min(H, int(math.ceil(max(ys))))
    if x1 - x0 < 4 or y1 - y0 < 4:
        return
    tw, th = tpimg.size
    try:
        coeffs = _persp_coeffs([(px - x0, py - y0) for px, py in dpts], [(0, 0), (tw, 0), (tw, th), (0, th)])
    except np.linalg.LinAlgError:
        return
    warped = tpimg.transform((x1 - x0, y1 - y0), Image.Transform.PERSPECTIVE, coeffs, Image.Resampling.BILINEAR)
    img.paste(warped, (x0, y0), warped if warped.mode == "RGBA" else None)
    if bloom_buf is not None and tem > 0.25:
        ImageDraw.Draw(bloom_buf).polygon([(x * 0.25, y * 0.25) for x, y in dpts], fill=(45, 75, 95))
