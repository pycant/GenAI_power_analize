# 模型映射修复总结

## 问题描述

运行 `run_mixed_task_analysis.py` 时出现以下警告：

```
⚠ 数据缺失情况:
  缺失能耗数据: 11 个模型
  缺失速度数据: 11 个模型
  缺失能耗的模型: deepseek_8b_ol_q4km, gemma_2b_hf_4bit, gemma_2b_hf_8bit, 
                   gemma_4b_ol_q4km, phi3_4b_hf_4bit, phi3_4b_hf_8bit, 
                   qwen25_3b_hf_4bit, qwen25_3b_hf_8bit, qwen25_7b_hf_4bit, 
                   qwen_4b_ol_q4km, qwen_8b_ol_q4km
⚠ 由于数据缺失，排除了 11 个模型
```

## 根本原因

`run_mixed_task_analysis.py` 中的 `merge_energy_speed_data` 函数（第220-289行）**没有使用 MODEL_MAPPING** 进行模型名称转换。

### 问题细节

1. **CSV文件中的列名格式**（完整名称）：
   - `deepseek-r1:8b`
   - `google--gemma-2b-it:4bit`
   - `microsoft--phi-3-mini-4k-instruct:4bit`
   - `qwen--qwen2.5-3b-instruct:4bit`

2. **质量数据中的模型名格式**（短名称）：
   - `deepseek_8b_ol_q4km`
   - `gemma_2b_hf_4bit`
   - `phi3_4b_hf_4bit`
   - `qwen25_3b_hf_4bit`

3. **问题代码**：
   ```python
   def merge_energy_speed_data(quality_df, tasks, verbose=True):
       for _, row in quality_df.iterrows():
           model = row['model']  # 短名称，如 'gemma_2b_hf_4bit'
           
           for task in tasks:
               energy_dict, speed_dict = load_energy_speed_data(...)
               
               # ❌ 问题：直接用短名称查找，但字典的键是完整名称
               if model in energy_dict:
                   energies.append(energy_dict[model])
               if model in speed_dict:
                   speeds.append(speed_dict[model])
   ```

4. **MODEL_MAPPING 的作用**：
   ```python
   MODEL_MAPPING = {
       'gemma_2b_hf_4bit': 'google--gemma-2b-it:4bit',
       'phi3_4b_hf_4bit': 'microsoft--phi-3-mini-4k-instruct:4bit',
       # ... 其他映射
   }
   ```

## 解决方案

修改 `merge_energy_speed_data` 函数，添加模型名称转换逻辑：

```python
def merge_energy_speed_data(quality_df: pd.DataFrame, 
                            tasks: List[str],
                            verbose: bool = True) -> pd.DataFrame:
    """合并能耗和速度数据"""
    merged_data = []
    
    for _, row in quality_df.iterrows():
        model = row['model']
        quality = row['quality']
        
        # ✓ 修复：使用 MODEL_MAPPING 转换模型名称
        model_full = MODEL_MAPPING.get(model)
        if not model_full:
            if verbose:
                print(f"⚠ 警告: 模型 '{model}' 不在 MODEL_MAPPING 中，跳过")
            continue
        
        energies = []
        speeds = []
        
        for task in tasks:
            energy_dict, speed_dict = load_energy_speed_data(
                task, 
                DATA_PATHS['energy'], 
                DATA_PATHS['speed']
            )
            
            # ✓ 修复：使用完整名称查找
            if model_full in energy_dict:
                energies.append(energy_dict[model_full])
            if model_full in speed_dict:
                speeds.append(speed_dict[model_full])
        
        # ... 后续处理
```

## 验证结果

运行测试脚本 `test_model_mapping_fix.py`：

```
✓ 所有模型都能正确映射！
  找到的模型: 12/12
  缺失的模型: 0/12
```

所有12个模型（包括之前缺失的11个HuggingFace模型）现在都能正确找到能耗和速度数据。

## 影响范围

- **修复文件**: `analysis/qe_research/scripts/run_mixed_task_analysis.py`
- **修复函数**: `merge_energy_speed_data` (第220-289行)
- **受益分析**: 混合任务帕累托前沿分析现在可以包含所有12个模型

## 相关文件

- 配置文件: `analysis/qe_research/scripts/pareto_core/config.py`
- 数据文件: 
  - `analysis/qe_research/results/derived_metrics/07_avg_token_speed.csv`
  - `analysis/qe_research/results/derived_metrics/08_energy_per_token.csv`
- 测试脚本: `analysis/qe_research/scripts/test_model_mapping_fix.py`

## 注意事项

1. **编码问题**: 在Windows终端运行时需要设置 `$env:PYTHONUTF8=1` 避免中文乱码
2. **一致性**: 其他使用能耗/速度数据的脚本（如 `pareto_mixed_task.py`）已经正确使用了 `merge_quality_metrics` 函数，该函数内置了模型映射逻辑
3. **最佳实践**: 建议统一使用 `pareto_core.merge_quality_metrics` 函数处理数据合并，避免重复实现

## 修复日期

2025-03-09

## 修复人员

Kiro AI Assistant
