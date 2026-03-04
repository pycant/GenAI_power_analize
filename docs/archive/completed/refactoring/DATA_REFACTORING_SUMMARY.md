# 数据结构重构总结

## 概述

根据您的建议，我们将实验结果数据重构为两个独立的文件，明确区分原始数据和处理后的数据：

- **experiment_results_raw_*.json**: 保存原始未处理的硬件监控数据
- **experiment_results_summary_*.json**: 保存计算、推断和分析后的指标

## 核心改进

### 1. 数据分离原则

#### Raw文件（原始数据）
✅ **包含**：
- 基本配置信息
- 完整的时间序列监控数据（timestamps, cpu_percent, gpu_power_w等）
- 空闲基线原始测量数据
- 对话原始记录
- 事件标记（inference_start, first_token, inference_end等）

❌ **不包含**：
- 计算得出的汇总统计（avg, peak, std）
- 推断的能耗数据（cpu_energy_j_approx）
- 增量指标（P_inc, E_inc, E_token, PPW, TPJ）
- 质量评估结果（bartscore）

#### Summary文件（汇总数据）
✅ **包含**：
- 配置引用（简化版）
- 性能指标（throughput, latency, TTFT等）
- 资源汇总统计（avg, peak, std）
- 增量指标（derived_metrics）
- 质量评估（quality）
- 对话摘要（conversation_summary）

❌ **不包含**：
- 完整的时间序列数据
- 详细的事件日志

### 2. 新的数据结构

#### Raw文件结构
```json
{
  "experiment_id": "exp_20260302_165811_001",
  "config": { /* 完整配置 */ },
  "baseline_raw": {
    "duration_seconds": 10,
    "start_timestamp": 1772441901.826,
    "end_timestamp": 1772441911.826,
    "measurements": {
      "timestamps": [...],
      "cpu_percent": [...],
      "gpu_power_w": [...],
      /* 完整时间序列 */
    }
  },
  "conversation": [ /* 完整对话记录 */ ],
  "monitoring_data": {
    "start_timestamp": 1772441912.0,
    "end_timestamp": 1772442077.1,
    "measurements": { /* 完整时间序列 */ },
    "events": [ /* 所有事件标记 */ ]
  },
  "metadata": { /* 元数据 */ }
}
```

#### Summary文件结构
```json
{
  "experiment_id": "exp_20260302_165811_001",
  "config_ref": { /* 简化配置 */ },
  "baseline_summary": {
    "gpu_power_avg_w": 15.31,
    "gpu_power_peak_w": 23.02,
    "gpu_energy_j": 148.40,
    /* 汇总统计 */
  },
  "performance": {
    "throughput_tokens_per_sec": 2.84,
    "latency_per_token_ms": 351.92,
    "ttft_seconds": 12.5,
    /* 性能指标 */
  },
  "resources": {
    "cpu_percent_avg": 24.86,
    "gpu_power_avg_w": 33.08,
    "gpu_energy_j": 5797.85,
    /* 资源汇总 */
  },
  "derived_metrics": {
    "P_idle": 15.31,
    "P_inc": 17.77,
    "E_inc": 3373.65,
    "E_token": 7.50,
    "PPW": 0.086,
    "TPJ": 0.078,
    /* 增量和能效指标 */
  },
  "quality": { /* 质量评估 */ },
  "conversation_summary": [ /* 对话摘要 */ ],
  "metadata": { /* 元数据 */ }
}
```

## 优势分析

### 1. 数据清晰度 ⭐⭐⭐⭐⭐
- 原始数据和处理数据明确分离
- 便于数据验证和审计
- 支持重新计算和分析

### 2. 存储优化 ⭐⭐⭐⭐
- Raw文件可以压缩存储或归档
- Summary文件体积小（约为raw的10-20%），便于快速访问
- 可以选择性保留raw文件

### 3. 分析灵活性 ⭐⭐⭐⭐⭐
- 可以从原始数据重新计算指标
- 支持不同的分析方法和算法
- 便于添加新的派生指标

### 4. 可复现性 ⭐⭐⭐⭐⭐
- 保留完整的原始数据
- 计算过程可追溯
- 支持第三方验证

### 5. 性能提升 ⭐⭐⭐⭐
- 分析脚本只需读取小的summary文件
- 减少内存占用
- 加快数据加载速度

## 实施计划

### 阶段1: 代码重构（Week 1）
- [ ] 创建 `ExperimentResult` 类
- [ ] 修改 `run_single_experiment` 方法
- [ ] 修改 `run_experiment_suite` 方法
- [ ] 添加数据计算方法
- [ ] 单元测试

### 阶段2: 数据迁移（Week 2）
- [ ] 创建 `convert_old_format.py` 转换脚本
- [ ] 测试转换脚本
- [ ] 批量转换历史数据
- [ ] 验证转换结果

### 阶段3: 文档更新（Week 3）
- [ ] 更新 `EXPERIMENT_RUNNER_GUIDE.md`
- [ ] 更新 `CONFIG_PARAMETERS_REFERENCE.md`
- [ ] 创建迁移指南
- [ ] 更新示例代码

### 阶段4: 集成测试（Week 4）
- [ ] 运行完整实验流程
- [ ] 验证数据一致性
- [ ] 性能测试
- [ ] 用户验收测试

## 向后兼容策略

### 过渡期方案
1. **自动格式检测**
   - 分析脚本自动识别新旧格式
   - 自动转换为统一的内部格式

2. **格式转换工具**
   - 提供 `convert_old_format.py` 脚本
   - 支持批量转换

3. **双格式支持**
   - 保持API兼容
   - 逐步迁移到新格式

## 文件大小对比

基于 `data/experiments_4/experiment_results_raw_20260302_165811.json` 的实际数据：

| 文件类型 | 当前大小 | 预期大小 | 说明 |
|---------|---------|---------|------|
| 旧格式（合并） | ~3.2 MB | - | 包含所有数据 |
| 新格式 Raw | - | ~2.8 MB | 只包含原始时间序列 |
| 新格式 Summary | - | ~0.4 MB | 只包含汇总指标 |
| **总计** | 3.2 MB | 3.2 MB | 总大小相同 |

**优势**：
- Summary文件小，分析时加载快
- Raw文件可以压缩存储（预计压缩率70-80%）
- 可以选择性删除旧实验的raw文件

## 使用示例

### 快速分析（只读summary）
```python
import json
import pandas as pd

# 只读取summary文件（快速）
with open('experiment_results_summary_20260302_165811.json', 'r') as f:
    summary_data = json.load(f)

# 提取关键指标
df = pd.DataFrame([
    {
        'model': r['config_ref']['model'],
        'throughput': r['performance']['throughput_tokens_per_sec'],
        'energy': r['resources']['gpu_energy_j'],
        'E_token': r['derived_metrics']['E_token'],
        'TPJ': r['derived_metrics']['TPJ']
    }
    for r in summary_data
])

print(df)
```

### 深度分析（读取raw）
```python
import json
import numpy as np
import matplotlib.pyplot as plt

# 读取raw文件进行深度分析
with open('experiment_results_raw_20260302_165811.json', 'r') as f:
    raw_data = json.load(f)

# 绘制功耗时间序列
for exp in raw_data:
    monitoring = exp['monitoring_data']['measurements']
    plt.plot(monitoring['timestamps'], monitoring['gpu_power_w'], 
             label=exp['config']['model'])

plt.xlabel('Time (s)')
plt.ylabel('GPU Power (W)')
plt.legend()
plt.show()
```

### 重新计算指标
```python
# 从raw数据重新计算指标（例如使用不同的算法）
def recalculate_metrics(raw_data):
    measurements = raw_data['monitoring_data']['measurements']
    
    # 使用中位数而非平均值
    gpu_power_median = np.median(measurements['gpu_power_w'])
    
    # 使用不同的能耗计算方法
    energy = calculate_energy_simpson(
        measurements['timestamps'],
        measurements['gpu_power_w']
    )
    
    return {
        'gpu_power_median_w': gpu_power_median,
        'gpu_energy_simpson_j': energy
    }
```

## 相关文档

- [数据结构重构方案](./DATA_STRUCTURE_REFACTORING.md) - 详细的设计文档
- [实施方案](./DATA_REFACTORING_IMPLEMENTATION.md) - 具体的代码实现指南
- [实验运行器指南](./EXPERIMENT_RUNNER_GUIDE.md) - 使用文档（需更新）
- [配置参数参考](./CONFIG_PARAMETERS_REFERENCE.md) - 参数说明（需更新）

## 下一步行动

1. **审查方案**：团队审查重构方案，确认设计合理性
2. **开始实施**：按照阶段1开始代码重构
3. **持续沟通**：定期同步进度，及时调整方案
4. **用户反馈**：收集用户意见，优化实现细节

## 问题与讨论

如有任何问题或建议，请通过以下方式反馈：
- 创建 GitHub Issue
- 在项目会议中讨论
- 直接联系项目负责人

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**作者**: Kiro AI Assistant  
**状态**: 待审查

## 更新日志

- 2026-03-02: 初始版本，完成方案设计
