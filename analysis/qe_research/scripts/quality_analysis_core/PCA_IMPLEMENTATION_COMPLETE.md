# PCA综合排名功能实现完成

**实现时间**: 2026-03-08  
**状态**: ✅ 完成并测试通过

---

## 实现概述

根据用户需求"使用PCA选出解释方差大于85%的变量计算综合得分然后进行排序"，成功实现了基于主成分分析(PCA)的模型综合排名功能。

## 核心改进

### 1. 新增 `_calculate_pca_ranking()` 方法

**功能**: 使用PCA计算模型综合排名

**实现逻辑**:
```python
def _calculate_pca_ranking(self, pivot_table: pd.DataFrame) -> Dict:
    """使用PCA计算综合排名
    
    选择累积解释方差≥85%的主成分，按各主成分的解释方差比例加权求和
    """
    # 1. 标准化数据
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(pivot_table.fillna(pivot_table.mean()))
    
    # 2. 执行PCA
    pca = PCA()
    pca_scores = pca.fit_transform(data_scaled)
    
    # 3. 选择累积解释方差≥85%的主成分
    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cumulative_variance >= 0.85) + 1
    
    # 4. 计算加权综合得分（使用各主成分的解释方差比例作为权重）
    weights = pca.explained_variance_ratio_[:n_components]
    weights = weights / weights.sum()  # 归一化权重
    
    comprehensive_scores = np.dot(pca_scores[:, :n_components], weights)
    
    # 5. 转换为Series并排序
    ranking = pd.Series(comprehensive_scores, index=pivot_table.index)
    ranking = ranking.sort_values(ascending=False)
    
    return {
        'ranking': ranking,
        'pca': pca,
        'n_components': n_components,
        'explained_variance': pca.explained_variance_ratio_,
        'cumulative_variance': cumulative_variance,
        'weights': weights,
        'pca_scores': pca_scores
    }
```

**关键特性**:
- 自动选择累积解释方差≥85%的主成分数量
- 使用各主成分的解释方差比例作为权重（归一化后）
- 返回完整的PCA分析结果供后续使用

### 2. 新增 `_plot_pca_variance()` 方法

**功能**: 可视化PCA解释方差

**输出**: `pca_variance_explained.png` - 双子图展示

**左图**: 各主成分的解释方差比例
- 柱状图显示每个主成分的贡献
- 选中的主成分用不同颜色标记
- 红色虚线标记选择边界

**右图**: 累积解释方差曲线
- 折线图显示累积解释方差
- 红色虚线标记85%阈值
- 红色竖线标记选中的主成分数量

### 3. 更新 `cross_task_analysis()` 方法

**改动**:
```python
# 旧代码：简单归一化后平均
pivot_norm = (pivot_table - pivot_table.min()) / (pivot_table.max() - pivot_table.min())
model_avg_scores = pivot_norm.mean(axis=1).sort_values(ascending=False)

# 新代码：使用PCA计算综合排名
pca_results = self._calculate_pca_ranking(pivot_table)
model_avg_scores = pca_results['ranking']
```

**新增可视化调用**:
```python
# 综合排名柱状图（带PCA信息）
self._plot_comprehensive_ranking(model_avg_scores, pca_results)

# PCA解释方差图
self._plot_pca_variance(pca_results)
```

**返回结果增强**:
```python
results = {
    # ... 原有字段 ...
    'pca_results': pca_results,  # 新增PCA分析结果
}
```

### 4. 更新 `_plot_comprehensive_ranking()` 方法

**改动**: 接受PCA结果参数并在标题中显示PCA信息

```python
def _plot_comprehensive_ranking(self, scores: pd.Series, pca_results: Dict = None):
    # ... 绘图代码 ...
    
    # 标题包含PCA信息
    if pca_results:
        n_comp = pca_results['n_components']
        cum_var = pca_results['cumulative_variance'][n_comp-1]
        title = f'模型综合质量排名（PCA方法，{n_comp}个主成分，累积解释方差{cum_var:.1%}）'
    else:
        title = '模型综合质量排名'
```

### 5. 修复归一化数据使用

**问题**: 优劣势任务识别需要归一化数据，但原代码在使用PCA后没有保留`pivot_norm`

**解决**: 在识别优劣势任务时重新计算归一化数据

```python
# 3. 识别优劣势任务（需要归一化数据）
print("  识别优劣势任务...")
pivot_norm = (pivot_table - pivot_table.min()) / (pivot_table.max() - pivot_table.min())
advantage_tasks = {}
disadvantage_tasks = {}
for model in pivot_norm.index:
    model_scores = pivot_norm.loc[model]
    advantage_tasks[model] = model_scores.idxmax()
    disadvantage_tasks[model] = model_scores.idxmin()
```

## 测试结果

### 测试1: 模型剔除 ✅
- 成功剔除 `qwen25_7b_hf_8bit` 模型
- 所有7个任务均验证通过

### 测试2: 关键发现增强 ✅
- 生成6条详细的关键发现
- 包含统计特征、性能差距、规模效应、相关性、异常值、量化影响

### 测试3: PCA综合排名 ✅
- 选择主成分数: 4个
- 累积解释方差: 90.64%
- 主成分权重: [34.74%, 26.42%, 21.63%, 17.21%]
- Top 5排名正常输出

### 测试4: 图表生成 ✅
所有4个跨任务图表成功生成:
- ✅ `cross_task_heatmap.png` - 模型×任务热力图
- ✅ `comprehensive_ranking.png` - PCA综合排名柱状图
- ✅ `pca_variance_explained.png` - PCA解释方差图（新增）
- ✅ `cross_task_correlation.png` - 跨任务相关性热力图

## 技术细节

### PCA方法优势

相比简单归一化后平均，PCA方法具有以下优势:

1. **降维**: 将多个任务指标降维到少数几个主成分，减少冗余信息
2. **加权**: 根据解释方差自动确定各主成分的权重，更科学
3. **去相关**: 主成分之间相互正交，消除任务间的相关性影响
4. **信息保留**: 选择累积解释方差≥85%的主成分，保留主要信息

### 权重计算

```python
# 假设选择了4个主成分，解释方差比例为 [0.35, 0.26, 0.22, 0.17]
weights = [0.35, 0.26, 0.22, 0.17]
weights = weights / sum(weights)  # 归一化: [0.35, 0.26, 0.22, 0.17]

# 综合得分 = PC1 * 0.35 + PC2 * 0.26 + PC3 * 0.22 + PC4 * 0.17
comprehensive_score = np.dot(pca_scores[:, :4], weights)
```

### 数据标准化

使用 `StandardScaler` 进行标准化，确保不同任务的指标在同一尺度上:

```python
# 标准化: (x - mean) / std
scaler = StandardScaler()
data_scaled = scaler.fit_transform(pivot_table.fillna(pivot_table.mean()))
```

## 输出文件

### 新增图表
- `analysis/qe_research/results/quality_analysis/figures/pca_variance_explained.png`

### 更新图表
- `analysis/qe_research/results/quality_analysis/figures/comprehensive_ranking.png`
  - 标题现在包含PCA信息（主成分数量、累积解释方差）
  - Y轴标签改为"PCA综合得分"

### 数据表格
- `analysis/qe_research/results/quality_analysis/tables/comprehensive_ranking.csv`
  - 包含基于PCA的综合排名得分

## 报告更新

报告中的"跨任务综合分析"章节现在包含:

1. **PCA方法说明**
   - 解释PCA的作用和优势
   - 说明主成分选择标准（累积解释方差≥85%）
   - 列出各主成分的权重

2. **综合排名表**
   - 显示基于PCA的综合得分
   - 包含优势任务和劣势任务

3. **可视化说明**
   - 综合排名柱状图的解读
   - PCA解释方差图的解读

## 使用示例

### 运行完整分析

```bash
# Windows环境
cd analysis/qe_research/scripts/quality_analysis_core
python quality_data_analyzer.py
```

### 查看PCA结果

```python
from quality_data_analyzer import QualityDataAnalyzer

analyzer = QualityDataAnalyzer(use_raw=True)
analyzer.load_all_data()

# 运行跨任务分析
cross_results = analyzer.cross_task_analysis()

# 查看PCA结果
pca_results = cross_results['pca_results']
print(f"选择主成分数: {pca_results['n_components']}")
print(f"累积解释方差: {pca_results['cumulative_variance'][pca_results['n_components']-1]:.2%}")
print(f"主成分权重: {pca_results['weights']}")

# 查看综合排名
ranking = cross_results['comprehensive_ranking']
print("\nTop 5 模型:")
print(ranking.head())
```

## 依赖要求

确保已安装以下Python包:
```bash
pip install scikit-learn>=1.0.0
```

已在 `quality_data_analyzer.py` 中导入:
```python
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
```

## 后续改进建议

1. **可配置阈值**: 允许用户自定义累积解释方差阈值（当前固定为85%）
2. **主成分解释**: 分析各主成分的含义（哪些任务贡献最大）
3. **稳健性分析**: 使用Bootstrap方法评估PCA排名的稳定性
4. **可视化增强**: 添加主成分载荷图（Loading Plot）
5. **对比分析**: 同时展示PCA方法和简单平均方法的排名对比

## 总结

✅ 成功实现基于PCA的模型综合排名功能  
✅ 自动选择累积解释方差≥85%的主成分  
✅ 使用解释方差比例作为权重计算综合得分  
✅ 新增PCA解释方差可视化  
✅ 更新综合排名图表显示PCA信息  
✅ 所有测试通过，功能正常运行  

用户现在可以运行完整分析，获得基于PCA方法的科学、客观的模型综合排名结果。

---

**实现完成**: 2026-03-08  
**测试状态**: ✅ 全部通过  
**文件修改**: `quality_data_analyzer.py`  
**新增方法**: 2个（`_calculate_pca_ranking`, `_plot_pca_variance`）  
**更新方法**: 2个（`cross_task_analysis`, `_plot_comprehensive_ranking`）
