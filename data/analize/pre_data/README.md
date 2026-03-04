# 预处理数据说明

## 数据提取完成情况

✅ **提取时间**: 2026-03-04  
✅ **数据来源**: 12 个模型的实验结果  
✅ **总样本数**: 446 条回答数据  
✅ **任务类型**: 8 种（code, creative, math, multi_turn, qa, reasoning, summary, translation）

## 文件说明

### 1. responses_raw.csv（原始数据）

**用途**: 包含所有模型的原始回答数据和性能指标

**字段说明**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| experiment_id | string | 实验唯一标识符 |
| model | string | 模型名称（如 deepseek_8b_ol_q4km） |
| task_type | string | 任务类型（code/creative/math/qa等） |
| timestamp | string | 实验时间戳 |
| prompt | string | 输入提示词（可能包含换行符） |
| response | string | 模型生成的回答（可能包含换行符） |
| response_length | int | 回答字符长度 |
| token_count | int | 生成的 token 数量 |
| throughput_tps | float | 吞吐量（tokens/秒） |
| latency_s | float | 总延迟（秒） |
| gpu_energy_j | float | GPU 能耗（焦耳） |
| gpu_power_avg_w | float | GPU 平均功耗（瓦特） |
| bartscore | float/null | BARTScore 质量得分（如果有） |
| has_reference | bool | 是否有参考答案 |
| temperature | float | 生成温度参数 |
| max_tokens | int | 最大 token 限制 |

**数据格式**: CSV with UTF-8-BOM encoding  
**特殊字符处理**: CSV 自动转义换行符、引号等特殊字符  
**文件大小**: ~191 KB

**使用示例**:
```python
import pandas as pd

# 读取数据
df = pd.read_csv('responses_raw.csv', encoding='utf-8-sig')

# 查看特定模型的回答
deepseek_responses = df[df['model'] == 'deepseek_8b_ol_q4km']

# 查看特定任务类型
code_responses = df[df['task_type'] == 'code']

# 访问包含换行符的回答
print(df.loc[0, 'response'])  # 自动处理换行符
```

### 2. responses_summary.csv

**用途**: 按模型和任务类型的统计摘要

**字段说明**:

| 字段名 | 说明 |
|--------|------|
| model | 模型名称 |
| task_type | 任务类型 |
| sample_count | 样本数量 |
| response_length_mean/std/min/max | 回答长度统计 |
| token_count_mean/std | Token 数量统计 |
| throughput_tps_mean/std | 吞吐量统计 |
| latency_s_mean/std | 延迟统计 |
| gpu_energy_j_mean/std | GPU 能耗统计 |
| gpu_power_avg_w_mean/std | GPU 功耗统计 |

**文件大小**: ~20 KB

### 3. comparison_matrices/（对比矩阵目录）

**用途**: 按任务类型组织的模型回答对比矩阵，方便横向对比

**目录结构**:
```
comparison_matrices/
├── overview.csv              # 总览统计
├── code/                     # 代码生成任务
│   ├── code_responses.csv    # 回答对比（行=模型，列=题号）
│   ├── code_prompts.csv      # 题目参考
│   ├── code_throughput_tps.csv  # 吞吐量对比
│   ├── code_latency_s.csv    # 延迟对比
│   ├── code_gpu_energy_j.csv # 能耗对比
│   └── ...                   # 其他指标
├── creative/                 # 创意写作任务
├── math/                     # 数学推理任务
└── ...                       # 其他任务类型
```

**矩阵格式**:
- **行**: 模型名称（如 deepseek_8b_ol_q4km）
- **列**: 题号（q01, q02, q03, ...）
- **单元格**: 完整回答文本或性能指标值

**使用示例**:
```python
import pandas as pd

# 读取代码生成任务的回答对比
responses = pd.read_csv('comparison_matrices/code/code_responses.csv', 
                       encoding='utf-8-sig', index_col=0)

# 查看所有模型在第一题的回答
print(responses['q01'])

# 对比两个模型
print("DeepSeek:", responses.loc['deepseek_8b_ol_q4km', 'q01'][:200])
print("Qwen:", responses.loc['qwen_8b_ol_q4km', 'q01'][:200])

# 读取能耗对比
energy = pd.read_csv('comparison_matrices/code/code_gpu_energy_j.csv',
                    encoding='utf-8-sig', index_col=0)
print("平均能耗:", energy.mean(axis=1).sort_values())
```

**详细说明**: 参见 `comparison_matrices/README.md`

**文件大小**: ~2 MB（所有任务类型）

## 模型覆盖情况

| 模型名称 | 参数量 | 量化方式 | 框架 | 样本数 |
|---------|--------|---------|------|--------|
| deepseek_8b_ol_q4km | 8B | Q4_K_M | Ollama | 40 |
| gemma_2b_hf_4bit | 2B | 4bit | HuggingFace | 40 |
| gemma_2b_hf_8bit | 2B | 8bit | HuggingFace | 40 |
| gemma_4b_ol_q4km | 4B | Q4_K_M | Ollama | 40 |
| phi3_4b_hf_4bit | 4B | 4bit | HuggingFace | 40 |
| phi3_4b_hf_8bit | 4B | 8bit | HuggingFace | 40 |
| qwen_4b_ol_q4km | 4B | Q4_K_M | Ollama | 40 |
| qwen_8b_ol_q4km | 8B | Q4_K_M | Ollama | 40 |
| qwen25_3b_hf_4bit | 3B | 4bit | HuggingFace | 40 |
| qwen25_3b_hf_8bit | 3B | 8bit | HuggingFace | 40 |
| qwen25_7b_hf_4bit | 7B | 4bit | HuggingFace | 40 |
| qwen25_7b_hf_8bit | 7B | 8bit | HuggingFace | 6 |

**注意**: qwen25_7b_hf_8bit 只有 6 个样本（可能实验未完成）

## 任务类型分布

| 任务类型 | 说明 | 样本数（估算） |
|---------|------|---------------|
| code | 代码生成 | ~60 |
| creative | 创意写作 | ~60 |
| math | 数学推理 | ~60 |
| qa | 问答 | ~60 |
| reasoning | 推理 | ~60 |
| summary | 文本摘要 | ~60 |
| translation | 翻译 | ~60 |
| multi_turn | 多轮对话 | ~26 |

## 数据质量说明

### ✅ 优势
- **完整性**: 所有字段都已提取，无缺失关键信息
- **格式统一**: CSV 格式便于后续分析
- **编码正确**: UTF-8-BOM 确保中文正常显示
- **特殊字符处理**: CSV 自动转义，无需手动处理

### ⚠️ 注意事项
1. **回答文本可能很长**: 部分代码生成任务的回答超过 2000 字符
2. **换行符已保留**: 在 CSV 中以转义形式存储，读取时自动还原
3. **BARTScore 缺失**: 大部分样本的 bartscore 字段为空（需要后续质量评估）
4. **样本不均衡**: qwen25_7b_hf_8bit 样本数较少

## 下一步工作

### 1. 质量评估（优先级：高）
- [ ] 实现任务特定的质量评估器
- [ ] 计算多维度质量指标
- [ ] 生成 `quality_scores_detailed.csv`

### 2. 数据预处理（优先级：高）
- [ ] 合并性能指标和质量指标
- [ ] 计算派生指标（每 token 能耗等）
- [ ] 按任务分组归一化

### 3. 统计分析（优先级：中）
- [ ] 描述性统计
- [ ] 方差分析（ANOVA）
- [ ] 相关性分析

### 4. 可视化（优先级：中）
- [ ] 生成 10 张核心图表
- [ ] 任务-模型适配性热力图
- [ ] 帕累托前沿分析

### 5. 报告生成（优先级：低）
- [ ] 自动化 Markdown 报告
- [ ] 嵌入图表和数据表

## 脚本使用

### 重新提取数据
```bash
conda activate bartscore
set PYTHONUTF8=1
python data/analize/scripts/extract_responses.py
```

### 查看数据
```python
import pandas as pd

# 读取原始数据
df = pd.read_csv('data/analize/pre_data/responses_raw.csv', encoding='utf-8-sig')
print(df.info())
print(df.head())

# 读取统计摘要
summary = pd.read_csv('data/analize/pre_data/responses_summary.csv', encoding='utf-8-sig')
print(summary)
```

## 参考文档

- 分析设计: `data/analize/scripts/analysis_design.md`
- 质量评估: `data/analize/scripts/quality_evaluation_system.md`
- 使用说明: `data/analize/scripts/README_QUALITY_EVAL.md`

---

**更新时间**: 2026-03-04  
**数据版本**: v1.0  
**提取脚本**: `extract_responses.py`
