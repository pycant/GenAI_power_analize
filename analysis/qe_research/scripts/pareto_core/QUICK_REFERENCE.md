# 混合任务分析快速参考

## 快速运行

```bash
# 1. 激活环境
conda activate bartscore

# 2. 设置编码（Windows）
set PYTHONUTF8=1

# 3. 运行分析（从任意目录）
python F:\all_proj\GenAI_power_analize\analysis\qe_research\scripts\pareto_core\pareto_mixed_task.py
```

## 权重格式示例

### ✅ 格式1: 标准小数（推荐）
```python
weights = {
    'code': 0.30,
    'math': 0.25,
    'qa': 0.20,
    'reasoning': 0.15,
    'creative': 0.05,
    'summary': 0.03,
    'translation': 0.02
}
# 和 = 1.00，无需调整
```

### ✅ 格式2: 整数（自动归一化）
```python
weights = {
    'code': 30,
    'math': 25,
    'qa': 20,
    'reasoning': 15,
    'creative': 5,
    'summary': 3,
    'translation': 2
}
# 和 = 100，自动归一化为 0.30, 0.25, 0.20, ...
```

### ✅ 格式3: 任意比例（自动归一化）
```python
weights = {
    'code': 3,
    'math': 2,
    'qa': 1,
    'reasoning': 1
}
# 和 = 7，自动归一化为 3/7, 2/7, 1/7, 1/7
```

## 自定义配置

```python
from pathlib import Path
from pareto_core.pareto_mixed_task import WEIGHT_CONFIGS, run_mixed_task_analysis

# 添加自定义配置
WEIGHT_CONFIGS['my_config'] = {
    'name': '我的配置',
    'description': '自定义权重方案',
    'weights': {
        'code': 40,      # 使用整数，会自动归一化
        'math': 30,
        'qa': 20,
        'reasoning': 10
    }
}

# 运行分析
output_dir = Path('analysis/qe_research/results/mixed_task_analysis/task_01')
run_mixed_task_analysis('my_config', output_dir)
```

## 输出位置

```
analysis/qe_research/results/mixed_task_analysis/task_01/
├── objective/                           # 客观任务为主
├── subjective/                          # 主观任务为主
├── balanced/                            # 均衡配置
└── my_config/                           # 自定义配置
```

## 测试权重归一化

```bash
python analysis/qe_research/scripts/pareto_core/test_weight_normalization.py
```

## 常见问题

### Q: 权重和不为1怎么办？
**A**: 脚本会自动归一化，无需手动调整。

### Q: 可以使用整数权重吗？
**A**: 可以，脚本会自动转换为小数并归一化。

### Q: 从哪个目录运行脚本？
**A**: 任意目录都可以，脚本会自动切换到项目根目录。

### Q: 如何查看归一化结果？
**A**: 运行时会在控制台输出详细的权重调整信息。

## 预配置方案

### Objective（客观任务为主）
- 客观任务: 90% (code 30%, math 25%, qa 20%, reasoning 15%)
- 主观任务: 10% (creative 5%, summary 3%, translation 2%)
- 适用: 技术应用、代码助手

### Subjective（主观任务为主）
- 主观任务: 80% (creative 35%, summary 25%, translation 20%)
- 客观任务: 20% (code 10%, math 5%, qa 3%, reasoning 2%)
- 适用: 内容创作、翻译服务

### Balanced（均衡配置）
- 相对均衡: code 15%, math 15%, qa 15%, creative 15%, summary 15%, translation 13%, reasoning 12%
- 适用: 通用评估、综合应用

## 关键文件

- 📜 主脚本: `pareto_mixed_task.py`
- 🧪 测试脚本: `test_weight_normalization.py`
- 📖 详细说明: `MIXED_TASK_UPDATE.md`
- 📊 方法文档: `../results/mixed_task_analysis/method.md`
- 🚀 快速开始: `../results/mixed_task_analysis/QUICK_START.md`

## 工作目录

脚本会自动设置工作目录为:
```
F:\all_proj\GenAI_power_analize
```

验证:
```python
import os
print(f"工作目录: {os.getcwd()}")
```

---

**版本**: 1.1  
**更新**: 2026-03-08  
**状态**: ✅ 可用
