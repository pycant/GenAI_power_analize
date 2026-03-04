# 困惑度（Perplexity）计算指南

## 概述

困惑度是衡量语言模型对文本预测能力的指标，用于评估生成文本的流畅性。困惑度越低，表示文本越流畅、越符合自然语言规律。

**公式**: `Perplexity = exp(CrossEntropyLoss)`

## 快速开始

### 1. 安装依赖

```bash
conda activate bartscore
pip install transformers torch
```

### 2. 运行计算

```bash
# 使用中文GPT-2模型（推荐）
python data/analize/scripts/calculate_perplexity.py

# 使用英文GPT-2模型（更快，但对中文效果较差）
python data/analize/scripts/calculate_perplexity.py --model gpt2

# 使用CPU（如果没有GPU）
python data/analize/scripts/calculate_perplexity.py --device cpu
```

### 3. 查看结果

输出文件：`data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv`

新增字段：`perplexity`（困惑度值）

## 支持的模型

### 中文模型（推荐）

| 模型名称 | 大小 | 下载时间 | 推荐场景 |
|---------|------|---------|---------|
| `uer/gpt2-chinese-cluecorpussmall` | ~500MB | 5-10分钟 | 中文文本（推荐） |
| `bert-base-chinese` | ~400MB | 5-10分钟 | 中文文本（备选） |

### 英文模型

| 模型名称 | 大小 | 下载时间 | 推荐场景 |
|---------|------|---------|---------|
| `gpt2` | ~500MB | 5-10分钟 | 英文文本或快速测试 |
| `gpt2-medium` | ~1.5GB | 15-20分钟 | 英文文本（更准确） |

## 计算原理

### 因果语言模型（GPT系列）

1. 将文本输入模型
2. 模型预测每个位置的下一个词
3. 计算预测与实际的交叉熵损失
4. 困惑度 = exp(平均损失)

**优点**: 计算快速，适合长文本

### 掩码语言模型（BERT系列）

1. 逐个掩盖文本中的词
2. 模型预测被掩盖的词
3. 计算所有位置的平均损失
4. 困惑度 = exp(平均损失)

**优点**: 双向上下文，更准确

## 困惑度解读

### 数值范围

- **< 50**: 非常流畅，接近人类写作
- **50-100**: 流畅，语法正确
- **100-200**: 基本流畅，可能有小问题
- **200-500**: 不太流畅，语法或逻辑问题
- **> 500**: 很不流畅，可能是乱码或无意义文本

### 影响因素

1. **文本长度**: 长文本通常困惑度更高
2. **语言复杂度**: 专业术语、诗歌等困惑度较高
3. **模型匹配度**: 使用中文模型评估中文文本更准确
4. **生成质量**: 困惑度低不一定内容好，但高一定有问题

## 使用示例

### 示例1：基础使用

```python
from calculate_perplexity import PerplexityCalculator

# 初始化
calculator = PerplexityCalculator(
    model_name='uer/gpt2-chinese-cluecorpussmall',
    device='cuda'
)

# 计算单个文本
text = "春天来了，万物复苏。"
ppl = calculator.calculate_perplexity(text)
print(f"困惑度: {ppl:.2f}")

# 批量计算
texts = ["文本1", "文本2", "文本3"]
ppls = calculator.calculate_batch_perplexity(texts)
```

### 示例2：集成到评估流程

```python
import pandas as pd
from calculate_perplexity import PerplexityCalculator

# 加载数据
df = pd.read_csv('creative_quality_scores_detailed.csv')

# 初始化计算器
calculator = PerplexityCalculator(model_name='uer/gpt2-chinese-cluecorpussmall')

# 计算困惑度
df['perplexity'] = df['response_text'].apply(
    lambda x: calculator.calculate_perplexity(x)
)

# 保存结果
df.to_csv('scores_with_perplexity.csv', index=False)
```

### 示例3：对比不同模型

```python
models = [
    'uer/gpt2-chinese-cluecorpussmall',
    'bert-base-chinese',
    'gpt2'
]

for model_name in models:
    calculator = PerplexityCalculator(model_name=model_name)
    ppl = calculator.calculate_perplexity("测试文本")
    print(f"{model_name}: {ppl:.2f}")
```

## 性能优化

### GPU加速

```python
# 使用GPU（推荐）
calculator = PerplexityCalculator(device='cuda')

# 检查GPU可用性
import torch
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
else:
    print("使用CPU（较慢）")
```

### 批处理

```python
# 批量计算（更快）
ppls = calculator.calculate_batch_perplexity(
    texts=text_list,
    batch_size=16  # 根据显存调整
)
```

### 长度限制

```python
# 限制最大长度（避免显存溢出）
ppl = calculator.calculate_perplexity(
    text=long_text,
    max_length=512  # 默认512，可调整
)
```

## 常见问题

### Q1: 首次运行很慢？

**A**: 首次运行会下载模型（约500MB-1.5GB），需要5-20分钟。模型会缓存到本地，后续运行会很快。

**缓存位置**: `~/.cache/huggingface/`

### Q2: 显存不足？

**A**: 尝试以下方法：
1. 减小 `max_length`（如改为256）
2. 减小 `batch_size`（如改为4）
3. 使用更小的模型（如 `gpt2` 而非 `gpt2-medium`）
4. 使用CPU（`device='cpu'`）

### Q3: 中文困惑度异常高？

**A**: 确保使用中文模型：
- ✅ `uer/gpt2-chinese-cluecorpussmall`
- ✅ `bert-base-chinese`
- ❌ `gpt2`（英文模型，对中文效果差）

### Q4: 如何离线使用？

**A**: 
1. 首次在线运行，下载模型
2. 模型缓存到 `~/.cache/huggingface/`
3. 后续可离线使用

或手动下载模型：
```bash
# 使用 huggingface-cli
huggingface-cli download uer/gpt2-chinese-cluecorpussmall
```

### Q5: 困惑度和质量的关系？

**A**: 
- 困惑度低 → 流畅性好（语法正确）
- 困惑度低 ≠ 内容质量高（可能是平庸的文本）
- 困惑度高 → 一定有问题（语法错误、乱码等）

**建议**: 将困惑度与其他指标（Distinct-N、修辞手法等）结合使用

## 与其他指标的关系

| 指标 | 衡量维度 | 关系 |
|------|---------|------|
| Distinct-N | 多样性 | 负相关（多样性高可能困惑度高） |
| 修辞手法 | 创造力 | 弱正相关（复杂修辞可能提高困惑度） |
| 文本长度 | 长度 | 正相关（长文本困惑度通常更高） |
| BERTScore | 语义质量 | 弱负相关 |

## 最佳实践

1. **选择合适的模型**: 中文文本用中文模型，英文文本用英文模型
2. **归一化处理**: 不同长度的文本困惑度不可直接比较
3. **结合其他指标**: 困惑度只是流畅性指标，需要与多样性、创造力等结合
4. **设置阈值**: 根据任务设定困惑度阈值，过滤低质量文本
5. **批量计算**: 使用批处理提高效率

## 参考资料

- [Perplexity 定义](https://en.wikipedia.org/wiki/Perplexity)
- [GPT-2 论文](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [BERT 论文](https://arxiv.org/abs/1810.04805)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)

---

**更新日期**: 2026-03-04  
**作者**: Kiro AI Assistant
