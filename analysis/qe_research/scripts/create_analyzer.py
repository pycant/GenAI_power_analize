#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
临时脚本：创建quality_data_analyzer.py文件
"""

import os

# 目标文件路径
target_file = 'analysis/qe_research/scripts/quality_analysis_core/quality_data_analyzer.py'

# 文件内容
content = '''"""
质量数据分析器

对质量评分数据进行描述性分析，生成报告和可视化
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sys

# 导入共享函数
import shared_functions as sf


class QualityDataAnalyzer:
    """质量数据分析器类"""
    
    def __init__(self, 
                 data_dir: str = 'analysis/qe_research/results/quality_scores',
                 output_dir: str = 'analysis/qe_research/results/quality_analysis',
                 use_raw: bool = True):
        """
        初始化分析器
        
        Args:
            data_dir: 质量评分数据目录
            output_dir: 输出目录
            use_raw: 是否使用原始精度数据
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.use_raw = use_raw
        
        # 创建输出目录
        self.reports_dir = self.output_dir / 'reports'
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir = self.output_dir / 'tables'
        
        for dir_path in [self.reports_dir, self.figures_dir, self.tables_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 任务类型列表
        self.task_types = ['code', 'creative', 'math', 'qa', 
                          'reasoning', 'summary', 'translation']
        
        # 存储加载的数据
        self.data = {}
        
        print(f"分析器初始化完成")
        print(f"  数据目录: {self.data_dir}")
        print(f"  输出目录: {self.output_dir}")
        print(f"  使用原始精度: {self.use_raw}")
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """加载所有任务的质量评分数据"""
        print("\\n" + "="*80)
        print("加载质量评分数据")
        print("="*80)
        
        for task in self.task_types:
            try:
                df = sf.load_quality_scores(task, self.use_raw, str(self.data_dir))
                self.data[task] = df
                print(f"✓ {task:12s}: {len(df)} 个模型, {len(df.columns)-1} 个指标")
            except FileNotFoundError as e:
                print(f"✗ {task:12s}: 文件不存在")
                self.data[task] = None
            except Exception as e:
                print(f"✗ {task:12s}: 加载失败 - {str(e)}")
                self.data[task] = None
        
        loaded_count = sum(1 for v in self.data.values() if v is not None)
        print(f"\\n成功加载 {loaded_count}/{len(self.task_types)} 个任务数据")
        
        return self.data
    
    def run_all_analyses(self):
        """运行完整分析流程"""
        print("\\n" + "="*80)
        print("质量数据描述性分析 - 完整流程")
        print("="*80)
        
        self.load_all_data()
        print("\\n分析完成!")


if __name__ == '__main__':
    analyzer = QualityDataAnalyzer(use_raw=True)
    analyzer.run_all_analyses()
'''

# 写入文件
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"文件已创建: {target_file}")
print(f"文件大小: {os.path.getsize(target_file)} 字节")
