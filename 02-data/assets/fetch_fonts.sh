#!/usr/bin/env bash
# 拉取出图用的字体（17MB 二进制，不入库，克隆后跑一次即可）
set -euo pipefail
cd "$(dirname "$0")/fonts"

URL="https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf"

if [ -f NotoSansSC-VF.ttf ]; then
  echo "已存在，跳过：NotoSansSC-VF.ttf"
  exit 0
fi

echo "下载 Noto Sans SC 可变字体…"
curl -fL --progress-bar -o NotoSansSC-VF.ttf "$URL"

python3 - <<'PY'
from PIL import ImageFont
p = "NotoSansSC-VF.ttf"
for w in ("Regular", "Medium", "Bold", "Black"):
    f = ImageFont.truetype(p, 60)
    f.set_variation_by_name(w)
    print("ok", w, f.getname())
PY

echo "字体就绪。"
