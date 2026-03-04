


## 3. 详细指标对比分析

### 3.1 功耗指标 (Power Metrics)

| 符号　　　| 设计要求　　　　　　　　　| 当前实现　　　　　　　　　 | 状态　 | 优先级 |
| -----------| ---------------------------| ----------------------------| --------| --------|
| P_idle　　| 空闲基线功耗　　　　　　　| ❌ 未实现　　　　　　　　　 | 缺失　 | 高　　 |
| P_inc　　 | 增量功耗 (P_avg - P_idle) | ❌ 未实现　　　　　　　　　 | 缺失　 | 高　　 |
| P_avg　　 | 平均功耗　　　　　　　　　| ✅ gpu_power_avg_w　　　　　| 已实现 | -　　　|
| P_peak　　| 峰值功耗　　　　　　　　　| ✅ gpu_power_peak_w (phase) | 已实现 | -　　　|
| P_prefill | Prefill阶段功耗　　　　　 | ⚠️ 需phase_analysis　　　　 | 部分　 | 中　　 |
| P_decode　| Decode阶段功耗　　　　　　| ⚠️ 需phase_analysis　　　　 | 部分　 | 中　　 |

**实现建议**:
1. 在实验开始前测量5-10秒的空闲功耗作为 P_idle
2. 计算 P_inc = P_avg - P_idle
3. 使用 get_phase_data() 获取 Prefill/Decode 阶段功耗

### 3.2 能耗指标 (Energy kens  # 每token能耗
E_prefill = phase_analysis['prefill']['gpu_energy_j']
E_decode = phase_analysis['decode']['gpu_energy_j']
```

### 3.3 时间指标 (Time Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| T_total | 总推理时间 | ✅ latency_s | 已实现 | - |
| T_prefill | Prefill时间 (TTFT) | ✅ first_token_time | 已实现 | - |
| T_decode | Decode时间 | ✅ decode_time | 已实现 | - |
| T_token | 每token平均时间 | ✅ tpot (1/toks_per_s) | 已实现 | - |

**状态**: ✅ 时间指标已完整实现

### 3.4 吞吐指标 (Throughput Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| Throughput | 吞吐量 (tokens/s) | ✅ toks_per_s | 已实现 | - |
| PPW | 每瓦性能 (tokens/s/W) | ❌ 未计算 | 缺失 | 高 |
| TPJ | 每焦耳tokens (tokens/J) | ❌ 未计算 | 缺失 | 高 |

**实现建议**:
```python
# 在 experiment_runner.py 或 analyze_experiments_1.py 中添加
PPW = toks_per_s / P_avg  # 每瓦性能
TPJ = output_tokens / E_total  # 能效比 (tokens/J)
```

### 3.5 质量指标 (Quality Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| Q_task | 任务特定质量分 | ⚠️ 部分实现 | 部分 | 高 |
| Acc | 准确率 (QA) | ❌ 未实现 | 缺失 | 高 |
| ROUGE | ROUGE分数 (Summary) | ❌ 未实现 | 缺失 | 高 |
| BARTScore | BARTScore | ✅ bartscore | 已实现 | - |
| BERTScore | BERTScore | ❌ 未实现 | 缺失 | 中 |
| Distinct | Distinct-n (Creative) | ⚠️ 部分实现 | 部分 | 中 |
| CodeCompile | 代码编译通过率 | ⚠️ 部分实现 | 部分 | 中 |
| CodeCorrect | 代码正确性 | ❌ 未实现 | 缺失 | 低 |

**当前实现**:
- ✅ BARTScore: 在 quality.py 中实现
- ⚠️ Distinct-2: 在 analyze_experiments_1.py 中从 raw JSON 读取
- ⚠️ CodeCompile: 在 analyze_experiments_1.py 中从 raw JSON 推断

**实现建议**:
1. 集成 ROUGE 评估 (使用 rouge-score 库)
2. 集成 BERTScore 评估 (使用 bert-score 库)
3. 为 QA 任务实现准确率计算 (需要标准答案)
4. 标准化 Distinct-n 和 CodeCompile 的计算流程

### 3.6 归一化指标 (Normalized Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| Q_norm | 归一化质量 | ✅ norm_quality | 已实现 | - |
| E_norm | 归一化能耗 | ✅ norm_energy | 已实现 | - |
| T_norm | 归一化时间 | ✅ norm_lat | 已实现 | - |
| L_norm | 归一化延迟 | ✅ norm_lat | 已实现 | - |
| P_norm | 归一化功耗 | ❌ 未实现 | 缺失 | 中 |

**实现方法**: 使用 Min-Max Scaling，按任务分组归一化
**状态**: 核心指标已实现，功耗归一化可补充

### 3.7 复合指标 (Composite Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| Eff_score | 效率得分 | ✅ efficiency_score | 已实现 | - |
| QE_ratio | 质效比 | ✅ qe_ratio | 已实现 | - |
| Score_final | 最终综合分 | ❌ 未实现 | 缺失 | 中 |
| QE_fair | 公平化质效比 | ✅ fair_quality_score | 已实现 | - |

**当前实现**:
```python
# efficiency_score = 0.4 × norm_tps + 0.3 × norm_lat + 0.3 × norm_energy
# qe_ratio = (norm_quality + 0.01) / (1.01 - efficiency_score)
# fair_quality_score = global_mean × (1 - λ × FG)
```

**实现建议**:
- Score_final 可以综合 QE_ratio、公平性、成本等多维度
- 考虑加权方案: Score_final = w1×QE_ratio + w2×(1-FG) + w3×(1-Cost_norm)

### 3.8 成本指标 (Cost Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| Cost_GPU | GPU成本 ($/h) | ❌ 未实现 | 缺失 | 低 |
| Cost_energy | 能源成本 ($/kWh) | ❌ 未实现 | 缺失 | 低 |
| CPQ | 每质量点成本 | ❌ 未实现 | 缺失 | 低 |
| CPT | 每token成本 | ❌ 未实现 | 缺失 | 低 |

**实现建议**:
```python
# 定义成本模型
GPU_COST_PER_HOUR = 0.5  # $/h (根据实际硬件调整)
ENERGY_COST_PER_KWH = 0.12  # $/kWh (根据地区调整)

Cost_GPU = (T_total / 3600) * GPU_COST_PER_HOUR
Cost_energy = (E_total / 3600000) * ENERGY_COST_PER_KWH  # J -> kWh
CPQ = (Cost_GPU + Cost_energy) / Q_task
CPT = (Cost_GPU + Cost_energy) / output_tokens
```

### 3.9 系统指标 (System Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| U_CPU | CPU利用率 | ✅ cpu_percent_avg | 已实现 | - |
| U_GPU | GPU利用率 | ✅ gpu_util_avg | 已实现 | - |
| M_GPU | GPU显存使用 | ✅ gpu_mem_peak_mb | 已实现 | - |
| T_GPU | GPU温度 | ✅ gpu_temp_peak_c | 已实现 | - |
| M_CPU | CPU内存使用 | ✅ mem_used_peak_mb | 已实现 | - |

**状态**: ✅ 系统指标已完整实现

### 3.10 公平性指标 (Fairness Metrics)

| 符号 | 设计要求 | 当前实现 | 状态 | 优先级 |
|------|---------|---------|------|--------|
| FG | Fairness Gap | ✅ fairness_gap | 已实现 | - |
| Gini | Gini系数 | ✅ gini | 已实现 | - |
| Theil | Theil指数 | ✅ theil | 已实现 | - |
| NSW | Nash Social Welfare | ✅ nsw | 已实现 | - |
| Envy | 嫉妒率 | ❌ 未实现 | 缺失 | 低 |

**状态**: 核心公平性指标已实现，嫉妒率可选实现

## 4. 优先级分类总结

### 4.1 高优先级缺失项 (需立即实现)

1. **基线功耗测量 (P_idle)**
   - 影响: 无法计算增量功耗 P_inc
   - 实现: 实验前测量5-10秒空闲功耗

2. **每token能耗 (E_token)**
   - 影响: 无法评估token级能效
   - 实现: E_token = E_total / output_tokens

3. **每瓦性能 (PPW) 和能效比 (TPJ)**
   - 影响: 缺少关键能效指标
   - 实现: PPW = toks_per_s / P_avg; TPJ = output_tokens / E_total

4. **ROUGE 和准确率 (Acc)**
   - 影响: QA/Summary 任务质量评估不完整
   - 实现: 集成 rouge-score 库，实现答案匹配逻辑

### 4.2 中优先级缺失项 (建议实现)

1. **BERTScore**
   - 影响: 缺少语义相似度评估
   - 实现: 集成 bert-score 库

2. **阶段能耗分析 (E_prefill, E_decode)**
   - 影响: 无法分析Prefill/Decode能耗分布
   - 实现: 使用 get_phase_data() 方法

3. **最终综合分 (Score_final)**
   - 影响: 缺少统一的模型排名指标
   - 实现: 设计加权方案综合多维度指标

4. **功耗归一化 (P_norm)**
   - 影响: 功耗对比不直观
   - 实现: 按任务分组 Min-Max 归一化

### 4.3 低优先级缺失项 (可选实现)

1. **成本指标 (Cost_GPU, Cost_energy, CPQ, CPT)**
   - 影响: 缺少经济性分析
   - 实现: 定义成本模型并计算

2. **代码正确性 (CodeCorrect)**
   - 影响: 代码质量评估不完整
   - 实现: 需要测试用例和执行环境

3. **嫉妒率 (Envy)**
   - 影响: 公平性分析不够全面
   - 实现: 随机两群体比较质量差异

## 5. 数据流程改进建议

### 5.1 当前数据流程

```
实验执行 (experiment_runner.py)
  ↓
原始数据 (raw/*.json)
  ↓
汇总数据 (summary/results.csv, stats.csv)
  ↓
数据分析 (analyze_experiments_1.py)
  ↓
可视化报告 (figures/*.png, report.md)
```

### 5.2 建议改进流程

```
实验执行 (experiment_runner.py)
  ├─ 空闲基线测量 (P_idle, E_idle)
  ├─ 推理执行 + 事件标记
  ├─ 阶段能耗分析 (Prefill/Decode)
  └─ 计算衍生指标 (E_token, PPW, TPJ)
  ↓
原始数据 (raw/*.json) [增强字段]
  ↓
质量评估 (quality.py)
  ├─ BARTScore
  ├─ ROUGE (新增)
  ├─ BERTScore (新增)
  ├─ Distinct-n (标准化)
  └─ Accuracy (新增)
  ↓
汇总数据 (summary/results.csv) [扩展字段]
  ↓
数据分析 (analyze_experiments_1.py)
  ├─ 归一化指标
  ├─ 复合指标
  ├─ 公平性指标
  └─ 成本指标 (新增)
  ↓
可视化报告 (figures/*.png, report.md)
```

### 5.3 数据结构扩展建议

**results.csv 新增字段**:
```csv
# 功耗指标
P_idle, P_inc, P_prefill, P_decode

# 能耗指标
E_token, E_prefill, E_decode, E_inc

# 吞吐指标
PPW, TPJ

# 质量指标
ROUGE_1, ROUGE_2, ROUGE_L, BERTScore_F1, Accuracy, Distinct_1, Distinct_2

# 成本指标
Cost_GPU, Cost_energy, CPQ, CPT

# 归一化指标
P_norm

# 复合指标
Score_final
```

## 6. 实现路线图

### Phase 1: 核心指标补全 (1-2周)
- [ ] 实现空闲基线功耗测量
- [ ] 计算 E_token, PPW, TPJ
- [ ] 集成 ROUGE 评估
- [ ] 实现 QA 准确率计算
- [ ] 标准化 Distinct-n 和 CodeCompile

### Phase 2: 高级指标集成 (2-3周)
- [ ] 集成 BERTScore
- [ ] 实现阶段能耗分析 (Prefill/Decode)
- [ ] 设计并实现 Score_final
- [ ] 添加功耗归一化

### Phase 3: 成本与优化 (1-2周)
- [ ] 实现成本模型
- [ ] 优化数据流程
- [ ] 完善可视化报告
- [ ] 添加更多公平性指标

### Phase 4: 文档与测试 (1周)
- [ ] 更新文档
- [ ] 编写单元测试
- [ ] 性能优化
- [ ] 用户指南

## 7. 技术依赖

### 新增 Python 包
```bash
pip install rouge-score  # ROUGE 评估
pip install bert-score   # BERTScore 评估
pip install scipy        # 统计分析
```

### 配置文件更新
- `experiments/config.py`: 添加成本模型参数
- `data/experiments_N/config.json`: 扩展配置字段

## 8. 风险与挑战

1. **向后兼容性**: 新增字段需保持与现有数据的兼容
2. **计算开销**: BERTScore 等指标计算较慢，需考虑批处理
3. **数据质量**: 需要标准答案才能计算准确率
4. **成本模型**: 不同硬件和地区的成本差异大，需参数化

## 9. 下一步行动

1. **立即行动**: 实现 Phase 1 的核心指标补全
2. **代码审查**: 确认当前实现的准确性
3. **测试验证**: 使用小规模数据验证新指标
4. **文档更新**: 同步更新 experiment_design.md

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**最后更新**: 2026-03-02  
**作者**: Kiro AI Assistant
