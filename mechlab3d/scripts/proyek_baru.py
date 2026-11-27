import argparse, os, sys
_R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _R not in sys.path: sys.path.insert(0, _R)
from aset_global.cutaway_runner import make_new_project
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("proyek")
    ap.add_argument("--rasio", default="9:16")
    ap.add_argument("--judul", default="Proyek mechlab3d")
    a = ap.parse_args()
    make_new_project("mechlab3d", a.proyek, rasio=a.rasio, judul=a.judul)
