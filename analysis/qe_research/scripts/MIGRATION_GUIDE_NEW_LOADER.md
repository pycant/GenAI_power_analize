# 迁移指南：使用新的 load_process_quality_data() 函数

## 概述

本指南说明如何将现有的帕累托分析脚本迁移到使用新的 `load_process_quality_data()` 统一数据加载接口。

## 迁移优势

- ✅ 统一接口：所有任务使用相同的数据加载方式
- ✅ 灵活配置：支持多种质量处理方法（熵权法、单一指标、PCA等）
- ✅ 代码简化：减少重复代码，提高可维护性
- ✅ 自动处理：自动归一化、权重计算、数据合并
- ✅ 易于切换：通过配置参数轻松切换不同方法

## 迁移步骤

### 步骤1: 更新导入语句

**旧版本：**
```python
from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d, identify_pareto_frontier_3d,
    calculate_hypervolume, calculate_spacing, find_knee_point,
    plot_pareto_2d, load_energy_speed_data, merge_quality_metrics,
    perturbation_analysis, cross_validation_pareto,
    generate_pareto_report, print_analysis_summary
)
```

**新版本：**
```python
from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d, identify_pareto_frontier_3d,
    calculate_hypervolume, calculate_spacing, find_knee_point,
    plot_pareto_2d, load_energy_speed_data, load_process_quality_data,  # 新增
    perturbation_analysis, cross_validation_pareto,
    generate_pareto_report, print_analysis_summary
)
```

### 步骤2: 添加任务配置

在文件顶部添加配置常量：

```python
# 任务配置
TASK_NAME = 'summary'  # 任务名称
QUALITY_METHOD = 'entropy'  # 质量处理方法
QUALITY_METRIC_NAME = 'ROUGE-L得分'  # 质量指标显示名称

OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / TASK_NAME
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
```

### 步骤3: 替换数据加载函数

**旧版本：**
```python
def load_and_prepare_data():
    """加载并准备数据"""
    print("\n" + "="*80)
    print("加载数据：摘要任务")
    print("="*80)
    
    # 手动加载质量数据
    quality_df = pd.read_csv(QUALITY_FILE)
    quality_data = pd.DataFrame({
        'model': quality_df['model'],
        'quality': quality_df['quality']
    })
    print(f"✓ 质量数据: {len(quality_data)} 个模型")
    
    # 加载能耗和速度
    energy_dict, speed_dict = load_energy_speed_data('summary', DATA_PATHS['energy'], DATA_PATHS['speed'])
    
    # 手动合并
    df = merge_quality_metrics(quality_data, energy_dict, speed_dict, MODEL_MAPPING, 'quality')
    
    return df
```

**新版本：**
```python
def load_and_prepare_data():
    """加载并准备数据"""
    print("\n" + "="*80)
    print(f"加载数据：{TASK_NAME.upper()}任务")
    print("="*80)
    
    # 1. 使用新的统一接口加载质量数据
    print(f"\n步骤1: 加载质量数据（方法: {QUALITY_METHOD}）")
    quality_df = load_process_quality_data(
        task_name=TASK_NAME,
        method=QUALITY_METHOD,
        normalize_method='minmax',
        use_raw=True,
        verbose=True
    )
    
    # 2. 加载能耗和速度数据
    print(f"\n步骤2: 加载能耗和速度数据")
    energy_dict, speed_dict = load_energy_speed_data(
        TASK_NAME, 
        DATA_PATHS['energy'], 
        DATA_PATHS['speed']
    )
    
    # 3. 合并数据
    print(f"\n步骤3: 合并质量、能耗、速度数据")
    merged_data = []
    for _, row in quality_df.iterrows():
        model_short = row['model']
        model_full = MODEL_MAPPING.get(model_short)
        
        if model_full and model_full in energy_dict and model_full in speed_dict:
            merged_data.append({
                'model': model_short,
                'model_full': model_full,
                'quality': row['quality'],
                'energy': energy_dict[model_full],
                'speed': speed_dict[model_full]
            })
    
    df = pd.DataFrame(merged_data)
    print(f"✓ 合并后数据: {len(df)} 个模型")
    
    # 4. 保存合并数据
    merged_file = OUTPUT_DIR / 'merged_data.csv'
    df.to_csv(merged_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 合并数据已保存: {merged_file}")
    
    return df
```

### 步骤4: 更新主函数

在主函数开头添加配置信息输出：

```python
def main():
    """主函数"""
    print("\n" + "="*80)
    print(f"{TASK_NAME.upper()}任务帕累托前沿分析（重构版 - 使用新数据加载器）")
    print("="*80)
    print(f"质量处理方法: {QUALITY_METHOD}")
    print(f"质量指标名称: {QUALITY_METRIC_NAME}")
    print("="*80)
    
    # ... 其余代码
```

## 不同任务的配置示例

### Code 任务

```python
# 任务配置
TASK_NAME = 'code'
QUALITY_METHOD = 'entropy'  # 或 'single' 使用编译成功率
QUALITY_METRIC_NAME = '编译成功率'

# 如果使用单一指标
# 在 load_process_quality_data() 中添加:
# quality_column='compilation_rate'
```

### Creative 任务

```python
# 任务配置
TASK_NAME = 'creative'
QUALITY_METHOD = 'entropy'  # 推荐使用熵权法
QUALITY_METRIC_NAME = '创意质量得分'
```

### QA 任务

```python
# 任务配置
TASK_NAME = 'qa'
QUALITY_METHOD = 'entropy'
QUALITY_METRIC_NAME = 'QA质量得分'
```

### Reasoning 任务

```python
# 任务配置
TASK_NAME = 'reasoning'
QUALITY_METHOD = 'entropy'  # 或 'pca' 用于降维
QUALITY_METRIC_NAME = '推理质量得分'
```

### Math 任务

```python
# 任务配置
TASK_NAME = 'math'
QUALITY_METHOD = 'single'  # 使用准确率
QUALITY_METRIC_NAME = '数学准确率'

# 在 load_process_quality_data() 中添加:
# quality_column='accuracy'
```

### Translation 任务

```python
# 任务配置
TASK_NAME = 'translation'
QUALITY_METHOD = 'single'  # 使用BLEU分数
QUALITY_METRIC_NAME = 'BLEU分数'

# 在 load_process_quality_data() 中添加:
# quality_column='bleu_score'
```

## 质量处理方法选择指南

### 1. 熵权法（entropy）- 默认推荐

```python
QUALITY_METHOD = 'entropy'

quality_df = load_process_quality_data(
    task_name=TASK_NAME,
    method='entropy',
    normalize_method='minmax',
    verbose=True
)
```

**适用场景**：
- 多个质量指标需要综合评价
- 需要客观赋权
- 指标间相互独立

### 2. 单一指标（single）

```python
QUALITY_METHOD = 'single'

quality_df = load_process_quality_data(
    task_name=TASK_NAME,
    method='single',
    quality_column='compilation_rate',  # 指定具体指标
    verbose=True
)
```

**适用场景**：
- 有明确的核心质量指标
- Code任务的编译成功率
- Math任务的准确率
- Translation任务的BLEU分数

### 3. PCA降维（pca）

```python
QUALITY_METHOD = 'pca'

quality_df = load_process_quality_data(
    task_name=TASK_NAME,
    method='pca',
    n_components=1,  # 使用第一主成分
    verbose=True
)
```

**适用场景**：
- 指标间高度相关
- 需要降维处理
- Reasoning任务的多维推理指标

### 4. 简单平均（mean）

```python
QUALITY_METHOD = 'mean'

quality_df = load_process_quality_data(
    task_name=TASK_NAME,
    method='mean',
    normalize_method='minmax',
    verbose=True
)
```

**适用场景**：
- 快速评估
- 指标重要性相近
- 基线对比

### 5. 自定义权重（custom）

```python
QUALITY_METHOD = 'custom'

custom_weights = {
    'compilation_rate': 0.5,
    'test_pass_rate': 0.3,
    'code_length': 0.2
}

quality_df = load_process_quality_data(
    task_name=TASK_NAME,
    method='custom',
    weights=custom_weights,
    verbose=True
)
```

**适用场景**：
- 有专家经验或领域知识
- 特定应用场景的权重偏好
- 与熵权法对比验证

## 完整迁移示例

### 迁移前（旧版本）

```python
"""
摘要任务帕累托前沿分析
"""

import sys
from pathlib import Path
import pandas as pd

from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d,
    load_energy_speed_data, merge_quality_metrics
)

QUALITY_FILE = PROJECT_ROOT / 'data' / 'analize' / 'results' / 'summary_quality' / 'summary_quality_processed.csv'
OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / 'summary'

def load_and_prepare_data():
    quality_df = pd.read_csv(QUALITY_FILE)
    quality_data = pd.DataFrame({
        'model': quality_df['model'],
        'quality': quality_df['quality']
    })
    
    energy_dict, speed_dict = load_energy_speed_data('summary', DATA_PATHS['energy'], DATA_PATHS['speed'])
    df = merge_quality_metrics(quality_data, energy_dict, speed_dict, MODEL_MAPPING, 'quality')
    
    return df

def main():
    df = load_and_prepare_data()
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', x_minimize=False, y_minimize=True)
    print(f"前沿模型: {pareto_qe.sum()}")

if __name__ == '__main__':
    main()
```

### 迁移后（新版本）

```python
"""
摘要任务帕累托前沿分析（使用新数据加载器）
"""

import sys
from pathlib import Path
import pandas as pd

from pareto_core import (
    MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
    identify_pareto_frontier_2d,
    load_energy_speed_data, load_process_quality_data  # 新增
)

# 任务配置
TASK_NAME = 'summary'
QUALITY_METHOD = 'entropy'
QUALITY_METRIC_NAME = 'ROUGE-L得分'

OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / TASK_NAME
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_and_prepare_data():
    # 使用新接口加载质量数据
    quality_df = load_process_quality_data(
        task_name=TASK_NAME,
        method=QUALITY_METHOD,
        normalize_method='minmax',
        verbose=True
    )
    
    # 加载能耗和速度
    energy_dict, speed_dict = load_energy_speed_data(
        TASK_NAME, DATA_PATHS['energy'], DATA_PATHS['speed']
    )
    
    # 合并数据
    merged_data = []
    for _, row in quality_df.iterrows():
        model_short = row['model']
        model_full = MODEL_MAPPING.get(model_short)
        
        if model_full and model_full in energy_dict and model_full in speed_dict:
            merged_data.append({
                'model': model_short,
                'model_full': model_full,
                'quality': row['quality'],
                'energy': energy_dict[model_full],
                'speed': speed_dict[model_full]
            })
    
    return pd.DataFrame(merged_data)

def main():
    print(f"\n{TASK_NAME.upper()}任务帕累托分析")
    print(f"质量方法: {QUALITY_METHOD}")
    
    df = load_and_prepare_data()
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', x_minimize=False, y_minimize=True)
    print(f"前沿模型: {pareto_qe.sum()}")

if __name__ == '__main__':
    main()
```

## 迁移检查清单

- [ ] 更新导入语句，添加 `load_process_quality_data`
- [ ] 添加任务配置常量（TASK_NAME, QUALITY_METHOD, QUALITY_METRIC_NAME）
- [ ] 替换 `load_and_prepare_data()` 函数
- [ ] 更新主函数，添加配置信息输出
- [ ] 删除旧的 QUALITY_FILE 常量
- [ ] 测试运行，确保输出正确
- [ ] 更新文档字符串，说明使用新加载器

## 常见问题

### Q1: 如何查看某个任务有哪些可用的质量指标？

```python
from pareto_core.process_quality_data import QualityDataProcessor

processor = QualityDataProcessor(task_name='code')
data = processor.load_quality_data()
print("可用指标:", list(data.columns))
```

### Q2: 如何对比不同质量处理方法的结果？

```python
methods = ['entropy', 'mean', 'pca']
results = {}

for method in methods:
    quality_df = load_process_quality_data(
        task_name='code',
        method=method,
        verbose=False
    )
    results[method] = quality_df

# 对比分析
```

### Q3: 迁移后结果与旧版本不一致？

可能原因：
1. 熵权法与旧方法的权重不同
2. 归一化方法不同
3. 数据源文件更新

解决方案：
- 使用 `method='single'` 指定与旧版本相同的单一指标
- 检查归一化方法是否一致
- 对比原始数据文件

### Q4: 如何保持向后兼容？

在迁移期间，可以同时保留旧版本函数：

```python
def load_and_prepare_data_old():
    """旧版本数据加载（保留用于对比）"""
    # ... 旧代码

def load_and_prepare_data():
    """新版本数据加载"""
    # ... 新代码

# 在main中可以选择使用哪个版本
USE_NEW_LOADER = True
df = load_and_prepare_data() if USE_NEW_LOADER else load_and_prepare_data_old()
```

## 相关文档

- [load_process_quality_data() 使用指南](pareto_core/LOAD_PROCESS_QUALITY_DATA_GUIDE.md)
- [质量数据处理详细指南](pareto_core/QUALITY_DATA_PROCESSING_GUIDE.md)
- [帕累托分析脚本总结](PARETO_SCRIPTS_SUMMARY.md)

## 已迁移的脚本

- ✅ `pareto_analysis_summary.py` - 摘要任务（示例）

## 待迁移的脚本

- [ ] `pareto_analysis_code.py` - 代码任务
- [ ] `pareto_analysis_creative.py` - 创意任务
- [ ] `pareto_analysis_qa.py` - 问答任务
- [ ] `pareto_analysis_reasoning.py` - 推理任务
- [ ] `pareto_analysis_math.py` - 数学任务
- [ ] `pareto_analysis_translation.py` - 翻译任务

---

**更新日期**: 2026-03-07  
**版本**: v1.0.0
