"""
测试权重归一化功能

验证 normalize_weights() 函数的正确性
"""

import sys
from pathlib import Path
from typing import Dict

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接定义 normalize_weights 函数（从 pareto_mixed_task.py 复制）
def normalize_weights(weights: Dict[str, float], verbose: bool = True) -> Dict[str, float]:
    """
    归一化权重，使其和为1
    
    Args:
        weights: 原始权重字典
        verbose: 是否输出详细信息
    
    Returns:
        Dict[str, float]: 归一化后的权重字典
    """
    total = sum(weights.values())
    
    if verbose:
        print(f"\n权重归一化:")
        print(f"  原始权重和: {total:.6f}")
    
    if abs(total - 1.0) < 1e-6:
        if verbose:
            print(f"  权重已归一化，无需调整")
        return weights.copy()
    
    # 归一化
    normalized = {task: weight / total for task, weight in weights.items()}
    
    if verbose:
        print(f"  归一化后权重和: {sum(normalized.values()):.6f}")
        print(f"\n权重调整:")
        for task in weights.keys():
            print(f"    {task}: {weights[task]:.6f} -> {normalized[task]:.6f} ({normalized[task]*100:.2f}%)")
    
    return normalized


def test_already_normalized():
    """测试已归一化的权重"""
    print("\n" + "="*80)
    print("测试1: 已归一化的权重（和为1）")
    print("="*80)
    
    weights = {
        'code': 0.30,
        'math': 0.25,
        'qa': 0.20,
        'reasoning': 0.15,
        'creative': 0.05,
        'summary': 0.03,
        'translation': 0.02
    }
    
    print(f"原始权重和: {sum(weights.values()):.6f}")
    
    normalized = normalize_weights(weights, verbose=True)
    
    print(f"\n验证:")
    print(f"  归一化后权重和: {sum(normalized.values()):.6f}")
    print(f"  是否等于1: {abs(sum(normalized.values()) - 1.0) < 1e-6}")
    
    assert abs(sum(normalized.values()) - 1.0) < 1e-6, "权重和应该为1"
    print(f"  ✓ 测试通过")


def test_integer_weights():
    """测试整数权重"""
    print("\n" + "="*80)
    print("测试2: 整数权重（和为100）")
    print("="*80)
    
    weights = {
        'code': 30,
        'math': 25,
        'qa': 20,
        'reasoning': 15,
        'creative': 5,
        'summary': 3,
        'translation': 2
    }
    
    print(f"原始权重和: {sum(weights.values()):.6f}")
    
    normalized = normalize_weights(weights, verbose=True)
    
    print(f"\n验证:")
    print(f"  归一化后权重和: {sum(normalized.values()):.6f}")
    print(f"  是否等于1: {abs(sum(normalized.values()) - 1.0) < 1e-6}")
    print(f"  code权重是否为30%: {abs(normalized['code'] - 0.30) < 1e-6}")
    
    assert abs(sum(normalized.values()) - 1.0) < 1e-6, "权重和应该为1"
    assert abs(normalized['code'] - 0.30) < 1e-6, "code权重应该为30%"
    print(f"  ✓ 测试通过")


def test_slight_deviation():
    """测试权重和略有偏差的情况"""
    print("\n" + "="*80)
    print("测试3: 权重和略有偏差（和为1.01）")
    print("="*80)
    
    weights = {
        'code': 0.30,
        'math': 0.25,
        'qa': 0.20,
        'reasoning': 0.15,
        'creative': 0.05,
        'summary': 0.03,
        'translation': 0.03  # 总和 = 1.01
    }
    
    print(f"原始权重和: {sum(weights.values()):.6f}")
    
    normalized = normalize_weights(weights, verbose=True)
    
    print(f"\n验证:")
    print(f"  归一化后权重和: {sum(normalized.values()):.6f}")
    print(f"  是否等于1: {abs(sum(normalized.values()) - 1.0) < 1e-6}")
    
    assert abs(sum(normalized.values()) - 1.0) < 1e-6, "权重和应该为1"
    print(f"  ✓ 测试通过")


def test_percentage_weights():
    """测试百分比权重"""
    print("\n" + "="*80)
    print("测试4: 百分比权重（和为100%）")
    print("="*80)
    
    weights = {
        'code': 30.0,
        'math': 25.0,
        'qa': 20.0,
        'reasoning': 15.0,
        'creative': 5.0,
        'summary': 3.0,
        'translation': 2.0
    }
    
    print(f"原始权重和: {sum(weights.values()):.6f}")
    
    normalized = normalize_weights(weights, verbose=True)
    
    print(f"\n验证:")
    print(f"  归一化后权重和: {sum(normalized.values()):.6f}")
    print(f"  是否等于1: {abs(sum(normalized.values()) - 1.0) < 1e-6}")
    
    assert abs(sum(normalized.values()) - 1.0) < 1e-6, "权重和应该为1"
    print(f"  ✓ 测试通过")


def test_arbitrary_weights():
    """测试任意权重"""
    print("\n" + "="*80)
    print("测试5: 任意权重（和为7）")
    print("="*80)
    
    weights = {
        'code': 3,
        'math': 2,
        'qa': 1,
        'reasoning': 1
    }
    
    print(f"原始权重和: {sum(weights.values()):.6f}")
    
    normalized = normalize_weights(weights, verbose=True)
    
    print(f"\n验证:")
    print(f"  归一化后权重和: {sum(normalized.values()):.6f}")
    print(f"  是否等于1: {abs(sum(normalized.values()) - 1.0) < 1e-6}")
    print(f"  code权重是否为3/7: {abs(normalized['code'] - 3/7) < 1e-6}")
    
    assert abs(sum(normalized.values()) - 1.0) < 1e-6, "权重和应该为1"
    assert abs(normalized['code'] - 3/7) < 1e-6, "code权重应该为3/7"
    print(f"  ✓ 测试通过")


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("权重归一化功能测试")
    print("="*80)
    
    try:
        test_already_normalized()
        test_integer_weights()
        test_slight_deviation()
        test_percentage_weights()
        test_arbitrary_weights()
        
        print("\n" + "="*80)
        print("所有测试通过！✓")
        print("="*80)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    except Exception as e:
        print(f"\n✗ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
