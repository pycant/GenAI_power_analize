# Pareto 脚本功能总结文档

## 概述

`analysis/qe_research/scripts` 目录下包含 11 个 pareto 相关的 Python 脚本，用于对不同任务进行帕累托前沿分析。这些脚本基于质量-能耗-速度三维指标，识别最优模型组合。

⚠️ **重要发现**：经过详细分析，发现存在严重的代码重复问题：
- **重复率**：60-70% 的代码在 7 个任务脚本中重复
- **重复代码量**：约 1400-2100 行
- **未使用资源**：通用工具脚本（`pareto_metrics_calculator.py`、`pareto_robustness_analyzer.py`）完全未被调用

✅ **重构进展**（2026-03-07）：
- **阶段 1 已完成**：创建了 `pareto_core` 共享模块
- **阶段 2 已完成**：重构了 6 个任务脚本
- **阶段 3 已完成**：集成稳健性分析功能
- **共享模块**：`config.py`（配置）、`shared_functions.py`（核心函数 + 稳健性分析）
- **重构完成**：code, creative, math, qa, summary, translation - 代码量减少 60%
- **新增功能**：扰动分析、交叉验证已集成到 pareto_core
- **代码重复减少**：约 1200 行（从 1500 行目标中的 80%）
- **下一步**：编写单元测试，验证功能正确性

详细分析请参考：
- [CODE_DUPLICATION_ANALYSIS.md](./CODE_DUPLICATION_ANALYSIS.md) - 代码重复详细分析
- [REFACTORING_ROADMAP.md](./REFACTORING_ROADMAP.md) - 重构路线图和进度

---

## 脚本分类

### 0. 重构版本脚本（新增）⭐

使用 `pareto_core` 共享模块的重构版本，消除代码重复。

#### 0.1 重构完成的任务脚本

所有基础任务脚本已完成重构，使用共享模块：

- **`pareto_analysis_code.py`** - 代码生成任务（重构版）
- **`pareto_analysis_creative.py`** - 创意写作任务（重构版）
- **`pareto_analysis_math.py`** - 数学推理任务（重构版）
- **`pareto_analysis_qa.py`** - 问答任务（重构版）
- **`pareto_analysis_summary.py`** - 摘要任务（重构版）
- **`pareto_analysis_translation.py`** - 翻译任务（重构版）

**状态**: ✅ 已完成（6/6）

**代码量**: 每个脚本约 180 行（原版约 450-500 行，减少 60%）

**改进**:
- 使用 `pareto_core.MODEL_MAPPING` 替代重复的模型映射
- 使用 `pareto_core.identify_pareto_frontier_2d/3d()` 替代重复实现
- 使用 `pareto_core.calculate_hypervolume/spacing()` 替代重复实现
- 使用 `pareto_core.find_knee_point()` 替代重复实现
- 使用 `pareto_core.plot_pareto_2d()` 替代重复实现
- 使用 `pareto_core.load_energy_speed_data()` 简化数据加载
- 使用 `pareto_core.merge_quality_metrics()` 简化数据合并
- 使用 `pareto_core.perturbation_analysis()` 进行稳健性分析（新增）
- 使用 `pareto_core.cross_validation_pareto()` 进行交叉验证（新增）

**输出**: 与原版完全相同，并新增稳健性分析章节

**优势**: 代码简洁、易维护、算法统一

**使用方式**:
```bash
# 运行任意任务分析
python analysis/qe_research/scripts/pareto_analysis_code.py
python analysis/qe_research/scripts/pareto_analysis_creative.py
python analysis/qe_research/scripts/pareto_analysis_math.py
python analysis/qe_research/scripts/pareto_analysis_qa.py
python analysis/qe_research/scripts/pareto_analysis_summary.py
python analysis/qe_research/scripts/pareto_analysis_translation.py
```

**未重构任务**:
- reasoning - 保留原版（使用人工评分，结构特殊）
  - `pareto_analysis_reasoning.py` - 基础版
  - `pareto_analysis_reasoning_enhanced.py` - 增强版

---

### 1. 任务特定分析脚本（7个）

这些脚本针对特定任务类型进行帕累托前沿分析，结构相似但数据源和质量指标不同。

#### 1.1 `pareto_analysis_code.py` - 代码生成任务
- **质量指标**: 编译成功率（compilation_rate）
- **数据源**: `data/analize/results/code_quality/quality_summary_code.csv`
- **特点**: 评估代码生成的可执行性
- **输出目录**: `results/pareto_analysis/code/`

#### 1.2 `pareto_analysis_creative.py` - 创意写作任务
- **质量指标**: Distinct-2 多样性指标
- **数据源**: `data/analize/results/creative_quality/creative_quality_summary.csv`
- **特点**: 评估文本生成的多样性和创造性
- **输出目录**: `results/pareto_analysis/creative/`

#### 1.3 `pareto_analysis_math.py` - 数学推理任务
- **质量指标**: 数值匹配准确率（numerical_match）
- **数据源**: `data/analize/results/math_quality/math_quality_summary.csv`
- **特点**: 评估数学问题求解的准确性
- **输出目录**: `results/pareto_analysis/math/`

#### 1.4 `pareto_analysis_qa.py` - 问答任务
- **质量指标**: 综合质量得分
- **数据源**: `data/analize/results/qa_quality/qa_quality_summary.csv`
- **特点**: 评估问答的准确性和完整性
- **输出目录**: `results/pareto_analysis/qa/`

#### 1.5 `pareto_analysis_summary.py` - 摘要任务
- **质量指标**: ROUGE-L 得分
- **数据源**: `data/analize/results/summary_quality/summary_quality_summary.csv`
- **特点**: 评估文本摘要的质量
- **输出目录**: `results/pareto_analysis/summary/`

#### 1.6 `pareto_analysis_translation.py` - 翻译任务（基础版）
- **质量指标**: BLEU-1 得分
- **数据源**: `data/analize/results/translation_quality/translation_quality_summary.csv`
- **特点**: 评估机器翻译质量
- **输出目录**: `results/pareto_analysis/translation/`

#### 1.7 `pareto_analysis_translation_enhanced.py` - 翻译任务（增强版）
- **质量指标**: BLEU 得分
- **数据源**: 同上
- **增强功能**:
  - 基础帕累托前沿识别（2D 和 3D）
  - 定量指标：超体积、间距、GD/IGD、边际效益、拐点
  - 稳健性分析：扰动分析、权重敏感性、交叉验证
  - 决策支持：目标达成度、决策鲁棒性、升级代价量化
- **输出目录**: `results/pareto_analysis/translation/`

---

### 2. Reasoning 任务专用脚本（2个）

Reasoning 任务使用人工评分，需要特殊处理。

#### 2.1 `pareto_analysis_reasoning.py` - Reasoning 任务（基础版）
- **质量指标**: 基于人工评分的加权质量得分（熵权法）
- **质量维度**: 正确性、完整性、严谨性、清晰度、效率
- **数据源**: `results/quality_scores/reasoning_scores_aggregated.csv`
- **特点**: 
  - 使用熵权法计算综合质量得分
  - 需要先运行 `extract_manual_scores.py` 提取质量得分
- **输出目录**: `results/pareto_analysis/reasoning/`

#### 2.2 `pareto_analysis_reasoning_enhanced.py` - Reasoning 任务（增强版）
- **质量指标**: 同上
- **增强功能**:
  - 熵权法计算过程可视化
  - 数据分布分析
  - 相关性分析
  - 完整的分析步骤可视化
  - 过程可视化输出到 `process_visualization/` 子目录
- **输出目录**: `results/pareto_analysis/reasoning/`

---

### 3. 通用工具脚本（2个）

#### 3.1 `pareto_metrics_calculator.py` - 定量指标计算器

**状态**: ⚠️ 功能已集成到 pareto_core，建议使用共享模块

**功能模块**:
1. **超体积（Hypervolume, HV）**: 衡量帕累托前沿覆盖的目标空间体积
2. **间距指标（Spacing, SP）**: 衡量前沿解的分布均匀性
3. **最大扩散度（Maximum Spread, MS）**: 衡量前沿的覆盖范围
4. **边际效益分析（Marginal Benefit）**: 分析性能提升的边际成本
5. **拐点识别（Knee Point Detection）**: 识别质效比最优的拐点

**使用方式**: 建议使用 `pareto_core` 中的对应函数

#### 3.2 `pareto_robustness_analyzer.py` - 稳健性分析器

**状态**: ✅ 功能已集成到 pareto_core.shared_functions

**功能模块**:
1. **扰动分析（Perturbation Analysis）**: 
   - 添加噪声测试前沿稳定性
   - 默认噪声水平 ±5%，迭代 100 次
   - 已集成为 `perturbation_analysis()` 函数
2. **权重敏感性分析（Weight Sensitivity Analysis）**: 
   - 测试不同权重配置下的前沿变化
   - 待集成
3. **交叉验证（Cross Validation）**: 
   - 验证前沿的可靠性
   - 已集成为 `cross_validation_pareto()` 函数

**使用方式**: 
```python
from pareto_core import perturbation_analysis, cross_validation_pareto

# 扰动分析
robustness = perturbation_analysis(df, 'quality', 'energy', 
                                   x_minimize=False, y_minimize=True)

# 交叉验证
cv_results = cross_validation_pareto(df, 'quality', 'energy',
                                     x_minimize=False, y_minimize=True)
```

---

### 4. 批量处理脚本（3个）

#### 4.1 `universal_pareto_analyzer.py` - 通用分析系统
**功能**: 整合所有分析功能的通用框架
- 熵权法计算质量综合得分
- 帕累托前沿识别（2D + 3D）
- 定量指标计算（超体积、间距、扩散度、边际效益、拐点）
- 稳健性验证（扰动分析、权重敏感性、交叉验证）
- 自动生成完整报告

**使用方式**:
```bash
python universal_pareto_analyzer.py --task reasoning --quality-file path/to/quality.csv --energy-file path/to/energy.csv
```

**依赖模块**: 
- `pareto_core.EntropyWeightCalculator`
- `pareto_core.ParetoFrontierIdentifier`
- `pareto_core.QuantitativeMetricsCalculator`
- `pareto_core.RobustnessAnalyzer`
- `pareto_core.ReportGenerator`

#### 4.2 `batch_pareto_analysis.py` - 批量分析脚本
**功能**: 批量处理多个任务的帕累托分析
- 支持任务: qa, summary, creative, translation
- 自动检查数据文件是否存在
- 依次运行各任务的分析脚本

**使用方式**:
```bash
python batch_pareto_analysis.py
```

#### 4.3 `quick_pareto_analysis.py` - 快速分析工具
**功能**: 一键完成基础分析
- 熵权法计算
- 帕累托前沿识别
- 定量指标计算
- 稳健性验证

**使用方式**:
```bash
python quick_pareto_analysis.py --task reasoning --quality-file path/to/file.csv
```

---

## 共同特征

### 数据输入
所有任务特定脚本都使用以下三类数据：
1. **质量数据**: 各任务的质量评估结果（CSV 格式）
2. **能耗数据**: `results/derived_metrics/08_energy_per_token.csv`
3. **速度数据**: `results/derived_metrics/07_avg_token_speed.csv`

### 模型名称映射
所有脚本都包含统一的模型名称映射表，将质量数据中的短名称映射到能耗/速度数据中的完整名称：
```python
model_mapping = {
    'deepseek_8b_ol_q4km': 'deepseek-r1:8b',
    'gemma_2b_hf_4bit': 'google--gemma-2b-it:4bit',
    'gemma_2b_hf_8bit': 'google--gemma-2b-it:8bit',
    'gemma_4b_ol_q4km': 'gemma3:4b',
    'phi3_4b_hf_4bit': 'microsoft--phi-3-mini-4k-instruct:4bit',
    'phi3_4b_hf_8bit': 'microsoft--phi-3-mini-4k-instruct:8bit',
    'qwen25_3b_hf_4bit': 'qwen--qwen2.5-3b-instruct:4bit',
    'qwen25_3b_hf_8bit': 'qwen--qwen2.5-3b-instruct:8bit',
    'qwen25_7b_hf_4bit': 'qwen--qwen2.5-7b-instruct:4bit',
    'qwen_4b_ol_q4km': 'qwen3:4b',
    'qwen_8b_ol_q4km': 'qwen3:8b'
}
```

### 分析维度
- **质量（Quality）**: 最大化，任务特定指标
- **能耗（Energy）**: 最小化，每 token 能耗（J/token）
- **速度（Speed）**: 最大化，token 生成速度（tokens/s）

### 输出内容
1. **数据文件**:
   - `merged_data.csv`: 合并后的原始数据
   - `pareto_2d_*.csv`: 2D 帕累托前沿数据
   - `pareto_3d.csv`: 3D 帕累托前沿数据

2. **可视化图表**:
   - 2D 帕累托前沿图（质量 vs 能耗、质量 vs 速度）
   - 3D 帕累托前沿图
   - 定量指标可视化
   - 稳健性分析图表

3. **分析报告**:
   - `README.md`: 完整分析报告
   - `QUICK_REFERENCE.md`: 快速参考指南

---

## 脚本对比

### 基础版 vs 增强版

| 特性 | 基础版 | 增强版 |
|------|--------|--------|
| 帕累托前沿识别 | ✓ | ✓ |
| 2D/3D 可视化 | ✓ | ✓ |
| 定量指标 | 基础 | 完整（HV, SP, MS, MB, Knee） |
| 稳健性分析 | ✗ | ✓（扰动、权重敏感性、交叉验证） |
| 决策支持 | ✗ | ✓（目标达成度、升级代价） |
| 过程可视化 | ✗ | ✓（熵权法、分布、相关性） |

**增强版适用任务**: Translation, Reasoning

### 任务特定 vs 通用工具

| 类型 | 脚本 | 特点 |
|------|------|------|
| 任务特定 | `pareto_analysis_*.py` | 针对特定任务优化，直接可运行 |
| 通用工具 | `pareto_metrics_calculator.py` | 提供可复用的计算函数 |
| 通用工具 | `pareto_robustness_analyzer.py` | 提供可复用的分析函数 |
| 通用框架 | `universal_pareto_analyzer.py` | 整合所有功能，支持任意任务 |

---

## 使用建议

### 1. 单任务分析
直接运行对应的任务特定脚本：
```bash
# 代码生成任务
python analysis/qe_research/scripts/pareto_analysis_code.py

# Reasoning 任务（增强版）
python analysis/qe_research/scripts/pareto_analysis_reasoning_enhanced.py

# 翻译任务（增强版）
python analysis/qe_research/scripts/pareto_analysis_translation_enhanced.py
```

### 2. 批量分析
使用批量处理脚本：
```bash
python analysis/qe_research/scripts/batch_pareto_analysis.py
```

### 3. 快速原型
使用快速分析工具：
```bash
python analysis/qe_research/scripts/quick_pareto_analysis.py --task reasoning
```

### 4. 自定义分析
使用通用分析系统：
```bash
python analysis/qe_research/scripts/universal_pareto_analyzer.py \
    --task custom_task \
    --quality-file path/to/quality.csv \
    --energy-file path/to/energy.csv \
    --speed-file path/to/speed.csv
```

---

## 依赖关系

```
任务特定脚本
    ├── pareto_metrics_calculator.py (定量指标)
    └── pareto_robustness_analyzer.py (稳健性分析)

universal_pareto_analyzer.py
    └── pareto_core/ (核心模块)
        ├── EntropyWeightCalculator
        ├── ParetoFrontierIdentifier
        ├── QuantitativeMetricsCalculator
        ├── RobustnessAnalyzer
        └── ReportGenerator

batch_pareto_analysis.py
    └── 调用各任务特定脚本

quick_pareto_analysis.py
    └── 独立实现（轻量级）
```

---

## 核心算法

### 1. 帕累托前沿识别
对于每个解 i，检查是否存在其他解 j 满足：
- 在所有目标上不差于 i
- 至少在一个目标上严格优于 i

如果不存在这样的 j，则 i 是帕累托最优解。

### 2. 熵权法（Reasoning 任务）
1. 数据标准化: `x_norm = (x - x_min) / (x_max - x_min)`
2. 计算概率: `p = x_norm / sum(x_norm)`
3. 计算熵: `H = -sum(p * log(p)) / log(n)`
4. 计算权重: `w = (1 - H) / sum(1 - H)`

### 3. 超体积计算
计算帕累托前沿与参考点之间的目标空间体积，值越大表示前沿质量越好。

### 4. 扰动分析
添加 ±5% 噪声，重复 100 次，统计模型在前沿中的出现频率，评估稳定性。

---

## 输出示例

### 目录结构
```
results/pareto_analysis/{task}/
├── merged_data.csv                 # 合并数据
├── pareto_2d_quality_energy.csv    # 2D 前沿（质量-能耗）
├── pareto_2d_quality_speed.csv     # 2D 前沿（质量-速度）
├── pareto_3d.csv                   # 3D 前沿
├── figures/                        # 可视化图表
│   ├── pareto_2d_quality_energy.png
│   ├── pareto_2d_quality_speed.png
│   ├── pareto_3d.png
│   └── ...
├── README.md                       # 完整报告
└── QUICK_REFERENCE.md              # 快速参考
```

### 报告内容
1. 数据概览
2. 帕累托前沿识别结果
3. 定量指标分析
4. 稳健性验证
5. 决策建议

---

## 注意事项

1. **数据格式**: 确保质量数据、能耗数据、速度数据的模型名称一致
2. **模型映射**: 检查 `model_mapping` 是否包含所有模型
3. **质量指标**: 不同任务的质量指标列名可能不同，需要确认
4. **Reasoning 任务**: 需要先运行 `extract_manual_scores.py` 提取人工评分
5. **中文显示**: 脚本已配置中文字体，确保系统安装了 Microsoft YaHei

---

## 代码重复问题分析

### 重复情况总结

经过详细检查，发现以下严重的代码重复问题：

#### 1. 任务特定脚本中的重复实现

**所有 7 个任务特定脚本**（code, creative, math, qa, summary, translation, translation_enhanced）都包含以下函数的完全相同或高度相似的实现：

- `identify_pareto_frontier_2d()` - 2D 帕累托前沿识别
- `identify_pareto_frontier_3d()` - 3D 帕累托前沿识别
- `calculate_hypervolume()` - 超体积计算
- `calculate_spacing()` - 间距指标计算
- `find_knee_point()` - 拐点识别

**重复代码量估算**：
- 每个脚本约 200-300 行重复代码
- 7 个脚本总计约 1400-2100 行重复代码
- 代码重复率：约 60-70%

#### 2. 与通用工具脚本的关系

**关键发现**：
- ❌ 任务特定脚本**完全没有**调用 `pareto_metrics_calculator.py` 和 `pareto_robustness_analyzer.py`
- ❌ 所有任务特定脚本都**独立实现**了相同的功能
- ✓ `pareto_metrics_calculator.py` 提供了更完善的实现（包含类封装、更多指标）
- ✓ `pareto_robustness_analyzer.py` 提供了稳健性分析功能

#### 3. 具体重复示例

**`identify_pareto_frontier_2d()` 函数**：
- 在 7 个任务脚本中实现几乎完全相同
- 代码行数：约 40-50 行/脚本
- 总重复：约 280-350 行

**`calculate_hypervolume()` 函数**：
- 在 7 个任务脚本中实现高度相似
- 代码行数：约 30-40 行/脚本
- 总重复：约 210-280 行

**`find_knee_point()` 函数**：
- 在 7 个任务脚本中实现相似（部分有细微差异）
- 代码行数：约 40-50 行/脚本
- 总重复：约 280-350 行

#### 4. 模型名称映射重复

所有任务脚本都包含相同的 `model_mapping` 字典（约 12 行），总重复约 84 行。

### 重复的影响

#### 负面影响：
1. **维护困难**：修改算法需要在 7 个文件中同步更新
2. **一致性风险**：不同脚本可能出现实现差异
3. **代码膨胀**：大量重复代码增加代码库体积
4. **测试成本**：需要为每个脚本单独测试相同功能
5. **学习成本**：新开发者需要理解多个相似实现

#### 正面方面：
1. **独立性**：每个脚本可以独立运行，不依赖外部模块
2. **简单性**：不需要理解复杂的类继承关系
3. **调试方便**：问题定位在单个文件内

### 重构建议

#### 方案 1：使用通用工具类（推荐）

```python
# 任务特定脚本简化为：
from analysis.qe_research.scripts.pareto_metrics_calculator import ParetoMetricsCalculator
from analysis.qe_research.scripts.pareto_robustness_analyzer import ParetoRobustnessAnalyzer

def main():
    # 1. 加载数据
    df = load_and_prepare_data()
    
    # 2. 使用通用工具
    calculator = ParetoMetricsCalculator(df)
    pareto_qe = calculator.identify_pareto_frontier_2d('quality', 'energy')
    hv = calculator.calculate_hypervolume_2d(pareto_qe, 'quality', 'energy', ref_point)
    
    # 3. 稳健性分析
    analyzer = ParetoRobustnessAnalyzer(df)
    robustness = analyzer.perturbation_analysis('quality', 'energy')
    
    # 4. 生成报告
    generate_report(df, results)
```

**优点**：
- 消除 60-70% 的重复代码
- 统一算法实现，保证一致性
- 便于维护和扩展

**缺点**：
- 需要重构现有脚本
- 增加模块间依赖

#### 方案 2：提取共享模块

创建 `pareto_core/shared_functions.py`：
```python
# 共享函数库
def identify_pareto_frontier_2d(df, x_col, y_col, x_minimize=True, y_minimize=True):
    """通用 2D 帕累托前沿识别"""
    # 实现...

def calculate_hypervolume(df, pareto_mask, reference_point):
    """通用超体积计算"""
    # 实现...

# 其他共享函数...
```

任务脚本导入：
```python
from pareto_core.shared_functions import (
    identify_pareto_frontier_2d,
    calculate_hypervolume,
    find_knee_point
)
```

**优点**：
- 保持脚本结构相对简单
- 逐步重构，风险较低

**缺点**：
- 仍需要在每个脚本中调用
- 不如类封装灵活

#### 方案 3：使用 universal_pareto_analyzer（最佳）

完全使用 `universal_pareto_analyzer.py`，任务特定脚本变为配置文件：

```yaml
# config/pareto_analysis_code.yaml
task_name: code
quality_file: data/analize/results/code_quality/quality_summary_code.csv
quality_metric: compilation_rate_mean
energy_file: analysis/qe_research/results/derived_metrics/08_energy_per_token.csv
speed_file: analysis/qe_research/results/derived_metrics/07_avg_token_speed.csv
output_dir: analysis/qe_research/results/pareto_analysis/code
```

运行命令：
```bash
python universal_pareto_analyzer.py --config config/pareto_analysis_code.yaml
```

**优点**：
- 完全消除代码重复
- 配置驱动，易于管理
- 统一的分析流程

**缺点**：
- 需要大规模重构
- 学习成本较高

### 推荐行动计划

#### 短期（1-2 周）：
1. ✅ 创建 `pareto_core/` 模块目录
2. ✅ 提取共享函数到 `shared_functions.py`
3. ✅ 重构 1-2 个任务脚本作为示例
4. ✅ 编写单元测试

#### 中期（1 个月）：
1. ✅ 重构所有任务特定脚本使用共享函数
2. ✅ 统一模型名称映射到配置文件
3. ✅ 完善 `universal_pareto_analyzer.py`
4. ✅ 编写完整文档

#### 长期（2-3 个月）：
1. ✅ 迁移到配置驱动模式
2. ✅ 废弃旧的任务特定脚本
3. ✅ 建立自动化测试流程
4. ✅ 优化性能和可扩展性

---

## 未来改进方向

1. **消除代码重复**: 按照上述重构建议，将重复代码降低到 10% 以下
2. **统一接口**: 将所有任务特定脚本整合到 `universal_pareto_analyzer.py`
3. **配置文件**: 使用 YAML 配置文件管理任务参数
4. **交互式可视化**: 使用 Plotly 生成交互式图表
5. **自动化报告**: 生成 LaTeX 格式的学术报告
6. **多目标优化**: 支持超过 3 个目标的分析
7. **实时分析**: 支持增量数据的实时分析
8. **单元测试**: 为所有核心函数编写测试用例

---

## 相关文档

- [README_PARETO.md](../README_PARETO.md): 帕累托分析总体说明
- [EVALUATION_SUMMARY.md](../results/pareto_analysis/EVALUATION_SUMMARY.md): 评估总结
- [AGENTS.md](../../../AGENTS.md): 项目整体指南

---

**文档版本**: 1.0  
**最后更新**: 2026-03-06  
**维护者**: GenAI Power Analysis Team
