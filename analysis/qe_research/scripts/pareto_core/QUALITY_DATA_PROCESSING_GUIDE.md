# 质量数据处理模块使用指南

## 概述

`process_quality_data.py` 模块提供了完整的质量数据处理功能，包括：

- ✅ 从标准化目录加载质量数据
- ✅ 多种归一化方法（Min-Max、Z-Score、Robust、MaxAbs）
- ✅ 熵权法计算指标权重
- ✅ PCA降维分析
- ✅ 一键处理流程

## 快速开始

### 1. 基础用法

```python
from pareto_core.process_quality_data import QualityDataProcessor

# 初始化处理器
processor = QualityDataProcessor(task_name='code')

# 加载数据
data = processor.load_quality_data()
print(data.head())
```

### 2. 数据归一化

```python
# Min-Max归一化 [0, 1]
normalized = processor.normalize(method='minmax')

# Z-Score标准化（均值0，标准差1）
normalized = processor.normalize(method='zscore')

# 鲁棒标准化（使用中位数和四分位距）
normalized = processor.normalize(method='robust')

# 最大绝对值归一化 [-1, 1]
normalized = processor.normalize(method='maxabs')
```

### 3. 熵权法计算权重

```python
# 计算熵权
weights = processor.calculate_entropy_weights()

# 输出示例：
# {
#     'compilation_rate': 0.3245,
#     'test_pass_rate': 0.2876,
#     'code_length': 0.1543,
#     ...
# }

# 获取加权质量得分
quality_score = processor.get_weighted_quality_score(weights)
print(quality_score.sort_values(ascending=False))
```

### 4. PCA降维

```python
# 降维到2个主成分
pca_result = processor.apply_pca(n_components=2)

# 访问结果
print("降维后的数据:")
print(pca_result['transformed'])

print("\n主成分载荷:")
print(pca_result['components'])

print("\n解释方差比例:")
print(pca_result['explained_variance_ratio'])

# 或者保留90%的方差
pca_result = processor.apply_pca(n_components=0.9)
```

### 5. 一键处理

```python
from pareto_core.process_quality_data import quick_process

# 一键完成所有处理
results = quick_process(
    task_name='reasoning',
    normalize_method='minmax',
    use_entropy=True,
    use_pca=True,
    n_components=3,
    output_dir='results/quality_processing'
)

# 访问结果
data = results['raw_data']
normalized = results['normalized_data']
weights = results['entropy_weights']
quality_score = results['weighted_quality_score']
pca = results['pca_result']
```

## 详细功能说明

### 支持的任务类型

- `code` - 代码生成任务
- `creative` - 创意写作任务
- `math` - 数学推理任务
- `qa` - 问答任务
- `reasoning` - 逻辑推理任务
- `summary` - 文本摘要任务
- `translation` - 翻译任务

### 归一化方法对比

| 方法 | 公式 | 范围 | 适用场景 |
|------|------|------|----------|
| Min-Max | (x - min) / (max - min) | [0, 1] | 数据无异常值，需要固定范围 |
| Z-Score | (x - mean) / std | (-∞, +∞) | 数据近似正态分布 |
| Robust | (x - median) / IQR | (-∞, +∞) | 数据有异常值 |
| MaxAbs | x / max(\|x\|) | [-1, 1] | 保留正负号信息 |

### 熵权法原理

熵权法是一种客观赋权方法，基于信息熵理论：

1. **数据归一化**：将所有指标归一化到 [0, 1]
2. **计算信息熵**：E_j = -Σ(p_ij × ln(p_ij)) / ln(n)
3. **计算差异系数**：d_j = 1 - E_j
4. **归一化权重**：w_j = d_j / Σd_j

**特点**：
- 指标变异程度越大，权重越高
- 完全客观，不受主观影响
- 适合多指标综合评价

### PCA降维原理

主成分分析（PCA）通过线性变换将多个相关指标转换为少数几个不相关的主成分：

1. **数据标准化**：Z-Score标准化
2. **计算协方差矩阵**
3. **特征值分解**：提取主成分
4. **降维投影**：保留前k个主成分

**应用场景**：
- 指标过多，需要降维
- 指标间存在多重共线性
- 可视化高维数据

## 完整示例

### 示例1：代码任务质量分析

```python
from pareto_core.process_quality_data import QualityDataProcessor

# 初始化
processor = QualityDataProcessor(task_name='code', verbose=True)

# 加载数据
data = processor.load_quality_data()
print(f"模型数量: {len(data)}")
print(f"指标数量: {len(data.columns)}")

# 归一化
normalized = processor.normalize(method='minmax')

# 熵权法
weights = processor.calculate_entropy_weights()
quality_score = processor.get_weighted_quality_score(weights)

# 查看最佳模型
print("\n质量得分排名:")
for model, score in quality_score.sort_values(ascending=False).items():
    print(f"{model}: {score:.4f}")

# PCA降维
pca_result = processor.apply_pca(n_components=2)

# 导出结果
processor.export_results('results/code_quality_analysis', prefix='code')
```

### 示例2：多任务对比分析

```python
from pareto_core.process_quality_data import quick_process
import pandas as pd

tasks = ['code', 'creative', 'qa', 'reasoning']
all_scores = {}

for task in tasks:
    print(f"\n处理任务: {task.upper()}")
    results = quick_process(
        task_name=task,
        normalize_method='minmax',
        use_entropy=True,
        use_pca=False,
        output_dir=f'results/{task}_processing'
    )
    all_scores[task] = results['weighted_quality_score']

# 合并所有任务的得分
scores_df = pd.DataFrame(all_scores)
print("\n跨任务质量得分对比:")
print(scores_df)

# 计算平均得分
scores_df['average'] = scores_df.mean(axis=1)
print("\n平均质量得分排名:")
print(scores_df['average'].sort_values(ascending=False))
```

### 示例3：自定义权重

```python
from pareto_core.process_quality_data import QualityDataProcessor

processor = QualityDataProcessor(task_name='code')
data = processor.load_quality_data()

# 方案1：使用熵权法
entropy_weights = processor.calculate_entropy_weights()
entropy_score = processor.get_weighted_quality_score(entropy_weights)

# 方案2：自定义权重（专家经验）
custom_weights = {
    'compilation_rate': 0.4,      # 编译成功率最重要
    'test_pass_rate': 0.3,        # 测试通过率次之
    'cyclomatic_complexity': 0.2, # 代码复杂度
    'code_length': 0.1            # 代码长度
}
custom_score = processor.get_weighted_quality_score(custom_weights)

# 对比两种方案
comparison = pd.DataFrame({
    'entropy_weight': entropy_score,
    'custom_weight': custom_score
})
print(comparison.sort_values('entropy_weight', ascending=False))
```

### 示例4：PCA可视化

```python
from pareto_core.process_quality_data import QualityDataProcessor
import matplotlib.pyplot as plt

processor = QualityDataProcessor(task_name='reasoning')
data = processor.load_quality_data()

# PCA降维到2维
pca_result = processor.apply_pca(n_components=2)
pca_data = pca_result['transformed']

# 可视化
plt.figure(figsize=(10, 8))
plt.scatter(pca_data['PC1'], pca_data['PC2'], s=100, alpha=0.6)

# 添加模型标签
for idx, model in enumerate(pca_data.index):
    plt.annotate(model, (pca_data.iloc[idx, 0], pca_data.iloc[idx, 1]),
                fontsize=9, alpha=0.8)

plt.xlabel(f"PC1 ({pca_result['explained_variance_ratio'][0]:.1%})")
plt.ylabel(f"PC2 ({pca_result['explained_variance_ratio'][1]:.1%})")
plt.title('模型质量PCA降维可视化')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('pca_visualization.png', dpi=300)
plt.show()
```

## 数据结构说明

### 输入数据格式

质量数据文件位于：`analysis/qe_research/results/quality_scores/`

文件命名规则：
- 格式化版本：`{task}_scores.csv`
- 原始版本：`{task}_scores_raw.csv`（推荐，保留完整精度）

数据格式（指标×模型）：
```csv
评分指标 \ 模型,model1,model2,model3,...
metric1,0.85,0.92,0.78,...
metric2,12.5,15.3,10.2,...
metric3,0.65,0.71,0.59,...
...
```

### 输出数据格式

调用 `export_results()` 后生成的文件：

1. `{prefix}_quality_data.csv` - 原始数据（模型×指标）
2. `{prefix}_normalized_data.csv` - 归一化后的数据
3. `{prefix}_entropy_weights.csv` - 熵权法权重
4. `{prefix}_pca_transformed.csv` - PCA降维后的数据
5. `{prefix}_pca_components.csv` - 主成分载荷矩阵
6. `{prefix}_pca_variance.csv` - 方差解释比例

## API参考

### QualityDataProcessor 类

#### 初始化参数

- `task_name` (str): 任务名称
- `use_raw` (bool): 是否使用原始数据，默认True
- `verbose` (bool): 是否输出详细信息，默认True

#### 主要方法

##### load_quality_data()
加载质量数据

**返回**: DataFrame（模型×指标格式）

##### normalize(method, columns)
归一化数据

**参数**:
- `method` (str): 归一化方法（'minmax', 'zscore', 'robust', 'maxabs'）
- `columns` (List[str], optional): 要归一化的列

**返回**: DataFrame（归一化后的数据）

##### calculate_entropy_weights(data, columns)
计算熵权法权重

**参数**:
- `data` (DataFrame, optional): 输入数据
- `columns` (List[str], optional): 要计算权重的列

**返回**: Dict[str, float]（指标权重字典）

##### get_weighted_quality_score(weights, data, normalize_first)
计算加权质量得分

**参数**:
- `weights` (Dict, optional): 指标权重
- `data` (DataFrame, optional): 输入数据
- `normalize_first` (bool): 是否先归一化，默认True

**返回**: Series（每个模型的加权得分）

##### apply_pca(n_components, data, normalize_first)
应用PCA降维

**参数**:
- `n_components` (int or float): 主成分数量或方差比例
- `data` (DataFrame, optional): 输入数据
- `normalize_first` (bool): 是否先标准化，默认True

**返回**: Dict（PCA结果字典）

##### export_results(output_dir, prefix)
导出所有处理结果

**参数**:
- `output_dir` (str or Path): 输出目录
- `prefix` (str): 文件名前缀

### quick_process 函数

一键完成质量数据处理流程

**参数**:
- `task_name` (str): 任务名称
- `normalize_method` (str): 归一化方法，默认'minmax'
- `use_entropy` (bool): 是否使用熵权法，默认True
- `use_pca` (bool): 是否使用PCA，默认True
- `n_components` (int): PCA主成分数量，默认2
- `output_dir` (str or Path, optional): 输出目录

**返回**: Dict（处理结果字典）

## 常见问题

### Q1: 如何处理缺失值？

模块会自动处理缺失值：
- 归一化时跳过NaN值
- 熵权法计算时删除包含NaN的行
- PCA时删除包含NaN的行
- 加权得分时用均值填充NaN

### Q2: 如何选择归一化方法？

- 数据无异常值 → Min-Max
- 数据近似正态分布 → Z-Score
- 数据有异常值 → Robust
- 需要保留正负号 → MaxAbs

### Q3: 熵权法适用于所有场景吗？

熵权法适合：
- 指标间相互独立
- 需要客观赋权
- 指标变异程度有意义

不适合：
- 指标间高度相关（考虑PCA）
- 有明确的专家经验（考虑自定义权重）

### Q4: PCA降维会损失信息吗？

是的，但可以控制：
- 查看累积方差比例
- 保留90%以上的方差通常足够
- 通过载荷矩阵理解主成分含义

### Q5: 如何集成到帕累托分析？

```python
from pareto_core.process_quality_data import QualityDataProcessor
from pareto_core import merge_quality_metrics

# 1. 处理质量数据
processor = QualityDataProcessor(task_name='code')
data = processor.load_quality_data()
weights = processor.calculate_entropy_weights()
quality_score = processor.get_weighted_quality_score(weights)

# 2. 转换为帕累托分析所需格式
quality_df = pd.DataFrame({
    'model': quality_score.index,
    'quality': quality_score.values
})

# 3. 合并能耗和速度数据
# ... 继续帕累托分析流程
```

## 更新日志

### v1.0.0 (2026-03-07)
- ✅ 初始版本发布
- ✅ 支持7种任务类型
- ✅ 实现4种归一化方法
- ✅ 实现熵权法
- ✅ 实现PCA降维
- ✅ 提供一键处理函数

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License
