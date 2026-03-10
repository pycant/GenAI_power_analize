# 混合任务分析脚本更新说明

## 更新日期
2026-03-08

## 更新内容

### 1. 工作目录设置
**变更**: 脚本启动时自动切换到项目根目录

**代码位置**: 脚本开头
```python
# 设置工作目录为项目根目录
project_root = Path(__file__).parent.parent.parent.parent
import os
os.chdir(project_root)
sys.path.insert(0, str(project_root))
```

**效果**:
- 无论从哪个目录运行脚本，工作目录都会自动设置为 `F:\all_proj\GenAI_power_analize`
- 确保相对路径的一致性
- 避免路径错误

**验证**:
```python
print(f"工作目录: {os.getcwd()}")
# 输出: 工作目录: F:\all_proj\GenAI_power_analize
```

### 2. 权重归一化功能
**新增函数**: `normalize_weights()`

**功能**: 自动归一化权重，使其和为1

**代码**:
```python
def normalize_weights(weights: Dict[str, float], verbose: bool = True) -> Dict[str, float]:
    """
    归一化权重，使其和为1
    
    Args:
        weights: 原始权重字典
        verbose: 是否输出详细信息
    
    Returns:
        Dict[str, float]: 归一化后的权重字典
    """
    total = sum(weights.values())
    
    if verbose:
        print(f"\n权重归一化:")
        print(f"  原始权重和: {total:.6f}")
    
    if abs(total - 1.0) < 1e-6:
        if verbose:
            print(f"  权重已归一化，无需调整")
        return weights.copy()
    
    # 归一化
    normalized = {task: weight / total for task, weight in weights.items()}
    
    if verbose:
        print(f"  归一化后权重和: {sum(normalized.values()):.6f}")
        print(f"\n权重调整:")
        for task in weights.keys():
            print(f"    {task}: {weights[task]:.6f} -> {normalized[task]:.6f} ({normalized[task]*100:.2f}%)")
    
    return normalized
```

**使用场景**:

#### 场景1: 权重和为1（无需调整）
```python
weights = {
    'code': 0.30,
    'math': 0.25,
    'qa': 0.20,
    'reasoning': 0.15,
    'creative': 0.05,
    'summary': 0.03,
    'translation': 0.02
}
# 总和 = 1.00，无需调整
```

输出:
```
权重归一化:
  原始权重和: 1.000000
  权重已归一化，无需调整
```

#### 场景2: 权重和不为1（自动归一化）
```python
weights = {
    'code': 30,
    'math': 25,
    'qa': 20,
    'reasoning': 15,
    'creative': 5,
    'summary': 3,
    'translation': 2
}
# 总和 = 100，需要归一化
```

输出:
```
权重归一化:
  原始权重和: 100.000000
  归一化后权重和: 1.000000

权重调整:
    code: 30.000000 -> 0.300000 (30.00%)
    math: 25.000000 -> 0.250000 (25.00%)
    qa: 20.000000 -> 0.200000 (20.00%)
    reasoning: 15.000000 -> 0.150000 (15.00%)
    creative: 5.000000 -> 0.050000 (5.00%)
    summary: 3.000000 -> 0.030000 (3.00%)
    translation: 2.000000 -> 0.020000 (2.00%)
```

#### 场景3: 权重和略有偏差（自动修正）
```python
weights = {
    'code': 0.30,
    'math': 0.25,
    'qa': 0.20,
    'reasoning': 0.15,
    'creative': 0.05,
    'summary': 0.03,
    'translation': 0.03  # 总和 = 1.01
}
```

输出:
```
权重归一化:
  原始权重和: 1.010000
  归一化后权重和: 1.000000

权重调整:
    code: 0.300000 -> 0.297030 (29.70%)
    math: 0.250000 -> 0.247525 (24.75%)
    ...
```

### 3. 集成到分析流程

**更新函数**: `aggregate_quality_scores()`

**变更**:
- 在聚合质量得分前自动调用 `normalize_weights()`
- 使用归一化后的权重进行计算
- 输出权重调整信息

**更新函数**: `run_mixed_task_analysis()`

**变更**:
- 在分析开始时显示权重归一化信息
- 在报告中使用归一化后的权重
- 在可视化中使用归一化后的权重
- 输出工作目录信息

**更新函数**: `main()`

**变更**:
- 显示工作目录和项目根目录
- 便于调试和验证

## 使用示例

### 示例1: 使用标准权重（和为1）
```python
from pareto_core.pareto_mixed_task import run_mixed_task_analysis
from pathlib import Path

output_dir = Path('analysis/qe_research/results/mixed_task_analysis/task_01')
run_mixed_task_analysis('objective', output_dir)
```

输出:
```
================================================================================
混合任务帕累托前沿分析 - 客观任务为主
================================================================================
配置: objective
说明: 适用于技术应用、工程实践、需要精确结果的场景
================================================================================

权重归一化:
  原始权重和: 1.000000
  权重已归一化，无需调整

...
```

### 示例2: 使用自定义权重（和不为1）
```python
# 修改权重配置
WEIGHT_CONFIGS['custom'] = {
    'name': '自定义配置',
    'description': '测试权重归一化',
    'weights': {
        'code': 30,      # 使用整数
        'math': 25,
        'qa': 20,
        'reasoning': 15,
        'creative': 5,
        'summary': 3,
        'translation': 2
    }
}

run_mixed_task_analysis('custom', output_dir)
```

输出:
```
权重归一化:
  原始权重和: 100.000000
  归一化后权重和: 1.000000

权重调整:
    code: 30.000000 -> 0.300000 (30.00%)
    math: 25.000000 -> 0.250000 (25.00%)
    ...
```

### 示例3: 从任意目录运行
```bash
# 从任意目录运行
cd F:\any_directory
python F:\all_proj\GenAI_power_analize\analysis\qe_research\scripts\pareto_core\pareto_mixed_task.py
```

输出:
```
================================================================================
混合任务帕累托前沿分析 - 批量执行
================================================================================
工作目录: F:\all_proj\GenAI_power_analize
项目根目录: F:\all_proj\GenAI_power_analize
配置数量: 3
任务数量: 7
================================================================================
```

## 优势

### 1. 灵活性
- 支持任意权重格式（整数、小数、百分比）
- 自动处理权重和不为1的情况
- 无需手动计算归一化

### 2. 鲁棒性
- 自动修正权重偏差
- 避免因权重和不为1导致的错误
- 提供详细的调整信息

### 3. 可维护性
- 工作目录自动设置，避免路径问题
- 清晰的日志输出，便于调试
- 代码模块化，易于扩展

### 4. 用户友好
- 无需关心权重格式
- 自动处理常见错误
- 详细的输出信息

## 兼容性

### 向后兼容
- 现有的权重配置（和为1）无需修改
- 自动检测并跳过归一化
- 不影响现有功能

### 新功能
- 支持新的权重格式
- 自动归一化
- 详细的调试信息

## 测试建议

### 测试1: 标准权重
```python
weights = {'code': 0.3, 'math': 0.25, 'qa': 0.2, 'reasoning': 0.15, 
           'creative': 0.05, 'summary': 0.03, 'translation': 0.02}
assert abs(sum(weights.values()) - 1.0) < 1e-6
```

### 测试2: 整数权重
```python
weights = {'code': 30, 'math': 25, 'qa': 20, 'reasoning': 15, 
           'creative': 5, 'summary': 3, 'translation': 2}
normalized = normalize_weights(weights, verbose=False)
assert abs(sum(normalized.values()) - 1.0) < 1e-6
```

### 测试3: 权重偏差
```python
weights = {'code': 0.301, 'math': 0.25, 'qa': 0.2, 'reasoning': 0.15, 
           'creative': 0.05, 'summary': 0.03, 'translation': 0.02}
normalized = normalize_weights(weights, verbose=False)
assert abs(sum(normalized.values()) - 1.0) < 1e-6
```

### 测试4: 工作目录
```python
import os
from pathlib import Path

# 运行脚本前
original_cwd = os.getcwd()

# 运行脚本（会自动切换工作目录）
# ...

# 验证工作目录
assert os.getcwd() == str(Path(__file__).parent.parent.parent.parent)
```

## 注意事项

1. **权重格式**: 支持任意正数，会自动归一化
2. **精度**: 使用 `1e-6` 作为浮点数比较阈值
3. **日志**: 默认输出详细信息，可通过 `verbose=False` 关闭
4. **工作目录**: 脚本会自动切换到项目根目录，无需手动设置

## 相关文件

- 实现脚本: `analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py`
- 使用指南: `analysis/qe_research/results/mixed_task_analysis/QUICK_START.md`
- 方法文档: `analysis/qe_research/results/mixed_task_analysis/method.md`

---

**更新版本**: 1.1  
**更新日期**: 2026-03-08  
**状态**: ✅ 已完成并测试
