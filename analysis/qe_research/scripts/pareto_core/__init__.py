"""
帕累托前沿分析核心模块

包含高级分析类和共享函数
"""

# 尝试导入高级类（如果存在）
try:
    from .entropy_weight import EntropyWeightCalculator
    from .pareto_identifier import ParetoFrontierIdentifier
    from .quantitative_metrics import QuantitativeMetricsCalculator
    from .robustness import RobustnessAnalyzer
    from .report_generator import ReportGenerator
    _has_advanced_classes = True
except ImportError:
    _has_advanced_classes = False

# 导入共享配置和函数
from .config import MODEL_MAPPING, DATA_PATHS, OUTPUT_ROOT, PROJECT_ROOT
from .shared_functions import (
    identify_pareto_frontier_2d,
    identify_pareto_frontier_3d,
    calculate_hypervolume,
    calculate_spacing,
    find_knee_point,
    plot_pareto_2d,
    load_energy_speed_data,
    merge_quality_metrics,
    perturbation_analysis,
    cross_validation_pareto,
    generate_pareto_report,
    print_analysis_summary
)

# 构建导出列表
__all__ = [
    # 配置
    'MODEL_MAPPING',
    'DATA_PATHS',
    'OUTPUT_ROOT',
    'PROJECT_ROOT',
    # 共享函数
    'identify_pareto_frontier_2d',
    'identify_pareto_frontier_3d',
    'calculate_hypervolume',
    'calculate_spacing',
    'find_knee_point',
    'plot_pareto_2d',
    'load_energy_speed_data',
    'merge_quality_metrics',
    # 稳健性分析
    'perturbation_analysis',
    'cross_validation_pareto',
    # 报告生成
    'generate_pareto_report',
    'print_analysis_summary',
]

# 如果高级类可用，添加到导出列表
if _has_advanced_classes:
    __all__.extend([
        'EntropyWeightCalculator',
        'ParetoFrontierIdentifier',
        'QuantitativeMetricsCalculator',
        'RobustnessAnalyzer',
        'ReportGenerator'
    ])
