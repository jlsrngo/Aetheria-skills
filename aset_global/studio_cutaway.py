# -*- coding: utf-8 -*-
"""
aset_global/studio_cutaway.py
Mesin render 3D Cutaway PBR-Lite murni Python (NumPy + Pillow + True Per-Pixel Z-Buffer)
yang menjadi basis bersama untuk 3 skill cutaway bergaya engineering:
  1. cutaway-tanah  (gaya penampang tanah berlapis, rumah cutaway, sumur/tangki, maskot)
  2. cutaway-air    (gaya kolam/tangki air transparan, pompa/filter pasir, dusk lighting, cards)
  3. cutaway-mesin  (gaya studio bengkel navy, material logam mengkilap, cutaway amber, HUD gauge)

Tanpa Blender / GPU cloud — berjalan 100% lokal di CPU (NumPy + Pillow + ffmpeg).
"""
import importlib
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .gerak import clamp, flow_positions, piston_kinematics, pop_scale, pulse_scale, smoothstep
from .tekstur import get_font, tex_dial_gauge, tex_tag_callout

# Import Z-buffer rasterizer inti dari 3D-stickman secara dinamis (reuse, zero duplicate rasterizer!)
_S3D_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "3D-stickman", "scripts"))
if _S3D_DIR not in sys.path:
    sys.path.insert(0, _S3D_DIR)
_e3d = importlib.import_module("engine3d")


def _norm3(v):
    a = np.array(v, dtype=np.float32)
    n = float(np.linalg.norm(a))
    return a / max(n, 1e-6)


class CutawayScene(_e3d.Scene3D):
    """
    Turunan Scene3D Z-buffer dengan mode shading `studio_metal` (tanpa outline kartun,
    specular logam halus, ambient studio lebih lembut) + overlay HUD & subtitle gaya engineering.
    """

    def __init__(self, style="mesin"):
        super().__init__()
        self.style = style
        self.ink_scale = 0.0          # Matikan outline komik -> tampilan 3D engineering bersih!
        self.cel_strength = 0.0       # Matikan 2-tone cel shading -> aktifkan smooth PBR studio shading!
        self.hud_items = []           # Elemen 2D HUD nempel kamera (gauge, kartu judul, label, subtitle)
        if style == "mesin":
            self.set_sky(
                (38, 52, 76), (54, 68, 96),
                amb_sky=(0.56, 0.60, 0.68),
                amb_ground=(0.24, 0.26, 0.32),
                sun_dir=(0.46, 0.70, 0.54),
                sun_col=(1.0, 0.98, 0.95),
                sun_int=0.78,
            )
            self.rim_strength = 0.22
            self.bloom_strength = 0.28
        elif style == "air":
            self.set_sky(
                (128, 188, 245), (212, 236, 252),
                amb_sky=(0.74, 0.78, 0.84),
                amb_ground=(0.44, 0.42, 0.38),
                sun_dir=(0.52, 0.80, 0.42),
                sun_int=0.68,
            )
            self.rim_strength = 0.08
            self.bloom_strength = 0.14
        else:  # "tanah"
            self.set_sky(
                (142, 198, 248), (214, 235, 250),
                amb_sky=(0.72, 0.76, 0.82),
                amb_ground=(0.42, 0.38, 0.34),
                sun_dir=(0.48, 0.78, 0.45),
                sun_int=0.66,
            )
            self.rim_strength = 0.06
            self.bloom_strength = 0.12

    def add_hud_gauge(self, pos_frac, nilai=0.65, teks_nilai="2,2", satuan="BAR", judul="TEKANAN", size_frac=0.22):
        self.hud_items.append({
            "kind": "gauge", "pos": pos_frac, "nilai": nilai,
            "teks_nilai": teks_nilai, "satuan": satuan, "judul": judul, "size": size_frac,
        })

    def add_hud_badge(self, pos_frac, judul, sub="", bg=(22, 34, 62), accent=(248, 196, 44), w_frac=0.38):
        self.hud_items.append({
            "kind": "badge", "pos": pos_frac, "judul": judul, "sub": sub,
            "bg": bg, "accent": accent, "w": w_frac,
        })

    def add_hud_callout(self, pos_frac, teks, bg=(216, 52, 46), fg=(255, 255, 255), size=26):
        self.hud_items.append({
            "kind": "callout", "pos": pos_frac, "teks": teks, "bg": bg, "fg": fg, "size": size,
        })

    def add_subtitle(self, teks, gaya="phrases", sorot=None, y_frac=0.70):
        self.hud_items.append({
            "kind": "subtitle", "teks": teks, "gaya": gaya, "sorot": sorot, "y": y_frac,
        })

    def render_frame(self, cam, W=1080, H=1920, t=0.0, aa=1.5):
        img = self.render(cam, W, H, t=t, aa=aa).convert("RGBA")
        # Post-polish khusus studio logam: tone filmis lembut + vignette + ketajaman mikro
        if self.style == "mesin":
            arr = np.asarray(img, dtype=np.float32)
            rgb = arr[..., :3] / 255.0
            rgb = np.clip((rgb - 0.5) * 1.06 + 0.5, 0.0, 1.0)
            hh, ww = rgb.shape[:2]
            yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
            rr = np.sqrt(((xx / ww - 0.5) / 0.62) ** 2 + ((yy / hh - 0.47) / 0.74) ** 2)
            vig = 1.0 - 0.22 * np.clip(rr - 0.35, 0.0, 1.0) ** 1.6
            rgb = rgb * vig[..., None]
            arr[..., :3] = rgb * 255.0
            img = Image.fromarray(arr.astype(np.uint8), "RGBA")
            img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))

        # Gambar semua elemen HUD & subtitle tajam di atas frame 3D
        d = ImageDraw.Draw(img)
        for item in self.hud_items:
            k = item["kind"]
            if k == "gauge":
                sz = max(64, int(round(W * item["size"])))
                frac_q = round(clamp(float(item["nilai"]), 0.0, 1.0) * 40.0) / 40.0
                g_im = tex_dial_gauge(item["judul"], item["satuan"], frac_q, item["teks_nilai"]).resize(
                    (sz, sz), Image.LANCZOS
                )
                cx = int(round(W * item["pos"][0])) - sz // 2
                cy = int(round(H * item["pos"][1])) - sz // 2
                img.alpha_composite(g_im, (cx, cy))
            elif k == "badge":
                bw = int(round(W * item["w"]))
                bh = int(round(W * (0.145 if item["sub"] else 0.105)))
                cx = int(round(W * item["pos"][0]))
                cy = int(round(H * item["pos"][1]))
                x0, y0, x1, y1 = cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2
                d.rounded_rectangle([x0, y0, x1, y1], radius=max(8, int(W * 0.014)),
                                    fill=tuple(item["bg"]) + (236,), outline=tuple(item["accent"]) + (255,),
                                    width=max(2, int(W * 0.004)))
                f1 = get_font("judul", max(16, int(W * 0.036)))
                if item["sub"]:
                    f0 = get_font("teks", max(13, int(W * 0.024)))
                    d.text((cx, y0 + bh * 0.30), str(item["sub"]).upper(), font=f0, fill=(215, 224, 240, 255), anchor="mm")
                    d.text((cx, y0 + bh * 0.68), str(item["judul"]).upper(), font=f1, fill=tuple(item["accent"]) + (255,), anchor="mm")
                else:
                    d.text((cx, cy), str(item["judul"]).upper(), font=f1, fill=(255, 255, 255, 255), anchor="mm")
            elif k == "callout":
                f = get_font("judul", max(14, int(W * item["size"] / 1080.0)))
                txt = str(item["teks"]).upper()
                tw = int(d.textlength(txt, font=f))
                pad_x = max(14, int(W * 0.022))
                pad_y = max(8, int(W * 0.012))
                cx, cy = int(round(W * item["pos"][0])), int(round(H * item["pos"][1]))
                th = max(24, int(W * item["size"] / 1080.0) + pad_y * 2)
                d.rounded_rectangle([cx - tw // 2 - pad_x, cy - th // 2, cx + tw // 2 + pad_x, cy + th // 2],
                                    radius=max(6, int(W * 0.01)), fill=tuple(item["bg"]) + (242,))
                d.text((cx, cy), txt, font=f, fill=tuple(item["fg"]) + (255,), anchor="mm")
            elif k == "subtitle":
                txt = str(item["teks"])
                if not txt.strip():
                    continue
                is_cards = str(item["gaya"]).lower() in ("cards", "kata")
                f = get_font("judul", max(20, int(W * (0.072 if is_cards else 0.046))))
                cx, cy = W // 2, int(round(H * item["y"]))
                stroke_w = max(3, int(W * (0.010 if is_cards else 0.006)))
                fill_col = (255, 214, 52, 255) if (is_cards and item.get("sorot")) else (255, 255, 255, 255)
                d.text((cx, cy), txt, font=f, fill=fill_col, anchor="mm",
                       stroke_width=stroke_w, stroke_fill=(14, 16, 22, 255))
        return img.convert("RGB")


# ================================================================ Helper Geometri Cutaway Bersama
def draw_worker_mascot(sc, pos, s=1.0, wave=0.0):
    """Maskot insinyur low-poly (helm kuning, rompi oranye + strip putih, celana biru)."""
    x, y, z = pos
    # Kaki & badan
    sc.box((x - 0.09 * s, y + 0.30 * s, z), (0.11 * s, 0.60 * s, 0.12 * s), (58, 92, 146))
    sc.box((x + 0.09 * s, y + 0.30 * s, z), (0.11 * s, 0.60 * s, 0.12 * s), (58, 92, 146))
    sc.box((x, y + 0.86 * s, z), (0.34 * s, 0.54 * s, 0.20 * s), (238, 128, 34))
    # Strip reflektif rompi
    sc.box((x, y + 0.82 * s, z + 0.105 * s), (0.35 * s, 0.07 * s, 0.015 * s), (238, 242, 246), emissive=0.25)
    # Lengan
    sc.tapered_limb((x - 0.22 * s, y + 1.06 * s, z),
                    (x - 0.30 * s, y + (0.68 + 0.55 * wave) * s, z),
                    0.055 * s, 0.048 * s, (238, 200, 162), seg_u=10, outline=False, caps=True)
    sc.tapered_limb((x + 0.22 * s, y + 1.06 * s, z),
                    (x + 0.26 * s, y + 0.66 * s, z),
                    0.055 * s, 0.048 * s, (238, 200, 162), seg_u=10, outline=False, caps=True)
    # Kepala + helm kuning
    sc.sphere((x, y + 1.28 * s, z), 0.145 * s, (242, 202, 166), seg_u=14, seg_v=10, outline=False)
    sc.sphere((x, y + 1.34 * s, z), 0.165 * s, (248, 204, 42), seg_u=14, seg_v=8, outline=False, hemi=True)
    sc.cylinder((x, y + 1.33 * s, z), 0.185 * s, 0.03 * s, (242, 194, 34), seg_u=14, outline=False)


def draw_lowpoly_tree(sc, pos, s=1.0, col=(92, 152, 74)):
    x, y, z = pos
    sc.cylinder((x, y + 0.45 * s, z), 0.08 * s, 0.90 * s, (124, 86, 54), seg_u=8, outline=False)
    sc.sphere((x, y + 1.15 * s, z), 0.46 * s, col, seg_u=8, seg_v=6, outline=False)
    sc.sphere((x + 0.22 * s, y + 0.92 * s, z + 0.12 * s), 0.30 * s, (col[0] + 10, col[1] + 10, col[2] + 6),
              seg_u=8, seg_v=6, outline=False)


def draw_soil_cross_section(sc, width=10.0, top_y=0.0, depth=4.5, z_cut=0.0):
    """Penampang tanah berlapis khas cutaway-tanah & cutaway-air."""
    # Rumput hijau permukaan
    sc.box((0.0, top_y + 0.07, z_cut - 2.6), (width, 0.14, 5.2), (108, 168, 78))
    # Lapisan tanah atas (coklat hangat)
    sc.box((0.0, top_y - 0.85, z_cut - 2.6), (width, 1.70, 5.2), (138, 92, 58))
    # Lapisan tanah dalam (coklat gelap)
    sc.box((0.0, top_y - 2.95, z_cut - 2.6), (width, 2.50, 5.2), (82, 62, 46))


# ================================================================ 3 Builder Demo / Preset Style
def build_style_tanah(sc, t=1.2):
    """Style 1: cutaway-tanah (penampang tanah, rumah + pipa, tangki septik 2 ruang berlapis)."""
    draw_soil_cross_section(sc, width=9.0, top_y=0.0, z_cut=0.0)
    # Pohon latar
    draw_lowpoly_tree(sc, (-2.6, 0.12, -2.5), s=1.0)
    draw_lowpoly_tree(sc, (2.4, 0.12, -2.8), s=1.15)
    # Rumah mini cutaway di kiri atas
    sc.box((-1.55, 0.85, -0.85), (1.75, 1.45, 1.35), (232, 224, 206))
    sc.box((-1.55, 1.78, -0.85), (2.05, 0.42, 1.55), (196, 102, 68))
    # Maskot insinyur
    draw_worker_mascot(sc, (1.55, 0.14, -0.55), s=0.92, wave=0.3)
    # Tangki septik 2 ruang cutaway di bawah tanah
    tx, ty, tz = 0.0, -0.95, -0.18
    tw, th, td = 2.65, 1.25, 0.72
    wall = (212, 214, 208)
    sc.box((tx, ty - th * 0.5, tz), (tw, 0.12, td), wall)
    sc.box((tx, ty + th * 0.5, tz), (tw, 0.12, td), wall)
    sc.box((tx - tw * 0.48, ty, tz), (0.12, th, td), wall)
    sc.box((tx + tw * 0.48, ty, tz), (0.12, th, td), wall)
    sc.box((tx + 0.35, ty, tz), (0.10, th, td), wall)  # sekat tengah
    sc.box((tx, ty, tz - td * 0.45), (tw, th, 0.08), (162, 166, 158))
    # Tutup manhole atas
    sc.box((tx - 0.55, 0.12, tz), (0.58, 0.28, 0.48), (176, 180, 178))
    sc.box((tx + 0.82, 0.12, tz), (0.54, 0.28, 0.48), (176, 180, 178))
    # 3 lapisan isi tangki kiri: lumpur (sludge), air lebih jernih, buih (scum)
    sc.box((tx - 0.46, ty - 0.40, tz + 0.04), (1.42, 0.26, 0.52), (96, 72, 46))
    sc.box((tx - 0.46, ty - 0.02, tz + 0.04), (1.42, 0.50, 0.52), (168, 158, 114), alpha=0.88)
    sc.box((tx - 0.46, ty + 0.28, tz + 0.06), (1.40, 0.10, 0.50), (226, 214, 134))
    # Ruang kanan (air olahan)
    sc.box((tx + 0.84, ty - 0.10, tz + 0.04), (0.78, 0.82, 0.52), (124, 152, 136), alpha=0.88)
    # Pipa masuk dari rumah + aliran
    pts_in = [(-1.55, 0.25, -0.15), (-1.55, -0.58, -0.15), (-1.22, -0.58, -0.15)]
    for i in range(len(pts_in) - 1):
        sc.tapered_limb(pts_in[i], pts_in[i + 1], 0.08, 0.08, (206, 212, 218), seg_u=12, outline=False, caps=True)
    for p in flow_positions(pts_in, t=t, speed=0.8, gap=0.42):
        sc.sphere(p + np.array([0, 0, 0.07], np.float32), 0.045, (148, 214, 248), emissive=0.45, outline=False)
    # Pipa keluar kanan
    sc.tapered_limb((tx + 1.22, ty + 0.20, -0.15), (2.4, ty + 0.20, -0.15), 0.075, 0.075,
                    (206, 212, 218), seg_u=12, outline=False, caps=True)
    # Callout & subtitle gaya Video #1
    sc.add_hud_callout((0.39, 0.565), "BUIH / SCUM", bg=(34, 48, 72), size=22)
    sc.add_hud_callout((0.39, 0.620), "AIR LEBIH JERNIH", bg=(44, 68, 102), size=22)
    sc.add_hud_callout((0.39, 0.675), "LUMPUR / SLUDGE", bg=(34, 48, 72), size=22)
    sc.add_subtitle("air jernih mengalir keluar", gaya="phrases", y_frac=0.77)


def build_style_air(sc, t=1.2):
    """Style 2: cutaway-air (kolam renang cutaway transparan, rumah tropis, pompa & filter pasir)."""
    draw_soil_cross_section(sc, width=9.0, top_y=0.0, z_cut=0.0)
    # Rumah tropis di belakang
    sc.box((0.0, 0.72, -2.1), (3.4, 1.35, 1.2), (242, 232, 206))
    sc.box((0.0, 1.62, -2.05), (3.9, 0.52, 1.55), (218, 122, 82))
    sc.box((-0.95, 0.72, -1.48), (0.65, 0.55, 0.04), (168, 224, 244), emissive=0.2)
    sc.box((0.95, 0.72, -1.48), (0.65, 0.55, 0.04), (168, 224, 244), emissive=0.2)
    draw_lowpoly_tree(sc, (-2.3, 0.12, -2.2), s=1.1, col=(102, 168, 82))
    draw_lowpoly_tree(sc, (2.3, 0.12, -2.2), s=1.2, col=(92, 158, 74))
    draw_worker_mascot(sc, (-0.85, 0.14, -1.15), s=0.82, wave=0.9)
    # Kolam renang cutaway di depan (dinding beton putih + air biru cerah transparan)
    px, py, pz = -0.35, -0.45, -0.25
    pw, ph, pd = 2.35, 0.96, 1.15
    sc.box((px, py - ph * 0.5, pz), (pw + 0.16, 0.10, pd + 0.16), (226, 232, 238))
    sc.box((px, py, pz - pd * 0.48), (pw, ph, 0.10), (222, 228, 236))
    sc.box((px - pw * 0.48, py, pz), (0.10, ph, pd), (222, 228, 236))
    sc.box((px + pw * 0.48, py, pz), (0.10, ph, pd), (222, 228, 236))
    # Volume air biru jernih + bebek kuning kecil
    sc.box((px, py - 0.04, pz + 0.02), (pw - 0.18, ph - 0.16, pd - 0.14), (66, 168, 236), alpha=0.80, specular=0.35)
    sc.sphere((px + 0.35, py + 0.44, pz + 0.08), 0.095, (252, 218, 52), seg_u=12, seg_v=8, outline=False)
    # Tabung filter pasir cutaway di kanan
    fx, fy, fz = 1.42, 0.15, -0.10
    sc.box((fx, fy + 0.42, fz - 0.12), (0.88, 1.12, 0.24), (72, 146, 218))
    sc.box((fx, fy + 0.26, fz + 0.02), (0.74, 0.62, 0.18), (196, 178, 128))  # media pasir
    for r_i in range(4):
        for c_i in range(5):
            sc.sphere((fx - 0.26 + c_i * 0.13, fy + 0.04 + r_i * 0.13, fz + 0.12),
                      0.055, (226, 212, 168), seg_u=8, seg_v=6, outline=False)
    # Pipa sirkulasi + titik aliran
    pts_p = [(px + 1.12, py - 0.25, -0.05), (fx, py - 0.25, -0.05), (fx, fy + 1.05, -0.05)]
    for i in range(len(pts_p) - 1):
        sc.tapered_limb(pts_p[i], pts_p[i + 1], 0.065, 0.065, (200, 212, 224), seg_u=12, outline=False, caps=True)
    for p in flow_positions(pts_p, t=t, speed=0.95, gap=0.38):
        sc.sphere(p + np.array([0, 0, 0.07], np.float32), 0.048, (142, 236, 128), emissive=0.75, outline=False)
    sc.add_hud_callout((0.78, 0.37), "FILTER PASIR", bg=(34, 96, 168), size=24)
    sc.add_subtitle("sirkulasi", gaya="cards", sorot=True, y_frac=0.72)


def _xdisc(sc, center, radius, thick, color, spec=0.7, seg=28, emissive=0.0):
    """Cakram/silinder dengan sumbu sepanjang X (crank web, flywheel, roda gigi, puli)."""
    sc.cylinder(tuple(float(v) for v in center), radius, thick, color, seg_u=seg, rot=(0, 0, 90),
                outline=False, specular=spec, emissive=emissive)


def _zdisc(sc, center, radius, thick, color, spec=0.7, seg=28, emissive=0.0):
    """Cakram dengan sumbu sepanjang Z (menghadap kamera: rumah turbo, baut muka)."""
    sc.cylinder(tuple(float(v) for v in center), radius, thick, color, seg_u=seg, rot=(90, 0, 0),
                outline=False, specular=spec, emissive=emissive)


def _pipe(sc, pts, r, color, spec=0.75, seg=16):
    for a, b in zip(pts[:-1], pts[1:]):
        sc.tapered_limb(a, b, r, r, color, seg_u=seg, outline=False, specular=spec, caps=True)
    for p in pts[1:-1]:
        sc.sphere(p, r * 1.01, color, seg_u=seg, seg_v=10, outline=False, specular=spec)


def draw_workshop_env(sc):
    """Bengkel studio navy: lantai abu semi-gloss, dinding navy + strip kuning, lemari perkakas merah, mobil teal, jeriken."""
    sc.box((0.0, -0.06, -1.0), (16.0, 0.12, 12.0), (178, 182, 190), specular=0.22)
    sc.box((0.0, 2.6, -2.8), (16.0, 5.6, 0.15), (50, 66, 96))
    sc.box((0.0, 0.32, -2.70), (16.0, 0.64, 0.06), (38, 50, 74))
    sc.box((0.0, 1.05, -2.68), (16.0, 0.10, 0.04), (238, 190, 46), emissive=0.25)
    # Lemari perkakas merah (kiri belakang)
    sc.box((-2.55, 0.72, -2.15), (0.95, 1.44, 0.62), (176, 40, 36), specular=0.40)
    for k in range(5):
        sc.box((-2.55, 0.22 + k * 0.26, -1.83), (0.86, 0.02, 0.02), (90, 20, 20))
        sc.box((-2.55, 0.32 + k * 0.26, -1.82), (0.22, 0.03, 0.03), (210, 214, 222), specular=0.8)
    # Mobil teal (kiri jauh)
    sc.box((-3.65, 0.58, -1.55), (1.9, 0.62, 1.25), (40, 112, 120), specular=0.55)
    sc.box((-3.75, 1.10, -1.55), (1.25, 0.46, 1.08), (36, 100, 108), specular=0.55)
    sc.box((-3.10, 1.10, -1.00), (0.04, 0.36, 0.86), (24, 34, 44), specular=0.7)
    for wx in (-4.25, -3.05):
        _zdisc(sc, (wx, 0.28, -0.90), 0.27, 0.16, (26, 28, 32), spec=0.3, seg=20)
    # Meja biru + jeriken merah (kanan belakang)
    sc.box((2.75, 0.78, -2.05), (1.0, 0.06, 0.6), (44, 92, 168), specular=0.45)
    for lx in (2.30, 3.20):
        sc.box((lx, 0.39, -2.05), (0.05, 0.78, 0.05), (44, 92, 168), specular=0.45)
    sc.box((2.70, 1.05, -2.05), (0.34, 0.48, 0.20), (196, 44, 38), specular=0.45)


def draw_engine_stand(sc, col=(40, 92, 172)):
    """Stand mesin baja biru (rangka tabung + roda kastor) seperti bengkel referensi."""
    for z in (-0.62, 0.30):
        _pipe(sc, [(-1.15, 0.08, z), (1.15, 0.08, z)], 0.045, col, spec=0.55)
    for x in (-1.15, 1.15):
        _pipe(sc, [(x, 0.08, -0.62), (x, 0.08, 0.30)], 0.045, col, spec=0.55)
        for z in (-0.62, 0.30):
            sc.cylinder((x, 0.04, z), 0.05, 0.06, (22, 24, 28), seg_u=14, outline=False, specular=0.3)
    for x in (-0.80, 0.80):
        _pipe(sc, [(x, 0.08, -0.16), (x, 0.62, -0.16)], 0.050, col, spec=0.55)
        _pipe(sc, [(x * 1.40, 0.08, -0.62), (x, 0.55, -0.16)], 0.035, col, spec=0.55)
        _pipe(sc, [(x * 1.40, 0.08, 0.30), (x, 0.55, -0.16)], 0.035, col, spec=0.55)
    sc.box((0.0, 0.64, -0.16), (1.75, 0.05, 0.16), col, specular=0.5)


def build_style_mesin(sc, t=0.05, glow_override=None):
    """Style 3: MechLab3D — mesin inline-4 cutaway studio PBR (gaya CR-V Engine)."""
    AMBER = (244, 172, 34)
    HEAD_CUT = (222, 86, 56)
    HEAD_IN = (132, 46, 36)
    ALU = (184, 190, 200)
    STEEL = (204, 210, 222)
    CHROME = (226, 230, 238)
    IRON = (78, 82, 92)
    BORE = (98, 106, 120)
    SPRING = (46, 98, 210)
    GOLD = (220, 176, 70)
    COPPER = (214, 122, 58)

    # Lampu studio: key hangat kiri-atas, fill dingin kanan, rim belakang
    sc.add_light((-2.6, 4.2, 3.6), color=(255, 246, 232), intensity=1.20, radius=7.0)
    sc.add_light((3.4, 2.8, 3.0), color=(186, 210, 255), intensity=0.70, radius=6.5)
    sc.add_light((0.0, 3.4, -1.6), color=(220, 230, 255), intensity=0.55, radius=4.0)

    draw_workshop_env(sc)
    sc.drop_shadow(0.0, 0.005, -0.16, 1.55, 0.72)
    draw_engine_stand(sc)

    pitch, n_cyl = 0.42, 4
    xs = [(i - 1.5) * pitch for i in range(n_cyl)]
    web_xs = [(k - 2.0) * pitch for k in range(n_cyl + 1)]
    y_pan0, y_blk0, y_deck, y_head1 = 0.66, 0.78, 1.90, 2.26
    crank_y, z_ax = 0.98, -0.02
    r_c, L_r = 0.15, 0.50
    zf = 0.0  # bidang potong depan

    # ---------- Bak oli + blok belakang aluminium ----------
    sc.box((0.0, (y_pan0 + y_blk0) * 0.5, -0.20), (1.86, y_blk0 - y_pan0, 0.40), IRON, specular=0.55)
    sc.box((0.0, (y_blk0 + y_deck) * 0.5, -0.43), (2.12, y_deck - y_blk0, 0.10), ALU, specular=0.62)
    # Dinding samping (aluminium) + muka potong amber
    for sx in (-1.0, 1.0):
        x = sx * 1.02
        sc.box((x, (y_blk0 + y_deck) * 0.5, -0.22), (0.10, y_deck - y_blk0, 0.46), ALU, specular=0.62)
        sc.box((x, (y_blk0 + y_deck) * 0.5, zf + 0.012), (0.11, y_deck - y_blk0, 0.024), AMBER, specular=0.16)
        # Saluran pendingin (water jacket) biru
        sc.box((x - sx * 0.002, 1.48, zf + 0.026), (0.046, 0.64, 0.01), (64, 192, 244), emissive=0.35)
    # Sekat antar-silinder & bulkhead bantalan utama
    for wx in web_xs[1:-1]:
        sc.box((wx, (y_blk0 + y_deck) * 0.5, -0.22), (0.07, y_deck - y_blk0, 0.44), ALU, specular=0.6)
        sc.box((wx, 1.48, zf + 0.012), (0.075, 0.82, 0.024), AMBER, specular=0.16)
        sc.box((wx, 0.86, zf + 0.012), (0.09, 0.16, 0.024), AMBER, specular=0.16)
    # Dek atas amber + bawah blok
    sc.box((0.0, y_deck - 0.03, zf + 0.012), (2.14, 0.06, 0.024), AMBER, specular=0.16)
    sc.box((0.0, 1.07, zf + 0.012), (2.14, 0.035, 0.024), AMBER, specular=0.16)
    # Paking kepala
    sc.box((0.0, y_deck + 0.012, -0.21), (2.16, 0.024, 0.46), (40, 42, 48), specular=0.4)

    # ---------- Kepala silinder cutaway merah ----------
    y_h0 = y_deck + 0.024
    sc.box((0.0, (y_h0 + y_head1) * 0.5, -0.27), (2.14, y_head1 - y_h0, 0.34), HEAD_IN, specular=0.25)
    sc.box((0.0, y_head1 - 0.03, zf + 0.010), (2.16, 0.06, 0.02), HEAD_CUT, specular=0.2)
    sc.box((0.0, y_h0 + 0.03, zf + 0.010), (2.16, 0.06, 0.02), HEAD_CUT, specular=0.2)
    for wx in web_xs:
        sc.box((wx, (y_h0 + y_head1) * 0.5, -0.05), (0.08, y_head1 - y_h0, 0.12), HEAD_CUT, specular=0.2)
    for sx in (-1.0, 1.0):
        sc.box((sx * 1.04, (y_h0 + y_head1) * 0.5, -0.22), (0.08, y_head1 - y_h0, 0.46), HEAD_CUT, specular=0.2)
    # Baut kepala emas
    for wx in web_xs:
        _zdisc(sc, (wx, y_head1 - 0.03, zf + 0.03), 0.022, 0.02, GOLD, spec=0.8, seg=6)

    # ---------- Noken as ganda + roda gigi timing ----------
    y_cam = y_head1 + 0.10
    for zc in (-0.06, -0.26):
        _pipe(sc, [(-1.10, y_cam, zc), (1.10, y_cam, zc)], 0.040, CHROME, spec=0.9, seg=18)
        for wx in web_xs:
            sc.box((wx, y_cam - 0.02, zc), (0.08, 0.09, 0.11), ALU, specular=0.6)
    _xdisc(sc, (-1.16, y_cam, -0.06), 0.13, 0.04, GOLD, spec=0.8, seg=24)
    _xdisc(sc, (-1.16, y_cam, -0.26), 0.13, 0.04, GOLD, spec=0.8, seg=24)

    # ---------- Bore silinder ----------
    for cx in xs:
        sc.cylinder((cx, 1.48, -0.20), 0.17, 0.80, BORE, seg_u=28, outline=False, specular=0.75)

    # ---------- Poros engkol, flywheel, puli ----------
    _pipe(sc, [(-1.30, crank_y, z_ax), (1.24, crank_y, z_ax)], 0.052, CHROME, spec=0.9, seg=20)
    _xdisc(sc, (-1.34, crank_y, z_ax), 0.34, 0.06, IRON, spec=0.65, seg=36)
    _xdisc(sc, (-1.38, crank_y, z_ax), 0.36, 0.03, (156, 162, 172), spec=0.8, seg=36)
    _xdisc(sc, (1.26, crank_y, z_ax), 0.12, 0.07, (52, 56, 64), spec=0.55, seg=24)

    kin = piston_kinematics(t, n_cyl=n_cyl, rpm_vis=1.8, crank_r=r_c, rod_l=L_r)
    for st, cx in zip(kin, xs):
        th = st["theta"]
        dy, dz = math.cos(th) * r_c, math.sin(th) * r_c
        pin = np.array([cx, crank_y + dy, z_ax + dz], dtype=np.float32)
        wrist = np.array([cx, crank_y + st["piston_y"], z_ax], dtype=np.float32)
        # Crank web + bobot penyeimbang
        for wsx in (-0.115, 0.115):
            _xdisc(sc, (cx + wsx, crank_y + dy * 0.5, z_ax + dz * 0.5), 0.10, 0.05, STEEL, spec=0.82, seg=24)
            _xdisc(sc, (cx + wsx, crank_y - dy * 0.55, z_ax - dz * 0.55), 0.13, 0.05, (150, 158, 172), spec=0.75, seg=24)
        sc.tapered_limb((cx - 0.12, pin[1], pin[2]), (cx + 0.12, pin[1], pin[2]), 0.045, 0.045, CHROME,
                        seg_u=16, outline=False, specular=0.9, caps=True)
        # Setang (conrod) baja tempa
        _xdisc(sc, pin, 0.075, 0.13, (170, 178, 192), spec=0.82, seg=22)
        sc.tapered_limb(pin, wrist, 0.042, 0.030, (170, 178, 192), seg_u=16, outline=False, specular=0.85, caps=True)
        _xdisc(sc, wrist, 0.045, 0.10, (150, 158, 170), spec=0.8, seg=18)
        # Piston + 3 ring
        sc.cylinder(tuple(wrist + np.array([0, 0.07, 0], np.float32)), 0.152, 0.23, (220, 226, 236),
                    seg_u=32, outline=False, specular=0.9)
        for ry in (0.155, 0.125, 0.095):
            sc.cylinder(tuple(wrist + np.array([0, ry, 0], np.float32)), 0.156, 0.016, (44, 48, 56),
                        seg_u=28, outline=False, specular=0.6)
        crown_y = float(wrist[1] + 0.185)
        # Katup + pegas biru + retainer emas
        for vx in (-0.08, 0.08):
            sc.cylinder((cx + vx, y_h0 + 0.02, -0.03), 0.055, 0.02, (70, 74, 84), seg_u=18, outline=False, specular=0.7)
            sc.tapered_limb((cx + vx, y_h0 + 0.02, -0.03), (cx + vx, y_cam - 0.05, -0.03), 0.013, 0.013, CHROME,
                            seg_u=10, outline=False, specular=0.9, caps=True)
            for k in range(7):
                sc.cylinder((cx + vx, y_h0 + 0.11 + k * 0.028, -0.03), 0.040, 0.012, SPRING,
                            seg_u=16, outline=False, specular=0.65)
            sc.cylinder((cx + vx, y_h0 + 0.32, -0.03), 0.046, 0.016, GOLD, seg_u=16, outline=False, specular=0.8)
        # Api pembakaran (gradasi + cahaya oranye)
        ga = st["tdc_glow"] if glow_override is None else glow_override[st["index"]]
        if ga > 0.0:
            gh = max(0.02, y_h0 - crown_y - 0.01)
            sc.cylinder((cx, crown_y + gh * 0.5, -0.04), 0.148, gh, (255, 150, 46), seg_u=24,
                        emissive=1.5, alpha=0.62 + 0.3 * ga, outline=False)
            sc.cylinder((cx, crown_y + gh * 0.35, -0.04), 0.10, gh * 0.7, (255, 232, 150), seg_u=20,
                        emissive=1.6, alpha=0.75, outline=False)
            sc.add_light((cx, crown_y + 0.1, 0.20), color=(255, 150, 50), intensity=1.4 * ga, radius=1.1, halo=0.16 * ga)

    # ---------- Turbo keong spiral aluminium mulus + pipa ----------
    tx, ty, tz = 1.46, 1.98, -0.12
    _zdisc(sc, (tx, ty, tz - 0.02), 0.24, 0.24, (206, 212, 224), spec=0.88, seg=36)
    snail_pts = []
    for k in range(25):
        u = k / 24.0
        a = math.radians(-50.0 + u * 350.0)
        rr = 0.165 + u * 0.085
        snail_pts.append((tx + math.cos(a) * rr, ty + math.sin(a) * rr, tz - 0.01))
    for k in range(len(snail_pts) - 1):
        r0 = 0.068 + (k / 24.0) * 0.036
        r1 = 0.068 + ((k + 1) / 24.0) * 0.036
        sc.tapered_limb(snail_pts[k], snail_pts[k + 1], r0, r1, (206, 212, 224),
                        seg_u=18, outline=False, specular=0.88, caps=True)
    _zdisc(sc, (tx, ty, tz + 0.14), 0.165, 0.06, (176, 182, 194), spec=0.86, seg=32)
    _zdisc(sc, (tx, ty, tz + 0.18), 0.112, 0.05, (32, 36, 44), spec=0.52, seg=28)
    _zdisc(sc, (tx, ty, tz + 0.20), 0.042, 0.03, CHROME, spec=0.92, seg=16)
    _pipe(sc, [(tx - 0.10, ty - 0.24, tz - 0.06), (tx - 0.10, 1.52, tz - 0.10), (1.10, 1.40, -0.20)], 0.065, COPPER, spec=0.72)
    _pipe(sc, [(tx + 0.02, ty + 0.24, tz - 0.04), (tx - 0.04, 2.48, tz - 0.12), (0.95, 2.50, -0.22)], 0.058, STEEL, spec=0.86)

    # ---------- HUD khas CR-V ----------
    sc.add_hud_gauge((0.19, 0.125), nilai=0.74, teks_nilai="2,2", satuan="BAR", size_frac=0.24)
    sc.add_hud_badge((0.72, 0.105), "TEKANAN", sub="MUSUH 1", bg=(20, 28, 48), accent=(248, 198, 48), w_frac=0.34)
    sc.add_hud_callout((0.72, 0.185), "2,2 BAR TURBO", bg=(214, 52, 46), size=24)
    sc.add_subtitle("dan ledakan di ruang bakar", gaya="phrases", y_frac=0.74)


MESIN_CAM = {"pos": (2.55, 3.05, 7.7), "target": (0.10, 1.55, -0.15), "fov": 40.0}


def render_style_preview(style, out_path, W=540, H=960, t=0.05):
    sc = CutawayScene(style=style)
    if style == "tanah":
        build_style_tanah(sc, t=t)
        cam = _e3d.Cam3D(pos=(0.0, 0.45, 7.6), target=(0.0, -0.25, -0.2), fov=42.0)
    elif style == "air":
        build_style_air(sc, t=t)
        cam = _e3d.Cam3D(pos=(0.25, 1.05, 7.8), target=(0.18, 0.05, -0.2), fov=42.0)
    else:
        build_style_mesin(sc, t=t)
        cam = _e3d.Cam3D(pos=MESIN_CAM["pos"], target=MESIN_CAM["target"], fov=MESIN_CAM["fov"])
    img = sc.render_frame(cam, W, H, t=t, aa=1.5)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    img.save(out_path)
    return out_path
