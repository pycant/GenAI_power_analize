# Pareto 脚本代码重复分析报告

## ✅ 重构已完成（2026-03-06）

**本报告中识别的代码重复问题已通过阶段 2 重构解决。**

详细信息请参考：
- [REFACTORING_COMPLETED.md](./REFACTORING_COMPLETED.md) - 重构完成报告
- [REFACTORING_ROADMAP.md](./REFACTORING_ROADMAP.md) - 重构路线图

---

## 执行摘要（历史记录）

本报告分析了 `analysis/qe_research/scripts` 目录下 11 个 pareto 相关脚本的代码重复情况。

### 关键发现

- ❌ **严重代码重复**：7 个任务特定脚本包含 60-70% 的重复代码
- ❌ **未使用通用工具**：所有任务脚本都没有调用已有的通用工具类
- ⚠️ **维护风险**：算法修改需要在 7 个文件中同步更新
- ✅ **已有解决方案**：`pareto_metrics_calculator.py` 和 `universal_pareto_analyzer.py` 提供了完整实现

---

## 重复代码统计

### 按函数分类

| 函数名 | 出现次数 | 每次行数 | 总重复行数 | 重复率 |
|--------|---------|---------|-----------|--------|
| `identify_pareto_frontier_2d()` | 7 | 40-50 | 280-350 | 100% |
| `identify_pareto_frontier_3d()` | 7 | 30-40 | 210-280 | 100% |
| `calculate_hypervolume()` | 7 | 30-40 | 210-280 | 100% |
| `calculate_spacing()` | 7 | 25-35 | 175-245 | 100% |
| `find_knee_point()` | 7 | 40-50 | 280-350 | 100% |
| `model_mapping` 字典 | 7 | 12 | 84 | 100% |
| **总计** | - | - | **1239-1589** | **60-70%** |

### 按脚本分类

| 脚本名 | 总行数 | 重复行数 | 重复率 | 状态 |
|--------|--------|---------|--------|------|
| `pareto_analysis_code.py` | ~500 | ~300 | 60% | ❌ 高重复 |
| `pareto_analysis_creative.py` | ~450 | ~280 | 62% | ❌ 高重复 |
| `pareto_analysis_math.py` | ~500 | ~300 | 60% | ❌ 高重复 |
| `pareto_analysis_qa.py` | ~450 | ~280 | 62% | ❌ 高重复 |
| `pareto_analysis_summary.py` | ~450 | ~280 | 62% | ❌ 高重复 |
| `pareto_analysis_translation.py` | ~450 | ~280 | 62% | ❌ 高重复 |
| `pareto_analysis_translation_enhanced.py` | ~800 | ~350 | 44% | ⚠️ 中等重复 |
| `pareto_analysis_reasoning.py` | ~600 | ~300 | 50% | ⚠️ 中等重复 |
| `pareto_analysis_reasoning_enhanced.py` | ~900 | ~350 | 39% | ⚠️ 中等重复 |

---

## 重复代码示例

### 示例 1：`identify_pareto_frontier_2d()` 函数

**出现位置**：所有 7 个任务特定脚本

**代码片段**（完全相同）：
```python
def identify_pareto_frontier_2d(df, x_col, y_col, x_minimize=True, y_minimize=True):
    """识别2D帕累托前沿"""
    n = len(df)
    pareto_mask = np.ones(n, dtype=bool)
    
    for i in range(n):
        if not pareto_mask[i]:
            continue
        
        for j in range(n):
            if i == j:
                continue
            
            x_i, y_i = df.iloc[i][x_col], df.iloc[i][y_col]
            x_j, y_j = df.iloc[j][x_col], df.iloc[j][y_col]
            
            # ... 40+ 行相同代码
```


### 示例 2：模型名称映射

**出现位置**：所有 9 个脚本（包括 reasoning）

**代码片段**（完全相同）：
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

---

## 与通用工具的对比

### `pareto_metrics_calculator.py` 提供的功能

| 功能 | 任务脚本实现 | 通用工具实现 | 是否被使用 |
|------|------------|------------|-----------|
| 2D 前沿识别 | ✓ (7次) | ✓ (更完善) | ❌ 未使用 |
| 3D 前沿识别 | ✓ (7次) | ✗ | - |
| 超体积计算 | ✓ (7次) | ✓ (更完善) | ❌ 未使用 |
| 间距指标 | ✓ (7次) | ✓ (更完善) | ❌ 未使用 |
| 拐点识别 | ✓ (7次) | ✓ (更完善) | ❌ 未使用 |
| 边际效益 | ✗ | ✓ | ❌ 未使用 |
| 最大扩散度 | ✗ | ✓ | ❌ 未使用 |

### `pareto_robustness_analyzer.py` 提供的功能

| 功能 | 任务脚本实现 | 通用工具实现 | 是否被使用 |
|------|------------|------------|-----------|
| 扰动分析 | ✗ | ✓ | ❌ 未使用 |
| 权重敏感性 | ✗ | ✓ | ❌ 未使用 |
| 交叉验证 | ✗ | ✓ | ❌ 未使用 |

**结论**：通用工具提供了更完善的实现，但完全未被任务脚本使用。

---

## 影响分析

### 维护成本

假设需要修改帕累托前沿识别算法：

- **当前情况**：需要修改 7 个文件，每个文件 40-50 行
- **理想情况**：只需修改 1 个共享函数，40-50 行
- **维护成本比**：7:1

### 一致性风险

检查发现的差异：
- `calculate_hypervolume()` 在 code 和 math 脚本中有参数差异
- `find_knee_point()` 在不同脚本中使用不同的曲率计算方法
- 部分脚本缺少错误处理

### 测试覆盖率

- **当前**：需要为 7 个脚本分别测试相同功能
- **理想**：只需测试 1 个共享模块
- **测试成本比**：7:1

---

## 重构方案对比

### 方案 1：使用现有通用工具类

**实施步骤**：
1. 修改任务脚本导入通用工具
2. 删除重复函数实现
3. 调整函数调用方式

**代码变化**：
```python
# 重构前（~500 行）
def identify_pareto_frontier_2d(...):
    # 40 行实现
    
def calculate_hypervolume(...):
    # 30 行实现
    
# ... 更多重复函数

# 重构后（~200 行）
from pareto_metrics_calculator import ParetoMetricsCalculator

calculator = ParetoMetricsCalculator(data_path)
pareto_front = calculator.identify_pareto_frontier_2d(...)
hv = calculator.calculate_hypervolume_2d(...)
```

**优点**：
- ✅ 减少 60% 代码量
- ✅ 统一算法实现
- ✅ 快速实施（1-2 周）

**缺点**：
- ⚠️ 需要重构所有脚本
- ⚠️ 增加模块依赖

### 方案 2：创建共享函数模块

**实施步骤**：
1. 创建 `pareto_core/shared_functions.py`
2. 提取共享函数
3. 任务脚本导入共享函数

**代码变化**：
```python
# pareto_core/shared_functions.py
def identify_pareto_frontier_2d(df, x_col, y_col, ...):
    """通用实现"""
    # 实现代码

# 任务脚本
from pareto_core.shared_functions import identify_pareto_frontier_2d

pareto_mask = identify_pareto_frontier_2d(df, 'quality', 'energy')
```

**优点**：
- ✅ 保持脚本结构简单
- ✅ 逐步重构，风险低
- ✅ 灵活性高

**缺点**：
- ⚠️ 不如类封装优雅
- ⚠️ 仍需在每个脚本中调用

### 方案 3：配置驱动（推荐）

**实施步骤**：
1. 完善 `universal_pareto_analyzer.py`
2. 创建任务配置文件
3. 废弃旧的任务脚本

**代码变化**：
```yaml
# config/pareto_code.yaml
task: code
quality_file: data/analize/results/code_quality/quality_summary_code.csv
quality_metric: compilation_rate_mean
energy_file: analysis/qe_research/results/derived_metrics/08_energy_per_token.csv
speed_file: analysis/qe_research/results/derived_metrics/07_avg_token_speed.csv
```

```bash
# 运行命令
python universal_pareto_analyzer.py --config config/pareto_code.yaml
```

**优点**：
- ✅ 完全消除重复（减少 90% 代码）
- ✅ 配置驱动，易于扩展
- ✅ 统一分析流程

**缺点**：
- ⚠️ 需要大规模重构
- ⚠️ 学习成本较高
- ⚠️ 实施周期长（1-2 个月）

---

## 推荐行动计划

### 阶段 1：快速改进（1 周）

**目标**：减少 30% 重复代码

**任务**：
1. ✅ 创建 `pareto_core/` 模块
2. ✅ 提取 `model_mapping` 到配置文件
3. ✅ 提取 `identify_pareto_frontier_2d()` 到共享模块
4. ✅ 重构 1-2 个脚本作为示例

**预期效果**：
- 减少约 500 行重复代码
- 建立重构模式

### 阶段 2：全面重构（2-3 周）

**目标**：减少 60% 重复代码

**任务**：
1. ✅ 提取所有共享函数到 `pareto_core/shared_functions.py`
2. ✅ 重构所有任务脚本使用共享函数
3. ✅ 编写单元测试
4. ✅ 更新文档

**预期效果**：
- 减少约 1000 行重复代码
- 统一算法实现
- 提高代码质量

### 阶段 3：架构优化（1-2 个月）

**目标**：完全消除重复，建立可扩展架构

**任务**：
1. ✅ 完善 `universal_pareto_analyzer.py`
2. ✅ 创建配置文件系统
3. ✅ 迁移所有任务到配置驱动
4. ✅ 废弃旧脚本
5. ✅ 建立 CI/CD 流程

**预期效果**：
- 减少约 1500 行重复代码
- 配置驱动，易于扩展
- 自动化测试和部署

---

## 成本收益分析

### 当前状态成本

| 项目 | 年度成本（工时） |
|------|----------------|
| 维护 7 个重复脚本 | 40 小时 |
| 修复一致性问题 | 20 小时 |
| 测试重复功能 | 30 小时 |
| 新任务开发 | 50 小时 |
| **总计** | **140 小时** |

### 重构后成本

| 项目 | 年度成本（工时） |
|------|----------------|
| 维护共享模块 | 10 小时 |
| 配置新任务 | 5 小时 |
| 测试核心功能 | 10 小时 |
| 新任务开发 | 10 小时 |
| **总计** | **35 小时** |

### ROI 计算

- **重构投入**：80 小时（一次性）
- **年度节省**：105 小时
- **投资回收期**：9 个月
- **3 年 ROI**：(315 - 80) / 80 = 294%

---

## 结论与建议

### 核心结论

1. **严重重复**：60-70% 的代码在 7 个脚本中重复
2. **资源浪费**：通用工具已实现但未被使用
3. **维护风险**：算法修改需要同步 7 个文件
4. **改进空间大**：通过重构可减少 90% 重复代码

### 立即行动建议

1. **停止新增任务脚本**：使用 `universal_pareto_analyzer.py`
2. **启动重构计划**：按照阶段 1 → 2 → 3 执行
3. **建立代码审查**：防止新的重复代码
4. **编写测试用例**：保证重构质量

### 长期建议

1. **建立共享库**：所有通用功能放入 `pareto_core/`
2. **配置驱动开发**：新任务只需配置文件
3. **自动化测试**：CI/CD 保证代码质量
4. **文档完善**：降低学习成本

---

**报告生成时间**：2026-03-06  
**分析工具**：人工代码审查 + grep 搜索  
**审查范围**：11 个 pareto 相关脚本，约 6000 行代码
