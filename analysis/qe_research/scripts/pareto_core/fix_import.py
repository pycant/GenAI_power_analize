"""
修复 pareto_mixed_task.py 的导入问题
"""

import re
from pathlib import Path

# 读取文件
file_path = Path(__file__).parent / 'pareto_mixed_task.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 定义正确的导入部分
correct_imports = '''import sys
from pathlib import Path
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import Dict, List, Optional

# 设置工作目录为项目根目录（必须在导入 pareto_core 之前）
project_root = Path(__file__).parent.parent.parent.parent
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# 添加 scripts 目录到路径，以便导入 pareto_core
sys.path.insert(0, str(project_root / 'analysis' / 'qe_research' / 'scripts'))

from pareto_core.shared_functions import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d, identify_pareto_frontier_3d,
    calculate_hypervolume, calculate_spacing, find_knee_point,
    plot_pareto_2d, load_energy_speed_data,
    perturbation_analysis, cross_validation_pareto,
    generate_pareto_report, print_analysis_summary
)
from pareto_core.process_quality_data import load_process_quality_data

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
'''

# 找到导入部分的结束位置（第一个 # ==== 或 WEIGHT_CONFIGS）
pattern = r'(""".*?""")\s*(import sys.*?)(# ={70,}|WEIGHT_CONFIGS\s*=)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # 替换导入部分
    new_content = match.group(1) + '\n\n' + correct_imports + '\n\n\n' + match.group(3)
    # 保留后面的内容
    rest_content = content[match.end(3):]
    final_content = new_content + rest_content
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print("✓ 导入部分已修复")
    print(f"✓ 文件已更新: {file_path}")
else:
    print("✗ 无法找到导入部分，请手动修复")
