"""
测试假设检验功能的简单脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from analysis.qe_research.scripts.raw_data_analysis import RawDataAnalyzer

def main():
    print("=" * 80)
    print("测试假设检验功能")
    print("=" * 80)
    
    # 创建分析器实例
    analyzer = RawDataAnalyzer(data_root='data')
    
    # 加载数据
    print("\n加载原始数据...")
    analyzer.load_all_raw_data()
    
    if len(analyzer.experiments) == 0:
        print("警告: 未找到实验数据")
        return
    
    print(f"成功加载 {len(analyzer.experiments)} 个实验")
    
    # 运行假设检验分析
    print("\n运行假设检验分析...")
    analyzer.analyze_hypothesis_testing()
    
    print("\n" + "=" * 80)
    print("假设检验分析完成!")
    print("=" * 80)
    print(f"\n结果位置:")
    print(f"  - 表格: {analyzer.tables_dir}/")
    print(f"  - 图表: {analyzer.figures_dir}/")
    print(f"  - 报告: {analyzer.reports_dir}/hypothesis_testing_report.md")

if __name__ == '__main__':
    main()
