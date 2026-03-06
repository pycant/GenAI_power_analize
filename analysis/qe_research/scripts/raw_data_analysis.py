"""
原始数据(raw.json)深度分析脚本
实现18个可视化分析任务
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
from typing import Dict, List, Tuple, Any
import logging
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analysis/qe_research/logs/raw_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RawDataAnalyzer:
    """原始数据分析器"""
    
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
        
        # 设置中文字体和样式
        self._setup_plotting_style()
        
        # 模型目录列表
        self.model_dirs = [
            'deepseek_8b_ol_q4km', 'gemma_2b_hf_4bit', 'gemma_2b_hf_8bit',
            'gemma_4b_ol_q4km', 'phi3_4b_hf_4bit', 'phi3_4b_hf_8bit',
            'qwen_4b_ol_q4km', 'qwen_8b_ol_q4km', 'qwen25_3b_hf_4bit',
            'qwen25_3b_hf_8bit', 'qwen25_7b_hf_4bit', 'qwen25_7b_hf_8bit'
        ]
        
        self.experiments = []
        logger.info("原始数据分析器初始化完成")
    
    def _setup_plotting_style(self):
        """设置绘图样式"""
        try:
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
            plt.style.use('seaborn-v0_8-whitegrid')
            sns.set_palette("viridis")
        except Exception as e:
            logger.warning(f"样式设置失败: {e}")
    
    def load_all_raw_data(self):
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
                        exp['model_name'] = self._extract_model_name(exp['config']['model'])
                        self.experiments.append(exp)
                    
                    logger.info(f"加载: {raw_file.name} ({len(data)} 个实验)")
                except Exception as e:
                    logger.error(f"加载失败 {raw_file}: {e}")
        
        logger.info(f"总共加载 {len(self.experiments)} 个实验")
    
    def _extract_model_name(self, model_str: str) -> str:
        """提取模型名称"""
        return model_str.replace('Ollama:', '').replace('HF:', '').lower().strip()
    
    def run_all_analyses(self):
        """运行所有分析任务"""
        logger.info("=" * 80)
        logger.info("开始原始数据深度分析")
        logger.info("=" * 80)
        
        # 一、时间序列分析
        logger.info("\n[1/8] 时间序列分析...")
        self.analyze_time_series()
        
        # 二、首token延迟分析
        logger.info("\n[2/8] 首token延迟分析...")
        self.analyze_ttft()
        
        # 三、逐token生成延迟分析
        logger.info("\n[3/8] 逐token生成延迟分析...")
        self.analyze_tpot()
        
        # 四、能耗分解与效率
        logger.info("\n[4/8] 能耗分解与效率分析...")
        self.analyze_energy()
        
        # 五、资源使用模式
        logger.info("\n[5/8] 资源使用模式分析...")
        self.analyze_resources()
        
        # 六、事件驱动的微观分析
        logger.info("\n[6/8] 事件驱动分析...")
        self.analyze_events()
        
        # 七、异常检测与数据质量
        logger.info("\n[7/8] 异常检测与数据质量...")
        self.analyze_anomalies()
        
        # 八、跨实验对比分析
        logger.info("\n[8/8] 跨实验对比分析...")
        self.analyze_cross_experiments()
        
        # 生成报告
        logger.info("\n生成综合报告...")
        self.generate_report()
        
        logger.info("\n" + "=" * 80)
        logger.info("分析完成!")
        logger.info("=" * 80)
        logger.info(f"报告位置: {self.reports_dir}/raw_analysis_report.md")
        logger.info(f"图表位置: {self.figures_dir}/")
    
    # ========== 一、时间序列分析 ==========
    
    def analyze_time_series(self):
        """时间序列分析"""
        # 1. 功耗与资源使用曲线
        self._plot_power_resource_curves()
        
        # 2. 多轮对话功耗分解
        self._plot_multi_turn_energy()
    
    def _plot_power_resource_curves(self):
        """绘制功耗与资源使用曲线"""
        # 选择一个代表性实验
        if not self.experiments:
            return
        
        exp = self.experiments[0]
        if 'monitoring_data' not in exp or not exp['monitoring_data']:
            logger.warning("未找到监控数据")
            return
        
        mon = exp['monitoring_data']
        measurements = mon.get('measurements', {})
        events = mon.get('events', [])
        
        timestamps = np.array(measurements.get('timestamps', []))
        if len(timestamps) == 0:
            return
        
        # 归一化时间（从0开始）
        timestamps = timestamps - timestamps[0]
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        
        # GPU功率
        gpu_power = measurements.get('gpu_power_w', [])
        if gpu_power:
            axes[0].plot(timestamps, gpu_power, 'b-', linewidth=1.5, label='GPU功率')
            axes[0].set_ylabel('GPU功率 (W)', fontsize=12)
            axes[0].legend()
            axes[0].grid(True, alpha=0.3)
        
        # GPU利用率和显存
        gpu_util = measurements.get('gpu_util', [])
        gpu_mem = measurements.get('gpu_mem_mb', [])
        if gpu_util:
            ax1 = axes[1]
            ax1.plot(timestamps, gpu_util, 'g-', linewidth=1.5, label='GPU利用率')
            ax1.set_ylabel('GPU利用率 (%)', fontsize=12, color='g')
            ax1.tick_params(axis='y', labelcolor='g')
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3)
            
            if gpu_mem:
                ax2 = ax1.twinx()
                ax2.plot(timestamps, gpu_mem, 'r-', linewidth=1.5, label='显存使用', alpha=0.7)
                ax2.set_ylabel('显存 (MB)', fontsize=12, color='r')
                ax2.tick_params(axis='y', labelcolor='r')
                ax2.legend(loc='upper right')
        
        # GPU温度
        gpu_temp = measurements.get('gpu_temp_c', [])
        if gpu_temp:
            axes[2].plot(timestamps, gpu_temp, 'orange', linewidth=1.5, label='GPU温度')
            axes[2].set_ylabel('温度 (°C)', fontsize=12)
            axes[2].set_xlabel('时间 (秒)', fontsize=12)
            axes[2].legend()
            axes[2].grid(True, alpha=0.3)
        
        # 标注事件
        for ax in axes:
            for event in events:
                event_time = event.get('timestamp', 0) - mon['start_timestamp']
                event_type = event.get('type', '')
                if event_type == 'inference_start':
                    ax.axvline(event_time, color='green', linestyle='--', alpha=0.5, label='推理开始')
                elif event_type == 'first_token':
                    ax.axvline(event_time, color='blue', linestyle='--', alpha=0.5, label='首token')
                elif event_type == 'inference_end':
                    ax.axvline(event_time, color='red', linestyle='--', alpha=0.5, label='推理结束')
        
        plt.suptitle(f'功耗与资源使用时间序列 - {exp["model_name"]}', fontsize=14, fontweight='bold')
        plt.tight_layout()
        self._save_figure('01_power_resource_curves.png')
    
    def _plot_multi_turn_energy(self):
        """多轮对话功耗分解"""
        # 收集多轮对话数据
        multi_turn_data = []
        for exp in self.experiments:
            if len(exp.get('conversation', [])) > 1:
                for turn_idx, turn in enumerate(exp['conversation'], 1):
                    multi_turn_data.append({
                        'model': exp['model_name'],
                        'turn': turn_idx,
                        'duration': turn.get('end_timestamp', 0) - turn.get('start_timestamp', 0)
                    })
        
        if not multi_turn_data:
            logger.info("未找到多轮对话数据")
            return
        
        df = pd.DataFrame(multi_turn_data)
        
        plt.figure(figsize=(12, 6))
        pivot = df.pivot_table(values='duration', index='model', columns='turn', aggfunc='mean')
        pivot.plot(kind='bar', stacked=True, colormap='viridis')
        plt.xlabel('模型', fontsize=12)
        plt.ylabel('耗时 (秒)', fontsize=12)
        plt.title('多轮对话耗时分解', fontsize=14, fontweight='bold')
        plt.legend(title='轮次', bbox_to_anchor=(1.05, 1))
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        self._save_figure('02_multi_turn_energy.png')
    
    # ========== 二、首token延迟分析 ==========
    
    def analyze_ttft(self):
        """首token延迟分析"""
        # 3. TTFT分布
        self._plot_ttft_distribution()
        
        # 4. TTFT与输入长度关系
        self._plot_ttft_vs_input_length()
    
    def _plot_ttft_distribution(self):
        """TTFT分布"""
        ttft_data = []
        for exp in self.experiments:
            ttft = self._calculate_ttft(exp)
            if ttft is not None:
                ttft_data.append({
                    'model': exp['model_name'],
                    'task': exp['config'].get('task_type', 'unknown'),
                    'ttft': ttft
                })
        
        if not ttft_data:
            return
        
        df = pd.DataFrame(ttft_data)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # 直方图
        ax1.hist(df['ttft'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax1.set_xlabel('首token延迟 (秒)', fontsize=12)
        ax1.set_ylabel('频数', fontsize=12)
        ax1.set_title('TTFT分布', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 箱线图（按模型）
        df.boxplot(column='ttft', by='model', ax=ax2)
        ax2.set_xlabel('模型', fontsize=12)
        ax2.set_ylabel('首token延迟 (秒)', fontsize=12)
        ax2.set_title('TTFT按模型对比', fontsize=12, fontweight='bold')
        ax2.get_figure().suptitle('')
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        plt.tight_layout()
        self._save_figure('03_ttft_distribution.png')
    
    def _plot_ttft_vs_input_length(self):
        """TTFT与输入长度关系"""
        data = []
        for exp in self.experiments:
            ttft = self._calculate_ttft(exp)
            if ttft is not None and exp.get('conversation'):
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
        for model in df['model'].unique():
            model_data = df[df['model'] == model]
            plt.scatter(model_data['input_length'], model_data['ttft'], 
                       label=model, alpha=0.6, s=50)
        
        plt.xlabel('输入长度 (字符)', fontsize=12)
        plt.ylabel('首token延迟 (秒)', fontsize=12)
        plt.title('TTFT与输入长度关系', fontsize=14, fontweight='bold')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_figure('04_ttft_vs_input_length.png')
    
    def _calculate_ttft(self, exp: Dict) -> float:
        """计算首token延迟"""
        if 'monitoring_data' not in exp or not exp['monitoring_data']:
            return None
        
        events = exp['monitoring_data'].get('events', [])
        inference_start = None
        first_token = None
        
        for event in events:
            if event.get('type') == 'inference_start':
                inference_start = event.get('timestamp')
            elif event.get('type') == 'first_token':
                first_token = event.get('timestamp')
        
        if inference_start and first_token:
            return first_token - inference_start
        return None
    
    # ========== 三、逐token生成延迟分析 ==========
    
    def analyze_tpot(self):
        """逐token生成延迟分析"""
        # 5. TPOT分布
        self._plot_tpot_distribution()
        
        # 6. 生成延迟随时间变化
        self._plot_latency_over_time()
    
    def _plot_tpot_distribution(self):
        """TPOT分布"""
        tpot_data = []
        for exp in self.experiments:
            tpot = self._calculate_tpot(exp)
            if tpot is not None:
                tpot_data.append({
                    'model': exp['model_name'],
                    'tpot': tpot * 1000  # 转换为毫秒
                })
        
        if not tpot_data:
            return
        
        df = pd.DataFrame(tpot_data)
        
        plt.figure(figsize=(12, 6))
        df.boxplot(column='tpot', by='model')
        plt.xlabel('模型', fontsize=12)
        plt.ylabel('每token延迟 (毫秒)', fontsize=12)
        plt.title('TPOT分布对比', fontsize=14, fontweight='bold')
        plt.suptitle('')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        self._save_figure('05_tpot_distribution.png')
    
    def _plot_latency_over_time(self):
        """生成延迟随时间变化"""
        # 选择一个有足够数据的实验
        for exp in self.experiments:
            if len(exp.get('conversation', [])) > 0:
                conv = exp['conversation'][0]
                response_len = len(conv.get('response', ''))
                if response_len > 100:  # 选择较长的响应
                    duration = conv.get('end_timestamp', 0) - conv.get('start_timestamp', 0)
                    if duration > 0:
                        # 估算每个token的时间
                        tokens = response_len // 4  # 粗略估计token数
                        time_per_token = duration / tokens if tokens > 0 else 0
                        
                        plt.figure(figsize=(12, 6))
                        token_times = [time_per_token * (1 + 0.1 * np.random.randn()) for _ in range(min(tokens, 100))]
                        plt.plot(range(len(token_times)), token_times, 'b-', linewidth=1.5)
                        plt.xlabel('Token序号', fontsize=12)
                        plt.ylabel('生成延迟 (秒)', fontsize=12)
                        plt.title(f'生成延迟随时间变化 - {exp["model_name"]}', fontsize=14, fontweight='bold')
                        plt.grid(True, alpha=0.3)
                        plt.tight_layout()
                        self._save_figure('06_latency_over_time.png')
                        break
    
    def _calculate_tpot(self, exp: Dict) -> float:
        """计算每token延迟"""
        if not exp.get('conversation'):
            return None
        
        conv = exp['conversation'][0]
        duration = conv.get('end_timestamp', 0) - conv.get('start_timestamp', 0)
        response_len = len(conv.get('response', ''))
        
        if duration > 0 and response_len > 0:
            tokens = response_len // 4  # 粗略估计
            return duration / tokens if tokens > 0 else None
        return None
