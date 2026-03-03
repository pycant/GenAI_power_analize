#!/usr/bin/env python3
"""
将 Gemma 2B HF 实验配置分成两份，分别使用 4-bit 和 8-bit 量化
"""

import json
import sys
from pathlib import Path

def split_gemma_configs():
    """将 gemma_2b_hf 配置分成 4-bit 和 8-bit 两份"""
    
    # 读取原始配置
    source_file = Path("data/experiments_gemma_2b_hf/test_cases.json")
    
    if not source_file.exists():
        print(f"错误: 找不到源文件 {source_file}")
        return False
    
    with open(source_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"✓ 读取到 {len(test_cases)} 个测试用例")
    
    # 创建 4-bit 配置
    test_cases_4bit = []
    for case in test_cases:
        case_4bit = case.copy()
        # 修改模型路径，添加 4-bit 量化参数
        case_4bit['model'] = "hf:models/huggingface/google--gemma-2b-it:4bit"
        case_4bit['quantization'] = "4bit"
        test_cases_4bit.append(case_4bit)
    
    # 创建 8-bit 配置
    test_cases_8bit = []
    for case in test_cases:
        case_8bit = case.copy()
        # 修改模型路径，添加 8-bit 量化参数
        case_8bit['model'] = "hf:models/huggingface/google--gemma-2b-it:8bit"
        case_8bit['quantization'] = "8bit"
        test_cases_8bit.append(case_8bit)
    
    # 保存 4-bit 配置
    output_4bit = Path("data/experiments_gemma_2b_hf_4bit/test_cases.json")
    output_4bit.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_4bit, 'w', encoding='utf-8') as f:
        json.dump(test_cases_4bit, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已生成 4-bit 配置: {output_4bit}")
    print(f"  - 测试用例数: {len(test_cases_4bit)}")
    print(f"  - 模型: hf:models/huggingface/google--gemma-2b-it:4bit")
    
    # 保存 8-bit 配置
    output_8bit = Path("data/experiments_gemma_2b_hf_8bit/test_cases.json")
    output_8bit.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_8bit, 'w', encoding='utf-8') as f:
        json.dump(test_cases_8bit, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已生成 8-bit 配置: {output_8bit}")
    print(f"  - 测试用例数: {len(test_cases_8bit)}")
    print(f"  - 模型: hf:models/huggingface/google--gemma-2b-it:8bit")
    
    # 统计信息
    print("\n配置统计:")
    task_types = {}
    for case in test_cases:
        task_type = case.get('task_type', 'unknown')
        task_types[task_type] = task_types.get(task_type, 0) + 1
    
    for task_type, count in sorted(task_types.items()):
        print(f"  - {task_type}: {count} 个任务")
    
    print("\n✓ 配置文件生成完成！")
    print("\n运行实验:")
    print("  # 4-bit 量化")
    print("  python experiments/experiment_runner.py \\")
    print("    --config data/experiments_gemma_2b_hf_4bit/test_cases.json \\")
    print("    --output-dir data/experiments_gemma_2b_hf_4bit \\")
    print("    --skip-bartscore")
    print()
    print("  # 8-bit 量化")
    print("  python experiments/experiment_runner.py \\")
    print("    --config data/experiments_gemma_2b_hf_8bit/test_cases.json \\")
    print("    --output-dir data/experiments_gemma_2b_hf_8bit \\")
    print("    --skip-bartscore")
    
    return True

if __name__ == "__main__":
    success = split_gemma_configs()
    sys.exit(0 if success else 1)
