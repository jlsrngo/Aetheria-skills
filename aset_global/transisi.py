# -*- coding: utf-8 -*-
"""
aset_global/transisi.py
Pustaka 22 transisi video sinematik GLOBAL (pure Python + Pillow + NumPy) untuk seluruh
skill Aetheria (/3D-stickman, /paperworld, /voxelverse, /stikman-cerita, /strata3d,
/hydro3d, /mechlab3d).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .gerak import clamp, ease_io, ease_out_cubic

OUT_DEFAULT = (22, 22, 28)

TRANSISI_ALIAS = {
    "cut": "potong",
    "dissolve": "fade",
    "silang": "fade",
    "crossfade": "fade",
    "dip_hitam": "fade_hitam",
    "dip_black": "fade_hitam",
    "dip_putih": "flash",
    "kilat": "flash",
    "blink": "kedip",
    "slide": "geser",
    "push_slide": "geser",
    "whip_pan": "whip",
    "zoom_in": "zoom",
    "diagonal": "wipe_diagonal",
    "pillar_wipe": "wipe_tiang",
    "foreground_wipe": "wipe_tiang",
    "tiang": "wipe_tiang",
    "spin": "putar",
    "split": "belah",
    "tirai_belah": "belah",
    "blinds": "tirai",
    "venetian": "tirai",
    "burn": "luma",
    "film_burn": "luma",
    "light_leak": "luma",
    "defocus": "blur_cross",
    "rack_focus": "blur_cross",
    "rgb_split": "glitch",
    "pixelate": "kotak",
    "mosaic": "kotak",
    "page_turn": "halaman",
    "lipat": "halaman",
    "radial_flash": "cahaya",
    "flare": "cahaya",
}

DAFTAR_TRANSISI = (
    "potong",
    "fade",
    "fade_hitam",
    "flash",
    "kedip",
    "iris",
    "geser",
    "whip",
    "zoom",
    "zoom_out",
    "wipe",
    "wipe_diagonal",
    "wipe_tiang",
    "putar",
    "belah",
    "tirai",
    "luma",
    "blur_cross",
    "glitch",
    "kotak",
    "halaman",
    "cahaya",
)


def norm_transisi(tr, default_dur=0.42):
    """Normalisasi spec transisi (str/dict/None) menjadi dict standar."""
    if tr is None:
        return {"jenis": "potong", "dur": 0.0}
    if isinstance(tr, str):
        tr = {"jenis": tr}
    d = dict(tr)
    raw = str(d.get("jenis", "fade")).strip().lower().replace("-", "_")
    jenis = TRANSISI_ALIAS.get(raw, raw)
    d["jenis"] = jenis
    d.setdefault("dur", 0.0 if jenis == "potong" else float(default_dur))
    return d


def sfx_transisi(jenis):
    """Kembalikan pasangan (nama_sfx, volume) atau None untuk jenis transisi tertentu."""
    k = TRANSISI_ALIAS.get(str(jenis).lower(), str(jenis).lower())
    if k in ("whip", "geser", "putar", "belah", "wipe_tiang", "wipe_diagonal"):
        return ("whoosh", 0.80)
    if k == "iris":
        return ("iris", 0.72)
    if k in ("zoom", "zoom_out", "kedip", "tirai", "blur_cross", "kotak"):
        return ("whoosh_lembut", 0.78)
    if k in ("flash", "luma", "cahaya"):
        return ("kilat", 0.82)
    if k == "halaman":
        return ("lipat", 0.85)
    if k == "glitch":
        return ("punch", 0.72)
    return None


def _zoom_crop(img, scale):
    W, H = img.size
    nw = max(2, int(round(W * scale)))
    nh = max(2, int(round(H * scale)))
    res = img.resize((nw, nh), Image.BILINEAR)
    if scale >= 1.0:
        x0 = (nw - W) // 2
        y0 = (nh - H) // 2
        return res.crop((x0, y0, x0 + W, y0 + H))
    canvas = Image.new("RGB", (W, H), (14, 16, 22))
    canvas.paste(res, ((W - nw) // 2, (H - nh) // 2))
    return canvas


def blend_transisi(A, B, p, tr=None, outline_col=OUT_DEFAULT):
    """Gabungkan frame A -> B pada progres p in [0, 1] sesuai spec transisi global."""
    tr = norm_transisi(tr)
    k = tr["jenis"]
    p = clamp(float(p), 0.0, 1.0)
    if p <= 0.0:
        return A
    if p >= 1.0 or k == "potong":
        return B if p >= 0.5 else A

    W, H = A.size
    e = ease_io(p)
    ol = tuple(outline_col) if outline_col is not None else OUT_DEFAULT

    if k == "fade":
        return Image.blend(A, B, e)

    if k == "fade_hitam":
        bg_col = tuple(tr.get("warna", (12, 14, 20)))
        black = Image.new("RGB", (W, H), bg_col)
        if p < 0.5:
            return Image.blend(A, black, ease_io(p * 2.0))
        return Image.blend(black, B, ease_io((p - 0.5) * 2.0))

    if k == "flash":
        flash_col = tuple(tr.get("warna", (255, 255, 255)))
        white = Image.new("RGB", (W, H), flash_col)
        if p < 0.5:
            return Image.blend(A, white, ease_out_cubic(p * 2.0))
        return Image.blend(white, B, ease_io((p - 0.5) * 2.0))

    if k == "kedip":
        im = A.copy() if p < 0.5 else B.copy()
        q = ease_io(p * 2.0) if p < 0.5 else 1.0 - ease_io((p - 0.5) * 2.0)
        d = ImageDraw.Draw(im)
        h = int(H * 0.52 * q)
        d.rectangle([0, 0, W, h], fill=(14, 16, 24))
        d.rectangle([0, H - h, W, H], fill=(14, 16, 24))
        return im

    if k == "iris":
        cx = float(tr.get("x", 0.5)) * W
        cy = float(tr.get("y", 0.5)) * H
        R_max = math.hypot(max(cx, W - cx), max(cy, H - cy))
        keluar = bool(tr.get("keluar", False))
        if keluar:
            # Iris-out ke hitam lalu iris-in ke B
            q = (1.0 - ease_io(p * 2.0)) if p < 0.5 else ease_io((p - 0.5) * 2.0)
            src = A if p < 0.5 else B
            R = R_max * q
            mask = Image.new("L", (W, H), 0)
            ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
            out = Image.composite(src, Image.new("RGB", (W, H), (14, 16, 24)), mask)
            return out
        R = R_max * e
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
        out = Image.composite(B, A, mask)
        if 0.02 < p < 0.98 and tr.get("garis", True):
            ImageDraw.Draw(out).ellipse([cx - R, cy - R, cx + R, cy + R], outline=ol, width=max(4, W // 160))
        return out

    if k in ("geser", "whip"):
        arah = str(tr.get("arah", "kiri")).lower()
        dx, dy = {"kiri": (-1, 0), "kanan": (1, 0), "atas": (0, -1), "bawah": (0, 1)}.get(arah, (-1, 0))
        ox, oy = int(-dx * W * e), int(-dy * H * e)
        canvas = Image.new("RGB", (W, H))
        canvas.paste(A, (ox, oy))
        canvas.paste(B, (ox + dx * W, oy + dy * H))
        if k == "whip":
            r = max(1, int(math.sin(math.pi * p) * max(6, W // 110)))
            canvas = canvas.filter(ImageFilter.GaussianBlur(r))
        return canvas

    if k == "zoom":
        # Zoom-in dinamis: A membesar cepat lalu dissolve mulus ke B yang ikut settling
        s_a = 1.0 + 0.85 * e
        s_b = 1.32 - 0.32 * e
        a_im = _zoom_crop(A, s_a)
        b_im = _zoom_crop(B, s_b)
        out = Image.blend(a_im, b_im, e)
        r = int(math.sin(math.pi * p) * max(3, W // 260))
        return out.filter(ImageFilter.GaussianBlur(r)) if r >= 1 else out

    if k == "zoom_out":
        s_a = max(0.45, 1.0 - 0.42 * e)
        s_b = 1.48 - 0.48 * e
        a_im = _zoom_crop(A, s_a)
        b_im = _zoom_crop(B, s_b)
        out = Image.blend(a_im, b_im, e)
        r = int(math.sin(math.pi * p) * max(2, W // 300))
        return out.filter(ImageFilter.GaussianBlur(r)) if r >= 1 else out

    if k == "wipe":
        arah = str(tr.get("arah", "kanan")).lower()
        out = A.copy()
        lw = max(4, W // 180)
        d = ImageDraw.Draw(out)
        if arah == "kiri":
            x = int(W * (1.0 - e))
            out.paste(B.crop((x, 0, W, H)), (x, 0))
            if tr.get("garis", True):
                d.line([(x, 0), (x, H)], fill=ol, width=lw)
        elif arah == "atas":
            y = int(H * (1.0 - e))
            out.paste(B.crop((0, y, W, H)), (0, y))
            if tr.get("garis", True):
                d.line([(0, y), (W, y)], fill=ol, width=lw)
        elif arah == "bawah":
            y = int(H * e)
            out.paste(B.crop((0, 0, W, y)), (0, 0))
            if tr.get("garis", True):
                d.line([(0, y), (W, y)], fill=ol, width=lw)
        else:  # kanan (default: sapuan kiri->kanan)
            x = int(W * e)
            out.paste(B.crop((0, 0, x, H)), (0, 0))
            if tr.get("garis", True):
                d.line([(x, 0), (x, H)], fill=ol, width=lw)
        return out

    if k == "wipe_diagonal":
        # Sapuan garis miring 45 derajat dari sudut ke sudut (mendukung arah kanan_bawah / kiri_bawah)
        arah_d = str(tr.get("arah", "kanan_bawah")).lower()
        skew = int(H * 0.42)
        mask = Image.new("L", (W, H), 0)
        if "kiri" in arah_d:
            x_top = int(W + skew - (W + skew * 2) * e)
            x_bot = x_top + skew
            ImageDraw.Draw(mask).polygon([(W + skew, 0), (x_top, 0), (x_bot, H), (W + skew, H)], fill=255)
        else:
            x_top = int(-skew + (W + skew * 2) * e)
            x_bot = x_top - skew
            ImageDraw.Draw(mask).polygon([(-skew, 0), (x_top, 0), (x_bot, H), (-skew, H)], fill=255)
        out = Image.composite(B, A, mask)
        if tr.get("garis", True) and 0.02 < p < 0.98:
            ImageDraw.Draw(out).line([(x_top, 0), (x_bot, H)], fill=ol, width=max(5, W // 150))
        return out

    if k == "wipe_tiang":
        # Transisi film ikonik: siluet tiang/pilar gelap menyapu cepat di depan lensa!
        arah = str(tr.get("arah", "kiri")).lower()
        bar_w = int(W * float(tr.get("lebar", 0.24)))
        col = tuple(tr.get("warna", (20, 22, 28)))
        edge_col = tuple(min(255, c + 24) for c in col)
        if arah == "kanan":
            cx = int(-bar_w * 0.6 + (W + bar_w * 1.2) * e)
            cut_x = clamp(cx, 0, W)
            out = A.copy()
            if cut_x > 0:
                out.paste(B.crop((0, 0, int(cut_x), H)), (0, 0))
        else:
            cx = int(W + bar_w * 0.6 - (W + bar_w * 1.2) * e)
            cut_x = clamp(cx, 0, W)
            out = A.copy()
            if cut_x < W:
                out.paste(B.crop((int(cut_x), 0, W, H)), (int(cut_x), 0))
        # Gambar siluet pilar foreground dengan tepi blur gerak lembut
        bar = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(bar)
        x0, x1 = int(cx - bar_w * 0.5), int(cx + bar_w * 0.5)
        bd.rectangle([x0, 0, x1, H], fill=col + (255,))
        # Highlight tipis di satu sisi tiang biar terasa 3D
        hl_w = max(6, bar_w // 12)
        bd.rectangle([x0, 0, x0 + hl_w, H], fill=edge_col + (210,))
        bar = bar.filter(ImageFilter.GaussianBlur(max(2, W // 220)))
        out = Image.alpha_composite(out.convert("RGBA"), bar).convert("RGB")
        return out

    if k == "putar":
        arah_s = -1.0 if str(tr.get("arah", "kanan")).lower() == "kiri" else 1.0
        ang = (180.0 * e * arah_s) if p < 0.5 else (-180.0 * (1.0 - e) * arah_s)
        src = A if p < 0.5 else B
        # Zoom otomatis menyesuaikan aspek rasio agar rotasi 180 derajat bebas sudut hitam
        diag_scale = math.hypot(W, H) / float(min(W, H))
        zoomed = _zoom_crop(src, 1.0 + (diag_scale - 1.0) * math.sin(math.pi * p))
        rot = zoomed.rotate(ang, resample=Image.BICUBIC)
        r = max(1, int(math.sin(math.pi * p) * max(7, W // 100)))
        return rot.filter(ImageFilter.GaussianBlur(r))

    if k == "belah":
        out = B.copy()
        lw = max(4, W // 180)
        d = ImageDraw.Draw(out)
        if str(tr.get("arah", "horizontal")).lower() == "vertikal":
            half = H // 2
            dy = int(half * e)
            if dy < half:
                out.paste(A.crop((0, 0, W, half)), (0, -dy))
                out.paste(A.crop((0, half, W, H)), (0, half + dy))
                d.line([(0, half - dy), (W, half - dy)], fill=ol, width=lw)
                d.line([(0, half + dy), (W, half + dy)], fill=ol, width=lw)
        else:
            half = W // 2
            dx = int(half * e)
            if dx < half:
                out.paste(A.crop((0, 0, half, H)), (-dx, 0))
                out.paste(A.crop((half, 0, W, H)), (half + dx, 0))
                d.line([(half - dx, 0), (half - dx, H)], fill=ol, width=lw)
                d.line([(half + dx, 0), (half + dx, H)], fill=ol, width=lw)
        return out

    if k == "tirai":
        n = max(3, int(tr.get("jumlah", 8)))
        vert = str(tr.get("arah", "vertikal")).lower() != "horizontal"
        out = A.copy()
        if vert:
            sw = W / float(n)
            for i in range(n):
                x0 = int(round(i * sw))
                x1 = int(round((i + 1) * sw))
                delay = (i / float(n)) * 0.25
                u = ease_io(clamp((p - delay) / max(0.05, 1.0 - 0.25)))
                bw = int(round((x1 - x0) * u))
                if bw > 0:
                    out.paste(B.crop((x0, 0, x0 + bw, H)), (x0, 0))
        else:
            sh = H / float(n)
            for i in range(n):
                y0 = int(round(i * sh))
                y1 = int(round((i + 1) * sh))
                delay = (i / float(n)) * 0.25
                u = ease_io(clamp((p - delay) / max(0.05, 1.0 - 0.25)))
                bh = int(round((y1 - y0) * u))
                if bh > 0:
                    out.paste(B.crop((0, y0, W, y0 + bh)), (0, y0))
        return out

    if k == "luma":
        # Film Burn / Light Leak hangat oranye-emas (mendukung pola: horizontal | radial)
        pola = str(tr.get("pola", "horizontal")).lower()
        base = np.asarray(Image.blend(A, B, e), dtype=np.float32)
        xs = np.linspace(0.0, 1.0, W, dtype=np.float32)[None, :]
        ys = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
        if pola == "radial":
            r = np.sqrt((xs - 0.5) ** 2 + (ys - 0.5) ** 2)
            ring_r = 0.05 + 0.85 * e
            wave = np.exp(-((r - ring_r) ** 2) / 0.045) * 0.95 + np.exp(-(r ** 2) / 0.28) * 0.35
        else:
            center = 1.25 - 1.50 * e
            wave = np.exp(-((xs - center) ** 2) / 0.14) * (0.65 + 0.35 * np.sin(ys * 4.5 + p * 6.0))
        glow = (math.sin(math.pi * p) ** 1.1) * wave
        leak = np.zeros_like(base)
        leak[:, :, 0] = 255.0 * glow * 1.10
        leak[:, :, 1] = 158.0 * glow * 0.92
        leak[:, :, 2] = 52.0 * glow * 0.55
        out = np.clip(base + leak, 0.0, 255.0).astype(np.uint8)
        return Image.fromarray(out)

    if k == "blur_cross":
        r = max(1, int(math.sin(math.pi * p) * max(8, W // 85)))
        src = Image.blend(A, B, e)
        return src.filter(ImageFilter.GaussianBlur(r))

    if k == "glitch":
        # RGB channel split + horizontal slice offset singkat ala film thriller/sci-fi
        strength = math.sin(math.pi * p)
        arr = np.asarray(A if p < 0.5 else B, dtype=np.uint8).copy()
        shift = max(2, int(strength * W * 0.032))
        out = arr.copy()
        # RGB split
        out[:, :, 0] = np.roll(arr[:, :, 0], shift, axis=1)
        out[:, :, 2] = np.roll(arr[:, :, 2], -shift, axis=1)
        # 7 pita glitch horizontal deterministik
        n_bands = 7
        for i in range(n_bands):
            by = int(((i * 0.14 + p * 0.37) % 0.92) * H)
            bh = max(4, int(H * (0.02 + 0.035 * ((i * 7) % 3) * 0.5)))
            bx = int(math.sin(p * 37.0 + i * 2.3) * W * 0.08 * strength)
            y2 = min(H, by + bh)
            out[by:y2] = np.roll(out[by:y2], bx, axis=1)
        return Image.fromarray(out)

    if k == "kotak":
        # Pixelate / mosaic membesar lalu kembali tajam
        factor = 1.0 + math.sin(math.pi * p) * float(tr.get("besar", 28.0))
        src = Image.blend(A, B, e)
        sw = max(8, int(W / factor))
        sh = max(8, int(H / factor))
        return src.resize((sw, sh), Image.NEAREST).resize((W, H), Image.NEAREST)

    if k == "halaman":
        # Efek membalik halaman kertas dengan bayangan lipatan lembut
        fold_x = int(W * (1.0 - e))
        out = B.copy()
        if fold_x > 0:
            # Sisi kiri masih halaman A yang sedikit menyusut saat terlipat
            out.paste(A.crop((0, 0, fold_x, H)), (0, 0))
            # Strip lipatan kertas + bayangan jatuh ke kanan
            curl_w = max(8, int(min(W * 0.12, math.sin(math.pi * p) * W * 0.16)))
            sh_w = max(6, int(curl_w * 0.9))
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            # Bayangan jatuh ke halaman B
            for k_i in range(sh_w):
                a = int(135 * (1.0 - k_i / float(sh_w)))
                xx = fold_x + k_i
                if 0 <= xx < W:
                    od.line([(xx, 0), (xx, H)], fill=(18, 16, 22, a), width=1)
            # Kilau lipatan kertas di sisi kiri fold_x
            for k_i in range(curl_w):
                u = k_i / float(curl_w)
                a = int(165 * (1.0 - u))
                xx = fold_x - k_i
                if 0 <= xx < W:
                    od.line([(xx, 0), (xx, H)], fill=(252, 248, 238, a), width=1)
            out = Image.alpha_composite(out.convert("RGBA"), ov).convert("RGB")
        return out

    if k == "cahaya":
        # Ledakan lens flare lembut dari pusat layar
        base = np.asarray(Image.blend(A, B, e), dtype=np.float32)
        xs = np.linspace(-1.0, 1.0, W, dtype=np.float32)[None, :]
        ys = np.linspace(-1.0, 1.0, H, dtype=np.float32)[:, None]
        r2 = xs * xs + ys * ys
        pulse = math.sin(math.pi * p) ** 1.25
        rad = np.exp(-r2 / max(0.08, 0.35 + 0.45 * pulse)) * pulse
        flare = np.zeros_like(base)
        flare[:, :, 0] = 255.0 * rad * 1.15
        flare[:, :, 1] = 236.0 * rad * 1.05
        flare[:, :, 2] = 190.0 * rad * 0.90
        out = np.clip(base + flare, 0.0, 255.0).astype(np.uint8)
        return Image.fromarray(out)

    return B if p >= 0.5 else A
