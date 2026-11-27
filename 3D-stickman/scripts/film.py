# -*- coding: utf-8 -*-
"""
film.py - menyusun semua adegan 3D-stickman jadi film: jadwal, subtitle ("kata" 1-2 kata ala explainer pendek, komik, sinematik, pil), transisi, fade, panel komik.
"""
import math, os, sys, json
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine3d import OUT, PUTIH, KUNING, clamp, lerp, e_io, e_out, e_back, prog, font
import timing
from adegan import Adegan


class Film:
    def __init__(self, projdir, ss=1.5, ukuran=None):
        self.dir = projdir
        self.proj = json.load(open(os.path.join(projdir, "proyek.json"), encoding="utf-8"))
        W, H = ukuran or self.proj.get("ukuran", [1080, 1920])
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
        self.word_chunks = self._word_chunks()
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
    def _word_chunks(self):
        """Chunk 1-2 kata pendek di tengah bawah (gaya_subtitle='kata' ala video explainer vertikal)."""
        chunks = []
        for ws in self.words:
            i = 0
            while i < len(ws):
                w0 = ws[i]
                # Gabung maksimal 2 kata pendek jika keduanya <= 5 huruf dan tidak diakhiri tanda baca
                if i + 1 < len(ws) and len(w0[0]) <= 4 and len(ws[i + 1][0]) <= 5 and w0[0][-1:] not in ".?!,;":
                    w1 = ws[i + 1]
                    chunks.append((w0[1], w1[2], f"{w0[0]} {w1[0]}"))
                    i += 2
                else:
                    chunks.append((w0[1], w0[2], w0[0]))
                    i += 1
        out = []
        for idx, (s, e, txt) in enumerate(chunks):
            nxt_s = chunks[idx + 1][0] if idx + 1 < len(chunks) else e + 0.45
            end_t = min(nxt_s, e + 0.35)
            out.append((s, max(end_t, e + 0.06), txt))
        return out

    def _pages(self):
        pages = []
        for ws in self.words:
            cur = []
            for w in ws:
                cur.append(w)
                txt = " ".join(x[0] for x in cur)
                if len(cur) >= 6 or len(txt) > 30 or w[0][-1:] in ".?!" or (w[0][-1:] in ",;:" and len(txt) > 16):
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
        style = self.proj.get("gaya_subtitle", "kata")
        scale_ref = self.H / 1080.0 if self.W >= self.H else self.W / 1080.0

        if style == "kata":
            hit = None
            for a, b, txt in self.word_chunks:
                if a - 0.02 <= t < b:
                    hit = (a, b, txt)
                    break
            if hit is None:
                return img
            ov = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            pop = e_back(prog(t, hit[0], hit[0] + 0.11), 1.4)
            sz = max(24, int(92 * scale_ref * lerp(0.86, 1.0, clamp(pop))))
            f = font("judul", sz)
            yy = self.H * (0.83 if self.W < self.H else 0.87)
            d.text(
                (self.W * 0.5, yy), hit[2], font=f,
                fill=PUTIH + (255,),
                stroke_width=max(5, int(sz * 0.14)),
                stroke_fill=OUT + (255,),
                anchor="mm",
            )
            out = img.convert("RGBA")
            out.alpha_composite(ov)
            return out.convert("RGB")

        pg = None
        for a, b, p in self.pages:
            if a - 0.05 <= t < b:
                pg = p
                break
        if pg is None:
            return img

        ov = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        size = int((46 if style == "sinematik" else 56) * scale_ref)
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

        y0 = self.H * (0.885 if self.W >= self.H else 0.83) - (len(lines) - 1) * size * 0.62
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
                    d.text((x + l / 2, yy), w[0], font=f, fill=col, anchor="mm", stroke_width=max(4, int(size * 0.14)), stroke_fill=OUT + (255,))
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
            tr = {"jenis": "potong"} if same else {"jenis": "fade", "dur": 0.35}
        if isinstance(tr, str):
            tr = {"jenis": tr}
        d = dict(tr)
        d.setdefault("dur", 0.0 if d["jenis"] == "potong" else 0.40)
        return d

    def raw(self, T):
        i = self.scene_index(T)
        if i + 1 < len(self.scenes):
            tr = self.trans_of(i + 1)
            nxt = self.scenes[i + 1]
            if tr["dur"] > 0 and T >= nxt.start - tr["dur"] / 2:
                p = clamp((T - (nxt.start - tr["dur"] / 2)) / tr["dur"])
                A = self.scenes[i].render(T - self.scenes[i].start, self.level(T))
                B = nxt.render(T - nxt.start, self.level(T))
                return blend(A, B, p, tr)
        return self.scenes[i].render(T - self.scenes[i].start, self.level(T))

    def frame(self, f):
        T = f / self.fps
        img = self.raw(T)
        img = self.caption(img, T)
        fi = float(self.proj.get("fade_masuk", 0.35))
        fo = float(self.proj.get("fade_keluar", 0.6))
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
                tr = self.trans_of(i)
                k = tr["jenis"]
                if k in ("whip", "geser", "putar", "belah"):
                    ev.append((s.start - tr["dur"] / 2, "whoosh", 0.8))
                elif k == "iris":
                    ev.append((s.start - tr["dur"] / 2, "iris", 0.7))
                elif k in ("zoom", "kedip"):
                    ev.append((s.start - tr["dur"] / 2, "whoosh_lembut", 0.8))
                elif k == "flash":
                    ev.append((s.start - 0.02, "kilat", 0.85))
        return sorted(ev)


def blend(A, B, p, tr):
    k = tr["jenis"]
    W, H = A.size
    e = e_io(p)
    if k == "fade":
        return Image.blend(A, B, e)
    if k == "flash":
        if p < 0.5:
            return Image.blend(A, Image.new("RGB", A.size, PUTIH), e_out(p * 2))
        return Image.blend(Image.new("RGB", A.size, PUTIH), B, e_io((p - 0.5) * 2))
    if k == "kedip":
        im = A.copy() if p < 0.5 else B.copy()
        q = e_io(p * 2) if p < 0.5 else 1.0 - e_io((p - 0.5) * 2)
        d = ImageDraw.Draw(im)
        h = int(H * 0.5 * q)
        d.rectangle([0, 0, W, h], fill=(16, 18, 26))
        d.rectangle([0, H - h, W, H], fill=(16, 18, 26))
        return im
    if k == "iris":
        cx, cy = tr.get("x", 0.5) * W, tr.get("y", 0.5) * H
        R = math.hypot(max(cx, W - cx), max(cy, H - cy)) * e
        mask = Image.new("L", A.size, 0)
        ImageDraw.Draw(mask).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
        out = Image.composite(B, A, mask)
        if 0.02 < p < 0.98:
            ImageDraw.Draw(out).ellipse([cx - R, cy - R, cx + R, cy + R], outline=OUT, width=8)
        return out
    if k in ("geser", "whip"):
        arah = tr.get("arah", "kiri")
        dx, dy = {"kiri": (-1, 0), "kanan": (1, 0), "atas": (0, -1), "bawah": (0, 1)}.get(arah, (-1, 0))
        ox, oy = int(-dx * W * e), int(-dy * H * e)
        canvas = Image.new("RGB", A.size)
        canvas.paste(A, (ox, oy))
        canvas.paste(B, (ox + dx * W, oy + dy * H))
        if k == "whip":
            r = max(1, int(math.sin(math.pi * p) * 10))
            canvas = canvas.filter(ImageFilter.GaussianBlur(r))
        return canvas
    if k == "zoom":
        s_out = 1.0 + 0.75 * e
        a = A.resize((int(W * s_out), int(H * s_out)), Image.BILINEAR)
        a = a.crop(((a.width - W) // 2, (a.height - H) // 2, (a.width + W) // 2, (a.height + H) // 2))
        return Image.blend(a, B, e)
    if k == "wipe":
        x = int(W * e)
        out = A.copy()
        out.paste(B.crop((0, 0, x, H)), (0, 0))
        ImageDraw.Draw(out).line([(x, 0), (x, H)], fill=OUT, width=6)
        return out
    if k == "putar":
        # Spin whip cepat dengan blur di tengah transisi
        ang = (180.0 * e) if p < 0.5 else (-180.0 * (1.0 - e))
        src = A if p < 0.5 else B
        rot = src.rotate(ang, resample=Image.BICUBIC)
        r = max(1, int(math.sin(math.pi * p) * 12))
        return rot.filter(ImageFilter.GaussianBlur(r))
    if k == "belah":
        # Split curtain: layar lama terbelah ke kiri & kanan membuka adegan baru
        out = B.copy()
        half = W // 2
        dx = int(half * e)
        if dx < half:
            left_part = A.crop((0, 0, half, H))
            right_part = A.crop((half, 0, W, H))
            out.paste(left_part, (-dx, 0))
            out.paste(right_part, (half + dx, 0))
            d = ImageDraw.Draw(out)
            d.line([(half - dx, 0), (half - dx, H)], fill=OUT, width=6)
            d.line([(half + dx, 0), (half + dx, H)], fill=OUT, width=6)
        return out
    return B if p >= 0.5 else A


class Komik:
    """Halaman panel komik 3D-stickman."""

    def __init__(self, spec, W, H, start, end, fps, film, idx):
        self.s = spec
        self.W, self.H = W, H
        self.start, self.end = start, end
        self.dur = max(0.2, end - start)
        self.fps, self.film, self.idx = fps, film, idx
        self.warn = []
        cols, rows = spec.get("grid", [2, 2])
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

    def render(self, t, level=0.0):
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
                return self.full[i].render(t - tmu, level)
            im = sub.render(t - tmu, level)
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
