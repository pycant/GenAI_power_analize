## 目标概述

* 分析 `data/experiments_1` 中的实验数据，在 `results/experiments_1` 下构建分析文件。

* 完成“基于大语言模型的多维质效比评估”课题的分析部分，得出结论。

## 数据分析流程与脚本设计

* 分析脚本：`scripts/analyze_experiments_1.py`

  * 读取 `data/experiments_1/summary/results.csv` 与 `stats.csv`

  * 读取 `data/experiments_1/raw` 下的 JSON 文件（提取更细粒度指标，如时序波动）

  * 计算复合指标（“质效比”）：

    * `Efficiency_Score` = `f(Throughput, Latency, Energy)`（归一化加权）

    * `Quality_Score` = `f(BARTScore, Code_Compile, Creative_Distinct)`（归一化加权）

    * `Q_E_Ratio` = `Quality_Score / Efficiency_Cost`

  * 生成可视化图表（保存至 `results/experiments_1/figures/`）：

    * `throughput_vs_latency.png`：吞吐量与延迟散点图

    * `energy_vs_quality.png`：能耗与质量散点图

    * `radar_chart.png`：各模型在（吞吐、延迟、能耗、质量）上的雷达图

    * `quality_efficiency_tradeoff.png`：质效比折线/柱状图

  * 生成分析报告（保存至 `results/experiments_1/report.md`）：

    * 实验概况（模型、任务、配置）

    * 关键发现（如：Model A 吞吐高但能耗大，Model B 质效比最优）

    * 数据汇总表（Markdown 格式）

## 目录结构规划

* `results/experiments_1/`

  * `figures/`：存放生成的 PNG/SVG 图表

  * `report.md`：自动生成的分析报告

  * `analysis_data.csv`：处理后的中间数据表（含复合指标）

  * `notebooks/`（可选）：交互式分析 Notebook（如需要）

## 分析脚本关键逻辑

* 数据加载与预处理

  * 加载 `results.csv`，按 `model` 和 `task` 分组。

  * 清洗异常值（如 BARTScore 为空的情况）。

* 复合指标计算公式（示例）

  * `Norm_Throughput` = `(TPS - Min_TPS) / (Max_TPS - Min_TPS)`

  * `Norm_Latency` = `1 - (Lat - Min_Lat) / (Max_Lat - Min_Lat)`（越低越好 -> 越高越好）

  * `Norm_Energy` = `1 - (Energy - Min_Energy) / (Max_Energy - Min_Energy)`

  * `Efficiency_Score` = `0.4 * Norm_Throughput + 0.3 * Norm_Latency + 0.3 * Norm_Energy`

  * `Quality_Score` = 归一化后的任务特定分数

  * `QE_Ratio` = `Quality_Score / (1 - Efficiency_Score + epsilon)` 或直接对比

* 可视化实现

  * 使用 `matplotlib` 或 `seaborn` 绘制图表。

  * 确保图表包含图例、坐标轴标签与标题。

* 报告生成

  * 使用 Python 字符串模板或 `pandas` 的 `to_markdown()` 生成报告内容。

  * 包含“结论与建议”章节，基于数据自动生成初步结论（如“推荐在资源受限场景使用 Model X”）。

## 实施步骤

* 创建目录结构 `results/experiments_1/figures`

* 编写 `scripts/analyze_experiments_1.py`

  * 导入必要库（pandas, matplotlib, seaborn, json, os）

  * 实现数据读取与预处理函数

  * 实现指标计算函数

  * 实现绘图函数

  * 实现报告生成函数

  * 主函数串联流程

* 执行脚本并验证输出

  * 运行 `E:\ananconda\Scripts\conda.exe run -n bartscore python scripts/analyze_experiments_1.py`

  * 检查 `results/experiments_1/report.md` 与图表

* （可选）人工润色报告

  * 在自动生成的基础上，结合领域知识补充深入见解。

## 依赖库检查

* 确认环境包含 `pandas`, `matplotlib`, `seaborn`。若缺失，需安装：`pip install pandas matplotlib seaborn`。

## 预期产出

* 一个完整的分析报告 `report.md`，包含数据支撑的结论。

* 一组直观的可视化图表。

* 可复用的分析脚本，用于后续实验批次。

