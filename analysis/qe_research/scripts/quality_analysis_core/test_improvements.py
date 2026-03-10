"""
测试改进后的质量数据分析器

改进内容：
1. 剔除 qwen25_7b_hf_8bit 模型
2. 增强关键发现的详细程度
3. 添加更多图片描述
4. 使用PCA进行综合排名
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入分析器
from analysis.qe_research.scripts.quality_analysis_core.quality_data_analyzer import QualityDataAnalyzer

if __name__ == '__main__':
    print("="*80)
    print("测试改进后的质量数据分析器")
    print("="*80)
    
    # 创建分析器实例
    analyzer = QualityDataAnalyzer(use_raw=True)
    
    # 测试1: 加载数据（应该剔除qwen25_7b_hf_8bit）
    print("\n测试1: 加载数据并剔除指定模型")
    analyzer.load_all_data()
    
    # 检查是否成功剔除
    for task, df in analyzer.data.items():
        if df is not None:
            if 'qwen25_7b_hf_8bit' in df['model'].values:
                print(f"  警告: {task}任务中仍包含qwen25_7b_hf_8bit")
            else:
                print(f"  OK: {task}任务已成功剔除qwen25_7b_hf_8bit")
    
    # 测试2: 分析单个任务（检查关键发现）
    print("\n测试2: 分析单个任务（检查关键发现详细程度）")
    if analyzer.data.get('code') is not None:
        code_results = analyzer.analyze_task('code')
        print(f"  - 模型数: {code_results['n_models']}")
        print(f"  - 指标数: {code_results['n_metrics']}")
        print(f"  - 关键发现数: {len(code_results['key_findings'])}")
        print("\n  关键发现内容:")
        for i, finding in enumerate(code_results['key_findings'], 1):
            print(f"    {i}. {finding[:80]}...")
    
    # 测试3: 跨任务分析（检查PCA）
    print("\n测试3: 跨任务分析（检查PCA综合排名）")
    cross_results = analyzer.cross_task_analysis()
    
    if 'pca_results' in cross_results:
        pca = cross_results['pca_results']
        print(f"  - 选择主成分数: {pca['n_components']}")
        print(f"  - 累积解释方差: {pca['cumulative_variance'][pca['n_components']-1]:.2%}")
        print(f"  - 主成分权重: {[f'{w:.2%}' for w in pca['weights']]}")
        
        print("\n  Top 5 综合排名:")
        for rank, (model, score) in enumerate(
            cross_results['comprehensive_ranking'].head(5).items(), 1):
            print(f"    {rank}. {model}: {score:.4f}")
    
    # 测试4: 检查生成的图表
    print("\n测试4: 检查生成的图表文件")
    figures_dir = analyzer.figures_dir
    
    expected_figures = [
        'cross_task_heatmap.png',
        'comprehensive_ranking.png',
        'pca_variance_explained.png',
        'cross_task_correlation.png'
    ]
    
    for fig in expected_figures:
        fig_path = figures_dir / fig
        if fig_path.exists():
            print(f"  OK: {fig} 已生成")
        else:
            print(f"  X:  {fig} 未找到")
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    print("\n如果所有测试通过，可以运行完整分析：")
    print("  python quality_data_analyzer.py")
