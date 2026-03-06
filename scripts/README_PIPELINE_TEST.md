# 数据管道测试说明

## 🎯 目标

测试数据管道系统并进行初步的探索性分析，验证：
- JSON数据加载功能
- 数据转换和标准化
- 数据完整性和质量
- 基本统计分析

## 🚀 快速开始

### 一键运行（推荐）

```bash
# Windows
conda activate bartscore
set PYTHONUTF8=1
python scripts/test_and_explore_pipeline.py
```

```bash
# Linux/Mac
conda activate bartscore
export PYTHONUTF8=1
python scripts/test_and_explore_pipeline.py
```

### 预期时间

- 首次运行: 2-5分钟（需要转换数据）
- 后续运行: 30秒-1分钟（使用缓存）

## 📋 测试流程

脚本会按以下步骤执行：

### 步骤1: 测试JSON加载器
- 扫描模型目录
- 加载summary.json文件
- 验证数据格式

### 步骤2: 初始化数据管道
- 加载原始数据
- 清洗和标准化
- 计算派生指标
- 转换为Parquet格式

### 步骤3: 加载和验证数据
- 加载处理后的数据
- 验证数据完整性
- 检查数据质量

### 步骤4-9: 探索性分析
- 数据概览
- 性能指标分析
- 资源使用分析
- 质量指标分析
- 任务分布分析
- 数据质量检查

### 步骤10: 生成报告
- 创建Markdown报告
- 保存分析结果

## 📊 输出内容

### 控制台输出

```
================================================================================
  步骤1: 测试JSON加载器
================================================================================

✓ 找到 12 个模型目录:
  - deepseek_8b_ol_q4km
  - qwen_8b_ol_q4km
  - gemma_4b_ol_q4km
  ...

✓ JSON数据加载成功
  - 总记录数: 120
  - 总列数: 35

================================================================================
  步骤2: 初始化数据管道
================================================================================

[1/5] 加载原始数据...
  ✓ 加载完成: 150 行

[2/5] 清洗和标准化...
  ✓ 清洗完成: 150 行

...
```

### 生成的文件

```
data/analize/
├── processed/                          # 处理后的数据
│   ├── master_data.parquet            # 主数据表
│   ├── quality_metrics.parquet        # 质量指标
│   ├── efficiency_metrics.parquet     # 效率指标
│   └── task_summaries/                # 按任务汇总
├── logs/                               # 日志和报告
│   ├── pipeline_test.log              # 详细日志
│   └── pipeline_test_report.md        # 测试报告
└── cache/                              # 缓存文件
```

## 📈 关键指标

测试会分析以下指标：

### 性能指标
- ✅ latency_s - 延迟（秒）
- ✅ toks_per_s - 吞吐量（tokens/秒）
- ✅ gpu_energy_j - GPU能耗（焦耳）
- ✅ ttft_s - 首token时间（秒）

### 资源使用
- ✅ cpu_usage_avg - CPU使用率
- ✅ memory_used_avg_mb - 内存使用
- ✅ gpu_util_avg - GPU利用率
- ✅ gpu_memory_avg_mb - GPU显存
- ✅ gpu_power_avg_w - GPU功耗
- ✅ gpu_temp_avg_c - GPU温度

### 质量指标
- ✅ bartscore - BARTScore质量得分
- ✅ generated_text_length - 生成文本长度

## ✅ 验证清单

运行完成后，确认：

- [ ] 所有步骤都显示 ✓ 成功
- [ ] 生成了 `processed/` 目录
- [ ] 生成了 `master_data.parquet` 文件
- [ ] 生成了测试报告 `pipeline_test_report.md`
- [ ] 能够看到模型列表和统计信息
- [ ] 性能指标显示正常
- [ ] 无严重错误或警告

## 🐛 故障排除

### 问题1: 未找到模型数据

**症状**:
```
⚠ 警告: 未找到任何模型数据
```

**解决方案**:
1. 检查数据目录是否存在:
   ```bash
   dir data\deepseek_8b_ol_q4km
   dir data\qwen_8b_ol_q4km
   ```

2. 确认JSON文件存在:
   ```bash
   dir data\deepseek_8b_ol_q4km\*_summary.json
   ```

3. 如果没有数据，需要先运行实验生成数据

### 问题2: 依赖缺失

**症状**:
```
ModuleNotFoundError: No module named 'pyarrow'
```

**解决方案**:
```bash
pip install pandas pyarrow fastparquet pyyaml
```

### 问题3: 内存不足

**症状**:
```
MemoryError
```

**解决方案**:
1. 关闭其他程序
2. 重启Python环境
3. 使用分批处理（脚本已内置）

### 问题4: 权限错误

**症状**:
```
PermissionError: [Errno 13] Permission denied
```

**解决方案**:
1. 以管理员身份运行
2. 检查文件是否被其他程序占用
3. 确保有写入权限

## 📚 相关文档

- **详细指南**: `scripts/PIPELINE_TEST_GUIDE.md`
- **数据管道文档**: `data/analize/pipeline/README.md`
- **JSON加载器**: `data/analize/pipeline/JSON_LOADERS_GUIDE.md`
- **实现总结**: `data/analize/pipeline/IMPLEMENTATION_SUMMARY.md`

## 🎓 下一步

测试通过后，可以：

### 1. 查看测试报告

```bash
# Windows
notepad data\analize\logs\pipeline_test_report.md

# Linux/Mac
cat data/analize/logs/pipeline_test_report.md
```

### 2. 进行深入分析

```python
from data.analize.pipeline import ExperimentDataManager

dm = ExperimentDataManager()
df = dm.load_all_data()

# 自定义分析
print(df.describe())
```

### 3. 生成可视化

```bash
cd data/analize/visualization/scripts
python generate_all_visualizations.py
```

### 4. 运行综合分析

```bash
# 待创建
python scripts/comprehensive_qe_analysis.py
```

## 💡 提示

### 加速后续运行

首次运行后，数据已转换为Parquet格式并缓存，后续运行会快很多：

```python
from data.analize.pipeline import ExperimentDataManager

dm = ExperimentDataManager()
df = dm.load_all_data()  # 从缓存加载，很快！
```

### 强制重新转换

如果数据有更新，需要重新转换：

```python
dm = ExperimentDataManager()
dm.refresh_data()  # 重新扫描和转换
```

### 清理缓存

如果遇到问题，可以清理缓存：

```python
dm = ExperimentDataManager()
dm.clear_cache()
```

或手动删除：
```bash
rmdir /s data\analize\cache
rmdir /s data\analize\processed
```

## 📞 获取帮助

如果遇到问题：

1. 查看日志文件: `data/analize/logs/pipeline_test.log`
2. 查看详细文档: `scripts/PIPELINE_TEST_GUIDE.md`
3. 检查数据管道文档: `data/analize/pipeline/README.md`

## 🎉 成功标志

看到以下输出表示测试成功：

```
================================================================================
  完成
================================================================================

结束时间: 2026-03-05 14:30:00

✓ 所有测试和分析完成！

查看详细报告: data/analize/logs/pipeline_test_report.md
查看日志: data/analize/logs/pipeline_test.log
```

---

**创建时间**: 2026-03-05  
**版本**: v1.0  
**状态**: ✅ 可用
