"""
质量数据分析运行脚本
快速启动质量数据描述性分析
"""
import sys
from pathlib import Path

# 添加quality_analysis_core目录到路径
current_dir = Path(__file__).parent
core_dir = current_dir / 'quality_analysis_core'
sys.path.insert(0, str(core_dir))

from quality_data_analyzer import QualityDataAnalyzer

def main():
    """运行质量数据分析"""
    print("=" * 80)
    print("质量数据描述性分析")
    print("=" * 80)
    print()
    
    # 创建分析器并运行
    analyzer = QualityDataAnalyzer(use_raw=True)
    analyzer.run_all_analyses()
    
    print()
    print("分析完成! 请查看输出目录:")
    print("  - 报告: analysis/qe_research/results/quality_analysis/reports/")
    print("  - 图表: analysis/qe_research/results/quality_analysis/figures/")
    print("  - 表格: analysis/qe_research/results/quality_analysis/tables/")


if __name__ == '__main__':
    main()
