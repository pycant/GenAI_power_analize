#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学术可视化工具模块
提供符合学术标准的图表配置和绘制函数

使用方法:
    from visualization_utils import setup_academic_style, get_academic_colors, save_academic_figure
    
    setup_academic_style()
    colors = get_academic_colors(5, 'colorblind')
    fig, ax = plt.subplots(figsize=(3.5, 2.625))
    # ... 绘图代码 ...
    save_academic_figure(fig, 'output.pdf', ['pdf', 'png'])
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# ============================================================================
# 配置常量
# ============================================================================

# 图像参数
FIGURE_CONFIG = {
    'dpi': 300,
    'format': 'pdf',
    'format_fallback': 'png',
    'bbox_inches': 'tight',
    'pad_inches': 0.05,
    'transparent': False,
    'facecolor': 'white',
    'edgecolor': 'none'
}

# 图表尺寸 (inches)
FIGURE_SIZES = {
    'single_column': (3.5, 2.625),
    'single_column_tall': (3.5, 4.0),
    'double_column': (7.0, 3.5),
    'double_column_square': (7.0, 5.25),
    'presentation': (10, 6)
}

# 字体大小
FONT_SIZES = {
    'title': 10,
    'label': 9,
    'tick': 8,
    'legend': 8,
    'annotation': 7
}

# 线条和标记
LINE_CONFIG = {
    'linewidth': 1.5,
    'markersize': 6,
    'markeredgewidth': 0.5,
    'alpha': 0.8
}

GRID_CONFIG = {
    'linewidth': 0.5,
    'alpha': 0.3,
    'linestyle': '--'
}

# 颜色方案
ACADEMIC_COLORS = {
    'primary': [
        '#1f77b4',  # Blue
        '#ff7f0e',  # Orange
        '#2ca02c',  # Green
        '#d62728',  # Red
        '#9467bd',  # Purple
        '#8c564b',  # Brown
        '#e377c2',  # Pink
        '#7f7f7f'   # Gray
    ],
    'colorblind': [
        '#0173B2',  # Blue
        '#DE8F05',  # Orange
        '#029E73',  # Green
        '#CC78BC',  # Purple
        '#CA9161',  # Brown
        '#949494',  # Gray
        '#ECE133',  # Yellow
        '#56B4E9'   # Sky Blue
    ]
}

SEMANTIC_COLORS = {
    'excellent': '#2ca02c',
    'good': '#1f77b4',
    'average': '#ff7f0e',
    'poor': '#d62728',
    'baseline': '#7f7f7f',
    'highlight': '#e377c2'
}

# 图表配置
SCATTER_CONFIG = {
    's': 80,
    'alpha': 0.7,
    'edgecolors': 'black',
    'linewidths': 0.5
}

BAR_CONFIG = {
    'width': 0.8,
    'edgecolor': 'black',
    'linewidth': 0.5,
    'error_kw': {
        'linewidth': 1,
        'capsize': 3,
        'capthick': 1
    }
}

HEATMAP_CONFIG = {
    'cmap': 'RdYlGn',
    'annot': True,
    'fmt': '.3f',
    'linewidths': 0.5,
    'linecolor': 'gray',
    'cbar_kws': {
        'label': 'Score',
        'shrink': 0.8
    }
}

RADAR_CONFIG = {
    'linewidth': 2,
    'alpha': 0.25,
    'marker': 'o',
    'markersize': 6
}

BOX_CONFIG = {
    'widths': 0.6,
    'patch_artist': True,
    'showmeans': True,
    'meanline': True,
    'flierprops': {
        'marker': 'o',
        'markersize': 4,
        'alpha': 0.5
    }
}

# ============================================================================
# 核心函数
# ============================================================================

def setup_academic_style():
    """设置学术风格"""
    
    plt.rcParams.update({
        # Image quality
        'figure.dpi': 100,
        'savefig.dpi': 300,
        'savefig.format': 'pdf',
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
        
        # Fonts
        'font.family': 'sans-serif',
        'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
        'font.size': 9,
        
        # Axes
        'axes.labelsize': 9,
        'axes.titlesize': 10,
        'axes.linewidth': 0.8,
        'axes.grid': True,
        'axes.axisbelow': True,
        
        # Ticks
        'xtick.labelsize': 8,
        'ytick.labelsize': 8,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        
        # Legend
        'legend.fontsize': 8,
        'legend.frameon': True,
        'legend.framealpha': 0.8,
        'legend.edgecolor': 'gray',
        
        # Grid
        'grid.linewidth': 0.5,
        'grid.alpha': 0.3,
        'grid.linestyle': '--',
        
        # Lines
        'lines.linewidth': 1.5,
        'lines.markersize': 6,
        
        # Other
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'savefig.facecolor': 'white'
    })
    
    # Set seaborn style
    sns.set_style("whitegrid", {
        'grid.linestyle': '--',
        'grid.alpha': 0.3
    })
    
    print("✅ Academic style configured")


def get_academic_colors(n_colors: Optional[int] = None, palette: str = 'primary') -> List[str]:
    """
    获取学术配色
    
    Args:
        n_colors: 需要的颜色数量，None表示返回全部
        palette: 配色方案 ('primary' 或 'colorblind')
    
    Returns:
        颜色列表
    """
    colors = ACADEMIC_COLORS.get(palette, ACADEMIC_COLORS['primary'])
    
    if n_colors is None:
        return colors
    elif n_colors <= len(colors):
        return colors[:n_colors]
    else:
        # Use seaborn to generate more colors
        return sns.color_palette('husl', n_colors).as_hex()


def save_academic_figure(
    fig,
    filename: str,
    formats: List[str] = ['pdf', 'png'],
    dpi: int = 300
):
    """
    保存学术图表
    
    Args:
        fig: matplotlib figure对象
        filename: 输出文件名（不含扩展名或含任意扩展名）
        formats: 输出格式列表
        dpi: 分辨率
    """
    # Remove extension from filename
    base_filename = str(filename)
    for ext in ['.pdf', '.png', '.svg', '.jpg']:
        if base_filename.endswith(ext):
            base_filename = base_filename[:-len(ext)]
            break
    
    for fmt in formats:
        output_file = f"{base_filename}.{fmt}"
        fig.savefig(
            output_file,
            format=fmt,
            dpi=dpi,
            bbox_inches='tight',
            pad_inches=0.05,
            facecolor='white',
            edgecolor='none'
        )
        print(f"  ✅ Saved: {output_file}")


def get_figure_size(size_name: str = 'double_column') -> Tuple[float, float]:
    """
    获取标准图表尺寸
    
    Args:
        size_name: 尺寸名称
    
    Returns:
        (width, height) in inches
    """
    return FIGURE_SIZES.get(size_name, FIGURE_SIZES['double_column'])


# ============================================================================
# 专用绘图函数
# ============================================================================

def create_scatter_plot(
    x_data,
    y_data,
    labels=None,
    colors=None,
    xlabel: str = 'X Axis',
    ylabel: str = 'Y Axis',
    title: str = 'Scatter Plot',
    figsize: Tuple[float, float] = None,
    **kwargs
):
    """
    创建学术风格散点图
    
    Args:
        x_data: X轴数据（可以是单个数组或数组列表）
        y_data: Y轴数据（可以是单个数组或数组列表）
        labels: 数据标签列表
        colors: 颜色列表
        xlabel: X轴标签
        ylabel: Y轴标签
        title: 图表标题
        figsize: 图表尺寸
        **kwargs: 传递给scatter的额外参数
    
    Returns:
        fig, ax
    """
    if figsize is None:
        figsize = get_figure_size('double_column')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Handle single or multiple datasets
    if not isinstance(x_data, list):
        x_data = [x_data]
        y_data = [y_data]
    
    n_datasets = len(x_data)
    
    if colors is None:
        colors = get_academic_colors(n_datasets, 'colorblind')
    
    if labels is None:
        labels = [f'Dataset {i+1}' for i in range(n_datasets)]
    
    # Plot each dataset
    scatter_params = {**SCATTER_CONFIG, **kwargs}
    
    for i, (x, y) in enumerate(zip(x_data, y_data)):
        ax.scatter(x, y, label=labels[i], color=colors[i], **scatter_params)
    
    ax.set_xlabel(xlabel, fontsize=FONT_SIZES['label'])
    ax.set_ylabel(ylabel, fontsize=FONT_SIZES['label'])
    ax.set_title(title, fontsize=FONT_SIZES['title'], fontweight='bold')
    
    if len(labels) > 1:
        ax.legend(loc='best', fontsize=FONT_SIZES['legend'], framealpha=0.8)
    
    ax.grid(True, **GRID_CONFIG)
    
    plt.tight_layout()
    
    return fig, ax


def create_bar_plot(
    categories,
    values,
    labels=None,
    colors=None,
    xlabel: str = 'Category',
    ylabel: str = 'Value',
    title: str = 'Bar Plot',
    figsize: Tuple[float, float] = None,
    **kwargs
):
    """
    创建学术风格柱状图
    
    Args:
        categories: 类别列表
        values: 值（可以是单个数组或数组列表，用于分组柱状图）
        labels: 数据标签列表
        colors: 颜色列表
        xlabel: X轴标签
        ylabel: Y轴标签
        title: 图表标题
        figsize: 图表尺寸
        **kwargs: 传递给bar的额外参数
    
    Returns:
        fig, ax
    """
    if figsize is None:
        figsize = get_figure_size('double_column')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Handle single or multiple datasets
    if not isinstance(values[0], (list, np.ndarray)):
        values = [values]
    
    n_groups = len(values)
    
    if colors is None:
        colors = get_academic_colors(n_groups, 'colorblind')
    
    if labels is None:
        labels = [f'Group {i+1}' for i in range(n_groups)]
    
    # Calculate bar positions
    x = np.arange(len(categories))
    width = BAR_CONFIG['width'] / n_groups
    
    bar_params = {k: v for k, v in BAR_CONFIG.items() if k != 'width'}
    bar_params.update(kwargs)
    
    # Plot bars
    for i, (vals, label, color) in enumerate(zip(values, labels, colors)):
        offset = (i - n_groups/2 + 0.5) * width
        ax.bar(x + offset, vals, width, label=label, color=color, **bar_params)
    
    ax.set_xlabel(xlabel, fontsize=FONT_SIZES['label'])
    ax.set_ylabel(ylabel, fontsize=FONT_SIZES['label'])
    ax.set_title(title, fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha='right')
    
    if n_groups > 1:
        ax.legend(loc='best', fontsize=FONT_SIZES['legend'], framealpha=0.8)
    
    ax.grid(axis='y', **GRID_CONFIG)
    
    plt.tight_layout()
    
    return fig, ax


def create_heatmap(
    data,
    row_labels,
    col_labels,
    title: str = 'Heatmap',
    cmap: str = 'RdYlGn',
    cbar_label: str = 'Score',
    figsize: Tuple[float, float] = None,
    **kwargs
):
    """
    创建学术风格热力图
    
    Args:
        data: 2D数组数据
        row_labels: 行标签
        col_labels: 列标签
        title: 图表标题
        cmap: 颜色映射
        cbar_label: 颜色条标签
        figsize: 图表尺寸
        **kwargs: 传递给heatmap的额外参数
    
    Returns:
        fig, ax
    """
    if figsize is None:
        figsize = get_figure_size('double_column_square')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    heatmap_params = {**HEATMAP_CONFIG, **kwargs}
    heatmap_params['cmap'] = cmap
    heatmap_params['cbar_kws'] = {'label': cbar_label, 'shrink': 0.8}
    
    sns.heatmap(
        data,
        xticklabels=col_labels,
        yticklabels=row_labels,
        ax=ax,
        **heatmap_params
    )
    
    ax.set_title(title, fontsize=FONT_SIZES['title'], fontweight='bold', pad=10)
    
    plt.tight_layout()
    
    return fig, ax


def create_radar_chart(
    categories,
    values,
    labels=None,
    colors=None,
    title: str = 'Radar Chart',
    figsize: Tuple[float, float] = None,
    **kwargs
):
    """
    创建学术风格雷达图
    
    Args:
        categories: 维度标签列表
        values: 值（可以是单个数组或数组列表）
        labels: 数据标签列表
        colors: 颜色列表
        title: 图表标题
        figsize: 图表尺寸
        **kwargs: 额外参数
    
    Returns:
        fig, ax
    """
    if figsize is None:
        figsize = (7, 7)
    
    # Handle single or multiple datasets
    if not isinstance(values[0], (list, np.ndarray)):
        values = [values]
    
    n_datasets = len(values)
    n_vars = len(categories)
    
    if colors is None:
        colors = get_academic_colors(n_datasets, 'colorblind')
    
    if labels is None:
        labels = [f'Model {i+1}' for i in range(n_datasets)]
    
    # Compute angle for each axis
    angles = [n / float(n_vars) * 2 * np.pi for n in range(n_vars)]
    angles += angles[:1]
    
    # Create plot
    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(projection='polar'))
    
    radar_params = {**RADAR_CONFIG, **kwargs}
    
    # Plot each dataset
    for i, (vals, label, color) in enumerate(zip(values, labels, colors)):
        vals_plot = list(vals) + [vals[0]]
        ax.plot(angles, vals_plot, 'o-', label=label, color=color, 
                linewidth=radar_params['linewidth'],
                markersize=radar_params['markersize'])
        ax.fill(angles, vals_plot, alpha=radar_params['alpha'], color=color)
    
    # Set category labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=FONT_SIZES['label'])
    
    # Set y-axis
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=FONT_SIZES['tick'])
    
    # Title and legend
    ax.set_title(title, size=FONT_SIZES['title'], fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=FONT_SIZES['legend'])
    
    ax.grid(True)
    
    plt.tight_layout()
    
    return fig, ax


# ============================================================================
# 测试函数
# ============================================================================

def test_visualization_utils():
    """测试可视化工具"""
    print("\n" + "="*60)
    print("Testing Visualization Utils")
    print("="*60 + "\n")
    
    # Setup style
    setup_academic_style()
    
    # Test scatter plot
    print("Creating scatter plot...")
    x = np.random.rand(50)
    y = np.random.rand(50)
    fig, ax = create_scatter_plot(
        x, y,
        xlabel='Energy (J)',
        ylabel='Quality Score',
        title='Test Scatter Plot'
    )
    save_academic_figure(fig, 'test_scatter', ['png'])
    plt.close()
    
    # Test bar plot
    print("Creating bar plot...")
    categories = ['Model A', 'Model B', 'Model C']
    values = [0.8, 0.6, 0.9]
    fig, ax = create_bar_plot(
        categories, values,
        xlabel='Model',
        ylabel='Score',
        title='Test Bar Plot'
    )
    save_academic_figure(fig, 'test_bar', ['png'])
    plt.close()
    
    # Test radar chart
    print("Creating radar chart...")
    categories = ['Quality', 'Efficiency', 'Speed', 'Cost']
    values = [0.8, 0.6, 0.7, 0.9]
    fig, ax = create_radar_chart(
        categories, values,
        title='Test Radar Chart'
    )
    save_academic_figure(fig, 'test_radar', ['png'])
    plt.close()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    test_visualization_utils()
