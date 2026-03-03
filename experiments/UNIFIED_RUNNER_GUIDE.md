# 统一实验运行器使用指南

本指南介绍如何使用 `unified_runner.py` 运行混合模型（Ollama + Hugging Face）实验。

## 功能特性

- ✅ 统一接口调用Ollama和Hugging Face模型
- ✅ 支持4bit/8bit量化
- ✅ 自动资源监控（CPU、GPU、内存、能耗）
- ✅ BARTScore质量评估
- ✅ 实时结果保存
- ✅ 模型缓存管理

## 模型规格格式

### Ollama模型

```
格式: "model_name" 或 "ollama:model_name"

示例:
- "qwen3:4b"
- "ollama:deepseek-r1:8b"
- "gemma3:4b"
```

### Hugging Face模型

```
格式: "hf:model_path" 或 "hf:model_path:quantize"

示例:
- "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit"
- "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:8bit"
- "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct"  # 默认fp16
```

量化选项:
- `4bit`: 4位量化，最省显存（推荐8GB显存）
- `8bit`: 8位量化，平衡性能
- 不指定: 使用fp16（需要更多显存）

## 快速开始

### 1. 运行示例实验

```bash
# 激活conda环境
conda activate bartscore

# 运行示例测试用例（包含Ollama和HF模型）
python experiments/unified_runner.py --sample
```

### 2. 使用配置文件

```bash
# 使用预定义的混合模型配置
python experiments/unified_runner.py --config experiments/test_cases_mixed.json

# 指定输出目录
python experiments/unified_runner.py --config experiments/test_cases_mixed.json --output-dir results/experiment_2
```

## 配置文件格式

创建 JSON 格式的测试用例配置文件：

```json
[
  {
    "model": "qwen3:4b",
    "prompt": "请解释什么是机器学习。",
    "task_type": "qa",
    "reference_text": "机器学习是...",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
    "prompt": "请解释什么是机器学习。",
    "task_type": "qa",
    "reference_text": "机器学习是...",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9
  }
]
```

### 字段说明

- `model` (必需): 模型规格字符串
- `prompt` (必需): 输入提示
- `task_type` (必需): 任务类型 (qa, code, creative, summary)
- `reference_text` (可选): 参考文本，用于质量评估
- `max_tokens` (可选): 最大生成token数，默认500
- `temperature` (可选): 温度参数，默认0.7
- `top_p` (可选): Top-p采样参数，默认0.9

## 实验结果

### 输出文件

结果保存为JSON格式，包含以下信息：

```json
{
  "model_spec": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
  "model_info": {
    "type": "huggingface",
    "path": "models/huggingface/Qwen--Qwen2.5-3B-Instruct",
    "quantize": "4bit",
    "display_name": "HF:Qwen2.5-3B-Instruct:4bit"
  },
  "prompt": "请解释什么是机器学习。",
  "task_type": "qa",
  "generated_text": "机器学习是...",
  "performance": {
    "total_time_seconds": 2.5,
    "token_count": 150,
    "throughput_tokens_per_sec": 60.0,
    "latency_per_token_ms": 16.67
  },
  "resources": {
    "cpu_percent_avg": 45.2,
    "cpu_percent_peak": 78.5,
    "mem_used_peak_mb": 8192.0,
    "gpu_util_avg": 85.3,
    "gpu_util_peak": 95.2,
    "gpu_mem_peak_mb": 6144.0,
    "gpu_power_avg_w": 75.5,
    "gpu_energy_j": 188.75,
    "gpu_temp_peak_c": 72.0,
    "cpu_energy_j_approx": 162.5
  },
  "quality": {
    "bartscore": -2.45,
    "has_reference": true
  },
  "metadata": {
    "timestamp": "2024-01-15T10:30:00",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

### 关键指标

**性能指标**:
- `total_time_seconds`: 总生成时间
- `throughput_tokens_per_sec`: 吞吐量（tokens/秒）
- `latency_per_token_ms`: 每token延迟（毫秒）

**资源指标**:
- `gpu_energy_j`: GPU能耗（焦耳）
- `gpu_util_avg`: 平均GPU利用率
- `gpu_mem_peak_mb`: 峰值GPU显存（MB）
- `cpu_energy_j_approx`: 估算CPU能耗（焦耳）

**质量指标**:
- `bartscore`: BARTScore质量分数（越高越好）

## 使用场景

### 场景1: 对比Ollama和HF模型

```json
[
  {
    "model": "qwen3:4b",
    "prompt": "相同的提示词",
    "task_type": "qa",
    "max_tokens": 200
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
    "prompt": "相同的提示词",
    "task_type": "qa",
    "max_tokens": 200
  }
]
```

### 场景2: 对比不同量化方案

```json
[
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompt": "测试提示词",
    "task_type": "qa"
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:8bit",
    "prompt": "测试提示词",
    "task_type": "qa"
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct",
    "prompt": "测试提示词",
    "task_type": "qa"
  }
]
```

### 场景3: 多任务评估

```json
[
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompt": "QA任务提示",
    "task_type": "qa"
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompt": "代码生成提示",
    "task_type": "code"
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompt": "创意写作提示",
    "task_type": "creative"
  }
]
```

## 性能优化建议

### 1. 显存管理

基于你的硬件（RTX 4060 8GB）：

```python
# 推荐配置
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
  "max_tokens": 512  # 避免过长生成
}

# 如果显存不足，使用更小的模型
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit"
}
```

### 2. 批量实验

```bash
# 分批运行，避免显存累积
python experiments/unified_runner.py --config batch1.json
python experiments/unified_runner.py --config batch2.json
```

### 3. 模型缓存

首次加载HF模型会较慢，但后续实验会使用缓存：

```
第一次: 加载模型 (30-60秒) + 生成 (2-5秒)
后续: 从缓存加载 (1秒) + 生成 (2-5秒)
```

## 与现有实验框架集成

### 方法1: 直接替换

```bash
# 原来使用 experiment_runner.py
python experiments/experiment_runner.py --config test_cases.json

# 现在使用 unified_runner.py（支持HF模型）
python experiments/unified_runner.py --config test_cases_mixed.json
```

### 方法2: 并行使用

```bash
# Ollama实验
python experiments/experiment_runner.py --config ollama_cases.json

# HF实验
python experiments/unified_runner.py --config hf_cases.json

# 混合实验
python experiments/unified_runner.py --config mixed_cases.json
```

## 常见问题

### Q1: HF模型加载失败

```
错误: Hugging Face模型加载器不可用
```

解决方案:
```bash
pip install transformers huggingface_hub accelerate bitsandbytes
```

### Q2: 显存不足

```
错误: CUDA out of memory
```

解决方案:
1. 使用4bit量化
2. 减小max_tokens
3. 使用更小的模型
4. 关闭其他GPU程序

### Q3: 量化不生效

```
警告: bitsandbytes不可用
```

解决方案:
```bash
# Windows用户可能需要特定版本
pip install bitsandbytes --prefer-binary

# 或者不使用量化（需要更多显存）
"model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct"
```

### Q4: 模型路径错误

```
错误: 模型文件不存在
```

解决方案:
```bash
# 先下载模型
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct --quantize 4bit

# 检查模型路径
python scripts/manage_models.py --list
```

## 最佳实践

1. **先测试小模型**: 使用3B模型验证配置正确
2. **逐步增加规模**: 确认无误后再使用7B+模型
3. **监控资源使用**: 注意GPU显存和温度
4. **保存中间结果**: 实验会实时保存，可随时中断
5. **对比分析**: 使用相同提示词对比不同模型

## 下一步

1. ✅ 运行示例实验
2. ✅ 创建自定义配置
3. ✅ 对比Ollama和HF模型
4. ⏭️ 分析实验结果
5. ⏭️ 生成评估报告

参考文档:
- [HF模型使用指南](../docs/experiment/hf_models_guide.md)
- [模型下载配置](../configs/models_to_download.yaml)
- [快速开始](../HUGGINGFACE_SETUP.md)
