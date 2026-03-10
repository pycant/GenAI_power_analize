# 混合任务分析快速开始

## 前置条件

### 1. 确保质量数据已生成
所有任务的质量得分文件应存在于：
```
analysis/qe_research/results/quality_scores/
├── code_scores_raw.csv
├── creative_scores_raw.csv
├── math_scores_raw.csv
├── qa_scores_raw.csv
├── reasoning_scores_raw.csv
├── summary_scores_raw.csv
└── translation_scores_raw.csv
```

如果缺失，请先运行质量分析：
```bash
python analysis/qe_research/scripts/create_quality_score_tables.py
```

### 2. 确保能耗和速度数据存在
```
analysis/qe_research/results/metric_tables/
├── energy_per_token_transposed.csv
└── tokens_per_second_transposed.csv
```

如果缺失，请先运行指标表生成：
```bash
python analysis/qe_research/scripts/create_metric_tables.py
```

## 运行分析

### 方法1: 运行所有配置（推荐）

```bash
# 激活conda环境
conda activate bartscore

# 设置UTF-8编码（Windows）
set PYTHONUTF8=1

# 运行分析
cd analysis/qe_research/scripts/pareto_core
python pareto_mixed_task.py
```

这将依次运行三种权重配置：
1. **objective**: 客观任务为主（90% vs 10%）
2. **subjective**: 主观任务为主（80% vs 20%）
3. **balanced**: 均衡配置（57% vs 43%）

### 方法2: 运行单个配置

```python
import sys
from pathlib import Path

# 添加项目路径
project_root = Path.cwd().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pareto_core.pareto_mixed_task import run_mixed_task_analysis

# 选择配置：'objective', 'subjective', 或 'balanced'
config_name = 'objective'

# 设置输出目录
output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'mixed_task_analysis' / 'task_01'

# 运行分析
run_mixed_task_analysis(config_name, output_dir)
```

## 预期输出

### 控制台输出示例
```
================================================================================
混合任务帕累托前沿分析 - 客观任务为主
================================================================================
配置: objective
说明: 适用于技术应用、工程实践、需要精确结果的场景
================================================================================

================================================================================
加载所有任务的质量数据
================================================================================

加载任务: CODE
✓ code: 12 个模型

加载任务: CREATIVE
✓ creative: 12 个模型

...

✓ 成功加载 7/7 个任务

================================================================================
聚合多任务质量得分
================================================================================
共有 12 个模型

✓ 聚合完成
  质量得分范围: [0.3245, 0.8756]

前5名模型:
  qwen3_8b                       0.8756
  deepseek-r1_8b                 0.8234
  ...

================================================================================
识别帕累托前沿
================================================================================
✓ 质量-能耗前沿: 5 个模型
✓ 质量-速度前沿: 4 个模型
✓ 三维前沿: 3 个模型

...
```

### 输出文件结构
```
analysis/qe_research/results/mixed_task_analysis/task_01/
├── objective/                           # 客观任务为主配置
│   ├── merged_data.csv                  # 合并数据
│   ├── task_quality_scores.csv          # 质量得分矩阵
│   ├── task_weights.png                 # 权重分布图
│   ├── quality_heatmap.png              # 质量热力图
│   ├── pareto_quality_energy.png        # 质量-能耗前沿
│   ├── pareto_quality_speed.png         # 质量-速度前沿
│   ├── MIXED_TASK_ANALYSIS_REPORT.md    # 分析报告
│   └── code/                            # 各任务的熵权法权重
│       └── entropy_weights.png
│
├── subjective/                          # 主观任务为主配置
│   └── ...（同上）
│
└── balanced/                            # 均衡配置
    └── ...（同上）
```

## 查看结果

### 1. 查看分析报告
```bash
# 使用文本编辑器或Markdown查看器
code analysis/qe_research/results/mixed_task_analysis/task_01/objective/MIXED_TASK_ANALYSIS_REPORT.md
```

报告包含：
- 权重配置详情
- 数据概览
- 帕累托前沿识别结果
- 定量指标
- 稳健性分析
- 各任务质量得分矩阵
- 推荐配置

### 2. 查看可视化图表
使用图片查看器打开PNG文件：
- `task_weights.png`: 任务权重分布
- `quality_heatmap.png`: 模型×任务质量热力图
- `pareto_quality_energy.png`: 质量-能耗帕累托前沿
- `pareto_quality_speed.png`: 质量-速度帕累托前沿

### 3. 查看数据文件
使用Excel或Python查看CSV文件：

```python
import pandas as pd

# 查看合并数据
df = pd.read_csv('merged_data.csv')
print(df.head())

# 查看质量得分矩阵
quality_matrix = pd.read_csv('task_quality_scores.csv', index_col=0)
print(quality_matrix)
```

## 结果解读

### 综合质量得分
- **范围**: [0, 1]
- **含义**: 模型在多任务场景下的加权综合表现
- **影响因素**: 权重配置、各任务表现

### 帕累托前沿模型
- **质量-能耗前沿**: 在质量和能耗之间达到最优权衡的模型
- **质量-速度前沿**: 在质量和速度之间达到最优权衡的模型
- **三维前沿**: 在质量、能耗、速度三个维度都不被支配的模型

### 拐点模型
- **定义**: 帕累托前沿上曲率最大的点
- **意义**: 综合性价比最高的推荐选择
- **特点**: 在质量提升和效率损失之间达到最佳平衡

### 稳健性指标
- **前沿一致性**: 模型在数据扰动下保持在前沿的概率
- **交叉验证一致性**: 模型在不同数据子集上的前沿稳定性
- **稳定性得分**: 单个模型的稳健性评分

## 对比不同配置

### 查看三种配置的拐点模型
```bash
# objective配置
grep "拐点模型" analysis/qe_research/results/mixed_task_analysis/task_01/objective/MIXED_TASK_ANALYSIS_REPORT.md

# subjective配置
grep "拐点模型" analysis/qe_research/results/mixed_task_analysis/task_01/subjective/MIXED_TASK_ANALYSIS_REPORT.md

# balanced配置
grep "拐点模型" analysis/qe_research/results/mixed_task_analysis/task_01/balanced/MIXED_TASK_ANALYSIS_REPORT.md
```

### 对比综合质量得分
```python
import pandas as pd

configs = ['objective', 'subjective', 'balanced']
base_path = 'analysis/qe_research/results/mixed_task_analysis/task_01'

for config in configs:
    df = pd.read_csv(f'{base_path}/{config}/merged_data.csv')
    print(f"\n{config.upper()} 配置:")
    print(df.nlargest(5, 'quality')[['model', 'quality', 'energy', 'speed']])
```

## 常见问题

### Q1: 提示找不到质量数据文件
**A**: 请先运行质量分析生成质量得分：
```bash
python analysis/qe_research/scripts/create_quality_score_tables.py
```

### Q2: 某些任务加载失败
**A**: 检查该任务的质量数据是否存在且格式正确。可以跳过失败的任务继续分析。

### Q3: 内存不足
**A**: 混合任务分析需要加载所有任务数据，确保有足够内存（建议8GB+）。

### Q4: 如何自定义权重配置
**A**: 编辑 `pareto_mixed_task.py` 中的 `WEIGHT_CONFIGS` 字典，添加新配置：
```python
WEIGHT_CONFIGS['custom'] = {
    'name': '自定义配置',
    'description': '您的描述',
    'weights': {
        'code': 0.20,
        'math': 0.20,
        # ... 其他任务
    }
}
```

### Q5: 如何只分析部分任务
**A**: 修改 `ALL_TASKS` 列表，只包含需要的任务：
```python
ALL_TASKS = ['code', 'math', 'qa']  # 只分析这三个任务
```

## 下一步

### 1. 深入分析
- 查看各任务的熵权法权重分布
- 分析模型在不同任务上的表现差异
- 对比不同权重配置的结果

### 2. 结果应用
- 根据应用场景选择合适的权重配置
- 识别最适合特定场景的模型
- 为模型选型提供数据支持

### 3. 扩展分析
- 添加公平性分析（参考AGENTS.md）
- 进行时间序列分析（跨版本对比）
- 集成到自动化评估流程

## 参考文档

- **方法说明**: `method.md`
- **实现总结**: `IMPLEMENTATION_SUMMARY.md`
- **项目指南**: `../../AGENTS.md`
- **帕累托分析**: `../../README_PARETO.md`

---

**更新日期**: 2026-03-08
**版本**: 1.0
