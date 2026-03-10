"""
混合任务帕累托前沿分析

功能：
1. 加载多个任务的质量数据
2. 根据权重配置聚合质量得分
3. 合并能耗和速度数据
4. 执行帕累托前沿分析
5. 生成可视化和报告

支持三种权重配置：
- objective: 客观任务为主（技术应用）
- subjective: 主观任务为主（内容创作）
- balanced: 均衡配置（通用评估）
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'analysis' / 'qe_research' / 'scripts'))

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Tuple

os.chdir(project_root)

from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d, identify_pareto_frontier_3d,
    calculate_hypervolume, calculate_spacing, find_knee_point,
    plot_pareto_2d, load_energy_speed_data, load_process_quality_data,
    perturbation_analysis, cross_validation_pareto,
    generate_pareto_report, print_analysis_summary
)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


# ============================================================================
# 模型排除配置
# ============================================================================

# 需要排除的模型（存在数据问题和缺失值）
EXCLUDED_MODELS = [
    'qwen25_7b_hf_8bit',  # 在其他任务上数据有缺失
    'qwen--qwen2.5-7b-instruct:8bit',
    'qwen2.5-7b-instruct:8bit'
]


# ============================================================================
# 权重配置
# ============================================================================

WEIGHT_CONFIGS = {
    'objective': {
        'name': '客观任务为主',
        'description': '适用于技术应用、工程实践、需要精确结果的场景',
        'weights': {
            'code': 0.30,
            'math': 0.25,
            'qa': 0.20,
            'reasoning': 0.15,
            'creative': 0.05,
            'summary': 0.03,
            'translation': 0.02
        }
    },
    'subjective': {
        'name': '主观任务为主',
        'description': '适用于内容创作、文学创作、需要创造性的场景',
        'weights': {
            'creative': 0.35,
            'summary': 0.25,
            'translation': 0.20,
            'code': 0.10,
            'math': 0.05,
            'qa': 0.03,
            'reasoning': 0.02
        }
    },
    'balanced': {
        'name': '均衡配置',
        'description': '适用于通用评估、综合应用',
        'weights': {
            'code': 0.15,
            'math': 0.15,
            'qa': 0.15,
            'reasoning': 0.12,
            'creative': 0.15,
            'summary': 0.15,
            'translation': 0.13
        }
    }
}

ALL_TASKS = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']


# ============================================================================
# 核心函数
# ============================================================================

def normalize_weights(weights: Dict[str, float], verbose: bool = True) -> Dict[str, float]:
    """归一化权重，使其和为1"""
    total = sum(weights.values())
    
    if abs(total - 1.0) < 1e-6:
        if verbose:
            print(f"✓ 权重已归一化（总和 = {total:.6f}）")
        return weights.copy()
    
    normalized = {k: v / total for k, v in weights.items()}
    
    if verbose:
        print(f"⚠ 权重未归一化（原始总和 = {total:.6f}），已自动归一化")
        print("归一化前后对比：")
        for task in weights:
            print(f"  {task:12s}: {weights[task]:.4f} → {normalized[task]:.4f}")
    
    return normalized


def load_all_task_quality_data(tasks: List[str], output_dir: Path, verbose: bool = True) -> Dict[str, pd.DataFrame]:
    """加载所有任务的质量数据"""
    quality_data = {}
    
    for task in tasks:
        if verbose:
            print(f"\n加载任务: {task}")
        
        task_output_dir = output_dir / task
        task_output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            df = load_process_quality_data(
                task_name=task,
                method='entropy',
                normalize_method='zscore',
                use_raw=True,
                verbose=verbose,
                output_dir=task_output_dir
            )
            quality_data[task] = df
            if verbose:
                print(f"✓ 成功加载 {len(df)} 个模型的质量数据")
        except Exception as e:
            print(f"✗ 加载任务 {task} 失败: {str(e)}")
            continue
    
    return quality_data


def aggregate_quality_scores(quality_data: Dict[str, pd.DataFrame], 
                            weights: Dict[str, float],
                            verbose: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """聚合多个任务的质量得分"""
    weights = normalize_weights(weights, verbose=verbose)
    
    # 统一列名：将 'quality' 重命名为 'quality_score'（如果需要）
    for task, df in quality_data.items():
        if 'quality' in df.columns and 'quality_score' not in df.columns:
            quality_data[task] = df.rename(columns={'quality': 'quality_score'})
    
    # 排除指定模型
    excluded_count = 0
    for task, df in quality_data.items():
        original_count = len(df)
        quality_data[task] = df[~df['model'].isin(EXCLUDED_MODELS)]
        excluded_count += original_count - len(quality_data[task])
    
    if verbose and excluded_count > 0:
        print(f"\n⚠ 已排除 {len(EXCLUDED_MODELS)} 个模型: {', '.join(EXCLUDED_MODELS)}")
        print(f"  共排除 {excluded_count} 条数据记录")
    
    all_models = set()
    for df in quality_data.values():
        all_models.update(df['model'].unique())
    
    if verbose:
        print(f"\n共有 {len(all_models)} 个模型")
    
    results = []
    task_scores_matrix = []
    
    for model in sorted(all_models):
        weighted_score = 0.0
        task_scores = {'model': model}
        
        for task, weight in weights.items():
            if task in quality_data:
                df = quality_data[task]
                model_data = df[df['model'] == model]
                
                if len(model_data) > 0:
                    quality_score = model_data['quality_score'].values[0]
                    all_scores = df['quality_score'].values
                    mean_score = all_scores.mean()
                    std_score = all_scores.std()
                    
                    if std_score > 0:
                        normalized_score = (quality_score - mean_score) / std_score
                    else:
                        normalized_score = 0.0
                    
                    weighted_score += weight * normalized_score
                    task_scores[task] = normalized_score
                else:
                    task_scores[task] = np.nan
        
        task_scores['aggregated_quality'] = weighted_score
        task_scores_matrix.append(task_scores)
        
        results.append({
            'model': model,
            'quality': weighted_score
        })
    
    task_scores_df = pd.DataFrame(task_scores_matrix)
    
    if verbose:
        print(f"\n✓ 成功聚合 {len(results)} 个模型的质量得分")
        print(f"  质量得分范围: [{min(r['quality'] for r in results):.4f}, {max(r['quality'] for r in results):.4f}]")
    
    return pd.DataFrame(results), task_scores_df


def merge_energy_speed_data(quality_df: pd.DataFrame, 
                            tasks: List[str],
                            verbose: bool = True) -> pd.DataFrame:
    """合并能耗和速度数据"""
    merged_data = []
    
    for _, row in quality_df.iterrows():
        model = row['model']
        quality = row['quality']
        
        energies = []
        speeds = []
        
        for task in tasks:
            energy_dict, speed_dict = load_energy_speed_data(
                task, 
                DATA_PATHS['energy'], 
                DATA_PATHS['speed']
            )
            
            if model in energy_dict:
                energies.append(energy_dict[model])
            if model in speed_dict:
                speeds.append(speed_dict[model])
        
        avg_energy = np.mean(energies) if energies else np.nan
        avg_speed = np.mean(speeds) if speeds else np.nan
        
        merged_data.append({
            'model': model,
            'quality': quality,
            'energy': avg_energy,
            'speed': avg_speed
        })
    
    df = pd.DataFrame(merged_data)
    df = df.dropna()
    
    if verbose:
        print(f"\n✓ 合并后数据: {len(df)} 个模型")
        print(f"  能耗范围: [{df['energy'].min():.6f}, {df['energy'].max():.6f}] J/token")
        print(f"  速度范围: [{df['speed'].min():.2f}, {df['speed'].max():.2f}] tokens/s")
    
    return df


def plot_task_weights(weights: Dict[str, float], config_name: str, output_path: Path):
    """绘制任务权重分布图"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    tasks = list(weights.keys())
    values = list(weights.values())
    
    colors = plt.cm.Set3(np.linspace(0, 1, len(tasks)))
    bars = ax.bar(tasks, values, color=colors, edgecolor='black', linewidth=1.5)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2%}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('任务类型', fontsize=12, fontweight='bold')
    ax.set_ylabel('权重', fontsize=12, fontweight='bold')
    ax.set_title(f'任务权重分布 - {WEIGHT_CONFIGS[config_name]["name"]}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_ylim(0, max(values) * 1.15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 任务权重图已保存: {output_path.name}")


def plot_quality_heatmap(task_scores_df: pd.DataFrame, config_name: str, output_path: Path):
    """绘制模型×任务质量热力图"""
    heatmap_data = task_scores_df.set_index('model')
    heatmap_data = heatmap_data.drop('aggregated_quality', axis=1, errors='ignore')
    
    if 'aggregated_quality' in task_scores_df.columns:
        sorted_models = task_scores_df.sort_values('aggregated_quality', ascending=False)['model'].values
        heatmap_data = heatmap_data.loc[sorted_models]
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(heatmap_data, annot=True, fmt='.3f', cmap='RdYlGn', 
                cbar_kws={'label': '归一化质量得分'},
                linewidths=0.5, linecolor='gray',
                vmin=0, vmax=1, ax=ax)
    
    ax.set_title(f'模型×任务质量热力图 - {WEIGHT_CONFIGS[config_name]["name"]}', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('任务类型', fontsize=12, fontweight='bold')
    ax.set_ylabel('模型', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 质量热力图已保存: {output_path.name}")


def run_mixed_task_analysis(config_name: str, output_base_dir: Path):
    """运行混合任务分析"""
    config = WEIGHT_CONFIGS[config_name]
    output_dir = output_base_dir / config_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "="*80)
    print(f"混合任务帕累托前沿分析 - {config['name']}")
    print("="*80)
    print(f"配置: {config_name}")
    print(f"描述: {config['description']}")
    print(f"输出目录: {output_dir}")
    print("="*80)
    
    # 1. 加载质量数据
    print("\n步骤1: 加载质量数据")
    print("-" * 80)
    quality_data = load_all_task_quality_data(ALL_TASKS, output_dir, verbose=True)
    
    if not quality_data:
        print("✗ 没有成功加载任何任务数据，退出")
        return
    
    # 2. 聚合质量得分
    print("\n步骤2: 聚合质量得分")
    print("-" * 80)
    quality_df, task_scores_df = aggregate_quality_scores(quality_data, config['weights'], verbose=True)
    
    task_scores_file = output_dir / 'task_quality_scores.csv'
    task_scores_df.to_csv(task_scores_file, index=False, encoding='utf-8-sig')
    print(f"✓ 任务得分矩阵已保存: {task_scores_file.name}")
    
    # 3. 合并能耗和速度数据
    print("\n步骤3: 合并能耗和速度数据")
    print("-" * 80)
    df = merge_energy_speed_data(quality_df, ALL_TASKS, verbose=True)
    
    merged_file = output_dir / 'merged_data.csv'
    df.to_csv(merged_file, index=False, encoding='utf-8-sig')
    print(f"✓ 合并数据已保存: {merged_file.name}")
    
    # 4. 生成可视化
    print("\n步骤4: 生成可视化")
    print("-" * 80)
    
    plot_task_weights(config['weights'], config_name, output_dir / 'task_weights.png')
    plot_quality_heatmap(task_scores_df, config_name, output_dir / 'quality_heatmap.png')
    
    # 5. 帕累托前沿分析
    print("\n步骤5: 帕累托前沿分析")
    print("-" * 80)
    
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', x_minimize=False, y_minimize=True)
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    
    pareto_qs = identify_pareto_frontier_2d(df, 'quality', 'speed', x_minimize=False, y_minimize=False)
    print(f"✓ 质量-速度前沿: {pareto_qs.sum()} 个模型")
    
    pareto_3d = identify_pareto_frontier_3d(df)
    print(f"✓ 三维前沿: {pareto_3d.sum()} 个模型")
    
    # 6. 生成帕累托图
    print("\n步骤6: 生成帕累托图")
    print("-" * 80)
    
    plot_pareto_2d(df, pareto_qe, 'quality', 'energy',
                   f'混合任务：质量-能耗帕累托前沿 ({config["name"]})',
                   output_dir / 'pareto_quality_energy.png',
                   '综合质量得分', '平均能耗 (J/token)',
                   x_minimize=False, y_minimize=True)
    
    plot_pareto_2d(df, pareto_qs, 'quality', 'speed',
                   f'混合任务：质量-速度帕累托前沿 ({config["name"]})',
                   output_dir / 'pareto_quality_speed.png',
                   '综合质量得分', '平均速度 (tokens/s)',
                   x_minimize=False, y_minimize=False)
    
    # 7. 计算定量指标
    print("\n步骤7: 计算定量指标")
    print("-" * 80)
    
    hv_qe = calculate_hypervolume(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 超体积（质量-能耗）: {hv_qe:.4f}")
    
    spacing_qe = calculate_spacing(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 间距指标（质量-能耗）: {spacing_qe:.4f}")
    
    knee = find_knee_point(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 拐点模型: {knee}")
    
    # 8. 稳健性分析
    print("\n步骤8: 稳健性分析")
    print("-" * 80)
    
    print("扰动分析（质量-能耗前沿）...")
    robustness_qe = perturbation_analysis(df, 'quality', 'energy',
                                          x_minimize=False, y_minimize=True,
                                          noise_level=0.05, n_iterations=100)
    print(f"✓ 前沿一致性: {robustness_qe['mean_consistency']:.2%}")
    
    print("交叉验证分析（质量-能耗前沿）...")
    cross_val_qe = cross_validation_pareto(df, 'quality', 'energy',
                                           x_minimize=False, y_minimize=True,
                                           n_folds=5)
    print(f"✓ 交叉验证一致性: {cross_val_qe['mean_consistency']:.2%}")
    
    results = {
        'pareto_qe': pareto_qe,
        'pareto_qs': pareto_qs,
        'pareto_3d': pareto_3d,
        'hypervolume_qe': hv_qe,
        'spacing_qe': spacing_qe,
        'knee_point': knee,
        'robustness_qe': robustness_qe,
        'cross_val_qe': cross_val_qe
    }
    
    # 9. 生成报告
    print("\n步骤9: 生成报告")
    print("-" * 80)
    
    task_config = {
        'task_name': 'mixed',
        'task_name_cn': f'混合任务 - {config["name"]}',
        'quality_metric': '综合质量得分',
        'quality_method': 'weighted_aggregation',
        'report_filename': 'MIXED_TASK_ANALYSIS_REPORT.md'
    }
    
    report_path = generate_pareto_report(df, results, output_dir, task_config)
    print(f"✓ 报告已保存: {report_path.name}")
    
    print_analysis_summary(df, results, f"混合任务 - {config['name']}")
    
    print("\n" + "="*80)
    print(f"分析完成！配置: {config_name}")
    print("="*80)
    print(f"输出目录: {output_dir}")


def main():
    """主函数"""
    output_base_dir = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'mixed_task_analysis' / 'task_01'
    
    print("\n" + "="*80)
    print("混合任务帕累托前沿分析 - 批量执行")
    print("="*80)
    print(f"输出基础目录: {output_base_dir}")
    print(f"配置数量: {len(WEIGHT_CONFIGS)}")
    print("="*80)
    
    for idx, config_name in enumerate(WEIGHT_CONFIGS.keys(), 1):
        print(f"\n\n{'#'*80}")
        print(f"# 进度: {idx}/{len(WEIGHT_CONFIGS)} - 配置: {config_name}")
        print(f"{'#'*80}\n")
        
        try:
            run_mixed_task_analysis(config_name, output_base_dir)
            print(f"\n✓ 配置 {config_name} 完成！")
        except Exception as e:
            print(f"\n✗ 配置 {config_name} 失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n\n" + "="*80)
    print("所有配置分析完成！")
    print("="*80)
    print(f"结果保存在: {output_base_dir}")
    print("="*80)


if __name__ == '__main__':
    main()
