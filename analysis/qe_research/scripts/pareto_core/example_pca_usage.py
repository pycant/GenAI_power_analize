"""
PCA分析功能使用示例

演示如何使用PCA方法进行质量数据分析
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

from analysis.qe_research.scripts.pareto_core.shared_functions import (
    load_process_quality_data,
    load_energy_speed_data,
    merge_quality_metrics,
    identify_pareto_frontier_2d,
    plot_pareto_2d
)


def example_pca_quality_analysis():
    """示例1: 使用PCA进行质量分析"""
    
    print("\n" + "="*80)
    print("示例1: PCA质量分析")
    print("="*80)
    
    # 使用PCA方法加载质量数据
    # 会自动生成图表和报告到指定目录
    quality_df = load_process_quality_data(
        task_name='code',
        method='pca',
        normalize_method='minmax',
        use_raw=True,
        verbose=True,
        output_dir='analysis/qe_research/results/example_pca/code'
    )
    
    print("\n✓ 质量数据加载完成")
    print(f"  模型数量: {len(quality_df)}")
    print(f"  质量得分范围: [{quality_df['quality'].min():.4f}, {quality_df['quality'].max():.4f}]")
    
    # 显示前5名模型
    print("\n前5名模型:")
    top5 = quality_df.nlargest(5, 'quality')
    for idx, row in top5.iterrows():
        print(f"  {idx+1}. {row['model']}: {row['quality']:.4f}")
    
    return quality_df


def example_pca_pareto_analysis():
    """示例2: 结合PCA和Pareto分析"""
    
    print("\n" + "="*80)
    print("示例2: PCA + Pareto分析")
    print("="*80)
    
    # 1. 使用PCA加载质量数据
    quality_df = load_process_quality_data(
        task_name='code',
        method='pca',
        output_dir='analysis/qe_research/results/example_pca/code',
        verbose=False  # 简化输出
    )
    
    print(f"\n✓ 步骤1: 质量数据加载完成 ({len(quality_df)} 个模型)")
    
    # 2. 加载能耗和速度数据（示例路径，需要根据实际情况调整）
    try:
        energy_dict, speed_dict = load_energy_speed_data(
            task_name='code',
            energy_file='analysis/qe_research/results/metric_tables/gpu_energy_per_token.csv',
            speed_file='analysis/qe_research/results/metric_tables/tokens_per_second.csv'
        )
        print(f"✓ 步骤2: 能耗和速度数据加载完成")
        
        # 3. 模型名称映射（示例，需要根据实际情况调整）
        MODEL_MAPPING = {
            'gemma_2b_hf_4bit': 'gemma_2b_hf_4bit',
            'gemma_2b_hf_8bit': 'gemma_2b_hf_8bit',
            'gemma_4b_ol_q4km': 'gemma_4b_ol_q4km',
            # ... 添加更多映射
        }
        
        # 4. 合并数据
        merged_df = merge_quality_metrics(
            quality_df=quality_df,
            energy_dict=energy_dict,
            speed_dict=speed_dict,
            model_mapping=MODEL_MAPPING
        )
        
        print(f"✓ 步骤3: 数据合并完成 ({len(merged_df)} 个模型)")
        
        # 5. 识别Pareto前沿
        pareto_mask = identify_pareto_frontier_2d(
            df=merged_df,
            x_col='energy',
            y_col='quality',
            x_minimize=True,   # 能耗最小化
            y_minimize=False   # 质量最大化
        )
        
        pareto_models = merged_df[pareto_mask]
        print(f"\n✓ 步骤4: Pareto前沿识别完成 ({len(pareto_models)} 个模型)")
        
        # 显示Pareto前沿模型
        print("\nPareto前沿模型:")
        for _, row in pareto_models.sort_values('quality', ascending=False).iterrows():
            print(f"  - {row['model']}: 质量={row['quality']:.4f}, "
                  f"能耗={row['energy']:.3f} J/token, 速度={row['speed']:.2f} tokens/s")
        
        # 6. 绘制Pareto图
        output_dir = Path('analysis/qe_research/results/example_pca/code')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        plot_pareto_2d(
            df=merged_df,
            pareto_mask=pareto_mask,
            x_col='energy',
            y_col='quality',
            title='Quality-Energy Pareto Frontier (PCA Quality)',
            output_path=output_dir / 'pareto_quality_energy_pca.png',
            x_label='Energy (J/token)',
            y_label='Quality Score (PCA)',
            x_minimize=True,
            y_minimize=False
        )
        
        print(f"\n✓ 步骤5: Pareto图已保存")
        
    except FileNotFoundError as e:
        print(f"\n⚠ 警告: 能耗/速度数据文件未找到")
        print(f"  请确保以下文件存在:")
        print(f"  - analysis/qe_research/results/metric_tables/gpu_energy_per_token.csv")
        print(f"  - analysis/qe_research/results/metric_tables/tokens_per_second.csv")
        print(f"\n  可以先运行质量分析查看PCA结果")


def example_compare_methods():
    """示例3: 比较不同质量评估方法"""
    
    print("\n" + "="*80)
    print("示例3: 比较不同质量评估方法")
    print("="*80)
    
    methods = ['entropy', 'pca', 'mean']
    task = 'code'
    
    results = {}
    
    for method in methods:
        print(f"\n使用 {method.upper()} 方法...")
        
        quality_df = load_process_quality_data(
            task_name=task,
            method=method,
            output_dir=f'analysis/qe_research/results/example_pca/{task}_{method}',
            verbose=False
        )
        
        results[method] = quality_df
        print(f"  ✓ 完成: {len(quality_df)} 个模型")
    
    # 比较前3名模型
    print("\n" + "="*80)
    print("各方法前3名模型对比:")
    print("="*80)
    
    for method in methods:
        print(f"\n{method.upper()} 方法:")
        top3 = results[method].nlargest(3, 'quality')
        for idx, row in top3.iterrows():
            print(f"  {idx+1}. {row['model']}: {row['quality']:.4f}")


def main():
    """主函数"""
    
    print("\n" + "="*80)
    print("PCA分析功能使用示例")
    print("="*80)
    
    # 示例1: 基本PCA分析
    example_pca_quality_analysis()
    
    # 示例2: PCA + Pareto分析
    example_pca_pareto_analysis()
    
    # 示例3: 比较不同方法
    example_compare_methods()
    
    print("\n" + "="*80)
    print("所有示例完成")
    print("="*80)
    print("\n查看生成的文件:")
    print("  - 报告: analysis/qe_research/results/example_pca/code/pca_analysis/PCA_ANALYSIS_REPORT.md")
    print("  - 图表: analysis/qe_research/results/example_pca/code/pca_analysis/*.png")


if __name__ == '__main__':
    main()
