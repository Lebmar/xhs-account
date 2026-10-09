# -*- coding: utf-8 -*-
"""
选题 #18 出图：生成 9 张 1080x1440 成品图
读取 ../results/topic18_result.json，输出 ../../03-output/topic18-换个考场不及格/
"""
import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
RES_JSON = os.path.join(HERE, "..", "results", "topic18_result.json")
OUT_DIR = os.path.join(HERE, "..", "..", "03-output", "topic18-换个考场不及格")
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- 视觉规范 ----------
BG = (230, 241, 251)          # #E6F1FB
MAIN = (24, 95, 165)          # #185FA5
SUB = (133, 183, 235)         # #85B7EB
ACCENT = (216, 90, 48)        # #D85A30
TEXT = (44, 44, 42)           # #2C2C2A
MUTED = (95, 94, 90)          # #5F5E5A
WHITE = (255, 255, 255)
W, H = 1080, 1440

FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
font_manager.fontManager.addfont("/Library/Fonts/Arial Unicode.ttf")
plt.rcParams["font.sans-serif"] = ["Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def F(size):
    return ImageFont.truetype(FONT_PATH, size)


def wrap(text, font, max_w):
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur); cur = ""; continue
        if font.getlength(cur + ch) > max_w:
            lines.append(cur); cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def card():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def center_text(d, y, text, font, fill, gap=14):
    for ln in wrap(text, font, W - 160):
        d.text(((W - font.getlength(ln)) / 2, y), ln, font=font, fill=fill)
        y += font.size + gap
    return y


def left_text(d, x, y, text, font, fill, max_w=880, gap=12):
    for ln in wrap(text, font, max_w):
        d.text((x, y), ln, font=font, fill=fill)
        y += font.size + gap
    return y


def footer(d, page, note="跑个数看看 · 数据实测 01"):
    d.text((60, H - 70), note, font=F(26), fill=MUTED)
    t = f"{page}/9"
    d.text((W - 60 - F(26).getlength(t), H - 70), t, font=F(26), fill=MUTED)


def head(d, title, sub=None):
    y = 90
    d.rectangle([60, 70, 60 + 8, 70 + 52], fill=MAIN)
    d.text((88, 78), title, font=F(38), fill=MAIN)
    y = 175
    if sub:
        y = left_text(d, 60, y, sub, F(30), TEXT, gap=14)
    return y


# ---------- 读结果 ----------
with open(RES_JSON, "r", encoding="utf-8") as f:
    rows = json.load(f)
rand = [r for r in rows if r["场景"] == "A_随机划分"][0]
areas = [r for r in rows if r["场景"] == "B_留出地理区域"]
acc_a, f1_a = rand["准确率"], rand["Macro_F1"]
area_f1 = [r["Macro_F1"] for r in areas]
area_names = [r["测试集"].split(" (")[0].replace("Wilderness_Area", "区域") for r in areas]
mean_b = sum(area_f1) / len(area_f1)
worst_b = min(area_f1)
drop = (mean_b - f1_a) / f1_a * 100

print(f"随机 F1={f1_a:.4f}  区域均值={mean_b:.4f}  跌幅={drop:.1f}%")

# ---------- 图 4 数据：4 区域柱状图 ----------
def chart_areas(path):
    fig, ax = plt.subplots(figsize=(9, 5.6), dpi=150)
    bars = ax.bar(range(len(area_f1)), area_f1, color="#85B7EB", width=0.6)
    bars[int(area_f1.index(worst_b))].set_color("#D85A30")
    ax.axhline(f1_a, color="#185FA5", linestyle="--", linewidth=2,
               label=f"随机划分 {f1_a:.3f}")
    ax.set_ylim(0, max(f1_a, max(area_f1)) * 1.25)
    ax.set_xticks(range(len(area_f1)))
    ax.set_xticklabels([n.replace("区域", "区域 ") for n in area_names], fontsize=18)
    ax.set_ylabel("Macro-F1", fontsize=18)
    ax.tick_params(labelsize=16)
    for i, v in enumerate(area_f1):
        ax.text(i, v + 0.015, f"{v:.3f}", ha="center", fontsize=17,
                color="#D85A30" if v == worst_b else "#185FA5")
    ax.legend(fontsize=16, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    for s in ["bottom", "left"]:
        ax.spines[s].set_color("#BFBFBF")
    ax.set_title("按地理区域划分后，各区域 Macro-F1", fontsize=20, color="#2C2C2A", pad=14)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


# ---------- 图 6 数据：对比柱状 ----------
def chart_compare(path):
    fig, ax = plt.subplots(figsize=(9, 5.2), dpi=150)
    labels = ["随机划分\n（普通考法）", "留出地理区域\n（换个考场）"]
    vals = [f1_a, mean_b]
    bars = ax.bar(labels, vals, color=["#185FA5", "#D85A30"], width=0.46)
    ax.set_ylim(0, max(vals) * 1.3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.3f}",
                ha="center", fontsize=24, color=b.get_facecolor(), fontweight="bold")
    ax.annotate("", xy=(1, mean_b + 0.015), xytext=(1, f1_a),
                arrowprops=dict(arrowstyle="-|>", color="#D85A30", lw=2.5))
    ax.text(1.06, (f1_a + mean_b) / 2, f"↓{abs(drop):.0f}%", fontsize=24,
            color="#D85A30", fontweight="bold")
    ax.set_ylabel("Macro-F1", fontsize=18)
    ax.tick_params(labelsize=17)
    ax.spines[["top", "right"]].set_visible(False)
    for s in ["bottom", "left"]:
        ax.spines[s].set_color("#BFBFBF")
    ax.set_title("同一种模型，两种考法", fontsize=20, color="#2C2C2A", pad=14)
    fig.tight_layout()
    fig.savefig(path, facecolor="white")
    plt.close(fig)


tmp_a = os.path.join(OUT_DIR, "_chart_areas.png")
tmp_c = os.path.join(OUT_DIR, "_chart_compare.png")
chart_areas(tmp_a)
chart_compare(tmp_c)


def paste(d, path, y, box_w=960):
    im = Image.open(path).convert("RGB")
    ratio = im.width / im.height
    nw = box_w
    nh = int(nw / ratio)
    im = im.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new("RGB", (nw + 40, nh + 40), WHITE)
    canvas.paste(im, (20, 20))
    d_img = Image.open(path)  # noqa
    return canvas, nw + 40, nh + 40


def mount(img, canvas, cw, ch, y):
    img.paste(canvas, ((W - cw) // 2, y))
    return y + ch


# ================= 01 封面 =================
img, d = card()
d.rectangle([0, 0, W, 14], fill=MAIN)
d.text((60, 210), "数据实测 01", font=F(34), fill=MAIN)
y = 400
for ln in ["58 万条数据训的模型", "换个考场直接不及格"]:
    f = F(78)
    d.text(((W - f.getlength(ln)) / 2, y), ln, font=f, fill=MAIN)
    y += f.size + 30
d.line([(140, y + 40), (W - 140, y + 40)], fill=SUB, width=3)
y += 110
f_big = F(150)
s1, s2 = f"{f1_a:.2f}", f"{mean_b:.2f}"
d.text((150, y), s1, font=f_big, fill=MAIN)
d.text((150 + f_big.getlength(s1) + 30, y + 10), "→", font=F(90), fill=MUTED)
d.text((150 + f_big.getlength(s1) + 150, y), s2, font=f_big, fill=ACCENT)
y += f_big.size + 40
d.text((155, y), "Macro-F1（随机考法 → 换考场）", font=F(34), fill=MUTED)
d.line([(140, 1180), (W - 140, 1180)], fill=SUB, width=2)
src = "数据来源：UCI Covertype · 581,012 条样本"
d.text(((W - F(28).getlength(src)) / 2, 1225), src, font=F(28), fill=MUTED)
footer(d, 1)
img.save(os.path.join(OUT_DIR, "01-封面.png"))

# ================= 02 提出问题 =================
img, d = card()
y = head(d, "先问一个问题")
y += 40
y = center_text(d, y, "同一份数据、同一个模型，\n只换一种考法，\n成绩能差多少？", F(56), MAIN, gap=26)
y += 60
d.rounded_rectangle([80, y, W - 80, y + 260], radius=24, fill=WHITE)
left_text(d, 130, y + 50, "大多数课程作业里，我们随机抽 20% 数据当考卷。\n但真实世界不会让你抽到\"见过的题\"。\n\n这个实验想看看：差距到底有多大。",
          F(34), TEXT, max_w=W - 260, gap=22)
footer(d, 2)
img.save(os.path.join(OUT_DIR, "02-问题.png"))

# ================= 03 数据从哪来 =================
img, d = card()
y = head(d, "数据从哪来")
rows_txt = [
    ("数据集", "UCI Covertype（美国林务局公开数据）"),
    ("样本量", "581,012 条 · 54 个特征"),
    ("任务", "7 分类：预测森林覆盖类型"),
    ("模型", "ExtraTrees，100 棵树"),
    ("划分方式 A", "随机抽 20% 当测试集"),
    ("划分方式 B", "整块地理区域留作测试集（4 次）"),
]
y += 30
for k, v in rows_txt:
    d.rounded_rectangle([80, y, W - 80, y + 128], radius=18, fill=WHITE)
    d.text((120, y + 30), k, font=F(32), fill=MAIN)
    d.text((120, y + 76), v, font=F(28), fill=TEXT)
    y += 148
footer(d, 3)
img.save(os.path.join(OUT_DIR, "03-数据来源.png"))

# ================= 04 普通考法的成绩 =================
img, d = card()
y = head(d, "考法一：随机抽题", "把 58 万条数据随机分成 80% 训练 / 20% 测试")
y += 50
for label, val, col in [("准确率", f"{acc_a:.3f}", MAIN), ("Macro-F1", f"{f1_a:.3f}", MAIN)]:
    d.rounded_rectangle([90, y, W - 90, y + 240], radius=28, fill=WHITE)
    d.text((140, y + 45), label, font=F(38), fill=MUTED)
    fv = F(120)
    d.text((140, y + 100), val, font=fv, fill=col)
    y += 270
d.text((95, y + 10), "看起来是个很能打的模型。", font=F(34), fill=MUTED)
footer(d, 4)
img.save(os.path.join(OUT_DIR, "04-随机划分成绩.png"))

# ================= 05 换考场后 =================
img, d = card()
y = head(d, "考法二：整块区域留作考卷", "4 个地理区域轮流当测试集，训练集完全不含该区域")
canvas, cw, ch = paste(d, tmp_a, y)
y2 = mount(img, canvas, cw, ch, y + 20)
left_text(d, 90, y2 + 30, f"橙色柱是最差的那个区域，Macro-F1 只有 {worst_b:.3f}。\n虚线是随机划分时的 {f1_a:.3f}。",
          F(32), TEXT, max_w=W - 180, gap=18)
footer(d, 5)
img.save(os.path.join(OUT_DIR, "05-留出区域成绩.png"))

# ================= 06 对比 =================
img, d = card()
y = head(d, "两种考法放一起看")
canvas, cw, ch = paste(d, tmp_c, y)
y2 = mount(img, canvas, cw, ch, y + 30)
d.rounded_rectangle([80, y2 + 30, W - 80, y2 + 215], radius=24, fill=WHITE)
left_text(d, 130, y2 + 70, f"平均下滑 {abs(drop):.0f}%，最差区域只有 {worst_b:.3f}。\n模型没变，数据没变，只是考卷换了。",
          F(36), TEXT, max_w=W - 260, gap=20)
footer(d, 6)
img.save(os.path.join(OUT_DIR, "06-对比.png"))

# ================= 07 为什么 =================
img, d = card()
y = head(d, "为什么会这样")
top = y + 20
d.rounded_rectangle([80, top, W - 80, top + 600], radius=26, fill=WHITE)
cx, cy = W // 2, top + 150
d.ellipse([cx - 290, cy - 130, cx + 290, cy + 130], outline=MAIN, width=5)
d.text((cx, cy - 35), "训练集", font=F(42), fill=MAIN, anchor="mm")
d.text((cx, cy + 40), "区域 1 / 2 / 3", font=F(32), fill=MUTED, anchor="mm")
by = top + 482
d.rounded_rectangle([cx - 230, top + 420, cx + 230, top + 545], radius=20,
                    fill=BG, outline=ACCENT, width=4)
d.text((cx, by - 22), "测试集：区域 4", font=F(36), fill=ACCENT, anchor="mm")
d.text((cx, by + 30), "模型从没见过这块地方", font=F(28), fill=MUTED, anchor="mm")
left_text(d, 130, top + 645,
          "随机划分时，训练集和测试集来自同一片区域、同样的土壤和海拔分布——相当于考原题。\n\n换成整块区域后，模型面对的是没见过的地理条件，平时背的答案就不管用了。",
          F(34), TEXT, max_w=W - 260, gap=22)
footer(d, 7)
img.save(os.path.join(OUT_DIR, "07-为什么.png"))

# ================= 08 结论 =================
img, d = card()
y = head(d, "结论")
concl = [
    ("1", "随机划分会系统性高估模型能力", f"本实验里高估了约 {abs(drop):.0f}%"),
    ("2", "真实数据往往来自\"不同的地方\"", "换个城市、换个时间段、换批用户，都是换考场"),
    ("3", "做过不等于会做", "这道题刷题的人最懂"),
]
y += 30
for n, t1, t2 in concl:
    d.rounded_rectangle([80, y, W - 80, y + 240], radius=24, fill=WHITE)
    d.ellipse([130, y + 55, 200, y + 125], fill=MAIN)
    tn = F(46)
    d.text((165 - tn.getlength(n) / 2 + 35, y + 68), n, font=tn, fill=WHITE)
    d.text((240, y + 55), t1, font=F(38), fill=TEXT)
    d.text((240, y + 125), t2, font=F(28), fill=MUTED)
    y += 270
footer(d, 8)
img.save(os.path.join(OUT_DIR, "08-结论.png"))

# ================= 09 互动 =================
img, d = card()
d.rectangle([0, 0, W, 14], fill=MAIN)
y = 240
y = center_text(d, y, "你遇到过\n「平时会做，考试不会」吗？", F(64), MAIN, gap=28)
y += 80
d.line([(340, y), (W - 340, y)], fill=SUB, width=3)
y += 70
y = center_text(d, y, "评论区聊聊，\n下一期想看我实测什么数据？", F(40), TEXT, gap=22)
y += 120
d.text((60, H - 240), "数据来源：UCI Covertype（美国林务局公开数据集）", font=F(26), fill=MUTED)
d.text((60, H - 195), "样本 581,012 条 · 模型 ExtraTrees(100) · 代码开源在 GitHub", font=F(26), fill=MUTED)
d.text((60, H - 150), "工具：Python / scikit-learn", font=F(26), fill=MUTED)
d.text((60, H - 70), "跑个数看看", font=F(30), fill=MAIN)
img.save(os.path.join(OUT_DIR, "09-互动.png"))

for p in (tmp_a, tmp_c):
    if os.path.exists(p):
        os.remove(p)

print("9 张图已生成 ->", OUT_DIR)
for f in sorted(os.listdir(OUT_DIR)):
    print("  ", f)
