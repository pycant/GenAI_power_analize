#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
困惑度计算测试脚本

快速测试困惑度计算功能是否正常工作

作者：Kiro AI Assistant
日期：2026-03-04
"""

import sys
from pathlib import Path

# 测试文本
test_texts = {
    "流畅文本": "春天来了，万物复苏。小鸟在枝头歌唱，花朵在阳光下绽放。",
    "诗歌": "融化的是冰川不是春天，在光的上游，柳枝弯腰探视暗涌的光痕。",
    "重复文本": "好好好好好好好好好好好好好好好好好好好好好好好好好好。",
    "乱码": "asdf qwer zxcv 1234 !@#$ 测试 test 混合 mix"
}

def test_perplexity():
    """测试困惑度计算"""
    print("="*60)
    print("困惑度计算测试")
    print("="*60)
    
    # 检查依赖
    try:
        import torch
        import transformers
        print("\n✅ 依赖检查通过")
        print(f"   PyTorch: {torch.__version__}")
        print(f"   Transformers: {transformers.__version__}")
        print(f"   CUDA 可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"\n❌ 依赖缺失: {e}")
        print("\n请安装依赖:")
        print("   pip install transformers torch")
        return
    
    # 导入计算器
    try:
        from calculate_perplexity import PerplexityCalculator
    except ImportError:
        print("\n❌ 无法导入 calculate_perplexity 模块")
        print("   请确保 calculate_perplexity.py 在同一目录")
        return
    
    # 测试不同模型
    models_to_test = [
        ('gpt2', 'CPU'),  # 英文模型，快速测试
    ]
    
    # 如果有GPU，测试中文模型
    if torch.cuda.is_available():
        models_to_test.append(('uer/gpt2-chinese-cluecorpussmall', 'CUDA'))
    
    for model_name, device in models_to_test:
        print(f"\n{'='*60}")
        print(f"测试模型: {model_name}")
        print(f"设备: {device}")
        print(f"{'='*60}")
        
        try:
            # 初始化
            calculator = PerplexityCalculator(
                model_name=model_name,
                device=device.lower()
            )
            
            # 测试每个文本
            print("\n测试结果:")
            for name, text in test_texts.items():
                ppl = calculator.calculate_perplexity(text)
                print(f"  {name:12s}: {ppl:8.2f}")
            
            print("\n✅ 测试通过")
            
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    
    print("\n💡 使用建议:")
    print("   1. 流畅文本的困惑度应该较低（< 100）")
    print("   2. 重复文本和乱码的困惑度应该较高（> 200）")
    print("   3. 中文模型评估中文文本更准确")
    print("   4. 如果所有困惑度都很高，可能是模型选择不当")


if __name__ == '__main__':
    test_perplexity()
