# 学术可视化风格指南

**版本**: 1.0  
**创建时间**: 2026-03-05  
**适用范围**: 所有学术论文图表

---

## 📋 目录

1. [核心原则](#核心原则)
2. [技术规范](#技术规范)
3. [颜色方案](#颜色方案)
4. [字体规范](#字体规范)
5. [图表类型规范](#图表类型规范)
6. [文件命名规范](#文件命名规范)
7. [实现代码](#实现代码)

---

## 1. 核心原则

### 1.1 学术标准

- ✅ **纯英文**: 所有文本（标题、标签、图例）必须使用英文
- ✅ **高分辨率**: 300 DPI 或更高，适合印刷
- ✅ **矢量优先**: 优先使用 PDF/SVG 格式，PNG 作为备选
- ✅ **色盲友好**: 使用色盲可区分的颜色方案
- ✅ **黑白可读**: 图表在黑白打印时仍可区分
- ✅ **简洁清晰**: 避免过度装饰，突出数据本身

### 1.2 期刊要求

参考主流 AI/ML 期刊标准：
- **NeurIPS/ICML/ICLR**: 单栏宽度 3.25 inches, 双栏宽度 6.75 inches
- **ACL/EMNLP**: 单栏宽度 3.33 inches, 双栏宽度 6.83 inches
- **IEEE**: 单栏宽度 3.5 inches, 双栏宽度 7.16 inches

---

## 2. 技术规范

### 2.1 图像参数

```python
# 标准配置
FIGURE_CONFIG = {
    'dpi': 300,                    # 分辨率 (印刷标准)
    'format': 'pdf',               # 主格式 (矢量)
    'format_fallback': 'png',      # 备选格式 (位图)
    'bbox_inches': 'tight',        # 紧凑边界
    'pad_inches': 0.05,            # 边距
    'transparent': False,          # 不透明背景
    'facecolor': 'white',          # 白色背景
    'edgecolor': 'none'            # 无边框
}

# 图表尺寸 (inches)
FIGURE_SIZES = {
    'single_column': (3.5, 2.625),      # 单栏 (4:3 比例)
    'single_column_tall': (3.5, 4.0),   # 单栏高图
    'double_column': (7.0, 3.5),        # 双栏 (2:1 比例)
    'double_column_square': (7.0, 5.25) # 双栏方图 (4:3 比例)
}
```

### 2.2 字体大小

```python
FONT_SIZES = {
    'title': 10,           # 图表标题
    'label': 9,            # 坐标轴标签
    'tick': 8,             # 刻度标签
    'legend': 8,           # 图例
    'annotation': 7        # 注释文字
}
```

### 2.3 线条和标记

```python
LINE_CONFIG = {
    'linewidth': 1.5,      # 线条宽度
    'markersize': 6,       # 标记大小
    'markeredgewidth': 0.5,# 标记边框宽度
    'alpha': 0.8           # 透明度
}

GRID_CONFIG = {
    'linewidth': 0.5,      # 网格线宽度
    'alpha': 0.3,          # 网格透明度
    'linestyle': '--'      # 网格线样式
}
```

---

## 3. 颜色方案

### 3.1 主色板 (色盲友好)

基于 **ColorBrewer** 和 **Tableau** 的学术配色：

```python
# 主色板 (最多8种颜色)
ACADEMIC_COLORS = {
    'primary': [
        '#1f77b4',  # 蓝色 - 主要数据
        '#ff7f0e',  # 橙色 - 次要数据
        '#2ca02c',  # 绿色 - 正向指标
        '#d62728',  # 红色 - 负向指标/警告
        '#9467bd',  # 紫色 - 特殊类别
        '#8c564b',  # 棕色 - 辅助数据
        '#e377c2',  # 粉色 - 对比数据
        '#7f7f7f'   # 灰色 - 基线/参考
    ],
    
    # 色盲友好配色 (Okabe-Ito)
    'colorblind_safe': [
        '#0173B2',  # 蓝色
        '#DE8F05',  # 橙色
        '#029E73',  # 绿色
        '#CC78BC',  # 紫色
        '#CA9161',  # 棕色
        '#949494',  # 灰色
        '#ECE133',  # 黄色
        '#56B4E9'   # 天蓝色
    ],
    
    # 渐变色 (用于热力图)
    'sequential': 'RdYlGn',     # 红-黄-绿 (质量评分)
    'diverging': 'RdBu_r',      # 红-蓝 (正负对比)
    'heatmap': 'viridis'        # 紫-绿-黄 (通用热力图)
}
```

### 3.2 语义颜色

```python
SEMANTIC_COLORS = {
    'excellent': '#2ca02c',     # 优秀 - 绿色
    'good': '#1f77b4',          # 良好 - 蓝色
    'average': '#ff7f0e',       # 一般 - 橙色
    'poor': '#d62728',          # 较差 - 红色
    'baseline': '#7f7f7f',      # 基线 - 灰色
    'highlight': '#e377c2'      # 高亮 - 粉色
}
```

### 3.3 黑白模式

```python
GRAYSCALE_PATTERNS = {
    'solid': {'facecolor': '#000000', 'edgecolor': 'black', 'linewidth': 0},
    'light': {'facecolor': '#CCCCCC', 'edgecolor': 'black', 'linewidth': 0.5},
    'medium': {'facecolor': '#888888', 'edgecolor': 'black', 'linewidth': 0.5},
    'dark': {'facecolor': '#444444', 'edgecolor': 'black', 'linewidth': 0.5},
    'hatched': {'facecolor': 'white', 'edgecolor': 'black', 'hatch': '///', 'linewidth': 0.5}
}
```

---

## 4. 字体规范

### 4.1 字体选择

```python
FONT_CONFIG = {
    # 优先级顺序
    'serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif'],
    'monospace': ['Courier New', 'DejaVu Sans Mono', 'monospace']
}

# 推荐配置
RECOMMENDED_FONT = {
    'family': 'sans-serif',           # 无衬线字体（更清晰）
    'sans-serif': ['Arial', 'Helvetica'],
    'size': 9,                        # 基础字号
    'weight': 'normal'                # 正常粗细
}
```

### 4.2 数学符号

```python
# 启用 LaTeX 渲染（可选）
plt.rcParams['text.usetex'] = False  # 默认关闭，避免依赖问题
plt.rcParams['mathtext.fontset'] = 'dejavusans'  # 数学字体
```

---

## 5. 图表类型规范

### 5.1 散点图 (Scatter Plot)

**用途**: 质量-能耗关系、吞吐量-延迟关系

```python
SCATTER_CONFIG = {
    's': 80,                    # 点大小
    'alpha': 0.7,               # 透明度
    'edgecolors': 'black',      # 边框颜色
    'linewidths': 0.5           # 边框宽度
}
```

**示例**:
- X轴: Energy Consumption (J)
- Y轴: Quality Score
- 颜色: Task Type
- 标记: Model Category

### 5.2 柱状图 (Bar Chart)

**用途**: 模型对比、任务性能对比

```python
BAR_CONFIG = {
    'width': 0.8,               # 柱宽
    'edgecolor': 'black',       # 边框
    'linewidth': 0.5,           # 边框宽度
    'error_kw': {               # 误差线
        'linewidth': 1,
        'capsize': 3,
        'capthick': 1
    }
}
```

**示例**:
- X轴: Model Name
- Y轴: Quality-Efficiency Ratio
- 颜色: 按模型类别区分
- 误差线: 标准差

### 5.3 热力图 (Heatmap)

**用途**: 模型-任务性能矩阵

```python
HEATMAP_CONFIG = {
    'cmap': 'RdYlGn',           # 颜色映射
    'annot': True,              # 显示数值
    'fmt': '.3f',               # 数值格式
    'linewidths': 0.5,          # 网格线宽
    'linecolor': 'gray',        # 网格线颜色
    'cbar_kws': {               # 颜色条
        'label': 'Score',
        'shrink': 0.8
    }
}
```

### 5.4 雷达图 (Radar Chart)

**用途**: 多维能力对比

```python
RADAR_CONFIG = {
    'linewidth': 2,             # 线宽
    'alpha': 0.25,              # 填充透明度
    'marker': 'o',              # 标记样式
    'markersize': 6             # 标记大小
}
```

### 5.5 箱线图 (Box Plot)

**用途**: 稳定性分析、分布对比

```python
BOX_CONFIG = {
    'widths': 0.6,              # 箱体宽度
    'patch_artist': True,       # 填充颜色
    'showmeans': True,          # 显示均值
    'meanline': True,           # 均值线
    'flierprops': {             # 异常值
        'marker': 'o',
        'markersize': 4,
        'alpha': 0.5
    }
}
```

---

## 6. 文件命名规范

### 6.1 命名格式

```
{category}_{type}_{description}.{format}

示例:
- quality_scatter_energy_vs_quality.pdf
- performance_bar_model_comparison.pdf
- efficiency_heatmap_model_task_matrix.pdf
- comprehensive_radar_top5_models.pdf
```

### 6.2 类别代码

```python
CATEGORY_CODES = {
    'quality': 'qual',          # 质量相关
    'performance': 'perf',      # 性能相关
    'efficiency': 'effi',       # 效率相关
    'cost': 'cost',             # 成本相关
    'comprehensive': 'comp'     # 综合分析
}

TYPE_CODES = {
    'scatter': 'scat',          # 散点图
    'bar': 'bar',               # 柱状图
    'line': 'line',             # 折线图
    'heatmap': 'heat',          # 热力图
    'radar': 'radar',           # 雷达图
    'box': 'box',               # 箱线图
    'violin': 'viol'            # 小提琴图
}
```

---

## 7. 实现代码

### 7.1 配置初始化

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def setup_academic_style():
    """设置学术风格"""
    
    # 基础配置
    plt.rcParams.update({
        # 图像质量
        'figure.dpi': 100,              # 屏幕显示DPI
        'savefig.dpi': 300,             # 保存DPI
        'savefig.format': 'pdf',        # 默认格式
        'savefig.bbox': 'tight',        # 紧凑边界
        'savefig.pad_inches': 0.05,     # 边距
        
        # 字体
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 9,
        
        # 坐标轴
        'axes.labelsize': 9,
        'axes.titlesize': 10,
        'axes.linewidth': 0.8,
        'axes.grid': True,
        'axes.axisbelow': True,
        
        # 刻度
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        
        # 图例
        'legend.fontsize': 8,
        'legend.frameon': True,
        'legend.framealpha': 0.8,
        'legend.edgecolor': 'gray',
        
        # 网格
        'grid.linewidth': 0.5,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        
        # 线条
        'lines.linewidth': 1.5,
        'lines.markersize': 6,
        
        # 其他
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'savefig.facecolor': 'white'
    })
    
    # 设置 seaborn 样式
    sns.set_style("whitegrid", {
        'grid.linestyle': '--',
        'grid.alpha': 0.3
    })
    
    print("✅ Academic style configured")
```

### 7.2 颜色获取函数

```python
def get_academic_colors(n_colors=None, palette='primary'):
    """获取学术配色"""
    
    palettes = {
        'primary': [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
            '#9467bd', '#8c564b', '#e377c2', '#7f7f7f'
        ],
        'colorblind': [
            '#0173B2', '#DE8F05', '#029E73', '#CC78BC',
            '#CA9161', '#949494', '#ECE133', '#56B4E9'
        ]
    }
    
    colors = palettes.get(palette, palettes['primary'])
    
    if n_colors is None:
        return colors
    elif n_colors <= len(colors):
        return colors[:n_colors]
    else:
        # 使用 seaborn 生成更多颜色
        return sns.color_palette('husl', n_colors)
```

### 7.3 保存函数

```python
def save_academic_figure(fig, filename, formats=['pdf', 'png']):
    """保存学术图表"""
    
    for fmt in formats:
        output_file = filename.replace('.pdf', f'.{fmt}').replace('.png', f'.{fmt}')
        fig.savefig(
            output_file,
            format=fmt,
            dpi=300,
            bbox_inches='tight',
            pad_inches=0.05,
            facecolor='white',
            edgecolor='none'
        )
        print(f"  ✅ Saved: {output_file}")
```

---

## 8. 使用示例

### 8.1 完整示例

```python
import matplotlib.pyplot as plt
import numpy as np

# 初始化学术风格
setup_academic_style()

# 创建图表
fig, ax = plt.subplots(figsize=(3.5, 2.625))  # 单栏尺寸

# 生成示例数据
x = np.linspace(0, 10, 50)
y1 = np.sin(x)
y2 = np.cos(x)

# 绘制数据
colors = get_academic_colors(2, 'colorblind')
ax.plot(x, y1, label='Model A', color=colors[0], linewidth=1.5)
ax.plot(x, y2, label='Model B', color=colors[1], linewidth=1.5)

# 设置标签（纯英文）
ax.set_xlabel('Energy Consumption (J)', fontsize=9)
ax.set_ylabel('Quality Score', fontsize=9)
ax.set_title('Quality vs Energy Trade-off', fontsize=10, fontweight='bold')

# 图例
ax.legend(loc='best', fontsize=8, framealpha=0.8)

# 网格
ax.grid(True, linestyle='--', alpha=0.3, linewidth=0.5)

# 保存
save_academic_figure(fig, 'quality_scatter_energy_vs_quality.pdf', ['pdf', 'png'])
plt.close()
```

---

## 9. 检查清单

在提交论文前，确保所有图表符合以下标准：

- [ ] 所有文本使用英文
- [ ] 分辨率 ≥ 300 DPI
- [ ] 提供 PDF 矢量格式
- [ ] 字体大小适中（标题10pt，标签9pt，刻度8pt）
- [ ] 颜色色盲友好
- [ ] 黑白打印可读
- [ ] 图例清晰完整
- [ ] 坐标轴标签包含单位
- [ ] 文件命名规范
- [ ] 图表尺寸符合期刊要求

---

## 10. 参考资源

- **ColorBrewer**: https://colorbrewer2.org/
- **Matplotlib 学术风格**: https://matplotlib.org/stable/gallery/style_sheets/
- **Nature 图表指南**: https://www.nature.com/nature/for-authors/final-submission
- **IEEE 图表标准**: https://www.ieee.org/publications/authors/

---

**版本历史**:
- v1.0 (2026-03-05): 初始版本，定义核心规范

**维护者**: AI Assistant  
**最后更新**: 2026-03-05
