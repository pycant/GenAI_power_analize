# 模型排除功能更新说明

## 更新日期
2024年（根据用户需求）

## 问题描述

在假设检验分析中发现 `qwen--qwen2.5-7b-instruct:8bit` 模型存在数据问题和缺失值，需要在所有分析脚本中将其排除。

## 影响的脚本

### 1. hypothesis_test_metric_tables.py
- **用途**: 检验同一任务下不同模型间GPU能耗差异
- **图表输出**: `energy_by_model_<task>.png`

### 2. raw_data_analysis.py
- **用途**: 原始数据深度分析，包括假设检验
- **图表输出**: `09_energy_by_model_boxplot.png` (即 `hypothesis_model_boxplot.png`)

## 实施的修改

### 共同修改点

#### 1. 在 `__init__` 方法中添加排除列表

```python
# 需要排除的模型（存在数据问题和缺失值）
self.excluded_models = [
    'qwen--qwen2.5-7b-instruct:8bit',
    'qwen2.5-7b-instruct:8bit'
]

self.excluded_count = 0
logger.info(f"排除的模型: {', '.join(self.excluded_models)}")
```

#### 2. 添加模型排除检查方法

```python
def _should_exclude_model(self, model_name: str) -> bool:
    """检查模型是否应该被排除"""
    model_name_lower = model_name.lower()
    for excluded in self.excluded_models:
        if excluded.lower() in model_name_lower:
            return True
    return False
```

#### 3. 在数据加载时过滤

```python
def load_all_raw_data(self):
    for exp in data:
        exp['model_name'] = self._extract_model_name(exp['config']['model'])
        
        # 检查是否为需要排除的模型
        if self._should_exclude_model(exp['model_name']):
            self.excluded_count += 1
            continue
        
        self.experiments.append(exp)
    
    if self.excluded_count > 0:
        logger.info(f"排除了 {self.excluded_count} 个问题模型的实验数据")
```

#### 4. 在分析方法中再次检查

在以下方法中添加了排除检查：
- `_test_energy_across_tasks()` - 任务间能耗差异检验
- `_test_energy_across_models()` - 模型间能耗差异检验
- `_test_interaction_effects()` - 交互效应检验
- `test_energy_across_models_by_task()` - 按任务的模型间差异检验

```python
for exp in self.experiments:
    model = exp['model_name']
    
    # 再次确认不包含排除的模型
    if self._should_exclude_model(model):
        continue
    
    # 继续处理...
```

#### 5. 更新报告生成

在生成的报告中添加数据说明部分：

```markdown
## 数据说明

- **数据来源**: 原始实验数据 (raw.json)
- **排除的模型**: qwen--qwen2.5-7b-instruct:8bit, qwen2.5-7b-instruct:8bit (存在数据问题和缺失值)
- **排除的实验数**: X
- **有效实验数**: Y
```

## 排除机制的工作原理

### 多层防护

1. **数据加载层**: 在 `load_all_raw_data()` 中首次过滤，不将问题模型的数据加入 `self.experiments`
2. **分析处理层**: 在各个分析方法中再次检查，确保没有遗漏
3. **日志记录层**: 记录排除的实验数量，便于追踪
4. **报告文档层**: 在生成的报告中明确说明排除的模型和原因

### 灵活的模式匹配

排除检查使用不区分大小写的子串匹配：
```python
model_name_lower = model_name.lower()
for excluded in self.excluded_models:
    if excluded.lower() in model_name_lower:
        return True
```

这样可以匹配各种命名变体：
- `qwen--qwen2.5-7b-instruct:8bit`
- `Qwen--Qwen2.5-7B-Instruct:8bit`
- `HF:qwen2.5-7b-instruct:8bit`

## 验证方法

### 1. 检查日志输出

运行脚本后查看日志：
```
排除的模型: qwen--qwen2.5-7b-instruct:8bit, qwen2.5-7b-instruct:8bit
排除了 X 个问题模型的实验数据
总共加载 Y 个实验
```

### 2. 检查生成的图表

查看以下图表，确认不包含被排除的模型：
- `analysis/qe_research/results/raw_analysis/figures/09_energy_by_model_boxplot.png`
- `analysis/qe_research/results/raw_analysis/figures/energy_by_model_<task>.png`

### 3. 检查CSV文件

查看描述性统计文件，确认模型列表中不包含被排除的模型：
- `energy_by_model_descriptive.csv`
- `energy_by_model_<task>_descriptive.csv`

### 4. 检查报告

查看生成的Markdown报告，确认包含排除说明：
- `hypothesis_testing_report.md`
- `GPU_ENERGY_MODEL_HYPOTHESIS_TESTING_REPORT.md`

## 如何添加更多排除模型

如果需要排除其他模型，只需在 `__init__` 方法中的 `excluded_models` 列表添加：

```python
self.excluded_models = [
    'qwen--qwen2.5-7b-instruct:8bit',
    'qwen2.5-7b-instruct:8bit',
    'another-problematic-model',  # 添加新的排除模型
]
```

## 注意事项

1. **模型名称匹配**: 排除列表中的名称应该是模型名称的关键部分，能够唯一标识该模型
2. **大小写不敏感**: 匹配时会转换为小写，因此不需要担心大小写问题
3. **子串匹配**: 使用 `in` 操作符，因此可以使用部分名称
4. **日志追踪**: 始终检查日志确认排除是否生效
5. **报告透明**: 所有排除操作都会在报告中明确说明

## 影响范围

### 受影响的分析

- ✅ 任务间GPU能耗差异检验
- ✅ 模型间GPU能耗差异检验
- ✅ 任务×模型交互效应分析
- ✅ 按任务的模型间差异检验
- ✅ 所有相关的描述性统计
- ✅ 所有相关的可视化图表
- ✅ 所有生成的报告文档

### 不受影响的分析

- 其他不涉及模型比较的分析（如时间序列分析、TTFT分析等）仍会包含所有模型的数据

## 运行脚本

### hypothesis_test_metric_tables.py
```bash
python analysis/qe_research/scripts/hypothesis_test_metric_tables.py
# 或
analysis/qe_research/scripts/run_hypothesis_test_metric_tables.bat
```

### raw_data_analysis.py
```bash
python analysis/qe_research/scripts/raw_data_analysis.py
# 或
analysis/qe_research/scripts/run_raw_analysis.bat
```

## 相关文档

- `HYPOTHESIS_TEST_METRIC_TABLES_FIX.md` - 假设检验脚本修复说明
- `假设检验功能说明.md` - 假设检验功能总体说明
- `HYPOTHESIS_TESTING_GUIDE.md` - 假设检验使用指南

## 总结

通过在两个关键脚本中实施一致的模型排除机制，确保了：

1. **数据质量**: 排除有问题的模型数据，提高分析可靠性
2. **透明度**: 在日志和报告中明确说明排除操作
3. **一致性**: 所有相关分析使用相同的排除逻辑
4. **可维护性**: 集中管理排除列表，易于更新
5. **可追溯性**: 完整的日志记录便于审计和验证
