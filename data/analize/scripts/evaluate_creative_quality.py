"""
创意写作任务质量批量评估脚本

评估所有模型在创意写作任务上的表现，生成多维度质量指标。
"""

import sys
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.creative_evaluator import CreativeEvaluator


def evaluate_creative_quality(data_dir: Path, output_dir: Path, 
                              use_ppl: bool = True, 
                              use_semantic: bool = False):
    """
    评估创意写作任务质量
    
    Args:
        data_dir: 数据目录
        output_dir: 输出目录
        use_ppl: 是否计算困惑度
        use_semantic: 是否计算语义多样性
    """
    
    print("\n" + "="*60)
    print("🎨 Creative Writing Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/creative/creative_responses.csv'
    
    if not responses_file.exists():
        print(f"❌ File not found: {responses_file}")
        return None
    
    print(f"\n📂 Loading data from: {responses_file}")
    df = pd.read_csv(responses_file)
    
    print(f"✅ Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_ppl': use_ppl,
        'use_semantic': use_semantic,
        'ppl_model': 'uer/gpt2-chinese-cluecorpussmall'
    }
    
    print(f"\n⚙️  Configuration:")
    print(f"  - Distinct-N: ✅ Enabled")
    print(f"  - Perplexity: {'✅ Enabled' if use_ppl else '❌ Disabled'}")
    print(f"  - Semantic Diversity: {'✅ Enabled' if use_semantic else '❌ Disabled'}")
    
    evaluator = CreativeEvaluator(config)
    
    # 评估每个模型的每个响应
    results = []
    
    print(f"\n🔄 Evaluating responses...")
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Models"):
        model = row['model']
        
        for col in df.columns:
            if col == 'model':
                continue
            
            # 提取响应文本
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
    
    # 保存详细结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'creative_quality_scores.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
    # 生成分析报告
    generate_analysis_report(results_df, output_dir)
    
    return results_df


def generate_summary_stats(df: pd.DataFrame, output_dir: Path):
    """生成汇总统计"""
    
    print(f"\n📊 Generating summary statistics...")
    
    # 按模型汇总
    metric_cols = [col for col in df.columns 
                   if col not in ['model', 'question_id'] and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'creative_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型（按Distinct-2排序）
    print(f"\n🏆 Top 3 Models by Distinct-2:")
    if 'distinct_2' in df.columns:
        top_models = df.groupby('model')['distinct_2'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")
    
    # 打印流畅性最好的模型
    if 'perplexity' in df.columns and df['perplexity'].notna().any():
        print(f"\n🎯 Top 3 Models by Fluency (lowest perplexity):")
        top_fluency = df.groupby('model')['perplexity'].mean().sort_values(ascending=True).head(3)
        for rank, (model, score) in enumerate(top_fluency.items(), 1):
            print(f"  {rank}. {model}: {score:.2f}")


def generate_analysis_report(df: pd.DataFrame, output_dir: Path):
    """生成分析报告"""
    
    print(f"\n📝 Generating analysis report...")
    
    report_lines = []
    report_lines.append("# 创意写作任务质量评估报告\n")
    report_lines.append(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append(f"**评估模型数**: {df['model'].nunique()}\n")
    report_lines.append(f"**评估样本数**: {len(df)}\n")
    
    # 指标说明
    report_lines.append("\n## 评估指标说明\n")
    report_lines.append("### 多样性指标\n")
    report_lines.append("- **Distinct-1**: 词级别多样性（去重率）\n")
    report_lines.append("- **Distinct-2**: 短语级别多样性（核心指标）\n")
    report_lines.append("- **Distinct-3**: 长短语多样性\n")
    
    if 'perplexity' in df.columns and df['perplexity'].notna().any():
        report_lines.append("\n### 流畅性指标\n")
        report_lines.append("- **Perplexity**: 困惑度，越低表示越流畅\n")
    
    if 'semantic_diversity' in df.columns and df['semantic_diversity'].notna().any():
        report_lines.append("\n### 语义多样性\n")
        report_lines.append("- **Semantic Diversity**: 句子间语义距离，越高越多样\n")
    
    # 整体统计
    report_lines.append("\n## 整体统计\n")
    report_lines.append("| 指标 | 均值 | 标准差 | 最小值 | 最大值 |\n")
    report_lines.append("|------|------|--------|--------|--------|\n")
    
    for col in ['distinct_1', 'distinct_2', 'distinct_3', 'perplexity']:
        if col in df.columns and df[col].notna().any():
            mean_val = df[col].mean()
            std_val = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            report_lines.append(f"| {col} | {mean_val:.4f} | {std_val:.4f} | {min_val:.4f} | {max_val:.4f} |\n")
    
    # 模型排名
    report_lines.append("\n## 模型排名\n")
    
    if 'distinct_2' in df.columns:
        report_lines.append("\n### 按多样性排名（Distinct-2）\n")
        report_lines.append("| 排名 | 模型 | Distinct-2 | Distinct-1 | Distinct-3 |\n")
        report_lines.append("|------|------|------------|------------|------------|\n")
        
        model_diversity = df.groupby('model')[['distinct_1', 'distinct_2', 'distinct_3']].mean()
        model_diversity = model_diversity.sort_values('distinct_2', ascending=False)
        
        for rank, (model, row) in enumerate(model_diversity.iterrows(), 1):
            report_lines.append(f"| {rank} | {model} | {row['distinct_2']:.4f} | {row['distinct_1']:.4f} | {row['distinct_3']:.4f} |\n")
    
    if 'perplexity' in df.columns and df['perplexity'].notna().any():
        report_lines.append("\n### 按流畅性排名（Perplexity，越低越好）\n")
        report_lines.append("| 排名 | 模型 | Perplexity |\n")
        report_lines.append("|------|------|------------|\n")
        
        model_fluency = df.groupby('model')['perplexity'].mean().sort_values(ascending=True)
        
        for rank, (model, score) in enumerate(model_fluency.items(), 1):
            report_lines.append(f"| {rank} | {model} | {score:.2f} |\n")
    
    # 保存报告
    report_file = output_dir / 'creative_quality_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    
    print(f"✅ Analysis report: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估创意写作质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/creative_quality',
                       help='输出目录')
    parser.add_argument('--no-ppl', action='store_true',
                       help='禁用困惑度计算（节省时间和显存）')
    parser.add_argument('--use-semantic', action='store_true',
                       help='启用语义多样性计算（需要额外模型）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_creative_quality(
        data_dir, 
        output_dir, 
        use_ppl=not args.no_ppl,
        use_semantic=args.use_semantic
    )
