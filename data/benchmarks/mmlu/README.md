# MMLU 数据集

## 下载方法

### 使用 Hugging Face datasets（推荐）

```python
from datasets import load_dataset

# 下载完整 MMLU 数据集
dataset = load_dataset("cais/mmlu", "all")

# 或下载特定学科
dataset = load_dataset("cais/mmlu", "abstract_algebra")

# 保存为 JSON
dataset['test'].to_json('mmlu_test.json')
```

### 可用学科（57 个）

#### STEM
- abstract_algebra, anatomy, astronomy, college_biology, 
  college_chemistry, college_computer_science, college_mathematics,
  college_physics, computer_security, conceptual_physics,
  electrical_engineering, elementary_mathematics, high_school_biology,
  high_school_chemistry, high_school_computer_science,
  high_school_mathematics, high_school_physics, high_school_statistics,
  machine_learning

#### 人文
- formal_logic, high_school_european_history, high_school_us_history,
  high_school_world_history, international_law, jurisprudence,
  logical_fallacies, moral_disputes, moral_scenarios, philosophy,
  prehistory, professional_law, world_religions

#### 社会科学
- econometrics, high_school_geography, high_school_government_and_politics,
  high_school_macroeconomics, high_school_microeconomics,
  high_school_psychology, human_sexuality, professional_psychology,
  public_relations, security_studies, sociology, us_foreign_policy

#### 其他
- business_ethics, clinical_knowledge, college_medicine, global_facts,
  human_aging, management, marketing, medical_genetics, miscellaneous,
  nutrition, professional_accounting, professional_medicine, virology

## 数据格式

每个题目包含：
- question: 问题文本
- choices: 4 个选项 (A, B, C, D)
- answer: 正确答案索引 (0-3)

## 使用示例

```python
import json

# 加载数据
with open('mmlu_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍历题目
for item in data:
    print(f"Q: {item['question']}")
    for i, choice in enumerate(item['choices']):
        print(f"  {chr(65+i)}. {choice}")
    print(f"A: {chr(65+item['answer'])}")
```

## 评估方法

MMLU 使用 5-shot 评估：
1. 提供 5 个示例题目
2. 让模型回答测试题目
3. 计算准确率
