# Reasoning任务帕累托前沿分析结果

## 📊 分析概述

本目录包含Reasoning任务的完整帕累托前沿分析结果，采用熵权法对人工评分进行加权，综合分析模型在质量、能耗、速度三个维度上的权衡关系。

## 📁 文件结构

```
reasoning/
├── README.md                              # 本文件
├── merged_data.csv                        # 合并后的完整数据
├── pareto_analysis_report.md              # 标准分析报告
├── pareto_analysis_report_enhanced.md     # 增强版报告（推荐）⭐
├── ANALYSIS_SUMMARY.md                    # 分析总结
├── process_visualization/                 # 分析过程可视化
│   ├── 01_entropy_weight_process.png     # 熵权法计算过程
│   ├── 02_data_distribution.png          # 数据分布分析
│   ├── 03_correlation_analysis.png       # 相关性分析
│   └── 04_pareto_frontier_process.png    # 帕累托前沿识别
├── pareto_quality_energy.png              # 质量-能耗帕累托图
├── pareto_quality_speed.png               # 质量-速度帕累托图
├── pareto_speed_energy.png                # 速度-能耗帕累托图
└── pareto_3d.png                          # 三维帕累托图
```

## 🎯 快速开始

### 查看分析结果

1. **推荐阅读**：`pareto_analysis_report_enhanced.md` - 包含完整的分析流程和可视化说明
2. **快速总结**：`ANALYSIS_SUMMARY.md` - 关键发现和推荐建议
3. **标准报告**：`pareto_analysis_report.md` - 简洁版分析报告

### 查看可视化

#### 分析过程可视化（推荐）⭐

1. **熵权法计算**：`process_visualization/01_entropy_weight_process.png`
   - 原始评分矩阵
   - 标准化数据
   - 信息熵计算
   - 多样性系数
   - 最终权重分布

2. **数据分布**：`process_visualization/02_data_distribution.png`
   - 质量、能耗、速度的分布直方图
   - 箱线图对比
   - 小提琴图
   - 描述性统计表

3. **相关性分析**：`process_visualization/03_correlation_analysis.png`
   - Pearson相关系数矩阵
   - 质量-能耗散点图
   - 质量-速度散点图
   - 趋势线和显著性检验

4. **帕累托前沿**：`process_visualization/04_pareto_frontier_process.png`
   - 2D帕累托前沿（质量-能耗、质量-速度）
   - 3D帕累托前沿
   - 前沿统计
   - 模型出现频次
   - 综合性能雷达图

#### 结果可视化

- `pareto_quality_energy.png` - 质量与能耗的权衡
- `pareto_quality_speed.png` - 质量与速度的权衡
- `pareto_speed_energy.png` - 速度与能耗的权衡
- `pareto_3d.png` - 三维空间的帕累托前沿

## 🔑 关键发现

### 熵权法权重分配

| 维度 | 权重 | 说明 |
|------|------|------|
| 清晰度 | 27.64% | 权重最高，模型间差异最大 |
| 正确性 | 19.24% | 推理准确性的重要性 |
| 完整性 | 18.51% | 答案完整度 |
| 效率 | 17.78% | 推理效率 |
| 严谨性 | 16.83% | 逻辑严谨性 |

### 帕累托前沿模型

#### 质量-能耗前沿（5个模型）
1. qwen25_7b_hf_4bit - 最高质量
2. deepseek_8b_ol_q4km - 质量优秀
3. gemma_4b_ol_q4km - 平衡最优 ⭐
4. gemma_2b_hf_8bit - 低能耗
5. gemma_2b_hf_4bit - 最低能耗

#### 质量-速度前沿（4个模型）
1. qwen25_7b_hf_4bit - 最高质量
2. deepseek_8b_ol_q4km - 质量优秀
3. gemma_4b_ol_q4km - 平衡最优 ⭐
4. qwen_4b_ol_q4km - 最快速度

#### 3D帕累托前沿（6个模型）
综合评分最高：**gemma_4b_ol_q4km** (0.805) ⭐⭐⭐

## 💡 应用场景推荐

### 场景1：学术研究 / 关键决策
- **推荐**：qwen25_7b_hf_4bit
- **特点**：质量最高（1.000），适合高准确性要求
- **代价**：能耗较高（1267.88 J），速度较慢（19.31 t/s）

### 场景2：实时应用 / 高并发
- **推荐**：qwen_4b_ol_q4km
- **特点**：速度最快（64.56 t/s），响应时间短
- **代价**：质量中等（0.570）

### 场景3：通用应用（推荐）⭐⭐⭐
- **推荐**：gemma_4b_ol_q4km
- **特点**：三维度平衡最优，综合评分最高
- **性能**：质量 0.889 | 速度 49.53 t/s | 能耗 340.86 J

### 场景4：边缘设备 / 移动端
- **推荐**：gemma_2b_hf_4bit
- **特点**：能耗最低（58.13 J），能效比最高
- **代价**：质量较低（0.000）

## 📈 数据统计

- **分析模型数量**：11个
- **质量得分范围**：0.000 - 1.000
- **能耗范围**：58.13 - 1267.88 J
- **速度范围**：7.49 - 64.56 tokens/s

## 🔬 方法论

### 熵权法

客观赋权方法，通过信息熵自动确定权重：

```
1. 数据标准化：x'ij = (xij - min(xj)) / (max(xj) - min(xj))
2. 计算概率：pij = x'ij / Σx'ij
3. 信息熵：Ej = -1/ln(n) * Σ(pij * ln(pij))
4. 多样性：Dj = 1 - Ej
5. 权重：wj = Dj / ΣDj
```

### 帕累托最优

一个解被称为帕累托最优，当且仅当不存在其他解在所有目标上都不差于它，且至少在一个目标上优于它。

### 综合评分

```
综合评分 = 质量(归一化) × 0.4 + 速度(归一化) × 0.3 + 能效(归一化) × 0.3
```

## 🛠️ 重新运行分析

### 标准版本
```bash
python analysis/qe_research/scripts/pareto_analysis_reasoning.py
```

### 增强版本（包含完整可视化）
```bash
python analysis/qe_research/scripts/pareto_analysis_reasoning_enhanced.py
```

## 📝 引用

如需引用本分析结果，请参考：

```
GenAI模型能效评级体系 - Reasoning任务帕累托前沿分析
分析方法：熵权法 + 帕累托前沿识别
分析时间：2026-03-06
```

## 📧 联系方式

如有问题或建议，请查看项目根目录的 `AGENTS.md` 文件。

---

*最后更新：2026-03-06*
