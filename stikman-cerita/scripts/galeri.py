# -*- coding: utf-8 -*-
"""
galeri.py - lembar karakter (ekspresi + pose + semua preset) untuk QA atau ditunjukkan ke user.

  python3 galeri.py <keluar.png>            # lembar Pria + Wanita seperti referensi gaya
  python3 galeri.py <keluar.png> --semua    # semua ekspresi, pose, dan preset tokoh
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from stik import *
import tokoh as TK


def potret(spec, W, H, cam, bg=(255, 255, 255, 0), ss=2, **st):
    c = Canvas(W, H, ss, cam, 1.0)
    c.fill(bg[:3] if len(bg) == 4 else bg)
    TK.Tokoh(spec).draw(c, TK.state(**st))
    return c.finish()


def pil(im, text, xy, size, fg, bgc, d):
    f = font("judul", size)
    b = d.textbbox((0, 0), text, font=f)
    w, h = b[2] - b[0], b[3] - b[1]
    pad = size * .45
    d.rounded_rectangle([xy[0] - w / 2 - pad, xy[1] - h / 2 - pad, xy[0] + w / 2 + pad, xy[1] + h / 2 + pad * .9], radius=size * .6, fill=bgc)
    d.text(xy, text, font=f, fill=fg, anchor="mm")


def lembar(out):
    W, H = 1920, 1080
    sheet = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    # kribo jadi tokoh utama di galeri default; kamera wajah disesuaikan dengan afro besar
    cols = [("Tokoh Utama — Kribo", "kribo", (84, 124, 128), (226, 238, 238), 0, Cam(0, -384, 0.40)),
            ("Karakter Wanita", "nadia", (230, 80, 130), (255, 232, 240), 960, Cam(0, -320, 0.82))]
    eks6 = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa"]
    poses = ["lambai", "tunjuk", "silang", "ide", "jalan"]
    for title, spec, col, light, ox, cam_eks in cols:
        d.ellipse([ox + 30, 90, ox + 400, 460], fill=light)
        cam_main = Cam(0, -264, 0.80) if spec == "kribo" else Cam(0, -230, 1.0)
        im = potret(spec, 420, 520, cam_main, pose="jempol", expr="senang")
        sheet.paste(im, (ox + 10, 40))
        pil(None, title, (ox + 560, 60), 46, (255, 255, 255), col, d)
        d.rounded_rectangle([ox + 400, 120, ox + 930, 540], radius=26, fill=light)
        pil(None, "Ekspresi Wajah", (ox + 665, 150), 26, (40, 40, 60), (255, 255, 255), d)
        for i, e in enumerate(eks6):
            im = potret(spec, 160, 150, cam_eks, expr=e, pose="diam")
            sheet.paste(im, (ox + 420 + (i % 3) * 165, 190 + (i // 3) * 170))
        pil(None, "Pose & Gestur", (ox + 480, 600), 26, (40, 40, 60), light, d)
        cam_pose = Cam(10, -266, 0.40) if spec == "kribo" else Cam(0, -230, 0.48)
        for i, p in enumerate(poses):
            im = potret(spec, 184, 390, cam_pose, pose=p, expr="senang" if p != "silang" else "tenang", t=0.3, amp=1.0 if p == "jalan" else 0, phase=0.9)
            sheet.paste(im, (ox + 12 + i * 185, 640))
    sheet.save(out)
    print("GALERI", out)


def uji_kribo(out):
    """Lembar QC khusus: kribo dalam 6 ekspresi yang paling sering dipakai."""
    W, H = 1560, 960
    sheet = Image.new("RGB", (W, H), (250, 248, 242))
    d = ImageDraw.Draw(sheet)
    d.text((30, 16), "KRIBO — UJI 6 EKSPRESI (rig prosedural)", font=font("judul", 40), fill=(40, 40, 60))
    eks = ["senang", "marah", "kaget", "sedih", "mikir", "tertawa"]
    for i, e in enumerate(eks):
        x, y = 30 + (i % 3) * 510, 92 + (i // 3) * 430
        d.rounded_rectangle([x, y, x + 480, y + 388], radius=28, fill=(226, 238, 238))
        im = potret("kribo", 480, 388, Cam(0, -268, 0.65), expr=e, pose="diam", blink=0.0)
        sheet.paste(im, (x, y))
        pil(None, e, (x + 70, y + 352), 26, (255, 255, 255), (84, 124, 128), d)
    d.text((30, H - 32), "Cek: afro tidak menutup kacamata/alis, dasi kupu pas di bawah dagu, lengan & sneaker berwarna sesuai preset.",
           font=font("teks", 22), fill=(90, 90, 110))
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
    H = (rows_e + rows_p + rows_c) * cell + 120
    sheet = Image.new("RGB", (W, H), (250, 248, 242))
    d = ImageDraw.Draw(sheet)
    y = 20
    d.text((20, y), "EKSPRESI", font=font("judul", 34), fill=(40, 40, 60)); y += 50
    for i, e in enumerate(names):
        spec = "kribo" if i % 2 == 0 else "nadia"
        cam_e = Cam(0, -378, 0.62) if spec == "kribo" else Cam(0, -320, 1.1)
        im = potret(spec, cell, cell - 70, cam_e, expr=e)
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 36), e, font=font("judul", 26), fill=(40, 40, 60), anchor="mm")
    y += rows_e * cell
    d.text((20, y), "POSE", font=font("judul", 34), fill=(40, 40, 60)); y += 50
    for i, p in enumerate(poses):
        spec = "kribo" if i % 2 == 0 else "nadia"
        cam_p = Cam(0, -264, 0.42) if spec == "kribo" else Cam(0, -215, 0.62)
        im = potret(spec, cell, cell - 30, cam_p, pose=p, t=0.3, amp=1.0 if "jalan" in p or "lari" in p else 0, phase=0.9,
                    expr="senang", y=-0)
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 20), p, font=font("judul", 24), fill=(40, 40, 60), anchor="mm")
    y += rows_p * cell
    d.text((20, y), "TOKOH BAWAAN", font=font("judul", 34), fill=(40, 40, 60)); y += 50
    for i, p in enumerate(presets):
        cam_c = Cam(0, -264, 0.42) if p == "kribo" else Cam(0, -215, 0.62)
        im = potret(p, cell, cell - 30, cam_c, pose="diam")
        sheet.paste(im, ((i % cols) * 320, y + (i // cols) * cell))
        d.text(((i % cols) * 320 + 150, y + (i // cols) * cell + cell - 20), p, font=font("judul", 24), fill=(40, 40, 60), anchor="mm")
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
