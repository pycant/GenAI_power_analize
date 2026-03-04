#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
困惑度（Perplexity）计算脚本 - 使用本地模型版本

使用本地已下载的模型计算困惑度，避免网络下载

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
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️  transformers 未安装")


class LocalPerplexityCalculator:
    """使用本地模型的困惑度计算器"""
    
    def __init__(self, model_path, device='cuda'):
        """
        初始化困惑度计算器
        
        Args:
            model_path: 本地模型路径（如 'models/huggingface/Qwen--Qwen2.5-3B-Instruct'）
            device: 'cuda' 或 'cpu'
        """
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("需要安装 transformers 和 torch")
        
        self.model_path = model_path
        self.device = device if torch.cuda.is_available() else 'cpu'
        
        print(f"📦 加载本地模型: {model_path}")
        print(f"🖥️  设备: {self.device}")
        
        try:
            # 从本地加载
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=True
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                local_files_only=True,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            print(f"✅ 模型加载成功")
            
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            raise
    
    def calculate_perplexity(self, text, max_length=512):
        """
        计算困惑度
        
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
    
    def calculate_batch_perplexity(self, texts, max_length=512):
        """
        批量计算困惑度
        
        Args:
            texts: 文本列表
            max_length: 最大序列长度
        
        Returns:
            list: 困惑度列表
        """
        perplexities = []
        
        for text in tqdm(texts, desc="计算困惑度"):
            ppl = self.calculate_perplexity(text, max_length)
            perplexities.append(ppl)
        
        return perplexities


def add_perplexity_to_creative_scores_local(
    input_file='data/analize/results/creative_quality/creative_quality_scores_detailed.csv',
    output_file='data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv',
    model_path='models/huggingface/Qwen--Qwen2.5-3B-Instruct',
    device='cuda'
):
    """
    为创意写作评分添加困惑度指标（使用本地模型）
    
    Args:
        input_file: 输入CSV文件
        output_file: 输出CSV文件
        model_path: 本地模型路径
        device: 计算设备
    """
    print("="*60)
    print("为创意写作评分添加困惑度指标（本地模型）")
    print("="*60)
    
    # 检查模型路径
    model_path = Path(model_path)
    if not model_path.exists():
        print(f"❌ 模型路径不存在: {model_path}")
        print("\n可用的本地模型:")
        hf_dir = Path('models/huggingface')
        if hf_dir.exists():
            for model_dir in hf_dir.iterdir():
                if model_dir.is_dir():
                    print(f"   - {model_dir}")
        return
    
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
        calculator = LocalPerplexityCalculator(model_path=str(model_path), device=device)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
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
        max_finite_ppl = max(finite_ppls) * 2
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
    
    parser = argparse.ArgumentParser(description='计算创意写作的困惑度（本地模型）')
    parser.add_argument('--input', type=str,
                       default='data/analize/results/creative_quality/creative_quality_scores_detailed.csv',
                       help='输入CSV文件')
    parser.add_argument('--output', type=str,
                       default='data/analize/results/creative_quality/creative_quality_scores_with_perplexity.csv',
                       help='输出CSV文件')
    parser.add_argument('--model-path', type=str,
                       default='models/huggingface/Qwen--Qwen2.5-3B-Instruct',
                       help='本地模型路径')
    parser.add_argument('--device', type=str,
                       default='cuda',
                       choices=['cuda', 'cpu'],
                       help='计算设备')
    
    args = parser.parse_args()
    
    add_perplexity_to_creative_scores_local(
        input_file=args.input,
        output_file=args.output,
        model_path=args.model_path,
        device=args.device
    )


if __name__ == '__main__':
    main()
