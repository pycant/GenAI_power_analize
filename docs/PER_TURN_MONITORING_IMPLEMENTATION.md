# 分轮监控功能实现总结

## 实现日期
2026-03-01

## 功能概述
为多轮对话实验添加了每轮独立监控资源使用的功能，可以精确追踪每个问题的能耗、时间和资源消耗。

## 核心实现

### 1. 新增方法
- `_run_with_per_turn_monitoring()`: 使用每轮独立监控的方式运行实验
- `_run_with_overall_monitoring()`: 使用整体监控的方式运行实验（原有逻辑）
- `_generate_summary_file()`: 从原始数据生成汇总文件

### 2. 配置参数
- `per_turn_monitoring` (bool): 是否启用分轮监控，默认 False
- 在 test_cases.json 中可配置

### 3. 数据分离
实验结果保存为两个文件：
- `experiment_results_raw_{timestamp}.json`: 包含完整监控数据（时间序列）
- `experiment_results_summary_{timestamp}.json`: 只包含关键指标和汇总数据

### 4. 数据结构

#### 原始数据 (raw)
```json
{
  "conversation": [
    {
      "turn": 1,
      "prompt": "...",
      "response": "...",
      "performance": {...},
      "resources": {...},
      "system_metrics_full": {
        "timestamps": [...],
        "cpu_percent": [...],
        "gpu_utilization": [...],
        ...
      }
    }
  ]
}
```

#### 汇总数据 (summary)
```json
{
  "performance": {
    "per_turn_summary": [
      {
        "turn": 1,
        "time_seconds": 4.01,
        "token_count": 3,
        "throughput": 0.75,
        "gpu_energy_j": 219.6,
        "gpu_power_avg_w": 48.8
      }
    ]
  },
  "conversation_summary": [
    {
      "turn": 1,
      "prompt": "...",
      "response": "...",
      "performance": {...},
      "resources": {...}
    }
  ]
}
```

## 测试结果

### 测试配置
- 测试文件: `data/test/test_cases_per_turn_monitoring.json`
- 测试模型: qwen3:4b, gemma3:4b
- 测试场景: 2轮对话，保持上下文

### 测试结果
✅ 所有测试通过
- 分轮监控正常工作
- 数据分离正确实现
- 文件大小对比：
  - 原始数据: ~466KB (包含完整时间序列)
  - 汇总数据: ~8.7KB (只包含关键指标)

## 使用示例

### 命令行运行
```bash
set PYTHONUTF8=1
python experiments/experiment_runner.py --config data/test/test_cases_per_turn_monitoring.json --output-dir data/test
```

### 测试用例配置
```json
{
  "model": "qwen3:4b",
  "prompts": [
    "请解释牛顿第一定律。",
    "请举出一个实际应用例子。"
  ],
  "task_type": "qa",
  "keep_context": true,
  "per_turn_monitoring": true,
  "max_tokens": 200,
  "temperature": 0.7
}
```

## 向后兼容性
- 默认 `per_turn_monitoring=False`，保持原有行为
- 单轮对话自动使用整体监控模式
- 现有测试用例无需修改

## 性能影响
- 每轮监控启停开销: ~0.5秒
- 对于多轮对话，这个开销是可接受的
- 可以通过配置开关灵活控制

## 后续优化建议
1. 考虑添加监控数据的可视化工具
2. 支持导出为CSV格式便于分析
3. 添加更多资源指标（如网络I/O）
4. 优化监控器启停开销
