# GPU 优先加载策略

## 目的

为了保证实验的严谨性和结果的可比性，我们实现了"GPU 优先加载"策略：
1. **优先尝试**：将模型完全加载到 GPU
2. **失败回退**：只有在显存不足时才使用 CPU offload
3. **明确标注**：在结果中清楚标注是否使用了 CPU offload

## 实现策略

### 加载流程

```python
# 1. 第一次尝试：完全加载到 GPU
device_map_config = {"": 0}  # 将所有层放在 GPU 0

try:
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=quantization_config,
        device_map=device_map_config,  # 强制使用 GPU
        ...
    )
    print("✓ 模型已完全加载到 GPU")
    
except (RuntimeError, ValueError) as e:
    # 2. 如果显存不足，回退到 CPU offload
    if "out of memory" in str(e).lower() or "cuda" in str(e).lower():
        print("⚠️ GPU 显存不足，尝试使用 CPU offload...")
        device_map_config = "auto"  # 自动分配到 GPU + CPU
        
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=quantization_config,
            device_map=device_map_config,  # 允许 CPU offload
            ...
        )
        print("✓ 模型已加载（使用 CPU offload）")
        print("⚠️ 注意：使用 CPU offload 可能影响推理速度和结果可比性")
```

### 信息显示

加载完成后，系统会显示详细的设备映射信息：

```
模型信息:
   总参数: 7,615,616,000
   可训练参数: 7,615,616,000
   量化: 4bit
   设备映射: {'model.embed_tokens': 0, 'model.layers.0': 0, ..., 'model.layers.27': 'cpu', 'lm_head': 'cpu'}
   ⚠️  CPU Offload: 是 (3/30 层在 CPU)
   ⚠️  注意: 使用 CPU offload 会影响推理速度和能耗测量
   显存占用: 6.05 GB (已分配)
   显存预留: 7.22 GB (已预留)
```

或者（完全在 GPU 上）：

```
模型信息:
   总参数: 3,821,079,552
   可训练参数: 3,821,079,552
   量化: 4bit
   设备映射: {'': 0}
   ✓ 完全在 GPU 上运行
   显存占用: 2.85 GB (已分配)
   显存预留: 3.12 GB (已预留)
```

## 优势

### 1. 实验严谨性
- **一致的测试环境**：所有能在 GPU 上运行的模型都在相同环境下测试
- **可比的结果**：避免因设备差异导致的性能波动
- **明确的限制**：清楚知道哪些模型需要 CPU offload

### 2. 性能优化
- **最大化 GPU 利用**：充分利用 GPU 的计算能力
- **避免不必要的 offload**：只在真正需要时才使用 CPU
- **更快的推理速度**：GPU 推理比 CPU 快 10-100 倍

### 3. 结果可解释性
- **清晰的标注**：结果中明确标注是否使用了 CPU offload
- **性能差异说明**：用户可以理解为什么某些模型速度较慢
- **能耗测量准确性**：CPU offload 会影响能耗测量的准确性

## 对不同模型的影响

### RTX 4060 8GB 显卡

#### 完全在 GPU 上运行 ✅
- **Qwen 3B 4-bit**：约 2-3GB 显存
- **Phi-3 mini 4-bit**：约 2-3GB 显存
- **Gemma 2B 4-bit**：约 1-2GB 显存

#### 需要 CPU Offload ⚠️
- **Qwen 7B 4-bit**：约 4-6GB 显存（部分层在 CPU）
- **Llama 7B 4-bit**：约 4-6GB 显存（部分层在 CPU）
- **Mistral 7B 4-bit**：约 4-6GB 显存（部分层在 CPU）

#### 无法运行 ❌
- **Qwen 14B 4-bit**：需要 8-12GB 显存
- **Llama 13B 4-bit**：需要 8-12GB 显存

## 实验建议

### 1. 优先使用完全在 GPU 上的模型
对于严格的性能对比实验，建议只使用能完全加载到 GPU 的模型：
- Qwen 3B-4B
- Phi-3 mini
- Gemma 2B-4B
- 或使用 Ollama 模型（已优化）

### 2. 分组对比
如果需要测试 7B 模型，建议分组对比：
- **组 A（GPU only）**：3B-4B 模型，完全在 GPU 上
- **组 B（CPU offload）**：7B 模型，使用 CPU offload
- 不要直接对比组 A 和组 B 的绝对性能

### 3. 标注结果
在实验报告中明确标注：
- 哪些模型完全在 GPU 上运行
- 哪些模型使用了 CPU offload
- CPU offload 对性能的影响（通常慢 2-5 倍）

## 与 bitsandbytes 4-bit 量化的兼容性

### 问题
之前我们发现 bitsandbytes 的 4-bit 量化与 CPU offload 不兼容：
```
ValueError: Blockwise quantization only supports 16/32-bit floats, but got torch.uint8
```

### 解决方案
通过"GPU 优先"策略：
1. **小模型（3B-4B）**：完全在 GPU 上，无问题 ✅
2. **中等模型（7B）**：
   - 第一次尝试 GPU only → 可能失败
   - 回退到 CPU offload → 仍然会失败（bitsandbytes 限制）
   - **建议**：使用 Ollama 或 8-bit 量化

### 最终建议
对于 RTX 4060 8GB + bitsandbytes 4-bit：
- ✅ **推荐**：使用 3B-4B 模型（完全在 GPU）
- ✅ **推荐**：使用 Ollama 模型（任何大小）
- ⚠️ **备选**：使用 7B 模型 + 8-bit 量化
- ❌ **不推荐**：使用 7B 模型 + 4-bit 量化（会失败）

## 代码示例

### 测试配置（推荐）

```json
[
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
    "task_type": "qa",
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "comment": "完全在 GPU 上运行"
  },
  {
    "model": "qwen3:4b",
    "task_type": "qa",
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "comment": "Ollama 模型，已优化"
  }
]
```

### 测试配置（不推荐）

```json
[
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "task_type": "qa",
    "max_tokens": 100,
    "temperature": 0.7,
    "top_p": 0.9,
    "comment": "会尝试 CPU offload，但会失败"
  }
]
```

## 监控和日志

系统会在日志中记录：
1. 是否尝试了 GPU only 加载
2. 是否回退到 CPU offload
3. 最终的设备映射
4. CPU offload 的警告信息

示例日志：
```
🤖 加载模型...
   尝试完全加载到 GPU...
   ⚠️  GPU 显存不足，尝试使用 CPU offload...
   ✓ 模型已加载（使用 CPU offload）
   ⚠️  注意：使用 CPU offload 可能影响推理速度和结果可比性

模型信息:
   总参数: 7,615,616,000
   可训练参数: 7,615,616,000
   量化: 4bit
   设备映射: {...}
   ⚠️  CPU Offload: 是 (3/30 层在 CPU)
   ⚠️  注意: 使用 CPU offload 会影响推理速度和能耗测量
```

## 总结

"GPU 优先加载"策略确保：
1. ✅ 最大化实验严谨性
2. ✅ 最优化推理性能
3. ✅ 明确标注设备使用情况
4. ✅ 提供清晰的性能预期

对于 RTX 4060 8GB 显卡，建议使用 3B-4B 模型或 Ollama 模型进行严格的性能对比实验。
