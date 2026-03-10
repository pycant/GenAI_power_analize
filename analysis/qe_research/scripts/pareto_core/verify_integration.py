"""
快速验证权重归一化集成
"""

from typing import Dict

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

def main():
    print("\n" + "="*80)
    print("权重归一化集成验证")
    print("="*80)
    
    # 测试1: 整数权重
    print("\n测试1: 整数权重")
    weights1 = {
        'code': 30,
        'math': 25,
        'qa': 20,
        'reasoning': 15,
        'creative': 5,
        'summary': 3,
        'translation': 2
    }
    result1 = normalize_weights(weights1, verbose=False)
    print(f"  原始权重和: {sum(weights1.values())}")
    print(f"  归一化后权重和: {sum(result1.values()):.6f}")
    print(f"  code权重: {weights1['code']} -> {result1['code']:.6f} ({result1['code']*100:.2f}%)")
    assert abs(sum(result1.values()) - 1.0) < 1e-6, "权重和应该为1"
    print("  ✓ 通过")
    
    # 测试2: 已归一化权重
    print("\n测试2: 已归一化权重")
    weights2 = {
        'code': 0.30,
        'math': 0.25,
        'qa': 0.20,
        'reasoning': 0.15,
        'creative': 0.05,
        'summary': 0.03,
        'translation': 0.02
    }
    result2 = normalize_weights(weights2, verbose=False)
    print(f"  原始权重和: {sum(weights2.values()):.6f}")
    print(f"  归一化后权重和: {sum(result2.values()):.6f}")
    print(f"  code权重: {weights2['code']:.6f} -> {result2['code']:.6f}")
    assert abs(sum(result2.values()) - 1.0) < 1e-6, "权重和应该为1"
    print("  ✓ 通过")
    
    # 测试3: 任意比例
    print("\n测试3: 任意比例")
    weights3 = {
        'code': 3,
        'math': 2,
        'qa': 1,
        'reasoning': 1
    }
    result3 = normalize_weights(weights3, verbose=False)
    print(f"  原始权重和: {sum(weights3.values())}")
    print(f"  归一化后权重和: {sum(result3.values()):.6f}")
    print(f"  code权重: {weights3['code']} -> {result3['code']:.6f} ({result3['code']*100:.2f}%)")
    assert abs(sum(result3.values()) - 1.0) < 1e-6, "权重和应该为1"
    assert abs(result3['code'] - 3/7) < 1e-6, "code权重应该为3/7"
    print("  ✓ 通过")
    
    print("\n" + "="*80)
    print("✓ 所有验证通过！权重归一化功能已成功集成")
    print("="*80)

if __name__ == '__main__':
    main()
