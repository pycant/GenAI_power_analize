# QE Research 分析状态总结

**更新时间**: 2026-03-06

---

## 已完成的分析任务

### 1. 质量数据分析 (Quality Data Analysis) ✅

**状态**: 已完成并修复

**位置**: `analysis/qe_research/results/quality_analysis/`

**生成图表**: 8/10 张
- ✅ Task 1: 任务类型分布
- ✅ Task 2: 模型性能对比
- ❌ Task 3: 质量指标相关性（数据不足）
- ✅ Task 4: 各任务质量分布
- ✅ Task 5: 编译成功率对比
- ❌ Task 6: 质量-效率散点图（数据不足）
- ✅ Task 7: 综合质量雷达图
- ✅ Task 8: 质量指标热力图
- ✅ Task 9: 任务难度分析
- ✅ Task 10: 模型稳定性分析

**关键修复**:
- 更新了列名检测逻辑，适配新的数据格式
- 从简单列名（`compilation_rate_mean`）更新为详细列名（`functional_correctness_mean`, `compilation_success_mean`）
- 添加了向后兼容性支持

**脚本**: `analysis/qe_research/scripts/quality_data_analyzer.py`

---

### 2. 原始数据分析 (Raw Data Analysis) ✅

**状态**: 已完成并验证

**位置**: `analysis/qe_research/results/raw_analysis/`

**生成图表**: 10/10 张
- ✅ Task 1: 模型性能对比
- ✅ Task 2: 能耗效率分析
- ✅ Task 3: TTFT分布（仅4个模型有数据）
- ✅ Task 4: 吞吐量-延迟关系
- ✅ Task 5: GPU利用率分析
- ✅ Task 6: 内存使用分析
- ✅ Task 7: 温度监控
- ✅ Task 8: 任务类型对比
- ✅ Task 9: 质效比分析
- ✅ Task 10: 综合性能雷达图

**关键发现**:
- TTFT数据仅在4个Ollama模型中可用（gemma3:4b, deepseek-r1:8b, qwen3:8b, qwen3:4b）
- HuggingFace模型缺少`first_token`事件记录
- 数据访问方法已验证正确

**脚本**: `analysis/qe_research/scripts/raw_data_analyzer_complete.py`

---

### 3. 任务功率曲线分析 (Task Power Curves) ✅

**状态**: 新完成

**位置**: `analysis/qe_research/results/task_power_analysis/`

**生成图表**: 9/9 张
- ✅ code任务功率曲线
- ✅ creative任务功率曲线
- ✅ math任务功率曲线
- ✅ multi_turn任务功率曲线
- ✅ qa任务功率曲线
- ✅ reasoning任务功率曲线
- ✅ summary任务功率曲线
- ✅ translation任务功率曲线
- ✅ 平均功率对比

**关键特性**:
- 按任务类型分组对比不同模型的GPU/CPU功率变化
- 支持新旧两种数据格式（dict和list）
- 使用学术配色方案和300 DPI输出
- 显示功率随时间的动态变化曲线

**脚本**: `analysis/qe_research/scripts/plot_task_power_curves.py`

**运行方式**:
```bash
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/plot_task_power_curves.py
```

---

### 4. 模型性能指标对比表格 (Metric Tables) ✅

**状态**: 新完成

**位置**: `analysis/qe_research/results/metric_tables/`

**生成表格**: 6/6 个CSV文件
- ✅ 01_avg_gpu_energy.csv - 平均GPU能耗 (J)
- ✅ 02_avg_output_tokens.csv - 平均回答token数量
- ✅ 03_ttft.csv - 首token延迟 (ms)
- ✅ 04_avg_response_time.csv - 平均回答时间 (s)
- ✅ 05_avg_gpu_memory.csv - 平均显存占用 (MB)
- ✅ 06_avg_gpu_utilization.csv - 平均GPU占用率 (%)

**表格格式**:
- 行标题: 任务类型 (code, creative, math, multi_turn, qa, reasoning, summary, translation)
- 列标题: 模型名称 (12个模型)
- 数值: 该模型-任务组合的平均值

**关键发现**:
- 能耗覆盖率: 100% (所有实验都有数据)
- TTFT覆盖率: 15.7% (仅Ollama模型)
- 最节能模型: gemma3:4b
- 最快响应: gemma3:4b
- 最小显存: google--gemma-2b-it:4bit (约2.6-3.0 GB)

**脚本**: `analysis/qe_research/scripts/create_metric_tables.py`

**运行方式**:
```bash
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/create_metric_tables.py
# 或使用批处理脚本
analysis\qe_research\scripts\run_create_metric_tables.bat
```

---

## 数据结构说明

### 实验数据位置
- 原始数据: `data/{model_name}/experiment_results_*_raw.json`
- 汇总数据: `data/{model_name}/experiment_results_*_summary.json`

### 数据格式变化

**Measurements 结构**:
- **新格式** (dict): `{"timestamps": [...], "gpu_power_w": [...], "cpu_percent": [...]}`
- **旧格式** (list): `[{"timestamp": ..., "gpu_power_w": ..., "cpu_percent": ...}, ...]`

**Quality 列名**:
- **新格式**: `functional_correctness_mean`, `compilation_success_mean`, `code_quality_mean`
- **旧格式**: `compilation_rate_mean`, `overall_score`

---

## 数据覆盖情况

### 总体统计
- **总实验数**: 446
- **模型数量**: 12
- **任务类型**: 8 (code, creative, math, multi_turn, qa, reasoning, summary, translation)

### 模型列表
1. deepseek-r1:8b (Ollama, Q4_K_M)
2. gemma3:4b (Ollama, Q4_K_M)
3. qwen3:8b (Ollama, Q4_K_M)
4. qwen3:4b (Ollama, Q4_K_M)
5. Qwen2.5-7B-Instruct (HF, 4bit)
6. Qwen2.5-3B-Instruct (HF, 4bit)
7. Phi-3-mini-4k-instruct (HF, 4bit)
8. gemma-2b-it (HF, 4bit)
9. Mistral-7B-Instruct-v0.3 (HF, 4bit)
10. Llama-3.2-3B-Instruct (HF, 4bit)
11. Qwen2.5-Coder-7B-Instruct (HF, 4bit)
12. deepseek-coder-6.7b-instruct (HF, 4bit)

### TTFT数据覆盖
- **有完整TTFT数据**: 4个Ollama模型
- **缺少TTFT数据**: 8个HuggingFace模型
- **原因**: HF模型监控未记录`first_token`事件

---

### 4. 任务-模型透视表 (Pivot Tables) ✅

**状态**: 新完成

**位置**: `analysis/qe_research/results/pivot_tables/`

**生成表格**: 6个CSV文件（每个都有格式化版和原始版）
- ✅ 表1: 平均GPU能耗 (J)
- ✅ 表2: 平均回答token数量
- ✅ 表3: 首token延迟 (ms)
- ✅ 表4: 平均回答时间 (s)
- ✅ 表5: 平均显存占用 (MB)
- ✅ 表6: 平均GPU占用 (%)

**表格格式**:
- 行标题：任务类型 (code, creative, math, multi_turn, qa, reasoning, summary, translation)
- 列标题：模型名称
- 数值：该模型在该任务上的平均值
- N/A：表示该模型-任务组合没有数据

**关键特性**:
- 每个表格提供两个版本：格式化版（便于阅读）和原始版（便于计算）
- 自动从raw.json文件提取和计算指标
- 支持Excel和Python pandas直接读取
- 包含汇总报告说明数据来源和使用方法

**脚本**: `analysis/qe_research/scripts/create_pivot_tables.py`

**运行方式**:
```bash
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/create_pivot_tables.py
# 或使用批处理脚本
analysis\qe_research\scripts\run_pivot_tables.bat
```

---

## 待完成任务

### 1. 综合分析报告
- 整合所有分析结果
- 生成跨任务、跨模型的综合对比
- 提供能效评级建议

### 2. 数据管道优化
- 实施数据结构重构方案（参考`analysis/DATA_STRUCTURE_REFACTORING.md`）
- 转换为Parquet格式提升性能
- 建立统一的数据访问接口

### 3. 公平性分析
- 实施RLHF公平性评估（参考`AGENTS.md`中的文献启示）
- 计算群体公平差距（Fairness Gap）
- 添加Nash Social Welfare聚合

### 4. HuggingFace模型TTFT修复
- 修改HF模型监控代码，添加`first_token`事件记录
- 重新运行实验收集完整TTFT数据

---

## 快速运行指南

### 运行质量分析
```bash
conda activate bartscore
set PYTHONUTF8=1
cd analysis/qe_research
python scripts/quality_data_analyzer.py
```

### 运行原始数据分析
```bash
conda activate bartscore
set PYTHONUTF8=1
cd analysis/qe_research
scripts\run_raw_analysis.bat
```

### 运行任务功率分析
```bash
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/plot_task_power_curves.py
```

### 生成透视表
```bash
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/create_pivot_tables.py
# 或使用批处理脚本
analysis\qe_research\scripts\run_pivot_tables.bat
```

### 运行综合分析
```bash
conda activate bartscore
set PYTHONUTF8=1
cd analysis/qe_research
python scripts/comprehensive_analysis.py
```

---

## 相关文档

- [数据管道系统](../数据管道系统.md)
- [数据结构重构方案](../DATA_STRUCTURE_REFACTORING.md)
- [指标说明文档](../METRICS_GUIDE.md)
- [质量数据分析文档](docs/quality_data_analize.md)
- [原始数据分析文档](docs/raw_data_analize.md)
- [Agents使用指南](../../AGENTS.md)

---

**文档维护**: Kiro AI Assistant  
**最后更新**: 2026-03-06
