import os, sys
_R = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _R not in sys.path: sys.path.insert(0, _R)
from aset_global.cutaway_runner import cli_render
if __name__ == "__main__": cli_render("mechlab3d")
