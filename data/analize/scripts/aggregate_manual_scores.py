#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聚合人工评分结果

从填写完成的打分表中提取分数，计算统计数据，生成报告

使用方法:
    python aggregate_manual_scores.py
    
输入: data/analize/REASONING_MANUAL_SCORING_RUBRIC.md (填写完成的打分表)
输出: 
    - data/analize/results/reasoning_quality/manual_scores.csv
    - data/analize/results/reasoning_quality/manual_scores_summary.csv
    - data/analize/results/reasoning_quality/manual_scores_report.md
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data.analize.scripts.reasoning_config import REASONING_REFERENCE_ANSWERS


# 评分维度权重
DIMENSION_WEIGHTS = {
    'correctness': 0.40,
    'completeness': 0.25,
    'rigor': 0.20,
    'clarity': 0.10,
    'efficiency': 0.05
}


def parse_scoring_table(markdown_file):
    """
    从Markdown打分表中解析评分数据
    
    返回: DataFrame with columns [model, question, correctness, completeness, rigor, clarity, efficiency, total, notes]
    """
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取每个问题的评分表
    scores = []
    
    # 匹配每个问题的表格
    question_pattern = r'## 问题 (q\d+):.*?\n\n\*\*标准答案\*\*:.*?\n\n\|(.*?)\n\n'
    
    for match in re.finditer(question_pattern, content, re.DOTALL):
        question_id = match.group(1)
        table_content = match.group(2)
        
        # 解析表格行
        lines = table_content.strip().split('\n')
        
        for line in lines[2:]:  # 跳过表头和分隔线
            if not line.strip() or line.startswith('|---'):
                continue
            
            # 解析表格列
            cols = [col.strip() for col in line.split('|')]
            cols = [col for col in cols if col]  # 移除空列
            
            if len(cols) < 7:
                continue
            
            model = cols[0]
            
            # 检查是否有评分数据
            if not cols[1] or cols[1] == '':
                continue
            
            try:
                correctness = float(cols[1]) if cols[1] else np.nan
                completeness = float(cols[2]) if cols[2] else np.nan
                rigor = float(cols[3]) if cols[3] else np.nan
                clarity = float(cols[4]) if cols[4] else np.nan
                efficiency = float(cols[5]) if cols[5] else np.nan
                total = float(cols[6]) if cols[6] else np.nan
                notes = cols[7] if len(cols) > 7 else ''
                
                scores.append({
                    'model': model,
                    'question': question_id,
                    'correctness': correctness,
                    'completeness': completeness,
                    'rigor': rigor,
                    'clarity': clarity,
                    'efficiency': efficiency,
                    'total_raw': total,
                    'notes': notes
                })
            except (ValueError, IndexError) as e:
                print(f"警告: 解析 {model} 在 {question_id} 的评分时出错: {e}")
                continue
    
    if not scores:
        print("错误: 未找到任何评分数据。请确保打分表已填写完成。")
        return None
    
    df = pd.DataFrame(scores)
    return df


def calculate_weighted_scores(df):
    """计算加权总分和归一化分数"""
    # 计算加权总分
    df['weighted_total'] = (
        df['correctness'] * DIMENSION_WEIGHTS['correctness'] +
        df['completeness'] * DIMENSION_WEIGHTS['completeness'] +
        df['rigor'] * DIMENSION_WEIGHTS['rigor'] +
        df['clarity'] * DIMENSION_WEIGHTS['clarity'] +
        df['efficiency'] * DIMENSION_WEIGHTS['efficiency']
    )
    
    # 归一化到0-100
    df['normalized_score'] = (df['weighted_total'] / 5.0) * 100
    
    return df


def generate_summary_statistics(df):
    """生成汇总统计"""
    summary_data = []
    
    # 按模型汇总
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        summary_data.append({
            'model': model,
            'avg_correctness': model_data['correctness'].mean(),
            'avg_completeness': model_data['completeness'].mean(),
            'avg_rigor': model_data['rigor'].mean(),
            'avg_clarity': model_data['clarity'].mean(),
            'avg_efficiency': model_data['efficiency'].mean(),
            'avg_weighted_total': model_data['weighted_total'].mean(),
            'avg_normalized_score': model_data['normalized_score'].mean(),
            'std_normalized_score': model_data['normalized_score'].std(),
            'min_normalized_score': model_data['normalized_score'].min(),
            'max_normalized_score': model_data['normalized_score'].max(),
            'num_questions': len(model_data)
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('avg_normalized_score', ascending=False)
    
    return summary_df


def generate_question_analysis(df):
    """生成问题难度分析"""
    question_data = []
    
    for question in df['question'].unique():
        q_data = df[df['question'] == question]
        
        question_data.append({
            'question': question,
            'description': REASONING_REFERENCE_ANSWERS.get(question, {}).get('answer', ''),
            'avg_correctness': q_data['correctness'].mean(),
            'avg_completeness': q_data['completeness'].mean(),
            'avg_rigor': q_data['rigor'].mean(),
            'avg_clarity': q_data['clarity'].mean(),
            'avg_efficiency': q_data['efficiency'].mean(),
            'avg_normalized_score': q_data['normalized_score'].mean(),
            'std_normalized_score': q_data['normalized_score'].std(),
            'num_models': len(q_data)
        })
    
    question_df = pd.DataFrame(question_data)
    question_df = question_df.sort_values('avg_normalized_score', ascending=True)  # 难度从高到低
    
    return question_df


def generate_markdown_report(df, summary_df, question_df, output_path):
    """生成Markdown格式的报告"""
    report = []
    
    report.append("# 逻辑推理任务人工评分结果报告\n")
    report.append(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append(f"**评分模型数**: {df['model'].nunique()}\n")
    report.append(f"**评分问题数**: {df['question'].nunique()}\n")
    report.append(f"**总评分数**: {len(df)}\n\n")
    
    # 评分维度权重
    report.append("## 评分维度权重\n\n")
    report.append("| 维度 | 权重 |\n")
    report.append("|------|------|\n")
    report.append(f"| 结论正确性 | {DIMENSION_WEIGHTS['correctness']:.0%} |\n")
    report.append(f"| 推理完整性 | {DIMENSION_WEIGHTS['completeness']:.0%} |\n")
    report.append(f"| 逻辑严谨性 | {DIMENSION_WEIGHTS['rigor']:.0%} |\n")
    report.append(f"| 表达清晰度 | {DIMENSION_WEIGHTS['clarity']:.0%} |\n")
    report.append(f"| 推理效率 | {DIMENSION_WEIGHTS['efficiency']:.0%} |\n\n")
    
    # 模型排名
    report.append("## 模型综合排名\n\n")
    report.append("| 排名 | 模型 | 归一化分数 | 正确性 | 完整性 | 严谨性 | 清晰度 | 效率 |\n")
    report.append("|------|------|------------|--------|--------|--------|--------|------|\n")
    
    for idx, row in summary_df.iterrows():
        rank = idx + 1
        report.append(
            f"| {rank} | {row['model']} | {row['avg_normalized_score']:.2f} | "
            f"{row['avg_correctness']:.2f} | {row['avg_completeness']:.2f} | "
            f"{row['avg_rigor']:.2f} | {row['avg_clarity']:.2f} | {row['avg_efficiency']:.2f} |\n"
        )
    
    report.append("\n")
    
    # 问题难度分析
    report.append("## 问题难度分析\n\n")
    report.append("按平均得分从低到高排序（得分越低，难度越高）\n\n")
    report.append("| 问题 | 描述 | 平均分 | 正确性 | 完整性 | 严谨性 | 清晰度 | 效率 |\n")
    report.append("|------|------|--------|--------|--------|--------|--------|------|\n")
    
    for idx, row in question_df.iterrows():
        report.append(
            f"| {row['question']} | {row['description']} | {row['avg_normalized_score']:.2f} | "
            f"{row['avg_correctness']:.2f} | {row['avg_completeness']:.2f} | "
            f"{row['avg_rigor']:.2f} | {row['avg_clarity']:.2f} | {row['avg_efficiency']:.2f} |\n"
        )
    
    report.append("\n")
    
    # 详细评分矩阵
    report.append("## 详细评分矩阵\n\n")
    
    for question in sorted(df['question'].unique()):
        q_info = REASONING_REFERENCE_ANSWERS.get(question, {})
        report.append(f"### {question}: {q_info.get('answer', '')}\n\n")
        
        q_data = df[df['question'] == question].sort_values('normalized_score', ascending=False)
        
        report.append("| 模型 | 归一化分数 | 正确性 | 完整性 | 严谨性 | 清晰度 | 效率 | 备注 |\n")
        report.append("|------|------------|--------|--------|--------|--------|------|------|\n")
        
        for _, row in q_data.iterrows():
            notes = row['notes'][:50] + '...' if len(row['notes']) > 50 else row['notes']
            report.append(
                f"| {row['model']} | {row['normalized_score']:.2f} | "
                f"{row['correctness']:.1f} | {row['completeness']:.1f} | "
                f"{row['rigor']:.1f} | {row['clarity']:.1f} | {row['efficiency']:.1f} | "
                f"{notes} |\n"
            )
        
        report.append("\n")
    
    # 统计摘要
    report.append("## 统计摘要\n\n")
    report.append(f"- **最高平均分**: {summary_df['avg_normalized_score'].max():.2f} ({summary_df.iloc[0]['model']})\n")
    report.append(f"- **最低平均分**: {summary_df['avg_normalized_score'].min():.2f} ({summary_df.iloc[-1]['model']})\n")
    report.append(f"- **平均分差距**: {summary_df['avg_normalized_score'].max() - summary_df['avg_normalized_score'].min():.2f}\n")
    report.append(f"- **整体平均分**: {df['normalized_score'].mean():.2f}\n")
    report.append(f"- **整体标准差**: {df['normalized_score'].std():.2f}\n\n")
    
    report.append("## 维度分析\n\n")
    report.append(f"- **正确性平均分**: {df['correctness'].mean():.2f} / 5.0\n")
    report.append(f"- **完整性平均分**: {df['completeness'].mean():.2f} / 5.0\n")
    report.append(f"- **严谨性平均分**: {df['rigor'].mean():.2f} / 5.0\n")
    report.append(f"- **清晰度平均分**: {df['clarity'].mean():.2f} / 5.0\n")
    report.append(f"- **效率平均分**: {df['efficiency'].mean():.2f} / 5.0\n\n")
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(''.join(report))
    
    print(f"✓ 报告已生成: {output_path}")


def main():
    # 文件路径
    rubric_file = project_root / "data" / "analize" / "REASONING_MANUAL_SCORING_RUBRIC_FILLED.md"
    output_dir = project_root / "data" / "analize" / "results" / "reasoning_quality"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scores_file = output_dir / "manual_scores.csv"
    summary_file = output_dir / "manual_scores_summary.csv"
    question_file = output_dir / "manual_scores_by_question.csv"
    report_file = output_dir / "manual_scores_report.md"
    
    print("=" * 80)
    print("逻辑推理任务人工评分聚合工具")
    print("=" * 80)
    print()
    
    # 检查输入文件
    if not rubric_file.exists():
        print(f"错误: 找不到打分表文件 {rubric_file}")
        sys.exit(1)
    
    print(f"读取打分表: {rubric_file}")
    
    # 解析评分数据
    df = parse_scoring_table(rubric_file)
    
    if df is None or len(df) == 0:
        print("\n错误: 未找到评分数据或打分表未填写完成")
        print("请确保已在打分表中填写所有模型和问题的评分")
        sys.exit(1)
    
    print(f"✓ 成功解析 {len(df)} 条评分记录")
    print(f"  - 模型数: {df['model'].nunique()}")
    print(f"  - 问题数: {df['question'].nunique()}")
    print()
    
    # 计算加权分数
    print("计算加权分数...")
    df = calculate_weighted_scores(df)
    print("✓ 加权分数计算完成")
    print()
    
    # 生成汇总统计
    print("生成汇总统计...")
    summary_df = generate_summary_statistics(df)
    question_df = generate_question_analysis(df)
    print("✓ 汇总统计生成完成")
    print()
    
    # 保存结果
    print("保存结果文件...")
    df.to_csv(scores_file, index=False, encoding='utf-8-sig')
    print(f"✓ 详细评分已保存: {scores_file}")
    
    summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
    print(f"✓ 模型汇总已保存: {summary_file}")
    
    question_df.to_csv(question_file, index=False, encoding='utf-8-sig')
    print(f"✓ 问题分析已保存: {question_file}")
    print()
    
    # 生成报告
    print("生成Markdown报告...")
    generate_markdown_report(df, summary_df, question_df, report_file)
    print()
    
    # 显示Top 3模型
    print("=" * 80)
    print("Top 3 模型 (按归一化分数排序)")
    print("=" * 80)
    for idx, row in summary_df.head(3).iterrows():
        print(f"{idx + 1}. {row['model']}: {row['avg_normalized_score']:.2f}")
    print()
    
    print("=" * 80)
    print("聚合完成!")
    print("=" * 80)


if __name__ == '__main__':
    main()
