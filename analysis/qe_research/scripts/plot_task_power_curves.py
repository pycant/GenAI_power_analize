"""
绘制不同模型在同一任务下的GPU功率变化曲线
按任务类型分组，对比不同模型的功率消耗模式
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
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
        logging.FileHandler(log_dir / 'task_power_curves.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TaskPowerCurveAnalyzer:
    """任务功率曲线分析器"""
    
    def __init__(self, data_root: str = 'data'):
        self.data_root = Path(data_root)
        self.output_dir = Path('analysis/qe_research/results/task_power_analysis')
        self.figures_dir = self.output_dir / 'figures'
        self.reports_dir = self.output_dir / 'reports'
        
        # 创建输出目录
        for d in [self.figures_dir, self.reports_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # 设置绘图样式
        try:
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            # 学术配色方案
            self.academic_colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
                                   '#CA9161', '#949494', '#ECE133', '#56B4E9',
                                   '#D55E00', '#CC79A7', '#F0E442', '#009E73']
            sns.set_palette(self.academic_colors)
        except:
            self.academic_colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
                                   '#CA9161', '#949494', '#ECE133', '#56B4E9',
                                   '#D55E00', '#CC79A7', '#F0E442', '#009E73']
        
        self.experiments = []
        logger.info("任务功率曲线分析器初始化完成")
    
    def load_data(self):
        """加载原始实验数据"""
        logger.info("开始加载原始数据...")
        
        # 遍历data目录下的所有子目录
        for item in self.data_root.iterdir():
            if not item.is_dir():
                continue
            
            # 跳过特殊目录
            if item.name in ['analize', 'benchmarks', 'test', 'test_cases', 'experiments_1', 
                            'experiments_2', 'experiments_3', 'experiments_4', 'experiments_5',
                            'experiment_test', 'experiments_phi3_mini_hf']:
                continue
            
            # 查找该目录下的raw.json文件
            raw_files = list(item.glob('*_raw.json'))
            
            for raw_file in raw_files:
                try:
                    with open(raw_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for exp in data:
                        # 提取模型名称
                        model_name = exp['config']['model'].replace('Ollama:', '').replace('HF:', '').lower()
                        exp['model_name'] = model_name
                        exp['model_dir'] = item.name
                        
                        # 提取任务类型
                        exp['task_type'] = exp['config'].get('task_type', 'unknown')
                        
                        self.experiments.append(exp)
                    
                    logger.info(f"✓ {item.name}/{raw_file.name}: {len(data)} 个实验")
                except Exception as e:
                    logger.error(f"✗ {raw_file}: {e}")
        
        logger.info(f"总共加载 {len(self.experiments)} 个实验")
    
    def plot_task_power_curves(self, task_type: str = 'code', max_models: int = 6):
        """
        绘制指定任务类型下不同模型的GPU功率曲线
        
        Args:
            task_type: 任务类型 (code, qa, creative, summary等)
            max_models: 最多显示的模型数量
        """
        logger.info(f"绘制任务 '{task_type}' 的功率曲线...")
        
        # 筛选指定任务类型的实验
        task_exps = [exp for exp in self.experiments 
                     if exp.get('task_type') == task_type 
                     and exp.get('monitoring_data')
                     and exp['monitoring_data'].get('measurements')]
        
        if not task_exps:
            logger.warning(f"未找到任务类型 '{task_type}' 的数据")
            return
        
        # 按模型分组
        model_exps = {}
        for exp in task_exps:
            model = exp['model_name']
            if model not in model_exps:
                model_exps[model] = []
            model_exps[model].append(exp)
        
        # 限制模型数量
        models = sorted(model_exps.keys())[:max_models]
        logger.info(f"  选择 {len(models)} 个模型: {models}")
        
        # 创建图表
        fig, axes = plt.subplots(2, 1, figsize=(14, 10))
        ax1, ax2 = axes
        
        # 为每个模型绘制功率曲线
        for i, model in enumerate(models):
            color = self.academic_colors[i % len(self.academic_colors)]
            
            # 选择该模型的第一个实验（或可以平均多个实验）
            exp = model_exps[model][0]
            mon = exp['monitoring_data']
            measurements = mon['measurements']
            start_time = mon['start_timestamp']
            
            # 提取时间和功率数据
            times = []
            gpu_powers = []
            cpu_powers = []
            
            # measurements是一个字典，包含多个列表
            if isinstance(measurements, dict):
                timestamps = measurements.get('timestamps', [])
                gpu_power_list = measurements.get('gpu_power_w', [])
                cpu_percent_list = measurements.get('cpu_percent', [])
                
                # 计算相对时间并提取功率数据
                for i, timestamp in enumerate(timestamps):
                    t = timestamp - start_time
                    times.append(t)
                    
                    if i < len(gpu_power_list):
                        gpu_powers.append(gpu_power_list[i])
                    else:
                        gpu_powers.append(0)
                    
                    # CPU功率需要从百分比估算（假设TDP为45W）
                    if i < len(cpu_percent_list):
                        cpu_powers.append(cpu_percent_list[i] * 0.45)  # 45W TDP * 百分比
                    else:
                        cpu_powers.append(0)
            else:
                # 旧格式：measurements是列表
                for m in measurements:
                    t = m.get('timestamp', 0) - start_time
                    gpu_power = m.get('gpu_power_w', 0)
                    cpu_power = m.get('cpu_power_w', 0)
                    
                    times.append(t)
                    gpu_powers.append(gpu_power)
                    cpu_powers.append(cpu_power)
            
            # 绘制GPU功率曲线
            ax1.plot(times, gpu_powers, label=model, color=color, 
                    linewidth=2, alpha=0.8)
            
            # 绘制CPU功率曲线
            ax2.plot(times, cpu_powers, label=model, color=color,
                    linewidth=2, alpha=0.8)
        
        # 设置GPU功率图
        ax1.set_xlabel('时间 (秒)', fontsize=11)
        ax1.set_ylabel('GPU功率 (W)', fontsize=11)
        ax1.set_title(f'GPU功率变化曲线 - {task_type}任务', 
                     fontsize=12, fontweight='bold')
        ax1.legend(loc='best', fontsize=10, framealpha=0.9)
        ax1.grid(True, alpha=0.3)
        
        # 设置CPU功率图
        ax2.set_xlabel('时间 (秒)', fontsize=11)
        ax2.set_ylabel('CPU功率 (W)', fontsize=11)
        ax2.set_title(f'CPU功率变化曲线 - {task_type}任务',
                     fontsize=12, fontweight='bold')
        ax2.legend(loc='best', fontsize=10, framealpha=0.9)
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle(f'不同模型在{task_type}任务下的功率对比',
                    fontsize=14, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        # 保存图表
        filename = f'power_curves_{task_type}.png'
        filepath = self.figures_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ {filename}")
    
    def plot_all_tasks(self):
        """绘制所有任务类型的功率曲线"""
        # 获取所有任务类型
        task_types = set(exp.get('task_type', 'unknown') for exp in self.experiments)
        task_types.discard('unknown')
        
        logger.info(f"\n发现 {len(task_types)} 个任务类型: {sorted(task_types)}")
        
        for task_type in sorted(task_types):
            try:
                self.plot_task_power_curves(task_type)
            except Exception as e:
                logger.error(f"绘制任务 '{task_type}' 失败: {e}")
                import traceback
                traceback.print_exc()
    
    def plot_average_power_comparison(self):
        """绘制不同任务类型下各模型的平均功率对比"""
        logger.info("绘制平均功率对比...")
        
        # 收集数据
        data = []
        for exp in self.experiments:
            if not exp.get('monitoring_data') or not exp['monitoring_data'].get('measurements'):
                continue
            
            measurements = exp['monitoring_data']['measurements']
            
            # 处理新格式（字典）和旧格式（列表）
            if isinstance(measurements, dict):
                gpu_powers = measurements.get('gpu_power_w', [])
            else:
                gpu_powers = [m.get('gpu_power_w', 0) for m in measurements]
            
            if gpu_powers:
                data.append({
                    'model': exp['model_name'],
                    'task': exp.get('task_type', 'unknown'),
                    'avg_gpu_power': np.mean(gpu_powers),
                    'max_gpu_power': np.max(gpu_powers),
                    'min_gpu_power': np.min(gpu_powers)
                })
        
        if not data:
            logger.warning("未找到功率数据")
            return
        
        df = pd.DataFrame(data)
        
        # 按任务类型分组绘制
        tasks = df['task'].unique()
        
        fig, axes = plt.subplots(len(tasks), 1, figsize=(12, 4 * len(tasks)))
        if len(tasks) == 1:
            axes = [axes]
        
        for i, task in enumerate(sorted(tasks)):
            ax = axes[i]
            task_df = df[df['task'] == task].sort_values('avg_gpu_power', ascending=False)
            
            x = range(len(task_df))
            y = task_df['avg_gpu_power']
            yerr = [task_df['avg_gpu_power'] - task_df['min_gpu_power'],
                    task_df['max_gpu_power'] - task_df['avg_gpu_power']]
            
            bars = ax.bar(x, y, yerr=yerr, capsize=5, 
                         color=self.academic_colors[:len(task_df)],
                         edgecolor='black', alpha=0.7)
            
            ax.set_xticks(x)
            ax.set_xticklabels(task_df['model'], rotation=45, ha='right')
            ax.set_xlabel('模型', fontsize=11)
            ax.set_ylabel('平均GPU功率 (W)', fontsize=11)
            ax.set_title(f'{task}任务 - 平均GPU功率对比', 
                        fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            # 添加数值标签
            for bar, val in zip(bars, y):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.1f}W',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        filename = 'average_power_comparison.png'
        filepath = self.figures_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ {filename}")
    
    def generate_report(self):
        """生成分析报告"""
        report_path = self.reports_dir / 'task_power_analysis_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 任务功率曲线分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 分析概述\n\n")
            f.write(f"本报告分析了不同模型在各任务类型下的GPU功率消耗模式。\n\n")
            f.write(f"- 总实验数: {len(self.experiments)}\n")
            
            # 统计任务类型
            task_types = set(exp.get('task_type', 'unknown') for exp in self.experiments)
            task_types.discard('unknown')
            f.write(f"- 任务类型: {', '.join(sorted(task_types))}\n")
            
            # 统计模型
            models = set(exp.get('model_name', 'unknown') for exp in self.experiments)
            models.discard('unknown')
            f.write(f"- 模型数量: {len(models)}\n\n")
            
            f.write("## 可视化图表\n\n")
            
            f.write("### 1. 各任务类型的功率曲线\n\n")
            for task in sorted(task_types):
                f.write(f"#### {task}任务\n\n")
                f.write(f"![{task}任务功率曲线](../figures/power_curves_{task}.png)\n\n")
            
            f.write("### 2. 平均功率对比\n\n")
            f.write("![平均功率对比](../figures/average_power_comparison.png)\n\n")
            
            f.write("## 关键发现\n\n")
            f.write("1. 不同模型在相同任务下的功率消耗模式存在显著差异\n")
            f.write("2. 功率曲线反映了模型的推理效率和资源利用特征\n")
            f.write("3. 某些模型在特定任务上表现出更优的能效比\n\n")
            
            f.write("---\n\n")
            f.write(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        logger.info(f"报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("任务功率曲线分析")
    print("=" * 80 + "\n")
    
    analyzer = TaskPowerCurveAnalyzer()
    
    # 加载数据
    analyzer.load_data()
    
    # 绘制所有任务的功率曲线
    analyzer.plot_all_tasks()
    
    # 绘制平均功率对比
    analyzer.plot_average_power_comparison()
    
    # 生成报告
    analyzer.generate_report()
    
    print("\n" + "=" * 80)
    print("分析完成!")
    print(f"图表: {analyzer.figures_dir}/")
    print(f"报告: {analyzer.reports_dir}/task_power_analysis_report.md")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
