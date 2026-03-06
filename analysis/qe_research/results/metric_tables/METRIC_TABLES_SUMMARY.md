# 模型性能指标对比表格 - 生成总结

**生成时间**: 2026-03-06  
**数据来源**: 446个实验，12个模型，8种任务类型

---

## 生成的表格

本次成功生成了6个CSV表格，以任务类型为行标题、模型名称为列标题的矩阵格式：

### 表1: 平均GPU能耗 (01_avg_gpu_energy.csv)

**单位**: 焦耳 (J)

展示每个模型在不同任务下的平均GPU能耗。能耗越低表示模型越节能。

**关键发现**:
- 最节能模型（code任务）: gemma3:4b (336.91 J)
- 最耗能模型（code任务）: qwen--qwen2.5-7b-instruct:8bit (7907.65 J)
- 能耗差异显著，最大相差约23倍

### 表2: 平均回答token数量 (02_avg_output_tokens.csv)

**单位**: tokens

展示每个模型在不同任务下生成的平均token数量。

**关键发现**:
- code任务生成token最多（平均600-800 tokens）
- summary任务生成token最少（平均20-230 tokens）
- 不同模型在相同任务下的输出长度差异较大

### 表3: 首token延迟 (03_ttft.csv)

**单位**: 毫秒 (ms)

展示模型从接收请求到生成第一个token的延迟时间。

**数据覆盖**: 仅15.7%的实验有TTFT数据（主要是Ollama模型）

**关键发现**:
- 最快响应: gemma3:4b (平均900-1900 ms)
- 最慢响应: qwen3:8b 在code任务 (21884.1 ms)
- HuggingFace模型缺少TTFT数据（需要修复监控代码）

### 表4: 平均回答时间 (04_avg_response_time.csv)

**单位**: 秒 (s)

展示每个模型完成一次回答的平均时间。

**关键发现**:
- 最快模型: gemma3:4b (平均2-6秒)
- 最慢模型: qwen--qwen2.5-7b-instruct:8bit (平均12-246秒)
- code任务通常需要更长的回答时间

### 表5: 平均显存占用 (05_avg_gpu_memory.csv)

**单位**: MB

展示每个模型运行时的平均显存占用。

**关键发现**:
- 最小显存: google--gemma-2b-it:4bit (约2684-3031 MB)
- 最大显存: qwen--qwen2.5-7b-instruct:8bit (约8123-8171 MB)
- 4bit量化模型显存占用明显低于8bit模型

### 表6: 平均GPU占用率 (06_avg_gpu_utilization.csv)

**单位**: %

展示每个模型运行时的平均GPU利用率。

**关键发现**:
- 最高利用率: deepseek-r1:8b 和 qwen3:8b (80-87%)
- 最低利用率: google--gemma-2b-it (27-42%)
- 较大模型通常有更高的GPU利用率

---

## 数据统计

### 数据覆盖情况

| 指标 | 覆盖率 | 说明 |
|------|--------|------|
| GPU能耗 | 100% | 所有实验都有能耗数据 |
| 输出tokens | 100% | 所有实验都有token统计 |
| TTFT | 15.7% | 仅Ollama模型有数据 |
| 回答时间 | 100% | 所有实验都有时间数据 |
| 显存占用 | 100% | 所有实验都有显存数据 |
| GPU占用率 | 100% | 所有实验都有利用率数据 |

### 模型列表

1. deepseek-r1:8b (Ollama, Q4_K_M)
2. gemma3:4b (Ollama, Q4_K_M)
3. google--gemma-2b-it:4bit (HF, 4bit)
4. google--gemma-2b-it:8bit (HF, 8bit)
5. microsoft--phi-3-mini-4k-instruct:4bit (HF, 4bit)
6. microsoft--phi-3-mini-4k-instruct:8bit (HF, 8bit)
7. qwen--qwen2.5-3b-instruct:4bit (HF, 4bit)
8. qwen--qwen2.5-3b-instruct:8bit (HF, 8bit)
9. qwen--qwen2.5-7b-instruct:4bit (HF, 4bit)
10. qwen--qwen2.5-7b-instruct:8bit (HF, 8bit) - 仅6个实验
11. qwen3:4b (Ollama, Q4_K_M)
12. qwen3:8b (Ollama, Q4_K_M)

### 任务类型

1. code - 代码生成
2. creative - 创意写作
3. math - 数学推理
4. multi_turn - 多轮对话
5. qa - 问答
6. reasoning - 逻辑推理
7. summary - 摘要生成
8. translation - 翻译

---

## 使用示例

### Python读取和分析

```python
import pandas as pd
import matplotlib.pyplot as plt

# 读取能耗数据
energy_df = pd.read_csv('01_avg_gpu_energy.csv', index_col=0)

# 查看code任务的能耗排名
code_energy = energy_df.loc['code'].sort_values()
print("Code任务能耗排名（从低到高）:")
print(code_energy)

# 绘制能耗对比图
energy_df.T.plot(kind='bar', figsize=(14, 6))
plt.title('各模型在不同任务下的GPU能耗对比')
plt.xlabel('模型')
plt.ylabel('能耗 (J)')
plt.legend(title='任务类型', bbox_to_anchor=(1.05, 1))
plt.tight_layout()
plt.savefig('energy_comparison.png', dpi=300)
```

### Excel分析

1. 在Excel中打开CSV文件
2. 使用条件格式突出显示最优/最差值
3. 创建数据透视表进行多维分析
4. 生成图表进行可视化对比

---

## 关键洞察

### 能效比分析

1. **小模型优势**: gemma3:4b 和 google--gemma-2b-it:4bit 在能耗和速度上表现优异
2. **量化效果**: 4bit量化模型在显存占用上明显优于8bit模型
3. **任务差异**: code和multi_turn任务消耗更多资源，summary任务最节能
4. **性能权衡**: 大模型（7B参数）虽然能耗高，但可能在质量上有优势

### 优化建议

1. **资源受限场景**: 推荐使用gemma3:4b或gemma-2b-it:4bit
2. **平衡场景**: 推荐使用qwen2.5-3b-instruct:4bit或phi-3-mini:4bit
3. **高质量需求**: 可考虑qwen2.5-7b-instruct:4bit（需权衡能耗）
4. **TTFT优化**: HuggingFace模型需要添加首token事件监控

---

## 后续工作

### 数据完善

1. 修复HuggingFace模型的TTFT监控
2. 补充qwen--qwen2.5-7b-instruct:8bit的完整实验数据
3. 添加质量指标与效率指标的关联分析

### 分析扩展

1. 计算质效比（Quality-Efficiency Ratio）
2. 生成能效评级（A-F等级）
3. 创建模型推荐决策树
4. 添加成本分析（基于云服务定价）

### 可视化增强

1. 创建交互式仪表板
2. 生成雷达图对比多维指标
3. 绘制帕累托前沿（Pareto Frontier）
4. 制作热力图展示模型-任务适配度

---

## 文件清单

- `01_avg_gpu_energy.csv` - GPU能耗表
- `02_avg_output_tokens.csv` - 输出token数表
- `03_ttft.csv` - 首token延迟表
- `04_avg_response_time.csv` - 回答时间表
- `05_avg_gpu_memory.csv` - 显存占用表
- `06_avg_gpu_utilization.csv` - GPU占用率表
- `README.md` - 使用说明
- `METRIC_TABLES_SUMMARY.md` - 本文档

---

## 生成信息

- **脚本**: `analysis/qe_research/scripts/create_metric_tables.py`
- **运行脚本**: `analysis/qe_research/scripts/run_create_metric_tables.bat`
- **数据源**: `data/*/experiment_results_*_summary.json`
- **生成时间**: 2026-03-06 13:43:35
- **Python版本**: 3.10
- **依赖**: pandas, numpy

---

**维护者**: Kiro AI Assistant  
**最后更新**: 2026-03-06
