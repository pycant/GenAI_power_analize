# -*- coding: utf-8 -*-
"""
文本摘要任务质量批量评估脚本

使用指标: ROUGE-1/2/L, BERTScore, 压缩比, 字数符合度
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

from quality_evaluation.summary_evaluator import SummaryEvaluator
from summary_config import SUMMARY_SOURCE_TEXTS, SUMMARY_LENGTH_REQUIREMENTS


def evaluate_summary_quality(data_dir: Path, output_dir: Path, 
                             use_bertscore: bool = True):
    """评估文本摘要任务质量"""
    
    print("\n" + "="*60)
    print("📝 Summary Quality Evaluation")
    print("="*60)
    print(f"📊 Metrics: ROUGE-1/2/L, BERTScore, Compression Ratio, Length Compliance")
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/summary/summary_responses.csv'
    
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
        'lang': 'zh'
    }
    evaluator = SummaryEvaluator(config)
    
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
            
            # 获取原文和字数要求
            source_text = SUMMARY_SOURCE_TEXTS.get(col)
            length_req = SUMMARY_LENGTH_REQUIREMENTS.get(col)
            
            if source_text is None:
                print(f"⚠️  No source text for {col}")
                continue
            
            # 构建上下文
            context = {}
            if length_req:
                context['min_length'] = length_req['min']
                context['max_length'] = length_req['max']
            
            # 评估质量
            scores = evaluator.evaluate(
                str(response), 
                reference=source_text,
                context=context
            )
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                'source_length': len(source_text),
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'summary_quality_scores.csv'
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
                   if col not in ['model', 'question_id', 'source_length'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'summary_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'rouge_l_f1' in df.columns:
        print(f"\n🏆 Top 3 Models by ROUGE-L F1:")
        top_models = df.groupby('model')['rouge_l_f1'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")
    
    if 'bertscore_f1' in df.columns and df['bertscore_f1'].notna().sum() > 0:
        print(f"\n🎯 Top 3 Models by BERTScore F1:")
        top_models = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_lines = []
    report_lines.append("# 文本摘要质量评估报告\n")
    report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append(f"**评估模型数**: {df['model'].nunique()}\n")
    report_lines.append(f"**评估样本数**: {len(df)}\n")
    report_lines.append("")
    
    # 评估指标说明
    report_lines.append("## 评估指标说明\n")
    report_lines.append("### 核心指标\n")
    report_lines.append("- **ROUGE-L F1**: 基于最长公共子序列的F1分数，衡量结构完整性\n")
    report_lines.append("- **ROUGE-1/2 F1**: 基于Unigram/Bigram的F1分数，衡量词汇覆盖\n")
    report_lines.append("- **BERTScore F1**: 基于BERT的语义相似度\n")
    report_lines.append("- **压缩比**: 摘要长度/原文长度，衡量简洁性\n")
    report_lines.append("- **字数符合度**: 是否符合字数要求\n")
    report_lines.append("- **信息密度**: ROUGE-L召回率/压缩比，衡量信息效率\n")
    report_lines.append("")
    
    # 整体统计
    report_lines.append("## 整体统计\n")
    report_lines.append("| 指标 | 均值 | 标准差 | 最小值 | 最大值 |\n")
    report_lines.append("|------|------|--------|--------|--------|\n")
    
    key_metrics = ['rouge_l_f1', 'rouge_1_f1', 'rouge_2_f1', 'bertscore_f1', 
                   'compression_ratio', 'information_density']
    for metric in key_metrics:
        if metric in df.columns and df[metric].notna().sum() > 0:
            mean_val = df[metric].mean()
            std_val = df[metric].std()
            min_val = df[metric].min()
            max_val = df[metric].max()
            
            report_lines.append(f"| {metric} | {mean_val:.4f} | {std_val:.4f} | {min_val:.4f} | {max_val:.4f} |\n")
    
    report_lines.append("")
    
    # 模型排名
    report_lines.append("## 模型排名\n")
    report_lines.append("### 按ROUGE-L F1排名\n")
    report_lines.append("| 排名 | 模型 | ROUGE-L | ROUGE-1 | ROUGE-2 | BERTScore |\n")
    report_lines.append("|------|------|---------|---------|---------|----------|\n")
    
    model_stats = df.groupby('model').agg({
        'rouge_l_f1': 'mean',
        'rouge_1_f1': 'mean',
        'rouge_2_f1': 'mean',
        'bertscore_f1': 'mean'
    }).sort_values('rouge_l_f1', ascending=False)
    
    for rank, (model, row) in enumerate(model_stats.iterrows(), 1):
        bert_score = row['bertscore_f1'] if pd.notna(row['bertscore_f1']) else 0.0
        report_lines.append(
            f"| {rank} | {model} | {row['rouge_l_f1']:.4f} | "
            f"{row['rouge_1_f1']:.4f} | {row['rouge_2_f1']:.4f} | {bert_score:.4f} |\n"
        )
    
    report_lines.append("")
    
    # 压缩比分析
    if 'compression_ratio' in df.columns:
        report_lines.append("### 压缩比分析\n")
        report_lines.append("| 模型 | 平均压缩比 | 标准差 |\n")
        report_lines.append("|------|-----------|--------|\n")
        
        comp_stats = df.groupby('model')['compression_ratio'].agg(['mean', 'std']).sort_values('mean')
        for model, row in comp_stats.iterrows():
            report_lines.append(f"| {model} | {row['mean']:.3f} | {row['std']:.3f} |\n")
        
        report_lines.append("")
    
    # 字数符合度
    if 'in_range' in df.columns and df['in_range'].notna().sum() > 0:
        report_lines.append("### 字数符合度\n")
        report_lines.append("| 模型 | 符合率 | 平均长度 |\n")
        report_lines.append("|------|--------|----------|\n")
        
        compliance_stats = df.groupby('model').agg({
            'in_range': 'mean',
            'length': 'mean'
        }).sort_values('in_range', ascending=False)
        
        for model, row in compliance_stats.iterrows():
            report_lines.append(f"| {model} | {row['in_range']:.1%} | {row['length']:.0f} |\n")
        
        report_lines.append("")
    
    # 保存报告
    report_file = output_dir / 'summary_quality_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估文本摘要质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/summary_quality',
                       help='输出目录')
    parser.add_argument('--use-bertscore', action='store_true', default=True,
                       help='是否使用BERTScore（默认：是）')
    parser.add_argument('--no-bertscore', dest='use_bertscore', action='store_false',
                       help='不使用BERTScore')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_summary_quality(
        data_dir, 
        output_dir,
        use_bertscore=args.use_bertscore
    )
