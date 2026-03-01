#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试 HF 模型生成功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.model_deployment.hf_loader import HuggingFaceModelLoader

def test_hf_generation():
    """测试 HF 模型生成"""
    print("\n" + "="*60)
    print("测试 Hugging Face 模型生成")
    print("="*60 + "\n")
    
    # 初始化加载器
    loader = HuggingFaceModelLoader()
    
    # 模型路径
    model_path = "models/huggingface/Qwen--Qwen2.5-7B-Instruct"
    
    try:
        # 加载模型
        print("步骤 1: 加载模型...")
        model, tokenizer = loader.load_model(
            model_path,
            quantize="4bit",
            device="auto"
        )
        
        # 测试生成
        print("\n步骤 2: 测试生成...")
        prompt = "你好，请用一句话介绍人工智能。"
        print(f"输入: {prompt}")
        
        generated_text = loader.generate(
            model,
            tokenizer,
            prompt,
            max_new_tokens=50,
            temperature=0.7,
            top_p=0.9,
            do_sample=True
        )
        
        print(f"\n生成结果:")
        print(f"{generated_text}")
        
        print("\n" + "="*60)
        print("✓ 测试成功！")
        print("="*60)
        return 0
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ 测试失败")
        print("="*60)
        print(f"\n错误: {e}")
        
        import traceback
        print("\n详细错误信息:")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_hf_generation())
