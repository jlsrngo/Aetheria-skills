# -*- coding: utf-8 -*-
"""
aset_global/tekstur.py
Generator tekstur HD (PIL RGBA, di-cache) GLOBAL untuk gauge, callout teknis,
dan papan data yang dapat dipakai di seluruh skill 3D maupun 2D.
"""
import functools
import math
import os
from PIL import Image, ImageDraw, ImageFont

from .gerak import clamp

OUT = (24, 24, 30)
PUTIH = (255, 255, 255)
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


@functools.lru_cache(maxsize=64)
def get_font(style="judul", size=24):
    """Muat font global dari aset_global/fonts/ (fallback ke font sistem Windows/Linux)."""
    sz = max(8, int(round(size)))
    if style == "judul":
        cands = [
            os.path.join(FONT_DIR, "Baloo2-Var.ttf"),
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    elif style == "seru":
        cands = [
            os.path.join(FONT_DIR, "Bungee-Regular.ttf"),
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    elif style == "kode":
        cands = [
            "C:/Windows/Fonts/consolab.ttf",
            "C:/Windows/Fonts/consola.ttf",
            os.path.join(FONT_DIR, "Nunito-Var.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        ]
    else:
        cands = [
            os.path.join(FONT_DIR, "Nunito-Var.ttf"),
            os.path.join(FONT_DIR, "Fredoka-Var.ttf"),
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, sz)
            except Exception:
                pass
    return ImageFont.load_default()


@functools.lru_cache(maxsize=256)
def tex_dial_gauge(judul, satuan, frac_q, val_txt):
    """Tekstur dial instrumen tajam 256x256 (RPM / BAR / Suhu) dengan zona bahaya & jarum."""
    S = 256
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([10, 10, S - 10, S - 10], fill=(28, 32, 42, 255), outline=(235, 198, 56, 255), width=10)
    d.ellipse([22, 22, S - 22, S - 22], fill=(22, 26, 36, 255))
    # Zona merah bahaya (25% akhir)
    d.arc([34, 34, S - 34, S - 34], -25, 38, fill=(228, 62, 58, 255), width=14)
    # Skala tick dari 140° ke 400° (260° sweep)
    for i in range(11):
        ang = math.radians(140.0 + i * 26.0)
        r0 = 78 if i % 2 == 0 else 86
        r1 = 98
        col = (242, 82, 74, 255) if i >= 8 else (232, 236, 244, 255)
        d.line(
            [
                (128 + math.cos(ang) * r0, 128 + math.sin(ang) * r0),
                (128 + math.cos(ang) * r1, 128 + math.sin(ang) * r1),
            ],
            fill=col,
            width=5 if i % 2 == 0 else 3,
        )
    # Jarum bergerak
    n_ang = math.radians(140.0 + clamp(frac_q, 0.0, 1.0) * 260.0)
    d.line(
        [(128, 128), (128 + math.cos(n_ang) * 76, 128 + math.sin(n_ang) * 76)],
        fill=(252, 206, 62, 255),
        width=8,
    )
    d.ellipse([116, 116, 140, 140], fill=(236, 238, 244, 255), outline=(24, 24, 30, 255), width=3)
    d.text((128, 178), str(val_txt), font=get_font("judul", 28), fill=(255, 226, 84, 255), anchor="mm")
    d.text((128, 206), str(satuan or judul), font=get_font("teks", 16), fill=(190, 198, 214, 255), anchor="mm")
    return im


@functools.lru_cache(maxsize=128)
def tex_tag_callout(judul, sub, bg_col):
    """Tekstur badge label teknis 340x104 dengan border tegas."""
    im = Image.new("RGBA", (340, 104), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bg = tuple(bg_col[:3])
    d.rounded_rectangle([6, 6, 334, 98], radius=18, fill=bg + (246,), outline=OUT + (255,), width=6)
    if sub:
        d.text((170, 36), str(judul).upper(), font=get_font("judul", 26), fill=PUTIH + (255,), anchor="mm")
        d.text((170, 72), str(sub), font=get_font("teks", 20), fill=(255, 236, 140, 255), anchor="mm")
    else:
        d.text((170, 52), str(judul).upper(), font=get_font("judul", 30), fill=PUTIH + (255,), anchor="mm")
    return im
