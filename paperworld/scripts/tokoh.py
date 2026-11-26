# -*- coding: utf-8 -*-
"""
tokoh.py - karakter 3D Pop-Up Paper Craft (potongan karton berlapis) untuk PaperWorld.

Pemeran utama & bawaan:
  * luna   : gadis kertas berambut bob coklat + jambul melengkung, syal kuning berumbai,
             mantel koral berkancing kuning, kaki biru (gaya video referensi PaperWorld)
  * kribo  : wajib ada — afro kertas bergelombang penuh, kacamata kotak, baju teal + dasi kupu-kupu, sneaker
  * nadia  : chibi kertas berhijab hitam modern, kacamata bulat, blazer krem, rok gelap
  * kucing : kucing pop-up kertas kuning berdasi pita merah yang melambai
  * raka, bimo, dimas, sari, tika, ayah, ibu, guru, adik
"""
import math
import numpy as np
from paper import (
    OUT, KERTAS_TEPI, PUTIH, KRIM, HITAM, COKLAT_RAMBUT, KORAL, MERAH, MERAH_TUA,
    PIPI, BIRU, BIRU_TUA, BIRU_MUDA, TEAL, PINK, KUNING, ORANYE, HIJAU, HIJAU_TUA,
    COKLAT, COKLAT_TUA, UNGU, NAVY, ABU, KULIT, MINT,
    clamp, lerp, euler_mat, mix, gelap, terang,
    circle_2d, rrect_2d, coat_2d, cloud_afro_2d, bob_hair_2d, spiral_ahoge_2d, cat_silhouette_2d,
)
import benda as BD

WARNA = {
    "putih": PUTIH, "hitam": HITAM, "merah": MERAH, "koral": KORAL, "biru": BIRU,
    "biru_muda": BIRU_MUDA, "teal": TEAL, "pink": PINK, "kuning": KUNING,
    "oranye": ORANYE, "hijau": HIJAU, "ungu": UNGU, "coklat": COKLAT, "abu": ABU,
    "navy": NAVY, "krem": KRIM, "kulit": KULIT,
}


def warna(v, default=None):
    if v is None:
        return default
    if isinstance(v, str):
        return WARNA.get(v.lower(), default)
    return tuple(v)


PRESET = {
    "luna": dict(
        nama="Luna", tipe="humanoid", rambut="bob_ahoge", rambut_warna=COKLAT_RAMBUT,
        kulit=(242, 210, 180), kemeja=(216, 84, 60), mantel=True, syal=KUNING,
        kancing_kuning=True, bawah="celana", bawah_warna=BIRU, sepatu=COKLAT_TUA,
        mata_polos=True,
    ),
    "kribo": dict(
        nama="Kribo", tipe="humanoid", rambut="afro", rambut_warna=(28, 28, 34),
        kulit=(244, 206, 174), kacamata="kotak", kemeja=TEAL,
        dasi_kupu=True, bawah="celana", bawah_warna=(48, 50, 58), sepatu_sneaker=True,
    ),
    "nadia": dict(
        nama="Nadia", tipe="humanoid", hijab=(36, 38, 48), hijab_tua=(70, 74, 90),
        kulit=(248, 224, 196), kacamata="bulat", kemeja=(224, 194, 154),
        blazer=True, kemeja_dalam=PUTIH, bawah="rok", bawah_warna=(48, 50, 58), sepatu=(78, 54, 44),
    ),
    "kucing": dict(
        nama="Kucing Kertas", tipe="kucing", warna=(228, 168, 30), dasi=MERAH, skala=1.08,
    ),
    "raka": dict(
        nama="Raka", tipe="humanoid", rambut="jambul", rambut_warna=HITAM,
        kulit=KULIT, kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=NAVY,
    ),
    "bimo": dict(
        nama="Bimo", tipe="humanoid", rambut="keriting", rambut_warna=(72, 46, 34),
        kulit=KULIT, kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=NAVY,
    ),
    "dimas": dict(
        nama="Dimas", tipe="humanoid", rambut="rapi", rambut_warna=HITAM,
        kulit=KULIT, kacamata="kotak", kemeja=PUTIH, dasi=BIRU, bawah="celana", bawah_warna=NAVY,
    ),
    "sari": dict(
        nama="Sari", tipe="humanoid", hijab=(248, 246, 242), hijab_tua=ABU,
        kulit=KULIT, kemeja=PUTIH, dasi=MERAH, bawah="rok", bawah_warna=NAVY,
    ),
    "tika": dict(
        nama="Tika", tipe="humanoid", rambut="kuncir", rambut_warna=HITAM,
        kulit=KULIT, kemeja=PUTIH, dasi=MERAH, bawah="rok", bawah_warna=NAVY,
    ),
    "ayah": dict(
        nama="Ayah", tipe="humanoid", rambut="rapi", rambut_warna=(76, 78, 88),
        kumis=True, kulit=KULIT, kemeja=(192, 218, 244), bawah="celana", bawah_warna=NAVY, skala=1.06,
    ),
    "ibu": dict(
        nama="Ibu", tipe="humanoid", hijab=HIJAU, hijab_tua=HIJAU_TUA,
        kulit=KULIT, kemeja=(248, 232, 206), bawah="rok", bawah_warna=COKLAT_TUA, skala=1.02,
    ),
    "guru": dict(
        nama="Pak Guru", tipe="humanoid", rambut="uban", rambut_warna=(204, 206, 214),
        kacamata="kotak", kumis=True, kulit=KULIT, kemeja=(234, 228, 210), dasi=MERAH_TUA,
        bawah="celana", bawah_warna=NAVY, skala=1.05,
    ),
    "adik": dict(
        nama="Adik", tipe="humanoid", rambut="bob", rambut_warna=HITAM,
        kulit=KULIT, kemeja=KUNING, bawah="rok", bawah_warna=PINK, skala=0.82,
    ),
}


def casting(spec):
    if isinstance(spec, str):
        spec = {"dasar": spec}
    base = dict(PRESET.get(spec.get("dasar", "luna"), PRESET["luna"]))
    for k, v in spec.items():
        if k == "dasar":
            continue
        if isinstance(v, list) and len(v) == 3 and all(isinstance(i, (int, float)) for i in v):
            base[k] = tuple(int(c) for c in v)
        else:
            base[k] = v
    base.setdefault("skala", 1.0)
    return base


EKSPRESI = {
    "senang":   dict(eyes="oval", mouth="open", blush=0.75),
    "tenang":   dict(eyes="oval", mouth="smile", blush=0.65),
    "fokus":    dict(eyes="oval", mouth="flat", blush=0.55),
    "tertawa":  dict(eyes="arc_up", mouth="open", blush=0.90),
    "kaget":    dict(eyes="wide", mouth="o", blush=0.70),
    "marah":    dict(eyes="oval", mouth="frown", brow=-1.0, blush=0.2),
    "mikir":    dict(eyes="oval", mouth="flat", blush=0.50, look=(0.35, 0.25)),
    "sedih":    dict(eyes="oval", mouth="frown", brow=0.8, blush=0.2),
    "malu":     dict(eyes="arc_up", mouth="smile", blush=1.0),
    "ngantuk":  dict(eyes="half", mouth="flat", blush=0.2),
    "menguap":  dict(eyes="arc_dn", mouth="o", blush=0.2),
    "tidur":    dict(eyes="arc_dn", mouth="smile", blush=0.45),
    "semangat": dict(eyes="wide", mouth="open", blush=0.85),
    "panik":    dict(eyes="wide", mouth="o", brow=0.9, blush=0.4),
    "bangga":   dict(eyes="half", mouth="smile", blush=0.6),
    "jahil":    dict(eyes="wink", mouth="smile", blush=0.65),
    "cemberut": dict(eyes="oval", mouth="frown", blush=0.8),
    "cemas":    dict(eyes="oval", mouth="flat", brow=0.8, blush=0.3),
    "lega":     dict(eyes="arc_dn", mouth="open", blush=0.65),
    "terpana":  dict(eyes="wide", mouth="o", blush=0.8),
    "datar":    dict(eyes="dot", mouth="flat", blush=0.4),
}
EKSPRESI_ALIAS = {
    "senyum": "tenang", "senyum_kecil": "tenang", "ceria": "senang",
    "penasaran": "fokus", "kecewa": "sedih", "bingung": "mikir",
    "ketawa": "tertawa", "heran": "kaget", "kesal": "cemberut", "takut": "panik",
}


def get_expr(name):
    return EKSPRESI.get(EKSPRESI_ALIAS.get(name, name), EKSPRESI["tenang"])


POSE = {
    "diam":          dict(l_arm=(0, 0, -10), r_arm=(0, 0, 10)),
    "santai":        dict(l_arm=(0, 0, -14), r_arm=(-18, 0, 18)),
    "lambai":        dict(l_arm=(0, 0, -12), r_arm=(0, 0, 138), wave_r=1),
    "lambai2":       dict(l_arm=(0, 0, -138), r_arm=(0, 0, 138), wave_r=1),
    "tunjuk":        dict(l_arm=(0, 0, -12), r_arm=(-82, 0, 14)),
    "tunjuk_kiri":   dict(l_arm=(-82, 0, -14), r_arm=(0, 0, 12)),
    "tunjuk_atas":   dict(l_arm=(0, 0, -10), r_arm=(-150, 0, 16)),
    "buka_pintu":    dict(l_arm=(0, 0, -10), r_arm=(-46, 0, 12)),
    "ide":           dict(l_arm=(0, 0, -16), r_arm=(0, 0, 142)),
    "pinggang":      dict(l_arm=(0, 0, -36), r_arm=(0, 0, 36)),
    "jempol":        dict(l_arm=(0, 0, -12), r_arm=(-76, 0, 20)),
    "silang":        dict(l_arm=(-35, 30, -14), r_arm=(-35, -30, 14)),
    "sorak":         dict(l_arm=(0, 0, -152), r_arm=(0, 0, 152)),
    "peregangan":    dict(l_arm=(0, 0, -164), r_arm=(0, 0, 164)),
    "garuk":         dict(l_arm=(0, 0, -10), r_arm=(0, 0, 125)),
    "mikir":         dict(l_arm=(0, 0, -16), r_arm=(-55, -20, 22), head=(0, 0, -6)),
    "kaget":         dict(l_arm=(0, 0, -108), r_arm=(0, 0, 108)),
    "kaget_halus":   dict(l_arm=(0, 0, -18), r_arm=(0, 0, 18)),
    "sedih":         dict(l_arm=(0, 0, -6), r_arm=(0, 0, 6), body=(10, 0, 0)),
    "marah":         dict(l_arm=(-24, 0, -28), r_arm=(-24, 0, 28)),
    "angkat_bahu":   dict(l_arm=(0, 0, -48), r_arm=(0, 0, 48)),
    "jalan":         dict(walk=1),
    "lari":          dict(run=1),
    "duduk":         dict(sit=1, l_arm=(-18, 0, -12), r_arm=(-18, 0, 12)),
    "duduk_sorak":   dict(sit=1, l_arm=(0, 0, -148), r_arm=(0, 0, 148)),
    "tidur":         dict(lie=1, l_arm=(0, 0, -14), r_arm=(0, 0, 14)),
}
POSE_ALIAS = {"angkattangan": "sorak", "tepuk": "sorak", "menari": "lambai2", "pikir": "mikir"}


def state(**kw):
    st = dict(
        pose="diam", pose2=None, mix=0.0, expr="tenang", hadap="depan",
        lihat=(0.0, 0.0), blink=0.0, open_amt=0.0, bawa=None, ransel=False,
        t=0.0, phase=0.0, amp=0.0, pop_up=1.0,
    )
    st.update(kw)
    return st


def _interp_pose(p1, p2, m):
    out = {}
    for k in ("l_arm", "r_arm", "l_leg", "r_leg", "body", "head"):
        a = p1.get(k, (0.0, 0.0, 0.0))
        b = p2.get(k, (0.0, 0.0, 0.0))
        out[k] = tuple(lerp(a[i], b[i], m) for i in range(3))
    for k in ("sit", "lie", "walk", "run", "wave_r"):
        out[k] = lerp(float(p1.get(k, 0.0)), float(p2.get(k, 0.0)), m)
    return out


class TokohKertas:
    def __init__(self, spec="luna"):
        self.p = casting(spec)

    def head_anchor(self, pos, skala=1.0, pose="diam"):
        s = float(skala) * float(self.p.get("skala", 1.0))
        y_top = 1.78
        if POSE.get(pose, {}).get("sit"):
            y_top -= 0.25
        if self.p.get("tipe") == "kucing":
            y_top = 0.95
        return (pos[0], pos[1] + y_top * s, pos[2])

    def _yaw_from_hadap(self, hadap):
        if isinstance(hadap, (int, float)):
            return float(hadap)
        return {
            "depan": 0.0, "belakang": 180.0, "kanan": 90.0, "kiri": -90.0,
            "serong_kanan": 30.0, "serong_kiri": -30.0,
        }.get(hadap, 0.0)

    def draw(self, sc, pos, st, skala=1.0):
        s = float(skala) * float(self.p.get("skala", 1.0))
        t = float(st.get("t", 0.0))
        yaw = self._yaw_from_hadap(st.get("hadap", "depan"))

        if self.p.get("tipe") == "kucing":
            self._draw_kucing(sc, pos, st, s, yaw, t)
            return

        p1_k = POSE_ALIAS.get(st.get("pose", "diam"), st.get("pose", "diam"))
        p2_k = POSE_ALIAS.get(st.get("pose2") or p1_k, st.get("pose2") or p1_k)
        p1 = POSE.get(p1_k, POSE["diam"])
        p2 = POSE.get(p2_k, p1)
        m = clamp(float(st.get("mix", 0.0)))
        P = _interp_pose(p1, p2, m)

        amp = float(st.get("amp", 0.0))
        ph = float(st.get("phase", t * 6.8))
        if P["walk"] > 0.1 or P["run"] > 0.1 or amp > 0.05:
            sp = 1.0 if P["run"] > 0.3 else 0.78
            cyc = math.sin(ph) * max(amp, P["walk"], P["run"])
            swing = 34.0 * sp * (1.25 if P["run"] > 0.3 else 1.0)
            P["l_leg"] = (swing * cyc, 0.0, 0.0)
            P["r_leg"] = (-swing * cyc, 0.0, 0.0)
            P["l_arm"] = (-swing * 0.75 * cyc, 0.0, -10.0)
            P["r_arm"] = (swing * 0.75 * cyc, 0.0, 10.0)
            bob = abs(math.cos(ph)) * 0.035 * s
        else:
            bob = math.sin(t * 2.2) * 0.008 * s

        if P["wave_r"] > 0.1:
            P["r_arm"] = (P["r_arm"][0], P["r_arm"][1], P["r_arm"][2] + math.sin(t * 8.0) * 14.0)

        px, py, pz = pos
        pop_rx = (1.0 - clamp(float(st.get("pop_up", 1.0)))) * 88.0
        root_origin = np.array([px, py, pz], dtype=np.float32)
        root_mat = euler_mat(pop_rx, yaw, 0.0)
        if P["lie"] > 0.5:
            root_mat = euler_mat(-88.0, yaw, 0.0)

        body_mat = root_mat @ euler_mat(*P["body"])
        thk = 0.046 * s
        kulit = warna(self.p.get("kulit"), KULIT)
        baju = warna(self.p.get("kemeja"), KORAL)
        bawah_col = warna(self.p.get("bawah_warna"), BIRU)
        sepatu_col = warna(self.p.get("sepatu"), COKLAT_TUA)

        # ------------------ KAKI KERTAS (berengsel di pinggul)
        hip_y = (0.44 - P["sit"] * 0.22) * s + bob
        leg_sep = 0.095 * s
        l_leg_rot = (-80.0, 0.0, 0.0) if P["sit"] > 0.5 else P["l_leg"]
        r_leg_rot = (-80.0, 0.0, 0.0) if P["sit"] > 0.5 else P["r_leg"]
        leg_strip = rrect_2d(0.0, -0.20 * s, 0.092 * s, 0.40 * s, 0.028 * s)
        shoe_sh = rrect_2d(0.0, -0.40 * s, 0.125 * s, 0.075 * s, 0.030 * s)
        for side, lx, lrot in ((-1, -leg_sep, l_leg_rot), (1, leg_sep, r_leg_rot)):
            h_o = root_origin + root_mat @ np.array([lx, hip_y, side * 0.008 * s], dtype=np.float32)
            lmat = root_mat @ euler_mat(*lrot)
            p_col = kulit if self.p.get("bawah") == "rok" else bawah_col
            sc.extrude_2d(leg_strip, thk * 0.85, p_col, p_col, None, origin=h_o, mat=lmat)
            if self.p.get("sepatu_sneaker"):
                sc.extrude_2d(shoe_sh, thk * 1.15, (30, 32, 40), (30, 32, 40), PUTIH, origin=h_o + lmat @ np.array([0.0, 0.0, 0.022 * s]), mat=lmat)
            else:
                sc.extrude_2d(shoe_sh, thk * 1.10, sepatu_col, sepatu_col, None, origin=h_o + lmat @ np.array([0.0, 0.0, 0.018 * s]), mat=lmat)

        # ------------------ BADAN / MANTEL KERTAS
        torso_o = root_origin + root_mat @ np.array([0.0, hip_y - 0.02 * s, 0.0], dtype=np.float32)
        tc = torso_o + body_mat @ np.array([0.0, 0.28 * s, 0.0], dtype=np.float32)
        tc_front = tc + body_mat @ np.array([0.0, 0.0, +0.055 * s], dtype=np.float32)
        tc_front2 = tc + body_mat @ np.array([0.0, 0.0, +0.075 * s], dtype=np.float32)
        tc_mid = tc + body_mat @ np.array([0.0, 0.0, +0.025 * s], dtype=np.float32)
        tc_back = tc + body_mat @ np.array([0.0, 0.0, -0.055 * s], dtype=np.float32)
        tc_skirt = tc + body_mat @ np.array([0.0, 0.0, -0.015 * s], dtype=np.float32)
        if self.p.get("mantel"):
            coat_pts = coat_2d(0.40 * s, 0.50 * s, 0.57 * s, 0.055 * s)
            coat_edge = mix(baju, KERTAS_TEPI, 0.42)
            sc.extrude_2d(coat_pts, thk * 1.32, baju, baju, coat_edge, origin=torso_o, mat=body_mat, sort_anchor=tc)
            # Garis sabuk pinggang & 2 kancing kuning di depan + belakang (persis gaya mantel Luna referensi!)
            belt_col = gelap(baju, 0.16)
            sc.extrude_2d(rrect_2d(0.0, 0.19 * s, 0.43 * s, 0.036 * s, 0.012 * s), 0.012 * s, belt_col, belt_col, belt_col, origin=torso_o + body_mat @ np.array([0.0, 0.0, thk * 0.68]), mat=body_mat, cast_shadow=False, sort_anchor=tc_mid)
            sc.extrude_2d(rrect_2d(0.0, 0.19 * s, 0.43 * s, 0.036 * s, 0.012 * s), 0.012 * s, belt_col, belt_col, belt_col, origin=torso_o + body_mat @ np.array([0.0, 0.0, -thk * 0.68]), mat=body_mat, cast_shadow=False, sort_anchor=tc_back)
            if self.p.get("kancing_kuning"):
                btn = circle_2d(0.0, 0.0, 0.022 * s, 0.022 * s, n=14)
                for bx in (-0.095 * s, 0.095 * s):
                    sc.extrude_2d(btn, 0.014 * s, KUNING, KUNING, KUNING, origin=torso_o + body_mat @ np.array([bx, 0.19 * s, thk * 0.72]), mat=body_mat, cast_shadow=False, sort_anchor=tc_front, drop_shadow=0.14)
                    sc.extrude_2d(btn, 0.014 * s, KUNING, KUNING, KUNING, origin=torso_o + body_mat @ np.array([bx, 0.19 * s, -thk * 0.72]), mat=body_mat, cast_shadow=False, sort_anchor=tc_back)
        else:
            if self.p.get("bawah") == "rok":
                sc.extrude_2d(coat_2d(0.38 * s, 0.52 * s, 0.26 * s, 0.03 * s), thk * 1.25, bawah_col, bawah_col, None, origin=torso_o + body_mat @ np.array([0.0, -0.06 * s, 0.0]), mat=body_mat, sort_anchor=tc_skirt)
            sc.extrude_2d(rrect_2d(0.0, 0.28 * s, 0.40 * s, 0.54 * s, 0.05 * s), thk * 1.25, baju, baju, None, origin=torso_o, mat=body_mat, sort_anchor=tc)
            if self.p.get("blazer"):
                sc.extrude_2d(rrect_2d(0.0, 0.31 * s, 0.14 * s, 0.42 * s, 0.02 * s), 0.016 * s, PUTIH, PUTIH, None, origin=torso_o + body_mat @ np.array([0.0, 0.0, thk * 0.70]), mat=body_mat, cast_shadow=False, sort_anchor=tc_mid, drop_shadow=0.20)
            if self.p.get("dasi_kupu"):
                for dx, rz in ((-0.055 * s, 14), (0.055 * s, -14)):
                    sc.extrude_2d(rrect_2d(0.0, 0.0, 0.09 * s, 0.065 * s, 0.018 * s), 0.018 * s, HITAM, HITAM, None, origin=torso_o + body_mat @ np.array([dx, 0.51 * s, thk * 0.72]), mat=body_mat @ euler_mat(0, 0, rz), cast_shadow=False, sort_anchor=tc_front, drop_shadow=0.22)
            elif self.p.get("dasi"):
                dc = warna(self.p.get("dasi"), BIRU)
                sc.extrude_2d(rrect_2d(0.0, 0.34 * s, 0.07 * s, 0.28 * s, 0.02 * s), 0.016 * s, dc, dc, None, origin=torso_o + body_mat @ np.array([0.0, 0.0, thk * 0.72]), mat=body_mat, cast_shadow=False, sort_anchor=tc_front, drop_shadow=0.22)

        # ------------------ SYAL KUNING BERUMBAI (rapi melingkar leher tanpa duri vertikal di belakang!)
        if self.p.get("syal"):
            scol = warna(self.p.get("syal"), KUNING)
            s_rib = gelap(scol, 0.16)
            sway = math.sin(t * 4.0) * 6.0 if P["walk"] > 0.1 else 0.0
            collar = rrect_2d(0.0, 0.56 * s, 0.34 * s, 0.115 * s, 0.050 * s)
            sc.extrude_2d(collar, thk * 1.78, scol, scol, mix(scol, KERTAS_TEPI, 0.30), origin=torso_o, mat=body_mat, sort_anchor=tc_front)
            for rx in (-0.08 * s, 0.0, 0.08 * s):
                sc.extrude_2d(rrect_2d(rx, 0.56 * s, 0.012 * s, 0.072 * s, 0.004 * s), 0.008 * s, s_rib, s_rib, s_rib, origin=torso_o + body_mat @ np.array([0.0, 0.0, thk * 0.90]), mat=body_mat, cast_shadow=False, sort_anchor=tc_front2)
            tail_pts = (
                (-0.054 * s, 0.0), (0.054 * s, 0.0), (0.054 * s, -0.23 * s),
                (0.025 * s, -0.19 * s), (0.0, -0.23 * s), (-0.025 * s, -0.19 * s), (-0.054 * s, -0.23 * s),
            )
            sc.extrude_2d(tail_pts, 0.020 * s, scol, scol, mix(scol, KERTAS_TEPI, 0.30), origin=torso_o + body_mat @ np.array([0.10 * s, 0.54 * s, thk * 0.92]), mat=body_mat @ euler_mat(0.0, 0.0, 14.0 + sway), cast_shadow=False, sort_anchor=tc_front2)
            sc.extrude_2d(tail_pts, 0.020 * s, scol, scol, mix(scol, KERTAS_TEPI, 0.30), origin=torso_o + body_mat @ np.array([0.09 * s, 0.54 * s, -thk * 0.92]), mat=body_mat @ euler_mat(0.0, 0.0, 14.0 + sway), cast_shadow=False, sort_anchor=tc_back)

        if st.get("ransel"):
            sc.extrude_2d(rrect_2d(0.0, 0.30 * s, 0.36 * s, 0.38 * s, 0.05 * s), 0.14 * s, (74, 88, 132), (74, 88, 132), None, origin=torso_o + body_mat @ np.array([0.0, 0.0, -0.09 * s]), mat=body_mat, sort_anchor=tc + body_mat @ np.array([0.0, 0.0, -0.10 * s], dtype=np.float32))

        # ------------------ LENGAN & TANGAN KERTAS (menyambung rapat dengan bahu mantel!)
        sh_x = 0.195 * s
        sh_y = 0.49 * s
        arm_strip = rrect_2d(0.0, -0.165 * s, 0.092 * s, 0.33 * s, 0.042 * s)
        hand_c = circle_2d(0.0, -0.34 * s, 0.048 * s, 0.048 * s, n=20)
        arm_edge = mix(baju, KERTAS_TEPI, 0.38)
        for side, sx, arot in ((-1, -sh_x, P["l_arm"]), (1, sh_x, P["r_arm"])):
            sh_o = torso_o + body_mat @ np.array([sx, sh_y, 0.0], dtype=np.float32)
            amat = body_mat @ euler_mat(*arot)
            sc.extrude_2d(arm_strip, thk * 0.88, baju, baju, arm_edge, origin=sh_o, mat=amat)
            sc.extrude_2d(hand_c, thk * 0.78, kulit, kulit, mix(kulit, KERTAS_TEPI, 0.35), origin=sh_o, mat=amat, bias=-0.01, cast_shadow=False)
            bawa = st.get("bawa")
            if bawa:
                bname = bawa["jenis"] if isinstance(bawa, dict) else bawa
                bhand = bawa.get("tangan", "kanan") if isinstance(bawa, dict) else "kanan"
                if (side == 1 and bhand == "kanan") or (side == -1 and bhand == "kiri"):
                    hand_world = sh_o + amat @ np.array([0.0, -0.34 * s, 0.03 * s], dtype=np.float32)
                    BD.draw_prop(sc, bname, tuple(hand_world.tolist()), s=s * 0.85, t=t, rot=(0.0, yaw, 0.0))

        # ------------------ LEHER, KEPALA, RAMBUT / HIJAB, & WAJAH KERTAS
        head_o = torso_o + body_mat @ np.array([0.0, 0.84 * s, 0.0], dtype=np.float32)
        head_mat = body_mat @ euler_mat(*P["head"])
        sc.extrude_2d(rrect_2d(0.0, 0.58 * s, 0.13 * s, 0.10 * s, 0.02 * s), thk * 0.88, kulit, kulit, mix(kulit, KERTAS_TEPI, 0.35), origin=torso_o, mat=body_mat, cast_shadow=False, sort_anchor=torso_o + body_mat @ np.array([0.0, 0.58 * s, -0.01 * s], dtype=np.float32))
        head_pts = circle_2d(0.0, 0.0, 0.275 * s, 0.258 * s, n=32)
        sc.extrude_2d(head_pts, thk * 1.40, kulit, kulit, mix(kulit, KERTAS_TEPI, 0.42), origin=head_o, mat=head_mat, sort_anchor=head_o)

        if self.p.get("hijab"):
            self._draw_hijab(sc, head_o, head_mat, thk, s, torso_o, body_mat)
        else:
            self._draw_hair(sc, head_o, head_mat, thk, s)

        self._draw_face(sc, head_o, head_mat, thk, s, st, kulit)

    def _draw_hair(self, sc, head_o, head_mat, thk, s):
        style = self.p.get("rambut", "rapi")
        hcol = warna(self.p.get("rambut_warna"), COKLAT_RAMBUT)
        anc_back = head_o + head_mat @ np.array([0.0, 0.0, -0.055 * s], dtype=np.float32)
        anc_front = head_o + head_mat @ np.array([0.0, 0.0, +0.025 * s], dtype=np.float32)
        if style == "bob_ahoge":
            h_edge = mix(hcol, KERTAS_TEPI, 0.28)
            bob_back = bob_hair_2d(0.65 * s, 0.62 * s, n_top=28)
            sc.extrude_2d(bob_back, thk * 1.05, hcol, hcol, h_edge, origin=head_o + head_mat @ np.array([0.0, 0.035 * s, -thk * 0.82]), mat=head_mat, sort_anchor=anc_back)
            # Poni belah samping melengkung organik membingkai wajah bulat chubby (seperti REF!)
            bang_pts = []
            # Garis bawah poni melengkung lembut asimetris dari pipi kiri naik melewati dahi ke pipi kanan
            for k in range(13):
                u = -1.0 + 2.0 * (k / 12.0)
                bx = 0.295 * s * u
                # Melengkung naik di dahi kanan-tengah, turun membingkai pelipis kiri & kanan
                arch_h = 0.125 - 0.17 * (u * u) + 0.045 * math.sin((u + 0.25) * 1.8)
                bang_pts.append((round(bx, 5), round(arch_h * s, 5)))
            # Busur luar atas mengikuti kubah kepala bulat
            for k in range(15):
                a = math.pi * (k / 14.0)
                bang_pts.append((round(0.305 * s * math.cos(a), 5), round((0.08 + 0.225 * math.sin(a)) * s, 5)))
            sc.extrude_2d(bang_pts, thk * 0.56, hcol, hcol, h_edge, origin=head_o + head_mat @ np.array([0.0, 0.0, thk * 0.68]), mat=head_mat, cast_shadow=False, sort_anchor=anc_front, drop_shadow=0.14)
            # Jambul spiral halus khas Luna di puncak kepala
            sc.extrude_2d(spiral_ahoge_2d(s), thk * 0.68, hcol, hcol, h_edge, origin=head_o + head_mat @ np.array([0.0, 0.275 * s, 0.0]), mat=head_mat, cast_shadow=False, sort_anchor=anc_front, drop_shadow=0.12)
        elif style == "afro":
            afro_pts = cloud_afro_2d(0.40 * s, 0.34 * s, lobes=9, n=48)
            sc.extrude_2d(afro_pts, thk * 1.30, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.0, 0.11 * s, -thk * 0.90]), mat=head_mat, sort_anchor=anc_back)
            top_cap = cloud_afro_2d(0.30 * s, 0.12 * s, lobes=7, n=32)
            sc.extrude_2d(top_cap, thk * 0.70, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.0, 0.27 * s, thk * 0.68]), mat=head_mat, cast_shadow=False, sort_anchor=anc_front, drop_shadow=0.20)
        elif style in ("jambul", "rapi", "uban"):
            top = bob_hair_2d(0.58 * s, 0.38 * s, n_top=22)
            sc.extrude_2d(top, thk * 1.15, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.0, 0.13 * s, -thk * 0.72]), mat=head_mat, sort_anchor=anc_back)
            if style == "jambul":
                sc.extrude_2d(circle_2d(0.0, 0.0, 0.12 * s, 0.08 * s, 18), thk * 0.8, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.04 * s, 0.30 * s, 0.0]), mat=head_mat, cast_shadow=False, sort_anchor=anc_front, drop_shadow=0.18)
        elif style == "keriting":
            sc.extrude_2d(cloud_afro_2d(0.34 * s, 0.28 * s, lobes=7, n=36), thk * 1.15, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.0, 0.11 * s, -thk * 0.82]), mat=head_mat, sort_anchor=anc_back)
        elif style == "kuncir":
            sc.extrude_2d(bob_hair_2d(0.58 * s, 0.42 * s, 22), thk * 1.1, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.0, 0.12 * s, -thk * 0.78]), mat=head_mat, sort_anchor=anc_back)
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.13 * s, 0.30 * s, 0.05 * s), thk * 0.9, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.0, 0.06 * s, -thk * 1.45]), mat=head_mat, sort_anchor=head_o + head_mat @ np.array([0.0, 0.0, -0.080 * s], dtype=np.float32))
        elif style == "bob":
            sc.extrude_2d(bob_hair_2d(0.62 * s, 0.58 * s, 24), thk * 1.1, hcol, hcol, None, origin=head_o + head_mat @ np.array([0.0, 0.02 * s, -thk * 0.82]), mat=head_mat, sort_anchor=anc_back)

    def _draw_hijab(self, sc, head_o, head_mat, thk, s, torso_o, body_mat):
        hc = warna(self.p.get("hijab"), (36, 38, 48))
        ht = warna(self.p.get("hijab_tua"), gelap(hc, 0.18))
        anc_back = head_o + head_mat @ np.array([0.0, 0.0, -0.055 * s], dtype=np.float32)
        tc_front = torso_o + body_mat @ np.array([0.0, 0.28 * s, +0.055 * s], dtype=np.float32)
        sc.extrude_2d(bob_hair_2d(0.66 * s, 0.68 * s, 28), thk * 1.35, hc, hc, None, origin=head_o + head_mat @ np.array([0.0, 0.0, -thk * 0.75]), mat=head_mat, sort_anchor=anc_back)
        sc.extrude_2d(rrect_2d(0.0, 0.51 * s, 0.46 * s, 0.16 * s, 0.06 * s), thk * 1.45, ht, ht, None, origin=torso_o, mat=body_mat, cast_shadow=False, sort_anchor=tc_front, drop_shadow=0.22)

    def _draw_face(self, sc, head_o, head_mat, thk, s, st, kulit):
        ex = get_expr(st.get("expr", "tenang"))
        zf = thk * 0.76
        anc_face = head_o + head_mat @ np.array([0.0, 0.0, +0.055 * s], dtype=np.float32)
        anc_hi = head_o + head_mat @ np.array([0.0, 0.0, +0.068 * s], dtype=np.float32)
        anc_g = head_o + head_mat @ np.array([0.0, 0.0, +0.085 * s], dtype=np.float32)
        eye_y = 0.015 * s
        eye_x = 0.105 * s
        blink = float(st.get("blink", 0.0))
        eyes = "arc_dn" if blink > 0.45 else ex["eyes"]
        lx, ly = st.get("lihat", (0.0, 0.0))
        if lx == 0.0 and ly == 0.0 and "look" in ex:
            lx, ly = ex["look"]

        # Pipi kertas bulat merona lembut
        bl = ex.get("blush", 0.55)
        if bl > 0.1:
            bc = mix(kulit, PIPI, clamp(bl * 0.78, 0.30, 0.82))
            chk = circle_2d(0.0, 0.0, 0.044 * s, 0.034 * s, n=18)
            sc.extrude_2d(chk, 0.006 * s, bc, bc, bc, origin=head_o + head_mat @ np.array([-0.152 * s, -0.068 * s, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)
            sc.extrude_2d(chk, 0.006 * s, bc, bc, bc, origin=head_o + head_mat @ np.array([0.152 * s, -0.068 * s, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)

        # Mata kertas (untuk Luna / mata_polos: mata titik lembut tanpa sclera putih melotot!)
        mata_polos = bool(self.p.get("mata_polos", False))
        for side in (-1, 1):
            cx = side * eye_x
            if eyes in ("arc_up", "arc_dn"):
                dy_a = 0.008 * s if eyes == "arc_up" else -0.008 * s
                arc_bar = rrect_2d(0.0, 0.0, 0.056 * s, 0.015 * s, 0.006 * s)
                sc.extrude_2d(arc_bar, 0.008 * s, OUT, OUT, OUT, origin=head_o + head_mat @ np.array([cx, eye_y + dy_a, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)
            elif eyes == "wink" and side == 1:
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.056 * s, 0.015 * s, 0.006 * s), 0.008 * s, OUT, OUT, OUT, origin=head_o + head_mat @ np.array([cx, eye_y, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)
            else:
                if mata_polos:
                    erx = 0.025 * s if eyes == "wide" else 0.021 * s
                    ery = 0.029 * s if eyes == "wide" else 0.024 * s
                else:
                    erx = 0.032 * s if eyes == "wide" else (0.022 * s if eyes == "dot" else 0.027 * s)
                    ery = 0.038 * s if eyes == "wide" else (0.022 * s if eyes == "dot" else 0.034 * s)
                ox, oy = clamp(lx, -1, 1) * 0.010 * s, clamp(ly, -1, 1) * 0.008 * s
                sc.extrude_2d(circle_2d(0.0, 0.0, erx, ery, n=18), 0.008 * s, OUT, OUT, OUT, origin=head_o + head_mat @ np.array([cx + ox, eye_y + oy, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)
                if (not mata_polos) and eyes != "dot":
                    sc.extrude_2d(circle_2d(0.0, 0.0, erx * 0.28, ery * 0.24, n=12), 0.008 * s, PUTIH, PUTIH, PUTIH, origin=head_o + head_mat @ np.array([cx + ox - 0.007 * s, eye_y + oy + 0.010 * s, zf + 0.004 * s]), mat=head_mat, cast_shadow=False, sort_anchor=anc_hi)

        # Mulut kertas mungil & manis (proporsional gaya miniatur stop-motion)
        my = -0.106 * s
        open_amt = float(st.get("open_amt", 0.0))
        mouth = ex.get("mouth", "smile")
        if open_amt > 0.15:
            mh = (0.016 + 0.032 * open_amt) * s
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.028 * s, mh * 0.60, 16), 0.007 * s, (112, 48, 44), (112, 48, 44), (112, 48, 44), origin=head_o + head_mat @ np.array([0.0, my, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)
        elif mouth == "o":
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.024 * s, 0.029 * s, 18), 0.007 * s, (68, 36, 34), (68, 36, 34), (68, 36, 34), origin=head_o + head_mat @ np.array([0.0, my, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)
        elif mouth == "open":
            sc.extrude_2d(circle_2d(0.0, 0.0, 0.026 * s, 0.018 * s, 16), 0.007 * s, (148, 62, 56), (148, 62, 56), (148, 62, 56), origin=head_o + head_mat @ np.array([0.0, my, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)
        elif mouth == "smile":
            for sx, rz in ((-0.012 * s, -15), (0.012 * s, 15)):
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.028 * s, 0.010 * s, 0.004 * s), 0.007 * s, OUT, OUT, OUT, origin=head_o + head_mat @ np.array([sx, my + 0.003 * s, zf]), mat=head_mat @ euler_mat(0, 0, rz), cast_shadow=False, sort_anchor=anc_face)
        else:
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.040 * s, 0.011 * s, 0.004 * s), 0.007 * s, OUT, OUT, OUT, origin=head_o + head_mat @ np.array([0.0, my, zf]), mat=head_mat, cast_shadow=False, sort_anchor=anc_face)

        # Kacamata kertas (Kribo kotak & Nadia bulat mulus)
        kac = self.p.get("kacamata")
        if kac:
            gz = zf + 0.016 * s
            fc = (34, 30, 30)
            for side in (-1, 1):
                gx = side * eye_x
                if kac == "bulat":
                    rad = 0.062 * s
                    for flip in (0.0, 180.0):
                        sc.extrude_ring_arch(rad - 0.011 * s, rad + 0.006 * s, 0.0, 0.014 * s, fc, edge_col=fc, n_arc=16, origin=head_o + head_mat @ np.array([gx, eye_y, gz]), mat=head_mat @ euler_mat(0, 0, flip), cast_shadow=False, sort_anchor=anc_g)
                else:
                    bw, bh, th = 0.132 * s, 0.104 * s, 0.016 * s
                    for bx, by, w0, h0 in ((0, bh * 0.5, bw + th * 0.5, th), (0, -bh * 0.5, bw + th * 0.5, th), (-bw * 0.5, 0, th, bh), (bw * 0.5, 0, th, bh)):
                        sc.extrude_2d(rrect_2d(0.0, 0.0, w0, h0, 0.005 * s), 0.015 * s, fc, fc, fc, origin=head_o + head_mat @ np.array([gx + bx, eye_y + by, gz]), mat=head_mat, cast_shadow=False, sort_anchor=anc_g, drop_shadow=0.14)
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.075 * s, 0.014 * s, 0.005 * s), 0.015 * s, fc, fc, fc, origin=head_o + head_mat @ np.array([0.0, eye_y + 0.01 * s, gz]), mat=head_mat, cast_shadow=False, sort_anchor=anc_g, drop_shadow=0.14)

    # ------------------------------------------------------------------ KUCING POP-UP KERTAS
    def _draw_kucing(self, sc, pos, st, s, yaw, t):
        pop_v = clamp(float(st.get("pop_up", 1.0)))
        if pop_v <= 0.02:
            return
        px, py, pz = pos
        col = warna(self.p.get("warna"), KUNING)
        dcol = warna(self.p.get("dasi"), MERAH)
        pop_rx = (1.0 - pop_v) * 88.0
        root = np.array([px, py, pz], dtype=np.float32)
        rmat = euler_mat(pop_rx, yaw, 0.0)
        thk = 0.052 * s
        kc = root + rmat @ np.array([0.0, 0.38 * s, 0.0], dtype=np.float32)
        kc_belly = kc + rmat @ np.array([0.0, 0.0, +0.028 * s], dtype=np.float32)
        kc_front = kc + rmat @ np.array([0.0, 0.0, +0.055 * s], dtype=np.float32)
        kc_front2 = kc + rmat @ np.array([0.0, 0.0, +0.072 * s], dtype=np.float32)
        kc_paw = kc + rmat @ np.array([0.0, 0.0, +0.090 * s], dtype=np.float32)

        sc.extrude_2d(cat_silhouette_2d(s), thk, col, col, None, origin=root, mat=rmat, sort_anchor=kc)
        # Perut krem oval + 3 motif kapsul pastel
        sc.extrude_2d(circle_2d(0.0, 0.22 * s, 0.16 * s, 0.18 * s, 26), 0.018 * s, KRIM, KRIM, None, origin=root + rmat @ np.array([0.0, 0.0, thk * 0.65]), mat=rmat, cast_shadow=False, sort_anchor=kc_belly, drop_shadow=0.22)
        for mx, mc in ((-0.068 * s, MINT), (0.0, KUNING), (0.068 * s, KORAL)):
            sc.extrude_2d(rrect_2d(mx, 0.21 * s, 0.036 * s, 0.098 * s, 0.015 * s), 0.012 * s, mc, mc, None, origin=root + rmat @ np.array([0.0, 0.0, thk * 0.80]), mat=rmat, cast_shadow=False, sort_anchor=kc_front, drop_shadow=0.14)
        # 3 belang coklat di dahi
        stripe_c = gelap(col, 0.34)
        for sx in (-0.055 * s, 0.0, 0.055 * s):
            sc.extrude_2d(rrect_2d(sx, 0.71 * s, 0.022 * s, 0.075 * s, 0.009 * s), 0.012 * s, stripe_c, stripe_c, None, origin=root + rmat @ np.array([0.0, 0.0, thk * 0.68]), mat=rmat, cast_shadow=False, sort_anchor=kc_front, drop_shadow=0.16)
        # Dasi kupu-kupu merah & hidung pink
        for dx, rz in ((-0.075 * s, 16), (0.075 * s, -16)):
            sc.extrude_2d(rrect_2d(0.0, 0.0, 0.12 * s, 0.075 * s, 0.022 * s), 0.020 * s, dcol, dcol, None, origin=root + rmat @ np.array([dx, 0.44 * s, thk * 0.72]), mat=rmat @ euler_mat(0, 0, rz), cast_shadow=False, sort_anchor=kc_front, drop_shadow=0.22)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.038 * s, 0.038 * s, 16), 0.024 * s, dcol, dcol, None, origin=root + rmat @ np.array([0.0, 0.44 * s, thk * 0.78]), mat=rmat, cast_shadow=False, sort_anchor=kc_front2, drop_shadow=0.22)
        sc.extrude_2d(circle_2d(0.0, 0.0, 0.024 * s, 0.018 * s, 14), 0.014 * s, PINK, PINK, None, origin=root + rmat @ np.array([0.0, 0.57 * s, thk * 0.70]), mat=rmat, cast_shadow=False, sort_anchor=kc_front, drop_shadow=0.18)
        # Mata melengkung ^ ^ + 3 kumis per pipi
        for side in (-1, 1):
            for half, hrz in ((-0.018 * s, 26), (0.018 * s, -26)):
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.044 * s, 0.015 * s, 0.005 * s), 0.014 * s, OUT, OUT, OUT, origin=root + rmat @ np.array([side * 0.10 * s + half, 0.635 * s, thk * 0.68]), mat=rmat @ euler_mat(0, 0, hrz), cast_shadow=False, sort_anchor=kc_front, drop_shadow=0.18)
            for wk, wdy in ((-8, -0.025 * s), (0, 0.0), (8, 0.025 * s)):
                sc.extrude_2d(rrect_2d(0.0, 0.0, 0.088 * s, 0.010 * s, 0.004 * s), 0.012 * s, OUT, OUT, OUT, origin=root + rmat @ np.array([side * 0.215 * s, 0.56 * s + wdy, thk * 0.68]), mat=rmat @ euler_mat(0, 0, side * wk), cast_shadow=False, sort_anchor=kc_front, drop_shadow=0.16)
        # Tangan kiri diam membulat & tangan kanan melambai
        sc.extrude_2d(rrect_2d(0.0, 0.0, 0.086 * s, 0.17 * s, 0.038 * s), thk * 0.72, col, col, None, origin=root + rmat @ np.array([-0.16 * s, 0.22 * s, thk * 0.75]), mat=rmat @ euler_mat(0, 0, -14), cast_shadow=False, sort_anchor=kc_paw, drop_shadow=0.22)
        paw_ang = math.sin(t * 7.5) * 18.0 + 18.0
        p_o = root + rmat @ np.array([0.24 * s, 0.36 * s, thk * 0.5], dtype=np.float32)
        sc.extrude_2d(rrect_2d(0.0, 0.13 * s, 0.095 * s, 0.26 * s, 0.042 * s), thk * 0.85, col, col, None, origin=p_o, mat=rmat @ euler_mat(0, 0, -24 + paw_ang), cast_shadow=True, sort_anchor=kc_paw, drop_shadow=0.22)
