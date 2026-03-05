# -*- coding: utf-8 -*-
"""
逻辑推理质量评估脚本

评估所有模型在逻辑推理任务上的表现
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.reasoning_evaluator import ReasoningEvaluator
from reasoning_config import REASONING_REFERENCE_ANSWERS


def evaluate_reasoning_quality(data_dir: Path, output_dir: Path,
                               use_llm_judge: bool = False):
    """评估逻辑推理任务质量"""
    
    print("\n" + "="*60)
    print("🧠 Reasoning Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/reasoning/reasoning_responses.csv'
    prompts_file = data_dir / 'comparison_matrices/reasoning/reasoning_prompts.csv'
    
    if not responses_file.exists():
        print(f"❌ Error: File not found: {responses_file}")
        return None
    
    df_responses = pd.read_csv(responses_file)
    df_prompts = pd.read_csv(prompts_file)
    
    print(f"\n📂 Loaded {len(df_responses)} models")
    print(f"🧠 Questions: {len([c for c in df_responses.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_llm_judge': use_llm_judge,
        'llm_model': 'gpt-4'
    }
    evaluator = ReasoningEvaluator(config)
    
    print(f"\n⚙️  Configuration:")
    print(f"   - LLM-as-Judge: {'✅ Enabled' if use_llm_judge else '❌ Disabled'}")
    
    # 评估每个模型的每个响应
    results = []
    
    total_evaluations = len(df_responses) * len([c for c in df_responses.columns if c != 'model'])
    
    with tqdm(total=total_evaluations, desc="Evaluating") as pbar:
        for _, row in df_responses.iterrows():
            model = row['model']
            
            for col in df_responses.columns:
                if col == 'model':
                    continue
                
                response = row[col]
                
                if pd.isna(response) or len(str(response).strip()) == 0:
                    pbar.update(1)
                    continue
                
                # 获取标准答案和问题
                ref_data = REASONING_REFERENCE_ANSWERS.get(col)
                question_row = df_prompts[df_prompts['question_id'] == col]
                
                if ref_data is None or question_row.empty:
                    print(f"\n⚠️  No reference data for {col}")
                    pbar.update(1)
                    continue
                
                reference = ref_data['answer']
                question = question_row['prompt'].values[0]
                
                # 构建上下文
                context = {
                    'question': question,
                    'reasoning_type': ref_data['reasoning_type'],
                    'key_points': ref_data['key_points']
                }
                
                # 评估质量
                scores = evaluator.evaluate(
                    str(response),
                    reference=reference,
                    context=context
                )
                
                # 保存结果
                result = {
                    'model': model,
                    'question_id': col,
                    'reasoning_type': ref_data['reasoning_type'],
                    **scores
                }
                results.append(result)
                
                pbar.update(1)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'reasoning_quality_scores.csv'
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
                   if col not in ['model', 'question_id', 'reasoning_type'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'reasoning_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'conclusion_correct' in df.columns:
        print(f"\n🏆 Top 3 Models by Conclusion Correctness:")
        top_models = df.groupby('model')['conclusion_correct'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")
    
    if 'completeness_score' in df.columns:
        print(f"\n📝 Top 3 Models by Reasoning Completeness:")
        top_models = df.groupby('model')['completeness_score'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_file = output_dir / 'reasoning_quality_report.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 逻辑推理质量评估报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 评估概览\n\n")
        f.write(f"- 评估模型数: {df['model'].nunique()}\n")
        f.write(f"- 评估问题数: {df['question_id'].nunique()}\n")
        f.write(f"- 总评估次数: {len(df)}\n\n")
        
        f.write("## 2. 核心指标排名\n\n")
        
        # 结论正确性排名
        if 'conclusion_correct' in df.columns:
            f.write("### 2.1 结论正确性排名\n\n")
            f.write("结论正确性衡量最终答案是否正确。\n\n")
            correctness_ranking = df.groupby('model')['conclusion_correct'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(correctness_ranking.items(), 1):
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.2%}\n")
            f.write("\n")
        
        # 推理完整性排名
        if 'completeness_score' in df.columns:
            f.write("### 2.2 推理完整性排名\n\n")
            f.write("推理完整性衡量推理过程是否包含前提、步骤和结论。\n\n")
            completeness_ranking = df.groupby('model')['completeness_score'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(completeness_ranking.items(), 1):
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 逻辑连贯性排名
        if 'coherence_score' in df.columns:
            f.write("### 2.3 逻辑连贯性排名\n\n")
            f.write("逻辑连贯性衡量推理步骤之间的连贯性。\n\n")
            coherence_ranking = df.groupby('model')['coherence_score'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(coherence_ranking.items(), 1):
                f.write(f"{rank}. **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 按推理类型分析
        if 'reasoning_type' in df.columns and 'conclusion_correct' in df.columns:
            f.write("### 2.4 按推理类型分析\n\n")
            f.write("各模型在不同推理类型上的正确率：\n\n")
            type_analysis = df.groupby(['reasoning_type', 'model'])['conclusion_correct'].mean().unstack()
            f.write(type_analysis.to_markdown())
            f.write("\n\n")
        
        f.write("## 3. 指标说明\n\n")
        f.write("### 3.1 结论正确性\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 最终结论是否正确\n")
        f.write("- **解释**: 1.0 完全正确，0.0 完全错误\n\n")
        
        f.write("### 3.2 推理完整性\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 推理过程是否包含前提、步骤和结论\n")
        f.write("- **解释**: 0.8+ 优秀，0.6-0.8 良好，<0.6 需改进\n\n")
        
        f.write("### 3.3 逻辑连贯性\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 推理步骤之间的逻辑连贯性\n")
        f.write("- **解释**: 基于逻辑连接词密度评估\n\n")
        
        f.write("## 4. 详细数据\n\n")
        f.write("详细评分数据请参考:\n")
        f.write("- `reasoning_quality_scores.csv` - 每个模型每个问题的详细评分\n")
        f.write("- `reasoning_quality_summary.csv` - 按模型汇总的统计数据\n")
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估逻辑推理质量')
    parser.add_argument('--data-dir', type=str,
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/reasoning_quality',
                       help='输出目录')
    parser.add_argument('--use-llm-judge', action='store_true',
                       help='启用LLM-as-Judge（需要API，评估较慢）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_reasoning_quality(
        data_dir,
        output_dir,
        use_llm_judge=args.use_llm_judge
    )
