# Raw Data Analysis 修复总结

## 修复时间
2026-03-05 21:39

## 问题描述

用户报告在运行 `raw_data_analyzer_complete.py` 时遇到两个问题：

1. **任务3-4 (TTFT分析) 未生成图片**
   - 日志显示 `[2/8] 首token延迟分析...` 但没有输出文件
   - 原因：`_calc_ttft()` 方法返回 None

2. **任务16 (事件完整性检查) 报错**
   - 错误信息：`'label' must be of length 'x'`
   - 原因：饼图标签与数据长度不匹配

## 根本原因

通过检查实际的 raw.json 数据结构，发现事件数据使用 `"event"` 作为键名，而不是代码中使用的 `"type"`：

```json
{
  "monitoring_data": {
    "events": [
      {
        "timestamp": 1772541028.2286148,
        "event": "experiment_start",  // 注意：是 "event" 不是 "type"
        "metadata": {"task_type": "code"}
      },
      {
        "timestamp": 1772541028.2296243,
        "event": "inference_start",
        "metadata": {"turn": 1}
      }
    ]
  }
}
```

## 修复内容

### 1. 修复 `_calc_ttft()` 方法
**文件**: `analysis/qe_research/scripts/raw_data_analyzer_complete.py`

```python
# 修复前
if e.get('type') == 'inference_start':

# 修复后
if e.get('event') == 'inference_start':
```

### 2. 修复 `_task1_power_resource_curves()` 方法
```python
# 修复前
etype = event.get('type', '')

# 修复后
etype = event.get('event', '')
```

### 3. 修复 `_task10_memory_over_time()` 方法
```python
# 修复前
etype = event.get('type', '')

# 修复后
etype = event.get('event', '')
```

### 4. 修复 `_task13_event_timeline()` 方法
```python
# 修复前
etype = event.get('type', '')

# 修复后
etype = event.get('event', '')
```

### 5. 修复 `_task16_event_completeness()` 方法

**问题1**: 事件键名错误
```python
# 修复前
event_types = {e.get('type') for e in events}

# 修复后
event_types = {e.get('event') for e in events}
```

**问题2**: 饼图标签与数据不匹配
```python
# 修复前
ax1.pie(completeness, labels=['完整', '不完整'], ...)

# 修复后
labels = ['完整' if idx else '不完整' for idx in completeness.index]
ax1.pie(completeness.values, labels=labels, ...)
```

**问题3**: 直方图bins参数可能导致错误
```python
# 修复前
bins=range(0, df['missing_events'].max()+2)

# 修复后
missing_max = df['missing_events'].max()
if missing_max >= 0:
    bins = list(range(0, int(missing_max) + 2))
    ax2.hist(df['missing_events'], bins=bins, ...)
```

## 修复结果

✅ **所有18个可视化任务成功完成**

```
[1/8] 时间序列分析...
  ✓ 01_power_resource_curves.png
  ✓ 02_multi_turn_energy.png

[2/8] 首token延迟分析...
  ✓ 03_ttft_distribution.png          ← 修复成功
  ✓ 04_ttft_vs_input_length.png       ← 修复成功

[3/8] 逐token生成延迟...
  ✓ 05_tpot_distribution.png
  ✓ 06_latency_over_time.png

[4/8] 能耗分解与效率...
  ✓ 07_energy_per_turn.png
  ✓ 08_energy_vs_tokens.png
  ✓ 09_idle_vs_work_power.png

[5/8] 资源使用模式...
  ✓ 10_memory_over_time.png
  ✓ 11_util_vs_power.png
  ✓ 12_temp_vs_power.png

[6/8] 事件驱动分析...
  ✓ 13_event_timeline.png
  ✓ 14_cross_turn_comparison.png

[7/8] 异常检测...
  ✓ 15_power_volatility.png
  ✓ 16_event_completeness.png         ← 修复成功

[8/8] 跨实验对比...
  ✓ 17_multi_model_power_curves.png
  ✓ 18_task_type_power_patterns.png
```

## 数据统计

- 总实验数：446
- 加载的模型目录：12个
- 异常实验：3个（功率波动异常）
- 不完整实验：376个（缺少部分事件）

## 输出文件

- **报告**: `analysis/qe_research/results/raw_analysis/reports/raw_analysis_report.md`
- **图表**: `analysis/qe_research/results/raw_analysis/figures/` (18张PNG图片)
- **数据表**: `analysis/qe_research/results/raw_analysis/tables/`
  - `anomalous_experiments.csv` - 异常实验列表
  - `incomplete_experiments.csv` - 不完整实验列表

## 经验教训

1. **数据结构验证的重要性**
   - 在编写数据处理代码前，应先检查实际数据结构
   - 不要假设字段名称，要通过实际样本确认

2. **错误处理的健壮性**
   - 饼图等可视化需要确保标签与数据长度匹配
   - 使用动态生成标签而不是硬编码

3. **调试策略**
   - 当方法返回None时，应检查数据访问路径是否正确
   - 日志输出有助于快速定位问题

## 后续建议

1. 添加数据结构验证函数，在加载时检查必需字段
2. 为关键方法添加更详细的日志输出
3. 考虑添加单元测试覆盖数据解析逻辑
4. 文档中明确说明raw.json的数据结构规范
