# GPU能耗假设检验分析 - 执行总结

## 📋 任务完成情况

✅ **已完成**: 基于metric_tables数据的GPU能耗假设检验分析

**生成时间**: 2026-03-08 14:15:03

## 🎯 分析目标

使用 `analysis/qe_research/results/metric_tables/01_avg_gpu_energy.csv` 中的数据，通过统计假设检验方法回答以下问题:

1. **不同任务类型的GPU能耗是否存在显著差异？**
2. **不同模型的GPU能耗是否存在显著差异？**
3. **在同一任务下，不同模型的GPU能耗是否存在显著差异？**

## 📊 数据概况

- **任务类型**: 8种 (code, creative, math, multi_turn, qa, reasoning, summary, translation)
- **模型数量**: 12个
- **有效数据点**: 90条
- **剔除空值**: 6条

## 🔬 核心发现

### 1. 任务间差异 (RQ1)

**结论**: ✅ **存在极显著差异**

- **检验方法**: Kruskal-Wallis H检验
- **H统计量**: 39.0522
- **p值**: < 0.0001 (***极显著***)
- **能耗范围**: 339.04 J (summary) ~ 1790.55 J (code)
- **差异倍数**: 5.28x

**事后检验发现8对任务间存在显著差异**:
- code vs qa (p=0.0004)
- code vs summary (p=0.0005)
- code vs translation (p=0.0010)
- math vs multi_turn (p=0.0008)
- multi_turn vs qa (p=0.0001)
- multi_turn vs reasoning (p=0.0013)
- multi_turn vs summary (p=0.0001)
- multi_turn vs translation (p=0.0001)

### 2. 模型间差异 (RQ2)

**结论**: ✅ **存在极显著差异**

- **检验方法**: Kruskal-Wallis H检验
- **H统计量**: 42.9883
- **p值**: < 0.0001 (***极显著***)
- **能耗范围**: 225.27 J (google--gemma-2b-it:4bit) ~ 6271.11 J (qwen--qwen2.5-7b-instruct:8bit)
- **差异倍数**: 27.84x

**最节能模型TOP 3**:
1. google--gemma-2b-it:4bit (225.27 J)
2. google--gemma-2b-it:8bit (356.15 J)
3. gemma3:4b (358.85 J)

**最耗能模型TOP 3**:
1. qwen--qwen2.5-7b-instruct:8bit (6271.11 J)
2. qwen--qwen2.5-7b-instruct:4bit (1523.98 J)
3. qwen--qwen2.5-3b-instruct:8bit (1187.36 J)

### 3. 任务内模型差异 (RQ3)

**结论**: ❌ **在所有8个任务中均未发现显著差异**

- 所有任务的p值均 > 0.44
- 可能原因: 样本量较小（每个任务-模型组合仅1个数据点）

## 📈 生成的输出文件

### 表格文件 (6个CSV)
1. `hypothesis_task_descriptive.csv` - 任务描述性统计
2. `hypothesis_task_test.csv` - 任务间主检验结果
3. `hypothesis_task_posthoc.csv` - 任务间事后比较
4. `hypothesis_model_descriptive.csv` - 模型描述性统计
5. `hypothesis_model_test.csv` - 模型间主检验结果
6. `hypothesis_models_within_task.csv` - 任务内模型检验结果

### 图表文件 (3个PNG)
1. `hypothesis_task_boxplot.png` - 任务间能耗箱线图
2. `hypothesis_model_boxplot.png` - 模型间能耗箱线图
3. `hypothesis_task_model_significance.png` - 任务-模型显著性图

### 报告文件 (1个MD)
1. `GPU_ENERGY_HYPOTHESIS_TESTING_REPORT.md` - 完整的假设检验报告

## 💡 关键洞察

### 任务特性影响
- **高能耗任务**: code (1790.55 J), multi_turn (1613.21 J), creative (1038.47 J)
- **低能耗任务**: summary (339.04 J), qa (387.44 J), translation (472.00 J)
- **启示**: 任务复杂度和输出长度是能耗的主要影响因素

### 模型效率差异
- **小模型优势**: 2B-4B参数模型能耗显著低于7B+模型
- **量化影响**: 4bit量化通常比8bit更节能
- **架构差异**: Gemma系列模型整体能耗较低

### 实践建议
1. **能耗优先场景**: 选择小参数量模型（如gemma-2b-it:4bit）
2. **性能平衡场景**: 根据任务类型选择合适规模的模型
3. **系统优化**: 对高能耗任务考虑任务分解或批处理

## 🔧 使用的统计方法

- **主检验**: Kruskal-Wallis H检验（非参数）
- **事后检验**: Mann-Whitney U检验 + Bonferroni校正
- **显著性水平**: α = 0.05
- **软件**: Python 3.10 + scipy.stats

## 📂 文件位置

- **脚本**: `analysis/qe_research/scripts/hypothesis_test_metric_tables.py`
- **报告**: `analysis/qe_research/results/raw_analysis/reports/GPU_ENERGY_HYPOTHESIS_TESTING_REPORT.md`
- **表格**: `analysis/qe_research/results/raw_analysis/tables/`
- **图表**: `analysis/qe_research/results/raw_analysis/figures/`

## 🚀 如何使用

### 重新运行分析
```bash
conda activate bartscore
python analysis/qe_research/scripts/hypothesis_test_metric_tables.py
```

### 查看完整报告
```bash
# Windows
start analysis/qe_research/results/raw_analysis/reports/GPU_ENERGY_HYPOTHESIS_TESTING_REPORT.md

# 或直接打开文件
```

### 查看图表
```bash
# 打开figures目录
explorer analysis\qe_research\results\raw_analysis\figures
```

## ⚠️ 研究局限性

1. **样本量**: 每个任务-模型组合仅1个数据点，限制了任务内检验的效力
2. **数据范围**: 仅分析了特定模型和任务类型
3. **环境因素**: 未考虑硬件配置、温度等环境变量
4. **质量权衡**: 未综合考虑能耗与输出质量的权衡

## 📝 结论

通过严格的统计假设检验，本研究证实:

1. ✅ **不同任务类型的GPU能耗存在极显著差异** (p < 0.0001)
2. ✅ **不同模型的GPU能耗存在极显著差异** (p < 0.0001)
3. ⚠️ **任务内模型差异需要更多数据支持**

这些发现为模型选择、系统优化和资源分配提供了科学依据。

---

**分析完成时间**: 2026-03-08 14:15:03  
**分析师**: Kiro AI Assistant  
**状态**: ✅ 完成
