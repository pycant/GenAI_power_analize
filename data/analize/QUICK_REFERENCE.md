# 快速参考卡片

## 📂 数据文件位置

```
data/analize/pre_data/
├── responses_raw.csv              # 原始数据（446条，674KB）
├── responses_summary.csv          # 统计摘要
└── comparison_matrices/           # 对比矩阵（8任务×8文件）
    ├── overview.csv
    ├── code/code_responses.csv    # 代码生成回答对比
    ├── creative/...
    └── ...
```

## 🔧 常用命令

### 重新生成数据
```bash
conda activate bartscore
set PYTHONUTF8=1
python data/analize/scripts/extract_responses.py
python data/analize/scripts/create_comparison_matrix.py
```

### 验证数据
```bash
python data/analize/scripts/verify_data.py
```

### 查看样本
```bash
python data/analize/scripts/view_samples.py
```

## 💻 代码示例

### 读取原始数据
```python
import pandas as pd
df = pd.read_csv('data/analize/pre_data/responses_raw.csv', 
                 encoding='utf-8-sig')
```

### 读取对比矩阵
```python
# 回答对比
responses = pd.read_csv(
    'data/analize/pre_data/comparison_matrices/code/code_responses.csv',
    encoding='utf-8-sig', index_col=0)

# 能耗对比
energy = pd.read_csv(
    'data/analize/pre_data/comparison_matrices/code/code_gpu_energy_j.csv',
    encoding='utf-8-sig', index_col=0)
```

## 📊 数据统计

- **总样本**: 446 条
- **模型数**: 12 个
- **任务类型**: 8 种
- **质量评分**: 85/100

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| `pre_data/README.md` | 数据说明 |
| `comparison_matrices/README.md` | 对比矩阵说明 |
| `EXTRACTION_SUMMARY.md` | 提取工作总结 |
| `DATA_PREPARATION_COMPLETE.md` | 完成报告 |
| `scripts/analysis_design.md` | 分析设计 |
| `scripts/quality_evaluation_system.md` | 质量评估设计 |

## 🎯 下一步

1. 实现质量评估（`evaluate_all_models.py`）
2. 数据预处理（合并质量和性能数据）
3. 统计分析和可视化

---
**更新**: 2026-03-04 | **状态**: 数据准备完成 ✅
