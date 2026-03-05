# 质量评估结果文档总结

本文档总结了 `data/analize/results/` 目录下的所有文档及其用途。

---

## 📚 文档清单

### 1. 核心文档

| 文档名称 | 用途 | 推荐阅读顺序 |
|---------|------|------------|
| **[README.md](README.md)** | 目录概述和快速开始 | ⭐ 首先阅读 |
| **[METRICS_GUIDE.md](METRICS_GUIDE.md)** | 详细的评估指标说明 | ⭐⭐ 理解指标 |
| **[METRICS_QUICK_REFERENCE.md](METRICS_QUICK_REFERENCE.md)** | 指标快速查询卡 | ⭐⭐⭐ 日常使用 |
| [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md) | 完整目录结构 | 了解文件组织 |
| [CHANGELOG.md](CHANGELOG.md) | 变更记录 | 了解更新历史 |
| [INDEX.md](INDEX.md) | 快速导航索引 | 快速定位文件 |

### 2. 任务特定文档

每个任务目录下都包含：

| 文件类型 | 说明 | 示例 |
|---------|------|------|
| `*_scores.csv` | 详细评分数据 | `qa_quality_scores.csv` |
| `*_summary.csv` | 汇总统计数据 | `qa_quality_summary.csv` |
| `*_report.md` | 评估报告 | `qa_quality_report.md` |
| `figures/` | 可视化图表 | `figures/qa_em_vs_f1.png` |

---

## 🎯 使用场景指南

### 场景1：快速了解评估结果

**推荐阅读顺序：**
1. [README.md](README.md) - 了解整体结构
2. 对应任务的 `*_report.md` - 查看评估报告
3. `figures/` 目录 - 查看可视化图表

**时间：** 5-10分钟

---

### 场景2：理解评估指标

**推荐阅读顺序：**
1. [METRICS_QUICK_REFERENCE.md](METRICS_QUICK_REFERENCE.md) - 快速查询指标
2. [METRICS_GUIDE.md](METRICS_GUIDE.md) - 深入理解指标含义
3. 对应任务的评估设计文档（在 `../scripts/` 目录）

**时间：** 15-30分钟

---

### 场景3：数据分析

**推荐阅读顺序：**
1. [METRICS_QUICK_REFERENCE.md](METRICS_QUICK_REFERENCE.md) - 了解字段含义
2. [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md) - 找到数据文件
3. 读取 `*_scores.csv` 或 `*_summary.csv` 进行分析

**时间：** 根据分析需求而定

---

### 场景4：跨任务对比

**推荐阅读顺序：**
1. [METRICS_GUIDE.md](METRICS_GUIDE.md) - 了解各任务指标
2. 读取多个任务的 `*_summary.csv` 文件
3. 使用 `overall_score` 进行归一化对比

**时间：** 20-40分钟

---

### 场景5：撰写报告或论文

**推荐阅读顺序：**
1. [METRICS_GUIDE.md](METRICS_GUIDE.md) - 引用指标定义
2. 各任务的 `*_report.md` - 获取关键发现
3. `figures/` 目录 - 使用可视化图表
4. [CHANGELOG.md](CHANGELOG.md) - 说明数据版本

**时间：** 根据报告复杂度而定

---

## 📖 文档详细说明

### README.md
**内容：**
- 目录结构概览
- 7种任务类型说明
- 文件类型说明
- 使用指南
- 相关文档链接

**适合：** 首次使用者、快速了解

---

### METRICS_GUIDE.md
**内容：**
- 7种任务类型的详细指标说明
- 每个指标的含义、取值范围、评估方法
- 数据文件类型说明
- 评分归一化说明
- 使用建议

**适合：** 需要深入理解指标的用户

**特点：**
- ✅ 完整的指标定义
- ✅ 详细的评估方法说明
- ✅ 数据文件使用指南
- ✅ 跨任务对比建议

---

### METRICS_QUICK_REFERENCE.md
**内容：**
- 所有指标的快速查询表
- 字段名和含义对照
- 评分等级参考
- 常用代码示例
- 常见问题解答

**适合：** 日常使用、快速查询

**特点：**
- ✅ 表格化呈现，查询方便
- ✅ 包含代码示例
- ✅ 常见问题解答
- ✅ 使用技巧

---

### DIRECTORY_STRUCTURE.md
**内容：**
- 完整的目录树
- 文件大小统计
- 文件列表
- 统计信息

**适合：** 了解文件组织、查找特定文件

**特点：**
- ✅ 自动生成的目录结构
- ✅ 包含文件大小信息
- ✅ 分类清晰

---

### CHANGELOG.md
**内容：**
- 目录变更记录
- QA任务目录合并说明
- 文件迁移指南
- 版本历史

**适合：** 了解更新历史、迁移旧代码

**特点：**
- ✅ 详细的变更记录
- ✅ 迁移指南
- ✅ 影响说明

---

### INDEX.md
**内容：**
- 快速导航链接
- 按功能分类的文档索引
- 外部文档链接

**适合：** 快速定位文档

---

## 🔄 文档更新流程

### 1. 添加新任务类型

需要更新的文档：
- [ ] README.md - 添加任务说明
- [ ] METRICS_GUIDE.md - 添加指标说明
- [ ] METRICS_QUICK_REFERENCE.md - 添加快速参考
- [ ] DIRECTORY_STRUCTURE.md - 更新目录结构
- [ ] CHANGELOG.md - 记录变更

### 2. 修改评估指标

需要更新的文档：
- [ ] METRICS_GUIDE.md - 更新指标定义
- [ ] METRICS_QUICK_REFERENCE.md - 更新快速参考
- [ ] CHANGELOG.md - 记录变更

### 3. 重组目录结构

需要更新的文档：
- [ ] README.md - 更新目录结构
- [ ] DIRECTORY_STRUCTURE.md - 重新生成
- [ ] CHANGELOG.md - 详细记录变更和迁移指南

---

## 📊 文档统计

| 文档类型 | 数量 | 总字数（估算） |
|---------|------|--------------|
| 核心文档 | 6 | ~15,000字 |
| 任务报告 | 7-14 | ~20,000字 |
| 评估设计 | 7 | ~30,000字 |
| 总计 | 20-27 | ~65,000字 |

---

## 🎓 学习路径

### 初学者路径
1. 阅读 [README.md](README.md)
2. 浏览 [METRICS_QUICK_REFERENCE.md](METRICS_QUICK_REFERENCE.md)
3. 查看一个任务的 `*_report.md`
4. 尝试读取一个 `*_summary.csv` 文件

**预计时间：** 30分钟

---

### 进阶用户路径
1. 深入阅读 [METRICS_GUIDE.md](METRICS_GUIDE.md)
2. 阅读多个任务的评估设计文档
3. 分析 `*_scores.csv` 详细数据
4. 使用可视化图表进行对比

**预计时间：** 2-3小时

---

### 研究者路径
1. 完整阅读所有核心文档
2. 研究评估系统设计文档
3. 分析原始数据和评估代码
4. 进行跨任务、跨模型的深入分析

**预计时间：** 1-2天

---

## 💡 最佳实践

### 1. 文档维护
- 每次重大变更都更新 CHANGELOG.md
- 定期重新生成 DIRECTORY_STRUCTURE.md
- 保持文档之间的链接有效

### 2. 数据使用
- 优先使用 `*_summary.csv` 进行快速对比
- 使用 `*_scores.csv` 进行深入分析
- 参考 `*_report.md` 了解关键发现

### 3. 指标理解
- 先查 METRICS_QUICK_REFERENCE.md
- 需要详细说明时查 METRICS_GUIDE.md
- 有疑问时查看评估设计文档

---

## 🔗 相关资源

### 内部文档
- [评估系统指南](../scripts/EVALUATION_SYSTEM_GUIDE.md)
- [可视化快速指南](../visualization/VISUALIZATION_QUICK_GUIDE.md)
- [快速开始指南](../QUICK_START.md)

### 外部资源
- [ROUGE指标说明](https://en.wikipedia.org/wiki/ROUGE_(metric))
- [BLEU指标说明](https://en.wikipedia.org/wiki/BLEU)
- [BERTScore论文](https://arxiv.org/abs/1904.09675)

---

## ❓ 获取帮助

如果你在使用文档时遇到问题：

1. **查找答案**
   - 先查看 METRICS_QUICK_REFERENCE.md 的常见问题
   - 搜索相关文档的关键词

2. **理解概念**
   - 阅读 METRICS_GUIDE.md 的详细说明
   - 查看评估设计文档

3. **实践操作**
   - 参考 METRICS_QUICK_REFERENCE.md 的代码示例
   - 查看可视化图表理解数据

---

## 📝 文档反馈

如果你发现文档有以下问题，请及时反馈：

- ❌ 信息错误或过时
- ❌ 链接失效
- ❌ 说明不清楚
- ❌ 缺少重要信息
- ✅ 改进建议

---

**文档维护者**：Kiro AI Assistant  
**最后更新**：2026年3月5日  
**文档版本**：v1.0
