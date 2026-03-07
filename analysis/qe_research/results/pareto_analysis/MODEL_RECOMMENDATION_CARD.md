# 模型推荐速查卡

**更新日期**: 2026-03-07

---

## 🎯 场景化推荐

### 生产环境 - 通用场景
```
推荐: gemma_4b_ol_q4km ⭐⭐⭐⭐⭐

优势:
✓ 质量-能耗权衡最优
✓ 稳定性极高 (100%)
✓ 多任务表现优异

适用: 通用应用、生产部署、长期运行
```

### 高质量场景 - 学术研究
```
推荐: qwen25_7b_hf_4bit ⭐⭐⭐⭐⭐

优势:
✓ Reasoning质量满分 (1.000)
✓ 推理能力最强

适用: 学术研究、高质量推理、质量优先

权衡: 能耗高、速度慢
```

### 低延迟场景 - 实时应用
```
推荐: qwen_4b_ol_q4km ⭐⭐⭐⭐

优势:
✓ 速度最快 (60-65 tokens/s)
✓ 能耗相对较低

适用: 实时应用、高吞吐量、低延迟需求

权衡: 质量中等
```

---

## 📋 任务专项推荐

### Code（代码生成）
```
首选: gemma_4b_ol_q4km
- 编译率: 100%
- 稳定性: 100%
- 拐点模型

备选: deepseek_8b_ol_q4km
- 编译率: 60%
- 速度: 41.08 tokens/s
```

### Creative（创意写作）
```
首选: qwen_8b_ol_q4km
- 质量: 0.961 (最高)
- 多样性最佳

备选: gemma_4b_ol_q4km
- 质量: 0.917
- 拐点模型
```

### Reasoning（推理）
```
首选: qwen25_7b_hf_4bit
- 质量: 1.000 (满分)
- 推理能力最强

备选: gemma_4b_ol_q4km
- 质量: 0.889
- 综合评分最高 (0.805)
```

### Math（数学推理）
```
首选: phi3_4b_hf_8bit
- 质量: 1.000 (满分)
- 数学能力最强

备选: qwen25_3b_hf_4bit
- 质量: 0.800
- 拐点模型
```

### Translation（翻译）
```
首选: deepseek_8b_ol_q4km
- 质量: 0.690 (最高)
- BLEU得分最佳

备选: phi3_4b_hf_4bit
- 拐点模型
```

### Summary（摘要）
```
首选: qwen25_3b_hf_4bit
- 质量: 0.181 (最高)
- 拐点模型
- 稳健性100%
```

---

## 🔍 模型对比速查表

| 模型 | 综合评级 | 最佳任务 | 速度 | 能耗 | 稳定性 |
|------|---------|---------|------|------|--------|
| gemma_4b_ol_q4km | ⭐⭐⭐⭐⭐ | Code, Reasoning | 中 | 中 | 极高 |
| qwen25_7b_hf_4bit | ⭐⭐⭐⭐⭐ | Reasoning | 慢 | 高 | 高 |
| qwen_4b_ol_q4km | ⭐⭐⭐⭐ | 速度优先 | 极快 | 低 | 中 |
| qwen_8b_ol_q4km | ⭐⭐⭐⭐ | Creative | 中 | 中 | 高 |
| phi3_4b_hf_8bit | ⭐⭐⭐⭐ | Math | 慢 | 中 | 中 |
| deepseek_8b_ol_q4km | ⭐⭐⭐⭐ | Translation | 中 | 中 | 中 |
| qwen25_3b_hf_4bit | ⭐⭐⭐ | Summary | 中 | 中 | 极高 |

---

## 💡 决策流程图

```
需求分析
    │
    ├─ 质量最重要？
    │  └─ 是 → qwen25_7b_hf_4bit (Reasoning)
    │         phi3_4b_hf_8bit (Math)
    │
    ├─ 速度最重要？
    │  └─ 是 → qwen_4b_ol_q4km (60-65 tokens/s)
    │
    ├─ 稳定性最重要？
    │  └─ 是 → gemma_4b_ol_q4km (100%稳定性)
    │
    └─ 需要平衡？
       └─ 是 → gemma_4b_ol_q4km (全能冠军)
```

---

## 📊 性能指标快速参考

### 速度排名（tokens/s）
1. qwen_4b_ol_q4km: 60-65
2. gemma_4b_ol_q4km: 40-50
3. deepseek_8b_ol_q4km: 40-42
4. qwen_8b_ol_q4km: 41-42
5. qwen25_7b_hf_4bit: 17-19

### 能耗排名（J/token）
1. qwen_4b_ol_q4km: 1.0-1.2 (最低)
2. gemma_4b_ol_q4km: 1.3-1.4
3. qwen25_3b_hf_4bit: 1.5-1.6
4. deepseek_8b_ol_q4km: 1.9-2.0
5. qwen25_7b_hf_4bit: 3.0-3.4 (最高)

### 稳定性排名
1. gemma_4b_ol_q4km: 100% (Code)
2. qwen25_3b_hf_4bit: 100% (Summary)
3. gemma_4b_ol_q4km: 90%+ (Creative)
4. 其他模型: 60-90%

---

## ⚠️ 注意事项

### QA任务
- 所有模型质量相同（has_answer=1.0）
- 建议使用更细粒度的质量指标
- 当前推荐基于能耗和速度

### Translation任务
- 稳健性分析未完成
- 推荐基于质量和定量指标

### 能耗考虑
- 长时间运行场景优先考虑低能耗模型
- 短时任务可选择高质量高能耗模型

---

## 🚀 快速开始

### 1. 查看详细报告
```bash
# 综合报告
analysis/qe_research/results/pareto_analysis/COMPLETE_ANALYSIS_SUMMARY_2026-03-07.md

# 任务报告
analysis/qe_research/results/pareto_analysis/{task}/
```

### 2. 查看可视化图表
```bash
# 图表目录
analysis/qe_research/results/pareto_analysis/{task}/*.png
```

### 3. 重新运行分析
```bash
conda activate bartscore
python analysis/qe_research/scripts/pareto_analysis_{task}.py
```

---

**更新**: 2026-03-07  
**基于**: 7个任务、11-12个模型的完整分析  
**数据来源**: Pareto前沿分析（重构版）
