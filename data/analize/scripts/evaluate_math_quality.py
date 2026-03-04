"""
数学推理任务质量批量评估脚本

评估所有模型在数学推理任务上的表现，生成多维度质量指标。
"""

import sys
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.math_evaluator import MathEvaluator


# 标准答案配置
REFERENCE_ANSWERS = {
    'q01': '90',    # 利润计算
    'q02': '60',    # 百分比增长
    'q03': '5',     # 除法分配
    'q04': '21',    # 差值计算
    'q05': '66'     # 总和计算
}


def evaluate_math_quality(data_dir: Path, output_dir: Path, 
                          tolerance: float = 0.01):
    """
    评估数学推理任务质量
    
    Args:
        data_dir: 数据目录
        output_dir: 输出目录
        tolerance: 数值匹配容忍度（默认1%）
    """
    
    print("\n" + "="*60)
    print("🔢 Math Reasoning Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/math/math_responses.csv'
    
    if not responses_file.exists():
        print(f"❌ File not found: {responses_file}")
        return None
    
    print(f"\n📂 Loading data from: {responses_file}")
    df = pd.read_csv(responses_file)
    
    print(f"✅ Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {'tolerance': tolerance}
    
    print(f"\n⚙️  Configuration:")
    print(f"  - Numerical Match Tolerance: {tolerance:.1%}")
    print(f"  - Exact Match: ✅ Enabled")
    print(f"  - Reasoning Completeness: ✅ Enabled")
    
    evaluator = MathEvaluator(config)
    
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
            
            # 获取标准答案
            reference = REFERENCE_ANSWERS.get(col)
            
            # 评估质量
            scores = evaluator.evaluate(str(response), reference=reference)
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                'reference_answer': reference,
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存详细结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'math_quality_scores.csv'
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
                   if col not in ['model', 'question_id', 'reference_answer', 'extracted_answer'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'math_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型（按准确率排序）
    if 'exact_match' in df.columns:
        print(f"\n🏆 Top 3 Models by Exact Match:")
        top_models = df.groupby('model')['exact_match'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")
    
    if 'numerical_match' in df.columns:
        print(f"\n🎯 Top 3 Models by Numerical Match:")
        top_models = df.groupby('model')['numerical_match'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")
    
    # 打印推理完整性统计
    if 'has_reasoning' in df.columns:
        print(f"\n💭 Reasoning Completeness:")
        reasoning_rate = df.groupby('model')['has_reasoning'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(reasoning_rate.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")


def generate_analysis_report(df: pd.DataFrame, output_dir: Path):
    """生成分析报告"""
    
    print(f"\n📝 Generating analysis report...")
    
    report_lines = []
    report_lines.append("# 数学推理任务质量评估报告\n")
    report_lines.append(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append(f"**评估模型数**: {df['model'].nunique()}\n")
    report_lines.append(f"**评估样本数**: {len(df)}\n")
    
    # 指标说明
    report_lines.append("\n## 评估指标说明\n")
    report_lines.append("### 准确性指标\n")
    report_lines.append("- **Exact Match**: 精确匹配，答案完全正确\n")
    report_lines.append("- **Numerical Match**: 数值匹配，允许1%误差\n")
    
    report_lines.append("\n### 推理完整性指标\n")
    report_lines.append("- **Has Reasoning**: 是否包含推理关键词\n")
    report_lines.append("- **Step Count**: 推理步骤数量\n")
    report_lines.append("- **Has Calculation**: 是否包含计算式\n")
    
    report_lines.append("\n### 置信度指标\n")
    report_lines.append("- **Extraction Confidence**: 答案提取可靠性\n")
    report_lines.append("- **Has Answer**: 是否成功提取答案\n")
    
    # 整体统计
    report_lines.append("\n## 整体统计\n")
    report_lines.append("| 指标 | 均值 | 标准差 | 最小值 | 最大值 |\n")
    report_lines.append("|------|------|--------|--------|--------|\n")
    
    for col in ['exact_match', 'numerical_match', 'has_reasoning', 'has_calculation']:
        if col in df.columns and df[col].notna().any():
            mean_val = df[col].mean()
            std_val = df[col].std()
            min_val = df[col].min()
            max_val = df[col].max()
            report_lines.append(f"| {col} | {mean_val:.2%} | {std_val:.2%} | {min_val:.2%} | {max_val:.2%} |\n")
    
    # 模型排名 - 准确性
    report_lines.append("\n## 模型排名\n")
    
    if 'numerical_match' in df.columns:
        report_lines.append("\n### 按准确性排名（Numerical Match）\n")
        report_lines.append("| 排名 | 模型 | 准确率 | 推理率 | 平均步骤数 |\n")
        report_lines.append("|------|------|--------|--------|------------|\n")
        
        model_stats = df.groupby('model').agg({
            'numerical_match': 'mean',
            'has_reasoning': 'mean',
            'step_count': 'mean'
        }).sort_values('numerical_match', ascending=False)
        
        for rank, (model, row) in enumerate(model_stats.iterrows(), 1):
            report_lines.append(
                f"| {rank} | {model} | {row['numerical_match']:.2%} | "
                f"{row['has_reasoning']:.2%} | {row['step_count']:.1f} |\n"
            )
    
    # 按问题分析
    report_lines.append("\n## 按问题分析\n")
    report_lines.append("| 问题 | 平均准确率 | 最高准确率 | 最低准确率 |\n")
    report_lines.append("|------|------------|------------|------------|\n")
    
    if 'numerical_match' in df.columns:
        question_stats = df.groupby('question_id')['numerical_match'].agg(['mean', 'max', 'min'])
        
        for question, row in question_stats.iterrows():
            report_lines.append(
                f"| {question} | {row['mean']:.2%} | {row['max']:.2%} | {row['min']:.2%} |\n"
            )
    
    # 推理完整性分析
    if 'has_reasoning' in df.columns:
        report_lines.append("\n## 推理完整性分析\n")
        report_lines.append("| 模型 | 推理关键词 | 包含计算式 | 平均步骤数 |\n")
        report_lines.append("|------|------------|------------|------------|\n")
        
        reasoning_stats = df.groupby('model').agg({
            'has_reasoning': 'mean',
            'has_calculation': 'mean',
            'step_count': 'mean'
        }).sort_values('has_reasoning', ascending=False)
        
        for model, row in reasoning_stats.iterrows():
            report_lines.append(
                f"| {model} | {row['has_reasoning']:.2%} | "
                f"{row['has_calculation']:.2%} | {row['step_count']:.1f} |\n"
            )
    
    # 保存报告
    report_file = output_dir / 'math_quality_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    
    print(f"✅ Analysis report: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估数学推理质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/math_quality',
                       help='输出目录')
    parser.add_argument('--tolerance', type=float, default=0.01,
                       help='数值匹配容忍度（默认1%）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_math_quality(data_dir, output_dir, tolerance=args.tolerance)
