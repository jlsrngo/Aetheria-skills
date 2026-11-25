# -*- coding: utf-8 -*-
"""
tokoh.py - rig karakter 3D low-poly chamfered (`rbox` seg=1) artikulasi penuh untuk VoxelVerse.

Karakter utama & bawaan:
  * kribo : chibi low-poly berambut afro hitam penuh, kacamata kotak tipis, kaos teal + dasi kupu-kupu, sneaker hitam-putih
  * arka  : developer hoodie teal bertali putih, poni & jambul miring, hidung 3D mungil, kacamata tipis (gaya video referensi)
  * robo  : robot pendamping / lampu meja oranye-teal bersudut tumpul dengan cincin layar bercahaya PointLight
  * nadia : chibi hijab hitam modern, kacamata bulat 8-sisi, blazer krem, rok gelap
  * raka, bimo, dimas, sari, tika, ayah, ibu, guru, bu_guru, kakek, adik, kucing

Satuan lokal (skala 1): kaki berdiri di y=0, tinggi total ±1.75 m, menghadap +Z secara default.
"""
import math
import numpy as np
from voxel import (
    OUT, PUTIH, KRIM, HITAM, MERAH, MERAH_TUA, PIPI, BIRU, BIRU_TUA, BIRU_MUDA,
    TEAL, TEAL_TUA, PINK, PINK_TUA, KUNING, ORANYE, HIJAU, HIJAU_TUA,
    COKLAT, COKLAT_TUA, KAYU, KAYU_TUA, UNGU, UNGU_TUA, NAVY, ABU, ABU_TUA, KULIT,
    clamp, lerp, euler_mat, mix, gelap, terang,
)
import benda as BD

WARNA = {
    "putih": PUTIH, "hitam": HITAM, "merah": MERAH, "merah_tua": MERAH_TUA,
    "biru": BIRU, "biru_tua": BIRU_TUA, "biru_muda": BIRU_MUDA, "teal": TEAL,
    "pink": PINK, "kuning": KUNING, "oranye": ORANYE, "hijau": HIJAU,
    "ungu": UNGU, "coklat": COKLAT, "abu": ABU, "navy": NAVY, "krem": KRIM,
    "kulit": (232, 184, 146),
}


def warna(v, default=None):
    if v is None:
        return default
    if isinstance(v, str):
        return WARNA.get(v.lower(), default)
    return tuple(v)


# ------------------------------------------------------------------ preset pemeran
PRESET = {
    "kribo": dict(
        nama="Kribo", tipe="humanoid", rambut="afro", rambut_warna=(22, 22, 28),
        kulit=(232, 184, 146), kacamata="kotak", kemeja=(76, 126, 132),
        dasi_kupu=True, dasi=None, lengan_pendek=True, badan_lebar=1.18,
        bawah="celana", bawah_warna=(44, 46, 54), sepatu_sneaker=True,
    ),
    "arka": dict(
        nama="Arka", tipe="humanoid", rambut="jambul_kode", rambut_warna=(26, 22, 22),
        kulit=(232, 184, 146), kacamata="kotak", kemeja=(58, 118, 128),
        hoodie=True, dasi=None, lengan_pendek=False, badan_lebar=1.08,
        bawah="celana", bawah_warna=(44, 52, 66), sepatu=(46, 48, 56),
    ),
    "robo": dict(
        nama="Robo", tipe="robo", utama=(228, 112, 46), aksen=(62, 126, 138),
        layar=(32, 40, 50), cahaya=(255, 196, 110), skala=0.62,
    ),
    "nadia": dict(
        nama="Nadia", tipe="humanoid", hijab=(34, 36, 46), hijab_tua=(70, 74, 90),
        kulit=(234, 188, 152), kacamata="bulat", bulu_mata=True,
        kemeja=(222, 192, 152), kemeja_dalam=PUTIH, blazer=True, dasi=None,
        lengan_pendek=False, badan_lebar=0.96,
        bawah="rok", bawah_warna=(44, 46, 54), sepatu=(68, 52, 46),
    ),
    "raka": dict(
        nama="Raka", tipe="humanoid", rambut="jambul", rambut_warna=HITAM,
        kulit=(234, 188, 152), kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=NAVY,
    ),
    "bimo": dict(
        nama="Bimo", tipe="humanoid", rambut="keriting", rambut_warna=(66, 42, 34),
        kulit=(234, 188, 152), kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=NAVY,
    ),
    "dimas": dict(
        nama="Dimas", tipe="humanoid", rambut="rapi", rambut_warna=HITAM,
        kulit=(234, 188, 152), kacamata="kotak", kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=NAVY,
    ),
    "sari": dict(
        nama="Sari", tipe="humanoid", hijab=(248, 248, 252), hijab_tua=ABU,
        kulit=(234, 188, 152), bulu_mata=True, kemeja=PUTIH, dasi=MERAH, bawah="rok", bawah_warna=NAVY,
    ),
    "tika": dict(
        nama="Tika", tipe="humanoid", rambut="kuncir", rambut_warna=HITAM,
        kulit=(234, 188, 152), bulu_mata=True, kemeja=PUTIH, dasi=MERAH, bawah="rok", bawah_warna=NAVY,
    ),
    "ayah": dict(
        nama="Ayah", tipe="humanoid", rambut="rapi", rambut_warna=(70, 72, 82),
        kumis=True, kulit=(232, 184, 146), kemeja=(196, 220, 246), dasi=None, bawah="celana", bawah_warna=NAVY, skala=1.06,
    ),
    "ibu": dict(
        nama="Ibu", tipe="humanoid", hijab=HIJAU, hijab_tua=HIJAU_TUA,
        bulu_mata=True, kulit=(234, 188, 152), kemeja=(248, 232, 206), dasi=None, bawah="rok", bawah_warna=COKLAT_TUA, skala=1.02,
    ),
    "guru": dict(
        nama="Pak Guru", tipe="humanoid", rambut="uban", rambut_warna=(205, 208, 214),
        kacamata="kotak", kumis=True, kulit=(232, 184, 146), kemeja=(234, 228, 210), dasi=MERAH_TUA,
        bawah="celana", bawah_warna=NAVY, skala=1.05,
    ),
    "bu_guru": dict(
        nama="Bu Guru", tipe="humanoid", hijab=UNGU, hijab_tua=UNGU_TUA,
        kacamata="bulat", bulu_mata=True, kulit=(234, 188, 152), kemeja=(238, 228, 248),
        bawah="rok", bawah_warna=UNGU_TUA, skala=1.02,
    ),
    "kakek": dict(
        nama="Kakek", tipe="humanoid", rambut="botak", peci=True, kumis=True, jenggot=True,
        kulit=(232, 184, 146), kemeja=PUTIH, bawah="celana", bawah_warna=(92, 72, 62), skala=0.98,
    ),
    "adik": dict(
        nama="Adik", tipe="humanoid", rambut="bob", rambut_warna=HITAM,
        bulu_mata=True, kulit=(236, 192, 156), kemeja=KUNING, bawah="rok", bawah_warna=PINK_TUA, skala=0.80,
    ),
    "kucing": dict(
        nama="Kucing", tipe="kucing", warna=(232, 132, 54), skala=0.72,
    ),
}


def casting(spec):
    if isinstance(spec, str):
        spec = {"dasar": spec}
    base = dict(PRESET.get(spec.get("dasar", "kribo"), PRESET["kribo"]))
    for k, v in spec.items():
        if k == "dasar":
            continue
        if isinstance(v, list) and len(v) == 3 and all(isinstance(i, (int, float)) for i in v):
            base[k] = tuple(int(c) for c in v)
        else:
            base[k] = v
    base.setdefault("skala", 1.0)
    return base


# ------------------------------------------------------------------ ekspresi
EKSPRESI = {
    "senang":   dict(eyes="oval", mouth="open", open=0.58, blush=0.55),
    "tenang":   dict(eyes="oval", mouth="smile", blush=0.40),
    "fokus":    dict(eyes="oval", mouth="flat", brow=(-2, -0.3, -0.3), blush=0.35),
    "tertawa":  dict(eyes="arc_up", mouth="grin", open=1.0, blush=0.85),
    "kaget":    dict(eyes="wide", mouth="o", brow=(4, 0, 0), blush=0.15),
    "marah":    dict(eyes="oval", mouth="gigit", brow=(-3, -1.0, -1.0), blush=0.0, vein=True),
    "mikir":    dict(eyes="oval", mouth="flat", brow=(1, 0.2, 1.0), blush=0.15, look=(0.35, 0.35)),
    "sedih":    dict(eyes="oval", mouth="frown", brow=(0, 0.9, 0.9), blush=0.0, tear=True),
    "malu":     dict(eyes="arc_up", mouth="wave", blush=1.0, sweat=True),
    "ngantuk":  dict(eyes="half", mouth="flat", blush=0.1),
    "menguap":  dict(eyes="arc_dn", mouth="yawn", blush=0.1),
    "tidur":    dict(eyes="arc_dn", mouth="smile", blush=0.45),
    "semangat": dict(eyes="spark", mouth="grin", open=0.9, blush=0.8),
    "panik":    dict(eyes="dot", mouth="o", brow=(4, 0.8, 0.8), blush=0.0, sweat=True),
    "bangga":   dict(eyes="half", mouth="smirk", blush=0.45, brow=(0, -0.3, -0.3)),
    "jahil":    dict(eyes="wink", mouth="smirk", blush=0.5),
    "cemberut": dict(eyes="oval", mouth="frown", blush=0.75, brow=(-2, -0.5, -0.5)),
    "cemas":    dict(eyes="oval", mouth="wave", brow=(1, 0.9, 0.9), blush=0.1, sweat=True),
    "lega":     dict(eyes="arc_dn", mouth="open", open=0.35, blush=0.5, sweat=True),
    "terpana":  dict(eyes="spark", mouth="o", brow=(4, 0, 0), blush=0.6),
    "datar":    dict(eyes="dot", mouth="flat", blush=0.1),
}
EKSPRESI_ALIAS = {
    "senyum": "tenang", "kecewa": "sedih", "bingung": "mikir",
    "ketawa": "tertawa", "heran": "kaget", "kesal": "cemberut", "takut": "panik",
}


def get_expr(name):
    return EKSPRESI.get(EKSPRESI_ALIAS.get(name, name), EKSPRESI["senang"])


# ------------------------------------------------------------------ pose 3D
POSE = {
    "diam":             dict(l_arm=(6, 0, -8), r_arm=(6, 0, 8)),
    "santai":           dict(l_arm=(10, 0, -14), r_arm=(-15, 0, 18), r_fore=(-35,), body=(0, 6, 0)),
    "lambai":           dict(l_arm=(8, 0, -10), r_arm=(-135, 0, 32), r_fore=(-25,), wave_r=1),
    "lambai2":          dict(l_arm=(-135, 0, -32), r_arm=(-135, 0, 32), l_fore=(-25,), r_fore=(-25,), wave_r=1),
    "tunjuk":           dict(l_arm=(10, 0, -12), r_arm=(-88, -12, 8), r_fore=(-5,), body=(0, -10, 0)),
    "tunjuk_kiri":      dict(l_arm=(-88, 12, -8), r_arm=(10, 0, 12), l_fore=(-5,), body=(0, 10, 0)),
    "tunjuk_atas":      dict(l_arm=(8, 0, -10), r_arm=(-155, 0, 14), r_fore=(-10,), head=(12, 0, 0)),
    "ide":              dict(l_arm=(-20, 0, -18), r_arm=(-132, 10, 15), r_fore=(-45,), head=(8, -6, 4)),
    "pinggang":         dict(l_arm=(-15, 0, -48), r_arm=(-15, 0, 48), l_fore=(-55,), r_fore=(-55,)),
    "jempol":           dict(l_arm=(10, 0, -12), r_arm=(-82, -14, 18), r_fore=(-35,)),
    "silang":           dict(l_arm=(-48, 35, -10), r_arm=(-48, -35, 10), l_fore=(-55,), r_fore=(-55,)),
    "sorak":            dict(l_arm=(-155, 0, -25), r_arm=(-155, 0, 25), l_fore=(-15,), r_fore=(-15,)),
    "peregangan":       dict(l_arm=(-166, 0, -18), r_arm=(-166, 0, 18), l_fore=(-10,), r_fore=(-10,), head=(8, 0, 0)),
    "garuk":            dict(l_arm=(8, 0, -10), r_arm=(-125, -18, 22), r_fore=(-85,), head=(-4, 8, -6)),
    "mikir":            dict(l_arm=(-25, 20, -20), r_arm=(-72, -25, 12), r_fore=(-85,), head=(-6, 10, -5)),
    "dagu":             dict(l_arm=(-40, 25, -18), r_arm=(-76, -24, 10), r_fore=(-90,)),
    "kaget":            dict(l_arm=(-108, 0, -34), r_arm=(-108, 0, 34), l_fore=(-35,), r_fore=(-35,), body=(-8, 0, 0)),
    "sedih":            dict(l_arm=(14, 0, -5), r_arm=(14, 0, 5), body=(12, 0, 0), head=(-18, 0, 0)),
    "marah":            dict(l_arm=(-35, 0, -24), r_arm=(-35, 0, 24), l_fore=(-45,), r_fore=(-45,), body=(8, 0, 0)),
    "kepal":            dict(l_arm=(-55, 0, -18), r_arm=(-55, 0, 18), l_fore=(-55,), r_fore=(-55,)),
    "menyerahkan":      dict(l_arm=(-68, 14, -8), r_arm=(-68, -14, 8), l_fore=(-18,), r_fore=(-18,), body=(8, 0, 0)),
    "angkat_tangan":    dict(l_arm=(8, 0, -10), r_arm=(-162, 0, 12)),
    "angkat_bahu":      dict(l_arm=(-38, 0, -42), r_arm=(-38, 0, 42), l_fore=(-62,), r_fore=(-62,), head=(0, 0, 6)),
    "tepuk":            dict(l_arm=(-65, 28, -10), r_arm=(-65, -28, 10), l_fore=(-45,), r_fore=(-45,)),
    "menguap":          dict(l_arm=(8, 0, -10), r_arm=(-96, -25, 10), r_fore=(-85,), head=(10, 0, 0)),
    "pegang_dada":      dict(l_arm=(10, 0, -10), r_arm=(-58, -32, 12), r_fore=(-75,)),
    "hormat":           dict(l_arm=(6, 0, -8), r_arm=(-122, -16, 22), r_fore=(-95,)),
    "membungkuk":       dict(l_arm=(22, 0, -8), r_arm=(22, 0, 8), body=(28, 0, 0), head=(-12, 0, 0)),
    "lihat_jendela":    dict(l_arm=(-40, 0, -12), r_arm=(-40, 0, 12), head=(6, 18, 0)),
    "pegang_hp":        dict(l_arm=(-50, 18, -12), r_arm=(-64, -20, 12), r_fore=(-42,)),
    "pegang_buku":      dict(l_arm=(-58, 22, -12), r_arm=(-58, -22, 12), l_fore=(-40,), r_fore=(-40,)),
    "menulis":          dict(l_arm=(-52, 18, -12), r_arm=(-66, -16, 10), r_fore=(-35,), head=(-10, 0, 0)),
    "jalan":            dict(walk=1),
    "lari":             dict(run=1),
    "berjinjit":        dict(walk=0.6, body=(8, 0, 0)),
    "duduk":            dict(sit=1, l_arm=(-24, 0, -10), r_arm=(-24, 0, 10), l_fore=(-30,), r_fore=(-30,)),
    "duduk_santai":     dict(sit=1, l_arm=(-18, 0, -18), r_arm=(-32, 0, 16), body=(-8, 0, 0)),
    "duduk_ketik":      dict(sit=1, type=1, body=(8, 0, 0), head=(-10, 0, 0)),
    "ketik":            dict(sit=1, type=1, body=(8, 0, 0), head=(-10, 0, 0)),
    "duduk_peregangan": dict(sit=1, l_arm=(-164, 0, -16), r_arm=(-164, 0, 16), l_fore=(-10,), r_fore=(-10,), head=(8, 0, 0), body=(-6, 0, 0)),
    "duduk_nulis":      dict(sit=1, l_arm=(-54, 15, -10), r_arm=(-64, -15, 10), l_fore=(-38,), r_fore=(-38,), body=(10, 0, 0), head=(-12, 0, 0)),
    "duduk_game":       dict(sit=1, l_arm=(-62, 22, -10), r_arm=(-62, -22, 10), l_fore=(-34,), r_fore=(-34,)),
    "duduk_hp":         dict(sit=1, l_arm=(-48, 16, -12), r_arm=(-66, -20, 10), r_fore=(-46,), head=(-14, 0, 0)),
    "duduk_kopi":       dict(sit=1, l_arm=(-24, 0, -10), r_arm=(-68, -14, 10), r_fore=(-52,)),
    "duduk_sorak":      dict(sit=1, l_arm=(-156, 0, -24), r_arm=(-156, 0, 24)),
    "tidur":            dict(lie=1, l_arm=(8, 0, -14), r_arm=(8, 0, 14)),
}


def state(**kw):
    st = dict(
        pose="diam", pose2=None, mix=0.0, expr="senang", hadap="depan",
        lihat=(0.0, 0.0), blink=0.0, open_amt=0.0, bawa=None, ransel=False,
        t=0.0, phase=0.0, amp=0.0,
    )
    st.update(kw)
    return st


def _interp_pose(p1, p2, m):
    def g(p, k, d):
        return p.get(k, d)
    out = {}
    for k in ("l_arm", "r_arm", "l_leg", "r_leg", "body", "head"):
        a = g(p1, k, (0.0, 0.0, 0.0))
        b = g(p2, k, (0.0, 0.0, 0.0))
        out[k] = tuple(lerp(a[i] if i < len(a) else 0.0, b[i] if i < len(b) else 0.0, m) for i in range(3))
    for k in ("l_fore", "r_fore"):
        a = g(p1, k, (0.0,))
        b = g(p2, k, (0.0,))
        out[k] = lerp(a[0], b[0], m)
    for k in ("sit", "lie", "walk", "run", "type", "wave_r"):
        out[k] = lerp(float(p1.get(k, 0.0)), float(p2.get(k, 0.0)), m)
    return out


def _xform_rbox(sc, origin, mat, local_center, size, color, roundness=0.36, seg=1, lrot=None, **kw):
    c_world = origin + mat @ np.array(local_center, dtype=np.float32)
    m_use = mat if lrot is None else (mat @ euler_mat(*lrot))
    sc.rbox(c_world, size, color, roundness=roundness, seg=seg, mat=m_use, **kw)


def _xform_box(sc, origin, mat, local_center, size, color, lrot=None, **kw):
    c_world = origin + mat @ np.array(local_center, dtype=np.float32)
    m_use = mat if lrot is None else (mat @ euler_mat(*lrot))
    sc.box(c_world, size, color, mat=m_use, **kw)


class TokohVoxel:
    def __init__(self, spec="kribo"):
        self.p = casting(spec)

    def head_anchor(self, pos, skala=1.0, pose="diam"):
        p_spec = POSE.get(pose, POSE["diam"])
        y_top = 1.85
        if p_spec.get("sit"):
            y_top -= 0.28
        elif p_spec.get("lie"):
            y_top = 0.55
        if self.p.get("tipe") == "robo":
            y_top = 0.95
        elif self.p.get("tipe") == "kucing":
            y_top = 0.52
        return (pos[0], pos[1] + y_top * skala * self.p.get("skala", 1.0), pos[2])

    def _yaw_from_hadap(self, hadap):
        if isinstance(hadap, (int, float)):
            return float(hadap)
        return {
            "depan": 0.0, "belakang": 180.0, "kanan": 90.0, "kiri": -90.0,
            "serong_kanan": 34.0, "serong_kiri": -34.0,
        }.get(hadap, 0.0)

    def draw(self, sc, pos, st, skala=1.0):
        s = float(skala) * float(self.p.get("skala", 1.0))
        t = float(st.get("t", 0.0))
        yaw = self._yaw_from_hadap(st.get("hadap", "depan"))

        if self.p.get("tipe") == "robo":
            self._draw_robo(sc, pos, st, s, yaw, t)
            return
        if self.p.get("tipe") == "kucing":
            self._draw_kucing(sc, pos, st, s, yaw, t)
            return

        p1 = POSE.get(st.get("pose", "diam"), POSE["diam"])
        p2 = POSE.get(st.get("pose2") or st.get("pose", "diam"), p1)
        m = clamp(float(st.get("mix", 0.0)))
        P = _interp_pose(p1, p2, m)

        amp = float(st.get("amp", 0.0))
        ph = float(st.get("phase", t * 6.5))
        if P["walk"] > 0.1 or P["run"] > 0.1 or amp > 0.05:
            sp = 1.0 if P["run"] > 0.3 else 0.72
            cyc = math.sin(ph) * max(amp, P["walk"], P["run"])
            swing = 38.0 * sp * (1.25 if P["run"] > 0.3 else 1.0)
            P["l_leg"] = (swing * cyc, 0.0, 0.0)
            P["r_leg"] = (-swing * cyc, 0.0, 0.0)
            P["l_arm"] = (-swing * 0.8 * cyc, 0.0, -8.0)
            P["r_arm"] = (swing * 0.8 * cyc, 0.0, 8.0)
            bob = abs(math.cos(ph)) * 0.045 * s
        else:
            bob = math.sin(t * 2.2) * 0.012 * s

        if P["type"] > 0.1:
            tap_l = math.sin(t * 16.0) * 8.0
            tap_r = math.sin(t * 16.0 + 2.4) * 8.0
            P["l_arm"] = (-68.0 + tap_l, 16.0, -8.0)
            P["r_arm"] = (-68.0 + tap_r, -16.0, 8.0)
            P["l_fore"] = -34.0 - tap_l * 0.6
            P["r_fore"] = -34.0 - tap_r * 0.6

        if P["wave_r"] > 0.1:
            P["r_arm"] = (P["r_arm"][0], P["r_arm"][1], P["r_arm"][2] + math.sin(t * 8.0) * 14.0)

        px, py, pz = pos
        if P["sit"] < 0.5 and P["lie"] < 0.5:
            sc.drop_shadow(px, py, pz, 0.28 * s, 0.22 * s, 0.28)

        pelvis_y = 0.48 - P["sit"] * 0.26
        root_origin = np.array([px, py + pelvis_y * s + bob, pz], dtype=np.float32)
        root_mat = euler_mat(0.0, yaw, 0.0)
        if P["lie"] > 0.5:
            root_origin = np.array([px, py + 0.28 * s, pz], dtype=np.float32)
            root_mat = euler_mat(-90.0 * P["lie"], yaw, 0.0)

        body_mat = root_mat @ euler_mat(*P["body"])
        bw = float(self.p.get("badan_lebar", 1.0))

        kulit = warna(self.p.get("kulit"), (232, 184, 146))
        baju = warna(self.p.get("kemeja"), TEAL)
        bawah_col = warna(self.p.get("bawah_warna"), (44, 46, 54))
        sepatu_col = warna(self.p.get("sepatu"), (32, 34, 42))

        # ------------------ KAKI (chamfered octagonal prism + sepatu tumpul)
        leg_sep = 0.125 * s * bw
        thigh_l_rot = (-84.0, 0.0, 0.0) if P["sit"] > 0.5 else P["l_leg"]
        thigh_r_rot = (-84.0, 0.0, 0.0) if P["sit"] > 0.5 else P["r_leg"]
        shin_l_rot = (84.0, 0.0, 0.0) if P["sit"] > 0.5 else (0.0, 0.0, 0.0)
        shin_r_rot = (84.0, 0.0, 0.0) if P["sit"] > 0.5 else (0.0, 0.0, 0.0)

        for side, sx, trot, srot in ((-1, -leg_sep, thigh_l_rot, shin_l_rot), (1, leg_sep, thigh_r_rot, shin_r_rot)):
            hip_o = root_origin + root_mat @ np.array([sx, 0.0, 0.0], dtype=np.float32)
            tmat = root_mat @ euler_mat(*trot)
            pant_col = kulit if self.p.get("bawah") == "rok" else bawah_col
            _xform_rbox(sc, hip_o, tmat, (0.0, -0.11 * s, 0.0), (0.148 * s, 0.23 * s, 0.152 * s), pant_col, roundness=0.54, seg=1, cast_refl=True)
            knee_o = hip_o + tmat @ np.array([0.0, -0.22 * s, 0.0], dtype=np.float32)
            smat = tmat @ euler_mat(*srot)
            _xform_rbox(sc, knee_o, smat, (0.0, -0.10 * s, 0.0), (0.138 * s, 0.21 * s, 0.142 * s), pant_col, roundness=0.54, seg=1, cast_refl=True)
            foot_c = (0.0, -0.225 * s, 0.038 * s)
            if self.p.get("sepatu_sneaker"):
                _xform_rbox(sc, knee_o, smat, foot_c, (0.158 * s, 0.098 * s, 0.235 * s), (28, 30, 38), roundness=0.52, seg=1, cast_refl=True)
                _xform_rbox(sc, knee_o, smat, (0.0, -0.244 * s, 0.125 * s), (0.152 * s, 0.056 * s, 0.08 * s), PUTIH, roundness=0.55, seg=1, bias=-0.01)
                _xform_rbox(sc, knee_o, smat, (0.0, -0.268 * s, 0.038 * s), (0.160 * s, 0.026 * s, 0.236 * s), PUTIH, roundness=0.45, seg=1, bias=-0.01)
            else:
                _xform_rbox(sc, knee_o, smat, foot_c, (0.152 * s, 0.098 * s, 0.225 * s), sepatu_col, roundness=0.52, seg=1, cast_refl=True)

        # ------------------ BADAN & BAJU (chamfered low-poly)
        torso_w = 0.44 * s * bw
        torso_h = 0.54 * s
        torso_d = 0.29 * s
        if self.p.get("bawah") == "rok":
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.03 * s, 0.0), (torso_w * 1.12, 0.25 * s, torso_d * 1.18), bawah_col, roundness=0.38, seg=1, cast_refl=True)
        _xform_rbox(sc, root_origin, body_mat, (0.0, 0.27 * s, 0.0), (torso_w, torso_h, torso_d), baju, roundness=0.30, seg=1, cast_refl=True)

        z_front = torso_d * 0.5 + 0.010 * s
        if self.p.get("blazer"):
            inner = warna(self.p.get("kemeja_dalam"), PUTIH)
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.30 * s, z_front), (0.15 * s, 0.41 * s, 0.024 * s), inner, roundness=0.40, seg=1, bias=-0.02)
            _xform_rbox(sc, root_origin, body_mat, (-0.11 * s, 0.34 * s, z_front + 0.005 * s), (0.072 * s, 0.28 * s, 0.024 * s), gelap(baju, 0.16), roundness=0.40, seg=1, bias=-0.02)
            _xform_rbox(sc, root_origin, body_mat, (0.11 * s, 0.34 * s, z_front + 0.005 * s), (0.072 * s, 0.28 * s, 0.024 * s), gelap(baju, 0.16), roundness=0.40, seg=1, bias=-0.02)
        if self.p.get("hoodie"):
            # Lis pinggang bawah hoodie + tudung belakang + kantong kanguru + 2 tali putih
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.028 * s, 0.0), (torso_w * 1.03, 0.075 * s, torso_d * 1.04), gelap(baju, 0.26), roundness=0.52, seg=1)
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.50 * s, -torso_d * 0.38), (torso_w * 0.84, 0.15 * s, 0.20 * s), gelap(baju, 0.22), roundness=0.48, seg=1)
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.145 * s, z_front + 0.004 * s), (torso_w * 0.58, 0.145 * s, 0.036 * s), gelap(baju, 0.28), roundness=0.35, seg=1, bias=-0.02)
            _xform_rbox(sc, root_origin, body_mat, (-0.062 * s, 0.40 * s, z_front + 0.005 * s), (0.026 * s, 0.155 * s, 0.024 * s), PUTIH, roundness=0.62, seg=1, bias=-0.03)
            _xform_rbox(sc, root_origin, body_mat, (0.062 * s, 0.40 * s, z_front + 0.005 * s), (0.026 * s, 0.155 * s, 0.024 * s), PUTIH, roundness=0.62, seg=1, bias=-0.03)
        if self.p.get("dasi_kupu"):
            _xform_rbox(sc, root_origin, body_mat, (-0.056 * s, 0.485 * s, z_front + 0.012 * s), (0.078 * s, 0.066 * s, 0.032 * s), (26, 28, 34), roundness=0.45, seg=1, lrot=(0, 0, -10), bias=-0.03)
            _xform_rbox(sc, root_origin, body_mat, (0.056 * s, 0.485 * s, z_front + 0.012 * s), (0.078 * s, 0.066 * s, 0.032 * s), (26, 28, 34), roundness=0.45, seg=1, lrot=(0, 0, 10), bias=-0.03)
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.485 * s, z_front + 0.018 * s), (0.044 * s, 0.048 * s, 0.036 * s), (18, 18, 24), roundness=0.55, seg=1, bias=-0.04)
        elif self.p.get("dasi"):
            dc = warna(self.p.get("dasi"), BIRU)
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.34 * s, z_front), (0.07 * s, 0.29 * s, 0.026 * s), dc, roundness=0.42, seg=1, bias=-0.02)
        if st.get("ransel"):
            _xform_rbox(sc, root_origin, body_mat, (0.0, 0.30 * s, -torso_d * 0.5 - 0.10 * s), (torso_w * 0.78, 0.40 * s, 0.19 * s), (74, 86, 128), roundness=0.38, seg=1)

        # ------------------ LENGAN CHAMFERED + CUFF + TANGAN BERJEMPOL
        sh_x = torso_w * 0.5 + 0.075 * s
        sh_y = 0.45 * s
        sleeve_col = baju
        fore_col = baju if not self.p.get("lengan_pendek", False) else kulit
        for side, sx, arot, frot in ((-1, -sh_x, P["l_arm"], P["l_fore"]), (1, sh_x, P["r_arm"], P["r_fore"])):
            sh_o = root_origin + body_mat @ np.array([sx, sh_y, 0.0], dtype=np.float32)
            amat = body_mat @ euler_mat(*arot)
            _xform_rbox(sc, sh_o, amat, (0.0, -0.10 * s, 0.0), (0.132 * s, 0.22 * s, 0.132 * s), sleeve_col, roundness=0.56, seg=1, cast_refl=True)
            el_o = sh_o + amat @ np.array([0.0, -0.20 * s, 0.0], dtype=np.float32)
            fmat = amat @ euler_mat(frot, 0.0, 0.0)
            _xform_rbox(sc, el_o, fmat, (0.0, -0.095 * s, 0.0), (0.118 * s, 0.20 * s, 0.118 * s), fore_col, roundness=0.56, seg=1, cast_refl=True)
            if not self.p.get("lengan_pendek", False):
                _xform_rbox(sc, el_o, fmat, (0.0, -0.175 * s, 0.0), (0.126 * s, 0.048 * s, 0.126 * s), gelap(baju, 0.25), roundness=0.56, seg=1)
            hand_o = el_o + fmat @ np.array([0.0, -0.215 * s, 0.0], dtype=np.float32)
            _xform_rbox(sc, hand_o, fmat, (0.0, 0.0, 0.0), (0.105 * s, 0.118 * s, 0.088 * s), kulit, roundness=0.58, seg=1)
            # Jempol mungil chamfered
            _xform_rbox(sc, hand_o, fmat, (-side * 0.052 * s, 0.015 * s, 0.025 * s), (0.045 * s, 0.070 * s, 0.045 * s), kulit, roundness=0.64, seg=1, lrot=(12.0, 0.0, side * 26.0))
            bawa = st.get("bawa")
            if bawa:
                bname = bawa["jenis"] if isinstance(bawa, dict) else bawa
                bhand = bawa.get("tangan", "kanan") if isinstance(bawa, dict) else "kanan"
                if (side == 1 and bhand == "kanan") or (side == -1 and bhand == "kiri"):
                    BD.draw_prop(sc, bname, tuple(hand_o.tolist()), s=s * 0.85, t=t, rot=(0.0, yaw, 0.0))

        # ------------------ LEHER & KEPALA CHAMFERED + TELINGA
        neck_o = root_origin + body_mat @ np.array([0.0, 0.55 * s, 0.0], dtype=np.float32)
        _xform_rbox(sc, neck_o, body_mat, (0.0, 0.02 * s, 0.0), (0.18 * s, 0.10 * s, 0.16 * s), kulit, roundness=0.50, seg=1)
        head_o = root_origin + body_mat @ np.array([0.0, 0.85 * s, 0.0], dtype=np.float32)
        head_mat = body_mat @ euler_mat(*P["head"])
        hw, hh, hd = 0.58 * s, 0.56 * s, 0.52 * s
        _xform_rbox(sc, head_o, head_mat, (0.0, 0.0, 0.0), (hw, hh, hd), kulit, roundness=0.28, seg=1, cast_refl=True)
        _xform_rbox(sc, head_o, head_mat, (-hw * 0.51, -0.02 * s, -0.01 * s), (0.068 * s, 0.135 * s, 0.115 * s), gelap(kulit, 0.08), roundness=0.60, seg=1)
        _xform_rbox(sc, head_o, head_mat, (hw * 0.51, -0.02 * s, -0.01 * s), (0.068 * s, 0.135 * s, 0.115 * s), gelap(kulit, 0.08), roundness=0.60, seg=1)

        if self.p.get("hijab"):
            self._draw_hijab_3d(sc, head_o, head_mat, hw, hh, hd, s, root_origin, body_mat)
        else:
            self._draw_hair_3d(sc, head_o, head_mat, hw, hh, hd, s)

        self._draw_face_3d(sc, head_o, head_mat, hw, hh, hd, s, st, kulit)

    def _draw_hair_3d(self, sc, head_o, head_mat, hw, hh, hd, s):
        style = self.p.get("rambut", "rapi")
        hcol = warna(self.p.get("rambut_warna"), HITAM)
        if style == "afro":
            # Afro Kribo berprofil bundar dari gumpalan low-poly chamfered bertumpuk (wajah tetap bersih!)
            puffs = [
                ((0.0, 0.34, -0.04), (0.64, 0.34, 0.58), (0, 0, 0)),
                ((0.0, 0.44, -0.04), (0.48, 0.24, 0.46), (0, 12, 0)),
                ((-0.24, 0.36, -0.02), (0.34, 0.30, 0.44), (8, 0, 18)),
                ((0.24, 0.36, -0.02), (0.34, 0.30, 0.44), (8, 0, -18)),
                ((-0.34, 0.16, -0.05), (0.28, 0.36, 0.46), (0, 10, 14)),
                ((0.34, 0.16, -0.05), (0.28, 0.36, 0.46), (0, -10, -14)),
                ((-0.33, -0.02, -0.10), (0.22, 0.26, 0.34), (0, 0, 10)),
                ((0.33, -0.02, -0.10), (0.22, 0.26, 0.34), (0, 0, -10)),
                ((-0.14, 0.22, 0.18), (0.26, 0.14, 0.20), (10, 0, 10)),
                ((0.14, 0.22, 0.18), (0.26, 0.14, 0.20), (10, 0, -10)),
                ((0.0, 0.06, -0.28), (0.68, 0.52, 0.28), (0, 0, 0)),
                ((-0.22, 0.12, -0.24), (0.32, 0.36, 0.26), (0, 18, 0)),
                ((0.22, 0.12, -0.24), (0.32, 0.36, 0.26), (0, -18, 0)),
            ]
            for c, sz, lr in puffs:
                _xform_rbox(sc, head_o, head_mat, (c[0] * s, c[1] * s, c[2] * s), (sz[0] * s, sz[1] * s, sz[2] * s), hcol, roundness=0.68, seg=1, lrot=lr, cast_refl=True)
        elif style in ("jambul_kode", "jambul"):
            # Puncak kepala + belakang + cambang samping + 2 poni melengkung di dahi + 2 helai jambul miring atas
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.26 * s, -0.02 * s), (hw * 1.06, 0.16 * s, hd * 1.08), hcol, roundness=0.45, seg=1, cast_refl=True)
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.02 * s, -hd * 0.46), (hw * 1.02, hh * 0.88, 0.15 * s), hcol, roundness=0.45, seg=1)
            _xform_rbox(sc, head_o, head_mat, (-hw * 0.48, 0.12 * s, -0.05 * s), (0.10 * s, 0.28 * s, hd * 0.78), hcol, roundness=0.50, seg=1)
            _xform_rbox(sc, head_o, head_mat, (hw * 0.48, 0.12 * s, -0.05 * s), (0.10 * s, 0.28 * s, hd * 0.78), hcol, roundness=0.50, seg=1)
            # Dua poni lembut di atas alis (seperti di screenshot referensi!)
            _xform_rbox(sc, head_o, head_mat, (-0.125 * s, 0.195 * s, hd * 0.45), (0.24 * s, 0.105 * s, 0.14 * s), hcol, roundness=0.64, seg=1, lrot=(8.0, 0.0, 6.0))
            _xform_rbox(sc, head_o, head_mat, (0.125 * s, 0.195 * s, hd * 0.45), (0.24 * s, 0.105 * s, 0.14 * s), hcol, roundness=0.64, seg=1, lrot=(8.0, 0.0, -6.0))
            # Dua helai jambul kecil di atas kepala
            _xform_rbox(sc, head_o, head_mat, (0.02 * s, 0.365 * s, 0.03 * s), (0.065 * s, 0.13 * s, 0.065 * s), hcol, roundness=0.65, seg=1, lrot=(10.0, 0.0, -32.0))
            _xform_rbox(sc, head_o, head_mat, (0.095 * s, 0.345 * s, -0.01 * s), (0.055 * s, 0.105 * s, 0.055 * s), gelap(hcol, 0.08), roundness=0.65, seg=1, lrot=(-8.0, 0.0, -45.0))
        elif style == "keriting":
            for ix in (-0.20, 0.0, 0.20):
                _xform_rbox(sc, head_o, head_mat, (ix * s, 0.31 * s, 0.0), (0.25 * s, 0.22 * s, hd * 1.04), hcol, roundness=0.68, seg=1)
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.04 * s, -hd * 0.46), (hw * 1.04, hh * 0.88, 0.15 * s), hcol, roundness=0.45, seg=1)
        elif style == "kuncir":
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.25 * s, 0.0), (hw * 1.05, 0.15 * s, hd * 1.05), hcol, roundness=0.50, seg=1)
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.02 * s, -hd * 0.46), (hw * 1.02, hh * 0.88, 0.13 * s), hcol, roundness=0.45, seg=1)
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.18 * s, -hd * 0.62), (0.16 * s, 0.34 * s, 0.16 * s), hcol, roundness=0.64, seg=1, lrot=(16.0, 0.0, 0.0))
        elif style == "bob":
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.25 * s, 0.0), (hw * 1.08, 0.16 * s, hd * 1.08), hcol, roundness=0.52, seg=1)
            _xform_rbox(sc, head_o, head_mat, (-hw * 0.49, -0.04 * s, -0.03 * s), (0.11 * s, 0.43 * s, hd * 0.94), hcol, roundness=0.52, seg=1)
            _xform_rbox(sc, head_o, head_mat, (hw * 0.49, -0.04 * s, -0.03 * s), (0.11 * s, 0.43 * s, hd * 0.94), hcol, roundness=0.52, seg=1)
            _xform_rbox(sc, head_o, head_mat, (0.0, -0.02 * s, -hd * 0.46), (hw * 1.05, hh * 1.00, 0.15 * s), hcol, roundness=0.45, seg=1)
        elif style == "botak":
            if self.p.get("peci"):
                _xform_rbox(sc, head_o, head_mat, (0.0, 0.30 * s, 0.0), (hw * 0.92, 0.18 * s, hd * 0.92), (24, 24, 30), roundness=0.46, seg=1)
        else:
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.25 * s, -0.01 * s), (hw * 1.05, 0.14 * s, hd * 1.05), hcol, roundness=0.48, seg=1)
            _xform_rbox(sc, head_o, head_mat, (0.0, 0.02 * s, -hd * 0.46), (hw * 1.02, hh * 0.88, 0.13 * s), hcol, roundness=0.45, seg=1)

    def _draw_hijab_3d(self, sc, head_o, head_mat, hw, hh, hd, s, root_origin, body_mat):
        hc = warna(self.p.get("hijab"), (34, 36, 46))
        ht = warna(self.p.get("hijab_tua"), gelap(hc, 0.18))
        _xform_rbox(sc, head_o, head_mat, (0.0, 0.25 * s, -0.02 * s), (hw * 1.13, 0.19 * s, hd * 1.13), hc, roundness=0.52, seg=1, cast_refl=True)
        _xform_rbox(sc, head_o, head_mat, (-hw * 0.51, -0.02 * s, -0.02 * s), (0.125 * s, hh * 1.02, hd * 1.06), hc, roundness=0.54, seg=1, lrot=(0, 0, -5))
        _xform_rbox(sc, head_o, head_mat, (hw * 0.51, -0.02 * s, -0.02 * s), (0.125 * s, hh * 1.02, hd * 1.06), hc, roundness=0.54, seg=1, lrot=(0, 0, 5))
        _xform_rbox(sc, head_o, head_mat, (0.0, -0.02 * s, -hd * 0.48), (hw * 1.12, hh * 1.04, 0.16 * s), hc, roundness=0.48, seg=1)
        _xform_rbox(sc, head_o, head_mat, (0.0, -0.27 * s, 0.04 * s), (hw * 1.06, 0.115 * s, hd * 0.98), ht, roundness=0.56, seg=1)
        _xform_rbox(sc, root_origin, body_mat, (0.0, 0.48 * s, 0.02 * s), (0.50 * s, 0.17 * s, 0.35 * s), hc, roundness=0.48, seg=1)

    def _draw_face_3d(self, sc, head_o, head_mat, hw, hh, hd, s, st, kulit):
        ex = get_expr(st.get("expr", "senang"))
        zf = hd * 0.5 + 0.012 * s
        eye_y = 0.008 * s
        eye_x = 0.132 * s
        blink = float(st.get("blink", 0.0))
        eyes = "arc_dn" if blink > 0.45 else ex["eyes"]
        lx, ly = st.get("lihat", (0.0, 0.0))
        if lx == 0.0 and ly == 0.0 and "look" in ex:
            lx, ly = ex["look"]

        # Hidung 3D mungil chamfered di antara mata
        _xform_rbox(sc, head_o, head_mat, (0.0, -0.045 * s, zf + 0.012 * s), (0.062 * s, 0.072 * s, 0.062 * s), gelap(kulit, 0.09), roundness=0.62, seg=1, bias=-0.05)

        # Pipi merona lembut
        bl = ex.get("blush", 0.0)
        if bl > 0.1:
            bc = mix(kulit, (216, 128, 122), clamp(bl * 0.72, 0.25, 0.75))
            _xform_rbox(sc, head_o, head_mat, (-0.185 * s, -0.096 * s, zf), (0.074 * s, 0.040 * s, 0.016 * s), bc, roundness=0.52, seg=1, bias=-0.03)
            _xform_rbox(sc, head_o, head_mat, (0.185 * s, -0.096 * s, zf), (0.074 * s, 0.040 * s, 0.016 * s), bc, roundness=0.52, seg=1, bias=-0.03)

        # Mata (sklera putih + iris gelap + kilau seperti referensi)
        for side in (-1, 1):
            cx = side * eye_x
            if eyes in ("arc_up", "arc_dn"):
                dy_arc = 0.012 * s if eyes == "arc_up" else -0.010 * s
                _xform_rbox(sc, head_o, head_mat, (cx - 0.024 * s, eye_y, zf), (0.048 * s, 0.020 * s, 0.018 * s), OUT, roundness=0.5, seg=1, lrot=(0, 0, -24 if eyes == "arc_up" else 24), bias=-0.04)
                _xform_rbox(sc, head_o, head_mat, (cx + 0.024 * s, eye_y, zf), (0.048 * s, 0.020 * s, 0.018 * s), OUT, roundness=0.5, seg=1, lrot=(0, 0, 24 if eyes == "arc_up" else -24), bias=-0.04)
                _xform_rbox(sc, head_o, head_mat, (cx, eye_y + dy_arc, zf), (0.042 * s, 0.020 * s, 0.018 * s), OUT, roundness=0.5, seg=1, bias=-0.04)
            elif eyes == "wink" and side == 1:
                _xform_rbox(sc, head_o, head_mat, (cx, eye_y, zf), (0.084 * s, 0.022 * s, 0.018 * s), OUT, roundness=0.5, seg=1, bias=-0.04)
            elif eyes == "half":
                _xform_rbox(sc, head_o, head_mat, (cx, eye_y - 0.012 * s, zf), (0.078 * s, 0.048 * s, 0.018 * s), (22, 28, 38), roundness=0.45, seg=1, bias=-0.04)
                _xform_rbox(sc, head_o, head_mat, (cx, eye_y + 0.024 * s, zf + 0.004 * s), (0.088 * s, 0.022 * s, 0.018 * s), gelap(kulit, 0.14), roundness=0.45, seg=1, bias=-0.04)
            else:
                ox = clamp(lx, -1, 1) * 0.012 * s
                oy = clamp(ly, -1, 1) * 0.010 * s
                sc_w = 0.086 * s if eyes in ("wide", "spark") else 0.078 * s
                sc_h = 0.108 * s if eyes in ("wide", "spark") else 0.098 * s
                if eyes != "dot":
                    _xform_rbox(sc, head_o, head_mat, (cx, eye_y, zf), (sc_w, sc_h, 0.014 * s), (244, 248, 252), roundness=0.38, seg=1, bias=-0.03)
                ir_w = 0.048 * s if eyes == "dot" else 0.056 * s
                ir_h = 0.052 * s if eyes == "dot" else (0.072 * s if eyes == "wide" else 0.092 * s)
                _xform_rbox(sc, head_o, head_mat, (cx - side * 0.008 * s + ox, eye_y + oy, zf + 0.005 * s), (ir_w, ir_h, 0.016 * s), (22, 28, 38), roundness=0.42, seg=1, bias=-0.04)
                if eyes != "dot":
                    _xform_rbox(sc, head_o, head_mat, (cx - side * 0.008 * s + ox - 0.014 * s, eye_y + oy + 0.020 * s, zf + 0.010 * s), (0.022 * s, 0.024 * s, 0.012 * s), PUTIH, roundness=0.55, seg=1, bias=-0.05)

            # Alis chamfered
            by = eye_y + 0.078 * s
            br_off, br_l, br_r = ex.get("brow", (0, 0, 0))
            ang = (br_l if side == -1 else br_r) * 14.0 * (-1 if side == 1 else 1)
            _xform_rbox(sc, head_o, head_mat, (cx, by + br_off * 0.004 * s, zf + 0.006 * s), (0.082 * s, 0.020 * s, 0.018 * s), (36, 26, 24), roundness=0.55, seg=1, lrot=(0.0, 0.0, ang), bias=-0.04)

        # Mulut 3D (terbuka sesuai VO jika bicara aktif)
        my = -0.145 * s
        open_amt = float(st.get("open_amt", 0.0))
        mouth = ex.get("mouth", "smile")
        if open_amt > 0.14:
            mh = (0.032 + 0.068 * open_amt) * s
            _xform_rbox(sc, head_o, head_mat, (0.0, my, zf + 0.004 * s), (0.115 * s, mh, 0.020 * s), MERAH_TUA, roundness=0.48, seg=1, bias=-0.04)
            _xform_rbox(sc, head_o, head_mat, (0.0, my - mh * 0.24, zf + 0.008 * s), (0.078 * s, mh * 0.34, 0.016 * s), MERAH, roundness=0.50, seg=1, bias=-0.05)
        elif mouth in ("open", "grin"):
            _xform_rbox(sc, head_o, head_mat, (0.0, my, zf + 0.004 * s), (0.112 * s, 0.066 * s, 0.020 * s), MERAH_TUA, roundness=0.50, seg=1, bias=-0.04)
            _xform_rbox(sc, head_o, head_mat, (0.0, my + 0.018 * s, zf + 0.008 * s), (0.090 * s, 0.022 * s, 0.015 * s), PUTIH, roundness=0.40, seg=1, bias=-0.05)
        elif mouth in ("o", "yawn"):
            _xform_rbox(sc, head_o, head_mat, (0.0, my, zf + 0.004 * s), (0.064 * s, 0.068 * s, 0.020 * s), MERAH_TUA, roundness=0.65, seg=1, bias=-0.04)
        elif mouth == "gigit":
            _xform_rbox(sc, head_o, head_mat, (0.0, my, zf + 0.002 * s), (0.142 * s, 0.060 * s, 0.018 * s), OUT, roundness=0.45, seg=1, bias=-0.04)
            _xform_rbox(sc, head_o, head_mat, (0.0, my, zf + 0.006 * s), (0.122 * s, 0.042 * s, 0.020 * s), PUTIH, roundness=0.45, seg=1, bias=-0.05)
        else:
            _xform_rbox(sc, head_o, head_mat, (0.0, my, zf + 0.004 * s), (0.094 * s, 0.026 * s, 0.020 * s), (68, 32, 30), roundness=0.62, seg=1, bias=-0.04)

        if self.p.get("kumis"):
            _xform_rbox(sc, head_o, head_mat, (0.0, -0.098 * s, zf + 0.010 * s), (0.15 * s, 0.036 * s, 0.022 * s), (70, 72, 82), roundness=0.55, seg=1, bias=-0.05)
        if self.p.get("jenggot"):
            _xform_rbox(sc, head_o, head_mat, (0.0, -0.23 * s, zf * 0.92), (0.20 * s, 0.14 * s, 0.06 * s), (210, 212, 220), roundness=0.52, seg=1, bias=-0.04)

        # Kacamata 3D tipis ramping (kotak bersudut tumpul / bulat 8-sisi)
        kac = self.p.get("kacamata")
        if kac:
            gz = zf + 0.024 * s
            fc = (42, 28, 24)
            bw_g = 0.156 * s
            bh_g = 0.130 * s
            th = 0.020 * s
            for side in (-1, 1):
                gx = side * eye_x
                if kac == "bulat":
                    rad = 0.072 * s
                    for k in range(8):
                        a_deg = k * 45.0
                        a_rad = math.radians(a_deg)
                        rx_off = math.cos(a_rad) * rad
                        ry_off = math.sin(a_rad) * rad
                        _xform_rbox(sc, head_o, head_mat, (gx + rx_off, eye_y + ry_off, gz), (0.022 * s, 0.068 * s, 0.020 * s), fc, roundness=0.50, seg=1, lrot=(0.0, 0.0, a_deg), bias=-0.06)
                else:
                    _xform_rbox(sc, head_o, head_mat, (gx, eye_y, gz - 0.004 * s), (bw_g - th, bh_g - th, 0.008 * s), (220, 238, 252), roundness=0.35, seg=1, alpha=0.14, specular=0.85, bias=-0.05)
                    _xform_rbox(sc, head_o, head_mat, (gx, eye_y + bh_g * 0.5, gz), (bw_g + th * 0.5, th, 0.020 * s), fc, roundness=0.50, seg=1, bias=-0.06)
                    _xform_rbox(sc, head_o, head_mat, (gx, eye_y - bh_g * 0.5, gz), (bw_g + th * 0.5, th, 0.020 * s), fc, roundness=0.50, seg=1, bias=-0.06)
                    _xform_rbox(sc, head_o, head_mat, (gx - bw_g * 0.5, eye_y, gz), (th, bh_g + th * 0.5, 0.020 * s), fc, roundness=0.50, seg=1, bias=-0.06)
                    _xform_rbox(sc, head_o, head_mat, (gx + bw_g * 0.5, eye_y, gz), (th, bh_g + th * 0.5, 0.020 * s), fc, roundness=0.50, seg=1, bias=-0.06)
            _xform_rbox(sc, head_o, head_mat, (0.0, eye_y + 0.015 * s, gz), (0.105 * s, th, 0.020 * s), fc, roundness=0.50, seg=1, bias=-0.06)
            _xform_rbox(sc, head_o, head_mat, (-hw * 0.495, eye_y + 0.015 * s, 0.05 * s), (0.018 * s, th * 0.85, hd * 0.72), fc, roundness=0.45, seg=1)
            _xform_rbox(sc, head_o, head_mat, (hw * 0.495, eye_y + 0.015 * s, 0.05 * s), (0.018 * s, th * 0.85, hd * 0.72), fc, roundness=0.45, seg=1)

    # ------------------------------------------------------------------ ROBO (robot lampu oranye-teal chamfered)
    def _draw_robo(self, sc, pos, st, s, yaw, t):
        px, py, pz = pos
        col_main = warna(self.p.get("utama"), ORANYE)
        col_sub = warna(self.p.get("aksen"), TEAL)
        col_scr = warna(self.p.get("layar"), (30, 38, 48))
        col_glow = warna(self.p.get("cahaya"), (255, 198, 110))

        pose = st.get("pose", "diam")
        bob = math.sin(t * 3.2) * 0.022 * s
        tilt_z = 8.0 * math.sin(t * 1.9)
        tilt_x = -8.0 if pose in ("tanya", "mikir", "kaget") else (6.0 * math.sin(t * 2.5))
        if pose in ("sorak", "semangat"):
            bob += abs(math.sin(t * 7.0)) * 0.08 * s

        sc.drop_shadow(px, py, pz, 0.24 * s, 0.22 * s, 0.28)
        root = np.array([px, py, pz], dtype=np.float32)
        rmat = euler_mat(0.0, yaw, 0.0)

        _xform_rbox(sc, root, rmat, (-0.13 * s, 0.08 * s, 0.02 * s), (0.14 * s, 0.16 * s, 0.20 * s), col_sub, roundness=0.52, seg=1)
        _xform_rbox(sc, root, rmat, (0.13 * s, 0.08 * s, 0.02 * s), (0.14 * s, 0.16 * s, 0.20 * s), col_sub, roundness=0.52, seg=1)
        _xform_rbox(sc, root, rmat, (0.0, 0.36 * s + bob, 0.0), (0.44 * s, 0.40 * s, 0.34 * s), col_main, roundness=0.38, seg=1, cast_refl=True)
        _xform_rbox(sc, root, rmat, (0.0, 0.36 * s + bob, 0.18 * s), (0.28 * s, 0.22 * s, 0.032 * s), col_sub, roundness=0.45, seg=1, bias=-0.02)

        arm_ang = -110.0 if pose in ("lambai", "sorak", "ide") else -18.0
        for side in (-1, 1):
            a_o = root + rmat @ np.array([side * 0.27 * s, 0.44 * s + bob, 0.0], dtype=np.float32)
            amat = rmat @ euler_mat(arm_ang if side == 1 else -14.0, 0.0, side * 12.0)
            _xform_rbox(sc, a_o, amat, (0.0, -0.10 * s, 0.0), (0.10 * s, 0.24 * s, 0.11 * s), col_sub, roundness=0.58, seg=1)

        head_o = root + rmat @ np.array([0.0, 0.80 * s + bob, 0.0], dtype=np.float32)
        hmat = rmat @ euler_mat(tilt_x, 0.0, tilt_z)
        _xform_rbox(sc, head_o, hmat, (0.0, 0.0, 0.0), (0.56 * s, 0.46 * s, 0.42 * s), col_main, roundness=0.36, seg=1, cast_refl=True)
        _xform_rbox(sc, head_o, hmat, (0.0, 0.0, 0.205 * s), (0.50 * s, 0.40 * s, 0.024 * s), col_sub, roundness=0.36, seg=1, bias=-0.01)
        _xform_rbox(sc, head_o, hmat, (0.0, 0.0, 0.215 * s), (0.44 * s, 0.34 * s, 0.024 * s), col_scr, roundness=0.32, seg=1, specular=0.8, bias=-0.02)

        # Cincin mata bercahaya 8-sisi
        eye_c = col_glow if st.get("expr") not in ("kaget", "semangat") else (120, 235, 255)
        for k in range(8):
            ad = k * 45.0
            ar = math.radians(ad)
            _xform_rbox(sc, head_o, hmat, (math.cos(ar) * 0.072 * s, 0.02 * s + math.sin(ar) * 0.072 * s, 0.232 * s), (0.036 * s, 0.072 * s, 0.016 * s), eye_c, roundness=0.45, seg=1, lrot=(0, 0, ad), emissive=1.4, bias=-0.04)

        _xform_rbox(sc, head_o, hmat, (-0.12 * s, 0.31 * s, 0.0), (0.042 * s, 0.18 * s, 0.042 * s), ABU_TUA, roundness=0.5, seg=1)
        tip_pos = head_o + hmat @ np.array([-0.12 * s, 0.42 * s, 0.0], dtype=np.float32)
        sc.rbox(tip_pos, (0.088 * s, 0.088 * s, 0.088 * s), col_glow, roundness=0.68, seg=1, mat=hmat, emissive=1.5)

        lpos = head_o + hmat @ np.array([0.0, 0.02 * s, 0.35 * s], dtype=np.float32)
        sc.add_light(lpos, color=col_glow, intensity=1.35 * clamp(s * 1.4, 0.6, 1.4), radius=2.6, halo=0.22 * s)

    # ------------------------------------------------------------------ KUCING LOW-POLY
    def _draw_kucing(self, sc, pos, st, s, yaw, t):
        px, py, pz = pos
        col = warna(self.p.get("warna"), (232, 132, 54))
        col2 = terang(col, 0.35)
        sc.drop_shadow(px, py, pz, 0.22 * s, 0.24 * s, 0.24)
        root = np.array([px, py, pz], dtype=np.float32)
        rmat = euler_mat(0.0, yaw, 0.0)
        _xform_rbox(sc, root, rmat, (0.0, 0.18 * s, 0.0), (0.28 * s, 0.24 * s, 0.44 * s), col, roundness=0.48, seg=1, cast_refl=True)
        _xform_rbox(sc, root, rmat, (0.0, 0.36 * s, 0.22 * s), (0.26 * s, 0.24 * s, 0.24 * s), col, roundness=0.45, seg=1, cast_refl=True)
        _xform_rbox(sc, root, rmat, (-0.09 * s, 0.51 * s, 0.22 * s), (0.07 * s, 0.09 * s, 0.06 * s), col, roundness=0.48, seg=1)
        _xform_rbox(sc, root, rmat, (0.09 * s, 0.51 * s, 0.22 * s), (0.07 * s, 0.09 * s, 0.06 * s), col, roundness=0.48, seg=1)
        _xform_rbox(sc, root, rmat, (0.0, 0.31 * s, 0.345 * s), (0.14 * s, 0.09 * s, 0.02 * s), col2, roundness=0.5, seg=1, bias=-0.02)
        _xform_rbox(sc, root, rmat, (-0.06 * s, 0.39 * s, 0.348 * s), (0.04 * s, 0.04 * s, 0.015 * s), OUT, roundness=0.5, seg=1, bias=-0.03)
        _xform_rbox(sc, root, rmat, (0.06 * s, 0.39 * s, 0.348 * s), (0.04 * s, 0.04 * s, 0.015 * s), OUT, roundness=0.5, seg=1, bias=-0.03)
        wag = math.sin(t * 4.5) * 24.0
        t_o = root + rmat @ np.array([0.0, 0.24 * s, -0.22 * s], dtype=np.float32)
        tmat = rmat @ euler_mat(35.0, wag, 0.0)
        _xform_rbox(sc, t_o, tmat, (0.0, 0.16 * s, -0.05 * s), (0.06 * s, 0.30 * s, 0.06 * s), col, roundness=0.55, seg=1)
