"""
修复 pareto_mixed_task.py 的导入问题 - V2
"""

from pathlib import Path

# 读取文件
file_path = Path(__file__).parent / 'pareto_mixed_task.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到需要替换的行
new_lines = []
skip_until = -1
i = 0

while i < len(lines):
    line = lines[i]
    
    # 跳过已标记要跳过的行
    if i < skip_until:
        i += 1
        continue
    
    # 找到 "from pareto_core import (" 开始的导入
    if 'from pareto_core import (' in line:
        # 跳过整个导入块直到找到结束的 ")"
        j = i
        while j < len(lines) and ')' not in lines[j]:
            j += 1
        skip_until = j + 1
        
        # 插入新的导入
        new_lines.append('# 添加 scripts 目录到路径，以便导入 pareto_core\n')
        new_lines.append("sys.path.insert(0, str(project_root / 'analysis' / 'qe_research' / 'scripts'))\n")
        new_lines.append('\n')
        new_lines.append('from pareto_core.shared_functions import (\n')
        new_lines.append('    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,\n')
        new_lines.append('    identify_pareto_frontier_2d, identify_pareto_frontier_3d,\n')
        new_lines.append('    calculate_hypervolume, calculate_spacing, find_knee_point,\n')
        new_lines.append('    plot_pareto_2d, load_energy_speed_data,\n')
        new_lines.append('    perturbation_analysis, cross_validation_pareto,\n')
        new_lines.append('    generate_pareto_report, print_analysis_summary\n')
        new_lines.append(')\n')
        new_lines.append('from pareto_core.process_quality_data import load_process_quality_data\n')
        i = skip_until
        continue
    
    new_lines.append(line)
    i += 1

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✓ 导入部分已修复")
print(f"✓ 文件已更新: {file_path}")
