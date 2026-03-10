# 导入问题修复说明

## 问题

`pareto_mixed_task.py` 文件中的导入语句有问题：

```python
from pareto_core import (...)  # ❌ 错误：pareto_core 不是一个包
```

## 解决方案

需要修改为：

```python
# 添加 scripts 目录到路径
sys.path.insert(0, str(project_root / 'analysis' / 'qe_research' / 'scripts'))

# 从子模块导入
from pareto_core.shared_functions import (...)
from pareto_core.process_quality_data import load_process_quality_data
```

## 手动修复步骤

1. 打开文件：`analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py`

2. 找到第 27-40 行的导入部分

3. 在第 31 行 `sys.path.insert(0, str(project_root))` 之后添加：
   ```python
   # 添加 scripts 目录到路径，以便导入 pareto_core
   sys.path.insert(0, str(project_root / 'analysis' / 'qe_research' / 'scripts'))
   ```

4. 将第 33-40 行的：
   ```python
   from pareto_core import (
       MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
       identify_pareto_frontier_2d, identify_pareto_frontier_3d,
       calculate_hypervolume, calculate_spacing, find_knee_point,
       plot_pareto_2d, load_energy_speed_data, load_process_quality_data,
       perturbation_analysis, cross_validation_pareto,
       generate_pareto_report, print_analysis_summary
   )
   ```
   
   替换为：
   ```python
   from pareto_core.shared_functions import (
       MODEL_MAPPING, DATA_PATHS, PROJECT_ROOT,
       identify_pareto_frontier_2d, identify_pareto_frontier_3d,
       calculate_hypervolume, calculate_spacing, find_knee_point,
       plot_pareto_2d, load_energy_speed_data,
       perturbation_analysis, cross_validation_pareto,
       generate_pareto_report, print_analysis_summary
   )
   from pareto_core.process_quality_data import load_process_quality_data
   ```

5. 保存文件

6. 测试：
   ```bash
   python analysis/qe_research/scripts/pareto_core/pareto_mixed_task.py
   ```

## 参考

正确的导入方式可以参考 `pareto_analysis_all.py` 文件。
