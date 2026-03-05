#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聚合所有任务类型的质量评估结果
生成综合分析报告和可视化图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 配置
RESULTS_DIR = Path("data/analize/results")
OUTPUT_DIR = RESULTS_DIR / "aggregate"
OUTPUT_DIR.mkdir(exist_ok=True)

# 任务类型配置
TASK_CONFIGS = {
    'code': {
        'dir': 'code_quality',
        'name': '代码生成',
        'key_metrics': ['syntax_score', 'functionality_score', 'code_quality_score']
    },
    'creative': {
        'dir': 'creative_quality',
        'name': '创意写作',
        'key_metrics': ['diversity_score', 'coherence_score', 'creativity_score']
    },
    'math': {
        'dir': 'math_quality',
        'name': '数学推理',
        'key_metrics': ['correctness', 'reasoning_quality', 'final_score']
    },
    'qa': {
        'dir': 'qa_quality',
        'name': '问答',
        'key_metrics': ['exact_match', 'f1_score', 'semantic_similarity']
    },
    'reasoning': {
        'dir': 'reasoning_quality',
        'name': '逻辑推理',
        'key_metrics': ['step_count', 'completeness', 'conclusion_correct']
    },
    'summary': {
        'dir': 'summary_quality',
        'name': '文本摘要',
        'key_metrics': ['rouge_l', 'bertscore_f1', 'compression_ratio']
    },
    'translation': {
        'dir': 'translation_quality',
        'name': '翻译',
        'key_metrics': ['bleu_4', 'chrf_plus', 'bertscore_f1']
    }
}


def load_task_summary(task_type: str) -> pd.DataFrame:
    """加载单个任务的汇总结果"""
    config = TASK_CONFIGS[task_type]
    summary_file = RESULTS_DIR / config['dir'] / f"{task_type}_quality_summary.csv"
    
    if not summary_file.exists():
        print(f"⚠️  {config['name']}任务汇总文件不存在: {summary_file}")
        return None
    
    try:
        df = pd.read_csv(summary_file, encoding='utf-8')
        df['task_type'] = task_type
        df['task_name'] = config['name']
        return df
    except Exception as e:
        print(f"❌ 加载{config['name']}任务失败: {e}")
        return None


def aggregate_all_summaries() -> pd.DataFrame:
    """聚合所有任务的汇总结果"""
    all_data = []
    
    for task_type in TASK_CONFIGS.keys():
        df = load_task_summary(task_type)
        if df is not None:
            all_data.append(df)
    
    if not all_data:
        raise ValueError("没有找到任何任务的汇总数据")
    
    return pd.concat(all_data, ignore_index=True)


def calculate_overall_scores(df: pd.DataFrame) -> pd.DataFrame:
    """计算每个模型在所有任务上的综合得分"""
    # 提取模型名称（假设在model或model_name列）
    model_col = 'model' if 'model' in df.columns else 'model_name'
    
    # 按模型和任务分组，计算平均得分
    score_cols = [col for col in df.columns if 'score' in col.lower() or 
                  col in ['exact_match', 'f1_score', 'correctness', 'bleu_4', 'rouge_l']]
    
    # 归一化每个任务的得分到0-1范围
    df_norm = df.copy()
    for task in df['task_type'].unique():
        task_mask = df['task_type'] == task
        for col in score_cols:
            if col in df.columns:
                task_data = df.loc[task_mask, col]
                if task_data.notna().any():
                    min_val = task_data.min()
                    max_val = task_data.max()
                    if max_val > min_val:
                        df_norm.loc[task_mask, f'{col}_norm'] = (task_data - min_val) / (max_val - min_val)
    
    # 计算每个模型的平均归一化得分
    norm_cols = [col for col in df_norm.columns if col.endswith('_norm')]
    if norm_cols:
        df_norm['overall_score'] = df_norm[norm_cols].mean(axis=1)
    
    return df_norm


def plot_task_comparison(df: pd.DataFrame):
    """绘制任务间对比图"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('所有任务类型质量评估综合对比', fontsize=16, fontweight='bold')
    
    model_col = 'model' if 'model' in df.columns else 'model_name'
    
    # 1. 各任务平均得分对比
    ax1 = axes[0, 0]
    if 'overall_score' in df.columns:
        task_scores = df.groupby('task_name')['overall_score'].mean().sort_values(ascending=False)
        task_scores.plot(kind='bar', ax=ax1, color='steelblue')
        ax1.set_title('各任务类型平均质量得分', fontsize=12, fontweight='bold')
        ax1.set_xlabel('任务类型')
        ax1.set_ylabel('平均得分')
        ax1.grid(axis='y', alpha=0.3)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. 模型在各任务上的表现热力图
    ax2 = axes[0, 1]
    if 'overall_score' in df.columns:
        pivot_data = df.pivot_table(values='overall_score', 
                                     index=model_col, 
                                     columns='task_name', 
                                     aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, fmt='.3f', cmap='RdYlGn', 
                   ax=ax2, cbar_kws={'label': '得分'})
        ax2.set_title('模型-任务质量热力图', fontsize=12, fontweight='bold')
        ax2.set_xlabel('任务类型')
        ax2.set_ylabel('模型')
    
    # 3. 模型综合排名
    ax3 = axes[1, 0]
    if 'overall_score' in df.columns:
        model_scores = df.groupby(model_col)['overall_score'].mean().sort_values(ascending=True)
        model_scores.plot(kind='barh', ax=ax3, color='coral')
        ax3.set_title('模型综合质量排名', fontsize=12, fontweight='bold')
        ax3.set_xlabel('平均得分')
        ax3.set_ylabel('模型')
        ax3.grid(axis='x', alpha=0.3)
    
    # 4. 任务数量统计
    ax4 = axes[1, 1]
    task_counts = df['task_name'].value_counts()
    ax4.pie(task_counts.values, labels=task_counts.index, autopct='%1.1f%%',
           startangle=90, colors=sns.color_palette('pastel'))
    ax4.set_title('评估样本分布', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    output_file = OUTPUT_DIR / 'aggregate_task_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存: {output_file}")
    plt.close()


def plot_model_radar(df: pd.DataFrame):
    """绘制模型能力雷达图"""
    model_col = 'model' if 'model' in df.columns else 'model_name'
    
    if 'overall_score' not in df.columns:
        print("⚠️  缺少overall_score列，跳过雷达图")
        return
    
    # 计算每个模型在各任务上的平均得分
    pivot_data = df.pivot_table(values='overall_score', 
                                 index=model_col, 
                                 columns='task_name', 
                                 aggfunc='mean')
    
    # 选择前5个模型
    top_models = df.groupby(model_col)['overall_score'].mean().nlargest(5).index
    pivot_data = pivot_data.loc[top_models]
    
    # 绘制雷达图
    categories = list(pivot_data.columns)
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = sns.color_palette('husl', len(top_models))
    
    for idx, (model, row) in enumerate(pivot_data.iterrows()):
        values = row.tolist()
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, size=10)
    ax.set_ylim(0, 1)
    ax.set_title('Top 5 模型多任务能力雷达图', size=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    output_file = OUTPUT_DIR / 'aggregate_model_radar.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存: {output_file}")
    plt.close()


def generate_aggregate_report(df: pd.DataFrame):
    """生成综合分析报告"""
    model_col = 'model' if 'model' in df.columns else 'model_name'
    
    report = []
    report.append("# 质量评估综合分析报告\n")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n\n")
    
    # 1. 总体统计
    report.append("## 1. 总体统计\n\n")
    report.append(f"- 评估任务类型: {df['task_type'].nunique()} 种\n")
    report.append(f"- 评估模型数量: {df[model_col].nunique()} 个\n")
    report.append(f"- 总评估样本数: {len(df)} 条\n\n")
    
    # 2. 任务类型分布
    report.append("## 2. 任务类型分布\n\n")
    report.append("| 任务类型 | 样本数 | 占比 |\n")
    report.append("|---------|--------|------|\n")
    task_dist = df['task_name'].value_counts()
    for task, count in task_dist.items():
        pct = count / len(df) * 100
        report.append(f"| {task} | {count} | {pct:.1f}% |\n")
    report.append("\n")
    
    # 3. 模型综合排名
    report.append("## 3. 模型综合排名\n\n")
    if 'overall_score' in df.columns:
        model_ranking = df.groupby(model_col)['overall_score'].mean().sort_values(ascending=False)
        report.append("| 排名 | 模型 | 综合得分 |\n")
        report.append("|------|------|----------|\n")
        for rank, (model, score) in enumerate(model_ranking.items(), 1):
            report.append(f"| {rank} | {model} | {score:.4f} |\n")
        report.append("\n")
    
    # 4. 各任务最佳模型
    report.append("## 4. 各任务最佳模型\n\n")
    report.append("| 任务类型 | 最佳模型 | 得分 |\n")
    report.append("|---------|---------|------|\n")
    for task in df['task_name'].unique():
        task_data = df[df['task_name'] == task]
        if 'overall_score' in task_data.columns:
            best_idx = task_data['overall_score'].idxmax()
            best_model = task_data.loc[best_idx, model_col]
            best_score = task_data.loc[best_idx, 'overall_score']
            report.append(f"| {task} | {best_model} | {best_score:.4f} |\n")
    report.append("\n")
    
    # 5. 关键发现
    report.append("## 5. 关键发现\n\n")
    if 'overall_score' in df.columns:
        # 最佳模型
        best_model = df.groupby(model_col)['overall_score'].mean().idxmax()
        best_score = df.groupby(model_col)['overall_score'].mean().max()
        report.append(f"- **综合表现最佳模型**: {best_model} (得分: {best_score:.4f})\n")
        
        # 最稳定模型（标准差最小）
        model_std = df.groupby(model_col)['overall_score'].std()
        most_stable = model_std.idxmin()
        report.append(f"- **表现最稳定模型**: {most_stable} (标准差: {model_std.min():.4f})\n")
        
        # 任务难度
        task_avg = df.groupby('task_name')['overall_score'].mean().sort_values()
        easiest = task_avg.idxmax()
        hardest = task_avg.idxmin()
        report.append(f"- **最容易任务**: {easiest} (平均得分: {task_avg.max():.4f})\n")
        report.append(f"- **最困难任务**: {hardest} (平均得分: {task_avg.min():.4f})\n")
    
    report.append("\n")
    
    # 6. 数据文件
    report.append("## 6. 详细数据文件\n\n")
    report.append("- 综合数据: `aggregate/aggregate_all_tasks.csv`\n")
    report.append("- 归一化数据: `aggregate/aggregate_normalized.csv`\n")
    report.append("- 模型排名: `aggregate/model_ranking.csv`\n")
    report.append("- 任务统计: `aggregate/task_statistics.csv`\n\n")
    
    # 7. 可视化图表
    report.append("## 7. 可视化图表\n\n")
    report.append("- 任务对比图: `aggregate/aggregate_task_comparison.png`\n")
    report.append("- 模型雷达图: `aggregate/aggregate_model_radar.png`\n\n")
    
    # 保存报告
    report_file = OUTPUT_DIR / 'AGGREGATE_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"✅ 已保存: {report_file}")


def save_aggregate_data(df: pd.DataFrame, df_norm: pd.DataFrame):
    """保存聚合数据"""
    model_col = 'model' if 'model' in df.columns else 'model_name'
    
    # 1. 保存完整数据
    output_file = OUTPUT_DIR / 'aggregate_all_tasks.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ 已保存: {output_file}")
    
    # 2. 保存归一化数据
    output_file = OUTPUT_DIR / 'aggregate_normalized.csv'
    df_norm.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✅ 已保存: {output_file}")
    
    # 3. 保存模型排名
    if 'overall_score' in df_norm.columns:
        model_ranking = df_norm.groupby(model_col).agg({
            'overall_score': ['mean', 'std', 'min', 'max', 'count']
        }).round(4)
        model_ranking.columns = ['平均得分', '标准差', '最低分', '最高分', '样本数']
        model_ranking = model_ranking.sort_values('平均得分', ascending=False)
        output_file = OUTPUT_DIR / 'model_ranking.csv'
        model_ranking.to_csv(output_file, encoding='utf-8')
        print(f"✅ 已保存: {output_file}")
    
    # 4. 保存任务统计
    task_stats = df_norm.groupby('task_name').agg({
        'overall_score': ['mean', 'std', 'min', 'max', 'count']
    }).round(4)
    task_stats.columns = ['平均得分', '标准差', '最低分', '最高分', '样本数']
    task_stats = task_stats.sort_values('平均得分', ascending=False)
    output_file = OUTPUT_DIR / 'task_statistics.csv'
    task_stats.to_csv(output_file, encoding='utf-8')
    print(f"✅ 已保存: {output_file}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("📊 聚合所有任务质量评估结果")
    print("="*60 + "\n")
    
    # 1. 加载所有任务数据
    print("📂 加载任务数据...")
    df = aggregate_all_summaries()
    print(f"✅ 成功加载 {len(df)} 条记录\n")
    
    # 2. 计算综合得分
    print("🔢 计算综合得分...")
    df_norm = calculate_overall_scores(df)
    print("✅ 完成\n")
    
    # 3. 保存数据
    print("💾 保存聚合数据...")
    save_aggregate_data(df, df_norm)
    print()
    
    # 4. 生成可视化
    print("📊 生成可视化图表...")
    plot_task_comparison(df_norm)
    plot_model_radar(df_norm)
    print()
    
    # 5. 生成报告
    print("📝 生成综合报告...")
    generate_aggregate_report(df_norm)
    print()
    
    print("="*60)
    print("✅ 聚合分析完成!")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
