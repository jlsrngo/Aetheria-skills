# -*- coding: utf-8 -*-
"""
benda.py - properti 3D Pop-Up Paper Craft berlapis detail (pintu lengkung, kartu pita,
           HP kertas bertumpuk, menara jam, jam weker, pensil, dan ikon kertas).
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from paper import (
    OUT, KERTAS_TEPI, PUTIH, KRIM, HITAM, KORAL, MERAH, MERAH_TUA,
    BIRU, BIRU_TUA, BIRU_MUDA, MINT, MINT_MUDA, TEAL, PINK, SALMON, KUNING, KUNING_MUDA,
    ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA, ABU, ABU_TUA,
    clamp, gelap, terang, mix, e_spring, e_io, euler_mat, font,
    circle_2d, rrect_2d, coat_2d, arch_2d, star_2d,
)


def _plaque_texture(teks_besar="5", teks_kecil="MENIT", accent=MERAH):
    """Plakat kartu pita gading bersih ala '5 MENIT', '1 JAM', 'SATU PINTU lagi'."""
    W, H = 420, 128
    im = Image.new("RGBA", (W, H), (252, 249, 242, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([5, 5, W - 6, H - 6], outline=(224, 212, 196, 255), width=3)
    d.rectangle([11, 11, W - 12, H - 12], outline=(235, 224, 208, 255), width=2)
    tb = str(teks_besar or "")
    tk = str(teks_kecil or "")
    if tb and tk:
        is_num = tb.strip().isdigit()
        s1 = 74 if is_num else 34
        s2 = 40 if is_num else 48
        c1 = accent if is_num else OUT
        c2 = OUT if is_num else accent
        fn1 = "judul" if is_num else "teks"
        gap = 16
        while s1 > 18:
            f1 = font(fn1, s1)
            f2 = font("judul", s2)
            w1 = d.textlength(tb, font=f1)
            w2 = d.textlength(tk, font=f2)
            if w1 + gap + w2 <= W - 44:
                break
            s1 = int(s1 * 0.88)
            s2 = max(18, int(s2 * 0.88))
        x0 = (W - (w1 + gap + w2)) * 0.5
        d.text((x0 + w1 * 0.5, H * 0.50), tb, font=f1, fill=c1 + (255,), anchor="mm")
        d.text((x0 + w1 + gap + w2 * 0.5, H * (0.53 if is_num else 0.49)), tk, font=f2, fill=c2 + (255,), anchor="mm")
    else:
        txt = tb or tk
        sz = 40
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
        pop_rx = (1.0 - e_spring(pop_p)) * 88.0
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

        # Lapisan lis luar krem tipis + kusen utama berwarna mulus tanpa ear-clipping busur
        for sgn in (-1.0, 1.0):
            sc.extrude_2d(rrect_2d(0.0, cy_a * 0.5, jw + 0.05 * s, cy_a, 0.01 * s), thk * 0.82, PUTIH, PUTIH, None, origin=np.array(pos) + pmat @ np.array([sgn * (r_in + jw * 0.55), 0.0, -0.01 * s]), mat=pmat, sort_anchor=anc_trim, drop_shadow=0.18)
            sc.extrude_2d(rrect_2d(0.0, cy_a * 0.5, jw, cy_a, 0.01 * s), thk, col_frame, col_frame, None, origin=np.array(pos) + pmat @ np.array([sgn * (r_in + jw * 0.5), 0.0, 0.0]), mat=pmat, sort_anchor=anc_frame)
        sc.extrude_ring_arch(r_out - 0.01 * s, r_out + 0.045 * s, cy_a, thk * 0.82, PUTIH, n_arc=32, origin=np.array(pos) + pmat @ np.array([0, 0, -0.01 * s]), mat=pmat, cast_shadow=False, sort_anchor=anc_trim, drop_shadow=0.18)
        sc.extrude_ring_arch(r_in, r_out, cy_a, thk, col_frame, n_arc=32, origin=pos, mat=pmat, sort_anchor=anc_frame)

        # Lubang portal bercahaya / siluet rusa malam (00:15)
        if opsi.get("cahaya_portal"):
            inner_arch = arch_2d(w * 0.88, h * 0.92, n_arc=28)
            p_col = opsi.get("warna_portal", (252, 228, 138))
            sc.extrude_2d(inner_arch, 0.02 * s, p_col, p_col, p_col, origin=np.array(pos) + pmat @ np.array([0, 0, thk * 0.35]), mat=pmat, emissive=0.40, cast_shadow=False, sort_anchor=anc_port)
            sc.add_light(np.array(pos) + pmat @ np.array([0, h * 0.5, 0.45 * s]), color=p_col, intensity=0.85, radius=3.5, halo=0.16 * s)
            if opsi.get("siluet") == "rusa":
                sil_c = (58, 52, 48)
                so_z = thk * 0.56
                # Mantel ramping + leher + kepala oval + dua mata putih kecil + tanduk bercabang 3 ranting
                sc.extrude_2d(coat_2d(0.24 * s, 0.38 * s, h * 0.45, 0.04 * s), 0.014 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([0, 0.01 * s, so_z]), mat=pmat, cast_shadow=False, sort_anchor=anc_sil)
                sc.extrude_2d(rrect_2d(0.0, h * 0.48, 0.08 * s, 0.12 * s, 0.02 * s), 0.014 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([0, 0, so_z]), mat=pmat, cast_shadow=False, sort_anchor=anc_sil)
                sc.extrude_2d(circle_2d(0.0, h * 0.54, 0.115 * s, 0.12 * s, 20), 0.014 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([0, 0, so_z]), mat=pmat, cast_shadow=False, sort_anchor=anc_sil)
                for ex in (-0.042 * s, 0.042 * s):
                    sc.extrude_2d(circle_2d(ex, h * 0.545, 0.013 * s, 0.016 * s, 10), 0.010 * s, PUTIH, PUTIH, PUTIH, origin=np.array(pos) + pmat @ np.array([0, 0, so_z + 0.01 * s]), mat=pmat, emissive=0.6, cast_shadow=False, sort_anchor=anc_sil + pmat @ np.array([0, 0, 0.012 * s], dtype=np.float32))
                for sx in (-1, 1):
                    # Batang tanduk utama + 2 cabang ranting
                    sc.extrude_2d(rrect_2d(0.0, 0.12 * s, 0.026 * s, 0.25 * s, 0.010 * s), 0.012 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([sx * 0.05 * s, h * 0.59, so_z]), mat=pmat @ euler_mat(0, 0, sx * -26), cast_shadow=False, sort_anchor=anc_sil)
                    sc.extrude_2d(rrect_2d(0.0, 0.06 * s, 0.020 * s, 0.12 * s, 0.008 * s), 0.012 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([sx * 0.11 * s, h * 0.67, so_z]), mat=pmat @ euler_mat(0, 0, sx * 16), cast_shadow=False, sort_anchor=anc_sil)
                    sc.extrude_2d(rrect_2d(0.0, 0.05 * s, 0.018 * s, 0.10 * s, 0.007 * s), 0.012 * s, sil_c, sil_c, sil_c, origin=np.array(pos) + pmat @ np.array([sx * 0.14 * s, h * 0.72, so_z]), mat=pmat @ euler_mat(0, 0, sx * -46), cast_shadow=False, sort_anchor=anc_sil)

        # Ornamen mahkota di atas pintu (setengah lingkaran / matahari bersinar)
        orn = opsi.get("ornamen")
        if orn == "setengah_lingkaran":
            semi = [(-0.42 * s, 0.0), (0.42 * s, 0.0)] + [(round(0.42 * s * math.cos(math.pi * i / 20), 5), round(0.42 * s * math.sin(math.pi * i / 20), 5)) for i in range(21)]
            sc.extrude_2d(semi, thk * 0.72, opsi.get("warna_ornamen", HIJAU), opsi.get("warna_ornamen", HIJAU), None, origin=np.array(pos) + pmat @ np.array([0, h + 0.09 * s, -0.02 * s]), mat=pmat, sort_anchor=anc_frame, drop_shadow=0.18)
        elif orn == "matahari":
            for k in range(9):
                ang = -72 + k * 18
                ar = math.radians(ang)
                ray_o = np.array(pos) + pmat @ np.array([math.sin(ar) * (w * 0.56), h * 0.65 + math.cos(ar) * (h * 0.43), -0.03 * s])
                sc.extrude_2d(((-0.085 * s, 0.0), (0.085 * s, 0.0), (0.0, 0.56 * s)), 0.028 * s, KUNING, KUNING, None, origin=ray_o, mat=pmat @ euler_mat(0, 0, -ang), sort_anchor=anc_frame, drop_shadow=0.18)

        # Daun pintu berengsel di kiri (-w*0.44) + panel karton timbul
        leaf = arch_2d(w * 0.88, h * 0.94, n_arc=28)
        hinge_off = np.array([-w * 0.44, 0.0, thk * 0.55], dtype=np.float32)
        leaf_mat = pmat @ euler_mat(0.0, -e_io(buka) * 102.0, 0.0)
        leaf_origin = np.array(pos) + pmat @ hinge_off
        leaf_base = leaf_origin - leaf_mat @ np.array([-w * 0.44, 0.0, 0.0])
        lc = leaf_base + leaf_mat @ np.array([0.0, h * 0.48, 0.02 * s], dtype=np.float32)
        sc.extrude_2d(leaf, 0.040 * s, col_door, gelap(col_door, 0.14), None, origin=leaf_base, mat=leaf_mat, sort_anchor=lc)
        # Panel dalam berlapis pada daun pintu
        panel = arch_2d(w * 0.64, h * 0.72, n_arc=22)
        sc.extrude_2d(panel, 0.012 * s, terang(col_door, 0.10), terang(col_door, 0.06), None, origin=leaf_base + leaf_mat @ np.array([0.0, h * 0.10, 0.022 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=lc + leaf_mat @ np.array([0, 0, 0.015 * s], dtype=np.float32), drop_shadow=0.18)
        # Gagang pintu kuning
        knob_pos = leaf_base + leaf_mat @ np.array([w * 0.34, h * 0.46, 0.036 * s])
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.045 * s, 0.045 * s, 18), 0.028 * s, KUNING, KUNING, None, origin=knob_pos, mat=leaf_mat, cast_shadow=False, sort_anchor=lc + leaf_mat @ np.array([0, 0, 0.045 * s], dtype=np.float32), drop_shadow=0.22)
        if opsi.get("jendela_bulat"):
            win_pos = leaf_base + leaf_mat @ np.array([0.0, h * 0.64, 0.030 * s])
            w_anc = lc + leaf_mat @ np.array([0, 0, 0.030 * s], dtype=np.float32)
            w_anc2 = lc + leaf_mat @ np.array([0, 0, 0.042 * s], dtype=np.float32)
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.21 * s, 0.21 * s, 24), 0.014 * s, PUTIH, PUTIH, None, origin=win_pos, mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc, drop_shadow=0.18)
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.165 * s, 0.165 * s, 24), 0.014 * s, BIRU_MUDA, BIRU_MUDA, None, origin=win_pos + leaf_mat @ np.array([0, 0, 0.008 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc2)
            # Palang + jendela bulat
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.34 * s, 0.026 * s, 0.008 * s), 0.014 * s, PUTIH, PUTIH, None, origin=win_pos + leaf_mat @ np.array([0, 0, 0.014 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc2, drop_shadow=0.14)
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.026 * s, 0.34 * s, 0.008 * s), 0.014 * s, PUTIH, PUTIH, None, origin=win_pos + leaf_mat @ np.array([0, 0, 0.014 * s]), mat=leaf_mat, cast_shadow=False, sort_anchor=w_anc2, drop_shadow=0.14)

    elif jenis in ("kartu_pita", "label_kertas"):
        w = float(opsi.get("lebar", 1.32)) * s
        h = float(opsi.get("tinggi", 0.44)) * s
        sc.extrude_2d(rrect_2d(0.0, 0.0, w, h, 0.03 * s), 0.046 * s, PUTIH, PUTIH, KERTAS_TEPI, origin=pos, mat=mat, bias=-1.4, sort_anchor=pos, cast_shadow=bool(opsi.get("bayangan", False)), drop_shadow=0.20)
        tex = _plaque_texture(opsi.get("teks_besar", ""), opsi.get("teks_kecil", ""), opsi.get("warna_aksen", MERAH))
        pts = _world_quad(pos, mat, [(-w * 0.49, h * 0.48, 0.028 * s), (w * 0.49, h * 0.48, 0.028 * s), (w * 0.49, -h * 0.48, 0.028 * s), (-w * 0.49, -h * 0.48, 0.028 * s)])
        sc.textured_quad(pts, tex, emissive=0.04, bias=-1.5)

    elif jenis == "hp_kertas":
        # Smartphone karton berlapis 8 lembar (extrude_2d ber-sort_anchor bebas Z-fighting!)
        pw, pl = 2.6 * s, 4.1 * s
        rmat_flat = mat @ euler_mat(-90.0, 0.0, 0.0)
        o_base = np.array(pos, dtype=np.float32)
        layer_cols = [MINT_MUDA, KRIM, MINT, KRIM, MINT_MUDA, KRIM, MINT]
        for i, lc in enumerate(layer_cols):
            yi = (0.016 + i * 0.028) * s
            p_l = o_base + mat @ np.array([0.0, yi, 0.0])
            sc.extrude_2d(rrect_2d(0.0, 0.0, pw, pl, 0.28 * s, n_corner=5), 0.024 * s, lc, lc, None, origin=p_l, mat=rmat_flat, cast_shadow=(i == 0), sort_anchor=p_l)
        # Tab pembatas warna biru & kuning menonjol di samping tumpukan
        for side, tz, tcol in ((-1, -0.6 * s, BIRU), (1, 0.45 * s, KUNING)):
            tl_o = o_base + mat @ np.array([side * (pw * 0.52), 0.13 * s, tz])
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.24 * s, 0.62 * s, 0.06 * s), 0.022 * s, tcol, tcol, None, origin=tl_o, mat=rmat_flat, cast_shadow=False, sort_anchor=o_base + mat @ np.array([0.0, 0.13 * s, 0.0]))

        # Bezel biru tua + layar putih gading
        bz_o = o_base + mat @ np.array([0.0, 0.218 * s, 0.0])
        sc.extrude_2d(rrect_2d(0.0, 0.0, pw * 0.96, pl * 0.96, 0.26 * s, n_corner=5), 0.024 * s, BIRU_TUA, BIRU_TUA, None, origin=bz_o, mat=rmat_flat, cast_shadow=False, sort_anchor=bz_o)
        scr_o = o_base + mat @ np.array([0.0, 0.240 * s, 0.0])
        sc.extrude_2d(rrect_2d(0.0, 0.0, pw * 0.86, pl * 0.88, 0.18 * s, n_corner=5), 0.016 * s, (250, 248, 244), (250, 248, 244), None, origin=scr_o, mat=rmat_flat, cast_shadow=False, sort_anchor=scr_o)

        # Video player card merah-koral + segitiga putih + progress bar
        p_ui = o_base + mat @ np.array([0.0, 0.258 * s, 0.0])
        sc.extrude_2d(rrect_2d(0.0, 0.95 * s, pw * 0.76, pl * 0.27, 0.10 * s, n_corner=4), 0.014 * s, KORAL, KORAL, None, origin=p_ui, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui, drop_shadow=0.18)
        p_ui2 = o_base + mat @ np.array([0.0, 0.272 * s, 0.0])
        sc.extrude_2d(((-0.14 * s, 0.80 * s), (0.18 * s, 0.96 * s), (-0.14 * s, 1.12 * s)), 0.010 * s, PUTIH, PUTIH, PUTIH, origin=p_ui2, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui2)
        sc.extrude_2d(rrect_2d(0.0, 0.56 * s, pw * 0.66, 0.045 * s, 0.015 * s), 0.008 * s, (248, 214, 206), (248, 214, 206), None, origin=p_ui2, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui2)

        # 4 kartu aplikasi warna pastel (2x2) + 3 titik navigasi bawah
        for ix, iz, col in ((-0.50, 0.12, HIJAU), (0.50, 0.12, KUNING), (-0.50, -0.62, BIRU_MUDA), (0.50, -0.62, PINK)):
            sc.extrude_2d(rrect_2d(ix * s, iz * s, 0.90 * s, 0.56 * s, 0.10 * s, n_corner=4), 0.014 * s, col, col, None, origin=p_ui, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui, drop_shadow=0.16)
        for dx in (-0.28 * s, 0.0, 0.28 * s):
            sc.extrude_2d(circle_2d(dx, -1.28 * s, 0.065 * s, 0.065 * s, 14), 0.010 * s, (218, 212, 202), (218, 212, 202), None, origin=p_ui, mat=rmat_flat, cast_shadow=False, sort_anchor=p_ui)

        # Kartu Play merah pop-up + lencana angka '1' kuning di kanan atas
        pop = clamp(float(opsi.get("pop_up", 1.0)))
        if pop > 0.02:
            rx_card = (1.0 - e_spring(pop)) * 88.0
            cmat = mat @ euler_mat(rx_card, 0.0, 0.0)
            c_o = o_base + mat @ np.array([0.0, 0.26 * s, -0.15 * s])
            c_anc = c_o + cmat @ np.array([0.0, 0.45 * s, 0.0], dtype=np.float32)
            c_anc_front = c_o + cmat @ np.array([0.0, 0.45 * s, +0.038 * s], dtype=np.float32)
            sc.extrude_2d(rrect_2d(0.0, 0.45 * s, 1.08 * s, 0.92 * s, 0.10 * s, n_corner=4), 0.046 * s, MERAH, MERAH, None, origin=c_o, mat=cmat, sort_anchor=c_anc, drop_shadow=0.22)
            sc.extrude_2d(((-0.14 * s, 0.28 * s), (0.20 * s, 0.45 * s), (-0.14 * s, 0.62 * s)), 0.02 * s, PUTIH, PUTIH, PUTIH, origin=c_o + cmat @ np.array([0.0, 0.0, 0.028 * s]), mat=cmat, cast_shadow=False, sort_anchor=c_anc_front, drop_shadow=0.16)
            b_o = c_o + cmat @ np.array([0.52 * s, 0.88 * s, 0.034 * s])
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.19 * s, 0.19 * s, 24), 0.028 * s, KUNING, KUNING, None, origin=b_o, mat=cmat, cast_shadow=False, sort_anchor=c_anc_front, drop_shadow=0.20)
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.046 * s, 0.18 * s, 0.012 * s), 0.012 * s, OUT, OUT, OUT, origin=b_o + cmat @ np.array([0.0, 0.0, 0.022 * s]), mat=cmat, cast_shadow=False, sort_anchor=c_o + cmat @ np.array([0.0, 0.45 * s, +0.058 * s], dtype=np.float32))

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
        # 3 tingkat menara biru bertumpuk + blok rumah jam krem + atap koral + jam kuning 12 garis
        sc.box(np.array(pos) + mat @ np.array([0.0, 1.72 * s, 0.0]), (1.82 * s, 3.44 * s, 1.64 * s), BIRU, mat=mat)
        for fl in range(3):
            fy = (0.42 + fl * 1.05) * s
            sc.box(np.array(pos) + mat @ np.array([0.0, fy - 0.14 * s, 0.0]), (1.96 * s, 0.10 * s, 1.76 * s), KRIM, mat=mat)
            for wx in (-0.42 * s, 0.42 * s):
                w_o = np.array(pos) + mat @ np.array([wx, fy + 0.05 * s, 0.84 * s])
                sc.extrude_2d(arch_2d(0.36 * s, 0.62 * s, 20), 0.04 * s, KRIM, KRIM, None, origin=w_o, mat=mat, cast_shadow=False, sort_anchor=w_o, drop_shadow=0.18)
                sc.extrude_2d(arch_2d(0.26 * s, 0.50 * s, 18), 0.03 * s, BIRU_TUA, BIRU_TUA, None, origin=w_o + mat @ np.array([0, 0.02 * s, 0.022 * s]), mat=mat, cast_shadow=False, sort_anchor=w_o + mat @ np.array([0, 0, 0.025 * s]))
        # Blok rumah jam krem persegi + atap koral
        sc.box(np.array(pos) + mat @ np.array([0.0, 4.26 * s, 0.0]), (2.06 * s, 1.66 * s, 1.74 * s), KRIM, mat=mat)
        sc.extrude_2d(((-1.14 * s, 0.0), (1.14 * s, 0.0), (0.86 * s, 0.56 * s), (-0.86 * s, 0.56 * s)), 1.84 * s, KORAL, KORAL, None, origin=np.array(pos) + mat @ np.array([0.0, 5.08 * s, 0.0]), mat=mat)
        cf_o = np.array(pos) + mat @ np.array([0.0, 4.26 * s, 0.90 * s])
        anc_cf = np.array(pos) + mat @ np.array([0.0, 3.2 * s, 1.35 * s])
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.78 * s, 0.78 * s, 32), 0.06 * s, KUNING, KUNING, None, origin=cf_o, mat=mat, sort_anchor=anc_cf, drop_shadow=0.20)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.63 * s, 0.63 * s, 28), 0.02 * s, (252, 249, 242), (252, 249, 242), None, origin=cf_o + mat @ np.array([0.0, 0.0, 0.034 * s]), mat=mat, cast_shadow=False, sort_anchor=anc_cf + mat @ np.array([0.0, 0.0, 0.03 * s]))
        tick_anc = anc_cf + mat @ np.array([0.0, 0.0, 0.06 * s])
        for k in range(12):
            a = k * math.pi / 6.0
            sc.extrude_2d(rrect_2d(0.0, 0.52 * s, 0.03 * s, 0.09 * s, 0.008 * s), 0.012 * s, BIRU_TUA, BIRU_TUA, None, origin=cf_o + mat @ np.array([0.0, 0.0, 0.048 * s]), mat=mat @ euler_mat(0, 0, -k * 30.0), cast_shadow=False, sort_anchor=tick_anc)
        sc.extrude_2d(rrect_2d(0.0, 0.20 * s, 0.05 * s, 0.42 * s, 0.02 * s), 0.02 * s, BIRU_TUA, BIRU_TUA, BIRU_TUA, origin=cf_o + mat @ np.array([0.0, 0.0, 0.052 * s]), mat=mat @ euler_mat(0, 0, -t * 140.0), cast_shadow=False, sort_anchor=tick_anc, drop_shadow=0.14)
        sc.extrude_2d(rrect_2d(0.0, 0.14 * s, 0.055 * s, 0.30 * s, 0.02 * s), 0.02 * s, OUT, OUT, OUT, origin=cf_o + mat @ np.array([0.0, 0.0, 0.058 * s]), mat=mat @ euler_mat(0, 0, -t * 25.0), cast_shadow=False, sort_anchor=tick_anc, drop_shadow=0.14)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.06 * s, 0.06 * s, 14), 0.024 * s, KUNING, KUNING, None, origin=cf_o + mat @ np.array([0.0, 0.0, 0.064 * s]), mat=mat, cast_shadow=False, sort_anchor=tick_anc)

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
        sc.box(np.array(pos) + mat @ np.array([0.0, 0.72 * s, 0.0]), (0.06 * s, 1.44 * s, 0.06 * s), (62, 62, 72), mat=mat)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.14 * s, 0.14 * s, 20), 0.14 * s, KUNING_MUDA, KUNING_MUDA, KUNING, origin=np.array(pos) + mat @ np.array([0.0, 1.52 * s, 0.0]), mat=mat, emissive=0.75)

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
