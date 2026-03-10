"""
测试 pareto_mixed_task.py 中的绘图函数
"""

import sys
from pathlib import Path
import os

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'analysis' / 'qe_research' / 'scripts'))

os.chdir(project_root)

import pandas as pd
import numpy as np

# 现在导入应该可以工作了
from pareto_core.pareto_mixed_task import plot_task_weights, plot_quality_heatmap, WEIGHT_CONFIGS

def test_plot_task_weights():
    """测试任务权重图"""
    print("测试 1: 绘制任务权重图")
    print("-" * 60)
    
    output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'mixed_task_analysis' / 'test'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for config_name in WEIGHT_CONFIGS.keys():
        try:
            output_path = output_dir / f'test_task_weights_{config_name}.png'
            plot_task_weights(WEIGHT_CONFIGS[config_name]['weights'], config_name, output_path)
            print(f"✓ {config_name} 权重图生成成功")
        except Exception as e:
            print(f"✗ {config_name} 权重图生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    print()

def test_plot_quality_heatmap():
    """测试质量热力图"""
    print("测试 2: 绘制质量热力图")
    print("-" * 60)
    
    # 创建模拟数据
    models = ['qwen3_8b', 'deepseek-r1_8b', 'gemma3_4b', 'qwen3_4b']
    tasks = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']
    
    data = {
        'model': models,
        'aggregated_quality': np.random.rand(len(models))
    }
    
    for task in tasks:
        data[task] = np.random.rand(len(models))
    
    task_scores_df = pd.DataFrame(data)
    
    output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'mixed_task_analysis' / 'test'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for config_name in WEIGHT_CONFIGS.keys():
        try:
            output_path = output_dir / f'test_quality_heatmap_{config_name}.png'
            plot_quality_heatmap(task_scores_df, config_name, output_path)
            print(f"✓ {config_name} 热力图生成成功")
        except Exception as e:
            print(f"✗ {config_name} 热力图生成失败: {e}")
            import traceback
            traceback.print_exc()
    
    print()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("测试 pareto_mixed_task.py 绘图函数")
    print("="*60 + "\n")
    
    test_plot_task_weights()
    test_plot_quality_heatmap()
    
    print("="*60)
    print("测试完成！")
    print("="*60)
    print(f"测试图表保存在: analysis/qe_research/results/mixed_task_analysis/test/")
