# -*- coding: utf-8 -*-
"""
tokoh.py - rig tokoh: kepala besar chibi, badan kecil, gambar penuh lewat Python/Pillow.

Satuan lokal (skala 1): kaki di y=0, tinggi total ±470, jari-jari kepala 100.
Gaya bawaan tetap: kepala tebal-bergaris, mata oval hitam, mulut D merah, seragam SMP,
tangan bulatan, sepatu hitam. Preset utama "kribo" memakai rambut afro, kacamata kotak,
kaos teal + dasi kupu-kupu, lengan berisi kulit, dan sneaker hitam-putih.
Semua varian memakai rig prosedural yang sama (lipsync/kedip/ekspresi/pose tidak berubah).
"""
import math
from stik import *
import benda

HEAD_R = 96.0
HEAD_Y = -352.0          # pusat kepala (berdiri, proporsi chibi Ghibli hangat)
SHOULDER_Y = -254.0
HIP_Y = -142.0
SIT_DROP = 64.0
UP_ARM = 56.0
FORE_ARM = 52.0
SHOULDER_X = 40.0

# ------------------------------------------------------------------ casting
# Semua field opsional. Semua karakter manusia & maskot memakai bahasa visual & proporsi tubuh
# seragam bergaya Kribo (chibi anime wajah berkarakter, kulit hangat, lengan tebal, celana/kaki bervolume, sepatu chunky 3/4).
_BODY_KRIBO = dict(
    outline_hangat=True, lengan_tebal=True, sepatu_chunky=True,
    badan_lebar=1.56, pinggul_lebar=1.68, bahu_x=52.0, lengan_besar=1.28,
    hip_y=-146.0, kaki_tebal=2.35, kaki_lebar=1.24, sepatu_besar=1.34, tangan_besar=0.92,
)
_BODY_KRIBO_ROK = dict(
    outline_hangat=True, lengan_tebal=True, sepatu_chunky=True,
    badan_lebar=1.52, pinggul_lebar=1.64, bahu_x=51.0, lengan_besar=1.22,
    hip_y=-146.0, kaki_tebal=2.05, kaki_lebar=1.22, sepatu_besar=1.28, tangan_besar=0.90,
)

PRESET = {
    "kribo":  dict(_BODY_KRIBO, nama="Kribo", rambut="kribo_chibi", rambut_warna=(24, 20, 22), kulit=(254, 232, 214),
                   kacamata="pintar_kotak", wajah_chibi_ref=True, bentuk_wajah="tirus", gaya_mata="fokus",
                   gaya_mulut="senyum_hangat", telinga=True,
                   iris=(24, 24, 28), kaos_chibi=True,
                   kemeja=(44, 46, 52), krah=False, kancing=False,
                   dasi=(68, 138, 144), dasi_kupu=True, lengan_panjang=False,
                   celana_jogger=True, strip_jogger=True, tangan_saku=True,
                   bawah="celana", bawah_warna=(164, 168, 174), sepatu=(42, 44, 50)),
    "raka":   dict(_BODY_KRIBO, nama="Raka", rambut="jambul", rambut_warna=(32, 28, 34), kulit=(252, 224, 200),
                   wajah_chibi_ref=True, bentuk_wajah="tirus", gaya_mata="ghibli_bulat",
                   gaya_mulut="ceria_lebar", telinga=True, iris=(46, 36, 32),
                   kemeja=(248, 248, 250), rompi=True, rompi_warna=(78, 112, 152), krah=True, kancing=False, dasi=(52, 118, 208),
                   lengan_panjang=False, celana_jogger=True, tangan_saku=True,
                   bawah="celana", bawah_warna=(86, 102, 128), sepatu=(216, 220, 228)),
    "nadia":  dict(_BODY_KRIBO_ROK, nama="Nadia", hijab=(226, 180, 174), hijab_tua=(182, 132, 128), hijab_gaya="modern",
                   hijab_model="pashmina", kulit=(254, 228, 206), kacamata="bulat", wajah_chibi_ref=True,
                   bentuk_wajah="oval", gaya_mata="chibi_hijab", gaya_mulut="senyum_kecil",
                   bulu_mata=True, iris=(82, 50, 34), bahu_x=44.0,
                   tunik_chibi=True, kemeja=(236, 152, 86), krah=False, kancing=False, dasi=None,
                   lengan_panjang=True, rok_panjang=True, bawah="rok", bawah_warna=(122, 82, 58), sepatu=(104, 68, 48), sepatu_gaya="chibi_bulat"),
    "hana":   dict(_BODY_KRIBO, nama="Hana", rambut="panjang_naa", rambut_warna=(92, 68, 52), kulit=(254, 230, 210),
                   wajah_chibi_ref=True, bentuk_wajah="oval", gaya_mata="ghibli_lembut",
                   gaya_mulut="senyum_hangat", tahi_lalat=True, telinga=True, iris=(48, 138, 132), bulu_mata=True,
                   kemeja=(114, 138, 162), kemeja_dalam=(56, 64, 74), coat_naa=True, turtleneck=True,
                   krah=False, kancing=False, dasi=None, lengan_panjang=True, celana_jogger=True,
                   bawah="celana", bawah_warna=(122, 140, 162), sepatu=(128, 86, 62), sepatu_gaya="loafer"),
    "arka":   dict(_BODY_KRIBO, nama="Arka", rambut="comma", rambut_warna=(48, 52, 68), kulit=(252, 226, 208),
                   kacamata="browline", wajah_chibi_ref=True, bentuk_wajah="lonjong", gaya_mata="kalem",
                   gaya_mulut="smirk", telinga=True, iris=(64, 72, 96),
                   kemeja=(198, 224, 246), krah=True, kancing=False, saku_dada=True,
                   dasi=(48, 52, 66), dasi_klip=True, sabuk=(72, 62, 66), lengan_gulung=True,
                   lengan_panjang=False, celana_jogger=True, tangan_saku=True,
                   bawah="celana", bawah_warna=(104, 110, 124), sepatu=(96, 70, 54)),
    "bimo":   dict(_BODY_KRIBO, nama="Bimo", rambut="keriting", rambut_warna=(64, 42, 34), kulit=(242, 206, 178),
                   wajah_chibi_ref=True, bentuk_wajah="bulat_chibi", gaya_mata="ghibli_bulat",
                   gaya_mulut="ceria_lebar", freckles=True, telinga=True, iris=(62, 38, 28),
                   sweater=True, kemeja=(228, 132, 68), krah=False, kancing=False, dasi=None,
                   lengan_panjang=True, celana_jogger=True,
                   bawah="celana", bawah_warna=(176, 152, 116), sepatu=(152, 64, 64)),
    "dimas":  dict(_BODY_KRIBO, nama="Dimas", rambut="belah_samping", rambut_warna=(32, 30, 38), kulit=(252, 228, 210),
                   kacamata="pintar_kotak", wajah_chibi_ref=True, bentuk_wajah="oval", gaya_mata="fokus",
                   gaya_mulut="senyum_kecil", telinga=True, iris=(36, 44, 58),
                   kemeja=(246, 248, 250), rompi=True, rompi_warna=(116, 154, 128), krah=True, kancing=False, dasi=(56, 114, 198),
                   lengan_panjang=False, celana_jogger=True, tangan_saku=True,
                   bawah="celana", bawah_warna=(92, 98, 112), sepatu=(62, 82, 118)),
    "sari":   dict(_BODY_KRIBO_ROK, nama="Sari", hijab=(246, 248, 252), hijab_tua=(196, 204, 218), hijab_gaya="modern",
                   hijab_model="bergo", kulit=(254, 228, 206), wajah_chibi_ref=True, bentuk_wajah="bulat_chibi",
                   gaya_mata="chibi_hijab", gaya_mulut="senyum_kucing", bulu_mata=True, iris=(64, 46, 38), bahu_x=44.0,
                   tunik_chibi=True, kemeja=(246, 248, 252), krah=False, dasi=(208, 62, 62), lengan_panjang=True,
                   rok_panjang=True, bawah="rok", bawah_warna=(58, 70, 98), sepatu=(68, 62, 72), sepatu_gaya="chibi_bulat"),
    "tika":   dict(_BODY_KRIBO_ROK, nama="Tika", rambut="kuncir", rambut_warna=(38, 30, 34), kulit=(252, 228, 206),
                   wajah_chibi_ref=True, bentuk_wajah="bulat_chibi", gaya_mata="ghibli_bulat",
                   gaya_mulut="senyum_kucing", telinga=True, bulu_mata=True, iris=(72, 46, 36),
                   kemeja=(250, 246, 238), rompi=True, rompi_warna=(198, 108, 114), krah=True, dasi=(212, 66, 68), lengan_panjang=False,
                   bawah="rok", bawah_warna=(122, 64, 76), sepatu=(102, 68, 58), sepatu_gaya="maryjane"),
    "ayah":   dict(_BODY_KRIBO, nama="Ayah", rambut="sisir_belakang", rambut_warna=(64, 62, 70), kulit=(242, 210, 184),
                   wajah_chibi_ref=True, bentuk_wajah="lonjong", gaya_mata="ghibli_dewasa",
                   gaya_mulut="dewasa_ramah", telinga=True, iris=(42, 38, 38), kumis=True,
                   kemeja=(192, 218, 244), krah=True, kancing=True, saku_dada=True, dasi=None,
                   lengan_panjang=False, celana_jogger=True, tangan_saku=True,
                   bawah="celana", bawah_warna=(126, 134, 112), sepatu=(116, 80, 56), sepatu_gaya="loafer", skala=1.06),
    "ibu":    dict(_BODY_KRIBO_ROK, nama="Ibu", hijab=(134, 184, 152), hijab_tua=(88, 138, 108), hijab_gaya="modern",
                   hijab_model="syari", kulit=(248, 220, 196), wajah_chibi_ref=True, bentuk_wajah="oval",
                   gaya_mata="ghibli_lembut", gaya_mulut="senyum_kecil", bulu_mata=True, iris=(68, 48, 38), bahu_x=44.0,
                   tunik_chibi=True, kemeja=(244, 214, 168), krah=False, dasi=None, lengan_panjang=True,
                   rok_panjang=True, bawah="rok", bawah_warna=(126, 92, 70), sepatu=(108, 76, 56), sepatu_gaya="chibi_bulat", skala=1.02),
    "guru":   dict(_BODY_KRIBO, nama="Pak Guru", rambut="uban", rambut_warna=(196, 198, 208), kulit=(246, 216, 192),
                   kacamata="pintar_kotak", wajah_chibi_ref=True, bentuk_wajah="kotak", gaya_mata="ghibli_dewasa",
                   gaya_mulut="dewasa_ramah", kerut_mata=True, telinga=True, iris=(46, 44, 48), kumis=True,
                   kemeja=(244, 240, 228), rompi=True, rompi_warna=(164, 144, 116), krah=True, dasi=MERAH_TUA,
                   lengan_panjang=True, celana_jogger=True,
                   bawah="celana", bawah_warna=(104, 92, 82), sepatu=(86, 62, 48), sepatu_gaya="loafer", skala=1.05),
    "bu_guru": dict(_BODY_KRIBO_ROK, nama="Bu Guru", hijab=(182, 152, 214), hijab_tua=(136, 106, 174), hijab_gaya="modern",
                    hijab_model="segiempat", kulit=(250, 222, 198), kacamata="bulat", wajah_chibi_ref=True,
                    bentuk_wajah="lonjong", gaya_mata="kalem", gaya_mulut="senyum_hangat",
                    bulu_mata=True, iris=(72, 50, 66), bahu_x=44.0,
                    tunik_chibi=True, kemeja=(232, 220, 246), krah=False, dasi=None, lengan_panjang=True,
                    rok_panjang=True, bawah="rok", bawah_warna=(104, 80, 134), sepatu=(84, 64, 102), sepatu_gaya="chibi_bulat", skala=1.02),
    "kakek":  dict(_BODY_KRIBO, nama="Kakek", rambut="botak", peci=True, kulit=(242, 212, 188),
                   wajah_chibi_ref=True, bentuk_wajah="kotak", gaya_mata="ramah_sipit",
                   gaya_mulut="dewasa_ramah", kerut_mata=True, telinga=True, iris=(48, 44, 44), kumis=True, jenggot=True, uban=True,
                   kemeja=(246, 242, 232), koko=True, krah=False, kancing=True, dasi=None,
                   lengan_panjang=True, celana_jogger=True,
                   bawah="celana", bawah_warna=(146, 124, 100), sepatu=(106, 78, 56), sepatu_gaya="loafer", skala=0.98),
    "adik":   dict(_BODY_KRIBO, nama="Adik", rambut="ghibli_kuncir", rambut_warna=(30, 28, 30), kulit=(254, 224, 198),
                   wajah_chibi_ref=True, bentuk_wajah="bulat_chibi", gaya_mata="ghibli_bulat",
                   gaya_mulut="mungil_o", freckles=True, telinga=True, bulu_mata=False, iris=(58, 36, 28),
                   anak_ghibli=True, head_scale=1.15,
                   badan_lebar=1.84, pinggul_lebar=1.88, bahu_x=58.0, lengan_besar=1.48,
                   hip_y=-114.0, kaki_lebar=1.34, sepatu_besar=1.24, tangan_besar=0.84,
                   sweater=True, kemeja=(248, 214, 72), krah=False, kancing=False, dasi=None, lengan_panjang=True,
                   celana_jogger=True, bawah="celana", bawah_warna=(132, 134, 140), sepatu=(92, 62, 50), sepatu_gaya="loafer", skala=0.90),
    "otak":   dict(_BODY_KRIBO, nama="Sang Otak", maskot=True, bentuk_maskot="otak", kepala="otak",
                   kulit=(248, 174, 178), lengan_warna=(240, 152, 158), sepatu=(232, 132, 138), sol_warna=(248, 248, 250),
                   aksen=(248, 248, 250), iris=(58, 128, 178), headphone=False, bulu_mata=False, gaya_mulut="senyum_hangat", skala=0.98),
    "virus":  dict(_BODY_KRIBO, nama="Virus", maskot=True, bentuk_maskot="virus", kepala="virus",
                   kulit=(136, 198, 56), lengan_warna=(112, 172, 46), sepatu=(102, 152, 46), sol_warna=(248, 248, 246),
                   aksen=(168, 220, 86), bulu_mata=False, gaya_mulut="smirk", skala=0.94),
    "sel_imun": dict(_BODY_KRIBO, nama="Sel Imun", maskot=True, bentuk_maskot="sel_imun", kepala="sel_imun",
                     kulit=(244, 246, 238), lengan_warna=(132, 182, 212), sepatu=(86, 144, 188), sol_warna=(248, 248, 250),
                     aksen=(226, 174, 84), iris=(56, 124, 174), bulu_mata=False, gaya_mulut="ceria_lebar", skala=0.96),
    "bos":    dict(_BODY_KRIBO, nama="Bos", rambut="botak", telinga=True, kacamata="bulat",
                   wajah_chibi_ref=True, bentuk_wajah="kotak", gaya_mata="kalem",
                   gaya_mulut="smirk", iris=(38, 40, 48),
                   kulit=(248, 220, 198), kemeja=(54, 58, 72), kemeja_dalam=PUTIH, blazer=True, dasi=MERAH,
                   lengan_panjang=True, celana_jogger=True,
                   bawah="celana", bawah_warna=(58, 62, 74), sepatu=(46, 48, 56), skala=1.04),
}
PRESET["formal"] = dict(PRESET["bos"], nama="Formal", rambut="klimis", rambut_warna=(38, 42, 54),
                        bentuk_wajah="lonjong", gaya_mata="ghibli_dewasa", gaya_mulut="dewasa_ramah",
                        kemeja=(58, 70, 96),
                        bawah_warna=(56, 70, 98), sepatu=(96, 68, 52), sepatu_gaya="loafer")


ALIAS_PRESET = {"imun": "sel_imun", "sel_darah_putih": "sel_imun", "brain": "otak"}


def casting(spec):
    """spec = nama preset (str) atau dict {'dasar': 'kribo', ...override}. Default = kribo."""
    if isinstance(spec, str):
        spec = {"dasar": spec}
    nm = spec.get("dasar", "kribo")
    nm = ALIAS_PRESET.get(nm, nm)
    base = dict(PRESET.get(nm, PRESET["kribo"]))
    base.update({k: (tuple(v) if isinstance(v, list) and len(v) == 3 and all(isinstance(i, int) for i in v) else v)
                 for k, v in spec.items() if k != "dasar"})
    base.setdefault("skala", 1.0)
    for k, v in _BODY_KRIBO.items():
        base.setdefault(k, v)
    return base


WARNA = {"putih": PUTIH, "hitam": HITAM, "merah": MERAH, "biru": BIRU, "biru_tua": BIRU_TUA, "pink": PINK, "kuning": KUNING,
         "hijau": HIJAU, "ungu": UNGU, "oranye": ORANYE, "coklat": COKLAT, "abu": ABU, "navy": NAVY, "krem": KRIM,
         "biru_muda": BIRU_MUDA, "pink_muda": PINK_MUDA, "hijau_muda": HIJAU_MUDA, "merah_tua": MERAH_TUA}


def warna(v, default=None):
    if v is None:
        return default
    if isinstance(v, str):
        return WARNA.get(v, default)
    return tuple(v)


# ------------------------------------------------------------------ ekspresi
# eyes: oval arc_up arc_dn half wide spark wink dot | mouth: open smile o frown flat wave smirk grin pout yawn
EKSPRESI = {
    "senang":   dict(eyes="oval", mouth="open", open=0.62, blush=0.55),
    "tenang":   dict(eyes="oval", mouth="smile", blush=0.35),
    "tertawa":  dict(eyes="arc_up", mouth="grin", open=1.0, blush=0.9),
    "kaget":    dict(eyes="wide", mouth="o", brow=(14, 0, 0), blush=0.0),
    "marah":    dict(eyes="oval", mouth="gigit", brow=(-4, -1.0, -1.0), blush=0.0, vein=True, small=0.9),
    "mikir":    dict(eyes="oval", mouth="flat_miring", brow=(0, 0.2, 1.2), blush=0.0, look=(0.35, -0.5)),
    "sedih":    dict(eyes="oval", mouth="frown", brow=(0, 0.9, 0.9), blush=0.0, tear=True, hl=1.3),
    "malu":     dict(eyes="arc_up", mouth="wave", blush=1.0, sweat=True, small=0.8),
    "ngantuk":  dict(eyes="half", mouth="flat", blush=0.0),
    "menguap":  dict(eyes="arc_dn", mouth="yawn", blush=0.0),
    "tidur":    dict(eyes="arc_dn", mouth="smile", blush=0.4),
    "semangat": dict(eyes="spark", mouth="grin", open=0.9, blush=0.8),
    "panik":    dict(eyes="dot", mouth="wave_o", brow=(8, 0.8, 0.8), blush=0.0, sweat=True),
    "bangga":   dict(eyes="half", mouth="smirk", blush=0.4, brow=(0, -0.3, -0.3)),
    "jahil":    dict(eyes="wink", mouth="smirk", blush=0.5),
    "cemberut": dict(eyes="oval", mouth="pout", blush=0.9, brow=(-2, -0.5, -0.5)),
    "cemas":    dict(eyes="oval", mouth="wave", brow=(2, 0.9, 0.9), blush=0.0, sweat=True),
    "lega":     dict(eyes="arc_dn", mouth="open", open=0.35, blush=0.5, sweat=True),
    "terpana":  dict(eyes="spark", mouth="o", brow=(10, 0, 0), blush=0.6),
    "datar":    dict(eyes="dot", mouth="flat", blush=0.0),
}
ALIAS_EKS = {"senyum": "tenang", "kecewa": "sedih", "bingung": "mikir", "gembira": "senang", "ketawa": "tertawa",
             "heran": "kaget", "kesal": "cemberut", "takut": "panik", "ngakak": "tertawa", "ceria": "senang"}


def eks(name):
    name = ALIAS_EKS.get(name, name)
    return EKSPRESI.get(name, EKSPRESI["senang"])


# ------------------------------------------------------------------ pose
# lengan: (a, e, tangan) a=bahu (0 turun,90 samping,180 atas) e=siku (+ terus keluar/atas, - melipat). tangan: m p t f
def _P(L, R, **k):
    d = dict(L=L, R=R, legs="stand", sit=0.0, lean=0.0, tilt=0.0)
    d.update(k)
    return d


POSE = {
    "diam":        _P((8, -8, "m"), (8, -8, "m")),
    "santai":      _P((6, -10, "m"), (6, -10, "m")),
    "lambai":      _P((14, 10, "m"), (116, 18, "m"), wave="R"),
    "lambai2":     _P((116, 18, "m"), (116, 18, "m"), wave="LR"),
    "tunjuk":      _P((26, -80, "m"), (84, -6, "p"), tilt=-2),
    "tunjuk_kiri": _P((84, -6, "p"), (26, -80, "m"), tilt=2),
    "tunjuk_atas": _P((26, -86, "m"), (124, 26, "p")),
    "ide":         _P((26, -86, "m"), (122, 26, "p"), tilt=-3),
    "pinggang":    _P((46, -112, "m"), (46, -112, "m")),
    "jempol":      _P((46, -112, "m"), (92, 46, "t")),
    "silang":      _P((28, -128, "m"), (28, -128, "m")),
    "sorak":       _P((132, 18, "m"), (132, 18, "m"), lean=-3),
    "peregangan":  _P((138, 14, "m"), (138, 14, "m"), lean=-5, tilt=-4),
    "garuk":       _P((164, 36, "m"), (14, 10, "m"), tilt=6),
    "mikir":       _P((24, -150, "m"), (50, -150, "m"), tilt=-6),
    "dagu":        _P((14, 10, "m"), (56, -158, "m"), tilt=7),
    "kaget":       _P((100, 24, "m"), (100, 24, "m"), lean=-5),
    "sedih":       _P((6, 4, "m"), (6, 4, "m"), lean=3, tilt=8),
    "pusing":      _P((128, 88, "m"), (128, 88, "m"), lean=3, tilt=6),
    "marah":       _P((40, -108, "f"), (40, -108, "f"), lean=3),
    "kepal":       _P((16, -110, "f"), (16, -110, "f")),
    "menyerahkan": _P((62, -14, "m"), (62, -14, "m")),
    "angkat_tangan": _P((14, 10, "m"), (132, 24, "m")),
    "angkat_bahu": _P((52, -104, "m"), (52, -104, "m"), tilt=-4),
    "tepuk":       _P((42, -118, "m"), (42, -118, "m")),
    "menguap":     _P((14, 10, "m"), (30, -150, "m"), tilt=-3),
    "pegang_dada": _P((14, 10, "m"), (30, -138, "m")),
    "hormat":      _P((14, 10, "m"), (150, -112, "m")),
    "jalan":       _P((14, 10, "m"), (14, 10, "m"), legs="walk", swing=1.0),
    "lari":        _P((38, -80, "m"), (38, -80, "m"), legs="walk", swing=1.9, lean=9),
    "berjinjit":   _P((14, 10, "m"), (14, 10, "m"), legs="walk", swing=0.5),
    "duduk":       _P((26, -92, "m"), (26, -92, "m"), legs="stand", sit=1.0),
    "duduk_santai": _P((18, -40, "m"), (18, -40, "m"), sit=1.0, lean=-4),
    "duduk_hp":    _P((34, -128, "m"), (34, -128, "m"), sit=1.0, tilt=10, lean=3),
    "duduk_nulis": _P((30, -70, "m"), (40, -112, "m"), sit=1.0, tilt=12, lean=10),
    "duduk_game":  _P((36, -118, "m"), (36, -118, "m"), sit=1.0, tilt=4, lean=-3),
    "duduk_sorak": _P((132, 18, "m"), (132, 18, "m"), sit=1.0, lean=-4),
    "pegang_hp":   _P((34, -128, "m"), (34, -128, "m"), tilt=8),
    "pegang_buku": _P((34, -122, "m"), (34, -122, "m")),
    "menulis":     _P((30, -70, "m"), (40, -112, "m"), tilt=10, lean=6),
    "membungkuk":  _P((22, 4, "m"), (22, 4, "m"), lean=22, tilt=6),
    "bersandar":   _P((14, 10, "m"), (14, 10, "m"), lean=-8),
    "memeluk":     _P((30, -142, "m"), (30, -142, "m")),
    "tidur":       _P((8, 6, "m"), (8, 6, "m"), lean=-82),
    "tidur_kanan": _P((8, 6, "m"), (8, 6, "m"), lean=82),
    "hormat_bendera": _P((14, 10, "m"), (150, -118, "m")),
}
ALIAS_POSE = {"berdiri": "diam", "salam": "lambai", "nunjuk": "tunjuk", "cheer": "sorak", "jongkok": "duduk"}


def pose_def(name):
    return POSE.get(ALIAS_POSE.get(name, name), POSE["diam"])


# ------------------------------------------------------------------ tokoh
def _rot(p, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def _ellpts(cx, cy, rx, ry, n=44):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _wavy_ring(cx, cy, rx, ry, a0, a1, n, amps, steps=9):
    """Siluet rambut ikal lembut: deretan helai bergelombang yang ujungnya mengait ke bawah-luar."""
    def g(v):
        # helai ikal tak beraturan: naik landai membulat lalu ujungnya mengait (tidak simetris, tidak runcing)
        return math.sin(math.pi * (v ** 0.62)) ** 0.75
    pts = []
    for k in range(n):
        ta = a0 + (a1 - a0) * k / n
        tb = a0 + (a1 - a0) * (k + 1) / n
        A = amps[k % len(amps)]
        right = math.cos(math.radians((ta + tb) / 2)) >= 0
        for j in range(steps):
            u = j / steps
            v = u if right else 1.0 - u
            off = A * g(v)
            ang = math.radians(ta + (tb - ta) * u)
            pts.append((cx + (rx + off) * math.cos(ang), cy + (ry + off) * math.sin(ang)))
    ang = math.radians(a1)
    pts.append((cx + rx * math.cos(ang), cy + ry * math.sin(ang)))
    return pts


def _crescent(p0, pm, p1, w, n=10):
    """Helai bulan sabit meruncing di kedua ujung (tekstur ikal rambut)."""
    up = bezier(p0, pm, p1, n)
    out, inn = [], []
    for i, (x, y) in enumerate(up):
        t = i / n
        j, k = min(n, i + 1), max(0, i - 1)
        dx, dy = up[j][0] - up[k][0], up[j][1] - up[k][1]
        l = max(1e-6, math.hypot(dx, dy))
        nx, ny = -dy / l, dx / l
        h = w * math.sin(math.pi * t) * 0.5
        out.append((x + nx * h, y + ny * h))
        inn.append((x - nx * h, y - ny * h))
    return out + inn[::-1]


def _rectpts(x0, y0, x1, y1, r=0.0, n=5):
    """Persegi panjang bersudut tumpul, searah jarum jam dari sudut kiri-atas."""
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0),
                       (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += arc_pts(cx, cy, r, r, a0, a0 + 90, n)[:-1]
    return pts


class Tokoh:
    def __init__(self, spec):
        self.p = casting(spec)

    # st: x y s flip lean tilt sit look expr talk blink arms legs phase amp bob squash bawa
    def draw(self, c, st):
        p = self.p
        if p.get("maskot"):
            return self._draw_mascot(c, st)
        s = st["s"] * p["skala"]
        fl = st["flip"]
        sx, sy = st.get("squash", (1.0, 1.0))
        lean = math.radians(st.get("lean", 0))
        sit = st.get("sit", 0.0)
        dy = SIT_DROP * sit
        X0, Y0 = st["x"], st["y"] + st.get("hop", 0)
        cl, sl = math.cos(lean), math.sin(lean)

        def T(lx, ly, nodrop=False):
            if not nodrop:
                ly = ly + dy                      # badan turun saat duduk
            lx = lx * fl
            rx, ry = lx * cl - ly * sl, lx * sl + ly * cl
            return (X0 + rx * s * sx, Y0 + ry * s * sy)

        def TT(pts):
            return [T(*q) for q in pts]

        ow = (2.7 if p.get("outline_hangat") else 3.8) * s    # garis tepi halus & modern (tidak kaku tebal!)
        oc_w = (62, 44, 38) if p.get("outline_hangat") else OUT
        kemeja = warna(p.get("kemeja"), PUTIH)
        kulit = warna(p.get("kulit"), PUTIH)
        dasi = warna(p.get("dasi"))
        bawah_c = warna(p.get("bawah_warna"), HITAM)
        sepatu = warna(p.get("sepatu"), HITAM)
        # arah hadap: "depan" (0.0), "miring"/"3/4" (0.55), "samping" (0.92) atau float 0..1
        # otomatis pakai side-profile ("samping") saat berjalan/berlari kecuali user eksplisit meminta hadap="depan"
        stance_cur = st.get("legs", "stand")
        walking = stance_cur == "walk" and st.get("amp", 0.0) > 0.01
        hadap_raw = st.get("hadap", st.get("miring", None))
        if hadap_raw is None:
            turn = 0.92 if stance_cur == "walk" else 0.0
        elif isinstance(hadap_raw, str):
            turn = {"depan": 0.0, "miring": 0.55, "3/4": 0.55, "tiga_perempat": 0.55, "samping": 0.92, "side": 0.92}.get(hadap_raw.lower(), 0.0)
        elif isinstance(hadap_raw, bool):
            turn = 0.55 if hadap_raw else 0.0
        else:
            turn = clamp(float(hadap_raw), 0.0, 1.0)
        side_prof = turn >= 0.80
        # proporsi badan: berisi seimbang (tidak terlalu kurus di depan, 3/4, maupun side-profile)
        bw_base = float(p.get("badan_lebar", 1.52))
        hipb_base = float(p.get("pinggul_lebar", bw_base * 0.92))
        w_scale = (0.76 if side_prof else (1.0 - 0.14 * turn))
        bw = bw_base * w_scale
        hipb = hipb_base * w_scale
        hy = float(p.get("hip_y", -144.0))
        kt = float(p.get("kaki_tebal", 1.44))
        sm = float(p.get("sepatu_besar", 1.0))
        cx_t = (24.0 * bw if side_prof else 13.0 * turn)     # pergeseran garis tengah dada ke depan saat miring/samping

        # ransel (bagian belakang)
        if st.get("ransel"):
            rc = warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU
            rw = max(0.75, bw * 0.72)
            rx_off = -26.0 * turn
            c.blob(TT([(rx_off - 54 * rw, -256), (rx_off - 66 * rw, -230), (rx_off - 62 * rw, -176), (rx_off - 40 * rw, -152),
                       (rx_off + 40 * rw, -152), (rx_off + 62 * rw, -176), (rx_off + 66 * rw, -230), (rx_off + 54 * rw, -256), (rx_off, -268)]),
                   rc, ow, OUT)
            c.ell(*T(rx_off - 56 * rw, -214), 12 * s, 22 * s, gelap(rc, 0.18), ow * .85)
            c.ell(*T(rx_off + 56 * rw, -214), 12 * s, 22 * s, gelap(rc, 0.18), ow * .85)

        # ---- Layer 1: ekor kain hijab belakang punggung (di belakang badan & lengan, persis chibi hijab referensi!)
        if p.get("hijab") and p.get("hijab_gaya") == "modern":
            hj_b = warna(p["hijab"])
            hjd_b = warna(p.get("hijab_tua"), gelap(hj_b, 0.16))
            oc_h = (68, 44, 34)
            hx_b = -8.0 * turn
            hm_b = p.get("hijab_model", "pashmina")
            if hm_b in ("pashmina", "segiempat"):
                # ekor kain hijab mengalir anggun jatuh di belakang bahu kanan (persis referensi user!)
                tail_b = [
                    (hx_b + 10, -340), (hx_b + 92, -310), (hx_b + 106, -242),
                    (hx_b + 112, -162), (hx_b + 88, -140), (hx_b + 48, -158),
                    (hx_b + 20, -210),
                ]
                c.blob(TT(tail_b), gelap(hj_b, 0.04), 2.8 * s, oc_h, n=5)
                c.curve(TT([(hx_b + 84, -276), (hx_b + 90, -212), (hx_b + 82, -158)]), hjd_b, 2.2 * s)
            elif hm_b == "syari":
                # kain hijab syar'i lebar lembut mengalir di belakang kiri-kanan punggung
                tail_s = [
                    (hx_b - 92, -314), (hx_b - 102, -238), (hx_b - 94, -154),
                    (hx_b - 52, -142), (hx_b + 52, -142), (hx_b + 94, -154),
                    (hx_b + 102, -238), (hx_b + 92, -314),
                ]
                c.blob(TT(tail_s), gelap(hj_b, 0.04), 2.8 * s, oc_h, n=5)

        # ---- lengan belakang (saat hadap miring/samping, lengan sisi jauh digambar di belakang torso)
        arms = st["arms"]
        hands = {}
        front_arms = []
        mid_arms = []
        ph_w = st.get("phase", 0.0)
        amp_w = st.get("amp", 0.0)
        sw_w = st.get("swing", 1.0)
        for side, key in (("L", -1), ("R", 1)):
            a, e, hk = arms[side]
            if side_prof and walking:
                # ayunan lengan maju-mundur natural berlawanan fase dengan kaki (tampak samping)
                swing_ang = math.sin(ph_w + (0.0 if side == "R" else math.pi)) * 34.0 * min(1.3, amp_w) * sw_w
                a = swing_ang
                e = max(12.0, 22.0 + swing_ang * 0.35)   # siku menekuk lembut ke depan (+x)
            ar, br = math.radians(a), math.radians(a + e)
            hd_y = SHOULDER_Y + 12 + math.cos(ar) * UP_ARM + math.cos(br) * FORE_ARM
            if turn >= 0.25 and side == "L" and hd_y >= SHOULDER_Y - 52:
                # sisi belakang (L) berada di belakang torso saat miring/samping
                hands[side] = self._arm(c, T, s, fl, key, a, e, hk, kemeja, ow, dy, turn)
            elif hd_y < SHOULDER_Y - 52:
                front_arms.append((side, key, a, e, hk))
            else:
                mid_arms.append((side, key, a, e, hk))

        # ---- kaki
        hipy = hy + dy
        hip = [T(-18, hy), T(18, hy)]
        feet, knees, hip = self._legs(st, T, sit, turn)
        skirt = p.get("bawah") == "rok"
        legw = (11.5 if skirt else 13.6) * kt
        legc = (56, 56, 68) if (skirt and (p.get("hijab") or bawah_c == HITAM)) else (gelap(bawah_c, .36) if skirt else bawah_c)
        legoc = OUT
        jog_mode = bool(p.get("celana_jogger")) and not skirt
        if jog_mode:
            # ===== 1) KAKI CELANA JOGGER LONGGAR DULU (agar sepatu & lidah sepatu tampil utuh 3D di depan manset!) =====
            cxw = T(0, hy)[0]
            wk_s = 0.80 if side_prof else 1.0

            def _nrm(p0, p1):
                ddx, ddy = p1[0] - p0[0], p1[1] - p0[1]
                ll = max(1e-6, math.hypot(ddx, ddy))
                return (-ddy / ll, ddx / ll)
            for i in (0, 1):
                A, K, F = hip[i], knees[i], feet[i]
                N_ = (F[0], F[1] - 22.0 * s * sm)
                n1, n2 = _nrm(A, K), _nrm(K, N_)
                nk = ((n1[0] + n2[0]) * 0.5, (n1[1] + n2[1]) * 0.5)
                ext = 1.0 if abs(A[0] + n1[0] - cxw) >= abs(A[0] - n1[0] - cxw) else -1.0
                is_ag = bool(p.get("anak_ghibli"))
                Wo = (33.5 * s * wk_s, 35.5 * s * wk_s, 26.0 * s) if is_ag else (29.5 * s * wk_s, 33.0 * s * wk_s, 21.0 * s)
                Wi = (20.5 * s * wk_s, 22.0 * s * wk_s, 17.5 * s) if is_ag else (18.5 * s * wk_s, 20.0 * s * wk_s, 14.5 * s)

                def LP(t, f, A=A, K=K, N_=N_, n1=n1, n2=n2, nk=nk, ext=ext, Wo=Wo, Wi=Wi):
                    W_use = Wo if f >= 0 else Wi
                    if t <= 0.58:
                        u = t / 0.58
                        P = (lerp(A[0], K[0], u), lerp(A[1], K[1], u))
                        nn = (lerp(n1[0], nk[0], u), lerp(n1[1], nk[1], u))
                        w = lerp(W_use[0], W_use[1], math.sin(u * math.pi / 2))
                    else:
                        u = (t - 0.58) / 0.42
                        P = (lerp(K[0], N_[0], u), lerp(K[1], N_[1], u))
                        nn = (lerp(nk[0], n2[0], u), lerp(nk[1], n2[1], u))
                        w = lerp(W_use[1], W_use[2], u ** 1.6)
                    return (P[0] + nn[0] * w * f * ext, P[1] + nn[1] * w * f * ext)
                ts = [k / 10.0 for k in range(11)]
                leg_fill = gelap(legc, 0.12) if ((turn >= 0.25 or walking) and i == 0) else legc
                outline = [LP(t, 1.0) for t in ts] + [LP(t, -1.0) for t in reversed(ts)]
                c.poly(outline, leg_fill)
                # bayangan sisi dalam & bawah lutut
                c.poly([LP(t, -0.98) for t in ts[:10]] + [LP(t, -0.38) for t in reversed(ts[:10])], gelap(leg_fill, 0.12))
                # strip sporty putih (paha) + hitam (betis) khusus untuk karakter dengan `strip_jogger=True` (Kribo)
                if p.get("strip_jogger") and i == 1 and not side_prof:
                    tw = [0.04 + 0.50 * k / 6 for k in range(7)]
                    tb_ = [0.54 + 0.38 * k / 6 for k in range(7)]
                    c.poly([LP(t, 0.96) for t in tw] + [LP(t, 0.54) for t in reversed(tw)], PUTIH)
                    c.poly([LP(t, 0.96) for t in tb_] + [LP(t, 0.54) for t in reversed(tb_)], (42, 44, 50))
                    c.line([LP(t, 0.54) for t in tw + tb_], gelap(leg_fill, 0.32), 1.8 * s)
                # lipatan kain jogger organik
                c.curve([LP(0.42, -0.68), LP(0.48, -0.15), LP(0.45, 0.28)], gelap(leg_fill, 0.22), 1.9 * s)
                c.curve([LP(0.75, -0.65), LP(0.82, -0.05), LP(0.78, 0.42)], gelap(leg_fill, 0.25), 2.1 * s)
                c.poly(outline, None, 2.8 * s, OUT)
                # manset karet pergelangan kaki
                cb = LP(1.0, 0.92), LP(1.0, -0.92)
                cuff = [LP(0.90, -0.94), LP(0.90, 0.94), (cb[0][0], cb[0][1] + 4 * s), (cb[1][0], cb[1][1] + 4 * s)]
                c.blob(cuff, gelap(leg_fill, 0.08), 2.6 * s, OUT, n=3)
                # sedikit pergelangan kaki mengintip di bawah manset sebelum masuk sepatu (persis referensi!)
                c.poly([(cb[1][0] + 4 * s, cb[1][1] + 2 * s), (cb[0][0] - 4 * s, cb[0][1] + 2 * s),
                        (cb[0][0] - 5 * s, cb[0][1] + 10 * s), (cb[1][0] + 5 * s, cb[1][1] + 10 * s)],
                       gelap(kulit, 0.08), 2.0 * s, OUT)
            # ===== 2) dudukan pinggul + jahitan fly + pinggang karet berkerut =====
            pw = 50.0 * (0.62 if side_prof else 1.0 - 0.12 * turn)
            seat = [(-pw, hy - 22), (pw, hy - 22), (pw + 2, hy - 2), (pw * 0.58, hy + 15),
                    (0, hy + 17), (-pw * 0.58, hy + 15), (-pw - 2, hy - 2)]
            c.poly(TT(seat), bawah_c)
            c.line(TT([(-pw, hy - 22), (-pw - 2, hy - 2)]), OUT, 2.8 * s)
            c.line(TT([(pw, hy - 22), (pw + 2, hy - 2)]), OUT, 2.8 * s)
            if not side_prof:
                c.curve(TT([(0, hy - 6), (-1, hy + 8), (2, hy + 17)]), gelap(bawah_c, 0.30), 2.2 * s)
                c.curve(TT([(3, hy - 6), (5, hy + 6), (1, hy + 13)]), gelap(bawah_c, 0.22), 1.6 * s)
                c.line(TT([(-18, hy - 5), (-25, hy + 14)]), gelap(bawah_c, 0.24), 1.8 * s)
                c.line(TT([(18, hy - 5), (25, hy + 14)]), gelap(bawah_c, 0.24), 1.8 * s)
            c.poly(TT([(-pw - 1, hy - 26), (pw + 1, hy - 26), (pw + 2, hy - 6), (-pw - 2, hy - 6)]),
                   gelap(bawah_c, 0.05), 2.6 * s, OUT)
            for kx in (-0.76, -0.46, -0.18, 0.12, 0.42, 0.72):
                c.line(TT([(pw * kx, hy - 24), (pw * kx + 1.5, hy - 8)]), gelap(bawah_c, 0.26), 1.6 * s)
            # ===== 3) SEPATU GHIBLI LOAFER atau SNEAKER CHUNKY 3/4 DI DEPAN MANSET =====
            S_sh = s * sm
            for i in (0, 1):
                fx, fy = feet[i]
                dx_ = (1.0 if (turn >= 0.25 or walking) else (-1.0 if i == 0 else -0.82)) * fl
                fx_s = fx + (-2.0 * s if i == 0 else 0.0) * fl
                fy_s = fy + (3.0 * s if i == 1 else 0.0)
                base_sh = sepatu if p.get("sepatu") else (44, 46, 52)
                shoe_col = base_sh if i == 1 else gelap(base_sh, 0.10)
                sole_col = gelap(base_sh, 0.44)
                mid_col = terang(base_sh, 0.20)

                def SP(u, v, fx_s=fx_s, fy_s=fy_s, dx_=dx_):
                    return (fx_s + dx_ * u * S_sh, fy_s + v * S_sh)

                if p.get("sepatu_gaya") == "loafer":
                    # sepatu kulit membulat bersih ala Studio Ghibli (seperti referensi user!)
                    loafer = [
                        SP(-15, -4), SP(-16, -15), SP(-9, -19), SP(3, -18),
                        SP(18, -14), SP(27, -6), SP(26, 2),
                        SP(13, 5), SP(-2, 3), SP(-14, 1),
                    ]
                    c.blob(loafer, shoe_col, 2.6 * s, OUT, n=5)
                    sole_l = [SP(-15, -3), SP(0, -1), SP(14, 1), SP(26, -1), SP(25, 3), SP(12, 5), SP(-14, 2)]
                    c.blob(sole_l, sole_col, 2.0 * s, OUT, n=4)
                    c.ell(*SP(13, -9), 7.5 * S_sh, 3.5 * S_sh, terang(shoe_col, 0.16))
                else:
                    # 1) siluet penuh sepatu chunky 3/4 (tumit kanan-atas, lidah tinggi di tengah-atas, moncong bulat tebal)
                    full_shoe = [
                        SP(-16, -6), SP(-17, -18), SP(-11, -22), SP(-4, -20),
                        SP(0, -29), SP(8, -29), SP(13, -21),
                        SP(23, -14), SP(29, -6), SP(27, 3),
                        SP(14, 6), SP(2, 2), SP(-6, 0), SP(-14, 0),
                    ]
                    c.blob(full_shoe, shoe_col, 2.8 * s, OUT, n=5)
                    # 2) pita sol karet tebal
                    sole_band = [
                        SP(-16, -6), SP(-6, -4), SP(2, -3), SP(14, 1), SP(28, -2),
                        SP(27, 3), SP(14, 6), SP(2, 2), SP(-6, 0), SP(-14, 0),
                    ]
                    c.blob(sole_band, sole_col, 2.2 * s, OUT, n=4)
                    c.curve([SP(-15, -5.5), SP(-2, -3), SP(14, 1), SP(27, -1.5)], mid_col, 2.0 * s)
                    c.poly([SP(-12, -19), SP(-4, -18), SP(-3, -21), SP(-10, -21)], gelap(shoe_col, 0.50), 1.6 * s, OUT)
                    c.curve([SP(-2, -19), SP(1, -27), SP(7, -27), SP(11, -19)], gelap(shoe_col, 0.28), 1.8 * s)
                    c.curve([SP(-4, -5), SP(2, -15), SP(14, -15), SP(23, -6)], gelap(shoe_col, 0.34), 1.8 * s)
                    c.ell(*SP(18, -6), 6.2 * S_sh, 3.6 * S_sh, terang(shoe_col, 0.16))
                    for lu, lv in ((3, -22), (8, -19), (13, -16)):
                        c.line([SP(lu, lv), SP(lu + 5.5, lv - 1.5)], terang(shoe_col, 0.32), 2.2 * s)
        for i in ((0, 1) if not jog_mode else ()):
            ax, ay = hip[i]
            kx, ky = knees[i]
            fx, fy = feet[i]
            # pergelangan berhenti di dalam bagian atas sepatu agar cap bulat kaki tidak tembus ke bawah sol
            ank_y = fy - max(14.0 * s * sm, legw * 0.50 * s)
            leg_fill = gelap(legc, 0.16) if ((turn >= 0.25 or walking) and i == 0) else legc
            if p.get("celana_jogger") and not skirt:
                # CELANA JOGGER LONGGAR BERISI MERUNCING DI PERGELANGAN (persis gambar referensi!)
                sg_l = -1 if i == 0 else 1
                w_hip = 22.0 * s * (0.78 if side_prof else 1.0)
                w_mid = 24.5 * s * (0.82 if side_prof else 1.0)
                w_ank = 13.5 * s
                jog_pts = [
                    (ax - w_hip, ay - 6 * s), (ax + w_hip, ay - 6 * s),
                    (kx + w_mid, ky), (fx + w_ank, ank_y),
                    (fx - w_ank, ank_y), (kx - w_mid, ky),
                ]
                c.poly(jog_pts, leg_fill, 3.0 * s, OUT)
                # strip sporty putih-hitam hanya untuk karakter yang mengaktifkan `strip_jogger` (Kribo)
                if p.get("strip_jogger") and not side_prof and i == 1:
                    c.poly([(kx + w_mid * 0.45, ky - 22 * s), (kx + w_mid * 0.92, ky - 22 * s),
                            (fx + w_ank * 0.90, ank_y - 26 * s), (fx + w_ank * 0.35, ank_y - 26 * s)], PUTIH)
                    c.poly([(fx + w_ank * 0.35, ank_y - 26 * s), (fx + w_ank * 0.90, ank_y - 26 * s),
                            (fx + w_ank * 0.95, ank_y - 2 * s), (fx + w_ank * 0.35, ank_y - 2 * s)], (44, 46, 52))
                # lipatan kain jogger & manset pergelangan kaki
                c.line([(kx - sg_l * 6 * s, ky - 8 * s), (kx + sg_l * 10 * s, ky + 6 * s)], gelap(leg_fill, 0.22), 2.2 * s)
                c.poly([(fx - w_ank * 0.92, ank_y - 8 * s), (fx + w_ank * 0.92, ank_y - 8 * s),
                        (fx + w_ank * 0.85, ank_y + 2 * s), (fx - w_ank * 0.85, ank_y + 2 * s)], gelap(leg_fill, 0.14), 2.2 * s, OUT)
                c.poly(jog_pts, None, 3.0 * s, OUT)
            else:
                c.line([(ax, ay), (kx, ky), (fx, ank_y)], legoc, (legw + 2 * 3.8) * s)
                c.line([(ax, ay), (kx, ky), (fx, ank_y)], leg_fill, legw * s)
            # sepatu
            toe = 1 if (turn >= 0.25 or walking) else (-1 if i == 0 else 1)
            dir_x = toe * fl
            shoe_col = gelap(sepatu, 0.16) if ((turn >= 0.25 or walking) and i == 0) else sepatu
            if p.get("sepatu_chunky"):
                # SEPATU GHIBLI LOAFER atau SNEAKER CHUNKY 3/4 untuk karakter ber-rok & non-jogger
                S_sh = s * sm
                dx_s = (1.0 if (turn >= 0.25 or walking) else (-1.0 if i == 0 else -0.82)) * fl
                fx_s = fx + (-2.0 * s if i == 0 else 0.0) * fl
                fy_s = fy + (3.0 * s if i == 1 else 0.0)
                base_sh = sepatu if p.get("sepatu") else (44, 46, 52)
                sc_s = base_sh if i == 1 else gelap(base_sh, 0.10)
                sole_s = gelap(base_sh, 0.44)
                mid_s = terang(base_sh, 0.20)

                def SP2(u, v, fx_s=fx_s, fy_s=fy_s, dx_s=dx_s):
                    return (fx_s + dx_s * u * S_sh, fy_s + v * S_sh)

                if p.get("sepatu_gaya") == "chibi_bulat":
                    # sepatu bundar mungil lembut mengintip dari bawah rok panjang (persis referensi chibi hijab!)
                    oc_s = (68, 44, 34)
                    sx_c = fx + (dir_x * 6.0 * s * sm if (turn >= 0.25 or walking) else (-4.0 if i == 0 else 4.0) * s * fl)
                    c.ell(sx_c, fy - 7.5 * s * sm, 21.0 * s * sm, 10.5 * s * sm, sc_s, 2.6 * s, oc_s)
                    c.ell(sx_c + (2.5 if i == 1 else -2.5) * s, fy - 9.5 * s * sm, 9.0 * s * sm, 4.0 * s * sm, terang(sc_s, 0.16))
                elif p.get("sepatu_gaya") in ("loafer", "maryjane"):
                    loafer = [
                        SP2(-15, -4), SP2(-16, -15), SP2(-9, -19), SP2(3, -18),
                        SP2(18, -14), SP2(27, -6), SP2(26, 2),
                        SP2(13, 5), SP2(-2, 3), SP2(-14, 1),
                    ]
                    c.blob(loafer, sc_s, 2.6 * s, OUT, n=5)
                    sole_l = [SP2(-15, -3), SP2(0, -1), SP2(14, 1), SP2(26, -1), SP2(25, 3), SP2(12, 5), SP2(-14, 2)]
                    c.blob(sole_l, sole_s, 2.0 * s, OUT, n=4)
                    if p.get("sepatu_gaya") == "maryjane":
                        # bukaan sepatu Mary-Jane chibi + tali strap mungil melintang di punggung kaki!
                        c.ell(*SP2(4, -15), 8.2 * S_sh, 4.4 * S_sh, (248, 244, 238), 1.6 * s, OUT)
                        c.line([SP2(-1, -18), SP2(8, -11)], gelap(sc_s, 0.20), 3.4 * s)
                        c.ell(*SP2(8, -11), 2.2 * S_sh, 2.2 * S_sh, (236, 206, 136))
                    c.ell(*SP2(16, -8), 6.2 * S_sh, 3.0 * S_sh, terang(sc_s, 0.18))
                else:
                    full_sh = [
                        SP2(-16, -6), SP2(-17, -18), SP2(-11, -22), SP2(-4, -20),
                        SP2(0, -29), SP2(8, -29), SP2(13, -21),
                        SP2(23, -14), SP2(29, -6), SP2(27, 3),
                        SP2(14, 6), SP2(2, 2), SP2(-6, 0), SP2(-14, 0),
                    ]
                    c.blob(full_sh, sc_s, 2.8 * s, OUT, n=5)
                    sole_b = [
                        SP2(-16, -6), SP2(-6, -4), SP2(2, -3), SP2(14, 1), SP2(28, -2),
                        SP2(27, 3), SP2(14, 6), SP2(2, 2), SP2(-6, 0), SP2(-14, 0),
                    ]
                    c.blob(sole_b, sole_s, 2.2 * s, OUT, n=4)
                    c.curve([SP2(-15, -5.5), SP2(-2, -3), SP2(14, 1), SP2(27, -1.5)], mid_s, 2.0 * s)
                    c.poly([SP2(-12, -19), SP2(-4, -18), SP2(-3, -21), SP2(-10, -21)], gelap(sc_s, 0.50), 1.6 * s, OUT)
                    c.curve([SP2(-2, -19), SP2(1, -27), SP2(7, -27), SP2(11, -19)], gelap(sc_s, 0.28), 1.8 * s)
                    c.curve([SP2(-4, -5), SP2(2, -15), SP2(14, -15), SP2(23, -6)], gelap(sc_s, 0.34), 1.8 * s)
                    c.ell(*SP2(18, -6), 6.2 * S_sh, 3.6 * S_sh, terang(sc_s, 0.16))
                    for lu, lv in ((3, -22), (8, -19), (13, -16)):
                        c.line([SP2(lu, lv), SP2(lu + 5.5, lv - 1.5)], terang(sc_s, 0.32), 2.2 * s)
            else:
                heel_x = fx - dir_x * 11.5 * s * sm
                front_x = fx + dir_x * 26.5 * s * sm
                top_y = fy - 18.5 * s * sm
                mid_y = fy - 15.5 * s * sm
                sole_y = fy - 4.8 * s * sm
                bot_y = fy
                shoe_poly = [
                    (heel_x, bot_y),
                    (heel_x - dir_x * 1.5 * s * sm, fy - 7.5 * s * sm),
                    (heel_x + dir_x * 2.0 * s * sm, top_y),
                    (fx + dir_x * 4.0 * s * sm, top_y - 1.0 * s * sm),
                    (fx + dir_x * 16.0 * s * sm, mid_y + 1.5 * s * sm),
                    (front_x, fy - 6.5 * s * sm),
                    (front_x - dir_x * 1.5 * s * sm, bot_y),
                ]
                if p.get("sepatu_sneaker"):
                    c.poly(shoe_poly, shoe_col, ow * .82, OUT)
                    cap_poly = [
                        (fx + dir_x * 16.5 * s * sm, sole_y),
                        (fx + dir_x * 17.5 * s * sm, mid_y + 2.8 * s * sm),
                        (front_x - dir_x * 1.2 * s * sm, fy - 7.0 * s * sm),
                        (front_x - dir_x * 0.6 * s * sm, sole_y),
                    ]
                    c.poly(cap_poly, PUTIH)
                    sole_poly = [
                        (heel_x, bot_y),
                        (heel_x - dir_x * 0.6 * s * sm, sole_y),
                        (front_x - dir_x * 0.5 * s * sm, sole_y),
                        (front_x - dir_x * 1.5 * s * sm, bot_y),
                    ]
                    c.poly(sole_poly, PUTIH, ow * .55, OUT)
                    c.poly(shoe_poly, None, ow * .82, OUT)
                else:
                    c.poly(shoe_poly, shoe_col, ow * .82, OUT)
                    c.line([(fx + dir_x * 1.0 * s * sm, top_y + 4.0 * s * sm),
                            (fx + dir_x * 11.0 * s * sm, mid_y + 4.5 * s * sm)],
                           terang(shoe_col, 0.24), 3.0 * s * sm)
        if skirt:
            oc_sk = (68, 44, 34) if p.get("hijab_gaya") == "modern" else OUT
            if p.get("rok_panjang"):
                # ROK PANJANG CHIBI JATUH LEMBUT DARI BAWAH TUNIK (ramping-mekar alami, TIDAK menggembung balon di pinggul!)
                hem = -20.0 + dy * 0.45
                sw = max(0.74 if side_prof else 1.0, hipb * 0.64)
                y_rk_top = hy + 16.0
                w_top = 56.0 * sw
                w_bot = 68.0 * sw
                if side_prof:
                    w_top, w_bot = 38.0 * sw, 52.0 * sw
                    bot_r = [
                        (w_bot, hem - 4), (w_bot * 0.45, hem + 5), (0, hem - 1),
                        (-w_bot * 0.45, hem + 5), (-w_bot, hem - 3),
                    ]
                else:
                    # tepi bawah bergelombang 3 kelopak lembut persis referensi chibi hijab!
                    bot_r = (
                        bezier((w_bot, hem - 5), (w_bot * 0.68, hem + 6), (w_bot * 0.34, hem - 1), 6) +
                        bezier((w_bot * 0.34, hem - 1), (0, hem + 8), (-w_bot * 0.34, hem - 1), 6)[1:] +
                        bezier((-w_bot * 0.34, hem - 1), (-w_bot * 0.68, hem + 6), (-w_bot, hem - 5), 6)[1:]
                    )
                skirt_pts = [(-w_top, y_rk_top), (w_top, y_rk_top)] + bot_r
                c.poly(TT(skirt_pts), bawah_c, 2.8 * s, oc_sk)
                # bayangan cel lembut di sisi kanan & lipatan rok jatuh lurus alami
                c.poly(TT([(w_top * 0.25, y_rk_top), (w_top, y_rk_top), (w_bot, hem - 5), (w_bot * 0.30, hem)]),
                       gelap(bawah_c, 0.16))
                if not side_prof:
                    for fx_r in (-0.42, -0.10, 0.24, 0.56):
                        c.line(TT([(w_top * fx_r, y_rk_top + 4), (w_bot * fx_r * 1.04, hem - 1)]),
                               gelap(bawah_c, 0.28), 2.0 * s)
                c.poly(TT(skirt_pts), None, 2.8 * s, oc_sk)
            else:
                hem = hy + 62 + dy * 0.85
                sw = max(0.74 if side_prof else 0.98, hipb * 1.04)
                skirt_pts = [(-32 * sw, hy - 14), (32 * sw, hy - 14), (54 * sw, hem - 4)] + bezier((54 * sw, hem - 4), (0, hem + 18), (-54 * sw, hem - 4), 10)[1:-1] + [(-54 * sw, hem - 4)]
                c.poly(TT(skirt_pts), bawah_c, 2.8 * s, oc_sk)
                if turn >= 0.25:
                    c.poly(TT([(-30 * sw, hy - 12), (-6 * sw, hy - 12), (-16 * sw, hem + 4), (-48 * sw, hem - 5)]),
                           gelap(bawah_c, 0.14))
                else:
                    c.poly(TT([(10 * sw, hy - 12), (30 * sw, hy - 12), (49 * sw, hem - 5), (22 * sw, hem + 4)]),
                           gelap(bawah_c, 0.14))
                if not side_prof:
                    for px_s in (-22, -6, 10, 24):
                        c.line(TT([(px_s * sw * 0.68, hy - 6), (px_s * sw * 1.08, hem + 3)]), gelap(bawah_c, 0.24), 1.8 * s)
                c.poly(TT(skirt_pts), None, 2.8 * s, oc_sk)
        elif not jog_mode:
            if side_prof:
                # pinggul celana side-profile ramping sejajar paha depan-belakang (tidak terpotong/melebar)
                px_w = max(21.0 * hipb, legw * 0.62)
                c.poly(TT([(-px_w, hy - 14), (px_w, hy - 14),
                           (px_w * 0.94, hy + 10), (0, hy + 16), (-px_w * 0.94, hy + 10)]), bawah_c, ow, OUT)
                # gambar ulang pangkal paha depan agar menyatu mulus ke pinggul
                c.line([hip[1], knees[1]], legc, legw * s)
            else:
                kl_p = float(p.get("kaki_lebar", 1.15)) * (1.0 - 0.22 * turn)
                walk_k = (1.0 - 0.18 * min(1.0, st.get("amp", 0.0))) if walking else 1.0
                px_w = max(25.0 * hipb, 17.5 * kl_p * walk_k + legw * 0.50)
                c.poly(TT([(-px_w, hy - 14), (px_w, hy - 14),
                           (px_w * 0.94, hy + 10), (0, hy + 16), (-px_w * 0.94, hy + 10)]), bawah_c, ow, OUT)
                for i in (0, 1):
                    leg_fill = gelap(legc, 0.16) if ((turn >= 0.25 or walking) and i == 0) else legc
                    c.line([hip[i], knees[i]], leg_fill, legw * s)
        # ---- torso
        if p.get("tunik_chibi"):
            self._tunik_chibi(c, TT, s, kemeja, hy, turn, side_prof)
        elif p.get("sweater"):
            self._sweater_ghibli(c, TT, s, kemeja, kulit, hy, turn, side_prof)
        elif p.get("kaos_chibi"):
            self._kaos_chibi(c, TT, s, kemeja, kulit, hy, turn, side_prof)
        elif False:
            # KAOS A-LINE / OVERSIZED BAHU MELENGKUNG TURUN (persis gambar referensi, BUKAN kotak persegi panjang!)
            y_top = SHOULDER_Y - 4.0
            y_bot = hy - 4.0
            tw_n = 18.0 * (0.75 if side_prof else 1.0)
            tw_s = 46.0 * bw * (0.68 if side_prof else 1.0)
            bw_b = 34.0 * hipb * (0.74 if side_prof else 1.0)
            # siluet bahu melengkung miring alami ke bawah & hem bawah membulat lembut
            kaos_pts = [
                (-tw_n, y_top), (0, y_top + 6), (tw_n, y_top),
                (tw_s * 0.72, y_top + 8), (tw_s, y_top + 28),
                (bw_b * 1.06, y_bot - 22), (bw_b, y_bot - 4),
                (0, y_bot + 6), (-bw_b, y_bot - 4),
                (-bw_b * 1.06, y_bot - 22), (-tw_s, y_top + 28), (-tw_s * 0.72, y_top + 8),
            ]
            c.blob(TT(kaos_pts), kemeja, 3.2 * s, OUT, n=5)
            # cel shading lembut di sisi kanan & lipatan bawah kaos
            c.poly(TT([(tw_n * 0.5, y_top + 8), (tw_s * 0.92, y_top + 26),
                       (bw_b * 0.96, y_bot - 4), (bw_b * 0.30, y_bot + 2)]), gelap(kemeja, 0.16))
            c.curve(TT([(-bw_b * 0.72, y_bot - 6), (0, y_bot + 2), (bw_b * 0.72, y_bot - 6)]), gelap(kemeja, 0.28), 2.6 * s)
            c.blob(TT(kaos_pts), None, 3.2 * s, OUT, n=5)
            # pita pinggang jogger berkerut di bawah hem kaos
            if p.get("celana_jogger"):
                c.poly(TT([(-bw_b * 0.94, y_bot + 2), (bw_b * 0.94, y_bot + 2),
                           (bw_b * 0.96, y_bot + 16), (-bw_b * 0.96, y_bot + 16)]), bawah_c, 2.6 * s, OUT)
                for kx in (-0.55, -0.22, 0.22, 0.55):
                    c.line(TT([(bw_b * kx, y_bot + 4), (bw_b * kx, y_bot + 14)]), gelap(bawah_c, 0.24), 1.8 * s)
        elif p.get("coat_naa"):
            # coat/blazer panjang terbuka persis gaya cewek @naa (turtleneck gelap + coat slate-blue panjang + badge + saku)
            inner_c = warna(p.get("kemeja_dalam"), (54, 62, 70))
            top_w = 34.0 * bw
            bot_w = 37.0 * hipb
            y_top = SHOULDER_Y - 2.0
            y_bot = hy + 34.0    # coat panjang jatuh sampai paha atas!
            # inner turtleneck gelap
            c.poly(TT([(-top_w * 0.68, y_top), (top_w * 0.68, y_top),
                       (bot_w * 0.65, hy + 4), (-bot_w * 0.65, hy + 4)]), inner_c, ow * .78, OUT)
            # kerah turtleneck memeluk leher
            c.poly(TT([(cx_t - 18, y_top - 14), (cx_t + 18, y_top - 14),
                       (cx_t + 20, y_top + 6), (cx_t - 20, y_top + 6)]), inner_c, ow * .76, OUT)
            if side_prof:
                c.poly(TT([(-top_w, y_top + 10), (-top_w * 0.68, y_top - 2), (cx_t - 2, y_top + 2),
                           (cx_t + 4, y_bot), (-bot_w * 0.94, y_bot), (-bot_w, hy - 8)]), kemeja, ow, OUT)
            else:
                for sg in (-1, 1):
                    cc = gelap(kemeja, 0.09) if (sg < 0 if turn >= 0.25 else sg > 0) else kemeja
                    in_t = cx_t + sg * 16.0
                    in_b = cx_t + sg * 24.0
                    c.poly(TT([
                        (in_t, y_top), (sg * top_w * 0.72, y_top - 2), (sg * top_w, y_top + 12),
                        (sg * bot_w, y_bot - 4), (in_b, y_bot + 4), (in_t, y_top + 32),
                    ]), cc, ow, OUT)
                    # lapel kecil
                    c.poly(TT([(in_t, y_top), (in_t + sg * 14, y_top + 18), (in_t + sg * 6, y_top + 28),
                               (in_t + sg * 14, y_top + 38), (in_t, y_top + 48)]), terang(kemeja, 0.06), ow * .72, OUT)
                # saku miring halus di kedua sisi coat (rapi & elegan)
                for sg in (-1, 1):
                    c.line(TT([(cx_t + sg * 30, hy - 2), (cx_t + sg * 48, hy - 12)]), gelap(kemeja, 0.24), 2.4 * s)
        elif p.get("jaket"):
            # jaket bomber/kasual terbuka (gaya chibi Ghibli gambar 1: inner putih + jaket kiri-kanan + saku + sabuk)
            inner_c = warna(p.get("kemeja_dalam"), (242, 240, 234))
            top_w = 34.0 * bw
            bot_w = 33.5 * hipb
            y_top = SHOULDER_Y - 2.0
            y_bot = hy - 8.0
            # kaos dalaman putih-krem
            c.poly(TT([(-top_w * 0.72, y_top), (top_w * 0.72, y_top),
                       (bot_w * 0.72, y_bot + 2), (-bot_w * 0.72, y_bot + 2)]), inner_c, ow * .78, OUT)
            # sabuk coklat + gesper emas di pinggang
            if p.get("sabuk"):
                sbc = warna(p["sabuk"], (136, 98, 66))
                c.poly(TT([(-bot_w * 0.76, y_bot - 12), (bot_w * 0.76, y_bot - 12),
                           (bot_w * 0.76, y_bot + 2), (-bot_w * 0.76, y_bot + 2)]), sbc, ow * .72, OUT)
                c.poly(TT([(cx_t - 9, y_bot - 13), (cx_t + 9, y_bot - 13),
                           (cx_t + 9, y_bot + 3), (cx_t - 9, y_bot + 3)]), (218, 178, 96), ow * .68, OUT)
            # panel kiri & kanan jaket terbuka + kerah rib & saku miring
            if side_prof:
                # saat side-profile: jaket membungkus punggung hingga dekat dada depan (kaos putih mengintip di depan)
                c.poly(TT([
                    (-top_w, y_top + 10), (-top_w * 0.72, y_top - 2), (cx_t - 4, y_top + 2),
                    (cx_t - 4, y_bot + 4), (-bot_w * 0.88, y_bot + 4), (-bot_w, y_bot - 6),
                ]), kemeja, ow, OUT)
                c.line(TT([(-bot_w * 0.94, y_bot - 8), (cx_t - 4, y_bot - 8)]), gelap(kemeja, 0.24), 3.0 * s)
            else:
                gap = 12.0
                for sg in (-1, 1):
                    jc = gelap(kemeja, 0.11) if (sg < 0 if turn >= 0.25 else sg > 0) else kemeja
                    in_x = cx_t + sg * gap
                    out_t = sg * top_w
                    out_b = sg * bot_w
                    c.poly(TT([
                        (in_x, y_top + 2), (out_t * 0.75, y_top - 2), (out_t, y_top + 12),
                        (out_b, y_bot - 6), (out_b * 0.88, y_bot + 4), (in_x, y_bot + 4),
                    ]), jc, ow, OUT)
                    c.line(TT([(in_x, y_bot - 8), (out_b * 0.94, y_bot - 8)]), gelap(kemeja, 0.24), 3.0 * s)
                    c.line(TT([(lerp(in_x, out_b, 0.42), y_bot - 22), (lerp(in_x, out_b, 0.80), y_bot - 36)]), gelap(kemeja, 0.26), 3.2 * s)
        elif p.get("blazer"):
            inner_c = warna(p.get("kemeja_dalam"), PUTIH)
            lum = 0.299 * kemeja[0] + 0.587 * kemeja[1] + 0.114 * kemeja[2]
            lap_c = gelap(kemeja, 0.14) if lum > 180 else terang(kemeja, 0.08)
            btn_y = min(hy - 20, SHOULDER_Y + 62)
            nx = min(17.5 * bw, 20.5)
            c.poly(TT([(cx_t - nx - 5, SHOULDER_Y), (cx_t + nx + 5, SHOULDER_Y),
                       (cx_t + 7, btn_y + 8), (cx_t - 7, btn_y + 8)]), inner_c, ow * .78, OUT)
            if p.get("krah", True) and not p.get("dasi_kupu"):
                c.poly(TT([(cx_t - 3.5, SHOULDER_Y - 2), (cx_t - 18, SHOULDER_Y - 1), (cx_t - 11.5, SHOULDER_Y + 17)]), inner_c, ow * .78, OUT)
                c.poly(TT([(cx_t + 3.5, SHOULDER_Y - 2), (cx_t + 18, SHOULDER_Y - 1), (cx_t + 11.5, SHOULDER_Y + 17)]), inner_c, ow * .78, OUT)
            if dasi and not p.get("dasi_kupu"):
                c.poly(TT([(cx_t - 4.0, SHOULDER_Y + 16), (cx_t + 4.0, SHOULDER_Y + 16),
                           (cx_t + 9.5, SHOULDER_Y + 48), (cx_t, SHOULDER_Y + 61), (cx_t - 9.5, SHOULDER_Y + 48)]), dasi, ow * .78, OUT)
                c.poly(TT([(cx_t - 6.2, SHOULDER_Y + 7), (cx_t + 6.2, SHOULDER_Y + 7),
                           (cx_t + 4.4, SHOULDER_Y + 16), (cx_t - 4.4, SHOULDER_Y + 16)]), dasi, ow * .78, OUT)
            for sg in (-1, 1):
                panel_c = gelap(kemeja, 0.10) if (sg < 0 if turn >= 0.25 else sg > 0) else kemeja
                outer_m = (1.0 - 0.18 * turn) if sg > 0 else (1.0 + 0.08 * turn)
                # bahu blazer melandai bulat-mulus menyatu ke pangkal lengan (TIDAK ada sudut mencuat di luar lengan!)
                c.poly(TT([
                    (cx_t + sg * (nx - 2) * outer_m, SHOULDER_Y - 10),
                    (sg * 22 * bw, SHOULDER_Y - 4),
                    (sg * 29 * bw, SHOULDER_Y + 4),
                    (sg * 31 * bw, SHOULDER_Y + 16),
                    (sg * 32 * bw, SHOULDER_Y + 44),
                    (sg * 32 * hipb, hy - 32),
                    (sg * 31 * hipb, hy - 10),
                    (sg * 20 * hipb, hy - 8),
                    (cx_t + sg * 2, hy - 9),
                    (cx_t, btn_y),
                ]), panel_c, ow, oc_w)
                c.poly(TT([
                    (cx_t + sg * (nx - 2) * outer_m, SHOULDER_Y - 10),
                    (cx_t + sg * (nx + 12 * bw * 0.68) * outer_m, SHOULDER_Y + 10),
                    (cx_t + sg * (nx + 7.5 * bw * 0.68) * outer_m, SHOULDER_Y + 20),
                    (cx_t + sg * (nx + 12.5 * bw * 0.68) * outer_m, SHOULDER_Y + 28),
                    (cx_t + sg * 1.5, btn_y),
                    (cx_t + sg * (nx - 3.5) * outer_m, SHOULDER_Y + 16),
                ]), lap_c, ow * .78, oc_w)
                c.line(TT([(cx_t + sg * (nx + 7.5 * bw * 0.68) * outer_m, SHOULDER_Y + 20),
                           (cx_t + sg * (nx - 3.5) * outer_m, SHOULDER_Y + 15)]), oc_w, ow * .60)
            c.ell(*T(cx_t, btn_y + 6), 2.8 * s, 2.8 * s, oc_w)
            if hy - btn_y > 28:
                c.ell(*T(cx_t, btn_y + 19), 2.6 * s, 2.6 * s, oc_w)
        else:
            # torso dengan BAHU MIRING ALAMI KE ARAH LEHER (segitiga/trapesium lembut, BUKAN kotak datar terpotong!)
            top_w = 34.0 * bw
            bot_w = 33.0 * hipb
            y_top = SHOULDER_Y - 2.0
            y_bot = hy - 8.0
            nk_w = 16.0 * (0.72 if side_prof else 1.0)
            torso_pts = [
                (-nk_w, y_top - 8), (0, y_top - 4), (nk_w, y_top - 8),
                (top_w * 0.66, y_top - 1), (top_w, y_top + 12),
                (bot_w * 1.01, y_bot - 18), (bot_w * 0.96, y_bot),
                (0, y_bot + 3), (-bot_w * 0.96, y_bot),
                (-bot_w * 1.01, y_bot - 18), (-top_w, y_top + 12), (-top_w * 0.66, y_top - 1),
            ]
            c.blob(TT(torso_pts), kemeja, ow, oc_w, n=5)
            # 2-band cel shading bersih
            if turn >= 0.25:
                c.poly(TT([
                    (-top_w + 3, y_top + 14), (-top_w * 0.66, y_top + 1),
                    (-top_w * 0.22, y_top - 2), (-bot_w * 0.18, y_bot - 1),
                    (-bot_w * 0.94, y_bot - 1), (-bot_w + 3, y_bot - 16),
                ]), gelap(kemeja, 0.11))
            else:
                c.poly(TT([
                    (top_w * 0.42, y_top - 1), (top_w * 0.72, y_top + 2),
                    (top_w - 2, y_top + 14), (bot_w - 2, y_bot - 16),
                    (bot_w * 0.94, y_bot - 1), (bot_w * 0.38, y_bot - 1),
                ]), gelap(kemeja, 0.10))
            c.blob(TT(torso_pts), None, ow, oc_w, n=5)
            # rompi rajut V-neck di atas kemeja (mengikuti kemiringan bahu alami!)
            if p.get("rompi"):
                rc = warna(p.get("rompi_warna"), (92, 118, 152))
                v_y = SHOULDER_Y + 34
                vest_pts = [
                    (-top_w * 0.88, y_top + 9), (-nk_w, y_top - 6), (cx_t, v_y), (nk_w, y_top - 6),
                    (top_w * 0.88, y_top + 9), (bot_w * 0.98, y_bot - 10), (bot_w * 0.92, y_bot + 2),
                    (-bot_w * 0.92, y_bot + 2), (-bot_w * 0.98, y_bot - 10),
                ]
                c.poly(TT(vest_pts), rc, 2.5 * s, oc_w)
                c.poly(TT([(top_w * 0.36, y_top + 4), (top_w * 0.86, y_top + 10), (bot_w * 0.94, y_bot), (bot_w * 0.36, y_bot)]),
                       gelap(rc, 0.14))
                c.poly(TT([(-bot_w * 0.94, y_bot - 10), (bot_w * 0.94, y_bot - 10),
                           (bot_w * 0.92, y_bot + 2), (-bot_w * 0.92, y_bot + 2)]), gelap(rc, 0.08), 2.0 * s, oc_w)
                for rx_r in (-0.72, -0.44, -0.16, 0.14, 0.44, 0.72):
                    c.line(TT([(bot_w * rx_r, y_bot - 9), (bot_w * rx_r, y_bot + 1)]), gelap(rc, 0.28), 1.5 * s)
                c.curve(TT([(-nk_w, y_top - 5), (cx_t, v_y + 2), (nk_w, y_top - 5)]), gelap(rc, 0.26), 2.4 * s)
                c.poly(TT(vest_pts), None, 2.5 * s, oc_w)
            # baju koko (kerah sanghai + bordir dada halus untuk Kakek)
            if p.get("koko"):
                c.poly(TT([(cx_t - 18, y_top - 8), (cx_t + 18, y_top - 8), (cx_t + 16, y_top + 6), (cx_t - 16, y_top + 6)]),
                       gelap(kemeja, 0.06), 2.4 * s, OUT)
                c.line(TT([(cx_t, y_top + 6), (cx_t, y_top + 56)]), gelap(kemeja, 0.26), 2.2 * s)
                for sg_k in (-1, 1):
                    c.line(TT([(cx_t + sg_k * 12, y_top + 14), (cx_t + sg_k * 12, y_top + 54)]), (186, 168, 134), 2.4 * s)
        if p.get("kemeja_garis"):
            gc = warna(p["kemeja_garis"], BIRU)
            for yy in (-220, -198, -176):
                if yy < hy - 14:
                    c.line(TT([(-33 * bw, yy), (33 * bw, yy)]), gc, 5.2 * s, False)
        if p.get("saku_dada") and not side_prof:
            # saku kemeja kiri (persis gambar 2 Arka)
            sx0, sx1, sy0, sy1 = cx_t + 16, cx_t + 42, SHOULDER_Y + 34, SHOULDER_Y + 62
            c.poly(TT([(sx0, sy0), (sx1, sy0), (sx1, sy1 - 5), ((sx0 + sx1) / 2, sy1), (sx0, sy1 - 5)]),
                   terang(kemeja, 0.08), ow * .65, OUT)
        if p.get("sabuk") and not p.get("jaket"):
            sbc = warna(p["sabuk"], (72, 62, 66))
            bot_w = 33.0 * hipb
            c.poly(TT([(-bot_w * 0.94, hy - 16), (bot_w * 0.94, hy - 16),
                       (bot_w * 0.94, hy - 2), (-bot_w * 0.94, hy - 2)]), sbc, ow * .72, OUT)
            c.poly(TT([(cx_t - 9, hy - 17), (cx_t + 9, hy - 17),
                       (cx_t + 9, hy - 1), (cx_t - 9, hy - 1)]), (196, 202, 214), ow * .68, OUT)
        if p.get("perisai_dada"):
            by = SHOULDER_Y + 46
            c.poly(TT([(cx_t, by - 20), (cx_t + 20, by - 12), (cx_t + 16, by + 9), (cx_t, by + 22), (cx_t - 16, by + 9), (cx_t - 20, by - 12)]), PUTIH, ow * .8, OUT)
            c.line(TT([(cx_t, by - 9), (cx_t, by + 9)]), BIRU, 5.0 * s, False)
            c.line(TT([(cx_t - 9, by), (cx_t + 9, by)]), BIRU, 5.0 * s, False)
        # ---- leher (pendek & rapi di antara bahu dan dagu, memberi proporsi mirip 3D-stickman)
        if not p.get("hijab") and not p.get("kaos_chibi") and not p.get("sweater"):
            neck_c = kulit
            nx_c = 4.0 * turn
            c.poly(TT([(nx_c - 13.5, SHOULDER_Y - 24), (nx_c + 13.5, SHOULDER_Y - 24),
                       (nx_c + 14.5, SHOULDER_Y + 6), (nx_c, SHOULDER_Y + 10), (nx_c - 14.5, SHOULDER_Y + 6)]),
                   neck_c, ow * .82, OUT)
            c.poly(TT([(nx_c - 12.5, SHOULDER_Y - 22), (nx_c + 12.5, SHOULDER_Y - 22),
                       (nx_c + 12.5, SHOULDER_Y - 8), (nx_c - 12.5, SHOULDER_Y - 12)]),
                   gelap(neck_c, 0.14))
        # krah + dasi (dasi kupu-kupu menggantikan krah/dasi biasa)
        def _draw_bowtie(bc):
            by = SHOULDER_Y + (14 if p.get("kaos_chibi") else 11)
            k_bt = 1.38 if p.get("kaos_chibi") else 1.15
            lw_b = 19.0 * k_bt * (1.0 - 0.10 * turn)
            rw_b = 19.0 * k_bt * (1.0 - 0.22 * turn)
            hh_b = 10.0 * k_bt
            c.blob(TT([(cx_t - 3, by - 3), (cx_t - lw_b, by - hh_b), (cx_t - lw_b - 2.5, by), (cx_t - lw_b, by + hh_b), (cx_t - 3, by + 3)]), bc, ow * .78, OUT, n=4)
            c.blob(TT([(cx_t + 3, by - 3), (cx_t + rw_b, by - hh_b), (cx_t + rw_b + 2.5, by), (cx_t + rw_b, by + hh_b), (cx_t + 3, by + 3)]), gelap(bc, .10), ow * .78, OUT, n=4)
            c.ell(*T(cx_t, by), 7.8 * s, 7.8 * s, gelap(bc, .16), ow * .75, OUT)

        if not p.get("blazer"):
            # tampilkan kerah kemeja putih di bawah dasi kupu bila krah=True (gaya smart student Ghibli)
            if p.get("krah", True):
                c.poly(TT([(cx_t - 4, SHOULDER_Y - 2), (cx_t - 22, SHOULDER_Y - 1), (cx_t - 13, SHOULDER_Y + 20)]), PUTIH, ow * .78, OUT)
                c.poly(TT([(cx_t + 4, SHOULDER_Y - 2), (cx_t + 22, SHOULDER_Y - 1), (cx_t + 13, SHOULDER_Y + 20)]), PUTIH, ow * .78, OUT)
            if p.get("dasi_kupu"):
                _draw_bowtie(warna(p.get("dasi"), HITAM))
            elif dasi:
                c.poly(TT([(cx_t - 4.5, SHOULDER_Y + 17), (cx_t + 4.5, SHOULDER_Y + 17),
                           (cx_t + 10.5, SHOULDER_Y + 58), (cx_t, SHOULDER_Y + 74), (cx_t - 10.5, SHOULDER_Y + 58)]), dasi, ow * .8, OUT)
                c.poly(TT([(cx_t - 7.0, SHOULDER_Y + 8), (cx_t + 7.0, SHOULDER_Y + 8),
                           (cx_t + 5.0, SHOULDER_Y + 17), (cx_t - 5.0, SHOULDER_Y + 17)]), dasi, ow * .8, OUT)
                if p.get("dasi_klip"):
                    c.line(TT([(cx_t - 7.5, SHOULDER_Y + 46), (cx_t + 7.5, SHOULDER_Y + 46)]), (192, 198, 214), 4.0 * s)
            elif p.get("kancing", True):
                for yy in (-224, -202, -180):
                    if yy < hy - 16:
                        c.ell(*T(cx_t, yy), 3.1 * s, 3.1 * s, OUT)
        elif p.get("dasi_kupu"):
            _draw_bowtie(warna(p.get("dasi"), HITAM))
        if st.get("tali_ransel"):
            for sgn in (-1, 1):
                c.line(TT([(sgn * 25 * bw, SHOULDER_Y), (sgn * 25 * bw, hy - 12)]), warna(st["ransel"], UNGU) if not isinstance(st["ransel"], bool) else UNGU, 8.5 * s, False)

        # ---- lengan depan / normal (di depan torso, DI BAWAH drape lilitan hijab agar bahu tidak menimpa kerudung!)
        for side, key, a, e, hk in mid_arms:
            hands[side] = self._arm(c, T, s, fl, key, a, e, hk, kemeja, ow, dy, turn)

        # ---- Layer 4: drape lilitan hijab di atas bahu & dada (DI ATAS pangkal lengan, persis referensi chibi hijab!)
        if p.get("hijab"):
            hj, hjd = warna(p["hijab"]), warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .18))
            oc_h = (68, 44, 34) if p.get("hijab_gaya") == "modern" else OUT
            hx_sh = -6.0 * turn
            hm = p.get("hijab_model", "pashmina")
            if p.get("hijab_gaya") == "modern":
                if hm == "syari":
                    # hijab syar'i chibi anggun jatuh lebar melengkung menutup dada & bahu (Ibu)
                    drape = [
                        (hx_sh - 86, -310), (hx_sh - 90, -250), (hx_sh - 76, -206),
                        (hx_sh - 38, -184), (cx_t * 0.3, -180),
                        (hx_sh + 38, -184), (hx_sh + 76, -206),
                        (hx_sh + 90, -250), (hx_sh + 86, -310), (hx_sh, -346),
                    ]
                    c.blob(TT(drape), hj, 2.8 * s, oc_h, n=7)
                    c.curve(TT([(hx_sh - 60, -238), (hx_sh - 18, -210), (hx_sh + 34, -220)]), hjd, 2.2 * s)
                    c.curve(TT([(hx_sh - 46, -264), (cx_t * 0.25, -242), (hx_sh + 52, -260)]), hjd, 2.4 * s)
                elif hm == "bergo":
                    # jilbab sekolah bergo chibi lembut melengkung manis di bahu (Sari)
                    drape = [
                        (hx_sh - 84, -310), (hx_sh - 84, -258), (hx_sh - 64, -226),
                        (hx_sh - 28, -212), (cx_t * 0.3, -208),
                        (hx_sh + 28, -212), (hx_sh + 64, -226),
                        (hx_sh + 84, -258), (hx_sh + 84, -310), (hx_sh, -346),
                    ]
                    c.blob(TT(drape), hj, 2.8 * s, oc_h, n=7)
                    c.curve(TT([(hx_sh - 56, -244), (cx_t * 0.3, -228), (hx_sh + 56, -244)]), hjd, 2.2 * s)
                elif hm == "segiempat":
                    # hijab segi empat chibi rapi dengan lipatan simetris & bros mungil (Bu Guru)
                    drape = [
                        (hx_sh - 82, -310), (hx_sh - 82, -256), (hx_sh - 62, -222),
                        (hx_sh - 22, -200), (cx_t * 0.3, -194),
                        (hx_sh + 22, -200), (hx_sh + 62, -222),
                        (hx_sh + 82, -256), (hx_sh + 82, -310), (hx_sh, -346),
                    ]
                    c.blob(TT(drape), hj, 2.8 * s, oc_h, n=7)
                    c.curve(TT([(hx_sh - 54, -246), (cx_t * 0.25, -216), (hx_sh + 50, -244)]), hjd, 2.4 * s)
                    c.curve(TT([(hx_sh - 34, -262), (cx_t * 0.25, -240), (hx_sh + 36, -260)]), hjd, 2.0 * s)
                    c.ell(*T(cx_t * 0.3, -230), 5.2 * s, 5.2 * s, (246, 224, 152), 1.8 * s, oc_h)
                else:
                    # pashmina lilit chibi persis referensi user: selendang lembut melengkung asimetris di dada & leher!
                    drape = [
                        (hx_sh - 82, -310), (hx_sh - 80, -258), (hx_sh - 56, -224),
                        (hx_sh - 12, -206), (hx_sh + 34, -216), (hx_sh + 76, -238),
                        (hx_sh + 88, -274), (hx_sh + 82, -316), (hx_sh, -346),
                    ]
                    c.blob(TT(drape), hj, 2.8 * s, oc_h, n=7)
                    # bayangan lembut di bagian bawah lipatan lilitan pashmina
                    c.curve(TT([(hx_sh - 56, -248), (hx_sh - 10, -222), (hx_sh + 54, -242), (hx_sh + 78, -268)]), hjd, 2.6 * s)
                    c.curve(TT([(hx_sh - 44, -266), (hx_sh - 4, -244), (hx_sh + 46, -258)]), hjd, 2.1 * s)
                    c.curve(TT([(hx_sh - 36, -232), (hx_sh - 10, -214), (hx_sh + 24, -222)]), hjd, 1.8 * s)
            else:
                c.blob(TT([(hx_sh - 98, -346), (hx_sh - 106, -288), (hx_sh - 88, -236), (hx_sh - 46, -206), (cx_t * 0.4, -194), (hx_sh + 46, -206), (hx_sh + 88, -236), (hx_sh + 106, -288), (hx_sh + 98, -346), (hx_sh, -394)]),
                       hj, ow, OUT, n=7)
                c.curve(TT([(hx_sh - 62, -244), (hx_sh - 26, -228), (cx_t * 0.4, -218)]), hjd, 4.4 * s)
                c.curve(TT([(hx_sh + 62, -244), (hx_sh + 26, -228), (cx_t * 0.4, -218)]), hjd, 4.4 * s)
                c.curve(TT([(hx_sh - 84, -274), (hx_sh - 52, -250)]), hjd, 3.6 * s)
                c.curve(TT([(hx_sh + 84, -274), (hx_sh + 52, -250)]), hjd, 3.6 * s)
            if dasi and not p.get("dasi_kupu"):
                c.poly(TT([(cx_t - 3.8, -198), (cx_t + 3.8, -198), (cx_t + 8.5, -170), (cx_t, -158), (cx_t - 8.5, -170)]), dasi, ow * .7, oc_h)
                c.poly(TT([(cx_t - 5.5, -208), (cx_t + 5.5, -208), (cx_t + 4.0, -198), (cx_t - 4.0, -198)]), dasi, ow * .7, oc_h)

        # ---- kepala
        self._head(c, st, T, s, fl, ow, turn)

        # ---- lengan terangkat / dekat wajah (di depan kepala & rambut)
        for side, key, a, e, hk in front_arms:
            hands[side] = self._arm(c, T, s, fl, key, a, e, hk, kemeja, ow, dy, turn)

        # ---- benda di tangan
        return hands

    # ------------------------------------------------------------ kaki
    def _legs(self, st, T, sit, turn=0.0):
        stance = st.get("legs", "stand")
        ph, amp = st.get("phase", 0.0), st.get("amp", 0.0)
        side_prof = turn >= 0.80
        kl = float(self.p.get("kaki_lebar", 1.15)) * (0.28 if side_prof else (1.0 - 0.24 * turn))
        hy = float(self.p.get("hip_y", -144.0))
        feet, knees, hips = [], [], []
        for sgn in (-1, 1):
            hx = sgn * (3.5 if side_prof else 17.5 * kl)
            fx, fy = sgn * (10.0 if side_prof else 20.5 * kl), (-4.5 * turn if sgn < 0 else 0.0)
            knee_bend = 0.0
            if stance == "walk" and amp > 0.01:
                q = ph + (0 if sgn < 0 else math.pi)
                if side_prof:
                    # langkah samping sejati: pinggul sejajar, kaki ayun maju-mundur + lutut menekuk ke depan (+x)
                    hx = sgn * 3.0
                    stride = math.sin(q) * 0.48 * amp
                    fx = hx + math.sin(stride) * 105.0
                    lift = max(0.0, -math.cos(q)) * 18.0 * amp
                    fy = -lift + (-3.0 if sgn < 0 else 0.0)
                    knee_bend = (14.0 + 16.0 * max(0.0, math.sin(q))) * min(1.0, amp)
                else:
                    hx = sgn * 17.5 * kl * (1.0 - 0.18 * min(1.0, amp))
                    stride = math.sin(q) * 0.42 * amp
                    fx = hx + math.sin(stride) * 118.0
                    fy = -max(0.0, -math.cos(q)) * 16.0 * amp
            elif stance == "wide":
                fx = sgn * 48 * kl
            hipw = T(hx, hy)
            f_stand, f_sit = T(fx, fy, True), T(hx + 92, 0.0, True)
            foot = (lerp(f_stand[0], f_sit[0], sit), lerp(f_stand[1], f_sit[1], sit))
            # lutut sedikit menekuk ke arah maju (+x lokal) saat side-profile berjalan agar langkah alami
            kx_stand = (hx + fx) * 0.5 + knee_bend
            ky_stand = (hy + fy) * 0.5
            k_stand = T(kx_stand, ky_stand)
            k_sit = T(hx + 84, hy + SIT_DROP, True)
            knee = (lerp(k_stand[0], k_sit[0], sit), lerp(k_stand[1], k_sit[1], sit))
            feet.append(foot)
            knees.append(knee)
            hips.append(hipw)
        return feet, knees, hips

    # ------------------------------------------------------------ lengan
    def _arm(self, c, T, s, fl, sgn, a, e, hk, sleeve, ow, dy, turn=0.0):
        ar, br = math.radians(a), math.radians(a + e)
        # tangan masuk saku celana saat pose diam/santai (persis gaya referensi chibi)
        saku = bool(self.p.get("tangan_saku")) and hk == "m" and turn < 0.25 and a <= 22 and -12 <= e <= 20
        if saku:
            a, e = 10.0, -26.0
            ar, br = math.radians(a), math.radians(a + e)
        elif self.p.get("tunik_chibi") and hk == "m" and turn < 0.25 and a <= 14 and e < 0:
            # pada tunik A-line chibi, lengan saat diam jatuh lembut mengikuti kemiringan sisi tunik (persis referensi!)
            a, e = 17.0, -4.0
            ar, br = math.radians(a), math.radians(a + e)
        bahu = float(self.p.get("bahu_x", 47.0)) - 3.5
        sh_drop = 19.0 if (self.p.get("lengan_panjang") and not self.p.get("tunik_chibi")) else 14.0
        side_prof = turn >= 0.80
        if side_prof:
            # side-profile: kedua bahu berada di dekat sumbu tengah tubuh, lengan ayun maju-mundur (+x/-x)
            bahu_x = -3.0 if sgn < 0 else 2.0
            sh = (bahu_x, SHOULDER_Y + sh_drop)
            el = (sh[0] + math.sin(ar) * UP_ARM, sh[1] + math.cos(ar) * UP_ARM)
            hd = (el[0] + math.sin(br) * FORE_ARM, el[1] + math.cos(br) * FORE_ARM)
        else:
            if turn >= 0.25:
                bahu_x = sgn * bahu * (0.62 if sgn < 0 else 0.72) + (6.0 * turn if sgn > 0 else 10.0 * turn)
                a_eff = a if sgn > 0 else (a + 6.0 * turn)
                ar, br = math.radians(a_eff), math.radians(a_eff + e)
            else:
                bahu_x = sgn * (bahu - (2.5 if self.p.get("lengan_panjang") else 0.0))
            sh = (bahu_x, SHOULDER_Y + sh_drop)
            el = (sh[0] + sgn * math.sin(ar) * UP_ARM, sh[1] + math.cos(ar) * UP_ARM)
            hd = (el[0] + sgn * math.sin(br) * FORE_ARM, el[1] + math.cos(br) * FORE_ARM)
        S, E, H = T(*sh), T(*el), T(*hd)
        tebal = bool(self.p.get("lengan_tebal", True))
        lb = float(self.p.get("lengan_besar", 0.94)) if tebal else 1.0
        tb = float(self.p.get("tangan_besar", 0.94))
        skin = warna(self.p.get("kulit"), PUTIH)
        slv_c = gelap(sleeve, 0.12) if (turn >= 0.25 and sgn < 0) else sleeve
        skin_c = gelap(skin, 0.08) if (turn >= 0.25 and sgn < 0) else skin
        arm_ow = (2.6 if self.p.get("outline_hangat") else 3.6) * s
        arm_oc = (62, 44, 38) if self.p.get("outline_hangat") else OUT
        # lengan kartun ramping & halus (menyatu mulus dari kemiringan bahu tanpa tonjolan terpotong!)
        if self.p.get("lengan_panjang"):
            arm_w = (19.2 if self.p.get("sweater") else 16.4) * lb
            if saku:
                c.curve([S, E, H], arm_oc, (arm_w + 2 * 2.6) * s, n=6)
                c.curve([S, E, H], slv_c, arm_w * s, n=6)
                c.ell(*S, arm_w * 0.48 * s, arm_w * 0.48 * s, slv_c)
            elif self.p.get("tunik_chibi"):
                oc_a = (68, 44, 34)
                dx, dy_ = H[0] - E[0], H[1] - E[1]
                dl = max(1e-5, math.hypot(dx, dy_))
                ux, uy = dx / dl, dy_ / dl
                r_hand = 11.5 * tb * s
                H_cuff = (H[0] - ux * (r_hand + 10.5 * s), H[1] - uy * (r_hand + 10.5 * s))
                H_wrist = (H[0] - ux * (r_hand + 1.0 * s), H[1] - uy * (r_hand + 1.0 * s))
                aw_t = 18.8 * lb
                c.curve([S, E, H_cuff], oc_a, (aw_t + 2 * 2.6) * s, n=6)
                c.curve([S, E, H_cuff], slv_c, aw_t * s, n=6)
                c.ell(*S, aw_t * 0.48 * s, aw_t * 0.48 * s, slv_c)
                c.tube(H_cuff, H_wrist, (aw_t - 2.6) * s, gelap(slv_c, 0.05), 2.4 * s, oc_a)
            elif self.p.get("sweater"):
                dx, dy_ = H[0] - E[0], H[1] - E[1]
                dl = max(1e-5, math.hypot(dx, dy_))
                ux, uy = dx / dl, dy_ / dl
                nx, ny = -uy, ux
                r_hand = 10.5 * tb * s
                H_cuff = (H[0] - ux * (r_hand + 10.0 * s), H[1] - uy * (r_hand + 10.0 * s))
                H_wrist = (H[0] - ux * (r_hand + 1.0 * s), H[1] - uy * (r_hand + 1.0 * s))
                if self.p.get("anak_ghibli"):
                    # lengan sweater oversized menggelembung empuk persis referensi Ghibli user!
                    d_se_x, d_se_y = E[0] - S[0], E[1] - S[1]
                    l_se = max(1e-5, math.hypot(d_se_x, d_se_y))
                    n1x, n1y = -d_se_y / l_se, d_se_x / l_se
                    if (n1x * sgn * fl) < 0:
                        n1x, n1y = -n1x, -n1y
                    r_sh = 17.5 * s
                    r_el_out = 26.5 * s
                    r_el_in = 15.5 * s
                    r_cf = 15.5 * s
                    M_up = (lerp(S[0], E[0], 0.55), lerp(S[1], E[1], 0.55))
                    M_lo = (lerp(E[0], H_cuff[0], 0.52), lerp(E[1], H_cuff[1], 0.52))
                    puffy = [
                        (S[0] - n1x * r_sh * 0.72, S[1] - n1y * r_sh * 0.72),
                        (S[0] + n1x * r_sh, S[1] + n1y * r_sh),
                        (M_up[0] + n1x * (r_el_out * 0.96), M_up[1] + n1y * (r_el_out * 0.96)),
                        (E[0] + n1x * r_el_out, E[1] + n1y * r_el_out),
                        (M_lo[0] + n1x * (r_el_out * 0.94), M_lo[1] + n1y * (r_el_out * 0.94)),
                        (H_cuff[0] + n1x * r_cf, H_cuff[1] + n1y * r_cf),
                        (H_cuff[0] - n1x * r_cf * 0.85, H_cuff[1] - n1y * r_cf * 0.85),
                        (M_lo[0] - n1x * r_el_in, M_lo[1] - n1y * r_el_in),
                        (E[0] - n1x * r_el_in, E[1] - n1y * r_el_in),
                    ]
                    c.blob(puffy, slv_c, 2.4 * s, arm_oc, n=6)
                    # lipatan kain siku lembut & tutup bahu menyatu mulus
                    c.curve([
                        (E[0] - n1x * r_el_in * 0.75, E[1] - n1y * r_el_in * 0.75),
                        (E[0] + n1x * 4.0 * s, E[1] + n1y * 4.0 * s),
                        (M_lo[0] + n1x * 6.0 * s, M_lo[1] + n1y * 6.0 * s),
                    ], gelap(slv_c, 0.24), 1.8 * s)
                    c.ell(*S, r_sh * 0.85, r_sh * 0.80, slv_c)
                    c.tube(H_cuff, H_wrist, r_cf * 1.45, gelap(slv_c, 0.06), 2.2 * s, arm_oc)
                    for rk in (-0.34, 0.0, 0.34):
                        p0_r = (H_cuff[0] + nx * rk * (r_cf * 0.85), H_cuff[1] + ny * rk * (r_cf * 0.85))
                        p1_r = (H_wrist[0] + nx * rk * (r_cf * 0.78), H_wrist[1] + ny * rk * (r_cf * 0.78))
                        c.line([p0_r, p1_r], gelap(slv_c, 0.28), 1.4 * s)
                else:
                    c.curve([S, E, H_cuff], arm_oc, (arm_w + 2 * 2.6) * s, n=6)
                    c.curve([S, E, H_cuff], slv_c, arm_w * s, n=6)
                    c.ell(*S, arm_w * 0.50 * s, arm_w * 0.50 * s, slv_c)
                    c.tube(H_cuff, H_wrist, (arm_w - 4.2) * s, gelap(slv_c, 0.06), 2.4 * s, arm_oc)
                    for rk in (-0.35, 0.0, 0.35):
                        p0_r = (H_cuff[0] + nx * rk * (arm_w * 0.38 * s), H_cuff[1] + ny * rk * (arm_w * 0.38 * s))
                        p1_r = (H_wrist[0] + nx * rk * (arm_w * 0.34 * s), H_wrist[1] + ny * rk * (arm_w * 0.34 * s))
                        c.line([p0_r, p1_r], gelap(slv_c, 0.28), 1.5 * s)
            elif self.p.get("manset") or self.p.get("blazer"):
                dx, dy_ = H[0] - E[0], H[1] - E[1]
                dl = max(1e-5, math.hypot(dx, dy_))
                ux, uy = dx / dl, dy_ / dl
                r_hand = 14.0 * tb * s
                c0 = (H[0] - ux * (r_hand + 11.5 * s), H[1] - uy * (r_hand + 11.5 * s))
                c1 = (H[0] - ux * (r_hand + 1.5 * s), H[1] - uy * (r_hand + 1.5 * s))
                c.tube(c0, c1, (arm_w - 3.2) * s, PUTIH, 2.4 * s, arm_oc)
                H_slv = (H[0] - ux * (r_hand + 17.5 * s), H[1] - uy * (r_hand + 17.5 * s))
                c.line([S, E, H_slv], arm_oc, (arm_w + 2 * 2.6) * s)
                c.line([S, E, H_slv], slv_c, arm_w * s)
                # tutup pangkal bahu jas menyatu mulus ke lereng pundak (nol sudut tajam!)
                c.ell(*T(bahu_x - sgn * 3.5, SHOULDER_Y + sh_drop - 1.5), arm_w * 0.52 * s, arm_w * 0.48 * s, slv_c)
            else:
                c.line([S, E, H], arm_oc, (arm_w + 2 * 2.6) * s)
                c.line([S, E, H], slv_c, arm_w * s)
                c.ell(*S, arm_w * 0.48 * s, arm_w * 0.48 * s, slv_c)
        else:
            if tebal:
                arm_w = 14.2 * lb
                S_arm = T(sh[0] + (el[0] - sh[0]) * 0.24, sh[1] + (el[1] - sh[1]) * 0.24) if not self.p.get("lengan_gulung") else S
                if saku:
                    c.curve([S_arm, E, H], OUT, (arm_w + 2 * 3.8) * s, n=6)
                    c.curve([S_arm, E, H], skin_c, arm_w * s, n=6)
                else:
                    c.line([S_arm, E, H], OUT, (arm_w + 2 * 3.8) * s)
                    c.line([S_arm, E, H], skin_c, arm_w * s)
            else:
                c.line([S, E, H], OUT, 6.0 * s)
            # lengan pendek rapi ala Kribo untuk semua karakter lengan pendek; lengan gulung untuk Arka
            sl_k = 0.72 if self.p.get("lengan_gulung") else 0.42
            sl = (sh[0] + (el[0] - sh[0]) * sl_k, sh[1] + (el[1] - sh[1]) * sl_k)
            slv_w = (19.5 * lb if self.p.get("lengan_gulung") else (17.5 * lb if tebal else 16.0)) * s
            if tebal and not self.p.get("lengan_gulung"):
                self._sleeve_chibi(c, T, s, sh, el, slv_c, arm_ow)
            else:
                c.tube(S, T(*sl), slv_w, slv_c, arm_ow)
            if self.p.get("lengan_gulung"):
                # lipatan manset gulung di ujung lengan siku
                sl2 = (sh[0] + (el[0] - sh[0]) * (sl_k + 0.14), sh[1] + (el[1] - sh[1]) * (sl_k + 0.14))
                c.tube(T(*sl), T(*sl2), slv_w * 1.08, terang(slv_c, 0.10), arm_ow * .85)
        # tangan berjari kartun 2D rapi (2-pass outline menyatu antara telapak & jari)
        dirv = (H[0] - E[0], H[1] - E[1])
        ang = math.atan2(dirv[1], dirv[0])
        if saku:
            # pergelangan masuk ke saku celana: tutup tangan dengan kain + garis bukaan saku miring
            bc = warna(self.p.get("bawah_warna"), (160, 164, 170))
            hx_, hy_ = hd
            pk = [(hx_ - sgn * 11, hy_ - 4), (hx_ + sgn * 11, hy_ - 10), (hx_ + sgn * 10, hy_ + 9), (hx_ - sgn * 10, hy_ + 9)]
            c.blob([T(*q) for q in pk], bc, 0, n=3)
            c.curve([T(hx_ - sgn * 13, hy_ - 2), T(hx_, hy_ - 8), T(hx_ + sgn * 13, hy_ - 11)], OUT, 2.8 * s)
        else:
            self._hand(c, H, ang, s, tb, sgn, fl, hk, skin_c)
        return {"pos": H, "ang": ang, "elbow": E}

    def _sleeve_chibi(self, c, T, s, sh, el, col, ow_):
        """Lengan kaos pendek rapi lurus-halus (tidak ketekuk saat lengan turun maupun saat menunjuk!)."""
        dx, dy = el[0] - sh[0], el[1] - sh[1]
        l = max(1e-6, math.hypot(dx, dy))
        ux, uy = dx / l, dy / l
        nx, ny = -uy, ux
        if abs(sh[0] + nx) < abs(sh[0] - nx):
            nx, ny = -nx, -ny
        # pangkal lengan kaos membulat rapi di bahu, turun lurus ke manset tanpa garis tekukan di dada
        b_in = (sh[0] - ux * 8 - nx * 11, sh[1] - uy * 8 - ny * 8)
        b_out = (sh[0] - ux * 4 + nx * 12, sh[1] - uy * 4 + ny * 11)
        cf_out = (sh[0] + ux * 34 + nx * 17, sh[1] + uy * 34 + ny * 17)
        cf_in = (sh[0] + ux * 33 - nx * 11, sh[1] + uy * 33 - ny * 11)
        P = [T(*q) for q in (b_in, b_out, cf_out, cf_in)]
        c.poly(P, col)
        # tutup pangkal bahu dengan elips warna kaos agar sambungan bahu selalu bulat-rapi di segala sudut pose!
        c.ell(*T(sh[0] - ux * 3, sh[1] - uy * 2), 13.5 * s, 13.5 * s, col)
        c.line([P[1], P[2], P[3]], OUT, ow_)
        c.line([P[3], T(sh[0] + ux * 18 - nx * 11, sh[1] + uy * 18 - ny * 11)], OUT, ow_ * 0.85)
        lum = 0.299 * col[0] + 0.587 * col[1] + 0.114 * col[2]
        hem_c = terang(col, 0.15) if lum < 90 else gelap(col, 0.20)
        c.line([T(cf_out[0] - ux * 4.5, cf_out[1] - uy * 4.5),
                T(cf_in[0] - ux * 4.5, cf_in[1] - uy * 4.5)], hem_c, 1.8 * s)

    def _tunik_chibi(self, c, TT, s, kemeja, hy, turn, side_prof):
        """Tunik A-line chibi lembut (persis baju oranye referensi chibi hijab: jatuh panjang melebar di atas rok panjang!)."""
        k = 0.72 if side_prof else (1.0 - 0.10 * turn)
        yb = hy + 42.0
        oc_t = (68, 44, 34)
        pts = [
            (-28 * k, -252), (0, -248), (28 * k, -252),
            (46 * k, -238), (58 * k, -184), (70 * k, yb - 10),
            (68 * k, yb + 2), (28 * k, yb + 9), (0, yb + 11),
            (-28 * k, yb + 9), (-68 * k, yb + 2), (-70 * k, yb - 10),
            (-58 * k, -184), (-46 * k, -238),
        ]
        c.blob(TT(pts), kemeja, 2.8 * s, oc_t, n=5)
        # cel-shading lembut di sisi kanan & lipatan kain alami di tengah (persis referensi!)
        c.poly(TT([(22 * k, -246), (46 * k, -236), (68 * k, yb - 2), (28 * k, yb + 9), (30 * k, -180)]),
               gelap(kemeja, 0.13))
        c.curve(TT([(-22 * k, -210), (-12 * k, -168), (-24 * k, yb - 16)]), gelap(kemeja, 0.24), 1.9 * s)
        c.curve(TT([(26 * k, -200), (34 * k, -158), (42 * k, yb - 14)]), gelap(kemeja, 0.22), 1.8 * s)
        c.blob(TT(pts), None, 2.8 * s, oc_t, n=5)

    def _sweater_ghibli(self, c, TT, s, kemeja, kulit, hy, turn, side_prof):
        """Sweater rajut Studio Ghibli (persis referensi user: kerah rib bergaris, bahu jatuh lembut, bodi empuk gemoy, pinggang rib!)."""
        is_ag = bool(self.p.get("anak_ghibli"))
        k = (0.76 if side_prof else (1.0 - 0.06 * turn)) * (1.20 if is_ag else 1.0)
        yb = hy - (0.0 if is_ag else 4.0)
        oc_f = (66, 48, 40)
        # leher pendek hangat + bayangan dagu
        neck_pts = [(-15.5, -276), (15.5, -276), (17.0, -248), (0, -242), (-17.0, -248)]
        c.poly(TT(neck_pts), kulit, 2.3 * s, oc_f)
        c.poly(TT([(-15.0, -274), (15.0, -274), (15.5, -256), (-2, -258), (-15.0, -261)]), gelap(kulit, 0.14))
        # bodi sweater rajut bervolume & membulat lembut (oversized gemoy bila anak_ghibli!)
        pts = [
            (-22 * k, -260), (0, -248), (22 * k, -260),
            (48 * k, -246), (59 * k, -224), (62 * k, -184),
            (58 * k, yb - 12), (52 * k, yb + 4),
            (0, yb + 11), (-52 * k, yb + 4), (-58 * k, yb - 12),
            (-62 * k, -184), (-59 * k, -224), (-48 * k, -246),
        ]
        c.blob(TT(pts), kemeja, 2.5 * s, oc_f, n=6)
        # shading cel hangat di sisi kanan & bawah sweater
        c.poly(TT([(20 * k, -248), (48 * k, -242), (59 * k, -206), (55 * k, yb - 6),
                   (22 * k, yb + 8), (34 * k, -180)]), gelap(kemeja, 0.13))
        # rib pinggang sweater rajut dengan garis vertikal halus
        c.poly(TT([(-54 * k, yb - 13), (54 * k, yb - 13), (50 * k, yb + 5), (0, yb + 10), (-50 * k, yb + 5)]),
               gelap(kemeja, 0.05), 2.2 * s, oc_f)
        for rx_ in (-0.76, -0.52, -0.28, -0.04, 0.22, 0.48, 0.74):
            c.line(TT([(52 * k * rx_, yb - 11), (49 * k * rx_, yb + 4)]), gelap(kemeja, 0.26), 1.5 * s)
        # lipatan kain alami lembut di dada & pinggang
        c.curve(TT([(-34 * k, -210), (-26 * k, -182), (-32 * k, -156)]), gelap(kemeja, 0.24), 1.8 * s)
        c.curve(TT([(34 * k, -204), (24 * k, -176), (30 * k, -152)]), gelap(kemeja, 0.24), 1.8 * s)
        # kerah rajut rib bundar tebal bergaris-garis (persis gambar referensi!)
        collar_pts = [
            (-24 * k, -262), (-12 * k, -250), (0, -246), (12 * k, -250), (24 * k, -262),
            (28 * k, -248), (14 * k, -234), (0, -230), (-14 * k, -234), (-28 * k, -248),
        ]
        c.blob(TT(collar_pts), gelap(kemeja, 0.04), 2.2 * s, oc_f, n=5)
        for cx_r in (-18, -10, -2, 6, 14, 20):
            c.line(TT([(cx_r * k, -256), (cx_r * k * 1.06, -238)]), gelap(kemeja, 0.28), 1.4 * s)
        c.blob(TT(pts), None, 2.5 * s, oc_f, n=6)

    def _kaos_chibi(self, c, TT, s, kemeja, kulit, hy, turn, side_prof):
        """Kaos rapi bersih tanpa garis ketekuk di dada/pinggang + leher pendek mungil."""
        k = 0.70 if side_prof else (1.0 - 0.10 * turn)
        yb = hy - 18.0
        oc_f = (74, 52, 46)
        # leher pendek mungil dengan bayangan dagu hangat
        neck_pts = [(-14.0, -274), (14.0, -274), (15.0, -250), (0, -245), (-15.0, -250)]
        c.poly(TT(neck_pts), kulit, 2.6 * s, oc_f)
        c.poly(TT([(-13.5, -272), (13.5, -272), (14.0, -257), (-2, -259), (-13.5, -262)]), (228, 160, 146))
        # bodi kaos bersih-rapi: bahu mulus dan sisi badan lurus-halus (TIDAK melekuk/ketekuk!)
        pts = [
            (-19 * k, -256), (0, -247), (19 * k, -256),
            (44 * k, -251), (52 * k, -238), (52 * k, -206),
            (52 * k, yb - 4), (32 * k, yb + 2),
            (0, yb + 3), (-32 * k, yb + 2), (-52 * k, yb - 4),
            (-52 * k, -206), (-52 * k, -238), (-44 * k, -251),
        ]
        c.blob(TT(pts), kemeja, 3.2 * s, OUT, n=6)
        # shading cel halus di sisi kanan kaos (tanpa garis lipatan ketekuk di dada!)
        c.poly(TT([(26 * k, -253), (44 * k, -250), (51 * k, -237), (51 * k, yb - 5),
                   (36 * k, yb + 1), (34 * k, -200)]), gelap(kemeja, 0.18))
        lum = 0.299 * kemeja[0] + 0.587 * kemeja[1] + 0.114 * kemeja[2]
        rib = terang(kemeja, 0.16) if lum < 90 else gelap(kemeja, 0.18)
        c.curve(TT([(-20 * k, -255), (0, -244), (20 * k, -255)]), rib, 2.8 * s)
        c.blob(TT(pts), None, 3.2 * s, OUT, n=6)

    def _hair_back_ref(self, c, HH, s, hc, sh):
        """Kembalikan bentuk rambut terbaik pilihan user (af_cy=-44, ikal bulat mengembang & sulur helai lepas)."""
        oc_h = (16, 12, 14)
        ow_h = 2.6 * s
        af_cy = -44
        c_deep = (14, 10, 12)
        c_mid = (78, 54, 46)
        c_bright = (128, 94, 80)
        c_fine = (168, 130, 114)
        outer_puffs = []
        dr_pat = (0, 8, -1, 10, 3, 11, 0, 9, 5, 12, 1, 10, 4, 12, 0, 9, 5, 11, 1, 10, 3, 9, -1, 6)
        pr_pat = (21, 25, 21, 26, 23, 27, 22, 26, 24, 27, 22, 26, 24, 27, 22, 26, 24, 27, 23, 26, 21, 25, 21, 20)
        for i in range(24):
            a = 142 + (398 - 142) * i / 23.0
            rad_a = math.radians(a)
            px = sh + math.cos(rad_a) * (136 + dr_pat[i])
            py = af_cy + math.sin(rad_a) * (114 + dr_pat[i])
            outer_puffs.append((px, py, pr_pat[i], a))

        # pass 1: sulur-sulur helai ikal lepas mencuat di luar tepi afro
        for i in range(22):
            a = 144 + (396 - 144) * i / 21.0
            rad_a = math.radians(a)
            dist_w = 152 + (8 if i % 2 == 0 else 2)
            wx = sh + math.cos(rad_a) * dist_w
            wy = af_cy + math.sin(rad_a) * (dist_w * 0.85)
            wr = 11.5 + (3.5 if i % 3 == 0 else 0.0)
            a_start = int(a - 125) if i % 2 == 0 else int(a - 35)
            loop_pts = arc_pts(wx, wy, wr, wr * 0.92, a_start, a_start + 245, 12)
            c.line(HH(loop_pts), oc_h, 2.6 * s)
            c.line(HH(loop_pts[2:-2]), c_bright, 1.4 * s)

        # pass 2: outline dasar afro + gumpalan ikal tepi
        c.ell(*HH([(sh, af_cy)])[0], 136 * s + ow_h, 114 * s + ow_h, oc_h)
        for px, py, pr, _ in outer_puffs:
            c.ell(*HH([(px, py)])[0], pr * s + ow_h, pr * s + ow_h, oc_h)

        # pass 3: isi warna dasar rambut hitam-espresso pekat + helai spiral di tepi luar
        c.ell(*HH([(sh, af_cy)])[0], 136 * s, 114 * s, hc)
        for px, py, pr, a in outer_puffs:
            c.ell(*HH([(px, py)])[0], pr * s, pr * s, hc)
            sa = int(a + 25)
            p_arc = arc_pts(px, py, pr * 0.78, pr * 0.76, sa, sa + 210, 11)
            c.line(HH(p_arc), c_mid, 2.4 * s)
            c.line(HH(p_arc[2:-2]), c_bright, 1.4 * s)

        # pass 4: cincin ikal luar di belakang telinga
        for k in range(19):
            ang_d = 144 + (396 - 144) * k / 18.0
            rad = math.radians(ang_d)
            cx_c = sh + math.cos(rad) * 120
            cy_c = af_cy + math.sin(rad) * 100
            cr = 18.5
            c.ell(*HH([(cx_c, cy_c)])[0], (cr + 1.5) * s, (cr + 1.5) * s, c_deep)
            c.ell(*HH([(cx_c, cy_c)])[0], cr * s, cr * s, hc)
            sa = int(ang_d + (k * 47) % 120 - 60)
            arc1 = arc_pts(cx_c, cy_c, cr * 0.84, cr * 0.80, sa, sa + 205, 12)
            arc2 = arc_pts(cx_c, cy_c, cr * 0.60, cr * 0.58, sa + 35, sa + 215, 10)
            c.line(HH(arc1), c_mid, 2.6 * s)
            c.line(HH(arc1[2:-2]), c_bright, 1.6 * s)
            c.line(HH(arc2), c_mid, 1.9 * s)
            if k % 2 == 0:
                arc3 = arc_pts(cx_c, cy_c, cr * 0.88, cr * 0.84, sa + 40, sa + 145, 8)
                c.line(HH(arc3), c_fine, 1.2 * s)

    def _hair_front_ref(self, c, HH, s, hc):
        """Kembalikan rambut depan persis gambar pilihan user (media_1795797796870_ad975d11.png)."""
        oc_h = (16, 12, 14)
        af_cy = -44
        c_deep = (14, 10, 12)
        c_mid = (78, 54, 46)
        c_bright = (128, 94, 80)
        c_fine = (168, 130, 114)

        cap_outer = arc_pts(0, -42, 124, 104, 174, 366, 24)
        forehead_arch = list(reversed(arc_pts(0, -14, 80, 38, 186, 354, 16)))
        c.poly(HH(cap_outer + forehead_arch), hc)

        fringe_curls = [
            (-82, -16, 17), (-74, -34, 19), (-56, -46, 20),
            (-32, -52, 20), (-6, -50, 20), (20, -52, 20),
            (46, -48, 20), (68, -36, 19), (80, -18, 17),
        ]
        for bx, by, br in fringe_curls:
            c.ell(*HH([(bx, by + 5)])[0], br * 0.88 * s, br * 0.70 * s, (226, 182, 160, 115))
        for bx, by, br in fringe_curls:
            c.ell(*HH([(bx, by)])[0], br * s, br * 0.90 * s, hc, 2.0 * s, oc_h)

        rings = [
            (96, 80, 13, 17.5, 170, 370, 11),
            (68, 56, 9, 16.5, 178, 362, 23),
        ]
        for idx_r, (rx_r, ry_r, n_c, cr, a0_r, a1_r, ph_r) in enumerate(rings):
            for k in range(n_c):
                ang_d = a0_r + (a1_r - a0_r) * k / max(1, n_c - 1) + ((k % 2) * 4 - 2)
                rad = math.radians(ang_d)
                cx_c = math.cos(rad) * rx_r
                cy_c = af_cy + math.sin(rad) * ry_r
                c.ell(*HH([(cx_c, cy_c)])[0], (cr + 1.5) * s, (cr + 1.5) * s, c_deep)
                c.ell(*HH([(cx_c, cy_c)])[0], cr * s, cr * s, hc)
                sa = int(ang_d + ph_r + (k * 47) % 120 - 60)
                arc1 = arc_pts(cx_c, cy_c, cr * 0.84, cr * 0.80, sa, sa + 205, 12)
                arc2 = arc_pts(cx_c, cy_c, cr * 0.62, cr * 0.60, sa + 35, sa + 215, 10)
                c.line(HH(arc1), c_mid, 2.6 * s)
                c.line(HH(arc1[2:-2]), c_bright, 1.6 * s)
                c.line(HH(arc2), c_mid, 1.9 * s)
                if (k + idx_r) % 2 == 0:
                    arc3 = arc_pts(cx_c, cy_c, cr * 0.88, cr * 0.84, sa + 40, sa + 145, 8)
                    c.line(HH(arc3), c_fine, 1.2 * s)

        for idx_f, (bx, by, br) in enumerate(fringe_curls):
            sa = 20 + (idx_f * 53) % 140
            f_arc1 = arc_pts(bx, by, br * 0.78, br * 0.76, sa, sa + 210, 11)
            f_arc2 = arc_pts(bx, by, br * 0.52, br * 0.52, sa + 50, sa + 220, 9)
            c.line(HH(f_arc1), c_mid, 2.4 * s)
            c.line(HH(f_arc1[2:-2]), c_bright, 1.4 * s)
            c.line(HH(f_arc2), c_deep, 2.0 * s)

        forehead_wisps = [
            (-64, -30, 10, 15, 225), (-38, -40, 11, 5, 215), (-10, -40, 12, -15, 205),
            (16, -40, 11, -25, 195), (44, -38, 10, -10, 210), (-76, -12, 9, 30, 230), (76, -12, 9, -50, 150),
        ]
        for wx, wy, wr, a0_w, a1_w in forehead_wisps:
            w_pts = arc_pts(wx, wy, wr, wr * 0.9, a0_w, a1_w, 11)
            c.line(HH(w_pts), oc_h, 2.1 * s)
            c.line(HH(w_pts[1:-1]), c_bright, 1.15 * s)

    def _eye_ref(self, c, HH, s, ex_, eye_y, i, eyes, blink, turn, lx_, ly_):
        """Mata Chibi Anime & Studio Ghibli dengan 4 variasi gaya (`fokus`, `ghibli_bulat`, `ghibli_lembut`, `ghibli_dewasa`) agar wajah tiap tokoh berbeda-beda & hidup."""
        gm = self.p.get("gaya_mata", "fokus")
        is_fem = bool(self.p.get("bulu_mata"))
        sc = 1.10 if eyes == "wide" else 1.0
        cy = eye_y + 2.0
        sg = -1 if i == 0 else 1
        line_c = (44, 32, 28) if gm.startswith("ghibli") else (24, 18, 20)
        iris_col = warna(self.p.get("iris"), (58, 40, 34) if gm.startswith("ghibli") else (22, 22, 26))

        if gm == "chibi_hijab":
            # MATA CHIBI BESAR BULAT BERBINAR (persis referensi chibi hijab user: iris cokelat 2-tone hangat + 2 kilau putih jernih + kelopak tebal lentik!)
            ew = 19.6 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
            eh = (20.8 * 0.46 if eyes == "half" else 20.8 * sc) * (1.0 - 0.92 * blink)
            oc_e = (62, 38, 28)
            if eh > 2.6:
                c.poly(HH(_ellpts(ex_, cy + 1.0, ew, eh, 24)), (254, 252, 248))
                ir_w = 14.8 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
                ir_h = min(eh * 0.90, 16.4 * sc)
                ix = ex_ + lx_ * 4.0 + 2.5 * turn
                iy = cy + 1.8 + ly_ * 1.5
                c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 22)), gelap(iris_col, 0.14), 1.2 * s, oc_e)
                # gradasi terang hangat di bagian bawah iris (2-tone khas chibi!)
                c.poly(HH(_ellpts(ix, iy + ir_h * 0.30, ir_w * 0.78, ir_h * 0.48, 16)), terang(iris_col, 0.36))
                c.poly(HH(_ellpts(ix, iy - ir_h * 0.06, ir_w * 0.50, ir_h * 0.50, 14)), (40, 24, 18))
                # 2 kilau putih jernih (besar kiri-atas + kecil kanan-bawah)
                c.poly(HH(_ellpts(ix - ir_w * 0.36, iy - ir_h * 0.34, 4.8, 4.6, 12)), PUTIH)
                c.poly(HH(_ellpts(ix + ir_w * 0.34, iy + ir_h * 0.34, 2.2, 2.2, 8)), PUTIH)
                c.curve(HH(arc_pts(ex_, cy + 1.0, ew * 0.78, eh, 30, 150, 10)), (134, 98, 82), 1.5 * s)
            # kelopak atas tebal melengkung lembut + ujung bulu mata melentik manis
            c.curve(HH(arc_pts(ex_, cy + 1.0, ew + 0.8, max(2.0, eh + 0.8), 190, 350, 16)), oc_e, 4.4 * s)
            if eh > 4.0:
                c.line(HH([(ex_ + sg * (ew - 0.5), cy - 1.5), (ex_ + sg * (ew + 6.5), cy - 6.5)]), oc_e, 2.8 * s)
            return

        if gm == "ghibli_bulat":
            # MATA BULAT JERNIH STUDIO GHIBLI (persis referensi user: oval bulat putih bersih + iris cokelat gelap hangat + 1 kilau putih jernih!)
            ew = 16.5 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
            eh = (18.2 * 0.48 if eyes == "half" else 18.2 * sc) * (1.0 - 0.92 * blink)
            if eh > 2.6:
                c.poly(HH(_ellpts(ex_, cy, ew, eh, 22)), (252, 250, 246), 1.4 * s, (124, 96, 82))
                ir_w = 10.8 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
                ir_h = min(eh * 0.86, 12.6 * sc)
                ix = ex_ + lx_ * 4.0 + 2.5 * turn
                iy = cy + 0.8 + ly_ * 1.5
                c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 20)), iris_col, 1.0 * s, line_c)
                c.poly(HH(_ellpts(ix, iy + ir_h * 0.24, ir_w * 0.72, ir_h * 0.44, 14)), terang(iris_col, 0.24))
                c.poly(HH(_ellpts(ix, iy - ir_h * 0.04, ir_w * 0.46, ir_h * 0.46, 14)), gelap(iris_col, 0.55))
                # 1 titik kilau putih jernih khas Ghibli (kiri-atas)
                c.poly(HH(_ellpts(ix - ir_w * 0.34, iy - ir_h * 0.32, 3.8, 3.6, 12)), PUTIH)
            c.curve(HH(arc_pts(ex_, cy, ew + 0.6, max(2.0, eh + 0.4), 192, 348, 14)), line_c, 3.6 * s)
            if is_fem and eh > 4.0:
                c.line(HH([(ex_ + sg * (ew - 1.0), cy - eh * 0.25), (ex_ + sg * (ew + 5.0), cy - eh * 0.55)]), line_c, 2.2 * s)
            return

        if gm == "ghibli_lembut":
            # MATA GHIBLI LEMBUT RAMAH (sedikit lebih almond hangat + bulu mata halus tipis)
            ew = 18.0 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
            eh = (15.4 * 0.50 if eyes == "half" else 15.4 * sc) * (1.0 - 0.92 * blink)
            if eh > 2.6:
                c.poly(HH(_ellpts(ex_, cy, ew, eh, 22)), (252, 250, 246))
                ir_w = 11.4 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
                ir_h = min(eh * 0.90, 12.6 * sc)
                ix = ex_ + lx_ * 4.0 + 2.2 * turn
                iy = cy + 0.8 + ly_ * 1.5
                c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 20)), iris_col, 1.0 * s, line_c)
                c.poly(HH(_ellpts(ix, iy + ir_h * 0.28, ir_w * 0.72, ir_h * 0.44, 14)), terang(iris_col, 0.32))
                c.poly(HH(_ellpts(ix, iy - ir_h * 0.04, ir_w * 0.45, ir_h * 0.45, 14)), gelap(iris_col, 0.55))
                c.poly(HH(_ellpts(ix - ir_w * 0.34, iy - ir_h * 0.28, 3.4, 3.2, 10)), PUTIH)
                c.poly(HH(_ellpts(ix + ir_w * 0.30, iy + ir_h * 0.30, 1.5, 1.5, 8)), (242, 244, 248))
                c.curve(HH(arc_pts(ex_, cy, ew * 0.85, eh, 28, 152, 10)), (122, 96, 84), 1.5 * s)
            c.curve(HH(arc_pts(ex_, cy, ew + 0.8, max(2.0, eh + 0.6), 192, 348, 14)), line_c, 3.5 * s)
            if is_fem and eh > 4.0:
                c.line(HH([(ex_ + sg * (ew + 0.2), cy - 1.5), (ex_ + sg * (ew + 6.0), cy - 5.5)]), line_c, 2.3 * s)
            if eh > 5.0:
                c.curve(HH(arc_pts(ex_, cy - 2.0, ew * 0.78, eh + 3.2, 212, 328, 10)), (134, 102, 88), 1.4 * s)
            return

        if gm == "ramah_sipit":
            # MATA RAMAH MENYIPIT TERSENYUM (khas kakek/senior Ghibli yang hangat!)
            ew = 17.5 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
            if blink > 0.5 or eyes == "half":
                c.curve(HH([(ex_ - sg * ew, cy + 2.0), (ex_, cy - 3.5), (ex_ + sg * ew, cy + 2.5)]), line_c, 3.2 * s)
            else:
                c.curve(HH([(ex_ - sg * ew, cy + 3.5), (ex_, cy - 7.5), (ex_ + sg * ew, cy + 3.0)]), line_c, 3.6 * s)
                c.curve(HH([(ex_ - sg * ew * 0.72, cy + 5.5), (ex_, cy + 2.5), (ex_ + sg * ew * 0.72, cy + 5.5)]), (142, 108, 92), 1.6 * s)
            if self.p.get("kerut_mata"):
                c.line(HH([(ex_ + sg * (ew + 2.0), cy + 1.0), (ex_ + sg * (ew + 8.5), cy - 1.5)]), (152, 118, 102), 1.5 * s)
                c.line(HH([(ex_ + sg * (ew + 2.0), cy + 4.5), (ex_ + sg * (ew + 7.5), cy + 5.5)]), (152, 118, 102), 1.4 * s)
            return

        if gm == "kalem":
            # MATA KALEM/ELEGAN SEDIKIT RAMPING (Arka, Bu Guru, Bos — beda jelas dari mata bulat anak!)
            ew = 18.6 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
            eh = (11.2 * 0.52 if eyes == "half" else 11.2 * sc) * (1.0 - 0.92 * blink)
            if eh > 2.4:
                c.poly(HH(_ellpts(ex_, cy + 1.5, ew, eh, 20)), (250, 249, 246))
                ir_w = 9.8 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
                ir_h = min(eh * 0.94, 10.2 * sc)
                ix = ex_ + lx_ * 4.0 + 2.2 * turn
                iy = cy + 1.6 + ly_ * 1.4
                c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 18)), iris_col, 1.0 * s, line_c)
                c.poly(HH(_ellpts(ix, iy + ir_h * 0.25, ir_w * 0.72, ir_h * 0.44, 12)), terang(iris_col, 0.28))
                c.poly(HH(_ellpts(ix, iy - ir_h * 0.05, ir_w * 0.44, ir_h * 0.44, 12)), gelap(iris_col, 0.55))
                c.poly(HH(_ellpts(ix - ir_w * 0.34, iy - ir_h * 0.26, 2.7, 2.5, 8)), PUTIH)
                c.line(HH([(ex_ - sg * ew * 0.6, cy + eh + 0.5), (ex_ + sg * ew * 0.7, cy + eh + 0.2)]), (116, 90, 80), 1.5 * s)
            c.curve(HH([(ex_ - sg * (ew + 1.0), cy + 1.2), (ex_, cy - eh + 0.8), (ex_ + sg * (ew + 1.8), cy - 0.8)]), line_c, 3.6 * s)
            if is_fem and eh > 3.5:
                c.line(HH([(ex_ + sg * (ew + 0.5), cy - 1.2), (ex_ + sg * (ew + 6.5), cy - 4.8)]), line_c, 2.3 * s)
            return

        if gm == "ghibli_dewasa":
            # MATA GHIBLI DEWASA TENANG (lebih ringkas, kelopak atas datar-ramah, garis kelopak lembut)
            ew = 16.8 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
            eh = (11.6 * 0.54 if eyes == "half" else 11.6 * sc) * (1.0 - 0.92 * blink)
            if eh > 2.4:
                c.poly(HH(_ellpts(ex_, cy + 1.0, ew, eh, 20)), (250, 248, 244))
                ir_w = 9.4 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
                ir_h = min(eh * 0.92, 9.8 * sc)
                ix = ex_ + lx_ * 3.8 + 2.0 * turn
                iy = cy + 1.2 + ly_ * 1.4
                c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 18)), iris_col, 1.0 * s, line_c)
                c.poly(HH(_ellpts(ix, iy - ir_h * 0.05, ir_w * 0.48, ir_h * 0.48, 12)), gelap(iris_col, 0.55))
                c.poly(HH(_ellpts(ix - ir_w * 0.34, iy - ir_h * 0.28, 2.6, 2.4, 8)), PUTIH)
                c.curve(HH(arc_pts(ex_, cy + 1.5, ew * 0.80, eh, 32, 148, 8)), (128, 100, 88), 1.4 * s)
            c.curve(HH([(ex_ - sg * (ew + 1.0), cy + 1.0), (ex_, cy - eh + 0.5), (ex_ + sg * (ew + 1.2), cy + 0.5)]), line_c, 3.4 * s)
            if eh > 4.5:
                c.curve(HH([(ex_ - sg * ew * 0.65, cy - eh - 3.5), (ex_, cy - eh - 5.2), (ex_ + sg * ew * 0.65, cy - eh - 3.5)]), (136, 106, 92), 1.4 * s)
            if self.p.get("kerut_mata"):
                c.line(HH([(ex_ + sg * (ew + 2.0), cy + 1.5), (ex_ + sg * (ew + 8.0), cy + 0.0)]), (152, 118, 102), 1.4 * s)
            return

        # Default "fokus" (Kribo / Arka / Dimas): sharp half-lidded obsidian
        ew = (18.4 if is_fem else 19.2) * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
        base_eh = 15.6 if is_fem else 13.4
        eh = (base_eh * 0.50 if eyes == "half" else base_eh * sc) * (1.0 - 0.92 * blink)
        iris_bot = terang(iris_col, 0.34 if is_fem else 0.24)
        if not is_fem and iris_col == (24, 24, 28):
            iris_col = (22, 22, 26)
            iris_bot = (72, 76, 86)
        if eh > 2.6:
            p_in = (ex_ - sg * ew, cy + 1.2)
            p_top_in = (ex_ - sg * ew * 0.52, cy - eh * (0.92 if is_fem else 0.78))
            p_top_out = (ex_ + sg * ew * 0.48, cy - eh * (0.98 if is_fem else 0.96))
            p_out = (ex_ + sg * ew, cy - (0.6 if is_fem else 1.2))
            p_bot_out = (ex_ + sg * ew * 0.56, cy + eh * 0.92)
            p_bot_in = (ex_ - sg * ew * 0.50, cy + eh * 0.92)
            eye_poly = [p_in, p_top_in, p_top_out, p_out, p_bot_out, p_bot_in]
            c.poly(HH(eye_poly), (250, 250, 248))

            ir_w = (12.6 if is_fem else 12.8) * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
            ir_h = min(eh * 0.95, (14.0 if is_fem else 12.8) * sc)
            ix = ex_ + lx_ * 4.0 + 2.0 * turn
            iy = cy + ly_ * 1.5
            c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 20)), iris_col, 1.2 * s, line_c)
            c.poly(HH(_ellpts(ix, iy + ir_h * 0.30, ir_w * 0.74, ir_h * 0.48, 16)), iris_bot)
            c.poly(HH(_ellpts(ix, iy - ir_h * 0.05, ir_w * 0.48, ir_h * 0.48, 14)), gelap(iris_col, 0.55))
            c.poly(HH([
                p_in, p_top_in, p_top_out, p_out,
                (ex_ + sg * ew * 0.85, cy - eh * 0.38),
                (ex_ - sg * ew * 0.85, cy - eh * 0.28),
            ]), (18, 18, 22, 95 if is_fem else 115))
            hl_r = 3.4 if is_fem else 2.8
            c.poly(HH(_ellpts(ix - ir_w * 0.36, iy - ir_h * 0.24, hl_r, hl_r * 0.86, 10)), PUTIH)
            c.poly(HH(_ellpts(ix + ir_w * 0.34, iy + ir_h * 0.32, 1.6 if is_fem else 1.3, 1.6 if is_fem else 1.3, 8)), (235, 240, 248))
            c.poly(HH([
                (ex_ - sg * (ew + 2), cy - eh * 0.32),
                (ex_ - sg * (ew + 2), cy - eh * 1.25),
                (ex_ + sg * (ew + 2), cy - eh * 1.25),
                p_top_out, p_top_in,
            ]), warna(self.p.get("kulit"), (254, 232, 214)))
            c.line(HH([p_bot_in, p_bot_out, p_out]), (96, 76, 68), 1.6 * s)

        lid_pts = [
            (ex_ - sg * (ew + 0.8), cy + 0.5),
            (ex_ - sg * ew * 0.50, cy - eh * (0.92 if is_fem else 0.78)),
            (ex_ + sg * ew * 0.48, cy - eh * (0.98 if is_fem else 0.96)),
            (ex_ + sg * (ew + 1.8), cy - (0.8 if is_fem else 1.5)),
        ]
        c.line(HH(lid_pts), line_c, (3.8 if is_fem else 3.5) * s)
        if is_fem and eh > 4.0:
            c.line(HH([(ex_ + sg * (ew + 0.5), cy - 2.0), (ex_ + sg * (ew + 6.5), cy - 6.8)]), line_c, 2.5 * s)
            c.line(HH([(ex_ + sg * (ew - 2.5), cy - eh * 0.55), (ex_ + sg * (ew + 4.0), cy - eh * 0.82)]), line_c, 2.0 * s)
        if eh > 5.0:
            c.line(HH([
                (ex_ - sg * ew * 0.52, cy - eh * (1.10 if is_fem else 0.98)),
                (ex_ + sg * ew * 0.46, cy - eh * (1.20 if is_fem else 1.16)),
            ]), (116, 86, 76), 1.5 * s)

    def _hand(self, c, H, ang, s, tb, sgn, fl, hk, skin):
        """Tangan kartun berjari-jari rapi: 'm' terbuka (4 jari), 'p' menunjuk, 't' jempol, 'f' mengepal."""
        sc = s * tb
        hx, hy = H
        ux, uy = math.cos(ang), math.sin(ang)
        # sisi dalam (arah jempol): menghadap ke arah tubuh / wajah secara alami
        ts = -sgn * fl
        vx, vy = -uy * ts, ux * ts

        def pt(fwd, side):
            return (hx + ux * fwd * sc + vx * side * sc, hy + uy * fwd * sc + vy * side * sc)

        how = 3.2 * s
        if hk == "p":
            # telunjuk lurus memanjang + jempol terbuka ringan + 2 jari lain terlipat
            palm_c = pt(3.5, -1.0)
            idx_a, idx_b = pt(6.0, 2.2), pt(24.5, 2.8)
            th_a, th_b = pt(2.0, 6.5), pt(10.5, 13.0)
            curl_pts = [pt(9.5, -3.5), pt(8.0, -8.5)]
            # pass 1: outline
            c.ell(palm_c[0], palm_c[1], 11.2 * sc + how, 10.2 * sc + how, OUT)
            c.line([idx_a, idx_b], OUT, 7.6 * sc + 2 * how)
            c.line([th_a, th_b], OUT, 6.8 * sc + 2 * how)
            for cp in curl_pts:
                c.ell(cp[0], cp[1], 4.6 * sc + how, 4.6 * sc + how, OUT)
            # pass 2: isi kulit
            c.ell(palm_c[0], palm_c[1], 11.2 * sc, 10.2 * sc, skin)
            c.line([idx_a, idx_b], skin, 7.6 * sc)
            c.line([th_a, th_b], skin, 6.8 * sc)
            for cp in curl_pts:
                c.ell(cp[0], cp[1], 4.6 * sc, 4.6 * sc, skin, how * 0.65, OUT)
        elif hk == "t":
            # jempol ke atas (thumbs up) + kepalan 3 jari terlipat rapi
            palm_c = pt(4.0, 0.0)
            th_a = (hx, hy - 4.0 * sc)
            th_b = (hx + sgn * fl * 1.5 * sc, hy - 22.5 * sc)
            # pass 1: outline
            c.ell(palm_c[0], palm_c[1], 12.0 * sc + how, 11.0 * sc + how, OUT)
            c.line([th_a, th_b], OUT, 8.2 * sc + 2 * how)
            # pass 2: isi kulit
            c.ell(palm_c[0], palm_c[1], 12.0 * sc, 11.0 * sc, skin)
            c.line([th_a, th_b], skin, 8.2 * sc)
            # 2 garis ruas jari terlipat di sisi depan kepalan
            for k in (-3.5, 2.5):
                c.line([pt(6.0, k - 2.0), pt(13.5, k - 2.0)], OUT, 2.2 * s)
        elif hk == "f":
            # kepalan tangan rapi dengan ruas jari & jempol melintang
            palm_c = pt(4.0, 0.0)
            c.ell(palm_c[0], palm_c[1], 12.4 * sc, 11.2 * sc, skin, how, OUT)
            for k in (-4.8, 0.0, 4.8):
                c.line([pt(5.5, k), pt(13.0, k)], OUT, 2.1 * s)
            c.line([pt(0.0, 8.5), pt(8.5, 4.5)], OUT, 2.6 * s)
        else:
            # tangan terbuka santai: telapak + jempol + 3 jari kartun halus menyatu mulus (2-pass)
            palm_c = pt(3.2, -0.5)
            fingers = [
                # (pangkal_fwd, pangkal_side, ujung_fwd, ujung_side, tebal)
                (1.5,  6.2,  9.5,  13.8, 6.2),   # jempol
                (7.5,  4.8, 19.2,   7.0, 6.0),   # telunjuk
                (8.5,  0.0, 21.2,   0.2, 6.2),   # jari tengah
                (7.0, -5.0, 17.8,  -6.8, 5.8),   # jari manis/kelingking
            ]
            # pass 1: outline luar menyatu
            c.ell(palm_c[0], palm_c[1], 10.6 * sc + how, 9.8 * sc + how, OUT)
            for f0, s0, f1, s1, fw in fingers:
                c.line([pt(f0, s0), pt(f1, s1)], OUT, fw * sc + 2 * how)
            # pass 2: isi kulit menyatu bersih
            c.ell(palm_c[0], palm_c[1], 10.6 * sc, 9.8 * sc, skin)
            for f0, s0, f1, s1, fw in fingers:
                c.line([pt(f0, s0), pt(f1, s1)], skin, fw * sc)
            # garis sekat halus di sela antar jari agar jari-jari tetap terbaca jelas
            for sep_s in (3.4, -2.5):
                c.line([pt(9.8, sep_s), pt(14.2, sep_s * 1.15)], OUT, 1.9 * s)

    # ------------------------------------------------------------ kepala
    def _head(self, c, st, T, s, fl, ow, turn=0.0):
        p = self.p
        ex = eks(st.get("expr", "senang"))
        tilt = math.radians(st.get("tilt", 0) * (fl if False else 1))
        look = st.get("look", (0.0, 0.0))
        lk = ex.get("look")
        if lk and abs(look[0]) < .01 and abs(look[1]) < .01:
            look = lk
        fem = bool(p.get("hijab")) or p.get("bulu_mata")
        mask = bool(p.get("wajah_maskulin"))
        hij = bool(p.get("hijab"))
        cx, cy = 4.0 * turn, HEAD_Y
        face_rx, face_ry = (78.0, 84.0) if hij else (HEAD_R, HEAD_R)
        hs = float(p.get("head_scale", 1.0))
        fcy = cy + (4 if hij else (2 if hs > 1.05 else (-2 if p.get("wajah_chibi_ref") else 0)))
        yaw_x = 22.0 * turn     # pergeseran fitur wajah ke arah hadap 3/4 (+x lokal)
        hair_sh = -10.0 * turn  # massa rambut/hijab sedikit bergeser ke belakang saat miring

        def H(lx, ly):
            rx, ry = _rot((lx * hs, ly * hs), tilt * fl)
            return T(cx + rx, fcy + ry)

        def HH(pts):
            return [H(*q) for q in pts]

        # belakang rambut
        hair_c = warna(p.get("rambut_warna"), HITAM)
        r = p.get("rambut")
        if hij:
            hj, hjd = warna(p["hijab"]), warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .16))
            if p.get("hijab_gaya") == "modern":
                # SILUET KEPALA HIJAB CHIBI 1 KURVA BLOB MULUS (nol sudut patah di pipi!) mengikuti bentuk wajah masing-masing
                oc_h = (68, 44, 34)
                bw_h = p.get("bentuk_wajah", "oval")
                hw_x = 108 if bw_h == "bulat_chibi" else (96 if bw_h == "lonjong" else 102)
                ht_y = -104 if bw_h == "lonjong" else -100
                hb_y = 90 if bw_h == "lonjong" else 86
                outer_pts = [
                    (hair_sh, ht_y), (hair_sh + hw_x * 0.56, ht_y + 10), (hair_sh + hw_x * 0.94, -44),
                    (hair_sh + hw_x, 10), (hair_sh + hw_x * 0.90, 56), (hair_sh + hw_x * 0.52, hb_y - 4),
                    (hair_sh, hb_y), (hair_sh - hw_x * 0.52, hb_y - 4), (hair_sh - hw_x * 0.90, 56),
                    (hair_sh - hw_x, 10), (hair_sh - hw_x * 0.94, -44), (hair_sh - hw_x * 0.56, ht_y + 10),
                ]
                c.blob(HH(outer_pts), hj, 2.4 * s, oc_h, n=10)
                # lapisan lipatan kain lembut membingkai pipi kiri-kanan
                c.curve(HH([(hair_sh - hw_x * 0.78, 46), (hair_sh - hw_x * 0.84, -14), (hair_sh - hw_x * 0.58, -66), (hair_sh - 20, ht_y + 14)]), hjd, 2.0 * s)
                c.curve(HH([(hair_sh + hw_x * 0.78, 46), (hair_sh + hw_x * 0.84, -14), (hair_sh + hw_x * 0.58, -66), (hair_sh + 20, ht_y + 14)]), hjd, 2.0 * s)
                c.curve(HH([(hair_sh - hw_x * 0.62, -52), (hair_sh - hw_x * 0.30, ht_y + 14), (hair_sh + 10, ht_y + 10)]), terang(hj, 0.16), 3.0 * s)
            else:
                outer = HH(_ellpts(hair_sh, -12, 102, 104))
                c.poly(outer, hj, ow, OUT)
                c.curve(HH([(hair_sh - 70, -54), (hair_sh - 40, -88), (hair_sh, -96)]), terang(hj, 0.14), 3.6 * s)
        if r in ("kuncir",) and not hij:
            if p.get("wajah_chibi_ref"):
                oc_h = (50, 38, 34)
                for sg_k in (-1, 1):
                    if sg_k > 0 and turn >= 0.75:
                        continue
                    bx_k = hair_sh + sg_k * 82
                    by_k = -60
                    rx_k = 28 * (1.0 - 0.35 * turn if sg_k > 0 else 1.0)
                    c.ell(*H(bx_k, by_k), rx_k * s, 28 * s, gelap(hair_c, 0.32))
                    # 3 bundel helai sutra melingkar rapat membentuk sanggul/bun!
                    self._draw_silk_bundle(c, HH, (bx_k - rx_k * 0.92, by_k + 6), (bx_k - rx_k * 0.65, by_k - 28),
                                           (bx_k + rx_k * 0.65, by_k - 28), (bx_k + rx_k * 0.92, by_k + 6),
                                           7.5, 11.0, 6.0, hair_c, n_strands=10, seed=11 + sg_k, shine=1.1)
                    self._draw_silk_bundle(c, HH, (bx_k - rx_k * 0.85, by_k + 12), (bx_k - rx_k * 0.35, by_k - 14),
                                           (bx_k + rx_k * 0.45, by_k - 14), (bx_k + rx_k * 0.85, by_k + 14),
                                           7.0, 10.0, 5.5, hair_c, n_strands=9, seed=21 + sg_k, shine=0.9)
                    self._draw_silk_bundle(c, HH, (bx_k - rx_k * 0.78, by_k + 10), (bx_k - rx_k * 0.30, by_k + 26),
                                           (bx_k + rx_k * 0.35, by_k + 26), (bx_k + rx_k * 0.78, by_k + 10),
                                           6.0, 8.5, 5.0, hair_c, n_strands=8, seed=31 + sg_k, shine=0.5)
                    acc_c = warna(p.get("dasi") or p.get("aksen"), (218, 86, 98))
                    c.ell(*H(hair_sh + sg_k * 63, -52), 7.5 * s, 10.5 * s, acc_c, 1.8 * s, oc_h)
            else:
                c.ell(*H(hair_sh - 86, -58), 27 * s, 27 * s, hair_c, ow, OUT)
                if turn < 0.75:
                    c.ell(*H(hair_sh + 86, -58), 27 * s * (1.0 - 0.35 * turn), 27 * s, hair_c, ow, OUT)
        if r == "ghibli_kuncir" and not hij:
            # rambut belakang Studio Ghibli + ekor kuda samping kiri padat-rapi berhelai sutra + ikat merah bundar
            oc_h = (32, 26, 26)
            # ekor kuda samping kiri merapat menyatu menjadi 1 siluet kuncir Ghibli yang rapi & padat!
            self._draw_silk_bundle(c, HH, (hair_sh - 74, 46), (hair_sh - 102, 50), (hair_sh - 122, 68), (hair_sh - 132, 92),
                                   12.5, 16.5, 2.0, hair_c, n_strands=11, seed=41, shine=1.0)
            self._draw_silk_bundle(c, HH, (hair_sh - 72, 50), (hair_sh - 98, 66), (hair_sh - 116, 88), (hair_sh - 122, 114),
                                   13.5, 17.5, 1.8, hair_c, n_strands=12, seed=42, shine=1.15)
            self._draw_silk_bundle(c, HH, (hair_sh - 70, 54), (hair_sh - 90, 76), (hair_sh - 104, 98), (hair_sh - 104, 120),
                                   12.0, 15.0, 1.5, hair_c, n_strands=10, seed=43, shine=0.85)
            self._draw_wispy_tips(c, HH, hair_c, [
                ((hair_sh - 106, 66), (hair_sh - 124, 78), (hair_sh - 134, 90), (hair_sh - 138, 100), 2.4),
                ((hair_sh - 104, 88), (hair_sh - 116, 104), (hair_sh - 120, 116), (hair_sh - 118, 124), 2.2),
            ])
            c.ell(*H(hair_sh - 76, 46), 11.5 * s, 9.5 * s, (194, 48, 52), 2.0 * s, oc_h)
            # massa rambut belakang gelap lembut
            c.blob(HH([
                (hair_sh - 94, 22), (hair_sh - 100, -38), (hair_sh - 80, -92),
                (hair_sh - 34, -118), (hair_sh + 14, -120), (hair_sh + 62, -106),
                (hair_sh + 92, -74), (hair_sh + 98, -24), (hair_sh + 88, 20),
                (hair_sh + 68, 34), (hair_sh - 68, 34),
            ]), gelap(hair_c, 0.34), 0, n=8)
        if r == "bob" and not hij and p.get("wajah_chibi_ref"):
            c.blob(HH([
                (hair_sh - 92, 46), (hair_sh - 94, -18), (hair_sh - 80, -74),
                (hair_sh - 40, -104), (hair_sh, -110), (hair_sh + 40, -104),
                (hair_sh + 80, -74), (hair_sh + 94, -18), (hair_sh + 92, 46),
                (hair_sh + 72, 68), (hair_sh, 64), (hair_sh - 72, 68),
            ]), gelap(hair_c, 0.30), 0, n=7)
        if r == "jambul" and not hij and p.get("wajah_chibi_ref"):
            c.blob(HH([
                (hair_sh - 84, 14), (hair_sh - 90, -44), (hair_sh - 70, -92),
                (hair_sh, -112), (hair_sh + 70, -92), (hair_sh + 90, -44),
                (hair_sh + 84, 14), (hair_sh + 64, 24), (hair_sh - 64, 24),
            ]), gelap(hair_c, 0.36), 0, n=7)
        if r in ("rapi", "uban", "belah_samping", "sisir_belakang", "klimis") and not hij and p.get("wajah_chibi_ref"):
            bw_hb = p.get("bentuk_wajah", "oval")
            w_hb = 76 if bw_hb == "lonjong" else (82 if bw_hb == "oval" else 88)
            top_hb = -120 if r == "sisir_belakang" else (-112 if r in ("uban", "belah_samping") else -108)
            c.blob(HH([
                (hair_sh - w_hb, 12), (hair_sh - w_hb - 4, -44), (hair_sh - w_hb * 0.78, -86),
                (hair_sh, top_hb), (hair_sh + w_hb * 0.78, -86), (hair_sh + w_hb + 4, -44),
                (hair_sh + w_hb, 12), (hair_sh + w_hb * 0.70, 22), (hair_sh - w_hb * 0.70, 22),
            ]), gelap(hair_c, 0.34), 0, n=7)
        if r == "keriting" and not hij:
            if p.get("wajah_chibi_ref"):
                # RAMBUT IKAL PENDEK KASTANYE 3-TONE HALUS (setara kerapian Kribo!)
                oc_h = (42, 26, 22)
                ow_h = 2.2 * s
                c_mid = mix(hair_c, (124, 86, 66), 0.45)
                c_br = (*mix(hair_c, (168, 124, 96), 0.55), 145)
                c_sh = gelap(hair_c, 0.28)
                puffs = []
                for i, a in enumerate(range(164, 377, 16)):
                    rr = 92 + (7 if i % 2 else 0)
                    puffs.append((hair_sh + math.cos(math.radians(a)) * rr, -22 + math.sin(math.radians(a)) * (rr * 0.88), 24 + (3 if i % 2 else 0), a))
                for i in range(0, len(puffs), 2):
                    px, py, pr, a = puffs[i]
                    rad_a = math.radians(a)
                    wx, wy = px + math.cos(rad_a) * 12, py + math.sin(rad_a) * 10
                    lp = arc_pts(wx, wy, 9.5, 8.5, int(a - 110), int(a + 120), 10)
                    c.line(HH(lp), oc_h, 2.0 * s)
                    c.line(HH(lp[2:-2]), c_br, 1.1 * s)
                c.ell(*H(hair_sh, -28), 94 * s + ow_h, 82 * s + ow_h, oc_h)
                for px, py, pr, _ in puffs:
                    c.ell(*H(px, py), pr * s + ow_h, pr * s + ow_h, oc_h)
                c.ell(*H(hair_sh, -28), 94 * s, 82 * s, hair_c)
                for px, py, pr, a in puffs:
                    c.ell(*H(px, py), pr * s, pr * s, hair_c)
                    sa = int(a + 20)
                    a1 = arc_pts(px, py, pr * 0.74, pr * 0.72, sa, sa + 200, 10)
                    c.line(HH(a1), c_mid, 1.7 * s)
                    c.line(HH(a1[2:-2]), c_br, 1.1 * s)
                for cx_, cy_, cr_ in ((-58, -74, 15), (-18, -90, 17), (28, -86, 16), (64, -64, 14), (-72, -38, 13), (70, -34, 13)):
                    a2 = arc_pts(hair_sh + cx_, cy_, cr_, cr_ * 0.85, 195, 390, 10)
                    c.line(HH(a2), c_sh, 1.7 * s)
                    c.line(HH(a2[2:-3]), c_br, 1.0 * s)
            else:
                for i, a in enumerate(range(188, 353, 15)):
                    rr = 86 + (5 if i % 2 else 0)
                    c.ell(*H(hair_sh + math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr), 27 * s, 27 * s, hair_c, ow * .9, OUT)
        if r == "kribo_chibi" and not hij:
            self._hair_back_ref(c, HH, s, hair_c, hair_sh)
        if False:
            # RAMBUT KRIBO ANIME BERLAYER MELENGKUNG (persis siluet referensi: ikal melengkung organik, BUKAN brokoli bulat!)
            oc_h = (28, 24, 30)
            ow_h = 2.6 * s
            # massa dasar asimetris sedikit melebar di atas & merapat ke pipi
            base_pts = [
                (hair_sh - 114, 14), (hair_sh - 134, -22), (hair_sh - 132, -74), (hair_sh - 96, -122),
                (hair_sh - 34, -148), (hair_sh + 34, -146), (hair_sh + 98, -118), (hair_sh + 134, -68),
                (hair_sh + 130, -18), (hair_sh + 112, 16), (hair_sh + 86, 26), (hair_sh - 86, 26),
            ]
            # 12 helai ikal melengkung lebar-organik di sekeliling siluet (persis gambar referensi!)
            locks_out = [
                ((-126, 6), (-148, -2), (-154, -18), (-124, -22)),
                ((-134, -34), (-160, -48), (-166, -66), (-126, -68)),
                ((-124, -80), (-146, -104), (-142, -124), (-102, -108)),
                ((-92, -118), (-98, -146), (-82, -158), (-58, -132)),
                ((-36, -142), (-18, -168), (8, -174), (16, -142)),
                ((34, -142), (66, -162), (86, -154), (68, -126)),
                ((94, -116), (126, -128), (138, -112), (112, -88)),
                ((126, -72), (154, -76), (160, -58), (128, -46)),
                ((130, -28), (156, -24), (156, -6), (122, -6)),
                ((116, 6), (134, 22), (122, 34), (102, 18)),
                ((-116, 6), (-134, 22), (-122, 34), (-102, 18)),
            ]
            # pass 1: outline
            c.blob(HH(base_pts), oc_h, ow_h * 1.4, oc_h, n=6)
            for p0, pm, tip, p1 in locks_out:
                e1 = bezier((hair_sh + p0[0], p0[1]), (hair_sh + pm[0], pm[1]), (hair_sh + tip[0], tip[1]), 6)
                e2 = list(reversed(bezier((hair_sh + p1[0], p1[1]), (hair_sh + (pm[0] + p1[0]) * 0.5, (pm[1] + tip[1]) * 0.5), (hair_sh + tip[0], tip[1]), 6)))
                c.poly(HH(e1 + e2), oc_h, ow_h * 1.5, oc_h)
            # pass 2: isi warna hitam arang hangat menyatu
            c.blob(HH(base_pts), hair_c, 0, n=6)
            for p0, pm, tip, p1 in locks_out:
                e1 = bezier((hair_sh + p0[0], p0[1]), (hair_sh + pm[0], pm[1]), (hair_sh + tip[0], tip[1]), 6)
                e2 = list(reversed(bezier((hair_sh + p1[0], p1[1]), (hair_sh + (pm[0] + p1[0]) * 0.5, (pm[1] + tip[1]) * 0.5), (hair_sh + tip[0], tip[1]), 6)))
                c.poly(HH(e1 + e2), hair_c)
            # pass 3: 3-tone tekstur ikal berlapis (bayangan dalam + highlight lembut + lekukan C-curl organik)
            sh_c = gelap(hair_c, 0.34)
            hl_c = terang(hair_c, 0.20)
            for cx_, cy_, rx_, ry_ in ((-74, -96, 30, 18), (-12, -120, 34, 20), (54, -104, 30, 18), (94, -62, 24, 16)):
                c.ell(*H(hair_sh + cx_, cy_), rx_ * s, ry_ * s, hl_c)
            # garis lengkung ikal berlapis (seperti goresan kuas ikal pada referensi!)
            for (x0_, y0_, xm_, ym_, x1_, y1_) in (
                (-102, -62, -82, -96, -54, -84), (-64, -108, -32, -132, -4, -108),
                (-12, -124, 22, -134, 48, -104), (42, -116, 78, -112, 96, -80),
                (-94, -36, -68, -62, -42, -46), (-38, -82, -6, -98, 24, -78),
                (22, -86, 56, -88, 80, -58), (74, -46, 102, -44, 108, -18),
            ):
                c.curve(HH([(hair_sh + x0_, y0_), (hair_sh + xm_, ym_), (hair_sh + x1_, y1_)]), sh_c, 2.6 * s)
        if r == "panjang_naa" and not hij:
            # rambut belakang panjang bergelombang sutra berlapis (mengalir lewat samping bahu + ujung wispy!)
            back_pts = [
                (hair_sh - 84, -8), (hair_sh - 86, -60), (hair_sh - 64, -94), (hair_sh, -106),
                (hair_sh + 64, -94), (hair_sh + 86, -60), (hair_sh + 84, -8),
                (hair_sh + 90, 48), (hair_sh + 84, 88), (hair_sh + 64, 96),
                (hair_sh + 32, 86), (hair_sh, 84), (hair_sh - 32, 86),
                (hair_sh - 64, 96), (hair_sh - 84, 88), (hair_sh - 90, 48),
            ]
            c.blob(HH(back_pts), gelap(hair_c, 0.34), 0, n=6)
            for sg_p in (-1, 1):
                self._draw_silk_bundle(c, HH,
                    (hair_sh + sg_p * 74, -22), (hair_sh + sg_p * 94, 18),
                    (hair_sh + sg_p * 98, 62), (hair_sh + sg_p * 74, 104),
                    15.0, 19.0, 2.2, hair_c, n_strands=13, seed=51 + sg_p, shine=1.1)
                self._draw_silk_bundle(c, HH,
                    (hair_sh + sg_p * 62, 6), (hair_sh + sg_p * 82, 42),
                    (hair_sh + sg_p * 76, 78), (hair_sh + sg_p * 52, 102),
                    13.0, 15.5, 2.0, hair_c, n_strands=10, seed=55 + sg_p, shine=0.75)
                self._draw_wispy_tips(c, HH, hair_c, [
                    ((hair_sh + sg_p * 86, 54), (hair_sh + sg_p * 98, 76), (hair_sh + sg_p * 94, 94), (hair_sh + sg_p * 82, 108), 3.0),
                    ((hair_sh + sg_p * 74, 72), (hair_sh + sg_p * 78, 92), (hair_sh + sg_p * 68, 104), (hair_sh + sg_p * 56, 110), 2.6),
                ])
        if r == "comma" and not hij:
            # rambut belakang comma gelap lembut (bundel sutra luar digambar di _hair_front)
            c.blob(HH([
                (hair_sh - 84, 16), (hair_sh - 94, -34), (hair_sh - 78, -86), (hair_sh - 38, -112),
                (hair_sh + 2, -118), (hair_sh + 44, -112), (hair_sh + 80, -86), (hair_sh + 94, -34),
                (hair_sh + 84, 16), (hair_sh + 62, 26), (hair_sh - 62, 26),
            ]), gelap(hair_c, 0.36), 0, n=8)
        if r == "panjang" and not hij:
            # rambut panjang coklat lembut berlapis (gaya chibi cewek Ghibli gambar 2)
            c.blob(HH([
                (hair_sh - 104, 10), (hair_sh - 102, -56), (hair_sh - 72, -102), (hair_sh, -116),
                (hair_sh + 72, -102), (hair_sh + 102, -56), (hair_sh + 104, 10),
                (hair_sh + 116, 104), (hair_sh + 86, 134), (hair_sh + 42, 118),
                (hair_sh, 126), (hair_sh - 42, 118), (hair_sh - 86, 134), (hair_sh - 116, 104),
            ]), hair_c, ow * .88, OUT, n=6)
        if r == "afro" and not hij:
            # afro kribo organik bergaya chibi Ghibli: massa afro mengembang + jambul-jambul ikal melengkung!
            af_cy = -44
            puffs = []
            dr_pat = (2, 10, -2, 12, 3, 10, -1, 13, 6, 13, -1, 10, 3, 12, -2, 10, 2)
            pr_pat = (25, 31, 28, 34, 30, 35, 31, 35, 34, 35, 31, 35, 30, 34, 28, 31, 25)
            for i, a in enumerate(range(144, 397, 16)):
                rad_a = math.radians(a)
                px = hair_sh + math.cos(rad_a) * (112 + dr_pat[i])
                py = af_cy + math.sin(rad_a) * (98 + dr_pat[i])
                puffs.append((px, py, pr_pat[i]))
            # helaian ujung ikal organik mencuat lembut di tepi afro (membuat siluet kribo berkarakter seperti gambar 1!)
            curls = [
                (-124, -68, -148, -90, -112, -88), (-96, -124, -112, -158, -72, -138),
                (-28, -146, -18, -178, 12, -148), (48, -140, 74, -170, 82, -130),
                (112, -96, 144, -116, 124, -70), (126, -34, 152, -40, 124, -12),
                (-126, -24, -150, -28, -120, -4),
            ]
            # pass 1: outline
            c.ell(*H(hair_sh, af_cy), 108 * s + ow, 94 * s + ow, OUT)
            for px, py, pr in puffs:
                c.ell(*H(px, py), pr * s + ow, pr * s + ow, OUT)
            for x0_, y0_, xt_, yt_, x1_, y1_ in curls:
                c.poly(HH([(hair_sh + x0_, y0_), (hair_sh + xt_, yt_), (hair_sh + x1_, y1_)]), OUT, ow * 1.4, OUT)
            # pass 2: isi warna rambut hangat + tekstur ikal berlapis (cel shadow + pusaran ikal + highlight)
            c.ell(*H(hair_sh, af_cy), 108 * s, 94 * s, hair_c)
            for px, py, pr in puffs:
                c.ell(*H(px, py), pr * s, pr * s, hair_c)
            for x0_, y0_, xt_, yt_, x1_, y1_ in curls:
                c.poly(HH([(hair_sh + x0_, y0_), (hair_sh + xt_, yt_), (hair_sh + x1_, y1_)]), hair_c)
            # bayangan cel bawah-kanan di dalam afro (memberi volume 3D lembut)
            sh_h = gelap(hair_c, 0.24)
            for sx_, sy_, sr_ in ((74, -26, 36), (48, -12, 34), (-78, -22, 32), (86, -64, 30)):
                c.ell(*H(hair_sh + sx_, sy_), sr_ * s, sr_ * 0.82 * s, sh_h)
            # highlight hangat di klaster atas-kiri afro
            hl_c = terang(hair_c, 0.16)
            for hx_, hy_, hr in ((hair_sh - 58, -114, 24), (hair_sh - 16, -128, 28), (hair_sh + 32, -116, 22), (hair_sh - 86, -78, 18)):
                c.ell(*H(hx_, hy_), hr * s, hr * 0.68 * s, hl_c)
            # tekstur pusaran & helai ikal kribo organik tersebar di seluruh volume rambut!
            curl_c = gelap(hair_c, 0.34)
            curl_hl = terang(hair_c, 0.22)
            swirls = [
                (-82, -78, 18, 1), (-46, -104, 20, -1), (4, -116, 22, 1), (52, -102, 20, -1), (86, -72, 18, 1),
                (-66, -48, 16, -1), (-24, -76, 19, 1), (26, -78, 19, -1), (68, -46, 16, 1), (0, -90, 17, 1),
            ]
            for cx_, cy_, cr_, dir_ in swirls:
                c.curve(HH([(hair_sh + cx_ - cr_, cy_ + 5 * dir_), (hair_sh + cx_, cy_ - cr_ * 0.55),
                            (hair_sh + cx_ + cr_, cy_ + 3 * dir_)]), curl_c, 3.0 * s)
                c.curve(HH([(hair_sh + cx_ - cr_ * 0.6, cy_ - 2), (hair_sh + cx_, cy_ - cr_ * 0.38),
                            (hair_sh + cx_ + cr_ * 0.5, cy_ - 1)]), curl_hl, 1.8 * s)
        # wajah
        kepala = p.get("kepala")
        if kepala == "otak":
            # kepala otak pink chibi berlekuk-lekuk (2-pass: outline luar dulu lalu isi pink + lekukan sulkus)
            bc = warna(p.get("kulit"), (250, 174, 198))
            lip = gelap(bc, 0.25)
            lobes = [
                (-78, 30, 38), (-88, -12, 42), (-76, -52, 42), (-38, -76, 42),
                (38, -76, 42), (76, -52, 42), (88, -12, 42), (78, 30, 38),
                (-42, 58, 38), (0, 64, 40), (42, 58, 38),
            ]
            c.ell(*H(0, -6), 96 * s + ow, 82 * s + ow, OUT)
            for lx, ly, lr in lobes:
                c.ell(*H(lx, ly), lr * s + ow, lr * s + ow, OUT)
            c.ell(*H(0, -6), 96 * s, 82 * s, bc)
            for lx, ly, lr in lobes:
                c.ell(*H(lx, ly), lr * s, lr * s, bc)
            c.curve(HH([(0, -104), (-3, -78), (2, -52)]), lip, 4.4 * s)
            c.curve(HH([(-84, -44), (-62, -62), (-38, -48)]), lip, 3.8 * s)
            c.curve(HH([(84, -44), (62, -62), (38, -48)]), lip, 3.8 * s)
            c.curve(HH([(-100, -12), (-80, -22), (-68, -4)]), lip, 3.6 * s)
            c.curve(HH([(100, -12), (80, -22), (68, -4)]), lip, 3.6 * s)
            c.curve(HH([(-90, 26), (-72, 14), (-62, 34)]), lip, 3.4 * s)
            c.curve(HH([(90, 26), (72, 14), (62, 34)]), lip, 3.4 * s)
            c.ell(*H(-42, -80), 13 * s, 6.5 * s, (255, 255, 255, 130))
        elif kepala == "virus":
            vc = warna(p.get("kulit"), (112, 204, 88))
            spikes = []
            for i in range(10):
                a = math.radians(i * 36 + 18)
                ca, sa = math.cos(a), math.sin(a)
                spikes.append(((ca * 84, sa * 84), (ca * 118, sa * 118)))
            for p0, p1 in spikes:
                c.line(HH([p0, p1]), OUT, 20 * s)
                c.ell(*H(*p1), 15.5 * s + ow, 15.5 * s + ow, OUT)
            c.ell(*H(0, 0), 88 * s + ow, 88 * s + ow, OUT)
            for p0, p1 in spikes:
                c.line(HH([p0, p1]), vc, 11 * s)
                c.ell(*H(*p1), 14 * s, 14 * s, terang(vc, 0.22))
            c.ell(*H(0, 0), 88 * s, 88 * s, vc)
            for bx, by, br in ((-52, -42, 11), (54, -34, 9.5), (-56, 40, 9.5), (50, 44, 11)):
                c.ell(*H(bx, by), br * s, br * s, gelap(vc, 0.20))
        elif kepala == "sel_imun":
            ic = warna(p.get("kulit"), (236, 248, 255))
            c.ell(*H(0, 0), 114 * s, 114 * s, (120, 204, 252, 70))
            bumps = [(math.cos(math.radians(i * 45)) * 68, math.sin(math.radians(i * 45)) * 68, 42) for i in range(8)]
            c.ell(*H(0, 0), 84 * s + ow, 84 * s + ow, OUT)
            for bx, by, br in bumps:
                c.ell(*H(bx, by), br * s + ow, br * s + ow, OUT)
            c.ell(*H(0, 0), 84 * s, 84 * s, ic)
            for bx, by, br in bumps:
                c.ell(*H(bx, by), br * s, br * s, ic)
            c.ell(*H(-38, -52), 15 * s, 9 * s, (255, 255, 255, 190))
        elif hij and p.get("hijab_gaya") == "modern":
            skin_c = warna(p.get("kulit"), PUTIH)
            hj_c = warna(p["hijab"])
            hjd2 = warna(p.get("hijab_tua"), gelap(hj_c, .18))
            oc_f = (68, 46, 36)
            jx = 6.0 * turn
            bw_h = p.get("bentuk_wajah", "oval")
            if bw_h == "bulat_chibi":
                # wajah chibi bulat tembam (Sari)
                ch_w, fy_top, fy_bot = 82, -52, 74
            elif bw_h == "lonjong":
                # wajah agak lonjong ramping elegan (Bu Guru)
                ch_w, fy_top, fy_bot = 68, -64, 84
            else:
                # wajah oval manis proporsional (Nadia, Ibu)
                ch_w, fy_top, fy_bot = 74, -58, 80
            # inner ciput melengkung halus (tanpa sudut tajam di pelipis!)
            ciput_c = gelap(hj_c, 0.16)
            c.blob(HH([
                (-ch_w * 0.90, -18), (-ch_w * 0.68, fy_top - 10), (0, fy_top - 18),
                (ch_w * 0.68, fy_top - 10), (ch_w * 0.90, -18),
                (ch_w * 0.80, -30), (0, fy_top + 4), (-ch_w * 0.80, -30),
            ]), ciput_c, 2.0 * s, oc_f, n=6)
            # BUKAAN WAJAH CHIBI MULUS SESUAI BENTUK WAJAH (bulat / oval / lonjong!)
            face_pts = [
                (0, fy_top), (ch_w * 0.56, fy_top + 8), (ch_w * 0.92, -16), (ch_w, 16),
                (ch_w * 0.94, 44), (ch_w * 0.64 + jx * 0.2, fy_bot - 10),
                (ch_w * 0.28 + jx * 0.4, fy_bot - 1), (jx, fy_bot),
                (-ch_w * 0.28 + jx * 0.4, fy_bot - 1), (-ch_w * 0.64, fy_bot - 10),
                (-ch_w * 0.94, 44), (-ch_w, 16), (-ch_w * 0.92, -16), (-ch_w * 0.56, fy_top + 8),
            ]
            c.blob(HH(face_pts), skin_c, 2.3 * s, oc_f, n=8)
            c.curve(HH([(ch_w - 8, 22), (ch_w * 0.64, fy_bot - 14), (10, fy_bot - 5)]), gelap(skin_c, 0.09), 6.5 * s)
            c.curve(HH([(-ch_w * 0.78, -22), (-ch_w * 0.40, fy_top + 6), (0, fy_top + 2),
                        (ch_w * 0.40, fy_top + 6), (ch_w * 0.78, -22)]), gelap(skin_c, 0.08), 4.5 * s)
            c.blob(HH(face_pts), None, 2.3 * s, oc_f, n=8)
            # garis lipatan hijab lembut memeluk dagu
            c.curve(HH([(-ch_w - 4, 24), (-ch_w * 0.74, fy_bot - 8), (-14, fy_bot + 3)]), hjd2, 2.0 * s)
            c.curve(HH([(ch_w + 4, 24), (ch_w * 0.74, fy_bot - 8), (14, fy_bot + 3)]), hjd2, 2.0 * s)
            if p.get("hijab_model") == "bergo":
                c.curve(HH([(-ch_w - 2, -16), (-ch_w * 0.58, fy_top - 4), (0, fy_top - 12),
                            (ch_w * 0.58, fy_top - 4), (ch_w + 2, -16)]), hjd2, 2.2 * s)
        else:
            skin_c = warna(p.get("kulit"), PUTIH)
            pintar = bool(p.get("wajah_pintar")) or bool(p.get("wajah_naa")) or bool(p.get("wajah_arka"))
            is_arka = bool(p.get("wajah_arka"))
            is_naa = bool(p.get("wajah_naa"))
            is_chibi_ref = bool(p.get("wajah_chibi_ref"))
            oc_f = (62, 48, 44) if is_chibi_ref else ((64, 52, 46) if p.get("outline_hangat") else OUT)
            if p.get("telinga") and not hij and kepala not in ("otak", "virus", "sel_imun"):
                bw_e = p.get("bentuk_wajah", "tirus")
                ear_x_base = 84 if bw_e == "bulat_chibi" else (67 if bw_e == "lonjong" else (72 if bw_e == "oval" else (79 if bw_e == "kotak" else 77)))
                for sg in (-1, 1):
                    if turn >= 0.70 and sg > 0:
                        continue
                    ex_ear = sg * ((ear_x_base if is_chibi_ref else face_rx + (-2 if is_arka else (-4 if pintar else 0)))) - (6.0 * turn if sg < 0 else 0.0)
                    erx = (15.5 if is_chibi_ref else (18.5 if is_arka else 13.5)) * s
                    ery = (18.5 if (is_arka or is_chibi_ref) else 18.0) * s
                    ey_ear = 14 if is_chibi_ref else (14 if is_arka else (10 if pintar else 6))
                    c.ell(*H(ex_ear, ey_ear), erx, ery, skin_c, 2.3 * s if is_chibi_ref else ow * .82, oc_f)
                    if is_chibi_ref:
                        c.ell(*H(ex_ear - sg * 2, ey_ear + 1), erx * 0.48, ery * 0.45, gelap(skin_c, 0.14))
                        c.curve(HH([(ex_ear - sg * 4, ey_ear - 4), (ex_ear + sg * 4, ey_ear + 1), (ex_ear - sg * 2, ey_ear + 8)]), oc_f, 1.8 * s)
                    elif pintar:
                        c.curve(HH([(ex_ear - sg * 4, 5), (ex_ear + sg * 5, 14), (ex_ear - sg * 3, 22)]), gelap(skin_c, 0.22), 2.4 * s)
            if is_chibi_ref:
                # 5 BENTUK WAJAH NYATA BERBEDA (bulat_chibi / oval / lonjong / tirus / kotak) — kurva mulus anti-kaku!
                jx = 8.0 * turn
                bw_f = p.get("bentuk_wajah", "tirus")
                if bw_f == "bulat_chibi":
                    # lebar-pendek, pipi bawah chubby gemoy manis (Adik, Bimo, Tika)
                    face_pts = [
                        (0, -76), (56, -66), (82, -26),
                        (88, 14), (84, 44), (64 + jx * 0.2, 66),
                        (36 + jx * 0.4, 75), (14 + jx * 0.6, 77), (jx, 78),
                        (-14 + jx * 0.4, 77), (-36, 75),
                        (-64, 66), (-84, 44), (-88, 14),
                        (-82, -26), (-56, -66),
                    ]
                elif bw_f == "lonjong":
                    # agak lonjong ramping elegan (Arka, Ayah, Formal)
                    face_pts = [
                        (0, -90), (46, -80), (67, -40),
                        (68, 2), (66, 34), (54 + jx * 0.2, 64),
                        (34 + jx * 0.4, 83), (14 + jx * 0.6, 91), (jx, 92),
                        (-14 + jx * 0.4, 91), (-34, 83),
                        (-54, 64), (-66, 34), (-68, 2),
                        (-67, -40), (-46, -80),
                    ]
                elif bw_f == "oval":
                    # oval lembut agak memanjang manis (Hana, Dimas)
                    face_pts = [
                        (0, -84), (49, -74), (72, -36),
                        (74, 4), (71, 34), (58 + jx * 0.2, 62),
                        (36 + jx * 0.4, 79), (15 + jx * 0.6, 86), (jx, 87),
                        (-15 + jx * 0.4, 86), (-36, 79),
                        (-58, 62), (-71, 34), (-74, 4),
                        (-72, -36), (-49, -74),
                    ]
                elif bw_f == "kotak":
                    # rahang bawah kokoh & lebih tegas kotak dewasa (Bos, Kakek, Pak Guru)
                    face_pts = [
                        (0, -86), (52, -76), (78, -38),
                        (80, 2), (79, 34), (74 + jx * 0.2, 60),
                        (54 + jx * 0.4, 78), (28 + jx * 0.6, 86), (jx, 87),
                        (-28 + jx * 0.4, 86), (-54, 78),
                        (-74, 60), (-79, 34), (-80, 2),
                        (-78, -38), (-52, -76),
                    ]
                else:
                    # "tirus" (Kribo, Raka): rahang V-shape tegas meruncing ke dagu
                    face_pts = [
                        (0, -84), (52, -74), (77, -38),
                        (79, -4), (76, 20), (68 + jx * 0.2, 46),
                        (44 + jx * 0.4, 70), (16 + jx * 0.6, 83), (jx, 85),
                        (-16 + jx * 0.4, 83), (-44, 70),
                        (-68, 46), (-76, 20), (-79, -4),
                        (-77, -38), (-52, -74),
                    ]
                c.blob(HH(face_pts), skin_c, 2.3 * s, oc_f, n=8)
                c.curve(HH([(face_pts[4][0] - 4, 24), (face_pts[5][0] - 4, face_pts[5][1]), (10, face_pts[8][1] - 4)]), gelap(skin_c, 0.08), 6.0 * s)
                c.blob(HH(face_pts), None, 2.3 * s, oc_f, n=8)
            elif is_naa or is_arka:
                # wajah chibi lembut pipi tembam manis & dagu bundar halus (persis gambar 1 & 2!)
                jx = 8.0 * turn
                w_k = 1.04 if is_arka else 1.02
                face_pts = [
                    (0, -face_ry * 0.96), (face_rx * 0.60 * w_k, -face_ry * 0.84), (face_rx * 0.96 * w_k, -face_ry * 0.32),
                    (face_rx * 1.00 * w_k, face_ry * 0.22), (face_rx * 0.84 * w_k + jx * 0.3, face_ry * 0.68),
                    (face_rx * 0.42 * w_k + jx * 0.6, face_ry * 0.94), (jx, face_ry * 1.00),
                    (-face_rx * 0.42 * w_k + jx * 0.4, face_ry * 0.94), (-face_rx * 0.84 * w_k, face_ry * 0.68),
                    (-face_rx * 1.00 * w_k, face_ry * 0.22), (-face_rx * 0.96 * w_k, -face_ry * 0.32),
                    (-face_rx * 0.60 * w_k, -face_ry * 0.84),
                ]
                c.blob(HH(face_pts), skin_c, ow * .82, OUT, n=6)
                c.curve(HH([(face_rx * 0.82, face_ry * 0.36), (face_rx * 0.56, face_ry * 0.78), (jx, face_ry * 0.94)]),
                        gelap(skin_c, 0.08), 8.0 * s)
                c.blob(HH(face_pts), None, ow * .82, OUT, n=6)
            elif pintar:
                # bentuk wajah anime Ghibli: pipi lembut meruncing ke dagu berkarakter (bukan lingkaran bola polos!)
                jx = 8.0 * turn
                face_pts = [
                    (0, -face_ry), (face_rx * 0.56, -face_ry * 0.86), (face_rx * 0.94, -face_ry * 0.36),
                    (face_rx * 0.96, face_ry * 0.14), (face_rx * 0.78 + jx * 0.3, face_ry * 0.62),
                    (face_rx * 0.34 + jx * 0.7, face_ry * 0.94), (jx, face_ry * 1.02),
                    (-face_rx * 0.34 + jx * 0.5, face_ry * 0.94), (-face_rx * 0.78, face_ry * 0.62),
                    (-face_rx * 0.96, face_ry * 0.14), (-face_rx * 0.94, -face_ry * 0.36),
                    (-face_rx * 0.56, -face_ry * 0.86),
                ]
                c.blob(HH(face_pts), skin_c, ow * .88, OUT, n=6)
                # bayangan lembut di pipi & bawah dagu (dimensi karakter anime Ghibli)
                c.curve(HH([(face_rx * 0.80, face_ry * 0.26), (face_rx * 0.56, face_ry * 0.72), (jx, face_ry * 0.94)]),
                        gelap(skin_c, 0.09), 9.0 * s)
                c.blob(HH(face_pts), None, ow * .88, OUT, n=6)
            else:
                face = HH(_ellpts(0, 0, face_rx, face_ry, 36))
                c.poly(face, skin_c, ow, OUT)
                shade_outer = arc_pts(0, 0, face_rx - 1.5, face_ry - 1.5, -15, 115, 20)
                shade_inner = []
                for k in range(20, -1, -1):
                    t_a = k / 20.0
                    ang = math.radians(-15 + 130 * t_a)
                    thick = 11.5 * math.sin(math.pi * t_a)
                    shade_inner.append((math.cos(ang) * (face_rx - 1.5 - thick),
                                        math.sin(ang) * (face_ry - 1.5 - thick)))
                c.poly(HH(shade_outer + shade_inner), gelap(skin_c, 0.075))
                c.poly(face, None, ow, OUT)
            # rambut depan
            if not hij:
                self._hair_front(c, H, HH, s, ow, r, hair_c, p)
            else:
                hjd2 = warna(p.get("hijab_tua"), gelap(warna(p["hijab"]), .15))
                c.curve(HH(arc_pts(0, 2, face_rx + 1, face_ry + 1, 200, 340, 12)), hjd2, 3.8 * s)
        # topi/peci
        if p.get("peci"):
            if p.get("wajah_chibi_ref"):
                c.poly(HH([(-66, -64), (-60, -106), (0, -116), (60, -106), (66, -64), (32, -56), (0, -54), (-32, -56)]),
                       (34, 34, 40), 2.8 * s, OUT)
                c.curve(HH([(-48, -98), (0, -106), (48, -98)]), (66, 66, 76), 2.2 * s)
            else:
                c.poly(HH([(-65, -72), (-58, -110), (0, -118), (58, -110), (65, -72), (0, -58)]), HITAM, ow, OUT)
        if p.get("topi"):
            tc = warna(p["topi"] if not isinstance(p["topi"], bool) else "merah", MERAH)
            c.blob(HH([(-80, -48), (-72, -104), (0, -124), (72, -104), (80, -48), (0, -42)]), tc, ow, OUT)
            c.poly(HH([(38, -52), (120, -44), (120, -34), (38, -39)]), gelap(tc, .15), ow * .8, OUT)

        # fitur wajah (bergeser natural ke kanan +x lokal saat hadap miring 3/4)
        lx_, ly_ = look
        fs = 0.90 if hij else 0.94
        chibi_eye = bool(p.get("mata_chibi"))
        is_naa_f = bool(p.get("wajah_naa"))
        is_arka_f = bool(p.get("wajah_arka"))
        is_chibi_ref_f = bool(p.get("wajah_chibi_ref"))
        fx0, fy0 = lx_ * 14 + yaw_x, ly_ * 7.5
        eyes = ex["eyes"]
        blink = st.get("blink", 0.0)
        # jarak antar mata lebar & posisi sedikit lebih rendah untuk karakter chibi anime agar tidak berdesakan!
        if is_chibi_ref_f:
            eye_sep = 37.5 * (1.0 - 0.16 * turn)
            eye_y = 12.0 + fy0
        elif is_naa_f:
            eye_sep = 43.0 * (1.0 - 0.16 * turn)
            eye_y = 12.0 + fy0
        elif is_arka_f:
            eye_sep = 42.0 * (1.0 - 0.16 * turn)
            eye_y = 12.0 + fy0
        else:
            eye_sep = (33 if chibi_eye else 32) * fs * (1.0 - 0.16 * turn)
            eye_y = (9 if chibi_eye else -3) * fs + fy0
        # mata depan (i=1) lebih dekat tepi depan, mata belakang (i=0) sedikit lebih dekat tengah
        ec = (-eye_sep * (1.0 + 0.06 * turn), eye_sep * (1.0 - 0.08 * turn))
        ew = 11.2 * (0.94 if mask else 1.0)
        eh = 16.5 * (1.10 if fem else (0.92 if mask else 1.0))
        hlk = ex.get("hl", 1.0) * (0.88 if mask else 1.0)
        # lensa kacamata digambar SEBELUM mata agar tidak menutupi mata/kilau
        hw, hh_g, rad_g = 27.5 * fs * (1.0 - 0.12 * turn), 20.5 * fs, 8.5 * fs
        r_bulat = 27.5 * fs * (1.0 - 0.10 * turn)
        if p.get("kacamata") == "kotak":
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = hw * (1.0 - 0.14 * turn if i == 1 else 1.0)
                frame = _rectpts(gx - hw_i, gy - hh_g, gx + hw_i, gy + hh_g, rad_g, 6)
                c.poly(HH(frame), (255, 255, 255, 225))
        elif p.get("kacamata") == "browline":
            # lensa bening lebar browline (gambar 2 Arka)
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 4
                rx_p = 35.5 * (1.0 - 0.14 * turn if i == 1 else 1.0)
                ry_p = 27.0
                c.poly(HH(_ellpts(gx, gy, rx_p, ry_p, 28)), (242, 248, 255, 58))
                c.line(HH([(gx - rx_p * 0.48, gy - ry_p * 0.30), (gx - rx_p * 0.12, gy - ry_p * 0.62)]), (255, 255, 255, 130), 2.8 * s)
        elif p.get("kacamata") == "pintar_kotak":
            # kacamata kotak-membulat tipis elegan khas Kribo (tidak menutupi ekspresi mata!)
            big_g = 1.06 if p.get("wajah_chibi_ref") else 1.0
            big_h = 1.08 if p.get("wajah_chibi_ref") else 1.0
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = (28.5 * big_g * fs) * (1.0 - 0.14 * turn if i == 1 else 1.0)
                hh_i = 22.0 * big_h * fs
                frame = _rectpts(gx - hw_i, gy - hh_i, gx + hw_i, gy + hh_i, 10.5 * fs, 6)
                c.poly(HH(frame), (236, 248, 255, 36))
                c.line(HH([(gx - hw_i * 0.55, gy - hh_i * 0.32), (gx - hw_i * 0.14, gy - hh_i * 0.64)]), (255, 255, 255, 115), 2.6 * s)
        elif p.get("kacamata") == "pintar":
            # kacamata pintar Ghibli: lensa kaca bening tipis + pantulan kilau diagonal halus (mata tetap hidup!)
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                rx_p = (27.0 * fs) * (1.0 - 0.14 * turn if i == 1 else 1.0)
                ry_p = 22.5 * fs
                c.poly(HH(_ellpts(gx, gy, rx_p, ry_p, 26)), (236, 248, 255, 62))
                c.line(HH([(gx - rx_p * 0.48, gy - ry_p * 0.36), (gx - rx_p * 0.12, gy - ry_p * 0.62)]), (255, 255, 255, 130), 3.0 * s)
        elif p.get("kacamata") == "bulat":
            for i, ex_ in enumerate(ec):
                rx_b = r_bulat * (1.0 - 0.14 * turn if i == 1 else 1.0)
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, rx_b, r_bulat, 26)), (255, 255, 255, 58))

        for i, ex_ in enumerate(ec):
            ex_ = ex_ + fx0
            if eyes in ("oval", "wide", "spark", "dot", "half", "wink") and not (eyes == "wink" and i == 1):
                if p.get("wajah_chibi_ref") and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    self._eye_ref(c, HH, s, ex_, eye_y, i, eyes, blink, turn, lx_, ly_)
                elif False:
                    # MATA CHIBI REFERENSI: besar bulat hangat, kelopak atas tebal lembut, iris 2-tone coklat/hazel + kilau besar!
                    sc = 1.10 if eyes == "wide" else 1.0
                    ew_r = 22.5 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
                    eh_r = (24.0 * 0.52 if eyes == "half" else 24.0 * sc) * (1.0 - 0.9 * blink)
                    iris_c = warna(p.get("iris"), (96, 68, 52))
                    iris_lt = terang(mix(iris_c, (216, 174, 128), 0.48), 0.18)
                    line_c = (66, 44, 38)
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_r, max(1.8, eh_r), 22)), PUTIH)
                    if eh_r > 5.5:
                        ir_w = 16.5 * sc * (1.0 - 0.12 * turn if i == 1 else 1.0)
                        ir_h = min(eh_r * 0.92, 18.8 * sc)
                        ix = ex_ + lx_ * 4.5 + (2.5 * turn)
                        iy = eye_y + 3.0 + ly_ * 2.5
                        # iris 2-tone coklat-hangat (gelap atas -> terang lembut bawah)
                        c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 20)), gelap(iris_c, 0.25), 1.6 * s, line_c)
                        c.poly(HH(_ellpts(ix, iy + ir_h * 0.24, ir_w * 0.80, ir_h * 0.56, 16)), iris_lt)
                        c.poly(HH(_ellpts(ix, iy - ir_h * 0.06, ir_w * 0.48, ir_h * 0.48, 14)), (48, 34, 28))
                        # 2 kilau putih jernih (1 besar kiri-atas, 1 kecil kanan-bawah)
                        c.poly(HH(_ellpts(ix - ir_w * 0.36, iy - ir_h * 0.36, 5.4, 5.4, 12)), PUTIH)
                        c.poly(HH(_ellpts(ix + ir_w * 0.34, iy + ir_h * 0.34, 2.4, 2.4, 8)), PUTIH)
                    # kelopak atas tebal melengkung lembut + garis lipatan tipis di atasnya
                    c.curve(HH(arc_pts(ex_, eye_y + 2, ew_r + 1.2, max(2.2, eh_r + 1.0), 192, 348, 16)), line_c, 5.8 * s)
                    if eh_r > 6.0:
                        c.curve(HH(arc_pts(ex_, eye_y + 2, ew_r * 0.82, eh_r, 30, 150, 8)), (128, 96, 86), 1.8 * s)
                elif p.get("wajah_arka") and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    # MATA MASKULIN TENANG & CERDAS (persis cowok gambar 2: kelopak atas agak lurus, iris abu-ungu lembut!)
                    sc = 1.12 if eyes == "wide" else 1.0
                    ew_a = 18.5 * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
                    eh_a = (13.5 * 0.56 if eyes == "half" else 13.5 * sc) * (1.0 - 0.9 * blink)
                    iris_c = warna(p.get("iris"), (118, 122, 144))
                    iris_lt = terang(iris_c, 0.34)
                    line_c = (56, 50, 58)
                    c.poly(HH(_ellpts(ex_, eye_y + 4, ew_a, max(1.6, eh_a), 20)), PUTIH)
                    if eh_a > 4.5:
                        ir_w = 11.2 * (1.0 - 0.12 * turn if i == 1 else 1.0)
                        ir_h = min(eh_a * 0.92, 11.5)
                        ix = ex_ + lx_ * 4.5 + (2.5 * turn)
                        iy = eye_y + 4.5 + ly_ * 2.5
                        c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 18)), gelap(iris_c, 0.16), 1.4 * s, line_c)
                        c.poly(HH(_ellpts(ix, iy + ir_h * 0.22, ir_w * 0.78, ir_h * 0.54, 14)), iris_lt)
                        c.poly(HH(_ellpts(ix, iy - ir_h * 0.08, ir_w * 0.44, ir_h * 0.44, 12)), (54, 54, 68))
                        c.poly(HH(_ellpts(ix - ir_w * 0.38, iy - ir_h * 0.28, 3.8, 3.6, 10)), PUTIH)
                    # kelopak atas datar-tegas + lipatan kelopak atas tipis
                    c.curve(HH([(ex_ - ew_a - 1, eye_y + 2), (ex_, eye_y - eh_a + 3), (ex_ + ew_a + 1, eye_y + 2)]), line_c, 4.6 * s)
                    c.curve(HH([(ex_ - ew_a * 0.75, eye_y - eh_a - 4), (ex_, eye_y - eh_a - 7), (ex_ + ew_a * 0.75, eye_y - eh_a - 4)]), (126, 108, 104), 2.0 * s)
                elif (p.get("wajah_pintar") or p.get("wajah_naa")) and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    # MATA CHIBI GHIBLI SOFT (gambar 1 @naa: bulat besar berbinar + iris 2-tone teal bercahaya)
                    sc = 1.12 if eyes == "wide" else 1.0
                    big = 1.14 if p.get("wajah_naa") else 1.0
                    ew_p = 17.5 * big * sc * (1.0 - 0.14 * turn if i == 1 else 1.0)
                    eh_p = (19.5 * big * 0.52 if eyes == "half" else 19.5 * big * sc) * (1.0 - 0.9 * blink)
                    iris_c = warna(p.get("iris"), (62, 122, 124))
                    iris_lt = terang(mix(iris_c, (172, 232, 224), 0.45), 0.18)
                    line_c = (62, 50, 44) if p.get("outline_hangat") else OUT
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_p, max(1.8, eh_p), 22)), PUTIH)
                    if eh_p > 5.0:
                        ir_w = (10.5 if eyes == "wide" else 12.2) * big * (1.0 - 0.12 * turn if i == 1 else 1.0)
                        ir_h = min(eh_p * 0.90, 14.8 * big)
                        ix = ex_ + lx_ * 4.5 + (2.5 * turn)
                        iy = eye_y + 2.5 + ly_ * 2.5
                        c.poly(HH(_ellpts(ix, iy, ir_w, ir_h, 18)), gelap(iris_c, 0.22), 1.6 * s, line_c)
                        c.poly(HH(_ellpts(ix, iy + ir_h * 0.24, ir_w * 0.78, ir_h * 0.56, 14)), iris_lt)
                        c.poly(HH(_ellpts(ix, iy - ir_h * 0.06, ir_w * 0.48, ir_h * 0.48, 12)), (42, 46, 52))
                        c.poly(HH(_ellpts(ix - ir_w * 0.36, iy - ir_h * 0.34, 4.4, 4.4, 10)), PUTIH)
                        c.poly(HH(_ellpts(ix + ir_w * 0.32, iy + ir_h * 0.34, 2.2, 2.2, 8)), PUTIH)
                    c.curve(HH(arc_pts(ex_, eye_y + 1.5, ew_p + 1.0, max(2.0, eh_p + 0.8), 192, 348, 14)), line_c, 4.8 * s)
                    if eh_p > 5.5:
                        c.curve(HH(arc_pts(ex_, eye_y + 2, ew_p * 0.85, eh_p, 26, 154, 8)), (110, 92, 82), 1.8 * s)
                    if p.get("bulu_mata") and eh_p > 5.5:
                        sg_e = -1 if i == 0 else 1
                        c.line(HH([(ex_ + sg_e * (ew_p - 1), eye_y - 3), (ex_ + sg_e * (ew_p + 7), eye_y - 10)]), line_c, 3.8 * s)
                elif mask and eyes in ("oval", "wide", "spark", "dot", "half", "wink"):
                    # mata ekspresif berkilau (mengikuti uji-kribo 3D-stickman versi 2D)
                    sc = 1.15 if eyes == "wide" else 1.0
                    ew_m = 9.4 * sc
                    hh = (12.2 * 0.52 if eyes == "half" else 12.2 * sc) * (1 - 0.9 * blink)
                    if eyes == "dot":
                        c.poly(HH(_ellpts(ex_, eye_y + 2, 11.5, 11.5, 16)), PUTIH, ow * .75, OUT)
                        c.poly(HH(_ellpts(ex_ + lx_ * 3, eye_y + 2, 4.2, 4.2, 10)), OUT)
                    else:
                        c.poly(HH(_ellpts(ex_, eye_y + 2, ew_m, max(1.6, hh), 18)), OUT)
                        if hh > 5.0:
                            c.poly(HH(_ellpts(ex_ - 3.0, eye_y + 2 - hh * .32, 3.6 * hlk, 3.6 * hlk, 10)), PUTIH)
                            c.poly(HH(_ellpts(ex_ + 3.0, eye_y + 2 + hh * .28, 1.7, 1.7, 8)), PUTIH)
                        if eyes == "half":
                            c.line(HH([(ex_ - ew_m - 2.5, eye_y + 2 - hh * .42), (ex_ + ew_m + 2.5, eye_y + 2 - hh * .42)]), OUT, 4.2 * s)
                elif chibi_eye and eyes in ("oval", "wide", "spark", "half", "wink"):
                    # mata bulat besar berkilau (gaya chibi anime imut)
                    sc = 1.15 if eyes == "wide" else 1.0
                    ew_c = 16.0 * sc
                    hh = 18.8 * sc * (1 - 0.9 * blink)
                    if eyes == "half":
                        hh = 18.8 * 0.52
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_c, max(1.8, hh), 20)), OUT)
                    if hh > 6:
                        c.curve(HH(arc_pts(ex_, eye_y + 1, ew_c + 1.4, hh + 1.0, 200, 340, 10)), OUT, 4.0 * s)
                        c.poly(HH(_ellpts(ex_ - 5.2, eye_y + 2 - hh * .30, 5.8 * hlk, 5.8 * hlk, 12)), PUTIH)
                        c.poly(HH(_ellpts(ex_ + 5.0, eye_y + 2 + hh * .32, 2.6, 2.6, 10)), PUTIH)
                    if eyes == "spark" and hh > 6:
                        c.poly(HH(_ellpts(ex_ - 4.5, eye_y + 2 + hh * .36, 2.4, 2.4, 8)), PUTIH)
                    if eyes == "half":
                        c.line(HH([(ex_ - ew_c - 3, eye_y + 2 - hh * .4), (ex_ + ew_c + 3, eye_y + 2 - hh * .4)]), OUT, 4.6 * s)
                elif p.get("mata_sclera") and eyes in ("oval", "wide", "spark", "half", "wink"):
                    sc = 1.18 if eyes == "wide" else 1.0
                    ew_s = 14.5 * sc
                    eh_s = 16.5 * sc * (1 - 0.9 * blink)
                    c.poly(HH(_ellpts(ex_, eye_y + 2, ew_s, max(1.8, eh_s), 20)), PUTIH, 3.8 * s, OUT)
                    pr = (5.0 if eyes == "wide" else 6.2) * (1.0 if blink < 0.5 else 0.4)
                    px_, py_ = ex_ + lx_ * 4.5, eye_y + 2 + ly_ * 3.0
                    c.poly(HH(_ellpts(px_, py_, pr, pr * (1 - 0.85 * blink), 14)), OUT)
                    if eh_s > 6 and blink < 0.5:
                        c.poly(HH(_ellpts(px_ - 2.0, py_ - 2.2, 2.2, 2.2, 8)), PUTIH)
                    if eyes == "half" and blink < 0.5:
                        lid_top = arc_pts(ex_, eye_y + 2, ew_s + 0.5, eh_s + 0.5, 185, 355, 12)
                        c.poly(HH(lid_top + [(ex_ + ew_s + 0.5, eye_y + 1), (ex_ - ew_s - 0.5, eye_y + 1)]),
                               warna(p.get("kulit"), PUTIH))
                        c.poly(HH(_ellpts(ex_, eye_y + 2, ew_s, eh_s, 20)), None, 3.8 * s, OUT)
                        c.line(HH([(ex_ - ew_s - 2, eye_y + 1), (ex_ + ew_s + 2, eye_y + 1)]), OUT, 4.0 * s)
                else:
                    sc = 1.3 if eyes == "wide" else 1.0
                    hh = eh * sc * (1 - 0.9 * blink)
                    if eyes == "half":
                        hh = eh * 0.52
                    if eyes == "dot":
                        c.poly(HH(_ellpts(ex_, eye_y, 13, 13, 16)), PUTIH, ow * .8, OUT)
                        c.poly(HH(_ellpts(ex_ + lx_ * 3, eye_y, 4.5, 4.5, 10)), OUT)
                    else:
                        c.poly(HH(_ellpts(ex_, eye_y, ew * sc, hh, 18)), OUT)
                        if hh > 6 and eyes != "wide":
                            c.poly(HH(_ellpts(ex_ - 3.5, eye_y - hh * .38, 4.6 * hlk, 4.6 * hlk, 10)), PUTIH)
                        if eyes == "wide" and hh > 6:
                            c.poly(HH(_ellpts(ex_ - 3, eye_y - hh * .3, 4, 4, 10)), PUTIH)
                    if eyes == "spark":
                        c.poly(HH(_ellpts(ex_ + 4, eye_y + 6, 3.6, 3.6, 8)), PUTIH)
                    if eyes == "half":
                        c.line(HH([(ex_ - ew - 3, eye_y - hh * .4), (ex_ + ew + 3, eye_y - hh * .4)]), OUT, 5 * s)
            if eyes == "arc_up" or (eyes == "wink" and i == 1):      # ^ ^
                c.curve(HH(arc_pts(ex_, eye_y + 8, 15, 15, 200, 340, 10)), OUT, 5.2 * s)
            if eyes == "arc_dn":                                       # ⌣ ⌣
                c.curve(HH(arc_pts(ex_, eye_y - 4, 15, 12, 20, 160, 10)), OUT, 5.2 * s)
            if fem and p.get("bulu_mata", True) and eyes in ("oval", "wide", "spark", "half", "wink", "dot"):
                sg = -1 if i == 0 else 1
                for k in (0, 1):
                    c.line(HH([(ex_ + sg * 11, eye_y - 10 + k * 7), (ex_ + sg * (19 + k * 2), eye_y - 18 + k * 8)]), OUT, 3.6 * s)

        # bingkai kacamata (di atas mata)
        if p.get("kacamata") == "kotak":
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = hw * (1.0 - 0.14 * turn if i == 1 else 1.0)
                frame = _rectpts(gx - hw_i, gy - hh_g, gx + hw_i, gy + hh_g, rad_g, 6)
                c.poly(HH(frame), None, 4.8 * s, OUT)
            hw0, hw1 = hw, hw * (1.0 - 0.14 * turn)
            c.line(HH([(ec[0] + fx0 + hw0, eye_y - 1), (ec[1] + fx0 - hw1, eye_y - 1)]), OUT, 4.8 * s)
            # tangkai kacamata: saat miring, tangkai sisi belakang (-1) memanjang ke telinga, sisi depan (+1) sangat pendek
            gx_l = ec[0] + fx0 - hw0
            c.line(HH([(gx_l, eye_y - 2), (-face_rx + 2, eye_y - 6)]), OUT, 4.0 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + hw1
                c.line(HH([(gx_r, eye_y - 2), (min(face_rx - 2, gx_r + 12 * (1.0 - turn)), eye_y - 6)]), OUT, 4.0 * s)
        elif p.get("kacamata") == "browline":
            # kacamata browline lebar & elegan (persis gambar 2 Arka: atas tebal gelap, bawah tipis)
            fr_c = (62, 54, 62)
            rx_l = 35.5
            rx_r = 35.5 * (1.0 - 0.14 * turn)
            ry_p = 27.0
            for i, ex_ in enumerate(ec):
                rx_i = rx_r if i == 1 else rx_l
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 4, rx_i, ry_p, 28)), None, 2.6 * s, fr_c)
                c.curve(HH(arc_pts(ex_ + fx0, eye_y + 4, rx_i, ry_p, 192, 348, 14)), fr_c, 5.4 * s)
            c.curve(HH([(ec[0] + fx0 + rx_l, eye_y + 1), (fx0, eye_y - 6), (ec[1] + fx0 - rx_r, eye_y + 1)]), fr_c, 3.6 * s, n=6)
            gx_l = ec[0] + fx0 - rx_l
            c.line(HH([(gx_l, eye_y - 1), (-face_rx + 2, eye_y + 3)]), fr_c, 3.8 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + rx_r
                c.line(HH([(gx_r, eye_y - 1), (min(face_rx - 2, gx_r + 12 * (1.0 - turn)), eye_y + 3)]), fr_c, 3.8 * s)
        elif p.get("kacamata") == "pintar_kotak":
            # bingkai kacamata kotak tipis-elegan khas Kribo
            fr_c = (68, 48, 44) if p.get("wajah_chibi_ref") else (48, 44, 46)
            big_g = 1.06 if p.get("wajah_chibi_ref") else 1.0
            big_h = 1.08 if p.get("wajah_chibi_ref") else 1.0
            hw0 = 28.5 * big_g * fs
            hw1 = (28.5 * big_g * fs) * (1.0 - 0.14 * turn)
            hh_i = 22.0 * big_h * fs
            for i, ex_ in enumerate(ec):
                gx, gy = ex_ + fx0, eye_y + 2
                hw_i = hw1 if i == 1 else hw0
                frame = _rectpts(gx - hw_i, gy - hh_i, gx + hw_i, gy + hh_i, 10.5 * fs, 6)
                c.poly(HH(frame), None, 2.2 * s, fr_c)
            c.line(HH([(ec[0] + fx0 + hw0, eye_y - 1), (ec[1] + fx0 - hw1, eye_y - 1)]), fr_c, 2.2 * s)
            gx_l = ec[0] + fx0 - hw0
            c.line(HH([(gx_l, eye_y - 1), (-78.0, eye_y + 3)]), fr_c, 2.0 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + hw1
                c.line(HH([(gx_r, eye_y - 1), (min(78.0, gx_r + 12 * (1.0 - turn)), eye_y + 3)]), fr_c, 2.0 * s)
        elif p.get("kacamata") == "pintar":
            # bingkai kacamata kawat tipis-elegan ala karakter pintar Ghibli
            fr_c = (44, 42, 48)
            rx_l = 27.0 * fs
            rx_r = (27.0 * fs) * (1.0 - 0.14 * turn)
            ry_p = 22.5 * fs
            for i, ex_ in enumerate(ec):
                rx_i = rx_r if i == 1 else rx_l
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, rx_i, ry_p, 28)), None, 3.2 * s, fr_c)
            # bridge melengkung halus di pangkal hidung
            c.curve(HH([(ec[0] + fx0 + rx_l, eye_y + 1), (fx0, eye_y - 4),
                        (ec[1] + fx0 - rx_r, eye_y + 1)]), fr_c, 3.0 * s, n=6)
            # tangkai kawat halus ke telinga
            gx_l = ec[0] + fx0 - rx_l
            c.line(HH([(gx_l, eye_y - 1), (-face_rx + 3, eye_y + 2)]), fr_c, 2.8 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + rx_r
                c.line(HH([(gx_r, eye_y - 1), (min(face_rx - 3, gx_r + 12 * (1.0 - turn)), eye_y + 2)]), fr_c, 2.8 * s)
        elif p.get("kacamata") == "bulat":
            fr_b = (68, 48, 40) if p.get("outline_hangat") else OUT
            bw_g = p.get("bentuk_wajah", "oval")
            w_edge = 68.0 if bw_g == "lonjong" else (74.0 if bw_g == "oval" else 78.0)
            rb_eff = r_bulat * (0.94 if bw_g == "lonjong" else 1.0)
            for i, ex_ in enumerate(ec):
                rx_b = rb_eff * (1.0 - 0.14 * turn if i == 1 else 1.0)
                c.poly(HH(_ellpts(ex_ + fx0, eye_y + 2, rx_b, rb_eff, 32)), None, 2.3 * s, fr_b)
            rx_r = rb_eff * (1.0 - 0.14 * turn)
            c.curve(HH([(ec[0] + fx0 + rb_eff, eye_y + 1), (fx0, eye_y - 3),
                        (ec[1] + fx0 - rx_r, eye_y + 1)]), fr_b, 2.2 * s, n=6)
            gx_l = ec[0] + fx0 - rb_eff
            c.line(HH([(gx_l, eye_y - 1), (max(-w_edge, gx_l - 12.0), eye_y + 1)]), fr_b, 2.0 * s)
            if turn < 0.65:
                gx_r = ec[1] + fx0 + rx_r
                c.line(HH([(gx_r, eye_y - 1), (min(w_edge, gx_r + 12.0 * (1.0 - turn)), eye_y + 1)]), fr_b, 2.0 * s)
        elif p.get("kacamata"):
            for ex_ in ec:
                c.poly(HH(_ellpts(ex_ + fx0, eye_y, 27 * (1.0 - 0.12 * turn), 27, 22)), (255, 255, 255, 70), ow * .95, OUT)
            c.line(HH([(ec[0] + 27 * (1.0 - 0.12 * turn) + fx0, eye_y - 3), (ec[1] - 27 * (1.0 - 0.12 * turn) + fx0, eye_y - 3)]), OUT, 4.2 * s)
        # hidung mungil (aktif saat hadap miring 3/4, atau hidung tipis halus pada wajah_pintar)
        if turn >= 0.28:
            nx_n = fx0 + 6.0 * turn
            ny_n = eye_y + 24.0 * fs
            c.curve(HH([(nx_n - 2.0, ny_n - 5.0), (nx_n + 5.5 * turn, ny_n + 1.0), (nx_n - 1.0, ny_n + 5.5)]), OUT, 3.2 * s)
        elif p.get("wajah_chibi_ref"):
            gm = p.get("gaya_mata", "fokus")
            if gm in ("ghibli_bulat", "ghibli_lembut", "chibi_hijab"):
                # hidung titik/lengkung mungil khas Studio Ghibli / Chibi + 3 goresan blush pipi hangat lembut
                nx_n = fx0 + 1.0
                ny_n = eye_y + (26.0 if gm == "chibi_hijab" else 23.0)
                if gm == "chibi_hijab":
                    c.ell(*H(nx_n, ny_n), 1.8 * s, 2.2 * s, (116, 78, 64))
                else:
                    c.curve(HH([(nx_n - 1.8, ny_n - 1.5), (nx_n + 1.5, ny_n + 1.2), (nx_n - 1.0, ny_n + 2.8)]), (142, 102, 86), 2.0 * s)
                for sg_b in (-1, 1):
                    if turn >= 0.72 and sg_b > 0:
                        continue
                    bx_g = fx0 + sg_b * (48 if gm == "chibi_hijab" else 46) * (1.0 - 0.16 * turn)
                    by_g = eye_y + (28.0 if gm == "chibi_hijab" else 24.0)
                    c.poly(HH(_ellpts(bx_g, by_g, 13.5 if gm == "chibi_hijab" else 11.5, 7.2 if gm == "chibi_hijab" else 6.2, 12)), (242, 160, 134, 82))
                    for dk in ((-4.5, 0.0, 4.5) if gm == "chibi_hijab" else (-3.2, 2.2)):
                        c.line(HH([(bx_g + dk + 1.6, by_g - 3.0), (bx_g + dk - 1.6, by_g + 3.0)]), (218, 136, 110), 1.5 * s)
            else:
                # hidung cowok tegas minimalis: garis batang + sudut hidung kecil
                nx_n = fx0 + 1.5
                ny_n = eye_y + 23.0
                c.line(HH([(nx_n - 0.5, ny_n - 6.0), (nx_n + 2.0, ny_n + 1.0), (nx_n - 2.0, ny_n + 3.0)]), (136, 98, 84), 2.1 * s)
        elif p.get("wajah_pintar"):
            nx_n = fx0 + 1.5
            ny_n = eye_y + 23.0 * fs
            c.curve(HH([(nx_n - 1.0, ny_n - 3.5), (nx_n + 2.5, ny_n + 1.5), (nx_n - 1.5, ny_n + 3.5)]), (136, 98, 82), 2.4 * s)
        # tahi lalat mungil khas karakter (mis. Hana di bawah mata kiri)
        if p.get("tahi_lalat") and turn < 0.72:
            c.ell(*H(fx0 + 34 * (1.0 - 0.16 * turn), eye_y + 23.0), 2.1 * s, 2.1 * s, (78, 54, 46))
        # freckles tipis khas karakter pintar / anak Ghibli di pipi kiri & kanan
        if p.get("freckles"):
            fc_dot = (176, 128, 104, 150)
            for sg in (-1, 1):
                if turn >= 0.72 and sg > 0:
                    continue
                bx_f = fx0 + sg * 38 * fs * (1.0 - 0.16 * turn)
                by_f = eye_y + 25 * fs
                for dx_, dy_ in ((-6, 0), (0, 3), (6, -1)):
                    c.ell(*H(bx_f + dx_, by_f + dy_), 1.8 * s, 1.5 * s, fc_dot)

        # alis
        br = ex.get("brow")
        if br:
            lift, tl, tr = br
            for i, (bx, tv) in enumerate(((ec[0], tl), (ec[1], tr))):
                sg = -1 if i == 0 else 1
                by = eye_y - 29 * fs - lift - (5 if p.get("kacamata") in ("kotak", "bulat") else 0)
                outer = (bx + fx0 + sg * 16, by + tv * 10)
                inner = (bx + fx0 - sg * 16, by - tv * 10)
                mid = (bx + fx0, by - 4 + (4 if abs(tv) > .5 else 0) + (-5 if lift > 6 else 0))
                c.curve(HH([outer, mid, inner]), OUT, (5.2 if mask else (4.2 if chibi_eye else 5.0)) * s)
        elif p.get("wajah_chibi_ref"):
            gm = p.get("gaya_mata", "fokus")
            if p.get("bulu_mata") or gm in ("ghibli_bulat", "chibi_hijab"):
                # alis melengkung halus natural khas Studio Ghibli / Chibi
                br_c = (72, 46, 36) if p.get("hijab") else (gelap(hair_c, 0.15) if p.get("rambut") not in (None, "botak") else (72, 54, 46))
                for i, bx in enumerate(ec):
                    sg = -1 if i == 0 else 1
                    by = eye_y - (29.5 if gm == "chibi_hijab" else (25.5 if gm == "ghibli_bulat" else 24.0))
                    c.curve(HH([(bx + fx0 - sg * 14, by + 2.8), (bx + fx0, by - 3.8), (bx + fx0 + sg * 15, by + 2.0)]),
                            br_c, 3.0 * s)
            elif gm == "ghibli_dewasa":
                # alis dewasa tenang sedikit tebal & berwibawa
                br_c = (132, 134, 144) if p.get("rambut") == "uban" else (58, 48, 46)
                for i, bx in enumerate(ec):
                    sg = -1 if i == 0 else 1
                    by = eye_y - 20.5
                    c.curve(HH([(bx + fx0 - sg * 16, by + 2.0), (bx + fx0, by - 2.5), (bx + fx0 + sg * 17, by + 1.0)]),
                            br_c, 4.2 * s)
            else:
                # alis cowok tegas khas Kribo (warna ikut uban bila rambut abu-abu)
                br_c = (118, 120, 130) if p.get("rambut") == "uban" else (28, 22, 24)
                for i, bx in enumerate(ec):
                    sg = -1 if i == 0 else 1
                    by = eye_y - 21.5
                    c.poly(HH([
                        (bx + fx0 - sg * 17, by + 4.5),
                        (bx + fx0 - sg * 15, by - 1.5),
                        (bx + fx0 + sg * 6, by - 6.0),
                        (bx + fx0 + sg * 20, by - 2.0),
                        (bx + fx0 + sg * 17, by + 1.5),
                        (bx + fx0 + sg * 4, by - 1.2),
                    ]), br_c)
                    c.line(HH([(bx + fx0 - sg * 15, by + 5.5), (bx + fx0 - sg * 12, by + 8.0)]), (148, 110, 96), 1.4 * s)
        elif p.get("alis_tebal"):
            # alis tebal maskulin meruncing lembut di ujung luar (bukan kotak kaku!)
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 26
                c.poly(HH([
                    (bx + fx0 - sg * 20, by + 3), (bx + fx0 - sg * 18, by - 6),
                    (bx + fx0 + sg * 8, by - 7), (bx + fx0 + sg * 22, by - 1),
                    (bx + fx0 + sg * 18, by + 3), (bx + fx0 - sg * 10, by + 4),
                ]), (58, 56, 68))
        elif p.get("wajah_naa"):
            # alis melengkung tipis manis di atas mata besar (persis cewek @naa gambar 1!)
            for i, bx in enumerate(ec):
                by = eye_y - 31
                c.curve(HH([(bx + fx0 - 15, by + 3), (bx + fx0, by - 4), (bx + fx0 + 15, by + 3)]), (72, 56, 46), 3.0 * s)
        elif mask:
            # alis melengkung halus di atas kacamata (gaya uji-kribo 3D-stickman)
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 31 * fs
                c.curve(HH([(bx + fx0 + sg * 14, by + 2.5), (bx + fx0, by - 2.5),
                            (bx + fx0 - sg * 13, by + 1.5)]), OUT, 4.6 * s)
        elif chibi_eye or p.get("mata_sclera"):
            # alis melengkung lembut di atas kacamata bulat
            for i, bx in enumerate(ec):
                sg = -1 if i == 0 else 1
                by = eye_y - 34 * fs
                c.curve(HH([(bx + fx0 + sg * 14, by + 3), (bx + fx0, by - 2),
                            (bx + fx0 - sg * 13, by + 2)]), OUT, 3.8 * s)

        # pipi blush hangat + 3 garis miring kecil /// (khas chibi Ghibli gambar 1 & 2)
        if p.get("pipi_garis"):
            for sg in (-1, 1):
                if turn >= 0.72 and sg > 0:
                    continue
                bx_p = fx0 + sg * 48 * fs * (1.0 - 0.16 * turn)
                by_p = eye_y + 28 * fs
                c.poly(HH(_ellpts(bx_p, by_p, 16, 9.5, 14)), (242, 166, 134, 92))
                for k in (-5.5, 0.0, 5.5):
                    c.line(HH([(bx_p + k + 2.5, by_p - 4.5), (bx_p + k - 2.5, by_p + 4.5)]), (214, 134, 108), 2.0 * s)
        # pipi (hilangkan blush pink lebar pada mode maskulin kecuali saat sangat malu)
        bl = ex.get("blush", 0.0)
        if mask:
            bl = 0.45 if bl >= 0.95 else 0.0
        elif chibi_eye and bl > 0.02:
            bl = max(bl, 0.55)
        if bl > 0.02 and not p.get("wajah_chibi_ref"):
            bx_off = 48 if chibi_eye else 58
            by_off = (eye_y + 24 * fs) if chibi_eye else (28 * fs + fy0 * .4)
            for sg in (-1, 1):
                c.poly(HH(_ellpts(sg * bx_off * fs + fx0 * .6, by_off, 17, 10.5, 16)), (255, 140, 160, int(150 * bl)))
        # mulut
        self._mouth(c, st, ex, HH, s, ow, fs, fx0, fy0)
        # kumis jenggot
        if p.get("kumis"):
            uc = hair_c if p.get("rambut") != "botak" else (216, 218, 224)
            if p.get("wajah_chibi_ref"):
                kx_, ky_ = fx0 * 0.7, 36.5 + fy0 * 0.4
                c.blob(HH([
                    (kx_ - 28, ky_ + 3), (kx_ - 13, ky_ - 4), (kx_, ky_),
                    (kx_ + 13, ky_ - 4), (kx_ + 28, ky_ + 3),
                    (kx_ + 14, ky_ + 9), (kx_, ky_ + 5), (kx_ - 14, ky_ + 9),
                ]), uc, 2.2 * s, OUT, n=4)
            else:
                c.blob(HH([(-40, 28), (-18, 20), (0, 24), (18, 20), (40, 28), (20, 36), (0, 30), (-20, 36)]), uc, ow * .8, OUT)
        if p.get("jenggot"):
            if p.get("wajah_chibi_ref"):
                jx_ = fx0 * 0.6
                c.blob(HH([
                    (jx_ - 40, 68), (jx_ - 22, 84), (jx_, 93), (jx_ + 22, 84), (jx_ + 40, 68),
                    (jx_ + 24, 75), (jx_, 79), (jx_ - 24, 75),
                ]), (226, 226, 232), 2.2 * s, OUT, n=4)
            else:
                c.blob(HH([(-60, 52), (-30, 82), (0, 100), (30, 82), (60, 52), (40, 70), (0, 76), (-40, 70)]), (224, 224, 228), ow * .8, OUT)
        # tetes keringat / air mata / urat marah
        if ex.get("sweat"):
            sx, sy = 72, -52
            c.poly(HH([(sx, sy - 24), (sx + 12, sy), (sx + 8, sy + 14), (sx - 8, sy + 14), (sx - 12, sy)]), BIRU_MUDA, ow * .7, OUT)
        if ex.get("tear"):
            for sg in (-1, 1):
                c.poly(HH([(sg * 40, 22), (sg * 40 + 8, 46), (sg * 40, 56), (sg * 40 - 8, 46)]), BIRU_MUDA, ow * .6, OUT)
        if ex.get("vein"):
            vx, vy = 58, -76
            for ang in (0, 90):
                a = math.radians(ang)
                for sg in (-1, 1):
                    pts = [(vx + sg * 4 * math.cos(a), vy + sg * 4 * math.sin(a)), (vx + sg * 13 * math.cos(a), vy + sg * 13 * math.sin(a))]
                c.curve(HH(arc_pts(vx - 7, vy - 7, 9, 9, 90, 0, 6)), MERAH, 4.4 * s)
                c.curve(HH(arc_pts(vx + 7, vy - 7, 9, 9, 180, 90, 6)), MERAH, 4.4 * s)
                c.curve(HH(arc_pts(vx - 7, vy + 7, 9, 9, 0, -90, 6)), MERAH, 4.4 * s)
                c.curve(HH(arc_pts(vx + 7, vy + 7, 9, 9, -90, -180, 6)), MERAH, 4.4 * s)
                break

    @staticmethod
    def _cubic_pts(p0, p1, p2, p3, n=14):
        pts = []
        for k in range(n + 1):
            t = k / n
            u = 1.0 - t
            u2, t2 = u * u, t * t
            x = u2 * u * p0[0] + 3 * u2 * t * p1[0] + 3 * u * t2 * p2[0] + t2 * t * p3[0]
            y = u2 * u * p0[1] + 3 * u2 * t * p1[1] + 3 * u * t2 * p2[1] + t2 * t * p3[1]
            pts.append((x, y))
        return pts

    @staticmethod
    def _spine_norms(pts):
        n = len(pts)
        norms = []
        for k in range(n):
            p_prev = pts[max(0, k - 1)]
            p_next = pts[min(n - 1, k + 1)]
            dx, dy = p_next[0] - p_prev[0], p_next[1] - p_prev[1]
            L = math.hypot(dx, dy) or 1.0
            norms.append((-dy / L, dx / L))
        return norms

    @classmethod
    def _taper_poly(cls, pts, w0, wm, w1, norms=None, round_root=False):
        """Bangun poligon pita helai rambut meruncing mulus di sepanjang kurva pts (tanpa ujung kotak terpotong!)."""
        if norms is None:
            norms = cls._spine_norms(pts)
        n = len(pts) - 1
        left, right = [], []
        for k, (px, py) in enumerate(pts):
            t = k / n if n > 0 else 0.0
            st = math.sin(math.pi * t)
            w = (w0 * (1.0 - t) + w1 * t) * (1.0 - 0.55 * st) + wm * (0.55 * st)
            if round_root and t < 0.22:
                # pangkal melengkung halus masuk ke akar/belahan (NOL potongan kotak lurus!)
                rt = t / 0.22
                w *= (0.14 + 0.86 * math.sqrt(max(0.0, rt)))
            elif t == 0.0:
                w = w0
            elif t == 1.0:
                w = w1
            nx, ny = norms[k]
            left.append((px + nx * w, py + ny * w))
            right.append((px - nx * w, py - ny * w))
        right.reverse()
        return left + right

    @staticmethod
    def _hair_palette(hc, cool=False):
        lum = 0.299 * hc[0] + 0.587 * hc[1] + 0.114 * hc[2]
        if lum > 155:
            # rambut perak / uban sutra
            return (
                gelap(hc, 0.36),                     # c_deep (sela bayangan dalam)
                gelap(hc, 0.18),                     # c_dark
                hc,                                  # c_base
                terang(hc, 0.24),                    # c_mid
                terang(hc, 0.50),                    # c_silk
                (252, 253, 255),                     # c_spec (kilau sutra terang)
            )
        if cool:
            # hitam-biru / slate-blue dingin (Arka, Formal)
            return (
                gelap(hc, 0.52),
                gelap(hc, 0.26),
                hc,
                mix(hc, (108, 124, 164), 0.44),
                mix(hc, (166, 182, 218), 0.54),
                mix(hc, (222, 232, 250), 0.68),
            )
        if lum > 62:
            # cokelat kastanye / madu (Hana, Bimo)
            return (
                gelap(hc, 0.48),
                gelap(hc, 0.22),
                hc,
                mix(hc, (166, 122, 92), 0.46),
                mix(hc, (214, 174, 142), 0.54),
                mix(hc, (246, 224, 204), 0.62),
            )
        # hitam-espresso hangat (persis referensi rambut sutra user!)
        return (
            gelap(hc, 0.54),
            gelap(hc, 0.24),
            hc,
            mix(hc, (118, 82, 64), 0.46),
            mix(hc, (176, 136, 114), 0.52),
            mix(hc, (232, 204, 188), 0.60),
        )

    def _draw_silk_bundle(self, c, HH, p0, p1, p2, p3, w0, wm, w1, hc, n_strands=11, cool=False, seed=0, shine=1.0):
        """Gambar 1 bundel/lock rambut bergelombang sutra dengan puluhan helai paralel meruncing di pangkal & ujung!"""
        c_deep, c_dark, c_base, c_mid, c_silk, c_spec = self._hair_palette(hc, cool=cool)
        spine = self._cubic_pts(p0, p1, p2, p3, 16)
        norms = self._spine_norms(spine)
        n = len(spine) - 1
        # 1) Badan bundel gelap lembut dengan pangkal membulat-meruncing (NOL potongan kotak!)
        c.poly(HH(self._taper_poly(spine, w0 * 1.02, wm * 1.02, max(0.3, w1 * 0.72), norms, round_root=True)), c_deep)

        # 2) Helai-helai paralel rapat menguncup mulus di pangkal akar lalu mekar mengikuti ombak kurva!
        palette_cycle = (c_dark, c_base, c_mid, c_base, c_dark, c_mid, c_silk)
        for i in range(n_strands):
            frac = -1.0 + 2.0 * (i + 0.5) / n_strands  # -0.9..+0.9
            ph = (seed * 1.7 + i * 2.31)
            k_end = n - (1 if (i % 4 == 0 and n > 6) else 0)
            pts_i = []
            for k in range(k_end + 1):
                t = k / n
                st = math.sin(math.pi * t)
                bw = (w0 * (1.0 - t) + w1 * t) * (1.0 - 0.52 * st) + wm * (0.52 * st)
                # pinch lembut di pangkal agar semua helai tumbuh menyatu dari belahan/ubun-ubun!
                if t < 0.22:
                    rt = t / 0.22
                    bw *= (0.18 + 0.82 * math.sqrt(max(0.0, rt)))
                wob = math.sin(t * 5.2 + ph) * (0.09 * bw)
                off = frac * bw * 0.90 + wob
                px, py = spine[k]
                nx, ny = norms[k]
                pts_i.append((px + nx * off, py + ny * off))
            sw = max(1.05, (wm * 2.15 / n_strands) * (0.86 + 0.26 * math.sin(ph)))
            col_i = palette_cycle[(i + seed) % len(palette_cycle)]
            if i == 0 or i == n_strands - 1:
                col_i = c_dark
            c.poly(HH(self._taper_poly(pts_i, 0.18, sw, 0.15)), col_i)

        # 3) Pita helai kilau sutra (specular fibers) di punggung gelombang rambut (t=0.18..0.82)
        if shine > 0.05:
            hl_offsets = (-0.42, -0.18, 0.06, 0.28, 0.48) if shine >= 0.95 else (-0.28, 0.02, 0.30)
            for j, u_hl in enumerate(hl_offsets):
                k0 = max(2, int(n * (0.16 + 0.04 * (j % 2))))
                k1 = min(n - 1, int(n * (0.78 + 0.05 * ((j + 1) % 2))))
                if k1 <= k0 + 2:
                    continue
                pts_h = []
                for k in range(k0, k1 + 1):
                    t = k / n
                    st = math.sin(math.pi * t)
                    bw = (w0 * (1.0 - t) + w1 * t) * (1.0 - 0.52 * st) + wm * (0.52 * st)
                    if t < 0.22:
                        rt = t / 0.22
                        bw *= (0.18 + 0.82 * math.sqrt(max(0.0, rt)))
                    off = u_hl * bw * 0.85
                    px, py = spine[k]
                    nx, ny = norms[k]
                    pts_h.append((px + nx * off, py + ny * off))
                w_hl = (1.55 if j % 2 == 0 else 1.15) * min(1.3, shine)
                c.poly(HH(self._taper_poly(pts_h, 0.12, w_hl, 0.10)), c_silk)
                if j in (1, 2) and shine >= 0.8:
                    sub_h = pts_h[1:-1] if len(pts_h) > 4 else pts_h
                    c.poly(HH(self._taper_poly(sub_h, 0.08, 0.78 * min(1.25, shine), 0.08)), c_spec)

    def _draw_wispy_tips(self, c, HH, hc, wisps, cool=False):
        """Gambar helai-helai ujung tipis melengkung keluar (flyaway wisps & feathered sideburns)."""
        c_deep, c_dark, c_base, c_mid, c_silk, _ = self._hair_palette(hc, cool=cool)
        for idx, (p0, p1, p2, p3, wb) in enumerate(wisps):
            pts = self._cubic_pts(p0, p1, p2, p3, 10)
            norms = self._spine_norms(pts)
            c.poly(HH(self._taper_poly(pts, wb, wb * 0.72, 0.0, norms)), c_deep)
            # helai mid-tone tipis di tengah wisp agar ikut berkilau
            pts_m = [(px + nx * (wb * 0.18), py + ny * (wb * 0.18)) for (px, py), (nx, ny) in zip(pts, norms)]
            c.poly(HH(self._taper_poly(pts_m, wb * 0.42, wb * 0.34, 0.0)), c_mid if idx % 2 == 0 else c_silk)

    def _draw_sideburns(self, c, HH, hc, lx, rx, y_top=-38, y_bot=28, w=9.5, cool=False):
        """Cambang meruncing berhelai lembut di kiri-kanan wajah (persis gambar referensi!)."""
        for sg, sx in ((-1, lx), (1, rx)):
            self._draw_silk_bundle(c, HH,
                (sx + sg * 6, y_top), (sx + sg * 4, (y_top + y_bot) * 0.45),
                (sx + sg * 1.5, y_bot - 14), (sx - sg * 2.0, y_bot),
                w, w * 0.78, 0.4, hc, n_strands=7, cool=cool, seed=90 + sg, shine=0.55)
            self._draw_wispy_tips(c, HH, hc, [
                ((sx + sg * 5, y_bot - 22), (sx + sg * 3, y_bot - 8), (sx, y_bot + 2), (sx - sg * 3, y_bot + 8), 2.0),
            ], cool=cool)

    def _draw_hair_strands(self, c, HH, hc, strands, hl_strands=(), cool=False):
        """Helper cadangan helai crescent 3-tone."""
        _, _, _, c_mid, c_hl, _ = self._hair_palette(hc, cool=cool)
        c_sh = gelap(hc, 0.40)
        for p0, pm, p1, w_ in strands:
            c.poly(HH(_crescent((p0[0] + 1.5, p0[1] + 1.8), (pm[0] + 1.5, pm[1] + 1.8), (p1[0] + 1.2, p1[1] + 1.6), w_ * 0.95)), c_sh)
            c.poly(HH(_crescent(p0, pm, p1, w_)), c_mid)
        for p0, pm, p1, w_ in hl_strands:
            c.poly(HH(_crescent(p0, pm, p1, w_)), c_hl)

    def _hair_front(self, c, H, HH, s, ow, r, hc, p):
        if r in (None, "botak"):
            return
        if r == "kribo_chibi":
            self._hair_front_ref(c, HH, s, hc)
        elif False:
            # PONI IKAL LEBAR MELENGKUNG LEMBUT (BUKAN gigi hiu tajam!) — persis gaya poni ikal referensi
            oc_h = (28, 24, 30)
            ow_h = 2.2 * s
            # tutup penuh dahi atas menyatu mulus ke rambut atas
            cap_top = arc_pts(0, -18, 114, 96, 178, 362, 20)
            c.poly(HH(cap_top + [(108, -18), (64, -44), (0, -52), (-64, -44), (-108, -18)]), hc)
            # 5 helai poni ikal lebar & melengkung lembut (tengah lebih tebal melengkung ke kiri-kanan)
            bang_curls = [
                ((-108, -32), (-112, 0), (-96, 26), (-82, -26)),      # jambang kiri
                ((-84, -48), (-82, -14), (-60, 0), (-42, -44)),       # poni kiri lebar melengkung
                ((-42, -56), (-36, -14), (-6, 4), (10, -48)),         # poni tengah besar melengkung lembut!
                ((8, -56), (26, -16), (48, 2), (56, -46)),            # poni kanan melengkung
                ((58, -46), (82, -14), (96, 26), (94, -24)),          # jambang kanan
            ]
            for p0, pm, tip, p1 in bang_curls:
                e1 = bezier(p0, pm, tip, 6)
                e2 = list(reversed(bezier(p1, ((pm[0] + p1[0]) * 0.52, (pm[1] + tip[1]) * 0.55), tip, 6)))
                c.poly(HH(e1 + e2), hc, ow_h, oc_h)
            # haluskan pangkal poni & tambah 2 goresan ikal halus
            c.poly(HH(cap_top + [(104, -36), (62, -52), (0, -58), (-62, -52), (-104, -36)]), hc)
            sh_c = gelap(hc, 0.34)
            for cx_, cy_ in ((-46, -46), (4, -52), (50, -44)):
                c.curve(HH([(cx_ - 18, cy_ + 4), (cx_, cy_ - 10), (cx_ + 18, cy_ + 3)]), sh_c, 2.2 * s)
        elif r == "afro":
            # poni & jambang keriting menyatu mulus ke massa afro belakang (proporsional untuk HEAD_R=92)
            bangs = [
                (-92, -8, 19), (-82, -34, 21), (-65, -58, 22),
                (-38, -74, 22), (0, -80, 23), (38, -74, 22),
                (65, -58, 22), (82, -34, 21), (92, -8, 19),
            ]
            for bx, by, br in bangs:
                c.ell(*H(bx, by), br * s + ow * .72, br * s + ow * .72, OUT)
            cap_top = arc_pts(0, -16, 98, 98, 174, 366, 18)
            cap_bot = [(bx, by) for bx, by, _ in reversed(bangs)]
            c.poly(HH(cap_top + cap_bot), hc)
            for bx, by, br in bangs:
                c.ell(*H(bx, by), br * s, br * s, hc)
        elif r == "jambul":
            if p.get("wajah_chibi_ref"):
                # TOUSLED WAVY SPIKY BERHELAI SUTRA (Raka) — dinamis mengembang ke atas & poni runcing berhelai!
                c.blob(HH([(-66, -18), (-32, -34), (0, -28), (32, -34), (66, -18), (52, -10), (20, -14), (-14, -12), (-48, -12)]),
                       (220, 174, 152, 76), 0, n=4)
                c.blob(HH([(-78, -2), (-82, -46), (-64, -90), (0, -110), (64, -90), (82, -46), (78, -2),
                           (54, -40), (0, -48), (-54, -40)]), gelap(hc, 0.44), 0, n=5)
                self._draw_sideburns(c, HH, hc, -78, 78, y_top=-38, y_bot=24, w=9.5)
                # bundel samping kiri-kanan mengembang keluar & jambul puncak dinamis
                self._draw_silk_bundle(c, HH, (-10, -102), (-54, -104), (-86, -76), (-96, -32), 15, 19, 2.0, hc, n_strands=12, seed=101, shine=1.0)
                self._draw_silk_bundle(c, HH, (10, -102), (56, -104), (88, -74), (96, -30), 15, 19, 2.0, hc, n_strands=12, seed=102, shine=1.0)
                self._draw_silk_bundle(c, HH, (-6, -104), (-36, -120), (-64, -106), (-82, -72), 14, 17, 1.6, hc, n_strands=11, seed=103, shine=1.1)
                self._draw_silk_bundle(c, HH, (4, -104), (36, -120), (66, -106), (84, -72), 14, 17, 1.6, hc, n_strands=11, seed=104, shine=1.1)
                # jambul tengah melengkung ke atas
                self._draw_silk_bundle(c, HH, (-22, -98), (-6, -124), (16, -130), (38, -114), 14, 16, 1.2, hc, n_strands=10, seed=105, shine=1.2)
                # 5 rumpun poni berhelai meruncing di dahi (pangkal rapat di ubun-ubun!)
                self._draw_silk_bundle(c, HH, (-14, -98), (-46, -78), (-62, -52), (-58, -16), 14, 14.5, 1.2, hc, n_strands=9, seed=106, shine=0.9)
                self._draw_silk_bundle(c, HH, (-4, -100), (-22, -76), (-28, -48), (-22, -12), 14, 14.5, 1.0, hc, n_strands=9, seed=107, shine=1.1)
                self._draw_silk_bundle(c, HH, (4, -100), (12, -74), (16, -46), (12, -10), 14, 14.5, 1.0, hc, n_strands=9, seed=108, shine=1.15)
                self._draw_silk_bundle(c, HH, (14, -98), (42, -76), (56, -48), (52, -16), 14, 14.5, 1.2, hc, n_strands=9, seed=109, shine=0.95)
                self._draw_wispy_tips(c, HH, hc, [
                    ((-44, -98), (-70, -110), (-88, -104), (-98, -90), 3.2),
                    ((-68, -68), (-90, -68), (-102, -52), (-104, -36), 3.0),
                    ((44, -98), (70, -110), (88, -104), (98, -90), 3.2),
                    ((68, -66), (90, -64), (102, -48), (104, -32), 3.0),
                    ((-4, -112), (10, -130), (26, -134), (42, -124), 2.8),
                ])
            else:
                outer, inner = [], []
                n = 8
                for i in range(n * 2 + 1):
                    a = 196 + (344 - 196) * i / (n * 2)
                    rr = HEAD_R + (36 if i % 2 else 6) + (10 if 5 <= i <= 11 and i % 2 else 0)
                    outer.append((math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr))
                for i in range(14, -1, -1):
                    a = 196 + (344 - 196) * i / 14
                    rr = HEAD_R * (0.74 + 0.08 * math.sin(i * 1.7))
                    inner.append((math.cos(math.radians(a)) * rr * 1.0, math.sin(math.radians(a)) * rr * 1.0 + 6))
                c.poly(HH(outer + inner), hc, ow * .9, OUT)
        elif r == "keriting":
            if p.get("wajah_chibi_ref"):
                oc_h = (42, 26, 22)
                ow_h = 2.0 * s
                c_mid = mix(hc, (132, 92, 68), 0.50)
                c_br = mix(hc, (182, 136, 104), 0.56)
                c_sh = gelap(hc, 0.34)
                cap = arc_pts(0, -26, 88, 76, 178, 362, 20)
                arch = list(reversed(arc_pts(0, -10, 78, 36, 188, 352, 12)))
                curls = [(-76, -20, 16), (-56, -40, 17), (-30, -50, 18), (-2, -48, 18), (26, -50, 18), (54, -40, 17), (74, -20, 16)]
                for bx, by, br in curls:
                    c.ell(*H(bx, by + 5), br * 0.86 * s, br * 0.68 * s, (220, 174, 152, 95))
                c.poly(HH(cap + arch), hc)
                for bx, by, br in curls:
                    c.ell(*H(bx, by), br * s + ow_h, br * 0.88 * s + ow_h, oc_h)
                c.poly(HH(cap + arch), hc)
                for bx, by, br in curls:
                    c.ell(*H(bx, by), br * s, br * 0.88 * s, hc)
                for idx_k, (bx, by, br) in enumerate(curls):
                    sa = 15 + (idx_k * 47) % 150
                    a1 = arc_pts(bx, by, br * 0.72, br * 0.66, sa, sa + 205, 10)
                    c.line(HH(a1), c_mid, 2.0 * s)
                    c.line(HH(a1[2:-2]), c_br, 1.2 * s)
                for cx_, cy_, cr_ in ((-48, -68, 15), (-14, -78, 17), (22, -76, 16), (54, -64, 14), (-28, -56, 13), (24, -56, 13)):
                    a2 = arc_pts(cx_, cy_, cr_, cr_ * 0.82, 190, 380, 10)
                    c.line(HH(a2), c_sh, 2.0 * s)
                    c.line(HH(a2[2:-3]), c_br, 1.2 * s)
            else:
                for i, a in enumerate(range(200, 345, 18)):
                    rr = HEAD_R * 0.8
                    c.ell(*H(math.cos(math.radians(a)) * rr, math.sin(math.radians(a)) * rr + 4), 26 * s, 26 * s, hc, ow * .9, OUT)
        elif r == "belah_samping":
            # RAMBUT BEROMBAK SUTRA RAPI MENYAPU SAMPING (Dimas — bervolume elegan, kontur terkontrol rapi!)
            c.blob(HH([(-58, -28), (-20, -26), (18, -34), (54, -44), (36, -54), (-26, -44)]), (220, 174, 152, 72), 0, n=4)
            c.blob(HH([(-74, -4), (-78, -44), (-64, -88), (0, -110), (62, -90), (78, -42), (74, -4),
                       (50, -44), (0, -44), (-52, -40)]), gelap(hc, 0.44), 0, n=5)
            self._draw_sideburns(c, HH, hc, -74, 74, y_top=-38, y_bot=24, w=9.5)
            # bundel sisi kanan rapi memeluk lekuk kepala
            self._draw_silk_bundle(c, HH, (36, -98), (74, -86), (92, -52), (78, -8), 14, 18, 2.6, hc, n_strands=12, seed=201, shine=1.0)
            self._draw_silk_bundle(c, HH, (32, -76), (66, -66), (84, -38), (74, 2), 12, 15, 2.2, hc, n_strands=10, seed=202, shine=0.9)
            # bundel puncak & ombak utama menyapu S-wave rapi dari belahan kanan ke kiri (tanpa mencuat terlalu jauh!)
            self._draw_silk_bundle(c, HH, (48, -94), (6, -124), (-44, -118), (-82, -80), 15, 21, 3.0, hc, n_strands=14, seed=203, shine=1.2)
            self._draw_silk_bundle(c, HH, (40, -76), (0, -104), (-48, -94), (-90, -50), 15, 22, 2.6, hc, n_strands=14, seed=204, shine=1.25)
            self._draw_silk_bundle(c, HH, (30, -58), (-6, -80), (-50, -68), (-88, -28), 14, 20, 2.2, hc, n_strands=13, seed=205, shine=1.15)
            # ombak poni depan lembut membingkai dahi di atas kacamata
            self._draw_silk_bundle(c, HH, (26, -50), (-10, -54), (-44, -38), (-76, -22), 12, 16, 2.0, hc, n_strands=11, seed=206, shine=1.05)
            self._draw_silk_bundle(c, HH, (8, -48), (-20, -42), (-46, -30), (-64, -18), 8.5, 10.5, 1.0, hc, n_strands=8, seed=207, shine=0.85)
            # sedikit wisp halus terkontrol di tepi ombak (rapi & natural!)
            self._draw_wispy_tips(c, HH, hc, [
                ((-56, -86), (-80, -86), (-94, -74), (-98, -60), 2.8),
                ((-68, -56), (-90, -52), (-98, -36), (-96, -20), 2.6),
                ((64, -78), (84, -74), (96, -58), (96, -40), 2.6),
                ((68, -48), (86, -40), (92, -24), (88, -10), 2.4),
            ])
        elif r == "sisir_belakang":
            # RAMBUT POMPADOUR / SISIR BELAKANG BEROMBAK SUTRA + HELAI UBAN PELIPIS MENYATU (Ayah)
            c.blob(HH([(-54, -52), (0, -56), (54, -52), (44, -64), (-44, -64)]), (220, 174, 152, 74), 0, n=4)
            c.blob(HH([(-68, -4), (-74, -46), (-64, -92), (0, -122), (64, -92), (74, -46), (68, -4),
                       (50, -56), (0, -64), (-50, -56)]), gelap(hc, 0.44), 0, n=5)
            self._draw_sideburns(c, HH, hc, -68, 68, y_top=-38, y_bot=22, w=9.0)
            # bundel disisir gagah melengkung ke atas-belakang dengan puncak kubah penuh tanpa cekungan!
            self._draw_silk_bundle(c, HH, (-56, -56), (-74, -84), (-58, -112), (-14, -124), 15, 19, 3.2, hc, n_strands=12, seed=301, shine=1.0)
            self._draw_silk_bundle(c, HH, (56, -56), (74, -84), (58, -112), (14, -124), 15, 19, 3.2, hc, n_strands=12, seed=302, shine=1.0)
            self._draw_silk_bundle(c, HH, (-36, -64), (-44, -98), (-20, -124), (20, -124), 16, 21, 3.8, hc, n_strands=13, seed=303, shine=1.15)
            self._draw_silk_bundle(c, HH, (36, -64), (44, -98), (20, -124), (-20, -124), 16, 21, 3.8, hc, n_strands=13, seed=304, shine=1.15)
            self._draw_silk_bundle(c, HH, (-14, -64), (-6, -98), (12, -122), (42, -112), 16, 21, 3.0, hc, n_strands=13, seed=305, shine=1.25)
            # bundel pelipis menyapu rapi ke belakang + helai uban garam-lada menyatu natural (BUKAN blok putih keras!)
            uban_soft = mix(hc, (216, 220, 230), 0.62)
            for sg_u in (-1, 1):
                self._draw_silk_bundle(c, HH, (sg_u * 66, -12), (sg_u * 78, -36), (sg_u * 78, -66), (sg_u * 62, -94),
                                       11, 14, 2.5, hc, n_strands=9, seed=310 + sg_u, shine=0.8)
                self._draw_silk_bundle(c, HH, (sg_u * 64, 4), (sg_u * 71, -14), (sg_u * 72, -34), (sg_u * 65, -52),
                                       4.4, 5.4, 1.0, uban_soft, n_strands=7, seed=320 + sg_u, shine=0.95)
            self._draw_wispy_tips(c, HH, hc, [
                ((-50, -96), (-68, -112), (-62, -124), (-44, -128), 2.6),
                ((50, -96), (68, -112), (62, -124), (44, -128), 2.6),
                ((-12, -118), (12, -132), (34, -130), (48, -118), 2.6),
            ])
        elif r == "klimis":
            # RAMBUT EXECUTIVE SIDE-WAVE KLIMIS SUPER RAPI (Formal / Bos — 1 kurva eksekutif bersih tanpa rambut liar!)
            c.blob(HH([(-50, -42), (-10, -38), (42, -46), (32, -56), (-36, -54)]), (220, 174, 152, 70), 0, n=4)
            c.blob(HH([(-68, -6), (-72, -44), (-62, -84), (-22, -106), (12, -112), (56, -94), (72, -44), (68, -6),
                       (48, -48), (0, -46), (-48, -50)]), gelap(hc, 0.44), 0, n=6)
            self._draw_sideburns(c, HH, hc, -68, 68, y_top=-38, y_bot=16, w=8.0, cool=True)
            # sisi kiri pendek rapi memeluk kepala
            self._draw_silk_bundle(c, HH, (-28, -98), (-60, -82), (-74, -46), (-70, -6), 12, 14.5, 2.0, hc, n_strands=10, cool=True, seed=401, shine=0.9)
            self._draw_silk_bundle(c, HH, (-36, -88), (-60, -68), (-70, -38), (-66, -4), 10, 13, 1.8, hc, n_strands=9, cool=True, seed=406, shine=0.85)
            # mahkota transisi kiri->atas->kanan mulus (menghilangkan tangga di belahan kiri!)
            self._draw_silk_bundle(c, HH, (-54, -76), (-18, -114), (32, -116), (72, -78), 12, 18, 4.0, hc, n_strands=12, cool=True, seed=407, shine=1.15)
            # bundel eksekutif klimis melengkung rapi mengikuti kontur kepala kanan (nol ujung mencuat liar!)
            self._draw_silk_bundle(c, HH, (-44, -84), (2, -116), (50, -106), (76, -64), 13, 19, 3.2, hc, n_strands=13, cool=True, seed=402, shine=1.2)
            self._draw_silk_bundle(c, HH, (-40, -72), (6, -98), (54, -84), (78, -36), 14, 19, 2.8, hc, n_strands=13, cool=True, seed=403, shine=1.25)
            self._draw_silk_bundle(c, HH, (-36, -58), (8, -74), (50, -62), (74, -18), 12, 16, 2.4, hc, n_strands=11, cool=True, seed=404, shine=1.1)
            self._draw_silk_bundle(c, HH, (-34, -52), (0, -52), (34, -46), (62, -38), 8.5, 11, 1.6, hc, n_strands=8, cool=True, seed=405, shine=0.9)
        elif r in ("rapi", "uban"):
            if p.get("wajah_chibi_ref"):
                # RAMBUT KLASIK / UBAN PERAK BERHELAI SUTRA (Pak Guru)
                c.blob(HH([(-62, -34), (-14, -30), (46, -42), (34, -54), (-36, -48)]), (220, 174, 152, 74), 0, n=4)
                c.blob(HH([(-80, -4), (-84, -44), (-70, -88), (0, -114), (70, -88), (84, -44), (80, -4),
                           (56, -44), (0, -46), (-56, -42)]), gelap(hc, 0.28), 0, n=5)
                self._draw_sideburns(c, HH, hc, -80, 80, y_top=-38, y_bot=22, w=9.5)
                self._draw_silk_bundle(c, HH, (24, -100), (-26, -118), (-76, -94), (-92, -44), 15, 20, 2.8, hc, n_strands=13, seed=501, shine=1.1)
                self._draw_silk_bundle(c, HH, (22, -84), (-26, -94), (-74, -68), (-88, -20), 15, 20, 2.5, hc, n_strands=13, seed=502, shine=1.2)
                self._draw_silk_bundle(c, HH, (18, -66), (-20, -68), (-58, -48), (-76, -16), 13, 17, 2.0, hc, n_strands=11, seed=503, shine=1.0)
                self._draw_silk_bundle(c, HH, (26, -96), (64, -92), (88, -62), (90, -16), 14, 19, 2.6, hc, n_strands=12, seed=504, shine=1.1)
                self._draw_silk_bundle(c, HH, (24, -74), (58, -68), (82, -42), (82, -6), 12, 16, 2.2, hc, n_strands=10, seed=505, shine=0.95)
                self._draw_wispy_tips(c, HH, hc, [
                    ((-62, -86), (-86, -82), (-96, -66), (-98, -48), 2.8),
                    ((60, -86), (84, -82), (94, -66), (96, -48), 2.8),
                    ((-24, -108), (-2, -120), (24, -118), (42, -108), 2.5),
                ])
            else:
                top = arc_pts(0, 0, HEAD_R + 5, HEAD_R + 5, 188, 352, 20)
                fringe = [(70, -50), (40, -62), (10, -48), (-18, -60), (-48, -46), (-72, -52)]
                c.poly(HH(top + fringe), hc, ow * .9, OUT)
        elif r == "ghibli_kuncir":
            # RAMBUT DEPAN STUDIO GHIBLI RAPI BERHELAI SUTRA + JUMBAI KANAN MANIS (Adik)
            c.blob(HH([(-68, -16), (-26, -14), (24, -14), (66, -16), (56, -30), (-56, -30)]), (220, 174, 152, 64), 0, n=4)
            c.blob(HH([(-88, 6), (-94, -44), (-76, -96), (0, -118), (76, -96), (92, -40), (86, 4),
                       (68, -42), (0, -48), (-68, -42)]), gelap(hc, 0.44), 0, n=6)
            self._draw_sideburns(c, HH, hc, -86, 86, y_top=-38, y_bot=26, w=10.0)
            # 2 jumbai kanan pendek-manis menyatu erat dengan kubah kepala (bukan tanduk panjang terpisah!)
            self._draw_silk_bundle(c, HH, (14, -108), (56, -114), (84, -106), (104, -88), 13, 14, 1.2, hc, n_strands=10, seed=601, shine=1.05)
            self._draw_silk_bundle(c, HH, (32, -92), (72, -88), (96, -72), (108, -48), 13, 14, 1.2, hc, n_strands=10, seed=602, shine=1.0)
            # kubah utama membulat penuh lembut & poni berhelai rapat menyatu
            self._draw_silk_bundle(c, HH, (-58, -98), (-16, -122), (24, -122), (66, -96), 13, 17, 11, hc, n_strands=11, seed=611, shine=1.15)
            self._draw_silk_bundle(c, HH, (14, -116), (-50, -112), (-90, -72), (-94, -14), 17, 22, 3.0, hc, n_strands=13, seed=604, shine=1.15)
            self._draw_silk_bundle(c, HH, (-14, -116), (52, -110), (88, -68), (92, -12), 17, 22, 3.0, hc, n_strands=13, seed=605, shine=1.15)
            # 5 rumpun poni rapat & lembut jatuh manis di dahi (sedikit melebar di tengah agar tidak pecah-pecah)
            self._draw_silk_bundle(c, HH, (-4, -110), (-44, -84), (-64, -50), (-62, -14), 16, 17.5, 1.6, hc, n_strands=10, seed=606, shine=1.0)
            self._draw_silk_bundle(c, HH, (0, -110), (-24, -78), (-34, -46), (-30, -12), 16, 17.5, 1.4, hc, n_strands=10, seed=607, shine=1.15)
            self._draw_silk_bundle(c, HH, (2, -110), (4, -78), (6, -46), (4, -12), 16, 17.5, 1.4, hc, n_strands=10, seed=608, shine=1.2)
            self._draw_silk_bundle(c, HH, (6, -108), (34, -78), (44, -46), (40, -12), 16, 17.5, 1.4, hc, n_strands=10, seed=609, shine=1.1)
            self._draw_silk_bundle(c, HH, (14, -106), (58, -78), (74, -46), (70, -14), 15, 16.5, 1.6, hc, n_strands=9, seed=610, shine=0.95)
            self._draw_wispy_tips(c, HH, hc, [
                ((76, -102), (96, -98), (108, -88), (114, -76), 2.2),
                ((82, -74), (100, -68), (110, -54), (114, -40), 2.2),
            ])
        elif r == "bob":
            if p.get("wajah_chibi_ref"):
                c.blob(HH([(-84, 24), (-88, -32), (-72, -80), (0, -108), (72, -80), (88, -32), (84, 24),
                           (64, -30), (0, -40), (-64, -30)]), gelap(hc, 0.40), 0, n=6)
                for sg_b in (-1, 1):
                    self._draw_silk_bundle(c, HH, (-sg_b * 4, -106), (sg_b * 52, -98), (sg_b * 90, -52), (sg_b * 82, 42),
                                           17, 21, 3.0, hc, n_strands=13, seed=701 + sg_b, shine=1.15)
                    self._draw_silk_bundle(c, HH, (0, -100), (sg_b * 28, -76), (sg_b * 46, -48), (sg_b * 42, -18),
                                           13, 15, 1.2, hc, n_strands=9, seed=705 + sg_b, shine=1.0)
                self._draw_silk_bundle(c, HH, (0, -100), (-2, -72), (2, -46), (0, -18), 12, 14, 1.0, hc, n_strands=9, seed=709, shine=1.1)
            else:
                top = arc_pts(0, 0, HEAD_R + 6, HEAD_R + 6, 176, 364, 22)
                fr = [(88, 4), (80, -48), (40, -58), (0, -48), (-40, -58), (-80, -48), (-88, 4)]
                c.poly(HH(top + fr), hc, ow * .9, OUT)
        elif r == "panjang_naa":
            # RAMBUT PANJANG BERGELOMBANG SUTRA COKELAT MADU (Hana — puncak ubun-ubun 1 lengkungan mulus tanpa potongan!)
            c.blob(HH([(-64, -20), (-26, -14), (18, -14), (60, -20), (50, -34), (-50, -34)]), (220, 174, 152, 68), 0, n=4)
            c.blob(HH([(-82, 24), (-86, -34), (-74, -84), (0, -114), (74, -84), (86, -34), (82, 24),
                       (68, -36), (0, -52), (-68, -36)]), gelap(hc, 0.36), 0, n=6)
            # mahkota lembut menyambungkan puncak kiri & kanan dengan mulus
            self._draw_silk_bundle(c, HH, (-50, -96), (-12, -118), (12, -118), (50, -96), 11, 15, 11, hc, n_strands=10, seed=820, shine=1.1)
            # bundel panjang S-wave kiri & kanan overlap penuh di ubun-ubun (pangkal melengkung halus!)
            for sg_h in (-1, 1):
                self._draw_silk_bundle(c, HH, (-sg_h * 14, -110), (sg_h * 52, -108), (sg_h * 94, -52), (sg_h * 84, 58),
                                       16, 22, 2.8, hc, n_strands=14, seed=801 + sg_h, shine=1.2)
                self._draw_silk_bundle(c, HH, (-sg_h * 10, -104), (sg_h * 44, -86), (sg_h * 80, -30), (sg_h * 74, 52),
                                       14, 17, 2.0, hc, n_strands=11, seed=805 + sg_h, shine=1.05)
                self._draw_wispy_tips(c, HH, hc, [
                    ((sg_h * 80, -2), (sg_h * 94, 28), (sg_h * 90, 54), (sg_h * 78, 70), 3.0),
                    ((sg_h * 74, 16), (sg_h * 82, 42), (sg_h * 74, 60), (sg_h * 64, 68), 2.4),
                ])
            # poni tipis berhelai sutra membingkai dahi lembut (pangkal menyatu penuh di puncak!)
            self._draw_silk_bundle(c, HH, (0, -108), (-36, -82), (-54, -52), (-58, -16), 14, 14.5, 1.2, hc, n_strands=9, seed=811, shine=1.1)
            self._draw_silk_bundle(c, HH, (2, -108), (-16, -78), (-24, -48), (-28, -12), 13, 13.5, 1.0, hc, n_strands=9, seed=812, shine=1.15)
            self._draw_silk_bundle(c, HH, (-2, -108), (16, -78), (22, -48), (18, -12), 13, 13.5, 1.0, hc, n_strands=9, seed=813, shine=1.15)
            self._draw_silk_bundle(c, HH, (0, -108), (38, -80), (54, -50), (56, -16), 14, 14.5, 1.2, hc, n_strands=9, seed=814, shine=1.1)
        elif r == "comma":
            # KOREAN WAVY COMMA HAIR BERHELAI SUTRA DINGIN (Arka) — ombak bervolume belah tengah-comma!
            c.blob(HH([(-54, -28), (-26, -14), (0, -34), (26, -14), (54, -28), (40, -48), (-40, -48)]), (220, 174, 152, 74), 0, n=4)
            c.blob(HH([(-78, -2), (-84, -44), (-72, -88), (-34, -112), (0, -104), (34, -112), (72, -88), (84, -44), (78, -2),
                       (56, -46), (0, -64), (-56, -46)]), gelap(hc, 0.44), 0, n=6)
            self._draw_sideburns(c, HH, hc, -74, 74, y_top=-38, y_bot=26, w=9.5, cool=True)
            for sg_c in (-1, 1):
                self._draw_silk_bundle(c, HH, (-sg_c * 4, -102), (sg_c * 46, -126), (sg_c * 94, -92), (sg_c * 88, -24),
                                       16, 22, 3.0, hc, n_strands=14, cool=True, seed=901 + sg_c, shine=1.2)
                self._draw_silk_bundle(c, HH, (-sg_c * 2, -92), (sg_c * 44, -106), (sg_c * 80, -66), (sg_c * 72, -12),
                                       14, 19, 2.4, hc, n_strands=12, cool=True, seed=905 + sg_c, shine=1.15)
                self._draw_silk_bundle(c, HH, (sg_c * 2, -84), (sg_c * 38, -82), (sg_c * 52, -46), (sg_c * 22, -12),
                                       13, 16, 1.2, hc, n_strands=11, cool=True, seed=909 + sg_c, shine=1.25)
                self._draw_wispy_tips(c, HH, hc, [
                    ((sg_c * 58, -94), (sg_c * 86, -96), (sg_c * 100, -78), (sg_c * 102, -56), 3.0),
                    ((sg_c * 72, -58), (sg_c * 94, -50), (sg_c * 102, -30), (sg_c * 96, -12), 2.8),
                    ((sg_c * 42, -40), (sg_c * 36, -22), (sg_c * 24, -10), (sg_c * 10, -6), 2.4),
                ], cool=True)
        elif r == "panjang":
            top = arc_pts(0, -4, HEAD_R + 6, HEAD_R + 4, 184, 356, 22)
            fringe = [
                (86, 12), (76, -34), (56, -18), (44, -48),
                (18, -22), (8, -56), (-18, -24), (-36, -54),
                (-60, -24), (-78, -42), (-88, 12),
            ]
            c.poly(HH(top + fringe), hc, ow * .85, OUT)
            hl_h = terang(hc, 0.24)
            for hx_, hy_, rx_, ry_ in ((-46, -68, 11, 6), (-14, -76, 14, 6), (26, -74, 12, 6), (56, -64, 9, 5)):
                c.ell(*H(hx_, hy_), rx_ * s, ry_ * s, hl_h)
        elif r == "kuncir":
            if p.get("wajah_chibi_ref"):
                # TWIN-BUNS BERHELAI SUTRA + PONI MANIS BERHELAI (Tika)
                c.blob(HH([(-62, -18), (-22, -20), (22, -20), (62, -18), (48, -38), (-48, -38)]), (220, 174, 152, 74), 0, n=4)
                c.blob(HH([(-82, -2), (-86, -40), (-72, -82), (0, -108), (72, -82), (86, -40), (82, -2),
                           (64, -30), (0, -42), (-64, -30)]), gelap(hc, 0.42), 0, n=6)
                self._draw_sideburns(c, HH, hc, -82, 82, y_top=-36, y_bot=20, w=8.8)
                for sg_t in (-1, 1):
                    self._draw_silk_bundle(c, HH, (-sg_t * 4, -108), (sg_t * 48, -102), (sg_t * 86, -64), (sg_t * 86, -6),
                                           16, 20, 2.5, hc, n_strands=13, seed=951 + sg_t, shine=1.15)
                    self._draw_silk_bundle(c, HH, (0, -102), (sg_t * 34, -82), (sg_t * 58, -50), (sg_t * 56, -18),
                                           14, 15, 1.2, hc, n_strands=10, seed=955 + sg_t, shine=1.05)
                    self._draw_silk_bundle(c, HH, (0, -102), (sg_t * 16, -76), (sg_t * 24, -48), (sg_t * 20, -16),
                                           13, 13.5, 1.0, hc, n_strands=9, seed=959 + sg_t, shine=1.15)
                self._draw_silk_bundle(c, HH, (0, -102), (-2, -74), (2, -46), (-2, -14), 12, 12.5, 1.0, hc, n_strands=8, seed=963, shine=1.1)
                self._draw_wispy_tips(c, HH, hc, [
                    ((-70, -56), (-90, -44), (-96, -26), (-90, -10), 2.4),
                    ((70, -56), (90, -44), (96, -26), (90, -10), 2.4),
                ])
            else:
                top = arc_pts(0, 0, HEAD_R + 4, HEAD_R + 4, 190, 350, 18)
                fr = [(74, -46), (44, -64), (14, -50), (-14, -66), (-48, -50), (-76, -50)]
                c.poly(HH(top + fr), hc, ow * .9, OUT)
                c.ell(*H(0, -HEAD_R - 22), 24 * s, 24 * s, hc, ow * .9, OUT)

    def _mouth(self, c, st, ex, HH, s, ow, fs, fx0, fy0):
        kind = ex.get("mouth", "open")
        talk = st.get("talk")
        op = ex.get("open", 0.6)
        if talk is not None:
            if kind in ("o", "yawn"):
                op = 0.5 + 0.5 * talk
            else:
                kind = "open"
                op = 0.12 + 0.88 * talk
        mx, my = fx0 * .6, (49 if self.p.get("wajah_chibi_ref") else (50 if self.p.get("mata_chibi") else 44)) * fs + fy0 * .4
        k = ex.get("small", 1.0) * (0.76 if self.p.get("mata_chibi") and talk is None and kind == "open" else 1.0)

        def D(w, d):
            m_col = (206, 126, 102) if self.p.get("outline_hangat") else MERAH_TUA
            t_col = (232, 160, 134) if self.p.get("outline_hangat") else LIDAH
            oc_m = (64, 52, 46) if self.p.get("outline_hangat") else OUT
            top = [(mx - w, my - 1), (mx - w * .5, my - 4), (mx + w * .5, my - 4), (mx + w, my - 1)]
            bot = arc_pts(mx, my - 1, w, d, 0, 180, 14)
            c.poly(HH(top + bot), m_col, ow * .82, oc_m)
            if d > 14:
                c.poly(HH(_ellpts(mx, my + d * .62, w * .5, d * .32, 14)), t_col)
            return
        if kind == "open":
            # Saat tidak bicara (diam/pose), pakai `gaya_mulut` khas tiap karakter agar ekspresi dasar TIDAK seragam copy-paste!
            gm_m = self.p.get("gaya_mulut") if (talk is None and ex.get("mouth") == "open" and op <= 0.75) else None
            oc_m = (64, 52, 46) if self.p.get("outline_hangat") else OUT
            if gm_m == "senyum_kecil":
                c.curve(HH([(mx - 12, my + 2.5), (mx, my + 8.5), (mx + 12, my + 2.0)]), oc_m, 2.8 * s)
            elif gm_m == "senyum_kucing":
                c.curve(HH([(mx - 14, my + 2.0), (mx - 7, my + 8.0), (mx, my + 2.0)]), oc_m, 2.6 * s)
                c.curve(HH([(mx, my + 2.0), (mx + 7, my + 8.0), (mx + 14, my + 2.0)]), oc_m, 2.6 * s)
            elif gm_m == "mungil_o":
                # mulut kecil lembut khas anak Studio Ghibli (persis gambar referensi user!)
                c.poly(HH(_ellpts(mx, my + 5.5, 6.2, 4.4, 14)), (214, 126, 108), 2.0 * s, oc_m)
            elif gm_m == "smirk":
                c.curve(HH([(mx - 13, my + 5.0), (mx + 2, my + 6.5), (mx + 16, my - 2.0)]), oc_m, 2.9 * s)
            elif gm_m == "dewasa_ramah":
                c.curve(HH([(mx - 16, my + 3.0), (mx, my + 9.5), (mx + 16, my + 2.5)]), oc_m, 3.0 * s)
            elif gm_m == "senyum_hangat":
                D(15.5 * k, lerp(5, 19, op))
            else:
                D(22 * k, lerp(5, 28, op))
        elif kind == "grin":
            D(31, lerp(14, 38, op))
        elif kind == "smile":
            if self.p.get("wajah_arka") or self.p.get("wajah_chibi_ref"):
                # mulut senyum halus melengkung lembut persis gambar referensi (bukan V lancip!)
                c.line(HH([(mx - 13, my + 2.0), (mx + 2, my + 2.5), (mx + 15, my - 1.2)]), (86, 54, 48), 2.7 * s)
            else:
                c.curve(HH(arc_pts(mx, my - 14, 25, 22, 28, 152, 10)), (64, 52, 46) if self.p.get("outline_hangat") else OUT, 4.4 * s)
        elif kind == "o":
            c.poly(HH(_ellpts(mx, my + 6, 12 + 4 * (op - 0.6), 15 + 6 * (op - 0.6), 16)), MERAH_TUA, ow * .85, OUT)
        elif kind == "yawn":
            c.poly(HH(_ellpts(mx, my + 8, 21, 28 * (0.7 + 0.3 * op), 18)), MERAH_TUA, ow * .85, OUT)
            c.poly(HH(_ellpts(mx, my + 20, 12, 8, 12)), LIDAH)
        elif kind == "frown":
            c.curve(HH(arc_pts(mx, my + 22, 22, 15, 205, 335, 10)), OUT, 4.8 * s)
        elif kind == "flat":
            c.line(HH([(mx - 15, my + 4), (mx + 15, my + 4)]), OUT, 4.8 * s)
        elif kind == "flat_miring":
            c.line(HH([(mx - 14, my + 8), (mx + 16, my)]), OUT, 4.8 * s)
        elif kind == "gigit":     # marah menggeram
            c.poly(HH([(mx - 26, my + 2), (mx + 26, my + 2), (mx + 22, my + 20), (mx - 22, my + 20)]), PUTIH, ow * .8, OUT)
            for xx in (-12, 0, 12):
                c.line(HH([(mx + xx, my + 2), (mx + xx, my + 20)]), OUT, 2.8 * s)
        elif kind == "wave":
            pts = [(mx - 22 + i * 4.4, my + 6 + 4.2 * math.sin(i * 1.6)) for i in range(11)]
            c.line(HH(pts), OUT, 4.4 * s)
        elif kind == "wave_o":
            c.poly(HH(_ellpts(mx, my + 8, 14, 12, 14)), MERAH_TUA, ow * .85, OUT)
        elif kind == "smirk":
            c.curve(HH([(mx - 20, my + 2), (mx + 4, my + 10), (mx + 24, my - 8)]), OUT, 4.8 * s)
        elif kind == "pout":
            c.curve(HH(arc_pts(mx, my + 14, 13, 8, 205, 335, 8)), OUT, 4.8 * s)

    # =========================================================================
    # MASKOT NON-MANUSIA (RETRO RUBBER-HOSE OBJECT-BODY MASCOT)
    # Bentuk tubuh = langsung wujud asli karakternya (otak, virus, sel_imun, dsb.)
    # TANPA baju/celana manusia; tangan & kaki rubber-hose + sarung tangan kartun + sepatu chunky!
    # =========================================================================
    def _draw_mascot(self, c, st):
        p = self.p
        s = st["s"] * p["skala"]
        fl = st["flip"]
        sx, sy = st.get("squash", (1.0, 1.0))
        lean = math.radians(st.get("lean", 0))
        sit = st.get("sit", 0.0)
        dy = SIT_DROP * sit
        X0, Y0 = st["x"], st["y"] + st.get("hop", 0)
        cl, sl = math.cos(lean), math.sin(lean)

        def T(lx, ly, nodrop=False):
            if not nodrop:
                ly = ly + dy
            lx = lx * fl
            rx, ry = lx * cl - ly * sl, lx * sl + ly * cl
            return (X0 + rx * s * sx, Y0 + ry * s * sy)

        def TT(pts):
            return [T(*q) for q in pts]

        oc_m = (52, 24, 22) if p.get("bentuk_maskot") == "otak" else (42, 34, 34)
        ow = 3.4 * s
        limb_c = warna(p.get("lengan_warna"), (240, 152, 158))
        shoe_c = warna(p.get("sepatu"), (232, 132, 138))
        sol_c = warna(p.get("sol_warna"), (248, 248, 250))
        acc_c = warna(p.get("aksen"), (248, 248, 250))
        bentuk = p.get("bentuk_maskot", p.get("kepala", "otak"))

        stance_cur = st.get("legs", "stand")
        walking = stance_cur == "walk" and st.get("amp", 0.0) > 0.01
        hadap_raw = st.get("hadap", st.get("miring", None))
        if hadap_raw is None:
            turn = 0.50 if stance_cur == "walk" else 0.0
        elif isinstance(hadap_raw, str):
            turn = {"depan": 0.0, "miring": 0.40, "3/4": 0.40, "samping": 0.60, "side": 0.60}.get(hadap_raw.lower(), 0.0)
        else:
            turn = clamp(float(hadap_raw), 0.0, 0.65)

        # Proporsi badan besar & kaki pendek gemoy (persis referensi otak user: kaki pendek ~58px!)
        cy = -206.0
        # 1) Bayangan oval lembut di lantai
        c.ell(*T(0, 6, nodrop=True), 104 * s, 18 * s, (48, 34, 34, 56))

        # 2) Lengan pendek gemoy yang SELALU keluar rapi di sisi badan (tidak tersembunyi di belakang otak!)
        arms = st["arms"]
        hands = {}
        front_arms = []
        ph_w = st.get("phase", 0.0)
        amp_w = st.get("amp", 0.0)
        sw_w = st.get("swing", 1.0)
        for side, sgn in (("L", -1), ("R", 1)):
            a, e, hk = arms[side]
            if walking:
                swing_ang = math.sin(ph_w + (0.0 if side == "R" else math.pi)) * 30.0 * min(1.3, amp_w) * sw_w
                a = 28.0 + swing_ang
                e = 18.0 if side == "R" else -14.0
            if e < -125:
                front_arms.append((side, sgn, a, e, hk))
            else:
                hands[side] = self._mascot_arm(c, T, s, fl, sgn, a, e, hk, limb_c, oc_m, ow, cy, bentuk)

        # 3) Kaki pendek gemoy bersih + kaus kaki putih + sepatu sneaker kanvas rapi (persis referensi!)
        self._mascot_legs_and_shoes(c, st, T, s, fl, sit, limb_c, shoe_c, sol_c, acc_c, oc_m, ow, cy)

        # 4) Badan Utama = Wujud Asli Karakter Non-Manusia (bertekstur 3D penuh!)
        if bentuk == "virus":
            self._mascot_body_virus(c, T, TT, s, oc_m, ow, cy, p)
        elif bentuk in ("sel_imun", "imun"):
            self._mascot_body_imun(c, T, TT, s, oc_m, ow, cy, p)
        else:
            self._mascot_body_otak(c, T, TT, s, oc_m, ow, cy, p)

        # 5) Wajah Ekspresif + Lipsync VO penuh langsung di permukaan badan maskot!
        self._mascot_face(c, st, T, TT, s, fl, ow, oc_m, cy, turn, bentuk, p)

        # 6) Lengan depan khusus pose tangan dekat dagu/wajah
        for side, sgn, a, e, hk in front_arms:
            hands[side] = self._mascot_arm(c, T, s, fl, sgn, a, e, hk, limb_c, oc_m, ow, cy, bentuk)

        return hands

    def _mascot_halftone(self, c, T, s, cx, cy, rx, ry, col, a0_deg=110, a1_deg=255):
        """Titik-titik halftone retro lembut (opsional untuk maskot gaya print)."""
        for ring_k, r_frac in ((0, 0.86), (1, 0.74), (2, 0.62)):
            n_d = 12 - ring_k * 2
            for i in range(n_d):
                ang = math.radians(lerp(a0_deg, a1_deg, i / max(1, n_d - 1)) + ring_k * 5.0)
                px = cx + math.cos(ang) * rx * r_frac
                py = cy + math.sin(ang) * ry * r_frac
                rad = (3.4 - ring_k * 0.65) * s
                c.ell(*T(px, py), rad, rad, col)

    def _mascot_legs_and_shoes(self, c, st, T, s, fl, sit, limb_c, shoe_c, sol_c, acc_c, oc_m, ow, cy):
        """Kaki pendek kokoh super rapi + kaus kaki pergelangan putih + sepatu sneaker kanvas rata-tanah bertali rapi (persis referensi!)."""
        stance = st.get("legs", "stand")
        ph = st.get("phase", 0.0)
        amp = st.get("amp", 0.0)
        hip_y = cy + 92.0
        leg_specs = []
        for idx, sgn in enumerate((-1, 1)):
            hx = sgn * 32.0
            if stance == "walk" and amp > 0.01:
                sw = math.sin(ph + idx * math.pi)
                lift = max(0.0, -math.cos(ph + idx * math.pi)) * 20.0 * amp
                fx = hx + sw * 36.0 * amp
                fy = -14.0 - lift
                kx = (hx + fx) * 0.5 + 8.0 * max(0.0, sw)
                ky = (hip_y + fy) * 0.5 - lift * 0.25
                order = 0 if sw < 0 else 1
            elif sit > 0.05:
                fx = hx + sgn * 14.0 * sit
                fy = -16.0 - 14.0 * sit
                kx = hx + sgn * 16.0 * sit
                ky = hip_y + 28.0 * (1.0 - 0.3 * sit)
                order = idx
            else:
                fx = sgn * 36.0
                fy = -14.0
                kx = sgn * 34.0
                ky = (hip_y + fy) * 0.5
                order = idx
            leg_specs.append((order, sgn, (hx, hip_y), (kx, ky), (fx, fy)))
        leg_specs.sort(key=lambda item: item[0])

        limb_sh = gelap(limb_c, 0.16)
        shoe_sh = gelap(shoe_c, 0.18)
        shoe_hl = terang(shoe_c, 0.22)
        for _, sgn, H0, K0, F0 in leg_specs:
            fd = 1 if (stance == "walk" and amp > 0.01) else sgn
            fx, fy = F0
            ank = (fx - fd * 2.0, fy - 24.0)
            # 1) Tungkai pendek bersih bentuk tabung meruncing halus (tanpa garis coretan tengah!)
            dx_l, dy_l = ank[0] - H0[0], ank[1] - H0[1]
            ll_l = max(1e-5, math.hypot(dx_l, dy_l))
            nx_l, ny_l = -dy_l / ll_l, dx_l / ll_l
            if nx_l < 0:
                nx_l, ny_l = -nx_l, -ny_l
            r_top, r_bot = 12.0, 9.8
            leg_poly = [
                (H0[0] - nx_l * r_top, H0[1] - ny_l * r_top),
                (H0[0] + nx_l * r_top, H0[1] + ny_l * r_top),
                (ank[0] + nx_l * r_bot, ank[1] + ny_l * r_bot),
                (ank[0] - nx_l * r_bot, ank[1] - ny_l * r_bot),
            ]
            c.poly([T(*q) for q in leg_poly], limb_c, ow * 0.95, oc_m)
            # satu jalur cel-shading halus di tepi dalam + bayangan paha atas di bawah badan
            sh_side = [
                (H0[0] + nx_l * (r_top * 0.25), H0[1] + ny_l * (r_top * 0.25)),
                (H0[0] + nx_l * (r_top - 1.2), H0[1] + ny_l * (r_top - 1.2)),
                (ank[0] + nx_l * (r_bot - 1.2), ank[1] + ny_l * (r_bot - 1.2)),
                (ank[0] + nx_l * (r_bot * 0.25), ank[1] + ny_l * (r_bot * 0.25)),
            ]
            c.poly([T(*q) for q in sh_side], limb_sh)
            c.poly([T(H0[0] - nx_l * (r_top - 1), H0[1]), T(H0[0] + nx_l * (r_top - 1), H0[1]),
                    T(H0[0] + nx_l * (r_top - 1), H0[1] + 15), T(H0[0] - nx_l * (r_top - 1), H0[1] + 15)], limb_sh)
            c.poly([T(*q) for q in leg_poly], None, ow * 0.95, oc_m)

            # 2) Kaus kaki pendek putih rapi di atas kerah sneaker
            sock_pts = [
                (ank[0] - 11.5, ank[1] - 4), (ank[0] + 11.5, ank[1] - 4),
                (ank[0] + 13.0, ank[1] + 9), (ank[0] - 13.0, ank[1] + 9),
            ]
            c.poly([T(*q) for q in sock_pts], (248, 248, 252), ow * 0.85, oc_m)
            c.poly([T(ank[0] + 2, ank[1] - 3), T(ank[0] + 11, ank[1] - 3),
                    T(ank[0] + 12, ank[1] + 8), T(ank[0] + 2, ank[1] + 8)], (214, 222, 234))

            # 3) SEPATU SNEAKER KANVAS CHUNKY RAPI (sol putih rata-tanah + toe-cap putih bersih + 3 tali DI DALAM punggung sepatu!)
            # Sol karet putih tebal rata-bawah
            sole_pts = [
                (fx - fd * 24, fy + 2), (fx + fd * 46, fy + 2),
                (fx + fd * 47, fy + 10), (fx + fd * 38, fy + 15),
                (fx - fd * 18, fy + 15), (fx - fd * 25, fy + 10),
            ]
            c.poly([T(*q) for q in sole_pts], (248, 249, 252), ow * 0.95, oc_m)
            c.line([T(fx - fd * 21, fy + 11), T(fx + fd * 42, fy + 11)], (196, 206, 220), 2.4 * s)
            # Badan kanvas sneaker (kurva bersih mulus tanpa sudut runcing!)
            upper_pts = [
                (fx - fd * 24, fy + 2), (fx - fd * 24, fy - 16), (fx - fd * 14, fy - 24),
                (fx + fd * 4, fy - 24), (fx + fd * 22, fy - 15), (fx + fd * 42, fy - 8),
                (fx + fd * 47, fy + 2),
            ]
            c.poly([T(*q) for q in upper_pts], shoe_c, ow * 0.95, oc_m)
            # shading bawah tipis di sepanjang tumit-samping kanvas
            c.poly([T(fx - fd * 23, fy - 4), T(fx + fd * 20, fy - 3), T(fx + fd * 20, fy + 1), T(fx - fd * 23, fy + 1)], shoe_sh)
            # garis jahitan kanvas halus
            c.line([T(fx - fd * 16, fy - 14), T(fx - fd * 4, fy - 18)], shoe_hl, 2.2 * s)
            # ujung toe-cap putih rapi di bagian depan (mengikuti batas atas sepatu persis!)
            toe_pts = [
                (fx + fd * 22, fy + 2), (fx + fd * 24, fy - 13),
                (fx + fd * 36, fy - 11), (fx + fd * 44, fy - 6),
                (fx + fd * 47, fy + 2),
            ]
            c.poly([T(*q) for q in toe_pts], (250, 251, 254), ow * 0.85, oc_m)
            # 3 tali sepatu putih rapi DI DALAM lereng punggung sepatu (tidak mencuat keluar!)
            for lk_i in range(3):
                p_l = lk_i / 2.0
                lx_c = lerp(fx + fd * 1, fx + fd * 17, p_l)
                ly_c = lerp(fy - 18, fy - 11, p_l)
                c.line([T(lx_c - fd * 5, ly_c - 3), T(lx_c + fd * 6, ly_c - 1)], oc_m, 6.2 * s)
                c.line([T(lx_c - fd * 5, ly_c - 3), T(lx_c + fd * 6, ly_c - 1)], (252, 252, 254), 3.4 * s)

    def _mascot_arm(self, c, T, s, fl, sgn, a, e, hk, limb_c, oc_m, ow, cy, bentuk="otak"):
        """Lengan pendek jelas & natural yang SELALU berada di luar tepi badan + sarung tangan putih 2-pass super bersih!"""
        # Pastikan lengan tidak pernah melipat masuk ke belakang tubuh otak yang lebar!
        a_eff = max(34.0, a) if a < 38.0 else a
        e_eff = e
        if e_eff < -45.0 and e_eff > -125.0:
            # lengan santai/pinggang: melengkung lembut ke bawah-luar (persis tangan kanan referensi otak!)
            a_eff = 48.0
            e_eff = -38.0
        elif hk == "p":
            # pose peace/tunjuk: melengkung gagah keluar lalu NAIK KE ATAS (persis tangan kiri referensi otak!)
            a_eff = 68.0
            e_eff = 76.0
        ar = math.radians(a_eff)
        br = math.radians(a_eff + e_eff)
        sh_x = 104.0 if bentuk == "otak" else 90.0
        sh = (sgn * sh_x, cy + 20.0)
        up_l = 44.0
        fo_l = 40.0
        el = (sh[0] + sgn * math.sin(ar) * up_l, sh[1] + math.cos(ar) * up_l)
        hd = (el[0] + sgn * math.sin(br) * fo_l, el[1] + math.cos(br) * fo_l)
        S, E, H = T(*sh), T(*el), T(*hd)
        aw = 19.5 * s
        # Pipa lengan pendek bersih 1-warna + bayangan tepi bawah tipis (tanpa garis ganda acak!)
        c.curve([S, E, H], oc_m, aw + 2.1 * ow, n=7)
        c.curve([S, E, H], limb_c, aw, n=7)
        c.curve([T(sh[0], sh[1] + 3), T(el[0], el[1] + 3), T(hd[0], hd[1] + 3)], gelap(limb_c, 0.14), aw * 0.34, n=6)
        dvx, dvy = H[0] - E[0], H[1] - E[1]
        ang = math.atan2(dvy, dvx)
        g_kind = hk
        if hk == "m" and a_eff < 55.0 and e_eff <= 0:
            g_kind = "hang"
        self._mascot_glove(c, H, ang, s * 1.15, sgn, fl, g_kind, oc_m, ow)
        return {"pos": H, "ang": ang, "elbow": E}

    def _mascot_glove(self, c, H, ang, s, sgn, fl, kind, oc_m, ow):
        """Sarung tangan kartun dengan JARI-JARI ANATOMIS JELAS (peace V, jempol + 3 jari terlipat, tangan santai berjari 4, kepal berbuku, & tangan terbuka 5 jari!)."""
        gl_c = (252, 253, 255)
        gl_sh = (204, 216, 232)
        d_x = sgn * fl
        pad_o = ow * 0.92

        def UP(dx, dy):
            """Koordinat tegak dunia (untuk pose yang harus selalu menghadap ke atas/bawah alami seperti peace, jempol, tangan santai!)."""
            return (H[0] + dx * d_x * s, H[1] + dy * s)

        # 1) PEACE / TUNJUK ("p"): 2 jari V tegak + 2 jari terlipat jelas + ibu jari melingkup (persis tangan kiri referensi otak!)
        if kind == "p":
            for pass_i in range(2):
                pad = pad_o if pass_i == 0 else 0.0
                col = oc_m if pass_i == 0 else gl_c
                # manset pergelangan & telapak
                c.ell(*UP(-1, 16), (13.0 + pad) * s, (7.5 + pad) * s, col)
                c.ell(*UP(0, 2), (19.5 + pad) * s, (17.5 + pad) * s, col)
                # jari telunjuk & jari tengah tegak membentuk V rapi
                c.line([UP(-5, -6), UP(-15, -45)], col, (12.2 + pad * 2) * s)
                c.line([UP(6, -6), UP(15, -45)], col, (12.2 + pad * 2) * s)
            # shading lembut bawah telapak
            c.ell(*UP(0, 9), 15.0 * s, 8.5 * s, gl_sh)
            # 2 jari manis & kelingking tertekuk rapi + ibu jari melingkup di atasnya!
            c.ell(*UP(13, -1), 7.2 * s, 9.5 * s, gl_c, ow * 0.85, oc_m)
            c.ell(*UP(5, 1), 7.6 * s, 9.5 * s, gl_c, ow * 0.85, oc_m)
            c.curve([UP(-13, -4), UP(-4, -8), UP(5, -2), UP(-2, 7), UP(-13, 4)], oc_m, 12.0 * s)
            c.curve([UP(-13, -4), UP(-4, -8), UP(5, -2), UP(-2, 7), UP(-13, 4)], gl_c, 7.6 * s)
            c.curve([UP(-10, 14), UP(0, 17), UP(10, 14)], oc_m, 2.0 * s)
            return

        # 2) JEMPOL ("t"): Ibu jari tegak jelas ke atas + 3 jari melingkar bertumpuk rapi di sisi depan kepalan!
        if kind == "t":
            for pass_i in range(2):
                pad = pad_o if pass_i == 0 else 0.0
                col = oc_m if pass_i == 0 else gl_c
                # manset pergelangan
                c.ell(*UP(-16, 4), (7.5 + pad) * s, (12.5 + pad) * s, col)
                # badan kepalan tangan
                c.ell(*UP(0, 4), (17.5 + pad) * s, (17.0 + pad) * s, col)
                # ibu jari melengkung tegak ke atas!
                c.curve([UP(-4, -6), UP(-5, -22), UP(-11, -35)], col, (12.0 + pad * 2) * s)
                # 3 jari terlipat bertumpuk di tepi kanan kepalan (jelas terlihat 3 ruas jari!)
                for fy_j, rx_j in ((-6, 11.5), (4, 12.2), (14, 10.5)):
                    c.ell(*UP(11, fy_j), (rx_j + pad) * s, (5.8 + pad) * s, col)
            c.ell(*UP(-2, 12), 13.5 * s, 7.5 * s, gl_sh)
            # garis lipatan jelas memisahkan 3 jari yang terlipat!
            for fy_j, rx_j in ((-6, 11.0), (4, 11.8), (14, 10.0)):
                c.ell(*UP(11, fy_j), rx_j * s, 5.4 * s, gl_c, ow * 0.80, oc_m)
            c.curve([UP(-10, -7), UP(-10, 14)], oc_m, 2.0 * s)
            return

        # 3) TANGAN SANTAI MENGGANTUNG ("hang"): persis tangan kanan bawah referensi otak — ibu jari melengkung ke dalam + 3 jari jatuh rapi!
        if kind == "hang":
            for pass_i in range(2):
                pad = pad_o if pass_i == 0 else 0.0
                col = oc_m if pass_i == 0 else gl_c
                # manset pergelangan atas
                c.ell(*UP(0, -10), (13.0 + pad) * s, (7.2 + pad) * s, col)
                # punggung telapak
                c.ell(*UP(1, 3), (17.0 + pad) * s, (14.5 + pad) * s, col)
                # ibu jari melengkung lembut di sisi dalam (-x)
                c.curve([UP(-12, 0), UP(-19, 10), UP(-14, 21)], col, (10.5 + pad * 2) * s)
                # 3 jari melengkung ke bawah (telunjuk, tengah, manis/kelingking — jelas terpisah!)
                c.curve([UP(-5, 10), UP(-6, 22), UP(-9, 28)], col, (10.0 + pad * 2) * s)
                c.curve([UP(5, 11), UP(5, 24), UP(1, 31)], col, (10.2 + pad * 2) * s)
                c.curve([UP(14, 8), UP(15, 19), UP(11, 25)], col, (9.4 + pad * 2) * s)
            # shading biru-abu lembut di sisi dalam & bawah jari
            c.ell(*UP(-4, 10), 12.0 * s, 8.5 * s, gl_sh)
            # garis celah antar-jari jelas sehingga benar-benar terbaca jari-jari tangan!
            c.curve([UP(-10, 4), UP(-12, 16)], oc_m, 2.2 * s)
            c.curve([UP(-1, 13), UP(-1, 26)], oc_m, 2.2 * s)
            c.curve([UP(9, 12), UP(9, 24)], oc_m, 2.2 * s)
            c.curve([UP(-10, -8), UP(0, -5), UP(11, -8)], oc_m, 2.0 * s)
            return

        # 4) KEPAL MARAH ("f"): kepalan tangan dengan 4 buku jari terlipat + ibu jari mengunci di depan!
        if kind == "f":
            for pass_i in range(2):
                pad = pad_o if pass_i == 0 else 0.0
                col = oc_m if pass_i == 0 else gl_c
                c.ell(*UP(-1, -11), (12.5 + pad) * s, (7.0 + pad) * s, col)
                c.ell(*UP(0, 3), (18.5 + pad) * s, (16.0 + pad) * s, col)
                for fx_j in (-12, -4, 4, 12):
                    c.ell(*UP(fx_j, 12), (5.8 + pad) * s, (8.5 + pad) * s, col)
            c.ell(*UP(0, 12), 14.0 * s, 7.0 * s, gl_sh)
            for fx_j in (-11, -3.5, 4, 11.5):
                c.ell(*UP(fx_j, 11), 5.2 * s, 8.0 * s, gl_c, ow * 0.78, oc_m)
            # ibu jari melintang mengunci kepalan
            c.curve([UP(-14, 1), UP(-4, 5), UP(5, 4)], oc_m, 11.0 * s)
            c.curve([UP(-14, 1), UP(-4, 5), UP(5, 4)], gl_c, 6.8 * s)
            return

        # 5) TANGAN TERBUKA / MELAMBAI ("m"): 5 jari (ibu jari + 4 jari mekar jelas & natural mengikuti arah lengan!)
        ux, uy = math.cos(ang), math.sin(ang)
        nx, ny = -uy, ux
        if d_x < 0:
            nx, ny = -nx, -ny

        def G(dx, dy):
            return (H[0] + (ux * dx + nx * dy) * s, H[1] + (uy * dx + ny * dy) * s)

        fingers = [
            (9, -8, 20, -25, 9.6),    # ibu jari
            (13, -7, 34, -15, 9.4),   # telunjuk
            (15, -2, 39, -3, 9.6),    # jari tengah
            (14, 4, 36, 9, 9.2),      # jari manis
            (11, 9, 28, 17, 8.4),     # kelingking
        ]
        for pass_i in range(2):
            pad = pad_o if pass_i == 0 else 0.0
            col = oc_m if pass_i == 0 else gl_c
            c.ell(*G(-4, 0), (8.5 + pad) * s, (13.0 + pad) * s, col)
            c.ell(*G(10, 0), (16.5 + pad) * s, (15.5 + pad) * s, col)
            for x0_f, y0_f, x1_f, y1_f, wf in fingers:
                c.line([G(x0_f, y0_f), G(x1_f, y1_f)], col, (wf + pad * 2) * s)
        # shading lembut telapak + garis celah pangkal jari agar 5 jari terbaca sangat jelas!
        c.ell(*G(11, 5), 11.5 * s, 8.5 * s, gl_sh)
        for sx_g, sy_g, ex_g, ey_g in ((17, -9, 24, -12), (19, -3, 27, -3), (18, 4, 26, 6), (14, 9, 21, 13)):
            c.line([G(sx_g, sy_g), G(ex_g, ey_g)], oc_m, 2.0 * s)
        c.curve([G(2, -10), G(0, 0), G(2, 10)], oc_m, 2.0 * s)

    def _mascot_body_otak(self, c, T, TT, s, oc_m, ow, cy, p):
        """Wujud maskot Otak 3D GLOSSY BERGELOMBANG (persis referensi user: lipatan gyri gembul, kilau glossy DI BAWAH garis celah, sulkus melingkar mulus!)."""
        bc = warna(p.get("kulit"), (248, 174, 178))
        b_deep = (196, 98, 108)       # bayangan dalam bawah & celah lipatan
        b_mid = (232, 134, 142)       # pink koral sedang (sisi bawah)
        b_lit = (252, 202, 204)       # pink peach cerah (bagian atas)
        b_spec = (255, 242, 244)      # kilau glossy lembut (digambar SEBELUM garis sulkus!)
        oc_b = (56, 22, 22)

        # 1) Siluet 2-pass luar otak lebar penuh (2 hemisfer jelas dengan lekukan tengah atas & bawah!)
        outer_lobes = [
            (-36, -78, 44, 38), (-78, -62, 46, 42), (-108, -26, 46, 42),
            (-120, 18, 44, 40), (-96, 58, 46, 38), (-54, 76, 46, 36), (-20, 70, 38, 32),
            (36, -78, 44, 38), (78, -62, 46, 42), (108, -26, 46, 42),
            (120, 18, 44, 40), (96, 58, 46, 38), (54, 76, 46, 36), (20, 70, 38, 32),
            (-36, -4, 76, 70), (36, -4, 76, 70),
        ]
        # Pass A: outline luar coklat-maroon tebal menyatu mulus
        for dx, dy, rx, ry in outer_lobes:
            c.ell(*T(dx, cy + dy), (rx + 5.2) * s, (ry + 5.2) * s, oc_b)
        # Pass B: dasar bayangan rose-tua -> lalu isi pink koral naik ke kiri-atas (shading 100% di dalam siluet!)
        for dx, dy, rx, ry in outer_lobes:
            c.ell(*T(dx, cy + dy), rx * s, ry * s, b_deep)
        for dx, dy, rx, ry in outer_lobes:
            c.ell(*T(dx - 3, cy + dy - 8), (rx - 4) * s, (ry - 7) * s, bc)
        # Gradasi pencahayaan hangat atas otak lebih cerah (peach-pink) & bawah lebih teduh
        c.ell(*T(-42, cy - 52), 78 * s, 54 * s, b_lit)
        c.ell(*T(42, cy - 52), 78 * s, 54 * s, b_lit)
        c.ell(*T(0, cy + 4), 76 * s, 58 * s, bc)

        # 2) Bantal-bantal lipatan GYRI 3D lembut + kilau melengkung glossy (DIGAMBAR SEBELUM GARIS SULKUS agar tidak menimpa garis!)
        gyri = [
            (-36, -76, 32, 22, b_lit), (36, -76, 32, 22, b_lit),
            (-78, -58, 32, 24, b_lit), (78, -58, 32, 24, b_lit),
            (-104, -22, 30, 24, bc), (104, -22, 30, 24, bc),
            (-114, 18, 30, 24, b_mid), (114, 18, 30, 24, b_mid),
            (-92, 54, 32, 22, b_mid), (92, 54, 32, 22, b_mid),
            (-52, 70, 32, 20, b_mid), (52, 70, 32, 20, b_mid),
        ]
        for gx, gy, grx, gry, gcol in gyri:
            c.ell(*T(gx + 2, cy + gy + 5), grx * s, gry * s, b_deep)
            c.ell(*T(gx, cy + gy), (grx - 2) * s, (gry - 2) * s, gcol)
            # kilau melengkung lembut di punggung atas tiap bantal lipatan (khas tekstur kenyal glossy referensi!)
            c.curve(TT(arc_pts(gx - 2, cy + gy + 2, grx * 0.65, gry * 0.65, 205, 315, 8)), b_spec, 5.2 * s)

        # 3) Belahan tengah hemisfer & lipatan SULKUS MELINGKAR MULUS (semua kurva organik mulus, NOL garis patah zig-zag!)
        def _sulcus(pts, w_line=3.0):
            # bayangan rose tipis tepat di bawah lipatan untuk ilusi kedalaman 3D lembut
            c.curve(TT([(px + 1.5, py + 3.5) for px, py in pts]), b_deep, (w_line + 3.2) * s)
            c.curve(TT(pts), oc_b, w_line * s)

        # Belahan utama tengah atas membelah 2 hemisfer + belahan bawah
        _sulcus([(0, cy - 104), (-3, cy - 82), (2, cy - 60), (-2, cy - 42), (0, cy - 28)], 4.2)
        _sulcus([(0, cy + 94), (2, cy + 78), (-1, cy + 62)], 3.4)

        # Lipatan-lipatan sulkus melengkung bundar-mulus (U-loops & C-coils halus di kedua hemisfer!)
        coils = [
            # Hemisfer kiri (melingkar lembut mengelilingi dahi, pelipis, pipi & dagu!)
            arc_pts(-32, cy - 72, 24, 18, 120, 290, 10),
            arc_pts(-64, cy - 52, 22, 18, 30, 210, 10),
            arc_pts(-92, cy - 22, 22, 18, -55, 130, 10),
            arc_pts(-100, cy + 20, 22, 18, -75, 115, 10),
            arc_pts(-76, cy + 50, 22, 16, -25, 165, 10),
            arc_pts(-44, cy + 66, 20, 15, 20, 205, 10),
            # Cabang pendek lembut di antara dahi & pelipis
            [(-4, cy - 64), (-22, cy - 56), (-38, cy - 62)],
            [(-118, cy - 2), (-98, cy - 4), (-84, cy + 6)],
            # Hemisfer kanan (simetris tapi sedikit variatif organik!)
            arc_pts(32, cy - 72, 24, 18, 250, 420, 10),
            arc_pts(64, cy - 52, 22, 18, -30, 150, 10),
            arc_pts(92, cy - 22, 22, 18, 50, 235, 10),
            arc_pts(100, cy + 20, 22, 18, 65, 255, 10),
            arc_pts(76, cy + 50, 22, 16, 15, 205, 10),
            arc_pts(44, cy + 66, 20, 15, -25, 160, 10),
            [(4, cy - 62), (22, cy - 54), (38, cy - 60)],
            [(118, cy - 2), (98, cy - 4), (84, cy + 6)],
        ]
        for pts_cr in coils:
            _sulcus(pts_cr, 2.8)

    def _mascot_body_virus(self, c, T, TT, s, oc_m, ow, cy, p):
        """Wujud maskot Virus 100% persis referensi user: 2-pass siluet hijau menyatu mulus, 10 spike corong hijau + 4 tonjolan kecil + shading bersih di dalam!"""
        vc = warna(p.get("kulit"), (136, 198, 56))
        vsh = gelap(vc, 0.19)
        vhl = terang(vc, 0.30)
        voc = (34, 42, 22)

        # Pra-hitung 10 spike-corong utama & 4 tonjolan kecil (persis siluet referensi virus user!)
        main_angles = [k * 36.0 - 90.0 for k in range(10)]
        nub_angles = [-112.0, -40.0, 68.0, 140.0]

        def _draw_virus_shapes(pad, col, draw_inner_shade=False):
            # 1) 10 spike corong/jamur menyatu mulus
            for deg in main_angles:
                ang = math.radians(deg)
                ca, sa = math.cos(ang), math.sin(ang)
                nx, ny = -sa, ca
                r0, r1 = 84.0, 120.0
                # tangkai menyempit di tengah lalu melebar di pangkal & kepala corong
                stem = [
                    (ca * r0 + nx * (15 + pad), cy + sa * r0 + ny * (15 + pad)),
                    (ca * ((r0 + r1) * 0.52) + nx * (7.5 + pad), cy + sa * ((r0 + r1) * 0.52) + ny * (7.5 + pad)),
                    (ca * r1 + nx * (11 + pad), cy + sa * r1 + ny * (11 + pad)),
                    (ca * r1 - nx * (11 + pad), cy + sa * r1 - ny * (11 + pad)),
                    (ca * ((r0 + r1) * 0.52) - nx * (7.5 + pad), cy + sa * ((r0 + r1) * 0.52) - ny * (7.5 + pad)),
                    (ca * r0 - nx * (15 + pad), cy + sa * r0 - ny * (15 + pad)),
                ]
                c.poly(TT(stem), col)
                # kepala corong bulat melebar sedikit
                tx, ty = ca * (r1 + 6), cy + sa * (r1 + 6)
                c.ell(*T(tx, ty), (17.5 + pad) * s, (16.5 + pad) * s, col)
                if draw_inner_shade:
                    # highlight mungil di sisi kiri-atas tiap kepala spike
                    c.ell(*T(tx - 4.5, ty - 4.5), 6.0 * s, 4.2 * s, vhl)
            # 2) 4 tonjolan kecil mungil di sela-sela spike utama (ciri khas referensi!)
            for deg in nub_angles:
                ang = math.radians(deg)
                ca, sa = math.cos(ang), math.sin(ang)
                c.ell(*T(ca * 102, cy + sa * 102), (10.5 + pad) * s, (10.5 + pad) * s, col)
            # 3) Badan bulat sempurna
            c.ell(*T(0, cy), (97.0 + pad) * s, (97.0 + pad) * s, col)

        # Pass 1: Outline tebal bersih menyatu (NOL garis pemotong di pangkal spike!)
        _draw_virus_shapes(5.2, voc, False)
        # Pass 2: Isi bayangan hijau-tua pada seluruh bentuk dulu (cel-shading bawah-kanan yang 100% rapi & melengkung mulus!)
        _draw_virus_shapes(0.0, vsh, False)
        # Pass 3: Isi hijau cerah utama, lalu lingkaran hijau cerah bergeser sedikit ke kiri-atas untuk bulan sabit bayangan mulus tanpa garis lurus patah!
        _draw_virus_shapes(0.0, vc, True)
        c.ell(*T(0, cy), 96.5 * s, 96.5 * s, vsh)
        c.ell(*T(-8, cy - 8), 89.0 * s, 89.0 * s, vc)
        # 6 bintik mikroba hijau-tua TANPA outline kasar (persis referensi user!)
        for sx_p, sy_p, rx_p, ry_p in ((-62, -46, 9, 7), (-34, -74, 7, 5), (26, -70, 10, 7),
                                       (64, -42, 8, 6), (52, 54, 11, 7), (-56, 48, 9, 6)):
            c.ell(*T(sx_p, cy + sy_p), rx_p * s, ry_p * s, vsh)
        # kilau mengkilap di pojok kiri atas bola virus
        c.ell(*T(-50, cy - 58), 16 * s, 7.5 * s, vhl)

    def _mascot_body_imun(self, c, T, TT, s, oc_m, ow, cy, p):
        """Wujud maskot Sel Imun 2-pass siluet sel darah putih amoeboid mulus + cel-shading rapi di dalam + topi perisai medis!"""
        ic = warna(p.get("kulit"), (244, 246, 238))
        ish = (204, 222, 234)
        badge_c = warna(p.get("sepatu"), (78, 134, 178))
        gold_c = warna(p.get("sol_warna"), (226, 174, 84))

        lobes = [
            (-82, -24, 52, 48), (-44, -66, 54, 46), (44, -66, 54, 46),
            (82, -24, 52, 48), (90, 26, 48, 44), (46, 70, 52, 42),
            (-46, 70, 52, 42), (-90, 26, 48, 44), (0, 0, 96, 84),
        ]
        # Pass 1: outline luar menyatu
        for dx, dy, rx, ry in lobes:
            c.ell(*T(dx, cy + dy), (rx + 4.4) * s, (ry + 4.4) * s, oc_m)
        # Pass 2: bayangan biru-lembut di dalam siluet -> isi putih-gading bergeser ke kiri-atas (NOL bocor keluar!)
        for dx, dy, rx, ry in lobes:
            c.ell(*T(dx, cy + dy), rx * s, ry * s, ish)
        for dx, dy, rx, ry in lobes:
            c.ell(*T(dx - 5, cy + dy - 7), (rx - 4) * s, (ry - 5) * s, ic)
        for gx, gy, gr in ((-76, -24, 9), (78, -20, 10), (-72, 44, 8), (72, 46, 9)):
            c.ell(*T(gx, cy + gy), gr * s, gr * 0.85 * s, (188, 216, 234))
        c.ell(*T(-26, cy - 60), 34 * s, 14 * s, (255, 255, 252))

        # Topi/helm lencana penjaga imun mungil di puncak sel
        cap_y = cy - 90
        c.blob(TT([(-56, cap_y + 18), (-50, cap_y - 24), (0, cap_y - 36), (50, cap_y - 24),
                   (56, cap_y + 18), (0, cap_y + 24)]), badge_c, ow, oc_m, n=6)
        c.blob(TT([(-62, cap_y + 16), (0, cap_y + 8), (62, cap_y + 16), (54, cap_y + 28), (0, cap_y + 22), (-54, cap_y + 28)]),
               gold_c, ow * 0.85, oc_m, n=5)
        c.ell(*T(0, cap_y - 8), 18 * s, 18 * s, (248, 246, 236), ow * 0.75, oc_m)
        c.poly(TT([(-10, cap_y - 12), (10, cap_y - 12), (10, cap_y - 4), (-10, cap_y - 4)]), (206, 82, 74))
        c.poly(TT([(-4, cap_y - 18), (4, cap_y - 18), (4, cap_y + 2), (-4, cap_y + 2)]), (206, 82, 74))

    def _mascot_face(self, c, st, T, TT, s, fl, ow, oc_m, cy, turn, bentuk, p):
        """Wajah maskot ekspresif & super rapi (Virus = mata miring tajam + seringai bertaring persis referensi; Otak/Imun = mata pie-cut ceria!)."""
        ex = eks(st.get("expr", "senang"))
        bl = st.get("blink", 0.0)
        lk = st.get("look", ex.get("look", (0.0, 0.0)))
        fx = 10.0 * turn

        # === KHUSUS VIRUS: ekspresi nakal ikonik persis referensi user (alis V tegas + 2 mata besar tajam + seringai lebar bertaring!) ===
        if bentuk == "virus":
            voc = (34, 42, 22)
            vc = warna(p.get("kulit"), (136, 198, 56))
            eye_y = cy - 12.0
            eye_sep = 30.0
            ek = ex["eyes"]
            # 1) 2 Mata Virus lebar ekspresif
            for sg in (-1, 1):
                ex_x = fx + sg * eye_sep
                if bl > 0.72 or ek == "arc_dn":
                    c.curve(TT([(ex_x - 18, eye_y + 2), (ex_x, eye_y + 12), (ex_x + 18, eye_y + 2)]), voc, 4.2 * s)
                elif ek == "arc_up":
                    c.curve(TT([(ex_x - 18, eye_y + 8), (ex_x, eye_y - 10), (ex_x + 18, eye_y + 8)]), voc, 4.2 * s)
                elif ek == "wink" and sg > 0:
                    c.curve(TT([(ex_x - 18, eye_y + 4), (ex_x, eye_y - 8), (ex_x + 18, eye_y + 4)]), voc, 4.2 * s)
                else:
                    erx = 24.5 if ek != "wide" else 27.0
                    ery = 22.0 if ek != "wide" else 26.0
                    c.ell(*T(ex_x, eye_y), erx * s, ery * s, (254, 253, 248), ow * 1.15, voc)
                    if ek == "dot":
                        c.ell(*T(ex_x + lk[0] * 4, eye_y + lk[1] * 4), 6.0 * s, 6.0 * s, voc)
                    else:
                        px = ex_x + lk[0] * 6.0 + (7.0 if sg < 0 else 6.0)
                        py = eye_y + lk[1] * 5.0 + 1.0
                        c.ell(*T(px, py), 11.5 * s, 12.5 * s, voc)
                        c.ell(*T(px - 3.5, py - 4.0), 3.4 * s, 3.4 * s, (255, 255, 255))
                    # kelopak miring tegas di atas mata untuk ekspresi nakal/marah khas referensi virus!
                    if ek not in ("wide", "dot") and st.get("expr") not in ("kaget", "panik", "sedih"):
                        cut_in = eye_y - 6.0
                        cut_out = eye_y - 24.0
                        if sg < 0:
                            c.poly(TT([(ex_x - erx - 4, eye_y - ery - 8), (ex_x + erx + 4, eye_y - ery - 8),
                                       (ex_x + erx + 4, cut_in), (ex_x - erx - 4, cut_out)]), vc)
                        else:
                            c.poly(TT([(ex_x - erx - 4, eye_y - ery - 8), (ex_x + erx + 4, eye_y - ery - 8),
                                       (ex_x + erx + 4, cut_out), (ex_x - erx - 4, cut_in)]), vc)
            # 2) Alis V tegas bergaris tebal (persis gambar referensi virus!)
            brow = ex.get("brow", (0, 0, 0))
            if st.get("expr") in ("kaget", "panik"):
                for sg in (-1, 1):
                    bx = fx + sg * eye_sep
                    c.curve(TT([(bx - 18, eye_y - 34), (bx, eye_y - 42), (bx + 18, eye_y - 34)]), voc, 5.2 * s)
            elif st.get("expr") == "sedih":
                for sg in (-1, 1):
                    bx = fx + sg * eye_sep
                    c.curve(TT([(bx - 18, eye_y - 26 + sg * 6), (bx + 18, eye_y - 26 - sg * 6)]), voc, 5.2 * s)
            else:
                # alis V nakal/jahil khas referensi: menukik tajam ke tengah!
                c.curve(TT([(fx - 58, eye_y - 28), (fx - 26, eye_y - 16), (fx - 6, eye_y - 5)]), voc, 6.2 * s)
                c.curve(TT([(fx + 58, eye_y - 28), (fx + 26, eye_y - 16), (fx + 6, eye_y - 5)]), voc, 6.2 * s)
                c.curve(TT([(fx - 6, eye_y - 5), (fx - 8, eye_y - 16)]), voc, 3.2 * s)
                c.curve(TT([(fx + 6, eye_y - 5), (fx + 8, eye_y - 16)]), voc, 3.2 * s)

            # 3) Mulut seringai lebar bertaring khas referensi virus (tetap mendukung VO lipsync & 20 ekspresi!)
            talk = st.get("mouth")
            op = talk if talk is not None else ex.get("open", 0.65)
            mk = "open" if talk is not None else ex["mouth"]
            my = eye_y + 26.0
            if mk in ("smirk", "grin", "open", "smile"):
                mw = 52.0 if mk in ("smirk", "grin") else 40.0
                mh = lerp(22.0, 42.0, clamp(op, 0.35, 1.0)) if mk == "open" else 36.0
                # lengkung seringai bulan sabit lebar persis referensi!
                top_arc = [(fx - mw, my - 6), (fx - mw * 0.45, my + 8), (fx, my + 12), (fx + mw * 0.45, my + 8), (fx + mw, my - 6)]
                bot_arc = [(fx + mw * 0.80, my + mh * 0.72), (fx + mw * 0.35, my + mh), (fx, my + mh + 2),
                           (fx - mw * 0.35, my + mh), (fx - mw * 0.80, my + mh * 0.72)]
                c.blob(TT(top_arc + bot_arc), voc, ow * 0.9, voc, n=4)
                # barisan gigi putih tajam bertaring kiri & kanan (persis referensi!)
                t_pts = [
                    (fx - mw * 0.78, my + 2), (fx - mw * 0.42, my + 11), (fx, my + 14),
                    (fx + mw * 0.42, my + 11), (fx + mw * 0.78, my + 2),
                    (fx + mw * 0.60, my + mh * 0.76), (fx + mw * 0.44, my + mh * 0.48),
                    (fx + mw * 0.30, my + mh * 0.82), (fx, my + mh * 0.86),
                    (fx - mw * 0.30, my + mh * 0.82), (fx - mw * 0.44, my + mh * 0.48),
                    (fx - mw * 0.60, my + mh * 0.76),
                ]
                c.poly(TT(t_pts), (254, 253, 248))
                # garis pemisah antar-gigi + sudut lesung senyum nakal
                c.line(TT([(fx, my + 14), (fx, my + mh * 0.84)]), voc, 2.4 * s)
                c.line(TT([(fx - mw * 0.28, my + 12), (fx - mw * 0.28, my + mh * 0.80)]), voc, 2.2 * s)
                c.line(TT([(fx + mw * 0.28, my + 12), (fx + mw * 0.28, my + mh * 0.80)]), voc, 2.2 * s)
                c.curve(TT(top_arc), voc, 4.4 * s)
                c.curve(TT([(fx - mw - 6, my - 4), (fx - mw + 3, my - 10)]), voc, 3.2 * s)
                c.curve(TT([(fx + mw + 6, my - 4), (fx + mw - 3, my - 10)]), voc, 3.2 * s)
            elif mk == "gigit":
                c.poly(TT([(fx - 38, my + 2), (fx + 38, my + 2), (fx + 32, my + 24), (fx - 32, my + 24)]), (254, 253, 248), ow, voc)
                for gx in (-18, 0, 18):
                    c.line(TT([(fx + gx, my + 2), (fx + gx, my + 24)]), voc, 2.6 * s)
            elif mk in ("o", "yawn", "wave_o"):
                c.ell(*T(fx, my + 16), 16 * s, 20 * s, (156, 48, 52), ow, voc)
                c.ell(*T(fx, my + 24), 8 * s, 6 * s, (226, 108, 92))
            elif mk in ("frown", "pout"):
                c.curve(TT([(fx - 26, my + 24), (fx, my + 8), (fx + 26, my + 24)]), voc, 4.4 * s)
            else:
                c.curve(TT([(fx - 24, my + 12), (fx, my + 10), (fx + 24, my + 12)]), voc, 4.2 * s)

            if ex.get("sweat"):
                c.blob(TT([(fx + 66, eye_y - 30), (fx + 74, eye_y - 10), (fx + 66, eye_y - 4), (fx + 58, eye_y - 10)]),
                       (142, 212, 246), ow * 0.6, voc, n=4)
            return

        # === OTAK & SEL IMUN: Mata Chibi/Ghibli Besar Berkilau Biru-Samudra (persis referensi otak user!) ===
        eye_y = cy - 4.0
        eye_sep = 34.0
        iris_c = warna(p.get("iris"), (56, 126, 178))
        iris_glow = terang(iris_c, 0.42)
        ek = ex["eyes"]
        for idx, sg in enumerate((-1, 1)):
            ex_x = fx + sg * eye_sep
            if bl > 0.72 or ek == "arc_dn":
                c.curve(TT([(ex_x - 19, eye_y + 2), (ex_x, eye_y + 13), (ex_x + 19, eye_y + 2)]), oc_m, 4.2 * s)
            elif ek == "arc_up" or (ek == "wink" and sg > 0):
                c.curve(TT([(ex_x - 19, eye_y + 7), (ex_x, eye_y - 12), (ex_x + 19, eye_y + 7)]), oc_m, 4.4 * s)
            else:
                erx = 26.5 if ek != "wide" else 29.0
                ery = 27.5 if ek != "wide" else 30.5
                # sklera putih bersih + garis tebal kelopak atas
                c.ell(*T(ex_x, eye_y), erx * s, ery * s, (254, 254, 255), ow * 1.15, oc_m)
                c.curve(TT(arc_pts(ex_x, eye_y, erx, ery, 200, 340, 14)), oc_m, ow * 1.65)
                if ek == "dot":
                    c.ell(*T(ex_x + lk[0] * 4, eye_y + lk[1] * 4), 6.2 * s, 6.2 * s, oc_m)
                else:
                    px = ex_x + lk[0] * 6.0
                    py = eye_y + lk[1] * 6.0 + 2.0
                    ir = 19.5 * (0.85 if ek == "wide" else 1.0)
                    # iris biru-samudra bergradasi + kilau sabit bawah + pupil hitam mengkilap + 2 titik kilau putih!
                    c.ell(*T(px, py), ir * s, ir * s, gelap(iris_c, 0.28), ow * 0.55, oc_m)
                    c.ell(*T(px, py + 1.5), (ir - 2.0) * s, (ir - 2.5) * s, iris_c)
                    c.ell(*T(px, py + ir * 0.36), ir * 0.62 * s, ir * 0.36 * s, iris_glow)
                    c.ell(*T(px, py - 1.0), ir * 0.60 * s, ir * 0.62 * s, (24, 22, 28))
                    # 2 titik kilau besar & kecil persis referensi mata chibi!
                    c.ell(*T(px - ir * 0.34, py - ir * 0.34), ir * 0.34 * s, ir * 0.32 * s, (255, 255, 255))
                    c.ell(*T(px + ir * 0.30, py + ir * 0.28), ir * 0.16 * s, ir * 0.16 * s, (255, 255, 255))
                if ek == "half":
                    c.poly(TT([(ex_x - erx - 2, eye_y - ery - 2), (ex_x + erx + 2, eye_y - ery - 2),
                               (ex_x + erx + 2, eye_y - 6), (ex_x - erx - 2, eye_y - 6)]), warna(p.get("kulit"), (248, 174, 178)))
                    c.line(TT([(ex_x - erx, eye_y - 6), (ex_x + erx, eye_y - 6)]), oc_m, 3.2 * s)

        # Alis lembut melengkung manis di atas mata (persis referensi!)
        brow = ex.get("brow", (0, 0, 0))
        for sg, tilt_b in ((-1, brow[1]), (1, brow[2])):
            bx = fx + sg * (eye_sep - 2)
            by = eye_y - 38.0 - brow[0] * 0.55
            p0 = (bx - 13, by + 2 + sg * tilt_b * 8)
            pm = (bx, by - 3)
            p1 = (bx + 13, by + 2 - sg * tilt_b * 8)
            c.curve(TT([p0, pm, p1]), oc_m, 5.4 * s)

        # Pipi merona hangat halus (tanpa hidung tajam agar wajah super imut seperti referensi!)
        blush = ex.get("blush", 0.45)
        if blush > 0.05:
            bcol = (242, 134, 152) if bentuk == "otak" else (242, 152, 176)
            for sg in (-1, 1):
                c.ell(*T(fx + sg * 54, eye_y + 24), 11.0 * s, 6.5 * s, bcol + (int(150 * blush),))

        # Mulut senyum manis / lipsync VO penuh!
        talk = st.get("mouth")
        op = talk if talk is not None else ex.get("open", 0.55)
        mk = "open" if talk is not None else ex["mouth"]
        my = eye_y + 24.0
        if mk == "open" and talk is None and op <= 0.68:
            # senyum U membulat manis bersih saat diam (persis referensi otak user, bukan V lancip!)
            c.curve(TT(arc_pts(fx, my - 3, 17, 15, 22, 158, 12)), oc_m, 4.4 * s)
        elif mk in ("open", "grin"):
            mw = 26.0 if mk == "grin" else 22.0
            mh = lerp(11.0, 26.0, clamp(op, 0.2, 1.0))
            pts_m = [(fx - mw, my), (fx, my + 4), (fx + mw, my),
                     (fx + mw * 0.78, my + mh * 0.85), (fx, my + mh), (fx - mw * 0.78, my + mh * 0.85)]
            c.blob(TT(pts_m), oc_m, ow * 0.9, oc_m, n=5)
            c.ell(*T(fx + 2, my + mh * 0.72), mw * 0.48 * s, mh * 0.28 * s, (232, 112, 98))
            if mh > 14:
                c.poly(TT([(fx - mw * 0.68, my + 2), (fx + mw * 0.68, my + 2),
                           (fx + mw * 0.56, my + 8), (fx - mw * 0.56, my + 8)]), (252, 250, 244))
            c.blob(TT(pts_m), None, ow * 0.85, oc_m, n=5)
        elif mk == "smile":
            c.curve(TT([(fx - 18, my + 2), (fx, my + 14), (fx + 18, my + 2)]), oc_m, 4.4 * s)
        elif mk == "smirk":
            c.curve(TT([(fx - 16, my + 6), (fx + 4, my + 10), (fx + 22, my - 3)]), oc_m, 4.2 * s)
        elif mk in ("o", "yawn", "wave_o"):
            c.ell(*T(fx, my + 10), 12 * s, 15 * s, (168, 52, 56), ow * 0.85, oc_m)
            c.ell(*T(fx, my + 17), 6.5 * s, 4.5 * s, (232, 112, 98))
        elif mk in ("frown", "pout"):
            c.curve(TT([(fx - 16, my + 16), (fx, my + 5), (fx + 16, my + 16)]), oc_m, 4.2 * s)
        elif mk == "gigit":
            c.poly(TT([(fx - 22, my), (fx + 22, my), (fx + 22, my + 15), (fx - 22, my + 15)]), (252, 250, 244), ow * 0.8, oc_m)
            for gx in (-10, 0, 10):
                c.line(TT([(fx + gx, my), (fx + gx, my + 15)]), oc_m, 2.2 * s)
        else:
            c.curve(TT([(fx - 15, my + 8), (fx, my + 6), (fx + 15, my + 8)]), oc_m, 3.8 * s)

        if ex.get("tear"):
            for sg in (-1, 1):
                c.ell(*T(fx + sg * 32, eye_y + 26), 5.5 * s, 8.5 * s, (132, 206, 244), ow * 0.5, oc_m)
        if ex.get("sweat"):
            c.blob(TT([(fx + 64, eye_y - 34), (fx + 72, eye_y - 14), (fx + 64, eye_y - 8), (fx + 56, eye_y - 14)]),
                   (142, 212, 246), ow * 0.55, oc_m, n=4)
        if ex.get("vein"):
            vx, vy = fx + 54, eye_y - 46
            c.curve(TT([(vx - 10, vy - 6), (vx - 3, vy - 3), (vx - 6, vy - 12)]), (214, 72, 66), 2.8 * s)
            c.curve(TT([(vx + 10, vy + 6), (vx + 3, vy + 3), (vx + 6, vy + 12)]), (214, 72, 66), 2.8 * s)


def pose_state(name, t=0.0):
    """Nama pose -> dict lengan/kaki/duduk/miring pada waktu t (animasi lambai dsb. ikut t)."""
    d = pose_def(name)
    L, R = list(d["L"]), list(d["R"])
    w = d.get("wave", "")
    if "R" in w:
        R[1] += 24 * math.sin(t * 9.0)
        R[0] += 4 * math.sin(t * 4.5)
    if "L" in w:
        L[1] += 24 * math.sin(t * 9.0 + 1.3)
    return dict(arms={"L": tuple(L), "R": tuple(R)}, legs=d["legs"], sit=d["sit"], lean=d["lean"], tilt=d["tilt"],
                swing=d.get("swing", 1.0))


def blink_at(t, seed=0.0):
    """0..1 kedip: sekali tiap ±3.3 detik."""
    q = (t + seed * 1.7) % 3.3
    return 1.0 - abs(q - 3.22) / 0.08 if 3.14 < q < 3.30 else 0.0


def state(pose="diam", expr="senang", x=0, y=0, s=1.0, flip=1, t=0.0, **over):
    st = dict(x=x, y=y, s=s, flip=flip, expr=expr, look=(0.0, 0.0), blink=0.0, phase=0.0, amp=0.0)
    ps = pose_state(pose, t)
    st.update(ps)
    st.update(over)
    return st
