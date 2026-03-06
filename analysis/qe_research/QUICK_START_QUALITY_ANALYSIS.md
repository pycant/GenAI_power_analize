# 质量数据分析快速开始指南

## 概述

质量数据分析器对模型的质量评估数据进行深度分析和可视化，生成10个分析任务的图表和综合报告。

## 当前状态

✅ **已修复**: 所有图片生成问题已解决
- 生成图片: 8/10张
- 任务3生成CSV表格（设计如此）
- 任务10需要多任务类型数据（当前只有code）

## 快速运行

### 方法1: 批处理脚本（推荐）
```cmd
analysis\qe_research\scripts\run_quality_analysis.bat
```

### 方法2: PowerShell
```powershell
$env:PYTHONUTF8=1
python analysis/qe_research/scripts/quality_data_analyzer.py
```

### 方法3: CMD
```cmd
set PYTHONUTF8=1
python analysis/qe_research/scripts/quality_data_analyzer.py
```

## 输出结果

### 图表（8张PNG，300 DPI）
1. ✅ `01_score_distribution_code.png` - 质量得分分布（直方图+KDE+统计摘要）
2. ✅ `02_model_comparison_code.png` - 按模型分组的箱线图
3. ⚠️ 任务3生成CSV表格而非图片
4. ✅ `04_model_ranking_code.png` - 模型排名条形图
5. ✅ `05_radar_chart_code.png` - 模型能力雷达图
6. ✅ `06_model_task_heatmap.png` - 模型×任务热力图
7. ✅ `07_code_submetrics.png` - 代码任务子指标构成
8. ✅ `08_correlation_matrix_code.png` - 子指标相关性矩阵
9. ✅ `09_stability_code.png` - 模型稳定性对比
10. ⚠️ 任务10需要多任务类型数据

### 报告
- `quality_analysis_report.md` - 综合分析报告（包含所有图表引用）

### 表格
- `missing_values.csv` - 缺失值分析结果

### 日志
- `quality_analysis.log` - 详细执行日志

## 数据要求

### 输入数据位置
```
data/analize/results/
├── code_quality/
│   └── quality_summary_code.csv
├── qa_quality/
│   └── quality_summary_qa.csv
├── creative_quality/
│   └── quality_summary_creative.csv
└── summary_quality/
    └── quality_summary_summary.csv
```

### 必需列（按优先级）
1. `overall_score` - 综合得分
2. `functional_correctness_mean` - 功能正确性
3. `compilation_success_mean` - 编译成功率
4. `compilation_rate_mean` - 编译率（向后兼容）

### 当前数据状态
- ✅ code任务: 12个模型
- ⚠️ qa任务: 未加载
- ⚠️ creative任务: 未加载
- ⚠️ summary任务: 未加载

## 分析任务详解

### 一、数据探索性分析
- **任务1**: 质量得分分布 - 直方图、KDE曲线、统计摘要
- **任务2**: 按模型分组的箱线图 - 模型间质量对比
- **任务3**: 缺失值分析 - 生成CSV表格

### 二、模型对比分析
- **任务4**: 模型排名条形图 - 水平条形图展示排名
- **任务5**: 雷达图 - 多维度能力对比（前3个模型）
- **任务6**: 模型×任务热力图 - 跨任务性能矩阵

### 三、任务专项分析
- **任务7**: 代码任务专项分析 - 子指标堆叠条形图

### 四、子指标关系分析
- **任务8**: 相关性矩阵 - 子指标间的相关系数热力图

### 五、质量稳定性分析
- **任务9**: 模型稳定性对比 - 均值vs标准差散点图

### 六、跨任务综合评估
- **任务10**: 综合质量得分 - 需要多个任务类型的数据

## 可视化风格

### 学术配色方案
```python
['#0173B2', '#DE8F05', '#029E73', '#CC78BC',
 '#CA9161', '#949494', '#ECE133', '#56B4E9']
```

### 图表规格
- **分辨率**: 300 DPI（出版质量）
- **字体**: Microsoft YaHei（中文）
- **格式**: PNG
- **尺寸**: 根据内容自适应（通常10-14英寸宽）

## 故障排除

### 问题1: 缺少图片
**症状**: 只生成了部分图片

**原因**: 数据列名不匹配

**解决**: 
- 检查CSV文件是否包含必需的质量指标列
- 查看日志文件了解跳过原因
- 确保使用最新版本的分析器（已支持新旧列名）

### 问题2: 中文乱码
**症状**: 图表中中文显示为方框

**原因**: 系统缺少中文字体或编码设置错误

**解决**:
```powershell
$env:PYTHONUTF8=1  # 设置UTF-8编码
```

### 问题3: 任务10未生成
**症状**: 缺少综合质量得分图表

**原因**: 只有一个任务类型的数据

**解决**: 添加更多任务类型的质量评估数据（qa、creative、summary等）

## 修复历史

### 2026-03-05 修复
- ✅ 修复任务1、2、4、6图片缺失问题
- ✅ 添加对新列名结构的支持
- ✅ 保持向后兼容性
- ✅ 添加详细调试日志
- ✅ 更新任务7的指标列表

**修复前**: 4/10张图片
**修复后**: 8/10张图片（2张因数据限制未生成）

## 相关文档

- **需求文档**: `analysis/qe_research/docs/quality_data_analize.md`
- **修复总结**: `analysis/qe_research/results/quality_analysis/QUALITY_ANALYSIS_FIX_SUMMARY.md`
- **数据管线**: `data/analize/pipeline/README.md`
- **原始数据分析**: `analysis/qe_research/QUICK_START_RAW_ANALYSIS.md`

## 下一步

1. **添加更多任务类型数据** - 启用任务10
2. **处理缺失值** - 提高数据完整性
3. **扩展分析维度** - 添加质量-效率权衡分析
4. **优化可视化** - 根据反馈调整图表样式

---

**最后更新**: 2026-03-05 22:44:42
**状态**: ✅ 正常运行
**生成图片**: 8/10张
