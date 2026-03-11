# 第5章实现总结: 成本效益分析与选择策略

## 实现概述

本文档总结了论文第5章"成本效益分析与选择策略"的完整实现，包括成本核算模型、跨任务比较、难度加权分析、场景化选择和边际效益分析。

**实现时间**: 2026-03-11  
**实现状态**: ✅ 完成

---

## 1. 实现的功能模块

### 1.1 成本核算模型 (5.1节)

**文件**: `analysis/qe_research/scripts/cost_benefit_analysis.py`

**核心类**: `CostModel`

**功能**:
- 能耗成本计算: `C_energy = (E × N) / 3600000 × P_kwh`
- 时间成本计算: `C_time = (N / Speed) / 3600 × D_gpu`
- 总成本计算: `C_total = C_energy + C_time`
- 成本效益指标:
  - QPC (Quality per Cost): `Q / C` (越大越好)
  - CBR (Cost-Benefit Ratio): `C / Q` (越小越好)

**参数配置**:
```python
CostModel(
    energy_cost_per_kwh=0.12,      # 电价 $/kWh
    gpu_depreciation_per_hour=0.50, # GPU折旧 $/hour
    inference_time_weight=1.0       # 时间权重
)
```

### 1.2 跨任务成本效益比较 (5.2节)

**函数**: `cross_task_cost_benefit_comparison()`

**功能**:
- 加载所有任务的质量、能耗、速度数据
- 计算每个模型在每个任务上的成本指标
- 生成跨任务综合数据集
- 按QPC和CBR排序模型

**输出**:
- `cross_task_cost_benefit.csv` - 原始数据
- `model_ranking_by_qpc.csv` - QPC排名
- `model_ranking_by_cbr.csv` - CBR排名

### 1.3 任务难度加权分析 (5.3节)

**函数**: 
- `calculate_task_difficulty()` - 计算任务难度
- `difficulty_weighted_cost_benefit()` - 难度加权分析

**方法**:
1. 计算任务难度: `d_t = σ_t / μ_t` (变异系数)
2. 归一化难度: `d̃_t = (d_t - min) / (max - min)`
3. 综合权重: `w_combined = w_user × d_t`
4. 加权质量: `Q_weighted = Σ(w_combined × Q_task) / Σ(w_combined)`

**理论依据**:
- 变异系数越大 → 任务难度越高 → 模型区分度越强
- 高难度任务应获得更高权重
- 结合用户偏好和客观难度

**输出**:
- `difficulty_weighted_cost_benefit.csv`

### 1.4 场景化模型选择 (5.4节)

**函数**: `scenario_based_selection()`

**预定义场景**:

| 场景 | 描述 | 质量权重 | 成本权重 | 速度权重 |
|------|------|----------|----------|----------|
| cost_sensitive | 成本敏感 | 0.2 | 0.8 | - |
| quality_priority | 质量优先 | 0.8 | 0.2 | - |
| balanced | 均衡场景 | 0.5 | 0.5 | - |
| speed_critical | 速度关键 | 0.3 | 0.3 | 0.4 |

**方法**:
1. 归一化所有指标到 [0, 1]
2. 计算场景得分: `Score = w_q × Q_norm + w_c × C_norm + w_s × S_norm`
3. 应用质量阈值过滤
4. 按场景得分排序

**输出**:
- `scenario_selection_*.csv` (每个场景一个文件)

### 1.5 边际效益分析 (5.5节)

**函数**: `marginal_benefit_analysis()`

**功能**:
1. **边际效益计算**:
   - 按成本排序模型
   - 计算相邻模型间的成本增量 `ΔC` 和质量增量 `ΔQ`
   - 边际效益: `MB = ΔQ / ΔC`

2. **成本-质量曲线拟合**:
   - 对数函数: `Q = a × log(C) + b`
   - 计算拟合优度 R²
   - 验证边际递减效应

3. **拐点识别**:
   - 找到边际效益最大的模型
   - 该模型代表性价比最优点

**输出**:
- `marginal_benefit_analysis.csv`
- 拟合参数和拐点模型

---

## 2. 可视化功能

### 2.1 成本-质量散点图
**函数**: `plot_cost_benefit_scatter()`

**特点**:
- X轴: 总成本
- Y轴: 质量得分
- 颜色: QPC值 (渐变色)
- 标注: 模型名称

### 2.2 边际效益曲线
**函数**: `plot_marginal_benefit_curve()`

**包含**:
- 子图1: 成本-质量曲线 + 对数拟合
- 子图2: 边际效益柱状图

### 2.3 场景对比图
**函数**: `plot_scenario_comparison()`

**特点**:
- 2×2网格布局
- 每个场景显示Top 10模型
- 颜色编码场景得分

---

## 3. 报告生成

### 3.1 报告生成器
**文件**: `analysis/qe_research/scripts/generate_cost_benefit_report.py`

**函数**: `generate_section_5_report()`

**报告结构**:
```
第5章: 成本效益分析与选择策略
├── 5.1 成本核算模型与指标定义
│   ├── 5.1.1 成本模型
│   └── 5.1.2 成本效益指标
├── 5.2 跨任务成本效益比较与模型排序
│   ├── 5.2.1 按QPC排序
│   └── 5.2.2 按CBR排序
├── 5.3 任务难度加权的成本效益分析
│   ├── 5.3.1 任务难度计算
│   └── 5.3.2 难度加权排序结果
├── 5.4 场景化模型选择策略
│   ├── 5.4.1 场景定义
│   └── 5.4.2 各场景推荐模型
├── 5.5 成本-质量权衡的边际效益分析
│   ├── 5.5.1 边际效益理论
│   ├── 5.5.2 成本-质量拟合曲线
│   ├── 5.5.3 拐点识别
│   └── 5.5.4 边际效益排序
└── 5.6 综合结论与建议
    ├── 5.6.1 主要发现
    ├── 5.6.2 决策建议
    └── 5.6.3 成本优化策略
```

**输出**: `SECTION_5_COST_BENEFIT_ANALYSIS_REPORT.md`

---

## 4. 使用方法

### 4.1 快速运行

**Windows批处理**:
```bash
cd analysis/qe_research/scripts
run_cost_benefit_analysis.bat
```

**Python脚本**:
```bash
conda activate bartscore
cd analysis/qe_research/scripts
python generate_cost_benefit_report.py
```

### 4.2 自定义配置

**调整成本参数**:
```python
from cost_benefit_analysis import CostModel

cost_model = CostModel(
    energy_cost_per_kwh=0.15,
    gpu_depreciation_per_hour=1.0,
    inference_time_weight=1.5
)
```

**自定义用户权重**:
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
```

**添加新场景**:
```python
SCENARIO_CONFIGS['my_scenario'] = {
    'name': '自定义场景',
    'description': '场景描述',
    'quality_threshold': 0.3,
    'cost_weight': 0.4,
    'quality_weight': 0.6
}
```

---

## 5. 输出文件清单

### 5.1 数据文件
```
analysis/qe_research/results/cost_benefit_analysis/
├── cross_task_cost_benefit.csv          # 跨任务原始数据
├── model_ranking_by_qpc.csv             # QPC排名
├── model_ranking_by_cbr.csv             # CBR排名
├── difficulty_weighted_cost_benefit.csv # 难度加权结果
├── scenario_selection_cost_sensitive.csv
├── scenario_selection_quality_priority.csv
├── scenario_selection_balanced.csv
├── scenario_selection_speed_critical.csv
└── marginal_benefit_analysis.csv        # 边际效益数据
```

### 5.2 可视化图表
```
├── cost_benefit_scatter.png             # 成本-质量散点图
├── marginal_benefit_curve.png           # 边际效益曲线
└── scenario_comparison.png              # 场景对比图
```

### 5.3 报告文档
```
└── SECTION_5_COST_BENEFIT_ANALYSIS_REPORT.md  # 完整分析报告
```

---

## 6. 技术特点

### 6.1 创新点

1. **综合成本模型**:
   - 同时考虑能耗成本和时间成本
   - 可配置的成本参数
   - 适应不同部署环境

2. **任务难度加权**:
   - 基于变异系数的客观难度量化
   - 结合用户偏好的双重权重
   - 突出模型在困难任务上的表现

3. **场景化选择**:
   - 预定义多种典型应用场景
   - 灵活的权重配置
   - 支持自定义场景

4. **边际效益分析**:
   - 识别性价比最优点
   - 对数曲线拟合验证递减效应
   - 为预算分配提供理论依据

### 6.2 方法论优势

1. **理论严谨**:
   - 基于经济学边际效益理论
   - 多目标优化框架
   - 统计学显著性检验

2. **实用性强**:
   - 直接支持决策
   - 场景化推荐
   - 可解释性强

3. **可扩展性**:
   - 模块化设计
   - 易于添加新指标
   - 支持自定义场景

---

## 7. 与其他章节的关联

### 7.1 数据来源

- **第4章**: 帕累托前沿分析提供质量、能耗、速度数据
- **质量评估**: PCA综合质量得分
- **能耗监控**: GPU能耗实测数据
- **速度测试**: 吞吐量和延迟数据

### 7.2 分析流程

```
第4章: 帕累托前沿分析
    ↓
识别非支配模型集合
    ↓
第5章: 成本效益分析
    ↓
├─ 成本核算 (5.1)
├─ 跨任务比较 (5.2)
├─ 难度加权 (5.3)
├─ 场景选择 (5.4)
└─ 边际效益 (5.5)
    ↓
决策支持与模型推荐
```

---

## 8. 验证与测试

### 8.1 数据完整性检查
- ✅ 所有任务数据加载成功
- ✅ 模型映射正确
- ✅ 缺失值处理

### 8.2 计算正确性验证
- ✅ 成本计算公式验证
- ✅ 归一化范围检查 [0, 1]
- ✅ 权重和为1验证

### 8.3 结果合理性检查
- ✅ QPC和CBR排名一致性
- ✅ 边际效益递减趋势
- ✅ 场景推荐符合预期

---

## 9. 已知限制与改进方向

### 9.1 当前限制

1. **成本模型简化**:
   - 未考虑模型加载时间
   - 未包含存储成本
   - 批处理效应未建模

2. **任务难度单一指标**:
   - 仅使用变异系数
   - 可考虑其他难度度量

3. **场景预定义**:
   - 场景数量有限
   - 需要更多实际应用场景

### 9.2 改进方向

1. **成本模型扩展**:
   - 添加内存成本
   - 考虑批处理优化
   - 建模冷启动开销

2. **难度度量增强**:
   - 多维难度指标
   - 任务复杂度分析
   - 领域知识融合

3. **动态场景生成**:
   - 基于用户输入自动生成场景
   - 交互式权重调整
   - 实时推荐更新

4. **不确定性量化**:
   - 成本估计置信区间
   - 敏感性分析
   - 鲁棒性评估

---

## 10. 文档与支持

### 10.1 相关文档
- `COST_BENEFIT_ANALYSIS_QUICK_START.md` - 快速开始指南
- `cost_benefit_analysis.py` - 核心实现代码
- `generate_cost_benefit_report.py` - 报告生成脚本

### 10.2 示例代码
参见 `generate_cost_benefit_report.py` 中的 `__main__` 部分

### 10.3 常见问题
参见 `COST_BENEFIT_ANALYSIS_QUICK_START.md` 的FAQ部分

---

## 11. 总结

第5章的实现提供了一套完整的成本效益分析框架，包括:

✅ **成本核算**: 综合能耗和时间成本  
✅ **跨任务比较**: 多任务综合评估  
✅ **难度加权**: 考虑任务区分度  
✅ **场景选择**: 面向实际应用  
✅ **边际分析**: 识别性价比最优点  

该实现为GenAI模型的实际部署提供了科学的决策支持，帮助用户在质量、成本、速度之间找到最优平衡点。

---

**实现完成时间**: 2026-03-11  
**实现者**: Kiro AI Assistant  
**版本**: 1.0
