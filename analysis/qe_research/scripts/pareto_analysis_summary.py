"""
摘要任务帕累托前沿分析（重构版 - 使用新数据加载器）

使用 pareto_core 共享模块，消除代码重复

基于以下数据：
1. 质量指标：使用 load_process_quality_data() 统一接口加载
   - 默认方法：熵权法（entropy）
   - 可选方法：单一指标（single）、PCA降维（pca）、简单平均（mean）、自定义权重（custom）
2. 能耗指标：每token能耗
3. 速度指标：token生成速度

配置说明：
- TASK_NAME: 任务名称（summary）
- QUALITY_METHOD: 质量处理方法
  * 'entropy' - 熵权法（默认，推荐）
  * 'single' - 使用单一指标（需配置 quality_column）
  * 'pca' - PCA降维
  * 'mean' - 简单平均
  * 'custom' - 自定义权重（需配置 custom_weights）
- QUALITY_METRIC_NAME: 质量指标显示名称

使用示例：
1. 使用熵权法（默认）：
   QUALITY_METHOD = 'entropy'

2. 使用单一指标（如ROUGE-L）：
   QUALITY_METHOD = 'single'
   在 load_process_quality_data() 中添加: quality_column='rouge_l_score'

3. 使用PCA降维：
   QUALITY_METHOD = 'pca'
   在 load_process_quality_data() 中添加: n_components=1
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d, identify_pareto_frontier_3d,
    calculate_hypervolume, calculate_spacing, find_knee_point,
    plot_pareto_2d, load_energy_speed_data, load_process_quality_data,
    perturbation_analysis, cross_validation_pareto,
    generate_pareto_report, print_analysis_summary,merge_quality_metrics
)

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 任务配置
TASK_NAME = 'summary'
QUALITY_METHOD = 'entropy'  # 可选: 'entropy', 'single', 'pca', 'mean', 'custom'
QUALITY_METRIC_NAME = 'ROUGE-L得分'

OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / TASK_NAME
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_and_prepare_data():
    """加载并准备数据"""
    print("\n" + "="*80)
    print(f"加载数据：{TASK_NAME.upper()}任务")
    print("="*80)
    
    # 1. 使用新的统一接口加载质量数据
    print(f"\n步骤1: 加载质量数据（方法: {QUALITY_METHOD}）")
    quality_df = load_process_quality_data(
        task_name=TASK_NAME,
        method=QUALITY_METHOD,
        normalize_method='zscore',
        use_raw=True,
        verbose=True,
        output_dir=OUTPUT_DIR
    )
    
    # 2. 加载能耗和速度数据
    print(f"\n步骤2: 加载能耗和速度数据,合并质量、能耗、速度数据")
    energy_dict, speed_dict = load_energy_speed_data(
        TASK_NAME, 
        DATA_PATHS['energy'], 
        DATA_PATHS['speed']
    )
    print(f"✓ 能耗数据: {len(energy_dict)} 个模型")
    print(f"✓ 速度数据: {len(speed_dict)} 个模型")
    
    # 3. 合并数据
    print(f"\n步骤3: 合并质量、能耗、速度数据")
    merged_data = []
    merged_data = merge_quality_metrics(quality_df, energy_dict, speed_dict, MODEL_MAPPING)
    
    df = pd.DataFrame(merged_data)
    print(f"✓ 合并后数据: {len(df)} 个模型")
    print(f"  列: {', '.join(df.columns)}")
    
    # 4. 保存合并数据
    merged_file = OUTPUT_DIR / 'merged_data.csv'
    df.to_csv(merged_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 合并数据已保存: {merged_file}")
    
    return df



def main():
    """主函数"""
    print("\n" + "="*80)
    print(f"{TASK_NAME.upper()}任务帕累托前沿分析（重构版 - 使用新数据加载器）")
    print("="*80)
    print(f"质量处理方法: {QUALITY_METHOD}")
    print(f"质量指标名称: {QUALITY_METRIC_NAME}")
    print("="*80)
    
    # 1. 加载数据
    df = load_and_prepare_data()
    
    # 2. 识别帕累托前沿
    print("\n" + "="*80)
    print("识别帕累托前沿")
    print("="*80)
    
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', x_minimize=False, y_minimize=True)
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    
    pareto_qs = identify_pareto_frontier_2d(df, 'quality', 'speed', x_minimize=False, y_minimize=False)
    print(f"✓ 质量-速度前沿: {pareto_qs.sum()} 个模型")
    
    pareto_3d = identify_pareto_frontier_3d(df)
    print(f"✓ 三维前沿: {pareto_3d.sum()} 个模型")
    
    # 3. 生成可视化图表
    print("\n" + "="*80)
    print("生成可视化图表")
    print("="*80)
    
    plot_pareto_2d(df, pareto_qe, 'quality', 'energy',
                   f'{TASK_NAME.capitalize()}任务：质量-能耗帕累托前沿',
                   OUTPUT_DIR / 'pareto_quality_energy.png',
                   QUALITY_METRIC_NAME, '每token能耗 (J/token)',
                   x_minimize=False, y_minimize=True)
    
    plot_pareto_2d(df, pareto_qs, 'quality', 'speed',
                   f'{TASK_NAME.capitalize()}任务：质量-速度帕累托前沿',
                   OUTPUT_DIR / 'pareto_quality_speed.png',
                   QUALITY_METRIC_NAME, 'Token生成速度 (tokens/s)',
                   x_minimize=False, y_minimize=False)
    
    # 4. 计算定量指标
    print("\n" + "="*80)
    print("计算定量指标")
    print("="*80)
    
    hv_qe = calculate_hypervolume(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 超体积（质量-能耗）: {hv_qe:.4f}")
    
    spacing_qe = calculate_spacing(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 间距指标（质量-能耗）: {spacing_qe:.4f}")
    
    knee = find_knee_point(df, pareto_qe, 'quality', 'energy')
    print(f"✓ 拐点模型: {knee}")
    
    # 5. 稳健性分析
    print("\n" + "="*80)
    print("稳健性分析")
    print("="*80)
    
    print("\n扰动分析（质量-能耗前沿）...")
    robustness_qe = perturbation_analysis(df, 'quality', 'energy',
                                          x_minimize=False, y_minimize=True,
                                          noise_level=0.05, n_iterations=100)
    print(f"✓ 前沿一致性: {robustness_qe['mean_consistency']:.2%}")
    
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
        'task_name': TASK_NAME,
        'task_name_cn': '摘要',
        'quality_metric': QUALITY_METRIC_NAME,
        'quality_method': QUALITY_METHOD,
        'report_filename': 'SUMMARY_PARETO_ANALYSIS_REPORT.md'
    }
    
    report_path = generate_pareto_report(df, results, OUTPUT_DIR, task_config)
    print(f"✓ 报告已保存: {report_path.name}")
    
    # 打印分析摘要
    print_analysis_summary(df, results, f"{TASK_NAME.capitalize()}任务")
    
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print(f"质量处理方法: {QUALITY_METHOD}")
    print(f"质量指标: {QUALITY_METRIC_NAME}")


if __name__ == '__main__':
    main()
