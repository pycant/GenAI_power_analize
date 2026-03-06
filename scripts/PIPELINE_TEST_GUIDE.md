# 数据管道测试指南

## 概述

本指南帮助你测试数据管道系统并进行初步的探索性分析。

## 快速开始

### 方法1: 运行完整测试（推荐）

```bash
# 激活conda环境
conda activate bartscore

# 设置UTF-8编码（Windows）
set PYTHONUTF8=1

# 运行测试脚本
python scripts/test_and_explore_pipeline.py
```

这个脚本会：
1. ✅ 测试JSON加载器
2. ✅ 初始化数据管道
3. ✅ 加载和验证数据
4. ✅ 数据概览分析
5. ✅ 性能指标分析
6. ✅ 资源使用分析
7. ✅ 质量指标分析
8. ✅ 任务分布分析
9. ✅ 数据质量检查
10. ✅ 生成总结报告

### 方法2: 分步测试

#### 步骤1: 测试JSON加载器

```bash
cd data/analize/pipeline
python test_json_loaders.py
```

#### 步骤2: 运行快速开始

```bash
cd data/analize/pipeline
python quick_start.py
```

#### 步骤3: 查看示例

```bash
cd data/analize/pipeline
python example_json_loading.py
```

## 预期输出

### 1. JSON加载器测试

```
可用模型:
  - deepseek_8b_ol_q4km
  - qwen_8b_ol_q4km
  - gemma_4b_ol_q4km
  ...

✓ JSON数据加载成功
  - 总记录数: 120
  - 总列数: 35
```

### 2. 数据管道初始化

```
[1/5] 加载原始数据...
  ✓ 加载完成: 150 行

[2/5] 清洗和标准化...
  ✓ 清洗完成: 150 行

[3/5] 计算派生指标...
  ✓ 计算完成: 45 列

[4/5] 保存主数据...
  ✓ 保存完成

[5/5] 生成分析数据...
  ✓ 生成完成

数据管道完成 (耗时: 15.23秒)
```

### 3. 数据概览

```
【基本信息】
  总记录数: 150
  总列数: 45
  模型数量: 12
  任务类型: 7

【模型信息】
  模型列表:
    - deepseek-r1:8b: 15 条记录
    - qwen3:8b: 15 条记录
    - gemma3:4b: 15 条记录
    ...

【任务类型】
  任务列表:
    - code: 25 条记录
    - qa: 25 条记录
    - creative: 25 条记录
    ...
```

### 4. 性能指标

```
【各模型平均延迟】
  deepseek-r1:8b              :    18.58秒
  qwen3:8b                    :    12.34秒
  gemma3:4b                   :    15.67秒
  ...

【各模型平均吞吐量】
  qwen3:8b                    :    45.23 tokens/s
  deepseek-r1:8b              :    36.59 tokens/s
  gemma3:4b                   :    32.15 tokens/s
  ...

【各模型平均能耗】
  gemma3:4b                   :    1024.56焦耳
  qwen3:8b                    :    1156.78焦耳
  deepseek-r1:8b              :    1387.42焦耳
  ...
```

## 输出文件

测试完成后会生成以下文件：

### 1. 处理后的数据

```
data/analize/processed/
├── master_data.parquet          # 主数据表
├── quality_metrics.parquet      # 质量指标
├── efficiency_metrics.parquet   # 效率指标
├── metadata.json                # 元数据
└── task_summaries/              # 按任务汇总
    ├── code_summary.parquet
    ├── qa_summary.parquet
    └── ...
```

### 2. 报告和日志

```
data/analize/logs/
├── pipeline_test.log            # 测试日志
└── pipeline_test_report.md      # 测试报告
```

### 3. 缓存

```
data/analize/cache/
└── (自动生成的缓存文件)
```

## 常见问题

### Q1: 未找到JSON文件

**问题**: `WARNING - 未找到summary.json文件`

**解决**:
1. 确保模型目录存在: `data/deepseek_8b_ol_q4km/`
2. 确保包含JSON文件: `experiment_results_*_summary.json`
3. 检查文件命名是否正确

### Q2: 数据管道运行失败

**问题**: `ERROR - 数据管道失败`

**解决**:
1. 检查Python环境: `python --version` (需要3.8+)
2. 安装依赖: `pip install pandas pyarrow fastparquet`
3. 查看详细日志: `data/analize/logs/pipeline_test.log`

### Q3: 内存不足

**问题**: `MemoryError`

**解决**:
1. 关闭其他程序释放内存
2. 使用分批处理（已内置）
3. 增加系统虚拟内存

### Q4: 中文乱码

**问题**: 输出显示乱码

**解决**:
```bash
# Windows
set PYTHONUTF8=1

# Linux/Mac
export PYTHONUTF8=1
```

## 验证清单

运行测试后，确认以下内容：

- [ ] JSON加载器成功加载数据
- [ ] 数据管道运行完成
- [ ] 生成了processed目录和文件
- [ ] 数据验证通过
- [ ] 能够查看模型和任务列表
- [ ] 性能指标正常显示
- [ ] 生成了测试报告

## 下一步

测试通过后，可以进行：

1. **综合分析**: 运行 `scripts/comprehensive_qe_analysis.py`
2. **可视化**: 使用 `data/analize/visualization/` 下的脚本
3. **自定义分析**: 使用数据管道API进行自定义分析

## 示例代码

### 基本使用

```python
from data.analize.pipeline import ExperimentDataManager

# 创建数据管理器
dm = ExperimentDataManager()

# 加载数据
df = dm.load_all_data()

# 查看基本信息
print(f"总记录数: {len(df)}")
print(f"模型数量: {len(dm.list_models())}")
print(f"任务类型: {dm.list_tasks()}")
```

### 按模型分析

```python
# 获取特定模型的数据
df_deepseek = dm.get_by_model('deepseek-r1:8b')

# 计算平均性能
avg_latency = df_deepseek['latency_s'].mean()
avg_throughput = df_deepseek['toks_per_s'].mean()
avg_energy = df_deepseek['gpu_energy_j'].mean()

print(f"平均延迟: {avg_latency:.2f}秒")
print(f"平均吞吐: {avg_throughput:.2f} tokens/s")
print(f"平均能耗: {avg_energy:.2f}焦耳")
```

### 按任务分析

```python
# 获取特定任务的数据
df_code = dm.get_by_task('code')

# 按模型对比
comparison = df_code.groupby('model_name').agg({
    'latency_s': 'mean',
    'toks_per_s': 'mean',
    'gpu_energy_j': 'mean'
})

print(comparison)
```

### 计算复合得分

```python
# 计算质效比
scores = dm.compute_composite_score()

# 按模型排名
ranking = scores.groupby('model_name')['composite_score'].mean().sort_values(ascending=False)

print("模型综合排名:")
for i, (model, score) in enumerate(ranking.items(), 1):
    print(f"{i}. {model}: {score:.3f}")
```

## 技术支持

- 查看文档: `data/analize/pipeline/README.md`
- JSON加载器指南: `data/analize/pipeline/JSON_LOADERS_GUIDE.md`
- 实现总结: `data/analize/pipeline/IMPLEMENTATION_SUMMARY.md`

## 更新日志

### v1.0 (2026-03-05)

- ✅ 初始版本
- ✅ 完整的测试流程
- ✅ 探索性分析
- ✅ 自动报告生成
