# 空闲基线功耗测量功能说明

## 概述

空闲基线功耗测量功能允许在运行模型推理之前，先测量系统在空闲状态下的功耗，从而计算出模型推理的增量功耗和能耗。这对于准确评估模型的实际能耗非常重要。

## 功能特性

### 1. 空闲基线测量

在实验开始前，系统会：
- 测量指定时长的空闲状态功耗
- 记录平均GPU功耗、CPU利用率、GPU利用率等
- 保存基线数据供后续计算使用

### 2. 增量指标计算

基于空闲基线数据，系统会自动计算：

| 指标 | 符号 | 计算公式 | 说明 |
|------|------|---------|------|
| 空闲功耗 | P_idle | 测量值 | 系统空闲时的平均GPU功耗 |
| 增量功耗 | P_inc | P_avg - P_idle | 模型推理增加的功耗 |
| 增量能耗 | E_inc | E_total - (P_idle × T_total) | 模型推理增加的能耗 |
| 每token能耗 | E_token | E_inc / output_tokens | 每生成一个token的能耗 |
| 每瓦性能 | PPW | throughput / P_avg | 每瓦功耗的吞吐量 |
| 能效比 | TPJ | output_tokens / E_total | 每焦耳能量生成的token数 |

## 使用方法

### 1. 在测试用例JSON中添加参数

在测试用例配置文件中，添加 `idle_measurement_duration` 参数（单位：秒）：

```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
  "prompts": [
    "什么是Python？",
    "它有哪些主要特点？",
    "请给我一个简单的代码示例。"
  ],
  "task_type": "qa",
  "keep_context": true,
  "max_tokens": 150,
  "temperature": 0.5,
  "top_p": 0.9,
  "idle_measurement_duration": 10
}
```

### 2. 参数说明

- **idle_measurement_duration**: 空闲基线测量时长（秒）
  - `0`: 不进行空闲基线测量（默认值）
  - `> 0`: 测量指定秒数的空闲功耗
  - 推荐值: 5-10秒（足够获得稳定的基线数据）

### 3. 运行实验

```bash
# 激活环境
conda activate bartscore

# 运行带空闲基线测量的实验
python experiments/experiment_runner.py --config data/test/test_cases_with_idle_baseline.json --output-dir data/test
```

## 输出结果

### 1. 控制台输出

实验运行时会显示：

```
============================================================
开始实验
  模型: HF:Qwen2.5-7B-Instruct:4bit
  任务: qa
  对话轮数: 3
  保持上下文: 是
  分轮监控: 否
  空闲基线测量: 10 秒
============================================================
  --> 测量空闲基线功耗 (持续 10 秒)...
      请保持系统空闲，不要运行其他程序...
  [OK] 空闲基线测量完成
      平均GPU功耗: 45.23 W
      平均CPU利用率: 5.2%
      平均GPU利用率: 2.1%

  [轮次 1/3]
  提示: 什么是Python？
  ...

  [增量指标]
    空闲功耗 (P_idle): 45.23 W
    增量功耗 (P_inc): 15.67 W
    增量能耗 (E_inc): 125.34 J
    每token能耗 (E_token): 1.1032 J/token
    每瓦性能 (PPW): 0.75 tokens/s/W
    能效比 (TPJ): 0.91 tokens/J
```

### 2. JSON结果文件

结果文件中会包含以下新增字段：

```json
{
  "model": "HF:Qwen2.5-7B-Instruct:4bit",
  "baseline": {
    "duration_seconds": 10,
    "gpu_power_avg_w": 45.23,
    "gpu_power_peak_w": 48.56,
    "gpu_energy_j": 452.3,
    "cpu_percent_avg": 5.2,
    "gpu_util_avg": 2.1,
    "gpu_mem_peak_mb": 1024.5,
    "timestamp": 1709366400.123
  },
  "resources": {
    "P_idle": 45.23,
    "P_inc": 15.67,
    "E_inc": 125.34,
    "E_token": 1.1032,
    "PPW": 0.75,
    "TPJ": 0.91,
    "gpu_power_avg_w": 60.90,
    "gpu_energy_j": 577.64,
    ...
  },
  ...
}
```

## 最佳实践

### 1. 测量时机

- **首次测量**: 在开始实验前进行一次空闲基线测量
- **定期测量**: 如果实验持续时间较长，建议每隔一段时间重新测量
- **环境稳定**: 确保测量时系统处于稳定状态

### 2. 测量时长

| 场景 | 推荐时长 | 说明 |
|------|---------|------|
| 快速测试 | 5秒 | 适合快速验证 |
| 标准实验 | 10秒 | 推荐值，平衡准确性和时间 |
| 精确测量 | 15-30秒 | 获得更稳定的基线数据 |

### 3. 注意事项

1. **保持系统空闲**: 测量期间不要运行其他程序
2. **关闭后台任务**: 关闭不必要的后台程序和服务
3. **稳定电源**: 使用稳定的电源供应
4. **温度稳定**: 等待系统温度稳定后再测量
5. **多次测量**: 对于重要实验，建议多次测量取平均值

## 示例测试用例

### 示例1: 单轮对话 + 空闲基线

```json
{
  "model": "ollama:qwen3:4b",
  "prompts": ["解释一下机器学习的基本概念。"],
  "task_type": "qa",
  "max_tokens": 200,
  "idle_measurement_duration": 10
}
```

### 示例2: 多轮对话 + 空闲基线

```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
  "prompts": [
    "什么是Python？",
    "它有哪些主要特点？",
    "请给我一个简单的代码示例。"
  ],
  "task_type": "qa",
  "keep_context": true,
  "idle_measurement_duration": 10
}
```

### 示例3: 不测量空闲基线（默认行为）

```json
{
  "model": "ollama:gemma3:4b",
  "prompts": ["写一首关于春天的诗。"],
  "task_type": "creative",
  "max_tokens": 150
}
```

## 数据分析

### 1. 使用增量指标

在数据分析时，优先使用增量指标：

```python
import pandas as pd
import json

# 加载结果
with open("experiment_results.json", "r") as f:
    results = json.load(f)

# 提取增量指标
for result in results:
    if "baseline" in result:
        resources = result["resources"]
        print(f"模型: {result['model']}")
        print(f"  增量功耗: {resources['P_inc']:.2f} W")
        print(f"  增量能耗: {resources['E_inc']:.2f} J")
        print(f"  每token能耗: {resources['E_token']:.4f} J/token")
        print(f"  能效比: {resources['TPJ']:.2f} tokens/J")
```

### 2. 对比分析

```python
# 对比不同模型的增量能耗
models_data = []
for result in results:
    if "baseline" in result:
        models_data.append({
            "model": result["model"],
            "P_inc": result["resources"]["P_inc"],
            "E_inc": result["resources"]["E_inc"],
            "E_token": result["resources"]["E_token"],
            "TPJ": result["resources"]["TPJ"]
        })

df = pd.DataFrame(models_data)
print(df.sort_values("E_token"))
```

## 故障排除

### 问题1: 无法测量空闲基线

**症状**: 显示 "高级监控不可用，跳过空闲基线测量"

**解决方案**:
1. 确保已安装 `pynvml`: `pip install pynvml`
2. 确保 NVIDIA 驱动正常工作
3. 检查 `experiments/monitor.py` 是否可用

### 问题2: 空闲功耗异常高

**症状**: P_idle 值异常高（如 >100W）

**解决方案**:
1. 关闭所有不必要的程序
2. 等待系统温度稳定
3. 增加测量时长（如 15-30秒）
4. 检查是否有后台任务在运行

### 问题3: 增量功耗为负值

**症状**: P_inc < 0

**解决方案**:
1. 重新测量空闲基线
2. 确保测量时系统状态一致
3. 检查是否有其他程序影响GPU使用

## 相关文档

- [实施优先级清单](./IMPLEMENTATION_PRIORITY.md)
- [数据采集缺口分析](./DATA_COLLECTION_GAP_ANALYSIS.md)
- [TTFT和Token追踪改进](./TTFT_AND_TOKEN_TRACKING_IMPROVEMENTS.md)
- [实验运行器指南](../experiments/UNIFIED_RUNNER_GUIDE.md)

## 更新日志

### v1.0 (2026-03-02)
- 初始版本
- 实现空闲基线功耗测量
- 自动计算增量指标（P_inc, E_inc, E_token, PPW, TPJ）
- 支持在测试用例JSON中配置测量时长

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**维护者**: Kiro AI Assistant
