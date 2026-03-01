# 实验测试数据目录

## 目录说明

本目录包含实验测试数据和分析结果，用于验证实验运行器的功能和性能监控能力。

## 文件列表

### 配置文件
- `test_cases.json` - HF模型测试配置（需要解决NumPy兼容性问题）
- `test_cases_ollama.json` - Ollama模型测试配置（已弃用）
- `test_cases_ollama_only.json` - 纯Ollama模型测试配置（推荐使用）

### 实验结果
- `experiment_results_20260228_192556.json` - 第一次运行结果（无详细监控数据）
- `experiment_results_20260228_194736.json` - 第二次运行结果（包含完整监控数据）✅

### 分析报告
- `实验结果分析报告.md` - 第一次实验的详细分析报告
- `监控数据可视化说明.md` - 监控数据使用和可视化完整指南

### 图表目录
- `figures/` - 监控数据可视化图表
  - `monitoring_Ollama_qwen3_4b_summary.png` - qwen3:4b详细监控
  - `monitoring_Ollama_gemma3_4b_code.png` - gemma3:4b详细监控
  - `monitoring_Ollama_deepseek-r1_8b_qa.png` - deepseek-r1:8b详细监控
  - `monitoring_Ollama_qwen3_8b_creative.png` - qwen3:8b详细监控
  - `monitoring_comparison.png` - 多模型对比图表

## 快速开始

### 1. 运行实验

```bash
# 激活conda环境
conda activate bartscore

# 运行Ollama模型实验
python experiments/experiment_runner.py --config data/test/test_cases_ollama_only.json --output-dir data/test
```

### 2. 查看监控数据汇总

```bash
python scripts/visualize_monitoring_data.py data/test/experiment_results_20260228_194736.json --summary-only
```

### 3. 生成可视化图表

```bash
# 生成每个实验的详细图表
python scripts/visualize_monitoring_data.py data/test/experiment_results_20260228_194736.json --output data/test/figures

# 生成多实验对比图表
python scripts/visualize_monitoring_data.py data/test/experiment_results_20260228_194736.json --output data/test/figures --comparison
```

## 实验配置说明

### test_cases_ollama_only.json

包含4个测试用例，覆盖4种任务类型：

1. **文本摘要** (summary) - qwen3:4b
   - 测试模型的文本理解和概括能力
   - 包含参考答案，可计算BARTScore

2. **代码生成** (code) - gemma3:4b
   - 测试模型的编程能力
   - 生成Python函数

3. **问答** (qa) - deepseek-r1:8b
   - 测试模型的推理和解释能力
   - 包含参考答案，可计算BARTScore

4. **创意写作** (creative) - qwen3:8b
   - 测试模型的创造力
   - 生成诗歌

## 监控数据说明

### 采集的指标

每个实验会采集以下实时监控数据（采样间隔0.2秒）：

#### 系统级指标
- CPU使用率（整体 + Ollama进程）
- 内存使用量
- 磁盘I/O（读写字节数）

#### GPU指标
- GPU核心使用率（%）
- GPU显存使用量（MB）
- GPU功耗（W）
- GPU温度（°C）
- GPU能耗（J，累计）

#### 性能指标
- 生成耗时（秒）
- Token数量
- 吞吐量（tokens/s）
- 每Token延迟（ms）

### 数据格式

```json
{
  "system_metrics_summary": {
    "cpu_percent_avg": 39.6,
    "gpu_util_avg": 57.3,
    "gpu_energy_j": 333.21,
    ...
  },
  "system_metrics_full": {
    "timestamps": [1765350107.875741, ...],
    "cpu_percent": [0.0, 23.9, ...],
    "gpu_util": [98, 73, ...],
    "gpu_power_w": [45.2, 46.1, ...],
    ...
  }
}
```

## 实验结果摘要

基于 `experiment_results_20260228_194736.json`：

| 模型 | 任务 | 耗时 | GPU能耗 | 平均GPU使用率 | 显存峰值 |
|------|------|------|---------|---------------|----------|
| qwen3:4b | summary | 6.70s | 333.21 J | 57.3% | 5.9 GB |
| gemma3:4b | code | 10.05s | 428.40 J | 48.7% | 6.6 GB |
| deepseek-r1:8b | qa | 48.06s | 1850.83 J | 90.5% | 8.0 GB |
| qwen3:8b | creative | 42.46s | 1535.45 J | 89.8% | 8.0 GB |

### 关键发现

1. **最快模型**：qwen3:4b（6.70秒）
2. **最节能**：qwen3:4b（333.21 J）
3. **GPU利用率最高**：deepseek-r1:8b（90.5%平均，100%峰值）
4. **显存使用**：8B模型约8GB，4B模型约6GB

## 已知问题

### 1. Token计数不准确

**问题**：部分模型（qwen3、deepseek-r1）的token计数显示为0

**原因**：这些模型使用推理模式，将内容放在`thinking`字段而非`response`字段

**解决方案**：
- 使用Ollama API返回的`eval_count`字段（在`metadata.response_metadata`中）
- 或修改代码以正确提取`thinking`字段内容

### 2. HF模型NumPy兼容性

**问题**：无法运行HF模型测试（`test_cases.json`）

**原因**：bartscore环境中NumPy 2.x与某些依赖不兼容

**解决方案**：
```bash
conda activate bartscore
pip install "numpy<2.0"
```

## 下一步工作

1. ✅ 实现详细监控数据保存
2. ✅ 创建监控数据可视化工具
3. ⏳ 修复Token计数问题
4. ⏳ 解决HF模型NumPy兼容性
5. ⏳ 将数据转换为experiments_1格式，使用analyze_experiments_1.py进行深度分析
6. ⏳ 实现公平性评估指标（Fairness Gap、Gini系数等）

## 参考文档

- [实验结果分析报告](./实验结果分析报告.md) - 第一次实验的详细分析
- [监控数据可视化说明](./监控数据可视化说明.md) - 完整的监控数据使用指南
- [实验运行器文档](../../experiments/experiment_runner.py) - 实验运行器源码
- [可视化脚本](../../scripts/visualize_monitoring_data.py) - 监控数据可视化工具

## 联系与反馈

如有问题或建议，请参考项目根目录的 `AGENTS.md` 文档。
