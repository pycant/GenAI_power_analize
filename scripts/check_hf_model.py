#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查 Hugging Face 模型是否存在
"""

import os
import sys
from pathlib import Path

def check_model_exists(model_path):
    """检查模型文件是否存在"""
    model_path = Path(model_path)
    
    print(f"\n{'='*60}")
    print(f"检查模型: {model_path}")
    print(f"{'='*60}\n")
    
    # 检查路径是否存在
    if not model_path.exists():
        print(f"❌ 模型路径不存在: {model_path}")
        print(f"   绝对路径: {model_path.resolve()}")
        return False
    
    print(f"✓ 模型路径存在: {model_path}")
    print(f"  绝对路径: {model_path.resolve()}")
    
    # 检查必需的文件
    required_files = [
        "config.json",
        "tokenizer_config.json",
        "tokenizer.json"
    ]
    
    model_files = [
        "model.safetensors",
        "pytorch_model.bin",
        "model.safetensors.index.json",
        "pytorch_model.bin.index.json"
    ]
    
    print("\n检查必需文件:")
    all_required_exist = True
    for file in required_files:
        file_path = model_path / file
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} (缺失)")
            all_required_exist = False
    
    print("\n检查模型文件 (至少需要一个):")
    model_file_exists = False
    for file in model_files:
        file_path = model_path / file
        if file_path.exists():
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ {file} ({size_mb:.2f} MB)")
            model_file_exists = True
        else:
            print(f"  - {file} (不存在)")
    
    if not model_file_exists:
        print("\n❌ 没有找到模型权重文件")
        return False
    
    if not all_required_exist:
        print("\n⚠️  缺少必需的配置文件")
        return False
    
    # 列出所有文件
    print("\n模型目录内容:")
    try:
        files = list(model_path.iterdir())
        for f in sorted(files)[:20]:  # 只显示前20个
            if f.is_file():
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"  - {f.name} ({size_mb:.2f} MB)")
            else:
                print(f"  - {f.name}/ (目录)")
        
        if len(files) > 20:
            print(f"  ... 还有 {len(files) - 20} 个文件/目录")
    except Exception as e:
        print(f"  ❌ 无法列出目录内容: {e}")
    
    print("\n✓ 模型文件完整，可以使用")
    return True

def main():
    """主函数"""
    # 检查常见的模型路径
    model_paths = [
        "models/huggingface/Qwen--Qwen2.5-7B-Instruct",
        "models/huggingface/Qwen/Qwen2.5-7B-Instruct",
    ]
    
    print("\n" + "="*60)
    print("Hugging Face 模型检查工具")
    print("="*60)
    
    # 检查 models 目录
    models_dir = Path("models/huggingface")
    if not models_dir.exists():
        print(f"\n❌ models/huggingface 目录不存在")
        print(f"   请先创建目录: mkdir -p models/huggingface")
        return 1
    
    print(f"\n✓ models/huggingface 目录存在")
    
    # 列出已下载的模型
    print("\n已下载的模型:")
    try:
        subdirs = [d for d in models_dir.iterdir() if d.is_dir()]
        if subdirs:
            for d in subdirs:
                print(f"  - {d.name}")
        else:
            print("  (无)")
    except Exception as e:
        print(f"  ❌ 无法列出目录: {e}")
    
    # 检查指定的模型
    found_any = False
    for model_path in model_paths:
        if check_model_exists(model_path):
            found_any = True
    
    if not found_any:
        print("\n" + "="*60)
        print("❌ 没有找到可用的模型")
        print("="*60)
        print("\n请使用以下命令下载模型:")
        print("\n  python scripts/download_hf_model.py \\")
        print("    --model Qwen/Qwen2.5-7B-Instruct \\")
        print("    --output-dir models/huggingface \\")
        print("    --quantize 4bit")
        print("\n或者使用批量下载:")
        print("\n  python scripts/batch_download_models.py \\")
        print("    --config configs/models_to_download.yaml")
        return 1
    
    print("\n" + "="*60)
    print("✓ 模型检查完成")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
