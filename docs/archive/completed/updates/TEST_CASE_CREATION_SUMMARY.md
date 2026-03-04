# 测试用例创建总结

## 创建日期
2026-03-02

## 已创建的文档和资源

### 1. 测试用例设计指南
**文件**: `docs/experiment/TEST_CASE_DESIGN_GUIDE.md`

**内容概览**:
- ✅ 主流 LLM 评估基准参考（MMLU, GSM8K, HumanEval, FLORES-200, WMT）
- ✅ 8 种任务类型详细设计（知识问答、数学、代码、翻译、摘要、创意、多轮对话、上下文检验）
- ✅ 翻译任务完整设计方案（英→中、中→英、专业领域）
- ✅ 测试用例最佳实践（难度分层、温度设置、重复策略）
- ✅ 评估指标选择指南
- ✅ 推荐测试集配置（最小/标准/扩展）

### 2. 示例测试用例文件
**文件**: `data/test/test_cases_with_translation.json`

**包含的测试用例**:
1. **知识问答** (qa_001): 光合作用问题
2. **数学计算** (math_001): 长方形面积和周长
3. **代码生成** (code_001): 回文判断函数
4. **英译中** (trans_en_zh_001): AI 通用翻译
5. **英译中** (trans_en_zh_002): 机器学习技术翻译
6. **中译英** (trans_zh_en_001): 天气日常翻译
7. **中译英** (trans_zh_en_002): 深度学习技术翻译
8. **技术翻译** (trans_en_zh_tech_001): CNN 专业术语翻译
9. **文本摘要** (summary_001): AI 芯片新闻摘要
10. **创意写作** (creative_001): 科幻故事续写
11. **多轮对话** (multi_turn_001): 机器学习概念讨论

**总计**: 11 个测试用例，覆盖 7 种任务类型

## 翻译任务设计亮点

### 为什么添加翻译任务？

1. **多语言能力评估**: 测试模型的跨语言理解和生成能力
2. **实用性强**: 翻译是 LLM 最常见的实际应用之一
3. **客观评估**: 有成熟的自动评估指标（BLEU, chrF++, COMET）
4. **能效对比明显**: 不同模型在翻译任务上的资源消耗差异显著
5. **标准化基准**: 可参考 FLORES-200 和 WMT 等国际标准

### 翻译任务配置

#### 语言对
- **英→中** (en_to_zh): 8 个测试用例
- **中→英** (zh_to_en): 8 个测试用例

#### 难度分层
- **简单** (30%): 日常对话、简单句式
- **中等** (50%): 新闻、科技文本
- **困难** (20%): 学术、专业术语

#### 领域覆盖
- 通用领域（日常对话）
- 科技领域（AI、机器学习）
- 技术领域（专业术语）

### 翻译评估指标

#### 自动评估
1. **BLEU**: n-gram 重叠度（0-100）
2. **chrF++**: 字符级 F-score（对中文友好）
3. **COMET**: 神经网络评估（与人工评估相关性最高）
4. **BERTScore**: 语义相似度（适合意译）

#### 人工评估维度
1. **准确性**: 是否忠实原文
2. **流畅度**: 译文是否自然
3. **术语一致性**: 专业术语是否准确

## 参考的研究和基准

### 主流评估基准

| 基准 | 规模 | 任务类型 | 参考价值 |
|------|------|---------|---------|
| **MMLU** | 16,000+ 题 | 知识问答 | 难度分层、多领域覆盖 |
| **GSM8K** | 8,500 题 | 数学推理 | 多步骤推理、过程评估 |
| **HumanEval** | 164 题 | 代码生成 | 自动化测试、客观评估 |
| **FLORES-200** | 200 语言 | 机器翻译 | 标准化翻译测试集 |
| **WMT** | 年度竞赛 | 机器翻译 | 人工评估黄金标准 |

### 关键研究发现

1. **多样性很重要**: 覆盖不同难度、领域、任务类型
2. **少样本学习**: 5-shot 评估比 0-shot 更稳定
3. **自动化评估**: 结合客观指标和主观指标
4. **上下文长度**: 测试不同输入长度的影响
5. **温度参数**: 确定性任务用 0.0，创意任务用 0.7-0.9

## 测试用例最佳实践

### 1. 难度分层原则（30-50-20）
- 简单题（30%）: 验证基础能力
- 中等题（50%）: 评估实际应用能力
- 困难题（20%）: 测试边界情况

### 2. 温度参数设置

| 任务类型 | 温度 | 重复次数 | 原因 |
|---------|------|---------|------|
| 知识问答 | 0.0 | 1 | 需要确定性答案 |
| 数学计算 | 0.0 | 1 | 唯一正确答案 |
| 代码生成 | 0.1 | 3 | 轻微随机性 |
| 翻译 | 0.1-0.2 | 3 | 允许轻微变化 |
| 文本摘要 | 0.7 | 5 | 需要创造性 |
| 创意写作 | 0.8-0.9 | 5-10 | 鼓励多样性 |

### 3. 推荐测试集配置

#### 最小测试集（快速验证）
- 知识问答: 10 题
- 数学计算: 5 题
- 代码生成: 5 题
- 翻译: 8 题（英→中 4，中→英 4）
- 文本摘要: 3 题
- **总计**: 31 题，预计 30-60 分钟

#### 标准测试集（完整评估）
- 知识问答: 20 题
- 数学计算: 15 题
- 代码生成: 12 题
- 翻译: 32 题（英→中 16，中→英 16）
- 逻辑推理: 10 题
- 文本摘要: 8 题
- 创意写作: 8 题
- 多轮对话: 8 组
- **总计**: 113 题，预计 3-5 小时

#### 扩展测试集（深度分析）
- 标准测试集 + 上下文检验 + 专业翻译 + 长文本
- **总计**: 144 题，预计 5-8 小时

## 如何使用这些资源

### 步骤 1：阅读设计指南
```bash
# 查看完整的设计指南
cat docs/experiment/TEST_CASE_DESIGN_GUIDE.md
```

### 步骤 2：查看示例测试用例
```bash
# 查看示例测试用例
cat data/test/test_cases_with_translation.json
```

### 步骤 3：运行示例测试
```bash
# 使用示例测试用例运行实验
python experiments/experiment_runner.py \
  --test-cases data/test/test_cases_with_translation.json \
  --output-dir data/experiments_5
```

### 步骤 4：创建自定义测试用例

基于设计指南和示例，创建你自己的测试用例文件：

```json
{
  "id": "your_test_id",
  "task_type": "translation",  // 或其他任务类型
  "difficulty": "medium",
  "prompts": ["你的测试提示"],
  "config": {
    "model": "Ollama:qwen3:4b",
    "temperature": 0.2,
    "max_tokens": 200
  }
}
```

### 步骤 5：扩展测试集

根据你的研究需求，参考以下来源扩展测试集：

1. **FLORES-200**: [GitHub](https://github.com/openlanguagedata/flores)
2. **WMT 测试集**: [官网](https://www.statmt.org/wmt24/)
3. **MMLU**: [GitHub](https://github.com/hendrycks/test)
4. **GSM8K**: [GitHub](https://github.com/openai/grade-school-math)
5. **HumanEval**: [GitHub](https://github.com/openai/human-eval)

## 翻译评估工具安装

如果需要使用翻译评估指标，安装以下工具：

```bash
# BLEU 和 chrF++
pip install sacrebleu

# COMET（需要额外模型）
pip install unbabel-comet

# BERTScore
pip install bert-score
```

### 使用示例

```python
# BLEU 评估
from sacrebleu import corpus_bleu
bleu = corpus_bleu([hypothesis], [[reference]])
print(f"BLEU: {bleu.score:.2f}")

# BERTScore 评估
from bert_score import score
P, R, F1 = score([hypothesis], [reference], lang='zh')
print(f"BERTScore F1: {F1.mean():.4f}")
```

## 下一步建议

### 短期（1-2 天）
1. ✅ 使用示例测试用例运行快速实验
2. ✅ 验证数据收集和分析流程
3. ✅ 熟悉各种任务类型的评估方法

### 中期（1 周）
1. 扩展测试用例到标准测试集（113 题）
2. 添加更多翻译测试用例（参考 FLORES-200）
3. 实现翻译自动评估指标（BLEU, chrF++）
4. 对比不同模型在翻译任务上的表现

### 长期（2-4 周）
1. 创建完整的扩展测试集（144 题）
2. 实现所有评估指标（包括 COMET）
3. 进行多模型全面对比实验
4. 撰写实验报告和论文

## 相关文档

- [实验设计文档](experiment_design.md) - 完整实验方法论
- [测试用例设计指南](TEST_CASE_DESIGN_GUIDE.md) - 详细设计指南
- [实验操作指南](experiment_operation_guide.md) - 操作步骤
- [下一步行动指南](../../NEXT_STEPS.md) - 行动路径

## 参考资源

### 学术论文
1. Hendrycks et al. (2021). "Measuring Massive Multitask Language Understanding"
2. Cobbe et al. (2021). "Training Verifiers to Solve Math Word Problems"
3. Chen et al. (2021). "Evaluating Large Language Models Trained on Code"
4. NLLB Team (2022). "No Language Left Behind: Scaling Human-Centered Machine Translation"
5. Freitag et al. (2022). "Results of WMT22 Metrics Shared Task"

### 在线资源
- [FLORES-200 数据集](https://github.com/openlanguagedata/flores)
- [WMT 竞赛](https://www.statmt.org/wmt24/)
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [Papers with Code - Translation](https://paperswithcode.com/task/machine-translation)

## 总结

✅ **已完成**:
1. 创建了全面的测试用例设计指南
2. 提供了 11 个示例测试用例（包含翻译任务）
3. 整合了主流评估基准的最佳实践
4. 设计了三个级别的测试集配置

🎯 **核心价值**:
- **翻译任务**: 新增了重要的多语言评估维度
- **标准化**: 参考国际主流基准（FLORES-200, WMT）
- **实用性**: 所有测试用例都可直接运行
- **可扩展**: 提供了清晰的扩展路径

🚀 **准备就绪**: 你现在可以开始设计和运行你的大语言模型能效评估实验了！

---

**文档版本**: 1.0  
**创建日期**: 2026-03-02  
**维护者**: 项目团队
