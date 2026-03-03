#!/usr/bin/env python3
"""验证 experiments_5 配置"""

import json
from pathlib import Path

def verify_experiment_5():
    """验证实验配置"""
    exp_dir = Path("data/experiments_5")
    
    print("="*70)
    print("验证 experiments_5 配置")
    print("="*70)
    
    # 检查目录结构
    print("\n1. 检查目录结构...")
    required_dirs = ["raw", "texts", "summary"]
    for dir_name in required_dirs:
        dir_path = exp_dir / dir_name
        if dir_path.exists():
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (缺失)")
    
    # 检查配置文件
    print("\n2. 检查配置文件...")
    config_files = ["config.py", "config.json", "test_cases.json", "README.md"]
    for file_name in config_files:
        file_path = exp_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {file_name} ({size:,} bytes)")
        else:
            print(f"  ✗ {file_name} (缺失)")
    
    # 加载并验证测试用例
    print("\n3. 验证测试用例...")
    test_cases_file = exp_dir / "test_cases.json"
    with open(test_cases_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"  总测试用例数: {len(test_cases)}")
    
    # 统计任务类型
    task_types = {}
    for tc in test_cases:
        task_type = tc.get("task_type", "unknown")
        task_types[task_type] = task_types.get(task_type, 0) + 1
    
    print(f"\n  任务类型分布:")
    for task_type, count in sorted(task_types.items()):
        print(f"    - {task_type}: {count} 题")
    
    # 检查必需字段
    print(f"\n4. 检查测试用例字段...")
    required_fields = ["id", "model", "task_type", "prompt", "temperature", "max_tokens"]
    missing_fields = []
    
    for i, tc in enumerate(test_cases[:5]):  # 检查前5个
        for field in required_fields:
            if field not in tc:
                missing_fields.append(f"测试用例 {i}: 缺少字段 '{field}'")
    
    if missing_fields:
        print(f"  ⚠️  发现问题:")
        for msg in missing_fields:
            print(f"    - {msg}")
    else:
        print(f"  ✓ 所有必需字段完整")
    
    # 显示示例
    print(f"\n5. 示例测试用例:")
    for task_type in ["qa", "math", "code", "translation"]:
        examples = [tc for tc in test_cases if tc["task_type"] == task_type]
        if examples:
            ex = examples[0]
            print(f"\n  {task_type.upper()}:")
            print(f"    ID: {ex['id']}")
            print(f"    Prompt: {ex['prompt'][:80]}...")
            print(f"    Temperature: {ex['temperature']}")
            print(f"    Max tokens: {ex['max_tokens']}")
            print(f"    Repeat: {ex.get('repeat', 1)}")
    
    # 加载配置
    print(f"\n6. 验证配置...")
    config_file = exp_dir / "config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print(f"  模型数量: {len(config['args']['models'])}")
    print(f"  模型列表:")
    for model in config['args']['models']:
        print(f"    - {model}")
    
    print("\n" + "="*70)
    print("✅ 验证完成！")
    print("="*70)
    print(f"\n实验已准备就绪，可以运行:")
    print(f"  python experiments/experiment_runner.py --config data/experiments_5/config.py")
    print("="*70)


if __name__ == "__main__":
    verify_experiment_5()
