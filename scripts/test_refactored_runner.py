#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试重构后的实验运行器
验证新的数据结构（raw + summary分离）
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from experiments.experiment_runner import ExperimentRunner

def test_single_experiment():
    """测试单个实验"""
    print("="*70)
    print("测试1: 单轮对话实验（整体监控）")
    print("="*70)
    
    runner = ExperimentRunner(output_dir="data/test")
    
    # 创建简单的测试用例
    test_case = {
        "model": "ollama:qwen3:4b",
        "prompts": ["什么是Python？请用一句话回答。"],
        "task_type": "qa",
        "max_tokens": 50,
        "temperature": 0.7,
        "idle_measurement_duration": 3
    }
    
    print(f"\n运行测试实验...")
    result = runner.run_single_experiment(
        model=test_case["model"],
        prompts=test_case["prompts"],
        task_type=test_case["task_type"],
        max_tokens=test_case["max_tokens"],
        temperature=test_case["temperature"],
        idle_measurement_duration=test_case["idle_measurement_duration"]
    )
    
    if result:
        print(f"\n✅ 实验成功完成")
        
        # 验证数据结构
        raw_data = result.get_raw_data()
        summary_data = result.get_summary_data()
        
        print(f"\n检查数据结构...")
        print(f"  Raw数据包含的键: {list(raw_data.keys())}")
        print(f"  Summary数据包含的键: {list(summary_data.keys())}")
        
        # 验证raw数据
        assert "experiment_id" in raw_data
        assert "config" in raw_data
        assert "baseline_raw" in raw_data
        assert "conversation" in raw_data
        assert "monitoring_data" in raw_data
        print(f"  ✓ Raw数据结构正确")
        
        # 验证summary数据
        assert "experiment_id" in summary_data
        assert "config_ref" in summary_data
        assert "baseline_summary" in summary_data
        assert "performance" in summary_data
        assert "resources" in summary_data
        assert "derived_metrics" in summary_data
        assert "quality" in summary_data
        assert "conversation_summary" in summary_data
        print(f"  ✓ Summary数据结构正确")
        
        # 保存测试结果
        output_dir = Path("data/test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        raw_file = output_dir / "test_refactored_raw.json"
        summary_file = output_dir / "test_refactored_summary.json"
        
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存:")
        print(f"  Raw: {raw_file}")
        print(f"  Summary: {summary_file}")
        
        return True
    else:
        print(f"\n❌ 实验失败")
        return False

def test_multi_turn_experiment():
    """测试多轮对话实验（分轮监控）"""
    print("\n" + "="*70)
    print("测试2: 多轮对话实验（分轮监控）")
    print("="*70)
    
    runner = ExperimentRunner(output_dir="data/test")
    
    # 创建多轮对话测试用例
    test_case = {
        "model": "ollama:qwen3:4b",
        "prompts": [
            "什么是机器学习？",
            "它有哪些应用？"
        ],
        "task_type": "qa",
        "max_tokens": 50,
        "temperature": 0.7,
        "keep_context": True,
        "per_turn_monitoring": True,
        "idle_measurement_duration": 3
    }
    
    print(f"\n运行多轮对话实验...")
    result = runner.run_single_experiment(
        model=test_case["model"],
        prompts=test_case["prompts"],
        task_type=test_case["task_type"],
        max_tokens=test_case["max_tokens"],
        temperature=test_case["temperature"],
        keep_context=test_case["keep_context"],
        per_turn_monitoring=test_case["per_turn_monitoring"],
        idle_measurement_duration=test_case["idle_measurement_duration"]
    )
    
    if result:
        print(f"\n✅ 多轮对话实验成功完成")
        
        # 验证分轮监控数据
        raw_data = result.get_raw_data()
        summary_data = result.get_summary_data()
        
        print(f"\n检查分轮监控数据...")
        print(f"  对话轮数: {len(raw_data['conversation'])}")
        
        # 检查每轮是否有独立的监控数据
        for turn in raw_data['conversation']:
            if 'monitoring_data' in turn:
                print(f"  ✓ 轮次 {turn['turn']} 有独立监控数据")
            else:
                print(f"  ⚠ 轮次 {turn['turn']} 没有独立监控数据")
        
        # 检查conversation_summary
        print(f"\n  Conversation Summary包含 {len(summary_data['conversation_summary'])} 轮")
        for turn_summary in summary_data['conversation_summary']:
            print(f"    轮次 {turn_summary['turn']}: {turn_summary.get('tokens', 'N/A')} tokens")
        
        # 保存测试结果
        output_dir = Path("data/test")
        raw_file = output_dir / "test_multi_turn_raw.json"
        summary_file = output_dir / "test_multi_turn_summary.json"
        
        with open(raw_file, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=2)
        
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试结果已保存:")
        print(f"  Raw: {raw_file}")
        print(f"  Summary: {summary_file}")
        
        return True
    else:
        print(f"\n❌ 多轮对话实验失败")
        return False

def test_experiment_suite():
    """测试实验套件"""
    print("\n" + "="*70)
    print("测试3: 实验套件（多个实验）")
    print("="*70)
    
    runner = ExperimentRunner(output_dir="data/test")
    
    # 创建测试套件
    test_cases = [
        {
            "model": "ollama:qwen3:4b",
            "prompts": ["什么是深度学习？"],
            "task_type": "qa",
            "max_tokens": 30,
            "temperature": 0.7,
            "idle_measurement_duration": 2
        },
        {
            "model": "ollama:qwen3:4b",
            "prompts": ["解释神经网络。"],
            "task_type": "qa",
            "max_tokens": 30,
            "temperature": 0.7,
            "idle_measurement_duration": 0  # 第二个实验不测量基线
        }
    ]
    
    print(f"\n运行实验套件（{len(test_cases)}个实验）...")
    raw_results, summary_results = runner.run_experiment_suite(
        test_cases,
        output_file="data/test/test_suite"
    )
    
    if raw_results and summary_results:
        print(f"\n✅ 实验套件成功完成")
        print(f"  Raw结果数: {len(raw_results)}")
        print(f"  Summary结果数: {len(summary_results)}")
        
        # 验证文件是否存在
        raw_file = Path("data/test/test_suite_raw.json")
        summary_file = Path("data/test/test_suite_summary.json")
        
        if raw_file.exists() and summary_file.exists():
            print(f"  ✓ 输出文件已创建")
            print(f"    Raw: {raw_file}")
            print(f"    Summary: {summary_file}")
            return True
        else:
            print(f"  ❌ 输出文件未创建")
            return False
    else:
        print(f"\n❌ 实验套件失败")
        return False

def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("开始测试重构后的实验运行器")
    print("="*70)
    
    results = []
    
    # 测试1: 单轮对话
    try:
        result1 = test_single_experiment()
        results.append(("单轮对话实验", result1))
    except Exception as e:
        print(f"\n❌ 测试1失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("单轮对话实验", False))
    
    # 测试2: 多轮对话（分轮监控）
    try:
        result2 = test_multi_turn_experiment()
        results.append(("多轮对话实验", result2))
    except Exception as e:
        print(f"\n❌ 测试2失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("多轮对话实验", False))
    
    # 测试3: 实验套件
    try:
        result3 = test_experiment_suite()
        results.append(("实验套件", result3))
    except Exception as e:
        print(f"\n❌ 测试3失败: {e}")
        import traceback
        traceback.print_exc()
        results.append(("实验套件", False))
    
    # 汇总结果
    print("\n" + "="*70)
    print("测试结果汇总")
    print("="*70)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！数据结构重构成功！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
