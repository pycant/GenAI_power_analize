#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理质量评估结果目录

将所有任务类型的评估结果整理到统一的目录结构中
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


def organize_results():
    """整理评估结果目录"""
    
    print("\n" + "="*60)
    print("📁 整理质量评估结果目录")
    print("="*60)
    
    # 定义基础路径
    results_dir = Path('data/analize/results')
    
    # 定义任务类型和对应的目录
    task_dirs = {
        'code': 'code_quality',
        'creative': 'creative_quality',
        'math': 'math_quality',
        'qa': 'qa_quality',
        'reasoning': 'reasoning_quality',
        'summary': 'summary_quality',
        'translation': 'translation_quality'
    }
    
    print(f"\n📂 结果目录: {results_dir}")
    print(f"📋 任务类型: {len(task_dirs)} 种")
    
    # 检查每个任务目录
    print(f"\n{'='*60}")
    print("检查任务目录结构")
    print(f"{'='*60}\n")
    
    for task, dir_name in task_dirs.items():
        task_dir = results_dir / dir_name
        
        print(f"📁 {task.upper()} ({dir_name})")
        
        if not task_dir.exists():
            print(f"   ⚠️  目录不存在，创建中...")
            task_dir.mkdir(parents=True, exist_ok=True)
            (task_dir / 'figures').mkdir(exist_ok=True)
            print(f"   ✅ 已创建目录")
        else:
            print(f"   ✅ 目录存在")
            
            # 检查figures子目录
            figures_dir = task_dir / 'figures'
            if not figures_dir.exists():
                figures_dir.mkdir(exist_ok=True)
                print(f"   📊 已创建 figures/ 子目录")
            
            # 列出现有文件
            files = list(task_dir.glob('*'))
            csv_files = [f for f in files if f.suffix == '.csv']
            md_files = [f for f in files if f.suffix == '.md']
            png_files = list(figures_dir.glob('*.png'))
            
            print(f"   📄 CSV文件: {len(csv_files)} 个")
            print(f"   📝 MD文件: {len(md_files)} 个")
            print(f"   📊 图表文件: {len(png_files)} 个")
            
            # 显示关键文件
            key_files = [
                f'{dir_name}_scores.csv',
                f'{dir_name}_summary.csv',
                f'{dir_name}_report.md'
            ]
            
            for key_file in key_files:
                if (task_dir / key_file).exists():
                    print(f"      ✅ {key_file}")
                else:
                    print(f"      ⚠️  {key_file} (缺失)")
        
        print()
    
    # 清理重复或过时的文件
    print(f"{'='*60}")
    print("清理建议")
    print(f"{'='*60}\n")
    
    # 检查qa_quality_academic目录
    qa_academic_dir = results_dir / 'qa_quality_academic'
    if qa_academic_dir.exists():
        print("📁 发现 qa_quality_academic/ 目录")
        print("   💡 建议: 这是QA任务的学术版本评估结果")
        print("   💡 可以保留作为备份，或合并到 qa_quality/")
        print()
    
    # 检查根目录下的文件
    root_files = [f for f in results_dir.glob('*.md') if f.is_file()]
    if root_files:
        print("📄 根目录下的文件:")
        for f in root_files:
            print(f"   - {f.name}")
        print("   💡 建议: 将这些文件移动到对应的任务目录中")
        print()
    
    # 生成目录结构报告
    print(f"{'='*60}")
    print("生成目录结构报告")
    print(f"{'='*60}\n")
    
    report_file = results_dir / 'DIRECTORY_STRUCTURE.md'
    generate_structure_report(results_dir, report_file)
    print(f"✅ 目录结构报告已生成: {report_file}")
    
    print(f"\n{'='*60}")
    print("✅ 整理完成")
    print(f"{'='*60}\n")
    
    print("📋 后续步骤:")
    print("   1. 查看 data/analize/results/README.md 了解目录结构")
    print("   2. 查看 data/analize/results/DIRECTORY_STRUCTURE.md 了解详细文件列表")
    print("   3. 运行各任务的评估脚本生成缺失的结果文件")
    print("   4. 使用 aggregate_all_quality_results.py 汇总所有结果")
    print()


def generate_structure_report(results_dir: Path, output_file: Path):
    """生成目录结构报告"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 质量评估结果目录结构\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 目录树\n\n")
        f.write("```\n")
        f.write("data/analize/results/\n")
        
        # 遍历所有子目录
        for item in sorted(results_dir.iterdir()):
            if item.is_dir():
                f.write(f"├── {item.name}/\n")
                
                # 列出子目录中的文件
                files = sorted(item.glob('*'))
                for i, file in enumerate(files):
                    if file.is_file():
                        is_last = i == len(files) - 1
                        prefix = "└──" if is_last else "├──"
                        f.write(f"│   {prefix} {file.name}\n")
                    elif file.is_dir():
                        f.write(f"│   ├── {file.name}/\n")
                        # 列出figures中的文件
                        if file.name == 'figures':
                            fig_files = sorted(file.glob('*.png'))
                            for j, fig in enumerate(fig_files):
                                is_last_fig = j == len(fig_files) - 1
                                fig_prefix = "└──" if is_last_fig else "├──"
                                f.write(f"│   │   {fig_prefix} {fig.name}\n")
        
        f.write("```\n\n")
        
        # 统计信息
        f.write("## 统计信息\n\n")
        
        task_dirs = [d for d in results_dir.iterdir() if d.is_dir() and d.name.endswith('_quality')]
        
        f.write(f"- 任务类型数: {len(task_dirs)}\n")
        
        total_csv = sum(len(list(d.glob('*.csv'))) for d in task_dirs)
        total_md = sum(len(list(d.glob('*.md'))) for d in task_dirs)
        total_png = sum(len(list((d / 'figures').glob('*.png'))) for d in task_dirs if (d / 'figures').exists())
        
        f.write(f"- CSV文件总数: {total_csv}\n")
        f.write(f"- Markdown文件总数: {total_md}\n")
        f.write(f"- 图表文件总数: {total_png}\n\n")
        
        # 详细列表
        f.write("## 详细文件列表\n\n")
        
        for task_dir in sorted(task_dirs):
            f.write(f"### {task_dir.name}\n\n")
            
            csv_files = sorted(task_dir.glob('*.csv'))
            md_files = sorted(task_dir.glob('*.md'))
            
            if csv_files:
                f.write("**CSV文件**:\n")
                for csv in csv_files:
                    size = csv.stat().st_size / 1024  # KB
                    f.write(f"- `{csv.name}` ({size:.1f} KB)\n")
                f.write("\n")
            
            if md_files:
                f.write("**Markdown文件**:\n")
                for md in md_files:
                    size = md.stat().st_size / 1024  # KB
                    f.write(f"- `{md.name}` ({size:.1f} KB)\n")
                f.write("\n")
            
            figures_dir = task_dir / 'figures'
            if figures_dir.exists():
                png_files = sorted(figures_dir.glob('*.png'))
                if png_files:
                    f.write("**图表文件**:\n")
                    for png in png_files:
                        size = png.stat().st_size / 1024  # KB
                        f.write(f"- `{png.name}` ({size:.1f} KB)\n")
                    f.write("\n")


if __name__ == '__main__':
    organize_results()
