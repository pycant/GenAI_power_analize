# Experiment 5 配置完成报告

## 概述

已成功创建 experiments_5 实验配置，测试用例格式完全符合 `docs/EXPERIMENT_RUNNER_GUIDE.md` 规范。

## 完成时间

2026-03-02

## 配置详情

### 测试用例统计

- **原始任务数**: 80 个（来自 `data/test_cases/test_cases_comprehensive.json`）
- **模型数量**: 4 个
- **总测试用例数**: 320 个（4 模型 × 80 任务）

### 模型列表

1. `qwen3:4b` - Qwen 3 4B 参数模型
2. `qwen3:8b` - Qwen 3 8B 参数模型
3. `deepseek-r1:8b` - DeepSeek R1 8B 模型
4. `gemma3:4b` - Gemma 3 4B 模型

### 任务类型分布

| 任务类型 | 数量 | 来源 |
|---------|------|------|
| QA (问答) | 18 | MMLU |
| Math (数学) | 12 | GSM8K |
| Code (代码) | 12 | HumanEval |
| Translation (翻译) | 10 | FLORES-200 |
| Reasoning (推理) | 10 | Manual |
| Summary (摘要) | 6 | Manual |
| Creative (创作) | 6 | Manual |
| Multi-turn (多轮对话) | 6 | Manual |
| **总计** | **80** | - |

## 格式规范

### 测试用例格式

所有测试用例严格遵循 `EXPERIMENT_RUNNER_GUIDE.md` 中定义的格式：

#### 必需字段

- `model`: 模型规格字符串（如 "qwen3:4b"）
- `prompts`: 提示词（字符串或数组）
- `task_type`: 任务类型标识

#### 可选字段

- `max_tokens`: 最大生成token数（默认 500）
- `temperature`: 温度参数（默认 0.7）
- `top_p`: Top-p采样参数（默认 0.9）
- `idle_measurement_duration`: 空闲基线测量时长（秒，默认 10）
- `reference_text`: 参考文本（用于质量评估）
- `keep_context`: 是否保持上下文（多轮对话）
- `per_turn_monitoring`: 是否分轮监控（多轮对话）

### 格式示例

#### 1. 单轮问答（QA）

```json
{
  "model": "qwen3:4b",
  "task_type": "qa",
  "max_tokens": 100,
  "temperature": 0.0,
  "top_p": 0.9,
  "idle_measurement_duration": 10,
  "prompts": "High entropy means that the partitions in classification are\n\nOptions:\nA. pure\nB. not pure\nC. useful\nD. useless\n\nPlease select the correct answer.",
  "reference_text": "not pure"
}
```

#### 2. 翻译任务（Translation）

```json
{
  "model": "qwen3:4b",
  "task_type": "translation",
  "max_tokens": 200,
  "temperature": 0.2,
  "top_p": 0.9,
  "idle_measurement_duration": 10,
  "prompts": "Please translate the following English text to Chinese:\n\nThe quick brown fox jumps over the lazy dog.",
  "reference_text": "敏捷的棕色狐狸跳过懒狗。"
}
```

#### 3. 多轮对话（Multi-turn）

```json
{
  "model": "qwen3:4b",
  "task_type": "multi_turn",
  "max_tokens": 200,
  "temperature": 0.7,
  "top_p": 0.9,
  "idle_measurement_duration": 10,
  "prompts": [
    "我想去北京旅游，有什么推荐的景点吗？",
    "你刚才提到的第一个景点，门票多少钱？",
    "那个景点附近有什么好吃的？"
  ],
  "keep_context": true,
  "per_turn_monitoring": false
}
```

#### 4. 代码生成（Code）

```json
{
  "model": "qwen3:4b",
  "task_type": "code",
  "max_tokens": 500,
  "temperature": 0.1,
  "top_p": 0.9,
  "idle_measurement_duration": 10,
  "prompts": "from typing import List\n\n\ndef separate_paren_groups(paren_string: str) -> List[str]:\n    \"\"\" Input to this function is a string containing multiple groups of nested parentheses...",
  "reference_text": "    result = []\n    current_string = []\n    current_depth = 0\n\n    for c in paren_string:..."
}
```

## 目录结构

```
data/experiments_5/
├── config.py                    # Python 配置文件
├── config.json                  # JSON 配置元数据
├── test_cases.json              # 320 个测试用例（符合规范）
├── README.md                    # 实验说明文档
├── raw/                         # 原始实验结果（按模型分类）
│   ├── qwen3_4b/
│   ├── qwen3_8b/
│   ├── deepseek-r1_8b/
│   └── gemma3_4b/
├── texts/                       # 文本输出（按模型分类）
│   ├── qwen3_4b/
│   ├── qwen3_8b/
│   ├── deepseek-r1_8b/
│   └── gemma3_4b/
└── summary/                     # 汇总结果
    ├── results.csv              # 详细结果（待生成）
    └── stats.csv                # 统计摘要（待生成）
```

## 关键改进

### 1. 格式修正

之前的版本使用了错误的格式（`model="all"`），现已修正为：
- 为每个模型生成独立的测试用例
- 每个测试用例包含正确的模型规格字符串
- 符合 `EXPERIMENT_RUNNER_GUIDE.md` 的所有要求

### 2. 任务类型处理

针对不同任务类型实现了专门的转换逻辑：

- **QA**: 问题 + 选项格式化
- **Math**: 数学问题 + 预期答案
- **Code**: 代码问题 + 标准解决方案
- **Translation**: 翻译指令 + 源文本 + 目标文本
- **Reasoning**: 推理问题 + 预期答案
- **Summary**: 摘要指令 + 源文本
- **Creative**: 创意提示
- **Multi-turn**: 多轮对话数组 + 上下文保持

### 3. 参数优化

- 所有任务启用空闲基线测量（10秒）
- 多轮对话自动启用 `keep_context`
- 多轮对话默认关闭 `per_turn_monitoring` 以节省开销
- 根据任务类型设置合适的 `temperature` 和 `max_tokens`

## 运行实验

### 方法 1: 使用实验运行器

```bash
python experiments/experiment_runner.py \
  --config data/experiments_5/test_cases.json \
  --output-dir data/experiments_5
```

### 方法 2: 使用快速测试脚本（如果存在）

```bash
python scripts/run_experiment_5.py
```

## 预估运行时间

- **单个测试用例**: 约 1-3 分钟（包括空闲基线测量）
- **总测试用例数**: 320 个
- **预估总时间**: 约 5-16 小时（取决于模型大小和任务复杂度）

### 优化建议

1. **分批运行**: 可以按模型或任务类型分批运行
2. **并行执行**: 如果有多个 GPU，可以并行运行不同模型
3. **优先级排序**: 先运行小模型或简单任务进行验证

## 后续步骤

### 1. 验证配置

```bash
# 检查测试用例格式
python scripts/verify_experiment_5.py

# 查看配置文件
cat data/experiments_5/config.py
cat data/experiments_5/README.md
```

### 2. 运行实验

```bash
# 运行完整实验
python experiments/experiment_runner.py \
  --config data/experiments_5/test_cases.json \
  --output-dir data/experiments_5
```

### 3. 分析结果

```bash
# 运行分析脚本（需要先创建）
python scripts/analyze_experiments_5.py
```

## 文件清单

### 生成的文件

- ✅ `data/experiments_5/config.py` - Python 配置文件
- ✅ `data/experiments_5/config.json` - JSON 配置元数据
- ✅ `data/experiments_5/test_cases.json` - 320 个测试用例
- ✅ `data/experiments_5/README.md` - 实验说明文档
- ✅ 目录结构（raw/, texts/, summary/）

### 脚本文件

- ✅ `scripts/setup_experiment_5.py` - 配置生成脚本（已更新）
- ⏳ `scripts/run_experiment_5.py` - 实验运行脚本（待创建）
- ⏳ `scripts/analyze_experiments_5.py` - 结果分析脚本（待创建）
- ✅ `scripts/verify_experiment_5.py` - 配置验证脚本（已存在）

## 注意事项

### 1. 资源需求

- **显存**: 建议至少 8GB（对于 8B 模型）
- **内存**: 建议至少 16GB
- **磁盘空间**: 预留至少 10GB 用于结果存储

### 2. 运行环境

- **Ollama**: 确保 Ollama 服务正在运行
- **模型**: 确保所有 4 个模型已下载
- **Python 环境**: 激活 bartscore conda 环境

### 3. 质量保证

- 所有测试用例格式已验证
- 符合 `EXPERIMENT_RUNNER_GUIDE.md` 规范
- 包含适当的 `reference_text` 用于质量评估
- 多轮对话正确配置上下文保持

## 相关文档

- [EXPERIMENT_RUNNER_GUIDE.md](../docs/EXPERIMENT_RUNNER_GUIDE.md) - 实验运行器使用指南
- [TEST_CASES_READY.md](../docs/TEST_CASES_READY.md) - 测试用例准备完成报告
- [EXPERIMENT_5_SETUP.md](../docs/EXPERIMENT_5_SETUP.md) - 实验 5 设置文档

## 总结

experiments_5 配置已完全准备就绪，所有测试用例格式正确，符合实验运行器的要求。现在可以开始运行实验，评估 4 个模型在 80 个综合任务上的质效比表现。

---

**配置完成时间**: 2026-03-02  
**配置脚本**: `scripts/setup_experiment_5.py`  
**测试用例文件**: `data/experiments_5/test_cases.json`  
**总测试用例数**: 320 个
