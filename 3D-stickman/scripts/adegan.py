# -*- coding: utf-8 -*-
"""
adegan.py - Sutradara adegan 3D-stickman: aktor, kamera 3D, properti, balon ucapan, teks, efek, dan pemicu SFX.
"""
import math, os, re, sys
import numpy as np
from PIL import Image, ImageDraw
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from engine3d import (
    OUT, PUTIH, KRIM, HITAM, MERAH, BIRU, KUNING, ORANYE, HIJAU, TEAL,
    clamp, prog, lerp, lerp3, e_io, e_out, e_in, e_back, e_snap, EASE,
    catmull_rom, font, Cam3D, Scene3D,
)
from aset_global.sinematografi import (
    ANGLE_PRESET, GAYA_DRIFT, SinematografiRig,
    apply_cinematic_modifiers, calc_ots_pose, terapkan_sinemaskop,
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


def norm(s):
    return re.sub(r"[^\w\s]", "", (s or "").lower().replace("-", " ")).split()


_HADAP_DEG = {
    "depan": 0.0, "serong_kanan": 24.0, "serong_kiri": -24.0,
    "kanan": 78.0, "kiri": -78.0, "belakang": 180.0,
}
_WALK_STYLES = ("jalan", "jalan_santai", "mengendap", "lari", "mundur")
_WALK_FREQ = {
    "lari": 9.8,
    "jalan": 6.8,
    "jalan_santai": 5.2,
    "mengendap": 4.4,
    "mundur": 5.6,
}


def _hadap_to_deg(v):
    if isinstance(v, (int, float)):
        return float(v)
    return _HADAP_DEG.get(str(v), 0.0)


def _lerp_angle_deg(a0, a1, u):
    d = ((a1 - a0 + 180.0) % 360.0) - 180.0
    return a0 + d * u


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
        self.seed = (sum(ord(ch) * (i + 1) for i, ch in enumerate(self.id)) % 97) / 10.0

        base_state = {k: spec[k] for k in ("pose", "ekspresi", "hadap", "bawa", "buku_kiri", "buku_kanan", "buku_isi", "bicara", "lihat", "gerak") if k in spec}
        base_state.setdefault("pose", "diam")
        base_state.setdefault("ekspresi", "senang")
        base_state.setdefault("hadap", "depan")
        base_state.setdefault("gerak", "aktif")
        base_state["t"] = 0.0
        self.keys = [base_state]
        self.moves = []
        self.icons = []
        self.t_in = None
        self.t_out = None
        self.patrol = spec.get("mondar_mandir")

        acts = [(sc.when(a), a) for a in spec.get("aksi", [])]
        # Dukungan multi-waypoint "jalur": [{"ke_pos": [...], "durasi": 2.0, "gaya": "jalan", "jeda": 0.4}, ...]
        jalur = spec.get("jalur")
        if isinstance(jalur, list) and jalur:
            t_cur = float(spec.get("jalur_mulai", 0.0))
            for wp in jalur:
                t_wp = sc.when(wp) if ("t" in wp or "kata" in wp) else t_cur
                acts.append((t_wp, wp))
                t_cur = t_wp + float(wp.get("durasi", 1.4)) + float(wp.get("jeda", 0.25))

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
                self.keys.append(dict(t=t0, hadap=h_in, durasi_putar=0.05))
                self.keys.append(dict(t=t0 + dur, hadap=mk.get("hadap_akhir", base_state["hadap"]), durasi_putar=float(mk.get("durasi_putar", 0.45))))
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
            st = {k: a[k] for k in ("pose", "ekspresi", "hadap", "durasi_putar", "durasi_pose", "bawa", "buku_kiri", "buku_kanan", "buku_isi", "bicara", "lihat", "skala", "gerak") if k in a}
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
                dur = float(a.get("durasi", max(0.5, dist / 1.15)))
                gaya = a.get("gaya", "jalan" if dist > 0.18 else "geser")
                self.moves.append(dict(t0=t, t1=t + dur, p0=p0, p1=(tx, ty, tz), gaya=gaya))
                if dist > 0.18 and "hadap" not in a and gaya in ("jalan", "jalan_santai", "mengendap", "lari", "lompat"):
                    dx, dz = tx - p0[0], tz - p0[2]
                    self.keys.append(dict(t=t, hadap=math.degrees(math.atan2(dx, dz)), durasi_putar=float(a.get("durasi_putar", 0.35))))
                    if a.get("hadap_akhir") is not None:
                        self.keys.append(dict(t=t + dur, hadap=a["hadap_akhir"], durasi_putar=float(a.get("durasi_putar", 0.45))))
                elif a.get("hadap_akhir") is not None:
                    self.keys.append(dict(t=t + dur, hadap=a["hadap_akhir"], durasi_putar=float(a.get("durasi_putar", 0.45))))
                cur = (tx, ty, tz)
            if "efek" in a:
                self.icons.append((t, t + float(a.get("efek_dur", 1.8)), a["efek"]))

        self.keys.sort(key=lambda d: d["t"])

    def pos_at(self, t):
        p = (self.x0, self.y0, self.z0)
        moving = False
        gaya = "diam"
        move_q = 1.0
        patrol_yaw = None
        for m in self.moves:
            if t < m["t0"]:
                break
            if t <= m["t1"]:
                q = prog(t, m["t0"], m["t1"])
                e = e_io(q) if m["gaya"] in ("geser", "lompat", "mundur") else (0.12 * e_io(q) + 0.88 * q)
                p = lerp3(m["p0"], m["p1"], e)
                if m["gaya"] == "lompat":
                    p = (p[0], p[1] + math.sin(math.pi * q) * 0.42, p[2])
                moving = m["gaya"] in _WALK_STYLES
                gaya = m["gaya"]
                move_q = q
                break
            p = m["p1"]

        # Mondar-mandir kontinu jika diaktifkan dan tidak sedang menjalankan move eksplisit
        if not moving and isinstance(self.patrol, dict):
            jarak = float(self.patrol.get("jarak", 0.65))
            siklus = max(1.2, float(self.patrol.get("siklus", 4.6)))
            sumbu = str(self.patrol.get("sumbu", "x")).lower()
            g_pat = self.patrol.get("gaya", "jalan_santai")
            u = ((t + self.seed * 0.25) % siklus) / siklus
            if u < 0.5:
                f = e_io(u * 2.0)
                off = lerp(-jarak, +jarak, f)
                vel = math.sin(math.pi * (u * 2.0))
                patrol_yaw = 78.0 if sumbu == "x" else 0.0
            else:
                f = e_io((u - 0.5) * 2.0)
                off = lerp(+jarak, -jarak, f)
                vel = math.sin(math.pi * ((u - 0.5) * 2.0))
                patrol_yaw = -78.0 if sumbu == "x" else 180.0
            p = (p[0] + off, p[1], p[2]) if sumbu == "x" else (p[0], p[1], p[2] + off)
            if vel > 0.14:
                moving = True
                gaya = g_pat
                move_q = 0.5
        return p, moving, gaya, move_q, patrol_yaw

    def state_at(self, t, level):
        cur = dict(self.keys[0])
        prev_pose = cur.get("pose", "diam")
        pose_t = 0.0
        pose_dur = 0.36
        prev_yaw = _hadap_to_deg(cur.get("hadap", "depan"))
        cur_yaw = prev_yaw
        yaw_t = -1.0
        yaw_dur = 0.48
        for k in self.keys[1:]:
            if k["t"] <= t:
                if "pose" in k and k["pose"] != cur.get("pose"):
                    prev_pose = cur.get("pose", "diam")
                    pose_t = k["t"]
                    pose_dur = max(0.08, float(k.get("durasi_pose", 0.36)))
                if "hadap" in k:
                    ny = _hadap_to_deg(k["hadap"])
                    if abs(((ny - cur_yaw + 180.0) % 360.0) - 180.0) > 1.0:
                        prev_yaw = cur_yaw
                        cur_yaw = ny
                        yaw_t = k["t"]
                        yaw_dur = max(0.05, float(k.get("durasi_putar", 0.48)))
                cur.update(k)

        pos, moving, gaya, move_q, patrol_yaw = self.pos_at(t)
        if yaw_t >= 0.0 and t < yaw_t + yaw_dur:
            yu = e_io(prog(t, yaw_t, yaw_t + yaw_dur))
            hadap_deg = _lerp_angle_deg(prev_yaw, cur_yaw, yu)
        else:
            hadap_deg = cur_yaw
        if patrol_yaw is not None:
            hadap_deg = patrol_yaw

        pose = cur.get("pose", "diam")
        mix = prog(t, pose_t, pose_t + pose_dur) if pose_t > 0 else 1.0
        if moving:
            # Transisi masuk/keluar jalan halus di 12% awal dan akhir langkah
            edge_mix = min(1.0, move_q / 0.12, (1.0 - move_q) / 0.12) if 0.0 < move_q < 1.0 else 1.0
            if edge_mix < 0.99:
                prev_pose, pose, mix = pose, gaya, edge_mix
            else:
                pose, prev_pose, mix = gaya, gaya, 1.0

        blink = 1.0 if ((t + self.seed) % 3.1) < 0.12 else 0.0
        bicara = cur.get("bicara", False)
        if isinstance(bicara, list):
            bicara = any(a <= t <= b for a, b in bicara)
        open_amt = level if bicara else 0.0
        walk_freq = _WALK_FREQ.get(gaya if moving else pose, 6.4)
        st = TK.state(
            pose=prev_pose if mix < 1.0 else pose,
            pose2=pose if mix < 1.0 else None,
            mix=e_io(mix) if mix < 1.0 else 0.0,
            expr=cur.get("ekspresi", "senang"),
            hadap=hadap_deg,
            lihat=tuple(cur.get("lihat", (0.0, 0.0))),
            blink=blink,
            open_amt=open_amt,
            bicara=bool(bicara),
            bawa=cur.get("bawa"),
            t=t,
            seed=self.seed,
            gerak=cur.get("gerak", "aktif"),
            amp=1.0 if moving else (0.78 if pose in _WALK_STYLES else 0.0),
            phase=(t + self.seed * 0.3) * walk_freq,
        )
        for bk in ("buku_kiri", "buku_kanan", "buku_isi"):
            if bk in cur:
                st[bk] = cur[bk]
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

        # Reset roll & blur bila berpindah ke bidikan baru (prev is None atau ada ukuran/bahu/pos baru)
        if prev is None or any(k in spec for k in ("ukuran", "bahu", "pos")):
            roll = 0.0
            blur = 0.0

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

        # Komposisi over-the-shoulder profesional via aset_global.sinematografi
        bahu_id = spec.get("bahu")
        if bahu_id and bahu_id in self.actor_map:
            pos, tgt, fov = calc_ots_pose(
                self.actor_map[bahu_id].pos_at(t)[0],
                self._resolve_target(spec, t),
                spec,
                portrait=portrait,
            )

        return apply_cinematic_modifiers(pos, tgt, fov, roll, blur, spec)

    def _resolve_actor_pos(self, fid, t):
        fid = fid or (self.actors[0].id if self.actors else None)
        if fid and fid in self.actor_map:
            return self.actor_map[fid].pos_at(t)[0]
        return None

    def _prep_cam(self):
        self.cam_rig = SinematografiRig(
            self.s.get("kamera", {}),
            self.dur,
            self.when,
            self._cam_pose_from_spec,
            self._resolve_target,
            self._resolve_actor_pos,
        )
        self.shots = self.cam_rig.shots
        return self.cam_rig.moves

    def cam_at(self, t):
        pos, tgt, fov, roll, blur = self.cam_rig.eval(t)
        return Cam3D(pos=pos, target=tgt, fov=fov, roll=roll, blur=blur)

    def _draw_2d_overlays(self, img, cam, t):
        W, H = self.W, self.H
        if self.s.get("sinemaskop") or self.film.proj.get("sinemaskop"):
            img = terapkan_sinemaskop(img)
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
        img = sc.render(cam, self.W, self.H, t=t, aa=float(getattr(self.film, "ss", 1.5)))
        return self._draw_2d_overlays(img, cam, t)

    def events(self):
        ev = []
        for ak in self.actors:
            if ak.t_in is not None:
                ev.append((self.start + ak.t_in, "pop", "masuk"))
            for t0, _, kind in ak.icons:
                ev.append((self.start + t0, "ikon", kind))
        ev.extend(self.cam_rig.sfx_events(self.start))
        return ev
