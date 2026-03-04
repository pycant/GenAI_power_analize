# QA质量评估快速参考

## 🚀 快速开始

```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行评估
python data/analize/scripts/evaluate_qa_quality.py

# 查看结果
type data\analize\results\qa_quality\qa_quality_report.md
```

## 📊 核心指标

| 指标 | 说明 | 范围 | 越大越好 |
|------|------|------|----------|
| confidence_score | 答案置信度 | [0, 1] | ✅ |
| technical_term_density | 技术术语密度 | [0, 1] | ✅ |
| has_reasoning | 包含推理 | {0, 1} | ✅ |
| has_conclusion | 有结论 | {0, 1} | ✅ |
| reasoning_steps | 推理步骤数 | [0, ∞) | ✅ |
| uncertainty_count | 不确定性表达 | [0, ∞) | ❌ |

## 🏆 Top 3 模型

### 按置信度
1. gemma_2b_hf_4bit: 56.00%
2. gemma_4b_ol_q4km: 56.00%
3. phi3_4b_hf_8bit: 54.00%

### 按技术密度
1. phi3_4b_hf_4bit: 53.67%
2. phi3_4b_hf_8bit: 53.66%
3. gemma_2b_hf_8bit: 52.98%

## 📈 整体表现

- **平均置信度**: 48.18%
- **平均技术密度**: 39.82%
- **推理完整性**: 92.73%
- **有结论比例**: 16.36%
- **平均答案长度**: 882字符
- **平均推理步骤**: 10.5步

## 💡 关键发现

1. **Gemma模型置信度最高**(56%)
2. **Phi3模型技术性最强**(53%+)
3. **推理完整性普遍较高**(92.73%)
4. **结论性语句较少**(16.36%)
5. **答案长度差异大**(450-1076字符)

## 🎯 模型推荐

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 快速问答 | gemma_2b_hf_4bit | 高置信度,简洁 |
| 技术文档 | phi3_4b_hf_4bit | 高技术性,专业 |
| 平衡选择 | phi3_4b_hf_8bit | 置信度+技术性 |
| 详细解释 | qwen25_7b_hf_4bit | 详细推理,14.6步 |

## 📁 输出文件

```
data/analize/results/qa_quality/
├── qa_quality_scores.csv          # 详细评分(55行×14列)
├── qa_quality_summary.csv         # 汇总统计(11行)
└── qa_quality_report.md           # 分析报告
```

## 🔧 自定义评估

```python
from quality_evaluation.qa_evaluator import QAEvaluator

# 初始化评估器
evaluator = QAEvaluator(config={'domain': 'cs'})

# 评估单个响应
response = "The answer is quicksort..."
scores = evaluator.evaluate(response)

print(f"Confidence: {scores['confidence_score']:.2%}")
print(f"Technical Density: {scores['technical_term_density']:.2%}")
```

## 📖 详细文档

- [评估方法设计](scripts/QA_EVALUATION_DESIGN.md)
- [评估总结](QA_EVALUATION_SUMMARY.md)
- [评估器代码](scripts/quality_evaluation/qa_evaluator.py)

---

**版本**: v1.0 | **更新**: 2026-03-04 | **状态**: ✅ 完成
