"""
通用帕累托前沿分析系统

功能：
1. 熵权法计算质量综合得分
2. 帕累托前沿识别（2D + 3D）
3. 定量指标计算（超体积、间距、扩散度、边际效益、拐点）
4. 稳健性验证（扰动分析、权重敏感性、交叉验证）
5. 自动生成完整报告

使用方法：
    python universal_pareto_analyzer.py --task reasoning --quality-file path/to/quality.csv --energy-file path/to/energy.csv
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from analysis.qe_research.scripts.pareto_core import (
    EntropyWeightCalculator,
    ParetoFrontierIdentifier,
    QuantitativeMetricsCalculator,
    RobustnessAnalyzer,
    ReportGenerator
)

import argparse
import pandas as pd
import numpy as np
from datetime import datetime


class UniversalParetoAnalyzer:
    """通用帕累托前沿分析器"""
    
    def __init__(self, task_name, output_dir=None):
        """
        初始化
        
        Args:
            task_name: 任务名称（如'reasoning', 'qa', 'summary'等）
            output_dir: 输出目录（默认为results/pareto_analysis/{task_name}）
        """
        self.task_name = task_name
        
        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent / 'results' / 'pareto_analysis' / task_name
        else:
            self.output_dir = Path(output_dir)
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.data = None
        self.results = {}
        
    def load_data(self, quality_file=None, energy_file=None, speed_file=None, 
                  quality_scores=None, model_col='model'):
        """
        加载数据
        
        Args:
            quality_file: 质量评分文件（CSV，包含多个质量维度）
            energy_file: 能耗数据文件（CSV，包含model和energy列）
            speed_file: 速度数据文件（CSV，包含model和speed列）
            quality_scores: 直接提供的质量得分字典 {model: score}
            model_col: 模型列名
        """
        print(f"\n{'='*80}")
        print(f"加载数据：{self.task_name}任务")
        print(f"{'='*80}")
        
        # 加载质量数据
        if quality_file:
            quality_df = pd.read_csv(quality_file)
            print(f"✓ 质量数据: {len(quality_df)} 行")
        elif quality_scores:
            quality_df = pd.DataFrame(list(quality_scores.items()), 
                                     columns=[model_col, 'quality_score'])
            print(f"✓ 质量数据: {len(quality_df)} 个模型")
        else:
            raise ValueError("必须提供quality_file或quality_scores")
        
        # 加载能耗数据
        if energy_file:
            energy_df = pd.read_csv(energy_file)
            print(f"✓ 能耗数据: {len(energy_df)} 行")
        else:
            raise ValueError("必须提供energy_file")
        
        # 加载速度数据
        if speed_file:
            speed_df = pd.read_csv(speed_file)
            print(f"✓ 速度数据: {len(speed_df)} 行")
        else:
            print("⚠ 未提供速度数据，将跳过速度相关分析")
            speed_df = None
        
        # 合并数据
        self.data = quality_df.copy()
        
        # 合并能耗
        if 'energy' not in self.data.columns:
            self.data = self.data.merge(energy_df[[model_col, 'energy']], 
                                       on=model_col, how='left')
        
        # 合并速度
        if speed_df is not None and 'speed' not in self.data.columns:
            self.data = self.data.merge(speed_df[[model_col, 'speed']], 
                                       on=model_col, how='left')
        
        print(f"\n合并后数据: {len(self.data)} 行")
        print(f"列: {', '.join(self.data.columns)}")
        
        return self.data
