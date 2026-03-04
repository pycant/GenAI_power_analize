# -*- coding: utf-8 -*-
"""
问答任务质量评估可视化脚本

生成图表:
1. EM vs F1 散点图
2. 模型-问题热力图
3. 指标对比柱状图
4. 答案提取效果对比
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def load_data(results_dir: Path):
    """加载评估结果"""
    scores_file = results_dir / 'qa_quality_scores_academic.csv'
    
    if not scores_file.exists():
        print(f"❌ Error: File not found: {scores_file}")
        return None
    
    df = pd.read_csv(scores_file)
    print(f"✅ Loaded {len(df)} evaluations")
    
    return df


def plot_em_vs_f1(df: pd.DataFrame, output_dir: Path):
    """绘制EM vs F1散点图"""
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 按模型分组计算平均值
    model_stats = df.groupby('model').agg({
        'exact_match': 'mean',
        'f1_score': 'mean'
    }).reset_index()
    
    # 绘制散点
    scatter = ax.scatter(
        model_stats['f1_score'] * 100,
        model_stats['exact_match'] * 100,
        s=200,
        alpha=0.6,
        c=range(len(model_stats)),
        cmap='viridis'
    )
    
    # 添加模型标签
    for _, row in model_stats.iterrows():
        ax.annotate(
            row['model'],
            (row['f1_score'] * 100, row['exact_match'] * 100),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9,
            alpha=0.8
        )
    
    ax.set_xlabel('F1 Score (%)', fontsize=12)
    ax.set_ylabel('Exact Match (%)', fontsize=12)
    ax.set_title('问答任务: Exact Match vs F1 Score', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = output_dir / 'qa_em_vs_f1.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def plot_model_question_heatmap(df: pd.DataFrame, output_dir: Path):
    """绘制模型-问题热力图"""
    
    # 创建透视表
    pivot_em = df.pivot_table(
        values='exact_match',
        index='model',
        columns='question_id',
        aggfunc='mean'
    )
    
    pivot_f1 = df.pivot_table(
        values='f1_score',
        index='model',
        columns='question_id',
        aggfunc='mean'
    )
    
    # 绘制两个热力图
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    # EM热力图
    sns.heatmap(
        pivot_em * 100,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        ax=axes[0],
        cbar_kws={'label': 'Exact Match (%)'}
    )
    axes[0].set_title('Exact Match (%)', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Question ID', fontsize=12)
    axes[0].set_ylabel('Model', fontsize=12)
    
    # F1热力图
    sns.heatmap(
        pivot_f1 * 100,
        annot=True,
        fmt='.1f',
        cmap='YlGnBu',
        ax=axes[1],
        cbar_kws={'label': 'F1 Score (%)'}
    )
    axes[1].set_title('F1 Score (%)', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Question ID', fontsize=12)
    axes[1].set_ylabel('Model', fontsize=12)
    
    plt.tight_layout()
    output_file = output_dir / 'qa_model_question_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def plot_metric_comparison(df: pd.DataFrame, output_dir: Path):
    """绘制指标对比柱状图"""
    
    # 按模型汇总
    model_stats = df.groupby('model').agg({
        'exact_match': 'mean',
        'f1_score': 'mean',
        'rouge_l': 'mean',
        'bleu': 'mean'
    }).reset_index()
    
    # 转换为百分比
    model_stats['exact_match'] *= 100
    model_stats['f1_score'] *= 100
    model_stats['rouge_l'] *= 100
    model_stats['bleu'] *= 100
    
    # 按F1排序
    model_stats = model_stats.sort_values('f1_score', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    x = np.arange(len(model_stats))
    width = 0.2
    
    ax.barh(x - 1.5*width, model_stats['exact_match'], width, label='Exact Match', alpha=0.8)
    ax.barh(x - 0.5*width, model_stats['f1_score'], width, label='F1 Score', alpha=0.8)
    ax.barh(x + 0.5*width, model_stats['rouge_l'], width, label='ROUGE-L', alpha=0.8)
    ax.barh(x + 1.5*width, model_stats['bleu'], width, label='BLEU', alpha=0.8)
    
    ax.set_yticks(x)
    ax.set_yticklabels(model_stats['model'])
    ax.set_xlabel('Score (%)', fontsize=12)
    ax.set_title('问答任务: 多指标对比', fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    output_file = output_dir / 'qa_metric_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def plot_question_difficulty(df: pd.DataFrame, output_dir: Path):
    """绘制问题难度分析"""
    
    # 按问题汇总
    question_stats = df.groupby('question_id').agg({
        'exact_match': ['mean', 'std'],
        'f1_score': ['mean', 'std']
    }).reset_index()
    
    question_stats.columns = ['question_id', 'em_mean', 'em_std', 'f1_mean', 'f1_std']
    question_stats = question_stats.sort_values('f1_mean', ascending=False)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # EM柱状图
    axes[0].bar(
        question_stats['question_id'],
        question_stats['em_mean'] * 100,
        yerr=question_stats['em_std'] * 100,
        alpha=0.7,
        capsize=5
    )
    axes[0].set_xlabel('Question ID', fontsize=12)
    axes[0].set_ylabel('Exact Match (%)', fontsize=12)
    axes[0].set_title('问题难度: Exact Match', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # F1柱状图
    axes[1].bar(
        question_stats['question_id'],
        question_stats['f1_mean'] * 100,
        yerr=question_stats['f1_std'] * 100,
        alpha=0.7,
        capsize=5,
        color='orange'
    )
    axes[1].set_xlabel('Question ID', fontsize=12)
    axes[1].set_ylabel('F1 Score (%)', fontsize=12)
    axes[1].set_title('问题难度: F1 Score', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_file = output_dir / 'qa_question_difficulty.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_file}")
    plt.close()


def main():
    """主函数"""
    
    print("\n" + "="*60)
    print("📊 QA Quality Visualization")
    print("="*60)
    
    results_dir = Path('data/analize/results/qa_quality_academic')
    figures_dir = results_dir / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    df = load_data(results_dir)
    
    if df is None:
        return
    
    print(f"\n📈 Generating visualizations...")
    
    # 生成图表
    plot_em_vs_f1(df, figures_dir)
    plot_model_question_heatmap(df, figures_dir)
    plot_metric_comparison(df, figures_dir)
    plot_question_difficulty(df, figures_dir)
    
    print(f"\n✅ All visualizations completed!")
    print(f"📁 Output directory: {figures_dir}")


if __name__ == '__main__':
    main()
