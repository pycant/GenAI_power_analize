# Reasoning任务帕累托分析 - 快速参考

## 🎯 一句话总结

基于熵权法的多维度帕累托前沿分析，识别出**gemma_4b_ol_q4km**为综合性能最优模型。

## 📊 核心数据

| 指标 | 数值 |
|------|------|
| 分析模型数 | 11个 |
| 帕累托最优模型 | 6个（3D前沿）|
| 质量得分范围 | 0.000 - 1.000 |
| 能耗范围 | 58.13 - 1267.88 J |
| 速度范围 | 7.49 - 64.56 t/s |

## 🏆 推荐模型

### 🥇 综合最优（推荐）
**gemma_4b_ol_q4km**
- 综合评分: 0.805
- 质量: 0.889
- 速度: 49.53 t/s
- 能耗: 340.86 J

### 🥈 质量优先
**qwen25_7b_hf_4bit**
- 质量: 1.000（最高）
- 速度: 19.31 t/s
- 能耗: 1267.88 J

### 🥉 速度优先
**qwen_4b_ol_q4km**
- 速度: 64.56 t/s（最快）
- 质量: 0.570
- 能耗: 428.41 J

### 🔋 低功耗
**gemma_2b_hf_4bit**
- 能耗: 58.13 J（最低）
- 能效比: 0.36 t/J（最高）
- 质量: 0.000

## 📈 熵权法权重

```
清晰度: 27.64% ████████████████████████████
正确性: 19.24% ███████████████████
完整性: 18.51% ██████████████████
效率:   17.78% █████████████████
严谨性: 16.83% ████████████████
```

## 🔍 快速查找

### 我需要...

- **最高质量** → qwen25_7b_hf_4bit
- **最快速度** → qwen_4b_ol_q4km
- **最低能耗** → gemma_2b_hf_4bit
- **最佳平衡** → gemma_4b_ol_q4km ⭐

### 我的场景是...

- **学术研究** → qwen25_7b_hf_4bit
- **实时应用** → qwen_4b_ol_q4km
- **通用应用** → gemma_4b_ol_q4km ⭐
- **边缘设备** → gemma_2b_hf_4bit

## 📁 关键文件

| 文件 | 用途 |
|------|------|
| `pareto_analysis_report_enhanced.md` | 完整分析报告 ⭐ |
| `process_visualization/01_*.png` | 熵权法过程 |
| `process_visualization/02_*.png` | 数据分布 |
| `process_visualization/03_*.png` | 相关性分析 |
| `process_visualization/04_*.png` | 帕累托识别 |

## 🚀 运行命令

```bash
# 增强版（推荐）
python analysis/qe_research/scripts/pareto_analysis_reasoning_enhanced.py

# 或使用批处理
analysis/qe_research/scripts/run_pareto_analysis.bat
```

## 💡 关键洞察

1. **清晰度最重要**: 在Reasoning任务中，清晰度权重最高（27.64%）
2. **质量与能耗正相关**: 高质量模型往往需要更多能耗
3. **存在最优平衡点**: gemma_4b_ol_q4km在三个维度上达到最佳平衡
4. **小模型也有价值**: gemma_2b系列在低功耗场景下有独特优势

## 📞 需要帮助？

查看完整文档:
- `README.md` - 详细说明
- `ANALYSIS_SUMMARY.md` - 分析总结
- `IMPLEMENTATION_COMPLETE.md` - 实施报告

---
*快速参考 | 更新时间: 2026-03-06*
