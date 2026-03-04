# Experiment 5 配置完成

## 概述

已成功创建 experiments_5 实验配置，包含 80 个从标准测试集抽取的综合测试用例。

## 配置详情

### 实验目录结构

```
data/experiments_5/
├── config.py              # Python 配置文件
├── config.json            # JSON 配置文件  
├── test_cases.json        # 80 个测试用例（已转换格式）
├── README.md              # 实验说明文档
├── raw/                   # 原始实验结果（按模型分类）
│   ├── qwen3_4b/
│   ├── qwen3_8b/
│   ├── deepseek-r1_8b/
│   └── gemma3_4b/
├── texts/                 # 文本输出（按模型分类）
│   ├── qwen3_4b/
│   ├── qwen3_8b/
│   ├── deepseek-r1_8b/
│   └── gemma3_4b/
└── summary/               # 汇总结果（实验运行后生成）
    ├── results.csv
    └── stats.csv
```

### 测试用例分布

| 任务类型 | 数量 | 说明 |
|---------|------|------|
| QA (知识问答) | 18 | 来自 MMLU |
| Math (数学计算) | 12 | 来自 GSM8K |
| Code (代码生成) | 12 | 来自 HumanEval |
| Translation (翻译) | 10 | 来自 FLORES-200 |
| Reasoning (逻辑推理) | 10 | 手动设计 |
| Summary (文本摘要) | 6 | 手动设计 |
| Creative (创意写作) | 6 | 手动设计 |
| Multi-turn (多轮对话) | 6 | 手动设计 |
| **总计** | **80** | |

### 评估模型

1. qwen3:4b (约 2.5GB)
2. qwen3:8b (约 5.2GB)
3. deepseek-r1:8b (约 5.2GB)
4. gemma3:4b (约 3.3GB)

### 实验参数

```python
TEMPERATURE = 0.7      # 默认温度（会被测试用例覆盖）
TOP_P = 0.9
NUM_CTX = 8192         # 上下文窗口
SEED = 42
KEEPALIVE = "5m"
WARMUP = True
RUNS = 1               # 每个测试用例的重复次数从测试用例读取
```

## 使用方法

### 1. 验证配置

```bash
python scripts/verify_experiment_5.py
```

### 2. 运行实验

使用现有的实验运行器：

```bash
python experiments/experiment_runner.py --config data/experiments_5/config.py
```

或者创建专用的运行脚本（推荐）：

```bash
python scripts/run_experiment_5.py
```

### 3. 分析结果

实验完成后，运行分析脚本：

```bash
python scripts/analyze_experiments_5.py
```

## 测试用例格式

测试用例已从 `test_cases_comprehensive.json` 转换为实验运行器兼容格式：

### QA 任务示例

```json
{
  "id": "qa_machine_learning_001",
  "model": "all",
  "task_type": "qa",
  "difficulty": "easy",
  "language": "en",
  "prompt": "Statement 1| In a Bayesian network...\n\n选项：\nA. True, True\nB. False, False\n...",
  "reference_text": "True, False",
  "expected_answer": 2,
  "choices": ["True, True", "False, False", "True, False", "False, True"],
  "temperature": 0.0,
  "max_tokens": 100,
  "repeat": 1,
  "source": "MMLU-machine_learning"
}
```

### Math 任务示例

```json
{
  "id": "math_001",
  "model": "all",
  "task_type": "math",
  "difficulty": "easy",
  "language": "en",
  "prompt": "Sarah went to buy books from the store...",
  "reference_text": "5",
  "expected_steps": "Since she spent $300...",
  "temperature": 0.0,
  "max_tokens": 300,
  "repeat": 1,
  "source": "GSM8K"
}
```

### Translation 任务示例

```json
{
  "id": "translation_001",
  "model": "all",
  "task_type": "translation",
  "difficulty": "easy",
  "language": "mixed",
  "prompt": "请将以下eng文本翻译成zho_Hans：\n\nThe quick brown fox...",
  "source_text": "The quick brown fox jumps over the lazy dog.",
  "reference_text": "敏捷的棕色狐狸跳过懒狗。",
  "source_lang": "eng",
  "target_lang": "zho_Hans",
  "domain": "general",
  "temperature": 0.2,
  "max_tokens": 200,
  "repeat": 3,
  "source": "FLORES-200-curated"
}
```

## 自定义配置

### 修改模型列表

编辑 `data/experiments_5/config.py`:

```python
MODELS = [
    "qwen3:4b",
    "qwen3:8b",
    "deepseek-r1:8b",
    "gemma3:4b",
    # 添加更多模型...
]
```

或重新运行设置脚本：

```bash
python scripts/setup_experiment_5.py --models qwen3:4b qwen3:8b llama3:8b
```

### 修改实验参数

编辑 `data/experiments_5/config.py` 中的参数。

## 预期输出

实验运行后，将生成：

1. **原始结果** (`raw/{model}/`): 每个测试用例的完整 JSON 输出
2. **文本输出** (`texts/{model}/`): 纯文本格式的模型响应
3. **汇总结果** (`summary/`):
   - `results.csv`: 详细的性能指标（吞吐量、延迟、能耗、质量分数）
   - `stats.csv`: 统计摘要

## 后续步骤

1. ✅ 配置已创建
2. ⏳ 运行实验（预计耗时：根据模型和硬件而定）
3. ⏳ 分析结果
4. ⏳ 生成报告和可视化

## 相关文件

- 源测试用例: `data/test_cases/test_cases_comprehensive.json`
- 设置脚本: `scripts/setup_experiment_5.py`
- 验证脚本: `scripts/verify_experiment_5.py`
- 实验配置: `data/experiments_5/config.py`
- 测试用例: `data/experiments_5/test_cases.json`

## 注意事项

1. 确保 Ollama 服务正在运行
2. 确保所有模型已下载：`ollama list`
3. 实验可能需要较长时间（80 个测试用例 × 4 个模型）
4. 建议在实验期间保持系统稳定，避免其他高负载任务

---

创建时间: 2026-03-02  
脚本版本: 1.0
