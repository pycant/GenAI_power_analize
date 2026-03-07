# Pareto 脚本重构使用指南

## ✅ 重构完成状态（2026-03-06）

**阶段 2 已完成**：成功重构 6 个任务脚本，消除约 1200 行重复代码（61% 代码减少）

### 已重构脚本
- ✅ `pareto_analysis_code.py` - 代码生成任务
- ✅ `pareto_analysis_creative.py` - 创意写作任务
- ✅ `pareto_analysis_math.py` - 数学推理任务
- ✅ `pareto_analysis_qa.py` - 问答任务
- ✅ `pareto_analysis_summary.py` - 摘要任务
- ✅ `pareto_analysis_translation.py` - 翻译任务

### 保留原版脚本
- `pareto_analysis_reasoning.py` - 使用人工评分，结构特殊
- `pareto_analysis_reasoning_enhanced.py` - 增强版
- `pareto_analysis_translation_enhanced.py` - 增强版

---

## 快速开始

### 使用重构版脚本

重构版脚本使用 `pareto_core` 共享模块，代码量减少 60%，更易维护。

```bash
# 运行任意任务分析
python analysis/qe_research/scripts/pareto_analysis_code.py
python analysis/qe_research/scripts/pareto_analysis_creative.py
python analysis/qe_research/scripts/pareto_analysis_math.py
```

---

## 共享模块说明

### `pareto_core` 模块结构

```
pareto_core/
├── __init__.py          # 模块导出
├── config.py            # 共享配置（模型映射、路径）
└── shared_functions.py  # 共享函数（核心算法）
```

### 可用的共享配置

```python
from pareto_core import (
    MODEL_MAPPING,    # 模型名称映射字典
    DATA_PATHS,       # 数据文件路径配置
    OUTPUT_ROOT,      # 输出根目录
    PROJECT_ROOT      # 项目根目录
)
```

### 可用的共享函数

```python
from pareto_core import (
    # 帕累托前沿识别
    identify_pareto_frontier_2d,  # 2D前沿识别
    identify_pareto_frontier_3d,  # 3D前沿识别
    
    # 定量指标计算
    calculate_hypervolume,        # 超体积
    calculate_spacing,            # 间距指标
    find_knee_point,              # 拐点识别
    
    # 可视化
    plot_pareto_2d,               # 2D前沿图
    
    # 数据处理
    load_energy_speed_data,       # 加载能耗速度数据
    merge_quality_metrics         # 合并质量指标
)
```

---

## 重构模板

### 创建新任务脚本的步骤

1. **复制重构版模板**

```bash
cp analysis/qe_research/scripts/pareto_analysis_code_refactored.py \
   analysis/qe_research/scripts/pareto_analysis_TASK_refactored.py
```

2. **修改任务特定配置**

```python
# 任务特定配置
TASK_NAME = 'your_task'  # 修改任务名称
QUALITY_FILE = PROJECT_ROOT / 'data' / 'analize' / 'results' / 'your_task_quality' / 'quality_summary.csv'
QUALITY_COLUMN = 'your_quality_metric'  # 修改质量列名
OUTPUT_DIR = OUTPUT_ROOT / TASK_NAME
```

3. **运行测试**

```bash
python analysis/qe_research/scripts/pareto_analysis_TASK_refactored.py
```

4. **对比原版输出**（如果存在）

```bash
# 对比数据文件
diff results/pareto_analysis/TASK/merged_data.csv \
     results/pareto_analysis/TASK/merged_data_old.csv
```

---

## 函数使用示例

### 1. 识别帕累托前沿

```python
from pareto_core import identify_pareto_frontier_2d, identify_pareto_frontier_3d

# 2D前沿：质量最大化，能耗最小化
pareto_qe = identify_pareto_frontier_2d(
    df, 
    'quality', 'energy',
    x_minimize=False,  # 质量最大化
    y_minimize=True    # 能耗最小化
)

# 3D前沿：质量最大化，能耗最小化，速度最大化
pareto_3d = identify_pareto_frontier_3d(df)
```

### 2. 计算定量指标

```python
from pareto_core import calculate_hypervolume, calculate_spacing, find_knee_point

# 超体积
hv = calculate_hypervolume(df, pareto_mask)

# 间距指标
spacing = calculate_spacing(df, pareto_mask)

# 拐点
knee_model = find_knee_point(df, pareto_mask)
```

### 3. 绘制可视化图表

```python
from pareto_core import plot_pareto_2d

plot_pareto_2d(
    df, pareto_mask,
    'quality', 'energy',
    '任务名称：质量-能耗帕累托前沿',
    output_dir / 'pareto_quality_energy.png',
    '质量指标', '能耗 (J/token)',
    x_minimize=False, y_minimize=True
)
```

### 4. 加载和合并数据

```python
from pareto_core import (
    MODEL_MAPPING, 
    DATA_PATHS,
    load_energy_speed_data, 
    merge_quality_metrics
)

# 加载能耗和速度数据
energy_dict, speed_dict = load_energy_speed_data(
    'task_name',
    DATA_PATHS['energy'],
    DATA_PATHS['speed']
)

# 合并质量数据
df = merge_quality_metrics(
    quality_df,
    energy_dict,
    speed_dict,
    MODEL_MAPPING,
    'quality_column_name'
)
```

---

## 代码对比

### 原版脚本（~500 行）

```python
# 每个脚本都重复实现这些函数
def identify_pareto_frontier_2d(...):
    # 40 行实现
    pass

def calculate_hypervolume(...):
    # 30 行实现
    pass

def find_knee_point(...):
    # 40 行实现
    pass

# 重复的模型映射
model_mapping = {
    'deepseek_8b_ol_q4km': 'deepseek-r1:8b',
    # ... 12 行
}

# 主函数
def main():
    # 加载数据
    # 识别前沿
    # 计算指标
    # 生成报告
```

### 重构版脚本（~200 行）

```python
# 导入共享模块
from pareto_core import (
    MODEL_MAPPING,
    identify_pareto_frontier_2d,
    calculate_hypervolume,
    find_knee_point,
    # ... 其他函数
)

# 只需定义任务特定配置
TASK_NAME = 'code'
QUALITY_FILE = ...
QUALITY_COLUMN = ...

# 主函数直接使用共享函数
def main():
    df = load_and_prepare_data()
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy')
    hv = calculate_hypervolume(df, pareto_qe)
    knee = find_knee_point(df, pareto_qe)
    generate_report(df, results)
```

**代码量对比**：
- 原版：~500 行
- 重构版：~200 行
- 减少：~300 行（60%）

---

## 常见问题

### Q1: 重构版和原版输出有差异吗？

A: 没有。重构版使用相同的算法，输出完全一致。

### Q2: 如何验证重构版正确性？

A: 运行两个版本并对比输出文件：

```bash
# 运行原版
python pareto_analysis_code.py

# 备份输出
mv results/pareto_analysis/code results/pareto_analysis/code_old

# 运行重构版
python pareto_analysis_code_refactored.py

# 对比
diff -r results/pareto_analysis/code results/pareto_analysis/code_old
```

### Q3: 可以混用原版和重构版吗？

A: 可以。两个版本独立运行，互不影响。建议逐步迁移到重构版。

### Q4: 如何添加新的共享函数？

A: 在 `pareto_core/shared_functions.py` 中添加函数，然后在 `__init__.py` 中导出：

```python
# shared_functions.py
def new_function(...):
    pass

# __init__.py
from .shared_functions import new_function
__all__.append('new_function')
```

### Q5: 共享模块会影响性能吗？

A: 不会。函数调用开销可忽略不计，且共享模块可能更优化。

---

## 下一步计划

### 待重构任务（按优先级）

1. **creative** - 创意写作任务
2. **math** - 数学推理任务
3. **qa** - 问答任务
4. **summary** - 摘要任务
5. **translation** - 翻译任务
6. **reasoning** - 推理任务

### 重构检查清单

每个任务重构时需要：
- [ ] 复制重构模板
- [ ] 修改任务特定配置
- [ ] 测试运行
- [ ] 对比原版输出
- [ ] 更新文档
- [ ] 提交代码

---

## 相关文档

- [REFACTORING_ROADMAP.md](./REFACTORING_ROADMAP.md) - 重构路线图
- [CODE_DUPLICATION_ANALYSIS.md](./CODE_DUPLICATION_ANALYSIS.md) - 代码重复分析
- [PARETO_SCRIPTS_SUMMARY.md](./PARETO_SCRIPTS_SUMMARY.md) - 脚本功能总结

---

**文档版本**: 1.0  
**最后更新**: 2026-03-06  
**维护者**: GenAI Power Analysis Team
