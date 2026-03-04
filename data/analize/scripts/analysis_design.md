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

### 2.1 数据准备状态 ✅

**状态**: 数据提取阶段已完成（2026-03-04）

**已完成工作**:
1. ✅ 从 `*_raw.json` 提取完整回答（非截断）
2. ✅ 从 `*_summary.json` 提取性能和资源指标
3. ✅ 生成统一的 CSV 格式数据
4. ✅ 创建对比矩阵（行=模型，列=题号）
5. ✅ 数据验证（质量评分：85/100）

**数据统计**:
- 总样本数：446 条
- 模型数量：12 个
- 任务类型：8 种（code, creative, math, multi_turn, qa, reasoning, summary, translation）
- 数据文件大小：674 KB（完整回答）

### 2.2 当前数据格式

**主数据文件**: `data/analize/pre_data/responses_raw.csv`

**字段结构**:
```
experiment_id       - 实验唯一标识
model              - 模型名称
task_type          - 任务类型
timestamp          - 时间戳
prompt             - 输入提示词（完整）
response           - 模型回答（完整，非截断）
response_length    - 回答字符长度
token_count        - 生成的 token 数
throughput_tps     - 吞吐量（tokens/秒）
latency_s          - 总延迟（秒）
gpu_energy_j       - GPU 能耗（焦耳）
gpu_power_avg_w    - GPU 平均功耗（瓦特）
bartscore          - BARTScore（待评估）
has_reference      - 是否有参考答案
temperature        - 生成温度
max_tokens         - 最大 token 限制
```

**对比矩阵**: `data/analize/pre_data/comparison_matrices/`
- 8 个任务目录
- 每个任务包含：回答对比 + 7 个性能指标矩阵
- 格式：行=模型，列=题号（q01, q02, ...）

### 2.3 数据完整性验证结果 ✅

**验证完成**（2026-03-04）:

✅ **完整性检查**:
- 所有关键字段完整
- 完整回答已提取（非截断预览）
- 性能指标齐全

✅ **数据质量**:
- 质量评分：85/100
- 无异常值（功耗、延迟、能耗均在合理范围）
- 特殊字符处理正确（换行符、引号等）

⚠️ **已知问题**（轻微，不影响分析）:
- 11 个空回答（2.47%）- 生成失败
- qwen25_7b_hf_8bit 只有 6 个样本（其他模型 40 个）
- bartscore 全部缺失（需要后续质量评估补充）

**详细报告**: 参见 `data/analize/DATA_PREPARATION_COMPLETE.md`

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

## 6. 实现计划与当前进度

### 当前进度总览

| 阶段 | 脚本 | 状态 | 完成时间 |
|------|------|------|---------|
| 0. 数据提取 | `extract_responses.py` | ✅ 已完成 | 2026-03-04 |
| 0. 对比矩阵 | `create_comparison_matrix.py` | ✅ 已完成 | 2026-03-04 |
| 0. 数据验证 | `verify_data.py` | ✅ 已完成 | 2026-03-04 |
| 1. 质量评估 | `evaluate_all_models.py` | ⏳ 进行中 | - |
| 2. 数据预处理 | `load_and_preprocess.py` | ⏸️ 待开始 | - |
| 3. 指标计算 | `calculate_metrics.py` | ⏸️ 待开始 | - |
| 4. 统计分析 | `statistical_analysis.py` | ⏸️ 待开始 | - |
| 5. 可视化 | `generate_visualizations.py` | ⏸️ 待开始 | - |
| 6. 报告生成 | `generate_report.py` | ⏸️ 待开始 | - |
| 7. 主控脚本 | `analyze_all_models.py` | ⏸️ 待开始 | - |

### 6.0 数据提取与准备 ✅ 已完成

**脚本**: 
- `extract_responses.py` - 数据提取
- `create_comparison_matrix.py` - 对比矩阵生成
- `verify_data.py` - 数据验证
- `view_samples.py` - 样本查看

**完成内容**:
1. ✅ 从 `*_raw.json` 提取完整回答（674 KB）
2. ✅ 从 `*_summary.json` 提取性能指标
3. ✅ 生成 `responses_raw.csv` 和 `responses_summary.csv`
4. ✅ 创建对比矩阵（8任务 × 8文件 = 64个CSV）
5. ✅ 数据验证（质量评分：85/100）
6. ✅ 完善文档（5个说明文档）

**输出文件**:
- `pre_data/responses_raw.csv` (674 KB)
- `pre_data/responses_summary.csv` (20 KB)
- `pre_data/comparison_matrices/` (~2 MB)
  - `overview.csv`
  - `code/` (8文件)
  - `creative/` (8文件)
  - `math/` (8文件)
  - `multi_turn/` (8文件)
  - `qa/` (8文件)
  - `reasoning/` (8文件)
  - `summary/` (8文件)
  - `translation/` (8文件)

**详细报告**: 参见 `DATA_PREPARATION_COMPLETE.md`

### 6.1 质量评估 ⏳ 当前阶段

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

**输出文件**:
- `quality_scores_detailed.csv`：所有原始指标（多维度）
- `task_model_matching.csv`：任务-模型适配性分析（每个指标的Top 3模型）
- `quality_summary.csv`：按模型和任务的质量统计

**实现阶段**:

**阶段一（必需，2-3小时）** ⏳ 当前重点:
- ⏳ Exact Match
- ⏳ F1 Score
- ⏳ Distinct-N
- ⏳ 编译检查（Python）
- ⏳ ROUGE

**阶段二（推荐，3-4小时）**:
- ⏸️ BERTScore
- ⏸️ BARTScore（使用已有工具）
- ⏸️ 客观聚合方法（熵权法、PCA、TOPSIS）

**阶段三（可选，4-6小时）**:
- ⏸️ Pass@k（需要测试用例执行）
- ⏸️ 困惑度计算

**依赖安装**:
```bash
pip install rouge nltk bert-score transformers torch scikit-learn
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab')"
```

**详细设计**: 参见 `quality_evaluation_system.md` 和 `README_QUALITY_EVAL.md`

### 6.2 数据加载与预处理 ⏸️ 待开始

**脚本**: `load_and_preprocess.py`

**输入数据**:
- `pre_data/responses_raw.csv` (已完成)
- `pre_data/quality_scores_detailed.csv` (质量评估输出)

**功能**:
1. 加载已提取的回答数据
2. 合并质量评分数据
3. 数据清洗：
   - 处理缺失值（NaN）
   - 异常值检测（3σ原则）
   - 数据类型转换
4. 保存为 `pre_data/all_models_raw.csv`

**输出字段**:
```
# 基础信息
model_name, task_type, experiment_id, timestamp,

# 性能指标
throughput_tps, latency_s, token_count,

# 能耗指标
gpu_power_w, gpu_energy_j, cpu_energy_j, total_energy_j,

# 资源指标
gpu_util_pct, gpu_mem_mb,

# 质量指标（多维度，不聚合）
exact_match, f1_score, bertscore_f1, rouge_l, distinct_2, 
compilation_rate, numerical_match, self_bleu,
bartscore_info, bartscore_faith, compression_ratio,

# 可选：客观聚合分数（如果指定）
quality_score_entropy, quality_score_pca, quality_score_topsis,

# 其他
response_length, temperature, max_tokens
```

**注意**:
- 默认不生成 `quality_score_*`，除非质量评估时指定聚合方法
- 所有原始指标都保留，用于后续分析

### 6.3 指标计算 ⏸️ 待开始

**脚本**: `calculate_metrics.py`

**功能**:
1. 计算派生指标：`e_token`, `ppw`, `e_total`
2. 按任务分组归一化：`q_norm`, `e_norm`, `t_norm`, `l_norm`
3. 计算复合指标：`eff_score`, `qe_ratio`, `score_final`
4. 保存为 `pre_data/all_models_metrics.csv`

### 6.4 统计分析 ⏸️ 待开始

**脚本**: `statistical_analysis.py`

**功能**:
1. 描述性统计：均值、标准差、中位数、四分位数
2. 方差分析（ANOVA）：模型间差异显著性
3. 事后检验（Tukey HSD）
4. 相关性分析（Pearson）
5. 保存为 `pre_data/statistical_summary.csv`

### 6.5 可视化生成 ⏸️ 待开始

**脚本**: `generate_visualizations.py`

**功能**:
1. 生成 10 张核心图表（见 5.1 和 5.2）
2. 保存为 PNG（300 DPI）
3. 输出目录：`figures/`

### 6.6 报告生成 ⏸️ 待开始

**脚本**: `generate_report.py`

**功能**:
1. 基于模板生成 Markdown 报告
2. 嵌入图表和数据表
3. 自动化结论和建议
4. 保存为 `analysis_report.md`

### 6.7 主控脚本 ⏸️ 待开始

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

### 7.1 当前已完成文件 ✅

```
data/analize/
├── pre_data/                          # 预处理数据 ✅
│   ├── responses_raw.csv              # 原始数据（674 KB）✅
│   ├── responses_summary.csv          # 统计摘要（20 KB）✅
│   ├── README.md                      # 数据说明 ✅
│   └── comparison_matrices/           # 对比矩阵（~2 MB）✅
│       ├── overview.csv               # 总览统计 ✅
│       ├── README.md                  # 对比矩阵说明 ✅
│       ├── code/                      # 代码生成（8文件）✅
│       ├── creative/                  # 创意写作（8文件）✅
│       ├── math/                      # 数学推理（8文件）✅
│       ├── multi_turn/                # 多轮对话（8文件）✅
│       ├── qa/                        # 问答（8文件）✅
│       ├── reasoning/                 # 推理（8文件）✅
│       ├── summary/                   # 摘要（8文件）✅
│       └── translation/               # 翻译（8文件）✅
├── scripts/                           # 分析脚本
│   ├── extract_responses.py           # 数据提取 ✅
│   ├── create_comparison_matrix.py    # 对比矩阵生成 ✅
│   ├── verify_data.py                 # 数据验证 ✅
│   ├── view_samples.py                # 样本查看 ✅
│   ├── analysis_design.md             # 本文档 ✅
│   ├── quality_evaluation_system.md   # 质量评估设计 ✅
│   └── README_QUALITY_EVAL.md         # 质量评估说明 ✅
├── DATA_PREPARATION_COMPLETE.md       # 数据准备完成报告 ✅
└── EXTRACTION_SUMMARY.md              # 提取工作总结 ✅
```

### 7.2 待生成文件 ⏸️

```
data/analize/
├── pre_data/                          # 预处理数据
│   ├── quality_scores_detailed.csv    # 质量评分（多维度）⏳
│   ├── task_model_matching.csv        # 任务-模型适配性分析 ⏳
│   ├── quality_summary.csv            # 质量统计 ⏳
│   ├── all_models_raw.csv             # 原始数据汇总 ⏸️
│   ├── all_models_metrics.csv         # 计算指标 ⏸️
│   └── statistical_summary.csv        # 统计摘要 ⏸️
├── figures/                           # 可视化图表 ⏸️
│   ├── 00_quality_metrics_correlation.png  # 质量指标相关性 ⏸️
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
│   ├── quality_evaluation/            # 质量评估模块 ⏳
│   │   ├── __init__.py
│   │   ├── base_evaluator.py
│   │   ├── code_evaluator.py
│   │   ├── creative_evaluator.py
│   │   ├── math_evaluator.py
│   │   ├── qa_evaluator.py
│   │   ├── summary_evaluator.py
│   │   └── metrics/
│   ├── evaluate_all_models.py         # 质量评估主脚本 ⏳
│   ├── analyze_all_models.py          # 主控脚本 ⏸️
│   ├── load_and_preprocess.py         # 数据预处理 ⏸️
│   ├── calculate_metrics.py           # 指标计算 ⏸️
│   ├── statistical_analysis.py        # 统计分析 ⏸️
│   ├── generate_visualizations.py     # 可视化生成 ⏸️
│   └── generate_report.py             # 报告生成 ⏸️
└── analysis_report.md                 # 最终报告 ⏸️
```

**图例**:
- ✅ 已完成
- ⏳ 进行中（当前阶段）
- ⏸️ 待开始

## 8. 质量控制

### 8.1 数据验证 ✅

- [x] 所有模型数据完整性检查
- [x] 缺失值比例 < 5%（实际 2.47%）
- [x] 异常值标记和处理
- [x] 数据类型一致性
- [x] 特殊字符处理验证
- [x] 数据质量评分：85/100

**验证报告**: 参见 `DATA_PREPARATION_COMPLETE.md`

### 8.2 计算验证 ⏸️

- [ ] 手动验证 3 个样本的指标计算
- [ ] 归一化范围检查（[0, 1]）
- [ ] 复合指标合理性检查
- [ ] 质量指标准确性验证

### 8.3 可视化验证 ⏸️

- [ ] 图表标签完整（标题、轴标签、图例）
- [ ] 中文显示正常（无乱码）
- [ ] 颜色区分清晰
- [ ] 数据点可读（无重叠）

### 8.4 报告验证 ⏸️

- [ ] 结论与数据一致
- [ ] 推荐建议可操作
- [ ] 格式规范（Markdown）
- [ ] 引用图表正确

## 9. 时间安排

| 阶段 | 任务 | 预计时间 | 实际状态 |
|------|------|---------|---------|
| 0 | 数据提取与准备 | 2 小时 | ✅ 已完成（2026-03-04） |
| 1 | 质量评估（基础指标） | 2-3 小时 | ⏳ 进行中 |
| 2 | 质量评估（高级指标） | 3-4 小时 | ⏸️ 待开始 |
| 3 | 数据加载与预处理 | 1 小时 | ⏸️ 待开始 |
| 4 | 指标计算 | 1 小时 | ⏸️ 待开始 |
| 5 | 统计分析 | 1 小时 | ⏸️ 待开始 |
| 6 | 可视化生成 | 2 小时 | ⏸️ 待开始 |
| 7 | 报告生成 | 1 小时 | ⏸️ 待开始 |
| 8 | 质量检查与修订 | 1 小时 | ⏸️ 待开始 |
| **已完成** | | **2 小时** | |
| **剩余** | | **12-13 小时** | |
| **总计** | | **14-15 小时** | |

## 10. 风险与应对

| 风险 | 影响 | 概率 | 应对措施 | 当前状态 |
|------|------|------|---------|---------|
| 数据缺失严重 | 高 | 低 | 标记缺失模型，仅分析完整数据 | ✅ 已验证，缺失率 2.47% |
| BARTScore缺失 | 中 | 高 | 使用多维度质量指标替代 | ⏳ 计划中 |
| 中文乱码 | 低 | 低 | 强制UTF-8编码，回退英文标签 | ✅ 已解决 |
| 内存不足 | 中 | 低 | 分批处理，减少缓存 | ⏸️ 待观察 |
| 计算时间过长 | 低 | 低 | 优化代码，使用向量化操作 | ⏸️ 待观察 |
| 样本不均衡 | 中 | 中 | qwen25_7b_hf_8bit 样本少，分析时注意权重 | ✅ 已识别 |

## 11. 后续扩展

1. **交互式仪表板**：使用 Plotly Dash 或 Streamlit
2. **实时监控**：集成到实验流程，实时更新分析
3. **自动化报告**：定期生成周报/月报
4. **模型推荐系统**：基于用户需求推荐最优模型
5. **成本计算器**：输入使用量，输出预估成本

---

**文档版本**: v1.1  
**创建日期**: 2026-03-04  
**最后更新**: 2026-03-04  
**作者**: Kiro AI Assistant  
**审核状态**: 待审核

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2026-03-04 | 初始版本，完整分析设计 |
| v1.1 | 2026-03-04 | 更新数据准备完成状态，反映实际进度 |

## 主要更新（v1.1）

1. **第2节 数据结构分析**：更新为实际完成的数据格式和统计信息
2. **第6节 实现计划**：添加进度跟踪表，标记已完成和待开始的阶段
3. **第7节 输出文件结构**：分为"已完成文件"和"待生成文件"两部分
4. **第8节 质量控制**：更新数据验证状态为已完成
5. **第9节 时间安排**：添加实际状态列，更新已完成和剩余时间
6. **第10节 风险与应对**：添加当前状态列，更新风险评估

**下一步**: 开始质量评估阶段（evaluate_all_models.py）
