#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试空闲基线功耗测量功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from experiments.experiment_runner import ExperimentRunner

def test_idle_baseline_measurement():
    """测试空闲基线测量功能"""
    print("="*70)
    print("测试空闲基线功耗测量功能")
    print("="*70)
    
    # 创建实验运行器
    runner = ExperimentRunner(output_dir="./data/test")
    
    # 测试用例1: 使用Ollama模型 + 空闲基线测量
    print("\n[测试1] Ollama模型 + 10秒空闲基线测量")
    test_case_1 = {
        "model": "ollama:qwen3:4b",
        "prompts": ["什么是Python？"],
        "task_type": "qa",
        "max_tokens": 100,
        "temperature": 0.7,
        "idle_measurement_duration": 10
    }
    
    result_1 = runner.run_single_experiment(
        model=test_case_1["model"],
        prompts=test_case_1["prompts"],
        task_type=test_case_1["task_type"],
        max_tokens=test_case_1["max_tokens"],
        temperature=test_case_1["temperature"],
        idle_measurement_duration=test_case_1["idle_measurement_duration"]
    )
    
    if result_1:
        print("\n✅ 测试1通过")
        print(f"  - 空闲基线数据: {'存在' if 'baseline' in result_1 else '不存在'}")
        if 'baseline' in result_1:
            baseline = result_1['baseline']
            print(f"  - P_idle: {baseline['gpu_power_avg_w']:.2f} W")
            print(f"  - 测量时长: {baseline['duration_seconds']} 秒")
        
        if 'resources' in result_1:
            resources = result_1['resources']
            print(f"  - P_inc: {resources.get('P_inc', 'N/A')}")
            print(f"  - E_inc: {resources.get('E_inc', 'N/A')}")
            print(f"  - E_token: {resources.get('E_token', 'N/A')}")
            print(f"  - PPW: {resources.get('PPW', 'N/A')}")
            print(f"  - TPJ: {resources.get('TPJ', 'N/A')}")
    else:
        print("\n❌ 测试1失败")
    
    # 测试用例2: 不使用空闲基线测量（默认行为）
    print("\n[测试2] Ollama模型 + 不测量空闲基线")
    test_case_2 = {
        "model": "ollama:qwen3:4b",
        "prompts": ["解释一下机器学习。"],
        "task_type": "qa",
        "max_tokens": 100,
        "temperature": 0.7,
        "idle_measurement_duration": 0  # 不测量
    }
    
    result_2 = runner.run_single_experiment(
        model=test_case_2["model"],
        prompts=test_case_2["prompts"],
        task_type=test_case_2["task_type"],
        max_tokens=test_case_2["max_tokens"],
        temperature=test_case_2["temperature"],
        idle_measurement_duration=test_case_2["idle_measurement_duration"]
    )
    
    if result_2:
        print("\n✅ 测试2通过")
        print(f"  - 空闲基线数据: {'存在' if 'baseline' in result_2 else '不存在'}")
        print(f"  - 增量指标: {'存在' if 'P_inc' in result_2.get('resources', {}) else '不存在'}")
    else:
        print("\n❌ 测试2失败")
    
    # 清理
    runner.cleanup()
    
    print("\n" + "="*70)
    print("测试完成")
    print("="*70)

if __name__ == "__main__":
    try:
        test_idle_baseline_measurement()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
