#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
标准测试集下载脚本

支持下载以下数据集：
1. FLORES-200 (多语言翻译)
2. HumanEval (代码生成)
3. GSM8K (数学推理)
4. MMLU (多学科知识)
"""

import argparse
import json
import os
import sys
import urllib.request
import zipfile
import tarfile
from pathlib import Path
from typing import Optional, List, Dict
import shutil

class BenchmarkDownloader:
    """标准测试集下载器"""
    
    def __init__(self, output_dir: str = "data/benchmarks"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def download_file(self, url: str, output_path: Path, desc: str = ""):
        """下载文件"""
        print(f"📥 下载 {desc}...")
        print(f"   URL: {url}")
        print(f"   目标: {output_path}")
        
        try:
            urllib.request.urlretrieve(url, output_path)
            print(f"   ✓ 下载完成")
            return True
        except Exception as e:
            print(f"   ✗ 下载失败: {e}")
            return False
    
    def extract_archive(self, archive_path: Path, extract_to: Path):
        """解压文件"""
        print(f"📦 解压 {archive_path.name}...")
        
        try:
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
            elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_to)
            
            print(f"   ✓ 解压完成")
            return True
        except Exception as e:
            print(f"   ✗ 解压失败: {e}")
            return False
    
    def download_flores200(self, sample_size: Optional[int] = None):
        """
        下载 FLORES-200 数据集
        
        Args:
            sample_size: 采样大小（每个语言对的句子数），None 表示全部
        """
        print("\n" + "="*70)
        print("下载 FLORES-200 (多语言翻译)")
        print("="*70)
        
        flores_dir = self.output_dir / "flores200"
        flores_dir.mkdir(parents=True, exist_ok=True)
        
        # FLORES-200 devtest 数据集 URL
        # 注意：这是简化版本，完整版本需要从 Hugging Face 下载
        print("\n提示: FLORES-200 完整数据集较大，建议使用 Hugging Face datasets 库下载")
        print("这里提供简化的下载方法...")
        
        # 创建示例说明文件
        readme_content = """# FLORES-200 数据集

## 下载方法

### 方法 1: 使用 Hugging Face datasets（推荐）

```python
from datasets import load_dataset

# 下载 FLORES-200 devtest
dataset = load_dataset("facebook/flores", "zho_Hans-eng")

# 保存为 JSON
dataset['devtest'].to_json('flores200_zh_en.json')
```

### 方法 2: 从 GitHub 下载

访问: https://github.com/facebookresearch/flores/tree/main/flores200

## 语言对

常用语言对：
- eng_Latn (英语) ↔ zho_Hans (简体中文)
- eng_Latn (英语) ↔ zho_Hant (繁体中文)
- eng_Latn (英语) ↔ jpn_Jpan (日语)
- eng_Latn (英语) ↔ kor_Hang (韩语)

## 数据格式

每个语言对包含约 1,012 个句子对。

## 使用示例

```python
import json

# 加载数据
with open('flores200_zh_en.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍历句子对
for item in data:
    source = item['sentence_eng_Latn']
    target = item['sentence_zho_Hans']
    print(f"EN: {source}")
    print(f"ZH: {target}")
```
"""
        
        readme_path = flores_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"\n✓ 已创建说明文件: {readme_path}")
        print("\n建议使用 Hugging Face datasets 库下载完整数据集")
        
        return flores_dir

    
    def download_humaneval(self):
        """下载 HumanEval 数据集"""
        print("\n" + "="*70)
        print("下载 HumanEval (代码生成)")
        print("="*70)
        
        humaneval_dir = self.output_dir / "humaneval"
        humaneval_dir.mkdir(parents=True, exist_ok=True)
        
        # HumanEval 数据集 URL
        url = "https://github.com/openai/human-eval/raw/master/data/HumanEval.jsonl.gz"
        output_file = humaneval_dir / "HumanEval.jsonl.gz"
        
        if output_file.exists():
            print(f"⚠️  文件已存在: {output_file}")
            return humaneval_dir
        
        # 下载数据
        if self.download_file(url, output_file, "HumanEval 数据集"):
            # 解压
            import gzip
            jsonl_file = humaneval_dir / "HumanEval.jsonl"
            with gzip.open(output_file, 'rb') as f_in:
                with open(jsonl_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            print(f"✓ 已解压到: {jsonl_file}")
            
            # 读取并显示统计信息
            problems = []
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    problems.append(json.loads(line))
            
            print(f"\n📊 数据集统计:")
            print(f"   题目数量: {len(problems)}")
            print(f"   示例题目: {problems[0]['task_id']}")
            
            return humaneval_dir
        
        return None
    
    def download_gsm8k(self, split: str = "test"):
        """
        下载 GSM8K 数据集
        
        Args:
            split: 数据集分割 ('train' 或 'test')
        """
        print("\n" + "="*70)
        print("下载 GSM8K (数学推理)")
        print("="*70)
        
        gsm8k_dir = self.output_dir / "gsm8k"
        gsm8k_dir.mkdir(parents=True, exist_ok=True)
        
        # GSM8K 数据集 URL
        base_url = "https://github.com/openai/grade-school-math/raw/master/grade_school_math/data"
        
        splits_to_download = [split] if split != "all" else ["train", "test"]
        
        for split_name in splits_to_download:
            url = f"{base_url}/{split_name}.jsonl"
            output_file = gsm8k_dir / f"{split_name}.jsonl"
            
            if output_file.exists():
                print(f"⚠️  文件已存在: {output_file}")
                continue
            
            if self.download_file(url, output_file, f"GSM8K {split_name} 数据集"):
                # 读取并显示统计信息
                problems = []
                with open(output_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        problems.append(json.loads(line))
                
                print(f"\n📊 {split_name} 数据集统计:")
                print(f"   题目数量: {len(problems)}")
                if problems:
                    print(f"   示例问题: {problems[0]['question'][:100]}...")
        
        return gsm8k_dir
    
    def download_mmlu(self, subjects: Optional[List[str]] = None):
        """
        下载 MMLU 数据集
        
        Args:
            subjects: 要下载的学科列表，None 表示全部
        """
        print("\n" + "="*70)
        print("下载 MMLU (多学科知识)")
        print("="*70)
        
        mmlu_dir = self.output_dir / "mmlu"
        mmlu_dir.mkdir(parents=True, exist_ok=True)
        
        # MMLU 数据集较大，建议使用 Hugging Face datasets
        print("\n提示: MMLU 数据集包含 57 个学科，建议使用 Hugging Face datasets 库下载")
        
        # 创建示例说明文件
        readme_content = """# MMLU 数据集

## 下载方法

### 使用 Hugging Face datasets（推荐）

```python
from datasets import load_dataset

# 下载完整 MMLU 数据集
dataset = load_dataset("cais/mmlu", "all")

# 或下载特定学科
dataset = load_dataset("cais/mmlu", "abstract_algebra")

# 保存为 JSON
dataset['test'].to_json('mmlu_test.json')
```

### 可用学科（57 个）

#### STEM
- abstract_algebra, anatomy, astronomy, college_biology, 
  college_chemistry, college_computer_science, college_mathematics,
  college_physics, computer_security, conceptual_physics,
  electrical_engineering, elementary_mathematics, high_school_biology,
  high_school_chemistry, high_school_computer_science,
  high_school_mathematics, high_school_physics, high_school_statistics,
  machine_learning

#### 人文
- formal_logic, high_school_european_history, high_school_us_history,
  high_school_world_history, international_law, jurisprudence,
  logical_fallacies, moral_disputes, moral_scenarios, philosophy,
  prehistory, professional_law, world_religions

#### 社会科学
- econometrics, high_school_geography, high_school_government_and_politics,
  high_school_macroeconomics, high_school_microeconomics,
  high_school_psychology, human_sexuality, professional_psychology,
  public_relations, security_studies, sociology, us_foreign_policy

#### 其他
- business_ethics, clinical_knowledge, college_medicine, global_facts,
  human_aging, management, marketing, medical_genetics, miscellaneous,
  nutrition, professional_accounting, professional_medicine, virology

## 数据格式

每个题目包含：
- question: 问题文本
- choices: 4 个选项 (A, B, C, D)
- answer: 正确答案索引 (0-3)

## 使用示例

```python
import json

# 加载数据
with open('mmlu_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍历题目
for item in data:
    print(f"Q: {item['question']}")
    for i, choice in enumerate(item['choices']):
        print(f"  {chr(65+i)}. {choice}")
    print(f"A: {chr(65+item['answer'])}")
```

## 评估方法

MMLU 使用 5-shot 评估：
1. 提供 5 个示例题目
2. 让模型回答测试题目
3. 计算准确率
"""
        
        readme_path = mmlu_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"\n✓ 已创建说明文件: {readme_path}")
        print("\n建议使用 Hugging Face datasets 库下载完整数据集")
        
        return mmlu_dir
    
    def create_sample_datasets(self):
        """创建示例数据集用于快速测试"""
        print("\n" + "="*70)
        print("创建示例数据集")
        print("="*70)
        
        samples_dir = self.output_dir / "samples"
        samples_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. HumanEval 示例
        humaneval_sample = [
            {
                "task_id": "HumanEval/0",
                "prompt": "from typing import List\n\n\ndef has_close_elements(numbers: List[float], threshold: float) -> bool:\n    \"\"\" Check if in given list of numbers, are any two numbers closer to each other than\n    given threshold.\n    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)\n    False\n    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)\n    True\n    \"\"\"\n",
                "entry_point": "has_close_elements",
                "canonical_solution": "    for idx, elem in enumerate(numbers):\n        for idx2, elem2 in enumerate(numbers):\n            if idx != idx2:\n                distance = abs(elem - elem2)\n                if distance < threshold:\n                    return True\n\n    return False\n",
                "test": "def check(candidate):\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.3) == True\n    assert candidate([1.0, 2.0, 3.9, 4.0, 5.0, 2.2], 0.05) == False\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.95) == True\n    assert candidate([1.0, 2.0, 5.9, 4.0, 5.0], 0.8) == False\n    assert candidate([1.0, 2.0, 3.0, 4.0, 5.0, 2.0], 0.1) == True\n"
            }
        ]
        
        humaneval_path = samples_dir / "humaneval_sample.json"
        with open(humaneval_path, 'w', encoding='utf-8') as f:
            json.dump(humaneval_sample, f, indent=2, ensure_ascii=False)
        print(f"✓ 创建 HumanEval 示例: {humaneval_path}")
        
        # 2. GSM8K 示例
        gsm8k_sample = [
            {
                "question": "Natalia sold clips to 48 of her friends in April, and then she sold half as many clips in May. How many clips did Natalia sell altogether in April and May?",
                "answer": "Natalia sold 48/2 = <<48/2=24>>24 clips in May.\nNatalia sold 48+24 = <<48+24=72>>72 clips altogether in April and May.\n#### 72"
            },
            {
                "question": "Weng earns $12 an hour for babysitting. Yesterday, she just did 50 minutes of babysitting. How much did she earn?",
                "answer": "Weng earns 12/60 = $<<12/60=0.2>>0.2 per minute.\nWorking 50 minutes, she earned 0.2 x 50 = $<<0.2*50=10>>10.\n#### 10"
            }
        ]
        
        gsm8k_path = samples_dir / "gsm8k_sample.json"
        with open(gsm8k_path, 'w', encoding='utf-8') as f:
            json.dump(gsm8k_sample, f, indent=2, ensure_ascii=False)
        print(f"✓ 创建 GSM8K 示例: {gsm8k_path}")
        
        # 3. MMLU 示例
        mmlu_sample = [
            {
                "question": "What is the embryological origin of the hyoid bone?",
                "subject": "anatomy",
                "choices": [
                    "The first pharyngeal arch",
                    "The first and second pharyngeal arches",
                    "The second pharyngeal arch",
                    "The second and third pharyngeal arches"
                ],
                "answer": 3
            },
            {
                "question": "Which of the following is not a way to form recombinant DNA?",
                "subject": "college_biology",
                "choices": [
                    "Translation",
                    "Conjugation",
                    "Specialized transduction",
                    "Transformation"
                ],
                "answer": 0
            }
        ]
        
        mmlu_path = samples_dir / "mmlu_sample.json"
        with open(mmlu_path, 'w', encoding='utf-8') as f:
            json.dump(mmlu_sample, f, indent=2, ensure_ascii=False)
        print(f"✓ 创建 MMLU 示例: {mmlu_path}")
        
        # 4. FLORES-200 示例
        flores_sample = [
            {
                "id": 1,
                "sentence_eng_Latn": "The Internet combines elements of both mass and interpersonal communication.",
                "sentence_zho_Hans": "互联网结合了大众传播和人际交流的元素。"
            },
            {
                "id": 2,
                "sentence_eng_Latn": "The distinct characteristics of the Internet lead to additional dimensions in terms of the uses and gratifications approach.",
                "sentence_zho_Hans": "互联网的独特特征在使用和满足方法方面带来了额外的维度。"
            }
        ]
        
        flores_path = samples_dir / "flores200_sample.json"
        with open(flores_path, 'w', encoding='utf-8') as f:
            json.dump(flores_sample, f, indent=2, ensure_ascii=False)
        print(f"✓ 创建 FLORES-200 示例: {flores_path}")
        
        print(f"\n✓ 所有示例数据集已创建在: {samples_dir}")
        
        return samples_dir


def main():
    parser = argparse.ArgumentParser(
        description="下载标准测试集数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载所有数据集
  python download_benchmark_datasets.py --all
  
  # 下载特定数据集
  python download_benchmark_datasets.py --humaneval --gsm8k
  
  # 仅创建示例数据集
  python download_benchmark_datasets.py --samples-only
  
  # 指定输出目录
  python download_benchmark_datasets.py --all --output-dir data/my_benchmarks
        """
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/benchmarks",
        help="输出目录 (默认: data/benchmarks)"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="下载所有数据集"
    )
    
    parser.add_argument(
        "--flores200",
        action="store_true",
        help="下载 FLORES-200 (多语言翻译)"
    )
    
    parser.add_argument(
        "--humaneval",
        action="store_true",
        help="下载 HumanEval (代码生成)"
    )
    
    parser.add_argument(
        "--gsm8k",
        action="store_true",
        help="下载 GSM8K (数学推理)"
    )
    
    parser.add_argument(
        "--mmlu",
        action="store_true",
        help="下载 MMLU (多学科知识)"
    )
    
    parser.add_argument(
        "--samples-only",
        action="store_true",
        help="仅创建示例数据集（用于快速测试）"
    )
    
    args = parser.parse_args()
    
    # 创建下载器
    downloader = BenchmarkDownloader(output_dir=args.output_dir)
    
    print("="*70)
    print("标准测试集下载工具")
    print("="*70)
    print(f"输出目录: {args.output_dir}")
    
    # 如果只创建示例
    if args.samples_only:
        downloader.create_sample_datasets()
        print("\n✅ 示例数据集创建完成！")
        return 0
    
    # 确定要下载的数据集
    download_all = args.all
    download_flores = args.flores200 or download_all
    download_humaneval = args.humaneval or download_all
    download_gsm8k = args.gsm8k or download_all
    download_mmlu = args.mmlu or download_all
    
    # 如果没有指定任何数据集，显示帮助
    if not any([download_flores, download_humaneval, download_gsm8k, download_mmlu]):
        parser.print_help()
        print("\n提示: 使用 --samples-only 创建示例数据集进行快速测试")
        return 1
    
    # 下载数据集
    try:
        if download_flores:
            downloader.download_flores200()
        
        if download_humaneval:
            downloader.download_humaneval()
        
        if download_gsm8k:
            downloader.download_gsm8k(split="test")
        
        if download_mmlu:
            downloader.download_mmlu()
        
        # 创建示例数据集
        print("\n")
        downloader.create_sample_datasets()
        
        print("\n" + "="*70)
        print("✅ 下载完成！")
        print("="*70)
        print(f"\n数据集位置: {args.output_dir}")
        print("\n下一步:")
        print("1. 查看各数据集的 README.md 了解使用方法")
        print("2. 使用 samples/ 目录中的示例数据进行快速测试")
        print("3. 根据需要使用 Hugging Face datasets 下载完整数据集")
        
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
