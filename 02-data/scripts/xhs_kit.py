# -*- coding: utf-8 -*-
"""
xhs_kit —— 「跑个数看看」小红书图文通用出图设计系统

设计原则
--------
1. 纯白底、大留白但**不留空**：内容区固定 200 → 1268，底部必须有事做
2. 只用两个数据色：墨黑（正常/好） + 朱红（异常/失败），不用第三色
3. 全程 PIL 手绘（含图表），不借助 matplotlib，保证字体与全篇完全一致
4. 中英混排：中文 Noto Sans SC，数字与英文同字体，字重区分层级

用法
----
    from xhs_kit import *
    img, d = new_page()
    y = kicker(d, "先说结论")
    y = title(d, "同一个模型，成绩差了 71%", y)
    y = text_block(d, M, y, "正文……", F(36), INK2, lh=1.62)
    footer(d, 2)
    save(img, "out/02.png")
"""

import os
import re
from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- 画布与配色

W, H = 1080, 1440          # 小红书 3:4
M = 88                     # 左右安全边距
BODY_W = W - 2 * M         # 正文可用宽度 904
BODY_TOP = 200             # 正文起始 y
BODY_BOTTOM = 1268         # 正文必须结束于此之前
FOOT_Y = 1310              # 页脚分隔线

BG = "#FFFFFF"             # 底色
CARD = "#F4F5F7"           # 卡片底
CARD2 = "#EEF0F3"          # 次级卡片底
INK = "#15171C"            # 主文字 / 正常数据
INK2 = "#414752"           # 正文
SUB = "#6B7280"            # 次要句子（整句式说明）
MUTED = "#8E949E"          # 次要说明
FAINT = "#C7CBD2"          # 极淡（页码等）
LINE = "#E8EAEE"           # 分隔线
RED = "#E23E2B"            # 强调 / 异常数据
RED_BG = "#FBEDEA"         # 红色浅底

# ---------------------------------------------------------------- 字体

_HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(_HERE, "..", "assets", "fonts", "NotoSansSC-VF.ttf")

_FC = {}


def F(size, weight="Regular"):
    """取字体。weight: Thin/ExtraLight/Light/Regular/Medium/SemiBold/Bold/ExtraBold/Black"""
    key = (size, weight)
    if key not in _FC:
        f = ImageFont.truetype(FONT_PATH, size)
        f.set_variation_by_name(weight)
        _FC[key] = f
    return _FC[key]


# ---------------------------------------------------------------- 文本工具

_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9\.\-–—%/_+]*|\s+|.", re.S)


def wrap(text, font, max_w):
    """中英混排折行：中文逐字断，英文/数字整体不拆"""
    out = []
    for para in text.split("\n"):
        toks = _TOKEN.findall(para)
        cur = ""
        for t in toks:
            if font.getlength(cur + t) <= max_w or not cur.strip():
                cur += t
            else:
                out.append(cur.rstrip())
                cur = "" if t.isspace() else t.lstrip()
        out.append(cur.rstrip())
    return out


def text_block(d, x, y, text, font, fill, max_w=None, lh=1.60, spacing=0, anchor=None):
    """
    画一段会自动折行的文本。返回紧贴最后一行的底部 y。
    spacing：行间额外间距（用于长段落舒服些）
    """
    max_w = max_w or (W - M - x)
    step = int(font.size * lh) + spacing
    for ln in wrap(text, font, max_w):
        if anchor:
            d.text((x, y), ln, font=font, fill=fill, anchor=anchor)
        else:
            d.text((x, y), ln, font=font, fill=fill)
        y += step
    return y - step + int(font.size * 1.30)


def measure_lines(text, font, max_w):
    return len(wrap(text, font, max_w))


# ---------------------------------------------------------------- 页面骨架


def new_page(bg=BG):
    img = Image.new("RGB", (W, H), bg)
    return img, ImageDraw.Draw(img)


def kicker(d, label, color=None):
    """页顶栏目条：竖短线 + 栏目名。返回用完的 y（正文从这里往下一点开始）"""
    y = 92
    d.rounded_rectangle([M, y + 5, M + 7, y + 41], radius=3, fill=color or RED)
    d.text((M + 24, y), label, font=F(34, "Medium"), fill=INK)
    return y + 62


def footer(d, idx=None, total=9):
    d.line([(M, FOOT_Y), (W - M, FOOT_Y)], fill=LINE, width=2)
    d.text((M, FOOT_Y + 28), "跑个数看看", font=F(28, "Medium"), fill=MUTED)
    if idx:
        s = f"{idx}/{total}"
        f = F(28, "Medium")
        d.text((W - M - f.getlength(s), FOOT_Y + 28), s, font=f, fill=MUTED)


def title(d, text, y, size=72, fill=INK, weight="Bold", max_w=None, lh=1.30):
    """大标题。返回底部 y"""
    f = F(size, weight)
    max_w = max_w or BODY_W
    step = int(size * lh)
    for ln in wrap(text, f, max_w):
        d.text((M, y), ln, font=f, fill=fill)
        y += step
    return y - step + int(size * 1.26)


def big_title_center(d, text, y, size=76, fill=INK, weight="Bold", max_w=None, lh=1.34):
    f = F(size, weight)
    max_w = max_w or BODY_W
    step = int(size * lh)
    for ln in wrap(text, f, max_w):
        d.text((W // 2, y), ln, font=f, fill=fill, anchor="ma")
        y += step
    return y - step + int(size * 1.26)


def rule(d, y, color=LINE, width=2, x0=None, x1=None):
    d.line([(x0 or M, y), (x1 or W - M, y)], fill=color, width=width)
    return y


def card(d, y0, y1, fill=CARD, x0=None, x1=None, radius=28, outline=None, ow=2):
    x0 = M if x0 is None else x0
    x1 = W - M if x1 is None else x1
    d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill,
                        outline=outline, width=ow if outline else 0)
    return y1


def pill(d, x, y, text, font=None, fg=INK, bg=CARD, padx=26, pady=14):
    """小标签胶囊，返回 (宽度, 高度)"""
    font = font or F(30, "Medium")
    tw = font.getlength(text)
    w = int(tw + padx * 2)
    h = font.size + pady * 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    d.text((x + padx, y + pady - 2), text, font=font, fill=fg)
    return w, h


# ---------------------------------------------------------------- 数据组件


def stat(d, x, y, label, value, color=INK, size=116, label_size=32, label_gap=16):
    """
    竖排数据块：小标签 + 巨大数字。返回底部 y。
    """
    fl = F(label_size, "Medium")
    d.text((x, y), label, font=fl, fill=MUTED)
    y += label_size + label_gap
    fv = F(size, "Bold")
    d.text((x, y), value, font=fv, fill=color)
    y += int(size * 1.05)
    return y


def stat_pair(d, y, items, gap=40):
    """
    并列数据块：items = [(label, value, color), ...] 均分 BODY_W。
    返回底部 y。
    """
    n = len(items)
    cw = (BODY_W - gap * (n - 1)) / n
    y0 = y
    ymax = y
    for i, (label, value, color) in enumerate(items):
        x = M + i * (cw + gap)
        yy = stat(d, int(x), y0, label, value, color=color,
                  size=112 if n <= 2 else 84,
                  label_size=30 if n <= 2 else 28)
        ymax = max(ymax, yy)
    return ymax


def stat_grid(d, y, items, cols=2, gapx=32, gapy=44, size=84, label_size=28):
    """
    网格数据块：items = [(label, value, color), ...]。返回底部 y。
    """
    cw = (BODY_W - gapx * (cols - 1)) / cols
    y0 = y
    for i, (label, value, color) in enumerate(items):
        r, c = divmod(i, cols)
        x = M + c * (cw + gapx)
        yy = y0 + r * (label_size + 16 + int(size * 1.05) + gapy)
        stat(d, int(x), int(yy), label, value, color=color, size=size, label_size=label_size)
    rows = (len(items) + cols - 1) // cols
    return y0 + rows * (label_size + 16 + int(size * 1.05) + gapy) - gapy


def checklist(d, y, items, num_size=40, text_size=36, gap=34, num_color=RED):
    """
    带序号的要点列表。items = [str, ...]。返回底部 y。
    """
    fn = F(num_size, "Bold")
    ft = F(text_size, "Regular")
    for i, t in enumerate(items, 1):
        n = f"{i:02d}"
        d.text((M, y), n, font=fn, fill=num_color)
        end = text_block(d, M + 78, y + 4, t, ft, INK2, max_w=BODY_W - 78, lh=1.55)
        y = end + gap
    return y - gap


def hbar_chart(d, y, rows, max_value, bar_h=62, value_size=52, label_size=32,
               track=CARD2, width=None):
    """
    横向条形图，纯 PIL 手绘。
    rows = [(标签, 数值, 显示文本, 颜色), ...]
    返回底部 y。
    """
    width = width or BODY_W
    fv = F(value_size, "Bold")
    fl = F(label_size, "Medium")
    # 给数值文字留出右侧空间
    reserve = 190
    track_w = width - reserve
    for label, value, show, color in rows:
        d.text((M, y), label, font=fl, fill=MUTED)
        y += label_size + 18
        w = max(int(track_w * (value / max_value)), 10)
        d.rounded_rectangle([M, y, M + track_w, y + bar_h], radius=bar_h // 2, fill=track)
        d.rounded_rectangle([M, y, M + w, y + bar_h], radius=bar_h // 2, fill=color)
        d.text((M + w + 26, y + bar_h // 2), show, font=fv, fill=color, anchor="lm")
        y += bar_h + 54
    return y - 54


DOT_TRAIN = "#2B3038"     # 训练集点
DOT_TEST = RED            # 测试集点


def dot_field(d, x0, y0, x1, y1, red_ratio, seed, cell=16, gap=5, mixed=True, split_at=0.72):
    """
    点阵示意图。
    mixed=True  → 红点随机混在训练点中间（随机划分）
    mixed=False → 右侧一整块红点（按区域留一）
    """
    import random
    rnd = random.Random(seed)
    step = cell + gap
    cols = int((x1 - x0) // step)
    rows = int((y1 - y0) // step)
    split = int(cols * split_at)
    for r in range(rows):
        for c in range(cols):
            is_red = (rnd.random() < red_ratio) if mixed else (c >= split)
            px, py = x0 + c * step, y0 + r * step
            d.rounded_rectangle([px, py, px + cell, py + cell], radius=4,
                                fill=DOT_TEST if is_red else DOT_TRAIN)
    return x0, x1


def compare_strip(d, y, x0, x1, h, mode, seed=7):
    """一整块对比示意条：mode='mixed' 或 'split'"""
    d.rounded_rectangle([x0, y, x1, y + h], radius=20, fill="#F0F1F4")
    pad = 18
    dot_field(d, x0 + pad, y + pad, x1 - pad, y + h - pad,
              red_ratio=0.20, seed=seed, cell=16, gap=6, mixed=(mode == "mixed"))
    return y + h


def legend(d, x_right, y, items, size=26, sq=16):
    """右对齐的小图例：items=[(颜色, 文字), ...]"""
    f = F(size, "Medium")
    x = x_right
    for col, txt in reversed(items):
        tw = f.getlength(txt)
        d.rounded_rectangle([x - tw - sq - 10, y + 4, x - tw - 10, y + 4 + sq],
                            radius=4, fill=col)
        d.text((x - tw, y), txt, font=f, fill=MUTED)
        x -= tw + sq + 44
    return y + size


# ---------------------------------------------------------------- 输出


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, "PNG", optimize=True)
    return path
