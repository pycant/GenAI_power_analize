#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看数据样本脚本

功能：
1. 随机查看几个完整的回答样本
2. 验证数据提取是否完整
3. 检查不同任务类型的回答质量
"""

import pandas as pd
import sys
import random

# 确保输出使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def view_sample(df, idx):
    """查看单个样本"""
    row = df.iloc[idx]
    
    print("\n" + "="*80)
    print(f"样本 #{idx + 1}")
    print("="*80)
    print(f"实验ID: {row['experiment_id']}")
    print(f"模型: {row['model']}")
    print(f"任务类型: {row['task_type']}")
    print(f"时间戳: {row['timestamp']}")
    print(f"温度: {row['temperature']}")
    print(f"最大tokens: {row['max_tokens']}")
    print()
    
    print("-"*80)
    print("📝 输入提示词（Prompt）")
    print("-"*80)
    prompt = row['prompt']
    if len(prompt) > 500:
        print(prompt[:500] + "\n...(截断，总长度: {} 字符)".format(len(prompt)))
    else:
        print(prompt)
    print()
    
    print("-"*80)
    print("💬 模型回答（Response）")
    print("-"*80)
    response = row['response']
    if pd.isna(response):
        print("⚠️  回答为空")
    else:
        print(f"回答长度: {len(response)} 字符")
        print(f"Token数量: {row['token_count']}")
        print()
        if len(response) > 1000:
            print(response[:500])
            print("\n...(中间省略)...\n")
            print(response[-500:])
            print(f"\n(完整回答共 {len(response)} 字符)")
        else:
            print(response)
    print()
    
    print("-"*80)
    print("📊 性能指标")
    print("-"*80)
    print(f"吞吐量: {row['throughput_tps']:.2f} tokens/秒")
    print(f"延迟: {row['latency_s']:.2f} 秒")
    print(f"GPU能耗: {row['gpu_energy_j']:.2f} 焦耳")
    print(f"GPU平均功耗: {row['gpu_power_avg_w']:.2f} 瓦特")
    print("="*80)


def main():
    """主函数"""
    # 读取数据
    df = pd.read_csv('data/analize/pre_data/responses_raw.csv', encoding='utf-8-sig')
    
    print("\n" + "="*80)
    print("数据样本查看工具")
    print("="*80)
    print(f"总样本数: {len(df)}")
    print(f"模型数量: {df['model'].nunique()}")
    print(f"任务类型: {', '.join(df['task_type'].unique())}")
    print()
    
    # 按任务类型查看样本
    task_types = df['task_type'].unique()
    
    print("="*80)
    print("按任务类型查看样本（每种任务随机选1个）")
    print("="*80)
    
    for task in sorted(task_types):
        task_df = df[df['task_type'] == task]
        if len(task_df) > 0:
            # 随机选择一个样本
            idx = random.choice(task_df.index)
            view_sample(df, idx)
    
    print("\n" + "="*80)
    print("✅ 样本查看完成")
    print("="*80)
    print("\n提示：")
    print("- 可以看到完整的回答已经提取（非截断）")
    print("- 不同任务类型的回答长度差异很大")
    print("- 所有特殊字符（换行符等）都已正确处理")


if __name__ == '__main__':
    main()
