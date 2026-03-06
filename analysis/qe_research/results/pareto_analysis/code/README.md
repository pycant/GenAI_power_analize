# 代码生成任务帕累托前沿分析

## 🎯 核心结论

**最佳综合配置**: gemma_4b_ol_q4km ⭐⭐⭐⭐⭐

- **编译成功率**: 100%（所有模型中最高）
- **每token能耗**: 1.392 J/token（在高质量模型中最低）
- **生成速度**: 40.20 tokens/s（中等偏上）
- **推荐理由**: 拐点模型，在质量-能耗权衡中达到最优平衡

---

## 📊 帕累托前沿分析

### 质量-能耗前沿（2个模型）

在质量和能耗的权衡中，只有2个模型位于帕累托前沿：

1. **gemma_4b_ol_q4km**: 质量最高（100%），能耗适中
2. **qwen_4b_ol_q4km**: 能耗最低，但质量为0%（无法编译）

### 质量-速度前沿（4个模型）

在质量和速度的权衡中，4个模型位于帕累托前沿：

1. **gemma_4b_ol_q4km**: 质量100%，速度40.20 tokens/s
2. **deepseek_8b_ol_q4km**: 质量60%，速度41.08 tokens/s
3. **qwen_8b_ol_q4km**: 质量20%，速度41.13 tokens/s
4. **qwen_4b_ol_q4km**: 质量0%，速度最快（59.35 tokens/s）

### 三维前沿（质量-能耗-速度，4个模型）

综合考虑质量、能耗和速度三个维度：

1. **gemma_4b_ol_q4km**: 最佳综合配置
2. **deepseek_8b_ol_q4km**: 质量60%，速度和能耗平衡
3. **qwen_8b_ol_q4km**: 质量20%，速度快
4. **qwen_4b_ol_q4km**: 速度最快，但质量为0

---

## 🔍 关键发现

### 1. 质量差异显著

- **最高**: gemma_4b_ol_q4km（100%编译成功率）
- **次高**: gemma_2b_hf_4bit, qwen25_3b_hf_4bit（80%）
- **最低**: qwen_4b_ol_q4km（0%）

编译成功率从0%到100%，差异巨大，说明不同模型在代码生成质量上存在本质差异。

### 2. 能耗与模型大小相关

- **最低能耗**: qwen_4b_ol_q4km（1.195 J/token）
- **最高能耗**: qwen25_7b_hf_8bit（9.727 J/token）

8bit量化的7B模型能耗是4bit量化4B模型的8倍以上，量化策略对能耗影响巨大。

### 3. 速度与量化策略强相关

- **最快**: qwen_4b_ol_q4km（59.35 tokens/s）
- **最慢**: qwen25_7b_hf_8bit（3.30 tokens/s）

Ollama模型（q4km量化）普遍比HuggingFace模型（4bit/8bit）快2-3倍。

### 4. 质量-能耗权衡

gemma_4b_ol_q4km在质量-能耗平面上是唯一的拐点，实现了：
- 最高质量（100%）
- 相对较低的能耗（1.392 J/token，仅比最低高16%）
- 中等偏上的速度（40.20 tokens/s）

---

## 💡 应用建议

### 场景1: 生产环境（质量优先）

**推荐**: gemma_4b_ol_q4km

- 100%编译成功率，保证代码可用性
- 能耗和速度都在可接受范围内
- 最佳质效比

### 场景2: 快速原型（速度优先）

**推荐**: deepseek_8b_ol_q4km 或 qwen_8b_ol_q4km

- 速度快（41+ tokens/s）
- 质量尚可（20-60%）
- 适合快速迭代

### 场景3: 资源受限（能耗优先）

**推荐**: gemma_2b_hf_4bit

- 能耗较低（1.436 J/token）
- 质量较高（80%）
- 速度可接受（22.47 tokens/s）

### 场景4: 不推荐

**避免使用**:
- qwen25_7b_hf_8bit: 能耗极高（9.727 J/token），速度极慢（3.30 tokens/s）
- qwen_4b_ol_q4km: 虽然速度快，但质量为0%，完全不可用

---

## 📈 定量指标

- **超体积（质量-能耗）**: 0.9768
  - 接近理论最大值1.0，说明帕累托前沿覆盖了大部分可行空间
  
- **间距指标（质量-能耗）**: 0.0000
  - 前沿点分布极不均匀（只有2个点）
  
- **拐点**: gemma_4b_ol_q4km
  - 曲率最大的点，质量-能耗权衡最优

---

## 📁 输出文件

- `merged_data.csv`: 合并后的原始数据
- `pareto_quality_energy.png`: 质量-能耗帕累托前沿图
- `pareto_quality_speed.png`: 质量-速度帕累托前沿图
- `CODE_PARETO_ANALYSIS_REPORT.md`: 完整分析报告

---

## 🔧 技术细节

### 数据来源

1. **质量数据**: `data/analize/results/code_quality/quality_summary_code.csv`
   - 指标: compilation_rate_mean（编译成功率）
   
2. **能耗数据**: `analysis/qe_research/results/derived_metrics/08_energy_per_token.csv`
   - 指标: 每token能耗（J/token）
   
3. **速度数据**: `analysis/qe_research/results/derived_metrics/07_avg_token_speed.csv`
   - 指标: token生成速度（tokens/s）

### 帕累托前沿识别方法

- **2D前沿**: 支配关系判断（质量最大化，能耗最小化）
- **3D前沿**: 三维支配关系（质量↑，能耗↓，速度↑）
- **拐点识别**: 曲率法（三点法计算曲率，选择曲率最大点）

### 定量指标计算

- **超体积**: 归一化后的帕累托前沿覆盖面积
- **间距指标**: 前沿点之间距离的标准差（衡量均匀性）

---

## 🚀 快速开始

```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行分析
python analysis/qe_research/scripts/pareto_analysis_code.py

# 查看结果
cd analysis/qe_research/results/pareto_analysis/code
```

---

**生成时间**: 2026-03-06  
**分析脚本**: `analysis/qe_research/scripts/pareto_analysis_code.py`  
**状态**: ✅ 完成
