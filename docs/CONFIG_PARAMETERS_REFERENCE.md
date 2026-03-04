# 配置文件参数快速参考

## 参数总览表

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | string | ✅ | - | 模型规格字符串 |
| `prompts` | string/array | ✅ | - | 提示词或提示词列表 |
| `task_type` | string | ✅ | - | 任务类型标识 |
| `reference_text` | string | ❌ | `null` | 参考文本（用于质量评估） |
| `max_tokens` | int | ❌ | `500` | 最大生成token数 |
| `temperature` | float | ❌ | `0.7` | 温度参数 (0.0-2.0) |
| `top_p` | float | ❌ | `0.9` | Top-p采样 (0.0-1.0) |
| `keep_context` | bool | ❌ | `false` | 多轮对话是否保持上下文 |
| `per_turn_monitoring` | bool | ❌ | `false` | 是否分轮监控资源 |
| `idle_measurement_duration` | int | ❌ | `0` | 空闲基线测量时长（秒） |

## 参数详细说明

### model (模型规格)

**格式**:
- Ollama: `"model_name"` 或 `"ollama:model_name"`
- HuggingFace: `"hf:model_path"` 或 `"hf:model_path:quantize"`

**示例**:
```json
"model": "qwen3:4b"
"model": "ollama:deepseek-r1:8b"
"model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct"
"model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"
```

**量化选项**:
- 不指定: FP16
- `:4bit`: 4位量化（推荐）
- `:8bit`: 8位量化

---

### prompts (提示词)

**格式**:
- 单轮: `"string"` 或 `["string"]`
- 多轮: `["string1", "string2", ...]`

**示例**:
```json
"prompts": "什么是Python？"
"prompts": ["什么是Python？"]
"prompts": ["问题1", "问题2", "问题3"]
```

---

### task_type (任务类型)

**推荐值**:

| 值 | 说明 | 适用场景 |
|----|------|---------|
| `qa` | 问答 | 知识问答、信息查询 |
| `summary` | 摘要 | 文本摘要、内容总结 |
| `creative` | 创作 | 写作、诗歌、故事 |
| `code` | 代码 | 代码生成、调试 |
| `translation` | 翻译 | 语言翻译 |
| `reasoning` | 推理 | 逻辑推理、数学 |

**示例**:
```json
"task_type": "qa"
"task_type": "creative"
```

---

### reference_text (参考文本)

**用途**: 用于质量评估（BARTScore）

**示例**:
```json
"reference_text": "牛顿第一定律，也称为惯性定律..."
```

**注意**: 如果不提供，质量评估将返回 `null`

---

### max_tokens (最大token数)

**范围**: 1 - 模型最大上下文长度

**推荐值**:

| 任务类型 | 推荐值 | 说明 |
|---------|--------|------|
| 简短回答 | 50-100 | 快速问答 |
| 标准回答 | 200-500 | 一般对话 |
| 详细回答 | 500-1000 | 详细解释 |
| 长文本 | 1000+ | 文章、故事 |

**示例**:
```json
"max_tokens": 200
"max_tokens": 500
```

---

### temperature (温度参数)

**范围**: 0.0 - 2.0

**效果**:

| 值 | 效果 | 适用场景 |
|----|------|---------|
| 0.0-0.3 | 确定性强 | 事实问答、代码 |
| 0.4-0.7 | 平衡 | 通用对话、摘要 |
| 0.8-1.0 | 创造性强 | 创意写作 |
| 1.0+ | 高度随机 | 实验探索 |

**示例**:
```json
"temperature": 0.5  // 事实性任务
"temperature": 0.7  // 通用任务
"temperature": 0.9  // 创意任务
```

---

### top_p (Top-p采样)

**范围**: 0.0 - 1.0

**推荐值**:

| 值 | 效果 |
|----|------|
| 0.9 | 推荐值（平衡） |
| 0.95 | 更多样化 |
| 0.8 | 更保守 |
| 1.0 | 考虑所有token |

**示例**:
```json
"top_p": 0.9
```

**与 temperature 的关系**:
- 两者共同控制生成的随机性
- 通常只调整其中一个
- 推荐: 固定 `top_p=0.9`，调整 `temperature`

---

### keep_context (保持上下文)

**类型**: boolean

**效果**:
- `true`: 每轮对话能看到之前的内容
- `false`: 每轮对话独立

**示例**:
```json
{
  "prompts": ["问题1", "问题2", "问题3"],
  "keep_context": true
}
```

**适用场景**:
- `true`: 连续对话、追问、上下文相关
- `false`: 独立问题、批量测试

**注意**:
- Ollama: 使用 `context` 字段
- HuggingFace: 拼接历史对话

---

### per_turn_monitoring (分轮监控)

**类型**: boolean

**效果**:
- `true`: 每轮独立监控资源
- `false`: 整体监控（默认）

**对比**:

| 模式 | 数据粒度 | 开销 | 适用场景 |
|------|---------|------|---------|
| 整体监控 | 总体数据 | 小 | 单轮、快速测试 |
| 分轮监控 | 每轮详细数据 | 大 | 多轮分析 |

**示例**:
```json
{
  "prompts": ["问题1", "问题2", "问题3"],
  "per_turn_monitoring": true
}
```

**输出差异**:
- `false`: `resources` 包含总体数据
- `true`: `conversation[i].resources` 包含每轮数据

---

### idle_measurement_duration (空闲测量)

**类型**: int (秒)

**范围**: 0 - 任意正整数

**推荐值**:

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 不测量 | 0 | 默认值 |
| 快速测试 | 5 | 快速验证 |
| 标准实验 | 10 | 推荐值 |
| 精确测量 | 15-30 | 更稳定 |

**示例**:
```json
"idle_measurement_duration": 10
```

**自动计算的指标**:
- `P_idle`: 空闲功耗 (W)
- `P_inc`: 增量功耗 (W)
- `E_inc`: 增量能耗 (J)
- `E_token`: 每token能耗 (J/token)
- `PPW`: 每瓦性能 (tokens/s/W)
- `TPJ`: 能效比 (tokens/J)

**注意事项**:
- 测量期间保持系统空闲
- 关闭不必要的后台程序
- 等待系统温度稳定

---

## 配置模板

### 模板1: 最小配置

```json
{
  "model": "ollama:qwen3:4b",
  "prompts": "你的问题",
  "task_type": "qa"
}
```

### 模板2: 标准配置

```json
{
  "model": "ollama:qwen3:4b",
  "prompts": "你的问题",
  "task_type": "qa",
  "max_tokens": 200,
  "temperature": 0.7,
  "top_p": 0.9
}
```

### 模板3: 完整配置

```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
  "prompts": ["问题1", "问题2", "问题3"],
  "task_type": "qa",
  "reference_text": "参考答案",
  "max_tokens": 200,
  "temperature": 0.7,
  "top_p": 0.9,
  "keep_context": true,
  "per_turn_monitoring": false,
  "idle_measurement_duration": 10
}
```

## 常见配置组合

### 1. 事实性问答

```json
{
  "model": "ollama:qwen3:4b",
  "prompts": "什么是Python？",
  "task_type": "qa",
  "max_tokens": 200,
  "temperature": 0.5,
  "top_p": 0.9
}
```

### 2. 创意写作

```json
{
  "model": "ollama:qwen3:4b",
  "prompts": "写一首关于春天的诗",
  "task_type": "creative",
  "max_tokens": 300,
  "temperature": 0.9,
  "top_p": 0.95
}
```

### 3. 代码生成

```json
{
  "model": "ollama:deepseek-r1:8b",
  "prompts": "写一个Python快速排序函数",
  "task_type": "code",
  "max_tokens": 500,
  "temperature": 0.3,
  "top_p": 0.9
}
```

### 4. 多轮对话

```json
{
  "model": "ollama:qwen3:4b",
  "prompts": [
    "什么是机器学习？",
    "它有哪些主要应用？",
    "请举一个实际例子。"
  ],
  "task_type": "qa",
  "keep_context": true,
  "max_tokens": 200,
  "temperature": 0.7
}
```

### 5. 能效评估

```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
  "prompts": "解释一下深度学习",
  "task_type": "qa",
  "max_tokens": 200,
  "temperature": 0.7,
  "idle_measurement_duration": 10
}
```

### 6. 多模型对比

```json
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": "相同的问题",
    "task_type": "qa",
    "temperature": 0.7,
    "idle_measurement_duration": 10
  },
  {
    "model": "ollama:gemma3:4b",
    "prompts": "相同的问题",
    "task_type": "qa",
    "temperature": 0.7,
    "idle_measurement_duration": 10
  }
]
```

## 参数验证规则

### 必需参数检查

```python
# model: 必须提供
if "model" not in config:
    raise ValueError("缺少必需参数: model")

# prompts: 必须提供
if "prompts" not in config and "prompt" not in config:
    raise ValueError("缺少必需参数: prompts 或 prompt")

# task_type: 必须提供
if "task_type" not in config:
    raise ValueError("缺少必需参数: task_type")
```

### 参数范围检查

```python
# temperature: 0.0 - 2.0
if not 0.0 <= temperature <= 2.0:
    raise ValueError("temperature 必须在 0.0 到 2.0 之间")

# top_p: 0.0 - 1.0
if not 0.0 <= top_p <= 1.0:
    raise ValueError("top_p 必须在 0.0 到 1.0 之间")

# max_tokens: > 0
if max_tokens <= 0:
    raise ValueError("max_tokens 必须大于 0")

# idle_measurement_duration: >= 0
if idle_measurement_duration < 0:
    raise ValueError("idle_measurement_duration 必须大于等于 0")
```

## 相关文档

- [Experiment Runner 使用指南](./EXPERIMENT_RUNNER_GUIDE.md)
- [空闲基线测量功能说明](./IDLE_BASELINE_MEASUREMENT.md)
- [多轮对话指南](./MULTI_TURN_CONVERSATION_GUIDE.md)

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**维护者**: Kiro AI Assistant
