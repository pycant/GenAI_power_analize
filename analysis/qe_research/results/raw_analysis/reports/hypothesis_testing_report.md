# GPU能耗假设检验分析报告

生成时间: 2026-03-08 15:09:51

## 1. 分析目的

本报告通过统计假设检验方法，分析不同任务类型和模型之间的GPU能耗是否存在显著差异。

## 2. 检验方法

### 2.1 任务间差异检验

- **正态性检验**: Shapiro-Wilk检验
- **方差齐性检验**: Levene检验
- **主检验**: 根据数据分布选择ANOVA或Kruskal-Wallis检验
- **事后检验**: Mann-Whitney U检验（Bonferroni校正）

### 2.2 模型间差异检验

- **主检验**: Kruskal-Wallis H检验（非参数方法）

### 2.3 交互效应分析

- **方法**: 任务×模型交互效应热力图

## 3. 显著性水平

- α = 0.05（主检验）
- Bonferroni校正用于多重比较

## 4. 结果文件

### 描述性统计
- `energy_by_task_descriptive.csv`: 各任务GPU能耗描述性统计
- `energy_by_model_descriptive.csv`: 各模型GPU能耗描述性统计

### 假设检验结果
- `energy_normality_test.csv`: 正态性检验结果
- `energy_task_hypothesis_test.csv`: 任务间差异检验结果
- `energy_model_hypothesis_test.csv`: 模型间差异检验结果
- `energy_post_hoc_comparisons.csv`: 事后多重比较结果
- `energy_interaction_table.csv`: 交互效应表

### 可视化图表
- `08_energy_by_task_boxplot.png`: 任务间能耗箱线图
- `09_energy_by_model_boxplot.png`: 模型间能耗箱线图
- `07_interaction_heatmap.png`: 交互效应热力图

## 5. 解读指南

### p值解读
- p < 0.001: 极显著差异 (***)
- p < 0.01: 非常显著差异 (**)
- p < 0.05: 显著差异 (*)
- p ≥ 0.05: 无显著差异 (ns)

### 效应量
- 除了p值，还应关注实际差异的大小（均值差、中位数差）
- 统计显著不等于实际重要

## 6. 注意事项

- 样本量不足可能影响检验效力
- 异常值可能影响参数检验结果
- 多重比较需要校正显著性水平
- 交互效应需要结合领域知识解释

