# 测试用例设计指南

## 目录
1. [参考基准与研究](#参考基准与研究)
2. [任务类型设计](#任务类型设计)
3. [翻译任务设计](#翻译任务设计)
4. [测试用例最佳实践](#测试用例最佳实践)
5. [评估指标选择](#评估指标选择)

## 参考基准与研究

### 主流 LLM 评估基准

#### 1. MMLU (Massive Multitask Language Understanding)
- **来源**: [Hendrycks et al., 2021](https://arxiv.org/abs/2009.03300)
- **规模**: 16,000+ 多选题，涵盖 57 个学科
- **领域**: STEM、人文、社会科学、法律、医学等
- **评估方式**: 5-shot 多选题
- **适用场景**: 知识问答、推理能力评估
- **参考价值**: 题目难度分层、多领域覆盖

#### 2. GSM8K (Grade School Math 8K)
- **来源**: [Cobbe et al., 2021](https://arxiv.org/abs/2110.14168)
- **规模**: 8,500 道小学数学应用题
- **特点**: 多步骤算术推理
- **评估方式**: 生成式回答 + 答案验证
- **适用场景**: 数学计算、逻辑推理
- **参考价值**: 推理步骤完整性、中间过程评估

#### 3. HumanEval
- **来源**: [Chen et al., 2021](https://arxiv.org/abs/2107.03374)
- **规模**: 164 道编程问题
- **语言**: Python
- **评估方式**: 单元测试通过率 (pass@k)
- **适用场景**: 代码生成、编程能力
- **参考价值**: 自动化测试、客观评估

#### 4. FLORES-200 (翻译基准)
- **来源**: [NLLB Team, 2022](https://arxiv.org/abs/2207.04672)
- **规模**: 200 种语言，每种语言 1,012 个句子
- **特点**: 低资源语言、多语言对
- **评估方式**: BLEU、chrF++、COMET
- **适用场景**: 机器翻译质量评估
- **参考价值**: 标准化翻译测试集

#### 5. WMT (Workshop on Machine Translation)
- **来源**: 年度竞赛基准
- **特点**: 人工评估 + 自动指标
- **语言对**: 主流语言对（英-中、英-德等）
- **评估方式**: 人工排序 + BLEU/COMET
- **参考价值**: 翻译质量黄金标准

### 关键研究发现

1. **多样性很重要**: 覆盖不同难度、领域、任务类型
2. **少样本学习**: 5-shot 评估比 0-shot 更稳定
3. **自动化评估**: 结合客观指标（准确率）和主观指标（流畅度）
4. **上下文长度**: 测试不同输入长度对性能的影响
5. **温度参数**: 确定性任务用 0.0，创意任务用 0.7-0.9

## 任务类型设计

### 1. 知识问答 (QA)

#### 设计原则
- **难度分层**: 简单（30%）、中等（50%）、困难（20%）
- **领域覆盖**: 科学、历史、文化、常识
- **问题类型**: 事实性、概念性、多跳推理

#### 示例题目结构
```json
{
  "id": "qa_001",
  "task_type": "qa",
  "difficulty": "medium",
  "domain": "science",
  "question": "光合作用的主要产物是什么？",
  "expected_answer": "葡萄糖和氧气",
  "keywords": ["葡萄糖", "氧气", "糖", "O2"],
  "temperature": 0.0,
  "max_tokens": 100
}
```

#### 参考来源
- MMLU 科学类题目
- 中文百科知识
- 常识推理数据集

### 2. 数学计算 (Math)

#### 设计原则
- **步骤可验证**: 要求展示计算过程
- **难度递进**: 基础算术 → 代数 → 应用题
- **答案明确**: 有唯一正确答案

#### 示例题目结构
```json
{
  "id": "math_001",
  "task_type": "math",
  "difficulty": "medium",
  "question": "一个长方形的长是 12 米，宽是 8 米，求其面积和周长。",
  "expected_answer": {
    "area": 96,
    "perimeter": 40
  },
  "expected_steps": [
    "面积 = 长 × 宽 = 12 × 8 = 96 平方米",
    "周长 = 2 × (长 + 宽) = 2 × (12 + 8) = 40 米"
  ],
  "temperature": 0.0,
  "max_tokens": 300
}
```

#### 参考来源
- GSM8K 应用题
- 中国小学数学题库
- MATH 数据集

### 3. 代码生成 (Code)

#### 设计原则
- **功能明确**: 清晰的输入输出规范
- **可测试**: 提供单元测试用例
- **难度适中**: 避免过于复杂的算法

#### 示例题目结构
```json
{
  "id": "code_001",
  "task_type": "code",
  "difficulty": "medium",
  "language": "python",
  "question": "编写一个函数，判断一个字符串是否为回文。",
  "function_signature": "def is_palindrome(s: str) -> bool:",
  "test_cases": [
    {"input": "racecar", "expected": true},
    {"input": "hello", "expected": false},
    {"input": "A man a plan a canal Panama", "expected": true}
  ],
  "temperature": 0.1,
  "max_tokens": 500
}
```

#### 参考来源
- HumanEval
- LeetCode 简单/中等题
- 实际编程场景

### 4. 文本摘要 (Summary)

#### 设计原则
- **长度控制**: 原文 300-800 字，摘要 50-150 字
- **信息完整**: 保留关键信息
- **多样性**: 新闻、论文、会议纪要

#### 示例题目结构
```json
{
  "id": "summary_001",
  "task_type": "summary",
  "difficulty": "medium",
  "source_type": "news",
  "source_text": "（300-500字新闻文本）",
  "reference_summary": "（50-100字参考摘要）",
  "instruction": "请将以下新闻总结为 50-100 字的摘要，保留关键信息。",
  "temperature": 0.7,
  "max_tokens": 200,
  "repeat": 5
}
```

#### 评估指标
- ROUGE-L (与参考摘要的重叠度)
- BERTScore (语义相似度)
- 压缩比 (原文长度 / 摘要长度)

### 5. 创意写作 (Creative)

#### 设计原则
- **开放性**: 允许多样化输出
- **主题明确**: 提供清晰的写作方向
- **多样性评估**: 使用 Distinct-N 指标

#### 示例题目结构
```json
{
  "id": "creative_001",
  "task_type": "creative",
  "difficulty": "medium",
  "prompt_type": "story_continuation",
  "prompt": "夜幕降临，小镇的街道上空无一人。突然，一道刺眼的光芒从天而降...",
  "instruction": "请续写这个故事（100-200字）",
  "temperature": 0.8,
  "max_tokens": 300,
  "repeat": 5
}
```

#### 评估指标
- Distinct-2 (词汇多样性)
- Self-BLEU (生成多样性)
- 流畅度 (困惑度)

## 翻译任务设计

### 为什么添加翻译任务？

1. **多语言能力评估**: 测试模型的跨语言理解
2. **实用性强**: 翻译是常见的实际应用场景
3. **客观评估**: 有标准参考译文和成熟的评估指标
4. **能效对比**: 翻译任务对不同模型的资源消耗差异明显

### 翻译任务类型

#### 1. 英译中 (En→Zh)
```json
{
  "id": "trans_en_zh_001",
  "task_type": "translation",
  "direction": "en_to_zh",
  "difficulty": "easy",
  "domain": "general",
  "source_text": "Artificial intelligence is transforming the way we live and work.",
  "reference_translation": "人工智能正在改变我们的生活和工作方式。",
  "instruction": "请将以下英文翻译成中文：",
  "temperature": 0.2,
  "max_tokens": 200
}
```

#### 2. 中译英 (Zh→En)
```json
{
  "id": "trans_zh_en_001",
  "task_type": "translation",
  "direction": "zh_to_en",
  "difficulty": "medium",
  "domain": "technology",
  "source_text": "深度学习模型在图像识别领域取得了突破性进展。",
  "reference_translation": "Deep learning models have made breakthrough progress in the field of image recognition.",
  "instruction": "请将以下中文翻译成英文：",
  "temperature": 0.2,
  "max_tokens": 200
}
```

#### 3. 专业领域翻译
```json
{
  "id": "trans_tech_001",
  "task_type": "translation",
  "direction": "en_to_zh",
  "difficulty": "hard",
  "domain": "technical",
  "source_text": "The convolutional neural network architecture consists of multiple layers including convolution, pooling, and fully connected layers.",
  "reference_translation": "卷积神经网络架构由多个层组成，包括卷积层、池化层和全连接层。",
  "terminology": {
    "convolutional neural network": "卷积神经网络",
    "pooling": "池化",
    "fully connected": "全连接"
  },
  "instruction": "请将以下技术文本翻译成中文，注意专业术语的准确性：",
  "temperature": 0.1,
  "max_tokens": 300
}
```

### 翻译难度设计

| 难度 | 特征 | 句子长度 | 领域 | 比例 |
|------|------|---------|------|------|
| 简单 | 日常对话、简单句式 | 10-20 词 | 通用 | 30% |
| 中等 | 复合句、常见术语 | 20-40 词 | 新闻、科技 | 50% |
| 困难 | 复杂句式、专业术语 | 40+ 词 | 学术、法律 | 20% |

### 翻译评估指标

#### 自动评估指标
1. **BLEU** (Bilingual Evaluation Understudy)
   - 计算 n-gram 重叠度
   - 范围: 0-100，越高越好
   - 适用: 快速评估

2. **chrF++** (Character n-gram F-score)
   - 基于字符级别的 F-score
   - 对中文等非空格分隔语言更友好
   - 范围: 0-100

3. **COMET** (Crosslingual Optimized Metric for Evaluation of Translation)
   - 基于神经网络的评估
   - 与人工评估相关性最高
   - 需要额外模型

4. **BERTScore**
   - 基于 BERT 的语义相似度
   - 捕捉语义而非字面匹配
   - 适用: 意译评估

#### 人工评估维度
1. **准确性** (Accuracy): 是否忠实原文
2. **流畅度** (Fluency): 译文是否自然
3. **术语一致性** (Terminology): 专业术语是否准确

### 翻译测试用例数量建议

| 语言对　 | 简单　 | 中等　 | 困难　| 总计　 |
| ----------| --------| --------| -------| --------|
| 英→中　　| 5　　　| 8　　　| 3　　 | 16　　 |
| 中→英　　| 5　　　| 8　　　| 3　　 | 16　　 |
| **总计** | **10** | **16** | **6** | **32** |

### 翻译数据来源

1. **FLORES-200**: 标准化多语言测试集
2. **WMT 新闻测试集**: 新闻领域翻译
3. **自建语料**: 
   - 技术文档（GitHub README）
   - 学术摘要（arXiv 论文）
   - 日常对话（电影字幕）

## 测试用例最佳实践

### 1. 难度分层原则

遵循 **30-50-20 原则**：
- 简单题（30%）: 验证基础能力
- 中等题（50%）: 评估实际应用能力
- 困难题（20%）: 测试边界情况

### 2. 领域覆盖

确保多样性：
- 通用知识（40%）
- 专业领域（30%）: 科技、医学、法律
- 日常应用（30%）: 对话、写作、翻译

### 3. 温度参数设置

| 任务类型 | 温度　　| 原因　　　　　　　　　　　　　　　　　　　　|
| ----------| ---------| ---------------------------------------------|
| 知识问答 | 0.0　　 | 需要确定性答案　　　　　　　　　　　　　　　|
| 数学计算 | 0.0　　 | 唯一正确答案　　　　　　　　　　　　　　　　|
| 代码生成 | 0.1　　 | 轻微随机性，避免过拟合　　　　　　　　　　　|
| 翻译　　 | 0.1-0.2 | 允许    "user": "它和深度学习有什么区别？", |

## 评估指标选择

### 客观任务指标

| 任务　　 | 主指标　　　 | 辅助指标　　　　 |
| ----------| --------------| ------------------|
| 知识问答 | 准确率　　　 | F1 分数　　　　　|
| 数学计算 | 答案准确率　 | 步骤完整性　　　 |
| 代码生成 | 测试通过率　 | 编译成功率　　　 |
| 翻译　　 | BLEU, chrF++ | BERTScore, COMET |

### 主观任务指标

| 任务 | 主指标 | 辅助指标 |
|------|--------|---------|
| 文本摘要 | ROUGE-L | BERTScore, 压缩比 |
| 创意写作 | Distinct-2 | Self-BLEU, 流畅度 |
| 多轮对话 | 上下文一致性  数据集
- [MMLU](https://github.com/hendrycks/test)
- [GSM8K](https://github.com/openai/grade-school-math)
- [HumanEval](https://github.com/openai/human-eval)
- [FLORES-200](https://github.com/facebookresearch/flores)
- [WMT](https://www.statmt.org/wmt24/)

### 评估工具
- [BLEU/chrF++](https://github.com/mjpost/sacrebleu)
- [COMET](https://github.com/Unbabel/COMET)
- [BERTScore](https://github.com/Tiiiger/bert_score)
- [ROUGE](https://github.com/google-research/google-research/tree/master/rouge)

### 相关论文
1. Hendrycks et al. (2021). "Measuring Massive Multitask Language Understanding"
2. Cobbe et al. (2021). "Training Verifiers to Solve Math Word Problems"
3. Chen et al. (2021). "Evaluating Large Language Models Trained on Code"
4. NLLB Team (2022). "No Language Left Behind"
5. Freitag et al. (2022). "Results of WMT22 Metrics Shared Task"

## 下一步

1. 根据本指南创建测试用例 JSON 文件
2. 参考 `data/test/test_cases.json` 的格式
3. 使用 `experiments/experiment_runner.py` 运行实验
4. 分析结果并迭代优化测试用例

---

**文档版本**: 1.0  
**最后更新**: 2026-03-02  
**维护者**: 项目团队
