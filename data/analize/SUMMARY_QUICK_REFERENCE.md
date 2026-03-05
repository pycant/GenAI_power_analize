# Summary任务评估快速参考

## 快速运行

```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行基础评估
cd data/analize/scripts
python evaluate_summary_quality.py

# 运行BARTScore评估（可选，需GPU）
python evaluate_summary_bartscore.py --device cuda

# 生成可视化
python visualize_summary_quality.py
```

## 核心指标

| 指标 | 说明 | 范围 | 越大越好 |
|------|------|------|----------|
| ROUGE-L F1 | 结构完整性 | [0, 1] | ✅ |
| BERTScore F1 | 语义相似度 | [0, 1] | ✅ |
| BARTScore | 生成质量（信息性+忠实性） | (-∞, 0] | ✅ (越接近0) |
| 压缩比 | 简洁性 | [0, ∞) | ❌ (0.2-0.4理想) |
| 信息密度 | 信息效率 | [0, ∞) | ✅ |
| 字数符合度 | 任务完成度 | [0, 1] | ✅ |

## Top 3 模型

### ROUGE-L F1 (结构完整性)
1. qwen25_3b_hf_4bit: 0.1810
2. qwen25_3b_hf_8bit: 0.1333
3. qwen25_7b_hf_4bit: 0.0333

### BERTScore F1 (语义相似度)
1. gemma_2b_hf_8bit: 0.8986
2. qwen_4b_ol_q4km: 0.8062
3. gemma_4b_ol_q4km: 0.7747

### BARTScore (综合质量) ⭐新增
1. gemma_2b_hf_8bit: -2.4015
2. qwen25_3b_hf_4bit: -2.5030
3. qwen_4b_ol_q4km: -2.8505

### 信息密度 (信息效率)
1. qwen25_3b_hf_4bit: 0.1107
2. qwen25_3b_hf_8bit: 0.0600
3. qwen25_7b_hf_4bit: 0.0156

## 应用场景推荐

- **信息保留优先**: qwen25_3b_hf_4bit
- **语义准确优先**: gemma_2b_hf_8bit
- **综合质量优先**: gemma_2b_hf_8bit (BARTScore最高) ⭐
- **简洁性优先**: gemma_4b_ol_q4km
- **字数控制优先**: phi3_4b_hf_8bit

## 输出文件

```
data/analize/results/summary_quality/
├── summary_quality_scores.csv                      # 基础评分
├── summary_quality_scores_with_bartscore.csv       # 包含BARTScore ⭐
├── summary_quality_summary.csv                     # 汇总统计
├── summary_bartscore_summary.csv                   # BARTScore统计 ⭐
├── summary_quality_report.md                       # 基础报告
├── summary_bartscore_report.md                     # BARTScore报告 ⭐
├── summary_quality_insights.md                     # 洞察分析
├── summary_rouge_vs_bertscore.png                  # 图表1
├── summary_compression_ratio_distribution.png      # 图表2
├── summary_radar_chart.png                         # 图表3
├── summary_compliance_vs_density.png               # 图表4
└── summary_bartscore_comparison.png                # 图表5 ⭐
```

## 关键发现

1. **压缩比问题**: 大多数模型>1.0，生成摘要比原文还长
2. **字数符合度低**: 只有phi3_4b_hf_8bit达到20%
3. **量化影响**: 8bit在语义上更好，4bit在结构上可能更好
4. **小模型优势**: Gemma 2B在语义相似度和BARTScore上超越更大模型
5. **BARTScore验证**: 与BERTScore高度相关（0.8239），验证了评估一致性

## 指标相关性

- BARTScore vs BERTScore: 0.8239 (高度相关)
- BARTScore vs ROUGE-L: 0.5420 (中度相关)

## 改进方向

1. **提示工程**: 明确强调字数限制和简洁性
2. **后处理**: 实现智能截断到指定字数
3. **模型微调**: 在摘要数据集上微调以提高字数控制
4. **多参考摘要**: 收集人工标注提高可靠性

## BARTScore使用建议

✅ **推荐使用**:
- 需要最高质量的评估
- 有GPU资源可用
- 评估样本数量适中（<1000）

❌ **不推荐使用**:
- 评估样本数量巨大（>10000）
- 只有CPU资源
- 需要实时评估

