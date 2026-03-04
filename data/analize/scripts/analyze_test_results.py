"""
分析代码测试结果

查看测试通过率统计
"""

import pandas as pd
import sys

def main():
    # 读取数据
    df = pd.read_csv('data/analize/pre_data/quality_scores_code.csv', encoding='utf-8-sig')
    
    print("="*80)
    print("代码测试结果分析")
    print("="*80)
    
    # 基本统计
    print(f"\n总样本数: {len(df)}")
    print(f"包含测试用例的样本: {df['test_pass_rate'].notna().sum()}")
    print(f"测试覆盖率: {df['test_pass_rate'].notna().sum() / len(df):.1%}")
    
    # 测试通过率统计
    has_tests = df[df['test_pass_rate'].notna()]
    if len(has_tests) > 0:
        print(f"\n整体测试通过率: {has_tests['test_pass_rate'].mean():.1%}")
        print(f"测试通过率中位数: {has_tests['test_pass_rate'].median():.1%}")
        print(f"完全通过的样本: {(has_tests['test_pass_rate'] == 1.0).sum()}/{len(has_tests)} ({(has_tests['test_pass_rate'] == 1.0).sum() / len(has_tests):.1%})")
        print(f"完全失败的样本: {(has_tests['test_pass_rate'] == 0.0).sum()}/{len(has_tests)} ({(has_tests['test_pass_rate'] == 0.0).sum() / len(has_tests):.1%})")
    
    # 按模型统计
    print("\n" + "="*80)
    print("按模型统计")
    print("="*80)
    
    model_stats = df.groupby('model').agg({
        'test_pass_rate': ['count', 'mean'],
        'tests_passed': 'sum',
        'tests_total': 'sum',
        'compilation_rate': 'mean'
    }).round(4)
    
    # 重命名列
    model_stats.columns = ['样本数', '平均通过率', '通过测试数', '总测试数', '编译成功率']
    
    # 计算总通过率
    model_stats['总通过率'] = model_stats['通过测试数'] / model_stats['总测试数']
    
    # 排序
    model_stats = model_stats.sort_values('平均通过率', ascending=False)
    
    print(model_stats.to_string())
    
    # Top 5 模型
    print("\n" + "="*80)
    print("Top 5 模型（按测试通过率）")
    print("="*80)
    
    for i, (model, row) in enumerate(model_stats.head(5).iterrows(), 1):
        print(f"{i}. {model:<30}")
        print(f"   平均通过率: {row['平均通过率']:.1%}")
        print(f"   总通过率: {row['总通过率']:.1%} ({int(row['通过测试数'])}/{int(row['总测试数'])})")
        print(f"   编译成功率: {row['编译成功率']:.1%}")
    
    # 编译成功但测试失败的情况
    print("\n" + "="*80)
    print("编译成功但测试失败的样本")
    print("="*80)
    
    compiled_but_failed = df[(df['compilation_rate'] == 1.0) & 
                             (df['test_pass_rate'].notna()) & 
                             (df['test_pass_rate'] < 1.0)]
    
    print(f"数量: {len(compiled_but_failed)}")
    
    if len(compiled_but_failed) > 0:
        print("\n示例:")
        for i, (idx, row) in enumerate(compiled_but_failed.head(3).iterrows(), 1):
            print(f"\n{i}. {row['model']}")
            print(f"   测试通过率: {row['test_pass_rate']:.1%} ({int(row['tests_passed'])}/{int(row['tests_total'])})")
            print(f"   提示词: {row['prompt'][:80]}...")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    main()
