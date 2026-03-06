"""
翻译任务帕累托前沿分析（增强版）

整合功能：
1. 基础帕累托前沿识别（2D和3D）
2. 定量指标：超体积、间距、GD/IGD、边际效益、拐点
3. 稳健性分析：扰动分析、权重敏感性、交叉验证
4. 决策支持：目标达成度、决策鲁棒性、升级代价量化

数据来源：
- 质量指标：BLEU得分
- 能耗指标：每token能耗（energy_per_token）
- 速度指标：平均token速度（avg_token_speed）
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from collections import Counter
from scipy.spatial.distance import euclidean
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 数据路径
QUALITY_FILE = project_root / 'data' / 'analize' / 'results' / 'translation_quality' / 'translation_quality_summary.csv'
ENERGY_FILE = project_root / 'analysis' / 'qe_research' / 'results' / 'derived_metrics' / '08_energy_per_token.csv'
SPEED_FILE = project_root / 'analysis' / 'qe_research' / 'results' / 'derived_metrics' / '07_avg_token_speed.csv'

# 输出目录
OUTPUT_DIR = project_root / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / 'translation'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class TranslationParetoAnalyzer:
    """翻译任务帕累托前沿分析器（增强版）"""
    
    def __init__(self, df):
        self.data = df
        self.results = {}
        
    # ==================== 基础功能：帕累托前沿识别 ====================
    
    def identify_pareto_frontier_2d(self, x_col, y_col, x_minimize=True, y_minimize=True):
        """识别2D帕累托前沿"""
        n = len(self.data)
        pareto_mask = np.ones(n, dtype=bool)
        
        for i in range(n):
            if not pareto_mask[i]:
                continue
            
            for j in range(n):
                if i == j:
                    continue
                
                x_i, y_i = self.data.iloc[i][x_col], self.data.iloc[i][y_col]
                x_j, y_j = self.data.iloc[j][x_col], self.data.iloc[j][y_col]
                
                x_better = (x_j <= x_i) if x_minimize else (x_j >= x_i)
                x_strictly_better = (x_j < x_i) if x_minimize else (x_j > x_i)
                y_better = (y_j <= y_i) if y_minimize else (y_j >= y_i)
                y_strictly_better = (y_j < y_i) if y_minimize else (y_j > y_i)
                
                if x_better and y_better and (x_strictly_better or y_strictly_better):
                    pareto_mask[i] = False
                    break
        
        return pareto_mask
    
    def identify_pareto_frontier_3d(self):
        """识别3D帕累托前沿（质量最大化，能耗最小化，速度最大化）"""
        n = len(self.data)
        pareto_mask = np.ones(n, dtype=bool)
        
        for i in range(n):
            if not pareto_mask[i]:
                continue
            
            for j in range(n):
                if i == j:
                    continue
                
                q_i, e_i, s_i = self.data.iloc[i]['quality'], self.data.iloc[i]['energy'], self.data.iloc[i]['speed']
                q_j, e_j, s_j = self.data.iloc[j]['quality'], self.data.iloc[j]['energy'], self.data.iloc[j]['speed']
                
                quality_better = q_j >= q_i
                energy_better = e_j <= e_i
                speed_better = s_j >= s_i
                strictly_better = (q_j > q_i) or (e_j < e_i) or (s_j > s_i)
                
                if quality_better and energy_better and speed_better and strictly_better:
                    pareto_mask[i] = False
                    break
        
        return pareto_mask

    
    # ==================== 定量指标计算 ====================
    
    def calculate_hypervolume(self, pareto_mask, x_col, y_col, x_minimize=True, y_minimize=True):
        """计算超体积指标"""
        pareto = self.data[pareto_mask].copy()
        
        if len(pareto) == 0:
            return 0
        
        # 归一化
        x_min, x_max = self.data[x_col].min(), self.data[x_col].max()
        y_min, y_max = self.data[y_col].min(), self.data[y_col].max()
        
        if x_minimize:
            pareto['x_norm'] = 1 - (pareto[x_col] - x_min) / (x_max - x_min) if x_max > x_min else 0
        else:
            pareto['x_norm'] = (pareto[x_col] - x_min) / (x_max - x_min) if x_max > x_min else 0
        
        if y_minimize:
            pareto['y_norm'] = 1 - (pareto[y_col] - y_min) / (y_max - y_min) if y_max > y_min else 0
        else:
            pareto['y_norm'] = (pareto[y_col] - y_min) / (y_max - y_min) if y_max > y_min else 0
        
        pareto = pareto.sort_values('x_norm')
        
        hv = 0
        for i in range(len(pareto)):
            if i == 0:
                width = pareto.iloc[i]['x_norm'] - 0
            else:
                width = pareto.iloc[i]['x_norm'] - pareto.iloc[i-1]['x_norm']
            
            height = pareto.iloc[i]['y_norm']
            hv += width * height
        
        return hv
    
    def calculate_spacing(self, pareto_mask, x_col, y_col):
        """计算间距指标"""
        pareto = self.data[pareto_mask]
        
        if len(pareto) < 2:
            return 0
        
        # 归一化
        x_norm = (pareto[x_col] - self.data[x_col].min()) / (self.data[x_col].max() - self.data[x_col].min())
        y_norm = (pareto[y_col] - self.data[y_col].min()) / (self.data[y_col].max() - self.data[y_col].min())
        
        distances = []
        points = np.column_stack([x_norm, y_norm])
        
        for i in range(len(points)):
            min_dist = float('inf')
            for j in range(len(points)):
                if i != j:
                    dist = np.linalg.norm(points[i] - points[j])
                    min_dist = min(min_dist, dist)
            distances.append(min_dist)
        
        mean_dist = np.mean(distances)
        spacing = np.sqrt(np.mean([(d - mean_dist)**2 for d in distances]))
        
        return spacing

    
    def calculate_gd_igd(self, pareto_mask, x_col, y_col, x_minimize=True, y_minimize=True):
        """
        计算GD（Generational Distance）和IGD（Inverted Generational Distance）
        
        GD: 衡量前沿到理想前沿的平均距离（收敛性）
        IGD: 衡量理想前沿到实际前沿的平均距离（收敛性+分布）
        """
        pareto = self.data[pareto_mask]
        
        if len(pareto) == 0:
            return {'gd': 0, 'igd': 0}
        
        # 归一化
        x_norm = (self.data[x_col] - self.data[x_col].min()) / (self.data[x_col].max() - self.data[x_col].min())
        y_norm = (self.data[y_col] - self.data[y_col].min()) / (self.data[y_col].max() - self.data[y_col].min())
        
        # 构建理想前沿（使用所有数据点的凸包近似）
        all_points = np.column_stack([x_norm, y_norm])
        pareto_points = all_points[pareto_mask]
        
        # GD: 前沿点到理想点的距离
        if x_minimize and y_minimize:
            ideal_point = np.array([0, 0])
        elif not x_minimize and not y_minimize:
            ideal_point = np.array([1, 1])
        elif x_minimize and not y_minimize:
            ideal_point = np.array([0, 1])
        else:
            ideal_point = np.array([1, 0])
        
        gd_distances = [np.linalg.norm(p - ideal_point) for p in pareto_points]
        gd = np.mean(gd_distances) if gd_distances else 0
        
        # IGD: 理想前沿点到实际前沿的距离（使用所有数据点作为参考）
        igd_distances = []
        for point in all_points:
            min_dist = min([np.linalg.norm(point - p) for p in pareto_points])
            igd_distances.append(min_dist)
        igd = np.mean(igd_distances) if igd_distances else 0
        
        return {'gd': gd, 'igd': igd}
    
    def calculate_marginal_benefit(self, pareto_mask, x_col, y_col):
        """计算边际效益曲线"""
        pareto = self.data[pareto_mask].sort_values(x_col).reset_index(drop=True)
        
        if len(pareto) < 2:
            return pd.DataFrame()
        
        marginal_benefits = []
        for i in range(1, len(pareto)):
            delta_x = pareto.loc[i, x_col] - pareto.loc[i-1, x_col]
            delta_y = pareto.loc[i, y_col] - pareto.loc[i-1, y_col]
            
            mb = delta_y / delta_x if delta_x != 0 else 0
            
            marginal_benefits.append({
                'from_model': pareto.loc[i-1, 'model'],
                'to_model': pareto.loc[i, 'model'],
                'delta_x': delta_x,
                'delta_y': delta_y,
                'marginal_benefit': mb
            })
        
        return pd.DataFrame(marginal_benefits)
    
    def find_knee_point(self, pareto_mask, x_col, y_col):
        """识别拐点（最大曲率法）"""
        pareto = self.data[pareto_mask].sort_values(x_col)
        
        if len(pareto) < 3:
            return pareto.iloc[0]['model'] if len(pareto) > 0 else None
        
        # 归一化
        x_norm = (pareto[x_col] - self.data[x_col].min()) / (self.data[x_col].max() - self.data[x_col].min())
        y_norm = (pareto[y_col] - self.data[y_col].min()) / (self.data[y_col].max() - self.data[y_col].min())
        
        pareto_copy = pareto.copy()
        pareto_copy['x_norm'] = x_norm.values
        pareto_copy['y_norm'] = y_norm.values
        pareto_copy = pareto_copy.sort_values('x_norm')
        
        max_curvature = -1
        knee_idx = 0
        
        for i in range(1, len(pareto_copy) - 1):
            p1 = np.array([pareto_copy.iloc[i-1]['x_norm'], pareto_copy.iloc[i-1]['y_norm']])
            p2 = np.array([pareto_copy.iloc[i]['x_norm'], pareto_copy.iloc[i]['y_norm']])
            p3 = np.array([pareto_copy.iloc[i+1]['x_norm'], pareto_copy.iloc[i+1]['y_norm']])
            
            v1 = p2 - p1
            v2 = p3 - p2
            
            if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                cos_angle = np.clip(cos_angle, -1, 1)
                curvature = 1 - cos_angle
                
                if curvature > max_curvature:
                    max_curvature = curvature
                    knee_idx = i
        
        return pareto_copy.iloc[knee_idx]['model']

    
    # ==================== 稳健性分析 ====================
    
    def perturbation_analysis(self, x_col, y_col, x_minimize=True, y_minimize=True, 
                             noise_level=0.05, n_iterations=100):
        """扰动分析：评估前沿对数据噪声的敏感性"""
        print(f"\n{'='*80}")
        print(f"扰动分析：{y_col} vs {x_col}")
        print(f"噪声水平: ±{noise_level*100:.0f}%, 迭代次数: {n_iterations}")
        print(f"{'='*80}")
        
        # 原始前沿
        original_pareto = self.identify_pareto_frontier_2d(x_col, y_col, x_minimize, y_minimize)
        original_models = set(self.data[original_pareto]['model'])
        
        print(f"\n原始帕累托前沿: {len(original_models)} 个模型")
        
        # 扰动分析
        pareto_models_count = Counter()
        consistency_scores = []
        
        np.random.seed(42)
        for i in range(n_iterations):
            # 添加噪声
            noisy_data = self.data.copy()
            noisy_data[x_col] = noisy_data[x_col] * (1 + np.random.uniform(-noise_level, noise_level, len(noisy_data)))
            noisy_data[y_col] = noisy_data[y_col] * (1 + np.random.uniform(-noise_level, noise_level, len(noisy_data)))
            
            # 创建临时分析器
            temp_analyzer = TranslationParetoAnalyzer(noisy_data)
            pareto_mask = temp_analyzer.identify_pareto_frontier_2d(x_col, y_col, x_minimize, y_minimize)
            pareto_models = set(noisy_data[pareto_mask]['model'])
            
            for model in pareto_models:
                pareto_models_count[model] += 1
            
            # 计算Jaccard相似度
            jaccard = len(pareto_models & original_models) / len(pareto_models | original_models)
            consistency_scores.append(jaccard)
        
        # 计算稳定性得分
        stability_scores = {model: count / n_iterations for model, count in pareto_models_count.items()}
        sorted_stability = sorted(stability_scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n稳定性得分（Top 5）:")
        for i, (model, score) in enumerate(sorted_stability[:5], 1):
            rating = "⭐" * int(score * 5 + 0.5)
            in_original = "✓" if model in original_models else "✗"
            print(f"{i}. {model}: {score:.2%} {rating} [{in_original}]")
        
        mean_consistency = np.mean(consistency_scores)
        print(f"\n前沿一致性（Jaccard）: {mean_consistency:.2%} ± {np.std(consistency_scores):.2%}")
        
        return {
            'stability_scores': stability_scores,
            'mean_consistency': mean_consistency,
            'std_consistency': np.std(consistency_scores)
        }
    
    def weight_sensitivity_analysis(self, n_samples=50):
        """权重敏感性分析：验证综合评分的稳定性"""
        print(f"\n{'='*80}")
        print(f"权重敏感性分析")
        print(f"采样数量: {n_samples}")
        print(f"{'='*80}")
        
        best_models = []
        
        np.random.seed(42)
        for i in range(n_samples):
            # 随机生成权重（质量、速度、能效）
            w_quality = np.random.uniform(0.3, 0.5)
            w_speed = np.random.uniform(0.2, 0.4)
            w_energy = 1 - w_quality - w_speed
            
            if w_energy < 0.2 or w_energy > 0.4:
                continue
            
            # 计算综合评分
            df = self.data.copy()
            df['quality_norm'] = (df['quality'] - df['quality'].min()) / (df['quality'].max() - df['quality'].min())
            df['speed_norm'] = (df['speed'] - df['speed'].min()) / (df['speed'].max() - df['speed'].min())
            df['energy_norm'] = 1 - (df['energy'] - df['energy'].min()) / (df['energy'].max() - df['energy'].min())
            
            df['comprehensive_score'] = w_quality * df['quality_norm'] + w_speed * df['speed_norm'] + w_energy * df['energy_norm']
            
            best_model = df.loc[df['comprehensive_score'].idxmax(), 'model']
            best_models.append(best_model)
        
        model_frequency = Counter(best_models)
        
        print(f"\n最优模型频率（Top 5）:")
        for i, (model, count) in enumerate(model_frequency.most_common(5), 1):
            freq = count / len(best_models)
            rating = "⭐" * int(freq * 5 + 0.5)
            print(f"{i}. {model}: {freq:.2%} ({count}/{len(best_models)}) {rating}")
        
        return {'model_frequency': model_frequency}
    
    def cross_validation_analysis(self, n_folds=5):
        """交叉验证：评估前沿的泛化能力"""
        print(f"\n{'='*80}")
        print(f"交叉验证分析（{n_folds}折）")
        print(f"{'='*80}")
        
        n_models = len(self.data)
        indices = np.arange(n_models)
        np.random.seed(42)
        np.random.shuffle(indices)
        
        fold_size = n_models // n_folds
        
        qe_pareto_models = []
        qs_pareto_models = []
        
        for fold in range(n_folds):
            test_indices = indices[fold * fold_size : (fold + 1) * fold_size]
            train_indices = np.concatenate([indices[:fold * fold_size], indices[(fold + 1) * fold_size:]])
            
            train_data = self.data.iloc[train_indices]
            
            # 创建临时分析器
            temp_analyzer = TranslationParetoAnalyzer(train_data)
            
            # 质量-能耗前沿
            qe_mask = temp_analyzer.identify_pareto_frontier_2d('energy', 'quality', x_minimize=True, y_minimize=False)
            qe_pareto = set(train_data[qe_mask]['model'])
            qe_pareto_models.append(qe_pareto)
            
            # 质量-速度前沿
            qs_mask = temp_analyzer.identify_pareto_frontier_2d('speed', 'quality', x_minimize=False, y_minimize=False)
            qs_pareto = set(train_data[qs_mask]['model'])
            qs_pareto_models.append(qs_pareto)
        
        # 计算一致性
        qe_model_counts = Counter()
        for pareto_set in qe_pareto_models:
            for model in pareto_set:
                qe_model_counts[model] += 1
        
        qs_model_counts = Counter()
        for pareto_set in qs_pareto_models:
            for model in pareto_set:
                qs_model_counts[model] += 1
        
        print(f"\n质量-能耗前沿一致性:")
        for model, count in qe_model_counts.most_common(5):
            freq = count / n_folds
            print(f"  {model}: {count}/{n_folds} ({freq:.0%})")
        
        print(f"\n质量-速度前沿一致性:")
        for model, count in qs_model_counts.most_common(5):
            freq = count / n_folds
            print(f"  {model}: {count}/{n_folds} ({freq:.0%})")
        
        return {
            'qe_model_counts': qe_model_counts,
            'qs_model_counts': qs_model_counts
        }

    
    # ==================== 决策支持 ====================
    
    def calculate_objective_achievement(self, pareto_mask, x_col, y_col):
        """计算目标达成度：量化前沿覆盖能力"""
        pareto = self.data[pareto_mask]
        
        # 计算覆盖范围
        x_coverage = (pareto[x_col].max() - pareto[x_col].min()) / (self.data[x_col].max() - self.data[x_col].min())
        y_coverage = (pareto[y_col].max() - pareto[y_col].min()) / (self.data[y_col].max() - self.data[y_col].min())
        
        # 计算前沿点占比
        pareto_ratio = len(pareto) / len(self.data)
        
        # 综合达成度
        achievement = (x_coverage + y_coverage) / 2
        
        return {
            'x_coverage': x_coverage,
            'y_coverage': y_coverage,
            'pareto_ratio': pareto_ratio,
            'achievement': achievement
        }
    
    def identify_robust_solutions(self, stability_scores, threshold=0.7):
        """识别鲁棒解：稳定性高的模型"""
        robust_models = {model: score for model, score in stability_scores.items() if score >= threshold}
        
        print(f"\n鲁棒解识别（稳定性 ≥ {threshold:.0%}）:")
        for model, score in sorted(robust_models.items(), key=lambda x: x[1], reverse=True):
            print(f"  {model}: {score:.2%}")
        
        return robust_models
    
    def quantify_upgrade_cost(self, pareto_mask, x_col, y_col):
        """量化升级代价：提供具体建议"""
        pareto = self.data[pareto_mask].sort_values(x_col).reset_index(drop=True)
        
        if len(pareto) < 2:
            return pd.DataFrame()
        
        upgrade_costs = []
        for i in range(len(pareto) - 1):
            from_model = pareto.loc[i, 'model']
            to_model = pareto.loc[i+1, 'model']
            
            delta_quality = pareto.loc[i+1, y_col] - pareto.loc[i, y_col]
            delta_cost = pareto.loc[i+1, x_col] - pareto.loc[i, x_col]
            
            # 计算性价比
            cost_effectiveness = delta_quality / delta_cost if delta_cost != 0 else 0
            
            # 计算相对提升
            quality_improvement = (delta_quality / pareto.loc[i, y_col]) * 100 if pareto.loc[i, y_col] != 0 else 0
            cost_increase = (delta_cost / pareto.loc[i, x_col]) * 100 if pareto.loc[i, x_col] != 0 else 0
            
            upgrade_costs.append({
                'from_model': from_model,
                'to_model': to_model,
                'delta_quality': delta_quality,
                'delta_cost': delta_cost,
                'cost_effectiveness': cost_effectiveness,
                'quality_improvement_%': quality_improvement,
                'cost_increase_%': cost_increase,
                'recommendation': self._get_upgrade_recommendation(quality_improvement, cost_increase)
            })
        
        return pd.DataFrame(upgrade_costs)
    
    def _get_upgrade_recommendation(self, quality_improvement, cost_increase):
        """生成升级建议"""
        if quality_improvement > 10 and cost_increase < 20:
            return "⭐⭐⭐⭐⭐ 强烈推荐"
        elif quality_improvement > 5 and cost_increase < 30:
            return "⭐⭐⭐⭐ 推荐"
        elif quality_improvement > 2 and cost_increase < 40:
            return "⭐⭐⭐ 可考虑"
        elif quality_improvement > 0:
            return "⭐⭐ 谨慎考虑"
        else:
            return "⭐ 不推荐"

    
    # ==================== 可视化 ====================
    
    def plot_pareto_2d(self, pareto_mask, x_col, y_col, title, filename, 
                       x_label, y_label):
        """绘制2D帕累托前沿图"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        non_pareto = self.data[~pareto_mask]
        ax.scatter(non_pareto[x_col], non_pareto[y_col], 
                  c='lightgray', s=100, alpha=0.6, label='非帕累托点')
        
        pareto = self.data[pareto_mask]
        ax.scatter(pareto[x_col], pareto[y_col], 
                  c='red', s=200, marker='*', label='帕累托前沿', zorder=5)
        
        for _, row in self.data.iterrows():
            ax.annotate(row['model'], 
                       (row[x_col], row[y_col]),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, alpha=0.8)
        
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 图表已保存: {filename}")
    
    def plot_marginal_benefit_curve(self, marginal_benefit_df, filename):
        """绘制边际效益曲线"""
        if len(marginal_benefit_df) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(marginal_benefit_df))
        y = marginal_benefit_df['marginal_benefit'].values
        
        ax.plot(x, y, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel('升级路径', fontsize=12)
        ax.set_ylabel('边际效益 (ΔQ/ΔE)', fontsize=12)
        ax.set_title('边际效益曲线', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 标注拐点
        if len(y) > 1:
            max_idx = np.argmax(y)
            ax.axvline(x=max_idx, color='red', linestyle='--', alpha=0.5, label='最大边际效益')
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 图表已保存: {filename}")


# ==================== 数据加载与主流程 ====================

def load_and_prepare_data():
    """加载并准备数据"""
    print("\n" + "="*80)
    print("加载数据：翻译任务")
    print("="*80)
    
    # 1. 加载质量数据
    quality_df = pd.read_csv(QUALITY_FILE, skiprows=[0])
    quality_df.columns = quality_df.iloc[0]
    quality_df = quality_df[1:].reset_index(drop=True)
    
    quality_data = pd.DataFrame({
        'model': quality_df['model'],
        'quality': pd.to_numeric(quality_df.iloc[:, 1])  # bleu_1 mean
    })
    print(f"✓ 质量数据: {len(quality_data)} 个模型")
    
    # 2. 加载能耗数据
    energy_df = pd.read_csv(ENERGY_FILE, index_col=0)
    energy_task = energy_df.loc['translation'].to_dict()
    print(f"✓ 能耗数据: {len(energy_task)} 个模型")
    
    # 3. 加载速度数据
    speed_df = pd.read_csv(SPEED_FILE, index_col=0)
    speed_task = speed_df.loc['translation'].to_dict()
    print(f"✓ 速度数据: {len(speed_task)} 个模型")
    
    # 4. 模型名称映射
    model_mapping = {
        'deepseek_8b_ol_q4km': 'deepseek-r1:8b',
        'gemma_2b_hf_4bit': 'google--gemma-2b-it:4bit',
        'gemma_2b_hf_8bit': 'google--gemma-2b-it:8bit',
        'gemma_4b_ol_q4km': 'gemma3:4b',
        'phi3_4b_hf_4bit': 'microsoft--phi-3-mini-4k-instruct:4bit',
        'phi3_4b_hf_8bit': 'microsoft--phi-3-mini-4k-instruct:8bit',
        'qwen25_3b_hf_4bit': 'qwen--qwen2.5-3b-instruct:4bit',
        'qwen25_3b_hf_8bit': 'qwen--qwen2.5-3b-instruct:8bit',
        'qwen25_7b_hf_4bit': 'qwen--qwen2.5-7b-instruct:4bit',
        'qwen_4b_ol_q4km': 'qwen3:4b',
        'qwen_8b_ol_q4km': 'qwen3:8b'
    }
    
    # 5. 合并数据
    data = []
    for _, row in quality_data.iterrows():
        model_short = row['model']
        model_full = model_mapping.get(model_short)
        
        if model_full and model_full in energy_task and model_full in speed_task:
            data.append({
                'model': model_short,
                'model_full': model_full,
                'quality': row['quality'],
                'energy': energy_task[model_full],
                'speed': speed_task[model_full]
            })
    
    df = pd.DataFrame(data)
    
    print(f"\n合并后数据: {len(df)} 个模型")
    
    # 保存合并数据
    merged_file = OUTPUT_DIR / 'merged_data.csv'
    df.to_csv(merged_file, index=False, encoding='utf-8-sig')
    print(f"✓ 合并数据已保存: {merged_file}")
    
    return df



def generate_comprehensive_report(analyzer, results):
    """生成综合分析报告"""
    report_file = OUTPUT_DIR / 'TRANSLATION_PARETO_ANALYSIS_ENHANCED_REPORT.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 翻译任务帕累托前沿分析报告（增强版）\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 1. 数据概览
        f.write("## 1. 数据概览\n\n")
        f.write(f"- **任务类型**: 翻译任务（translation）\n")
        f.write(f"- **模型数量**: {len(analyzer.data)}\n")
        f.write(f"- **质量指标**: BLEU得分\n")
        f.write(f"- **能耗指标**: 每token能耗（J/token）\n")
        f.write(f"- **速度指标**: token生成速度（tokens/s）\n\n")
        
        # 2. 帕累托前沿识别
        f.write("## 2. 帕累托前沿识别\n\n")
        
        f.write("### 2.1 质量-能耗前沿\n\n")
        pareto_qe = results['pareto_qe']
        f.write(f"**前沿模型数**: {pareto_qe.sum()}\n\n")
        f.write("**前沿模型列表**:\n\n")
        for model in analyzer.data[pareto_qe]['model']:
            row = analyzer.data[analyzer.data['model'] == model].iloc[0]
            f.write(f"- {model}: 质量={row['quality']:.3f}, 能耗={row['energy']:.3f} J/token\n")
        f.write("\n")
        
        f.write("### 2.2 质量-速度前沿\n\n")
        pareto_qs = results['pareto_qs']
        f.write(f"**前沿模型数**: {pareto_qs.sum()}\n\n")
        f.write("**前沿模型列表**:\n\n")
        for model in analyzer.data[pareto_qs]['model']:
            row = analyzer.data[analyzer.data['model'] == model].iloc[0]
            f.write(f"- {model}: 质量={row['quality']:.3f}, 速度={row['speed']:.2f} tokens/s\n")
        f.write("\n")
        
        f.write("### 2.3 三维前沿（质量-能耗-速度）\n\n")
        pareto_3d = results['pareto_3d']
        f.write(f"**前沿模型数**: {pareto_3d.sum()}\n\n")
        
        # 3. 定量指标
        f.write("## 3. 定量指标\n\n")
        f.write("### 3.1 质量-能耗前沿\n\n")
        f.write(f"- **超体积（Hypervolume）**: {results['metrics_qe']['hypervolume']:.4f}\n")
        f.write(f"- **间距指标（Spacing）**: {results['metrics_qe']['spacing']:.4f}\n")
        f.write(f"- **GD（Generational Distance）**: {results['metrics_qe']['gd_igd']['gd']:.4f}\n")
        f.write(f"- **IGD（Inverted GD）**: {results['metrics_qe']['gd_igd']['igd']:.4f}\n")
        f.write(f"- **拐点模型**: {results['knee_qe']}\n\n")
        
        f.write("### 3.2 质量-速度前沿\n\n")
        f.write(f"- **超体积（Hypervolume）**: {results['metrics_qs']['hypervolume']:.4f}\n")
        f.write(f"- **间距指标（Spacing）**: {results['metrics_qs']['spacing']:.4f}\n")
        f.write(f"- **GD（Generational Distance）**: {results['metrics_qs']['gd_igd']['gd']:.4f}\n")
        f.write(f"- **IGD（Inverted GD）**: {results['metrics_qs']['gd_igd']['igd']:.4f}\n")
        f.write(f"- **拐点模型**: {results['knee_qs']}\n\n")
        
        # 4. 稳健性分析
        f.write("## 4. 稳健性分析\n\n")
        
        f.write("### 4.1 扰动分析（质量-能耗）\n\n")
        pert_qe = results['perturbation_qe']
        f.write(f"- **前沿一致性**: {pert_qe['mean_consistency']:.2%} ± {pert_qe['std_consistency']:.2%}\n")
        f.write(f"- **稳定性评级**: ")
        if pert_qe['mean_consistency'] >= 0.8:
            f.write("⭐⭐⭐⭐⭐ 极稳定\n\n")
        elif pert_qe['mean_consistency'] >= 0.6:
            f.write("⭐⭐⭐⭐ 很稳定\n\n")
        else:
            f.write("⭐⭐⭐ 较稳定\n\n")
        
        f.write("**最稳定模型（Top 5）**:\n\n")
        sorted_stability = sorted(pert_qe['stability_scores'].items(), key=lambda x: x[1], reverse=True)
        for i, (model, score) in enumerate(sorted_stability[:5], 1):
            f.write(f"{i}. {model}: {score:.2%}\n")
        f.write("\n")
        
        f.write("### 4.2 权重敏感性分析\n\n")
        weight_sens = results['weight_sensitivity']
        f.write("**不同权重组合下的最优模型频率（Top 5）**:\n\n")
        for i, (model, count) in enumerate(weight_sens['model_frequency'].most_common(5), 1):
            total = sum(weight_sens['model_frequency'].values())
            freq = count / total
            f.write(f"{i}. {model}: {freq:.2%}\n")
        f.write("\n")
        
        f.write("### 4.3 交叉验证\n\n")
        cv = results['cross_validation']
        f.write("**质量-能耗前沿一致性（Top 5）**:\n\n")
        for i, (model, count) in enumerate(cv['qe_model_counts'].most_common(5), 1):
            f.write(f"{i}. {model}: {count}/5 折\n")
        f.write("\n")
        
        # 5. 决策支持
        f.write("## 5. 决策支持\n\n")
        
        f.write("### 5.1 目标达成度\n\n")
        obj_qe = results['objective_qe']
        f.write(f"- **能耗维度覆盖**: {obj_qe['x_coverage']:.2%}\n")
        f.write(f"- **质量维度覆盖**: {obj_qe['y_coverage']:.2%}\n")
        f.write(f"- **前沿点占比**: {obj_qe['pareto_ratio']:.2%}\n")
        f.write(f"- **综合达成度**: {obj_qe['achievement']:.2%}\n\n")
        
        f.write("### 5.2 鲁棒解推荐\n\n")
        robust = results['robust_solutions']
        f.write("**高稳定性模型（稳定性 ≥ 70%）**:\n\n")
        for model, score in sorted(robust.items(), key=lambda x: x[1], reverse=True):
            f.write(f"- {model}: {score:.2%} ⭐⭐⭐⭐⭐\n")
        f.write("\n")
        
        f.write("### 5.3 升级代价分析\n\n")
        upgrade = results['upgrade_cost']
        if len(upgrade) > 0:
            f.write("**升级路径推荐（按性价比排序）**:\n\n")
            upgrade_sorted = upgrade.sort_values('cost_effectiveness', ascending=False)
            for i, row in upgrade_sorted.head(5).iterrows():
                f.write(f"- {row['from_model']} → {row['to_model']}\n")
                f.write(f"  - 质量提升: {row['quality_improvement_%']:.1f}%\n")
                f.write(f"  - 能耗增加: {row['cost_increase_%']:.1f}%\n")
                f.write(f"  - 性价比: {row['cost_effectiveness']:.4f}\n")
                f.write(f"  - 推荐度: {row['recommendation']}\n\n")
        
        # 6. 推荐配置
        f.write("## 6. 推荐配置\n\n")
        
        knee_model = results['knee_qe']
        if knee_model:
            knee_row = analyzer.data[analyzer.data['model'] == knee_model].iloc[0]
            f.write(f"### 最佳综合配置: {knee_model} ⭐⭐⭐⭐⭐\n\n")
            f.write(f"- **BLEU**: {knee_row['quality']:.3f}\n")
            f.write(f"- **每token能耗**: {knee_row['energy']:.3f} J/token\n")
            f.write(f"- **生成速度**: {knee_row['speed']:.2f} tokens/s\n")
            f.write(f"- **推荐理由**: 拐点模型，质量-能耗权衡最优\n\n")
        
        best_quality = analyzer.data.loc[analyzer.data['quality'].idxmax()]
        f.write(f"### 最高质量: {best_quality['model']}\n\n")
        f.write(f"- **BLEU**: {best_quality['quality']:.3f}\n")
        f.write(f"- **每token能耗**: {best_quality['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_quality['speed']:.2f} tokens/s\n\n")
        
        best_energy = analyzer.data.loc[analyzer.data['energy'].idxmin()]
        f.write(f"### 最低能耗: {best_energy['model']}\n\n")
        f.write(f"- **BLEU**: {best_energy['quality']:.3f}\n")
        f.write(f"- **每token能耗**: {best_energy['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_energy['speed']:.2f} tokens/s\n\n")
        
        # 7. 指标解释
        f.write("## 7. 指标解释\n\n")
        f.write("### 超体积（Hypervolume）\n")
        f.write("- 定义：解集相对于参考点覆盖的目标空间体积\n")
        f.write("- 意义：越大越好，综合衡量收敛性和多样性\n\n")
        
        f.write("### 间距指标（Spacing）\n")
        f.write("- 定义：前沿上相邻点距离的标准差\n")
        f.write("- 意义：越小越好，表示分布越均匀\n\n")
        
        f.write("### GD/IGD\n")
        f.write("- GD：前沿到理想前沿的平均距离，衡量收敛性\n")
        f.write("- IGD：理想前沿到实际前沿的平均距离，衡量收敛性和分布\n")
        f.write("- 意义：越小越好\n\n")
        
        f.write("---\n")
        f.write("**生成脚本**: `analysis/qe_research/scripts/pareto_analysis_translation_enhanced.py`\n")
    
    print(f"\n✓ 综合报告已生成: {report_file}")



def main():
    """主函数"""
    print("\n" + "="*80)
    print("翻译任务帕累托前沿分析（增强版）")
    print("="*80)
    
    # 1. 加载数据
    df = load_and_prepare_data()
    
    # 2. 创建分析器
    analyzer = TranslationParetoAnalyzer(df)
    
    # 3. 识别帕累托前沿
    print("\n" + "="*80)
    print("识别帕累托前沿")
    print("="*80)
    
    pareto_qe = analyzer.identify_pareto_frontier_2d('energy', 'quality', x_minimize=True, y_minimize=False)
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    
    pareto_qs = analyzer.identify_pareto_frontier_2d('speed', 'quality', x_minimize=False, y_minimize=False)
    print(f"✓ 质量-速度前沿: {pareto_qs.sum()} 个模型")
    
    pareto_3d = analyzer.identify_pareto_frontier_3d()
    print(f"✓ 三维前沿: {pareto_3d.sum()} 个模型")
    
    # 4. 计算定量指标
    print("\n" + "="*80)
    print("计算定量指标")
    print("="*80)
    
    # 质量-能耗前沿指标
    hv_qe = analyzer.calculate_hypervolume(pareto_qe, 'energy', 'quality', x_minimize=True, y_minimize=False)
    spacing_qe = analyzer.calculate_spacing(pareto_qe, 'energy', 'quality')
    gd_igd_qe = analyzer.calculate_gd_igd(pareto_qe, 'energy', 'quality', x_minimize=True, y_minimize=False)
    knee_qe = analyzer.find_knee_point(pareto_qe, 'energy', 'quality')
    
    print(f"✓ 质量-能耗前沿:")
    print(f"  - 超体积: {hv_qe:.4f}")
    print(f"  - 间距: {spacing_qe:.4f}")
    print(f"  - GD: {gd_igd_qe['gd']:.4f}")
    print(f"  - IGD: {gd_igd_qe['igd']:.4f}")
    print(f"  - 拐点: {knee_qe}")
    
    # 质量-速度前沿指标
    hv_qs = analyzer.calculate_hypervolume(pareto_qs, 'speed', 'quality', x_minimize=False, y_minimize=False)
    spacing_qs = analyzer.calculate_spacing(pareto_qs, 'speed', 'quality')
    gd_igd_qs = analyzer.calculate_gd_igd(pareto_qs, 'speed', 'quality', x_minimize=False, y_minimize=False)
    knee_qs = analyzer.find_knee_point(pareto_qs, 'speed', 'quality')
    
    print(f"✓ 质量-速度前沿:")
    print(f"  - 超体积: {hv_qs:.4f}")
    print(f"  - 间距: {spacing_qs:.4f}")
    print(f"  - GD: {gd_igd_qs['gd']:.4f}")
    print(f"  - IGD: {gd_igd_qs['igd']:.4f}")
    print(f"  - 拐点: {knee_qs}")
    
    # 5. 稳健性分析
    print("\n" + "="*80)
    print("稳健性分析")
    print("="*80)
    
    perturbation_qe = analyzer.perturbation_analysis('energy', 'quality', 
                                                      x_minimize=True, y_minimize=False,
                                                      noise_level=0.05, n_iterations=100)
    
    weight_sensitivity = analyzer.weight_sensitivity_analysis(n_samples=50)
    
    cross_validation = analyzer.cross_validation_analysis(n_folds=5)
    
    # 6. 决策支持
    print("\n" + "="*80)
    print("决策支持分析")
    print("="*80)
    
    objective_qe = analyzer.calculate_objective_achievement(pareto_qe, 'energy', 'quality')
    print(f"✓ 目标达成度: {objective_qe['achievement']:.2%}")
    
    robust_solutions = analyzer.identify_robust_solutions(perturbation_qe['stability_scores'], threshold=0.7)
    
    upgrade_cost = analyzer.quantify_upgrade_cost(pareto_qe, 'energy', 'quality')
    if len(upgrade_cost) > 0:
        print(f"✓ 升级路径分析: {len(upgrade_cost)} 条路径")
    
    # 7. 生成可视化
    print("\n" + "="*80)
    print("生成可视化图表")
    print("="*80)
    
    analyzer.plot_pareto_2d(pareto_qe, 'energy', 'quality',
                           '翻译任务：质量-能耗帕累托前沿',
                           'pareto_quality_energy_enhanced.png',
                           '每token能耗 (J/token)', 'BLEU')
    
    analyzer.plot_pareto_2d(pareto_qs, 'speed', 'quality',
                           '翻译任务：质量-速度帕累托前沿',
                           'pareto_quality_speed_enhanced.png',
                           'Token生成速度 (tokens/s)', 'BLEU')
    
    # 边际效益曲线
    marginal_benefit = analyzer.calculate_marginal_benefit(pareto_qe, 'energy', 'quality')
    analyzer.plot_marginal_benefit_curve(marginal_benefit, 'marginal_benefit_curve.png')
    
    # 8. 汇总结果
    results = {
        'pareto_qe': pareto_qe,
        'pareto_qs': pareto_qs,
        'pareto_3d': pareto_3d,
        'metrics_qe': {
            'hypervolume': hv_qe,
            'spacing': spacing_qe,
            'gd_igd': gd_igd_qe
        },
        'metrics_qs': {
            'hypervolume': hv_qs,
            'spacing': spacing_qs,
            'gd_igd': gd_igd_qs
        },
        'knee_qe': knee_qe,
        'knee_qs': knee_qs,
        'perturbation_qe': perturbation_qe,
        'weight_sensitivity': weight_sensitivity,
        'cross_validation': cross_validation,
        'objective_qe': objective_qe,
        'robust_solutions': robust_solutions,
        'upgrade_cost': upgrade_cost
    }
    
    # 9. 生成综合报告
    generate_comprehensive_report(analyzer, results)
    
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print(f"- merged_data.csv: 合并数据")
    print(f"- pareto_quality_energy_enhanced.png: 质量-能耗前沿图")
    print(f"- pareto_quality_speed_enhanced.png: 质量-速度前沿图")
    print(f"- marginal_benefit_curve.png: 边际效益曲线")
    print(f"- TRANSLATION_PARETO_ANALYSIS_ENHANCED_REPORT.md: 综合分析报告")


if __name__ == '__main__':
    main()
