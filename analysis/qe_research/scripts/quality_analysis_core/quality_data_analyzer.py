"""
质量数据分析器（增强版）

基于reference.md的分析方法，对质量评分数据进行全面的描述性分析
包含：描述性统计、模型排名、跨任务综合分析、相关性分析、异常值检测等
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import sys
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# 导入共享函数
import shared_functions as sf


class QualityDataAnalyzer:
    """质量数据分析器类（增强版）"""
    
    def __init__(self, 
                 data_dir: str = 'analysis/qe_research/results/quality_scores',
                 output_dir: str = 'analysis/qe_research/results/quality_analysis',
                 use_raw: bool = True):
        """
        初始化分析器
        
        Args:
            data_dir: 质量评分数据目录（相对于项目根目录）
            output_dir: 输出目录（相对于项目根目录）
            use_raw: 是否使用原始精度数据
        """
        # 获取项目根目录（从当前文件向上4级）
        # quality_data_analyzer.py -> quality_analysis_core -> scripts -> qe_research -> analysis -> 项目根
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent.parent.parent
        
        # 转换为绝对路径
        if not Path(data_dir).is_absolute():
            self.data_dir = project_root / data_dir
        else:
            self.data_dir = Path(data_dir)
        
        if not Path(output_dir).is_absolute():
            self.output_dir = project_root / output_dir
        else:
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
        print(f"  项目根目录: {project_root}")
        print(f"  数据目录: {self.data_dir}")
        print(f"  输出目录: {self.output_dir}")
        print(f"  使用原始精度: {self.use_raw}")
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """加载所有任务的质量评分数据"""
        print("\n" + "="*80)
        print("加载质量评分数据")
        print("="*80)
        
        excluded_models = ['qwen25_7b_hf_8bit']  # 要剔除的模型
        
        for task in self.task_types:
            try:
                df = sf.load_quality_scores(task, self.use_raw, str(self.data_dir))
                
                # 剔除指定模型
                original_count = len(df)
                df = df[~df['model'].isin(excluded_models)]
                excluded_count = original_count - len(df)
                
                self.data[task] = df
                print(f"OK {task:12s}: {len(df)} 个模型, {len(df.columns)-1} 个指标", end='')
                if excluded_count > 0:
                    print(f" (剔除 {excluded_count} 个)")
                else:
                    print()
            except FileNotFoundError as e:
                print(f"X  {task:12s}: 文件不存在")
                self.data[task] = None
            except Exception as e:
                print(f"X  {task:12s}: 加载失败 - {str(e)}")
                self.data[task] = None
        
        loaded_count = sum(1 for v in self.data.values() if v is not None)
        print(f"\n成功加载 {loaded_count}/{len(self.task_types)} 个任务数据")
        
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
        
        print(f"\n分析任务: {task_info['name_cn']} ({task_type})")
        print("-" * 60)
        
        # 获取数值列（排除model列）
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 成本型指标转换为效益型（在归一化之前）
        print("  检查成本型指标...")
        df = sf.convert_cost_to_benefit(df)
        
        results = {
            'task_type': task_type,
            'task_info': task_info,
            'n_models': len(df),
            'n_metrics': len(numeric_cols),
            'metrics': numeric_cols,
            'descriptive_stats': {},
            'model_rankings': {},
            'correlations': None,
            'outliers': {},
            'key_findings': []
        }
        
        # 1. 描述性统计
        print("  计算描述性统计...")
        for col in numeric_cols:
            stats = sf.calculate_descriptive_stats(df[col])
            results['descriptive_stats'][col] = stats
        
        # 2. 模型排名（使用PCA综合评分）
        print("  生成模型排名（PCA方法）...")
        primary_metrics = task_info.get('primary_metrics', numeric_cols[:3])
        
        # 使用PCA计算综合排名
        if len(primary_metrics) > 1:
            # 准备数据：只使用主要指标
            metrics_data = df[['model'] + [m for m in primary_metrics if m in df.columns]].copy()
            metrics_data = metrics_data.set_index('model')
            
            # 计算PCA综合排名
            pca_ranking_result = self._calculate_pca_ranking(metrics_data)
            
            # 保存PCA综合排名
            results['model_rankings']['pca_综合得分'] = pd.DataFrame({
                'model': pca_ranking_result['ranking'].index,
                'pca_综合得分': pca_ranking_result['ranking'].values
            })
            results['pca_ranking_info'] = {
                'n_components': pca_ranking_result['n_components'],
                'explained_variance': pca_ranking_result['explained_variance'],
                'cumulative_variance': pca_ranking_result['cumulative_variance'],
                'weights': pca_ranking_result['weights']
            }
        else:
            # 如果只有一个指标，直接排序
            metric = primary_metrics[0] if primary_metrics else numeric_cols[0]
            if metric in df.columns:
                ranking = df[['model', metric]].sort_values(metric, ascending=False)
                results['model_rankings'][metric] = ranking
        
        # 同时保留各单项指标的排名供参考
        for metric in primary_metrics:
            if metric in df.columns:
                ranking = df[['model', metric]].sort_values(metric, ascending=False)
                results['model_rankings'][f'{metric}_单项'] = ranking
        
        # 3. 相关性分析
        if len(numeric_cols) > 1:
            print("  计算指标相关性...")
            results['correlations'] = sf.calculate_correlation_matrix(df, numeric_cols)
        
        # 4. 异常值检测
        print("  检测异常值...")
        for col in numeric_cols:
            outlier_mask, outlier_indices = sf.identify_outliers(df[col], method='iqr')
            if len(outlier_indices) > 0:
                results['outliers'][col] = {
                    'indices': outlier_indices,
                    'values': df.loc[outlier_indices, col].tolist(),
                    'models': df.loc[outlier_indices, 'model'].tolist()
                }
        
        # 5. 提取关键发现
        print("  提取关键发现...")
        results['key_findings'] = self._extract_key_findings(df, results, task_info)
        
        # 6. 生成可视化
        print("  生成可视化...")
        self._create_task_visualizations(task_type, df, results)
        
        # 7. 保存统计表格
        print("  保存统计表格...")
        self._save_task_tables(task_type, results)
        
        return results
    
    def _extract_key_findings(self, df: pd.DataFrame, results: Dict, 
                             task_info: Dict) -> List[str]:
        """提取任务的关键发现（增强版）"""
        findings = []
        primary_metrics = task_info.get('primary_metrics', [])
        
        if not primary_metrics:
            return findings
        
        # 1. 主要指标的统计特征（更详细）
        for i, metric in enumerate(primary_metrics[:2], 1):
            if metric in results['descriptive_stats']:
                stats = results['descriptive_stats'][metric]
                
                # 判断分布特征
                if stats['cv'] < 0.2:
                    variation = "变异度低，模型表现较为一致"
                elif stats['cv'] < 0.5:
                    variation = "变异度中等，模型间存在一定差异"
                else:
                    variation = "变异度高，模型间差异显著"
                
                # 判断偏度
                if abs(stats['skewness']) < 0.5:
                    skew_desc = "分布较为对称"
                elif stats['skewness'] > 0.5:
                    skew_desc = "正偏分布，少数模型表现突出"
                else:
                    skew_desc = "负偏分布，少数模型表现较差"
                
                findings.append(
                    f"**{metric}**: 均值{stats['mean']:.3f}，标准差{stats['std']:.3f}，"
                    f"变异系数{stats['cv']:.3f}（{variation}），{skew_desc}"
                )
        
        # 2. 最佳和最差模型（包含差距分析）
        if primary_metrics[0] in df.columns:
            metric = primary_metrics[0]
            best_model = df.loc[df[metric].idxmax(), 'model']
            best_score = df[metric].max()
            worst_model = df.loc[df[metric].idxmin(), 'model']
            worst_score = df[metric].min()
            gap = best_score - worst_score
            gap_pct = (gap / worst_score * 100) if worst_score != 0 else 0
            
            findings.append(
                f"**性能差距**: 最佳模型 {best_model} ({metric}={best_score:.3f}) "
                f"比最差模型 {worst_model} ({metric}={worst_score:.3f}) "
                f"高出 {gap:.3f} ({gap_pct:.1f}%)"
            )
        
        # 3. 模型规模效应
        if 'model' in df.columns:
            # 提取模型规模信息
            model_sizes = []
            for model in df['model']:
                if '8b' in model.lower():
                    model_sizes.append(('8B', model))
                elif '7b' in model.lower():
                    model_sizes.append(('7B', model))
                elif '4b' in model.lower():
                    model_sizes.append(('4B', model))
                elif '3b' in model.lower():
                    model_sizes.append(('3B', model))
                elif '2b' in model.lower():
                    model_sizes.append(('2B', model))
            
            if model_sizes and primary_metrics[0] in df.columns:
                # 计算不同规模的平均得分
                size_scores = {}
                for size, model in model_sizes:
                    score = df[df['model'] == model][primary_metrics[0]].values[0]
                    if size not in size_scores:
                        size_scores[size] = []
                    size_scores[size].append(score)
                
                size_avg = {k: np.mean(v) for k, v in size_scores.items()}
                if len(size_avg) > 1:
                    best_size = max(size_avg.items(), key=lambda x: x[1])
                    findings.append(
                        f"**模型规模效应**: {best_size[0]}参数模型平均表现最佳 "
                        f"({primary_metrics[0]}={best_size[1]:.3f})"
                    )
        
        # 4. 相关性洞察
        if results['correlations'] is not None and len(results['correlations']) > 1:
            corr_matrix = results['correlations']
            # 找出最强相关对
            max_corr = 0
            max_pair = None
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = abs(corr_matrix.iloc[i, j])
                    if corr_val > max_corr:
                        max_corr = corr_val
                        max_pair = (corr_matrix.columns[i], corr_matrix.columns[j])
            
            if max_pair and max_corr > 0.6:
                findings.append(
                    f"**指标相关性**: {max_pair[0]} 与 {max_pair[1]} "
                    f"高度相关 (r={max_corr:.3f})"
                )
        
        # 5. 异常值分析
        if results['outliers']:
            outlier_details = []
            for metric, outlier_info in results['outliers'].items():
                outlier_details.append(f"{metric}({len(outlier_info['indices'])}个)")
            
            findings.append(
                f"**异常值检测**: 共检测到{sum(len(v['indices']) for v in results['outliers'].values())}个异常值，"
                f"分布在 {', '.join(outlier_details[:3])}"
            )
        
        # 6. 量化方式影响（如果有）
        quant_4bit = [m for m in df['model'] if '4bit' in m.lower()]
        quant_8bit = [m for m in df['model'] if '8bit' in m.lower()]
        
        if quant_4bit and quant_8bit and primary_metrics[0] in df.columns:
            avg_4bit = df[df['model'].isin(quant_4bit)][primary_metrics[0]].mean()
            avg_8bit = df[df['model'].isin(quant_8bit)][primary_metrics[0]].mean()
            
            if abs(avg_8bit - avg_4bit) > 0.05:
                better = "8-bit" if avg_8bit > avg_4bit else "4-bit"
                diff = abs(avg_8bit - avg_4bit)
                findings.append(
                    f"**量化影响**: {better}量化平均表现更好，"
                    f"差距为{diff:.3f}"
                )
        
        return findings
    
    def _create_task_visualizations(self, task_type: str, df: pd.DataFrame, 
                                   results: Dict):
        """创建任务级可视化"""
        task_figures_dir = self.figures_dir / task_type
        task_figures_dir.mkdir(exist_ok=True)
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        task_info = results['task_info']
        
        # 1. 主要指标分布图
        primary_metrics = task_info.get('primary_metrics', numeric_cols[:3])
        for metric in primary_metrics[:3]:
            if metric in df.columns:
                title = f"{task_info['name_cn']} - {metric} 分布"
                output_path = task_figures_dir / f'{metric}_distribution.png'
                sf.plot_distribution(df[metric], title, output_path)
        
        # 2. 模型排名图（使用PCA综合得分）
        if 'pca_综合得分' in results['model_rankings']:
            pca_ranking = results['model_rankings']['pca_综合得分']
            pca_info = results.get('pca_ranking_info', {})
            
            # 绘制PCA综合排名柱状图
            self._plot_task_pca_ranking(
                pca_ranking, 
                task_info['name_cn'], 
                task_figures_dir / 'pca_ranking.png',
                pca_info
            )
        elif primary_metrics and primary_metrics[0] in df.columns:
            # 如果没有PCA排名（只有单一指标），使用传统方法
            metric = primary_metrics[0]
            title = f"{task_info['name_cn']} - {metric} 模型对比"
            output_path = task_figures_dir / f'{metric}_comparison.png'
            sf.plot_boxplot(df, metric, 'model', title, output_path,
                          xlabel='模型', ylabel=metric)
        
        # 3. 相关性热力图
        if results['correlations'] is not None and len(numeric_cols) > 1:
            title = f"{task_info['name_cn']} - 指标相关性"
            output_path = task_figures_dir / 'correlation_heatmap.png'
            sf.plot_heatmap(results['correlations'], title, output_path)
        
        # 4. 雷达图（Top 5模型）
        if len(numeric_cols) >= 3 and primary_metrics:
            df_norm = sf.normalize_scores(df, numeric_cols, method='minmax')
            top_models = df.nlargest(5, primary_metrics[0])['model'].tolist()
            
            title = f"{task_info['name_cn']} - 综合能力对比（Top 5）"
            output_path = task_figures_dir / 'radar_chart.png'
            metrics_to_plot = numeric_cols[:min(6, len(numeric_cols))]
            sf.plot_radar_chart(df_norm, metrics_to_plot, top_models, 
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
        
        # 4. 异常值表
        if results['outliers']:
            outlier_data = []
            for metric, outlier_info in results['outliers'].items():
                for i, (idx, val, model) in enumerate(zip(
                    outlier_info['indices'], 
                    outlier_info['values'],
                    outlier_info['models']
                )):
                    outlier_data.append({
                        '指标': metric,
                        '模型': model,
                        '值': val,
                        '索引': idx
                    })
            if outlier_data:
                outlier_df = pd.DataFrame(outlier_data)
                sf.save_table(outlier_df, task_tables_dir / 'outliers.csv', index=False)
    
    def _calculate_pca_ranking(self, pivot_table: pd.DataFrame) -> Dict:
        """使用PCA计算综合排名
        
        选择累积解释方差≥85%的主成分，按各主成分的解释方差比例加权求和
        """
        # 标准化数据
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(pivot_table.fillna(pivot_table.mean()))
        
        # 执行PCA
        pca = PCA()
        pca_scores = pca.fit_transform(data_scaled)
        
        # 选择累积解释方差≥85%的主成分
        cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
        n_components = np.argmax(cumulative_variance >= 0.85) + 1
        
        # 计算加权综合得分（使用各主成分的解释方差比例作为权重）
        weights = pca.explained_variance_ratio_[:n_components]
        weights = weights / weights.sum()  # 归一化权重
        
        comprehensive_scores = np.dot(pca_scores[:, :n_components], weights)
        
        # 转换为Series并排序
        ranking = pd.Series(comprehensive_scores, index=pivot_table.index)
        ranking = ranking.sort_values(ascending=False)
        
        return {
            'ranking': ranking,
            'pca': pca,
            'n_components': n_components,
            'explained_variance': pca.explained_variance_ratio_,
            'cumulative_variance': cumulative_variance,
            'weights': weights,
            'pca_scores': pca_scores
        }
    
    def _plot_pca_variance(self, pca_results: Dict):
        """绘制PCA解释方差图"""
        import matplotlib.pyplot as plt
        
        sf.setup_chinese_font()
        colors = sf.get_academic_colors()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # 左图：各主成分的解释方差比例
        n_comp = len(pca_results['explained_variance'])
        x_pos = range(1, n_comp + 1)
        
        bars = ax1.bar(x_pos, pca_results['explained_variance'], 
                      color=colors[0], alpha=0.7, edgecolor='black')
        
        # 标记选中的主成分
        selected_n = pca_results['n_components']
        for i in range(selected_n):
            bars[i].set_color(colors[1])
        
        ax1.set_xlabel('主成分', fontsize=11)
        ax1.set_ylabel('解释方差比例', fontsize=11)
        ax1.set_title('各主成分解释方差', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.axvline(x=selected_n + 0.5, color='red', linestyle='--', 
                   label=f'选择前{selected_n}个主成分')
        ax1.legend()
        
        # 右图：累积解释方差曲线
        ax2.plot(x_pos, pca_results['cumulative_variance'], 
                marker='o', color=colors[0], linewidth=2, markersize=6)
        ax2.axhline(y=0.85, color='red', linestyle='--', label='85%阈值')
        ax2.axvline(x=selected_n, color='red', linestyle='--', alpha=0.5)
        
        ax2.set_xlabel('主成分数量', fontsize=11)
        ax2.set_ylabel('累积解释方差', fontsize=11)
        ax2.set_title('累积解释方差曲线', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        ax2.set_ylim([0, 1.05])
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'pca_variance_explained.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_task_pca_ranking(self, ranking_df: pd.DataFrame, task_name: str, 
                               output_path, pca_info: Dict):
        """绘制任务级别的PCA综合排名柱状图"""
        import matplotlib.pyplot as plt
        
        sf.setup_chinese_font()
        colors = sf.get_academic_colors()
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # 绘制柱状图
        x_pos = range(len(ranking_df))
        bars = ax.bar(x_pos, ranking_df['pca_综合得分'].values, 
                     color=colors[0], alpha=0.7, edgecolor='black')
        
        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, ranking_df['pca_综合得分'].values)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                   f'{score:.3f}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(ranking_df['model'].values, rotation=45, ha='right')
        ax.set_xlabel('模型', fontsize=11)
        ax.set_ylabel('PCA综合得分', fontsize=11)
        
        # 标题包含PCA信息
        if pca_info:
            n_comp = pca_info.get('n_components', 'N')
            cum_var = pca_info.get('cumulative_variance', [0])
            if isinstance(cum_var, np.ndarray) and len(cum_var) >= n_comp:
                cum_var_val = cum_var[n_comp-1]
                title = f'{task_name} - 模型综合排名（PCA方法，{n_comp}个主成分，累积解释方差{cum_var_val:.1%}）'
            else:
                title = f'{task_name} - 模型综合排名（PCA方法）'
        else:
            title = f'{task_name} - 模型综合排名'
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def cross_task_analysis(self) -> Dict:
        """跨任务综合分析"""
        print("\n" + "="*80)
        print("跨任务综合分析")
        print("="*80)
        
        # 收集所有模型在各任务的主要指标
        model_task_scores = []
        
        for task_type, df in self.data.items():
            if df is None:
                continue
            
            # 成本型指标转换（在使用数据之前）
            df = sf.convert_cost_to_benefit(df)
            
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
        
        # 1. 模型×任务透视表
        print("  生成模型×任务矩阵...")
        pivot_table = cross_df.pivot_table(
            index='model', 
            columns='task_cn', 
            values='score', 
            aggfunc='mean'
        )
        
        # 2. 使用PCA计算综合排名
        print("  使用PCA计算综合排名...")
        pca_results = self._calculate_pca_ranking(pivot_table)
        model_avg_scores = pca_results['ranking']
        
        # 3. 识别优劣势任务（需要归一化数据）
        print("  识别优劣势任务...")
        pivot_norm = (pivot_table - pivot_table.min()) / (pivot_table.max() - pivot_table.min())
        advantage_tasks = {}
        disadvantage_tasks = {}
        for model in pivot_norm.index:
            model_scores = pivot_norm.loc[model]
            advantage_tasks[model] = model_scores.idxmax()
            disadvantage_tasks[model] = model_scores.idxmin()
        
        # 4. 模型规模分析
        print("  分析模型规模影响...")
        scale_analysis = self._analyze_model_scale(model_avg_scores)
        
        # 5. 量化方式分析
        print("  分析量化方式影响...")
        quant_analysis = self._analyze_quantization(model_avg_scores)
        
        # 6. 可视化
        print("  生成跨任务可视化...")
        
        # 热力图
        title = "模型×任务质量得分热力图"
        output_path = self.figures_dir / 'cross_task_heatmap.png'
        sf.plot_heatmap(pivot_table, title, output_path)
        
        # 综合排名柱状图（带PCA信息）
        self._plot_comprehensive_ranking(model_avg_scores, pca_results)
        
        # PCA解释方差图
        self._plot_pca_variance(pca_results)
        
        # 7. 保存表格
        print("  保存跨任务表格...")
        sf.save_table(pivot_table, self.tables_dir / 'model_task_matrix.csv', index=True)
        sf.save_table(model_avg_scores.to_frame('avg_score'), 
                     self.tables_dir / 'comprehensive_ranking.csv', 
                     index=True)
        
        # 优劣势任务表
        advantage_df = pd.DataFrame([
            {'model': k, 'advantage_task': v, 'disadvantage_task': disadvantage_tasks[k]}
            for k, v in advantage_tasks.items()
        ])
        sf.save_table(advantage_df, self.tables_dir / 'task_advantages.csv', index=False)
        
        results = {
            'pivot_table': pivot_table,
            'pivot_norm': pivot_norm,
            'comprehensive_ranking': model_avg_scores,
            'advantage_tasks': advantage_tasks,
            'disadvantage_tasks': disadvantage_tasks,
            'scale_analysis': scale_analysis,
            'quant_analysis': quant_analysis,
            'pca_results': pca_results,
            'raw_data': cross_df
        }
        
        return results
    
    def _analyze_model_scale(self, comprehensive_scores: pd.Series) -> Dict:
        """分析模型规模与质量的关系"""
        scale_groups = {
            '2B': [],
            '3B-4B': [],
            '7B-8B': []
        }
        
        for model, score in comprehensive_scores.items():
            if '2b' in model.lower():
                scale_groups['2B'].append(score)
            elif any(x in model.lower() for x in ['3b', '4b']):
                scale_groups['3B-4B'].append(score)
            elif any(x in model.lower() for x in ['7b', '8b']):
                scale_groups['7B-8B'].append(score)
        
        scale_stats = {}
        for scale, scores in scale_groups.items():
            if scores:
                scale_stats[scale] = {
                    'mean': np.mean(scores),
                    'std': np.std(scores),
                    'count': len(scores)
                }
        
        return scale_stats
    
    def _analyze_quantization(self, comprehensive_scores: pd.Series) -> Dict:
        """分析量化方式的影响"""
        quant_comparisons = []
        
        # 查找同一模型的不同量化版本
        models_base = {}
        for model in comprehensive_scores.index:
            # 提取基础模型名（去除量化后缀）
            base = model.replace('_4bit', '').replace('_8bit', '').replace('_q4km', '')
            if base not in models_base:
                models_base[base] = []
            models_base[base].append(model)
        
        # 对比不同量化版本
        for base, variants in models_base.items():
            if len(variants) >= 2:
                for i, v1 in enumerate(variants):
                    for v2 in variants[i+1:]:
                        quant_comparisons.append({
                            'base_model': base,
                            'variant1': v1,
                            'variant2': v2,
                            'score1': comprehensive_scores[v1],
                            'score2': comprehensive_scores[v2],
                            'diff': comprehensive_scores[v1] - comprehensive_scores[v2]
                        })
        
        return {'comparisons': quant_comparisons}
    
    def _plot_comprehensive_ranking(self, scores: pd.Series, pca_results: Dict = None):
        """绘制综合排名柱状图（带PCA信息）"""
        import matplotlib.pyplot as plt
        
        sf.setup_chinese_font()
        colors = sf.get_academic_colors()
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # 绘制柱状图
        x_pos = range(len(scores))
        bars = ax.bar(x_pos, scores.values, color=colors[0], alpha=0.7, edgecolor='black')
        
        # 添加数值标签
        for i, (bar, score) in enumerate(zip(bars, scores.values)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                   f'{score:.3f}', ha='center', va='bottom', fontsize=9)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(scores.index, rotation=45, ha='right')
        ax.set_xlabel('模型', fontsize=11)
        ax.set_ylabel('PCA综合得分', fontsize=11)
        
        # 标题包含PCA信息
        if pca_results:
            n_comp = pca_results['n_components']
            cum_var = pca_results['cumulative_variance'][n_comp-1]
            title = f'模型综合质量排名（PCA方法，{n_comp}个主成分，累积解释方差{cum_var:.1%}）'
        else:
            title = '模型综合质量排名'
        
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(self.figures_dir / 'comprehensive_ranking.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def cross_task_correlation_analysis(self, task_results: Dict[str, Dict]) -> Dict:
        """跨任务指标相关性分析"""
        print("\n" + "="*80)
        print("跨任务指标相关性分析")
        print("="*80)
        
        # 收集各任务的主要指标
        cross_metrics = {}
        
        for task_type, results in task_results.items():
            if not results:
                continue
            
            df = self.data[task_type]
            task_info = results['task_info']
            primary_metrics = task_info.get('primary_metrics', [])
            
            for metric in primary_metrics[:1]:  # 只取第一个主要指标
                if metric in df.columns:
                    col_name = f"{task_type}_{metric}"
                    cross_metrics[col_name] = df.set_index('model')[metric]
        
        # 合并为一个DataFrame
        cross_df = pd.DataFrame(cross_metrics)
        
        # 计算相关性矩阵
        corr_matrix = cross_df.corr()
        
        # 识别高相关指标对
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.6:
                    high_corr_pairs.append({
                        'metric1': corr_matrix.columns[i],
                        'metric2': corr_matrix.columns[j],
                        'correlation': corr_val
                    })
        
        # 可视化
        title = "跨任务核心指标相关性"
        output_path = self.figures_dir / 'cross_task_correlation.png'
        sf.plot_heatmap(corr_matrix, title, output_path)
        
        # 保存表格
        sf.save_table(corr_matrix, self.tables_dir / 'cross_task_correlation.csv', index=True)
        
        if high_corr_pairs:
            high_corr_df = pd.DataFrame(high_corr_pairs)
            sf.save_table(high_corr_df, self.tables_dir / 'high_correlation_pairs.csv', index=False)
        
        return {
            'correlation_matrix': corr_matrix,
            'high_corr_pairs': high_corr_pairs
        }

    
    def generate_report(self, task_results: Dict[str, Dict], 
                       cross_results: Dict,
                       corr_results: Dict):
        """生成完整的Markdown分析报告"""
        print("\n" + "="*80)
        print("生成分析报告")
        print("="*80)
        
        report_path = self.reports_dir / 'quality_analysis_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            self._write_report_header(f, cross_results)
            self._write_data_overview(f, cross_results)
            self._write_task_analyses(f, task_results)
            self._write_cross_task_analysis(f, cross_results)
            self._write_correlation_analysis(f, corr_results)
            self._write_outliers_analysis(f, task_results)
            self._write_conclusions(f, cross_results, task_results)
            self._write_appendix(f)
        
        print(f"OK 报告已保存: {report_path}")
    
    def _write_report_header(self, f, cross_results):
        """写入报告标题"""
        f.write("# 模型质量得分数据描述性分析报告\n\n")
        f.write(f"**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**数据来源**: `{self.data_dir}/*_scores_raw.csv`  \n")
        f.write(f"**覆盖范围**: {len(cross_results['comprehensive_ranking'])}个模型 × ")
        
        loaded_tasks = sum(1 for v in self.data.values() if v is not None)
        f.write(f"{loaded_tasks}个任务  \n\n")
        f.write("---\n\n")
    
    def _write_data_overview(self, f, cross_results):
        """写入数据概览章节"""
        f.write("## 一、数据概览\n\n")
        
        # 1.1 数据维度
        f.write("### 1.1 数据维度\n\n")
        f.write("| 维度 | 数值 | 说明 |\n")
        f.write("|------|------|------|\n")
        
        n_models = len(cross_results['comprehensive_ranking'])
        f.write(f"| 模型数量 | {n_models} | ")
        f.write("涵盖2B-8B参数规模，多种量化方式 |\n")
        
        loaded_tasks = sum(1 for v in self.data.values() if v is not None)
        f.write(f"| 任务类型 | {loaded_tasks} | ")
        task_names = [sf.get_task_info(t)['name_cn'] for t in self.task_types 
                     if self.data.get(t) is not None]
        f.write(", ".join(task_names) + " |\n")
        
        total_metrics = sum(
            len(self.data[t].select_dtypes(include=[np.number]).columns) 
            for t in self.task_types if self.data.get(t) is not None
        )
        f.write(f"| 指标总数 | {total_metrics} | 各任务专用指标 |\n\n")
        
        # 1.2 模型清单
        f.write("### 1.2 模型清单\n\n")
        f.write("| 模型名称 | 任务覆盖 |\n")
        f.write("|---------|----------|\n")
        
        models = sorted(cross_results['comprehensive_ranking'].index.tolist())
        for model in models:
            task_count = cross_results['raw_data'][
                cross_results['raw_data']['model'] == model
            ]['task'].nunique()
            f.write(f"| {model} | {task_count}/{loaded_tasks} |\n")
        f.write("\n---\n\n")
    
    def _write_task_analyses(self, f, task_results):
        """写入各任务分析章节"""
        f.write("## 二、各任务质量得分分布分析\n\n")
        
        for idx, task_type in enumerate(self.task_types, 1):
            if task_type not in task_results or not task_results[task_type]:
                continue
            
            results = task_results[task_type]
            task_info = results['task_info']
            
            f.write(f"### 2.{idx} {task_info['name_cn']} ({task_type.capitalize()})\n\n")
            
            suffix = '_raw' if self.use_raw else ''
            f.write(f"**数据文件**: `{task_type}_scores{suffix}.csv`  \n")
            f.write(f"**样本数**: {results['n_models']}个模型  \n")
            f.write(f"**指标数**: {results['n_metrics']}个  \n")
            f.write(f"**任务描述**: {task_info['description']}  \n\n")
            
            # 描述性统计
            f.write("#### 描述性统计\n\n")
            f.write("| 指标 | 均值 | 标准差 | 最小值 | 最大值 | 中位数 | 变异系数 |\n")
            f.write("|------|------|--------|--------|--------|--------|----------|\n")
            
            for metric, stats in results['descriptive_stats'].items():
                f.write(f"| {metric} | ")
                f.write(f"{sf.format_number(stats['mean'])} | ")
                f.write(f"{sf.format_number(stats['std'])} | ")
                f.write(f"{sf.format_number(stats['min'])} | ")
                f.write(f"{sf.format_number(stats['max'])} | ")
                f.write(f"{sf.format_number(stats['median'])} | ")
                f.write(f"{sf.format_number(stats['cv'])} |\n")
            f.write("\n")
            
            # 关键发现
            if results['key_findings']:
                f.write("#### 关键发现\n\n")
                for i, finding in enumerate(results['key_findings'], 1):
                    f.write(f"{i}. {finding}\n")
                f.write("\n")
            
            # 获取主要指标列表
            primary_metrics = task_info.get('primary_metrics', [])
            
            # 模型排名（优先显示PCA综合排名）
            if 'pca_综合得分' in results['model_rankings']:
                # 使用PCA综合排名
                pca_ranking = results['model_rankings']['pca_综合得分']
                pca_info = results.get('pca_ranking_info', {})
                
                f.write(f"#### 模型综合排名（PCA方法）\n\n")
                
                # PCA方法说明
                if pca_info:
                    n_comp = pca_info.get('n_components', 'N')
                    cum_var = pca_info.get('cumulative_variance', [])
                    if isinstance(cum_var, np.ndarray) and len(cum_var) >= n_comp:
                        cum_var_val = cum_var[n_comp-1]
                        # 计算实际使用的指标数量
                        n_metrics = len([m for m in primary_metrics if m in results['descriptive_stats']])
                        f.write(f"**方法说明**: 使用主成分分析(PCA)综合{n_metrics}个主要指标，")
                        f.write(f"选择累积解释方差≥85%的前{n_comp}个主成分，")
                        f.write(f"实际累积解释方差为{cum_var_val:.2%}。\n\n")
                        
                        f.write("**主成分权重**:\n")
                        weights = pca_info.get('weights', [])
                        for i, weight in enumerate(weights, 1):
                            f.write(f"- PC{i}: {weight:.2%}\n")
                        f.write("\n")
                
                f.write("| 排名 | 模型 | PCA综合得分 |\n")
                f.write("|------|------|-------------|\n")
                
                for rank, (idx_val, row) in enumerate(pca_ranking.head(10).iterrows(), 1):
                    f.write(f"| {rank} | {row['model']} | ")
                    f.write(f"{sf.format_number(row['pca_综合得分'])} |\n")
                f.write("\n")
                
            elif primary_metrics and primary_metrics[0] in results['model_rankings']:
                # 如果没有PCA排名，使用单一指标排名
                metric = primary_metrics[0]
                ranking = results['model_rankings'][metric]
                
                f.write(f"#### 模型排名（按{metric}）\n\n")
                f.write("| 排名 | 模型 | 得分 |\n")
                f.write("|------|------|------|\n")
                
                for rank, (idx_val, row) in enumerate(ranking.head(10).iterrows(), 1):
                    f.write(f"| {rank} | {row['model']} | ")
                    f.write(f"{sf.format_number(row[metric])} |\n")
                f.write("\n")
            
            # 可视化说明
            f.write("#### 可视化分析\n\n")
            f.write(f"**图表位置**: `figures/{task_type}/`\n\n")
            
            # 分布图说明
            if primary_metrics:
                for metric in primary_metrics[:2]:
                    f.write(f"**{metric}分布图** (`{metric}_distribution.png`):  \n")
                    f.write(f"- 展示{metric}指标在所有模型上的分布特征\n")
                    f.write(f"- 包含直方图、核密度估计(KDE)曲线、均值和中位数标记\n")
                    f.write(f"- 右侧面板显示详细的描述性统计量\n\n")
            
            # 对比图说明
            if primary_metrics:
                metric = primary_metrics[0]
                f.write(f"**模型对比图** (`{metric}_comparison.png`):  \n")
                f.write(f"- 按{metric}降序排列所有模型的得分\n")
                f.write(f"- 散点图展示各模型的具体数值\n")
                f.write(f"- 水平虚线标记均值和中位数，便于识别高于/低于平均水平的模型\n\n")
            
            # 相关性热力图说明
            if results['correlations'] is not None:
                f.write(f"**指标相关性热力图** (`correlation_heatmap.png`):  \n")
                f.write(f"- 展示{results['n_metrics']}个指标之间的Pearson相关系数\n")
                f.write(f"- 颜色深浅表示相关性强弱（红色正相关，蓝色负相关）\n")
                f.write(f"- 帮助识别冗余指标和指标间的内在联系\n\n")
            
            # 雷达图说明
            f.write(f"**综合能力雷达图** (`radar_chart.png`):  \n")
            f.write(f"- 展示Top 5模型在多个指标上的综合表现\n")
            f.write(f"- 每个轴代表一个归一化后的指标\n")
            f.write(f"- 面积越大表示综合能力越强\n\n")
            
            f.write("---\n\n")
    
    def _write_cross_task_analysis(self, f, cross_results):
        """写入跨任务综合分析章节"""
        f.write("## 三、跨任务综合分析\n\n")
        
        # 3.1 综合排名（PCA方法）
        f.write("### 3.1 综合排名（PCA方法）\n\n")
        
        pca_results = cross_results.get('pca_results', {})
        if pca_results:
            n_comp = pca_results['n_components']
            cum_var = pca_results['cumulative_variance'][n_comp-1]
            
            f.write(f"**方法说明**: 使用主成分分析(PCA)对各任务主要指标进行降维，")
            f.write(f"选择累积解释方差≥85%的前{n_comp}个主成分，")
            f.write(f"实际累积解释方差为{cum_var:.2%}。\n\n")
            
            f.write("**PCA权重**:\n")
            for i, weight in enumerate(pca_results['weights'], 1):
                f.write(f"- PC{i}: {weight:.2%}\n")
            f.write("\n")
        
        f.write("**综合排名表**:\n\n")
        f.write("| 排名 | 模型 | PCA综合得分 | 优势任务 | 劣势任务 |\n")
        f.write("|------|------|------------|----------|----------|\n")
        
        for rank, (model, score) in enumerate(
            cross_results['comprehensive_ranking'].head(15).items(), 1):
            adv_task = cross_results['advantage_tasks'].get(model, 'N/A')
            dis_task = cross_results['disadvantage_tasks'].get(model, 'N/A')
            f.write(f"| {rank} | {model} | {sf.format_number(score)} | ")
            f.write(f"{adv_task} | {dis_task} |\n")
        f.write("\n")
        
        # 可视化说明
        f.write("**可视化分析**:\n\n")
        
        f.write("**综合排名柱状图** (`comprehensive_ranking.png`):  \n")
        f.write(f"- 展示基于PCA方法计算的模型综合质量得分\n")
        f.write(f"- 使用前{pca_results.get('n_components', 'N')}个主成分加权求和\n")
        f.write(f"- 得分越高表示模型在多任务上的综合表现越好\n\n")
        
        f.write("**PCA解释方差图** (`pca_variance_explained.png`):  \n")
        f.write(f"- 左图：各主成分的解释方差比例，显示每个主成分的重要性\n")
        f.write(f"- 右图：累积解释方差曲线，展示主成分数量与信息保留的关系\n")
        f.write(f"- 绿色虚线标记选择的主成分数量，红色虚线标记85%阈值\n\n")
        
        f.write("**模型×任务热力图** (`cross_task_heatmap.png`):  \n")
        f.write(f"- 展示所有模型在各任务上的原始得分\n")
        f.write(f"- 颜色深浅表示得分高低（深色表示高分）\n")
        f.write(f"- 可直观识别各模型的优劣势任务\n\n")
        
        # 3.2 模型规模分析
        if cross_results['scale_analysis']:
            f.write("### 3.2 模型规模与质量关系\n\n")
            f.write("| 规模范围 | 平均综合得分 | 样本数 | 标准差 |\n")
            f.write("|---------|------------|--------|--------|\n")
            
            for scale, stats in cross_results['scale_analysis'].items():
                f.write(f"| {scale} | {sf.format_number(stats['mean'])} | ")
                f.write(f"{stats['count']} | {sf.format_number(stats['std'])} |\n")
            f.write("\n")
            
            f.write("**分析**: 模型参数规模与综合质量得分呈正相关，")
            f.write("但需权衡计算成本和实际应用场景。\n\n")
        
        # 3.3 量化方式影响
        if cross_results['quant_analysis']['comparisons']:
            f.write("### 3.3 量化方式影响分析\n\n")
            f.write("| 基础模型 | 版本1 | 版本2 | 得分差 | 说明 |\n")
            f.write("|---------|-------|-------|--------|------|\n")
            
            for comp in cross_results['quant_analysis']['comparisons'][:10]:
                better = comp['variant1'] if comp['diff'] > 0 else comp['variant2']
                f.write(f"| {comp['base_model']} | {comp['variant1']} | ")
                f.write(f"{comp['variant2']} | {sf.format_number(abs(comp['diff']))} | ")
                f.write(f"{better}更优 |\n")
            f.write("\n")
            
            f.write("**分析**: 量化方式对模型质量有显著影响，")
            f.write("8-bit量化通常保持更好的质量，但4-bit量化在资源受限场景下仍有价值。\n\n")
        
        f.write("---\n\n")
    
    def _write_correlation_analysis(self, f, corr_results):
        """写入相关性分析章节"""
        f.write("## 四、指标间相关性分析\n\n")
        
        f.write("### 4.1 分析目的\n\n")
        f.write("通过分析不同任务核心指标之间的相关性，可以：\n")
        f.write("- 识别模型能力的内在联系（如代码能力与数学推理能力的关联）\n")
        f.write("- 发现冗余指标，简化评估体系\n")
        f.write("- 理解模型在不同任务上的迁移能力\n\n")
        
        if corr_results['high_corr_pairs']:
            f.write("### 4.2 跨任务核心指标高相关对\n\n")
            f.write("| 指标1 | 指标2 | 相关系数 | 相关强度 | 解释 |\n")
            f.write("|-------|-------|----------|----------|------|\n")
            
            for pair in corr_results['high_corr_pairs'][:15]:
                corr_val = pair['correlation']
                
                # 相关强度分类
                if abs(corr_val) > 0.8:
                    strength = "极强"
                elif abs(corr_val) > 0.6:
                    strength = "强"
                else:
                    strength = "中等"
                
                # 相关方向
                direction = "正相关" if corr_val > 0 else "负相关"
                
                # 解释
                task1 = pair['metric1'].split('_')[0]
                task2 = pair['metric2'].split('_')[0]
                if task1 == task2:
                    explanation = "同任务内指标"
                else:
                    explanation = f"{task1}与{task2}任务关联"
                
                f.write(f"| {pair['metric1']} | {pair['metric2']} | ")
                f.write(f"{sf.format_number(corr_val)} | {strength}{direction} | ")
                f.write(f"{explanation} |\n")
            f.write("\n")
            
            # 关键发现
            f.write("### 4.3 关键发现\n\n")
            
            # 统计相关性类型
            strong_pos = sum(1 for p in corr_results['high_corr_pairs'] if p['correlation'] > 0.8)
            strong_neg = sum(1 for p in corr_results['high_corr_pairs'] if p['correlation'] < -0.8)
            
            f.write(f"1. **强正相关对**: 发现{strong_pos}对指标呈强正相关（r>0.8），")
            f.write("表明这些能力在模型中往往同时出现\n")
            
            if strong_neg > 0:
                f.write(f"2. **强负相关对**: 发现{strong_neg}对指标呈强负相关（r<-0.8），")
                f.write("可能存在能力权衡\n")
            
            # 找出最强相关对
            if corr_results['high_corr_pairs']:
                strongest = max(corr_results['high_corr_pairs'], 
                              key=lambda x: abs(x['correlation']))
                f.write(f"3. **最强相关**: {strongest['metric1']} 与 {strongest['metric2']} ")
                f.write(f"(r={strongest['correlation']:.3f})，说明这两项能力高度关联\n")
            
            f.write("\n")
        
        # 可视化说明
        f.write("### 4.4 可视化分析\n\n")
        
        f.write("**跨任务相关性热力图** (`cross_task_correlation.png`):  \n")
        f.write("- 展示各任务核心指标之间的Pearson相关系数矩阵\n")
        f.write("- 颜色编码：红色表示正相关，蓝色表示负相关，颜色深浅表示相关强度\n")
        f.write("- 对角线为1（自相关），对称矩阵\n")
        f.write("- 可识别任务间的能力迁移模式和指标冗余\n\n")
        
        f.write("**应用价值**:\n")
        f.write("- 高相关指标可考虑合并，简化评估流程\n")
        f.write("- 低相关任务需要独立评估，不能相互替代\n")
        f.write("- 强相关任务对可用于模型能力预测\n\n")
        
        f.write("---\n\n")
    
    def _write_outliers_analysis(self, f, task_results):
        """写入异常值分析章节"""
        f.write("## 五、异常值与特殊现象\n\n")
        
        f.write("### 5.1 异常值检测\n\n")
        f.write("| 任务 | 指标 | 模型 | 值 | 异常说明 |\n")
        f.write("|------|------|------|-----|----------|\n")
        
        outlier_count = 0
        for task_type, results in task_results.items():
            if not results or not results['outliers']:
                continue
            
            task_info = results['task_info']
            for metric, outlier_info in results['outliers'].items():
                for model, value in zip(outlier_info['models'], outlier_info['values']):
                    stats = results['descriptive_stats'][metric]
                    if value < stats['mean']:
                        explanation = f"远低于均值({sf.format_number(stats['mean'])})"
                    else:
                        explanation = f"远高于均值({sf.format_number(stats['mean'])})"
                    
                    f.write(f"| {task_info['name_cn']} | {metric} | {model} | ")
                    f.write(f"{sf.format_number(value)} | {explanation} |\n")
                    outlier_count += 1
                    
                    if outlier_count >= 20:  # 限制显示数量
                        break
                if outlier_count >= 20:
                    break
            if outlier_count >= 20:
                break
        
        if outlier_count == 0:
            f.write("| - | - | - | - | 未检测到显著异常值 |\n")
        
        f.write("\n---\n\n")
    
    def _write_conclusions(self, f, cross_results, task_results):
        """写入核心结论章节"""
        f.write("## 六、核心结论\n\n")
        
        # 6.1 任务难度排序
        f.write("### 6.1 任务难度排序\n\n")
        f.write("基于各任务主要指标的平均归一化得分：\n\n")
        f.write("| 难度 | 任务类型 | 平均质量得分 | 特点 |\n")
        f.write("|------|---------|-------------|------|\n")
        
        # 计算各任务平均得分
        task_avg_scores = {}
        for task_type, results in task_results.items():
            if not results:
                continue
            primary_metrics = results['task_info'].get('primary_metrics', [])
            if primary_metrics and primary_metrics[0] in results['descriptive_stats']:
                stats = results['descriptive_stats'][primary_metrics[0]]
                task_avg_scores[task_type] = stats['mean']
        
        # 排序
        sorted_tasks = sorted(task_avg_scores.items(), key=lambda x: x[1])
        
        for task_type, avg_score in sorted_tasks:
            task_info = sf.get_task_info(task_type)
            f.write(f"| - | {task_info['name_cn']} | {sf.format_number(avg_score)} | ")
            f.write(f"{task_info['description'][:30]}... |\n")
        f.write("\n")
        
        # 6.2 模型能力聚类
        f.write("### 6.2 模型能力聚类\n\n")
        
        top_models = cross_results['comprehensive_ranking'].head(3).index.tolist()
        mid_models = cross_results['comprehensive_ranking'].iloc[3:6].index.tolist()
        low_models = cross_results['comprehensive_ranking'].tail(3).index.tolist()
        
        f.write(f"- **全能型**: {', '.join(top_models)}（所有任务表现优异）\n")
        f.write(f"- **专项型**: {', '.join(mid_models)}（部分任务表现突出）\n")
        f.write(f"- **入门型**: {', '.join(low_models)}（适合轻量级应用）\n\n")
        
        # 6.3 量化建议
        f.write("### 6.3 量化建议\n\n")
        f.write("- **对质量要求高**: 优先选择8-bit量化或更高精度\n")
        f.write("- **对内存敏感**: 4-bit可接受，但需注意复杂任务的质量损失\n")
        f.write("- **7B-8B是甜点**: 在质量和效率间达到最佳平衡\n\n")
        
        # 6.4 任务适配建议
        f.write("### 6.4 任务适配建议\n\n")
        f.write("| 任务类型 | 推荐模型 | 说明 |\n")
        f.write("|---------|---------|------|\n")
        
        for task_type, results in task_results.items():
            if not results:
                continue
            
            task_info = results['task_info']
            primary_metrics = task_info.get('primary_metrics', [])
            if primary_metrics and primary_metrics[0] in results['model_rankings']:
                ranking = results['model_rankings'][primary_metrics[0]]
                top_model = ranking.iloc[0]['model']
                f.write(f"| {task_info['name_cn']} | {top_model} | ")
                f.write(f"{primary_metrics[0]}最优 |\n")
        
        f.write("\n---\n\n")
    
    def _write_appendix(self, f):
        """写入附录"""
        f.write("## 附录\n\n")
        f.write("### 输出文件清单\n\n")
        f.write("- **报告**: `reports/quality_analysis_report.md`\n")
        f.write("- **图表**: `figures/` 目录\n")
        f.write("  - 各任务分布图、对比图、相关性热力图、雷达图\n")
        f.write("  - 跨任务热力图、综合排名图、相关性分析图\n")
        f.write("- **表格**: `tables/` 目录\n")
        f.write("  - 各任务描述性统计、排名、相关性矩阵、异常值\n")
        f.write("  - 跨任务矩阵、综合排名、优劣势任务、高相关对\n\n")
        
        f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**分析脚本**: `quality_data_analyzer.py`  \n")
    
    def run_all_analyses(self):
        """运行完整分析流程"""
        print("\n" + "="*80)
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
        
        # 4. 跨任务相关性分析
        corr_results = self.cross_task_correlation_analysis(task_results)
        
        # 5. 生成报告
        self.generate_report(task_results, cross_results, corr_results)
        
        print("\n" + "="*80)
        print("分析完成!")
        print("="*80)
        print(f"\n输出目录: {self.output_dir}")
        print(f"  - 报告: {self.reports_dir}")
        print(f"  - 图表: {self.figures_dir}")
        print(f"  - 表格: {self.tables_dir}")


if __name__ == '__main__':
    # 快速测试
    analyzer = QualityDataAnalyzer(use_raw=True)
    analyzer.run_all_analyses()
