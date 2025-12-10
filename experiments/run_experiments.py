import os
import sys
import json
import time
import argparse
from datetime import datetime
import importlib.util
import shutil

def _ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def _next_experiment_index(base_out):
    try:
        names = os.listdir(base_out)
    except Exception:
        return 1
    idx = 1
    for n in names:
        if n.startswith("experiments_"):
            parts = n.split("_")
            try:
                i = int(parts[1])
                idx = max(idx, i + 1)
            except Exception:
                pass
    return idx

def _load_cases(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _validate_cases(cases):
    required = ["model", "prompt", "task_type", "max_tokens", "temperature"]
    problems = []
    for i, c in enumerate(cases):
        for k in required:
            if k not in c or c[k] in (None, ""):
                problems.append(f"case[{i}] missing {k}")
        if c.get("max_tokens", 0) <= 0:
            problems.append(f"case[{i}] invalid max_tokens")
        if not (0 <= float(c.get("temperature", 0.7)) <= 2):
            problems.append(f"case[{i}] invalid temperature")
        m = c.get("model")
        if isinstance(m, list):
            if not m:
                problems.append(f"case[{i}] model list empty")
            else:
                for j, mm in enumerate(m):
                    if not isinstance(mm, str) or not mm.strip():
                        problems.append(f"case[{i}] model[{j}] invalid")
        elif isinstance(m, str):
            if not m.strip():
                problems.append(f"case[{i}] model string empty")
        else:
            problems.append(f"case[{i}] model type invalid")
    return problems

def _load_config_py(path):
    try:
        spec = importlib.util.spec_from_file_location("exp_config", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cfg = {}
        for k in ["TEMPERATURE","TOP_P","NUM_CTX","SEED","KEEPALIVE","WARMUP","RUNS"]:
            if hasattr(mod, k):
                cfg[k.lower()] = getattr(mod, k)
        return cfg
    except Exception:
        return {}

def _ollama_generate_stream(model, prompt, options=None, keep_alive="0s"):
    import requests
    import json as _json
    import time as _time
    url = "http://localhost:11434/api/generate"
    body = {"model": model, "prompt": prompt, "stream": True}
    if options:
        body["options"] = options
    if keep_alive is not None:
        body["keep_alive"] = keep_alive
    r = requests.post(url, json=body, stream=True, timeout=600)
    r.raise_for_status()
    t0 = _time.time()
    t_first = None
    text_parts = []
    final = {}
    for line in r.iter_lines():
        if not line:
            continue
        d = _json.loads(line.decode("utf-8", errors="ignore"))
        resp = d.get("response")
        if resp:
            if t_first is None:
                t_first = _time.time()
            text_parts.append(resp)
        if d.get("done"):
            final = d
            break
    full_text = "".join(text_parts)
    return {
        "response": full_text,
        "first_token_seconds": (t_first - t0) if t_first else None,
        "eval_count": final.get("eval_count"),
        "eval_duration": final.get("eval_duration"),
        "total_duration": final.get("total_duration"),
        "load_duration": final.get("load_duration"),
        "prompt_eval_duration": final.get("prompt_eval_duration")
    }

def _model_info(model):
    import subprocess
    try:
        p = subprocess.run(["ollama", "show", model], capture_output=True, text=False, timeout=15)
        if p.returncode == 0:
            try:
                txt = p.stdout.decode("utf-8", errors="ignore")
            except Exception:
                txt = ""
            return {"raw": txt}
    except Exception:
        return {}
    return {}

def _model_details_from_tags(model):
    import requests
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=10)
        r.raise_for_status()
        data = r.json().get("models", [])
        for m in data:
            if m.get("name") == model or m.get("model") == model:
                d = m.get("details", {})
                return {
                    "digest": m.get("digest"),
                    "parameter_size": d.get("parameter_size"),
                    "quantization_level": d.get("quantization_level"),
                    "family": d.get("family"),
                    "families": d.get("families")
                }
    except Exception:
        return {}
    return {}

def _installed_models():
    import requests
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=10)
        r.raise_for_status()
        data = r.json().get("models", [])
        return [m.get("name") or m.get("model") for m in data if (m.get("name") or m.get("model"))]
    except Exception:
        return []

def _resolve_case_models(m):
    if isinstance(m, list):
        return [x for x in m if isinstance(x, str) and x.strip()]
    if isinstance(m, str):
        if m.strip().lower() == "all":
            return _installed_models()
        return [m]
    return []

def _distinct_metrics(text):
    import re
    toks = re.findall(r"\S+", text)
    def ngrams(n):
        return [tuple(toks[i:i+n]) for i in range(len(toks)-n+1)]
    def distinct(n):
        ng = ngrams(n)
        return (len(set(ng))/len(ng)) if ng else 0.0
    return {"distinct_1": distinct(1), "distinct_2": distinct(2), "distinct_3": distinct(3), "length_tokens": len(toks)}

def _extract_python_code(text):
    import re
    m = re.search(r"```python\s*(.*?)```", text, re.S|re.I)
    if m:
        return m.group(1)
    m = re.search(r"```\s*(.*?)```", text, re.S)
    if m:
        return m.group(1)
    return ""

def _code_quality_metrics(text):
    import ast
    code = _extract_python_code(text)
    compiles = False
    try:
        if code:
            ast.parse(code)
            compiles = True
    except Exception:
        compiles = False
    has_bs = ("binary_search" in code) or ("二分" in text)
    mentions_complex = ("O(log" in text) or ("log n" in text) or ("logn" in text) or ("时间复杂度" in text)
    return {"code_compiles": compiles, "has_binary_search_symbol": has_bs, "mentions_complexity": mentions_complex}

def _bartscore_optional(reference, hypothesis):
    try:
        from experiments.quality import bartscore_single
        return bartscore_single(reference, hypothesis, device="cuda") if reference else None
    except Exception:
        return None

def _case_id(task, load, run_idx):
    return f"{task}_{load}_r{run_idx}"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["llama3.2:3b", "llama3.2:11b", "gemma2:9b"])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--out", default="data")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top_p", type=float, default=0.9)
    parser.add_argument("--num_ctx", type=int, default=4096)
    parser.add_argument("--max_tokens", type=int, default=512)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--warmup", action="store_true")
    parser.add_argument("--keepalive", default="0s")
    parser.add_argument("--tasks", nargs="+", choices=["qa","summary","code","creative"])
    parser.add_argument("--loads", nargs="+", choices=["short","medium","long"])
    parser.add_argument("--exp-dir")
    parser.add_argument("--cases-file")
    parser.add_argument("--exp-config")
    parser.add_argument("--use-default-on-error", action="store_true")
    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.exp_dir:
        base_dir = args.exp_dir
    else:
        _ensure_dir(args.out)
        idx = _next_experiment_index(args.out)
        base_dir = os.path.join(args.out, f"experiments_{idx}_{timestamp}")
    _ensure_dir(base_dir)
    raw_base = os.path.join(base_dir, "raw")
    txt_base = os.path.join(base_dir, "texts")
    sum_base = os.path.join(base_dir, "summary")
    _ensure_dir(raw_base)
    _ensure_dir(txt_base)
    _ensure_dir(sum_base)
    summary_path = os.path.join(sum_base, "results.csv")

    tasks = {
        "qa": {
            "prompt": "请解释牛顿第一定律。",
            "reference": "牛顿第一定律也称惯性定律,当物体所受合外力为零时,静止保持静止,运动保持匀速直线运动。"
        },
        "summary": {
            "prompt": "请阅读并总结以下文本,给出200字摘要: 牛顿第一定律描述了物体在不受外力作用时的运动状态,强调惯性的概念。",
            "reference": "该定律表明无外力时物体保持原有状态,体现惯性。"
        },
        "code": {
            "prompt": "请用Python实现二分查找并解释时间复杂度。",
            "reference": None
        },
        "creative": {
            "prompt": "以\"人工智能与未来社会\"为题写一段约300字短文。",
            "reference": None
        }
    }

    loads = {
        "short": {"max_tokens": min(128, args.max_tokens)},
        "medium": {"max_tokens": min(256, args.max_tokens)},
        "long": {"max_tokens": args.max_tokens}
    }

    if args.tasks:
        tasks = {k:v for k,v in tasks.items() if k in set(args.tasks)}
    if args.loads:
        loads = {k:v for k,v in loads.items() if k in set(args.loads)}

    cfg_override = {}
    if args.exp_dir and not args.exp_config:
        p = os.path.join(args.exp_dir, "config.py")
        if os.path.exists(p):
            args.exp_config = p
    if args.exp_config:
        cfg_override = _load_config_py(args.exp_config)
        if "temperature" in cfg_override:
            args.temperature = cfg_override["temperature"]
        if "top_p" in cfg_override:
            args.top_p = cfg_override["top_p"]
        if "num_ctx" in cfg_override:
            args.num_ctx = cfg_override["num_ctx"]
        if "seed" in cfg_override:
            args.seed = cfg_override["seed"]
        if "keepalive" in cfg_override:
            args.keepalive = cfg_override["keepalive"]
        if "warmup" in cfg_override:
            args.warmup = bool(cfg_override["warmup"]) 
        if "runs" in cfg_override:
            args.runs = int(cfg_override["runs"])

    cases = None
    if args.exp_dir and not args.cases_file:
        p = os.path.join(args.exp_dir, "test_cases.json")
        if os.path.exists(p):
            args.cases_file = p
    if args.cases_file:
        try:
            cases = _load_cases(args.cases_file)
            problems = _validate_cases(cases)
            if problems:
                if args.use_default_on_error:
                    print("参数验证失败,使用默认任务配置:", "; ".join(problems))
                    cases = None
                else:
                    print("参数验证失败:", "; ".join(problems))
                    return 2
        except Exception as e:
            if args.use_default_on_error:
                print("读取用例失败,使用默认任务配置:", str(e))
                cases = None
            else:
                print("读取用例失败:", str(e))
                return 2

    if args.dry_run:
        print("准备运行模型:", args.models)
        print("任务:", list(tasks.keys()))
        print("负载层级:", list(loads.keys()))
        print("重复次数:", args.runs)
        print("输出目录:", base_dir)
        if args.cases_file:
            print("用例文件:", args.cases_file)
        if args.exp_config:
            print("配置文件:", args.exp_config)
        return 0

    from experiments.monitor import ResourceMonitor

    rows = []
    # 保存配置快照
    try:
        with open(os.path.join(base_dir, "config.json"), "w", encoding="utf-8") as cf:
            json.dump({
                "timestamp": timestamp,
                "args": {
                    "models": args.models,
                    "runs": args.runs,
                    "temperature": args.temperature,
                    "top_p": args.top_p,
                    "num_ctx": args.num_ctx,
                    "max_tokens": args.max_tokens,
                    "seed": args.seed,
                    "warmup": bool(args.warmup),
                    "keepalive": args.keepalive
                },
                "exp_config_path": args.exp_config,
                "cases_file": args.cases_file
            }, cf, ensure_ascii=False, indent=2)
        if args.cases_file:
            shutil.copy2(args.cases_file, os.path.join(base_dir, "test_cases.json"))
        if args.exp_config:
            shutil.copy2(args.exp_config, os.path.join(base_dir, "config.py"))
    except Exception:
        pass

    def _run_case(model, prompt, task_name, ref_text, max_toks, run_idx):
        minfo = _model_info(model)
        mdetails = _model_details_from_tags(model)
        if args.warmup:
            try:
                _ = _ollama_generate_stream(model, prompt, options={"num_ctx": max(512, args.num_ctx//2), "max_tokens": 16, "temperature": args.temperature, "top_p": args.top_p, "seed": args.seed}, keep_alive=args.keepalive)
            except Exception:
                pass
        case_opts = {
            "temperature": args.temperature,
            "top_p": args.top_p,
            "num_ctx": args.num_ctx,
            "max_tokens": max_toks,
            "seed": args.seed
        }
        mon = ResourceMonitor(interval=0.2)
        mon.start()
        t0 = time.time()
        try:
            api = _ollama_generate_stream(model, prompt, options=case_opts, keep_alive=args.keepalive)
        except Exception as e:
            msg = str(e).lower()
            if ("out of memory" in msg) or ("500" in msg):
                case_opts["num_ctx"] = max(512, int(case_opts["num_ctx"] * 0.5))
                case_opts["max_tokens"] = max(64, int(case_opts["max_tokens"] * 0.5))
                api = _ollama_generate_stream(model, prompt, options=case_opts, keep_alive=args.keepalive)
            else:
                raise
        t1 = time.time()
        mon.stop()
        gen = api.get("response", "")
        eval_count = api.get("eval_count")
        eval_dur_ns = api.get("eval_duration")
        total_dur_ns = api.get("total_duration")
        load_dur_ns = api.get("load_duration")
        prompt_eval_ns = api.get("prompt_eval_duration")
        tok_per_sec = (eval_count / (eval_dur_ns / 1e9)) if eval_count and eval_dur_ns else None
        first_token_s = api.get("first_token_seconds")
        qscore = _bartscore_optional(ref_text, gen)
        code_q = _code_quality_metrics(gen) if task_name == "code" else None
        creative_q = _distinct_metrics(gen) if task_name == "creative" else None
        raw_dir = os.path.join(raw_base, model.replace(":", "_"))
        txt_dir = os.path.join(txt_base, model.replace(":", "_"))
        _ensure_dir(raw_dir)
        _ensure_dir(txt_dir)
        cid = _case_id(task_name, "custom", run_idx)
        with open(os.path.join(txt_dir, f"{cid}.txt"), "w", encoding="utf-8") as f:
            f.write(gen)
        rec = {
                        "model": model,
                        "prompt": prompt,
                        "generated_text": gen,
                        "latency_seconds": t1 - t0,
                        "throughput_tokens_per_sec": tok_per_sec,
                        "first_token_seconds": first_token_s,
                        "api_metrics": {
                            "eval_count": eval_count,
                            "eval_duration_ns": eval_dur_ns,
                            "total_duration_ns": total_dur_ns,
                            "load_duration_ns": load_dur_ns,
                            "prompt_eval_duration_ns": prompt_eval_ns
                        },
                        "system_metrics_summary": mon.summary(),
                        "system_metrics_full": mon.to_dict(),
                        "quality": {"bartscore": qscore, "code": code_q, "creative": creative_q},
                        "metadata": {
                            "options": case_opts,
                            "timestamp": time.time(),
                            "model_info": minfo,
                            "model_details": mdetails,
                            "warm_run": bool(args.warmup)
                        }
        }
        with open(os.path.join(raw_dir, f"{cid}.json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        rows.append([
            timestamp,
            model,
            task_name,
            "custom",
            run_idx,
            rec["latency_seconds"],
            rec["throughput_tokens_per_sec"] or 0,
            rec["system_metrics_summary"]["gpu_mem_peak_mb"],
            rec["system_metrics_summary"]["gpu_util_avg"],
            rec["system_metrics_summary"]["gpu_energy_j"],
            qscore if qscore is not None else ""
        ])

    if cases:
        def map_task(tt):
            m = {
                "knowledge_qa": "qa",
                "text_summarization": "summary",
                "creative_writing": "creative",
                "code_generation": "code"
            }
            return m.get(tt, "qa")
        ridx = 1
        for c in cases:
            mm = _resolve_case_models(c.get("model"))
            for one in mm:
                _run_case(
                    one,
                    c["prompt"],
                    map_task(c.get("task_type")),
                    c.get("reference_text"),
                    int(c.get("max_tokens", args.max_tokens)),
                    ridx
                )
                ridx += 1
    else:
        for model in args.models:
            minfo = _model_info(model)  # prefetch
            for task_name, task in tasks.items():
                for load_name, load in loads.items():
                    for r in range(1, args.runs + 1):
                        _run_case(model, task["prompt"], task_name, task.get("reference"), load["max_tokens"], r)
    def _write_stats(path, rows):
        from collections import defaultdict
        import math
        grp = defaultdict(list)
        for ts, model, task, load, run, lat, tps, gmem, gutil, gj, bs in rows:
            grp[(model, task, load)].append((lat, tps, gmem, gutil, gj, bs))
        with open(path, "w", encoding="utf-8") as f:
            f.write("model,task,load,count,latency_mean,latency_std,tps_mean,tps_std,gmem_peak_mean,gutil_mean,energy_j_mean,bartscore_mean\n")
            for (model, task, load), vals in grp.items():
                n = len(vals)
                def mean(lst):
                    return sum(lst)/len(lst) if lst else 0
                def std(lst):
                    m = mean(lst)
                    return math.sqrt(sum((x-m)**2 for x in lst)/len(lst)) if lst else 0
                lat = [v[0] for v in vals]
                tps = [v[1] for v in vals]
                gmem = [v[2] for v in vals]
                gutil = [v[3] for v in vals]
                gj = [v[4] for v in vals]
                bs = [float(v[5]) for v in vals if isinstance(v[5], (int, float, str)) and str(v[5]) != ""]
                f.write(
                    ",".join([
                        model, task, load, str(n),
                        str(mean(lat)), str(std(lat)),
                        str(mean(tps)), str(std(tps)),
                        str(mean(gmem)), str(mean(gutil)),
                        str(mean(gj)), str(mean(bs)) if bs else ""
                    ]) + "\n"
                )
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("timestamp,model,task,load,run,latency_s,toks_per_s,gpu_mem_peak_mb,gpu_util_avg,gpu_energy_j,bartscore\n")
        for row in rows:
            f.write(",".join([str(x) for x in row]) + "\n")
    print("汇总写入:", summary_path)
    stats_path = os.path.join(sum_base, "stats.csv")
    _write_stats(stats_path, rows)
    print("统计写入:", stats_path)
    return 0

if __name__ == "__main__":
    sys.exit(main())
