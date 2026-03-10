# GPU能耗假设检验分析指南

## 概述

本模块为 `raw_data_analysis.py` 添加了统计假设检验功能，用于检验不同任务类型和模型之间的GPU能耗是否存在显著差异。

## 功能特性

### 1. 任务间差异检验
检验不同任务类型（code、creative、qa、summary等）之间的GPU能耗是否存在显著差异。

**检验流程**:
1. **描述性统计**: 计算各任务的均值、标准差、中位数等
2. **正态性检验**: Shapiro-Wilk检验判断数据是否服从正态分布
3. **方差齐性检验**: Levene检验判断各组方差是否相等
4. **主检验**: 
   - 如果数据正态且方差齐性 → 单因素方差分析(ANOVA)
   - 否则 → Kruskal-Wallis H检验（非参数）
5. **事后检验**: 如果主检验显著，进行两两比较（Mann-Whitney U检验 + Bonferroni校正）

### 2. 模型间差异检验
检验不同模型之间的GPU能耗是否存在显著差异。

**检验方法**:
- Kruskal-Wallis H检验（非参数方法，适用于多组比较）

### 3. 交互效应分析
分析任务类型和模型之间的交互效应，通过热力图展示不同任务-模型组合的能耗模式。

## 使用方法

### 方法1: 单独运行假设检验

```bash
# 激活环境
conda activate bartscore

# 运行测试脚本
python analysis/qe_research/scripts/test_hypothesis_testing.py
```

### 方法2: 在完整分析中包含假设检验

```python
from analysis.qe_research.scripts.raw_data_analysis import RawDataAnalyzer

# 创建分析器
analyzer = RawDataAnalyzer(data_root='data')

# 加载数据
analyzer.load_all_raw_data()

# 运行假设检验
analyzer.analyze_hypothesis_testing()
```

### 方法3: 在完整分析流程中运行

```bash
# 运行完整分析（包含假设检验）
python analysis/qe_research/scripts/raw_data_analysis.py
```

## 输出文件

### 表格文件 (tables/)

1. **energy_by_task_descriptive.csv**
   - 各任务GPU能耗的描述性统计
   - 包含: 样本量、均值、标准差、中位数、最小值、最大值

2. **energy_by_model_descriptive.csv**
   - 各模型GPU能耗的描述性统计

3. **energy_normality_test.csv**
   - Shapiro-Wilk正态性检验结果
   - W统计量、p值、是否正态

4. **energy_task_hypothesis_test.csv**
   - 任务间差异的主检验结果
   - 检验类型、统计量、p值、结论

5. **energy_model_hypothesis_test.csv**
   - 模型间差异的主检验结果

6. **energy_post_hoc_comparisons.csv**
   - 事后多重比较结果（两两比较）
   - U统计量、p值、校正后显著性、均值差

7. **energy_interaction_table.csv**
   - 任务×模型交互效应表（能耗均值）

### 图表文件 (figures/)

1. **08_energy_by_task_boxplot.png**
   - 任务间GPU能耗箱线图
   - 包含散点图和统计显著性标注

2. **09_energy_by_model_boxplot.png**
   - 模型间GPU能耗箱线图

3. **07_interaction_heatmap.png**
   - 任务×模型交互效应热力图

### 报告文件 (reports/)

**hypothesis_testing_report.md**
- 完整的假设检验分析报告
- 包含方法说明、结果文件列表、解读指南

## 统计方法说明

### 1. Shapiro-Wilk检验
- **用途**: 检验数据是否服从正态分布
- **零假设**: 数据服从正态分布
- **判断**: p > 0.05 → 正态分布

### 2. Levene检验
- **用途**: 检验各组方差是否相等
- **零假设**: 各组方差相等
- **判断**: p > 0.05 → 方差齐性

### 3. 单因素方差分析(ANOVA)
- **适用条件**: 数据正态 + 方差齐性
- **零假设**: 各组均值相等
- **判断**: p < 0.05 → 存在显著差异

### 4. Kruskal-Wallis H检验
- **适用条件**: 非参数方法，无需正态性假设
- **零假设**: 各组分布相同
- **判断**: p < 0.05 → 存在显著差异

### 5. Mann-Whitney U检验
- **用途**: 两组间的非参数比较
- **零假设**: 两组分布相同
- **Bonferroni校正**: α_corrected = 0.05 / n_comparisons

## 显著性水平解读

| p值范围 | 显著性 | 符号 | 解释 |
|---------|--------|------|------|
| p < 0.001 | 极显著 | *** | 有极强证据表明存在差异 |
| p < 0.01 | 非常显著 | ** | 有很强证据表明存在差异 |
| p < 0.05 | 显著 | * | 有证据表明存在差异 |
| p ≥ 0.05 | 不显著 | ns | 无足够证据表明存在差异 |

## 结果解读示例

### 示例1: 任务间存在显著差异

```
Kruskal-Wallis检验: H=25.34, p=0.0001 ***
结论: 不同任务类型的GPU能耗存在极显著差异
```

**解读**:
- 至少有两个任务的能耗分布存在显著差异
- 需要查看事后检验结果，确定具体哪些任务对之间存在差异
- 结合描述性统计，了解各任务的能耗水平

### 示例2: 事后检验结果

```
code vs creative: p=0.0023 ** (显著)
code vs qa: p=0.1234 ns (不显著)
creative vs qa: p=0.0456 * (显著)
```

**解读**:
- code和creative任务的能耗存在显著差异
- creative和qa任务的能耗存在显著差异
- code和qa任务的能耗无显著差异

## 注意事项

### 1. 样本量要求
- 每组至少需要3个样本才能进行正态性检验
- 样本量过小会降低检验效力
- 建议每组至少有10个样本

### 2. 异常值处理
- 箱线图可以帮助识别异常值
- 异常值可能影响参数检验结果
- 非参数检验对异常值更稳健

### 3. 多重比较校正
- 进行多次比较时必须校正显著性水平
- Bonferroni校正较为保守
- 可以考虑其他校正方法（如FDR）

### 4. 统计显著 vs 实际重要
- p < 0.05只表示统计显著
- 还需要关注效应量（均值差、中位数差）
- 小的差异可能统计显著但实际不重要

### 5. 假设检验的局限性
- 不能证明零假设为真
- 只能拒绝或不拒绝零假设
- 需要结合领域知识解释结果

## 扩展功能建议

### 1. 效应量计算
- Cohen's d（标准化均值差）
- η² (eta squared) 用于ANOVA
- ε² (epsilon squared) 用于Kruskal-Wallis

### 2. 置信区间
- 均值差的置信区间
- 中位数差的置信区间

### 3. 功效分析
- 事前功效分析（样本量估计）
- 事后功效分析（检验效力评估）

### 4. 其他检验方法
- Welch's ANOVA（方差不齐时）
- Friedman检验（重复测量）
- 双因素方差分析（交互效应）

## 参考文献

1. Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality. Biometrika, 52(3/4), 591-611.

2. Levene, H. (1960). Robust tests for equality of variances. In Contributions to Probability and Statistics, 278-292.

3. Kruskal, W. H., & Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. Journal of the American Statistical Association, 47(260), 583-621.

4. Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. The Annals of Mathematical Statistics, 18(1), 50-60.

5. Bonferroni, C. (1936). Teoria statistica delle classi e calcolo delle probabilita. Pubblicazioni del R Istituto Superiore di Scienze Economiche e Commericiali di Firenze, 8, 3-62.

## 技术支持

如有问题或建议，请查看:
- 主分析脚本: `analysis/qe_research/scripts/raw_data_analysis.py`
- 测试脚本: `analysis/qe_research/scripts/test_hypothesis_testing.py`
- 日志文件: `analysis/qe_research/logs/raw_analysis.log`
