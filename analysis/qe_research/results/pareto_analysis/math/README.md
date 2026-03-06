# 数学推理任务帕累托前沿分析

## 🎯 核心结论

**最佳综合配置**: qwen25_3b_hf_4bit ⭐⭐⭐⭐⭐

- **数值匹配准确率**: 80%（第二梯队）
- **每token能耗**: 1.563 J/token（在高质量模型中最低）
- **生成速度**: 17.73 tokens/s（中等）
- **推荐理由**: 拐点模型，在质量-能耗权衡中达到最优平衡

---

## 📊 帕累托前沿分析

### 质量-能耗前沿（3个模型）

在质量和能耗的权衡中，3个模型位于帕累托前沿：

1. **phi3_4b_hf_8bit**: 质量最高（100%），能耗1.992 J/token
2. **qwen25_3b_hf_4bit**: 质量80%，能耗1.563 J/token（拐点）⭐
3. **qwen_4b_ol_q4km**: 质量60%，能耗最低（1.049 J/token）

### 质量-速度前沿（3个模型）

在质量和速度的权衡中，3个模型位于帕累托前沿：

1. **phi3_4b_hf_8bit**: 质量100%，速度12.77 tokens/s
2. **qwen25_7b_hf_4bit**: 质量80%，速度19.46 tokens/s
3. **qwen_4b_ol_q4km**: 质量60%，速度最快（64.66 tokens/s）

### 三维前沿（质量-能耗-速度，5个模型）

综合考虑质量、能耗和速度三个维度：

1. **phi3_4b_hf_8bit**: 质量最高（100%）
2. **qwen25_3b_hf_4bit**: 最佳综合配置（拐点）⭐
3. **phi3_4b_hf_4bit**: 质量80%，平衡配置
4. **qwen25_7b_hf_4bit**: 质量80%，速度较快
5. **qwen_4b_ol_q4km**: 速度最快，能耗最低

---

## 🔍 关键发现

### 1. Phi3模型数学能力突出

- **phi3_4b_hf_8bit**: 100%准确率，唯一满分模型
- **phi3_4b_hf_4bit**: 80%准确率，第二梯队
- Phi3系列在数学推理任务上表现最佳

### 2. 质量分层明显

- **第一梯队（100%）**: phi3_4b_hf_8bit
- **第二梯队（80%）**: phi3_4b_hf_4bit, qwen25_3b_hf_4bit, qwen25_3b_hf_8bit, qwen25_7b_hf_4bit
- **第三梯队（60%）**: qwen_4b_ol_q4km
- **第四梯队（50%）**: gemma_2b_hf_4bit, gemma_2b_hf_8bit
- **第五梯队（40%及以下）**: deepseek_8b_ol_q4km, gemma_4b_ol_q4km, qwen_8b_ol_q4km

### 3. 能耗与量化策略

- **最低能耗**: qwen_4b_ol_q4km（1.049 J/token）
- **最高能耗**: qwen25_7b_hf_4bit（3.124 J/token）
- 4bit量化的3B模型能耗优于8bit量化的4B模型

### 4. 速度差异巨大

- **最快**: qwen_4b_ol_q4km（64.66 tokens/s）
- **最慢**: qwen25_3b_hf_8bit（7.43 tokens/s）
- Ollama模型速度优势明显（3-5倍于HuggingFace）

### 5. 质量-能耗权衡

qwen25_3b_hf_4bit是拐点模型：
- 质量80%（第二梯队）
- 能耗1.563 J/token（比最高质量模型低21%）
- 速度17.73 tokens/s（中等）
- 在质量和能耗之间达到最佳平衡

---

## 💡 应用建议

### 场景1: 追求准确性（推荐）

**推荐**: phi3_4b_hf_8bit

- 100%准确率，唯一满分
- 能耗适中（1.992 J/token）
- 适合对准确性要求极高的场景

### 场景2: 平衡质效比（推荐）⭐

**推荐**: qwen25_3b_hf_4bit

- 80%准确率，满足大多数需求
- 能耗较低（1.563 J/token）
- 速度适中（17.73 tokens/s）
- 最佳综合配置

### 场景3: 快速响应

**推荐**: qwen_4b_ol_q4km

- 速度最快（64.66 tokens/s）
- 能耗最低（1.049 J/token）
- 准确率60%，基本可用
- 适合对速度要求高的场景

### 场景4: 不推荐

**避免使用**:
- **gemma_4b_ol_q4km**: 准确率仅20%，不可用
- **qwen_8b_ol_q4km**: 准确率20%，8B模型表现不如小模型
- **qwen25_3b_hf_8bit**: 速度极慢（7.43 tokens/s），能耗高

---

## 📈 定量指标

- **超体积（质量-能耗）**: 0.8246
  - 较高，说明帕累托前沿覆盖了大部分可行空间
  
- **间距指标（质量-能耗）**: 0.0128
  - 较小，前沿点分布较均匀
  
- **拐点**: qwen25_3b_hf_4bit
  - 曲率最大的点，质量-能耗权衡最优

---

## 📁 输出文件

- `merged_data.csv`: 合并后的原始数据
- `pareto_quality_energy.png`: 质量-能耗帕累托前沿图
- `pareto_quality_speed.png`: 质量-速度帕累托前沿图
- `MATH_PARETO_ANALYSIS_REPORT.md`: 完整分析报告

---

## 🔧 技术细节

### 数据来源

1. **质量数据**: `data/analize/results/math_quality/math_quality_summary.csv`
   - 指标: numerical_match（数值匹配准确率）
   
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
python analysis/qe_research/scripts/pareto_analysis_math.py

# 查看结果
cd analysis/qe_research/results/pareto_analysis/math
```

---

## 📊 与其他任务对比

| 维度 | Math任务 | Code任务 | Reasoning任务 |
|------|---------|---------|--------------|
| 最佳模型 | qwen25_3b_hf_4bit | gemma_4b_ol_q4km | gemma_4b_ol_q4km |
| 最高质量 | phi3_4b_hf_8bit (100%) | gemma_4b_ol_q4km (100%) | qwen25_7b_hf_4bit |
| 质量范围 | 20%-100% | 0%-100% | 较窄 |
| 前沿模型数 | 3（质量-能耗） | 2（质量-能耗） | 5（质量-能耗） |
| 超体积 | 0.8246 | 0.9768 | 3375.77（不同尺度） |
| 间距指标 | 0.0128 | 0.0000 | 0.1594 |

**关键差异**:
- Math任务最佳模型是qwen25_3b_hf_4bit，而Code和Reasoning是gemma_4b_ol_q4km
- Phi3模型在Math任务上表现突出（100%准确率）
- Math任务前沿点较多（3个），分布较均匀

---

**生成时间**: 2026-03-06  
**分析脚本**: `analysis/qe_research/scripts/pareto_analysis_math.py`  
**状态**: ✅ 完成
