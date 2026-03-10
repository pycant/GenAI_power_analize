# PCA绘图功能实现总结

**实现时间**: 2024-01-XX  
**实现内容**: 在 `shared_functions.py` 中添加 `plot_pca_figures()` 函数，并集成到 `load_process_quality_data()` 的PCA模式中

---

## 1. 新增函数：`plot_pca_figures()`

### 函数签名
```python
def plot_pca_figures(pca_result, task_name, output_dir, n_components_to_show=None)
```

### 功能说明
该函数为PCA分析生成4类可视化图表，帮助理解主成分分析的结果：

#### 图表1: 解释方差比例柱状图
- **文件名**: `{task_name}_pca_explained_variance.png`
- **内容**: 显示每个主成分的解释方差比例
- **用途**: 快速了解各主成分的重要性

#### 图表2: 累积解释方差曲线图
- **文件名**: `{task_name}_pca_cumulative_variance.png`
- **内容**: 显示累积解释方差随主成分数量的变化
- **特点**: 包含85%阈值线，标注每个点的累积方差百分比
- **用途**: 确定需要保留的主成分数量

#### 图表3: 主成分载荷图
- **文件名**: `{task_name}_pca_loadings.png`
- **内容**: 显示前3个主成分的载荷分布（仅显示|载荷|>0.2的指标）
- **特点**: 
  - 正载荷用深蓝色表示
  - 负载荷用深红色表示
  - 每个子图标注该主成分的解释方差
- **用途**: 理解各指标对主成分的贡献方向和强度

#### 图表4: 双标图（Biplot）
- **文件名**: `{task_name}_pca_biplot.png`
- **内容**: 在PC1-PC2平面上同时显示模型位置和指标向量
- **特点**:
  - 模型用蓝色散点表示，带标签
  - 指标用红色箭头表示（仅显示载荷最大的前10个）
  - 箭头长度和方向反映指标对主成分的贡献
- **用途**: 直观理解模型在主成分空间的分布和指标的影响方向
- **条件**: 仅当主成分数≥2时生成

### 参数说明
- `pca_result` (dict): PCA结果字典，由 `QualityDataProcessor.apply_pca()` 返回
  - `'transformed'`: 降维后的数据（DataFrame）
  - `'components'`: 主成分载荷矩阵（DataFrame）
  - `'explained_variance_ratio'`: 解释方差比例（array）
  - `'cumulative_variance_ratio'`: 累积方差比例（array）
  - `'n_components'`: 实际主成分数量
- `task_name` (str): 任务名称，用于文件命名
- `output_dir` (str or Path): 输出目录路径
- `n_components_to_show` (int, optional): 要显示的主成分数量，默认为全部

### 返回值
- `list`: 生成的图表文件路径列表

---

## 2. 集成到 `load_process_quality_data()`

### 修改位置
在 `load_process_quality_data()` 函数的 `elif method == 'pca':` 分支中，添加了对 `plot_pca_figures()` 的调用。

### 调用时机
在完成PCA降维并选择主成分数量后，自动调用绘图函数：

```python
# 绘制PCA可视化图表
if verbose:
    print(f"\n生成PCA可视化图表...")
plot_pca_figures(pca_result_full, task_name, output_dir, n_components_to_show=min(5, n_components_selected))
```

### 参数传递
- `pca_result_full`: 完整的PCA结果（包含所有主成分）
- `task_name`: 当前任务名称
- `output_dir`: 从函数参数传入的输出目录
- `n_components_to_show`: 显示前5个主成分或实际选择的主成分数（取较小值）

---

## 3. 使用示例

### 示例1: 基础使用
```python
from analysis.qe_research.scripts.pareto_core.shared_functions import load_process_quality_data

# 使用PCA模式加载数据（自动生成图表）
quality_df = load_process_quality_data(
    task_name='code',
    method='pca',
    normalize_method='minmax',
    use_raw=True,
    verbose=True,
    output_dir='./pca_figures'
)

# 图表将自动保存到 ./pca_figures/ 目录
# - code_pca_explained_variance.png
# - code_pca_cumulative_variance.png
# - code_pca_loadings.png
# - code_pca_biplot.png
```

### 示例2: 在帕累托分析中使用
```python
from analysis.qe_research.scripts.pareto_core.shared_functions import (
    load_process_quality_data,
    merge_quality_metrics,
    identify_pareto_frontier_2d
)

# 加载质量数据（使用PCA）
quality_df = load_process_quality_data(
    task_name='creative',
    method='pca',
    output_dir='./results/creative/pca_analysis'
)

# 合并能耗和速度数据
merged_df = merge_quality_metrics(
    quality_df, 
    energy_dict, 
    speed_dict, 
    MODEL_MAPPING
)

# 识别帕累托前沿
pareto_mask = identify_pareto_frontier_2d(
    merged_df, 
    'energy', 
    'quality',
    x_minimize=True, 
    y_minimize=False
)
```

### 示例3: 单独调用绘图函数
```python
from analysis.qe_research.scripts.pareto_core.process_quality_data import QualityDataProcessor
from analysis.qe_research.scripts.pareto_core.shared_functions import plot_pca_figures

# 手动执行PCA
processor = QualityDataProcessor(task_name='math')
data = processor.load_quality_data()
pca_result = processor.apply_pca(n_components=None, normalize_first=True)

# 单独调用绘图函数
saved_files = plot_pca_figures(
    pca_result=pca_result,
    task_name='math',
    output_dir='./custom_output',
    n_components_to_show=3
)

print(f"生成的图表: {saved_files}")
```

---

## 4. 测试脚本

创建了测试脚本 `test_pca_plotting.py` 用于验证功能：

```bash
# 运行测试
cd analysis/qe_research/scripts/pareto_core
python test_pca_plotting.py
```

测试脚本会：
1. 对 code、creative、math 三个任务执行PCA分析
2. 自动生成所有PCA可视化图表
3. 验证图表文件是否成功创建
4. 输出质量得分的统计信息

---

## 5. 技术细节

### 中文字体支持
函数内部自动设置中文字体，支持：
- Microsoft YaHei（微软雅黑）
- SimHei（黑体）
- Arial Unicode MS

### 图表配色
- 解释方差图：钢蓝色（steelblue）
- 累积方差图：深绿色（darkgreen）
- 载荷图：深蓝色（正载荷）/ 深红色（负载荷）
- 双标图：钢蓝色（模型点）/ 红色（指标向量）

### 载荷阈值
- 载荷图仅显示 |载荷| > 0.2 的指标
- 双标图仅显示载荷最大的前10个指标

### 图表分辨率
所有图表均以300 DPI保存，确保打印质量

---

## 6. 文件结构

```
analysis/qe_research/scripts/pareto_core/
├── shared_functions.py              # 主函数文件（已修改）
│   ├── plot_pca_figures()          # 新增：PCA绘图函数
│   └── load_process_quality_data() # 已修改：集成PCA绘图
├── process_quality_data.py          # PCA处理模块（未修改）
├── test_pca_plotting.py             # 新增：测试脚本
└── PCA_PLOTTING_IMPLEMENTATION.md   # 本文档
```

---

## 7. 注意事项

### 依赖项
确保已安装以下Python包：
- `matplotlib` >= 3.5.0
- `numpy` >= 1.21.0
- `pandas` >= 1.3.0
- `scikit-learn` >= 1.0.0

### 输出目录
- 函数会自动创建输出目录（如果不存在）
- 建议为每个任务使用独立的输出目录

### 主成分数量
- 函数自动选择累积解释方差≥85%的主成分
- 至少保留1个主成分
- 可通过 `n_components_to_show` 参数控制显示数量

### 双标图限制
- 仅当主成分数≥2时生成双标图
- 如果只有1个主成分，会跳过双标图生成

---

## 8. 后续改进建议

### 功能增强
1. 添加3D双标图（PC1-PC2-PC3）
2. 支持自定义配色方案
3. 添加交互式图表（使用plotly）
4. 支持导出图表为SVG格式

### 性能优化
1. 对大规模数据集优化绘图性能
2. 添加图表缓存机制
3. 支持并行生成多个图表

### 文档完善
1. 添加更多使用示例
2. 补充图表解读指南
3. 提供常见问题解答

---

## 9. 相关文档

- [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 快速参考指南
- [process_quality_data.py](./process_quality_data.py) - 质量数据处理模块
- [TASK_METRICS_MAPPING.md](../../results/quality_scores/TASK_METRICS_MAPPING.md) - 任务指标映射表

---

**实现完成** ✓

所有功能已实现并通过测试，可以在帕累托分析中使用PCA模式并自动生成可视化图表。
