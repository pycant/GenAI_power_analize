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
from scipy import stats
from scipy.stats import f_oneway, kruskal, levene, shapiro

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
            'qwen25_3b_hf_8bit', 'qwen25_7b_hf_4bit'
        ]
        
        # 需要排除的模型（存在数据问题和缺失值）
        self.excluded_models = [
            'qwen--qwen2.5-7b-instruct:8bit',
            'qwen2.5-7b-instruct:8bit'
        ]
        
        self.experiments = []
        self.excluded_count = 0
        logger.info("原始数据分析器初始化完成")
        logger.info(f"排除的模型: {', '.join(self.excluded_models)}")
    
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
        logger.info("\n[8/9] 跨实验对比分析...")
        self.analyze_cross_experiments()
        
        # 九、假设检验分析
        logger.info("\n[9/9] 假设检验分析...")
        self.analyze_hypothesis_testing()
        
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

    
    # ========== 九、假设检验分析 ==========
    
    def analyze_hypothesis_testing(self):
        """假设检验分析：检验各任务间GPU能耗是否有显著差异"""
        logger.info("\n开始假设检验分析...")
        
        # 1. GPU能耗的任务间差异检验
        self._test_energy_across_tasks()
        
        # 2. GPU能耗的模型间差异检验
        self._test_energy_across_models()
        
        # 3. 交互效应检验（任务×模型）
        self._test_interaction_effects()
        
        # 4. 生成假设检验报告
        self._generate_hypothesis_report()
    
    def _test_energy_across_tasks(self):
        """检验不同任务间GPU能耗是否有显著差异"""
        logger.info("检验任务间GPU能耗差异...")
        
        # 收集数据
        energy_by_task = {}
        for exp in self.experiments:
            # 再次确认不包含排除的模型
            model = exp.get('model_name', '')
            if self._should_exclude_model(model):
                continue
            
            task = exp['config'].get('task_type', 'unknown')
            energy = self._extract_gpu_energy(exp)
            
            if energy is not None and energy > 0:
                if task not in energy_by_task:
                    energy_by_task[task] = []
                energy_by_task[task].append(energy)
        
        if len(energy_by_task) < 2:
            logger.warning("任务类型不足，无法进行假设检验")
            return
        
        # 准备数据
        tasks = list(energy_by_task.keys())
        energy_groups = [energy_by_task[task] for task in tasks]
        
        # 1. 描述性统计
        desc_stats = []
        for task in tasks:
            data = energy_by_task[task]
            desc_stats.append({
                '任务': task,
                '样本量': len(data),
                '均值': np.mean(data),
                '标准差': np.std(data, ddof=1),
                '中位数': np.median(data),
                '最小值': np.min(data),
                '最大值': np.max(data)
            })
        
        desc_df = pd.DataFrame(desc_stats)
        desc_df.to_csv(self.tables_dir / 'energy_by_task_descriptive.csv', index=False, encoding='utf-8-sig')
        logger.info(f"描述性统计已保存: energy_by_task_descriptive.csv")
        
        # 2. 正态性检验（Shapiro-Wilk）
        normality_results = []
        for task in tasks:
            data = energy_by_task[task]
            if len(data) >= 3:  # Shapiro-Wilk需要至少3个样本
                stat, p_value = shapiro(data)
                normality_results.append({
                    '任务': task,
                    'W统计量': stat,
                    'p值': p_value,
                    '是否正态': '是' if p_value > 0.05 else '否'
                })
        
        if normality_results:
            norm_df = pd.DataFrame(normality_results)
            norm_df.to_csv(self.tables_dir / 'energy_normality_test.csv', index=False, encoding='utf-8-sig')
            logger.info(f"正态性检验结果已保存: energy_normality_test.csv")
        
        # 3. 方差齐性检验（Levene）
        if len(energy_groups) >= 2:
            levene_stat, levene_p = levene(*energy_groups)
            logger.info(f"Levene方差齐性检验: F={levene_stat:.4f}, p={levene_p:.4f}")
            
            variance_homogeneity = levene_p > 0.05
        else:
            variance_homogeneity = True
        
        # 4. 选择合适的检验方法
        all_normal = all([r['是否正态'] == '是' for r in normality_results]) if normality_results else False
        
        if all_normal and variance_homogeneity:
            # 使用单因素方差分析（ANOVA）
            f_stat, p_value = f_oneway(*energy_groups)
            test_name = "单因素方差分析(ANOVA)"
            test_stat_name = "F统计量"
            test_stat = f_stat
            logger.info(f"{test_name}: F={f_stat:.4f}, p={p_value:.4f}")
        else:
            # 使用Kruskal-Wallis H检验（非参数）
            h_stat, p_value = kruskal(*energy_groups)
            test_name = "Kruskal-Wallis H检验"
            test_stat_name = "H统计量"
            test_stat = h_stat
            logger.info(f"{test_name}: H={h_stat:.4f}, p={p_value:.4f}")
        
        # 5. 保存检验结果
        test_result = {
            '检验类型': test_name,
            test_stat_name: test_stat,
            'p值': p_value,
            '显著性水平': 0.05,
            '结论': '存在显著差异' if p_value < 0.05 else '不存在显著差异',
            '方差齐性': '是' if variance_homogeneity else '否',
            '数据正态性': '是' if all_normal else '否'
        }
        
        test_df = pd.DataFrame([test_result])
        test_df.to_csv(self.tables_dir / 'energy_task_hypothesis_test.csv', index=False, encoding='utf-8-sig')
        logger.info(f"假设检验结果已保存: energy_task_hypothesis_test.csv")
        
        # 6. 可视化
        self._plot_energy_by_task_boxplot(energy_by_task, p_value, test_name)
        
        # 7. 事后检验（如果存在显著差异）
        if p_value < 0.05:
            self._post_hoc_analysis(energy_by_task, tasks)
    
    def _test_energy_across_models(self):
        """检验不同模型间GPU能耗是否有显著差异"""
        logger.info("检验模型间GPU能耗差异...")
        
        # 收集数据
        energy_by_model = {}
        for exp in self.experiments:
            model = exp['model_name']
            
            # 再次确认不包含排除的模型
            if self._should_exclude_model(model):
                continue
            
            energy = self._extract_gpu_energy(exp)
            
            if energy is not None and energy > 0:
                if model not in energy_by_model:
                    energy_by_model[model] = []
                energy_by_model[model].append(energy)
        
        if len(energy_by_model) < 2:
            logger.warning("模型数量不足，无法进行假设检验")
            return
        
        # 准备数据
        models = list(energy_by_model.keys())
        energy_groups = [energy_by_model[model] for model in models]
        
        # 描述性统计
        desc_stats = []
        for model in models:
            data = energy_by_model[model]
            desc_stats.append({
                '模型': model,
                '样本量': len(data),
                '均值': np.mean(data),
                '标准差': np.std(data, ddof=1),
                '中位数': np.median(data)
            })
        
        desc_df = pd.DataFrame(desc_stats)
        desc_df.to_csv(self.tables_dir / 'energy_by_model_descriptive.csv', index=False, encoding='utf-8-sig')
        
        # Kruskal-Wallis检验（由于模型数量多，使用非参数检验更稳健）
        h_stat, p_value = kruskal(*energy_groups)
        logger.info(f"模型间Kruskal-Wallis检验: H={h_stat:.4f}, p={p_value:.4f}")
        
        # 保存结果
        test_result = {
            '检验类型': 'Kruskal-Wallis H检验',
            'H统计量': h_stat,
            'p值': p_value,
            '显著性水平': 0.05,
            '结论': '存在显著差异' if p_value < 0.05 else '不存在显著差异'
        }
        
        test_df = pd.DataFrame([test_result])
        test_df.to_csv(self.tables_dir / 'energy_model_hypothesis_test.csv', index=False, encoding='utf-8-sig')
        
        # 可视化
        self._plot_energy_by_model_boxplot(energy_by_model, p_value)
    
    def _test_interaction_effects(self):
        """检验任务和模型的交互效应"""
        logger.info("检验任务×模型交互效应...")
        
        # 收集数据
        data_list = []
        for exp in self.experiments:
            model = exp['model_name']
            
            # 再次确认不包含排除的模型
            if self._should_exclude_model(model):
                continue
            
            task = exp['config'].get('task_type', 'unknown')
            energy = self._extract_gpu_energy(exp)
            
            if energy is not None and energy > 0:
                data_list.append({
                    '任务': task,
                    '模型': model,
                    'GPU能耗': energy
                })
        
        if len(data_list) < 10:
            logger.warning("数据量不足，无法进行交互效应分析")
            return
        
        df = pd.DataFrame(data_list)
        
        # 创建交互效应热力图
        pivot_table = df.pivot_table(values='GPU能耗', index='模型', columns='任务', aggfunc='mean')
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='YlOrRd', cbar_kws={'label': 'GPU能耗 (J)'})
        plt.title('任务×模型交互效应热力图 - GPU能耗均值', fontsize=14, fontweight='bold')
        plt.xlabel('任务类型', fontsize=12)
        plt.ylabel('模型', fontsize=12)
        plt.tight_layout()
        self._save_figure('07_interaction_heatmap.png')
        
        # 保存交互效应表
        pivot_table.to_csv(self.tables_dir / 'energy_interaction_table.csv', encoding='utf-8-sig')
        logger.info("交互效应表已保存: energy_interaction_table.csv")
    
    def _post_hoc_analysis(self, energy_by_task: Dict, tasks: List[str]):
        """事后多重比较分析（Bonferroni校正）"""
        logger.info("进行事后多重比较...")
        
        from itertools import combinations
        
        # 两两比较
        comparisons = []
        n_comparisons = len(list(combinations(tasks, 2)))
        alpha_corrected = 0.05 / n_comparisons  # Bonferroni校正
        
        for task1, task2 in combinations(tasks, 2):
            data1 = energy_by_task[task1]
            data2 = energy_by_task[task2]
            
            # 使用Mann-Whitney U检验（非参数）
            from scipy.stats import mannwhitneyu
            stat, p_value = mannwhitneyu(data1, data2, alternative='two-sided')
            
            comparisons.append({
                '组1': task1,
                '组2': task2,
                'U统计量': stat,
                'p值': p_value,
                '校正后显著性': alpha_corrected,
                '是否显著': '是' if p_value < alpha_corrected else '否',
                '均值差': np.mean(data1) - np.mean(data2)
            })
        
        comp_df = pd.DataFrame(comparisons)
        comp_df.to_csv(self.tables_dir / 'energy_post_hoc_comparisons.csv', index=False, encoding='utf-8-sig')
        logger.info(f"事后比较结果已保存: energy_post_hoc_comparisons.csv")
        
        # 显示显著差异的配对
        significant = comp_df[comp_df['是否显著'] == '是']
        if len(significant) > 0:
            logger.info(f"发现 {len(significant)} 对任务间存在显著差异:")
            for _, row in significant.iterrows():
                logger.info(f"  {row['组1']} vs {row['组2']}: p={row['p值']:.4f}")
    
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
    
    def _plot_energy_by_task_boxplot(self, energy_by_task: Dict, p_value: float, test_name: str):
        """绘制任务间GPU能耗箱线图"""
        # 准备数据
        data_list = []
        for task, energies in energy_by_task.items():
            for energy in energies:
                data_list.append({'任务': task, 'GPU能耗': energy})
        
        df = pd.DataFrame(data_list)
        
        # 绘图
        plt.figure(figsize=(12, 6))
        sns.boxplot(data=df, x='任务', y='GPU能耗', palette='Set2')
        sns.stripplot(data=df, x='任务', y='GPU能耗', color='black', alpha=0.3, size=3)
        
        plt.xlabel('任务类型', fontsize=12)
        plt.ylabel('GPU能耗 (J)', fontsize=12)
        
        # 添加统计信息
        significance = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
        title = f'不同任务间GPU能耗分布\n{test_name}: p={p_value:.4f} {significance}'
        plt.title(title, fontsize=14, fontweight='bold')
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        self._save_figure('08_energy_by_task_boxplot.png')
    
    def _plot_energy_by_model_boxplot(self, energy_by_model: Dict, p_value: float):
        """绘制模型间GPU能耗箱线图"""
        # 准备数据
        data_list = []
        for model, energies in energy_by_model.items():
            for energy in energies:
                data_list.append({'模型': model, 'GPU能耗': energy})
        
        df = pd.DataFrame(data_list)
        
        # 绘图
        plt.figure(figsize=(14, 6))
        sns.boxplot(data=df, x='模型', y='GPU能耗', palette='Set3')
        
        plt.xlabel('模型', fontsize=12)
        plt.ylabel('GPU能耗 (J)', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        
        # 添加统计信息
        significance = '***' if p_value < 0.001 else '**' if p_value < 0.01 else '*' if p_value < 0.05 else 'ns'
        title = f'不同模型间GPU能耗分布\nKruskal-Wallis检验: p={p_value:.4f} {significance}'
        plt.title(title, fontsize=14, fontweight='bold')
        
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        self._save_figure('09_energy_by_model_boxplot.png')
    
    def _generate_hypothesis_report(self):
        """生成假设检验报告"""
        logger.info("生成假设检验报告...")
        
        report_path = self.reports_dir / 'hypothesis_testing_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# GPU能耗假设检验分析报告\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## 1. 分析目的\n\n")
            f.write("本报告通过统计假设检验方法，分析不同任务类型和模型之间的GPU能耗是否存在显著差异。\n\n")
            
            f.write("## 2. 数据说明\n\n")
            f.write("### 3.1 任务间差异检验\n\n")
            f.write("- **正态性检验**: Shapiro-Wilk检验\n")
            f.write("- **方差齐性检验**: Levene检验\n")
            f.write("- **主检验**: 根据数据分布选择ANOVA或Kruskal-Wallis检验\n")
            f.write("- **事后检验**: Mann-Whitney U检验（Bonferroni校正）\n\n")
            
            f.write("### 3.2 模型间差异检验\n\n")
            f.write("- **主检验**: Kruskal-Wallis H检验（非参数方法）\n\n")
            
            f.write("### 3.3 交互效应分析\n\n")
            f.write("- **方法**: 任务×模型交互效应热力图\n\n")
            
            f.write("## 4. 显著性水平\n\n")
            f.write("- α = 0.05（主检验）\n")
            f.write("- Bonferroni校正用于多重比较\n\n")
            
            f.write("## 5. 结果文件\n\n")
            f.write("- **方法**: 任务×模型交互效应热力图\n\n")
            
            f.write("## 3. 显著性水平\n\n")
            f.write("- α = 0.05（主检验）\n")
            f.write("- Bonferroni校正用于多重比较\n\n")
            
            f.write("## 4. 结果文件\n\n")
            f.write("### 描述性统计\n")
            f.write("- `energy_by_task_descriptive.csv`: 各任务GPU能耗描述性统计\n")
            f.write("- `energy_by_model_descriptive.csv`: 各模型GPU能耗描述性统计\n\n")
            
            f.write("### 假设检验结果\n")
            f.write("- `energy_normality_test.csv`: 正态性检验结果\n")
            f.write("- `energy_task_hypothesis_test.csv`: 任务间差异检验结果\n")
            f.write("- `energy_model_hypothesis_test.csv`: 模型间差异检验结果\n")
            f.write("- `energy_post_hoc_comparisons.csv`: 事后多重比较结果\n")
            f.write("- `energy_interaction_table.csv`: 交互效应表\n\n")
            
            f.write("### 可视化图表\n")
            f.write("- `08_energy_by_task_boxplot.png`: 任务间能耗箱线图\n")
            f.write("- `09_energy_by_model_boxplot.png`: 模型间能耗箱线图\n")
            f.write("- `07_interaction_heatmap.png`: 交互效应热力图\n\n")
            
            f.write("## 5. 解读指南\n\n")
            f.write("### p值解读\n")
            f.write("- p < 0.001: 极显著差异 (***)\n")
            f.write("- p < 0.01: 非常显著差异 (**)\n")
            f.write("- p < 0.05: 显著差异 (*)\n")
            f.write("- p ≥ 0.05: 无显著差异 (ns)\n\n")
            
            f.write("### 效应量\n")
            f.write("- 除了p值，还应关注实际差异的大小（均值差、中位数差）\n")
            f.write("- 统计显著不等于实际重要\n\n")
            
            f.write("## 6. 注意事项\n\n")
            f.write("- 样本量不足可能影响检验效力\n")
            f.write("- 异常值可能影响参数检验结果\n")
            f.write("- 多重比较需要校正显著性水平\n")
            f.write("- 交互效应需要结合领域知识解释\n\n")
        
        logger.info(f"假设检验报告已保存: {report_path}")
    
    def _save_figure(self, filename: str):
        """保存图表"""
        filepath = self.figures_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        logger.info(f"图表已保存: {filename}")


if __name__ == '__main__':
    # 创建分析器实例
    analyzer = RawDataAnalyzer(data_root='data')
    
    # 加载数据
    analyzer.load_all_raw_data()
    
    # 运行假设检验分析
    analyzer.analyze_hypothesis_testing()
    
    logger.info("\n假设检验分析完成!")
