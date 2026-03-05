#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复评估脚本的输出路径

将所有评估脚本的默认输出路径统一为:
data/analize/results/{task}_quality/

作者: Kiro AI Assistant
日期: 2026-03-05
"""

from pathlib import Path
import re

SCRIPTS_DIR = Path(__file__).parent

# 需要修复的脚本和对应的输出目录
SCRIPTS_TO_FIX = {
    'evaluate_code_quality.py': 'code_quality',
    'evaluate_creative_quality.py': 'creative_quality',
    'evaluate_math_quality.py': 'math_quality',
    'evaluate_qa_quality.py': 'qa_quality',
    'evaluate_qa_quality_academic.py': 'qa_quality_academic',
    'evaluate_reasoning_quality.py': 'reasoning_quality',
    'evaluate_summary_quality.py': 'summary_quality',
    'evaluate_summary_bartscore.py': 'summary_quality',
    'evaluate_translation_quality.py': 'translation_quality',
}

def fix_script_paths(script_name, output_dir):
    """修复单个脚本的输出路径"""
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        print(f"⚠️  脚本不存在: {script_name}")
        return False
    
    try:
        # 读取脚本内容
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复 --output-dir 的默认值
        # 匹配模式: default='data/analize/pre_data' 或类似路径
        pattern1 = r"(--output-dir.*?default=)['\"]([^'\"]*)['\"]"
        replacement1 = rf"\1'data/analize/results/{output_dir}'"
        content = re.sub(pattern1, replacement1, content)
        
        # 修复直接定义的输出目录
        # 匹配模式: output_dir = Path('...')
        pattern2 = r"(output_dir\s*=\s*Path\()['\"]([^'\"]*)['\"](\))"
        replacement2 = rf"\1'data/analize/results/{output_dir}'\3"
        content = re.sub(pattern2, replacement2, content)
        
        # 修复 data_dir 的默认值
        pattern3 = r"(--data-dir.*?default=)['\"]([^'\"]*)['\"]"
        replacement3 = r"\1'data/analize/pre_data'"
        content = re.sub(pattern3, replacement3, content)
        
        # 修复直接定义的数据目录
        pattern4 = r"(data_dir\s*=\s*Path\()['\"]([^'\"]*comparison_matrices[^'\"]*)['\"](\))"
        replacement4 = r"\1'data/analize/pre_data/comparison_matrices/...'\3"
        # 这个需要保留原有的子路径，所以不做替换
        
        if content != original_content:
            # 写回文件
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 已修复: {script_name}")
            return True
        else:
            print(f"ℹ️  无需修复: {script_name}")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败 {script_name}: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🔧 修复评估脚本输出路径")
    print("="*80 + "\n")
    
    fixed_count = 0
    skipped_count = 0
    failed_count = 0
    
    for script_name, output_dir in SCRIPTS_TO_FIX.items():
        print(f"\n处理: {script_name} -> results/{output_dir}/")
        result = fix_script_paths(script_name, output_dir)
        
        if result is True:
            fixed_count += 1
        elif result is False:
            skipped_count += 1
        else:
            failed_count += 1
    
    print("\n" + "="*80)
    print("📊 修复摘要")
    print("="*80)
    print(f"✅ 已修复: {fixed_count} 个脚本")
    print(f"ℹ️  无需修复: {skipped_count} 个脚本")
    print(f"❌ 修复失败: {failed_count} 个脚本")
    print("="*80 + "\n")
    
    if fixed_count > 0:
        print("✅ 路径修复完成!")
        print("\n建议:")
        print("1. 检查修复后的脚本是否正常工作")
        print("2. 运行测试: python run_all_evaluations.py --list")
        print("3. 提交更改到版本控制")
    else:
        print("ℹ️  所有脚本路径已是最新")


if __name__ == '__main__':
    main()
