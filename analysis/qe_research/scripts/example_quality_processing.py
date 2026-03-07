"""
质量数据处理示例脚本

演示如何使用 process_quality_data.py 模块
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pareto_core.process_quality_data import QualityDataProcessor, quick_process
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
matplotlib.rcParams['axes.unicode_minus'] = False


def example_1_basic_usage():
    """示例1: 基础用法"""
    print("\n" + "="*80)
    print("示例1: 基础用法 - 加载和查看数据")
    print("="*80)
    
    # 初始化处理器
    processor = QualityDataProcessor(task_name='code', verbose=True)
    
    # 加载数据
    data = processor.load_quality_data()
    
    # 查看数据
    print("\n数据预览:")
    print(data.head())
    
    # 描述性统计
    print("\n描述性统计:")
    stats = processor.get_summary_statistics()
    print(stats[['mean', 'std', 'min', 'max', 'missing_pct']])


def example_2_normalization():
    """示例2: 数据归一化"""
    print("\n" + "="*80)
    print("示例2: 数据归一化对比")
    print("="*80)
    
    processor = QualityDataProcessor(task_name='code', verbose=False)
    data = processor.load_quality_data()
    
    # 选择一个指标进行对比
    metric = 'compilation_rate'
    
    print(f"\n对比指标: {metric}")
    print(f"原始数据: {data[metric].values}")
    
    # 不同归一化方法
    methods = ['minmax', 'zscore', 'robust']
    
    for method in methods:
        normalized = processor.normalize(method=method)
        print(f"\n{method.upper()} 归一化: {normalized[metric].values}")


def example_3_entropy_weights():
    """示例3: 熵权法计算权重"""
    print("\n" + "="*80)
    print("示例3: 熵权法计算指标权重")
    print("="*80)
    
    processor = QualityDataProcessor(task_name='reasoning', verbose=True)
    data = processor.load_quality_data()
    
    # 计算熵权
    weights = processor.calculate_entropy_weights()
    
    # 获取加权质量得分
    quality_score = processor.get_weighted_quality_score(weights)
    
    # 可视化权重
    weights_df = pd.DataFrame(list(weights.items()), columns=['指标', '权重'])
    weights_df = weights_df.sort_values('权重', ascending=True)
    
    plt.figure(figsize=(10, 8))
    plt.barh(weights_df['指标'], weights_df['权重'])
    plt.xlabel('权重')
    plt.title('Reasoning任务 - 熵权法指标权重')
    plt.tight_layout()
    plt.savefig('entropy_weights_reasoning.png', dpi=300, bbox_inches='tight')
    print("\n✓ 权重可视化已保存: entropy_weights_reasoning.png")
    
    # 可视化质量得分
    quality_score_sorted = quality_score.sort_values(ascending=True)
    
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(quality_score_sorted)), quality_score_sorted.values)
    plt.yticks(range(len(quality_score_sorted)), quality_score_sorted.index)
    plt.xlabel('加权质量得分')
    plt.title('Reasoning任务 - 模型质量得分排名')
    plt.tight_layout()
    plt.savefig('quality_scores_reasoning.png', dpi=300, bbox_inches='tight')
    print("✓ 质量得分可视化已保存: quality_scores_reasoning.png")


def example_4_pca():
    """示例4: PCA降维分析"""
    print("\n" + "="*80)
    print("示例4: PCA降维分析")
    print("="*80)
    
    processor = QualityDataProcessor(task_name='reasoning', verbose=True)
    data = processor.load_quality_data()
    
    # PCA降维到2维
    pca_result = processor.apply_pca(n_components=2)
    pca_data = pca_result['transformed']
    
    # 可视化
    plt.figure(figsize=(10, 8))
    plt.scatter(pca_data['PC1'], pca_data['PC2'], s=150, alpha=0.6, c='steelblue')
    
    # 添加模型标签
    for idx, model in enumerate(pca_data.index):
        plt.annotate(model, 
                    (pca_data.iloc[idx, 0], pca_data.iloc[idx, 1]),
                    fontsize=9, alpha=0.8, ha='center')
    
    var1 = pca_result['explained_variance_ratio'][0]
    var2 = pca_result['explained_variance_ratio'][1]
    
    plt.xlabel(f"PC1 ({var1:.1%} 方差)")
    plt.ylabel(f"PC2 ({var2:.1%} 方差)")
    plt.title(f'Reasoning任务 - PCA降维可视化\n累积方差: {var1+var2:.1%}')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('pca_visualization_reasoning.png', dpi=300, bbox_inches='tight')
    print("\n✓ PCA可视化已保存: pca_visualization_reasoning.png")
    
    # 显示主要贡献指标
    print("\n主成分载荷矩阵（前5个指标）:")
    components = pca_result['components']
    for pc in ['PC1', 'PC2']:
        print(f"\n{pc}:")
        top_features = components[pc].abs().sort_values(ascending=False).head(5)
        for feat, load in top_features.items():
            sign = '+' if components.loc[feat, pc] > 0 else '-'
            print(f"  {sign} {feat:<30} {load:.3f}")


def example_5_multi_task_comparison():
    """示例5: 多任务对比分析"""
    print("\n" + "="*80)
    print("示例5: 多任务质量对比分析")
    print("="*80)
    
    tasks = ['code', 'creative', 'qa', 'reasoning']
    all_scores = {}
    
    for task in tasks:
        print(f"\n处理任务: {task.upper()}")
        processor = QualityDataProcessor(task_name=task, verbose=False)
        data = processor.load_quality_data()
        
        # 计算熵权法得分
        weights = processor.calculate_entropy_weights()
        quality_score = processor.get_weighted_quality_score(weights)
        
        all_scores[task] = quality_score
        print(f"  ✓ 完成: {len(quality_score)} 个模型")
    
    # 合并所有任务的得分
    scores_df = pd.DataFrame(all_scores)
    
    # 计算平均得分
    scores_df['average'] = scores_df.mean(axis=1)
    
    print("\n跨任务质量得分:")
    print(scores_df.round(4))
    
    # 可视化
    scores_sorted = scores_df.sort_values('average', ascending=True)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = range(len(scores_sorted))
    width = 0.15
    
    for i, task in enumerate(tasks):
        offset = (i - len(tasks)/2 + 0.5) * width
        ax.barh([xi + offset for xi in x], scores_sorted[task], 
               width, label=task.upper(), alpha=0.8)
    
    ax.set_yticks(x)
    ax.set_yticklabels(scores_sorted.index)
    ax.set_xlabel('质量得分')
    ax.set_title('多任务质量得分对比')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig('multi_task_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✓ 多任务对比图已保存: multi_task_comparison.png")
    
    # 显示排名
    print("\n平均质量得分排名:")
    for rank, (model, score) in enumerate(scores_df['average'].sort_values(ascending=False).items(), 1):
        print(f"  {rank}. {model:<30} {score:.4f}")


def example_6_quick_process():
    """示例6: 一键处理"""
    print("\n" + "="*80)
    print("示例6: 一键处理流程")
    print("="*80)
    
    output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'example_quality_processing'
    
    results = quick_process(
        task_name='code',
        normalize_method='minmax',
        use_entropy=True,
        use_pca=True,
        n_components=2,
        output_dir=output_dir
    )
    
    print("\n✓ 一键处理完成！")
    print(f"  输出目录: {output_dir}")
    print(f"\n可用结果:")
    for key in results.keys():
        if key != 'processor':
            print(f"  - {key}")


def main():
    """运行所有示例"""
    print("\n" + "="*80)
    print("质量数据处理模块使用示例")
    print("="*80)
    
    examples = [
        ("基础用法", example_1_basic_usage),
        ("数据归一化", example_2_normalization),
        ("熵权法", example_3_entropy_weights),
        ("PCA降维", example_4_pca),
        ("多任务对比", example_5_multi_task_comparison),
        ("一键处理", example_6_quick_process),
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
    print("  - entropy_weights_reasoning.png")
    print("  - quality_scores_reasoning.png")
    print("  - pca_visualization_reasoning.png")
    print("  - multi_task_comparison.png")
    print("  - analysis/qe_research/results/example_quality_processing/")


if __name__ == '__main__':
    main()
