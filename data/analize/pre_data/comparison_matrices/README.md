# 模型回答对比矩阵说明

## 📋 概述

本目录包含按任务类型组织的模型回答对比矩阵，方便横向对比不同模型在相同题目上的表现。

**生成时间**: 2026-03-04  
**数据来源**: `responses_raw.csv`  
**总任务类型**: 8 种

## 📁 目录结构

```
comparison_matrices/
├── overview.csv                    # 总览统计
├── code/                          # 代码生成任务
│   ├── code_responses.csv         # 回答对比矩阵
│   ├── code_prompts.csv           # 题目参考
│   ├── code_throughput_tps.csv    # 吞吐量对比
│   ├── code_latency_s.csv         # 延迟对比
│   ├── code_gpu_energy_j.csv      # 能耗对比
│   ├── code_gpu_power_avg_w.csv   # 功耗对比
│   ├── code_response_length.csv   # 回答长度对比
│   └── code_token_count.csv       # Token数量对比
├── creative/                      # 创意写作任务
├── math/                          # 数学推理任务
├── multi_turn/                    # 多轮对话任务
├── qa/                            # 问答任务
├── reasoning/                     # 推理任务
├── summary/                       # 文本摘要任务
└── translation/                   # 翻译任务
```

## 📊 矩阵格式

### 回答对比矩阵 (`*_responses.csv`)

**格式**: 行=模型，列=题号，单元格=完整回答

**示例**:
```
model              | q01        | q02        | q03        | ...
-------------------|------------|------------|------------|----
deepseek_8b_ol_q4km| 完整回答1  | 完整回答2  | 完整回答3  | ...
gemma_2b_hf_4bit   | 完整回答1  | 完整回答2  | 完整回答3  | ...
...                | ...        | ...        | ...        | ...
```

**用途**:
- 横向对比不同模型在同一题目上的回答质量
- 识别模型的优势和劣势
- 人工评估回答的准确性和完整性

### 性能指标矩阵 (`*_throughput_tps.csv` 等)

**格式**: 行=模型，列=题号，单元格=指标值

**可用指标**:
- `throughput_tps`: 吞吐量（tokens/秒）
- `latency_s`: 延迟（秒）
- `gpu_energy_j`: GPU 能耗（焦耳）
- `gpu_power_avg_w`: GPU 平均功耗（瓦特）
- `response_length`: 回答字符长度
- `token_count`: 生成的 token 数量

**用途**:
- 对比不同模型在相同题目上的性能表现
- 识别性能瓶颈
- 分析能耗效率

### 题目参考表 (`*_prompts.csv`)

**格式**: 题号 → 完整 prompt

**示例**:
```
question_id | prompt
------------|--------------------------------------------------
q01         | def multiply(a, b): """Complete the function...
q02         | def triples_sum_to_zero(l: list): """...
...         | ...
```

**用途**:
- 查看每个题号对应的完整题目
- 理解题目要求
- 验证题目分配是否正确

## 📈 总览统计 (`overview.csv`)

包含每个任务类型的统计信息：

| 字段 | 说明 |
|------|------|
| task_type | 任务类型 |
| total_samples | 总样本数 |
| num_models | 模型数量 |
| num_questions | 题目数量 |
| avg_response_length | 平均回答长度 |
| avg_throughput | 平均吞吐量 |
| avg_latency | 平均延迟 |
| avg_energy | 平均能耗 |

## 🔍 使用示例

### 1. 查看代码生成任务的回答对比

```python
import pandas as pd

# 读取回答矩阵
responses = pd.read_csv('code/code_responses.csv', 
                       encoding='utf-8-sig', 
                       index_col=0)

# 查看所有模型在第一题的回答
print(responses['q01'])

# 查看 deepseek 模型在所有题目的回答
print(responses.loc['deepseek_8b_ol_q4km'])

# 对比两个模型在第一题的回答
print("DeepSeek 回答:")
print(responses.loc['deepseek_8b_ol_q4km', 'q01'])
print("\nQwen 回答:")
print(responses.loc['qwen_8b_ol_q4km', 'q01'])
```

### 2. 分析性能指标

```python
import pandas as pd
import matplotlib.pyplot as plt

# 读取能耗矩阵
energy = pd.read_csv('code/code_gpu_energy_j.csv', 
                    encoding='utf-8-sig', 
                    index_col=0)

# 计算每个模型的平均能耗
avg_energy = energy.mean(axis=1).sort_values()
print("平均能耗排名（从低到高）:")
print(avg_energy)

# 可视化
avg_energy.plot(kind='barh', figsize=(10, 6))
plt.xlabel('平均 GPU 能耗 (焦耳)')
plt.title('代码生成任务 - 模型能耗对比')
plt.tight_layout()
plt.savefig('code_energy_comparison.png', dpi=300)
```

### 3. 查看题目内容

```python
import pandas as pd

# 读取题目参考
prompts = pd.read_csv('code/code_prompts.csv', 
                     encoding='utf-8-sig')

# 查看所有题目
for idx, row in prompts.iterrows():
    print(f"\n{row['question_id']}:")
    print(row['prompt'][:200] + "...")  # 显示前200字符
```

### 4. 综合分析

```python
import pandas as pd

# 读取多个指标
responses = pd.read_csv('code/code_responses.csv', encoding='utf-8-sig', index_col=0)
energy = pd.read_csv('code/code_gpu_energy_j.csv', encoding='utf-8-sig', index_col=0)
latency = pd.read_csv('code/code_latency_s.csv', encoding='utf-8-sig', index_col=0)

# 计算综合指标
summary = pd.DataFrame({
    'avg_response_length': responses.applymap(lambda x: len(str(x)) if pd.notna(x) else 0).mean(axis=1),
    'avg_energy': energy.mean(axis=1),
    'avg_latency': latency.mean(axis=1)
})

# 计算能效比（字符数/能耗）
summary['efficiency'] = summary['avg_response_length'] / summary['avg_energy']

# 排序
summary = summary.sort_values('efficiency', ascending=False)
print("能效比排名（从高到低）:")
print(summary)
```

## 📊 任务类型统计

| 任务类型 | 样本数 | 模型数 | 题目数 | 平均回答长度 |
|---------|--------|--------|--------|-------------|
| code | 60 | 12 | 5 | 2053 字符 |
| creative | 56 | 12 | 5 | 420 字符 |
| math | 55 | 11 | 5 | 861 字符 |
| multi_turn | 55 | 11 | 5 | 417 字符 |
| qa | 55 | 11 | 5 | 900 字符 |
| reasoning | 55 | 11 | 5 | 453 字符 |
| summary | 55 | 11 | 5 | 253 字符 |
| translation | 55 | 11 | 5 | 836 字符 |

## ⚠️ 注意事项

1. **空值处理**: 部分单元格可能为空（NaN），表示该模型在该题目上没有回答或回答失败
2. **样本不均衡**: qwen25_7b_hf_8bit 模型的样本数较少（6个），在某些任务中可能缺失
3. **回答长度**: 代码生成任务的回答通常较长（平均 2000+ 字符），其他任务较短
4. **编码格式**: 所有文件使用 UTF-8-BOM 编码，确保中文正常显示

## 🔄 重新生成

如果需要重新生成对比矩阵：

```bash
conda activate bartscore
set PYTHONUTF8=1
python data/analize/scripts/create_comparison_matrix.py
```

## 📚 相关文档

- **原始数据**: `../responses_raw.csv`
- **数据说明**: `../README.md`
- **分析设计**: `../../scripts/analysis_design.md`
- **质量评估**: `../../scripts/quality_evaluation_system.md`

---

**更新时间**: 2026-03-04  
**版本**: v1.0  
**生成脚本**: `create_comparison_matrix.py`
