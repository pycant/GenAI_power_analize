#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取Reasoning任务的人工评分数据并生成聚合质量得分
Extract manual scores for Reasoning task and generate aggregated quality scores
"""

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np

def calculate_entropy_weights(df, score_columns):
    """
    使用熵权法计算权重
    
    Parameters:
    -----------
    df : DataFrame
        包含评分数据的DataFrame
    score_columns : list
        需要计算权重的列名列表
    
    Returns:
    --------
    dict : 各维度的权重
    """
    # 标准化数据到[0,1]
    data = df[score_columns].values
    data_norm = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-10)
    
    # 计算信息熵
    n = len(data_norm)
    p = data_norm / (data_norm.sum(axis=0) + 1e-10)
    entropy = -np.sum(p * np.log(p + 1e-10), axis=0) / np.log(n)
    
    # 计算权重
    diversity = 1 - entropy
    weights = diversity / diversity.sum()
    
    return dict(zip(score_columns, weights))

def main():
    print("=" * 80)
    print("提取Reasoning任务人工评分数据")
    print("=" * 80)
    
    # 输入文件
    input_file = project_root / 'data/analize/results/reasoning_quality/manual_scores_summary.csv'
    
    if not input_file.exists():
        print(f"错误: 输入文件不存在: {input_file}")
        return
    
    # 读取数据
    df = pd.read_csv(input_file)
    print(f"\n读取数据: {len(df)} 个模型")
    print("\n原始数据:")
    print(df.head())
    
    # 评分维度列
    score_columns = ['avg_correctness', 'avg_completeness', 'avg_rigor', 
                    'avg_clarity', 'avg_efficiency']
    
    # 计算熵权
    print("\n" + "=" * 80)
    print("计算熵权...")
    print("=" * 80)
    
    weights = calculate_entropy_weights(df, score_columns)
    
    print("\n各维度权重:")
    for col, weight in weights.items():
        dim_name = col.replace('avg_', '')
        print(f"  {dim_name:15s}: {weight:.4f} ({weight*100:.2f}%)")
    
    # 计算加权质量得分
    df['weighted_quality'] = sum(df[col] * weights[col] for col in score_columns)
    
    # 归一化到[0,1]
    df['quality_normalized'] = (df['weighted_quality'] - df['weighted_quality'].min()) / \
                               (df['weighted_quality'].max() - df['weighted_quality'].min())
    
    # 标准化模型名称
    df['model'] = df['model'].str.strip().str.lower()
    
    # 选择输出列
    output_df = df[['model', 'weighted_quality', 'quality_normalized'] + score_columns].copy()
    
    # 保存结果
    output_dir = project_root / 'analysis/qe_research/results/quality_scores'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'reasoning_scores_aggregated.csv'
    output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 80)
    print("质量得分统计")
    print("=" * 80)
    print(f"\n加权质量得分范围: {df['weighted_quality'].min():.3f} - {df['weighted_quality'].max():.3f}")
    print(f"归一化质量得分范围: {df['quality_normalized'].min():.3f} - {df['quality_normalized'].max():.3f}")
    
    print("\n模型排名 (按归一化质量得分):")
    ranked = output_df.sort_values('quality_normalized', ascending=False)
    for i, (_, row) in enumerate(ranked.iterrows(), 1):
        print(f"  {i:2d}. {row['model']:25s} - 质量得分: {row['quality_normalized']:.3f} (加权: {row['weighted_quality']:.3f})")
    
    print("\n" + "=" * 80)
    print(f"结果已保存: {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    main()
