# -*- coding: utf-8 -*-
"""账号品牌素材：主页头像（1080×1080，小红书头像规范）"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xhs_kit import F, RED, INK, save  # noqa
from PIL import Image, ImageDraw

S = 1080
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "03-output", "账号素材")

img = Image.new("RGB", (S, S), RED)
d = ImageDraw.Draw(img)

f_mark = F(540, "Black")
d.text((S // 2, 486), "跑", font=f_mark, fill="#FFFFFF", anchor="mm")

f_sub = F(88, "Medium")
d.text((S // 2, 884), "跑个数看看", font=f_sub, fill="#FFFFFF", anchor="mm")

save(img, os.path.join(OUT, "头像.png"))
print("saved ->", os.path.normpath(os.path.join(OUT, "头像.png")))
