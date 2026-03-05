# -*- coding: utf-8 -*-
"""
文本摘要质量评估可视化

生成图表：
1. ROUGE-L F1 vs BERTScore F1 散点图
2. 压缩比分布箱线图
3. 各模型核心指标雷达图
4. 字数符合度与信息密度对比
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 设置样式
sns.set_style("whitegrid")
sns.set_palette("husl")


def load_data(results_dir: Path):
    """加载评估结果"""
    # 优先加载包含BARTScore的文件
    bartscore_file = results_dir / 'summary_quality_scores_with_bartscore.csv'
    scores_file = results_dir / 'summary_quality_scores.csv'
    
    if bartscore_file.exists():
        scores_df = pd.read_csv(bartscore_file)
        print("✅ 已加载包含BARTScore的评估结果")
    else:
        scores_df = pd.read_csv(scores_file)
        print("ℹ️  加载基础评估结果（不含BARTScore）")
    
    summary_file = results_dir / 'summary_quality_summary.csv'
    summary_df = pd.read_csv(summary_file)
    
    return scores_df, summary_df


def plot_rouge_vs_bertscore(scores_df: pd.DataFrame, output_dir: Path):
    """绘制ROUGE-L vs BERTScore散点图"""
    
    # 计算每个模型的平均分数
    model_avg = scores_df.groupby('model').agg({
        'rouge_l_f1': 'mean',
        'bertscore_f1': 'mean',
        'compression_ratio': 'mean'
    }).reset_index()
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 绘制散点，大小表示压缩比
    scatter = ax.scatter(
        model_avg['rouge_l_f1'],
        model_avg['bertscore_f1'],
        s=model_avg['compression_ratio'] * 200,  # 放大以便可见
        alpha=0.6,
        c=range(len(model_avg)),
        cmap='tab20'
    )
    
    # 添加模型标签
    for idx, row in model_avg.iterrows():
        ax.annotate(
            row['model'],
            (row['rouge_l_f1'], row['bertscore_f1']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9,
            alpha=0.8
        )
    
    # 添加参考线
    ax.axhline(y=model_avg['bertscore_f1'].mean(), 
               color='gray', linestyle='--', alpha=0.5, label='BERTScore均值')
    ax.axvline(x=model_avg['rouge_l_f1'].mean(), 
               color='gray', linestyle='--', alpha=0.5, label='ROUGE-L均值')
    
    ax.set_xlabel('ROUGE-L F1 (结构完整性)', fontsize=12)
    ax.set_ylabel('BERTScore F1 (语义相似度)', fontsize=12)
    ax.set_title('文本摘要质量：ROUGE-L vs BERTScore\n(气泡大小表示压缩比)', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = output_dir / 'summary_rouge_vs_bertscore.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 图表已保存: {output_file}")


def plot_compression_ratio_distribution(scores_df: pd.DataFrame, output_dir: Path):
    """绘制压缩比分布箱线图"""
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # 按模型分组
    models = scores_df['model'].unique()
    data_to_plot = [scores_df[scores_df['model'] == model]['compression_ratio'].values 
                    for model in models]
    
    # 绘制箱线图
    bp = ax.boxplot(data_to_plot, labels=models, patch_artist=True)
    
    # 设置颜色
    colors = sns.color_palette("husl", len(models))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    
    # 添加理想压缩比范围
    ax.axhspan(0.2, 0.4, alpha=0.1, color='green', label='理想压缩比范围 (0.2-0.4)')
    
    ax.set_xlabel('模型', fontsize=12)
    ax.set_ylabel('压缩比 (摘要长度/原文长度)', fontsize=12)
    ax.set_title('各模型压缩比分布\n(越接近0.2-0.4越理想)', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 旋转x轴标签
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    output_file = output_dir / 'summary_compression_ratio_distribution.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 图表已保存: {output_file}")


def plot_radar_chart(scores_df: pd.DataFrame, output_dir: Path):
    """绘制核心指标雷达图"""
    
    # 选择Top 6模型（基于BERTScore F1）
    top_models = scores_df.groupby('model')['bertscore_f1'].mean().nlargest(6).index.tolist()
    
    # 准备数据
    metrics = ['rouge_l_f1', 'bertscore_f1', 'information_density']
    metric_labels = ['ROUGE-L F1\n(结构完整性)', 'BERTScore F1\n(语义相似度)', 
                     '信息密度\n(信息效率)']
    
    # 计算每个模型的平均分数并归一化
    model_scores = []
    for model in top_models:
        model_data = scores_df[scores_df['model'] == model]
        scores = []
        for metric in metrics:
            score = model_data[metric].mean()
            if pd.isna(score):
                score = 0.0
            scores.append(score)
        model_scores.append(scores)
    
    # 归一化到[0, 1]
    model_scores = np.array(model_scores)
    for i in range(model_scores.shape[1]):
        col = model_scores[:, i]
        if col.max() > 0:
            model_scores[:, i] = col / col.max()
    
    # 创建雷达图
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = sns.color_palette("husl", len(top_models))
    
    for idx, (model, scores) in enumerate(zip(top_models, model_scores)):
        scores_plot = scores.tolist()
        scores_plot += scores_plot[:1]  # 闭合
        
        ax.plot(angles, scores_plot, 'o-', linewidth=2, 
                label=model, color=colors[idx])
        ax.fill(angles, scores_plot, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=9)
    ax.grid(True, alpha=0.3)
    
    ax.set_title('Top 6 模型核心指标对比\n(归一化分数)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    
    plt.tight_layout()
    output_file = output_dir / 'summary_radar_chart.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 图表已保存: {output_file}")


def plot_compliance_vs_density(scores_df: pd.DataFrame, output_dir: Path):
    """绘制字数符合度与信息密度对比"""
    
    # 计算每个模型的平均值
    model_avg = scores_df.groupby('model').agg({
        'in_range': lambda x: x.mean() * 100,  # 转换为百分比
        'information_density': 'mean',
        'rouge_l_f1': 'mean'
    }).reset_index()
    
    # 按信息密度排序
    model_avg = model_avg.sort_values('information_density', ascending=False)
    
    # 创建双轴图表
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    x = np.arange(len(model_avg))
    width = 0.35
    
    # 字数符合度（左轴）
    bars1 = ax1.bar(x - width/2, model_avg['in_range'], width, 
                    label='字数符合率 (%)', color='steelblue', alpha=0.7)
    ax1.set_xlabel('模型', fontsize=12)
    ax1.set_ylabel('字数符合率 (%)', fontsize=12, color='steelblue')
    ax1.tick_params(axis='y', labelcolor='steelblue')
    ax1.set_ylim(0, 100)
    
    # 信息密度（右轴）
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, model_avg['information_density'], width,
                    label='信息密度', color='coral', alpha=0.7)
    ax2.set_ylabel('信息密度', fontsize=12, color='coral')
    ax2.tick_params(axis='y', labelcolor='coral')
    
    # 设置x轴标签
    ax1.set_xticks(x)
    ax1.set_xticklabels(model_avg['model'], rotation=45, ha='right')
    
    # 添加标题和图例
    ax1.set_title('字数符合度 vs 信息密度\n(按信息密度排序)', 
                  fontsize=14, fontweight='bold')
    
    # 合并图例
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ax1.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    output_file = output_dir / 'summary_compliance_vs_density.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 图表已保存: {output_file}")


def plot_bartscore_comparison(scores_df: pd.DataFrame, output_dir: Path):
    """绘制BARTScore对比图"""
    
    # 检查是否有BARTScore数据
    if 'bartscore_avg' not in scores_df.columns:
        print("ℹ️  跳过BARTScore图表（数据不可用）")
        return
    
    # 过滤有效数据
    valid_df = scores_df[scores_df['bartscore_avg'].notna()].copy()
    
    if len(valid_df) == 0:
        print("⚠️  没有有效的BARTScore数据")
        return
    
    # 计算每个模型的平均分数
    model_avg = valid_df.groupby('model').agg({
        'bartscore_info': 'mean',
        'bartscore_faith': 'mean',
        'bartscore_avg': 'mean',
        'bertscore_f1': 'mean'
    }).reset_index()
    
    # 按平均BARTScore排序
    model_avg = model_avg.sort_values('bartscore_avg', ascending=False)
    
    # 创建图表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 左图：BARTScore信息性 vs 忠实性
    x = np.arange(len(model_avg))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, model_avg['bartscore_info'], width,
                    label='信息性 (Informativeness)', color='skyblue', alpha=0.8)
    bars2 = ax1.bar(x + width/2, model_avg['bartscore_faith'], width,
                    label='忠实性 (Faithfulness)', color='lightcoral', alpha=0.8)
    
    ax1.set_xlabel('模型', fontsize=12)
    ax1.set_ylabel('BARTScore (越高越好)', fontsize=12)
    ax1.set_title('BARTScore: 信息性 vs 忠实性', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(model_avg['model'], rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # 右图：BARTScore vs BERTScore散点图
    ax2.scatter(model_avg['bartscore_avg'], model_avg['bertscore_f1'],
                s=200, alpha=0.6, c=range(len(model_avg)), cmap='tab20')
    
    # 添加模型标签
    for idx, row in model_avg.iterrows():
        ax2.annotate(
            row['model'],
            (row['bartscore_avg'], row['bertscore_f1']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9,
            alpha=0.8
        )
    
    # 计算相关系数
    corr = model_avg[['bartscore_avg', 'bertscore_f1']].corr().iloc[0, 1]
    
    ax2.set_xlabel('BARTScore (平均)', fontsize=12)
    ax2.set_ylabel('BERTScore F1', fontsize=12)
    ax2.set_title(f'BARTScore vs BERTScore\n(相关系数: {corr:.4f})', 
                  fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = output_dir / 'summary_bartscore_comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ 图表已保存: {output_file}")


def generate_summary_insights(scores_df: pd.DataFrame, output_dir: Path):
    """生成评估洞察报告"""
    
    insights = []
    
    # 1. 最佳模型分析
    insights.append("## 关键发现\n")
    
    # ROUGE-L最高
    best_rouge = scores_df.groupby('model')['rouge_l_f1'].mean().idxmax()
    best_rouge_score = scores_df.groupby('model')['rouge_l_f1'].mean().max()
    insights.append(f"### 1. 结构完整性最佳")
    insights.append(f"- **{best_rouge}** 在ROUGE-L F1上表现最好 ({best_rouge_score:.4f})")
    insights.append(f"- 说明该模型能够保留原文的关键结构和信息\n")
    
    # BERTScore最高
    best_bert = scores_df.groupby('model')['bertscore_f1'].mean().idxmax()
    best_bert_score = scores_df.groupby('model')['bertscore_f1'].mean().max()
    insights.append(f"### 2. 语义相似度最佳")
    insights.append(f"- **{best_bert}** 在BERTScore F1上表现最好 ({best_bert_score:.4f})")
    insights.append(f"- 说明该模型生成的摘要在语义层面与原文最接近\n")
    
    # BARTScore最高（如果有）
    if 'bartscore_avg' in scores_df.columns:
        valid_bart = scores_df[scores_df['bartscore_avg'].notna()]
        if len(valid_bart) > 0:
            best_bart = valid_bart.groupby('model')['bartscore_avg'].mean().idxmax()
            best_bart_score = valid_bart.groupby('model')['bartscore_avg'].mean().max()
            insights.append(f"### 3. BARTScore综合评分最佳")
            insights.append(f"- **{best_bart}** 在BARTScore上表现最好 ({best_bart_score:.4f})")
            insights.append(f"- BARTScore综合评估信息性和忠实性，是最接近人类评分的自动指标\n")
    
    # 压缩比分析
    ideal_compression = scores_df.groupby('model')['compression_ratio'].mean()
    ideal_models = ideal_compression[(ideal_compression >= 0.2) & (ideal_compression <= 0.4)]
    section_num = 4 if 'bartscore_avg' in scores_df.columns else 3
    if len(ideal_models) > 0:
        insights.append(f"### {section_num}. 压缩比理想模型")
        for model, ratio in ideal_models.items():
            insights.append(f"- **{model}**: {ratio:.3f} (在理想范围0.2-0.4内)")
    else:
        closest_model = (ideal_compression - 0.3).abs().idxmin()
        closest_ratio = ideal_compression[closest_model]
        insights.append(f"### {section_num}. 压缩比分析")
        insights.append(f"- 没有模型在理想范围(0.2-0.4)内")
        insights.append(f"- **{closest_model}** 最接近理想值 ({closest_ratio:.3f})")
    insights.append("")
    
    # 信息密度最高
    section_num += 1
    best_density = scores_df.groupby('model')['information_density'].mean().idxmax()
    best_density_score = scores_df.groupby('model')['information_density'].mean().max()
    insights.append(f"### {section_num}. 信息效率最高")
    insights.append(f"- **{best_density}** 信息密度最高 ({best_density_score:.4f})")
    insights.append(f"- 说明该模型能用更少的字表达更多信息\n")
    
    # 字数符合度
    section_num += 1
    compliance_rate = scores_df.groupby('model')['in_range'].mean() * 100
    if compliance_rate.max() > 0:
        best_compliance = compliance_rate.idxmax()
        best_compliance_rate = compliance_rate.max()
        insights.append(f"### {section_num}. 字数符合度")
        insights.append(f"- **{best_compliance}** 字数符合率最高 ({best_compliance_rate:.1f}%)")
    else:
        insights.append(f"### {section_num}. 字数符合度")
        insights.append(f"- 所有模型的字数符合率都较低")
        insights.append(f"- 建议：大多数模型生成的摘要超出或不足指定字数范围")
    insights.append("")
    
    # 综合建议
    insights.append("## 综合建议\n")
    insights.append("### 应用场景推荐\n")
    insights.append(f"- **信息保留优先**: 选择 **{best_rouge}** (ROUGE-L最高)")
    insights.append(f"- **语义准确优先**: 选择 **{best_bert}** (BERTScore最高)")
    if 'bartscore_avg' in scores_df.columns and len(valid_bart) > 0:
        insights.append(f"- **综合质量优先**: 选择 **{best_bart}** (BARTScore最高)")
    insights.append(f"- **信息效率优先**: 选择 **{best_density}** (信息密度最高)")
    
    # 保存洞察报告
    insights_file = output_dir / 'summary_quality_insights.md'
    with open(insights_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(insights))
    
    print(f"✅ 洞察报告已保存: {insights_file}")


def main():
    """主函数"""
    
    print("\n" + "="*60)
    print("📊 Summary Quality Visualization")
    print("="*60 + "\n")
    
    # 设置路径
    results_dir = Path('data/analize/results/summary_quality')
    output_dir = results_dir
    
    # 加载数据
    print("📂 加载评估结果...")
    scores_df, summary_df = load_data(results_dir)
    print(f"✅ 已加载 {len(scores_df)} 条评估记录")
    print(f"✅ 涉及 {scores_df['model'].nunique()} 个模型\n")
    
    # 生成图表
    print("📈 生成可视化图表...\n")
    
    print("1️⃣ ROUGE-L vs BERTScore 散点图...")
    plot_rouge_vs_bertscore(scores_df, output_dir)
    
    print("2️⃣ 压缩比分布箱线图...")
    plot_compression_ratio_distribution(scores_df, output_dir)
    
    print("3️⃣ 核心指标雷达图...")
    plot_radar_chart(scores_df, output_dir)
    
    print("4️⃣ 字数符合度 vs 信息密度...")
    plot_compliance_vs_density(scores_df, output_dir)
    
    print("5️⃣ BARTScore对比图...")
    plot_bartscore_comparison(scores_df, output_dir)
    
    # 生成洞察报告
    print("\n📝 生成评估洞察...")
    generate_summary_insights(scores_df, output_dir)
    
    # 统计生成的图表数量
    chart_count = 4
    if 'bartscore_avg' in scores_df.columns:
        chart_count = 5
    
    print("\n" + "="*60)
    print("✅ 可视化完成！")
    print("="*60)
    print(f"\n📁 输出目录: {output_dir}")
    print(f"📊 生成图表: {chart_count} 张")
    print(f"📄 洞察报告: summary_quality_insights.md\n")


if __name__ == '__main__':
    main()
