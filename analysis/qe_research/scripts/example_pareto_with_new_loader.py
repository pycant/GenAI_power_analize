"""
使用新的 load_process_quality_data() 函数的帕累托分析示例

演示如何用新接口简化帕累托分析流程
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
matplotlib.rcParams['axes.unicode_minus'] = False

from pareto_core import (
    load_process_quality_data,
    load_energy_speed_data,
    MODEL_MAPPING,
    DATA_PATHS,
    identify_pareto_frontier_2d,
    plot_pareto_2d
)


def example_1_basic_pareto():
    """示例1: 基础帕累托分析（使用熵权法）"""
    print("\n" + "="*80)
    print("示例1: 基础帕累托分析 - Code任务（熵权法）")
    print("="*80)
    
    # 1. 加载质量数据（熵权法）
    print("\n步骤1: 加载质量数据")
    quality_df = load_process_quality_data(
        task_name='code',
        method='entropy',
        verbose=True
    )
    
    # 2. 加载能耗和速度数据
    print("\n步骤2: 加载能耗和速度数据")
    energy_dict, speed_dict = load_energy_speed_data(
        'code',
        DATA_PATHS['energy'],
        DATA_PATHS['speed']
    )
    
    # 3. 合并数据
    print("\n步骤3: 合并数据")
    merged_data = []
    for _, row in quality_df.iterrows():
        model_short = row['model']
        model_full = MODEL_MAPPING.get(model_short)
        
        if model_full and model_full in energy_dict and model_full in speed_dict:
            merged_data.append({
                'model': model_short,
                'quality': row['quality'],
                'energy': energy_dict[model_full],
                'speed': speed_dict[model_full]
            })
    
    df = pd.DataFrame(merged_data)
    print(f"✓ 合并完成: {len(df)} 个模型")
    
    # 4. 识别帕累托前沿
    print("\n步骤4: 识别帕累托前沿")
    pareto_qe = identify_pareto_frontier_2d(
        df, 'quality', 'energy',
        x_minimize=False, y_minimize=True
    )
    
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    print(f"  前沿模型: {df[pareto_qe]['model'].tolist()}")
    
    # 5. 可视化
    print("\n步骤5: 生成可视化")
    output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'example_new_loader'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plot_pareto_2d(
        df, pareto_qe, 'quality', 'energy',
        'Code任务：质量-能耗帕累托前沿（熵权法）',
        output_dir / 'pareto_qe_entropy.png',
        '质量得分（熵权法）', '每token能耗 (J/token)',
        x_minimize=False, y_minimize=True
    )
    
    print(f"✓ 图表已保存: {output_dir / 'pareto_qe_entropy.png'}")


def example_2_single_metric():
    """示例2: 使用单一指标的帕累托分析"""
    print("\n" + "="*80)
    print("示例2: 单一指标帕累托分析 - Code任务（编译成功率）")
    print("="*80)
    
    # 使用编译成功率作为质量指标
    quality_df = load_process_quality_data(
        task_name='code',
        method='single',
        quality_column='compilation_rate',
        verbose=True
    )
    
    # 加载能耗和速度
    energy_dict, speed_dict = load_energy_speed_data(
        'code',
        DATA_PATHS['energy'],
        DATA_PATHS['speed']
    )
    
    # 合并数据
    merged_data = []
    for _, row in quality_df.iterrows():
        model_short = row['model']
        model_full = MODEL_MAPPING.get(model_short)
        
        if model_full and model_full in energy_dict and model_full in speed_dict:
            merged_data.append({
                'model': model_short,
                'quality': row['quality'],
                'energy': energy_dict[model_full],
                'speed': speed_dict[model_full]
            })
    
    df = pd.DataFrame(merged_data)
    
    # 识别帕累托前沿
    pareto_qe = identify_pareto_frontier_2d(
        df, 'quality', 'energy',
        x_minimize=False, y_minimize=True
    )
    
    print(f"\n✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    print(f"  前沿模型: {df[pareto_qe]['model'].tolist()}")
    
    # 可视化
    output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'example_new_loader'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plot_pareto_2d(
        df, pareto_qe, 'quality', 'energy',
        'Code任务：质量-能耗帕累托前沿（编译成功率）',
        output_dir / 'pareto_qe_single.png',
        '编译成功率', '每token能耗 (J/token)',
        x_minimize=False, y_minimize=True
    )
    
    print(f"✓ 图表已保存: {output_dir / 'pareto_qe_single.png'}")


def example_3_method_comparison():
    """示例3: 对比不同方法的帕累托前沿"""
    print("\n" + "="*80)
    print("示例3: 对比不同质量处理方法的帕累托前沿")
    print("="*80)
    
    methods = {
        'entropy': '熵权法',
        'single': '编译成功率',
        'mean': '简单平均'
    }
    
    all_results = {}
    
    for method, method_name in methods.items():
        print(f"\n处理方法: {method_name}")
        
        # 加载质量数据
        if method == 'single':
            quality_df = load_process_quality_data(
                task_name='code',
                method=method,
                quality_column='compilation_rate',
                verbose=False
            )
        else:
            quality_df = load_process_quality_data(
                task_name='code',
                method=method,
                verbose=False
            )
        
        # 加载能耗和速度
        energy_dict, speed_dict = load_energy_speed_data(
            'code',
            DATA_PATHS['energy'],
            DATA_PATHS['speed']
        )
        
        # 合并数据
        merged_data = []
        for _, row in quality_df.iterrows():
            model_short = row['model']
            model_full = MODEL_MAPPING.get(model_short)
            
            if model_full and model_full in energy_dict and model_full in speed_dict:
                merged_data.append({
                    'model': model_short,
                    'quality': row['quality'],
                    'energy': energy_dict[model_full]
                })
        
        df = pd.DataFrame(merged_data)
        
        # 识别帕累托前沿
        pareto_qe = identify_pareto_frontier_2d(
            df, 'quality', 'energy',
            x_minimize=False, y_minimize=True
        )
        
        all_results[method_name] = {
            'df': df,
            'pareto': pareto_qe,
            'pareto_models': df[pareto_qe]['model'].tolist()
        }
        
        print(f"  ✓ 前沿模型数: {pareto_qe.sum()}")
        print(f"    模型: {all_results[method_name]['pareto_models']}")
    
    # 对比可视化
    print("\n生成对比图表...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, (method_name, result) in enumerate(all_results.items()):
        ax = axes[idx]
        df = result['df']
        pareto = result['pareto']
        
        # 非帕累托点
        non_pareto = df[~pareto]
        ax.scatter(non_pareto['quality'], non_pareto['energy'],
                  c='lightgray', s=100, alpha=0.6, label='非帕累托点')
        
        # 帕累托点
        pareto_df = df[pareto]
        ax.scatter(pareto_df['quality'], pareto_df['energy'],
                  c='red', s=200, marker='*', label='帕累托前沿', zorder=5)
        
        # 标注
        for _, row in df.iterrows():
            ax.annotate(row['model'],
                       (row['quality'], row['energy']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8, alpha=0.7)
        
        ax.set_xlabel('质量得分', fontsize=11)
        ax.set_ylabel('每token能耗 (J/token)', fontsize=11)
        ax.set_title(f'{method_name}', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'example_new_loader'
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_dir / 'method_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 对比图表已保存: {output_dir / 'method_comparison.png'}")
    
    # 打印对比总结
    print("\n" + "="*80)
    print("方法对比总结")
    print("="*80)
    
    for method_name, result in all_results.items():
        print(f"\n{method_name}:")
        print(f"  前沿模型数: {len(result['pareto_models'])}")
        print(f"  前沿模型: {', '.join(result['pareto_models'])}")


def example_4_multi_task():
    """示例4: 多任务帕累托分析"""
    print("\n" + "="*80)
    print("示例4: 多任务帕累托分析（熵权法）")
    print("="*80)
    
    tasks = ['code', 'creative', 'qa']
    all_pareto_models = {}
    
    for task in tasks:
        print(f"\n处理任务: {task.upper()}")
        
        # 加载质量数据
        quality_df = load_process_quality_data(
            task_name=task,
            method='entropy',
            verbose=False
        )
        
        # 加载能耗和速度
        energy_dict, speed_dict = load_energy_speed_data(
            task,
            DATA_PATHS['energy'],
            DATA_PATHS['speed']
        )
        
        # 合并数据
        merged_data = []
        for _, row in quality_df.iterrows():
            model_short = row['model']
            model_full = MODEL_MAPPING.get(model_short)
            
            if model_full and model_full in energy_dict and model_full in speed_dict:
                merged_data.append({
                    'model': model_short,
                    'quality': row['quality'],
                    'energy': energy_dict[model_full]
                })
        
        df = pd.DataFrame(merged_data)
        
        # 识别帕累托前沿
        pareto_qe = identify_pareto_frontier_2d(
            df, 'quality', 'energy',
            x_minimize=False, y_minimize=True
        )
        
        pareto_models = df[pareto_qe]['model'].tolist()
        all_pareto_models[task] = pareto_models
        
        print(f"  ✓ 前沿模型数: {len(pareto_models)}")
        print(f"    模型: {', '.join(pareto_models)}")
    
    # 找出在所有任务中都在前沿的模型
    print("\n" + "="*80)
    print("跨任务分析")
    print("="*80)
    
    all_models = set()
    for models in all_pareto_models.values():
        all_models.update(models)
    
    print(f"\n所有参与的模型: {len(all_models)} 个")
    
    # 统计每个模型在多少个任务中位于前沿
    model_counts = {}
    for model in all_models:
        count = sum(1 for models in all_pareto_models.values() if model in models)
        model_counts[model] = count
    
    print("\n模型前沿出现次数:")
    for model, count in sorted(model_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {model:<30} {count}/{len(tasks)} 个任务")
    
    # 找出最稳定的模型
    max_count = max(model_counts.values())
    stable_models = [m for m, c in model_counts.items() if c == max_count]
    
    print(f"\n最稳定的模型（在 {max_count}/{len(tasks)} 个任务中位于前沿）:")
    for model in stable_models:
        print(f"  - {model}")


def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("使用新 load_process_quality_data() 的帕累托分析示例")
    print("="*80)
    
    examples = [
        ("基础帕累托分析（熵权法）", example_1_basic_pareto),
        ("单一指标帕累托分析", example_2_single_metric),
        ("方法对比", example_3_method_comparison),
        ("多任务分析", example_4_multi_task),
    ]
    
    for name, func in examples:
        try:
            func()
        except Exception as e:
            print(f"\n✗ 示例 '{name}' 执行失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("所有示例执行完成！")
    print("="*80)
    print("\n生成的文件:")
    print("  - analysis/qe_research/results/example_new_loader/pareto_qe_entropy.png")
    print("  - analysis/qe_research/results/example_new_loader/pareto_qe_single.png")
    print("  - analysis/qe_research/results/example_new_loader/method_comparison.png")


if __name__ == '__main__':
    main()
