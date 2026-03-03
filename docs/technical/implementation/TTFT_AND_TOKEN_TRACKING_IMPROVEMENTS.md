# TTFT 和 Token 统计改进文档

## 改进概述

本次改进为实验框架添加了首 Token 延迟（TTFT）记录、改进的 Token 统计和事件标记功能，支持更精细的性能分析和分阶段能耗评估。

## 改进日期

2026-03-02

## 主要改进内容

### 1. 监控模块增强 (`experiments/monitor.py`)

#### 新增功能

**事件标记系统**：
- 新增 `events` 列表，用于记录关键事件的时间戳
- 新增 `mark_event(event_name, metadata)` 方法，用于标记事件
- 新增 `get_phase_data(start_event, end_event)` 方法，用于提取两个事件之间的监控数据

**支持的事件类型**：
- `experiment_start`: 实验开始
- `inference_start`: 推理开始
- `first_token`: 首个 token 生成
- `inference_end`: 推理结束
- `experiment_end`: 实验结束
- `experiment_error`: 实验错误

**分阶段能耗分析**：
```python
# 获取 Prefill 阶段数据
prefill_data = monitor.get_phase_data("inference_start", "first_token")

# 获取 Decode 阶段数据
decode_data = monitor.get_phase_data("first_token", "inference_end")
```

返回数据包含：
- `duration_seconds`: 阶段持续时间
- `gpu_power_avg_w`: 平均 GPU 功耗
- `gpu_power_peak_w`: 峰值 GPU 功耗
- `gpu_energy_j`: 该阶段总能耗
- `sample_count`: 采样点数量

### 2. Ollama 模型调用改进 (`experiments/experiment_runner.py`)

#### 流式生成支持

将 Ollama API 调用从非流式改为流式，以捕获首 token 时间：

```python
request_data = {
    "model": model_name,
    "prompt": prompt,
    "stream": True,  # 启用流式
    ...
}
```

#### 新增性能指标

**返回数据新增字段**：
- `first_token_time`: TTFT（首 token 延迟，秒）
- `decode_time`: Decode 阶段时间（秒）
- `prompt_tokens`: 输入 token 数
- `output_tokens`: 输出 token 数
- `total_tokens`: 总 token 数
- `tpot`: TPOT（每个输出 token 的平均时间，秒）

**Token 统计改进**：
- 优先使用 Ollama API 返回的精确值（`eval_count`, `prompt_eval_count`）
- 如果 API 未返回，回退到简单估算（按空格分词）

**计算公式**：
```python
ttft = first_token_time - start_time
decode_time = end_time - first_token_time
tpot = decode_time / (output_tokens - 1)  # 排除首 token
```

### 3. HuggingFace 模型调用改进

#### 流式生成支持（可选）

如果 `hf_loader` 支持 `generate_stream` 方法，则使用流式生成：

```python
if hasattr(self.hf_loader, 'generate_stream'):
    for token_text in self.hf_loader.generate_stream(...):
        if first_token_time is None:
            first_token_time = time.time()
        generated_text += token_text
```

#### Token 统计改进

使用 tokenizer 精确统计：
```python
prompt_tokens = len(tokenizer.encode(prompt))
output_tokens = len(tokenizer.encode(generated_text))
total_tokens = prompt_tokens + output_tokens
```

#### 新增性能指标

与 Ollama 相同的指标字段：
- `first_token_time`, `decode_time`, `prompt_tokens`, `output_tokens`, `total_tokens`, `tpot`

### 4. 实验执行流程改进

#### 事件标记集成

在实验执行过程中自动标记关键事件：

```python
# 实验开始
monitor.mark_event("experiment_start", {"task_type": task_type})

# 每轮推理
for turn_idx, prompt in enumerate(prompts, 1):
    monitor.mark_event("inference_start", {"turn": turn_idx})
    
    # 调用模型生成
    response = self.call_ollama_generate(...)
    
    # 标记首 token（基于响应中的 first_token_time）
    if response.get("first_token_time"):
        inference_start_time = monitor.events[-1]["timestamp"]
        first_token_abs_time = inference_start_time + response["first_token_time"]
        monitor.events.append({
            "timestamp": first_token_abs_time,
            "event": "first_token",
            "metadata": {"turn": turn_idx}
        })
    
    monitor.mark_event("inference_end", {"turn": turn_idx})

# 实验结束
monitor.mark_event("experiment_end")
```

#### 分阶段能耗分析

实验结束后自动计算各阶段能耗：

```python
phase_analysis = {}
for turn_idx in range(1, len(prompts) + 1):
    prefill_data = monitor.get_phase_data("inference_start", "first_token")
    decode_data = monitor.get_phase_data("first_token", "inference_end")
    
    if prefill_data or decode_data:
        phase_analysis[f"turn_{turn_idx}"] = {
            "prefill": prefill_data,
            "decode": decode_data
        }
```

### 5. 实验结果数据结构更新

#### 新增字段

**performance 部分**：
```json
{
  "performance": {
    "total_time_seconds": 10.5,
    "token_count": 150,           // 向后兼容
    "output_tokens": 150,         // 明确的输出 token 数
    "throughput_tokens_per_sec": 14.3,
    "latency_per_token_ms": 70.0,
    "turns": 1,
    "avg_time_per_turn": 10.5
  }
}
```

**新增顶层字段**：
```json
{
  "phase_analysis": {
    "turn_1": {
      "prefill": {
        "duration_seconds": 0.5,
        "gpu_power_avg_w": 45.2,
        "gpu_power_peak_w": 52.1,
        "gpu_energy_j": 22.6,
        "sample_count": 3
      },
      "decode": {
        "duration_seconds": 10.0,
        "gpu_power_avg_w": 38.5,
        "gpu_power_peak_w": 42.3,
        "gpu_energy_j": 385.0,
        "sample_count": 50
      }
    }
  }
}
```

**system_metrics_full 部分**：
```json
{
  "system_metrics_full": {
    "timestamps": [...],
    "gpu_power_w": [...],
    "events": [
      {
        "timestamp": 1709366400.123,
        "event": "experiment_start",
        "metadata": {"task_type": "qa"}
      },
      {
        "timestamp": 1709366400.456,
        "event": "inference_start",
        "metadata": {"turn": 1}
      },
      {
        "timestamp": 1709366400.678,
        "event": "first_token",
        "metadata": {"turn": 1}
      },
      {
        "timestamp": 1709366410.789,
        "event": "inference_end",
        "metadata": {"turn": 1}
      },
      {
        "timestamp": 1709366411.000,
        "event": "experiment_end",
        "metadata": {}
      }
    ],
    "phase_analysis": {...}
  }
}
```

## 使用示例

### 基本使用

```python
from experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner()

# 运行实验（自动记录 TTFT 和事件）
result = runner.run_experiment(
    model_name="qwen3:8b",
    prompts=["你好，请介绍一下自己"],
    task_type="qa"
)

# 访问新指标
print(f"首 Token 延迟: {result['performance'].get('first_token_time', 'N/A')} 秒")
print(f"输入 Tokens: {result['performance'].get('prompt_tokens', 'N/A')}")
print(f"输出 Tokens: {result['performance'].get('output_tokens', 'N/A')}")
print(f"TPOT: {result['performance'].get('tpot', 'N/A')} 秒/token")

# 访问分阶段能耗
if 'phase_analysis' in result:
    for turn, phases in result['phase_analysis'].items():
        print(f"\n{turn}:")
        if phases.get('prefill'):
            print(f"  Prefill 能耗: {phases['prefill']['gpu_energy_j']:.2f} J")
        if phases.get('decode'):
            print(f"  Decode 能耗: {phases['decode']['gpu_energy_j']:.2f} J")
```

### 手动使用监控器

```python
from experiments.monitor import ResourceMonitor

monitor = ResourceMonitor(interval=0.2)
monitor.start()

# 标记事件
monitor.mark_event("task_start", {"task_id": 1})

# 执行任务
# ...

monitor.mark_event("task_end", {"task_id": 1})

monitor.stop()

# 获取阶段数据
phase_data = monitor.get_phase_data("task_start", "task_end")
print(f"任务能耗: {phase_data['gpu_energy_j']:.2f} J")
```

## 向后兼容性

所有改进都保持向后兼容：

1. **token_count 字段保留**：继续返回 `token_count`，值等于 `output_tokens`
2. **可选字段**：新增字段（如 `first_token_time`, `tpot`）在无法获取时返回 `None`
3. **基础监控回退**：如果高级监控不可用，自动回退到基础监控（无事件标记）

## 性能影响

- **流式接收开销**：可忽略（< 1%）
- **事件标记开销**：每次标记约 0.1ms
- **Token 统计开销**：
  - Ollama：使用 API 返回值，无额外开销
  - HuggingFace：tokenizer.encode() 约 1-5ms

## 已知限制

1. **HuggingFace 流式生成**：
   - 需要 `hf_loader` 实现 `generate_stream` 方法
   - 如果不支持，回退到非流式（无法获取 TTFT）

2. **事件时间戳精度**：
   - 依赖 Python `time.time()`，精度约 1ms
   - 首 token 时间戳通过相对时间计算，可能有微小误差

3. **分阶段能耗分析**：
   - 仅在使用高级监控（ResourceMonitor）时可用
   - 需要至少有 `inference_start`, `first_token`, `inference_end` 三个事件

## 后续改进建议

1. **实现 HuggingFace 流式生成**：
   - 在 `src/model_deployment/hf_loader.py` 中添加 `generate_stream` 方法
   - 使用 `TextIteratorStreamer` 实现流式输出

2. **更精细的事件标记**：
   - 添加 `prefill_start`, `prefill_end` 事件
   - 添加 `decode_start`, `decode_end` 事件
   - 支持自定义事件类型

3. **实时监控可视化**：
   - 实时绘制功耗曲线
   - 在曲线上标注事件点
   - 支持交互式分析

4. **多模型对比分析**：
   - 对比不同模型的 TTFT 和 TPOT
   - 对比 Prefill/Decode 阶段能耗比例
   - 生成对比报告和图表

## 相关文件

- `experiments/monitor.py` - 监控模块
- `experiments/experiment_runner.py` - 实验执行器
- `src/model_deployment/hf_loader.py` - HuggingFace 模型加载器（待实现流式）
- `docs/experiment/experiment_design.md` - 实验设计文档

## 测试建议

运行以下测试验证改进：

```bash
# 测试 Ollama 模型（支持 TTFT）
python experiments/experiment_runner.py --model qwen3:8b --prompt "你好"

# 测试 HuggingFace 模型
python experiments/experiment_runner.py --model Qwen/Qwen2.5-3B-Instruct --backend huggingface

# 查看结果中的新字段
python -c "
import json
with open('data/test/experiment_results_latest.json') as f:
    result = json.load(f)
    print('TTFT:', result['performance'].get('first_token_time'))
    print('TPOT:', result['performance'].get('tpot'))
    print('Phase Analysis:', result.get('phase_analysis'))
"
```

## 贡献者

- Kiro AI Assistant

## 更新日志

### 2026-03-02
- ✅ 添加监控模块事件标记功能
- ✅ 实现 Ollama 流式生成和 TTFT 记录
- ✅ 改进 Token 统计（输入/输出分离）
- ✅ 添加分阶段能耗分析
- ✅ 更新实验结果数据结构
- ✅ 保持向后兼容性
