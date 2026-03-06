"""
一键运行任务帕累托前沿分析

使用方法：
    python run_task_pareto.py --task qa
    python run_task_pareto.py --task summary
    python run_task_pareto.py --task creative
    python run_task_pareto.py --task code
"""

import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import subprocess
import sys


def prepare_data_for_task(task_name):
    """
    为指定任务准备数据
    
    Args:
        task_name: 任务名称（qa, summary, creative, code, reasoning）
    
    Returns:
        merged_data_path: 合并后的数据文件路径
    """
    print(f"\n{'='*80}")
    print(f"准备{task_name}任务数据")
    print(f"{'='*80}")
    
    # 数据路径配置
    base_dir = Path(__file__).parent.parent
    
    # 根据任务类型加载不同的质量评分
    quality_file_map = {
        'reasoning': base_dir / 'data' / 'analize' / 'results' / 'reasoning_quality' / 'reasoning_quality_summary.csv',
        'qa': base_dir / 'data' / 'analize' / 'results' / 'qa_quality' / 'qa_quality_summary.csv',
        'summary': base_dir / 'data' / 'analize' / 'results' / 'summary_quality' / 'summary_quality_summary.csv',
        'creative': base_dir / 'data' / 'analize' / 'results' / 'creative_quality' / 'creative_quality_summary.csv',
        'code': base_dir / 'data' / 'analize' / 'results' / 'code_quality' / 'code_quality_summary.csv',
    }
    
    # 能耗和速度数据（通常是共享的）
    # TODO: 根据实际数据结构调整路径
    energy_speed_file = base_dir / 'data' / 'experiments_1' / 'summary' / 'results.csv'
    
    quality_file = quality_file_map.get(task_name)
    
    if not quality_file or not quality_file.exists():
        print(f"⚠ 警告：未找到{task_name}任务的质量评分文件")
        print(f"  预期路径：{quality_file}")
        print(f"  请先运行质量评估脚本")
        return None
    
    # 加载质量数据
    print(f"✓ 加载质量数据：{quality_file.name}")
    quality_df = pd.read_csv(quality_file)
    
    # 加载能耗和速度数据
    if energy_speed_file.exists():
        print(f"✓ 加载能耗/速度数据：{energy_speed_file.name}")
        perf_df = pd.read_csv(energy_speed_file)
        
        # 筛选当前任务的数据
        if 'task' in perf_df.columns:
            perf_df = perf_df[perf_df['task'] == task_name].copy()
        
        # 提取需要的列
        if 'gpu_energy_j' in perf_df.columns:
            perf_df = perf_df.rename(columns={'gpu_energy_j': 'energy'})
        if 'toks_per_s' in perf_df.columns:
            perf_df = perf_df.rename(columns={'toks_per_s': 'speed'})
        
        # 合并数据
        merged_df = quality_df.merge(
            perf_df[['model', 'energy', 'speed']], 
            on='model', 
            how='inner'
        )
    else:
        print(f"⚠ 警告：未找到能耗/速度数据文件")
        merged_df = quality_df
    
    # 保存合并数据
    output_dir = base_dir / 'results' / 'pareto_analysis' / task_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    merged_data_path = output_dir / 'merged_data.csv'
    merged_df.to_csv(merged_data_path, index=False)
    
    print(f"✓ 数据已保存：{merged_data_path}")
    print(f"  模型数量：{len(merged_df)}")
    print(f"  列：{', '.join(merged_df.columns)}")
    
    return merged_data_path


def run_analysis(task_name):
    """运行完整的帕累托前沿分析"""
    print(f"\n{'='*80}")
    print(f"运行{task_name}任务帕累托前沿分析")
    print(f"{'='*80}")
    
    # 准备数据
    data_path = prepare_data_for_task(task_name)
    
    if data_path is None:
        print("\n❌ 数据准备失败，无法继续分析")
        return False
    
    # 运行定量指标计算
    print(f"\n{'='*80}")
    print("步骤1：定量指标计算")
    print(f"{'='*80}")
    
    # TODO: 调用pareto_metrics_calculator.py
    # 需要修改该脚本以接受任务参数
    
    # 运行稳健性验证
    print(f"\n{'='*80}")
    print("步骤2：稳健性验证")
    print(f"{'='*80}")
    
    # TODO: 调用pareto_robustness_analyzer.py
    # 需要修改该脚本以接受任务参数
    
    print(f"\n{'='*80}")
    print(f"✓ {task_name}任务分析完成")
    print(f"{'='*80}")
    
    output_dir = Path(__file__).parent.parent / 'results' / 'pareto_analysis' / task_name
    print(f"\n查看结果：{output_dir}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='一键运行任务帕累托前沿分析')
    parser.add_argument('--task', required=True, 
                       choices=['reasoning', 'qa', 'summary', 'creative', 'code'],
                       help='任务名称')
    
    args = parser.parse_args()
    
    success = run_analysis(args.task)
    
    if success:
        print("\n✓ 分析成功完成")
        sys.exit(0)
    else:
        print("\n❌ 分析失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
