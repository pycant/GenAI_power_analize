# load_process_quality_data() 函数使用指南

## 概述

`load_process_quality_data()` 是一个统一的质量数据加载接口，集成了 `process_quality_data` 模块的所有功能，为帕累托分析提供便捷的质量数据处理方法。

## 功能特点

- ✅ 统一接口：一个函数支持多种处理方法
- ✅ 自动处理：自动加载、归一化、计算权重
- ✅ 灵活配置：支持5种处理方法和4种归一化方法
- ✅ 标准输出：返回统一格式的 DataFrame（model, quality）
- ✅ 易于集成：可直接用于帕累托分析流程

## 函数签名

```python
def load_process_quality_data(
    task_name,              # 任务名称
    method='entropy',       # 处理方法
    normalize_method='minmax',  # 归一化方法
    use_raw=True,          # 使用原始数据
    verbose=True,          # 输出详细信息
    **kwargs               # 额外参数
)
```

## 支持的处理方法

### 1. 熵权法（entropy）- 默认推荐

基于信息熵理论客观计算指标权重，适合多指标综合评价。

```python
df = load_process_quality_data(
    task_name='code',
    method='entropy',
    normalize_method='minmax'
)
```

**特点**：
- ✅ 完全客观，不受主观影响
- ✅ 指标变异越大，权重越高
- ✅ 适合指标间相互独立的场景

### 2. 单一指标（single）

使用单个质量指标，适合有明确核心指标的任务。

```python
df = load_process_quality_data(
    task_name='code',
    method='single',
    quality_column='compilation_rate'  # 必须指定
)
```

**适用场景**：
- Code任务：使用 `compilation_rate`（编译成功率）
- QA任务：使用 `answer_relevance`（答案相关性）
- Translation任务：使用 `bleu_score`（BLEU分数）

### 3. PCA降维（pca）

使用主成分分析降维，取第一主成分作为质量得分。

```python
df = load_process_quality_data(
    task_name='reasoning',
    method='pca',
    n_components=1  # 可选，默认为1
)
```

**特点**：
- ✅ 消除指标间多重共线性
- ✅ 保留最大方差信息
- ✅ 适合指标间高度相关的场景

### 4. 简单平均（mean）

对所有指标进行简单平均，适合快速评估。

```python
df = load_process_quality_data(
    task_name='creative',
    method='mean',
    normalize_method='minmax'
)
```

**特点**：
- ✅ 简单直观
- ✅ 计算快速
- ✅ 适合指标重要性相近的场景

### 5. 自定义权重（custom）

使用专家经验或领域知识自定义权重。

```python
custom_weights = {
    'compilation_rate': 0.5,
    'test_pass_rate': 0.3,
    'code_length': 0.2
}

df = load_process_quality_data(
    task_name='code',
    method='custom',
    weights=custom_weights  # 必须指定
)
```

**适用场景**：
- 有明确的专家经验
- 特定应用场景的权重偏好
- 需要与熵权法对比验证

## 归一化方法

支持4种归一化方法（通过 `normalize_method` 参数指定）：

| 方法 | 范围 | 适用场景 |
|------|------|----------|
| `minmax` | [0, 1] | 数据无异常值（默认） |
| `zscore` | (-∞, +∞) | 数据近似正态分布 |
| `robust` | (-∞, +∞) | 数据有异常值 |
| `maxabs` | [-1, 1] | 需要保留正负号 |

## 返回格式

函数返回标准化的 DataFrame：

```python
   model      quality
0  model1     0.8523
1  model2     0.7234
2  model3     0.9012
...
```

- `model`: 模型短名称（如 'qwen25_7b_hf_4bit'）
- `quality`: 处理后的质量得分

## 完整示例

### 示例1: 代码任务 - 熵权法

```python
from pareto_core import load_process_quality_data

# 使用熵权法处理代码任务质量数据
df = load_process_quality_data(
    task_name='code',
    method='entropy',
    normalize_method='minmax',
    verbose=True
)

print(df.sort_values('quality', ascending=False))
```

### 示例2: 代码任务 - 单一指标

```python
# 只使用编译成功率作为质量指标
df = load_process_quality_data(
    task_name='code',
    method='single',
    quality_column='compilation_rate',
    verbose=True
)
```

### 示例3: Reasoning任务 - PCA降维

```python
# 使用PCA降维处理多指标
df = load_process_quality_data(
    task_name='reasoning',
    method='pca',
    n_components=1,
    verbose=True
)
```

### 示例4: 方法对比

```python
import pandas as pd

# 对比不同方法的结果
methods = ['entropy', 'mean', 'pca']
results = {}

for method in methods:
    df = load_process_quality_data(
        task_name='code',
        method=method,
        verbose=False
    )
    results[method] = df.set_index('model')['quality']

# 合并对比
comparison = pd.DataFrame(results)
print(comparison)

# 计算相关性
print("\n方法间相关性:")
print(comparison.corr())
```

### 示例5: 集成到帕累托分析

```python
from pareto_core import (
    load_process_quality_data,
    load_energy_speed_data,
    MODEL_MAPPING,
    DATA_PATHS,
    identify_pareto_frontier_2d
)

# 1. 加载质量数据（熵权法）
quality_df = load_process_quality_data(
    task_name='code',
    method='entropy',
    verbose=True
)

# 2. 加载能耗和速度数据
energy_dict, speed_dict = load_energy_speed_data(
    'code',
    DATA_PATHS['energy'],
    DATA_PATHS['speed']
)

# 3. 合并数据
merged_data = []
for _, row in quality_df.iterrows():
    model_short = row['model']
    model_full = MODEL_MAPPING.get(model_short)
    
    if model_full and model_full in energy_dict and model_full in speed_dict:
        merged_data.append({
            'model': model_short,
            'quality': row['quality'],
            'energy': energy_dict[model_full],
            'speed': speed_dict[model_full]
        })

df = pd.DataFrame(merged_data)

# 4. 识别帕累托前沿
pareto_qe = identify_pareto_frontier_2d(
    df, 'quality', 'energy',
    x_minimize=False, y_minimize=True
)

print(f"帕累托前沿模型: {df[pareto_qe]['model'].tolist()}")
```

## 方法选择指南

### 按任务类型选择

| 任务类型 | 推荐方法 | 原因 |
|---------|---------|------|
| Code | `single` (compilation_rate) 或 `entropy` | 编译成功率是核心指标 |
| Creative | `entropy` 或 `pca` | 多维度创意评价 |
| Math | `single` (accuracy) 或 `entropy` | 准确性是核心 |
| QA | `entropy` | 多维度问答质量 |
| Reasoning | `entropy` 或 `pca` | 复杂推理需综合评价 |
| Summary | `entropy` | 多维度摘要质量 |
| Translation | `single` (bleu_score) 或 `entropy` | BLEU是标准指标 |

### 按场景选择

| 场景 | 推荐方法 |
|------|---------|
| 快速评估 | `mean` |
| 标准评估 | `entropy` |
| 有核心指标 | `single` |
| 指标高度相关 | `pca` |
| 有专家经验 | `custom` |
| 需要对比验证 | 多种方法对比 |

## 参数详解

### task_name (必需)
任务名称，支持：
- `'code'` - 代码生成
- `'creative'` - 创意写作
- `'math'` - 数学推理
- `'qa'` - 问答
- `'reasoning'` - 逻辑推理
- `'summary'` - 文本摘要
- `'translation'` - 翻译

### method (可选，默认='entropy')
处理方法：
- `'entropy'` - 熵权法（推荐）
- `'single'` - 单一指标
- `'pca'` - PCA降维
- `'mean'` - 简单平均
- `'custom'` - 自定义权重

### normalize_method (可选，默认='minmax')
归一化方法：
- `'minmax'` - Min-Max归一化 [0, 1]
- `'zscore'` - Z-Score标准化
- `'robust'` - 鲁棒标准化
- `'maxabs'` - 最大绝对值归一化

### use_raw (可选，默认=True)
是否使用原始数据（保留完整精度）

### verbose (可选，默认=True)
是否输出详细信息

### **kwargs (可选)
额外参数：
- `quality_column` (str): 当 method='single' 时必需
- `n_components` (int): 当 method='pca' 时可选，默认1
- `weights` (dict): 当 method='custom' 时必需

## 错误处理

### 常见错误1: 缺少必需参数

```python
# 错误：method='single' 但未指定 quality_column
df = load_process_quality_data('code', method='single')
# ValueError: method='single' 时必须指定 quality_column 参数

# 正确：
df = load_process_quality_data('code', method='single', 
                               quality_column='compilation_rate')
```

### 常见错误2: 指标不存在

```python
# 错误：指定的指标不存在
df = load_process_quality_data('code', method='single', 
                               quality_column='nonexistent_metric')
# ValueError: 指标 'nonexistent_metric' 不存在

# 解决：查看可用指标
from pareto_core.process_quality_data import QualityDataProcessor
processor = QualityDataProcessor('code')
data = processor.load_quality_data()
print(data.columns)  # 查看所有可用指标
```

### 常见错误3: 不支持的方法

```python
# 错误：使用不支持的方法
df = load_process_quality_data('code', method='unknown')
# ValueError: 不支持的处理方法: unknown

# 正确：使用支持的方法
df = load_process_quality_data('code', method='entropy')
```

## 性能优化

### 批量处理多个任务

```python
tasks = ['code', 'creative', 'qa', 'reasoning']
all_quality = {}

for task in tasks:
    df = load_process_quality_data(
        task_name=task,
        method='entropy',
        verbose=False  # 关闭详细输出提高速度
    )
    all_quality[task] = df

print(f"处理完成: {len(all_quality)} 个任务")
```

### 缓存结果

```python
import pickle

# 保存结果
df = load_process_quality_data('code', method='entropy')
with open('code_quality_cache.pkl', 'wb') as f:
    pickle.dump(df, f)

# 加载缓存
with open('code_quality_cache.pkl', 'rb') as f:
    df = pickle.load(f)
```

## 与旧版本的对比

### 旧版本（手动处理）

```python
# 旧方式：需要多步操作
quality_df = pd.read_csv('quality_file.csv')
# ... 手动归一化
# ... 手动计算权重
# ... 手动合并数据
```

### 新版本（一键处理）

```python
# 新方式：一行代码完成
df = load_process_quality_data('code', method='entropy')
```

**优势**：
- ✅ 代码更简洁
- ✅ 减少错误
- ✅ 统一接口
- ✅ 易于维护

## 最佳实践

1. **默认使用熵权法**：适合大多数场景
2. **有核心指标时使用单一指标**：如代码任务的编译率
3. **多方法对比验证**：确保结果稳健性
4. **关闭verbose提高批量处理速度**
5. **使用原始数据保留精度**：use_raw=True

## 相关文档

- [质量数据处理详细指南](QUALITY_DATA_PROCESSING_GUIDE.md)
- [帕累托分析脚本总结](../PARETO_SCRIPTS_SUMMARY.md)
- [重构指南](../REFACTORING_GUIDE.md)

## 更新日志

### v1.0.0 (2026-03-07)
- ✅ 初始版本发布
- ✅ 支持5种处理方法
- ✅ 支持4种归一化方法
- ✅ 统一返回格式
- ✅ 完整错误处理

---

**作者**: GenAI Power Analysis Team  
**版本**: v1.0.0  
**更新日期**: 2026-03-07
