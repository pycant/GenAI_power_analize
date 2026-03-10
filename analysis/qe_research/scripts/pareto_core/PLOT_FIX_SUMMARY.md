# 绘图函数修复总结

## 问题描述

在 `pareto_mixed_task.py` 中，`plot_task_weights()` 和 `plot_quality_heatmap()` 函数无法生成图片。

## 根本原因

**作用域问题**：`WEIGHT_CONFIGS` 和 `ALL_TASKS` 被定义在 `if __name__ == '__main__':` 块内，导致模块级别的函数无法访问这些变量。

```python
# 错误的结构
def plot_task_weights(...):
    # 尝试访问 WEIGHT_CONFIGS
    ax.set_title(f'... - {WEIGHT_CONFIGS[config_name]["name"]}')  # ❌ NameError

if __name__ == '__main__':
    WEIGHT_CONFIGS = {...}  # 只在 __main__ 块中定义
```

当函数在模块级别定义但尝试访问只在 `__main__` 块中存在的变量时，会导致 `NameError`。

## 解决方案

将 `WEIGHT_CONFIGS` 和 `ALL_TASKS` 移到模块级别（在所有函数定义之前）：

```python
# 正确的结构
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 权重配置（模块级别）
# ============================================================================

WEIGHT_CONFIGS = {
    'objective': {...},
    'subjective': {...},
    'balanced': {...}
}

ALL_TASKS = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']

# ============================================================================
# 核心函数
# ============================================================================

def plot_task_weights(...):
    # 现在可以访问 WEIGHT_CONFIGS ✓
    ax.set_title(f'... - {WEIGHT_CONFIGS[config_name]["name"]}')

if __name__ == '__main__':
    main()  # 简化 __main__ 块
```

## 修改内容

### 1. 移动配置定义（第 43-99 行）

将 `WEIGHT_CONFIGS` 和 `ALL_TASKS` 从 `if __name__ == '__main__':` 块移到模块顶部。

### 2. 简化 __main__ 块（文件末尾）

```python
# 修改前
if __name__ == '__main__':
    WEIGHT_CONFIGS = {...}
    ALL_TASKS = [...]
    main()

# 修改后
if __name__ == '__main__':
    main()
```

## 影响的函数

修复后以下函数可以正常工作：

1. `plot_task_weights()` - 绘制任务权重分布图
2. `plot_quality_heatmap()` - 绘制模型×任务质量热力图
3. `run_mixed_task_analysis()` - 主分析函数（调用上述绘图函数）

## 验证方法

运行混合任务分析脚本：

```bash
cd analysis/qe_research/scripts/pareto_core
python pareto_mixed_task.py
```

预期输出：
- ✓ 任务权重图已保存: task_weights.png
- ✓ 质量热力图已保存: quality_heatmap.png

输出位置：
```
analysis/qe_research/results/mixed_task_analysis/task_01/
├── objective/
│   ├── task_weights.png          ✓ 新生成
│   ├── quality_heatmap.png       ✓ 新生成
│   └── ...
├── subjective/
│   ├── task_weights.png          ✓ 新生成
│   ├── quality_heatmap.png       ✓ 新生成
│   └── ...
└── balanced/
    ├── task_weights.png          ✓ 新生成
    ├── quality_heatmap.png       ✓ 新生成
    └── ...
```

## Python 作用域最佳实践

### ✓ 推荐做法

```python
# 模块级常量
CONFIG = {...}

def function():
    # 可以访问 CONFIG
    return CONFIG['key']

if __name__ == '__main__':
    main()
```

### ✗ 避免做法

```python
def function():
    # 尝试访问未定义的变量
    return CONFIG['key']  # ❌ NameError

if __name__ == '__main__':
    CONFIG = {...}  # 太晚定义
    main()
```

## 相关文件

- 修复文件：`analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py`
- 测试脚本：`analysis/qe_research/scripts/pareto_core/test_plot_functions.py`（可选）

## 修复日期

2025-03-08

## 状态

✅ 已修复并验证
