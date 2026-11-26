# -*- coding: utf-8 -*-
"""
dunia.py - 12 set diorama 3D Pop-Up Paper Craft berlapis detail & mekanik lipat buku pop-up nyata.

Mekanik kinetik buku pop-up:
  * meja_hp         : HP buku tebal 10 lapis + Play pop-up + transformasi pintu '5 MENIT' + plaza di baliknya
  * kota_jam        : Menara Jam & 18 gedung BANGKIT 90° dari rebah (pop_kota), flip '1 JAM',
                      gang arkade & lampu jalan BANGKIT 90° (pop_gang), lampion kuning di balik pintu merah
  * ruang_pintu     : Kamar garis hijau + pohon pinus kertas + pintu biru BANGKIT 90° dari lantai (pop_pintu_biru)
  * panggung_kertas : Panggung 1-lokasi berengsel HALAMAN BUKU (dinding polkadot kucing & tirai malam berayun
                      terbuka seperti halaman buku, bulan & 3 ikan turun pakai tali, sinar matahari mekar!)
  * labirin_pintu   : 3 pintu koridor domino (domino_pintu), gelombang 26 pintu mini, & seluruh dinding
                      labirin MELIPAT RATA ke lembaran kertas (rebah_labirin)
  * lipat_meja      : 3 TAHAP LIPATAN ORIGAMI 3D NYATA (atas→bawah, kanan→kiri, atas→bawah) menjadi HP tebal!
"""
import math
import numpy as np
from paper import (
    OUT, KERTAS_TEPI, PUTIH, KRIM, MEJA, HITAM, KORAL, MERAH, MERAH_TUA, BIRU, BIRU_TUA,
    BIRU_MUDA, BIRU_MALAM, MINT, MINT_MUDA, TEAL, PINK, SALMON, KUNING, KUNING_MUDA,
    ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA, UNGU, NAVY, ABU,
    clamp, prog, lerp, e_io, e_out, e_spring, euler_mat, gelap, terang,
    circle_2d, rrect_2d, arch_2d, star_2d, crescent_2d,
)
import benda as BD

LATAR_ALIAS = {
    "meja": "meja_hp", "kota": "kota_jam", "kamar_pintu": "ruang_pintu",
    "panggung": "panggung_kertas", "labirin": "labirin_pintu", "lipat": "lipat_meja",
    "kamar": "kamar_kertas", "sekolah": "sekolah_kertas", "sekolah_luar": "sekolah_kertas",
    "kelas": "kelas_kertas", "taman": "taman_kertas", "kafe": "kafe_kertas", "kantin": "kafe_kertas",
}


def _studio_lights(sc, floor_col=MEJA, wall_top=(238, 224, 198), wall_bot=(226, 208, 180)):
    sc.set_sky(
        wall_top, wall_bot,
        (0.62, 0.60, 0.56), (0.46, 0.41, 0.35),
        [-0.64, 0.60, 0.48], [1.08, 0.99, 0.86], 0.56, wall_bot,
    )
    sc.shadow_floor_y = 0.0
    sc.floor_shadow_col = tuple(int(c * 0.72) for c in floor_col)
    sc.use_shadow_map = True
    sc.shadow_strength = 1.0
    sc.shadow_tint = (0.28, 0.31, 0.36)
    sc.shadow_blur = 1.6
    sc.use_ssao = True
    sc.ssao_strength = 0.38


def _paper_cloud(sc, pos, s=1.0):
    px, py, pz = pos
    anc = np.array([px, py, pz], dtype=np.float32)
    sc.extrude_2d(circle_2d(0.0, 0.0, 0.68 * s, 0.34 * s, 22), 0.06 * s, PUTIH, PUTIH, None, origin=(px, py, pz), sort_anchor=anc, cast_shadow=False)
    sc.extrude_2d(circle_2d(-0.42 * s, -0.06 * s, 0.36 * s, 0.26 * s, 18), 0.06 * s, PUTIH, PUTIH, None, origin=(px, py, pz + 0.01), sort_anchor=anc, cast_shadow=False)
    sc.extrude_2d(circle_2d(0.42 * s, -0.06 * s, 0.36 * s, 0.26 * s, 18), 0.06 * s, PUTIH, PUTIH, None, origin=(px, py, pz + 0.01), sort_anchor=anc, cast_shadow=False)


# ================================================================== 1. MEJA HP
def set_meja_hp(sc, t, o):
    """Meja kerajinan hangat: jam weker kiri + HP buku 10 lapis utuh + Play pop-up + pintu '5 MENIT' (loop mulus dengan ending!)."""
    _studio_lights(sc, MEJA)
    sc.tiled_plane(-9.0, -9.0, 9.0, 9.0, 0.0, MEJA, tile=2.0)
    sc.box((0.0, 2.8, -5.8), (18.0, 5.6, 0.16), (236, 222, 198), cast_shadow=False)
    sc.box((0.0, 0.28, -5.68), (18.0, 0.56, 0.08), (218, 200, 174), cast_shadow=False)

    # Jam weker mint-hijau mengintip pas di sisi kiri layar (identik REF s01 & s27-s30!)
    BD.draw_prop(sc, "jam_weker_kertas", (-2.05, 0.0, -0.35), rot=(0.0, 26.0, 0.0), s=1.48, t=t, putar=True, warna=(92, 152, 128))

    pop_door = clamp(float(o.get("pop_door", 1.0 if o.get("mode_pintu", False) else 0.0)))
    pop_play = clamp(float(o.get("pop_play", 0.0 if pop_door > 0.05 else clamp(t * 2.4, 0.0, 1.0))))
    play_vis = pop_play * (1.0 - clamp(pop_door * 3.0, 0.0, 1.0))
    BD.draw_prop(sc, "hp_kertas", (0.28, 0.0, 0.0), rot=(0.0, -4.0, 0.0), s=0.96, t=t, pop_up=play_vis, play_dx=-0.30)

    if pop_door > 0.02:
        buka = float(o.get("buka_pintu", 0.0))
        flip_j = float(o.get("flip_judul", 0.0))
        BD.draw_prop(sc, "pintu_kertas", (0.28, 0.40, -0.28), rot=(0.0, -4.0, 0.0), s=0.96, warna_bingkai=BIRU, warna_pintu=KORAL, pop_up=pop_door, buka=buka, play_door=True)
        if flip_j > 0.02:
            BD.draw_prop(sc, "kartu_pita", (0.28, 2.55, -0.22), rot=(0.0, -4.0, 0.0), s=0.90, flip=flip_j, teks_besar="5", teks_kecil="MENIT", warna_aksen=MERAH)
        if buka > 0.04:
            # Hamparan peta kota pop-up yang masih rebah rata di balik pintu '5 MENIT' (REF s02-s03!)
            sc.box((0.28, 0.39, -2.55), (3.4, 0.02, 4.4), (236, 222, 194), cast_shadow=False)
            sc.extrude_2d(circle_2d(0.0, 0.0, 1.05, 1.05, 28), 0.015, KUNING, KUNING, None, origin=(0.28, 0.405, -1.65), rot=(-90.0, 0.0, 0.0), cast_shadow=False)
            for tx, tz, tc in ((-0.35, -1.15, KUNING_MUDA), (0.92, -1.15, MINT), (-0.35, -2.35, BIRU_MUDA), (0.92, -2.35, SALMON), (0.28, -3.25, (94, 128, 178))):
                sc.rbox((tx, 0.41, tz), (0.68, 0.018, 0.72), tc, roundness=0.14, seg=1, cast_shadow=False)


# ================================================================== 2. KOTA JAM
def set_kota_jam(sc, t, o):
    """Alun-alun Kota Jam POP-UP: Menara Jam & 18 gedung BANGKIT 90° dari lantai + Gang Arkade BANGKIT 90° + Lampion!"""
    _studio_lights(sc, MEJA, (238, 226, 202), (228, 214, 188))
    sc.set_sky((238, 226, 202), (228, 214, 188), (0.62, 0.60, 0.56), (0.45, 0.40, 0.34), [-0.66, 0.58, 0.48], [1.08, 0.98, 0.85], 0.58, (228, 214, 188))
    sc.tiled_plane(-16.0, -20.0, 16.0, 14.0, 0.0, (228, 212, 184), tile=2.4)
    sc.box((0.0, 0.012, -2.0), (2.9, 0.015, 22.0), (240, 228, 204), bias=0.85, cast_shadow=False)
    sc.extrude_2d(circle_2d(0.0, 0.0, 2.05, 2.05, 32), 0.02, KUNING, KUNING, None, origin=(0.0, 0.016, 2.8), rot=(-90.0, 0.0, 0.0), bias=0.75, cast_shadow=False)

    pop_kota = clamp(float(o.get("pop_kota", 1.0)))
    if pop_kota > 0.2:
        _paper_cloud(sc, (-3.6, 6.8, -12.5), 1.35 * e_out(pop_kota))
        _paper_cloud(sc, (3.8, 6.2, -12.0), 1.2 * e_out(pop_kota))

    # Menara jam biru berengsel pop-up 90° dari rebah (REF s03.0 -> s03.4!)
    BD.draw_prop(sc, "menara_jam", (0.0, 0.0, -9.0), s=1.16, t=t, pop_up=pop_kota)
    jam_pop = clamp(float(o.get("pop_jam", 0.0)), 0.0, 1.0)
    if jam_pop > 0.03:
        BD.draw_prop(sc, "kartu_pita", (0.0, 6.95, -7.85), s=1.92, flip=jam_pop, teks_besar="1", teks_kecil="JAM", warna_aksen=MERAH, bayangan=True)

    # 18 Gedung pastel BANGKIT 90° dari rebah secara bergelombang (pop_kota 0 -> 1!)
    buildings = [
        (-2.8, -11.5, 1.7, 3.8, 1.6, KUNING_MUDA, KORAL), (-4.9, -11.0, 1.9, 4.6, 1.7, PUTIH, BIRU),
        (2.8, -11.4, 1.7, 3.6, 1.6, MINT_MUDA, KUNING),   (4.9, -10.8, 1.9, 4.5, 1.7, SALMON, BIRU),
        (-2.6, -8.8, 1.6, 3.2, 1.5, PUTIH, KUNING),       (-4.4, -8.2, 1.8, 4.3, 1.7, SALMON, MERAH),
        (-6.3, -7.4, 1.9, 3.7, 1.7, BIRU_MUDA, KUNING),   (-2.9, -6.5, 1.7, 2.9, 1.5, MINT, KORAL),
        (-4.8, -5.8, 1.8, 3.9, 1.6, KUNING_MUDA, BIRU),   (2.6, -8.6, 1.6, 3.4, 1.5, SALMON, MINT),
        (4.5, -8.0, 1.9, 4.2, 1.7, MINT_MUDA, KORAL),     (6.3, -7.2, 1.8, 3.5, 1.6, KUNING_MUDA, BIRU),
        (2.9, -6.3, 1.7, 3.0, 1.5, BIRU_MUDA, KUNING),    (4.8, -5.6, 1.8, 3.8, 1.6, PUTIH, KORAL),
        (-3.0, -4.0, 1.7, 2.8, 1.6, KORAL, KUNING),       (-4.8, -3.2, 1.8, 3.5, 1.6, PUTIH, MINT),
        (-3.0, -1.6, 1.7, 2.6, 1.6, MINT_MUDA, BIRU),     (-3.0, 0.8, 1.7, 2.8, 1.6, KUNING_MUDA, KORAL),
    ]
    for bi, (bx, bz, bw, bh, bd, col, rcol) in enumerate(buildings):
        p_b = clamp(pop_kota * 1.35 - (bi % 4) * 0.08, 0.0, 1.0)
        if p_b <= 0.01:
            continue
        b_rx = (1.0 - e_spring(p_b)) * -88.0
        bmat = euler_mat(b_rx, 0.0, 0.0)
        base_b = np.array([bx, 0.0, bz], dtype=np.float32)
        sc.box(base_b + bmat @ np.array([0.0, bh * 0.5, 0.0]), (bw, bh, bd), col, mat=bmat)
        sc.box(base_b + bmat @ np.array([0.0, bh + 0.14, 0.0]), (bw * 1.06, 0.28, bd * 1.06), rcol, mat=bmat)
        wcol = MERAH_TUA if col in (PUTIH, KUNING_MUDA) else BIRU_TUA
        for wy in (0.75, 1.45, 2.15, 2.85, 3.55):
            if wy < bh - 0.42:
                for wx_o in (-bw * 0.23, bw * 0.23):
                    sc.box(base_b + bmat @ np.array([wx_o, wy, bd * 0.51]), (0.28, 0.38, 0.05), wcol, mat=bmat, bias=-0.02, cast_shadow=False)
                side_x = -bw * 0.51 if bx > 0 else bw * 0.51
                for wz_o in (-bd * 0.22, bd * 0.22):
                    sc.box(base_b + bmat @ np.array([side_x, wy, wz_o]), (0.05, 0.38, 0.28), wcol, mat=bmat, bias=-0.02, cast_shadow=False)

    # ---------------- GANG DERETAN PINTU BERENGSEL POP-UP 90° (pop_gang 0 -> 1, REF s05.8-s06.2!) ----------------
    pop_gang = clamp(float(o.get("pop_gang", 1.0)))
    if pop_gang > 0.02:
        g_ang = (1.0 - e_spring(pop_gang)) * 88.0
        # Engsel dinding arkade kanan sepanjang garis x = 1.92, y = 0 (berputar di sumbu Z dari rebah keluar kanan!)
        gmat_r = euler_mat(0.0, 0.0, -g_ang)
        g_orig = np.array([1.92, 0.0, 0.0], dtype=np.float32)

        sc.box(g_orig + gmat_r @ np.array([0.0, 1.75, -2.05]), (0.22, 3.5, 5.5), (242, 232, 212), mat=gmat_r)
        sc.arch_wall(g_orig + gmat_r @ np.array([0.0, 0.0, 1.80]), 2.2, 3.5, 1.05, 1.92, thickness=0.22, wall_col=(242, 232, 212), trim_col=None, mat=gmat_r @ euler_mat(0.0, -90.0, 0.0), cast_shadow=True, bias=0.45)
        sc.box(g_orig + gmat_r @ np.array([0.0, 1.75, 3.70]), (0.22, 3.5, 1.6), (242, 232, 212), mat=gmat_r)
        for cz in np.linspace(-4.4, 4.0, 13):
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.36, 0.28, 18), 0.14, KORAL, KORAL, None, origin=g_orig + gmat_r @ np.array([0.0, 3.52, float(cz)]), mat=gmat_r @ euler_mat(0.0, -90.0, 0.0), cast_shadow=False)

        # Dinding rendah kiri gang bermahkota gelombang hijau-mint ikut bangkit (REF s06.0!)
        gmat_l = euler_mat(0.0, 0.0, +g_ang)
        gl_o = np.array([-2.05, 0.0, 0.0], dtype=np.float32)
        sc.box(gl_o + gmat_l @ np.array([0.0, 1.35, 0.6]), (0.20, 2.7, 7.6), (236, 226, 206), mat=gmat_l)
        for cz in np.linspace(-2.8, 3.8, 9):
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.34, 0.26, 16), 0.12, MINT, MINT, None, origin=gl_o + gmat_l @ np.array([0.0, 2.72, float(cz)]), mat=gmat_l @ euler_mat(0.0, 90.0, 0.0), cast_shadow=False)

        # Interior kamar hijau-putih + karpet pink + LAMPION KERTAS KUNING di balik pintu hero (REF s08.8!)
        sc.box((3.55, 0.016, 1.80), (3.0, 0.02, 3.8), (216, 236, 224), bias=0.82, cast_shadow=False)
        sc.rbox((3.35, 0.028, 1.80), (1.8, 0.018, 2.2), SALMON, roundness=0.28, seg=1, bias=0.78, cast_shadow=False)
        sc.rbox((3.35, 0.036, 1.80), (1.42, 0.016, 1.82), (248, 242, 232), roundness=0.28, seg=1, bias=0.75, cast_shadow=False)
        sc.box((4.95, 1.75, 1.80), (0.14, 3.5, 3.8), (244, 238, 224), cast_shadow=False)
        for sz in (0.4, 1.0, 1.6, 2.2, 2.8, 3.4):
            sc.box((4.86, 1.75, sz), (0.04, 3.3, 0.24), (194, 222, 206), cast_shadow=False)
        sc.box((3.55, 1.75, -0.05), (3.0, 3.5, 0.14), (244, 238, 224), cast_shadow=False)
        # Lampion bulat kuning bergelantung di dalam pintu (REF s08.8!)
        sc.box((2.75, 2.95, 2.25), (0.018, 1.2, 0.018), (196, 186, 170), cast_shadow=False)
        sc.rbox((2.75, 2.15, 2.25), (0.44, 0.42, 0.44), KUNING_MUDA, roundness=0.85, seg=2, emissive=0.22, cast_shadow=False)

        door_specs = [
            (1.73, 1.80, KORAL, KORAL, KUNING, 1),
            (1.73, -0.35, PUTIH, SALMON, KORAL, 0),
            (1.73, -2.35, MINT, MINT, KUNING, 0),
            (1.73, -4.15, KORAL, PUTIH, MINT, 0),
        ]
        for dx, dz, fcol, dcol, ocol, is_hero in door_specs:
            buka = float(o.get("buka_pintu_kanan", 0.0)) if is_hero else 0.0
            BD.draw_prop(sc, "pintu_kertas", (dx, 0.0, dz), rot=(0.0, -90.0, 0.0), s=0.92, warna_bingkai=fcol, warna_pintu=dcol, pop_up=pop_gang, buka=buka, ornamen="setengah_lingkaran", warna_ornamen=ocol, cahaya_portal=False)

        for lz in (2.85, 0.72, -1.35, -3.25):
            BD.draw_prop(sc, "lampu_taman_kertas", (1.28, 0.0, lz), s=0.86, pop_up=pop_gang)
            BD.draw_prop(sc, "lampu_taman_kertas", (-1.55, 0.0, lz + 0.35), s=0.86, pop_up=pop_gang)
        for pz in (0.25, -1.78, -3.65):
            if pop_gang > 0.2:
                ps = e_spring(pop_gang)
                sc.rbox((1.35, 0.18 * ps, pz), (0.34, 0.34 * ps, 0.42), (108, 148, 86), roundness=0.22, seg=1)
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.24 * ps, 0.22 * ps, 16), 0.16, HIJAU, HIJAU, None, origin=(1.35, 0.44 * ps, pz))


# ================================================================== 3. RUANG PINTU
def set_ruang_pintu(sc, t, o):
    """Kamar garis hijau + pohon pinus kertas + pintu biru BANGKIT 90° dari lantai + 'SATU PINTU lagi' flip."""
    _studio_lights(sc, MINT_MUDA, (226, 238, 228), (212, 228, 218))
    sc.tiled_plane(-5.5, -5.5, 5.5, 5.5, 0.0, (216, 236, 224), tile=1.5)
    sc.rbox((-0.15, 0.015, 0.45), (3.3, 0.02, 2.3), SALMON, roundness=0.30, seg=1, bias=0.85, cast_shadow=False)
    sc.rbox((-0.15, 0.024, 0.45), (2.85, 0.02, 1.88), (246, 240, 230), roundness=0.30, seg=1, bias=0.75, cast_shadow=False)

    # Dinding kiri bergaris vertikal hijau-mint + wainscoting + lukisan gunung + POHON PINUS KERTAS (REF s09.6!)
    sc.box((-2.55, 2.2, 0.0), (0.16, 4.4, 9.0), (244, 238, 224), cast_shadow=False)
    for sz in np.linspace(-3.6, 3.6, 13):
        sc.box((-2.45, 2.2, float(sz)), (0.04, 4.2, 0.24), (194, 222, 206), bias=-0.01, cast_shadow=False)
    sc.box((-2.43, 0.36, 0.0), (0.06, 0.72, 9.0), (144, 186, 164), bias=-0.02, cast_shadow=False)
    sc.extrude_2d(rrect_2d(0.0, 0.0, 1.38, 1.10, 0.05), 0.06, TEAL, TEAL, None, origin=(-2.39, 2.18, -0.35), rot=(0.0, 90.0, 0.0), cast_shadow=True)
    sc.extrude_2d(rrect_2d(0.0, 0.0, 1.18, 0.90, 0.03), 0.03, PUTIH, PUTIH, None, origin=(-2.35, 2.18, -0.35), rot=(0.0, 90.0, 0.0), cast_shadow=False)
    sc.extrude_2d(((-0.42, 0.0), (0.0, 0.48), (0.42, 0.0)), 0.025, KUNING, KUNING, None, origin=(-2.32, 1.76, -0.35), rot=(0.0, 90.0, 0.0), cast_shadow=False)

    # Pohon pinus kertas silang 3D di pojok kiri dekat dinding (REF s09.6!)
    sc.box((-1.92, 0.16, -1.42), (0.12, 0.32, 0.12), COKLAT)
    for ry_t in (0.0, 90.0):
        sc.extrude_2d(((-0.38, 0.0), (0.38, 0.0), (0.0, 1.05)), 0.03, HIJAU_TUA, HIJAU_TUA, None, origin=(-1.92, 0.28, -1.42), rot=(0.0, ry_t, 0.0))

    # Dinding belakang berlubang pintu nyata
    sc.arch_wall((0.0, 0.0, -2.20), 6.8, 4.4, 1.02, 1.94, thickness=0.18, wall_col=(244, 238, 224), trim_col=None, cast_shadow=True, bias=0.45)
    for sx in (-2.45, -1.90, -1.35, 1.35, 1.90, 2.45):
        sc.box((sx, 2.2, -2.10), (0.24, 4.2, 0.03), (194, 222, 206), bias=0.38, cast_shadow=False)
    for sx in (-1.85, 1.85):
        sc.box((sx, 0.36, -2.08), (2.4, 0.72, 0.05), (144, 186, 164), bias=0.35, cast_shadow=False)

    # Pintu biru BANGKIT 90° keluar dari lantai (pop_pintu_biru: 0 -> 1, REF s10.0-s10.4!)
    pop_biru = clamp(float(o.get("pop_pintu_biru", 1.0)))
    buka = float(o.get("buka_pintu", 0.0))
    flip_j = float(o.get("flip_judul", 0.0))
    if pop_biru > 0.02:
        BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, -2.01), s=1.0, warna_bingkai=BIRU, warna_pintu=BIRU_TUA, pop_up=pop_biru, buka=buka, jendela_bulat=True, ornamen="setengah_lingkaran", warna_ornamen=(138, 192, 162))
    if flip_j > 0.02:
        BD.draw_prop(sc, "kartu_pita", (0.0, 2.92, -1.86), s=1.12, flip=flip_j, teks_besar="SATU PINTU", teks_kecil="lagi", warna_aksen=MERAH)

    # Interior karpet merah & tirai emas hangat di BALIK pintu biru (REF s11.2-s12.4!)
    sc.box((0.0, 0.016, -3.55), (3.8, 0.02, 2.6), (232, 184, 92), cast_shadow=False)
    sc.box((0.0, 0.026, -3.45), (1.15, 0.02, 2.4), KORAL, cast_shadow=False)
    sc.box((0.0, 1.85, -4.65), (4.6, 3.8, 0.16), (234, 188, 96), cast_shadow=False)
    for cx in (-1.45, -0.95, 0.95, 1.45):
        sc.box((cx, 1.85, -4.45), (0.28, 3.6, 0.12), (218, 152, 58), cast_shadow=False)
    sc.box((-1.65, 1.65, -3.45), (0.14, 3.3, 2.5), KORAL, cast_shadow=False)
    sc.box((1.65, 1.65, -3.45), (0.14, 3.3, 2.5), (222, 168, 64), cast_shadow=False)


# ================================================================== 4. PANGGUNG KERTAS (HALAMAN BUKU BERAYUN!)
def set_panggung_kertas(sc, t, o):
    """
    1 PANGGUNG TEATER LIPAT BUKU (x = 0.0) — TANPA HARD CUT (REF s12.6-s17.5!):
      * trans_malam (0->1): dinding polkadot kucing berayun terbuka seperti halaman buku, podium melipat,
                            tirai malam muncul, bukit naik, & bulan/ikan TURUN pakai tali (drop_malam 0->1)!
      * trans_fajar (0->1): tirai malam & bukit berayun terbuka, bulan/ikan naik ke atas,
                            dinding fajar oranye & 11 sinar matahari mekar keluar (ray_scale 0->1)!
    """
    trans_malam = clamp(float(o.get("trans_malam", 0.0)))
    drop_malam = clamp(float(o.get("drop_malam", trans_malam)))
    trans_fajar = clamp(float(o.get("trans_fajar", 0.0)))
    ray_scale = clamp(float(o.get("ray_scale", trans_fajar)))

    # Latar langit berubah halus mengikuti fase panggung
    if trans_fajar > 0.5:
        sky_c = (224, 118, 70)
    elif trans_malam > 0.35:
        sky_c = (34, 56, 114)
    else:
        sky_c = (178, 102, 60)
    _studio_lights(sc, (164, 114, 74), sky_c, sky_c)
    sc.set_sky(sky_c, sky_c, (0.58, 0.56, 0.54), (0.42, 0.36, 0.30), [-0.56, 0.56, 0.61], [1.06, 0.96, 0.84], 0.56, sky_c)
    sc.bloom_strength = 0.38 if (trans_malam > 0.2 or trans_fajar > 0.2) else 0.20
    sc.shadow_strength = 0.95
    sc.shadow_tint = (0.30, 0.33, 0.39)

    # Lantai papan kayu panggung
    sc.tiled_plane(-6.0, -2.5, 6.0, 5.2, 0.0, (172, 120, 78), tile=1.5)
    for kz in np.linspace(-1.7, 4.2, 14):
        sc.box((0.0, 0.014, float(kz)), (12.0, 0.01, 0.028), (138, 92, 58), bias=0.82, cast_shadow=False)

    # ---------- LAPIS 3 (BELAKANG — FAJAR MATAHARI, z = -1.66) ----------
    if trans_fajar > 0.02:
        sc.box((0.0, 2.2, -1.68), (5.4, 4.4, 0.12), (222, 112, 66), cast_shadow=False)
        for sx in np.linspace(-2.2, 2.2, 9):
            sc.box((float(sx), 2.2, -1.60), (0.24, 4.4, 0.03), (236, 146, 92), bias=-0.01, cast_shadow=False)
        BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, -1.02), s=1.04, warna_bingkai=(76, 102, 134), warna_pintu=BIRU_TUA, tanpa_daun=True, cahaya_portal=True, warna_portal=(254, 224, 146), emissive_portal=0.52, ornamen="matahari", ray_scale=ray_scale)

    # ---------- LAPIS 2 (TENGAH — TIRAI MALAM BERAYUN + BUKIT + BULAN & IKAN BERTALI, z = -1.52) ----------
    if trans_malam > 0.02 and trans_fajar < 0.98:
        # Halaman tirai biru berengsel di kiri x = -2.45 (berayun membuka KE BELAKANG +108° saat trans_fajar 0 -> 1!)
        hinge2 = np.array([-2.45, 0.0, -1.52], dtype=np.float32)
        m2 = euler_mat(0.0, +108.0 * e_io(trans_fajar), 0.0)
        sc.box(hinge2 + m2 @ np.array([2.45, 2.2, 0.0]), (4.9, 4.4, 0.08), BIRU_MALAM, mat=m2, cast_shadow=False)
        for cx in np.linspace(0.35, 4.55, 11):
            sc.box(hinge2 + m2 @ np.array([float(cx), 2.2, 0.05]), (0.18, 4.4, 0.03), (42, 70, 136), mat=m2, cast_shadow=False)

        # Bukit hijau + rumah berlampu BANGKIT saat malam muncul & MELIPAT saat fajar datang!
        hill_p = clamp(trans_malam * 1.4, 0.0, 1.0) * (1.0 - clamp(trans_fajar * 1.6, 0.0, 1.0))
        if hill_p > 0.03:
            hmat = euler_mat((1.0 - e_spring(hill_p)) * 86.0, 0.0, 0.0)
            hills = ((-1.18, -1.16, 1.28, HIJAU_TUA), (1.18, -1.16, 1.28, HIJAU_TUA), (0.0, -1.04, 1.05, (64, 128, 92)))
            for hx, hz, hr, hc in hills:
                semi = [(-hr, 0.0), (hr, 0.0)] + [(round(hr * math.cos(math.pi * i / 22), 5), round(hr * 0.72 * math.sin(math.pi * i / 22), 5)) for i in range(23)]
                sc.extrude_2d(semi, 0.05, hc, hc, None, origin=(hx, 0.0, hz), mat=hmat, cast_shadow=True, cast_wall_shadow=True)
            for rhx, rcol in ((-1.02, KORAL), (0.98, (186, 134, 72))):
                sc.extrude_2d(rrect_2d(0.0, 0.14, 0.26, 0.26, 0.02), 0.04, rcol, rcol, None, origin=np.array([rhx, 0.0, -0.94]) + hmat @ np.array([0.0, 0.24, 0.0]), mat=hmat, cast_shadow=False)
                sc.extrude_2d(((-0.16, 0.0), (0.16, 0.0), (0.0, 0.15)), 0.04, gelap(rcol, 0.2), gelap(rcol, 0.2), None, origin=np.array([rhx, 0.0, -0.94]) + hmat @ np.array([0.0, 0.49, 0.0]), mat=hmat, cast_shadow=False)
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.085, 0.095, 0.01), 0.02, KUNING_MUDA, KUNING_MUDA, None, origin=np.array([rhx, 0.0, -0.91]) + hmat @ np.array([0.0, 0.38, 0.0]), mat=hmat, emissive=0.85, cast_shadow=False)

        # Bulan sabit, bintang, & 3 ikan TURUN pakai tali dari atas (drop_malam) & NAIK kembali (trans_fajar)!
        y_drop = lerp(2.85, 0.0, e_out(drop_malam)) + lerp(0.0, 2.85, e_io(trans_fajar))
        if y_drop < 2.65:
            def _tali(tx, y_bot, tz=-0.82):
                yb = y_bot + y_drop
                if yb < 4.5:
                    sc.box((tx, (4.5 + yb) * 0.5, tz), (0.014, 4.5 - yb, 0.012), (228, 224, 214), cast_shadow=True, cast_wall_shadow=True)

            _tali(-0.42, 2.92, -0.78)
            sc.extrude_2d(crescent_2d(0.46, 0.44, n=26), 0.036, KUNING_MUDA, KUNING_MUDA, None, origin=(-0.36, 2.74 + y_drop, -0.78), rot=(0.0, 0.0, -24.0), cast_shadow=True, cast_wall_shadow=True)
            for sx, sy in ((-1.12, 2.52), (-0.82, 2.12), (0.28, 2.68), (0.72, 2.32), (1.06, 2.75), (-1.38, 1.88), (1.02, 1.78)):
                _tali(sx, sy + 0.07, -0.84)
                sc.extrude_2d(star_2d(0.095, 0.042, 5), 0.024, KUNING, KUNING, None, origin=(sx, sy + y_drop, -0.84), rot=(0.0, math.sin(t * 2 + sx) * 14.0, 0.0), cast_shadow=True, cast_wall_shadow=True)
            for fx, fy, fz, fcol, dir_x in ((-1.12, 2.04, -0.66, (132, 168, 214), 1.0), (0.48, 2.26, -0.70, (162, 192, 226), -1.0), (0.36, 1.66, -0.62, PUTIH, -1.0)):
                _tali(fx, fy + 0.10, fz)
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.24, 0.12, 20), 0.028, fcol, fcol, None, origin=(fx, fy + y_drop, fz), cast_shadow=True, cast_wall_shadow=True)
                sc.extrude_2d(((0.0, 0.0), (dir_x * -0.16, 0.10), (dir_x * -0.16, -0.10)), 0.024, fcol, fcol, None, origin=(fx - dir_x * 0.20, fy + y_drop, fz), cast_shadow=True, cast_wall_shadow=True)
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.020, 0.020, 10), 0.012, OUT, OUT, OUT, origin=(fx + dir_x * 0.12, fy + 0.02 + y_drop, fz + 0.018), cast_shadow=False)

        # Portal rusa emas malam (muncul saat dinding polkadot terbuka, lenyap saat portal fajar menggantikan!)
        if trans_fajar < 0.25:
            BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, -0.95), s=0.96, warna_bingkai=(196, 154, 62), warna_pintu=BIRU_TUA, pop_up=clamp(trans_malam * 1.3, 0.0, 1.0), tanpa_daun=True, cahaya_portal=True, warna_portal=(248, 212, 128), emissive_portal=0.46, siluet="rusa")

    # ---------- LAPIS 1 (DEPAN — RUANG POLKADOT KUCING BERAYUN SEPERTI HALAMAN BUKU, z = -1.35) ----------
    if trans_malam < 0.98:
        # Dinding belakang terakota + dinding polkadot berengsel di kiri x = -1.65 (berayun membuka KE BELAKANG +110°!)
        hinge1 = np.array([-1.65, 0.0, -1.35], dtype=np.float32)
        m1 = euler_mat(0.0, +110.0 * e_io(trans_malam), 0.0)
        sc.box(hinge1 + m1 @ np.array([1.95, 2.1, 0.0]), (4.1, 4.2, 0.08), (178, 102, 60), mat=m1, cast_shadow=False)
        # Panel polkadot kuning di kiri berayun KELUAR KE KIRI (-105°) agar tidak melintang di depan kamera!
        m1_l = euler_mat(0.0, -105.0 * e_io(trans_malam), 0.0)
        sc.box(hinge1 + m1_l @ np.array([0.0, 2.1, 1.45]), (0.08, 4.2, 3.0), (228, 202, 114), mat=m1_l, cast_shadow=False)
        for pz, py, pc in ((0.55, 1.55, KORAL), (1.15, 1.15, MERAH), (0.85, 2.05, HIJAU), (1.75, 1.75, BIRU), (0.35, 0.85, ORANYE)):
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.14, 0.14, 18), 0.02, pc, pc, None, origin=hinge1 + m1_l @ np.array([0.06, py, pz]), mat=m1_l @ euler_mat(0.0, 90.0, 0.0), cast_shadow=False)
        sc.add_light((0.6, 2.4, 1.2), color=(255, 224, 152), intensity=0.52 * (1.0 - trans_malam), radius=4.2, halo=0.0)

        # Podium drum silinder kucing MELIPAT turun ke lantai saat trans_malam -> 1!
        pod_s = 1.0 - e_io(clamp(trans_malam * 1.4, 0.0, 1.0))
        if pod_s > 0.05:
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.62, 0.62, 30), 0.36 * pod_s, KUNING, KUNING, KORAL, origin=(0.0, 0.18 * pod_s, -0.35), rot=(-90.0, 0.0, 0.0))
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.58, 0.58, 28), 0.04 * pod_s, (238, 192, 48), (238, 192, 48), KUNING, origin=(0.0, 0.36 * pod_s, -0.35), rot=(-90.0, 0.0, 0.0), cast_shadow=False)


# ================================================================== 5. LABIRIN PINTU
def set_labirin_pintu(sc, t, o):
    """Labirin 5 koridor + 3 pintu domino (domino_pintu) + 26 pintu pop-up + seluruh dinding REBAH RATA (rebah_labirin)!"""
    _studio_lights(sc, MINT_MUDA, (238, 226, 202), (226, 214, 192))
    sc.set_sky((238, 226, 202), (226, 214, 192), (0.64, 0.63, 0.60), (0.48, 0.45, 0.41), [-0.78, 0.56, 0.28], [1.08, 1.00, 0.88], 0.56, (226, 214, 192))
    sc.shadow_strength = 1.0
    sc.shadow_tint = (0.26, 0.30, 0.35)
    sc.shadow_blur = 1.2

    rebah = clamp(float(o.get("rebah_labirin", 0.0)))
    # Saat labirin rebah, dasar lantai berubah lembut ke meja krem dengan lembar kertas labirin di tengah (REF s23.6-24.0!)
    sc.tiled_plane(-13.0, -16.0, 13.0, 12.0, 0.0, MEJA if rebah > 0.35 else (206, 232, 218), tile=2.2)
    sc.box((0.0, 0.010, -2.85), (10.9, 0.012, 16.5), (210, 234, 220), bias=0.88, cast_shadow=False)
    for gx in (-5.35, -3.95, -2.55, -1.15, 0.0, 1.15, 2.55, 3.95, 5.35):
        sc.box((gx, 0.018, -2.85), (0.03, 0.006, 16.4), (182, 214, 198), bias=0.85, cast_shadow=False)
    for gz in (-10.0, -7.8, -5.6, -3.4, -1.2, 1.0, 3.2, 5.2):
        sc.box((0.0, 0.018, gz), (10.8, 0.006, 0.03), (182, 214, 198), bias=0.85, cast_shadow=False)

    tile_cols = [KORAL, BIRU_MUDA, KUNING, HIJAU, SALMON]
    for ci, cx in enumerate((-4.65, -3.25, -1.85, 0.0, 1.85, 3.25, 4.65)):
        for ri, rz in enumerate((-8.8, -6.6, -4.4, -2.2, 0.0, 2.0)):
            if (ci + ri) % 2 == 0:
                ox = 0.0 if cx == 0.0 else (-0.22 if ri % 2 == 0 else 0.22)
                sc.rbox((cx + ox, 0.022, rz), (0.48, 0.010, 0.52), tile_cols[(ci + ri) % 5], roundness=0.18, seg=1, bias=0.80, cast_shadow=False)

    # 15 Dinding labirin berengsel di dasar y=0 -> MELIPAT RATA 90° saat rebah_labirin 0 -> 1 (REF s23.4-s24.0!)
    wall_h = 1.42
    segs = [
        (-1.15, -2.6, 0.10, 10.4, KORAL, "z"), (1.15, -2.6, 0.10, 10.4, MINT, "z"),
        (-2.55, -2.6, 0.10, 13.0, BIRU, "z"),  (2.55, -2.6, 0.10, 13.0, KORAL, "z"),
        (0.0, -7.8, 2.40, 0.10, KUNING, "x"),
        (-3.95, -2.6, 0.10, 15.8, KUNING, "z"), (3.95, -2.6, 0.10, 15.8, BIRU, "z"),
        (-1.6, -9.4, 4.8, 0.10, KORAL, "x"),    (1.8, -9.4, 4.4, 0.10, HIJAU, "x"),
        (-2.55, 3.9, 2.8, 0.10, BIRU, "x"),     (2.55, 3.9, 2.8, 0.10, KORAL, "x"),
        (-5.35, -2.8, 0.10, 16.4, KORAL, "z"),  (5.35, -2.8, 0.10, 16.4, KUNING, "z"),
        (0.0, -11.0, 10.8, 0.10, BIRU, "x"),    (0.0, 5.3, 10.8, 0.10, KORAL, "x"),
    ]
    for si, (wx, wz, ww, wd, trim, axis) in enumerate(segs):
        r_i = clamp(rebah * 1.45 - (si % 4) * 0.10, 0.0, 1.0)
        ang_f = e_io(r_i) * 88.5
        if axis == "z":
            sgn = -1.0 if wx < 0 else 1.0
            wmat = euler_mat(0.0, 0.0, sgn * ang_f)
        else:
            wmat = euler_mat(ang_f, 0.0, 0.0)
        base_w = np.array([wx, 0.015, wz], dtype=np.float32)
        sc.box(base_w + wmat @ np.array([0.0, wall_h * 0.5, 0.0]), (ww, wall_h, wd), (236, 228, 214), mat=wmat, cast_shadow=(r_i < 0.85))
        sc.box(base_w + wmat @ np.array([0.0, wall_h + 0.032, 0.0]), (ww + 0.03, 0.064, wd + 0.03), trim, mat=wmat, cast_shadow=False)

    # Gerbang masuk koridor (ikut rebah saat labirin melipat rata!)
    if rebah < 0.75:
        BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, 2.65), s=0.96, warna_bingkai=BIRU_TUA, warna_pintu=KUNING, pop_up=1.0 - rebah, tanpa_daun=True)

    # 3 Pintu Koridor Domino (biru -> hijau jendela -> kuning bergaris jatuh beruntun di REF s18.0-s18.6!)
    domino = clamp(float(o.get("domino_pintu", 0.0)))
    dom_specs = [
        (0.55, BIRU, KORAL, False, False, 0.0, 0.42),
        (-0.45, PUTIH, MINT, True, False, 0.25, 0.70),
        (-1.45, MINT, KUNING, False, True, 0.50, 1.00),
    ]
    for dz, fc, dc, jwin, pgar, d0, d1 in dom_specs:
        jp = clamp((domino - d0) / max(0.05, d1 - d0), 0.0, 1.0)
        if jp < 0.99 and rebah < 0.2:
            BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, dz), s=0.80, warna_bingkai=fc, warna_pintu=dc, jendela_bulat=jwin, panel_garis=pgar, jatuh=jp, buka=0.0)

    # 24 Pintu mungil POP-UP bergelombang di dinding & ikut melipat rata saat rebah_labirin!
    buka_all = clamp(float(o.get("pintu_buka_semua", 0.0)))
    door_list = [
        (-1.08, 0.9, 90, KORAL),   (1.08, 0.2, -90, HIJAU),   (-1.08, -2.4, 90, KUNING), (1.08, -3.2, -90, BIRU),
        (-1.08, -5.4, 90, SALMON), (1.08, -5.8, -90, MINT),
        (-2.48, 1.8, 90, BIRU),    (-2.48, -1.2, 90, KORAL),  (-2.48, -4.6, 90, HIJAU),  (-2.48, -7.2, 90, KUNING),
        (2.48, 1.5, -90, KUNING),  (2.48, -1.6, -90, HIJAU),  (2.48, -4.8, -90, KORAL),  (2.48, -7.0, -90, BIRU),
        (-3.88, 2.2, 90, HIJAU),   (-3.88, -0.8, 90, BIRU),   (-3.88, -4.2, 90, KUNING), (-3.88, -7.4, 90, SALMON),
        (3.88, 2.0, -90, KORAL),   (3.88, -1.0, -90, KUNING), (3.88, -4.4, -90, BIRU),   (3.88, -7.2, -90, HIJAU),
        (-5.28, -0.5, 90, KUNING), (5.28, -0.2, -90, BIRU),
    ]
    for i, (dx, dz, ry, dc) in enumerate(door_list):
        wave_p = clamp(buka_all * 1.65 - (i % 6) * 0.11, 0.0, 1.0)
        p_stand = wave_p * (1.0 - clamp(rebah * 1.5, 0.0, 1.0))
        if p_stand > 0.04:
            BD.draw_prop(sc, "pintu_kertas", (dx, 0.0, dz), rot=(0.0, ry, 0.0), s=0.62, warna_bingkai=dc, warna_pintu=dc, pop_up=p_stand, buka=wave_p * 0.58)


# ================================================================== 6. LIPAT MEJA (3 TAHAP ORIGAMI -> HP!)
def set_lipat_meja(sc, t, o):
    """
    3 TAHAP LIPATAN ORIGAMI 3D RAPI DI MEJA HANGAT -> HP TEBAL 10 LAPIS + JAM WEKER KIRI + LUNA DI ATAS MEJA (REF s24-s30!):
      * lipat_tahap 0.0..1.0 : Lipatan #1 — separuh atas (baris 2-3) melipat 180° ke bawah di engsel z=0
      * lipat_tahap 1.0..2.0 : Lipatan #2 — separuh kanan (kolom 1) melipat 180° ke kiri di engsel x=0.28
      * lipat_tahap 2.0..3.0 : Lipatan #3 — lembaran melipat & membuka mulus menjadi HP tebal di (0.28, 0, 0)
      * lipat_tahap >= 2.92  : HP buku 10 lapis di (0.28, 0, 0), Luna berdiri BERSIH di meja depan HP (z=2.62), jam weker kiri!
    """
    _studio_lights(sc, MEJA)
    sc.set_sky((236, 220, 194), (224, 204, 174), (0.62, 0.59, 0.54), (0.45, 0.39, 0.33), [-0.66, 0.56, 0.50], [1.08, 0.98, 0.84], 0.58, (224, 204, 174))
    sc.tiled_plane(-12.0, -12.0, 12.0, 12.0, 0.0, MEJA, tile=2.2)
    sc.box((0.0, 2.8, -5.8), (24.0, 5.6, 0.16), (232, 214, 186), cast_shadow=False)
    sc.box((0.0, 0.28, -5.68), (24.0, 0.56, 0.08), (212, 192, 162), cast_shadow=False)

    # Jam weker mint-hijau mengintip di kiri (persis REF s25-s30!) + 2 pensil runcing di kanan bawah
    BD.draw_prop(sc, "jam_weker_kertas", (-2.05, 0.0, -0.35), rot=(0.0, 26.0, 0.0), s=1.48, t=t, warna=(92, 152, 128))
    BD.draw_prop(sc, "pensil_kertas", (1.65, 0.0, 3.35), rot=(0.0, 24.0, 0.0), s=0.92, warna=KUNING)
    BD.draw_prop(sc, "pensil_kertas", (1.98, 0.0, 3.78), rot=(0.0, 16.0, 0.0), s=0.92, warna=BIRU)

    st = float(o.get("lipat_tahap", 3.0))
    pop_notif = float(o.get("pop_notif", 0.0))

    if st < 2.92:
        # Kertas origami 2x4 berpusat di (0.28, 0.0, -0.15) — ujung depannya di z=+1.85, JAUH di belakang kaki Luna (z=+2.62)!
        ox, oz = 0.28, -0.15
        cw, cd = 1.18, 1.00
        col_c = (206, 232, 216)
        col_back = (182, 214, 196)
        line_c = (138, 184, 162)
        tab_cols = [BIRU, KORAL, KUNING, MINT]

        def _draw_panel(center, mat_p, thk_p, col_p, outline=True):
            sc.box(center, (cw - 0.04, thk_p, cd - 0.04), col_p, mat=mat_p, cast_shadow=True)
            if outline:
                w0, d0, bt = 0.36, 0.22, 0.026
                for dx, dz, bw, bd in ((0, -d0 * 0.5, w0, bt), (0, d0 * 0.5, w0, bt), (-w0 * 0.5, 0, bt, d0), (w0 * 0.5, 0, bt, d0)):
                    sc.box(center + mat_p @ np.array([dx, thk_p * 0.5 + 0.005, dz]), (bw, 0.006, bd), line_c, mat=mat_p, bias=-0.15, cast_shadow=False)

        if st < 1.0:
            # TAHAP 1: Baris atas (z < oz) melipat 180° ke bawah di engsel z = oz!
            ang = 180.0 * e_io(clamp(st))
            fmat = euler_mat(+ang, 0.0, 0.0)
            hinge = np.array([ox, 0.036, oz], dtype=np.float32)
            for r in (0, 1):
                for c in (0, 1):
                    px = ox + (-0.5 + c) * cw
                    pz = oz + (0.5 + r) * cd
                    _draw_panel(np.array([px, 0.022, pz], np.float32), np.eye(3, dtype=np.float32), 0.030, col_c)
                    if c == 0:
                        sc.box((px - cw * 0.54, 0.022, pz), (0.14, 0.024, 0.24), tab_cols[r], cast_shadow=False)
            for r in (0, 1):
                for c in (0, 1):
                    lx = (-0.5 + c) * cw
                    lz = -(0.5 + r) * cd
                    p_c = hinge + fmat @ np.array([lx, 0.0, lz], dtype=np.float32)
                    _draw_panel(p_c, fmat, 0.030, col_c if ang < 90.0 else col_back, outline=(ang < 95.0))
                    if c == 0:
                        sc.box(hinge + fmat @ np.array([lx - cw * 0.54, 0.0, lz], dtype=np.float32), (0.14, 0.024, 0.24), tab_cols[2 + r], mat=fmat, cast_shadow=False)
        elif st < 2.0:
            # TAHAP 2: Kotak 2x2 — kolom kanan melipat 180° ke kiri di engsel x = ox!
            ang = 180.0 * e_io(clamp(st - 1.0))
            fmat = euler_mat(0.0, 0.0, +ang)
            hinge = np.array([ox, 0.068, oz], dtype=np.float32)
            for r in (0, 1):
                pz = oz + (0.5 + r) * cd
                _draw_panel(np.array([ox - 0.5 * cw, 0.038, pz], np.float32), np.eye(3, dtype=np.float32), 0.062, col_c)
                p_c = hinge + fmat @ np.array([+0.5 * cw, 0.0, (0.5 + r) * cd], dtype=np.float32)
                _draw_panel(p_c, fmat, 0.062, col_c if ang < 90.0 else col_back, outline=(ang < 95.0))
        else:
            # TAHAP 3: Jalur lipatan membuka rata menjadi tumpukan HP tepat di (0.28, 0, 0.0)
            q = clamp(st - 2.0)
            ang = 180.0 * e_io(q)
            fmat = euler_mat(+ang, 0.0, 0.0)
            cx_strip = lerp(ox - 0.5 * cw, ox, e_io(q))
            cz_base = lerp(oz + 1.0 * cd, 0.0, e_io(q))
            hinge = np.array([cx_strip, 0.16, cz_base], dtype=np.float32)
            w_cur = lerp(cw, 2.48, e_io(q))
            d_cur = lerp(cd, 1.96, e_io(q))
            sc.box((cx_strip, 0.09, cz_base + d_cur * 0.5), (w_cur, 0.17, d_cur), col_c, cast_shadow=True)
            p_top = hinge + fmat @ np.array([0.0, 0.0, -d_cur * 0.5], dtype=np.float32)
            sc.box(p_top, (w_cur, 0.17, d_cur), BIRU_TUA if ang > 90.0 else col_c, mat=fmat, cast_shadow=True)
    else:
        # HP buku 10 lapis utuh di (0.28, 0.0, 0.0) — sisi tumpukan halaman & meja krem di depan terlihat lega & estetik!
        BD.draw_prop(sc, "hp_kertas", (0.28, 0.0, 0.0), rot=(0.0, -4.0, 0.0), s=0.96, t=t, pop_up=pop_notif, play_dx=-0.30)


# ================================================================== SET CERITA UMUM (7–12)
def set_kamar_kertas(sc, t, o):
    _studio_lights(sc, KRIM)
    sc.tiled_plane(-5.0, -5.0, 5.0, 5.0, 0.0, (242, 230, 206), tile=1.5)
    sc.box((0.0, 2.0, -3.2), (9.0, 4.0, 0.16), (244, 234, 214), cast_shadow=False)
    sc.box((-1.4, 0.32, -1.7), (1.8, 0.50, 2.2), KORAL)
    sc.box((-1.4, 0.60, -1.4), (1.7, 0.14, 1.4), BIRU_MUDA)
    sc.box((0.4, 0.36, -2.1), (0.68, 0.72, 0.56), KUNING)
    BD.draw_prop(sc, "jam_weker_kertas", (0.4, 0.72, -2.05), s=0.45, t=t)


def set_sekolah_kertas(sc, t, o):
    _studio_lights(sc, (176, 214, 152), (188, 224, 248), (228, 240, 248))
    sc.tiled_plane(-12.0, -10.0, 12.0, 10.0, 0.0, (164, 208, 142), tile=2.4)
    sc.box((0.0, 0.015, 0.5), (3.0, 0.02, 14.0), (242, 232, 208), bias=0.85, cast_shadow=False)
    sc.box((0.0, 2.0, -5.2), (8.2, 4.0, 3.0), PUTIH)
    sc.box((0.0, 4.2, -5.2), (8.6, 0.45, 3.4), KORAL)
    BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, -3.65), s=1.05, warna_bingkai=BIRU, warna_pintu=BIRU_TUA)
    BD.draw_prop(sc, "kartu_pita", (0.0, 3.35, -3.60), s=1.4, teks_besar=o.get("papan", "SMP"), teks_kecil="KERTAS", warna_aksen=BIRU)
    for px, pz in ((-5.0, 1.0), (5.0, 1.2), (-5.2, -2.5), (5.2, -2.8)):
        BD.draw_prop(sc, "pohon_kertas", (px, 0.0, pz), s=1.2)


def set_kelas_kertas(sc, t, o):
    _studio_lights(sc, MEJA)
    sc.tiled_plane(-6.0, -6.0, 6.0, 6.0, 0.0, MEJA, tile=1.8)
    sc.box((0.0, 2.2, -3.2), (10.0, 4.4, 0.16), (244, 236, 218), cast_shadow=False)
    sc.box((0.0, 1.85, -3.05), (3.4, 1.45, 0.12), HIJAU_TUA, cast_shadow=False)
    for mx in (-1.5, 0.0, 1.5):
        sc.box((mx, 0.42, -0.4), (0.95, 0.84, 0.55), KUNING)


def set_taman_kertas(sc, t, o):
    _studio_lights(sc, (164, 210, 142), (196, 230, 250), (232, 242, 248))
    sc.tiled_plane(-12.0, -12.0, 12.0, 12.0, 0.0, (164, 210, 142), tile=2.4)
    sc.box((0.0, 0.015, 0.0), (2.4, 0.02, 18.0), (242, 232, 208), bias=0.85, cast_shadow=False)
    sc.box((-2.2, 0.35, -0.8), (1.6, 0.70, 0.55), KORAL)
    for px, pz in ((-4.0, -3.0), (3.8, -2.5), (-4.2, 3.0), (4.0, 3.5)):
        BD.draw_prop(sc, "pohon_kertas", (px, 0.0, pz), s=1.2)


def set_kafe_kertas(sc, t, o):
    _studio_lights(sc, KRIM)
    sc.tiled_plane(-6.0, -6.0, 6.0, 6.0, 0.0, (238, 218, 186), tile=1.8)
    sc.box((0.0, 2.2, -3.2), (10.0, 4.4, 0.16), (244, 234, 214), cast_shadow=False)
    sc.box((0.0, 0.52, -2.0), (4.4, 1.04, 0.90), MINT)
    for mx in (-1.3, 1.3):
        sc.box((mx, 0.38, 0.6), (0.90, 0.76, 0.90), KUNING)


def set_polos(sc, t, o):
    col = o.get("warna", (236, 224, 200))
    _studio_lights(sc, col, col, col)
    sc.tiled_plane(-6.0, -6.0, 6.0, 6.0, 0.0, col, tile=2.0)


SET = {
    "meja_hp": set_meja_hp,
    "kota_jam": set_kota_jam,
    "ruang_pintu": set_ruang_pintu,
    "panggung_kertas": set_panggung_kertas,
    "labirin_pintu": set_labirin_pintu,
    "lipat_meja": set_lipat_meja,
    "kamar_kertas": set_kamar_kertas,
    "sekolah_kertas": set_sekolah_kertas,
    "kelas_kertas": set_kelas_kertas,
    "taman_kertas": set_taman_kertas,
    "kafe_kertas": set_kafe_kertas,
    "polos": set_polos,
}


def build_world(sc, latar, t, opsi):
    name = LATAR_ALIAS.get(latar, latar)
    SET.get(name, set_meja_hp)(sc, t, opsi)
