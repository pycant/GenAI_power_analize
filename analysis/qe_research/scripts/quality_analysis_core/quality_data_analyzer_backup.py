"""
代码生成任务帕累托前沿分析（重构版）

使用 pareto_core 共享模块，消除代码重复

基于以下数据：
1. 质量指标：编译成功率（compilation_rate）
2. 能耗指标：每token能耗（energy_per_token）
3. 速度指标：平均token速度（avg_token_speed）
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 导入共享模块
from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d, identify_pareto_frontier_3d,
    calculate_hypervolume, calculate_spacing, find_knee_point,
    plot_pareto_2d, load_energy_speed_data, merge_quality_metrics,
    perturbation_analysis, cross_validation_pareto,
    generate_pareto_report, print_analysis_summary
)

# 任务特定配置
TASK_NAME = 'code'
QUALITY_FILE = PROJECT_ROOT / 'data' / 'analize' / 'results' / 'code_quality' / 'quality_summary_code.csv'
QUALITY_COLUMN = 'compilation_rate_mean'
OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / TASK_NAME
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_and_prepare_data():
    """加载并准备数据"""
    print("\n" + "="*80)
    print("加载数据：代码生成任务")
    print("="*80)
    
    # 1. 加载质量数据
    quality_df = pd.read_csv(QUALITY_FILE)
    print(f"✓ 质量数据: {len(quality_df)} 个模型")
    
    # 2. 加载能耗和速度数据
    energy_dict, speed_dict = load_energy_speed_data(TASK_NAME, DATA_PATHS['energy'], DATA_PATHS['speed'])
    
    # 3. 合并数据
    df = merge_quality_metrics(quality_df, energy_dict, speed_dict, MODEL_MAPPING, QUALITY_COLUMN)
    
    print(f"\n合并后数据: {len(df)} 个模型")
    print(f"列: {', '.join(df.columns)}")
    
    # 保存合并数据
    merged_file = OUTPUT_DIR / 'merged_data.csv'
    df.to_csv(merged_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 合并数据已保存: {merged_file}")
    
    return df



def main():
    """主函数"""
    print("\n" + "="*80)
    print("代码生成任务帕累托前沿分析")
    print("="*80)
    
    # 1. 加载数据
    df = load_and_prepare_data()
    
    # 2. 识别帕累托前沿
    print("\n" + "="*80)
    print("识别帕累托前沿")
    print("="*80)
    
    # 2.1 质量-能耗前沿（质量最大化，能耗最小化）
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', 
                                            x_minimize=False, y_minimize=True)
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    
    # 2.2 质量-速度前沿（质量最大化，速度最大化）
    pareto_qs = identify_pareto_frontier_2d(df, 'quality', 'speed',
                                            x_minimize=False, y_minimize=False)
    print(f"✓ 质量-速度前沿: {pareto_qs.sum()} 个模型")
    
    # 2.3 三维前沿
    pareto_3d = identify_pareto_frontier_3d(df)
    print(f"✓ 三维前沿: {pareto_3d.sum()} 个模型")
    
    # 3. 绘制图表
    print("\n" + "="*80)
    print("生成可视化图表")
    print("="*80)
    
    plot_pareto_2d(df, pareto_qe, 'quality', 'energy',
                   '代码生成任务：质量-能耗帕累托前沿',
                   'pareto_quality_energy.png',
                   '编译成功率', '每token能耗 (J/token)',
                   x_minimize=False, y_minimize=True)
    
    plot_pareto_2d(df, pareto_qs, 'quality', 'speed',
                   '代码生成任务：质量-速度帕累托前沿',
                   'pareto_quality_speed.png',
                   '编译成功率', 'Token生成速度 (tokens/s)',
                   x_minimize=False, y_minimize=False)
    
    # 4. 计算定量指标
    print("\n" + "="*80)
    print("计算定量指标")
    print("="*80)
    
    hv_qe = calculate_hypervolume(df, pareto_qe)
    print(f"✓ 超体积（质量-能耗）: {hv_qe:.4f}")
    
    spacing_qe = calculate_spacing(df, pareto_qe)
    print(f"✓ 间距指标（质量-能耗）: {spacing_qe:.4f}")
    
    knee = find_knee_point(df, pareto_qe)
    print(f"✓ 拐点模型: {knee}")
    
    # 5. 稳健性分析
    print("\n" + "="*80)
    print("稳健性分析")
    print("="*80)
    
    # 5.1 扰动分析（质量-能耗）
    print("\n扰动分析（质量-能耗前沿）...")
    robustness_qe = perturbation_analysis(df, 'quality', 'energy',
                                          x_minimize=False, y_minimize=True,
                                          noise_level=0.05, n_iterations=100)
    print(f"✓ 前沿一致性: {robustness_qe['mean_consistency']:.2%}")
    print(f"  最稳定模型: {max(robustness_qe['stability_scores'].items(), key=lambda x: x[1])[0]}")
    
    # 5.2 交叉验证（质量-能耗）
    print("\n交叉验证分析（质量-能耗前沿）...")
    cross_val_qe = cross_validation_pareto(df, 'quality', 'energy',
                                           x_minimize=False, y_minimize=True,
                                           n_folds=5)
    print(f"✓ 交叉验证一致性: {cross_val_qe['mean_consistency']:.2%}")
    
    results = {
        'pareto_qe': pareto_qe,
        'pareto_qs': pareto_qs,
        'pareto_3d': pareto_3d,
        'hypervolume_qe': hv_qe,
        'spacing_qe': spacing_qe,
        'knee_point': knee,
        'robustness_qe': robustness_qe,
        'cross_val_qe': cross_val_qe
    }
    
    # 6. 生成报告
    task_config = {
        'task_name': 'code',
        'task_name_cn': '代码生成',
        'quality_metric': '编译成功率',
        'report_filename': 'CODE_PARETO_ANALYSIS_REPORT.md'
    }
    
    report_path = generate_pareto_report(df, results, OUTPUT_DIR, task_config)
    print(f"✓ 报告已保存: {report_path.name}")
    
    # 打印分析摘要
    print_analysis_summary(df, results, "代码生成任务")
    
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)
    print(f"\n输出目录: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
