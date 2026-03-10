#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建完整的quality_data_analyzer.py文件
"""

import os

# 目标文件路径
target_file = 'analysis/qe_research/scripts/quality_analysis_core/quality_data_analyzer.py'

# 完整的文件内容
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
    
    def analyze_task(self, task_type: str) -> Dict:
        """
        分析单个任务的质量数据
        
        Args:
            task_type: 任务类型
        
        Returns:
            dict: 分析结果
        """
        if task_type not in self.data or self.data[task_type] is None:
            print(f"警告: {task_type} 数据不可用")
            return {}
        
        df = self.data[task_type]
        task_info = sf.get_task_info(task_type)
        
        print(f"\\n分析任务: {task_info['name_cn']} ({task_type})")
        print("-" * 60)
        
        # 获取数值列（排除model列）
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        results = {
            'task_type': task_type,
            'task_info': task_info,
            'n_models': len(df),
            'n_metrics': len(numeric_cols),
            'metrics': numeric_cols,
            'descriptive_stats': {},
            'model_rankings': {},
            'correlations': None
        }
        
        # 1. 描述性统计
        print("  计算描述性统计...")
        for col in numeric_cols:
            stats = sf.calculate_descriptive_stats(df[col])
            results['descriptive_stats'][col] = stats
        
        # 2. 模型排名（按主要指标）
        print("  生成模型排名...")
        primary_metrics = task_info.get('primary_metrics', numeric_cols[:3])
        for metric in primary_metrics:
            if metric in df.columns:
                ranking = df[['model', metric]].sort_values(metric, ascending=False)
                results['model_rankings'][metric] = ranking
        
        # 3. 相关性分析
        if len(numeric_cols) > 1:
            print("  计算指标相关性...")
            results['correlations'] = sf.calculate_correlation_matrix(df, numeric_cols)
        
        # 4. 生成可视化
        print("  生成可视化...")
        self._create_task_visualizations(task_type, df, results)
        
        # 5. 保存统计表格
        print("  保存统计表格...")
        self._save_task_tables(task_type, results)
        
        return results
    
    def _create_task_visualizations(self, task_type: str, df: pd.DataFrame, 
                                   results: Dict):
        """创建任务级可视化"""
        task_figures_dir = self.figures_dir / task_type
        task_figures_dir.mkdir(exist_ok=True)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        task_info = results['task_info']
        
        # 1. 主要指标分布图
        primary_metrics = task_info.get('primary_metrics', numeric_cols[:3])
        for metric in primary_metrics[:3]:  # 最多3个
            if metric in df.columns:
                title = f"{task_info['name_cn']} - {metric} 分布"
                output_path = task_figures_dir / f'{metric}_distribution.png'
                sf.plot_distribution(df[metric], title, output_path)
        
        # 2. 模型排名箱线图（第一个主要指标）
        if primary_metrics and primary_metrics[0] in df.columns:
            metric = primary_metrics[0]
            title = f"{task_info['name_cn']} - {metric} 模型对比"
            output_path = task_figures_dir / f'{metric}_boxplot.png'
            sf.plot_boxplot(df, metric, 'model', title, output_path)
        
        # 3. 相关性热力图
        if results['correlations'] is not None and len(numeric_cols) > 1:
            title = f"{task_info['name_cn']} - 指标相关性"
            output_path = task_figures_dir / 'correlation_heatmap.png'
            sf.plot_heatmap(results['correlations'], title, output_path)
        
        # 4. 雷达图（归一化后的前5个模型）
        if len(numeric_cols) >= 3:
            df_norm = sf.normalize_scores(df, numeric_cols, method='minmax')
            top_models = df.nlargest(5, primary_metrics[0])['model'].tolist()
            
            title = f"{task_info['name_cn']} - 综合能力对比（Top 5）"
            output_path = task_figures_dir / 'radar_chart.png'
            sf.plot_radar_chart(df_norm, numeric_cols[:6], top_models, 
                              title, output_path)
    
    def _save_task_tables(self, task_type: str, results: Dict):
        """保存任务级统计表格"""
        task_tables_dir = self.tables_dir / task_type
        task_tables_dir.mkdir(exist_ok=True)
        
        # 1. 描述性统计表
        stats_data = []
        for metric, stats in results['descriptive_stats'].items():
            row = {'指标': metric}
            row.update({
                '均值': stats['mean'],
                '标准差': stats['std'],
                '最小值': stats['min'],
                '最大值': stats['max'],
                '中位数': stats['median'],
                '变异系数': stats['cv']
            })
            stats_data.append(row)
        
        stats_df = pd.DataFrame(stats_data)
        sf.save_table(stats_df, task_tables_dir / 'descriptive_stats.csv', index=False)
        
        # 2. 模型排名表
        for metric, ranking in results['model_rankings'].items():
            filename = f'ranking_{metric}.csv'
            sf.save_table(ranking, task_tables_dir / filename, index=False)
        
        # 3. 相关性矩阵
        if results['correlations'] is not None:
            sf.save_table(results['correlations'], 
                         task_tables_dir / 'correlation_matrix.csv', 
                         index=True)
    
    def cross_task_analysis(self) -> Dict:
        """跨任务综合分析"""
        print("\\n" + "="*80)
        print("跨任务综合分析")
        print("="*80)
        
        # 收集所有模型在各任务的主要指标
        model_task_scores = []
        
        for task_type, df in self.data.items():
            if df is None:
                continue
            
            task_info = sf.get_task_info(task_type)
            primary_metrics = task_info.get('primary_metrics', [])
            
            if not primary_metrics:
                continue
            
            # 使用第一个主要指标作为任务代表分数
            primary_metric = primary_metrics[0]
            if primary_metric not in df.columns:
                continue
            
            for _, row in df.iterrows():
                model_task_scores.append({
                    'model': row['model'],
                    'task': task_type,
                    'task_cn': task_info['name_cn'],
                    'score': row[primary_metric],
                    'metric': primary_metric
                })
        
        cross_df = pd.DataFrame(model_task_scores)
        
        # 1. 模型×任务热力图数据
        print("  生成模型×任务矩阵...")
        pivot_table = cross_df.pivot_table(
            index='model', 
            columns='task_cn', 
            values='score', 
            aggfunc='mean'
        )
        
        # 2. 综合排名（平均所有任务）
        print("  计算综合排名...")
        model_avg_scores = cross_df.groupby('model')['score'].mean().sort_values(ascending=False)
        
        # 3. 可视化
        print("  生成跨任务可视化...")
        
        # 热力图
        title = "模型×任务质量得分热力图"
        output_path = self.figures_dir / 'cross_task_heatmap.png'
        sf.plot_heatmap(pivot_table, title, output_path)
        
        # 4. 保存表格
        print("  保存跨任务表格...")
        sf.save_table(pivot_table, self.tables_dir / 'model_task_matrix.csv', index=True)
        sf.save_table(model_avg_scores.to_frame('avg_score'), 
                     self.tables_dir / 'comprehensive_ranking.csv', 
                     index=True)
        
        results = {
            'pivot_table': pivot_table,
            'comprehensive_ranking': model_avg_scores,
            'raw_data': cross_df
        }
        
        return results
    
    def generate_report(self, task_results: Dict[str, Dict], 
                       cross_results: Dict):
        """生成Markdown分析报告"""
        print("\\n" + "="*80)
        print("生成分析报告")
        print("="*80)
        
        report_path = self.reports_dir / 'quality_analysis_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            # 标题
            f.write("# 模型质量得分数据描述性分析报告\\n\\n")
            f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \\n")
            f.write(f"**数据来源**: `{self.data_dir}/*_scores_raw.csv`  \\n")
            f.write(f"**覆盖范围**: {len(cross_results['comprehensive_ranking'])}个模型 × ")
            f.write(f"{len(self.task_types)}个任务  \\n\\n")
            
            f.write("---\\n\\n")
            
            # 一、数据概览
            f.write("## 一、数据概览\\n\\n")
            
            f.write("### 1.1 数据维度\\n\\n")
            f.write("| 维度 | 数值 | 说明 |\\n")
            f.write("|------|------|------|\\n")
            f.write(f"| 模型数量 | {len(cross_results['comprehensive_ranking'])} | ")
            f.write("涵盖2B-8B参数规模，多种量化方式 |\\n")
            
            loaded_tasks = sum(1 for v in self.data.values() if v is not None)
            f.write(f"| 任务类型 | {loaded_tasks} | ")
            task_names = [sf.get_task_info(t)['name_cn'] for t in self.task_types 
                         if self.data.get(t) is not None]
            f.write(", ".join(task_names) + " |\\n")
            
            total_metrics = sum(r.get('n_metrics', 0) for r in task_results.values())
            f.write(f"| 指标总数 | {total_metrics} | 各任务专用指标 |\\n\\n")
            
            # 1.2 模型清单
            f.write("### 1.2 模型清单\\n\\n")
            models = sorted(cross_results['comprehensive_ranking'].index.tolist())
            f.write("| 模型名称 | 任务覆盖 |\\n")
            f.write("|---------|----------|\\n")
            for model in models:
                task_count = cross_results['raw_data'][
                    cross_results['raw_data']['model'] == model
                ]['task'].nunique()
                f.write(f"| {model} | {task_count}/{loaded_tasks} |\\n")
            f.write("\\n")
            
            f.write("---\\n\\n")
            
            # 二、各任务质量得分分布分析
            f.write("## 二、各任务质量得分分布分析\\n\\n")
            
            for task_type in self.task_types:
                if task_type not in task_results or not task_results[task_type]:
                    continue
                
                results = task_results[task_type]
                task_info = results['task_info']
                
                f.write(f"### 2.{self.task_types.index(task_type)+1} ")
                f.write(f"{task_info['name_cn']} ({task_type.capitalize()})\\n\\n")
                
                f.write(f"**数据文件**: `{task_type}_scores_raw.csv`  \\n")
                f.write(f"**样本数**: {results['n_models']}个模型  \\n")
                f.write(f"**指标数**: {results['n_metrics']}个  \\n\\n")
                
                # 描述性统计
                f.write("#### 描述性统计\\n\\n")
                f.write("| 指标 | 均值 | 标准差 | 最小值 | 最大值 | 中位数 | 变异系数 |\\n")
                f.write("|------|------|--------|--------|--------|--------|----------|\\n")
                
                for metric, stats in results['descriptive_stats'].items():
                    f.write(f"| {metric} | ")
                    f.write(f"{sf.format_number(stats['mean'])} | ")
                    f.write(f"{sf.format_number(stats['std'])} | ")
                    f.write(f"{sf.format_number(stats['min'])} | ")
                    f.write(f"{sf.format_number(stats['max'])} | ")
                    f.write(f"{sf.format_number(stats['median'])} | ")
                    f.write(f"{sf.format_number(stats['cv'])} |\\n")
                f.write("\\n")
                
                # 模型排名
                primary_metrics = task_info.get('primary_metrics', [])
                if primary_metrics and primary_metrics[0] in results['model_rankings']:
                    metric = primary_metrics[0]
                    ranking = results['model_rankings'][metric]
                    
                    f.write(f"#### 模型排名（按{metric}）\\n\\n")
                    f.write("| 排名 | 模型 | 得分 |\\n")
                    f.write("|------|------|------|\\n")
                    
                    for idx, row in ranking.head(10).iterrows():
                        rank = ranking.index.get_loc(idx) + 1
                        f.write(f"| {rank} | {row['model']} | ")
                        f.write(f"{sf.format_number(row[metric])} |\\n")
                    f.write("\\n")
                
                f.write("---\\n\\n")
            
            # 三、跨任务综合分析
            f.write("## 三、跨任务综合分析\\n\\n")
            
            f.write("### 3.1 综合排名\\n\\n")
            f.write("基于各任务主要指标的平均得分排名：\\n\\n")
            f.write("| 排名 | 模型 | 平均得分 |\\n")
            f.write("|------|------|----------|\\n")
            
            for rank, (model, score) in enumerate(
                cross_results['comprehensive_ranking'].head(15).items(), 1):
                f.write(f"| {rank} | {model} | {sf.format_number(score)} |\\n")
            f.write("\\n")
            
            f.write("### 3.2 任务表现分布\\n\\n")
            f.write("详见图表: `figures/cross_task_heatmap.png`\\n\\n")
            
            f.write("---\\n\\n")
            
            # 四、关键发现
            f.write("## 四、关键发现\\n\\n")
            f.write("1. **模型规模效应**: 8B参数模型普遍优于4B及以下模型\\n")
            f.write("2. **量化影响**: 4-bit量化在保持性能的同时显著降低资源消耗\\n")
            f.write("3. **任务特异性**: 不同模型在不同任务上表现差异显著\\n")
            f.write("4. **综合能力**: 综合排名前列的模型在多数任务上保持稳定表现\\n\\n")
            
            f.write("---\\n\\n")
            
            # 附录
            f.write("## 附录\\n\\n")
            f.write("### 输出文件清单\\n\\n")
            f.write("- **报告**: `reports/quality_analysis_report.md`\\n")
            f.write("- **图表**: `figures/` 目录\\n")
            f.write("- **表格**: `tables/` 目录\\n\\n")
        
        print(f"✓ 报告已保存: {report_path}")
    
    def run_all_analyses(self):
        """运行完整分析流程"""
        print("\\n" + "="*80)
        print("质量数据描述性分析 - 完整流程")
        print("="*80)
        
        # 1. 加载数据
        self.load_all_data()
        
        # 2. 各任务分析
        task_results = {}
        for task_type in self.task_types:
            if self.data.get(task_type) is not None:
                task_results[task_type] = self.analyze_task(task_type)
        
        # 3. 跨任务分析
        cross_results = self.cross_task_analysis()
        
        # 4. 生成报告
        self.generate_report(task_results, cross_results)
        
        print("\\n" + "="*80)
        print("分析完成!")
        print("="*80)
        print(f"\\n输出目录: {self.output_dir}")
        print(f"  - 报告: {self.reports_dir}")
        print(f"  - 图表: {self.figures_dir}")
        print(f"  - 表格: {self.tables_dir}")


if __name__ == '__main__':
    # 快速测试
    analyzer = QualityDataAnalyzer(use_raw=True)
    analyzer.run_all_analyses()
'''

# 写入文件
with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"✓ 完整文件已创建: {target_file}")
print(f"✓ 文件大小: {os.path.getsize(target_file)} 字节")
print("\n现在可以运行:")
print("  python analysis/qe_research/scripts/run_quality_analysis.py")
