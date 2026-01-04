import os
import sys
import math
from typing import List, Tuple, Dict


def _safe_positive(values: List[float], eps: float = 1e-6) -> List[float]:
    m = min(values)
    shift = -m + eps if m <= 0 else 0.0
    return [v + shift for v in values]


def gini(values: List[float]) -> float:
    vals = _safe_positive(values)
    n = len(vals)
    if n == 0:
        return 0.0
    vals.sort()
    cum = 0.0
    for i, v in enumerate(vals, start=1):
        cum += (2 * i - n - 1) * v
    mu = sum(vals) / n
    if mu == 0:
        return 0.0
    return abs(cum) / (n * n * mu)


def theil(values: List[float]) -> float:
    vals = _safe_positive(values)
    n = len(vals)
    if n == 0:
        return 0.0
    mu = sum(vals) / n
    t = 0.0
    for v in vals:
        r = v / mu if mu > 0 else 0.0
        t += r * math.log(r + 1e-12)
    return t / n


def fairness_gap(group_means: Dict[str, float], global_mean: float) -> float:
    return max(abs(m - global_mean) for m in group_means.values()) if group_means else 0.0


def nsw(group_means: Dict[str, float], eps: float = 1e-6) -> float:
    return sum(math.log(eps + m) for m in group_means.values())


def normalize(values: List[float]) -> List[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi - lo < 1e-12:
        return [0.5 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def compute_fairness_scores(data: List[Tuple[str, float]], lam: float = 0.2) -> Dict[str, float]:
    groups: Dict[str, List[float]] = {}
    for g, q in data:
        groups.setdefault(g, []).append(q)
    all_vals = [q for _, q in data]
    norm_vals = normalize(all_vals)
    idx = 0
    norm_groups: Dict[str, List[float]] = {}
    for g, qs in groups.items():
        k = len(qs)
        norm_groups[g] = norm_vals[idx : idx + k]
        idx += k
    group_means = {g: (sum(vs) / len(vs) if vs else 0.0) for g, vs in norm_groups.items()}
    global_mean = sum(sum(vs) for vs in norm_groups.values()) / len(norm_vals) if norm_vals else 0.0
    fg = fairness_gap(group_means, global_mean)
    g = gini(norm_vals)
    t = theil(norm_vals)
    w = nsw(group_means)
    fair_score = global_mean * (1.0 - lam * fg)
    return {
        "global_mean": global_mean,
        "fairness_gap": fg,
        "gini": g,
        "theil": t,
        "nsw": w,
        "fair_quality_score": fair_score,
    }


def fair_quality_scoring_demo() -> bool:
    sample = [
        ("code", 0.95), ("code", 0.88), ("code", 0.91),
        ("creative", 0.72), ("creative", 0.68), ("creative", 0.73),
        ("qa", 0.90), ("qa", 0.87), ("qa", 0.89),
        ("summary", 0.80), ("summary", 0.78), ("summary", 0.77),
    ]
    scores = compute_fairness_scores(sample, lam=0.2)
    print("Fairness scoring demo")
    for k, v in scores.items():
        print(k, "=", float(v))
    ok = scores["global_mean"] > 0 and scores["fair_quality_score"] > 0
    return bool(ok)


def trf_readiness_check() -> bool:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Towards-Reward-Fairness"))
    dpo_dir = os.path.join(base, "Fair-DPO")
    rm_dir = os.path.join(base, "Fair-RM")
    dpo_files = [
        os.path.join(dpo_dir, "dpo_launch.sh"),
        os.path.join(dpo_dir, "launch.py"),
        os.path.join(dpo_dir, "accelerate_config", "fsdp_4gpu.yaml"),
    ]
    rm_files = [
        os.path.join(rm_dir, "run_llama3.sh"),
        os.path.join(rm_dir, "llama3_8B_rm.py"),
    ]
    for p in dpo_files + rm_files:
        if not os.path.exists(p):
            print("Missing", p)
            return False
    try:
        import accelerate  # noqa
        import torch  # noqa
        print("Core deps ok", accelerate.__version__, torch.__version__)
    except Exception as e:
        print("Core deps error", str(e))
        return False
    try:
        win_path = os.path.join(dpo_dir, "dpo_launch.sh")
        drive = win_path[0].lower()
        wsl_path = "/mnt/" + drive + win_path[2:].replace("\\", "/")
        import subprocess
        r = subprocess.run(["wsl", "-e", "bash", "-lc", f"bash -n '{wsl_path}' && echo OK"], capture_output=True, text=True)
        if r.returncode != 0:
            print("WSL bash check failed", r.stderr.strip())
            return False
        print("WSL bash check", r.stdout.strip())
    except Exception as e:
        print("WSL check error", str(e))
        return False
    return True


def main() -> int:
    a = fair_quality_scoring_demo()
    b = trf_readiness_check()
    print("demo_ok", a)
    print("trf_ok", b)
    return 0 if (a and b) else 1


if __name__ == "__main__":
    sys.exit(main())
