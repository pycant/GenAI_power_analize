# 模型性能指标对比表格

**生成时间**: 2026-03-06 13:43:35

---

## 表格说明

本目录包含6个CSV表格，以任务类型为行、模型名称为列的矩阵格式展示各项性能指标。

### 表格列表

1. **01_avg_gpu_energy.csv** - 平均GPU能耗 (焦耳)
2. **02_avg_output_tokens.csv** - 平均回答token数量
3. **03_ttft.csv** - 首token延迟 (毫秒)
4. **04_avg_response_time.csv** - 平均回答时间 (秒)
5. **05_avg_gpu_memory.csv** - 平均显存占用 (MB)
6. **06_avg_gpu_utilization.csv** - 平均GPU占用率 (%)

### 数据来源

- 数据源: `data/*/experiment_results_*_summary.json` 和 `*_raw.json`
- 实验总数: 446
- 模型数量: 12
- 任务类型: 8

### 使用方法

```python
import pandas as pd

# 读取表格
df = pd.read_csv('01_avg_gpu_energy.csv', index_col=0)

# 查看特定任务的能耗
print(df.loc['code'])

# 查看特定模型的能耗
print(df['qwen3:8b'])
```

### 注意事项

- 表格中的NaN值表示该模型-任务组合没有数据
- 首token延迟(TTFT)仅在部分Ollama模型中可用
- 所有数值均为该模型-任务组合下多次实验的平均值

---

**生成脚本**: `analysis/qe_research/scripts/create_metric_tables.py`
