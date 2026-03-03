# 模型快速参考表

快速查阅模型的关键信息和使用建议。

## 一句话总结

| 模型 | 一句话描述 |
|------|-----------|
| **Phi-3 Mini 4K** | 英文数学和代码专家，不支持中文 |
| **Qwen 2.5 3B** | 轻量级多语言模型，中文能力优秀 |
| **Qwen 2.5 7B** | 全能型多语言模型，支持超长上下文 |

## 核心参数对比

| 参数 | Phi-3 Mini | Qwen 2.5 3B | Qwen 2.5 7B |
|------|-----------|------------|------------|
| 参数量 | 3.8B | 3.09B | 7.61B |
| 上下文 | 4K | 32K | 128K |
| 中文 | ❌ | ✅ | ✅ |
| 英文 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 数学 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 代码 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 显存 (4bit) | ~2.5GB | ~2.5GB | ~5-6GB |

## 使用决策树

```
需要中文支持？
├─ 是 → Qwen 2.5 系列
│   ├─ 简单任务 → Qwen 2.5 3B
│   └─ 复杂任务 → Qwen 2.5 7B
│
└─ 否（仅英文）
    ├─ 数学/代码任务 → Phi-3 Mini
    ├─ 长文本 (>4K) → Qwen 2.5 7B
    └─ 通用任务 → Qwen 2.5 3B 或 Phi-3 Mini
```

## 任务推荐速查

| 任务类型 | 推荐模型 | 备选 |
|---------|---------|------|
| 英文数学 | Phi-3 Mini | Qwen 2.5 7B |
| 英文代码 | Phi-3 Mini | Qwen 2.5 7B |
| 中文对话 | Qwen 2.5 3B | Qwen 2.5 7B |
| 中文写作 | Qwen 2.5 7B | Qwen 2.5 3B |
| 长文本理解 | Qwen 2.5 7B | - |
| 多语言翻译 | Qwen 2.5 7B | Qwen 2.5 3B |
| JSON 生成 | Qwen 2.5 3B/7B | - |
| 快速推理 | Phi-3 Mini / Qwen 2.5 3B | - |

## 基准测试亮点

### Phi-3 Mini 4K

| 基准 | 分数 | 排名 |
|------|-----|------|
| GSM8K (数学) | 85.7 | 🥇 同级别第一 |
| HumanEval (代码) | 57.3 | 🥈 同级别前列 |
| MBPP (代码) | 69.8 | 🥇 同级别第一 |
| ARC Challenge | 86.3 | 🥇 同级别第一 |
| BigBench Hard | 73.5 | 🥇 同级别第一 |

### Qwen 2.5 系列

| 特性 | 描述 |
|------|------|
| 多语言 | 29+ 语言原生支持 |
| 长上下文 | 3B: 32K, 7B: 128K |
| 结构化输出 | JSON/表格生成优秀 |
| 指令遵循 | 显著改进 |
| 中文能力 | 业界领先 |

## 实验配置建议

### 英文实验

```json
{
  "models": [
    "hf:microsoft--phi-3-mini-4k-instruct:4bit",
    "hf:Qwen--Qwen2.5-3B-Instruct:4bit",
    "hf:Qwen--Qwen2.5-7B-Instruct:4bit"
  ],
  "language": "en",
  "prompts": ["English prompts..."]
}
```

### 中文实验

```json
{
  "models": [
    "hf:Qwen--Qwen2.5-3B-Instruct:4bit",
    "hf:Qwen--Qwen2.5-7B-Instruct:4bit"
  ],
  "language": "zh",
  "prompts": ["中文提示..."],
  "note": "不包含 Phi-3（不支持中文）"
}
```

### 数学/代码实验

```json
{
  "models": [
    "hf:microsoft--phi-3-mini-4k-instruct:4bit",
    "hf:Qwen--Qwen2.5-7B-Instruct:4bit"
  ],
  "language": "en",
  "task_type": "code",
  "benchmark": "HumanEval"
}
```

## 常见问题

### Q: 为什么 Phi-3 中文表现这么差？

**A**: Phi-3 官方只支持英语和法语，训练数据中没有中文。官方明确警告："Languages other than English will experience worse performance."

### Q: Qwen 2.5 3B 和 7B 如何选择？

**A**: 
- **3B**: 轻量级，速度快，适合简单任务和资源受限环境
- **7B**: 能力更强，支持 128K 上下文，适合复杂任务

### Q: 哪个模型最适合我的 RTX 4060 8GB？

**A**:
- ✅ Phi-3 Mini 4bit (~2.5GB) - 完全 GPU
- ✅ Qwen 2.5 3B 4bit (~2.5GB) - 完全 GPU
- ⚠️ Qwen 2.5 7B 4bit (~5-6GB) - 可能需要 CPU offload

### Q: 如何测试模型的真实能力？

**A**: 
1. 使用模型支持的语言（Phi-3 用英文，Qwen 可用中英文）
2. 选择模型擅长的任务（Phi-3 擅长数学/代码）
3. 注意上下文长度限制（Phi-3 最多 4K）

## 避免的错误

❌ **错误做法**：
- 用中文测试 Phi-3
- 用 Phi-3 处理超过 4K tokens 的文本
- 期望 3B 模型在所有任务上都优于 7B 模型
- 忽略模型的语言支持限制

✅ **正确做法**：
- 根据任务语言选择模型
- 根据文本长度选择合适的上下文窗口
- 在模型擅长的领域进行测试
- 参考官方基准测试结果

## 相关文档

- [详细基准测试数据](./MODEL_BENCHMARKS_SUMMARY.md)
- [模型质量问题诊断](./MODEL_QUALITY_ISSUES.md)
- [实验设计指南](./experiment/experiment_design.md)

---

**快速链接**:
- Phi-3 README: `models/huggingface/microsoft--phi-3-mini-4k-instruct/README.md`
- Qwen 2.5 3B README: `models/huggingface/Qwen--Qwen2.5-3B-Instruct/README.md`
- Qwen 2.5 7B README: `models/huggingface/Qwen--Qwen2.5-7B-Instruct/README.md`
