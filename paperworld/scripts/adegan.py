# -*- coding: utf-8 -*-
"""
adegan.py - sutradara adegan 3D Pop-Up Paper Craft untuk PaperWorld:
            aktor kertas, kamera 3D, animasi opsi pop-up/pintu, balon, teks, dan SFX.
"""
import math, os, re, sys
import numpy as np
from PIL import Image, ImageDraw
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from paper import (
    OUT, KERTAS_TEPI, PUTIH, KRIM, HITAM, KORAL, MERAH, BIRU, KUNING, HIJAU, TEAL,
    clamp, prog, lerp, lerp3, e_io, e_spring, EASE, catmull_rom, font, Cam3D, ScenePaper,
)
from aset_global.sinematografi import (
    SinematografiRig, apply_cinematic_modifiers, calc_ots_pose, terapkan_sinemaskop,
)
from aset_global.variasi import project_seed, seed_aktor, variasi_aksi_aktor_3d, variasi_kamera_3d
import tokoh as TK
import benda as BD
import dunia as DN

UKURAN = {
    "sangat_lebar": (8.2, 2.2, 50.0),
    "lebar":        (4.6, 0.85, 45.0),
    "penuh":        (3.3, 0.45, 44.0),
    "sedang":       (2.2, 0.35, 40.0),
    "dekat":        (1.45, 0.22, 36.0),
    "sangat_dekat": (0.95, 0.12, 32.0),
}


def norm(s):
    return re.sub(r"[^\w\s]", "", (s or "").lower().replace("-", " ")).split()


class Aktor:
    def __init__(self, sc, spec, cast):
        self.sc = sc
        self.id = spec.get("id") or spec.get("dasar") or "luna"
        dasar = spec.get("dasar", self.id)
        base = cast.get(self.id, cast.get(dasar, dasar))
        if isinstance(base, str):
            base = {"dasar": base}
        base = dict(base)
        for k in ("kacamata", "hijab", "rambut", "kemeja", "dasi", "bawah", "bawah_warna", "syal", "mantel", "blazer"):
            if k in spec:
                base[k] = spec[k]
        self.tk = TK.TokohKertas(base)
        self.s = float(spec.get("skala", 1.0))
        if "pos" in spec:
            self.x0, self.y0, self.z0 = [float(v) for v in spec["pos"]]
        else:
            self.x0 = float(spec.get("x", 0.0))
            self.y0 = float(spec.get("y", 0.0))
            self.z0 = float(spec.get("z", 0.0))
        proj = getattr(getattr(sc, "film", None), "proj", None)
        self.seed = seed_aktor(project_seed(proj), self.id, getattr(sc, "idx", 0))

        base_state = {
            k: spec[k] for k in ("pose", "ekspresi", "hadap", "bawa", "ransel", "bicara", "lihat", "pop_up") if k in spec
        }
        base_state.setdefault("pose", "diam")
        base_state.setdefault("ekspresi", "tenang")
        base_state.setdefault("hadap", "depan")
        base_state.setdefault("pop_up", 1.0)
        base_state["t"] = 0.0
        self.keys = [base_state]
        self.moves = []
        self.icons = []
        self.t_in = None
        self.t_out = None

        raw_aksi = spec.get("aksi") or variasi_aksi_aktor_3d(spec, sc.dur, getattr(sc, "idx", 0), proj, valid_poses=getattr(TK, "POSE", None))
        acts = [(sc.when(a), a) for a in raw_aksi]
        mk = spec.get("masuk")
        if mk:
            t0 = sc.when(mk)
            dur = float(mk.get("dur", 0.9))
            dr = mk.get("dari", "kiri")
            gaya = mk.get("gaya", "jalan")
            self.t_in = t0
            if dr == "lipat":
                self.keys.append(dict(t=t0, pop_up=0.0))
                self.keys.append(dict(t=t0 + dur, pop_up=1.0))
            elif dr in ("kiri", "kanan", "belakang", "depan"):
                jarak = float(mk.get("jarak", 4.0))
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
            jarak = float(xk.get("jarak", 4.0))
            dx = jarak if dr == "kanan" else -jarak if dr == "kiri" else 0.0
            dz = jarak if dr == "depan" else -jarak if dr == "belakang" else 0.0
            acts.append((t0, dict(ke_pos=(self.x0 + dx, self.y0, self.z0 + dz), durasi=dur, gaya=xk.get("gaya", "jalan"))))

        acts.sort(key=lambda z: z[0])
        cur = (self.x0, self.y0, self.z0)
        for t, a in acts:
            st = {k: a[k] for k in ("pose", "ekspresi", "hadap", "bawa", "ransel", "bicara", "lihat", "skala", "pop_up") if k in a}
            if st:
                st["t"] = t
                self.keys.append(st)
            if any(k in a for k in ("ke_x", "ke_y", "ke_z", "ke_pos")):
                p0 = self.moves[-1]["p1"] if self.moves else cur
                if "ke_pos" in a:
                    tx, ty, tz = [float(v) for v in a["ke_pos"]]
                else:
                    tx, ty, tz = float(a.get("ke_x", p0[0])), float(a.get("ke_y", p0[1])), float(a.get("ke_z", p0[2]))
                dist = math.dist(p0, (tx, ty, tz))
                dur = float(a.get("durasi", max(0.5, dist / 1.4)))
                gaya = a.get("gaya", "jalan" if dist > 0.2 else "geser")
                self.moves.append(dict(t0=t, t1=t + dur, p0=p0, p1=(tx, ty, tz), gaya=gaya))
                if dist > 0.2 and "hadap" not in a and gaya in ("jalan", "lari", "lompat"):
                    ang = math.degrees(math.atan2(tx - p0[0], tz - p0[2]))
                    self.keys.append(dict(t=t, hadap=ang))
                    if a.get("hadap_akhir"):
                        self.keys.append(dict(t=t + dur, hadap=a["hadap_akhir"]))
                cur = (tx, ty, tz)
            if "efek" in a:
                self.icons.append((t, t + float(a.get("efek_dur", 1.8)), a["efek"]))
        self.keys.sort(key=lambda d: d["t"])

    def pos_at(self, t):
        p = (self.x0, self.y0, self.z0)
        moving, gaya = False, "diam"
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
        prev_hadap = cur.get("hadap", "depan")
        hadap_t = -99.0
        prev_pop = float(cur.get("pop_up", 1.0))
        pop_t = -99.0
        for k in self.keys[1:]:
            if k["t"] <= t:
                if "pose" in k and k["pose"] != cur.get("pose"):
                    prev_pose = cur.get("pose", "diam")
                    pose_t = k["t"]
                if "hadap" in k and k["hadap"] != cur.get("hadap"):
                    prev_hadap = cur.get("hadap", "depan")
                    hadap_t = k["t"]
                if "pop_up" in k and float(k["pop_up"]) != float(cur.get("pop_up", 1.0)):
                    prev_pop = float(cur.get("pop_up", 1.0))
                    pop_t = k["t"]
                cur.update(k)
        pos, moving, gaya = self.pos_at(t)
        pose = cur.get("pose", "diam")
        mix = prog(t, pose_t, pose_t + 0.28) if pose_t > 0 else 1.0
        if moving:
            pose = prev_pose = gaya
            mix = 1.0
        # Interpolasi putaran badan 3D halus saat hadap berubah (misal berbalik 180 derajat!)
        hadap_val = cur.get("hadap", "depan")
        if hadap_t > -50.0 and t < hadap_t + 0.36:
            y0 = self.tk._yaw_from_hadap(prev_hadap)
            y1 = self.tk._yaw_from_hadap(hadap_val)
            dy = ((y1 - y0 + 180.0) % 360.0) - 180.0
            if abs(dy) < 1e-3 and abs(y1 - y0) > 90.0:
                dy = 180.0
            hadap_val = y0 + dy * e_io(prog(t, hadap_t, hadap_t + 0.36))
        pop_val = float(cur.get("pop_up", 1.0))
        if pop_t > -50.0 and t < pop_t + 0.42:
            pop_val = lerp(prev_pop, pop_val, e_io(prog(t, pop_t, pop_t + 0.42)))
        bt = (t + self.seed) % 3.2
        blink = 1.0 if bt < 0.12 else 0.0
        bicara = cur.get("bicara", False)
        if isinstance(bicara, list):
            bicara = any(a <= t <= b for a, b in bicara)
        open_amt = level if bicara else 0.0
        amp = 1.0 if moving else 0.0
        phase = t * (9.5 if gaya == "lari" else 6.8)
        st = TK.state(
            pose=prev_pose if mix < 1.0 else pose,
            pose2=pose if mix < 1.0 else None,
            mix=e_io(mix) if mix < 1.0 else 0.0,
            expr=cur.get("ekspresi", "tenang"),
            hadap=hadap_val,
            lihat=tuple(cur.get("lihat", (0.0, 0.0))),
            blink=blink, open_amt=open_amt,
            bawa=cur.get("bawa"), ransel=bool(cur.get("ransel", False)),
            pop_up=pop_val,
            t=t, amp=amp, phase=phase,
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
                BD.draw_icon_3d(sc, kind, (head_p[0], head_p[1] + 0.24, head_p[2]), t=t - t0, s=s * 0.95)


# =================================================================== ADEGAN
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
        for k in ("waktu", "jam", "alarm", "papan", "warna", "mode_pintu", "buka_pintu",
                  "buka_pintu_kanan", "pop_jam", "pintu_tengah_pop", "pintu_buka_semua",
                  "pop_notif", "flip_judul", "jatuh_pintu", "lipat_kartu",
                  "pop_play", "pop_door", "pop_kota", "pop_gang", "pop_pintu_biru",
                  "trans_malam", "drop_malam", "trans_fajar", "ray_scale",
                  "domino_pintu", "rebah_labirin", "lipat_tahap"):
            if k in spec:
                self.opsi[k] = spec[k]
        self.anim_opsi = [(self.when(a), a) for a in spec.get("animasi_opsi", [])]
        self.anim_opsi.sort(key=lambda z: z[0])
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
        if key in obj:
            return float(obj[key])
        return float(default)

    def opsi_at(self, t):
        out = dict(self.opsi)
        for t0, sp in self.anim_opsi:
            if t < t0:
                break
            dur = float(sp.get("dur", 0.0))
            q = 1.0 if dur <= 0.01 else e_io(prog(t, t0, t0 + dur))
            for k, v in sp.items():
                if k in ("t", "kata", "geser", "urutan", "dur"):
                    continue
                if isinstance(v, (int, float)) and not isinstance(v, bool) and dur > 0.01:
                    prev = float(out.get(k, 0.0))
                    out[k] = lerp(prev, float(v), q)
                else:
                    out[k] = v
        return out

    def _resolve_target(self, cam_spec, t):
        if "target" in cam_spec:
            return tuple(float(v) for v in cam_spec["target"])
        fok = cam_spec.get("fokus")
        if isinstance(fok, list) and fok:
            pts = [self.actor_map[fid].pos_at(t)[0] for fid in fok if fid in self.actor_map]
            if pts:
                return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts) + 0.95, sum(p[2] for p in pts) / len(pts))
        if isinstance(fok, str) and fok in self.actor_map:
            p = self.actor_map[fok].pos_at(t)[0]
            return (p[0], p[1] + 0.95, p[2])
        if self.actors:
            p = self.actors[0].pos_at(t)[0]
            return (p[0], p[1] + 0.95, p[2])
        return (0.0, 1.0, 0.0)

    def _cam_pose_from_spec(self, spec, prev=None, t=0.0):
        portrait = self.W < self.H
        if prev is None:
            pos = np.array([0.0, 1.5, 4.4], dtype=np.float32)
            tgt = np.array([0.0, 0.95, 0.0], dtype=np.float32)
            fov, roll, blur = 45.0, 0.0, 0.0
        else:
            pos = np.array(prev[0], dtype=np.float32)
            tgt = np.array(prev[1], dtype=np.float32)
            fov, roll, blur = prev[2], prev[3], prev[4]

        uk = spec.get("ukuran")
        if uk == "aerial":
            tgt = np.array(self._resolve_target(spec, t), dtype=np.float32)
            pos = tgt + np.array([0.0, 12.0, 8.5], dtype=np.float32)
            fov = 48.0
        elif uk in UKURAN:
            dist, dy, fv = UKURAN[uk]
            tgt = np.array(self._resolve_target(spec, t), dtype=np.float32)
            sudut = spec.get("sudut", "depan")
            dir_v = {
                "depan": np.array([0.0, 0.0, 1.0]),
                "kanan": np.array([0.85, 0.0, 0.52]),
                "kiri":  np.array([-0.85, 0.0, 0.52]),
                "belakang": np.array([0.0, 0.0, -1.0]),
                "serong_kanan": np.array([0.48, 0.0, 0.88]),
                "serong_kiri":  np.array([-0.48, 0.0, 0.88]),
            }.get(sudut, np.array([0.0, 0.0, 1.0]))
            pos = tgt + dir_v.astype(np.float32) * dist + np.array([0.0, dy, 0.0], dtype=np.float32)
            fov = fv
        elif "fokus" in spec or "target" in spec:
            tgt = np.array(self._resolve_target(spec, t), dtype=np.float32)

        if prev is None or any(k in spec for k in ("ukuran", "bahu", "pos")):
            roll, blur = 0.0, 0.0
        bahu_id = spec.get("bahu")
        if bahu_id and bahu_id in self.actor_map:
            pos, tgt, fov = calc_ots_pose(self.actor_map[bahu_id].pos_at(t)[0], self._resolve_target(spec, t), spec, portrait=portrait)
        if "pos" in spec:
            pos = np.array(spec["pos"], dtype=np.float32)
        if "target" in spec:
            tgt = np.array(spec["target"], dtype=np.float32)
        if "dx" in spec or "dy" in spec or "dz" in spec:
            d = np.array([float(spec.get("dx", 0)), float(spec.get("dy", 0)), float(spec.get("dz", 0))], dtype=np.float32)
            pos, tgt = pos + d, tgt + d
        if "fov" in spec:
            fov = float(spec["fov"])
        elif portrait and uk in UKURAN:
            fov = min(58.0, fov * 1.14)
        if "r" in spec or "roll" in spec:
            roll = float(spec.get("r", spec.get("roll", roll)))
        if "blur" in spec:
            blur = float(spec["blur"])
        pos, tgt, fov, roll, blur = apply_cinematic_modifiers(pos, tgt, fov, roll, blur, spec)
        return [pos, tgt, fov, roll, blur]

    def _resolve_actor_pos(self, fid, t):
        fid = fid or (self.actors[0].id if self.actors else None)
        if fid and fid in self.actor_map:
            return self.actor_map[fid].pos_at(t)[0]
        return None

    def _prep_cam(self):
        raw_cam = self.s.get("kamera", {})
        proj = getattr(self.film, "proj", None)
        cam_spec = variasi_kamera_3d(raw_cam, self.dur, self.idx, proj, actor_ids=[a.id for a in self.actors])
        self.cam_rig = None
        if cam_spec.get("shot") or cam_spec.get("shots") or (isinstance(raw_cam, dict) and not raw_cam.get("gerak") and cam_spec.get("gerak")):
            self.cam_rig = SinematografiRig(
                cam_spec, self.dur, self.when,
                self._cam_pose_from_spec, self._resolve_target, self._resolve_actor_pos,
            )
            self.awal_cam = self._cam_pose_from_spec(cam_spec.get("awal", {"ukuran": "lebar"}), None, 0.0)
            return []
        awal = self._cam_pose_from_spec(cam_spec.get("awal", {"ukuran": "lebar"}), None, 0.0)
        self.awal_cam = awal
        moves = []
        cur = [awal[0].copy(), awal[1].copy(), awal[2], awal[3], awal[4]]
        for g in cam_spec.get("gerak", []):
            t0 = self.when(g)
            k = g.get("jenis", "pindah")
            dur = float(g.get("dur", 0.25 if k in ("zoom_cepat", "potong") else 0.38 if k == "whip" else 1.5))
            if k in ("punch", "goyang", "ikut", "ayun"):
                moves.append(dict(kind=k, t0=t0, t1=self.when(g, "sampai", t0 + dur), spec=g))
                continue
            ke = g.get("ke", {})
            nxt = self._cam_pose_from_spec(ke, cur, t0)
            if k in ("push", "mendekat") and "pos" not in ke and "ukuran" not in ke:
                kali = float(g.get("kali", ke.get("kali", 1.5)))
                nxt[0] = cur[1] + (cur[0] - cur[1]) / max(0.35, kali)
            elif k in ("pull", "menjauh", "reveal") and "pos" not in ke and "ukuran" not in ke:
                kali = float(g.get("kali", ke.get("kali", 1.65)))
                nxt[0] = cur[1] + (cur[0] - cur[1]) * kali
            elif k == "orbit":
                ang = math.radians(float(g.get("sudut", ke.get("sudut", 36.0))))
                vec = cur[0] - cur[1]
                c, s = math.cos(ang), math.sin(ang)
                nxt[0] = cur[1] + np.array([vec[0] * c + vec[2] * s, vec[1] + float(g.get("dy", 0.0)), -vec[0] * s + vec[2] * c], dtype=np.float32)
            elif k == "crane":
                nxt[0] = cur[0] + np.array([float(ke.get("dx", 0.0)), float(ke.get("dy", 8.0)), float(ke.get("dz", 5.5))], dtype=np.float32)
                if "target" not in ke:
                    nxt[1] = cur[1] + np.array([0.0, float(ke.get("target_dy", -0.5)), 0.0], dtype=np.float32)
            elif k == "pan" and "target" not in ke and "fokus" not in ke:
                nxt[1] = cur[1] + np.array([float(ke.get("dx", g.get("dx", 1.2))), 0.0, 0.0], dtype=np.float32)
            elif k == "tilt" and "target" not in ke:
                nxt[1] = cur[1] + np.array([0.0, float(ke.get("dy", g.get("dy", 0.8))), 0.0], dtype=np.float32)
            elif k == "miring":
                nxt[3] = float(g.get("r", ke.get("r", 3.5)))
            elif k == "fokus":
                nxt[4] = float(g.get("blur", ke.get("blur", 5.0)))
            ease = g.get("ease", "snap" if k in ("zoom_cepat", "potong") else "io")
            moves.append(dict(kind=k, t0=t0, t1=t0 + (0.01 if k == "potong" else dur), a=cur, b=nxt, ease=ease, via=g.get("via")))
            cur = [nxt[0].copy(), nxt[1].copy(), nxt[2], nxt[3], nxt[4]]
        return moves

    def camera_at(self, t):
        if getattr(self, "cam_rig", None) is not None:
            pos, tgt, fov, roll, blur = self.cam_rig.eval(t)
            return Cam3D(pos=pos, target=tgt, fov=fov, roll=roll, blur=blur)
        pos = self.awal_cam[0].copy()
        tgt = self.awal_cam[1].copy()
        fov, roll, blur = self.awal_cam[2], self.awal_cam[3], self.awal_cam[4]
        for m in self.cam_moves:
            if m["kind"] in ("punch", "goyang", "ikut", "ayun"):
                continue
            if t < m["t0"]:
                break
            e = EASE.get(m["ease"], e_io)(prog(t, m["t0"], m["t1"]))
            a, b = m["a"], m["b"]
            if m["kind"] in ("terbang", "fly_through"):
                pts = [tuple(a[0].tolist())] + ([tuple(v) for v in m["via"]] if m["via"] else [
                    ((a[0][0] + b[0][0]) * 0.5, max(a[0][1], b[0][1]) + 0.45, (a[0][2] + b[0][2]) * 0.5)
                ]) + [tuple(b[0].tolist())]
                pos = np.array(catmull_rom(pts, e), dtype=np.float32)
            else:
                pos = a[0] + (b[0] - a[0]) * e
            tgt = a[1] + (b[1] - a[1]) * e
            fov, roll, blur = lerp(a[2], b[2], e), lerp(a[3], b[3], e), lerp(a[4], b[4], e)

        for m in self.cam_moves:
            k = m["kind"]
            if k not in ("ikut", "punch", "goyang", "ayun"):
                continue
            sp = m["spec"]
            if k == "ikut" and m["t0"] <= t <= m["t1"]:
                fok = sp.get("fokus")
                if fok in self.actor_map:
                    ap = np.array(self.actor_map[fok].pos_at(max(0.0, t - float(sp.get("lag", 0.22))))[0], dtype=np.float32)
                    ap_now = np.array(self.actor_map[fok].pos_at(t)[0], dtype=np.float32)
                    off = np.array(sp.get("offset", [0.4, 1.45, 3.6]), dtype=np.float32)
                    tgt = ap_now + np.array([0.0, 0.95, 0.0], dtype=np.float32)
                    pos = ap + off
            elif k == "punch" and m["t0"] <= t <= m["t1"]:
                fov *= (1.0 - float(sp.get("kuat", 0.14)) * math.sin(math.pi * prog(t, m["t0"], m["t1"])))
            elif k == "goyang" and m["t0"] <= t <= m["t1"]:
                q = prog(t, m["t0"], m["t1"])
                kuat = float(sp.get("kuat", 6.0)) * 0.008 * (1.0 - q)
                pos = pos + np.array([math.sin(t * 47.0) * kuat, math.cos(t * 53.0) * kuat * 0.8, 0.0], dtype=np.float32)
                roll += math.sin(t * 39.0) * kuat * 18.0
            elif k == "ayun" and m["t0"] <= t <= m["t1"]:
                per = float(sp.get("periode", 5.5))
                kuat = float(sp.get("kuat", 0.30))
                if kuat > 5.0:
                    kuat *= 0.008
                pos = pos + np.array([math.sin(t * 2 * math.pi / per) * kuat, math.cos(t * 2 * math.pi / per) * kuat * 0.2, 0.0], dtype=np.float32)

        pos = pos + np.array([math.sin(t * 0.7) * 0.010, math.cos(t * 0.9) * 0.008, 0.0], dtype=np.float32)
        return Cam3D(pos=pos, target=tgt, fov=fov, roll=roll, blur=blur)

    def _draw_2d_overlays(self, img, cam, t):
        W, H = self.W, self.H
        if self.s.get("sinemaskop") or self.film.proj.get("sinemaskop"):
            img = terapkan_sinemaskop(img)
        for t0, t1, fx in self.fxs:
            k = fx.get("jenis")
            if k == "flash" and t0 <= t <= t0 + float(fx.get("dur", 0.35)):
                a = clamp((1.0 - prog(t, t0, t0 + float(fx.get("dur", 0.35)))) * float(fx.get("kuat", 0.85)), 0.0, 0.92)
                img = Image.blend(img, Image.new("RGB", (W, H), PUTIH), a)
            elif k == "gelap" and t0 <= t <= t1:
                img = Image.blend(img, Image.new("RGB", (W, H), (22, 20, 26)), clamp(float(fx.get("kuat", 0.5)), 0.0, 0.9))

        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for t0, t1, fx in self.fxs:
            k = fx.get("jenis")
            if k == "vinyet" and t0 <= t <= t1:
                kuat = clamp(float(fx.get("kuat", 0.45)), 0.1, 0.9)
                pad = int(min(W, H) * 0.14)
                for step in range(4):
                    al = int(kuat * 48 * (4 - step) / 4)
                    bw = int(pad * (step + 1) * 0.35)
                    d.rectangle([0, 0, W, bw], fill=(16, 12, 10, al))
                    d.rectangle([0, H - bw, W, H], fill=(16, 12, 10, al))
                    d.rectangle([0, 0, bw, H], fill=(16, 12, 10, al))
                    d.rectangle([W - bw, 0, W, H], fill=(16, 12, 10, al))
            elif k == "garis_kecepatan" and t0 <= t <= t0 + float(fx.get("dur", 0.7)):
                cx, cy = W * 0.5, H * 0.5
                r_in, r_out = min(W, H) * 0.28, max(W, H) * 0.85
                for i in range(28):
                    ang = i * (2 * math.pi / 28) + t * 3.0
                    d.line([(cx + math.cos(ang) * r_in, cy + math.sin(ang) * r_in), (cx + math.cos(ang) * r_out, cy + math.sin(ang) * r_out)], fill=(255, 252, 245, 165), width=max(2, int(W * 0.003)))

        for t0, t1, bl in self.balloons:
            if not (t0 <= t <= t1) or bl.get("oleh") not in self.actor_map:
                continue
            ak = self.actor_map[bl["oleh"]]
            pos, st, s = ak.state_at(t, 0.0)
            hp = ak.tk.head_anchor(pos, s, st["pose"])
            proj = cam.project_point((hp[0], hp[1] + 0.14, hp[2]), W, H)
            if proj is None:
                continue
            sx, sy, _, _ = proj
            txt = bl.get("teks", "")
            shown = txt[:max(1, int(len(txt) * clamp((t - t0) / max(0.3, len(txt) * 0.03), 0.15, 1.0)))]
            fs = max(18, int(min(W, H) * 0.030))
            f = font("teks", fs)
            bb = d.textbbox((0, 0), txt, font=f)
            tw, th = bb[2] - bb[0] + fs * 1.4, bb[3] - bb[1] + fs * 0.9
            bx, by = clamp(sx, tw * 0.55 + 16, W - tw * 0.55 - 16), clamp(sy - th * 0.8, th * 0.55 + 16, H * 0.72)
            d.rounded_rectangle([bx - tw / 2, by - th / 2, bx + tw / 2, by + th / 2], radius=fs * 0.65, fill=PUTIH + (244,), outline=KORAL + (255,), width=4)
            d.polygon([(bx - 10, by + th / 2 - 2), (bx + 10, by + th / 2 - 2), (clamp(sx, bx - 40, bx + 40), by + th / 2 + 18)], fill=PUTIH + (244,))
            d.text((bx, by), shown, font=f, fill=OUT + (255,), anchor="mm")

        for t0, t1, tx in self.texts:
            if not (t0 <= t <= t1):
                continue
            gaya, isi = tx.get("gaya", "kapsul"), tx.get("isi", "")
            pos_sp = tx.get("posisi", "atas")
            px, py = (pos_sp[0] * W, pos_sp[1] * H) if isinstance(pos_sp, list) else {
                "atas": (W * 0.5, H * 0.12), "tengah": (W * 0.5, H * 0.50),
                "bawah": (W * 0.5, H * 0.76), "kiri_atas": (W * 0.22, H * 0.12), "kanan_atas": (W * 0.78, H * 0.12),
            }.get(pos_sp, (W * 0.5, H * 0.12))
            sz = float(tx.get("ukuran", 44 if gaya != "kapsul" else 28)) * (min(W, H) / 1080.0)
            col = TK.warna(tx.get("warna"), KORAL if gaya == "judul" else MERAH)
            if gaya == "kapsul":
                f = font("teks", sz)
                bb = d.textbbox((0, 0), isi, font=f)
                bw, bh = bb[2] - bb[0] + sz * 1.4, bb[3] - bb[1] + sz * 0.8
                d.rounded_rectangle([px - bw / 2, py - bh / 2, px + bw / 2, py + bh / 2], radius=bh * 0.45, fill=PUTIH + (238,), outline=KORAL + (255,), width=3)
                d.text((px, py), isi, font=f, fill=OUT + (255,), anchor="mm")
            elif gaya == "judul":
                f = font("judul", sz)
                bb = d.textbbox((0, 0), isi, font=f)
                bw, bh = bb[2] - bb[0] + sz * 1.5, bb[3] - bb[1] + sz * 0.9
                d.rounded_rectangle([px - bw / 2, py - bh / 2, px + bw / 2, py + bh / 2], radius=bh * 0.45, fill=col + (245,))
                d.text((px, py), isi, font=f, fill=PUTIH + (255,), anchor="mm")
            else:
                f = font("seru" if gaya == "seru" else "judul", sz * 1.25)
                d.text((px, py), isi, font=f, fill=col + (255,), anchor="mm", stroke_width=max(3, int(sz * 0.14)), stroke_fill=PUTIH + (255,))

        out = img.convert("RGBA")
        out.alpha_composite(ov)
        return out.convert("RGB")

    def render(self, t, finish=True):
        sc = ScenePaper()
        DN.build_world(sc, self.s.get("latar", "meja_hp"), t, self.opsi_at(t))
        lvl = self.film.level(self.start + t)
        for ak in self.actors:
            ak.draw(sc, t, lvl)
        for t0, t1, b in self.props:
            if t0 <= t <= t1:
                pos = tuple(b.get("pos", [b.get("x", 0.0), b.get("y", 0.0), b.get("z", 0.0)]))
                rot = tuple(b.get("rot", [0.0, 0.0, 0.0]))
                BD.draw_prop(sc, b.get("jenis", "buku"), pos, rot=rot, s=float(b.get("skala", 1.0)), t=t, **{k: v for k, v in b.items() if k not in ("jenis", "pos", "x", "y", "z", "rot", "skala", "t", "sampai")})
        cam = self.camera_at(t)
        return self._draw_2d_overlays(sc.render(cam, self.W, self.H, t=t, finish=finish), cam, t)

    def events(self):
        ev = []
        if self.opsi.get("alarm"):
            ev.append((self.start + 0.1, "alarm", 0.85))
        for ak in self.actors:
            for t0, _, kind in ak.icons:
                sfx_k = {"bohlam": "ding", "tanda_seru": "seru", "tanya": "tanya", "kilau": "sparkle", "bintang": "sparkle", "zzz": "zzz"}.get(kind, "pop")
                ev.append((self.start + t0, sfx_k, 0.85))
            for m in ak.moves:
                if m["gaya"] in ("jalan", "lari"):
                    tt = m["t0"] + 0.1
                    while tt < m["t1"]:
                        ev.append((self.start + tt, "langkah", 0.48))
                        tt += (0.28 if m["gaya"] == "lari" else 0.42)
        for t0, sp in self.anim_opsi:
            if "buka_pintu" in sp or "buka_pintu_kanan" in sp or "pintu_buka_semua" in sp:
                ev.append((self.start + t0, "pintu", 0.8))
            if "mode_pintu" in sp or "pintu_tengah_pop" in sp or "pop_jam" in sp:
                ev.append((self.start + t0, "lipat", 0.85))
            if "pop_notif" in sp:
                ev.append((self.start + t0, "notif", 0.9))
        for m in self.cam_moves:
            if m["kind"] == "whip":
                ev.append((self.start + m["t0"], "whoosh", 0.8))
            elif m["kind"] == "punch":
                ev.append((self.start + m["t0"], "thud", 0.8))
            elif m["kind"] in ("terbang", "fly_through"):
                ev.append((self.start + m["t0"], "whoosh_lembut", 0.65))
        for sx in self.s.get("sfx", []):
            ev.append((self.start + self.when(sx), sx.get("jenis", "pop"), float(sx.get("gain", 1.0))))
        return ev
