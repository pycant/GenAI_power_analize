# 成本效益分析快速开始指南

## 概述

本指南介绍如何运行第5章"成本效益分析与选择策略"的完整分析流程。

## 分析内容

### 5.1 成本核算模型与指标定义
- 能耗成本计算
- 时间成本计算
- 综合成本指标 (QPC, CBR)

### 5.2 跨任务成本效益比较与模型排序
- 多任务成本效益数据收集
- 按QPC和CBR排序模型
- 识别最优性价比模型

### 5.3 任务难度加权的成本效益分析
- 计算任务难度系数 (变异系数)
- 难度加权质量聚合
- 考虑任务区分度的模型评估

### 5.4 场景化模型选择策略
- 成本敏感场景
- 质量优先场景
- 均衡场景
- 速度关键场景

### 5.5 成本-质量权衡的边际效益分析
- 边际效益计算
- 成本-质量曲线拟合
- 拐点识别

## 快速运行

### 方法1: 使用Python脚本

```bash
# 激活环境
conda activate bartscore

# 运行完整分析
cd analysis/qe_research/scripts
python generate_cost_benefit_report.py
```

### 方法2: 使用批处理脚本 (Windows)

```bash
cd analysis/qe_research/scripts
run_cost_benefit_analysis.bat
```

### 方法3: 在Python中调用

```python
from cost_benefit_analysis import run_cost_benefit_analysis, CostModel
from pathlib import Path

# 配置
tasks = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']
output_dir = Path('analysis/qe_research/results')

# 自定义成本模型
cost_model = CostModel(
    energy_cost_per_kwh=0.12,  # 电价 $/kWh
    gpu_depreciation_per_hour=0.50,  # GPU折旧 $/hour
    inference_time_weight=1.0  # 时间权重
)

# 运行分析
results = run_cost_benefit_analysis(
    tasks=tasks,
    output_base_dir=output_dir,
    cost_model=cost_model
)
```

## 输出文件

分析完成后，结果保存在 `analysis/qe_research/results/cost_benefit_analysis/`:

### 数据文件
- `cross_task_cost_benefit.csv` - 跨任务成本效益原始数据
- `model_ranking_by_qpc.csv` - 按QPC排序的模型
- `model_ranking_by_cbr.csv` - 按CBR排序的模型
- `difficulty_weighted_cost_benefit.csv` - 难度加权结果
- `scenario_selection_*.csv` - 各场景选择结果
- `marginal_benefit_analysis.csv` - 边际效益分析数据

### 可视化图表
- `cost_benefit_scatter.png` - 成本-质量散点图
- `marginal_benefit_curve.png` - 边际效益曲线
- `scenario_comparison.png` - 场景对比图

### 报告
- `SECTION_5_COST_BENEFIT_ANALYSIS_REPORT.md` - 完整分析报告

## 自定义配置

### 调整成本参数

```python
cost_model = CostModel(
    energy_cost_per_kwh=0.15,  # 提高电价
    gpu_depreciation_per_hour=1.0,  # 提高GPU成本
    inference_time_weight=1.5  # 增加时间权重
)
```

### 自定义用户偏好权重

```python
user_weights = {
    'code': 0.30,
    'math': 0.25,
    'qa': 0.20,
    'reasoning': 0.15,
    'creative': 0.05,
    'summary': 0.03,
    'translation': 0.02
}

results = run_cost_benefit_analysis(
    tasks=tasks,
    output_base_dir=output_dir,
    cost_model=cost_model,
    user_weights=user_weights
)
```

### 添加新场景

在 `cost_benefit_analysis.py` 中修改 `SCENARIO_CONFIGS`:

```python
SCENARIO_CONFIGS['my_scenario'] = {
    'name': '我的场景',
    'description': '场景描述',
    'quality_threshold': 0.3,
    'cost_weight': 0.4,
    'quality_weight': 0.6
}
```

## 结果解读

### QPC (Quality per Cost)
- 定义: 单位成本的质量产出
- 公式: QPC = Quality / Cost
- 越大越好
- 适用场景: 追求性价比

### CBR (Cost-Benefit Ratio)
- 定义: 单位质量的成本投入
- 公式: CBR = Cost / Quality
- 越小越好
- 适用场景: 成本敏感

### 边际效益 (Marginal Benefit)
- 定义: 成本增加带来的质量提升
- 公式: MB = ΔQuality / ΔCost
- 越大越好
- 用途: 识别拐点模型

### 拐点模型 (Knee Point)
- 边际效益最高的模型
- 代表成本-质量权衡的最优点
- 推荐用于均衡场景

## 常见问题

### Q1: 如何选择合适的电价和GPU成本?

A: 根据实际部署环境:
- 云服务: 参考云厂商定价 (AWS, Azure, GCP)
- 本地部署: 使用当地电价和硬件折旧
- 默认值: 0.12 $/kWh (美国平均电价), 0.50 $/hour (RTX 4060折旧)

### Q2: 任务难度权重如何影响结果?

A: 任务难度权重会:
- 放大高难度任务的重要性
- 突出在困难任务上表现好的模型
- 适合需要区分模型能力的场景

### Q3: 如何为特定应用选择模型?

A: 按场景选择:
1. 预算受限 → 选择CBR最低的模型
2. 质量优先 → 选择质量最高的模型
3. 均衡需求 → 选择拐点模型
4. 实时应用 → 选择速度关键场景推荐模型

### Q4: 边际效益分析有什么实际意义?

A: 边际效益分析帮助:
- 识别性价比最优的模型
- 避免过度投资 (超过拐点后收益递减)
- 制定预算分配策略
- 理解成本-质量权衡关系

## 进阶使用

### 批量场景分析

```python
scenarios = ['cost_sensitive', 'quality_priority', 'balanced', 'speed_critical']

for scenario in scenarios:
    df_scenario = scenario_based_selection(df, scenario, output_dir)
    print(f"{scenario}: {df_scenario.iloc[0]['model']}")
```

### 敏感性分析

```python
# 测试不同电价对排名的影响
for price in [0.08, 0.12, 0.16, 0.20]:
    cost_model = CostModel(energy_cost_per_kwh=price)
    results = run_cost_benefit_analysis(tasks, output_dir, cost_model)
    print(f"电价 ${price}: Top模型 = {results['ranked_qpc'].iloc[0]['model']}")
```

### 导出Excel报告

```python
import pandas as pd

# 合并所有结果到Excel
with pd.ExcelWriter('cost_benefit_analysis.xlsx') as writer:
    results['cross_task'].to_excel(writer, sheet_name='原始数据', index=False)
    results['ranked_qpc'].to_excel(writer, sheet_name='QPC排名', index=False)
    results['ranked_cbr'].to_excel(writer, sheet_name='CBR排名', index=False)
    results['weighted'].to_excel(writer, sheet_name='难度加权', index=False)
    results['marginal']['marginal_df'].to_excel(writer, sheet_name='边际效益', index=False)
```

## 参考文献

1. 成本效益分析理论
2. 边际效益递减原理
3. 多目标优化与帕累托前沿
4. 任务难度量化方法

## 技术支持

如有问题，请查看:
- 完整文档: `analysis/qe_research/README.md`
- 实现细节: `analysis/qe_research/scripts/cost_benefit_analysis.py`
- 示例代码: `analysis/qe_research/scripts/generate_cost_benefit_report.py`

---

**最后更新**: 2026-03-11
