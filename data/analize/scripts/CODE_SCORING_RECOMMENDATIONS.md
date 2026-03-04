# 代码任务打分逻辑详细建议

**日期**: 2026-03-04  
**版本**: v1.0  
**目标**: 为代码生成任务构建科学、全面的质量评估体系

---

## 📊 当前评估体系分析

### 现有指标

| 指标 | 类型 | 范围 | 方向 | 权重 | 说明 |
|------|------|------|------|------|------|
| `compilation_rate` | 正确性 | [0, 1] | ↑ | 60% | 代码是否能编译通过 |
| `code_length` | 质量 | [0, ∞) | ↓ | 20% | 代码行数（越短越好） |
| `cyclomatic_complexity` | 质量 | [1, ∞) | ↓ | 20% | 圈复杂度（越低越好） |
| `test_pass_rate` | 正确性 | [0, 1] | ↑ | - | 测试通过率（可选） |

### 当前聚合公式

```python
# 如果没有代码 → 0.0
# 如果编译失败 → 0.1
# 如果编译成功：
final_score = 0.6 × compilation_rate + 0.2 × length_score + 0.2 × complexity_score

# 其中：
length_score = {
    1.0,                              if 10 ≤ length ≤ 50
    max(0.5, 1.0 - |length - 30|/100), otherwise
}

complexity_score = {
    1.0,                              if 1 ≤ complexity ≤ 10
    max(0.5, 1.0 - (complexity - 10)/20), otherwise
}
```

---

## 🎯 核心问题与改进方向

### 问题1: 编译成功 ≠ 功能正确

**现状**:
- 整体编译成功率: 50%
- 整体测试通过率: 20%
- 差距: 30个百分点

**示例**:
```python
# 题目：返回两个数的单位数字乘积
# 错误代码（编译成功但逻辑错误）
def multiply(a, b):
    return a * b  # ❌ 应该是 (a % 10) * (b % 10)

# 正确代码
def multiply(a, b):
    return (a % 10) * (b % 10)  # ✅
```

**建议**: 测试通过率应该是最重要的指标

---

### 问题2: 权重设置缺乏科学依据

**当前权重**:
- 编译: 60%
- 长度: 20%
- 复杂度: 20%

**问题**:
1. 为什么是 60-20-20？
2. 不同任务类型应该有不同权重
3. 没有考虑测试通过率

---

### 问题3: 代码长度和复杂度的归一化不合理

**当前逻辑**:
```python
# 假设 10-50 行是"合理范围"
# 假设复杂度 1-10 是"合理范围"
```

**问题**:
1. 这些范围是主观假设，没有数据支撑
2. 不同题目的合理范围差异很大
3. 简单题目（如 multiply）只需 1 行，复杂题目可能需要 50+ 行

---

### 问题4: 缺少代码风格和可读性评估

**当前缺失**:
- 变量命名质量
- 注释完整性
- 代码结构清晰度
- PEP 8 规范遵守

---

## 💡 改进建议方案

### 方案A: 分层评估体系（推荐）

#### 第一层：功能正确性（必要条件）

```
Level 0: 无代码或无法提取代码 → 0 分
Level 1: 有代码但编译失败 → 0.1-0.2 分
Level 2: 编译成功但测试失败 → 0.3-0.5 分
Level 3: 部分测试通过 → 0.5-0.8 分
Level 4: 全部测试通过 → 0.8-1.0 分
```

#### 第二层：代码质量（加分项）

在功能正确的基础上，根据代码质量调整分数：

```python
quality_bonus = (
    0.3 × efficiency_score +      # 效率（时间/空间复杂度）
    0.3 × simplicity_score +      # 简洁性（长度、复杂度）
    0.2 × readability_score +     # 可读性（命名、注释）
    0.2 × robustness_score        # 鲁棒性（边界处理）
)

final_score = base_score × (1 + 0.2 × quality_bonus)
```

**示例**:
```
测试全通过（base_score = 0.9）
+ 代码简洁（quality_bonus = 0.8）
→ final_score = 0.9 × (1 + 0.2 × 0.8) = 1.044 → 1.0（截断）
```

---

### 方案B: 多维度独立评分（推荐用于分析）

不聚合成单一分数，而是保留多个维度：

```python
scores = {
    # 功能维度
    'functional_correctness': test_pass_rate,  # [0, 1]
    'compilation_success': compilation_rate,    # [0, 1]
    
    # 效率维度
    'time_complexity': time_complexity_score,   # [0, 1]
    'space_complexity': space_complexity_score, # [0, 1]
    
    # 质量维度
    'code_simplicity': simplicity_score,        # [0, 1]
    'code_readability': readability_score,      # [0, 1]
    
    # 鲁棒性维度
    'edge_case_handling': edge_case_score,      # [0, 1]
}
```

**优点**:
- 保留完整信息，便于多角度分析
- 不同场景可以选择不同维度
- 避免主观权重设置

---

### 方案C: 基于参考代码的相对评分

如果有标准答案，可以进行相对评估：

```python
# 1. 功能等价性
functional_equivalence = test_pass_rate

# 2. 效率对比
efficiency_ratio = reference_time / generated_time

# 3. 简洁度对比
simplicity_ratio = reference_length / generated_length

# 4. 综合评分
relative_score = (
    0.6 × functional_equivalence +
    0.2 × min(1.0, efficiency_ratio) +
    0.2 × min(1.0, simplicity_ratio)
)
```

---

## 🔬 具体指标设计

### 1. 功能正确性指标

#### 1.1 测试通过率（核心指标）

```python
test_pass_rate = passed_tests / total_tests

# 分级评估
if test_pass_rate == 1.0:
    correctness_score = 1.0      # 完美
elif test_pass_rate >= 0.8:
    correctness_score = 0.8      # 优秀
elif test_pass_rate >= 0.5:
    correctness_score = 0.6      # 良好
elif test_pass_rate > 0:
    correctness_score = 0.4      # 及格
else:
    correctness_score = 0.2      # 不及格
```

#### 1.2 编译成功率（基础指标）

```python
compilation_score = {
    1.0,  if compiles successfully
    0.0,  otherwise
}
```

#### 1.3 边界用例处理

```python
# 检查是否处理了边界情况
edge_cases = [
    'empty_input',      # 空输入
    'null_input',       # None 输入
    'negative_numbers', # 负数
    'large_numbers',    # 大数
    'special_chars',    # 特殊字符
]

edge_case_score = handled_cases / total_cases
```

---

### 2. 代码效率指标

#### 2.1 时间复杂度评估

```python
# 静态分析（基于 AST）
def estimate_time_complexity(code):
    """
    估算时间复杂度
    
    O(1)   → 1.0
    O(log n) → 0.9
    O(n)   → 0.8
    O(n log n) → 0.7
    O(n²)  → 0.5
    O(n³)  → 0.3
    O(2ⁿ)  → 0.1
    """
    # 检测嵌套循环层数
    nested_loops = count_nested_loops(code)
    
    if nested_loops == 0:
        return 1.0  # O(1) or O(log n)
    elif nested_loops == 1:
        return 0.8  # O(n)
    elif nested_loops == 2:
        return 0.5  # O(n²)
    else:
        return 0.3  # O(n³) or worse
```

#### 2.2 空间复杂度评估

```python
def estimate_space_complexity(code):
    """
    估算空间复杂度
    
    基于：
    - 是否创建新数据结构
    - 递归深度
    - 临时变量数量
    """
    # 检测数据结构创建
    creates_list = 'list(' in code or '[' in code
    creates_dict = 'dict(' in code or '{' in code
    
    # 检测递归
    has_recursion = detect_recursion(code)
    
    if not creates_list and not creates_dict and not has_recursion:
        return 1.0  # O(1)
    elif creates_list or creates_dict:
        return 0.7  # O(n)
    else:
        return 0.5  # O(n) or worse
```

---

### 3. 代码质量指标

#### 3.1 简洁性评分

```python
def calculate_simplicity_score(code, reference_length=None):
    """
    代码简洁性评分
    
    考虑：
    - 代码行数（相对于参考实现）
    - 圈复杂度
    - 嵌套深度
    """
    length = count_code_lines(code)
    complexity = calculate_cyclomatic_complexity(code)
    nesting = calculate_max_nesting_depth(code)
    
    # 如果有参考长度，计算相对简洁度
    if reference_length:
        length_ratio = reference_length / max(1, length)
        length_score = min(1.0, length_ratio)
    else:
        # 使用绝对标准
        length_score = 1.0 / (1.0 + length / 20)
    
    # 复杂度评分
    complexity_score = 1.0 / (1.0 + complexity / 5)
    
    # 嵌套深度评分
    nesting_score = 1.0 / (1.0 + nesting / 3)
    
    # 综合评分
    simplicity = (
        0.4 × length_score +
        0.4 × complexity_score +
        0.2 × nesting_score
    )
    
    return simplicity
```

#### 3.2 可读性评分

```python
def calculate_readability_score(code):
    """
    代码可读性评分
    
    考虑：
    - 变量命名质量
    - 注释完整性
    - 代码结构
    - PEP 8 遵守度
    """
    # 变量命名（避免 a, b, x, y 等单字母）
    naming_score = evaluate_variable_naming(code)
    
    # 注释比例
    comment_ratio = count_comments(code) / max(1, count_code_lines(code))
    comment_score = min(1.0, comment_ratio * 5)  # 20% 注释为满分
    
    # 函数文档字符串
    has_docstring = '"""' in code or "'''" in code
    docstring_score = 1.0 if has_docstring else 0.5
    
    # PEP 8 检查（使用 pycodestyle）
    pep8_score = check_pep8_compliance(code)
    
    # 综合评分
    readability = (
        0.3 × naming_score +
        0.2 × comment_score +
        0.2 × docstring_score +
        0.3 × pep8_score
    )
    
    return readability
```

#### 3.3 鲁棒性评分

```python
def calculate_robustness_score(code):
    """
    代码鲁棒性评分
    
    考虑：
    - 异常处理
    - 输入验证
    - 边界条件检查
    """
    # 异常处理
    has_try_except = 'try:' in code and 'except' in code
    exception_score = 1.0 if has_try_except else 0.5
    
    # 输入验证
    has_validation = any(kw in code for kw in ['if not', 'assert', 'raise'])
    validation_score = 1.0 if has_validation else 0.5
    
    # 类型检查
    has_type_hints = '->' in code or ': ' in code
    type_score = 1.0 if has_type_hints else 0.7
    
    # 综合评分
    robustness = (
        0.4 × exception_score +
        0.4 × validation_score +
        0.2 × type_score
    )
    
    return robustness
```

---

## 📐 推荐的综合评分公式

### 公式1: 加权平均（适合排名）

```python
def calculate_final_score(metrics):
    """
    综合评分公式
    
    优先级：功能 > 效率 > 质量
    """
    # 第一层：功能正确性（必要条件）
    if metrics['test_pass_rate'] == 0:
        return 0.2  # 测试全失败
    
    if metrics['compilation_rate'] == 0:
        return 0.1  # 编译失败
    
    # 第二层：综合评分
    functional_score = (
        0.7 × metrics['test_pass_rate'] +
        0.3 × metrics['compilation_rate']
    )
    
    efficiency_score = (
        0.6 × metrics['time_complexity_score'] +
        0.4 × metrics['space_complexity_score']
    )
    
    quality_score = (
        0.4 × metrics['simplicity_score'] +
        0.3 × metrics['readability_score'] +
        0.3 × metrics['robustness_score']
    )
    
    # 最终评分
    final_score = (
        0.6 × functional_score +  # 功能最重要
        0.2 × efficiency_score +  # 效率次之
        0.2 × quality_score       # 质量加分
    )
    
    return final_score
```

### 公式2: 分级评分（适合分类）

```python
def classify_code_quality(metrics):
    """
    代码质量分级
    
    S: 优秀（90-100）
    A: 良好（80-90）
    B: 中等（70-80）
    C: 及格（60-70）
    D: 不及格（<60）
    """
    score = calculate_final_score(metrics)
    
    if score >= 0.9:
        return 'S', score
    elif score >= 0.8:
        return 'A', score
    elif score >= 0.7:
        return 'B', score
    elif score >= 0.6:
        return 'C', score
    else:
        return 'D', score
```

---

## 🎨 可视化建议

### 1. 雷达图（多维度对比）

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_code_quality_radar(metrics, model_name):
    """
    绘制代码质量雷达图
    """
    categories = [
        'Functional\nCorrectness',
        'Time\nEfficiency',
        'Space\nEfficiency',
        'Code\nSimplicity',
        'Code\nReadability',
        'Robustness'
    ]
    
    values = [
        metrics['test_pass_rate'],
        metrics['time_complexity_score'],
        metrics['space_complexity_score'],
        metrics['simplicity_score'],
        metrics['readability_score'],
        metrics['robustness_score']
    ]
    
    # 绘制雷达图
    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
    values += values[:1]  # 闭合
    angles = np.concatenate((angles, [angles[0]]))
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values, 'o-', linewidth=2, label=model_name)
    ax.fill(angles, values, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, 1)
    ax.legend()
    
    return fig
```

### 2. 热力图（模型-指标对比）

```python
def plot_model_metric_heatmap(df):
    """
    绘制模型-指标热力图
    """
    import seaborn as sns
    
    metrics = [
        'test_pass_rate',
        'compilation_rate',
        'simplicity_score',
        'readability_score'
    ]
    
    pivot = df.pivot_table(
        values=metrics,
        index='model',
        aggfunc='mean'
    )
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='RdYlGn', vmin=0, vmax=1)
    plt.title('Model Performance Heatmap')
    plt.tight_layout()
    
    return plt.gcf()
```

---

## 🚀 实施路线图

### 阶段1: 基础增强（1-2天）

- [x] 实现测试用例提取（已完成）
- [x] 实现代码执行测试（已完成）
- [ ] 优化测试通过率计算
- [ ] 添加边界用例检测

### 阶段2: 效率评估（2-3天）

- [ ] 实现时间复杂度静态分析
- [ ] 实现空间复杂度估算
- [ ] 添加嵌套循环检测
- [ ] 添加递归检测

### 阶段3: 质量评估（3-4天）

- [ ] 实现变量命名质量评估
- [ ] 实现注释完整性检查
- [ ] 集成 PEP 8 检查（pycodestyle）
- [ ] 实现代码结构分析

### 阶段4: 综合评分（1-2天）

- [ ] 实现多维度评分系统
- [ ] 实现分级评估
- [ ] 添加可视化功能
- [ ] 生成详细报告

---

## 📊 评估示例

### 示例1: 优秀代码

```python
def multiply(a: int, b: int) -> int:
    """
    返回两个整数的单位数字乘积
    
    Args:
        a: 第一个整数
        b: 第二个整数
    
    Returns:
        单位数字的乘积
    
    Examples:
        >>> multiply(148, 412)
        16
    """
    return (a % 10) * (b % 10)
```

**评分**:
```
功能正确性: 1.0 (测试全通过)
时间效率: 1.0 (O(1))
空间效率: 1.0 (O(1))
简洁性: 1.0 (1行核心代码)
可读性: 1.0 (有文档字符串、类型注解)
鲁棒性: 0.7 (无输入验证)

综合评分: 0.95 (S级)
```

### 示例2: 中等代码

```python
def multiply(a, b):
    # 获取单位数字
    unit_a = a % 10
    unit_b = b % 10
    # 返回乘积
    return unit_a * unit_b
```

**评分**:
```
功能正确性: 1.0 (测试全通过)
时间效率: 1.0 (O(1))
空间效率: 0.9 (使用临时变量)
简洁性: 0.8 (3行，略冗余)
可读性: 0.7 (有注释但无文档字符串)
鲁棒性: 0.5 (无类型注解、无输入验证)

综合评分: 0.82 (A级)
```

### 示例3: 错误代码

```python
def multiply(a, b):
    return a * b  # 错误：直接相乘
```

**评分**:
```
功能正确性: 0.0 (测试全失败)
时间效率: 1.0 (O(1))
空间效率: 1.0 (O(1))
简洁性: 1.0 (1行)
可读性: 0.5 (无文档字符串)
鲁棒性: 0.5 (无类型注解)

综合评分: 0.2 (D级) - 功能错误导致低分
```

---

## 🔍 关键建议总结

### 1. 优先级排序

```
功能正确性 > 效率 > 质量 > 风格
```

### 2. 必须实现的指标

1. **测试通过率**（最重要）
2. 编译成功率
3. 时间复杂度
4. 代码简洁性

### 3. 可选的增强指标

1. 空间复杂度
2. 可读性评分
3. 鲁棒性评分
4. PEP 8 遵守度

### 4. 避免的陷阱

1. ❌ 不要用主观权重（如 60-20-20）
2. ❌ 不要假设"合理范围"（如 10-50 行）
3. ❌ 不要忽视测试通过率
4. ❌ 不要过度惩罚代码长度

### 5. 推荐做法

1. ✅ 保留多维度原始指标
2. ✅ 提供多种聚合方式
3. ✅ 基于数据统计确定阈值
4. ✅ 允许用户自定义权重

---

## 📚 参考资源

### 代码质量评估工具

- **pylint**: Python 代码静态分析
- **pycodestyle**: PEP 8 风格检查
- **radon**: 代码复杂度分析
- **bandit**: 安全性检查

### 学术参考

1. **Halstead Complexity Measures**: 代码复杂度度量
2. **Maintainability Index**: 可维护性指数
3. **Code Smells**: 代码坏味道检测

### 工业实践

- Google Code Review Guidelines
- Microsoft Code Quality Metrics
- Facebook Code Quality Standards

---

**更新时间**: 2026-03-04  
**作者**: Kiro AI Assistant  
**状态**: 建议文档 v1.0
