"""
测试所有5个问题的测试用例提取

验证code_executor能够从所有问题中提取测试用例
"""

import sys
import pandas as pd
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.code_executor import CodeExecutor


def test_all_questions():
    """测试所有5个问题"""
    
    # 读取问题
    prompts_file = Path(__file__).parent.parent / 'pre_data' / 'comparison_matrices' / 'code' / 'code_prompts.csv'
    df = pd.read_csv(prompts_file, encoding='utf-8-sig')
    
    print("="*80)
    print("测试所有代码问题的测试用例提取")
    print("="*80)
    print(f"\n总问题数: {len(df)}\n")
    
    executor = CodeExecutor()
    
    total_tests = 0
    
    for idx, row in df.iterrows():
        question_id = row['question_id']
        prompt = row['prompt']
        
        # 提取测试用例
        test_cases = executor.extract_test_cases(prompt)
        
        print(f"问题 {question_id}:")
        print(f"  提取的测试数: {len(test_cases)}")
        
        if test_cases:
            print(f"  测试用例示例:")
            for i, test in enumerate(test_cases[:2], 1):  # 只显示前2个
                print(f"    {i}. {test}")
            if len(test_cases) > 2:
                print(f"    ... (还有 {len(test_cases) - 2} 个)")
        else:
            print(f"  ⚠️  未提取到测试用例")
        
        print()
        total_tests += len(test_cases)
    
    print("="*80)
    print(f"总计提取测试用例: {total_tests}")
    print(f"平均每题测试数: {total_tests / len(df):.1f}")
    print("="*80)
    
    # 统计
    questions_with_tests = sum(1 for _, row in df.iterrows() 
                               if len(executor.extract_test_cases(row['prompt'])) > 0)
    
    print(f"\n✅ 有测试用例的问题: {questions_with_tests}/{len(df)} ({questions_with_tests/len(df)*100:.0f}%)")
    
    if questions_with_tests == len(df):
        print("🎉 所有问题都成功提取到测试用例!")
    else:
        print(f"⚠️  有 {len(df) - questions_with_tests} 个问题未提取到测试用例")


if __name__ == '__main__':
    test_all_questions()
