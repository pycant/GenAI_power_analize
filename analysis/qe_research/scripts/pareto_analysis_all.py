"""
所有任务帕累托前沿分析（批量执行版 - 使用新数据加载器）

使用 pareto_core 共享模块，消除代码重复

批量执行所有任务的帕累托分析：
- summary (摘要)
- qa (问答)
- math (数学)
- translation (翻译)
- code (代码生成)
- creative (创意写作)

基于以下数据：
1. 质量指标：使用 load_process_quality_data() 统一接口加载
   - 默认方法：熵权法（entropy）
   - 可选方法：单一指标（single）、PCA降维（pca）、简单平均（mean）、自定义权重（custom）
2. 能耗指标：每token能耗
3. 速度指标：token生成速度

配置说明：
- TASK_NAME: 任务名称（在循环中动态设置）
- QUALITY_METHOD: 质量处理方法
  * 'entropy' - 熵权法（默认，推荐）
  * 'single' - 使用单一指标（需配置 quality_column）
  * 'pca' - PCA降维
  * 'mean' - 简单平均
  * 'custom' - 自定义权重（需配置 custom_weights）
- QUALITY_METRIC_NAME: 质量指标显示名称（根据任务自动设置）

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
    print(f"{TASK_NAME.upper()}任务帕累托前沿分析")
    print("="*80)
    print(f"任务名称: {TASK_NAME}")
    print(f"质量处理方法: {QUALITY_METHOD}")
    print("="*80)
    
    # 1. 加载数据
    df = load_and_prepare_data()
    
    # 2. 识别帕累托前沿
    print("\n" + "="*80)
    print("识别帕累托前沿")
    print("="*80)
    
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', x_minimize=False, y_minimize=True)
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    
    pareto_qs = identify_pareto_frontier_2d(df, 'quality', 'speed', x_minimize=True, y_minimize=True)
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
                                          x_minimize=True, y_minimize=True,
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
    # 任务名称映射
    task_name_mapping = {
        'summary': '摘要',
        'qa': '问答',
        'math': '数学',
        'translation': '翻译',
        'code': '代码生成',
        'creative': '创意写作',
        'reasoning': '推理'
    }
    
    # 质量指标映射
    quality_metric_mapping = {
        'summary': 'ROUGE-L得分',
        'qa': 'F1得分',
        'math': '准确率',
        'translation': 'BLEU得分',
        'code': '编译成功率',
        'creative': 'Distinct-2',
        'reasoning': '推理准确率'
    }
    
    task_config = {
        'task_name': TASK_NAME,
        'task_name_cn': task_name_mapping.get(TASK_NAME, TASK_NAME.capitalize()),
        'quality_metric': quality_metric_mapping.get(TASK_NAME, QUALITY_METRIC_NAME),
        'quality_method': QUALITY_METHOD,
        'report_filename': f'{TASK_NAME.upper()}_PARETO_ANALYSIS_REPORT.md'
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
    global TASK_NAME, QUALITY_METHOD, QUALITY_METRIC_NAME, OUTPUT_DIR

    task_list = ['summary', 'qa', 'math', 'code', 'creative', 'reasoning','translation']
    
    print("\n" + "="*80)
    print("批量执行所有任务的帕累托前沿分析")
    print("="*80)
    print(f"任务列表: {', '.join(task_list)}")
    print(f"质量处理方法: pca (PCA降维)")
    print("="*80)
    
    for idx, task in enumerate(task_list, 1):
        print(f"\n\n{'#'*80}")
        print(f"# 进度: {idx}/{len(task_list)} - 正在处理任务: {task.upper()}")
        print(f"{'#'*80}\n")
        
        TASK_NAME = task
        QUALITY_METHOD = 'pca'  # 可选: 'entropy', 'single', 'pca', 'mean', 'custom'
        QUALITY_METRIC_NAME = '质量得分'  # 将根据任务自动设置

        OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis_v3' / TASK_NAME
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        try:
            main()
            print(f"\n✓ 任务 {task.upper()} 完成！")
        except Exception as e:
            print(f"\n✗ 任务 {task.upper()} 失败: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n\n" + "="*80)
    print("所有任务分析完成！")
    print("="*80)
    print(f"结果保存在: {PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis_v3'}")
    print("="*80)
