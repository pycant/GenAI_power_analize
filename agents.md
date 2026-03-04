# Agents 使用指南：项目目的、结构与环境

## 项目目的

- 研究目标：在给定的硬件资源和计算预算下，最小化推理延迟（latency）、降低能耗（energy/power）与最大化模型输出质量（accuracy/quality） 这三个目标无法同时达到全局最优。围绕生成式大语言模型的质效比，构建一套模型评价体系，在算力不变（相同硬件设备条件下），同时保证满足推理质量与效率的要求条件下找到能耗最低的大语言模型，换而言之就是构建一个全面、客观的GenAI（生成式人工智能）模型能效评级体系，通过多维效质比评估方法，为学术界和工业界提供标准化的模型评估工具，促进AI技术的可持续发展。
- 核心输出：
  - 数据分析脚本与管线
  - 标准化图表与自动化 Markdown 报告
  - 可协作的数据集与配置

## 仓库结构

- 数据
  - data/experiments_1/
    - raw/ 各模型原始 JSON 结果
    - texts/ 各模型原始文本输出
    - summary/ 汇总 CSV（results.csv、stats.csv）
    - config.py、config.json、test_cases.json
- 脚本
  - scripts/analyze_experiments_1.py：主分析脚本，完成加载、归一化、复合指标计算、图表生成与报告输出
- 结果
  - results/experiments_1/
    - figures/ 分析图表 PNG
    - report.md 自动化报告
- 评测资产
  - tools/thesis_reproduction/BARTScore/ 保留说明文件与脚本，避免大型基准文件入库
- 版本控制
  - .gitignore：允许 experiments_1 数据被跟踪，同时忽略缓存与编译产物

## 关键文件链接

- 脚本：[analyze_experiments_1.py](file:///f:/all_proj/GenAI_power_analize/scripts/analyze_experiments_1.py)
- 数据汇总：[results.csv](file:///f:/all_proj/GenAI_power_analize/data/experiments_1/summary/results.csv)
- 统计汇总：[stats.csv](file:///f:/all_proj/GenAI_power_analize/data/experiments_1/summary/stats.csv)
- 报告输出：[report.md](file:///f:/all_proj/GenAI_power_analize/results/experiments_1/report.md)
- 图表目录：[figures](file:///f:/all_proj/GenAI_power_analize/results/experiments_1/figures)

## 基本环境
- 操作系统：Windows
- cuda 信息：CUDA 12.6（nvcc 12.6.85），NVIDIA 驱动 561.17
- 显卡信息：NVIDIA GeForce RTX 4060 Laptop GPU 8GB；Intel Iris Xe 2GB
- CPU信息：Intel Core i7-13700H，14核20线程，基础频率 2.4GHz
- 内存/显存：内存约 16GB；显存 8GB（RTX 4060）
- conda 环境：bartscore，Python 3.10
- Python：3.8+
- ollama信息：Ollama 0.13.2，服务运行中，API http://localhost:11434/，可用模型：deepseek-r1:8b（约5.2GB，Q4_K_M）、gemma3:4b（约3.3GB，Q4_K_M）、qwen3:8b（约5.2GB，Q4_K_M）、qwen3:4b（约2.5GB，Q4_K_M）
- HuggingFace 模型信息：
  - 存储位置：models/huggingface/
  - 模型注册表：models/model_registry.json
  - 推荐模型（按优先级）：
    - 小型模型（4-8GB显存）：Qwen/Qwen2.5-3B-Instruct、microsoft/phi-3-mini-4k-instruct、google/gemma-2b-it
    - 中型模型（6-8GB显存，4bit量化）：Qwen/Qwen2.5-7B-Instruct、meta-llama/Llama-3.2-7B-Instruct、mistralai/Mistral-7B-Instruct-v0.3
    - 大型模型（12-16GB显存，4bit量化）：Qwen/Qwen2.5-14B-Instruct、meta-llama/Llama-3.1-13B-Instruct
    - 专用模型：Qwen/Qwen2.5-Coder-7B-Instruct（代码生成）、deepseek-ai/deepseek-coder-6.7b-instruct（代码生成）
  - 配置文件：configs/models_to_download.yaml
  - 管理脚本：scripts/manage_models.py、scripts/download_hf_model.py、scripts/batch_download_models.py
  - 加载器：src/model_deployment/hf_loader.py
  - 环境变量：HF_TOKEN（访问受限模型）、HF_HOME（缓存目录）
- 包依赖：
  - pandas、numpy、matplotlib、seaborn、tabulate
  - transformers、torch、accelerate、bitsandbytes（HuggingFace模型）

 - 字体与中文显示：
  - 脚本自动检测系统中文字体并优先使用 Microsoft YaHei，若缺失则回退英文标签
  - 终端中文输出采用 UTF-8，避免乱码

## 快速开始
- 安装依赖（示例）
  - conda create -n bartscore python=3.10
  - conda activate bartscore
  - pip install pandas numpy matplotlib seaborn tabulate
- 运行分析
  - Windows 终端中运行：
    - conda activate bartscore
    - set PYTHONUTF8=1
    - python scripts/analyze_experiments_1.py
- 输出结果
  - figures/ 生成 4 张图表
  - report.md 自动化分析报告
  - analysis_data.csv 中间分析数据

## 数据说明
- 任务类型：code、creative、qa、summary
- 原始 JSON 命名：{task}_custom_r{run}.json（按模型分文件夹）
- 关键字段（summary/results.csv）：
  - bartscore：质量得分（面向 QA/Summary）
  - toks_per_s：吞吐量（tokens/s）
  - latency_s：延迟（秒）
  - gpu_energy_j：能耗（焦耳）
- 细粒度质量指标：
  - code：编译通过率（从 raw JSON 推断 code_compiles）
  - creative：distinct-2（从 raw JSON 中 creative 节点读取）

## 指标与方法（暂定）
- 归一化（按任务分组）：Min-Max Scaling
- 效率得分（efficiency_score）：
  - 0.4 × 吞吐归一 + 0.3 × 延迟优归一 + 0.3 × 能耗优归一
- 质效比（qe_ratio）：
  - (norm_quality + 0.01) / (1.01 - efficiency_score)
  - 加入微小偏置避免分母为零

## 文献启示：RLHF 奖励公平性与资源分配视角
- 参考文献：[Towards Reward Fairness in RLHF](file:///f:/all_proj/GenAI_power_analize/docs/reference/方法论基础构建/pdfs/Towards%20Reward%20Fairness%20in%20RLHF%20From%20a%20Resource%20Allocation%20Perspective.pdf)
- 核心观点：
  - 将 RLHF 的奖励学习视作“资源分配”问题：在不同用户/任务/群体间分配有限的“奖励预算”，目标是兼顾整体效用与公平。
  - 公平性不应仅体现在单点性能，而应体现在跨群体的效用一致性（避免奖励系统性偏向某类输入或风格）。
- 指标建议（可与质效评估结合）：
  - 群体公平差距（Fairness Gap，按任务或语言分组）：FG = max_g |mean_quality_g − mean_quality_global|，越小越公平。
  - 质量不均衡指数：可选 Theil/Gini 对每模型的样本质量分布做衡量，反映是否“少数群体被系统性低估”。
  - 嫉妒率（Envy Proxy）：随机两群体比较，A 的平均质量明显低于 B 的比例，越低越好。
- 公平化聚合建议：
  - 采用 Nash Social Welfare 风格聚合：Q_nsw = Σ_g log(ε + mean_quality_g)，兼顾整体与弱势群体，提高“尾部群体”的话语权。
  - 在质效比中加入公平正则：qe_ratio_fair = qe_ratio × (1 − λ · FG)（或基于 Gini/Theil），在公平差距扩大时降低综合评分。
- 资源分配与采样启示：
  - 评估采样权重按群体覆盖度逆比例分配（弱代表群体更高权重），降低训练/评估的偏倚。
  - 将评估预算在任务/风格/语言上做配额控制，防止某一类型样本主导综合结论。
- 管线改造建议（落地到本项目）：
  - 在 [analyze_experiments_1.py](file:///f:/all_proj/GenAI_power_analize/scripts/analyze_experiments_1.py) 中新增 compute_fairness_metrics(df)：
    - 基于列 task（或后续加入的 language/style）计算各模型的 mean_quality_g、FG、Gini/Theil。
  - 在报告中加入“公平性”章节与图表：
    - 模型-任务公平差距柱状图、Gini/Theil 对比、NSW 聚合评分对比。
  - 将 qe_ratio 扩展为 qe_ratio_fair，并在 figures 中新增“公平性 vs 质量/效率”的散点或热力图。
  - 数据需求：为样本补充群体标签（如语言、写作风格、领域），以便开展更细粒度公平评估。

## 可视化输出
- Throughput vs Latency 散点图
- Energy vs Quality 散点图
- Q/E Ratio 柱状图（按任务与模型对比）
- 综合能力雷达图（吞吐/延迟优/能耗优/质量）

## 协作指南
- 数据提交
  - experiments_1 数据已纳入版本控制，保持既有命名与结构
  - 避免提交缓存与编译产物（__pycache__/、*.pyc）
- 新实验批次
  - 建议复制 experiments_1 结构形成 experiments_2
  - 如需分析新批次，可调整脚本中的 DATA_DIR/RESULTS_DIR 或按需参数化
- 结果复核
  - 优先查看 report.md 与 figures 中的图表
  - 如需深入复盘，结合 analysis_data.csv 与 summary/stats.csv

## 常见问题
- 中文乱码
  - 终端设置 PYTHONUTF8=1，脚本已强制 stdout/stderr 使用 UTF-8
- 中文缺字警告
  - 脚本会自动选择系统中文字体；如系统缺失中文字体则会使用英文标签避免警告
- 依赖缺失
  - 安装 tabulate 等缺少的包；确保 conda 环境已激活

## 安全与合规
- 不提交大型基准与机密数据
- 不提交敏感配置或密钥
- 严格遵守 .gitignore 规则

## 参考
- 论文草稿：[paper.md](file:///f:/all_proj/GenAI_power_analize/paper.md)
*** End Patch*** }``` />
`
  print("This tool only accepts a valid patch string") }``` />
`json
{"patch":"*** Begin Patch\\n*** Add File: agents.md\\n+# Agents 使用指南：项目目的、结构与环境\\n\\n## 项目目的\\n- 研究目标：基于多元统计方法评估生成式大语言模型的质效比，综合质量与效率维度，形成可复用的分析流程与结论。\\n- 核心输出：\\n  - 数据分析脚本与管线\\n  - 标准化图表与自动化 Markdown 报告\\n  - 可协作的数据集与配置\\n\\n## 仓库结构\\n- 数据\\n  - data/experiments_1/\\n    - raw/ 各模型原始 JSON 结果\\n    - texts/ 各模型原始文本输出\\n    - summary/ 汇总 CSV（results.csv、stats.csv）\\n    - config.py、config.json、test_cases.json\\n- 脚本\\n  - scripts/analyze_experiments_1.py：主分析脚本，完成加载、归一化、复合指标计算、图表生成与报告输出\\n- 结果\\n  - results/experiments_1/\\n    - figures/ 分析图表 PNG\\n    - report.md 自动化报告\\n- 评测资产\\n  - tools/thesis_reproduction/BARTScore/ 保留说明文件与脚本，避免大型基准文件入库\\n- 版本控制\\n  - .gitignore：允许 experiments_1 数据被跟踪，同时忽略缓存与编译产物\\n\\n## 关键文件链接\\n- 脚本：[analyze_experiments_1.py](file:///f:/all_proj/GenAI_power_analize/scripts/analyze_experiments_1.py)\\n- 数据汇总：[results.csv](file:///f:/all_proj/GenAI_power_analize/data/experiments_1/summary/results.csv)\\n- 统计汇总：[stats.csv](file:///f:/all_proj/GenAI_power_analize/data/experiments_1/summary/stats.csv)\\n- 报告输出：[report.md](file:///f:/all_proj/GenAI_power_analize/results/experiments_1/report.md)\\n- 图表目录：[figures](file:///f:/all_proj/GenAI_power_analize/results/experiments_1/figures)\\n\\n## 基本环境\\n- 操作系统：Windows\\n- Python：3.8+（推荐 3.10）\\n- 包依赖：\\n  - pandas、numpy、matplotlib、seaborn、tabulate\\n- 字体与中文显示：\\n  - 脚本自动检测系统中文字体并优先使用 Microsoft YaHei，若缺失则回退英文标签\\n  - 终端中文输出采用 UTF-8，避免乱码\\n\\n## 快速开始\\n- 安装依赖（示例）\\n  - conda create -n bartscore python=3.10\\n  - conda activate bartscore\\n  - pip install pandas numpy matplotlib seaborn tabulate\\n- 运行分析\\n  - Windows 终端中运行：\\n    - conda activate bartscore\\n    - set PYTHONUTF8=1\\n    - python scripts/analyze_experiments_1.py\\n- 输出结果\\n  - figures/ 生成 4 张图表\\n  - report.md 自动化分析报告\\n  - analysis_data.csv 中间分析数据\\n\\n## 数据说明\\n- 任务类型：code、creative、qa、summary\\n- 原始 JSON 命名：{task}_custom_r{run}.json（按模型分文件夹）\\n- 关键字段（summary/results.csv）：\\n  - bartscore：质量得分（面向 QA/Summary）\\n  - toks_per_s：吞吐量（tokens/s）\\n  - latency_s：延迟（秒）\\n  - gpu_energy_j：能耗（焦耳）\\n- 细粒度质量指标：\\n  - code：编译通过率（从 raw JSON 推断 code_compiles）\\n  - creative：distinct-2（从 raw JSON 中 creative 节点读取）\\n\\n## 指标与方法\\n- 归一化（按任务分组）：Min-Max Scaling\\n- 效率得分（efficiency_score）：\\n  - 0.4 × 吞吐归一 + 0.3 × 延迟优归一 + 0.3 × 能耗优归一\\n- 质效比（qe_ratio）：\\n  - (norm_quality + 0.01) / (1.01 - efficiency_score)\\n  - 加入微小偏置避免分母为零\\n\\n## 可视化输出\\n- Throughput vs Latency 散点图\\n- Energy vs Quality 散点图\\n- Q/E Ratio 柱状图（按任务与模型对比）\\n- 综合能力雷达图（吞吐/延迟优/能耗优/质量）\\n\\n## 协作指南\\n- 数据提交\\n  - experiments_1 数据已纳入版本控制，保持既有命名与结构\\n  - 避免提交缓存与编译产物（__pycache__/、*.pyc）\\n- 新实验批次\\n  - 建议复制 experiments_1 结构形成 experiments_2\\n  - 如需分析新批次，可调整脚本中的 DATA_DIR/RESULTS_DIR 或按需参数化\\n- 结果复核\\n  - 优先查看 report.md 与 figures 中的图表\\n  - 如需深入复盘，结合 analysis_data.csv 与 summary/stats.csv\\n\\n## 常见问题\\n- 中文乱码\\n  - 终端设置 PYTHONUTF8=1，脚本已强制 stdout/stderr 使用 UTF-8\\n- 中文缺字警告\\n  - 脚本会自动选择系统中文字体；如系统缺失中文字体则会使用英文标签避免警告\\n- 依赖缺失\\n  - 安装 tabulate 等缺少的包；确保 conda 环境已激活\\n\\n## 安全与合规\\n- 不提交大型基准与机密数据\\n- 不提交敏感配置或密钥\\n- 严格遵守 .gitignore 规则\\n\\n## 参考\\n- 论文草稿：[paper.md](file:///f:/all_proj/GenAI_power_analize/paper.md)\\n*** End Patch"}
