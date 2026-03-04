#!/usr/bin/env python3
"""
标准化实验目录命名
命名规范: {模型名}_{参数量}_{平台}_{量化}
"""

import json
import shutil
from pathlib import Path
import sys

# 定义重命名映射
RENAME_MAP = {
    # Ollama 模型
    'experiments_gemma3': 'gemma_4b_ol_q4km',
    'experiments_qwen3_4b': 'qwen_4b_ol_q4km',
    'experiments_qwen3_8b': 'qwen_8b_ol_q4km',
    'experiments_deepseek_r1_8b': 'deepseek_8b_ol_q4km',
    
    # HuggingFace 模型 - Gemma
    'experiments_gemma_2b_hf_4bit': 'gemma_2b_hf_4bit',
    'experiments_gemma_2b_hf_8bit': 'gemma_2b_hf_8bit',
    
    # HuggingFace 模型 - Phi-3
    'experiments_phi3_mini_hf_4bit': 'phi3_4b_hf_4bit',
    'experiments_phi3_mini_hf_8bit': 'phi3_4b_hf_8bit',
    
    # HuggingFace 模型 - Qwen 2.5
    'experiments_qwen25_3b_hf_4bit': 'qwen25_3b_hf_4bit',
    'experiments_qwen25_3b_hf_8bit': 'qwen25_3b_hf_8bit',
    'experiments_qwen25_7b_hf_4bit': 'qwen25_7b_hf_4bit',
    'experiments_qwen25_7b_hf_8bit': 'qwen25_7b_hf_8bit',
}

def rename_directories(dry_run=True):
    """重命名实验目录"""
    
    data_dir = Path("data")
    renamed_count = 0
    skipped_count = 0
    
    print("="*60)
    print("实验目录标准化重命名")
    print("="*60)
    print(f"模式: {'预览模式（不实际重命名）' if dry_run else '执行模式（实际重命名）'}")
    print()
    
    for old_name, new_name in RENAME_MAP.items():
        old_path = data_dir / old_name
        new_path = data_dir / new_name
        
        if not old_path.exists():
            print(f"⚠️  跳过: {old_name} (目录不存在)")
            skipped_count += 1
            continue
        
        if new_path.exists() and new_path != old_path:
            print(f"⚠️  跳过: {old_name} -> {new_name} (目标已存在)")
            skipped_count += 1
            continue
        
        if old_name == new_name:
            print(f"✓ 已标准: {old_name}")
            continue
        
        print(f"{'[预览]' if dry_run else '[执行]'} {old_name} -> {new_name}")
        
        if not dry_run:
            try:
                old_path.rename(new_path)
                print(f"  ✓ 重命名成功")
                renamed_count += 1
            except Exception as e:
                print(f"  ❌ 重命名失败: {e}")
                skipped_count += 1
        else:
            renamed_count += 1
    
    print()
    print("="*60)
    print("统计")
    print("="*60)
    print(f"✓ {'将要重命名' if dry_run else '已重命名'}: {renamed_count} 个目录")
    print(f"⚠️  跳过: {skipped_count} 个目录")
    
    return renamed_count, skipped_count

def update_batch_script(dry_run=True):
    """更新批处理脚本中的路径"""
    
    batch_file = Path("scripts/run_all_experiments_complete.bat")
    
    if not batch_file.exists():
        print(f"\n⚠️  批处理脚本不存在: {batch_file}")
        return False
    
    print()
    print("="*60)
    print("更新批处理脚本")
    print("="*60)
    
    with open(batch_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 替换所有路径
    for old_name, new_name in RENAME_MAP.items():
        content = content.replace(f"data/{old_name}/", f"data/{new_name}/")
        content = content.replace(f"data\\{old_name}\\", f"data\\{new_name}\\")
    
    if content == original_content:
        print("✓ 批处理脚本无需更新")
        return True
    
    if dry_run:
        print("[预览] 批处理脚本将被更新")
        # 显示部分变更
        changes = []
        for old_name, new_name in RENAME_MAP.items():
            if old_name in original_content:
                changes.append(f"  {old_name} -> {new_name}")
        if changes:
            print("变更预览:")
            for change in changes[:5]:  # 只显示前5个
                print(change)
            if len(changes) > 5:
                print(f"  ... 还有 {len(changes) - 5} 个变更")
    else:
        with open(batch_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✓ 批处理脚本已更新")
    
    return True

def update_documentation(dry_run=True):
    """更新文档中的路径"""
    
    doc_files = [
        "EXPERIMENT_STATUS.md",
        "QUANTIZATION_QUICK_REFERENCE.md",
        "docs/QUANTIZATION_EXPERIMENTS_COMPLETE.md",
        "docs/GEMMA_QUANTIZATION_SPLIT.md",
        "README_EXPERIMENTS.md",
    ]
    
    print()
    print("="*60)
    print("更新文档")
    print("="*60)
    
    updated_count = 0
    
    for doc_file in doc_files:
        doc_path = Path(doc_file)
        
        if not doc_path.exists():
            print(f"⚠️  跳过: {doc_file} (文件不存在)")
            continue
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 替换所有路径
        for old_name, new_name in RENAME_MAP.items():
            content = content.replace(f"data/{old_name}/", f"data/{new_name}/")
            content = content.replace(f"data\\{old_name}\\", f"data\\{new_name}\\")
            content = content.replace(f"`{old_name}`", f"`{new_name}`")
            content = content.replace(f"experiments_{old_name.replace('experiments_', '')}", new_name)
        
        if content == original_content:
            print(f"✓ 无需更新: {doc_file}")
            continue
        
        if dry_run:
            print(f"[预览] 将更新: {doc_file}")
        else:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 已更新: {doc_file}")
            updated_count += 1
    
    print(f"\n{'将要更新' if dry_run else '已更新'} {updated_count} 个文档")
    
    return True

def show_new_structure():
    """显示新的目录结构"""
    
    print()
    print("="*60)
    print("标准化后的目录结构")
    print("="*60)
    print()
    print("命名规范: {模型名}_{参数量}_{平台}_{量化}")
    print()
    print("Ollama 模型 (ol = Ollama, q4km = Q4_K_M):")
    print("  - gemma_4b_ol_q4km/")
    print("  - qwen_4b_ol_q4km/")
    print("  - qwen_8b_ol_q4km/")
    print("  - deepseek_8b_ol_q4km/")
    print()
    print("HuggingFace 模型 (hf = HuggingFace):")
    print("  Gemma 2B:")
    print("    - gemma_2b_hf_4bit/")
    print("    - gemma_2b_hf_8bit/")
    print("  Phi-3 Mini 3.8B:")
    print("    - phi3_4b_hf_4bit/")
    print("    - phi3_4b_hf_8bit/")
    print("  Qwen 2.5 3B:")
    print("    - qwen25_3b_hf_4bit/")
    print("    - qwen25_3b_hf_8bit/")
    print("  Qwen 2.5 7B:")
    print("    - qwen25_7b_hf_4bit/")
    print("    - qwen25_7b_hf_8bit/")
    print()

def main():
    """主函数"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description='标准化实验目录命名')
    parser.add_argument('--execute', action='store_true', 
                       help='实际执行重命名（默认为预览模式）')
    parser.add_argument('--show-structure', action='store_true',
                       help='只显示新的目录结构')
    
    args = parser.parse_args()
    
    if args.show_structure:
        show_new_structure()
        return 0
    
    dry_run = not args.execute
    
    if dry_run:
        print()
        print("⚠️  当前为预览模式，不会实际修改文件")
        print("⚠️  使用 --execute 参数执行实际重命名")
        print()
    else:
        print()
        print("⚠️  警告：将实际执行重命名操作！")
        response = input("确认继续？(yes/no): ")
        if response.lower() != 'yes':
            print("已取消")
            return 0
        print()
    
    # 1. 重命名目录
    renamed, skipped = rename_directories(dry_run)
    
    # 2. 更新批处理脚本
    update_batch_script(dry_run)
    
    # 3. 更新文档
    update_documentation(dry_run)
    
    # 4. 显示新结构
    show_new_structure()
    
    if dry_run:
        print()
        print("="*60)
        print("预览完成")
        print("="*60)
        print("如果确认无误，请运行:")
        print("  python scripts/standardize_experiment_names.py --execute")
    else:
        print()
        print("="*60)
        print("重命名完成！")
        print("="*60)
        print("✓ 所有实验目录已标准化")
        print("✓ 批处理脚本已更新")
        print("✓ 文档已更新")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
