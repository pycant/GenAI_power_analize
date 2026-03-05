#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成所有学术可视化图表
整合质量评估和性能数据，生成8种标准学术图表

使用方法:
    python generate_all_visualizations.py
    python generate_all_visualizations.py --data-file data/analysis/composite_metrics.csv
    python generate_all_visualizations.py --output-dir data/analize/visualization/figures
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse
import sys

# Import visualization utilities
sys.path.insert(0, str(Path(__file__).parent))
from visualization_utils import (
    setup_academic_style,
    get_academic_colors,
    save_academic_figure,
    get_figure_size,
    SCATTER_CONFIG,
    BAR_CONFIG,
    HEATMAP_CONFIG,
    RADAR_CONFIG,
    FONT_SIZES,
    GRID_CONFIG
)

# ============================================================================
# 图表1: 质量-能耗散点图
# ============================================================================

def plot_quality_vs_energy(df: pd.DataFrame, output_dir: Path):
    """
    Quality vs Energy Scatter Plot
    展示质量和能耗的权衡关系
    """
    print("  📊 Generating: Quality vs Energy scatter plot...")
    
    fig, ax = plt.subplots(figsize=get_figure_size('double_column'))
    
    tasks = df['task_type'].unique()
    colors = get_academic_colors(len(tasks), 'colorblind')
    
    for task, color in zip(tasks, colors):
        task_df = df[df['task_type'] == task]
        ax.scatter(
            task_df['gpu_energy_j'],
            task_df['quality_score'],
            label=task.capitalize(),
            color=color,
            **SCATTER_CONFIG
        )
    
    ax.set_xlabel('GPU Energy Consumption (J)', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Quality Score', fontsize=FONT_SIZES['label'])
    ax.set_title('Quality vs Energy Trade-off Analysis', 
                 fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.legend(loc='best', fontsize=FONT_SIZES['legend'], framealpha=0.8, ncol=2)
    ax.grid(True, **GRID_CONFIG)
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'quality_scatter_energy_vs_quality', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: quality_scatter_energy_vs_quality")


# ============================================================================
# 图表2: 吞吐量-延迟散点图
# ============================================================================

def plot_throughput_vs_latency(df: pd.DataFrame, output_dir: Path):
    """
    Throughput vs Latency Scatter Plot
    展示吞吐量和延迟的关系
    """
    print("  📊 Generating: Throughput vs Latency scatter plot...")
    
    fig, ax = plt.subplots(figsize=get_figure_size('double_column'))
    
    models = df['model'].unique()
    colors = get_academic_colors(len(models), 'colorblind')
    
    for model, color in zip(models, colors):
        model_df = df[df['model'] == model]
        ax.scatter(
            model_df['latency_s'],
            model_df['toks_per_s'],
            label=model,
            color=color,
            **SCATTER_CONFIG
        )
    
    ax.set_xlabel('Latency (seconds)', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Throughput (tokens/s)', fontsize=FONT_SIZES['label'])
    ax.set_title('Throughput vs Latency Trade-off', 
                 fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.legend(loc='best', fontsize=FONT_SIZES['legend'], framealpha=0.8)
    ax.grid(True, **GRID_CONFIG)
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'performance_scatter_throughput_vs_latency', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: performance_scatter_throughput_vs_latency")


# ============================================================================
# 图表3: 质效比柱状图
# ============================================================================

def plot_qe_ratio_comparison(df: pd.DataFrame, output_dir: Path):
    """
    Quality-Efficiency Ratio Bar Chart
    对比各模型在不同任务上的质效比
    """
    print("  📊 Generating: QE Ratio comparison bar chart...")
    
    # Calculate average QE ratio by model and task
    qe_data = df.groupby(['model', 'task_type'])['qe_ratio'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=get_figure_size('double_column'))
    
    tasks = qe_data['task_type'].unique()
    models = qe_data['model'].unique()
    
    x = np.arange(len(tasks))
    width = 0.8 / len(models)
    
    colors = get_academic_colors(len(models), 'colorblind')
    
    for idx, (model, color) in enumerate(zip(models, colors)):
        model_data = qe_data[qe_data['model'] == model]
        values = []
        for task in tasks:
            task_val = model_data[model_data['task_type'] == task]['qe_ratio'].values
            values.append(task_val[0] if len(task_val) > 0 else 0)
        
        offset = (idx - len(models)/2 + 0.5) * width
        ax.bar(x + offset, values, width, label=model, color=color,
               edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Task Type', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Quality-Efficiency Ratio', fontsize=FONT_SIZES['label'])
    ax.set_title('QE Ratio Comparison Across Tasks and Models', 
                 fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([t.capitalize() for t in tasks], rotation=45, ha='right')
    ax.legend(loc='best', fontsize=FONT_SIZES['legend'], framealpha=0.8)
    ax.grid(axis='y', **GRID_CONFIG)
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'efficiency_bar_qe_ratio_comparison', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: efficiency_bar_qe_ratio_comparison")


# ============================================================================
# 图表4: 综合能力雷达图
# ============================================================================

def plot_comprehensive_radar(df: pd.DataFrame, output_dir: Path):
    """
    Comprehensive Capability Radar Chart
    展示Top 5模型的多维能力
    """
    print("  📊 Generating: Comprehensive radar chart...")
    
    # Select top 5 models by QE ratio
    top_models = df.groupby('model')['qe_ratio'].mean().nlargest(5).index
    
    # Calculate normalized scores
    metrics = ['quality_score_norm', 'toks_per_s_norm', 
               'latency_s_norm', 'gpu_energy_j_norm']
    metric_labels = ['Quality', 'Throughput', 'Latency\nOptimization', 'Energy\nEfficiency']
    
    model_scores = df[df['model'].isin(top_models)].groupby('model')[metrics].mean()
    
    # Create radar chart
    n_vars = len(metrics)
    angles = [n / float(n_vars) * 2 * np.pi for n in range(n_vars)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(projection='polar'))
    
    colors = get_academic_colors(len(top_models), 'colorblind')
    
    for idx, (model, row) in enumerate(model_scores.iterrows()):
        values = row.tolist()
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=model, 
                color=colors[idx], markersize=6)
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels, size=FONT_SIZES['label'])
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], size=FONT_SIZES['tick'])
    ax.set_title('Top 5 Models: Comprehensive Capability Analysis', 
                 size=FONT_SIZES['title'], fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=FONT_SIZES['legend'])
    ax.grid(True)
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'comprehensive_radar_top5_models', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: comprehensive_radar_top5_models")


# ============================================================================
# 图表5: 帕累托前沿图
# ============================================================================

def plot_pareto_frontier(df: pd.DataFrame, output_dir: Path):
    """
    Pareto Frontier Analysis
    识别质量-能耗权衡的最优模型
    """
    print("  📊 Generating: Pareto frontier plot...")
    
    fig, ax = plt.subplots(figsize=get_figure_size('double_column'))
    
    # Calculate Pareto frontier
    pareto_mask = np.ones(len(df), dtype=bool)
    
    for i in range(len(df)):
        for j in range(len(df)):
            if i != j:
                # Model j dominates model i if: higher quality AND lower energy
                if (df.iloc[j]['quality_score'] >= df.iloc[i]['quality_score'] and
                    df.iloc[j]['gpu_energy_j'] <= df.iloc[i]['gpu_energy_j'] and
                    (df.iloc[j]['quality_score'] > df.iloc[i]['quality_score'] or
                     df.iloc[j]['gpu_energy_j'] < df.iloc[i]['gpu_energy_j'])):
                    pareto_mask[i] = False
                    break
    
    pareto_df = df[pareto_mask]
    
    # Plot all points
    ax.scatter(
        df['gpu_energy_j'],
        df['quality_score'],
        s=60,
        alpha=0.4,
        color='gray',
        label='All Models',
        edgecolors='black',
        linewidths=0.3
    )
    
    # Highlight Pareto frontier
    ax.scatter(
        pareto_df['gpu_energy_j'],
        pareto_df['quality_score'],
        s=150,
        alpha=0.9,
        color='red',
        marker='*',
        label='Pareto Frontier',
        edgecolors='darkred',
        linewidths=1
    )
    
    # Annotate Pareto frontier models
    for _, row in pareto_df.iterrows():
        ax.annotate(
            row['model'],
            (row['gpu_energy_j'], row['quality_score']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=FONT_SIZES['annotation'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3)
        )
    
    ax.set_xlabel('GPU Energy Consumption (J)', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Quality Score', fontsize=FONT_SIZES['label'])
    ax.set_title('Pareto Frontier: Quality-Energy Trade-off', 
                 fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.legend(loc='best', fontsize=FONT_SIZES['legend'], framealpha=0.8)
    ax.grid(True, **GRID_CONFIG)
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'efficiency_scatter_pareto_frontier', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: efficiency_scatter_pareto_frontier")


# ============================================================================
# 图表6: 模型-任务热力图
# ============================================================================

def plot_model_task_heatmap(df: pd.DataFrame, output_dir: Path):
    """
    Model-Task Performance Heatmap
    展示各模型在不同任务上的质效比
    """
    print("  📊 Generating: Model-Task heatmap...")
    
    # Create pivot table
    pivot_data = df.pivot_table(
        values='qe_ratio',
        index='model',
        columns='task_type',
        aggfunc='mean'
    )
    
    fig, ax = plt.subplots(figsize=get_figure_size('double_column_square'))
    
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt='.3f',
        cmap='RdYlGn',
        ax=ax,
        linewidths=0.5,
        linecolor='gray',
        cbar_kws={'label': 'QE Ratio', 'shrink': 0.8}
    )
    
    ax.set_title('Model-Task QE Ratio Heatmap', 
                 fontsize=FONT_SIZES['title'], fontweight='bold', pad=10)
    ax.set_xlabel('Task Type', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Model', fontsize=FONT_SIZES['label'])
    
    # Capitalize task labels
    ax.set_xticklabels([label.get_text().capitalize() for label in ax.get_xticklabels()],
                       rotation=45, ha='right')
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'efficiency_heatmap_model_task_matrix', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: efficiency_heatmap_model_task_matrix")


# ============================================================================
# 图表7: 公平性分析图
# ============================================================================

def plot_fairness_analysis(df: pd.DataFrame, output_dir: Path):
    """
    Fairness Analysis
    评估模型在不同任务间的公平性
    """
    print("  📊 Generating: Fairness analysis plot...")
    
    # Calculate fairness metrics
    fairness_metrics = {}
    
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        
        # Fairness Gap
        task_means = model_df.groupby('task_type')['quality_score'].mean()
        global_mean = model_df['quality_score'].mean()
        fairness_gap = (task_means - global_mean).abs().max()
        
        # Gini Coefficient
        quality_scores = model_df['quality_score'].sort_values().values
        n = len(quality_scores)
        if n > 0 and quality_scores.sum() > 0:
            gini = (2 * np.sum((np.arange(1, n+1)) * quality_scores)) / (n * quality_scores.sum()) - (n + 1) / n
        else:
            gini = 0
        
        # Coefficient of Variation
        cv = model_df['quality_score'].std() / (model_df['quality_score'].mean() + 1e-6)
        
        # Task quality range
        task_range = task_means.max() - task_means.min()
        
        fairness_metrics[model] = {
            'fairness_gap': fairness_gap,
            'gini_coefficient': gini,
            'cv': cv,
            'task_quality_range': task_range
        }
    
    fairness_df = pd.DataFrame(fairness_metrics).T
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=get_figure_size('double_column_square'))
    
    colors = get_academic_colors(1, 'colorblind')
    
    # 1. Fairness Gap
    ax1 = axes[0, 0]
    fairness_df['fairness_gap'].sort_values().plot(kind='barh', ax=ax1, color=colors[0],
                                                     edgecolor='black', linewidth=0.5)
    ax1.set_title('Fairness Gap', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax1.set_xlabel('Fairness Gap', fontsize=FONT_SIZES['label'])
    ax1.grid(axis='x', **GRID_CONFIG)
    
    # 2. Gini Coefficient
    ax2 = axes[0, 1]
    fairness_df['gini_coefficient'].sort_values().plot(kind='barh', ax=ax2, color=colors[0],
                                                         edgecolor='black', linewidth=0.5)
    ax2.set_title('Gini Coefficient', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax2.set_xlabel('Gini Coefficient', fontsize=FONT_SIZES['label'])
    ax2.grid(axis='x', **GRID_CONFIG)
    
    # 3. Coefficient of Variation
    ax3 = axes[1, 0]
    fairness_df['cv'].sort_values().plot(kind='barh', ax=ax3, color=colors[0],
                                          edgecolor='black', linewidth=0.5)
    ax3.set_title('Coefficient of Variation', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax3.set_xlabel('CV', fontsize=FONT_SIZES['label'])
    ax3.grid(axis='x', **GRID_CONFIG)
    
    # 4. Task Quality Range
    ax4 = axes[1, 1]
    fairness_df['task_quality_range'].sort_values().plot(kind='barh', ax=ax4, color=colors[0],
                                                           edgecolor='black', linewidth=0.5)
    ax4.set_title('Task Quality Range', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax4.set_xlabel('Quality Range', fontsize=FONT_SIZES['label'])
    ax4.grid(axis='x', **GRID_CONFIG)
    
    plt.suptitle('Model Fairness Analysis', fontsize=FONT_SIZES['title']+2, fontweight='bold', y=0.995)
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'quality_bar_fairness_analysis', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: quality_bar_fairness_analysis")


# ============================================================================
# 图表8: 成本效益分析图
# ============================================================================

def plot_cost_benefit_analysis(df: pd.DataFrame, output_dir: Path):
    """
    Cost-Benefit Analysis
    分析成本和质量的关系
    """
    print("  📊 Generating: Cost-benefit analysis plot...")
    
    fig, axes = plt.subplots(1, 2, figsize=get_figure_size('double_column'))
    
    # 1. Cost vs Quality scatter
    ax1 = axes[0]
    models = df['model'].unique()
    colors = get_academic_colors(len(models), 'colorblind')
    
    for model, color in zip(models, colors):
        model_df = df[df['model'] == model]
        if 'cost_total_usd' in model_df.columns:
            ax1.scatter(
                model_df['cost_total_usd'],
                model_df['quality_score'],
                label=model,
                color=color,
                **SCATTER_CONFIG
            )
    
    ax1.set_xlabel('Total Cost (USD)', fontsize=FONT_SIZES['label'])
    ax1.set_ylabel('Quality Score', fontsize=FONT_SIZES['label'])
    ax1.set_title('Cost vs Quality Trade-off', fontsize=FONT_SIZES['title'], fontweight='bold')
    ax1.legend(loc='best', fontsize=FONT_SIZES['legend']-1, framealpha=0.8)
    ax1.grid(True, **GRID_CONFIG)
    
    # 2. CPQ ranking
    ax2 = axes[1]
    if 'cpq' in df.columns:
        cpq_data = df.groupby('model')['cpq'].mean().sort_values(ascending=False)
        cpq_data.plot(kind='bar', ax=ax2, color=colors[0], 
                      edgecolor='black', linewidth=0.5)
        ax2.set_title('Cost Per Quality (CPQ) Ranking', 
                      fontsize=FONT_SIZES['title'], fontweight='bold')
        ax2.set_xlabel('Model', fontsize=FONT_SIZES['label'])
        ax2.set_ylabel('CPQ (Quality/USD)', fontsize=FONT_SIZES['label'])
        ax2.grid(axis='y', **GRID_CONFIG)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'cost_bar_benefit_analysis', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: cost_bar_benefit_analysis")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Generate all academic visualizations')
    parser.add_argument('--data-file', default='data/analysis/composite_metrics.csv',
                        help='Input data file with composite metrics')
    parser.add_argument('--output-dir', default='data/analize/visualization/figures',
                        help='Output directory for figures')
    args = parser.parse_args()
    
    # Setup paths
    data_file = Path(args.data_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("\n" + "="*60)
    print("📊 Generating Academic Visualizations")
    print("="*60 + "\n")
    print(f"Data file: {data_file}")
    print(f"Output directory: {output_dir}\n")
    
    # Check if data file exists
    if not data_file.exists():
        print(f"❌ Error: Data file not found: {data_file}")
        print("\nPlease run comprehensive_analysis.py first to generate the data.")
        sys.exit(1)
    
    # Load data
    print("📂 Loading data...")
    try:
        df = pd.read_csv(data_file, encoding='utf-8')
        print(f"  ✅ Loaded {len(df)} records")
        print(f"     - Models: {df['model'].nunique()}")
        print(f"     - Tasks: {df['task_type'].nunique()}\n")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        sys.exit(1)
    
    # Setup academic style
    setup_academic_style()
    print()
    
    # Generate all visualizations
    print("🎨 Generating visualizations...")
    print("-" * 60)
    
    try:
        plot_quality_vs_energy(df, output_dir)
        plot_throughput_vs_latency(df, output_dir)
        plot_qe_ratio_comparison(df, output_dir)
        plot_comprehensive_radar(df, output_dir)
        plot_pareto_frontier(df, output_dir)
        plot_model_task_heatmap(df, output_dir)
        plot_fairness_analysis(df, output_dir)
        plot_cost_benefit_analysis(df, output_dir)
        
        print("-" * 60)
        print("\n✅ All visualizations generated successfully!")
        print(f"📁 Output directory: {output_dir}")
        print("\nGenerated files:")
        for file in sorted(output_dir.glob('*.pdf')):
            print(f"  - {file.name}")
        
    except Exception as e:
        print(f"\n❌ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
