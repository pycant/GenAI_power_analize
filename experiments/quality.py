def bartscore_single(reference, hypothesis, device="cuda"):
    try:
        from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
        scorer = BARTScorer(device=device, checkpoint="facebook/bart-large-cnn")
        scores = scorer.score([reference], [hypothesis])
        return scores[0]
    except Exception:
        return None

def bartscore_batch(references, hypotheses, device="cuda"):
    try:
        from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
        scorer = BARTScorer(device=device, checkpoint="facebook/bart-large-cnn")
        return scorer.score(references, hypotheses)
    except Exception:
        return [None for _ in hypotheses]

def _minmax_normalize(values):
    import numpy as np
    arr = np.array(values, dtype=float)
    if arr.size == 0:
        return arr
    lo = float(arr.min())
    hi = float(arr.max())
    if abs(hi - lo) < 1e-12:
        return np.ones_like(arr) * 0.5
    return (arr - lo) / (hi - lo)

def gini(values):
    import numpy as np
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
    import numpy as np
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
    import math
    return float(sum(math.log(eps + m) for m in group_means.values()))

def bartscore_fair_aggregate(df, group_by="task", lam=0.2):
    """
    输入: DataFrame，至少包含列 ['model','task','run','bartscore']
    返回: 每模型的公平化聚合指标结果 DataFrame
    """
    import pandas as pd
    df = df.copy()
    vals = df['bartscore'].fillna(0).values
    df['quality'] = _minmax_normalize(-vals)
    rows = []
    for m in sorted(df['model'].unique()):
        sub = df[df['model'] == m]
        gm = float(sub['quality'].mean()) if len(sub) else 0.0
        if group_by not in sub.columns:
            group_by = "task"
        group_means = {g: float(sub[sub[group_by] == g]['quality'].mean()) for g in sub[group_by].unique()}
        fg = fairness_gap(group_means, gm)
        g = gini(list(sub['quality'].values))
        t = theil(list(sub['quality'].values))
        w = nsw(group_means)
        fair = gm * (1.0 - lam * fg)
        rows.append({
            "model": m,
            "global_mean": gm,
            "fairness_gap": fg,
            "gini": g,
            "theil": t,
            "nsw": w,
            "fair_quality_score": fair
        })
    return pd.DataFrame(rows).sort_values("fair_quality_score", ascending=False)
