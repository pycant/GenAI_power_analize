# 质效比深度研究 (Quality-Efficiency Research)

## 📁 目录结构

```
analysis/qe_research/
├── README.md                           # 本文档
├── notebooks/                          # Jupyter笔记本
│   ├── 01_data_exploration.ipynb      # 数据探索
│   ├── 02_performance_analysis.ipynb  # 性能分析
│   ├── 03_efficiency_analysis.ipynb   # 效率分析
│   ├── 04_quality_analysis.ipynb      # 质量分析
│   └── 05_qe_ratio_analysis.ipynb     # 质效比分析
├── scripts/                            # 分析脚本
│   ├── comprehensive_analysis.py      # 综合分析
│   ├── model_comparison.py            # 模型对比
│   ├── task_analysis.py               # 任务分析
│   ├── fairness_analysis.py           # 公平性分析
│   └── statistical_tests.py           # 统计检验
├── results/                            # 分析结果
│   ├── figures/                       # 图表
│   ├── tables/                        # 数据表
│   ├── reports/                       # 报告
│   └── exports/                       # 导出数据
├── configs/                            # 配置文件
│   ├── analysis_config.yaml           # 分析配置
│   └── weights_config.yaml            # 权重配置
└── docs/                               # 文档
    ├── methodology.md                 # 方法论
    ├── metrics_definition.md          # 指标定义
    └── findings.md                    # 研究发现
```

## 🎯 研究目标

基于项目的核心目标，构建全面的GenAI模型能效评级体系：

### 主要研究问题

1. **性能-效率权衡**
   - 在给定硬件条件下，如何平衡质量、延迟和能耗？
   - 哪些模型在质效比上表现最优？

2. **任务特异性**
   - 不同任务类型对模型性能的影响
   - 模型在不同任务上的一致性

3. **量化方式影响**
   - 4bit vs 8bit vs Q4_K_M量化的性能差异
   - 量化对质量和效率的影响

4. **公平性分析**
   - 模型在不同任务上的表现公平性
   - 识别系统性偏差

5. **能效评级**
   - 构建标准化的能效评级体系
   - 为不同应用场景推荐最优模型

## 🔬 研究方法

### 1. 数据收集与预处理

- 使用数据管道系统加载所有实验数据
- 数据清洗、标准化和验证
- 计算派生指标

### 2. 探索性数据分析 (EDA)

- 数据分布分析
- 相关性分析
- 异常值检测

### 3. 多维指标分析

#### 性能维度
- 延迟 (latency_s)
- 吞吐量 (toks_per_s)
- 首token时间 (ttft_s)

#### 效率维度
- GPU能耗 (gpu_energy_j)
- CPU使用率 (cpu_usage_avg)
- 内存使用 (memory_used_avg_mb)

#### 质量维度
- BARTScore (bartscore)
- 任务特定质量指标
- 生成文本质量

### 4. 质效比计算

```python
# 效率得分
efficiency_score = (
    0.4 × norm_throughput + 
    0.3 × (1 - norm_latency) + 
    0.3 × (1 - norm_energy)
)

# 质效比
qe_ratio = (norm_quality + ε) / (1 + ε - efficiency_score)
```

### 5. 统计分析

- 描述性统计
- 假设检验 (t-test, ANOVA)
- 相关性分析
- 回归分析

### 6. 公平性分析

基于RLHF文献的公平性视角：

- **Fairness Gap**: `FG = max_g |mean_quality_g - mean_quality_global|`
- **Gini系数**: 质量分布不均衡度
- **Nash Social Welfare**: 公平化聚合

### 7. 可视化

- 散点图：性能权衡
- 雷达图：多维能力
- 热力图：模型-任务矩阵
- 箱线图：分布对比

## 📊 关键指标定义

### 复合指标

| 指标 | 公式 | 说明 |
|------|------|------|
| 效率得分 | `0.4×吞吐 + 0.3×(1-延迟) + 0.3×(1-能耗)` | 综合效率评价 |
| 质效比 | `(质量 + ε) / (1 + ε - 效率)` | 质量与效率的平衡 |
| 能效比 | `质量 / 能耗` | 单位能耗的质量产出 |
| 时效比 | `质量 / 延迟` | 单位时间的质量产出 |

### 归一化方法

- **Min-Max归一化**: `(x - min) / (max - min)`
- **按任务分组**: 同一任务内归一化
- **Z-score标准化**: `(x - μ) / σ` (可选)

## 🚀 快速开始

### 1. 环境准备

```bash
conda activate bartscore
set PYTHONUTF8=1
cd analysis/qe_research
```

### 2. 运行综合分析

```bash
python scripts/comprehensive_analysis.py
```

### 3. 查看结果

```bash
# 查看报告
notepad results/reports/comprehensive_report.md

# 查看图表
explorer results/figures
```

### 4. 使用Jupyter笔记本

```bash
jupyter lab notebooks/
```

## 📈 预期输出

### 1. 分析报告

- **综合分析报告**: 完整的研究发现
- **模型对比报告**: 各模型详细对比
- **任务分析报告**: 按任务类型分析
- **公平性报告**: 公平性评估结果

### 2. 可视化图表

- 性能-效率散点图
- 质效比排名柱状图
- 多维能力雷达图
- 模型-任务热力图
- 能耗分布箱线图

### 3. 数据表格

- 模型性能汇总表
- 任务统计表
- 质效比排名表
- 统计检验结果表

### 4. 导出数据

- CSV格式的分析结果
- Excel格式的汇总表
- JSON格式的元数据

## 🔍 研究流程

### 阶段1: 数据准备 (已完成)

- ✅ 数据管道系统
- ✅ JSON数据加载
- ✅ 数据验证

### 阶段2: 探索性分析 (进行中)

- [ ] 数据分布分析
- [ ] 相关性分析
- [ ] 异常值处理

### 阶段3: 深度分析

- [ ] 性能指标分析
- [ ] 效率指标分析
- [ ] 质量指标分析
- [ ] 质效比计算

### 阶段4: 高级分析

- [ ] 统计检验
- [ ] 公平性分析
- [ ] 回归建模
- [ ] 聚类分析

### 阶段5: 结果输出

- [ ] 生成报告
- [ ] 创建可视化
- [ ] 导出数据
- [ ] 撰写论文

## 📚 参考文献

### 核心文献

1. **RLHF公平性**: Towards Reward Fairness in RLHF From a Resource Allocation Perspective
2. **能效评估**: 相关的模型能效评估论文
3. **质量评估**: BARTScore和其他质量指标

### 方法论

- 多维效质比评估框架
- 公平性度量方法
- 统计分析方法

## 🛠️ 工具和依赖

### Python包

```bash
pip install pandas numpy scipy scikit-learn
pip install matplotlib seaborn plotly
pip install jupyter notebook
pip install statsmodels
```

### 数据管道

```python
from data.analize.pipeline import ExperimentDataManager
dm = ExperimentDataManager()
df = dm.load_all_data()
```

## 📝 使用示例

### 基本分析

```python
from data.analize.pipeline import ExperimentDataManager

# 加载数据
dm = ExperimentDataManager()
df = dm.load_all_data()

# 计算质效比
scores = dm.compute_composite_score()

# 按模型排名
ranking = scores.groupby('model_name')['qe_ratio'].mean().sort_values(ascending=False)
print(ranking)
```

### 模型对比

```python
# 对比两个模型
model1 = dm.get_by_model('deepseek-r1:8b')
model2 = dm.get_by_model('qwen3:8b')

# 性能对比
comparison = pd.DataFrame({
    'deepseek': model1[['latency_s', 'toks_per_s', 'gpu_energy_j']].mean(),
    'qwen': model2[['latency_s', 'toks_per_s', 'gpu_energy_j']].mean()
})
print(comparison)
```

### 任务分析

```python
# 按任务分析
for task in dm.list_tasks():
    df_task = dm.get_by_task(task)
    print(f"\n任务: {task}")
    print(df_task[['model_name', 'latency_s', 'gpu_energy_j']].groupby('model_name').mean())
```

## 🎯 下一步计划

1. **立即执行**
   - 运行综合分析脚本
   - 生成初步报告
   - 创建基础可视化

2. **短期目标** (1-2周)
   - 完成探索性分析
   - 计算所有质效比指标
   - 进行统计检验

3. **中期目标** (1个月)
   - 完成公平性分析
   - 构建评级体系
   - 撰写技术报告

4. **长期目标** (2-3个月)
   - 完善方法论
   - 撰写学术论文
   - 发布研究成果

## 📞 技术支持

- 数据管道文档: `data/analize/pipeline/README.md`
- 可视化指南: `data/analize/visualization/`
- 项目文档: `docs/`

---

**创建时间**: 2026-03-05  
**版本**: v1.0  
**状态**: 🚀 准备就绪
