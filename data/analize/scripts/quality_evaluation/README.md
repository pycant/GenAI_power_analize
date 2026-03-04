# 质量评估模块使用说明

## 概述

本模块提供针对不同任务类型的质量评估功能，目前已实现代码生成任务（code）的评估。

## 已实现的评估器

### 1. CodeEvaluator - 代码生成任务评估器

**评估指标**:
- `compilation_rate`: 编译成功率 [0, 1]
- `has_code`: 是否包含代码 [0, 1]
- `code_length`: 代码行数（越短越好）
- `cyclomatic_complexity`: 圈复杂度（越低越好）

**使用示例**:

```python
from quality_evaluation import CodeEvaluator

# 初始化评估器
evaluator = CodeEvaluator(config={'verbose': True})

# 评估单个代码
generated_code = """
def add(a, b):
    return a + b
"""

scores = evaluator.evaluate(generated_code)
print(scores)
# 输出: {'compilation_rate': 1.0, 'code_length': 2, 'cyclomatic_complexity': 1, 'has_code': 1.0}
```

## 批量评估脚本

### evaluate_code_quality.py

批量评估所有模型在代码生成任务上的质量。

**基础用法**:

```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行评估
python data/analize/scripts/evaluate_code_quality.py
```

**高级用法**:

```bash
# 详细输出（显示每个样本的评估过程）
python evaluate_code_quality.py --verbose

# 自定义输入输出路径
python evaluate_code_quality.py \
  --input data/analize/pre_data/responses_raw.csv \
  --output-dir data/analize/pre_data
```

**输出文件**:
- `quality_scores_code.csv`: 详细评分结果（每个样本一行）
- `quality_summary_code.csv`: 汇总统计（每个模型一行）

## 模块结构

```
quality_evaluation/
├── __init__.py              # 模块初始化
├── base_evaluator.py        # 基础评估器接口
├── code_evaluator.py        # 代码任务评估器
├── utils.py                 # 工具函数
└── README.md                # 本文档
```

## 扩展新的评估器

### 步骤1: 创建评估器类

```python
# creative_evaluator.py
from .base_evaluator import BaseEvaluator

class CreativeEvaluator(BaseEvaluator):
    def evaluate(self, generated, reference=None, context=None):
        scores = {}
        
        # 实现你的评估逻辑
        scores['distinct_2'] = self._calculate_distinct_2(generated)
        
        return scores
    
    def _calculate_distinct_2(self, text):
        # 计算 Distinct-2
        pass
```

### 步骤2: 注册到模块

```python
# __init__.py
from .creative_evaluator import CreativeEvaluator

__all__ = [
    'BaseEvaluator',
    'CodeEvaluator',
    'CreativeEvaluator',  # 添加新的评估器
]
```

### 步骤3: 创建批量评估脚本

参考 `evaluate_code_quality.py` 创建对应的批量评估脚本。

## 工具函数

### 代码提取

```python
from quality_evaluation.utils import extract_python_code

text = """
Here is the code:
```python
def hello():
    print("Hello")
```
"""

code = extract_python_code(text)
print(code)
# 输出: def hello():\n    print("Hello")
```

### 代码行数统计

```python
from quality_evaluation.utils import count_code_lines

code = """
def add(a, b):
    # This is a comment
    return a + b

"""

lines = count_code_lines(code)
print(lines)  # 输出: 2（不包括空行和注释）
```

### 圈复杂度计算

```python
from quality_evaluation.utils import calculate_cyclomatic_complexity

code = """
def check(x):
    if x > 0:
        return True
    elif x < 0:
        return False
    else:
        return None
"""

complexity = calculate_cyclomatic_complexity(code)
print(complexity)  # 输出: 3（1 + if + elif）
```

## 依赖

**标准库**（无需安装）:
- `ast` - Python 抽象语法树
- `re` - 正则表达式
- `sys` - 系统功能
- `pathlib` - 路径操作

**第三方库**（已安装）:
- `pandas` - 数据处理
- `tqdm` - 进度条

## 常见问题

### Q: 为什么有些代码编译失败？

A: 常见原因：
1. 缺少缩进（Python 语法要求）
2. 字符串未正确闭合
3. 语法结构不完整（如 `for` 循环没有循环体）

### Q: 如何查看详细的评估过程？

A: 使用 `--verbose` 参数：

```bash
python evaluate_code_quality.py --verbose
```

### Q: 如何评估其他编程语言的代码？

A: 当前仅支持 Python。要支持其他语言，需要：
1. 在 `utils.py` 中添加语言特定的代码提取函数
2. 在 `code_evaluator.py` 中添加语言特定的编译检查
3. 更新 `evaluate()` 方法以支持 `language` 参数

### Q: 圈复杂度是如何计算的？

A: 使用简化的关键字计数法：

```
complexity = 1 + count(if) + count(elif) + count(for) + 
             count(while) + count(and) + count(or) + 
             count(except) + count(with)
```

这是一个近似值，不是严格的圈复杂度。

## 下一步计划

- [ ] CreativeEvaluator - 创意写作评估
- [ ] MathEvaluator - 数学推理评估
- [ ] QAEvaluator - 问答评估
- [ ] SummaryEvaluator - 文本摘要评估
- [ ] 支持更多编程语言（JavaScript, Java, C++）
- [ ] 实现 Pass@k 指标（需要测试用例执行）

## 参考文档

- **评估设计**: `../quality_evaluation_system.md`
- **评估说明**: `../README_QUALITY_EVAL.md`
- **完成报告**: `../../CODE_QUALITY_EVALUATION_COMPLETE.md`

---

**版本**: v1.0  
**更新时间**: 2026-03-04  
**作者**: Kiro AI Assistant
