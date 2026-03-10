# GPU能耗假设检验功能实现总结

## 实现概述

为 `raw_data_analysis.py` 脚本添加了完整的统计假设检验功能，用于分析不同任务类型和模型之间的GPU能耗是否存在显著差异。

## 新增功能

### 1. 核心分析方法

#### `analyze_hypothesis_testing()`
主入口方法，协调所有假设检验分析：
- 任务间差异检验
- 模型间差异检验
- 交互效应分析
- 生成综合报告

#### `_test_energy_across_tasks()`
检验不同任务间GPU能耗差异：
- 描述性统计（均值、标准差、中位数等）
- Shapiro-Wilk正态性检验
- Levene方差齐性检验
- ANOVA或Kruskal-Wallis主检验
- Mann-Whitney U事后检验（Bonferroni校正）
- 箱线图可视化

#### `_test_energy_across_models()`
检验不同模型间GPU能耗差异：
- 描述性统计
- Kruskal-Wallis H检验
- 箱线图可视化

#### `_test_interaction_effects()`
分析任务×模型交互效应：
- 创建交互效应数据透视表
- 生成热力图可视化
- 保存交互效应表

#### `_post_hoc_analysis()`
事后多重比较分析：
- 两两比较所有任务对
- Mann-Whitney U检验
- Bonferroni校正
- 识别显著差异的配对

### 2. 辅助方法

#### `_extract_gpu_energy()`
从实验数据中提取GPU能耗：
- 优先从summary获取
- 备选方案：使用梯形法则计算

#### `_plot_energy_by_task_boxplot()`
绘制任务间能耗箱线图：
- 箱线图 + 散点图
- 显著性标注
- 统计信息展示

#### `_plot_energy_by_model_boxplot()`
绘制模型间能耗箱线图

#### `_generate_hypothesis_report()`
生成Markdown格式的综合报告

## 新增依赖

```python
from scipy import stats
from scipy.stats import f_oneway, kruskal, levene, shapiro, mannwhitneyu
from itertools import combinations
```

## 输出文件结构

```
analysis/qe_research/results/raw_analysis/
├── tables/
│   ├── energy_by_task_descriptive.csv          # 任务描述性统计
│   ├── energy_by_model_descriptive.csv         # 模型描述性统计
│   ├── energy_normality_test.csv               # 正态性检验
│   ├── energy_task_hypothesis_test.csv         # 任务间主检验
│   ├── energy_model_hypothesis_test.csv        # 模型间主检验
│   ├── energy_post_hoc_comparisons.csv         # 事后比较
│   └── energy_interaction_table.csv            # 交互效应表
├── figures/
│   ├── 07_interaction_heatmap.png              # 交互效应热力图
│   ├── 08_energy_by_task_boxplot.png           # 任务箱线图
│   └── 09_energy_by_model_boxplot.png          # 模型箱线图
└── reports/
    └── hypothesis_testing_report.md            # 综合报告
```

## 统计方法选择逻辑

```
数据收集
    ↓
描述性统计
    ↓
正态性检验 (Shapiro-Wilk)
    ↓
方差齐性检验 (Levene)
    ↓
    ├─→ 正态 + 方差齐性 → ANOVA
    └─→ 否则 → Kruskal-Wallis
         ↓
    p < 0.05?
         ↓
    是 → 事后检验 (Mann-Whitney U + Bonferroni)
```

## 使用示例

### 示例1: 单独运行假设检验

```bash
conda activate bartscore
python analysis/qe_research/scripts/test_hypothesis_testing.py
```

### 示例2: Python代码调用

```python
from analysis.qe_research.scripts.raw_data_analysis import RawDataAnalyzer

# 创建分析器
analyzer = RawDataAnalyzer(data_root='data')

# 加载数据
analyzer.load_all_raw_data()

# 运行假设检验
analyzer.analyze_hypothesis_testing()
```

### 示例3: 集成到完整分析流程

```python
# 在 run_all_analyses() 中已自动包含
analyzer.run_all_analyses()
```

## 关键特性

### 1. 自动方法选择
- 根据数据分布自动选择参数或非参数方法
- 确保统计检验的有效性

### 2. 多重比较校正
- Bonferroni校正控制家族错误率
- 避免假阳性结果

### 3. 完整的可视化
- 箱线图展示分布和离群值
- 热力图展示交互效应
- 统计显著性标注

### 4. 详细的日志记录
- 每个步骤都有日志输出
- 便于调试和结果追踪

### 5. 中文支持
- 所有输出文件使用UTF-8编码
- 图表标签支持中文显示

## 技术亮点

### 1. 稳健的数据提取
```python
def _extract_gpu_energy(self, exp: Dict) -> float:
    # 多种数据源尝试
    # 1. 从summary获取
    # 2. 从measurements计算
    # 3. 返回None（缺失数据）
```

### 2. 灵活的检验策略
```python
if all_normal and variance_homogeneity:
    # 参数方法
    f_stat, p_value = f_oneway(*energy_groups)
else:
    # 非参数方法
    h_stat, p_value = kruskal(*energy_groups)
```

### 3. 完整的错误处理
```python
if len(energy_by_task) < 2:
    logger.warning("任务类型不足，无法进行假设检验")
    return
```

## 验证和测试

### 测试脚本
`test_hypothesis_testing.py` 提供了独立的测试功能：
- 加载数据验证
- 假设检验执行
- 结果文件检查

### 预期输出
- 7个CSV表格文件
- 3个PNG图表文件
- 1个Markdown报告文件

## 扩展建议

### 短期扩展
1. 添加效应量计算（Cohen's d, η²）
2. 添加置信区间估计
3. 支持其他校正方法（FDR, Holm）

### 中期扩展
1. 功效分析（样本量估计）
2. 双因素方差分析（完整交互效应）
3. 重复测量设计支持

### 长期扩展
1. 贝叶斯假设检验
2. 自动化报告生成（包含解释）
3. 交互式可视化（Plotly）

## 文档资源

1. **使用指南**: `docs/HYPOTHESIS_TESTING_GUIDE.md`
   - 详细的使用说明
   - 统计方法解释
   - 结果解读指南

2. **测试脚本**: `scripts/test_hypothesis_testing.py`
   - 独立测试功能
   - 快速验证

3. **主脚本**: `scripts/raw_data_analysis.py`
   - 完整实现代码
   - 集成到分析流程

## 依赖要求

```bash
# 核心依赖
pip install pandas numpy matplotlib seaborn scipy

# 可选依赖（已有）
pip install tabulate
```

## 性能考虑

- 对于大数据集，Kruskal-Wallis比ANOVA更快
- 事后检验的复杂度为O(n²)，任务数量多时较慢
- 可视化生成是主要时间消耗

## 已知限制

1. **样本量要求**: 每组至少需要3个样本
2. **计算复杂度**: 事后检验在组数多时较慢
3. **交互效应**: 仅提供描述性分析，未进行统计检验

## 版本信息

- **实现日期**: 2025-01-XX
- **Python版本**: 3.8+
- **SciPy版本**: 1.7+

## 贡献者

- 实现: Kiro AI Assistant
- 需求: 用户需求分析

## 许可证

遵循项目主许可证

## 更新日志

### v1.0.0 (2025-01-XX)
- ✅ 初始实现
- ✅ 任务间差异检验
- ✅ 模型间差异检验
- ✅ 交互效应分析
- ✅ 事后多重比较
- ✅ 完整文档

## 联系方式

如有问题或建议，请查看项目文档或提交Issue。
