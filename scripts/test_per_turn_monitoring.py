#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from experiments.experiment_runner import ExperimentRunner

# 创建运行器
runner = ExperimentRunner(output_dir="data/test")

# 测试单个实验
try:
    result = runner.run_single_experiment(
        model="qwen3:4b",
        prompts=["请解释牛顿第一定律。", "请举出一个实际应用例子。"],
        task_type="qa",
        keep_context=True,
        per_turn_monitoring=True,
        max_tokens=200,
        temperature=0.7
    )
    
    if result:
        print("\n实验成功!")
        print(f"对话轮数: {result['performance']['turns']}")
        print(f"总时间: {result['performance']['total_time_seconds']:.2f}秒")
    else:
        print("\n实验失败!")
        
except Exception as e:
    print(f"\n发生错误: {e}")
    import traceback
    traceback.print_exc()
