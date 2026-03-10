# Translation 任务 PCA 失败问题修复

> 📅 修复时间: 2026-03-09
> 
> 🐛 问题: Translation 任务在执行 PCA 时报错 "所有行都包含NaN，无法进行PCA"

## 问题描述

### 错误信息

```
✗ 任务 TRANSLATION 失败: 所有行都包含NaN，无法进行PCA
Traceback (most recent call last):
  File "pareto_analysis_all.py", line 267, in <module>
    main()
  File "pareto_analysis_all.py", line 122, in main
    df = load_and_prepare_data()
  File "pareto_analysis_all.py", line 75, in load_and_prepare_data
    quality_df = load_process_quality_data(
  File "shared_functions.py", line 939, in load_process_quality_data
    pca_result_full = processor.apply_pca(n_components=None, normalize_first=True)
  File "process_quality_data.py", line 469, in apply_pca
    raise ValueError("所有行都包含NaN，无法进行PCA")
ValueError: 所有行都包含NaN，无法进行PCA
```

### 根本原因

Translation 任务的质量数据文件 `translation_scores.csv` 包含以下指标：

| 指标 | 状态 |
|------|------|
| bertscore_f1 | ✅ 有效数据 |
| bertscore_precision | ✅ 有效数据 |
| bertscore_recall | ✅ 有效数据 |
| bleu_1 | ✅ 有效数据 |
| bleu_2 | ✅ 有效数据 |
| bleu_4 | ✅ 有效数据 |
| chrf | ✅ 有效数据 |
| **edit_distance** | ❌ **全部 NaN** |
| **edit_similarity** | ❌ **全部 NaN** |
| length_ratio | ✅ 有效数据 |
| **normalized_edit_distance** | ❌ **全部 NaN** |

**问题**: 原代码使用 `data.dropna()` 删除包含 NaN 的行，但由于有3个指标全部是 NaN，导致所有行都被删除。

## 修复方案

### 修改位置

文件: `analysis/qe_research/scripts/pareto_core/process_quality_data.py`

函数: `QualityDataProcessor.apply_pca()` (第 458-469 行)

### 修改前代码

```python
# 处理缺失值：删除包含NaN的行
data_clean = data.dropna()

if len(data_clean) == 0:
    raise ValueError("所有行都包含NaN，无法进行PCA")

if self.verbose:
    print(f"有效样本数: {len(data_clean)}/{len(data)}")
    print(f"特征数量: {len(data_clean.columns)}")
```

### 修改后代码

```python
# 处理缺失值：
# 1. 删除全为NaN的列
data_clean = data.dropna(axis=1, how='all')

if len(data_clean.columns) == 0:
    raise ValueError("所有列都是NaN，无法进行PCA")

# 2. 删除包含NaN的行
data_clean = data_clean.dropna(axis=0)

if len(data_clean) == 0:
    raise ValueError("删除NaN后没有有效样本，无法进行PCA")

if self.verbose:
    removed_cols = set(data.columns) - set(data_clean.columns)
    if removed_cols:
        print(f"⚠️  已删除全为NaN的列: {removed_cols}")
    print(f"有效样本数: {len(data_clean)}/{len(data)}")
    print(f"有效特征数: {len(data_clean.columns)}/{len(data.columns)}")
```

### 修复逻辑

1. **第一步**: 删除全为 NaN 的列 (`axis=1, how='all'`)
   - 移除 `edit_distance`, `edit_similarity`, `normalized_edit_distance`
   
2. **第二步**: 删除包含 NaN 的行 (`axis=0`)
   - 确保剩余数据没有缺失值

3. **增强提示**: 显示被删除的列名，便于调试

## 修复验证

### 测试结果

```python
# 测试 translation 任务
processor = QualityDataProcessor(task_name='translation', use_raw=True, verbose=True)
data = processor.load_quality_data()

# 原始数据
print('原始数据形状:', data.shape)  # (11, 11)
print('NaN统计:')
# edit_distance: 11 NaN
# edit_similarity: 11 NaN  
# normalized_edit_distance: 11 NaN

# 执行 PCA
pca_result = processor.apply_pca(n_components=None, normalize_first=True)

# 输出结果
⚠️  已删除全为NaN的列: {'edit_distance', 'edit_similarity', 'normalized_edit_distance'}
有效样本数: 11/11
有效特征数: 8/11

✓ PCA降维完成
  实际主成分数: 8
  
各主成分解释方差比例:
  PC1: 0.8659 (86.59%)
  PC2: 0.0810 (8.10%)
  PC3: 0.0352 (3.52%)
  ...
```

### 验证通过 ✅

- ✅ 成功删除全为 NaN 的3个指标
- ✅ 保留8个有效指标进行 PCA
- ✅ 所有11个模型样本都参与分析
- ✅ PCA 成功完成，第一主成分解释 86.59% 方差

## 影响范围

### 受益任务

此修复不仅解决了 translation 任务的问题，还提高了所有任务的鲁棒性：

- ✅ **Translation**: 直接修复 PCA 失败问题
- ✅ **其他任务**: 增强对部分指标缺失的容错能力
- ✅ **未来扩展**: 支持新增任务可能存在的指标缺失情况

### 不影响现有功能

- ✅ 对于没有全 NaN 列的任务，行为保持不变
- ✅ 向后兼容，不破坏现有分析流程
- ✅ 增强的错误提示更便于调试

## 后续建议

### 1. 数据质量检查

建议在质量数据生成阶段添加检查：

```python
# 在 create_quality_score_tables.py 中添加
def check_data_quality(df, task_name):
    """检查数据质量"""
    nan_cols = df.columns[df.isna().all()]
    if len(nan_cols) > 0:
        print(f"⚠️  警告: {task_name} 任务中以下指标全部为NaN:")
        for col in nan_cols:
            print(f"  - {col}")
```

### 2. 指标缺失原因调查

需要调查 translation 任务中这3个指标为何全部缺失：

- `edit_distance`: 编辑距离
- `edit_similarity`: 编辑相似度
- `normalized_edit_distance`: 归一化编辑距离

**可能原因**:
- 计算脚本中未实现这些指标
- 数据收集过程中出现错误
- 这些指标不适用于 translation 任务

**建议行动**:
1. 检查 `scripts/create_quality_score_tables.py` 中的指标计算逻辑
2. 确认是否需要为 translation 任务实现这些指标
3. 如果不需要，从指标映射中移除

### 3. 文档更新

更新以下文档以反映此修复：

- ✅ `TRANSLATION_NAN_FIX.md` (本文档)
- [ ] `analysis/qe_research/results/quality_scores/TASK_METRICS_MAPPING.md`
- [ ] `analysis/qe_research/scripts/pareto_core/PCA_FEATURE_COMPLETE.md`

## 相关文件

- 修复文件: `analysis/qe_research/scripts/pareto_core/process_quality_data.py`
- 数据文件: `analysis/qe_research/results/quality_scores/translation_scores.csv`
- 调用脚本: `analysis/qe_research/scripts/pareto_analysis_all.py`
- 共享函数: `analysis/qe_research/scripts/pareto_core/shared_functions.py`

## 测试命令

```bash
# 测试单个任务
python -c "
import sys
sys.path.insert(0, 'analysis/qe_research/scripts')
from pareto_core.process_quality_data import QualityDataProcessor

processor = QualityDataProcessor(task_name='translation', use_raw=True, verbose=True)
data = processor.load_quality_data()
pca_result = processor.apply_pca(n_components=None, normalize_first=True)
print('✓ Translation 任务 PCA 成功!')
"

# 运行完整分析
python analysis/qe_research/scripts/pareto_analysis_all.py
```

## 总结

通过改进 NaN 处理逻辑，成功修复了 translation 任务的 PCA 失败问题。修复方案：

1. ✅ 先删除全为 NaN 的列
2. ✅ 再删除包含 NaN 的行
3. ✅ 增强错误提示和日志

这个修复提高了系统的鲁棒性，使其能够优雅地处理部分指标缺失的情况。

---

*修复完成时间: 2026-03-09*
