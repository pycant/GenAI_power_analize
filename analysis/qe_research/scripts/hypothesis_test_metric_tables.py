"""
基于原始数据的假设检验分析器
检验同一任务下不同模型间GPU能耗差异
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import logging
from scipy.stats import kruskal, mannwhitneyu
from itertools import combinations
import warnings

warnings.filterwarnings('ignore')

# 配置日志
log_dir = Path('analysis/qe_research/logs')
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis/qe_research/logs/hypothesis_test_metric_tables.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MetricTablesHypothesisTester:
    """基于原始数据的假设检验分析器"""
    
    def __init__(self, data_root: str = 'data'):
        """初始化分析器"""
        self.data_root = Path(data_root)
        self.output_dir = Path('analysis/qe_research/results/raw_analysis')
        self.figures_dir = self.output_dir / 'figures'
        self.tables_dir = self.output_dir / 'tables'
        self.reports_dir = self.output_dir / 'reports'
        
        # 创建输出目录
        for dir_path in [self.figures_dir, self.tables_dir, self.reports_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图样式
        self._setup_plotting_style()
        
        # 模型目录列表
        self.model_dirs = [
            'deepseek_8b_ol_q4km', 'gemma_2b_hf_4bit', 'gemma_2b_hf_8bit',
            'gemma_4b_ol_q4km', 'phi3_4b_hf_4bit', 'phi3_4b_hf_8bit',
            'qwen_4b_ol_q4km', 'qwen_8b_ol_q4km', 'qwen25_3b_hf_4bit',
            'qwen25_3b_hf_8bit', 'qwen25_7b_hf_4bit', 'qwen25_7b_hf_8bit'
        ]
        
        # 需要排除的模型（存在数据问题和缺失值）
        self.excluded_models = [
            'qwen--qwen2.5-7b-instruct:8bit',
            'qwen2.5-7b-instruct:8bit'
        ]
        
        self.experiments = []
        self.excluded_count = 0
        logger.info("假设检验分析器初始化完成")
        logger.info(f"排除的模型: {', '.join(self.excluded_models)}")
    
    def _setup_plotting_style(self):
        """设置绘图样式"""
        try:
            # 先设置样式
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("viridis")
            
            # 样式设置后再设置中文字体（避免被覆盖）
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            
            logger.info("绘图样式设置完成")
        except Exception as e:
            logger.warning(f"样式设置失败: {e}")
            # 即使样式设置失败，也要确保中文字体可用
            try:
                plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
                plt.rcParams['axes.unicode_minus'] = False
            except:
                pass
    
    def load_all_raw_data(self):
        """加载所有raw.json文件"""
        logger.info("开始加载原始数据...")
        
        for model_dir in self.model_dirs:
            dir_path = self.data_root / model_dir
            if not dir_path.exists():
                logger.warning(f"目录不存在: {dir_path}")
                continue
            
            raw_files = list(dir_path.glob('*_raw.json'))
            for raw_file in raw_files:
                try:
                    with open(raw_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for exp in data:
                        exp['model_dir'] = model_dir
                        exp['model_name'] = self._extract_model_name(exp['config']['model'])
                        
                        # 检查是否为需要排除的模型
                        if self._should_exclude_model(exp['model_name']):
                            self.excluded_count += 1
                            continue
                        
                        self.experiments.append(exp)
                    
                    logger.info(f"加载: {raw_file.name} ({len(data)} 个实验)")
                except Exception as e:
                    logger.error(f"加载失败 {raw_file}: {e}")
        
        logger.info(f"总共加载 {len(self.experiments)} 个实验")
        if self.excluded_count > 0:
            logger.info(f"排除了 {self.excluded_count} 个问题模型的实验数据")
    
    def _extract_model_name(self, model_str: str) -> str:
        """提取模型名称"""
        return model_str.replace('Ollama:', '').replace('HF:', '').lower().strip()
    
    def _should_exclude_model(self, model_name: str) -> bool:
        """检查模型是否应该被排除"""
        model_name_lower = model_name.lower()
        for excluded in self.excluded_models:
            if excluded.lower() in model_name_lower:
                return True
        return False
    
    def _extract_gpu_energy(self, exp: Dict) -> float:
        """从实验数据中提取GPU能耗"""
        if 'monitoring_data' not in exp or not exp['monitoring_data']:
            return None
        
        mon = exp['monitoring_data']
        
        # 尝试从summary中获取
        if 'summary' in mon and 'gpu_energy_j' in mon['summary']:
            return mon['summary']['gpu_energy_j']
        
        # 尝试计算
        measurements = mon.get('measurements', {})
        gpu_power = measurements.get('gpu_power_w', [])
        timestamps = measurements.get('timestamps', [])
        
        if len(gpu_power) > 1 and len(timestamps) > 1:
            # 使用梯形法则计算能耗
            time_diffs = np.diff(timestamps)
            avg_power = (np.array(gpu_power[:-1]) + np.array(gpu_power[1:])) / 2
            energy = np.sum(avg_power * time_diffs)
            return energy
        
        return None
    
    def _extract_task_type(self, exp: Dict) -> str:
        """提取任务类型"""
        task_type = exp.get('config', {}).get('task_type', 'unknown')
        return task_type.lower()
    
    def test_energy_across_models_by_task(self):
        """检验同一任务下不同模型间GPU能耗差异"""
        logger.info("=" * 80)
        logger.info("检验同一任务下不同模型间GPU能耗差异")
        logger.info("=" * 80)
        
        # 按任务和模型组织数据
        task_model_energy = {}
        
        for exp in self.experiments:
            task = self._extract_task_type(exp)
            model = exp['model_name']
            
            # 再次确认不包含排除的模型
            if self._should_exclude_model(model):
                continue
            
            energy = self._extract_gpu_energy(exp)
            
            if energy is not None and energy > 0:
                if task not in task_model_energy:
                    task_model_energy[task] = {}
                if model not in task_model_energy[task]:
                    task_model_energy[task][model] = []
                task_model_energy[task][model].append(energy)
        
        if not task_model_energy:
            logger.warning("未找到有效的能耗数据")
            return
        
        # 对每个任务进行检验
        all_results = []
        
        for task in sorted(task_model_energy.keys()):
            logger.info(f"\n任务: {task}")
            logger.info("-" * 60)
            
            energy_by_model = task_model_energy[task]
            
            # 至少需要2个模型才能比较
            if len(energy_by_model) < 2:
                logger.warning(f"  任务 {task} 只有 {len(energy_by_model)} 个模型，跳过")
                continue
            
            # 描述性统计
            desc_stats = []
            for model in sorted(energy_by_model.keys()):
                data = energy_by_model[model]
                desc_stats.append({
                    '任务': task,
                    '模型': model,
                    '样本量': len(data),
                    '均值': np.mean(data),
                    '标准差': np.std(data, ddof=1),
                    '中位数': np.median(data),
                    '最小值': np.min(data),
                    '最大值': np.max(data)
                })
            
            desc_df = pd.DataFrame(desc_stats)
            logger.info(f"\n描述性统计:\n{desc_df.to_string(index=False)}")
            
            # Kruskal-Wallis检验
            models = sorted(energy_by_model.keys())
            energy_groups = [energy_by_model[model] for model in models]
            
            h_stat, p_value = kruskal(*energy_groups)
            logger.info(f"\nKruskal-Wallis检验: H={h_stat:.4f}, p={p_value:.4f}")
            
            result = {
                '任务': task,
                '模型数量': len(models),
                '总样本量': sum(len(g) for g in energy_groups),
                'H统计量': h_stat,
                'p值': p_value,
                '显著性': '是' if p_value < 0.05 else '否'
            }
            all_results.append(result)
            
            # 如果显著，进行事后比较
            if p_value < 0.05:
                logger.info(f"  结论: 存在显著差异 (p < 0.05)")
                self._post_hoc_analysis_for_task(task, energy_by_model, models)
            else:
                logger.info(f"  结论: 不存在显著差异 (p >= 0.05)")
            
            # 可视化
            self._plot_energy_by_model_for_task(task, energy_by_model, p_value)
            
            # 保存任务级描述性统计
            desc_df.to_csv(
                self.tables_dir / f'energy_by_model_{task}_descriptive.csv',
                index=False,
                encoding='utf-8-sig'
            )
        
        # 保存汇总结果
        if all_results:
            results_df = pd.DataFrame(all_results)
            results_df.to_csv(
                self.tables_dir / 'energy_model_hypothesis_test_by_task.csv',
                index=False,
                encoding='utf-8-sig'
            )
            logger.info(f"\n汇总结果已保存: energy_model_hypothesis_test_by_task.csv")
            
            # 生成报告
            self._generate_report(results_df, task_model_energy)
    
    def _post_hoc_analysis_for_task(self, task: str, energy_by_model: Dict, models: List[str]):
        """对单个任务进行事后比较"""
        logger.info(f"\n  事后比较 (Mann-Whitney U检验):")
        
        comparisons = []
        for model1, model2 in combinations(models, 2):
            data1 = energy_by_model[model1]
            data2 = energy_by_model[model2]
            
            u_stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
            
            # Bonferroni校正
            n_comparisons = len(list(combinations(models, 2)))
            p_corrected = min(p_value * n_comparisons, 1.0)
            
            comparisons.append({
                '任务': task,
                '模型1': model1,
                '模型2': model2,
                '模型1均值': np.mean(data1),
                '模型2均值': np.mean(data2),
                'U统计量': u_stat,
                'p值': p_value,
                'p值(校正)': p_corrected,
                '是否显著': '是' if p_corrected < 0.05 else '否'
            })
            
            if p_corrected < 0.05:
                logger.info(f"    {model1} vs {model2}: p={p_value:.4f} (校正后={p_corrected:.4f}) *")
        
        # 保存事后比较结果
        comp_df = pd.DataFrame(comparisons)
        comp_df.to_csv(
            self.tables_dir / f'energy_post_hoc_{task}.csv',
            index=False,
            encoding='utf-8-sig'
        )
    
    def _plot_energy_by_model_for_task(self, task: str, energy_by_model: Dict, p_value: float):
        """绘制单个任务的模型间GPU能耗箱线图"""
        # 准备数据
        data_list = []
        for model, energies in energy_by_model.items():
            for energy in energies:
                data_list.append({'模型': model, 'GPU能耗(J)': energy})
        
        df = pd.DataFrame(data_list)
        
        # 绘图
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # 确保中文字体设置
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 按均值排序模型
        model_order = df.groupby('模型')['GPU能耗(J)'].mean().sort_values().index.tolist()
        
        sns.boxplot(data=df, x='模型', y='GPU能耗(J)', order=model_order, palette='Set2', ax=ax)
        sns.stripplot(data=df, x='模型', y='GPU能耗(J)', order=model_order, 
                     color='black', alpha=0.3, size=3, ax=ax)
        
        ax.set_title(f'任务 {task.upper()} - 不同模型GPU能耗分布\n(Kruskal-Wallis p={p_value:.4f})', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('模型', fontsize=12)
        ax.set_ylabel('GPU能耗 (焦耳)', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        # 保存
        filename = f'energy_by_model_{task}.png'
        plt.savefig(self.figures_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  图表已保存: {filename}")
    
    def _generate_report(self, results_df: pd.DataFrame, task_model_energy: Dict):
        """生成假设检验报告"""
        report_path = self.reports_dir / 'GPU_ENERGY_MODEL_HYPOTHESIS_TESTING_REPORT.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# GPU能耗模型间差异假设检验报告\n\n")
            f.write("## 分析目标\n\n")
            f.write("检验同一任务下不同模型间GPU能耗是否存在显著差异。\n\n")
            
            f.write("## 数据说明\n\n")
            f.write("- **数据来源**: 原始实验数据 (raw.json)\n")
            f.write(f"- **排除的模型**: {', '.join(self.excluded_models)} (存在数据问题和缺失值)\n")
            if self.excluded_count > 0:
                f.write(f"- **排除的实验数**: {self.excluded_count}\n")
            f.write("\n")
            
            f.write("## 方法说明\n\n")
            f.write("- **检验方法**: Kruskal-Wallis H检验（非参数检验）\n")
            f.write("- **显著性水平**: α = 0.05\n")
            f.write("- **事后比较**: Mann-Whitney U检验 + Bonferroni校正\n\n")
            
            f.write("## 整体结果\n\n")
            f.write(f"- 分析任务数: {len(results_df)}\n")
            f.write(f"- 存在显著差异的任务: {len(results_df[results_df['显著性'] == '是'])}\n")
            f.write(f"- 不存在显著差异的任务: {len(results_df[results_df['显著性'] == '否'])}\n\n")
            
            f.write("## 各任务检验结果\n\n")
            f.write("| 任务 | 模型数量 | 总样本量 | H统计量 | p值 | 显著性 |\n")
            f.write("|------|----------|----------|---------|-----|--------|\n")
            
            for _, row in results_df.iterrows():
                f.write(f"| {row['任务']} | {row['模型数量']} | {row['总样本量']} | "
                       f"{row['H统计量']:.4f} | {row['p值']:.4f} | {row['显著性']} |\n")
            
            f.write("\n## 详细分析\n\n")
            
            for _, row in results_df.iterrows():
                task = row['任务']
                f.write(f"### 任务: {task.upper()}\n\n")
                
                if row['显著性'] == '是':
                    f.write(f"**结论**: 不同模型间GPU能耗存在显著差异 (p={row['p值']:.4f} < 0.05)\n\n")
                    
                    # 读取描述性统计
                    desc_file = self.tables_dir / f'energy_by_model_{task}_descriptive.csv'
                    if desc_file.exists():
                        desc_df = pd.read_csv(desc_file)
                        f.write("**描述性统计**:\n\n")
                        f.write(desc_df.to_markdown(index=False))
                        f.write("\n\n")
                    
                    # 读取事后比较
                    posthoc_file = self.tables_dir / f'energy_post_hoc_{task}.csv'
                    if posthoc_file.exists():
                        posthoc_df = pd.read_csv(posthoc_file)
                        significant = posthoc_df[posthoc_df['是否显著'] == '是']
                        if len(significant) > 0:
                            f.write(f"**显著差异的模型对** (共{len(significant)}对):\n\n")
                            for _, comp in significant.iterrows():
                                f.write(f"- {comp['模型1']} vs {comp['模型2']}: "
                                       f"p={comp['p值']:.4f} (校正后={comp['p值(校正)']:.4f})\n")
                            f.write("\n")
                else:
                    f.write(f"**结论**: 不同模型间GPU能耗不存在显著差异 (p={row['p值']:.4f} >= 0.05)\n\n")
                
                # 添加图表引用
                f.write(f"**可视化**: `figures/energy_by_model_{task}.png`\n\n")
                f.write("---\n\n")
            
            f.write("## 数据文件\n\n")
            f.write("- 汇总结果: `tables/energy_model_hypothesis_test_by_task.csv`\n")
            f.write("- 各任务描述性统计: `tables/energy_by_model_<task>_descriptive.csv`\n")
            f.write("- 各任务事后比较: `tables/energy_post_hoc_<task>.csv`\n")
            f.write("- 可视化图表: `figures/energy_by_model_<task>.png`\n\n")
            
            f.write("---\n\n")
            f.write(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("**生成脚本**: `analysis/qe_research/scripts/hypothesis_test_metric_tables.py`\n")
        
        logger.info(f"\n报告已生成: {report_path}")


def main():
    """主函数"""
    logger.info("=" * 80)
    logger.info("GPU能耗模型间差异假设检验分析")
    logger.info("=" * 80)
    
    # 创建分析器
    tester = MetricTablesHypothesisTester(data_root='data')
    
    # 加载数据
    tester.load_all_raw_data()
    
    if len(tester.experiments) == 0:
        logger.error("未找到实验数据，退出")
        return
    
    # 运行检验
    tester.test_energy_across_models_by_task()
    
    logger.info("\n" + "=" * 80)
    logger.info("分析完成!")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()
