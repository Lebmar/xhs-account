# -*- coding: utf-8 -*-
"""
选题 #18：58 万条数据训出的模型，换个考法直接不及格

数据来源：UCI Covertype（美国林务局 RIS 数据，公开数据集）
采集时间：2026-10-09
样本量：581012 行 × 54 特征，7 分类（森林覆盖类型）

要证明的结论：
  随机划分测试集时模型 macro-F1 高达 0.9+；但一旦按地理区域划分（模拟"换个考场"），
  性能暴跌。说明随机划分会高估模型在真实场景的表现——这是机器学习里最容易被忽视的坑。

产出：../results/topic18_result.csv
"""
import os
import time
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.metrics import accuracy_score, f1_score

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "raw", "covtype.data")
OUT_DIR = os.path.join(HERE, "..", "results")
os.makedirs(OUT_DIR, exist_ok=True)

NUM_COLS = [
    "Elevation", "Aspect", "Slope",
    "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology",
    "Horizontal_Distance_To_Roadways",
    "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm",
    "Horizontal_Distance_To_Fire_Points",
]
WA_COLS = [f"Wilderness_Area{i}" for i in range(1, 5)]
SOIL_COLS = [f"Soil_Type{i}" for i in range(1, 41)]
COLS = NUM_COLS + WA_COLS + SOIL_COLS + ["Cover_Type"]

print("读取数据 ...")
t0 = time.time()
df = pd.read_csv(RAW, header=None, names=COLS)
print(f"  形状: {df.shape}  耗时 {time.time() - t0:.1f}s")

X = df.drop(columns=["Cover_Type"]).values
y = df["Cover_Type"].values
wa = df[WA_COLS].values.argmax(axis=1) + 1  # 1..4

print(f"  类别分布: {dict(zip(*np.unique(y, return_counts=True)))}")
print(f"  地理区域分布: {dict(zip(*np.unique(wa, return_counts=True)))}")


def run(Xtr, ytr, Xte, yte, tag):
    clf = ExtraTreesClassifier(
        n_estimators=100, random_state=42, n_jobs=-1, bootstrap=True
    )
    t = time.time()
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xte)
    acc = accuracy_score(yte, pred)
    f1 = f1_score(yte, pred, average="macro", zero_division=0)
    print(f"  [{tag}] acc={acc:.4f}  macro-F1={f1:.4f}  ({time.time() - t:.0f}s)")
    return acc, f1


rows = []

# ---- 场景 A：随机划分（课堂里的标准做法）----
print("\n场景 A：随机 80/20 划分")
rng = np.random.RandomState(42)
idx = rng.permutation(len(X))
cut = int(len(X) * 0.8)
tr, te = idx[:cut], idx[cut:]
acc_a, f1_a = run(X[tr], y[tr], X[te], y[te], "随机划分")
rows.append({"场景": "A_随机划分", "测试集": "随机 20%", "准确率": acc_a, "Macro_F1": f1_a})

# ---- 场景 B：按地理区域留一（模拟"换个考场"）----
print("\n场景 B：leave-one-wilderness-area-out")
for area in sorted(np.unique(wa)):
    tr_idx = np.where(wa != area)[0]
    te_idx = np.where(wa == area)[0]
    acc_b, f1_b = run(X[tr_idx], y[tr_idx], X[te_idx], y[te_idx], f"留出区域{area}")
    rows.append({
        "场景": "B_留出地理区域",
        "测试集": f"Wilderness_Area{area} (n={len(te_idx)})",
        "准确率": acc_b, "Macro_F1": f1_b,
    })

res = pd.DataFrame(rows)
res["准确率"] = res["准确率"].round(4)
res["Macro_F1"] = res["Macro_F1"].round(4)
out = os.path.join(OUT_DIR, "topic18_result.csv")
res.to_csv(out, index=False, encoding="utf-8-sig")

b = res[res["场景"] == "B_留出地理区域"]["Macro_F1"]
print("\n" + "=" * 52)
print(f"随机划分      macro-F1 = {f1_a:.4f}")
print(f"留出地理区域  macro-F1 均值 = {b.mean():.4f}  最差 = {b.min():.4f}")
print(f"性能跌幅      {(b.mean() - f1_a) / f1_a * 100:.1f}%")
print(f"结果已保存: {out}")
print("=" * 52)

# 供出图脚本读取
res.to_json(os.path.join(OUT_DIR, "topic18_result.json"), orient="records", force_ascii=False)
