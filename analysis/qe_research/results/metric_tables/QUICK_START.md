# 快速开始 - 模型性能指标对比表格

## 一键运行

### Windows批处理

```bash
# 直接双击运行
analysis\qe_research\scripts\run_create_metric_tables.bat
```

### 命令行运行

```bash
# 激活环境
conda activate bartscore

# 设置编码
set PYTHONUTF8=1

# 运行脚本
python analysis/qe_research/scripts/create_metric_tables.py
```

---

## 查看结果

生成的6个CSV文件位于: `analysis/qe_research/results/metric_tables/`

### 在Excel中打开

1. 打开Excel
2. 文件 → 打开 → 选择CSV文件
3. 选择UTF-8编码
4. 查看数据表格

### 在Python中分析

```python
import pandas as pd

# 读取能耗数据
df = pd.read_csv('analysis/qe_research/results/metric_tables/01_avg_gpu_energy.csv', 
                 index_col=0)

# 查看code任务的能耗
print(df.loc['code'])

# 查看qwen3:8b模型的能耗
print(df['qwen3:8b'])

# 找出最节能的模型（code任务）
print(df.loc['code'].idxmin())
print(f"最低能耗: {df.loc['code'].min():.2f} J")
```

---

## 表格说明

| 文件名 | 指标 | 单位 | 说明 |
|--------|------|------|------|
| 01_avg_gpu_energy.csv | GPU能耗 | 焦耳(J) | 越低越好 |
| 02_avg_output_tokens.csv | 输出token数 | tokens | 反映输出长度 |
| 03_ttft.csv | 首token延迟 | 毫秒(ms) | 越低越好，仅部分模型有数据 |
| 04_avg_response_time.csv | 回答时间 | 秒(s) | 越低越好 |
| 05_avg_gpu_memory.csv | 显存占用 | MB | 越低越好 |
| 06_avg_gpu_utilization.csv | GPU占用率 | % | 反映GPU利用效率 |

---

## 快速分析示例

### 找出最节能的模型

```python
import pandas as pd

energy = pd.read_csv('01_avg_gpu_energy.csv', index_col=0)

# 每个任务的最节能模型
for task in energy.index:
    best_model = energy.loc[task].idxmin()
    best_value = energy.loc[task].min()
    print(f"{task}: {best_model} ({best_value:.2f} J)")
```

### 对比4bit vs 8bit量化

```python
import pandas as pd

memory = pd.read_csv('05_avg_gpu_memory.csv', index_col=0)

# 筛选4bit和8bit模型
bit4_cols = [col for col in memory.columns if '4bit' in col]
bit8_cols = [col for col in memory.columns if '8bit' in col]

print("4bit模型平均显存:", memory[bit4_cols].mean().mean())
print("8bit模型平均显存:", memory[bit8_cols].mean().mean())
```

### 生成能耗排名

```python
import pandas as pd

energy = pd.read_csv('01_avg_gpu_energy.csv', index_col=0)

# 计算每个模型的平均能耗
avg_energy = energy.mean().sort_values()

print("模型能耗排名（从低到高）:")
for i, (model, value) in enumerate(avg_energy.items(), 1):
    print(f"{i}. {model}: {value:.2f} J")
```

---

## 可视化示例

### 绘制能耗对比图

```python
import pandas as pd
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
energy = pd.read_csv('01_avg_gpu_energy.csv', index_col=0)

# 绘制热力图
import seaborn as sns

plt.figure(figsize=(14, 6))
sns.heatmap(energy, annot=True, fmt='.0f', cmap='YlOrRd', cbar_kws={'label': '能耗 (J)'})
plt.title('各模型在不同任务下的GPU能耗热力图', fontsize=14, fontweight='bold')
plt.xlabel('模型', fontsize=12)
plt.ylabel('任务类型', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('energy_heatmap.png', dpi=300)
plt.show()
```

### 绘制性能对比雷达图

```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 读取多个指标
energy = pd.read_csv('01_avg_gpu_energy.csv', index_col=0)
time = pd.read_csv('04_avg_response_time.csv', index_col=0)
memory = pd.read_csv('05_avg_gpu_memory.csv', index_col=0)

# 选择一个任务和几个模型
task = 'code'
models = ['gemma3:4b', 'qwen3:8b', 'deepseek-r1:8b']

# 归一化数据（越小越好的指标取倒数）
data = []
for model in models:
    data.append([
        1 / energy.loc[task, model],  # 能耗（倒数）
        1 / time.loc[task, model],    # 时间（倒数）
        1 / memory.loc[task, model],  # 显存（倒数）
    ])

# 绘制雷达图
categories = ['能效', '速度', '显存效率']
N = len(categories)

angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))

for i, model in enumerate(models):
    values = data[i]
    values += values[:1]
    ax.plot(angles, values, 'o-', linewidth=2, label=model)
    ax.fill(angles, values, alpha=0.25)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=12)
ax.set_ylim(0, max([max(d) for d in data]) * 1.1)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
ax.set_title(f'{task}任务 - 模型性能对比', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig('performance_radar.png', dpi=300)
plt.show()
```

---

## 常见问题

### Q: 为什么有些单元格是空的（NaN）？

A: 表示该模型-任务组合没有实验数据。例如qwen--qwen2.5-7b-instruct:8bit只有6个实验，部分任务没有数据。

### Q: 为什么TTFT表格数据很少？

A: TTFT（首token延迟）仅在Ollama模型中有完整记录，HuggingFace模型的监控代码需要修复。

### Q: 如何选择最优模型？

A: 需要综合考虑多个指标：
- 资源受限：选择gemma3:4b或gemma-2b-it:4bit
- 平衡性能：选择qwen2.5-3b-instruct:4bit
- 高质量需求：选择qwen2.5-7b-instruct:4bit（需权衡能耗）

### Q: 数据是如何计算的？

A: 所有数值都是该模型-任务组合下多次实验的平均值。例如gemma3:4b在code任务下有5次实验，表格中显示的是这5次的平均能耗。

---

## 相关文档

- [详细总结](METRIC_TABLES_SUMMARY.md) - 完整的数据分析和洞察
- [使用说明](README.md) - 基础使用指南
- [分析状态](../../ANALYSIS_STATUS_SUMMARY.md) - 整体分析进度

---

**最后更新**: 2026-03-06
