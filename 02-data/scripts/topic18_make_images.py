# -*- coding: utf-8 -*-
"""
选题 #18 出图 —— 「你的 94% 准确率，可能只是在背答案」

叙事线（全篇只讲一件事）：
  01 封面：抛钩子
  02 结论：先说答案
  03 关联：这跟你有什么关系        ← 旧版缺这一页，读者不知道看点在哪
  04 方法：实验对象（一句话带过）
  05 对照 A：随机抽题 → 高分
  06 对照 B：换个考场 → 崩盘
  07 对比：一张图看完
  08 原因：在背答案
  09 行动：三个自查问题

运行：python3 topic18_make_images.py
每页会自检是否溢出正文区（BODY_BOTTOM = 1268）
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from xhs_kit import *  # noqa

HERE = os.path.dirname(os.path.abspath(__file__))
RESULT_JSON = os.path.join(HERE, "..", "results", "topic18_result.json")
OUT = os.path.join(HERE, "..", "..", "03-output", "topic18-换个考场不及格")

with open(RESULT_JSON, encoding="utf-8") as f:
    ROWS = json.load(f)

A = [r for r in ROWS if r["场景"] == "A_随机划分"][0]
B = [r for r in ROWS if r["场景"] == "B_留出地理区域"]
f1_a, acc_a = A["Macro_F1"], A["准确率"]
bs = [r["Macro_F1"] for r in B]
mean_b, worst_b = sum(bs) / len(bs), min(bs)
drop = (1 - mean_b / f1_a) * 100


# ============================================================ 01 封面
def page01():
    img, d = new_page()
    kicker(d, "数据实测 01")
    text_block(d, M, 246, "我把本科踩过的一个坑，用 58 万条真实数据复现了一遍",
               F(34, "Medium"), SUB, lh=1.5)

    y = title(d, "你的 94% 准确率\n可能只是在背答案", 322, size=84)
    rule(d, y + 64)

    ny = 661
    f_big, fa = F(158, "Bold"), F(90, "Regular")
    s1, s2 = f"{f1_a:.2f}", f"{mean_b:.2f}"
    x = M
    d.text((x, ny), s1, font=f_big, fill=INK)
    x += f_big.getlength(s1) + 30
    d.text((x, ny + 34), "→", font=fa, fill=FAINT)
    x += fa.getlength("→") + 30
    d.text((x, ny), s2, font=f_big, fill=RED)
    d.text((M, ny + 202), "同一个模型 · 同一份数据 · 只换了一种考法",
           font=F(38, "Medium"), fill=INK2)
    rule(d, ny + 282)

    cy = ny + 344
    card(d, cy, cy + 164, fill=RED_BG, radius=26)
    text_block(d, M + 46, cy + 40,
               "这一篇会给你三个自查问题\n判断手里的分数是真的，还是测出来的假象",
               F(38, "Medium"), "#9E2A1C", max_w=BODY_W - 92, lh=1.44)

    end = cy + 206
    d.text((M, end), "数据：UCI Covertype（美国林务局公开数据集）· 581,012 条",
           font=F(28, "Regular"), fill=MUTED)
    footer(d, 1)
    return img, end + 36


# ============================================================ 02 先说结论
def page02():
    img, d = new_page()
    kicker(d, "先说结论")
    y = big_title_center(d, "同一个模型\n成绩差了 71%", 244, size=82)
    rule(d, y + 70)

    y = stat_pair(d, y + 142, [
        ("随机划分 · 得分", "0.920", INK),
        ("换个考场 · 得分", "0.266", RED),
    ])

    cy = y + 74
    card(d, cy, cy + 300, fill=CARD, radius=28)
    yy = cy + 42
    for i, t in enumerate([
        "随机划分会系统性高估模型能力。",
        "换个城市、换时间段、换用户，都是换考场。",
        "不是模型变笨了，是之前那道题太简单。",
    ], 1):
        d.text((M + 44, yy + 3), f"{i:02d}", font=F(38, "Bold"), fill=RED)
        yy = text_block(d, M + 112, yy, t, F(36, "Regular"), INK2,
                        max_w=BODY_W - 156, lh=1.5) + 44

    end = cy + 340
    d.text((M, end), "得分 = Macro-F1，7 个类别平均后的分数，比准确率更能暴露问题",
           font=F(28, "Regular"), fill=SUB)
    footer(d, 2)
    return img, end + 36


# ============================================================ 03 这跟你有什么关系
def page03():
    img, d = new_page()
    y = kicker(d, "为什么值得你看完")
    y = title(d, "这个坑\n你大概已经踩了", 252, size=80)
    rule(d, y + 62)

    rows = [
        ("课程作业", "随机抽 20% 当测试集，跑出 94%。\n这个分数只在「这套考法」里成立。"),
        ("实习 / 比赛", "模型上线后面对的是没见过的用户、\n没见过的时间段 —— 那才是真考场。"),
        ("论文 / 答辩", "被问「你的测试集怎么划的」，\n答不上来，前面的分数都要打折。"),
    ]
    yy = y + 138
    for i, (name, desc) in enumerate(rows):
        if i:
            rule(d, yy - 34, color=LINE)
        d.text((M, yy), name, font=F(38, "Bold"), fill=INK)
        yy = text_block(d, M, yy + 58, desc, F(32, "Regular"), INK2,
                        max_w=BODY_W, lh=1.5) + 50

    end = yy + 10
    d.text((M, end), "下面用真实数据，把差距量出来。", font=F(32, "Medium"), fill=RED)
    footer(d, 3)
    return img, end + 42


# ============================================================ 04 实验对象
def page04():
    img, d = new_page()
    y = kicker(d, "实验对象")
    y = title(d, "我拿什么做的实验", 250, size=74)
    rule(d, y + 64)

    rows = [
        ("数据", "UCI Covertype，581,012 条真实森林调查记录"),
        ("特征", "54 个：海拔、坡度、到水源距离、土壤类型…"),
        ("任务", "判断这块地属于 7 种森林类型里的哪一种"),
        ("模型", "ExtraTrees（100 棵树），不用调参的经典基线"),
    ]
    yy = y + 128
    for i, (k, v) in enumerate(rows):
        d.text((M, yy + 2), k, font=F(32, "Medium"), fill=MUTED)
        text_block(d, M + 150, yy - 4, v, F(36, "Regular"), INK2,
                   max_w=BODY_W - 150, lh=1.5)
        yy += 132
        if i < len(rows) - 1:
            rule(d, yy - 40, color=LINE)

    cy = yy + 20
    card(d, cy, cy + 156, fill=RED_BG, radius=26)
    text_block(d, M + 46, cy + 44,
               "数据集本身不是重点。\n重点是下面两种考法，结果差了 3 倍多。",
               F(36, "Medium"), "#9E2A1C", max_w=BODY_W - 92, lh=1.46)
    footer(d, 4)
    return img, cy + 156


# ============================================================ 05 考法一
def page05():
    img, d = new_page()
    y = kicker(d, "考法一 · 随机抽题")
    y = title(d, "把 58 万条\n随机切成训练和测试", 250, size=74)
    y = text_block(d, M, y + 54,
                   "随机抽 80% 训练、20% 测试。这是课程作业里最默认的做法。",
                   F(34, "Regular"), INK2, lh=1.6)
    rule(d, y + 64)

    y = stat_pair(d, y + 140, [
        ("准确率", f"{acc_a:.3f}", INK),
        ("Macro-F1 得分", f"{f1_a:.3f}", INK),
    ])

    cy = y + 84
    card(d, cy, cy + 150, fill=CARD, radius=26)
    d.text((M + 46, cy + 44), "在课堂上，这是一份满分答卷。",
           font=F(38, "Bold"), fill=INK)
    d.text((M + 46, cy + 102), "换成任何一份作业，你都会直接交上去。",
           font=F(32, "Regular"), fill=SUB)

    end = cy + 208
    d.text((M, end), "但它考的是「同一片区域里的原题」。", font=F(32, "Medium"), fill=RED)
    footer(d, 5)
    return img, end + 42


# ============================================================ 06 考法二
def page06():
    img, d = new_page()
    y = kicker(d, "考法二 · 换个考场")
    y = title(d, "按地理区域切开\n每次留一整块当考卷", 250, size=74)
    y = text_block(d, M, y + 54,
                   "数据自带 4 个地理区域。每次拿 3 块训练、留 1 块测试 —— "
                   "这一块地方，模型从头到尾没见过。",
                   F(34, "Regular"), INK2, lh=1.6)
    rule(d, y + 64)

    y = stat_grid(d, y + 130, [
        ("区域 1", f"{bs[0]:.3f}", RED),
        ("区域 2", f"{bs[1]:.3f}", RED),
        ("区域 3", f"{bs[2]:.3f}", RED),
        ("区域 4", f"{bs[3]:.3f}", RED),
    ], cols=4, gapx=14, size=62, label_size=28)

    cy = y + 64
    card(d, cy, cy + 238, fill=RED_BG, radius=26)
    f_big = F(118, "Bold")
    sv = f"{mean_b:.3f}"
    d.text((M + 46, cy + 44), sv, font=f_big, fill=RED)
    d.text((M + 46 + f_big.getlength(sv) + 34, cy + 92),
           f"平均分 · 比随机划分低 {drop:.0f}%", font=F(38, "Bold"), fill="#9E2A1C")
    d.text((M + 46, cy + 178), f"最差的一块地方，只有 {worst_b:.3f}。",
           font=F(34, "Regular"), fill="#9E2A1C")
    footer(d, 6)
    return img, cy + 238


# ============================================================ 07 对比
def page07():
    img, d = new_page()
    y = kicker(d, "放在一起看")
    y = title(d, "两种考法，一张图", 250, size=74)
    rule(d, y + 88)

    y = hbar_chart(d, y + 186, [
        ("随机划分（课程作业里的默认做法）", f1_a, f"{f1_a:.3f}", INK),
        ("按区域留一（模型没见过的地方）", mean_b, f"{mean_b:.3f}", RED),
    ], max_value=f1_a, bar_h=74, value_size=56, label_size=33)

    cy = y + 92
    card(d, cy, cy + 248, fill=CARD, radius=26)
    d.text((M + 46, cy + 44), f"↓ {drop:.0f}%", font=F(96, "Bold"), fill=RED)
    text_block(d, M + 46, cy + 172,
               "模型没变，数据没变，只是考卷换了一种出法。",
               F(36, "Medium"), INK2, max_w=BODY_W - 92, lh=1.5)
    footer(d, 7)
    return img, cy + 248


# ============================================================ 08 为什么
def page08():
    img, d = new_page()
    y = kicker(d, "原因")
    y = title(d, "因为它只是在背答案", 250, size=74)
    rule(d, y + 60)

    blocks = [
        ("随机划分", "mixed", "训练和测试来自同一片区域 —— 相当于考原题。"),
        ("按区域留一", "split", "整块区域从没进过训练集 —— 相当于换考场。"),
    ]
    yy = y + 112
    for i, (label, mode, cap) in enumerate(blocks):
        d.text((M, yy), label, font=F(36, "Bold"), fill=INK)
        if i == 0:
            legend(d, W - M, yy + 4, [(DOT_TRAIN, "训练集"), (RED, "测试集")])
        yy += 54
        compare_strip(d, yy, M, W - M, 132, mode, seed=11 if mode == "mixed" else 0)
        yy = text_block(d, M, yy + 152, cap, F(32, "Regular"), INK2,
                        max_w=BODY_W, lh=1.5) + 54

    end = yy + 6
    card(d, end, end + 148, fill=RED_BG, radius=26)
    text_block(d, M + 46, end + 52,
               "分数掉下来不是模型变笨了，是之前那道题太简单。",
               F(36, "Bold"), "#9E2A1C", max_w=BODY_W - 92, lh=1.45)
    footer(d, 8)
    return img, end + 148


# ============================================================ 09 自查
def page09():
    img, d = new_page()
    y = kicker(d, "所以，你自己也测一下")
    y = title(d, "三个问题\n判断你的分数是真的吗", 250, size=74)
    rule(d, y + 62)

    y = checklist(d, y + 110, [
        "你的测试集和训练集，是不是同一批来源？同一批用户、同一段时间、同一个地方都算。",
        "把测试集换成另一段时间或另一批人，分数会掉多少？",
        "别只看准确率。7 个类别里只猜中多数类，准确率也可能很好看。",
    ], num_size=38, text_size=34, gap=36)

    cy = y + 72
    card(d, cy, cy + 196, fill=CARD, radius=26)
    d.text((M + 46, cy + 42), "你的项目掉过多少？", font=F(38, "Bold"), fill=INK)
    text_block(d, M + 46, cy + 106,
               "评论区报个数 —— 留言最多的那种数据，我下期拿真实数据跑一遍。",
               F(33, "Regular"), INK2, max_w=BODY_W - 92, lh=1.5)
    footer(d, 9)
    return img, cy + 196


PAGES = [
    (page01, "01-封面"),
    (page02, "02-结论"),
    (page03, "03-跟你有什么关系"),
    (page04, "04-实验对象"),
    (page05, "05-随机抽题"),
    (page06, "06-换个考场"),
    (page07, "07-对比"),
    (page08, "08-原因"),
    (page09, "09-自查"),
]

if __name__ == "__main__":
    for f in os.listdir(OUT):
        if f.endswith(".png"):
            os.remove(os.path.join(OUT, f))

    over = []
    for fn, name in PAGES:
        img, end = fn()
        save(img, os.path.join(OUT, f"{name}.png"))
        flag = "OK " if end <= BODY_BOTTOM else "溢出"
        if end > BODY_BOTTOM:
            over.append((name, round(end)))
        print(f"{flag} {name:20s} 内容底部 y={end:.0f}  剩余={BODY_BOTTOM - end:.0f}px")

    print()
    if over:
        print("!! 以下页面超出正文区：", over)
    else:
        print("全部通过，无溢出")
    print(f"A f1={f1_a:.4f} acc={acc_a:.4f} | B mean={mean_b:.4f} worst={worst_b:.4f} | drop={drop:.1f}%")
