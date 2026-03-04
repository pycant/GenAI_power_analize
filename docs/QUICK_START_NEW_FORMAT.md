# 新数据格式快速入门

## 概述

从v2.0开始，实验结果被分离为两个文件：
- **Raw文件**: 原始监控数据（完整时间序列）
- **Summary文件**: 汇总统计和派生指标

## 快速开始

### 1. 运行单个实验

```python
from experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner(output_dir="data/experiments_5")

result = runner.run_single_experiment(
    model="ollama:qwen3:4b",
    prompts=["什么是Python？"],
    task_type="qa",
    max_tokens=100,
    temperature=0.7,
    idle_measurement_duration=10  # 测量10秒空闲基线
)

# 获取数据
raw_data = result.get_raw_data()
summary_data = result.get_summary_data()
```

### 2. 运行多轮对话（分轮监控）

```python
result = runner.run_single_experiment(
    model="ollama:qwen3:4b",
    prompts=[
        "什么是机器学习？",
        "它有哪些应用？",
        "如何入门？"
    ],
    task_type="qa",
    max_tokens=100,
    temperature=0.7,
    keep_context=True,              # 保持对话上下文
    per_turn_monitoring=True,       # 每轮独立监控
    idle_measurement_duration=10
)
```

### 3. 运行实验套件

```python
test_cases = [
    {
        "model": "ollama:qwen3:4b",
        "prompts": ["什么是深度学习？"],
        "task_type": "qa",
        "max_tokens": 100,
        "idle_measurement_duration": 10
    },
    {
        "model": "ollama:gemma3:4b",
        "prompts": ["解释神经网络"],
        "task_type": "qa",
        "max_tokens": 100,
        "idle_measurement_duration": 10
    }
]

raw_results, summary_results = runner.run_experiment_suite(
    test_cases,
    output_file="data/experiments_5/results"
)

# 结果自动保存到:
# - data/experiments_5/results_raw.json
# - data/experiments_5/results_summary.json
```

## 数据访问

### 读取Raw数据

```python
import json

with open("experiment_results_20260302_165811_raw.json", "r") as f:
    raw_data = json.load(f)

# 访问完整时间序列
timestamps = raw_data["monitoring_data"]["measurements"]["timestamps"]
gpu_power = raw_data["monitoring_data"]["measurements"]["gpu_power_w"]

# 访问事件
events = raw_data["monitoring_data"]["events"]
for event in events:
    print(f"{event['timestamp']}: {event['event']}")

# 访问对话
for turn in raw_data["conversation"]:
    print(f"轮次 {turn['turn']}: {turn['prompt']}")
    print(f"回答: {turn['response']}")
    
    # 如果启用了分轮监控
    if "monitoring_data" in turn:
        turn_power = turn["monitoring_data"]["measurements"]["gpu_power_w"]
        print(f"该轮GPU功耗: {turn_power}")
```

### 读取Summary数据

```python
import json

with open("experiment_results_20260302_165811_summary.json", "r") as f:
    summary_data = json.load(f)

# 访问性能指标
performance = summary_data["performance"]
print(f"吞吐量: {performance['throughput_tokens_per_sec']:.2f} tokens/s")
print(f"总时间: {performance['total_time_seconds']:.2f}秒")
print(f"TTFT: {performance['ttft_seconds']:.3f}秒")

# 访问资源指标
resources = summary_data["resources"]
print(f"平均GPU功耗: {resources['gpu_power_avg_w']:.2f} W")
print(f"GPU能耗: {resources['gpu_energy_j']:.2f} J")

# 访问派生指标
derived = summary_data["derived_metrics"]
print(f"空闲功耗: {derived['P_idle']:.2f} W")
print(f"增量功耗: {derived['P_inc']:.2f} W")
print(f"每token能耗: {derived['E_token']:.4f} J/token")
print(f"能效比: {derived['TPJ']:.2f} tokens/J")

# 访问质量指标
quality = summary_data["quality"]
if quality["bartscore"]:
    print(f"BARTScore: {quality['bartscore']:.4f}")

# 访问对话摘要
for turn_summary in summary_data["conversation_summary"]:
    print(f"轮次 {turn_summary['turn']}: {turn_summary['tokens']} tokens")
    if "throughput" in turn_summary:
        print(f"  吞吐量: {turn_summary['throughput']:.2f} tokens/s")
```

## 数据分析示例

### 绘制功耗曲线

```python
import matplotlib.pyplot as plt
import json

with open("experiment_results_20260302_165811_raw.json", "r") as f:
    raw_data = json.load(f)

timestamps = raw_data["monitoring_data"]["measurements"]["timestamps"]
gpu_power = raw_data["monitoring_data"]["measurements"]["gpu_power_w"]

# 转换为相对时间
start_time = timestamps[0]
relative_times = [(t - start_time) for t in timestamps]

plt.figure(figsize=(12, 6))
plt.plot(relative_times, gpu_power, label="GPU功耗")
plt.xlabel("时间 (秒)")
plt.ylabel("功耗 (W)")
plt.title("GPU功耗随时间变化")
plt.grid(True)
plt.legend()
plt.savefig("gpu_power_curve.png")
```

### 对比多个模型

```python
import json
import pandas as pd

# 读取summary文件
with open("results_summary.json", "r") as f:
    summary_results = json.load(f)

# 提取关键指标
data = []
for result in summary_results:
    data.append({
        "model": result["config_ref"]["model"],
        "throughput": result["performance"]["throughput_tokens_per_sec"],
        "gpu_energy": result["resources"]["gpu_energy_j"],
        "E_token": result["derived_metrics"].get("E_token", 0),
        "TPJ": result["derived_metrics"].get("TPJ", 0)
    })

df = pd.DataFrame(data)
print(df)

# 绘制对比图
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

df.plot(x="model", y="throughput", kind="bar", ax=axes[0, 0], title="吞吐量对比")
df.plot(x="model", y="gpu_energy", kind="bar", ax=axes[0, 1], title="GPU能耗对比")
df.plot(x="model", y="E_token", kind="bar", ax=axes[1, 0], title="每token能耗对比")
df.plot(x="model", y="TPJ", kind="bar", ax=axes[1, 1], title="能效比对比")

plt.tight_layout()
plt.savefig("model_comparison.png")
```

## 常见问题

### Q: 如何只读取summary数据？

A: Summary文件包含所有汇总指标，通常足够用于分析。只有需要完整时间序列或详细事件时才需要读取raw文件。

### Q: 分轮监控数据在哪里？

A: 如果启用了 `per_turn_monitoring=True`，每轮的监控数据保存在：
- Raw文件: `conversation[i]["monitoring_data"]`
- Summary文件: `conversation_summary[i]` 包含该轮的汇总指标

### Q: 如何计算自定义指标？

A: 从raw文件读取完整时间序列数据，然后进行自定义计算：

```python
import numpy as np

# 读取raw数据
with open("experiment_results_raw.json", "r") as f:
    raw_data = json.load(f)

# 获取时间序列
timestamps = raw_data["monitoring_data"]["measurements"]["timestamps"]
gpu_power = raw_data["monitoring_data"]["measurements"]["gpu_power_w"]

# 计算自定义指标
power_variance = np.var(gpu_power)
power_95th_percentile = np.percentile(gpu_power, 95)

print(f"功耗方差: {power_variance:.2f}")
print(f"95分位功耗: {power_95th_percentile:.2f} W")
```

### Q: 如何转换旧格式数据？

A: 可以创建转换脚本（参考 `docs/REFACTORING_IMPLEMENTATION_PLAN.md` 中的转换脚本示例）。

## 测试

运行测试脚本验证新格式：

```bash
python scripts/test_refactored_runner.py
```

## 更多信息

- [完整重构报告](REFACTORING_COMPLETED.md)
- [数据结构设计](DATA_STRUCTURE_REFACTORING.md)
- [实施计划](REFACTORING_IMPLEMENTATION_PLAN.md)

---

**版本**: v2.0  
**更新时间**: 2026-03-02
