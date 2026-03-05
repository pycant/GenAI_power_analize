# -*- coding: utf-8 -*-
"""
使用BARTScore评估文本摘要质量

BARTScore是基于BART模型的文本生成评估指标，能够同时评估：
- 信息性 (Informativeness): P(summary|source) - 摘要是否来自原文
- 忠实性 (Faithfulness): P(source|summary) - 原文是否支持摘要

注意：BARTScore计算成本较高，需要GPU加速
"""

import sys
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# 添加BARTScore路径
bartscore_path = Path('tools/thesis_reproduction/BARTScore')
sys.path.insert(0, str(bartscore_path))

from bart_score import BARTScorer
from summary_config import SUMMARY_SOURCE_TEXTS


def evaluate_with_bartscore(data_dir: Path, output_dir: Path, device: str = 'cuda'):
    """使用BARTScore评估摘要质量"""
    
    print("\n" + "="*60)
    print("📊 BARTScore Evaluation for Summary Task")
    print("="*60)
    print(f"⚠️  注意: BARTScore计算成本较高，预计需要10-20分钟")
    print(f"🖥️  使用设备: {device}")
    print("="*60 + "\n")
    
    # 加载已有的评估结果
    scores_file = output_dir / 'summary_quality_scores.csv'
    if not scores_file.exists():
        print(f"❌ 错误: 找不到评估结果文件 {scores_file}")
        print("请先运行 evaluate_summary_quality.py")
        return
    
    df = pd.read_csv(scores_file)
    print(f"📂 已加载 {len(df)} 条评估记录")
    
    # 初始化BARTScorer
    print(f"\n🔧 初始化BARTScorer...")
    print(f"   模型: facebook/bart-large-cnn")
    print(f"   设备: {device}")
    
    try:
        bart_scorer = BARTScorer(device=device, checkpoint='facebook/bart-large-cnn')
        print(f"✅ BARTScorer初始化成功\n")
    except Exception as e:
        print(f"❌ BARTScorer初始化失败: {e}")
        print(f"💡 提示: 确保已安装transformers和torch")
        return
    
    # 加载原始响应数据
    responses_file = data_dir / 'comparison_matrices/summary/summary_responses.csv'
    responses_df = pd.read_csv(responses_file)
    
    # 为每条记录计算BARTScore
    bartscore_info_list = []
    bartscore_faith_list = []
    bartscore_avg_list = []
    
    print("📈 开始计算BARTScore...")
    print(f"   总样本数: {len(df)}")
    print(f"   预计时间: ~{len(df) * 10}秒\n")
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="计算BARTScore"):
        model = row['model']
        question_id = row['question_id']
        
        # 获取原文
        source_text = SUMMARY_SOURCE_TEXTS.get(question_id)
        if source_text is None:
            bartscore_info_list.append(None)
            bartscore_faith_list.append(None)
            bartscore_avg_list.append(None)
            continue
        
        # 获取生成的摘要
        model_responses = responses_df[responses_df['model'] == model]
        if len(model_responses) == 0:
            bartscore_info_list.append(None)
            bartscore_faith_list.append(None)
            bartscore_avg_list.append(None)
            continue
        
        summary = model_responses[question_id].values[0]
        if pd.isna(summary) or len(str(summary).strip()) == 0:
            bartscore_info_list.append(None)
            bartscore_faith_list.append(None)
            bartscore_avg_list.append(None)
            continue
        
        summary = str(summary)
        
        try:
            # 计算信息性: P(summary|source)
            # 即：给定原文，生成摘要的概率
            info_score = bart_scorer.score([source_text], [summary], batch_size=1)[0]
            
            # 计算忠实性: P(source|summary)
            # 即：给定摘要，生成原文的概率
            faith_score = bart_scorer.score([summary], [source_text], batch_size=1)[0]
            
            # 平均分数
            avg_score = (info_score + faith_score) / 2
            
            bartscore_info_list.append(info_score)
            bartscore_faith_list.append(faith_score)
            bartscore_avg_list.append(avg_score)
            
        except Exception as e:
            print(f"\n⚠️  计算失败 (model={model}, question={question_id}): {e}")
            bartscore_info_list.append(None)
            bartscore_faith_list.append(None)
            bartscore_avg_list.append(None)
    
    # 添加BARTScore列
    df['bartscore_info'] = bartscore_info_list
    df['bartscore_faith'] = bartscore_faith_list
    df['bartscore_avg'] = bartscore_avg_list
    
    # 保存更新后的结果
    output_file = output_dir / 'summary_quality_scores_with_bartscore.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ BARTScore评估完成!")
    print(f"📊 结果已保存到: {output_file}")
    
    # 生成统计报告
    generate_bartscore_report(df, output_dir)
    
    return df


def generate_bartscore_report(df: pd.DataFrame, output_dir: Path):
    """生成BARTScore评估报告"""
    
    print(f"\n📝 生成BARTScore评估报告...")
    
    # 过滤有效数据
    valid_df = df[df['bartscore_avg'].notna()].copy()
    
    if len(valid_df) == 0:
        print(f"⚠️  没有有效的BARTScore数据")
        return
    
    # 按模型汇总
    model_stats = valid_df.groupby('model').agg({
        'bartscore_info': ['mean', 'std', 'min', 'max'],
        'bartscore_faith': ['mean', 'std', 'min', 'max'],
        'bartscore_avg': ['mean', 'std', 'min', 'max']
    }).round(4)
    
    # 保存统计数据
    stats_file = output_dir / 'summary_bartscore_summary.csv'
    model_stats.to_csv(stats_file, encoding='utf-8-sig')
    print(f"✅ 统计数据: {stats_file}")
    
    # 生成Markdown报告
    report_file = output_dir / 'summary_bartscore_report.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# BARTScore评估报告\n\n")
        f.write("## 1. 评估概览\n\n")
        f.write(f"- 有效样本数: {len(valid_df)}\n")
        f.write(f"- 评估模型数: {valid_df['model'].nunique()}\n")
        f.write(f"- 评估问题数: {valid_df['question_id'].nunique()}\n\n")
        
        f.write("## 2. BARTScore指标说明\n\n")
        f.write("BARTScore是基于BART模型的文本生成评估指标：\n\n")
        f.write("- **信息性 (Informativeness)**: P(summary|source)\n")
        f.write("  - 衡量摘要是否来自原文\n")
        f.write("  - 分数越高（越接近0）表示摘要越符合原文\n\n")
        f.write("- **忠实性 (Faithfulness)**: P(source|summary)\n")
        f.write("  - 衡量原文是否支持摘要\n")
        f.write("  - 分数越高（越接近0）表示摘要越忠实于原文\n\n")
        f.write("- **平均分数**: (信息性 + 忠实性) / 2\n")
        f.write("  - 综合评估摘要质量\n\n")
        
        f.write("**注意**: BARTScore分数为负值，值越高（越接近0）表示质量越好\n\n")
        
        f.write("## 3. 模型排名\n\n")
        
        # 按平均分数排名
        f.write("### 3.1 按平均BARTScore排名\n\n")
        avg_ranking = valid_df.groupby('model')['bartscore_avg'].mean().sort_values(ascending=False)
        for rank, (model, score) in enumerate(avg_ranking.items(), 1):
            f.write(f"{rank}. **{model}**: {score:.4f}\n")
        f.write("\n")
        
        # 按信息性排名
        f.write("### 3.2 按信息性排名\n\n")
        info_ranking = valid_df.groupby('model')['bartscore_info'].mean().sort_values(ascending=False)
        for rank, (model, score) in enumerate(info_ranking.items(), 1):
            f.write(f"{rank}. **{model}**: {score:.4f}\n")
        f.write("\n")
        
        # 按忠实性排名
        f.write("### 3.3 按忠实性排名\n\n")
        faith_ranking = valid_df.groupby('model')['bartscore_faith'].mean().sort_values(ascending=False)
        for rank, (model, score) in enumerate(faith_ranking.items(), 1):
            f.write(f"{rank}. **{model}**: {score:.4f}\n")
        f.write("\n")
        
        f.write("## 4. 与其他指标的对比\n\n")
        
        # 计算相关性
        if 'rouge_l_f1' in valid_df.columns and 'bertscore_f1' in valid_df.columns:
            corr_rouge = valid_df[['bartscore_avg', 'rouge_l_f1']].corr().iloc[0, 1]
            corr_bert = valid_df[['bartscore_avg', 'bertscore_f1']].corr().iloc[0, 1]
            
            f.write("### 4.1 指标相关性\n\n")
            f.write(f"- BARTScore vs ROUGE-L: {corr_rouge:.4f}\n")
            f.write(f"- BARTScore vs BERTScore: {corr_bert:.4f}\n\n")
        
        f.write("## 5. 关键发现\n\n")
        
        best_model = avg_ranking.index[0]
        best_score = avg_ranking.values[0]
        
        f.write(f"- **最佳模型**: {best_model} (平均BARTScore: {best_score:.4f})\n")
        f.write(f"- **分数范围**: [{valid_df['bartscore_avg'].min():.4f}, {valid_df['bartscore_avg'].max():.4f}]\n")
        f.write(f"- **平均分数**: {valid_df['bartscore_avg'].mean():.4f}\n")
        
    print(f"✅ 评估报告: {report_file}")
    
    # 打印Top 3
    print(f"\n🏆 Top 3 模型 (按平均BARTScore):")
    for rank, (model, score) in enumerate(avg_ranking.head(3).items(), 1):
        print(f"  {rank}. {model}: {score:.4f}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='使用BARTScore评估摘要质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/summary_quality',
                       help='输出目录')
    parser.add_argument('--device', type=str, default='cuda',
                       choices=['cuda', 'cpu'],
                       help='计算设备（默认：cuda）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    # 检查CUDA可用性
    if args.device == 'cuda':
        try:
            import torch
            if not torch.cuda.is_available():
                print("⚠️  CUDA不可用，切换到CPU模式")
                args.device = 'cpu'
        except ImportError:
            print("⚠️  未安装torch，切换到CPU模式")
            args.device = 'cpu'
    
    evaluate_with_bartscore(data_dir, output_dir, args.device)


if __name__ == '__main__':
    main()
