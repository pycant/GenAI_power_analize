#!/usr/bin/env python3
"""
修复代码质量评分数据中的空测试指标
对于编译失败的代码：test_pass_rate 应该为 0，而不是空值
"""

import pandas as pd
import numpy as np
from pathlib import Path

def fix_code_test_metrics():
    """修复代码质量评分数据中的空测试指标"""
    
    # 输入文件路径
    input_file = Path('data/analize/results/code_quality/quality_scores_code_v2.csv')
    
    if not input_file.exists():
        print(f"错误: 文件不存在: {input_file}")
        return
    
    # 读取数据
    print(f"读取文件: {input_file}")
    df = pd.read_csv(input_file, encoding='utf-8')
    
    print(f"原始数据形状: {df.shape}")
    print(f"列名: {df.columns.tolist()}")
    
    # 检查空值情况
    test_metrics = ['test_pass_rate', 'tests_passed', 'tests_total']
    for metric in test_metrics:
        empty_count = df[metric].isna().sum()
        print(f"{metric} 空值数量: {empty_count}/{len(df)} ({empty_count/len(df)*100:.1f}%)")
    
    # 检查编译失败的情况
    compilation_failures = df[df['compilation_success'] == 0.0]
    print(f"\n编译失败的行数: {len(compilation_failures)}/{len(df)} ({len(compilation_failures)/len(df)*100:.1f}%)")
    
    # 检查编译失败且测试指标为空的情况
    for metric in test_metrics:
        fail_and_empty = df[(df['compilation_success'] == 0.0) & (df[metric].isna())]
        print(f"编译失败且 {metric} 为空: {len(fail_and_empty)}")
    
    # 修复逻辑：对于编译失败的代码，测试指标应该为0
    rows_fixed = 0
    for metric in test_metrics:
        # 找到编译失败且该指标为空的记录
        mask = (df['compilation_success'] == 0.0) & (df[metric].isna())
        fix_count = mask.sum()
        
        if fix_count > 0:
            # 对于 test_pass_rate 和 tests_passed，设置为 0.0
            if metric in ['test_pass_rate', 'tests_passed']:
                df.loc[mask, metric] = 0.0
                print(f"修复 {metric}: {fix_count} 行设置为 0.0")
                rows_fixed += fix_count
            # 对于 tests_total，设置为 0（整数）
            elif metric == 'tests_total':
                df.loc[mask, metric] = 0
                print(f"修复 {metric}: {fix_count} 行设置为 0")
                rows_fixed += fix_count
    
    print(f"\n总共修复了 {rows_fixed} 个空值")
    
    # 检查修复后的情况
    print("\n修复后检查:")
    for metric in test_metrics:
        empty_count = df[metric].isna().sum()
        print(f"{metric} 空值数量: {empty_count}/{len(df)}")
    
    # 保存修复后的文件
    output_file = input_file  # 覆盖原文件
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n已保存修复后的文件: {output_file}")
    
    # 显示一些修复示例
    print("\n修复示例:")
    fixed_rows = df[(df['compilation_success'] == 0.0) & (df['test_pass_rate'] == 0.0)]
    if len(fixed_rows) > 0:
        sample = fixed_rows.head(3)
        for _, row in sample.iterrows():
            print(f"模型: {row['model']}, 编译成功: {row['compilation_success']}, "
                  f"test_pass_rate: {row['test_pass_rate']}, tests_passed: {row['tests_passed']}, "
                  f"tests_total: {row['tests_total']}")
    
    return df

if __name__ == '__main__':
    fix_code_test_metrics()