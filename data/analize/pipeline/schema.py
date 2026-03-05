"""
数据模式定义 - 标准化的列名、类型和验证规则
"""
from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class ColumnSchema:
    """列模式定义"""
    name: str
    dtype: str
    required: bool = True
    description: str = ""
    valid_range: tuple = None
    valid_values: list = None

@dataclass
class DataSchema:
    """数据模式"""
    
    # 主键列
    PRIMARY_KEYS = ['model_name', 'task_type', 'prompt_id', 'run_id']
    
    # 任务类型
    TASK_TYPES = ['code', 'qa', 'creative', 'summary', 'reasoning', 'math', 'translation']
    
    # 基础列定义
    BASE_COLUMNS = [
        ColumnSchema('model_name', 'category', True, '模型名称'),
        ColumnSchema('task_type', 'category', True, '任务类型', valid_values=TASK_TYPES),
        ColumnSchema('prompt_id', 'int32', True, '提示词ID', valid_range=(0, 1000)),
        ColumnSchema('run_id', 'int32', True, '运行ID', valid_range=(0, 100)),
        ColumnSchema('response_text', 'string', True, '响应文本'),
        ColumnSchema('timestamp', 'datetime64[ns]', False, '时间戳'),
    ]
    
    # 效率指标列
    EFFICIENCY_COLUMNS = [
        ColumnSchema('latency_s', 'float32', True, '延迟(秒)', valid_range=(0, 1000)),
        ColumnSchema('toks_per_s', 'float32', True, '吞吐量(tokens/s)', valid_range=(0, 10000)),
        ColumnSchema('gpu_energy_j', 'float32', True, 'GPU能耗(焦耳)', valid_range=(0, 100000)),
        ColumnSchema('cpu_usage', 'float32', False, 'CPU使用率(%)', valid_range=(0, 100)),
        ColumnSchema('memory_usage', 'float32', False, '内存使用(MB)', valid_range=(0, 100000)),
        ColumnSchema('gpu_memory_mb', 'float32', False, 'GPU显存(MB)', valid_range=(0, 100000)),
    ]
    
    # 通用质量指标列
    QUALITY_COLUMNS = [
        ColumnSchema('quality_score', 'float32', False, '综合质量得分', valid_range=(0, 1)),
        ColumnSchema('bartscore', 'float32', False, 'BARTScore', valid_range=(-10, 0)),
    ]
    
    # 任务特定质量指标
    TASK_SPECIFIC_QUALITY = {
        'code': [
            ColumnSchema('code_compiles', 'bool', False, '代码可编译'),
            ColumnSchema('syntax_score', 'float32', False, '语法得分', valid_range=(0, 1)),
            ColumnSchema('logic_score', 'float32', False, '逻辑得分', valid_range=(0, 1)),
            ColumnSchema('readability_score', 'float32', False, '可读性得分', valid_range=(0, 1)),
        ],
        'qa': [
            ColumnSchema('relevance', 'float32', False, '相关性', valid_range=(0, 1)),
            ColumnSchema('completeness', 'float32', False, '完整性', valid_range=(0, 1)),
            ColumnSchema('accuracy', 'float32', False, '准确性', valid_range=(0, 1)),
        ],
        'creative': [
            ColumnSchema('distinct_2', 'float32', False, 'Distinct-2', valid_range=(0, 1)),
            ColumnSchema('fluency', 'float32', False, '流畅度', valid_range=(0, 1)),
            ColumnSchema('creativity', 'float32', False, '创造性', valid_range=(0, 1)),
        ],
        'summary': [
            ColumnSchema('rouge_1', 'float32', False, 'ROUGE-1', valid_range=(0, 1)),
            ColumnSchema('rouge_2', 'float32', False, 'ROUGE-2', valid_range=(0, 1)),
            ColumnSchema('rouge_l', 'float32', False, 'ROUGE-L', valid_range=(0, 1)),
            ColumnSchema('coherence', 'float32', False, '连贯性', valid_range=(0, 1)),
        ],
        'reasoning': [
            ColumnSchema('logical_steps', 'int32', False, '逻辑步骤数', valid_range=(0, 100)),
            ColumnSchema('correctness', 'float32', False, '正确性', valid_range=(0, 1)),
            ColumnSchema('clarity', 'float32', False, '清晰度', valid_range=(0, 1)),
        ],
        'math': [
            ColumnSchema('accuracy', 'float32', False, '准确性', valid_range=(0, 1)),
            ColumnSchema('step_validity', 'float32', False, '步骤有效性', valid_range=(0, 1)),
            ColumnSchema('final_answer_correct', 'bool', False, '最终答案正确'),
        ],
        'translation': [
            ColumnSchema('bleu', 'float32', False, 'BLEU分数', valid_range=(0, 1)),
            ColumnSchema('adequacy', 'float32', False, '充分性', valid_range=(0, 1)),
            ColumnSchema('fluency', 'float32', False, '流畅度', valid_range=(0, 1)),
        ],
    }
    
    # 派生指标列
    DERIVED_COLUMNS = [
        ColumnSchema('efficiency_score', 'float32', False, '效率得分', valid_range=(0, 1)),
        ColumnSchema('qe_ratio', 'float32', False, '质效比', valid_range=(0, 100)),
        ColumnSchema('norm_quality', 'float32', False, '归一化质量', valid_range=(0, 1)),
        ColumnSchema('norm_efficiency', 'float32', False, '归一化效率', valid_range=(0, 1)),
    ]
    
    @classmethod
    def get_all_columns(cls, task_type: str = None) -> List[ColumnSchema]:
        """获取所有列定义"""
        columns = cls.BASE_COLUMNS + cls.EFFICIENCY_COLUMNS + cls.QUALITY_COLUMNS
        
        if task_type and task_type in cls.TASK_SPECIFIC_QUALITY:
            columns += cls.TASK_SPECIFIC_QUALITY[task_type]
        
        columns += cls.DERIVED_COLUMNS
        return columns
    
    @classmethod
    def get_column_names(cls, task_type: str = None) -> List[str]:
        """获取列名列表"""
        return [col.name for col in cls.get_all_columns(task_type)]
    
    @classmethod
    def get_dtype_dict(cls, task_type: str = None) -> Dict[str, str]:
        """获取数据类型字典"""
        return {col.name: col.dtype for col in cls.get_all_columns(task_type)}
    
    @classmethod
    def get_required_columns(cls, task_type: str = None) -> List[str]:
        """获取必需列"""
        return [col.name for col in cls.get_all_columns(task_type) if col.required]
    
    @classmethod
    def get_quality_columns(cls, task_type: str) -> List[str]:
        """获取质量指标列名"""
        cols = [col.name for col in cls.QUALITY_COLUMNS]
        if task_type in cls.TASK_SPECIFIC_QUALITY:
            cols += [col.name for col in cls.TASK_SPECIFIC_QUALITY[task_type]]
        return cols
    
    @classmethod
    def get_efficiency_columns(cls) -> List[str]:
        """获取效率指标列名"""
        return [col.name for col in cls.EFFICIENCY_COLUMNS]


# 配置常量
class PipelineConfig:
    """管道配置"""
    
    # 路径配置
    BASE_PATH = 'data/analize'
    RAW_DATA_PATH = f'{BASE_PATH}/pre_data'
    RESULTS_PATH = f'{BASE_PATH}/results'
    PROCESSED_PATH = f'{BASE_PATH}/processed'
    CACHE_PATH = f'{BASE_PATH}/cache'
    
    # 文件名
    MASTER_DATA_FILE = 'master_data.parquet'
    QUALITY_METRICS_FILE = 'quality_metrics.parquet'
    EFFICIENCY_METRICS_FILE = 'efficiency_metrics.parquet'
    METADATA_FILE = 'metadata.json'
    
    # 性能配置
    CHUNK_SIZE = 10000  # 分块处理大文件
    CACHE_ENABLED = True
    CACHE_TTL = 3600  # 缓存过期时间(秒)
    
    # 归一化配置
    NORMALIZATION_METHOD = 'minmax'  # 'minmax', 'zscore', 'robust'
    NORMALIZATION_BY_TASK = True  # 按任务类型分组归一化
    
    # 复合得分默认权重
    DEFAULT_WEIGHTS = {
        'quality': 0.5,
        'efficiency': 0.5,
    }
    
    EFFICIENCY_WEIGHTS = {
        'throughput': 0.4,
        'latency': 0.3,
        'energy': 0.3,
    }
