# 列名不匹配问题修复总结

## 问题描述

运行 `run_mixed_task_analysis.py` 时出现 `KeyError: 'quality_score'` 错误。

## 错误信息

```
KeyError: 'quality_score'
File "...\run_mixed_task_analysis.py", line 161, in aggregate_quality_scores
    quality_score = model_data['quality_score'].values[0]
```

## 根本原因

**列名不一致**：

1. `load_process_quality_data()` 函数（在 `shared_functions.py` 中）返回的 DataFrame 包含列：
   - `'model'`
   - `'quality'` ✓

2. `aggregate_quality_scores()` 函数期望的列名：
   - `'model'`
   - `'quality_score'` ✗

这导致在尝试访问 `model_data['quality_score']` 时出现 KeyError。

## 解决方案

在 `aggregate_quality_scores()` 函数开始处添加列名统一逻辑：

```python
def aggregate_quality_scores(quality_data: Dict[str, pd.DataFrame], 
                            weights: Dict[str, float],
                            verbose: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """聚合多个任务的质量得分"""
    weights = normalize_weights(weights, verbose=verbose)
    
    # 统一列名：将 'quality' 重命名为 'quality_score'（如果需要）
    for task, df in quality_data.items():
        if 'quality' in df.columns and 'quality_score' not in df.columns:
            quality_data[task] = df.rename(columns={'quality': 'quality_score'})
    
    # ... 其余代码保持不变
```

## 修改内容

### 文件：`analysis/qe_research/scripts/run_mixed_task_analysis.py`

在 `aggregate_quality_scores()` 函数的第 140-142 行添加：

```python
# 统一列名：将 'quality' 重命名为 'quality_score'（如果需要）
for task, df in quality_data.items():
    if 'quality' in df.columns and 'quality_score' not in df.columns:
        quality_data[task] = df.rename(columns={'quality': 'quality_score'})
```

## 为什么这样修复

1. **向后兼容**：检查列是否存在再重命名，不会破坏已有代码
2. **最小侵入**：只修改一个函数，不需要改动多个文件
3. **清晰明确**：在数据聚合前统一列名，避免后续混淆

## 替代方案（未采用）

### 方案 A：修改 `load_process_quality_data()` 返回列名

```python
# 在 shared_functions.py 中
result_df = pd.DataFrame({
    'model': quality_score.index,
    'quality_score': quality_score.values  # 改为 quality_score
})
```

**缺点**：可能影响其他使用该函数的代码

### 方案 B：修改 `aggregate_quality_scores()` 使用 'quality' 列

```python
# 在 run_mixed_task_analysis.py 中
quality_score = model_data['quality'].values[0]  # 使用 quality
```

**缺点**：列名语义不够明确，且可能与其他 'quality' 列混淆

## 验证方法

运行混合任务分析：

```bash
cd analysis/qe_research/scripts
python run_mixed_task_analysis.py
```

预期输出：
```
================================================================================
混合任务帕累托前沿分析 - 客观任务为主
================================================================================
...
步骤2: 聚合质量得分
--------------------------------------------------------------------------------
✓ 权重已归一化（总和 = 1.000000）

共有 12 个模型

✓ 成功聚合 12 个模型的质量得分
  质量得分范围: [0.xxxx, 0.xxxx]
```

## 相关文件

- 修复文件：`analysis/qe_research/scripts/run_mixed_task_analysis.py`
- 数据加载：`analysis/qe_research/scripts/pareto_core/shared_functions.py`
- 数据处理：`analysis/qe_research/scripts/pareto_core/process_quality_data.py`

## 修复日期

2025-03-08

## 状态

✅ 已修复
