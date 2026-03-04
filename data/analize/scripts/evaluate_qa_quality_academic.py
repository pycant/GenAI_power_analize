# -*- coding: utf-8 -*-
"""
问答任务质量批量评估脚本 - 学术标准版

使用传统NLP指标: EM, F1, BERTScore, ROUGE-L, BLEU
"""

import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from quality_evaluation.qa_evaluator import QAEvaluator

# 标准答案
REFERENCE_ANSWERS = {
    'q01': 'Quicksort',
    'q02': 'Range search: Given values a and b, find all the records whose key value is in the range a, b.',
    'q03': 'It is a scanner which works by injecting packets to a range of addresses, and inferring what hosts and services might be at those addresses, based on the responses',
    'q04': '{AND, OR}',
    'q05': 'Privacy'
}


def evaluate_qa_quality(data_dir: Path, output_dir: Path, use_bertscore: bool = False):
    """评估问答任务质量 - 学术标准指标"""
    
    print("\n" + "="*60)
    print("❓ Question Answering Quality Evaluation (Academic)")
    print("="*60)
    print(f"📊 Metrics: EM, F1, ROUGE-L, BLEU" + (", BERTScore" if use_bertscore else ""))
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/qa/qa_responses.csv'
    
    if not responses_file.exists():
        print(f"❌ Error: File not found: {responses_file}")
        return None
    
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_bertscore': use_bertscore,
        'device': 'cuda',
        'lang': 'en'
    }
    evaluator = QAEvaluator(config)
    
    # 评估每个模型的每个响应
    results = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating models"):
        model = row['model']
        
        for col in df.columns:
            if col == 'model':
                continue
            
            response = row[col]
            
            if pd.isna(response) or len(str(response).strip()) == 0:
                continue
            
            # 获取标准答案
            reference = REFERENCE_ANSWERS.get(col)
            
            if reference is None:
                print(f"⚠️  No reference answer for {col}")
                continue
            
            # 评估质量
            scores = evaluator.evaluate(str(response), reference=reference)
            
            # 提取extracted_answer(如果有)
            extracted_answer = scores.pop('extracted_answer', None)
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                'reference_answer': reference,
                'extracted_answer': extracted_answer,
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'qa_quality_scores_academic.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
    # 生成报告
    generate_report(results_df, output_dir)
    
    return results_df



def generate_summary_stats(df: pd.DataFrame, output_dir: Path):
    """生成汇总统计"""
    
    print(f"\n📊 Generating summary statistics...")
    
    # 按模型汇总
    metric_cols = [col for col in df.columns 
                   if col not in ['model', 'question_id', 'reference_answer', 'extracted_answer'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'qa_quality_summary_academic.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'exact_match' in df.columns:
        print(f"\n🏆 Top 3 Models by Exact Match:")
        top_models = df.groupby('model')['exact_match'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")
    
    if 'f1_score' in df.columns:
        print(f"\n🎯 Top 3 Models by F1 Score:")
        top_models = df.groupby('model')['f1_score'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_lines = []
    report_lines.append("# 问答任务质量评估报告 (学术标准)")
    report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**评估模型数**: {df['model'].nunique()}")
    report_lines.append(f"**评估样本数**: {len(df)}")
    report_lines.append("")
    
    # 评估指标说明
    report_lines.append("## 评估指标说明")
    report_lines.append("")
    report_lines.append("### 核心指标")
    report_lines.append("- **Exact Match (EM)**: 预测答案与标准答案完全匹配")
    report_lines.append("- **F1 Score**: 词级别的精确率和召回率调和平均")
    report_lines.append("- **BERTScore**: 基于BERT的语义相似度(可选)")
    report_lines.append("")
    report_lines.append("### 辅助指标")
    report_lines.append("- **ROUGE-L**: 基于最长公共子序列的F1分数")
    report_lines.append("- **BLEU**: 基于N-gram的精确率")
    report_lines.append("")
    
    # 整体统计
    report_lines.append("## 整体统计")
    report_lines.append("")
    report_lines.append("| 指标 | 均值 | 标准差 | 最小值 | 最大值 |")
    report_lines.append("|------|------|--------|--------|--------|")
    
    key_metrics = ['exact_match', 'f1_score', 'rouge_l', 'bleu']
    for metric in key_metrics:
        if metric in df.columns and df[metric].notna().sum() > 0:
            mean_val = df[metric].mean()
            std_val = df[metric].std()
            min_val = df[metric].min()
            max_val = df[metric].max()
            
            report_lines.append(f"| {metric} | {mean_val:.4f} | {std_val:.4f} | {min_val:.4f} | {max_val:.4f} |")
    
    report_lines.append("")
    
    # 模型排名
    report_lines.append("## 模型排名")
    report_lines.append("")
    report_lines.append("### 按Exact Match排名")
    report_lines.append("")
    report_lines.append("| 排名 | 模型 | EM | F1 | ROUGE-L | BLEU |")
    report_lines.append("|------|------|----|----|---------|------|")
    
    model_stats = df.groupby('model').agg({
        'exact_match': 'mean',
        'f1_score': 'mean',
        'rouge_l': 'mean',
        'bleu': 'mean'
    }).sort_values('exact_match', ascending=False)
    
    for rank, (model, row) in enumerate(model_stats.iterrows(), 1):
        report_lines.append(
            f"| {rank} | {model} | {row['exact_match']:.4f} | "
            f"{row['f1_score']:.4f} | {row['rouge_l']:.4f} | {row['bleu']:.4f} |"
        )
    
    report_lines.append("")
    
    # 按F1排名
    report_lines.append("### 按F1 Score排名")
    report_lines.append("")
    report_lines.append("| 排名 | 模型 | F1 | EM | ROUGE-L | BLEU |")
    report_lines.append("|------|------|----|----|---------| ------|")
    
    f1_stats = df.groupby('model').agg({
        'f1_score': 'mean',
        'exact_match': 'mean',
        'rouge_l': 'mean',
        'bleu': 'mean'
    }).sort_values('f1_score', ascending=False)
    
    for rank, (model, row) in enumerate(f1_stats.iterrows(), 1):
        report_lines.append(
            f"| {rank} | {model} | {row['f1_score']:.4f} | "
            f"{row['exact_match']:.4f} | {row['rouge_l']:.4f} | {row['bleu']:.4f} |"
        )
    
    report_lines.append("")
    
    # 按问题分析
    report_lines.append("## 按问题分析")
    report_lines.append("")
    report_lines.append("| 问题 | 平均EM | 平均F1 | 最高EM | 最低EM |")
    report_lines.append("|------|--------|--------|--------|--------|")
    
    question_stats = df.groupby('question_id').agg({
        'exact_match': ['mean', 'max', 'min'],
        'f1_score': 'mean'
    })
    
    for question_id, row in question_stats.iterrows():
        report_lines.append(
            f"| {question_id} | {row[('exact_match', 'mean')]:.4f} | "
            f"{row[('f1_score', 'mean')]:.4f} | {row[('exact_match', 'max')]:.4f} | "
            f"{row[('exact_match', 'min')]:.4f} |"
        )
    
    report_lines.append("")
    
    # 保存报告
    report_file = output_dir / 'qa_quality_report_academic.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估问答质量 - 学术标准')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/qa_quality_academic',
                       help='输出目录')
    parser.add_argument('--use-bertscore', action='store_true',
                       help='是否使用BERTScore(需要GPU)')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_qa_quality(data_dir, output_dir, use_bertscore=args.use_bertscore)
