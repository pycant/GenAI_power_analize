# Ollama 模型量化完整指南

## Ollama 量化概述

Ollama 使用 GGUF 格式，所有模型都是预量化的。当你运行 `ollama pull` 时，默认下载的就是量化版本。

## 量化级别说明

### GGUF 量化格式

Ollama 支持多种量化级别，从高精度到高压缩：

| 量化级别 | 位数 | 相对大小 | 质量 | 速度 | 推荐用途 |
|---------|------|---------|------|------|---------|
| **Q2_K** | 2-bit | ~25% | 较低 | 最快 | 极限压缩，测试用 |
| **Q3_K_S** | 3-bit | ~35% | 中低 | 很快 | 资源受限环境 |
| **Q3_K_M** | 3-bit | ~38% | 中等 | 很快 | 平衡压缩和质量 |
| **Q3_K_L** | 3-bit | ~40% | 中高 | 快 | 较好的 3-bit 选择 |
| **Q4_0** | 4-bit | ~45% | 中等 | 快 | 基础 4-bit |
| **Q4_K_S** | 4-bit | ~48% | 良好 | 快 | 小型 4-bit |
| **Q4_K_M** | 4-bit | ~50% | 很好 | 快 | **推荐默认** ⭐ |
| **Q5_0** | 5-bit | ~55% | 很好 | 中等 | 更高质量 |
| **Q5_K_S** | 5-bit | ~58% | 很好 | 中等 | 小型 5-bit |
| **Q5_K_M** | 5-bit | ~60% | 优秀 | 中等 | 高质量 5-bit |
| **Q6_K** | 6-bit | ~70% | 优秀 | 较慢 | 接近原始质量 |
| **Q8_0** | 8-bit | ~85% | 极好 | 慢 | 最高质量量化 |
| **F16** | 16-bit | ~100% | 完美 | 最慢 | 原始精度 |

### 你当前使用的量化级别

你的所有 Ollama 模型都是 **Q4_K_M**：

```bash
deepseek-r1:8b    # Q4_K_M, 5.2GB
gemma3:4b         # Q4_K_M, 3.3GB
qwen3:8b          # Q4_K_M, 5.2GB
qwen3:4b          # Q4_K_M, 2.5GB
```

**Q4_K_M 特点**：
- ✅ 质量和性能的最佳平衡
- ✅ 适合大多数应用场景
- ✅ 显存占用合理（RTX 4060 8GB 可轻松运行）
- ✅ 推理速度快

## 如何使用不同量化级别

### 方法 1: 下载时指定量化级别

```bash
# 默认（通常是 Q4_K_M）
ollama pull qwen3:8b

# 指定量化级别
ollama pull qwen3:8b-q2_k      # 2-bit
ollama pull qwen3:8b-q3_k_m    # 3-bit medium
ollama pull qwen3:8b-q4_k_m    # 4-bit medium (默认)
ollama pull qwen3:8b-q5_k_m    # 5-bit medium
ollama pull qwen3:8b-q6_k      # 6-bit
ollama pull qwen3:8b-q8_0      # 8-bit
ollama pull qwen3:8b-fp16      # 16-bit (原始精度)
```

### 方法 2: 查看可用的量化版本

```bash
# 列出模型的所有可用标签
ollama list

# 在 Ollama 库中搜索
# 访问: https://ollama.com/library/qwen3
```

### 方法 3: 自定义量化（高级）

如果你有原始模型，可以使用 `llama.cpp` 工具自己量化：

```bash
# 1. 转换为 GGUF 格式
python convert.py model_path --outtype f16 --outfile model.gguf

# 2. 量化
./quantize model.gguf model-q4_k_m.gguf Q4_K_M

# 3. 导入 Ollama
ollama create my-model -f Modelfile
```

## 量化级别选择建议

### 根据硬件选择

**8GB 显存（你的配置）**：
- ✅ Q4_K_M - 推荐，最佳平衡
- ✅ Q5_K_M - 如果只运行小模型（<7B）
- ⚠️ Q6_K - 仅适用于 4B 以下模型
- ❌ Q8_0/F16 - 显存不足

**16GB 显存**：
- ✅ Q5_K_M - 推荐
- ✅ Q6_K - 高质量
- ⚠️ Q8_0 - 小模型可用

**24GB+ 显存**：
- ✅ Q6_K - 推荐
- ✅ Q8_0 - 高质量
- ✅ F16 - 原始精度

### 根据任务选择

**代码生成**：
- 推荐 Q4_K_M 或更高
- 精度对代码质量影响较大

**对话/QA**：
- Q4_K_M 足够
- Q3_K_M 也可接受

**创意写作**：
- Q4_K_M 或 Q5_K_M
- 更高精度可能产生更丰富的输出

**翻译**：
- Q4_K_M 推荐
- 精度对翻译质量有明显影响

## 量化对性能的影响

### 质量损失

```
F16 (基准)     ━━━━━━━━━━ 100%
Q8_0           ━━━━━━━━━  98%
Q6_K           ━━━━━━━━   95%
Q5_K_M         ━━━━━━━    92%
Q4_K_M         ━━━━━━     88%  ← 你当前使用
Q3_K_M         ━━━━       75%
Q2_K           ━━         60%
```

### 速度提升

```
F16            ━━━━━━━━━━ 1.0x (基准)
Q8_0           ━━━━━━━━━━ 1.2x
Q6_K           ━━━━━━━━━━ 1.5x
Q5_K_M         ━━━━━━━━━━ 1.8x
Q4_K_M         ━━━━━━━━━━ 2.2x  ← 你当前使用
Q3_K_M         ━━━━━━━━━━ 2.8x
Q2_K           ━━━━━━━━━━ 3.5x
```

### 显存占用

以 7B 模型为例：

```
F16:    ~14 GB
Q8_0:   ~12 GB
Q6_K:   ~10 GB
Q5_K_M: ~8.5 GB
Q4_K_M: ~7 GB   ← 你当前使用
Q3_K_M: ~5 GB
Q2_K:   ~3.5 GB
```

## 实验建议

### 对于质效比评估

你当前的 **Q4_K_M** 配置非常适合：

1. **公平对比**：所有 Ollama 模型使用相同量化级别
2. **性能平衡**：质量损失可接受，速度提升明显
3. **显存友好**：8GB 显存可同时测试多个模型

### 如果想测试量化影响

可以下载同一模型的不同量化版本进行对比：

```bash
# 下载 Qwen3 8B 的多个量化版本
ollama pull qwen3:8b-q3_k_m    # 3-bit
ollama pull qwen3:8b-q4_k_m    # 4-bit (已有)
ollama pull qwen3:8b-q5_k_m    # 5-bit
```

然后在实验中对比：
- 质量差异（BARTScore, 准确率等）
- 效率差异（吞吐量、延迟、能耗）
- 质效比变化

## 查看当前模型信息

```bash
# 查看已安装的模型
ollama list

# 查看模型详细信息
ollama show qwen3:8b

# 查看模型文件大小
ollama show qwen3:8b --modelfile
```

## 常见问题

### Q1: 为什么 Ollama 默认使用 Q4_K_M？

**A**: Q4_K_M 是质量、速度和显存占用的最佳平衡点，适合大多数用户。

### Q2: 可以在 Ollama 中使用 HuggingFace 的 4-bit 模型吗？

**A**: 不能直接使用。HuggingFace 的 4-bit（bitsandbytes）和 Ollama 的 Q4_K_M（GGUF）是不同的量化格式。需要转换。

### Q3: Q4_K_M 和 HuggingFace 4-bit 哪个更好？

**A**: 
- **GGUF Q4_K_M**（Ollama）：更快，显存占用更少，适合推理
- **bitsandbytes 4-bit**（HF）：质量稍好，适合微调，需要更多显存

### Q4: 如何选择最适合我的量化级别？

**A**: 
1. 从 Q4_K_M 开始（默认推荐）
2. 如果质量不够，尝试 Q5_K_M 或 Q6_K
3. 如果速度不够，尝试 Q3_K_M
4. 根据实际测试结果调整

## 相关资源

- [Ollama 官方文档](https://github.com/ollama/ollama)
- [GGUF 格式说明](https://github.com/ggerganov/llama.cpp)
- [量化方法对比](https://github.com/ggerganov/llama.cpp/pull/1684)

---

**最后更新**: 2026-03-03  
**适用版本**: Ollama 0.13.2+
