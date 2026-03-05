# -*- coding: utf-8 -*-
"""
翻译任务质量评估脚本

评估所有模型在翻译任务上的表现
"""

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent))

from quality_evaluation.translation_evaluator import TranslationEvaluator
from translation_config import TRANSLATION_REFERENCES


def evaluate_translation_quality(data_dir: Path, output_dir: Path,
                                 use_bertscore: bool = True):
    """评估翻译任务质量"""
    
    print("\n" + "="*60)
    print("🌐 Translation Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/translation/translation_responses.csv'
    
    if not responses_file.exists():
        print(f"❌ Error: File not found: {responses_file}")
        return None
    
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"🌐 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_bertscore': use_bertscore,
        'device': 'cuda'
    }
    evaluator = TranslationEvaluator(config)
    
    print(f"\n⚙️  Configuration:")
    print(f"   - BERTScore: {'✅ Enabled' if use_bertscore else '❌ Disabled'}")
    
    # 评估每个模型的每个响应
    results = []
    
    total_evaluations = len(df) * len([c for c in df.columns if c != 'model'])
    
    with tqdm(total=total_evaluations, desc="Evaluating") as pbar:
        for _, row in df.iterrows():
            model = row['model']
            
            for col in df.columns:
                if col == 'model':
                    continue
                
                response = row[col]
                
                if pd.isna(response) or len(str(response).strip()) == 0:
                    pbar.update(1)
                    continue
                
                # 获取参考译文和源文本
                ref_data = TRANSLATION_REFERENCES.get(col)
                
                if ref_data is None:
                    print(f"\n⚠️  No reference data for {col}")
                    pbar.update(1)
                    continue
                
                reference = ref_data['reference']
                source_text = ref_data['source']
                target_lang = ref_data['target_lang']
                
                # 构建上下文
                context = {
                    'source_text': source_text,
                    'source_lang': ref_data['source_lang'],
                    'target_lang': target_lang,
                    'domain': ref_data['domain']
                }
                
                # 评估质量
                scores = evaluator.evaluate(
                    str(response),
                    reference=reference,
                    context=context
                )
                
                # 保存结果
                result = {
                    'model': model,
                    'question_id': col,
                    'source_lang': ref_data['source_lang'],
                    'target_lang': target_lang,
                    'domain': ref_data['domain'],
                    **scores
                }
                results.append(result)
                
                pbar.update(1)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'translation_quality_scores.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
    # 生成报告
    generate_report(results_df, output_dir)
    
    return results_df


def generate_summary_stats(df: pd.DataFrame, output_dir: Path):
    """生成汇总统计"""
    
    print(f"\n📊 Generating summary statistics...")
    
    # 按模型汇总
    metric_cols = [col for col in df.columns 
                   if col not in ['model', 'question_id', 'source_lang', 
                                 'target_lang', 'domain'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'translation_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'bleu_4' in df.columns:
        print(f"\n🏆 Top 3 Models by BLEU-4:")
        top_models = df.groupby('model')['bleu_4'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")
    
    if 'bertscore_f1' in df.columns:
        print(f"\n🎯 Top 3 Models by BERTScore F1:")
        top_models = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")
    
    if 'chrf' in df.columns:
        print(f"\n📝 Top 3 Models by chrF:")
        top_models = df.groupby('model')['chrf'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_file = output_dir / 'TRANSLATION_EVALUATION_REPORT.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 翻译质量评估报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 评估概览\n\n")
        f.write(f"- 评估模型数: {df['model'].nunique()}\n")
        f.write(f"- 评估问题数: {df['question_id'].nunique()}\n")
        f.write(f"- 总评估次数: {len(df)}\n")
        f.write(f"- 语言对: 英→中 (4题), 中→英 (1题)\n\n")
        
        f.write("## 2. 核心指标排名\n\n")
        
        # BLEU-4排名
        if 'bleu_4' in df.columns:
            f.write("### 2.1 BLEU-4 排名\n\n")
            f.write("BLEU-4 是机器翻译最经典的评估指标，衡量词汇级别的匹配度。\n\n")
            bleu_ranking = df.groupby('model')['bleu_4'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(bleu_ranking.items(), 1):
                status = "✅" if score >= 0.4 else "⚠️" if score >= 0.2 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # chrF排名
        if 'chrf' in df.columns:
            f.write("### 2.2 chrF 排名\n\n")
            f.write("chrF 基于字符级别匹配，对中文等字符级语言更友好。\n\n")
            chrf_ranking = df.groupby('model')['chrf'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(chrf_ranking.items(), 1):
                status = "✅" if score >= 0.5 else "⚠️" if score >= 0.3 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # BERTScore排名
        if 'bertscore_f1' in df.columns:
            f.write("### 2.3 BERTScore F1 排名\n\n")
            f.write("BERTScore 基于语义相似度，能识别同义词和改写。\n\n")
            bert_ranking = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(bert_ranking.items(), 1):
                status = "✅" if score >= 0.8 else "⚠️" if score >= 0.6 else "❌"
                f.write(f"{rank}. {status} **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 按语言对分析
        if 'source_lang' in df.columns and 'bleu_4' in df.columns:
            f.write("### 2.4 按语言对分析\n\n")
            f.write("各模型在不同语言对上的BLEU-4分数：\n\n")
            
            # 英译中
            eng_to_zh = df[df['source_lang'] == 'eng'].groupby('model')['bleu_4'].mean().sort_values(ascending=False)
            f.write("**英译中 (eng → zho_Hans)**:\n\n")
            for rank, (model, score) in enumerate(eng_to_zh.head(5).items(), 1):
                f.write(f"{rank}. {model}: {score:.4f}\n")
            f.write("\n")
            
            # 中译英
            zh_to_eng = df[df['source_lang'] == 'zho_Hans'].groupby('model')['bleu_4'].mean().sort_values(ascending=False)
            f.write("**中译英 (zho_Hans → eng)**:\n\n")
            for rank, (model, score) in enumerate(zh_to_eng.head(5).items(), 1):
                f.write(f"{rank}. {model}: {score:.4f}\n")
            f.write("\n")
        
        f.write("## 3. 指标说明\n\n")
        f.write("### 3.1 BLEU-4\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 4-gram词汇匹配度\n")
        f.write("- **解释**: 0.4+ 优秀，0.2-0.4 良好，<0.2 需改进\n\n")
        
        f.write("### 3.2 chrF\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 字符级F分数\n")
        f.write("- **解释**: 0.5+ 优秀，0.3-0.5 良好，<0.3 需改进\n\n")
        
        f.write("### 3.3 BERTScore F1\n")
        f.write("- **范围**: [0, 1]\n")
        f.write("- **含义**: 语义相似度\n")
        f.write("- **解释**: 0.8+ 优秀，0.6-0.8 良好，<0.6 需改进\n\n")
        
        f.write("## 4. 详细数据\n\n")
        f.write("详细评分数据请参考:\n")
        f.write("- `translation_quality_scores.csv` - 每个模型每个问题的详细评分\n")
        f.write("- `translation_quality_summary.csv` - 按模型汇总的统计数据\n")
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估翻译质量')
    parser.add_argument('--data-dir', type=str,
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/translation_quality',
                       help='输出目录')
    parser.add_argument('--no-bertscore', action='store_true',
                       help='禁用BERTScore')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_translation_quality(
        data_dir,
        output_dir,
        use_bertscore=not args.no_bertscore
    )
