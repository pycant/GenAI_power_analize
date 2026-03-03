# 数据采集改进实施优先级清单

## 快速概览

本文档提供数据采集缺失项的快速参考和实施检查清单。详细分析请参考 [DATA_COLLECTION_GAP_ANALYSIS.md](./DATA_COLLECTION_GAP_ANALYSIS.md)。

## 🔴 高优先级 (立即实施)

### 1. 基线功耗测量 (P_idle) ✅ 已完成
- **文件**: `experiments/experiment_runner.py`
- **状态**: ✅ 已实现
- **实现方式**:
  - 添加 `measure_idle_baseline()` 方法
  - 在测试用例JSON中添加 `idle_measurement_duration` 参数
  - 自动计算增量指标：P_inc, E_inc, E_token, PPW, TPJ
- **使用方法**:
  ```json
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompts": ["什么是Python？"],
    "task_type": "qa",
    "idle_measurement_duration": 10
  }
  ```
- **文档**: [空闲基线测量功能说明](./IDLE_BASELINE_MEASUREMENT.md)

### 2. 每Token能耗 (E_token) ✅ 已完成
- **文件**: `experiments/experiment_runner.py`
- **状态**: ✅ 已实现（作为空闲基线测量的一部分）
- **实现方式**:
  ```python
  E_token = E_inc / output_tokens
  result['resources']['E_token'] = E_token
  ```
- **说明**: 使用增量能耗计算，更准确地反映模型推理的实际能耗

### 3. 每瓦性能 (PPW) 和能效比 (TPJ) ✅ 已完成
- **文件**: `experiments/experiment_runner.py`
- **状态**: ✅ 已实现（作为空闲基线测量的一部分）
- **实现方式**:
  ```python
  PPW = toks_per_s / P_avg  # tokens/s/W
  TPJ = output_tokens / E_total  # tokens/J
  result['resources']['PPW'] = PPW
  result['resources']['TPJ'] = TPJ
  ```
- **说明**: 自动计算并保存到结果中

### 4. ROUGE 评估
- **文件**: `experiments/quality.py`
- **依赖**: `pip install rouge-score`
- **实现**:
  ```python
  from rouge_score import rouge_scorer
  
  def rouge_scores(reference, hypothesis):
      scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
      scores = scorer.score(reference, hypothesis)
      return {
          'rouge1': scores['rouge1'].fmeasure,
          'rouge2': scores['rouge2'].fmeasure,
          'rougeL': scores['rougeL'].fmeasure
      }
  ```
- **影响**: Summary任务质量评估不完整

### 5. QA准确率 (Accuracy)
- **文件**: `experiments/quality.py`
- **实现**:
  ```python
  def qa_accuracy(reference, hypothesis, method='exact_match'):
      if method == 'exact_match':
          return 1.0 if reference.strip().lower() == hypothesis.strip().lower() else 0.0
      elif method == 'contains':
          return 1.0 if reference.strip().lower() in hypothesis.strip().lower() else 0.0
      # 可扩展为F1、EM等
  ```
- **影响**: QA任务质量评估不完整

## 🟡 中优先级 (建议实施)

### 6. BERTScore 评估
- **文件**: `experiments/quality.py`
- **依赖**: `pip install bert-score`
- **实现**:
  ```python
  from bert_score import score
  
  def bertscore_batch(references, hypotheses, lang='en'):
      P, R, F1 = score(hypotheses, references, lang=lang, verbose=False)
      return F1.tolist()
  ```

### 7. 阶段能耗分析
- **文件**: `experiments/experiment_runner.py`
- **实现**:
  ```python
  # 已有 get_phase_data() 方法，需调用
  prefill_data = monitor.get_phase_data("inference_start", "first_token")
  decode_data = monitor.get_phase_data("first_token", "inference_end")
  
  result['phase_analysis'] = {
      'prefill': prefill_data,
      'decode': decode_data
  }
  ```

### 8. 最终综合分 (Score_final)
- **文件**: `scripts/analyze_experiments_1.py`
- **实现**:
  ```python
  # 加权综合多维度指标
  w_qe = 0.4  # 质效比权重
  w_fair = 0.3  # 公平性权重
  w_cost = 0.3  # 成本权重
  
  df['Score_final'] = (
      w_qe * df['qe_ratio_norm'] +
      w_fair * (1 - df['fairness_gap']) +
      w_cost * (1 - df['cost_norm'])
  )
  ```

### 9. 功耗归一化 (P_norm)
- **文件**: `scripts/analyze_experiments_1.py`
- **实现**:
  ```python
  df['norm_power'] = df.groupby('task')['gpu_power_avg_w'].transform(
      lambda x: (x - x.min()) / (x.max() - x.min())
  )
  ```

## 🟢 低优先级 (可选实施)

### 10. 成本指标
- **文件**: `experiments/config.py`, `scripts/analyze_experiments_1.py`
- **实现**:
  ```python
  # config.py
  GPU_COST_PER_HOUR = 0.5  # $/h
  ENERGY_COST_PER_KWH = 0.12  # $/kWh
  
  # analyze_experiments_1.py
  df['Cost_GPU'] = (df['latency_s'] / 3600) * GPU_COST_PER_HOUR
  df['Cost_energy'] = (df['gpu_energy_j'] / 3600000) * ENERGY_COST_PER_KWH
  df['CPQ'] = (df['Cost_GPU'] + df['Cost_energy']) / df['quality_raw']
  df['CPT'] = (df['Cost_GPU'] + df['Cost_energy']) / df['output_tokens']
  ```

### 11. 代码正确性 (CodeCorrect)
- **需求**: 测试用例和执行环境
- **实现**: 需要设计代码执行沙箱

### 12. 嫉妒率 (Envy)
- **文件**: `experiments/quality.py`
- **实现**: 随机两群体比较质量差异

## 实施检查清单

### Phase 1: 核心指标补全 (1-2周)
- [ ] 实现空闲基线功耗测量 (P_idle)
- [ ] 计算每token能耗 (E_token)
- [ ] 计算每瓦性能 (PPW) 和能效比 (TPJ)
- [ ] 集成 ROUGE 评估
- [ ] 实现 QA 准确率计算
- [ ] 标准化 Distinct-n 计算流程
- [ ] 标准化 CodeCompile 计算流程
- [ ] 更新 results.csv 字段结构
- [ ] 测试向后兼容性

### Phase 2: 高级指标集成 (2-3周)
- [ ] 集成 BERTScore
- [ ] 实现阶段能耗分析调用
- [ ] 设计并实现 Score_final
- [ ] 添加功耗归一化
- [ ] 更新可视化图表
- [ ] 更新分析报告模板

### Phase 3: 成本与优化 (1-2周)
- [ ] 实现成本模型
- [ ] 优化数据流程
- [ ] 完善可视化报告
- [ ] 添加更多公平性指标
- [ ] 性能优化

### Phase 4: 文档与测试 (1周)
- [ ] 更新 experiment_design.md
- [ ] 更新 agents.md
- [ ] 编写单元测试
- [ ] 编写用户指南
- [ ] 代码审查

## 快速命令参考

### 安装新依赖
```bash
conda activate bartscore
pip install rouge-score bert-score scipy
```

### 运行改进后的分析
```bash
# 确保数据完整
python experiments/experiment_runner.py

# 运行分析
python scripts/analyze_experiments_1.py

# 查看结果
cat results/experiments_1/report.md
```

### 验证新指标
```bash
# 检查 results.csv 是否包含新字段
head -n 1 data/experiments_1/summary/results.csv

# 检查分析数据
head -n 1 results/experiments_1/analysis_data.csv
```

## 相关文档

- [详细缺口分析](./DATA_COLLECTION_GAP_ANALYSIS.md)
- [实验设计文档](./experiment/experiment_design.md)
- [TTFT和Token追踪改进](./TTFT_AND_TOKEN_TRACKING_IMPROVEMENTS.md)
- [Agents使用指南](../agents.md)

---

**版本**: v1.0  
**创建时间**: 2026-03-02  
**维护者**: Kiro AI Assistant
