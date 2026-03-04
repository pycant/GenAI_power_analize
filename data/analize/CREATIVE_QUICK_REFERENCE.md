# 创意写作质量评估 - 快速参考

## 🚀 快速开始

### 运行基础评估（无需 GPU）
```bash
conda activate bartscore
python data/analize/scripts/evaluate_creative_quality.py --no-ppl
```

### 生成可视化图表
```bash
python data/analize/scripts/visualize_creative_quality.py
```

### 运行完整评估（需要 torch）
```bash
# 先安装依赖
pip install torch transformers

# 运行评估
python data/analize/scripts/evaluate_creative_quality.py
```

## 📊 核心指标

| 指标 | 含义 | 范围 | 越大越好？ |
|------|------|------|-----------|
| Distinct-1 | 词级别多样性 | [0, 1] | ✅ |
| Distinct-2 | 短语多样性（核心） | [0, 1] | ✅ |
| Distinct-3 | 长短语多样性 | [0, 1] | ✅ |
| Perplexity | 流畅度 | [1, ∞) | ❌ |

## 🏆 Top 3 模型

1. 🥇 **qwen_8b_ol_q4km** - Distinct-2: 0.9832
2. 🥈 **phi3_4b_hf_8bit** - Distinct-2: 0.9185
3. 🥉 **deepseek_8b_ol_q4km** - Distinct-2: 0.9011

## 📁 输出文件位置

```
data/analize/results/creative_quality/
├── creative_quality_scores.csv      # 详细评分
├── creative_quality_summary.csv     # 汇总统计
├── creative_quality_report.md       # 分析报告
└── figures/                         # 可视化图表
    ├── creative_diversity_comparison.png
    ├── creative_diversity_heatmap.png
    ├── creative_radar_chart.png
    ├── creative_distribution_violin.png
    └── creative_correlation_matrix.png
```

## 🔧 命令行选项

```bash
# 禁用困惑度计算（快速模式）
--no-ppl

# 启用语义多样性（需要额外模型）
--use-semantic

# 指定数据目录
--data-dir path/to/data

# 指定输出目录
--output-dir path/to/output
```

## 📚 相关文档

- 📖 [完整设计文档](CREATIVE_EVALUATION_DESIGN.md)
- 📊 [评估总结](CREATIVE_EVALUATION_SUMMARY.md)
- 🔧 [困惑度安装指南](INSTALL_PERPLEXITY.md)
- 📝 [工作总结](CREATIVE_WORK_SUMMARY_20260304.md)

## 💡 常见问题

**Q: 为什么有些模型没有评分？**  
A: 部分模型-问题组合的响应数据缺失，评估器会自动跳过。

**Q: Distinct-2 为什么是核心指标？**  
A: Distinct-2 在词级和短语级之间取得最佳平衡，最能反映真实的多样性。

**Q: 需要 GPU 吗？**  
A: Distinct-N 不需要 GPU。困惑度计算建议使用 GPU，但 CPU 也可以（较慢）。

**Q: 评估需要多长时间？**  
A: 基础评估（Distinct-N）约 1 分钟，完整评估（含 PPL）约 5-10 分钟。

## 🎯 下一步

1. ⏳ 安装 torch 和 transformers
2. ⏳ 运行完整评估（含困惑度）
3. ⏳ 分析多样性与流畅性的权衡
4. ⏳ 集成到主分析流程

---

**快速参考版本**: v1.0  
**最后更新**: 2026-03-04
