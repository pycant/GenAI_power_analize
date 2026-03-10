# Pareto Analysis V3 完整文档索引

> 📅 生成时间: 2026-03-09 16:54:40
> 
> 📂 目录: `pareto_analysis_v3`

## 📋 概述

本目录包含基于 PCA（主成分分析）方法的帕累托前沿分析结果。通过 PCA 综合各模型的多维质量指标，
并结合效率指标（速度、能耗）进行帕累托前沿分析，识别在质量-效率权衡中表现最优的模型。

### 🎯 分析方法

1. **PCA 质量综合**: 使用主成分分析将多个质量指标降维为综合质量得分
2. **熵权法**: 基于信息熵计算各质量指标的客观权重
3. **帕累托前沿**: 识别在质量-速度和质量-能耗两个维度上的非支配解
4. **多任务评估**: 针对不同任务类型（代码、创意、数学、问答、推理、摘要、翻译）分别分析

### 📊 任务类型覆盖

- ✅ **代码生成** (`code`)
- ✅ **创意写作** (`creative`)
- ✅ **数学推理** (`math`)
- ✅ **问答任务** (`qa`)
- ✅ **逻辑推理** (`reasoning`)
- ✅ **文本摘要** (`summary`)
- ✅ **机器翻译** (`translation`)

## 📚 综合报告

### 📖 [生成式语言模型多任务质效比综合评估报告](qe_research\results\pareto_analysis_v3\COMPREHENSIVE_PARETO_ANALYSIS_REPORT.md)

> **报告生成时间**: 2026-03-09 **分析版本**: v3 **评估任务**: 代码生成、创意写作、数学推理、问答、摘要生成、翻译

### 📈 资源统计

- 📄 报告文件: 8 个
- 🔬 PCA 分析报告: 6 个
- 📊 图表文件: 44 张
- 💾 数据文件: 7 个

## 🔍 任务详细索引

以下按任务类型组织的详细文档和资源索引：

### CODE 任务

📊 **资源统计**: 1 个主报告 | 1 个PCA报告 | 7 张图表 | 1 个数据文件

#### 📄 主报告

**[代码生成任务帕累托前沿分析报告](qe_research\results\pareto_analysis_v3\code\CODE_PARETO_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:59 - **任务类型**: 代码生成任务（code） - **模型数量**: 11

#### 🔬 PCA 分析报告

**[PCA降维分析报告 - CODE任务](qe_research\results\pareto_analysis_v3\code\pca_analysis\PCA_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:58 - **任务类型**: code - **样本数量**: 11 个模型

#### 📈 主要图表

- [entropy_weights.png](qe_research\results\pareto_analysis_v3\code\entropy_weights.png)
- [pareto_quality_energy.png](qe_research\results\pareto_analysis_v3\code\pareto_quality_energy.png)
- [pareto_quality_speed.png](qe_research\results\pareto_analysis_v3\code\pareto_quality_speed.png)

#### 🔍 PCA 可视化

- [pca_biplot.png](qe_research\results\pareto_analysis_v3\code\pca_analysis\pca_biplot.png)
- [pca_component_scores.png](qe_research\results\pareto_analysis_v3\code\pca_analysis\pca_component_scores.png)
- [pca_loadings_heatmap.png](qe_research\results\pareto_analysis_v3\code\pca_analysis\pca_loadings_heatmap.png)
- [pca_scree_plot.png](qe_research\results\pareto_analysis_v3\code\pca_analysis\pca_scree_plot.png)

#### 💾 数据文件

- [merged_data.csv](qe_research\results\pareto_analysis_v3\code\merged_data.csv) (1.1 KB)

---

### CREATIVE 任务

📊 **资源统计**: 1 个主报告 | 1 个PCA报告 | 7 张图表 | 1 个数据文件

#### 📄 主报告

**[创意写作任务帕累托前沿分析报告](qe_research\results\pareto_analysis_v3\creative\CREATIVE_PARETO_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:20:02 - **任务类型**: 创意写作任务（creative） - **模型数量**: 12

#### 🔬 PCA 分析报告

**[PCA降维分析报告 - CREATIVE任务](qe_research\results\pareto_analysis_v3\creative\pca_analysis\PCA_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:20:01 - **任务类型**: creative - **样本数量**: 12 个模型

#### 📈 主要图表

- [entropy_weights.png](qe_research\results\pareto_analysis_v3\creative\entropy_weights.png)
- [pareto_quality_energy.png](qe_research\results\pareto_analysis_v3\creative\pareto_quality_energy.png)
- [pareto_quality_speed.png](qe_research\results\pareto_analysis_v3\creative\pareto_quality_speed.png)

#### 🔍 PCA 可视化

- [pca_biplot.png](qe_research\results\pareto_analysis_v3\creative\pca_analysis\pca_biplot.png)
- [pca_component_scores.png](qe_research\results\pareto_analysis_v3\creative\pca_analysis\pca_component_scores.png)
- [pca_loadings_heatmap.png](qe_research\results\pareto_analysis_v3\creative\pca_analysis\pca_loadings_heatmap.png)
- [pca_scree_plot.png](qe_research\results\pareto_analysis_v3\creative\pca_analysis\pca_scree_plot.png)

#### 💾 数据文件

- [merged_data.csv](qe_research\results\pareto_analysis_v3\creative\merged_data.csv) (1.2 KB)

---

### MATH 任务

📊 **资源统计**: 1 个主报告 | 1 个PCA报告 | 7 张图表 | 1 个数据文件

#### 📄 主报告

**[数学任务帕累托前沿分析报告](qe_research\results\pareto_analysis_v3\math\MATH_PARETO_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:56 - **任务类型**: 数学任务（math） - **模型数量**: 11

#### 🔬 PCA 分析报告

**[PCA降维分析报告 - MATH任务](qe_research\results\pareto_analysis_v3\math\pca_analysis\PCA_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:55 - **任务类型**: math - **样本数量**: 11 个模型

#### 📈 主要图表

- [entropy_weights.png](qe_research\results\pareto_analysis_v3\math\entropy_weights.png)
- [pareto_quality_energy.png](qe_research\results\pareto_analysis_v3\math\pareto_quality_energy.png)
- [pareto_quality_speed.png](qe_research\results\pareto_analysis_v3\math\pareto_quality_speed.png)

#### 🔍 PCA 可视化

- [pca_biplot.png](qe_research\results\pareto_analysis_v3\math\pca_analysis\pca_biplot.png)
- [pca_component_scores.png](qe_research\results\pareto_analysis_v3\math\pca_analysis\pca_component_scores.png)
- [pca_loadings_heatmap.png](qe_research\results\pareto_analysis_v3\math\pca_analysis\pca_loadings_heatmap.png)
- [pca_scree_plot.png](qe_research\results\pareto_analysis_v3\math\pca_analysis\pca_scree_plot.png)

#### 💾 数据文件

- [merged_data.csv](qe_research\results\pareto_analysis_v3\math\merged_data.csv) (1.1 KB)

---

### QA 任务

📊 **资源统计**: 1 个主报告 | 1 个PCA报告 | 7 张图表 | 1 个数据文件

#### 📄 主报告

**[问答任务帕累托前沿分析报告](qe_research\results\pareto_analysis_v3\qa\QA_PARETO_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:53 - **任务类型**: 问答任务（qa） - **模型数量**: 11

#### 🔬 PCA 分析报告

**[PCA降维分析报告 - QA任务](qe_research\results\pareto_analysis_v3\qa\pca_analysis\PCA_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:52 - **任务类型**: qa - **样本数量**: 11 个模型

#### 📈 主要图表

- [entropy_weights.png](qe_research\results\pareto_analysis_v3\qa\entropy_weights.png)
- [pareto_quality_energy.png](qe_research\results\pareto_analysis_v3\qa\pareto_quality_energy.png)
- [pareto_quality_speed.png](qe_research\results\pareto_analysis_v3\qa\pareto_quality_speed.png)

#### 🔍 PCA 可视化

- [pca_biplot.png](qe_research\results\pareto_analysis_v3\qa\pca_analysis\pca_biplot.png)
- [pca_component_scores.png](qe_research\results\pareto_analysis_v3\qa\pca_analysis\pca_component_scores.png)
- [pca_loadings_heatmap.png](qe_research\results\pareto_analysis_v3\qa\pca_analysis\pca_loadings_heatmap.png)
- [pca_scree_plot.png](qe_research\results\pareto_analysis_v3\qa\pca_analysis\pca_scree_plot.png)

#### 💾 数据文件

- [merged_data.csv](qe_research\results\pareto_analysis_v3\qa\merged_data.csv) (1.1 KB)

---

### REASONING 任务

📊 **资源统计**: 1 个主报告 | 1 个PCA报告 | 6 张图表 | 1 个数据文件

#### 📄 主报告

**[推理任务帕累托前沿分析报告](qe_research\results\pareto_analysis_v3\reasoning\REASONING_PARETO_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:20:05 - **任务类型**: 推理任务（reasoning） - **模型数量**: 11

#### 🔬 PCA 分析报告

**[PCA降维分析报告 - REASONING任务](qe_research\results\pareto_analysis_v3\reasoning\pca_analysis\PCA_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:20:04 - **任务类型**: reasoning - **样本数量**: 11 个模型

#### 📈 主要图表

- [pareto_quality_energy.png](qe_research\results\pareto_analysis_v3\reasoning\pareto_quality_energy.png)
- [pareto_quality_speed.png](qe_research\results\pareto_analysis_v3\reasoning\pareto_quality_speed.png)

#### 🔍 PCA 可视化

- [pca_biplot.png](qe_research\results\pareto_analysis_v3\reasoning\pca_analysis\pca_biplot.png)
- [pca_component_scores.png](qe_research\results\pareto_analysis_v3\reasoning\pca_analysis\pca_component_scores.png)
- [pca_loadings_heatmap.png](qe_research\results\pareto_analysis_v3\reasoning\pca_analysis\pca_loadings_heatmap.png)
- [pca_scree_plot.png](qe_research\results\pareto_analysis_v3\reasoning\pca_analysis\pca_scree_plot.png)

#### 💾 数据文件

- [merged_data.csv](qe_research\results\pareto_analysis_v3\reasoning\merged_data.csv) (1.1 KB)

---

### SUMMARY 任务

📊 **资源统计**: 1 个主报告 | 1 个PCA报告 | 7 张图表 | 1 个数据文件

#### 📄 主报告

**[摘要任务帕累托前沿分析报告](qe_research\results\pareto_analysis_v3\summary\SUMMARY_PARETO_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:50 - **任务类型**: 摘要任务（summary） - **模型数量**: 11

#### 🔬 PCA 分析报告

**[PCA降维分析报告 - SUMMARY任务](qe_research\results\pareto_analysis_v3\summary\pca_analysis\PCA_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 16:19:49 - **任务类型**: summary - **样本数量**: 11 个模型

#### 📈 主要图表

- [entropy_weights.png](qe_research\results\pareto_analysis_v3\summary\entropy_weights.png)
- [pareto_quality_energy.png](qe_research\results\pareto_analysis_v3\summary\pareto_quality_energy.png)
- [pareto_quality_speed.png](qe_research\results\pareto_analysis_v3\summary\pareto_quality_speed.png)

#### 🔍 PCA 可视化

- [pca_biplot.png](qe_research\results\pareto_analysis_v3\summary\pca_analysis\pca_biplot.png)
- [pca_component_scores.png](qe_research\results\pareto_analysis_v3\summary\pca_analysis\pca_component_scores.png)
- [pca_loadings_heatmap.png](qe_research\results\pareto_analysis_v3\summary\pca_analysis\pca_loadings_heatmap.png)
- [pca_scree_plot.png](qe_research\results\pareto_analysis_v3\summary\pca_analysis\pca_scree_plot.png)

#### 💾 数据文件

- [merged_data.csv](qe_research\results\pareto_analysis_v3\summary\merged_data.csv) (1.1 KB)

---

### TRANSLATION 任务

📊 **资源统计**: 1 个主报告 | 0 个PCA报告 | 3 张图表 | 1 个数据文件

#### 📄 主报告

**[翻译任务帕累托前沿分析报告](qe_research\results\pareto_analysis_v3\translation\TRANSLATION_PARETO_ANALYSIS_REPORT.md)**

> **生成时间**: 2026-03-09 15:56:40 - **任务类型**: 翻译任务（translation） - **模型数量**: 11

#### 📈 主要图表

- [entropy_weights.png](qe_research\results\pareto_analysis_v3\translation\entropy_weights.png)
- [pareto_quality_energy.png](qe_research\results\pareto_analysis_v3\translation\pareto_quality_energy.png)
- [pareto_quality_speed.png](qe_research\results\pareto_analysis_v3\translation\pareto_quality_speed.png)

#### 💾 数据文件

- [merged_data.csv](qe_research\results\pareto_analysis_v3\translation\merged_data.csv) (1.1 KB)

---

## 📖 使用指南

### 查看分析结果

1. **综合报告**: 从 `COMPREHENSIVE_PARETO_ANALYSIS_REPORT.md` 开始，了解整体分析结果
2. **任务特定分析**: 根据感兴趣的任务类型，查看对应目录下的主报告
3. **PCA 详情**: 查看 `pca_analysis/PCA_ANALYSIS_REPORT.md` 了解质量指标的降维和综合过程
4. **可视化**: 浏览各目录下的 PNG 图表文件，直观理解帕累托前沿

### 关键图表说明

- `pareto_quality_speed.png`: 质量-速度帕累托前沿图
- `pareto_quality_energy.png`: 质量-能耗帕累托前沿图
- `entropy_weights.png`: 熵权法计算的指标权重分布
- `pca_scree_plot.png`: PCA 碎石图（主成分方差解释率）
- `pca_loadings_heatmap.png`: PCA 载荷热力图（指标贡献度）
- `pca_biplot.png`: PCA 双标图（模型与指标关系）
- `pca_component_scores.png`: 主成分得分分布

### 数据文件

- `merged_data.csv`: 合并的质量、效率和 PCA 结果数据，可用于进一步分析

## 🔗 相关文档

- [PCA 功能完整说明](../../scripts/pareto_core/PCA_FEATURE_COMPLETE.md)
- [帕累托分析快速参考](../../scripts/pareto_core/QUICK_REFERENCE.md)
- [质量分析指南](../../COMPREHENSIVE_QUALITY_ANALYSIS_GUIDE.md)
- [假设检验指南](../../docs/HYPOTHESIS_TESTING_GUIDE.md)

## 🛠️ 重新生成索引

运行以下命令重新生成本索引文档：

```bash
python analysis/qe_research/scripts/generate_pareto_v3_index.py
```

---

*本文档由自动化脚本生成，如有问题请查看脚本源码或联系维护者。*
