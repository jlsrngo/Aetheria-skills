# -*- coding: utf-8 -*-
"""
benda.py - properti 3D Pop-Up Paper Craft berlapis detail (pintu lengkung, kartu pita,
           HP kertas bertumpuk, menara jam, jam weker, pensil, dan ikon kertas).
"""
import os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from paper import (
    OUT, KERTAS_TEPI, PUTIH, KRIM, HITAM, KORAL, MERAH, MERAH_TUA,
    BIRU, BIRU_TUA, BIRU_MUDA, MINT, MINT_MUDA, TEAL, PINK, SALMON, KUNING, KUNING_MUDA,
    ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA, ABU, ABU_TUA,
    clamp, gelap, terang, mix, e_spring, e_io, euler_mat, font,
    circle_2d, rrect_2d, coat_2d, arch_2d, star_2d,
)


def _serif_font(size, italic=False, bold=False):
    cands = (
        ["C:/Windows/Fonts/georgiai.ttf", "C:/Windows/Fonts/timesi.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"]
        if italic else
        ["C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/timesbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"]
        if bold else
        ["C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
    )
    for p in cands:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, max(8, int(size)))
            except Exception:
                pass
    return font("judul", size)


def _plaque_texture(teks_besar="5", teks_kecil="MENIT", accent=MERAH):
    """Plakat kartu pita gading bergaya editorial serif ala '5 MENIT', '1 JAM', 'SATU PINTU lagi'."""
    W, H = 460, 140
    im = Image.new("RGBA", (W, H), (250, 245, 236, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([4, 4, W - 5, H - 5], outline=(228, 216, 198, 255), width=2)
    tb = str(teks_besar or "")
    tk = str(teks_kecil or "")
    if tb and tk:
        is_num = tb.strip().isdigit()
        is_lagi = tk.strip().lower() == "lagi"
        s1 = 100 if is_num else 38
        s2 = 48 if is_num else 58
        c1 = accent if is_num else OUT
        c2 = OUT if is_num else accent
        gap = 18
        while s1 > 18:
            f1 = _serif_font(s1, italic=False, bold=True) if is_num else font("teks", s1)
            f2 = _serif_font(s2, italic=True, bold=False) if is_lagi else font("teks", s2)
            w1 = d.textlength(tb, font=f1)
            w2 = d.textlength(tk, font=f2)
            if w1 + gap + w2 <= W - 44:
                break
            s1 = int(s1 * 0.88)
            s2 = max(18, int(s2 * 0.88))
        x0 = (W - (w1 + gap + w2)) * 0.5
        d.text((x0 + w1 * 0.5, H * 0.48), tb, font=f1, fill=c1 + (255,), anchor="mm")
        d.text((x0 + w1 + gap + w2 * 0.5, H * (0.56 if is_num else 0.48)), tk, font=f2, fill=c2 + (255,), anchor="mm")
    else:
        txt = tb or tk
        sz = 42
        while sz > 18 and d.textlength(txt, font=font("judul", sz)) > W - 44:
            sz -= 3
        d.text((W * 0.5, H * 0.5), txt, font=font("judul", sz), fill=OUT + (255,), anchor="mm")
    return im


def _world_quad(pos, mat, local_pts):
    o = np.array(pos, dtype=np.float32)
    return [tuple((o + mat @ np.array(p, dtype=np.float32)).tolist()) for p in local_pts]


def draw_prop(sc, jenis, pos, rot=(0.0, 0.0, 0.0), s=1.0, t=0.0, **opsi):
    mat = euler_mat(*rot)

    if jenis == "pintu_kertas":
        col_frame = opsi.get("warna_bingkai", BIRU)
        col_door = opsi.get("warna_pintu", KORAL)
        w = float(opsi.get("lebar", 1.15)) * s
        h = float(opsi.get("tinggi", 2.05)) * s
        buka = clamp(float(opsi.get("buka", 0.0)))
        pop_p = clamp(float(opsi.get("pop_up", 1.0)))
        jatuh = clamp(float(opsi.get("jatuh", 0.0)))
        pop_rx = (1.0 - e_spring(pop_p)) * 88.0 + e_io(jatuh) * 86.0
        pmat = mat @ euler_mat(pop_rx, 0.0, 0.0)
        thk = 0.068 * s

        anc_trim = np.array(pos, dtype=np.float32) + pmat @ np.array([0.0, h * 0.5, -0.04 * s], dtype=np.float32)
        anc_frame = np.array(pos, dtype=np.float32) + pmat @ np.array([0.0, h * 0.5, -0.01 * s], dtype=np.float32)
        anc_port = np.array(pos, dtype=np.float32) + pmat @ np.array([0.0, h * 0.5, +0.02 * s], dtype=np.float32)
        anc_sil = np.array(pos, dtype=np.float32) + pmat @ np.array([0.0, h * 0.5, +0.045 * s], dtype=np.float32)

        r_in = w * 0.44
        r_out = w * 0.50 + 0.11 * s
        cy_a = max(0.05 * s, h - w * 0.50)
        jw = r_out - r_in

        # Lapisan lis luar krem tipis + kusen utama berwarna mulus (bias negatif ringan agar tidak pernah terpotong arch_wall!)
        for sgn in (-1.0, 1.0):
            sc.extrude_2d(rrect_2d(0.0, cy_a * 0.5, jw + 0.05 * s, cy_a, 0.01 * s), thk * 0.82, PUTIH, PUTIH, None, origin=np.array(pos) + pmat @ np.array([sgn * (r_in + jw * 0.55), 0.0, -0.01 * s]), mat=pmat, bias=-0.12, sort_anchor=anc_trim)
            sc.extrude_2d(rrect_2d(0.0, cy_a * 0.5, jw, cy_a, 0.01 * s), thk, col_frame, col_frame, None, origin=np.array(pos) + pmat @ np.array([sgn * (r_in + jw * 0.5), 0.0, 0.0]), mat=pmat, bias=-0.18, sort_anchor=anc_frame)
        sc.extrude_ring_arch(r_out - 0.01 * s, r_out + 0.045 * s, cy_a, thk * 0.82, PUTIH, n_arc=44, origin=np.array(pos) + pmat @ np.array([0, 0, -0.01 * s]), mat=pmat, bias=-0.12, cast_shadow=False, sort_anchor=anc_trim)
        sc.extrude_ring_arch(r_in, r_out, cy_a, thk, col_frame, n_arc=44, origin=pos, mat=pmat, bias=-0.18, sort_anchor=anc_frame)

        # Lubang portal bercahaya / siluet rusa malam (00:15 — kabut cahaya emas hangat, tidak overexposed!)
        if opsi.get("cahaya_portal"):
            inner_arch = arch_2d(w * 0.88, h * 0.92, n_arc=28)
            p_col = opsi.get("warna_portal", (248, 214, 128))
            em_lvl = float(opsi.get("emissive_portal", 0.46))
            sc.extrude_2d(inner_arch, 0.02 * s, p_col, p_col, p_col, origin=np.array(pos) + pmat @ np.array([0, 0, thk * 0.35]), mat=pmat, emissive=em_lvl, cast_shadow=False, sort_anchor=anc_port)
            sc.add_light(np.array(pos) + pmat @ np.array([0, h * 0.52, 0.55 * s]), color=p_col, intensity=0.95, radius=3.6, halo=0.28 * s)
            if opsi.get("siluet") == "rusa":
                sil_c = (168, 134, 92)
                so_z = thk * 0.56
                # Siluet rusa lembut berkabut emas + dua mata kecil bersinar putih + tanduk bercabang
                sc.extrude_2d(coat_2d(0.22 * s, 0.36 * s, h * 0.44, 0.04 * s), 0.012 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([0, 0.01 * s, so_z]), mat=pmat, emissive=0.18, cast_shadow=False, sort_anchor=anc_sil)
                sc.extrude_2d(rrect_2d(0.0, h * 0.48, 0.075 * s, 0.12 * s, 0.02 * s), 0.012 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([0, 0, so_z]), mat=pmat, emissive=0.18, cast_shadow=False, sort_anchor=anc_sil)
                sc.extrude_2d(circle_2d(0.0, h * 0.54, 0.105 * s, 0.115 * s, 20), 0.012 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([0, 0, so_z]), mat=pmat, emissive=0.18, cast_shadow=False, sort_anchor=anc_sil)
                for ex in (-0.038 * s, 0.038 * s):
                    sc.extrude_2d(circle_2d(ex, h * 0.545, 0.015 * s, 0.017 * s, 10), 0.010 * s, (255, 255, 248), (255, 255, 248), (255, 255, 248), origin=np.array(pos) + pmat @ np.array([0, 0, so_z + 0.01 * s]), mat=pmat, emissive=1.10, cast_shadow=False, sort_anchor=anc_sil + pmat @ np.array([0, 0, 0.012 * s], dtype=np.float32))
                for sx in (-1, 1):
                    sc.extrude_2d(rrect_2d(0.0, 0.12 * s, 0.022 * s, 0.26 * s, 0.008 * s), 0.010 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([sx * 0.048 * s, h * 0.59, so_z]), mat=pmat @ euler_mat(0, 0, sx * -26), emissive=0.18, cast_shadow=False, sort_anchor=anc_sil)
                    sc.extrude_2d(rrect_2d(0.0, 0.06 * s, 0.018 * s, 0.12 * s, 0.007 * s), 0.010 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([sx * 0.105 * s, h * 0.67, so_z]), mat=pmat @ euler_mat(0, 0, sx * 16), emissive=0.18, cast_shadow=False, sort_anchor=anc_sil)
                    sc.extrude_2d(rrect_2d(0.0, 0.05 * s, 0.016 * s, 0.10 * s, 0.006 * s), 0.010 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([sx * 0.135 * s, h * 0.72, so_z]), mat=pmat @ euler_mat(0, 0, sx * -46), emissive=0.18, cast_shadow=False, sort_anchor=anc_sil)

        # Ornamen mahkota di atas pintu (ditempatkan di depan dinding dengan sort_anchor sendiri agar tidak pernah hilang!)
        orn = opsi.get("ornamen")
        if orn == "setengah_lingkaran":
            semi = [(-0.42 * s, 0.0), (0.42 * s, 0.0)] + [(round(0.42 * s * math.cos(math.pi * i / 24), 5), round(0.42 * s * math.sin(math.pi * i / 24), 5)) for i in range(25)]
            orn_o = np.array(pos, dtype=np.float32) + pmat @ np.array([0, h + 0.12 * s, +0.015 * s], dtype=np.float32)
            sc.extrude_2d(semi, thk * 0.65, opsi.get("warna_ornamen", HIJAU), opsi.get("warna_ornamen", HIJAU), None, origin=orn_o, mat=pmat, bias=-0.20, cast_shadow=False, sort_anchor=orn_o)
        elif orn == "matahari":
            r_sc = clamp(float(opsi.get("ray_scale", 1.0)))
            if r_sc > 0.02:
                re = e_spring(r_sc)
                for k in range(11):
                    ang = -85 + k * 17
                    ar = math.radians(ang)
                    ray_o = np.array(pos) + pmat @ np.array([math.sin(ar) * (w * 0.56), h * 0.58 + math.cos(ar) * (h * 0.44), -0.04 * s])
                    sc.extrude_2d(((-0.095 * s, 0.0), (0.095 * s, 0.0), (0.0, 0.96 * s * re)), 0.032 * s, KUNING, KUNING, None, origin=ray_o, mat=pmat @ euler_mat(0, 0, -ang), bias=-0.10, sort_anchor=anc_frame)

        # Daun pintu berengsel di kiri (-w*0.44) + panel karton timbul (opsional sembunyikan daun untuk portal terbuka penuh)
        if not opsi.get("tanpa_daun", False):
            leaf = arch_2d(w * 0.88, h * 0.94, n_arc=28)
            hinge_off = np.array([-w * 0.44, 0.0, thk * 0.55], dtype=np.float32)
            leaf_mat = pmat @ euler_mat(0.0, -e_io(buka) * 102.0, 0.0)
            leaf_origin = np.array(pos) + pmat @ hinge_off
            leaf_base = leaf_origin - leaf_mat @ np.array([-w * 0.44, 0.0, 0.0])
            lc = leaf_base + leaf_mat @ np.array([0.0, h * 0.48, 0.02 * s], dtype=np.float32)
            sc.extrude_2d(leaf, 0.040 * s, col_door, gelap(col_door, 0.14), None, origin=leaf_base, mat=leaf_mat, sort_anchor=lc)
            if opsi.get("panel_garis"):
                # Pintu bergaris kayu/kertas horizontal seperti pintu jatuh labirin (REF s19!)
                for gy in (0.24, 0.44, 0.64, 0.84, 1.04, 1.24):
                    if gy * s < h * 0.78:
                        sc.extrude_2d(rrect_2d(0.0, gy * s, w * 0.72, 0.038 * s, 0.01 * s), 0.014 * s, gelap(col_door, 0.22), gelap(col_door, 0.22), None, origin=leaf_base + leaf_mat @ np.array([0.0, 0.0, 0.024 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=lc + leaf_mat @ np.array([0, 0, 0.02 * s], dtype=np.float32))
            else:
                panel = arch_2d(w * 0.64, h * 0.72, n_arc=22)
                sc.extrude_2d(panel, 0.012 * s, terang(col_door, 0.10), terang(col_door, 0.06), None, origin=leaf_base + leaf_mat @ np.array([0.0, h * 0.10, 0.022 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=lc + leaf_mat @ np.array([0, 0, 0.015 * s], dtype=np.float32), drop_shadow=0.14)
            knob_pos = leaf_base + leaf_mat @ np.array([w * 0.34, h * 0.42, 0.042 * s])
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.048 * s, 0.048 * s, 18), 0.042 * s, KUNING, KUNING, None, origin=knob_pos, mat=leaf_mat, cast_shadow=False, sort_anchor=lc + leaf_mat @ np.array([0, 0, 0.052 * s], dtype=np.float32), drop_shadow=0.18)
            if opsi.get("play_door"):
                p_anc = lc + leaf_mat @ np.array([0, 0, 0.032 * s], dtype=np.float32)
                p_anc2 = lc + leaf_mat @ np.array([0, 0, 0.046 * s], dtype=np.float32)
                top_arch = arch_2d(w * 0.60, h * 0.42, n_arc=22)
                sc.extrude_2d(top_arch, 0.014 * s, SALMON, SALMON, None, origin=leaf_base + leaf_mat @ np.array([0.0, h * 0.46, 0.028 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=p_anc, drop_shadow=0.14)
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.075 * s, 0.075 * s, 18), 0.014 * s, KUNING, KUNING, None, origin=leaf_base + leaf_mat @ np.array([0.0, h * 0.72, 0.038 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=p_anc2, drop_shadow=0.12)
                play_o = leaf_base + leaf_mat @ np.array([0.0, h * 0.34, 0.036 * s])
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.23 * s, 0.23 * s, 26), 0.020 * s, PUTIH, PUTIH, None, origin=play_o, mat=leaf_mat, cast_shadow=False, sort_anchor=p_anc, drop_shadow=0.16)
                sc.extrude_2d(((-0.08 * s, -0.10 * s), (0.12 * s, 0.0), (-0.08 * s, 0.10 * s)), 0.016 * s, col_door, col_door, None, origin=play_o + leaf_mat @ np.array([0.01 * s, 0.0, 0.018 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=p_anc2, drop_shadow=0.12)
                b_o = leaf_base + leaf_mat @ np.array([w * 0.38, h * 0.56, 0.044 * s])
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.135 * s, 0.135 * s, 22), 0.024 * s, KUNING, KUNING, None, origin=b_o, mat=leaf_mat, cast_shadow=False, sort_anchor=p_anc2, drop_shadow=0.16)
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.032 * s, 0.12 * s, 0.008 * s), 0.012 * s, PUTIH, PUTIH, PUTIH, origin=b_o + leaf_mat @ np.array([0.0, 0.0, 0.018 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=lc + leaf_mat @ np.array([0, 0, 0.058 * s], dtype=np.float32))
            if opsi.get("jendela_bulat"):
                win_pos = leaf_base + leaf_mat @ np.array([0.0, h * 0.64, 0.030 * s])
                w_anc = lc + leaf_mat @ np.array([0, 0, 0.030 * s], dtype=np.float32)
                w_anc2 = lc + leaf_mat @ np.array([0, 0, 0.042 * s], dtype=np.float32)
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.21 * s, 0.21 * s, 24), 0.014 * s, PUTIH, PUTIH, None, origin=win_pos, mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc, drop_shadow=0.14)
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.165 * s, 0.165 * s, 24), 0.014 * s, BIRU_MUDA, BIRU_MUDA, None, origin=win_pos + leaf_mat @ np.array([0, 0, 0.008 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc2)
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.34 * s, 0.026 * s, 0.008 * s), 0.014 * s, PUTIH, PUTIH, None, origin=win_pos + leaf_mat @ np.array([0, 0, 0.014 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc2)
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.026 * s, 0.34 * s, 0.008 * s), 0.014 * s, PUTIH, PUTIH, None, origin=win_pos + leaf_mat @ np.array([0, 0, 0.014 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc2)

    elif jenis in ("kartu_pita", "label_kertas"):
        w = float(opsi.get("lebar", 1.24)) * s
        h = float(opsi.get("tinggi", 0.42)) * s
        flip = clamp(float(opsi.get("flip", 1.0)))
        flip_rx = (1.0 - e_spring(flip)) * 84.0
        kmat = mat @ euler_mat(flip_rx, 0.0, 0.0)
        sc.extrude_2d(rrect_2d(0.0, 0.0, w, h, 0.025 * s), 0.036 * s, PUTIH, PUTIH, KERTAS_TEPI, origin=pos, mat=kmat, bias=-1.4, sort_anchor=pos, cast_shadow=bool(opsi.get("bayangan", False)))
        tex = _plaque_texture(opsi.get("teks_besar", ""), opsi.get("teks_kecil", ""), opsi.get("warna_aksen", MERAH))
        pts = _world_quad(pos, kmat, [(-w * 0.49, h * 0.48, 0.022 * s), (w * 0.49, h * 0.48, 0.022 * s), (w * 0.49, -h * 0.48, 0.022 * s), (-w * 0.49, -h * 0.48, 0.022 * s)])
        sc.textured_quad(pts, tex, emissive=0.02, bias=-1.5)

    elif jenis == "hp_kertas":
        # Smartphone buku kertas tebal bertumpuk 10 lembar nyata (sisi berlapis jelas seperti REF s01 & s27-30!)
        pw, pl = 2.65 * s, 4.15 * s
        rmat_flat = mat @ euler_mat(-90.0, 0.0, 0.0)
        o_base = np.array(pos, dtype=np.float32)
        layer_cols = [
            (132, 174, 158), (242, 236, 224), (154, 196, 178), (246, 240, 228),
            (142, 184, 168), (240, 234, 222), (160, 202, 184), (246, 240, 228),
            (148, 190, 172), (244, 238, 226),
        ]
        for i, lc in enumerate(layer_cols):
            yi = (0.018 + i * 0.036) * s
            p_l = o_base + mat @ np.array([0.0, yi, 0.0])
            edge_l = gelap(lc, 0.14) if i % 2 == 0 else (218, 210, 196)
            sc.extrude_2d(rrect_2d(0.0, 0.0, pw, pl, 0.28 * s, n_corner=5), 0.032 * s, lc, lc, edge_l, origin=p_l, mat=rmat_flat, cast_shadow=(i in (0, 5, 9)), sort_anchor=p_l)
        # Tab pembatas warna biru, merah, & kuning menonjol di samping tumpukan halaman
        for side, tz, tcol, ty in ((-1, -0.75 * s, BIRU, 0.20 * s), (-1, 0.35 * s, KORAL, 0.14 * s), (1, 0.55 * s, KUNING, 0.22 * s)):
            tl_o = o_base + mat @ np.array([side * (pw * 0.52), ty, tz])
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.26 * s, 0.56 * s, 0.06 * s), 0.026 * s, tcol, tcol, None, origin=tl_o, mat=rmat_flat, cast_shadow=True, sort_anchor=o_base + mat @ np.array([0.0, ty, 0.0]))

        # Bezel biru tua + layar putih gading di puncak tumpukan (y ~ 0.40*s)
        bz_o = o_base + mat @ np.array([0.0, 0.376 * s, 0.0])
        sc.extrude_2d(rrect_2d(0.0, 0.0, pw * 0.96, pl * 0.96, 0.26 * s, n_corner=5), 0.028 * s, BIRU_TUA, BIRU_TUA, None, origin=bz_o, mat=rmat_flat, cast_shadow=True, sort_anchor=bz_o)
        scr_o = o_base + mat @ np.array([0.0, 0.400 * s, 0.0])
        sc.extrude_2d(rrect_2d(0.0, 0.0, pw * 0.86, pl * 0.88, 0.18 * s, n_corner=5), 0.016 * s, (246, 240, 228), (246, 240, 228), None, origin=scr_o, mat=rmat_flat, cast_shadow=False, sort_anchor=scr_o)

        # Video player card merah-koral + segitiga putih + progress bar
        p_ui = o_base + mat @ np.array([0.0, 0.416 * s, 0.0])
        sc.extrude_2d(rrect_2d(0.0, 0.95 * s, pw * 0.76, pl * 0.27, 0.10 * s, n_corner=4), 0.014 * s, KORAL, KORAL, None, origin=p_ui, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui)
        p_ui2 = o_base + mat @ np.array([0.0, 0.428 * s, 0.0])
        sc.extrude_2d(((-0.14 * s, 0.80 * s), (0.18 * s, 0.96 * s), (-0.14 * s, 1.12 * s)), 0.010 * s, PUTIH, PUTIH, PUTIH, origin=p_ui2, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui2)
        sc.extrude_2d(rrect_2d(0.0, 0.56 * s, pw * 0.66, 0.045 * s, 0.015 * s), 0.008 * s, (244, 210, 200), (244, 210, 200), None, origin=p_ui2, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui2)

        # 4 kartu aplikasi warna pastel (2x2) + 3 titik navigasi bawah
        for ix, iz, col in ((-0.50, 0.12, HIJAU), (0.50, 0.12, KUNING), (-0.50, -0.62, BIRU_MUDA), (0.50, -0.62, PINK)):
            sc.extrude_2d(rrect_2d(ix * s, iz * s, 0.90 * s, 0.56 * s, 0.10 * s, n_corner=4), 0.014 * s, col, col, None, origin=p_ui, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui)
        for dx in (-0.28 * s, 0.0, 0.28 * s):
            sc.extrude_2d(circle_2d(dx, -1.28 * s, 0.065 * s, 0.065 * s, 14), 0.010 * s, (208, 200, 188), (208, 200, 188), None, origin=p_ui, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui)

        # Kartu Play merah pop-up + lencana angka '1' kuning (opsional geser x via play_dx agar tak ketutup kepala Luna!)
        pop = clamp(float(opsi.get("pop_up", 1.0)))
        if pop > 0.02:
            rx_card = (1.0 - e_spring(pop)) * 88.0
            cmat = mat @ euler_mat(rx_card, 0.0, 0.0)
            play_dx = float(opsi.get("play_dx", 0.0)) * s
            c_o = o_base + mat @ np.array([play_dx, 0.42 * s, -0.25 * s])
            c_anc = c_o + cmat @ np.array([0.0, 0.48 * s, 0.0], dtype=np.float32)
            c_anc_front = c_o + cmat @ np.array([0.0, 0.48 * s, +0.042 * s], dtype=np.float32)
            sc.extrude_2d(rrect_2d(0.0, 0.48 * s, 1.06 * s, 0.94 * s, 0.09 * s, n_corner=4), 0.054 * s, MERAH, MERAH, None, origin=c_o, mat=cmat, sort_anchor=c_anc)
            sc.extrude_2d(circle_2d(0.0, 0.48 * s, 0.27 * s, 0.27 * s, 24), 0.018 * s, PUTIH, PUTIH, PUTIH, origin=c_o + cmat @ np.array([0.0, 0.0, 0.032 * s]), mat=cmat, cast_shadow=False, sort_anchor=c_anc_front)
            sc.extrude_2d(((-0.08 * s, 0.36 * s), (0.14 * s, 0.48 * s), (-0.08 * s, 0.60 * s)), 0.016 * s, MERAH, MERAH, MERAH, origin=c_o + cmat @ np.array([0.02 * s, 0.0, 0.045 * s]), mat=cmat, cast_shadow=False, sort_anchor=c_o + cmat @ np.array([0.0, 0.48 * s, +0.056 * s], dtype=np.float32))
            b_o = c_o + cmat @ np.array([0.48 * s, 0.92 * s, 0.038 * s])
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.17 * s, 0.17 * s, 22), 0.028 * s, KUNING, KUNING, None, origin=b_o, mat=cmat, cast_shadow=False, sort_anchor=c_anc_front)
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.040 * s, 0.16 * s, 0.010 * s), 0.012 * s, PUTIH, PUTIH, PUTIH, origin=b_o + cmat @ np.array([0.0, 0.0, 0.022 * s]), mat=cmat, cast_shadow=False, sort_anchor=c_o + cmat @ np.array([0.0, 0.48 * s, +0.062 * s], dtype=np.float32))

    elif jenis in ("jam_weker_kertas", "weker", "jam"):
        r = 0.62 * s
        case_c = opsi.get("warna", KORAL)
        for sx in (-0.34 * s, 0.34 * s):
            sc.extrude_2d(rrect_2d(0.0, 0.12 * s, 0.11 * s, 0.24 * s, 0.035 * s), 0.11 * s, KUNING, KUNING, None, origin=np.array(pos) + mat @ np.array([sx, 0.0, 0.0]), mat=mat)
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.18 * s, 0.18 * s, 20), 0.18 * s, KUNING, KUNING, None, origin=np.array(pos) + mat @ np.array([sx * 1.15, r * 2.06, 0.0]), mat=mat)
        c_o = np.array(pos) + mat @ np.array([0.0, r + 0.16 * s, 0.0])
        sc.extrude_2d(circle_2d(0.0, 0.0, r, r, 32), 0.26 * s, case_c, case_c, None, origin=c_o, mat=mat, sort_anchor=c_o)
        sc.extrude_2d(circle_2d(0.0, 0.0, r * 0.80, r * 0.80, 28), 0.02 * s, (242, 246, 236), (242, 246, 236), None, origin=c_o + mat @ np.array([0.0, 0.0, 0.138 * s]), mat=mat, cast_shadow=False, sort_anchor=c_o + mat @ np.array([0.0, 0.0, 0.15 * s]), drop_shadow=0.18)
        ang_m = -t * 90.0 if opsi.get("putar") else -35.0
        ang_h = -t * 15.0 if opsi.get("putar") else 45.0
        tick_anc = c_o + mat @ np.array([0.0, 0.0, 0.175 * s])
        for k in range(12):
            a = k * math.pi / 6.0
            sc.extrude_2d(circle_2d(r * 0.66 * math.sin(a), r * 0.66 * math.cos(a), 0.022 * s, 0.022 * s, 10), 0.012 * s, OUT, OUT, OUT, origin=c_o + mat @ np.array([0.0, 0.0, 0.152 * s]), mat=mat, cast_shadow=False, sort_anchor=tick_anc)
        sc.extrude_2d(rrect_2d(0.0, 0.16 * s, 0.04 * s, 0.34 * s, 0.015 * s), 0.02 * s, OUT, OUT, OUT, origin=c_o + mat @ np.array([0.0, 0.0, 0.158 * s]), mat=mat @ euler_mat(0, 0, ang_m), cast_shadow=False, sort_anchor=tick_anc, drop_shadow=0.14)
        sc.extrude_2d(rrect_2d(0.0, 0.11 * s, 0.048 * s, 0.24 * s, 0.015 * s), 0.02 * s, OUT, OUT, OUT, origin=c_o + mat @ np.array([0.0, 0.0, 0.164 * s]), mat=mat @ euler_mat(0, 0, ang_h), cast_shadow=False, sort_anchor=tick_anc, drop_shadow=0.14)
        sc.extrude_2d(rrect_2d(0.0, 0.18 * s, 0.018 * s, 0.36 * s, 0.008 * s), 0.015 * s, MERAH, MERAH, MERAH, origin=c_o + mat @ np.array([0.0, 0.0, 0.170 * s]), mat=mat @ euler_mat(0, 0, -t * 220.0), cast_shadow=False, sort_anchor=tick_anc)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.042 * s, 0.042 * s, 14), 0.024 * s, KUNING, KUNING, None, origin=c_o + mat @ np.array([0.0, 0.0, 0.174 * s]), mat=mat, cast_shadow=False, sort_anchor=tick_anc)

    elif jenis == "menara_jam":
        # Menara jam 3 tingkat berengsel pop-up di dasar y=0 (bangkit 90° dari rebah seperti buku pop-up REF s03!)
        pop_p = clamp(float(opsi.get("pop_up", 1.0)))
        if pop_p <= 0.005:
            return
        pop_rx = (1.0 - e_spring(pop_p)) * -88.0
        mmat = mat @ euler_mat(pop_rx, 0.0, 0.0)
        sc.box(np.array(pos) + mmat @ np.array([0.0, 1.90 * s, 0.0]), (1.52 * s, 3.80 * s, 1.48 * s), (94, 128, 178), mat=mmat)
        for fl in range(3):
            fy = (0.48 + fl * 1.18) * s
            sc.box(np.array(pos) + mmat @ np.array([0.0, fy - 0.18 * s, 0.0]), (1.66 * s, 0.10 * s, 1.62 * s), KRIM, mat=mmat)
            w_o = np.array(pos) + mmat @ np.array([0.0, fy + 0.06 * s, 0.76 * s])
            sc.extrude_2d(arch_2d(0.42 * s, 0.66 * s, 18), 0.036 * s, BIRU_TUA, BIRU_TUA, None, origin=w_o, mat=mmat, cast_shadow=False, sort_anchor=w_o)
            for sx_s in (-0.76 * s, 0.76 * s):
                ws_o = np.array(pos) + mmat @ np.array([sx_s, fy + 0.06 * s, 0.0])
                sc.extrude_2d(arch_2d(0.38 * s, 0.60 * s, 16), 0.03 * s, BIRU_TUA, BIRU_TUA, None, origin=ws_o, mat=mmat @ euler_mat(0, 90 if sx_s > 0 else -90, 0), cast_shadow=False, sort_anchor=ws_o)
        sc.box(np.array(pos) + mmat @ np.array([0.0, 4.66 * s, 0.0]), (1.88 * s, 1.72 * s, 1.68 * s), PUTIH, mat=mmat)
        sc.extrude_2d(((-1.04 * s, 0.0), (1.04 * s, 0.0), (0.0, 0.92 * s)), 1.72 * s, KORAL, KORAL, None, origin=np.array(pos) + mmat @ np.array([0.0, 5.52 * s, 0.0]), mat=mmat)
        sc.extrude_2d(((-0.035 * s, 0.0), (0.035 * s, 0.0), (0.0, 0.48 * s)), 0.035 * s, KUNING, KUNING, KUNING, origin=np.array(pos) + mmat @ np.array([0.0, 6.42 * s, 0.0]), mat=mmat)
        cf_o = np.array(pos) + mmat @ np.array([0.0, 4.66 * s, 0.86 * s])
        anc_cf = np.array(pos) + mmat @ np.array([0.0, 3.6 * s, 1.35 * s])
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.78 * s, 0.78 * s, 32), 0.06 * s, KUNING, KUNING, None, origin=cf_o, mat=mmat, sort_anchor=anc_cf)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.62 * s, 0.62 * s, 28), 0.02 * s, (250, 246, 236), (250, 246, 236), None, origin=cf_o + mmat @ np.array([0.0, 0.0, 0.034 * s]), mat=mmat, cast_shadow=False, sort_anchor=anc_cf + mmat @ np.array([0.0, 0.0, 0.03 * s]))
        tick_anc = anc_cf + mmat @ np.array([0.0, 0.0, 0.06 * s])
        for k in range(12):
            sc.extrude_2d(rrect_2d(0.0, 0.51 * s, 0.035 * s, 0.10 * s, 0.008 * s), 0.012 * s, BIRU_TUA, BIRU_TUA, None, origin=cf_o + mmat @ np.array([0.0, 0.0, 0.048 * s]), mat=mmat @ euler_mat(0, 0, -k * 30.0), cast_shadow=False, sort_anchor=tick_anc)
        sc.extrude_2d(rrect_2d(0.0, 0.21 * s, 0.055 * s, 0.44 * s, 0.02 * s), 0.02 * s, BIRU_TUA, BIRU_TUA, BIRU_TUA, origin=cf_o + mmat @ np.array([0.0, 0.0, 0.052 * s]), mat=mmat @ euler_mat(0, 0, -t * 210.0), cast_shadow=False, sort_anchor=tick_anc)
        sc.extrude_2d(rrect_2d(0.0, 0.14 * s, 0.060 * s, 0.30 * s, 0.02 * s), 0.02 * s, OUT, OUT, OUT, origin=cf_o + mmat @ np.array([0.0, 0.0, 0.058 * s]), mat=mmat @ euler_mat(0, 0, -t * 36.0), cast_shadow=False, sort_anchor=tick_anc)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.06 * s, 0.06 * s, 14), 0.024 * s, KUNING, KUNING, None, origin=cf_o + mmat @ np.array([0.0, 0.0, 0.064 * s]), mat=mmat, cast_shadow=False, sort_anchor=tick_anc)

    elif jenis == "pensil_kertas":
        col = opsi.get("warna", KUNING)
        sc.rbox(np.array(pos) + mat @ np.array([0.0, 0.08 * s, 0.0]), (2.5 * s, 0.16 * s, 0.16 * s), col, roundness=0.45, seg=1, mat=mat)
        sc.box(np.array(pos) + mat @ np.array([-1.32 * s, 0.08 * s, 0.0]), (0.14 * s, 0.165 * s, 0.165 * s), ABU, mat=mat)
        sc.box(np.array(pos) + mat @ np.array([-1.46 * s, 0.08 * s, 0.0]), (0.16 * s, 0.155 * s, 0.155 * s), SALMON, mat=mat)
        sc.extrude_2d(((0.0, -0.08 * s), (0.34 * s, -0.025 * s), (0.34 * s, 0.025 * s), (0.0, 0.08 * s)), 0.13 * s, KRIM, KRIM, None, origin=np.array(pos) + mat @ np.array([1.25 * s, 0.08 * s, 0.0]), mat=mat)
        sc.extrude_2d(((0.0, -0.026 * s), (0.13 * s, 0.0), (0.0, 0.026 * s)), 0.08 * s, OUT, OUT, OUT, origin=np.array(pos) + mat @ np.array([1.58 * s, 0.08 * s, 0.0]), mat=mat)

    elif jenis == "pohon_kertas":
        sc.extrude_2d(rrect_2d(0.0, 0.45 * s, 0.14 * s, 0.90 * s, 0.03 * s), 0.06 * s, COKLAT, COKLAT, None, origin=pos, mat=mat)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.48 * s, 0.46 * s, 24), 0.05 * s, opsi.get("warna", HIJAU), opsi.get("warna", HIJAU), None, origin=np.array(pos) + mat @ np.array([0.0, 1.12 * s, 0.0]), mat=mat)

    elif jenis == "lampu_taman_kertas":
        pop_p = clamp(float(opsi.get("pop_up", 1.0)))
        if pop_p <= 0.01:
            return
        lmat = mat @ euler_mat((1.0 - e_spring(pop_p)) * -88.0, 0.0, 0.0)
        sc.box(np.array(pos) + lmat @ np.array([0.0, 0.72 * s, 0.0]), (0.06 * s, 1.44 * s, 0.06 * s), (62, 62, 72), mat=lmat)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.14 * s, 0.14 * s, 20), 0.14 * s, KUNING_MUDA, KUNING_MUDA, KUNING, origin=np.array(pos) + lmat @ np.array([0.0, 1.52 * s, 0.0]), mat=lmat, emissive=0.75)

    elif jenis == "buku":
        sc.extrude_2d(rrect_2d(0.0, 0.0, 0.22 * s, 0.28 * s, 0.03 * s), 0.05 * s, opsi.get("warna", BIRU), opsi.get("warna", BIRU), PUTIH, origin=pos, mat=mat)

    elif jenis == "kado":
        sc.box(np.array(pos) + mat @ np.array([0.0, 0.14 * s, 0.0]), (0.28 * s, 0.28 * s, 0.28 * s), opsi.get("warna", PINK), mat=mat)
        sc.box(np.array(pos) + mat @ np.array([0.0, 0.14 * s, 0.0]), (0.30 * s, 0.29 * s, 0.05 * s), KUNING, mat=mat, bias=-0.01)

    elif jenis == "payung":
        sc.box(np.array(pos) + mat @ np.array([0.0, 0.42 * s, 0.0]), (0.04 * s, 0.84 * s, 0.04 * s), OUT, mat=mat)
        sc.extrude_2d(((-0.48 * s, 0.0), (0.48 * s, 0.0), (0.24 * s, 0.22 * s), (-0.24 * s, 0.22 * s)), 0.42 * s, opsi.get("warna", MERAH), opsi.get("warna", MERAH), None, origin=np.array(pos) + mat @ np.array([0.0, 0.78 * s, 0.0]), mat=mat)


def draw_icon_3d(sc, kind, pos, t=0.0, s=1.0):
    px, py, pz = pos
    py += math.sin(t * 5.0) * 0.04 * s
    if kind == "bohlam":
        sc.extrude_2d(circle_2d(0.0, 0.14 * s, 0.13 * s, 0.14 * s, 20), 0.04 * s, KUNING, KUNING, PUTIH, origin=(px, py, pz), emissive=0.75)
    elif kind == "tanda_seru":
        sc.extrude_2d(rrect_2d(0.0, 0.16 * s, 0.08 * s, 0.24 * s, 0.03 * s), 0.04 * s, MERAH, MERAH, None, origin=(px, py, pz))
        sc.extrude_2d(circle_2d(0.0, -0.02 * s, 0.045 * s, 0.045 * s, 14), 0.04 * s, MERAH, MERAH, None, origin=(px, py, pz))
    elif kind == "tanya":
        sc.extrude_2d(rrect_2d(0.0, 0.16 * s, 0.16 * s, 0.18 * s, 0.06 * s), 0.04 * s, BIRU, BIRU, None, origin=(px, py, pz))
        sc.extrude_2d(circle_2d(0.0, -0.02 * s, 0.045 * s, 0.045 * s, 14), 0.04 * s, BIRU, BIRU, None, origin=(px, py, pz))
    elif kind == "hati":
        sc.extrude_2d(circle_2d(0.0, 0.12 * s, 0.14 * s, 0.13 * s, 18), 0.04 * s, PINK, PINK, None, origin=(px, py, pz))
    elif kind in ("kilau", "bintang"):
        sc.extrude_2d(star_2d(0.16 * s, 0.07 * s, 5), 0.03 * s, KUNING, KUNING, None, origin=(px, py, pz), rot=(0.0, t * 80.0, 0.0), emissive=0.75)
    elif kind == "zzz":
        sc.extrude_2d(rrect_2d(0.0, 0.12 * s, 0.18 * s, 0.06 * s, 0.02 * s), 0.03 * s, BIRU_MUDA, BIRU_MUDA, None, origin=(px, py, pz))
