"""
原始JSON数据加载器 - 加载实验raw.json文件
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import logging
import re

logger = logging.getLogger(__name__)


class RawJsonLoader:
    """加载和解析原始实验JSON数据"""
    
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
    
    def load_all_raw_data(self) -> pd.DataFrame:
        """
        加载所有模型目录下的raw.json文件
        
        Returns:
            合并后的DataFrame
        """
        all_data = []
        
        for model_dir in self.model_dirs:
            dir_path = self.data_root / model_dir
            
            if not dir_path.exists():
                logger.warning(f"目录不存在: {dir_path}")
                continue
            
            # 查找所有raw.json文件
            raw_files = list(dir_path.glob('*_raw.json'))
            
            if not raw_files:
                logger.warning(f"未找到raw.json文件: {dir_path}")
                continue
            
            for raw_file in raw_files:
                logger.info(f"加载: {raw_file}")
                try:
                    df = self.load_raw_json(raw_file, model_dir)
                    all_data.append(df)
                except Exception as e:
                    logger.error(f"加载失败 {raw_file}: {e}")
        
        if not all_data:
            raise ValueError("未找到任何有效的raw.json数据")
        
        # 合并所有数据
        combined = pd.concat(all_data, ignore_index=True)
        logger.info(f"总共加载 {len(combined)} 条记录")
        
        return combined
    
    def load_raw_json(self, file_path: Path, model_dir: str) -> pd.DataFrame:
        """
        加载单个raw.json文件
        
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
            record = self._parse_experiment(experiment, model_dir)
            if record:
                records.append(record)
        
        return pd.DataFrame(records)
    
    def _parse_experiment(self, exp: Dict[str, Any], model_dir: str) -> Dict[str, Any]:
        """
        解析单个实验记录
        
        Args:
            exp: 实验数据字典
            model_dir: 模型目录名
            
        Returns:
            解析后的记录字典
        """
        try:
            # 基础信息
            record = {
                'experiment_id': exp.get('experiment_id'),
                'model_dir': model_dir,
                'model_name': self._extract_model_name(exp.get('config', {}).get('model', model_dir)),
                'task_type': exp.get('config', {}).get('task_type', 'unknown'),
            }
            
            # 提取对话信息
            conversation = exp.get('conversation', [])
            if conversation:
                first_turn = conversation[0]
                record['prompt'] = first_turn.get('prompt', '')
                record['response'] = first_turn.get('response', '')
                record['response_length'] = len(first_turn.get('response', ''))
                
                # 时间信息
                start_ts = first_turn.get('start_timestamp')
                end_ts = first_turn.get('end_timestamp')
                if start_ts and end_ts:
                    record['turn_duration_s'] = end_ts - start_ts
            
            # 监控数据
            monitoring = exp.get('monitoring_data', {})
            if monitoring:
                measurements = monitoring.get('measurements', {})
                
                # CPU指标
                cpu_percent = measurements.get('cpu_percent', [])
                if cpu_percent:
                    record['cpu_usage_avg'] = sum(cpu_percent) / len(cpu_percent)
                    record['cpu_usage_peak'] = max(cpu_percent)
                
                # GPU指标
                gpu_util = measurements.get('gpu_util', [])
                if gpu_util:
                    record['gpu_util_avg'] = sum(gpu_util) / len(gpu_util)
                    record['gpu_util_peak'] = max(gpu_util)
                
                gpu_mem = measurements.get('gpu_mem_mb', [])
                if gpu_mem:
                    record['gpu_memory_avg_mb'] = sum(gpu_mem) / len(gpu_mem)
                    record['gpu_memory_peak_mb'] = max(gpu_mem)
                
                gpu_power = measurements.get('gpu_power_w', [])
                if gpu_power:
                    record['gpu_power_avg_w'] = sum(gpu_power) / len(gpu_power)
                    record['gpu_power_peak_w'] = max(gpu_power)
                
                gpu_temp = measurements.get('gpu_temp_c', [])
                if gpu_temp:
                    record['gpu_temp_avg_c'] = sum(gpu_temp) / len(gpu_temp)
                    record['gpu_temp_peak_c'] = max(gpu_temp)
                
                # 内存指标
                mem_used = measurements.get('mem_used_mb', [])
                if mem_used:
                    record['memory_used_avg_mb'] = sum(mem_used) / len(mem_used)
                    record['memory_used_peak_mb'] = max(mem_used)
            
            return record
            
        except Exception as e:
            logger.error(f"解析实验记录失败: {e}")
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
                raw_files = list(dir_path.glob('*_raw.json'))
                if raw_files:
                    available.append(model_dir)
        return available


if __name__ == '__main__':
    # 测试加载器
    logging.basicConfig(level=logging.INFO)
    
    loader = RawJsonLoader()
    
    print("可用模型:")
    for model in loader.get_available_models():
        print(f"  - {model}")
    
    print("\n加载数据...")
    df = loader.load_all_raw_data()
    
    print(f"\n数据形状: {df.shape}")
    print(f"\n列名: {df.columns.tolist()}")
    print(f"\n前5行:")
    print(df.head())
    
    print(f"\n模型统计:")
    print(df['model_name'].value_counts())
    
    print(f"\n任务类型统计:")
    print(df['task_type'].value_counts())
