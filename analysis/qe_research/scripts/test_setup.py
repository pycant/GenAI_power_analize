"""
测试研究环境设置
验证所有依赖和配置是否正确
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import logging

print("=" * 80)
print("质效比研究环境测试")
print("=" * 80)

# 1. 测试Python包
print("\n[1/6] 测试Python包...")
packages = {
    'pandas': pd.__version__,
    'numpy': np.__version__,
    'matplotlib': plt.matplotlib.__version__,
    'seaborn': sns.__version__,
}

for pkg, version in packages.items():
    print(f"  ✓ {pkg}: {version}")

# 2. 测试配置文件
print("\n[2/6] 测试配置文件...")
config_path = project_root / 'analysis' / 'qe_research' / 'configs' / 'analysis_config.yaml'
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    print(f"  ✓ 配置文件加载成功: {config_path}")
    print(f"    - 数据路径: {config['data']['base_path']}")
    print(f"    - 输出路径: {config['data']['output_path']}")
else:
    print(f"  ✗ 配置文件不存在: {config_path}")

# 3. 测试数据管道
print("\n[3/6] 测试数据管道...")
try:
    from data.analize.pipeline import ExperimentDataManager
    dm = ExperimentDataManager()
    print("  ✓ 数据管理器初始化成功")
    
    # 检查数据文件
    master_file = dm.processed_path / 'master_data.parquet'
    if master_file.exists():
        print(f"  ✓ 主数据文件存在: {master_file}")
        df = dm.load_all_data()
        print(f"    - 数据行数: {len(df)}")
        print(f"    - 数据列数: {len(df.columns)}")
        print(f"    - 模型数量: {df['model_name'].nunique()}")
        print(f"    - 任务类型: {df['task_type'].nunique()}")
    else:
        print(f"  ⚠ 主数据文件不存在，需要初始化数据管道")
        print(f"    运行: python scripts/test_and_explore_pipeline.py")
except Exception as e:
    print(f"  ✗ 数据管道测试失败: {e}")

# 4. 测试输出目录
print("\n[4/6] 测试输出目录...")
output_dirs = [
    'analysis/qe_research/results/figures',
    'analysis/qe_research/results/tables',
    'analysis/qe_research/results/reports',
    'analysis/qe_research/results/exports',
    'analysis/qe_research/logs',
    'analysis/qe_research/cache',
]

for dir_path in output_dirs:
    full_path = project_root / dir_path
    if full_path.exists():
        print(f"  ✓ {dir_path}")
    else:
        print(f"  ✗ {dir_path} (不存在)")

# 5. 测试中文字体
print("\n[5/6] 测试中文字体...")
try:
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建测试图表
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.text(0.5, 0.5, '中文测试', fontsize=20, ha='center', va='center')
    ax.set_title('字体测试')
    
    test_fig_path = project_root / 'analysis' / 'qe_research' / 'results' / 'figures' / 'font_test.png'
    plt.savefig(test_fig_path, dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ 中文字体设置成功")
    print(f"    测试图表: {test_fig_path}")
except Exception as e:
    print(f"  ⚠ 中文字体设置失败: {e}")
    print(f"    图表将使用英文标签")

# 6. 测试日志
print("\n[6/6] 测试日志...")
try:
    log_path = project_root / 'analysis' / 'qe_research' / 'logs' / 'test.log'
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("测试日志记录")
    print(f"  ✓ 日志系统正常")
    print(f"    日志文件: {log_path}")
except Exception as e:
    print(f"  ✗ 日志系统失败: {e}")

# 总结
print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)
print("\n下一步:")
print("1. 如果数据管道未初始化，运行:")
print("   python scripts/test_and_explore_pipeline.py")
print("\n2. 运行综合分析:")
print("   python analysis/qe_research/scripts/comprehensive_analysis.py")
print("\n3. 查看快速开始指南:")
print("   notepad analysis/qe_research/QUICK_START.md")
print("=" * 80)
