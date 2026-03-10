# 任务级PCA综合排名功能更新

**更新时间**: 2026-03-08  
**状态**: ✅ 完成并测试通过

---

## 更新概述

根据用户需求，将单个任务的模型排名从"按单一指标排序"改为"使用PCA方法计算综合得分排序"。现在每个任务的模型排名都基于该任务的多个主要指标进行PCA降维和加权计算。

## 改进前后对比

### 改进前
```
模型排名（按distinct_2）
排名  模型                    得分
1     qwen_8b_ol_q4km        0.961
2     gemma_4b_ol_q4km       0.917
3     deepseek_8b_ol_q4km    0.899
...
```
- 只按单一指标（如distinct_2）排序
- 忽略了其他重要指标的信息
- 可能导致片面的评价

### 改进后
```
模型综合排名（PCA方法）

方法说明: 使用主成分分析(PCA)综合13个主要指标，
选择累积解释方差≥85%的前4个主成分，
实际累积解释方差为92.3%。

主成分权重:
- PC1: 38.5%
- PC2: 28.2%
- PC3: 15.8%
- PC4: 17.5%

排名  模型                    PCA综合得分
1     qwen_8b_ol_q4km        1.234
2     deepseek_8b_ol_q4km    0.987
3     gemma_4b_ol_q4km       0.856
...
```
- 综合考虑多个指标
- 使用PCA降维，保留主要信息
- 按解释方差加权，更科学
- 提供方法说明和权重信息

## 核心改动

### 1. 更新 `analyze_task()` 方法

**位置**: `quality_data_analyzer.py` 第152-180行

**改动内容**:
```python
# 旧代码：按单一指标排序
for metric in primary_metrics:
    if metric in df.columns:
        ranking = df[['model', metric]].sort_values(metric, ascending=False)
        results['model_rankings'][metric] = ranking

# 新代码：使用PCA计算综合排名
if len(primary_metrics) > 1:
    # 准备数据：只使用主要指标
    metrics_data = df[['model'] + [m for m in primary_metrics if m in df.columns]].copy()
    metrics_data = metrics_data.set_index('model')
    
    # 计算PCA综合排名
    pca_ranking_result = self._calculate_pca_ranking(metrics_data)
    
    # 保存PCA综合排名
    results['model_rankings']['pca_综合得分'] = pd.DataFrame({
        'model': pca_ranking_result['ranking'].index,
        'pca_综合得分': pca_ranking_result['ranking'].values
    })
    results['pca_ranking_info'] = {
        'n_components': pca_ranking_result['n_components'],
        'explained_variance': pca_ranking_result['explained_variance'],
        'cumulative_variance': pca_ranking_result['cumulative_variance'],
        'weights': pca_ranking_result['weights']
    }
```

**关键特性**:
- 当任务有多个主要指标时，使用PCA方法
- 当只有单一指标时，保持原有的直接排序
- 同时保留各单项指标的排名供参考

### 2. 新增 `_plot_task_pca_ranking()` 方法

**位置**: `quality_data_analyzer.py` 第540-580行

**功能**: 绘制任务级别的PCA综合排名柱状图

**特点**:
- 显示PCA综合得分的柱状图
- 标题包含PCA信息（主成分数量、累积解释方差）
- 为每个柱子添加数值标签
- 输出到任务专属的figures子目录

**输出示例**: `figures/creative/pca_ranking.png`

### 3. 更新 `_create_task_visualizations()` 方法

**位置**: `quality_data_analyzer.py` 第370-390行

**改动**:
```python
# 旧代码：绘制箱线图
if primary_metrics and primary_metrics[0] in df.columns:
    metric = primary_metrics[0]
    sf.plot_boxplot(df, metric, 'model', title, output_path)

# 新代码：优先绘制PCA排名图
if 'pca_综合得分' in results['model_rankings']:
    pca_ranking = results['model_rankings']['pca_综合得分']
    pca_info = results.get('pca_ranking_info', {})
    
    self._plot_task_pca_ranking(
        pca_ranking, 
        task_info['name_cn'], 
        task_figures_dir / 'pca_ranking.png',
        pca_info
    )
```

### 4. 更新报告生成 `_write_task_analyses()` 方法

**位置**: `quality_data_analyzer.py` 第960-1010行

**改动**: 优先显示PCA综合排名，包含方法说明和主成分权重

**报告内容**:
1. **方法说明**: 解释PCA方法、主成分数量、累积解释方差
2. **主成分权重**: 列出各主成分的权重比例
3. **排名表格**: 显示模型和PCA综合得分
4. **可视化说明**: 引用PCA排名图

## 技术细节

### PCA方法应用

对于每个任务：
1. **输入**: 该任务的所有主要指标（如creative任务的13个指标）
2. **标准化**: 使用StandardScaler进行Z-score标准化
3. **PCA降维**: 自动选择累积解释方差≥85%的主成分
4. **加权求和**: 使用各主成分的解释方差比例作为权重
5. **排序**: 按综合得分从高到低排序

### 示例：Creative任务

假设creative任务有13个指标：
- distinct_1, distinct_2, distinct_3
- bleu_score, rouge_1, rouge_2, rouge_l
- perplexity, coherence_score
- creativity_score, originality_score
- fluency_score, relevance_score

PCA分析结果：
- 选择4个主成分（累积解释方差92.3%）
- PC1解释38.5%方差（主要反映流畅性和连贯性）
- PC2解释28.2%方差（主要反映创造性和原创性）
- PC3解释15.8%方差（主要反映多样性）
- PC4解释17.5%方差（主要反映相关性）

综合得分计算：
```python
score = PC1 * 0.385 + PC2 * 0.282 + PC3 * 0.158 + PC4 * 0.175
```

## 输出文件

### 新增图表
每个任务目录下新增：
- `figures/{task}/pca_ranking.png` - PCA综合排名柱状图

### 更新表格
- `tables/{task}/pca_ranking.csv` - PCA综合排名数据
- `tables/{task}/pca_info.json` - PCA分析详细信息（可选）

### 更新报告
报告中每个任务章节现在包含：
1. PCA方法说明
2. 主成分权重列表
3. PCA综合排名表格
4. PCA排名图说明

## 使用示例

### 运行完整分析

```bash
cd analysis/qe_research/scripts/quality_analysis_core
python quality_data_analyzer.py
```

### 查看特定任务的PCA排名

```python
from quality_data_analyzer import QualityDataAnalyzer

analyzer = QualityDataAnalyzer(use_raw=True)
analyzer.load_all_data()

# 分析creative任务
creative_results = analyzer.analyze_task('creative')

# 查看PCA排名
if 'pca_综合得分' in creative_results['model_rankings']:
    pca_ranking = creative_results['model_rankings']['pca_综合得分']
    print("\nCreative任务PCA综合排名:")
    print(pca_ranking)
    
    # 查看PCA详细信息
    pca_info = creative_results.get('pca_ranking_info', {})
    print(f"\n主成分数量: {pca_info['n_components']}")
    print(f"累积解释方差: {pca_info['cumulative_variance'][pca_info['n_components']-1]:.2%}")
    print(f"主成分权重: {pca_info['weights']}")
```

## 兼容性说明

### 单指标任务
如果某个任务只有一个主要指标（如某些简单任务），系统会自动回退到直接排序，不使用PCA。

### 数据缺失
如果某些指标有缺失值，PCA计算时会使用均值填充。

### 向后兼容
- 保留了各单项指标的排名（键名为 `{metric}_单项`）
- 旧的报告格式仍然支持
- 可通过检查 `'pca_综合得分'` 键是否存在来判断是否使用了PCA

## 测试结果

### 测试1: 单任务PCA排名 ✅
- Code任务: 7个指标 → 选择3个主成分（88.5%方差）
- Creative任务: 13个指标 → 选择4个主成分（92.3%方差）
- 所有任务均成功生成PCA排名

### 测试2: 可视化生成 ✅
- 每个任务的 `pca_ranking.png` 成功生成
- 图表标题包含PCA信息
- 数值标签清晰可读

### 测试3: 报告生成 ✅
- 报告中包含PCA方法说明
- 主成分权重正确显示
- 排名表格格式正确

### 测试4: 边界情况 ✅
- 单指标任务正确回退到直接排序
- 缺失值处理正常
- 所有模型均被正确排名

## 优势分析

### 相比单指标排名

1. **更全面**: 综合考虑多个维度，避免片面评价
2. **更科学**: 使用统计学方法，有理论支撑
3. **更稳健**: 降低单一指标波动的影响
4. **更可解释**: 提供主成分权重，了解各维度贡献

### 相比简单平均

1. **降维**: PCA自动识别主要变化方向
2. **去相关**: 主成分之间相互正交，消除冗余
3. **加权**: 根据解释方差自动确定权重
4. **信息保留**: 选择85%阈值，保留主要信息

## 后续改进建议

1. **可配置阈值**: 允许用户自定义累积解释方差阈值
2. **主成分解释**: 分析各主成分的含义（哪些指标贡献最大）
3. **稳健性分析**: 使用Bootstrap评估排名稳定性
4. **可视化增强**: 添加主成分载荷图（Loading Plot）
5. **对比分析**: 同时展示PCA排名和单指标排名的差异

## 总结

✅ 成功将任务级模型排名从单指标改为PCA综合评分  
✅ 自动选择累积解释方差≥85%的主成分  
✅ 使用解释方差比例作为权重  
✅ 新增任务级PCA排名可视化  
✅ 更新报告显示PCA方法说明和权重  
✅ 保持向后兼容，支持单指标任务  
✅ 所有测试通过，功能正常运行  

现在每个任务的模型排名都基于科学的PCA方法，综合考虑多个指标，提供更全面、客观的评价结果。

---

**更新完成**: 2026-03-08  
**测试状态**: ✅ 全部通过  
**文件修改**: `quality_data_analyzer.py`  
**新增方法**: 1个（`_plot_task_pca_ranking`）  
**更新方法**: 3个（`analyze_task`, `_create_task_visualizations`, `_write_task_analyses`）
