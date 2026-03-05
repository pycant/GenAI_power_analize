# 实验结果数据结构文档

本文档介绍实验结果 JSON 文件的数据结构，包括原始数据（raw）和汇总数据（summary）两种格式。

## 文件类型概述

| 文件类型 | 文件名模式 | 用途 |
|---------|-----------|------|
| 原始数据 | `experiment_results_*_raw.json` | 完整的实验记录，包含所有原始测量数据 |
| 汇总数据 | `experiment_results_*_summary.json` | 聚合后的统计指标，便于快速分析 |

## 目录结构

```
data/
├── gemma_2b_hf_4bit/
│   ├── experiment_results_20260303_190201_raw.json      # 原始数据
│   └── experiment_results_20260303_190201_summary.json  # 汇总数据
├── qwen25_7b_hf_4bit/
├── phi3_4b_hf_4bit/
└── ...
```

---

## 汇总数据结构 (summary.json)

汇总文件包含每个实验的聚合统计指标，是数据分析的主要依据。

### 顶级结构

```json
{
  "experiment_id": "exp_20260303_190201_2518223083168",
  "config_ref": { ... },
  "baseline_summary": null,
  "performance": { ... },
  "resources": { ... },
  "derived_metrics": { ... },
  "quality": { ... },
  "conversation_summary": [ ... ],
  "metadata": { ... }
}
```

### 字段详解

#### 1. experiment_id

**类型**: `string`  
**说明**: 实验唯一标识符，格式为 `exp_{timestamp}_{process_id}`

**示例值**:
```json
"exp_20260303_190201_2518223083168"
```

#### 2. config_ref (配置引用)

**类型**: `object`  
**说明**: 实验配置的摘要信息

| 字段 | 类型 | 说明 |
|-----|------|------|
| `model` | string | 模型标识符，格式如 `HF:google--gemma-2b-it:4bit` |
| `task_type` | string | 任务类型（见下方任务类型说明） |
| `prompts_count` | int | 提示词数量 |
| `keep_context` | boolean | 是否保持对话上下文 |
| `per_turn_monitoring` | boolean | 是否启用逐轮监控 |

**示例**:
```json
"config_ref": {
  "model": "HF:google--gemma-2b-it:4bit",
  "task_type": "code",
  "prompts_count": 1,
  "keep_context": false,
  "per_turn_monitoring": false
}
```

#### 3. baseline_summary (基线汇总)

**类型**: `object | null`  
**说明**: 空闲状态基线测量的汇总统计，仅在启用空闲测量时存在

| 字段 | 类型 | 单位 | 说明 |
|-----|------|------|------|
| `duration_seconds` | number | 秒 | 基线测量持续时间 |
| `gpu_power_avg_w` | number | 瓦特 | GPU 平均功率 |
| `gpu_power_peak_w` | number | 瓦特 | GPU 峰值功率 |
| `gpu_power_std_w` | number | 瓦特 | GPU 功率标准差 |
| `gpu_energy_j` | number | 焦耳 | GPU 总能耗 |
| `cpu_percent_avg` | number | % | CPU 平均使用率 |
| `cpu_percent_peak` | number | % | CPU 峰值使用率 |
| `gpu_util_avg` | number | % | GPU 平均利用率 |
| `gpu_util_peak` | number | % | GPU 峰值利用率 |
| `gpu_mem_avg_mb` | number | MB | GPU 显存平均使用量 |
| `gpu_mem_peak_mb` | number | MB | GPU 显存峰值使用量 |
| `gpu_temp_avg_c` | number | °C | GPU 平均温度 |
| `gpu_temp_peak_c` | number | °C | GPU 峰值温度 |

#### 4. performance (性能指标)

**类型**: `object`  
**说明**: 模型推理性能的核心指标

| 字段 | 类型 | 单位 | 说明 |
|-----|------|------|------|
| `total_time_seconds` | number | 秒 | 推理总耗时 |
| `token_count` | int | tokens | 生成的 token 总数 |
| `output_tokens` | int | tokens | 输出 token 数（与 token_count 相同） |
| `throughput_tokens_per_sec` | number | tokens/s | 吞吐量（每秒生成 token 数） |
| `latency_per_token_ms` | number | ms | 每个 token 的延迟 |
| `turns` | int | - | 对话轮次数量 |
| `avg_time_per_turn` | number | 秒 | 每轮平均耗时 |
| `ttft_seconds` | number \| null | 秒 | 首个 token 生成时间（Time To First Token） |

**计算公式**:
- `throughput_tokens_per_sec = token_count / total_time_seconds`
- `latency_per_token_ms = (total_time_seconds * 1000) / token_count`

#### 5. resources (资源使用指标)

**类型**: `object`  
**说明**: 系统资源使用情况的统计

| 字段 | 类型 | 单位 | 说明 |
|-----|------|------|------|
| `cpu_percent_avg` | number | % | CPU 平均使用率 |
| `cpu_percent_peak` | number | % | CPU 峰值使用率 |
| `cpu_percent_std` | number | % | CPU 使用率标准差 |
| `mem_used_avg_mb` | number | MB | 系统内存平均使用量 |
| `mem_used_peak_mb` | number | MB | 系统内存峰值使用量 |
| `gpu_util_avg` | number | % | GPU 平均利用率 |
| `gpu_util_peak` | number | % | GPU 峰值利用率 |
| `gpu_util_std` | number | % | GPU 利用率标准差 |
| `gpu_mem_avg_mb` | number | MB | GPU 显存平均使用量 |
| `gpu_mem_peak_mb` | number | MB | GPU 显存峰值使用量 |
| `gpu_power_avg_w` | number | 瓦特 | GPU 平均功率 |
| `gpu_power_peak_w` | number | 瓦特 | GPU 峰值功率 |
| `gpu_power_std_w` | number | 瓦特 | GPU 功率标准差 |
| `gpu_energy_j` | number | 焦耳 | GPU 总能耗（梯形积分计算） |
| `gpu_temp_avg_c` | number | °C | GPU 平均温度 |
| `gpu_temp_peak_c` | number | °C | GPU 峰值温度 |
| `cpu_energy_j_approx` | number | 焦耳 | CPU 能耗估算值 |

**能耗计算方法**:
```python
# 梯形积分法
energy = sum((power[i] + power[i+1]) / 2 * (timestamps[i+1] - timestamps[i]))
```

#### 6. derived_metrics (派生指标)

**类型**: `object`  
**说明**: 基于性能指标和资源指标计算得出的复合指标

| 字段 | 类型 | 单位 | 说明 |
|-----|------|------|------|
| `P_idle` | number | 瓦特 | 空闲功率（来自基线测量） |
| `P_inc` | number | 瓦特 | 增量功率（平均功率 - 空闲功率） |
| `E_inc` | number | 焦耳 | 增量能耗（总能耗 - 空闲能耗） |
| `E_token` | number | J/token | 每个 token 的增量能耗 |
| `PPW` | number | tokens/s/W | 每瓦特吞吐量（Power Per Watt） |
| `TPJ` | number | tokens/J | 每焦耳 token 数（Tokens Per Joule） |

**计算公式**:
- `P_inc = max(0, P_avg - P_idle)`
- `E_inc = max(0, E_total - P_idle * total_time)`
- `E_token = E_inc / output_tokens`
- `PPW = throughput / P_avg`
- `TPJ = output_tokens / E_total`

#### 7. quality (质量指标)

**类型**: `object`  
**说明**: 模型输出质量的评估指标

| 字段 | 类型 | 说明 |
|-----|------|------|
| `bartscore` | number \| null | BARTScore 质量评分（仅在有参考文本时计算） |
| `generated_text_length` | int | 生成的文本总长度（字符数） |
| `has_reference` | boolean | 是否有参考文本用于评估 |
| `avg_response_length` | number | 平均每轮响应长度 |

**BARTScore 说明**:
- 基于预训练 BART 模型的条件语言建模概率
- 分数范围通常为负值，越接近 0 表示质量越好
- 仅在配置中提供了 `reference_text` 时计算

#### 8. conversation_summary (对话摘要)

**类型**: `array`  
**说明**: 每轮对话的摘要信息

| 字段 | 类型 | 说明 |
|-----|------|------|
| `turn` | int | 轮次编号（从 1 开始） |
| `prompt_preview` | string | 提示词预览（截取前 50 字符） |
| `response_preview` | string | 响应预览（截取前 100 字符） |
| `response_length` | int | 响应文本长度 |
| `duration_seconds` | number | 该轮耗时 |
| `tokens` | int | 该轮生成的 token 数 |
| `throughput` | number | 该轮吞吐量 |
| `gpu_power_avg_w` | number | 该轮平均 GPU 功率（仅在 per_turn_monitoring 时有） |
| `gpu_energy_j` | number | 该轮 GPU 能耗（仅在 per_turn_monitoring 时有） |

**示例**:
```json
"conversation_summary": [
  {
    "turn": 1,
    "prompt_preview": "def multiply(a, b):\n    \"\"\"Complete the function ...",
    "response_preview": "    product = 0\n    carry = 0\n    while a > 0...",
    "response_length": 1112,
    "duration_seconds": 20.519726276397705,
    "tokens": 352,
    "throughput": 17.154224927692095
  }
]
```

#### 9. metadata (元数据)

**类型**: `object`  
**说明**: 实验的附加信息

| 字段 | 类型 | 说明 |
|-----|------|------|
| `timestamp` | string | 实验完成时间（ISO 8601 格式） |
| `analysis_version` | string | 分析脚本版本 |
| `max_tokens` | int | 最大 token 限制 |
| `temperature` | number | 采样温度 |
| `top_p` | number | Top-p 采样参数 |

**示例**:
```json
"metadata": {
  "timestamp": "2026-03-03T19:02:22.790318",
  "analysis_version": "1.0",
  "max_tokens": 1200,
  "temperature": 0.1,
  "top_p": 0.9
}
```

---

## 原始数据结构 (raw.json)

原始文件包含完整的实验记录，用于需要细粒度分析的场景。

### 顶级结构

```json
{
  "experiment_id": "exp_20260303_190201_2518223083168",
  "config": { ... },
  "baseline_raw": null,
  "conversation": [ ... ],
  "monitoring_data": { ... },
  "metadata": { ... }
}
```

### 字段详解

#### 1. config (完整配置)

**类型**: `object`  
**说明**: 实验的完整配置信息

| 字段 | 类型 | 说明 |
|-----|------|------|
| `model` | string | 模型标识符 |
| `model_info` | object | 模型详细信息 |
| `prompts` | array | 提示词列表 |
| `task_type` | string | 任务类型 |
| `keep_context` | boolean | 是否保持上下文 |
| `per_turn_monitoring` | boolean | 是否逐轮监控 |
| `max_tokens` | int \| null | 最大 token 数 |
| `temperature` | number \| null | 采样温度 |
| `top_p` | number \| null | Top-p 参数 |
| `reference_text` | string \| null | 参考文本 |

**model_info 结构**:
```json
"model_info": {
  "type": "huggingface",
  "path": "F:/all_proj/GenAI_power_analize/models/huggingface/google--gemma-2b-it",
  "quantize": "4bit",
  "display_name": "HF:google--gemma-2b-it:4bit"
}
```

#### 2. baseline_raw (原始基线数据)

**类型**: `object | null`  
**说明**: 空闲状态基线的原始测量数据

| 字段 | 类型 | 说明 |
|-----|------|------|
| `duration_seconds` | number | 基线测量持续时间 |
| `start_timestamp` | number | 开始时间戳 |
| `end_timestamp` | number | 结束时间戳 |
| `measurements` | object | 原始测量数据 |

**measurements 结构**:
```json
"measurements": {
  "timestamps": [1772535720.6595109, 1772535721.3430715, ...],
  "cpu_percent": [5.2, 4.8, ...],
  "mem_used_mb": [8000.5, 8010.2, ...],
  "gpu_util": [0, 0, ...],
  "gpu_mem_mb": [2560.0, 2560.0, ...],
  "gpu_power_w": [13.5, 13.4, ...],
  "gpu_temp_c": [38, 38, ...]
}
```

#### 3. conversation (对话记录)

**类型**: `array`  
**说明**: 每轮对话的完整记录

| 字段 | 类型 | 说明 |
|-----|------|------|
| `turn` | int | 轮次编号 |
| `prompt` | string | 完整的提示词 |
| `response` | string | 完整的响应文本 |
| `start_timestamp` | number | 该轮开始时间戳 |
| `end_timestamp` | number | 该轮结束时间戳 |
| `monitoring_data` | object | 该轮的监控数据（仅在 per_turn_monitoring 时有） |

**示例**:
```json
"conversation": [
  {
    "turn": 1,
    "prompt": "def multiply(a, b):\n    \"\"\"Complete the function...\"\"\"\n",
    "response": "    product = 0\n    carry = 0\n    while a > 0 and b > 0:\n        ...",
    "start_timestamp": 1772535721.660512,
    "end_timestamp": 1772535742.1802382
  }
]
```

#### 4. monitoring_data (监控数据)

**类型**: `object`  
**说明**: 实验期间的完整监控数据

| 字段 | 类型 | 说明 |
|-----|------|------|
| `start_timestamp` | number | 开始时间戳 |
| `end_timestamp` | number | 结束时间戳 |
| `measurements` | object | 原始测量数据（与 baseline_raw.measurements 结构相同） |
| `events` | array | 关键事件记录 |

**events 结构**:
```json
"events": [
  {
    "event": "experiment_start",
    "timestamp": 1772535721.6595109,
    "metadata": {
      "task_type": "code",
      "model": "HF:google--gemma-2b-it:4bit"
    }
  },
  {
    "event": "inference_start",
    "timestamp": 1772535721.660512,
    "metadata": {
      "turn": 1
    }
  },
  {
    "event": "first_token",
    "timestamp": 1772535722.3430715,
    "metadata": {
      "turn": 1,
      "tokens": 1
    }
  },
  {
    "event": "inference_end",
    "timestamp": 1772535742.1802382,
    "metadata": {
      "turn": 1,
      "tokens": 352
    }
  }
]
```

---

## 任务类型说明 (task_type)

| 任务类型 | 说明 | 典型应用场景 |
|---------|------|-------------|
| `qa` | 问答任务 | 知识问答、事实查询 |
| `code` | 代码生成 | 编程问题、代码补全 |
| `math` | 数学计算 | 算术问题、应用题 |
| `reasoning` | 逻辑推理 | 推理题、论证分析 |
| `summary` | 文本摘要 | 长文本摘要 |
| `creative` | 创意写作 | 故事创作、诗歌生成 |
| `translation` | 翻译任务 | 跨语言翻译 |
| `multi_turn` | 多轮对话 | 复杂对话场景 |
| `context_verification` | 上下文验证 | 信息提取、验证 |

---

## 数据访问示例

### Python 读取汇总数据

```python
import json

# 读取汇总数据
with open('data/gemma_2b_hf_4bit/experiment_results_20260303_190201_summary.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# 访问单个实验
for exp in results:
    print(f"实验ID: {exp['experiment_id']}")
    print(f"模型: {exp['config_ref']['model']}")
    print(f"任务类型: {exp['config_ref']['task_type']}")
    print(f"吞吐量: {exp['performance']['throughput_tokens_per_sec']:.2f} tokens/s")
    print(f"能耗: {exp['resources']['gpu_energy_j']:.2f} J")
    print(f"BARTScore: {exp['quality']['bartscore']}")
```

### 按任务类型筛选

```python
# 筛选所有 code 任务
code_experiments = [exp for exp in results if exp['config_ref']['task_type'] == 'code']

# 计算平均吞吐量
avg_throughput = sum(exp['performance']['throughput_tokens_per_sec'] for exp in code_experiments) / len(code_experiments)
print(f"Code 任务平均吞吐量: {avg_throughput:.2f} tokens/s")
```

### 计算派生指标

```python
for exp in results:
    perf = exp['performance']
    res = exp['resources']
    
    # 计算能效比 (tokens per Joule)
    if res['gpu_energy_j'] > 0:
        tpj = perf['output_tokens'] / res['gpu_energy_j']
        print(f"能效比: {tpj:.4f} tokens/J")
    
    # 计算每 token 能耗
    if perf['output_tokens'] > 0:
        e_per_token = res['gpu_energy_j'] / perf['output_tokens']
        print(f"每 token 能耗: {e_per_token:.6f} J/token")
```

### 读取原始数据获取时间序列

```python
import json

with open('data/gemma_2b_hf_4bit/experiment_results_20260303_190201_raw.json', 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

# 获取 GPU 功率时间序列
exp = raw_data[0]
measurements = exp['monitoring_data']['measurements']
power_values = measurements['gpu_power_w']
timestamps = measurements['timestamps']

print(f"采样点数: {len(power_values)}")
print(f"平均功率: {sum(power_values)/len(power_values):.2f} W")
print(f"最大功率: {max(power_values):.2f} W")
```

---

## 字段对照表

| 汇总字段 | 原始数据来源 | 计算方法 |
|---------|-------------|---------|
| `performance.total_time_seconds` | monitoring_data timestamps | end - start |
| `performance.token_count` | events (inference_end) | sum of tokens |
| `performance.throughput_tokens_per_sec` | derived | tokens / time |
| `resources.gpu_energy_j` | measurements (power, timestamps) | 梯形积分 |
| `resources.cpu_energy_j_approx` | measurements (cpu_percent) | TDP * usage * time |

---

## 版本历史

| 版本 | 日期 | 变更 |
|-----|------|------|
| 1.0 | 2026-03-03 | 初始版本结构 |

---

## 相关文件

- **实验运行器**: `experiments/experiment_runner.py` - 包含 `ExperimentResult` 类定义
- **快速开始指南**: `docs/QUICK_START_NEW_FORMAT.md` - 数据访问示例
- **实验运行指南**: `docs/EXPERIMENT_RUNNER_GUIDE.md` - 完整配置说明