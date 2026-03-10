"""
测试模型映射修复

验证 merge_energy_speed_data 函数是否正确使用 MODEL_MAPPING
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from pareto_core import MODEL_MAPPING, DATA_PATHS, load_energy_speed_data

print("="*80)
print("测试模型映射修复")
print("="*80)

# 1. 加载能耗和速度数据（以code任务为例）
print("\n步骤1: 加载能耗和速度数据")
energy_dict, speed_dict = load_energy_speed_data(
    'code',
    DATA_PATHS['energy'],
    DATA_PATHS['speed']
)

print(f"能耗数据键数量: {len(energy_dict)}")
print(f"速度数据键数量: {len(speed_dict)}")
print(f"\n能耗数据键示例:")
for i, key in enumerate(list(energy_dict.keys())[:5]):
    print(f"  {i+1}. {key}")

# 2. 测试 MODEL_MAPPING
print(f"\n步骤2: 测试 MODEL_MAPPING")
print(f"MODEL_MAPPING 条目数: {len(MODEL_MAPPING)}")
print(f"\nMODEL_MAPPING 示例:")
for i, (short, full) in enumerate(list(MODEL_MAPPING.items())[:5]):
    print(f"  {i+1}. {short} -> {full}")

# 3. 验证映射是否正确
print(f"\n步骤3: 验证映射")
missing_models = []
found_models = []

for short_name, full_name in MODEL_MAPPING.items():
    if full_name in energy_dict and full_name in speed_dict:
        found_models.append(short_name)
        print(f"✓ {short_name} -> {full_name} (找到)")
    else:
        missing_models.append(short_name)
        print(f"✗ {short_name} -> {full_name} (缺失)")

print(f"\n总结:")
print(f"  找到的模型: {len(found_models)}/{len(MODEL_MAPPING)}")
print(f"  缺失的模型: {len(missing_models)}/{len(MODEL_MAPPING)}")

if missing_models:
    print(f"\n缺失的模型列表:")
    for model in missing_models:
        print(f"  - {model}")
else:
    print(f"\n✓ 所有模型都能正确映射！")

print("\n" + "="*80)
