# -*- coding: utf-8 -*-
"""
问答任务质量批量评估脚本

评估所有模型在QA任务上的响应质量
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


def evaluate_qa_quality(data_dir: Path, output_dir: Path):
    """评估问答任务质量"""
    
    print("\n" + "="*60)
    print("❓ Question Answering Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/qa/qa_responses.csv'
    
    if not responses_file.exists():
        print(f"❌ Error: File not found: {responses_file}")
        return None
    
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    evaluator = QAEvaluator(config={'domain': 'cs'})
    
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
            
            # 评估质量
            scores = evaluator.evaluate(str(response))
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'qa_quality_scores.csv'
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
                   if col not in ['model', 'question_id'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'qa_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'confidence_score' in df.columns:
        print(f"\n🏆 Top 3 Models by Confidence Score:")
        top_models = df.groupby('model')['confidence_score'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.3f}")
    
    if 'technical_term_density' in df.columns:
        print(f"\n🎯 Top 3 Models by Technical Term Density:")
        top_models = df.groupby('model')['technical_term_density'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.3f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_lines = []
    report_lines.append("# 问答任务质量评估报告")
    report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**评估模型数**: {df['model'].nunique()}")
    report_lines.append(f"**评估样本数**: {len(df)}")
    report_lines.append("")
    
    # 评估指标说明
    report_lines.append("## 评估指标说明")
    report_lines.append("")
    report_lines.append("### 完整性指标")
    report_lines.append("- **Has Answer**: 是否包含答案")
    report_lines.append("- **Has Conclusion**: 是否有结论性语句")
    report_lines.append("- **Answer Length**: 答案长度")
    report_lines.append("")
    report_lines.append("### 专业性指标")
    report_lines.append("- **Technical Term Density**: 技术术语密度")
    report_lines.append("- **Technical Term Count**: 技术术语数量")
    report_lines.append("")
    report_lines.append("### 置信度指标")
    report_lines.append("- **Confidence Score**: 答案置信度")
    report_lines.append("- **Uncertainty Count**: 不确定性表达数量")
    report_lines.append("- **Certainty Count**: 确定性表达数量")
    report_lines.append("")
    report_lines.append("### 结构与推理指标")
    report_lines.append("- **Has Enumeration**: 是否有列举")
    report_lines.append("- **Has Reasoning**: 是否包含推理")
    report_lines.append("- **Reasoning Steps**: 推理步骤数")
    report_lines.append("- **Has Examples**: 是否有例子")
    report_lines.append("")
    
    # 整体统计
    report_lines.append("## 整体统计")
    report_lines.append("")
    report_lines.append("| 指标 | 均值 | 标准差 | 最小值 | 最大值 |")
    report_lines.append("|------|------|--------|--------|--------|")
    
    key_metrics = ['confidence_score', 'technical_term_density', 'has_reasoning', 'has_conclusion']
    for metric in key_metrics:
        if metric in df.columns:
            mean_val = df[metric].mean()
            std_val = df[metric].std()
            min_val = df[metric].min()
            max_val = df[metric].max()
            
            if df[metric].dtype == 'float64' and mean_val <= 1.0:
                report_lines.append(f"| {metric} | {mean_val:.2%} | {std_val:.2%} | {min_val:.2%} | {max_val:.2%} |")
            else:
                report_lines.append(f"| {metric} | {mean_val:.2f} | {std_val:.2f} | {min_val:.2f} | {max_val:.2f} |")
    
    report_lines.append("")
    
    # 模型排名
    report_lines.append("## 模型排名")
    report_lines.append("")
    report_lines.append("### 按置信度排名")
    report_lines.append("")
    report_lines.append("| 排名 | 模型 | 置信度 | 技术密度 | 推理率 | 平均步骤数 |")
    report_lines.append("|------|------|--------|----------|--------|------------|")
    
    model_stats = df.groupby('model').agg({
        'confidence_score': 'mean',
        'technical_term_density': 'mean',
        'has_reasoning': 'mean',
        'reasoning_steps': 'mean'
    }).sort_values('confidence_score', ascending=False)
    
    for rank, (model, row) in enumerate(model_stats.iterrows(), 1):
        report_lines.append(
            f"| {rank} | {model} | {row['confidence_score']:.2%} | "
            f"{row['technical_term_density']:.2%} | {row['has_reasoning']:.2%} | "
            f"{row['reasoning_steps']:.1f} |"
        )
    
    report_lines.append("")
    
    # 按技术密度排名
    report_lines.append("### 按技术术语密度排名")
    report_lines.append("")
    report_lines.append("| 排名 | 模型 | 技术密度 | 术语数量 | 答案长度 |")
    report_lines.append("|------|------|----------|----------|----------|")
    
    tech_stats = df.groupby('model').agg({
        'technical_term_density': 'mean',
        'technical_term_count': 'mean',
        'answer_length': 'mean'
    }).sort_values('technical_term_density', ascending=False)
    
    for rank, (model, row) in enumerate(tech_stats.iterrows(), 1):
        report_lines.append(
            f"| {rank} | {model} | {row['technical_term_density']:.2%} | "
            f"{row['technical_term_count']:.1f} | {row['answer_length']:.0f} |"
        )
    
    report_lines.append("")
    
    # 推理完整性分析
    report_lines.append("## 推理完整性分析")
    report_lines.append("")
    report_lines.append("| 模型 | 推理率 | 平均步骤数 | 有例子 | 有列举 |")
    report_lines.append("|------|--------|------------|--------|--------|")
    
    reasoning_stats = df.groupby('model').agg({
        'has_reasoning': 'mean',
        'reasoning_steps': 'mean',
        'has_examples': 'mean',
        'has_enumeration': 'mean'
    }).sort_values('has_reasoning', ascending=False)
    
    for model, row in reasoning_stats.iterrows():
        report_lines.append(
            f"| {model} | {row['has_reasoning']:.2%} | {row['reasoning_steps']:.1f} | "
            f"{row['has_examples']:.2%} | {row['has_enumeration']:.2%} |"
        )
    
    report_lines.append("")
    
    # 保存报告
    report_file = output_dir / 'qa_quality_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估问答质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/qa_quality',
                       help='输出目录')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_qa_quality(data_dir, output_dir)
