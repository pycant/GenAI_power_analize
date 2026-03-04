#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创意写作任务质量评估脚本

根据 quality_evaluation_system.md 设计，评估创意写作任务的多维度质量指标：
- 多样性：Distinct-1, Distinct-2
- 流畅性：文本长度、句子数
- 创造力：独特表达、修辞手法

作者：Kiro AI Assistant
日期：2026-03-04
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
from collections import Counter
import warnings
warnings.filterwarnings('ignore')


class CreativeQualityEvaluator:
    """创意写作质量评估器"""
    
    def __init__(self):
        self.metrics = {}
    
    def tokenize_chinese(self, text):
        """简单的中文分词（基于字符和标点）"""
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 分离标点符号
        text = re.sub(r'([，。！？；：、""''（）《》【】])', r' \1 ', text)
        # 分词：中文按字，英文按词
        tokens = []
        for word in text.split():
            if re.match(r'[a-zA-Z]+', word):
                tokens.append(word.lower())
            elif re.match(r'[\u4e00-\u9fff]', word):
                tokens.extend(list(word))
            elif word.strip():
                tokens.append(word)
        return [t for t in tokens if t.strip()]
    
    def calculate_distinct_n(self, tokens, n=2):
        """
        计算 Distinct-N 指标
        
        Args:
            tokens: 分词列表
            n: N-gram 大小
        
        Returns:
            float: Distinct-N 分数 [0, 1]
        """
        if len(tokens) < n:
            return 0.0
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = tuple(tokens[i:i+n])
            ngrams.append(ngram)
        
        if not ngrams:
            return 0.0
        
        unique_ngrams = len(set(ngrams))
        total_ngrams = len(ngrams)
        
        return unique_ngrams / total_ngrams
    
    def count_rhetorical_devices(self, text):
        """
        检测修辞手法（简化版）
        
        Returns:
            dict: 修辞手法计数
        """
        devices = {
            'metaphor': 0,      # 比喻
            'personification': 0,  # 拟人
            'repetition': 0,    # 重复
            'parallelism': 0    # 排比
        }
        
        # 比喻标志词
        metaphor_markers = ['像', '如', '似', '仿佛', '好像', '犹如', '宛如']
        for marker in metaphor_markers:
            devices['metaphor'] += text.count(marker)
        
        # 拟人标志（动词+非生物主语）
        personification_markers = ['微笑', '哭泣', '歌唱', '舞蹈', '低语', '呼唤', '拥抱']
        for marker in personification_markers:
            devices['personification'] += text.count(marker)
        
        # 重复（连续相同词）
        tokens = self.tokenize_chinese(text)
        for i in range(len(tokens) - 1):
            if tokens[i] == tokens[i+1] and len(tokens[i]) > 1:
                devices['repetition'] += 1
        
        # 排比（简化：检测句式重复）
        sentences = re.split(r'[。！？；]', text)
        sentence_starts = [s.strip()[:2] for s in sentences if len(s.strip()) > 2]
        start_counts = Counter(sentence_starts)
        devices['parallelism'] = sum(1 for count in start_counts.values() if count >= 2)
        
        return devices
    
    def evaluate_single_response(self, text, question_id):
        """
        评估单个回答
        
        Args:
            text: 生成文本
            question_id: 问题ID
        
        Returns:
            dict: 质量指标
        """
        if pd.isna(text) or not text.strip():
            return {
                'question_id': question_id,
                'distinct_1': 0.0,
                'distinct_2': 0.0,
                'text_length': 0,
                'sentence_count': 0,
                'avg_sentence_length': 0.0,
                'token_count': 0,
                'unique_token_ratio': 0.0,
                'metaphor_count': 0,
                'personification_count': 0,
                'repetition_count': 0,
                'parallelism_count': 0,
                'total_rhetorical_devices': 0
            }
        
        # 分词
        tokens = self.tokenize_chinese(text)
        
        # 基础统计
        text_length = len(text)
        sentences = [s.strip() for s in re.split(r'[。！？；]', text) if s.strip()]
        sentence_count = len(sentences)
        avg_sentence_length = text_length / sentence_count if sentence_count > 0 else 0
        
        # 多样性指标
        distinct_1 = self.calculate_distinct_n(tokens, n=1)
        distinct_2 = self.calculate_distinct_n(tokens, n=2)
        
        # 词汇丰富度
        token_count = len(tokens)
        unique_tokens = len(set(tokens))
        unique_token_ratio = unique_tokens / token_count if token_count > 0 else 0
        
        # 修辞手法
        rhetorical = self.count_rhetorical_devices(text)
        
        return {
            'question_id': question_id,
            'distinct_1': round(distinct_1, 4),
            'distinct_2': round(distinct_2, 4),
            'text_length': text_length,
            'sentence_count': sentence_count,
            'avg_sentence_length': round(avg_sentence_length, 2),
            'token_count': token_count,
            'unique_token_ratio': round(unique_token_ratio, 4),
            'metaphor_count': rhetorical['metaphor'],
            'personification_count': rhetorical['personification'],
            'repetition_count': rhetorical['repetition'],
            'parallelism_count': rhetorical['parallelism'],
            'total_rhetorical_devices': sum(rhetorical.values())
        }
    
    def evaluate_model(self, model_name, responses_df):
        """
        评估单个模型的所有回答
        
        Args:
            model_name: 模型名称
            responses_df: 回答数据框（行=模型，列=问题）
        
        Returns:
            pd.DataFrame: 质量评估结果
        """
        if model_name not in responses_df.index:
            print(f"⚠️  模型 {model_name} 不在数据中")
            return None
        
        model_responses = responses_df.loc[model_name]
        results = []
        
        for question_id in responses_df.columns:
            response_text = model_responses[question_id]
            metrics = self.evaluate_single_response(response_text, question_id)
            metrics['model'] = model_name
            results.append(metrics)
        
        return pd.DataFrame(results)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='创意写作质量评估')
    parser.add_argument('--with-perplexity', action='store_true',
                       help='计算困惑度（需要额外时间和GPU）')
    parser.add_argument('--perplexity-model', type=str,
                       default='uer/gpt2-chinese-cluecorpussmall',
                       help='困惑度计算使用的模型')
    
    args = parser.parse_args()
    
    print("="*60)
    print("创意写作任务质量评估")
    print("="*60)
    
    # 路径配置
    data_dir = Path('data/analize/pre_data/comparison_matrices/creative')
    output_dir = Path('data/analize/results/creative_quality')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    print("\n📂 加载数据...")
    responses_file = data_dir / 'creative_responses.csv'
    prompts_file = data_dir / 'creative_prompts.csv'
    
    if not responses_file.exists():
        print(f"❌ 文件不存在: {responses_file}")
        return
    
    responses_df = pd.read_csv(responses_file, encoding='utf-8-sig', index_col=0)
    prompts_df = pd.read_csv(prompts_file, encoding='utf-8-sig')
    
    print(f"✅ 加载完成")
    print(f"   - 模型数量: {len(responses_df)}")
    print(f"   - 问题数量: {len(responses_df.columns)}")
    
    # 初始化评估器
    evaluator = CreativeQualityEvaluator()
    
    # 评估所有模型
    print("\n🔍 开始评估...")
    all_results = []
    
    for model_name in responses_df.index:
        print(f"   评估模型: {model_name}")
        model_results = evaluator.evaluate_model(model_name, responses_df)
        if model_results is not None:
            all_results.append(model_results)
    
    # 合并结果
    if not all_results:
        print("❌ 没有评估结果")
        return
    
    final_df = pd.concat(all_results, ignore_index=True)
    
    # 保存详细结果
    detail_file = output_dir / 'creative_quality_scores_detailed.csv'
    final_df.to_csv(detail_file, index=False, encoding='utf-8-sig')
    print(f"\n✅ 详细结果已保存: {detail_file}")
    
    # 生成汇总统计
    print("\n📊 生成汇总统计...")
    summary_stats = final_df.groupby('model').agg({
        'distinct_1': ['mean', 'std'],
        'distinct_2': ['mean', 'std'],
        'text_length': ['mean', 'std'],
        'sentence_count': ['mean', 'std'],
        'unique_token_ratio': ['mean', 'std'],
        'total_rhetorical_devices': ['mean', 'std']
    }).round(4)
    
    summary_stats.columns = ['_'.join(col).strip() for col in summary_stats.columns.values]
    summary_file = output_dir / 'creative_quality_summary.csv'
    summary_stats.to_csv(summary_file, encoding='utf-8-sig')
    print(f"✅ 汇总统计已保存: {summary_file}")
    
    # 打印关键指标排名
    print("\n🏆 关键指标排名（按均值）:")
    print("\n1. Distinct-2（多样性，越高越好）:")
    top_distinct2 = final_df.groupby('model')['distinct_2'].mean().sort_values(ascending=False).head(5)
    for i, (model, score) in enumerate(top_distinct2.items(), 1):
        print(f"   {i}. {model}: {score:.4f}")
    
    print("\n2. 独特词汇比例（词汇丰富度，越高越好）:")
    top_unique = final_df.groupby('model')['unique_token_ratio'].mean().sort_values(ascending=False).head(5)
    for i, (model, score) in enumerate(top_unique.items(), 1):
        print(f"   {i}. {model}: {score:.4f}")
    
    print("\n3. 修辞手法总数（创造力，越高越好）:")
    top_rhetorical = final_df.groupby('model')['total_rhetorical_devices'].mean().sort_values(ascending=False).head(5)
    for i, (model, score) in enumerate(top_rhetorical.items(), 1):
        print(f"   {i}. {model}: {score:.2f}")
    
    # 生成任务-模型匹配分析
    print("\n🎯 生成任务-模型匹配分析...")
    matching_results = []
    
    for question_id in final_df['question_id'].unique():
        question_data = final_df[final_df['question_id'] == question_id]
        
        # 每个指标的Top 3模型
        metrics = ['distinct_2', 'unique_token_ratio', 'total_rhetorical_devices']
        for metric in metrics:
            top3 = question_data.nlargest(3, metric)[['model', metric]]
            for rank, (idx, row) in enumerate(top3.iterrows(), 1):
                matching_results.append({
                    'question_id': question_id,
                    'metric': metric,
                    'rank': rank,
                    'model': row['model'],
                    'score': row[metric]
                })
    
    matching_df = pd.DataFrame(matching_results)
    matching_file = output_dir / 'creative_task_model_matching.csv'
    matching_df.to_csv(matching_file, index=False, encoding='utf-8-sig')
    print(f"✅ 任务-模型匹配已保存: {matching_file}")
    
    print("\n" + "="*60)
    print("✅ 创意写作质量评估完成！")
    print("="*60)
    print(f"\n输出文件:")
    print(f"  1. {detail_file}")
    print(f"  2. {summary_file}")
    print(f"  3. {matching_file}")
    
    # 可选：计算困惑度
    if args.with_perplexity:
        print("\n" + "="*60)
        print("📊 计算困惑度（可能需要几分钟）...")
        print("="*60)
        
        try:
            from calculate_perplexity import add_perplexity_to_creative_scores
            
            add_perplexity_to_creative_scores(
                input_file=str(detail_file),
                output_file=str(output_dir / 'creative_quality_scores_with_perplexity.csv'),
                model_name=args.perplexity_model,
                device='cuda'
            )
        except ImportError:
            print("⚠️  困惑度计算需要安装 transformers 和 torch")
            print("   运行: pip install transformers torch")
        except Exception as e:
            print(f"⚠️  困惑度计算失败: {e}")
            print("   可以稍后单独运行: python calculate_perplexity.py")


if __name__ == '__main__':
    main()
