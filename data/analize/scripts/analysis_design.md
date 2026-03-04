# 多模型实验数据分析设计文档

## 1. 分析目标

本分析旨在对 12 个大语言模型（涵盖不同参数规模、量化方式和推理框架）的实验数据进行系统性评估，建立基于多维效质比的综合评价体系，为模型选型和能效优化提供数据支持。

### 1.1 核心研究问题

1. **模型规模 vs 能效权衡**：不同参数量（2B-8B）模型的质效比如何？
2. **量化精度影响**：4bit vs 8bit 量化对质量和能耗的影响？
3. **推理框架对比**：Ollama (Q4_K_M) vs HuggingFace (4bit/8bit) 的性能差异？
4. **任务适配性**：不同模型在各任务类型（code, creative, math, qa, summary）上的表现？
5. **帕累托最优**：在质量-能效空间中，哪些模型构成最优集合？

### 1.2 待分析模型清单

| 模型名称 | 参数量 | 量化方式 | 推理框架 | 数据目录 |
|---------|--------|---------|---------|---------|
| deepseek_8b_ol_q4km | 8B | Q4_K_M | Ollama | data/deepseek_8b_ol_q4km/ |
| gemma_2b_hf_4bit | 2B | 4bit | HuggingFace | data/gemma_2b_hf_4bit/ |
| gemma_2b_hf_8bit | 2B | 8bit | HuggingFace | data/gemma_2b_hf_8bit/ |
| gemma_4b_ol_q4km | 4B | Q4_K_M | Ollama | data/gemma_4b_ol_q4km/ |
| phi3_4b_hf_4bit | 4B | 4bit | HuggingFace | data/phi3_4b_hf_4bit/ |
| phi3_4b_hf_8bit | 4B | 8bit | HuggingFace | data/phi3_4b_hf_8bit/ |
| qwen_4b_ol_q4km | 4B | Q4_K_M | Ollama | data/qwen_4b_ol_q4km/ |
| qwen_8b_ol_q4km | 8B | Q4_K_M | Ollama | data/qwen_8b_ol_q4km/ |
| qwen25_3b_hf_4bit | 3B | 4bit | HuggingFace | data/qwen25_3b_hf_4bit/ |
| qwen25_3b_hf_8bit | 3B | 8bit | HuggingFace | data/qwen25_3b_hf_8bit/ |
| qwen25_7b_hf_4bit | 7B | 4bit | HuggingFace | data/qwen25_7b_hf_4bit/ |
| qwen25_7b_hf_8bit | 7B | 8bit | HuggingFace | data/qwen25_7b_hf_8bit/ |

**模型分组**：
- 按参数量：2B (1), 3B (2), 4B (4), 7B (1), 8B (2)
- 按量化：4bit/Q4 (7), 8bit (5)
- 按框架：Ollama (4), HuggingFace (8)
- 按模型系列：DeepSeek (1), Gemma (3), Phi3 (2), Qwen (6)

## 2. 数据结构分析

### 2.1 原始数据格式

基于样本数据（`deepseek_8b_ol_q4km/experiment_results_20260303_203028_summary.json`），每个实验记录包含：

**核心字段**：
```json
{
  "experiment_id": "唯一标识",
  "config_ref": {
    "model": "模型名称",
    "task_type": "任务类型 (code/creative/math/qa/summary)",
    "temperature": "生成温度",
    "max_tokens": "最大token数"
  },
  "performance": {
    "total_time_seconds": "总推理时间",
    "token_count": "生成token数",
    "throughput_tokens_per_sec": "吞吐量",
    "latency_per_token_ms": "每token延迟",
    "ttft_seconds": "首token时间"
  },
  "resources": {
    "gpu_power_avg_w": "平均GPU功耗",
    "gpu_energy_j": "总GPU能耗",
    "gpu_util_avg": "平均GPU利用率",
    "gpu_mem_peak_mb": "峰值显存",
    "cpu_energy_j_approx": "估算CPU能耗"
  },
  "quality": {
    "bartscore": "BARTScore质量得分（部分任务）",
    "generated_text_length": "生成文本长度"
  }
}
```

### 2.2 数据完整性检查

**必需字段验证**：
- 所有模型是否都有 5 种任务类型的数据？
- 每个任务是否有足够的样本数（建议 ≥ 3）？
- 关键指标是否存在缺失值（`null`）？

**异常值检测**：
- 功耗异常：`gpu_power_avg_w` 是否在合理范围（10-100W）？
- 延迟异常：`latency_per_token_ms` 是否过高（> 200ms）？
- 能耗异常：`gpu_energy_j` 是否与时间成正比？

## 3. 分析指标体系

### 3.1 原始指标（直接提取）

| 类别 | 指标 | 符号 | 单位 | 数据来源 |
|------|------|------|------|---------|
| **性能** | 吞吐量 | $Throughput$ | tokens/s | `performance.throughput_tokens_per_sec` |
| | 总延迟 | $Latency$ | s | `performance.total_time_seconds` |
| | 首token延迟 | $TTFT$ | s | `performance.ttft_seconds` |
| | 每token延迟 | $TPOT$ | ms/token | `performance.latency_per_token_ms` |
| **能耗** | GPU平均功耗 | $P_{GPU}$ | W | `resources.gpu_power_avg_w` |
| | GPU总能耗 | $E_{GPU}$ | J | `resources.gpu_energy_j` |
| | CPU能耗（估算） | $E_{CPU}$ | J | `resources.cpu_energy_j_approx` |
| **资源** | GPU利用率 | $U_{GPU}$ | % | `resources.gpu_util_avg` |
| | 峰值显存 | $M_{GPU}$ | MB | `resources.gpu_mem_peak_mb` |
| **质量** | BARTScore | $Q_{BART}$ | [-∞, 0] | `quality.bartscore` |
| | 文本长度 | $L_{text}$ | chars | `quality.generated_text_length` |

### 3.2 派生指标（计算得出）

| 指标 | 符号 | 计算公式 | 说明 |
|------|------|---------|------|
| **每token能耗** | $E_{token}$ | $E_{GPU} / N_{tokens}$ | 能效核心指标 |
| **每瓦性能** | $PPW$ | $Throughput / P_{GPU}$ | 性能功耗比 |
| **总能耗** | $E_{total}$ | $E_{GPU} + E_{CPU}$ | 系统总能耗 |
| **归一化质量** | $Q_{norm}$ | Min-Max归一化（按任务） | [0, 1] |
| **归一化能效** | $E_{norm}$ | $1 - \frac{E_{token} - E_{min}}{E_{max} - E_{min}}$ | [0, 1]，越大越好 |
| **归一化吞吐** | $T_{norm}$ | $\frac{Throughput - T_{min}}{T_{max} - T_{min}}$ | [0, 1] |
| **归一化延迟** | $L_{norm}$ | $1 - \frac{Latency - L_{min}}{L_{max} - L_{min}}$ | [0, 1]，越大越好 |

### 3.3 复合指标（综合评估）

| 指标 | 符号 | 计算公式 | 权重 |
|------|------|---------|------|
| **效率得分** | $Eff_{score}$ | $0.4 \times T_{norm} + 0.3 \times L_{norm} + 0.3 \times E_{norm}$ | 综合效率 |
| **质效比** | $QE_{ratio}$ | $\frac{Q_{norm} + 0.01}{1.01 - Eff_{score}}$ | 质量-效率权衡 |
| **最终得分** | $Score_{final}$ | $Q_{norm} \times PPW$ | 质量×能效 |

## 4. 分析维度与方法

### 4.1 单模型分析

**目标**：评估每个模型的基础性能

**分析内容**：
1. **任务表现分布**：各任务类型的性能、能耗、质量分布（箱线图）
2. **稳定性评估**：同一任务多次运行的标准差（变异系数）
3. **资源利用**：GPU利用率、显存占用、温度分布
4. **能耗分解**：GPU vs CPU能耗占比

**输出**：
- 单模型性能报告（Markdown）
- 任务分布箱线图（PNG）
- 资源利用雷达图（PNG）

### 4.2 横向对比分析

**目标**：识别最优模型和权衡关系

**对比维度**：

1. **参数量对比**（2B vs 3B vs 4B vs 7B vs 8B）
   - 质量提升 vs 能耗增加
   - 边际效益分析

2. **量化精度对比**（4bit vs 8bit）
   - 同一模型系列的量化影响
   - 质量损失 vs 能耗节省

3. **推理框架对比**（Ollama vs HuggingFace）
   - 同参数量模型的框架差异
   - 吞吐量、延迟、能耗对比

4. **模型系列对比**（DeepSeek vs Gemma vs Phi3 vs Qwen）
   - 同参数量下的模型架构差异
   - 任务适配性对比

**输出**：
- 吞吐量 vs 延迟散点图（按参数量着色）
- 能耗 vs 质量散点图（按量化方式着色）
- 质效比柱状图（按模型排序）
- 帕累托前沿图（质量-能效空间）

### 4.3 任务维度分析（重点强化）

**目标**：识别任务特性和最适模型，支持应用场景导向的模型选择

**分析内容**：

1. **任务-指标分析**
   - 每个任务的各项指标分布（箱线图）
   - 识别任务难度和区分度
   - 任务间差异显著性检验（ANOVA）

2. **模型-任务适配性矩阵**
   - 热力图：模型 × 任务 × 指标 → 得分
   - 为每个任务的每个指标推荐Top 3模型
   - 识别"全能型"模型 vs "专家型"模型

3. **应用场景推荐**
   - **场景一：代码生成助手**
     - 关键指标：`pass_at_1`, `compilation_rate`
     - 推荐模型：在这些指标上表现最优的模型
   
   - **场景二：创意写作辅助**
     - 关键指标：`distinct_2`, `self_bleu`（低）
     - 推荐模型：多样性高的模型
   
   - **场景三：数学题解答**
     - 关键指标：`exact_match`, `numerical_match`
     - 推荐模型：准确性最高的模型
   
   - **场景四：智能问答系统**
     - 关键指标：`exact_match`, `f1_score`, `bertscore_f1`
     - 推荐模型：准确性和语义理解均衡的模型
   
   - **场景五：文档摘要工具**
     - 关键指标：`rouge_l`, `bertscore_f1`, `compression_ratio`
     - 推荐模型：信息保留和简洁性均衡的模型
   
   - **场景六：综合应用（多任务）**
     - 关键指标：所有任务的核心指标
     - 推荐模型：帕累托前沿分析，无明显短板的模型

4. **指标权衡分析**
   - 散点图：指标A vs 指标B（如准确性 vs 多样性）
   - 识别不可兼得的指标对
   - 为用户提供权衡建议

**输出**：
- 任务-指标分布箱线图
- 模型-任务-指标三维热力图
- 应用场景推荐表（Markdown）
- 指标权衡散点图

### 4.4 帕累托前沿分析

**目标**：识别质量-能效空间的最优模型集合

**方法**：
1. 在二维空间（质量 vs 能效）绘制所有模型
2. 识别帕累托最优解：不被其他模型同时在质量和能效上超越
3. 分析权衡曲线：质量提升的能耗代价

**输出**：
- 帕累托前沿散点图
- 最优模型集合列表
- 权衡分析报告

### 4.5 统计显著性检验

**目标**：验证模型间差异的统计显著性

**方法**：
1. **方差分析（ANOVA）**：检验模型间性能差异
2. **事后检验（Tukey HSD）**：识别显著不同的模型对
3. **效应量（Cohen's d）**：量化差异大小

**输出**：
- 显著性检验结果表
- 置信区间图

## 5. 可视化设计

### 5.1 核心图表（必需）

1. **吞吐量 vs 延迟散点图**
   - X轴：Latency (s)
   - Y轴：Throughput (tokens/s)
   - 颜色：参数量
   - 大小：能耗
   - 标注：模型名称

2. **能耗 vs 质量散点图**
   - X轴：E_token (J/token)
   - Y轴：Q_norm (归一化质量)
   - 颜色：量化方式
   - 形状：推理框架
   - 帕累托前沿线

3. **质效比柱状图**
   - X轴：模型名称（按QE_ratio排序）
   - Y轴：QE_ratio
   - 颜色：任务类型（分组柱状图）

4. **综合能力雷达图**
   - 维度：吞吐量、延迟、能效、质量、显存占用
   - 每个模型一条线
   - 归一化到 [0, 1]

5. **模型-任务热力图**
   - 行：模型
   - 列：任务类型
   - 值：QE_ratio
   - 颜色：渐变（红-黄-绿）

### 5.2 辅助图表（可选）

6. **箱线图**：各模型的延迟分布（评估稳定性）
7. **相关性矩阵**：指标间相关性（Pearson系数）
8. **功耗轨迹图**：时间序列功耗曲线（选取代表性样本）
9. **显存占用对比**：柱状图，按模型排序
10. **成本效益分析**：单位成本质量（CPQ）对比

### 5.3 可视化规范

**配色方案**：
- 参数量：渐变色（浅蓝 → 深蓝）
- 量化方式：4bit（橙色），8bit（绿色）
- 推理框架：Ollama（圆形），HuggingFace（方形）
- 模型系列：DeepSeek（红），Gemma（蓝），Phi3（绿），Qwen（紫）

**字体设置**：
- 中文：Microsoft YaHei（优先）或 SimHei
- 英文：Arial
- 标题：14pt，加粗
- 标签：10pt

**图表尺寸**：
- 单图：10×6 英寸（适合报告）
- 组图：12×8 英寸
- DPI：300（高清）

## 6. 实现计划

### 6.0 质量评估（新增，优先执行）

**脚本**：`evaluate_all_models.py`

**核心理念**：**任务-模型适配性分析** > 主观综合评分

**功能**：
1. 为所有模型的生成结果计算多维度质量指标
2. 保留所有原始指标，避免主观加权
3. 生成任务-模型适配性分析报告
4. 可选：使用客观方法（PCA、熵权法、TOPSIS）生成综合分数

**评估指标体系**（多维度保留）：

| 任务类型 | 核心维度 | 具体指标 | 方向 |
| -------- | -------- | -------- | ---- |
| code | 正确性 | pass_at_1, compilation_rate | ↑ |
| | 质量 | code_length, complexity | ↓ |
| creative | 多样性 | distinct_1, distinct_2, self_bleu | ↑/↓ |
| | 流畅性 | perplexity, avg_length | ↓/- |
| math | 准确性 | exact_match, numerical_match | ↑ |
| | 推理 | has_steps, step_count | ↑ |
| qa | 准确性 | exact_match, f1_score | ↑ |
| | 语义 | bertscore_f1, rouge_l | ↑ |
| summary | 内容 | rouge_1, rouge_2, rouge_l | ↑ |
| | 语义 | bertscore_f1, bartscore_info | ↑ |
| | 简洁性 | compression_ratio | 0.2-0.4 |

**客观综合评分方法**（可选）：

1. **熵权法**（推荐）：
   - 根据指标信息熵自动确定权重
   - 完全数据驱动，无主观性
   - 适用于所有任务类型

2. **主成分分析（PCA）**：
   - 自动发现指标间主要变化方向
   - 可解释性强
   - 需要足够样本数

3. **TOPSIS**：
   - 基于理想解的距离排序
   - 可处理不同方向的指标
   - 结果直观

4. **不聚合**（默认）：
   - 保留所有原始指标
   - 用于任务-模型适配性分析
   - 最客观，最灵活

**运行方式**：
```bash
# 默认：不聚合，保留所有原始指标
python evaluate_all_models.py

# 使用熵权法聚合
python evaluate_all_models.py --aggregation entropy

# 使用PCA聚合
python evaluate_all_models.py --aggregation pca

# 使用TOPSIS聚合
python evaluate_all_models.py --aggregation topsis
```

**输出文件**：
- `quality_scores_detailed.csv`：所有原始指标
- `task_model_matching.csv`：任务-模型适配性分析（每个指标的Top 3模型）

**实现阶段**：

**阶段一（必需，2-3小时）**：
- ✅ Exact Match
- ✅ F1 Score
- ✅ Distinct-N
- ✅ 编译检查
- ✅ ROUGE

**阶段二（推荐，3-4小时）**：
- ⏳ BERTScore
- ⏳ BARTScore（使用已有工具）
- ⏳ 客观聚合方法（熵权法、PCA、TOPSIS）

**阶段三（可选，4-6小时）**：
- ⏳ Pass@k（需要测试用例执行）
- ⏳ 困惑度计算

**依赖安装**：
```bash
pip install rouge nltk bert-score transformers torch scikit-learn
python -c "import nltk; nltk.download('punkt')"
```

**详细设计**：参见 `quality_evaluation_system.md`

### 6.1 数据加载与预处理

**脚本**：`load_and_preprocess.py`

**功能**：
1. 遍历所有模型目录，加载 `*_summary.json` 文件
2. 提取关键字段，构建统一DataFrame
3. **合并质量评分数据**（从 `quality_scores.csv`）
4. 数据清洗：
   - 处理缺失值（`null` → NaN）
   - 异常值检测（3σ原则）
   - 数据类型转换
5. 保存为 `data/analize/pre_data/all_models_raw.csv`

**输出字段**：
```
model_name, task_type, experiment_id, timestamp,
throughput_tps, latency_s, ttft_s, tpot_ms,
gpu_power_w, gpu_energy_j, cpu_energy_j, total_energy_j,
gpu_util_pct, gpu_mem_mb, gpu_temp_c,
# 质量指标（多维度，不聚合）
exact_match, f1_score, bertscore_f1, rouge_l, distinct_2, 
pass_at_1, compilation_rate, numerical_match, self_bleu,
bartscore_info, bartscore_faith, compression_ratio,
# 可选：客观聚合分数
quality_score_entropy, quality_score_pca, quality_score_topsis,
text_length, token_count,
temperature, max_tokens
```

**注意**：
- 默认不生成 `quality_score_*`，除非指定聚合方法
- 所有原始指标都保留，用于后续分析

### 6.2 指标计算

**脚本**：`calculate_metrics.py`

**功能**：
1. 计算派生指标：`e_token`, `ppw`, `e_total`
2. 按任务分组归一化：`q_norm`（使用 `quality_score`）, `e_norm`, `t_norm`, `l_norm`
3. 计算复合指标：`eff_score`, `qe_ratio`, `score_final`
4. 保存为 `data/analize/pre_data/all_models_metrics.csv`

### 6.3 统计分析

**脚本**：`statistical_analysis.py`

**功能**：
1. 描述性统计：均值、标准差、中位数、四分位数
2. 方差分析（ANOVA）：模型间差异显著性
3. 事后检验（Tukey HSD）
4. 相关性分析（Pearson）
5. 保存为 `data/analize/pre_data/statistical_summary.csv`

### 6.4 可视化生成

**脚本**：`generate_visualizations.py`

**功能**：
1. 生成 10 张核心图表（见 5.1 和 5.2）
2. 保存为 PNG（300 DPI）
3. 输出目录：`data/analize/figures/`

### 6.5 报告生成

**脚本**：`generate_report.py`

**功能**：
1. 基于模板生成 Markdown 报告
2. 嵌入图表和数据表
3. 自动化结论和建议
4. 保存为 `data/analize/analysis_report.md`

### 6.6 主控脚本

**脚本**：`analyze_all_models.py`

**功能**：
1. **首先执行质量评估**（`evaluate_all_models.py`）
2. 依次调用数据加载、指标计算、统计分析、可视化、报告生成
3. 进度显示和日志记录
4. 错误处理和异常报告
5. 生成完整分析报告

**运行方式**：
```bash
conda activate bartscore
set PYTHONUTF8=1
cd data/analize/scripts

# 完整流程（包含质量评估）
python analyze_all_models.py --with-quality-eval

# 仅分析（跳过质量评估，使用已有结果）
python analyze_all_models.py
```

## 7. 输出文件结构

```
data/analize/
├── pre_data/                          # 预处理数据
│   ├── quality_scores.csv             # 质量评分（新增）
│   ├── quality_summary.csv            # 质量统计（新增）
│   ├── all_models_raw.csv             # 原始数据汇总
│   ├── all_models_metrics.csv         # 计算指标
│   └── statistical_summary.csv        # 统计摘要
├── figures/                           # 可视化图表
│   ├── 00_quality_metrics_correlation.png  # 质量指标相关性（新增）
│   ├── 01_throughput_vs_latency.png
│   ├── 02_energy_vs_quality.png
│   ├── 03_qe_ratio_bars.png
│   ├── 04_radar_chart.png
│   ├── 05_heatmap_model_task.png
│   ├── 06_boxplot_latency.png
│   ├── 07_correlation_matrix.png
│   ├── 08_power_trace_sample.png
│   ├── 09_memory_comparison.png
│   └── 10_cost_analysis.png
├── scripts/                           # 分析脚本
│   ├── quality_evaluation/            # 质量评估模块（新增）
│   │   ├── __init__.py
│   │   ├── base_evaluator.py
│   │   ├── code_evaluator.py
│   │   ├── creative_evaluator.py
│   │   ├── math_evaluator.py
│   │   ├── qa_evaluator.py
│   │   ├── summary_evaluator.py
│   │   └── metrics/
│   ├── evaluate_all_models.py         # 质量评估主脚本（新增）
│   ├── analyze_all_models.py          # 主控脚本
│   ├── load_and_preprocess.py
│   ├── calculate_metrics.py
│   ├── statistical_analysis.py
│   ├── generate_visualizations.py
│   ├── generate_report.py
│   ├── analysis_design.md             # 本文档
│   └── quality_evaluation_system.md   # 质量评估设计（新增）
└── analysis_report.md                 # 最终报告
```

## 8. 质量控制

### 8.1 数据验证

- [ ] 所有模型数据完整性检查
- [ ] 缺失值比例 < 5%
- [ ] 异常值标记和处理
- [ ] 数据类型一致性

### 8.2 计算验证

- [ ] 手动验证 3 个样本的指标计算
- [ ] 归一化范围检查（[0, 1]）
- [ ] 复合指标合理性检查

### 8.3 可视化验证

- [ ] 图表标签完整（标题、轴标签、图例）
- [ ] 中文显示正常（无乱码）
- [ ] 颜色区分清晰
- [ ] 数据点可读（无重叠）

### 8.4 报告验证

- [ ] 结论与数据一致
- [ ] 推荐建议可操作
- [ ] 格式规范（Markdown）
- [ ] 引用图表正确

## 9. 时间安排

| 阶段 | 任务 | 预计时间 | 负责人 |
|------|------|---------|--------|
| 1 | 数据加载与预处理 | 2 小时 | - |
| 2 | 指标计算 | 1 小时 | - |
| 3 | 统计分析 | 1 小时 | - |
| 4 | 可视化生成 | 2 小时 | - |
| 5 | 报告生成 | 1 小时 | - |
| 6 | 质量检查与修订 | 1 小时 | - |
| **总计** | | **8 小时** | |

## 10. 风险与应对

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|---------|
| 数据缺失严重 | 高 | 中 | 标记缺失模型，仅分析完整数据 |
| BARTScore缺失 | 中 | 高 | 使用文本长度作为替代质量指标 |
| 中文乱码 | 低 | 低 | 强制UTF-8编码，回退英文标签 |
| 内存不足 | 中 | 低 | 分批处理，减少缓存 |
| 计算时间过长 | 低 | 低 | 优化代码，使用向量化操作 |

## 11. 后续扩展

1. **交互式仪表板**：使用 Plotly Dash 或 Streamlit
2. **实时监控**：集成到实验流程，实时更新分析
3. **自动化报告**：定期生成周报/月报
4. **模型推荐系统**：基于用户需求推荐最优模型
5. **成本计算器**：输入使用量，输出预估成本

---

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**作者**: Kiro AI Assistant  
**审核状态**: 待审核
