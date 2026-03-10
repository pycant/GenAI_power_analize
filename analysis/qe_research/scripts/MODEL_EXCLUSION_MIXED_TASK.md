# 混合任务分析中的模型排除实现

## 概述

在混合任务帕累托前沿分析中添加了模型排除机制，以剔除存在数据缺失问题的模型。

## 排除的模型

```python
EXCLUDED_MODELS = [
    'qwen25_7b_hf_8bit',  # 在其他任务上数据有缺失
    'qwen--qwen2.5-7b-instruct:8bit',
    'qwen2.5-7b-instruct:8bit'
]
```

## 排除原因

- `qwen25_7b_hf_8bit`: 在多个任务上存在数据缺失，会导致聚合分析时出现不完整的结果
- 其他变体：同一模型的不同命名格式，确保完全排除

## 实现位置

### 1. `run_mixed_task_analysis.py`

**位置**: `analysis/qe_research/scripts/run_mixed_task_analysis.py`

**修改内容**:

1. 在文件顶部添加模型排除配置（第 31-40 行）：
```python
# ============================================================================
# 模型排除配置
# ============================================================================

# 需要排除的模型（存在数据问题和缺失值）
EXCLUDED_MODELS = [
    'qwen25_7b_hf_8bit',  # 在其他任务上数据有缺失
    'qwen--qwen2.5-7b-instruct:8bit',
    'qwen2.5-7b-instruct:8bit'
]
```

2. 在 `aggregate_quality_scores()` 函数中添加排除逻辑（第 145-157 行）：
```python
# 统一列名：将 'quality' 重命名为 'quality_score'（如果需要）
for task, df in quality_data.items():
    if 'quality' in df.columns and 'quality_score' not in df.columns:
        quality_data[task] = df.rename(columns={'quality': 'quality_score'})

# 排除指定模型
excluded_count = 0
for task, df in quality_data.items():
    original_count = len(df)
    quality_data[task] = df[~df['model'].isin(EXCLUDED_MODELS)]
    excluded_count += original_count - len(quality_data[task])

if verbose and excluded_count > 0:
    print(f"\n⚠ 已排除 {len(EXCLUDED_MODELS)} 个模型: {', '.join(EXCLUDED_MODELS)}")
    print(f"  共排除 {excluded_count} 条数据记录")
```

### 2. `pareto_mixed_task.py`

**位置**: `analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py`

**修改内容**:

1. 在文件顶部添加模型排除配置（第 46-55 行）：
```python
# ============================================================================
# 模型排除配置
# ============================================================================

# 需要排除的模型（存在数据问题和缺失值）
EXCLUDED_MODELS = [
    'qwen25_7b_hf_8bit',  # 在其他任务上数据有缺失
    'qwen--qwen2.5-7b-instruct:8bit',
    'qwen2.5-7b-instruct:8bit'
]
```

2. 在 `aggregate_quality_scores()` 函数中添加相同的排除逻辑

## 工作流程

```
加载质量数据
    ↓
统一列名 (quality → quality_score)
    ↓
排除指定模型 ← EXCLUDED_MODELS
    ↓
聚合质量得分
    ↓
合并能耗和速度数据
    ↓
帕累托前沿分析
```

## 输出示例

运行脚本时会显示排除信息：

```
步骤2: 聚合质量得分
--------------------------------------------------------------------------------
✓ 权重已归一化（总和 = 1.000000）

⚠ 已排除 3 个模型: qwen25_7b_hf_8bit, qwen--qwen2.5-7b-instruct:8bit, qwen2.5-7b-instruct:8bit
  共排除 21 条数据记录

共有 11 个模型

✓ 成功聚合 11 个模型的质量得分
  质量得分范围: [0.xxxx, 0.xxxx]
```

## 与其他脚本的一致性

此实现与以下脚本保持一致：

1. `raw_data_analysis.py` - 原始数据分析
2. `hypothesis_test_metric_tables.py` - 假设检验分析
3. `quality_data_analyzer.py` - 质量数据分析

所有脚本都使用相同的 `EXCLUDED_MODELS` 列表，确保分析结果的一致性。

## 验证方法

运行混合任务分析：

```bash
cd analysis/qe_research/scripts
python run_mixed_task_analysis.py
```

或者：

```bash
cd analysis/qe_research/scripts/pareto_core
python pareto_mixed_task.py
```

检查输出中是否显示模型排除信息，以及最终模型数量是否正确（应该比原始数据少 1 个模型）。

## 注意事项

1. **数据完整性**: 排除模型后，确保剩余模型在所有任务上都有完整数据
2. **权重归一化**: 模型排除不影响任务权重，权重仍然基于所有任务
3. **结果解释**: 在报告中应说明已排除的模型及原因
4. **可扩展性**: 如需排除更多模型，只需在 `EXCLUDED_MODELS` 列表中添加

## 相关文件

- 主脚本：`analysis/qe_research/scripts/run_mixed_task_analysis.py`
- 核心模块：`analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py`
- 列名修复：`analysis/qe_research/scripts/COLUMN_NAME_FIX_SUMMARY.md`
- 绘图修复：`analysis/qe_research/scripts/pareto_core/PLOT_FIX_SUMMARY.md`

## 修复日期

2025-03-08

## 状态

✅ 已实现并测试
