"""
测试PCA绘图和报告生成功能

验证 plot_pca_figures() 和 generate_pca_report() 函数是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(project_root))

from analysis.qe_research.scripts.pareto_core.shared_functions import (
    load_process_quality_data
)


def test_pca_plotting():
    """测试PCA绘图和报告生成功能"""
    
    print("="*80)
    print("测试PCA绘图和报告生成功能")
    print("="*80)
    
    # 测试任务列表
    test_tasks = ['code', 'creative', 'reasoning']
    
    for task in test_tasks:
        print(f"\n{'='*80}")
        print(f"测试任务: {task.upper()}")
        print(f"{'='*80}")
        
        try:
            # 设置输出目录
            output_dir = Path(__file__).parent.parent.parent / 'results' / 'test_pca_plotting' / task
            
            # 使用PCA方法加载数据（会自动调用绘图和报告生成函数）
            quality_df = load_process_quality_data(
                task_name=task,
                method='pca',
                normalize_method='minmax',
                use_raw=True,
                verbose=True,
                output_dir=output_dir
            )
            
            print(f"\n✓ {task} 任务测试成功")
            print(f"  - 模型数量: {len(quality_df)}")
            print(f"  - 质量得分范围: [{quality_df['quality'].min():.4f}, {quality_df['quality'].max():.4f}]")
            print(f"  - 输出目录: {output_dir}")
            
            # 检查生成的文件
            pca_dir = output_dir / 'pca_analysis'
            if pca_dir.exists():
                png_files = list(pca_dir.glob('*.png'))
                md_files = list(pca_dir.glob('*.md'))
                
                print(f"\n  生成的文件:")
                print(f"  - 图表数量: {len(png_files)}")
                for f in png_files:
                    print(f"    • {f.name}")
                
                print(f"  - 报告数量: {len(md_files)}")
                for f in md_files:
                    print(f"    • {f.name}")
                    # 显示报告文件大小
                    size_kb = f.stat().st_size / 1024
                    print(f"      大小: {size_kb:.1f} KB")
            
        except Exception as e:
            print(f"\n✗ {task} 任务测试失败: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("测试完成")
    print(f"{'='*80}")
    print("\n提示: 请查看生成的报告文件以验证内容完整性")
    print("报告位置: analysis/qe_research/results/test_pca_plotting/{task}/pca_analysis/PCA_ANALYSIS_REPORT.md")


if __name__ == '__main__':
    test_pca_plotting()
