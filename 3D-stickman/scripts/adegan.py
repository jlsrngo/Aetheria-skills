# -*- coding: utf-8 -*-
"""
adegan.py - Sutradara adegan 3D-stickman: aktor, kamera 3D, properti, balon ucapan, teks, efek, dan pemicu SFX.
"""
import math, re
import numpy as np
from PIL import Image, ImageDraw
from engine3d import (
    OUT, PUTIH, KRIM, HITAM, MERAH, BIRU, KUNING, ORANYE, HIJAU, TEAL,
    clamp, prog, lerp, lerp3, e_io, e_out, e_in, e_back, e_snap, EASE,
    catmull_rom, font, Cam3D, Scene3D,
)
import tokoh as TK
import benda as BD
import dunia as DN

UKURAN = {
    "panorama":      (10.5, 2.20, 52.0),
    "sangat_lebar":  (7.6,  1.35, 48.0),
    "lebar":         (4.8,  0.55, 44.0),
    "penuh":         (3.5,  0.36, 42.0),
    "sedang":        (2.6,  0.34, 38.0),
    "dekat":         (1.65, 0.24, 35.0),
    "sangat_dekat":  (1.15, 0.16, 32.0),
    "ekstrem_dekat": (0.78, 0.14, 28.0),
}

# Offset vertikal (dy) & roll otomatis untuk preset sudut sinematik
ANGLE_PRESET = {
    "normal": (0.0,   0.0),
    "bawah":  (-0.55, 0.0),   # low angle (hero shot)
    "atas":   (+1.15, 0.0),   # high angle
    "burung": (+3.40, 0.0),   # bird's eye
    "dutch":  (0.0,   10.0),  # horizon miring tegang
}

# Intensitas gerak nafas/handheld: (amp_x, amp_y, freq)
GAYA_DRIFT = {
    "tripod":   (0.0,   0.0,   0.0),
    "halus":    (0.015, 0.010, 0.85),
    "handheld": (0.042, 0.032, 1.85),
    "tegang":   (0.028, 0.024, 6.50),
}


def norm(s):
    return re.sub(r"[^\w\s]", "", (s or "").lower().replace("-", " ")).split()


class Aktor:
    def __init__(self, sc, spec, cast):
        self.sc = sc
        self.id = spec.get("id") or spec.get("dasar") or "kribo"
        dasar = spec.get("dasar", self.id)
        base = cast.get(self.id, cast.get(dasar, dasar))
        if isinstance(base, str):
            base = {"dasar": base}
        base = dict(base)
        for k in ("kacamata", "hijab", "rambut", "kemeja", "dasi", "dasi_kupu",
                  "bawah", "bawah_warna", "jas", "blazer", "peci",
                  "outline", "telinga", "mata_sclera"):
            if k in spec:
                base[k] = spec[k]
        self.tk = TK.TokohStick3D(base)
        self.s = float(spec.get("skala", 1.0))
        if "pos" in spec:
            self.x0, self.y0, self.z0 = [float(v) for v in spec["pos"]]
        else:
            self.x0 = float(spec.get("x", 0.0))
            self.y0 = float(spec.get("y", 0.0))
            self.z0 = float(spec.get("z", 0.0))
        self.seed = (hash(self.id) % 97) / 10.0

        base_state = {k: spec[k] for k in ("pose", "ekspresi", "hadap", "bawa", "bicara", "lihat") if k in spec}
        base_state.setdefault("pose", "diam")
        base_state.setdefault("ekspresi", "senang")
        base_state.setdefault("hadap", "depan")
        base_state["t"] = 0.0
        self.keys = [base_state]
        self.moves = []
        self.icons = []
        self.t_in = None
        self.t_out = None

        acts = [(sc.when(a), a) for a in spec.get("aksi", [])]
        mk = spec.get("masuk")
        if mk:
            t0 = sc.when(mk)
            dur = float(mk.get("dur", 0.9))
            dr = mk.get("dari", "kiri")
            gaya = mk.get("gaya", "jalan")
            self.t_in = t0
            if dr in ("kiri", "kanan", "belakang", "depan"):
                jarak = float(mk.get("jarak", 3.6))
                dx = -jarak if dr == "kiri" else jarak if dr == "kanan" else 0.0
                dz = -jarak if dr == "belakang" else jarak if dr == "depan" else 0.0
                self.moves.append(dict(t0=t0, t1=t0 + dur, p0=(self.x0 + dx, self.y0, self.z0 + dz), p1=(self.x0, self.y0, self.z0), gaya=gaya))
                h_in = "kanan" if dr == "kiri" else "kiri" if dr == "kanan" else "depan" if dr == "belakang" else "belakang"
                self.keys.append(dict(t=t0, hadap=h_in))
                self.keys.append(dict(t=t0 + dur, hadap=mk.get("hadap_akhir", base_state["hadap"])))
        xk = spec.get("keluar")
        if xk:
            t0 = sc.when(xk)
            dur = float(xk.get("dur", 1.0))
            dr = xk.get("ke", "kanan")
            self.t_out = t0 + dur
            jarak = float(xk.get("jarak", 3.6))
            dx = jarak if dr == "kanan" else -jarak if dr == "kiri" else 0.0
            dz = jarak if dr == "depan" else -jarak if dr == "belakang" else 0.0
            acts.append((t0, dict(ke_pos=(self.x0 + dx, self.y0, self.z0 + dz), durasi=dur, gaya=xk.get("gaya", "jalan"))))

        acts.sort(key=lambda z: z[0])
        cur = (self.x0, self.y0, self.z0)
        for t, a in acts:
            st = {k: a[k] for k in ("pose", "ekspresi", "hadap", "bawa", "bicara", "lihat", "skala") if k in a}
            if st:
                st["t"] = t
                self.keys.append(st)
            if any(k in a for k in ("ke_x", "ke_y", "ke_z", "ke_pos")):
                p0 = self.moves[-1]["p1"] if self.moves else cur
                if "ke_pos" in a:
                    tx, ty, tz = [float(v) for v in a["ke_pos"]]
                else:
                    tx = float(a.get("ke_x", p0[0]))
                    ty = float(a.get("ke_y", p0[1]))
                    tz = float(a.get("ke_z", p0[2]))
                dist = math.dist(p0, (tx, ty, tz))
                dur = float(a.get("durasi", max(0.5, dist / 1.4)))
                gaya = a.get("gaya", "jalan" if dist > 0.2 else "geser")
                self.moves.append(dict(t0=t, t1=t + dur, p0=p0, p1=(tx, ty, tz), gaya=gaya))
                if dist > 0.2 and "hadap" not in a and gaya in ("jalan", "lari", "lompat"):
                    dx, dz = tx - p0[0], tz - p0[2]
                    self.keys.append(dict(t=t, hadap=math.degrees(math.atan2(dx, dz))))
                    if a.get("hadap_akhir"):
                        self.keys.append(dict(t=t + dur, hadap=a["hadap_akhir"]))
                cur = (tx, ty, tz)
            if "efek" in a:
                self.icons.append((t, t + float(a.get("efek_dur", 1.8)), a["efek"]))

        self.keys.sort(key=lambda d: d["t"])

    def pos_at(self, t):
        p = (self.x0, self.y0, self.z0)
        moving = False
        gaya = "diam"
        for m in self.moves:
            if t < m["t0"]:
                break
            if t <= m["t1"]:
                q = prog(t, m["t0"], m["t1"])
                e = e_io(q) if m["gaya"] in ("geser", "lompat") else q
                p = lerp3(m["p0"], m["p1"], e)
                if m["gaya"] == "lompat":
                    p = (p[0], p[1] + math.sin(math.pi * q) * 0.42, p[2])
                moving = m["gaya"] in ("jalan", "lari")
                gaya = m["gaya"]
                break
            p = m["p1"]
        return p, moving, gaya

    def state_at(self, t, level):
        cur = dict(self.keys[0])
        prev_pose = cur.get("pose", "diam")
        pose_t = 0.0
        for k in self.keys[1:]:
            if k["t"] <= t:
                if "pose" in k and k["pose"] != cur.get("pose"):
                    prev_pose = cur.get("pose", "diam")
                    pose_t = k["t"]
                cur.update(k)
        pos, moving, gaya = self.pos_at(t)
        pose = cur.get("pose", "diam")
        mix = prog(t, pose_t, pose_t + 0.26) if pose_t > 0 else 1.0
        if moving:
            pose, prev_pose, mix = gaya, gaya, 1.0
        blink = 1.0 if ((t + self.seed) % 3.1) < 0.12 else 0.0
        bicara = cur.get("bicara", False)
        if isinstance(bicara, list):
            bicara = any(a <= t <= b for a, b in bicara)
        open_amt = level if bicara else 0.0
        st = TK.state(
            pose=prev_pose if mix < 1.0 else pose,
            pose2=pose if mix < 1.0 else None,
            mix=e_io(mix) if mix < 1.0 else 0.0,
            expr=cur.get("ekspresi", "senang"),
            hadap=cur.get("hadap", "depan"),
            lihat=tuple(cur.get("lihat", (0.0, 0.0))),
            blink=blink,
            open_amt=open_amt,
            bawa=cur.get("bawa"),
            t=t,
            amp=1.0 if moving else 0.0,
            phase=t * (9.5 if gaya == "lari" else 6.8),
        )
        return pos, st, float(cur.get("skala", self.s))

    def draw(self, sc, t, level):
        if self.t_in is not None and t < self.t_in:
            return
        if self.t_out is not None and t > self.t_out:
            return
        pos, st, s = self.state_at(t, level)
        self.tk.draw(sc, pos, st, skala=s)
        head_p = self.tk.head_anchor(pos, s, st["pose"])
        for t0, t1, kind in self.icons:
            if t0 <= t <= t1:
                BD.draw_icon_3d(sc, kind, (head_p[0], head_p[1] + 0.26, head_p[2]), t=t - t0, s=s * 0.95)


class Adegan:
    def __init__(self, spec, W, H, start, end, fps, film, idx):
        self.s = spec
        self.W, self.H = W, H
        self.start, self.end = start, end
        self.dur = max(0.2, end - start)
        self.fps, self.film, self.idx = fps, film, idx
        self.warn = []
        self.nar_words = self._prep_words()
        self.actors = [Aktor(self, a, film.cast) for a in spec.get("tokoh", [])]
        self.actor_map = {a.id: a for a in self.actors}
        self.opsi = dict(spec.get("opsi", {}))
        for k in ("waktu", "tahun", "bulan", "sub_kalender", "banner", "judul", "baris1", "baris2", "harga",
                  "kiri_lbl", "kiri_val", "kanan_lbl", "kanan_val", "judul_poster", "bus", "bus_x"):
            if k in spec:
                self.opsi[k] = spec[k]
        self.opsi.setdefault("waktu", "siang")
        self.cam_moves = self._prep_cam()
        self.props = [(self.when(b), self.when(b, "sampai", 999), b) for b in spec.get("benda", [])]
        self.balloons = [(self.when(b), self.when(b, "sampai", 999), b) for b in spec.get("balon", [])]
        self.texts = [(self.when(tx), self.when(tx, "sampai", 999), tx) for tx in spec.get("teks", [])]
        self.fxs = [(self.when(fx), self.when(fx, "sampai", 999), fx) for fx in spec.get("efek", [])]

    def _prep_words(self):
        ws = self.film.words_rel(self.idx)
        return [(norm(w)[0] if norm(w) else w.lower(), s - self.start, e - self.start) for w, s, e in ws]

    def when(self, obj, key="t", default=0.0):
        if isinstance(obj, (int, float)):
            return float(obj)
        k_field = "kata" if key == "t" else "sampai_kata"
        if k_field in obj:
            q = norm(obj[k_field])
            occ = int(obj.get("urutan", 0))
            hits = []
            ws = [w[0] for w in self.nar_words]
            for i in range(len(ws) - len(q) + 1):
                if q and ws[i:i + len(q)] == q:
                    hits.append(self.nar_words[i][1])
            if hits:
                return max(0.0, hits[min(occ, len(hits) - 1)] + float(obj.get("geser", 0.0)))
            self.warn.append(f"adegan {self.idx + 1}: frasa '{obj[k_field]}' tidak ada di narasi")
            return 0.0
        return float(obj[key]) if key in obj else float(default)

    def _resolve_target(self, cam_spec, t):
        if "target" in cam_spec:
            return tuple(float(v) for v in cam_spec["target"])
        fok = cam_spec.get("fokus")
        if isinstance(fok, list) and fok:
            pts = [self.actor_map[fid].pos_at(t)[0] for fid in fok if fid in self.actor_map]
            if pts:
                return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts) + 1.05, sum(p[2] for p in pts) / len(pts))
        if isinstance(fok, str) and fok in self.actor_map:
            p = self.actor_map[fok].pos_at(t)[0]
            return (p[0], p[1] + 1.05, p[2])
        if self.actors:
            p = self.actors[0].pos_at(t)[0]
            return (p[0], p[1] + 1.05, p[2])
        return (0.0, 1.05, 0.0)

    def _cam_pose_from_spec(self, spec, prev=None, t=0.0):
        portrait = self.W < self.H
        if prev is None:
            pos = np.array([0.0, 1.42, 4.2], dtype=np.float32)
            tgt = np.array([0.0, 1.05, 0.0], dtype=np.float32)
            fov, roll, blur = 44.0, 0.0, 0.0
        else:
            pos, tgt = np.array(prev[0], dtype=np.float32), np.array(prev[1], dtype=np.float32)
            fov, roll, blur = prev[2], prev[3], prev[4]

        uk = spec.get("ukuran")
        if uk in UKURAN:
            dist, dy, fv = UKURAN[uk]
            if portrait:
                fok = spec.get("fokus")
                multi = 1.18 if isinstance(fok, list) and len(fok) >= 2 else 1.0
                dist *= 1.48 * multi
                fv = max(34.0, fv - 1.0)
            tgt = np.array(self._resolve_target(spec, t), dtype=np.float32)
            if uk in ("ekstrem_dekat", "sangat_dekat", "dekat") and "target" not in spec:
                tgt[1] += {"dekat": 0.16, "sangat_dekat": 0.28, "ekstrem_dekat": 0.33}[uk]
            yaw = math.radians(float(spec.get("sudut", 10.0)))
            pos = tgt + np.array([math.sin(yaw) * dist, dy, math.cos(yaw) * dist], dtype=np.float32)
            fov = fv
        if ("target" in spec or "fokus" in spec) and uk not in ("ekstrem_dekat", "sangat_dekat", "dekat"):
            tgt = np.array(self._resolve_target(spec, t), dtype=np.float32)

        # Preset angle vertikal (bawah / atas / burung / dutch) & offset vertikal manual
        ang_name = spec.get("angle")
        if ang_name in ANGLE_PRESET:
            ady, aroll = ANGLE_PRESET[ang_name]
            pos = pos + np.array([0.0, ady, 0.0], dtype=np.float32)
            if "roll" not in spec and "miring" not in spec:
                roll = aroll
        if "sudut_v" in spec:
            pos = pos + np.array([0.0, float(spec["sudut_v"]), 0.0], dtype=np.float32)

        # Komposisi over-the-shoulder: {"bahu": "tokoh_a", "fokus": "tokoh_b"}
        bahu_id = spec.get("bahu")
        if bahu_id and bahu_id in self.actor_map:
            p_bahu = np.array(self.actor_map[bahu_id].pos_at(t)[0], dtype=np.float32)
            p_tgt = np.array(self._resolve_target(spec, t), dtype=np.float32)
            d_vec = np.array([p_bahu[0] - p_tgt[0], 0.0, p_bahu[2] - p_tgt[2]], dtype=np.float32)
            d_len = float(np.linalg.norm(d_vec))
            d_dir = d_vec / d_len if d_len > 1e-4 else np.array([0.0, 0.0, 1.0], dtype=np.float32)
            side = np.array([-d_dir[2], 0.0, d_dir[0]], dtype=np.float32) * float(spec.get("sisi_bahu", 1.38))
            pos = p_bahu + d_dir * 1.45 + side + np.array([0.0, 1.34, 0.0], dtype=np.float32)
            tgt = p_tgt + np.array([0.0, 0.12, 0.0], dtype=np.float32)
            fov = float(spec.get("fov", 38.0))

        if "pos" in spec:
            pos = np.array(spec["pos"], dtype=np.float32)
        if "fov" in spec:
            fov = float(spec["fov"])
        if "roll" in spec or "miring" in spec:
            roll = float(spec.get("roll", spec.get("miring", 0.0)))
        if "blur" in spec:
            blur = float(spec["blur"])
        return pos, tgt, fov, roll, blur

    def _eval_cam_move(self, g, start_pose, t, p, t1):
        """Evaluasi pose kamera (pos, tgt, fov, roll, blur) untuk 1 gerak pada progres p in [0, 1]."""
        jn = g.get("jenis", "push")
        e = EASE.get(g.get("ease", "io"), e_io)(p)
        p0, tgt0, f0, r0, b0 = start_pose

        if jn == "orbit":
            d_vec = p0 - tgt0
            rad = math.hypot(float(d_vec[0]), float(d_vec[2]))
            a0 = math.atan2(float(d_vec[0]), float(d_vec[2]))
            da = math.radians(float(g.get("derajat", 45.0))) * e
            dh = float(g.get("naik", 0.0)) * e
            tgt = np.array(self._resolve_target(g, t), dtype=np.float32) if ("fokus" in g or "target" in g) else tgt0
            pos = tgt + np.array([math.sin(a0 + da) * rad, float(d_vec[1]) + dh, math.cos(a0 + da) * rad], dtype=np.float32)
            return pos, tgt, f0, r0, b0

        if jn == "spiral":
            d_vec = p0 - tgt0
            rad = math.hypot(float(d_vec[0]), float(d_vec[2])) * lerp(1.0, float(g.get("faktor", 0.72)), e)
            a0 = math.atan2(float(d_vec[0]), float(d_vec[2]))
            da = math.radians(float(g.get("derajat", 60.0))) * e
            dh = float(g.get("naik", 0.65)) * e
            tgt = np.array(self._resolve_target(g, t), dtype=np.float32) if ("fokus" in g or "target" in g) else tgt0
            pos = tgt + np.array([math.sin(a0 + da) * rad, float(d_vec[1]) + dh, math.cos(a0 + da) * rad], dtype=np.float32)
            fov = clamp(lerp(f0, f0 - float(g.get("zoom", 4.0)), e), 18.0, 85.0)
            return pos, tgt, fov, r0, b0

        if jn == "crane":
            end_pose = self._cam_pose_from_spec(g.get("ke", g), start_pose, t1)
            p1, tgt1, f1, r1, b1 = end_pose
            if "naik" in g and "pos" not in g.get("ke", {}):
                p1 = p0 + np.array([0.0, float(g["naik"]), float(g.get("maju", 0.0))], dtype=np.float32)
            return (np.array(lerp3(p0, p1, e), dtype=np.float32),
                    np.array(lerp3(tgt0, tgt1, e), dtype=np.float32),
                    lerp(f0, f1, e), lerp(r0, r1, e), lerp(b0, b1, e))

        if jn == "terbang" and "jalur" in g:
            pts = [tuple(float(v) for v in pt) for pt in g["jalur"]]
            pos = np.array(catmull_rom(pts, e), dtype=np.float32)
            tgt = np.array(self._resolve_target(g, t), dtype=np.float32)
            return pos, tgt, f0, r0, b0

        if jn == "ikut":
            fid = g.get("fokus") or (self.actors[0].id if self.actors else None)
            if fid and fid in self.actor_map:
                ap = self.actor_map[fid].pos_at(t)[0]
                off = np.array(g.get("offset", [0.4, 1.35, 3.0]), dtype=np.float32)
                tgt = np.array([ap[0], ap[1] + 1.05, ap[2]], dtype=np.float32)
                pos = np.array([ap[0] + off[0], ap[1] + off[1], ap[2] + off[2]], dtype=np.float32)
                return pos, tgt, f0, r0, b0
            return start_pose

        if jn == "punch_in":
            es = e_snap(p)
            faktor = float(g.get("faktor", 0.58))
            pos = np.array(lerp3(p0, tgt0 + (p0 - tgt0) * faktor, es), dtype=np.float32)
            fov = lerp(f0, max(24.0, f0 - float(g.get("zoom", 10.0))), es)
            return pos, tgt0, fov, r0, b0

        if jn == "hentak":
            # Zoom cepat masuk lalu memantul kembali ke posisi semula
            pulse = math.sin(math.pi * clamp(p)) * float(g.get("kuat", 0.16))
            pos = tgt0 + (p0 - tgt0) * (1.0 - pulse)
            fov = max(22.0, f0 - pulse * 18.0)
            return pos, tgt0, fov, r0, b0

        if jn == "dolly_zoom":
            # Efek Vertigo: jarak berubah, FOV disesuaikan agar ukuran subjek tetap konstan
            faktor = float(g.get("faktor", 1.65))
            dist_scale = lerp(1.0, faktor, e)
            pos = tgt0 + (p0 - tgt0) * dist_scale
            half_rad = math.atan(math.tan(math.radians(f0 * 0.5)) / max(0.35, dist_scale))
            fov = clamp(math.degrees(half_rad * 2.0), 18.0, 85.0)
            return pos, tgt0, fov, r0, b0

        if jn == "truck":
            delta = np.array([float(g.get("x", 1.2)), float(g.get("y", 0.0)), float(g.get("z", 0.0))], dtype=np.float32) * e
            return p0 + delta, tgt0 + delta, f0, r0, b0

        if jn == "pan":
            v = tgt0 - p0
            da = math.radians(float(g.get("derajat", 30.0))) * e
            c_a, s_a = math.cos(da), math.sin(da)
            nv = np.array([v[0] * c_a + v[2] * s_a, v[1] + float(g.get("naik", 0.0)) * e, -v[0] * s_a + v[2] * c_a], dtype=np.float32)
            return p0, p0 + nv, f0, r0, b0

        if jn == "pindah_fokus":
            tgt1 = np.array(self._resolve_target(g, t), dtype=np.float32)
            tgt = np.array(lerp3(tgt0, tgt1, e), dtype=np.float32)
            blur = max(b0, float(g.get("blur", 1.6)) * math.sin(math.pi * p))
            return p0, tgt, f0, r0, blur

        if jn in ("push", "pull", "terbang", "miring", "whip", "potong"):
            end_pose = self._cam_pose_from_spec(g.get("ke", g), start_pose, t1)
            p1, tgt1, f1, r1, b1 = end_pose
            if jn == "push" and "ke" not in g:
                f1 = max(28.0, f0 - float(g.get("zoom", 8.0)))
                p1 = tgt0 + (p0 - tgt0) * float(g.get("faktor", 0.78))
            elif jn == "pull" and "ke" not in g:
                f1 = min(60.0, f0 + float(g.get("zoom", 8.0)))
                p1 = tgt0 + (p0 - tgt0) * float(g.get("faktor", 1.32))
            u = 1.0 if jn == "potong" else e
            blur = lerp(b0, b1, u)
            if jn == "whip" and 0.1 < p < 0.9:
                blur = max(blur, 3.0 * math.sin(math.pi * p))
            return (np.array(lerp3(p0, p1, u), dtype=np.float32),
                    np.array(lerp3(tgt0, tgt1, u), dtype=np.float32),
                    lerp(f0, f1, u), lerp(r0, r1, u), blur)

        return start_pose

    def _prep_cam(self):
        cam = self.s.get("kamera", {})
        base = self._cam_pose_from_spec(cam.get("awal", {"ukuran": "penuh"}), None, 0.0)
        moves = []
        for g in sorted(cam.get("gerak", []), key=lambda x: self.when(x)):
            t0 = self.when(g)
            dur = float(g.get("dur", 0.22 if g.get("jenis") in ("punch_in", "hentak") else 1.2))
            t1 = t0 + dur
            moves.append((t0, t1, g, base))
            if g.get("jenis") not in ("goyang", "hentak"):
                base = self._eval_cam_move(g, base, t1, 1.0, t1)
        return moves

    def cam_at(self, t):
        cam = self.s.get("kamera", {})
        pose = self._cam_pose_from_spec(cam.get("awal", {"ukuran": "penuh"}), None, 0.0)
        shake = np.zeros(3, dtype=np.float32)

        for t0, t1, g, start_pose in self.cam_moves:
            if t < t0:
                continue
            p = prog(t, t0, t1)
            if g.get("jenis") == "goyang":
                kuat = float(g.get("kuat", 0.06)) * (1.0 - p)
                shake += np.array([math.sin(t * 48.0) * kuat, math.cos(t * 55.0) * kuat * 0.7, 0.0], dtype=np.float32)
            else:
                pose = self._eval_cam_move(g, start_pose, t, p, t1)

        pos, tgt, fov, roll, blur = pose
        dx_a, dy_a, freq = GAYA_DRIFT.get(cam.get("gaya", "halus"), GAYA_DRIFT["halus"])
        drift = np.array([math.sin(t * freq) * dx_a, math.cos(t * freq * 0.76) * dy_a, 0.0], dtype=np.float32) if freq > 0 else np.zeros(3, dtype=np.float32)
        return Cam3D(pos=pos + shake + drift, target=tgt + shake * 0.35, fov=fov, roll=roll, blur=blur)

    def _draw_2d_overlays(self, img, cam, t):
        W, H = self.W, self.H
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        scale_ref = H / 1080.0 if W >= H else W / 1080.0

        # Balon ucapan
        for a, b, bl in self.balloons:
            if not (a <= t <= b):
                continue
            aid = bl.get("tokoh")
            if aid in self.actor_map:
                ap = self.actor_map[aid].pos_at(t)[0]
                pr = cam.project_point((ap[0], ap[1] + 1.85, ap[2]), W, H)
            else:
                pr = (W * 0.5, H * 0.28, 3.0, 600.0)
            if not pr:
                continue
            px, py = pr[0], pr[1]
            txt = str(bl.get("teks", ""))
            f = font("teks", int(30 * scale_ref))
            tb = d.textbbox((0, 0), txt, font=f)
            tw, th = tb[2] - tb[0], tb[3] - tb[1]
            pad = int(18 * scale_ref)
            bx = clamp(px, tw * 0.5 + pad + 16, W - tw * 0.5 - pad - 16)
            by = max(th * 0.5 + pad + 16, py - 42 * scale_ref)
            d.rounded_rectangle([bx - tw / 2 - pad, by - th / 2 - pad * 0.8, bx + tw / 2 + pad, by + th / 2 + pad * 0.8],
                                radius=int(20 * scale_ref), fill=PUTIH + (245,), outline=OUT + (255,), width=4)
            d.text((bx, by), txt, font=f, fill=HITAM + (255,), anchor="mm")

        # Teks overlay (judul / seru / label)
        for a, b, tx in self.texts:
            if not (a <= t <= b):
                continue
            txt = str(tx.get("teks", ""))
            gaya = tx.get("gaya", "judul")
            pos_rel = tx.get("pos", [0.5, 0.16])
            x, y = pos_rel[0] * W, pos_rel[1] * H
            sz = int(tx.get("ukuran", 52 if gaya == "seru" else 42) * scale_ref)
            f = font("seru" if gaya == "seru" else "judul", sz)
            sc_pop = e_back(prog(t, a, a + 0.25))
            if sc_pop > 0.05:
                d.text((x, y), txt, font=f, fill=KUNING + (255,) if gaya == "seru" else PUTIH + (255,),
                       stroke_width=max(3, int(sz * 0.14)), stroke_fill=OUT + (255,), anchor="mm")

        # Efek layar (vinyet / flash / garis_kecepatan)
        for a, b, fx in self.fxs:
            if not (a <= t <= b):
                continue
            jn = fx.get("jenis", "vinyet")
            if jn == "flash":
                al = int(220 * (1.0 - prog(t, a, min(b, a + 0.35))))
                if al > 0:
                    d.rectangle([0, 0, W, H], fill=PUTIH + (al,))
            elif jn == "vinyet":
                for k in range(6):
                    al = int(22 * (6 - k))
                    m = k * 14
                    d.rectangle([m, m, W - m, H - m], outline=(10, 12, 18, al), width=14)
            elif jn == "garis_kecepatan":
                cx, cy = W * 0.5, H * 0.5
                ang0 = int((t * 12) % 360)
                for i in range(28):
                    ang = math.radians(i * (360 / 28) + ang0)
                    r0, r1 = min(W, H) * 0.36, max(W, H) * 0.85
                    d.line([cx + math.cos(ang) * r0, cy + math.sin(ang) * r0,
                            cx + math.cos(ang) * r1, cy + math.sin(ang) * r1], fill=PUTIH + (135,), width=4)

        return Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB")

    def render(self, t, level):
        sc = Scene3D()
        DN.build_set(sc, self.s.get("latar", "kamar_belajar"), t, self.opsi)
        for a, b, pr in self.props:
            if a <= t <= b:
                BD.draw_prop(sc, pr, t=t)
        for ak in self.actors:
            ak.draw(sc, t, level)
        cam = self.cam_at(t)
        img = sc.render(cam, self.W, self.H, t=t)
        return self._draw_2d_overlays(img, cam, t)

    def events(self):
        ev = []
        for ak in self.actors:
            if ak.t_in is not None:
                ev.append((self.start + ak.t_in, "pop", "masuk"))
            for t0, _, kind in ak.icons:
                ev.append((self.start + t0, "ikon", kind))
        for t0, _, g, _ in self.cam_moves:
            jn = g.get("jenis")
            if jn in ("whip", "terbang", "crane", "orbit", "spiral", "dolly_zoom"):
                ev.append((self.start + t0, "whoosh", jn))
            elif jn in ("goyang", "punch_in", "hentak"):
                ev.append((self.start + t0, "punch", jn))
        return ev
