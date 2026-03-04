#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证脚本

功能：
1. 验证 CSV 文件可以正确读取
2. 检查特殊字符（换行符、引号等）是否正确处理
3. 生成数据质量报告
"""

import pandas as pd
from pathlib import Path
import sys

# 确保输出使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def verify_data():
    """验证数据完整性和正确性"""
    
    data_file = Path('data/analize/pre_data/responses_raw.csv')
    
    if not data_file.exists():
        print(f"❌ 数据文件不存在: {data_file}")
        return
    
    print("="*60)
    print("数据验证报告")
    print("="*60 + "\n")
    
    # 读取数据
    print("📂 读取数据文件...")
    df = pd.read_csv(data_file, encoding='utf-8-sig')
    print(f"✅ 成功读取 {len(df)} 行数据\n")
    
    # 基本信息
    print("="*60)
    print("1. 基本信息")
    print("="*60)
    print(f"总行数: {len(df)}")
    print(f"总列数: {len(df.columns)}")
    print(f"模型数量: {df['model'].nunique()}")
    print(f"任务类型: {df['task_type'].nunique()}")
    print(f"文件大小: {data_file.stat().st_size / 1024:.2f} KB\n")
    
    # 列信息
    print("="*60)
    print("2. 列信息")
    print("="*60)
    print(df.dtypes)
    print()
    
    # 缺失值检查
    print("="*60)
    print("3. 缺失值检查")
    print("="*60)
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        '缺失数量': missing,
        '缺失比例(%)': missing_pct
    })
    print(missing_df[missing_df['缺失数量'] > 0])
    print()
    
    # 特殊字符验证
    print("="*60)
    print("4. 特殊字符处理验证")
    print("="*60)
    
    # 检查第一个包含换行符的回答
    sample_idx = 0
    sample_response = df.loc[sample_idx, 'response']
    
    print(f"样本索引: {sample_idx}")
    print(f"模型: {df.loc[sample_idx, 'model']}")
    print(f"任务: {df.loc[sample_idx, 'task_type']}")
    print(f"回答长度: {len(sample_response)} 字符")
    print(f"包含换行符: {'是' if '\\n' in sample_response else '否'}")
    print(f"\n回答预览（前 200 字符）:")
    print("-" * 60)
    print(sample_response[:200])
    print("-" * 60)
    print()
    
    # 模型分布
    print("="*60)
    print("5. 模型样本分布")
    print("="*60)
    model_counts = df['model'].value_counts().sort_index()
    print(model_counts)
    print()
    
    # 任务类型分布
    print("="*60)
    print("6. 任务类型分布")
    print("="*60)
    task_counts = df['task_type'].value_counts().sort_index()
    print(task_counts)
    print()
    
    # 性能指标统计
    print("="*60)
    print("7. 性能指标统计")
    print("="*60)
    metrics = ['throughput_tps', 'latency_s', 'gpu_energy_j', 'gpu_power_avg_w']
    stats = df[metrics].describe().round(2)
    print(stats)
    print()
    
    # 回答长度分布
    print("="*60)
    print("8. 回答长度分布")
    print("="*60)
    length_stats = df.groupby('task_type')['response_length'].agg(['count', 'mean', 'std', 'min', 'max']).round(2)
    print(length_stats)
    print()
    
    # 数据质量评分
    print("="*60)
    print("9. 数据质量评分")
    print("="*60)
    
    quality_score = 100
    issues = []
    
    # 检查缺失值
    critical_cols = ['model', 'task_type', 'response', 'throughput_tps', 'latency_s', 'gpu_energy_j']
    for col in critical_cols:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            quality_score -= 10
            issues.append(f"关键字段 '{col}' 有 {missing_count} 个缺失值")
    
    # 检查样本不均衡
    min_samples = model_counts.min()
    max_samples = model_counts.max()
    if max_samples - min_samples > 10:
        quality_score -= 5
        issues.append(f"样本不均衡：最少 {min_samples} 个，最多 {max_samples} 个")
    
    # 检查异常值
    if (df['throughput_tps'] < 0).any():
        quality_score -= 10
        issues.append("吞吐量存在负值")
    
    if (df['latency_s'] < 0).any():
        quality_score -= 10
        issues.append("延迟存在负值")
    
    print(f"数据质量评分: {quality_score}/100")
    
    if issues:
        print("\n⚠️  发现的问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n✅ 未发现数据质量问题")
    
    print("\n" + "="*60)
    print("✅ 数据验证完成！")
    print("="*60)


if __name__ == '__main__':
    verify_data()
