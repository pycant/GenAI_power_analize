"""
最终修复脚本 - 使用精确的行号替换
"""

from pathlib import Path

file_path = Path(__file__).parent / 'pareto_mixed_task.py'

# 读取所有行
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要修改的行
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 在 sys.path.insert(0, str(project_root)) 之后添加新行
    if 'sys.path.insert(0, str(project_root))' in line and 'scripts' not in line:
        new_lines.append(line)
        # 添加新的路径
        new_lines.append("\n")
        new_lines.append("# 添加 scripts 目录到路径，以便导入 pareto_core\n")
        new_lines.append("sys.path.insert(0, str(project_root / 'analysis' / 'qe_research' / 'scripts'))\n")
        i += 1
        continue
    
    # 替换 from pareto_core import 行
    if line.strip().startswith('from pareto_core import'):
        # 跳过整个导入块
        while i < len(lines) and ')' not in lines[i]:
            i += 1
        i += 1  # 跳过包含 ) 的行
        
        # 添加新的导入
        new_lines.append("\n")
        new_lines.append("from pareto_core.shared_functions import (\n")
        new_lines.append("    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,\n")
        new_lines.append("    identify_pareto_frontier_2d, identify_pareto_frontier_3d,\n")
        new_lines.append("    calculate_hypervolume, calculate_spacing, find_knee_point,\n")
        new_lines.append("    plot_pareto_2d, load_energy_speed_data,\n")
        new_lines.append("    perturbation_analysis, cross_validation_pareto,\n")
        new_lines.append("    generate_pareto_report, print_analysis_summary\n")
        new_lines.append(")\n")
        new_lines.append("from pareto_core.process_quality_data import load_process_quality_data\n")
        continue
    
    new_lines.append(line)
    i += 1

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ 导入已修复")
print(f"✓ 文件: {file_path}")
