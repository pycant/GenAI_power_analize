# 测试用例语言类型标注指南

## 目的

为测试用例添加详细的语言类型标注，用于：
1. 分析模型在不同语言上的质效比表现
2. 评估模型的多语言能力和公平性
3. 识别模型在特定语言上的优势和劣势

## 语言类型分类

### 1. 单语言任务（Monolingual）

任务的输入和输出都使用同一种语言。

**标注格式**:
```json
{
  "language": "en",           // 主要语言代码
  "language_type": "monolingual",
  "languages": ["en"]         // 涉及的语言列表
}
```

**示例**:
- 英文 QA: `language: "en"`, `language_type: "monolingual"`
- 中文推理: `language: "zh"`, `language_type: "monolingual"`
- 英文代码: `language: "en"`, `language_type: "monolingual"`

### 2. 跨语言任务（Cross-lingual）

任务涉及两种或多种语言，如翻译任务。

**标注格式**:
```json
{
  "language": "mixed",        // 标记为混合语言
  "language_type": "cross-lingual",
  "languages": ["en", "zh"],  // 涉及的语言列表
  "source_lang": "en",        // 源语言
  "target_lang": "zh"         // 目标语言
}
```

**示例**:
- 英译中: `languages: ["en", "zh"]`, `source_lang: "en"`, `target_lang: "zh"`
- 中译英: `languages: ["zh", "en"]`, `source_lang: "zh"`, `target_lang: "en"`

### 3. 代码相关任务（Code）

涉及编程语言的任务。

**标注格式**:
```json
{
  "language": "en",           // 自然语言（通常是英文）
  "language_type": "code",
  "languages": ["en"],
  "programming_language": "python"  // 编程语言
}
```

**示例**:
- Python 代码生成: `language: "en"`, `programming_language: "python"`
- JavaScript 代码: `language: "en"`, `programming_language: "javascript"`

### 4. 多语言混合任务（Multilingual）

任务中自然地混合使用多种语言。

**标注格式**:
```json
{
  "language": "mixed",
  "language_type": "multilingual",
  "languages": ["en", "zh", "ja"]  // 所有涉及的语言
}
```

## 语言代码标准

使用 ISO 639-1 或 ISO 639-3 标准：

| 语言 | 代码 | 说明 |
|------|------|------|
| 英语 | en | English |
| 中文（简体） | zh | Chinese (Simplified) |
| 中文（繁体） | zh-Hant | Chinese (Traditional) |
| 日语 | ja | Japanese |
| 韩语 | ko | Korean |
| 法语 | fr | French |
| 德语 | de | German |
| 西班牙语 | es | Spanish |
| 俄语 | ru | Russian |
| 阿拉伯语 | ar | Arabic |

## 编程语言标准

| 编程语言 | 标识符 |
|---------|--------|
| Python | python |
| JavaScript | javascript |
| Java | java |
| C++ | cpp |
| C | c |
| Go | go |
| Rust | rust |
| TypeScript | typescript |
| Ruby | ruby |
| PHP | php |

## 更新后的字段结构

### 完整字段列表

```json
{
  "id": "task_id",
  "task_type": "qa",
  
  // 语言相关字段（新增/更新）
  "language": "en",                    // 主要语言或 "mixed"
  "language_type": "monolingual",      // 语言类型
  "languages": ["en"],                 // 涉及的所有语言
  "source_lang": "en",                 // 源语言（翻译任务）
  "target_lang": "zh",                 // 目标语言（翻译任务）
  "programming_language": "python",    // 编程语言（代码任务）
  
  // 其他现有字段
  "difficulty": "easy",
  "question": "...",
  "temperature": 0.0,
  "max_tokens": 100,
  "repeat": 1,
  "source": "MMLU"
}
```

## 实际应用示例

### 示例 1: 英文 QA 任务

```json
{
  "id": "qa_machine_learning_001",
  "task_type": "qa",
  "difficulty": "easy",
  "language": "en",
  "language_type": "monolingual",
  "languages": ["en"],
  "question": "Statement 1| In a Bayesian network...",
  "temperature": 0.0,
  "max_tokens": 100,
  "source": "MMLU"
}
```

### 示例 2: 中文推理任务

```json
{
  "id": "reasoning_001",
  "task_type": "reasoning",
  "difficulty": "easy",
  "language": "zh",
  "language_type": "monolingual",
  "languages": ["zh"],
  "question": "所有的猫都是哺乳动物...",
  "temperature": 0.1,
  "max_tokens": 200
}
```

### 示例 3: 英译中翻译任务

```json
{
  "id": "translation_001",
  "task_type": "translation",
  "difficulty": "easy",
  "language": "mixed",
  "language_type": "cross-lingual",
  "languages": ["en", "zh"],
  "source_lang": "en",
  "target_lang": "zh",
  "source_text": "The quick brown fox...",
  "target_text": "敏捷的棕色狐狸...",
  "temperature": 0.2,
  "max_tokens": 200
}
```

### 示例 4: Python 代码生成任务

```json
{
  "id": "code_001",
  "task_type": "code",
  "difficulty": "easy",
  "language": "en",
  "language_type": "code",
  "languages": ["en"],
  "programming_language": "python",
  "question": "def separate_paren_groups...",
  "temperature": 0.1,
  "max_tokens": 500
}
```

### 示例 5: 多轮对话（中文）

```json
{
  "id": "multi_turn_001",
  "task_type": "multi_turn",
  "difficulty": "medium",
  "language": "zh",
  "language_type": "monolingual",
  "languages": ["zh"],
  "conversation": [
    {
      "turn": 1,
      "user": "我想去北京旅游..."
    }
  ],
  "temperature": 0.7,
  "max_tokens": 200
}
```

## 数据分析应用

### 1. 按语言类型分组分析

```python
# 分析不同语言类型的质效比
df.groupby('language_type').agg({
    'bartscore': 'mean',
    'toks_per_s': 'mean',
    'gpu_energy_j': 'mean'
})
```

### 2. 跨语言能力评估

```python
# 对比单语言和跨语言任务的表现
monolingual = df[df['language_type'] == 'monolingual']
cross_lingual = df[df['language_type'] == 'cross-lingual']
```

### 3. 语言公平性分析

```python
# 计算不同语言的公平差距
fairness_gap = df.groupby('language')['bartscore'].mean().std()
```

### 4. 编程语言性能对比

```python
# 对比不同编程语言的代码生成质量
df[df['language_type'] == 'code'].groupby('programming_language').agg({
    'code_compiles': 'mean',
    'latency_s': 'mean'
})
```

## 更新脚本

使用以下脚本批量更新现有测试用例：

```python
import json

def add_language_annotations(test_cases_file):
    with open(test_cases_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for task in data['tasks']:
        # 根据现有 language 字段推断 language_type
        if task['task_type'] == 'translation':
            task['language_type'] = 'cross-lingual'
            task['languages'] = [task.get('source_lang', 'en'), 
                                task.get('target_lang', 'zh')]
        elif task['task_type'] == 'code':
            task['language_type'] = 'code'
            task['languages'] = [task.get('language', 'en')]
            task['programming_language'] = 'python'  # 默认
        elif task.get('language') == 'mixed':
            task['language_type'] = 'multilingual'
            task['languages'] = ['en', 'zh']  # 需要手动调整
        else:
            task['language_type'] = 'monolingual'
            task['languages'] = [task.get('language', 'en')]
    
    # 保存更新后的文件
    with open(test_cases_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# 使用示例
add_language_annotations('data/test_cases/test_cases_comprehensive.json')
```

## 注意事项

1. **一致性**: 确保所有测试用例都使用相同的标注标准
2. **完整性**: 新增的字段应该覆盖所有任务类型
3. **可扩展性**: 预留字段用于未来添加新的语言或编程语言
4. **向后兼容**: 保留原有的 `language` 字段，新增字段作为补充

## 相关文档

- [测试用例设计指南](./TEST_CASE_DESIGN_GUIDE.md)
- [实验运行指南](./EXPERIMENT_RUNNER_GUIDE.md)
- [数据分析脚本](../scripts/analyze_experiments_1.py)

---

**创建日期**: 2026-03-03  
**维护者**: GenAI Power Analysis Team
