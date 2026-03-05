# -*- coding: utf-8 -*-
"""
文本摘要质量评估脚本

评估所有模型在文本摘要任务上的表现
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.summary_evaluator import SummaryEvaluator
from summary_config import SUMMARY_SOURCE_TEXTS, SUMMARY_LENGTH_REQUIREMENTS


def evaluate_summary_quality(data_dir: Path, output_dir: Path, 
                             use_bertscore: bool = True,
                             use_bartscore: bool = False):
    """评估文本摘要任务质量"""
    
    print("\n" + "="*60)
    print("📝 Summary Quality Evaluation")
    print("="*60)
    
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
        'use_bartscore': use_bartscore,
        'device': 'cuda',
        'lang': 'zh'
    }
    evaluator = SummaryEvaluator(config)
    
    print(f"\n⚙️  Configuration:")
    print(f"   - BERTScore: {'✅ Enabled' if use_bertscore else '❌ Disabled'}")
    print(f"   - BARTScore: {'✅ Enabled' if use_bartscore else '❌ Disabled'}")
    print(f"   - Device: {config['device']}")
    print(f"   - Language: {config['lang']}")
    
    # 评估每个模型的每个响应
    results = []
    
    total_evaluations = len(df) * len([c for c in df.columns if c != 'model'])
    
    with tqdm(total=total_evaluations, desc="Evaluating") as pbar:
        for _, row in df.iterrows():
            model = row['model']
            
            for col in df.columns:
                if col == 'model':
                    continue
                
                response = row[col]
                
                if pd.isna(response) or len(str(response).strip()) == 0:
                    pbar.update(1)
                    continue
                
                # 获取原文和字数要求
                source_text = SUMMARY_SOURCE_TEXTS.get(col)
                length_req = SUMMARY_LENGTH_REQUIREMENTS.get(col)
                
                if source_text is None:
                    print(f"\n⚠️  No source text for {col}")
                    pbar.update(1)
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
                
                pbar.update(1)
    
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
    
    if 'bertscore_f1' in df.columns and df['bertscore_f1'].notna().any():
        print(f"\n🎯 Top 3 Models by BERTScore F1:")
        top_models = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            if pd.notna(score):
                print(f"  {rank}. {model}: {score:.4f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_file = output_dir / 'summary_quality_report.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 文本摘要质量评估报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 评估概览\n\n")
        f.write(f"- 评估模型数: {df['model'].nunique()}\n")
        f.write(f"- 评估问题数: {df['question_id'].nunique()}\n")
        f.write(f"- 总评估次数: {len(df)}\n\n")
        
        f.write("## 2. 核心指标排名\n\n")
        
        # ROUGE-L排名
        if 'rouge_l_f1' in df.columns:
            f.write("### 2.1 ROUGE-L F1 排名\n\n")
            f.write("ROUGE-L衡量摘要的结构完整性和信息保留度。\n\n")
            rouge_ranking = df.groupby('model')['rouge_l_f1'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(rouge_ranking.items(), 1):
                f.write(f"{rank}. **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # BERTScore排名
        if 'bertscore_f1' in df.columns and df['bertscore_f1'].notna().any():
            f.write("### 2.2 BERTScore F1 排名\n\n")
            f.write("BERTScore衡量摘要的语义相似度。\n\n")
            bert_ranking = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(bert_ranking.items(), 1):
                if pd.notna(score):
                    f.write(f"{rank}. **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 压缩比分析
        if 'compression_ratio' in df.columns:
            f.write("### 2.3 压缩比分析\n\n")
            f.write("压缩比衡量摘要的简洁性（理想范围：0.2-0.4）。\n\n")
            comp_stats = df.groupby('model')['compression_ratio'].mean().sort_values()
            for model, ratio in comp_stats.items():
                status = "✅" if 0.2 <= ratio <= 0.4 else "⚠️"
                f.write(f"- {status} **{model}**: {ratio:.3f}\n")
            f.write("\n")
        
        # 字数符合度
        if 'in_range' in df.columns:
            f.write("### 2.4 字数符合度\n\n")
            f.write("字数符合度衡量摘要是否满足字数要求。\n\n")
            compliance = df.groupby('model')['in_range'].mean().sort_values(ascending=False)
            for model, rate in compliance.items():
                status = "✅" if rate >= 0.8 else "⚠️"
                f.write(f"- {status} **{model}**: {rate:.1%}\n")
            f.write("\n")
        
        # 信息密度
        if 'information_density' in df.columns and df['information_density'].notna().any():
            f.write("### 2.5 信息密度排名\n\n")
            f.write("信息密度衡量单位长度内的信息量（越高越好）。\n\n")
            density_ranking = df.groupby('model')['information_density'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(density_ranking.items(), 1):
                if pd.notna(score):
                    f.write(f"{rank}. **{model}**: {score:.4f}\n")
            f.write("\n")
        
        f.write("## 3. 指标说明\n\n")
        f.write("### 3.1 ROUGE-L F1\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 基于最长公共子序列的F1分数\n")
        f.write("- **解释**: 0.6-1.0 优秀，0.4-0.6 中等，0.0-0.4 较差\n\n")
        
        f.write("### 3.2 BERTScore F1\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 基于BERT的语义相似度\n")
        f.write("- **解释**: 0.8-1.0 优秀，0.6-0.8 良好，0.0-0.6 较差\n\n")
        
        f.write("### 3.3 压缩比\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 摘要长度/原文长度\n")
        f.write("- **解释**: 0.2-0.4 合理，<0.2 过度压缩，>0.4 不够简洁\n\n")
        
        f.write("### 3.4 信息密度\n")
        f.write("- **范围**: [0, +∞)\n")
        f.write("- **含义**: ROUGE-L召回率 / 压缩比\n")
        f.write("- **解释**: 越高表示用更少的字表达更多信息\n\n")
        
        f.write("## 4. 详细数据\n\n")
        f.write("详细评分数据请参考:\n")
        f.write("- `summary_quality_scores.csv` - 每个模型每个问题的详细评分\n")
        f.write("- `summary_quality_summary.csv` - 按模型汇总的统计数据\n")
    
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
    parser.add_argument('--no-bertscore', action='store_true',
                       help='禁用BERTScore（加快评估速度）')
    parser.add_argument('--use-bartscore', action='store_true',
                       help='启用BARTScore（需要GPU，评估较慢）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_summary_quality(
        data_dir, 
        output_dir,
        use_bertscore=not args.no_bertscore,
        use_bartscore=args.use_bartscore
    )
