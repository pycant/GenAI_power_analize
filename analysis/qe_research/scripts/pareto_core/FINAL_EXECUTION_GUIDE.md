# 混合任务分析 - 最终执行指南

## ✅ 问题已解决！

脚本已经修复并可以正常运行。新的执行脚本位于：
```
analysis/qe_research/scripts/run_mixed_task_analysis.py
```

## 执行方法

### 完整命令（推荐）

```bash
# 1. 激活conda环境
conda activate bartscore

# 2. 设置UTF-8编码（重要！）
set PYTHONUTF8=1

# 3. 切换到scripts目录
cd analysis/qe_research/scripts

# 4. 执行脚本
python run_mixed_task_analysis.py
```

### 一行命令版本

```bash
conda activate bartscore && set PYTHONUTF8=1 && cd analysis/qe_research/scripts && python run_mixed_task_analysis.py
```

### 从项目根目录执行

```bash
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/run_mixed_task_analysis.py
```

## 脚本功能

脚本会依次执行三个权重配置的混合任务分析：

1. **objective（客观任务为主）**
   - code: 30%, math: 25%, qa: 20%, reasoning: 15%
   - creative: 5%, summary: 3%, translation: 2%

2. **subjective（主观任务为主）**
   - creative: 35%, summary: 25%, translation: 20%
   - code: 10%, math: 5%, qa: 3%, reasoning: 2%

3. **balanced（均衡配置）**
   - 各任务权重相对均衡（12-15%）

## 执行流程

每个配置会执行以下步骤：

```
步骤1: 加载质量数据（7个任务）
  ├── code, creative, math, qa, reasoning, summary, translation
  └── 使用熵权法处理质量指标

步骤2: 聚合质量得分
  ├── 按权重配置加权聚合
  └── 生成任务得分矩阵

步骤3: 合并能耗和速度数据
  └── 计算各任务的平均能耗和速度

步骤4: 生成可视化
  ├── 任务权重分布图
  └── 模型×任务质量热力图

步骤5: 帕累托前沿分析
  ├── 质量-能耗前沿
  ├── 质量-速度前沿
  └── 三维前沿

步骤6: 生成帕累托图

步骤7: 计算定量指标
  ├── 超体积
  ├── 间距指标
  └── 拐点模型

步骤8: 稳健性分析
  ├── 扰动分析
  └── 交叉验证

步骤9: 生成报告
```

## 输出结果

结果保存在：
```
analysis/qe_research/results/mixed_task_analysis/task_01/
├── objective/
│   ├── task_weights.png
│   ├── quality_heatmap.png
│   ├── pareto_quality_energy.png
│   ├── pareto_quality_speed.png
│   ├── task_quality_scores.csv
│   ├── merged_data.csv
│   ├── MIXED_TASK_ANALYSIS_REPORT.md
│   └── [各任务的熵权法权重图]
├── subjective/
│   └── [同上]
└── balanced/
    └── [同上]
```

## 预计执行时间

- 每个配置：5-10 分钟
- 总计：15-30 分钟

## 常见问题

### Q1: UnicodeEncodeError: 'gbk' codec can't encode character
**解决方法**：执行前必须设置 `set PYTHONUTF8=1`

### Q2: ModuleNotFoundError: No module named 'pareto_core'
**解决方法**：确保从 `analysis/qe_research/scripts` 目录执行

### Q3: 某个任务数据加载失败
这是正常的，脚本会跳过缺失的任务并继续执行。

## 验证脚本是否正常

快速测试（只显示前100行输出）：

```bash
conda activate bartscore
set PYTHONUTF8=1
cd analysis/qe_research/scripts
python run_mixed_task_analysis.py 2>&1 | Select-Object -First 100
```

如果看到以下输出，说明脚本正常运行：

```
================================================================================
混合任务帕累托前沿分析 - 批量执行
================================================================================
输出基础目录: ...
配置数量: 3
================================================================================

################################################################################
# 进度: 1/3 - 配置: objective
################################################################################

步骤1: 加载质量数据
--------------------------------------------------------------------------------
加载任务: code
...
```

## 关键改进

相比之前的版本，新脚本：

1. ✅ 修复了导入路径问题
2. ✅ 从 scripts 目录运行，避免路径混乱
3. ✅ 完整实现了混合任务分析逻辑
4. ✅ 支持三种权重配置
5. ✅ 自动权重归一化
6. ✅ 完整的可视化和报告生成

---

**创建日期**: 2026-03-08
**状态**: ✅ 已完成，可执行
**脚本位置**: `analysis/qe_research/scripts/run_mixed_task_analysis.py`
