# 帕累托前沿分析快速开始

## 🚀 5分钟快速上手

### 已完成的任务：Reasoning ✅

```bash
# 查看Reasoning任务的分析结果
cd analysis/qe_research/results/pareto_analysis/reasoning

# 主要文件：
# - pareto_metrics_summary.md（定量指标）
# - pareto_robustness_report.md（稳健性验证）
# - COMPLETION_SUMMARY.md（完成总结）
```

**核心结论**：gemma_4b_ol_q4km 是最佳综合配置 ⭐⭐⭐⭐⭐

---

## 📋 分析新任务的3个步骤

### 步骤1：准备数据

创建包含以下列的CSV文件：
- `model`：模型名称
- 质量维度列（如`correctness`, `completeness`等）
- `energy`：能耗（焦耳）
- `speed`：速度（tokens/s）

### 步骤2：计算熵权法质量得分

```python
import pandas as pd
import numpy as np

# 加载数据
df = pd.read_csv('your_data.csv')

# 质量维度列
quality_cols = ['correctness', 'completeness', 'rigor', 'clarity', 'efficiency']

# 标准化
data_norm = (df[quality_cols] - df[quality_cols].min()) / (df[quality_cols].max() - df[quality_cols].min())

# 计算熵
prob = data_norm / data_norm.sum()
entropy = -np.sum(prob * np.log(prob + 1e-10), axis=0) / np.log(len(df))

# 计算权重
weights = (1 - entropy) / (1 - entropy).sum()

# 计算加权质量
df['quality_normalized'] = (data_norm * weights).sum(axis=1)

# 保存
df.to_csv('merged_data.csv', index=False)
```

### 步骤3：运行分析

```bash
# 修改pareto_metrics_calculator.py中的数据路径
# 然后运行：
python analysis/qe_research/scripts/pareto_metrics_calculator.py
python analysis/qe_research/scripts/pareto_robustness_analyzer.py
```

---

## 📊 核心指标解读

### 超体积（Hypervolume）
- **含义**：前沿覆盖的目标空间体积
- **越大越好**
- **用途**：比较不同任务的前沿质量

### 拐点（Knee Point）
- **含义**：性价比最高的配置
- **识别方法**：最大距离法 + 边际效益法
- **推荐**：两种方法一致的模型最可靠

### 稳定性评级
- **⭐⭐⭐⭐⭐**：极稳定（>90%）
- **⭐⭐⭐⭐**：很稳定（70-90%）
- **⭐⭐⭐**：较稳定（50-70%）
- **⭐⭐**：不稳定（<50%）

---

## 🎯 典型使用场景

### 场景1：快速评估新任务

```bash
# 1. 准备数据（merged_data.csv）
# 2. 运行分析
python run_task_pareto.py --task qa

# 3. 查看结果
# results/pareto_analysis/qa/pareto_metrics_summary.md
```

### 场景2：比较多个任务

```bash
# 对每个任务运行分析
python run_task_pareto.py --task reasoning
python run_task_pareto.py --task qa
python run_task_pareto.py --task summary

# 比较超体积（任务难易度）
# 比较拐点模型（是否一致）
```

### 场景3：模型选择决策

1. 查看拐点推荐（性价比最高）
2. 查看稳定性评级（可靠性）
3. 根据场景选择：
   - 质量优先 → 前沿最高质量点
   - 效率优先 → 前沿最快速度点
   - 平衡方案 → 拐点模型

---

## 📁 文件结构

```
analysis/qe_research/
├── scripts/
│   ├── pareto_metrics_calculator.py      # 定量指标计算
│   ├── pareto_robustness_analyzer.py     # 稳健性验证
│   ├── run_task_pareto.py                # 一键运行脚本
│   └── run_pareto_analysis.bat           # Windows批处理
├── results/pareto_analysis/
│   ├── reasoning/                        # Reasoning任务结果 ✅
│   │   ├── pareto_metrics_summary.md
│   │   ├── pareto_robustness_report.md
│   │   ├── COMPLETION_SUMMARY.md
│   │   └── merged_data.csv
│   ├── qa/                               # QA任务结果（待完成）
│   ├── summary/                          # Summary任务结果（待完成）
│   ├── creative/                         # Creative任务结果（待完成）
│   └── code/                             # Code任务结果（待完成）
├── PARETO_ANALYSIS_GUIDE.md              # 完整使用指南
└── PARETO_QUICK_START.md                 # 本文件
```

---

## 🔧 常见问题

### Q1：如何修改质量维度？

编辑熵权法计算部分，修改 `quality_cols` 列表。

### Q2：如何调整稳健性参数？

编辑 `pareto_robustness_analyzer.py`：
- `noise_level=0.05` → 扰动噪声水平
- `n_iterations=100` → 扰动迭代次数
- `weight_range=0.1` → 权重变化范围
- `n_folds=5` → 交叉验证折数

### Q3：如何自定义权重？

不使用熵权法，手动指定：

```python
custom_weights = {
    'correctness': 0.3,
    'completeness': 0.2,
    'rigor': 0.2,
    'clarity': 0.2,
    'efficiency': 0.1
}

weighted_quality = sum(data_norm[col] * weight 
                      for col, weight in custom_weights.items())
```

---

## 📞 获取帮助

- 完整指南：`PARETO_ANALYSIS_GUIDE.md`
- 评价报告：`results/pareto_analysis/EVALUATION_SUMMARY.md`
- 项目说明：`AGENTS.md`

---

*最后更新：2026-03-06*
