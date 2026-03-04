"""
代码生成任务质量评估脚本

批量评估所有模型在代码生成任务上的质量
"""

import sys
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import argparse

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation import CodeEvaluator


def load_responses_data(data_file: Path) -> pd.DataFrame:
    """
    加载回答数据
    
    Args:
        data_file: 数据文件路径
    
    Returns:
        pd.DataFrame: 回答数据
    """
    print(f"📂 Loading data from: {data_file}")
    
    try:
        df = pd.read_csv(data_file, encoding='utf-8-sig')
        print(f"✓ Loaded {len(df)} records")
        return df
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        sys.exit(1)


def evaluate_code_task(df: pd.DataFrame, config: dict = None) -> pd.DataFrame:
    """
    评估代码生成任务
    
    Args:
        df: 包含所有回答的数据框
        config: 评估器配置
            - enable_execution: 是否启用代码执行测试
            - verbose: 是否输出详细信息
    
    Returns:
        pd.DataFrame: 包含质量评分的数据框
    """
    # 筛选代码生成任务
    code_df = df[df['task_type'] == 'code'].copy()
    
    if len(code_df) == 0:
        print("⚠️  No code generation tasks found")
        return pd.DataFrame()
    
    enable_execution = config.get('enable_execution', False) if config else False
    
    print(f"\n📊 Evaluating {len(code_df)} code generation samples")
    print(f"   Models: {code_df['model'].nunique()}")
    print(f"   Samples per model: ~{len(code_df) // code_df['model'].nunique()}")
    print(f"   Code execution: {'✅ Enabled' if enable_execution else '❌ Disabled'}")
    
    # 初始化评估器
    evaluator = CodeEvaluator(config)
    
    # 评估每个样本
    results = []
    
    for idx, row in tqdm(code_df.iterrows(), total=len(code_df), desc="Evaluating"):
        # 提取生成的代码和提示词
        generated_code = row['response']
        prompt = row['prompt']
        
        # 评估质量
        try:
            # 传递prompt用于提取测试用例
            context = {'prompt': prompt}
            scores = evaluator.evaluate(generated_code, context=context)
            
            # 添加元数据
            result = {
                'experiment_id': row['experiment_id'],
                'model': row['model'],
                'task_type': row['task_type'],
                'prompt': row['prompt'][:100] + '...' if len(row['prompt']) > 100 else row['prompt'],
                **scores  # 展开所有质量指标
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"\n⚠️  Error evaluating {row['experiment_id']}: {e}")
            continue
    
    # 转换为数据框
    results_df = pd.DataFrame(results)
    
    return results_df


def generate_summary_statistics(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    生成汇总统计
    
    Args:
        results_df: 评估结果数据框
    
    Returns:
        pd.DataFrame: 汇总统计数据框
    """
    if len(results_df) == 0:
        return pd.DataFrame()
    
    # 按模型分组统计
    summary = results_df.groupby('model').agg({
        'compilation_rate': ['mean', 'std', 'count'],
        'code_length': ['mean', 'std', 'min', 'max'],
        'cyclomatic_complexity': ['mean', 'std', 'min', 'max'],
        'has_code': ['mean']
    }).round(4)
    
    # 展平多级列名
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    
    return summary


def print_summary_report(summary_df: pd.DataFrame):
    """
    打印汇总报告
    
    Args:
        summary_df: 汇总统计数据框
    """
    if len(summary_df) == 0:
        return
    
    print("\n" + "="*80)
    print("📊 CODE GENERATION QUALITY SUMMARY")
    print("="*80)
    
    # 按编译成功率排序
    summary_sorted = summary_df.sort_values('compilation_rate_mean', ascending=False)
    
    print("\n🏆 Top Models by Compilation Rate:")
    print("-" * 80)
    
    for idx, row in summary_sorted.head(5).iterrows():
        print(f"{idx+1}. {row['model']:<30} "
              f"Compilation: {row['compilation_rate_mean']:.2%} "
              f"(n={int(row['compilation_rate_count'])})")
    
    print("\n📏 Code Length Statistics:")
    print("-" * 80)
    
    for idx, row in summary_sorted.head(5).iterrows():
        print(f"{idx+1}. {row['model']:<30} "
              f"Avg Length: {row['code_length_mean']:.1f} lines "
              f"(range: {int(row['code_length_min'])}-{int(row['code_length_max'])})")
    
    print("\n🔄 Cyclomatic Complexity:")
    print("-" * 80)
    
    for idx, row in summary_sorted.head(5).iterrows():
        print(f"{idx+1}. {row['model']:<30} "
              f"Avg Complexity: {row['cyclomatic_complexity_mean']:.1f} "
              f"(range: {int(row['cyclomatic_complexity_min'])}-{int(row['cyclomatic_complexity_max'])})")
    
    print("\n" + "="*80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='评估代码生成任务质量',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础评估
  python evaluate_code_quality.py
  
  # 详细输出
  python evaluate_code_quality.py --verbose
  
  # 指定输入输出路径
  python evaluate_code_quality.py --input data/analize/pre_data/responses_raw.csv --output data/analize/pre_data
        """
    )
    
    parser.add_argument('--input', type=str, 
                       default='data/analize/pre_data/responses_raw.csv',
                       help='输入数据文件路径')
    parser.add_argument('--output-dir', type=str, 
                       default='data/analize/pre_data',
                       help='输出目录')
    parser.add_argument('--verbose', action='store_true',
                       help='输出详细信息')
    parser.add_argument('--enable-execution', action='store_true',
                       help='启用代码执行测试（验证正确性）')
    
    args = parser.parse_args()
    
    # 配置
    config = {
        'verbose': args.verbose,
        'enable_execution': args.enable_execution
    }
    
    # 路径
    input_file = Path(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*80)
    print("🚀 CODE GENERATION QUALITY EVALUATION")
    print("="*80)
    print(f"Input:  {input_file}")
    print(f"Output: {output_dir}")
    print(f"Verbose: {args.verbose}")
    print(f"Code Execution: {args.enable_execution}")
    print("="*80)
    
    # 加载数据
    df = load_responses_data(input_file)
    
    # 评估代码质量
    results_df = evaluate_code_task(df, config)
    
    if len(results_df) == 0:
        print("\n❌ No results to save")
        return
    
    # 保存详细结果
    output_file = output_dir / 'quality_scores_code.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ Detailed results saved: {output_file}")
    
    # 生成汇总统计
    summary_df = generate_summary_statistics(results_df)
    
    if len(summary_df) > 0:
        summary_file = output_dir / 'quality_summary_code.csv'
        summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"✅ Summary statistics saved: {summary_file}")
        
        # 打印汇总报告
        print_summary_report(summary_df)
    
    # 打印整体统计
    print("\n📈 Overall Statistics:")
    print("-" * 80)
    print(f"Total samples evaluated: {len(results_df)}")
    print(f"Models evaluated: {results_df['model'].nunique()}")
    print(f"Overall compilation rate: {results_df['compilation_rate'].mean():.2%}")
    print(f"Samples with code: {results_df['has_code'].mean():.2%}")
    print(f"Average code length: {results_df['code_length'].mean():.1f} lines")
    print(f"Average complexity: {results_df['cyclomatic_complexity'].mean():.1f}")
    
    print("\n" + "="*80)
    print("✅ CODE QUALITY EVALUATION COMPLETED!")
    print("="*80)


if __name__ == '__main__':
    main()
