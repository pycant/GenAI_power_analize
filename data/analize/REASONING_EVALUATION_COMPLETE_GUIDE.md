# 逻辑推理任务评估完整指南

## 概述

本指南提供了逻辑推理任务评估的完整流程，包括人工评分和自动化评估两部分。

## 快速开始

### 1. 人工评分（推荐先完成）

#### 步骤1: 准备工作
```bash
# 打开打分表
notepad data\analize\REASONING_MANUAL_SCORING_RUBRIC.md

# 或使用你喜欢的编辑器
code data\analize\REASONING_MANUAL_SCORING_RUBRIC.md
```

#### 步骤2: 查看模型响应
```bash
# 激活环境
conda activate bartscore

# 列出所有模型
python data\analize\scripts\view_reasoning_responses.py --list-models

# 列出所有问题
python data\analize\scripts\view_reasoning_responses.py --list-questions

# 查看特定模型对特定问题的响应
python data\analize\scripts\view_reasoning_responses.py --model qwen_8b_ol_q4km --question q01

# 查看所有模型对某个问题的响应（逐个显示）
python data\analize\scripts\view_reasoning_responses.py --question q02

# 查看某个模型对所有问题的响应（逐个显示）
python data\analize\scripts\view_reasoning_responses.py --model gemma_4b_ol_q4km
```

#### 步骤3: 进行评分

在打分表中填写评分，每个维度1-5分：

| 维度 | 权重 | 说明 |
|------|------|------|
| 结论正确性 | 40% | 最终答案是否正确 |
| 推理完整性 | 25% | 是否包含完整的推理过程 |
| 逻辑严谨性 | 20% | 推理是否严密、无矛盾 |
| 表达清晰度 | 10% | 表达是否清晰易懂 |
| 推理效率 | 5% | 是否简洁、无冗余 |

**评分技巧**：
- 先完成一个问题的所有模型评分（保持标准一致）
- 每个维度独立评分
- 在备注栏记录特殊情况
- 定期休息，避免疲劳

#### 步骤4: 聚合评分结果
```bash
# 评分完成后，运行聚合脚本
python data\analize\scripts\aggregate_manual_scores.py
```

**输出文件**：
- `manual_scores.csv` - 详细评分数据
- `manual_scores_summary.csv` - 模型汇总统计
- `manual_scores_by_question.csv` - 问题难度分析
- `manual_scores_report.md` - 完整评估报告

### 2. 自动化评估（可并行进行）

```bash
# 激活环境
conda activate bartscore

# 运行自动化评估
python data\analize\scripts\evaluate_reasoning_quality.py
```

**输出文件**：
- `reasoning_quality_scores.csv` - 详细评分
- `reasoning_quality_report.md` - 评估报告
- `reasoning_quality_summary.csv` - 统计摘要

### 3. 对比分析（人工评分完成后）

创建对比分析脚本来比较人工评分和自动化评分的结果。

## 评估指标说明

### 人工评分指标

#### 1. 结论正确性 (Correctness) - 40%
- 5分: 完全正确，与标准答案一致
- 4分: 基本正确，表述略有偏差
- 3分: 部分正确，方向对但不够准确
- 2分: 基本错误，但推理有部分合理
- 1分: 完全错误

#### 2. 推理完整性 (Completeness) - 25%
- 5分: 包含前提、推理步骤、结论，非常完整
- 4分: 基本完整，略有跳跃
- 3分: 有推理但缺少前提或结论
- 2分: 推理简略，缺少关键步骤
- 1分: 几乎没有推理过程

#### 3. 逻辑严谨性 (Rigor) - 20%
- 5分: 逻辑严密，无矛盾，每步有依据
- 4分: 基本严谨，偶有小跳跃
- 3分: 大致合理但有逻辑漏洞
- 2分: 存在明显逻辑错误
- 1分: 推理混乱，严重错误

#### 4. 表达清晰度 (Clarity) - 10%
- 5分: 表达清晰，结构分明
- 4分: 表达清楚，偶有不精确
- 3分: 能理解但略显混乱
- 2分: 表达混乱，难以理解
- 1分: 极其混乱，无法理解

#### 5. 推理效率 (Efficiency) - 5%
- 5分: 直击要点，简洁无冗余
- 4分: 基本简洁，略有冗余
- 3分: 适中，有一定冗余
- 2分: 冗长，大量无关信息
- 1分: 极其冗长，大量重复

### 自动化评估指标

#### 1. 结论正确性检测
- 精确匹配
- 模糊匹配（相似度阈值）
- 关键词匹配

#### 2. 推理完整性评分
- 前提识别
- 推理步骤识别
- 结论识别
- 结构完整性

#### 3. 逻辑严谨性评分
- 逻辑连接词使用
- 矛盾检测
- 推理链连贯性

#### 4. 推理深度分析
- 推理步骤数量
- 推理复杂度
- 论证深度

#### 5. 关键词覆盖率
- 标准答案关键词覆盖
- 推理类型相关词汇

## 文件结构

```
data/analize/
├── scripts/
│   ├── REASONING_EVALUATION_DESIGN.md          # 评估设计文档
│   ├── reasoning_config.py                      # 配置文件
│   ├── evaluate_reasoning_quality.py            # 自动化评估脚本
│   ├── view_reasoning_responses.py              # 响应查看工具 ⭐
│   ├── aggregate_manual_scores.py               # 人工评分聚合脚本 ⭐
│   └── quality_evaluation/
│       └── reasoning_evaluator.py               # 评估器实现
├── pre_data/
│   └── comparison_matrices/
│       └── reasoning/
│           └── reasoning_responses.csv          # 模型响应数据
├── REASONING_EVALUATION_DESIGN.md               # 设计文档
├── REASONING_EVALUATION_QUICK_REFERENCE.md      # 快速参考
├── REASONING_MANUAL_SCORING_RUBRIC.md           # 人工评分打分表 ⭐
├── REASONING_EVALUATION_STATUS.md               # 当前状态说明 ⭐
├── REASONING_EVALUATION_COMPLETE_GUIDE.md       # 完整指南（本文件）⭐
└── results/
    └── reasoning_quality/                       # 评估结果输出目录
        ├── reasoning_quality_scores.csv         # 自动化评分
        ├── reasoning_quality_report.md          # 自动化报告
        ├── reasoning_quality_summary.csv        # 自动化摘要
        ├── manual_scores.csv                    # 人工评分
        ├── manual_scores_summary.csv            # 人工评分汇总
        ├── manual_scores_by_question.csv        # 问题分析
        └── manual_scores_report.md              # 人工评分报告
```

## 评估流程建议

### 方案A: 先人工后自动（推荐）

1. **人工评分** (5-9小时)
   - 使用`view_reasoning_responses.py`查看响应
   - 在打分表中填写评分
   - 运行`aggregate_manual_scores.py`生成报告

2. **自动化评估** (5-10分钟)
   - 运行`evaluate_reasoning_quality.py`
   - 查看自动化评估报告

3. **对比分析**
   - 比较人工和自动化评分的一致性
   - 分析差异原因
   - 改进自动化评估方法

### 方案B: 并行进行

1. **同时启动**
   - 运行自动化评估（快速完成）
   - 开始人工评分（耗时较长）

2. **先看自动化结果**
   - 了解模型的基本表现
   - 识别明显的优劣势

3. **完成人工评分**
   - 参考自动化结果但保持独立判断
   - 聚合人工评分

4. **综合分析**
   - 对比两种评估方法
   - 生成最终报告

## 常见问题

### Q1: 人工评分需要多长时间？
A: 预计5-9小时，可分多次完成。每个模型-问题组合约5-10分钟。

### Q2: 如何确保评分的一致性？
A: 
- 先完成一个问题的所有模型评分
- 建立"锚点"案例（如典型的5分、3分、1分案例）
- 定期回顾已评分的案例
- 在备注栏记录评分理由

### Q3: 评分时遇到不确定的情况怎么办？
A: 
- 在备注栏记录不确定的原因
- 标记为"待讨论"
- 可以先给一个初步分数，后续调整
- 如有多位评分者，可以讨论达成共识

### Q4: 自动化评估和人工评分哪个更重要？
A: 两者互补：
- 自动化评估：客观、快速、可重复
- 人工评分：深度、准确、有洞察力
- 建议两者结合使用

### Q5: 如何处理评分数据？
A: 
- 人工评分：使用`aggregate_manual_scores.py`聚合
- 自动化评估：直接查看生成的报告
- 对比分析：创建自定义分析脚本

### Q6: 评分表格式错误怎么办？
A: 
- 确保表格格式正确（Markdown表格）
- 每个单元格只填写数字（1-5）
- 备注栏可以填写文字
- 如果聚合脚本报错，检查是否有空行或格式问题

### Q7: 可以修改评分维度权重吗？
A: 可以，在`aggregate_manual_scores.py`中修改`DIMENSION_WEIGHTS`字典。

### Q8: 如何添加新的评分维度？
A: 需要修改：
1. 打分表的表格结构
2. `aggregate_manual_scores.py`中的解析逻辑
3. 权重配置

## 工具使用示例

### 查看响应工具

```bash
# 查看所有可用模型
python data\analize\scripts\view_reasoning_responses.py --list-models

# 输出:
# 可用模型列表:
# 1. deepseek_8b_ol_q4km
# 2. gemma_2b_hf_4bit
# ...

# 查看所有问题
python data\analize\scripts\view_reasoning_responses.py --list-questions

# 输出:
# 可用问题列表:
# q01: 三个盒子逻辑谜题
#    类型: 逻辑推理
# q02: 三段论演绎推理
#    类型: 演绎推理
# ...

# 查看特定响应
python data\analize\scripts\view_reasoning_responses.py --model qwen_8b_ol_q4km --question q01

# 输出:
# ================================================================================
# 问题 q01: 三个盒子逻辑谜题
# --------------------------------------------------------------------------------
# 问题内容:
# 有三个盒子，一个装有两个金币...
# --------------------------------------------------------------------------------
# 标准答案: 从标签"一金一银"的盒子中取硬币
# 推理类型: 逻辑推理
# ================================================================================
#
# 模型: qwen_8b_ol_q4km
# --------------------------------------------------------------------------------
# 响应内容:
# 嗯，这个问题看起来有点挑战性...
# ================================================================================
```

### 聚合评分工具

```bash
# 运行聚合脚本
python data\analize\scripts\aggregate_manual_scores.py

# 输出:
# ================================================================================
# 逻辑推理任务人工评分聚合工具
# ================================================================================
#
# 读取打分表: data\analize\REASONING_MANUAL_SCORING_RUBRIC.md
# ✓ 成功解析 55 条评分记录
#   - 模型数: 11
#   - 问题数: 5
#
# 计算加权分数...
# ✓ 加权分数计算完成
#
# 生成汇总统计...
# ✓ 汇总统计生成完成
#
# 保存结果文件...
# ✓ 详细评分已保存: manual_scores.csv
# ✓ 模型汇总已保存: manual_scores_summary.csv
# ✓ 问题分析已保存: manual_scores_by_question.csv
#
# 生成Markdown报告...
# ✓ 报告已生成: manual_scores_report.md
#
# ================================================================================
# Top 3 模型 (按归一化分数排序)
# ================================================================================
# 1. qwen_8b_ol_q4km: 85.60
# 2. qwen25_7b_hf_4bit: 82.40
# 3. deepseek_8b_ol_q4km: 78.20
#
# ================================================================================
# 聚合完成!
# ================================================================================
```

## 下一步计划

### 短期（评分完成后）
1. 完成人工评分
2. 运行聚合脚本
3. 查看评估报告
4. 识别模型优劣势

### 中期（分析阶段）
1. 创建可视化脚本
   - 模型性能雷达图
   - 问题难度分析图
   - 自动vs人工评分对比图
2. 进行深度分析
   - 模型在不同推理类型上的表现
   - 评分维度之间的相关性
   - 自动化评估的准确性

### 长期（改进阶段）
1. 改进自动化评估方法
2. 扩展评估数据集
3. 开发更多评估工具
4. 撰写学术论文

## 参考资料

- **设计文档**: `REASONING_EVALUATION_DESIGN.md`
- **快速参考**: `REASONING_EVALUATION_QUICK_REFERENCE.md`
- **当前状态**: `REASONING_EVALUATION_STATUS.md`
- **配置文件**: `scripts/reasoning_config.py`
- **评估器代码**: `scripts/quality_evaluation/reasoning_evaluator.py`

## 联系与支持

如有问题或需要帮助，请查阅相关文档或联系项目维护者。

---

**最后更新**: 2026-03-05
**版本**: v1.0
**状态**: 准备就绪，可以开始评分
