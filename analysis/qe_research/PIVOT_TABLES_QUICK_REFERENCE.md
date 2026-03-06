# 透视表快速参考

**生成时间**: 2026-03-06  
**位置**: `analysis/qe_research/results/pivot_tables/`

---

## 表格概览

所有表格采用统一格式：
- **行**: 任务类型 (code, creative, math, multi_turn, qa, reasoning, summary, translation)
- **列**: 模型名称
- **值**: 该模型在该任务上的平均指标值

---

## 6个透视表

### 表1: 平均GPU能耗 (J)
**文件**: `table1_avg_gpu_energy.csv`

显示每个模型在各任务上的平均GPU能耗（焦耳）。

**关键发现**:
- code任务能耗最高（平均1000-3000J）
- summary任务能耗最低（平均50-700J）
- qwen--qwen2.5-7b-instruct:8bit在code任务上能耗最高（7889.15J）
- google--gemma-2b-it:4bit在summary任务上能耗最低（30.89J）

---

### 表2: 平均回答token数量
**文件**: `table2_avg_output_tokens.csv`

显示每个模型在各任务上的平均输出token数量。

**关键发现**:
- translation任务输出最长（平均100-1200 tokens）
- math任务输出较短（平均35-270 tokens）
- qwen3:4b在translation任务上输出最长（1189.0 tokens）
- google--gemma-2b-it:8bit在math任务上输出最短（35.0 tokens）

---

### 表3: 首token延迟 (ms)
**文件**: `table3_ttft.csv`

显示每个模型在各任务上的首token延迟（毫秒）。

**重要说明**: 
- ⚠️ 仅Ollama模型有TTFT数据
- HuggingFace模型显示为N/A（监控未记录first_token事件）

**关键发现**:
- qwen3:8b在code任务上TTFT最长（21884.1ms）
- gemma3:4b在qa/reasoning/summary任务上TTFT最短（约900-970ms）
- deepseek-r1:8b的TTFT普遍较高（6500-8000ms）

---

### 表4: 平均回答时间 (s)
**文件**: `table4_avg_response_time.csv`

显示每个模型在各任务上的平均回答时间（秒）。

**关键发现**:
- code任务耗时最长（平均5-250秒）
- summary任务耗时最短（平均1-30秒）
- qwen--qwen2.5-7b-instruct:8bit在code任务上最慢（246.10s）
- google--gemma-2b-it:4bit在summary任务上最快（0.88s）

---

### 表5: 平均显存占用 (MB)
**文件**: `table5_avg_gpu_mem.csv`

显示每个模型在各任务上的平均显存占用（MB）。

**关键发现**:
- 显存占用主要取决于模型大小，与任务类型关系不大
- microsoft--phi-3-mini-4k-instruct:4bit显存占用最高（约8000MB）
- google--gemma-2b-it:4bit显存占用最低（约2680-3030MB）
- 4bit量化模型显存占用明显低于8bit版本

**模型显存占用排序**（从低到高）:
1. google--gemma-2b-it:4bit: ~2700-3000 MB
2. qwen3:4b: ~3330-3400 MB
3. qwen--qwen2.5-3b-instruct:4bit: ~3470-3650 MB
4. gemma3:4b: ~3745-4030 MB
5. qwen--qwen2.5-3b-instruct:8bit: ~4730-4890 MB
6. deepseek-r1:8b: ~5615-5690 MB
7. qwen3:8b: ~5640-5690 MB
8. google--gemma-2b-it:8bit: ~5255-5768 MB
9. microsoft--phi-3-mini-4k-instruct:8bit: ~4568-5396 MB
10. qwen--qwen2.5-7b-instruct:4bit: ~6547-6826 MB
11. microsoft--phi-3-mini-4k-instruct:4bit: ~3596-8109 MB
12. qwen--qwen2.5-7b-instruct:8bit: ~8123-8170 MB

---

### 表6: 平均GPU占用 (%)
**文件**: `table6_avg_gpu_util.csv`

显示每个模型在各任务上的平均GPU利用率（百分比）。

**关键发现**:
- deepseek-r1:8b和qwen3:8b的GPU利用率最高（80-87%）
- google--gemma-2b-it:4bit的GPU利用率较低（32-42%）
- code和reasoning任务的GPU利用率普遍较高
- summary任务的GPU利用率相对较低

---

## 数据版本说明

每个表格提供两个版本：

1. **格式化版本** (如 `table1_avg_gpu_energy.csv`)
   - 数值已格式化，便于阅读
   - 适合在Excel中查看
   - 适合生成报告

2. **原始版本** (如 `table1_avg_gpu_energy_raw.csv`)
   - 保留原始浮点数
   - 适合进一步计算和分析
   - 适合Python/R等工具处理

---

## 使用示例

### Excel中查看
直接双击CSV文件，用Excel打开即可。

### Python中读取
```python
import pandas as pd

# 读取格式化版本
df = pd.read_csv('analysis/qe_research/results/pivot_tables/table1_avg_gpu_energy.csv', 
                 index_col=0)
print(df)

# 读取原始版本（用于计算）
df_raw = pd.read_csv('analysis/qe_research/results/pivot_tables/table1_avg_gpu_energy_raw.csv', 
                     index_col=0)

# 查看特定任务的能耗
print(df_raw.loc['code'])

# 查看特定模型的能耗
print(df_raw['qwen3:8b'])

# 找出能耗最低的模型（按任务）
print(df_raw.idxmin(axis=1))

# 计算每个模型的平均能耗（跨所有任务）
print(df_raw.mean(axis=0))
```

### 数据分析示例
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 读取多个表格
energy = pd.read_csv('table1_avg_gpu_energy_raw.csv', index_col=0)
tokens = pd.read_csv('table2_avg_output_tokens_raw.csv', index_col=0)
time = pd.read_csv('table4_avg_response_time_raw.csv', index_col=0)

# 计算能效比：每token的能耗
energy_per_token = energy / tokens
print("每token能耗 (J/token):")
print(energy_per_token)

# 可视化：热力图
plt.figure(figsize=(14, 6))
sns.heatmap(energy, annot=True, fmt='.0f', cmap='YlOrRd')
plt.title('GPU能耗热力图 (J)')
plt.tight_layout()
plt.savefig('energy_heatmap.png', dpi=300)
```

---

## 数据说明

### N/A值的含义
- **表3 (TTFT)**: HuggingFace模型未记录first_token事件
- **其他表格**: 该模型-任务组合没有实验数据

### 数据来源
所有数据从以下文件提取：
- `data/{model_name}/experiment_results_*_raw.json`

### 计算方法
- **GPU能耗**: 平均功率 × 持续时间
- **输出token数**: 响应文本的token估算（中文按字符，英文按单词）
- **TTFT**: first_token事件时间 - inference_start事件时间
- **回答时间**: end_timestamp - start_timestamp
- **显存占用**: 监控数据中gpu_mem_mb的平均值
- **GPU占用**: 监控数据中gpu_util的平均值

---

## 重新生成表格

如果数据更新，可以重新生成透视表：

```bash
# 方法1: 直接运行Python脚本
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/create_pivot_tables.py

# 方法2: 使用批处理脚本
analysis\qe_research\scripts\run_pivot_tables.bat
```

---

## 相关文档

- [分析状态总结](ANALYSIS_STATUS_SUMMARY.md)
- [数据管道系统](../数据管道系统.md)
- [指标说明文档](../METRICS_GUIDE.md)
- [透视表汇总报告](results/pivot_tables/pivot_tables_summary.md)

---

**文档维护**: Kiro AI Assistant  
**最后更新**: 2026-03-06
