#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逻辑推理质量评估可视化脚本

生成评估结果的可视化图表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def load_data(results_dir):
    """加载评估结果数据"""
    scores_file = results_dir / 'reasoning_quality_scores.csv'
    summary_file = results_dir / 'reasoning_quality_summary.csv'
    
    df_scores = pd.read_csv(scores_file)
    df_summary = pd.read_csv(summary_file)
    
    return df_scores, df_summary


def plot_conclusion_correctness(df_scores, output_dir):
    """绘制结论正确性对比图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 计算每个模型的平均正确率
    correctness = df_scores.groupby('model')['conclusion_correct'].mean().sort_values(ascending=False)
    
    # 绘制柱状图
    bars = ax.bar(range(len(correctness)), correctness.values, color='steelblue', alpha=0.8)
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, correctness.values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.1%}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('模型', fontsize=12, fontweight='bold')
    ax.set_ylabel('结论正确率', fontsize=12, fontweight='bold')
    ax.set_title('逻辑推理任务 - 结论正确性对比', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(correctness)))
    ax.set_xticklabels(correctness.index, rotation=45, ha='right')
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'reasoning_conclusion_correctness.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 结论正确性图表已保存")


def plot_completeness_scores(df_scores, output_dir):
    """绘制推理完整性对比图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 计算每个模型的平均完整性得分
    completeness = df_scores.groupby('model')['completeness_score'].mean().sort_values(ascending=False)
    
    # 绘制柱状图
    colors = ['green' if x >= 0.8 else 'orange' if x >= 0.6 else 'red' for x in completeness.values]
    bars = ax.bar(range(len(completeness)), completeness.values, color=colors, alpha=0.7)
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, completeness.values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{value:.2f}', ha='center', va='bottom', fontsize=9)
    
    # 添加参考线
    ax.axhline(y=0.8, color='green', linestyle='--', alpha=0.5, label='优秀 (≥0.8)')
    ax.axhline(y=0.6, color='orange', linestyle='--', alpha=0.5, label='良好 (≥0.6)')
    
    ax.set_xlabel('模型', fontsize=12, fontweight='bold')
    ax.set_ylabel('推理完整性得分', fontsize=12, fontweight='bold')
    ax.set_title('逻辑推理任务 - 推理完整性对比', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(completeness)))
    ax.set_xticklabels(completeness.index, rotation=45, ha='right')
    ax.set_ylim(0, 1.1)
    ax.legend(loc='upper right')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'reasoning_completeness_scores.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 推理完整性图表已保存")


def plot_reasoning_type_heatmap(df_scores, output_dir):
    """绘制不同推理类型的表现热力图"""
    # 创建透视表
    pivot_data = df_scores.pivot_table(
        values='conclusion_correct',
        index='model',
        columns='reasoning_type',
        aggfunc='mean'
    )
    
    # 按平均正确率排序
    pivot_data['avg'] = pivot_data.mean(axis=1)
    pivot_data = pivot_data.sort_values('avg', ascending=False)
    pivot_data = pivot_data.drop('avg', axis=1)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制热力图
    sns.heatmap(pivot_data, annot=True, fmt='.1%', cmap='RdYlGn', 
                center=0.5, vmin=0, vmax=1, cbar_kws={'label': '正确率'},
                linewidths=0.5, ax=ax)
    
    ax.set_xlabel('推理类型', fontsize=12, fontweight='bold')
    ax.set_ylabel('模型', fontsize=12, fontweight='bold')
    ax.set_title('不同推理类型的表现热力图', fontsize=14, fontweight='bold', pad=20)
    
    # 调整标签
    reasoning_type_labels = {
        'deductive': '演绎推理',
        'logic_puzzle': '逻辑谜题',
        'game_theory': '博弈论'
    }
    ax.set_xticklabels([reasoning_type_labels.get(col, col) for col in pivot_data.columns], rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'reasoning_type_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 推理类型热力图已保存")


def plot_multi_metric_comparison(df_scores, output_dir):
    """绘制多指标雷达图"""
    # 计算每个模型的平均指标
    metrics = ['conclusion_correct', 'completeness_score', 'coherence_score', 'depth_score']
    metric_labels = ['结论正确性', '推理完整性', '逻辑连贯性', '推理深度']
    
    model_metrics = df_scores.groupby('model')[metrics].mean()
    
    # 选择Top 5模型（按结论正确性）
    top_models = model_metrics.sort_values('conclusion_correct', ascending=False).head(5)
    
    # 设置雷达图
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(top_models)))
    
    for idx, (model, row) in enumerate(top_models.iterrows()):
        values = row[metrics].tolist()
        values += values[:1]  # 闭合
        
        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
    ax.grid(True, alpha=0.3)
    
    ax.set_title('Top 5 模型多维度能力雷达图', fontsize=14, fontweight='bold', pad=30)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'reasoning_multi_metric_radar.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 多指标雷达图已保存")


def plot_question_difficulty(df_scores, output_dir):
    """绘制问题难度分析图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # 计算每个问题的平均正确率
    question_difficulty = df_scores.groupby('question_id')['conclusion_correct'].mean().sort_values()
    
    # 绘制柱状图
    colors = ['red' if x < 0.2 else 'orange' if x < 0.5 else 'green' for x in question_difficulty.values]
    bars = ax.barh(range(len(question_difficulty)), question_difficulty.values, color=colors, alpha=0.7)
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, question_difficulty.values)):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f'{value:.1%}', ha='left', va='center', fontsize=10)
    
    ax.set_yticks(range(len(question_difficulty)))
    ax.set_yticklabels(question_difficulty.index)
    ax.set_xlabel('平均正确率', fontsize=12, fontweight='bold')
    ax.set_ylabel('问题ID', fontsize=12, fontweight='bold')
    ax.set_title('问题难度分析（按平均正确率）', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlim(0, 1.0)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.0%}'))
    ax.grid(axis='x', alpha=0.3)
    
    # 添加难度标签
    ax.text(0.95, 0.95, '难度: 低→高', transform=ax.transAxes,
            ha='right', va='top', fontsize=10, style='italic',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig(output_dir / 'reasoning_question_difficulty.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 问题难度分析图已保存")


def plot_step_count_distribution(df_scores, output_dir):
    """绘制推理步骤数分布图"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 按模型分组的步骤数
    step_data = df_scores.groupby('model')['step_count'].mean().sort_values(ascending=False)
    
    # 绘制柱状图
    bars = ax.bar(range(len(step_data)), step_data.values, color='teal', alpha=0.7)
    
    # 添加数值标签
    for i, (bar, value) in enumerate(zip(bars, step_data.values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{value:.1f}', ha='center', va='bottom', fontsize=9)
    
    ax.set_xlabel('模型', fontsize=12, fontweight='bold')
    ax.set_ylabel('平均推理步骤数', fontsize=12, fontweight='bold')
    ax.set_title('逻辑推理任务 - 平均推理步骤数对比', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(range(len(step_data)))
    ax.set_xticklabels(step_data.index, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'reasoning_step_count.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 推理步骤数分布图已保存")


def main():
    # 设置路径
    project_root = Path(__file__).parent.parent.parent.parent
    results_dir = project_root / 'data' / 'analize' / 'results' / 'reasoning_quality'
    figures_dir = results_dir / 'figures'
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*60)
    print("📊 逻辑推理质量评估可视化")
    print("="*60)
    print()
    
    # 加载数据
    print("📂 加载评估数据...")
    df_scores, df_summary = load_data(results_dir)
    print(f"✓ 已加载 {len(df_scores)} 条评分记录")
    print()
    
    # 生成图表
    print("🎨 生成可视化图表...")
    print()
    
    plot_conclusion_correctness(df_scores, figures_dir)
    plot_completeness_scores(df_scores, figures_dir)
    plot_reasoning_type_heatmap(df_scores, figures_dir)
    plot_multi_metric_comparison(df_scores, figures_dir)
    plot_question_difficulty(df_scores, figures_dir)
    plot_step_count_distribution(df_scores, figures_dir)
    
    print()
    print("="*60)
    print(f"✅ 所有图表已保存到: {figures_dir}")
    print("="*60)
    print()
    
    # 列出生成的图表
    print("📊 生成的图表:")
    for img_file in sorted(figures_dir.glob('*.png')):
        print(f"  - {img_file.name}")


if __name__ == '__main__':
    main()
