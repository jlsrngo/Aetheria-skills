#!/bin/bash
# newjob.sh - buat folder job Blender lokal siap render: bash aset_global/blender_kit/newjob.sh <job_dir>
set -e
K="$(cd "$(dirname "$0")" && pwd)"
GF="$(cd "$K/.." && pwd)/fonts/Baloo2-Var.ttf"
J="$1"
[ -n "$J" ] || { echo "usage: bash newjob.sh <job_dir>"; exit 1; }
mkdir -p "$J"
cp "$K"/explainer_kit.py "$K"/scene_extras.py "$K"/kitjob.py "$K"/captions.py "$K"/scene_check.py "$K"/audio/*.py "$K"/box/* "$K"/sandbox/* "$J"/
[ -f "$J/Baloo2.ttf" ] || { [ -f "$GF" ] && cp "$GF" "$J/Baloo2.ttf"; } || true
echo "job folder siap: $J"
