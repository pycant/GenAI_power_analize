# 质量数据处理模块

## 📋 概述

`process_quality_data.py` 是一个完整的质量数据处理工具，为帕累托前沿分析提供标准化的质量指标处理流程。

## ✨ 核心功能

### 1. 数据加载
- ✅ 自动从标准化目录加载质量数据
- ✅ 支持7种任务类型（code, creative, math, qa, reasoning, summary, translation）
- ✅ 自动转置数据格式（指标×模型 → 模型×指标）
- ✅ 支持原始数据和格式化数据

### 2. 数据归一化
- ✅ **Min-Max归一化**: 缩放到 [0, 1] 范围
- ✅ **Z-Score标准化**: 均值0，标准差1
- ✅ **Robust标准化**: 基于中位数和四分位距，抗异常值
- ✅ **MaxAbs归一化**: 缩放到 [-1, 1]，保留正负号

### 3. 熵权法
- ✅ 客观计算指标权重
- ✅ 基于信息熵理论
- ✅ 自动处理缺失值
- ✅ 生成加权质量得分

### 4. PCA降维
- ✅ 主成分分析降维
- ✅ 支持固定主成分数量或方差比例
- ✅ 提供载荷矩阵和方差解释
- ✅ 自动标准化处理

### 5. 结果导出
- ✅ 导出原始数据
- ✅ 导出归一化数据
- ✅ 导出熵权法权重
- ✅ 导出PCA结果（转换数据、载荷矩阵、方差解释）

## 🚀 快速开始

### 安装依赖

```bash
pip install pandas numpy scikit-learn matplotlib
```

### 基础用法

```python
from pareto_core.process_quality_data import QualityDataProcessor

# 初始化
processor = QualityDataProcessor(task_name='code')

# 加载数据
data = processor.load_quality_data()

# 归一化
normalized = processor.normalize(method='minmax')

# 熵权法
weights = processor.calculate_entropy_weights()
quality_score = processor.get_weighted_quality_score(weights)

# PCA降维
pca_result = processor.apply_pca(n_components=2)
```

### 一键处理

```python
from pareto_core.process_quality_data import quick_process

results = quick_process(
    task_name='reasoning',
    normalize_method='minmax',
    use_entropy=True,
    use_pca=True,
    n_components=2,
    output_dir='results/quality_processing'
)
```

## 📊 数据结构

### 输入数据位置
```
analysis/qe_research/results/quality_scores/
├── code_scores.csv          # 格式化版本
├── code_scores_raw.csv      # 原始版本（推荐）
├── creative_scores.csv
├── creative_scores_raw.csv
├── ...
```

### 输入数据格式
```csv
评分指标 \ 模型,model1,model2,model3,...
metric1,0.85,0.92,0.78,...
metric2,12.5,15.3,10.2,...
```

### 输出文件
- `{prefix}_quality_data.csv` - 原始数据（模型×指标）
- `{prefix}_normalized_data.csv` - 归一化数据
- `{prefix}_entropy_weights.csv` - 熵权法权重
- `{prefix}_pca_transformed.csv` - PCA降维数据
- `{prefix}_pca_components.csv` - 主成分载荷
- `{prefix}_pca_variance.csv` - 方差解释

## 📖 使用示例

### 示例1: 代码任务质量分析

```python
processor = QualityDataProcessor(task_name='code', verbose=True)
data = processor.load_quality_data()

# 归一化
normalized = processor.normalize(method='minmax')

# 熵权法
weights = processor.calculate_entropy_weights()
quality_score = processor.get_weighted_quality_score(weights)

# 查看最佳模型
print(quality_score.sort_values(ascending=False))

# 导出结果
processor.export_results('results/code_analysis', prefix='code')
```

### 示例2: 多任务对比

```python
tasks = ['code', 'creative', 'qa', 'reasoning']
all_scores = {}

for task in tasks:
    results = quick_process(task_name=task, use_entropy=True, use_pca=False)
    all_scores[task] = results['weighted_quality_score']

# 合并得分
import pandas as pd
scores_df = pd.DataFrame(all_scores)
scores_df['average'] = scores_df.mean(axis=1)
print(scores_df.sort_values('average', ascending=False))
```

### 示例3: PCA可视化

```python
import matplotlib.pyplot as plt

processor = QualityDataProcessor(task_name='reasoning')
data = processor.load_quality_data()
pca_result = processor.apply_pca(n_components=2)

# 可视化
pca_data = pca_result['transformed']
plt.figure(figsize=(10, 8))
plt.scatter(pca_data['PC1'], pca_data['PC2'], s=100)

for idx, model in enumerate(pca_data.index):
    plt.annotate(model, (pca_data.iloc[idx, 0], pca_data.iloc[idx, 1]))

plt.xlabel(f"PC1 ({pca_result['explained_variance_ratio'][0]:.1%})")
plt.ylabel(f"PC2 ({pca_result['explained_variance_ratio'][1]:.1%})")
plt.title('模型质量PCA降维')
plt.savefig('pca_visualization.png', dpi=300)
```

## 🔧 API参考

### QualityDataProcessor 类

#### 初始化
```python
processor = QualityDataProcessor(
    task_name='code',      # 任务名称
    use_raw=True,          # 使用原始数据
    verbose=True           # 输出详细信息
)
```

#### 主要方法

| 方法 | 功能 | 返回值 |
|------|------|--------|
| `load_quality_data()` | 加载质量数据 | DataFrame |
| `normalize(method, columns)` | 归一化数据 | DataFrame |
| `calculate_entropy_weights(data, columns)` | 计算熵权 | Dict |
| `get_weighted_quality_score(weights, data)` | 加权得分 | Series |
| `apply_pca(n_components, data)` | PCA降维 | Dict |
| `export_results(output_dir, prefix)` | 导出结果 | None |

### quick_process 函数

```python
results = quick_process(
    task_name='code',              # 任务名称
    normalize_method='minmax',     # 归一化方法
    use_entropy=True,              # 使用熵权法
    use_pca=True,                  # 使用PCA
    n_components=2,                # 主成分数量
    output_dir='results/'          # 输出目录（可选）
)
```

返回字典包含：
- `raw_data`: 原始数据
- `normalized_data`: 归一化数据
- `entropy_weights`: 熵权法权重
- `weighted_quality_score`: 加权质量得分
- `pca_result`: PCA结果

## 📚 方法论说明

### 归一化方法选择

| 场景 | 推荐方法 | 原因 |
|------|----------|------|
| 数据无异常值 | Min-Max | 固定范围，易于解释 |
| 数据近似正态分布 | Z-Score | 标准化处理，适合统计分析 |
| 数据有异常值 | Robust | 基于中位数，抗异常值 |
| 需要保留正负号 | MaxAbs | 保留符号信息 |

### 熵权法原理

熵权法是一种客观赋权方法：

1. **归一化**: 将数据缩放到 [0, 1]
2. **计算熵**: E_j = -Σ(p_ij × ln(p_ij)) / ln(n)
3. **差异系数**: d_j = 1 - E_j
4. **归一化权重**: w_j = d_j / Σd_j

**特点**:
- ✅ 完全客观，不受主观影响
- ✅ 指标变异越大，权重越高
- ✅ 适合多指标综合评价

### PCA降维原理

主成分分析通过线性变换降维：

1. **标准化**: Z-Score标准化
2. **协方差矩阵**: 计算指标间相关性
3. **特征分解**: 提取主成分
4. **降维投影**: 保留主要信息

**应用**:
- ✅ 指标过多时降维
- ✅ 消除多重共线性
- ✅ 可视化高维数据

## 🧪 测试

运行测试脚本：

```bash
python analysis/qe_research/scripts/test_quality_processing.py
```

测试内容：
- ✅ 数据加载
- ✅ 归一化方法
- ✅ 熵权法计算
- ✅ PCA降维
- ✅ 结果导出
- ✅ 一键处理
- ✅ 所有任务类型

## 📝 示例脚本

运行示例：

```bash
python analysis/qe_research/scripts/example_quality_processing.py
```

示例包含：
1. 基础用法
2. 数据归一化
3. 熵权法
4. PCA降维
5. 多任务对比
6. 一键处理

## 🔗 集成到帕累托分析

```python
from pareto_core.process_quality_data import QualityDataProcessor
from pareto_core import merge_quality_metrics, identify_pareto_frontier_2d

# 1. 处理质量数据
processor = QualityDataProcessor(task_name='code')
data = processor.load_quality_data()
weights = processor.calculate_entropy_weights()
quality_score = processor.get_weighted_quality_score(weights)

# 2. 转换为帕累托分析格式
quality_df = pd.DataFrame({
    'model': quality_score.index,
    'quality': quality_score.values
})

# 3. 合并能耗和速度数据
# ... 继续帕累托分析流程
```

## 📄 相关文档

- [详细使用指南](QUALITY_DATA_PROCESSING_GUIDE.md)
- [帕累托分析总结](../PARETO_SCRIPTS_SUMMARY.md)
- [重构指南](../REFACTORING_GUIDE.md)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📜 许可证

MIT License

---

**作者**: GenAI Power Analysis Team  
**版本**: v1.0.0  
**更新日期**: 2026-03-07
