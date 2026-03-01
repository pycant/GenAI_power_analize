#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
import glob
import os

# 查找最新的结果文件
result_files = glob.glob('data/test/experiment_results_*.json')
if not result_files:
    print("未找到结果文件")
    sys.exit(1)

latest_file = max(result_files, key=os.path.getctime)
print(f"读取最新结果文件: {latest_file}\n")

# 读取结果文件
with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("多轮对话实验结果检查")
print("=" * 70)

for i, exp in enumerate(data, 1):
    print(f"\n实验 {i}: {exp['model']}")
    print(f"  任务类型: {exp['task_type']}")
    print(f"  对话轮数: {exp['performance']['turns']}")
    print(f"  保持上下文: {'是' if exp['keep_context'] else '否'}")
    print(f"  总耗时: {exp['performance']['total_time_seconds']:.2f}秒")
    print(f"  平均每轮: {exp['performance']['avg_time_per_turn']:.2f}秒")
    
    print(f"\n  对话内容:")
    for turn in exp['conversation']:
        print(f"    轮次 {turn['turn']}:")
        print(f"      提示: {turn['prompt'][:50]}...")
        response = turn['response']
        if response:
            print(f"      回复: {response[:100]}...")
        else:
            print(f"      回复: (空字符串)")
            # 检查metadata中是否有response
            if 'metadata' in exp and 'response_metadata' in exp.get('metadata', {}):
                print(f"      注意: 可能在metadata中")

print("\n" + "=" * 70)
