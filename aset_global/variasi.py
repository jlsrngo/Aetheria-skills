# -*- coding: utf-8 -*-
"""
aset_global/variasi.py
Mesin Variasi Sutradara & Anti-Monoton GLOBAL untuk seluruh 7 skill visual Aetheria.

Tujuan:
  - Membuat Video 1 dan Video 2 otomatis terasa BERBEDA (profil sutradara, urutan transisi,
    sudut & gerak kamera, serta ritme gerak karakter) meski memakai struktur adegan serupa.
  - Tetap 100% DETERMINISTIK per proyek (render ulang proyek yang sama = hasil sama persis).
  - Bisa dikontrol manual lewat field opsional di `proyek.json`:
      "seed": 12345                 # opsional; default otomatis dari hash judul + narasi
      "gaya_sutradara": "auto"      # atau: dinamis_film | dokumenter_halus | komik_enerjik |
                                    #       misteri_tegang | hangat_ghibli | retro_kreatif
"""
import hashlib
import random


OUTDOOR_HINTS = (
    "jalan", "taman", "halaman", "lapangan", "jembatan", "atap", "halte",
    "hutan", "sawah", "kota", "pantai", "warung", "kampus", "stasiun",
)

PROFIL_SUTRADARA = {
    "dinamis_film": {
        "gaya_kamera": "handheld",
        "gerak_aktor": "ekspresif",
        "same_interval": 2,
        "same_pool": [
            {"jenis": "whip", "arah": "kiri", "dur": 0.30},
            {"jenis": "blur_cross", "dur": 0.36},
            {"jenis": "zoom", "dur": 0.38},
        ],
        "timelapse_pool": [
            {"jenis": "luma", "pola": "radial", "dur": 0.62},
            {"jenis": "fade_hitam", "dur": 0.58},
            {"jenis": "blur_cross", "dur": 0.55},
        ],
        "outdoor_pool": [
            {"jenis": "wipe_tiang", "arah": "kiri", "dur": 0.52},
            {"jenis": "whip", "arah": "kanan", "dur": 0.36},
            {"jenis": "wipe_diagonal", "arah": "kanan_bawah", "dur": 0.48},
            {"jenis": "zoom", "dur": 0.45},
            {"jenis": "luma", "pola": "horizontal", "dur": 0.55},
        ],
        "indoor_pool": [
            {"jenis": "wipe_tiang", "arah": "kanan", "dur": 0.48},
            {"jenis": "blur_cross", "dur": 0.46},
            {"jenis": "belah", "arah": "horizontal", "dur": 0.48},
            {"jenis": "luma", "pola": "horizontal", "dur": 0.52},
            {"jenis": "iris", "dur": 0.50},
        ],
        "cam_moves": ("push", "orbit", "crane", "truck", "spiral"),
        "angles": ("normal", "bawah", "atas", "normal", "rendah"),
        "sudut_pool": (-22, 18, -14, 26, -28, 12),
    },
    "dokumenter_halus": {
        "gaya_kamera": "halus",
        "gerak_aktor": "aktif",
        "same_interval": 3,
        "same_pool": [
            {"jenis": "blur_cross", "dur": 0.42},
            {"jenis": "fade", "dur": 0.40},
        ],
        "timelapse_pool": [
            {"jenis": "fade", "dur": 0.65},
            {"jenis": "luma", "pola": "radial", "dur": 0.65},
            {"jenis": "blur_cross", "dur": 0.60},
        ],
        "outdoor_pool": [
            {"jenis": "fade", "dur": 0.50},
            {"jenis": "geser", "arah": "kiri", "dur": 0.52},
            {"jenis": "wipe", "arah": "kanan", "dur": 0.50},
            {"jenis": "blur_cross", "dur": 0.50},
            {"jenis": "zoom_out", "dur": 0.52},
        ],
        "indoor_pool": [
            {"jenis": "fade", "dur": 0.48},
            {"jenis": "iris", "dur": 0.54},
            {"jenis": "tirai", "arah": "horizontal", "dur": 0.52},
            {"jenis": "blur_cross", "dur": 0.48},
            {"jenis": "halaman", "arah": "kiri", "dur": 0.55},
        ],
        "cam_moves": ("push", "pull", "orbit", "pan", "truck"),
        "angles": ("normal", "normal", "atas", "bawah"),
        "sudut_pool": (-12, 14, -18, 10, 20, -8),
    },
    "komik_enerjik": {
        "gaya_kamera": "handheld",
        "gerak_aktor": "ekspresif",
        "same_interval": 2,
        "same_pool": [
            {"jenis": "whip", "arah": "kanan", "dur": 0.28},
            {"jenis": "flash", "dur": 0.28},
            {"jenis": "zoom", "dur": 0.34},
        ],
        "timelapse_pool": [
            {"jenis": "cahaya", "dur": 0.52},
            {"jenis": "kedip", "dur": 0.45},
            {"jenis": "luma", "pola": "radial", "dur": 0.55},
        ],
        "outdoor_pool": [
            {"jenis": "wipe_diagonal", "arah": "kanan_bawah", "dur": 0.44},
            {"jenis": "whip", "arah": "kiri", "dur": 0.32},
            {"jenis": "belah", "arah": "horizontal", "dur": 0.44},
            {"jenis": "putar", "arah": "kanan", "dur": 0.44},
            {"jenis": "zoom", "dur": 0.40},
        ],
        "indoor_pool": [
            {"jenis": "halaman", "arah": "kiri", "dur": 0.50},
            {"jenis": "iris", "dur": 0.46},
            {"jenis": "wipe_diagonal", "arah": "kiri_bawah", "dur": 0.44},
            {"jenis": "belah", "arah": "vertikal", "dur": 0.46},
            {"jenis": "flash", "dur": 0.32},
        ],
        "cam_moves": ("punch_in", "orbit", "push", "hentak", "truck"),
        "angles": ("bawah", "normal", "atas", "dutch", "normal"),
        "sudut_pool": (20, -24, 15, -16, 28, -20),
    },
    "misteri_tegang": {
        "gaya_kamera": "tegang",
        "gerak_aktor": "aktif",
        "same_interval": 3,
        "same_pool": [
            {"jenis": "kedip", "dur": 0.38},
            {"jenis": "blur_cross", "dur": 0.45},
            {"jenis": "glitch", "dur": 0.32},
        ],
        "timelapse_pool": [
            {"jenis": "fade_hitam", "dur": 0.70},
            {"jenis": "kedip", "dur": 0.55},
            {"jenis": "blur_cross", "dur": 0.65},
        ],
        "outdoor_pool": [
            {"jenis": "fade_hitam", "dur": 0.58},
            {"jenis": "wipe_tiang", "arah": "kiri", "dur": 0.56},
            {"jenis": "glitch", "dur": 0.36},
            {"jenis": "blur_cross", "dur": 0.55},
            {"jenis": "kedip", "dur": 0.50},
        ],
        "indoor_pool": [
            {"jenis": "fade_hitam", "dur": 0.55},
            {"jenis": "kedip", "dur": 0.48},
            {"jenis": "iris", "keluar": True, "dur": 0.60},
            {"jenis": "glitch", "dur": 0.36},
            {"jenis": "blur_cross", "dur": 0.52},
        ],
        "cam_moves": ("push", "dolly_zoom", "orbit", "pull", "crane"),
        "angles": ("bawah", "dutch", "rendah", "dutch_kiri", "atas"),
        "sudut_pool": (-18, 16, -26, 22, -10, 24),
    },
    "hangat_ghibli": {
        "gaya_kamera": "napas_film",
        "gerak_aktor": "aktif",
        "same_interval": 3,
        "same_pool": [
            {"jenis": "fade", "dur": 0.48},
            {"jenis": "blur_cross", "dur": 0.46},
        ],
        "timelapse_pool": [
            {"jenis": "luma", "pola": "radial", "dur": 0.72},
            {"jenis": "cahaya", "dur": 0.68},
            {"jenis": "fade", "dur": 0.70},
        ],
        "outdoor_pool": [
            {"jenis": "luma", "pola": "horizontal", "dur": 0.62},
            {"jenis": "wipe_tiang", "arah": "kanan", "dur": 0.58},
            {"jenis": "cahaya", "dur": 0.58},
            {"jenis": "fade", "dur": 0.58},
            {"jenis": "geser", "arah": "kanan", "dur": 0.56},
        ],
        "indoor_pool": [
            {"jenis": "halaman", "arah": "kiri", "dur": 0.60},
            {"jenis": "luma", "pola": "radial", "dur": 0.60},
            {"jenis": "tirai", "arah": "vertikal", "dur": 0.56},
            {"jenis": "iris", "dur": 0.58},
            {"jenis": "fade", "dur": 0.55},
        ],
        "cam_moves": ("crane", "orbit", "pull", "push", "pan"),
        "angles": ("normal", "atas", "normal", "bawah"),
        "sudut_pool": (-16, 12, -22, 18, -10, 14),
    },
    "retro_kreatif": {
        "gaya_kamera": "halus",
        "gerak_aktor": "ekspresif",
        "same_interval": 2,
        "same_pool": [
            {"jenis": "glitch", "dur": 0.30},
            {"jenis": "kotak", "dur": 0.38},
            {"jenis": "putar", "arah": "kiri", "dur": 0.38},
        ],
        "timelapse_pool": [
            {"jenis": "kotak", "dur": 0.52},
            {"jenis": "glitch", "dur": 0.42},
            {"jenis": "luma", "pola": "radial", "dur": 0.58},
        ],
        "outdoor_pool": [
            {"jenis": "glitch", "dur": 0.38},
            {"jenis": "kotak", "dur": 0.46},
            {"jenis": "putar", "arah": "kanan", "dur": 0.46},
            {"jenis": "wipe_diagonal", "arah": "kiri_bawah", "dur": 0.46},
            {"jenis": "zoom_out", "dur": 0.46},
        ],
        "indoor_pool": [
            {"jenis": "belah", "arah": "vertikal", "dur": 0.46},
            {"jenis": "kotak", "dur": 0.46},
            {"jenis": "tirai", "jumlah": 6, "dur": 0.48},
            {"jenis": "glitch", "dur": 0.36},
            {"jenis": "putar", "arah": "kiri", "dur": 0.46},
        ],
        "cam_moves": ("spiral", "truck", "orbit", "dolly_zoom", "push"),
        "angles": ("bawah", "atas", "dutch_kiri", "normal", "rendah"),
        "sudut_pool": (24, -20, 16, -28, 12, -14),
    },
}

_MOOD_PREFER = {
    "misteri": ("misteri_tegang", "dinamis_film"),
    "tegang": ("misteri_tegang", "dinamis_film"),
    "malam": ("misteri_tegang", "retro_kreatif"),
    "sinematik": ("dinamis_film", "hangat_ghibli"),
    "ceria": ("komik_enerjik", "hangat_ghibli"),
    "lucu": ("komik_enerjik", "retro_kreatif"),
    "semangat": ("komik_enerjik", "dinamis_film"),
    "hangat": ("hangat_ghibli", "dokumenter_halus"),
    "santai": ("hangat_ghibli", "dokumenter_halus"),
    "lofi": ("hangat_ghibli", "retro_kreatif"),
    "sedih": ("dokumenter_halus", "hangat_ghibli"),
    "kertas": ("hangat_ghibli", "komik_enerjik"),
}


def project_seed(proj):
    """Hitung integer seed deterministik unik per video dari proyek.json."""
    if not isinstance(proj, dict):
        return 104729
    if proj.get("seed") is not None:
        raw = str(proj["seed"])
        return int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8], 16)
    ad = proj.get("adegan") or []
    first_nar = str(ad[0].get("narasi", ""))[:80] if ad and isinstance(ad[0], dict) else ""
    last_lat = str(ad[-1].get("latar", "")) if ad and isinstance(ad[-1], dict) else ""
    sig = "|".join([
        str(proj.get("judul", "")),
        str(proj.get("mesin", "")),
        str(proj.get("mood_musik", "")),
        str(len(ad)),
        first_nar,
        last_lat,
    ])
    return int(hashlib.sha256(sig.encode("utf-8")).hexdigest()[:8], 16)


def pilih_profil_sutradara(proj):
    """Pilih nama profil sutradara (eksplisit via `gaya_sutradara` atau otomatis unik per video)."""
    if isinstance(proj, dict):
        req = str(proj.get("gaya_sutradara", "")).strip().lower().replace("-", "_")
        if req in PROFIL_SUTRADARA:
            return req
    sd = project_seed(proj)
    mood = str((proj or {}).get("mood_musik", "")).strip().lower()
    all_names = list(PROFIL_SUTRADARA.keys())
    if mood in _MOOD_PREFER:
        # 65% pakai profil selaras mood, 35% lintas profil agar video bermood sama tetap variatif
        rng = random.Random(sd ^ 0x5A3C9)
        if rng.random() < 0.65:
            return rng.choice(_MOOD_PREFER[mood])
    return all_names[sd % len(all_names)]


def seed_aktor(proj_seed, actor_id, scene_idx=0):
    """Hasilkan float seed unik untuk fase napas/idle aktor per video & per adegan."""
    raw = f"{int(proj_seed)}|{actor_id}|{int(scene_idx)}"
    h = int(hashlib.sha256(raw.encode("utf-8")).hexdigest()[:6], 16)
    return (h % 970) / 100.0


def _pick_no_repeat(pool, rng, prev_jenis=None):
    if not pool:
        return {"jenis": "fade", "dur": 0.45}
    cands = [dict(x) for x in pool if x.get("jenis") != prev_jenis] or [dict(x) for x in pool]
    chosen = dict(rng.choice(cands))
    # Variasikan arah sedikit secara deterministik agar tidak selalu dari kiri terus
    if "arah" in chosen and chosen["arah"] in ("kiri", "kanan") and rng.random() < 0.5:
        chosen["arah"] = "kanan" if chosen["arah"] == "kiri" else "kiri"
    elif "arah" in chosen and chosen["arah"] in ("kanan_bawah", "kiri_bawah") and rng.random() < 0.5:
        chosen["arah"] = "kiri_bawah" if chosen["arah"] == "kanan_bawah" else "kanan_bawah"
    return chosen


def pilih_transisi_cerdas(prev_spec, cur_spec, idx, proj=None, prev_jenis=None):
    """
    Pilih transisi kontekstual otomatis yang:
      1. Beda antara Video 1 dan Video 2 (berbasis project_seed + profil sutradara),
      2. Tetap cocok dengan konteks adegan (komik, time-lapse, dialog, pindah outdoor/indoor),
      3. Tidak mengulang transisi non-potong yang sama 2x berturut-turut.
    """
    sd = project_seed(proj)
    prof_name = pilih_profil_sutradara(proj)
    prof = PROFIL_SUTRADARA[prof_name]
    rng = random.Random((sd ^ (idx * 2654435761)) & 0xFFFFFFFF)

    prev_s = prev_spec or {}
    cur_s = cur_spec or {}
    lat_a = str(prev_s.get("latar", "")).lower()
    lat_b = str(cur_s.get("latar", "")).lower()
    wak_a = str(prev_s.get("waktu", "siang")).lower()
    wak_b = str(cur_s.get("waktu", "siang")).lower()

    if cur_s.get("tipe") == "komik" or prev_s.get("tipe") == "komik":
        return {"jenis": "halaman", "arah": "kiri" if idx % 2 else "kanan", "dur": 0.56}

    if lat_a and lat_a == lat_b and wak_a != wak_b:
        return _pick_no_repeat(prof["timelapse_pool"], rng, prev_jenis)

    if lat_a and lat_a == lat_b and wak_a == wak_b:
        interval = max(2, int(prof.get("same_interval", 3)))
        offset = sd % interval
        if (idx + offset) % interval == 0:
            return _pick_no_repeat(prof["same_pool"], rng, prev_jenis)
        return {"jenis": "potong", "dur": 0.0}

    is_outdoor = any(h in lat_b or h in lat_a for h in OUTDOOR_HINTS)
    pool = prof["outdoor_pool"] if is_outdoor else prof["indoor_pool"]
    return _pick_no_repeat(pool, rng, prev_jenis)


def variasi_kamera_3d(cam_spec, dur, idx, proj=None, actor_ids=None):
    """
    Beri variasi kamera sinematik otomatis untuk adegan 3D jika `kamera` belum punya
    `shot` maupun `gerak` (atau jika `kamera == "auto"` / `kamera.auto == True`).
    Jika user sudah mengisi `shot` atau `gerak`, spec user dihormati 100% tanpa ditimpa!
    """
    if isinstance(cam_spec, str) and cam_spec.strip().lower() == "auto":
        cam = {"auto": True}
    elif isinstance(cam_spec, dict):
        cam = dict(cam_spec)
    else:
        cam = {}

    if cam.get("shot") or cam.get("shots") or cam.get("gerak"):
        # User sudah merancang kamera manual -> cukup isi gaya default dari profil bila belum ada
        if "gaya" not in cam:
            prof = PROFIL_SUTRADARA[pilih_profil_sutradara(proj)]
            cam["gaya"] = prof["gaya_kamera"]
        return cam

    # Kalau user juga tidak punya "akhir" (cutaway), buat variasi kamera unik per video & per adegan!
    if "akhir" in cam and not cam.get("auto"):
        return cam

    sd = project_seed(proj)
    prof_name = pilih_profil_sutradara(proj)
    prof = PROFIL_SUTRADARA[prof_name]
    rng = random.Random((sd ^ ((idx + 1) * 1597334677)) & 0xFFFFFFFF)
    actors = list(actor_ids or [])

    cam.setdefault("gaya", prof["gaya_kamera"])
    awal = dict(cam.get("awal") or {})
    if "sudut" not in awal and "pos" not in awal:
        awal["sudut"] = rng.choice(prof["sudut_pool"])
    if "angle" not in awal and "pos" not in awal:
        awal["angle"] = rng.choice(prof["angles"])
    if "geser_x" not in awal and "pos" not in awal:
        awal["geser_x"] = round(rng.choice((-0.16, -0.10, 0.0, 0.10, 0.16)), 2)
    if "ukuran" not in awal and "pos" not in awal:
        awal["ukuran"] = rng.choice(("penuh", "lebar", "sedang"))
    cam["awal"] = awal

    # Jika adegan panjang (>= 4.8s) dan ada >= 2 aktor & tidak mengunci `pos`, buat 2-shot otomatis!
    if dur >= 4.8 and len(actors) >= 2 and "pos" not in awal and cam.get("auto", True):
        t_cut = round(dur * rng.uniform(0.42, 0.56), 2)
        mv1 = rng.choice(("push", "orbit", "crane"))
        mv2 = rng.choice(("push", "orbit", "pull"))
        g1 = {"jenis": mv1, "dur": max(0.8, t_cut - 0.1)}
        if mv1 == "orbit":
            g1["derajat"] = rng.choice((-20, -14, 14, 20))
        elif mv1 == "crane":
            g1["naik"] = rng.choice((-0.45, 0.45))
            g1["maju"] = -0.35
        else:
            g1["faktor"] = 0.86
            g1["zoom"] = 4

        a0, a1 = actors[0], actors[1]
        if rng.random() < 0.5:
            a0, a1 = a1, a0
        shot2 = {
            "t": t_cut,
            "bahu": a0,
            "fokus": a1,
            "sisi_bahu": rng.choice((-1.12, 1.12)),
            "geser_x": rng.choice((-0.14, 0.14)),
            "gerak": {"jenis": mv2, "faktor": 0.88 if mv2 == "push" else 1.14, "derajat": rng.choice((-16, 16))},
        }
        cam["shot"] = [
            dict(awal, t=0.0, gerak=g1),
            shot2,
        ]
        return cam

    # Single-shot bervariasi dengan gerak dinamis dari profil sutradara
    mv = rng.choice(prof["cam_moves"])
    g = {"t": 0.2, "dur": max(0.6, dur - 0.35), "jenis": mv}
    if mv == "orbit":
        g["derajat"] = rng.choice((-26, -18, 18, 26))
    elif mv == "spiral":
        g["derajat"] = rng.choice((-38, 38))
        g["faktor"] = 0.84
        g["naik"] = 0.35
    elif mv == "crane":
        g["naik"] = rng.choice((-0.55, 0.55))
        g["maju"] = rng.choice((-0.4, 0.35))
    elif mv == "truck":
        g["x"] = rng.choice((-0.9, 0.9))
    elif mv == "pan":
        g["derajat"] = rng.choice((-18, 18))
    elif mv == "dolly_zoom":
        g["faktor"] = rng.choice((1.35, 0.78))
    elif mv == "punch_in":
        g["t"] = round(dur * 0.35, 2)
        g["dur"] = 0.24
        g["faktor"] = 0.76
    elif mv == "hentak":
        g["t"] = round(dur * 0.4, 2)
        g["dur"] = 0.28
        g["kuat"] = 0.14
    elif mv == "pull":
        g["faktor"] = 1.22
        g["zoom"] = -5
    else:  # push
        g["faktor"] = 0.82
        g["zoom"] = 6
    cam["gerak"] = [g]
    return cam


def variasi_kamera_2d(cam_spec, dur, idx, proj=None):
    """Variasi gerak kamera 2D otomatis untuk `stikman-cerita` jika `kamera.gerak` kosong."""
    cam = dict(cam_spec) if isinstance(cam_spec, dict) else {}
    if cam.get("gerak"):
        return cam
    sd = project_seed(proj)
    rng = random.Random((sd ^ ((idx + 1) * 2246822519)) & 0xFFFFFFFF)
    awal = dict(cam.get("awal") or {"ukuran": "lebar"})
    cam["awal"] = awal
    mode = rng.choice(("mendekat", "menjauh", "geser_kiri", "geser_kanan", "punch_dan_tahan"))
    if mode == "mendekat":
        cam["gerak"] = [{"t": 0.15, "dur": max(0.8, dur - 0.3), "jenis": "mendekat", "kali": round(rng.uniform(1.12, 1.24), 2)}]
    elif mode == "menjauh":
        cam["gerak"] = [{"t": 0.15, "dur": max(0.8, dur - 0.3), "jenis": "menjauh", "kali": round(rng.uniform(1.10, 1.22), 2)}]
    elif mode == "geser_kiri":
        cam["gerak"] = [{"t": 0.15, "dur": max(0.8, dur - 0.3), "jenis": "geser", "dx": -rng.randint(45, 95)}]
    elif mode == "geser_kanan":
        cam["gerak"] = [{"t": 0.15, "dur": max(0.8, dur - 0.3), "jenis": "geser", "dx": rng.randint(45, 95)}]
    else:
        cam["gerak"] = [
            {"t": round(dur * 0.32, 2), "dur": 0.25, "jenis": "mendekat", "kali": 1.16},
        ]
    return cam


def variasi_aksi_aktor_3d(spec, dur, idx, proj=None, valid_poses=None):
    """
    Berikan koreografi hidup otomatis (anti-pasif) untuk aktor 3D jika di proyek.json
    aktor tersebut belum diberi `aksi`/`masuk`/`keluar`/`jalur`/`mondar_mandir`
    dan tidak diset `gerak: "kaku"` atau pose duduk/tidur.
    Hasilnya unik antar Video 1 vs Video 2 (deterministik via project_seed).
    """
    if not isinstance(spec, dict) or dur < 2.2:
        return []
    if str(spec.get("gerak", "")).lower() == "kaku":
        return []
    if any(spec.get(k) for k in ("aksi", "masuk", "keluar", "jalur", "mondar_mandir")):
        return []
    pose0 = str(spec.get("pose", "diam")).lower()
    if pose0.startswith("duduk") or pose0 in ("tidur", "membungkuk"):
        return []
    if pose0 not in ("diam", "santai", ""):
        return []

    sd = project_seed(proj)
    aid = str(spec.get("id") or spec.get("dasar") or "aktor")
    rng = random.Random((sd ^ hash(aid) ^ ((idx + 1) * 7919)) & 0xFFFFFFFF)
    # Gunakan sha256 agar 100% stabil lintas proses Python (tidak terpengaruh PYTHONHASHSEED)
    aid_h = int(hashlib.sha256(f"{sd}|{aid}|{idx}".encode("utf-8")).hexdigest()[:8], 16)
    rng = random.Random(aid_h)

    if "pos" in spec:
        x0, y0, z0 = [float(v) for v in spec["pos"]]
    else:
        x0 = float(spec.get("x", 0.0))
        y0 = float(spec.get("y", 0.0))
        z0 = float(spec.get("z", 0.0))

    hadap0 = spec.get("hadap", "depan")
    all_gestures = ["santai", "mikir", "mengamati", "bicara_aktif", "tunjuk", "angguk", "pinggang", "menoleh", "dagu"]
    if valid_poses is not None:
        pool_p = [p for p in all_gestures if p in valid_poses] or ["santai", "mikir", "tunjuk"]
    else:
        pool_p = all_gestures
    walk_style = "jalan_santai" if (valid_poses is None or "jalan_santai" in valid_poses) else "jalan"

    acts = []
    mode = rng.choice(("langkah_dan_pose", "dua_pose_hadap", "langkah_balik"))
    t1 = round(dur * rng.uniform(0.18, 0.30), 2)
    t2 = round(dur * rng.uniform(0.56, 0.72), 2)

    if mode == "langkah_dan_pose":
        dx = rng.choice((-0.42, -0.32, 0.32, 0.42))
        dz = rng.choice((-0.14, 0.0, 0.16))
        acts.append({
            "t": t1,
            "ke_pos": [round(x0 + dx, 2), round(y0, 2), round(z0 + dz, 2)],
            "durasi": round(rng.uniform(1.1, 1.7), 2),
            "gaya": walk_style,
            "hadap_akhir": hadap0 if hadap0 != "depan" else rng.choice(("serong_kanan", "serong_kiri", "depan")),
            "pose": rng.choice(pool_p),
        })
        if dur >= 4.5:
            acts.append({
                "t": t2,
                "pose": rng.choice(pool_p),
                "hadap": rng.choice(("depan", "serong_kanan", "serong_kiri")) if hadap0 != "belakang" else "belakang",
                "durasi_putar": 0.65,
            })
    elif mode == "langkah_balik":
        dx = rng.choice((-0.36, 0.36))
        acts.append({
            "t": t1,
            "ke_pos": [round(x0 + dx, 2), round(y0, 2), round(z0 + 0.10, 2)],
            "durasi": round(rng.uniform(1.0, 1.5), 2),
            "gaya": walk_style,
            "hadap_akhir": hadap0,
            "pose": rng.choice(pool_p),
        })
        if dur >= 4.2:
            acts.append({
                "t": t2,
                "ke_pos": [round(x0, 2), round(y0, 2), round(z0, 2)],
                "durasi": round(rng.uniform(1.0, 1.4), 2),
                "gaya": walk_style,
                "hadap_akhir": hadap0,
                "pose": rng.choice(pool_p),
            })
    else:
        p1 = rng.choice(pool_p)
        p2 = rng.choice([p for p in pool_p if p != p1] or pool_p)
        acts.append({
            "t": t1,
            "pose": p1,
            "hadap": rng.choice(("serong_kanan", "serong_kiri")) if hadap0 == "depan" else hadap0,
            "durasi_putar": 0.6,
        })
        if dur >= 3.8:
            acts.append({
                "t": t2,
                "pose": p2,
                "hadap": hadap0,
                "durasi_putar": 0.6,
            })
    return acts


def variasi_aksi_aktor_2d(spec, dur, idx, proj=None):
    """
    Berikan koreografi hidup otomatis (anti-pasif) untuk aktor 2D `stikman-cerita`
    jika belum punya `aksi`/`masuk`/`keluar` dan pose-nya pasif (`diam`/`santai`).
    """
    if not isinstance(spec, dict) or dur < 2.2:
        return []
    if str(spec.get("gerak", "")).lower() == "kaku":
        return []
    if any(spec.get(k) for k in ("aksi", "masuk", "keluar")):
        return []
    pose0 = str(spec.get("pose", "diam")).lower()
    if pose0.startswith("duduk") or pose0 in ("tidur", "rebah"):
        return []
    if pose0 not in ("diam", "santai", ""):
        return []

    sd = project_seed(proj)
    aid = str(spec.get("id") or spec.get("dasar") or "aktor")
    aid_h = int(hashlib.sha256(f"{sd}|{aid}|{idx}|2d".encode("utf-8")).hexdigest()[:8], 16)
    rng = random.Random(aid_h)

    x0 = float(spec.get("x", 0.0))
    hadap0 = spec.get("hadap", "depan")
    pool_p = ("santai", "mikir", "tunjuk", "pinggang", "dagu", "semangat", "lambai")
    mode = rng.choice(("langkah_pendek", "gestur_3_4"))
    t1 = round(dur * rng.uniform(0.18, 0.30), 2)
    t2 = round(dur * rng.uniform(0.56, 0.72), 2)

    acts = []
    if mode == "langkah_pendek":
        dx = rng.choice((-120, -85, 85, 120))
        acts.append({
            "t": t1,
            "ke_x": round(x0 + dx, 1),
            "durasi": round(rng.uniform(0.95, 1.45), 2),
            "gaya": "jalan",
            "hadap_akhir": hadap0 if hadap0 != "depan" else rng.choice(("kanan", "kiri", "depan")),
            "pose": rng.choice(pool_p),
        })
        if dur >= 4.2:
            acts.append({
                "t": t2,
                "pose": rng.choice(pool_p),
                "hadap": hadap0 if hadap0 != "depan" else rng.choice(("kanan", "kiri")),
            })
    else:
        p1 = rng.choice(pool_p)
        p2 = rng.choice([p for p in pool_p if p != p1])
        acts.append({
            "t": t1,
            "pose": p1,
            "hadap": rng.choice(("kanan", "kiri")) if hadap0 == "depan" else hadap0,
        })
        if dur >= 3.6:
            acts.append({
                "t": t2,
                "pose": p2,
                "hadap": hadap0,
            })
    return acts

