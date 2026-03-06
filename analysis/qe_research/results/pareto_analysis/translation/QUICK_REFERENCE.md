# 翻译任务帕累托分析快速参考

## 🚀 快速开始

### 运行分析
```bash
# Windows
cd /path/to/GenAI_power_analize
run_translation_pareto_enhanced.bat

# 或直接运行
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/pareto_analysis_translation_enhanced.py
```

### 查看结果
```bash
# 报告位置
analysis/qe_research/results/pareto_analysis/translation/TRANSLATION_PARETO_ANALYSIS_ENHANCED_REPORT.md

# 图表位置
analysis/qe_research/results/pareto_analysis/translation/*.png
```

## 📊 核心指标速查

### 定量指标

| 指标 | 含义 | 越大越好/越小越好 |
|------|------|------------------|
| **超体积（HV）** | 前沿覆盖的目标空间体积 | ↑ 越大越好 |
| **间距（SP）** | 前沿点分布均匀性 | ↓ 越小越好 |
| **GD** | 前沿到理想前沿的距离 | ↓ 越小越好 |
| **IGD** | 理想前沿到实际前沿的距离 | ↓ 越小越好 |

### 稳健性指标

| 指标 | 含义 | 阈值 |
|------|------|------|
| **稳定性得分** | 模型在扰动下保持在前沿的频率 | ≥70% 为鲁棒 |
| **前沿一致性** | 扰动前后前沿的Jaccard相似度 | ≥80% 为稳定 |
| **权重敏感性** | 不同权重下成为最优的频率 | ≥60% 为稳定 |

### 决策支持指标

| 指标 | 含义 | 用途 |
|------|------|------|
| **目标达成度** | 前沿覆盖目标空间的比例 | 评估前沿质量 |
| **性价比** | ΔQ/ΔC | 评估升级价值 |
| **推荐等级** | ⭐-⭐⭐⭐⭐⭐ | 升级建议 |

## 🎯 推荐配置速查

### 场景1: 追求最佳综合性能
**推荐**: 拐点模型（Knee Point）
- 质量-能耗权衡最优
- 性价比最高
- 稳定性好

### 场景2: 追求最高质量
**推荐**: 质量最高模型
- BLEU得分最高
- 适合质量敏感场景
- 能耗可能较高

### 场景3: 追求最低能耗
**推荐**: 能耗最低模型
- 每token能耗最低
- 适合资源受限场景
- 质量可能有所牺牲

### 场景4: 追求最快速度
**推荐**: 速度最快模型
- tokens/s最高
- 适合实时应用
- 需权衡质量和能耗

## 📈 指标解读

### 超体积（Hypervolume）
```
HV = 0.75  →  ⭐⭐⭐⭐⭐ 优秀
HV = 0.60  →  ⭐⭐⭐⭐   良好
HV = 0.45  →  ⭐⭐⭐     一般
HV < 0.30  →  ⭐⭐       较差
```

### 间距指标（Spacing）
```
SP < 0.10  →  ⭐⭐⭐⭐⭐ 分布极均匀
SP < 0.20  →  ⭐⭐⭐⭐   分布均匀
SP < 0.30  →  ⭐⭐⭐     分布一般
SP ≥ 0.30  →  ⭐⭐       分布不均
```

### 稳定性得分
```
≥ 90%  →  ⭐⭐⭐⭐⭐ 极稳定
≥ 70%  →  ⭐⭐⭐⭐   很稳定
≥ 50%  →  ⭐⭐⭐     较稳定
≥ 30%  →  ⭐⭐       不稳定
< 30%  →  ⭐         很不稳定
```

### 升级推荐等级
```
质量提升 > 10% 且 成本增加 < 20%  →  ⭐⭐⭐⭐⭐ 强烈推荐
质量提升 > 5%  且 成本增加 < 30%  →  ⭐⭐⭐⭐   推荐
质量提升 > 2%  且 成本增加 < 40%  →  ⭐⭐⭐     可考虑
质量提升 > 0%                    →  ⭐⭐       谨慎考虑
质量提升 ≤ 0%                    →  ⭐         不推荐
```

## 🔍 常见问题

### Q1: 如何选择最适合的模型？
**A**: 
1. 查看拐点模型（综合最优）
2. 检查稳定性得分（≥70%为佳）
3. 根据场景需求调整（质量/能耗/速度）

### Q2: 稳定性得分低怎么办？
**A**: 
- 稳定性低的模型在实际应用中表现可能不稳定
- 建议选择稳定性≥70%的模型
- 或进行更多实验验证

### Q3: 如何解读边际效益曲线？
**A**: 
- 曲线陡峭：性价比高，值得升级
- 曲线平缓：性价比低，升级收益小
- 拐点：最佳升级时机

### Q4: GD和IGD有什么区别？
**A**: 
- GD: 衡量前沿到理想前沿的距离（收敛性）
- IGD: 衡量理想前沿到实际前沿的距离（收敛性+分布）
- IGD更全面，同时考虑收敛和分布

### Q5: 为什么需要稳健性分析？
**A**: 
- 验证结论的可靠性
- 评估对数据噪声的敏感性
- 确保推荐配置的稳定性

## 📝 报告结构

```
TRANSLATION_PARETO_ANALYSIS_ENHANCED_REPORT.md
├── 1. 数据概览
├── 2. 帕累托前沿识别
│   ├── 2.1 质量-能耗前沿
│   ├── 2.2 质量-速度前沿
│   └── 2.3 三维前沿
├── 3. 定量指标
│   ├── 3.1 质量-能耗前沿指标
│   └── 3.2 质量-速度前沿指标
├── 4. 稳健性分析
│   ├── 4.1 扰动分析
│   ├── 4.2 权重敏感性分析
│   └── 4.3 交叉验证
├── 5. 决策支持
│   ├── 5.1 目标达成度
│   ├── 5.2 鲁棒解推荐
│   └── 5.3 升级代价分析
├── 6. 推荐配置
└── 7. 指标解释
```

## 🛠️ 自定义参数

### 扰动分析
```python
perturbation_analysis(
    noise_level=0.05,    # 噪声水平 ±5%
    n_iterations=100     # 迭代次数
)
```

### 权重敏感性
```python
weight_sensitivity_analysis(
    n_samples=50         # 采样数量
)
```

### 交叉验证
```python
cross_validation_analysis(
    n_folds=5            # 折数
)
```

### 鲁棒解识别
```python
identify_robust_solutions(
    threshold=0.7        # 稳定性阈值 70%
)
```

## 📚 相关文档

- [完整功能总结](ENHANCED_ANALYSIS_SUMMARY.md)
- [原始分析脚本](../../scripts/pareto_analysis_translation.py)
- [增强版脚本](../../scripts/pareto_analysis_translation_enhanced.py)
- [指标计算器](../../scripts/pareto_metrics_calculator.py)
- [稳健性分析器](../../scripts/pareto_robustness_analyzer.py)

## 🔗 快速链接

- 数据文件: `merged_data.csv`
- 质量-能耗图: `pareto_quality_energy_enhanced.png`
- 质量-速度图: `pareto_quality_speed_enhanced.png`
- 边际效益图: `marginal_benefit_curve.png`
- 综合报告: `TRANSLATION_PARETO_ANALYSIS_ENHANCED_REPORT.md`

---

**提示**: 首次运行需要约2-3分钟，后续运行会更快。

**更新时间**: 2026-03-06
