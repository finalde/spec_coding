#!/usr/bin/env bash
set -euo pipefail

# Run from anywhere:  ./run_man.sh        (mini shape, default)
#                       ./run_man.sh full  (Hunyuan3D-2 full DiT)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$SCRIPT_DIR"

RIGS="$REPO_ROOT/ai_videos/2026-04-08_weather_love_story/reference_rigs"
OUT="$REPO_ROOT/ai_videos/2026-04-08_weather_love_story/models"
mkdir -p "$OUT"

SHAPE_ARGS=()
if [[ "${1:-mini}" == "full" ]]; then
  SHAPE_ARGS=(--shape full)
fi

"$SCRIPT_DIR/.venv/bin/python" main.py \
  "${SHAPE_ARGS[@]}" \
  --front "$RIGS/man_front.png" \
  --side "$RIGS/man_side.png" \
  --back "$RIGS/man_back.png" \
  --output "$OUT/man.glb" \
  --prompt "男性，约30岁，185cm，清瘦修长，短黑发两侧服帖顶部略蓬松，深蓝羊毛过膝大衣，炭灰色直筒长裤，黑色系带皮鞋，平静内敛神态，双手自然垂于体侧，纯白背景" \
  --skip-validation

echo "Output: $OUT/man.glb"
