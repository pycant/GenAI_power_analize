# 数据结构对比：当前 vs 目标

## 概览

本文档对比当前实现的数据结构与设计文档要求的完整数据结构，便于快速识别缺失字段。

## 1. results.csv 字段对比

### 当前字段 (已实现)

```csv
model,task,run,prompt,response,bartscore,
toks_per_s,latency_s,gpu_energy_j,
cpu_percent_avg,gpu_util_avg,gpu_mem_peak_mb,
first_token_time,decode_time,
prompt_tokens,output_tokens,total_tokens,tpot
```

### 目标字段 (完整版)

```csv
# === 基本信息 ===
model,task,run,prompt,response,

# === 质量指标 ===
bartscore,rouge1,rouge2,rougeL,bertscore_f1,
accuracy,distinct_1,distinct_2,
code_compiles,code_correct,

# === 时间指标 ===
latency_s,first_token_time,decode_time,tpot,

# === Token统计 ===
prompt_tokens,output_tokens,total_tokens,

# === 吞吐指标 ===
toks_per_s,PPW,TPJ,

# === 功耗指标 ===
P_idle,P_avg,P_peak,P_inc,P_prefill,P_decode,

# === 能耗指标 ===
gpu_energy_j,cpu_energy_j,E_total,E_token,
E_prefill,E_decode,E_inc,

# === 系统指标 ===
cpu_percent_avg,cpu_percent_peak,
gpu_util_avg,gpu_util_peak,
gpu_mem_peak_mb,gpu_temp_peak_c,
mem_used_peak_mb,

# === 成本指标 ===
Cost_GPU,Cost_energy,CPQ,CPT,

# === 归一化指标 (在分析阶段计算) ===
norm_quality,norm_energy,norm_latency,norm_power,norm_throughput
```

### 缺失字段清单

#### 高优先级
- `rouge1`, `rouge2`, `rougeL` - ROUGE分数
- `accuracy` - QA准确率
- `P_idle` - 空闲基线功耗
- `P_inc` - 增量功耗
- `E_token` - 每token能耗
- `PPW` - 每瓦性能 (tokens/s/W)
- `TPJ` - 能效比 (tokens/J)

#### 中优先级
- `bertscore_f1` - BERTScore F1分数
- `distinct_1` - Distinct-1 (需标准化)
- `P_prefill`, `P_decode` - 阶段功耗
- `E_prefill`, `E_decode` - 阶段能耗
- `E_inc` - 增量能耗
- `norm_power` - 归一化功耗

#### 低优先级
- `code_correct` - 代码正确性
- `Cost_GPU`, `Cost_energy` - 成本指标
- `CPQ`, `CPT` - 每质量点/token成本

## 2. 监控数据结构对比

### 当前结构 (monitor.to_dict())

```python
{
    "timestamps": [...],
    "cpu_percent": [...],
    "cpu_proc_percent": [...],
    "mem_used_mb": [...],
    "disk_read_bytes": [...],
    "disk_write_bytes": [...],
    "gpu_util": [...],
    "gpu_mem_mb": [...],
    "gpu_power_w": [...],
    "gpu_temp_c": [...],
    "gpu_processes": [...],
    "gpu_energy_j": float,
    "cpu_power_w_approx": [...],
    "cpu_energy_j_approx": float,
    "events": [
        {"timestamp": float, "event": str, "metadata": dict}
    ],
    "summary": {
        "cpu_percent_avg": float,
        "cpu_percent_peak": float,
        "mem_used_peak_mb": float,
        "gpu_util_avg": float,
        "gpu_util_peak": float,
        "gpu_mem_peak_mb": float,
        "gpu_power_avg_w": float,
        "gpu_energy_j": float,
        "gpu_temp_peak_c": float,
        "cpu_energy_j_approx": float
    }
}
```

### 目标结构 (增强版)

```python
{
    # ... 现有字段 ...
    
    "baseline": {  # 新增：空闲基线
        "duration_s": float,
        "gpu_power_avg_w": float,
        "cpu_percent_avg": float,
        "timestamp_start": float,
        "timestamp_end": float
    },
    
    "phase_analysis": {  # 新增：阶段分析
        "prefill": {
            "duration_seconds": float,
            "gpu_power_avg_w": float,
            "gpu_power_peak_w": float,
            "gpu_energy_j": float,
            "sample_count": int
        },
        "decode": {
            "duration_seconds": float,
            "gpu_power_avg_w": float,
            "gpu_power_peak_w": float,
            "gpu_energy_j": float,
            "sample_count": int
        }
    },
    
    "summary": {
        # ... 现有字段 ...
        "P_idle": float,  # 新增
        "P_inc": float,   # 新增
        "E_inc": float    # 新增
    }
}
```

## 3. 实验结果JSON结构对比

### 当前结构 (raw/*.json)

```json
{
    "model": "qwen3:8b",
    "task": "qa",
    "run": 1,
    "prompt": "...",
    "response": "...",
    "quality": {
        "bartscore": -3.456,
        "creative": {
            "distinct_2": 0.85
        },
        "code": {
            "code_compiles": true
        }
    },
    "performance": {
        "toks_per_s": 45.2,
        "latency_s": 2.5,
        "first_token_time": 0.3,
        "decode_time": 2.2,
        "tpot": 0.022,
        "prompt_tokens": 50,
        "output_tokens": 113,
        "total_tokens": 163
    },
    "monitoring": {
        "timestamps": [...],
        "gpu_power_w": [...],
        "gpu_energy_j": 125.5,
        "cpu_energy_j_approx": 45.2,
        "events": [...],
        "summary": {...}
    }
}
```

### 目标结构 (增强版)

```json
{
    "model": "qwen3:8b",
    "task": "qa",
    "run": 1,
    "prompt": "...",
    "response": "...",
    
    "quality": {
        "bartscore": -3.456,
        "rouge": {  // 新增
            "rouge1": 0.45,
            "rouge2": 0.32,
            "rougeL": 0.41
        },
        "bertscore_f1": 0.88,  // 新增
        "accuracy": 1.0,  // 新增 (QA任务)
        "creative": {
            "distinct_1": 0.92,  // 新增
            "distinct_2": 0.85
        },
        "code": {
            "code_compiles": true,
            "code_correct": true  // 新增
        }
    },
    
    "performance": {
        "toks_per_s": 45.2,
        "latency_s": 2.5,
        "first_token_time": 0.3,
        "decode_time": 2.2,
        "tpot": 0.022,
        "prompt_tokens": 50,
        "output_tokens": 113,
        "total_tokens": 163,
        "PPW": 0.9,  // 新增：每瓦性能
        "TPJ": 0.9   // 新增：能效比
    },
    
    "power": {  // 新增：功耗详情
        "P_idle": 45.0,
        "P_avg": 50.2,
        "P_peak": 65.8,
        "P_inc": 5.2,
        "P_prefill": 62.5,
        "P_decode": 48.3
    },
    
    "energy": {  // 新增：能耗详情
        "E_GPU": 125.5,
        "E_CPU": 45.2,
        "E_total": 170.7,
        "E_token": 1.51,
        "E_prefill": 18.75,
        "E_decode": 106.26,
        "E_inc": 157.7
    },
    
    "cost": {  // 新增：成本分析
        "Cost_GPU": 0.00035,
        "Cost_energy": 0.0000057,
        "CPQ": 0.00035,
        "CPT": 0.0000031
    },
    
    "monitoring": {
        "timestamps": [...],
        "gpu_power_w": [...],
        "gpu_energy_j": 125.5,
        "cpu_energy_j_approx": 45.2,
        "events": [...],
        "baseline": {...},  // 新增
        "phase_analysis": {...},  // 新增
        "summary": {...}
    }
}
```

## 4. 分析数据结构对比 (analysis_data.csv)

### 当前字段

```csv
model,task,run,
tps,latency,energy,quality_raw,
norm_tps,norm_lat,norm_energy,norm_quality,
efficiency_score,qe_ratio
```

### 目标字段

```csv
# === 基本信息 ===
model,task,run,

# === 原始指标 ===
tps,latency,energy,power_avg,quality_raw,

# === 归一化指标 ===
norm_tps,norm_lat,norm_energy,norm_power,norm_quality,

# === 复合指标 ===
efficiency_score,qe_ratio,Score_final,

# === 公平性指标 ===
fairness_gap,gini,theil,nsw,fair_quality_score,

# === 成本指标 ===
cost_total,cost_norm,CPQ,CPT
```

## 5. 实施映射表

| 缺失字段 | 数据来源 | 计算位置 | 优先级 |
|---------|---------|---------|--------|
| P_idle | 空闲测量 | experiment_runner.py | 高 |
| P_inc | P_avg - P_idle | experiment_runner.py | 高 |
| E_token | E_total / output_tokens | experiment_runner.py | 高 |
| PPW | toks_per_s / P_avg | experiment_runner.py | 高 |
| TPJ | output_tokens / E_total | experiment_runner.py | 高 |
| rouge* | ROUGE评估 | quality.py | 高 |
| accuracy | 答案匹配 | quality.py | 高 |
| bertscore_f1 | BERTScore | quality.py | 中 |
| P_prefill | phase_analysis | experiment_runner.py | 中 |
| P_decode | phase_analysis | experiment_runner.py | 中 |
| E_prefill | phase_analysis | experiment_runner.py | 中 |
| E_decode | phase_analysis | experiment_runner.py | 中 |
| Score_final | 加权综合 | analyze_experiments_1.py | 中 |
| Cost_* | 成本模型 | analyze_experiments_1.py | 低 |

## 6. 代码修改清单

### experiment_runner.py
```python
# 1. 添加空闲基线测量
def measure_baseline(monitor, duration=10):
    monitor.start()
    time.sleep(duration)
    monitor.mark_event("baseline_end")
    baseline = monitor.get_phase_data("experiment_start", "baseline_end")
    return baseline['gpu_power_avg_w']

# 2. 计算衍生指标
result['P_idle'] = P_idle
result['P_inc'] = result['gpu_power_avg_w'] - P_idle
result['E_token'] = result['gpu_energy_j'] / result['output_tokens']
result['PPW'] = result['toks_per_s'] / result['gpu_power_avg_w']
result['TPJ'] = result['output_tokens'] / result['gpu_energy_j']

# 3. 添加阶段分析
prefill_data = monitor.get_phase_data("inference_start", "first_token")
decode_data = monitor.get_phase_data("first_token", "inference_end")
result['phase_analysis'] = {
    'prefill': prefill_data,
    'decode': decode_data
}
```

### quality.py
```python
# 1. 添加ROUGE评估
from rouge_score import rouge_scorer

def rouge_scores(reference, hypothesis):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference, hypothesis)
    return {
        'rouge1': scores['rouge1'].fmeasure,
        'rouge2': scores['rouge2'].fmeasure,
        'rougeL': scores['rougeL'].fmeasure
    }

# 2. 添加准确率计算
def qa_accuracy(reference, hypothesis, method='exact_match'):
    if method == 'exact_match':
        return 1.0 if reference.strip().lower() == hypothesis.strip().lower() else 0.0
    elif method == 'contains':
        return 1.0 if reference.strip().lower() in hypothesis.strip().lower() else 0.0

# 3. 添加BERTScore (可选)
from bert_score import score

def bertscore_batch(references, hypotheses, lang='en'):
    P, R, F1 = score(hypotheses, references, lang=lang, verbose=False)
    return F1.tolist()
```

### analyze_experiments_1.py
```python
# 1. 添加成本计算
GPU_COST_PER_HOUR = 0.5  # $/h
ENERGY_COST_PER_KWH = 0.12  # $/kWh

df['Cost_GPU'] = (df['latency_s'] / 3600) * GPU_COST_PER_HOUR
df['Cost_energy'] = (df['gpu_energy_j'] / 3600000) * ENERGY_COST_PER_KWH
df['cost_total'] = df['Cost_GPU'] + df['Cost_energy']
df['CPQ'] = df['cost_total'] / df['quality_raw']
df['CPT'] = df['cost_total'] / df['output_tokens']

# 2. 添加功耗归一化
df['norm_power'] = df.groupby('task')['gpu_power_avg_w'].transform(
    lambda x: (x - x.min()) / (x.max() - x.min())
)

# 3. 计算最终综合分
w_qe, w_fair, w_cost = 0.4, 0.3, 0.3
df['Score_final'] = (
    w_qe * df['qe_ratio_norm'] +
    w_fair * (1 - df['fairness_gap']) +
    w_cost * (1 - df['cost_norm'])
)
```

## 7. 测试验证清单

- [ ] 验证 P_idle 测量准确性
- [ ] 验证 E_token 计算正确性
- [ ] 验证 PPW 和 TPJ 计算
- [ ] 验证 ROUGE 分数合理性
- [ ] 验证准确率计算逻辑
- [ ] 验证阶段能耗分析
- [ ] 验证成本计算
- [ ] 验证向后兼容性
- [ ] 验证 CSV 导出完整性
- [ ] 验证报告生成正确性

## 相关文档

- [详细缺口分析](./DATA_COLLECTION_GAP_ANALYSIS.md)
- [实施优先级清单](./IMPLEMENTATION_PRIORITY.md)
- [实验设计文档](./experiment/experiment_design.md)

---

**版本**: v1.0  
**创建时间**: 2026-03-02
