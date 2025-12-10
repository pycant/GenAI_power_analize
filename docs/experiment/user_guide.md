# 项目使用说明与实验原理（GenAI 效质比采集管道）

## 1. 背景与目标
- 目标：围绕“效”（效率、资源消耗）与“质”（生成质量）两维，构建可重复的自动化采集，量化不同模型在多任务下的表现，用于计算“效质比”。
- 原理来源：
  - 效维度：CPU/GPU 利用率、显存与能耗；吞吐与时延。
  - 质维度：BARTScore（有参考任务）、任务特定指标（代码正确性线索、创作文本多样性）。

## 2. 环境准备
- 硬件：`RTX 4060` 或同等支持 CUDA 的显卡。
- 软件：
  - Conda（通过 `E:\ananconda\Scripts\conda.exe` 调用），创建或使用 `bartscore` 环境。
  - Ollama（本地模型运行）：`ollama --version`、`ollama list`。
  - Python 依赖：`psutil`、`pynvml`、`requests`、`tqdm`。
- 验证：
  - `E:\ananconda\Scripts\conda.exe run -n bartscore python -V`
  - `nvidia-smi`、`ollama list`
  - 目录快照：`tree /F /A f:\all_proj\GenAI_power_analize > f:\all_proj\GenAI_power_analize\docs\project_tree.txt`

## 3. 指标与计算原理
- 效率与资源
  - GPU 指标：`gpu_mem_peak_mb`、`gpu_util_avg`、`gpu_temp_peak_c`。
  - GPU 能耗：采样功率积分 `energy_j = Σ(power_w * dt)`（来自 NVML）。
  - CPU 能耗（近似）：通过 `CPU_TDP_W` 与 CPU 利用率积分估算 `cpu_energy_j_approx`（默认 65W；可设 `CPU_TDP_W` 环境变量调整）。
- 生成性能
  - 吞吐：`toks/s = eval_count / (eval_duration_ns / 1e9)`。
  - 首 token 时间：使用流式 API 记录首个响应块到达时间 `first_token_seconds`。
  - 总时延：端到端请求耗时（包含装载与推理）。
- 生成质量
  - BARTScore：对有参考文本的任务（摘要、QA）进行打分。
  - 代码生成：AST 编译检查、是否包含二分查找相关符号、是否提及复杂度。
  - 创意写作：`distinct-1/2/3` 与长度统计。
- 模型元数据
  - 从 Ollama 标签接口解析 `digest/parameter_size/quantization_level/family`。

## 4. 自动化采集管道
- 模块组成：
  - `experiments/run_experiments.py`：主控脚本（流式首包计时、Ollama API 调用、数据写入与汇总）。
  - `experiments/monitor.py`：资源监控（CPU/内存/磁盘/GPU 利用率/显存/功耗/温度/进程）、能耗积分与时序输出。
  - `experiments/quality.py`：BARTScore 简易封装（单条/批量）。
- 关键实现参考：
  - 批次目录建立与使用：`experiments/run_experiments.py:193–207`
  - 流式首包计时与 API 指标：`experiments/run_experiments.py:59–96、320–340`
  - 资源摘要与时序保存：`experiments/monitor.py:85–98、101–113`
  - 默认文件解析与参数回退：`experiments/run_experiments.py:239–271、301–300`
  - 用例 `model` 支持列表与 `"all"`：`experiments/run_experiments.py:129–136、402–411`

## 5. 批次目录与配置文件
- 批次目录结构（自动或手动）：
  - `data/experiments_{index}_{start_time}/`
    - `raw/`：原始 JSON（首包时间、API 指标、监控摘要+时序、质量扩展、元数据）。
    - `texts/`：生成文本归档。
    - `summary/`：`results.csv`（逐条）与 `stats.csv`（均值/方差）。
    - `config.json`：运行参数快照（含来源）。
    - `test_cases.json`（可选）：用例集。
    - `config.py`（可选）：全局参数覆盖。
- 默认文件解析：当指定 `--exp-dir` 时，若未传入 `--cases-file/--exp-config`，脚本会默认读取 `exp-dir\test_cases.json` 与 `exp-dir\config.py`（存在时）。
- 回退策略：文件读取失败或参数校验失败时，若加 `--use-default-on-error` 则回退到内置任务配置继续运行，否则提示并退出。

## 6. 用例与配置格式
- `test_cases.json`（示例）
  ```json
  [
    {
      "model": ["deepseek-r1:8b", "gemma3:4b"],
      "prompt": "请解释牛顿第一定律。",
      "task_type": "knowledge_qa",
      "reference_text": "牛顿第一定律，也称为惯性定律...",
      "max_tokens": 200,
      "temperature": 0.7
    },
    {
      "model": "all",
      "prompt": "写一段关于人工智能的短文。",
      "task_type": "creative_writing",
      "max_tokens": 300,
      "temperature": 0.8
    }
  ]
  ```
- `config.py`（示例）
  ```python
  TEMPERATURE = 0.7
  TOP_P = 0.9
  NUM_CTX = 4096
  SEED = 1234
  KEEPALIVE = "0s"
  WARMUP = True
  RUNS = 1
  ```

## 7. 运行流程（新手指南）
- 安装与准备：
  - `E:\ananconda\Scripts\conda.exe run -n bartscore pip install psutil pynvml requests tqdm`
  - `ollama list` 确认模型已下载（例如 `deepseek-r1:8b gemma3:4b qwen3:8b`）。
- 快速验证（干跑，不执行推理）：
  - `E:\ananconda\Scripts\conda.exe run -n bartscore python -m experiments.run_experiments --exp-dir data\experiments_2 --dry-run --use-default-on-error`
- 执行指定批次：
  - `E:\ananconda\Scripts\conda.exe run -n bartscore python -m experiments.run_experiments --exp-dir data\experiments_2 --use-default-on-error`
- 自动批次命名执行（无需手动创建目录）：
  - `E:\ananconda\Scripts\conda.exe run -n bartscore python -m experiments.run_experiments --models deepseek-r1:8b gemma3:4b qwen3:8b --tasks qa summary code creative --loads short medium long --runs 3 --out data --max_tokens 256 --temperature 0.7 --seed 1234 --warmup --keepalive 0s`

## 8. 输出文件查看
- 原始数据示例（字段）：
  - `model/prompt/generated_text`
  - `latency_seconds/first_token_seconds/throughput_tokens_per_sec`
  - `api_metrics: eval_count/eval_duration_ns/total_duration_ns/load_duration_ns/prompt_eval_duration_ns`
  - `system_metrics_summary`: 峰值/均值
  - `system_metrics_full`: 时序数组（CPU/GPU/内存/磁盘/温度/进程/能耗）
  - `quality`: `bartscore`（如有参考）、代码与创作指标
  - `metadata`: 配置项、模型元数据、是否预热
- 汇总：
  - `summary/results.csv`：逐条记录按 `timestamp, model, task, load, run, latency_s, toks_per_s, gpu_mem_peak_mb, gpu_util_avg, gpu_energy_j, bartscore`。
  - `summary/stats.csv`：按（模型×任务×负载）统计均值与方差，便于对照。

## 9. 显存管理与稳定性建议
- 显存释放：默认 `--keepalive 0s`，推理结束后释放模型显存。
- 防爆显存：捕获 OOM/500 后自动降级 `num_ctx/max_tokens` 并重试；优先用 `short/medium` 负载迭代，确认稳定后再拓展到 `long`。
- 预热：使用 `--warmup` 执行一次短例不计入统计，降低冷启动影响。
- 随机性控制：启用 `--seed` 保持采样一致性。

## 10. 常见问题与排错
- 子进程解码错误（`UnicodeDecodeError: 'gbk'`）
  - 原因：系统默认编码解码 `ollama show` 输出失败。
  - 处理：脚本已切换为二进制读取并用 `utf-8` 解码（`experiments/run_experiments.py:98–107`）。
- 终端中文乱码（Mojibake）
  - 处理：PowerShell 设置 UTF-8。
    - `chcp 65001`
    - `$OutputEncoding = [System.Text.UTF8Encoding]::new()`
- OOM/显存不足
  - 降低 `num_ctx/max_tokens` 或改用更高量化（如 `q4_K_M`），确认 `--keepalive 0s`。
- BARTScore 设备与下载
  - 首次运行会下载权重；网络不稳定时可重试或预下载；设备默认 `cuda`。

## 11. 原理补充（效质比）
- 效：综合考虑时延、吞吐、能耗、峰值资源占用；能耗计算采用采样积分，近似反映推理过程能量消耗。
- 质：BARTScore 度量相关性/可读性，有参考任务适用；代码与创作任务提供轻量指标保证“数据采集为主”。
- 对照设计：统一硬件/参数，任务短中长负载，重复运行取均值与方差；冷/热区分提高结论稳定性。

## 12. 快速上手示例
- 手动批次：在 `data\experiments_2` 放置 `test_cases.json` 与 `config.py`，执行：
  - `E:\ananconda\Scripts\conda.exe run -n bartscore python -m experiments.run_experiments --exp-dir data\experiments_2 --use-default-on-error`
- 指定小规模任务：
  - `E:\ananconda\Scripts\conda.exe run -n bartscore python -m experiments.run_experiments --models gemma3:4b qwen3:8b --tasks qa --loads short --runs 1 --out data --max_tokens 128 --temperature 0.7 --seed 1234 --keepalive 0s`

---
- 如需进一步扩展到更多模型与任务，请在 `test_cases.json` 使用 `"model": "all"` 或列表形式；若要统一参数，使用 `config.py` 覆盖。
