# 空 DataFrame 错误修复总结

## 问题描述

运行混合任务分析时出现 `ValueError: attempt to get argmax of an empty sequence` 错误。

## 错误信息

```
ValueError: attempt to get argmax of an empty sequence
File "...\shared_functions.py", line 866, in generate_pareto_report
    best_quality_model = df.loc[df['quality'].idxmax()]
```

## 根本原因

**数据缺失导致 DataFrame 为空**：

1. `merge_energy_speed_data()` 函数从多个任务加载能耗和速度数据
2. 某些模型在能耗或速度数据中缺失
3. `df.dropna()` 删除所有包含 NaN 的行
4. 如果所有模型都缺少至少一个数据点，DataFrame 变为空
5. 空 DataFrame 调用 `idxmax()` 导致错误

## 问题链

```
质量数据加载 (11 个模型)
    ↓
合并能耗/速度数据
    ↓
某些模型缺少能耗或速度数据 → NaN
    ↓
df.dropna() 删除包含 NaN 的行
    ↓
所有模型都有缺失 → DataFrame 为空
    ↓
generate_pareto_report() 尝试 df['quality'].idxmax()
    ↓
ValueError: empty sequence
```

## 解决方案

### 1. 增强 `merge_energy_speed_data()` 函数

**位置**: `analysis/qe_research/scripts/run_mixed_task_analysis.py` (第 220-270 行)

**修改内容**:

添加详细的数据缺失诊断信息：

```python
def merge_energy_speed_data(quality_df: pd.DataFrame, 
                            tasks: List[str],
                            verbose: bool = True) -> pd.DataFrame:
    """合并能耗和速度数据"""
    merged_data = []
    
    for _, row in quality_df.iterrows():
        model = row['model']
        quality = row['quality']
        
        energies = []
        speeds = []
        
        for task in tasks:
            energy_dict, speed_dict = load_energy_speed_data(
                task, 
                DATA_PATHS['energy'], 
                DATA_PATHS['speed']
            )
            
            if model in energy_dict:
                energies.append(energy_dict[model])
            if model in speed_dict:
                speeds.append(speed_dict[model])
        
        avg_energy = np.mean(energies) if energies else np.nan
        avg_speed = np.mean(speeds) if speeds else np.nan
        
        merged_data.append({
            'model': model,
            'quality': quality,
            'energy': avg_energy,
            'speed': avg_speed
        })
    
    df = pd.DataFrame(merged_data)
    
    # 显示缺失数据信息
    if verbose:
        missing_energy = df['energy'].isna().sum()
        missing_speed = df['speed'].isna().sum()
        if missing_energy > 0 or missing_speed > 0:
            print(f"\n⚠ 数据缺失情况:")
            print(f"  缺失能耗数据: {missing_energy} 个模型")
            print(f"  缺失速度数据: {missing_speed} 个模型")
            if missing_energy > 0:
                missing_models = df[df['energy'].isna()]['model'].tolist()
                print(f"  缺失能耗的模型: {', '.join(missing_models)}")
            if missing_speed > 0:
                missing_models = df[df['speed'].isna()]['model'].tolist()
                print(f"  缺失速度的模型: {', '.join(missing_models)}")
    
    # 删除包含 NaN 的行
    original_count = len(df)
    df = df.dropna()
    dropped_count = original_count - len(df)
    
    if verbose:
        if dropped_count > 0:
            print(f"\n⚠ 由于数据缺失，排除了 {dropped_count} 个模型")
        print(f"\n✓ 合并后数据: {len(df)} 个模型")
        if len(df) > 0:
            print(f"  能耗范围: [{df['energy'].min():.6f}, {df['energy'].max():.6f}] J/token")
            print(f"  速度范围: [{df['speed'].min():.2f}, {df['speed'].max():.2f}] tokens/s")
        else:
            print(f"  ✗ 警告: 没有完整数据的模型！")
    
    return df
```

### 2. 增强 `generate_pareto_report()` 函数

**位置**: `analysis/qe_research/scripts/pareto_core/shared_functions.py` (第 862-880 行)

**修改内容**:

添加空 DataFrame 检查：

```python
# 5. 推荐配置
f.write("## 5. 推荐配置\n\n")

# 检查 DataFrame 是否为空
if len(df) == 0:
    f.write("⚠ **警告**: 没有可用的模型数据，无法生成推荐配置。\n\n")
    f.write("可能原因：\n")
    f.write("- 所有模型都缺少能耗或速度数据\n")
    f.write("- 模型被排除列表过滤\n")
    f.write("- 数据加载失败\n\n")
else:
    # 找出最佳模型
    best_quality_model = df.loc[df['quality'].idxmax()]
    best_speed_model = df.loc[df['speed'].idxmax()]
    best_energy_model = df.loc[df['energy'].idxmin()]
    # ... 继续处理
```

## 输出示例

### 正常情况

```
步骤3: 合并能耗和速度数据
--------------------------------------------------------------------------------

✓ 合并后数据: 11 个模型
  能耗范围: [0.000123, 0.000456] J/token
  速度范围: [12.34, 56.78] tokens/s
```

### 数据缺失情况

```
步骤3: 合并能耗和速度数据
--------------------------------------------------------------------------------

⚠ 数据缺失情况:
  缺失能耗数据: 3 个模型
  缺失速度数据: 2 个模型
  缺失能耗的模型: model_a, model_b, model_c
  缺失速度的模型: model_d, model_e

⚠ 由于数据缺失，排除了 5 个模型

✓ 合并后数据: 6 个模型
  能耗范围: [0.000123, 0.000456] J/token
  速度范围: [12.34, 56.78] tokens/s
```

### 所有数据缺失情况

```
步骤3: 合并能耗和速度数据
--------------------------------------------------------------------------------

⚠ 数据缺失情况:
  缺失能耗数据: 11 个模型
  缺失速度数据: 11 个模型
  缺失能耗的模型: model_a, model_b, ..., model_k
  缺失速度的模型: model_a, model_b, ..., model_k

⚠ 由于数据缺失，排除了 11 个模型

✓ 合并后数据: 0 个模型
  ✗ 警告: 没有完整数据的模型！
```

## 可能的原因

1. **模型名称不匹配**: 质量数据中的模型名称与能耗/速度数据中的不一致
2. **数据文件缺失**: 某些任务的能耗或速度数据文件不存在
3. **数据格式问题**: CSV 文件格式不正确或列名不匹配
4. **模型被过度排除**: `EXCLUDED_MODELS` 列表排除了太多模型

## 调试步骤

1. **检查模型名称一致性**:
   ```python
   # 在质量数据中
   print("质量数据模型:", quality_df['model'].tolist())
   
   # 在能耗数据中
   energy_dict, _ = load_energy_speed_data('code', ...)
   print("能耗数据模型:", list(energy_dict.keys()))
   ```

2. **检查数据文件是否存在**:
   ```bash
   ls analysis/qe_research/results/metric_tables/*_energy.csv
   ls analysis/qe_research/results/metric_tables/*_speed.csv
   ```

3. **检查数据加载函数**:
   - 确认 `load_energy_speed_data()` 正确读取数据
   - 确认模型名称映射正确

4. **临时禁用 dropna**:
   ```python
   # 临时注释掉 dropna 查看原始数据
   # df = df.dropna()
   print(df)  # 查看哪些模型有 NaN
   ```

## 预防措施

1. **数据完整性检查**: 在分析开始前验证所有必需的数据文件存在
2. **模型名称标准化**: 统一所有数据源中的模型命名规范
3. **优雅降级**: 当数据不完整时，提供有意义的错误信息而不是崩溃
4. **数据备份**: 保留原始数据的备份以便调试

## 相关文件

- 主脚本：`analysis/qe_research/scripts/run_mixed_task_analysis.py`
- 共享函数：`analysis/qe_research/scripts/pareto_core/shared_functions.py`
- 数据路径：`analysis/qe_research/results/metric_tables/`

## 修复日期

2025-03-08

## 状态

✅ 已修复 - 添加了详细的诊断信息和空 DataFrame 检查
