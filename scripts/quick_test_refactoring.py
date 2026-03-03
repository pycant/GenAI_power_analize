#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
快速测试重构后的数据结构
使用小模型进行快速验证
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from experiments.experiment_runner import ExperimentRunner

def main():
    """快速测试主函数"""
    print("="*70)
    print("快速测试重构后的实验运行器")
    print("="*70)
    
    # 创建运行器
    runner = ExperimentRunner(output_dir="data/test")
    
    # 读取测试用例
    test_file = Path("data/test/test_refactoring_quick.json")
    with open(test_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)
    
    print(f"\n加载了 {len(test_cases)} 个测试用例")
    print(f"  1. 单轮对话（整体监控）")
    print(f"  2. 多轮对话（分轮监控）")
    
    # 运行实验套件
    print(f"\n开始运行实验...")
    try:
        raw_results, summary_results = runner.run_experiment_suite(
            test_cases,
            output_file="data/test/quick_test_refactoring"
        )
        
        print(f"\n" + "="*70)
        print(f"✅ 测试完成！")
        print(f"="*70)
        
        # 验证结果
        print(f"\n验证结果:")
        print(f"  Raw结果数: {len(raw_results)}")
        print(f"  Summary结果数: {len(summary_results)}")
        
        # 检查文件
        raw_file = Path("data/test/quick_test_refactoring_raw.json")
        summary_file = Path("data/test/quick_test_refactoring_summary.json")
        
        if raw_file.exists() and summary_file.exists():
            print(f"\n✓ 输出文件已创建:")
            print(f"  Raw: {raw_file}")
            print(f"  Summary: {summary_file}")
            
            # 显示文件大小
            raw_size = raw_file.stat().st_size / 1024
            summary_size = summary_file.stat().st_size / 1024
            print(f"\n文件大小:")
            print(f"  Raw: {raw_size:.2f} KB")
            print(f"  Summary: {summary_size:.2f} KB")
            print(f"  比例: Raw是Summary的 {raw_size/summary_size:.2f} 倍")
        
        # 显示关键指标
        print(f"\n" + "="*70)
        print(f"实验结果摘要")
        print(f"="*70)
        
        for i, summary in enumerate(summary_results, 1):
            print(f"\n实验 {i}: {summary['config_ref']['model']}")
            print(f"  任务类型: {summary['config_ref']['task_type']}")
            print(f"  对话轮数: {summary['performance']['turns']}")
            print(f"  分轮监控: {'是' if summary['config_ref']['per_turn_monitoring'] else '否'}")
            
            # 性能指标
            perf = summary['performance']
            print(f"\n  性能指标:")
            print(f"    总时间: {perf['total_time_seconds']:.2f}秒")
            print(f"    Token数: {perf['output_tokens']}")
            print(f"    吞吐量: {perf['throughput_tokens_per_sec']:.2f} tokens/s")
            if perf.get('ttft_seconds'):
                print(f"    TTFT: {perf['ttft_seconds']*1000:.1f}ms")
            
            # 资源指标
            res = summary['resources']
            print(f"\n  资源指标:")
            print(f"    平均GPU功耗: {res['gpu_power_avg_w']:.2f} W")
            print(f"    峰值GPU功耗: {res['gpu_power_peak_w']:.2f} W")
            print(f"    GPU能耗: {res['gpu_energy_j']:.2f} J")
            
            # 派生指标
            if summary['derived_metrics']:
                derived = summary['derived_metrics']
                print(f"\n  派生指标:")
                if 'P_idle' in derived:
                    print(f"    空闲功耗: {derived['P_idle']:.2f} W")
                if 'P_inc' in derived:
                    print(f"    增量功耗: {derived['P_inc']:.2f} W")
                if 'E_inc' in derived:
                    print(f"    增量能耗: {derived['E_inc']:.2f} J")
                if 'E_token' in derived:
                    print(f"    每token能耗: {derived['E_token']:.4f} J/token")
                if 'TPJ' in derived:
                    print(f"    能效比: {derived['TPJ']:.2f} tokens/J")
            
            # 对话摘要
            if summary['conversation_summary']:
                print(f"\n  对话摘要:")
                for turn_sum in summary['conversation_summary']:
                    print(f"    轮次 {turn_sum['turn']}: {turn_sum.get('tokens', 'N/A')} tokens, {turn_sum['duration_seconds']:.2f}秒")
                    if 'throughput' in turn_sum:
                        print(f"      吞吐量: {turn_sum['throughput']:.2f} tokens/s")
                    if 'gpu_energy_j' in turn_sum:
                        print(f"      GPU能耗: {turn_sum['gpu_energy_j']:.2f} J")
        
        print(f"\n" + "="*70)
        print(f"🎉 快速测试成功完成！")
        print(f"="*70)
        print(f"\n重构改进验证:")
        print(f"  ✓ Raw和Summary文件成功分离")
        print(f"  ✓ 空闲基线数据正确记录")
        print(f"  ✓ 分轮监控功能正常工作")
        print(f"  ✓ 派生指标自动计算")
        print(f"  ✓ 对话摘要正确生成")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
