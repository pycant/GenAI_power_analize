# -*- coding: utf-8 -*-
"""
翻译质量评估可视化脚本

生成翻译质量评估的可视化图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def visualize_translation_quality(results_dir: Path):
    """可视化翻译质量评估结果"""
    
    print("\n" + "="*60)
    print("📊 Translation Quality Visualization")
    print("="*60)
    
    # 加载数据
    scores_file = results_dir / 'translation_quality_scores.csv'
    
    if not scores_file.exists():
        print(f"❌ Error: File not found: {scores_file}")
        return
    
    df = pd.read_csv(scores_file)
    
    print(f"\n📂 Loaded {len(df)} evaluation records")
    print(f"📊 Models: {df['model'].nunique()}")
    print(f"🌐 Questions: {df['question_id'].nunique()}")
    
    # 创建图表目录
    figures_dir = results_dir / 'figures'
    figures_dir.mkdir(exist_ok=True)
    
    # 1. 核心指标对比（BLEU-4, chrF, BERTScore）
    plot_core_metrics_comparison(df, figures_dir)
    
    # 2. 按语言对分析
    plot_language_pair_analysis(df, figures_dir)
    
    # 3. 多指标雷达图
    plot_radar_chart(df, figures_dir)
    
    # 4. 指标相关性热力图
    plot_correlation_heatmap(df, figures_dir)
    
    # 5. 按领域分析
    plot_domain_analysis(df, figures_dir)
    
    print(f"\n✅ Visualization completed!")
    print(f"📁 Figures saved to: {figures_dir}")


def plot_core_metrics_comparison(df: pd.DataFrame, output_dir: Path):
    """绘制核心指标对比图"""
    
    print("\n📊 Plotting core metrics comparison...")
    
    # 按模型汇总
    metrics = ['bleu_4', 'chrf', 'bertscore_f1']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if not available_metrics:
        print("⚠️  No core metrics available")
        return
    
    summary = df.groupby('model')[available_metrics].mean().sort_values(
        by=available_metrics[0], ascending=False
    )
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(summary))
    width = 0.25
    
    for i, metric in enumerate(available_metrics):
        offset = (i - len(available_metrics)/2 + 0.5) * width
        bars = ax.bar(x + offset, summary[metric], width, 
                     label=metric.replace('_', ' ').title())
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=8)
    
    ax.set_xlabel('模型', fontsize=12, fontweight='bold')
    ax.set_ylabel('分数', fontsize=12, fontweight='bold')
    ax.set_title('翻译质量核心指标对比', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(summary.index, rotation=45, ha='right')
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'translation_core_metrics_comparison.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: translation_core_metrics_comparison.png")


def plot_language_pair_analysis(df: pd.DataFrame, output_dir: Path):
    """绘制按语言对分析图"""
    
    print("\n📊 Plotting language pair analysis...")
    
    if 'source_lang' not in df.columns or 'bleu_4' not in df.columns:
        print("⚠️  Missing required columns")
        return
    
    # 按语言对和模型汇总
    lang_summary = df.groupby(['source_lang', 'model'])['bleu_4'].mean().unstack()
    
    # 创建图表
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 英译中
    eng_to_zh = lang_summary.loc['eng'].sort_values(ascending=False)
    axes[0].barh(range(len(eng_to_zh)), eng_to_zh.values, color='steelblue')
    axes[0].set_yticks(range(len(eng_to_zh)))
    axes[0].set_yticklabels(eng_to_zh.index)
    axes[0].set_xlabel('BLEU-4 分数', fontsize=11, fontweight='bold')
    axes[0].set_title('英译中 (eng → zho_Hans)', fontsize=12, fontweight='bold')
    axes[0].grid(axis='x', alpha=0.3)
    
    # 添加数值标签
    for i, v in enumerate(eng_to_zh.values):
        axes[0].text(v, i, f' {v:.3f}', va='center', fontsize=9)
    
    # 中译英
    if 'zho_Hans' in lang_summary.index:
        zh_to_eng = lang_summary.loc['zho_Hans'].sort_values(ascending=False)
        axes[1].barh(range(len(zh_to_eng)), zh_to_eng.values, color='coral')
        axes[1].set_yticks(range(len(zh_to_eng)))
        axes[1].set_yticklabels(zh_to_eng.index)
        axes[1].set_xlabel('BLEU-4 分数', fontsize=11, fontweight='bold')
        axes[1].set_title('中译英 (zho_Hans → eng)', fontsize=12, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)
        
        # 添加数值标签
        for i, v in enumerate(zh_to_eng.values):
            axes[1].text(v, i, f' {v:.3f}', va='center', fontsize=9)
    
    plt.suptitle('按语言对分析', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / 'translation_language_pair_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: translation_language_pair_analysis.png")


def plot_radar_chart(df: pd.DataFrame, output_dir: Path):
    """绘制多指标雷达图（Top 5模型）"""
    
    print("\n📊 Plotting radar chart...")
    
    # 选择指标
    metrics = ['bleu_4', 'chrf', 'bertscore_f1']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 3:
        print("⚠️  Not enough metrics for radar chart")
        return
    
    # 选择Top 5模型（按BLEU-4）
    top_models = df.groupby('model')['bleu_4'].mean().sort_values(ascending=False).head(5).index
    
    # 准备数据
    radar_data = df[df['model'].isin(top_models)].groupby('model')[available_metrics].mean()
    
    # 归一化到[0, 1]
    radar_data_norm = (radar_data - radar_data.min()) / (radar_data.max() - radar_data.min())
    
    # 创建雷达图
    angles = np.linspace(0, 2 * np.pi, len(available_metrics), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    for model in radar_data_norm.index:
        values = radar_data_norm.loc[model].tolist()
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=model)
        ax.fill(angles, values, alpha=0.15)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([m.replace('_', ' ').title() for m in available_metrics], fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
    ax.grid(True, alpha=0.3)
    
    plt.title('翻译质量多指标雷达图 (Top 5 模型)', 
             fontsize=14, fontweight='bold', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'translation_radar_chart.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: translation_radar_chart.png")


def plot_correlation_heatmap(df: pd.DataFrame, output_dir: Path):
    """绘制指标相关性热力图"""
    
    print("\n📊 Plotting correlation heatmap...")
    
    # 选择数值列
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # 排除非指标列
    exclude_cols = ['edit_distance']
    metric_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    if len(metric_cols) < 2:
        print("⚠️  Not enough metrics for correlation analysis")
        return
    
    # 计算相关性
    corr = df[metric_cols].corr()
    
    # 创建热力图
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr, annot=True, fmt='.3f', cmap='coolwarm', 
                center=0, square=True, linewidths=1,
                cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title('翻译质量指标相关性热力图', fontsize=14, fontweight='bold', pad=20)
    
    # 旋转标签
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'translation_correlation_heatmap.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: translation_correlation_heatmap.png")


def plot_domain_analysis(df: pd.DataFrame, output_dir: Path):
    """绘制按领域分析图"""
    
    print("\n📊 Plotting domain analysis...")
    
    if 'domain' not in df.columns or 'bleu_4' not in df.columns:
        print("⚠️  Missing required columns")
        return
    
    # 按领域和模型汇总
    domain_summary = df.groupby(['domain', 'model'])['bleu_4'].mean().unstack()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(14, 8))
    
    domain_summary.T.plot(kind='bar', ax=ax, width=0.8)
    
    ax.set_xlabel('模型', fontsize=12, fontweight='bold')
    ax.set_ylabel('BLEU-4 分数', fontsize=12, fontweight='bold')
    ax.set_title('按领域分析 - BLEU-4 分数', fontsize=14, fontweight='bold', pad=20)
    ax.legend(title='领域', loc='upper right', fontsize=10)
    ax.grid(axis='y', alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_dir / 'translation_domain_analysis.png', 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: translation_domain_analysis.png")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='可视化翻译质量评估结果')
    parser.add_argument('--results-dir', type=str,
                       default='data/analize/results/translation_quality',
                       help='结果目录')
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    
    visualize_translation_quality(results_dir)
