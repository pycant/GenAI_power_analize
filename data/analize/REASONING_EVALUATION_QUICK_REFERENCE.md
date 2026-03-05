# 逻辑推理评估快速参考

## 快速开始

```bash
# 1. 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 2. 运行评估（基础指标）
cd data/analize/scripts
python evaluate_reasoning_quality.py

# 3. 查看结果
type ..\results\reasoning_quality\reasoning_quality_report.md
```

## 评估指标

### 核心指标（必须）

| 指标 | 含义 | 范围 | 优秀标准 |
|------|------|------|----------|
| **结论正确性** | 最终答案正确性 | [0, 1] | ≥0.8 |
| **推理完整性** | 包含前提/步骤/结论 | [0, 1] | ≥0.8 |
| **逻辑连贯性** | 推理步骤连贯性 | [0, 1] | ≥0.7 |
| **推理深度** | 推理复杂度 | [0, 1] | ≥0.6 |

### 辅助指标（可选）

| 指标 | 含义 | 说明 |
|------|------|------|
| **关键词覆盖** | 问题相关性 | 检测是否切题 |
| **答案提取置信度** | 答案明确性 | 辅助答案提取 |
| **LLM-as-Judge** | 深度评估 | 需要API，成本高 |

## 命令选项

```bash
# 基础评估（推荐）
python evaluate_reasoning_quality.py

# 高级评估（包含LLM-as-Judge，需要API）
python evaluate_reasoning_quality.py --use-llm-judge

# 自定义路径
python evaluate_reasoning_quality.py \
  --data-dir path/to/data \
  --output-dir path/to/output
```

## 输出文件

```
data/analize/results/reasoning_quality/
├── reasoning_quality_scores.csv       # 详细评分
├── reasoning_quality_summary.csv      # 汇总统计
└── reasoning_quality_report.md        # 评估报告
```

## 性能估算

基于 RTX 4060 8GB：

| 配置 | 评估时间 | 成本 |
|------|----------|------|
| 基础指标 | ~30秒-1分钟 | 免费 |
| 包含LLM-as-Judge | ~5-10分钟 | ~$0.01-0.05/评估 |

## 指标解释

### 结论正确性
- **1.0**: 完全正确 ✅
- **0.0**: 完全错误 ❌

### 推理完整性
- **0.8-1.0**: 推理完整，结构清晰 ✅
- **0.6-0.8**: 推理较完整 ⚠️
- **0.0-0.6**: 推理不完整，缺少关键步骤 ❌

### 逻辑连贯性
- **0.7-1.0**: 逻辑连贯，流畅 ✅
- **0.5-0.7**: 基本连贯 ⚠️
- **0.0-0.5**: 逻辑跳跃，不连贯 ❌

## 推理类型

| 类型 | 说明 | 示例问题 |
|------|------|----------|
| **logic_puzzle** | 逻辑谜题 | q01, q03 |
| **deductive** | 演绎推理 | q02, q04 |
| **game_theory** | 博弈论 | q05 |

## 常见问题

### Q: 如何提高结论正确性？
A: 确保模型输出包含明确的答案标记（"答案是"、"因此"等）

### Q: 推理完整性低怎么办？
A: 检查模型是否包含前提、推理步骤和结论三个部分

### Q: 如何使用LLM-as-Judge？
A: 需要配置OpenAI API密钥，使用 `--use-llm-judge` 参数

### Q: 评估速度慢？
A: 不使用 `--use-llm-judge`，基础指标评估很快（~1分钟）

## 数据配置

标准答案和推理类型在 `reasoning_config.py` 中配置：

```python
REASONING_REFERENCE_ANSWERS = {
    'q01': {
        'answer': '从标签"一金一银"的盒子中取硬币',
        'reasoning_type': 'logic_puzzle'
    },
    # ...
}
```

## 下一步

1. ✅ 运行评估获取基础数据
2. ⏳ 分析评估报告，识别优秀模型
3. ⏳ 按推理类型分析模型表现
4. ⏳ 创建可视化图表
5. ⏳ 整合到综合评估体系

## 相关文档

- 设计文档: `REASONING_EVALUATION_DESIGN.md`
- 系统概览: `quality_evaluation_system.md`
- QA评估参考: `QA_EVALUATION_DESIGN.md`
- 数学评估参考: `MATH_EVALUATION_DESIGN.md`
