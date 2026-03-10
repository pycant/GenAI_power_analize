# GPU能耗假设检验 - 快速开始

## 一分钟快速开始

```bash
# 1. 激活环境
conda activate bartscore

# 2. 安装依赖（如果需要）
pip install scipy

# 3. 运行假设检验
python analysis/qe_research/scripts/test_hypothesis_testing.py
```

## 查看结果

### 表格结果
```bash
# 查看任务间差异检验结果
cat analysis/qe_research/results/raw_analysis/tables/energy_task_hypothesis_test.csv

# 查看事后比较结果
cat analysis/qe_research/results/raw_analysis/tables/energy_post_hoc_comparisons.csv
```

### 图表结果
```
analysis/qe_research/results/raw_analysis/figures/
├── 07_interaction_heatmap.png          # 交互效应热力图
├── 08_energy_by_task_boxplot.png       # 任务间能耗对比
└── 09_energy_by_model_boxplot.png      # 模型间能耗对比
```

### 完整报告
```bash
# 查看综合报告
cat analysis/qe_research/results/raw_analysis/reports/hypothesis_testing_report.md
```

## 核心问题解答

### Q1: 不同任务的GPU能耗有显著差异吗？
**查看**: `energy_task_hypothesis_test.csv`
- p < 0.05 → 有显著差异
- p ≥ 0.05 → 无显著差异

### Q2: 哪些任务对之间存在显著差异？
**查看**: `energy_post_hoc_comparisons.csv`
- 找到"是否显著"列为"是"的行

### Q3: 不同模型的GPU能耗有显著差异吗？
**查看**: `energy_model_hypothesis_test.csv`

### Q4: 任务和模型有交互效应吗？
**查看**: `07_interaction_heatmap.png`
- 热力图颜色差异大 → 交互效应明显

## 结果解读示例

### 示例输出
```
Kruskal-Wallis检验: H=25.34, p=0.0001 ***
```

**解读**:
- H=25.34: 检验统计量
- p=0.0001: p值（远小于0.05）
- ***: 极显著（p < 0.001）
- **结论**: 不同任务的GPU能耗存在极显著差异

## 常见问题

### 问题1: 提示"任务类型不足"
**原因**: 数据中只有一种任务类型
**解决**: 确保数据包含多种任务（code、creative、qa等）

### 问题2: 提示"样本量不足"
**原因**: 某些任务的样本数太少
**解决**: 收集更多实验数据

### 问题3: 图表中文乱码
**原因**: 系统缺少中文字体
**解决**: 脚本会自动处理，使用英文标签

## 进阶使用

### 自定义分析
```python
from analysis.qe_research.scripts.raw_data_analysis import RawDataAnalyzer

analyzer = RawDataAnalyzer(data_root='data')
analyzer.load_all_raw_data()

# 只运行任务间检验
analyzer._test_energy_across_tasks()

# 只运行模型间检验
analyzer._test_energy_across_models()

# 只运行交互效应分析
analyzer._test_interaction_effects()
```

### 集成到完整分析
```python
# 运行所有分析（包括假设检验）
analyzer.run_all_analyses()
```

## 输出文件清单

| 文件名 | 内容 | 重要性 |
|--------|------|--------|
| energy_task_hypothesis_test.csv | 任务间主检验结果 | ⭐⭐⭐ |
| energy_post_hoc_comparisons.csv | 两两比较结果 | ⭐⭐⭐ |
| energy_by_task_descriptive.csv | 描述性统计 | ⭐⭐ |
| 08_energy_by_task_boxplot.png | 任务箱线图 | ⭐⭐⭐ |
| 07_interaction_heatmap.png | 交互效应图 | ⭐⭐ |
| hypothesis_testing_report.md | 完整报告 | ⭐⭐ |

## 下一步

1. ✅ 运行假设检验
2. 📊 查看箱线图和热力图
3. 📋 阅读CSV结果表格
4. 📝 查看完整报告
5. 🔍 结合领域知识解释结果

## 获取帮助

- **详细指南**: `docs/HYPOTHESIS_TESTING_GUIDE.md`
- **实现总结**: `HYPOTHESIS_TESTING_IMPLEMENTATION.md`
- **日志文件**: `logs/raw_analysis.log`

## 统计显著性速查

| 符号 | p值范围 | 含义 |
|------|---------|------|
| *** | p < 0.001 | 极显著 |
| ** | p < 0.01 | 非常显著 |
| * | p < 0.05 | 显著 |
| ns | p ≥ 0.05 | 不显著 |

## 检查清单

- [ ] 数据已加载（至少10个实验）
- [ ] 包含多种任务类型（≥2种）
- [ ] 包含多个模型（≥2个）
- [ ] scipy已安装
- [ ] 输出目录可写
- [ ] 结果文件已生成

## 快速诊断

```bash
# 检查数据
ls data/*/

# 检查scipy
python -c "import scipy; print(scipy.__version__)"

# 检查输出
ls analysis/qe_research/results/raw_analysis/tables/
```

---

**提示**: 首次运行建议使用测试脚本，确保一切正常后再集成到完整分析流程。
