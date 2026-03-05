# 翻译评估快速参考

## 快速运行

```bash
# 基础评估（快速，1秒）
conda activate bartscore
set PYTHONUTF8=1
python data/analize/scripts/evaluate_translation_quality.py --no-bertscore

# 完整评估（包含BERTScore，1-2分钟）
python data/analize/scripts/evaluate_translation_quality.py

# 生成可视化
python data/analize/scripts/visualize_translation_quality.py
```

## 核心指标

| 指标 | 优秀 | 良好 | 需改进 |
|------|------|------|--------|
| BLEU-4 | ≥0.4 | 0.2-0.4 | <0.2 |
| chrF | ≥0.5 | 0.3-0.5 | <0.3 |
| BERTScore | ≥0.8 | 0.6-0.8 | <0.6 |

## Top 3 模型

1. **deepseek_8b_ol_q4km**: BLEU-4=0.5407 ✅
2. **phi3_4b_hf_4bit**: BLEU-4=0.1008 ❌
3. **gemma_4b_ol_q4km**: BLEU-4=0.0230 ❌

## 输出文件

- `translation_quality_scores.csv` - 详细评分
- `translation_quality_summary.csv` - 汇总统计
- `TRANSLATION_EVALUATION_REPORT.md` - 评估报告
- `figures/` - 可视化图表（5张）

## 关键文件

- 配置: `translation_config.py`
- 评估器: `quality_evaluation/translation_evaluator.py`
- 评估脚本: `evaluate_translation_quality.py`
- 可视化: `visualize_translation_quality.py`
