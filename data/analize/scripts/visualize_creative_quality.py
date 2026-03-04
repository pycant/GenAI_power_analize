"""
创意写作质量评估可视化脚本

生成多维度对比图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
from math import pi

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def plot_diversity_comparison(df: pd.DataFrame, output_dir: Path):
    """绘制多样性对比柱状图"""
    
    print("📊 Generating diversity comparison chart...")
    
    # 按模型汇总
    model_diversity = df.groupby('model')[['distinct_1', 'distinct_2', 'distinct_3']].mean()
    model_diversity = model_diversity.sort_values('distinct_2', ascending=False)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(model_diversity))
    width = 0.25
    
    bars1 = ax.bar(x - width, model_diversity['distinct_1'], width, label='Distinct-1', alpha=0.8)
    bars2 = ax.bar(x, model_diversity['distinct_2'], width, label='Distinct-2', alpha=0.8)
    bars3 = ax.bar(x + width, model_diversity['distinct_3'], width, label='Distinct-3', alpha=0.8)
    
    ax.set_xlabel('Model', fontsize=12)
    ax.set_ylabel('Diversity Score', fontsize=12)
    ax.set_title('Creative Writing Diversity Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(model_diversity.index, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 1.1)
    
    # 添加数值标签
    for bars in [bars1, bars2, bars3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=7)
    
    plt.tight_layout()
    output_file = output_dir / 'creative_diversity_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file}")


def plot_diversity_heatmap(df: pd.DataFrame, output_dir: Path):
    """绘制多样性热力图"""
    
    print("📊 Generating diversity heatmap...")
    
    # 创建透视表
    pivot_data = df.pivot_table(
        values='distinct_2',
        index='model',
        columns='question_id',
        aggfunc='mean'
    )
    
    # 按平均值排序
    pivot_data = pivot_data.loc[pivot_data.mean(axis=1).sort_values(ascending=False).index]
    
    fig, ax = plt.subplots(figsize=(10, 12))
    
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlGnBu',
                cbar_kws={'label': 'Distinct-2 Score'},
                linewidths=0.5, ax=ax)
    
    ax.set_title('Distinct-2 Scores by Model and Question', fontsize=14, fontweight='bold')
    ax.set_xlabel('Question ID', fontsize=12)
    ax.set_ylabel('Model', fontsize=12)
    
    plt.tight_layout()
    output_file = output_dir / 'creative_diversity_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file}")


def plot_radar_chart(df: pd.DataFrame, output_dir: Path):
    """绘制雷达图（Top 5模型）"""
    
    print("📊 Generating radar chart...")
    
    # 选择Top 5模型
    top_models = df.groupby('model')['distinct_2'].mean().nlargest(5).index.tolist()
    
    # 准备数据
    categories = ['Distinct-1', 'Distinct-2', 'Distinct-3']
    N = len(categories)
    
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(top_models)))
    
    for idx, model in enumerate(top_models):
        model_data = df[df['model'] == model]
        values = [
            model_data['distinct_1'].mean(),
            model_data['distinct_2'].mean(),
            model_data['distinct_3'].mean()
        ]
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_title('Creative Writing Quality Radar Chart (Top 5 Models)', 
                 size=14, fontweight='bold', y=1.08)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    ax.grid(True)
    
    plt.tight_layout()
    output_file = output_dir / 'creative_radar_chart.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file}")


def plot_distribution_violin(df: pd.DataFrame, output_dir: Path):
    """绘制分布小提琴图"""
    
    print("📊 Generating distribution violin plot...")
    
    # 选择Top 8模型
    top_models = df.groupby('model')['distinct_2'].mean().nlargest(8).index.tolist()
    df_top = df[df['model'].isin(top_models)]
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    metrics = ['distinct_1', 'distinct_2', 'distinct_3']
    titles = ['Distinct-1 Distribution', 'Distinct-2 Distribution', 'Distinct-3 Distribution']
    
    for ax, metric, title in zip(axes, metrics, titles):
        sns.violinplot(data=df_top, y='model', x=metric, ax=ax, orient='h')
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Score', fontsize=11)
        ax.set_ylabel('Model', fontsize=11)
        ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    output_file = output_dir / 'creative_distribution_violin.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file}")


def plot_correlation_matrix(df: pd.DataFrame, output_dir: Path):
    """绘制指标相关性矩阵"""
    
    print("📊 Generating correlation matrix...")
    
    metric_cols = ['distinct_1', 'distinct_2', 'distinct_3', 'text_length', 'word_count']
    corr_matrix = df[metric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm',
                center=0, square=True, linewidths=1, ax=ax,
                cbar_kws={'label': 'Correlation Coefficient'})
    
    ax.set_title('Creative Quality Metrics Correlation Matrix', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / 'creative_correlation_matrix.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_file}")


def main():
    """主函数"""
    
    print("\n" + "="*60)
    print("📊 Creative Writing Quality Visualization")
    print("="*60 + "\n")
    
    # 加载数据
    data_file = Path('data/analize/results/creative_quality/creative_quality_scores.csv')
    output_dir = Path('data/analize/results/creative_quality/figures')
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return
    
    print(f"📂 Loading data from: {data_file}")
    df = pd.read_csv(data_file)
    print(f"✅ Loaded {len(df)} records\n")
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成图表
    plot_diversity_comparison(df, output_dir)
    plot_diversity_heatmap(df, output_dir)
    plot_radar_chart(df, output_dir)
    plot_distribution_violin(df, output_dir)
    plot_correlation_matrix(df, output_dir)
    
    print("\n" + "="*60)
    print("✅ All visualizations completed!")
    print(f"📁 Output directory: {output_dir}")
    print("="*60)


if __name__ == '__main__':
    main()
