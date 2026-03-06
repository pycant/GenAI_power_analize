# 快速开始指南

## 🚀 5分钟快速上手

### 步骤1: 环境准备

```bash
# 激活conda环境
conda activate bartscore

# 设置UTF-8编码（Windows）
set PYTHONUTF8=1

# 进入项目目录
cd D:\project\GenAI_power_analize
```

### 步骤2: 验证数据管道

```bash
# 快速查看数据概览
python scripts/quick_data_overview.py
```

如果数据管道未初始化，运行：
```bash
python scripts/test_and_explore_pipeline.py
```

### 步骤3: 运行综合分析

```bash
python analysis/qe_research/scripts/comprehensive_analysis.py
```

### 步骤4: 查看结果

```bash
# 查看报告
notepad analysis\qe_research\results\reports\comprehensive_report.md

# 打开图表目录
explorer analysis\qe_research\results\figures

# 查看数据表
explorer analysis\qe_research\results\tables
```

## 📊 输出说明

### 报告文件
- `comprehensive_report.md` - 完整的分析报告，包含所有章节

### 图表文件
- `latency_vs_throughput.png` - 延迟vs吞吐量散点图
- `energy_distribution.png` - 能耗分布箱线图
- `quality_heatmap.png` - 质量热力图（模型×任务）
- `qe_ranking.png` - 质效比排名柱状图
- `fairness_comparison.png` - 公平性对比图

### 数据表文件
- `data_overview.csv` - 数据概览统计
- `performance_by_model.csv` - 按模型的性能统计
- `efficiency_by_model.csv` - 按模型的效率统计
- `quality_by_model_task.csv` - 按模型和任务的质量统计
- `qe_ranking.csv` - 质效比排名表
- `fairness_metrics.csv` - 公平性指标表

### 导出数据
- `normalized_scores.csv` - 归一化后的得分数据

## 🔧 配置调整

编辑配置文件：
```bash
notepad analysis\qe_research\configs\analysis_config.yaml
```

常用配置项：
- `weights.efficiency` - 效率得分权重（吞吐量、延迟、能耗）
- `weights.composite` - 复合得分权重（质量、效率）
- `visualization.font.family` - 图表字体
- `output.figure_dpi` - 图表分辨率

## 📈 分析流程

```
1. 数据加载
   ↓
2. 数据概览（模型、任务统计）
   ↓
3. 性能分析（延迟、吞吐量）
   ↓
4. 效率分析（能耗、资源使用）
   ↓
5. 质量分析（BARTScore等）
   ↓
6. 质效比计算（归一化、加权）
   ↓
7. 公平性分析（Fairness Gap、Gini）
   ↓
8. 生成报告和可视化
```

## 🎯 关键指标

### 性能指标
- **延迟 (latency_s)**: 响应时间，越低越好
- **吞吐量 (toks_per_s)**: 每秒生成token数，越高越好
- **首token时间 (ttft_s)**: 首个token生成时间

### 效率指标
- **GPU能耗 (gpu_energy_j)**: GPU消耗的能量，越低越好
- **CPU使用率 (cpu_usage_avg)**: 平均CPU使用率
- **内存使用 (memory_used_avg_mb)**: 平均内存占用

### 质量指标
- **BARTScore**: 文本生成质量评分，越高越好

### 复合指标
- **效率得分**: 0.4×吞吐 + 0.3×(1-延迟) + 0.3×(1-能耗)
- **质效比**: (质量 + ε) / (1 + ε - 效率)

### 公平性指标
- **Fairness Gap**: 任务间质量差异的最大值，越小越公平
- **Gini系数**: 质量分布不均衡度，0表示完全均衡
- **Nash Social Welfare**: 公平化聚合得分

## 💡 使用技巧

### 1. 按任务分析

修改脚本，只分析特定任务：
```python
from data.analize.pipeline import ExperimentDataManager

dm = ExperimentDataManager()
df_code = dm.get_by_task('code')
# 进行分析...
```

### 2. 按模型分析

只分析特定模型：
```python
df_qwen = dm.get_by_model('qwen3:8b')
# 进行分析...
```

### 3. 自定义权重

在配置文件中调整权重：
```yaml
weights:
  efficiency:
    throughput: 0.5  # 增加吞吐量权重
    latency: 0.3
    energy: 0.2      # 降低能耗权重
```

### 4. 导出特定数据

```python
# 导出Top 5模型的详细数据
top_models = qe_ranking.head(5).index
df_top = df[df['model_name'].isin(top_models)]
df_top.to_csv('top5_models.csv', index=False)
```

## 🐛 常见问题

### Q1: 提示找不到数据文件

**A**: 运行数据管道初始化：
```bash
python scripts/test_and_explore_pipeline.py
```

### Q2: 图表中文显示为方框

**A**: 检查字体配置，确保系统已安装 Microsoft YaHei：
```yaml
visualization:
  font:
    family: "Microsoft YaHei"
```

### Q3: 内存不足

**A**: 在配置文件中禁用缓存：
```yaml
cache:
  enabled: false
```

### Q4: 分析速度慢

**A**: 启用缓存并减少数据量：
```yaml
cache:
  enabled: true
  ttl: 3600
```

### Q5: 某些指标缺失

**A**: 检查原始数据是否包含该指标，某些模型可能没有记录所有指标。

## 📚 进阶使用

### 使用Jupyter Notebook

```bash
# 启动Jupyter Lab
jupyter lab

# 打开notebooks目录
# 创建新的notebook进行交互式分析
```

### 批量分析

创建批处理脚本：
```bash
@echo off
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/comprehensive_analysis.py
python analysis/qe_research/scripts/model_comparison.py
python analysis/qe_research/scripts/task_analysis.py
echo 分析完成!
pause
```

### 定时分析

使用Windows任务计划程序定时运行分析脚本。

## 🔗 相关文档

- [完整README](README.md) - 详细的研究框架说明
- [脚本文档](scripts/README.md) - 所有脚本的详细说明
- [配置说明](configs/analysis_config.yaml) - 配置文件详解
- [数据管道文档](../../data/analize/pipeline/README.md) - 数据管道使用指南

## 📞 获取帮助

如有问题，请查看：
1. 日志文件: `analysis/qe_research/logs/analysis.log`
2. 项目文档: `docs/`
3. AGENTS.md: 项目环境和配置说明

---

**祝分析顺利！** 🎉
