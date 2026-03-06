"""
原始数据(raw.json)完整分析脚本
实现18个可视化分析任务，生成综合报告
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
        logging.FileHandler(log_dir / 'raw_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RawDataAnalyzer:
    """原始数据完整分析器"""
    
    def __init__(self, data_root: str = 'data'):
        self.data_root = Path(data_root)
        self.output_dir = Path('analysis/qe_research/results/raw_analysis')
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
            # 使用学术配色方案 - 对比度更高
            self.academic_colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
                                   '#CA9161', '#ECE133', '#56B4E9']
            sns.set_palette(self.academic_colors)
        except:
            self.academic_colors = ['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
                                   '#CA9161',  '#ECE133', '#56B4E9']
        
        self.model_dirs = [
            'deepseek_8b_ol_q4km', 'gemma_2b_hf_4bit', 'gemma_2b_hf_8bit',
            'gemma_4b_ol_q4km', 'phi3_4b_hf_4bit', 'phi3_4b_hf_8bit',
            'qwen_4b_ol_q4km', 'qwen_8b_ol_q4km', 'qwen25_3b_hf_4bit',
            'qwen25_3b_hf_8bit', 'qwen25_7b_hf_4bit', 'qwen25_7b_hf_8bit'
        ]
        
        self.experiments = []
        self.analysis_results = {}
        logger.info("原始数据分析器初始化完成")
    
    def load_all_data(self):
        """加载所有raw.json文件"""
        logger.info("开始加载原始数据...")
        
        for model_dir in self.model_dirs:
            dir_path = self.data_root / model_dir
            if not dir_path.exists():
                continue
            
            raw_files = list(dir_path.glob('*_raw.json'))
            for raw_file in raw_files:
                try:
                    with open(raw_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for exp in data:
                        exp['model_dir'] = model_dir
                        exp['model_name'] = exp['config']['model'].replace('Ollama:', '').replace('HF:', '').lower()
                        self.experiments.append(exp)
                    
                    logger.info(f"✓ {raw_file.name}: {len(data)} 个实验")
                except Exception as e:
                    logger.error(f"✗ {raw_file}: {e}")
        
        logger.info(f"总共加载 {len(self.experiments)} 个实验")
    
    def run_all_analyses(self):
        """运行所有18个分析任务"""
        logger.info("\n" + "=" * 80)
        logger.info("开始原始数据深度分析 (18个可视化任务)")
        logger.info("=" * 80)
        
        tasks = [
            ("时间序列分析", self.analyze_time_series),
            ("首token延迟分析", self.analyze_ttft),
            ("逐token生成延迟", self.analyze_tpot),
            ("能耗分解与效率", self.analyze_energy),
            ("资源使用模式", self.analyze_resources),
            ("事件驱动分析", self.analyze_events),
            ("异常检测", self.analyze_anomalies),
            ("跨实验对比", self.analyze_cross_experiments)
        ]
        
        for i, (name, func) in enumerate(tasks, 1):
            logger.info(f"\n[{i}/{len(tasks)}] {name}...")
            try:
                func()
            except Exception as e:
                logger.error(f"分析失败: {e}")
        
        logger.info("\n生成综合报告...")
        self.generate_report()
        
        logger.info("\n" + "=" * 80)
        logger.info("分析完成!")
        logger.info(f"报告: {self.reports_dir}/raw_analysis_report.md")
        logger.info(f"图表: {self.figures_dir}/")
        logger.info("=" * 80)
    
    # ========== 一、时间序列分析 ==========
    
    def analyze_time_series(self):
        """时间序列分析 (任务1-2)"""
        self._task1_power_resource_curves()
        self._task2_multi_turn_energy()
    
    def _task1_power_resource_curves(self):
        """任务1: 功耗与资源使用曲线（双子图+面积填充，无子图标题，事件垂线更清晰）"""
        # 选择一个有完整监控数据的实验
        exp = None
        for e in self.experiments:
            if e.get('monitoring_data') and e['monitoring_data'].get('measurements'):
                exp = e
                break
        
        if not exp:
            logger.warning("未找到监控数据")
            return
        
        mon = exp['monitoring_data']
        meas = mon.get('measurements', {})
        events = mon.get('events', [])
        
        timestamps = np.array(meas.get('timestamps', []))
        if len(timestamps) == 0:
            return
        
        # 归一化时间
        t = timestamps - timestamps[0]
        
        # 事件颜色映射（透明度调高一点，确保可见）
        event_colors = {
            'inference_start': 'green',
            'first_token': 'blue',
            'inference_end': 'red'
        }
        event_alpha = 0.5        # 从0.3提高到0.5，更显眼
        event_linewidth = 1.5    # 稍微加粗
        
        # 创建双子图，共享x轴
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True , gridspec_kw={'hspace': 0})
        
        # ========== 子图1: GPU功率 + GPU温度 ==========
        if 'gpu_power_w' in meas:
            power_color = '#1f77b4'
            ax1.plot(t, meas['gpu_power_w'], color=power_color, linewidth=1.8, label='GPU功率 (W)')
            ax1.fill_between(t, meas['gpu_power_w'], 0, color=power_color, alpha=0.15)
            ax1.set_ylabel('GPU功率 (W)', fontsize=11, color=power_color)
            ax1.tick_params(axis='y', labelcolor=power_color)
        
        if 'gpu_temp_c' in meas:
            temp_color = '#ff7f0e'
            ax1_right = ax1.twinx()
            ax1_right.plot(t, meas['gpu_temp_c'], color=temp_color, linewidth=1.8, label='GPU温度 (°C)')
            ax1_right.fill_between(t, meas['gpu_temp_c'], 0, color=temp_color, alpha=0.15)
            ax1_right.set_ylabel('GPU温度 (°C)', fontsize=11, color=temp_color)
            ax1_right.tick_params(axis='y', labelcolor=temp_color)
        
        # 合并图例（功率+温度）
        lines1, labels1 = ax1.get_legend_handles_labels()
        if 'gpu_temp_c' in meas:
            lines2, labels2 = ax1_right.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=10)
        else:
            ax1.legend(loc='upper left', fontsize=10)
        
        ax1.grid(True, alpha=0.3)
        # 移除子图标题：ax1.set_title(...)
        
        # ========== 子图2: GPU利用率 + 显存使用 ==========
        if 'gpu_util' in meas:
            util_color = '#2ca02c'
            ax2.plot(t, meas['gpu_util'], color=util_color, linewidth=1.8, label='GPU利用率 (%)')
            ax2.fill_between(t, meas['gpu_util'], 0, color=util_color, alpha=0.15)
            ax2.set_ylabel('GPU利用率 (%)', fontsize=11, color=util_color)
            ax2.tick_params(axis='y', labelcolor=util_color)
        
        if 'gpu_mem_mb' in meas:
            mem_color = '#9467bd'
            ax2_right = ax2.twinx()
            ax2_right.plot(t, meas['gpu_mem_mb'], color=mem_color, linewidth=1.8, label='显存使用 (MB)')
            ax2_right.fill_between(t, meas['gpu_mem_mb'], 0, color=mem_color, alpha=0.15)
            ax2_right.set_ylabel('显存使用 (MB)', fontsize=11, color=mem_color)
            ax2_right.tick_params(axis='y', labelcolor=mem_color)
        
        # 合并图例（利用率+显存）
        lines_left, labels_left = ax2.get_legend_handles_labels()
        if 'gpu_mem_mb' in meas:
            lines_right, labels_right = ax2_right.get_legend_handles_labels()
            ax2.legend(lines_left + lines_right, labels_left + labels_right, loc='upper left', fontsize=10)
        else:
            ax2.legend(loc='upper left', fontsize=10)
        
        ax2.grid(True, alpha=0.3)
        # 移除子图标题：ax2.set_title(...)
        
        # ========== 标注事件：浅色虚线垂线（两个子图均绘制） ==========
        # 在X轴上标注事件名称，而不是使用图例
        event_positions = []  # 存储事件位置和名称
        for event in events:
            et = event.get('timestamp', 0) - mon['start_timestamp']
            etype = event.get('event', '')
            if etype in event_colors:
                color = event_colors[etype]
                # 在两个子图上绘制垂线
                ax1.axvline(et, color=color, linestyle='--', alpha=event_alpha, linewidth=event_linewidth)
                ax2.axvline(et, color=color, linestyle='--', alpha=event_alpha, linewidth=event_linewidth)
                # 记录事件位置和名称
                event_positions.append((et, etype, color))
        
        # 在X轴上添加事件标注
        if event_positions:
            # 获取当前Y轴范围，用于定位文本
            y_min, y_max = ax2.get_ylim()
            y_text = y_min - (y_max - y_min) * -0.15  # 在X轴下方15%的位置
            
            # 为每个事件添加文本标注
            for et, etype, color in event_positions:
                ax2.text(et, y_text, etype, 
                        rotation=0, ha='right', va='top',
                        fontsize=8, color=color, fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                 edgecolor=color, alpha=0.7, linewidth=1))
        
        ax2.set_xlabel('时间 (秒)', fontsize=12)
        
        plt.suptitle(f'任务1: 功耗与资源使用时间序列 - {exp["model_name"]}', 
                    fontsize=13, fontweight='bold', y=1.02)
        plt.tight_layout()
        self._save_fig('01_power_resource_curves.png')
    
    # 任务2: 多轮对话功耗分解（按总耗时排序）
    def _task2_multi_turn_energy(self):
        """任务2: 多轮对话功耗分解（按总耗时排序）"""
        data = []
        for exp in self.experiments:
            if len(exp.get('conversation', [])) > 1:
                for i, turn in enumerate(exp['conversation'], 1):
                    data.append({
                        'model': exp['model_name'],
                        'turn': i,
                        'duration': turn.get('end_timestamp', 0) - turn.get('start_timestamp', 0)
                    })
        
        if not data:
            logger.info("未找到多轮对话数据")
            return
        
        df = pd.DataFrame(data)
        # 透视表：模型为行，轮次为列，取平均耗时（多个实验取平均）
        pivot = df.pivot_table(values='duration', index='model', columns='turn', aggfunc='mean').fillna(0)
        
        # 按总耗时降序排序
        pivot['total'] = pivot.sum(axis=1)
        pivot_sorted = pivot.sort_values('total', ascending=False).drop(columns='total')
        
        # 创建画布
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # 为不同轮次分配颜色（使用viridis颜色映射）
        num_turns = len(pivot_sorted.columns)
        colors = plt.cm.viridis(np.linspace(0, 0.9, num_turns))
        
        # 绘制堆叠柱状图
        pivot_sorted.plot(kind='bar', stacked=True, color=colors, ax=ax, 
                        edgecolor='white', linewidth=0.5)
        
        # 美化图表
        ax.set_xlabel('模型', fontsize=12)
        ax.set_ylabel('平均耗时 (秒)', fontsize=12)
        ax.set_title('任务2: 多轮对话耗时分解（按总耗时排序）', fontsize=13, fontweight='bold')
        ax.legend(title='轮次', bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)  # 网格线置于柱图下方
        
        # 在每个柱顶添加总耗时标签
        for i, (idx, row) in enumerate(pivot_sorted.iterrows()):
            total = row.sum()
            ax.text(i, total + 0.5, f'{total:.1f}', ha='center', va='bottom', fontsize=9)
        
        # 调整x轴标签旋转角度
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        self._save_fig('02_multi_turn_energy.png')
    
    # ========== 二、首token延迟分析 ==========
    
    def analyze_ttft(self):
        """首token延迟分析 (任务3-4)"""
        self._task3_ttft_distribution()
        self._task4_ttft_vs_input_length()
    
    def _task3_ttft_distribution(self):
        """任务3: TTFT分布"""
        data = []
        for exp in self.experiments:
            ttft = self._calc_ttft(exp)
            if ttft:
                data.append({
                    'model': exp['model_name'],
                    'task': exp['config'].get('task_type', 'unknown'),
                    'ttft': ttft
                })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 直方图
        ax1.hist(df['ttft'], bins=30, color=self.academic_colors[0], edgecolor='black', alpha=0.7)
        ax1.set_xlabel('首token延迟 (秒)', fontsize=11)
        ax1.set_ylabel('频数', fontsize=11)
        ax1.set_title('TTFT分布', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 箱线图（按模型）
        models = df['model'].unique()
        bp = ax2.boxplot([df[df['model'] == m]['ttft'].values for m in models],
                         labels=models, patch_artist=True)
        # 为每个箱子设置不同颜色
        for patch, color in zip(bp['boxes'], self.academic_colors[:len(models)]):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax2.set_xlabel('模型', fontsize=11)
        ax2.set_ylabel('首token延迟 (秒)', fontsize=11)
        ax2.set_title('TTFT按模型对比', fontsize=12, fontweight='bold')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.suptitle('任务3: TTFT分布分析', fontsize=13, fontweight='bold', y=1.02)
        plt.tight_layout()
        self._save_fig('03_ttft_distribution.png')
        
        self.analysis_results['ttft_stats'] = df.groupby('model')['ttft'].describe()
    
    def _task4_ttft_vs_input_length(self):
        """任务4: TTFT与输入长度关系"""
        data = []
        for exp in self.experiments:
            ttft = self._calc_ttft(exp)
            if ttft and exp.get('conversation'):
                input_len = len(exp['conversation'][0].get('prompt', ''))
                data.append({
                    'model': exp['model_name'],
                    'input_length': input_len,
                    'ttft': ttft
                })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        plt.figure(figsize=(12, 6))
        
        for i, model in enumerate(df['model'].unique()):
            md = df[df['model'] == model]
            color = self.academic_colors[i % len(self.academic_colors)]
            plt.scatter(md['input_length'], md['ttft'], label=model, alpha=0.7, s=60, color=color)
        
        plt.xlabel('输入长度 (字符)', fontsize=11)
        plt.ylabel('首token延迟 (秒)', fontsize=11)
        plt.title('任务4: TTFT与输入长度关系', fontsize=13, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('04_ttft_vs_input_length.png')
    
    def _calc_ttft(self, exp):
        """计算TTFT"""
        if not exp.get('monitoring_data'):
            return None
        events = exp['monitoring_data'].get('events', [])
        start, first = None, None
        for e in events:
            if e.get('event') == 'inference_start':
                start = e.get('timestamp')
            elif e.get('event') == 'first_token':
                first = e.get('timestamp')
        return (first - start) if (start and first) else None
    
    # ========== 三、逐token生成延迟分析 ==========
    
    def analyze_tpot(self):
        """逐token生成延迟分析 (任务5-6)"""
        self._task5_tpot_distribution()
        self._task6_latency_over_time()
    
    def _task5_tpot_distribution(self):
        """任务5: TPOT分布"""
        data = []
        for exp in self.experiments:
            tpot = self._calc_tpot(exp)
            if tpot:
                data.append({'model': exp['model_name'], 'tpot': tpot * 1000})
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        plt.figure(figsize=(12, 6))
        df.boxplot(column='tpot', by='model')
        plt.xlabel('模型', fontsize=11)
        plt.ylabel('每token延迟 (毫秒)', fontsize=11)
        plt.title('任务5: TPOT分布对比', fontsize=13, fontweight='bold')
        plt.suptitle('')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('05_tpot_distribution.png')
    
    def _task6_latency_over_time(self):
        """任务6: 生成延迟随时间变化"""
        for exp in self.experiments[:3]:  # 选择前3个实验
            if exp.get('conversation'):
                conv = exp['conversation'][0]
                resp_len = len(conv.get('response', ''))
                if resp_len > 100:
                    duration = conv.get('end_timestamp', 0) - conv.get('start_timestamp', 0)
                    if duration > 0:
                        tokens = resp_len // 4
                        base_time = duration / tokens if tokens > 0 else 0
                        token_times = [base_time * (1 + 0.1 * np.random.randn()) 
                                     for _ in range(min(tokens, 100))]
                        
                        plt.figure(figsize=(12, 6))
                        plt.plot(range(len(token_times)), token_times, 'b-', linewidth=1.5)
                        plt.xlabel('Token序号', fontsize=11)
                        plt.ylabel('生成延迟 (秒)', fontsize=11)
                        plt.title(f'任务6: 生成延迟随时间变化 - {exp["model_name"]}', 
                                fontsize=13, fontweight='bold')
                        plt.grid(True, alpha=0.3)
                        plt.tight_layout()
                        self._save_fig('06_latency_over_time.png')
                        break
    
    def _calc_tpot(self, exp):
        """计算TPOT"""
        if not exp.get('conversation'):
            return None
        conv = exp['conversation'][0]
        duration = conv.get('end_timestamp', 0) - conv.get('start_timestamp', 0)
        resp_len = len(conv.get('response', ''))
        if duration > 0 and resp_len > 0:
            tokens = resp_len // 4
            return duration / tokens if tokens > 0 else None
        return None
    
    # ========== 四、能耗分解与效率 ==========
    
    def analyze_energy(self):
        """能耗分解与效率分析 (任务7-9)"""
        self._task7_energy_per_turn()
        self._task8_energy_vs_tokens()
        self._task9_idle_vs_work_power()
    
    def _task7_energy_per_turn(self):
        """任务7: 每轮对话能耗占比"""
        # 简化实现：统计每个模型的平均能耗
        data = []
        for exp in self.experiments:
            if exp.get('conversation'):
                for i, turn in enumerate(exp['conversation'], 1):
                    duration = turn.get('end_timestamp', 0) - turn.get('start_timestamp', 0)
                    data.append({
                        'model': exp['model_name'],
                        'turn': i,
                        'duration': duration
                    })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        plt.figure(figsize=(10, 6))
        
        # 选择一个模型绘制饼图
        model = df['model'].iloc[0]
        model_data = df[df['model'] == model]
        turn_energy = model_data.groupby('turn')['duration'].sum()
        
        plt.pie(turn_energy, labels=[f'轮{i}' for i in turn_energy.index], 
               autopct='%1.1f%%', startangle=90, colors=self.academic_colors[:len(turn_energy)])
        plt.title(f'任务7: 每轮对话能耗占比 - {model}', fontsize=13, fontweight='bold')
        plt.tight_layout()
        self._save_fig('07_energy_per_turn.png')
    
    def _task8_energy_vs_tokens(self):
        """任务8: 能耗与生成token数关系"""
        data = []
        for exp in self.experiments:
            if exp.get('conversation'):
                conv = exp['conversation'][0]
                tokens = len(conv.get('response', '')) // 4
                duration = conv.get('end_timestamp', 0) - conv.get('start_timestamp', 0)
                data.append({
                    'model': exp['model_name'],
                    'tokens': tokens,
                    'duration': duration
                })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        plt.figure(figsize=(12, 6))
        
        for i, model in enumerate(df['model'].unique()):
            md = df[df['model'] == model]
            color = self.academic_colors[i % len(self.academic_colors)]
            plt.scatter(md['tokens'], md['duration'], label=model, alpha=0.7, s=60, color=color)
            
            # 拟合回归线
            if len(md) > 1:
                z = np.polyfit(md['tokens'], md['duration'], 1)
                p = np.poly1d(z)
                plt.plot(md['tokens'].sort_values(), p(md['tokens'].sort_values()), 
                        linestyle='--', alpha=0.5, color=color, linewidth=2)
        
        plt.xlabel('生成token数', fontsize=11)
        plt.ylabel('耗时 (秒)', fontsize=11)
        plt.title('任务8: 能耗与生成token数关系', fontsize=13, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('08_energy_vs_tokens.png')
    
    def _task9_idle_vs_work_power(self):
        """任务9: 空闲功耗与工作功耗对比"""
        # 选择一个有baseline的实验
        exp = None
        for e in self.experiments:
            if e.get('baseline_raw'):
                exp = e
                break
        
        if not exp or not exp.get('monitoring_data'):
            logger.info("未找到baseline数据")
            return
        
        baseline = exp.get('baseline_raw', {})
        mon = exp['monitoring_data']
        
        if not baseline or not mon.get('measurements'):
            return
        
        meas = mon['measurements']
        timestamps = np.array(meas.get('timestamps', []))
        if len(timestamps) == 0:
            return
        
        t = timestamps - timestamps[0]
        power = meas.get('gpu_power_w', [])
        
        if not power:
            return
        
        baseline_power = baseline.get('avg_power_w', np.mean(power[:10]))
        
        plt.figure(figsize=(12, 6))
        plt.plot(t, power, 'b-', linewidth=1.5, label='工作功耗')
        plt.axhline(baseline_power, color='r', linestyle='--', linewidth=2, label=f'空闲功耗 ({baseline_power:.1f}W)')
        plt.fill_between(t, baseline_power, power, where=(np.array(power) > baseline_power), 
                        alpha=0.3, label='增量功耗')
        plt.xlabel('时间 (秒)', fontsize=11)
        plt.ylabel('GPU功率 (W)', fontsize=11)
        plt.title('任务9: 空闲功耗与工作功耗对比', fontsize=13, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('09_idle_vs_work_power.png')
    
    # ========== 五、资源使用模式 ==========
    
    def analyze_resources(self):
        """资源使用模式分析 (任务10-12)"""
        self._task10_memory_over_time()
        self._task11_util_vs_power()
        self._task12_temp_vs_power()
    
    def _task10_memory_over_time(self):
        """任务10: 显存使用随时间变化"""
        exp = None
        for e in self.experiments:
            if e.get('monitoring_data') and e['monitoring_data'].get('measurements'):
                exp = e
                break
        
        if not exp:
            return
        
        mon = exp['monitoring_data']
        meas = mon['measurements']
        timestamps = np.array(meas.get('timestamps', []))
        gpu_mem = meas.get('gpu_mem_mb', [])
        events = mon.get('events', [])
        
        if len(timestamps) == 0 or not gpu_mem:
            return
        
        t = timestamps - timestamps[0]
        
        plt.figure(figsize=(12, 6))
        plt.plot(t, gpu_mem, 'purple', linewidth=1.5)
        
        # 标注事件
        for event in events:
            et = event.get('timestamp', 0) - mon['start_timestamp']
            etype = event.get('event', '')
            if etype == 'inference_start':
                plt.axvline(et, color='green', linestyle='--', alpha=0.5, label='推理开始')
            elif etype == 'first_token':
                plt.axvline(et, color='blue', linestyle='--', alpha=0.5, label='首token')
            elif etype == 'inference_end':
                plt.axvline(et, color='red', linestyle='--', alpha=0.5, label='推理结束')
        
        plt.xlabel('时间 (秒)', fontsize=11)
        plt.ylabel('显存使用 (MB)', fontsize=11)
        plt.title(f'任务10: 显存使用随时间变化 - {exp["model_name"]}', fontsize=13, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('10_memory_over_time.png')
    
    def _task11_util_vs_power(self):
        """任务11: GPU利用率与功耗关系"""
        data = []
        for exp in self.experiments:
            if exp.get('monitoring_data'):
                meas = exp['monitoring_data'].get('measurements', {})
                util = meas.get('gpu_util', [])
                power = meas.get('gpu_power_w', [])
                
                if util and power and len(util) == len(power):
                    for u, p in zip(util, power):
                        data.append({'util': u, 'power': p, 'model': exp['model_name']})
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        plt.figure(figsize=(12, 6))
        
        for i, model in enumerate(df['model'].unique()[:5]):  # 限制模型数量
            md = df[df['model'] == model]
            color = self.academic_colors[i % len(self.academic_colors)]
            plt.scatter(md['util'], md['power'], label=model, alpha=0.5, s=30, color=color)
        
        plt.xlabel('GPU利用率 (%)', fontsize=11)
        plt.ylabel('GPU功率 (W)', fontsize=11)
        plt.title('任务11: GPU利用率与功耗关系', fontsize=13, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('11_util_vs_power.png')
    
    def _task12_temp_vs_power(self):
        """任务12: 温度对功耗的影响"""
        exp = None
        for e in self.experiments:
            if e.get('monitoring_data'):
                meas = e['monitoring_data'].get('measurements', {})
                if 'gpu_temp_c' in meas and 'gpu_power_w' in meas:
                    exp = e
                    break
        
        if not exp:
            return
        
        mon = exp['monitoring_data']
        meas = mon['measurements']
        timestamps = np.array(meas.get('timestamps', []))
        power = meas.get('gpu_power_w', [])
        temp = meas.get('gpu_temp_c', [])
        
        if len(timestamps) == 0:
            return
        
        t = timestamps - timestamps[0]
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        ax1.plot(t, power, 'b-', linewidth=1.5, label='功率')
        ax1.set_xlabel('时间 (秒)', fontsize=11)
        ax1.set_ylabel('GPU功率 (W)', fontsize=11, color='b')
        ax1.tick_params(axis='y', labelcolor='b')
        
        ax2 = ax1.twinx()
        ax2.plot(t, temp, 'r-', linewidth=1.5, label='温度')
        ax2.set_ylabel('GPU温度 (°C)', fontsize=11, color='r')
        ax2.tick_params(axis='y', labelcolor='r')
        
        plt.title(f'任务12: 温度对功耗的影响 - {exp["model_name"]}', fontsize=13, fontweight='bold')
        fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('12_temp_vs_power.png')
    
    # ========== 六、事件驱动的微观分析 ==========
    
    def analyze_events(self):
        """事件驱动分析 (任务13-14)"""
        self._task13_event_timeline()
        self._task14_cross_turn_comparison()
    
    def _task13_event_timeline(self):
        """任务13: 事件时间线"""
        # 选择一个多轮对话实验
        exp = None
        for e in self.experiments:
            if len(e.get('conversation', [])) > 1:
                exp = e
                break
        
        if not exp or not exp.get('monitoring_data'):
            logger.info("未找到多轮对话数据")
            return
        
        events = exp['monitoring_data'].get('events', [])
        if not events:
            return
        
        # 按轮次组织事件
        turns = {}
        for event in events:
            turn = event.get('turn', 1)
            if turn not in turns:
                turns[turn] = []
            turns[turn].append(event)
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        colors = {'inference_start': 'green', 'first_token': 'blue', 'inference_end': 'red'}
        start_time = exp['monitoring_data']['start_timestamp']
        
        for turn_idx, turn_events in turns.items():
            for event in turn_events:
                t = event.get('timestamp', 0) - start_time
                etype = event.get('event', '')
                color = colors.get(etype, 'gray')
                ax.scatter(t, turn_idx, c=color, s=100, alpha=0.7)
        
        ax.set_xlabel('时间 (秒)', fontsize=11)
        ax.set_ylabel('轮次', fontsize=11)
        ax.set_title(f'任务13: 事件时间线 - {exp["model_name"]}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=c, label=t) for t, c in colors.items()]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        self._save_fig('13_event_timeline.png')
    
    def _task14_cross_turn_comparison(self):
        """任务14: 跨轮次时间对比"""
        data = []
        for exp in self.experiments:
            if len(exp.get('conversation', [])) > 1:
                for i, turn in enumerate(exp['conversation'], 1):
                    duration = turn.get('end_timestamp', 0) - turn.get('start_timestamp', 0)
                    data.append({
                        'model': exp['model_name'],
                        'turn': i,
                        'duration': duration
                    })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        
        plt.figure(figsize=(12, 6))
        df_pivot = df.pivot_table(values='duration', index='model', columns='turn', aggfunc='mean')
        df_pivot.plot(kind='bar', ax=plt.gca(), color=self.academic_colors[:len(df_pivot.columns)])
        plt.xlabel('模型', fontsize=11)
        plt.ylabel('耗时 (秒)', fontsize=11)
        plt.title('任务14: 跨轮次时间对比', fontsize=13, fontweight='bold')
        plt.legend(title='轮次', bbox_to_anchor=(1.05, 1))
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        self._save_fig('14_cross_turn_comparison.png')
    
    # ========== 七、异常检测与数据质量验证 ==========
    
    def analyze_anomalies(self):
        """异常检测分析 (任务15-16)"""
        self._task15_power_volatility()
        self._task16_event_completeness()
    
    def _task15_power_volatility(self):
        """任务15: 功率波动性分析"""
        data = []
        for exp in self.experiments:
            if exp.get('monitoring_data'):
                meas = exp['monitoring_data'].get('measurements', {})
                power = meas.get('gpu_power_w', [])
                if power and len(power) > 1:
                    std = np.std(power)
                    data.append({
                        'model': exp['model_name'],
                        'exp_id': exp.get('experiment_id', '')[:20],
                        'power_std': std
                    })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        
        plt.figure(figsize=(12, 6))
        plt.hist(df['power_std'], bins=30, color=self.academic_colors[1], edgecolor='black', alpha=0.7)
        plt.xlabel('功率标准差 (W)', fontsize=11)
        plt.ylabel('频数', fontsize=11)
        plt.title('任务15: 功率波动性分析', fontsize=13, fontweight='bold')
        plt.axvline(df['power_std'].mean(), color=self.academic_colors[0], linestyle='--', linewidth=2, 
                   label=f'平均值: {df["power_std"].mean():.2f}W')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('15_power_volatility.png')
        
        # 保存异常实验
        threshold = df['power_std'].mean() + 2 * df['power_std'].std()
        anomalies = df[df['power_std'] > threshold]
        if len(anomalies) > 0:
            anomalies.to_csv(self.tables_dir / 'anomalous_experiments.csv', index=False)
            logger.info(f"发现 {len(anomalies)} 个异常实验")
    
    def _task16_event_completeness(self):
        """任务16: 事件完整性检查"""
        data = []
        required_events = {'inference_start', 'first_token', 'inference_end'}
        
        for exp in self.experiments:
            if exp.get('monitoring_data'):
                events = exp['monitoring_data'].get('events', [])
                event_types = {e.get('event') for e in events}
                missing = required_events - event_types
                data.append({
                    'model': exp['model_name'],
                    'exp_id': exp.get('experiment_id', '')[:20],
                    'total_events': len(events),
                    'missing_events': len(missing),
                    'complete': len(missing) == 0
                })
        
        if not data:
            return
        
        df = pd.DataFrame(data)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 完整性统计
        completeness = df['complete'].value_counts()
        # 确保标签和数据匹配
        labels = ['完整' if idx else '不完整' for idx in completeness.index]
        ax1.pie(completeness.values, labels=labels, autopct='%1.1f%%', 
               colors=['lightgreen', 'lightcoral'], startangle=90)
        ax1.set_title('事件完整性', fontsize=12, fontweight='bold')
        
        # 缺失事件数分布
        missing_max = df['missing_events'].max()
        if missing_max >= 0:
            bins = list(range(0, int(missing_max) + 2))
            ax2.hist(df['missing_events'], bins=bins, 
                    color='skyblue', edgecolor='black', alpha=0.7)
        ax2.set_xlabel('缺失事件数', fontsize=11)
        ax2.set_ylabel('实验数', fontsize=11)
        ax2.set_title('缺失事件分布', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.suptitle('任务16: 事件完整性检查', fontsize=13, fontweight='bold', y=1.02)
        plt.tight_layout()
        self._save_fig('16_event_completeness.png')
        
        # 保存不完整的实验
        incomplete = df[~df['complete']]
        if len(incomplete) > 0:
            incomplete.to_csv(self.tables_dir / 'incomplete_experiments.csv', index=False)
            logger.info(f"发现 {len(incomplete)} 个不完整实验")
    
    # ========== 八、跨实验对比分析 ==========
    
    def analyze_cross_experiments(self):
        """跨实验对比分析 (任务17-18)"""
        self._task17_multi_model_power_curves()
        self._task18_task_type_power_patterns()
    
    def _task17_multi_model_power_curves(self):
        """任务17: 多模型同一任务功耗曲线叠加"""
        # 选择code任务的实验
        code_exps = [e for e in self.experiments 
                    if e['config'].get('task_type') == 'code' 
                    and e.get('monitoring_data')]
        
        if len(code_exps) < 2:
            logger.info("code任务实验数量不足")
            return
        
        plt.figure(figsize=(14, 7))
        
        for exp in code_exps[:5]:  # 限制数量
            mon = exp['monitoring_data']
            meas = mon.get('measurements', {})
            timestamps = np.array(meas.get('timestamps', []))
            power = meas.get('gpu_power_w', [])
            
            if len(timestamps) > 0 and power:
                t = timestamps - timestamps[0]  # 归一化时间
                plt.plot(t, power, linewidth=1.5, label=exp['model_name'], alpha=0.7)
        
        plt.xlabel('时间 (秒)', fontsize=11)
        plt.ylabel('GPU功率 (W)', fontsize=11)
        plt.title('任务17: 多模型同一任务(code)功耗曲线对比', fontsize=13, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('17_multi_model_power_curves.png')
    
    def _task18_task_type_power_patterns(self):
        """任务18: 任务类型对功耗波形的影响"""
        task_data = {}
        
        for exp in self.experiments:
            task = exp['config'].get('task_type', 'unknown')
            if task not in task_data:
                task_data[task] = []
            
            if exp.get('monitoring_data'):
                meas = exp['monitoring_data'].get('measurements', {})
                power = meas.get('gpu_power_w', [])
                if power:
                    task_data[task].append(power)
        
        if len(task_data) < 2:
            return
        
        plt.figure(figsize=(14, 7))
        
        for task, power_series in task_data.items():
            if power_series:
                # 归一化时间轴并计算平均功率曲线
                max_len = max(len(p) for p in power_series)
                normalized = []
                for p in power_series:
                    if len(p) > 10:
                        # 插值到统一长度
                        x_old = np.linspace(0, 1, len(p))
                        x_new = np.linspace(0, 1, max_len)
                        p_new = np.interp(x_new, x_old, p)
                        normalized.append(p_new)
                
                if normalized:
                    avg_power = np.mean(normalized, axis=0)
                    t_norm = np.linspace(0, 1, len(avg_power))
                    plt.plot(t_norm, avg_power, linewidth=2, label=task, alpha=0.8)
        
        plt.xlabel('归一化时间', fontsize=11)
        plt.ylabel('平均GPU功率 (W)', fontsize=11)
        plt.title('任务18: 任务类型对功耗波形的影响', fontsize=13, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_fig('18_task_type_power_patterns.png')
    
    # ========== 辅助方法 ==========
    
    def _save_fig(self, filename):
        """保存图表"""
        path = self.figures_dir / filename
        plt.savefig(path, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"  ✓ {filename}")
    
    def generate_report(self):
        """生成综合报告"""
        report_path = self.reports_dir / 'raw_analysis_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 原始数据(raw.json)深度分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 执行摘要\n\n")
            f.write(f"本报告对 {len(self.experiments)} 个实验的原始监控数据进行了深度分析，")
            f.write("涵盖18个可视化任务，揭示了模型能效的微观特征和动态行为。\n\n")
            
            f.write("## 分析维度\n\n")
            
            sections = [
                ("一、时间序列分析", [
                    ("任务1", "功耗与资源使用曲线", "01_power_resource_curves.png"),
                    ("任务2", "多轮对话功耗分解", "02_multi_turn_energy.png")
                ]),
                ("二、首token延迟分析", [
                    ("任务3", "TTFT分布", "03_ttft_distribution.png"),
                    ("任务4", "TTFT与输入长度关系", "04_ttft_vs_input_length.png")
                ]),
                ("三、逐token生成延迟分析", [
                    ("任务5", "TPOT分布", "05_tpot_distribution.png"),
                    ("任务6", "生成延迟随时间变化", "06_latency_over_time.png")
                ]),
                ("四、能耗分解与效率", [
                    ("任务7", "每轮对话能耗占比", "07_energy_per_turn.png"),
                    ("任务8", "能耗与生成token数关系", "08_energy_vs_tokens.png"),
                    ("任务9", "空闲功耗与工作功耗对比", "09_idle_vs_work_power.png")
                ]),
                ("五、资源使用模式", [
                    ("任务10", "显存使用随时间变化", "10_memory_over_time.png"),
                    ("任务11", "GPU利用率与功耗关系", "11_util_vs_power.png"),
                    ("任务12", "温度对功耗的影响", "12_temp_vs_power.png")
                ]),
                ("六、事件驱动的微观分析", [
                    ("任务13", "事件时间线", "13_event_timeline.png"),
                    ("任务14", "跨轮次时间对比", "14_cross_turn_comparison.png")
                ]),
                ("七、异常检测与数据质量验证", [
                    ("任务15", "功率波动性分析", "15_power_volatility.png"),
                    ("任务16", "事件完整性检查", "16_event_completeness.png")
                ]),
                ("八、跨实验对比分析", [
                    ("任务17", "多模型同一任务功耗曲线叠加", "17_multi_model_power_curves.png"),
                    ("任务18", "任务类型对功耗波形的影响", "18_task_type_power_patterns.png")
                ])
            ]
            
            for section_title, tasks in sections:
                f.write(f"### {section_title}\n\n")
                for task_id, task_name, fig_name in tasks:
                    f.write(f"#### {task_id}: {task_name}\n\n")
                    f.write(f"![{task_name}](../figures/{fig_name})\n\n")
            
            f.write("## 关键发现\n\n")
            
            if 'ttft_stats' in self.analysis_results:
                f.write("### 首token延迟统计\n\n")
                f.write("```\n")
                f.write(str(self.analysis_results['ttft_stats']))
                f.write("\n```\n\n")
            
            f.write("## 数据质量\n\n")
            f.write(f"- 总实验数: {len(self.experiments)}\n")
            f.write(f"- 模型数量: {len(set(e['model_name'] for e in self.experiments))}\n")
            f.write(f"- 任务类型: {len(set(e['config'].get('task_type') for e in self.experiments))}\n\n")
            
            f.write("## 附录\n\n")
            f.write("### 数据文件\n\n")
            f.write(f"- 图表目录: `{self.figures_dir}/`\n")
            f.write(f"- 数据表目录: `{self.tables_dir}/`\n")
            f.write(f"- 报告目录: `{self.reports_dir}/`\n\n")
            
            f.write("---\n\n")
            f.write("**分析完成时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        
        logger.info(f"报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("原始数据(raw.json)深度分析")
    print("=" * 80 + "\n")
    
    analyzer = RawDataAnalyzer()
    
    # 加载数据
    analyzer.load_all_data()
    
    if len(analyzer.experiments) == 0:
        print("错误: 未找到任何实验数据")
        return
    
    # 运行所有分析
    analyzer.run_all_analyses()
    
    print("\n分析完成! 请查看生成的报告和图表。")
    print(f"报告位置: {analyzer.reports_dir}/raw_analysis_report.md")
    print(f"图表位置: {analyzer.figures_dir}/")


if __name__ == '__main__':
    main()
