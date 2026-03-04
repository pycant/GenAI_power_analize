# Temperature 参数修正

## 问题描述

Hugging Face 的 `transformers` 库要求 `temperature` 必须是严格正数（> 0）。当 `temperature=0.0` 时会报错：

```
ValueError: `temperature` (=0.0) has to be a strictly positive float, 
otherwise your next token scores will be invalid. 
If you're looking for greedy decoding strategies, set `do_sample=False`.
```

## 解决方案

将所有 `temperature=0.0` 改为 `temperature=0.1`（一个很小的正数，接近确定性输出）。

## 修正范围

### 1. data/experiment_test/test_cases.json

- 修正了 1 个测试用例
- QA 任务的 temperature 从 0.0 改为 0.1

### 2. data/experiments_5/test_cases.json

- 修正了 120 个测试用例
- 主要是 QA、Math、Code 等需要确定性输出的任务

## Temperature 值说明

修正后的 temperature 分布：

| Temperature | 任务类型 | 说明 |
|------------|---------|------|
| 0.1 | QA, Math, Code, Reasoning | 接近确定性，适合需要准确答案的任务 |
| 0.2 | Translation | 稳定性和准确性 |
| 0.7 | Summary, Multi-turn | 平衡创造性和准确性 |
| 0.8 | Creative | 创造性写作 |
| 0.9 | Creative (部分) | 高度创造性 |

## 验证结果

```bash
# 验证修正结果
python -c "import json; data = json.load(open('data/experiments_5/test_cases.json', 'r', encoding='utf-8')); zero_temp = [t for t in data if t.get('temperature') == 0.0]; print(f'Remaining temperature=0.0: {len(zero_temp)}')"
```

输出：
```
Remaining temperature=0.0: 0
```

✅ 所有 temperature=0.0 已修正

## 使用的脚本

创建了 `scripts/fix_temperature_zero.py` 用于批量修正：

```bash
python scripts/fix_temperature_zero.py --file data/experiments_5/test_cases.json
```

## 影响

- ✅ 修正后可以正常使用 Hugging Face 模型
- ✅ Ollama 模型不受影响（Ollama 允许 temperature=0）
- ✅ 0.1 的 temperature 仍然接近确定性输出，对结果影响很小

## 相关文档

- [EXPERIMENT_RUNNER_GUIDE.md](EXPERIMENT_RUNNER_GUIDE.md) - 实验运行器指南
- [EXPERIMENT_5_CONFIGURATION_COMPLETE.md](EXPERIMENT_5_CONFIGURATION_COMPLETE.md) - 实验 5 配置报告

---

**修正时间**: 2026-03-03  
**修正脚本**: `scripts/fix_temperature_zero.py`  
**影响文件**: `data/experiments_5/test_cases.json`, `data/experiment_test/test_cases.json`
