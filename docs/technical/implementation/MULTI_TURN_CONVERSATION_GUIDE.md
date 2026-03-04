# 多轮对话功能使用指南

## 概述

实验运行器现已支持多轮对话功能，允许您测试模型在连续对话场景下的表现。这对于评估模型的上下文理解能力和对话连贯性非常有用。

## 新增参数

### 1. prompts（必需）

**类型**: `string` 或 `array`

**说明**: 替代原来的 `prompt` 参数，支持单个提示或多个提示的列表。

**示例**:
```json
// 单轮对话（向后兼容）
"prompts": "请解释牛顿第一定律。"

// 多轮对话
"prompts": [
  "请解释牛顿第一定律。",
  "请举出一个实际应用例子。"
]
```

### 2. keep_context（可选）

**类型**: `boolean`

**默认值**: `false`

**说明**: 是否在多轮对话中保持上下文记忆。

- `true`: 模型会记住之前的对话内容，后续回复会基于完整的对话历史
- `false`: 每轮对话独立，模型不会记住之前的内容

**示例**:
```json
"keep_context": true
```

## 配置文件格式

### 基本格式

```json
[
  {
    "model": "模型名称",
    "prompts": ["提示1", "提示2", ...],
    "task_type": "任务类型",
    "keep_context": true/false,
    "reference_text": "参考答案（可选）",
    "max_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9
  }
]
```

### 完整示例

```json
[
  {
    "model": "qwen3:4b",
    "prompts": [
      "请解释牛顿第一定律。",
      "请举出一个牛顿第一定律的实际应用例子。",
      "为什么安全带能保护乘客？"
    ],
    "task_type": "qa",
    "keep_context": true,
    "reference_text": "牛顿第一定律指出物体保持静止或匀速直线运动状态，除非受到外力作用。",
    "max_tokens": 200,
    "temperature": 0.7,
    "top_p": 0.9
  }
]
```

## 使用场景

### 场景1：连续问答（keep_context=true）

适用于需要基于前文回答的场景：

```json
{
  "model": "qwen3:4b",
  "prompts": [
    "什么是Python？",
    "它有哪些主要特点？",
    "请给我一个简单的代码示例。"
  ],
  "task_type": "qa",
  "keep_context": true
}
```

**效果**: 
- 第2轮："它"指代Python
- 第3轮：代码示例会基于前面讨论的特点

### 场景2：独立问答（keep_context=false）

适用于测试多个独立问题：

```json
{
  "model": "gemma3:4b",
  "prompts": [
    "什么是机器学习？",
    "什么是深度学习？",
    "什么是神经网络？"
  ],
  "task_type": "qa",
  "keep_context": false
}
```

**效果**: 每个问题独立回答，不受前面问题影响。

### 场景3：代码生成与优化

```json
{
  "model": "gemma3:4b",
  "prompts": [
    "写一个Python函数计算斐波那契数列。",
    "请优化这个函数的性能。",
    "添加错误处理。"
  ],
  "task_type": "code",
  "keep_context": true
}
```

### 场景4：创意写作迭代

```json
{
  "model": "qwen3:8b",
  "prompts": [
    "写一首关于春天的诗。",
    "请让这首诗更有画面感。",
    "加入一些比喻手法。"
  ],
  "task_type": "creative",
  "keep_context": true
}
```

## 运行实验

### 命令行

```bash
conda activate bartscore
python experiments/experiment_runner.py --config data/test/test_cases_multi_turn.json --output-dir data/test
```

### 输出示例

```
============================================================
开始实验
  模型: Ollama:qwen3:4b
  任务: qa
  对话轮数: 2
  保持上下文: 是
============================================================

  [轮次 1/2]
  提示: 请解释牛顿第一定律。
  → 调用Ollama模型: qwen3:4b
  ✓ 生成完成 (耗时: 3.45秒, Tokens: 85)

  [轮次 2/2]
  提示: 请举出一个实际应用例子。
  → 调用Ollama模型: qwen3:4b
  ✓ 生成完成 (耗时: 2.31秒, Tokens: 62)

  → 评估生成质量...
  ✓ 实验完成
    - 对话轮数: 2
    - 总生成时间: 5.76秒
    - 平均每轮: 2.88秒
    - 总Token数: 147
    - 吞吐量: 25.52 tokens/s
    - GPU能耗: 245.32 J
```

## 结果数据结构

### JSON输出格式

```json
{
  "model": "qwen3:4b",
  "prompts": ["提示1", "提示2"],
  "task_type": "qa",
  "keep_context": true,
  "conversation": [
    {
      "turn": 1,
      "prompt": "请解释牛顿第一定律。",
      "response": "牛顿第一定律，也称为惯性定律..."
    },
    {
      "turn": 2,
      "prompt": "请举出一个实际应用例子。",
      "response": "一个常见的例子是汽车安全带..."
    }
  ],
  "generated_text": "一个常见的例子是汽车安全带...",
  "all_responses": ["回复1", "回复2"],
  "performance": {
    "total_time_seconds": 5.76,
    "token_count": 147,
    "throughput_tokens_per_sec": 25.52,
    "turns": 2,
    "avg_time_per_turn": 2.88
  },
  "resources": { ... },
  "quality": { ... }
}
```

### 关键字段说明

| 字段 | 说明 |
|------|------|
| `prompts` | 所有提示的列表 |
| `keep_context` | 是否保持上下文 |
| `conversation` | 完整对话记录（每轮的提示和回复） |
| `generated_text` | 最后一轮的回复（向后兼容） |
| `all_responses` | 所有轮次的回复列表 |
| `performance.turns` | 对话轮数 |
| `performance.avg_time_per_turn` | 平均每轮耗时 |

## 技术实现

### Ollama模型

Ollama原生支持context机制：

- 第一轮调用返回 `context` 数组
- 后续轮次将 `context` 传回API
- 模型自动维护对话历史

### Hugging Face模型

HF模型通过手动拼接历史实现：

```
用户: 提示1
助手: 回复1

用户: 提示2
助手: 回复2

用户: 提示3
助手: 
```

## 向后兼容性

### 旧格式仍然支持

```json
{
  "model": "qwen3:4b",
  "prompt": "单个提示",
  "task_type": "qa"
}
```

会自动转换为：

```json
{
  "model": "qwen3:4b",
  "prompts": ["单个提示"],
  "keep_context": false
}
```

### 字段优先级

- 优先使用 `prompts`
- 如果没有 `prompts`，使用 `prompt`
- 如果都没有，报错

## 性能考虑

### 多轮对话的资源消耗

1. **时间**: 总时间 = 各轮时间之和
2. **Token**: 总Token = 各轮Token之和
3. **能耗**: 整个对话过程的累计能耗
4. **显存**: 
   - `keep_context=true`: 显存占用会随轮次增加
   - `keep_context=false`: 每轮独立，显存占用稳定

### 优化建议

1. **合理设置轮数**: 建议不超过5轮
2. **控制max_tokens**: 避免单轮生成过长
3. **监控显存**: 8GB显存建议3轮以内
4. **适当延迟**: 轮次间自动有短暂延迟

## 实验设计建议

### 对比实验

测试 `keep_context` 的影响：

```json
[
  {
    "model": "qwen3:4b",
    "prompts": ["问题1", "问题2"],
    "keep_context": true,
    "task_type": "qa_with_context"
  },
  {
    "model": "qwen3:4b",
    "prompts": ["问题1", "问题2"],
    "keep_context": false,
    "task_type": "qa_without_context"
  }
]
```

### 质效比评估

多轮对话的质效比计算：

- **质量**: 使用最后一轮的回复评估
- **效率**: 考虑总时间和总Token数
- **能耗**: 整个对话的累计能耗

## 常见问题

### Q1: 为什么qwen3和deepseek-r1的回复是思考过程？

**A**: qwen3和deepseek-r1是推理模型（reasoning models），它们的特点是：
- 将思考过程放在`thinking`字段
- 最终答案放在`response`字段
- 如果token限制太小，可能只输出思考过程而没有最终答案

**解决方案**:
1. 增加`max_tokens`参数（建议500-1000）
2. 或者接受thinking作为回复（这就是推理模型的特点）

**示例**:
```json
{
  "model": "qwen3:4b",
  "prompts": ["请解释牛顿第一定律。"],
  "max_tokens": 800,
  "temperature": 0.7
}
```

### Q2: keep_context=true时，HF模型会很慢吗？

**A**: 是的，因为需要手动拼接历史。建议：
- 使用Ollama模型进行多轮对话测试
- 或限制HF模型的对话轮数

### Q3: 如何查看每轮的详细回复？

**A**: 查看结果JSON中的 `conversation` 字段：

```python
import json

with open('results.json', 'r') as f:
    results = json.load(f)

for exp in results:
    print(f"模型: {exp['model']}")
    for turn in exp['conversation']:
        print(f"  轮次{turn['turn']}: {turn['prompt']}")
        print(f"  回复: {turn['response'][:100]}...")
```

### Q4: 可以混合单轮和多轮实验吗？

**A**: 可以！在同一个配置文件中：

```json
[
  {
    "model": "qwen3:4b",
    "prompts": "单轮提示",
    "task_type": "qa"
  },
  {
    "model": "qwen3:4b",
    "prompts": ["多轮1", "多轮2"],
    "keep_context": true,
    "task_type": "qa"
  }
]
```

## 示例配置文件

完整示例请参考：
- `data/test/test_cases_multi_turn.json` - 多轮对话示例
- `data/test/test_cases_ollama_only.json` - 单轮对话示例（向后兼容）

## 相关文档

- [实验运行器文档](../experiments/experiment_runner.py)
- [参数配置指南](./EXPERIMENT_PARAMETERS.md)
- [监控数据可视化](../data/test/监控数据可视化说明.md)
