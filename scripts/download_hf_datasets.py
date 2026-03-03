#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
使用 Hugging Face datasets 下载完整测试集

需要安装: pip install datasets
"""

import argparse
import json
import sys
from pathlib import Path

try:
    from datasets import load_dataset
except ImportError:
    print("错误: 缺少 datasets 库")
    print("请运行: pip install datasets")
    sys.exit(1)


def download_flores200(output_dir: Path, language_pairs: list = None):
    """
    下载 FLORES-200 数据集
    
    Args:
        output_dir: 输出目录
        language_pairs: 语言对列表，如 ['eng_Latn', 'zho_Hans']
    """
    print("\n" + "="*70)
    print("下载 FLORES-200 (多语言翻译)")
    print("="*70)
    
    flores_dir = output_dir / "flores200"
    flores_dir.mkdir(parents=True, exist_ok=True)
    
    # 默认语言
    if language_pairs is None:
        language_pairs = [
            "eng_Latn",   # 英语
            "zho_Hans",   # 简体中文
            "zho_Hant",   # 繁体中文
        ]
    
    print(f"\n📥 下载 FLORES-200 数据集...")
    
    try:
        # 下载完整数据集（包含所有语言）
        dataset = load_dataset("facebook/flores", "all", trust_remote_code=True)
        
        # 保存 devtest 分割
        print(f"\n处理 devtest 分割...")
        
        # 获取所有数据
        devtest_data = dataset['devtest']
        
        # 按语言保存
        for lang in language_pairs:
            if f"sentence_{lang}" in devtest_data.column_names:
                output_file = flores_dir / f"flores200_{lang}.json"
                
                # 提取该语言的句子
                data = []
                for i, item in enumerate(devtest_data):
                    data.append({
                        "id": item.get("id", i),
                        "sentence": item[f"sentence_{lang}"],
                        "language": lang,
                        "url": item.get("URL", ""),
                        "domain": item.get("domain", "")
                    })
                
                # 保存
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"✓ 已保存: {output_file}")
                print(f"  句子数量: {len(data)}")
            else:
                print(f"✗ 语言 {lang} 不在数据集中")
        
        # 创建语言对文件（英中对照）
        if "sentence_eng_Latn" in devtest_data.column_names and "sentence_zho_Hans" in devtest_data.column_names:
            output_file = flores_dir / "flores200_eng_zho_Hans_pairs.json"
            
            pairs = []
            for i, item in enumerate(devtest_data):
                pairs.append({
                    "id": item.get("id", i),
                    "source": item["sentence_eng_Latn"],
                    "target": item["sentence_zho_Hans"],
                    "source_lang": "eng_Latn",
                    "target_lang": "zho_Hans",
                    "domain": item.get("domain", "")
                })
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(pairs, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ 已保存语言对: {output_file}")
            print(f"  句子对数量: {len(pairs)}")
        
    except Exception as e:
        print(f"✗ 下载失败: {e}")
        import traceback
        traceback.print_exc()
    
    return flores_dir


def download_mmlu(output_dir: Path, subjects: list = None, split: str = "test"):
    """
    下载 MMLU 数据集
    
    Args:
        output_dir: 输出目录
        subjects: 学科列表，None 表示全部
        split: 数据集分割 ('test', 'validation', 'dev')
    """
    print("\n" + "="*70)
    print("下载 MMLU (多学科知识)")
    print("="*70)
    
    mmlu_dir = output_dir / "mmlu"
    mmlu_dir.mkdir(parents=True, exist_ok=True)
    
    # 如果没有指定学科，下载所有学科
    if subjects is None:
        print("\n提示: 下载所有 57 个学科可能需要较长时间...")
        print("建议先下载部分学科进行测试")
        
        # 推荐的学科子集
        subjects = [
            "abstract_algebra",
            "anatomy",
            "astronomy",
            "college_biology",
            "college_chemistry",
            "college_computer_science",
            "college_mathematics",
            "college_physics",
            "computer_security",
            "high_school_biology",
            "high_school_chemistry",
            "high_school_computer_science",
            "high_school_mathematics",
            "high_school_physics",
            "machine_learning",
        ]
        print(f"下载 {len(subjects)} 个 STEM 学科...")
    
    for subject in subjects:
        print(f"\n📥 下载学科: {subject}")
        
        try:
            # 下载数据集
            dataset = load_dataset("cais/mmlu", subject, trust_remote_code=True)
            
            # 保存指定分割
            output_file = mmlu_dir / f"mmlu_{subject}_{split}.json"
            
            # 转换为列表格式
            data = []
            for item in dataset[split]:
                data.append(item)
            
            # 保存
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ 已保存: {output_file}")
            print(f"  题目数量: {len(data)}")
            
        except Exception as e:
            print(f"✗ 下载失败: {e}")
    
    return mmlu_dir


def main():
    parser = argparse.ArgumentParser(
        description="使用 Hugging Face datasets 下载完整测试集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载 FLORES-200 英中语言对
  python download_hf_datasets.py --flores200
  
  # 下载 MMLU STEM 学科
  python download_hf_datasets.py --mmlu
  
  # 下载所有
  python download_hf_datasets.py --flores200 --mmlu
  
  # 指定输出目录
  python download_hf_datasets.py --flores200 --output-dir data/my_datasets
        """
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/benchmarks",
        help="输出目录 (默认: data/benchmarks)"
    )
    
    parser.add_argument(
        "--flores200",
        action="store_true",
        help="下载 FLORES-200"
    )
    
    parser.add_argument(
        "--mmlu",
        action="store_true",
        help="下载 MMLU"
    )
    
    parser.add_argument(
        "--language-pairs",
        nargs="+",
        help="FLORES-200 语言对，如: eng_Latn-zho_Hans"
    )
    
    parser.add_argument(
        "--mmlu-subjects",
        nargs="+",
        help="MMLU 学科列表"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    
    print("="*70)
    print("Hugging Face 数据集下载工具")
    print("="*70)
    print(f"输出目录: {output_dir}")
    
    if not args.flores200 and not args.mmlu:
        parser.print_help()
        return 1
    
    try:
        if args.flores200:
            download_flores200(output_dir, args.language_pairs)
        
        if args.mmlu:
            download_mmlu(output_dir, args.mmlu_subjects)
        
        print("\n" + "="*70)
        print("✅ 下载完成！")
        print("="*70)
        print(f"\n数据集位置: {output_dir}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  下载已取消")
        return 1
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
