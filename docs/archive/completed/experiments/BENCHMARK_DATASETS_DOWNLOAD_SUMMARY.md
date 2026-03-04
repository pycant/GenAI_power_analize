# 标准测试集下载总结

## 完成日期
2026-03-02

## 已下载的数据集

### ✅ 成功下载

| 数据集 | 题目数量 | 大小 | 位置 | 状态 |
|--------|---------|------|------|------|
| **HumanEval** | 164 题 | ~500 KB | `data/benchmarks/humaneval/` | ✅ 完整 |
| **GSM8K** | 1,319 题 | ~2.5 MB | `data/benchmarks/gsm8k/` | ✅ 完整 |
| **MMLU (STEM)** | 15 学科, 1,879 题 | ~500 KB | `data/benchmarks/mmlu/` | ✅ 完整 |
| **Translation** | 10 句对 | ~5 KB | `data/benchmarks/flores200/` | ✅ 手动创建 |
| **示例数据集** | 各 1-2 题 | ~10 KB | `data/benchmarks/samples/` | ✅ 完整 |

### 📝 说明文件已创建

| 数据集 | 说明文件 | 下载方法 |
|--------|---------|---------|
| **FLORES-200** | `data/benchmarks/flores200/README.md` | Hugging Face datasets |
| **MMLU** | `data/benchmarks/mmlu/README.md` | Hugging Face datasets |

## 数据集详情

### 1. HumanEval (代码生成)

**位置**: `data/benchmarks/humaneval/HumanEval.jsonl`

**统计信息**:
- 题目数量: 164 道编程题
- 语言: Python
- 格式: JSONL (每行一个 JSON 对象)

**数据结构**:
```json
{
  "task_id": "HumanEval/0",
  "prompt": "函数签名和文档字符串",
  "entry_point": "函数名",
  "canonical_solution": "参考解答",
  "test": "单元测试代码"
}
```

**使用示例**:
```python
import json

# 读取数据
problems = []
with open('data/benchmarks/humaneval/HumanEval.jsonl', 'r') as f:
    for line in f:
        problems.append(json.loads(line))

# 查看第一题
print(problems[0]['prompt'])
```

**评估方法**:
- pass@k: 生成 k 个解答，至少有一个通过所有测试用例的比例
- 常用: pass@1, pass@10, pass@100

### 2. GSM8K (数学推理)

**位置**: `data/benchmarks/gsm8k/test.jsonl`

**统计信息**:
- 题目数量: 1,319 道数学应用题
- 难度: 小学数学水平
- 格式: JSONL

**数据结构**:
```json
{
  "question": "问题文本",
  "answer": "解答步骤和最终答案"
}
```

**答案格式**:
- 包含详细的计算步骤
- 最后一行以 `#### 答案` 结尾

**使用示例**:
```python
import json
import re

# 读取数据
problems = []
with open('data/benchmarks/gsm8k/test.jsonl', 'r') as f:
    for line in f:
        problems.append(json.loads(line))

# 提取最终答案
def extract_answer(answer_text):
    # 答案在 #### 之后
    match = re.search(r'####\s*(\d+)', answer_text)
    if match:
        return int(match.group(1))
    return None

# 示例
problem = problems[0]
print(f"问题: {problem['question']}")
print(f"答案: {extract_answer(problem['answer'])}")
```

**评估方法**:
- 提取模型生成的最终答案
- 与标准答案比较（数值匹配）
- 计算准确率

### 3. FLORES-200 (多语言翻译)

**位置**: `data/benchmarks/flores200/`

**说明文件**: `data/benchmarks/flores200/README.md`

**下载方法**:
```bash
# 方法 1: 使用我们的脚本
python scripts/download_hf_datasets.py --flores200

# 方法 2: 直接使用 Python
python -c "
from datasets import load_dataset
dataset = load_dataset('facebook/flores', 'eng_Latn-zho_Hans')
dataset['devtest'].to_json('flores200_en_zh.json')
"
```

**推荐语言对**:
- `eng_Latn-zho_Hans`: 英语 ↔ 简体中文
- `eng_Latn-zho_Hant`: 英语 ↔ 繁体中文
- `eng_Latn-jpn_Jpan`: 英语 ↔ 日语
- `eng_Latn-kor_Hang`: 英语 ↔ 韩语

**数据规模**:
- 每个语言对: 1,012 个句子对
- 总语言数: 200+

**评估指标**:
- BLEU
- chrF++
- COMET
- BERTScore

### 4. MMLU (多学科知识)

**位置**: `data/benchmarks/mmlu/`

**说明文件**: `data/benchmarks/mmlu/README.md`

**下载方法**:
```bash
# 方法 1: 使用我们的脚本（下载 STEM 学科）
python scripts/download_hf_datasets.py --mmlu

# 方法 2: 下载特定学科
python scripts/download_hf_datasets.py --mmlu --mmlu-subjects abstract_algebra anatomy

# 方法 3: 直接使用 Python
python -c "
from datasets import load_dataset
dataset = load_dataset('cais/mmlu', 'abstract_algebra')
dataset['test'].to_json('mmlu_abstract_algebra.json')
"
```

**学科分类**:
- **STEM** (19 个): 数学、物理、化学、生物、计算机等
- **人文** (13 个): 历史、哲学、法律、宗教等
- **社会科学** (12 个): 经济、心理、社会学等
- **其他** (13 个): 医学、商业、营养等

**数据规模**:
- 总题目数: ~16,000 道
- 每个学科: 100-300 题
- 格式: 4 选 1 多选题

**评估方法**:
- 5-shot 评估（提供 5 个示例）
- 计算准确率
- 按学科和类别分析

## 示例数据集

**位置**: `data/benchmarks/samples/`

为快速测试创建的小规模示例数据集：

| 文件 | 题目数 | 用途 |
|------|--------|------|
| `humaneval_sample.json` | 1 题 | 代码生成测试 |
| `gsm8k_sample.json` | 2 题 | 数学推理测试 |
| `mmlu_sample.json` | 2 题 | 知识问答测试 |
| `flores200_sample.json` | 2 句 | 翻译测试 |

**使用示例**:
```bash
# 使用示例数据快速测试
python experiments/experiment_runner.py \
  --test-cases data/benchmarks/samples/humaneval_sample.json \
  --output-dir data/test_run
```

## 下载脚本

### 1. 基础下载脚本

**文件**: `scripts/download_benchmark_datasets.py`

**功能**:
- 下载 HumanEval 和 GSM8K（直接从 GitHub）
- 创建 FLORES-200 和 MMLU 的说明文件
- 生成示例数据集

**使用方法**:
```bash
# 下载 HumanEval 和 GSM8K
python scripts/download_benchmark_datasets.py --humaneval --gsm8k

# 仅创建示例数据集
python scripts/download_benchmark_datasets.py --samples-only

# 下载所有（创建说明文件）
python scripts/download_benchmark_datasets.py --all
```

### 2. Hugging Face 下载脚本

**文件**: `scripts/download_hf_datasets.py`

**功能**:
- 使用 Hugging Face datasets 库下载完整数据集
- 支持 FLORES-200 和 MMLU
- 可选择特定语言对或学科

**前置要求**:
```bash
pip install datasets
```

**使用方法**:
```bash
# 下载 FLORES-200 英中语言对
python scripts/download_hf_datasets.py --flores200

# 下载 MMLU STEM 学科
python scripts/download_hf_datasets.py --mmlu

# 下载特定学科
python scripts/download_hf_datasets.py --mmlu \
  --mmlu-subjects abstract_algebra college_mathematics

# 下载特定语言对
python scripts/download_hf_datasets.py --flores200 \
  --language-pairs eng_Latn-zho_Hans eng_Latn-jpn_Jpan
```

## 数据集使用建议

### 快速测试（30 分钟）
使用示例数据集验证流程：
```bash
# 1. 代码生成测试
python test_humaneval_sample.py

# 2. 数学推理测试
python test_gsm8k_sample.py

# 3. 翻译测试
python test_flores_sample.py
```

### 标准评估（3-5 小时）
使用完整数据集的子集：
- HumanEval: 全部 164 题
- GSM8K: 随机采样 100 题
- FLORES-200: 英中语言对 100 句
- MMLU: 选择 5-10 个学科

### 完整评估（1-2 天）
使用所有数据集：
- HumanEval: 全部 164 题
- GSM8K: 全部 1,319 题
- FLORES-200: 多个语言对
- MMLU: 全部 57 个学科

## 存储空间需求

| 数据集 | 最小配置 | 标准配置 | 完整配置 |
|--------|---------|---------|---------|
| HumanEval | 500 KB | 500 KB | 500 KB |
| GSM8K | 2.5 MB | 2.5 MB | 2.5 MB |
| FLORES-200 | 10 MB | 50 MB | 500 MB |
| MMLU | 50 MB | 200 MB | 500 MB |
| **总计** | **~63 MB** | **~253 MB** | **~1.5 GB** |

## 评估工具安装

### 代码评估
```bash
# HumanEval 官方评估工具
pip install human-eval
```

### 翻译评估
```bash
# BLEU, chrF++
pip install sacrebleu

# COMET
pip install unbabel-comet

# BERTScore
pip install bert-score
```

### 通用评估
```bash
# ROUGE (摘要评估)
pip install rouge-score

# 数学评估（自定义）
# 使用正则表达式提取答案
```

## 下一步

### 短期（1-2 天）
1. ✅ 使用示例数据集测试流程
2. ✅ 下载 HumanEval 和 GSM8K 完整数据
3. ⏳ 使用 Hugging Face 下载 FLORES-200
4. ⏳ 创建数据集加载和评估脚本

### 中期（1 周）
1. 实现各数据集的自动评估
2. 集成到实验运行器
3. 运行基准测试
4. 对比模型表现

### 长期（2-4 周）
1. 下载 MMLU 完整数据集
2. 实现 5-shot 评估
3. 完整的多模型对比实验
4. 撰写评估报告

## 相关文档

- [测试用例设计指南](experiment/TEST_CASE_DESIGN_GUIDE.md)
- [测试用例创建总结](experiment/TEST_CASE_CREATION_SUMMARY.md)
- [实验设计文档](experiment/experiment_design.md)
- [下一步行动指南](../NEXT_STEPS.md)

## 参考资源

### 官方仓库
- [HumanEval](https://github.com/openai/human-eval)
- [GSM8K](https://github.com/openai/grade-school-math)
- [FLORES-200](https://github.com/facebookresearch/flores)
- [MMLU](https://github.com/hendrycks/test)

### Hugging Face
- [FLORES-200 on HF](https://huggingface.co/datasets/facebook/flores)
- [MMLU on HF](https://huggingface.co/datasets/cais/mmlu)
- [Datasets 文档](https://huggingface.co/docs/datasets)

### 评估工具
- [SacreBLEU](https://github.com/mjpost/sacrebleu)
- [COMET](https://github.com/Unbabel/COMET)
- [BERTScore](https://github.com/Tiiiger/bert_score)

## 总结

✅ **已完成**:
1. 下载了 HumanEval (164 题) 和 GSM8K (1,319 题)
2. 创建了所有数据集的示例文件
3. 提供了 FLORES-200 和 MMLU 的下载说明
4. 创建了两个下载脚本（基础版和 HF 版）

📊 **数据集覆盖**:
- ✅ 代码生成: HumanEval
- ✅ 数学推理: GSM8K
- 📝 多语言翻译: FLORES-200 (说明已创建)
- 📝 多学科知识: MMLU (说明已创建)

🎯 **准备就绪**: 你现在可以使用这些标准测试集进行大语言模型评估了！

---

**文档版本**: 1.0  
**创建日期**: 2026-03-02  
**维护者**: 项目团队
