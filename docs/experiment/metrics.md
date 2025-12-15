# experiments_1 数据与指标说明

本文档详细说明 `data/experiments_1` 目录内各文件的结构与每个指标的含义，便于复现与分析。

## 目录结构

- `raw/`：每次运行的完整原始记录（按模型分子目录，JSON）。
- `texts/`：每次运行的模型输出纯文本（按模型分子目录，TXT）。
- `summary/`：汇总与统计表（CSV）。
- `config.json`：本批次实验的参数快照。
- `config.py`：可覆盖的实验参数定义。
- `test_cases.json`：自定义测试用例集合。

命名约定：单条样本的 ID 为 `task_load_r{run}`（例如 `code_custom_r10`）。

## summary/results.csv

逐条记录的汇总表，列定义如下：

- `timestamp`：时间戳标识（`YYYYMMDD_HHMMSS`）。
- `model`：模型名（如 `gemma3:4b`、`qwen3:8b`）。
- `task`：任务类型，取值 `qa`、`summary`、`code`、`creative`。
- `load`：负载层级，默认 `custom`；使用内置负载时为 `short`/`medium`/`long`。
- `run`：运行序号（从 1 递增）。
- `latency_s`：端到端时延（秒），从发送请求到接收最后一个 token 的墙钟时间。
- `toks_per_s`：吞吐量（tokens/s），近似为 `eval_count / (eval_duration_ns / 1e9)`。
- `gpu_mem_peak_mb`：GPU 显存峰值（MB）。
- `gpu_util_avg`：GPU 平均利用率（%）。
- `gpu_energy_j`：GPU 能耗（J），采样积分得到。
- `bartscore`：BARTScore 质量分数（QA/Summary 场景；未计算时为空）。

生成逻辑参考：`experiments/run_experiments.py:510–514`、`experiments/run_experiments.py:438–449`。

## summary/stats.csv

按 `(model, task, load)` 聚合后的统计表，列定义如下：

- `model`/`task`/`load`：分组键。
- `count`：样本数量。
- `latency_mean`/`latency_std`：时延均值与标准差（秒）。
- `tps_mean`/`tps_std`：吞吐量均值与标准差（tokens/s）。
- `gmem_peak_mean`：GPU 显存峰值的均值（MB）。
- `gutil_mean`：GPU 平均利用率的均值（%）。
- `energy_j_mean`：GPU 能耗均值（J）。
- `bartscore_mean`：BARTScore 均值（可为空）。

生成逻辑参考：`experiments/run_experiments.py:480–509`。

## raw/<model>/<case>.json

单次运行的完整记录，主要字段如下：

- `model`：模型名。
- `prompt`：输入提示词。
- `generated_text`：模型输出文本。
- `latency_seconds`：端到端时延（秒）。
- `throughput_tokens_per_sec`：吞吐量（tokens/s）。
- `first_token_seconds`：首 token 延迟（秒），从请求发出到收到首个 token 的时间。
- `api_metrics`：来自推理 API 的内部计时与计数（单位为纳秒或计数）：
  - `eval_count`：生成 token 数量（由 API 报告）。
  - `eval_duration_ns`：生成阶段耗时（ns）。
  - `total_duration_ns`：完整推理耗时（ns）。
  - `load_duration_ns`：模型加载耗时（ns）。
  - `prompt_eval_duration_ns`：提示词评估耗时（ns）。
    定义参考：`experiments/run_experiments.py:72–109`。
- `system_metrics_summary`：资源监控的摘要指标：
  - `cpu_percent_avg`/`cpu_percent_peak`：CPU 平均/峰值利用率（%）。
  - `mem_used_peak_mb`：系统内存使用峰值（MB）。
  - `gpu_util_avg`/`gpu_util_peak`：GPU 平均/峰值利用率（%）。
  - `gpu_mem_peak_mb`：GPU 显存使用峰值（MB）。
  - `gpu_power_avg_w`：GPU 平均功率（W）。
  - `gpu_energy_j`：GPU 能耗（J），按 `功率(W) × 时间(s)` 积分得到。
  - `gpu_temp_peak_c`：GPU 峰值温度（℃）。
  - `cpu_energy_j_approx`：CPU 能耗近似（J），以 CPU TDP 与利用率估算。
    采样与汇总实现参考：`experiments/monitor.py:134–150`。
- `system_metrics_full`：资源监控的完整时序数据：
  - `timestamps`：采样时间戳（秒）。
  - `cpu_percent`/`cpu_proc_percent`：系统 CPU 与相关进程 CPU 利用率（%）。
  - `mem_used_mb`：系统内存使用（MB）。
  - `disk_read_bytes`/`disk_write_bytes`：磁盘读写增量（字节）。
  - `gpu_util`/`gpu_mem_mb`/`gpu_power_w`/`gpu_temp_c`：GPU 利用率、显存、功率、温度时序。
  - `gpu_processes`：占用 GPU 的进程与其显存（MB）。
  - `gpu_energy_j`：GPU 能耗累计（J）。
  - `cpu_power_w_approx`/`cpu_energy_j_approx`：CPU 功率与能耗近似时序。
  - `summary`：同 `system_metrics_summary`。
    采样逻辑参考：`experiments/monitor.py:72–133`、`experiments/monitor.py:152–169`。
- `quality`：质量指标：
  - `bartscore`：BARTScore（用于 QA/Summary），模型 `facebook/bart-large-cnn`；实现参考 `experiments/quality.py:1–8`。
  - `code`：代码质量指标（仅 `code` 任务）：
    - `code_compiles`：能否成功解析为 AST（语法有效性）。
    - `has_binary_search_symbol`：是否包含 `binary_search` 或中文“二分”的语义/符号。
    - `mentions_complexity`：是否提及复杂度（包含 `O(log`、`log n`、`logn` 或“时间复杂度”）。
      定义参考：`experiments/run_experiments.py:184–196`。
  - `creative`：文本多样性指标（仅 `creative` 任务）：
    - `distinct_1`/`distinct_2`/`distinct_3`：唯一 n-gram 占比（`|unique n-grams| / |all n-grams|`）。
    - `length_tokens`：按空白分词的 token 数。
      定义参考：`experiments/run_experiments.py:164–173`。
- `metadata`：元信息：
  - `options`：推理参数（`temperature`、`top_p`、`num_ctx`、`max_tokens`、`seed`）。
  - `timestamp`：采集时间（秒）。
  - `model_info`：`ollama show` 原始信息快照。
  - `model_details`：标签中的模型细节（`digest`、`parameter_size`、`quantization_level`、`family` 等）。
  - `warm_run`：是否进行了预热运行。

## texts/<model>/<case>.txt

- 每次运行的 `generated_text` 纯文本副本，便于人工抽检与外部工具分析。

## config.json

- `timestamp`：本批次实验的时间戳。
- `args`：实验参数快照：
  - `models`：候选模型列表。
  - `runs`：每任务每负载的重复次数。
  - `temperature`/`top_p`：采样参数。
  - `num_ctx`：上下文窗口大小。
  - `max_tokens`：最大生成长度。
  - `seed`：随机种子。
  - `warmup`：是否启用预热运行。
  - `keepalive`：模型保活配置（如 `0s` 表示推理后立即释放）。
- `exp_config_path`：用于覆盖参数的 `config.py` 路径。
- `cases_file`：自定义用例文件路径（如 `test_cases.json`）。

## config.py

- 可覆盖的参数常量：`TEMPERATURE`、`TOP_P`、`NUM_CTX`、`SEED`、`KEEPALIVE`、`WARMUP`、`RUNS`。

## test_cases.json

- 数组形式的测试用例，每项包含：
  - `model`：模型集合或 `"all"`（表示对已安装模型逐一运行）。
  - `prompt`：任务输入。
  - `task_type`：任务类型（映射关系：`knowledge_qa→qa`、`text_summarization→summary`、`creative_writing→creative`、`code_generation→code`）。
  - `reference_text`：参考答案（BARTScore 计算可选）。
  - `max_tokens`/`temperature`：覆盖默认推理参数。
    映射逻辑参考：`experiments/run_experiments.py:452–459`。

## 单位与计算约定

- 时间：秒（`_seconds` 字段）或纳秒（`_ns` 字段）；吞吐量单位为 tokens/s。
- 资源占用：
  - 利用率：百分比（%）。
  - 显存：MB；内存：MB。
  - 功率：W；能耗：J，按功率与采样时间的积分累计。
- 采样间隔：默认 `0.2s`（资源监控）。
- BARTScore 数值范围：通常为负值区间，越高（越不负）表示质量更好。

## 关联可视化与分析

- Notebook/脚本可能对 `results.csv` 做列重命名或归一化（例如 `tps`、`latency`、`energy`、`norm_*`、`efficiency_score`、`qe_ratio`），但这些属于二次分析派生指标，原始定义以本文件为准。
