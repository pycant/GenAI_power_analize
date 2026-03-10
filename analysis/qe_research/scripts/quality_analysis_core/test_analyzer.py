"""
测试质量数据分析器
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
    print("测试质量数据分析器")
    print("="*80)
    
    # 创建分析器实例
    analyzer = QualityDataAnalyzer(use_raw=True)
    
    # 测试加载数据
    print("\n测试1: 加载数据")
    analyzer.load_all_data()
    
    # 检查加载结果
    loaded_count = sum(1 for v in analyzer.data.values() if v is not None)
    print(f"\n成功加载 {loaded_count} 个任务")
    
    if loaded_count > 0:
        # 测试单个任务分析
        print("\n测试2: 分析单个任务（code）")
        if analyzer.data.get('code') is not None:
            code_results = analyzer.analyze_task('code')
            print(f"  - 模型数: {code_results['n_models']}")
            print(f"  - 指标数: {code_results['n_metrics']}")
            print(f"  - 关键发现数: {len(code_results['key_findings'])}")
        
        print("\n测试完成！")
        print("如果上述测试通过，可以运行完整分析：")
        print("  analyzer.run_all_analyses()")
    else:
        print("\n警告: 没有成功加载任何数据")
        print("请检查数据文件路径是否正确")
