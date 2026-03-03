#!/usr/bin/env python3
"""
为所有 HuggingFace 模型创建 4-bit 和 8-bit 量化配置
"""

import json
import sys
from pathlib import Path
import shutil

# 定义需要处理的 HF 模型
HF_MODELS = [
    {
        'name': 'phi3_mini_hf',
        'display_name': 'Phi-3 Mini 3.8B',
        'original_model': 'hf:models/huggingface/microsoft--phi-3-mini-4k-instruct',
        'size': '3.8B'
    },
    {
        'name': 'qwen25_3b_hf',
        'display_name': 'Qwen 2.5 3B',
        'original_model': 'hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct',
        'size': '3B'
    },
    {
        'name': 'qwen25_7b_hf',
        'display_name': 'Qwen 2.5 7B',
        'original_model': 'hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct',
        'size': '7B'
    }
]

def split_model_config(model_info):
    """为单个模型创建 4-bit 和 8-bit 配置"""
    
    model_name = model_info['name']
    display_name = model_info['display_name']
    original_model = model_info['original_model']
    
    # 读取原始配置
    source_dir = Path(f"data/experiments_{model_name}")
    source_file = source_dir / "test_cases.json"
    
    if not source_file.exists():
        print(f"⚠️  跳过 {display_name}: 找不到配置文件 {source_file}")
        return False
    
    with open(source_file, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"\n{'='*60}")
    print(f"处理模型: {display_name}")
    print(f"{'='*60}")
    print(f"✓ 读取到 {len(test_cases)} 个测试用例")
    
    # 创建 4-bit 配置
    test_cases_4bit = []
    for case in test_cases:
        case_4bit = case.copy()
        case_4bit['model'] = f"{original_model}:4bit"
        case_4bit['quantization'] = "4bit"
        test_cases_4bit.append(case_4bit)
    
    # 创建 8-bit 配置
    test_cases_8bit = []
    for case in test_cases:
        case_8bit = case.copy()
        case_8bit['model'] = f"{original_model}:8bit"
        case_8bit['quantization'] = "8bit"
        test_cases_8bit.append(case_8bit)
    
    # 保存 4-bit 配置
    output_4bit_dir = Path(f"data/experiments_{model_name}_4bit")
    output_4bit_dir.mkdir(parents=True, exist_ok=True)
    output_4bit = output_4bit_dir / "test_cases.json"
    
    with open(output_4bit, 'w', encoding='utf-8') as f:
        json.dump(test_cases_4bit, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已生成 4-bit 配置: {output_4bit}")
    print(f"  - 模型: {original_model}:4bit")
    
    # 保存 8-bit 配置
    output_8bit_dir = Path(f"data/experiments_{model_name}_8bit")
    output_8bit_dir.mkdir(parents=True, exist_ok=True)
    output_8bit = output_8bit_dir / "test_cases.json"
    
    with open(output_8bit, 'w', encoding='utf-8') as f:
        json.dump(test_cases_8bit, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 已生成 8-bit 配置: {output_8bit}")
    print(f"  - 模型: {original_model}:8bit")
    
    return True

def main():
    """处理所有 HF 模型"""
    
    print("="*60)
    print("HuggingFace 模型量化配置生成器")
    print("="*60)
    print(f"\n将为 {len(HF_MODELS)} 个 HF 模型创建 4-bit 和 8-bit 配置\n")
    
    success_count = 0
    failed_count = 0
    
    for model_info in HF_MODELS:
        try:
            if split_model_config(model_info):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"❌ 处理 {model_info['display_name']} 时出错: {e}")
            failed_count += 1
    
    # 统计信息
    print(f"\n{'='*60}")
    print("处理完成统计")
    print(f"{'='*60}")
    print(f"✓ 成功: {success_count} 个模型")
    print(f"✗ 失败: {failed_count} 个模型")
    print(f"📊 总计生成: {success_count * 2} 个配置文件 ({success_count} × 2 量化级别)")
    
    if success_count > 0:
        print(f"\n{'='*60}")
        print("生成的配置目录")
        print(f"{'='*60}")
        for model_info in HF_MODELS:
            model_name = model_info['name']
            print(f"\n{model_info['display_name']}:")
            print(f"  - data/experiments_{model_name}_4bit/")
            print(f"  - data/experiments_{model_name}_8bit/")
        
        print(f"\n{'='*60}")
        print("运行实验示例")
        print(f"{'='*60}")
        print("\n# 4-bit 量化")
        for model_info in HF_MODELS:
            model_name = model_info['name']
            print(f"python experiments/experiment_runner.py \\")
            print(f"  --config data/experiments_{model_name}_4bit/test_cases.json \\")
            print(f"  --output-dir data/experiments_{model_name}_4bit \\")
            print(f"  --skip-bartscore\n")
        
        print("# 8-bit 量化")
        for model_info in HF_MODELS:
            model_name = model_info['name']
            print(f"python experiments/experiment_runner.py \\")
            print(f"  --config data/experiments_{model_name}_8bit/test_cases.json \\")
            print(f"  --output-dir data/experiments_{model_name}_8bit \\")
            print(f"  --skip-bartscore\n")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
