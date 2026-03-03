# 文档中心

欢迎来到 GenAI 模型能效评级体系项目文档中心。本页面提供所有文档的快速导航。

## 📚 文档分类

### 🚀 快速开始

| 文档 | 说明 | 适合人群 |
|------|------|---------|
| [Experiment Runner 使用指南](./EXPERIMENT_RUNNER_GUIDE.md) | 实验执行脚本完整使用说明 | 所有用户 |
| [配置文件参数参考](./CONFIG_PARAMETERS_REFERENCE.md) | 测试用例配置参数详解 | 实验人员 |
| [空闲基线快速参考](./IDLE_BASELINE_QUICK_REFERENCE.md) | 空闲基线功能快速上手 | 新用户 |

### 🔬 实验功能

| 文档 | 说明 | 更新时间 |
|------|------|---------|
| [空闲基线测量功能](./IDLE_BASELINE_MEASUREMENT.md) | 空闲功耗测量和增量指标计算 | 2026-03-02 |
| [多轮对话指南](./MULTI_TURN_CONVERSATION_GUIDE.md) | 多轮对话实验配置 | 2026-03-01 |
| [每轮监控指南](./PER_TURN_MONITORING_GUIDE.md) | 分轮资源监控功能 | 2026-03-01 |
| [TTFT和Token追踪改进](./TTFT_AND_TOKEN_TRACKING_IMPROVEMENTS.md) | 首token时间和token统计 | 2026-03-02 |

### 📊 数据分析

| 文档 | 说明 | 状态 |
|------|------|------|
| [数据采集缺口分析](./README_GAP_ANALYSIS.md) | 数据采集完整性分析索引 | ✅ 完成 |
| [详细缺口分析](./DATA_COLLECTION_GAP_ANALYSIS.md) | 完整的指标对比和分析 | ✅ 完成 |
| [实施优先级清单](./IMPLEMENTATION_PRIORITY.md) | 按优先级分类的改进清单 | 🔄 更新中 |
| [数据结构对比](./DATA_STRUCTURE_COMPARISON.md) | 当前vs目标数据结构 | ✅ 完成 |
| [可视化分析](./GAP_ANALYSIS_VISUAL.md) | 缺口分析可视化展示 | ✅ 完成 |

### 🎓 学术文档

| 文档 | 说明 | 位置 |
|------|------|------|
| 研究背景与意义 | 项目研究背景和学术价值 | `docs/academic/` |
| 文献综述 | 相关研究现状和发展趋势 | `docs/academic/` |
| 方法论 | 多维效质比评估理论框架 | `docs/academic/` |
| 实验设计 | 实验方案和数据收集方法 | `docs/experiment/` |

### 🔧 技术文档

| 文档 | 说明 | 位置 |
|------|------|------|
| 技术架构 | 系统架构设计和技术选型 | 根目录 |
| 产品需求 | 功能需求和非功能性需求 | 根目录 |
| 项目结构 | 目录结构和文件组织 | 根目录 |
| API文档 | RESTful API接口说明 | `docs/api/` |

### 🛠️ 开发指南

| 文档 | 说明 | 位置 |
|------|------|------|
| [统一运行器指南](../experiments/UNIFIED_RUNNER_GUIDE.md) | 实验运行器架构说明 | `experiments/` |
| [HuggingFace模型指南](./experiment/hf_models_guide.md) | HF模型下载和使用 | `docs/experiment/` |
| [故障排除](../TROUBLESHOOTING.md) | 常见问题和解决方案 | 根目录 |

### 📝 更新日志

| 文档 | 说明 | 日期 |
|------|------|------|
| [空闲基线更新总结](./IDLE_BASELINE_UPDATE_SUMMARY.md) | 空闲基线功能实现总结 | 2026-03-02 |
| [实验更新](../EXPERIMENTS_UPDATE.md) | 实验系统更新记录 | 2026-03-01 |

## 🎯 按角色导航

### 新用户

1. 阅读 [Experiment Runner 使用指南](./EXPERIMENT_RUNNER_GUIDE.md)
2. 查看 [配置文件参数参考](./CONFIG_PARAMETERS_REFERENCE.md)
3. 尝试 [空闲基线快速参考](./IDLE_BASELINE_QUICK_REFERENCE.md)

### 实验人员

1. [Experiment Runner 使用指南](./EXPERIMENT_RUNNER_GUIDE.md) - 完整功能说明
2. [空闲基线测量功能](./IDLE_BASELINE_MEASUREMENT.md) - 能效评估
3. [多轮对话指南](./MULTI_TURN_CONVERSATION_GUIDE.md) - 对话实验
4. [配置文件参数参考](./CONFIG_PARAMETERS_REFERENCE.md) - 参数详解

### 开发者

1. [数据采集缺口分析](./README_GAP_ANALYSIS.md) - 了解系统现状
2. [实施优先级清单](./IMPLEMENTATION_PRIORITY.md) - 开发任务
3. [数据结构对比](./DATA_STRUCTURE_COMPARISON.md) - 数据结构
4. [统一运行器指南](../experiments/UNIFIED_RUNNER_GUIDE.md) - 架构设计

### 研究人员

1. [实验设计文档](./experiment/experiment_design.md) - 实验方法论
2. [数据采集缺口分析](./README_GAP_ANALYSIS.md) - 指标体系
3. [可视化分析](./GAP_ANALYSIS_VISUAL.md) - 数据分析
4. 学术文档 (`docs/academic/`) - 理论基础

## 🔍 按主题导航

### 实验执行

- [Experiment Runner 使用指南](./EXPERIMENT_RUNNER_GUIDE.md)
- [配置文件参数参考](./CONFIG_PARAMETERS_REFERENCE.md)
- [统一运行器指南](../experiments/UNIFIED_RUNNER_GUIDE.md)

### 能效评估

- [空闲基线测量功能](./IDLE_BASELINE_MEASUREMENT.md)
- [空闲基线快速参考](./IDLE_BASELINE_QUICK_REFERENCE.md)
- [空闲基线更新总结](./IDLE_BASELINE_UPDATE_SUMMARY.md)

### 多轮对话

- [多轮对话指南](./MULTI_TURN_CONVERSATION_GUIDE.md)
- [每轮监控指南](./PER_TURN_MONITORING_GUIDE.md)
- [每轮监控实现](./PER_TURN_MONITORING_IMPLEMENTATION.md)

### 数据分析

- [数据采集缺口分析](./README_GAP_ANALYSIS.md)
- [详细缺口分析](./DATA_COLLECTION_GAP_ANALYSIS.md)
- [数据结构对比](./DATA_STRUCTURE_COMPARISON.md)
- [可视化分析](./GAP_ANALYSIS_VISUAL.md)

### 模型管理

- [HuggingFace模型指南](./experiment/hf_models_guide.md)
- [HuggingFace设置](../HUGGINGFACE_SETUP.md)
- [模型下载脚本](../scripts/download_hf_model.py)

## 📖 文档编写规范

### 文档结构

所有文档应包含：
1. 标题和概述
2. 目录（如果内容较长）
3. 详细内容
4. 示例代码/配置
5. 相关文档链接
6. 更新日志

### 命名规范

- 使用大写字母和下划线: `DOCUMENT_NAME.md`
- 使用描述性名称: `EXPERIMENT_RUNNER_GUIDE.md`
- 避免缩写: 使用完整单词

### 格式规范

- 使用 Markdown 格式
- 代码块使用语法高亮
- 表格对齐整齐
- 链接使用相对路径

## 🔄 文档更新

### 最近更新

- **2026-03-02**: 添加 Experiment Runner 使用指南
- **2026-03-02**: 添加配置文件参数参考
- **2026-03-02**: 完成空闲基线测量功能文档
- **2026-03-01**: 完成多轮对话功能文档
- **2026-03-01**: 完成数据采集缺口分析

### 待更新

- [ ] API 文档完善
- [ ] 数据库设计文档
- [ ] 部署指南更新
- [ ] 用户手册编写

## 💡 文档反馈

如果您发现文档有任何问题或建议，请：

1. 提交 [GitHub Issue](https://github.com/your-org/genai-power-evaluation/issues)
2. 发送邮件至项目邮箱
3. 在项目讨论区留言

## 📞 获取帮助

- **文档问题**: 查看 [故障排除](../TROUBLESHOOTING.md)
- **功能问题**: 查看对应功能文档
- **技术支持**: 联系项目维护者

---

**文档版本**: v2.0  
**最后更新**: 2026-03-02  
**维护者**: Kiro AI Assistant
