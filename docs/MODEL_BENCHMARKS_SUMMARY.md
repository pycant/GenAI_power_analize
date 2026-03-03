# 模型基准测试与能力总结

本文档整理了所有已下载模型的官方基准测试分数、语言支持和能力特点。

## 目录

- [模型对比总览](#模型对比总览)
- [详细基准测试数据](#详细基准测试数据)
  - [Phi-3 Mini 4K Instruct](#phi-3-mini-4k-instruct)
  - [Qwen 2.5 3B Instruct](#qwen-25-3b-instruct)
  - [Qwen 2.5 7B Instruct](#qwen-25-7b-instruct)
- [语言支持对比](#语言支持对比)
- [使用建议](#使用建议)

---

## 模型对比总览

| 模型　　　　　　　| 参数量 | 官方支持语言　　　 | 上下文长度 | 主要优势　　　　　 | 适用场景　　　　　　　　　　|
| -------------------| --------| --------------------| ------------| --------------------| -----------------------------|
| **Phi-3 Mini 4K** | 3.8B　 | 英语、法语　　　　 | 4K　　　　 | 数学、代码、推理　 | 英文/法文任务，资源受限环境 |
| **Qwen 2.5 3B**　 | 3.09B　| 29+ 语言（含中文） | 32K　　　　| 多语言、指令遵循　 | 中英文通用，轻量级部署　　　|
| **Qwen 2.5 7B**　 | 7.61B　| 29+ 语言（含中文） | 128K　　　 | 长文本、结构化输出 | 复杂任务，长上下文处理　　　|

### 关键发现

1. **语言能力**：
   - Phi-3：仅支持英语和法语，中文表现极差 ❌
   - Qwen 2.5：原生支持 29+ 语言，中文能力优秀 ✅

2. **上下文长度**：
   - Phi-3 Mini：4K tokens
   - Qwen 2.5 3B：32K tokens（可扩展到 128K）
   - Qwen 2.5 7B：128K tokens

3. **参数效率**：
   - Phi-3 Mini (3.8B) 和 Qwen 2.5 3B (3.09B) 参数量相近
   - 但 Qwen 支持更多语言和更长上下文

---

## 详细基准测试数据

### Phi-3 Mini 4K Instruct

**基本信息**：
- 参数量：3.8B (3.09B non-embedding)
- 上下文长度：4K tokens
- 训练数据：4.9T tokens
- 支持语言：英语 (en)、法语 (fr)
- 训练时间：10 天（512 H100-80G）

**官方基准测试结果**：

#### 与主流模型对比

| 基准测试　　　　　　　　　　　　　| Phi-3 Mini | Gemma 7B | Mistral 7B | Mixtral 8x7B | Llama-3 8B | GPT-3.5 |     |     |     |     |
| -----------------------------------| ------------| ----------| ------------| --------------| ------------| ---------| -----| -----| -----| -----|
| **综合基准**　　　　　　　　　　　|            |          |            |              |            |         |     |     |     |     |
| AGI Eval (5-shot)　　　　　　　　 | 39.0       | 42.1     | 35.1       | 45.2         | 42.0       | 48.4    |     |     |     |     |
| MMLU (5-shot)　　　　　　　　　　 | **70.9**   | 63.6     | 61.7       | 70.5         | 66.5       | 71.4    |     |     |     |     |
| BigBench Hard CoT (3-shot)　　　　| **73.5**   | 59.6     | 57.3       | 69.7         | 51.5       | 68.3    |     |     |     |     |
| **语言理解**　　　　　　　　　　　|            |          |            |              |            |         |     |     |     |     |
| ANLI (7-shot)　　　　　　　　　　 | 53.6       | 48.7     | 47.1       | 55.2         | 57.3       | 58.1    |     |     |     |     |
| HellaSwag (5-shot)　　　　　　　　| **75.3**   | 49.8     | 58.5       | 70.4         | 71.1       | 78.8    |     |     |     |     |
| **推理能力**　　　　　　　　　　　|            |          |            |              |            |         |     |     |     |     |
| ARC Challenge (10-shot)　　　　　 | **86.3**   | 78.3     | 78.6       | 87.4         |            |         |     |     |     |     |
| BoolQ (0-shot)　　　　　　　　　　| 78.1       | 66.0     | 72.2       | 76.6         | 80.9       | 79.1    |     |     |     |     |
| MedQA (2-shot)　　　　　　　　　　| 56.5       | 49.6     | 50.0       | 62.2         | 60.5       | 63.4    |     |     |     |     |
| OpenBookQA (10-shot)　　　　　　　| 82.2       | 78.6     | 79.8       | 85.8         | 82.6       | 86.0    |     |     |     |     |
| PIQA (5-shot)　　　　　　　　　　 | **83.5**   | 78.1     | 77.7       | 86.0         | 75.7       | 86.6    |     |     |     |     |
| GPQA (0-shot)　　　　　　　　　　 | 30.6       | 2.9      | 15.0       | 6.9          | 32.4       | 30.8    |     |     |     |     |
| Social IQA (5-shot)　　　　　　　 | **77.6**   | 65.5     | 74.6       | 75.9         | 73.9       | 68.3    |     |     |     |     |
| TruthfulQA MC2 (10-shot)　　　　　| 64.7       | 52.1     | 53.0       | 60.1         | 63.2       | 67.7    |     |     |     |     |
| WinoGrande (5-shot)　　　**71.6** | 55.6       | 54.2     | 62.0       | 65.0         | 68.8       |         |     |     |     |     |
| **知识**　　　　　　　　　　　　　|            |          |            |              |            |         |     |     |     |     |
| TriviaQA (5-shot)　　　　　　　　 | 61.4       | 72.3     | 75.2       | 82.2         | 67.7       | 85.8    |     |     |     |     |
| **数学**　　　　　　　　　　　　　|            |          |            |              |            |         |     |     |     |     |
| GSM8K CoT (8-shot)　　　　　　　　| **85.7**   | 59.8     | 46.4       | 64.7         | 77.4       | 78.1    |     |     |     |     |
| **代码生成**　　　　　　　　　　　|            |          |            |              |            |         |     |     |     |     |
| HumanEval (0-shot)　　　　　　　　| 57.3       | 34.1     | 28.0       | 37.8         | 60.4       | 62.2    |     |     |     |     |
| MBPP (3-shot)　　　　　　　　　　 | **69.8**   | 51.5     | 50.8       | 60.2         | 67.7       | 77.8    |     |     |     |     |
| **平均分**　　　　　　　　　　　　| **67.6**   | 56.0     | 56.4       | 64.4         | 65.5       | 70.4    |     |     |     |     |

#### 分类能力评估（100+ 基准测试）

| 类别 | Phi-3 Mini | Gemma 7B | Mistral 7B | Mixtral 8x7B | Llama-3 8B | GPT-3.5 |
|------|----------　|            | 87.3     | 82.8       |              |            |         |     |     |     |     |）
- ✅ 代码生成（HumanEval: 57.3, MBPP: 69.8）
- ✅ 常识推理（ARC Challenge: 86.3）
- ✅ 逻辑推理（BigBench Hard: 73.5）

**劣势领域**：
- ❌ 多语言支持（仅英语/法语）
- ❌ 事实知识（TriviaQA: 61.4，相对较低）
- ❌ 上下文长度（仅 4K tokens）

**官方警告**：
> "Languages other than English will experience worse performance."
> 
> 英语以外的语言会表现更差。

---

### Qwen 2.5 3B Instruct

**基本信息**：
- 参数量：3.09B (2.77B non-embedding)
- 上下文长度：32K tokens（生成 8K tokens）
- 支持语言：29+ 语言（包括中文、英文、法文、西班牙文、葡萄牙文、德文、意大利文、俄文、日文、韩文、越南文、泰文、阿拉伯文等）
- 架构：36 层，GQA (16 Q heads, 2 KV heads)

**核心改进**（相比 Qwen2）：
- ✅ 显著增强的知识储备
- ✅ 大幅提升的编码和数学能力
- ✅ 改进的指令遵循能力
- ✅ 长文本生成能力（8K+ tokens）
- ✅ 结构化数据理解（表格等）
- ✅ 结构化输出生成（特别是 JSON）
- ✅ 对系统提示的多样性更具韧性
- ✅ 长上下文支持（最高 128K tokens）
- ✅ 29+ 语言的多语言支持

**基准测试结果**：
- 官方建议查看博客：https://qwenlm.github.io/blog/qwen2.5/
- 详细性能数据：https://qwen.readthedocs.io/en/latest/benchmark/speed_benchmark.html

**优势领域**：
- ✅ 多语言支持（29+ 语言）
- ✅ 中文能力优秀
- ✅ 指令遵循
- ✅ 长文本生成
- ✅ 结构化输出（JSON）
- ✅ 较长上下文（32K）

---

### Qwen 2.5 7B Instruct

**基本信息**：
- 参数量：7.61B (6.53B non-embedding)
- 上下文长度：128K tokens（生成 8K tokens）
- 支持语言：29+ 语言（同 3B 版本）
- 架构：28 层，GQA (28 Q heads, 4 KV heads)

**核心特性**（相比 3B）：
- ✅ 更大的模型容量
- ✅ 更长的上下文支持（128K tokens，使用 YaRN 技术）
- ✅ 更强的推理能力
- ✅ 更好的长文本处理能力

**长上下文支持**：
- 默认配置：32K tokens
- 使用 YaRN 扩展：最高 128K tokens
- 建议使用 vLLM 进行部署

**基准测试结果**：
- 官方建议查看博客：https://qwenlm.github.io/blog/qwen2.5/
- 详细性能数据：https://qwen.readthedocs.io/en/latest/benchmark/speed_benchmark.html

**优势领域**：
- ✅ 所有 3B 版本的优势
- ✅ 更强的复杂推理能力
- ✅ 超长上下文处理（128K）
- ✅ 更好的长文本生成质量

---

## 语言支持对比

### 详细语言支持表

| 模型　　　　　　| 官方支持语言 | 中文　　　 | 英文　　　 | 其他语言　　　　 |
| -----------------| --------------| ------------| ------------| ------------------|
| **Phi-3 Mini**　| en, fr　　　 | ❌ 不支持　 | ⭐⭐⭐⭐⭐ 优秀 | 法语支持　　　　 |
| **Qwen 2.5 3B** | 29+ 语言　　 | ⭐⭐⭐⭐⭐ 优秀 | ⭐⭐⭐⭐ 良好　| 29+ 语言原生支持 |
| **Qwen 2.5 7B** | 29+ 语言　　 | ⭐⭐⭐⭐⭐ 优秀 | ⭐⭐⭐⭐⭐ 优秀 | 29+ 语言原生支持 |

### Qwen 2.5 支持的语言列表

中文、英文、法文、西班牙文、葡萄牙文、德文、意大利文、俄文、日文、韩文、越南文、泰文、阿拉伯文等 29+ 种语言。

---

## 使用建议

### 按任务类型选择模型

#### 1. 英文任务

**数学和代码**：
```
推荐：Phi-3 Mini 4K
原因：在数学（GSM8K: 85.7）和代码（HumanEval: 57.3）上表现优秀
```

**通用英文对话**：
```
推荐：Qwen 2.5 7B
原因：更全面的能力，更长的上下文支持
```

**资源受限环境**：
```
推荐：Phi-3 Mini 4K 或 Qwen 2.5 3B
原因：参数量小（~3B），推理速度快
```

#### 2. 中文任务

**所有中文任务**：
```
推荐：Qwen 2.5 3B 或 7B
原因：原生中文支持，Phi-3 不支持中文
```

**简单中文对话**：
```
推荐：Qwen 2.5 3B要 CPU offload）

**推荐配置**：
```json
{
  "英文数学/代码": "hf:microsoft--phi-3-mini-4k-instruct:4bit",
  "中文通用": "hf:Qwen--Qwen2.5-3B-Instruct:4bit",
  "复杂任务": "hf:Qwen--Qwen2.5-7B-Instruct:4bit"
}
```

### 实验设计建议

#### 按语言分组测试

```json
[
  {
    "group": "英文任务",
    "models": ["phi-3-mini", "qwen-2.5-3b", "qwen-2.5-7b"],
    "prompts": ["English prompts..."]
  },
  {
    "group": "中文任务",
    "models": ["qwen-2.5-3b", "qwen-2.5-7b"],
    "prompts": ["中文提示..."],
    "note": "不包含 Phi-3，因为不支持中文"
  }
]
```

#### 按能力分组测试

```json
[
  {
    "capability": "数学推理",
    "benchmark": "GSM8K",
    "models": ["phi-3-mini", "qwen-2.5-7b"],
    "language": "en"
  },
  {
    "capability": "代码生成",
    "benchmark": "HumanEval",
    "models": ["phi-3-mini", "qwen-2.5-7b"],
    "language": "en"
  },
  {
    "capability": "中文对话",
    "benchmark": "custom",
    "models": ["qwen-2.5-3b", "qwen-2.5-7b"],
    "language": "zh"
  }
]
```

---

## 关键结论

### 1. 语言能力是首要考虑因素

- **中文任务**：必须使用 Qwen 2.5，Phi-3 完全不支持
- **英文任务**：Phi-3 和 Qwen 2.5 都可以，根据具体需求选择
- **多语言任务**：只能使用 Qwen 2.5

### 2. 参数量不等于能力

- Phi-3 Mini (3.8B) 在英文数学和代码上优于很多 7B 模型
- Qwen 2.5 3B (3.09B) 支持 29+ 语言和 32K 上下文
- 模型设计和训练数据质量比参数量更重要

### 3. 上下文长度差异巨大

- Phi-3 Mini: 4K tokens
- Qwen 2.5 3B: 32K tokens (8x)
- Qwen 2.5 7B: 128K tokens (32x)

### 4. 实验设计要考虑模型特性

- 不要用中文测试 Phi-3（会得到无意义结果）
- 不要用 Phi-3 测试长文本（超过 4K）
- 根据任务语言和复杂度选择合适的模型

---

## 参考资料

### 官方文档

- **Phi-3**: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct
- **Qwen 2.5**: https://qwenlm.github.io/blog/qwen2.5/
- **Qwen 文档**: https://qwen.readthedocs.io/

### 基准测试

- **Phi-3 技术报告**: https://aka.ms/phi3-tech-report
- **Qwen 2.5 博客**: https://qwenlm.github.io/blog/qwen2.5/
- **Qwen 性能基准**: https://qwen.readthedocs.io/en/latest/benchmark/speed_benchmark.html

### 相关文档

- [模型质量问题诊断](./MODEL_QUALITY_ISSUES.md)
- [HuggingFace 模型指南](./experiment/hf_models_guide.md)
- [实验设计指南](./experiment/experiment_design.md)

---

**最后更新**: 2026-03-03  
**维护者**: GenAI Power Analysis Team
