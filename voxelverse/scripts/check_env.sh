#!/usr/bin/env bash
# check_env.sh - cek lingkungan VoxelVerse. Baris diawali [OK] / [GAGAL] / [INFO].
fail=0
ok()   { echo "[OK]    $*"; }
bad()  { echo "[GAGAL] $*"; fail=1; }
info() { echo "[INFO]  $*"; }
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null && "$c" -c "import sys" >/dev/null 2>&1; then
    PY="$c"
    break
  fi
done
if [ -z "$PY" ]; then
  bad "python3/python tidak ditemukan"
fi
if command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null; then
  ok "ffmpeg $(ffmpeg -version | head -1 | awk '{print $3}')"
  ffmpeg -hide_banner -encoders 2>/dev/null | grep -q libx264 && ok "encoder libx264" || bad "libx264 tidak ada"
  ffmpeg -hide_banner -encoders 2>/dev/null | grep -qE ' aac ' && ok "encoder aac" || bad "encoder aac tidak ada"
  ffmpeg -hide_banner -filters 2>/dev/null | grep -q sidechaincompress && ok "ducking musik (sidechaincompress)" || info "tanpa sidechaincompress"
else
  bad "ffmpeg/ffprobe tidak ditemukan"
fi
if [ -n "$PY" ]; then
  "$PY" -c "import PIL, numpy; print('[OK]    Pillow', PIL.__version__, '+ numpy', numpy.__version__)" 2>/dev/null || bad "Pillow/numpy tidak ada (pip install pillow numpy)"
  S="$(cd "$(dirname "$0")" && pwd)"
  command -v cygpath >/dev/null 2>&1 && S="$(cygpath -m "$S")"
  "$PY" -c "import sys; sys.path.insert(0,'$S'); import voxel; f=voxel.font('judul',40); print('[OK]    font bulat + mesin 3D voxel siap:', f.path.split('/')[-1].split('\\\\')[-1])" 2>/dev/null || bad "voxel.py / font gagal dimuat"
fi
info "CPU: $(nproc 2>/dev/null || echo "${NUMBER_OF_PROCESSORS:-?}") core (render paralel)"
[ -d /mnt/user-data/outputs ] && info "mode chat: hasil akhir disalin ke /mnt/user-data/outputs; perintah dibatasi ±3 menit" || info "mode lokal / desktop"
exit $fail
