#!/usr/bin/env python3
"""
为测试用例添加语言类型标注

功能：
- 自动识别任务的语言类型
- 添加 language_type 和 languages 字段
- 为代码任务添加 programming_language 字段
- 保持原有数据结构不变
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any


def infer_language_type(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据任务信息推断语言类型
    
    Args:
        task: 任务字典
        
    Returns:
        更新后的任务字典
    """
    task_type = task.get('task_type', '')
    language = task.get('language', 'en')
    
    # 翻译任务
    if task_type == 'translation':
        task['language_type'] = 'cross-lingual'
        source_lang = task.get('source_lang', 'en')
        target_lang = task.get('target_lang', 'zh')
        task['languages'] = [source_lang, target_lang]
        
    # 代码任务
    elif task_type == 'code':
        task['language_type'] = 'code'
        task['languages'] = [language]
        # 推断编程语言（默认 Python）
        if 'programming_language' not in task:
            task['programming_language'] = 'python'
            
    # 混合语言任务
    elif language == 'mixed':
        # 检查是否是翻译任务（可能没有正确标记）
        if 'source_lang' in task and 'target_lang' in task:
            task['language_type'] = 'cross-lingual'
            task['languages'] = [task['source_lang'], task['target_lang']]
        else:
            task['language_type'] = 'multilingual'
            # 默认假设是英中混合
            task['languages'] = ['en', 'zh']
            
    # 单语言任务
    else:
        task['language_type'] = 'monolingual'
        task['languages'] = [language]
    
    return task


def add_language_annotations(input_file: str, output_file: str = None, dry_run: bool = False):
    """
    为测试用例文件添加语言标注
    
    Args:
        input_file: 输入文件路径
        output_file: 输出文件路径（如果为 None，则覆盖输入文件）
        dry_run: 如果为 True，只打印统计信息，不写入文件
    """
    print(f"读取测试用例文件: {input_file}")
    
    # 读取文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 统计信息
    stats = {
        'total': 0,
        'monolingual': 0,
        'cross-lingual': 0,
        'code': 0,
        'multilingual': 0,
        'languages': {},
        'programming_languages': {}
    }
    
    # 处理每个任务
    tasks = data.get('tasks', [])
    for task in tasks:
        stats['total'] += 1
        
        # 添加语言标注
        task = infer_language_type(task)
        
        # 更新统计
        lang_type = task.get('language_type', 'unknown')
        stats[lang_type] = stats.get(lang_type, 0) + 1
        
        # 统计语言分布
        for lang in task.get('languages', []):
            stats['languages'][lang] = stats['languages'].get(lang, 0) + 1
        
        # 统计编程语言
        if 'programming_language' in task:
            prog_lang = task['programming_language']
            stats['programming_languages'][prog_lang] = \
                stats['programming_languages'].get(prog_lang, 0) + 1
    
    # 打印统计信息
    print(f"\n{'='*60}")
    print("语言标注统计")
    print(f"{'='*60}")
    print(f"总任务数: {stats['total']}")
    print(f"\n语言类型分布:")
    print(f"  单语言 (monolingual):    {stats.get('monolingual', 0)}")
    print(f"  跨语言 (cross-lingual):  {stats.get('cross-lingual', 0)}")
    print(f"  代码 (code):             {stats.get('code', 0)}")
    print(f"  多语言 (multilingual):   {stats.get('multilingual', 0)}")
    
    print(f"\n自然语言分布:")
    for lang, count in sorted(stats['languages'].items(), key=lambda x: x[1], reverse=True):
        lang_name = {
            'en': '英语',
            'zh': '中文',
            'zho_Hans': '中文（简体）',
            'eng': '英语',
            'ja': '日语',
            'ko': '韩语',
            'fr': '法语',
            'de': '德语'
        }.get(lang, lang)
        print(f"  {lang_name} ({lang}): {count}")
    
    if stats['programming_languages']:
        print(f"\n编程语言分布:")
        for prog_lang, count in sorted(stats['programming_languages'].items(), 
                                       key=lambda x: x[1], reverse=True):
            print(f"  {prog_lang}: {count}")
    
    print(f"{'='*60}\n")
    
    # 写入文件
    if not dry_run:
        output_path = output_file or input_file
        print(f"写入更新后的文件: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 完成！已更新 {stats['total']} 个任务")
    else:
        print("⚠️  Dry run 模式，未写入文件")
    
    return stats


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='为测试用例添加语言类型标注',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 更新文件（覆盖原文件）
  python add_language_annotations.py data/test_cases/test_cases_comprehensive.json
  
  # 输出到新文件
  python add_language_annotations.py input.json -o output.json
  
  # Dry run（只查看统计，不修改文件）
  python add_language_annotations.py input.json --dry-run
        """
    )
    
    parser.add_argument(
        'input_file',
        help='输入的测试用例 JSON 文件'
    )
    
    parser.add_argument(
        '-o', '--output',
        dest='output_file',
        help='输出文件路径（默认覆盖输入文件）'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只显示统计信息，不修改文件'
    )
    
    args = parser.parse_args()
    
    # 检查输入文件是否存在
    if not Path(args.input_file).exists():
        print(f"❌ 错误: 文件不存在: {args.input_file}")
        sys.exit(1)
    
    try:
        add_language_annotations(
            args.input_file,
            args.output_file,
            args.dry_run
        )
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
