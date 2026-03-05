# 可视化系统快速指南

**版本**: 1.0  
**创建时间**: 2026-03-05  
**目标**: 快速生成符合学术标准的可视化图表

---

## 快速开始

### 1. 生成所有图表（一键运行）

```bash
# 激活环境
conda activate bartscore

# 设置编码
set PYTHONUTF8=1

# 生成所有图表
cd data/analize/visualization/scripts
python generate_all_visualizations.py
```

### 2. 自定义数据源

```bash
python generate_all_visualizations.py \
    --data-file path/to/your/data.csv \
    --output-dir path/to/output
```

---

## 输出图表

生成的8种学术图表：

1. **quality_scatter_energy_vs_quality.pdf** - 质量-能耗散点图
2. **performance_scatter_throughput_vs_latency.pdf** - 吞吐量-延迟散点图
3. **efficiency_bar_qe_ratio_comparison.pdf** - 质效比柱状图
4. **comprehensive_radar_top5_models.pdf** - 综合能力雷达图
5. **efficiency_scatter_pareto_frontier.pdf** - 帕累托前沿图
6. **efficiency_heatmap_model_task_matrix.pdf** - 模型-任务热力图
7. **quality_bar_fairness_analysis.pdf** - 公平性分析图
8. **cost_bar_benefit_analysis.pdf** - 成本效益分析图

每个图表同时生成 PDF（矢量）和 PNG（位图）两种格式。

---

## 使用可视化工具库

### 基础使用

```python
from visualization_utils import (
    setup_academic_style,
    get_academic_colors,
    save_academic_figure
)

# 初始化学术风格
setup_academic_style()

# 获取配色
colors = get_academic_colors(5, 'colorblind')

# 创建图表
fig, ax = plt.subplots(figsize=(7, 3.5))
# ... 绘图代码 ...

# 保存图表
save_academic_figure(fig, 'my_figure', ['pdf', 'png'])
```


### 创建散点图

```python
from visualization_utils import create_scatter_plot

fig, ax = create_scatter_plot(
    x_data=[x1, x2],
    y_data=[y1, y2],
    labels=['Model A', 'Model B'],
    xlabel='Energy (J)',
    ylabel='Quality Score',
    title='Quality vs Energy'
)
save_academic_figure(fig, 'scatter_plot', ['pdf', 'png'])
```

### 创建柱状图

```python
from visualization_utils import create_bar_plot

fig, ax = create_bar_plot(
    categories=['Model A', 'Model B', 'Model C'],
    values=[0.8, 0.6, 0.9],
    xlabel='Model',
    ylabel='Score',
    title='Model Comparison'
)
save_academic_figure(fig, 'bar_plot', ['pdf', 'png'])
```

### 创建雷达图

```python
from visualization_utils import create_radar_chart

fig, ax = create_radar_chart(
    categories=['Quality', 'Speed', 'Efficiency', 'Cost'],
    values=[[0.8, 0.6, 0.7, 0.9], [0.7, 0.8, 0.6, 0.8]],
    labels=['Model A', 'Model B'],
    title='Comprehensive Comparison'
)
save_academic_figure(fig, 'radar_chart', ['pdf', 'png'])
```

---

## 学术标准检查清单

提交论文前，确保所有图表符合：

- [x] 所有文本使用英文
- [x] 分辨率 300 DPI
- [x] 提供 PDF 矢量格式
- [x] 字体大小适中（标题10pt，标签9pt）
- [x] 色盲友好配色
- [x] 黑白打印可读
- [x] 图例清晰完整
- [x] 坐标轴标签包含单位

---

## 常见问题

### Q: 如何修改图表尺寸？

```python
from visualization_utils import get_figure_size

# 使用预定义尺寸
figsize = get_figure_size('double_column')  # (7.0, 3.5)

# 或自定义尺寸
figsize = (8, 6)

fig, ax = plt.subplots(figsize=figsize)
```

### Q: 如何使用不同的配色方案？

```python
# 色盲友好配色
colors = get_academic_colors(5, 'colorblind')

# 主配色
colors = get_academic_colors(5, 'primary')
```

### Q: 如何调整字体大小？

```python
from visualization_utils import FONT_SIZES

# 使用标准字号
ax.set_xlabel('Label', fontsize=FONT_SIZES['label'])  # 9pt
ax.set_title('Title', fontsize=FONT_SIZES['title'])   # 10pt

# 或自定义
ax.set_xlabel('Label', fontsize=11)
```

---

## 文件结构

```
data/analize/visualization/
├── scripts/
│   ├── visualization_utils.py           # 工具库
│   └── generate_all_visualizations.py   # 主脚本
├── figures/                              # 输出图表
│   ├── *.pdf                            # 矢量格式
│   └── *.png                            # 位图格式
├── ACADEMIC_VISUALIZATION_STYLE_GUIDE.md # 完整风格指南
└── VISUALIZATION_QUICK_GUIDE.md          # 本文档
```

---

## 参考文档

- 完整风格指南: `ACADEMIC_VISUALIZATION_STYLE_GUIDE.md`
- 综合分析设计: `docs/analysis/comprehensive_analysis_design.md`
- 工具库源码: `scripts/visualization_utils.py`

---

**维护者**: AI Assistant  
**最后更新**: 2026-03-05
