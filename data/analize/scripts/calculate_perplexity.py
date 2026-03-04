#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
困惑度（Perplexity）计算脚本

使用预训练语言模型计算生成文本的困惑度，评估流畅性。
支持多种模型：GPT-2, GPT-2-Chinese, BERT等

作者：Kiro AI Assistant
日期：2026-03-04
"""

import pandas as pd
import numpy as np
import torch
from pathlib import Path
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForMaskedLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  transformers 未安装，请运行: pip install transformers torch")


class PerplexityCalculator:
    """困惑度计算器"""
    
    def __init__(self, model_name='gpt2', device='cuda'):
        """
        初始化困惑度计算器
        
        Args:
            model_name: 预训练模型名称
                - 'gpt2': 英文GPT-2（小型，124M）
                - 'gpt2-medium': 英文GPT-2（中型，355M）
                - 'uer/gpt2-chinese-cluecorpussmall': 中文GPT-2
                - 'bert-base-chinese': 中文BERT（需要特殊处理）
            device: 'cuda' 或 'cpu'
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("需要安装 transformers 和 torch")
        
        self.model_name = model_name
        self.device = device if torch.cuda.is_available() else 'cpu'
        
        print(f"📦 加载模型: {model_name}")
        print(f"🖥️  设备: {self.device}")
        
        # 加载分词器和模型
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # 判断模型类型
            if 'gpt' in model_name.lower():
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                self.model_type = 'causal'
            elif 'bert' in model_name.lower():
                self.model = AutoModelForMaskedLM.from_pretrained(model_name)
                self.model_type = 'masked'
            else:
                # 默认尝试因果语言模型
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                self.model_type = 'causal'
            
            self.model.to(self.device)
            self.model.eval()
            
            print(f"✅ 模型加载成功 (类型: {self.model_type})")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            raise
    
    def calculate_perplexity_causal(self, text, max_length=512):
        """
        计算因果语言模型的困惑度（GPT系列）
        
        Args:
            text: 输入文本
            max_length: 最大序列长度
        
        Returns:
            float: 困惑度值
        """
        if not text or not text.strip():
            return float('inf')
        
        try:
            # 分词
            encodings = self.tokenizer(
                text,
                return_tensors='pt',
                max_length=max_length,
                truncation=True,
                padding=False
            )
            
            input_ids = encodings.input_ids.to(self.device)
            
            # 计算损失
            with torch.no_grad():
                outputs = self.model(input_ids, labels=input_ids)
                loss = outputs.loss
            
            # 困惑度 = exp(loss)
            perplexity = torch.exp(loss).item()
            
            return perplexity
            
        except Exception as e:
            print(f"⚠️  计算困惑度失败: {e}")
            return float('inf')
    
    def calculate_perplexity_masked(self, text, max_length=512):
        """
        计算掩码语言模型的困惑度（BERT系列）
        
        使用伪似然估计（Pseudo-Likelihood）方法
        
        Args:
            text: 输入文本
            max_length: 最大序列长度
        
        Returns:
            float: 困惑度值
        """
        if not text or not text.strip():
            return float('inf')
        
        try:
            # 分词
            encodings = self.tokenizer(
                text,
                return_tensors='pt',
                max_length=max_length,
                truncation=True,
                padding=False
            )
            
            input_ids = encodings.input_ids.to(self.device)
            
            # 逐个掩码计算
            total_loss = 0.0
            num_tokens = input_ids.size(1)
            
            with torch.no_grad():
                for i in range(1, num_tokens - 1):  # 跳过[CLS]和[SEP]
                    # 创建掩码版本
                    masked_input = input_ids.clone()
                    original_token = masked_input[0, i].item()
                    masked_input[0, i] = self.tokenizer.mask_token_id
                    
                    # 预测
                    outputs = self.model(masked_input)
                    logits = outputs.logits[0, i]
                    
                    # 计算交叉熵损失
                    loss = torch.nn.functional.cross_entropy(
                        logits.unsqueeze(0),
                        torch.tensor([original_token]).to(self.device)
                    )
                    
                    total_loss += loss.item()
            
            # 平均损失
            avg_loss = total_loss / (num_tokens - 2)
            
            # 困惑度
            perplexity = np.exp(avg_loss)
            
            return perplexity
            
        except Exception as e:
            print(f"⚠️  计算困惑度失败: {e}")
            return float('inf')
    
    def calculate_perplexity(self, text, max_length=512):
        """
        计算困惑度（自动选择方法）
        
        Args:
            text: 输入文本
            max_length: 最大序列长度
        
        Returns:
            float: 困惑度值
        """
        if self.model_type == 'causal':
            return self.calculate_perplexity_causal(text, max_length)
        elif self.model_type == 'masked':
            return self.calculate_perplexity_masked(text, max_length)
        else:
            raise ValueError(f"未知模型类型: {self.model_type}")
    
    def calculate_batch_perplexity(self, texts, max_length=512, batch_size=8):
        """
        批量计算困惑度
        
        Args:
            texts: 文本列表
            max_length: 最大序列长度
            batch_size: 批次大小
        
        Returns:
            list: 困惑度列表
        """
        perplexities = []
        
        for i in tqdm(range(0, len(texts), batch_size), desc="计算困惑度"):
            batch_texts = texts[i:i+batch_size]
            
            for text in batch_texts:
                ppl = self.calculate_perplexity(text, max_length)
                perplexities.append(ppl)
        
        return perplexities


def add_perplexity_to_creative_scores(
    input_file='data/analize/results/creative_quality/creative_quality_scores_detailed.csv',
    output_file='data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv',
    model_name='uer/gpt2-chinese-cluecorpussmall',
    device='cuda'
):
    """
    为创意写作评分添加困惑度指标
    
    Args:
        input_file: 输入CSV文件
        output_file: 输出CSV文件
        model_name: 预训练模型名称
        device: 计算设备
    """
    print("="*60)
    print("为创意写作评分添加困惑度指标")
    print("="*60)
    
    # 加载数据
    print(f"\n📂 加载数据: {input_file}")
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    print(f"✅ 加载完成: {len(df)} 条记录")
    
    # 加载回答文本
    responses_file = Path('data/analize/pre_data/comparison_matrices/creative/creative_responses.csv')
    if not responses_file.exists():
        print(f"❌ 回答文件不存在: {responses_file}")
        return
    
    responses_df = pd.read_csv(responses_file, encoding='utf-8-sig', index_col=0)
    
    # 初始化困惑度计算器
    try:
        calculator = PerplexityCalculator(model_name=model_name, device=device)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        print("\n💡 建议:")
        print("   1. 安装依赖: pip install transformers torch")
        print("   2. 首次运行会下载模型（约500MB），需要网络连接")
        print("   3. 如果网络受限，可以使用更小的模型: 'gpt2'")
        return
    
    # 计算困惑度
    print("\n🔍 计算困惑度...")
    perplexities = []
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="处理"):
        model = row['model']
        question_id = row['question_id']
        
        # 获取回答文本
        if model in responses_df.index and question_id in responses_df.columns:
            text = responses_df.loc[model, question_id]
            
            if pd.notna(text) and text.strip():
                ppl = calculator.calculate_perplexity(text)
            else:
                ppl = float('inf')
        else:
            ppl = float('inf')
        
        perplexities.append(ppl)
    
    # 添加到数据框
    df['perplexity'] = perplexities
    
    # 处理无穷大值
    finite_ppls = [p for p in perplexities if np.isfinite(p)]
    if finite_ppls:
        max_finite_ppl = max(finite_ppls) * 2  # 用2倍最大值替代无穷大
        df['perplexity'] = df['perplexity'].replace([np.inf, -np.inf], max_finite_ppl)
    
    # 保存结果
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ 结果已保存: {output_path}")
    
    # 统计信息
    print("\n📊 困惑度统计:")
    print(f"   平均值: {df['perplexity'].mean():.2f}")
    print(f"   中位数: {df['perplexity'].median():.2f}")
    print(f"   最小值: {df['perplexity'].min():.2f}")
    print(f"   最大值: {df['perplexity'].max():.2f}")
    
    # 按模型统计
    print("\n🏆 各模型平均困惑度（越低越好）:")
    model_ppl = df.groupby('model')['perplexity'].mean().sort_values()
    for i, (model, ppl) in enumerate(model_ppl.head(10).items(), 1):
        print(f"   {i}. {model}: {ppl:.2f}")
    
    print("\n" + "="*60)
    print("✅ 困惑度计算完成！")
    print("="*60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='计算创意写作的困惑度')
    parser.add_argument('--input', type=str,
                       default='data/analize/results/creative_quality/creative_quality_scores_detailed.csv',
                       help='输入CSV文件')
    parser.add_argument('--output', type=str,
                       default='data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv',
                       help='输出CSV文件')
    parser.add_argument('--model', type=str,
                       default='uer/gpt2-chinese-cluecorpussmall',
                       choices=[
                           'gpt2',
                           'gpt2-medium',
                           'uer/gpt2-chinese-cluecorpussmall',
                           'bert-base-chinese'
                       ],
                       help='预训练模型名称')
    parser.add_argument('--device', type=str,
                       default='cuda',
                       choices=['cuda', 'cpu'],
                       help='计算设备')
    
    args = parser.parse_args()
    
    add_perplexity_to_creative_scores(
        input_file=args.input,
        output_file=args.output,
        model_name=args.model,
        device=args.device
    )


if __name__ == '__main__':
    main()
