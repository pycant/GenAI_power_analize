#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版 FLORES-200 下载脚本
直接从 Hugging Face 下载预处理好的数据
"""

import json
import sys
from pathlib import Path

try:
    from datasets import load_dataset
except ImportError:
    print("错误: 缺少 datasets 库")
    print("请运行: pip install datasets")
    sys.exit(1)


def download_flores200_simple():
    """
    下载 FLORES-200 devtest 数据集（简化版）
    """
    print("="*70)
    print("FLORES-200 下载工具（简化版）")
    print("="*70)
    
    output_dir = Path("data/benchmarks/flores200")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n📥 下载 FLORES-200 devtest 数据集...")
    print("提示: 使用预处理版本避免编码问题")
    
    try:
        # 使用 devtest 分割，指定具体语言对
        print("\n1. 下载英语-简体中文语言对...")
        dataset_en_zh = load_dataset(
            "facebook/flores",
            "eng_Latn-zho_Hans",
            split="devtest",
            trust_remote_code=True
        )
        
        # 保存为 JSON
        output_file = output_dir / "flores200_eng_zho_Hans.json"
        data = []
        for item in dataset_en_zh:
            data.append({
                "id": item.get("id", len(data)),
                "source": item.get("sentence_eng_Latn", ""),
                "target": item.get("sentence_zho_Hans", ""),
                "source_lang": "eng_Latn",
                "target_lang": "zho_Hans"
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 已保存: {output_file}")
        print(f"  句子对数量: {len(data)}")
        
        # 下载英语-繁体中文
        print("\n2. 下载英语-繁体中文语言对...")
        dataset_en_zht = load_dataset(
            "facebook/flores",
            "eng_Latn-zho_Hant",
            split="devtest",
            trust_remote_code=True
        )
        
        output_file = output_dir / "flores200_eng_zho_Hant.json"
        data = []
        for item in dataset_en_zht:
            data.append({
                "id": item.get("id", len(data)),
                "source": item.get("sentence_eng_Latn", ""),
                "target": item.get("sentence_zho_Hant", ""),
                "source_lang": "eng_Latn",
                "target_lang": "zho_Hant"
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 已保存: {output_file}")
        print(f"  句子对数量: {len(data)}")
        
        print("\n" + "="*70)
        print("✅ FLORES-200 下载完成！")
        print("="*70)
        print(f"\n数据集位置: {output_dir}")
        print("\n可用文件:")
        for f in output_dir.glob("*.json"):
            print(f"  - {f.name}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(download_flores200_simple())
