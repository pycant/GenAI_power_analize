## 目标概述
- 围绕“效”（效率、资源消耗）与“质”（生成质量）两维，构建可重复的自动化采集管道。
- 在相同硬件与统一参数下，对多模型、多任务进行对照测试，采集时序资源指标与生成性能，并保存结构化数据。

## 目录采集（tree）
- 运行命令采集现有项目目录：`tree /F /A f:\all_proj\GenAI_power_analize > f:\all_proj\GenAI_power_analize\docs\project_tree.txt`
- 目的：记录项目基线结构，便于审计与复现实验环境变化。

## 环境准备
- Conda 调用：`E:\ananconda\Scripts\conda.exe`
- 激活环境（推荐非交互方式）：`E:\ananconda\Scripts\conda.exe run -n bartscore python -V`
- 依赖安装（在 `bartscore` 环境）：`E:\ananconda\Scripts\conda.exe run -n bartscore pip install psutil pynvml requests tqdm`
- 验证 GPU/驱动：`nvidia-smi`
- 验证 Ollama：`ollama --version`、`ollama list`

## 数据采集范围与指标
- 硬件资源
  - GPU：显存占用、GPU 利用率、功耗（W）、温度（可选）
  - CPU：利用率（%）
  - 内存：系统内存占用（MB）
  - 磁盘：总读写字节（采样增量）
- 生成性能
  - 吞吐量：`tokens/sec`（来自 Ollama API 的 `eval_count` 与 `eval_duration`）
  - 响应延迟：首 token 时间（使用 API 的 `load_duration + prompt_eval_duration` 近似或流式首包时间）
  - 总推理时间：`total_duration`
- 生成质量
  - BARTScore：`bart_score` 对有参考文本的任务进行评估（摘要、问答等）
- 模型配置信息
  - `ollama show <model>` 解析模型名称、量化、上下文长度；记录 `ollama --version`

## 测试套件设计
- 模型集合（变量组）：`llama3.2:3b`、`llama3.2:11b`、`gemma2:9b`
- 任务类型（控制输入参数一致）
  - 知识问答：`请解释牛顿第一定律。`
  - 文本摘要：输入给定段落，输出 100–200 字摘要，提供参考摘要用于 BARTScore
  - 代码生成：实现“二分查找”，提供参考实现用于 BARTScore（可选）
  - 创意写作：给定主题生成 300 字短文（无参考，跳过 BARTScore）
- 负载层级：短（50–100 字）、中（200–400 字）、长（800–1200 字）输入
- 重复次数：每模型×任务×负载运行 5 次，取平均并保留原始记录

## 自动化脚本结构
- `experiments/run_experiments.py`
  - 读取测试配置（模型、任务、负载、重复次数）
  - 启动资源监控线程，采样周期 200ms
  - 通过 Ollama HTTP API（`POST http://localhost:11434/api/generate`，`stream:false`）发起推理
  - 记录响应字段：`response`、`eval_count`、`eval_duration`、`total_duration`、`load_duration`、`prompt_eval_count`、`prompt_eval_duration`
  - 汇总监控数据（均值、峰值、时间积分）
  - 若提供参考文本，调用 BARTScore 计算质量分
  - 写入结构化 JSON 与汇总 CSV
- `experiments/monitor.py`
  - 使用 `psutil` 采样 CPU、内存、磁盘
  - 使用 `pynvml` 采样 GPU 显存、利用率、功耗（mW），并积分得能耗（J）
  - 支持 `start()`/`stop()` 控制与 `to_dict()` 聚合输出
- `experiments/quality.py`
  - 封装 BARTScore 计算函数：`score_batch(references, hypotheses)`，设备为 `cuda`

## 关键实现要点
- Ollama API
  - 请求体示例：`{"model":"llama3.2:3b","prompt":"请解释牛顿第一定律。","stream":false}`
  - 吞吐量计算：`tokens_per_sec = eval_count / (eval_duration / 1e9)`
  - 首 token近似：`first_token_seconds = (load_duration + prompt_eval_duration) / 1e9`
- 资源能耗
  - `energy_joules ≈ Σ(power_watts_t * dt_seconds)`（采样积分）
  - 峰值与均值同时记录，便于后续分析
- 统一元数据
  - 记录执行时间戳、环境标识（主机名、GPU 型号、驱动版本）、模型量化参数、上下文长度、温度、最大 token 等

## 输出与存储
- 原始数据（每次运行）：`data/raw/<date>/<model>/<task_id>_<run>.json`
- 汇总数据：`data/summary/<date>/results.csv`
- 项目目录快照：`docs/project_tree.txt`
- 生成文本归档：`data/texts/<date>/<model>/<task_id>_<run>.txt`

## 标准化运行流程
- 重启 Ollama 服务（保证缓存一致）
  - 方式一：服务管理器重启 `Ollama` 服务
  - 方式二：命令行停止后再次启动（根据本机安装方式选择）
- 清理上下文与缓存
  - 保持统一 `num_ctx`、`temperature`、`top_p`、`max_tokens` 参数
- 执行脚本
  - 示例：`E:\ananconda\Scripts\conda.exe run -n bartscore python experiments\run_experiments.py --models llama3.2:3b llama3.2:11b gemma2:9b --tasks qa summary code creative --runs 5 --out data`
- 完成后检查
  - 查看 `data/summary/<date>/results.csv` 与若干 `raw` JSON

## 数据字典示例（JSON）
- `model`: 模型名称
- `prompt`: 输入提示
- `generated_text`: 输出文本
- `latency_seconds`: 总延迟（秒）
- `throughput_tokens_per_sec`: 吞吐量
- `api_metrics`: `eval_count`、`eval_duration_ns`、`total_duration_ns`、`load_duration_ns`、`prompt_eval_duration_ns`
- `system_metrics`: `cpu_percent_avg`、`mem_used_peak_mb`、`gpu_util_avg`、`gpu_mem_peak_mb`、`gpu_power_avg_w`、`gpu_energy_j`
- `quality`: `bartscore`（如有参考）
- `metadata`: `ollama_version`、`quantization`、`num_ctx`、`temperature`、`max_tokens`、`timestamp`

## 实验操作与说明文档（交付内容大纲）
- 实验目标与范围说明
- 环境准备步骤与命令
- 目录采集与基线记录方法
- 测试套件配置说明（模型、任务、负载）
- 采集脚本使用方法与参数说明
- 指标定义与计算方法
- 输出文件结构与字段解释
- 常见问题与排错指南（Ollama 服务、GPU 权限、依赖安装）

## 后续扩展
- 增加任务专属质量指标（代码单测通过率、事实性问答准确率）
- 支持流式首 token 精确测量（监听首包到达时间）
- 多 GPU 支持与并行批量运行
- 可视化仪表盘（Dash/Streamlit）与报告自动生成