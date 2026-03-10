#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版 plot_pareto_2d 函数

生成示例图表以验证所有优化功能
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from shared_functions import plot_pareto_2d, identify_pareto_frontier_2d


def generate_test_data():
    """生成测试数据"""
    np.random.seed(42)
    
    # 创建11个模型的测试数据
    models = [
        'deepseek_8b', 'gemma_2b_4bit', 'gemma_2b_8bit',
        'gemma_4b', 'phi3_4b_4bit', 'phi3_4b_8bit',
        'qwen25_3b_4bit', 'qwen25_3b_8bit', 'qwen25_7b_4bit',
        'qwen_4b', 'qwen_8b'
    ]
    
    # 生成质量和效率数据（模拟真实分布）
    quality = np.random.uniform(0.6, 0.95, len(models))
    speed = np.random.uniform(10, 100, len(models))  # tokens/s
    energy = np.random.uniform(50, 500, len(models))  # Joules
    
    # 确保有一些明显的帕累托点
    quality[0] = 0.92  # 高质量
    speed[0] = 80
    energy[0] = 100
    
    quality[1] = 0.75  # 高速度
    speed[1] = 95
    energy[1] = 150
    
    quality[2] = 0.85  # 低能耗
    speed[2] = 60
    energy[2] = 60
    
    df = pd.DataFrame({
        'model': models,
        'quality': quality,
        'speed': speed,
        'energy': energy
    })
    
    return df


def test_quality_speed():
    """测试质量-速度图"""
    print("\n" + "="*80)
    print("测试 1: 质量-速度帕累托前沿图")
    print("="*80)
    
    df = generate_test_data()
    
    # 识别帕累托前沿（质量最大化，速度最大化）
    pareto_mask = identify_pareto_frontier_2d(
        df, 
        x_col='speed',
        y_col='quality',
        x_minimize=False,  # 速度越大越好
        y_minimize=False   # 质量越大越好
    )
    
    print(f"数据点数量: {len(df)}")
    print(f"帕累托点数量: {pareto_mask.sum()}")
    print(f"帕累托点: {df[pareto_mask]['model'].tolist()}")
    
    # 绘制图表
    output_path = Path(__file__).parent / 'test_quality_speed.png'
    plot_pareto_2d(
        df=df,
        pareto_mask=pareto_mask,
        x_col='speed',
        y_col='quality',
        title='质量-速度帕累托前沿分析（测试）',
        output_path=output_path,
        x_label='推理速度 (tokens/s)',
        y_label='综合质量得分',
        x_minimize=False,  # 速度越大越好
        y_minimize=False   # 质量越大越好
    )


def test_quality_energy():
    """测试质量-能耗图"""
    print("\n" + "="*80)
    print("测试 2: 质量-能耗帕累托前沿图")
    print("="*80)
    
    df = generate_test_data()
    
    # 识别帕累托前沿（质量最大化，能耗最小化）
    pareto_mask = identify_pareto_frontier_2d(
        df,
        x_col='energy',
        y_col='quality',
        x_minimize=True,   # 能耗越小越好
        y_minimize=False   # 质量越大越好
    )
    
    print(f"数据点数量: {len(df)}")
    print(f"帕累托点数量: {pareto_mask.sum()}")
    print(f"帕累托点: {df[pareto_mask]['model'].tolist()}")
    
    # 绘制图表
    output_path = Path(__file__).parent / 'test_quality_energy.png'
    plot_pareto_2d(
        df=df,
        pareto_mask=pareto_mask,
        x_col='energy',
        y_col='quality',
        title='质量-能耗帕累托前沿分析（测试）',
        output_path=output_path,
        x_label='GPU能耗 (J)',
        y_label='综合质量得分',
        x_minimize=True,   # 能耗越小越好
        y_minimize=False   # 质量越大越好
    )


def main():
    """主测试函数"""
    print("\n" + "="*80)
    print("增强版 plot_pareto_2d 函数测试")
    print("="*80)
    print("\n测试目标:")
    print("  ✓ 渐变色映射")
    print("  ✓ 帕累托前沿连线")
    print("  ✓ 智能标注")
    print("  ✓ 统计信息框")
    print("  ✓ 参考线")
    print("  ✓ 优化方向指示")
    print("  ✓ 专业配色和布局")
    
    try:
        # 运行测试
        test_quality_speed()
        test_quality_energy()
        
        print("\n" + "="*80)
        print("✓ 所有测试完成！")
        print("="*80)
        print("\n生成的测试图表:")
        print("  - test_quality_speed.png")
        print("  - test_quality_energy.png")
        print("\n请查看图表以验证优化效果。")
        
        # 检查 adjustText 是否可用
        try:
            import adjustText
            print("\n✓ adjustText 已安装，标注避让功能已启用")
        except ImportError:
            print("\n⚠️  adjustText 未安装，使用简单标注偏移")
            print("   建议安装: pip install adjustText")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
