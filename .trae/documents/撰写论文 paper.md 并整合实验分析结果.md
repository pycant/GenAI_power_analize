我将撰写一份学术论文格式的文档 `results/experiments_1/paper.md`，基于现有的分析报告和实验数据。

### **文章结构与内容规划**

**1. 标题与摘要 (Abstract)**
*   **标题**: 《基于多元统计分析的大语言模型效能评估研究：质量、效率与资源消耗的权衡》
*   **摘要**: 概述研究背景（LLM 部署的资源约束）、方法（对 4 种模型在 4 类任务上的多维评估，引入 MANOVA 与 CCA 等统计方法）、核心发现（Gemma3-4B 的质效比优势，以及时延与能耗的强相关性）。

**2. 引言 (Introduction)**
*   简述 LLM 发展现状与端侧部署的挑战。
*   提出研究问题：如何在有限资源下评估模型的综合效能？
*   介绍本文提出的“质效比 (Q/E Ratio)”指标体系与多元统计分析框架。

**3. 实验设置 (Experimental Setup)**
*   **模型选择**: DeepSeek-R1-8B, Gemma3-4B, Qwen3-8B, Qwen3-4B。
*   **任务集**: QA, Summary, Code, Creative。
*   **评估指标**:
    *   效率：Latency, Throughput (TPS).
    *   资源：GPU Memory, GPU Energy, Utilization.
    *   质量：BARTScore (QA/Sum), Code Pass Rate, Distinct-N (Creative).
*   **环境**: 描述硬件与软件环境（基于已有元数据）。

**4. 结果与分析 (Results and Analysis)**
*   **4.1 描述性统计与基础性能**:
    *   引用 `report.md` 中的数据摘要表。
    *   插入图表: `throughput_vs_latency.png`, `energy_vs_quality.png`。
    *   分析 Gemma3-4B 在 TPS 和能耗上的显著优势。
*   **4.2 多元相关性与结构分析**:
    *   引用 `multivariate_report.md` 中的相关性矩阵与 PCA 结果。
    *   插入图表: `correlation_heatmap.png`, `pca_biplot.png`。
    *   解读 PC1 (资源-时延因子) 与 PC2 (吞吐-显存因子) 的含义。
*   **4.3 统计显著性检验 (MANOVA)**:
    *   报告 Wilks' Lambda 和 P 值，证明模型架构对性能有极显著影响 (P < 0.001)。
*   **4.4 投入产出关联 (CCA)**:
    *   插入图表: `cca_pair1.png`。
    *   分析第一对典型变量 (r=0.99) 揭示的“高能耗-高时延”强耦合关系。

**5. 讨论 (Discussion)**
*   **质效权衡**: 探讨 Qwen3-8B 的高质量与高资源消耗 vs Gemma3-4B 的高效率。
*   **任务敏感性**: 分析代码任务 (Code) 对资源的特殊需求（从聚类结果看）。
*   **局限性**: 样本量较小 (N=16)，质量评估指标的单一性。

**6. 结论 (Conclusion)**
*   总结 Gemma3-4B 为当前最佳端侧模型。
*   强调多元统计方法在 LLM 评估中的有效性。

**7. 附录 (Appendix)**
*   包含部分原始数据表格。

### **图片引用路径修正**
由于 Markdown 文件将位于 `results/experiments_1/paper.md`，图片引用的相对路径需调整：
*   原 `figures/xxx.png` -> `figures/xxx.png` (同级目录)
*   原 `multivariate_analysis/figures/xxx.png` -> `multivariate_analysis/figures/xxx.png` (子目录)

### **执行步骤**
1.  **创建文件**: 编写 `results/experiments_1/paper.md`。
2.  **整合内容**: 将 `report.md` 和 `multivariate_report.md` 的核心数据与图表嵌入上述结构，并转化为学术语言（使用被动语态、客观描述、统计术语）。
3.  **验证**: 确认所有图片链接有效，格式符合 Markdown 标准。
