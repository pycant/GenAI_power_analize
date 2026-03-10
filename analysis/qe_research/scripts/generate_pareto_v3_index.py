#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 Pareto Analysis V3 目录索引文档

该脚本扫描 pareto_analysis_v3 目录结构，提取所有报告和资源文件，
生成一个结构化的索引文档，方便查阅和导航。

功能：
- 扫描所有任务类型目录（code, creative, math, qa, reasoning, summary, translation）
- 提取报告文件的关键信息（标题、摘要）
- 统计图表和数据文件
- 生成带链接的 Markdown 索引文档
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def extract_report_summary(report_path: Path, max_lines: int = 10) -> Tuple[str, str]:
    """
    从报告文件中提取标题和摘要
    
    Args:
        report_path: 报告文件路径
        max_lines: 最多读取的行数
        
    Returns:
        (title, summary) 元组
    """
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f.readlines()[:max_lines]]
        
        # 提取标题（第一个 # 标题）
        title = "未命名报告"
        for line in lines:
            if line.startswith('# '):
                title = line.lstrip('# ').strip()
                break
        
        # 提取摘要（第一段非空文本）
        summary = ""
        in_summary = False
        for line in lines:
            if line and not line.startswith('#') and not line.startswith('---'):
                if not in_summary:
                    in_summary = True
                summary += line + " "
                if len(summary) > 200:  # 限制摘要长度
                    break
        
        summary = summary.strip()[:200] + "..." if len(summary) > 200 else summary.strip()
        
        return title, summary
    except Exception as e:
        return "读取失败", f"无法读取文件: {str(e)}"


def count_files_by_type(directory: Path) -> Dict[str, int]:
    """
    统计目录中各类型文件的数量
    
    Args:
        directory: 目录路径
        
    Returns:
        文件类型统计字典
    """
    counts = {
        'reports': 0,
        'images': 0,
        'data': 0,
        'pca_reports': 0
    }
    
    if not directory.exists():
        return counts
    
    for file in directory.rglob('*'):
        if file.is_file():
            if file.suffix == '.md':
                if 'pca_analysis' in str(file):
                    counts['pca_reports'] += 1
                else:
                    counts['reports'] += 1
            elif file.suffix in ['.png', '.jpg', '.jpeg', '.svg']:
                counts['images'] += 1
            elif file.suffix in ['.csv', '.json', '.xlsx']:
                counts['data'] += 1
    
    return counts


def generate_task_section(task_name: str, task_dir: Path, base_dir: Path) -> str:
    """
    生成单个任务类型的文档章节
    
    Args:
        task_name: 任务名称
        task_dir: 任务目录路径
        base_dir: 基础目录路径
        
    Returns:
        Markdown 格式的章节内容
    """
    section = f"\n### {task_name.upper()} 任务\n\n"
    
    if not task_dir.exists():
        section += f"⚠️ 目录不存在: `{task_dir.relative_to(base_dir)}`\n\n"
        return section
    
    # 统计文件
    counts = count_files_by_type(task_dir)
    section += f"📊 **资源统计**: {counts['reports']} 个主报告 | "
    section += f"{counts['pca_reports']} 个PCA报告 | "
    section += f"{counts['images']} 张图表 | "
    section += f"{counts['data']} 个数据文件\n\n"
    
    # 主报告
    main_report = task_dir / f"{task_name.upper()}_PARETO_ANALYSIS_REPORT.md"
    if main_report.exists():
        title, summary = extract_report_summary(main_report)
        rel_path = main_report.relative_to(base_dir)
        section += f"#### 📄 主报告\n\n"
        section += f"**[{title}]({rel_path})**\n\n"
        section += f"> {summary}\n\n"
    
    # PCA 分析报告
    pca_report = task_dir / "pca_analysis" / "PCA_ANALYSIS_REPORT.md"
    if pca_report.exists():
        title, summary = extract_report_summary(pca_report)
        rel_path = pca_report.relative_to(base_dir)
        section += f"#### 🔬 PCA 分析报告\n\n"
        section += f"**[{title}]({rel_path})**\n\n"
        section += f"> {summary}\n\n"
    
    # 图表文件
    images = sorted([f for f in task_dir.glob('*.png')])
    if images:
        section += f"#### 📈 主要图表\n\n"
        for img in images:
            rel_path = img.relative_to(base_dir)
            section += f"- [{img.name}]({rel_path})\n"
        section += "\n"
    
    # PCA 图表
    pca_images = sorted([f for f in (task_dir / "pca_analysis").glob('*.png')]) if (task_dir / "pca_analysis").exists() else []
    if pca_images:
        section += f"#### 🔍 PCA 可视化\n\n"
        for img in pca_images:
            rel_path = img.relative_to(base_dir)
            section += f"- [{img.name}]({rel_path})\n"
        section += "\n"
    
    # 数据文件
    data_files = sorted([f for f in task_dir.glob('*.csv')])
    if data_files:
        section += f"#### 💾 数据文件\n\n"
        for data in data_files:
            rel_path = data.relative_to(base_dir)
            size_kb = data.stat().st_size / 1024
            section += f"- [{data.name}]({rel_path}) ({size_kb:.1f} KB)\n"
        section += "\n"
    
    section += "---\n"
    return section


def generate_index_document(results_dir: Path) -> str:
    """
    生成完整的索引文档
    
    Args:
        results_dir: pareto_analysis_v3 目录路径
        
    Returns:
        完整的 Markdown 文档内容
    """
    doc = f"""# Pareto Analysis V3 完整文档索引

> 📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 
> 📂 目录: `{results_dir.name}`

## 📋 概述

本目录包含基于 PCA（主成分分析）方法的帕累托前沿分析结果。通过 PCA 综合各模型的多维质量指标，
并结合效率指标（速度、能耗）进行帕累托前沿分析，识别在质量-效率权衡中表现最优的模型。

### 🎯 分析方法

1. **PCA 质量综合**: 使用主成分分析将多个质量指标降维为综合质量得分
2. **熵权法**: 基于信息熵计算各质量指标的客观权重
3. **帕累托前沿**: 识别在质量-速度和质量-能耗两个维度上的非支配解
4. **多任务评估**: 针对不同任务类型（代码、创意、数学、问答、推理、摘要、翻译）分别分析

### 📊 任务类型覆盖

"""
    
    # 任务列表
    tasks = [
        ('code', '代码生成'),
        ('creative', '创意写作'),
        ('math', '数学推理'),
        ('qa', '问答任务'),
        ('reasoning', '逻辑推理'),
        ('summary', '文本摘要'),
        ('translation', '机器翻译')
    ]
    
    for task_id, task_name in tasks:
        task_dir = results_dir / task_id
        status = "✅" if task_dir.exists() else "❌"
        doc += f"- {status} **{task_name}** (`{task_id}`)\n"
    
    doc += "\n## 📚 综合报告\n\n"
    
    # 综合报告
    comprehensive_report = results_dir / "COMPREHENSIVE_PARETO_ANALYSIS_REPORT.md"
    if comprehensive_report.exists():
        title, summary = extract_report_summary(comprehensive_report)
        rel_path = comprehensive_report.relative_to(results_dir.parent.parent.parent)
        doc += f"### 📖 [{title}]({rel_path})\n\n"
        doc += f"> {summary}\n\n"
    
    # 统计总体信息
    total_counts = count_files_by_type(results_dir)
    doc += f"### 📈 资源统计\n\n"
    doc += f"- 📄 报告文件: {total_counts['reports']} 个\n"
    doc += f"- 🔬 PCA 分析报告: {total_counts['pca_reports']} 个\n"
    doc += f"- 📊 图表文件: {total_counts['images']} 张\n"
    doc += f"- 💾 数据文件: {total_counts['data']} 个\n\n"
    
    doc += "## 🔍 任务详细索引\n\n"
    doc += "以下按任务类型组织的详细文档和资源索引：\n"
    
    # 生成各任务章节
    base_dir = results_dir.parent.parent.parent  # 回到 analysis 目录
    for task_id, task_name in tasks:
        task_dir = results_dir / task_id
        doc += generate_task_section(task_id, task_dir, base_dir)
    
    # 添加使用指南
    doc += """
## 📖 使用指南

### 查看分析结果

1. **综合报告**: 从 `COMPREHENSIVE_PARETO_ANALYSIS_REPORT.md` 开始，了解整体分析结果
2. **任务特定分析**: 根据感兴趣的任务类型，查看对应目录下的主报告
3. **PCA 详情**: 查看 `pca_analysis/PCA_ANALYSIS_REPORT.md` 了解质量指标的降维和综合过程
4. **可视化**: 浏览各目录下的 PNG 图表文件，直观理解帕累托前沿

### 关键图表说明

- `pareto_quality_speed.png`: 质量-速度帕累托前沿图
- `pareto_quality_energy.png`: 质量-能耗帕累托前沿图
- `entropy_weights.png`: 熵权法计算的指标权重分布
- `pca_scree_plot.png`: PCA 碎石图（主成分方差解释率）
- `pca_loadings_heatmap.png`: PCA 载荷热力图（指标贡献度）
- `pca_biplot.png`: PCA 双标图（模型与指标关系）
- `pca_component_scores.png`: 主成分得分分布

### 数据文件

- `merged_data.csv`: 合并的质量、效率和 PCA 结果数据，可用于进一步分析

## 🔗 相关文档

- [PCA 功能完整说明](../../scripts/pareto_core/PCA_FEATURE_COMPLETE.md)
- [帕累托分析快速参考](../../scripts/pareto_core/QUICK_REFERENCE.md)
- [质量分析指南](../../COMPREHENSIVE_QUALITY_ANALYSIS_GUIDE.md)
- [假设检验指南](../../docs/HYPOTHESIS_TESTING_GUIDE.md)

## 🛠️ 重新生成索引

运行以下命令重新生成本索引文档：

```bash
python analysis/qe_research/scripts/generate_pareto_v3_index.py
```

---

*本文档由自动化脚本生成，如有问题请查看脚本源码或联系维护者。*
"""
    
    return doc


def main():
    """主函数"""
    # 确定路径
    script_dir = Path(__file__).parent
    results_dir = script_dir.parent / "results" / "pareto_analysis_v3"
    output_file = results_dir / "INDEX.md"
    
    print(f"📂 扫描目录: {results_dir}")
    
    if not results_dir.exists():
        print(f"❌ 错误: 目录不存在 - {results_dir}")
        return
    
    # 生成文档
    print("📝 生成索引文档...")
    doc_content = generate_index_document(results_dir)
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"✅ 索引文档已生成: {output_file}")
    print(f"📄 文档大小: {output_file.stat().st_size / 1024:.1f} KB")
    
    # 显示统计信息
    total_counts = count_files_by_type(results_dir)
    print("\n📊 资源统计:")
    print(f"  - 报告文件: {total_counts['reports']} 个")
    print(f"  - PCA 分析报告: {total_counts['pca_reports']} 个")
    print(f"  - 图表文件: {total_counts['images']} 张")
    print(f"  - 数据文件: {total_counts['data']} 个")


if __name__ == "__main__":
    main()
