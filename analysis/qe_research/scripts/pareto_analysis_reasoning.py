#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reasoning任务的帕累托前沿分析
Pareto Frontier Analysis for Reasoning Task

分析维度：
1. 质量 (Quality): 基于人工评分的加权质量得分（熵权法）
2. 能耗 (Energy): GPU能耗 (J)
3. 速度 (Speed): Token生成速度 (tokens/s)
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
from scipy.spatial import ConvexHull
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

class ParetoAnalyzer:
    """帕累托前沿分析器"""
    
    def __init__(self):
        self.project_root = project_root
        self.results_dir = self.project_root / 'analysis/qe_research/results/pareto_analysis/reasoning'
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型名称映射表（质量数据 -> 能耗/速度数据）
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
        
    def load_quality_data(self):
        """加载质量数据（从人工评分提取）"""
        quality_file = self.project_root / 'analysis/qe_research/results/quality_scores/reasoning_scores_aggregated.csv'
        
        if not quality_file.exists():
            raise FileNotFoundError(
                f"质量数据文件不存在: {quality_file}\n"
                "请先运行 extract_manual_scores.py 提取质量得分"
            )
        
        df = pd.read_csv(quality_file)
        
        # 标准化模型名称
        df['model'] = df['model'].str.strip().str.lower()
        
        return df
    
    def load_energy_data(self):
        """加载能耗数据"""
        energy_file = self.project_root / 'analysis/qe_research/results/metric_tables/01_avg_gpu_energy.csv'
        
        df = pd.read_csv(energy_file, index_col=0)
        
        # 提取reasoning任务的能耗
        if 'reasoning' not in df.index:
            raise ValueError("能耗数据中未找到reasoning任务")
        
        energy_data = df.loc['reasoning'].to_frame(name='energy')
        energy_data['model'] = energy_data.index
        energy_data = energy_data.reset_index(drop=True)
        
        # 标准化模型名称
        energy_data['model'] = energy_data['model'].str.strip().str.lower()
        
        return energy_data
    
    def load_speed_data(self):
        """加载速度数据"""
        speed_file = self.project_root / 'analysis/qe_research/results/derived_metrics/07_avg_token_speed.csv'
        
        df = pd.read_csv(speed_file, index_col=0)
        
        # 提取reasoning任务的速度
        if 'reasoning' not in df.index:
            raise ValueError("速度数据中未找到reasoning任务")
        
        speed_data = df.loc['reasoning'].to_frame(name='speed')
        speed_data['model'] = speed_data.index
        speed_data = speed_data.reset_index(drop=True)
        
        # 标准化模型名称
        speed_data['model'] = speed_data['model'].str.strip().str.lower()
        
        return speed_data
    
    def merge_data(self):
        """合并所有数据"""
        print("=" * 80)
        print("加载数据...")
        print("=" * 80)
        
        # 加载各维度数据
        quality_df = self.load_quality_data()
        energy_df = self.load_energy_data()
        speed_df = self.load_speed_data()
        
        print(f"\n质量数据: {len(quality_df)} 个模型")
        print(f"能耗数据: {len(energy_df)} 个模型")
        print(f"速度数据: {len(speed_df)} 个模型")
        
        # 映射质量数据的模型名称
        quality_df['model_mapped'] = quality_df['model'].map(self.model_mapping)
        
        # 检查未映射的模型
        unmapped = quality_df[quality_df['model_mapped'].isna()]['model'].tolist()
        if unmapped:
            print(f"\n警告: 以下模型未找到映射: {unmapped}")
        
        # 合并数据（使用映射后的名称）
        df = quality_df[['model', 'model_mapped', 'quality_normalized', 'weighted_quality']].copy()
        df = df.merge(energy_df[['model', 'energy']], 
                     left_on='model_mapped', right_on='model', 
                     how='inner', suffixes=('', '_energy'))
        df = df.merge(speed_df[['model', 'speed']], 
                     left_on='model_mapped', right_on='model', 
                     how='inner', suffixes=('', '_speed'))
        
        # 清理列名，保留原始模型名称
        df = df.drop(columns=['model_mapped', 'model_energy', 'model_speed'])
        
        print(f"\n合并后: {len(df)} 个模型")
        print("\n模型列表:")
        for model in sorted(df['model'].unique()):
            print(f"  - {model}")
        
        return df
    
    def find_pareto_frontier_2d(self, df, x_col, y_col, maximize_x=True, maximize_y=True):
        """
        找到2D帕累托前沿
        
        Parameters:
        -----------
        df : DataFrame
            数据
        x_col : str
            X轴列名
        y_col : str
            Y轴列名
        maximize_x : bool
            是否最大化X轴（True=越大越好，False=越小越好）
        maximize_y : bool
            是否最大化Y轴
        """
        data = df[[x_col, y_col]].copy()
        
        # 转换为最大化问题
        if not maximize_x:
            data[x_col] = -data[x_col]
        if not maximize_y:
            data[y_col] = -data[y_col]
        
        # 找帕累托前沿
        is_pareto = np.ones(len(data), dtype=bool)
        for i, row in enumerate(data.values):
            if is_pareto[i]:
                # 检查是否被其他点支配
                is_pareto[is_pareto] = np.any(data.values[is_pareto] > row, axis=1)
                is_pareto[i] = True
        
        return is_pareto
    
    def find_pareto_frontier_3d(self, df, maximize_quality=True, maximize_speed=True, minimize_energy=True):
        """
        找到3D帕累托前沿
        
        Parameters:
        -----------
        df : DataFrame
            包含quality_normalized, speed, energy的数据
        """
        data = df[['quality_normalized', 'speed', 'energy']].copy()
        
        # 转换为最大化问题
        if minimize_energy:
            data['energy'] = -data['energy']
        
        # 找帕累托前沿
        is_pareto = np.ones(len(data), dtype=bool)
        for i, row in enumerate(data.values):
            if is_pareto[i]:
                # 检查是否被其他点支配
                is_pareto[is_pareto] = np.any(data.values[is_pareto] > row, axis=1)
                is_pareto[i] = True
        
        return is_pareto
    
    def plot_2d_pareto(self, df, x_col, y_col, x_label, y_label, 
                       maximize_x=True, maximize_y=True, filename='pareto_2d.png'):
        """绘制2D帕累托前沿图"""
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        
        # 找帕累托前沿
        is_pareto = self.find_pareto_frontier_2d(df, x_col, y_col, maximize_x, maximize_y)
        
        # 绘制所有点
        ax.scatter(df[~is_pareto][x_col], df[~is_pareto][y_col], 
                  c='lightgray', s=100, alpha=0.6, label='非帕累托最优', zorder=1)
        
        # 绘制帕累托前沿点
        pareto_df = df[is_pareto].copy()
        ax.scatter(pareto_df[x_col], pareto_df[y_col], 
                  c=ACADEMIC_COLORS[0], s=150, alpha=0.8, 
                  edgecolors='black', linewidths=1.5, 
                  label='帕累托前沿', zorder=2)
        
        # 标注模型名称
        for idx, row in df.iterrows():
            if is_pareto[idx]:
                ax.annotate(row['model'], 
                           (row[x_col], row[y_col]),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', 
                                   facecolor=ACADEMIC_COLORS[0], 
                                   alpha=0.3, edgecolor='none'))
            else:
                ax.annotate(row['model'], 
                           (row[x_col], row[y_col]),
                           xytext=(5, 5), textcoords='offset points',
                           fontsize=8, alpha=0.6)
        
        ax.set_xlabel(x_label, fontsize=12, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12, fontweight='bold')
        ax.set_title(f'Reasoning任务帕累托前沿分析\n{y_label} vs {x_label}', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10, loc='best')
        ax.grid(True, alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        output_file = self.results_dir / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  保存图表: {output_file}")
        
        return pareto_df
    
    def plot_3d_pareto(self, df, filename='pareto_3d.png'):
        """绘制3D帕累托前沿图"""
        fig = plt.figure(figsize=(12, 10), dpi=300)
        ax = fig.add_subplot(111, projection='3d')
        
        # 找帕累托前沿
        is_pareto = self.find_pareto_frontier_3d(df)
        
        # 绘制所有点
        ax.scatter(df[~is_pareto]['quality_normalized'], 
                  df[~is_pareto]['speed'], 
                  df[~is_pareto]['energy'],
                  c='lightgray', s=100, alpha=0.4, label='非帕累托最优')
        
        # 绘制帕累托前沿点
        pareto_df = df[is_pareto].copy()
        ax.scatter(pareto_df['quality_normalized'], 
                  pareto_df['speed'], 
                  pareto_df['energy'],
                  c=ACADEMIC_COLORS[1], s=200, alpha=0.9,
                  edgecolors='black', linewidths=1.5,
                  label='帕累托前沿')
        
        # 标注帕累托前沿点
        for idx, row in pareto_df.iterrows():
            ax.text(row['quality_normalized'], row['speed'], row['energy'],
                   row['model'], fontsize=8, fontweight='bold')
        
        ax.set_xlabel('质量得分 (归一化)', fontsize=11, fontweight='bold', labelpad=10)
        ax.set_ylabel('速度 (tokens/s)', fontsize=11, fontweight='bold', labelpad=10)
        ax.set_zlabel('能耗 (J)', fontsize=11, fontweight='bold', labelpad=10)
        ax.set_title('Reasoning任务3D帕累托前沿\n质量-速度-能耗', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(fontsize=10)
        
        # 调整视角
        ax.view_init(elev=20, azim=45)
        
        plt.tight_layout()
        output_file = self.results_dir / filename
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  保存图表: {output_file}")
        
        return pareto_df
    
    def generate_report(self, df, pareto_2d_results, pareto_3d):
        """生成分析报告"""
        report_file = self.results_dir / 'pareto_analysis_report.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Reasoning任务帕累托前沿分析报告\n\n")
            f.write("## 1. 分析概述\n\n")
            f.write("本报告基于人工评分数据（熵权法加权）分析Reasoning任务中模型的质量-能耗-速度权衡关系。\n\n")
            
            f.write("### 1.1 分析维度\n\n")
            f.write("- **质量**: 基于5个维度的人工评分（正确性40%、完整性25%、严谨性20%、清晰度10%、效率5%）\n")
            f.write("- **能耗**: GPU平均能耗 (J)\n")
            f.write("- **速度**: Token生成速度 (tokens/s)\n\n")
            
            f.write("### 1.2 数据统计\n\n")
            f.write(f"- 分析模型数量: {len(df)}\n")
            
            if len(df) == 0:
                f.write("\n**警告**: 没有找到匹配的模型数据，请检查模型名称映射。\n")
                print(f"  保存报告: {report_file}")
                return
            
            f.write(f"- 质量得分范围: {df['quality_normalized'].min():.3f} - {df['quality_normalized'].max():.3f}\n")
            f.write(f"- 能耗范围: {df['energy'].min():.2f} - {df['energy'].max():.2f} J\n")
            f.write(f"- 速度范围: {df['speed'].min():.2f} - {df['speed'].max():.2f} tokens/s\n\n")
            
            f.write("## 2. 帕累托前沿分析\n\n")
            
            # 2D分析
            f.write("### 2.1 质量-能耗帕累托前沿\n\n")
            qe_pareto = pareto_2d_results['quality_energy']
            f.write(f"帕累托最优模型数量: {len(qe_pareto)}\n\n")
            f.write("| 模型 | 质量得分 | 能耗(J) | 质量/能耗比 |\n")
            f.write("|------|----------|---------|-------------|\n")
            for _, row in qe_pareto.sort_values('quality_normalized', ascending=False).iterrows():
                qe_ratio = row['quality_normalized'] / row['energy'] if row['energy'] > 0 else 0
                f.write(f"| {row['model']} | {row['quality_normalized']:.3f} | {row['energy']:.2f} | {qe_ratio:.4f} |\n")
            f.write("\n")
            
            f.write("### 2.2 质量-速度帕累托前沿\n\n")
            qs_pareto = pareto_2d_results['quality_speed']
            f.write(f"帕累托最优模型数量: {len(qs_pareto)}\n\n")
            f.write("| 模型 | 质量得分 | 速度(tokens/s) |\n")
            f.write("|------|----------|----------------|\n")
            for _, row in qs_pareto.sort_values('quality_normalized', ascending=False).iterrows():
                f.write(f"| {row['model']} | {row['quality_normalized']:.3f} | {row['speed']:.2f} |\n")
            f.write("\n")
            
            f.write("### 2.3 速度-能耗帕累托前沿\n\n")
            se_pareto = pareto_2d_results['speed_energy']
            f.write(f"帕累托最优模型数量: {len(se_pareto)}\n\n")
            f.write("| 模型 | 速度(tokens/s) | 能耗(J) | 能效比(tokens/J) |\n")
            f.write("|------|----------------|---------|------------------|\n")
            for _, row in se_pareto.sort_values('speed', ascending=False).iterrows():
                efficiency = row['speed'] / row['energy'] if row['energy'] > 0 else 0
                f.write(f"| {row['model']} | {row['speed']:.2f} | {row['energy']:.2f} | {efficiency:.2f} |\n")
            f.write("\n")
            
            f.write("### 2.4 三维帕累托前沿\n\n")
            f.write(f"3D帕累托最优模型数量: {len(pareto_3d)}\n\n")
            f.write("| 模型 | 质量得分 | 速度(tokens/s) | 能耗(J) | 综合评分 |\n")
            f.write("|------|----------|----------------|---------|----------|\n")
            for _, row in pareto_3d.iterrows():
                # 综合评分：归一化后的加权平均
                composite = (row['quality_normalized'] * 0.4 + 
                           (row['speed'] / df['speed'].max()) * 0.3 + 
                           (1 - row['energy'] / df['energy'].max()) * 0.3)
                f.write(f"| {row['model']} | {row['quality_normalized']:.3f} | {row['speed']:.2f} | {row['energy']:.2f} | {composite:.3f} |\n")
            f.write("\n")
            
            f.write("## 3. 关键发现\n\n")
            
            # 找最佳模型
            best_quality = df.loc[df['quality_normalized'].idxmax()]
            best_speed = df.loc[df['speed'].idxmax()]
            best_energy = df.loc[df['energy'].idxmin()]
            
            f.write(f"- **最高质量**: {best_quality['model']} (质量得分: {best_quality['quality_normalized']:.3f})\n")
            f.write(f"- **最快速度**: {best_speed['model']} (速度: {best_speed['speed']:.2f} tokens/s)\n")
            f.write(f"- **最低能耗**: {best_energy['model']} (能耗: {best_energy['energy']:.2f} J)\n\n")
            
            f.write("## 4. 推荐建议\n\n")
            f.write("根据不同应用场景的优先级选择模型：\n\n")
            f.write("- **质量优先**: 选择质量-能耗帕累托前沿上质量得分最高的模型\n")
            f.write("- **效率优先**: 选择速度-能耗帕累托前沿上能效比最高的模型\n")
            f.write("- **平衡方案**: 选择3D帕累托前沿上综合评分最高的模型\n\n")
            
            f.write("---\n")
            f.write(f"*报告生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        print(f"  保存报告: {report_file}")
    
    def run_analysis(self):
        """运行完整分析"""
        print("\n" + "=" * 80)
        print("Reasoning任务帕累托前沿分析")
        print("=" * 80)
        
        # 加载并合并数据
        df = self.merge_data()
        
        # 保存合并数据
        merged_file = self.results_dir / 'merged_data.csv'
        df.to_csv(merged_file, index=False, encoding='utf-8-sig')
        print(f"\n合并数据已保存: {merged_file}")
        
        print("\n" + "=" * 80)
        print("生成帕累托前沿图表...")
        print("=" * 80)
        
        # 2D帕累托分析
        pareto_2d_results = {}
        
        print("\n1. 质量-能耗帕累托前沿")
        pareto_2d_results['quality_energy'] = self.plot_2d_pareto(
            df, 'energy', 'quality_normalized',
            '能耗 (J)', '质量得分',
            maximize_x=False, maximize_y=True,
            filename='pareto_quality_energy.png'
        )
        
        print("\n2. 质量-速度帕累托前沿")
        pareto_2d_results['quality_speed'] = self.plot_2d_pareto(
            df, 'speed', 'quality_normalized',
            '速度 (tokens/s)', '质量得分',
            maximize_x=True, maximize_y=True,
            filename='pareto_quality_speed.png'
        )
        
        print("\n3. 速度-能耗帕累托前沿")
        pareto_2d_results['speed_energy'] = self.plot_2d_pareto(
            df, 'energy', 'speed',
            '能耗 (J)', '速度 (tokens/s)',
            maximize_x=False, maximize_y=True,
            filename='pareto_speed_energy.png'
        )
        
        print("\n4. 三维帕累托前沿")
        pareto_3d = self.plot_3d_pareto(df, filename='pareto_3d.png')
        
        print("\n" + "=" * 80)
        print("生成分析报告...")
        print("=" * 80)
        
        self.generate_report(df, pareto_2d_results, pareto_3d)
        
        print("\n" + "=" * 80)
        print("分析完成！")
        print("=" * 80)
        print(f"\n结果保存在: {self.results_dir}")
        print("\n生成的文件:")
        print("  - merged_data.csv: 合并后的原始数据")
        print("  - pareto_quality_energy.png: 质量-能耗帕累托图")
        print("  - pareto_quality_speed.png: 质量-速度帕累托图")
        print("  - pareto_speed_energy.png: 速度-能耗帕累托图")
        print("  - pareto_3d.png: 三维帕累托图")
        print("  - pareto_analysis_report.md: 分析报告")

def main():
    analyzer = ParetoAnalyzer()
    analyzer.run_analysis()

if __name__ == '__main__':
    main()
