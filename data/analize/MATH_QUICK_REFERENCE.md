# 数学推理任务质量评估 - 快速参考

## 🎯 评估目标

评估大语言模型在数学应用题上的表现，包括：
- ✅ 答案准确性
- ✅ 推理完整性
- ✅ 计算过程展示

## 📊 核心指标

| 指标 | 含义 | 范围 | 越大越好？ |
|------|------|------|-----------|
| Exact Match | 精确匹配 | {0, 1} | ✅ |
| Numerical Match | 数值匹配（1%误差） | {0, 1} | ✅ |
| Has Reasoning | 包含推理过程 | {0, 1} | ✅ |
| Step Count | 推理步骤数 | [0, ∞) | ✅ |
| Has Calculation | 包含计算式 | {0, 1} | ✅ |

## 📝 标准答案

| 问题 | 答案 | 说明 |
|------|------|------|
| q01 | 90 | 利润计算 |
| q02 | 60 | 百分比增长 |
| q03 | 5 | 除法分配 |
| q04 | 21 | 差值计算 |
| q05 | 66 | 总和计算 |

## 🚀 快速开始

### 运行评估
```bash
conda activate bartscore
python data/analize/scripts/evaluate_math_quality.py
```

### 自定义容忍度
```bash
# 允许5%误差
python evaluate_math_quality.py --tolerance 0.05
```

## 📁 输出文件

```
data/analize/results/math_quality/
├── math_quality_scores.csv      # 详细评分
├── math_quality_summary.csv     # 汇总统计
├── math_quality_report.md       # 分析报告
└── figures/                     # 可视化图表
    ├── math_accuracy_comparison.png
    ├── math_accuracy_heatmap.png
    ├── math_reasoning_analysis.png
    └── math_accuracy_vs_reasoning.png
```

## 🔧 答案提取策略

**优先级**：
1. 明确标记: "answer is 90", "result is 90"
2. 等号后: "= 90"
3. 关键词: "total 90", "profit 90"
4. 最后数值: 文本末尾的数字

**归一化**：
- 移除货币符号: $90 → 90
- 移除单位: 90 dollars → 90
- 统一格式: 90.0 → 90

## 💡 评分建议

### 方案1：准确性优先（推荐）
- Exact Match: 70%
- Has Reasoning: 20%
- Extraction Confidence: 10%

### 方案2：均衡评估
- Numerical Match: 50%
- Has Reasoning: 30%
- Has Calculation: 20%

### 方案3：多维度呈现（最推荐）
- 不计算单一分数
- 保留所有原始指标
- 根据应用场景选择关注点

## ⚡ 性能特点

- ✅ 无需GPU
- ✅ 无需外部模型
- ✅ 评估速度快（~1秒）
- ✅ 内存占用低（< 100MB）
- ✅ 完全基于规则

## 🎯 适用场景

**适合**：
- ✅ 简单算术应用题
- ✅ 单步或多步计算
- ✅ 有明确数值答案的问题

**不适合**：
- ❌ 开放式数学问题
- ❌ 需要证明的问题
- ❌ 多个可能答案的问题

## 📚 相关文档

- 📖 [完整设计文档](scripts/MATH_EVALUATION_DESIGN.md)
- 📊 [质量评估体系](scripts/quality_evaluation_system.md)
- 🔧 [评估器实现](scripts/quality_evaluation/math_evaluator.py)

## 🔍 常见问题

**Q: 为什么有两个准确性指标？**  
A: Exact Match 更严格（完全匹配），Numerical Match 更宽松（允许1%误差）。

**Q: 如何处理多个数值的情况？**  
A: 优先匹配明确的答案标记，其次使用最后一个数值。

**Q: 推理完整性如何评分？**  
A: 检测推理关键词、计算步骤数、识别计算式，作为独立维度评估。

**Q: 需要多长时间？**  
A: 约1秒（11模型 × 5问题），无需GPU。

## 🎯 下一步

1. ⏳ 实现MathEvaluator类
2. ⏳ 运行批量评估
3. ⏳ 生成可视化图表
4. ⏳ 分析模型表现差异

---

**快速参考版本**: v1.0  
**最后更新**: 2026-03-04
