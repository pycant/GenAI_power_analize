#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创意写作质量可视化脚本（包含困惑度）

生成包含困惑度指标的可视化图表

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


def plot_perplexity_comparison(df, output_dir):
    """绘制困惑度对比图"""
    
    # 计算每个模型的平均困惑度
    model_ppl = df.groupby('model')['perplexity'].mean().sort_values()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bars = ax.barh(model_ppl.index, model_ppl.values, color='skyblue')
    ax.set_xlabel('平均困惑度（越低越好）', fontsize=12)
    ax.set_title('各模型困惑度对比', fontsize=14, fontweight='bold')
    
    # 添加数值标签
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2, 
                f'{width:.2f}', va='center', fontsize=9)
    
    plt.tight_layout()
    output_file = output_dir / 'perplexity_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 困惑度对比图已保存: {output_file}")
    plt.close()


def plot_perplexity_vs_diversity(df, output_dir):
    """绘制困惑度 vs 多样性散点图"""
    
    model_avg = df.groupby('model').agg({
        'perplexity': 'mean',
        'distinct_2': 'mean',
        'unique_token_ratio': 'mean'
    }).reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 按独特词汇比例着色
    scatter = ax.scatter(model_avg['perplexity'], 
                        model_avg['distinct_2'],
                        s=model_avg['unique_token_ratio'] * 500,
                        c=model_avg['unique_token_ratio'],
                        cmap='viridis',
                        alpha=0.7,
                        edgecolors='black',
                        linewidth=1.5)
    
    # 添加模型标签
    for idx, row in model_avg.iterrows():
        ax.annotate(row['model'], 
                   (row['perplexity'], row['distinct_2']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.8)
    
    ax.set_xlabel('平均困惑度（越低越好）', fontsize=12)
    ax.set_ylabel('Distinct-2 分数（多样性）', fontsize=12)
    ax.set_title('困惑度 vs 多样性\n（气泡大小和颜色表示词汇丰富度）', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('独特词汇比例', fontsize=11)
    
    plt.tight_layout()
    output_file = output_dir / 'perplexity_vs_diversity.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 困惑度vs多样性图已保存: {output_file}")
    plt.close()


def plot_comprehensive_quality_metrics(df, output_dir):
    """绘制综合质量指标对比（包含困惑度）"""
    
    # 计算每个模型的平均指标
    model_avg = df.groupby('model').agg({
        'distinct_2': 'mean',
        'unique_token_ratio': 'mean',
        'total_rhetorical_devices': 'mean',
        'perplexity': 'mean'
    }).round(4)
    
    # 归一化困惑度（越低越好，所以取倒数）
    model_avg['perplexity_norm'] = 1 / (model_avg['perplexity'] + 1)
    
    # 按 distinct_2 排序
    model_avg = model_avg.sort_values('distinct_2', ascending=False)
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Distinct-2
    ax1 = axes[0, 0]
    bars1 = ax1.barh(model_avg.index, model_avg['distinct_2'], color='steelblue')
    ax1.set_xlabel('Distinct-2 分数', fontsize=11)
    ax1.set_title('多样性指标', fontsize=12, fontweight='bold')
    for i, bar in enumerate(bars1):
        width = bar.get_width()
        ax1.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', va='center', fontsize=8)
    
    # 2. 独特词汇比例
    ax2 = axes[0, 1]
    model_avg_sorted = model_avg.sort_values('unique_token_ratio', ascending=False)
    bars2 = ax2.barh(model_avg_sorted.index, model_avg_sorted['unique_token_ratio'], 
                     color='coral')
    ax2.set_xlabel('独特词汇比例', fontsize=11)
    ax2.set_title('词汇丰富度', fontsize=12, fontweight='bold')
    for i, bar in enumerate(bars2):
        width = bar.get_width()
        ax2.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', va='center', fontsize=8)
    
    # 3. 修辞手法
    ax3 = axes[1, 0]
    model_avg_sorted = model_avg.sort_values('total_rhetorical_devices', ascending=False)
    bars3 = ax3.barh(model_avg_sorted.index, model_avg_sorted['total_rhetorical_devices'], 
                     color='mediumseagreen')
    ax3.set_xlabel('修辞手法总数', fontsize=11)
    ax3.set_title('创造力指标', fontsize=12, fontweight='bold')
    for i, bar in enumerate(bars3):
        width = bar.get_width()
        ax3.text(width + 0.3, bar.get_y() + bar.get_height()/2, 
                f'{width:.1f}', va='center', fontsize=8)
    
    # 4. 困惑度（归一化，越高越好）
    ax4 = axes[1, 1]
    model_avg_sorted = model_avg.sort_values('perplexity_norm', ascending=False)
    bars4 = ax4.barh(model_avg_sorted.index, model_avg_sorted['perplexity_norm'], 
                     color='mediumpurple')
    ax4.set_xlabel('流畅度得分（归一化）', fontsize=11)
    ax4.set_title('流畅性指标（基于困惑度）', fontsize=12, fontweight='bold')
    for i, bar in enumerate(bars4):
        width = bar.get_width()
        # 显示原始困惑度
        orig_ppl = model_avg_sorted.iloc[i]['perplexity']
        ax4.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'{orig_ppl:.1f}', va='center', fontsize=8)
    
    plt.tight_layout()
    output_file = output_dir / 'comprehensive_quality_with_perplexity.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 综合质量指标图已保存: {output_file}")
    plt.close()


def plot_quality_efficiency_tradeoff(df, output_dir):
    """绘制质量-效率权衡图（多样性 vs 流畅性）"""
    
    model_avg = df.groupby('model').agg({
        'distinct_2': 'mean',
        'perplexity': 'mean',
        'total_rhetorical_devices': 'mean'
    }).reset_index()
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 按修辞手法数量着色
    scatter = ax.scatter(model_avg['perplexity'], 
                        model_avg['distinct_2'],
                        s=model_avg['total_rhetorical_devices'] * 50,
                        c=model_avg['total_rhetorical_devices'],
                        cmap='RdYlGn',
                        alpha=0.7,
                        edgecolors='black',
                        linewidth=1.5)
    
    # 添加模型标签
    for idx, row in model_avg.iterrows():
        ax.annotate(row['model'], 
                   (row['perplexity'], row['distinct_2']),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=8, alpha=0.8)
    
    # 添加理想区域标注
    ax.axvline(x=20, color='green', linestyle='--', alpha=0.3, label='流畅度阈值')
    ax.axhline(y=0.85, color='blue', linestyle='--', alpha=0.3, label='多样性阈值')
    
    ax.set_xlabel('困惑度（越低越流畅）', fontsize=12)
    ax.set_ylabel('Distinct-2（越高越多样）', fontsize=12)
    ax.set_title('创意写作质量权衡：多样性 vs 流畅性\n（气泡大小和颜色表示创造力）', 
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    
    # 添加颜色条
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('修辞手法数量', fontsize=11)
    
    plt.tight_layout()
    output_file = output_dir / 'quality_efficiency_tradeoff.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 质量-效率权衡图已保存: {output_file}")
    plt.close()


def main():
    """主函数"""
    print("="*60)
    print("创意写作质量可视化（包含困惑度）")
    print("="*60)
    
    # 路径配置
    data_file = Path('data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv')
    output_dir = Path('data/analize/results/creative_quality/figures')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    print("\n📂 加载评估结果...")
    
    if not data_file.exists():
        print(f"❌ 文件不存在: {data_file}")
        print("请先运行 calculate_perplexity_local.py")
        return
    
    df = pd.read_csv(data_file, encoding='utf-8-sig')
    print(f"✅ 加载完成: {len(df)} 条记录")
    
    # 生成可视化
    print("\n📊 生成可视化图表...")
    
    print("\n1. 困惑度对比图...")
    plot_perplexity_comparison(df, output_dir)
    
    print("\n2. 困惑度 vs 多样性...")
    plot_perplexity_vs_diversity(df, output_dir)
    
    print("\n3. 综合质量指标对比...")
    plot_comprehensive_quality_metrics(df, output_dir)
    
    print("\n4. 质量-效率权衡图...")
    plot_quality_efficiency_tradeoff(df, output_dir)
    
    print("\n" + "="*60)
    print("✅ 可视化完成！")
    print("="*60)
    print(f"\n输出目录: {output_dir}")


if __name__ == '__main__':
    main()
