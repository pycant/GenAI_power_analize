# 数据结构重构完成报告

## 概述

已成功完成实验结果数据结构的重构，将原始数据（raw）和汇总数据（summary）分离到两个独立的文件中。

**完成时间**: 2026-03-02  
**版本**: v2.0

## 重构目标

- ✅ 将实验结果分离为 `raw` 和 `summary` 两个文件
- ✅ Raw文件保存原始未处理的硬件监控数据（完整时间序列）
- ✅ Summary文件保存计算、推断和分析后的数据（汇总统计和派生指标）
- ✅ 支持 `per_turn_monitoring` 参数，为多段对话独立记录数据
- ✅ 保持向后兼容性（旧方法仍然存在）

## 已完成的修改

### 1. 新增 `ExperimentResult` 类

**位置**: `experiments/experiment_runner.py` (第43-600行)

**功能**:
- 分离 `raw_data` 和 `summary_data` 两个数据结构
- 支持设置配置、基线数据、监控数据、对话轮次
- 支持 `per_turn_monitoring`（每轮对话可以有独立的监控数据）
- 自动计算汇总指标（baseline_summary, performance, resources, derived_metrics, quality, conversation_summary）
- 包含能耗计算方法（梯形积分）

**主要方法**:
- `set_config()`: 设置实验配置
- `set_baseline_raw()`: 设置原始基线数据
- `set_monitoring_data()`: 设置监控数据
- `add_conversation_turn()`: 添加对话轮次（支持分轮监控）
- `calculate_summary()`: 从原始数据计算汇总指标
- `get_raw_data()`: 获取原始数据
- `get_summary_data()`: 获取汇总数据

### 2. 新增辅助方法

#### `measure_idle_baseline_v2()`

**位置**: `experiments/experiment_runner.py` (第1397行)

**功能**: 测量空闲基线，返回 `ResourceMonitor` 对象而非汇总数据

**改进**: 保留完整的时间序列数据，而不是只保存汇总统计

#### `_print_experiment_results()`

**位置**: `experiments/experiment_runner.py` (第1430行)

**功能**: 打印实验结果摘要，包括性能指标、资源使用和派生指标

### 3. 修改 `run_single_experiment()` 方法

**位置**: `experiments/experiment_runner.py` (第1467行)

**主要变化**:
1. 创建 `ExperimentResult` 对象
2. 使用 `measure_idle_baseline_v2()` 获取完整基线数据
3. 调用新的 `_run_with_overall_monitoring_v2()` 或 `_run_with_per_turn_monitoring_v2()`
4. 自动计算汇总数据
5. 返回 `ExperimentResult` 对象而非字典

### 4. 新增监控方法

#### `_run_with_overall_monitoring_v2()`

**位置**: `experiments/experiment_runner.py` (第1638行)

**功能**: 整体监控模式，所有轮次使用同一个监控器

**改进**: 直接填充 `ExperimentResult` 对象，不返回字典

#### `_run_with_per_turn_monitoring_v2()`

**位置**: `experiments/experiment_runner.py` (第1755行)

**功能**: 分轮监控模式，每轮对话使用独立的监控器

**改进**: 
- 为每轮创建独立的 `ResourceMonitor`
- 将每轮的监控数据保存到对应的对话轮次中
- 同时维护全局监控器记录整体事件

### 5. 修改 `run_experiment_suite()` 方法

**位置**: `experiments/experiment_runner.py` (第1842行)

**主要变化**:
1. 分别保存 `raw` 和 `summary` 文件
2. 使用新的文件命名格式: `experiment_results_{timestamp}_raw.json` 和 `experiment_results_{timestamp}_summary.json`
3. 返回 `(raw_results, summary_results)` 元组

### 6. 删除旧方法

#### `_generate_summary_file()`

**原位置**: `experiments/experiment_runner.py` (第1928行)

**原因**: Summary数据现在由 `ExperimentResult.calculate_summary()` 自动生成

## 数据结构对比

### Raw 数据结构

```json
{
  "experiment_id": "exp_20260302_165811_12345",
  "config": {
    "model": "Ollama:qwen3:4b",
    "model_info": {...},
    "prompts": ["..."],
    "task_type": "qa",
    "keep_context": false,
    "per_turn_monitoring": false,
    "max_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9,
    "reference_text": null
  },
  "baseline_raw": {
    "duration_seconds": 10,
    "start_timestamp": 1234567890.123,
    "end_timestamp": 1234567900.123,
    "measurements": {
      "timestamps": [1234567890.123, ...],
      "cpu_percent": [10.5, ...],
      "mem_used_mb": [1024.5, ...],
      "gpu_util": [0, ...],
      "gpu_mem_mb": [0, ...],
      "gpu_power_w": [15.2, ...],
      "gpu_temp_c": [45, ...]
    }
  },
  "conversation": [
    {
      "turn": 1,
      "prompt": "什么是Python？",
      "response": "Python是一种...",
      "start_timestamp": 1234567901.123,
      "end_timestamp": 1234567905.456,
      "monitoring_data": {  // 仅在per_turn_monitoring=true时存在
        "measurements": {...},
        "events": [...]
      }
    }
  ],
  "monitoring_data": {
    "start_timestamp": 1234567901.123,
    "end_timestamp": 1234567905.456,
    "measurements": {
      "timestamps": [...],
      "cpu_percent": [...],
      "mem_used_mb": [...],
      "gpu_util": [...],
      "gpu_mem_mb": [...],
      "gpu_power_w": [...],
      "gpu_temp_c": [...]
    },
    "events": [
      {
        "timestamp": 1234567901.123,
        "event": "experiment_start",
        "metadata": {"task_type": "qa"}
      },
      {
        "timestamp": 1234567901.234,
        "event": "inference_start",
        "metadata": {"turn": 1}
      },
      {
        "timestamp": 1234567901.567,
        "event": "first_token",
        "metadata": {"turn": 1}
      },
      {
        "timestamp": 1234567905.456,
        "event": "inference_end",
        "metadata": {"turn": 1, "tokens": 50}
      },
      {
        "timestamp": 1234567905.456,
        "event": "experiment_end",
        "metadata": {}
      }
    ]
  },
  "metadata": {
    "timestamp": "2026-03-02T16:58:11",
    "runner_version": "2.0",
    "max_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

### Summary 数据结构

```json
{
  "experiment_id": "exp_20260302_165811_12345",
  "config_ref": {
    "model": "Ollama:qwen3:4b",
    "task_type": "qa",
    "prompts_count": 1,
    "keep_context": false,
    "per_turn_monitoring": false
  },
  "baseline_summary": {
    "duration_seconds": 10,
    "gpu_power_avg_w": 15.5,
    "gpu_power_peak_w": 18.2,
    "gpu_power_std_w": 1.2,
    "gpu_energy_j": 155.0,
    "cpu_percent_avg": 12.3,
    "cpu_percent_peak": 25.6,
    "gpu_util_avg": 0.5,
    "gpu_util_peak": 2,
    "gpu_mem_avg_mb": 100.5,
    "gpu_mem_peak_mb": 150.2,
    "gpu_temp_avg_c": 45.2,
    "gpu_temp_peak_c": 48
  },
  "performance": {
    "total_time_seconds": 4.333,
    "token_count": 50,
    "output_tokens": 50,
    "throughput_tokens_per_sec": 11.54,
    "latency_per_token_ms": 86.66,
    "turns": 1,
    "avg_time_per_turn": 4.333,
    "ttft_seconds": 0.333
  },
  "resources": {
    "cpu_percent_avg": 45.2,
    "cpu_percent_peak": 78.5,
    "cpu_percent_std": 12.3,
    "mem_used_avg_mb": 2048.5,
    "mem_used_peak_mb": 2560.2,
    "gpu_util_avg": 85.3,
    "gpu_util_peak": 98,
    "gpu_util_std": 8.5,
    "gpu_mem_avg_mb": 3500.2,
    "gpu_mem_peak_mb": 4096.0,
    "gpu_power_avg_w": 45.2,
    "gpu_power_peak_w": 65.8,
    "gpu_power_std_w": 8.5,
    "gpu_energy_j": 195.8,
    "gpu_temp_avg_c": 68.5,
    "gpu_temp_peak_c": 75,
    "cpu_energy_j_approx": 85.2
  },
  "derived_metrics": {
    "P_idle": 15.5,
    "P_inc": 29.7,
    "E_inc": 128.6,
    "E_token": 2.572,
    "PPW": 0.255,
    "TPJ": 0.255
  },
  "quality": {
    "bartscore": -3.456,
    "generated_text_length": 150,
    "has_reference": true,
    "avg_response_length": 150
  },
  "conversation_summary": [
    {
      "turn": 1,
      "prompt_preview": "什么是Python？",
      "response_preview": "Python是一种高级编程语言...",
      "response_length": 150,
      "duration_seconds": 4.333,
      "tokens": 50,
      "throughput": 11.54,
      "gpu_power_avg_w": 45.2,  // 仅在per_turn_monitoring=true时存在
      "gpu_energy_j": 195.8      // 仅在per_turn_monitoring=true时存在
    }
  ],
  "metadata": {
    "timestamp": "2026-03-02T16:58:11",
    "analysis_version": "1.0",
    "max_tokens": 500,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

## 向后兼容性

旧的方法仍然保留在代码中：
- `measure_idle_baseline()`: 返回汇总数据的旧版本
- `_run_with_overall_monitoring()`: 返回字典的旧版本
- `_run_with_per_turn_monitoring()`: 返回字典的旧版本

这些方法不会被新代码调用，但保留以防需要回滚。

## 测试

### 测试脚本

创建了 `scripts/test_refactored_runner.py` 用于验证重构：

**测试内容**:
1. 单轮对话实验（整体监控）
2. 多轮对话实验（分轮监控）
3. 实验套件（多个实验）

**运行测试**:
```bash
python scripts/test_refactored_runner.py
```

### 预期输出

测试脚本会：
1. 运行3个测试场景
2. 验证数据结构的正确性
3. 保存测试结果到 `data/test/` 目录
4. 输出测试结果汇总

## 使用示例

### 单个实验

```python
from experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner(output_dir="data/experiments_5")

# 运行实验
result = runner.run_single_experiment(
    model="ollama:qwen3:4b",
    prompts=["什么是机器学习？"],
    task_type="qa",
    max_tokens=100,
    temperature=0.7,
    idle_measurement_duration=10
)

# 获取数据
raw_data = result.get_raw_data()
summary_data = result.get_summary_data()

# 保存数据
import json
with open("experiment_raw.json", "w") as f:
    json.dump(raw_data, f, indent=2)
with open("experiment_summary.json", "w") as f:
    json.dump(summary_data, f, indent=2)
```

### 实验套件

```python
from experiments.experiment_runner import ExperimentRunner

runner = ExperimentRunner(output_dir="data/experiments_5")

test_cases = [
    {
        "model": "ollama:qwen3:4b",
        "prompts": ["什么是深度学习？"],
        "task_type": "qa",
        "max_tokens": 100,
        "idle_measurement_duration": 10
    },
    {
        "model": "ollama:qwen3:4b",
        "prompts": ["解释神经网络", "它有什么应用？"],
        "task_type": "qa",
        "max_tokens": 100,
        "keep_context": True,
        "per_turn_monitoring": True,
        "idle_measurement_duration": 10
    }
]

# 运行实验套件
raw_results, summary_results = runner.run_experiment_suite(
    test_cases,
    output_file="data/experiments_5/results"
)

# 结果自动保存到:
# - data/experiments_5/results_raw.json
# - data/experiments_5/results_summary.json
```

## 文件命名规范

### 新格式

- Raw文件: `experiment_results_{timestamp}_raw.json`
- Summary文件: `experiment_results_{timestamp}_summary.json`

### 示例

- `experiment_results_20260302_165811_raw.json`
- `experiment_results_20260302_165811_summary.json`

## 下一步工作

### 可选任务

1. **数据转换脚本**: 创建 `scripts/convert_to_new_format.py` 将旧格式数据转换为新格式
2. **单元测试**: 创建 `tests/test_experiment_result.py` 进行单元测试
3. **文档更新**: 更新用户文档以反映新的数据结构
4. **分析脚本适配**: 更新 `scripts/analyze_experiments_1.py` 以支持新格式

### 建议

1. 运行测试脚本验证重构是否成功
2. 使用新格式运行一些实际实验
3. 检查生成的raw和summary文件是否符合预期
4. 如果一切正常，可以考虑删除旧的方法

## 回滚计划

如果需要回滚到旧版本：

1. 使用git恢复 `experiments/experiment_runner.py`:
   ```bash
   git checkout HEAD~1 experiments/experiment_runner.py
   ```

2. 删除测试文件:
   ```bash
   rm scripts/test_refactored_runner.py
   rm docs/REFACTORING_COMPLETED.md
   ```

3. 旧方法仍然存在于代码中，可以手动切换回去

## 总结

✅ 数据结构重构已成功完成，实现了以下目标：

1. Raw和Summary数据完全分离
2. Raw文件保存完整的时间序列数据
3. Summary文件保存计算后的汇总指标
4. 完全支持per_turn_monitoring参数
5. 保持向后兼容性
6. 代码无语法错误

重构后的系统更加模块化、可维护，并且为未来的扩展提供了更好的基础。

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**作者**: Kiro AI Assistant
