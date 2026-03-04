"""
代码生成质量评估脚本 v2.0 - 多维度独立评分

实现方案B：保留所有维度的独立指标，不强制聚合
"""

import sys
import argparse
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation import CodeEvaluator


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Code Generation Quality Evaluation v2.0 - Multi-dimensional Independent Scoring'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        default='data/analize/pre_data/responses_raw.csv',
        help='Input CSV file with responses'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/analize/pre_data',
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--enable-execution',
        action='store_true',
        help='Enable code execution and testing'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Print detailed evaluation results'
    )
    
    return parser.parse_args()


def load_data(input_file: str) -> pd.DataFrame:
    """加载数据"""
    print(f"📂 Loading data from: {input_file}")
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"✓ Loaded {len(df)} records")
    return df


def evaluate_code_samples(df: pd.DataFrame, enable_execution: bool = False, 
                          verbose: bool = False) -> pd.DataFrame:
    """
    评估代码样本（多维度）
    
    Args:
        df: 包含代码样本的数据框
        enable_execution: 是否启用代码执行测试
        verbose: 是否打印详细信息
    
    Returns:
        pd.DataFrame: 评估结果
    """
    # 筛选代码生成任务
    code_samples = df[df['task_type'] == 'code'].copy()
    
    if len(code_samples) == 0:
        print("⚠️  No code generation samples found")
        return pd.DataFrame()
    
    print(f"\n📊 Evaluating {len(code_samples)} code generation samples")
    print(f"   Models: {code_samples['model'].nunique()}")
    print(f"   Samples per model: ~{len(code_samples) // code_samples['model'].nunique()}")
    print(f"   Code execution: {'✅ Enabled' if enable_execution else '❌ Disabled'}")
    
    # 初始化评估器
    config = {
        'enable_execution': enable_execution,
        'execution_timeout': 5,
        'verbose': verbose
    }
    evaluator = CodeEvaluator(config)
    
    # 评估所有样本
    results = []
    
    for idx, row in tqdm(code_samples.iterrows(), total=len(code_samples), desc="Evaluating"):
        try:
            experiment_id = row['experiment_id']
            model = row['model']
            task_type = row['task_type']
            prompt = row.get('prompt', '')
            response = row['response']
            
            # 评估代码质量（多维度）
            context = {
                'language': 'python',
                'prompt': prompt
            }
            
            scores = evaluator.evaluate(response, context=context)
            
            # 获取维度评分
            dimension_scores = evaluator.get_dimension_scores(scores)
            
            # 合并所有指标
            result = {
                'experiment_id': experiment_id,
                'model': model,
                'task_type': task_type,
                'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            }
            
            # 添加所有原始指标
            result.update(scores)
            
            # 添加维度评分
            result.update(dimension_scores)
            
            results.append(result)
            
            # 详细输出（前3个样本）
            if verbose and idx < 3:
                print(f"\n{'='*80}")
                print(f"Sample {idx + 1}: {model} - {task_type}")
                print(f"{'='*80}")
                print(f"📊 Functional Dimension: {dimension_scores.get('functional_dimension', 0):.2f}")
                print(f"   - Functional correctness: {scores.get('functional_correctness', 0):.2f}")
                print(f"   - Compilation success: {scores.get('compilation_success', 0):.2f}")
                if scores.get('test_pass_rate') is not None:
                    print(f"   - Test pass rate: {scores['test_pass_rate']:.2f} ({scores.get('tests_passed', 0)}/{scores.get('tests_total', 0)})")
                
                eff_dim = dimension_scores.get('efficiency_dimension')
                if eff_dim is not None:
                    print(f"⚡ Efficiency Dimension: {eff_dim:.2f}")
                    print(f"   - Time complexity: {scores.get('time_complexity_score', 0):.2f}")
                    print(f"   - Space complexity: {scores.get('space_complexity_score', 0):.2f}")
                
                qual_dim = dimension_scores.get('quality_dimension')
                if qual_dim is not None:
                    print(f"✨ Quality Dimension: {qual_dim:.2f}")
                    print(f"   - Simplicity: {scores.get('code_simplicity', 0):.2f}")
                    print(f"   - Length: {scores.get('code_length', 0)} lines")
                    print(f"   - Complexity: {scores.get('cyclomatic_complexity', 0)}")
                    print(f"   - Nesting depth: {scores.get('nesting_depth', 0)}")
                
                read_dim = dimension_scores.get('readability_dimension')
                if read_dim is not None:
                    print(f"📖 Readability Dimension: {read_dim:.2f}")
                    print(f"   - Has docstring: {scores.get('has_docstring', 0):.0f}")
                    print(f"   - Has type hints: {scores.get('has_type_hints', 0):.0f}")
        
        except Exception as e:
            print(f"\n⚠️  Error evaluating {row['experiment_id']}: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            continue
    
    # 转换为数据框
    results_df = pd.DataFrame(results)
    
    return results_df


def generate_summary_statistics(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    生成汇总统计（多维度）
    
    Args:
        results_df: 评估结果数据框
    
    Returns:
        pd.DataFrame: 汇总统计数据框
    """
    if len(results_df) == 0:
        return pd.DataFrame()
    
    # 定义要统计的指标
    agg_dict = {
        # 功能维度
        'functional_correctness': ['mean', 'std'],
        'compilation_success': ['mean', 'std'],
        'test_pass_rate': ['mean', 'std'],
        'functional_dimension': ['mean', 'std'],
        
        # 效率维度
        'time_complexity_score': ['mean', 'std'],
        'space_complexity_score': ['mean', 'std'],
        'efficiency_dimension': ['mean', 'std'],
        
        # 质量维度
        'code_simplicity': ['mean', 'std'],
        'code_length': ['mean', 'std', 'min', 'max'],
        'cyclomatic_complexity': ['mean', 'std', 'min', 'max'],
        'nesting_depth': ['mean', 'std', 'max'],
        'quality_dimension': ['mean', 'std'],
        
        # 可读性维度
        'readability_score': ['mean', 'std'],
        'has_docstring': ['mean'],
        'has_type_hints': ['mean'],
        'readability_dimension': ['mean', 'std'],
    }
    
    # 只保留存在的列
    agg_dict = {k: v for k, v in agg_dict.items() if k in results_df.columns}
    
    # 按模型分组统计
    summary = results_df.groupby('model').agg(agg_dict).round(4)
    
    # 展平多级列名
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    
    return summary


def print_summary_report(summary_df: pd.DataFrame, results_df: pd.DataFrame):
    """
    打印汇总报告（多维度）
    
    Args:
        summary_df: 汇总统计数据框
        results_df: 原始结果数据框
    """
    if len(summary_df) == 0:
        return
    
    print("\n" + "="*80)
    print("📊 CODE GENERATION QUALITY SUMMARY (Multi-Dimensional)")
    print("="*80)
    
    # 1. 功能维度排名
    if 'functional_dimension_mean' in summary_df.columns:
        print("\n🏆 Top Models by Functional Correctness:")
        print("-"*80)
        functional_sorted = summary_df.sort_values('functional_dimension_mean', ascending=False).head(5)
        for idx, row in functional_sorted.iterrows():
            model = row['model']
            score = row['functional_dimension_mean']
            compilation = row.get('compilation_success_mean', 0)
            test_rate = row.get('test_pass_rate_mean', 0)
            print(f"{idx+1}. {model:30s} Score: {score:.2f} (Compile: {compilation:.2f}, Test: {test_rate:.2f})")
    
    # 2. 效率维度排名
    if 'efficiency_dimension_mean' in summary_df.columns:
        print("\n⚡ Top Models by Efficiency:")
        print("-"*80)
        efficiency_sorted = summary_df.sort_values('efficiency_dimension_mean', ascending=False).head(5)
        for idx, row in efficiency_sorted.iterrows():
            model = row['model']
            score = row['efficiency_dimension_mean']
            time_score = row.get('time_complexity_score_mean', 0)
            space_score = row.get('space_complexity_score_mean', 0)
            print(f"{idx+1}. {model:30s} Score: {score:.2f} (Time: {time_score:.2f}, Space: {space_score:.2f})")
    
    # 3. 质量维度排名
    if 'quality_dimension_mean' in summary_df.columns:
        print("\n✨ Top Models by Code Quality:")
        print("-"*80)
        quality_sorted = summary_df.sort_values('quality_dimension_mean', ascending=False).head(5)
        for idx, row in quality_sorted.iterrows():
            model = row['model']
            score = row['quality_dimension_mean']
            simplicity = row.get('code_simplicity_mean', 0)
            length = row.get('code_length_mean', 0)
            complexity = row.get('cyclomatic_complexity_mean', 0)
            print(f"{idx+1}. {model:30s} Score: {score:.2f} (Len: {length:.1f}, Cmplx: {complexity:.1f})")
    
    # 4. 可读性维度排名
    if 'readability_dimension_mean' in summary_df.columns:
        print("\n📖 Top Models by Readability:")
        print("-"*80)
        readability_sorted = summary_df.sort_values('readability_dimension_mean', ascending=False).head(5)
        for idx, row in readability_sorted.iterrows():
            model = row['model']
            score = row['readability_dimension_mean']
            docstring = row.get('has_docstring_mean', 0)
            type_hints = row.get('has_type_hints_mean', 0)
            print(f"{idx+1}. {model:30s} Score: {score:.2f} (Doc: {docstring:.0%}, Type: {type_hints:.0%})")
    
    # 5. 整体统计
    print("\n" + "="*80)
    print("📈 Overall Statistics:")
    print("-"*80)
    print(f"Total samples evaluated: {len(results_df)}")
    print(f"Models evaluated: {results_df['model'].nunique()}")
    
    if 'functional_correctness' in results_df.columns:
        print(f"Average functional correctness: {results_df['functional_correctness'].mean():.2%}")
    if 'compilation_success' in results_df.columns:
        print(f"Average compilation success: {results_df['compilation_success'].mean():.2%}")
    if 'test_pass_rate' in results_df.columns:
        test_pass_mean = results_df['test_pass_rate'].mean()
        if pd.notna(test_pass_mean):
            print(f"Average test pass rate: {test_pass_mean:.2%}")
    if 'code_length' in results_df.columns:
        print(f"Average code length: {results_df['code_length'].mean():.1f} lines")
    if 'cyclomatic_complexity' in results_df.columns:
        print(f"Average complexity: {results_df['cyclomatic_complexity'].mean():.1f}")


def main():
    """主函数"""
    args = parse_args()
    
    print("="*80)
    print("🚀 CODE GENERATION QUALITY EVALUATION v2.0")
    print("   Multi-Dimensional Independent Scoring (Plan B)")
    print("="*80)
    print(f"Input:  {args.input}")
    print(f"Output: {args.output_dir}")
    print(f"Verbose: {args.verbose}")
    print(f"Code Execution: {args.enable_execution}")
    print("="*80)
    
    # 加载数据
    df = load_data(args.input)
    
    # 评估代码质量
    results_df = evaluate_code_samples(df, args.enable_execution, args.verbose)
    
    if len(results_df) == 0:
        print("\n❌ No results to save")
        return
    
    # 生成汇总统计
    summary_df = generate_summary_statistics(results_df)
    
    # 保存结果
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    detailed_file = output_dir / 'quality_scores_code_v2.csv'
    summary_file = output_dir / 'quality_summary_code_v2.csv'
    
    results_df.to_csv(detailed_file, index=False, encoding='utf-8-sig')
    summary_df.to_csv(summary_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Detailed results saved: {detailed_file}")
    print(f"✅ Summary statistics saved: {summary_file}")
    
    # 打印汇总报告
    print_summary_report(summary_df, results_df)
    
    print("\n" + "="*80)
    print("✅ CODE QUALITY EVALUATION COMPLETED!")
    print("="*80)


if __name__ == '__main__':
    main()
