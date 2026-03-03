# Experiment Runner 使用指南

## 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [配置文件详解](#配置文件详解)
- [命令行参数](#命令行参数)
- [模型规格说明](#模型规格说明)
- [高级功能](#高级功能)
- [输出结果](#输出结果)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

## 概述

`experiment_runner.py` 是项目的核心实验执行脚本，支持：

- ✅ **双模型支持**: Ollama 和 Hugging Face 模型
- ✅ **多轮对话**: 支持保持上下文的多轮对话
- ✅ **资源监控**: 实时监控 CPU、GPU、内存、功耗等
- ✅ **质量评估**: 集成 BARTScore 质量评估
- ✅ **空闲基线**: 测量空闲功耗并计算增量指标
- ✅ **灵活配置**: 通过 JSON 配置文件或命令行参数

## 快速开始

### 1. 准备环境

```bash
# 激活 conda 环境
conda activate bartscore

# 确保依赖已安装
pip install pynvml psutil requests transformers torch
```

### 2. 创建测试用例文件

创建 `my_test_cases.json`:

```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["什么是Python？"],
    "task_type": "qa",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9,
    "idle_measurement_duration": 10
  }
]
```

### 3. 运行实验

```bash
python experiments/experiment_runner.py --config my_test_cases.json --output-dir ./results
```

### 4. 查看结果

结果保存在 `./results` 目录：
- `experiment_results_raw_YYYYMMDD_HHMMSS.json` - 完整原始数据
- `experiment_results_summary_YYYYMMDD_HHMMSS.json` - 汇总数据

## 配置文件详解

### 基本结构

配置文件是一个 JSON 数组，每个元素是一个测试用例：

```json
[
  {
    "model": "模型规格",
    "prompts": "提示词或提示词列表",
    "task_type": "任务类型",
    "reference_text": "参考文本（可选）",
    "max_tokens": 最大token数,
    "temperature": 温度参数,
    "top_p": Top-p采样参数,
    "keep_context": 是否保持上下文,
    "per_turn_monitoring": 是否分轮监控,
    "idle_measurement_duration": 空闲测量时长
  }
]
```

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `model` | string | 模型规格字符串 | `"ollama:qwen3:4b"` |
| `prompts` | string/array | 单个提示或提示列表 | `["问题1", "问题2"]` |
| `task_type` | string | 任务类型标识 | `"qa"`, `"creative"`, `"code"`, `"summary"` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `reference_text` | string | `null` | 参考文本，用于质量评估 |
| `max_tokens` | int | `500` | 最大生成token数 |
| `temperature` | float | `0.7` | 温度参数 (0.0-2.0) |
| `top_p` | float | `0.9` | Top-p采样参数 (0.0-1.0) |
| `keep_context` | bool | `false` | 多轮对话是否保持上下文 |
| `per_turn_monitoring` | bool | `false` | 是否为每轮独立监控资源 |
| `idle_measurement_duration` | int | `0` | 空闲基线测量时长（秒），0表示不测量 |

### 参数详细说明

#### 1. model (模型规格)

支持三种格式：

**Ollama 模型**:
```json
"model": "qwen3:4b"
// 或
"model": "ollama:qwen3:4b"
```

**Hugging Face 模型**:
```json
"model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct"
// 或带量化
"model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"
```

量化选项：
- `4bit` - 4位量化（推荐，显存占用最小）
- `8bit` - 8位量化
- 不指定 - FP16（默认）

#### 2. prompts (提示词)

**单轮对话**:
```json
"prompts": "什么是Python？"
// 或
"prompts": ["什么是Python？"]
```

**多轮对话**:
```json
"prompts": [
  "什么是Python？",
  "它有哪些主要特点？",
  "请给我一个简单的代码示例。"
]
```

#### 3. task_type (任务类型)

推荐的任务类型：

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| `qa` | 问答任务 | 知识问答、信息查询 |
| `summary` | 摘要任务 | 文本摘要、内容总结 |
| `creative` | 创作任务 | 写作、诗歌、故事 |
| `code` | 代码任务 | 代码生成、调试 |
| `translation` | 翻译任务 | 语言翻译 |
| `reasoning` | 推理任务 | 逻辑推理、数学问题 |

#### 4. temperature (温度参数)

控制生成的随机性：

| 值 | 效果 | 适用场景 |
|----|------|---------|
| 0.0-0.3 | 确定性强，输出稳定 | 事实性问答、代码生成 |
| 0.4-0.7 | 平衡创造性和准确性 | 通用对话、摘要 |
| 0.8-1.0 | 创造性强，输出多样 | 创意写作、头脑风暴 |
| 1.0+ | 高度随机 | 实验性探索 |

#### 5. top_p (Top-p采样)

控制采样范围：

| 值 | 效果 |
|----|------|
| 0.9 | 推荐值，平衡质量和多样性 |
| 0.95 | 更多样化 |
| 0.8 | 更保守 |
| 1.0 | 考虑所有可能的token |

#### 6. keep_context (保持上下文)

多轮对话时是否保持上下文：

```json
{
  "prompts": ["问题1", "问题2", "问题3"],
  "keep_context": true  // 每轮都能看到之前的对话
}
```

**注意**:
- Ollama: 使用 `context` 字段保持上下文
- HuggingFace: 将历史对话拼接到提示中

#### 7. per_turn_monitoring (分轮监控)

是否为每轮对话独立监控资源：

```json
{
  "prompts": ["问题1", "问题2", "问题3"],
  "per_turn_monitoring": true  // 每轮独立监控
}
```

**对比**:

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| 整体监控 (false) | 开销小，数据简洁 | 无法分析每轮差异 | 单轮对话，快速测试 |
| 分轮监控 (true) | 详细的每轮数据 | 开销大，数据量大 | 多轮对话分析 |

#### 8. idle_measurement_duration (空闲测量)

测量系统空闲功耗的时长（秒）：

```json
{
  "idle_measurement_duration": 10  // 测量10秒空闲功耗
}
```

**推荐值**:

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 快速测试 | 5 | 快速验证 |
| 标准实验 | 10 | 推荐值 |
| 精确测量 | 15-30 | 更稳定的基线 |
| 不测量 | 0 | 默认值 |

**自动计算的指标**:
- P_idle: 空闲功耗
- P_inc: 增量功耗
- E_inc: 增量能耗
- E_token: 每token能耗
- PPW: 每瓦性能
- TPJ: 能效比

## 命令行参数

### 基本用法

```bash
python experiments/experiment_runner.py [OPTIONS]
```

### 可用选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--config PATH` | 测试用例配置文件路径 | 无 |
| `--output-dir DIR` | 结果输出目录 | `./results` |
| `--sample` | 运行示例测试用例 | 无 |
| `-h, --help` | 显示帮助信息 | 无 |

### 使用示例

**1. 使用配置文件**:
```bash
python experiments/experiment_runner.py --config test_cases.json --output-dir ./my_results
```

**2. 运行示例**:
```bash
python experiments/experiment_runner.py --sample
```

**3. 指定输出目录**:
```bash
python experiments/experiment_runner.py --config test_cases.json --output-dir data/experiments_5
```

## 模型规格说明

### Ollama 模型

**格式**: `ollama:model_name` 或直接 `model_name`

**示例**:
```json
"model": "qwen3:4b"
"model": "ollama:deepseek-r1:8b"
"model": "gemma3:4b"
```

**可用模型** (需先通过 Ollama 下载):
- `qwen3:4b` - Qwen 3 4B 参数
- `qwen3:8b` - Qwen 3 8B 参数
- `deepseek-r1:8b` - DeepSeek R1 8B
- `gemma3:4b` - Gemma 3 4B

**下载模型**:
```bash
ollama pull qwen3:4b
```

### Hugging Face 模型

**格式**: `hf:model_path[:quantize]`

**示例**:
```json
"model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct"
"model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"
"model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:8bit"
```

**路径说明**:
- 相对路径: 相对于项目根目录
- 绝对路径: 完整的文件系统路径
- 自动规范化: 支持 Windows 和 Linux 路径

**量化选项**:
- 不指定: FP16 (默认)
- `:4bit`: 4位量化 (推荐，显存占用约为原来的 1/4)
- `:8bit`: 8位量化 (显存占用约为原来的 1/2)

**显存需求参考**:

| 模型大小 | FP16 | 8bit | 4bit |
|---------|------|------|------|
| 7B | ~14GB | ~7GB | ~3.5GB |
| 13B | ~26GB | ~13GB | ~6.5GB |
| 70B | ~140GB | ~70GB | ~35GB |

## 高级功能

### 1. 多轮对话

**基本多轮对话**:
```json
{
  "model": "ollama:qwen3:4b",
  "prompts": [
    "什么是Python？",
    "它有哪些主要特点？",
    "请给我一个简单的代码示例。"
  ],
  "task_type": "qa",
  "keep_context": false  // 每轮独立
}
```

**保持上下文的多轮对话**:
```json
{
  "model": "ollama:qwen3:4b",
  "prompts": [
    "什么是Python？",
    "它有哪些主要特点？",  // 可以引用第一轮的回答
    "请给我一个简单的代码示例。"  // 可以引用前两轮的内容
  ],
  "task_type": "qa",
  "keep_context": true  // 保持上下文
}
```

### 2. 分轮监控

**整体监控** (默认):
```json
{
  "prompts": ["问题1", "问题2", "问题3"],
  "per_turn_monitoring": false
}
```

输出: 整个对话的总体资源使用情况

**分轮监控**:
```json
{
  "prompts": ["问题1", "问题2", "问题3"],
  "per_turn_monitoring": true
}
```

输出: 每轮对话的独立资源使用情况

### 3. 空闲基线测量

**启用空闲基线测量**:
```json
{
  "model": "ollama:qwen3:4b",
  "prompts": ["什么是Python？"],
  "task_type": "qa",
  "idle_measurement_duration": 10
}
```

**测量流程**:
1. 系统提示保持空闲
2. 测量指定时长的空闲功耗
3. 运行模型推理
4. 自动计算增量指标

**输出增量指标**:
- P_idle: 45.23 W
- P_inc: 15.67 W
- E_inc: 125.34 J
- E_token: 1.1032 J/token
- PPW: 0.75 tokens/s/W
- TPJ: 0.91 tokens/J

### 4. 质量评估

**使用参考文本**:
```json
{
  "model": "ollama:qwen3:4b",
  "prompts": ["请解释牛顿第一定律。"],
  "task_type": "qa",
  "reference_text": "牛顿第一定律，也称为惯性定律，指出：一个物体如果不受外力作用，或者所受合外力为零，那么静止的物体会保持静止状态，运动的物体会保持匀速直线运动状态。"
}
```

**自动评估**:
- 使用 BARTScore 评估生成质量
- 计算与参考文本的相似度
- 保存在结果的 `quality` 字段

## 输出结果

### 文件结构

```
output-dir/
├── experiment_results_raw_20260302_165811.json      # 完整原始数据
└── experiment_results_summary_20260302_165811.json  # 汇总数据
```

### 原始数据结构概览

每个测试用例的结果是一个JSON对象，包含以下顶层字段：

```json
{
  "model": "模型标识符",
  "model_info": { ... },
  "prompts": [ ... ],
  "task_type": "任务类型",
  "keep_context": true/false,
  "per_turn_monitoring": true/false,
  "baseline": { ... },
  "conversation": [ ... ],
  "generated_text": "最后一轮的完整回答",
  "all_responses": [ ... ],
  "performance": { ... },
  "resources": { ... },
  "system_metrics_summary": { ... },
  "system_metrics_full": { ... },
  "phase_analysis": { ... },
  "quality": { ... },
  "metadata": { ... }
}
```

### 详细字段说明

#### 1. 基本信息字段

##### `model` (string)
模型的显示名称，格式化后的标识符。

**示例**:
```json
"model": "HF:Qwen--Qwen2.5-7B-Instruct:4bit"
"model": "ollama:qwen3:4b"
```

##### `model_info` (object)
模型的详细信息。

**字段**:
- `type` (string): 模型类型，`"huggingface"` 或 `"ollama"`
- `path` (string): 模型路径（HF模型）或名称（Ollama模型）
- `quantize` (string|null): 量化方式，如 `"4bit"`, `"8bit"`, 或 `null`
- `display_name` (string): 格式化的显示名称

**示例**:
```json
"model_info": {
  "type": "huggingface",
  "path": "F:/all_proj/GenAI_power_analize/models/huggingface/Qwen--Qwen2.5-7B-Instruct",
  "quantize": "4bit",
  "display_name": "HF:Qwen--Qwen2.5-7B-Instruct:4bit"
}
```

##### `prompts` (array)
输入的提示词列表。

**示例**:
```json
"prompts": [
  "什么是Python？",
  "它有哪些主要特点？",
  "请给我一个简单的代码示例。"
]
```

##### `task_type` (string)
任务类型标识。

**常见值**: `"qa"`, `"summary"`, `"creative"`, `"code"`, `"translation"`, `"reasoning"`

##### `keep_context` (boolean)
多轮对话是否保持上下文。

##### `per_turn_monitoring` (boolean)
是否为每轮对话独立监控资源。

#### 2. 空闲基线数据 (baseline)

仅当 `idle_measurement_duration > 0` 时存在。

**字段**:

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `duration_seconds` | float | 秒 | 测量时长 |
| `gpu_power_avg_w` | float | 瓦特 | 平均GPU功耗 |
| `gpu_power_peak_w` | float | 瓦特 | 峰值GPU功耗 |
| `gpu_energy_j` | float | 焦耳 | 总能耗 |
| `cpu_percent_avg` | float | % | 平均CPU使用率 |
| `gpu_util_avg` | float | % | 平均GPU利用率 |
| `gpu_mem_peak_mb` | float | MB | 峰值GPU显存 |
| `timestamp` | float | Unix时间戳 | 测量开始时间 |

**示例**:
```json
"baseline": {
  "duration_seconds": 10,
  "gpu_power_avg_w": 15.307888888888895,
  "gpu_power_peak_w": 23.024,
  "gpu_energy_j": 148.40483618569365,
  "cpu_percent_avg": 8.742857142857146,
  "gpu_util_avg": 4.428571428571429,
  "gpu_mem_peak_mb": 3100.28515625,
  "timestamp": 1772441901.8263838
}
```

#### 3. 对话记录 (conversation)

多轮对话的详细记录。

**数组元素结构**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `turn` | int | 轮次编号（从1开始） |
| `prompt` | string | 该轮的输入提示 |
| `response` | string | 该轮的模型回答 |

**示例**:
```json
"conversation": [
  {
    "turn": 1,
    "prompt": "什么是Python？",
    "response": "Python是一种高级编程语言..."
  },
  {
    "turn": 2,
    "prompt": "它有哪些主要特点？",
    "response": "以下是Python的一些主要特点..."
  }
]
```

##### `generated_text` (string)
最后一轮的完整回答文本。

##### `all_responses` (array)
所有轮次的回答列表。

**示例**:
```json
"all_responses": [
  "Python是一种高级编程语言...",
  "以下是Python的一些主要特点...",
  "以下是一个简单的 Python 代码示例..."
]
```

#### 4. 性能指标 (performance)

推理性能的关键指标。

**字段**:

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `total_time_seconds` | float | 秒 | 总执行时间 |
| `token_count` | int | tokens | 生成的token总数 |
| `output_tokens` | int | tokens | 输出token数（同token_count） |
| `throughput_tokens_per_sec` | float | tokens/s | 吞吐量 |
| `latency_per_token_ms` | float | 毫秒 | 每token延迟 |
| `turns` | int | - | 对话轮数 |
| `avg_time_per_turn` | float | 秒 | 每轮平均时间 |

**示例**:
```json
"performance": {
  "total_time_seconds": 158.3627631664276,
  "token_count": 450,
  "output_tokens": 450,
  "throughput_tokens_per_sec": 2.841577091750307,
  "latency_per_token_ms": 351.91725148095026,
  "turns": 3,
  "avg_time_per_turn": 52.78758772214254
}
```

**关键指标解读**:
- **吞吐量** (throughput): 越高越好，表示生成速度快
- **延迟** (latency): 越低越好，表示响应快
- **关系**: `latency_per_token_ms = 1000 / throughput_tokens_per_sec`

#### 5. 资源使用 (resources)

系统资源使用情况和能效指标。

**字段**:

| 字段 | 类型 | 单位 | 说明 |
|------|------|------|------|
| `P_idle` | float | 瓦特 | 空闲功耗（需启用baseline） |
| `P_inc` | float | 瓦特 | 增量功耗（推理时的额外功耗） |
| `E_inc` | float | 焦耳 | 增量能耗（推理的净能耗） |
| `E_token` | float | 焦耳/token | 每token能耗 |
| `PPW` | float | tokens/s/W | 每瓦性能（能效指标） |
| `TPJ` | float | tokens/J | 每焦耳token数（能效指标） |
| `cpu_percent_avg` | float | % | 平均CPU使用率 |
| `cpu_percent_peak` | float | % | 峰值CPU使用率 |
| `mem_used_peak_mb` | float | MB | 峰值内存使用 |
| `gpu_util_avg` | float | % | 平均GPU利用率 |
| `gpu_util_peak` | int | % | 峰值GPU利用率 |
| `gpu_mem_peak_mb` | float | MB | 峰值GPU显存 |
| `gpu_power_avg_w` | float | 瓦特 | 平均GPU功耗 |
| `gpu_energy_j` | float | 焦耳 | GPU总能耗 |
| `gpu_temp_peak_c` | int | 摄氏度 | 峰值GPU温度 |
| `cpu_energy_j_approx` | float | 焦耳 | CPU能耗估算值 |

**示例**:
```json
"resources": {
  "cpu_percent_avg": 24.860049937578,
  "cpu_percent_peak": 100.0,
  "mem_used_peak_mb": 15405.84375,
  "gpu_util_avg": 66.93882646691635,
  "gpu_util_peak": 100,
  "gpu_mem_peak_mb": 8147.55078125,
  "gpu_power_avg_w": 33.07697627965045,
  "gpu_energy_j": 5797.8540632061995,
  "gpu_temp_peak_c": 67,
  "cpu_energy_j_approx": 2856.084676113129,
  "P_idle": 15.307888888888895,
  "P_inc": 17.769087390761555,
  "E_inc": 3373.654480517099,
  "E_token": 7.497009956704664,
  "PPW": 0.08590800645518787,
  "TPJ": 0.07761492357245554
}
```

**能效指标说明**:

- **P_idle**: 系统空闲时的基线功耗
- **P_inc**: 推理时的增量功耗 = `gpu_power_avg_w - P_idle`
- **E_inc**: 推理的净能耗 = `gpu_energy_j - (P_idle × total_time_seconds)`
- **E_token**: 每生成一个token消耗的能量 = `E_inc / output_tokens`
- **PPW**: 每瓦特功耗下的性能 = `throughput_tokens_per_sec / gpu_power_avg_w`
- **TPJ**: 每焦耳能量生成的token数 = `output_tokens / gpu_energy_j`

**能效指标越高越好**，表示模型在相同能耗下能生成更多内容。

#### 6. 系统指标汇总 (system_metrics_summary)

与 `resources` 字段内容相同，提供系统资源使用的汇总统计。

#### 7. 完整系统指标 (system_metrics_full)

时间序列监控数据，用于详细分析。

**字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamps` | array[float] | Unix时间戳序列 |
| `cpu_percent` | array[float] | CPU使用率时间序列 |
| `mem_used_mb` | array[float] | 内存使用时间序列 |
| `gpu_util` | array[int] | GPU利用率时间序列 |
| `gpu_mem_mb` | array[float] | GPU显存时间序列 |
| `gpu_power_w` | array[float] | GPU功耗时间序列 |
| `gpu_temp_c` | array[int] | GPU温度时间序列 |
| `events` | array[object] | 事件标记（推理开始/结束等） |
| `summary` | object | 汇总统计 |

**示例**:
```json
"system_metrics_full": {
  "timestamps": [1772441901.826894, 1772441902.0525796, ...],
  "cpu_percent": [0.0, 38.8, 35.3, 76.5, ...],
  "mem_used_mb": [7234.5, 7245.2, ...],
  "gpu_util": [0, 45, 67, 89, ...],
  "gpu_mem_mb": [3100.2, 6234.5, ...],
  "gpu_power_w": [15.3, 45.2, 60.8, ...],
  "gpu_temp_c": [45, 52, 67, ...],
  "events": [
    {
      "timestamp": 1772441901.827901,
      "event": "experiment_start",
      "metadata": {}
    },
    {
      "timestamp": 1772441901.827901,
      "event": "inference_start",
      "metadata": {"turn": 1}
    },
    {
      "timestamp": 1772441965.8674734,
      "event": "inference_end",
      "metadata": {"turn": 1}
    }
  ],
  "summary": {
    "cpu_percent_avg": 24.86,
    "cpu_percent_peak": 100.0,
    ...
  }
}
```

**事件类型**:
- `experiment_start`: 实验开始
- `experiment_end`: 实验结束
- `inference_start`: 推理开始（包含turn信息）
- `inference_end`: 推理结束（包含turn信息）
- `first_token`: 首个token生成（用于TTFT计算）

#### 8. 阶段分析 (phase_analysis)

推理各阶段的详细分析（如果启用了分轮监控）。

**结构**: 空对象 `{}` 或包含各阶段的详细数据。

#### 9. 质量评估 (quality)

文本生成质量的评估结果。

**字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `bartscore` | float\|null | BARTScore评分（需要reference_text） |
| `generated_text_length` | int | 生成文本长度（字符数） |
| `has_reference` | boolean | 是否提供了参考文本 |

**示例**:
```json
"quality": {
  "bartscore": null,
  "generated_text_length": 316,
  "has_reference": false
}
```

**BARTScore说明**:
- 范围: 通常在 -5 到 0 之间
- 越接近0越好（表示生成文本与参考文本越相似）
- 需要提供 `reference_text` 参数才能计算
- `null` 表示未计算或计算失败

#### 10. 元数据 (metadata)

实验的配置元数据。

**字段**:

| 字段 | 类型 | 说明 |
|------|------|------|
| `timestamp` | string | ISO格式时间戳 |
| `max_tokens` | int | 最大token数配置 |
| `temperature` | float | 温度参数 |
| `top_p` | float | Top-p采样参数 |

**示例**:
```json
"metadata": {
  "timestamp": "2026-03-02T17:01:17.656786",
  "max_tokens": 150,
  "temperature": 0.5,
  "top_p": 0.9
}
```

### 字段快速参考表

#### 性能相关

| 字段路径 | 说明 | 单位 | 越大越好 |
|---------|------|------|---------|
| `performance.throughput_tokens_per_sec` | 吞吐量 | tokens/s | ✅ |
| `performance.latency_per_token_ms` | 延迟 | ms | ❌ |
| `performance.total_time_seconds` | 总时间 | s | ❌ |

#### 资源相关

| 字段路径 | 说明 | 单位 | 越小越好 |
|---------|------|------|---------|
| `resources.gpu_energy_j` | GPU总能耗 | J | ✅ |
| `resources.E_inc` | 增量能耗 | J | ✅ |
| `resources.gpu_power_avg_w` | 平均功耗 | W | ✅ |
| `resources.gpu_mem_peak_mb` | 峰值显存 | MB | ✅ |
| `resources.gpu_util_avg` | GPU利用率 | % | - |

#### 能效相关

| 字段路径 | 说明 | 单位 | 越大越好 |
|---------|------|------|---------|
| `resources.PPW` | 每瓦性能 | tokens/s/W | ✅ |
| `resources.TPJ` | 能效比 | tokens/J | ✅ |
| `resources.E_token` | 每token能耗 | J/token | ❌ |

#### 质量相关

| 字段路径 | 说明 | 范围 | 越大越好 |
|---------|------|------|---------|
| `quality.bartscore` | 质量评分 | -5 ~ 0 | ✅ |
| `quality.generated_text_length` | 文本长度 | - | - |

### 数据使用示例

#### Python读取和分析

```python
import json
import pandas as pd

# 读取结果文件
with open('experiment_results_raw_20260302_165811.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

# 提取关键指标
data = []
for result in results:
    data.append({
        'model': result['model'],
        'task_type': result['task_type'],
        'throughput': result['performance']['throughput_tokens_per_sec'],
        'latency': result['performance']['latency_per_token_ms'],
        'energy': result['resources']['gpu_energy_j'],
        'E_token': result['resources'].get('E_token'),
        'PPW': result['resources'].get('PPW'),
        'TPJ': result['resources'].get('TPJ'),
        'bartscore': result['quality']['bartscore']
    })

df = pd.DataFrame(data)
print(df)
```

#### 计算质效比

```python
# 归一化指标
df['norm_throughput'] = (df['throughput'] - df['throughput'].min()) / (df['throughput'].max() - df['throughput'].min())
df['norm_energy'] = 1 - (df['energy'] - df['energy'].min()) / (df['energy'].max() - df['energy'].min())

# 计算效率得分
df['efficiency_score'] = 0.5 * df['norm_throughput'] + 0.5 * df['norm_energy']

# 计算质效比
df['qe_ratio'] = df['bartscore'] / (1.01 - df['efficiency_score'])
```

## 最佳实践

### 1. 实验设计

**单变量对比**:
```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["相同的问题"],
    "temperature": 0.5
  },
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["相同的问题"],
    "temperature": 0.7
  },
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["相同的问题"],
    "temperature": 0.9
  }
]
```

**多模型对比**:
```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["相同的问题"],
    "temperature": 0.7
  },
  {
    "model": "ollama:gemma3:4b",
    "prompts": ["相同的问题"],
    "temperature": 0.7
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompts": ["相同的问题"],
    "temperature": 0.7
  }
]
```

### 2. 资源优化

**显存不足时**:
- 使用 4bit 量化
- 减少 max_tokens
- 关闭分轮监控
- 一次只运行一个实验

**提高准确性**:
- 增加 idle_measurement_duration
- 使用较低的 temperature
- 提供详细的 reference_text

### 3. 数据管理

**组织实验**:
```
data/
├── experiments_1/  # 第一批实验
│   ├── test_cases.json
│   └── results/
├── experiments_2/  # 第二批实验
│   ├── test_cases.json
│   └── results/
└── experiments_3/  # 第三批实验
    ├── test_cases.json
    └── results/
```

**命名规范**:
- 测试用例: `test_cases_[描述].json`
- 输出目录: `data/experiments_[编号]`

### 4. 性能调优

**加快实验速度**:
```json
{
  "max_tokens": 100,  // 减少生成长度
  "idle_measurement_duration": 5,  // 减少测量时间
  "per_turn_monitoring": false  // 关闭分轮监控
}
```

**提高测量精度**:
```json
{
  "idle_measurement_duration": 15,  // 增加测量时间
  "per_turn_monitoring": true  // 启用分轮监控
}
```

## 故障排除

### 常见问题

#### 1. 模型加载失败

**症状**: `Hugging Face模型加载器不可用`

**解决方案**:
```bash
pip install transformers torch accelerate bitsandbytes
```

#### 2. Ollama 连接失败

**症状**: `Ollama服务未运行或不可访问`

**解决方案**:
```bash
# 检查 Ollama 服务
ollama --version

# 启动 Ollama 服务
ollama serve
```

#### 3. 显存不足

**症状**: `CUDA out of memory`

**解决方案**:
- 使用 4bit 量化: `"model": "hf:path:4bit"`
- 减少 max_tokens
- 关闭其他 GPU 程序

#### 4. 空闲基线测量失败

**症状**: `高级监控不可用，跳过空闲基线测量`

**解决方案**:
```bash
pip install pynvml
```

#### 5. BARTScore 评估失败

**症状**: `BARTScore不可用`

**解决方案**:
```bash
# 确保 BARTScore 目录存在
ls tools/thesis_reproduction/BARTScore/

# 安装依赖
pip install transformers torch
```

### 调试技巧

**1. 启用详细日志**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**2. 测试单个用例**:
```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["测试"],
    "task_type": "qa",
    "max_tokens": 50
  }
]
```

**3. 检查输出文件**:
```bash
# 查看最新的结果文件
ls -lt results/*.json | head -1

# 检查文件内容
cat results/experiment_results_summary_*.json | jq .
```

## 示例配置文件

### 示例1: 基础单轮对话

```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["什么是Python？"],
    "task_type": "qa",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9
  }
]
```

### 示例2: 多轮对话 + 空闲基线

```json
[
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
]
```

### 示例3: 多模型对比实验

```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["写一首关于春天的诗"],
    "task_type": "creative",
    "max_tokens": 200,
    "temperature": 0.8,
    "idle_measurement_duration": 10
  },
  {
    "model": "ollama:gemma3:4b",
    "prompts": ["写一首关于春天的诗"],
    "task_type": "creative",
    "max_tokens": 200,
    "temperature": 0.8,
    "idle_measurement_duration": 10
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompts": ["写一首关于春天的诗"],
    "task_type": "creative",
    "max_tokens": 200,
    "temperature": 0.8,
    "idle_measurement_duration": 10
  }
]
```

### 示例4: 完整功能测试

```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": [
      "什么是机器学习？",
      "它有哪些主要应用？",
      "请举一个实际例子。"
    ],
    "task_type": "qa",
    "reference_text": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习并改进性能，而无需明确编程。",
    "keep_context": true,
    "per_turn_monitoring": true,
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9,
    "idle_measurement_duration": 10
  }
]
```

## 相关文档

- [空闲基线测量功能说明](./IDLE_BASELINE_MEASUREMENT.md)
- [空闲基线快速参考](./IDLE_BASELINE_QUICK_REFERENCE.md)
- [多轮对话指南](./MULTI_TURN_CONVERSATION_GUIDE.md)
- [统一运行器指南](../experiments/UNIFIED_RUNNER_GUIDE.md)
- [故障排除](../TROUBLESHOOTING.md)

## 更新日志

### v2.0 (2026-03-02)
- 添加空闲基线功耗测量功能
- 自动计算增量指标（P_inc, E_inc, E_token, PPW, TPJ）
- 完善文档和示例

### v1.0 (2026-03-01)
- 初始版本
- 支持 Ollama 和 Hugging Face 模型
- 多轮对话和资源监控

---

**文档版本**: v2.0  
**创建时间**: 2026-03-02  
**维护者**: Kiro AI Assistant
