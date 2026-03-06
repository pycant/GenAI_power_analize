# 分析脚本说明

## 脚本列表

### 1. comprehensive_analysis.py - 综合分析脚本

完整的质效比分析流程，包括：
- 数据加载和概览
- 性能分析（延迟、吞吐量）
- 效率分析（能耗、资源使用）
- 质量分析（BARTScore等）
- 质效比计算和排名
- 公平性分析（Fairness Gap、Gini系数、Nash Social Welfare）
- 自动生成报告和可视化

**使用方法**:
```bash
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/comprehensive_analysis.py
```

**输出**:
- 报告: `analysis/qe_research/results/reports/comprehensive_report.md`
- 图表: `analysis/qe_research/results/figures/*.png`
- 数据表: `analysis/qe_research/results/tables/*.csv`
- 导出数据: `analysis/qe_research/results/exports/*.csv`

### 2. model_comparison.py - 模型对比分析（待实现）

专注于模型间的详细对比：
- 性能对比
- 效率对比
- 质量对比
- 统计显著性检验

### 3. task_analysis.py - 任务分析（待实现）

按任务类型进行深入分析：
- 任务特定的性能特征
- 模型在不同任务上的适应性
- 任务难度评估

### 4. fairness_analysis.py - 公平性分析（待实现）

深入的公平性评估：
- 详细的Fairness Gap分析
- Gini系数和Lorenz曲线
- Nash Social Welfare优化
- 公平性-性能权衡分析

### 5. statistical_tests.py - 统计检验（待实现）

统计显著性检验：
- t检验
- ANOVA
- 事后检验（Tukey HSD）
- 相关性分析

## 配置文件

所有脚本使用统一的配置文件：
- `analysis/qe_research/configs/analysis_config.yaml`

可以修改配置文件来调整：
- 数据路径
- 输出格式
- 归一化方法
- 权重配置
- 可视化样式

## 依赖包

```bash
pip install pandas numpy scipy scikit-learn
pip install matplotlib seaborn
pip install pyyaml
```

## 快速开始

1. 确保数据管道已初始化：
```bash
python scripts/test_and_explore_pipeline.py
```

2. 运行综合分析：
```bash
python analysis/qe_research/scripts/comprehensive_analysis.py
```

3. 查看结果：
```bash
# 查看报告
notepad analysis/qe_research/results/reports/comprehensive_report.md

# 查看图表
explorer analysis/qe_research/results/figures
```

## 日志

所有脚本的日志保存在：
- `analysis/qe_research/logs/analysis.log`

## 缓存

计算结果缓存在：
- `analysis/qe_research/cache/`

清理缓存：
```bash
rmdir /s /q analysis\qe_research\cache
mkdir analysis\qe_research\cache
```

## 故障排除

### 中文显示问题

如果图表中文显示为方框：
1. 确认系统已安装 Microsoft YaHei 字体
2. 修改配置文件中的字体设置

### 数据加载失败

如果提示找不到数据：
1. 检查数据管道是否已初始化
2. 运行 `python scripts/test_and_explore_pipeline.py`
3. 检查数据目录结构

### 内存不足

如果遇到内存问题：
1. 在配置文件中禁用缓存
2. 减少可视化的数据点数量
3. 分批处理数据

## 扩展开发

添加新的分析脚本：
1. 继承 `ComprehensiveAnalyzer` 类
2. 使用 `ExperimentDataManager` 加载数据
3. 遵循现有的输出格式
4. 更新本README文档

## 联系方式

如有问题，请查看：
- 项目文档: `docs/`
- 数据管道文档: `data/analize/pipeline/README.md`
- 主README: `README.md`
