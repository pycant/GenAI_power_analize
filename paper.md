# 基于多元统计方法的生成式大语言模型质效比评估研究

**摘要**

随着生成式人工智能（Generative AI）技术的快速普及，大语言模型（LLM）在教育、医疗及代码生成等领域的应用日益深入。然而，现有的评估体系往往侧重于单一维度的性能（如准确率或流畅度），缺乏对资源消耗与生成质量之间权衡关系的系统性量化研究。本文提出了一种综合性的“质效比（Quality-Efficiency Ratio, Q/E Ratio）”评估框架，并采用多元统计方法（MANOVA, PCA, CCA）对 DeepSeek-R1:8b, Gemma3:4b, Qwen3:4b/8b 四种模型在多任务场景下的表现进行了实证研究。实验结果表明，Gemma3:4b 在综合质效比上表现最优（Q/E Ratio > 69），在保持竞争性生成质量的同时显著降低了能耗与延迟。典型相关分析（CCA）进一步揭示了资源投入（显存、能耗）与性能产出（吞吐、延迟）之间存在极强的内在耦合（r > 0.99）。本研究为资源受限场景下的模型选型与部署提供了统计学依据。

---

## 1. 引言 (Introduction)

生成式人工智能正在成为推动技术变革的关键力量。从 ChatGPT 到开源社区的 Llama、Gemma 系列，LLM 展现出了强大的多模态理解与生成能力。然而，正如 *Statistical Methods in Generative AI* [1] 所指出的，生成式模型基于概率采样，其输出具有内在的不确定性，且缺乏保证正确性与安全性的默认机制。

当前的评估工作面临双重挑战：
1.  **评估维度的割裂**：传统的自动评估指标（如 BLEU, ROUGE）难以捕捉语义层面的细微差别，而基于 LLM 的评估（如 GPT-4 as Judge）虽然提升了语义理解，但引入了新的偏差 [2]。
2.  **资源视角的缺失**：在 *Investigating generative AI models* [3] 等研究中，重点往往在于模型输出的检测与区分，而忽视了模型推理过程中的能耗、延迟等物理成本。这在端侧部署与大规模并发场景下显得尤为关键。

本文旨在填补这一空白，通过引入统计学严谨的多元分析框架，探索模型架构、任务类型对“质量-效率”平衡的影响机制。

## 2. 相关工作 (Related Work)

### 2.1 生成式 AI 的评估指标
自然语言生成（NLG）的评估长期依赖于 n-gram 重叠度量（如 BLEU, ROUGE），但这些指标在评估语义一致性与事实正确性方面表现不佳。*BARTScore* [4] 将评估概念化为文本生成任务，利用预训练模型的似然概率来衡量生成文本的质量，已被证明在多个维度上优于传统指标。本文采用 BARTScore 作为核心质量度量之一。

### 2.2 资源感知与公平性
在 *Towards Reward Fairness in RLHF* [5] 中，研究者从资源分配的角度探讨了奖励模型的公平性。类似的，*Establish Reliability Metrics for Reward Models* [6] 强调了建立可靠度量的重要性。本文将这一视角扩展至模型推理阶段，将计算资源（显存、能耗）视为投入，将生成质量与速度视为产出，构建投入产出比分析。

---

## 3. 方法论 (Methodology)

### 3.1 实验设置
本研究选取了当前开源社区具有代表性的四款模型进行对比实验：
- **DeepSeek-R1:8b**
- **Gemma3:4b**
- **Qwen3:8b**
- **Qwen3:4b**

测试涵盖四类典型任务（Task）：
1.  **知识问答 (QA)**：测试事实性与准确性。
2.  **文本摘要 (Summary)**：测试信息提取与概括能力。
3.  **代码生成 (Code)**：测试逻辑推理与语法正确性。
4.  **创意写作 (Creative)**：测试文本流畅度与多样性。

实验在统一的硬件环境下进行，使用 `Ollama` 作为推理后端，通过自定义的 Python 脚本 `run_experiments.py` 自动化采集数据。

### 3.2 评估指标体系

我们构建了包含效率与质量的多维指标体系：

1.  **效率维度 (Efficiency)**:
    - **端到端延迟 (Latency, s)**: 完成一次推理的总耗时。
    - **吞吐量 (Throughput, TPS)**: 每秒生成的 Token 数。
    - **能耗 (Energy, J)**: 推理过程中的 GPU 能耗积分。
    - **显存峰值 (Peak Memory, MB)**: 显存占用的最大值。

2.  **质量维度 (Quality)**:
    - **BARTScore**: 用于 QA 和 Summary 任务，衡量语义距离。
    - **Code Pass Rate**: 代码是否可编译及包含特定算法结构。
    - **Distinct-n**: 创意写作的多样性指标。

3.  **综合质效比 (Q/E Ratio)**:
    为了统一衡量，我们定义质效比：
    $$
    QE\_Ratio = \frac{Norm(Quality) + \epsilon}{1.01 - (0.4 \cdot Norm(TPS) + 0.3 \cdot Norm(Latency^{-1}) + 0.3 \cdot Norm(Energy^{-1}))}
    $$
    其中各项指标均经过 Min-Max 归一化处理。

### 3.3 统计分析方法
本研究采用以下多元统计方法处理高维实验数据：
- **多元方差分析 (MANOVA)**: 检验“模型”和“任务”对性能向量（延迟、吞吐、能耗、质量）的整体显著性影响。
- **主成分分析 (PCA)**: 对多维指标进行降维，探索模型在性能空间中的分布模式。
- **典型相关分析 (CCA)**: 研究“资源投入组”与“性能产出组”之间的内在相关结构。
- **层次聚类 (Hierarchical Clustering)**: 基于性能特征对实验运行进行无监督分类。

---

## 4. 实验结果与分析 (Results and Analysis)

### 4.1 基础性能评估

实验共收集 16 组完整样本数据。基础统计结果显示，**Gemma3:4b** 在多项指标上表现优异：

- **吞吐量 (TPS)**: Gemma3:4b 达到峰值 **83.02 tokens/s**，均值 **50.07 tokens/s**，显著高于其他模型（如 Qwen3:8b 仅约 14 TPS）。
- **能耗 (Energy)**: Gemma3:4b 的平均单次请求能耗最低，这与其较小的参数量（4B）及高效的架构设计有关。
- **质量 (Quality)**: 在 BARTScore 评估中，各模型差距较小（均值约 -4.06），但 Gemma3:4b 在保持高吞吐的同时，并未出现显著的质量下降。

**图 1** 展示了吞吐量与延迟的分布关系，可以明显看到 Gemma3:4b 位于“低延迟-高吞吐”的理想区域（左上角）。

![Throughput vs Latency](results/experiments_1/figures/throughput_vs_latency.png)

**图 2** 展示了能耗与质量的关系，进一步印证了小参数模型在特定任务上的能效优势。

![Energy vs Quality](results/experiments_1/figures/energy_vs_quality.png)

### 4.2 质效比 (Q/E Ratio) 排名

根据定义的 Q/E Ratio，模型排名如下：

| Rank | Model | Q/E Ratio |
| :--- | :--- | :--- |
| 1 | **Gemma3:4b** | **69.29** |
| 2 | DeepSeek-R1:8b | 2.23 |
| 3 | Qwen3:4b | 2.01 |
| 4 | Qwen3:8b | 0.52 |

Gemma3:4b 的遥遥领先主要得益于其极高的效率得分，在分母（效率成本）极小的情况下放大了比率。

![Q/E Ratio](results/experiments_1/figures/quality_efficiency_ratio.png)

### 4.3 多元统计分析

#### 4.3.1 相关性结构
多元相关性分析（图 4）显示，**延迟 (Latency)** 与 **能耗 (Energy)** 之间存在极强的正相关 (**r = 0.98**)。这意味着在当前硬件架构下，推理时间直接决定了能源成本，优化推理速度即是优化能耗。此外，显存占用与吞吐量呈负相关 (**r = -0.54**)，提示大模型在受限显存下的带宽瓶颈。

![Correlation Heatmap](results/experiments_1/multivariate_analysis/figures/correlation_heatmap.png)

#### 4.3.2 显著性检验 (MANOVA)
MANOVA 结果表明，**模型架构 (Model)** (Wilks' lambda=0.0029, p<0.001) 和 **任务类型 (Task)** (Wilks' lambda=0.0004, p<0.001) 均对综合性能指标有极显著影响。这说明不同模型在不同任务上的表现差异并非随机波动，而是具有统计学意义的结构性差异。

#### 4.3.3 主成分分析 (PCA)
PCA 将 6 维指标降维后，前两个主成分解释了 **68.16%** 的方差。
- **PC1 (46.6%)** 主要由延迟、能耗（正载荷）和吞吐量（负载荷）构成，可解释为 **“效率因子”**。
- **PC2 (21.6%)** 主要由显存峰值（负载荷）构成，可解释为 **“资源因子”**。

Biplot（图 5）清晰地将 Qwen3:8b（高延迟、高能耗）与 Gemma3:4b（高吞吐、低能耗）在 PC1 轴上区分开来。

![PCA Biplot](results/experiments_1/multivariate_analysis/figures/pca_biplot.png)

#### 4.3.4 典型相关分析 (CCA)
CCA 提取的第一对典型变量显示出 **r = 0.9902** 的极强相关性。
- **典型变量 1**：主要由能耗 (Load=0.99) 和 延迟 (Load=0.99) 主导。
这从统计上证实了：**在当前的生成式 AI 推理中，资源投入与性能产出几乎是线性锁定的**，尚未出现显著的“低投入-高产出”异常点（除 Gemma3:4b 的架构优化带来的整体平移外）。

![CCA Pair 1](results/experiments_1/multivariate_analysis/figures/cca_pair1.png)

#### 4.3.5 聚类分析
层次聚类（图 7）将 16 次运行分为了 3 类：
1.  **Cluster 1**: DeepSeek-R1:8b (中等性能)
2.  **Cluster 2**: Gemma3:4b 与 Qwen3:4b (高性能轻量级)
3.  **Cluster 3**: Qwen3:8b (高资源消耗)
这一结果验证了参数量级（4B vs 8B）是决定性能表现的主导因素。

![Clustering Dendrogram](results/experiments_1/multivariate_analysis/figures/clustering_dendrogram.png)

---

## 5. 讨论 (Discussion)

本研究通过引入多元统计方法，为 LLM 的评估提供了新的视角。
1.  **小模型的崛起**：Gemma3:4b 的优异表现表明，在特定任务（如 QA、Summary）下，经过良好训练的小参数模型完全可以替代大模型，且能效优势巨大（Q/E Ratio 提升 30 倍以上）。
2.  **评估的复杂性**：MANOVA 的显著性结果提示我们，单一的“模型评分”是不够的，必须结合“任务场景”进行评估。DeepSeek-R1 在代码任务上的表现（见原始数据）与在 QA 上的表现截然不同。
3.  **统计方法的价值**：PCA 和 CCA 等工具能有效剥离高维数据中的冗余信息（如延迟与能耗的共线性），帮助研究者聚焦于核心的性能驱动因子。

---

## 6. 结论 (Conclusion)

本文构建了一个包含效率与质量的多维评估框架，并对四种主流 LLM 进行了实证分析。研究发现：
1.  **Gemma3:4b** 是当前测试集中的最佳质效比选择。
2.  **资源与性能强耦合**，优化推理延迟是降低 AI 碳足迹的最直接路径。
3.  **多元统计方法** 为生成式 AI 的精细化评估提供了强有力的工具支持，能够揭示传统排行榜无法体现的结构性特征。

未来的工作将进一步扩展样本量，引入更多样化的模型架构（如 MoE），并结合人工评估进一步校准自动质量指标。

---

## 参考文献 (References)

[1] Statistical Methods in Generative AI.
[2] GenAI 竞技场：生成式模型的开放评估平台.
[3] Investigating generative AI models and detection techniques.
[4] BARTScore: Evaluating Generated Text as Text Generation.
[5] Towards Reward Fairness in RLHF: From a Resource Allocation Perspective.
[6] Establishing Reliability Metrics for Reward Models in Large Language Models.
[7] A Survey of Evaluation Metrics Used for NLG Systems.
