# 混合任务分析执行指南

## 脚本功能

`pareto_mixed_task.py` 实现了完整的混合任务帕累托前沿分析，支持三种权重配置：

1. **objective（客观任务为主）**：90% 客观任务 + 10% 主观任务
   - 适用于：技术应用、工程实践、需要精确结果的场景

2. **subjective（主观任务为主）**：80% 主观任务 + 20% 客观任务
   - 适用于：内容创作、文学创作、需要创造性的场景

3. **balanced（均衡配置）**：各任务权重相对均衡
   - 适用于：通用评估、综合应用

## 执行方法

### 方法1：从项目根目录执行（推荐）

```bash
# 1. 激活conda环境
conda activate bartscore

# 2. 设置UTF-8编码
set PYTHONUTF8=1

# 3. 执行脚本
python analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py
```

### 方法2：从scripts目录执行

```bash
# 1. 激活conda环境
conda activate bartscore

# 2. 设置UTF-8编码
set PYTHONUTF8=1

# 3. 切换到scripts目录并执行
cd analysis/qe_research/scripts
python pareto_core/pareto_mixed_task.py
```

## 执行流程

脚本会依次执行三个配置的分析：

```
进度: 1/3 - 配置: objective
  ├── 步骤1: 加载质量数据（7个任务）
  ├── 步骤2: 聚合质量得分（按权重加权）
  ├── 步骤3: 合并能耗和速度数据
  ├── 步骤4: 生成可视化（权重图、热力图）
  ├── 步骤5: 帕累托前沿分析
  ├── 步骤6: 生成帕累托图
  ├── 步骤7: 计算定量指标
  ├── 步骤8: 稳健性分析
  └── 步骤9: 生成报告

进度: 2/3 - 配置: subjective
  └── ... (同上)

进度: 3/3 - 配置: balanced
  └── ... (同上)
```

## 输出结果

结果保存在：`analysis/qe_research/results/mixed_task_analysis/task_01/`

```
task_01/
├── objective/                          # 客观任务为主配置
│   ├── task_weights.png               # 任务权重分布图
│   ├── quality_heatmap.png            # 模型×任务质量热力图
│   ├── pareto_quality_energy.png      # 质量-能耗帕累托前沿
│   ├── pareto_quality_speed.png       # 质量-速度帕累托前沿
│   ├── task_quality_scores.csv        # 任务得分矩阵
│   ├── merged_data.csv                # 合并后的完整数据
│   ├── MIXED_TASK_ANALYSIS_REPORT.md  # 分析报告
│   └── code/                          # 各任务的熵权法权重图
│       ├── creative/
│       ├── math/
│       ├── qa/
│       ├── reasoning/
│       ├── summary/
│       └── translation/
│
├── subjective/                         # 主观任务为主配置
│   └── ... (同上)
│
└── balanced/                           # 均衡配置
    └── ... (同上)
```

## 权重配置详情

### objective（客观任务为主）
```python
{
    'code': 0.30,        # 代码生成 - 30%
    'math': 0.25,        # 数学推理 - 25%
    'qa': 0.20,          # 问答 - 20%
    'reasoning': 0.15,   # 逻辑推理 - 15%
    'creative': 0.05,    # 创意写作 - 5%
    'summary': 0.03,     # 文本摘要 - 3%
    'translation': 0.02  # 机器翻译 - 2%
}
```

### subjective（主观任务为主）
```python
{
    'creative': 0.35,    # 创意写作 - 35%
    'summary': 0.25,     # 文本摘要 - 25%
    'translation': 0.20, # 机器翻译 - 20%
    'code': 0.10,        # 代码生成 - 10%
    'math': 0.05,        # 数学推理 - 5%
    'qa': 0.03,          # 问答 - 3%
    'reasoning': 0.02    # 逻辑推理 - 2%
}
```

### balanced（均衡配置）
```python
{
    'code': 0.15,
    'math': 0.15,
    'qa': 0.15,
    'reasoning': 0.12,
    'creative': 0.15,
    'summary': 0.15,
    'translation': 0.13
}
```

## 预计执行时间

- 每个配置约需 5-10 分钟（取决于数据量和系统性能）
- 总计约 15-30 分钟完成所有三个配置

## 注意事项

1. **数据依赖**：确保所有7个任务的质量数据已生成
   - 如果某个任务数据缺失，脚本会跳过该任务并继续

2. **内存使用**：脚本会同时加载多个任务的数据，确保有足够内存

3. **权重自动归一化**：如果权重和不为1，脚本会自动归一化

4. **中文显示**：脚本已配置中文字体支持，图表中的中文会正常显示

## 查看结果

执行完成后，可以查看：

1. **图表**：直接打开 PNG 文件查看可视化结果
2. **报告**：打开 `MIXED_TASK_ANALYSIS_REPORT.md` 查看详细分析
3. **数据**：使用 Excel 或 pandas 打开 CSV 文件查看原始数据

## 故障排除

### 问题1：ModuleNotFoundError
```bash
# 解决方法：确保在项目根目录执行
cd F:\all_proj\GenAI_power_analize
python analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py
```

### 问题2：某个任务数据加载失败
```
✗ 加载任务 reasoning 失败: ...
```
这是正常的，脚本会跳过缺失的任务并继续执行。

### 问题3：中文乱码
```bash
# 执行前设置UTF-8编码
set PYTHONUTF8=1
```

## 快速测试

如果想快速测试脚本是否正常工作：

```bash
# 只显示前100行输出
python analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py 2>&1 | Select-Object -First 100
```

---

**创建日期**: 2026-03-08
**脚本版本**: 1.0
**状态**: 已完成，可执行
