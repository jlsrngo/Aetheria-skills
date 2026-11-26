# -*- coding: utf-8 -*-
"""
render.py - Renderer Global Terpadu Aetheria (stikman-cerita · paperworld · voxelverse).

Langsung siap pakai setelah `git clone` / `git pull` tanpa perlu instalasi paket apa pun!
Otomatis mendeteksi mesin skill dari `proyek.json` dan menyegarkan PATH `ffmpeg` di Windows.

Contoh pakai:
  python render.py cek
  python render.py baru proyek-saya --gaya paperworld --rasio 9:16 --judul "Judul"
  python render.py qc proyek-saya --draft
  python render.py render proyek-saya --draft
  python render.py proyek-saya --draft               (shorthand: langsung render + audio)
  python render.py proyek-saya --stills auto --draft (shorthand: langsung QC stills)
  python render.py audio proyek-saya --musik none
  python render.py galeri paperworld
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

ENGINES = {
    "stikman-cerita": os.path.join(REPO_ROOT, "stikman-cerita", "scripts"),
    "paperworld": os.path.join(REPO_ROOT, "paperworld", "scripts"),
    "voxelverse": os.path.join(REPO_ROOT, "voxelverse", "scripts"),
}

ENGINE_ALIASES = {
    "stikman-cerita": "stikman-cerita",
    "stikman": "stikman-cerita",
    "stickman": "stikman-cerita",
    "stik": "stikman-cerita",
    "2d": "stikman-cerita",
    "paperworld": "paperworld",
    "paper": "paperworld",
    "pw": "paperworld",
    "kertas": "paperworld",
    "voxelverse": "voxelverse",
    "voxel": "voxelverse",
    "vv": "voxelverse",
    "3d": "voxelverse",
}

PAPER_LATAR = {
    "meja_hp", "kota_jam", "ruang_pintu", "panggung_kertas", "labirin_pintu", "lipat_meja",
    "kamar_kertas", "sekolah_kertas", "kelas_kertas", "taman_kertas", "kafe_kertas",
    "meja", "kota", "kamar_pintu", "panggung", "labirin", "lipat",
}
VOXEL_LATAR = {"studio_kode", "kota_hujan", "atap_kota", "halte"}
STIKMAN_LATAR = {"ruang_otak", "dalam_tubuh", "ruang_tamu", "jalan", "kantin", "lapangan", "rumah", "meja_makan"}


def resolve_engine_name(raw):
    if not raw:
        return None
    return ENGINE_ALIASES.get(str(raw).strip().lower().replace("_", "-"))


def detect_engine(projdir, explicit=None):
    """Deteksi otomatis mesin skill (paperworld / voxelverse / stikman-cerita) dari proyek.json."""
    eng = resolve_engine_name(explicit)
    if eng:
        return eng

    pj_path = os.path.join(projdir, "proyek.json")
    if not os.path.exists(pj_path):
        raise SystemExit(f"[ERROR] proyek.json tidak ditemukan di: {projdir}")

    with open(pj_path, encoding="utf-8") as fp:
        proj = json.load(fp)

    for k in ("mesin", "skill", "gaya", "engine"):
        eng = resolve_engine_name(proj.get(k))
        if eng:
            return eng

    if str(proj.get("gaya_subtitle", "")).lower() == "kertas" or str(proj.get("mood_musik", "")).lower() == "kertas":
        return "paperworld"

    tokoh_keys = {str(k).lower() for k in (proj.get("tokoh") or {}).keys()}
    tokoh_vals = set()
    for v in (proj.get("tokoh") or {}).values():
        if isinstance(v, str):
            tokoh_vals.add(v.lower())
        elif isinstance(v, dict) and v.get("dasar"):
            tokoh_vals.add(str(v["dasar"]).lower())
    all_chars = tokoh_keys | tokoh_vals

    adegan_list = proj.get("adegan") or []
    latars = {str(a.get("latar", "")).lower() for a in adegan_list if isinstance(a, dict)}
    has_3d_cam = any(
        isinstance(a, dict)
        and isinstance((a.get("kamera") or {}).get("awal"), dict)
        and isinstance(a["kamera"]["awal"].get("pos"), list)
        and len(a["kamera"]["awal"]["pos"]) == 3
        for a in adegan_list
    )
    has_voxel_feat = any(
        isinstance(a, dict) and any(k in a for k in ("percikan", "cuaca", "hujan", "salju"))
        for a in adegan_list
    )

    if latars & PAPER_LATAR or "luna" in all_chars:
        return "paperworld"
    if latars & VOXEL_LATAR or has_voxel_feat or (all_chars & {"arka", "robo"}):
        return "voxelverse"
    if latars & STIKMAN_LATAR:
        return "stikman-cerita"
    if has_3d_cam:
        return "paperworld" if ("kucing" in all_chars) else "voxelverse"
    return "stikman-cerita"


def _build_env():
    """Segarkan PATH Windows dari registry agar ffmpeg/ffprobe selalu ditemukan."""
    env = os.environ.copy()
    if os.name == "nt":
        try:
            import winreg
            parts = []
            for root, sub in (
                (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
                (winreg.HKEY_CURRENT_USER, r"Environment"),
            ):
                try:
                    with winreg.OpenKey(root, sub) as k:
                        val, _ = winreg.QueryValueEx(k, "Path")
                        if val:
                            parts.append(val)
                except OSError:
                    pass
            merged = ";".join([env.get("PATH", "")] + parts)
            seen, clean = set(), []
            for p in merged.split(";"):
                p = p.strip()
                if p and p.lower() not in seen:
                    seen.add(p.lower())
                    clean.append(p)
            env["PATH"] = ";".join(clean)
        except Exception:
            pass
    return env


def _run(cmd, env=None):
    print("+", " ".join(cmd), flush=True)
    res = subprocess.run(cmd, env=env or _build_env())
    if res.returncode != 0:
        sys.exit(res.returncode)


def _engine_script(engine, name):
    sdir = ENGINES.get(engine)
    if not sdir or not os.path.isdir(sdir):
        raise SystemExit(f"[ERROR] Mesin '{engine}' tidak ditemukan di {REPO_ROOT}")
    sp = os.path.join(sdir, name)
    if not os.path.exists(sp):
        raise SystemExit(f"[ERROR] Script '{name}' tidak ada untuk mesin '{engine}': {sp}")
    return sp


def cmd_baru(args, extra):
    engine = resolve_engine_name(args.gaya)
    if not engine:
        raise SystemExit(f"[ERROR] Gaya tidak dikenal: '{args.gaya}'. Pilih: paperworld | stikman-cerita | voxelverse")
    projdir = os.path.abspath(args.proyek)
    script = _engine_script(engine, "proyek_baru.py")
    _run([sys.executable, script, projdir] + extra)

    pj_path = os.path.join(projdir, "proyek.json")
    if os.path.exists(pj_path):
        with open(pj_path, encoding="utf-8") as fp:
            data = json.load(fp)
        ordered = {"mesin": engine}
        for k, v in data.items():
            if k != "mesin":
                ordered[k] = v
        with open(pj_path, "w", encoding="utf-8") as fp:
            json.dump(ordered, fp, indent=2, ensure_ascii=False)
            fp.write("\n")
    print(f"[OK] Proyek '{engine}' siap di: {projdir}")


def cmd_qc(args, extra):
    projdir = os.path.abspath(args.proyek)
    engine = detect_engine(projdir, args.gaya)
    print(f"[RENDER GLOBAL] QC ({engine}) -> {projdir}", flush=True)
    script = _engine_script(engine, "render.py")
    cmd = [sys.executable, script, projdir]
    if args.strip is not None:
        cmd += ["--strip", str(args.strip)]
    else:
        cmd += ["--stills", args.stills or "auto"]
    if args.draft:
        cmd.append("--draft")
    _run(cmd + extra)


def cmd_render(args, extra):
    env = _build_env()
    for p in args.proyek:
        projdir = os.path.abspath(p)
        engine = detect_engine(projdir, args.gaya)
        print(f"[RENDER GLOBAL] RENDER ({engine}) -> {projdir}", flush=True)
        r_script = _engine_script(engine, "render.py")
        cmd = [sys.executable, r_script, projdir]
        if args.draft:
            cmd.append("--draft")
        if args.ulang:
            cmd.append("--ulang")
        if args.jobs:
            cmd += ["--jobs", str(args.jobs)]
        if args.anggaran:
            cmd += ["--anggaran", str(args.anggaran)]
        _run(cmd, env=env)
        if not args.tanpa_audio:
            a_script = _engine_script(engine, "audio.py")
            a_cmd = [sys.executable, a_script, projdir]
            if args.musik:
                a_cmd += ["--musik", args.musik]
            if args.tanpa_sfx:
                a_cmd.append("--tanpa-sfx")
            _run(a_cmd + extra, env=env)


def cmd_audio(args, extra):
    projdir = os.path.abspath(args.proyek)
    engine = detect_engine(projdir, args.gaya)
    print(f"[RENDER GLOBAL] AUDIO ({engine}) -> {projdir}", flush=True)
    a_script = _engine_script(engine, "audio.py")
    _run([sys.executable, a_script, projdir] + extra)


def cmd_galeri(args, extra):
    engine = resolve_engine_name(args.gaya)
    if not engine:
        raise SystemExit(f"[ERROR] Gaya tidak dikenal: '{args.gaya}'. Pilih: paperworld | stikman-cerita | voxelverse")
    g_script = _engine_script(engine, "galeri.py")
    cmd = [sys.executable, g_script]
    if args.output:
        cmd.append(os.path.abspath(args.output))
    _run(cmd + extra)


def cmd_cek(_args, _extra):
    env = _build_env()
    print(f"Repo Aetheria : {REPO_ROOT}")
    print(f"Python        : {sys.version.split()[0]} ({sys.executable})")
    for pkg in ("numpy", "PIL"):
        try:
            m = __import__(pkg)
            print(f"  - {pkg:8s}  : OK ({getattr(m, '__version__', '?')})")
        except ImportError:
            print(f"  - {pkg:8s}  : BELUM TERPASANG")
    for tool in ("ffmpeg", "ffprobe"):
        path = shutil.which(tool, path=env.get("PATH"))
        print(f"  - {tool:8s}  : {'OK (' + path + ')' if path else 'BELUM TERPASANG'}")
    print("Skill tersedia (otomatis aktif via .agents/skills.json):")
    for name, sdir in ENGINES.items():
        skill_md = os.path.join(os.path.dirname(sdir), "SKILL.md")
        ok = os.path.exists(skill_md) and os.path.exists(os.path.join(sdir, "render.py"))
        print(f"  - /{name:15s} : {'SIAP' if ok else 'TIDAK LENGKAP'}")


def main(argv=None):
    raw = list(sys.argv[1:] if argv is None else argv)
    known = {"baru", "qc", "render", "audio", "galeri", "cek", "-h", "--help"}
    # Shorthand: `python render.py <folder-proyek> [--stills auto] [--draft]`
    if raw and raw[0] not in known and not raw[0].startswith("-"):
        if "--stills" in raw or "--strip" in raw:
            raw = ["qc"] + raw
        else:
            raw = ["render"] + raw

    ap = argparse.ArgumentParser(
        prog="python render.py",
        description="Renderer Global Aetheria (stikman-cerita · paperworld · voxelverse)",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_baru = sub.add_parser("baru", help="Buat folder proyek baru untuk gaya tertentu")
    p_baru.add_argument("proyek", help="Nama/path folder proyek baru")
    p_baru.add_argument("--gaya", "--mesin", dest="gaya", required=True, help="paperworld | stikman-cerita | voxelverse")
    p_baru.set_defaults(func=cmd_baru)

    p_qc = sub.add_parser("qc", help="Render stills/strip QC (deteksi mesin otomatis)")
    p_qc.add_argument("proyek", help="Folder proyek berisi proyek.json")
    p_qc.add_argument("--stills", default="auto", help="auto atau daftar detik misal 0.5,3.2,8.4")
    p_qc.add_argument("--strip", type=int, default=None, help="Nomor adegan (1-based) untuk 9-panel strip")
    p_qc.add_argument("--draft", action="store_true", help="Resolusi cepat")
    p_qc.add_argument("--gaya", "--mesin", dest="gaya", default=None, help="Paksa mesin tertentu (opsional)")
    p_qc.set_defaults(func=cmd_qc)

    p_ren = sub.add_parser("render", help="Render video + mix audio sampai MP4 final")
    p_ren.add_argument("proyek", nargs="+", help="Satu atau lebih folder proyek berisi proyek.json")
    p_ren.add_argument("--draft", action="store_true", help="Mode render cepat")
    p_ren.add_argument("--ulang", action="store_true", help="Render ulang dari awal")
    p_ren.add_argument("--jobs", type=int, default=0, help="Jumlah proses paralel")
    p_ren.add_argument("--anggaran", type=int, default=0, help="Batas detik per sesi render")
    p_ren.add_argument("--musik", default=None, help="Override musik (path file atau 'none')")
    p_ren.add_argument("--tanpa-sfx", action="store_true", help="Matikan SFX otomatis")
    p_ren.add_argument("--tanpa-audio", action="store_true", help="Hanya render video_bisu.mp4 tanpa audio.py")
    p_ren.add_argument("--gaya", "--mesin", dest="gaya", default=None, help="Paksa mesin tertentu (opsional)")
    p_ren.set_defaults(func=cmd_render)

    p_aud = sub.add_parser("audio", help="Mix ulang audio (VO + musik + SFX) tanpa render ulang video")
    p_aud.add_argument("proyek", help="Folder proyek")
    p_aud.add_argument("--gaya", "--mesin", dest="gaya", default=None, help="Paksa mesin tertentu (opsional)")
    p_aud.set_defaults(func=cmd_audio)

    p_gal = sub.add_parser("galeri", help="Render galeri karakter untuk gaya tertentu")
    p_gal.add_argument("gaya", help="paperworld | stikman-cerita | voxelverse")
    p_gal.add_argument("output", nargs="?", default=None, help="Path file PNG keluaran (opsional)")
    p_gal.set_defaults(func=cmd_galeri)

    p_cek = sub.add_parser("cek", help="Periksa Python, NumPy, Pillow, ffmpeg, dan status skill")
    p_cek.set_defaults(func=cmd_cek)

    args, extra = ap.parse_known_args(raw)
    args.func(args, extra)


if __name__ == "__main__":
    main()
