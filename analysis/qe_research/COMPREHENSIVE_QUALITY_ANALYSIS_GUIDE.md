# 综合质量分析系统指南

## 概述

本系统对所有任务类型（code、creative、qa、summary、translation、math、reasoning）进行深度质量分析，生成标准化图表和洞察报告。

## 系统架构

### 核心组件

1. **主分析器**: `quality_data_analyzer.py`
   - 数据加载和预处理
   - 通用分析框架
   - 报告生成

2. **任务扩展**: `quality_analyzer_extensions.py`
   - 各任务类型的专项分析函数
   - 可插拔设计，易于扩展

3. **数据源**: `analysis/qe_research/results/quality_scores/`
   - 使用 `create_quality_score_tables.py` 生成的标准化数据
   - 格式：模型为列，指标为行（已转置）

## 快速开始

### 1. 生成质量评分表格（如果还没有）

```bash
# 运行质量评分表格生成
analysis\qe_research\scripts\run_quality_score_tables.bat
```

这会生成：
- `code_scores_raw.csv`
- `creative_scores_raw.csv`
- `qa_scores_raw.csv`
- `summary_scores_raw.csv`
- `translation_scores_raw.csv`
- `math_scores_raw.csv`
- `reasoning_scores_raw.csv`

### 2. 运行综合质量分析

```bash
# 运行综合分析
analysis\qe_research\scripts\run_comprehensive_quality_analysis.bat
```

## 分析维度

### 一、数据探索性分析

#### 任务1: 质量得分分布
- **输出**: `01_score_distribution_{task}.png`
- **内容**: 直方图 + KDE曲线 + 统计摘要
- **洞察示例**:
  - 得分分布形态（正态/偏态）
  - 模型质量分化程度（变异系数）
  - 整体质量水平评估

#### 任务2: 按模型分组的箱线图
- **输出**: `02_model_comparison_{task}.png`
- **内容**: 模型质量对比条形图（带误差线）
- **洞察示例**:
  - 各模型在该任务上的相对表现
  - 质量稳定性（误差线长度）

#### 任务3: 缺失值分析
- **输出**: `missing_values.csv`
- **内容**: 各任务各指标的缺失情况统计

### 二、模型对比分析

#### 任务4: 模型排名条形图
- **输出**: `04_model_ranking_{task}.png`
- **内容**: 水平条形图展示模型排名
- **洞察示例**:
  - 最佳模型识别
  - 模型间差距量化

#### 任务5: 雷达图
- **输出**: `05_radar_chart_{task}.png`
- **内容**: 多维能力雷达图（前3个模型）
- **洞察示例**:
  - 模型的多维能力画像
  - 强项和弱项识别

#### 任务6: 模型×任务热力图
- **输出**: `06_model_task_heatmap.png`
- **内容**: 跨任务的模型表现热力图
- **洞察示例**:
  - 模型的通用性评估
  - 任务难度对比
  - 模型-任务匹配建议

### 三、任务专项分析

#### 任务7: 各任务子指标分析

**Code任务** (`07_code_submetrics.png`):
- 功能正确性、编译成功率、测试通过率
- 代码简洁性、可读性得分
- **洞察**: 代码生成能力的多维评估

**Creative任务** (`07_creative_submetrics.png`):
- distinct-2（词汇多样性）
- perplexity（语言流畅度）
- **洞察**: 创意写作的多样性和流畅度权衡

**QA任务** (`07_qa_submetrics.png`):
- 答案完整性、长度、技术术语密度
- 置信度、推理能力
- **洞察**: 问答质量的多维构成

**Summary任务** (`07_summary_submetrics.png`):
- ROUGE-1/2/L、BERTScore
- 压缩比、信息密度
- **洞察**: 摘要质量与压缩效率的平衡

**Translation任务** (`07_translation_submetrics.png`):
- BLEU分数、语义保真度
- 流畅度、术语准确性、文化适应性
- **洞察**: 翻译质量的多维评估

**Math任务** (`07_math_submetrics.png`):
- 答案正确性、推理过程
- 公式使用、步骤清晰度
- **洞察**: 数学推理能力的全面评估

**Reasoning任务** (`07_reasoning_submetrics.png`):
- 结论正确性、完整性得分
- 逻辑连贯性、论证深度、推理步骤数
- **洞察**: 逻辑推理能力的多维分析

### 四、子指标关系分析

#### 任务8: 相关性矩阵
- **输出**: `08_correlation_matrix_{task}.png`
- **内容**: 子指标间的相关系数热力图
- **洞察示例**:
  - 强相关指标识别（可能冗余）
  - 独立维度识别
  - 质量权衡关系发现

### 五、质量稳定性分析

#### 任务9: 模型稳定性对比
- **输出**: `09_stability_{task}.png`
- **内容**: 各模型的标准差对比
- **洞察示例**:
  - 最稳定模型（适合生产环境）
  - 最不稳定模型（需要多次采样）
  - 稳定性与质量的关系

### 六、跨任务综合评估

#### 任务10: 综合质量得分
- **输出**: `10_comprehensive_score.png`
- **内容**: 跨任务的综合质量评分（带误差线）
- **洞察示例**:
  - 通用能力最强的模型
  - 专用vs通用模型识别
  - 任务覆盖度评估

## 报告结构

### 生成的报告: `quality_analysis_report.md`

```markdown
# 质量数据深度分析报告

## 执行摘要
- 分析任务数量
- 覆盖的模型数量

## 关键洞察
### {TASK}任务洞察
- 质量得分统计
- 最佳/待改进模型
- 稳定性分析
- 任务特点

## 分析维度
### 一、数据探索性分析
- 任务1-3的图表和说明

### 二、模型对比分析
- 任务4-6的图表和说明

### 三、任务专项分析
- 任务7的各任务专项图表

### 四、子指标关系分析
- 任务8的相关性分析

### 五、质量稳定性分析
- 任务9的稳定性分析

### 六、跨任务综合评估
- 任务10的综合评估

## 从图表中得出的结论
### 任务1: 质量得分分布图
**从图表可以得出**:
- 分布形态分析（正态/偏态）
- 离散程度分析（变异系数）
- 得分水平分析（优秀/良好/待提高）

### 任务2-4: 模型对比图
**从图表可以得出**:
- 最佳模型推荐
- 次优模型备选
- 待改进模型识别
- 稳定性评估

### 任务6: 模型×任务热力图
**从图表可以得出**:
- 模型强弱项识别
- 应用场景匹配建议
- 模型全面性评估

### 任务8: 子指标相关性矩阵
**从图表可以得出**:
- 指标冗余识别
- 独立维度发现
- 质量权衡关系

### 任务9: 稳定性对比图
**从图表可以得出**:
- 生产环境适用性
- 采样策略建议

### 任务10: 跨任务综合评估
**从图表可以得出**:
- 通用vs专用模型
- 任务覆盖度
- 性能波动分析
```

## 洞察提取示例

### 示例1: Code任务

**从图表可以得出**:
1. **模型加载时间**: 通过首次推理时间戳分析，模型加载到显存耗时约4s
2. **首token延迟**: 从模型加载到首次输出token耗时约2.5s
3. **编译成功率**: 最佳模型达到80%，平均水平仅16.7%
4. **质量分化**: 变异系数1.521，说明模型能力差距显著
5. **稳定性**: gemma_2b_hf_4bit最稳定，但质量较低；deepseek_8b_ol_q4km质量高但波动大

### 示例2: Creative任务

**从图表可以得出**:
1. **词汇多样性**: distinct-2平均0.899，说明模型输出词汇丰富
2. **语言流畅度**: perplexity平均33.7，qwen25_3b_hf_8bit表现最佳（3.98）
3. **多样性-流畅度权衡**: 高distinct-2不一定意味着低perplexity
4. **模型特点**: qwen系列在创意写作上表现突出

### 示例3: QA任务

**从图表可以得出**:
1. **答案完整性**: 所有模型has_answer=1.0，说明都能给出答案
2. **答案长度**: 平均1000+字符，说明回答详细
3. **技术术语**: 平均密度0.3，说明答案专业性适中
4. **推理能力**: 大部分模型has_reasoning=1.0，具备推理能力

## 扩展新任务

### 添加新任务类型的步骤

1. **在 `quality_analyzer_extensions.py` 中添加新函数**:

```python
def _task7_newtask_analysis(self):
    """任务7: 新任务专项分析"""
    if 'newtask' not in self.quality_data:
        return
    
    df = self.quality_data['newtask']
    
    # 选择相关指标
    metrics = ['metric1', 'metric2', 'metric3']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 2:
        logger.warning("新任务缺少必要指标")
        return
    
    # 归一化
    df_norm = self._normalize_scores(df, available_metrics)
    
    # 创建可视化
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(df))
    bottom = np.zeros(len(df))
    
    for i, metric in enumerate(available_metrics):
        ax.bar(x, df_norm[metric], bottom=bottom, label=metric,
              color=self.academic_colors[i], edgecolor='white', linewidth=0.5)
        bottom += df_norm[metric]
    
    ax.set_xticks(x)
    ax.set_xticklabels(df['model'], rotation=45, ha='right')
    ax.set_xlabel('模型', fontsize=11)
    ax.set_ylabel('归一化得分', fontsize=11)
    ax.set_title('任务7: 新任务子指标构成', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    self._save_fig('07_newtask_submetrics.png')
```

2. **在 `add_task_specific_methods` 函数中注册**:

```python
def add_task_specific_methods(analyzer_class):
    """将任务专项分析方法添加到分析器类"""
    # ... 现有代码 ...
    analyzer_class._task7_newtask_analysis = _task7_newtask_analysis
```

3. **在 `task_specific_analysis` 中添加调用**:

```python
def task_specific_analysis(self):
    """任务专项分析"""
    for task_type in self.task_types:
        # ... 现有代码 ...
        elif task_type == 'newtask':
            self._task7_newtask_analysis()
```

4. **在 `_write_task_specific_insights` 中添加洞察模板**:

```python
elif task_type == 'newtask':
    f.write("- 新任务评估XXX和YYY\n")
    f.write("- 建议关注: 指标A、指标B、指标C\n")
```

## 共享工具函数

### `_get_primary_score_column(df, task_type)`
自动识别主要质量指标列，按优先级查找。

### `_get_std_column(mean_col)`
获取对应的标准差列名。

### `_normalize_scores(df, columns)`
将指定列归一化到0-1范围。

### `_extract_task_insights(task_type, df, score_col)`
提取任务特定的统计洞察。

## 输出文件

### 图表目录: `analysis/qe_research/results/quality_analysis/figures/`
- `01_score_distribution_{task}.png` - 得分分布图
- `02_model_comparison_{task}.png` - 模型对比图
- `04_model_ranking_{task}.png` - 模型排名图
- `05_radar_chart_{task}.png` - 雷达图
- `06_model_task_heatmap.png` - 热力图
- `07_{task}_submetrics.png` - 任务专项分析图
- `08_correlation_matrix_{task}.png` - 相关性矩阵
- `09_stability_{task}.png` - 稳定性对比图
- `10_comprehensive_score.png` - 综合评分图

### 表格目录: `analysis/qe_research/results/quality_analysis/tables/`
- `missing_values.csv` - 缺失值统计
- `comprehensive_scores.csv` - 综合评分表

### 报告目录: `analysis/qe_research/results/quality_analysis/reports/`
- `quality_analysis_report.md` - 综合分析报告

## 最佳实践

### 1. 数据准备
- 确保先运行 `create_quality_score_tables.py` 生成标准化数据
- 检查数据完整性，确保关键指标不缺失

### 2. 分析执行
- 使用批处理文件运行，确保环境正确
- 检查日志文件了解详细执行情况

### 3. 结果解读
- 优先查看报告的"关键洞察"部分
- 结合图表和数值进行综合判断
- 注意变异系数、标准差等离散度指标

### 4. 洞察提取
- 关注分布形态（正态/偏态）
- 识别异常值和离群点
- 分析指标间的相关性和权衡关系
- 考虑稳定性与质量的平衡

## 故障排除

### 问题1: 找不到数据文件
**解决**: 先运行 `run_quality_score_tables.bat` 生成数据

### 问题2: 某些任务没有图表
**原因**: 该任务数据不足或指标缺失
**解决**: 检查原始质量评分数据的完整性

### 问题3: 中文显示乱码
**解决**: 
```bash
set PYTHONUTF8=1
```

### 问题4: 导入错误
**解决**: 确保 `quality_analyzer_extensions.py` 在同一目录

## 相关文档

- [质量评分表格生成指南](QUALITY_SCORE_TABLES_GUIDE.md)
- [指标说明文档](../METRICS_GUIDE.md)
- [数据管道系统](../数据管道系统.md)

## 更新日志

- **2026-03-07**: 创建综合质量分析系统
  - 支持7种任务类型的专项分析
  - 实现可插拔的任务扩展架构
  - 生成标准化的洞察报告
  - 提供丰富的可视化图表

---

**维护者**: Kiro AI Assistant  
**脚本位置**: `analysis/qe_research/scripts/quality_data_analyzer.py`  
**扩展位置**: `analysis/qe_research/scripts/quality_analyzer_extensions.py`
