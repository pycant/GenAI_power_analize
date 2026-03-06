"""
Code任务帕累托前沿分析

自动完成：
1. 数据准备（质量评分 + 能耗 + 速度）
2. 熵权法计算质量综合得分
3. 帕累托前沿识别
4. 定量指标计算
5. 稳健性验证
6. 生成完整报告
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def prepare_code_data():
    """准备Code任务数据"""
    print("\n" + "="*80)
    print("准备Code任务数据")
    print("="*80)
    
    base_dir = Path(__file__).parent.parent.parent
    
    # 1. 加载质量评分
    quality_file = base_dir / 'data' / 'analize' / 'results' / 'code_quality' / 'quality_summary_code_v2.csv'
    quality_df = pd.read_csv(quality_file)
    print(f"✓ 质量数据: {len(quality_df)} 个模型")
    
    # 2. 加载能耗和速度数据
    perf_file = base_dir / 'data' / 'experiments_1' / 'summary' / 'results.csv'
    perf_df = pd.read_csv(perf_file)
    
    # 筛选code任务
    code_perf = perf_df[perf_df['task'] == 'code'].copy()
    
    # 模型名称映射
    model_mapping = {
        'deepseek-r1:8b': 'deepseek_8b_ol_q4km',
        'gemma3:4b': 'gemma_4b_ol_q4km',
        'qwen3:8b': 'qwen_8b_ol_q4km',
        'qwen3:4b': 'qwen_4b_ol_q4km'
    }
    
    code_perf['model_mapped'] = code_perf['model'].map(model_mapping)
    code_perf = code_perf.rename(columns={
        'gpu_energy_j': 'energy',
        'toks_per_s': 'speed'
    })
    
    print(f"✓ 能耗/速度数据: {len(code_perf)} 条记录")
    
    # 3. 计算熵权法质量得分
    print("\n" + "="*80)
    print("计算熵权法质量得分")
    print("="*80)
    
    # 选择质量维度
    quality_dimensions = [
        'functional_dimension_mean',  # 功能维度
        'efficiency_dimension_mean',  # 效率维度
        'quality_dimension_mean',     # 质量维度
        'readability_dimension_mean'  # 可读性维度
    ]
    
    # 标准化
    data = quality_df[quality_dimensions].values
    data_norm = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-10)
    
    # 计算概率
    prob = data_norm / (data_norm.sum(axis=0) + 1e-10)
    
    # 计算熵
    entropy = -np.sum(prob * np.log(prob + 1e-10), axis=0) / np.log(len(quality_df))
    
    # 计算权重
    diversity = 1 - entropy
    weights = diversity / diversity.sum()
    
    print("\n质量维度权重:")
    for dim, weight in zip(quality_dimensions, weights):
        print(f"  {dim}: {weight:.4f} ({weight*100:.2f}%)")
    
    # 计算加权质量得分
    quality_df['quality_normalized'] = (data_norm * weights).sum(axis=1)
    quality_df['weighted_quality'] = quality_df['quality_normalized'] * 5  # 转换到0-5分
    
    print(f"\n质量得分范围: {quality_df['quality_normalized'].min():.4f} - {quality_df['quality_normalized'].max():.4f}")
    
    # 4. 合并数据
    merged_df = quality_df[['model', 'quality_normalized', 'weighted_quality']].merge(
        code_perf[['model_mapped', 'energy', 'speed']],
        left_on='model',
        right_on='model_mapped',
        how='inner'
    )
    
    merged_df = merged_df.drop('model_mapped', axis=1)
    
    print(f"\n✓ 合并后数据: {len(merged_df)} 个模型")
    print(f"  列: {', '.join(merged_df.columns)}")
    
    # 5. 保存数据
    output_dir = base_dir / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / 'code'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'merged_data.csv'
    merged_df.to_csv(output_file, index=False)
    
    print(f"\n✓ 数据已保存: {output_file}")
    
    return output_file, weights, quality_dimensions


def main():
    """主函数"""
    print("\n" + "="*80)
    print("Code任务帕累托前沿分析")
    print("="*80)
    
    # 准备数据
    data_file, weights, dimensions = prepare_code_data()
    
    print("\n" + "="*80)
    print("数据准备完成！")
    print("="*80)
    print(f"\n下一步：")
    print(f"1. 修改 pareto_metrics_calculator.py 中的数据路径为:")
    print(f"   {data_file}")
    print(f"2. 运行定量指标计算:")
    print(f"   python pareto_metrics_calculator.py")
    print(f"3. 运行稳健性验证:")
    print(f"   python pareto_robustness_analyzer.py")
    
    return data_file


if __name__ == '__main__':
    main()
