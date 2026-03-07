# Pareto分析快速启动指南

## 快速运行

### 单任务分析

```bash
# 激活环境
conda activate bartscore

# 设置UTF-8编码
set PYTHONUTF8=1

# 运行特定任务分析
python analysis/qe_research/scripts/pareto_analysis_reasoning.py
python analysis/qe_research/scripts/pareto_analysis_code.py
python analysis/qe_research/scripts/pareto_analysis_creative.py
python analysis/qe_research/scripts/pareto_analysis_math.py
python analysis/qe_research/scripts/pareto_analysis_qa.py
python analysis/qe_research/scripts/pareto_analysis_summary.py
python analysis/qe_research/scripts/pareto_analysis_translation.py
```

### 使用批处理脚本

```bash
# 运行reasoning任务
analysis\qe_research\scripts\run_pareto_reasoning.bat

# 或直接双击.bat文件
```

## 查看结果

### 报告位置

```
analysis/qe_research/results/pareto_analysis/
├── reasoning/
│   ├── pareto_analysis_report.md          # 分析报告
│   ├── pareto_quality_energy.png          # 质量-能耗图
│   ├── pareto_quality_speed.png           # 质量-速度图
│   ├── pareto_speed_energy.png            # 速度-能耗图
│   ├── pareto_3d.png                      # 三维图
│   └── merged_data.csv                    # 原始数据
├── code/
│   ├── CODE_PARETO_ANALYSIS_REPORT.md     # 分析报告（含稳健性）
│   ├── pareto_quality_energy.png
│   ├── pareto_quality_speed.png
│   └── merged_data.csv
└── creative/
    ├── CREATIVE_PARETO_ANALYSIS_REPORT.md
    ├── pareto_quality_energy.png
    ├── pareto_quality_speed.png
    └── merged_data.csv
```

### 快速查看

1. **查看图表**: 打开对应任务目录下的PNG文件
2. **阅读报告**: 打开对应的Markdown报告文件
3. **数据分析**: 使用Excel或Python打开merged_data.csv

## 本次运行结果（2026-03-07）

### ✅ 成功完成的任务

- **Reasoning**: 11个模型，5个质量-能耗前沿模型
- **Code**: 12个模型，2个质量-能耗前沿模型，稳健性93.33%
- **Creative**: 12个模型，3个质量-能耗前沿模型，稳健性90.33%

### ⭐ 推荐模型

**最佳综合配置**: gemma_4b_ol_q4km
- 在所有3个任务中都是拐点模型
- 质量-能耗权衡最优
- 稳定性100%（Code任务）

**高质量场景**: qwen25_7b_hf_4bit
- Reasoning任务质量得分1.000

**低延迟场景**: qwen_4b_ol_q4km
- 速度最快（60-65 tokens/s）

### ❌ 待修复的任务

以下任务因数据格式问题未能运行：
- QA（问答）
- Summary（摘要）
- Translation（翻译）
- Math（数学推理）

**问题**: 质量数据CSV文件缺少'model'列

## 关键指标说明

### 帕累托前沿

在多目标优化中，没有其他解在所有目标上都优于它的解集合。

- **质量-能耗前沿**: 在保证质量的前提下能耗最低的模型
- **质量-速度前沿**: 在保证质量的前提下速度最快的模型
- **三维前沿**: 综合考虑质量、能耗、速度的最优模型

### 定量指标

- **超体积（Hypervolume）**: 前沿覆盖的目标空间体积，越大越好
- **间距指标（Spacing）**: 前沿解的分布均匀性，越小越好
- **拐点模型**: 质量-能耗权衡曲线上的最优点

### 稳健性分析

- **扰动分析**: 添加±5%噪声后前沿的稳定性
- **交叉验证**: 5折交叉验证的一致性
- **稳定性得分**: 模型在扰动中保持在前沿的频率

## 常见问题

### Q: 如何选择合适的模型？

A: 根据应用场景优先级：
- 质量优先 → 选择质量-能耗前沿上质量最高的模型
- 速度优先 → 选择质量-速度前沿上速度最快的模型
- 平衡方案 → 选择拐点模型或三维前沿上综合评分最高的模型

### Q: 为什么有些任务运行失败？

A: 数据格式问题，质量数据CSV文件缺少'model'列。需要检查数据源或修改脚本。

### Q: 如何理解稳健性分析？

A: 稳健性分析评估模型在数据波动下的稳定性：
- 一致性>90%: 非常稳定 ⭐⭐⭐⭐⭐
- 一致性80-90%: 稳定 ⭐⭐⭐⭐
- 一致性70-80%: 较稳定 ⭐⭐⭐
- 一致性<70%: 需要谨慎使用

### Q: 如何批量运行所有任务？

A: 使用批量分析脚本：
```bash
python analysis/qe_research/scripts/batch_pareto_analysis.py
```

## 下一步

1. 查看生成的可视化图表
2. 阅读详细分析报告
3. 根据应用场景选择合适的模型
4. 修复数据格式问题，完成剩余任务分析

## 技术支持

- 脚本文档: `analysis/qe_research/scripts/PARETO_SCRIPTS_SUMMARY.md`
- 重构说明: `analysis/qe_research/scripts/REFACTORING_COMPLETED.md`
- 项目指南: `AGENTS.md`

---

**更新时间**: 2026-03-07  
**版本**: v1.0
