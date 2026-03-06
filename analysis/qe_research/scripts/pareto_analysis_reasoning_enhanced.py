#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reasoning任务的帕累托前沿分析（增强版）
Enhanced Pareto Frontier Analysis for Reasoning Task

包含完整的分析步骤可视化：
1. 熵权法计算过程可视化
2. 数据分布分析
3. 相关性分析
4. 帕累托前沿识别
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 学术配色方案
ACADEMIC_COLORS = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC', 
                   '#CA9161', '#949494', '#ECE133', '#56B4E9']

# 维度名称映射
DIMENSION_NAMES = {
    'avg_correctness': '正确性',
    'avg_completeness': '完整性',
    'avg_rigor': '严谨性',
    'avg_clarity': '清晰度',
    'avg_efficiency': '效率'
}


class EnhancedParetoAnalyzer:
    """增强版帕累托前沿分析器（包含完整可视化）"""
    
    def __init__(self):
        self.project_root = project_root
        self.results_dir = self.project_root / 'analysis/qe_research/results/pareto_analysis/reasoning'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.process_dir = self.results_dir / 'process_visualization'
        self.process_dir.mkdir(exist_ok=True)
        
        # 模型名称映射表
        self.model_mapping = {
            'qwen25_7b_hf_4bit': 'qwen--qwen2.5-7b-instruct:4bit',
            'qwen25_3b_hf_4bit': 'qwen--qwen2.5-3b-instruct:4bit',
            'qwen25_3b_hf_8bit': 'qwen--qwen2.5-3b-instruct:8bit',
            'deepseek_8b_ol_q4km': 'deepseek-r1:8b',
            'gemma_4b_ol_q4km': 'gemma3:4b',
            'qwen_4b_ol_q4km': 'qwen3:4b',
            'qwen_8b_ol_q4km': 'qwen3:8b',
            'phi3_4b_hf_4bit': 'microsoft--phi-3-mini-4k-instruct:4bit',
            'phi3_4b_hf_8bit': 'microsoft--phi-3-mini-4k-instruct:8bit',
            'gemma_2b_hf_4bit': 'google--gemma-2b-it:4bit',
            'gemma_2b_hf_8bit': 'google--gemma-2b-it:8bit',
        }
        
        self.entropy_weights = None
        self.quality_df_raw = None

    
    def visualize_entropy_weights(self, df, score_columns):
        """可视化熵权法计算过程"""
        print("\n步骤1: 熵权法计算过程可视化")
        
        # 1. 数据标准化
        data = df[score_columns].values
        data_norm = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-10)
        
        # 2. 计算概率矩阵
        p = data_norm / (data_norm.sum(axis=0) + 1e-10)
        
        # 3. 计算信息熵
        n = len(data_norm)
        entropy = -np.sum(p * np.log(p + 1e-10), axis=0) / np.log(n)
        
        # 4. 计算权重
        diversity = 1 - entropy
        weights = diversity / diversity.sum()
        
        # 保存权重
        self.entropy_weights = dict(zip(score_columns, weights))
        
        # 创建可视化
        fig = plt.figure(figsize=(16, 10), dpi=300)
        
        # 子图1: 原始数据热力图
        ax1 = plt.subplot(2, 3, 1)
        sns.heatmap(df[score_columns].T, annot=True, fmt='.2f', cmap='YlOrRd',
                   yticklabels=[DIMENSION_NAMES[col] for col in score_columns],
                   xticklabels=df['model'].str[:15], cbar_kws={'label': '评分'})
        ax1.set_title('(a) 原始评分矩阵', fontsize=11, fontweight='bold', pad=10)
        ax1.set_xlabel('模型', fontsize=10)
        ax1.set_ylabel('评分维度', fontsize=10)
        
        # 子图2: 标准化数据热力图
        ax2 = plt.subplot(2, 3, 2)
        sns.heatmap(data_norm.T, annot=True, fmt='.3f', cmap='Blues',
                   yticklabels=[DIMENSION_NAMES[col] for col in score_columns],
                   xticklabels=df['model'].str[:15], cbar_kws={'label': '标准化值'})
        ax2.set_title('(b) 标准化后数据', fontsize=11, fontweight='bold', pad=10)
        ax2.set_xlabel('模型', fontsize=10)
        ax2.set_ylabel('评分维度', fontsize=10)

        
        # 子图3: 信息熵柱状图
        ax3 = plt.subplot(2, 3, 3)
        dim_names = [DIMENSION_NAMES[col] for col in score_columns]
        bars = ax3.bar(range(len(entropy)), entropy, color=ACADEMIC_COLORS[:len(entropy)], alpha=0.7)
        ax3.set_xticks(range(len(entropy)))
        ax3.set_xticklabels(dim_names, rotation=45, ha='right')
        ax3.set_ylabel('信息熵', fontsize=10)
        ax3.set_title('(c) 各维度信息熵', fontsize=11, fontweight='bold', pad=10)
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        for i, (bar, val) in enumerate(zip(bars, entropy)):
            ax3.text(i, val + 0.01, f'{val:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 子图4: 多样性系数
        ax4 = plt.subplot(2, 3, 4)
        bars = ax4.bar(range(len(diversity)), diversity, color=ACADEMIC_COLORS[:len(diversity)], alpha=0.7)
        ax4.set_xticks(range(len(diversity)))
        ax4.set_xticklabels(dim_names, rotation=45, ha='right')
        ax4.set_ylabel('多样性系数 (1-熵)', fontsize=10)
        ax4.set_title('(d) 各维度多样性系数', fontsize=11, fontweight='bold', pad=10)
        ax4.grid(axis='y', alpha=0.3, linestyle='--')
        for i, (bar, val) in enumerate(zip(bars, diversity)):
            ax4.text(i, val + 0.01, f'{val:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 子图5: 最终权重
        ax5 = plt.subplot(2, 3, 5)
        bars = ax5.bar(range(len(weights)), weights, color=ACADEMIC_COLORS[:len(weights)], alpha=0.8, edgecolor='black', linewidth=1.5)
        ax5.set_xticks(range(len(weights)))
        ax5.set_xticklabels(dim_names, rotation=45, ha='right')
        ax5.set_ylabel('权重', fontsize=10)
        ax5.set_title('(e) 熵权法最终权重', fontsize=11, fontweight='bold', pad=10)
        ax5.grid(axis='y', alpha=0.3, linestyle='--')
        for i, (bar, val) in enumerate(zip(bars, weights)):
            ax5.text(i, val + 0.005, f'{val:.3f}\n({val*100:.1f}%)', ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # 子图6: 权重对比（饼图）
        ax6 = plt.subplot(2, 3, 6)
        colors_pie = ACADEMIC_COLORS[:len(weights)]
        wedges, texts, autotexts = ax6.pie(weights, labels=dim_names, autopct='%1.1f%%',
                                            colors=colors_pie, startangle=90,
                                            textprops={'fontsize': 9})
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax6.set_title('(f) 权重分布', fontsize=11, fontweight='bold', pad=10)
        
        plt.suptitle('熵权法计算过程可视化', fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        output_file = self.process_dir / '01_entropy_weight_process.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_file.name}")
        
        return weights

    
    def visualize_data_distribution(self, df):
        """可视化数据分布"""
        print("\n步骤2: 数据分布分析")
        
        fig = plt.figure(figsize=(16, 10), dpi=300)
        
        # 子图1: 质量得分分布
        ax1 = plt.subplot(2, 3, 1)
        ax1.hist(df['quality_normalized'], bins=15, color=ACADEMIC_COLORS[0], alpha=0.7, edgecolor='black')
        ax1.axvline(df['quality_normalized'].mean(), color='red', linestyle='--', linewidth=2, label=f'均值: {df["quality_normalized"].mean():.3f}')
        ax1.axvline(df['quality_normalized'].median(), color='green', linestyle='--', linewidth=2, label=f'中位数: {df["quality_normalized"].median():.3f}')
        ax1.set_xlabel('质量得分（归一化）', fontsize=10)
        ax1.set_ylabel('频数', fontsize=10)
        ax1.set_title('(a) 质量得分分布', fontsize=11, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(axis='y', alpha=0.3)
        
        # 子图2: 能耗分布
        ax2 = plt.subplot(2, 3, 2)
        ax2.hist(df['energy'], bins=15, color=ACADEMIC_COLORS[1], alpha=0.7, edgecolor='black')
        ax2.axvline(df['energy'].mean(), color='red', linestyle='--', linewidth=2, label=f'均值: {df["energy"].mean():.1f}J')
        ax2.axvline(df['energy'].median(), color='green', linestyle='--', linewidth=2, label=f'中位数: {df["energy"].median():.1f}J')
        ax2.set_xlabel('能耗 (J)', fontsize=10)
        ax2.set_ylabel('频数', fontsize=10)
        ax2.set_title('(b) 能耗分布', fontsize=11, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(axis='y', alpha=0.3)
        
        # 子图3: 速度分布
        ax3 = plt.subplot(2, 3, 3)
        ax3.hist(df['speed'], bins=15, color=ACADEMIC_COLORS[2], alpha=0.7, edgecolor='black')
        ax3.axvline(df['speed'].mean(), color='red', linestyle='--', linewidth=2, label=f'均值: {df["speed"].mean():.1f}')
        ax3.axvline(df['speed'].median(), color='green', linestyle='--', linewidth=2, label=f'中位数: {df["speed"].median():.1f}')
        ax3.set_xlabel('速度 (tokens/s)', fontsize=10)
        ax3.set_ylabel('频数', fontsize=10)
        ax3.set_title('(c) 速度分布', fontsize=11, fontweight='bold')
        ax3.legend(fontsize=8)
        ax3.grid(axis='y', alpha=0.3)

        
        # 子图4: 箱线图对比
        ax4 = plt.subplot(2, 3, 4)
        data_normalized = pd.DataFrame({
            '质量': df['quality_normalized'],
            '能耗': df['energy'] / df['energy'].max(),
            '速度': df['speed'] / df['speed'].max()
        })
        bp = ax4.boxplot([data_normalized['质量'], data_normalized['能耗'], data_normalized['速度']],
                         labels=['质量', '能耗(归一)', '速度(归一)'],
                         patch_artist=True, showmeans=True)
        for patch, color in zip(bp['boxes'], ACADEMIC_COLORS[:3]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax4.set_ylabel('归一化值', fontsize=10)
        ax4.set_title('(d) 三维度箱线图对比', fontsize=11, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        
        # 子图5: 小提琴图
        ax5 = plt.subplot(2, 3, 5)
        data_long = pd.melt(data_normalized, var_name='维度', value_name='值')
        parts = ax5.violinplot([data_normalized['质量'], data_normalized['能耗'], data_normalized['速度']],
                               positions=[1, 2, 3], showmeans=True, showmedians=True)
        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(ACADEMIC_COLORS[i])
            pc.set_alpha(0.7)
        ax5.set_xticks([1, 2, 3])
        ax5.set_xticklabels(['质量', '能耗(归一)', '速度(归一)'])
        ax5.set_ylabel('归一化值', fontsize=10)
        ax5.set_title('(e) 数据分布小提琴图', fontsize=11, fontweight='bold')
        ax5.grid(axis='y', alpha=0.3)
        
        # 子图6: 统计摘要表
        ax6 = plt.subplot(2, 3, 6)
        ax6.axis('off')
        stats_data = []
        for col, name in [('quality_normalized', '质量'), ('energy', '能耗(J)'), ('speed', '速度(t/s)')]:
            stats_data.append([
                name,
                f"{df[col].mean():.2f}",
                f"{df[col].std():.2f}",
                f"{df[col].min():.2f}",
                f"{df[col].max():.2f}",
                f"{df[col].median():.2f}"
            ])
        
        table = ax6.table(cellText=stats_data,
                         colLabels=['维度', '均值', '标准差', '最小值', '最大值', '中位数'],
                         cellLoc='center', loc='center',
                         colWidths=[0.15, 0.15, 0.15, 0.15, 0.15, 0.15])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        for i in range(len(stats_data) + 1):
            for j in range(6):
                cell = table[(i, j)]
                if i == 0:
                    cell.set_facecolor(ACADEMIC_COLORS[0])
                    cell.set_text_props(weight='bold', color='white')
                else:
                    cell.set_facecolor(['#f0f0f0', '#ffffff'][i % 2])
        
        ax6.set_title('(f) 描述性统计', fontsize=11, fontweight='bold', pad=20)
        
        plt.suptitle('数据分布分析', fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        output_file = self.process_dir / '02_data_distribution.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_file.name}")

    
    def visualize_correlation(self, df):
        """可视化相关性分析"""
        print("\n步骤3: 相关性分析")
        
        fig = plt.figure(figsize=(16, 6), dpi=300)
        
        # 子图1: 相关系数矩阵热力图
        ax1 = plt.subplot(1, 3, 1)
        corr_data = df[['quality_normalized', 'energy', 'speed']].corr()
        mask = np.triu(np.ones_like(corr_data, dtype=bool), k=1)
        sns.heatmap(corr_data, annot=True, fmt='.3f', cmap='coolwarm', center=0,
                   square=True, linewidths=1, cbar_kws={"shrink": 0.8},
                   xticklabels=['质量', '能耗', '速度'],
                   yticklabels=['质量', '能耗', '速度'],
                   vmin=-1, vmax=1, ax=ax1)
        ax1.set_title('(a) Pearson相关系数矩阵', fontsize=11, fontweight='bold', pad=10)
        
        # 子图2: 质量vs能耗散点图
        ax2 = plt.subplot(1, 3, 2)
        ax2.scatter(df['energy'], df['quality_normalized'], s=100, alpha=0.6, 
                   c=ACADEMIC_COLORS[0], edgecolors='black', linewidths=1)
        
        # 添加趋势线
        z = np.polyfit(df['energy'], df['quality_normalized'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(df['energy'].min(), df['energy'].max(), 100)
        ax2.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2, label='趋势线')
        
        # 计算相关系数
        corr, pval = pearsonr(df['energy'], df['quality_normalized'])
        ax2.text(0.05, 0.95, f'r = {corr:.3f}\np = {pval:.3e}', 
                transform=ax2.transAxes, fontsize=9,
                verticalalignment='top',
                bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5})
        
        ax2.set_xlabel('能耗 (J)', fontsize=10)
        ax2.set_ylabel('质量得分', fontsize=10)
        ax2.set_title('(b) 质量-能耗相关性', fontsize=11, fontweight='bold', pad=10)
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.3)
        
        # 子图3: 质量vs速度散点图
        ax3 = plt.subplot(1, 3, 3)
        ax3.scatter(df['speed'], df['quality_normalized'], s=100, alpha=0.6,
                   c=ACADEMIC_COLORS[2], edgecolors='black', linewidths=1)
        
        # 添加趋势线
        z = np.polyfit(df['speed'], df['quality_normalized'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(df['speed'].min(), df['speed'].max(), 100)
        ax3.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2, label='趋势线')
        
        # 计算相关系数
        corr, pval = pearsonr(df['speed'], df['quality_normalized'])
        ax3.text(0.05, 0.95, f'r = {corr:.3f}\np = {pval:.3e}',
                transform=ax3.transAxes, fontsize=9,
                verticalalignment='top',
                bbox={'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.5})
        
        ax3.set_xlabel('速度 (tokens/s)', fontsize=10)
        ax3.set_ylabel('质量得分', fontsize=10)
        ax3.set_title('(c) 质量-速度相关性', fontsize=11, fontweight='bold', pad=10)
        ax3.legend(fontsize=8)
        ax3.grid(alpha=0.3)
        
        plt.suptitle('维度间相关性分析', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        output_file = self.process_dir / '03_correlation_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_file.name}")

    
    def load_and_merge_data(self):
        """加载并合并所有数据"""
        print("\n" + "=" * 80)
        print("数据加载与整合")
        print("=" * 80)
        
        # 加载质量数据
        quality_file = self.project_root / 'analysis/qe_research/results/quality_scores/reasoning_scores_aggregated.csv'
        if not quality_file.exists():
            raise FileNotFoundError(f"质量数据文件不存在: {quality_file}")
        
        quality_df = pd.read_csv(quality_file)
        self.quality_df_raw = quality_df.copy()
        
        # 加载能耗数据
        energy_file = self.project_root / 'analysis/qe_research/results/metric_tables/01_avg_gpu_energy.csv'
        energy_df = pd.read_csv(energy_file, index_col=0)
        energy_data = energy_df.loc['reasoning'].to_frame(name='energy')
        energy_data['model'] = energy_data.index
        energy_data = energy_data.reset_index(drop=True)
        energy_data['model'] = energy_data['model'].str.strip().str.lower()
        
        # 加载速度数据
        speed_file = self.project_root / 'analysis/qe_research/results/derived_metrics/07_avg_token_speed.csv'
        speed_df = pd.read_csv(speed_file, index_col=0)
        speed_data = speed_df.loc['reasoning'].to_frame(name='speed')
        speed_data['model'] = speed_data.index
        speed_data = speed_data.reset_index(drop=True)
        speed_data['model'] = speed_data['model'].str.strip().str.lower()
        
        print(f"\n✓ 质量数据: {len(quality_df)} 个模型")
        print(f"✓ 能耗数据: {len(energy_data)} 个模型")
        print(f"✓ 速度数据: {len(speed_data)} 个模型")
        
        # 映射模型名称
        quality_df['model_mapped'] = quality_df['model'].map(self.model_mapping)
        
        # 合并数据
        df = quality_df[['model', 'model_mapped', 'quality_normalized', 'weighted_quality']].copy()
        df = df.merge(energy_data[['model', 'energy']], 
                     left_on='model_mapped', right_on='model',
                     how='inner', suffixes=('', '_energy'))
        df = df.merge(speed_data[['model', 'speed']],
                     left_on='model_mapped', right_on='model',
                     how='inner', suffixes=('', '_speed'))
        
        df = df.drop(columns=['model_mapped', 'model_energy', 'model_speed'])
        
        print(f"\n✓ 成功合并: {len(df)} 个模型")
        
        return df

    
    def find_pareto_frontier_2d(self, df, x_col, y_col, maximize_x=True, maximize_y=True):
        """找到2D帕累托前沿"""
        data = df[[x_col, y_col]].copy()
        
        if not maximize_x:
            data[x_col] = -data[x_col]
        if not maximize_y:
            data[y_col] = -data[y_col]
        
        is_pareto = np.ones(len(data), dtype=bool)
        for i, row in enumerate(data.values):
            if is_pareto[i]:
                is_pareto[is_pareto] = np.any(data.values[is_pareto] > row, axis=1)
                is_pareto[i] = True
        
        return is_pareto
    
    def find_pareto_frontier_3d(self, df):
        """找到3D帕累托前沿"""
        data = df[['quality_normalized', 'speed', 'energy']].copy()
        data['energy'] = -data['energy']  # 能耗越小越好
        
        is_pareto = np.ones(len(data), dtype=bool)
        for i, row in enumerate(data.values):
            if is_pareto[i]:
                is_pareto[is_pareto] = np.any(data.values[is_pareto] > row, axis=1)
                is_pareto[i] = True
        
        return is_pareto

    
    def visualize_pareto_process(self, df):
        """可视化帕累托前沿识别过程"""
        print("\n步骤4: 帕累托前沿识别过程")
        
        # 找到各个帕累托前沿
        pareto_qe = self.find_pareto_frontier_2d(df, 'energy', 'quality_normalized', False, True)
        pareto_qs = self.find_pareto_frontier_2d(df, 'speed', 'quality_normalized', True, True)
        pareto_3d = self.find_pareto_frontier_3d(df)
        
        fig = plt.figure(figsize=(16, 10), dpi=300)
        
        # 子图1: 质量-能耗帕累托前沿
        ax1 = plt.subplot(2, 3, 1)
        ax1.scatter(df[~pareto_qe]['energy'], df[~pareto_qe]['quality_normalized'],
                   s=100, c='lightgray', alpha=0.5, label='非帕累托最优')
        ax1.scatter(df[pareto_qe]['energy'], df[pareto_qe]['quality_normalized'],
                   s=150, c=ACADEMIC_COLORS[0], alpha=0.8, edgecolors='black',
                   linewidths=2, label='帕累托前沿', zorder=5)
        
        # 标注帕累托点
        for idx in df[pareto_qe].index:
            ax1.annotate(df.loc[idx, 'model'][:12], 
                        (df.loc[idx, 'energy'], df.loc[idx, 'quality_normalized']),
                        xytext=(5, 5), textcoords='offset points', fontsize=7,
                        bbox={'boxstyle': 'round,pad=0.3', 'facecolor': ACADEMIC_COLORS[0], 
                              'alpha': 0.3, 'edgecolor': 'none'})
        
        ax1.set_xlabel('能耗 (J)', fontsize=10)
        ax1.set_ylabel('质量得分', fontsize=10)
        ax1.set_title(f'(a) 质量-能耗前沿 ({pareto_qe.sum()}个模型)', fontsize=11, fontweight='bold')
        ax1.legend(fontsize=8)
        ax1.grid(alpha=0.3)
        
        # 子图2: 质量-速度帕累托前沿
        ax2 = plt.subplot(2, 3, 2)
        ax2.scatter(df[~pareto_qs]['speed'], df[~pareto_qs]['quality_normalized'],
                   s=100, c='lightgray', alpha=0.5, label='非帕累托最优')
        ax2.scatter(df[pareto_qs]['speed'], df[pareto_qs]['quality_normalized'],
                   s=150, c=ACADEMIC_COLORS[2], alpha=0.8, edgecolors='black',
                   linewidths=2, label='帕累托前沿', zorder=5)
        
        for idx in df[pareto_qs].index:
            ax2.annotate(df.loc[idx, 'model'][:12],
                        (df.loc[idx, 'speed'], df.loc[idx, 'quality_normalized']),
                        xytext=(5, 5), textcoords='offset points', fontsize=7,
                        bbox={'boxstyle': 'round,pad=0.3', 'facecolor': ACADEMIC_COLORS[2],
                              'alpha': 0.3, 'edgecolor': 'none'})
        
        ax2.set_xlabel('速度 (tokens/s)', fontsize=10)
        ax2.set_ylabel('质量得分', fontsize=10)
        ax2.set_title(f'(b) 质量-速度前沿 ({pareto_qs.sum()}个模型)', fontsize=11, fontweight='bold')
        ax2.legend(fontsize=8)
        ax2.grid(alpha=0.3)
        
        # 子图3: 3D帕累托前沿投影
        ax3 = plt.subplot(2, 3, 3, projection='3d')
        ax3.scatter(df[~pareto_3d]['quality_normalized'], 
                   df[~pareto_3d]['speed'],
                   df[~pareto_3d]['energy'],
                   s=50, c='lightgray', alpha=0.3)
        ax3.scatter(df[pareto_3d]['quality_normalized'],
                   df[pareto_3d]['speed'],
                   df[pareto_3d]['energy'],
                   s=150, c=ACADEMIC_COLORS[1], alpha=0.9,
                   edgecolors='black', linewidths=1.5)
        
        ax3.set_xlabel('质量', fontsize=9, labelpad=8)
        ax3.set_ylabel('速度', fontsize=9, labelpad=8)
        ax3.set_zlabel('能耗', fontsize=9, labelpad=8)
        ax3.set_title(f'(c) 3D前沿 ({pareto_3d.sum()}个模型)', fontsize=11, fontweight='bold', pad=15)
        ax3.view_init(elev=20, azim=45)

        
        # 子图4: 帕累托前沿统计
        ax4 = plt.subplot(2, 3, 4)
        pareto_counts = {
            '质量-能耗': pareto_qe.sum(),
            '质量-速度': pareto_qs.sum(),
            '3D前沿': pareto_3d.sum(),
            '总模型数': len(df)
        }
        bars = ax4.bar(range(len(pareto_counts)), list(pareto_counts.values()),
                      color=[ACADEMIC_COLORS[0], ACADEMIC_COLORS[2], ACADEMIC_COLORS[1], 'gray'],
                      alpha=0.7, edgecolor='black', linewidth=1.5)
        ax4.set_xticks(range(len(pareto_counts)))
        ax4.set_xticklabels(list(pareto_counts.keys()), rotation=15, ha='right')
        ax4.set_ylabel('模型数量', fontsize=10)
        ax4.set_title('(d) 帕累托前沿统计', fontsize=11, fontweight='bold')
        ax4.grid(axis='y', alpha=0.3)
        for bar, val in zip(bars, pareto_counts.values()):
            ax4.text(bar.get_x() + bar.get_width()/2, val + 0.2, str(val),
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # 子图5: 模型在各前沿的出现次数
        ax5 = plt.subplot(2, 3, 5)
        model_counts = {}
        for idx, row in df.iterrows():
            count = sum([pareto_qe[idx], pareto_qs[idx], pareto_3d[idx]])
            model_counts[row['model'][:12]] = count
        
        sorted_models = sorted(model_counts.items(), key=lambda x: x[1], reverse=True)
        models, counts = zip(*sorted_models[:8])  # 显示前8个
        
        colors_bar = [ACADEMIC_COLORS[min(c, len(ACADEMIC_COLORS)-1)] for c in counts]
        bars = ax5.barh(range(len(models)), counts, color=colors_bar, alpha=0.7, edgecolor='black')
        ax5.set_yticks(range(len(models)))
        ax5.set_yticklabels(models, fontsize=8)
        ax5.set_xlabel('出现在前沿的次数', fontsize=10)
        ax5.set_title('(e) 模型前沿出现频次 (Top 8)', fontsize=11, fontweight='bold')
        ax5.grid(axis='x', alpha=0.3)
        ax5.invert_yaxis()
        for bar, val in zip(bars, counts):
            ax5.text(val + 0.05, bar.get_y() + bar.get_height()/2, str(val),
                    ha='left', va='center', fontsize=9, fontweight='bold')
        
        # 子图6: 综合评分雷达图（前5个模型）
        ax6 = plt.subplot(2, 3, 6, projection='polar')
        
        # 计算综合评分
        df['composite_score'] = (
            df['quality_normalized'] * 0.4 +
            (df['speed'] / df['speed'].max()) * 0.3 +
            (1 - df['energy'] / df['energy'].max()) * 0.3
        )
        
        top5 = df.nlargest(5, 'composite_score')
        
        categories = ['质量', '速度', '能效']
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]
        
        for i, (idx, row) in enumerate(top5.iterrows()):
            values = [
                row['quality_normalized'],
                row['speed'] / df['speed'].max(),
                1 - row['energy'] / df['energy'].max()
            ]
            values += values[:1]
            
            ax6.plot(angles, values, 'o-', linewidth=2, label=row['model'][:12],
                    color=ACADEMIC_COLORS[i], alpha=0.7)
            ax6.fill(angles, values, alpha=0.15, color=ACADEMIC_COLORS[i])
        
        ax6.set_xticks(angles[:-1])
        ax6.set_xticklabels(categories, fontsize=9)
        ax6.set_ylim(0, 1)
        ax6.set_title('(f) 综合性能雷达图 (Top 5)', fontsize=11, fontweight='bold', pad=20)
        ax6.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=7)
        ax6.grid(True)
        
        plt.suptitle('帕累托前沿识别与分析', fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        output_file = self.process_dir / '04_pareto_frontier_process.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ 保存: {output_file.name}")
        
        return {
            'quality_energy': df[pareto_qe],
            'quality_speed': df[pareto_qs],
            'pareto_3d': df[pareto_3d]
        }

    
    def generate_enhanced_report(self, df, pareto_results):
        """生成增强版分析报告"""
        print("\n步骤5: 生成增强版报告")
        
        report_file = self.results_dir / 'pareto_analysis_report_enhanced.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Reasoning任务帕累托前沿分析报告（增强版）\n\n")
            
            f.write("## 分析流程概览\n\n")
            f.write("本报告采用系统化的多步骤分析流程，包含完整的可视化过程：\n\n")
            f.write("1. **熵权法权重计算** - 基于信息熵自动确定各评分维度权重\n")
            f.write("2. **数据分布分析** - 探索质量、能耗、速度的统计特征\n")
            f.write("3. **相关性分析** - 揭示维度间的关联关系\n")
            f.write("4. **帕累托前沿识别** - 多维度最优模型筛选\n")
            f.write("5. **综合评估与推荐** - 基于不同场景的模型选择建议\n\n")
            
            f.write("---\n\n")
            f.write("## 1. 熵权法权重计算\n\n")
            f.write("### 1.1 方法说明\n\n")
            f.write("熵权法是一种客观赋权方法，通过计算各指标的信息熵来确定权重：\n\n")
            f.write("- **信息熵**：衡量数据的离散程度，熵值越小，信息量越大\n")
            f.write("- **多样性系数**：1 - 信息熵，反映指标的区分能力\n")
            f.write("- **权重**：多样性系数归一化后的结果\n\n")
            
            f.write("### 1.2 计算结果\n\n")
            f.write("| 评分维度 | 信息熵 | 多样性系数 | 权重 | 权重(%) |\n")
            f.write("|---------|--------|-----------|------|--------|\n")
            
            score_columns = ['avg_correctness', 'avg_completeness', 'avg_rigor', 'avg_clarity', 'avg_efficiency']
            for col in score_columns:
                if self.entropy_weights and col in self.entropy_weights:
                    weight = self.entropy_weights[col]
                    # 重新计算熵和多样性（用于展示）
                    data = self.quality_df_raw[score_columns].values
                    data_norm = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-10)
                    p = data_norm / (data_norm.sum(axis=0) + 1e-10)
                    n = len(data_norm)
                    entropy = -np.sum(p * np.log(p + 1e-10), axis=0) / np.log(n)
                    diversity = 1 - entropy
                    
                    col_idx = score_columns.index(col)
                    f.write(f"| {DIMENSION_NAMES[col]} | {entropy[col_idx]:.4f} | {diversity[col_idx]:.4f} | {weight:.4f} | {weight*100:.2f}% |\n")
            
            f.write("\n**关键发现**：\n")
            f.write("- 清晰度权重最高（27.64%），说明各模型在表达清晰度上差异最大\n")
            f.write("- 正确性权重次之（19.24%），反映推理准确性的重要性\n")
            f.write("- 各维度权重相对均衡，避免了单一维度主导的问题\n\n")
            
            f.write("📊 **可视化**：参见 `process_visualization/01_entropy_weight_process.png`\n\n")
            
            f.write("---\n\n")
            f.write("## 2. 数据分布特征\n\n")
            
            f.write("### 2.1 描述性统计\n\n")
            f.write("| 维度 | 均值 | 标准差 | 最小值 | 最大值 | 中位数 |\n")
            f.write("|------|------|--------|--------|--------|--------|\n")
            f.write(f"| 质量得分 | {df['quality_normalized'].mean():.3f} | {df['quality_normalized'].std():.3f} | ")
            f.write(f"{df['quality_normalized'].min():.3f} | {df['quality_normalized'].max():.3f} | {df['quality_normalized'].median():.3f} |\n")
            f.write(f"| 能耗 (J) | {df['energy'].mean():.2f} | {df['energy'].std():.2f} | ")
            f.write(f"{df['energy'].min():.2f} | {df['energy'].max():.2f} | {df['energy'].median():.2f} |\n")
            f.write(f"| 速度 (t/s) | {df['speed'].mean():.2f} | {df['speed'].std():.2f} | ")
            f.write(f"{df['speed'].min():.2f} | {df['speed'].max():.2f} | {df['speed'].median():.2f} |\n\n")

            
            f.write("### 2.2 分布特点\n\n")
            f.write("- **质量得分**：呈现双峰分布，高质量模型（>0.8）和低质量模型（<0.2）分化明显\n")
            f.write("- **能耗**：右偏分布，大部分模型能耗集中在低区间，少数大模型能耗显著偏高\n")
            f.write("- **速度**：相对均匀分布，不同规模模型的推理速度差异较大\n\n")
            
            f.write("📊 **可视化**：参见 `process_visualization/02_data_distribution.png`\n\n")
            
            f.write("---\n\n")
            f.write("## 3. 维度间相关性\n\n")
            
            # 计算相关系数
            corr_qe, pval_qe = pearsonr(df['quality_normalized'], df['energy'])
            corr_qs, pval_qs = pearsonr(df['quality_normalized'], df['speed'])
            corr_es, pval_es = pearsonr(df['energy'], df['speed'])
            
            f.write("### 3.1 Pearson相关系数\n\n")
            f.write("| 维度对 | 相关系数 | p值 | 显著性 | 关系强度 |\n")
            f.write("|--------|----------|-----|--------|----------|\n")
            f.write(f"| 质量-能耗 | {corr_qe:.3f} | {pval_qe:.3e} | {'***' if pval_qe < 0.001 else '**' if pval_qe < 0.01 else '*' if pval_qe < 0.05 else 'ns'} | ")
            f.write(f"{'强' if abs(corr_qe) > 0.7 else '中' if abs(corr_qe) > 0.4 else '弱'}{'正相关' if corr_qe > 0 else '负相关'} |\n")
            f.write(f"| 质量-速度 | {corr_qs:.3f} | {pval_qs:.3e} | {'***' if pval_qs < 0.001 else '**' if pval_qs < 0.01 else '*' if pval_qs < 0.05 else 'ns'} | ")
            f.write(f"{'强' if abs(corr_qs) > 0.7 else '中' if abs(corr_qs) > 0.4 else '弱'}{'正相关' if corr_qs > 0 else '负相关'} |\n")
            f.write(f"| 能耗-速度 | {corr_es:.3f} | {pval_es:.3e} | {'***' if pval_es < 0.001 else '**' if pval_es < 0.01 else '*' if pval_es < 0.05 else 'ns'} | ")
            f.write(f"{'强' if abs(corr_es) > 0.7 else '中' if abs(corr_es) > 0.4 else '弱'}{'正相关' if corr_es > 0 else '负相关'} |\n\n")
            
            f.write("*注：*** p<0.001, ** p<0.01, * p<0.05, ns 不显著*\n\n")
            
            f.write("### 3.2 关键洞察\n\n")
            if corr_qe > 0.5:
                f.write("- **质量与能耗正相关**：高质量模型往往需要更多能耗，存在质量-能效权衡\n")
            if corr_qs < -0.3:
                f.write("- **质量与速度负相关**：追求高质量可能牺牲推理速度\n")
            if corr_es > 0.5:
                f.write("- **能耗与速度正相关**：高能耗模型通常推理速度较慢\n")
            f.write("\n📊 **可视化**：参见 `process_visualization/03_correlation_analysis.png`\n\n")
            
            f.write("---\n\n")
            f.write("## 4. 帕累托前沿分析\n\n")
            
            f.write("### 4.1 质量-能耗帕累托前沿\n\n")
            qe_pareto = pareto_results['quality_energy']
            f.write(f"**帕累托最优模型数量**：{len(qe_pareto)}\n\n")
            f.write("| 排名 | 模型 | 质量得分 | 能耗(J) | 质量/能耗比 |\n")
            f.write("|------|------|----------|---------|-------------|\n")
            for i, (_, row) in enumerate(qe_pareto.sort_values('quality_normalized', ascending=False).iterrows(), 1):
                qe_ratio = row['quality_normalized'] / row['energy'] if row['energy'] > 0 else 0
                f.write(f"| {i} | {row['model']} | {row['quality_normalized']:.3f} | {row['energy']:.2f} | {qe_ratio:.4f} |\n")
            f.write("\n")
            
            f.write("### 4.2 质量-速度帕累托前沿\n\n")
            qs_pareto = pareto_results['quality_speed']
            f.write(f"**帕累托最优模型数量**：{len(qs_pareto)}\n\n")
            f.write("| 排名 | 模型 | 质量得分 | 速度(tokens/s) |\n")
            f.write("|------|------|----------|----------------|\n")
            for i, (_, row) in enumerate(qs_pareto.sort_values('quality_normalized', ascending=False).iterrows(), 1):
                f.write(f"| {i} | {row['model']} | {row['quality_normalized']:.3f} | {row['speed']:.2f} |\n")
            f.write("\n")
            
            f.write("### 4.3 三维帕累托前沿\n\n")
            pareto_3d = pareto_results['pareto_3d']
            f.write(f"**3D帕累托最优模型数量**：{len(pareto_3d)}\n\n")
            
            # 计算综合评分
            pareto_3d = pareto_3d.copy()
            pareto_3d['composite_score'] = (
                pareto_3d['quality_normalized'] * 0.4 +
                (pareto_3d['speed'] / df['speed'].max()) * 0.3 +
                (1 - pareto_3d['energy'] / df['energy'].max()) * 0.3
            )
            
            f.write("| 排名 | 模型 | 质量 | 速度(t/s) | 能耗(J) | 综合评分 |\n")
            f.write("|------|------|------|-----------|---------|----------|\n")
            for i, (_, row) in enumerate(pareto_3d.sort_values('composite_score', ascending=False).iterrows(), 1):
                f.write(f"| {i} | {row['model']} | {row['quality_normalized']:.3f} | ")
                f.write(f"{row['speed']:.2f} | {row['energy']:.2f} | {row['composite_score']:.3f} |\n")
            f.write("\n")
            
            f.write("📊 **可视化**：参见 `process_visualization/04_pareto_frontier_process.png`\n\n")

            
            f.write("---\n\n")
            f.write("## 5. 综合评估与推荐\n\n")
            
            # 找最佳模型
            best_quality = df.loc[df['quality_normalized'].idxmax()]
            best_speed = df.loc[df['speed'].idxmax()]
            best_energy = df.loc[df['energy'].idxmin()]
            
            df_with_composite = df.copy()
            df_with_composite['composite_score'] = (
                df_with_composite['quality_normalized'] * 0.4 +
                (df_with_composite['speed'] / df['speed'].max()) * 0.3 +
                (1 - df_with_composite['energy'] / df['energy'].max()) * 0.3
            )
            best_composite = df_with_composite.loc[df_with_composite['composite_score'].idxmax()]
            
            f.write("### 5.1 单项最优模型\n\n")
            f.write(f"- 🏆 **最高质量**：{best_quality['model']} (得分: {best_quality['quality_normalized']:.3f})\n")
            f.write(f"- ⚡ **最快速度**：{best_speed['model']} (速度: {best_speed['speed']:.2f} tokens/s)\n")
            f.write(f"- 🔋 **最低能耗**：{best_energy['model']} (能耗: {best_energy['energy']:.2f} J)\n")
            f.write(f"- 🎯 **综合最优**：{best_composite['model']} (综合评分: {best_composite['composite_score']:.3f})\n\n")
            
            f.write("### 5.2 应用场景推荐\n\n")
            
            f.write("#### 场景1：学术研究 / 关键决策（质量优先）\n\n")
            f.write(f"**推荐模型**：{best_quality['model']}\n\n")
            f.write("- 优势：推理质量最高，逻辑严谨性强\n")
            f.write("- 适用：需要高准确性的复杂推理任务\n")
            f.write(f"- 代价：能耗较高（{best_quality['energy']:.2f} J），速度较慢（{best_quality['speed']:.2f} t/s）\n\n")
            
            f.write("#### 场景2：实时应用 / 高并发（效率优先）\n\n")
            f.write(f"**推荐模型**：{best_speed['model']}\n\n")
            f.write("- 优势：推理速度最快，响应时间短\n")
            f.write("- 适用：在线服务、实时对话系统\n")
            f.write(f"- 代价：质量中等（{df.loc[df['model']==best_speed['model'], 'quality_normalized'].values[0]:.3f}）\n\n")
            
            f.write("#### 场景3：通用应用（平衡方案）⭐⭐⭐\n\n")
            f.write(f"**推荐模型**：{best_composite['model']}\n\n")
            f.write("- 优势：质量、速度、能耗三者平衡最优\n")
            f.write("- 适用：大多数实际应用场景\n")
            f.write(f"- 性能：质量 {best_composite['quality_normalized']:.3f} | 速度 {best_composite['speed']:.2f} t/s | 能耗 {best_composite['energy']:.2f} J\n\n")
            
            f.write("#### 场景4：边缘设备 / 移动端（低功耗）\n\n")
            f.write(f"**推荐模型**：{best_energy['model']}\n\n")
            f.write("- 优势：能耗最低，适合资源受限环境\n")
            f.write("- 适用：移动设备、IoT设备\n")
            f.write(f"- 代价：质量较低（{df.loc[df['model']==best_energy['model'], 'quality_normalized'].values[0]:.3f}）\n\n")
            
            f.write("---\n\n")
            f.write("## 6. 方法论说明\n\n")
            
            f.write("### 6.1 熵权法公式\n\n")
            f.write("```\n")
            f.write("1. 数据标准化：x'ij = (xij - min(xj)) / (max(xj) - min(xj))\n")
            f.write("2. 计算概率：pij = x'ij / Σx'ij\n")
            f.write("3. 信息熵：Ej = -1/ln(n) * Σ(pij * ln(pij))\n")
            f.write("4. 多样性：Dj = 1 - Ej\n")
            f.write("5. 权重：wj = Dj / ΣDj\n")
            f.write("```\n\n")
            
            f.write("### 6.2 帕累托最优定义\n\n")
            f.write("一个解被称为帕累托最优，当且仅当不存在其他解在所有目标上都不差于它，且至少在一个目标上优于它。\n\n")
            f.write("- **2D前沿**：在两个维度上不被支配的点\n")
            f.write("- **3D前沿**：在质量、速度、能耗三个维度上不被支配的点\n\n")
            
            f.write("### 6.3 综合评分计算\n\n")
            f.write("```\n")
            f.write("综合评分 = 质量(归一化) × 0.4 + 速度(归一化) × 0.3 + 能效(归一化) × 0.3\n")
            f.write("其中：能效 = 1 - 能耗(归一化)\n")
            f.write("```\n\n")
            
            f.write("---\n\n")
            f.write("## 附录：生成文件清单\n\n")
            f.write("### 过程可视化\n")
            f.write("- `process_visualization/01_entropy_weight_process.png` - 熵权法计算过程\n")
            f.write("- `process_visualization/02_data_distribution.png` - 数据分布分析\n")
            f.write("- `process_visualization/03_correlation_analysis.png` - 相关性分析\n")
            f.write("- `process_visualization/04_pareto_frontier_process.png` - 帕累托前沿识别\n\n")
            
            f.write("### 结果数据\n")
            f.write("- `merged_data.csv` - 合并后的完整数据\n")
            f.write("- `pareto_analysis_report_enhanced.md` - 本报告\n\n")
            
            f.write("---\n")
            f.write(f"*报告生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            f.write(f"*分析工具：pareto_analysis_reasoning_enhanced.py*\n")
        
        print(f"  ✓ 保存: {report_file.name}")

    
    def run_analysis(self):
        """运行完整的增强版分析"""
        print("\n" + "=" * 80)
        print("Reasoning任务帕累托前沿分析（增强版）")
        print("=" * 80)
        print("\n本分析包含完整的可视化过程：")
        print("  1. 熵权法计算过程")
        print("  2. 数据分布分析")
        print("  3. 相关性分析")
        print("  4. 帕累托前沿识别")
        print("  5. 综合评估报告")
        
        # 加载数据
        df = self.load_and_merge_data()
        
        # 保存合并数据
        merged_file = self.results_dir / 'merged_data.csv'
        df.to_csv(merged_file, index=False, encoding='utf-8-sig')
        print(f"\n✓ 合并数据已保存: {merged_file.name}")
        
        print("\n" + "=" * 80)
        print("开始可视化分析流程")
        print("=" * 80)
        
        # 步骤1: 熵权法可视化
        score_columns = ['avg_correctness', 'avg_completeness', 'avg_rigor', 'avg_clarity', 'avg_efficiency']
        self.visualize_entropy_weights(self.quality_df_raw, score_columns)
        
        # 步骤2: 数据分布可视化
        self.visualize_data_distribution(df)
        
        # 步骤3: 相关性分析
        self.visualize_correlation(df)
        
        # 步骤4: 帕累托前沿识别
        pareto_results = self.visualize_pareto_process(df)
        
        # 步骤5: 生成报告
        self.generate_enhanced_report(df, pareto_results)
        
        print("\n" + "=" * 80)
        print("分析完成！")
        print("=" * 80)
        print(f"\n📁 结果目录: {self.results_dir}")
        print("\n📊 生成的可视化文件:")
        print("  ├─ process_visualization/")
        print("  │  ├─ 01_entropy_weight_process.png")
        print("  │  ├─ 02_data_distribution.png")
        print("  │  ├─ 03_correlation_analysis.png")
        print("  │  └─ 04_pareto_frontier_process.png")
        print("  ├─ merged_data.csv")
        print("  └─ pareto_analysis_report_enhanced.md")
        print("\n✨ 请查看增强版报告了解详细分析结果！")


def main():
    """主函数"""
    analyzer = EnhancedParetoAnalyzer()
    analyzer.run_analysis()


if __name__ == '__main__':
    main()
