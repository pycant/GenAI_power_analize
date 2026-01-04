import os
import math
import pandas as pd
import numpy as np


def gini(arr):
    arr = np.array(arr, dtype=float)
    if arr.size == 0:
        return 0.0
    arr = arr + max(1e-6, -arr.min() + 1e-6)
    arr.sort()
    n = arr.size
    mu = arr.mean()
    if mu == 0:
        return 0.0
    cum = 0.0
    for i, v in enumerate(arr, start=1):
        cum += (2 * i - n - 1) * v
    return abs(cum) / (n * n * mu)


def theil(arr):
    arr = np.array(arr, dtype=float)
    if arr.size == 0:
        return 0.0
    arr = arr + max(1e-6, -arr.min() + 1e-6)
    mu = arr.mean()
    if mu == 0:
        return 0.0
    r = arr / mu
    return float(np.mean(r * np.log(r + 1e-12)))


def fairness_gap(group_means, gm):
    return max(abs(m - gm) for m in group_means.values()) if group_means else 0.0


def nsw(group_means, eps=1e-6):
    return sum(math.log(eps + m) for m in group_means.values())


def summarize(path, lam=0.2, group_by="task"):
    df = pd.read_csv(path)
    models = sorted(df["model"].unique())
    rows = []
    for m in models:
        sub = df[df["model"] == m]
        gm = float(sub["quality"].mean()) if len(sub) > 0 else 0.0
        if group_by not in sub.columns:
            group_by = "task"
        group_means = {
            g: float(sub[sub[group_by] == g]["quality"].mean()) for g in sub[group_by].unique()
        }
        fg = fairness_gap(group_means, gm)
        g = gini(sub["quality"])
        t = theil(sub["quality"])
        w = nsw(group_means)
        fair = gm * (1 - lam * fg)
        rows.append(
            {
                "model": m,
                "global_mean": gm,
                "fairness_gap": fg,
                "gini": g,
                "theil": t,
                "nsw": w,
                "fair_quality_score": fair,
            }
        )
    out = pd.DataFrame(rows).sort_values("fair_quality_score", ascending=False)
    return out


def summarize_multi_lambda(path, lambdas=(0.1, 0.2, 0.3), group_by="task", system="F1"):
    frames = []
    for lam in lambdas:
        out = summarize(path, lam=lam, group_by=group_by).copy()
        out["lam"] = lam
        out["system"] = system
        frames.append(out)
    return pd.concat(frames, ignore_index=True)


def main():
    base = os.path.dirname(__file__)
    f1_path = os.path.join(base, "qa_quality_scores.csv")
    bart_path = os.path.join(base, "bart_qa_quality_scores.csv")
    lambdas = (0.1, 0.2, 0.3)
    print("=" * 72)
    print("Fairness report by task groups")
    report_task_f1 = summarize_multi_lambda(f1_path, lambdas=lambdas, group_by="task", system="F1")
    report_task_bart = summarize_multi_lambda(bart_path, lambdas=lambdas, group_by="task", system="BART")
    report_task = pd.concat([report_task_f1, report_task_bart], ignore_index=True)
    print(report_task.sort_values(["system", "lam", "fair_quality_score"], ascending=[True, True, False]).to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("=" * 72)
    print("Fairness report by language groups")
    report_lang_f1 = summarize_multi_lambda(f1_path, lambdas=lambdas, group_by="language", system="F1")
    report_lang_bart = summarize_multi_lambda(bart_path, lambdas=lambdas, group_by="language", system="BART")
    report_lang = pd.concat([report_lang_f1, report_lang_bart], ignore_index=True)
    print(report_lang.sort_values(["system", "lam", "fair_quality_score"], ascending=[True, True, False]).to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("=" * 72)
    print("Fairness report by style groups")
    report_style_f1 = summarize_multi_lambda(f1_path, lambdas=lambdas, group_by="style", system="F1")
    report_style_bart = summarize_multi_lambda(bart_path, lambdas=lambdas, group_by="style", system="BART")
    report_style = pd.concat([report_style_f1, report_style_bart], ignore_index=True)
    print(report_style.sort_values(["system", "lam", "fair_quality_score"], ascending=[True, True, False]).to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    out_path = os.path.join(base, "fairness_report.csv")
    combined = pd.concat([report_task.assign(group_by="task"), report_lang.assign(group_by="language"), report_style.assign(group_by="style")], ignore_index=True)
    combined.to_csv(out_path, index=False, encoding="utf-8")
    print("=" * 72)
    print("saved", out_path)
    print("Top by fair_quality_score (task, F1):", report_task_f1[report_task_f1["lam"] == 0.2].sort_values("fair_quality_score", ascending=False).iloc[0]["model"])
    print("Top by fair_quality_score (task, BART):", report_task_bart[report_task_bart["lam"] == 0.2].sort_values("fair_quality_score", ascending=False).iloc[0]["model"])
    print("done")


if __name__ == "__main__":
    main()
