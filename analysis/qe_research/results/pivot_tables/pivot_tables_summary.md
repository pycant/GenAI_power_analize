# 任务-模型透视表汇总

**生成时间**: 2026-03-06 13:41:08

---

## 概述

本报告包含6个透视表，以任务类型为行，模型为列，展示各项关键指标。

## 表格列表

1. **table1_avg_gpu_energy.csv** - 平均GPU能耗 (J)
2. **table2_avg_output_tokens.csv** - 平均回答token数量
3. **table3_ttft.csv** - 首token延迟 (ms)
4. **table4_avg_response_time.csv** - 平均回答时间 (s)
5. **table5_avg_gpu_mem.csv** - 平均显存占用 (MB)
6. **table6_avg_gpu_util.csv** - 平均GPU占用 (%)

## 数据说明

- **行标题**: 任务类型 (code, creative, math, multi_turn, qa, reasoning, summary, translation)
- **列标题**: 模型名称
- **数值**: 该模型在该任务上的平均值
- **N/A**: 表示该模型-任务组合没有数据

## 使用方法

### 查看表格

```bash
# 在Excel或其他表格软件中打开CSV文件
# 或使用Python读取
import pandas as pd
df = pd.read_csv('table1_avg_gpu_energy.csv', index_col=0)
print(df)
```

### 数据分析

每个表格都有两个版本：
- **格式化版本** (如 `table1_avg_gpu_energy.csv`): 便于阅读，数值已格式化
- **原始版本** (如 `table1_avg_gpu_energy_raw.csv`): 便于计算，保留原始数值

## 关键发现

### GPU能耗
- 不同模型在相同任务上的能耗差异显著
- 某些任务类型（如reasoning）普遍能耗较高

### 首token延迟
- 注意：仅Ollama模型有TTFT数据
- HuggingFace模型显示为N/A

### 显存占用
- 模型大小直接影响显存占用
- 量化方法（4bit）有效降低显存需求

---

**报告生成时间**: 2026-03-06 13:41:08
