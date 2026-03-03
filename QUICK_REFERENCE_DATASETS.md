# 数据集快速参考

## 📊 已下载数据集概览

| 数据集　　　| 文件路径　　　　　　　　　　　　　　　　　　　　　　　| 题目数 | 用途　　 |
| -------------| -------------------------------------------------------| --------| ----------|
| HumanEval　 | `data/benchmarks/humaneval/HumanEval.jsonl`　　　　　 | 164　　| 代码生成 |
| GSM8K　　　 | `data/benchmarks/gsm8k/test.jsonl`　　　　　　　　　　| 1,319 | 数学推理 |
| MMLU　　　　| `data/benchmarks/mmlu/mmlu_*.json`　　　　　　　　　　| 1,879 | 知识问答 |
| Translation | `data/benchmarks/flores200/translation_test_set.json` | 10　　 | 翻译质量 |

**总计**: 3,372 题，约 2 MB

---

## 🚀 快速使用

### 1. 加载数据集

```python
import json

# HumanEval
with open('data/benchmarks/humaneval/HumanEval.jsonl', 'r') as f:
    humaneval = [json.loads(line) for line in f]

# GSM8K
with open('data/benchmarks/gsm8k/test.jsonl', 'r') as f:
    gsm8k = [json.loads(line) for line in f]

# MMLU (单个学科)
with open('data/benchmarks/mmlu/mmlu_machine_learning_test.json', 'r') as f:
    mmlu_ml = json.load(f)

# Translation
with open('data/benchmarks/flores200/translation_test_set.json', 'r', encoding='utf-8') as f:
    translation = json.load(f)
```

### 2. 运行实验

```bash
# 使用 Ollama 模型
python experiments/experiment_runner.py \
  --model "Ollama:qwen3:4b" \
  --test-cases data/test/test_cases.json \
  --output-dir data/experiments_5

# 使用 HuggingFace 模型
python experiments/experiment_runner.py \
  --model "HF:Qwen/Qwen2.5-3B-Instruct" \
  --test-cases data/test/test_cases.json \
  --output-dir data/experiments_5
```

---

## 📁 MMLU 学科列表

```python
mmlu_subjects = [
    "abstract_algebra",           # 100 题
    "anatomy",                    # 135 题
    "astronomy",                  # 152 题
    "college_biology",            # 144 题
    "college_chemistry",          # 100 题
    "college_computer_science",   # 100 题
    "college_mathematics",        # 100 题
    "college_physics",            # 102 题
    "computer_security",          # 100 题
    "high_school_biology",        # 310 题
    "high_school_chemistry",      # 203 题
    "high_school_computer_science", # 100 题
    "high_school_mathematics",    # 270 题
    "high_school_physics",        # 151 题
    "machine_learning",           # 112 题
]
```

---

## 🔧 下载更多数据

### 下载更多 MMLU 学科

```bash
# 下载特定学科
python scripts/download_hf_datasets.py --mmlu \
  --mmlu-subjects physics chemistry biology

# 下载所有 STEM 学科（默认）
python scripts/download_hf_datasets.py --mmlu
```

### 重新下载基础数据集

```bash
python scripts/download_benchmark_datasets.py --all
```

---

## 📚 相关文档

- **完整文档**: `docs/DATASET_DOWNLOAD_COMPLETE.md`
- **详细总结**: `docs/BENCHMARK_DATASETS_DOWNLOAD_SUMMARY.md`
- **会话记录**: `SESSION_SUMMARY_DATASET_DOWNLOAD.md`
- **下一步**: `NEXT_STEPS.md`

---

## ⚠️ 已知问题

**FLORES-200 编码问题**: 完整 FLORES-200 数据集在 Windows 上无法下载（编码错误）。当前使用手动创建的 10 句对作为替代。

**解决方案**:
- 使用 WSL 或 Linux 环境下载
- 或使用现有的 10 句对进行初步测试

---

**最后更新**: 2026-03-02
　　　　　　　　　　　　　　　| 　　　 | 　　　　 |