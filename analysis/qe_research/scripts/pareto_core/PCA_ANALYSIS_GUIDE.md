# PCA分析功能使用指南

## 功能概述

PCA（主成分分析）功能已集成到 `shared_functions.py` 中，提供完整的降维分析、可视化和报告生成能力。

## 核心功能

### 1. 自动PCA分析
- 自动选择累积解释方差 ≥ 85% 的主成分
- 按解释方差比例加权计算综合质量得分
- 支持多种归一化方法

### 2. 可视化图表（4种）
- **碎石图** (`pca_scree_plot.png`): 解释方差比例和累积方差
- **载荷热力图** (`pca_loadings_heatmap.png`): 特征载荷矩阵
- **双标图** (`pca_biplot.png`): 样本和特征的二维投影
- **主成分得分图** (`pca_component_scores.png`): 各模型在主成分上的得分

### 3. 详细分析报告
自动生成 `PCA_ANALYSIS_REPORT.md`，包含：
- 分析概览和方差解释
- 主成分载荷分析
- 模型得分排名
- 综合质量评估
- 原始数据统计
- 分析结论和建议

## 使用方法

### 基本用法

```python
from analysis.qe_research.scripts.pareto_core.shared_functions import load_process_quality_data

# 使用PCA方法加载质量数据
quality_df = load_process_quality_data(
    task_name='code',           # 任务名称
    method='pca',               # 使用PCA方法
    output_dir='results/code',  # 输出目录
    verbose=True                # 显示详细信息
)
```

### 输出结构

```
results/code/
└── pca_analysis/
    ├── PCA_ANALYSIS_REPORT.md          # 详细分析报告
    ├── pca_scree_plot.png              # 碎石图
    ├── pca_loadings_heatmap.png        # 载荷热力图
    ├── pca_biplot.png                  # 双标图
    └── pca_component_scores.png        # 主成分得分图
```

### 在Pareto分析中使用

```python
from analysis.qe_research.scripts.pareto_core.shared_functions import (
    load_process_quality_data,
    load_energy_speed_data,
    merge_quality_metrics
)

# 1. 使用PCA加载质量数据
quality_df = load_process_quality_data(
    task_name='code',
    method='pca',
    output_dir='results/pareto_analysis/code'
)

# 2. 加载能耗和速度数据
energy_dict, speed_dict = load_energy_speed_data(
    task_name='code',
    energy_file='path/to/energy.csv',
    speed_file='path/to/speed.csv'
)

# 3. 合并数据
merged_df = merge_quality_metrics(
    quality_df=quality_df,
    energy_dict=energy_dict,
    speed_dict=speed_dict,
    model_mapping=MODEL_MAPPING
)

# 4. 继续进行Pareto分析...
```

## 参数说明

### load_process_quality_data() 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| task_name | str | 必需 | 任务名称（code, creative, reasoning等） |
| method | str | 'entropy' | 处理方法，使用 'pca' 启用PCA分析 |
| normalize_method | str | 'minmax' | 归一化方法（minmax, zscore, robust, maxabs） |
| use_raw | bool | True | 是否使用原始数据（保留完整精度） |
| verbose | bool | True | 是否输出详细信息 |
| output_dir | str/Path | None | 输出目录，None则不生成图表和报告 |

## 报告内容说明

### 1. 分析概览
- 任务类型和样本数量
- 原始特征数和主成分数量
- 累积解释方差

### 2. 方差解释
- 各主成分的解释方差比例
- 累积解释方差
- 主成分选择策略说明

### 3. 主成分载荷分析
- 各主成分的主要贡献特征
- 载荷值和方向
- 主成分含义解释

### 4. 完整载荷矩阵
- 所有特征在各主成分上的载荷值
- 便于深入分析特征关系

### 5. 模型主成分得分
- 各模型在主成分上的得分排名
- 相对表现评级

### 6. 综合质量得分
- 基于解释方差加权的综合得分
- 模型综合排名和评级

### 7. 原始数据统计
- 特征的描述性统计
- 均值、标准差、最小值、最大值

### 8. 可视化图表
- 生成的图表列表和说明

### 9. 分析结论
- 降维效果评估
- 最佳模型推荐
- 主要发现总结

## 测试

运行测试脚本验证功能：

```bash
# 激活conda环境
conda activate bartscore

# 运行测试
python analysis/qe_research/scripts/pareto_core/test_pca_plotting.py
```

测试将对 code、creative、reasoning 三个任务执行PCA分析，并生成完整的报告和图表。

## 注意事项

1. **数据要求**: 确保质量数据文件存在且格式正确
2. **输出目录**: 必须指定 `output_dir` 参数才会生成图表和报告
3. **中文支持**: 报告和图表支持中文显示，自动检测系统字体
4. **内存占用**: PCA分析需要加载完整数据到内存，大数据集可能需要较多内存

## 高级用法

### 自定义主成分数量

如果需要手动指定主成分数量，可以直接使用 `QualityDataProcessor`:

```python
from analysis.qe_research.scripts.pareto_core.process_quality_data import QualityDataProcessor

processor = QualityDataProcessor(task_name='code', verbose=True)
data = processor.load_quality_data()

# 指定保留3个主成分
pca_result = processor.apply_pca(n_components=3, normalize_first=True)

# 或指定保留90%的方差
pca_result = processor.apply_pca(n_components=0.9, normalize_first=True)
```

### 单独生成报告

```python
from analysis.qe_research.scripts.pareto_core.shared_functions import (
    generate_pca_report,
    plot_pca_figures
)

# 假设已有pca_result
report_path = generate_pca_report(
    pca_result=pca_result,
    task_name='code',
    output_dir='custom/output/dir',
    quality_data=original_data,  # 可选
    verbose=True
)

# 单独生成图表
figures = plot_pca_figures(
    pca_result=pca_result,
    task_name='code',
    output_dir='custom/output/dir',
    verbose=True
)
```

## 相关文档

- [Pareto分析快速参考](QUICK_REFERENCE.md)
- [质量数据处理模块](process_quality_data.py)
- [共享函数文档](shared_functions.py)

## 更新日志

- **2026-03-09**: 添加PCA分析报告生成功能
- **2026-03-09**: 添加PCA可视化图表功能
- **2026-03-09**: 集成到 load_process_quality_data 函数

---

**维护者**: Kiro AI Assistant  
**最后更新**: 2026-03-09
