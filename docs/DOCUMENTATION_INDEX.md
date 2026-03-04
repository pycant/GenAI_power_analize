# 项目文档索引

本文档提供项目中所有 Markdown 文档的分类索引和快速导航。

## 📚 文档分类

- [核心文档](#核心文档) - 项目入口和关键指南
- [实验相关](#实验相关) - 实验设计、执行和分析
- [模型相关](#模型相关) - 模型信息、基准测试和使用指南
- [技术文档](#技术文档) - 架构、API 和实现细节
- [问题修复](#问题修复) - Bug 修复和问题解决记录
- [会话总结](#会话总结) - 开发会话的总结记录
- [参考资料](#参考资料) - 文献综述和研究笔记
- [工具文档](#工具文档) - 第三方工具使用说明
- [归档文档](#归档文档) - 历史文档和已完成任务

---

## 核心文档

### 项目入口

| 文档 | 描述 | 路径 |
|------|------|------|
| **README.md** | 项目主文档，快速开始指南 | `README.md` |
| **agents.md** | Agent 使用指南，项目目的和环境说明 | `agents.md` |
| **CONTRIBUTING.md** | 贡献指南 | `CONTRIBUTING.md` |
| **TROUBLESHOOTING.md** | 常见问题排查 | `TROUBLESHOOTING.md` |

### 快速参考

| 文档 | 描述 | 路径 |
|------|------|------|
| **QUICK_REFERENCE_DATASETS.md** | 数据集快速参考 | `QUICK_REFERENCE_DATASETS.md` |
| **NEXT_STEPS.md** | 下一步行动指南 | `NEXT_STEPS.md` |

### Steering 文件（Kiro AI 指导）

| 文档 | 描述 | 路径 |
|------|------|------|
| **product.md** | 产品概述和目标 | `.kiro/steering/product.md` |
| **structure.md** | 项目结构说明 | `.kiro/steering/structure.md` |
| **tech.md** | 技术栈和工具链 | `.kiro/steering/tech.md` |

---

## 实验相关

### 实验设计与指南

| 文档 | 描述 | 路径 | 优先级 |
|------|------|------|--------|
| **experiment_design.md** | 实验设计完整指南 | `docs/experiment/experiment_design.md` | ⭐⭐⭐ |
| **EXPERIMENT_RUNNER_GUIDE.md** | 实验执行器使用指南 | `docs/EXPERIMENT_RUNNER_GUIDE.md` | ⭐⭐⭐ |
| **UNIFIED_RUNNER_GUIDE.md** | 统一实验执行器指南 | `experiments/UNIFIED_RUNNER_GUIDE.md` | ⭐⭐⭐ |
| **TEST_CASE_DESIGN_GUIDE.md** | 测试用例设计指南 | `docs/experiment/TEST_CASE_DESIGN_GUIDE.md` | ⭐⭐ |
| **CONFIG_PARAMETERS_REFERENCE.md** | 配置参数参考 | `docs/CONFIG_PARAMETERS_REFERENCE.md` | ⭐⭐ |
| **QUICK_START_NEW_FORMAT.md** | 新格式快速开始 | `docs/QUICK_START_NEW_FORMAT.md` | ⭐⭐ |

### 实验功能文档

| 文档 | 描述 | 路径 |
|------|------|------|
| **MULTI_TURN_CONVERSATION_GUIDE.md** | 多轮对话实验指南 | `docs/MULTI_TURN_CONVERSATION_GUIDE.md` |
| **IDLE_BASELINE_MEASUREMENT.md** | 空闲基线测量说明 | `docs/IDLE_BASELINE_MEASUREMENT.md` |
| **IDLE_BASELINE_QUICK_REFERENCE.md** | 空闲基线快速参考 | `docs/IDLE_BASELINE_QUICK_REFERENCE.md` |
| **PER_TURN_MONITORING_GUIDE.md** | 每轮监控指南 | `docs/PER_TURN_MONITORING_GUIDE.md` |
| **TTFT_AND_TOKEN_TRACKING_IMPROVEMENTS.md** | TTFT 和 Token 跟踪改进 | `docs/TTFT_AND_TOKEN_TRACKING_IMPROVEMENTS.md` |

### 实验操作与用户指南

| 文档 | 描述 | 路径 |
|------|------|------|
| **experiment_operation_guide.md** | 实验操作指南 | `docs/experiment/experiment_operation_guide.md` |
| **user_guide.md** | 用户使用指南 | `docs/experiment/user_guide.md` |
| **metrics.md** | 指标说明文档 | `docs/experiment/metrics.md` |

### 实验结果与分析

| 文档 | 描述 | 路径 |
|------|------|------|
| **report.md** | Experiments_1 分析报告 | `results/experiments_1/report.md` |
| **multivariate_report.md** | 多元统计分析报告 | `results/experiments_1/multivariate_analysis/multivariate_report.md` |
| **实验结果分析报告.md** | 测试实验结果分析 | `data/test/实验结果分析报告.md` |
| **监控数据可视化说明.md** | 监控数据可视化说明 | `data/test/监控数据可视化说明.md` |

### 实验配置完成记录

| 文档 | 描述 | 路径 |
|------|------|------|
| **EXPERIMENT_5_SETUP.md** | Experiment 5 设置文档 | `docs/EXPERIMENT_5_SETUP.md` |
| **EXPERIMENT_5_CONFIGURATION_COMPLETE.md** | Experiment 5 配置完成 | `docs/EXPERIMENT_5_CONFIGURATION_COMPLETE.md` |
| **EXPERIMENT_5_READY.md** | Experiment 5 就绪说明 | `EXPERIMENT_5_READY.md` |
| **TEST_CASES_READY.md** | 测试用例就绪说明 | `docs/TEST_CASES_READY.md` |
| **TEST_RESULTS.md** | 测试结果记录 | `docs/TEST_RESULTS.md` |

---

## 模型相关

### 模型基准测试与对比

| 文档 | 描述 | 路径 | 优先级 |
|------|------|------|--------|
| **MODEL_BENCHMARKS_SUMMARY.md** | 模型基准测试详细总结 | `docs/MODEL_BENCHMARKS_SUMMARY.md` | ⭐⭐⭐ |
| **MODEL_QUICK_REFERENCE.md** | 模型快速参考表 | `docs/MODEL_QUICK_REFERENCE.md` | ⭐⭐⭐ |
| **MODEL_QUALITY_ISSUES.md** | 模型质量问题诊断 | `docs/MODEL_QUALITY_ISSUES.md` | ⭐⭐ |

### 模型使用指南

| 文档 | 描述 | 路径 |
|------|------|------|
| **hf_models_guide.md** | HuggingFace 模型使用指南 | `docs/experiment/hf_models_guide.md` |
| **HUGGINGFACE_SETUP.md** | HuggingFace 环境设置 | `HUGGINGFACE_SETUP.md` |
| **models/README.md** | 模型目录说明 | `models/README.md` |

### 模型官方文档

| 文档 | 描述 | 路径 |
|------|------|------|
| **Phi-3 Mini README** | Phi-3 Mini 官方文档 | `models/huggingface/microsoft--phi-3-mini-4k-instruct/README.md` |
| **Qwen 2.5 3B README** | Qwen 2.5 3B 官方文档 | `models/huggingface/Qwen--Qwen2.5-3B-Instruct/README.md` |
| **Qwen 2.5 7B README** | Qwen 2.5 7B 官方文档 | `models/huggingface/Qwen--Qwen2.5-7B-Instruct/README.md` |

---

## 技术文档

### 架构与设计

| 文档 | 描述 | 路径 |
|------|------|------|
| **technical_architecture.md** | 技术架构文档 | `docs/project/technical_architecture.md` |
| **project_structure.md** | 项目结构说明 | `project_structure.md` |
| **docs/README.md** | 文档目录说明 | `docs/README.md` |

### 数据结构与重构

| 文档 | 描述 | 路径 |
|------|------|------|
| **DATA_STRUCTURE_REFACTORING.md** | 数据结构重构方案 | `docs/DATA_STRUCTURE_REFACTORING.md` |
| **DATA_STRUCTURE_COMPARISON.md** | 数据结构对比 | `docs/DATA_STRUCTURE_COMPARISON.md` |
| **DATA_REFACTORING_SUMMARY.md** | 数据重构总结 | `docs/DATA_REFACTORING_SUMMARY.md` |
| **DATA_REFACTORING_IMPLEMENTATION.md** | 数据重构实施 | `docs/DATA_REFACTORING_IMPLEMENTATION.md` |
| **REFACTORING_SUMMARY.md** | 重构总结 | `REFACTORING_SUMMARY.md` |
| **REFACTORING_COMPLETED.md** | 重构完成记录 | `docs/REFACTORING_COMPLETED.md` |
| **REFACTORING_IMPLEMENTATION_PLAN.md** | 重构实施计划 | `docs/REFACTORING_IMPLEMENTATION_PLAN.md` |

### 数据集与基准测试

| 文档 | 描述 | 路径 |
|------|------|------|
| **BENCHMARK_DATASETS_DOWNLOAD_SUMMARY.md** | 基准数据集下载总结 | `docs/BENCHMARK_DATASETS_DOWNLOAD_SUMMARY.md` |
| **DATASET_DOWNLOAD_COMPLETE.md** | 数据集下载完成 | `docs/DATASET_DOWNLOAD_COMPLETE.md` |
| **flores200/README.md** | FLORES-200 数据集说明 | `data/benchmarks/flores200/README.md` |
| **mmlu/README.md** | MMLU 数据集说明 | `data/benchmarks/mmlu/README.md` |

### 项目管理

| 文档 | 描述 | 路径 |
|------|------|------|
| **getting_started.md** | 项目入门指南 | `docs/project/getting_started.md` |
| **collaboration_workflow.md** | 协作工作流程 | `docs/project/collaboration_workflow.md` |
| **version_control_strategy.md** | 版本控制策略 | `docs/project/version_control_strategy.md` |
| **product_requirements.md** | 产品需求文档 | `docs/project/product_requirements.md` |
| **research_progress_management.md** | 研究进度管理 | `docs/project/research_progress_management.md` |

---

## 问题修复

### 模型加载与量化问题

| 文档 | 描述 | 路径 |
|------|------|------|
| **HF_4BIT_QUANTIZATION_ISSUES_SUMMARY.md** | HF 4-bit 量化问题总结 | `docs/HF_4BIT_QUANTIZATION_ISSUES_SUMMARY.md` |
| **PHI3_4BIT_QUANTIZATION_FIX.md** | Phi-3 4-bit 量化修复 | `docs/PHI3_4BIT_QUANTIZATION_FIX.md` |
| **GPU_FIRST_LOADING_STRATEGY.md** | GPU 优先加载策略 | `docs/GPU_FIRST_LOADING_STRATEGY.md` |

### 实验执行问题

| 文档 | 描述 | 路径 |
|------|------|------|
| **EXPERIMENT_SUITE_ERROR_HANDLING_FIX.md** | 实验套件错误处理修复 | `docs/EXPERIMENT_SUITE_ERROR_HANDLING_FIX.md` |
| **TEMPERATURE_FIX.md** | Temperature 参数修复 | `docs/TEMPERATURE_FIX.md` |

### 其他技术问题

| 文档 | 描述 | 路径 |
|------|------|------|
| **NUMPY_FIX_AND_MODEL_DOWNLOAD_SUMMARY.md** | NumPy 修复和模型下载 | `docs/NUMPY_FIX_AND_MODEL_DOWNLOAD_SUMMARY.md` |

---

## 会话总结

### 开发会话记录

| 文档 | 描述 | 路径 |
|------|------|------|
| **SESSION_SUMMARY_ERROR_HANDLING_AND_QUANTIZATION.md** | 错误处理和量化会话总结 | `SESSION_SUMMARY_ERROR_HANDLING_AND_QUANTIZATION.md` |
| **SESSION_SUMMARY_EXPERIMENT_5.md** | Experiment 5 会话总结 | `SESSION_SUMMARY_EXPERIMENT_5.md` |
| **SESSION_SUMMARY_DATASET_DOWNLOAD.md** | 数据集下载会话总结 | `SESSION_SUMMARY_DATASET_DOWNLOAD.md` |
| **SESSION_SUMMARY_2026_03_02.md** | 2026-03-02 会话总结 | `docs/SESSION_SUMMARY_2026_03_02.md` |

### 功能更新总结

| 文档 | 描述 | 路径 |
|------|------|------|
| **EXPERIMENTS_UPDATE.md** | 实验功能更新 | `EXPERIMENTS_UPDATE.md` |
| **DOCUMENTATION_UPDATE_SUMMARY.md** | 文档更新总结 | `docs/DOCUMENTATION_UPDATE_SUMMARY.md` |
| **IDLE_BASELINE_UPDATE_SUMMARY.md** | 空闲基线更新总结 | `docs/IDLE_BASELINE_UPDATE_SUMMARY.md` |
| **MULTI_TURN_TEST_SUMMARY.md** | 多轮测试总结 | `docs/MULTI_TURN_TEST_SUMMARY.md` |
| **PER_TURN_MONITORING_IMPLEMENTATION.md** | 每轮监控实施 | `docs/PER_TURN_MONITORING_IMPLEMENTATION.md` |
| **TEST_CASE_CREATION_SUMMARY.md** | 测试用例创建总结 | `docs/experiment/TEST_CASE_CREATION_SUMMARY.md` |
| **UPDATE_SUMMARY.md** | 实验文档更新总结 | `docs/experiment/UPDATE_SUMMARY.md` |
| **SECTIONS_UPDATED.md** | 章节更新记录 | `docs/experiment/SECTIONS_UPDATED.md` |

---

## 参考资料

### 学术论文与研究

| 文档 | 描述 | 路径 |
|------|------|------|
| **paper.md** | 论文草稿 | `paper.md` |
| **pre_experiment_paper.md** | 实验前论文 | `docs/paper/pre_experiment_paper.md` |

### 文献综述

| 文档 | 描述 | 路径 |
|------|------|------|
| **领域认知与问题界定/paper_read.md** | 领域认知文献综述 | `docs/reference/领域认知与问题界定/paper_read.md` |
| **方法论基础构建/paper_read.md** | 方法论文献综述 | `docs/reference/方法论基础构建/paper_read.md` |
| **实验设计与实施/paper_read.md** | 实验设计文献综述 | `docs/reference/实验设计与实施/paper_read.md` |
| **研究创新点/paper_read.md** | 研究创新点文献综述 | `docs/reference/研究创新点/paper_read.md` |
| **价值分析与成果形成/paper_read.md** | 价值分析文献综述 | `docs/reference/价值分析与成果形成/paper_read.md` |
| **pay.md** | 支付相关参考 | `docs/reference/pay.md` |

---

## 工具文档

### BARTScore

| 文档 | 描述 | 路径 |
|------|------|------|
| **BARTScore_使用说明.md** | BARTScore 使用说明 | `BARTScore_使用说明.md` |
| **BARTScore/README.md** | BARTScore 主文档 | `tools/thesis_reproduction/BARTScore/README.md` |
| **BARTSCORE_USAGE_GUIDE.md** | BARTScore 使用指南 | `tools/thesis_reproduction/BARTScore/BARTScore_USAGE_GUIDE.md` |
| **DEPLOYMENT_SUMMARY.md** | BARTScore 部署总结 | `tools/thesis_reproduction/BARTScore/DEPLOYMENT_SUMMARY.md` |

### 其他工具

| 文档 | 描述 | 路径 |
|------|------|------|
| **Towards-Reward-Fairness/README.md** | 奖励公平性工具 | `tools/thesis_reproduction/Towards-Reward-Fairness/README.md` |

---

## 归档文档

### 分析与规划（已完成）

| 文档 | 描述 | 路径 | 状态 |
|------|------|------|------|
| **GAP_ANALYSIS_SUMMARY.md** | 差距分析总结 | `docs/GAP_ANALYSIS_SUMMARY.md` | ✅ 已完成 |
| **GAP_ANALYSIS_VISUAL.md** | 差距分析可视化 | `docs/GAP_ANALYSIS_VISUAL.md` | ✅ 已完成 |
| **README_GAP_ANALYSIS.md** | README 差距分析 | `docs/README_GAP_ANALYSIS.md` | ✅ 已完成 |
| **DATA_COLLECTION_GAP_ANALYSIS.md** | 数据收集差距分析 | `docs/DATA_COLLECTION_GAP_ANALYSIS.md` | ✅ 已完成 |
| **IMPLEMENTATION_PRIORITY.md** | 实施优先级 | `docs/IMPLEMENTATION_PRIORITY.md` | ✅ 已完成 |

### Trae 文档（AI 辅助生成）

| 文档 | 描述 | 路径 |
|------|------|------|
| **构建 experiments_1 多维质效比评估实验.md** | Experiments_1 构建文档 | `.trae/documents/构建 experiments_1 多维质效比评估实验.md` |
| **构建 experiments_1 数据分析与质效比评估报告.md** | Experiments_1 分析报告 | `.trae/documents/构建 experiments_1 数据分析与质效比评估报告.md` |
| **使用多元统计方法分析实验数据.md** | 多元统计分析文档 | `.trae/documents/使用多元统计方法分析实验数据.md` |
| **效质比实验管道与操作文档.md** | 实验管道文档 | `.trae/documents/效质比实验管道与操作文档（基于 Ollama + BARTScore）.md` |
| **撰写论文 paper.md 并整合实验分析结果.md** | 论文撰写文档 | `.trae/documents/撰写论文 paper.md 并整合实验分析结果.md` |

### 其他归档

| 文档 | 描述 | 路径 |
|------|------|------|
| **task.md** | 任务列表（旧） | `docs/task.md` |
| **REFACTORING_COMPLETE.md** | 重构完成（旧版本） | `REFACTORING_COMPLETE.md` |

---

## 📖 使用指南

### 新用户入门路径

1. **了解项目**：
   - 阅读 `README.md` - 项目概述
   - 阅读 `agents.md` - 项目目的和环境
   - 阅读 `.kiro/steering/product.md` - 产品定位

2. **环境设置**：
   - 阅读 `docs/project/getting_started.md` - 入门指南
   - 阅读 `HUGGINGFACE_SETUP.md` - 模型环境设置
   - 参考 `TROUBLESHOOTING.md` - 问题排查

3. **运行实验**：
   - 阅读 `docs/EXPERIMENT_RUNNER_GUIDE.md` - 实验执行
   - 阅读 `docs/experiment/experiment_design.md` - 实验设计
   - 参考 `docs/CONFIG_PARAMETERS_REFERENCE.md` - 配置参数

4. **模型选择**：
   - 阅读 `docs/MODEL_QUICK_REFERENCE.md` - 快速选择模型
   - 阅读 `docs/MODEL_BENCHMARKS_SUMMARY.md` - 详细对比

### 开发者路径

1. **架构理解**：
   - `docs/project/technical_architecture.md`
   - `project_structure.md`
   - `.kiro/steering/tech.md`

2. **代码贡献**：
   - `CONTRIBUTING.md`
   - `docs/project/collaboration_workflow.md`
   - `docs/project/version_control_strategy.md`

3. **问题修复**：
   - 查看 `docs/` 下的 `*_FIX.md` 文件
   - 参考 `TROUBLESHOOTING.md`

### 研究者路径

1. **实验设计**：
   - `docs/experiment/experiment_design.md`
   - `docs/experiment/metrics.md`
   - `docs/experiment/TEST_CASE_DESIGN_GUIDE.md`

2. **数据分析**：
   - `results/experiments_1/report.md`
   - `results/experiments_1/multivariate_analysis/multivariate_report.md`
   - `agents.md` - 分析方法说明

3. **论文撰写**：
   - `paper.md`
   - `docs/paper/pre_experiment_paper.md`
   - `docs/reference/` - 文献综述

---

## 🔍 快速查找

### 按主题查找

- **实验执行**: `EXPERIMENT_RUNNER_GUIDE.md`, `UNIFIED_RUNNER_GUIDE.md`
- **模型对比**: `MODEL_BENCHMARKS_SUMMARY.md`, `MODEL_QUICK_REFERENCE.md`
- **配置参数**: `CONFIG_PARAMETERS_REFERENCE.md`, `experiment_design.md`
- **问题排查**: `TROUBLESHOOTING.md`, `MODEL_QUALITY_ISSUES.md`
- **数据分析**: `report.md`, `multivariate_report.md`, `agents.md`

### 按文件类型查找

- **指南类**: `*_GUIDE.md`, `*_guide.md`
- **总结类**: `*_SUMMARY.md`, `*_summary.md`
- **修复类**: `*_FIX.md`, `*_fix.md`
- **参考类**: `*_REFERENCE.md`, `*_reference.md`
- **会话类**: `SESSION_SUMMARY_*.md`

---

## 📝 文档维护

### 文档更新原则

1. **及时更新**: 功能变更后立即更新相关文档
2. **版本标注**: 在文档末尾标注最后更新日期
3. **交叉引用**: 使用相对路径链接相关文档
4. **分类清晰**: 新文档放入正确的目录

### 文档命名规范

- **指南**: `*_GUIDE.md` 或 `*_guide.md`
- **总结**: `*_SUMMARY.md` 或 `*_summary.md`
- **参考**: `*_REFERENCE.md` 或 `*_reference.md`
- **修复**: `*_FIX.md` 或 `*_fix.md`
- **会话**: `SESSION_SUMMARY_*.md`

### 需要定期审查的文档

- `README.md` - 项目主文档
- `agents.md` - 环境和方法说明
- `docs/EXPERIMENT_RUNNER_GUIDE.md` - 实验执行指南
- `docs/MODEL_QUICK_REFERENCE.md` - 模型快速参考
- `TROUBLESHOOTING.md` - 问题排查

---

**最后更新**: 2026-03-03  
**维护者**: GenAI Power Analysis Team  
**文档总数**: 100+ Markdown 文件
