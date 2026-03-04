"""
代码评分结果分析

分析当前代码质量评估的结果，发现问题并提供改进建议
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def load_data():
    """加载评分数据"""
    data_file = Path(__file__).parent.parent / 'pre_data' / 'quality_scores_code.csv'
    df = pd.read_csv(data_file, encoding='utf-8-sig')
    return df


def analyze_compilation_vs_tests(df):
    """分析编译成功率 vs 测试通过率"""
    print("="*80)
    print("📊 编译成功率 vs 测试通过率分析")
    print("="*80)
    
    # 按模型聚合
    model_stats = df.groupby('model').agg({
        'compilation_rate': 'mean',
        'test_pass_rate': 'mean',
        'tests_passed': 'sum',
        'tests_total': 'sum'
    }).round(3)
    
    # 计算差距
    model_stats['gap'] = model_stats['compilation_rate'] - model_stats['test_pass_rate']
    model_stats = model_stats.sort_values('test_pass_rate', ascending=False)
    
    print("\n模型表现对比:")
    print(model_stats.to_string())
    
    # 整体统计
    print(f"\n整体统计:")
    print(f"  平均编译成功率: {df['compilation_rate'].mean():.1%}")
    print(f"  平均测试通过率: {df['test_pass_rate'].mean():.1%}")
    print(f"  差距: {(df['compilation_rate'].mean() - df['test_pass_rate'].mean()):.1%}")
    
    # 关键发现
    print(f"\n🔍 关键发现:")
    print(f"  1. 编译成功但测试失败的样本: {((df['compilation_rate'] == 1) & (df['test_pass_rate'] < 1)).sum()}")
    print(f"  2. 编译成功但测试全失败: {((df['compilation_rate'] == 1) & (df['test_pass_rate'] == 0)).sum()}")
    print(f"  3. 这说明: 编译成功 ≠ 功能正确")
    
    return model_stats


def analyze_score_distribution(df):
    """分析各指标的分布"""
    print("\n" + "="*80)
    print("📈 指标分布分析")
    print("="*80)
    
    metrics = ['compilation_rate', 'test_pass_rate', 'code_length', 'cyclomatic_complexity']
    
    for metric in metrics:
        if metric in df.columns:
            print(f"\n{metric}:")
            print(f"  均值: {df[metric].mean():.2f}")
            print(f"  中位数: {df[metric].median():.2f}")
            print(f"  标准差: {df[metric].std():.2f}")
            print(f"  范围: [{df[metric].min():.2f}, {df[metric].max():.2f}]")


def analyze_length_complexity_correlation(df):
    """分析代码长度和复杂度的关系"""
    print("\n" + "="*80)
    print("🔗 代码长度 vs 复杂度相关性")
    print("="*80)
    
    # 计算相关系数
    corr = df[['code_length', 'cyclomatic_complexity']].corr().iloc[0, 1]
    print(f"\n相关系数: {corr:.3f}")
    
    if corr > 0.7:
        print("  → 强正相关：代码越长，复杂度越高")
    elif corr > 0.3:
        print("  → 中等正相关：代码长度和复杂度有一定关系")
    else:
        print("  → 弱相关：代码长度和复杂度关系不大")
    
    # 按长度分组分析
    df['length_group'] = pd.cut(df['code_length'], bins=[0, 5, 15, 50, 100], 
                                 labels=['很短(≤5)', '短(6-15)', '中(16-50)', '长(>50)'])
    
    print("\n按代码长度分组的测试通过率:")
    length_analysis = df.groupby('length_group').agg({
        'test_pass_rate': 'mean',
        'compilation_rate': 'mean',
        'cyclomatic_complexity': 'mean'
    }).round(3)
    print(length_analysis.to_string())


def identify_scoring_issues(df):
    """识别当前评分体系的问题"""
    print("\n" + "="*80)
    print("⚠️  当前评分体系的问题")
    print("="*80)
    
    issues = []
    
    # 问题1: 编译成功但测试失败
    compile_ok_test_fail = df[(df['compilation_rate'] == 1) & (df['test_pass_rate'] == 0)]
    if len(compile_ok_test_fail) > 0:
        issues.append({
            'issue': '编译成功但测试全失败',
            'count': len(compile_ok_test_fail),
            'percentage': len(compile_ok_test_fail) / len(df) * 100,
            'severity': 'HIGH',
            'recommendation': '测试通过率应该比编译成功率权重更高'
        })
    
    # 问题2: 代码长度范围假设不合理
    very_short = (df['code_length'] < 10).sum()
    very_long = (df['code_length'] > 50).sum()
    if very_short + very_long > len(df) * 0.5:
        issues.append({
            'issue': '大量代码不在"合理范围"(10-50行)',
            'count': very_short + very_long,
            'percentage': (very_short + very_long) / len(df) * 100,
            'severity': 'MEDIUM',
            'recommendation': '不应假设固定的"合理范围"，应基于数据统计'
        })
    
    # 问题3: 复杂度范围假设不合理
    high_complexity = (df['cyclomatic_complexity'] > 10).sum()
    if high_complexity > len(df) * 0.2:
        issues.append({
            'issue': '大量代码复杂度超过"合理范围"(1-10)',
            'count': high_complexity,
            'percentage': high_complexity / len(df) * 100,
            'severity': 'MEDIUM',
            'recommendation': '复杂度阈值应该基于任务难度动态调整'
        })
    
    # 问题4: 权重设置缺乏依据
    issues.append({
        'issue': '权重设置(60-20-20)缺乏科学依据',
        'count': None,
        'percentage': None,
        'severity': 'HIGH',
        'recommendation': '应该基于指标重要性和数据分析确定权重'
    })
    
    # 打印问题
    for i, issue in enumerate(issues, 1):
        print(f"\n问题 {i}: {issue['issue']}")
        print(f"  严重程度: {issue['severity']}")
        if issue['count'] is not None:
            print(f"  影响样本: {issue['count']} ({issue['percentage']:.1f}%)")
        print(f"  建议: {issue['recommendation']}")
    
    return issues


def suggest_improvements(df, model_stats):
    """提出改进建议"""
    print("\n" + "="*80)
    print("💡 改进建议")
    print("="*80)
    
    print("\n1. 调整指标权重")
    print("   当前: 编译60% + 长度20% + 复杂度20%")
    print("   建议: 测试通过率70% + 编译30% (功能正确性优先)")
    print("   或者: 保留多维度指标，不强制聚合")
    
    print("\n2. 改进归一化方法")
    print("   当前: 假设固定的'合理范围'")
    print("   建议: 基于数据分位数动态确定范围")
    print(f"   - 代码长度 P25-P75: {df['code_length'].quantile(0.25):.0f}-{df['code_length'].quantile(0.75):.0f} 行")
    print(f"   - 复杂度 P25-P75: {df['cyclomatic_complexity'].quantile(0.25):.0f}-{df['cyclomatic_complexity'].quantile(0.75):.0f}")
    
    print("\n3. 增加新指标")
    print("   - 时间复杂度评估（静态分析）")
    print("   - 空间复杂度评估")
    print("   - 代码可读性评分（变量命名、注释）")
    print("   - 边界用例处理")
    
    print("\n4. 分层评估")
    print("   Level 0: 无代码 → 0分")
    print("   Level 1: 编译失败 → 0.1分")
    print("   Level 2: 编译成功但测试失败 → 0.3-0.5分")
    print("   Level 3: 部分测试通过 → 0.5-0.8分")
    print("   Level 4: 全部测试通过 → 0.8-1.0分")
    
    print("\n5. 提供多种评分方案")
    print("   - 方案A: 功能优先（适合生产环境）")
    print("   - 方案B: 效率优先（适合性能敏感场景）")
    print("   - 方案C: 质量优先（适合代码审查）")
    print("   - 方案D: 多维度独立（适合研究分析）")


def create_visualizations(df, model_stats, output_dir):
    """创建可视化图表"""
    print("\n" + "="*80)
    print("📊 生成可视化图表")
    print("="*80)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 图1: 编译率 vs 测试通过率
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(model_stats))
    width = 0.35
    
    ax.bar(x - width/2, model_stats['compilation_rate'], width, 
           label='编译成功率', alpha=0.8)
    ax.bar(x + width/2, model_stats['test_pass_rate'], width, 
           label='测试通过率', alpha=0.8)
    
    ax.set_xlabel('模型')
    ax.set_ylabel('成功率')
    ax.set_title('编译成功率 vs 测试通过率对比')
    ax.set_xticks(x)
    ax.set_xticklabels(model_stats.index, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(output_dir / 'compilation_vs_test_rate.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir / 'compilation_vs_test_rate.png'}")
    plt.close()
    
    # 图2: 代码长度 vs 测试通过率散点图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        ax.scatter(model_df['code_length'], model_df['test_pass_rate'], 
                  label=model, alpha=0.6, s=100)
    
    ax.set_xlabel('代码长度（行）')
    ax.set_ylabel('测试通过率')
    ax.set_title('代码长度 vs 测试通过率')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(output_dir / 'length_vs_test_rate.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir / 'length_vs_test_rate.png'}")
    plt.close()
    
    # 图3: 复杂度 vs 测试通过率散点图
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        ax.scatter(model_df['cyclomatic_complexity'], model_df['test_pass_rate'], 
                  label=model, alpha=0.6, s=100)
    
    ax.set_xlabel('圈复杂度')
    ax.set_ylabel('测试通过率')
    ax.set_title('圈复杂度 vs 测试通过率')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    fig.savefig(output_dir / 'complexity_vs_test_rate.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir / 'complexity_vs_test_rate.png'}")
    plt.close()
    
    # 图4: 指标相关性热力图
    fig, ax = plt.subplots(figsize=(8, 6))
    
    corr_metrics = ['compilation_rate', 'test_pass_rate', 'code_length', 'cyclomatic_complexity']
    corr_matrix = df[corr_metrics].corr()
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, square=True, ax=ax, cbar_kws={'label': '相关系数'})
    ax.set_title('代码质量指标相关性')
    
    plt.tight_layout()
    fig.savefig(output_dir / 'metric_correlation.png', dpi=300, bbox_inches='tight')
    print(f"  ✓ 保存: {output_dir / 'metric_correlation.png'}")
    plt.close()


def main():
    """主函数"""
    print("="*80)
    print("🔍 代码评分结果分析")
    print("="*80)
    
    # 加载数据
    df = load_data()
    print(f"\n加载数据: {len(df)} 条记录, {df['model'].nunique()} 个模型")
    
    # 分析
    model_stats = analyze_compilation_vs_tests(df)
    analyze_score_distribution(df)
    analyze_length_complexity_correlation(df)
    issues = identify_scoring_issues(df)
    suggest_improvements(df, model_stats)
    
    # 可视化
    output_dir = Path(__file__).parent.parent / 'pre_data' / 'analysis_figures'
    create_visualizations(df, model_stats, output_dir)
    
    print("\n" + "="*80)
    print("✅ 分析完成")
    print("="*80)
    print(f"\n详细建议请查看: data/analize/scripts/CODE_SCORING_RECOMMENDATIONS.md")
    print(f"可视化图表: {output_dir}")


if __name__ == '__main__':
    main()
