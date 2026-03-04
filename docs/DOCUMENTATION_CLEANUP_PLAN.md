# 文档整理与清理计划

本文档提供项目文档的整理建议和清理方案。

## 📊 当前状态

### 文档统计

- **总文档数**: 100+ Markdown 文件
- **核心文档**: ~15 个
- **实验相关**: ~25 个
- **模型相关**: ~10 个
- **技术文档**: ~20 个
- **会话总结**: ~10 个
- **归档文档**: ~20 个

### 存在的问题

1. **文档分散**: 文档分布在多个目录，不易查找
2. **重复内容**: 部分文档内容重复或过时
3. **命名不统一**: 文档命名规范不一致
4. **缺少索引**: 没有统一的文档导航
5. **会话总结过多**: 大量临时会话总结文件

---

## 🎯 整理目标

1. **建立清晰的文档层次结构**
2. **删除过时和重复的文档**
3. **统一文档命名规范**
4. **创建文档索引和导航**
5. **归档历史文档**

---

## 📁 建议的目录结构

```
docs/
├── README.md                          # 文档目录说明
├── DOCUMENTATION_INDEX.md             # 文档索引（新建）✅
│
├── guides/                            # 用户指南
│   ├── getting_started.md            # 快速开始
│   ├── experiment_guide.md           # 实验指南（整合）
│   ├── model_selection_guide.md      # 模型选择指南（整合）
│   └── troubleshooting.md            # 问题排查
│
├── reference/                         # 参考文档
│   ├── config_parameters.md          # 配置参数
│   ├── metrics.md                    # 指标说明
│   ├── model_benchmarks.md           # 模型基准测试
│   └── api_reference.md              # API 参考
│
├── technical/                         # 技术文档
│   ├── architecture.md               # 架构设计
│   ├── data_structure.md             # 数据结构
│   ├── implementation/               # 实现细节
│   │   ├── multi_turn.md
│   │   ├── idle_baseline.md
│   │   └── monitoring.md
│   └── fixes/                        # 问题修复记录
│       ├── quantization_issues.md
│       ├── gpu_loading.md
│       └── temperature_fix.md
│
├── experiment/                        # 实验相关（保持现有）
│   ├── experiment_design.md
│   ├── experiment_operation_guide.md
│   ├── hf_models_guide.md
│   ├── metrics.md
│   └── user_guide.md
│
├── project/                           # 项目管理（保持现有）
│   ├── collaboration_workflow.md
│   ├── getting_started.md
│   ├── product_requirements.md
│   ├── research_progress_management.md
│   ├── technical_architecture.md
│   └── version_control_strategy.md
│
├── paper/                             # 论文相关（保持现有）
│   └── pre_experiment_paper.md
│
├── reference/                         # 文献综述（保持现有）
│   ├── 领域认知与问题界定/
│   ├── 方法论基础构建/
│   ├── 实验设计与实施/
│   ├── 研究创新点/
│   └── 价值分析与成果形成/
│
└── archive/                           # 归档文档（新建）
    ├── sessions/                     # 会话总结
    │   ├── 2026-03-02_session.md
    │   ├── error_handling_quantization.md
    │   ├── experiment_5.md
    │   └── dataset_download.md
    ├── completed/                    # 已完成任务
    │   ├── gap_analysis/
    │   ├── refactoring/
    │   └── experiments/
    └── deprecated/                   # 已废弃文档
        └── old_guides/
```

---

## 🗂️ 文档整理方案

### Phase 1: 创建新结构（已完成部分）

✅ **已完成**:
- [x] 创建 `DOCUMENTATION_INDEX.md`
- [x] 创建 `MODEL_BENCHMARKS_SUMMARY.md`
- [x] 创建 `MODEL_QUICK_REFERENCE.md`

⏳ **待完成**:
- [ ] 创建 `docs/guides/` 目录
- [ ] 创建 `docs/reference/` 目录（与现有 reference 区分）
- [ ] 创建 `docs/technical/` 目录
- [ ] 创建 `docs/archive/` 目录

### Phase 2: 整合重复文档

#### 实验指南整合

**目标**: 将多个实验相关指南整合为统一文档

**源文档**:
- `docs/EXPERIMENT_RUNNER_GUIDE.md`
- `experiments/UNIFIED_RUNNER_GUIDE.md`
- `docs/QUICK_START_NEW_FORMAT.md`
- `docs/experiment/experiment_operation_guide.md`

**目标文档**:
- `docs/guides/experiment_guide.md` - 统一实验指南

**整合内容**:
1. 快速开始
2. 实验配置
3. 执行实验
4. 结果分析
5. 常见问题

#### 模型指南整合

**目标**: 整合模型相关文档

**源文档**:
- `docs/MODEL_BENCHMARKS_SUMMARY.md` ✅
- `docs/MODEL_QUICK_REFERENCE.md` ✅
- `docs/MODEL_QUALITY_ISSUES.md`
- `docs/experiment/hf_models_guide.md`
- `HUGGINGFACE_SETUP.md`

**目标文档**:
- `docs/guides/model_selection_guide.md` - 模型选择指南
- `docs/reference/model_benchmarks.md` - 基准测试参考
- `docs/technical/model_issues.md` - 模型问题记录

#### 配置参数整合

**源文档**:
- `docs/CONFIG_PARAMETERS_REFERENCE.md`
- `docs/experiment/experiment_design.md` (部分)

**目标文档**:
- `docs/reference/config_parameters.md`

### Phase 3: 归档历史文档

#### 会话总结归档

**移动到 `docs/archive/sessions/`**:
- `SESSION_SUMMARY_ERROR_HANDLING_AND_QUANTIZATION.md`
- `SESSION_SUMMARY_EXPERIMENT_5.md`
- `SESSION_SUMMARY_DATASET_DOWNLOAD.md`
- `docs/SESSION_SUMMARY_2026_03_02.md`

#### 已完成任务归档

**移动到 `docs/archive/completed/`**:

**Gap Analysis**:
- `docs/GAP_ANALYSIS_SUMMARY.md`
- `docs/GAP_ANALYSIS_VISUAL.md`
- `docs/README_GAP_ANALYSIS.md`
- `docs/DATA_COLLECTION_GAP_ANALYSIS.md`
- `docs/IMPLEMENTATION_PRIORITY.md`

**Refactoring**:
- `REFACTORING_SUMMARY.md`
- `REFACTORING_COMPLETE.md`
- `docs/REFACTORING_COMPLETED.md`
- `docs/REFACTORING_IMPLEMENTATION_PLAN.md`
- `docs/DATA_REFACTORING_SUMMARY.md`
- `docs/DATA_REFACTORING_IMPLEMENTATION.md`
- `docs/DATA_STRUCTURE_REFACTORING.md`
- `docs/DATA_STRUCTURE_COMPARISON.md`

**Experiments**:
- `EXPERIMENT_5_READY.md`
- `docs/EXPERIMENT_5_SETUP.md`
- `docs/EXPERIMENT_5_CONFIGURATION_COMPLETE.md`
- `docs/TEST_CASES_READY.md`
- `docs/TEST_RESULTS.md`

**Updates**:
- `EXPERIMENTS_UPDATE.md`
- `docs/DOCUMENTATION_UPDATE_SUMMARY.md`
- `docs/IDLE_BASELINE_UPDATE_SUMMARY.md`
- `docs/MULTI_TURN_TEST_SUMMARY.md`
- `docs/PER_TURN_MONITORING_IMPLEMENTATION.md`
- `docs/experiment/TEST_CASE_CREATION_SUMMARY.md`
- `docs/experiment/UPDATE_SUMMARY.md`
- `docs/experiment/SECTIONS_UPDATED.md`

#### 技术修复归档

**移动到 `docs/technical/fixes/`**:
- `docs/HF_4BIT_QUANTIZATION_ISSUES_SUMMARY.md`
- `docs/PHI3_4BIT_QUANTIZATION_FIX.md`
- `docs/GPU_FIRST_LOADING_STRATEGY.md`
- `docs/EXPERIMENT_SUITE_ERROR_HANDLING_FIX.md`
- `docs/TEMPERATURE_FIX.md`
- `docs/NUMPY_FIX_AND_MODEL_DOWNLOAD_SUMMARY.md`

### Phase 4: 删除过时文档

**建议删除**:
- `docs/task.md` - 已过时的任务列表
- `REFACTORING_COMPLETE.md` - 与 `docs/REFACTORING_COMPLETED.md` 重复

**需要确认后删除**:
- `.trae/documents/*.md` - AI 生成的临时文档（如果已整合到正式文档）

### Phase 5: 更新主文档

**需要更新的文档**:

1. **README.md**:
   - 添加文档索引链接
   - 更新快速开始部分
   - 添加模型选择指南链接

2. **agents.md**:
   - 添加文档导航部分
   - 更新关键文件链接
   - 添加模型基准测试链接

3. **TROUBLESHOOTING.md**:
   - 整合各个 FIX 文档的内容
   - 添加模型质量问题部分
   - 添加常见错误索引

---

## 🔧 执行步骤

### 步骤 1: 备份（可选）

```bash
# 创建文档备份
mkdir -p backup/docs_$(date +%Y%m%d)
cp -r docs backup/docs_$(date +%Y%m%d)/
cp *.md backup/docs_$(date +%Y%m%d)/
```

### 步骤 2: 创建新目录结构

```bash
# 创建新目录
mkdir -p docs/guides
mkdir -p docs/reference
mkdir -p docs/technical/fixes
mkdir -p docs/technical/implementation
mkdir -p docs/archive/sessions
mkdir -p docs/archive/completed/gap_analysis
mkdir -p docs/archive/completed/refactoring
mkdir -p docs/archive/completed/experiments
mkdir -p docs/archive/completed/updates
mkdir -p docs/archive/deprecated
```

### 步骤 3: 移动会话总结

```bash
# 移动会话总结到归档
mv SESSION_SUMMARY_ERROR_HANDLING_AND_QUANTIZATION.md docs/archive/sessions/
mv SESSION_SUMMARY_EXPERIMENT_5.md docs/archive/sessions/
mv SESSION_SUMMARY_DATASET_DOWNLOAD.md docs/archive/sessions/
mv docs/SESSION_SUMMARY_2026_03_02.md docs/archive/sessions/
```

### 步骤 4: 归档已完成任务

```bash
# Gap Analysis
mv docs/GAP_ANALYSIS_*.md docs/archive/completed/gap_analysis/
mv docs/README_GAP_ANALYSIS.md docs/archive/completed/gap_analysis/
mv docs/DATA_COLLECTION_GAP_ANALYSIS.md docs/archive/completed/gap_analysis/
mv docs/IMPLEMENTATION_PRIORITY.md docs/archive/completed/gap_analysis/

# Refactoring
mv REFACTORING_*.md docs/archive/completed/refactoring/
mv docs/REFACTORING_*.md docs/archive/completed/refactoring/
mv docs/DATA_REFACTORING_*.md docs/archive/completed/refactoring/
mv docs/DATA_STRUCTURE_*.md docs/archive/completed/refactoring/

# Experiments
mv EXPERIMENT_5_READY.md docs/archive/completed/experiments/
mv docs/EXPERIMENT_5_*.md docs/archive/completed/experiments/
mv docs/TEST_CASES_READY.md docs/archive/completed/experiments/
mv docs/TEST_RESULTS.md docs/archive/completed/experiments/

# Updates
mv EXPERIMENTS_UPDATE.md docs/archive/completed/updates/
mv docs/DOCUMENTATION_UPDATE_SUMMARY.md docs/archive/completed/updates/
mv docs/IDLE_BASELINE_UPDATE_SUMMARY.md docs/archive/completed/updates/
mv docs/MULTI_TURN_TEST_SUMMARY.md docs/archive/completed/updates/
mv docs/PER_TURN_MONITORING_IMPLEMENTATION.md docs/archive/completed/updates/
mv docs/experiment/TEST_CASE_CREATION_SUMMARY.md docs/archive/completed/updates/
mv docs/experiment/UPDATE_SUMMARY.md docs/archive/completed/updates/
mv docs/experiment/SECTIONS_UPDATED.md docs/archive/completed/updates/
```

### 步骤 5: 移动技术修复文档

```bash
# 移动修复文档
mv docs/HF_4BIT_QUANTIZATION_ISSUES_SUMMARY.md docs/technical/fixes/
mv docs/PHI3_4BIT_QUANTIZATION_FIX.md docs/technical/fixes/
mv docs/GPU_FIRST_LOADING_STRATEGY.md docs/technical/fixes/
mv docs/EXPERIMENT_SUITE_ERROR_HANDLING_FIX.md docs/technical/fixes/
mv docs/TEMPERATURE_FIX.md docs/technical/fixes/
mv docs/NUMPY_FIX_AND_MODEL_DOWNLOAD_SUMMARY.md docs/technical/fixes/
```

### 步骤 6: 移动实现文档

```bash
# 移动实现细节文档
mv docs/MULTI_TURN_CONVERSATION_GUIDE.md docs/technical/implementation/
mv docs/IDLE_BASELINE_MEASUREMENT.md docs/technical/implementation/
mv docs/IDLE_BASELINE_QUICK_REFERENCE.md docs/technical/implementation/
mv docs/PER_TURN_MONITORING_GUIDE.md docs/technical/implementation/
mv docs/TTFT_AND_TOKEN_TRACKING_IMPROVEMENTS.md docs/technical/implementation/
```

### 步骤 7: 删除过时文档

```bash
# 删除过时文档
rm docs/task.md
rm REFACTORING_COMPLETE.md  # 保留 docs/REFACTORING_COMPLETED.md
```

### 步骤 8: 更新文档链接

需要手动更新以下文档中的链接：
- `README.md`
- `agents.md`
- `TROUBLESHOOTING.md`
- `docs/DOCUMENTATION_INDEX.md`

---

## 📝 整合文档内容建议

### 实验指南整合

创建 `docs/guides/experiment_guide.md`，整合以下内容：

```markdown
# 实验执行完整指南

## 快速开始
（来自 QUICK_START_NEW_FORMAT.md）

## 实验配置
（来自 EXPERIMENT_RUNNER_GUIDE.md）

## 执行实验
（来自 UNIFIED_RUNNER_GUIDE.md）

## 高级功能
- 多轮对话（来自 MULTI_TURN_CONVERSATION_GUIDE.md）
- 空闲基线（来自 IDLE_BASELINE_MEASUREMENT.md）
- 每轮监控（来自 PER_TURN_MONITORING_GUIDE.md）

## 结果分析
（来自 experiment_operation_guide.md）

## 常见问题
（来自各个文档的 FAQ 部分）
```

### 模型选择指南整合

创建 `docs/guides/model_selection_guide.md`，整合以下内容：

```markdown
# 模型选择完整指南

## 快速参考
（来自 MODEL_QUICK_REFERENCE.md）

## 模型对比
（来自 MODEL_BENCHMARKS_SUMMARY.md）

## HuggingFace 模型
（来自 hf_models_guide.md 和 HUGGINGFACE_SETUP.md）

## 常见问题
（来自 MODEL_QUALITY_ISSUES.md）

## 故障排除
（来自各个 FIX 文档）
```

---

## ✅ 验证清单

整理完成后，验证以下内容：

- [ ] 所有文档都有正确的分类
- [ ] 文档索引已更新
- [ ] 主文档（README.md, agents.md）已更新链接
- [ ] 没有断开的链接
- [ ] 归档文档已正确移动
- [ ] 过时文档已删除
- [ ] 新的目录结构清晰易懂

---

## 🎯 预期效果

整理后的文档结构将：

1. **更易导航**: 清晰的目录结构和索引
2. **减少冗余**: 删除重复和过时内容
3. **提高可维护性**: 统一的命名和组织方式
4. **改善用户体验**: 快速找到需要的文档
5. **便于协作**: 明确的文档分类和归档策略

---

## 📅 实施时间表

- **Phase 1**: 创建新结构 - 1 小时
- **Phase 2**: 整合文档 - 2-3 小时
- **Phase 3**: 归档历史文档 - 1 小时
- **Phase 4**: 删除过时文档 - 30 分钟
- **Phase 5**: 更新主文档 - 1 小时

**总计**: 约 5-6 小时

---

## ⚠️ 注意事项

1. **备份**: 在开始整理前备份所有文档
2. **链接更新**: 移动文档后需要更新所有引用链接
3. **Git 历史**: 使用 `git mv` 而不是直接移动，保留文件历史
4. **团队沟通**: 整理前通知团队成员，避免冲突
5. **分步执行**: 不要一次性完成所有整理，分阶段进行

---

**创建日期**: 2026-03-03  
**维护者**: GenAI Power Analysis Team  
**状态**: 待执行
