# 帕累托前沿分析系统使用指南

## 📋 系统概述

本系统提供完整的帕累托前沿分析流程，包括：

1. **熵权法**：客观计算质量维度权重
2. **帕累托前沿识别**：2D和3D前沿
3. **定量指标计算**：超体积、间距、扩散度、边际效益、拐点
4. **稳健性验证**：扰动分析、权重敏感性、交叉验证
5. **自动报告生成**：Markdown格式完整报告

---

## 🚀 快速开始

### 方法1：使用现有脚本（推荐）

#### Reasoning任务示例

```bash
# 1. 定量指标计算
python analysis/qe_research/scripts/pareto_metrics_calculator.py

# 2. 稳健性验证
python analysis/qe_research/scripts/pareto_robustness_analyzer.py
```

**输出位置**：`analysis/qe_research/results/pareto_analysis/reasoning/`

**生成文件**：
- `pareto_metrics_summary.md` - 定量指标汇总
- `pareto_robustness_report.md` - 稳健性分析报告
- 各类可视化图表

### 方法2：使用批处理脚本

```bash
cd analysis/qe_research/scripts
run_pareto_analysis.bat reasoning
```

---

## 📊 数据准备

### 必需数据

1. **质量评分数据**
   - 格式：CSV文件
   - 必需列：`model`（模型名称）+ 多个质量维度列
   - 示例：`model, correctness, completeness, rigor, clarity, efficiency`

2. **能耗数据**
   - 格式：CSV文件
   - 必需列：`model`, `energy`（单位：焦耳）

3. **速度数据**（可选）
   - 格式：CSV文件
   - 必需列：`model`, `speed`（单位：tokens/s）

### 数据示例

**quality_scores.csv**:
```csv
model,correctness,completeness,rigor,clarity,efficiency
qwen25_7b_hf_4bit,4.8,4.6,4.4,4.8,4.2
gemma_4b_ol_q4km,4.4,4.2,4.0,4.6,4.4
...
```

**energy_data.csv**:
```csv
model,energy
qwen25_7b_hf_4bit,1267.88
gemma_4b_ol_q4km,340.86
...
```

**speed_data.csv**:
```csv
model,speed
qwen25_7b_hf_4bit,19.31
gemma_4b_ol_q4km,49.53
...
```

---

## 🔧 适配新任务

### 步骤1：准备数据

将你的任务数据整理成上述格式，放在合适的位置。

### 步骤2：修改脚本路径

编辑 `pareto_metrics_calculator.py` 的 `main()` 函数：

```python
def main():
    # 修改数据路径
    data_path = Path(__file__).parent.parent / 'results' / 'pareto_analysis' / 'YOUR_TASK' / 'merged_data.csv'
    output_dir = Path(__file__).parent.parent / 'results' / 'pareto_analysis' / 'YOUR_TASK'
    
    # 其余代码保持不变
    ...
```

### 步骤3：合并数据

如果你的数据分散在多个文件中，先合并：

```python
import pandas as pd

# 加载数据
quality_df = pd.read_csv('quality_scores.csv')
energy_df = pd.read_csv('energy_data.csv')
speed_df = pd.read_csv('speed_data.csv')

# 计算熵权法质量得分
quality_columns = ['correctness', 'completeness', 'rigor', 'clarity', 'efficiency']
data_norm = (quality_df[quality_columns] - quality_df[quality_columns].min()) / (quality_df[quality_columns].max() - quality_df[quality_columns].min())

# 计算熵和权重
prob = data_norm / data_norm.sum()
entropy = -np.sum(prob * np.log(prob + 1e-10), axis=0) / np.log(len(quality_df))
weights = (1 - entropy) / (1 - entropy).sum()

# 计算加权质量
quality_df['quality_normalized'] = (data_norm * weights).sum(axis=1)
quality_df['weighted_quality'] = quality_df['quality_normalized'] * 5  # 转换到0-5分

# 合并数据
merged_df = quality_df[['model', 'quality_normalized', 'weighted_quality']].merge(
    energy_df, on='model'
).merge(
    speed_df, on='model'
)

# 保存
merged_df.to_csv('merged_data.csv', index=False)
```

### 步骤4：运行分析

```bash
python pareto_metrics_calculator.py
python pareto_robustness_analyzer.py
```

---

## 📈 输出解读

### 定量指标

1. **超体积（Hypervolume）**
   - 数值越大越好
   - 表示前沿覆盖的目标空间体积
   - 用于比较不同任务或算法

2. **间距指标（Spacing）**
   - 数值越小越好
   - 表示前沿分布的均匀性
   - <0.2为优秀，0.2-0.3为良好

3. **拐点（Knee Point）**
   - 性价比最高的配置
   - 两种方法一致推荐的模型最可靠

### 稳健性指标

1. **扰动分析一致性**
   - >80%为极稳定 ⭐⭐⭐⭐⭐
   - 60-80%为很稳定 ⭐⭐⭐⭐
   - <60%为不稳定

2. **权重敏感性**
   - 100%频率为极稳定
   - >80%频率为很稳定

3. **交叉验证一致性**
   - >75%为优秀
   - 60-75%为良好

---

## 🎯 典型应用场景

### 场景1：新任务快速评估

1. 准备质量评分、能耗、速度数据
2. 运行熵权法计算综合质量
3. 运行帕累托分析识别最优配置
4. 查看拐点推荐

### 场景2：跨任务比较

1. 对每个任务运行完整分析
2. 比较超体积（任务难易度）
3. 比较前沿形状（权衡关系）
4. 识别通用最优模型

### 场景3：模型选择决策

1. 查看拐点推荐（性价比最高）
2. 查看稳健性评级（可靠性）
3. 根据场景选择：
   - 质量优先：选前沿最高质量点
   - 效率优先：选前沿最快速度点
   - 平衡方案：选拐点模型

---

## 🛠️ 高级功能

### 自定义权重

如果不想使用熵权法，可以手动指定权重：

```python
# 在pareto_metrics_calculator.py中
custom_weights = {
    'correctness': 0.3,
    'completeness': 0.2,
    'rigor': 0.2,
    'clarity': 0.2,
    'efficiency': 0.1
}

weighted_quality = sum(data_norm[col] * weight 
                      for col, weight in custom_weights.items())
```

### 调整稳健性参数

```python
# 扰动分析
perturbation_analysis(noise_level=0.10, n_iterations=200)  # 更严格的测试

# 权重敏感性
weight_sensitivity_analysis(weight_range=0.15, n_samples=100)  # 更大范围

# 交叉验证
cross_validation_analysis(n_folds=10)  # 更多折数
```

---

## 📝 报告模板

生成的报告包含以下章节：

1. **分析概述**
   - 任务名称、分析时间、数据规模

2. **熵权法权重**
   - 各维度权重及解释

3. **帕累托前沿**
   - 质量-能耗前沿
   - 质量-速度前沿
   - 3D前沿（如有）

4. **定量指标**
   - 超体积、间距、扩散度
   - 边际效益分析
   - 拐点识别

5. **稳健性验证**
   - 扰动分析结果
   - 权重敏感性结果
   - 交叉验证结果

6. **推荐配置**
   - 最佳综合配置
   - 场景特定推荐

---

## 🔍 故障排查

### 问题1：数据加载失败

**原因**：文件路径错误或格式不正确

**解决**：
- 检查文件路径是否正确
- 确认CSV文件编码为UTF-8
- 确认必需列存在

### 问题2：熵权法计算异常

**原因**：数据中存在常数列或缺失值

**解决**：
- 检查数据是否有变化（标准差>0）
- 填充或删除缺失值
- 确保所有值为数值类型

### 问题3：前沿识别结果为空

**原因**：数据量太小或所有点被支配

**解决**：
- 确保至少有3个以上的模型
- 检查数据是否合理（不应所有模型完全相同）

---

## 📚 参考文献

1. **熵权法**：Shannon, C. E. (1948). A mathematical theory of communication.
2. **帕累托前沿**：Deb, K. (2001). Multi-Objective Optimization using Evolutionary Algorithms.
3. **超体积**：Zitzler, E., & Thiele, L. (1999). Multiobjective evolutionary algorithms.
4. **拐点识别**：Branke, J., et al. (2004). Finding knees in multi-objective optimization.

---

## 📞 技术支持

如有问题，请查看：
- `AGENTS.md` - 项目整体说明
- `EVALUATION_SUMMARY.md` - 评价总结
- `PARETO_EFFECTIVENESS_EVALUATION.md` - 完整评价报告

---

*最后更新：2026-03-06*
