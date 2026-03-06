"""
综合质效比分析脚本
执行完整的质量-效率分析流程
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple
import warnings

from data.analize.pipeline import ExperimentDataManager

warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis/qe_research/logs/analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ComprehensiveAnalyzer:
    """综合分析器"""
    
    def __init__(self, config_path: str = 'analysis/qe_research/configs/analysis_config.yaml'):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        self.dm = ExperimentDataManager()
        self.results = {}
        
        # 设置中文字体
        self._setup_chinese_font()
        
        # 创建输出目录
        self._create_output_dirs()
        
        logger.info("综合分析器初始化完成")
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _setup_chinese_font(self):
        """设置中文字体"""
        if self.config['visualization']['use_chinese']:
            try:
                plt.rcParams['font.sans-serif'] = [self.config['visualization']['font']['family']]
                plt.rcParams['axes.unicode_minus'] = False
                logger.info(f"中文字体设置: {self.config['visualization']['font']['family']}")
            except Exception as e:
                logger.warning(f"中文字体设置失败: {e}")
    
    def _create_output_dirs(self):
        """创建输出目录"""
        for key in ['figures_dir', 'tables_dir', 'reports_dir', 'exports_dir']:
            Path(self.config['output'][key]).mkdir(parents=True, exist_ok=True)
    
    def run_full_analysis(self):
        """运行完整分析流程"""
        logger.info("=" * 80)
        logger.info("开始综合质效比分析")
        logger.info("=" * 80)
        
        # 1. 加载数据
        logger.info("\n[1/8] 加载数据...")
        self.df = self.dm.load_all_data()
        logger.info(f"数据加载完成: {len(self.df)} 行, {len(self.df.columns)} 列")
        
        # 2. 数据概览
        logger.info("\n[2/8] 数据概览...")
        self.data_overview()
        
        # 3. 性能分析
        logger.info("\n[3/8] 性能分析...")
        self.performance_analysis()
        
        # 4. 效率分析
        logger.info("\n[4/8] 效率分析...")
        self.efficiency_analysis()
        
        # 5. 质量分析
        logger.info("\n[5/8] 质量分析...")
        self.quality_analysis()
        
        # 6. 质效比计算
        logger.info("\n[6/8] 质效比计算...")
        self.compute_qe_ratios()
        
        # 7. 公平性分析
        logger.info("\n[7/8] 公平性分析...")
        self.fairness_analysis()
        
        # 8. 生成报告
        logger.info("\n[8/8] 生成报告...")
        self.generate_report()
        
        logger.info("\n" + "=" * 80)
        logger.info("分析完成!")
        logger.info("=" * 80)
        logger.info(f"报告位置: {self.config['output']['reports_dir']}/comprehensive_report.md")
        logger.info(f"图表位置: {self.config['output']['figures_dir']}/")
        logger.info(f"数据表位置: {self.config['output']['tables_dir']}/")
    
    def data_overview(self):
        """数据概览"""
        overview = {
            'total_records': len(self.df),
            'models': self.df['model_name'].nunique(),
            'tasks': self.df['task_type'].nunique(),
            'model_list': sorted(self.df['model_name'].unique().tolist()),
            'task_list': sorted(self.df['task_type'].unique().tolist()),
        }
        
        self.results['overview'] = overview
        
        # 打印概览
        print("\n数据概览:")
        print(f"  总记录数: {overview['total_records']}")
        print(f"  模型数量: {overview['models']}")
        print(f"  任务类型: {overview['tasks']}")
        print(f"\n模型列表:")
        for model in overview['model_list']:
            count = len(self.df[self.df['model_name'] == model])
            print(f"    - {model}: {count} 条记录")
        print(f"\n任务列表:")
        for task in overview['task_list']:
            count = len(self.df[self.df['task_type'] == task])
            print(f"    - {task}: {count} 条记录")
        
        # 保存概览表
        overview_df = pd.DataFrame([
            {'指标': '总记录数', '值': overview['total_records']},
            {'指标': '模型数量', '值': overview['models']},
            {'指标': '任务类型数', '值': overview['tasks']},
        ])
        self._save_table(overview_df, 'data_overview.csv')
    
    def performance_analysis(self):
        """性能分析"""
        perf_cols = ['latency_s', 'toks_per_s', 'ttft_s']
        available_cols = [col for col in perf_cols if col in self.df.columns]
        
        if not available_cols:
            logger.warning("未找到性能指标列")
            return
        
        # 按模型统计
        perf_by_model = self.df.groupby('model_name')[available_cols].agg(['mean', 'std', 'min', 'max'])
        self.results['performance_by_model'] = perf_by_model
        
        # 保存表格
        perf_by_model_flat = perf_by_model.reset_index()
        perf_by_model_flat.columns = ['_'.join(col).strip('_') for col in perf_by_model_flat.columns.values]
        self._save_table(perf_by_model_flat, 'performance_by_model.csv')
        
        # 可视化: 延迟 vs 吞吐量
        if 'latency_s' in self.df.columns and 'toks_per_s' in self.df.columns:
            self._plot_latency_vs_throughput()
        
        print("\n性能分析完成")
        print(f"  平均延迟: {self.df['latency_s'].mean():.3f}s" if 'latency_s' in self.df.columns else "")
        print(f"  平均吞吐量: {self.df['toks_per_s'].mean():.2f} tokens/s" if 'toks_per_s' in self.df.columns else "")
    
    def efficiency_analysis(self):
        """效率分析"""
        eff_cols = ['gpu_energy_j', 'cpu_usage_avg', 'memory_used_avg_mb', 'gpu_util_avg']
        available_cols = [col for col in eff_cols if col in self.df.columns]
        
        if not available_cols:
            logger.warning("未找到效率指标列")
            return
        
        # 按模型统计
        eff_by_model = self.df.groupby('model_name')[available_cols].agg(['mean', 'std', 'min', 'max'])
        self.results['efficiency_by_model'] = eff_by_model
        
        # 保存表格
        eff_by_model_flat = eff_by_model.reset_index()
        eff_by_model_flat.columns = ['_'.join(col).strip('_') for col in eff_by_model_flat.columns.values]
        self._save_table(eff_by_model_flat, 'efficiency_by_model.csv')
        
        # 可视化: 能耗分布
        if 'gpu_energy_j' in self.df.columns:
            self._plot_energy_distribution()
        
        print("\n效率分析完成")
        print(f"  平均GPU能耗: {self.df['gpu_energy_j'].mean():.2f}J" if 'gpu_energy_j' in self.df.columns else "")
        print(f"  平均CPU使用率: {self.df['cpu_usage_avg'].mean():.1f}%" if 'cpu_usage_avg' in self.df.columns else "")
    
    def quality_analysis(self):
        """质量分析"""
        quality_cols = ['bartscore']
        available_cols = [col for col in quality_cols if col in self.df.columns]
        
        if not available_cols:
            logger.warning("未找到质量指标列")
            return
        
        # 按模型和任务统计
        quality_by_model_task = self.df.groupby(['model_name', 'task_type'])[available_cols].mean()
        self.results['quality_by_model_task'] = quality_by_model_task
        
        # 保存表格
        quality_table = quality_by_model_task.reset_index()
        self._save_table(quality_table, 'quality_by_model_task.csv')
        
        # 可视化: 质量热力图
        if 'bartscore' in self.df.columns:
            self._plot_quality_heatmap()
        
        print("\n质量分析完成")
        print(f"  平均BARTScore: {self.df['bartscore'].mean():.4f}" if 'bartscore' in self.df.columns else "")
    
    def compute_qe_ratios(self):
        """计算质效比"""
        # 归一化指标
        df_norm = self.df.copy()
        
        # 按任务分组归一化
        for task in df_norm['task_type'].unique():
            mask = df_norm['task_type'] == task
            
            # 归一化质量
            if 'bartscore' in df_norm.columns:
                df_norm.loc[mask, 'norm_quality'] = self._normalize(df_norm.loc[mask, 'bartscore'])
            
            # 归一化性能指标
            if 'toks_per_s' in df_norm.columns:
                df_norm.loc[mask, 'norm_throughput'] = self._normalize(df_norm.loc[mask, 'toks_per_s'])
            if 'latency_s' in df_norm.columns:
                df_norm.loc[mask, 'norm_latency'] = self._normalize(df_norm.loc[mask, 'latency_s'])
            if 'gpu_energy_j' in df_norm.columns:
                df_norm.loc[mask, 'norm_energy'] = self._normalize(df_norm.loc[mask, 'gpu_energy_j'])
        
        # 计算效率得分
        weights = self.config['weights']['efficiency']
        if all(col in df_norm.columns for col in ['norm_throughput', 'norm_latency', 'norm_energy']):
            df_norm['efficiency_score'] = (
                weights['throughput'] * df_norm['norm_throughput'] +
                weights['latency'] * (1 - df_norm['norm_latency']) +
                weights['energy'] * (1 - df_norm['norm_energy'])
            )
        
        # 计算质效比
        epsilon = self.config['qe_ratio']['epsilon']
        if 'norm_quality' in df_norm.columns and 'efficiency_score' in df_norm.columns:
            df_norm['qe_ratio'] = (
                (df_norm['norm_quality'] + epsilon) / 
                (1 + epsilon - df_norm['efficiency_score'])
            )
        
        self.df_norm = df_norm
        
        # 按模型排名
        if 'qe_ratio' in df_norm.columns:
            qe_ranking = df_norm.groupby('model_name')['qe_ratio'].mean().sort_values(ascending=False)
            self.results['qe_ranking'] = qe_ranking
            
            print("\n质效比排名 (Top 10):")
            for i, (model, score) in enumerate(qe_ranking.head(10).items(), 1):
                print(f"  {i}. {model}: {score:.4f}")
            
            # 保存排名表
            ranking_df = qe_ranking.reset_index()
            ranking_df.columns = ['模型', '质效比']
            self._save_table(ranking_df, 'qe_ranking.csv')
            
            # 可视化: 质效比柱状图
            self._plot_qe_ranking()
        
        # 保存归一化数据
        export_cols = ['model_name', 'task_type', 'norm_quality', 'efficiency_score', 'qe_ratio']
        export_cols = [col for col in export_cols if col in df_norm.columns]
        self._save_export(df_norm[export_cols], 'normalized_scores.csv')
    
    def fairness_analysis(self):
        """公平性分析"""
        if 'norm_quality' not in self.df_norm.columns:
            logger.warning("未找到归一化质量指标，跳过公平性分析")
            return
        
        fairness_results = {}
        
        # 1. Fairness Gap - 按任务分组
        for model in self.df_norm['model_name'].unique():
            model_data = self.df_norm[self.df_norm['model_name'] == model]
            
            # 计算每个任务的平均质量
            task_quality = model_data.groupby('task_type')['norm_quality'].mean()
            global_quality = model_data['norm_quality'].mean()
            
            # Fairness Gap = max |task_quality - global_quality|
            fairness_gap = (task_quality - global_quality).abs().max()
            
            fairness_results[model] = {
                'fairness_gap': fairness_gap,
                'global_quality': global_quality,
                'task_quality': task_quality.to_dict()
            }
        
        # 2. Gini系数
        for model in self.df_norm['model_name'].unique():
            model_data = self.df_norm[self.df_norm['model_name'] == model]
            gini = self._compute_gini(model_data['norm_quality'].values)
            fairness_results[model]['gini'] = gini
        
        # 3. Nash Social Welfare
        if self.config['fairness']['nash_social_welfare']['enabled']:
            epsilon = self.config['fairness']['nash_social_welfare']['epsilon']
            for model in self.df_norm['model_name'].unique():
                model_data = self.df_norm[self.df_norm['model_name'] == model]
                task_quality = model_data.groupby('task_type')['norm_quality'].mean()
                nsw = np.sum(np.log(task_quality + epsilon))
                fairness_results[model]['nash_social_welfare'] = nsw
        
        self.results['fairness'] = fairness_results
        
        # 创建公平性汇总表
        fairness_df = pd.DataFrame([
            {
                '模型': model,
                'Fairness Gap': data['fairness_gap'],
                'Gini系数': data['gini'],
                'Nash Social Welfare': data.get('nash_social_welfare', np.nan)
            }
            for model, data in fairness_results.items()
        ])
        fairness_df = fairness_df.sort_values('Fairness Gap')
        self._save_table(fairness_df, 'fairness_metrics.csv')
        
        print("\n公平性分析完成")
        print(f"  最公平模型 (最小Fairness Gap): {fairness_df.iloc[0]['模型']}")
        print(f"  Fairness Gap: {fairness_df.iloc[0]['Fairness Gap']:.4f}")
        
        # 可视化: 公平性对比
        self._plot_fairness_comparison()
    
    def generate_report(self):
        """生成综合报告"""
        report_path = Path(self.config['output']['reports_dir']) / 'comprehensive_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# GenAI模型质效比综合分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            # 1. 执行摘要
            f.write("## 1. 执行摘要\n\n")
            f.write(self._generate_executive_summary())
            f.write("\n\n")
            
            # 2. 数据概览
            f.write("## 2. 数据概览\n\n")
            f.write(self._generate_data_overview_section())
            f.write("\n\n")
            
            # 3. 性能分析
            f.write("## 3. 性能分析\n\n")
            f.write(self._generate_performance_section())
            f.write("\n\n")
            
            # 4. 效率分析
            f.write("## 4. 效率分析\n\n")
            f.write(self._generate_efficiency_section())
            f.write("\n\n")
            
            # 5. 质量分析
            f.write("## 5. 质量分析\n\n")
            f.write(self._generate_quality_section())
            f.write("\n\n")
            
            # 6. 质效比分析
            f.write("## 6. 质效比分析\n\n")
            f.write(self._generate_qe_ratio_section())
            f.write("\n\n")
            
            # 7. 公平性分析
            f.write("## 7. 公平性分析\n\n")
            f.write(self._generate_fairness_section())
            f.write("\n\n")
            
            # 8. 模型排名
            f.write("## 8. 模型排名\n\n")
            f.write(self._generate_ranking_section())
            f.write("\n\n")
            
            # 9. 建议
            f.write("## 9. 建议\n\n")
            f.write(self._generate_recommendations())
            f.write("\n\n")
            
            # 10. 附录
            f.write("## 10. 附录\n\n")
            f.write(self._generate_appendix())
        
        logger.info(f"报告已生成: {report_path}")
    
    # ========== 辅助方法 ==========
    
    def _normalize(self, series: pd.Series) -> pd.Series:
        """Min-Max归一化"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        return (series - min_val) / (max_val - min_val)
    
    def _compute_gini(self, values: np.ndarray) -> float:
        """计算Gini系数"""
        values = np.sort(values)
        n = len(values)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * values)) / (n * np.sum(values)) - (n + 1) / n
    
    def _save_table(self, df: pd.DataFrame, filename: str):
        """保存表格"""
        path = Path(self.config['output']['tables_dir']) / filename
        df.to_csv(path, index=False, encoding='utf-8-sig')
        logger.info(f"表格已保存: {path}")
    
    def _save_export(self, df: pd.DataFrame, filename: str):
        """保存导出数据"""
        path = Path(self.config['output']['exports_dir']) / filename
        df.to_csv(path, index=False, encoding='utf-8-sig')
        logger.info(f"数据已导出: {path}")
    
    def _save_figure(self, filename: str):
        """保存图表"""
        path = Path(self.config['output']['figures_dir']) / filename
        plt.savefig(path, dpi=self.config['output']['figure_dpi'], bbox_inches='tight')
        plt.close()
        logger.info(f"图表已保存: {path}")
    
    # ========== 可视化方法 ==========
    
    def _plot_latency_vs_throughput(self):
        """绘制延迟vs吞吐量散点图"""
        plt.figure(figsize=self.config['output']['figure_size'])
        
        for model in self.df['model_name'].unique():
            model_data = self.df[self.df['model_name'] == model]
            plt.scatter(
                model_data['latency_s'],
                model_data['toks_per_s'],
                label=model,
                alpha=0.6,
                s=100
            )
        
        plt.xlabel('延迟 (秒)', fontsize=12)
        plt.ylabel('吞吐量 (tokens/s)', fontsize=12)
        plt.title('模型性能对比: 延迟 vs 吞吐量', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        
        self._save_figure('latency_vs_throughput.png')
    
    def _plot_energy_distribution(self):
        """绘制能耗分布箱线图"""
        plt.figure(figsize=self.config['output']['figure_size'])
        
        data_to_plot = [
            self.df[self.df['model_name'] == model]['gpu_energy_j'].dropna()
            for model in sorted(self.df['model_name'].unique())
        ]
        
        plt.boxplot(data_to_plot, labels=sorted(self.df['model_name'].unique()))
        plt.xlabel('模型', fontsize=12)
        plt.ylabel('GPU能耗 (焦耳)', fontsize=12)
        plt.title('模型能耗分布对比', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        
        self._save_figure('energy_distribution.png')
    
    def _plot_quality_heatmap(self):
        """绘制质量热力图"""
        # 创建模型-任务质量矩阵
        pivot = self.df.pivot_table(
            values='bartscore',
            index='model_name',
            columns='task_type',
            aggfunc='mean'
        )
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            pivot,
            annot=True,
            fmt='.3f',
            cmap='YlOrRd',
            cbar_kws={'label': 'BARTScore'}
        )
        plt.title('模型质量热力图 (按任务)', fontsize=14, fontweight='bold')
        plt.xlabel('任务类型', fontsize=12)
        plt.ylabel('模型', fontsize=12)
        plt.tight_layout()
        
        self._save_figure('quality_heatmap.png')
    
    def _plot_qe_ranking(self):
        """绘制质效比排名柱状图"""
        if 'qe_ranking' not in self.results:
            return
        
        ranking = self.results['qe_ranking'].head(10)
        
        plt.figure(figsize=self.config['output']['figure_size'])
        ranking.plot(kind='barh', color='steelblue')
        plt.xlabel('质效比', fontsize=12)
        plt.ylabel('模型', fontsize=12)
        plt.title('质效比排名 (Top 10)', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        self._save_figure('qe_ranking.png')
    
    def _plot_fairness_comparison(self):
        """绘制公平性对比图"""
        if 'fairness' not in self.results:
            return
        
        fairness_data = self.results['fairness']
        models = list(fairness_data.keys())
        fairness_gaps = [fairness_data[m]['fairness_gap'] for m in models]
        gini_coeffs = [fairness_data[m]['gini'] for m in models]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Fairness Gap
        ax1.barh(models, fairness_gaps, color='coral')
        ax1.set_xlabel('Fairness Gap', fontsize=12)
        ax1.set_title('公平性差距对比', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Gini系数
        ax2.barh(models, gini_coeffs, color='skyblue')
        ax2.set_xlabel('Gini系数', fontsize=12)
        ax2.set_title('质量不均衡度对比', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        self._save_figure('fairness_comparison.png')
    
    # ========== 报告生成方法 ==========
    
    def _generate_executive_summary(self) -> str:
        """生成执行摘要"""
        summary = []
        summary.append("本报告对GenAI模型进行了全面的质效比分析，综合评估了模型在质量、性能和效率方面的表现。\n")
        
        if 'overview' in self.results:
            overview = self.results['overview']
            summary.append(f"- **评估范围**: {overview['models']} 个模型, {overview['tasks']} 种任务类型\n")
            summary.append(f"- **数据规模**: {overview['total_records']} 条实验记录\n")
        
        if 'qe_ranking' in self.results:
            top_model = self.results['qe_ranking'].index[0]
            top_score = self.results['qe_ranking'].iloc[0]
            summary.append(f"- **最佳模型**: {top_model} (质效比: {top_score:.4f})\n")
        
        return ''.join(summary)
    
    def _generate_data_overview_section(self) -> str:
        """生成数据概览章节"""
        if 'overview' not in self.results:
            return "数据概览信息不可用。\n"
        
        overview = self.results['overview']
        section = []
        section.append(f"本次分析共评估了 **{overview['models']}** 个模型在 **{overview['tasks']}** 种任务上的表现。\n\n")
        section.append("### 模型列表\n\n")
        for model in overview['model_list']:
            section.append(f"- {model}\n")
        section.append("\n### 任务类型\n\n")
        for task in overview['task_list']:
            section.append(f"- {task}\n")
        
        return ''.join(section)
    
    def _generate_performance_section(self) -> str:
        """生成性能分析章节"""
        section = []
        section.append("性能分析关注模型的响应速度和吞吐能力。\n\n")
        
        if 'latency_s' in self.df.columns:
            section.append(f"- **平均延迟**: {self.df['latency_s'].mean():.3f} 秒\n")
        if 'toks_per_s' in self.df.columns:
            section.append(f"- **平均吞吐量**: {self.df['toks_per_s'].mean():.2f} tokens/s\n")
        
        section.append("\n![延迟vs吞吐量](../figures/latency_vs_throughput.png)\n")
        
        return ''.join(section)
    
    def _generate_efficiency_section(self) -> str:
        """生成效率分析章节"""
        section = []
        section.append("效率分析评估模型的资源消耗情况。\n\n")
        
        if 'gpu_energy_j' in self.df.columns:
            section.append(f"- **平均GPU能耗**: {self.df['gpu_energy_j'].mean():.2f} 焦耳\n")
        if 'cpu_usage_avg' in self.df.columns:
            section.append(f"- **平均CPU使用率**: {self.df['cpu_usage_avg'].mean():.1f}%\n")
        
        section.append("\n![能耗分布](../figures/energy_distribution.png)\n")
        
        return ''.join(section)
    
    def _generate_quality_section(self) -> str:
        """生成质量分析章节"""
        section = []
        section.append("质量分析评估模型生成内容的质量。\n\n")
        
        if 'bartscore' in self.df.columns:
            section.append(f"- **平均BARTScore**: {self.df['bartscore'].mean():.4f}\n")
        
        section.append("\n![质量热力图](../figures/quality_heatmap.png)\n")
        
        return ''.join(section)
    
    def _generate_qe_ratio_section(self) -> str:
        """生成质效比分析章节"""
        section = []
        section.append("质效比综合考虑了模型的质量和效率，反映了模型的综合性价比。\n\n")
        
        if 'qe_ranking' in self.results:
            section.append("### Top 5 模型\n\n")
            for i, (model, score) in enumerate(self.results['qe_ranking'].head(5).items(), 1):
                section.append(f"{i}. **{model}**: {score:.4f}\n")
        
        section.append("\n![质效比排名](../figures/qe_ranking.png)\n")
        
        return ''.join(section)
    
    def _generate_fairness_section(self) -> str:
        """生成公平性分析章节"""
        section = []
        section.append("公平性分析评估模型在不同任务上的表现一致性。\n\n")
        
        if 'fairness' in self.results:
            # 找出最公平的模型
            fairness_gaps = {m: data['fairness_gap'] for m, data in self.results['fairness'].items()}
            most_fair = min(fairness_gaps, key=fairness_gaps.get)
            section.append(f"- **最公平模型**: {most_fair} (Fairness Gap: {fairness_gaps[most_fair]:.4f})\n")
        
        section.append("\n![公平性对比](../figures/fairness_comparison.png)\n")
        
        return ''.join(section)
    
    def _generate_ranking_section(self) -> str:
        """生成模型排名章节"""
        if 'qe_ranking' not in self.results:
            return "排名信息不可用。\n"
        
        section = []
        section.append("### 综合排名\n\n")
        section.append("| 排名 | 模型 | 质效比 |\n")
        section.append("|------|------|--------|\n")
        
        for i, (model, score) in enumerate(self.results['qe_ranking'].items(), 1):
            section.append(f"| {i} | {model} | {score:.4f} |\n")
        
        return ''.join(section)
    
    def _generate_recommendations(self) -> str:
        """生成建议"""
        recommendations = []
        recommendations.append("基于分析结果，我们提出以下建议：\n\n")
        
        if 'qe_ranking' in self.results:
            top_model = self.results['qe_ranking'].index[0]
            recommendations.append(f"1. **推荐模型**: {top_model} 在质效比方面表现最优\n")
        
        recommendations.append("2. **任务适配**: 根据具体任务选择合适的模型\n")
        recommendations.append("3. **资源优化**: 关注能耗较低的模型以降低运营成本\n")
        recommendations.append("4. **公平性考虑**: 选择在不同任务上表现一致的模型\n")
        
        return ''.join(recommendations)
    
    def _generate_appendix(self) -> str:
        """生成附录"""
        appendix = []
        appendix.append("### 方法论\n\n")
        appendix.append("- **归一化方法**: Min-Max归一化，按任务分组\n")
        appendix.append(f"- **效率得分**: {self.config['weights']['efficiency']}\n")
        appendix.append(f"- **质效比公式**: (质量 + ε) / (1 + ε - 效率)\n")
        appendix.append("\n### 数据文件\n\n")
        appendix.append(f"- 表格: `{self.config['output']['tables_dir']}/`\n")
        appendix.append(f"- 图表: `{self.config['output']['figures_dir']}/`\n")
        appendix.append(f"- 导出数据: `{self.config['output']['exports_dir']}/`\n")
        
        return ''.join(appendix)


def main():
    """主函数"""
    print("=" * 80)
    print("GenAI模型质效比综合分析")
    print("=" * 80)
    
    # 创建分析器
    analyzer = ComprehensiveAnalyzer()
    
    # 运行完整分析
    analyzer.run_full_analysis()
    
    print("\n分析完成! 请查看生成的报告和图表。")


if __name__ == '__main__':
    main()
