# 空闲基线功耗测量 - 快速参考

## 一分钟快速上手

### 1. 在测试用例中添加参数

```json
{
  "model": "your-model",
  "prompts": ["your prompt"],
  "task_type": "qa",
  "idle_measurement_duration": 10
}
```

### 2. 运行实验

```bash
python experiments/experiment_runner.py --config your_test_cases.json
```

### 3. 查看结果

结果中会包含：
- `baseline`: 空闲基线数据
- `resources.P_idle`: 空闲功耗
- `resources.P_inc`: 增量功耗
- `resources.E_inc`: 增量能耗
- `resources.E_token`: 每token能耗
- `resources.PPW`: 每瓦性能
- `resources.TPJ`: 能效比

## 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| idle_measurement_duration | int | 0 | 空闲测量时长（秒），0表示不测量 |

## 推荐值

| 场景 | 推荐值 | 说明 |
|------|--------|------|
| 快速测试 | 5 | 快速验证功能 |
| 标准实验 | 10 | 平衡准确性和时间 |
| 精确测量 | 15-30 | 获得更稳定的基线 |

## 计算公式

```
P_inc = P_avg - P_idle
E_inc = E_total - (P_idle × T_total)
E_token = E_inc / output_tokens
PPW = throughput / P_avg
TPJ = output_tokens / E_total
```

## 示例

### 示例1: 单轮对话

```json
{
  "model": "ollama:qwen3:4b",
  "prompts": ["什么是Python？"],
  "task_type": "qa",
  "idle_measurement_duration": 10
}
```

### 示例2: 多轮对话

```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
  "prompts": [
    "什么是Python？",
    "它有哪些主要特点？",
    "请给我一个简单的代码示例。"
  ],
  "task_type": "qa",
  "keep_context": true,
  "idle_measurement_duration": 10
}
```

### 示例3: 不测量（默认）

```json
{
  "model": "ollama:gemma3:4b",
  "prompts": ["写一首诗"],
  "task_type": "creative"
}
```

## 注意事项

⚠️ 测量期间保持系统空闲  
⚠️ 关闭不必要的后台程序  
⚠️ 等待系统温度稳定  
⚠️ 使用稳定的电源供应  

## 故障排除

### 问题: 显示"高级监控不可用"
**解决**: 安装 pynvml: `pip install pynvml`

### 问题: 空闲功耗异常高
**解决**: 关闭所有程序，增加测量时长

### 问题: 增量功耗为负值
**解决**: 重新测量空闲基线，确保环境一致

## 完整文档

详细说明请参考: [IDLE_BASELINE_MEASUREMENT.md](./IDLE_BASELINE_MEASUREMENT.md)

---

**版本**: v1.0 | **更新**: 2026-03-02
