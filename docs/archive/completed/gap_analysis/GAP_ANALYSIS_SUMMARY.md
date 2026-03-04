# 数据采集缺口分析总结

## 执行摘要

本次分析对比了 `docs/experiment/experiment_design.md` 中定义的完整指标体系与当前代码实现，识别出数据采集的缺口并提供了实施建议。

## 关键发现

### ✅ 已完整实现的模块

1. **时间指标**: TTFT、TPOT、总延迟等已完整实现
2. **系统监控**: CPU/GPU利用率、显存、温度等已完整实现
3. **基础能耗**: GPU/CPU能耗追踪已实现
4. **公平性指标**: Fairness Gap、Gini、Theil、NSW 已实现
5. **基础质量**: BARTScore 已实现

### ⚠️ 部分实现的模块

1. **质量评估**: 
   - ✅ BARTScore (QA/Summary)
   - ⚠️ Distinct-n (Creative) - 从JSON读取，需标准化
   - ⚠️ CodeCompile (Code) - 从JSON推断，需标准化
   - ❌ ROUGE、BERTScore、Accuracy 未实现

2. **阶段分析**:
   - ✅ 事件标记机制已实现
   - ✅ get_phase_data() 方法已实现
   - ❌ 未在实验流程中调用

### ❌ 完全缺失的模块

1. **基线功耗**: 无空闲基线测量 (P_idle)
2. **衍生能效指标**: E_token、PPW、TPJ 未计算
3. **高级质量指标**: ROUGE、BERTScore、Accuracy 未集成
4. **成本模型**: 完全未实现
5. **最终综合分**: Score_final 未设计

## 影响评估

### 高影响缺失项 (阻碍核心研究目标)

1. **P_idle 和 P_inc**: 无法准确评估模型的增量功耗
2. **E_token**: 无法进行token级能效对比
3. **PPW 和 TPJ**: 缺少关键能效指标，影响质效比评估
4. **ROUGE**: Summary任务质量评估不完整
5. **Accuracy**: QA任务质量评估不完整

### 中影响缺失项 (影响分析深度)

1. **BERTScore**: 缺少语义相似度评估
2. **阶段能耗**: 无法分析Prefill/Decode能耗分布
3. **Score_final**: 缺少统一的模型排名指标
4. **功耗归一化**: 功耗对比不直观

### 低影响缺失项 (可选功能)

1. **成本指标**: 缺少经济性分析
2. **代码正确性**: 代码质量评估不完整
3. **嫉妒率**: 公平性分析不够全面

## 实施建议

### 立即行动 (1-2周)

**Phase 1: 核心指标补全**

优先实施以下5项高影响缺失项：

1. **空闲基线功耗测量** (1天)
   - 文件: `experiments/experiment_runner.py`
   - 工作量: 小
   - 影响: 高

2. **衍生能效指标计算** (1天)
   - 文件: `experiments/experiment_runner.py`
   - 指标: E_token, PPW, TPJ
   - 工作量: 小
   - 影响: 高

3. **ROUGE 集成** (2天)
   - 文件: `experiments/quality.py`
   - 依赖: `pip install rouge-score`
   - 工作量: 中
   - 影响: 高

4. **QA准确率实现** (1天)
   - 文件: `experiments/quality.py`
   - 工作量: 小
   - 影响: 高

5. **标准化质量指标** (2天)
   - 文件: `experiments/quality.py`, `experiment_runner.py`
   - 任务: 统一 Distinct-n 和 CodeCompile 计算
   - 工作量: 中
   - 影响: 中

**预期成果**: 
- 完成80%的核心指标
- 支持完整的质效比评估
- 数据结构向后兼容

### 后续优化 (2-4周)

**Phase 2: 高级指标集成**

1. BERTScore 集成
2. 阶段能耗分析调用
3. Score_final 设计与实现
4. 功耗归一化

**Phase 3: 成本与扩展**

1. 成本模型实现
2. 更多公平性指标
3. 可视化增强
4. 文档完善

## 技术债务

### 当前技术债务

1. **质量指标分散**: 
   - BARTScore 在 quality.py
   - Distinct-n 在 analyze_experiments_1.py 从JSON读取
   - CodeCompile 在 analyze_experiments_1.py 从JSON推断
   - **建议**: 统一到 quality.py

2. **阶段分析未使用**:
   - get_phase_data() 已实现但未调用
   - **建议**: 在 experiment_runner.py 中调用

3. **配置硬编码**:
   - 成本参数、权重等硬编码在脚本中
   - **建议**: 移到 config.py

### 重构建议

1. **质量评估模块重构**:
   ```python
   # quality.py 统一接口
   def evaluate_quality(task_type, reference, hypothesis):
       if task_type == 'qa':
           return {
               'bartscore': bartscore_single(reference, hypothesis),
               'accuracy': qa_accuracy(reference, hypothesis),
               'rouge': rouge_scores(reference, hypothesis)
           }
       elif task_type == 'summary':
           return {
               'bartscore': bartscore_single(reference, hypothesis),
               'rouge': rouge_scores(reference, hypothesis),
               'bertscore': bertscore_single(reference, hypothesis)
           }
       # ... 其他任务类型
   ```

2. **配置管理重构**:
   ```python
   # config.py
   class EvaluationConfig:
       # 成本模型
       GPU_COST_PER_HOUR = 0.5
       ENERGY_COST_PER_KWH = 0.12
       
       # 权重配置
       EFFICIENCY_WEIGHTS = {'tps': 0.4, 'latency': 0.3, 'energy': 0.3}
       FINAL_SCORE_WEIGHTS = {'qe': 0.4, 'fair': 0.3, 'cost': 0.3}
       
       # 质量评估配置
       QUALITY_METRICS = {
           'qa': ['bartscore', 'accuracy', 'rouge'],
           'summary': ['bartscore', 'rouge', 'bertscore'],
           'code': ['code_compiles', 'code_correct'],
           'creative': ['distinct_1', 'distinct_2']
       }
   ```

## 风险与挑战

### 技术风险

1. **向后兼容性**: 新增字段可能影响现有数据
   - **缓解**: 使用默认值，保留旧字段

2. **计算开销**: BERTScore 等指标计算较慢
   - **缓解**: 批处理、缓存、可选开关

3. **依赖管理**: 新增多个Python包
   - **缓解**: 更新 requirements.txt，文档说明

### 数据风险

1. **标准答案缺失**: QA准确率需要标准答案
   - **缓解**: 在 test_cases.json 中添加 reference_answer 字段

2. **数据迁移**: 现有实验数据缺少新字段
   - **缓解**: 提供数据补全脚本

## 成功指标

### Phase 1 完成标准

- [ ] P_idle、P_inc 正确测量
- [ ] E_token、PPW、TPJ 正确计算
- [ ] ROUGE 分数合理 (0-1范围)
- [ ] QA准确率正确计算
- [ ] results.csv 包含所有新字段
- [ ] 向后兼容性测试通过
- [ ] 文档更新完成

### 整体成功标准

- [ ] 实现设计文档中90%以上的指标
- [ ] 所有高优先级指标完成
- [ ] 数据流程自动化
- [ ] 可视化报告完整
- [ ] 代码测试覆盖率>80%
- [ ] 文档完整且最新

## 资源需求

### 人力需求

- **Phase 1**: 1人 × 1-2周 (核心指标)
- **Phase 2**: 1人 × 2-3周 (高级指标)
- **Phase 3**: 1人 × 1-2周 (成本与优化)
- **Phase 4**: 1人 × 1周 (文档与测试)

**总计**: 1人 × 5-8周

### 技术需求

- Python 3.8+
- 新增依赖: rouge-score, bert-score, scipy
- 存储: 约增加20%数据量
- 计算: BERTScore 需GPU支持

## 相关文档

### 本次分析产出

1. **[详细缺口分析](./DATA_COLLECTION_GAP_ANALYSIS.md)** - 完整的指标对比和分析
2. **[实施优先级清单](./IMPLEMENTATION_PRIORITY.md)** - 快速参考和检查清单
3. **[数据结构对比](./DATA_STRUCTURE_COMPARISON.md)** - 当前vs目标数据结构
4. **本文档** - 执行摘要和总结

### 相关设计文档

1. **[实验设计文档](./experiment/experiment_design.md)** - 完整的指标体系定义
2. **[TTFT和Token追踪改进](./TTFT_AND_TOKEN_TRACKING_IMPROVEMENTS.md)** - 已完成的改进
3. **[Agents使用指南](../agents.md)** - 项目环境和结构

## 下一步行动

### 立即行动项

1. **审查本分析**: 确认优先级和实施计划
2. **准备环境**: 安装新依赖 (`pip install rouge-score bert-score scipy`)
3. **创建分支**: 为 Phase 1 改进创建功能分支
4. **开始实施**: 按优先级清单逐项实现

### 本周目标

- [ ] 完成空闲基线功耗测量
- [ ] 完成衍生能效指标计算
- [ ] 集成 ROUGE 评估
- [ ] 实现 QA 准确率
- [ ] 更新数据结构文档

### 本月目标

- [ ] 完成 Phase 1 所有项目
- [ ] 开始 Phase 2 实施
- [ ] 完成单元测试
- [ ] 更新用户文档

## 联系与反馈

如有问题或建议，请：
1. 查看详细文档获取更多信息
2. 运行测试验证实现
3. 更新文档记录变更

---

**分析完成时间**: 2026-03-02  
**分析师**: Kiro AI Assistant  
**文档版本**: v1.0  
**状态**: ✅ 完成

## 附录：快速链接

- [开始实施 →](./IMPLEMENTATION_PRIORITY.md#实施检查清单)
- [查看详细分析 →](./DATA_COLLECTION_GAP_ANALYSIS.md)
- [对比数据结构 →](./DATA_STRUCTURE_COMPARISON.md)
- [查看设计文档 →](./experiment/experiment_design.md)
