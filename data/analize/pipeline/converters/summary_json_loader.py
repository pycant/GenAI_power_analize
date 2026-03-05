"""
Summary JSON数据加载器 - 加载实验summary.json文件
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SummaryJsonLoader:
    """加载和解析summary实验JSON数据"""
    
    def __init__(self, data_root: str = 'data'):
        """
        初始化加载器
        
        Args:
            data_root: 数据根目录
        """
        self.data_root = Path(data_root)
        
        # 模型目录模式
        self.model_dirs = [
            'deepseek_8b_ol_q4km',
            'gemma_2b_hf_4bit',
            'gemma_2b_hf_8bit',
            'gemma_4b_ol_q4km',
            'phi3_4b_hf_4bit',
            'phi3_4b_hf_8bit',
            'qwen_4b_ol_q4km',
            'qwen_8b_ol_q4km',
            'qwen25_3b_hf_4bit',
            'qwen25_3b_hf_8bit',
            'qwen25_7b_hf_4bit',
            'qwen25_7b_hf_8bit',
        ]
    
    def load_all_summary_data(self) -> pd.DataFrame:
        """
        加载所有模型目录下的summary.json文件
        
        Returns:
            合并后的DataFrame
        """
        all_data = []
        
        for model_dir in self.model_dirs:
            dir_path = self.data_root / model_dir
            
            if not dir_path.exists():
                logger.warning(f"目录不存在: {dir_path}")
                continue
            
            # 查找所有summary.json文件
            summary_files = list(dir_path.glob('*_summary.json'))
            
            if not summary_files:
                logger.warning(f"未找到summary.json文件: {dir_path}")
                continue
            
            for summary_file in summary_files:
                logger.info(f"加载: {summary_file}")
                try:
                    df = self.load_summary_json(summary_file, model_dir)
                    all_data.append(df)
                except Exception as e:
                    logger.error(f"加载失败 {summary_file}: {e}")
        
        if not all_data:
            raise ValueError("未找到任何有效的summary.json数据")
        
        # 合并所有数据
        combined = pd.concat(all_data, ignore_index=True)
        logger.info(f"总共加载 {len(combined)} 条记录")
        
        return combined
    
    def load_summary_json(self, file_path: Path, model_dir: str) -> pd.DataFrame:
        """
        加载单个summary.json文件
        
        Args:
            file_path: JSON文件路径
            model_dir: 模型目录名
            
        Returns:
            DataFrame
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        records = []
        
        for experiment in data:
            record = self._parse_summary(experiment, model_dir)
            if record:
                records.append(record)
        
        return pd.DataFrame(records)
    
    def _parse_summary(self, summary: Dict[str, Any], model_dir: str) -> Dict[str, Any]:
        """
        解析单个summary记录
        
        Args:
            summary: summary数据字典
            model_dir: 模型目录名
            
        Returns:
            解析后的记录字典
        """
        try:
            # 基础信息
            record = {
                'experiment_id': summary.get('experiment_id'),
                'model_dir': model_dir,
            }
            
            # 配置信息
            config_ref = summary.get('config_ref', {})
            record['model_name'] = self._extract_model_name(config_ref.get('model', model_dir))
            record['task_type'] = config_ref.get('task_type', 'unknown')
            record['prompts_count'] = config_ref.get('prompts_count', 1)
            record['keep_context'] = config_ref.get('keep_context', False)
            
            # 性能指标
            performance = summary.get('performance', {})
            record['total_time_s'] = performance.get('total_time_seconds')
            record['token_count'] = performance.get('token_count')
            record['output_tokens'] = performance.get('output_tokens')
            record['toks_per_s'] = performance.get('throughput_tokens_per_sec')
            record['latency_per_token_ms'] = performance.get('latency_per_token_ms')
            record['turns'] = performance.get('turns', 1)
            record['avg_time_per_turn'] = performance.get('avg_time_per_turn')
            record['ttft_s'] = performance.get('ttft_seconds')  # Time to first token
            
            # 资源使用
            resources = summary.get('resources', {})
            
            # CPU
            record['cpu_usage_avg'] = resources.get('cpu_percent_avg')
            record['cpu_usage_peak'] = resources.get('cpu_percent_peak')
            record['cpu_usage_std'] = resources.get('cpu_percent_std')
            record['cpu_energy_j'] = resources.get('cpu_energy_j_approx')
            
            # 内存
            record['memory_used_avg_mb'] = resources.get('mem_used_avg_mb')
            record['memory_used_peak_mb'] = resources.get('mem_used_peak_mb')
            
            # GPU
            record['gpu_util_avg'] = resources.get('gpu_util_avg')
            record['gpu_util_peak'] = resources.get('gpu_util_peak')
            record['gpu_util_std'] = resources.get('gpu_util_std')
            record['gpu_memory_avg_mb'] = resources.get('gpu_mem_avg_mb')
            record['gpu_memory_peak_mb'] = resources.get('gpu_mem_peak_mb')
            record['gpu_power_avg_w'] = resources.get('gpu_power_avg_w')
            record['gpu_power_peak_w'] = resources.get('gpu_power_peak_w')
            record['gpu_power_std_w'] = resources.get('gpu_power_std_w')
            record['gpu_energy_j'] = resources.get('gpu_energy_j')
            record['gpu_temp_avg_c'] = resources.get('gpu_temp_avg_c')
            record['gpu_temp_peak_c'] = resources.get('gpu_temp_peak_c')
            
            # 质量指标
            quality = summary.get('quality', {})
            record['bartscore'] = quality.get('bartscore')
            record['generated_text_length'] = quality.get('generated_text_length')
            record['has_reference'] = quality.get('has_reference', False)
            record['avg_response_length'] = quality.get('avg_response_length')
            
            # 计算延迟（秒）
            if record.get('total_time_s'):
                record['latency_s'] = record['total_time_s']
            elif record.get('avg_time_per_turn'):
                record['latency_s'] = record['avg_time_per_turn']
            
            return record
            
        except Exception as e:
            logger.error(f"解析summary记录失败: {e}")
            return None
    
    def _extract_model_name(self, model_str: str) -> str:
        """
        从模型字符串中提取标准化的模型名称
        
        Args:
            model_str: 模型字符串，如 "Ollama:deepseek-r1:8b"
            
        Returns:
            标准化的模型名称
        """
        # 移除前缀
        model_str = model_str.replace('Ollama:', '').replace('HF:', '')
        
        # 标准化名称
        model_str = model_str.lower().strip()
        
        return model_str
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型目录列表"""
        available = []
        for model_dir in self.model_dirs:
            dir_path = self.data_root / model_dir
            if dir_path.exists():
                summary_files = list(dir_path.glob('*_summary.json'))
                if summary_files:
                    available.append(model_dir)
        return available


if __name__ == '__main__':
    # 测试加载器
    logging.basicConfig(level=logging.INFO)
    
    loader = SummaryJsonLoader()
    
    print("可用模型:")
    for model in loader.get_available_models():
        print(f"  - {model}")
    
    print("\n加载数据...")
    df = loader.load_all_summary_data()
    
    print(f"\n数据形状: {df.shape}")
    print(f"\n列名: {df.columns.tolist()}")
    print(f"\n前5行:")
    print(df.head())
    
    print(f"\n模型统计:")
    print(df['model_name'].value_counts())
    
    print(f"\n任务类型统计:")
    print(df['task_type'].value_counts())
    
    print(f"\n性能指标统计:")
    if 'latency_s' in df.columns:
        print(df[['latency_s', 'toks_per_s', 'gpu_energy_j']].describe())
