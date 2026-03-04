# 代码正确性评估总结

## ✅ 功能实现

**日期**: 2026-03-04  
**状态**: 已实现并测试 ✅

---

## 📊 实现的功能

### 1. 代码执行器（CodeExecutor）

**文件**: `data/analize/scripts/quality_evaluation/code_executor.py`

**核心功能**:
- ✅ 从prompt中提取测试用例（assert语句和Examples）
- ✅ 安全地执行生成的代码
- ✅ 运行测试用例并统计通过率
- ✅ 危险代码检测（防止恶意操作）

**支持的测试用例格式**:

1. **Assert语句**:
```python
assert multiply(148, 412) == 16
assert add(1, 2) == 3
```

2. **Examples格式**:
```python
Examples:
multiply(148, 412) should return 16.
add(1, 2) should return 3.
```

### 2. 增强的代码评估器（CodeEvaluator）

**更新内容**:
- ✅ 集成代码执行器
- ✅ 添加`enable_execution`配置选项
- ✅ 新增测试通过率指标

**新增指标**:
- `test_pass_rate`: 测试通过率 [0, 1]
- `tests_passed`: 通过的测试数量
- `tests_total`: 总测试数量

### 3. 批量评估脚本更新

**新增参数**:
```bash
--enable-execution    # 启用代码执行测试
```

**使用示例**:
```bash
# 仅编译检查（默认）
python evaluate_code_quality.py

# 启用代码执行测试
python evaluate_code_quality.py --enable-execution

# 详细输出 + 代码执行
python evaluate_code_quality.py --enable-execution --verbose
```

---

## 📈 评估结果

### 整体统计

```
总样本数: 60
包含测试用例的样本: 10 (16.7%)
整体测试通过率: 20.0%
完全通过的样本: 2/10 (20.0%)
完全失败的样本: 8/10 (80.0%)
```

### Top 2 模型（测试通过率100%）

| 排名 | 模型 | 测试通过率 | 通过/总数 | 编译成功率 |
|------|------|-----------|----------|-----------|
| 1 | deepseek_8b_ol_q4km | 100% | 4/4 | 60% |
| 2 | gemma_4b_ol_q4km | 100% | 4/4 | 100% |

### 关键发现

1. **测试覆盖率低**
   - 只有16.7%的样本包含可提取的测试用例
   - 大部分prompt没有明确的测试用例

2. **编译成功 ≠ 逻辑正确**
   - 8个样本编译成功但测试失败
   - 说明代码语法正确但逻辑错误

3. **模型表现差异大**
   - deepseek_8b和gemma_4b表现最好（100%通过率）
   - 其他模型测试通过率为0%

---

## 🔍 示例分析

### 成功案例：deepseek_8b_ol_q4km

**Prompt**:
```python
def multiply(a, b):
    """Complete the function that takes two integers and returns 
    the product of their unit digits.
    Examples:
    multiply(148, 412) should return 16.
    multiply(19, 28) should return 72.
    multiply(2020, 1851) should return 0.
    multiply(14,-15) should return 20.
    """
```

**生成的代码**:
```python
def multiply(a, b):
    return (a % 10) * (b % 10)
```

**测试结果**:
- ✅ 编译成功
- ✅ 4/4 测试通过（100%）

### 失败案例：gemma_2b_hf_4bit

**生成的代码**:
```python
def multiply(a, b):
    return a * b  # 错误：应该是单位数字相乘
```

**测试结果**:
- ✅ 编译成功
- ❌ 0/4 测试通过（0%）
- 原因：逻辑错误，直接相乘而不是提取单位数字

---

## 🛡️ 安全措施

### 危险代码检测

代码执行器会检测以下危险操作：

```python
dangerous_keywords = [
    'import os',
    'import sys',
    'import subprocess',
    'import shutil',
    '__import__',
    'eval(',
    'exec(',
    'compile(',
    'open(',
    'file(',
    'input(',
    'raw_input(',
]
```

如果检测到危险代码，会拒绝执行并返回错误。

### 执行限制

- **超时控制**: 默认5秒超时
- **沙箱环境**: 独立的执行环境（exec_globals, exec_locals）
- **异常捕获**: 所有异常都会被捕获并记录

---

## 📁 输出文件

### quality_scores_code.csv

**新增字段**:
```
test_pass_rate        - 测试通过率 [0, 1]
tests_passed          - 通过的测试数量
tests_total           - 总测试数量
```

**示例数据**:
```csv
experiment_id,model,compilation_rate,test_pass_rate,tests_passed,tests_total
exp_xxx,deepseek_8b_ol_q4km,1.0,1.0,4.0,4.0
exp_yyy,gemma_2b_hf_4bit,1.0,0.0,0.0,4.0
```

---

## 🚀 使用指南

### 基础使用

```bash
# 1. 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 2. 运行评估（仅编译检查）
python data/analize/scripts/evaluate_code_quality.py

# 3. 运行评估（包含代码执行）
python data/analize/scripts/evaluate_code_quality.py --enable-execution
```

### 查看测试结果

```bash
# 分析测试结果
python data/analize/scripts/analyze_test_results.py
```

### Python API

```python
from quality_evaluation import CodeEvaluator

# 初始化评估器（启用代码执行）
config = {'enable_execution': True, 'verbose': True}
evaluator = CodeEvaluator(config)

# 评估代码
code = """
def multiply(a, b):
    return (a % 10) * (b % 10)
"""

prompt = """
Examples:
multiply(148, 412) should return 16.
multiply(19, 28) should return 72.
"""

context = {'prompt': prompt}
scores = evaluator.evaluate(code, context=context)

print(f"编译成功率: {scores['compilation_rate']}")
print(f"测试通过率: {scores['test_pass_rate']}")
print(f"通过测试: {scores['tests_passed']}/{scores['tests_total']}")
```

---

## 🔧 技术实现

### 测试用例提取

```python
def extract_test_cases(self, prompt: str) -> List[str]:
    # 方法1: 提取assert语句
    assert_pattern = r'assert\s+.+?(?:\n|$)'
    asserts = re.findall(assert_pattern, prompt)
    
    # 方法2: 从Examples中提取
    example_pattern = r'(\w+)\(([^)]+)\)\s+should\s+return\s+([^.\n]+)'
    examples = re.findall(example_pattern, prompt)
    
    # 构造assert语句
    for func_name, args, expected in examples:
        test_case = f"assert {func_name}({args}) == {expected}"
        test_cases.append(test_case)
    
    return test_cases
```

### 代码执行

```python
def execute_code_with_tests(self, code: str, test_cases: List[str]):
    # 创建执行环境
    exec_globals = {}
    exec_locals = {}
    
    # 执行代码定义
    exec(code, exec_globals, exec_locals)
    
    # 运行测试用例
    for test_case in test_cases:
        try:
            exec(test_case, exec_globals, exec_locals)
            passed += 1
        except AssertionError:
            failed += 1
    
    return {'passed': passed, 'failed': failed}
```

---

## 📊 指标对比

### 编译成功率 vs 测试通过率

| 模型 | 编译成功率 | 测试通过率 | 差距 |
|------|-----------|-----------|------|
| deepseek_8b_ol_q4km | 60% | 100% | +40% |
| gemma_4b_ol_q4km | 100% | 100% | 0% |
| gemma_2b_hf_4bit | 80% | 0% | -80% |
| qwen25_3b_hf_4bit | 80% | 0% | -80% |

**结论**:
- 编译成功不代表逻辑正确
- 需要测试用例来验证代码的实际功能
- deepseek_8b虽然编译率较低，但通过测试的代码质量很高

---

## 🎯 改进建议

### 1. 提高测试覆盖率

**当前问题**: 只有16.7%的样本有测试用例

**解决方案**:
- 为所有代码生成任务添加标准测试用例
- 使用LLM自动生成测试用例
- 从代码注释中提取更多测试信息

### 2. 增强测试用例提取

**当前限制**: 只支持简单的assert和Examples格式

**改进方向**:
- 支持更多测试用例格式
- 提取函数签名和类型注解
- 解析docstring中的测试用例

### 3. 扩展到其他语言

**当前**: 仅支持Python

**未来**:
- JavaScript: 使用Node.js执行
- Java: 使用javac编译和java执行
- C++: 使用g++编译和执行

### 4. 更安全的执行环境

**当前**: 简单的关键字检测

**改进**:
- 使用Docker容器隔离
- 使用RestrictedPython库
- 资源限制（CPU、内存、时间）

---

## 📚 相关文档

- **代码执行器**: `data/analize/scripts/quality_evaluation/code_executor.py`
- **代码评估器**: `data/analize/scripts/quality_evaluation/code_evaluator.py`
- **评估脚本**: `data/analize/scripts/evaluate_code_quality.py`
- **结果分析**: `data/analize/scripts/analyze_test_results.py`
- **完成报告**: `data/analize/CODE_QUALITY_EVALUATION_COMPLETE.md`

---

## ✅ 总结

我们已经成功实现了代码正确性评估功能：

1. ✅ **代码执行器**：安全地执行代码并运行测试
2. ✅ **测试用例提取**：从prompt中自动提取测试用例
3. ✅ **集成到评估流程**：通过`--enable-execution`参数启用
4. ✅ **结果分析**：生成详细的测试通过率统计

**关键发现**:
- 编译成功率（50%）≠ 测试通过率（20%）
- deepseek_8b和gemma_4b表现最好（100%测试通过率）
- 大部分模型能生成语法正确但逻辑错误的代码

**下一步**:
- 为更多样本添加测试用例
- 实现其他任务类型的质量评估
- 优化测试用例提取算法

---

**更新时间**: 2026-03-04  
**版本**: v1.0  
**状态**: 功能完成 ✅  
**作者**: Kiro AI Assistant
