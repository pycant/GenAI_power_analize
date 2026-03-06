"""
帕累托前沿定量评价指标计算器

实现以下指标：
1. 超体积（Hypervolume, HV）
2. 间距指标（Spacing, SP）
3. 最大扩散度（Maximum Spread, MS）
4. 边际效益分析（Marginal Benefit）
5. 拐点识别（Knee Point Detection）
"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


class ParetoMetricsCalculator:
    """帕累托前沿定量评价指标计算器"""
    
    def __init__(self, data_path):
        """
        初始化
        
        Args:
            data_path: 数据文件路径（CSV格式）
        """
        self.data = pd.read_csv(data_path)
        self.results = {}
        
    def identify_pareto_frontier_2d(self, x_col, y_col, maximize_x=False, maximize_y=True):
        """
        识别2D帕累托前沿
        
        Args:
            x_col: X轴列名（如'energy'）
            y_col: Y轴列名（如'quality_normalized'）
            maximize_x: 是否最大化X（默认False，即最小化）
            maximize_y: 是否最大化Y（默认True）
        
        Returns:
            DataFrame: 帕累托最优解
        """
        data = self.data[[x_col, y_col, 'model']].copy()
        
        # 转换为最大化问题
        if not maximize_x:
            data[x_col] = -data[x_col]
        if not maximize_y:
            data[y_col] = -data[y_col]
        
        # 识别非支配解
        is_pareto = np.ones(len(data), dtype=bool)
        for i, row_i in data.iterrows():
            for j, row_j in data.iterrows():
                if i != j:
                    # 如果j支配i（j在所有维度上都不差于i，且至少一个维度更好）
                    if (row_j[x_col] >= row_i[x_col] and row_j[y_col] >= row_i[y_col] and
                        (row_j[x_col] > row_i[x_col] or row_j[y_col] > row_i[y_col])):
                        is_pareto[i] = False
                        break
        
        pareto_data = self.data[is_pareto].copy()
        
        # 恢复原始值
        if not maximize_x:
            pareto_data[x_col] = -pareto_data[x_col]
        if not maximize_y:
            pareto_data[y_col] = -pareto_data[y_col]
        
        return pareto_data.sort_values(x_col)
    
    def calculate_hypervolume_2d(self, pareto_front, x_col, y_col, ref_point):
        """
        计算2D超体积
        
        Args:
            pareto_front: 帕累托前沿数据
            x_col: X轴列名
            y_col: Y轴列名
            ref_point: 参考点 (x_ref, y_ref)，通常为最劣值
        
        Returns:
            float: 超体积值
        """
        # 按X轴排序
        sorted_front = pareto_front.sort_values(x_col)
        
        hv = 0.0
        prev_x = ref_point[0]
        
        for _, row in sorted_front.iterrows():
            x = row[x_col]
            y = row[y_col]
            
            # 计算矩形面积
            width = abs(prev_x - x)
            height = abs(y - ref_point[1])
            hv += width * height
            
            prev_x = x
        
        return hv
    
    def calculate_spacing(self, pareto_front, x_col, y_col):
        """
        计算间距指标（Spacing）
        
        Args:
            pareto_front: 帕累托前沿数据
            x_col: X轴列名
            y_col: Y轴列名
        
        Returns:
            float: 间距指标（标准差越小，分布越均匀）
        """
        points = pareto_front[[x_col, y_col]].values
        
        if len(points) < 2:
            return 0.0
        
        # 归一化
        points_norm = (points - points.min(axis=0)) / (points.max(axis=0) - points.min(axis=0) + 1e-10)
        
        # 计算每个点到最近邻的距离
        min_distances = []
        for i, p1 in enumerate(points_norm):
            distances = [euclidean(p1, p2) for j, p2 in enumerate(points_norm) if i != j]
            if distances:
                min_distances.append(min(distances))
        
        # 计算距离的标准差
        if len(min_distances) > 1:
            mean_dist = np.mean(min_distances)
            spacing = np.sqrt(np.sum((np.array(min_distances) - mean_dist)**2) / len(min_distances))
            return spacing
        else:
            return 0.0
    
    def calculate_maximum_spread(self, pareto_front, x_col, y_col):
        """
        计算最大扩散度（Maximum Spread）
        
        Args:
            pareto_front: 帕累托前沿数据
            x_col: X轴列名
            y_col: Y轴列名
        
        Returns:
            dict: 包含各维度范围和总扩散度
        """
        x_range = pareto_front[x_col].max() - pareto_front[x_col].min()
        y_range = pareto_front[y_col].max() - pareto_front[y_col].min()
        
        # 归一化后的扩散度
        x_norm_range = x_range / (self.data[x_col].max() - self.data[x_col].min())
        y_norm_range = y_range / (self.data[y_col].max() - self.data[y_col].min())
        
        total_spread = x_norm_range * y_norm_range
        
        return {
            'x_range': x_range,
            'y_range': y_range,
            'x_norm_range': x_norm_range,
            'y_norm_range': y_norm_range,
            'total_spread': total_spread
        }
    
    def calculate_marginal_benefit(self, pareto_front, x_col, y_col):
        """
        计算边际效益
        
        Args:
            pareto_front: 帕累托前沿数据
            x_col: X轴列名（成本维度，如能耗）
            y_col: Y轴列名（收益维度，如质量）
        
        Returns:
            DataFrame: 包含边际效益的数据
        """
        sorted_front = pareto_front.sort_values(x_col).reset_index(drop=True)
        
        marginal_benefits = []
        for i in range(1, len(sorted_front)):
            delta_x = sorted_front.loc[i, x_col] - sorted_front.loc[i-1, x_col]
            delta_y = sorted_front.loc[i, y_col] - sorted_front.loc[i-1, y_col]
            
            mb = delta_y / delta_x if delta_x != 0 else 0
            
            marginal_benefits.append({
                'from_model': sorted_front.loc[i-1, 'model'],
                'to_model': sorted_front.loc[i, 'model'],
                'delta_x': delta_x,
                'delta_y': delta_y,
                'marginal_benefit': mb,
                'from_x': sorted_front.loc[i-1, x_col],
                'to_x': sorted_front.loc[i, x_col],
                'from_y': sorted_front.loc[i-1, y_col],
                'to_y': sorted_front.loc[i, y_col]
            })
        
        return pd.DataFrame(marginal_benefits)
    
    def identify_knee_point(self, pareto_front, x_col, y_col):
        """
        识别拐点（Knee Point）
        
        使用最大曲率法识别性价比最高的点
        
        Args:
            pareto_front: 帕累托前沿数据
            x_col: X轴列名
            y_col: Y轴列名
        
        Returns:
            dict: 拐点信息
        """
        sorted_front = pareto_front.sort_values(x_col)
        
        if len(sorted_front) < 3:
            return {'knee_model': sorted_front.iloc[0]['model'], 'method': 'insufficient_points'}
        
        # 归一化
        x = sorted_front[x_col].values
        y = sorted_front[y_col].values
        x_norm = (x - x.min()) / (x.max() - x.min() + 1e-10)
        y_norm = (y - y.min()) / (y.max() - y.min() + 1e-10)
        
        # 方法1：最大距离法（到理想点和反理想点连线的距离）
        ideal_point = np.array([x_norm.min(), y_norm.max()])
        nadir_point = np.array([x_norm.max(), y_norm.min()])
        
        max_distance = 0
        knee_idx = 0
        
        for i, (xi, yi) in enumerate(zip(x_norm, y_norm)):
            point = np.array([xi, yi])
            # 计算点到直线的距离
            distance = np.abs(np.cross(nadir_point - ideal_point, ideal_point - point)) / np.linalg.norm(nadir_point - ideal_point)
            
            if distance > max_distance:
                max_distance = distance
                knee_idx = i
        
        knee_model = sorted_front.iloc[knee_idx]['model']
        
        # 方法2：边际效益下降最快的点
        mb_df = self.calculate_marginal_benefit(pareto_front, x_col, y_col)
        if len(mb_df) > 1:
            mb_changes = np.diff(mb_df['marginal_benefit'].values)
            if len(mb_changes) > 0:
                max_decline_idx = np.argmin(mb_changes)
                mb_knee_model = mb_df.iloc[max_decline_idx]['to_model']
            else:
                mb_knee_model = knee_model
        else:
            mb_knee_model = knee_model
        
        return {
            'knee_model_distance': knee_model,
            'knee_model_marginal': mb_knee_model,
            'knee_idx': knee_idx,
            'max_distance': max_distance,
            'x_value': sorted_front.iloc[knee_idx][x_col],
            'y_value': sorted_front.iloc[knee_idx][y_col]
        }
    
    def analyze_quality_energy_frontier(self):
        """分析质量-能耗帕累托前沿"""
        print("\n" + "="*80)
        print("质量-能耗帕累托前沿分析")
        print("="*80)
        
        # 识别前沿
        pareto_front = self.identify_pareto_frontier_2d('energy', 'quality_normalized', 
                                                         maximize_x=False, maximize_y=True)
        
        print(f"\n帕累托最优模型数量: {len(pareto_front)}")
        print("\n帕累托前沿模型:")
        print(pareto_front[['model', 'quality_normalized', 'energy']].to_string(index=False))
        
        # 计算超体积
        ref_point = (self.data['energy'].max(), self.data['quality_normalized'].min())
        hv = self.calculate_hypervolume_2d(pareto_front, 'energy', 'quality_normalized', ref_point)
        print(f"\n超体积（Hypervolume）: {hv:.4f}")
        print(f"参考点: 能耗={ref_point[0]:.2f} J, 质量={ref_point[1]:.4f}")
        
        # 计算间距指标
        spacing = self.calculate_spacing(pareto_front, 'energy', 'quality_normalized')
        print(f"\n间距指标（Spacing）: {spacing:.4f}")
        print("（越小表示分布越均匀）")
        
        # 计算最大扩散度
        spread = self.calculate_maximum_spread(pareto_front, 'energy', 'quality_normalized')
        print(f"\n最大扩散度（Maximum Spread）:")
        print(f"  能耗范围: {spread['x_range']:.2f} J ({spread['x_norm_range']:.2%})")
        print(f"  质量范围: {spread['y_range']:.4f} ({spread['y_norm_range']:.2%})")
        print(f"  总扩散度: {spread['total_spread']:.4f}")
        
        # 边际效益分析
        mb_df = self.calculate_marginal_benefit(pareto_front, 'energy', 'quality_normalized')
        print(f"\n边际效益分析:")
        print("\n| 从模型 | 到模型 | ΔQ | ΔE (J) | ΔQ/ΔE | 排名 |")
        print("|" + "-"*78 + "|")
        
        mb_sorted = mb_df.sort_values('marginal_benefit', ascending=False).reset_index(drop=True)
        for i, row in mb_sorted.iterrows():
            print(f"| {row['from_model'][:20]:20s} | {row['to_model'][:20]:20s} | "
                  f"{row['delta_y']:6.3f} | {row['delta_x']:7.2f} | "
                  f"{row['marginal_benefit']:9.6f} | {i+1:4d} |")
        
        # 拐点识别
        knee = self.identify_knee_point(pareto_front, 'energy', 'quality_normalized')
        print(f"\n拐点识别:")
        print(f"  最大距离法: {knee['knee_model_distance']}")
        print(f"  边际效益法: {knee['knee_model_marginal']}")
        print(f"  拐点位置: 能耗={knee['x_value']:.2f} J, 质量={knee['y_value']:.4f}")
        
        # 保存结果
        self.results['quality_energy'] = {
            'pareto_front': pareto_front,
            'hypervolume': hv,
            'spacing': spacing,
            'spread': spread,
            'marginal_benefit': mb_df,
            'knee_point': knee
        }
        
        return pareto_front
    
    def analyze_quality_speed_frontier(self):
        """分析质量-速度帕累托前沿"""
        print("\n" + "="*80)
        print("质量-速度帕累托前沿分析")
        print("="*80)
        
        # 识别前沿
        pareto_front = self.identify_pareto_frontier_2d('speed', 'quality_normalized', 
                                                         maximize_x=True, maximize_y=True)
        
        print(f"\n帕累托最优模型数量: {len(pareto_front)}")
        print("\n帕累托前沿模型:")
        print(pareto_front[['model', 'quality_normalized', 'speed']].to_string(index=False))
        
        # 计算超体积
        ref_point = (self.data['speed'].min(), self.data['quality_normalized'].min())
        hv = self.calculate_hypervolume_2d(pareto_front, 'speed', 'quality_normalized', ref_point)
        print(f"\n超体积（Hypervolume）: {hv:.4f}")
        print(f"参考点: 速度={ref_point[0]:.2f} t/s, 质量={ref_point[1]:.4f}")
        
        # 计算间距指标
        spacing = self.calculate_spacing(pareto_front, 'speed', 'quality_normalized')
        print(f"\n间距指标（Spacing）: {spacing:.4f}")
        
        # 计算最大扩散度
        spread = self.calculate_maximum_spread(pareto_front, 'speed', 'quality_normalized')
        print(f"\n最大扩散度（Maximum Spread）:")
        print(f"  速度范围: {spread['x_range']:.2f} t/s ({spread['x_norm_range']:.2%})")
        print(f"  质量范围: {spread['y_range']:.4f} ({spread['y_norm_range']:.2%})")
        print(f"  总扩散度: {spread['total_spread']:.4f}")
        
        # 拐点识别
        knee = self.identify_knee_point(pareto_front, 'speed', 'quality_normalized')
        print(f"\n拐点识别:")
        print(f"  最大距离法: {knee['knee_model_distance']}")
        print(f"  边际效益法: {knee['knee_model_marginal']}")
        
        # 保存结果
        self.results['quality_speed'] = {
            'pareto_front': pareto_front,
            'hypervolume': hv,
            'spacing': spacing,
            'spread': spread,
            'knee_point': knee
        }
        
        return pareto_front
    
    def generate_summary_report(self, output_dir):
        """生成汇总报告"""
        output_path = Path(output_dir) / 'pareto_metrics_summary.md'
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 帕累托前沿定量评价指标汇总\n\n")
            f.write("## 一、质量-能耗前沿\n\n")
            
            if 'quality_energy' in self.results:
                res = self.results['quality_energy']
                f.write(f"### 基本信息\n\n")
                f.write(f"- 帕累托最优模型数量: {len(res['pareto_front'])}\n")
                f.write(f"- 超体积（Hypervolume）: {res['hypervolume']:.4f}\n")
                f.write(f"- 间距指标（Spacing）: {res['spacing']:.4f}\n")
                f.write(f"- 总扩散度: {res['spread']['total_spread']:.4f}\n\n")
                
                f.write(f"### 拐点推荐\n\n")
                knee = res['knee_point']
                f.write(f"- 最大距离法: **{knee['knee_model_distance']}**\n")
                f.write(f"- 边际效益法: **{knee['knee_model_marginal']}**\n")
                f.write(f"- 拐点位置: 能耗={knee['x_value']:.2f} J, 质量={knee['y_value']:.4f}\n\n")
                
                f.write(f"### 边际效益排名（Top 3）\n\n")
                mb_top3 = res['marginal_benefit'].nlargest(3, 'marginal_benefit')
                for i, row in mb_top3.iterrows():
                    f.write(f"{i+1}. {row['from_model']} → {row['to_model']}: "
                           f"ΔQ/ΔE = {row['marginal_benefit']:.6f}\n")
                f.write("\n")
            
            f.write("## 二、质量-速度前沿\n\n")
            
            if 'quality_speed' in self.results:
                res = self.results['quality_speed']
                f.write(f"### 基本信息\n\n")
                f.write(f"- 帕累托最优模型数量: {len(res['pareto_front'])}\n")
                f.write(f"- 超体积（Hypervolume）: {res['hypervolume']:.4f}\n")
                f.write(f"- 间距指标（Spacing）: {res['spacing']:.4f}\n")
                f.write(f"- 总扩散度: {res['spread']['total_spread']:.4f}\n\n")
                
                f.write(f"### 拐点推荐\n\n")
                knee = res['knee_point']
                f.write(f"- 最大距离法: **{knee['knee_model_distance']}**\n")
                f.write(f"- 边际效益法: **{knee['knee_model_marginal']}**\n\n")
            
            f.write("## 三、指标解释\n\n")
            f.write("### 超体积（Hypervolume）\n")
            f.write("- 定义：解集相对于参考点覆盖的目标空间体积\n")
            f.write("- 意义：越大越好，综合衡量收敛性和多样性\n")
            f.write("- 用途：比较不同任务或算法的前沿质量\n\n")
            
            f.write("### 间距指标（Spacing）\n")
            f.write("- 定义：前沿上相邻点距离的标准差\n")
            f.write("- 意义：越小越好，表示分布越均匀\n")
            f.write("- 用途：评估前沿的多样性和覆盖均匀性\n\n")
            
            f.write("### 最大扩散度（Maximum Spread）\n")
            f.write("- 定义：前沿在各维度上的归一化范围乘积\n")
            f.write("- 意义：越大越好，表示覆盖范围越广\n")
            f.write("- 用途：评估前沿的覆盖能力\n\n")
            
            f.write("### 拐点（Knee Point）\n")
            f.write("- 定义：前沿上性价比最高的点\n")
            f.write("- 识别方法：最大距离法、边际效益法\n")
            f.write("- 用途：为决策者提供推荐配置\n\n")
            
            f.write("---\n")
            f.write("*报告生成时间: 2026-03-06*\n")
        
        print(f"\n汇总报告已保存至: {output_path}")


def main():
    """主函数"""
    # 数据路径
    data_path = Path(__file__).parent.parent / 'results' / 'pareto_analysis' / 'reasoning' / 'merged_data.csv'
    output_dir = Path(__file__).parent.parent / 'results' / 'pareto_analysis' / 'reasoning'
    
    # 创建计算器
    calculator = ParetoMetricsCalculator(data_path)
    
    # 分析质量-能耗前沿
    calculator.analyze_quality_energy_frontier()
    
    # 分析质量-速度前沿
    calculator.analyze_quality_speed_frontier()
    
    # 生成汇总报告
    calculator.generate_summary_report(output_dir)
    
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)


if __name__ == '__main__':
    main()
