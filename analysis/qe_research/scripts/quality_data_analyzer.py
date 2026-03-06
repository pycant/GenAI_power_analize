"""
质量数据分析脚本
实现质量评估数据的可视化和分析
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any
import logging
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 配置日志
log_dir = Path('analysis/qe_research/logs')
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'quality_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class QualityDataAnalyzer:
    """质量数据分析器"""
    
    def __init__(self, data_root: str = 'data/analize'):
        self.data_root = Path(data_root)
        self.output_dir = Path('analysis/qe_research/results/quality_analysis')
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir = self.output_dir / 'tables'
        self.reports_dir = self.output_dir / 'reports'
        
        # 创建输出目录
        for d in [self.figures_dir, self.tables_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图样式
        try:
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            # 学术配色方案
            self.academic_colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
                                   '#CA9161', '#949494', '#ECE133', '#56B4E9']
            sns.set_palette(self.academic_colors)
        except:
            self.academic_colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
                                   '#CA9161', '#949494', '#ECE133', '#56B4E9']
        
        self.quality_data = {}
        self.task_types = []
        logger.info("质量数据分析器初始化完成")
    
    def load_quality_data(self):
        """加载所有质量评估数据"""
        logger.info("开始加载质量数据...")
        
        # 查找所有quality_summary文件
        results_dir = self.data_root / 'results'
        quality_files = list(results_dir.glob('*/quality_summary_*.csv'))
        
        for file in quality_files:
            # 从文件名提取任务类型
            task_type = file.stem.replace('quality_summary_', '')
            if task_type.endswith('_v2'):
                task_type = task_type[:-3]
            
            try:
                df = pd.read_csv(file)
                self.quality_data[task_type] = df
                self.task_types.append(task_type)
                logger.info(f"✓ {task_type}: {len(df)} 个模型")
            except Exception as e:
                logger.error(f"✗ {file}: {e}")
        
        logger.info(f"总共加载 {len(self.quality_data)} 个任务类型的质量数据")
    
    def run_all_analyses(self):
        """运行所有分析任务"""
        logger.info("\n" + "=" * 80)
        logger.info("开始质量数据深度分析")
        logger.info("=" * 80)
        
        tasks = [
            ("数据探索性分析", self.exploratory_analysis),
            ("模型对比分析", self.model_comparison),
            ("任务专项分析", self.task_specific_analysis),
            ("子指标关系分析", self.submetric_correlation),
            ("质量稳定性分析", self.stability_analysis),
            ("跨任务综合评估", self.cross_task_evaluation)
        ]
        
        for i, (name, func) in enumerate(tasks, 1):
            logger.info(f"\n[{i}/{len(tasks)}] {name}...")
            try:
                func()
            except Exception as e:
                logger.error(f"分析失败: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info("\n生成综合报告...")
        self.generate_report()
        
        logger.info("\n" + "=" * 80)
        logger.info("分析完成!")
        logger.info(f"报告: {self.reports_dir}/quality_analysis_report.md")
        logger.info(f"图表: {self.figures_dir}/")
        logger.info("=" * 80)
    
    # ========== 一、数据探索性分析 ==========
    
    def exploratory_analysis(self):
        """数据探索性分析"""
        self._task1_score_distribution()
        self._task2_boxplot_by_model()
        self._task3_missing_values()
    
    def _task1_score_distribution(self):
        """任务1: 质量得分分布"""
        logger.info("  执行任务1: 质量得分分布")
        # 对于代码任务，使用compilation_rate作为主要质量指标
        for task_type, df in self.quality_data.items():
            logger.info(f"    处理任务类型: {task_type}, 数据行数: {len(df)}")
            if len(df) == 0:
                logger.warning(f"    跳过 {task_type}: 数据为空")
                continue
            
            # 确定主要质量指标（按优先级）
            score_col = None
            if 'overall_score' in df.columns:
                score_col = 'overall_score'
                logger.info(f"    使用 overall_score 作为质量指标")
            elif 'functional_correctness_mean' in df.columns:
                score_col = 'functional_correctness_mean'
                logger.info(f"    使用 functional_correctness_mean 作为质量指标")
            elif 'compilation_success_mean' in df.columns:
                score_col = 'compilation_success_mean'
                logger.info(f"    使用 compilation_success_mean 作为质量指标")
            elif 'compilation_rate_mean' in df.columns:
                score_col = 'compilation_rate_mean'
                logger.info(f"    使用 compilation_rate_mean 作为质量指标")
            else:
                logger.warning(f"    跳过 {task_type}: 未找到质量指标列")
                continue
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 直方图 + KDE
            ax1.hist(df[score_col], bins=15, color=self.academic_colors[0], 
                    edgecolor='black', alpha=0.7, density=True)
            df[score_col].plot(kind='kde', ax=ax1, color=self.academic_colors[1], 
                             linewidth=2, label='KDE')
            ax1.axvline(df[score_col].mean(), color='red', linestyle='--', 
                       linewidth=2, label=f'均值: {df[score_col].mean():.3f}')
            ax1.axvline(df[score_col].median(), color='green', linestyle='--', 
                       linewidth=2, label=f'中位数: {df[score_col].median():.3f}')
            ax1.set_xlabel('质量得分', fontsize=11)
            ax1.set_ylabel('密度', fontsize=11)
            ax1.set_title('得分分布', fontsize=12, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 统计摘要
            stats_text = f"""
统计摘要:
均值: {df[score_col].mean():.3f}
中位数: {df[score_col].median():.3f}
标准差: {df[score_col].std():.3f}
最小值: {df[score_col].min():.3f}
最大值: {df[score_col].max():.3f}
样本数: {len(df)}
            """
            ax2.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
                    family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            ax2.axis('off')
            
            plt.suptitle(f'任务1: 质量得分分布 - {task_type}', 
                        fontsize=13, fontweight='bold', y=1.02)
            plt.tight_layout()
            self._save_fig(f'01_score_distribution_{task_type}.png')
    
    def _task2_boxplot_by_model(self):
        """任务2: 按模型分组的箱线图"""
        logger.info("  执行任务2: 按模型分组的箱线图")
        for task_type, df in self.quality_data.items():
            logger.info(f"    处理任务类型: {task_type}, 数据行数: {len(df)}")
            if len(df) == 0:
                logger.warning(f"    跳过 {task_type}: 数据为空")
                continue
            
            # 确定主要质量指标（按优先级）
            score_col = None
            if 'overall_score' in df.columns:
                score_col = 'overall_score'
                logger.info(f"    使用 overall_score 作为质量指标")
            elif 'functional_correctness_mean' in df.columns:
                score_col = 'functional_correctness_mean'
                logger.info(f"    使用 functional_correctness_mean 作为质量指标")
            elif 'compilation_success_mean' in df.columns:
                score_col = 'compilation_success_mean'
                logger.info(f"    使用 compilation_success_mean 作为质量指标")
            elif 'compilation_rate_mean' in df.columns:
                score_col = 'compilation_rate_mean'
                logger.info(f"    使用 compilation_rate_mean 作为质量指标")
            else:
                logger.warning(f"    跳过 {task_type}: 未找到质量指标列")
                continue
            
            plt.figure(figsize=(12, 6))
            
            # 按得分排序模型
            df_sorted = df.sort_values(score_col, ascending=False)
            
            # 创建箱线图（这里用条形图+误差线代替，因为每个模型只有一个值）
            x = range(len(df_sorted))
            y = df_sorted[score_col]
            
            # 如果有标准差列，添加误差线
            std_col = score_col.replace('_mean', '_std')
            if std_col in df_sorted.columns:
                yerr = df_sorted[std_col]
            else:
                yerr = None
            
            plt.bar(x, y, color=self.academic_colors[:len(df_sorted)], 
                   edgecolor='black', alpha=0.7, yerr=yerr, capsize=5)
            plt.xticks(x, df_sorted['model'], rotation=45, ha='right')
            plt.xlabel('模型', fontsize=11)
            plt.ylabel('质量得分', fontsize=11)
            plt.title(f'任务2: 模型质量对比 - {task_type}', fontsize=13, fontweight='bold')
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            self._save_fig(f'02_model_comparison_{task_type}.png')
    
    def _task3_missing_values(self):
        """任务3: 缺失值分析"""
        missing_data = []
        
        for task_type, df in self.quality_data.items():
            missing_count = df.isnull().sum()
            missing_pct = (missing_count / len(df) * 100).round(2)
            
            for col in df.columns:
                if missing_count[col] > 0:
                    missing_data.append({
                        'task_type': task_type,
                        'column': col,
                        'missing_count': missing_count[col],
                        'missing_pct': missing_pct[col]
                    })
        
        if missing_data:
            df_missing = pd.DataFrame(missing_data)
            df_missing.to_csv(self.tables_dir / 'missing_values.csv', index=False)
            logger.info(f"发现 {len(missing_data)} 个缺失值情况")
        else:
            logger.info("未发现缺失值")
    
    # ========== 二、模型对比分析 ==========
    
    def model_comparison(self):
        """模型对比分析"""
        self._task4_model_ranking()
        self._task5_radar_chart()
        self._task6_heatmap()
    
    def _task4_model_ranking(self):
        """任务4: 模型排名条形图"""
        logger.info("  执行任务4: 模型排名条形图")
        for task_type, df in self.quality_data.items():
            logger.info(f"    处理任务类型: {task_type}, 数据行数: {len(df)}")
            if len(df) == 0:
                logger.warning(f"    跳过 {task_type}: 数据为空")
                continue
            
            # 确定主要质量指标（按优先级）
            score_col = None
            if 'overall_score' in df.columns:
                score_col = 'overall_score'
                logger.info(f"    使用 overall_score 作为质量指标")
            elif 'functional_correctness_mean' in df.columns:
                score_col = 'functional_correctness_mean'
                logger.info(f"    使用 functional_correctness_mean 作为质量指标")
            elif 'compilation_success_mean' in df.columns:
                score_col = 'compilation_success_mean'
                logger.info(f"    使用 compilation_success_mean 作为质量指标")
            elif 'compilation_rate_mean' in df.columns:
                score_col = 'compilation_rate_mean'
                logger.info(f"    使用 compilation_rate_mean 作为质量指标")
            else:
                logger.warning(f"    跳过 {task_type}: 未找到质量指标列")
                continue
            
            plt.figure(figsize=(12, 6))
            
            # 按得分排序
            df_sorted = df.sort_values(score_col, ascending=True)
            
            # 水平条形图
            y = range(len(df_sorted))
            x = df_sorted[score_col]
            
            # 误差线
            std_col = score_col.replace('_mean', '_std')
            if std_col in df_sorted.columns:
                xerr = df_sorted[std_col]
            else:
                xerr = None
            
            plt.barh(y, x, color=self.academic_colors[0], 
                    edgecolor='black', alpha=0.7, xerr=xerr, capsize=5)
            plt.yticks(y, df_sorted['model'])
            plt.xlabel('质量得分', fontsize=11)
            plt.ylabel('模型', fontsize=11)
            plt.title(f'任务4: 模型排名 - {task_type}', fontsize=13, fontweight='bold')
            plt.grid(True, alpha=0.3, axis='x')
            plt.tight_layout()
            self._save_fig(f'04_model_ranking_{task_type}.png')
    
    def _task5_radar_chart(self):
        """任务5: 雷达图"""
        for task_type, df in self.quality_data.items():
            if len(df) < 2:
                continue
            
            # 选择数值列（排除model列）
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) < 3:
                continue
            
            # 选择前5个指标
            metrics = numeric_cols[:min(5, len(numeric_cols))]
            
            # 归一化到0-1
            df_norm = df.copy()
            for col in metrics:
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:
                    df_norm[col] = (df[col] - min_val) / (max_val - min_val)
                else:
                    df_norm[col] = 0.5
            
            # 选择前3个模型绘制
            models_to_plot = df['model'].head(3).tolist()
            
            # 创建雷达图
            angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
            angles += angles[:1]  # 闭合
            
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            for i, model in enumerate(models_to_plot):
                values = df_norm[df_norm['model'] == model][metrics].values.flatten().tolist()
                values += values[:1]  # 闭合
                ax.plot(angles, values, 'o-', linewidth=2, label=model, 
                       color=self.academic_colors[i])
                ax.fill(angles, values, alpha=0.15, color=self.academic_colors[i])
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics, fontsize=10)
            ax.set_ylim(0, 1)
            ax.set_title(f'任务5: 模型能力雷达图 - {task_type}', 
                        fontsize=13, fontweight='bold', pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
            ax.grid(True)
            
            plt.tight_layout()
            self._save_fig(f'05_radar_chart_{task_type}.png')
    
    def _task6_heatmap(self):
        """任务6: 模型×任务热力图"""
        logger.info("  执行任务6: 模型×任务热力图")
        # 合并所有任务的数据
        all_data = []
        for task_type, df in self.quality_data.items():
            # 确定主要质量指标（按优先级）
            score_col = None
            if 'overall_score' in df.columns:
                score_col = 'overall_score'
            elif 'functional_correctness_mean' in df.columns:
                score_col = 'functional_correctness_mean'
            elif 'compilation_success_mean' in df.columns:
                score_col = 'compilation_success_mean'
            elif 'compilation_rate_mean' in df.columns:
                score_col = 'compilation_rate_mean'
            else:
                logger.warning(f"    跳过 {task_type}: 未找到质量指标列")
                continue
            
            for _, row in df.iterrows():
                all_data.append({
                    'model': row['model'],
                    'task': task_type,
                    'score': row[score_col]
                })
        
        if not all_data:
            return
        
        df_all = pd.DataFrame(all_data)
        pivot = df_all.pivot(index='model', columns='task', values='score')
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlOrRd', 
                   cbar_kws={'label': '质量得分'}, linewidths=0.5)
        plt.title('任务6: 模型×任务热力图', fontsize=13, fontweight='bold')
        plt.xlabel('任务类型', fontsize=11)
        plt.ylabel('模型', fontsize=11)
        plt.tight_layout()
        self._save_fig('06_model_task_heatmap.png')
    
    # ========== 三、任务专项分析 ==========
    
    def task_specific_analysis(self):
        """任务专项分析"""
        self._task7_code_analysis()
    
    def _task7_code_analysis(self):
        """任务7: 代码任务专项分析"""
        if 'code' not in self.quality_data:
            return
        
        df = self.quality_data['code']
        
        # 堆叠条形图：各子指标得分构成
        # 使用新的列名结构
        metrics = [
            'functional_correctness_mean',
            'compilation_success_mean', 
            'test_pass_rate_mean',
            'code_simplicity_mean',
            'readability_score_mean'
        ]
        available_metrics = [m for m in metrics if m in df.columns]
        
        if len(available_metrics) < 2:
            # 如果新列名不存在，尝试旧列名
            metrics = ['compilation_rate_mean', 'cyclomatic_complexity_mean', 'code_length_mean']
            available_metrics = [m for m in metrics if m in df.columns]
            if len(available_metrics) < 2:
                return
        
        # 归一化
        df_norm = df.copy()
        for col in available_metrics:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df_norm[col] = (df[col] - min_val) / (max_val - min_val)
            else:
                df_norm[col] = 0.5
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        x = range(len(df))
        bottom = np.zeros(len(df))
        
        for i, metric in enumerate(available_metrics):
            ax.bar(x, df_norm[metric], bottom=bottom, label=metric,
                  color=self.academic_colors[i], edgecolor='white', linewidth=0.5)
            bottom += df_norm[metric]
        
        ax.set_xticks(x)
        ax.set_xticklabels(df['model'], rotation=45, ha='right')
        ax.set_xlabel('模型', fontsize=11)
        ax.set_ylabel('归一化得分', fontsize=11)
        ax.set_title('任务7: 代码任务子指标构成', fontsize=13, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        self._save_fig('07_code_submetrics.png')
    
    # ========== 四、子指标关系分析 ==========
    
    def submetric_correlation(self):
        """子指标关系分析"""
        self._task8_correlation_matrix()
    
    def _task8_correlation_matrix(self):
        """任务8: 相关性矩阵"""
        for task_type, df in self.quality_data.items():
            # 选择数值列
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if len(numeric_cols) < 2:
                continue
            
            # 计算相关系数
            corr = df[numeric_cols].corr()
            
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', 
                       center=0, vmin=-1, vmax=1,
                       square=True, linewidths=0.5,
                       cbar_kws={'label': '相关系数'})
            plt.title(f'任务8: 子指标相关性矩阵 - {task_type}', 
                     fontsize=13, fontweight='bold')
            plt.tight_layout()
            self._save_fig(f'08_correlation_matrix_{task_type}.png')
    
    # ========== 五、质量稳定性分析 ==========
    
    def stability_analysis(self):
        """质量稳定性分析"""
        self._task9_stability_comparison()
    
    def _task9_stability_comparison(self):
        """任务9: 模型稳定性对比"""
        for task_type, df in self.quality_data.items():
            # 查找标准差列
            std_cols = [col for col in df.columns if '_std' in col]
            if not std_cols:
                continue
            
            # 使用第一个标准差列
            std_col = std_cols[0]
            mean_col = std_col.replace('_std', '_mean')
            
            if mean_col not in df.columns:
                continue
            
            plt.figure(figsize=(12, 6))
            
            # 按标准差排序
            df_sorted = df.sort_values(std_col)
            
            x = range(len(df_sorted))
            y = df_sorted[std_col]
            
            plt.bar(x, y, color=self.academic_colors[1], 
                   edgecolor='black', alpha=0.7)
            plt.xticks(x, df_sorted['model'], rotation=45, ha='right')
            plt.xlabel('模型', fontsize=11)
            plt.ylabel('标准差', fontsize=11)
            plt.title(f'任务9: 模型稳定性对比 - {task_type}', fontsize=13, fontweight='bold')
            plt.grid(True, alpha=0.3, axis='y')
            plt.tight_layout()
            self._save_fig(f'09_stability_{task_type}.png')
    
    # ========== 六、跨任务综合评估 ==========
    
    def cross_task_evaluation(self):
        """跨任务综合评估"""
        self._task10_comprehensive_score()
    
    def _task10_comprehensive_score(self):
        """任务10: 综合质量得分"""
        # 合并所有任务的数据
        all_scores = {}
        
        for task_type, df in self.quality_data.items():
            if 'overall_score' in df.columns:
                score_col = 'overall_score'
            elif 'compilation_rate_mean' in df.columns:
                score_col = 'compilation_rate_mean'
            else:
                continue
            
            for _, row in df.iterrows():
                model = row['model']
                if model not in all_scores:
                    all_scores[model] = []
                all_scores[model].append(row[score_col])
        
        if not all_scores:
            logger.info("没有足够的数据进行跨任务综合评估")
            return
        
        # 计算平均分和标准差
        comprehensive_data = []
        for model, scores in all_scores.items():
            comprehensive_data.append({
                'model': model,
                'mean_score': np.mean(scores),
                'std_score': np.std(scores),
                'task_count': len(scores)
            })
        
        df_comp = pd.DataFrame(comprehensive_data)
        df_comp = df_comp.sort_values('mean_score', ascending=False)
        
        # 保存到表格
        df_comp.to_csv(self.tables_dir / 'comprehensive_scores.csv', index=False)
        
        # 可视化
        plt.figure(figsize=(12, 6))
        
        x = range(len(df_comp))
        y = df_comp['mean_score']
        yerr = df_comp['std_score']
        
        plt.barh(x, y, xerr=yerr, color=self.academic_colors[0], 
                edgecolor='black', alpha=0.7, capsize=5)
        plt.yticks(x, df_comp['model'])
        plt.xlabel('综合质量得分', fontsize=11)
        plt.ylabel('模型', fontsize=11)
        plt.title('任务10: 跨任务综合质量评估', fontsize=13, fontweight='bold')
        plt.grid(True, alpha=0.3, axis='x')
        
        # 添加任务数量标注
        for i, (idx, row) in enumerate(df_comp.iterrows()):
            plt.text(row['mean_score'] + 0.01, i, f"n={row['task_count']}", 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        self._save_fig('10_comprehensive_score.png')
    
    # ========== 辅助方法 ==========
    
    def _save_fig(self, filename):
        """保存图表"""
        path = self.figures_dir / filename
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ {filename}")
    
    def generate_report(self):
        """生成综合报告"""
        report_path = self.reports_dir / 'quality_analysis_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 质量数据深度分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 执行摘要\n\n")
            f.write(f"本报告对 {len(self.quality_data)} 个任务类型的质量评估数据进行了深度分析，")
            f.write("涵盖数据探索、模型对比、任务专项分析、子指标关系、稳定性和跨任务综合评估。\n\n")
            
            f.write("## 分析维度\n\n")
            
            sections = [
                ("一、数据探索性分析", [
                    ("任务1", "质量得分分布", "01_score_distribution_*.png"),
                    ("任务2", "按模型分组的箱线图", "02_model_comparison_*.png"),
                    ("任务3", "缺失值分析", "missing_values.csv")
                ]),
                ("二、模型对比分析", [
                    ("任务4", "模型排名条形图", "04_model_ranking_*.png"),
                    ("任务5", "雷达图", "05_radar_chart_*.png"),
                    ("任务6", "模型×任务热力图", "06_model_task_heatmap.png")
                ]),
                ("三、任务专项分析", [
                    ("任务7", "代码任务专项分析", "07_code_submetrics.png")
                ]),
                ("四、子指标关系分析", [
                    ("任务8", "相关性矩阵", "08_correlation_matrix_*.png")
                ]),
                ("五、质量稳定性分析", [
                    ("任务9", "模型稳定性对比", "09_stability_*.png")
                ]),
                ("六、跨任务综合评估", [
                    ("任务10", "综合质量得分", "10_comprehensive_score.png")
                ])
            ]
            
            for section_title, tasks in sections:
                f.write(f"### {section_title}\n\n")
                for task_id, task_name, fig_name in tasks:
                    f.write(f"#### {task_id}: {task_name}\n\n")
                    if fig_name.endswith('.png'):
                        f.write(f"![{task_name}](../figures/{fig_name})\n\n")
                    else:
                        f.write(f"详见: `../tables/{fig_name}`\n\n")
            
            f.write("## 数据质量\n\n")
            f.write(f"- 任务类型数: {len(self.quality_data)}\n")
            for task_type, df in self.quality_data.items():
                f.write(f"- {task_type}: {len(df)} 个模型\n")
            f.write("\n")
            
            f.write("---\n\n")
            f.write("**分析完成时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        
        logger.info(f"报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("质量数据深度分析")
    print("=" * 80 + "\n")
    
    analyzer = QualityDataAnalyzer()
    
    # 加载数据
    analyzer.load_quality_data()
    
    if len(analyzer.quality_data) == 0:
        print("错误: 未找到任何质量数据")
        return
    
    # 运行所有分析
    analyzer.run_all_analyses()
    
    print("\n分析完成! 请查看生成的报告和图表。")
    print(f"报告位置: {analyzer.reports_dir}/quality_analysis_report.md")
    print(f"图表位置: {analyzer.figures_dir}/")


if __name__ == '__main__':
    main()
