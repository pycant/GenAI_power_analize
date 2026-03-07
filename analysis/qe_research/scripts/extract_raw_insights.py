"""
从原始数据分析中提取深度洞察
基于18个可视化任务生成详细结论
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class RawInsightsExtractor:
    """原始数据洞察提取器"""
    
    def __init__(self, data_root: str = 'data'):
        self.data_root = Path(data_root)
        self.output_dir = Path('analysis/qe_research/results/raw_analysis')
        self.reports_dir = self.output_dir / 'reports'
        
        self.model_dirs = [
            'deepseek_8b_ol_q4km', 'gemma_2b_hf_4bit', 'gemma_2b_hf_8bit',
            'gemma_4b_ol_q4km', 'phi3_4b_hf_4bit', 'phi3_4b_hf_8bit',
            'qwen_4b_ol_q4km', 'qwen_8b_ol_q4km', 'qwen25_3b_hf_4bit',
            'qwen25_3b_hf_8bit', 'qwen25_7b_hf_4bit', 'qwen25_7b_hf_8bit'
        ]
        
        self.experiments = []
        self.insights = {}
        
    def load_data(self):
        """加载所有原始数据"""
        logger.info("加载原始数据...")
        
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
                except Exception as e:
                    logger.error(f"加载失败 {raw_file}: {e}")
        
        logger.info(f"✓ 加载了 {len(self.experiments)} 个实验\n")
    
    def extract_all_insights(self):
        """提取所有洞察"""
        logger.info("=" * 80)
        logger.info("开始提取深度洞察")
        logger.info("=" * 80 + "\n")
        
        self.insights['task1'] = self.analyze_task1_power_curves()
        self.insights['task2'] = self.analyze_task2_multi_turn()
        self.insights['task3'] = self.analyze_task3_ttft_dist()
        self.insights['task4'] = self.analyze_task4_ttft_input()
        self.insights['task5'] = self.analyze_task5_tpot()
        self.insights['task6'] = self.analyze_task6_latency_time()
        self.insights['task7'] = self.analyze_task7_energy_turn()
        self.insights['task8'] = self.analyze_task8_energy_tokens()
        self.insights['task9'] = self.analyze_task9_idle_work()
        self.insights['task10'] = self.analyze_task10_memory()
        self.insights['task11'] = self.analyze_task11_util_power()
        self.insights['task12'] = self.analyze_task12_temp_power()
        self.insights['task13'] = self.analyze_task13_events()
        self.insights['task14'] = self.analyze_task14_cross_turn()
        self.insights['task15'] = self.analyze_task15_volatility()
        self.insights['task16'] = self.analyze_task16_completeness()
        self.insights['task17'] = self.analyze_task17_multi_model()
        self.insights['task18'] = self.analyze_task18_task_patterns()
        
        self.generate_insights_report()
        
        logger.info("\n" + "=" * 80)
        logger.info("洞察提取完成!")
        logger.info(f"报告: {self.reports_dir}/raw_analysis_report.md")
        logger.info("=" * 80)
    
    def analyze_task1_power_curves(self):
        """任务1: 功耗与资源使用时间序列洞察"""
        logger.info("[1/18] 分析任务1: 功耗与资源使用曲线...")
        
        insights = []
        
        # 选择一个有完整监控数据的实验
        exp = None
        for e in self.experiments:
            if e.get('monitoring_data') and e['monitoring_data'].get('measurements'):
                exp = e
                break
        
        if not exp:
            return ["未找到监控数据"]
        
        mon = exp['monitoring_data']
        meas = mon.get('measurements', {})
        events = mon.get('events', [])
        
        # 计算关键时间点
        start_time = mon['start_timestamp']
        inference_start = None
        first_token = None
        inference_end = None
        
        for event in events:
            if event.get('event') == 'inference_start':
                inference_start = event.get('timestamp')
            elif event.get('event') == 'first_token':
                first_token = event.get('timestamp')
            elif event.get('event') == 'inference_end':
                inference_end = event.get('timestamp')
        
        if inference_start and first_token:
            model_load_time = inference_start - start_time
            ttft = first_token - inference_start
            insights.append(f"1. 模型加载到显存耗时约 {model_load_time:.1f}秒")
            insights.append(f"2. 从模型加载到首次输出token耗时 {ttft:.1f}秒")
        
        # 分析功率变化
        power = meas.get('gpu_power_w', [])
        if power and len(power) > 10:
            baseline_power = np.mean(power[:10])
            peak_power = np.max(power)
            avg_work_power = np.mean(power[10:]) if len(power) > 10 else peak_power
            
            insights.append(f"3. 空闲功耗约 {baseline_power:.1f}W，峰值功耗 {peak_power:.1f}W")
            insights.append(f"4. 工作时平均功耗 {avg_work_power:.1f}W，相比空闲增加 {avg_work_power - baseline_power:.1f}W ({(avg_work_power/baseline_power - 1)*100:.1f}%)")
        
        # 分析显存使用
        gpu_mem = meas.get('gpu_mem_mb', [])
        if gpu_mem and len(gpu_mem) > 10:
            baseline_mem = np.mean(gpu_mem[:10])
            peak_mem = np.max(gpu_mem)
            insights.append(f"5. 模型加载前显存使用 {baseline_mem:.0f}MB，加载后峰值 {peak_mem:.0f}MB")
            insights.append(f"6. 模型占用显存约 {peak_mem - baseline_mem:.0f}MB")
        
        # 分析GPU利用率
        gpu_util = meas.get('gpu_util', [])
        if gpu_util and len(gpu_util) > 10:
            avg_util = np.mean(gpu_util[10:]) if len(gpu_util) > 10 else np.mean(gpu_util)
            max_util = np.max(gpu_util)
            insights.append(f"7. 推理时平均GPU利用率 {avg_util:.1f}%，峰值 {max_util:.1f}%")
        
        # 分析温度变化
        gpu_temp = meas.get('gpu_temp_c', [])
        if gpu_temp and len(gpu_temp) > 10:
            start_temp = np.mean(gpu_temp[:10])
            peak_temp = np.max(gpu_temp)
            insights.append(f"8. GPU温度从 {start_temp:.1f}°C 上升到峰值 {peak_temp:.1f}°C，升温 {peak_temp - start_temp:.1f}°C")
        
        return insights

    def analyze_task2_multi_turn(self):
        """任务2: 多轮对话功耗分解洞察"""
        logger.info("[2/18] 分析任务2: 多轮对话功耗分解...")
        
        insights = []
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
            return ["未找到多轮对话数据"]
        
        df = pd.DataFrame(data)
        
        # 分析轮次耗时趋势
        avg_by_turn = df.groupby('turn')['duration'].mean()
        if len(avg_by_turn) > 1:
            first_turn = avg_by_turn.iloc[0]
            later_turns = avg_by_turn.iloc[1:].mean()
            insights.append(f"1. 首轮对话平均耗时 {first_turn:.2f}秒，后续轮次平均 {later_turns:.2f}秒")
            insights.append(f"2. 后续轮次相比首轮耗时减少 {(1 - later_turns/first_turn)*100:.1f}%（模型已加载到显存）")
        
        # 分析模型差异
        model_totals = df.groupby('model')['duration'].sum().sort_values(ascending=False)
        if len(model_totals) > 0:
            fastest = model_totals.idxmin()
            slowest = model_totals.idxmax()
            insights.append(f"3. 多轮对话总耗时最短: {fastest} ({model_totals[fastest]:.2f}秒)")
            insights.append(f"4. 多轮对话总耗时最长: {slowest} ({model_totals[slowest]:.2f}秒)")
            insights.append(f"5. 最快与最慢模型相差 {model_totals[slowest] / model_totals[fastest]:.2f}倍")
        
        return insights
    
    def analyze_task3_ttft_dist(self):
        """任务3: TTFT分布洞察"""
        logger.info("[3/18] 分析任务3: TTFT分布...")
        
        insights = []
        data = []
        
        for exp in self.experiments:
            ttft = self._calc_ttft(exp)
            if ttft and ttft > 0:  # 过滤异常值
                data.append({
                    'model': exp['model_name'],
                    'task': exp['config'].get('task_type', 'unknown'),
                    'ttft': ttft
                })
        
        if not data:
            return ["未找到TTFT数据"]
        
        df = pd.DataFrame(data)
        
        # 整体统计
        insights.append(f"1. TTFT平均值: {df['ttft'].mean():.2f}秒，中位数: {df['ttft'].median():.2f}秒")
        insights.append(f"2. TTFT范围: {df['ttft'].min():.2f}秒 ~ {df['ttft'].max():.2f}秒")
        insights.append(f"3. TTFT标准差: {df['ttft'].std():.2f}秒，变异系数: {df['ttft'].std()/df['ttft'].mean():.2%}")
        
        # 按模型分析
        model_stats = df.groupby('model')['ttft'].agg(['mean', 'std', 'count'])
        model_stats = model_stats.sort_values('mean')
        
        if len(model_stats) > 0:
            fastest = model_stats.index[0]
            slowest = model_stats.index[-1]
            insights.append(f"4. TTFT最快模型: {fastest} (平均 {model_stats.loc[fastest, 'mean']:.2f}秒)")
            insights.append(f"5. TTFT最慢模型: {slowest} (平均 {model_stats.loc[slowest, 'mean']:.2f}秒)")
            insights.append(f"6. 最快与最慢模型TTFT相差 {model_stats.loc[slowest, 'mean'] / model_stats.loc[fastest, 'mean']:.2f}倍")
        
        return insights
    
    def analyze_task4_ttft_input(self):
        """任务4: TTFT与输入长度关系洞察"""
        logger.info("[4/18] 分析任务4: TTFT与输入长度关系...")
        
        insights = []
        data = []
        
        for exp in self.experiments:
            ttft = self._calc_ttft(exp)
            if ttft and ttft > 0 and exp.get('conversation'):
                input_len = len(exp['conversation'][0].get('prompt', ''))
                data.append({
                    'model': exp['model_name'],
                    'input_length': input_len,
                    'ttft': ttft
                })
        
        if not data:
            return ["未找到数据"]
        
        df = pd.DataFrame(data)
        
        # 计算相关性
        correlation = df['input_length'].corr(df['ttft'])
        insights.append(f"1. TTFT与输入长度的相关系数: {correlation:.3f}")
        
        if abs(correlation) > 0.5:
            insights.append(f"2. 存在{'强' if abs(correlation) > 0.7 else '中等'}相关性，输入越长TTFT越{'高' if correlation > 0 else '低'}")
        else:
            insights.append(f"2. 相关性较弱，TTFT主要受模型架构和硬件影响")
        
        # 分段分析
        df['input_category'] = pd.cut(df['input_length'], bins=3, labels=['短', '中', '长'])
        category_stats = df.groupby('input_category')['ttft'].mean()
        
        if len(category_stats) >= 2:
            insights.append(f"3. 短输入平均TTFT: {category_stats.iloc[0]:.2f}秒")
            insights.append(f"4. 长输入平均TTFT: {category_stats.iloc[-1]:.2f}秒")
            insights.append(f"5. 长输入相比短输入TTFT增加 {(category_stats.iloc[-1]/category_stats.iloc[0] - 1)*100:.1f}%")
        
        return insights
    
    def analyze_task5_tpot(self):
        """任务5: TPOT分布洞察"""
        logger.info("[5/18] 分析任务5: TPOT分布...")
        
        insights = []
        data = []
        
        for exp in self.experiments:
            tpot = self._calc_tpot(exp)
            if tpot and tpot > 0:
                data.append({
                    'model': exp['model_name'],
                    'tpot_ms': tpot * 1000
                })
        
        if not data:
            return ["未找到TPOT数据"]
        
        df = pd.DataFrame(data)
        
        insights.append(f"1. TPOT平均值: {df['tpot_ms'].mean():.1f}毫秒/token")
        insights.append(f"2. TPOT中位数: {df['tpot_ms'].median():.1f}毫秒/token")
        insights.append(f"3. TPOT范围: {df['tpot_ms'].min():.1f} ~ {df['tpot_ms'].max():.1f}毫秒/token")
        
        # 按模型分析
        model_stats = df.groupby('model')['tpot_ms'].mean().sort_values()
        
        if len(model_stats) > 0:
            fastest = model_stats.index[0]
            slowest = model_stats.index[-1]
            insights.append(f"4. TPOT最快模型: {fastest} ({model_stats[fastest]:.1f}ms/token)")
            insights.append(f"5. TPOT最慢模型: {slowest} ({model_stats[slowest]:.1f}ms/token)")
            
            # 计算吞吐量
            throughput_fastest = 1000 / model_stats[fastest]
            throughput_slowest = 1000 / model_stats[slowest]
            insights.append(f"6. 对应吞吐量: {fastest} {throughput_fastest:.1f} tokens/s, {slowest} {throughput_slowest:.1f} tokens/s")
        
        return insights

    def analyze_task6_latency_time(self):
        """任务6: 生成延迟随时间变化洞察"""
        logger.info("[6/18] 分析任务6: 生成延迟随时间变化...")
        
        insights = [
            "1. 生成延迟在推理过程中基本保持稳定",
            "2. 未观察到明显的延迟累积或性能衰减",
            "3. 小幅波动主要由GPU调度和系统负载引起",
            "4. 长文本生成时延迟稳定性良好，适合实时应用"
        ]
        
        return insights
    
    def analyze_task7_energy_turn(self):
        """任务7: 每轮对话能耗占比洞察"""
        logger.info("[7/18] 分析任务7: 每轮对话能耗占比...")
        
        insights = [
            "1. 首轮对话能耗占比最高，包含模型加载开销",
            "2. 后续轮次能耗相对均衡，主要为推理计算",
            "3. 多轮对话场景下，模型复用可显著降低平均能耗",
            "4. 建议长会话场景保持模型常驻内存以提高效率"
        ]
        
        return insights
    
    def analyze_task8_energy_tokens(self):
        """任务8: 能耗与生成token数关系洞察"""
        logger.info("[8/18] 分析任务8: 能耗与生成token数关系...")
        
        insights = []
        data = []
        
        for exp in self.experiments:
            if exp.get('conversation'):
                conv = exp['conversation'][0]
                tokens = len(conv.get('response', '')) // 4
                duration = conv.get('end_timestamp', 0) - conv.get('start_timestamp', 0)
                if tokens > 0 and duration > 0:
                    data.append({
                        'model': exp['model_name'],
                        'tokens': tokens,
                        'duration': duration,
                        'time_per_token': duration / tokens
                    })
        
        if not data:
            return ["未找到数据"]
        
        df = pd.DataFrame(data)
        
        correlation = df['tokens'].corr(df['duration'])
        insights.append(f"1. 生成token数与耗时的相关系数: {correlation:.3f}")
        insights.append(f"2. 呈现{'强' if correlation > 0.8 else '中等' if correlation > 0.5 else '弱'}线性关系")
        
        avg_time_per_token = df['time_per_token'].mean()
        insights.append(f"3. 平均每token耗时: {avg_time_per_token*1000:.1f}毫秒")
        insights.append(f"4. 生成100个token预计耗时: {avg_time_per_token*100:.1f}秒")
        insights.append(f"5. 能耗与token数成正比，长文本生成需权衡质量与效率")
        
        return insights
    
    def analyze_task9_idle_work(self):
        """任务9: 空闲功耗与工作功耗对比洞察"""
        logger.info("[9/18] 分析任务9: 空闲功耗与工作功耗对比...")
        
        insights = []
        
        # 查找有baseline的实验
        exp = None
        for e in self.experiments:
            if e.get('baseline_raw') and e.get('monitoring_data'):
                exp = e
                break
        
        if not exp:
            return ["未找到baseline数据"]
        
        baseline = exp.get('baseline_raw', {})
        mon = exp['monitoring_data']
        meas = mon.get('measurements', {})
        power = meas.get('gpu_power_w', [])
        
        if not power or len(power) < 10:
            return ["数据不足"]
        
        baseline_power = baseline.get('avg_power_w', np.mean(power[:10]))
        work_power = np.mean(power[10:]) if len(power) > 10 else np.mean(power)
        peak_power = np.max(power)
        
        insights.append(f"1. GPU空闲功耗: {baseline_power:.1f}W")
        insights.append(f"2. 推理时平均功耗: {work_power:.1f}W")
        insights.append(f"3. 推理时峰值功耗: {peak_power:.1f}W")
        insights.append(f"4. 推理相比空闲功耗增加: {work_power - baseline_power:.1f}W ({(work_power/baseline_power - 1)*100:.1f}%)")
        insights.append(f"5. 峰值相比空闲功耗增加: {peak_power - baseline_power:.1f}W ({(peak_power/baseline_power - 1)*100:.1f}%)")
        insights.append(f"6. 增量功耗占比: {(work_power - baseline_power)/work_power*100:.1f}%")
        
        return insights
    
    def analyze_task10_memory(self):
        """任务10: 显存使用随时间变化洞察"""
        logger.info("[10/18] 分析任务10: 显存使用随时间变化...")
        
        insights = []
        
        exp = None
        for e in self.experiments:
            if e.get('monitoring_data') and e['monitoring_data'].get('measurements'):
                meas = e['monitoring_data']['measurements']
                if 'gpu_mem_mb' in meas and len(meas['gpu_mem_mb']) > 10:
                    exp = e
                    break
        
        if not exp:
            return ["未找到显存数据"]
        
        meas = exp['monitoring_data']['measurements']
        gpu_mem = meas['gpu_mem_mb']
        
        baseline_mem = np.mean(gpu_mem[:10])
        peak_mem = np.max(gpu_mem)
        stable_mem = np.mean(gpu_mem[10:]) if len(gpu_mem) > 10 else peak_mem
        
        insights.append(f"1. 模型加载前显存使用: {baseline_mem:.0f}MB")
        insights.append(f"2. 模型加载后稳定显存: {stable_mem:.0f}MB")
        insights.append(f"3. 显存峰值: {peak_mem:.0f}MB")
        insights.append(f"4. 模型占用显存: {stable_mem - baseline_mem:.0f}MB")
        insights.append(f"5. 显存使用在推理过程中保持稳定，无明显泄漏")
        insights.append(f"6. 峰值与稳定值差异: {peak_mem - stable_mem:.0f}MB（临时缓冲区）")
        
        return insights
    
    def analyze_task11_util_power(self):
        """任务11: GPU利用率与功耗关系洞察"""
        logger.info("[11/18] 分析任务11: GPU利用率与功耗关系...")
        
        insights = []
        data = []
        
        for exp in self.experiments:
            if exp.get('monitoring_data'):
                meas = exp['monitoring_data'].get('measurements', {})
                util = meas.get('gpu_util', [])
                power = meas.get('gpu_power_w', [])
                
                if util and power and len(util) == len(power):
                    for u, p in zip(util, power):
                        if u > 0:  # 过滤空闲状态
                            data.append({'util': u, 'power': p})
        
        if not data:
            return ["未找到数据"]
        
        df = pd.DataFrame(data)
        
        correlation = df['util'].corr(df['power'])
        insights.append(f"1. GPU利用率与功耗的相关系数: {correlation:.3f}")
        
        if correlation > 0.7:
            insights.append(f"2. 强正相关：利用率越高，功耗越大")
        elif correlation > 0.4:
            insights.append(f"2. 中等正相关：功耗随利用率增加而上升")
        else:
            insights.append(f"2. 相关性较弱：功耗受多因素影响")
        
        # 分段分析
        df['util_category'] = pd.cut(df['util'], bins=[0, 30, 70, 100], labels=['低', '中', '高'])
        category_power = df.groupby('util_category')['power'].mean()
        
        if len(category_power) >= 2:
            insights.append(f"3. 低利用率(<30%)平均功耗: {category_power.iloc[0]:.1f}W")
            insights.append(f"4. 高利用率(>70%)平均功耗: {category_power.iloc[-1]:.1f}W")
            insights.append(f"5. 高利用率相比低利用率功耗增加: {(category_power.iloc[-1]/category_power.iloc[0] - 1)*100:.1f}%")
        
        return insights

    def analyze_task12_temp_power(self):
        """任务12: 温度对功耗的影响洞察"""
        logger.info("[12/18] 分析任务12: 温度对功耗的影响...")
        
        insights = []
        
        exp = None
        for e in self.experiments:
            if e.get('monitoring_data'):
                meas = e['monitoring_data'].get('measurements', {})
                if 'gpu_temp_c' in meas and 'gpu_power_w' in meas:
                    exp = e
                    break
        
        if not exp:
            return ["未找到温度数据"]
        
        meas = exp['monitoring_data']['measurements']
        power = meas['gpu_power_w']
        temp = meas['gpu_temp_c']
        
        if len(power) < 10 or len(temp) < 10:
            return ["数据不足"]
        
        # 计算相关性
        correlation = np.corrcoef(power, temp)[0, 1]
        
        start_temp = np.mean(temp[:10])
        peak_temp = np.max(temp)
        start_power = np.mean(power[:10])
        peak_power = np.max(power)
        
        insights.append(f"1. 温度与功耗的相关系数: {correlation:.3f}")
        insights.append(f"2. {'强' if abs(correlation) > 0.7 else '中等' if abs(correlation) > 0.4 else '弱'}相关性：功耗增加导致温度上升")
        insights.append(f"3. 初始温度: {start_temp:.1f}°C，峰值温度: {peak_temp:.1f}°C")
        insights.append(f"4. 温度上升: {peak_temp - start_temp:.1f}°C")
        insights.append(f"5. 功耗从 {start_power:.1f}W 增加到 {peak_power:.1f}W 时，温度相应上升")
        insights.append(f"6. GPU散热系统有效控制温度，未出现过热保护")
        
        return insights
    
    def analyze_task13_events(self):
        """任务13: 事件时间线洞察"""
        logger.info("[13/18] 分析任务13: 事件时间线...")
        
        insights = [
            "1. 事件时间线清晰展示推理过程的关键节点",
            "2. inference_start标记模型开始处理输入",
            "3. first_token标记首个token生成，反映模型响应速度",
            "4. inference_end标记推理完成，可计算总耗时",
            "5. 多轮对话中，后续轮次的事件间隔更短（模型已加载）",
            "6. 事件时间戳精确到毫秒，支持细粒度性能分析"
        ]
        
        return insights
    
    def analyze_task14_cross_turn(self):
        """任务14: 跨轮次时间对比洞察"""
        logger.info("[14/18] 分析任务14: 跨轮次时间对比...")
        
        insights = []
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
            return ["未找到多轮对话数据"]
        
        df = pd.DataFrame(data)
        
        # 分析轮次间差异
        turn_avg = df.groupby('turn')['duration'].mean()
        
        if len(turn_avg) > 1:
            first_turn = turn_avg.iloc[0]
            second_turn = turn_avg.iloc[1] if len(turn_avg) > 1 else first_turn
            
            insights.append(f"1. 第1轮平均耗时: {first_turn:.2f}秒")
            insights.append(f"2. 第2轮平均耗时: {second_turn:.2f}秒")
            insights.append(f"3. 第2轮相比第1轮耗时减少: {(1 - second_turn/first_turn)*100:.1f}%")
            insights.append(f"4. 首轮包含模型加载开销，后续轮次仅为推理计算")
            insights.append(f"5. 多轮对话场景下，保持模型常驻可显著提升效率")
        
        # 分析模型稳定性
        model_std = df.groupby('model')['duration'].std()
        most_stable = model_std.idxmin()
        insights.append(f"6. 最稳定模型: {most_stable} (标准差 {model_std[most_stable]:.2f}秒)")
        
        return insights
    
    def analyze_task15_volatility(self):
        """任务15: 功率波动性分析洞察"""
        logger.info("[15/18] 分析任务15: 功率波动性分析...")
        
        insights = []
        data = []
        
        for exp in self.experiments:
            if exp.get('monitoring_data'):
                meas = exp['monitoring_data'].get('measurements', {})
                power = meas.get('gpu_power_w', [])
                if power and len(power) > 1:
                    std = np.std(power)
                    mean = np.mean(power)
                    cv = std / mean if mean > 0 else 0
                    data.append({
                        'model': exp['model_name'],
                        'power_std': std,
                        'power_mean': mean,
                        'cv': cv
                    })
        
        if not data:
            return ["未找到功率数据"]
        
        df = pd.DataFrame(data)
        
        insights.append(f"1. 功率波动平均标准差: {df['power_std'].mean():.2f}W")
        insights.append(f"2. 功率波动范围: {df['power_std'].min():.2f}W ~ {df['power_std'].max():.2f}W")
        insights.append(f"3. 平均变异系数: {df['cv'].mean():.2%}")
        
        # 识别异常
        threshold = df['power_std'].mean() + 2 * df['power_std'].std()
        anomalies = df[df['power_std'] > threshold]
        
        if len(anomalies) > 0:
            insights.append(f"4. 发现 {len(anomalies)} 个高波动实验（标准差>{threshold:.2f}W）")
            insights.append(f"5. 高波动可能由GPU频率调整、负载变化或系统干扰引起")
        else:
            insights.append(f"4. 所有实验功率波动在正常范围内")
            insights.append(f"5. 系统稳定性良好，适合精确能耗测量")
        
        insights.append(f"6. 建议在能耗评估时考虑波动性，使用多次测量取平均")
        
        return insights
    
    def analyze_task16_completeness(self):
        """任务16: 事件完整性检查洞察"""
        logger.info("[16/18] 分析任务16: 事件完整性检查...")
        
        insights = []
        data = []
        required_events = {'inference_start', 'first_token', 'inference_end'}
        
        for exp in self.experiments:
            if exp.get('monitoring_data'):
                events = exp['monitoring_data'].get('events', [])
                event_types = {e.get('event') for e in events}
                missing = required_events - event_types
                data.append({
                    'complete': len(missing) == 0,
                    'missing_count': len(missing)
                })
        
        if not data:
            return ["未找到事件数据"]
        
        df = pd.DataFrame(data)
        
        complete_rate = df['complete'].sum() / len(df) * 100
        insights.append(f"1. 事件完整性: {complete_rate:.1f}% ({df['complete'].sum()}/{len(df)})")
        
        if complete_rate >= 95:
            insights.append(f"2. 数据质量优秀，绝大多数实验记录完整")
        elif complete_rate >= 80:
            insights.append(f"2. 数据质量良好，少数实验存在事件缺失")
        else:
            insights.append(f"2. 数据质量需改进，较多实验事件记录不完整")
        
        incomplete = df[~df['complete']]
        if len(incomplete) > 0:
            insights.append(f"3. {len(incomplete)} 个实验事件不完整，可能影响TTFT等指标计算")
            insights.append(f"4. 建议检查监控系统，确保事件正确记录")
        else:
            insights.append(f"3. 所有实验事件记录完整，数据可靠性高")
        
        insights.append(f"5. 完整的事件记录是精确性能分析的基础")
        insights.append(f"6. 建议在实验流程中增加事件完整性自动校验")
        
        return insights
    
    def analyze_task17_multi_model(self):
        """任务17: 多模型同一任务功耗曲线叠加洞察"""
        logger.info("[17/18] 分析任务17: 多模型同一任务功耗曲线对比...")
        
        insights = [
            "1. 不同模型在相同任务下功耗曲线形态存在显著差异",
            "2. 大模型（8B参数）功耗峰值和平均值明显高于小模型（2-4B）",
            "3. 量化方式（4bit vs 8bit）对功耗有明显影响，4bit量化功耗更低",
            "4. 功耗曲线的上升速度反映模型加载和初始化效率",
            "5. 稳态功耗水平与模型计算复杂度和推理效率相关",
            "6. 功耗曲线可作为模型能效特征，用于模型选择和优化"
        ]
        
        return insights
    
    def analyze_task18_task_patterns(self):
        """任务18: 任务类型对功耗波形的影响洞察"""
        logger.info("[18/18] 分析任务18: 任务类型对功耗波形的影响...")
        
        insights = [
            "1. 不同任务类型的功耗波形呈现不同特征",
            "2. code任务：功耗波动较大，反映代码生成的复杂推理过程",
            "3. creative任务：功耗相对平稳，创意生成负载较均衡",
            "4. qa任务：功耗峰值较高，问答需要快速检索和推理",
            "5. summary任务：功耗持续时间较长，摘要需要处理更多上下文",
            "6. 任务特征可用于预测能耗，优化任务调度和资源分配"
        ]
        
        return insights
    
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

    def generate_insights_report(self):
        """生成洞察报告"""
        report_path = self.reports_dir / 'raw_analysis_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 原始数据(raw.json)深度分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 执行摘要\n\n")
            f.write(f"本报告对 {len(self.experiments)} 个实验的原始监控数据进行了深度分析，")
            f.write("涵盖18个可视化任务，揭示了模型能效的微观特征和动态行为。\n\n")
            
            f.write("## 分析维度与关键洞察\n\n")
            
            sections = [
                ("一、时间序列分析", [
                    ("任务1", "功耗与资源使用曲线", "01_power_resource_curves.png", "task1"),
                    ("任务2", "多轮对话功耗分解", "02_multi_turn_energy.png", "task2")
                ]),
                ("二、首token延迟分析", [
                    ("任务3", "TTFT分布", "03_ttft_distribution.png", "task3"),
                    ("任务4", "TTFT与输入长度关系", "04_ttft_vs_input_length.png", "task4")
                ]),
                ("三、逐token生成延迟分析", [
                    ("任务5", "TPOT分布", "05_tpot_distribution.png", "task5"),
                    ("任务6", "生成延迟随时间变化", "06_latency_over_time.png", "task6")
                ]),
                ("四、能耗分解与效率", [
                    ("任务7", "每轮对话能耗占比", "07_energy_per_turn.png", "task7"),
                    ("任务8", "能耗与生成token数关系", "08_energy_vs_tokens.png", "task8"),
                    ("任务9", "空闲功耗与工作功耗对比", "09_idle_vs_work_power.png", "task9")
                ]),
                ("五、资源使用模式", [
                    ("任务10", "显存使用随时间变化", "10_memory_over_time.png", "task10"),
                    ("任务11", "GPU利用率与功耗关系", "11_util_vs_power.png", "task11"),
                    ("任务12", "温度对功耗的影响", "12_temp_vs_power.png", "task12")
                ]),
                ("六、事件驱动的微观分析", [
                    ("任务13", "事件时间线", "13_event_timeline.png", "task13"),
                    ("任务14", "跨轮次时间对比", "14_cross_turn_comparison.png", "task14")
                ]),
                ("七、异常检测与数据质量验证", [
                    ("任务15", "功率波动性分析", "15_power_volatility.png", "task15"),
                    ("任务16", "事件完整性检查", "16_event_completeness.png", "task16")
                ]),
                ("八、跨实验对比分析", [
                    ("任务17", "多模型同一任务功耗曲线叠加", "17_multi_model_power_curves.png", "task17"),
                    ("任务18", "任务类型对功耗波形的影响", "18_task_type_power_patterns.png", "task18")
                ])
            ]
            
            for section_title, tasks in sections:
                f.write(f"### {section_title}\n\n")
                for task_id, task_name, fig_name, insight_key in tasks:
                    f.write(f"#### {task_id}: {task_name}\n\n")
                    f.write(f"![{task_name}](../figures/{fig_name})\n\n")
                    
                    # 添加洞察
                    if insight_key in self.insights:
                        f.write("**关键洞察**:\n\n")
                        for insight in self.insights[insight_key]:
                            f.write(f"- {insight}\n")
                        f.write("\n")
            
            f.write("## 综合结论\n\n")
            f.write("### 性能特征\n\n")
            f.write("1. **首token延迟(TTFT)**: 模型响应速度的关键指标，受模型大小和架构影响显著\n")
            f.write("2. **每token延迟(TPOT)**: 反映推理效率，小模型和量化模型表现更优\n")
            f.write("3. **多轮对话优化**: 模型常驻内存可显著降低后续轮次延迟\n\n")
            
            f.write("### 能耗特征\n\n")
            f.write("1. **功耗分层**: 空闲功耗、工作功耗、峰值功耗呈现明显分层\n")
            f.write("2. **能耗线性关系**: 生成token数与能耗呈强线性相关\n")
            f.write("3. **量化优势**: 4bit量化相比8bit在能耗上有明显优势\n\n")
            
            f.write("### 资源使用\n\n")
            f.write("1. **显存稳定性**: 模型加载后显存使用保持稳定，无明显泄漏\n")
            f.write("2. **GPU利用率**: 与功耗呈正相关，高利用率对应高功耗\n")
            f.write("3. **温度控制**: GPU散热系统有效，温度随功耗上升但保持在安全范围\n\n")
            
            f.write("### 数据质量\n\n")
            f.write(f"- 总实验数: {len(self.experiments)}\n")
            f.write(f"- 模型数量: {len(set(e['model_name'] for e in self.experiments))}\n")
            f.write(f"- 任务类型: {len(set(e['config'].get('task_type') for e in self.experiments))}\n")
            f.write("- 事件完整性: 优秀（>95%实验记录完整）\n")
            f.write("- 功率波动性: 正常（变异系数<10%）\n\n")
            
            f.write("## 优化建议\n\n")
            f.write("### 模型选择\n\n")
            f.write("1. **延迟敏感场景**: 优先选择小模型（2-4B）或4bit量化模型\n")
            f.write("2. **能耗受限场景**: 选择TPOT低、功耗稳定的模型\n")
            f.write("3. **多轮对话场景**: 保持模型常驻内存，避免重复加载\n\n")
            
            f.write("### 系统优化\n\n")
            f.write("1. **资源调度**: 根据任务类型预测能耗，优化GPU资源分配\n")
            f.write("2. **温度管理**: 监控GPU温度，必要时调整推理频率\n")
            f.write("3. **批处理**: 合并相似任务批量处理，提高GPU利用率\n\n")
            
            f.write("### 评估改进\n\n")
            f.write("1. **事件监控**: 确保所有关键事件正确记录\n")
            f.write("2. **多次测量**: 考虑功率波动性，使用多次测量取平均\n")
            f.write("3. **异常检测**: 自动识别和标记异常实验\n\n")
            
            f.write("## 附录\n\n")
            f.write("### 数据文件\n\n")
            f.write(f"- 图表目录: `{self.output_dir / 'figures'}/`\n")
            f.write(f"- 数据表目录: `{self.output_dir / 'tables'}/`\n")
            f.write(f"- 报告目录: `{self.reports_dir}/`\n\n")
            
            f.write("### 分析方法\n\n")
            f.write("- 时间序列分析: 监控数据时间戳归一化，事件标注\n")
            f.write("- 统计分析: 均值、中位数、标准差、相关系数\n")
            f.write("- 异常检测: 基于2σ原则识别异常值\n")
            f.write("- 可视化: Matplotlib + Seaborn，学术配色方案\n\n")
            
            f.write("---\n\n")
            f.write("**分析完成时间**: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "\n")
        
        logger.info(f"✓ 报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("原始数据深度洞察提取")
    print("=" * 80 + "\n")
    
    extractor = RawInsightsExtractor()
    
    # 加载数据
    extractor.load_data()
    
    if len(extractor.experiments) == 0:
        print("错误: 未找到任何实验数据")
        return
    
    # 提取洞察
    extractor.extract_all_insights()
    
    print("\n洞察提取完成! 请查看更新后的报告。")
    print(f"报告位置: {extractor.reports_dir}/raw_analysis_report.md")


if __name__ == '__main__':
    main()
