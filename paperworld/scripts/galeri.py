# -*- coding: utf-8 -*-
"""
galeri.py - lembar karakter 3D Pop-Up Paper Craft (Luna + Kucing, Kribo, Nadia) untuk QA atau preview.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from paper import ScenePaper, Cam3D, font
import tokoh as TK


def potret(spec, W, H, cam, bg=(242, 228, 206), extra_cat=False, **st):
    sc = ScenePaper()
    sc.set_sky(bg, tuple(max(0, c - 14) for c in bg), (0.64, 0.62, 0.58), (0.50, 0.46, 0.42), [-0.46, 0.82, 0.44], [1.0, 0.96, 0.88], 0.36, bg)
    sc.shadow_floor_y = 0.0
    sc.floor_shadow_col = tuple(int(c * 0.78) for c in bg)
    sc.tiled_plane(-3.5, -3.5, 3.5, 3.5, 0.0, tuple(max(0, c - 12) for c in bg), tile=1.5)
    TK.TokohKertas(spec).draw(sc, (0.0, 0.0, 0.0), TK.state(**st))
    if extra_cat:
        TK.TokohKertas("kucing").draw(sc, (0.68, 0.0, 0.15), TK.state(pose="lambai", hadap="serong_kiri", t=0.4))
    return sc.render(cam, W, H)


def pil(text, xy, size, fg, bgc, d):
    f = font("judul", size)
    b = d.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0], b[3] - b[1]
    pad = size * 0.45
    d.rounded_rectangle([xy[0] - w / 2 - pad, xy[1] - h / 2 - pad, xy[0] + w / 2 + pad, xy[1] + h / 2 + pad * 0.9], radius=size * 0.6, fill=bgc)
    d.text(xy, text, font=f, fill=fg, anchor="mm")


def lembar(out):
    W, H = 1920, 1080
    sheet = Image.new("RGB", (W, H), (244, 236, 222))
    d = ImageDraw.Draw(sheet)
    cols = [
        ("Luna & Kucing", "luna", (224, 94, 74), (248, 234, 218), 0, True),
        ("Kribo — Kertas", "kribo", (74, 134, 138), (226, 238, 234), 640, False),
        ("Nadia — Hijab", "nadia", (152, 118, 86), (242, 234, 224), 1280, False),
    ]
    eks6 = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa"]
    poses = ["lambai", "tunjuk", "peregangan", "jalan"]

    for title, spec, col, light, ox, has_cat in cols:
        d.rounded_rectangle([ox + 16, 16, ox + 624, H - 16], radius=24, fill=(255, 252, 246))
        pil(title, (ox + 320, 56), 34, (255, 255, 255), col, d)
        cam_p = Cam3D(pos=(0.35 if has_cat else 0.25, 1.25, 3.15), target=(0.25 if has_cat else 0.0, 0.85, 0.0), fov=40)
        im = potret(spec, 300, 380, cam_p, bg=light, extra_cat=has_cat, pose="jempol", expr="senang", hadap="serong_kanan")
        sheet.paste(im, (ox + 28, 98))

        d.rounded_rectangle([ox + 340, 98, ox + 610, 478], radius=18, fill=light)
        pil("Ekspresi", (ox + 475, 126), 22, (40, 40, 58), (255, 255, 255), d)
        cam_e = Cam3D(pos=(0.10, 1.32, 1.35), target=(0.0, 1.28, 0.05), fov=36)
        for i, e in enumerate(eks6):
            ime = potret(spec, 122, 102, cam_e, bg=(252, 248, 242), expr=e, pose="diam")
            sheet.paste(ime, (ox + 350 + (i % 2) * 128, 152 + (i // 2) * 108))

        pil("Pose Pop-Up 3D", (ox + 320, 514), 24, (40, 40, 58), light, d)
        cam_pose = Cam3D(pos=(0.45, 1.25, 3.15), target=(0.0, 0.85, 0.0), fov=40)
        for i, p in enumerate(poses):
            imp = potret(spec, 286, 224, cam_pose, bg=light, pose=p, expr="senang", hadap="serong_kanan", t=0.4, amp=1.0 if p == "jalan" else 0.0)
            px, py = ox + 28 + (i % 2) * 296, 548 + (i // 2) * 246
            sheet.paste(imp, (px, py))
            d.text((px + 143, py + 234), p, font=font("judul", 20), fill=(48, 52, 68), anchor="mm")

    sheet.save(out)
    print("GALERI", out)


def uji_kribo(out):
    W, H = 1560, 960
    sheet = Image.new("RGB", (W, H), (248, 244, 236))
    d = ImageDraw.Draw(sheet)
    d.text((30, 18), "KRIBO PAPER CRAFT — UJI 6 EKSPRESI", font=font("judul", 38), fill=(40, 44, 60))
    eks = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa"]
    cam = Cam3D(pos=(0.15, 1.32, 1.45), target=(0.0, 1.28, 0.04), fov=36)
    for i, e in enumerate(eks):
        x, y = 30 + (i % 3) * 510, 90 + (i // 3) * 425
        sheet.paste(potret("kribo", 480, 385, cam, bg=(226, 238, 234), expr=e, pose="diam"), (x, y))
        pil(e, (x + 76, y + 348), 24, (255, 255, 255), (74, 134, 138), d)
    sheet.save(out)
    print("GALERI UJI KRIBO", out)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "galeri.png"
    if "--kribo" in sys.argv or "--uji-kribo" in sys.argv:
        uji_kribo(out)
    else:
        lembar(out)
