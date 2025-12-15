# 大语言模型多维质效比评估：一项基于多元统计的实证研究

## 摘要 (Abstract)

随着生成式人工智能（Generative AI）技术的飞速发展，大语言模型（LLMs）在知识问答、代码生成、创意写作等领域的应用日益广泛。然而，当前对于 LLMs 的评估往往局限于单一维度的性能指标（如准确率、流畅性）或资源消耗指标（如延迟、能耗），缺乏对模型“质量-效率”平衡的系统性量化研究。本研究旨在填补这一空白，提出了一种基于多元统计分析的多维质效比评估框架。我们选取了包括 DeepSeek-R1、Gemma3、Qwen3 在内的多个代表性开源模型，在四种不同任务类型（QA、摘要、代码、创意写作）下进行了全面的性能测试。通过收集时延、吞吐量、显存占用、GPU 能耗及 BARTScore 等多维指标，我们运用多元方差分析（MANOVA）、主成分分析（PCA）、层次聚类分析及典型相关分析（CCA）等统计方法，揭示了模型性能与资源消耗之间的内在联系。实验结果表明，Gemma3:4b 模型在综合质效比（Q/E Ratio）上表现最优，特别是在低能耗与高吞吐量方面具有显著优势，适合边缘计算场景；而 Qwen3:8b 虽在特定任务上表现不俗，但其高能耗特征限制了其大规模部署的潜力。本研究不仅为 LLMs 的选型与部署提供了实证依据，也为构建更公平、全面的 AI 评估体系提供了新的方法论视角。

## 1. 引言 (Introduction)

### 1.1 背景

近年来，以 ChatGPT、Claude、Gemini 为代表的大语言模型（LLMs）重塑了人工智能的版图，展现出强大的多模态生成与推理能力。这些模型不仅在自然语言处理（NLP）任务中表现卓越，更逐渐渗透至教育、医疗、软件开发等关键领域。然而，随着模型参数量的激增，其部署成本与环境影响（如碳足迹）也日益受到关注。如何在保证生成质量的前提下，最大化资源利用效率，成为学术界与工业界共同面临的挑战。

### 1.2 问题陈述

现有的 LLM 评估体系主要面临两大问题：

1.  **评价维度单一**：多数排行榜（Leaderboards）侧重于生成质量的评估（如 HumanEval, MMLU），忽视了推理延迟、吞吐量及能耗等实际部署中的关键指标。
2.  **缺乏综合度量**：缺乏一个能够统一量化“质量”与“效率”权衡关系的综合指标，导致在资源受限场景下（如移动端、实时交互）的模型选型困难。

### 1.3 研究目标

本研究旨在构建一个多维度的 LLM 评估框架，具体目标包括：

1.  设计并实施涵盖多任务、多负载的标准化实验，采集细粒度的性能与资源数据。
2.  引入多元统计分析方法，深入探究模型结构、任务类型对性能指标的显著性影响。
3.  提出“质效比”（Quality-Efficiency Ratio, Q/E Ratio）概念，量化模型的综合效能。
4.  通过实证分析，识别不同应用场景下的最优模型选择。

## 2. 相关工作 (Related Work)

### 2.1 生成式 AI 的评估挑战

生成式 AI 的评估一直是个难题。传统的 N-gram 指标（如 BLEU, ROUGE）在捕捉语义连贯性与事实一致性方面存在局限。近年来，基于模型的评估方法（Model-based Evaluation）如 BARTScore、BERTScore 逐渐兴起，它们利用预训练模型计算生成文本与参考文本的语义相似度，被证明与人类判断具有更高的一致性。此外，利用 LLM 作为评估者（LLM-as-a-Judge）也成为一种新趋势，尽管其在评估视觉内容等方面仍存在局限。

### 2.2 绿色 AI 与能效评估

随着 AI 模型规模的扩大，“绿色 AI”（Green AI）倡导将能效作为顶级评估指标。研究表明，训练与推理大型模型的碳排放不容小觑。然而，目前关于 LLMs 推理阶段能耗的细粒度测量与分析仍相对匮乏。本研究通过集成实时的 GPU 能耗监控，试图弥补这一数据缺口。

### 2.3 多元统计在 AI 评估中的应用

统计方法为 AI 评估提供了严谨的数学基础。MANOVA 可用于检验不同因素（如模型架构、量化精度）对多维性能指标的综合影响；PCA 与聚类分析则有助于发现模型间的潜在相似性与性能群组。本研究将这些经典统计方法应用于 LLM 评估，以期获得比单一指标比较更稳健的结论。

## 3. 方法论 (Methodology)

### 3.1 实验设计

本研究采用全因子实验设计（Full Factorial Design），主要变量包括：

- **模型（Model）**：DeepSeek-R1:8b, Gemma3:4b, Qwen3:8b, Qwen3:4b。覆盖了不同参数量级与架构。
- **任务（Task）**：知识问答（QA）、文本摘要（Summary）、代码生成（Code）、创意写作（Creative）。覆盖了 LLM 的主要应用场景。
- **负载（Load）**：Custom（自定义），根据任务特性设定不同的输入长度与生成要求。

### 3.2 数据采集与指标定义

我们构建了一个自动化的实验流水线，采集以下两类核心指标：

**效率指标 (Efficiency Metrics)**：

- **时延 (Latency)**：端到端推理时间（秒）。
- **吞吐量 (Throughput)**：每秒生成的 Token 数量（Tokens/s）。
- **能耗 (Energy)**：推理过程中的 GPU 能耗（Joules），通过积分实时功率获得。
- **显存占用 (Memory)**：推理过程中的 GPU 显存峰值（MB）。

**质量指标 (Quality Metrics)**：

- **BARTScore**：用于 QA 与摘要任务，衡量生成内容的语义质量。
- **代码编译率**：用于代码任务，衡量生成代码的语法正确性。
- **Distinct-N**：用于创意写作，衡量生成文本的多样性。
- **Final Quality**：归一化后的统一质量得分。

**综合指标**：

- **质效比 (Q/E Ratio)**：$Q/E = \frac{\text{Normalized Quality}}{1 - \text{Efficiency Score}}$，其中 Efficiency Score 是吞吐、时延与能耗的加权组合。

### 3.3 统计分析方法

本研究运用以下多元统计方法对采集的数据进行深度分析：

1.  **多元相关性分析**：探索各性能指标间的线性关系。
2.  **多元方差分析 (MANOVA)**：检验模型与任务对性能指标向量的显著性影响。
3.  **主成分分析 (PCA)**：对多维指标进行降维，可视化模型性能分布。
4.  **层次聚类分析**：基于性能特征对实验运行进行聚类。
5.  **典型相关分析 (CCA)**：研究资源消耗变量组与性能产出变量组之间的相关结构。

## 4. 实验结果 (Results)

### 4.1 描述性统计

实验共收集有效样本 16 组。表 1 展示了各模型在不同任务下的关键性能指标均值。

**表 1：各模型关键性能指标摘要**

| Model          | Latency (s) | TPS (toks/s) | Energy (J) | BARTScore |
| :------------- | :---------- | :----------- | :--------- | :-------- |
| **gemma3:4b**  | **10.76**   | **80.40**    | **775.5**  | -3.66     |
| qwen3:4b       | 48.05       | 74.89        | 3994.6     | -3.98     |
| deepseek-r1:8b | 35.85       | 27.03        | 1989.8     | -3.88     |
| qwen3:8b       | 177.69      | 17.68        | 9194.0     | -3.99     |

_注：数据来源于实验报告 `report.md`。_

### 4.2 多元相关性分析

相关性热力图（图 1）揭示了指标间的强相关性。

- **时延与能耗**呈现极强正相关（r=0.98），表明推理时间越长，能耗越高，这是符合预期的。
- **吞吐量与时延**呈现负相关（r=-0.45），说明高吞吐量模型通常能更快完成推理。
- **显存占用与吞吐量**呈现负相关（r=-0.54），暗示较大的显存占用可能伴随着计算效率的下降（可能是由于参数量大导致的）。

![Correlation Heatmap](d:/project/GenAI_power_analize/results/experiments_1/multivariate_analysis/figures/correlation_heatmap.png)
_图 1：多元指标相关性热力图_

### 4.3 多元方差分析 (MANOVA)

MANOVA 结果显示，**模型（Model）**和**任务（Task）**对整体性能指标均有极显著影响（Wilks' lambda < 0.05, Pr > F < 0.001）。这表明不同模型之间的性能差异不仅仅是随机波动，而是由模型架构和参数量决定的本质差异；同时，不同任务类型对资源的消耗和模型表现也有显著不同的要求。

### 4.4 主成分分析 (PCA)

PCA 结果显示，前两个主成分解释了总方差的 68.16%（图 2）。

- **PC1 (46.60%)**：主要由时延、能耗（正载荷）和吞吐量（负载荷）构成，可解释为“效率因子”。
- **PC2 (21.56%)**：主要由显存占用（负载荷）构成，可解释为“资源规模因子”。

从 Biplot 中可以看出，Gemma3:4b 分布在 PC1 的负轴（高效率区），而 Qwen3:8b 分布在 PC1 的正轴（低效率区）。

![PCA Biplot](d:/project/GenAI_power_analize/results/experiments_1/multivariate_analysis/figures/pca_biplot.png)
_图 2：PCA 主成分双标图_

### 4.5 层次聚类分析

层次聚类树状图（图 3）将实验运行分为了三类：

1.  **高效组**：包含 Gemma3:4b 的所有任务运行，以及 Qwen3:4b 的部分任务。
2.  **中效组**：主要包含 DeepSeek-R1:8b 的运行。
3.  **低效组**：包含 Qwen3:8b 的运行，特别是高负载任务。

这一结果验证了参数量是影响模型性能聚类的主要因素。

![Clustering Dendrogram](d:/project/GenAI_power_analize/results/experiments_1/multivariate_analysis/figures/clustering_dendrogram.png)
_图 3：层次聚类树状图_

### 4.6 典型相关分析 (CCA)

CCA 分析提取了第一对典型变量，其相关系数高达 0.99。载荷分析显示：

- **资源侧**：能耗（0.99）是主导变量。
- **性能侧**：时延（0.99）是主导变量。
  这再次确认了“能耗-时延”是 LLM 推理中最核心的资源-性能耦合关系。

![CCA Pair 1](d:/project/GenAI_power_analize/results/experiments_1/multivariate_analysis/figures/cca_pair1.png)
_图 4：第一对典型变量散点图_

### 4.7 综合质效比分析

根据定义的 Q/E Ratio，各模型排名如下：

1.  **Gemma3:4b (69.29)**：遥遥领先，得益于其极高的吞吐量和极低的能耗，且质量保持在可接受水平。
2.  **DeepSeek-R1:8b (2.23)**：位居第二，表现均衡。
3.  **Qwen3:4b (2.01)**：与 DeepSeek 接近。
4.  **Qwen3:8b (0.52)**：由于极高的延迟和能耗，质效比最低。

![Q/E Ratio](d:/project/GenAI_power_analize/results/experiments_1/figures/quality_efficiency_ratio.png)
_图 5：各模型质效比对比_

## 5. 讨论 (Discussion)

### 5.1 效率与质量的权衡

实验数据清晰地展示了“参数量-效率”的权衡（Trade-off）。4b 参数量的模型（Gemma3, Qwen3-4b）在吞吐量上显著优于 8b 模型，且能耗低一个数量级。在许多实际应用中，如果生成的质量差异在用户可接受范围内（如 BARTScore 差异小于 0.5），选择小参数模型能带来巨大的成本优势。

### 5.2 任务类型的影响

MANOVA 证实了任务类型的影响。例如，代码生成任务往往需要更长的推理时间和更多的显存（可能由于更长的上下文依赖），而创意写作则相对轻量。这意味着在部署 LLM 服务时，应根据具体任务类型配置不同的资源配额。

### 5.3 评估方法的有效性

本研究引入的多元统计方法为 LLM 评估提供了新的视角。PCA 和聚类分析能够直观地识别出性能相似的模型群组，这对于模型选型（如在同一群组内寻找更廉价的替代品）具有指导意义。CCA 则揭示了输入资源与输出性能之间的强耦合，提示我们在优化推理引擎时应重点关注能耗与时延的解耦。

### 5.4 局限性与改进方向 (Limitations and Future Work)

本研究虽构建了多维评估的雏形，但在实验设计、指标定义及物理测量层面仍存在以下显著局限，这些不足也为后续研究指明了方向。

#### 1. 实验设计的统计效力不足

- **样本量限制**：目前仅包含 16 个观测样本（4 模型 × 4 任务 × 1 次运行）。在多元统计分析（如 MANOVA）中，这远低于推荐的样本量标准，导致统计检验的功效（Power）较弱，且无法有效评估模型性能的随机波动（Variance）。
- **覆盖范围有限**：仅测试了 4B/8B 参数量级，缺乏对更大参数（如 70B+）或微型模型（<1B）的覆盖，无法完整拟合“参数量-能效”的非线性标度律（Scaling Law）。此外，缺乏对不同量化精度（如 Q4_K_M vs FP16）的对比研究。

#### 2. 质量评估的“代理偏差”

- **自动化指标的局限**：BARTScore 虽能捕捉语义重叠，但在评估“创意性”或“逻辑严密性”时仍显乏力。特别是在代码生成任务中，仅依赖“是否可编译”作为质量标准过于粗糙，无法检测代码的功能正确性（Functional Correctness）。
- **缺乏“金标准”校准**：未引入人类评估（Human Eval）或更强模型（如 GPT-4-as-a-Judge）作为参照系，无法验证自动化指标与人类偏好的一致性。

#### 3. 能耗测量的粒度问题

- **系统能耗的缺失**：当前仅统计 GPU 功耗。然而，对于轻量级模型（如 Gemma3:4b），GPU 负载较低时，CPU、内存及主板的基础能耗占比将显著提升。忽略系统能耗可能导致对小模型整体能效的高估。

#### 4. 综合指标的鲁棒性

- **权重的经验性**：质效比（Q/E Ratio）公式中各项权重（0.4/0.3/0.3）基于经验设定，缺乏敏感性分析。不同的应用场景（如实时交互 vs 离线批处理）对时延和质量的敏感度截然不同，固定权重无法适应多变的实际需求。

### 5.5 改进计划

针对上述不足，未来的研究将集中在以下维度：

1.  **扩展实验规模**：将重复运行次数增至 5 次以上以计算置信区间；引入 Llama-3、Mistral 等更多模型系列及不同量化版本。
2.  **升级评估体系**：
    - 代码任务：集成 HumanEval 数据集，采用单元测试通过率（Pass@k）作为核心指标。
    - 通用任务：引入 LLM-as-a-Judge 机制，利用 GPT-4o 对生成质量进行多维度打分。
3.  **精细化能耗建模**：引入系统级功率计或基于硬件计数器的全系统能耗估算模型（如 RAPL 接口），实现“端到端”的能效评估。
4.  **动态权重分析**：对 Q/E Ratio 进行蒙特卡洛模拟或敏感性分析，探索模型排名在不同偏好权重下的稳定性，为用户提供可配置的选型建议。

## 6. 结论 (Conclusion)

本研究通过构建多维质效比评估框架，并运用多元统计方法，对当前流行的开源大语言模型进行了系统性评估。主要结论如下：

1.  **Gemma3:4b** 是本次实验中综合质效比最优的模型，特别适合对时延敏感且追求高能效的应用场景。
2.  **能耗与时延** 是高度正相关的，优化推理速度是降低碳排放的关键路径。
3.  **多元统计方法**（如 MANOVA, PCA, CCA）能有效揭示 LLM 性能数据的内在结构，是单一指标评估的有力补充。

未来的工作将进一步扩大模型库与任务集，引入人类评估（Human-in-the-loop），并探索模型量化对质效比的非线性影响。

## 参考文献 (References)

[1] GAI-A: GenAI Arena - An Open Evaluation Platform for Generative Models.
[2] AI Competitions as a Standard for Empirical Rigor in Generative AI Evaluation.
[3] A Survey of Evaluation Metrics Used for NLG Systems.
[4] BARTScore: Evaluating Generated Text as Text Generation.
[5] Trlx: A Framework for Large Scale Open Source RLHF.
[6] Towards Reward Fairness in RLHF: From a Resource Allocation Perspective.
[7] Statistical Methods in Generative AI.
[8] Investigating generative AI models and detection techniques.
[9] A continual learning survey: Defying forgetting in classification tasks.
[10] From large language models to multimodal AI: a scoping review.

---

**附录：可视化图表集**

- 吞吐量 vs 延迟: `results/experiments_1/figures/throughput_vs_latency.png`
- 能耗 vs 质量: `results/experiments_1/figures/energy_vs_quality.png`
- 综合雷达图: `results/experiments_1/figures/radar_chart.png`
