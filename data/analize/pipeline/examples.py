"""
数据管道使用示例
"""
import sys
from pathlib import Path
import pandas as pd
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data.analize.pipeline import ExperimentDataManager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("\n" + "="*70)
    print("示例1: 基本使用")
    print("="*70)
    
    # 创建数据管理器
    dm = ExperimentDataManager()
    
    # 加载所有数据
    df = dm.load_all_data()
    print(f"\n总数据: {len(df)} 行, {len(df.columns)} 列")
    print(f"列名: {df.columns.tolist()}")


def example_2_filter_by_task():
    """示例2: 按任务类型筛选"""
    print("\n" + "="*70)
    print("示例2: 按任务类型筛选")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 获取所有任务类型
    tasks = dm.list_tasks()
    print(f"\n可用任务: {tasks}")
    
    # 筛选代码生成任务
    if 'code' in tasks:
        df_code = dm.get_by_task('code')
        print(f"\n代码生成任务: {len(df_code)} 行")
        print(df_code[['model_name', 'latency_s', 'toks_per_s']].head())


def example_3_filter_by_model():
    """示例3: 按模型筛选"""
    print("\n" + "="*70)
    print("示例3: 按模型筛选")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 获取所有模型
    models = dm.list_models()
    print(f"\n可用模型: {models}")
    
    # 筛选特定模型
    if models:
        model = models[0]
        df_model = dm.get_by_model(model)
        print(f"\n模型 '{model}': {len(df_model)} 行")
        print(df_model[['task_type', 'latency_s', 'gpu_energy_j']].head())


def example_4_quality_metrics():
    """示例4: 质量指标分析"""
    print("\n" + "="*70)
    print("示例4: 质量指标分析")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 获取归一化的质量指标
    quality = dm.get_quality_metrics(normalized=True)
    print(f"\n质量指标: {quality.shape}")
    
    # 统计分析
    norm_cols = [col for col in quality.columns if col.startswith('norm_')]
    if norm_cols:
        print("\n归一化质量指标统计:")
        print(quality[norm_cols].describe())


def example_5_efficiency_metrics():
    """示例5: 效率指标分析"""
    print("\n" + "="*70)
    print("示例5: 效率指标分析")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 获取原始效率指标
    efficiency = dm.get_efficiency_metrics(normalized=False)
    print(f"\n效率指标: {efficiency.shape}")
    
    # 按模型分组统计
    if 'model_name' in efficiency.columns:
        print("\n按模型统计平均延迟:")
        avg_latency = efficiency.groupby('model_name')['latency_s'].mean().sort_values()
        print(avg_latency)


def example_6_composite_score():
    """示例6: 计算复合得分"""
    print("\n" + "="*70)
    print("示例6: 计算复合得分")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 使用默认权重
    scores = dm.compute_composite_score()
    print(f"\n复合得分: {scores.shape}")
    
    if 'composite_score' in scores.columns:
        print("\n复合得分统计:")
        print(scores['composite_score'].describe())
        
        # 按模型排名
        if 'model_name' in scores.columns:
            print("\n按模型平均复合得分排名:")
            ranking = scores.groupby('model_name')['composite_score'].mean().sort_values(ascending=False)
            print(ranking)


def example_7_custom_weights():
    """示例7: 自定义权重"""
    print("\n" + "="*70)
    print("示例7: 自定义权重")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 更重视质量
    weights_quality_focused = {'quality': 0.7, 'efficiency': 0.3}
    scores_q = dm.compute_composite_score(weights=weights_quality_focused)
    
    # 更重视效率
    weights_efficiency_focused = {'quality': 0.3, 'efficiency': 0.7}
    scores_e = dm.compute_composite_score(weights=weights_efficiency_focused)
    
    print("\n质量优先 vs 效率优先:")
    if 'composite_score' in scores_q.columns and 'model_name' in scores_q.columns:
        comparison = pd.DataFrame({
            'quality_focused': scores_q.groupby('model_name')['composite_score'].mean(),
            'efficiency_focused': scores_e.groupby('model_name')['composite_score'].mean(),
        })
        print(comparison)


def example_8_summary_stats():
    """示例8: 汇总统计"""
    print("\n" + "="*70)
    print("示例8: 汇总统计")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 按模型汇总
    print("\n按模型汇总:")
    stats_model = dm.get_summary_stats(by='model')
    print(stats_model.head())
    
    # 按任务汇总
    print("\n按任务汇总:")
    stats_task = dm.get_summary_stats(by='task')
    print(stats_task.head())


def example_9_cross_analysis():
    """示例9: 交叉分析"""
    print("\n" + "="*70)
    print("示例9: 交叉分析 - 模型在不同任务上的表现")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    df = dm.load_all_data()
    
    if 'model_name' in df.columns and 'task_type' in df.columns:
        # 创建透视表
        if 'latency_s' in df.columns:
            pivot = df.pivot_table(
                values='latency_s',
                index='model_name',
                columns='task_type',
                aggfunc='mean'
            )
            print("\n各模型在不同任务上的平均延迟(秒):")
            print(pivot)


def example_10_export_data():
    """示例10: 导出数据"""
    print("\n" + "="*70)
    print("示例10: 导出数据")
    print("="*70)
    
    dm = ExperimentDataManager()
    
    # 获取质量指标
    quality = dm.get_quality_metrics(normalized=True)
    
    # 导出为CSV
    output_file = 'data/analize/cache/quality_metrics_export.csv'
    quality.to_csv(output_file, index=False)
    print(f"\n质量指标已导出到: {output_file}")
    
    # 导出复合得分
    scores = dm.compute_composite_score()
    output_file = 'data/analize/cache/composite_scores_export.csv'
    scores.to_csv(output_file, index=False)
    print(f"复合得分已导出到: {output_file}")


def run_all_examples():
    """运行所有示例"""
    examples = [
        example_1_basic_usage,
        example_2_filter_by_task,
        example_3_filter_by_model,
        example_4_quality_metrics,
        example_5_efficiency_metrics,
        example_6_composite_score,
        example_7_custom_weights,
        example_8_summary_stats,
        example_9_cross_analysis,
        example_10_export_data,
    ]
    
    print("\n" + "="*70)
    print("数据管道使用示例集")
    print("="*70)
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            logger.error(f"示例 {i} 执行失败: {str(e)}", exc_info=True)
            print(f"\n❌ 示例 {i} 失败: {str(e)}")
        
        input("\n按回车继续下一个示例...")
    
    print("\n" + "="*70)
    print("所有示例执行完成")
    print("="*70)


if __name__ == '__main__':
    # 运行所有示例
    run_all_examples()
    
    # 或者运行单个示例
    # example_1_basic_usage()
