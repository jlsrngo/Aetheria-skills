# -*- coding: utf-8 -*-
"""
galeri.py - lembar karakter 3D VoxelVerse (Kribo, Arka + Robo, Nadia, ekspresi, pose) untuk QA atau preview.

  python3 galeri.py <keluar.png>            # lembar utama: Kribo, Arka+Robo, Nadia
  python3 galeri.py <keluar.png> --kribo    # uji 6 ekspresi closeup Kribo 3D
  python3 galeri.py <keluar.png> --semua    # semua ekspresi, pose, dan preset tokoh
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from voxel import Scene3D, Cam3D, font
import tokoh as TK


def potret(spec, W, H, cam, bg=(236, 238, 242), extra_robo=False, **st):
    sc = Scene3D()
    sc.set_sky(bg, tuple(max(0, c - 18) for c in bg), (0.48, 0.50, 0.54), (0.28, 0.28, 0.30), [0.45, 0.85, 0.55], [1.0, 0.96, 0.90], 0.52, bg)
    sc.tiled_plane(-3.0, -3.0, 3.0, 3.0, 0.0, tuple(max(0, c - 26) for c in bg), tile=1.5)
    sc.add_light((1.4, 2.2, 2.2), color=(255, 224, 170), intensity=0.55, radius=5.0)
    TK.TokohVoxel(spec).draw(sc, (0.0, 0.0, 0.0), TK.state(**st))
    if extra_robo:
        TK.TokohVoxel("robo").draw(sc, (0.76, 0.0, 0.15), TK.state(pose="lambai", hadap="serong_kiri", t=0.4))
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
    sheet = Image.new("RGB", (W, H), (246, 246, 248))
    d = ImageDraw.Draw(sheet)
    cols = [
        ("Kribo — Utama", "kribo", (64, 118, 124), (222, 236, 238), 0, False),
        ("Arka & Robo", "arka", (214, 108, 46), (244, 232, 220), 640, True),
        ("Nadia — Hijab", "nadia", (152, 118, 86), (242, 234, 224), 1280, False),
    ]
    eks6 = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa"]
    poses = ["lambai", "tunjuk", "peregangan", "duduk_ketik"]

    for title, spec, col, light, ox, has_robo in cols:
        d.rounded_rectangle([ox + 16, 16, ox + 624, H - 16], radius=24, fill=(255, 255, 255))
        pil(title, (ox + 320, 56), 34, (255, 255, 255), col, d)
        cam_p = Cam3D(pos=(0.35 if has_robo else 0.25, 1.35, 3.25), target=(0.25 if has_robo else 0.0, 0.95, 0.0), fov=40)
        im = potret(spec, 300, 380, cam_p, bg=light, extra_robo=has_robo, pose="jempol", expr="senang", hadap="serong_kanan")
        sheet.paste(im, (ox + 28, 98))

        d.rounded_rectangle([ox + 340, 98, ox + 610, 478], radius=18, fill=light)
        pil("Ekspresi", (ox + 475, 126), 22, (40, 40, 58), (255, 255, 255), d)
        cam_e = Cam3D(pos=(0.12, 1.48, 1.42), target=(0.0, 1.40, 0.10), fov=36)
        for i, e in enumerate(eks6):
            ime = potret(spec, 122, 102, cam_e, bg=(252, 252, 254), expr=e, pose="diam")
            sheet.paste(ime, (ox + 350 + (i % 2) * 128, 152 + (i // 2) * 108))

        pil("Pose & Gestur 3D", (ox + 320, 514), 24, (40, 40, 58), light, d)
        cam_pose = Cam3D(pos=(0.45, 1.32, 3.35), target=(0.0, 0.92, 0.0), fov=40)
        for i, p in enumerate(poses):
            imp = potret(spec, 286, 224, cam_pose, bg=light, pose=p, expr="senang", hadap="serong_kanan", t=0.4)
            px = ox + 28 + (i % 2) * 296
            py = 548 + (i // 2) * 246
            sheet.paste(imp, (px, py))
            d.text((px + 143, py + 234), p, font=font("judul", 20), fill=(48, 52, 68), anchor="mm")

    sheet.save(out)
    print("GALERI", out)


def uji_kribo(out):
    W, H = 1560, 960
    sheet = Image.new("RGB", (W, H), (248, 246, 240))
    d = ImageDraw.Draw(sheet)
    d.text((30, 18), "KRIBO 3D VOXEL — UJI 6 EKSPRESI", font=font("judul", 38), fill=(40, 44, 60))
    eks = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa"]
    cam = Cam3D(pos=(0.18, 1.48, 1.50), target=(0.0, 1.40, 0.08), fov=36)
    for i, e in enumerate(eks):
        x, y = 30 + (i % 3) * 510, 90 + (i // 3) * 425
        im = potret("kribo", 480, 385, cam, bg=(222, 236, 238), expr=e, pose="diam")
        sheet.paste(im, (x, y))
        pil(e, (x + 76, y + 348), 24, (255, 255, 255), (64, 118, 124), d)
    sheet.save(out)
    print("GALERI UJI KRIBO", out)


def semua(out):
    cols = 6
    names = list(TK.EKSPRESI)
    W = 1920
    cell = 300
    rows_e = math.ceil(len(names) / cols)
    poses = list(TK.POSE)
    rows_p = math.ceil(len(poses) / cols)
    presets = list(TK.PRESET)
    rows_c = math.ceil(len(presets) / cols)
    H = (rows_e + rows_p + rows_c) * cell + 140
    sheet = Image.new("RGB", (W, H), (248, 246, 240))
    d = ImageDraw.Draw(sheet)
    y = 20
    d.text((20, y), "EKSPRESI 3D", font=font("judul", 34), fill=(40, 44, 60)); y += 50
    cam_e = Cam3D(pos=(0.15, 1.48, 1.48), target=(0.0, 1.40, 0.08), fov=36)
    for i, e in enumerate(names):
        spec = "kribo" if i % 2 == 0 else "arka"
        im = potret(spec, cell, cell - 60, cam_e, bg=(232, 238, 242), expr=e)
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 34), e, font=font("judul", 24), fill=(40, 44, 60), anchor="mm")
    y += rows_e * cell
    d.text((20, y), "POSE 3D", font=font("judul", 34), fill=(40, 44, 60)); y += 50
    cam_p = Cam3D(pos=(0.45, 1.35, 3.25), target=(0.0, 0.92, 0.0), fov=40)
    for i, p in enumerate(poses):
        spec = "kribo" if i % 2 == 0 else "nadia"
        im = potret(spec, cell, cell - 40, cam_p, bg=(236, 236, 240), pose=p, t=0.4, hadap="serong_kanan")
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 22), p, font=font("judul", 22), fill=(40, 44, 60), anchor="mm")
    y += rows_p * cell
    d.text((20, y), "TOKOH BAWAAN", font=font("judul", 34), fill=(40, 44, 60)); y += 50
    for i, p in enumerate(presets):
        c_preset = Cam3D(pos=(0.35, 0.85, 2.2), target=(0.0, 0.55, 0.0), fov=40) if p in ("robo", "kucing") else cam_p
        im = potret(p, cell, cell - 40, c_preset, bg=(232, 238, 242), pose="diam", hadap="serong_kanan")
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 22), p, font=font("judul", 22), fill=(40, 44, 60), anchor="mm")
    sheet.save(out)
    print("GALERI", out, sheet.size)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "galeri.png"
    if "--semua" in sys.argv:
        semua(out)
    elif "--kribo" in sys.argv or "--uji-kribo" in sys.argv:
        uji_kribo(out)
    else:
        lembar(out)
