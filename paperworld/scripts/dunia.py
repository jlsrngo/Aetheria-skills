# -*- coding: utf-8 -*-
"""
dunia.py - 12 set diorama 3D Pop-Up Paper Craft berlapis detail untuk PaperWorld.

Set referensi & cerita:
  meja_hp · kota_jam · ruang_pintu · panggung_kertas · labirin_pintu · lipat_meja
  kamar_kertas · sekolah_kertas · kelas_kertas · taman_kertas · kafe_kertas · polos
"""
import math
import numpy as np
from paper import (
    OUT, KERTAS_TEPI, PUTIH, KRIM, MEJA, HITAM, KORAL, MERAH, BIRU, BIRU_TUA,
    BIRU_MUDA, BIRU_MALAM, MINT, MINT_MUDA, TEAL, PINK, SALMON, KUNING, KUNING_MUDA,
    ORANYE, HIJAU, HIJAU_TUA, COKLAT, COKLAT_TUA, UNGU, NAVY, ABU,
    clamp, prog, e_io, e_spring, gelap, terang,
    circle_2d, rrect_2d, arch_2d, star_2d, crescent_2d,
)
import benda as BD

LATAR_ALIAS = {
    "meja": "meja_hp", "kota": "kota_jam", "kamar_pintu": "ruang_pintu",
    "panggung": "panggung_kertas", "labirin": "labirin_pintu", "lipat": "lipat_meja",
    "kamar": "kamar_kertas", "sekolah": "sekolah_kertas", "sekolah_luar": "sekolah_kertas",
    "kelas": "kelas_kertas", "taman": "taman_kertas", "kafe": "kafe_kertas", "kantin": "kafe_kertas",
}


def _studio_lights(sc, floor_col=MEJA, wall_top=(248, 240, 224), wall_bot=(242, 232, 212)):
    sc.set_sky(wall_top, wall_bot, (0.80, 0.78, 0.75), (0.68, 0.64, 0.59), [-0.48, 0.68, 0.56], [1.02, 0.97, 0.90], 0.28, wall_bot)
    sc.shadow_floor_y = 0.0
    sc.floor_shadow_col = tuple(int(c * 0.78) for c in floor_col)


def _paper_cloud(sc, pos, s=1.0):
    px, py, pz = pos
    anc = np.array([px, py, pz], dtype=np.float32)
    sc.extrude_2d(circle_2d(0.0, 0.0, 0.68 * s, 0.34 * s, 22), 0.06 * s, PUTIH, PUTIH, None, origin=(px, py, pz), sort_anchor=anc, cast_shadow=False, drop_shadow=0.16)
    sc.extrude_2d(circle_2d(-0.42 * s, -0.06 * s, 0.36 * s, 0.26 * s, 18), 0.06 * s, PUTIH, PUTIH, None, origin=(px, py, pz + 0.01), sort_anchor=anc, cast_shadow=False)
    sc.extrude_2d(circle_2d(0.42 * s, -0.06 * s, 0.36 * s, 0.26 * s, 18), 0.06 * s, PUTIH, PUTIH, None, origin=(px, py, pz + 0.01), sort_anchor=anc, cast_shadow=False)


# ================================================================== 1. MEJA HP
def set_meja_hp(sc, t, o):
    """Meja kerajinan hangat dengan jam weker raksasa + HP kertas bertumpuk + pintu '5 MENIT'."""
    _studio_lights(sc, MEJA)
    sc.tiled_plane(-8.0, -8.0, 8.0, 8.0, 0.0, MEJA, tile=2.0)
    # Dinding meja belakang & lis krem
    sc.box((0.0, 2.6, -4.6), (16.0, 5.2, 0.16), (248, 240, 224), cast_shadow=False)
    sc.box((0.0, 0.25, -4.48), (16.0, 0.50, 0.08), (232, 218, 194), cast_shadow=False)

    # Jam weker koral raksasa di kiri
    BD.draw_prop(sc, "jam_weker_kertas", (-2.05, 0.0, 0.15), rot=(0.0, 24.0, 0.0), s=1.55, t=t, putar=True, warna=KORAL)

    # HP kertas bertumpuk di tengah (tombol Play muncul atau pintu 5 MENIT terbuka)
    mode_pintu = bool(o.get("mode_pintu", False))
    pop_play = 0.0 if mode_pintu else clamp((t - 0.05) * 1.8, 0.0, 1.0)
    BD.draw_prop(sc, "hp_kertas", (0.20, 0.0, 0.25), rot=(0.0, 0.0, 0.0), s=1.05, t=t, pop_up=pop_play)
    if mode_pintu:
        buka = float(o.get("buka_pintu", clamp((t - 0.35) * 1.1, 0.0, 1.0)))
        BD.draw_prop(sc, "pintu_kertas", (0.20, 0.26, -0.10), s=1.05, warna_bingkai=BIRU, warna_pintu=KORAL, buka=buka, jendela_bulat=True)
        BD.draw_prop(sc, "kartu_pita", (0.20, 2.68, -0.05), s=1.08, teks_besar="5", teks_kecil="MENIT", warna_aksen=MERAH)
        if buka > 0.04:
            # Plaza cerah berubin warna-warni di balik pintu 5 MENIT (tanpa silau putih!)
            sc.box((0.20, 0.27, -1.65), (2.4, 0.02, 2.8), (244, 232, 206), cast_shadow=False)
            for tx, tz, tc in ((-0.25, -0.85, KUNING_MUDA), (0.65, -0.85, MINT_MUDA), (-0.25, -1.65, BIRU_MUDA), (0.65, -1.65, SALMON)):
                sc.rbox((tx, 0.285, tz), (0.65, 0.016, 0.65), tc, roundness=0.18, seg=1, cast_shadow=False)
            sc.box((0.20, 1.45, -2.95), (2.8, 2.5, 0.12), (246, 236, 214), cast_shadow=False)


# ================================================================== 2. KOTA JAM
def set_kota_jam(sc, t, o):
    """Alun-alun kota kertas cerah dengan Menara Jam '1 JAM', gedung rapat, & jalan arkade pintu."""
    _studio_lights(sc, MEJA, (248, 240, 224), (242, 232, 212))
    sc.tiled_plane(-14.0, -18.0, 14.0, 12.0, 0.0, (238, 224, 198), tile=2.4)
    sc.box((0.0, 0.012, 0.0), (2.8, 0.015, 24.0), (248, 238, 216), bias=0.85, cast_shadow=False)
    sc.extrude_2d(circle_2d(0.0, 0.0, 1.85, 1.85, 32), 0.02, KUNING, KUNING, None, origin=(0.0, 0.015, 3.8), rot=(-90.0, 0.0, 0.0), bias=0.75, cast_shadow=False)

    # Awan kertas di langit belakang
    _paper_cloud(sc, (-3.2, 6.2, -11.5), 1.3)
    _paper_cloud(sc, (3.6, 5.8, -11.0), 1.15)

    # Menara jam biru di ujung plaza + kartu '1 JAM' di atas atapnya
    BD.draw_prop(sc, "menara_jam", (0.0, 0.0, -9.2), s=1.12, t=t)
    jam_pop = clamp(float(o.get("pop_jam", prog(t, 0.0, 0.55))), 0.0, 1.0)
    if jam_pop > 0.05:
        BD.draw_prop(sc, "kartu_pita", (0.0, 6.45, -8.25), s=1.35 * e_spring(jam_pop), teks_besar="1", teks_kecil="JAM", warna_aksen=MERAH, bayangan=True)

    # Gedung-gedung kertas pastel rapat di sisi kiri-kanan + atap & deretan jendela
    buildings = [
        (-3.4, -7.8, 2.0, 3.6, 1.8, KORAL, KUNING), (-5.2, -6.4, 2.1, 4.4, 1.9, MINT, KORAL),
        (-3.6, -4.6, 1.9, 2.8, 1.7, KUNING, BIRU),  (3.5, -7.9, 2.0, 4.0, 1.8, HIJAU, KORAL),
        (5.3, -6.0, 2.1, 3.2, 1.9, BIRU_MUDA, KUNING), (3.8, -4.4, 1.8, 2.7, 1.6, SALMON, MINT),
    ]
    for bx, bz, bw, bh, bd, col, rcol in buildings:
        sc.box((bx, bh * 0.5, bz), (bw, bh, bd), col)
        sc.box((bx, bh + 0.16, bz), (bw * 1.04, 0.32, bd * 1.04), rcol)
        for wy in (0.95, 1.95, 2.95):
            if wy < bh - 0.5:
                # Jendela menghadap alun-alun (+Z dan sisi tengah)
                sc.box((bx, wy, bz + bd * 0.51), (0.48, 0.58, 0.05), BIRU_TUA, bias=-0.02, cast_shadow=False)
                side_x = bx + (-bw * 0.51 if bx > 0 else bw * 0.51)
                sc.box((side_x, wy, bz), (0.05, 0.58, 0.48), BIRU_TUA, bias=-0.02, cast_shadow=False)

    # Dinding arkade kanan bermahkota gelombang koral + 3 pintu + ruang mint di balik pintu hero
    sc.box((3.15, 1.85, -0.5), (0.26, 3.7, 13.5), PUTIH)
    for cz in np.linspace(-6.5, 5.5, 13):
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.36, 0.28, 18), 0.14, KORAL, KORAL, None, origin=(3.15, 3.72, float(cz)), rot=(0.0, -90.0, 0.0), cast_shadow=False)
    sc.box((4.4, 1.5, 1.2), (2.2, 3.0, 2.8), MINT_MUDA, cast_shadow=False)
    door_specs = [(2.95, 1.2, KORAL, 1), (2.95, -1.6, MINT, 0), (2.95, -4.2, SALMON, 0)]
    for dx, dz, dc, is_hero in door_specs:
        buka = float(o.get("buka_pintu_kanan", 0.0)) if is_hero else 0.0
        BD.draw_prop(sc, "pintu_kertas", (dx, 0.0, dz), rot=(0.0, -90.0, 0.0), s=0.95, warna_bingkai=KORAL if is_hero else dc, warna_pintu=dc, buka=buka, ornamen="setengah_lingkaran", warna_ornamen=KUNING, cahaya_portal=bool(is_hero), warna_portal=(244, 240, 212))

    # Lampu taman & pot tanaman di sepanjang jalan arkade
    for lx in (-1.85, 1.95):
        for lz in (2.2, 0.2, -2.0, -4.2):
            if lx > 0 and abs(lz - 0.2) < 0.8:
                continue
            BD.draw_prop(sc, "lampu_taman_kertas", (lx, 0.0, lz), s=0.88)
        for pz in (1.2, -0.9, -3.1):
            if lx > 0 and abs(pz - 1.2) < 0.3:
                continue
            sc.rbox((lx, 0.20, pz), (0.38, 0.38, 0.38), KORAL, roundness=0.22, seg=1)
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.26, 0.24, 16), 0.16, HIJAU, HIJAU, None, origin=(lx, 0.48, pz))


# ================================================================== 3. RUANG PINTU
def set_ruang_pintu(sc, t, o):
    """Kamar pastel krem bergaris wallpaper mint + wainscoting hijau + pintu 'SATU PINTU lagi'."""
    _studio_lights(sc, MINT_MUDA, (230, 244, 236), (218, 236, 226))
    sc.tiled_plane(-5.0, -5.0, 5.0, 5.0, 0.0, (224, 240, 230), tile=1.5)
    sc.rbox((0.0, 0.015, 0.5), (3.4, 0.02, 2.2), SALMON, roundness=0.25, seg=1, bias=0.85, cast_shadow=False)
    sc.rbox((0.0, 0.024, 0.5), (3.0, 0.02, 1.8), (250, 244, 236), roundness=0.25, seg=1, bias=0.75, cast_shadow=False)

    # Dinding kiri bergaris vertikal mint + wainscoting hijau + lukisan gunung berbayangan
    sc.box((-3.2, 2.2, 0.0), (0.16, 4.4, 9.0), (248, 242, 228), cast_shadow=False)
    for sz in np.linspace(-3.6, 3.6, 11):
        sc.box((-3.10, 2.2, float(sz)), (0.04, 4.2, 0.26), (206, 232, 218), bias=-0.01, cast_shadow=False)
    sc.box((-3.08, 0.38, 0.0), (0.06, 0.76, 9.0), MINT, bias=-0.02, cast_shadow=False)
    sc.extrude_2d(rrect_2d(0.0, 0.0, 1.45, 1.15, 0.05), 0.06, BIRU, BIRU, None, origin=(-3.04, 2.15, -0.5), rot=(0.0, 90.0, 0.0), cast_shadow=False, drop_shadow=0.20)
    sc.extrude_2d(rrect_2d(0.0, 0.0, 1.25, 0.96, 0.03), 0.03, PUTIH, PUTIH, None, origin=(-3.00, 2.15, -0.5), rot=(0.0, 90.0, 0.0), cast_shadow=False)
    sc.extrude_2d(((-0.45, 0.0), (0.0, 0.52), (0.45, 0.0)), 0.025, KUNING, KUNING, None, origin=(-2.97, 1.72, -0.5), rot=(0.0, 90.0, 0.0), cast_shadow=False, drop_shadow=0.16)

    # Dinding belakang bergaris mint + wainscoting + lubang pintu lengkung nyata!
    sc.arch_wall((0.0, 0.0, -2.4), 7.2, 4.4, 1.12, 2.02, thickness=0.16, wall_col=(248, 242, 228), trim_col=None, cast_shadow=False)
    for sx in (-2.85, -2.25, -1.65, -1.05, 1.05, 1.65, 2.25, 2.85):
        sc.box((sx, 2.2, -2.30), (0.26, 4.2, 0.03), (206, 232, 218), bias=-0.01, cast_shadow=False)
    for sx in (-2.05, 2.05):
        sc.box((sx, 0.38, -2.28), (2.9, 0.76, 0.05), MINT, bias=-0.02, cast_shadow=False)

    buka = float(o.get("buka_pintu", clamp((t - 0.8) * 0.9, 0.0, 1.0)))
    BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, -2.26), s=1.0, warna_bingkai=BIRU, warna_pintu=BIRU_TUA, buka=buka, jendela_bulat=True, ornamen="setengah_lingkaran", warna_ornamen=MINT)
    BD.draw_prop(sc, "kartu_pita", (0.0, 2.85, -1.98), s=1.08, teks_besar="SATU PINTU", teks_kecil="lagi", warna_aksen=MERAH)
    # Ruang hangat kuning-koral di balik pintu
    sc.box((0.0, 1.8, -4.3), (5.5, 3.6, 0.16), (252, 232, 184), emissive=0.18, cast_shadow=False)
    sc.box((-1.5, 1.4, -3.5), (0.14, 2.8, 2.4), KORAL, cast_shadow=False)
    sc.box((1.5, 1.4, -3.5), (0.14, 2.8, 2.4), KUNING, cast_shadow=False)


# ================================================================== 4. PANGGUNG KERTAS (3 ZONA)
def set_panggung_kertas(sc, t, o):
    """Panggung 3 zona: Kucing kuning polkadot (-4.5) | Malam berbintang + pintu rusa (0) | Pintu matahari (+4.5)."""
    _studio_lights(sc, (176, 126, 86), (44, 72, 142), (38, 62, 124))
    sc.shadow_wall_z = -1.6
    sc.wall_shadow_col = (14, 22, 48)
    sc.tiled_plane(-9.0, -2.2, 9.0, 5.0, 0.0, (186, 134, 92), tile=1.5)
    for kz in np.linspace(-1.8, 4.4, 14):
        sc.box((0.0, 0.015, float(kz)), (18.0, 0.01, 0.03), (154, 108, 72), bias=0.82, cast_shadow=False)

    # ZONA 1 (x = -4.5): Dinding polkadot kuning-krem cerah + podium drum
    sc.box((-4.5, 2.2, -1.62), (4.4, 4.4, 0.12), (246, 228, 158), cast_shadow=False)
    for px, py, pc in ((-5.4, 1.8, KORAL), (-3.7, 2.4, BIRU), (-4.6, 3.0, MINT), (-5.2, 0.9, MERAH), (-3.6, 1.1, ORANYE)):
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.18, 0.18, 20), 0.02, pc, pc, None, origin=(px, py, -1.54), cast_shadow=False, drop_shadow=0.18)
    sc.extrude_2d(circle_2d(0.0, 0.0, 0.58, 0.58, 28), 0.36, KUNING, KUNING, KORAL, origin=(-4.5, 0.18, -0.35), rot=(-90.0, 0.0, 0.0))

    # ZONA 2 (x = 0.0): Malam berbintang + bukit 3 lapis + rumah berjendela + ikan gantung + pintu siluet rusa
    sc.box((0.0, 2.2, -1.62), (4.6, 4.4, 0.12), BIRU_MALAM, cast_shadow=False)
    hills = ((-1.25, -1.24, 1.32, HIJAU_TUA), (1.25, -1.24, 1.32, HIJAU_TUA), (0.0, -1.10, 1.12, HIJAU))
    for hx, hz, hr, hc in hills:
        semi = [(-hr, 0.0), (hr, 0.0)] + [(round(hr * math.cos(math.pi * i / 20), 5), round(hr * 0.78 * math.sin(math.pi * i / 20), 5)) for i in range(21)]
        sc.extrude_2d(semi, 0.05, hc, hc, None, origin=(hx, 0.0, hz), cast_wall_shadow=True, drop_shadow=0.20)
    # 2 rumah kertas mungil berjendela nyala di atas bukit
    for rhx in (-1.22, 1.15):
        sc.extrude_2d(rrect_2d(0.0, 0.16, 0.28, 0.30, 0.02), 0.04, KRIM, KRIM, None, origin=(rhx, 0.45, -1.04), cast_shadow=False, drop_shadow=0.16)
        sc.extrude_2d(((-0.18, 0.0), (0.18, 0.0), (0.0, 0.16)), 0.04, KORAL, KORAL, None, origin=(rhx, 0.74, -1.04), cast_shadow=False)
        sc.extrude_2d(rrect_2d(0.0, 0.0, 0.09, 0.09, 0.01), 0.02, KUNING_MUDA, KUNING_MUDA, None, origin=(rhx, 0.60, -1.01), emissive=0.7, cast_shadow=False)

    # Tali gantung + bulan sabit, bintang-bintang, & ikan biru lengkap berekor
    def _tali(tx, y_bot):
        if y_bot < 4.2:
            sc.box((tx, (4.2 + y_bot) * 0.5, -0.84), (0.012, 4.2 - y_bot, 0.01), (226, 224, 218), cast_shadow=False)

    _tali(-1.25, 2.55)
    sc.extrude_2d(crescent_2d(0.42, 0.40, n=20), 0.03, KUNING_MUDA, KUNING_MUDA, None, origin=(-1.25, 2.35, -0.85), cast_wall_shadow=True, cast_shadow=False)
    for sx, sy in ((-0.4, 2.8), (0.5, 2.65), (1.35, 2.95), (-1.7, 1.85), (1.65, 1.75)):
        _tali(sx, sy + 0.1)
        sc.extrude_2d(star_2d(0.14, 0.06, 5), 0.028, KUNING, KUNING, None, origin=(sx, sy, -0.82), rot=(0.0, math.sin(t * 2 + sx) * 18.0, 0.0), cast_wall_shadow=True, cast_shadow=False)
    # Ikan biru kertas gantung lengkap dengan ekor segitiga & mata
    fx, fy, fz = 1.25, 1.95, -0.78
    _tali(fx, fy + 0.12)
    sc.extrude_2d(circle_2d(0.0, 0.0, 0.22, 0.13, 20), 0.028, BIRU_MUDA, BIRU_MUDA, None, origin=(fx, fy, fz), cast_wall_shadow=True, cast_shadow=False)
    sc.extrude_2d(((0.0, 0.0), (0.16, 0.11), (0.16, -0.11)), 0.024, BIRU_MUDA, BIRU_MUDA, None, origin=(fx + 0.18, fy, fz), cast_wall_shadow=True, cast_shadow=False)
    sc.extrude_2d(circle_2d(0.0, 0.0, 0.032, 0.032, 12), 0.014, PUTIH, PUTIH, PUTIH, origin=(fx - 0.10, fy + 0.03, fz + 0.02), cast_shadow=False)
    sc.extrude_2d(circle_2d(0.0, 0.0, 0.016, 0.016, 10), 0.010, OUT, OUT, OUT, origin=(fx - 0.10, fy + 0.03, fz + 0.03), cast_shadow=False)

    BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, -0.95), s=0.98, warna_bingkai=KUNING, warna_pintu=BIRU_TUA, buka=0.95, cahaya_portal=True, warna_portal=(252, 228, 138), siluet="rusa")

    # ZONA 3 (x = +4.5): Dinding oranye bergaris + pintu matahari bercahaya emas
    sc.box((4.5, 2.2, -1.62), (4.6, 4.4, 0.12), (242, 142, 92), cast_shadow=False)
    for sx in np.linspace(2.6, 6.4, 7):
        sc.box((float(sx), 2.2, -1.55), (0.24, 4.2, 0.03), (248, 174, 122), bias=-0.01, cast_shadow=False)
    BD.draw_prop(sc, "pintu_kertas", (4.5, 0.0, -0.95), s=1.02, warna_bingkai=BIRU, warna_pintu=BIRU_TUA, buka=0.98, cahaya_portal=True, warna_portal=(255, 228, 142), ornamen="matahari")


# ================================================================== 5. LABIRIN PINTU
def set_labirin_pintu(sc, t, o):
    """Labirin spiral persegi 4 cincin bersarang & 22 pintu warna-warni terbuka bergelombang."""
    _studio_lights(sc, MINT_MUDA, (248, 240, 224), (240, 232, 216))
    sc.tiled_plane(-9.5, -13.5, 9.5, 9.5, 0.0, (224, 242, 230), tile=2.2)
    # Garis kisi lantai + bintang koral mungil di persimpangan
    for gx in (-4.4, -2.2, 0.0, 2.2, 4.4):
        sc.box((gx, 0.01, -2.0), (0.04, 0.01, 18.0), (196, 226, 208), bias=0.85, cast_shadow=False)
    for gz in (-8.0, -5.8, -3.6, -1.4, 0.8, 3.0, 5.2):
        sc.box((0.0, 0.01, gz), (14.0, 0.01, 0.04), (196, 226, 208), bias=0.85, cast_shadow=False)

    # Keset warna-warni di lantai koridor
    mat_cols = [KORAL, BIRU_MUDA, KUNING, HIJAU, SALMON]
    for i, mz in enumerate((-7.5, -5.5, -3.5, -0.5, 1.5, 3.5)):
        sc.rbox((-0.45 if i % 2 == 0 else 0.45, 0.014, mz), (0.58, 0.015, 0.85), mat_cols[i % 5], roundness=0.22, seg=1, bias=0.82, cast_shadow=False)

    # 4 cincin dinding spiral persegi bersarang (karton krem + lis atas warna + garis sambungan panel)
    wall_h = 1.55
    segs = [
        # Koridor dalam (x = +-1.3)
        (-1.3, -2.4, 0.14, 9.6, KORAL), (1.3, -2.4, 0.14, 9.6, BIRU),
        # Cincin kedua (x = +-2.8, penutup z = -7.2 & +2.5)
        (-2.8, -2.5, 0.14, 12.6, KUNING), (2.8, -2.5, 0.14, 12.6, HIJAU),
        (0.0, -7.2, 2.74, 0.14, BIRU),
        # Cincin ketiga (x = +-4.4, penutup z = -9.0 & +4.1)
        (-4.4, -2.5, 0.14, 15.8, BIRU), (4.4, -2.5, 0.14, 15.8, KORAL),
        (-1.6, -9.0, 5.6, 0.14, KORAL), (2.2, -9.0, 4.4, 0.14, KUNING),
        (-2.8, 4.1, 3.2, 0.14, HIJAU), (2.8, 4.1, 3.2, 0.14, BIRU),
        # Cincin terluar (x = +-6.0, penutup z = -10.8 & +5.8)
        (-6.0, -2.5, 0.14, 18.0, KORAL), (6.0, -2.5, 0.14, 18.0, KUNING),
        (0.0, -10.8, 12.14, 0.14, BIRU), (0.0, 5.8, 12.14, 0.14, KORAL),
    ]
    for wx, wz, ww, wd, trim in segs:
        sc.box((wx, wall_h * 0.5, wz), (ww, wall_h, wd), PUTIH)
        sc.box((wx, wall_h + 0.035, wz), (ww + 0.04, 0.07, wd + 0.04), trim)

    # Gerbang depan koridor + pintu tengah pop-up kuning (00:18)
    BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, 2.55), s=0.95, warna_bingkai=BIRU, warna_pintu=KUNING, buka=1.0, ornamen="setengah_lingkaran", warna_ornamen=KORAL)
    pop_hero = float(o.get("pintu_tengah_pop", clamp(t * 1.4, 0.0, 1.0)))
    BD.draw_prop(sc, "pintu_kertas", (0.0, 0.0, -1.2), s=0.92, warna_bingkai=MINT, warna_pintu=KUNING, pop_up=pop_hero, buka=0.0)

    # 22 pintu warna-warni terbuka bergelombang di keempat cincin labirin
    buka_all = float(o.get("pintu_buka_semua", clamp((t - 1.2) * 0.65, 0.0, 1.0)))
    door_list = [
        (-1.20, 1.1, 90, KORAL), (1.20, 0.4, -90, HIJAU), (-1.20, -2.8, 90, KUNING), (1.20, -3.6, -90, BIRU),
        (-1.20, -5.6, 90, SALMON), (1.20, -6.0, -90, MINT),
        (-2.70, 2.0, 90, BIRU), (-2.70, -1.4, 90, KORAL), (-2.70, -5.0, 90, HIJAU),
        (2.70, 1.6, -90, KUNING), (2.70, -1.8, -90, HIJAU), (2.70, -5.2, -90, KORAL),
        (-4.30, 2.6, 90, HIJAU), (-4.30, -0.8, 90, BIRU), (-4.30, -4.6, 90, KUNING), (-4.30, -7.8, 90, SALMON),
        (4.30, 2.4, -90, KORAL), (4.30, -1.0, -90, KUNING), (4.30, -4.8, -90, BIRU), (4.30, -7.6, -90, HIJAU),
        (-5.90, 0.5, 90, KUNING), (5.90, 0.8, -90, BIRU),
    ]
    for i, (dx, dz, ry, dc) in enumerate(door_list):
        b_i = clamp(buka_all * 1.45 - (i % 5) * 0.14, 0.0, 1.0)
        BD.draw_prop(sc, "pintu_kertas", (dx, 0.0, dz), rot=(0.0, ry, 0.0), s=0.78, warna_bingkai=dc, warna_pintu=dc, buka=b_i)


# ================================================================== 6. LIPAT MEJA
def set_lipat_meja(sc, t, o):
    """Meja kerajinan dengan brosur 6 panel bertab warna, 2 pensil runcing, jam weker, & HP raksasa."""
    _studio_lights(sc, MEJA)
    sc.tiled_plane(-10.0, -12.0, 10.0, 10.0, 0.0, MEJA, tile=2.2)
    # 6 panel kartu mint sudut bulat (2 kolom x 3 baris) + garis sketsa pintu + tab warna di kiri
    tab_cols = [KORAL, BIRU, KUNING]
    for r in range(3):
        for c in range(2):
            px, pz = -0.85 + c * 1.72, 1.85 + r * 1.72
            sc.rbox((px, 0.02, pz), (1.58, 0.03, 1.62), MINT_MUDA, roundness=0.14, seg=1, bias=0.80, cast_shadow=False)
            # Sketsa mini pintu tipis di tengah kartu
            sc.rbox((px, 0.038, pz), (0.36, 0.008, 0.52), (168, 212, 192), roundness=0.22, seg=1, bias=0.78, cast_shadow=False)
            if c == 0:
                sc.rbox((px - 0.86, 0.024, pz), (0.18, 0.025, 0.42), tab_cols[r], roundness=0.2, seg=1, bias=0.79, cast_shadow=False)

    # Dua pensil kertas runcing menyerong rapi di kanan bawah + jam weker koral + HP bertumpuk tengah
    BD.draw_prop(sc, "pensil_kertas", (0.55, 0.0, 5.35), rot=(0.0, 22.0, 0.0), s=0.95, warna=KUNING)
    BD.draw_prop(sc, "pensil_kertas", (0.75, 0.0, 5.75), rot=(0.0, 14.0, 0.0), s=0.95, warna=BIRU)
    BD.draw_prop(sc, "jam_weker_kertas", (-1.75, 0.0, -1.10), rot=(0.0, 24.0, 0.0), s=1.45, t=t, warna=KORAL)
    pop_notif = float(o.get("pop_notif", 0.0))
    BD.draw_prop(sc, "hp_kertas", (-0.20, 0.0, -1.05), s=1.08, t=t, pop_up=pop_notif)


# ================================================================== SET CERITA UMUM (7–12)
def set_kamar_kertas(sc, t, o):
    _studio_lights(sc, KRIM)
    sc.tiled_plane(-5.0, -5.0, 5.0, 5.0, 0.0, (242, 230, 206), tile=1.5)
    sc.box((0.0, 2.0, -3.2), (9.0, 4.0, 0.16), (248, 240, 224), cast_shadow=False)
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
    sc.box((0.0, 2.2, -3.2), (10.0, 4.4, 0.16), (248, 242, 228), cast_shadow=False)
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
    sc.box((0.0, 2.2, -3.2), (10.0, 4.4, 0.16), (248, 238, 220), cast_shadow=False)
    sc.box((0.0, 0.52, -2.0), (4.4, 1.04, 0.90), MINT)
    for mx in (-1.3, 1.3):
        sc.box((mx, 0.38, 0.6), (0.90, 0.76, 0.90), KUNING)


def set_polos(sc, t, o):
    col = o.get("warna", (242, 232, 212))
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
