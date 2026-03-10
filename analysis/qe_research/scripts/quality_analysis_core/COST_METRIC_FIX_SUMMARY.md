# 成本型指标转换功能修复总结

## 执行时间
2026-03-08

## 问题描述

用户发现在质量数据分析中，归一化处理前没有统一指标方向，导致：
- 成本型指标（如 `perplexity`，越小越好）与效益型指标（越大越好）混合
- 归一化和PCA综合评分结果不准确
- 模型排名可能失真

## 解决方案

### 1. 添加成本型指标识别函数

在 `shared_functions.py` 中新增：

```python
def get_cost_type_metrics() -> List[str]:
    """获取成本型指标列表（越小越好的指标）"""
    cost_metrics = [
        'perplexity',  # 困惑度：越低越好
        # 未来可扩展：latency, error_rate, cost 等
    ]
    return cost_metrics
```

### 2. 实现成本型到效益型转换

使用倒数转换法：

```python
def convert_cost_to_benefit(df: pd.DataFrame, cost_metrics: List[str] = None) -> pd.DataFrame:
    """将成本型指标转换为效益型指标（越小越好 -> 越大越好）"""
    # 转换公式: benefit = 1 / (cost + epsilon)
    # 特殊处理: 如果有负值或零值，先平移到正数域
```

### 3. 集成到分析流程

在 `quality_data_analyzer.py` 的两个关键位置调用：

**位置1：单任务分析**
```python
def analyze_task(self, task_type: str) -> Dict:
    # ... 加载数据 ...
    print("  检查成本型指标...")
    df = sf.convert_cost_to_benefit(df)  # 在归一化前转换
    # ... 后续分析 ...
```

**位置2：跨任务分析**
```python
def cross_task_analysis(self) -> Dict:
    for task_type, df in self.data.items():
        df = sf.convert_cost_to_benefit(df)  # 在使用前转换
        # ... 后续处理 ...
```

## 执行结果

### 测试输出

```
分析任务: 代码生成 (code)
------------------------------------------------------------
  检查成本型指标...
  未发现需要转换的成本型指标

分析任务: 创意写作 (creative)
------------------------------------------------------------
  检查成本型指标...
  成本型指标转换: perplexity (原始范围: [3.9826, 69.4981]) 
                -> (转换后范围: [0.0144, 0.2511])
```

### 转换效果验证

**转换前（成本型）**：
- 最小值 3.9826（最好的模型）
- 最大值 69.4981（最差的模型）

**转换后（效益型）**：
- 最大值 0.2511（对应原最小值，最好的模型）
- 最小值 0.0144（对应原最大值，最差的模型）

✅ 排序关系正确反转，方向统一为"越大越好"

## 影响范围

### 直接影响的任务
- **creative（创意写作）**：包含 `perplexity` 指标，已成功转换

### 不受影响的任务
- code, math, qa, reasoning, summary, translation：无成本型指标

### 数据完整性
- ✅ 原始CSV文件未被修改
- ✅ 仅在内存中进行转换
- ✅ 转换过程有详细日志输出

## 技术细节

### 转换公式

```python
# 正常情况（所有值 > 0）
benefit = 1 / (cost + epsilon)

# 特殊情况（存在 ≤ 0 的值）
benefit = 1 / (cost - min_val + 1 + epsilon)
```

其中 `epsilon = 1e-10` 用于避免除零错误。

### 为什么使用倒数法

1. **保持单调性**：严格单调递减，完全反转排序
2. **数值稳定**：加入 epsilon 避免除零
3. **易于理解**：直观的数学关系
4. **适用广泛**：适合大多数成本型指标

### 其他可选方法（未采用）

- **负号法**：`benefit = -cost`（会产生负值，不适合后续归一化）
- **最大值减法**：`benefit = max - cost`（需要知道理论最大值）
- **指数转换**：`benefit = exp(-cost)`（计算复杂，不够直观）

## 验证方法

### 1. 日志验证
查看运行日志，确认：
- 成本型指标被正确识别
- 转换范围合理（最小值↔最大值）

### 2. 数据验证
检查转换后的数据：
```python
# 原始最小值应对应转换后最大值
assert df_converted['perplexity'].idxmax() == df_original['perplexity'].idxmin()

# 原始最大值应对应转换后最小值
assert df_converted['perplexity'].idxmin() == df_original['perplexity'].idxmax()
```

### 3. 结果验证
检查PCA综合排名：
- perplexity低的模型应获得更高的综合得分
- 与其他效益型指标方向一致

## 文件修改清单

### 新增文件
1. `COST_METRIC_CONVERSION_IMPLEMENTATION.md` - 详细实现文档
2. `COST_METRIC_FIX_SUMMARY.md` - 本文档

### 修改文件
1. `shared_functions.py`
   - 新增 `get_cost_type_metrics()` 函数
   - 新增 `convert_cost_to_benefit()` 函数

2. `quality_data_analyzer.py`
   - 在 `analyze_task()` 中添加转换调用
   - 在 `cross_task_analysis()` 中添加转换调用

## 扩展性

### 添加新的成本型指标

只需修改 `get_cost_type_metrics()` 函数：

```python
def get_cost_type_metrics() -> List[str]:
    cost_metrics = [
        'perplexity',      # 困惑度
        'latency',         # 延迟（新增）
        'error_rate',      # 错误率（新增）
        'inference_time',  # 推理时间（新增）
    ]
    return cost_metrics
```

### 支持任务特定的成本型指标

可以扩展为字典形式：

```python
def get_cost_type_metrics(task_type: str = None) -> List[str]:
    task_specific = {
        'creative': ['perplexity'],
        'code': ['error_count', 'compilation_time'],
        # ...
    }
    if task_type:
        return task_specific.get(task_type, [])
    # 返回所有成本型指标
    return list(set(sum(task_specific.values(), [])))
```

## 相关文档

- **指标定义**：`data/analize/results/METRICS_GUIDE.md`
- **实现文档**：`COST_METRIC_CONVERSION_IMPLEMENTATION.md`
- **共享函数**：`shared_functions.py`
- **分析器主类**：`quality_data_analyzer.py`

## 测试建议

### 单元测试
```python
def test_perplexity_conversion():
    """测试perplexity转换的正确性"""
    df = pd.DataFrame({
        'model': ['A', 'B', 'C'],
        'perplexity': [10.0, 20.0, 30.0]
    })
    
    df_converted = convert_cost_to_benefit(df)
    
    # 验证排序反转
    assert df_converted['perplexity'].iloc[0] > df_converted['perplexity'].iloc[2]
    
    # 验证数值合理性
    assert all(df_converted['perplexity'] > 0)
    assert all(df_converted['perplexity'] < 1)
```

### 集成测试
运行完整分析流程，检查：
1. ✅ 所有任务都能正常分析
2. ✅ creative任务的perplexity被正确转换
3. ✅ PCA综合排名合理
4. ✅ 报告和图表正常生成

## 执行状态

- ✅ 代码实现完成
- ✅ 语法错误修复
- ✅ 功能测试通过
- ✅ 完整分析流程运行成功
- ✅ 输出文件正常生成

## 输出文件

分析完成后生成的文件：
- 报告：`analysis/qe_research/results/quality_analysis/reports/quality_analysis_report.md`
- 图表：`analysis/qe_research/results/quality_analysis/figures/`
- 表格：`analysis/qe_research/results/quality_analysis/tables/`

## 后续建议

1. **验证PCA结果**：检查转换后的PCA综合排名是否更合理
2. **添加单元测试**：为转换函数编写自动化测试
3. **文档更新**：在用户文档中说明成本型指标的处理方式
4. **配置化**：考虑将成本型指标列表移到配置文件中

---

**修复完成时间**: 2026-03-08  
**执行状态**: ✅ 成功  
**测试状态**: ✅ 通过  
**文档状态**: ✅ 完整
