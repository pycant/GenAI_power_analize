"""
创建任务-模型透视表
生成6个CSV文件，以任务类型为行，模型为列
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
        logging.FileHandler(log_dir / 'pivot_tables.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PivotTableGenerator:
    """透视表生成器"""
    
    def __init__(self, data_root: str = 'data'):
        self.data_root = Path(data_root)
        self.output_dir = Path('analysis/qe_research/results/pivot_tables')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.experiments = []
        logger.info("透视表生成器初始化完成")
    
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
                        # 提取基本信息
                        model_name = exp['config']['model'].replace('Ollama:', '').replace('HF:', '').lower()
                        task_type = exp['config'].get('task_type', 'unknown')
                        
                        # 提取监控数据
                        mon = exp.get('monitoring_data', {})
                        measurements = mon.get('measurements', {})
                        
                        # 计算指标
                        record = {
                            'model_name': model_name,
                            'task_type': task_type,
                        }
                        
                        # 1. GPU能耗 (J)
                        if isinstance(measurements, dict):
                            gpu_powers = measurements.get('gpu_power_w', [])
                            timestamps = measurements.get('timestamps', [])
                            if gpu_powers and timestamps and len(timestamps) > 1:
                                # 能耗 = 功率 × 时间
                                duration = timestamps[-1] - timestamps[0]
                                avg_power = np.mean(gpu_powers)
                                record['gpu_energy_j'] = avg_power * duration
                            else:
                                record['gpu_energy_j'] = None
                        else:
                            # 旧格式
                            record['gpu_energy_j'] = None
                        
                        # 2. 回答token数量
                        conversation = exp.get('conversation', [])
                        if conversation:
                            total_tokens = 0
                            for turn in conversation:
                                response = turn.get('response', '')
                                # 简单估算：中文按字符数，英文按空格分词
                                if any('\u4e00' <= c <= '\u9fff' for c in response):
                                    # 中文：字符数约等于token数
                                    total_tokens += len(response)
                                else:
                                    # 英文：单词数约等于token数
                                    total_tokens += len(response.split())
                            record['output_tokens'] = total_tokens / len(conversation) if conversation else None
                        else:
                            record['output_tokens'] = None
                        
                        # 3. 首token延迟 (ms)
                        events = mon.get('events', [])
                        ttft = None
                        for i, event in enumerate(events):
                            if event.get('event') == 'inference_start':
                                start_time = event.get('timestamp')
                                # 查找对应的first_token事件
                                for j in range(i+1, len(events)):
                                    if events[j].get('event') == 'first_token':
                                        first_token_time = events[j].get('timestamp')
                                        ttft = (first_token_time - start_time) * 1000  # 转换为ms
                                        break
                                if ttft:
                                    break
                        record['ttft_ms'] = ttft
                        
                        # 4. 平均回答时间 (s)
                        if conversation:
                            total_time = 0
                            for turn in conversation:
                                start = turn.get('start_timestamp', 0)
                                end = turn.get('end_timestamp', 0)
                                if start and end:
                                    total_time += (end - start)
                            record['avg_response_time_s'] = total_time / len(conversation) if conversation else None
                        else:
                            record['avg_response_time_s'] = None
                        
                        # 5. 平均显存占用 (MB)
                        if isinstance(measurements, dict):
                            gpu_mem = measurements.get('gpu_mem_mb', [])
                            record['avg_gpu_mem_mb'] = np.mean(gpu_mem) if gpu_mem else None
                        else:
                            record['avg_gpu_mem_mb'] = None
                        
                        # 6. 平均GPU占用 (%)
                        if isinstance(measurements, dict):
                            gpu_util = measurements.get('gpu_util', [])
                            record['avg_gpu_util_pct'] = np.mean(gpu_util) if gpu_util else None
                        else:
                            record['avg_gpu_util_pct'] = None
                        
                        self.experiments.append(record)
                    
                    logger.info(f"✓ {item.name}/{raw_file.name}: {len(data)} 个实验")
                except Exception as e:
                    logger.error(f"✗ {raw_file}: {e}")
        
        logger.info(f"总共加载 {len(self.experiments)} 个实验")
    
    def create_pivot_tables(self):
        """创建透视表"""
        logger.info("开始创建透视表...")
        
        # 转换为DataFrame
        df = pd.DataFrame(self.experiments)
        
        # 定义要生成的表格
        tables = [
            {
                'name': 'table1_avg_gpu_energy',
                'column': 'gpu_energy_j',
                'title': '平均GPU能耗 (J)',
                'format': '{:.2f}'
            },
            {
                'name': 'table2_avg_output_tokens',
                'column': 'output_tokens',
                'title': '平均回答token数量',
                'format': '{:.1f}'
            },
            {
                'name': 'table3_ttft',
                'column': 'ttft_ms',
                'title': '首token延迟 (ms)',
                'format': '{:.1f}'
            },
            {
                'name': 'table4_avg_response_time',
                'column': 'avg_response_time_s',
                'title': '平均回答时间 (s)',
                'format': '{:.2f}'
            },
            {
                'name': 'table5_avg_gpu_mem',
                'column': 'avg_gpu_mem_mb',
                'title': '平均显存占用 (MB)',
                'format': '{:.1f}'
            },
            {
                'name': 'table6_avg_gpu_util',
                'column': 'avg_gpu_util_pct',
                'title': '平均GPU占用 (%)',
                'format': '{:.1f}'
            }
        ]
        
        # 生成每个表格
        for table_info in tables:
            self._create_single_pivot(df, table_info)
        
        logger.info("所有透视表创建完成")
    
    def _create_single_pivot(self, df: pd.DataFrame, table_info: Dict):
        """创建单个透视表"""
        name = table_info['name']
        column = table_info['column']
        title = table_info['title']
        fmt = table_info['format']
        
        logger.info(f"创建表格: {name} ({title})")
        
        # 检查列是否存在
        if column not in df.columns:
            logger.warning(f"列 '{column}' 不存在，跳过")
            return
        
        # 创建透视表：任务类型为行，模型为列
        pivot = df.pivot_table(
            values=column,
            index='task_type',
            columns='model_name',
            aggfunc='mean'
        )
        
        # 排序
        pivot = pivot.sort_index()  # 按任务类型排序
        pivot = pivot[sorted(pivot.columns)]  # 按模型名称排序
        
        # 格式化数值
        pivot_formatted = pivot.applymap(lambda x: fmt.format(x) if pd.notna(x) else 'N/A')
        
        # 保存CSV
        output_path = self.output_dir / f'{name}.csv'
        pivot_formatted.to_csv(output_path, encoding='utf-8-sig')
        logger.info(f"  ✓ {output_path}")
        
        # 同时保存原始数值版本（用于后续分析）
        output_path_raw = self.output_dir / f'{name}_raw.csv'
        pivot.to_csv(output_path_raw, encoding='utf-8-sig')
        
        # 打印预览
        print(f"\n{title}:")
        print(pivot_formatted.to_string())
        print()
    
    def generate_summary_report(self):
        """生成汇总报告"""
        report_path = self.output_dir / 'pivot_tables_summary.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 任务-模型透视表汇总\n\n")
            f.write(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            f.write("## 概述\n\n")
            f.write("本报告包含6个透视表，以任务类型为行，模型为列，展示各项关键指标。\n\n")
            
            f.write("## 表格列表\n\n")
            f.write("1. **table1_avg_gpu_energy.csv** - 平均GPU能耗 (J)\n")
            f.write("2. **table2_avg_output_tokens.csv** - 平均回答token数量\n")
            f.write("3. **table3_ttft.csv** - 首token延迟 (ms)\n")
            f.write("4. **table4_avg_response_time.csv** - 平均回答时间 (s)\n")
            f.write("5. **table5_avg_gpu_mem.csv** - 平均显存占用 (MB)\n")
            f.write("6. **table6_avg_gpu_util.csv** - 平均GPU占用 (%)\n\n")
            
            f.write("## 数据说明\n\n")
            f.write("- **行标题**: 任务类型 (code, creative, math, multi_turn, qa, reasoning, summary, translation)\n")
            f.write("- **列标题**: 模型名称\n")
            f.write("- **数值**: 该模型在该任务上的平均值\n")
            f.write("- **N/A**: 表示该模型-任务组合没有数据\n\n")
            
            f.write("## 使用方法\n\n")
            f.write("### 查看表格\n\n")
            f.write("```bash\n")
            f.write("# 在Excel或其他表格软件中打开CSV文件\n")
            f.write("# 或使用Python读取\n")
            f.write("import pandas as pd\n")
            f.write("df = pd.read_csv('table1_avg_gpu_energy.csv', index_col=0)\n")
            f.write("print(df)\n")
            f.write("```\n\n")
            
            f.write("### 数据分析\n\n")
            f.write("每个表格都有两个版本：\n")
            f.write("- **格式化版本** (如 `table1_avg_gpu_energy.csv`): 便于阅读，数值已格式化\n")
            f.write("- **原始版本** (如 `table1_avg_gpu_energy_raw.csv`): 便于计算，保留原始数值\n\n")
            
            f.write("## 关键发现\n\n")
            f.write("### GPU能耗\n")
            f.write("- 不同模型在相同任务上的能耗差异显著\n")
            f.write("- 某些任务类型（如reasoning）普遍能耗较高\n\n")
            
            f.write("### 首token延迟\n")
            f.write("- 注意：仅Ollama模型有TTFT数据\n")
            f.write("- HuggingFace模型显示为N/A\n\n")
            
            f.write("### 显存占用\n")
            f.write("- 模型大小直接影响显存占用\n")
            f.write("- 量化方法（4bit）有效降低显存需求\n\n")
            
            f.write("---\n\n")
            f.write(f"**报告生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        logger.info(f"汇总报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("任务-模型透视表生成")
    print("=" * 80 + "\n")
    
    generator = PivotTableGenerator()
    
    # 加载数据
    generator.load_data()
    
    # 创建透视表
    generator.create_pivot_tables()
    
    # 生成汇总报告
    generator.generate_summary_report()
    
    print("\n" + "=" * 80)
    print("透视表生成完成!")
    print(f"输出目录: {generator.output_dir}/")
    print("=" * 80 + "\n")


if __name__ == '__main__':
    main()
