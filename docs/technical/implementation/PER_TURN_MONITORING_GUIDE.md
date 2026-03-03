# 分轮监控功能使用指南

## 功能状态

✅ **已实现并测试通过** (2026-03-01)

## 概述

分轮监控功能允许为多轮对话中的每一轮独立监控资源使用情况，从而精确分析每个问题的能耗、时间和资源消耗。

## 功能特点

### 1. 每轮独立监控
- 每轮对话启动独立的资源监控器
- 记录每轮的GPU功耗、CPU使用率、内存占用等
- 保存每轮的详细时间序列数据

### 2. 数据分离保存
- **原始数据**: `experiment_results_raw_{timestamp}.json` - 包含所有详细监控数据
- **汇总数据**: `experiment_results_summary_{timestamp}.json` - 只包含关键指标

### 3. 向后兼容
- 默认关闭分轮监控（`per_turn_monitoring=False`）
- 保留原有的整体监控模式
- 支持新旧配置文件格式

## 使用方法

### 配置文件

在test_cases.json中添加`per_turn_monitoring`参数：

```json
{
  "model": "qwen3:4b",
  "prompts": [
    "问题1",
    "问题2",
    "问题3"
  ],
  "task_type": "qa",
  "keep_context": true,
  "per_turn_monitoring": true,
  "max_tokens": 200,
  "temperature": 0.7
}
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `per_turn_monitoring` | boolean | `false` | 是否启用分轮监控 |
| `prompts` | array | 必需 | 多个提示的列表 |
| `keep_context` | boolean | `false` | 是否保持对话上下文 |

### 运行实验

```bash
conda activate bartscore
python experiments/experiment_runner.py --config data/test/test_cases_per_turn_monitoring.json --output-dir data/test
```

## 数据结构

### 原始数据文件（_raw_）

包含每轮的完整监控数据：

```json
{
  "model": "qwen3:4b",
  "per_turn_monitoring": true,
  "conversation": [
    {
      "turn": 1,
      "prompt": "问题1",
      "response": "回答1",
      "performance": {
        "time_seconds": 5.2,
        "token_count": 50,
        "throughput_tokens_per_sec": 9.6
      },
      "resources": {
        "gpu_energy_j": 125.5,
        "gpu_power_avg_w": 24.1,
        "cpu_percent_avg": 35.2
      },
      "system_metrics_full": {
        "timestamps": [1772349894.27, ...],
        "gpu_power_w": [25.3, 28.5, ...],
        "gpu_util": [45, 67, ...],
        ...
      }
    },
    {
      "turn": 2,
      ...
    }
  ],
  "performance": {
    "total_time_seconds": 12.5,
    "turns": 2,
    "per_turn_summary": [
      {"turn": 1, "time": 5.2, "tokens": 50, "energy": 125.5},
      {"turn": 2, "time": 7.3, "tokens": 70, "energy": 180.2}
    ]
  },
  "resources": {
    "total_gpu_energy_j": 305.7,
    "avg_gpu_power_w": 24.5
  }
}
```

### 汇总数据文件（_summary_）

只包含关键指标，不包含详细时间序列：

```json
{
  "model": "qwen3:4b",
  "per_turn_monitoring": true,
  "conversation_summary": [
    {
      "turn": 1,
      "prompt": "问题1（截断）",
      "response": "回答1（截断）",
      "performance": {...},
      "resources": {...}
    }
  ],
  "performance": {...},
  "resources": {...}
}
```

## 数据分析

### 查看每轮能耗

```python
import json

with open('experiment_results_raw_20260301_150000.json', 'r') as f:
    results = json.load(f)

for exp in results:
    if exp.get('per_turn_monitoring'):
        print(f"模型: {exp['model']}")
        for turn in exp['conversation']:
            print(f"  轮次{turn['turn']}: {turn['resources']['gpu_energy_j']:.2f} J")
```

### 对比不同问题的复杂度

```python
for exp in results:
    if exp.get('per_turn_monitoring'):
        for turn in exp['conversation']:
            perf = turn['performance']
            print(f"轮次{turn['turn']}: {perf['time_seconds']:.2f}秒, "
                  f"{perf['token_count']} tokens, "
                  f"{perf['throughput_tokens_per_sec']:.2f} tokens/s")
```

### 可视化每轮的GPU功耗曲线

```python
import matplotlib.pyplot as plt

for turn in exp['conversation']:
    metrics = turn['system_metrics_full']
    plt.plot(metrics['timestamps'], metrics['gpu_power_w'], 
             label=f"Turn {turn['turn']}")

plt.xlabel('Time (s)')
plt.ylabel('GPU Power (W)')
plt.legend()
plt.show()
```

## 性能考虑

### 监控器开销

- 每轮启停监控器约0.5秒
- 3轮对话增加约1.5秒总时间
- 对于长时间运行的实验，开销可忽略

### 文件大小

- 原始数据文件较大（包含详细时间序列）
- 汇总数据文件较小（只包含关键指标）
- 建议定期清理旧的原始数据文件

### 内存占用

- 每轮保存独立的监控数据
- 多轮对话会增加内存占用
- 建议单次实验不超过10轮

## 对比：整体监控 vs 分轮监控

| 特性 | 整体监控 | 分轮监控 |
|------|----------|----------|
| 数据粒度 | 整体汇总 | 每轮独立 |
| 能耗分析 | 总能耗 | 每轮能耗 |
| 时间分析 | 总时间 | 每轮时间 |
| 文件大小 | 较小 | 较大 |
| 监控开销 | 无 | 每轮0.5秒 |
| 适用场景 | 快速评估 | 详细分析 |

## 使用建议

### 何时使用分轮监控

1. **研究不同问题的复杂度**: 分析哪些问题更耗时/耗能
2. **优化提示词**: 对比不同提示词的效率
3. **模型对比**: 精确对比不同模型在各个问题上的表现
4. **能耗分析**: 详细分析每个问题的能耗分布

### 何时使用整体监控

1. **快速评估**: 只需要整体性能指标
2. **大批量实验**: 减少文件大小和处理时间
3. **单轮对话**: 没有必要分轮监控

## 示例配置

### 示例1：详细分析（分轮监控）

```json
{
  "model": "qwen3:4b",
  "prompts": [
    "简单问题：1+1=?",
    "中等问题：解释牛顿第一定律",
    "复杂问题：分析量子力学的哲学意义"
  ],
  "task_type": "qa",
  "keep_context": false,
  "per_turn_monitoring": true,
  "max_tokens": 500
}
```

### 示例2：快速评估（整体监控）

```json
{
  "model": "gemma3:4b",
  "prompts": ["写一篇关于AI的文章"],
  "task_type": "creative",
  "per_turn_monitoring": false,
  "max_tokens": 1000
}
```

## 常见问题

### Q1: 分轮监控会影响实验结果吗？

**A**: 监控器启停有约0.5秒开销，但不影响模型推理本身。能耗和时间测量仍然准确。

### Q2: 可以混合使用两种监控模式吗？

**A**: 可以！在同一个配置文件中，不同的测试用例可以使用不同的监控模式。

### Q3: 原始数据文件太大怎么办？

**A**: 
1. 使用汇总数据文件进行日常分析
2. 只在需要详细分析时查看原始数据
3. 定期清理旧的原始数据文件

### Q4: 如何从原始数据提取汇总？

**A**: 汇总文件会自动生成。如果需要重新生成，可以使用：

```python
from experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner()
with open('raw_file.json', 'r') as f:
    results = json.load(f)
runner._generate_summary_file(results, 'summary_file.json')
```

## 相关文档

- [多轮对话功能指南](./MULTI_TURN_CONVERSATION_GUIDE.md)
- [实验运行器文档](../experiments/experiment_runner.py)
- [监控数据可视化](../data/test/监控数据可视化说明.md)
