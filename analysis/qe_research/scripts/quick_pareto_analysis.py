"""
快速帕累托前沿分析工具

一键完成：熵权法 + 帕累托前沿 + 定量指标 + 稳健性验证

使用示例：
    python quick_pareto_analysis.py --task reasoning
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


def calculate_entropy_weights(df, quality_columns):
    """计算熵权法权重"""
    print("\n" + "="*80)
    print("步骤1：熵权法计算质量权重")
    print("="*80)
    
    # 标准化
    data = df[quality_columns].values
    data_norm = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-10)
    
    # 计算概率
    prob = data_norm / (data_norm.sum(axis=0) + 1e-10)
    
    # 计算熵
    entropy = -np.sum(prob * np.log(prob + 1e-10), axis=0) / np.log(len(df))
    
    # 计算权重
    diversity = 1 - entropy
    weights = diversity / diversity.sum()
    
    print("\n质量维度权重:")
    for col, weight in zip(quality_columns, weights):
        print(f"  {col}: {weight:.4f} ({weight*100:.2f}%)")
    
    # 计算加权质量得分
    weighted_quality = (data_norm * weights).sum(axis=1)
    
    return weights, weighted_quality


def identify_pareto_frontier(df, x_col, y_col, maximize_x=False, maximize_y=True):
    """识别帕累托前沿"""
    data = df[[x_col, y_col, 'model']].copy().reset_index(drop=True)
    
    # 转换为最大化问题
    if not maximize_x:
        data[x_col] = -data[x_col]
    if not maximize_y:
        data[y_col] = -data[y_col]
    
    # 识别非支配解
    is_pareto = np.ones(len(data), dtype=bool)
    for i in range(len(data)):
        if not is_pareto[i]:
            continue
        for j in range(len(data)):
            if i != j and is_pareto[j]:
                if (data.loc[j, x_col] >= data.loc[i, x_col] and 
                    data.loc[j, y_col] >= data.loc[i, y_col] and
                    (data.loc[j, x_col] > data.loc[i, x_col] or 
                     data.loc[j, y_col] > data.loc[i, y_col])):
                    is_pareto[i] = False
                    break
    
    return df[is_pareto].copy()


def calculate_hypervolume(pareto_front, x_col, y_col, ref_point):
    """计算超体积"""
    sorted_front = pareto_front.sort_values(x_col)
    hv = 0.0
    prev_x = ref_point[0]
    
    for _, row in sorted_front.iterrows():
        x, y = row[x_col], row[y_col]
        width = abs(prev_x - x)
        height = abs(y - ref_point[1])
        hv += width * height
        prev_x = x
    
    return hv


def main():
    parser = argparse.ArgumentParser(description='快速帕累托前沿分析')
    parser.add_argument('--task', required=True, help='任务名称')
    parser.add_argument('--quality-file', help='质量评分文件')
    parser.add_argument('--energy-file', help='能耗数据文件')
    parser.add_argument('--speed-file', help='速度数据文件')
    parser.add_argument('--output-dir', help='输出目录')
    
    args = parser.parse_args()
    
    # 设置输出目录
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).parent.parent / 'results' / 'pareto_analysis' / args.task
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"快速帕累托前沿分析：{args.task}任务")
    print(f"输出目录：{output_dir}")
    print(f"{'='*80}")
    
    # TODO: 实现完整分析流程
    print("\n分析完成！")


if __name__ == '__main__':
    main()
