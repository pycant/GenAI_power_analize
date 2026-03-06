# 数据管道系统 (Data Pipeline System)

## 概述

统一的数据访问和处理层，将分散的实验数据转换为标准化、高性能的分析格式。

## 目录结构

```
pipeline/
├── README.md                    # 本文档
├── data_manager.py             # 核心数据管理类
├── data_pipeline.py            # ETL管道
├── data_validator.py           # 数据验证
├── schema.py                   # 数据模式定义
├── converters/                 # 数据转换器
│   ├── __init__.py
│   ├── csv_to_parquet.py      # CSV转Parquet
│   └── quality_aggregator.py  # 质量指标聚合
└── utils/                      # 工具函数
    ├── __init__.py
    ├── cache_manager.py       # 缓存管理
    └── performance.py         # 性能优化工具
```

## 数据流

```
原始数据源
├── 实验JSON数据 (data/*/experiment_results_*_summary.json)
├── CSV数据 (pre_data/responses_raw.csv)
├── 对比矩阵 (pre_data/comparison_matrices/)
└── 质量评估结果 (results/*/quality_summary_*.csv)
    ↓
[数据加载] converters/
├── SummaryJsonLoader - 加载实验summary.json
├── RawJsonLoader - 加载实验raw.json
└── CSV加载器 - 加载CSV文件
    ↓
[数据验证] data_validator.py
    ↓
[ETL转换] data_pipeline.py
    ↓
标准化数据 (processed/)
├── master_data.parquet
├── quality_metrics.parquet
├── efficiency_metrics.parquet
└── task_summaries/
    ↓
[数据管理] data_manager.py
    ↓
分析脚本 / 可视化
```

## 快速开始

### 1. 初始化数据管道

```python
from pipeline.data_manager import ExperimentDataManager

# 创建数据管理器
dm = ExperimentDataManager()

# 首次运行：转换所有数据
dm.initialize_pipeline()
```

### 2. 加载数据

```python
# 加载所有数据
df_all = dm.load_all_data()

# 按任务类型加载
df_code = dm.get_by_task('code')
df_qa = dm.get_by_task('qa')

# 按模型加载
df_qwen = dm.get_by_model('qwen3:8b')
```

### 3. 获取指标

```python
# 质量指标（归一化）
quality = dm.get_quality_metrics(normalized=True)

# 效率指标（原始值）
efficiency = dm.get_efficiency_metrics(normalized=False)

# 复合得分
scores = dm.compute_composite_score({
    'quality': 0.4,
    'efficiency': 0.6
})
```

## 数据格式

### 主数据表 (master_data.parquet)

| 列名 | 类型 | 说明 |
|------|------|------|
| model_name | category | 模型名称 |
| task_type | category | 任务类型 |
| prompt_id | int | 提示词ID |
| run_id | int | 运行ID |
| response_text | string | 响应文本 |
| latency_s | float | 延迟(秒) |
| toks_per_s | float | 吞吐量 |
| gpu_energy_j | float | GPU能耗(焦耳) |
| quality_score | float | 质量得分 |
| ... | ... | ... |

### 质量指标表 (quality_metrics.parquet)

按任务类型包含不同的质量指标：
- code: code_compiles, syntax_score, logic_score
- qa: bartscore, relevance, completeness
- creative: distinct_2, fluency, creativity
- summary: rouge_scores, coherence
- reasoning: logical_steps, correctness
- math: accuracy, step_validity
- translation: bleu, adequacy

### 效率指标表 (efficiency_metrics.parquet)

- latency_s: 延迟
- toks_per_s: 吞吐量
- gpu_energy_j: GPU能耗
- cpu_usage: CPU使用率
- memory_usage: 内存使用

## 性能优化

- **Parquet格式**: 比CSV快3-10倍，节省50-80%空间
- **列式存储**: 只加载需要的列
- **类型优化**: category类型存储重复字符串
- **缓存机制**: 自动缓存常用查询结果
- **延迟加载**: 按需加载数据

## 配置

编辑 `configs/pipeline_config.yaml` 自定义：
- 数据路径
- 缓存策略
- 归一化方法
- 指标权重

## 维护

### 更新数据
```python
dm.refresh_data()  # 重新扫描并转换新数据
```

### 清理缓存
```python
dm.clear_cache()  # 清理所有缓存
```

### 验证数据完整性
```python
from pipeline.data_validator import validate_all
validate_all()  # 检查数据一致性
```

## 依赖

```bash
pip install pandas pyarrow fastparquet
```

## 注意事项

1. 首次运行会创建 `processed/` 目录并转换所有数据
2. 原始数据保持不变，只读取不修改
3. 缓存存储在 `cache/` 目录，可安全删除
4. Parquet文件需要pyarrow或fastparquet库
