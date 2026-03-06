"""
计算派生指标
从基础指标表格中计算派生指标，如token速度、能效比等
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
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
        logging.FileHandler(log_dir / 'derived_metrics.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DerivedMetricsCalculator:
    """派生指标计算器"""
    
    def __init__(self, input_dir: str = 'analysis/qe_research/results/metric_tables'):
        self.input_dir = Path(input_dir)
        self.output_dir = Path('analysis/qe_research/results/derived_metrics')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载基础指标表格
        self.tables = {}
        logger.info("派生指标计算器初始化完成")
    
    def load_tables(self):
        """加载所有基础指标表格"""
        logger.info("加载基础指标表格...")
        
        table_files = {
            'energy': '01_avg_gpu_energy.csv',
            'tokens': '02_avg_output_tokens.csv',
            'ttft': '03_ttft.csv',
            'time': '04_avg_response_time.csv',
            'memory': '05_avg_gpu_memory.csv',
            'utilization': '06_avg_gpu_utilization.csv'
        }
        
        for key, filename in table_files.items():
            filepath = self.input_dir / filename
            if filepath.exists():
                self.tables[key] = pd.read_csv(filepath, index_col=0)
                logger.info(f"  ✓ {filename}: {self.tables[key].shape}")
            else:
                logger.warning(f"  ✗ {filename}: 文件不存在")
        
        logger.info(f"成功加载 {len(self.tables)} 个表格")
    
    def compute_token_speed(self) -> pd.DataFrame:
        """
        计算平均token速度 (tokens/s)
        公式: tokens / time
        """
        logger.info("计算平均token速度...")
        
        tokens = self.tables['tokens']
        time = self.tables['time']
        
        # 计算速度
        speed = tokens / time
        
        # 保存
        output_path = self.output_dir / '07_avg_token_speed.csv'
        speed.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 07_avg_token_speed.csv")
        
        return speed
    
    def compute_energy_per_token(self) -> pd.DataFrame:
        """
        计算每token能耗 (J/token)
        公式: energy / tokens
        """
        logger.info("计算每token能耗...")
        
        energy = self.tables['energy']
        tokens = self.tables['tokens']
        
        # 计算每token能耗
        energy_per_token = energy / tokens
        
        # 保存
        output_path = self.output_dir / '08_energy_per_token.csv'
        energy_per_token.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 08_energy_per_token.csv")
        
        return energy_per_token
    
    def compute_power_consumption(self) -> pd.DataFrame:
        """
        计算平均功率 (W)
        公式: energy / time
        """
        logger.info("计算平均功率...")
        
        energy = self.tables['energy']
        time = self.tables['time']
        
        # 计算功率
        power = energy / time
        
        # 保存
        output_path = self.output_dir / '09_avg_power.csv'
        power.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 09_avg_power.csv")
        
        return power
    
    def compute_memory_efficiency(self) -> pd.DataFrame:
        """
        计算显存效率 (tokens/MB)
        公式: tokens / memory
        """
        logger.info("计算显存效率...")
        
        tokens = self.tables['tokens']
        memory = self.tables['memory']
        
        # 计算显存效率
        memory_efficiency = tokens / memory
        
        # 保存
        output_path = self.output_dir / '10_memory_efficiency.csv'
        memory_efficiency.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 10_memory_efficiency.csv")
        
        return memory_efficiency
    
    def compute_throughput_per_watt(self) -> pd.DataFrame:
        """
        计算能效比 (tokens/J)
        公式: tokens / energy
        """
        logger.info("计算能效比...")
        
        tokens = self.tables['tokens']
        energy = self.tables['energy']
        
        # 计算能效比
        throughput_per_watt = tokens / energy
        
        # 保存
        output_path = self.output_dir / '11_throughput_per_joule.csv'
        throughput_per_watt.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 11_throughput_per_joule.csv")
        
        return throughput_per_watt
    
    def compute_time_to_first_token_ratio(self) -> pd.DataFrame:
        """
        计算首token延迟占比 (%)
        公式: (ttft / 1000) / time * 100
        """
        logger.info("计算首token延迟占比...")
        
        ttft = self.tables['ttft']  # ms
        time = self.tables['time']  # s
        
        # 转换ttft为秒，计算占比
        ttft_ratio = (ttft / 1000) / time * 100
        
        # 保存
        output_path = self.output_dir / '12_ttft_ratio.csv'
        ttft_ratio.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 12_ttft_ratio.csv")
        
        return ttft_ratio
    
    def compute_gpu_utilization_efficiency(self) -> pd.DataFrame:
        """
        计算GPU利用效率 (tokens/s per %)
        公式: token_speed / utilization
        """
        logger.info("计算GPU利用效率...")
        
        tokens = self.tables['tokens']
        time = self.tables['time']
        utilization = self.tables['utilization']
        
        # 计算token速度
        token_speed = tokens / time
        
        # 计算GPU利用效率
        gpu_efficiency = token_speed / utilization
        
        # 保存
        output_path = self.output_dir / '13_gpu_utilization_efficiency.csv'
        gpu_efficiency.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 13_gpu_utilization_efficiency.csv")
        
        return gpu_efficiency
    
    def compute_normalized_scores(self) -> pd.DataFrame:
        """
        计算归一化综合得分
        综合考虑速度、能效、显存效率
        """
        logger.info("计算归一化综合得分...")
        
        # 计算各项指标
        token_speed = self.tables['tokens'] / self.tables['time']
        energy_efficiency = self.tables['tokens'] / self.tables['energy']
        memory_efficiency = self.tables['tokens'] / self.tables['memory']
        
        # 按任务归一化（Min-Max）
        def normalize_by_task(df):
            normalized = df.copy()
            for task in df.index:
                row = df.loc[task]
                min_val = row.min()
                max_val = row.max()
                if max_val > min_val:
                    normalized.loc[task] = (row - min_val) / (max_val - min_val)
                else:
                    normalized.loc[task] = 0.5
            return normalized
        
        norm_speed = normalize_by_task(token_speed)
        norm_energy_eff = normalize_by_task(energy_efficiency)
        norm_memory_eff = normalize_by_task(memory_efficiency)
        
        # 综合得分（加权平均）
        weights = {
            'speed': 0.4,
            'energy_efficiency': 0.4,
            'memory_efficiency': 0.2
        }
        
        composite_score = (
            weights['speed'] * norm_speed +
            weights['energy_efficiency'] * norm_energy_eff +
            weights['memory_efficiency'] * norm_memory_eff
        )
        
        # 保存
        output_path = self.output_dir / '14_composite_efficiency_score.csv'
        composite_score.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ 14_composite_efficiency_score.csv")
        
        return composite_score
    
    def compute_all_metrics(self):
        """计算所有派生指标"""
        logger.info("\n" + "=" * 80)
        logger.info("开始计算派生指标")
        logger.info("=" * 80)
        
        # 加载基础表格
        self.load_tables()
        
        # 计算各项派生指标
        metrics = {}
        
        print("\n计算派生指标:")
        
        # 1. Token速度
        metrics['token_speed'] = self.compute_token_speed()
        self._print_metric_summary('平均token速度 (tokens/s)', metrics['token_speed'])
        
        # 2. 每token能耗
        metrics['energy_per_token'] = self.compute_energy_per_token()
        self._print_metric_summary('每token能耗 (J/token)', metrics['energy_per_token'])
        
        # 3. 平均功率
        metrics['power'] = self.compute_power_consumption()
        self._print_metric_summary('平均功率 (W)', metrics['power'])
        
        # 4. 显存效率
        metrics['memory_efficiency'] = self.compute_memory_efficiency()
        self._print_metric_summary('显存效率 (tokens/MB)', metrics['memory_efficiency'])
        
        # 5. 能效比
        metrics['throughput_per_joule'] = self.compute_throughput_per_watt()
        self._print_metric_summary('能效比 (tokens/J)', metrics['throughput_per_joule'])
        
        # 6. TTFT占比
        if 'ttft' in self.tables:
            metrics['ttft_ratio'] = self.compute_time_to_first_token_ratio()
            self._print_metric_summary('首token延迟占比 (%)', metrics['ttft_ratio'])
        
        # 7. GPU利用效率
        metrics['gpu_efficiency'] = self.compute_gpu_utilization_efficiency()
        self._print_metric_summary('GPU利用效率 (tokens/s/%)', metrics['gpu_efficiency'])
        
        # 8. 综合得分
        metrics['composite_score'] = self.compute_normalized_scores()
        self._print_metric_summary('综合效率得分 (0-1)', metrics['composite_score'])
        
        # 生成报告
        self.generate_report(metrics)
        
        logger.info("\n" + "=" * 80)
        logger.info("派生指标计算完成!")
        logger.info(f"输出目录: {self.output_dir}/")
        logger.info("=" * 80)
    
    def _print_metric_summary(self, name: str, df: pd.DataFrame):
        """打印指标摘要"""
        print(f"\n{name}:")
        
        # 找出每个任务的最优模型
        for task in df.index:
            row = df.loc[task].dropna()
            if len(row) > 0:
                # 对于速度、效率类指标，越大越好
                if '速度' in name or '效率' in name or '得分' in name or 'tokens/J' in name or 'tokens/MB' in name:
                    best_model = row.idxmax()
                    best_value = row.max()
                else:  # 对于能耗、功率类指标，越小越好
                    best_model = row.idxmin()
                    best_value = row.min()
                
                print(f"  {task}: {best_model} = {best_value:.2f}")
    
    def generate_report(self, metrics: dict):
        """生成派生指标报告"""
        report_path = self.output_dir / 'DERIVED_METRICS_REPORT.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 派生指标分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 概述\n\n")
            f.write("本报告基于6个基础指标表格，计算了8个派生指标，提供更深入的模型性能分析。\n\n")
            
            f.write("## 派生指标列表\n\n")
            
            f.write("### 1. 平均token速度 (tokens/s)\n\n")
            f.write("**公式**: 输出tokens / 回答时间\n\n")
            f.write("**意义**: 衡量模型的生成速度，越高越好。\n\n")
            f.write("**文件**: `07_avg_token_speed.csv`\n\n")
            
            f.write("### 2. 每token能耗 (J/token)\n\n")
            f.write("**公式**: GPU能耗 / 输出tokens\n\n")
            f.write("**意义**: 衡量生成每个token的能耗成本，越低越好。\n\n")
            f.write("**文件**: `08_energy_per_token.csv`\n\n")
            
            f.write("### 3. 平均功率 (W)\n\n")
            f.write("**公式**: GPU能耗 / 回答时间\n\n")
            f.write("**意义**: 衡量模型运行时的平均功率消耗，越低越好。\n\n")
            f.write("**文件**: `09_avg_power.csv`\n\n")
            
            f.write("### 4. 显存效率 (tokens/MB)\n\n")
            f.write("**公式**: 输出tokens / 显存占用\n\n")
            f.write("**意义**: 衡量显存利用效率，越高越好。\n\n")
            f.write("**文件**: `10_memory_efficiency.csv`\n\n")
            
            f.write("### 5. 能效比 (tokens/J)\n\n")
            f.write("**公式**: 输出tokens / GPU能耗\n\n")
            f.write("**意义**: 衡量能量利用效率，越高越好。这是评估模型可持续性的关键指标。\n\n")
            f.write("**文件**: `11_throughput_per_joule.csv`\n\n")
            
            f.write("### 6. 首token延迟占比 (%)\n\n")
            f.write("**公式**: (TTFT / 1000) / 回答时间 × 100\n\n")
            f.write("**意义**: 衡量首token延迟在总时间中的占比，越低表示生成过程越流畅。\n\n")
            f.write("**文件**: `12_ttft_ratio.csv`\n\n")
            f.write("**注意**: 仅部分Ollama模型有数据。\n\n")
            
            f.write("### 7. GPU利用效率 (tokens/s/%)\n\n")
            f.write("**公式**: token速度 / GPU占用率\n\n")
            f.write("**意义**: 衡量GPU利用的有效性，越高表示GPU资源利用越充分。\n\n")
            f.write("**文件**: `13_gpu_utilization_efficiency.csv`\n\n")
            
            f.write("### 8. 综合效率得分 (0-1)\n\n")
            f.write("**公式**: 0.4×归一化速度 + 0.4×归一化能效 + 0.2×归一化显存效率\n\n")
            f.write("**意义**: 综合评估模型的整体效率，越高越好。\n\n")
            f.write("**文件**: `14_composite_efficiency_score.csv`\n\n")
            
            f.write("## 关键发现\n\n")
            
            # Token速度
            if 'token_speed' in metrics:
                speed = metrics['token_speed']
                f.write("### Token生成速度\n\n")
                for task in speed.index:
                    row = speed.loc[task].dropna()
                    if len(row) > 0:
                        fastest = row.idxmax()
                        slowest = row.idxmin()
                        f.write(f"- **{task}任务**: 最快 {fastest} ({row.max():.1f} tokens/s), ")
                        f.write(f"最慢 {slowest} ({row.min():.1f} tokens/s)\n")
                f.write("\n")
            
            # 能效比
            if 'throughput_per_joule' in metrics:
                tpj = metrics['throughput_per_joule']
                f.write("### 能效比排名\n\n")
                for task in tpj.index:
                    row = tpj.loc[task].dropna()
                    if len(row) > 0:
                        best = row.idxmax()
                        f.write(f"- **{task}任务**: {best} ({row.max():.3f} tokens/J)\n")
                f.write("\n")
            
            # 综合得分
            if 'composite_score' in metrics:
                score = metrics['composite_score']
                f.write("### 综合效率得分 Top 3\n\n")
                
                # 计算每个模型的平均得分
                avg_scores = score.mean().sort_values(ascending=False)
                f.write("**跨任务平均得分**:\n\n")
                for i, (model, value) in enumerate(avg_scores.head(3).items(), 1):
                    f.write(f"{i}. {model}: {value:.3f}\n")
                f.write("\n")
            
            f.write("## 使用建议\n\n")
            f.write("### 场景推荐\n\n")
            f.write("1. **追求速度**: 选择token速度最高的模型\n")
            f.write("2. **追求节能**: 选择能效比最高的模型\n")
            f.write("3. **显存受限**: 选择显存效率最高的模型\n")
            f.write("4. **综合考虑**: 选择综合效率得分最高的模型\n\n")
            
            f.write("## 数据文件\n\n")
            f.write("所有派生指标CSV文件位于: `analysis/qe_research/results/derived_metrics/`\n\n")
            
            f.write("---\n\n")
            f.write("**生成脚本**: `analysis/qe_research/scripts/compute_derived_metrics.py`\n")
        
        logger.info(f"报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("计算派生指标")
    print("=" * 80 + "\n")
    
    calculator = DerivedMetricsCalculator()
    calculator.compute_all_metrics()
    
    print("\n完成!")


if __name__ == '__main__':
    main()
