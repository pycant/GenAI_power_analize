"""
创建指标对比表格
生成6个CSV文件，以任务类型为行、模型为列的矩阵表格
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import pandas as pd
import numpy as np
import logging
from typing import Dict, List
import warnings
warnings.filterwarnings('ignore')

# 配置日志
log_dir = Path('analysis/qe_research/logs')
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'create_metric_tables.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MetricTableCreator:
    """指标表格创建器"""
    
    def __init__(self, data_root: str = 'data'):
        self.data_root = Path(data_root)
        self.output_dir = Path('analysis/qe_research/results/metric_tables')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.experiments = []
        logger.info("指标表格创建器初始化完成")
    
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
            
            # 查找summary.json文件（优先）和raw.json文件
            summary_files = list(item.glob('*_summary.json'))
            raw_files = list(item.glob('*_raw.json'))
            
            # 优先使用summary文件
            files_to_process = summary_files if summary_files else raw_files
            
            for data_file in files_to_process:
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    for exp in data:
                        # 提取模型名称 - 兼容config和config_ref
                        config = exp.get('config') or exp.get('config_ref', {})
                        model_name = config.get('model', 'unknown').replace('Ollama:', '').replace('HF:', '').lower()
                        exp['model_name'] = model_name
                        exp['model_dir'] = item.name
                        
                        # 提取任务类型
                        exp['task_type'] = config.get('task_type', 'unknown')
                        
                        self.experiments.append(exp)
                    
                    logger.info(f"✓ {item.name}/{data_file.name}: {len(data)} 个实验")
                except Exception as e:
                    logger.error(f"✗ {data_file}: {e}")
        
        logger.info(f"总共加载 {len(self.experiments)} 个实验")
    
    def extract_metrics(self) -> pd.DataFrame:
        """从实验数据中提取所有指标"""
        logger.info("提取指标数据...")
        
        records = []
        
        for exp in self.experiments:
            model = exp['model_name']
            task = exp.get('task_type', 'unknown')
            
            # 初始化记录
            record = {
                'model': model,
                'task': task,
                'gpu_energy_j': None,
                'output_tokens': None,
                'ttft_ms': None,
                'response_time_s': None,
                'gpu_mem_avg_mb': None,
                'gpu_util_avg': None
            }
            
            # 1. GPU能耗 (J)
            if 'resources' in exp and 'gpu_energy_j' in exp['resources']:
                record['gpu_energy_j'] = exp['resources']['gpu_energy_j']
            elif 'monitoring_data' in exp:
                mon = exp['monitoring_data']
                if 'gpu_energy_j' in mon:
                    record['gpu_energy_j'] = mon['gpu_energy_j']
            
            # 2. 输出token数量
            if 'performance' in exp:
                perf = exp['performance']
                if 'output_tokens' in perf:
                    record['output_tokens'] = perf['output_tokens']
                elif 'token_count' in perf:
                    record['output_tokens'] = perf['token_count']
            elif 'conversation' in exp:
                # 从对话中统计token数
                total_tokens = 0
                for turn in exp['conversation']:
                    if 'tokens' in turn:
                        total_tokens += turn['tokens']
                    elif 'response' in turn:
                        # 粗略估计：按字符数/4
                        total_tokens += len(turn['response']) / 4
                if total_tokens > 0:
                    record['output_tokens'] = total_tokens
            
            # 3. 首token延迟 (ms)
            if 'performance' in exp and 'ttft_seconds' in exp['performance']:
                ttft = exp['performance']['ttft_seconds']
                if ttft is not None:
                    record['ttft_ms'] = ttft * 1000
            elif 'monitoring_data' in exp and 'events' in exp['monitoring_data']:
                # 从事件中计算TTFT
                events = exp['monitoring_data']['events']
                inference_start = None
                first_token = None
                
                for event in events:
                    if event.get('event') == 'inference_start' and event.get('metadata', {}).get('turn') == 1:
                        inference_start = event.get('timestamp')
                    elif event.get('event') == 'first_token' and event.get('metadata', {}).get('turn') == 1:
                        first_token = event.get('timestamp')
                        break
                
                if inference_start and first_token:
                    record['ttft_ms'] = (first_token - inference_start) * 1000
            
            # 4. 平均回答时间 (s)
            if 'performance' in exp:
                perf = exp['performance']
                if 'avg_time_per_turn' in perf:
                    record['response_time_s'] = perf['avg_time_per_turn']
                elif 'total_time_seconds' in perf and 'turns' in perf and perf['turns'] > 0:
                    record['response_time_s'] = perf['total_time_seconds'] / perf['turns']
            elif 'conversation' in exp:
                # 从对话中计算平均时间
                times = []
                for turn in exp['conversation']:
                    if 'duration_seconds' in turn:
                        times.append(turn['duration_seconds'])
                    elif 'start_timestamp' in turn and 'end_timestamp' in turn:
                        times.append(turn['end_timestamp'] - turn['start_timestamp'])
                if times:
                    record['response_time_s'] = np.mean(times)
            
            # 5. 平均显存占用 (MB)
            if 'resources' in exp and 'gpu_mem_avg_mb' in exp['resources']:
                record['gpu_mem_avg_mb'] = exp['resources']['gpu_mem_avg_mb']
            elif 'monitoring_data' in exp:
                mon = exp['monitoring_data']
                measurements = mon.get('measurements', {})
                
                if isinstance(measurements, dict) and 'gpu_mem_mb' in measurements:
                    gpu_mem_list = measurements['gpu_mem_mb']
                    if gpu_mem_list:
                        record['gpu_mem_avg_mb'] = np.mean(gpu_mem_list)
                elif isinstance(measurements, list):
                    gpu_mems = [m.get('gpu_mem_mb', 0) for m in measurements if 'gpu_mem_mb' in m]
                    if gpu_mems:
                        record['gpu_mem_avg_mb'] = np.mean(gpu_mems)
            
            # 6. 平均GPU占用 (%)
            if 'resources' in exp and 'gpu_util_avg' in exp['resources']:
                record['gpu_util_avg'] = exp['resources']['gpu_util_avg']
            elif 'monitoring_data' in exp:
                mon = exp['monitoring_data']
                measurements = mon.get('measurements', {})
                
                if isinstance(measurements, dict) and 'gpu_util' in measurements:
                    gpu_util_list = measurements['gpu_util']
                    if gpu_util_list:
                        record['gpu_util_avg'] = np.mean(gpu_util_list)
                elif isinstance(measurements, list):
                    gpu_utils = [m.get('gpu_util', 0) for m in measurements if 'gpu_util' in m]
                    if gpu_utils:
                        record['gpu_util_avg'] = np.mean(gpu_utils)
            
            records.append(record)
        
        df = pd.DataFrame(records)
        logger.info(f"提取完成: {len(df)} 条记录")
        
        return df
    
    def create_pivot_table(self, df: pd.DataFrame, metric: str, 
                          metric_name: str, unit: str = '') -> pd.DataFrame:
        """创建透视表"""
        logger.info(f"创建 {metric_name} 透视表...")
        
        # 按任务和模型分组，计算平均值
        pivot = df.pivot_table(
            values=metric,
            index='task',
            columns='model',
            aggfunc='mean'
        )
        
        # 排序
        pivot = pivot.sort_index()  # 按任务排序
        pivot = pivot[sorted(pivot.columns)]  # 按模型排序
        
        # 格式化数值
        if unit == 'J':
            pivot = pivot.round(2)
        elif unit == 'tokens':
            pivot = pivot.round(0)
        elif unit == 'ms':
            pivot = pivot.round(1)
        elif unit == 's':
            pivot = pivot.round(2)
        elif unit == 'MB':
            pivot = pivot.round(1)
        elif unit == '%':
            pivot = pivot.round(1)
        
        # 添加行列标签
        pivot.index.name = '任务类型 \\ 模型'
        
        return pivot
    
    def save_tables(self):
        """生成并保存所有表格"""
        logger.info("\n" + "=" * 80)
        logger.info("开始生成指标表格")
        logger.info("=" * 80)
        
        # 提取指标
        df = self.extract_metrics()
        
        # 统计数据覆盖情况
        logger.info("\n数据覆盖情况:")
        for metric in ['gpu_energy_j', 'output_tokens', 'ttft_ms', 
                      'response_time_s', 'gpu_mem_avg_mb', 'gpu_util_avg']:
            non_null = df[metric].notna().sum()
            total = len(df)
            logger.info(f"  {metric}: {non_null}/{total} ({non_null/total*100:.1f}%)")
        
        # 定义表格配置
        tables = [
            {
                'metric': 'gpu_energy_j',
                'name': '平均GPU能耗',
                'unit': 'J',
                'filename': '01_avg_gpu_energy.csv'
            },
            {
                'metric': 'output_tokens',
                'name': '平均回答token数量',
                'unit': 'tokens',
                'filename': '02_avg_output_tokens.csv'
            },
            {
                'metric': 'ttft_ms',
                'name': '首token延迟',
                'unit': 'ms',
                'filename': '03_ttft.csv'
            },
            {
                'metric': 'response_time_s',
                'name': '平均回答时间',
                'unit': 's',
                'filename': '04_avg_response_time.csv'
            },
            {
                'metric': 'gpu_mem_avg_mb',
                'name': '平均显存占用',
                'unit': 'MB',
                'filename': '05_avg_gpu_memory.csv'
            },
            {
                'metric': 'gpu_util_avg',
                'name': '平均GPU占用',
                'unit': '%',
                'filename': '06_avg_gpu_utilization.csv'
            }
        ]
        
        # 生成每个表格
        logger.info("\n生成表格:")
        for table_config in tables:
            try:
                pivot = self.create_pivot_table(
                    df,
                    table_config['metric'],
                    table_config['name'],
                    table_config['unit']
                )
                
                # 保存CSV
                output_path = self.output_dir / table_config['filename']
                pivot.to_csv(output_path, encoding='utf-8-sig')
                
                logger.info(f"  ✓ {table_config['filename']}: {pivot.shape[0]} 任务 × {pivot.shape[1]} 模型")
                
                # 打印预览
                print(f"\n{table_config['name']} ({table_config['unit']}):")
                print(pivot.to_string())
                print()
                
            except Exception as e:
                logger.error(f"  ✗ {table_config['filename']}: {e}")
                import traceback
                traceback.print_exc()
        
        logger.info("\n" + "=" * 80)
        logger.info("表格生成完成!")
        logger.info(f"输出目录: {self.output_dir}/")
        logger.info("=" * 80)
    
    def generate_summary_report(self):
        """生成汇总报告"""
        report_path = self.output_dir / 'README.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 模型性能指标对比表格\n\n")
            f.write("**生成时间**: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            f.write("---\n\n")
            
            f.write("## 表格说明\n\n")
            f.write("本目录包含6个CSV表格，以任务类型为行、模型名称为列的矩阵格式展示各项性能指标。\n\n")
            
            f.write("### 表格列表\n\n")
            f.write("1. **01_avg_gpu_energy.csv** - 平均GPU能耗 (焦耳)\n")
            f.write("2. **02_avg_output_tokens.csv** - 平均回答token数量\n")
            f.write("3. **03_ttft.csv** - 首token延迟 (毫秒)\n")
            f.write("4. **04_avg_response_time.csv** - 平均回答时间 (秒)\n")
            f.write("5. **05_avg_gpu_memory.csv** - 平均显存占用 (MB)\n")
            f.write("6. **06_avg_gpu_utilization.csv** - 平均GPU占用率 (%)\n\n")
            
            f.write("### 数据来源\n\n")
            f.write("- 数据源: `data/*/experiment_results_*_summary.json` 和 `*_raw.json`\n")
            f.write(f"- 实验总数: {len(self.experiments)}\n")
            f.write(f"- 模型数量: {len(set(exp['model_name'] for exp in self.experiments))}\n")
            f.write(f"- 任务类型: {len(set(exp['task_type'] for exp in self.experiments))}\n\n")
            
            f.write("### 使用方法\n\n")
            f.write("```python\n")
            f.write("import pandas as pd\n\n")
            f.write("# 读取表格\n")
            f.write("df = pd.read_csv('01_avg_gpu_energy.csv', index_col=0)\n\n")
            f.write("# 查看特定任务的能耗\n")
            f.write("print(df.loc['code'])\n\n")
            f.write("# 查看特定模型的能耗\n")
            f.write("print(df['qwen3:8b'])\n")
            f.write("```\n\n")
            
            f.write("### 注意事项\n\n")
            f.write("- 表格中的NaN值表示该模型-任务组合没有数据\n")
            f.write("- 首token延迟(TTFT)仅在部分Ollama模型中可用\n")
            f.write("- 所有数值均为该模型-任务组合下多次实验的平均值\n\n")
            
            f.write("---\n\n")
            f.write("**生成脚本**: `analysis/qe_research/scripts/create_metric_tables.py`\n")
        
        logger.info(f"汇总报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("创建模型性能指标对比表格")
    print("=" * 80 + "\n")
    
    creator = MetricTableCreator()
    
    # 加载数据
    creator.load_data()
    
    # 生成表格
    creator.save_tables()
    
    # 生成报告
    creator.generate_summary_report()
    
    print("\n完成!")


if __name__ == '__main__':
    main()
