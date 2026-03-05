# JSON数据加载器使用指南

## 概述

数据管道现已支持加载原始实验JSON数据，包括 `raw.json` 和 `summary.json` 文件。

## 支持的数据目录

系统自动扫描以下模型目录：

```
data/
├── deepseek_8b_ol_q4km/
├── gemma_2b_hf_4bit/
├── gemma_2b_hf_8bit/
├── gemma_4b_ol_q4km/
├── phi3_4b_hf_4bit/
├── phi3_4b_hf_8bit/
├── qwen_4b_ol_q4km/
├── qwen_8b_ol_q4km/
├── qwen25_3b_hf_4bit/
├── qwen25_3b_hf_8bit/
├── qwen25_7b_hf_4bit/
└── qwen25_7b_hf_8bit/
```

每个目录下应包含：
- `experiment_results_*_raw.json` - 原始实验数据
- `experiment_results_*_summary.json` - 汇总实验数据

## Summary JSON 加载器

### 功能

`SummaryJsonLoader` 加载实验汇总数据，包含：

**性能指标**:
- `total_time_s` - 总执行时间（秒）
- `toks_per_s` - 吞吐量（tokens/秒）
- `latency_per_token_ms` - 每token延迟（毫秒）
- `ttft_s` - 首token时间（秒）
- `token_count` - token总数
- `output_tokens` - 输出token数

**资源使用**:
- CPU: `cpu_usage_avg`, `cpu_usage_peak`, `cpu_energy_j`
- 内存: `memory_used_avg_mb`, `memory_used_peak_mb`
- GPU: `gpu_util_avg`, `gpu_util_peak`, `gpu_memory_avg_mb`, `gpu_memory_peak_mb`
- GPU功耗: `gpu_power_avg_w`, `gpu_power_peak_w`, `gpu_energy_j`
- GPU温度: `gpu_temp_avg_c`, `gpu_temp_peak_c`

**质量指标**:
- `bartscore` - BARTScore质量得分
- `generated_text_length` - 生成文本长度
- `avg_response_length` - 平均响应长度

### 使用方法

```python
from data.analize.pipeline.converters import SummaryJsonLoader

# 创建加载器
loader = SummaryJsonLoader()

# 列出可用模型
available_models = loader.get_available_models()
print(f"可用模型: {available_models}")

# 加载所有数据
df = loader.load_all_summary_data()

print(f"加载了 {len(df)} 条记录")
print(f"列名: {df.columns.tolist()}")

# 查看性能指标
print(df[['model_name', 'task_type', 'latency_s', 'toks_per_s', 'gpu_energy_j']].head())
```

### 输出示例

```
可用模型: ['deepseek_8b_ol_q4km', 'qwen_8b_ol_q4km', 'gemma_4b_ol_q4km', ...]

加载了 120 条记录

列名: ['experiment_id', 'model_dir', 'model_name', 'task_type', 
       'total_time_s', 'toks_per_s', 'latency_s', 'gpu_energy_j', ...]

   model_name task_type  latency_s  toks_per_s  gpu_energy_j
0  deepseek-r1:8b  code      18.58       36.59       1387.42
1  qwen3:8b        qa        12.34       45.23       1024.56
...
```

## Raw JSON 加载器

### 功能

`RawJsonLoader` 加载原始实验数据，包含：

**基础信息**:
- `experiment_id` - 实验ID
- `model_name` - 模型名称
- `task_type` - 任务类型
- `prompt` - 输入提示
- `response` - 模型响应
- `response_length` - 响应长度

**时间信息**:
- `turn_duration_s` - 单轮对话时长

**监控数据**:
- CPU: `cpu_usage_avg`, `cpu_usage_peak`
- GPU: `gpu_util_avg`, `gpu_util_peak`, `gpu_memory_avg_mb`, `gpu_memory_peak_mb`
- GPU功耗: `gpu_power_avg_w`, `gpu_power_peak_w`
- GPU温度: `gpu_temp_avg_c`, `gpu_temp_peak_c`
- 内存: `memory_used_avg_mb`, `memory_used_peak_mb`

### 使用方法

```python
from data.analize.pipeline.converters import RawJsonLoader

# 创建加载器
loader = RawJsonLoader()

# 列出可用模型
available_models = loader.get_available_models()

# 加载所有数据
df = loader.load_all_raw_data()

print(f"加载了 {len(df)} 条记录")

# 查看对话内容
print(df[['model_name', 'task_type', 'prompt', 'response']].head())
```

## 数据管道集成

JSON加载器已自动集成到数据管道中。运行管道时会自动加载JSON数据：

```python
from data.analize.pipeline import ExperimentDataManager

dm = ExperimentDataManager()

# 初始化管道（自动加载JSON数据）
dm.initialize_pipeline()

# 加载合并后的数据
df = dm.load_all_data()

# 数据已包含JSON文件中的所有指标
print(df.columns.tolist())
```

## 数据合并逻辑

管道按以下顺序加载和合并数据：

1. **实验JSON数据** (优先级最高)
   - 加载所有模型目录下的 `*_summary.json`
   - 提取性能、资源、质量指标

2. **CSV数据**
   - `pre_data/responses_raw.csv`
   - `pre_data/comparison_matrices/`

3. **质量评估结果**
   - `results/*/quality_summary_*.csv`

所有数据源合并为统一的DataFrame，重复列会被智能合并。

## 模型名称标准化

加载器自动标准化模型名称：

| 原始名称 | 标准化名称 |
|---------|-----------|
| `Ollama:deepseek-r1:8b` | `deepseek-r1:8b` |
| `HF:Qwen/Qwen2.5-3B` | `qwen/qwen2.5-3b` |
| `gemma-2b-it` | `gemma-2b-it` |

## 测试

运行测试脚本验证加载器：

```bash
cd data/analize/pipeline
python test_json_loaders.py
```

测试包括：
1. Summary JSON加载器测试
2. Raw JSON加载器测试
3. 数据管道集成测试

## 故障排除

### 问题1: 未找到JSON文件

```
WARNING - 未找到summary.json文件: data/model_name/
```

**解决方案**: 确保模型目录下存在 `experiment_results_*_summary.json` 文件。

### 问题2: JSON解析错误

```
ERROR - 加载失败: JSONDecodeError
```

**解决方案**: 检查JSON文件格式是否正确，确保是有效的JSON。

### 问题3: 缺少必需字段

```
WARNING - 解析实验记录失败: KeyError
```

**解决方案**: 检查JSON文件是否包含必需的字段（如 `experiment_id`, `config`, `performance` 等）。

## 性能优化

### 大文件处理

对于大型JSON文件（>100MB），加载器会：
- 使用流式解析
- 分批处理记录
- 自动优化内存使用

### 缓存

加载的数据会自动缓存，避免重复解析：

```python
# 首次加载（较慢）
df = loader.load_all_summary_data()

# 后续加载（从缓存，很快）
df = loader.load_all_summary_data()
```

## 扩展支持

### 添加新的模型目录

编辑 `converters/summary_json_loader.py` 和 `converters/raw_json_loader.py`：

```python
self.model_dirs = [
    'deepseek_8b_ol_q4km',
    'your_new_model_dir',  # 添加新目录
    # ...
]
```

### 自定义字段提取

在 `_parse_summary()` 或 `_parse_experiment()` 方法中添加自定义字段：

```python
def _parse_summary(self, summary: Dict[str, Any], model_dir: str) -> Dict[str, Any]:
    record = {
        # 现有字段...
        
        # 添加自定义字段
        'custom_metric': summary.get('custom', {}).get('metric'),
    }
    return record
```

## 完整示例

```python
from data.analize.pipeline import ExperimentDataManager
from data.analize.pipeline.converters import SummaryJsonLoader

# 方法1: 直接使用加载器
loader = SummaryJsonLoader()
df_summary = loader.load_all_summary_data()

# 查看数据
print(f"加载了 {len(df_summary)} 条实验记录")
print(f"\n模型统计:")
print(df_summary['model_name'].value_counts())

print(f"\n性能指标:")
print(df_summary[['model_name', 'latency_s', 'toks_per_s', 'gpu_energy_j']].describe())

# 方法2: 通过数据管道（推荐）
dm = ExperimentDataManager()
dm.initialize_pipeline()  # 自动加载JSON数据

# 获取所有数据
df_all = dm.load_all_data()

# 按模型筛选
df_deepseek = dm.get_by_model('deepseek-r1:8b')

# 获取效率指标
efficiency = dm.get_efficiency_metrics(normalized=True)

# 计算复合得分
scores = dm.compute_composite_score()
```

## 更新日志

### v1.1.0 (2026-03-05)

- ✅ 新增 `SummaryJsonLoader` - 加载实验汇总数据
- ✅ 新增 `RawJsonLoader` - 加载原始实验数据
- ✅ 支持12个模型目录的自动扫描
- ✅ 集成到数据管道
- ✅ 完整的测试覆盖

## 参考

- 数据管道文档: `README.md`
- 实现总结: `IMPLEMENTATION_SUMMARY.md`
- 测试脚本: `test_json_loaders.py`
