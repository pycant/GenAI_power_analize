# 数据结构重构方案

## 目标

将实验结果数据分离为两个文件，明确区分原始数据和处理后的数据：

1. **experiment_results_raw_*.json**: 保存原始未处理的监控数据
2. **experiment_results_summary_*.json**: 保存计算、推断和分析后的数据

## 数据分离原则

### Raw文件（原始数据）

保存直接从硬件/系统采集的原始数据，不包含任何计算或推断的指标。

**包含内容**:
- 基本配置信息（model, prompts, task_type等）
- 对话原始记录（conversation）
- 原始监控时间序列数据（system_metrics_full）
- 空闲基线原始测量数据（baseline_raw）
- 事件标记（events）

**不包含**:
- 计算得出的性能指标（throughput, latency等）
- 汇总统计数据（avg, peak等）
- 推断的能耗数据（cpu_energy_j_approx）
- 增量指标（P_inc, E_inc, E_token, PPW, TPJ）
- 质量评估结果（bartscore）

### Summary文件（汇总数据）

保存所有计算、推断和分析后的数据，便于直接使用和分析。

**包含内容**:
- 基本配置信息（引用）
- 性能指标（performance）
- 资源汇总统计（resources）
- 增量指标（derived_metrics）
- 质量评估（quality）
- 对话摘要（conversation_summary）

**不包含**:
- 完整的时间序列数据
- 详细的事件日志

## 新的数据结构

### 1. Raw文件结构

```json
{
  "experiment_id": "exp_20260302_165811_001",
  "config": {
    "model": "HF:Qwen--Qwen2.5-7B-Instruct:4bit",
    "model_info": { ... },
    "prompts": [ ... ],
    "task_type": "qa",
    "keep_context": true,
    "per_turn_monitoring": false,
    "max_tokens": 150,
    "temperature": 0.5,
    "top_p": 0.9,
    "reference_text": null
  },
  "baseline_raw": {
    "duration_seconds": 10,
    "start_timestamp": 1772441901.8263838,
    "end_timestamp": 1772441911.8263838,
    "measurements": {
      "timestamps": [1772441901.826, 1772441902.026, ...],
      "cpu_percent": [8.5, 9.2, 8.1, ...],
      "mem_used_mb": [7234.5, 7235.2, ...],
      "gpu_util": [4, 5, 3, ...],
      "gpu_mem_mb": [3100.2, 3100.5, ...],
      "gpu_power_w": [15.2, 15.5, 15.1, ...],
      "gpu_temp_c": [45, 45, 46, ...]
    }
  },
  "conversation": [
    {
      "turn": 1,
      "prompt": "什么是Python？",
      "response": "Python是一种高级编程语言...",
      "start_timestamp": 1772441912.0,
      "end_timestamp": 1772441965.8
    },
    {
      "turn": 2,
      "prompt": "它有哪些主要特点？",
      "response": "以下是Python的一些主要特点...",
      "start_timestamp": 1772441965.9,
      "end_timestamp": 1772442021.8
    }
  ],
  "monitoring_data": {
    "start_timestamp": 1772441912.0,
    "end_timestamp": 1772442077.1,
    "measurements": {
      "timestamps": [1772441912.0, 1772441912.2, ...],
      "cpu_percent": [0.0, 38.8, 35.3, ...],
      "mem_used_mb": [7234.5, 7245.2, ...],
      "gpu_util": [0, 45, 67, ...],
      "gpu_mem_mb": [3100.2, 6234.5, ...],
      "gpu_power_w": [15.3, 45.2, 60.8, ...],
      "gpu_temp_c": [45, 52, 67, ...]
    },
    "events": [
      {
        "timestamp": 1772441912.0,
        "event": "experiment_start",
        "metadata": {}
      },
      {
        "timestamp": 1772441912.0,
        "event": "inference_start",
        "metadata": {"turn": 1}
      },
      {
        "timestamp": 1772441965.8,
        "event": "first_token",
        "metadata": {"turn": 1}
      },
      {
        "timestamp": 1772441965.8,
        "event": "inference_end",
        "metadata": {"turn": 1, "tokens": 150}
      }
    ]
  },
  "metadata": {
    "timestamp": "2026-03-02T17:01:17.656786",
    "runner_version": "2.0",
    "monitor_interval": 0.2
  }
}
```

### 2. Summary文件结构

```json
{
  "experiment_id": "exp_20260302_165811_001",
  "config_ref": {
    "model": "HF:Qwen--Qwen2.5-7B-Instruct:4bit",
    "task_type": "qa",
    "prompts_count": 3,
    "keep_context": true
  },
  "baseline_summary": {
    "duration_seconds": 10,
    "gpu_power_avg_w": 15.31,
    "gpu_power_peak_w": 23.02,
    "gpu_power_std_w": 2.15,
    "gpu_energy_j": 148.40,
    "cpu_percent_avg": 8.74,
    "cpu_percent_peak": 12.5,
    "gpu_util_avg": 4.43,
    "gpu_util_peak": 8,
    "gpu_mem_avg_mb": 3100.28,
    "gpu_mem_peak_mb": 3100.50,
    "gpu_temp_avg_c": 45.2,
    "gpu_temp_peak_c": 46
  },
  "performance": {
    "total_time_seconds": 158.36,
    "token_count": 450,
    "output_tokens": 450,
    "throughput_tokens_per_sec": 2.84,
    "latency_per_token_ms": 351.92,
    "turns": 3,
    "avg_time_per_turn": 52.79,
    "ttft_seconds": 12.5
  },
  "resources": {
    "cpu_percent_avg": 24.86,
    "cpu_percent_peak": 100.0,
    "cpu_percent_std": 18.45,
    "mem_used_avg_mb": 14523.2,
    "mem_used_peak_mb": 15405.84,
    "gpu_util_avg": 66.94,
    "gpu_util_peak": 100,
    "gpu_util_std": 25.67,
    "gpu_mem_avg_mb": 7234.5,
    "gpu_mem_peak_mb": 8147.55,
    "gpu_power_avg_w": 33.08,
    "gpu_power_peak_w": 65.23,
    "gpu_power_std_w": 12.34,
    "gpu_energy_j": 5797.85,
    "gpu_temp_avg_c": 62.3,
    "gpu_temp_peak_c": 67,
    "cpu_energy_j_approx": 2856.08
  },
  "derived_metrics": {
    "P_idle": 15.31,
    "P_inc": 17.77,
    "E_inc": 3373.65,
    "E_token": 7.50,
    "PPW": 0.086,
    "TPJ": 0.078,
    "efficiency_score": 0.65,
    "energy_efficiency_class": "B"
  },
  "quality": {
    "bartscore": null,
    "generated_text_length": 316,
    "has_reference": false,
    "avg_response_length": 105.3,
    "distinct_1": 0.85,
    "distinct_2": 0.92
  },
  "conversation_summary": [
    {
      "turn": 1,
      "prompt_preview": "什么是Python？",
      "response_preview": "Python是一种高级编程语言...",
      "response_length": 150,
      "duration_seconds": 53.8,
      "tokens": 150,
      "throughput": 2.79
    },
    {
      "turn": 2,
      "prompt_preview": "它有哪些主要特点？",
      "response_preview": "以下是Python的一些主要特点...",
      "response_length": 145,
      "duration_seconds": 55.9,
      "tokens": 145,
      "throughput": 2.59
    },
    {
      "turn": 3,
      "prompt_preview": "请给我一个简单的代码示例。",
      "response_preview": "以下是一个简单的 Python 代码示例...",
      "response_length": 155,
      "duration_seconds": 55.3,
      "tokens": 155,
      "throughput": 2.80
    }
  ],
  "metadata": {
    "timestamp": "2026-03-02T17:01:17.656786",
    "analysis_version": "1.0",
    "raw_data_file": "experiment_results_raw_20260302_165811.json"
  }
}
```

## 实施步骤

### 阶段1: 代码重构

1. **修改 `run_single_experiment` 方法**
   - 分离原始数据收集和指标计算
   - 返回包含raw和summary两部分的结果

2. **修改 `_run_with_overall_monitoring` 方法**
   - 只收集原始监控数据
   - 不进行汇总计算

3. **新增 `_calculate_summary_metrics` 方法**
   - 从原始数据计算所有汇总指标
   - 计算增量指标
   - 计算质量评估

4. **修改 `run_experiment_suite` 方法**
   - 分别保存raw和summary文件
   - 保持文件命名一致性

### 阶段2: 数据迁移

1. **创建数据转换脚本**
   - 读取旧格式的结果文件
   - 分离为raw和summary两个文件
   - 保持向后兼容

2. **更新分析脚本**
   - 修改 `scripts/analyze_experiments_1.py`
   - 从summary文件读取数据
   - 必要时从raw文件读取详细数据

### 阶段3: 文档更新

1. **更新使用指南**
   - 说明新的数据结构
   - 提供数据访问示例
   - 更新字段说明

2. **创建迁移指南**
   - 说明如何转换旧数据
   - 提供兼容性说明

## 优势

### 1. 数据清晰度
- 原始数据和处理数据明确分离
- 便于数据验证和审计
- 支持重新计算和分析

### 2. 存储优化
- Raw文件可以压缩存储
- Summary文件体积小，便于快速访问
- 可以选择性保留raw文件

### 3. 分析灵活性
- 可以从原始数据重新计算指标
- 支持不同的分析方法
- 便于添加新的派生指标

### 4. 可复现性
- 保留完整的原始数据
- 计算过程可追溯
- 支持第三方验证

## 向后兼容

### 过渡期方案

在过渡期，同时支持新旧两种格式：

1. **读取时自动检测格式**
   - 检查文件结构判断版本
   - 自动转换为统一的内部格式

2. **提供格式转换工具**
   - `scripts/convert_old_format.py`
   - 批量转换历史数据

3. **保持API兼容**
   - 分析脚本自动适配两种格式
   - 逐步迁移到新格式

## 时间表

- **Week 1**: 代码重构和测试
- **Week 2**: 数据迁移工具开发
- **Week 3**: 文档更新和用户测试
- **Week 4**: 正式发布和历史数据迁移

## 相关文件

- `experiments/experiment_runner.py` - 主要修改文件
- `scripts/analyze_experiments_1.py` - 需要更新
- `docs/EXPERIMENT_RUNNER_GUIDE.md` - 需要更新
- `scripts/convert_old_format.py` - 新增转换工具

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**作者**: Kiro AI Assistant
