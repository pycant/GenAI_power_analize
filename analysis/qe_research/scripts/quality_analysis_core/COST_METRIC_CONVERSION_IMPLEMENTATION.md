# 成本型指标转换功能实现说明

## 实现时间
2026-03-08

## 问题背景

在质量数据分析中，不同指标具有不同的效应方向：
- **效益型指标（Benefit-type）**：数值越大越好（如准确率、F1分数、BLEU等）
- **成本型指标（Cost-type）**：数值越小越好（如困惑度perplexity、延迟latency、错误率等）

在进行归一化和综合评分计算之前，必须将所有指标统一为同一方向（效益型），否则会导致：
1. 归一化结果错误（成本型指标的高值被错误地视为好）
2. PCA综合评分失真（成本型指标贡献方向相反）
3. 模型排名不准确

## 解决方案

### 1. 识别成本型指标

根据 `data/analize/results/METRICS_GUIDE.md` 中的指标定义，当前识别的成本型指标：

| 指标名称 | 英文名称 | 说明 | 所属任务 |
|---------|---------|------|---------|
| 困惑度 | perplexity | 语言模型困惑度，越低越好 | creative |

未来可能添加的成本型指标：
- `latency` - 推理延迟
- `error_rate` - 错误率
- `cost` - 计算成本

### 2. 转换方法

使用**倒数转换法**将成本型指标转换为效益型：

```python
benefit = 1 / (cost + epsilon)
```

其中 `epsilon = 1e-10` 用于避免除零错误。

**特殊情况处理**：
- 如果指标存在负值或零值，先平移到正数域：
  ```python
  benefit = 1 / (cost - min_val + 1 + epsilon)
  ```

### 3. 实现位置

#### 3.1 共享函数模块 (`shared_functions.py`)

新增两个函数：

```python
def get_cost_type_metrics() -> List[str]:
    """获取成本型指标列表"""
    return ['perplexity']  # 可扩展

def convert_cost_to_benefit(df: pd.DataFrame, cost_metrics: List[str] = None) -> pd.DataFrame:
    """将成本型指标转换为效益型指标"""
    # 自动识别并转换
    # 输出转换日志
```

#### 3.2 质量数据分析器 (`quality_data_analyzer.py`)

在两个关键位置调用转换函数：

**位置1：单任务分析** (`analyze_task` 方法)
```python
def analyze_task(self, task_type: str) -> Dict:
    # ... 加载数据 ...
    
    # 成本型指标转换（在归一化之前）
    print("  检查成本型指标...")
    df = sf.convert_cost_to_benefit(df)
    
    # ... 后续分析 ...
```

**位置2：跨任务分析** (`cross_task_analysis` 方法)
```python
def cross_task_analysis(self) -> Dict:
    for task_type, df in self.data.items():
        # 成本型指标转换（在使用数据之前）
        df = sf.convert_cost_to_benefit(df)
        # ... 后续处理 ...
```

## 转换效果示例

假设 `perplexity` 指标的原始数据范围为 `[10.5, 50.2]`：

```
转换前（成本型）：
  模型A: perplexity = 10.5  （最好）
  模型B: perplexity = 30.0  （中等）
  模型C: perplexity = 50.2  （最差）

转换后（效益型）：
  模型A: perplexity = 0.0952  （最好）
  模型B: perplexity = 0.0333  （中等）
  模型C: perplexity = 0.0199  （最差）
```

转换后的值保持了原始的排序关系，但方向统一为"越大越好"。

## 验证方法

### 1. 日志输出验证

运行分析脚本时，会输出转换日志：

```
检查成本型指标...
  成本型指标转换: perplexity (原始范围: [10.5000, 50.2000]) 
                -> (转换后范围: [0.0199, 0.0952])
```

如果没有成本型指标，会输出：
```
  未发现需要转换的成本型指标
```

### 2. 数据一致性检查

转换后应满足：
- 原始数据中最小值 → 转换后最大值
- 原始数据中最大值 → 转换后最小值
- 排序关系完全反转

### 3. PCA结果验证

转换后，PCA综合评分应该：
- 困惑度低的模型得分更高
- 与其他效益型指标方向一致

## 使用注意事项

### 1. 添加新的成本型指标

如需添加新的成本型指标，修改 `shared_functions.py` 中的 `get_cost_type_metrics()` 函数：

```python
def get_cost_type_metrics() -> List[str]:
    cost_metrics = [
        'perplexity',      # 困惑度
        'latency',         # 延迟（新增）
        'error_rate',      # 错误率（新增）
    ]
    return cost_metrics
```

### 2. 指标命名规范

建议在指标命名中体现方向性：
- 效益型：`accuracy`, `f1_score`, `bleu_score`
- 成本型：`perplexity`, `latency`, `error_rate`

### 3. 数据质量检查

转换前应确保：
- 成本型指标的值都是有效数值（非NaN）
- 如果存在零值或负值，转换函数会自动处理

## 影响范围

### 直接影响
1. **描述性统计**：转换后的均值、标准差等统计量会改变
2. **归一化结果**：Min-Max归一化的结果会正确反映指标方向
3. **PCA综合评分**：所有指标方向一致，PCA结果更准确
4. **模型排名**：基于转换后数据的排名更合理

### 不影响
1. **原始数据文件**：不修改CSV文件，只在内存中转换
2. **相对排序**：同一指标内的模型相对排序保持不变
3. **可视化逻辑**：图表生成逻辑无需修改

## 测试建议

### 单元测试
```python
def test_cost_to_benefit_conversion():
    # 测试正常情况
    df = pd.DataFrame({'perplexity': [10, 20, 30]})
    df_converted = convert_cost_to_benefit(df)
    assert df_converted['perplexity'].iloc[0] > df_converted['perplexity'].iloc[2]
    
    # 测试零值情况
    df_zero = pd.DataFrame({'perplexity': [0, 10, 20]})
    df_converted = convert_cost_to_benefit(df_zero)
    assert all(df_converted['perplexity'] > 0)
```

### 集成测试
运行完整分析流程，检查：
1. 日志输出是否正确
2. 转换后的数据范围是否合理
3. PCA综合排名是否符合预期

## 相关文档

- **指标定义**：`data/analize/results/METRICS_GUIDE.md`
- **共享函数**：`analysis/qe_research/scripts/quality_analysis_core/shared_functions.py`
- **分析器主类**：`analysis/qe_research/scripts/quality_analysis_core/quality_data_analyzer.py`
- **质量评分报告**：`analysis/qe_research/results/quality_scores/QUALITY_SCORES_GENERATION_REPORT_V2.md`

## 版本历史

- **v1.0** (2026-03-08): 初始实现
  - 添加 `get_cost_type_metrics()` 函数
  - 添加 `convert_cost_to_benefit()` 函数
  - 在 `analyze_task()` 和 `cross_task_analysis()` 中集成转换逻辑
  - 识别 `perplexity` 为成本型指标

## 未来改进

1. **自动识别**：基于指标名称或元数据自动识别成本型指标
2. **多种转换方法**：支持其他转换方法（如负号法、最大值减法等）
3. **配置化**：通过配置文件管理成本型指标列表
4. **可视化标注**：在图表中标注哪些指标经过了转换

---

**文档维护者**: Kiro AI Assistant  
**最后更新**: 2026-03-08
