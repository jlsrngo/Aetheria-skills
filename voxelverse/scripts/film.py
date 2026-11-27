# -*- coding: utf-8 -*-
"""
film.py - menyusun semua adegan 3D VoxelVerse jadi film: jadwal, subtitle, transisi, fade, panel komik.
"""
import math, os, sys
import json
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from voxel import OUT, PUTIH, clamp, lerp, e_io, e_out, e_back, prog, font
from aset_global.transisi import blend_transisi, norm_transisi, sfx_transisi
import timing
from adegan import Adegan


class Film:
    def __init__(self, projdir, ss=1, ukuran=None):
        self.dir = projdir
        self.proj = json.load(open(os.path.join(projdir, "proyek.json"), encoding="utf-8"))
        W, H = ukuran or self.proj.get("ukuran", [1920, 1080])
        self.W, self.H = int(W), int(H)
        self.fps = int(self.proj.get("fps", 30))
        self.ss = ss
        vo = self.proj.get("vo")
        self.vo = os.path.join(projdir, vo) if vo and not os.path.isabs(vo) else vo
        if self.vo and not os.path.exists(self.vo):
            sys.exit(f"[GAGAL] file VO tidak ditemukan: {self.vo}")
        self.cast = self.proj.get("tokoh", {})
        sp = self.proj["adegan"]
        self.ts, self.total = timing.jadwal(sp, self.vo, tail=float(self.proj.get("ekor", 0.9)))
        wf = os.path.join(projdir, "input", "words.json")
        self.words = timing.kata_waktu(sp, self.ts, self.vo, wf)
        self.lv = timing.levels(self.vo, self.fps, self.total) if self.vo else None
        self.scenes = []
        for i, (sc, (a, b)) in enumerate(zip(sp, self.ts)):
            cls = Komik if sc.get("tipe") == "komik" else Adegan
            self.scenes.append(cls(dict(sc), self.W, self.H, a, b, self.fps, self, i))
        self.N = int(math.ceil(self.total * self.fps))
        self.pages = self._pages()
        self.warnings = [w for s in self.scenes for w in s.warn]

    def words_rel(self, idx):
        return self.words[idx] if idx < len(self.words) else []

    def level(self, t):
        if self.lv is None:
            return 0.5 + 0.5 * math.sin(t * 13.0) * math.sin(t * 5.3 + 1.0)
        i = int(t * self.fps)
        if i < 0 or i >= len(self.lv):
            return 0.0
        return float(self.lv[i])

    # ---------------------------------------------------------------- subtitle
    def _pages(self):
        pages = []
        for ws in self.words:
            cur = []
            for w in ws:
                cur.append(w)
                txt = " ".join(x[0] for x in cur)
                if len(cur) >= 6 or len(txt) > 32 or w[0][-1:] in ".?!" or (w[0][-1:] in ",;:" and len(txt) > 16):
                    pages.append(cur)
                    cur = []
            if cur:
                pages.append(cur)
        out = []
        for i, pg in enumerate(pages):
            t0 = pg[0][1]
            t1 = pages[i + 1][0][1] if i + 1 < len(pages) else pg[-1][2] + 0.6
            t1 = min(t1, pg[-1][2] + 0.9)
            out.append((t0, max(t1, pg[-1][2] + 0.15), pg))
        return out

    def caption(self, img, t):
        if not self.proj.get("subtitle", True):
            return img
        pg = None
        for a, b, p in self.pages:
            if a - 0.05 <= t < b:
                pg = p
                break
        if pg is None:
            return img

        style = self.proj.get("gaya_subtitle", "sinematik")
        ov = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        scale_ref = self.H / 1080.0 if self.W >= self.H else self.W / 1080.0
        size = int((46 if style == "sinematik" else 54) * scale_ref)
        f = font("teks", size)
        sp = size * 0.28
        lens = [d.textlength(w[0], font=f) for w in pg]
        maxw = self.W * 0.86
        lines = [[]]
        cw = 0.0
        for w, l in zip(pg, lens):
            if cw + l > maxw and lines[-1]:
                lines.append([])
                cw = 0.0
            lines[-1].append((w, l))
            cw += l + sp

        y0 = self.H * (0.885 if self.W >= self.H else 0.84) - (len(lines) - 1) * size * 0.62
        if style == "pil":
            bw = max(sum(l for _, l in ln) + sp * (len(ln) - 1) for ln in lines) + size * 1.4
            bh = len(lines) * size * 1.2 + size * 0.45
            d.rounded_rectangle(
                [self.W / 2 - bw / 2, y0 - bh / 2, self.W / 2 + bw / 2, y0 + bh / 2 + (len(lines) - 1) * size * 1.2],
                radius=size * 0.55, fill=PUTIH + (240,), outline=OUT + (255,), width=4,
            )
        elif style == "sinematik":
            bw = max(sum(l for _, l in ln) + sp * (len(ln) - 1) for ln in lines) + size * 1.1
            bh = len(lines) * size * 1.22 + size * 0.35
            d.rounded_rectangle(
                [self.W / 2 - bw / 2, y0 - bh / 2, self.W / 2 + bw / 2, y0 + bh / 2 + (len(lines) - 1) * size * 1.22],
                radius=size * 0.35, fill=(14, 18, 26, 145),
            )

        for li, ln in enumerate(lines):
            wline = sum(l for _, l in ln) + sp * (len(ln) - 1)
            x = self.W / 2 - wline / 2
            yy = y0 + li * size * 1.22
            for w, l in ln:
                active = w[1] - 0.02 <= t < w[2] + 0.05 or (t >= w[1] and w is pg[-1])
                if style == "sinematik":
                    col = (255, 224, 130, 255) if active else (242, 244, 248, 220)
                    d.text((x + l / 2, yy), w[0], font=f, fill=col, anchor="mm", stroke_width=max(2, int(size * 0.06)), stroke_fill=(10, 12, 18, 190))
                elif style == "pil":
                    col = (224, 62, 62, 255) if active else OUT + (255,)
                    d.text((x + l / 2, yy), w[0], font=f, fill=col, anchor="mm")
                else:  # komik
                    col = (255, 214, 60, 255) if active else PUTIH + (255,)
                    d.text((x + l / 2, yy), w[0], font=f, fill=col, anchor="mm", stroke_width=max(3, int(size * 0.14)), stroke_fill=OUT + (255,))
                x += l + sp

        out = img.convert("RGBA")
        out.alpha_composite(ov)
        return out.convert("RGB")

    # ---------------------------------------------------------------- frame & transisi
    def scene_index(self, T):
        i = 0
        while i + 1 < len(self.scenes) and T >= self.scenes[i + 1].start:
            i += 1
        return i

    def trans_of(self, j):
        sc = self.scenes[j]
        tr = sc.s.get("transisi")
        prev = self.scenes[j - 1]
        if tr is None or tr == "auto":
            same = prev.s.get("latar") == sc.s.get("latar") and prev.s.get("waktu") == sc.s.get("waktu")
            tr = {"jenis": "potong"} if same else {"jenis": "fade", "dur": 0.45}
        if isinstance(tr, str):
            tr = {"jenis": tr}
        d = dict(tr)
        d.setdefault("dur", 0.0 if d["jenis"] == "potong" else 0.50)
        return d

    def raw(self, T):
        i = self.scene_index(T)
        if i + 1 < len(self.scenes):
            tr = self.trans_of(i + 1)
            nxt = self.scenes[i + 1]
            if tr["dur"] > 0 and T >= nxt.start - tr["dur"] / 2:
                p = clamp((T - (nxt.start - tr["dur"] / 2)) / tr["dur"])
                A = self.scenes[i].render(T - self.scenes[i].start)
                B = nxt.render(T - nxt.start)
                return blend(A, B, p, tr)
        return self.scenes[i].render(T - self.scenes[i].start)

    def frame(self, f):
        T = f / self.fps
        img = self.raw(T)
        img = self.caption(img, T)
        fi = float(self.proj.get("fade_masuk", 0.5))
        fo = float(self.proj.get("fade_keluar", 0.8))
        a = 1.0
        if fi > 0 and T < fi:
            a = min(a, T / fi)
        if fo > 0 and T > self.total - fo:
            a = min(a, max(0.0, (self.total - T) / fo))
        if a < 0.999:
            img = Image.blend(Image.new("RGB", img.size, (16, 18, 26)), img, a)
        return img

    def events(self):
        ev = []
        for i, s in enumerate(self.scenes):
            ev += s.events()
            if i > 0:
                tr = norm_transisi(self.trans_of(i))
                sx = sfx_transisi(tr["jenis"])
                if sx:
                    t_ev = s.start - 0.02 if sx[0] == "kilat" else s.start - tr["dur"] / 2
                    ev.append((t_ev, sx[0], sx[1]))
        return sorted(ev)


def blend(A, B, p, tr):
    return blend_transisi(A, B, p, tr, outline_col=OUT)


# ==================================================================== panel komik 3D
class Komik:
    """Halaman panel 3D: beberapa mini-adegan voxel muncul satu per satu."""

    def __init__(self, spec, W, H, start, end, fps, film, idx):
        self.s = spec
        self.W, self.H = W, H
        self.start, self.end = start, end
        self.dur = max(0.2, end - start)
        self.fps, self.film, self.idx = fps, film, idx
        self.warn = []
        cols, rows = spec.get("grid", [3, 2])
        m = int(min(W, H) * 0.03)
        pw = (W - m * (cols + 1)) / cols
        ph = (H - m * (rows + 1)) / rows
        self.rect = []
        self.base = Adegan({"latar": "polos"}, W, H, start, end, fps, film, idx)
        self.warn += self.base.warn
        self.panels = []
        for i, ps in enumerate(spec.get("panel", [])):
            r, c = divmod(i, cols)
            x0, y0 = m + c * (pw + m), m + r * (ph + m)
            self.rect.append((x0, y0, pw, ph))
            tmu = self.base.when(ps.get("muncul", i * 1.2))
            sub = Adegan(dict(ps), int(pw), int(ph), start + tmu, end, fps, film, idx)
            self.panels.append((tmu, sub))
            self.warn += sub.warn
        self.full = {}

    def render(self, t):
        W, H = self.W, self.H
        page = Image.new("RGB", (W, H), (242, 236, 224))
        d = ImageDraw.Draw(page)
        zoom = self.s.get("zoom")
        zq, zi = 0.0, None
        if zoom:
            zi = int(zoom.get("panel", 0))
            z0 = self.base.when(zoom)
            zq = e_io(prog(t, z0, z0 + float(zoom.get("dur", 1.2))))
        for i, (tmu, sub) in enumerate(self.panels):
            if t < tmu:
                continue
            x0, y0, pw, ph = self.rect[i]
            q = e_back((t - tmu) / 0.35, 2.0)
            if zi == i and zq >= 0.995:
                if i not in self.full:
                    self.full[i] = Adegan(dict(sub.s), W, H, sub.start, sub.end, self.fps, self.film, self.idx)
                return self.full[i].render(t - tmu)
            im = sub.render(t - tmu)
            if q < 0.98:
                s = max(0.05, q)
                im = im.resize((max(2, int(pw * s)), max(2, int(ph * s))), Image.BILINEAR)
                px, py = int(x0 + pw / 2 - im.width / 2), int(y0 + ph / 2 - im.height / 2)
            else:
                px, py = int(x0), int(y0)
            page.paste(im, (px, py))
            d.rounded_rectangle([px, py, px + im.width, py + im.height], radius=6, outline=OUT, width=6)
        if zi is not None and zq > 0:
            x0, y0, pw, ph = self.rect[zi]
            fx0, fy0, fx1, fy1 = lerp(0, x0, zq), lerp(0, y0, zq), lerp(W, x0 + pw, zq), lerp(H, y0 + ph, zq)
            page = page.crop((int(fx0), int(fy0), int(fx1), int(fy1))).resize((W, H), Image.BICUBIC)
        return page

    def events(self):
        ev = []
        for tmu, sub in self.panels:
            ev.append((self.start + tmu, "pop", 0.9))
            ev += sub.events()
        return ev
