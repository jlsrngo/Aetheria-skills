# -*- coding: utf-8 -*-
"""
dunia.py - latar (set) gaya stikman: pastel datar + garis tepi hitam, lantai di y=0.

Tiap set = (belakang, depan):
  belakang(c, t, o) digambar SEBELUM tokoh; depan(c, t, o) SESUDAH tokoh (meja, selimut, semak depan).
o = opsi adegan: waktu (pagi|siang|sore|malam), jam, papan, warna, ...
Lapisan: c.set_depth(d) -> d<1 jauh (bergeser lebih sedikit saat kamera bergerak), d>1 dekat (foreground).
"""
import math, random, functools
from PIL import Image, ImageFilter
from stik import *

OW = 2.6
G_OC = (64, 52, 46)       # outline coklat-hangat halus gaya Ghibli/gouache (menggantikan hitam kaku)
G_SH = (76, 94, 122)      # warna bayangan jatuh biru-slate dingin (khas Ghibli & referensi Shinkai)
X0, X1 = -3200, 3200

# Palet langit Ghibli-Shinkai (cerulean biru kaya atas -> biru muda cerah -> cyan-putih berkabut cakrawala)
LANGIT = {
    "pagi":  ((54, 146, 212), (244, 236, 204)),
    "siang": ((18, 132, 212), (186, 234, 248)),
    "sore":  ((98, 92, 152),  (254, 198, 134)),
    "malam": ((16, 28, 66),   (48, 72, 124)),
}
# Mid-stop langit agar gradasi 3-tahap persis referensi langit cerulean Ghibli/Shinkai!
LANGIT_MID = {
    "pagi":  (138, 198, 232),
    "siang": (66, 178, 236),
    "sore":  (226, 132, 108),
    "malam": (28, 46, 94),
}
TINT = {
    "pagi":  ((255, 226, 168), 16),
    "siang": ((255, 255, 255), 0),
    "sore":  ((255, 142, 82),  34),
    "malam": ((18, 30, 84),    68),
}
TINT_INDOOR = {
    "pagi":  ((255, 232, 182), 14),
    "siang": ((255, 248, 234), 6),
    "sore":  ((255, 162, 94),  28),
    "malam": ((36, 36, 64),    28),   # malam dalam ruangan tetap hangat terang (bukan biru gelap pekat!)
}
TINT_FG = {"pagi": 0.45, "siang": 0.0, "sore": 0.55, "malam": 0.45}


def waktu_of(o):
    return o.get("waktu", "siang")


@functools.lru_cache(maxsize=12)
def _ghibli_wc_maps(w, h):
    """Peta tekstur kertas cat air (cold-press watercolor paper + pigment mottling) & gradasi cahaya hangat sinematik, di-cache super cepat via NumPy!"""
    import numpy as np
    rng = np.random.default_rng(1988)   # tahun Totoro :)
    # 1) Sapuan cat air frekuensi rendah (organic pigment wash / clouding)
    cw, ch = max(16, w // 28), max(16, h // 28)
    wash_s = rng.normal(0.0, 1.0, (ch, cw)).astype(np.float32)
    wash_im = Image.fromarray(np.clip((wash_s * 32 + 128), 0, 255).astype(np.uint8)).resize((w, h), Image.Resampling.BICUBIC)
    wash = (np.asarray(wash_im, dtype=np.float32) - 128.0) / 128.0

    # 2) Serat kertas cat air cold-press frekuensi sedang-halus (organic tooth)
    mw, mh = max(32, w // 4), max(32, h // 4)
    grain_m = rng.normal(0.0, 1.0, (mh, mw)).astype(np.float32)
    grain_im = Image.fromarray(np.clip((grain_m * 38 + 128), 0, 255).astype(np.uint8)).resize((w, h), Image.Resampling.BILINEAR)
    grain = (np.asarray(grain_im, dtype=np.float32) - 128.0) / 128.0

    # Gabungan tekstur kertas + pigmen cat air (bernilai sekitar -1..+1)
    tex = (wash * 0.58 + grain * 0.42).astype(np.float32)

    # 3) Peta pencahayaan sinematik lembut (warm sunlit key dari kanan-atas/kiri-atas + vinyet tepi sangat halus)
    yy = np.linspace(-1.0, 1.0, h, dtype=np.float32)[:, None]
    xx = np.linspace(-1.0, 1.0, w, dtype=np.float32)[None, :]
    r2 = xx * xx * 0.65 + yy * yy * 0.85
    vig = np.clip(1.0 - r2 * 0.085, 0.88, 1.0).astype(np.float32)
    sun_w = np.clip(1.0 - ((xx - 0.35) ** 2 * 0.55 + (yy + 0.65) ** 2 * 0.65), 0.0, 1.0).astype(np.float32)
    return tex, vig, sun_w


def _apply_watercolor_bg(c, wk="siang", indoor=False, strength=1.0):
    """Sentuhan akhir Ghibli Studio Art Style pada latar: tekstur kertas cat air halus + cahaya matahari hangat sinematik."""
    try:
        import numpy as np
        im = c.im
        w, h = im.size
        tex, vig, sun_w = _ghibli_wc_maps(w, h)
        arr = np.asarray(im, dtype=np.float32)
        rgb = arr[..., :3]

        # 1) Tekstur kertas cat air & pigmen gouache organik (sangat halus, berkelas, tidak kotor!)
        amp = (10.5 if indoor else 9.0) * strength
        # nada kertas sedikit hangat (krem katun)
        rgb[..., 0] += tex * (amp * 1.06)
        rgb[..., 1] += tex * (amp * 1.00)
        rgb[..., 2] += tex * (amp * 0.88)

        # 2) Cahaya sinematik hangat lembut & vinyet ambien Ghibli
        if wk != "malam":
            s_amt = (13.0 if wk == "siang" else (18.0 if wk == "pagi" else 22.0)) * (0.70 if indoor else 1.0) * strength
            rgb[..., 0] += sun_w * s_amt
            rgb[..., 1] += sun_w * (s_amt * 0.88)
            rgb[..., 2] += sun_w * (s_amt * 0.56)
        # vinyet tepi hangat/teduh yang halus (menyatukan komposisi bak film animasi klasik)
        rgb *= vig[..., None]

        arr[..., :3] = np.clip(rgb, 0.0, 255.0)
        new_im = Image.fromarray(arr.astype(np.uint8), mode=im.mode)
        c.im.paste(new_im)
    except Exception:
        pass


def tint(c, o, fg=False, indoor=False):
    w = waktu_of(o)
    tbl = TINT_INDOOR if indoor else TINT
    col, a = tbl.get(w, tbl["siang"])
    if fg:
        a = int(a * TINT_FG.get(w, 0.0))
    if a > 0:
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=col + (a,))
    if not fg and not o.get("tanpa_tekstur"):
        _apply_watercolor_bg(c, wk=w, indoor=indoor, strength=1.0)


def langit(c, o, sun=True, horizon=0.78, t=0.0):
    """Langit 3-tahap cerulean Ghibli-Shinkai (dalam di atas -> cerah di tengah -> kabut berkilau di cakrawala)."""
    w = waktu_of(o)
    top, bot = LANGIT.get(w, LANGIT["siang"])
    mid = LANGIT_MID.get(w, LANGIT_MID["siang"])
    # gradasi 2 segmen mulus (top -> mid -> bot)
    h_mid = horizon * 0.56
    c.gradient(top, mid, 0.0, h_mid)
    c.gradient(mid, bot, h_mid, min(1.0, horizon + 0.22))
    c.set_depth(0.15)
    if w == "malam":
        for i in range(56):
            x = ((i * 397) % 2800) - 1400
            y = -((i * 211) % 760) - 340
            tw = 0.60 + 0.40 * math.sin(t * 2.4 + i * 1.7)
            r = (2.2 + (i % 3) * 0.9) * tw
            c.ell(x, y, r, r, (255, 250, 224, int(190 + 60 * tw)))
        # bulan sabit bercahaya lembut TANPA outline hitam kasar!
        mx, my = 560, -680
        c.ell(mx, my, 175, 175, (216, 232, 255, 22))
        c.ell(mx, my, 110, 110, (242, 246, 255, 42))
        c.ell(mx, my, 64, 64, (255, 250, 214))
        c.ell(mx + 24, my - 14, 54, 54, mix(top, mid, 0.45))
    elif sun:
        sx, sy = {"pagi": (-580, -620), "siang": (620, -760), "sore": (-360, -340)}.get(w, (620, -760))
        if w == "siang":
            # siang cerah persis referensi Shinkai: pendaran matahari 12-lapis super lembut tanpa cincin banding!
            for si in range(12):
                k_s = 1.0 - si / 12.0
                r_s = 110 + 460 * k_s
                c.ell(sx, sy, r_s, r_s * 0.86, (255, 254, 242, 3))
        else:
            col = (255, 224, 136) if w == "pagi" else (255, 152, 92)
            for r_s, a_s in ((380, 10), (280, 14), (200, 18), (135, 26)):
                c.ell(sx, sy, r_s, r_s, col + (a_s,))
            c.ell(sx, sy, 68, 68, terang(col, 0.38))
            dir_s = 1 if sx < 0 else -1
            for b in range(3):
                bx = sx + dir_s * (140 + b * 260)
                c.poly([(sx, sy), (sx + dir_s * 75, sy + 20),
                        (bx + dir_s * 680, 140), (bx + dir_s * 440, 140)], col + (16,))
    c.set_depth(1.0)


# ================================================================= 20 STYLE AWAN PAINTERLY GHIBLI-SHINKAI
def _cloud_colors(w):
    """4 nada warna gouache awan per waktu dengan kontras 3D jelas: (rim_sun, cream_body, mid_shadow, deep_base)."""
    if w == "sore":
        return ((255, 244, 212), (252, 206, 174), (212, 144, 148), (146, 102, 134))
    if w == "pagi":
        return ((255, 252, 236), (236, 234, 224), (176, 198, 224), (128, 160, 198))
    if w == "malam":
        return ((114, 136, 182), (82, 102, 152), (52, 70, 118), (34, 48, 92))
    # siang cerah persis referensi Ghibli/Shinkai: puncak krem-putih terang -> tubuh mutiara -> bayangan biru-cerulean -> dasar biru-slate!
    return ((255, 253, 242), (230, 241, 249), (162, 198, 226), (116, 158, 198))


def _paint_cloud_puffs(c, x, y, s, puffs, cols, alpha=255):
    """Lukis awan gouache bergaya Ghibli-Shinkai 6-lapis: tepi kembang kol (cauliflower), lipatan bayangan dalam & sapuan cahaya matahari bertekstur!"""
    rim, body, mid, deep = cols
    fold = mix(mid, deep, 0.48)
    warm = mix(body, rim, 0.55)
    soft_mid = mix(body, mid, 0.52)

    def _ca(col, a_mul=1.0):
        a = int(min(255, alpha * a_mul))
        return col + (a,) if a < 255 else col

    # seed deterministik unik per awan agar setiap awan punya pahatan organik tersendiri
    seed_c = int(round(x * 7 + y * 13)) + len(puffs) * 31
    rng = random.Random(seed_c)

    # Pra-hitung gumpalan kembang kol (sub-billows) untuk setiap puff utama agar siluet & isi TIDAK pernah polos!
    sculpted = []
    for idx_p, (dx, dy, rx, ry) in enumerate(puffs):
        px = x + dx * s
        py = y + dy * s
        prx = rx * s
        pry = ry * s
        is_big = max(prx, pry) >= 58.0
        n_ring = 9 if is_big else (6 if max(prx, pry) >= 32.0 else 4)
        ring = []
        for k in range(n_ring):
            ang = (k / n_ring) * math.tau + rng.uniform(-0.24, 0.24)
            dist = rng.uniform(0.56, 0.88)
            bx = px + math.cos(ang) * prx * dist
            by = py + math.sin(ang) * pry * dist
            brx = prx * rng.uniform(0.32, 0.52)
            bry = pry * rng.uniform(0.32, 0.52)
            ring.append((bx, by, brx, bry, ang))
        # gumpalan internal tambahan khusus untuk awan besar (memecah bidang polos di tengah awan!)
        inners = []
        n_in = 6 if is_big else (3 if max(prx, pry) >= 32.0 else 1)
        for k in range(n_in):
            ix = px + rng.uniform(-prx * 0.54, prx * 0.42)
            iy = py + rng.uniform(-pry * 0.54, pry * 0.42)
            irx = prx * rng.uniform(0.28, 0.48)
            iry = pry * rng.uniform(0.26, 0.46)
            inners.append((ix, iy, irx, iry))
        sculpted.append((dx, dy, px, py, prx, pry, is_big, ring, inners))

    # 0) Sapuan kabut tepi halus (soft wispy atmospheric halo agar tidak terasa seperti tempelan vektor tajam!)
    for _, _, px, py, prx, pry, is_big, ring, _ in sculpted:
        if is_big:
            c.ell(px - prx * 0.08, py - pry * 0.06, prx * 1.12, pry * 1.08, _ca(warm, 0.16))
        for bx, by, brx, bry, ang in ring:
            if math.sin(ang) < 0.25:
                c.ell(bx - brx * 0.14, by - bry * 0.14, brx * 1.16, bry * 1.10, _ca(body, 0.22))

    # 1) Dasar bayangan dalam (deep underbelly) + tonjolan tepi kembang kol bawah-kanan
    deep_c = _ca(deep, 0.94)
    for _, _, px, py, prx, pry, _, ring, _ in sculpted:
        c.ell(px + 9 * s, py + 13 * s, prx * 1.02, pry * 0.98, deep_c)
        for bx, by, brx, bry, _ in ring:
            c.ell(bx + 7 * s, by + 10 * s, brx * 1.02, bry * 0.98, deep_c)

    # 2) Bayangan tengah biru-lavender (mid-shadow) & kantong lipatan bayangan internal
    mid_c = _ca(mid, 0.96)
    fold_c = _ca(fold, 0.86)
    for _, dy, px, py, prx, pry, is_big, ring, inners in sculpted:
        c.ell(px + 3 * s, py + 5 * s, prx * 0.94, pry * 0.90, mid_c)
        for bx, by, brx, bry, ang in ring:
            c.ell(bx + 2 * s, by + 4 * s, brx * 0.95, bry * 0.92, mid_c)
        # pahatan cekungan bayangan di sisi bawah-kanan tiap gumpalan besar!
        if is_big:
            for ix, iy, irx, iry in inners:
                if iy > py - pry * 0.12 or ix > px - prx * 0.08:
                    c.ell(ix + 10 * s, iy + 11 * s, irx * 0.95, iry * 0.85, fold_c)

    # 3) Massa utama & pahatan gumpalan kembang kol (cauliflower domes) bertingkat — setiap gumpalan punya bayangan lipatan sendiri!
    body_c = _ca(body, 1.0)
    smid_c = _ca(soft_mid, 0.88)
    mid_in_c = _ca(mid, 0.72)
    for _, dy, px, py, prx, pry, is_big, ring, inners in sculpted:
        if dy < 44:
            c.ell(px - 6 * s, py - 6 * s, prx * 0.80, pry * 0.76, body_c)
            for bx, by, brx, bry, ang in ring:
                if math.sin(ang) < 0.45 or math.cos(ang) < 0.25:
                    # bayangan lipatan di bawah-kanan tiap tonjolan tepi -> lalu kubah terang di atas-kirinya!
                    c.ell(bx + 3 * s, by + 4 * s, brx * 0.90, bry * 0.84, smid_c)
                    c.ell(bx - 5 * s, by - 5 * s, brx * 0.86, bry * 0.82, body_c)
            # pahatan kembang kol internal di tengah awan besar (khas lukisan awan Makoto Shinkai & Ghibli!)
            if is_big:
                for ix, iy, irx, iry in inners:
                    c.ell(ix + 10 * s, iy + 12 * s, irx * 0.94, iry * 0.84, mid_in_c)
                    c.ell(ix + 5 * s, iy + 6 * s, irx * 0.88, iry * 0.80, smid_c)
                    c.ell(ix - 4 * s, iy - 5 * s, irx * 0.80, iry * 0.74, body_c)

    # 4) Puncak kilau matahari hangat (sunlit gouache ridges) bertingkat di sisi atas-kiri + punggung awan besar!
    warm_c = _ca(warm, 0.96)
    rim_c = _ca(rim, 1.0)
    for _, dy, px, py, prx, pry, is_big, ring, inners in sculpted:
        if dy < 22:
            c.ell(px - 11 * s, py - 12 * s, prx * 0.58, pry * 0.50, warm_c)
            for bx, by, brx, bry, ang in ring:
                if math.sin(ang) < 0.14 and math.cos(ang) < 0.42:
                    c.ell(bx - 6 * s, by - 6 * s, brx * 0.74, bry * 0.66, warm_c)
                    c.ell(bx - 10 * s, by - 10 * s, brx * 0.54, bry * 0.46, rim_c)
            # undakan puncak terang + bayangan lembut di bagian dalam awan besar (benar-benar bervolume 3D!)
            if is_big:
                for ix, iy, irx, iry in inners:
                    if iy < py + pry * 0.22:
                        c.ell(ix - 7 * s, iy - 8 * s, irx * 0.66, iry * 0.56, warm_c)
                        c.ell(ix - 10 * s, iy - 11 * s, irx * 0.46, iry * 0.36, rim_c)
        if dy < -18:
            c.ell(px - 14 * s, py - 15 * s, prx * 0.44, pry * 0.36, rim_c)

    # 5) Serat sapuan kuas halus melayang tipis di pinggir awan besar (sentuhan cat air tangan!)
    for _, dy, px, py, prx, pry, is_big, _, _ in sculpted:
        if is_big and dy < 10:
            for wi in range(2):
                wx = px + rng.uniform(-prx * 1.05, prx * 0.95)
                wy = py + rng.uniform(-pry * 0.95, pry * 0.25)
                c.ell(wx, wy, rng.uniform(12, 24) * s, rng.uniform(6, 13) * s, _ca(rim if wi == 0 else body, 0.46))


def _paint_cirrus_streak(c, x, y, s, angle_deg, length, cols, seed=0):
    """Sapuan awan cirrus berbulu halus organik (multi-klaster cat air menyebar lembut persis referensi Shinkai!)."""
    rim, body, mid, _ = cols
    rad = math.radians(angle_deg)
    ca, sa = math.cos(rad), math.sin(rad)
    nx, ny = -sa, ca
    rng = random.Random(seed + 17)
    n_seg = 16
    for i in range(n_seg):
        u = i / (n_seg - 1)
        p = u - 0.5
        t_env = math.sin(u * math.pi)
        # kurva S lembut agar awan cirrus mengalir organik, bukan batang lurus kaku!
        curve_lat = math.sin(u * math.tau * 0.85 + seed) * 28.0 * s
        dist = p * length * s
        # 2-3 gumpalan serat kecil menyebar di setiap titik sepanjang arus angin
        for sub in range(3):
            lat = curve_lat + (rng.uniform(-42, 42) * (0.35 + t_env)) * s
            d_sub = dist + rng.uniform(-24, 24) * s
            cx = x + ca * d_sub + nx * lat
            cy = y + sa * d_sub + ny * lat
            rx = (22 + 34 * t_env + rng.uniform(-8, 16)) * s * (0.65 if sub == 2 else 1.0)
            ry = (9 + 15 * t_env + rng.uniform(-3, 7)) * s * (0.7 if sub == 2 else 1.0)
            a_m = int((34 + 44 * t_env) * (0.7 if sub == 2 else 1.0))
            a_r = int((56 + 74 * t_env) * (0.75 if sub == 2 else 1.0))
            pts = []
            for k in range(10):
                aa = k * math.tau / 10
                lx, ly = math.cos(aa) * rx, math.sin(aa) * ry
                pts.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
            c.poly(pts, mid + (a_m,))
            pts2 = []
            for k in range(10):
                aa = k * math.tau / 10
                lx, ly = math.cos(aa) * rx * 0.72 - 3 * s, math.sin(aa) * ry * 0.65 - 2 * s
                pts2.append((cx + lx * ca - ly * sa, cy + lx * sa + ly * ca))
            c.poly(pts2, (rim if sub == 0 else body) + (a_r,))


def awan(c, x, y, s=1.0, col=(255, 255, 255), menjulang=False, gaya=None, waktu="siang"):
    """Primitif awan gouache Ghibli tanpa outline: kumulus, menara, gumpal_lebar, puncak_jauh, tipis, cirrus_diag, riak, anvil."""
    if gaya is None:
        gaya = "kumulus" if menjulang else "gumpal_lebar"
    cols = _cloud_colors(waktu)
    if gaya == "cirrus_diag":
        _paint_cirrus_streak(c, x, y, s, 38, 360, cols, seed=int(abs(x)))
        return
    if gaya == "cirrus_kiri":
        _paint_cirrus_streak(c, x, y, s, -28, 340, cols, seed=int(abs(x)) + 5)
        return
    if gaya == "tipis":
        _paint_cirrus_streak(c, x, y, s, 6, 320, cols, seed=int(abs(x)) + 11)
        return
    if gaya == "riak":
        puffs = [(-150, 8, 46, 16), (-92, -6, 52, 18), (-32, 6, 48, 17), (26, -8, 54, 19),
                 (88, 4, 46, 16), (146, -4, 42, 15), (-60, 18, 44, 14), (58, 16, 44, 14)]
        _paint_cloud_puffs(c, x, y, s, puffs, cols, alpha=210)
        return
    if gaya == "puncak_jauh":
        puffs = [(-175, 28, 86, 40), (-82, 8, 96, 54), (18, -14, 108, 64), (118, 8, 88, 48), (198, 28, 74, 36)]
    elif gaya == "menara":
        puffs = [
            (-146, 52, 86, 52), (-58, 56, 98, 58), (44, 52, 102, 56), (138, 44, 82, 48),
            (-112, -8, 86, 68), (-24, -26, 106, 86), (72, -12, 88, 70),
            (-64, -96, 84, 76), (26, -112, 92, 82), (92, -74, 64, 58),
            (-18, -178, 76, 72), (46, -162, 56, 52), (-2, -236, 54, 50), (32, -214, 38, 36),
        ]
    elif gaya == "anvil":
        # awan cumulonimbus asimetris megah (organik bertingkat, bukan jamur simetris!)
        puffs = [
            (-154, 48, 86, 46), (-52, 52, 98, 52), (56, 46, 94, 48), (146, 38, 76, 42),
            (-96, -10, 82, 62), (-4, -22, 96, 68), (82, -16, 78, 56),
            (-64, -78, 80, 62), (26, -92, 88, 66), (94, -72, 66, 48),
            (-118, -124, 92, 44), (-18, -148, 112, 54), (78, -138, 96, 46), (156, -118, 72, 34),
            (-42, -196, 72, 44), (36, -184, 64, 38),
        ]
    elif gaya == "kumulus":
        puffs = [
            (-118, 42, 72, 50), (-48, 48, 86, 54), (36, 46, 92, 54), (114, 38, 74, 48),
            (-86, -14, 76, 62), (-14, -28, 94, 78), (64, -16, 80, 64),
            (-42, -88, 72, 64), (26, -96, 78, 68), (80, -64, 54, 48),
            (0, -148, 60, 56), (42, -134, 44, 42),
        ]
    else:  # gumpal_lebar
        puffs = [
            (-126, 18, 68, 28), (-46, 22, 82, 32), (42, 20, 80, 30), (122, 16, 62, 26),
            (-72, -12, 68, 38), (6, -26, 86, 46), (78, -10, 64, 36),
            (-18, -50, 56, 32), (38, -42, 48, 28),
        ]
    _paint_cloud_puffs(c, x, y, s, puffs, cols)


# 20 FORMASI & GAYA AWAN UNIK (setiap scene otomatis berbeda, atau pilih via o["awan_style"] = 0..19 / nama!)
AWAN_STYLES = [
    # 0: pesisir_shinkai (PERSIS REFERENSI USER: cumulus cakrawala + cirrus diagonal panjang kanan-atas!)
    ("pesisir_shinkai", [
        (-880, -250, 1.25, "puncak_jauh"), (-180, -240, 1.35, "kumulus"), (460, -230, 1.15, "puncak_jauh"),
        (980, -250, 1.20, "gumpal_lebar"), (360, -680, 1.35, "cirrus_diag"), (-680, -560, 1.10, "cirrus_diag"),
    ]),
    # 1: menara_laputa (menara cumulus megah di kiri-tengah + cirrus kanan)
    ("menara_laputa", [
        (-480, -320, 1.48, "menara"), (620, -260, 1.25, "puncak_jauh"),
        (460, -690, 1.15, "cirrus_kiri"), (-1180, -540, 0.95, "tipis"), (1160, -580, 0.95, "gumpal_lebar"),
    ]),
    # 2: cirrus_sapuan (langit cerulean luas + 6 sapuan cirrus diagonal tersapu angin)
    ("cirrus_sapuan", [
        (-740, -680, 1.30, "cirrus_diag"), (-120, -760, 1.25, "cirrus_diag"), (520, -640, 1.40, "cirrus_diag"),
        (-420, -440, 1.05, "cirrus_diag"), (260, -420, 1.10, "tipis"), (960, -520, 1.15, "cirrus_diag"),
    ]),
    # 3: gumpal_kembar (dua bukit awan cumulus seimbang kiri & kanan, langit tengah lapang!)
    ("gumpal_kembar", [
        (-760, -310, 1.32, "kumulus"), (740, -320, 1.36, "kumulus"),
        (-60, -740, 1.05, "tipis"), (240, -640, 0.85, "cirrus_kiri"), (-1260, -600, 0.85, "gumpal_lebar"),
    ]),
    # 4: pita_cakrawala (barisan awan cumulus lembut memanjang rendah di cakrawala)
    ("pita_cakrawala", [
        (-1120, -220, 1.35, "puncak_jauh"), (-440, -210, 1.28, "gumpal_lebar"), (220, -225, 1.38, "puncak_jauh"),
        (880, -215, 1.30, "gumpal_lebar"), (-280, -680, 1.00, "tipis"), (520, -740, 0.95, "cirrus_kiri"),
    ]),
    # 5: kabut_pagi (lapisan awan tipis datar bertingkat tenang)
    ("kabut_pagi", [
        (-760, -520, 1.35, "tipis"), (80, -640, 1.45, "tipis"), (780, -490, 1.30, "tipis"),
        (-340, -320, 1.25, "gumpal_lebar"), (540, -300, 1.15, "gumpal_lebar"), (-1160, -340, 1.05, "tipis"),
    ]),
    # 6: badai_cerah (awan anvil megah di kanan + serpihan awan melayang ke kiri)
    ("badai_cerah", [
        (480, -330, 1.42, "anvil"), (-660, -280, 1.18, "puncak_jauh"),
        (-380, -640, 1.10, "cirrus_kiri"), (-960, -560, 0.92, "gumpal_lebar"), (1180, -660, 0.90, "tipis"),
    ]),
    # 7: riak_domba (awan altocumulus bergerombol lembut seperti bulu domba di langit tinggi)
    ("riak_domba", [
        (-680, -660, 1.25, "riak"), (-40, -720, 1.32, "riak"), (640, -620, 1.22, "riak"),
        (-360, -450, 1.05, "riak"), (380, -440, 1.00, "riak"), (-980, -270, 1.15, "puncak_jauh"),
    ]),
    # 8: lengkung_angin (sapuan awan mengalir diagonal dari kiri-bawah ke kanan-atas)
    ("lengkung_angin", [
        (-840, -300, 1.22, "gumpal_lebar"), (-420, -440, 1.15, "cirrus_kiri"),
        (60, -590, 1.28, "cirrus_kiri"), (560, -720, 1.35, "cirrus_kiri"),
        (820, -280, 1.20, "puncak_jauh"), (-1180, -620, 0.90, "tipis"),
    ]),
    # 9: kumulus_tengah (satu kubah cumulus megah tepat di tengah belakang + cirrus tepi)
    ("kumulus_tengah", [
        (20, -310, 1.52, "kumulus"), (-820, -620, 1.15, "cirrus_diag"),
        (820, -640, 1.15, "cirrus_kiri"), (-1140, -260, 1.10, "puncak_jauh"), (1120, -260, 1.10, "puncak_jauh"),
    ]),
    # 10: tiga_pulau (3 pulau awan gumpal melayang terpisah di 3 ketinggian)
    ("tiga_pulau", [
        (-640, -620, 1.18, "gumpal_lebar"), (80, -360, 1.28, "gumpal_lebar"), (680, -680, 1.12, "gumpal_lebar"),
        (-1020, -310, 1.05, "tipis"), (960, -320, 1.05, "tipis"),
    ]),
    # 11: tirai_tipis (serat halus cat air bertingkat di seluruh langit)
    ("tirai_tipis", [
        (-620, -740, 1.40, "tipis"), (280, -780, 1.35, "tipis"), (-180, -560, 1.45, "tipis"),
        (660, -520, 1.30, "tipis"), (-860, -380, 1.20, "tipis"), (160, -310, 1.15, "gumpal_lebar"),
    ]),
    # 12: puncak_kiri (menara cumulus tinggi di kiri + horizon landai kanan)
    ("puncak_kiri", [
        (-680, -330, 1.46, "menara"), (160, -240, 1.24, "puncak_jauh"),
        (820, -260, 1.18, "gumpal_lebar"), (420, -660, 1.25, "cirrus_diag"), (-120, -760, 1.00, "tipis"),
    ]),
    # 13: puncak_kanan (menara cumulus tinggi di kanan + cirrus melintang kiri)
    ("puncak_kanan", [
        (660, -330, 1.44, "menara"), (-220, -245, 1.22, "puncak_jauh"),
        (-860, -280, 1.15, "gumpal_lebar"), (-460, -680, 1.25, "cirrus_kiri"), (80, -760, 1.00, "tipis"),
    ]),
    # 14: samudra_awan (lautan awan tebal rendah di dasar cakrawala, langit atas bersih biru dalam)
    ("samudra_awan", [
        (-1160, -210, 1.48, "puncak_jauh"), (-520, -220, 1.50, "puncak_jauh"), (140, -215, 1.52, "puncak_jauh"),
        (780, -220, 1.48, "puncak_jauh"), (1320, -210, 1.40, "puncak_jauh"), (-180, -740, 0.90, "tipis"),
    ]),
    # 15: gelombang_sore (gumpalan pipih berlapis horisontal + riak tipis di atas)
    ("gelombang_sore", [
        (-680, -360, 1.35, "gumpal_lebar"), (420, -390, 1.40, "gumpal_lebar"),
        (-120, -580, 1.28, "riak"), (720, -660, 1.15, "tipis"), (-960, -640, 1.10, "tipis"),
    ]),
    # 16: spiral_angin (deretan sapuan cirrus bersilangan dinamis di langit tinggi)
    ("spiral_angin", [
        (-540, -680, 1.25, "cirrus_diag"), (220, -720, 1.30, "cirrus_kiri"),
        (680, -520, 1.22, "cirrus_diag"), (-220, -480, 1.18, "cirrus_kiri"),
        (-820, -260, 1.15, "gumpal_lebar"), (560, -250, 1.15, "puncak_jauh"),
    ]),
    # 17: kubah_rendah (dua kubah cumulus rendah lembut membingkai kiri & kanan bawah)
    ("kubah_rendah", [
        (-640, -240, 1.45, "kumulus"), (680, -245, 1.38, "kumulus"),
        (0, -680, 1.18, "riak"), (-980, -640, 0.95, "cirrus_diag"), (980, -620, 0.95, "cirrus_kiri"),
    ]),
    # 18: cerah_minimal (langit cerulean super jernih dengan hanya 3 sapuan cirrus halus)
    ("cerah_minimal", [
        (-520, -660, 1.25, "cirrus_diag"), (440, -700, 1.30, "cirrus_kiri"),
        (120, -260, 1.15, "gumpal_lebar"), (-960, -250, 1.00, "puncak_jauh"),
    ]),
    # 19: katedral_awan (3 lapis menara cumulus megah ala The Wind Rises!)
    ("katedral_awan", [
        (-840, -280, 1.35, "kumulus"), (-60, -340, 1.48, "menara"), (820, -300, 1.38, "anvil"),
        (-440, -700, 1.18, "cirrus_diag"), (480, -720, 1.15, "cirrus_kiri"),
    ]),
]

# Pemetaan default style awan per scene agar SETIAP latar outdoor punya langit & awan berbeda!
SCENE_AWAN_MAP = {
    "pantai": 0,        # pesisir_shinkai (persis referensi user!)
    "rumah_depan": 1,   # menara_laputa
    "jalan": 8,         # lengkung_angin
    "sekolah_luar": 3,  # gumpal_kembar
    "lapangan": 18,     # cerah_minimal
    "taman": 19,        # katedral_awan
    "padang": 12,       # puncak_kiri
    "kota": 4,          # pita_cakrawala
    "kamar": 5,         # kabut_pagi (di jendela)
    "kelas": 2,         # cirrus_sapuan
    "kafe": 7,          # riak_domba
    "ruang_belajar": 10,# tiga_pulau
    "meja_makan": 15,   # gelombang_sore
    "ruang_tamu": 17,   # kubah_rendah
}


def _resolve_awan_style(o, scene_key=None):
    st = o.get("awan_style")
    if isinstance(st, int):
        return st % len(AWAN_STYLES)
    if isinstance(st, str):
        for idx, (nm, _) in enumerate(AWAN_STYLES):
            if nm == st:
                return idx
        return abs(hash(st)) % len(AWAN_STYLES)
    if scene_key in SCENE_AWAN_MAP:
        return SCENE_AWAN_MAP[scene_key]
    return 0


def awan_set(c, o, n=6, t=0.0, scene_key=None):
    """Gambar 1 dari 20 formasi awan Ghibli-Shinkai (tidak identik antar-scene!) + kabut cakrawala & burung."""
    w = waktu_of(o)
    style_idx = _resolve_awan_style(o, scene_key)
    _, specs = AWAN_STYLES[style_idx]
    c.set_depth(0.18)
    drift = t * (8.0 if w == "malam" else 11.0)
    # pada malam hari tetap tampilkan 2-3 siluet awan malam tipis agar langit malam berdimensi!
    lim = min(3, len(specs)) if w == "malam" else len(specs)
    for ax0, ay0, sc, gy in specs[:lim]:
        spd = 0.45 if gy in ("menara", "anvil", "kumulus", "puncak_jauh") else 0.95
        ax = ((ax0 + drift * spd + 2200) % 4400) - 2200
        awan(c, ax, ay0, sc, gaya=gy, waktu=w)
    # kabut atmosferik cakrawala khas Ghibli/Shinkai (memisahkan langit dengan daratan dengan mulus!)
    if w == "malam":
        haze = (42, 62, 110, 62)
    elif w == "sore":
        haze = (254, 198, 144, 88)
    elif w == "pagi":
        haze = (242, 238, 214, 78)
    else:
        haze = (206, 240, 250, 74)
    c.rect(X0, -170, X1, 35, haze)
    if w != "malam":
        c.set_depth(0.24)
        bcol = (248, 252, 255) if w == "siang" else ((118, 134, 158) if w == "pagi" else (112, 74, 86))
        for bi in range(3):
            bx = ((-420 + style_idx * 90 + bi * 95 + t * (42 + bi * 4) + 1800) % 3600) - 1800
            by = -600 - (style_idx % 3) * 40 - bi * 32 + math.sin(t * 2.2 + bi) * 10
            flap = math.sin(t * 7.5 + bi * 1.9) * 6.5
            c.curve([(bx - 13, by - flap), (bx - 3, by - 3), (bx, by + 2)], bcol, 2.2)
            c.curve([(bx, by + 2), (bx + 3, by - 3), (bx + 13, by - flap)], bcol, 2.2)
    c.set_depth(1.0)


def bukit_berlapis(c, o, y0=0):
    """3 lapis pegunungan & bukit atmosferik Ghibli dengan kabut lembah cat air & puncak tersinari matahari."""
    w = waktu_of(o)
    if w == "malam":
        c1, c2, c3 = (32, 46, 88), (26, 42, 76), (24, 50, 68)
        mist = (46, 66, 112)
    elif w == "sore":
        c1, c2, c3 = (182, 128, 146), (150, 108, 124), (112, 122, 92)
        mist = (252, 206, 154)
    elif w == "pagi":
        c1, c2, c3 = (146, 192, 224), (118, 178, 192), (108, 178, 126)
        mist = (244, 242, 224)
    else:
        c1, c2, c3 = (122, 184, 222), (88, 162, 176), (92, 174, 114)
        mist = (224, 242, 248)
    c.set_depth(0.28)
    c.blob([(-2200, y0 + 20), (-1650, y0 - 290), (-1050, y0 - 170), (-420, y0 - 340),
            (240, y0 - 180), (920, y0 - 310), (1580, y0 - 190), (2200, y0 + 20)], c1, 0)
    # kabut atmosferik tipis di kaki pegunungan jauh (kedalaman lukisan Kazuo Oga!)
    c.rect(-2400, y0 - 110, 2400, y0 + 20, mist + (46,))
    c.set_depth(0.42)
    c.blob([(-2200, y0 + 20), (-1500, y0 - 200), (-820, y0 - 110), (-140, y0 - 220),
            (540, y0 - 120), (1240, y0 - 210), (1950, y0 - 90), (2200, y0 + 20)], c2, 0)
    c.rect(-2400, y0 - 58, 2400, y0 + 20, mist + (34,))
    c.set_depth(0.58)
    c.blob([(-2200, y0 + 20), (-1350, y0 - 120), (-620, y0 - 68), (80, y0 - 135),
            (840, y0 - 72), (1560, y0 - 125), (2200, y0 + 20)], c3, 0)
    # highlight hangat matahari di punggung bukit dekat
    if w != "malam":
        c.blob([(-2200, y0 - 22), (-1350, y0 - 120), (-620, y0 - 68), (80, y0 - 135),
                (840, y0 - 72), (1560, y0 - 125), (2200, y0 - 22),
                (2200, y0 - 5), (1560, y0 - 92), (840, y0 - 44), (80, y0 - 102),
                (-620, y0 - 42), (-1350, y0 - 88), (-2200, y0 - 5)], terang(c3, 0.22) + (115,), 0)
    c.set_depth(1.0)


def lantai(c, col, y1=1400, garis=None, step=0):
    c.rect(X0, 0, X1, y1, col)
    # variasi nada papan hangat lembut (bukan satu bidang datar polos!)
    c.rect(X0, 28, X1, 120, terang(col, 0.05))
    c.rect(X0, 210, X1, 340, gelap(col, 0.04))
    # bayangan ambient occlusion lembut di pertemuan lantai & dinding (khas interior Ghibli!)
    c.rect(X0, 0, X1, 28, gelap(col, 0.14))
    c.rect(X0, 0, X1, 10, gelap(col, 0.22))
    c.line([(X0, 0), (X1, 0)], G_OC, 2.6)
    if garis:
        for i in range(1, 14):
            yy = i * i * 6 + 14
            if yy < y1:
                c.line([(X0, yy), (X1, yy)], garis, 2.0, False)


def dinding(c, col, atas=-1700):
    # dinding gouache bergradasi halus + sapuan cat air/plester lembut (tidak datar polos!)
    c.gradient(gelap(col, 0.09), col, 0.0, 0.78)
    for ox, oy, rx, ry, al in ((-680, -640, 420, 210, 16), (520, -560, 460, 220, 18), (-120, -420, 380, 180, 14), (240, -720, 340, 160, 14)):
        c.ell(ox, oy, rx, ry, terang(col, 0.16) + (al,))
    for ox, oy, rx, ry, al in ((-880, -340, 320, 170, 14), (760, -320, 360, 180, 14)):
        c.ell(ox, oy, rx, ry, gelap(col, 0.12) + (al,))
    c.rect(X0, -40, X1, 0, gelap(col, 0.06))


def _kupu_kupu_ghibli(c, x0, y0, t, col=(250, 232, 148), seed=0, s=1.0):
    """Kupu-kupu mungil Ghibli terbang santai & alami di atas bunga (tidak lebay, kepakan sayap lembut!)."""
    ang = t * 0.65 + seed * 1.9
    x = x0 + math.sin(ang) * 92 * s + math.cos(ang * 0.55) * 34 * s
    y = y0 + math.sin(ang * 1.8 + 0.7) * 24 * s
    flap = 0.28 + 0.72 * abs(math.cos(t * 9.5 + seed * 2.3))
    w_r = 10.5 * s * flap
    h_r = 7.5 * s
    sh = gelap(col, 0.22)
    # 2 sayap kiri-kanan organik lembut + tubuh mungil
    c.ell(x - w_r * 0.75, y - h_r * 0.35, w_r, h_r, col, 1.0, G_OC)
    c.ell(x + w_r * 0.75, y - h_r * 0.35, w_r, h_r, sh, 1.0, G_OC)
    c.ell(x - w_r * 0.55, y + h_r * 0.45, w_r * 0.72, h_r * 0.68, col)
    c.ell(x + w_r * 0.55, y + h_r * 0.45, w_r * 0.72, h_r * 0.68, sh)
    c.line([(x, y - 4 * s), (x, y + 6 * s)], G_OC, 2.0 * s)


def _kucing_jalan(c, t, y_ground=10, seed=0, col=(214, 152, 92), arah=1, speed=34.0, s=0.72):
    """Kucing kampung Ghibli kecil berjalan santai melintas di latar belakang (langkah pelan & ekor melambai alami!)."""
    d = 1 if arah >= 0 else -1
    span = 2500.0
    pos = ((t * speed + seed * 430.0) % span) - span * 0.5
    x = pos * d
    step = t * 5.2 + seed
    bob = abs(math.sin(step)) * 2.4 * s
    yy = y_ground - bob
    sh = gelap(col, 0.18)
    belly = terang(col, 0.38)
    # bayangan lembut di lantai/trotoar
    c.ell(x, y_ground + 2 * s, 32 * s, 6.5 * s, (46, 52, 62, 52))
    # ekor melengkung santai bergoyang
    tw = math.sin(t * 2.8 + seed) * 10 * s
    c.curve([(x - 24 * s * d, yy - 24 * s), (x - 42 * s * d, yy - 38 * s + tw * 0.4),
             (x - 36 * s * d + tw * 0.5, yy - 58 * s)], col, 6.2 * s)
    # 4 kaki melangkah bergantian pelan
    for lx_off, ph in ((-16, 0.0), (-8, math.pi), (10, math.pi * 0.5), (18, math.pi * 1.5)):
        sw = math.sin(step + ph) * 6.5 * s * d
        c.line([(x + lx_off * s * d, yy - 16 * s), (x + lx_off * s * d + sw, y_ground)], sh if ph > 1.5 else col, 5.2 * s)
    # badan & perut krem lembut
    c.ell(x, yy - 22 * s, 26 * s, 14 * s, col, 1.8 * s, G_OC)
    c.ell(x + 2 * s * d, yy - 18 * s, 16 * s, 7 * s, belly)
    # kepala + telinga segitiga + wajah ramah mungil
    hx, hy = x + 24 * s * d, yy - 34 * s
    c.ell(hx, hy, 14 * s, 12.5 * s, col, 1.8 * s, G_OC)
    for ex_o in (-6, 5):
        c.poly([(hx + (ex_o - 3) * s * d, hy - 9 * s), (hx + ex_o * s * d, hy - 21 * s),
                (hx + (ex_o + 4) * s * d, hy - 9 * s)], col, 1.4 * s, G_OC)
    c.ell(hx + 5 * s * d, hy - 1 * s, 2.0 * s, 2.2 * s, G_OC)
    c.ell(hx + 10 * s * d, hy + 2 * s, 1.8 * s, 1.4 * s, (218, 128, 122))


def _uap_hangat(c, x, y, t, s=1.0, n=2):
    """Uap hangat tipis melingkar naik pelan dari makanan/kopi/teh (suasana hangat Ghibli!)."""
    for i in range(n):
        ox = (i - (n - 1) * 0.5) * 16 * s
        ph = t * 1.6 + i * 2.1 + x * 0.02
        c.curve([
            (x + ox, y),
            (x + ox + math.sin(ph) * 7 * s, y - 18 * s),
            (x + ox - math.sin(ph + 0.9) * 8 * s, y - 38 * s),
            (x + ox + math.sin(ph + 1.8) * 6 * s, y - 56 * s),
        ], (255, 252, 242, 108), 3.0 * s)


def _asap_cerobong(c, x, y, t, s=1.0):
    """Kepulan asap cerobong rumah pedesaan Ghibli tipis melayang santai terbawa angin."""
    for i in range(4):
        p = ((t * 0.24 + i * 0.25) % 1.0)
        sx = x + p * 82 * s + math.sin(t * 1.4 + i * 1.7) * 9 * s
        sy = y - p * 118 * s
        rr = (7 + p * 22) * s
        al = int(max(0, math.sin(p * math.pi) * 86))
        if al > 4:
            c.ell(sx, sy, rr, rr * 0.78, (246, 244, 236, al))


def _perahu_layar_jauh(c, t, y_sea=-172, speed=16.0):
    """Perahu layar putih mungil melaju tenang di garis cakrawala laut (pantai Ghibli!)."""
    bx = ((t * speed + 380) % 2400) - 1200
    by = y_sea + math.sin(t * 1.7) * 2.4
    c.ell(bx, by + 6, 28, 3.2, (255, 255, 255, 110))
    c.poly([(bx - 22, by), (bx + 22, by), (bx + 15, by + 8), (bx - 15, by + 8)], (146, 98, 68), 1.2, G_OC)
    c.poly([(bx, by - 2), (bx, by - 36), (bx + 20, by - 4)], (252, 248, 236), 1.2, G_OC)
    c.poly([(bx - 2, by - 2), (bx - 2, by - 26), (bx - 14, by - 4)], (228, 238, 244), 1.0, G_OC)


def _daun_melayang(c, t, seed=0, count=2, col=(152, 198, 104), y_min=-460, y_max=40):
    """2-3 helai daun gugur lembut melayang pelan terbawa angin (bukan hujan partikel!)."""
    for i in range(count):
        p = ((t * 0.14 + i * 0.47 + seed * 0.19) % 1.0)
        lx = -760 + ((seed * 211 + i * 580 + t * 28) % 1520) + math.sin(t * 1.8 + i * 2.4) * 36
        ly = lerp(y_min, y_max, p)
        al = int(min(220, math.sin(p * math.pi) * 240))
        if al > 12:
            c.ell(lx, ly, 7.5, 4.0, col + (al,))


def _interior_warm_lighting(c, o, win_x=520, win_y=-520, win_w=320, win_h=300, lamp_pts=(), t=0.0):
    """Pencahayaan interior Ghibli sinematik: sunbeams diagonal + bercak sinar lantai + debu cahaya bergerak pelan (siang/pagi/sore) & warm lamp glow bernapas lembut (malam!)."""
    wk = waktu_of(o)
    if wk == "malam":
        # malam dalam ruangan: cahaya lampu kuning-madu hangat bernapas super halus!
        pulse = 1.0 + 0.04 * math.sin(t * 1.4)
        pts = lamp_pts if lamp_pts else [(0, -560, 520)]
        for lx, ly, lr in pts:
            glow(c, lx, ly, lr * pulse, (255, 218, 134), 82, n=10)
            glow(c, lx, ly + 220, lr * 0.85 * pulse, (255, 204, 118), 42, n=8)
    else:
        # berkas cahaya matahari diagonal lembut (cinematic Ghibli sunbeams!) & bercak cahaya jatuh di lantai!
        dir_x = -1 if win_x >= 0 else 1
        scol = (255, 244, 198) if wk != "sore" else (255, 186, 118)
        al = 34 if wk == "siang" else (44 if wk == "pagi" else 54)
        x0, x1 = win_x - win_w * 0.45, win_x + win_w * 0.45
        y0, y1 = win_y - win_h * 0.44, win_y + win_h * 0.44
        dx_f = dir_x * 480
        c.poly([(x0, y0), (x1, y0), (x1 + dx_f, 260), (x0 + dx_f, 260)], scol + (al,))
        c.poly([(x0 + win_w * 0.14, y0 + 20), (x1 - win_w * 0.14, y0 + 20),
                (x1 - win_w * 0.14 + dx_f * 0.85, 210), (x0 + win_w * 0.14 + dx_f * 0.85, 210)], scol + (int(al * 0.72),))
        # bercak cahaya jendela jatuh di lantai kayu
        fx0, fx1 = x0 + dx_f * 0.56, x1 + dx_f * 0.56
        c.poly([(fx0 + 40, 26), (fx1 + 40, 26), (fx1 - 55, 175), (fx0 - 55, 175)], scol + (int(al * 1.18),))
        # 5 butir debu cahaya keemasan mengambang SANGAT PELAN di dalam berkas sinar jendela!
        for di in range(5):
            dp = 0.22 + di * 0.15
            mx = lerp((x0 + x1) * 0.5, (x0 + x1) * 0.5 + dx_f * 0.72, dp) + ((di * 37) % 60 - 30) + math.sin(t * 0.65 + di * 1.7) * 14
            my = lerp(y0 + 30, 80, dp) + math.cos(t * 0.55 + di * 2.1) * 10
            tw = 0.65 + 0.35 * math.sin(t * 1.5 + di * 1.3)
            c.ell(mx, my, 4.2, 4.2, (255, 252, 224, int(95 * tw)))
            c.ell(mx, my, 9.0, 9.0, scol + (int(34 * tw),))


def _lampu_gantung_ghibli(c, x, y_top=-900, y_lamp=-620, col=(82, 92, 96), nyala=True, r_glow=280):
    """Lampu gantung retro Ghibli (kap melengkung enamel + bohlam hangat + pendaran lembut)."""
    c.line([(x, y_top), (x, y_lamp - 36)], G_OC, 3.0)
    c.ell(x, y_lamp - 36, 14, 10, gelap(col, 0.20), 2.0, G_OC)
    c.poly([(x - 52, y_lamp + 6), (x + 52, y_lamp + 6), (x + 26, y_lamp - 32), (x - 26, y_lamp - 32)], col, 2.4, G_OC)
    c.ell(x, y_lamp + 6, 52, 12, (255, 238, 174) if nyala else (196, 192, 182), 2.0, G_OC)
    if nyala:
        c.ell(x, y_lamp + 10, 14, 11, (255, 250, 224))
        glow(c, x, y_lamp + 26, r_glow, (255, 218, 134), 76, n=7)


def papan_nama(c, x, y, w, h, teks, col=(250, 232, 174), size=64):
    c.rect(x - w / 2 + 4, y - h / 2 + 6, x + w / 2 + 4, y + h / 2 + 6, (58, 66, 84, 52), 0, r=10)
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, col, 2.8, G_OC, r=10)
    c.text(x, y + 2, teks, size, (68, 54, 48), "judul")


def _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t):
    """Kanopi lukisan gouache Ghibli: TANPA outline hitam kaku, ratusan sapuan daun organik bertingkat 5 nada (unik per posisi x bertanda!)."""
    # pakai x bertanda agar pohon di -x dan +x TIDAK pernah identik kembar!
    seed_k = int(round(x * 13 + cy * 7)) + len(lobes) * 97 + (1009 if x < 0 else 0)
    rng = random.Random(seed_k)
    flip_l = -1.0 if (seed_k % 2 == 1) else 1.0
    # 5 nada warna khas Ghibli: deep blue-teal shadow -> forest shadow -> midtone -> warm sunlit -> yellow-lime rim
    deep_c = mix(gelap(wc, 0.48), (22, 62, 82), 0.42)
    sh_c = mix(gelap(wc, 0.24), (34, 86, 78), 0.26)
    mid_c = wc
    sun_c = terang(mix(wc, (232, 240, 118), 0.34), 0.10)
    rim_c = terang(mix(wc, (254, 248, 162), 0.50), 0.22)
    # sedikit jitter organik unik per pohon agar bentuk siluet tidak pernah copy-paste
    vlobes = [(dx_ * flip_l + rng.uniform(-10, 10), dy_ + rng.uniform(-7, 7),
               rx_ * rng.uniform(0.90, 1.12), ry_ * rng.uniform(0.90, 1.12)) for dx_, dy_, rx_, ry_ in lobes]

    for dx_, dy_, rx_, ry_ in vlobes:
        cx_ = x + dx_ * s + sway
        cy_ = cy + dy_ * s
        c.ell(cx_, cy_, rx_ * s, ry_ * s, deep_c)
        n_dabs = 7 if far else 11
        for k in range(n_dabs):
            ang = (k / n_dabs) * math.tau + rng.uniform(-0.22, 0.22)
            rr = rng.uniform(0.76, 1.04)
            bx = cx_ + math.cos(ang) * rx_ * rr * s
            by = cy_ + math.sin(ang) * ry_ * rr * s
            dr = rng.uniform(14, 24) * s * (rx_ / 72.0)
            c.ell(bx, by, dr, dr * rng.uniform(0.68, 0.95), deep_c)

    for dx_, dy_, rx_, ry_ in vlobes:
        cx_ = x + (dx_ - 4) * s + sway
        cy_ = cy + (dy_ - 9) * s
        c.ell(cx_, cy_, rx_ * 0.90 * s, ry_ * 0.86 * s, sh_c)
        for k in range(5 if far else 8):
            ang = rng.uniform(0, math.tau)
            bx = cx_ + math.cos(ang) * rx_ * rng.uniform(0.35, 0.85) * s
            by = cy_ + math.sin(ang) * ry_ * rng.uniform(0.35, 0.80) * s
            dr = rng.uniform(13, 22) * s * (rx_ / 72.0)
            c.ell(bx, by, dr, dr * 0.78, sh_c)

    for dx_, dy_, rx_, ry_ in vlobes:
        if dy_ <= 24 or dx_ <= 45:
            cx_ = x + (dx_ - 9) * s + sway
            cy_ = cy + (dy_ - 17) * s
            c.ell(cx_, cy_, rx_ * 0.76 * s, ry_ * 0.70 * s, mid_c)
            for k in range(4 if far else 7):
                ang = rng.uniform(math.pi * 0.8, math.pi * 2.15)
                bx = cx_ + math.cos(ang) * rx_ * rng.uniform(0.25, 0.75) * s
                by = cy_ + math.sin(ang) * ry_ * rng.uniform(0.20, 0.70) * s
                dr = rng.uniform(11, 19) * s * (rx_ / 72.0)
                c.ell(bx, by, dr, dr * 0.76, mid_c)

    for dx_, dy_, rx_, ry_ in vlobes:
        if dy_ < 6 or dx_ < 10:
            cx_ = x + (dx_ - 14) * s + sway
            cy_ = cy + (dy_ - 24) * s
            for k in range(4 if far else 7):
                ang = rng.uniform(math.pi * 0.95, math.pi * 2.05)
                bx = cx_ + math.cos(ang) * rx_ * rng.uniform(0.10, 0.62) * s
                by = cy_ + math.sin(ang) * ry_ * rng.uniform(0.08, 0.52) * s
                dr = rng.uniform(9, 17) * s * (rx_ / 72.0)
                c.ell(bx, by, dr, dr * 0.72, sun_c)
            if dy_ < -14:
                for k in range(2 if far else 4):
                    bx = cx_ + rng.uniform(-rx_ * 0.42, rx_ * 0.22) * s
                    by = cy_ + rng.uniform(-ry_ * 0.42, -ry_ * 0.05) * s
                    dr = rng.uniform(7, 13) * s * (rx_ / 72.0)
                    c.ell(bx, by, dr, dr * 0.66, rim_c)


def pohon(c, x, s=1.0, warna=HIJAU, batang=COKLAT, tinggi=300, gaya=None, t=0.0):
    """7 spesies pohon organik bergaya Ghibli dengan siluet yang benar-benar berbeda satu sama lain."""
    if gaya is None:
        gaya = ("rimbun", "bulat_tinggi", "cemara", "sakura", "palem", "gugur", "beringin")[abs(int(round(x / 137))) % 7]
    if gaya == "sakura":
        warna = (244, 168, 196)
    elif gaya == "gugur":
        warna = (232, 134, 62)
    elif gaya == "beringin":
        warna = (74, 150, 92)
    elif gaya == "cemara" and warna == HIJAU:
        warna = (58, 136, 98)
    elif gaya == "rimbun" and warna == HIJAU:
        warna = (92, 174, 96)
    elif gaya == "bulat_tinggi" and warna == HIJAU:
        warna = (104, 184, 102)

    far = getattr(c, "depth", 1.0) < 0.85
    fog = (182, 212, 232)
    wc = mix(warna, fog, 0.34) if far else warna
    bc = mix(batang, fog, 0.30) if far else batang
    oc = mix(OUT, fog, 0.55) if far else OUT
    ow_t = (OW * 0.42 if far else OW * 0.75) * s
    h = tinggi * s
    sway = math.sin(t * 1.5 + x * 0.013) * 5.0 * s

    # bayangan jatuh organik 2 lapis di tanah
    c.ell(x + 24 * s, 8 * s, 126 * s, 24 * s, (24, 52, 42, 22 if far else 38))
    c.ell(x + 12 * s, 5 * s, 72 * s, 13 * s, (20, 44, 36, 18 if far else 30))

    if gaya == "cemara":
        # PINUS GHIBLI: cabang organik bergelombang & klaster jarum asimetris (bukan segitiga kaku!)
        c.poly([(x - 20 * s, 0), (x + 20 * s, 0), (x + 9 * s, -h * 0.65), (x - 9 * s, -h * 0.65)], bc, ow_t, oc)
        c.poly([(x + 2 * s, 0), (x + 18 * s, 0), (x + 8 * s, -h * 0.65), (x + 1 * s, -h * 0.65)], gelap(bc, 0.24))
        cy = -h * 0.52
        lobes = [
            # tingkat bawah lebar menjuntai asimetris
            (-96, 62, 54, 34), (-38, 66, 62, 36), (34, 68, 60, 34), (92, 60, 50, 32),
            # tingkat 2
            (-76, 8, 52, 34), (-16, 12, 58, 36), (48, 14, 54, 34), (78, 4, 42, 30),
            # tingkat 3
            (-52, -46, 46, 34), (8, -42, 50, 34), (50, -48, 40, 30),
            # tingkat 4 meruncing ke puncak
            (-24, -96, 36, 32), (20, -94, 34, 30), (0, -140, 28, 34), (-4, -172, 16, 24),
        ]
        _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)
        return

    if gaya == "palem":
        # POHON KELAPA GHIBLI BERVARIASI (pakai x bertanda agar kiri & kanan SELALU beda bentuk!)
        var = (int(round(x / 53)) + (2 if x < 0 else 0)) % 4
        # tinggi & kelengkungan batang jelas bervariasi antar-pohon (miring kanan, miring kiri, tinggi tegak, & kembar tropis!)
        h_mul = (1.92, 1.62, 2.08, 1.78)[var]
        bend_dir = (1, -1, 1, -1)[var]
        bend_amt = (135, 110, 48, 125)[var] * bend_dir * s

        def _draw_one_palm(px0, sc_p, hh_p, bnd_p, seed_p):
            sw = sway * (0.9 + 0.15 * (seed_p % 2))
            tx = px0 + bnd_p + sw
            ty = -hh_p
            # bayangan jatuh miring biru-slate di pasir/tanah
            c.ell(px0 + bnd_p * 0.4 + 34 * sc_p, 10 * sc_p, 118 * sc_p, 20 * sc_p, (46, 68, 76, 48 if far else 66))
            # batang melengkung alami bergradasi cahaya-bayangan (pangkal lebar -> ramping ke puncak)
            mx_b = px0 + bnd_p * 0.38
            my_b = -hh_p * 0.52
            pts_l = bezier((px0 - 24 * sc_p, 0), (mx_b - 15 * sc_p, my_b), (tx - 9 * sc_p, ty), 10)
            pts_r = list(reversed(bezier((px0 + 24 * sc_p, 0), (mx_b + 15 * sc_p, my_b), (tx + 9 * sc_p, ty), 10)))
            c.poly(pts_l + pts_r, bc, ow_t * 0.72, oc)
            # sisi bayangan kanan batang + highlight hangat sisi kiri
            pts_m = bezier((px0 + 2 * sc_p, 0), (mx_b + 2 * sc_p, my_b), (tx + 1 * sc_p, ty), 10)
            c.poly(pts_m + pts_r, gelap(bc, 0.24))
            c.curve(bezier((px0 - 15 * sc_p, -6 * sc_p), (mx_b - 9 * sc_p, my_b), (tx - 5 * sc_p, ty + 14 * sc_p), 8),
                    terang(bc, 0.22), 3.6 * sc_p)
            # cincin ruas batang kelapa melengkung
            n_ring = 13
            for k in range(1, n_ring):
                p_ = k / n_ring
                u_ = 1.0 - p_
                rx = u_ * u_ * px0 + 2 * u_ * p_ * mx_b + p_ * p_ * tx
                ry = u_ * u_ * 0 + 2 * u_ * p_ * my_b + p_ * p_ * ty
                rw = lerp(21, 9, p_) * sc_p
                c.curve([(rx - rw, ry - 2 * sc_p), (rx, ry + 3 * sc_p), (rx + rw, ry - 3 * sc_p)], gelap(bc, 0.34), 2.2 * sc_p)

            # 3 nada warna daun kelapa gouache Ghibli (bayangan dalam teal-hijau -> tropis -> puncak sunlit kuning-limau!)
            deep_f = mix(gelap(wc, 0.42), (24, 72, 74), 0.45)
            mid_f = mix(wc, (84, 158, 76), 0.50)
            sun_f = mix(terang(wc, 0.24), (176, 208, 96), 0.55)
            rim_f = (212, 228, 128)

            def _draw_frond(dx_end, dy_end, dx_mid, dy_mid, col_main, col_hi, n_leaf=9, droop=1.0):
                ex = tx + dx_end * sc_p + sw * 0.42
                ey = ty + dy_end * sc_p
                mx = tx + dx_mid * sc_p + sw * 0.20
                my = ty + dy_mid * sc_p
                spine = bezier((tx, ty), (mx, my), (ex, ey), n_leaf)
                # gambar helai anak daun menyirip (coconut leaflets) menjuntai penuh di sepanjang tulang pelepah!
                for idx_l in range(1, len(spine)):
                    lx0, ly0 = spine[idx_l]
                    frac = idx_l / len(spine)
                    env = math.sin(frac * math.pi * 0.92)
                    ll = (38 + 34 * env) * sc_p * droop
                    side_dir = -1 if dx_end < 0 else (1 if dx_end > 0 else (1 if idx_l % 2 else -1))
                    # anak daun bawah menjuntai tajam alami
                    ang_x = side_dir * (10 + 18 * frac) * sc_p
                    c.poly(_blade_poly(lx0, ly0, lx0 + ang_x * 0.55, ly0 + ll * 0.48,
                                       lx0 + ang_x, ly0 + ll, (9.5 + 5 * env) * sc_p), col_main)
                    # anak daun sisi atas/sunlit (mengisi ketebalan pelepah agar rimbun!)
                    if idx_l % 2 == 1 and frac < 0.85:
                        c.poly(_blade_poly(lx0, ly0, lx0 + ang_x * 0.45, ly0 - ll * 0.26,
                                           lx0 + ang_x * 0.9, ly0 + ll * 0.35, (7.5 + 4 * env) * sc_p), col_hi)
                # tulang pelepah melengkung lentur
                c.curve([(tx, ty), (mx, my), (ex, ey)], gelap(col_main, 0.26), 4.0 * sc_p)
                c.curve([(tx, ty - 1.5 * sc_p), (mx, my - 1.5 * sc_p), (ex, ey)], col_hi, 1.8 * sc_p)

            # PASS 1: 4 pelepah belakang teduh (memberi kedalaman volume di belakang mahkota!)
            for dx_e, dy_e, dx_m, dy_m in (
                (-195, 78, -110, -28), (195, 76, 112, -26), (-145, -72, -78, -96), (145, -74, 78, -98),
            ):
                _draw_frond(dx_e, dy_e, dx_m, dy_m, deep_f, mid_f, n_leaf=9, droop=1.08)

            # PASS 2: Tandan 5 buah kelapa bervolume 3D tepat di pangkal tajuk!
            for cx_, cy_, cr_ in ((-16, 14, 13), (15, 15, 13), (-3, 22, 14), (-22, 26, 11), (12, 27, 11)):
                c.ell(tx + cx_ * sc_p, ty + cy_ * sc_p, cr_ * sc_p, (cr_ + 1.5) * sc_p, (118, 82, 46), ow_t * 0.55, oc)
                c.ell(tx + (cx_ - 3) * sc_p, ty + (cy_ - 3) * sc_p, cr_ * 0.42 * sc_p, cr_ * 0.36 * sc_p, (168, 128, 78))

            # PASS 3: 7 pelepah utama + PELEPAH TENGAH PENUH (menutup celah tengah yang dulu kosong!)
            for dx_e, dy_e, dx_m, dy_m, c1, c2, drp in (
                (-218, 36, -124, -56, mid_f, sun_f, 1.05),
                (218, 34, 124, -58, mid_f, sun_f, 1.05),
                (-168, -32, -92, -98, mid_f, sun_f, 0.96),
                (168, -30, 92, -98, mid_f, sun_f, 0.96),
                (-74, -108, -42, -118, sun_f, rim_f, 0.85),   # pelepah tengah-kiri menjulang ke atas!
                (76, -106, 44, -116, sun_f, rim_f, 0.85),     # pelepah tengah-kanan menjulang ke atas!
                (6 if bend_dir > 0 else -6, -124, 12 * bend_dir, -82, sun_f, rim_f, 0.78),  # pucuk tengah penuh!
                (-54, 88, -32, 18, mid_f, sun_f, 0.82),       # pelepah depan jatuh lembut menghadap kamera!
                (58, 92, 34, 20, mid_f, sun_f, 0.82),
            ):
                _draw_frond(dx_e, dy_e, dx_m, dy_m, c1, c2, n_leaf=9, droop=drp)

        _draw_one_palm(x, s, h * h_mul, bend_amt, var)
        # variasi ke-3: tambahkan 1 pohon kelapa kembar lebih rendah miring berlawanan agar alami seperti pantai tropis!
        if var == 3 and not far:
            _draw_one_palm(x + 48 * s * (-bend_dir), s * 0.76, h * 1.24, -bend_amt * 0.82, var + 7)
        return

    if gaya == "sakura":
        # WEEPING SAKURA: batang miring melengkung anggun + cabang menjuntai berderai bunga pink
        lean = 32 * s
        trunk_h = h * 0.90
        pts_l = bezier((x - 26 * s, 0), (x - 10 * s, -trunk_h * 0.5), (x + lean - 12 * s, -trunk_h), 7)
        pts_r = list(reversed(bezier((x + 26 * s, 0), (x + 18 * s, -trunk_h * 0.5), (x + lean + 12 * s, -trunk_h), 7)))
        c.poly(pts_l + pts_r, gelap(bc, 0.14), ow_t, oc)
        c.line([(x + lean * 0.5, -trunk_h * 0.62), (x - 86 * s, -trunk_h * 1.05)], gelap(bc, 0.14), 14 * s)
        c.line([(x + lean * 0.7, -trunk_h * 0.76), (x + 92 * s, -trunk_h * 1.02)], gelap(bc, 0.14), 12 * s)
        cy = -trunk_h - 32 * s
        # siluet sakura melengkung lebar & menjuntai (bukan bulat simetris!)
        lobes = [
            (-128, 34, 48, 56), (-92, -6, 68, 52), (-36, -42, 78, 56),
            (32, -48, 82, 58), (96, -12, 72, 54), (132, 32, 46, 58),
            (-64, 38, 44, 48), (68, 36, 46, 50), (0, -8, 76, 46),
        ]
        _ghibli_canopy(c, x + lean * 0.35, cy, lobes, wc, s, sway, far, oc, ow_t)
        # kelopak sakura lembut melayang
        for ki in range(5):
            px_ = x + (-110 + ki * 56) * s + math.sin(t * 2.1 + ki * 1.7) * 20 * s
            py_ = cy + (78 + ((t * 34 + ki * 38) % 145)) * s
            c.ell(px_, py_, 6 * s, 3.8 * s, (255, 228, 240))
        return

    if gaya == "gugur":
        # MAPLE / GUGUR BERTINGKAT: 3 gugusan kanopi terpisah bertumpu di dahan bercabang lebar (gaya bonsai/maple)
        trunk_h = h * 0.96
        c.poly([(x - 24 * s, 0), (x + 24 * s, 0), (x + 11 * s, -trunk_h * 0.72), (x - 11 * s, -trunk_h * 0.72)], bc, ow_t, oc)
        c.poly([(x + 2 * s, 0), (x + 22 * s, 0), (x + 10 * s, -trunk_h * 0.72), (x + 1 * s, -trunk_h * 0.72)], gelap(bc, 0.22))
        # 3 cabang utama menyebar jelas
        c.line([(x - 4 * s, -trunk_h * 0.56), (x - 92 * s, -trunk_h * 0.88)], bc, 14 * s)
        c.line([(x + 4 * s, -trunk_h * 0.62), (x + 98 * s, -trunk_h * 0.96)], bc, 13 * s)
        c.line([(x, -trunk_h * 0.68), (x - 8 * s, -trunk_h * 1.24)], bc, 12 * s)
        # 3 klaster awan daun terpisah (kiri bawah, kanan tengah, puncak atas) -> siluet benar-benar unik!
        _ghibli_canopy(c, x - 94 * s, -trunk_h * 0.92, [(-38, 8, 46, 30), (4, -10, 56, 36), (42, 6, 44, 28)], wc, s, sway * 0.7, far, oc, ow_t)
        _ghibli_canopy(c, x + 98 * s, -trunk_h * 1.02, [(-40, 10, 48, 32), (8, -12, 60, 38), (48, 8, 46, 30)], terang(wc, 0.08), s, sway * 0.85, far, oc, ow_t)
        _ghibli_canopy(c, x - 6 * s, -trunk_h * 1.32, [(-56, 12, 54, 34), (0, -14, 72, 44), (58, 10, 52, 34)], terang(wc, 0.14), s, sway, far, oc, ow_t)
        for ki in range(4):
            px_ = x + (-95 + ki * 64) * s + math.sin(t * 1.9 + ki * 2.2) * 22 * s
            py_ = -trunk_h * 0.7 + ((t * 38 + ki * 42) % 165) * s
            c.ell(px_, py_, 6.5 * s, 4 * s, (255, 206, 86))
        return

    if gaya == "bulat_tinggi":
        # POPLAR / CYPRESS TAMAN: tinggi menjulang ramping berombak seperti obor (bukan bulat melebar!)
        trunk_h = h * 0.82
        c.poly([(x - 18 * s, 0), (x + 18 * s, 0), (x + 10 * s, -trunk_h), (x - 10 * s, -trunk_h)], bc, ow_t, oc)
        c.poly([(x + 2 * s, 0), (x + 16 * s, 0), (x + 9 * s, -trunk_h), (x + 1 * s, -trunk_h)], gelap(bc, 0.22))
        cy = -trunk_h - 110 * s
        lobes = [
            (-40, 92, 46, 48), (42, 94, 44, 46), (0, 82, 56, 52),
            (-44, 34, 52, 56), (46, 38, 48, 52), (0, 18, 60, 62),
            (-32, -32, 46, 56), (34, -26, 44, 52), (0, -56, 52, 64),
            (-12, -108, 36, 48), (12, -102, 32, 44), (0, -138, 26, 36),
        ]
        _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)
        return

    if gaya == "beringin":
        # BERINGIN RAKSASA: payung sangat lebar + batang tebal berakar + akar gantung rimbun
        trunk_h = h * 0.82
        trunk_pts = [(x - 42 * s, 0), (x + 42 * s, 0), (x + 24 * s, -trunk_h * 0.34),
                     (x + 20 * s, -trunk_h), (x - 20 * s, -trunk_h), (x - 24 * s, -trunk_h * 0.34)]
        c.poly(trunk_pts, bc, ow_t, oc)
        c.poly([(x + 4 * s, 0), (x + 40 * s, 0), (x + 22 * s, -trunk_h * 0.34),
                (x + 19 * s, -trunk_h), (x + 3 * s, -trunk_h)], gelap(bc, 0.24))
        for rx_ in (-124, -92, -62, 66, 98, 128):
            c.curve([(x + rx_ * s + sway * 0.5, -trunk_h - 8 * s),
                     (x + (rx_ + 6) * s, -trunk_h * 0.48),
                     (x + (rx_ - 4) * s, -6 * s)], gelap(bc, 0.18), 4.0 * s)
        cy = -trunk_h - 36 * s
        lobes = [
            (-156, 22, 68, 44), (-98, -14, 82, 56), (-32, -46, 94, 62),
            (40, -42, 92, 60), (108, -10, 82, 54), (158, 24, 66, 42),
            (-64, 24, 76, 42), (68, 24, 76, 42), (0, 14, 86, 44),
        ]
        _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)
        return

    # RIMBUN (OAK GHIBLI): kanopi organik asimetris condong lembut + klaster daun penuh
    trunk_h = h * 0.94
    trunk_pts = [(x - 28 * s, 0), (x + 28 * s, 0), (x + 17 * s, -trunk_h * 0.3),
                 (x + 14 * s, -trunk_h), (x - 14 * s, -trunk_h), (x - 17 * s, -trunk_h * 0.3)]
    c.poly(trunk_pts, bc, ow_t, oc)
    c.poly([(x + 3 * s, 0), (x + 26 * s, 0), (x + 15 * s, -trunk_h * 0.3),
            (x + 13 * s, -trunk_h), (x + 2 * s, -trunk_h)], gelap(bc, 0.22))
    c.line([(x - 4 * s, -trunk_h * 0.68), (x - 66 * s, -trunk_h * 1.02)], bc, 15 * s)
    c.line([(x + 4 * s, -trunk_h * 0.74), (x + 54 * s, -trunk_h * 1.06)], bc, 13 * s)
    cy = -trunk_h - 52 * s
    lobes = [
        (-112, 26, 68, 52), (-68, -28, 78, 66), (-14, -66, 86, 68),
        (54, -44, 76, 62), (104, 10, 68, 54), (62, 34, 62, 46),
        (-36, 26, 70, 48), (18, -6, 74, 54),
    ]
    _ghibli_canopy(c, x, cy, lobes, wc, s, sway, far, oc, ow_t)


def semak(c, x, w=220, h=110, warna=HIJAU_TUA, y=0):
    """Semak belukar painterly Ghibli: 5 nada sapuan daun organik tanpa outline kaku + bayangan jatuh + bunga kecil."""
    far = getattr(c, "depth", 1.0) < 0.85
    wc = mix(warna, (182, 212, 232), 0.30) if far else warna
    # bayangan jatuh lembut di tanah
    c.ell(x + w * 0.06, y + 6, w * 0.56, h * 0.16, (22, 54, 42, 34 if far else 54))
    # klaster asimetris organik (bukan 4 bola polos bergaris hitam!)
    lobes = [
        (-w * 0.34, -h * 0.24, w * 0.22, h * 0.32),
        (-w * 0.14, -h * 0.44, w * 0.28, h * 0.44),
        (w * 0.12, -h * 0.40, w * 0.26, h * 0.40),
        (w * 0.34, -h * 0.22, w * 0.22, h * 0.30),
        (0.0, -h * 0.20, w * 0.32, h * 0.28),
    ]
    _ghibli_canopy(c, x, y, lobes, wc, 1.0, 0.0, far, OUT, 0.0)
    # 3-4 bintik bunga mungil di permukaan semak agar hidup & detail
    if not far:
        rng = random.Random(int(abs(x * 17 + w)))
        bcols = ((255, 250, 230), (255, 214, 102), (255, 188, 208))
        for k in range(4):
            bx = x + rng.uniform(-w * 0.34, w * 0.34)
            by = y - rng.uniform(h * 0.22, h * 0.62)
            c.ell(bx, by, 5.2, 4.4, bcols[k % len(bcols)])
            c.ell(bx, by, 2.0, 2.0, (255, 206, 68))


def bunga_detail(c, x, y, s=1.0, warna=PINK, jenis="daisy", t=0.0):
    """Bunga 2D detail dengan tangkai melengkung, daun pangkal, dan kelopak berlapis (daisy / tulip / liar)."""
    sway = math.sin(t * 2.1 + x * 0.03) * 3.5 * s
    stem_h = 46.0 * s
    tx, ty = x + sway, y - stem_h
    mx, my = x + sway * 0.45 + (4.0 if int(abs(x)) % 2 == 0 else -4.0) * s, y - stem_h * 0.52
    leaf_c = (74, 154, 78)
    leaf_sh = (48, 114, 62)
    oc = mix(OUT, leaf_sh, 0.45)

    # bayangan kecil di pangkal tangkai
    c.ell(x + 2 * s, y + 2 * s, 14 * s, 4 * s, (24, 58, 42, 42))
    # 2 daun pangkal melengkung kiri & kanan
    for sg in (-1, 1):
        lx0, ly0 = x, y - 4 * s
        lx1, ly1 = x + sg * 20 * s, y - 20 * s
        lmx, lmy = x + sg * 11 * s, y - 18 * s
        lpts = bezier((lx0, ly0), (lmx, lmy - 5 * s), (lx1, ly1), 5) + list(reversed(bezier((lx0, ly0), (lmx, lmy + 5 * s), (lx1, ly1), 5)))
        c.poly(lpts, leaf_sh if sg > 0 else leaf_c, 1.8 * s, oc)
    # tangkai melengkung halus
    c.curve([(x, y), (mx, my), (tx, ty)], leaf_sh, 3.2 * s)

    if jenis == "tulip":
        # kelopak tulip 3 lapis (belakang gelap -> kiri/kanan -> depan terang)
        c.ell(tx, ty - 6 * s, 10 * s, 14 * s, gelap(warna, 0.20), 1.6 * s, oc)
        c.poly([(tx - 12 * s, ty - 14 * s), (tx - 13 * s, ty + 2 * s), (tx - 2 * s, ty + 6 * s), (tx - 2 * s, ty - 8 * s)],
               warna, 1.6 * s, oc)
        c.poly([(tx + 12 * s, ty - 14 * s), (tx + 13 * s, ty + 2 * s), (tx + 2 * s, ty + 6 * s), (tx + 2 * s, ty - 8 * s)],
               gelap(warna, 0.08), 1.6 * s, oc)
        c.ell(tx, ty - 3 * s, 7.5 * s, 11 * s, terang(warna, 0.16), 1.4 * s, oc)
    else:
        # daisy / cosmos 6 kelopak memancar + putik emas hangat
        n_pet = 6
        for k in range(n_pet):
            ang = math.radians(k * (360.0 / n_pet) + 18)
            px = tx + math.cos(ang) * 10.5 * s
            py = ty + math.sin(ang) * 9.0 * s
            pcol = gelap(warna, 0.08) if math.sin(ang) > 0.2 else warna
            c.ell(px, py, 7.2 * s, 5.6 * s, pcol, 1.5 * s, oc)
            c.ell(px - 1.2 * s, py - 1.2 * s, 3.6 * s, 2.8 * s, terang(warna, 0.24))
        # putik tengah kuning hangat + titik kilau
        c.ell(tx, ty, 5.6 * s, 5.0 * s, (246, 192, 54), 1.4 * s, oc)
        c.ell(tx - 1.4 * s, ty - 1.4 * s, 2.2 * s, 1.8 * s, (255, 242, 168))


def _blade_poly(x0, y0, xm, ym, x1, y1, w_base):
    """Satu helai daun rumput meruncing tajam organik (poligon 2 sisi, bukan garis kaku!)."""
    e1 = bezier((x0 - w_base * 0.5, y0), (xm - w_base * 0.28, ym), (x1, y1), 4)
    e2 = list(reversed(bezier((x0 + w_base * 0.5, y0), (xm + w_base * 0.28, ym), (x1, y1), 4)))
    return e1 + e2


def _rumpun_ghibli(c, gx, gy, sc, sh_c, deep_c, sun_c, sway):
    """Satu rumpun rumput Ghibli bervolume penuh (gundukan teduh + helai daun meruncing padat 3-nada!)."""
    # bantal bayangan lembut di pangkal rumpun
    c.ell(gx + 3 * sc, gy + 2 * sc, 24 * sc, 7.5 * sc, deep_c + (155,) if len(deep_c) == 3 else deep_c)
    # 7 helai daun belakang (hijau-teal teduh) meruncing melengkung
    for ax, hh, wb in ((-22, 26, 6.2), (-14, 34, 6.8), (-6, 40, 7.2), (2, 42, 7.2), (10, 36, 6.8), (18, 28, 6.2), (25, 22, 5.4)):
        c.poly(_blade_poly(
            gx + ax * 0.28 * sc, gy + 2 * sc,
            gx + ax * 0.72 * sc, gy - hh * 0.54 * sc,
            gx + (ax * 1.15 + sway) * sc, gy - hh * sc,
            wb * sc,
        ), deep_c)
    # 5 helai daun tengah (hijau zaitun sedang)
    for ax, hh, wb in ((-15, 24, 5.4), (-7, 32, 5.8), (1, 34, 5.8), (9, 29, 5.4), (16, 22, 4.8)):
        c.poly(_blade_poly(
            gx + ax * 0.24 * sc, gy + 3 * sc,
            gx + ax * 0.65 * sc, gy - hh * 0.52 * sc,
            gx + (ax * 1.05 + sway * 1.05) * sc, gy - hh * sc,
            wb * sc,
        ), sh_c)
    # 4 pucuk helai tersinari matahari (kuning-limau hangat persis referensi rumput Ghibli!)
    for ax, hh, wb in ((-11, 22, 4.4), (-3, 28, 4.8), (5, 25, 4.5), (12, 19, 4.0)):
        c.poly(_blade_poly(
            gx + ax * 0.20 * sc, gy + 3 * sc,
            gx + ax * 0.58 * sc, gy - hh * 0.50 * sc,
            gx + (ax * 0.96 + sway * 1.15) * sc, gy - hh * sc,
            wb * sc,
        ), sun_c)


def _vol_mound(c, x, y, rx, ry, deep_c, sh_c, mid_c, sun_c, rim_c, rng):
    """Satu gundukan semak-rumput bervolume 4-nada gouache persis lereng referensi Ghibli user!"""
    # bayangan jatuh dingin ke lereng bawah
    c.ell(x + rx * 0.14, y + ry * 0.36, rx * 1.06, ry * 0.52, deep_c)
    # massa bawah gelap hijau-teal
    c.ell(x, y, rx, ry, sh_c)
    for _ in range(5):
        ox = rng.uniform(-rx * 0.65, rx * 0.65)
        oy = rng.uniform(-ry * 0.35, ry * 0.28)
        c.ell(x + ox, y + oy, rx * rng.uniform(0.32, 0.52), ry * rng.uniform(0.36, 0.56), sh_c)
    # lapisan tengah hijau zaitun hangat
    c.ell(x - rx * 0.08, y - ry * 0.16, rx * 0.86, ry * 0.78, mid_c)
    for _ in range(5):
        ox = rng.uniform(-rx * 0.58, rx * 0.45)
        oy = rng.uniform(-ry * 0.55, ry * 0.05)
        c.ell(x + ox, y + oy, rx * rng.uniform(0.28, 0.46), ry * rng.uniform(0.32, 0.48), mid_c)
    # puncak tersinari matahari kuning-limau (dappled sunlight!)
    for _ in range(6):
        ox = rng.uniform(-rx * 0.55, rx * 0.38)
        oy = rng.uniform(-ry * 0.68, -ry * 0.12)
        c.ell(x + ox, y + oy, rx * rng.uniform(0.20, 0.38), ry * rng.uniform(0.22, 0.38), sun_c)
    for _ in range(3):
        ox = rng.uniform(-rx * 0.44, rx * 0.20)
        oy = rng.uniform(-ry * 0.72, -ry * 0.28)
        c.ell(x + ox, y + oy, rx * rng.uniform(0.12, 0.24), ry * rng.uniform(0.14, 0.24), rim_c)


def rumput(c, y1=1400, warna=HIJAU_MUDA, t=0.0):
    """Hamparan rumput & semak bervolume 5-nada gouache Studio Ghibli (persis referensi rumput user!)."""
    # 5 nada organik Kazuo Oga / Ghibli (bukan hijau neon polos!):
    deep_c = (44, 86, 68)                                       # hijau-teal bayangan dalam
    sh_c = mix(gelap(warna, 0.28), (62, 114, 76), 0.55)         # hijau hutan teduh
    mid_c = mix(warna, (118, 166, 86), 0.58)                    # hijau zaitun lembut
    sun_c = mix(terang(warna, 0.22), (176, 208, 102), 0.62)     # puncak tersinari kuning-limau
    rim_c = (214, 228, 134)                                     # kilau rumput kena matahari

    c.rect(X0, 0, X1, y1, mid_c)
    # 1) Gelombang bukit rumput berlapis + bayangan kontras matahari (dappled sunlit & shadow slopes!)
    c.blob([(-2800, 12), (-1950, -14), (-980, 16), (-40, -10), (960, 18), (1920, -12), (2800, 12),
            (2800, 210), (-2800, 210)], sun_c, 0, n=6)
    c.blob([(-2800, 68), (-1750, 34), (-760, 82), (220, 40), (1180, 88), (2120, 44), (2800, 74),
            (2800, 340), (-2800, 340)], mid_c, 0, n=6)
    # pita bayangan miring sejuk hijau-teal menyilang lereng (persis kontras cahaya-bayangan di referensi!)
    c.blob([(-2800, 148), (-1650, 104), (-580, 166), (480, 118), (1560, 174), (2800, 124),
            (2800, y1), (-2800, y1)], sh_c, 0, n=6)
    c.blob([(-2800, 265), (-1450, 220), (-320, 275), (820, 228), (1960, 280), (2800, 240),
            (2800, y1), (-2800, y1)], deep_c, 0, n=6)

    # 2) Gundukan semak-rumput bervolume di sepanjang tepi atas horizon (NOL garis lurus hitam kaku!)
    rng = random.Random(77)
    for i in range(-14, 15):
        mx = i * 195 + rng.uniform(-32, 32)
        my = rng.uniform(-6, 12)
        rx = rng.uniform(86, 138)
        ry = rng.uniform(22, 38)
        _vol_mound(c, mx, my, rx, ry, deep_c, sh_c, mid_c, sun_c, rim_c, rng)

    # 3) Gundukan rumput bervolume tengah-bawah + bercak cahaya matahari hangat
    for i in range(-12, 13):
        mx = i * 225 + rng.uniform(-45, 45)
        my = 65 + (abs(i * 53) % 135)
        rx = rng.uniform(95, 165)
        ry = rng.uniform(22, 36)
        _vol_mound(c, mx, my, rx, ry, deep_c, sh_c, mid_c, sun_c, rim_c, rng)

    # 4) Hamparan helai rumput meruncing padat berlapis 3 kedalaman (jauh -> tengah -> foreground rimbun!)
    sway = math.sin(t * 2.0) * 4.2
    for i in range(-26, 27):
        gx = i * 88 + (i * 37 % 42)
        gy = 14 + (abs(i * 47) % 44)
        _rumpun_ghibli(c, gx, gy, 0.56 + (abs(i) % 3) * 0.08, mid_c, sh_c, sun_c, sway * 0.65)
    for i in range(-22, 23):
        gx = i * 108 + (i * 59 % 52)
        gy = 74 + (abs(i * 71) % 98)
        _rumpun_ghibli(c, gx, gy, 0.84 + (abs(i) % 3) * 0.12, mid_c, deep_c, sun_c, sway)
    for i in range(-18, 19):
        gx = i * 134 + (i * 83 % 62)
        gy = 178 + (abs(i * 43) % 150)
        _rumpun_ghibli(c, gx, gy, 1.18 + (abs(i) % 3) * 0.16, sh_c, deep_c, rim_c, sway * 1.25)

    # 5) Bunga liar cat air lembut (kuning mentega & putih krem tanpa outline kaku persis referensi!)
    fl_cols = ((252, 244, 192), (248, 224, 128), (255, 250, 232), (246, 212, 138))
    for i in range(-16, 17):
        fx = i * 145 + (i * 59 % 58)
        fy = 36 + (abs(i * 97) % 190)
        sc = 0.52 + (fy / 260.0) * 0.42
        fc = fl_cols[abs(i) % len(fl_cols)]
        # kelopak cat air lembut + titik bayangan pangkal
        c.ell(fx + 2 * sc, fy + 2 * sc, 11 * sc, 5.5 * sc, deep_c + (110,))
        c.ell(fx, fy, 10 * sc, 5.2 * sc, fc)
        c.ell(fx - 2 * sc, fy - 1.5 * sc, 5.5 * sc, 3.0 * sc, (255, 254, 244))
        c.ell(fx + 1 * sc, fy, 2.8 * sc, 2.0 * sc, (232, 176, 62))


def jendela(c, x, y, w, h, o, tirai=False, scene_key=None, t=0.0):
    """Jendela kayu Ghibli hidup & bergerak halus: awan & daun luar melayang pelan, burung jauh, & tirai melambai lembut ditiup angin!"""
    wk = waktu_of(o)
    top, bot = LANGIT.get(wk, LANGIT["siang"])
    mid = LANGIT_MID.get(wk, LANGIT_MID["siang"])
    wood = (158, 112, 74) if wk != "malam" else (112, 82, 58)
    wood_d = gelap(wood, 0.26)
    view_v = (abs(int(x)) // 73 + (abs(hash(scene_key)) if scene_key else 0)) % 4

    # 1) Bayangan bingkai & kedalaman recess kusen kayu
    c.rect(x - w / 2 + 8, y - h / 2 + 10, x + w / 2 + 10, y + h / 2 + 14, (58, 52, 64, 42), 0, r=8)
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, wood, 2.6, G_OC, r=7)
    x0, x1, y0, y1 = x - w / 2 + 15, x + w / 2 - 15, y - h / 2 + 15, y + h / 2 - 15
    # celah bayangan dalam kusen atas & kiri (memberi kedalaman 3D, bukan foto tempelan datar!)
    c.rect(x0 - 4, y0 - 4, x1 + 4, y1 + 4, wood_d, 1.4, G_OC, r=3)

    # 2) Pemandangan luar jendela yang HIDUP & BERGERAK HALUS mengikuti t!
    c.rect(x0, y0, x1, y1, bot)
    c.rect(x0, y0, x1, lerp(y0, y1, 0.62), mid)
    c.rect(x0, y0, x1, lerp(y0, y1, 0.28), top)
    if wk == "malam":
        mx = lerp(x0 + w * 0.24, x1 - w * 0.24, (view_v % 2) * 0.8 + 0.1)
        my = y0 + h * (0.24 + 0.06 * (view_v % 2))
        c.ell(mx, my, w * 0.14, w * 0.14, (226, 240, 255, 32))
        c.ell(mx, my, w * 0.072, w * 0.072, (255, 248, 212))
        c.ell(mx + w * 0.028, my - w * 0.016, w * 0.060, w * 0.060, mix(top, mid, 0.45))
        for i in range(9):
            sx = x0 + 18 + ((i * 53 + view_v * 31) % max(40, int(w - 50)))
            sy = y0 + 14 + ((i * 37 + view_v * 19) % max(40, int(h * 0.56)))
            tw = 0.65 + 0.35 * math.sin(t * 2.2 + i * 1.9)
            c.ell(sx, sy, (1.8 + (i % 2) * 0.7) * tw, (1.8 + (i % 2) * 0.7) * tw, (255, 252, 224))
        c.poly([(x0, y1), (x0 + w * 0.30, y1 - h * 0.28), (x0 + w * 0.68, y1 - h * 0.18), (x1, y1 - h * 0.26), (x1, y1)], (26, 40, 74))
        rx_h = x0 + w * (0.20 if view_v % 2 == 0 else 0.54)
        c.poly([(rx_h - 14, y1 - h * 0.18), (rx_h + w * 0.16, y1 - h * 0.34), (rx_h + w * 0.34, y1 - h * 0.18)], (36, 48, 82))
        c.rect(rx_h, y1 - h * 0.18, rx_h + w * 0.28, y1, (30, 42, 72))
        c.rect(rx_h + 14, y1 - h * 0.13, rx_h + 36, y1 - h * 0.05, (255, 224, 134))
        c.rect(rx_h + 44, y1 - h * 0.13, rx_h + 62, y1 - h * 0.05, (255, 214, 120))
    else:
        # awan kecil beragam yang melayang PELAN di luar kaca jendela!
        c_cols = _cloud_colors(wk)
        cdrift = math.sin(t * 0.22 + view_v) * (w * 0.09)
        if view_v == 0:
            _paint_cloud_puffs(c, x - w * 0.10 + cdrift, y - h * 0.10, w / 720.0, [(-56, 10, 52, 24), (10, -8, 60, 34), (72, 12, 48, 22)], c_cols)
        elif view_v == 1:
            _paint_cirrus_streak(c, x + w * 0.02 + cdrift * 0.8, y - h * 0.20, w / 680.0, -22, 210, c_cols, seed=view_v)
            _paint_cloud_puffs(c, x + w * 0.12 - cdrift * 0.6, y + h * 0.04, w / 760.0, [(-46, 8, 44, 20), (16, -4, 52, 26)], c_cols)
        elif view_v == 2:
            _paint_cloud_puffs(c, x + w * 0.08 + cdrift, y - h * 0.14, w / 720.0, [(-44, 12, 48, 24), (8, -14, 58, 38), (56, 10, 42, 22)], c_cols)
        else:
            _paint_cirrus_streak(c, x - w * 0.04 + cdrift, y - h * 0.18, w / 680.0, 20, 210, c_cols, seed=view_v + 3)
        # 1 burung mungil melintas tenang di kejauhan luar jendela!
        bp = ((t * 0.16 + view_v * 0.31) % 1.0)
        bx_w = lerp(x0 + 24, x1 - 24, bp)
        by_w = y0 + h * 0.26 + math.sin(t * 2.0 + view_v) * 6.0
        fl_w = math.sin(t * 7.5 + view_v) * 3.5
        c.curve([(bx_w - 7, by_w - fl_w), (bx_w, by_w + 1), (bx_w + 7, by_w - fl_w)], (246, 250, 255) if wk == "siang" else (112, 118, 134), 1.6)
        # lapisan bukit jauh berkabut biru + bukit dekat hijau lembut
        hill1 = (122, 178, 210) if wk != "sore" else (182, 132, 144)
        hill2 = (94, 158, 112) if wk != "sore" else (138, 114, 98)
        c.poly([(x0, y1), (x0 + w * 0.24, y1 - h * 0.30), (x0 + w * 0.56, y1 - h * 0.20), (x0 + w * 0.82, y1 - h * 0.32), (x1, y1 - h * 0.24), (x1, y1)], hill1)
        c.poly([(x0, y1), (x0 + w * 0.18, y1 - h * 0.18), (x0 + w * 0.52, y1 - h * 0.25), (x1, y1 - h * 0.14), (x1, y1)], hill2)
        if view_v in (0, 2):
            rx_h = x0 + w * (0.52 if view_v == 0 else 0.12)
            roof_c = (196, 104, 84) if wk != "sore" else (178, 92, 78)
            c.poly([(rx_h - 10, y1 - h * 0.14), (rx_h + w * 0.14, y1 - h * 0.28), (rx_h + w * 0.30, y1 - h * 0.14)], roof_c, 1.4, G_OC)
            c.rect(rx_h, y1 - h * 0.14, rx_h + w * 0.24, y1, (244, 234, 214), 1.2, G_OC)
            c.rect(rx_h + 14, y1 - h * 0.10, rx_h + 34, y1 - h * 0.03, (124, 168, 194))
        # rimbunan daun pohon mengintip dari pinggir kaca yang BERGOYANG PELAN tertiup angin!
        l_sway = math.sin(t * 1.6 + view_v) * 4.0
        tx_l = x0 + 18 if view_v % 2 == 0 else x1 - 24
        leaf_base = (238, 166, 190) if view_v == 1 else ((86, 152, 88) if wk != "sore" else (112, 128, 76))
        for ox, oy, rr in ((0, 0, 34), (24 if view_v % 2 == 0 else -24, 14, 28), (12 if view_v % 2 == 0 else -12, -22, 26)):
            cx_l, cy_l = clamp(tx_l + ox + l_sway, x0 + 16, x1 - 16), clamp(y1 - h * 0.18 + oy, y0 + 28, y1 - 16)
            c.ell(cx_l, cy_l, rr, rr * 0.82, gelap(leaf_base, 0.22))
            c.ell(cx_l - 4, cy_l - 4, rr * 0.78, rr * 0.64, leaf_base)
            c.ell(cx_l - 7, cy_l - 7, rr * 0.45, rr * 0.36, terang(leaf_base, 0.24))

    # 3) Pantulan kaca halus + kisi kayu bingkai daun jendela + ambang kayu dengan pot mini!
    c.poly([(x0 + 18, y1 - 6), (x0 + 50, y1 - 6), (x1 - 24, y0 + 6), (x1 - 54, y0 + 6)], (255, 255, 255, 32))
    c.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], None, 2.2, G_OC)
    c.rect((x0 + x1) / 2 - 5, y0, (x0 + x1) / 2 + 5, y1, wood, 1.6, G_OC)
    c.rect(x0, (y0 + y1) / 2 - 5, x1, (y0 + y1) / 2 + 5, wood, 1.6, G_OC)
    c.ell((x0 + x1) / 2, (y0 + y1) / 2 + 12, 4.5, 4.5, (226, 192, 104), 1.4, G_OC)
    c.rect(x0 - 18, y1 + 4, x1 + 18, y1 + 22, terang(wood, 0.12), 2.2, G_OC, r=5)
    c.rect(x0 - 16, y1 + 17, x1 + 16, y1 + 24, wood_d)
    px_w = x0 + w * 0.22
    c.poly([(px_w - 14, y1 - 22), (px_w + 14, y1 - 22), (px_w + 10, y1 + 4), (px_w - 10, y1 + 4)], (196, 114, 72), 1.6, G_OC)
    c.ell(px_w, y1 - 28, 16, 13, (96, 158, 86), 1.4, G_OC)
    c.ell(px_w - 5, y1 - 32, 9, 8, (156, 198, 102))

    # 4) Rel tirai kayu + tirai kain linen berlipat yang MELAMBAI HALUS tertiup angin jendela!
    if tirai:
        tc = (242, 232, 212) if not isinstance(tirai, tuple) else tirai
        tsh = gelap(tc, 0.16)
        thl = terang(tc, 0.10)
        rod_y = y0 - 24
        c.rect(x - w * 0.60, rod_y - 4, x + w * 0.60, rod_y + 4, (132, 92, 64), 1.8, G_OC, r=3)
        c.ell(x - w * 0.61, rod_y, 8, 8, (164, 118, 78), 1.8, G_OC)
        c.ell(x + w * 0.61, rod_y, 8, 8, (164, 118, 78), 1.8, G_OC)
        tie_y = lerp(y0, y1, 0.64)
        for sg in (-1, 1):
            ex_out = x + sg * (w * 0.56)
            ex_in = x + sg * (w * 0.34)
            # goyangan lembut ujung bawah tirai (4-6 px saja, sangat alami!)
            sw_c = math.sin(t * 1.15 + sg * 0.8 + x * 0.01) * 5.5
            drape_pts = [
                (ex_in, rod_y + 4), (ex_out, rod_y + 4),
                (ex_out + sg * 6 + sw_c * 0.25, lerp(rod_y, tie_y, 0.55)),
                (ex_out - sg * 4, tie_y),
                (ex_out + sg * 12 + sw_c, y1 + 52),
                (lerp(ex_in, ex_out, 0.45) + sw_c, y1 + 58),
                (ex_in + sg * 8 + sw_c * 0.9, y1 + 48),
                (ex_out - sg * 24, tie_y),
                (ex_in - sg * 4 + sw_c * 0.2, lerp(rod_y, tie_y, 0.45)),
            ]
            c.poly(drape_pts, tc, 2.0, G_OC)
            c.curve([(lerp(ex_in, ex_out, 0.35), rod_y + 8), (ex_out - sg * 16, tie_y), (lerp(ex_in, ex_out, 0.28) + sw_c, y1 + 46)], tsh, 2.2)
            c.curve([(lerp(ex_in, ex_out, 0.68), rod_y + 8), (ex_out - sg * 8, tie_y), (lerp(ex_in, ex_out, 0.72) + sw_c, y1 + 50)], tsh, 2.0)
            c.curve([(lerp(ex_in, ex_out, 0.52), rod_y + 10), (ex_out - sg * 12, tie_y), (lerp(ex_in, ex_out, 0.50) + sw_c, y1 + 48)], thl, 2.4)
            c.rect(min(ex_out - sg * 26, ex_out - sg * 2), tie_y - 5, max(ex_out - sg * 26, ex_out - sg * 2), tie_y + 5,
                   (188, 128, 92), 1.6, G_OC, r=3)
            for k_r in range(3):
                rx_r = lerp(ex_in + sg * 6, ex_out - sg * 6, k_r / 2.0)
                c.ell(rx_r, rod_y, 4.5, 6.5, (196, 162, 96), 1.4, G_OC)


def tanaman(c, x, y=0, s=1.0, pot=(198, 118, 76)):
    """Pot terakota hangat + rimbunan daun organik Ghibli (menggantikan daun vektor outline hitam lama!)."""
    _pot_tanaman_ghibli(c, x, y, s=s * 1.12, sunlit=True)


def rak_buku(c, x, y, w=300, h=520, rows=4, seed=0):
    """Rak buku kayu Ghibli penuh karakter dengan shading dalam & buku berpalet earth-tone hangat."""
    wood = (158, 108, 72)
    wood_d = (112, 74, 52)
    c.rect(x - w / 2 + 10, y - h + 10, x + w / 2 + 10, y, (46, 50, 66, 48), 0, r=6)
    c.rect(x - w / 2, y - h, x + w / 2, y, wood, 2.6, G_OC, r=6)
    c.rect(x - w / 2 + 14, y - h + 14, x + w / 2 - 14, y - 14, (132, 92, 66), 0)
    cols = [(186, 86, 72), (96, 128, 152), (218, 178, 86), (112, 148, 104),
            (158, 112, 134), (206, 136, 78), (232, 222, 198), (82, 134, 132)]
    rh = (h - 28) / rows
    for r in range(rows):
        by = y - 14 - r * rh
        c.rect(x - w / 2 + 14, by - rh + 4, x + w / 2 - 14, by - rh + 22, (74, 52, 42, 72))
        c.rect(x - w / 2 + 12, by - 4, x + w / 2 - 12, by + 6, wood_d, 1.8, G_OC)
        xx = x - w / 2 + 22
        i = 0
        while xx < x + w / 2 - 38:
            bw = 22 + ((i + r + seed) * 7 % 3) * 6
            bh = rh * (.58 + ((i * 5 + r + seed) % 4) * .09)
            col = cols[(i * 3 + r * 5 + seed) % len(cols)]
            c.rect(xx, by - bh, xx + bw, by - 4, col, 1.8, G_OC, r=2)
            c.line([(xx + 4, by - bh + 10), (xx + bw - 4, by - bh + 10)], terang(col, 0.35), 2.0)
            xx += bw + 4
            i += 1


def lukisan(c, x, y, w=150, h=110, col=(144, 196, 226), tema=None):
    """Bingkai foto / lukisan dinding Ghibli BERISI NYATA (5 tema berbeda: potret chibi, pesisir perahu, pondok sakura, vas bunga, senja danau)."""
    if tema is None:
        tema = abs(int(round(x / 89))) % 5
    # bayangan bingkai + bingkai kayu + matboard putih-krem estetik
    c.rect(x - w / 2 + 5, y - h / 2 + 6, x + w / 2 + 5, y + h / 2 + 6, (56, 52, 64, 42), 0, r=4)
    c.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, (154, 108, 70), 2.4, G_OC, r=4)
    c.rect(x - w / 2 + 9, y - h / 2 + 9, x + w / 2 - 9, y + h / 2 - 9, (248, 243, 232), 1.2, G_OC)
    x0, x1, y0, y1 = x - w / 2 + 15, x + w / 2 - 15, y - h / 2 + 15, y + h / 2 - 15
    iw, ih = x1 - x0, y1 - y0

    if tema == 0:
        # TEMA 0: Foto Potret 2 Sahabat Chibi di Taman (benar-benar terasa seperti foto keluarga/sahabat!)
        c.rect(x0, y0, x1, y1, (168, 214, 236))
        c.rect(x0, y1 - ih * 0.34, x1, y1, (132, 186, 114))
        c.ell(x0 + iw * 0.20, y0 + ih * 0.24, iw * 0.14, ih * 0.10, (254, 252, 244))
        # 2 tokoh chibi mini tersenyum di tengah foto
        for px_f, hc_f, sc_f in ((x - iw * 0.16, (38, 30, 32), (82, 134, 146)), (x + iw * 0.17, (112, 78, 58), (224, 142, 92))):
            by_f = y1 - ih * 0.08
            c.poly([(px_f - iw * 0.11, by_f), (px_f - iw * 0.09, by_f - ih * 0.26),
                    (px_f + iw * 0.09, by_f - ih * 0.26), (px_f + iw * 0.11, by_f)], sc_f, 1.2, G_OC)
            hy_f = by_f - ih * 0.44
            hr_f = min(iw, ih) * 0.21
            c.ell(px_f, hy_f - hr_f * 0.18, hr_f * 1.18, hr_f * 1.12, hc_f)
            c.ell(px_f, hy_f, hr_f, hr_f * 0.94, (252, 224, 202), 1.2, G_OC)
            c.ell(px_f - hr_f * 0.34, hy_f, 2.2, 2.6, G_OC)
            c.ell(px_f + hr_f * 0.34, hy_f, 2.2, 2.6, G_OC)
            c.curve([(px_f - hr_f * 0.24, hy_f + hr_f * 0.34), (px_f, hy_f + hr_f * 0.48), (px_f + hr_f * 0.24, hy_f + hr_f * 0.34)], G_OC, 1.4)
    elif tema == 1:
        # TEMA 1: Lukisan Pesisir Laut & Perahu Layar Putih
        c.rect(x0, y0, x1, y1, (104, 184, 232))
        c.rect(x0, y0 + ih * 0.56, x1, y1, (38, 148, 196))
        c.ell(x0 + iw * 0.28, y0 + ih * 0.28, iw * 0.18, ih * 0.12, (254, 252, 244))
        c.ell(x0 + iw * 0.72, y0 + ih * 0.36, iw * 0.14, ih * 0.09, (254, 252, 244))
        c.poly([(x0, y0 + ih * 0.58), (x0 + iw * 0.26, y0 + ih * 0.38), (x0 + iw * 0.48, y0 + ih * 0.58)], (88, 152, 126))
        # perahu layar kecil
        bx_s, by_s = x + iw * 0.14, y0 + ih * 0.68
        c.poly([(bx_s - 18, by_s), (bx_s + 18, by_s), (bx_s + 12, by_s + 9), (bx_s - 12, by_s + 9)], (152, 98, 66), 1.2, G_OC)
        c.poly([(bx_s, by_s - 2), (bx_s, by_s - 28), (bx_s + 16, by_s - 4)], (254, 250, 240), 1.2, G_OC)
        c.poly([(bx_s - 2, by_s - 2), (bx_s - 2, by_s - 22), (bx_s - 13, by_s - 4)], (232, 240, 244), 1.0, G_OC)
    elif tema == 2:
        # TEMA 2: Lukisan Pondok Ghibli Atap Merah & Pohon Sakura
        c.rect(x0, y0, x1, y1, (132, 196, 234))
        c.rect(x0, y0 + ih * 0.62, x1, y1, (124, 178, 102))
        c.poly([(x0 + iw * 0.36, y1), (x0 + iw * 0.46, y0 + ih * 0.62), (x0 + iw * 0.56, y0 + ih * 0.62), (x0 + iw * 0.68, y1)], (232, 212, 172))
        # pondok kecil tengah
        c.rect(x - iw * 0.16, y0 + ih * 0.44, x + iw * 0.16, y0 + ih * 0.68, (248, 238, 218), 1.2, G_OC)
        c.poly([(x - iw * 0.22, y0 + ih * 0.46), (x, y0 + ih * 0.26), (x + iw * 0.22, y0 + ih * 0.46)], (206, 98, 78), 1.2, G_OC)
        c.rect(x - 5, y0 + ih * 0.54, x + 5, y0 + ih * 0.68, (138, 94, 62))
        # pohon sakura pink di kiri
        c.line([(x0 + iw * 0.18, y0 + ih * 0.72), (x0 + iw * 0.20, y0 + ih * 0.44)], (118, 82, 58), 3.0)
        c.ell(x0 + iw * 0.18, y0 + ih * 0.38, iw * 0.14, ih * 0.15, (242, 168, 194))
        c.ell(x0 + iw * 0.14, y0 + ih * 0.34, iw * 0.08, ih * 0.09, (254, 214, 226))
    elif tema == 3:
        # TEMA 3: Still Life Vas Bunga Matahari Hangat (ala Ghibli/Van Gogh!)
        c.rect(x0, y0, x1, y1, (242, 226, 192))
        c.rect(x0, y1 - ih * 0.26, x1, y1, (194, 146, 98))
        # vas keramik biru-teal
        c.ell(x, y1 - ih * 0.28, iw * 0.15, ih * 0.18, (94, 146, 152), 1.4, G_OC)
        c.rect(x - iw * 0.08, y1 - ih * 0.46, x + iw * 0.08, y1 - ih * 0.36, (108, 162, 168), 1.2, G_OC)
        # 3 bunga matahari & daun hijau
        for fx_s, fy_s, r_s in ((-0.12, -0.58, 11), (0.04, -0.68, 13), (0.16, -0.54, 10)):
            c.line([(x, y1 - ih * 0.44), (x + iw * fx_s, y1 + ih * fy_s)], (74, 134, 72), 2.2)
            c.ell(x + iw * fx_s, y1 + ih * fy_s, r_s, r_s, (246, 198, 66), 1.2, G_OC)
            c.ell(x + iw * fx_s, y1 + ih * fy_s, r_s * 0.46, r_s * 0.46, (112, 72, 42))
    else:
        # TEMA 4: Lukisan Senja Gunung & Pantulan Danau Emas
        c.rect(x0, y0, x1, y1, (238, 152, 118))
        c.rect(x0, y0, x1, y0 + ih * 0.44, (132, 104, 154))
        c.ell(x, y0 + ih * 0.50, iw * 0.14, iw * 0.14, (255, 224, 142))
        c.poly([(x0, y0 + ih * 0.66), (x0 + iw * 0.28, y0 + ih * 0.38), (x0 + iw * 0.56, y0 + ih * 0.58),
                (x0 + iw * 0.82, y0 + ih * 0.36), (x1, y0 + ih * 0.66)], (94, 82, 118))
        c.rect(x0, y0 + ih * 0.66, x1, y1, (196, 128, 124))
        c.ell(x, y0 + ih * 0.80, iw * 0.16, ih * 0.05, (255, 224, 146, 180))
    c.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], None, 1.4, G_OC)


def karpet(c, x, w=620, col=(214, 166, 134), y=60):
    """Karpet tenun oval hangat Ghibli (cincin anyaman berongga pakai curve, bukan oval solid!)."""
    c.ell(x + 4, y + 6, w / 2, 40, (54, 48, 56, 38))
    c.ell(x, y, w / 2, 40, col, 2.4, G_OC)
    c.curve(arc_pts(x, y, w / 2 - 36, 29, 0, 360, 36), terang(col, 0.28), 3.0)
    c.curve(arc_pts(x, y, w / 2 - 78, 19, 0, 360, 32), gelap(col, 0.16), 2.2)
    c.curve(arc_pts(x, y, w / 2 - 120, 11, 0, 360, 28), terang(col, 0.22), 1.8)


def glow(c, x, y, r, col=(255, 214, 120), a=70, n=12):
    """Pendaran cahaya halus multi-lapis tanpa cincin patah (soft radial lamp glow)."""
    n_eff = max(10, n)
    for i in range(n_eff):
        k = 1.0 - i / n_eff
        rad = r * (0.18 + 0.82 * k)
        al = max(3, int((a / n_eff) * 1.45 * (1.0 - 0.55 * k)))
        c.ell(x, y, rad, rad * 0.90, col + (al,))


# ================================================================= KAMAR (GHIBLI COZY BEDROOM)
def kamar_b(c, t, o):
    wk = waktu_of(o)
    # dinding plester krem-madu hangat + panel kayu wainscoting (TETAP HANGAT saat malam oleh lampu tidur!)
    wall_c = (248, 236, 214) if wk != "malam" else (164, 144, 128)
    wain_c = (218, 184, 146) if wk != "malam" else (132, 104, 86)
    dinding(c, wall_c)
    c.rect(X0, -240, X1, 0, wain_c)
    for px in range(-1200, 1201, 110):
        c.line([(px, -240), (px, 0)], gelap(wain_c, 0.14), 1.6)
    c.rect(X0, -248, X1, -236, gelap(wain_c, 0.18), 1.8, G_OC)
    lantai(c, (198, 152, 108) if wk != "malam" else (136, 104, 80), garis=(166, 122, 82))
    # balok kayu plafon atas khas rumah Jepang Ghibli
    c.rect(X0, -760, X1, -724, (132, 92, 64), 2.2, G_OC)
    jendela(c, 520, -500, 330, 310, o, tirai=(238, 224, 198), scene_key="kamar", t=t)
    # tempat tidur kayu hangat + sprei linen sage-krem (bukan pink kartun neon!)
    wood_b = (152, 102, 68)
    c.ell(-280, 10, 360, 22, (58, 52, 66, 48))
    c.rect(-640, -420, -592, 0, wood_b, 2.4, G_OC, r=8)
    c.rect(-644, -456, -560, -404, gelap(wood_b, 0.12), 2.4, G_OC, r=14)
    c.rect(-600, -148, 40, -38, (214, 174, 134), 2.2, G_OC, r=10)
    c.rect(-594, -180, 36, -110, (248, 242, 228), 2.2, G_OC, r=24)
    c.rect(-596, -78, 36, 0, wood_b, 2.2, G_OC, r=8)
    c.rect(-560, -248, -418, -148, (242, 212, 184), 2.2, G_OC, r=26)
    # boneka kelinci hangat lembut
    bx, by = -290, -190
    for sg in (-1, 1):
        c.blob([(bx + sg * 12, by - 70), (bx + sg * 24, by - 126), (bx + sg * 38, by - 110), (bx + sg * 30, by - 66)], (250, 240, 226), 2.0, G_OC)
    c.ell(bx, by - 30, 48, 42, (250, 240, 226), 2.0, G_OC)
    c.ell(bx - 15, by - 34, 3.6, 4.4, G_OC); c.ell(bx + 15, by - 34, 3.6, 4.4, G_OC)
    c.ell(bx, by - 22, 3.8, 2.8, (212, 134, 128))
    # nakas kayu + lampu tidur Ghibli + jam digital
    c.rect(74, -172, 300, 0, wood_b, 2.4, G_OC, r=6)
    c.rect(84, -158, 290, -90, (206, 158, 112), 2.0, G_OC, r=4)
    c.ell(187, -124, 5.5, 5.5, (238, 216, 168), 1.6, G_OC)
    # lampu meja kecil di kanan nakas (menyala hangat saat malam!)
    c.rect(248, -228, 260, -172, (124, 88, 62), 2.0, G_OC)
    c.poly([(224, -226), (284, -226), (272, -276), (236, -276)], (246, 216, 152) if wk == "malam" else (238, 226, 202), 2.0, G_OC)
    benda_jam(c, 155, -210, o, t)
    # rak gantung kiri + pot tanaman Ghibli + buku
    c.rect(-970, -518, -740, -496, wood_b, 2.2, G_OC, r=4)
    tanaman(c, -905, -496, .52)
    for i, col in enumerate(((192, 96, 78), (96, 134, 156), (218, 178, 86))):
        c.rect(-836 + i * 23, -582 + (i % 2) * 8, -816 + i * 23, -498, col, 1.8, G_OC, r=2)
    lukisan(c, -250, -585, 195, 142)
    lukisan(c, 880, -585, 135, 104, (246, 204, 168))
    karpet(c, 160, 700, (214, 168, 138), 150)
    _lampu_gantung_ghibli(c, -60, -860, -645, (108, 134, 118), nyala=(wk == "malam"), r_glow=360)
    _interior_warm_lighting(c, o, 520, -500, 330, 310, lamp_pts=[(254, -250, 320), (-60, -610, 480)], t=t)
    tint(c, o, indoor=True)


def benda_jam(c, x, y, o, t):
    import benda
    benda.weker(c, benda._T(x, y, 1, 0), 1.0, t, jam=o.get("jam", "07:00"), on=bool(o.get("alarm")))


def kamar_f(c, t, o):
    """Selimut quilt/plaid bertekstur kain lembut Ghibli dengan kerah lipatan duvet krem & jahitan halus!"""
    if o.get("selimut", True):
        col = o.get("selimut_warna")
        if col is None:
            col = (206, 128, 108) if waktu_of(o) != "malam" else (178, 112, 98)
        sh_c = gelap(col, 0.22)
        plaid_c = gelap(col, 0.14)
        hl_c = terang(col, 0.24)
        cream_c = (248, 240, 224)
        # bayangan jatuh lembut selimut di sisi kasur
        c.blob([(-398, -182), (-296, -208), (-116, -190), (36, -158), (62, -32), (-398, -32)], (58, 48, 56, 52), 0, n=7)
        # badan utama selimut lembut menggelembung
        pts_s = [(-402, -196), (-296, -226), (-120, -208), (32, -172), (56, -40), (-402, -40)]
        c.blob(pts_s, col, 2.4, G_OC, n=7)
        # cel shading bawah & sisi kanan selimut (memberi volume empuk!)
        c.blob([(-400, -104), (-220, -118), (-40, -102), (48, -96), (54, -40), (-400, -40)], sh_c + (125,), 0, n=6)
        # pola tenun kotak-kotak (soft Ghibli plaid / gingham) mengikuti lekukan selimut!
        for vx in (-320, -245, -170, -95, -20):
            c.curve([(vx + 12, -206), (vx + 4, -128), (vx - 6, -44)], plaid_c + (115,), 7.5)
            c.curve([(vx + 12, -206), (vx + 4, -128), (vx - 6, -44)], hl_c + (75,), 2.0)
        for hy_p in (-168, -126, -84):
            c.curve([(-390, hy_p + 6), (-220, hy_p - 12), (-40, hy_p + 4), (44, hy_p + 18)], plaid_c + (110,), 6.5)
            c.curve([(-390, hy_p + 6), (-220, hy_p - 12), (-40, hy_p + 4), (44, hy_p + 18)], hl_c + (70,), 1.8)
        # garis lipatan kain alami + kilau cahaya jendela jatuh di punggung selimut
        c.curve([(-340, -152), (-204, -174), (-58, -148)], gelap(col, 0.28), 2.8)
        c.curve([(-310, -112), (-164, -128), (-24, -104)], gelap(col, 0.24), 2.2)
        c.curve([(-290, -186), (-186, -200), (-74, -182)], (255, 246, 224, 95), 5.0)
        # tepi lipatan kerah atas duvet warna krem-putih berjahit quilt (bikin langsung terasa empuk & rapi!)
        collar = [(-404, -198), (-340, -220), (-320, -178), (-336, -126), (-366, -40), (-404, -40)]
        c.blob(collar, cream_c, 2.2, G_OC, n=5)
        c.curve([(-364, -196), (-346, -134), (-376, -46)], (214, 198, 174), 2.2)
        # bingkai ulang outline hangat agar rapi sempurna
        c.blob(pts_s, None, 2.4, G_OC, n=7)
    tint(c, o, True, indoor=True)


# ================================================================= SEKOLAH LUAR (GHIBLI SCHOOL)
def sekolah_luar_b(c, t, o):
    wk = waktu_of(o)
    langit(c, o, t=t)
    awan_set(c, o, t=t, scene_key="sekolah_luar")
    bukit_berlapis(c, o, 0)
    c.set_depth(0.76)
    pohon(c, -960, 1.05, HIJAU, gaya="sakura", t=t)
    pohon(c, 1260, .96, HIJAU_TUA, gaya="rimbun", t=t)
    c.set_depth(1.0)
    rumput(c, warna=(144, 198, 108), t=t)
    # jalan masuk ubin krem + bayangan jatuh biru-slate dingin
    c.poly([(-155, 0), (155, 0), (350, 420), (-350, 420)], (228, 218, 194), 2.2, G_OC)
    for yy in (40, 100, 175, 265):
        p_ = yy / 420.0
        hw = lerp(155, 350, p_)
        c.line([(-hw, yy), (hw, yy)], (192, 182, 162), 1.8)
    # gedung sekolah kayu-plester klasik anime Jepang
    bx = 260
    wall_s = (248, 238, 216)
    roof_s = (196, 102, 82)
    c.ell(bx + 24, 10, 580, 24, G_SH + (56,))
    c.rect(bx - 560, -430, bx + 560, 0, wall_s, 2.6, G_OC)
    c.rect(bx + 300, -430, bx + 558, -2, gelap(wall_s, 0.10))
    # bayangan dalam atap (deep eaves)
    c.rect(bx - 560, -430, bx + 560, -398, G_SH + (65,))
    c.poly([(bx - 600, -430), (bx + 600, -430), (bx + 510, -528), (bx - 510, -528)], roof_s, 2.6, G_OC)
    for k in range(1, 5):
        gy = lerp(-430, -528, k / 5.0)
        c.line([(lerp(bx - 595, bx - 510, k / 5.0), gy), (lerp(bx + 595, bx + 510, k / 5.0), gy)], gelap(roof_s, 0.22), 1.8)
    c.rect(bx - 635, -448, bx + 635, -424, gelap(roof_s, 0.16), 2.2, G_OC, r=3)
    win_c = (255, 224, 140) if wk == "malam" else (142, 194, 226)
    for sx in (-1, 1):
        for i in range(2):
            wx = bx + sx * (250 + i * 150)
            c.rect(wx - 50, -338, wx + 50, -152, win_c, 2.2, G_OC, r=3)
            if wk != "malam":
                c.poly([(wx - 44, -158), (wx - 22, -158), (wx + 44, -332), (wx + 22, -332)], (255, 255, 255, 62))
            c.line([(wx, -338), (wx, -152)], G_OC, 2.2)
            c.line([(wx - 50, -245), (wx + 50, -245)], G_OC, 2.2)
            # kotak pot kayu bunga di bawah tiap jendela sekolah (detail pedesaan Ghibli!)
            c.rect(wx - 54, -152, wx + 54, -128, (158, 108, 70), 1.8, G_OC, r=3)
            for fx_p, fc_p in ((-32, (246, 212, 92)), (-10, (252, 246, 232)), (12, (238, 142, 152)), (32, (246, 212, 92))):
                c.ell(wx + fx_p, -156, 12, 8, (88, 154, 82))
                c.ell(wx + fx_p, -162, 6, 5, fc_p)
    # pintu kayu + jam sekolah bundar
    c.rect(bx - 126, -326, bx + 126, 0, (124, 152, 178), 2.4, G_OC)
    c.line([(bx, -326), (bx, 0)], G_OC, 2.4)
    for sx in (-1, 1):
        c.rect(bx + sx * 100 - 34 if sx < 0 else bx + 24, -288, bx + sx * 100 + 34 if sx > 0 else bx - 24, -172, win_c, 2.0, G_OC)
    c.rect(bx - 166, -354, bx + 166, -326, (236, 224, 198), 2.2, G_OC, r=4)
    papan_nama(c, bx, -418, 320, 86, o.get("papan", "SMP"), (250, 232, 174), 60)
    for i in range(4):
        c.rect(bx - 186 + i * 8, -i * 14, bx + 186 - i * 8, -i * 14 + 14, (226, 218, 198), 2.0, G_OC)
    # tiang bendera
    c.line([(-600, 0), (-600, -695)], (134, 142, 152), 7.5)
    c.ell(-600, -700, 8, 8, (238, 196, 94), 1.8, G_OC)
    c.poly([(-596, -695), (-442, -695 + 10 * math.sin(t * 3)), (-442, -638 + 10 * math.sin(t * 3 + 1)), (-596, -638)], (214, 72, 68), 2.0, G_OC)
    c.poly([(-596, -638), (-442, -638 + 10 * math.sin(t * 3 + 1)), (-442, -586 + 10 * math.sin(t * 3)), (-596, -586)], (248, 246, 238), 2.0, G_OC)
    semak(c, -210, 260, 110)
    semak(c, 770, 310, 120)
    # bunga liar lembut di tepi jalan halaman sekolah + 2 kupu-kupu santai (siang/pagi/sore)
    for fx, fy, fc in ((-360, 82, PUTIH), (-290, 118, KUNING), (360, 96, PINK), (430, 124, PUTIH)):
        bunga_detail(c, fx, fy, 0.80, fc, "daisy", t=t)
    if wk != "malam":
        _kupu_kupu_ghibli(c, -310, -45, t, (252, 236, 152), seed=1, s=0.90)
        _kupu_kupu_ghibli(c, 420, -65, t, (250, 246, 232), seed=4, s=0.82)
    tint(c, o)


def sekolah_luar_f(c, t, o):
    c.set_depth(1.25)
    semak(c, -900, 380, 190, HIJAU, y=120)
    semak(c, 1000, 380, 190, HIJAU, y=140)
    c.set_depth(1.0)
    tint(c, o, True)


def _pagar_kayu(c, x0, y0, x1, y1, n_posts=4, s=1.0):
    """Pagar kayu pedesaan Ghibli dengan tiang bertekstur, palang ganda, tali ikat & bayangan jatuh."""
    wood = (162, 118, 86)
    wood_sh = (108, 76, 62)
    wood_hl = (212, 168, 128)
    oc = (66, 48, 44)
    # bayangan jatuh lembut di tanah
    c.poly([(x0 - 12 * s, y0 + 18 * s), (x1 + 18 * s, y1 + 22 * s),
            (x1 + 36 * s, y1 + 36 * s), (x0 + 10 * s, y0 + 34 * s)], (44, 78, 56, 70))
    # palang horizontal atas & bawah
    for h_off in (-72, -36):
        c.line([(x0, y0 + h_off * s), (x1, y1 + h_off * s)], oc, 16 * s)
        c.line([(x0, y0 + h_off * s), (x1, y1 + h_off * s)], wood, 12 * s)
        c.line([(x0, y0 + (h_off - 3) * s), (x1, y1 + (h_off - 3) * s)], wood_hl, 3.5 * s)
    # tiang vertikal
    for k in range(n_posts):
        p = k / max(1, n_posts - 1)
        px, py = lerp(x0, x1, p), lerp(y0, y1, p)
        c.rect(px - 11 * s, py - 98 * s, px + 11 * s, py + 4 * s, wood, 2.2 * s, oc, r=3)
        c.rect(px + 2 * s, py - 96 * s, px + 10 * s, py + 2 * s, wood_sh)
        c.line([(px - 6 * s, py - 92 * s), (px - 6 * s, py - 4 * s)], wood_hl, 2.5 * s)


def _batu_taman(c, x, y, rx, ry):
    """Batu kali bergaya Ghibli (bayangan biru-abu bawah + highlight krem atas + rumput pangkal)."""
    base = (156, 164, 162)
    sh = (96, 110, 118)
    hl = (216, 218, 206)
    oc = (62, 72, 74)
    pts = [(x - rx, y + ry * 0.25), (x - rx * 0.78, y - ry * 0.62), (x - rx * 0.12, y - ry),
           (x + rx * 0.65, y - ry * 0.72), (x + rx, y + ry * 0.15), (x + rx * 0.55, y + ry * 0.42),
           (x - rx * 0.58, y + ry * 0.42)]
    c.ell(x + rx * 0.18, y + ry * 0.36, rx * 1.05, ry * 0.34, (36, 68, 52, 65))
    c.blob(pts, sh, 2.2, oc, n=5)
    c.blob([(x - rx * 0.85, y - ry * 0.05), (x - rx * 0.65, y - ry * 0.60), (x - rx * 0.08, y - ry * 0.94),
            (x + rx * 0.54, y - ry * 0.64), (x + rx * 0.45, y - ry * 0.02), (x - rx * 0.35, y + ry * 0.08)], base, 0, n=5)
    c.ell(x - rx * 0.24, y - ry * 0.55, rx * 0.36, ry * 0.22, hl)


def _jalan_setapak_ghibli(c, y_top=0, y_bot=460):
    """Jalan tanah berliku Ghibli tanpa outline hitam kaku, dengan cast shadow, batu pinggir & rumput melingkup."""
    sand = (232, 204, 158)
    sand_hl = (248, 232, 194)
    sand_sh = (182, 146, 114)
    # kurva S lembut jalan tanah melebar ke depan kamera
    left_pts, right_pts = [], []
    steps = 16
    for i in range(steps + 1):
        p = i / steps
        yy = lerp(y_top, y_bot, p)
        cx = math.sin(p * math.pi * 1.15) * 95.0 - 24.0 * p
        hw = lerp(68.0, 255.0, p ** 1.15)
        left_pts.append((cx - hw, yy))
        right_pts.append((cx + hw, yy))
    path_pts = left_pts + list(reversed(right_pts))
    c.poly(path_pts, sand)
    # sapuan terang di tengah jalan tanah
    mid_l = [(lerp(l[0], r[0], 0.22), l[1]) for l, r in zip(left_pts, right_pts)]
    mid_r = [(lerp(l[0], r[0], 0.76), l[1]) for l, r in zip(left_pts, right_pts)]
    c.poly(mid_l + list(reversed(mid_r)), sand_hl)
    # bayangan pohon/pagar menyilang diagonal di atas jalan tanah (cast shadows khas Ghibli!)
    for sy, sh_h in ((58, 34), (175, 48), (310, 60)):
        p = clamp((sy - y_top) / max(1, y_bot - y_top))
        cx = math.sin(p * math.pi * 1.15) * 95.0 - 24.0 * p
        hw = lerp(68.0, 255.0, p ** 1.15)
        c.ell(cx + 12, sy, hw * 0.92, sh_h * 0.55, (112, 104, 128, 62))
    # kerikil kecil & jejak tanah organik
    rng = random.Random(42)
    for _ in range(28):
        p = rng.uniform(0.05, 0.95)
        yy = lerp(y_top, y_bot, p)
        cx = math.sin(p * math.pi * 1.15) * 95.0 - 24.0 * p
        hw = lerp(68.0, 255.0, p ** 1.15)
        px = cx + rng.uniform(-hw * 0.85, hw * 0.85)
        c.ell(px, yy, rng.uniform(5, 16) * (0.6 + p), rng.uniform(2.5, 6) * (0.6 + p), sand_sh + (120,))
    # rumput-rumput melingkup menutupi tepi kiri & kanan jalan tanah (tidak ada garis potong lurus!)
    for i in range(0, steps + 1, 1):
        lx, ly = left_pts[i]
        rx, ry = right_pts[i]
        sc = 0.65 + (i / steps) * 0.75
        _rumpun_ghibli(c, lx - 6 * sc, ly + 4, sc, (64, 128, 68), (38, 86, 56), (176, 214, 102), 2.0)
        _rumpun_ghibli(c, rx + 6 * sc, ry + 4, sc, (64, 128, 68), (38, 86, 56), (176, 214, 102), 2.0)


# ================================================================= TAMAN
def taman_b(c, t, o):
    langit(c, o, t=t)
    awan_set(c, o, t=t, scene_key="taman")
    bukit_berlapis(c, o, 0)
    c.set_depth(0.72)
    for i, (x, g) in enumerate(((-1420, "cemara"), (-780, "rimbun"), (640, "cemara"), (1360, "gugur"))):
        pohon(c, x, .86 + (i % 2) * .12, HIJAU_TUA if i % 2 else HIJAU, gaya=g, t=t)
    c.set_depth(1.0)
    rumput(c, warna=(142, 200, 108), t=t)
    _jalan_setapak_ghibli(c, 0, 440)
    # rumah pedesaan Jepang (Minka Ghibli) di kanan-belakang
    rumah(c, 560, 320, 215, (250, 242, 224), (212, 102, 84), gaya="jepang", t=t)
    _asap_cerobong(c, 645, -245, t, s=0.85)
    if waktu_of(o) == "malam":
        # cahaya hangat menyala dari balik pintu shoji rumah di malam hari!
        c.rect(436, -130, 598, -36, (255, 222, 134, 155))
        glow(c, 515, -80, 175, (255, 212, 118), 72)
    pohon(c, -470, 1.14, HIJAU, gaya="rimbun", t=t)
    pohon(c, 880, 1.04, (118, 196, 100), gaya="sakura", t=t)
    _pagar_kayu(c, -740, 125, -245, 78, n_posts=4, s=0.95)
    _batu_taman(c, 280, 82, 46, 28)
    _batu_taman(c, 336, 96, 30, 19)
    bunga_set = [
        (-280, 102, 0.85, PUTIH, "daisy"), (-335, 122, 0.92, (164, 208, 252), "daisy"),
        (-410, 118, 0.88, KUNING, "tulip"), (-475, 138, 0.95, PINK, "daisy"),
        (260, 112, 0.86, KUNING, "daisy"), (318, 126, 0.92, PUTIH, "daisy"),
        (385, 110, 0.84, (168, 210, 252), "daisy"),
    ]
    for fx, fy, fs, fc, fj in bunga_set:
        bunga_detail(c, fx, fy, fs, fc, fj, t=t)
    semak(c, -860, 320, 115)
    semak(c, 420, 240, 95, HIJAU)
    if waktu_of(o) == "malam":
        # kunang-kunang hangat lembut di taman malam Ghibli!
        for k in range(10):
            kx = -680 + k * 145 + math.sin(t * 1.6 + k) * 28
            ky = -40 - (k * 47 % 220) + math.cos(t * 2.1 + k * 1.3) * 18
            glow(c, kx, ky, 22, (238, 255, 152), 78, n=3)
            c.ell(kx, ky, 3.2, 3.2, (255, 254, 214))
    else:
        _kupu_kupu_ghibli(c, -350, -35, t, (252, 232, 144), seed=2, s=0.92)
        _kupu_kupu_ghibli(c, 340, -55, t, (192, 228, 248), seed=5, s=0.84)
    tint(c, o)


def taman_f(c, t, o):
    c.set_depth(1.28)
    for gx, gy, sc in ((-960, 260, 1.55), (-820, 278, 1.45), (-680, 290, 1.30),
                       (940, 265, 1.55), (790, 282, 1.40), (660, 295, 1.25)):
        _rumpun_ghibli(c, gx, gy, sc, (64, 118, 72), (34, 72, 54), (182, 212, 102), math.sin(t * 2.0) * 5.0)
    for fx, fy, fc in ((-860, 252, PUTIH), (-770, 268, KUNING), (-710, 260, PINK),
                       (840, 258, (172, 214, 255)), (750, 272, PUTIH)):
        bunga_detail(c, fx, fy, 1.08, fc, "daisy", t=t)
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= KELAS (GHIBLI NOSTALGIC CLASSROOM)
def kelas_b(c, t, o):
    wk = waktu_of(o)
    wall_c = (248, 240, 220) if wk != "malam" else (162, 152, 138)
    wain_c = (212, 180, 142) if wk != "malam" else (130, 106, 86)
    dinding(c, wall_c)
    c.rect(X0, -245, X1, 0, wain_c)
    for px in range(-1200, 1201, 95):
        c.line([(px, -245), (px, 0)], gelap(wain_c, 0.14), 1.5)
    c.rect(X0, -252, X1, -240, gelap(wain_c, 0.18), 1.8, G_OC)
    lantai(c, (206, 166, 124) if wk != "malam" else (138, 112, 86), garis=(176, 138, 98))
    # papan tulis hijau klasik berbingkai kayu + bayangan jatuh + rak kapur
    c.rect(-512, -612, 232, -230, (64, 58, 66, 46), 0, r=8)
    c.rect(-520, -620, 224, -238, (164, 114, 74), 2.6, G_OC, r=8)
    c.rect(-500, -600, 204, -258, (54, 102, 84), 2.0, G_OC)
    # sedikit goresan debu kapur lembut di papan tulis
    c.ell(-160, -430, 260, 110, (255, 255, 246, 14))
    tx = o.get("papan_tulis", "")
    if tx:
        c.text(-148, -430, tx, 60, (244, 248, 238), "bulat")
    else:
        for i, (w, y) in enumerate(((300, -540), (420, -490), (240, -440), (380, -390))):
            c.curve([(-460, y), (-460 + w * .5, y - 8), (-460 + w, y + 4)], (242, 248, 238, 220), 4.4)
        c.curve([(-70, -340), (-20, -330), (40, -344)], (255, 228, 138), 4.4)
    c.rect(-480, -248, 184, -230, (132, 88, 56), 2.2, G_OC, r=3)
    c.rect(-100, -260, -34, -244, (242, 238, 224), 1.8, G_OC, r=2)
    # papan pengumuman kelas & rak loker kayu di sisi kiri
    c.rect(-1040, -585, -600, -340, (194, 148, 102), 2.4, G_OC, r=6)
    for nx, ny, nc in ((-950, -510, (246, 238, 204)), (-820, -500, (216, 234, 212)), (-690, -508, (248, 216, 198)),
                       (-910, -405, (216, 232, 246)), (-760, -400, (250, 234, 188))):
        c.rect(nx - 46, ny - 40, nx + 46, ny + 40, nc, 1.6, G_OC, r=2)
        c.line([(nx - 30, ny - 14), (nx + 28, ny - 14)], (146, 138, 128), 2.0)
        c.line([(nx - 30, ny + 6), (nx + 18, ny + 6)], (146, 138, 128), 2.0)
    # jendela kelas lebar khas sekolah Jepang + tirai krem tipis (melambai & awan luar bergerak halus!)
    jendela(c, 600, -475, 360, 320, o, tirai=(246, 240, 224), scene_key="kelas", t=t)
    jendela(c, 1060, -475, 320, 320, o, scene_key="kelas", t=t)
    # jam dinding klasik bingkai kayu
    c.ell(-760, -650, 52, 52, (250, 246, 234), 2.6, (148, 102, 68))
    ang = (t * 0.2) % (2 * math.pi)
    c.line([(-760, -650), (-760 + math.sin(ang) * 32, -650 - math.cos(ang) * 32)], G_OC, 3.2)
    c.line([(-760, -650), (-760 + 24, -650 + 5)], G_OC, 4.0)
    # meja guru kayu + pot tanaman Ghibli + tumpukan buku
    c.rect(290, -190, 690, -162, (166, 116, 74), 2.4, G_OC, r=4)
    c.rect(310, -162, 670, 0, (198, 148, 102), 2.4, G_OC)
    c.rect(520, -214, 630, -190, (186, 92, 76), 1.8, G_OC, r=2)
    c.rect(532, -236, 622, -214, (96, 136, 154), 1.8, G_OC, r=2)
    tanaman(c, 370, -190, .44)
    _lampu_gantung_ghibli(c, -160, -860, -685, (236, 228, 206), nyala=(wk == "malam"), r_glow=380)
    _lampu_gantung_ghibli(c, 340, -860, -685, (236, 228, 206), nyala=(wk == "malam"), r_glow=380)
    _interior_warm_lighting(c, o, 600, -475, 360, 320, lamp_pts=[(-160, -650, 440), (340, -650, 440)], t=t)
    tint(c, o, indoor=True)


def kelas_f(c, t, o):
    if o.get("meja_depan", True):
        c.set_depth(1.15)
        for x in (-860, 900):
            c.rect(x - 150, 150, x + 150, 188, (196, 146, 98), 2.4, G_OC, r=4)
            c.rect(x - 120, 188, x - 102, 330, (108, 114, 126), 2.2, G_OC)
            c.rect(x + 102, 188, x + 120, 330, (108, 114, 126), 2.2, G_OC)
        c.set_depth(1.0)
    tint(c, o, True, indoor=True)


# ================================================================= RUANG BELAJAR (GHIBLI STUDY)
def ruang_belajar_b(c, t, o):
    wk = waktu_of(o)
    dinding(c, (246, 232, 206) if wk != "malam" else (154, 136, 120))
    c.rect(X0, -230, X1, 0, (214, 180, 142) if wk != "malam" else (126, 100, 82))
    c.rect(X0, -238, X1, -226, (176, 138, 100), 1.8, G_OC)
    lantai(c, (196, 148, 104) if wk != "malam" else (130, 98, 74), garis=(164, 118, 78))
    rak_buku(c, -640, 0, 360, 740, 5)
    jendela(c, 700, -540, 300, 310, o, tirai=(238, 224, 196), scene_key="ruang_belajar", t=t)
    # papan gabus kayu hangat + sticky notes pastel Ghibli
    c.rect(-94, -734, 366, -474, (58, 52, 64, 44), 0, r=6)
    c.rect(-100, -740, 360, -480, (194, 142, 94), 2.6, G_OC, r=6)
    notes = ((-60, -700, (248, 234, 168)), (50, -690, (244, 204, 192)), (160, -706, (198, 224, 236)),
             (270, -690, (208, 228, 192)), (-20, -580, (244, 204, 192)), (150, -590, (248, 234, 168)), (270, -560, (198, 224, 236)))
    for x, y, col in notes:
        c.rect(x - 36, y - 34, x + 36, y + 34, col, 1.8, G_OC, r=2)
        c.line([(x - 20, y - 10), (x + 20, y - 10)], (134, 126, 118), 2.2, False)
        c.line([(x - 20, y + 8), (x + 10, y + 8)], (134, 126, 118), 2.2, False)
    kx = o.get("kursi_x", 230)
    c.rect(kx - 78, -338, kx + 78, -120, (108, 126, 146), 2.4, G_OC, r=18)
    c.line([(kx, -120), (kx, 0)], G_OC, 10)
    lx = o.get("lampu_x", 560)
    c.line([(lx, -132), (lx - 10, -250), (lx + 70, -340)], (82, 86, 102), 9)
    c.poly([(lx + 40, -350), (lx + 130, -330), (lx + 100, -288), (lx + 24, -308)], (82, 114, 102), 2.4, G_OC)
    _interior_warm_lighting(c, o, 700, -540, 300, 310, lamp_pts=[(lx + 80, -290, 420), (-120, -540, 420)], t=t)
    if wk == "malam" or o.get("lampu_nyala", True):
        glow(c, lx + 80, -290, 320 * (1.0 + 0.04 * math.sin(t * 1.4)), (255, 222, 138), 95)
    tint(c, o, indoor=True)


def ruang_belajar_f(c, t, o):
    c.rect(-60, -134, 760, -102, (198, 148, 100), 2.4, G_OC, r=6)
    c.rect(-40, -102, 740, 0, (176, 128, 86), 2.4, G_OC)
    c.rect(150, -102, 430, -30, (160, 114, 76), 2.2, G_OC)
    c.ell(290, -66, 6.5, 6.5, (238, 214, 162), 1.8, G_OC)
    for i, (w, col) in enumerate(((190, (96, 132, 156)), (170, (192, 92, 76)), (150, (112, 152, 104)))):
        c.rect(590 - w / 2, -134 - (i + 1) * 30, 590 + w / 2 + (i % 2) * 10, -134 - i * 30, col, 2.0, G_OC, r=3)
    c.rect(-20, -200, 40, -134, (206, 124, 98), 2.2, G_OC, r=8)
    for i, col in enumerate(((96, 132, 156), (224, 182, 86), (196, 94, 78))):
        c.line([(-10 + i * 18, -200), (-16 + i * 22, -252)], col, 7)
    tint(c, o, True, indoor=True)


# ================================================================= RUANG TAMU (GHIBLI LIVING ROOM)
def ruang_tamu_b(c, t, o):
    wk = waktu_of(o)
    # dinding plester krem-sage hangat + panel kayu bawah + jendela cahaya matahari!
    wall_c = (242, 236, 220) if wk != "malam" else (154, 144, 132)
    wain_c = (206, 178, 144) if wk != "malam" else (122, 102, 86)
    dinding(c, wall_c)
    c.rect(X0, -230, X1, 0, wain_c)
    for px in range(-1200, 1201, 110):
        c.line([(px, -230), (px, 0)], gelap(wain_c, 0.14), 1.5)
    c.rect(X0, -238, X1, -226, gelap(wain_c, 0.18), 1.8, G_OC)
    lantai(c, (204, 160, 118) if wk != "malam" else (136, 106, 82), garis=(172, 130, 92))
    karpet(c, -120, 900, (208, 154, 122), 190)
    # jendela Ghibli di kanan-tengah dengan tirai linen melambai lembut!
    jendela(c, 220, -520, 320, 300, o, tirai=(242, 232, 212), scene_key="ruang_tamu", t=t)
    # sofa kain linen sage-biru hangat + bantal mustard & terakota + bayangan jatuh
    sx = o.get("sofa_x", -260)
    sc = (118, 148, 146)
    c.ell(sx, 12, 390, 22, (58, 52, 66, 48))
    c.rect(sx - 330, -330, sx + 330, -90, gelap(sc, .10), 2.4, G_OC, r=42)
    c.rect(sx - 376, -210, sx - 296, 0, sc, 2.4, G_OC, r=28)
    c.rect(sx + 296, -210, sx + 376, 0, sc, 2.4, G_OC, r=28)
    c.rect(sx - 298, -102, sx + 298, 0, terang(sc, .12), 2.4, G_OC, r=22)
    c.line([(sx, -100), (sx, -14)], G_OC, 2.2)
    c.rect(sx - 278, -306, sx - 172, -190, (218, 128, 98), 2.2, G_OC, r=20)
    c.rect(sx + 172, -296, sx + 278, -190, (232, 192, 102), 2.2, G_OC, r=20)
    # selimut rajut hangat tersampir di sandaran kiri sofa (detail lived-in Ghibli!)
    c.poly([(sx - 374, -206), (sx - 294, -206), (sx - 282, -74), (sx - 368, -68)], (228, 186, 138), 2.0, G_OC)
    for gy_b in (-178, -148, -118, -88):
        c.line([(sx - 368, gy_b), (sx - 290, gy_b - 4)], (196, 148, 102), 2.4)
    # kucing oranye tidur pulas bernapas pelan + ekor melambai di sandaran sofa
    kx, ky = sx + 336, -212
    br_k = math.sin(t * 1.7) * 2.6
    c.ell(kx, ky - 28 - br_k * 0.4, 66, 36 + br_k, (226, 148, 82), 2.2, G_OC)
    c.ell(kx - 52, ky - 52, 32, 28, (226, 148, 82), 2.2, G_OC)
    for sg in (-1, 1):
        c.poly([(kx - 52 + sg * 11, ky - 74), (kx - 52 + sg * 28, ky - 96), (kx - 52 + sg * 30, ky - 68)], (226, 148, 82), 2.0, G_OC)
    c.line([(kx - 62, ky - 52), (kx - 56, ky - 50)], G_OC, 2.4); c.line([(kx - 46, ky - 52), (kx - 40, ky - 50)], G_OC, 2.4)
    c.curve([(kx + 64, ky - 24), (kx + 108, ky - 32 + 10 * math.sin(t * 2.4)), (kx + 126, ky - 68 + 14 * math.sin(t * 2.4))], (214, 134, 72), 10)
    # rak kayu TV + TV retro hangat + tanaman pot Ghibli
    c.rect(540, -172, 1040, 0, (166, 118, 78), 2.4, G_OC, r=4)
    c.rect(562, -154, 780, -22, (148, 102, 66), 1.8, G_OC, r=3)
    c.rect(800, -154, 1018, -22, (148, 102, 66), 1.8, G_OC, r=3)
    c.rect(580, -412, 990, -172, (62, 66, 76), 2.6, G_OC, r=10)
    c.rect(596, -396, 974, -188, (132, 186, 212) if wk != "malam" else (112, 148, 192), 0)
    tanaman(c, -780, 0, 1.15)
    lukisan(c, -680, -525, 220, 152, (142, 194, 224))
    _lampu_gantung_ghibli(c, -180, -860, -640, (224, 198, 146), nyala=(wk == "malam"), r_glow=440)
    _interior_warm_lighting(c, o, 220, -520, 320, 300, lamp_pts=[(-180, -600, 520), (420, -480, 360)], t=t)
    tint(c, o, indoor=True)


def ruang_tamu_f(c, t, o):
    tint(c, o, True, indoor=True)


# ================================================================= JALAN KAMPUNG / KOMPLEK (5 VARIAN RUMAH UNIK!)
def rumah(c, x, w=360, h=280, tembok=(250, 238, 216), atap=(212, 102, 84), gaya=None, t=0.0):
    """5 varian arsitektur rumah Ghibli ('jepang', 'cottage', 'modern_jp', 'vila_kayu', 'toko_kecil') agar TIDAK ADA rumah kembar dalam 1 scene!"""
    if gaya is None:
        gaya = ("jepang", "cottage", "modern_jp", "vila_kayu", "toko_kecil")[(int(round(x / 173)) + (3 if x < 0 else 0)) % 5]
    far = getattr(c, "depth", 1.0) < 0.85
    fog = (182, 212, 232)
    tc = mix(tembok, fog, 0.25) if far else tembok
    ac = mix(atap, fog, 0.25) if far else atap
    wood = mix((136, 98, 72), fog, 0.24) if far else (136, 98, 72)
    wood_d = gelap(wood, 0.28)
    wood_l = terang(wood, 0.18)
    oc = mix((58, 48, 44), fog, 0.45) if far else (58, 48, 44)
    ow_r = OW * (0.48 if far else 0.72)
    c.ell(x + w * 0.08, 6, w * 0.62, 18, (28, 56, 46, 42 if far else 64))

    if gaya == "modern_jp":
        # VARIAN 3: RUMAH 2 LANTAI MODERN JEPANG (balkon lantai 2, atap miring asimetris, kanopi pintu!)
        h2 = h * 1.24
        c.rect(x - w * 0.46, -h2, x + w * 0.46, 0, tc, ow_r, oc)
        c.rect(x + w * 0.18, -h2, x + w * 0.46 - 2, -2, gelap(tc, 0.11))
        # garis lantai 1 / 2 + bayangan
        c.rect(x - w * 0.48, -h2 * 0.50, x + w * 0.48, -h2 * 0.44, wood, ow_r * .7, oc)
        c.rect(x - w * 0.46, -h2 * 0.44, x + w * 0.46, -h2 * 0.38, (54, 58, 74, 56))
        # atap miring asimetris modern (skillion roof)
        c.poly([(x - w * 0.54, -h2 + 6), (x + w * 0.54, -h2 - h * 0.24),
                (x + w * 0.54, -h2 - h * 0.14), (x - w * 0.54, -h2 + 16)], ac, ow_r, oc)
        # balkon kayu lantai 2 di kiri + pintu kaca geser
        c.rect(x - w * 0.36, -h2 * 0.88, x + w * 0.06, -h2 * 0.50, (132, 182, 210), ow_r * .8, oc)
        c.line([(x - w * 0.15, -h2 * 0.88), (x - w * 0.15, -h2 * 0.50)], wood_d, 2.2)
        c.rect(x - w * 0.42, -h2 * 0.68, x + w * 0.12, -h2 * 0.50, wood_l, ow_r * .8, oc, r=2)
        for k in range(1, 7):
            bx = lerp(x - w * 0.42, x + w * 0.12, k / 7.0)
            c.line([(bx, -h2 * 0.68), (bx, -h2 * 0.50)], wood_d, 1.8)
        # jendela kanan lantai 2
        c.rect(x + w * 0.18, -h2 * 0.86, x + w * 0.38, -h2 * 0.60, (138, 188, 216), ow_r * .8, oc, r=2)
        # pintu masuk lantai 1 + kanopi + jendela lebar
        c.rect(x + w * 0.14, -h2 * 0.36, x + w * 0.36, 0, wood, ow_r * .8, oc, r=3)
        c.rect(x + w * 0.10, -h2 * 0.40, x + w * 0.40, -h2 * 0.34, gelap(ac, 0.16), ow_r * .6, oc)
        c.rect(x - w * 0.36, -h2 * 0.36, x + w * 0.04, -h2 * 0.12, (138, 188, 216), ow_r * .8, oc, r=2)
        c.line([(x - w * 0.16, -h2 * 0.36), (x - w * 0.16, -h2 * 0.12)], wood_d, 2.0)
        return

    if gaya == "vila_kayu":
        # VARIAN 4: VILA KAYU ALA TOTORO (menara loteng kanan + beranda bertiang putih + atap terakota bertingkat!)
        # sayap kiri 1 lantai + beranda
        c.rect(x - w * 0.50, -h * 0.78, x + w * 0.08, 0, tc, ow_r, oc)
        c.poly([(x - w * 0.56, -h * 0.74), (x - w * 0.22, -h * 1.12), (x + w * 0.12, -h * 0.74)], ac, ow_r, oc)
        # menara loteng kayu kanan (lebih tinggi & berkarakter!)
        tx0, tx1, th = x + w * 0.04, x + w * 0.48, h * 1.20
        c.rect(tx0, -th, tx1, 0, wood_l, ow_r, oc)
        for k in range(1, 7):
            vy = lerp(-th, 0, k / 7.0)
            c.line([(tx0, vy), (tx1, vy)], gelap(wood_l, 0.16), 1.4)
        c.poly([(tx0 - 16, -th + 8), ((tx0 + tx1) / 2, -th - h * 0.36), (tx1 + 16, -th + 8)], gelap(ac, 0.08), ow_r, oc)
        # jendela tinggi di menara loteng
        c.rect(tx0 + 18, -th + 24, tx1 - 18, -th + 88, (142, 192, 222), ow_r * .8, oc, r=3)
        c.line([((tx0 + tx1) / 2, -th + 24), ((tx0 + tx1) / 2, -th + 88)], (246, 242, 232), 2.2)
        c.rect(tx0 + 20, -h * 0.48, tx1 - 20, -h * 0.14, (142, 192, 222), ow_r * .8, oc, r=3)
        # beranda tiang putih & pintu di sayap kiri
        c.rect(x - w * 0.44, -h * 0.58, x - w * 0.18, 0, wood, ow_r * .8, oc)
        for px_v in (x - w * 0.48, x - w * 0.04):
            c.rect(px_v - 4, -h * 0.74, px_v + 4, 0, (244, 240, 230), ow_r * .6, oc)
        c.rect(x - w * 0.50, -h * 0.22, x + w * 0.02, -h * 0.14, (244, 240, 230), ow_r * .6, oc)
        return

    if gaya == "toko_kecil":
        # VARIAN 5: KEDAI ROTI / TOKO BUNGA KECIL GHIBLI (kanopi kain bergaris, etalase kaca, papan gantung bundar!)
        c.rect(x - w * 0.46, -h * 0.96, x + w * 0.46, 0, tc, ow_r, oc)
        c.rect(x + w * 0.20, -h * 0.96, x + w * 0.46 - 2, -2, gelap(tc, 0.10))
        # atap mansard melengkung
        c.poly([(x - w * 0.52, -h * 0.94), (x - w * 0.36, -h * 1.24), (x + w * 0.36, -h * 1.24), (x + w * 0.52, -h * 0.94)], ac, ow_r, oc)
        # jendela bundar kecil di atas
        c.ell(x, -h * 1.09, 18, 18, (148, 196, 224), ow_r * .8, (244, 238, 224))
        # kanopi bergaris hangat
        ay0, ay1 = -h * 0.62, -h * 0.44
        for k in range(6):
            ax0 = lerp(x - w * 0.50, x + w * 0.50, k / 6.0)
            ax1 = lerp(x - w * 0.50, x + w * 0.50, (k + 1) / 6.0)
            c.poly([(ax0, ay0), (ax1, ay0), (ax1 + 4, ay1), (ax0 - 4, ay1)], ac if k % 2 == 0 else (250, 244, 228), ow_r * .6, oc)
        # etalase kaca lebar + roti/bunga di dalam + pintu kayu kanan
        c.rect(x - w * 0.38, -h * 0.40, x + w * 0.08, -h * 0.08, (238, 224, 188), ow_r * .8, oc, r=4)
        for bx_t, bc_t in ((x - w * 0.28, (226, 152, 78)), (x - w * 0.14, (214, 108, 92)), (x - w * 0.01, (132, 184, 114))):
            c.ell(bx_t, -h * 0.18, 14, 10, bc_t, ow_r * .4, oc)
        c.rect(x + w * 0.14, -h * 0.42, x + w * 0.38, 0, wood, ow_r * .8, oc, r=3)
        c.rect(x + w * 0.18, -h * 0.36, x + w * 0.34, -h * 0.18, (148, 194, 220), ow_r * .5, oc)
        # papan gantung bundar di sisi kiri
        c.line([(x - w * 0.46, -h * 0.78), (x - w * 0.58, -h * 0.78)], wood_d, 3.0)
        c.ell(x - w * 0.56, -h * 0.68, 16, 16, (250, 232, 168), ow_r * .7, oc)
        return

    if gaya == "cottage":
        # PONDOK GHIBLI (gambar 1): dinding krem + batu sudut + gable kayu silang + cerobong asap + sayap samping
        # sayap teras/gudang kecil di kiri
        sx0, sx1 = x - w * 0.64, x - w * 0.44
        c.rect(sx0, -h * 0.56, sx1, 0, gelap(wood, 0.08), ow_r, oc)
        c.poly([(sx0 - 12, -h * 0.54), (sx1 + 4, -h * 0.72), (sx1 + 4, -h * 0.62), (sx0 - 12, -h * 0.46)], gelap(ac, 0.12), ow_r, oc)
        c.rect(sx0 + 12, -h * 0.36, sx1 - 6, 0, (56, 46, 42))
        # badan utama pondok + shading kanan
        c.rect(x - w * 0.46, -h * 0.76, x + w * 0.46, 0, tc, ow_r, oc)
        c.rect(x + w * 0.18, -h * 0.76, x + w * 0.46 - 2, -2, gelap(tc, 0.13))
        # tekstur batu sudut kiri & kanan
        stone_c = mix((168, 162, 148), fog, 0.25) if far else (168, 162, 148)
        for k in range(5):
            sy = -k * (h * 0.14) - 10
            sw_ = 16 + (k % 2) * 8
            c.rect(x - w * 0.46, sy - 14, x - w * 0.46 + sw_, sy, stone_c, ow_r * .5, oc, r=2)
            c.rect(x + w * 0.46 - sw_, sy - 14, x + w * 0.46, sy, gelap(stone_c, 0.14), ow_r * .5, oc, r=2)
        # cerobong batu + asap putih lembut mengepul ke langit
        ch_x = x + w * 0.26
        ch_top = -h * 1.38
        c.rect(ch_x - 16, ch_top, ch_x + 16, -h * 0.92, stone_c, ow_r, oc)
        c.rect(ch_x - 20, ch_top - 8, ch_x + 20, ch_top + 4, gelap(stone_c, 0.16), ow_r * .8, oc, r=2)
        for si in range(5):
            sp = (si + (t * 0.45 % 1.0)) / 5.0
            smx = ch_x + sp * 78 + math.sin(t * 1.8 + si) * 10
            smy = ch_top - 14 - sp * 95
            sr = 10 + sp * 26
            c.ell(smx, smy, sr, sr * 0.78, (255, 253, 248, int(130 * (1.0 - sp))))
        # atap pelana tinggi + segitiga gable kayu silang (half-timber)
        peak_y = -h * 1.32
        eave_y = -h * 0.74
        c.poly([(x - w * 0.56, eave_y + 10), (x, peak_y), (x + w * 0.56, eave_y + 10),
                (x + w * 0.50, eave_y + 22), (x, peak_y + 18), (x - w * 0.50, eave_y + 22)], wood_d, ow_r, oc)
        roof_poly = [(x - w * 0.56, eave_y + 4), (x, peak_y - 8), (x + w * 0.56, eave_y + 4),
                     (x + w * 0.52, eave_y + 14), (x, peak_y + 8), (x - w * 0.52, eave_y + 14)]
        c.poly(roof_poly, ac, ow_r, oc)
        # segitiga dinding gable + rangka kayu silang
        gable = [(x - w * 0.42, eave_y + 4), (x, peak_y + 14), (x + w * 0.42, eave_y + 4)]
        c.poly(gable, tc, ow_r * .8, oc)
        c.line([(x - w * 0.42, eave_y + 4), (x + w * 0.42, eave_y + 4)], wood, 6)
        c.line([(x, peak_y + 14), (x, eave_y + 4)], wood, 5)
        c.line([(x - w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48)), (x + w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48))], wood, 4.5)
        c.line([(x - w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48)), (x - w * 0.34, eave_y + 4)], wood, 4.0)
        c.line([(x + w * 0.22, lerp(eave_y + 4, peak_y + 14, 0.48)), (x + w * 0.34, eave_y + 4)], wood, 4.0)
        # jendela loteng kecil
        c.rect(x - 13, peak_y + 34, x + 13, peak_y + 62, (148, 194, 224), ow_r * .7, oc, r=3)
        c.line([(x, peak_y + 34), (x, peak_y + 62)], wood_d, 2.0)
        # bayangan atap jatuh di dinding
        c.rect(x - w * 0.45, eave_y + 4, x + w * 0.45, eave_y + 22, (58, 52, 68, 58))
        # pintu kayu melengkung + kanopi kecil
        dw, dh = w * 0.11, h * 0.52
        c.rect(x - dw, -dh, x + dw, 0, wood, ow_r, oc, r=4)
        c.line([(x - dw * 0.35, -dh + 4), (x - dw * 0.35, -2)], wood_d, 2.0)
        c.line([(x + dw * 0.35, -dh + 4), (x + dw * 0.35, -2)], wood_d, 2.0)
        c.rect(x - dw - 8, -dh - 10, x + dw + 8, -dh, wood_d, ow_r * .7, oc, r=2)
        c.ell(x + dw * 0.6, -dh * 0.48, 3.8, 3.8, KUNING)
        # jendela berkisi-kisi (4 panel) + bunga kecil di bawahnya
        for jx in (x - w * 0.28, x + w * 0.28):
            jw, jy0, jy1 = w * 0.11, -h * 0.56, -h * 0.30
            c.rect(jx - jw, jy0, jx + jw, jy1, (142, 190, 218), ow_r * .8, oc, r=3)
            c.poly([(jx - jw + 4, jy1 - 3), (jx - jw + 14, jy1 - 3), (jx + jw - 4, jy0 + 3), (jx + jw - 14, jy0 + 3)], (255, 255, 255, 70))
            c.line([(jx, jy0), (jx, jy1)], wood_d, 2.4)
            c.line([(jx - jw, (jy0 + jy1) / 2), (jx + jw, (jy0 + jy1) / 2)], wood_d, 2.4)
            c.rect(jx - jw - 4, jy1, jx + jw + 4, jy1 + 8, wood, ow_r * .6, oc, r=2)
        return

    # RUMAH PEDESAAN JEPANG / MINKA GHIBLI (seperti gambar 3):
    # pondasi batu kali + beranda kayu (engawa) + dinding 2 lapis (kayu bawah + plester atas) + pintu geser shoji + atap pelana lebar
    base_h = h * 0.14
    # pondasi batu kali di bawah rumah
    c.rect(x - w * 0.48, -base_h, x + w * 0.48, 0, (132, 138, 140), ow_r * .8, oc)
    for k in range(8):
        bx = x - w * 0.44 + k * (w * 0.118)
        c.ell(bx, -base_h * 0.5 + (k % 2) * 3, w * 0.06, base_h * 0.48, (164, 170, 168) if k % 2 == 0 else (112, 120, 126), ow_r * .45, oc)
    # dinding utama: plester putih-krem atas + papan kayu vertikal bawah
    wall_top = -h * 0.78
    mid_y = -h * 0.42
    c.rect(x - w * 0.47, wall_top, x + w * 0.47, -base_h, tc, ow_r, oc)
    c.rect(x - w * 0.47, mid_y, x + w * 0.47, -base_h, wood_l, ow_r * .7, oc)
    # garis papan kayu vertikal
    for k in range(1, 14):
        vx = x - w * 0.47 + k * (w * 0.94 / 14)
        c.line([(vx, mid_y), (vx, -base_h)], gelap(wood_l, 0.18), 1.6)
    # bayangan dalam atap (deep eaves shadow khas anime Jepang!)
    c.rect(x - w * 0.47, wall_top, x + w * 0.47, wall_top + h * 0.18, (46, 52, 72, 85))
    # rangka balok kayu tradisional (tiang kiri, tengah, kanan + balok horizontal)
    for tx in (x - w * 0.46, x - w * 0.14, x + w * 0.18, x + w * 0.46):
        c.rect(tx - 4.5, wall_top, tx + 4.5, -base_h, wood_d)
    c.rect(x - w * 0.48, mid_y - 4, x + w * 0.48, mid_y + 4, wood_d)
    # pintu geser shoji (kisi-kisi kertas putih hangat & kaca)
    sh_x0, sh_x1 = x - w * 0.42, x + w * 0.14
    sh_y0, sh_y1 = -h * 0.62, -base_h - 10
    c.rect(sh_x0, sh_y0, sh_x1, sh_y1, (238, 240, 236), ow_r * .8, wood_d)
    # kaca pantulan di panel kiri
    c.rect(sh_x0 + 4, sh_y0 + 4, lerp(sh_x0, sh_x1, 0.48), sh_y1 - 4, (132, 168, 192))
    # kisi-kisi kayu vertikal & horizontal halus
    for k in range(1, 7):
        kx = lerp(sh_x0, sh_x1, k / 7.0)
        c.line([(kx, sh_y0), (kx, sh_y1)], wood_d, 2.0)
    for k in range(1, 4):
        ky = lerp(sh_y0, sh_y1, k / 4.0)
        c.line([(sh_x0, ky), (sh_x1, ky)], wood_d, 1.8)
    # beranda kayu (engawa) menonjol di depan pintu + anak tangga
    c.rect(x - w * 0.50, -base_h - 10, x + w * 0.50, -base_h + 2, wood_l, ow_r * .8, oc, r=2)
    c.rect(x - w * 0.50, -base_h + 2, x + w * 0.50, -base_h + 8, wood_d)
    # atap genteng Jepang lebar dengan sudut overhang menonjol & garis genteng rapat
    rh = h * 0.46
    roof_pts = [(x - w * 0.60, wall_top + 10), (x + w * 0.60, wall_top + 10),
                (x + w * 0.36, wall_top - rh), (x - w * 0.36, wall_top - rh)]
    # bayangan kasau bawah atap
    c.poly([(x - w * 0.58, wall_top + 18), (x + w * 0.58, wall_top + 18),
            (x + w * 0.60, wall_top + 8), (x - w * 0.60, wall_top + 8)], wood_d, ow_r * .7, oc)
    c.poly(roof_pts, ac, ow_r, oc)
    # cel shadow sisi kanan atap + garis-garis genteng horizontal & vertikal halus
    c.poly([(x + w * 0.14, wall_top + 10), (x + w * 0.59, wall_top + 10),
            (x + w * 0.35, wall_top - rh + 2), (x + w * 0.08, wall_top - rh + 2)], gelap(ac, 0.18))
    for k in range(1, 5):
        p = k / 5.0
        gy = lerp(wall_top + 10, wall_top - rh, p)
        gx0 = lerp(x - w * 0.59, x - w * 0.36, p)
        gx1 = lerp(x + w * 0.59, x + w * 0.36, p)
        c.line([(gx0, gy), (gx1, gy)], gelap(ac, 0.24), 1.8)
    for k in range(1, 9):
        p = k / 9.0
        c.line([(lerp(x - w * 0.58, x + w * 0.58, p), wall_top + 10),
                (lerp(x - w * 0.35, x + w * 0.35, p), wall_top - rh)], gelap(ac, 0.18), 1.5)
    # bubungan atap tebal di puncak
    c.rect(x - w * 0.38, wall_top - rh - 10, x + w * 0.38, wall_top - rh + 4, gelap(ac, 0.28), ow_r * .8, oc, r=3)
    c.poly(roof_pts, None, ow_r, oc)


def ruko_kafe(c, x, w=340, h=320, tembok=(228, 236, 238), awning=(48, 146, 98)):
    """Toko/ruko Jepang 2 lantai bergaya Ghibli (gambar 4): genteng kawara, jendela kayu berkisi, AC, kanopi kain & etalase."""
    far = getattr(c, "depth", 1.0) < 0.85
    fog = (182, 212, 232)
    tc = mix(tembok, fog, 0.25) if far else tembok
    ac = mix(awning, fog, 0.25) if far else awning
    wood = mix((168, 112, 68), fog, 0.25) if far else (168, 112, 68)
    oc = mix((52, 48, 46), fog, 0.50) if far else (52, 48, 46)
    ow_r = OW * (0.48 if far else 0.72)
    c.rect(x - w / 2, -h, x + w / 2, 0, tc, ow_r, oc)
    c.rect(x + w * 0.26, -h + 2, x + w / 2 - 2, -2, gelap(tc, 0.10))
    # bayangan lembut di bawah atap
    c.rect(x - w / 2 + 2, -h + 2, x + w / 2 - 2, -h + 26, (54, 68, 80, 65))
    # atap genteng lengkung Jepang (kawara)
    tile_c = mix((96, 152, 158), fog, 0.25) if far else (96, 152, 158)
    c.rect(x - w / 2 - 14, -h - 26, x + w / 2 + 14, -h, tile_c, ow_r, oc, r=4)
    for k in range(11):
        kx = x - w / 2 - 8 + k * ((w + 16) / 11)
        c.ell(kx + 12, -h - 3, 14, 7, gelap(tile_c, 0.22), ow_r * .5, oc)
    # 2 jendela kayu berkisi di lantai 2 + penutup jendela kayu samping
    for jx in (x - w * 0.22, x + w * 0.18):
        c.rect(jx - 48, -h + 36, jx + 48, -h + 114, (116, 168, 188), ow_r * .8, oc, r=3)
        c.rect(jx - 48, -h + 36, jx + 48, -h + 52, (46, 78, 96, 70))
        for k in range(1, 4):
            kx = lerp(jx - 48, jx + 48, k / 4.0)
            c.line([(kx, -h + 36), (kx, -h + 114)], wood, 3.0)
        c.rect(jx - 52, -h + 32, jx + 52, -h + 40, wood, ow_r * .6, oc)
        c.rect(jx - 52, -h + 112, jx + 52, -h + 120, wood, ow_r * .6, oc)
    # 2 unit AC outdoor kecil di bawah jendela (detail ikonik toko Jepang!)
    for ax in (x - w * 0.34, x + w * 0.32):
        c.rect(ax - 22, -196, ax + 22, -166, (226, 224, 214), ow_r * .7, oc, r=3)
        c.ell(ax - 5, -181, 10, 10, (92, 98, 102), ow_r * .5, oc)
    # kanopi kain (awning) hijau bergelombang + lipatan bayangan
    aw_y0, aw_y1 = -164, -122
    c.poly([(x - w / 2 - 8, aw_y0), (x + w / 2 + 8, aw_y0), (x + w / 2 + 14, aw_y1), (x - w / 2 - 14, aw_y1)], ac, ow_r, oc)
    for k in range(1, 8):
        kx = lerp(x - w / 2 - 6, x + w / 2 + 6, k / 8.0)
        c.line([(kx, aw_y0 + 2), (kx + (kx - x) * 0.04, aw_y1 - 2)], gelap(ac, 0.22), 2.2)
    c.rect(x - w / 2 - 12, aw_y1, x + w / 2 + 12, aw_y1 + 10, gelap(ac, 0.20), ow_r * .6, oc)
    # etalase toko hangat di lantai 1 + rak warna-warni + pintu kayu
    c.rect(x - w / 2 + 18, -110, x + w / 2 - 18, 0, (62, 68, 78), ow_r * .8, oc)
    for ry, rc in ((-88, (238, 186, 86)), (-58, (132, 188, 114)), (-30, (236, 134, 88))):
        c.rect(x - w / 2 + 26, ry, x - 10, ry + 18, rc, ow_r * .4, oc, r=2)
    c.rect(x + 18, -104, x + w / 2 - 26, 0, wood, ow_r * .8, oc)
    c.rect(x + 28, -94, x + w / 2 - 36, -44, (242, 224, 184), ow_r * .5, oc)


def jalan_b(c, t, o):
    wk = waktu_of(o)
    langit(c, o, t=t)
    awan_set(c, o, 8, t=t, scene_key="jalan")
    bukit_berlapis(c, o, 0)
    c.set_depth(0.72)
    x0, x1, _, _ = c.visible(500)
    per = 620
    # pastikan setiap slot bangunan & pohon memakai varian BERBEDA (nol kembar kiri-kanan!)
    house_styles = ("jepang", "cottage", "modern_jp", "vila_kayu", "toko_kecil")
    tree_styles = ("rimbun", "sakura", "cemara", "gugur", "bulat_tinggi", "beringin")
    wall_pal = [(250, 238, 214), (224, 236, 242), (248, 224, 214), (234, 240, 218), (244, 232, 226)]
    roof_pal = [(206, 102, 82), (96, 132, 168), (196, 136, 82), (94, 146, 118), (168, 92, 102)]
    for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
        idx_u = i + 40   # offset positif agar -1 dan +1 SELALU beda!
        mod = idx_u % 4
        if mod == 0:
            gaya_p = tree_styles[idx_u % len(tree_styles)]
            pohon(c, i * per + 110, .86 + (idx_u % 3) * .09, HIJAU if idx_u % 2 else HIJAU_TUA, gaya=gaya_p, t=t)
        elif mod == 2:
            ruko_kafe(c, i * per, 330, 310, wall_pal[idx_u % len(wall_pal)],
                      [(206, 86, 76), (62, 148, 134), (222, 152, 68), (94, 128, 168)][idx_u % 4])
        else:
            st_r = house_styles[idx_u % len(house_styles)]
            rumah(c, i * per, 345, 238, wall_pal[idx_u % len(wall_pal)], roof_pal[(idx_u * 2) % len(roof_pal)], gaya=st_r, t=t)
            if wk == "malam":
                rx_m = i * per
                c.rect(rx_m - 110, -142, rx_m + 36, -42, (255, 224, 138, 160))
                glow(c, rx_m - 36, -92, 145, (255, 214, 122), 68)
    c.set_depth(1.0)
    # TROTOAR BERTEKSTUR UBIN + RUMPUT CELAH + ASPAL BERTEKSTUR GHIBLI-SHINKAI (persis referensi jalan user!)
    c.rect(X0, 0, X1, 118, (220, 214, 196), 2.2, G_OC)
    x0, x1, _, _ = c.visible(360)
    # variasi nada tiap ubin trotoar (tidak satu warna datar!) + garis sambungan nat + retakan tipis
    for i in range(int(math.floor(x0 / 160)) - 1, int(math.ceil(x1 / 160)) + 2):
        ux = i * 160
        tone = ((228, 222, 204), (214, 208, 190), (222, 215, 198), (208, 202, 186))[(i + 50) % 4]
        c.poly([(ux, 2), (ux + 160, 2), (ux + 138, 98), (ux - 22, 98)], tone)
        c.line([(ux, 0), (ux - 22, 118)], (172, 166, 152), 2.0)
        # garis nat horisontal tengah trotoar
        c.line([(ux - 10, 50), (ux + 150, 50)], (180, 174, 160), 1.5)
        # rumput kecil menyembul di celah tepi dinding/trotoar (detail khas referensi Shinkai!)
        if (i + 50) % 3 == 0:
            _rumpun_ghibli(c, ux + 32, 6, 0.34, (78, 136, 74), (48, 92, 62), (168, 198, 96), 1.5)
        if (i + 50) % 4 == 1:
            c.line([(ux + 45, 22), (ux + 68, 44), (ux + 58, 62)], (152, 146, 136), 1.2)
    # ubin kuning pemandu disabilitas (tactile paving) dekat zebra cross persis gambar referensi!
    c.poly([(-185, 70), (-45, 70), (-54, 96), (-196, 96)], (228, 196, 96), 1.4, (176, 146, 66))
    c.rect(X0, 98, X1, 118, (182, 176, 164))
    c.line([(X0, 98), (X1, 98)], (154, 148, 138), 1.8)
    # ASPAL JALAN BERTEKSTUR (gradasi hangat-sejuk + bercak aus + retakan halus + saluran air tepi)
    c.rect(X0, 118, X1, 1400, (112, 114, 122))
    c.rect(X0, 118, X1, 136, (152, 150, 144))      # saluran air beton (gutter) di tepi trotoar
    c.rect(X0, 136, X1, 162, G_SH + (56,))         # bayangan jatuh miring trotoar
    c.rect(X0, 260, X1, 1400, (98, 102, 112))
    c.line([(X0, 118), (X1, 118)], G_OC, 2.2)
    # bercak tekstur butiran & tambalan halus aspal + retakan tipis (bukan abu polos!)
    rng_j = random.Random(303)
    for k in range(38):
        ax = rng_j.uniform(-1180, 1180)
        ay = rng_j.uniform(148, 390)
        ac_ = (92, 94, 104, 85) if k % 2 == 0 else (132, 132, 136, 65)
        c.ell(ax, ay, rng_j.uniform(28, 95), rng_j.uniform(6, 16), ac_)
    for cr_x in (-520, -140, 290, 680):
        c.curve([(cr_x, 165), (cr_x + 28, 210), (cr_x + 12, 258), (cr_x + 42, 310)], (76, 80, 90, 110), 1.8)
    # zebra cross dengan sedikit tekstur aus & bayangan biru-slate di atasnya!
    for i in range(-2, 3):
        zx = i * 780
        for k in range(5):
            zy = 152 + k * 34
            c.poly([(zx - 110 - k * 14, zy), (zx + 110 + k * 14, zy),
                    (zx + 118 + k * 14, zy + 20), (zx - 118 - k * 14, zy + 20)], (246, 244, 234, 232))
            # sedikit goresan aus aspal di atas cat putih zebra cross (realistis seperti referensi!)
            c.ell(zx + ((k * 43) % 140) - 70, zy + 10, 24, 5, (108, 110, 118, 95))
    # tiang lampu jalan & bayangan miring biru-slate
    per = 1050
    for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
        px = i * per + 420
        if wk != "malam":
            c.poly([(px - 6, 4), (px + 8, 4), (px + 185, 195), (px + 155, 195)], G_SH + (78,))
        c.rect(px - 6, -430, px + 6, 0, (118, 128, 140), 2.0, G_OC)
        c.rect(px + 1, -430, px + 6, 0, (86, 96, 110))
        c.line([(px, -430), (px + 72, -448)], (104, 114, 128), 8)
        c.ell(px + 78, -444, 22, 12, (255, 242, 174) if wk == "malam" else (228, 232, 236), 2.0, G_OC)
    # kucing kampung santai melintas pelan di trotoar latar (tidak lebay, bikin jalan terasa hidup!)
    _kucing_jalan(c, t, y_ground=28, seed=2, col=(214, 152, 92), arah=1, speed=34.0, s=0.72)
    tint(c, o)
    if wk == "malam":
        for i in range(int(math.floor(x0 / per)) - 1, int(math.ceil(x1 / per)) + 2):
            px = i * per + 420
            glow(c, px + 78, -415, 290, (255, 224, 134), 108, n=12)
            c.ell(px + 78, -444, 18, 10, (255, 250, 220))


def jalan_f(c, t, o):
    tint(c, o, True)


# ================================================================= KANTIN (GHIBLI COZY CANTEEN)
def kantin_b(c, t, o):
    wk = waktu_of(o)
    wall_c = (246, 234, 212) if wk != "malam" else (158, 140, 122)
    dinding(c, wall_c)
    # panel keramik pastel bawah & kayu hangat (tidak lagi dinding kosong!)
    c.rect(X0, -250, X1, 0, (226, 214, 192) if wk != "malam" else (136, 122, 106))
    for px in range(-1200, 1201, 90):
        c.line([(px, -250), (px, 0)], (196, 182, 160), 1.4)
    c.rect(X0, -258, X1, -246, (164, 118, 78), 1.8, G_OC)
    lantai(c, (206, 188, 162) if wk != "malam" else (134, 118, 98), garis=(178, 160, 136))
    # jendela besar kiri agar cahaya Ghibli masuk ke ruang kantin (awan & tirai bergerak lembut!)
    jendela(c, -680, -490, 320, 290, o, tirai=(242, 232, 210), scene_key="kafe", t=t)
    # kios kantin kayu bergaya kedai Jepang hangat + rak dapur belakang + etalase kaca
    c.rect(-290, -420, 740, -100, (194, 152, 108), 2.4, G_OC)
    c.rect(-274, -400, 724, -120, (124, 94, 72))
    # rak piring, mangkuk, & teko di belakang konter
    c.rect(-250, -320, 700, -304, (176, 126, 82), 1.8, G_OC)
    for tx, tc in ((-190, (242, 236, 222)), (-110, (144, 186, 166)), (-30, (218, 132, 92)),
                   (60, (242, 236, 222)), (150, (232, 192, 102)), (260, (156, 184, 198)), (380, (214, 118, 86))):
        c.ell(tx, -334, 24, 14, tc, 1.8, G_OC)
    # konter kayu & etalase kaca makanan
    c.rect(-340, -126, 760, -90, (176, 124, 80), 2.4, G_OC, r=4)
    c.rect(-340, -90, 760, 0, (148, 102, 68), 2.4, G_OC)
    for kx in range(-300, 720, 120):
        c.line([(kx, -90), (kx, 0)], (118, 78, 52), 2.0)
    # atap kanopi kain terakota-krem hangat (bukan merah neon!)
    for i in range(10):
        col = (206, 94, 78) if i % 2 == 0 else (248, 240, 222)
        x = -340 + i * 110
        c.poly([(x, -482), (x + 110, -482), (x + 122, -396), (x - 12, -396)], col, 2.0, G_OC)
    papan_nama(c, 210, -536, 360, 70, o.get("papan", "KANTIN"), (250, 234, 182), 46)
    # papan menu kapur di dinding kanan
    c.rect(820, -610, 1120, -340, (52, 74, 68), 2.4, G_OC, r=8)
    c.text(970, -565, "MENU HARI INI", 24, (250, 226, 146), "judul")
    for my in (-505, -455, -405):
        c.line([(860, my), (1080, my)], (236, 240, 226), 3.0)
    # hidangan hangat di atas konter (mangkuk sup, nasi, roti + uap hangat tipis mengepul!)
    for x, col in ((-180, (226, 148, 76)), (20, (238, 198, 96)), (220, (216, 122, 106)), (440, (132, 184, 118))):
        c.ell(x, -142, 62, 18, (248, 244, 232), 2.0, G_OC)
        c.blob([(x - 44, -150), (x, -196), (x + 44, -150)], col, 2.0, G_OC)
    _uap_hangat(c, -180, -198, t, s=0.85, n=2)
    _uap_hangat(c, 220, -198, t + 1.1, s=0.80, n=2)
    # meja + bangku kayu + tanaman pot Ghibli
    for tx in (-980, 1000):
        c.rect(tx - 170, -180, tx + 170, -150, (194, 144, 98), 2.4, G_OC, r=4)
        c.rect(tx - 10, -150, tx + 10, 0, (108, 112, 122), 2.2, G_OC)
        for sg in (-1, 1):
            c.rect(tx + sg * 190 - 50, -90, tx + sg * 190 + 50, -66, (162, 114, 76), 2.2, G_OC, r=4)
            c.rect(tx + sg * 190 - 6, -66, tx + sg * 190 + 6, 0, (108, 112, 122), 2.0, G_OC)
    tanaman(c, -450, 0, 0.85)
    for lx in (-220, 210, 620):
        _lampu_gantung_ghibli(c, lx, -860, -610, (218, 168, 98), nyala=True, r_glow=300 if wk == "malam" else 190)
    _interior_warm_lighting(c, o, -680, -490, 320, 290, lamp_pts=[(-220, -580, 380), (210, -580, 420), (620, -580, 380)], t=t)
    tint(c, o, indoor=True)


def kantin_f(c, t, o):
    tint(c, o, True, indoor=True)


# ================================================================= LAPANGAN (GHIBLI TEXTURED FIELD)
def lapangan_b(c, t, o):
    langit(c, o, t=t)
    awan_set(c, o, t=t, scene_key="lapangan")
    bukit_berlapis(c, o, 0)
    c.set_depth(0.55)
    c.rect(-2400, -110, 2400, 0, (148, 176, 162, 145), 0)
    for i in range(-16, 17):
        c.line([(i * 150, -110), (i * 150, 0)], (102, 126, 118), 2.8)
    c.line([(-2400, -110), (2400, -110)], (102, 126, 118), 3.2)
    c.set_depth(0.75)
    # 4 spesies pohon berbeda di belakang lapangan (nol kembar!)
    for x, sc_, gy in ((-1380, 0.92, "rimbun"), (-520, 0.84, "cemara"), (880, 0.96, "bulat_tinggi"), (1680, 0.88, "gugur")):
        pohon(c, x, sc_, HIJAU_TUA, gaya=gy, t=t)
    c.set_depth(1.0)
    # lintasan lari tanah merah-pasir lembut di sepanjang batas lapangan belakang
    c.rect(X0, -14, X1, 24, (216, 190, 152))
    # lapangan rumput bergaris + TEKSTUR BERCAK CAHAYA, SERAT RUMPUT & TANAH AUS DEPAN GAWANG!
    c.rect(X0, 18, X1, 1400, (118, 176, 94))
    for i in range(-8, 9):
        if i % 2 == 0:
            c.rect(i * 260, 18, i * 260 + 260, 1400, (104, 164, 84), 0)
    # bercak sinar matahari hangat & bayangan awan menyapu lapangan (painterly sunlit turf!)
    rng_f = random.Random(512)
    for k in range(32):
        fx = rng_f.uniform(-1250, 1250)
        fy = rng_f.uniform(34, 380)
        col_p = (164, 202, 102, 72) if k % 2 == 0 else (68, 124, 74, 58)
        c.ell(fx, fy, rng_f.uniform(65, 175), rng_f.uniform(12, 28), col_p)
    # sedikit bercak tanah aus alami di dekat kotak penalti / gawang kiri-kanan
    for gx_d in (-920, 920):
        c.ell(gx_d, 78, 110, 26, (194, 168, 126, 135))
        c.ell(gx_d + 25, 86, 65, 16, (172, 146, 106, 115))
    # hamparan serat & rumpun rumput halus tersebar di lapangan + pinggir tebal Ghibli
    sway = math.sin(t * 2.0) * 3.5
    for i in range(-20, 21):
        _rumpun_ghibli(c, i * 120, 22, 0.56, (86, 146, 78), (52, 98, 66), (172, 206, 102), sway * 0.7)
    for k in range(44):
        gx_ = rng_f.uniform(-1180, 1180)
        gy_ = rng_f.uniform(46, 360)
        sc_g = 0.42 + (gy_ / 380.0) * 0.48
        _rumpun_ghibli(c, gx_, gy_, sc_g, (94, 152, 78), (58, 108, 68), (168, 204, 100), sway)
    # garis kapur lapangan + lingkaran tengah berongga (curve, bukan solid fill!)
    c.line([(-1600, 260), (1600, 260)], (246, 248, 238, 225), 6.5)
    c.curve(arc_pts(0, 260, 220, 88, 0, 360, 36), (246, 248, 238, 225), 6.5)
    c.ell(0, 260, 12, 6, (248, 250, 242))
    # gawang + bayangan jatuh biru-slate
    for gx, sg in ((-1050, 1), (1050, -1)):
        c.poly([(gx, 14), (gx + sg * 150, 14), (gx + sg * 150 + 55, 66), (gx + 55, 66)], G_SH + (58,))
        c.line([(gx, 16), (gx, -244)], (248, 250, 244), 10)
        c.line([(gx, -244), (gx + sg * 150, -224), (gx + sg * 150, 16)], (248, 250, 244), 9)
        for i in range(1, 6):
            c.line([(gx + sg * 150 * i / 6, -234 + 10 * i / 6), (gx + sg * 150 * i / 6, 16)], (255, 255, 255, 130), 2.5, False)
    if waktu_of(o) != "malam":
        _kupu_kupu_ghibli(c, -480, -30, t, (250, 244, 216), seed=7, s=0.84)
        _daun_melayang(c, t, seed=3, count=2, col=(144, 194, 102))
    tint(c, o)


def lapangan_f(c, t, o):
    tint(c, o, True)


# ================================================================= RUMAH DEPAN (GHIBLI FRONT YARD)
def rumah_depan_b(c, t, o):
    wk = waktu_of(o)
    langit(c, o, t=t)
    awan_set(c, o, t=t, scene_key="rumah_depan")
    bukit_berlapis(c, o, 0)
    c.set_depth(0.75)
    pohon(c, -1060, 1.02, HIJAU_TUA, gaya="rimbun", t=t)
    pohon(c, 1180, .94, HIJAU, gaya="sakura", t=t)
    c.set_depth(1.0)
    rumput(c, warna=(140, 196, 102), t=t)
    # rumah pedesaan Ghibli utuh + asap cerobong tipis + kupu-kupu santai!
    rumah(c, 0, 880, 390, (250, 240, 218), (206, 98, 78), gaya="jepang", t=t)
    _asap_cerobong(c, 225, -455, t, s=1.0)
    if wk == "malam":
        c.rect(-360, -232, 112, -56, (255, 224, 138, 165))
        glow(c, -120, -140, 260, (255, 214, 122), 78)
    _jalan_setapak_ghibli(c, 0, 420)
    _pagar_kayu(c, -980, 96, -290, 96, n_posts=6, s=0.92)
    _pagar_kayu(c, 290, 96, 980, 96, n_posts=6, s=0.92)
    semak(c, -560, 260, 110)
    semak(c, 580, 280, 115)
    for fx, fy, fc in ((-420, 120, PUTIH), (-350, 146, KUNING), (-240, 134, PINK), (260, 126, KUNING), (370, 148, PUTIH), (460, 132, (172, 212, 250))):
        bunga_detail(c, fx, fy, 0.84, fc, "daisy", t=t)
    if wk != "malam":
        _kupu_kupu_ghibli(c, -420, -20, t, (252, 232, 146), seed=3, s=0.92)
        _kupu_kupu_ghibli(c, 450, -35, t, (248, 246, 236), seed=8, s=0.84)
    tint(c, o)


def rumah_depan_f(c, t, o):
    tint(c, o, True)


# ================================================================= MEJA MAKAN / DAPUR (GHIBLI INTERIOR STYLE)
def _pot_tanaman_ghibli(c, x, y, s=1.0, sunlit=True):
    """Pot terakota hangat + rimbunan daun organik menyala terkena sinar jendela Ghibli."""
    oc = (66, 52, 44)
    pot_c = (196, 114, 72)
    c.poly([(x - 32 * s, y - 54 * s), (x + 32 * s, y - 54 * s), (x + 24 * s, y), (x - 24 * s, y)], pot_c, 2.4 * s, oc)
    c.rect(x - 36 * s, y - 62 * s, x + 36 * s, y - 50 * s, terang(pot_c, 0.14), 2.2 * s, oc, r=4)
    c.poly([(x + 4 * s, y - 50 * s), (x + 30 * s, y - 50 * s), (x + 23 * s, y - 2 * s), (x + 4 * s, y - 2 * s)], gelap(pot_c, 0.22))
    leaf_c = (128, 178, 92) if sunlit else (74, 124, 84)
    lobes = [(-38, -22, 34, 24), (36, -18, 32, 22), (-14, -42, 36, 26), (18, -36, 32, 24), (0, -16, 38, 22)]
    _ghibli_canopy(c, x, y - 56 * s, lobes, leaf_c, s * 0.85, 0.0, False, oc, 0.0)


def meja_makan_b(c, t, o):
    """Interior dapur/ruang makan bergaya Ghibli: dinding teal-sage bergradasi, balok kayu, cahaya jendela keemasan & bayangan diagonal."""
    wk = waktu_of(o)
    oc = (62, 50, 44)
    # 1) Dinding teal-sage bergradasi lembut (TETAP HANGAT saat malam dengan lampu dapur menyala!)
    wall_top = (68, 112, 118) if wk != "malam" else (58, 74, 86)
    wall_bot = (132, 168, 158) if wk != "malam" else (96, 112, 114)
    c.gradient(wall_top, wall_bot, 0.0, 0.85)
    c.poly([(-2200, -1200), (-340, -1200), (-340, 0), (-2200, 0)],
           (82, 128, 132) if wk != "malam" else (68, 84, 94))
    c.line([(-340, -1200), (-340, 0)], (52, 86, 92), 3.0)
    # 2) Balok kayu plafon atas
    beam_c = (128, 88, 60)
    c.rect(X0, -680, X1, -595, gelap(beam_c, 0.25), 2.4, oc)
    c.poly([(-380, -595), (-250, -595), (-160, -680), (-320, -680)], beam_c, 2.2, oc)
    c.poly([(180, -595), (310, -595), (440, -680), (280, -680)], beam_c, 2.2, oc)

    # 3) Counter dapur kayu hangat + kabinet teal-pudar di bawah
    wood_c = (198, 134, 78) if wk != "malam" else (154, 108, 68)
    cab_c = (104, 152, 152) if wk != "malam" else (78, 108, 112)
    c.rect(X0, -172, X1, -144, wood_c, 2.6, oc)
    c.rect(X0, -144, X1, 0, cab_c, 2.6, oc)
    for lx in (-740, -480, -220, 80, 360, 620):
        c.rect(lx, -132, lx + 210, -14, gelap(cab_c, 0.08), 2.2, oc, r=4)
        c.ell(lx + 105, -104, 5.5, 5.5, (226, 214, 186), 1.8, oc)
    lantai(c, (176, 126, 84) if wk != "malam" else (126, 94, 68), garis=(142, 98, 64))

    # 4) Jendela kayu tinggi di kanan (terintegrasi penuh siang/sore/malam + awan & daun bergerak halus!)
    jendela(c, 520, -376, 340, 384, o, scene_key="meja_makan", t=t)
    _pot_tanaman_ghibli(c, 460, -184, 0.62, sunlit=(wk != "malam"))
    _pot_tanaman_ghibli(c, 588, -184, 0.54, sunlit=(wk != "malam"))

    # 5) Rak kayu dinding kiri & tengah
    for rx0, rx1, ry in ((-640, -290, -475), (-640, -310, -330), (-120, 220, -405)):
        c.poly([(rx0, ry + 18), (rx1, ry + 18), (rx1 - 68, ry + 92), (rx0 - 68, ry + 92)], (42, 74, 82, 56))
        c.rect(rx0, ry, rx1, ry + 18, wood_c, 2.4, oc, r=4)
        c.poly([(rx0 + 22, ry + 18), (rx0 + 42, ry + 18), (rx0 + 22, ry + 52)], gelap(wood_c, 0.20), 2.0, oc)
        c.poly([(rx1 - 42, ry + 18), (rx1 - 22, ry + 18), (rx1 - 22, ry + 52)], gelap(wood_c, 0.20), 2.0, oc)
    for tx, col in ((-585, (162, 198, 178)), (-505, (226, 198, 146)), (-425, (214, 134, 96)), (-345, (172, 194, 206))):
        c.rect(tx - 22, -536, tx + 22, -475, col, 2.0, oc, r=8)
        c.rect(tx - 16, -548, tx + 16, -534, (238, 228, 208), 1.8, oc, r=4)
    for tx, col in ((-560, (206, 118, 72)), (-455, (232, 224, 206)), (-365, (148, 184, 152))):
        c.ell(tx, -354, 28, 23, col, 2.0, oc)
    _pot_tanaman_ghibli(c, 15, -405, 0.72, sunlit=(wk != "malam"))
    _pot_tanaman_ghibli(c, 135, -405, 0.58, sunlit=(wk != "malam"))
    c.rect(195, -228, 298, -172, (232, 226, 212), 2.2, oc, r=8)
    c.ell(246, -228, 52, 10, (216, 208, 194), 2.0, oc)
    c.ell(246, -238, 10, 7, (186, 178, 164), 1.8, oc)
    _lampu_gantung_ghibli(c, -80, -680, -565, (228, 178, 104), nyala=(wk == "malam"), r_glow=440)
    _interior_warm_lighting(c, o, 520, -376, 340, 384, lamp_pts=[(-80, -540, 480), (240, -420, 360)], t=t)
    tint(c, o, indoor=True)


def meja_makan_f(c, t, o):
    """Meja kayu hangat foreground bergaya Ghibli."""
    wk = waktu_of(o)
    oc = (62, 50, 44)
    wood_top = (224, 156, 92) if wk != "malam" else (172, 122, 76)
    wood_side = (176, 112, 66) if wk != "malam" else (132, 88, 56)
    c.set_depth(1.10)
    c.poly([(-680, 12), (680, 12), (820, 170), (-820, 170)], wood_top, 2.6, oc)
    c.rect(-820, 162, 820, 210, wood_side, 2.4, oc)
    c.ell(385, 58, 92, 18, (112, 68, 48, 62))
    c.ell(105, 66, 86, 16, (112, 68, 48, 58))
    c.ell(435, 16, 48, 40, (124, 178, 116), 2.2, oc)
    c.ell(418, 2, 18, 11, terang((124, 178, 116), 0.25))
    c.rect(412, -26, 458, -14, (148, 198, 136), 2.0, oc, r=5)
    c.ell(142, 32, 60, 28, (198, 124, 72), 2.2, oc)
    c.ell(142, 22, 56, 16, (238, 194, 118), 1.8, oc)
    _uap_hangat(c, 142, 8, t, s=0.85, n=2)
    _uap_hangat(c, 435, -30, t + 0.9, s=0.75, n=2)
    _pot_tanaman_ghibli(c, -485, 74, 0.72, sunlit=(wk != "malam"))
    c.set_depth(1.0)
    tint(c, o, True, indoor=True)


# ================================================================= PADANG / POLOS
def padang_b(c, t, o):
    langit(c, o, t=t)
    awan_set(c, o, t=t, scene_key="padang")
    bukit_berlapis(c, o, 0)
    c.set_depth(0.72)
    pohon(c, -860, .86, HIJAU_TUA, gaya="cemara", t=t)
    pohon(c, 920, .92, HIJAU, gaya="rimbun", t=t)
    c.set_depth(1.0)
    rumput(c, warna=(132, 194, 102), t=t)
    # semak & bunga detail Ghibli organik di padang luas (tanpa bulatan garis hitam lama!)
    semak(c, -1020, 320, 125)
    semak(c, 1060, 340, 130, HIJAU)
    for fx, fy, fc in ((-520, 145, PUTIH), (-280, 185, KUNING), (240, 165, PINK), (540, 195, PUTIH), (780, 150, KUNING)):
        bunga_detail(c, fx, fy, 0.88, fc, "daisy", t=t)
    if waktu_of(o) != "malam":
        _kupu_kupu_ghibli(c, -460, -25, t, (252, 236, 152), seed=6, s=0.92)
        _kupu_kupu_ghibli(c, 440, -40, t, (194, 228, 248), seed=11, s=0.84)
        _daun_melayang(c, t, seed=5, count=2, col=(162, 206, 108))
    tint(c, o)


def padang_f(c, t, o):
    c.set_depth(1.26)
    sway = math.sin(t * 2.0) * 5.0
    for gx, gy, sc in ((-920, 268, 1.45), (-760, 286, 1.32), (820, 276, 1.42), (960, 260, 1.50)):
        _rumpun_ghibli(c, gx, gy, sc, (64, 118, 72), (34, 72, 54), (186, 214, 104), sway)
    c.set_depth(1.0)
    tint(c, o, True)


def polos_b(c, t, o):
    col = o.get("warna", "krem")
    from tokoh import warna as _w
    base = _w(col, (255, 243, 226)) if isinstance(col, str) else tuple(col)
    c.gradient(terang(base, .35), base)
    # lingkaran lembut bernapas sangat halus (latar tetap bersih tanpa partikel acak!)
    c.set_depth(0.5)
    dr_p = math.sin(t * 0.75) * 18.0
    c.ell(220 + dr_p, -330 + math.cos(t * 0.6) * 10.0, 520, 520, mix(base, (255, 255, 255), .5))
    c.ell(-760 - dr_p * 0.7, -520, 190, 190, mix(base, (255, 255, 255), .35))
    c.set_depth(1.0)
    c.rect(X0, 0, X1, 1400, mix(base, (255, 255, 255), .25) if not o.get("lantai") else (240, 223, 195))
    c.line([(X0, 0), (X1, 0)], G_OC, 2.4)
    if not o.get("tanpa_tekstur"):
        _apply_watercolor_bg(c, wk="siang", indoor=True, strength=0.65)


def polos_f(c, t, o):
    pass


# ================================================================= RUANG OTAK & DALAM TUBUH (GHIBLI RETRO ANALOG STUDIO & PAINTERLY BLOODSTREAM)
def _crt_monitor_retro(c, x0, y0, x1, y1, scr_bg=(38, 46, 44), led_col=(142, 188, 146), side="left"):
    """Monitor CRT jadul era 80-90an bergaya Studio Ghibli (casing krem-abu tebal, bezel dalam, scanline halus, tombol putar)."""
    # bayangan jatuh lembut di belakang CRT
    c.rect(x0 + 10, y0 + 12, x1 + 14, y1 + 12, (28, 30, 32, 85), 0, r=14)
    # sisi kedalaman 3D casing CRT (efek bodi tabung gendut!)
    if side == "left":
        c.poly([(x1 - 8, y0 + 6), (x1 + 22, y0 + 18), (x1 + 22, y1 - 12), (x1 - 8, y1 - 4)], (146, 138, 122), 2.2, G_OC)
        c.poly([(x0 + 10, y0), (x1 - 6, y0), (x1 + 20, y0 + 16), (x0 + 22, y0 + 12)], (204, 196, 178), 2.0, G_OC)
    else:
        c.poly([(x0 + 8, y0 + 6), (x0 - 22, y0 + 18), (x0 - 22, y1 - 12), (x0 + 8, y1 - 4)], (146, 138, 122), 2.2, G_OC)
        c.poly([(x0 + 6, y0), (x1 - 10, y0), (x1 - 22, y0 + 12), (x0 - 20, y0 + 16)], (204, 196, 178), 2.0, G_OC)
    # casing depan krem-abu hangat khas komputer/monitor analog 80an
    c.rect(x0, y0, x1, y1, (186, 178, 160), 2.4, G_OC, r=14)
    # highlight tipis tepi atas casing
    c.line([(x0 + 16, y0 + 6), (x1 - 16, y0 + 6)], (216, 208, 192), 2.8)
    # bezel dalam gelap menjorok
    bx0, by0, bx1, by1 = x0 + 18, y0 + 16, x1 - 18, y1 - 36
    c.rect(bx0, by0, bx1, by1, (54, 58, 56), 2.0, G_OC, r=10)
    # layar tabung CRT fosfor redup
    sx0, sy0, sx1, sy1 = bx0 + 10, by0 + 10, bx1 - 10, by1 - 10
    c.rect(sx0, sy0, sx1, sy1, scr_bg, 1.8, (32, 36, 36), r=12)
    # garis scanline CRT sangat halus + kisi tipis
    for gy in range(int(sy0 + 12), int(sy1 - 6), 10):
        c.line([(sx0 + 6, gy), (sx1 - 6, gy)], (255, 255, 255, 10), 1.0)
    # refleksi kaca cembung lembut di pojok kiri atas layar
    c.poly([(sx0 + 14, sy0 + 10), (sx0 + 105, sy0 + 10), (sx0 + 52, sy0 + 78), (sx0 + 14, sy0 + 78)], (232, 236, 224, 18))
    # panel bawah bezel: logo garis kecil + 2 tombol putar analog + lampu power redup
    by_bar = y1 - 18
    c.rect(x0 + 24, by_bar - 5, x0 + 92, by_bar + 5, (148, 140, 126), 1.2, (98, 92, 82), r=3)
    for kx in (x1 - 92, x1 - 64):
        c.ell(kx, by_bar, 9, 9, (132, 126, 114), 1.5, G_OC)
        c.line([(kx, by_bar), (kx + 4, by_bar - 4)], (64, 60, 54), 1.8)
    c.ell(x1 - 34, by_bar, 5.5, 5.5, led_col, 1.4, G_OC)
    return sx0, sy0, sx1, sy1


def _tape_reel_deck(c, x0, y0, x1, y1, t):
    """Tape deck reel-to-reel analog berkayu kenari dengan dua gulungan pita aluminium berputar pelan (khas studio Ghibli!)."""
    # bodi kayu kenari hangat
    c.rect(x0 + 6, y0 + 8, x1 + 8, y1 + 8, (26, 28, 30, 72), 0, r=6)
    c.rect(x0, y0, x1, y1, (112, 78, 52), 2.4, G_OC, r=6)
    # pelat muka besi gelap
    fx0, fy0, fx1, fy1 = x0 + 14, y0 + 12, x1 - 14, y1 - 12
    c.rect(fx0, fy0, fx1, fy1, (54, 58, 60), 1.8, G_OC, r=4)
    # 2 gulungan pita aluminium berputar lembut
    ry = fy0 + (fy1 - fy0) * 0.38
    rx_l, rx_r = fx0 + (fx1 - fx0) * 0.29, fx0 + (fx1 - fx0) * 0.71
    rr = min(38, (fy1 - fy0) * 0.31)
    # pita coklat yang menghubungkan kedua gulungan lewat head bawah
    c.line([(rx_l - rr * 0.75, ry + rr * 0.4), (rx_l - 12, fy1 - 30), (rx_r + 12, fy1 - 30), (rx_r + rr * 0.75, ry + rr * 0.4)], (92, 66, 48), 3.0)
    for rx, dir_s in ((rx_l, 1.0), (rx_r, 1.0)):
        c.ell(rx, ry, rr + 2, rr + 2, (42, 44, 46), 1.6, G_OC)
        c.ell(rx, ry, rr, rr, (176, 172, 162), 1.8, G_OC)
        c.ell(rx, ry, rr * 0.62, rr * 0.62, (96, 72, 54), 1.2, (58, 44, 34))
        # 3 lubang segitiga/lingkaran pada reel yang ikut berputar
        ang0 = t * 1.4 * dir_s
        for k in range(3):
            a = ang0 + k * (2 * math.pi / 3)
            c.ell(rx + math.cos(a) * rr * 0.46, ry + math.sin(a) * rr * 0.46, rr * 0.17, rr * 0.17, (54, 58, 60), 1.2, G_OC)
        c.ell(rx, ry, rr * 0.22, rr * 0.22, (198, 194, 184), 1.4, G_OC)
        c.ell(rx, ry, 5, 5, (64, 62, 58))
    # baris tombol transport analog + roller bawah
    c.rect(fx0 + 18, fy1 - 26, fx1 - 18, fy1 - 8, (72, 76, 78), 1.4, G_OC, r=3)
    for bi in range(5):
        bx = fx0 + 36 + bi * 32
        col_b = (174, 96, 82) if bi == 0 else (166, 162, 150)
        c.rect(bx, fy1 - 22, bx + 22, fy1 - 12, col_b, 1.2, G_OC, r=2)
    # 2 meter VU mungil di sisi kanan bawah deck
    for vx in (fx1 - 110, fx1 - 60):
        c.rect(vx, fy1 - 24, vx + 38, fy1 - 10, (218, 196, 146), 1.2, G_OC, r=2)
        na = math.sin(t * 3.1 + vx) * 0.55
        c.line([(vx + 19, fy1 - 11), (vx + 19 + math.sin(na) * 10, fy1 - 21)], (62, 48, 42), 1.6)


def ruang_otak_b(c, t, o):
    """Ruang kendali otak bergaya Studio Ghibli Analog Retro 80-90an (dinding akustik arang-hangat, CRT krem, reel-to-reel, papan gabus & plakat kuningan)."""
    if "istirahat_t" in o and t >= float(o["istirahat_t"]):
        bahaya, mode = False, "istirahat"
    elif "bahaya_t" in o:
        bahaya = t >= float(o["bahaya_t"])
        mode = "bahaya" if bahaya else o.get("mode", "normal")
    else:
        bahaya = bool(o.get("bahaya"))
        mode = o.get("mode", "bahaya" if bahaya else "normal")

    # 1) Dinding studio akustik abu-arang redup hangat (TIDAK mencolok, palet Ghibli studio 80an!)
    w_top = (88, 66, 64) if bahaya else ((66, 70, 76) if mode == "istirahat" else (74, 78, 82))
    w_bot = (104, 78, 72) if bahaya else ((80, 84, 90) if mode == "istirahat" else (90, 94, 96))
    c.gradient(w_top, w_bot, 0.0, 0.85)

    wood_m = (118, 84, 56)
    wood_d = (84, 58, 38)
    brass = (186, 154, 98)
    brass_d = (126, 100, 60)

    # Panel busa akustik piramida (kanan atas) & bilah kayu akustik (kiri-tengah) khas studio rekaman retro
    c.set_depth(0.95)
    for rx in range(250, 960, 42):
        for ry in range(-900, -540, 42):
            c.poly([(rx, ry + 21), (rx + 21, ry), (rx + 42, ry + 21), (rx + 21, ry + 42)], gelap(w_top, 0.14), 1.0, gelap(w_top, 0.24))
            c.poly([(rx + 8, ry + 21), (rx + 21, ry + 8), (rx + 21, ry + 21)], terang(w_top, 0.08))
    # panel bilah dinding vertikal lembut di belakang
    for vx in range(-940, 960, 76):
        c.line([(vx, -900), (vx, -240)], gelap(w_top, 0.16), 1.8)
    # wainscoting / panel kayu kenari hangat di bagian bawah dinding
    c.rect(-1200, -248, 1200, 0, wood_m, 2.2, G_OC)
    c.rect(-1200, -258, 1200, -242, wood_d, 1.8, G_OC)
    for px in range(-960, 980, 120):
        c.line([(px, -242), (px, 0)], wood_d, 1.8)
    c.set_depth(1.0)

    # 2) Lantai papan kayu studio hangat yang tenang
    fl_c = (94, 76, 60) if not bahaya else (98, 70, 58)
    lantai(c, fl_c, garis=gelap(fl_c, 0.22))

    # 3) JENDELA OBSERVASI KIRI ATAS (khas ruang kontrol studio: bingkai kayu kenari + ruang sebelah ber-lampu amber hangat!)
    wx0, wy0, wx1, wy1 = -905, -808, -515, -598
    c.rect(wx0 - 12, wy0 - 12, wx1 + 12, wy1 + 12, wood_m, 2.4, G_OC, r=4)
    c.rect(wx0, wy0, wx1, wy1, (54, 58, 62), 2.0, G_OC)
    # siluet ruang studio sebelah (lampu meja kuning hangat redup + meja + rak)
    c.rect(wx0 + 4, wy0 + 125, wx1 - 4, wy1 - 4, (78, 68, 62))
    c.rect(wx0 + 26, wy0 + 36, wx0 + 115, wy0 + 155, (64, 62, 64), 1.4, (44, 44, 46))
    c.rect(wx1 - 125, wy0 + 48, wx1 - 24, wy0 + 150, (68, 62, 58), 1.4, (46, 42, 40))
    # lampu dinding/meja hangat redup di ruang sebelah
    glow(c, wx0 + 205, wy0 + 98, 115, (242, 198, 126), 62, n=9)
    c.rect(wx0 + 190, wy0 + 74, wx0 + 220, wy0 + 110, (246, 220, 162), 1.4, (152, 118, 72), r=4)
    c.rect(wx0 + 196, wy0 + 110, wx0 + 214, wy0 + 128, (108, 86, 64), 1.2, G_OC)
    # refleksi kaca jendela tipis diagonal
    c.poly([(wx0 + 30, wy1 - 4), (wx0 + 95, wy1 - 4), (wx0 + 210, wy0 + 4), (wx0 + 145, wy0 + 4)], (232, 234, 228, 22))
    c.poly([(wx0, wy0), (wx1, wy0), (wx1, wy1), (wx0, wy1)], None, 2.2, wood_d)

    # 4) JAM DINDING ANALOG BULAT KANAN ATAS (persis sudut kanan atas referensi!)
    cx_k, cy_k, cr_k = 790, -726, 72
    c.ell(cx_k + 5, cy_k + 6, cr_k + 5, cr_k + 5, (32, 34, 36, 65))
    c.ell(cx_k, cy_k, cr_k + 8, cr_k + 8, (156, 154, 146), 2.4, G_OC)
    c.ell(cx_k, cy_k, cr_k, cr_k, (232, 224, 204), 1.8, (112, 108, 98))
    for hi in range(12):
        ha = math.radians(hi * 30 - 90)
        r_in = cr_k - (14 if hi % 3 == 0 else 9)
        w_t = 3.0 if hi % 3 == 0 else 1.6
        c.line([(cx_k + math.cos(ha) * r_in, cy_k + math.sin(ha) * r_in),
                (cx_k + math.cos(ha) * (cr_k - 4), cy_k + math.sin(ha) * (cr_k - 4))], (68, 62, 56), w_t)
    # jarum jam, menit, dan detik halus
    a_hr = math.radians(305 - 90)
    a_mn = math.radians(72 - 90)
    a_sc = math.radians((t * 6.0) % 360.0 - 90)
    c.line([(cx_k, cy_k), (cx_k + math.cos(a_hr) * 33, cy_k + math.sin(a_hr) * 33)], (54, 48, 44), 4.4)
    c.line([(cx_k, cy_k), (cx_k + math.cos(a_mn) * 48, cy_k + math.sin(a_mn) * 48)], (54, 48, 44), 3.0)
    c.line([(cx_k, cy_k), (cx_k + math.cos(a_sc) * 52, cy_k + math.sin(a_sc) * 52)], (166, 78, 66), 1.6)
    c.ell(cx_k, cy_k, 5, 5, (64, 58, 52))

    # 5) TENGAH ATAS: PLAKAT NAMA KUNINGAN VINTAGE (berbentuk sudut lekuk klasik + bingkai kuningan utuh di dalam frame!)
    px0, py0, px1, py1 = -244, -812, 244, -694
    nt = 15
    plaque_pts = [
        (px0 + nt, py0), (px1 - nt, py0), (px1 - nt, py0 + nt), (px1, py0 + nt),
        (px1, py1 - nt), (px1 - nt, py1 - nt), (px1 - nt, py1), (px0 + nt, py1),
        (px0 + nt, py1 - nt), (px0, py1 - nt), (px0, py0 + nt), (px0 + nt, py0 + nt),
    ]
    c.poly([(x + 4, y + 6) for x, y in plaque_pts], (26, 26, 28, 78))
    plaque_bg = (68, 40, 38) if bahaya else (48, 44, 38)
    c.poly(plaque_pts, plaque_bg, 3.6, brass)
    # garis bingkai kuningan dalam + 4 paku keling kuningan
    c.poly([(px0 + 18, py0 + 10), (px1 - 18, py0 + 10), (px1 - 10, py0 + 18), (px1 - 10, py1 - 18),
            (px1 - 18, py1 - 10), (px0 + 18, py1 - 10), (px0 + 10, py1 - 18), (px0 + 10, py0 + 18)], None, 1.5, brass_d)
    for rx, ry in ((px0 + 22, py0 + 22), (px1 - 22, py0 + 22), (px0 + 22, py1 - 22), (px1 - 22, py1 - 22)):
        c.ell(rx, ry, 4.5, 4.5, brass, 1.0, brass_d)
    if bahaya:
        c.text(0, py0 + 42, "STATUS BAHAYA!", 38, (228, 134, 102), "seru")
        c.text(0, py0 + 86, "VIRUS TERDETEKSI", 20, (226, 200, 152), "judul")
    elif mode == "istirahat":
        c.text(0, py0 + 42, "MODE ISTIRAHAT", 36, (186, 206, 214), "judul")
        c.text(0, py0 + 86, "PEMULIHAN TUBUH", 20, (222, 212, 186), "teks")
    else:
        c.text(0, py0 + 42, "TUBUH NORMAL", 38, (236, 216, 168), "judul")
        c.text(0, py0 + 86, "SEMUA KENDALI AKTIF", 20, (198, 196, 178), "teks")

    # 6) PAPAN GABUS (CORKBOARD) DENGAN CATATAN KERTAS KREM BERPIN (tepat di bawah plakat kuningan, bebas kepala Kribo!)
    cbx0, cby0, cbx1, cby1 = -224, -676, 224, -492
    c.rect(cbx0 + 5, cby0 + 6, cbx1 + 6, cby1 + 6, (28, 28, 30, 68), 0, r=4)
    c.rect(cbx0, cby0, cbx1, cby1, wood_m, 2.2, G_OC, r=4)
    c.rect(cbx0 + 12, cby0 + 12, cbx1 - 12, cby1 - 12, (172, 138, 98), 1.6, wood_d, r=2)
    # tekstur titik gabus lembut
    for gi in range(18):
        gx_c = cbx0 + 26 + (gi * 47) % (cbx1 - cbx0 - 52)
        gy_c = cby0 + 24 + (gi * 31) % (cby1 - cby0 - 48)
        c.ell(gx_c, gy_c, 3.0, 2.2, (148, 116, 80, 120))
    # 3 lembar catatan tempel krem dengan pin kecil (khas studio Ghibli!)
    notes_cfg = [
        (-196, -654, -76, -566, (234, 224, 198), (174, 88, 76), "CATATAN", "TENANG"),
        (-56, -650, 62, -560, (228, 218, 192), (112, 148, 118), "KENDALI", "STABIL" if not bahaya else "SIAGA!"),
        (82, -656, 198, -568, (236, 228, 206), (176, 142, 86), "LOG 07", "OK" if not bahaya else "CEK!"),
    ]
    for nx0, ny0, nx1, ny1, nc, pin_c, t1, t2 in notes_cfg:
        c.rect(nx0 + 3, ny0 + 4, nx1 + 3, ny1 + 4, (112, 86, 58, 75))
        c.rect(nx0, ny0, nx1, ny1, nc, 1.4, (124, 108, 86))
        c.ell((nx0 + nx1) / 2, ny0 + 9, 5.5, 5.5, pin_c, 1.2, G_OC)
        c.text((nx0 + nx1) / 2, ny0 + 36, t1, 15, (72, 62, 52), "judul")
        c.text((nx0 + nx1) / 2, ny0 + 62, t2, 17, (162, 74, 64) if bahaya else (66, 112, 76), "judul")
    # 2 kartu catatan kecil baris bawah papan gabus
    for mx0, my0, mx1, my1 in ((-148, -552, -32, -508), (24, -550, 152, -508)):
        c.rect(mx0, my0, mx1, my1, (226, 216, 192), 1.3, (126, 110, 88))
        c.ell((mx0 + mx1) / 2, my0 + 7, 4.5, 4.5, (156, 128, 82), 1.0, G_OC)
        c.line([(mx0 + 16, my0 + 21), (mx1 - 16, my0 + 21)], (118, 106, 92), 2.0)
        c.line([(mx0 + 16, my0 + 32), (mx1 - 28, my0 + 32)], (118, 106, 92), 2.0)

    # 7) STASIUN KIRI: MONITOR CRT JADUL DETAK JANTUNG + RAK KAYU & KASET DATA
    # rak kayu di bawah CRT kiri
    c.rect(-915, -264, -395, -242, wood_m, 2.2, G_OC, r=3)
    c.rect(-895, -242, -875, -180, wood_d, 1.8, G_OC)
    c.rect(-435, -242, -415, -180, wood_d, 1.8, G_OC)
    # tumpukan 3 kaset pita/data retro rapi di bawah rak kiri
    for ci, ky in enumerate((-202, -218, -234)):
        c.rect(-852, ky, -748, ky + 15, (156, 148, 134) if ci % 2 == 0 else (128, 122, 112), 1.4, G_OC, r=2)
        c.rect(-840, ky + 3, -764, ky + 12, (224, 216, 194), 0.8, (96, 88, 76))
    led_l = (206, 114, 92) if bahaya else ((142, 178, 192) if mode == "istirahat" else (142, 188, 146))
    lx0, ly0, lx1, ly1 = _crt_monitor_retro(c, -892, -578, -424, -264, scr_bg=(36, 44, 42), led_col=led_l, side="left")
    # header bar tipis di dalam CRT kiri
    c.rect(lx0 + 4, ly0 + 4, lx1 - 4, ly0 + 34, (48, 58, 54), 1.0, (78, 92, 84), r=4)
    c.text((lx0 + lx1) / 2, ly0 + 19, "DETAK JANTUNG", 18, (214, 212, 194), "judul")
    # kisi osiloskop CRT redup
    for gx in range(int(lx0 + 36), int(lx1 - 18), 44):
        c.line([(gx, ly0 + 40), (gx, ly1 - 12)], (124, 152, 134, 34), 1.0)
    for gy in range(int(ly0 + 60), int(ly1 - 16), 38):
        c.line([(lx0 + 10, gy), (lx1 - 10, gy)], (124, 152, 134, 34), 1.0)
    # gelombang ECG fosfor vintage (redup lembut, TIDAK neon!)
    ecg_c = (212, 124, 98) if bahaya else ((150, 184, 194) if mode == "istirahat" else (148, 194, 156))
    pts = []
    speed = 5.2 if bahaya else (1.8 if mode == "istirahat" else 3.0)
    for k in range(30):
        xx = lx0 + 16 + k * ((lx1 - lx0 - 32) / 29.0)
        ph = (k * 0.44 - t * speed) % 3.2
        yy = (ly0 + ly1) * 0.52 + 8
        if 1.2 < ph < 1.45:
            yy -= 56
        elif 1.45 <= ph < 1.7:
            yy += 32
        elif 0.8 < ph <= 1.2:
            yy -= 13
        pts.append((xx, yy))
    c.line(pts, ecg_c + (58,), 9.0, False)
    c.line(pts, ecg_c, 3.6, False)
    c.ell(pts[-1][0], pts[-1][1], 5.5, 5.5, (224, 236, 218))
    bpm_txt = "124 BPM" if bahaya else ("58 BPM" if mode == "istirahat" else "72 BPM")
    c.rect(lx0 + 12, ly1 - 38, lx0 + 136, ly1 - 10, (44, 52, 48), 1.4, ecg_c, r=4)
    c.text(lx0 + 74, ly1 - 24, bpm_txt, 19, (226, 224, 206), "judul")

    # 8) STASIUN KANAN: MONITOR CRT JADUL SUHU TUBUH + TAPE DECK REEL-TO-REEL ANALOG!
    rx0, ry0, rx1, ry1 = _crt_monitor_retro(c, 424, -622, 876, -342, scr_bg=(38, 45, 43), led_col=led_l, side="right")
    c.rect(rx0 + 4, ry0 + 4, rx1 - 4, ry0 + 34, (48, 58, 54), 1.0, (78, 92, 84), r=4)
    c.text((rx0 + rx1) / 2, ry0 + 19, "SUHU TUBUH", 18, (214, 212, 194), "judul")
    suhu_txt = "39.2 C" if bahaya else ("37.4 C" if mode == "istirahat" else "36.6 C")
    suhu_col = (216, 128, 98) if bahaya else ((214, 186, 122) if mode == "istirahat" else (154, 196, 160))
    suhu_sub = "TINGGI" if bahaya else ("HANGAT" if mode == "istirahat" else "NORMAL")
    c.text((rx0 + rx1) / 2, ry0 + 82, suhu_txt, 46, suhu_col, "seru")
    c.text((rx0 + rx1) / 2, ry0 + 118, suhu_sub, 18, (206, 202, 184), "judul")
    # bar segmen analog lembut di bawah angka suhu (khas monitor audio/studio jadul!)
    seg_n = 14
    seg_on = 12 if bahaya else (8 if mode == "istirahat" else 6)
    seg_w = (rx1 - rx0 - 44) / seg_n
    for si in range(seg_n):
        sx = rx0 + 22 + si * seg_w
        if si < seg_on:
            sc_i = (196, 114, 92) if si >= 10 else ((204, 178, 114) if si >= 7 else (142, 184, 148))
        else:
            sc_i = (56, 64, 60)
        c.rect(sx + 2, ry1 - 42, sx + seg_w - 3, ry1 - 20, sc_i, 1.0, (32, 38, 36), r=2)
    # Tape deck reel-to-reel kayu kenari persis di bawah CRT kanan!
    _tape_reel_deck(c, 424, -338, 876, -182, t)

    # 9) LAMPU GANTUNG KUNINGAN HANGAT & LAMPU MEJA KLASIK DI KANAN (pencahayaan studio Ghibli yang teduh!)
    _lampu_gantung_ghibli(c, -450, -920, -760, brass, nyala=True, r_glow=250)
    _lampu_gantung_ghibli(c, 450, -920, -760, brass, nyala=True, r_glow=250)
    # lampu meja kuningan klasik di tepi kanan dekat tape deck (persis sudut kanan bawah referensi!)
    c.line([(930, -182), (945, -310), (898, -372)], (96, 86, 74), 6.0)
    c.poly([(862, -378), (924, -398), (938, -342), (852, -332)], brass, 2.2, G_OC)
    c.ell(886, -342, 24, 12, (250, 228, 170))
    glow(c, 872, -330, 175, (250, 212, 142), 52, n=10)

    if bahaya:
        # kedip amber-merah bata lembut (tidak norak/mencolok!)
        al = int(18 + 14 * (0.5 + 0.5 * math.sin(t * 7)))
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=(186, 64, 48, al))
    if not o.get("tanpa_tekstur"):
        _apply_watercolor_bg(c, wk="malam", indoor=True, strength=0.85)


def ruang_otak_f(c, t, o):
    if o.get("konsol", True):
        wood_m = (118, 84, 56)
        wood_d = (84, 58, 38)
        bahaya = bool(o.get("bahaya"))
        # bayangan meja mixer analog di lantai kayu (tinggi proporsional agar maskot pendek seperti Sang Otak terlihat penuh!)
        c.ell(0, 14, 560, 24, (32, 26, 22, 72))
        c.poly([(-488, -134), (488, -134), (548, 0), (-548, 0)], (146, 142, 132), 2.4, G_OC)
        c.poly([(-482, -130), (482, -130), (516, -54), (-516, -54)], (176, 172, 162), 2.0, G_OC)
        c.poly([(-478, -148), (478, -148), (486, -126), (-486, -126)], (56, 60, 62), 2.0, G_OC)
        c.poly([(-512, -148), (-478, -148), (-516, 0), (-554, 0)], wood_m, 2.2, G_OC)
        c.poly([(478, -148), (512, -148), (554, 0), (516, 0)], wood_m, 2.2, G_OC)
        c.line([(-514, -54), (514, -54)], wood_d, 4.0)
        for vx in (-270, 270):
            c.rect(vx - 54, -144, vx + 54, -128, (228, 204, 146), 1.4, G_OC, r=2)
            na = math.sin(t * 2.6 + vx) * 0.65
            c.line([(vx, -129), (vx + math.sin(na) * 12, -142)], (62, 48, 42), 2.0)
        for li in range(-6, 7):
            lx = li * 16
            lcol = (206, 114, 92) if (bahaya and li % 2 == 0) else ((218, 192, 116) if li % 3 == 0 else (142, 182, 144))
            c.ell(lx, -136, 3.5, 3.5, lcol)
        for ch in range(-7, 8):
            fx_top = ch * 58
            fx_bot = ch * 62
            c.line([(fx_top, -118), (fx_bot, -62)], (74, 72, 68), 3.4)
            c.ell(fx_top, -121, 6, 4.5, (84, 82, 78), 1.1, G_OC)
            frac = 0.28 + 0.45 * ((ch * 37 + 19) % 10) / 10.0
            fy = -112 + frac * 44
            fx = fx_top + (fx_bot - fx_top) * frac
            cap_c = (176, 86, 74) if abs(ch) <= 1 else ((224, 218, 202) if ch % 2 == 0 else (88, 90, 92))
            c.rect(fx - 10, fy - 5, fx + 10, fy + 5, cap_c, 1.3, G_OC, r=2)
            c.line([(fx - 7, fy), (fx + 7, fy)], (242, 238, 228) if cap_c[0] < 140 else (68, 62, 56), 1.2)
        c.rect(-170, -42, 170, -12, (66, 68, 70), 1.6, G_OC, r=4)
        for gx in range(-152, 156, 16):
            c.line([(gx, -36), (gx, -18)], (104, 102, 96), 2.2)
        c.rect(-466, -158, -432, -130, (234, 228, 212), 1.8, G_OC, r=4)
        c.curve(arc_pts(-430, -145, 10, 9, -90, 90, 10), G_OC, 2.2)
        c.ell(-449, -158, 16, 4, (132, 92, 62), 1.2, G_OC)
        _uap_hangat(c, -449, -166, t, s=0.68, n=2)


def dalam_tubuh_b(c, t, o):
    """Terowongan pembuluh darah bergaya Ghibli Painterly (lapisan dinding organik bercahaya, arus plasma, sel darah 3D lembut)."""
    demam = bool(o.get("demam"))
    # 1) Gradasi hangat subsurface-scattering (merah anggur dalam -> karang-mawar -> cahaya persik di tengah)
    top = (158, 42, 46) if demam else (154, 58, 86)
    mid = (218, 78, 62) if demam else (214, 104, 128)
    bot = (248, 134, 92) if demam else (246, 168, 176)
    c.gradient(top, mid, 0.0, 0.46)
    c.gradient(mid, bot, 0.46, 0.92)
    # pendaran cahaya hangat dari kedalaman terowongan (memberi ilusi ruang 3D melengkung!)
    c.set_depth(0.25)
    glow(c, 0, -340, 780, (255, 198, 146) if demam else (255, 214, 218), 64, n=12)

    # 2) Lapisan dinding terowongan jauh & arus plasma bercahaya lembut (TANPA outline hitam kasar!)
    c.set_depth(0.42)
    wall_far = (132, 36, 44) if demam else (138, 52, 78)
    wall_mid = (168, 48, 52) if demam else (168, 68, 96)
    c.blob([(-2600, -1200), (-2600, -640), (-1500, -560), (-500, -660), (450, -540), (1450, -650), (2600, -560), (2600, -1200)], wall_far, 0, n=7)
    c.blob([(-2600, -1200), (-2600, -720), (-1350, -650), (-250, -740), (850, -640), (1950, -730), (2600, -660), (2600, -1200)], wall_mid, 0, n=7)
    # highlight basah halus di tepi lengkungan dinding atas
    c.curve([(-2200, -690), (-1250, -630), (-220, -715), (850, -625), (1950, -705)], (255, 210, 206, 78), 7)
    # pita arus plasma mengalir di kejauhan
    for sy_p, al_p in ((-490, 48), (-330, 58), (-180, 44)):
        c.curve([(-2400, sy_p), (-1100, sy_p - 38), (0, sy_p + 26), (1100, sy_p - 32), (2400, sy_p)],
                (255, 224, 182, al_p) if demam else (255, 232, 236, al_p), 18)

    # 3) Sel darah merah bikonkaf 3D painterly berlapis (jauh buram-lembut -> tengah detail berkilau basah!)
    def _rbc_3d(rx, ry, rw, rh, col_r, al_r=255):
        oc_r = gelap(col_r, 0.36)
        sh_r = gelap(col_r, 0.22)
        hl_r = terang(col_r, 0.32)
        if al_r < 255:
            c.ell(rx, ry, rw, rh, col_r + (al_r,))
            c.ell(rx + rw * 0.06, ry + rh * 0.08, rw * 0.48, rh * 0.44, sh_r + (al_r,))
            c.ell(rx - rw * 0.28, ry - rh * 0.28, rw * 0.26, rh * 0.16, (255, 234, 230, int(al_r * 0.55)))
        else:
            c.ell(rx + 4, ry + 6, rw, rh, (108, 30, 46, 52))
            c.ell(rx, ry, rw, rh, col_r, 2.0, oc_r)
            c.ell(rx + rw * 0.05, ry + rh * 0.10, rw * 0.52, rh * 0.46, sh_r)
            c.ell(rx - rw * 0.02, ry + rh * 0.04, rw * 0.32, rh * 0.26, gelap(col_r, 0.32))
            c.ell(rx - rw * 0.32, ry - rh * 0.30, rw * 0.28, rh * 0.16, hl_r)
            c.ell(rx - rw * 0.36, ry - rh * 0.34, rw * 0.14, rh * 0.08, (255, 244, 240, 210))

    rbc_far = (212, 86, 102) if not demam else (228, 92, 68)
    for i in range(6):
        rx = -1500 + ((i * 510 + t * (48 if demam else 28)) % 3000)
        ry = -540 + (i % 3) * 145 + math.sin(t * 1.6 + i * 1.4) * 12
        _rbc_3d(rx, ry, 42, 24, rbc_far, al_r=155)
    c.set_depth(0.68)
    rbc_c = (224, 64, 76) if not demam else (238, 86, 52)
    for i in range(5):
        rx = -1400 + ((i * 620 + t * (92 if demam else 52)) % 2800)
        ry = -500 + (i % 3) * 155 + math.sin(t * 2.1 + i) * 16
        _rbc_3d(rx, ry, 58, 33, rbc_c)
    c.set_depth(1.0)

    # 4) Lantai jaringan organik bergelombang lembut (bukan garis-garis papan kayu lurus!)
    fl_base = (212, 92, 74) if demam else (218, 122, 140)
    fl_hi = terang(fl_base, 0.14)
    fl_sh = gelap(fl_base, 0.18)
    c.rect(X0, 0, X1, 1400, fl_base)
    c.blob([(-2600, 14), (-1600, -14), (-520, 12), (480, -10), (1560, 14), (2600, -8), (2600, 140), (-2600, 140)], fl_hi, 0, n=6)
    c.blob([(-2600, 130), (-1450, 96), (-320, 142), (760, 102), (1880, 144), (2600, 110), (2600, 1400), (-2600, 1400)], fl_sh, 0, n=6)
    # kilau basah organik lembut di permukaan lantai pembuluh
    for wx in (-720, -240, 260, 740):
        c.ell(wx, 48 + (abs(wx) % 3) * 28, 140, 16, (255, 224, 226, 64))
    if demam:
        c.rect(520, -640, 620, -240, (255, 240, 232), 2.6, G_OC, r=42)
        c.ell(570, -220, 66, 66, (255, 240, 232), 2.6, G_OC)
        lvl = 0.72 + 0.16 * (0.5 + 0.5 * math.sin(t * 4.0))
        top_y = lerp(-240, -600, lvl)
        c.rect(546, top_y, 594, -210, (226, 66, 56), 0, r=18)
        c.ell(570, -220, 44, 44, (226, 66, 56))
        c.text(570, -685, "39.2 C", 44, (255, 234, 152), "seru", stroke=4)
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=(255, 80, 40, 32))
    if not o.get("tanpa_tekstur"):
        _apply_watercolor_bg(c, wk="siang", indoor=True, strength=0.80)


def dalam_tubuh_f(c, t, o):
    # lekukan dinding jaringan lembut di pinggir bawah & atas sudut (depth framing tanpa outline hitam kaku!)
    c.set_depth(1.18)
    fc = (154, 42, 42) if o.get("demam") else (162, 64, 90)
    c.ell(-1060, 110, 290, 130, fc)
    c.ell(-1020, 96, 220, 86, terang(fc, 0.14))
    c.ell(1060, 110, 290, 130, fc)
    c.ell(1020, 96, 220, 86, terang(fc, 0.14))
    c.set_depth(1.0)


# ================================================================= KAFE COZY (GHIBLI COFFEE HOUSE)
def kafe_b(c, t, o):
    wk = waktu_of(o)
    # dinding plester krem-kayu hangat (TETAP COZY HANGAT di malam hari dengan 3 lampu gantung kuning-madu!)
    wall_c = (242, 226, 200) if wk != "malam" else (152, 130, 112)
    wood_w = (168, 120, 82) if wk != "malam" else (118, 84, 58)
    dinding(c, wall_c)
    c.rect(X0, -240, X1, 0, wood_w)
    for px in range(-1200, 1201, 90):
        c.line([(px, -240), (px, 0)], gelap(wood_w, 0.16), 1.6)
    c.rect(X0, -248, X1, -236, gelap(wood_w, 0.22), 1.8, G_OC)
    lantai(c, (186, 140, 98) if wk != "malam" else (130, 96, 68), garis=(154, 110, 74))
    # jendela kafe lebar bertirai melambai lembut + cahaya diagonal
    jendela(c, -480, -490, 440, 320, o, tirai=(238, 224, 198), scene_key="kafe", t=t)
    # papan menu kapur bingkai kayu + rak toples biji kopi di sampingnya!
    c.rect(96, -646, 546, -346, (62, 52, 58, 42), 0, r=12)
    c.rect(90, -652, 540, -352, (148, 102, 68), 2.4, G_OC, r=12)
    c.rect(106, -636, 524, -368, (48, 56, 58), 1.8, G_OC, r=6)
    c.text(315, -588, o.get("papan", "KOPI & CERITA"), 34, (252, 226, 146), "judul")
    for ly, lw in ((-524, 280), (-478, 240), (-432, 295)):
        c.line([(160, ly), (160 + lw, ly)], (232, 234, 224), 3.4)
    # rak kayu kanan penuh toples kopi & cangkir keramik + pot tanaman kecil
    for ry in (-500, -385):
        c.rect(610, ry, 1020, ry + 16, (164, 114, 74), 2.0, G_OC, r=3)
    for tx, tc in ((660, (194, 132, 82)), (740, (132, 168, 148)), (820, (226, 194, 128)), (900, (186, 102, 82))):
        c.rect(tx - 20, -552, tx + 20, -500, tc, 1.8, G_OC, r=6)
        c.rect(tx - 15, -562, tx + 15, -550, (236, 226, 206), 1.6, G_OC, r=3)
    for tx in (675, 755, 835):
        c.rect(tx - 16, -420, tx + 16, -385, (244, 238, 224), 1.8, G_OC, r=4)
    _pot_tanaman_ghibli(c, 950, -385, 0.56, sunlit=(wk != "malam"))
    # meja bar kayu + mesin espresso retro + cangkir di atas bar
    c.rect(620, -216, 1080, 0, (138, 94, 64), 2.4, G_OC)
    c.rect(604, -236, 1096, -212, (194, 144, 96), 2.4, G_OC, r=4)
    c.rect(720, -326, 860, -236, (186, 192, 196), 2.2, G_OC, r=8)
    c.rect(738, -280, 842, -242, (64, 68, 76), 1.6, G_OC, r=4)
    c.ell(765, -304, 10, 10, (226, 98, 78), 1.6, G_OC)
    c.ell(805, -304, 10, 10, (242, 206, 108), 1.6, G_OC)
    _uap_hangat(c, 790, -332, t, s=0.72, n=2)
    tanaman(c, -860, 0, 1.05)
    # 3 lampu gantung hangat berpendar (utama saat malam!)
    for lx in (-260, 180, 640):
        _lampu_gantung_ghibli(c, lx, -880, -635, (76, 92, 86), nyala=True, r_glow=340 if wk == "malam" else 190)
    _interior_warm_lighting(c, o, -480, -490, 440, 320, lamp_pts=[(-260, -600, 440), (180, -600, 480), (640, -600, 440)], t=t)
    tint(c, o, indoor=True)


def kafe_f(c, t, o):
    c.set_depth(1.18)
    c.rect(-1040, 80, -680, 118, (194, 144, 96), 2.4, G_OC, r=6)
    c.rect(-960, 118, -932, 300, (82, 84, 94), 2.2, G_OC)
    c.rect(-820, 24, -764, 80, (248, 244, 234), 2.0, G_OC, r=8)
    for sx in (-802, -782):
        c.curve([(sx, 14), (sx + 6 * math.sin(t * 3 + sx), -16), (sx - 6 * math.sin(t * 3), -44)], (255, 255, 255, 165), 3.2)
    c.set_depth(1.0)
    tint(c, o, True, indoor=True)


# ================================================================= KOTA MODERN (SHINKAI-GHIBLI CITY)
def kota_b(c, t, o):
    wk = waktu_of(o)
    langit(c, o, t=t)
    awan_set(c, o, 6, t=t, scene_key="kota")
    # skyline gedung jauh berlapis 2 kedalaman dengan kaca jendela berkilau (BUKAN blok abu polos!)
    c.set_depth(0.28)
    for i in range(-6, 7):
        bx = i * 320
        bh = 360 + (abs(i * 73) % 5) * 95
        bc = (128, 172, 206) if wk == "siang" else ((188, 134, 144) if wk == "sore" else ((154, 186, 214) if wk == "pagi" else (34, 46, 86)))
        c.rect(bx - 125, -bh, bx + 125, 0, bc)
        c.rect(bx + 42, -bh, bx + 125, 0, gelap(bc, 0.14))
        # garis lantai & jendela gedung berkilau lembut
        win_col = (255, 224, 132) if wk == "malam" else terang(bc, 0.30)
        for wy in range(-bh + 32, -32, 38):
            for wx in (bx - 96, bx - 44, bx + 8, bx + 60):
                if wk != "malam" or (wx + wy + i) % 3 != 0:
                    c.rect(wx, wy, wx + 32, wy + 18, win_col + ((165,) if wk != "malam" else ()))
    # lapisan tengah: ruko Jepang + rumah variasi + pohon kota BERBEDA SEMUA (fix bug abs(-1)==abs(1)!)
    c.set_depth(0.72)
    city_trees = ("sakura", "rimbun", "bulat_tinggi", "gugur", "cemara")
    for i in range(-4, 5):
        idx_c = i + 30
        if i % 2 == 0:
            if idx_c % 4 == 0:
                ruko_kafe(c, i * 520, 340, 330, [(244, 236, 222), (222, 236, 244), (248, 228, 220)][idx_c % 3],
                          [(56, 138, 148), (206, 92, 78), (218, 154, 72)][idx_c % 3])
            else:
                rumah(c, i * 520, 350, 275, (238, 236, 226), (112, 138, 166),
                      gaya=("modern_jp", "toko_kecil", "vila_kayu")[idx_c % 3], t=t)
        else:
            pohon(c, i * 520, 0.88 + (idx_c % 3) * 0.08, HIJAU, gaya=city_trees[idx_c % len(city_trees)], t=t)
    c.set_depth(1.0)
    # TROTOAR KOTA BERTEKSTUR UBIN + ASPAL BERTEKSTUR + ZEBRA CROSS + LAMPU LALU LINTAS!
    c.rect(X0, 0, X1, 126, (216, 212, 200), 2.2, G_OC)
    for i in range(-8, 9):
        ux = i * 180
        tone = ((224, 220, 208), (210, 206, 196), (218, 214, 202), (206, 202, 192))[(i + 40) % 4]
        c.poly([(ux, 2), (ux + 180, 2), (ux + 156, 108), (ux - 24, 108)], tone)
        c.line([(ux, 0), (ux - 24, 126)], (176, 172, 162), 1.8)
        c.line([(ux - 10, 54), (ux + 170, 54)], (184, 180, 170), 1.4)
    c.poly([(-210, 76), (-70, 76), (-80, 104), (-220, 104)], (228, 196, 96), 1.4, (176, 146, 66))
    c.rect(X0, 108, X1, 126, (178, 176, 170))
    c.rect(X0, 126, X1, 1400, (106, 110, 120))
    c.rect(X0, 126, X1, 142, (150, 148, 144))
    c.rect(X0, 142, X1, 168, G_SH + (58,))
    c.rect(X0, 265, X1, 1400, (94, 98, 108))
    rng_k = random.Random(404)
    for k in range(32):
        ax = rng_k.uniform(-1180, 1180)
        ay = rng_k.uniform(156, 390)
        c.ell(ax, ay, rng_k.uniform(28, 90), rng_k.uniform(6, 15), (86, 90, 100, 82) if k % 2 == 0 else (128, 130, 136, 60))
    for k in range(5):
        zy = 160 + k * 34
        c.poly([(-140 - k * 14, zy), (140 + k * 14, zy), (148 + k * 14, zy + 20), (-148 - k * 14, zy + 20)], (248, 246, 238, 232))
        c.ell(((k * 53) % 150) - 75, zy + 10, 26, 5, (104, 108, 118, 92))
    # tiang lampu lalu lintas khas referensi Shinkai user di kiri trotoar!
    tx = -640
    if wk != "malam":
        c.poly([(tx - 6, 4), (tx + 8, 4), (tx + 195, 195), (tx + 165, 195)], G_SH + (78,))
    c.rect(tx - 7, -560, tx + 7, 0, (124, 134, 144), 2.0, G_OC)
    c.rect(tx - 24, -420, tx + 24, -296, (72, 78, 86), 2.2, G_OC, r=8)
    c.ell(tx, -384, 15, 15, (238, 66, 62), 1.6, G_OC)
    c.ell(tx, -334, 15, 15, (64, 212, 112), 1.6, G_OC)
    glow(c, tx, -384, 34, (255, 84, 72), 75, n=6)
    glow(c, tx, -334, 34, (84, 242, 132), 75, n=6)
    # kucing kota abu-putih santai melintas pelan di trotoar
    _kucing_jalan(c, t, y_ground=32, seed=5, col=(142, 146, 154), arah=-1, speed=32.0, s=0.70)
    tint(c, o)


def kota_f(c, t, o):
    c.set_depth(1.36)
    c.rect(-1080, -680, -1010, 240, (44, 52, 68, 160))
    c.rect(1020, -680, 1090, 240, (44, 52, 68, 160))
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= PANTAI TROPIS (PERSIS REFERENSI SHINKAI-GHIBLI USER!)
def pantai_b(c, t, o):
    wk = waktu_of(o)
    langit(c, o, t=t)
    awan_set(c, o, 7, t=t, scene_key="pantai")
    # tanjung/pulau hijau berkabut biru di kiri cakrawala (persis referensi 1 & 2 user!)
    c.set_depth(0.32)
    cape_c = (78, 138, 136) if wk == "siang" else ((136, 102, 116) if wk == "sore" else ((92, 142, 146) if wk == "pagi" else (28, 48, 78)))
    c.blob([(-2200, -175), (-1480, -290), (-1080, -245), (-760, -175)], cape_c, 0, n=5)
    c.blob([(840, -175), (1260, -238), (1780, -268), (2200, -175)], mix(cape_c, (132, 184, 214), 0.35), 0, n=5)
    # laut biru-toska berlapis kaya dengan gradasi dalam -> turquoise -> buih ombak putih berkilau!
    c.set_depth(0.45)
    if wk == "sore":
        sea_far, sea_mid, sea_near = (118, 102, 142), (196, 124, 132), (242, 168, 128)
    elif wk == "malam":
        sea_far, sea_mid, sea_near = (18, 38, 82), (26, 56, 104), (38, 78, 126)
    elif wk == "pagi":
        sea_far, sea_mid, sea_near = (42, 138, 196), (62, 174, 212), (108, 210, 224)
    else:
        sea_far, sea_mid, sea_near = (16, 128, 186), (26, 158, 206), (68, 198, 218)
    c.rect(X0, -182, X1, -20, sea_far)
    c.rect(X0, -138, X1, -20, sea_mid)
    c.rect(X0, -82, X1, -20, sea_near)
    # gelombang laut painterly berlapis + buih putih halus (persis ombak referensi user!)
    for row_y, w_len, col_w, al_w in ((-160, 120, (255, 255, 255), 105), (-122, 150, (238, 252, 255), 145),
                                      (-84, 180, (255, 255, 255), 185), (-48, 210, (255, 255, 255), 215)):
        for i in range(-8, 9):
            ox = i * 280 + ((row_y * 7) % 140) + math.sin(t * 1.8 + i + row_y * 0.03) * 24
            c.ell(ox, row_y, w_len * 0.55, 5.5, col_w + (al_w,))
            c.ell(ox + 18, row_y + 4, w_len * 0.42, 3.8, gelap(sea_mid, 0.22) + (85,))
    # perahu layar mungil melaju tenang di cakrawala laut!
    _perahu_layar_jauh(c, t, y_sea=-172, speed=18.0)
    # buih ombak lembut berayun pelan di bibir pantai
    w_dy = math.sin(t * 1.5) * 6.0
    c.blob([(-2400, -24 + w_dy), (-1600, -16 - w_dy * 0.5), (-800, -28 + w_dy), (0, -18 - w_dy * 0.6),
            (800, -28 + w_dy), (1600, -16 - w_dy * 0.5), (2400, -24 + w_dy),
            (2400, 4), (-2400, 4)], (246, 252, 254, 225), 0, n=6)
    c.set_depth(1.0)
    # PASIR PANTAI BERTEKSTUR GHIBLI (pasir basah berkilau, riak angin pasir, butiran, kerang & bintang laut!)
    c.rect(X0, -16, X1, 1400, (240, 218, 174))
    # jalur pasir basah dekat ombak + kilau tipis pantulan air
    c.blob([(-2600, -16), (-1500, -12), (-400, -18), (600, -12), (1600, -18), (2600, -14),
            (2600, 26), (-2600, 26)], (210, 186, 142), 0, n=6)
    c.curve([(-2200, 2), (-1100, -4), (0, 4), (1100, -3), (2200, 2)], (255, 252, 242, 135), 4.5)
    # gelombang gundukan & riak pasir lembut (sand dunes & ripples)
    c.blob([(-2600, 96), (-1600, 62), (-520, 108), (540, 68), (1580, 112), (2600, 74),
            (2600, 320), (-2600, 320)], (232, 206, 158), 0, n=6)
    c.blob([(-2600, 210), (-1450, 174), (-320, 224), (780, 180), (1920, 228), (2600, 190),
            (2600, 1400), (-2600, 1400)], (220, 192, 142), 0, n=6)
    rng_s = random.Random(707)
    # riak angin pasir 2-nada (highlight krem + bayangan hangat tipis)
    for k in range(28):
        rx = rng_s.uniform(-1220, 1220)
        ry = rng_s.uniform(34, 340)
        rw = rng_s.uniform(55, 145)
        c.curve([(rx - rw, ry), (rx, ry - 6), (rx + rw, ry + 2)], (202, 174, 128, 125), 3.0)
        c.curve([(rx - rw * 0.85, ry - 3), (rx, ry - 9), (rx + rw * 0.85, ry - 1)], (254, 244, 214, 120), 2.4)
    # butiran pasir & kerikil pantai tersebar organik
    for k in range(85):
        px_s = rng_s.uniform(-1240, 1240)
        py_s = rng_s.uniform(18, 370)
        rr_s = rng_s.uniform(1.8, 4.4)
        sc_s = (182, 152, 108, 155) if k % 3 else (255, 246, 224, 165)
        c.ell(px_s, py_s, rr_s, rr_s * 0.65, sc_s)
    # kerang & bintang laut mungil di pasir (detail manis Ghibli!)
    for cx_s, cy_s, c_sh in ((-390, 118, (248, 232, 214)), (260, 172, (242, 204, 188)), (610, 92, (246, 236, 218))):
        c.ell(cx_s + 2, cy_s + 3, 14, 7, (164, 134, 96, 95))
        c.ell(cx_s, cy_s, 13, 8, c_sh, 1.4, (148, 118, 92))
        c.line([(cx_s, cy_s + 6), (cx_s - 6, cy_s - 5)], (178, 148, 122), 1.2)
        c.line([(cx_s, cy_s + 6), (cx_s + 6, cy_s - 5)], (178, 148, 122), 1.2)
    # 1 bintang laut kecil oranye-karang di kanan bawah
    stx, sty = 515, 205
    spts = []
    for j in range(10):
        rr = 16 if j % 2 == 0 else 7
        aa = math.radians(-90 + j * 36)
        spts.append((stx + math.cos(aa) * rr, sty + math.sin(aa) * rr * 0.62))
    c.poly(spts, (226, 118, 86), 1.4, (148, 72, 54))
    # sedikit rumput pantai di dekat pangkal pagar kayu
    _pagar_kayu(c, -1240, -12, -520, -12, n_posts=5, s=0.72)
    for gx_p in (-1040, -820, -560):
        _rumpun_ghibli(c, gx_p, 8, 0.48, (88, 148, 78), (52, 96, 62), (176, 206, 102), 2.5)
    # pohon kelapa tropis tinggi menjulang dengan 2 variasi BERBEDA (x=-636 var 0 vs x=+795 var 3 kembar!)
    pohon(c, -636, 1.15, (88, 168, 86), gaya="palem", t=t)
    pohon(c, 795, 1.08, (82, 162, 84), gaya="palem", t=t)
    # payung pantai garis-garis + bayangan jatuh biru-slate di pasir!
    ux = 370
    if wk != "malam":
        c.ell(ux + 68, 22, 155, 36, G_SH + (68,))
    c.line([(ux, 0), (ux + 24, -258)], (152, 108, 72), 9)
    c.poly([(ux - 140, -220), (ux + 24, -305), (ux + 188, -220)], (208, 86, 74), 2.4, G_OC)
    c.poly([(ux - 48, -220), (ux + 24, -305), (ux + 96, -220)], (248, 244, 232), 2.0, G_OC)
    tint(c, o)


def pantai_f(c, t, o):
    c.set_depth(1.28)
    c.ell(-1060, 200, 260, 90, (220, 192, 142))
    c.ell(1080, 210, 240, 85, (220, 192, 142))
    c.set_depth(1.0)
    tint(c, o, True)


# ================================================================= KENDARAAN SOFT GHIBLI (MOBIL, KERETA, BUS, SEPEDA)
def mobil_ghibli(c, x, y=0, s=1.0, warna=(212, 116, 98), arah=1, t=0.0):
    """Mobil retro Jepang / Ghibli membulat lucu dengan bodi 2-tone, kaca berpantulan, lampu bundar & roda berputar."""
    oc = (62, 52, 48)
    d = 1 if arah >= 0 else -1
    bob = math.sin(t * 14.0) * 1.8 * s
    yy = y + bob
    # bayangan di aspal
    c.ell(x, y + 6 * s, 148 * s, 16 * s, (38, 44, 56, 78))
    # bodi bawah & kabin atas membulat
    body = [(x - 134 * s * d, yy - 24 * s), (x - 138 * s * d, yy - 68 * s), (x - 94 * s * d, yy - 78 * s),
            (x - 66 * s * d, yy - 134 * s), (x + 48 * s * d, yy - 134 * s), (x + 86 * s * d, yy - 82 * s),
            (x + 136 * s * d, yy - 68 * s), (x + 134 * s * d, yy - 24 * s)]
    c.poly(body, warna, 3.2 * s, oc)
    # cel shadow bawah bodi & atap krem lembut (gaya 2-tone retro!)
    c.poly([(x - 132 * s * d, yy - 46 * s), (x + 132 * s * d, yy - 46 * s),
            (x + 132 * s * d, yy - 24 * s), (x - 132 * s * d, yy - 24 * s)], gelap(warna, 0.16))
    c.poly([(x - 62 * s * d, yy - 134 * s), (x + 46 * s * d, yy - 134 * s),
            (x + 56 * s * d, yy - 118 * s), (x - 70 * s * d, yy - 118 * s)], (246, 240, 224), 2.4 * s, oc)
    # jendela depan & belakang dengan pantulan kaca diagonal
    for wx0, wx1 in ((-60, -6), (6, 72)):
        c.poly([(x + wx0 * s * d, yy - 84 * s), (x + wx0 * s * d, yy - 116 * s),
                (x + wx1 * s * d, yy - 116 * s), (x + (wx1 + 6) * s * d, yy - 84 * s)], (152, 198, 222), 2.4 * s, oc)
        c.line([(x + (wx0 + 10) * s * d, yy - 88 * s), (x + (wx0 + 28) * s * d, yy - 112 * s)], (255, 255, 255, 130), 5 * s)
    # lampu depan & bemper krom
    c.ell(x + 130 * s * d, yy - 54 * s, 10 * s, 14 * s, (255, 236, 152), 2.2 * s, oc)
    c.ell(x - 130 * s * d, yy - 54 * s, 8 * s, 12 * s, (226, 88, 78), 2.0 * s, oc)
    c.rect(x - 144 * s, yy - 32 * s, x + 144 * s, yy - 20 * s, (214, 218, 222), 2.2 * s, oc, r=5)
    # 2 roda berputar
    ang = t * 9.0 * d
    for rx in (-82, 82):
        cx_w, cy_w = x + rx * s * d, y - 24 * s
        c.ell(cx_w, cy_w, 28 * s, 28 * s, (54, 58, 66), 2.8 * s, oc)
        c.ell(cx_w, cy_w, 15 * s, 15 * s, (226, 224, 214), 2.0 * s, oc)
        c.line([(cx_w - math.cos(ang) * 11 * s, cy_w - math.sin(ang) * 11 * s),
                (cx_w + math.cos(ang) * 11 * s, cy_w + math.sin(ang) * 11 * s)], oc, 2.2 * s)


def kereta_ghibli(c, x, y=0, s=1.0, gerbong=3, warna=(88, 146, 152), t=0.0):
    """Kereta api komuter/pedesaan Jepang bergaya Ghibli (rel, pantograf, garis krem-merah, jendela berjajar)."""
    oc = (58, 50, 48)
    # rel kereta & bantalan kayu di bawah
    c.rect(x - 1800 * s, y - 10 * s, x + 1800 * s, y + 6 * s, (124, 118, 114))
    for i in range(-18, 19):
        rx = x + i * 70 * s
        c.rect(rx - 14 * s, y - 4 * s, rx + 14 * s, y + 10 * s, (112, 84, 62), 1.6 * s, oc)
    c.line([(x - 1800 * s, y - 8 * s), (x + 1800 * s, y - 8 * s)], (82, 86, 96), 4.5 * s)
    car_w = 340 * s
    gap = 18 * s
    for g in range(gerbong):
        cx = x - g * (car_w + gap)
        x0, x1 = cx - car_w / 2, cx + car_w / 2
        # bodi gerbong
        c.rect(x0, y - 156 * s, x1, y - 24 * s, warna, 3.0 * s, oc, r=14 * s)
        # pita krem hangat & garis merah tipis khas kereta Jepang
        c.rect(x0 + 3 * s, y - 122 * s, x1 - 3 * s, y - 62 * s, (244, 238, 222))
        c.rect(x0 + 3 * s, y - 64 * s, x1 - 3 * s, y - 54 * s, (206, 92, 78))
        # atap abu lembut + pantograf listrik pada gerbong pertama
        c.rect(x0 + 6 * s, y - 168 * s, x1 - 6 * s, y - 154 * s, (186, 192, 198), 2.4 * s, oc, r=6 * s)
        if g == 0:
            px = cx - 40 * s
            c.line([(px - 22 * s, y - 168 * s), (px, y - 208 * s), (px + 22 * s, y - 168 * s)], oc, 3.2 * s)
            c.line([(px - 36 * s, y - 208 * s), (px + 36 * s, y - 208 * s)], oc, 4.2 * s)
            # lampu depan bulat khas kereta retro
            c.ell(x1 - 6 * s, y - 50 * s, 9 * s, 11 * s, (255, 238, 162), 2.0 * s, oc)
        # 5 jendela berjajar dengan pantulan kaca
        for j in range(5):
            jx = x0 + 26 * s + j * 60 * s
            c.rect(jx, y - 116 * s, jx + 44 * s, y - 70 * s, (148, 194, 218), 2.2 * s, oc, r=4 * s)
            c.line([(jx + 8 * s, y - 74 * s), (jx + 26 * s, y - 112 * s)], (255, 255, 255, 115), 4 * s)
        # bogie & 4 roda besi
        for bx in (x0 + 68 * s, x1 - 68 * s):
            c.rect(bx - 42 * s, y - 28 * s, bx + 42 * s, y - 14 * s, (64, 68, 78), 2.0 * s, oc, r=4 * s)
            for wx in (-24, 24):
                c.ell(bx + wx * s, y - 16 * s, 14 * s, 14 * s, (52, 56, 64), 2.0 * s, oc)
        # sambungan antar gerbong
        if g > 0:
            c.rect(x1, y - 134 * s, x1 + gap, y - 34 * s, (72, 76, 86), 2.0 * s, oc)


def bus_ghibli(c, x, y=0, s=1.0, warna=(226, 178, 92), arah=1, t=0.0):
    """Bus kota retro Ghibli (bodi 2-tone krem-kuning, jendela panjang, papan tujuan & roda berputar)."""
    oc = (60, 50, 46)
    d = 1 if arah >= 0 else -1
    yy = y + math.sin(t * 12.0) * 1.6 * s
    c.ell(x, y + 6 * s, 195 * s, 18 * s, (38, 44, 56, 75))
    c.rect(x - 186 * s, yy - 162 * s, x + 186 * s, yy - 26 * s, warna, 3.2 * s, oc, r=18 * s)
    c.rect(x - 182 * s, yy - 156 * s, x + 182 * s, yy - 86 * s, (246, 240, 224))
    c.rect(x - 182 * s, yy - 88 * s, x + 182 * s, yy - 76 * s, gelap(warna, 0.22))
    for j in range(5):
        jx = x - 162 * s + j * 66 * s
        c.rect(jx, yy - 142 * s, jx + 52 * s, yy - 94 * s, (152, 198, 222), 2.2 * s, oc, r=4 * s)
    c.ell(x + 178 * s * d, yy - 54 * s, 9 * s, 11 * s, (255, 238, 162), 2.0 * s, oc)
    for rx in (-112, 112):
        c.ell(x + rx * s, y - 26 * s, 28 * s, 28 * s, (54, 58, 66), 2.8 * s, oc)
        c.ell(x + rx * s, y - 26 * s, 14 * s, 14 * s, (226, 224, 214), 2.0 * s, oc)


def sepeda_ghibli(c, x, y=0, s=1.0, warna=(198, 118, 76)):
    """Sepeda keranjang retro Jepang (seperti referensi toko Jepang gambar 4)."""
    oc = (58, 48, 44)
    for wx in (-44, 44):
        c.ell(x + wx * s, y - 28 * s, 28 * s, 28 * s, None, 4.5 * s, oc)
        c.ell(x + wx * s, y - 28 * s, 22 * s, 22 * s, None, 1.8 * s, (186, 190, 194))
        c.ell(x + wx * s, y - 28 * s, 5 * s, 5 * s, oc)
    # rangka sepeda
    c.line([(x - 44 * s, y - 28 * s), (x - 4 * s, y - 28 * s), (x + 26 * s, y - 66 * s),
            (x - 24 * s, y - 64 * s), (x - 44 * s, y - 28 * s)], warna, 4.5 * s)
    c.line([(x + 44 * s, y - 28 * s), (x + 22 * s, y - 82 * s), (x + 10 * s, y - 86 * s)], warna, 4.5 * s)
    # sadel & keranjang depan
    c.ell(x - 26 * s, y - 70 * s, 13 * s, 5 * s, (112, 78, 54), 2.0 * s, oc)
    c.poly([(x + 26 * s, y - 76 * s), (x + 56 * s, y - 76 * s), (x + 50 * s, y - 54 * s), (x + 28 * s, y - 54 * s)],
           (168, 134, 96), 2.2 * s, oc)


# ================================================================= INTERIOR KERETA GHIBLI (500 DAYS / SPIRITED AWAY)
def _penumpang_latar(c, x, y, s=1.0, col_baju=(96, 112, 128), col_rambut=(58, 48, 44), baca=True, t=0.0, seed=0):
    """Penumpang latar bergaya lukisan Ghibli lembut (duduk tenang membaca/mendengar musik, tidak mengganggu fokus tokoh utama!)."""
    sw = math.sin(t * 2.2 + seed) * 2.2 * s
    oc_p = (74, 66, 64)
    # badan duduk santai di bangku kereta
    c.blob([
        (x - 42 * s, y - 4 * s), (x - 44 * s, y - 92 * s), (x - 22 * s, y - 122 * s),
        (x + 22 * s, y - 122 * s), (x + 44 * s, y - 92 * s), (x + 42 * s, y - 4 * s),
    ], col_baju, 2.0 * s, oc_p, n=5)
    c.blob([
        (x + 6 * s, y - 120 * s), (x + 42 * s, y - 92 * s), (x + 40 * s, y - 6 * s), (x + 8 * s, y - 6 * s),
    ], gelap(col_baju, 0.16), 0, n=4)
    # kepala sedikit menunduk + rambut lembut
    hx, hy = x + sw * 0.4, y - 158 * s
    c.ell(hx, hy - 8 * s, 38 * s, 36 * s, col_rambut, 2.0 * s, oc_p)
    c.ell(hx, hy + 4 * s, 31 * s, 28 * s, (238, 212, 192), 1.8 * s, oc_p)
    c.blob([
        (hx - 35 * s, hy - 6 * s), (hx - 28 * s, hy - 34 * s), (hx, hy - 40 * s),
        (hx + 28 * s, hy - 34 * s), (hx + 35 * s, hy - 6 * s),
        (hx + 16 * s, hy - 14 * s), (hx - 16 * s, hy - 14 * s),
    ], col_rambut, 1.8 * s, oc_p, n=4)
    # mata tenang menunduk
    for sg in (-1, 1):
        c.curve([(hx + sg * 12 * s - 5 * s, hy + 6 * s), (hx + sg * 12 * s, hy + 10 * s), (hx + sg * 12 * s + 5 * s, hy + 6 * s)], oc_p, 1.8 * s)
    if baca:
        # buku terbuka di pangkuan
        c.poly([(x - 36 * s, y - 58 * s), (x, y - 48 * s), (x + 36 * s, y - 58 * s),
                (x + 32 * s, y - 18 * s), (x, y - 10 * s), (x - 32 * s, y - 18 * s)], (242, 234, 216), 1.8 * s, oc_p)
        c.line([(x, y - 48 * s), (x, y - 10 * s)], (152, 138, 122), 1.8 * s)
    else:
        # headphone retro kecil di telinga
        c.curve(arc_pts(hx, hy - 8 * s, 39 * s, 37 * s, 195, 345, 14), (82, 76, 78), 4.0 * s)
        c.ell(hx - 35 * s, hy + 2 * s, 7 * s, 13 * s, (108, 98, 94), 1.5 * s, oc_p)
        c.ell(hx + 35 * s, hy + 2 * s, 7 * s, 13 * s, (108, 98, 94), 1.5 * s, oc_p)


def _kursi_amtrak(c, cx, y_bot, w=290, h=420, hangat=0.5, sun_side=0.0):
    """Kursi kereta Amtrak tinggi biru-navy bermotif ombak + sandaran kepala biru muda (persis referensi 500 Days of Summer, gaya cat air Ghibli!)."""
    seat_navy = mix((52, 66, 94), (66, 72, 98), hangat)
    seat_hi = mix((84, 102, 134), (138, 128, 144), hangat)
    head_c = mix((74, 104, 138), (94, 118, 152), hangat)
    oc_s = (52, 44, 42)
    hw = w * 0.5
    y_top = y_bot - h
    # Badan sandaran kursi tinggi melengkung empuk
    pts = [
        (cx - hw, y_bot),
        (cx - hw * 1.02, y_top + 86),
        (cx - hw * 0.84, y_top + 18),
        (cx - hw * 0.35, y_top),
        (cx + hw * 0.35, y_top),
        (cx + hw * 0.84, y_top + 18),
        (cx + hw * 1.02, y_top + 86),
        (cx + hw, y_bot),
    ]
    c.blob(pts, seat_navy, 2.6, oc_s, n=5)
    # Sorotan sinar matahari lembut di sisi kursi bila sun_side > 0
    if sun_side > 0.05:
        sun_col = mix((198, 214, 232), (255, 224, 168), hangat)
        c.blob([
            (cx + hw * 0.15, y_top + 14), (cx + hw * 0.82, y_top + 22),
            (cx + hw * 0.98, y_top + 110), (cx + hw * 0.96, y_bot - 10),
            (cx + hw * 0.10, y_bot - 10),
        ], sun_col + (int(82 * sun_side),), 0, n=4)
    # Motif ombak halus kain kursi Amtrak (tipis & organik Ghibli, tidak ramai!)
    pat_c = seat_hi + (90,)
    for row in range(6):
        ry = y_top + 95 + row * 46
        if ry > y_bot - 22:
            break
        for col_i in range(-3, 4):
            rx = cx + col_i * 36 + (18 if row % 2 else 0)
            if abs(rx - cx) < hw - 26:
                c.curve([(rx - 14, ry + 5), (rx, ry - 4), (rx + 14, ry + 5)], pat_c, 1.8)
    # Strip kain sandaran kepala vertikal + bantal headrest biru lembut di atas!
    c.rect(cx - hw * 0.34, y_top + 4, cx + hw * 0.34, y_top + 185, head_c, 2.0, oc_s, r=8)
    c.rect(cx - hw * 0.44, y_top + 46, cx + hw * 0.44, y_top + 124, terang(head_c, 0.08), 2.2, oc_s, r=18)
    c.rect(cx - hw * 0.38, y_top + 106, cx + hw * 0.38, y_top + 122, gelap(head_c, 0.16), 0, None, r=6)
    c.blob(pts, None, 2.6, oc_s, n=5)


def kereta_dalam_b(c, t, o):
    """Interior kereta komuter/Amtrak bergaya Studio Ghibli — mendukung 3 sudut POV film 500 Days of Summer:
    - sudut='tom'    : menghadap kursi penumpang Amtrak biru-navy bermotif + jendela kiri-belakang (persis Referensi 1!)
    - sudut='summer' : POV lorong kereta 1-titik hilang, jendela sisi kiri, rak bagasi+lampu baca, kursi berjajar (persis Referensi 2!)
    - sudut='berdua' : menghadap sepasang kursi penumpang Amtrak berdampingan + lorong & penumpang baris belakang!
    """
    hangat = clamp(float(o.get("hangat", 0.5)), 0.0, 1.0)
    sudut = str(o.get("sudut", "berdua")).lower()
    rail_jolt = math.sin(t * 7.8) * 1.2 + math.sin(t * 2.6) * 1.8

    # Warna kabin & langit dingin (0.0) -> hangat sore keemasan (1.0)
    s_top = mix((116, 148, 178), (92, 142, 196), hangat)
    s_bot = mix((208, 220, 228), (254, 212, 152), hangat)
    wall_c = mix((198, 204, 210), (236, 220, 194), hangat)
    ceil_c = mix((216, 220, 224), (244, 232, 210), hangat)
    trim_c = mix((126, 134, 144), (156, 128, 98), hangat)
    c_cols = _cloud_colors("sore" if hangat > 0.72 else ("pagi" if hangat < 0.25 else "siang"))
    hill_c = mix((116, 138, 156), (138, 148, 122), hangat)
    tree_c = mix((84, 118, 98), (112, 156, 88), hangat)

    # 1) PEMANDANGAN LUAR JENDELA BERGERAK (parallax 3 lapis!)
    c.set_depth(0.28)
    c.gradient(s_top, s_bot, 0.0, 0.78)
    for cx0, cy0, sc_c in ((-950, -590, 1.05), (-180, -615, 1.18), (620, -575, 1.00), (1380, -605, 1.12)):
        cx_ = ((cx0 - t * 42.0 + 2200) % 4400) - 2200
        _paint_cloud_puffs(c, cx_, cy0, sc_c, [(-64, 14, 58, 28), (6, -8, 72, 40), (76, 12, 54, 26)], c_cols)
    c.set_depth(0.45)
    for i in range(-4, 6):
        hx = ((i * 580 - t * 125.0 + 2600) % 5200) - 2600
        c.blob([(hx - 340, -160), (hx - 120, -340 - (abs(i) % 3) * 38), (hx + 160, -290), (hx + 340, -160)], hill_c, 0, n=4)
    c.set_depth(0.62)
    for i in range(-5, 7):
        tx = ((i * 410 - t * 410.0 + 2400) % 4800) - 2400
        c.ell(tx, -245, 96, 84, gelap(tree_c, 0.16))
        c.ell(tx - 12, -264, 76, 62, tree_c)
        if i % 2 == 0:
            px_e = ((i * 680 - t * 560.0 + 2400) % 4800) - 2400
            c.rect(px_e - 8, -790, px_e + 8, -160, (78, 84, 94, 165))

    c.set_depth(1.0)
    if sudut == "pintu":
        # ================= SUDUT 0: BINGKAI PINTU KERETA GHIBLI VERTIKAL 9:16 (persis referensi anime hangat!) =================
        # Dinding kabin krem-oker hangat di sekitar jendela kotak tengah (dingin krem-kelabu -> oker senja keemasan!)
        cab_wall = mix((198, 202, 204), (232, 198, 138), hangat)
        cab_ceil = mix((212, 216, 218), (242, 216, 162), hangat)
        cab_trim = mix((142, 148, 154), (176, 140, 88), hangat)
        # Bangku merah-terakota khas kereta Jepang/Ghibli (teduh dingin -> merah hangat menyala!)
        bench_c = mix((148, 86, 76), (194, 82, 54), hangat)
        bench_top = mix((168, 102, 90), (218, 104, 68), hangat)
        fl_c = mix((134, 138, 144), (174, 142, 102), hangat)
        oc_k = (48, 36, 30)

        # Dinding sekeliling jendela kotak lebar tengah (jendela tinggi elegan y=-840..-355!)
        c.rect(-1200, -1450, 1200, -840, cab_ceil)
        c.rect(-1200, -844, -262, -350, cab_wall)
        c.rect(262, -844, 1200, -350, cab_wall)
        c.rect(-1200, -355, 1200, 0, cab_wall)

        # Panel plafon atas & garis trim horizontal
        c.rect(-340, -1120, 340, -1010, terang(cab_ceil, 0.06), 2.0, oc_k)
        c.line([(-520, -965), (520, -965)], oc_k, 2.0)
        c.line([(-520, -952), (520, -952)], gelap(cab_wall, 0.16), 2.2)

        # Bayangan diagonal halus dari rak bagasi & bingkai jendela di dinding krem kiri & kanan!
        sh_w = gelap(cab_wall, 0.18) + (110,)
        for row_s in range(4):
            ys_r = -845 + row_s * 18
            c.line([(-460, ys_r), (-268, ys_r + 12)], sh_w, 5.5)
            c.line([(268, ys_r + 12), (460, ys_r + 24)], sh_w, 5.5)

        # 2 bingkai poster/papan iklan retro tipis di dinding kiri & kanan jendela
        c.rect(-455, -805, -305, -670, terang(cab_wall, 0.08), 2.0, oc_k, r=4)
        c.rect(305, -805, 455, -670, terang(cab_wall, 0.08), 2.0, oc_k, r=4)

        # Kusen jendela kotak ganda membulat + kait pegangan di puncak jendela + kilau hangat kaca!
        glass_tint = mix((232, 240, 246, 52), (255, 240, 188, 108), hangat)
        c.rect(-262, -840, 262, -355, glass_tint)
        c.poly([(-254, -362), (-120, -362), (45, -834), (-90, -834)], (255, 255, 242, 42))
        def _rr_pts(x0_, y0_, x1_, y1_, r_):
            return (
                arc_pts(x0_ + r_, y0_ + r_, r_, r_, 180, 270, 6)
                + arc_pts(x1_ - r_, y0_ + r_, r_, r_, 270, 360, 6)
                + arc_pts(x1_ - r_, y1_ - r_, r_, r_, 0, 90, 6)
                + arc_pts(x0_ + r_, y1_ - r_, r_, r_, 90, 180, 6)
            )
        c.poly(_rr_pts(-266, -844, 266, -352, 14), None, 3.2, oc_k)
        c.poly(_rr_pts(-254, -832, 254, -364, 10), None, 2.2, oc_k)
        c.rect(-36, -844, 36, -820, cab_ceil, 2.2, oc_k, r=4)
        c.line([(-480, -350), (480, -350)], oc_k, 2.4)

        # Rak bagasi logam horizontal di atas jendela + siku penopang kiri & kanan!
        for yr_b in (-898, -886, -874):
            c.line([(-420, yr_b), (420, yr_b)], (152, 146, 134), 3.6)
            c.line([(-420, yr_b - 2), (420, yr_b - 2)], oc_k, 1.4)
        for xb_s, sgn_b in ((-365, -1), (365, 1)):
            c.poly([(xb_s, -872), (xb_s + sgn_b * 28, -908), (xb_s + sgn_b * 18, -922), (xb_s - sgn_b * 4, -876)],
                   cab_ceil, 2.2, oc_k)

        # 4 tali pegangan melingkar (hand straps) persis referensi — berayun sangat pelan!
        for i_h, sx_h in enumerate((-235, -78, 78, 235)):
            ang_s = math.sin(t * 2.4 + i_h * 0.45) * 0.08
            bx_s = sx_h + math.sin(ang_s) * 145
            by_s = -1045 + math.cos(ang_s) * 145
            c.line([(sx_h, -1060), (bx_s, by_s)], oc_k, 9.5)
            c.line([(sx_h, -1060), (bx_s, by_s)], (92, 82, 72), 5.0)
            c.rect(bx_s - 8, by_s - 28, bx_s + 8, by_s + 2, cab_ceil, 2.0, oc_k, r=3)
            c.curve(arc_pts(bx_s, by_s + 22, 23, 23, 0, 360, 22), oc_k, 9.5)
            c.curve(arc_pts(bx_s, by_s + 22, 23, 23, 0, 360, 22), (236, 224, 198), 4.8)

        # Lantai kabin hangat
        lantai(c, fl_c, garis=gelap(fl_c, 0.18))

        # Bangku panjang empuk merah-terakota Ghibli (dudukan tinggi di y=-168..-116 agar kaki panjang menjuntai di depan kisi-kisi!)
        c.rect(-480, -330, 480, -162, bench_c, 2.8, oc_k, r=18)
        c.rect(-474, -324, 474, -296, terang(bench_c, 0.12))
        c.rect(-474, -182, 474, -162, gelap(bench_c, 0.18))
        for sj_x in (-240, 0, 240):
            c.line([(sj_x, -324), (sj_x, -166)], gelap(bench_c, 0.28), 2.2)
            c.line([(sj_x, -160), (sj_x, -118)], gelap(bench_c, 0.28), 2.2)
        c.rect(-485, -166, 485, -116, bench_top, 2.8, oc_k, r=14)
        c.rect(-478, -132, 478, -118, gelap(bench_c, 0.22))
        c.rect(-480, -116, 480, 0, mix((116, 114, 110), (146, 122, 86), hangat), 2.6, oc_k)
        for gx0, gx1 in ((-325, -18), (18, 325)):
            c.rect(gx0, -100, gx1, -16, gelap(fl_c, 0.30), 2.0, oc_k, r=4)
            for row_g in range(5):
                gy = -90 + row_g * 15
                for col_g in range(gx0 + 12, gx1 - 14, 22):
                    c.rect(col_g, gy, col_g + 13, gy + 8, (44, 38, 34))

        # 2 tiang pegangan logam vertikal rapi kiri & kanan
        for px_p in (-288, 296):
            c.rect(px_p - 6, -892, px_p + 6, -116, (186, 180, 166), 2.2, oc_k)
            c.line([(px_p - 2, -890), (px_p - 2, -118)], (242, 236, 222), 2.2)
        c.curve([(-288, -116), (-288, -96), (-268, -96)], oc_k, 8.0)
        c.curve([(-288, -116), (-288, -96), (-268, -96)], (186, 180, 166), 4.0)
        c.curve([(296, -116), (296, -96), (276, -96)], oc_k, 8.0)
        c.curve([(296, -116), (296, -96), (276, -96)], (186, 180, 166), 4.0)

    elif sudut == "summer":
        # ================= SUDUT 2: POV TOM MELIHAT KE LORONG KERETA & SUMMER (persis Referensi 2!) =================
        # Dinding kanan lorong & ujung belakang gerbong (perspektif 1-titik hilang di (120, -360)!)
        vp_x, vp_y = 115, -355
        # Plafon perspektif mengecil ke belakang
        c.poly([(-1200, -900), (1200, -900), (1200, -495), (360, -460), (-420, -460), (-1200, -560)], ceil_c, 2.2, G_OC)
        # Dinding kanan kabin (sisi kanan lorong, teduh hangat)
        c.poly([(360, -460), (1200, -520), (1200, 120), (360, -95)], gelap(wall_c, 0.14), 2.2, G_OC)
        # Dinding ujung belakang gerbong + pintu kaca penghubung gerbong
        c.rect(-140, -465, 365, -90, mix((112, 122, 134), (138, 122, 108), hangat), 2.2, G_OC)
        c.rect(48, -430, 210, -110, mix((66, 78, 94), (82, 74, 72), hangat), 2.2, G_OC, r=6)
        c.rect(74, -408, 184, -275, mix((128, 152, 174), (188, 164, 136), hangat), 2.0, G_OC, r=8)

        # Dinding kiri berjendela perspektif (jendela besar di kiri depan -> mengecil ke belakang!)
        # Bingkai atas & bawah dinding kiri miring mengikuti garis perspektif
        c.poly([(-1200, -560), (-140, -465), (-140, -438), (-1200, -518)], wall_c, 2.0, G_OC)
        c.poly([(-1200, -210), (-140, -255), (-140, 20), (-1200, 120)], wall_c, 2.0, G_OC)
        # Pilar pemisah antar-jendela sisi kiri mengecil ke belakang
        for px_l, pw_l, yt_l, yb_l in ((-920, 42, -520, -215), (-520, 32, -488, -234), (-260, 22, -468, -248)):
            c.rect(px_l - pw_l, yt_l, px_l + pw_l, yb_l, wall_c, 2.2, G_OC)
            c.rect(px_l + pw_l * 0.25, yt_l + 4, px_l + pw_l - 3, yb_l - 4, gelap(wall_c, 0.12))
        # Kilau jendela kiri
        c.poly([(-870, -220), (-780, -225), (-680, -496), (-770, -502)], (255, 255, 255, 28))
        c.poly([(-480, -238), (-420, -242), (-360, -474), (-420, -478)], (255, 255, 255, 24))

        # Rak bagasi overhead perspektif di kiri-atas & kanan-atas + lampu baca kecil berjajar!
        c.poly([(-1200, -760), (-140, -508), (-140, -470), (-1200, -640)], terang(wall_c, 0.06), 2.2, G_OC)
        c.line([(-1200, -640), (-140, -470)], gelap(trim_c, 0.18), 4.0)
        c.poly([(1200, -740), (360, -508), (360, -472), (1200, -630)], wall_c, 2.2, G_OC)
        for lx_r, ly_r, sr_l in ((-840, -645, 1.0), (-510, -578, 0.78), (-285, -528, 0.58)):
            c.rect(lx_r - 58 * sr_l, ly_r - 18 * sr_l, lx_r + 58 * sr_l, ly_r + 12 * sr_l, trim_c, 1.8, G_OC, r=6)
            c.ell(lx_r - 22 * sr_l, ly_r + 4 * sr_l, 11 * sr_l, 7 * sr_l, (72, 68, 66), 1.4, G_OC)
            c.ell(lx_r + 22 * sr_l, ly_r + 4 * sr_l, 11 * sr_l, 7 * sr_l, (72, 68, 66), 1.4, G_OC)
            glow(c, lx_r, ly_r + 28 * sr_l, 120 * sr_l, mix((232, 240, 248), (255, 224, 152), hangat), int(26 + 32 * hangat), n=6)

        # Lantai lorong perspektif
        lantai(c, mix((134, 140, 148), (154, 134, 116), hangat), garis=gelap(trim_c, 0.22))

        # Baris kursi Amtrak biru-navy berjajar mengecil ke belakang di kiri & kanan lorong!
        for bx_c, by_c, bw_c, bh_c in (
            (-265, -80, 155, 220), (-115, -82, 145, 215), (410, -82, 150, 215),
            (-420, -40, 200, 275), (-195, -42, 190, 270), (505, -40, 205, 275),
            (-640, 18, 260, 340), (-330, 18, 250, 335), (650, 18, 260, 340),
        ):
            _kursi_amtrak(c, bx_c, by_c, w=bw_c, h=bh_c, hangat=hangat, sun_side=0.35 if bx_c < 0 else 0.0)
        # Penumpang kecil mengintip tenang di baris kursi belakang kiri (persis Referensi 2!)
        if o.get("penumpang", True):
            _penumpang_latar(c, -225, -135 + rail_jolt * 0.3, 0.62, (124, 112, 98), (196, 162, 108), baca=True, t=t, seed=2)
            _penumpang_latar(c, 530, -108 + rail_jolt * 0.3, 0.68, (88, 98, 112), (56, 46, 42), baca=False, t=t, seed=5)
        # Sandaran kursi di sebelah depan Summer (tempat tangan Summer bersandar santai!)
        _kursi_amtrak(c, -110, 145, w=320, h=380, hangat=hangat, sun_side=0.25)

    elif sudut == "tom":
        # ================= SUDUT 1: POV KE TOM DUDUK DI KURSI AMTRAK (persis Referensi 1!) =================
        # Plafon & bingkai jendela besar di belakang-atas
        c.rect(X0, -1100, X1, -660, ceil_c)
        c.rect(X0, -672, X1, -646, trim_c, 2.0, G_OC)
        c.rect(X0, -255, X1, 0, wall_c)
        c.rect(X0, -264, X1, -244, trim_c, 2.0, G_OC)
        # Pilar jendela perspektif di belakang kursi Tom
        for px in (-820, -125, 560):
            c.rect(px - 26, -660, px + 26, -250, wall_c, 2.2, G_OC)
            c.rect(px + 8, -654, px + 22, -254, gelap(wall_c, 0.14))
        c.poly([(-60, -256), (90, -256), (260, -646), (110, -646)], (255, 255, 255, 26))
        lantai(c, mix((136, 142, 150), (166, 140, 114), hangat), garis=gelap(trim_c, 0.22))

        # Baris kursi belakang + 1 penumpang pria di kiri belakang (persis Referensi 1!)
        _kursi_amtrak(c, -560, -40, w=280, h=395, hangat=hangat, sun_side=0.10)
        _kursi_amtrak(c, -265, -45, w=260, h=370, hangat=hangat, sun_side=0.15)
        if o.get("penumpang", True):
            _penumpang_latar(c, -560, -115 + rail_jolt * 0.4, 1.08, (186, 184, 178), (64, 50, 44), baca=True, t=t, seed=1)

        # Sepasang kursi Amtrak utama di depan (Tom duduk di kursi kiri x=-125; kursi kanan kosong disorot matahari hangat!)
        _kursi_amtrak(c, -125, 110, w=340, h=490, hangat=hangat, sun_side=0.18)
        _kursi_amtrak(c, 255, 110, w=340, h=490, hangat=hangat, sun_side=0.85)

    else:
        # ================= SUDUT 3: TWO-SHOT BERDUA (2 kursi Amtrak berdampingan + lorong & penumpang belakang!) =================
        c.rect(X0, -1100, X1, -645, ceil_c)
        c.rect(X0, -660, X1, -634, trim_c, 2.0, G_OC)
        c.rect(X0, -265, X1, 0, wall_c)
        c.rect(X0, -274, X1, -254, trim_c, 2.0, G_OC)
        for px in (-920, -455, 455, 920):
            c.rect(px - 34, -650, px + 34, -260, wall_c, 2.2, G_OC)
            c.rect(px + 12, -644, px + 30, -264, gelap(wall_c, 0.12))
        for wx0 in (-860, -390, 520):
            c.poly([(wx0, -264), (wx0 + 84, -264), (wx0 + 195, -634), (wx0 + 110, -634)], (255, 255, 255, 22))
        # Rak bagasi & lampu plafon hangat
        c.line([(-1200, -700), (1200, -700)], (140, 146, 154), 5.0)
        for lx in (-460, 0, 460):
            c.rect(lx - 86, -805, lx + 86, -784, (254, 248, 226), 1.8, G_OC, r=8)
            glow(c, lx, -768, 240, mix((218, 234, 248), (255, 220, 144), hangat), int(30 + 36 * hangat), n=7)
        lantai(c, mix((138, 144, 152), (168, 142, 114), hangat), garis=gelap(trim_c, 0.22))

        # Penumpang latar duduk di kursi kanan & kiri baris belakang
        _kursi_amtrak(c, -665, -20, w=250, h=350, hangat=hangat, sun_side=0.15)
        _kursi_amtrak(c, 675, -20, w=250, h=350, hangat=hangat, sun_side=0.20)
        if o.get("penumpang", True):
            _penumpang_latar(c, -665, -88 + rail_jolt * 0.4, 0.96, (94, 110, 126), (56, 46, 42), baca=True, t=t, seed=1)
            _penumpang_latar(c, 675, -88 + rail_jolt * 0.4, 0.94, (132, 116, 102), (68, 52, 44), baca=False, t=t, seed=3)

        # Sepasang kursi Amtrak utama tempat Tom (kiri x=-185) & Summer (kanan x=+185) duduk berdampingan!
        _kursi_amtrak(c, -185, 65, w=315, h=440, hangat=hangat, sun_side=0.22)
        _kursi_amtrak(c, 185, 65, w=315, h=440, hangat=hangat, sun_side=0.65)
        # Dudukan bawah kursi menyatu rapi
        c.rect(-360, -108, 360, -56, mix((62, 78, 108), (76, 82, 112), hangat), 2.2, G_OC, r=10)
        c.rect(-340, -56, 340, 0, gelap(wall_c, 0.16), 2.0, G_OC)

    # 3) BERKAS CAHAYA MATAHARI MENYAPU MELALUI JENDELA
    sweep_phase = (t * 0.40) % 1.0
    sweep_env = math.sin(sweep_phase * math.pi)
    if sweep_env > 0.05:
        sun_col = mix((226, 238, 250), (255, 224, 148), hangat)
        s_al = int((18 + 40 * hangat) * (0.45 + 0.55 * sweep_env))
        sx_sh = lerp(520, -680, sweep_phase)
        c.poly([(sx_sh - 160, -640), (sx_sh + 190, -640), (sx_sh - 260, 240), (sx_sh - 610, 240)], sun_col + (s_al,))
        c.poly([(sx_sh + 260, -640), (sx_sh + 460, -640), (sx_sh + 10, 240), (sx_sh - 190, 240)], sun_col + (int(s_al * 0.65),))

    # Nuansa warna dingin->hangat bertahap sesuai parameter `hangat`
    if hangat < 0.45:
        cool_a = int((0.45 - hangat) * 52)
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=(110, 144, 186, cool_a))
    elif hangat > 0.55:
        warm_a = int((hangat - 0.55) * 48)
        c.d.rectangle([0, 0, c.im.width, c.im.height], fill=(255, 182, 104, warm_a))

    if not o.get("tanpa_tekstur"):
        _apply_watercolor_bg(c, wk="sore" if hangat > 0.7 else "siang", indoor=True, strength=0.90)


def kereta_dalam_f(c, t, o):
    """Lapisan foreground POV kereta: sapuan cahaya jendela melewati wajah + siluet POV over-the-shoulder/kursi depan!"""
    hangat = clamp(float(o.get("hangat", 0.5)), 0.0, 1.0)
    sudut = str(o.get("sudut", "berdua")).lower()
    # Sapuan tipis cahaya matahari melewati sisi wajah Tom & Summer saat kereta bergerak!
    sweep_phase = (t * 0.40) % 1.0
    sweep_env = math.sin(sweep_phase * math.pi)
    if sweep_env > 0.12:
        sun_col = mix((230, 242, 255), (255, 228, 152), hangat)
        s_al = int((12 + 24 * hangat) * sweep_env)
        sx_sh = lerp(520, -680, sweep_phase)
        c.poly([(sx_sh - 120, -630), (sx_sh + 140, -630), (sx_sh - 280, 220), (sx_sh - 540, 220)], sun_col + (s_al,))
    c.set_depth(1.24)
    if sudut == "pintu":
        # BINGKAI PINTU KERETA BIRU-SLATE TUA (persis referensi anime Ghibli! Membingkai indah saat wide/medium, otomatis minggir saat close-up!)
        c.set_depth(1.05)
        door_c = mix((58, 86, 108), (62, 82, 98), hangat)
        door_dark = gelap(door_c, 0.24)
        trim_d = mix((204, 206, 204), (232, 206, 158), hangat)
        oc_d = (34, 30, 30)
        # Panel pintu kiri, kanan, dan atas mengelilingi bukaan pintu x=-356..356, y=-1025..650
        c.rect(-1400, -1650, -356, 700, door_c)
        c.rect(356, -1650, 1400, 700, door_c)
        c.rect(-1400, -1650, 1400, -1025, door_c)
        c.rect(-1400, -145, -356, 40, door_dark)
        c.rect(356, -145, 1400, 40, door_dark)
        c.line([(-1400, -1120), (1400, -1120)], oc_d, 3.0)
        c.rect(-620, -900, -455, -550, gelap(door_c, 0.16), 3.0, oc_d, r=18)
        c.rect(455, -900, 620, -550, gelap(door_c, 0.16), 3.0, oc_d, r=18)
        for hx_d in (-404, 404):
            c.rect(hx_d - 12, -572, hx_d + 12, -534, (132, 144, 152), 2.4, oc_d, r=4)
            c.rect(hx_d - 12, -168, hx_d + 12, -130, (132, 144, 152), 2.4, oc_d, r=4)
            c.rect(hx_d - 7, -552, hx_d + 7, -150, (158, 168, 174), 2.4, oc_d, r=5)
            c.line([(hx_d - 2, -548), (hx_d - 2, -154)], (214, 222, 226), 2.0)
        def _door_arch(x0_, y0_, x1_, y1_, r_):
            return (
                [(x0_, y1_)]
                + arc_pts(x0_ + r_, y0_ + r_, r_, r_, 180, 270, 8)
                + arc_pts(x1_ - r_, y0_ + r_, r_, r_, 270, 360, 8)
                + [(x1_, y1_)]
            )
        c.poly([(-370, -1038), (-314, -1038)] + arc_pts(-314, -982, 56, 56, 270, 180, 8), door_c)
        c.poly([(370, -1038), (314, -1038)] + arc_pts(314, -982, 56, 56, 270, 360, 8), door_c)
        c.line(_door_arch(-364, -1032, 364, 650, 48), trim_d, 13.0)
        c.line(_door_arch(-370, -1038, 370, 656, 52), oc_d, 3.2)
        c.line(_door_arch(-356, -1024, 356, 642, 42), oc_d, 3.2)
    elif sudut == "tom":
        # Siluet tipis lengan/bahu foreground di pinggir kanan (over-the-shoulder persis Referensi 1!)
        fg_c = mix((74, 58, 48, 155), (96, 68, 50, 150), hangat)
        c.blob([(430, -560), (620, -560), (660, 220), (385, 220)], fg_c, 0, n=4)
    elif sudut == "summer":
        # Siluet puncak sandaran kursi & kepala Tom di sudut kiri bawah (POV Tom duduk persis Referensi 2!)
        fg_seat = mix((36, 46, 68, 185), (46, 48, 66, 180), hangat)
        c.blob([(-580, 180), (-560, -110), (-360, -145), (-195, -90), (-165, 180)], fg_seat, 0, n=5)
        c.ell(-420, -142, 95, 58, (34, 24, 20, 190))
    else:
        edge_c = mix((72, 82, 96, 105), (96, 76, 66, 95), hangat)
        c.rect(-1140, -900, -1060, 320, edge_c)
        c.rect(1060, -900, 1140, 320, edge_c)
    c.set_depth(1.0)


SET = {
    "kamar": (kamar_b, kamar_f), "sekolah_luar": (sekolah_luar_b, sekolah_luar_f), "sekolah": (sekolah_luar_b, sekolah_luar_f),
    "taman": (taman_b, taman_f), "kelas": (kelas_b, kelas_f), "ruang_belajar": (ruang_belajar_b, ruang_belajar_f),
    "ruang_tamu": (ruang_tamu_b, ruang_tamu_f), "jalan": (jalan_b, jalan_f), "kantin": (kantin_b, kantin_f),
    "lapangan": (lapangan_b, lapangan_f), "rumah_depan": (rumah_depan_b, rumah_depan_f), "meja_makan": (meja_makan_b, meja_makan_f),
    "padang": (padang_b, padang_f), "polos": (polos_b, polos_f),
    "ruang_otak": (ruang_otak_b, ruang_otak_f), "dalam_tubuh": (dalam_tubuh_b, dalam_tubuh_f),
    "kafe": (kafe_b, kafe_f), "kota": (kota_b, kota_f), "pantai": (pantai_b, pantai_f),
    "kereta_dalam": (kereta_dalam_b, kereta_dalam_f),
}
ALIAS = {"kamar_tidur": "kamar", "gerbang_sekolah": "sekolah_luar", "halaman_sekolah": "taman", "dapur": "meja_makan",
         "ruang_keluarga": "ruang_tamu", "meja_belajar": "ruang_belajar", "komplek": "jalan", "kampung": "jalan", "luar": "padang",
         "kedai": "kafe", "coffee": "kafe", "perkotaan": "kota", "laut": "pantai",
         "kereta": "kereta_dalam", "interior_kereta": "kereta_dalam", "train": "kereta_dalam"}


def set_of(name):
    name = ALIAS.get(name, name)
    return SET.get(name, SET["polos"])
