# -*- coding: utf-8 -*-
"""
galeri.py - lembar karakter 3D-stickman (Kribo utama, Prof. Habibie, Bos, ekspresi, pose).

  python3 galeri.py <keluar.png>            # lembar utama: Kribo, Prof. Habibie, Bos
  python3 galeri.py <keluar.png> --kribo    # uji 6 ekspresi closeup Kribo 3D
  python3 galeri.py <keluar.png> --semua    # semua ekspresi, pose, dan preset tokoh
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from engine3d import Scene3D, Cam3D, font
import tokoh as TK


def potret(spec, W, H, cam, bg=(236, 238, 242), aa=2.0, **st):
    sc = Scene3D()
    sc.set_sky(bg, tuple(max(0, c - 14) for c in bg), (0.68, 0.69, 0.72), (0.48, 0.46, 0.48),
               [0.62, 0.48, 0.62], [1.0, 0.99, 0.97], 0.48, bg)
    sc.tiled_plane(-3.0, -3.0, 3.0, 3.0, 0.0, tuple(max(0, c - 18) for c in bg), tile=1.5)
    sc.add_light((1.6, 2.2, 2.4), color=(255, 242, 224), intensity=0.20, radius=5.0)
    TK.TokohStick3D(spec).draw(sc, (0.0, 0.0, 0.0), TK.state(**st))
    return sc.render(cam, W, H, aa=aa)


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
        ("Kribo — Utama", "kribo", (64, 118, 124), (222, 236, 238), 0),
        ("Prof. Habibie", "habibie", (48, 72, 114), (228, 234, 244), 640),
        ("Bos — Formal", "bos", (48, 52, 64), (228, 232, 240), 1280),
    ]
    eks6 = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa"]
    poses = ["lambai", "tunjuk", "ide", "pidato"]

    for title, spec, col, light, ox in cols:
        d.rounded_rectangle([ox + 16, 16, ox + 624, H - 16], radius=24, fill=(255, 255, 255))
        pil(title, (ox + 320, 56), 34, (255, 255, 255), col, d)
        cam_p = Cam3D(pos=(0.25, 1.26, 3.15), target=(0.0, 0.90, 0.0), fov=40)
        im = potret(spec, 300, 380, cam_p, bg=light, pose="jempol", expr="senang", hadap="serong_kanan")
        sheet.paste(im, (ox + 28, 98))

        d.rounded_rectangle([ox + 340, 98, ox + 610, 478], radius=18, fill=light)
        pil("Ekspresi", (ox + 475, 126), 22, (40, 40, 58), (255, 255, 255), d)
        cam_e = Cam3D(pos=(0.10, 1.48, 1.78), target=(0.0, 1.42, 0.06), fov=36)
        for i, e in enumerate(eks6):
            ime = potret(spec, 122, 102, cam_e, bg=(252, 252, 254), expr=e, pose="diam")
            sheet.paste(ime, (ox + 350 + (i % 2) * 128, 152 + (i // 2) * 108))

        pil("Pose & Gestur 3D", (ox + 320, 514), 24, (40, 40, 58), light, d)
        cam_pose = Cam3D(pos=(0.40, 1.32, 3.30), target=(0.0, 0.96, 0.0), fov=40)
        for i, p in enumerate(poses):
            imp = potret(spec, 286, 224, cam_pose, bg=light, pose=p, expr="senang", hadap="serong_kanan", t=0.4)
            px = ox + 28 + (i % 2) * 296
            py = 548 + (i // 2) * 246
            sheet.paste(imp, (px, py))
            d.text((px + 143, py + 234), p, font=font("judul", 20), fill=(48, 52, 68), anchor="mm")

    sheet.save(out)
    print("GALERI", out)


def uji_kribo(out):
    W, H = 1920, 1140
    sheet = Image.new("RGB", (W, H), (248, 246, 240))
    d = ImageDraw.Draw(sheet)
    d.text((30, 18), "KRIBO 3D STICKMAN — UJI 12 EKSPRESI HALUS", font=font("judul", 36), fill=(40, 44, 60))
    eks = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa",
           "cinta", "pusing", "licik", "melet", "syok", "menangis"]
    cam = Cam3D(pos=(0.14, 1.50, 1.88), target=(0.0, 1.44, 0.06), fov=36)
    for i, e in enumerate(eks):
        x, y = 30 + (i % 4) * 470, 82 + (i // 4) * 350
        im = potret("kribo", 445, 320, cam, bg=(222, 236, 238), expr=e, pose="diam")
        sheet.paste(im, (x, y))
        pil(e, (x + 76, y + 286), 22, (255, 255, 255), (64, 118, 124), d)
    sheet.save(out)
    print("GALERI UJI KRIBO", out)


def uji_ekspresi(out):
    eks = list(TK.EKSPRESI)
    cols = 7
    rows = math.ceil(len(eks) / cols)
    W, H = 30 + cols * 270, 90 + rows * 250
    sheet = Image.new("RGB", (W, H), (248, 246, 240))
    d = ImageDraw.Draw(sheet)
    d.text((30, 22), f"KRIBO 3D STICKMAN — {len(eks)} EKSPRESI LENGKAP", font=font("judul", 34), fill=(40, 44, 60))
    cam = Cam3D(pos=(0.12, 1.50, 1.90), target=(0.0, 1.44, 0.06), fov=36)
    for i, e in enumerate(eks):
        x, y = 30 + (i % cols) * 270, 86 + (i // cols) * 250
        im = potret("kribo", 252, 232, cam, bg=(222, 236, 238), expr=e, pose="diam")
        sheet.paste(im, (x, y))
        pil(e, (x + 126, y + 210), 17, (255, 255, 255), (64, 118, 124), d)
    sheet.save(out)
    print("GALERI EKSPRESI", out, len(eks))


def sampingan(out):
    W, H = 1920, 880
    sheet = Image.new("RGB", (W, H), (244, 245, 248))
    d = ImageDraw.Draw(sheet)
    d.text((32, 20), "5 KARAKTER SAMPINGAN BEDA STYLE (3D STICKMAN)", font=font("judul", 36), fill=(36, 40, 56))
    cards = [
        ("Detektif Arya", "Noir / Fedora", "detektif", (68, 72, 86), (228, 230, 236), "mikir", "sinis", "serong_kanan"),
        ("Bang Teknik", "Konstruksi", "insinyur", (214, 108, 28), (244, 234, 222), "jempol", "bangga", "serong_kanan"),
        ("Zaki", "Punk / Jabrik", "zaki", (96, 56, 156), (234, 228, 246), "sorak", "melet", "serong_kiri"),
        ("Maya", "Reporter Modis", "maya", (204, 78, 104), (246, 230, 234), "lambai", "cinta", "serong_kanan"),
        ("Dodi", "Street / Topi", "dodi", (46, 100, 182), (226, 236, 248), "santai", "licik", "serong_kiri"),
    ]
    cw = 360
    cam_f = Cam3D(pos=(0.35, 1.24, 3.15), target=(0.0, 0.90, 0.0), fov=40)
    cam_c = Cam3D(pos=(0.14, 1.42, 1.58), target=(0.0, 1.36, 0.06), fov=36)
    for i, (nama, gaya, sp, col, bgc, pose, expr, hadap) in enumerate(cards):
        ox = 24 + i * 376
        d.rounded_rectangle([ox, 80, ox + cw, H - 24], radius=22, fill=(255, 255, 255))
        pil(nama, (ox + cw // 2, 118), 26, (255, 255, 255), col, d)
        d.text((ox + cw // 2, 154), gaya, font=font("teks", 20), fill=(90, 96, 112), anchor="mm")
        im_f = potret(sp, cw - 24, 410, cam_f, bg=bgc, pose=pose, expr=expr, hadap=hadap, t=0.4)
        sheet.paste(im_f, (ox + 12, 174))
        im_c = potret(sp, cw - 24, 230, cam_c, bg=(250, 251, 253), pose="diam", expr=expr, hadap="serong_kanan")
        sheet.paste(im_c, (ox + 12, 596))
        d.text((ox + cw // 2, 838), f"pose: {pose} | expr: {expr}", font=font("teks", 18), fill=(68, 74, 90), anchor="mm")
    sheet.save(out)
    print("GALERI SAMPINGAN", out)


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
    d.text((20, y), "EKSPRESI 3D-STICKMAN", font=font("judul", 34), fill=(40, 44, 60)); y += 50
    cam_e = Cam3D(pos=(0.12, 1.40, 1.52), target=(0.0, 1.35, 0.06), fov=36)
    for i, e in enumerate(names):
        im = potret("kribo", cell, cell - 60, cam_e, bg=(232, 238, 242), expr=e)
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 34), e, font=font("judul", 24), fill=(40, 44, 60), anchor="mm")
    y += rows_e * cell
    d.text((20, y), "POSE 3D-STICKMAN", font=font("judul", 34), fill=(40, 44, 60)); y += 50
    cam_p = Cam3D(pos=(0.40, 1.35, 3.20), target=(0.0, 0.94, 0.0), fov=40)
    for i, p in enumerate(poses):
        spec = "kribo" if i % 2 == 0 else "sari"
        im = potret(spec, cell, cell - 40, cam_p, bg=(236, 236, 240), pose=p, t=0.4, hadap="serong_kanan")
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 22), p, font=font("judul", 22), fill=(40, 44, 60), anchor="mm")
    y += rows_p * cell
    d.text((20, y), "TOKOH BAWAAN", font=font("judul", 34), fill=(40, 44, 60)); y += 50
    for i, p in enumerate(presets):
        im = potret(p, cell, cell - 40, cam_p, bg=(232, 238, 242), pose="diam", hadap="serong_kanan")
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 22), p, font=font("judul", 22), fill=(40, 44, 60), anchor="mm")
    sheet.save(out)
    print("GALERI", out, sheet.size)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out = args[0] if args else "galeri.png"
    if "--semua" in sys.argv:
        semua(out)
    elif "--sampingan" in sys.argv:
        sampingan(out)
    elif "--kribo" in sys.argv or "--uji-kribo" in sys.argv:
        uji_kribo(out)
    elif "--ekspresi" in sys.argv:
        uji_ekspresi(out)
    else:
        lembar(out)
