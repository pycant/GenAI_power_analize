import os
import sys
import math
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


os.environ["HF_ENDPOINT"] = "https://huggingface.co"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BARTScore"))


def build_samples():
    samples = []
    items = [
        ("qa_common", "法国的首都是哪里？", "巴黎", "zh", "terse"),
        ("qa_science", "光合作用的主要产物是什么？", "葡萄糖和氧气", "zh", "technical"),
        ("qa_programming", "Python中用于定义函数的关键字是什么？", "def", "en", "code"),
        ("qa_history", "《傲慢与偏见》的作者是谁？", "简·奥斯汀", "zh", "narrative"),
        ("qa_math", "圆的周长公式是什么？", "2πr", "en", "formulaic"),
        ("qa_common", "世界上使用人数最多的语言是哪种？", "英语或中文", "zh", "general"),
    ]
    models = {
        "model_A": [
            "巴黎",
            "氧气",
            "def",
            "简·奥斯汀",
            "2πr",
            "中文",
        ],
        "model_B": [
            "里昂",
            "葡萄糖",
            "function",
            "莎士比亚",
            "πr^2",
            "英语",
        ],
        "model_C": [
            "法国的首都是巴黎",
            "产生氧气作为副产物",
            "使用def来定义函数",
            "作者是简·奥斯汀",
            "周长等于半径乘以2π",
            "汉语普通话",
        ],
    }
    for idx, (task, q, ref, lang, style) in enumerate(items, start=1):
        for m, answers in models.items():
            ans = answers[idx - 1]
            samples.append(
                {
                    "qid": idx,
                    "task": task,
                    "language": lang,
                    "style": style,
                    "question": q,
                    "reference": ref,
                    "model": m,
                    "answer": ans,
                }
            )
    return pd.DataFrame(samples)


def minmax_normalize(values):
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return arr
    lo = arr.min()
    hi = arr.max()
    if abs(hi - lo) < 1e-12:
        return np.ones_like(arr) * 0.5
    return (arr - lo) / (hi - lo)


def gini(values):
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return 0.0
    arr = arr + max(1e-6, -arr.min() + 1e-6)
    arr.sort()
    n = arr.size
    cum = 0.0
    for i, v in enumerate(arr, start=1):
        cum += (2 * i - n - 1) * v
    mu = arr.mean()
    if mu == 0:
        return 0.0
    return abs(cum) / (n * n * mu)


def theil(values):
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return 0.0
    arr = arr + max(1e-6, -arr.min() + 1e-6)
    mu = arr.mean()
    if mu == 0:
        return 0.0
    r = arr / mu
    return float(np.mean(r * np.log(r + 1e-12)))


def fairness_gap(group_means, global_mean):
    return float(max(abs(m - global_mean) for m in group_means.values())) if group_means else 0.0


def nsw(group_means, eps=1e-6):
    return float(sum(math.log(eps + m) for m in group_means.values()))


def score_with_bart(df):
    from bart_score import BARTScorer

    try:
        import torch
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    except Exception:
        device = "cpu"

    scorer = BARTScorer(device=device, checkpoint="facebook/bart-large-cnn")
    refs = list(df["reference"].values)
    hyps = list(df["answer"].values)
    raw = scorer.score(refs, hyps, batch_size=4)
    return np.array(raw, dtype=float)


def compute_scores(df, lam=0.2, group_by="task"):
    raw = score_with_bart(df)
    quality = -raw
    norm_quality = minmax_normalize(quality)
    df = df.copy()
    df["raw_bartscore"] = raw
    df["quality"] = norm_quality
    records = []
    for m in sorted(df["model"].unique()):
        sub = df[df["model"] == m]
        global_mean = float(sub["quality"].mean()) if len(sub) else 0.0
        if group_by not in sub.columns:
            group_by = "task"
        group_means = {
            g: float(sub[sub[group_by] == g]["quality"].mean()) for g in sub[group_by].unique()
        }
        fg = fairness_gap(group_means, global_mean)
        g = gini(list(sub["quality"].values))
        t = theil(list(sub["quality"].values))
        w = nsw(group_means)
        fair_score = global_mean * (1.0 - lam * fg)
        records.append(
            {
                "model": m,
                "global_mean": global_mean,
                "fairness_gap": fg,
                "gini": g,
                "theil": t,
                "nsw": w,
                "fair_quality_score": fair_score,
            }
        )
    return df, pd.DataFrame(records)


def visualize(df, agg, outdir):
    os.makedirs(outdir, exist_ok=True)
    plt.figure(figsize=(8, 5))
    sns.barplot(data=agg, x="model", y="global_mean", hue=None)
    plt.ylabel("归一化质量分数（基于BARTScore）")
    plt.title("各模型平均问答质量（BARTScore→归一化）")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "bart_qa_quality_avg_bar.png"))
    plt.close()
    plt.figure(figsize=(9, 5))
    sns.barplot(data=agg, x="model", y="fair_quality_score", hue=None)
    plt.ylabel("公平化质量分数")
    plt.title("各模型公平化综合质量（BARTScore→TRF公平正则）")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "bart_qa_quality_fair_bar.png"))
    plt.close()
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x="model", y="quality")
    plt.ylabel("归一化质量分数")
    plt.title("各模型分布对比（按样本）")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "bart_qa_quality_box.png"))
    plt.close()
    pivot = df.pivot(index="qid", columns="model", values="quality")
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGnBu")
    plt.xlabel("模型")
    plt.ylabel("问题ID")
    plt.title("问题-模型质量热力图（BARTScore归一化）")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "bart_qa_quality_heatmap.png"))
    plt.close()


def main():
    df = build_samples()
    df, agg = compute_scores(df, lam=0.2)
    outdir = os.path.join(os.path.dirname(__file__), "figures")
    visualize(df, agg, outdir)
    csv_path = os.path.join(os.path.dirname(__file__), "bart_qa_quality_scores.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print("saved", csv_path)
    print("saved", os.path.join(outdir, "bart_qa_quality_avg_bar.png"))
    print("saved", os.path.join(outdir, "bart_qa_quality_fair_bar.png"))
    print("saved", os.path.join(outdir, "bart_qa_quality_box.png"))
    print("saved", os.path.join(outdir, "bart_qa_quality_heatmap.png"))
    print("done")


if __name__ == "__main__":
    main()
