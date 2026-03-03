#!/usr/bin/env python3
"""
验证测试用例格式是否符合 EXPERIMENT_RUNNER_GUIDE.md 规范
"""

import json
from pathlib import Path
from collections import Counter

def verify_test_cases(filepath):
    """验证测试用例格式"""
    print("="*70)
    print("测试用例格式验证")
    print("="*70)
    
    # 加载测试用例
    with open(filepath, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"\n文件: {filepath}")
    print(f"总测试用例数: {len(test_cases)}")
    
    # 统计信息
    models = Counter()
    task_types = Counter()
    errors = []
    warnings = []
    
    # 必需字段
    required_fields = ['model', 'prompts', 'task_type']
    
    # 可选字段
    optional_fields = [
        'max_tokens', 'temperature', 'top_p', 
        'idle_measurement_duration', 'reference_text',
        'keep_context', 'per_turn_monitoring'
    ]
    
    print("\n检查测试用例格式...")
    
    for i, test_case in enumerate(test_cases):
        # 检查必需字段
        for field in required_fields:
            if field not in test_case:
                errors.append(f"测试用例 {i}: 缺少必需字段 '{field}'")
        
        # 统计
        if 'model' in test_case:
            models[test_case['model']] += 1
        if 'task_type' in test_case:
            task_types[test_case['task_type']] += 1
        
        # 检查 prompts 格式
        if 'prompts' in test_case:
            prompts = test_case['prompts']
            if not isinstance(prompts, (str, list)):
                errors.append(f"测试用例 {i}: 'prompts' 必须是字符串或数组")
            elif isinstance(prompts, list):
                if not all(isinstance(p, str) for p in prompts):
                    errors.append(f"测试用例 {i}: 'prompts' 数组中的所有元素必须是字符串")
                # 多轮对话应该有 keep_context
                if len(prompts) > 1 and not test_case.get('keep_context'):
                    warnings.append(f"测试用例 {i}: 多轮对话建议设置 'keep_context': true")
        
        # 检查 model 格式
        if 'model' in test_case:
            model = test_case['model']
            if not isinstance(model, str):
                errors.append(f"测试用例 {i}: 'model' 必须是字符串")
            elif model == "all":
                errors.append(f"测试用例 {i}: 'model' 不应该是 'all'，应该是具体的模型名称")
        
        # 检查数值字段
        if 'max_tokens' in test_case and not isinstance(test_case['max_tokens'], int):
            errors.append(f"测试用例 {i}: 'max_tokens' 必须是整数")
        
        if 'temperature' in test_case:
            temp = test_case['temperature']
            if not isinstance(temp, (int, float)):
                errors.append(f"测试用例 {i}: 'temperature' 必须是数字")
            elif temp < 0 or temp > 2:
                warnings.append(f"测试用例 {i}: 'temperature' 通常在 0-2 之间")
        
        if 'top_p' in test_case:
            top_p = test_case['top_p']
            if not isinstance(top_p, (int, float)):
                errors.append(f"测试用例 {i}: 'top_p' 必须是数字")
            elif top_p < 0 or top_p > 1:
                errors.append(f"测试用例 {i}: 'top_p' 必须在 0-1 之间")
    
    # 打印统计信息
    print("\n" + "="*70)
    print("统计信息")
    print("="*70)
    
    print(f"\n模型分布:")
    for model, count in sorted(models.items()):
        print(f"  {model}: {count} 个测试用例")
    
    print(f"\n任务类型分布:")
    for task_type, count in sorted(task_types.items()):
        print(f"  {task_type}: {count} 个测试用例")
    
    # 打印错误和警告
    print("\n" + "="*70)
    print("验证结果")
    print("="*70)
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for error in errors[:10]:  # 只显示前10个
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... 还有 {len(errors) - 10} 个错误")
    else:
        print("\n✅ 没有发现错误")
    
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for warning in warnings[:10]:  # 只显示前10个
            print(f"  - {warning}")
        if len(warnings) > 10:
            print(f"  ... 还有 {len(warnings) - 10} 个警告")
    else:
        print("\n✅ 没有发现警告")
    
    # 检查示例
    print("\n" + "="*70)
    print("示例测试用例")
    print("="*70)
    
    # 显示每种任务类型的一个示例
    shown_types = set()
    for test_case in test_cases:
        task_type = test_case.get('task_type')
        if task_type and task_type not in shown_types:
            print(f"\n{task_type.upper()} 示例:")
            # 只显示关键字段
            example = {
                'model': test_case.get('model'),
                'task_type': task_type,
                'prompts': test_case.get('prompts')[:100] + '...' if isinstance(test_case.get('prompts'), str) and len(test_case.get('prompts', '')) > 100 else test_case.get('prompts'),
                'has_reference_text': 'reference_text' in test_case,
                'keep_context': test_case.get('keep_context'),
            }
            print(json.dumps(example, indent=2, ensure_ascii=False))
            shown_types.add(task_type)
            if len(shown_types) >= 3:  # 只显示3个示例
                break
    
    print("\n" + "="*70)
    
    return len(errors) == 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="验证测试用例格式")
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
    
    success = verify_test_cases(filepath)
    
    if success:
        print("\n✅ 所有测试用例格式正确！")
        return 0
    else:
        print("\n❌ 发现格式错误，请修正后重试。")
        return 1


if __name__ == "__main__":
    exit(main())
