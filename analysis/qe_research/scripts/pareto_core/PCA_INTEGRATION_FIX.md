# PCA 集成问题修复说明

**问题发现时间**: 2026-03-09  
**修复状态**: ✅ 已完成

## 问题描述

用户发现在 `analysis/qe_research/results/pareto_analysis_v3/` 目录下没有生成 PCA 分析相关的文件（`pca_analysis/` 子目录、PCA 图表和报告），尽管代码中设置了 `QUALITY_METHOD = 'pca'`。

## 问题根源

### 变量作用域问题

在 `pareto_analysis_all.py` 脚本中存在变量作用域问题：

1. **全局变量未定义**: 脚本顶部只定义了 `TASK_NAME = 'summary'`，但没有定义 `QUALITY_METHOD`、`QUALITY_METRIC_NAME` 和 `OUTPUT_DIR`

2. **局部赋值无效**: 在 `if __name__ == '__main__':` 块中对这些变量的赋值是**局部的**，不会影响全局作用域

3. **函数引用全局变量**: `load_and_prepare_data()` 等函数在定义时引用的是**全局变量**，但这些全局变量在函数执行时可能不存在或使用了默认值

### 实际运行情况

由于 `QUALITY_METHOD` 全局变量未定义或使用了默认值 `'entropy'`，所以：
- 实际运行时使用的是 `entropy` 方法而不是 `pca` 方法
- 生成的是 `entropy_weights.png` 而不是 PCA 相关文件
- 没有创建 `pca_analysis/` 子目录

## 修复方案

### 1. 定义全局变量

在脚本顶部添加所有需要的全局变量定义：

```python
# 任务配置（全局变量，会在 run_all_tasks 中动态设置）
TASK_NAME = 'summary'
QUALITY_METHOD = 'entropy'  # 默认值，会在运行时被覆盖
QUALITY_METRIC_NAME = '质量得分'
OUTPUT_DIR = None
```

### 2. 使用 global 声明

在 `if __name__ == '__main__':` 块的开头添加 `global` 声明：

```python
if __name__ == '__main__':
    global TASK_NAME, QUALITY_METHOD, QUALITY_METRIC_NAME, OUTPUT_DIR
    
    # ... 后续代码
```

### 3. 更新提示信息

将提示信息从 "熵权法" 更新为 "PCA降维"：

```python
print(f"质量处理方法: pca (PCA降维)")
```

## 修复后的效果

修复后，再次运行 `pareto_analysis_all.py` 将会：

1. ✅ 正确使用 `pca` 方法加载质量数据
2. ✅ 在每个任务目录下创建 `pca_analysis/` 子目录
3. ✅ 生成 4 种 PCA 可视化图表：
   - `pca_scree_plot.png` - 碎石图
   - `pca_loadings_heatmap.png` - 载荷热力图
   - `pca_biplot.png` - 双标图
   - `pca_component_scores.png` - 主成分得分图
4. ✅ 生成详细的 PCA 分析报告：
   - `PCA_ANALYSIS_REPORT.md`

## 预期输出结构

```
analysis/qe_research/results/pareto_analysis_v3/
├── code/
│   ├── pca_analysis/
│   │   ├── PCA_ANALYSIS_REPORT.md
│   │   ├── pca_scree_plot.png
│   │   ├── pca_loadings_heatmap.png
│   │   ├── pca_biplot.png
│   │   └── pca_component_scores.png
│   ├── CODE_PARETO_ANALYSIS_REPORT.md
│   ├── merged_data.csv
│   ├── pareto_quality_energy.png
│   └── pareto_quality_speed.png
├── creative/
│   ├── pca_analysis/
│   │   └── ... (同上)
│   └── ...
└── ... (其他任务)
```

## 如何重新运行

### 方法 1: 运行完整脚本

```bash
# 激活环境
conda activate bartscore

# 运行脚本（会处理所有任务）
python analysis/qe_research/scripts/pareto_analysis_all.py
```

### 方法 2: 单独运行某个任务

如果只想重新生成某个任务的 PCA 分析，可以修改脚本中的任务列表：

```python
# 在 if __name__ == '__main__': 块中
task_list = ['code']  # 只运行 code 任务
```

### 方法 3: 使用测试脚本

使用我们创建的测试脚本：

```bash
python analysis/qe_research/scripts/pareto_core/test_pca_plotting.py
```

## 验证修复

运行脚本后，检查以下内容：

1. **控制台输出**: 应该看到 "质量处理方法: pca (PCA降维)"
2. **PCA 分析输出**: 应该看到 "✓ PCA分析完成" 和生成的文件列表
3. **目录结构**: 每个任务目录下应该有 `pca_analysis/` 子目录
4. **文件数量**: 每个 `pca_analysis/` 目录应该包含 5 个文件（1个报告 + 4个图表）

## 技术要点

### Python 变量作用域规则

1. **局部变量**: 在函数或代码块内赋值的变量默认是局部的
2. **全局变量**: 在模块顶层定义的变量是全局的
3. **global 声明**: 在函数内修改全局变量需要使用 `global` 声明

### 示例

```python
# 全局变量
x = 10

def func1():
    # 这会创建一个新的局部变量 x，不影响全局 x
    x = 20
    print(f"func1 内部: {x}")  # 输出 20

def func2():
    global x
    # 这会修改全局变量 x
    x = 30
    print(f"func2 内部: {x}")  # 输出 30

func1()
print(f"全局: {x}")  # 输出 10（未被 func1 修改）

func2()
print(f"全局: {x}")  # 输出 30（被 func2 修改）
```

## 相关文档

- [PCA 分析功能使用指南](PCA_ANALYSIS_GUIDE.md)
- [PCA 功能完成摘要](PCA_FEATURE_COMPLETE.md)
- [Pareto 分析快速参考](QUICK_REFERENCE.md)

## 后续建议

### 1. 代码重构

考虑将主逻辑封装到函数中，避免在 `if __name__ == '__main__':` 块中直接使用全局变量：

```python
def run_all_tasks(quality_method='pca'):
    """批量执行所有任务"""
    task_list = ['summary', 'qa', 'math', 'translation', 'code', 'creative']
    
    for task in task_list:
        run_single_task(
            task_name=task,
            quality_method=quality_method,
            output_base_dir=PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis_v3'
        )

if __name__ == '__main__':
    run_all_tasks(quality_method='pca')
```

### 2. 配置文件

考虑使用配置文件（YAML/JSON）来管理参数，而不是硬编码在脚本中：

```yaml
# config.yaml
quality_method: pca
tasks:
  - summary
  - qa
  - math
  - translation
  - code
  - creative
output_dir: analysis/qe_research/results/pareto_analysis_v3
```

### 3. 命令行参数

添加命令行参数支持，提高脚本灵活性：

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--method', default='pca', choices=['entropy', 'pca', 'mean', 'single'])
parser.add_argument('--tasks', nargs='+', default=['all'])
args = parser.parse_args()
```

## 总结

这个问题是一个典型的 Python 变量作用域问题。通过正确定义全局变量并使用 `global` 声明，我们确保了 `QUALITY_METHOD = 'pca'` 的设置能够被所有函数正确识别和使用，从而生成预期的 PCA 分析文件。

---

**修复者**: Kiro AI Assistant  
**修复日期**: 2026-03-09  
**验证状态**: ✅ 代码已修复，等待用户运行验证
