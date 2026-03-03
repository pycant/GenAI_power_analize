# Hugging Face 4-bit 量化问题总结

## 问题概述

在尝试使用 Hugging Face 模型的 4-bit 量化时，遇到了多个兼容性问题。这些问题主要与 `bitsandbytes` 库、CPU offload 和模型架构有关。

## 遇到的问题

### 问题 1：显存不足需要 CPU Offload

**错误信息**：
```
ValueError: Some modules are dispatched on the CPU or the disk. Make sure you have enough GPU RAM to fit the
quantized model. If you want to dispatch the model on the CPU or the disk while keeping these modules
in 32-bit, you need to set `llm_int8_enable_fp32_cpu_offload=True`
```

**原因**：
- Qwen 7B 模型即使使用 4-bit 量化，仍需要约 6GB 显存
- RTX 4060 8GB 显存在加载模型后剩余空间不足
- 需要将部分层 offload 到 CPU

### 问题 2：CPU Offload 与 4-bit 量化不兼容

**错误信息**：
```
ValueError: Blockwise quantization only supports 16/32-bit floats, but got torch.uint8
```

**原因**：
- 当启用 `llm_int8_enable_fp32_cpu_offload=True` 后，模型的某些层被分配到 CPU
- 在推理时，这些层需要从 CPU 移回 GPU
- bitsandbytes 尝试重新量化这些层时，发现权重已经是 `uint8` 类型（已量化）
- bitsandbytes 的量化函数期望输入是 `float16` 或 `float32`，但收到了 `uint8`

**技术细节**：
```python
# 错误发生在 bitsandbytes/functional.py:1244
def quantize_4bit(A, ...):
    if A.dtype not in [torch.float16, torch.float32]:
        raise ValueError(f"Blockwise quantization only supports 16/32-bit floats, but got {A.dtype}")
```

### 问题 3：Phi-3 模型的数值稳定性问题

**错误信息**（在修复 CPU offload 问题前）：
```
RuntimeError: probability tensor contains either `inf`, `nan` or element < 0
```

**原因**：
- Phi-3 模型在使用 4-bit 量化时对数值精度非常敏感
- 低 temperature 值（如 0.1）可能导致概率分布出现数值不稳定

## 根本原因分析

这是 `bitsandbytes` 库的一个已知限制：

1. **4-bit 量化 + CPU offload 不兼容**：
   - bitsandbytes 的 4-bit 量化设计为完全在 GPU 上运行
   - 当层被 offload 到 CPU 时，权重被保存为量化后的 `uint8` 格式
   - 移回 GPU 时，bitsandbytes 尝试重新量化，但无法处理已量化的数据

2. **device_map="auto" 的行为**：
   - `device_map="auto"` 会自动将模型分配到 GPU 和 CPU
   - 对于大模型，这会导致部分层在 CPU 上
   - 这与 4-bit 量化的要求冲突

## 解决方案对比

### 方案 1：使用 Ollama 模型（推荐）✅

**优点**：
- 模型已预先量化，无需运行时量化
- 完全避免 bitsandbytes 的兼容性问题
- 推理速度更快，显存占用更低
- 支持流式输出和上下文保持
- 更稳定可靠

**缺点**：
- 需要单独下载 Ollama 模型
- 模型选择相对有限

**示例**：
```json
{
  "model": "qwen3:4b",
  "task_type": "qa",
  "max_tokens": 100,
  "temperature": 0.1,
  "top_p": 0.9
}
```

### 方案 2：使用 8-bit 量化

**优点**：
- 8-bit 量化与 CPU offload 兼容性更好
- 仍能显著减少显存占用

**缺点**：
- 显存占用比 4-bit 高（约 2倍）
- 对于 7B 模型，可能仍需要 CPU offload

**配置**：
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:8bit",
  ...
}
```

### 方案 3：使用更小的模型

**优点**：
- 完全在 GPU 上运行，无需 CPU offload
- 推理速度更快

**缺点**：
- 模型能力可能不足

**示例**：
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
  ...
}
```

### 方案 4：使用非量化模型（FP16）

**优点**：
- 无量化相关问题
- 推理质量最好

**缺点**：
- 显存需求高（7B 模型需要 14GB+）
- RTX 4060 8GB 无法运行

## 推荐配置

### 对于 RTX 4060 8GB 显卡

1. **首选：Ollama 模型**
   ```json
   {
     "model": "qwen3:4b",      // 或 "qwen3:8b", "gemma3:4b", "deepseek-r1:8b"
     "task_type": "qa",
     "max_tokens": 100,
     "temperature": 0.7,
     "top_p": 0.9
   }
   ```

2. **备选：HF 小模型 + 4-bit**
   ```json
   {
     "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
     "task_type": "qa",
     "max_tokens": 100,
     "temperature": 0.7,
     "top_p": 0.9
   }
   ```

3. **备选：HF 中等模型 + 8-bit**
   ```json
   {
     "model": "hf:models/huggingface/microsoft--phi-3-mini-4k-instruct:8bit",
     "task_type": "qa",
     "max_tokens": 100,
     "temperature": 0.7,
     "top_p": 0.9
   }
   ```

## 测试文件

### 成功的测试配置（Ollama）

文件：`data/experiment_test/test_cases_ollama.json`

```json
[
  {
    "model": "qwen3:4b",
    "task_type": "qa",
    "max_tokens": 100,
    "temperature": 0.1,
    "top_p": 0.9,
    "idle_measurement_duration": 10,
    "prompts": "Statement 1| In a Bayesian network...",
    "reference_text": "True, False"
  },
  {
    "model": "gemma3:4b",
    "task_type": "multi_turn",
    "max_tokens": 150,
    "temperature": 0.7,
    "top_p": 0.9,
    "idle_measurement_duration": 10,
    "prompts": [
      "今天天气怎么样？",
      "适合户外运动吗？",
      "那我应该穿什么衣服？"
    ],
    "keep_context": true
  }
]
```

运行命令：
```bash
conda activate bartscore
python experiments/experiment_runner.py --config data/experiment_test/test_cases_ollama.json --output-dir data/experiment_test
```

### 失败的测试配置（HF 4-bit + CPU offload）

文件：`data/experiment_test/test_cases.json`

这个配置会失败，因为：
- Qwen 7B 4-bit 需要 CPU offload
- Phi-3 mini 4-bit 需要 CPU offload
- CPU offload 与 4-bit 量化不兼容

## 相关资源

### bitsandbytes 问题追踪
- [Issue #1483: CPU offload with 4-bit quantization](https://github.com/huggingface/transformers/issues/1483)
- [bitsandbytes documentation](https://huggingface.co/docs/bitsandbytes/main/en/index)

### Ollama 文档
- [Ollama官网](https://ollama.ai/)
- [Ollama模型库](https://ollama.ai/library)
- [Ollama API文档](https://github.com/ollama/ollama/blob/main/docs/api.md)

## 环境信息

- **操作系统**：Windows
- **GPU**：NVIDIA GeForce RTX 4060 Laptop GPU 8GB
- **CUDA**：12.6
- **Python**：3.10
- **PyTorch**：2.x (with CUDA support)
- **bitsandbytes**：0.45.5
- **transformers**：4.x
- **Ollama**：0.13.2

## 结论

对于 RTX 4060 8GB 显卡：
1. **强烈推荐使用 Ollama 模型**，避免所有量化相关问题
2. 如果必须使用 Hugging Face 模型，选择 3B-4B 参数的小模型 + 4-bit 量化
3. 避免使用 7B+ 模型的 4-bit 量化，因为会触发 CPU offload 问题
4. 8-bit 量化是一个折中方案，但仍可能遇到显存问题

## 下一步行动

1. 更新 `data/experiments_5/test_cases.json`，使用 Ollama 模型
2. 或者使用更小的 HF 模型（3B-4B 参数）
3. 运行测试验证配置
4. 更新文档说明推荐配置
