#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创意写作质量可视化脚本

生成多维度质量指标的可视化图表

作者：Kiro AI Assistant
日期：2026-03-04
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def plot_quality_comparison(df, output_dir):
    """绘制质量指标对比图"""
    
    # 计算每个模型的平均指标
    model_avg = df.groupby('model').agg({
        'distinct_2': 'mean',
        'unique_token_ratio': 'mean',
        'total_rhetorical_devices': 'mean'
    }).round(4)
    
    # 按 distinct_2 排序
    model_avg = model_avg.sort_values('distinct_2', ascending=False)
    
    # 创建图表
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 1. Distinct-2 柱状图
    ax1 = axes[0]
    bars1 = ax1.barh(model_avg.index, model_avg['distinct_2'], color='steelblue')
    ax1.set_xlabel('Distinct-2 分数', fontsize=12)
    ax1.set_title('多样性指标 (Distinct-2)', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, 1.0)
    
    # 添加数值标签
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.4f}', va='center', fontsize=9)
    
    # 2. 独特词汇比例柱状图
    ax2 = axes[1]
    model_avg_sorted = model_avg.sort_values('unique_token_ratio', ascending=False)
    bars2 = ax2.barh(model_avg_sorted.index, model_avg_sorted['unique_token_ratio'], 
                     color='coral')
    ax2.set_xlabel('独特词汇比例', fontsize=12)
    ax2.set_title('词汇丰富度', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 1.0)
    
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.4f}', va='center', fontsize=9)
    
    # 3. 修辞手法总数柱状图
    ax3 = axes[2]
    model_avg_sorted = model_avg.sort_values('total_rhetorical_devices', ascending=False)
    bars3 = ax3.barh(model_avg_sorted.index, model_avg_sorted['total_rhetorical_devices'], 
                     color='mediumseagreen')
    ax3.set_xlabel('修辞手法总数', fontsize=12)
    ax3.set_title('创造力指标', fontsize=14, fontweight='bold')
    
    for i, bar in enumerate(bars3):
        width = bar.get_width()
        ax3.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}', va='center', fontsize=9)
    
    plt.tight_layout()
    output_file = output_dir / 'creative_quality_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 质量对比图已保存: {output_file}")
    plt.close()


def plot_radar_chart(df, output_dir):
    """绘制雷达图（综合能力）"""
    
    # 选择Top 6模型（按distinct_2）
    model_avg = df.groupby('model').agg({
        'distinct_2': 'mean',
        'unique_token_ratio': 'mean',
        'total_rhetorical_devices': 'mean',
        'text_length': 'mean',
        'sentence_count': 'mean'
    })
    
    top_models = model_avg.nlargest(6, 'distinct_2').index
    
    # 归一化指标到 [0, 1]
    metrics = ['distinct_2', 'unique_token_ratio', 'total_rhetorical_devices', 
               'text_length', 'sentence_count']
    
    normalized_data = model_avg.loc[top_models, metrics].copy()
    for col in metrics:
        min_val = normalized_data[col].min()
        max_val = normalized_data[col].max()
        if max_val > min_val:
            normalized_data[col] = (normalized_data[col] - min_val) / (max_val - min_val)
        else:
            normalized_data[col] = 0.5
    
    # 设置雷达图
    labels = ['多样性\n(Distinct-2)', '词汇丰富度', '修辞手法', '文本长度', '句子数']
    num_vars = len(labels)
    
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = plt.cm.Set2(np.linspace(0, 1, len(top_models)))
    
    for idx, model in enumerate(top_models):
        values = normalized_data.loc[model].tolist()
        values += values[:1]
        
        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
    ax.grid(True)
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    plt.title('创意写作综合能力雷达图 (Top 6 模型)', 
              fontsize=14, fontweight='bold', pad=20)
    
    output_file = output_dir / 'creative_quality_radar.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 雷达图已保存: {output_file}")
    plt.close()


def plot_question_heatmap(df, output_dir):
    """绘制问题-模型热力图"""
    
    # 创建透视表（模型 × 问题 × distinct_2）
    pivot_data = df.pivot_table(
        index='model', 
        columns='question_id', 
        values='distinct_2'
    )
    
    # 按平均分数排序
    pivot_data['avg'] = pivot_data.mean(axis=1)
    pivot_data = pivot_data.sort_values('avg', ascending=False)
    pivot_data = pivot_data.drop('avg', axis=1)
    
    # 绘制热力图
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='YlGnBu', 
                cbar_kws={'label': 'Distinct-2 分数'},
                linewidths=0.5, ax=ax)
    
    ax.set_xlabel('问题编号', fontsize=12)
    ax.set_ylabel('模型', fontsize=12)
    ax.set_title('创意写作多样性热力图 (Distinct-2)', 
                 fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    output_file = output_dir / 'creative_quality_heatmap.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 热力图已保存: {output_file}")
    plt.close()


def plot_scatter_diversity_vs_length(df, output_dir):
    """绘制多样性 vs 文本长度散点图"""
    
    model_avg = df.groupby('model').agg({
        'distinct_2': 'mean',
        'text_length': 'mean',
        'total_rhetorical_devices': 'mean'
    }).reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 按修辞手法数量着色
    scatter = ax.scatter(model_avg['text_length'], 
                        model_avg['distinct_2'],
                        s=model_avg['total_rhetorical_devices'] * 30,
                        c=model_avg['total_rhetorical_devices'],
                        cmap='viridis',
                        alpha=0.7,
                        edgecolors='black',
                        linewidth=1.5)
    
    # 添加模型标签
    for idx, row in model_avg.iterrows():
        ax.annotate(row['model'], 
                   (row['text_length'], row['distinct_2']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, alpha=0.8)
    
    ax.set_xlabel('平均文本长度（字符数）', fontsize=12)
    ax.set_ylabel('Distinct-2 分数（多样性）', fontsize=12)
    ax.set_title('创意写作：多样性 vs 文本长度\n（气泡大小和颜色表示修辞手法数量）', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('修辞手法总数', fontsize=11)
    
    plt.tight_layout()
    output_file = output_dir / 'creative_diversity_vs_length.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 散点图已保存: {output_file}")
    plt.close()


def main():
    """主函数"""
    print("="*60)
    print("创意写作质量可视化")
    print("="*60)
    
    # 路径配置
    data_dir = Path('data/analize/results/creative_quality')
    output_dir = Path('data/analize/results/creative_quality/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    print("\n📂 加载评估结果...")
    detail_file = data_dir / 'creative_quality_scores_detailed.csv'
    
    if not detail_file.exists():
        print(f"❌ 文件不存在: {detail_file}")
        print("请先运行 evaluate_creative_quality.py")
        return
    
    df = pd.read_csv(detail_file, encoding='utf-8-sig')
    print(f"✅ 加载完成: {len(df)} 条记录")
    
    # 生成可视化
    print("\n📊 生成可视化图表...")
    
    print("\n1. 质量指标对比图...")
    plot_quality_comparison(df, output_dir)
    
    print("\n2. 综合能力雷达图...")
    plot_radar_chart(df, output_dir)
    
    print("\n3. 问题-模型热力图...")
    plot_question_heatmap(df, output_dir)
    
    print("\n4. 多样性 vs 文本长度散点图...")
    plot_scatter_diversity_vs_length(df, output_dir)
    
    print("\n" + "="*60)
    print("✅ 可视化完成！")
    print("="*60)
    print(f"\n输出目录: {output_dir}")


if __name__ == '__main__':
    main()
