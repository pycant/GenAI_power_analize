# 文本摘要评估快速参考

## 快速开始

```bash
# 1. 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 2. 安装依赖
pip install rouge bert-score

# 3. 运行评估（推荐配置）
cd data/analize/scripts
python evaluate_summary_quality.py

# 4. 查看结果
type ..\results\summary_quality\summary_quality_report.md
```

## 评估指标

### 核心指标（必须）

| 指标 | 含义 | 范围 | 优秀标准 |
|------|------|------|----------|
| **ROUGE-L F1** | 结构完整性 | [0, 1] | ≥0.6 |
| **ROUGE-1 F1** | 词汇覆盖 | [0, 1] | ≥0.5 |
| **BERTScore F1** | 语义相似度 | [0, 1] | ≥0.8 |
| **压缩比** | 简洁性 | [0, 1] | 0.2-0.4 |
| **字数符合度** | 任务完成 | [0, 1] | =1.0 |

### 辅助指标（可选）

| 指标 | 含义 | 说明 |
|------|------|------|
| **信息密度** | 信息效率 | ROUGE-L召回率/压缩比，越高越好 |
| **BARTScore** | 深度评估 | 需要GPU，评估较慢 |

## 命令选项

```bash
# 基础评估（仅ROUGE）
python evaluate_summary_quality.py --no-bertscore

# 完整评估（ROUGE + BERTScore）
python evaluate_summary_quality.py

# 高级评估（包含BARTScore，需要GPU）
python evaluate_summary_quality.py --use-bartscore

# 自定义路径
python evaluate_summary_quality.py \
  --data-dir path/to/data \
  --output-dir path/to/output
```

## 输出文件

```
data/analize/results/summary_quality/
├── summary_quality_scores.csv       # 详细评分
├── summary_quality_summary.csv      # 汇总统计
└── summary_quality_report.md        # 评估报告
```

## 性能估算

基于 RTX 4060 8GB：

| 配置 | 评估时间 | 显存占用 |
|------|----------|----------|
| 仅ROUGE | ~30秒 | <1GB |
| ROUGE + BERTScore | ~2-5分钟 | ~2GB |
| 包含BARTScore | ~10-20分钟 | ~5GB |

## 指标解释

### ROUGE-L F1
- **0.6-1.0**: 信息保留完整，结构合理 ✅
- **0.4-0.6**: 信息保留中等 ⚠️
- **0.0-0.4**: 信息丢失严重 ❌

### BERTScore F1
- **0.8-1.0**: 语义高度相似 ✅
- **0.6-0.8**: 语义较相似 ⚠️
- **0.0-0.6**: 语义差异较大 ❌

### 压缩比
- **0.2-0.4**: 合理压缩 ✅
- **<0.2**: 过度压缩，可能丢失信息 ⚠️
- **>0.4**: 压缩不足，不够简洁 ⚠️

### 字数符合度
- **1.0**: 完全符合字数要求 ✅
- **<1.0**: 超出或不足字数要求 ❌

## 常见问题

### Q: ROUGE计算失败？
A: 确保安装了rouge包：`pip install rouge`

### Q: BERTScore很慢？
A: 首次运行需下载模型（~400MB），后续会使用缓存。可使用 `--no-bertscore` 跳过。

### Q: 显存不足？
A: 使用 `--no-bertscore` 禁用BERTScore，或不使用 `--use-bartscore`。

### Q: 如何只评估特定模型？
A: 修改 `summary_responses.csv`，只保留需要评估的模型行。

## 数据配置

原文和字数要求在 `summary_config.py` 中配置：

```python
SUMMARY_SOURCE_TEXTS = {
    'q01': "云计算原文...",
    'q02': "物联网原文...",
    # ...
}

SUMMARY_LENGTH_REQUIREMENTS = {
    'q01': {'min': 50, 'max': 70},
    'q02': {'min': 40, 'max': 60},
    # ...
}
```

## 下一步

1. ✅ 运行评估获取基础数据
2. ⏳ 分析评估报告，识别优秀模型
3. ⏳ 创建可视化图表（参考 `visualize_creative_quality.py`）
4. ⏳ 整合到综合评估体系

## 相关文档

- 设计文档: `SUMMARY_EVALUATION_DESIGN.md`
- 系统概览: `quality_evaluation_system.md`
- QA评估参考: `QA_EVALUATION_DESIGN.md`
- 创意写作参考: `CREATIVE_EVALUATION_DESIGN.md`
