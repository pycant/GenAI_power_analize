#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试BARTScore安装是否成功"""

import sys
import os

# 添加BARTScore目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../BARTScore'))

try:
    from bart_score import BARTScorer
    print("✓ 成功导入BARTScorer")
    
    # 初始化BARTScorer
    print("正在初始化BARTScorer...")
    bart_scorer = BARTScorer(device='cpu', checkpoint='facebook/bart-large-cnn')
    print("✓ BARTScorer初始化成功")
    
    # 测试评分
    print("\n测试评分功能...")
    srcs = ['This is a very good idea.']
    tgts = ['That is an excellent idea.']
    
    scores = bart_scorer.score(srcs, tgts, batch_size=1)
    print(f"✓ 评分成功！得分: {scores}")
    print(f"  说明: 分数为负值，值越高（越接近0）表示质量越好")
    
    # 测试多参考评分
    print("\n测试多参考评分功能...")
    srcs = ["I'm super happy today."]
    tgts = [["I feel good today.", "I feel sad today."]]
    
    multi_scores = bart_scorer.multi_ref_score(srcs, tgts, agg="max", batch_size=1)
    print(f"✓ 多参考评分成功！得分: {multi_scores}")
    
    print("\n" + "="*50)
    print("BARTScore安装测试完成！所有功能正常。")
    print("="*50)
    
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
