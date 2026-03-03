#!/usr/bin/env python3
"""
修正测试用例中的 temperature=0.0 问题
将 temperature=0.0 改为 0.1（HuggingFace 要求 temperature > 0）
"""

import json
from pathlib import Path

def fix_temperature(filepath):
    """修正测试用例中的 temperature=0.0"""
    print(f"处理文件: {filepath}")
    
    # 读取测试用例
    with open(filepath, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    # 统计
    fixed_count = 0
    
    # 修正 temperature=0.0
    for test_case in test_cases:
        if test_case.get('temperature') == 0.0:
            test_case['temperature'] = 0.1
            fixed_count += 1
    
    # 保存
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(test_cases, f, indent=2, ensure_ascii=False)
    
    print(f"✓ 修正了 {fixed_count} 个测试用例")
    print(f"✓ 总测试用例数: {len(test_cases)}")
    
    return fixed_count


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="修正 temperature=0.0 问题")
    parser.add_argument(
        "--file",
        default="data/experiments_5/test_cases.json",
        help="测试用例文件路径"
    )
    
    args = parser.parse_args()
    
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"❌ 文件不存在: {filepath}")
        return 1
    
    fixed_count = fix_temperature(filepath)
    
    print(f"\n✅ 完成！修正了 {fixed_count} 个测试用例")
    return 0


if __name__ == "__main__":
    exit(main())
