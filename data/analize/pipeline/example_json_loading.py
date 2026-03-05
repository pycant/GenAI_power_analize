"""
JSON数据加载示例
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def example_1_direct_loading():
    """示例1: 直接使用加载器"""
    print("\n" + "="*70)
    print("示例1: 直接加载Summary JSON数据")
    print("="*70)
    
    from data.analize.pipeline.converters import SummaryJsonLoader
    
    # 创建加载器
    loader = SummaryJsonLoader()
    
    # 列出可用模型
    print("\n可用模型:")
    for model in loader.get_available_models():
        print(f"  - {model}")
    
    # 加载数据
    print("\n加载数据...")
    df = loader.load_all_summary_data()
    
    print(f"\n✓ 加载完成: {len(df)} 条记录")
    
    # 显示基本信息
    print(f"\n数据形状: {df.shape}")
    print(f"\n列名: {df.columns.tolist()}")
    
    # 模型统计
    if 'model_name' in df.columns:
        print("\n模型统计:")
        print(df['model_name'].value_counts())
    
    # 任务类型统计
    if 'task_type' in df.columns:
        print("\n任务类型统计:")
        print(df['task_type'].value_counts())
    
    # 性能指标
    perf_cols = ['latency_s', 'toks_per_s', 'gpu_energy_j']
    available_cols = [col for col in perf_cols if col in df.columns]
    
    if available_cols:
        print("\n性能指标统计:")
        print(df[available_cols].describe())


def example_2_pipeline_integration():
    """示例2: 通过数据管道加载"""
    print("\n" + "="*70)
    print("示例2: 通过数据管道加载（推荐）")
    print("="*70)
    
    from data.analize.pipeline import ExperimentDataManager
    
    # 创建数据管理器
    dm = ExperimentDataManager()
    
    # 初始化管道（自动加载JSON数据）
    print("\n初始化数据管道...")
    dm.initialize_pipeline(force=True)
    
    # 加载所有数据
    print("\n加载数据...")
    df = dm.load_all_data()
    
    print(f"\n✓ 数据加载完成: {len(df)} 行, {len(df.columns)} 列")
    
    # 列出模型
    models = dm.list_models()
    print(f"\n可用模型 ({len(models)}):")
    for model in models:
        print(f"  - {model}")
    
    # 列出任务
    tasks = dm.list_tasks()
    print(f"\n可用任务 ({len(tasks)}):")
    for task in tasks:
        print(f"  - {task}")


def example_3_model_analysis():
    """示例3: 按模型分析"""
    print("\n" + "="*70)
    print("示例3: 按模型分析性能")
    print("="*70)
    
    from data.analize.pipeline import ExperimentDataManager
    
    dm = ExperimentDataManager()
    df = dm.load_all_data()
    
    # 按模型分组统计
    if 'model_name' in df.columns and 'latency_s' in df.columns:
        print("\n各模型平均延迟:")
        avg_latency = df.groupby('model_name')['latency_s'].mean().sort_values()
        for model, latency in avg_latency.items():
            print(f"  {model}: {latency:.2f}秒")
    
    if 'model_name' in df.columns and 'toks_per_s' in df.columns:
        print("\n各模型平均吞吐量:")
        avg_throughput = df.groupby('model_name')['toks_per_s'].mean().sort_values(ascending=False)
        for model, throughput in avg_throughput.items():
            print(f"  {model}: {throughput:.2f} tokens/s")
    
    if 'model_name' in df.columns and 'gpu_energy_j' in df.columns:
        print("\n各模型平均能耗:")
        avg_energy = df.groupby('model_name')['gpu_energy_j'].mean().sort_values()
        for model, energy in avg_energy.items():
            print(f"  {model}: {energy:.2f}焦耳")


def example_4_task_analysis():
    """示例4: 按任务分析"""
    print("\n" + "="*70)
    print("示例4: 按任务类型分析")
    print("="*70)
    
    from data.analize.pipeline import ExperimentDataManager
    
    dm = ExperimentDataManager()
    
    # 获取所有任务
    tasks = dm.list_tasks()
    
    for task in tasks:
        print(f"\n任务: {task}")
        df_task = dm.get_by_task(task)
        
        print(f"  记录数: {len(df_task)}")
        
        if 'model_name' in df_task.columns:
            print(f"  模型数: {df_task['model_name'].nunique()}")
        
        if 'latency_s' in df_task.columns:
            print(f"  平均延迟: {df_task['latency_s'].mean():.2f}秒")
        
        if 'toks_per_s' in df_task.columns:
            print(f"  平均吞吐: {df_task['toks_per_s'].mean():.2f} tokens/s")


def example_5_efficiency_metrics():
    """示例5: 效率指标分析"""
    print("\n" + "="*70)
    print("示例5: 效率指标分析")
    print("="*70)
    
    from data.analize.pipeline import ExperimentDataManager
    
    dm = ExperimentDataManager()
    
    # 获取归一化的效率指标
    efficiency = dm.get_efficiency_metrics(normalized=True)
    
    print(f"\n效率指标: {efficiency.shape}")
    
    # 显示归一化后的指标
    norm_cols = [col for col in efficiency.columns if col.startswith('norm_')]
    if norm_cols:
        print("\n归一化效率指标统计:")
        print(efficiency[norm_cols].describe())
    
    # 按模型排名
    if 'model_name' in efficiency.columns and 'norm_toks_per_s' in efficiency.columns:
        print("\n吞吐量排名（归一化）:")
        ranking = efficiency.groupby('model_name')['norm_toks_per_s'].mean().sort_values(ascending=False)
        for i, (model, score) in enumerate(ranking.items(), 1):
            print(f"  {i}. {model}: {score:.3f}")


def example_6_composite_score():
    """示例6: 计算复合得分"""
    print("\n" + "="*70)
    print("示例6: 计算复合得分")
    print("="*70)
    
    from data.analize.pipeline import ExperimentDataManager
    
    dm = ExperimentDataManager()
    
    # 计算复合得分
    scores = dm.compute_composite_score()
    
    print(f"\n复合得分: {scores.shape}")
    
    # 按模型排名
    if 'model_name' in scores.columns and 'composite_score' in scores.columns:
        print("\n模型综合排名:")
        ranking = scores.groupby('model_name')['composite_score'].mean().sort_values(ascending=False)
        for i, (model, score) in enumerate(ranking.items(), 1):
            print(f"  {i}. {model}: {score:.3f}")
    
    # 质效比排名
    if 'model_name' in scores.columns and 'qe_ratio' in scores.columns:
        print("\n质效比排名:")
        qe_ranking = scores.groupby('model_name')['qe_ratio'].mean().sort_values(ascending=False)
        for i, (model, ratio) in enumerate(qe_ranking.items(), 1):
            print(f"  {i}. {model}: {ratio:.3f}")


def example_7_export_data():
    """示例7: 导出数据"""
    print("\n" + "="*70)
    print("示例7: 导出分析结果")
    print("="*70)
    
    from data.analize.pipeline import ExperimentDataManager
    
    dm = ExperimentDataManager()
    
    # 计算复合得分
    scores = dm.compute_composite_score()
    
    # 导出为CSV
    output_file = 'data/analize/cache/model_scores_export.csv'
    scores.to_csv(output_file, index=False)
    print(f"\n✓ 数据已导出到: {output_file}")
    
    # 导出效率指标
    efficiency = dm.get_efficiency_metrics(normalized=True)
    output_file = 'data/analize/cache/efficiency_metrics_export.csv'
    efficiency.to_csv(output_file, index=False)
    print(f"✓ 效率指标已导出到: {output_file}")


def main():
    """运行所有示例"""
    examples = [
        example_1_direct_loading,
        example_2_pipeline_integration,
        example_3_model_analysis,
        example_4_task_analysis,
        example_5_efficiency_metrics,
        example_6_composite_score,
        example_7_export_data,
    ]
    
    print("="*70)
    print("JSON数据加载示例集")
    print("="*70)
    
    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n❌ 示例 {i} 失败: {e}")
            import traceback
            traceback.print_exc()
        
        if i < len(examples):
            input("\n按回车继续下一个示例...")
    
    print("\n" + "="*70)
    print("所有示例执行完成")
    print("="*70)


if __name__ == '__main__':
    main()
