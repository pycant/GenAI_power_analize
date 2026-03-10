# GPU能耗模型间差异假设检验脚本修复说明

## 问题描述

原 `hypothesis_test_metric_tables.py` 脚本在检验同一任务下不同模型间GPU能耗差异时存在数据加载问题。

## 解决方案

参考 `raw_data_analysis.py` 的正确实现，重新编写了完整的假设检验脚本。

## 核心改进

### 1. 正确的数据加载方式

```python
def load_all_raw_data(self):
    """加载所有raw.json文件"""
    for model_dir in self.model_dirs:
        dir_path = self.data_root / model_dir
        if not dir_path.exists():
            continue
        
        raw_files = list(dir_path.glob('*_raw.json'))
        for raw_file in raw_files:
            with open(raw_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for exp in data:
                exp['model_dir'] = model_dir
                exp['model_name'] = self._extract_model_name(exp['config']['model'])
                self.experiments.append(exp)
```

### 2. 正确的GPU能耗提取

```python
def _extract_gpu_energy(self, exp: Dict) -> float:
    """从实验数据中提取GPU能耗"""
    if 'monitoring_data' not in exp or not exp['monitoring_data']:
        return None
    
    mon = exp['monitoring_data']
    
    # 尝试从summary中获取
    if 'summary' in mon and 'gpu_energy_j' in mon['summary']:
        return mon['summary']['gpu_energy_j']
    
    # 尝试计算
    measurements = mon.get('measurements', {})
    gpu_power = measurements.get('gpu_power_w', [])
    timestamps = measurements.get('timestamps', [])
    
    if len(gpu_power) > 1 and len(timestamps) > 1:
        # 使用梯形法则计算能耗
        time_diffs = np.diff(timestamps)
        avg_power = (np.array(gpu_power[:-1]) + np.array(gpu_power[1:])) / 2
        energy = np.sum(avg_power * time_diffs)
        return energy
    
    return None
```

### 3. 按任务分组的假设检验

```python
def test_energy_across_models_by_task(self):
    """检验同一任务下不同模型间GPU能耗差异"""
    # 按任务和模型组织数据
    task_model_energy = {}
    
    for exp in self.experiments:
        task = self._extract_task_type(exp)
        model = exp['model_name']
        energy = self._extract_gpu_energy(exp)
        
        if energy is not None and energy > 0:
            if task not in task_model_energy:
                task_model_energy[task] = {}
            if model not in task_model_energy[task]:
                task_model_energy[task][model] = []
            task_model_energy[task][model].append(energy)
    
    # 对每个任务进行Kruskal-Wallis检验
    for task in sorted(task_model_energy.keys()):
        energy_by_model = task_model_energy[task]
        models = sorted(energy_by_model.keys())
        energy_groups = [energy_by_model[model] for model in models]
        
        h_stat, p_value = kruskal(*energy_groups)
        
        # 如果显著，进行事后比较
        if p_value < 0.05:
            self._post_hoc_analysis_for_task(task, energy_by_model, models)
```

## 分析流程

1. **数据加载**: 从 `data/` 目录加载所有模型的 `*_raw.json` 文件
2. **数据组织**: 按任务类型和模型名称组织GPU能耗数据
3. **描述性统计**: 计算每个任务-模型组合的均值、标准差、中位数等
4. **假设检验**: 对每个任务使用Kruskal-Wallis H检验
5. **事后比较**: 对显著差异的任务进行Mann-Whitney U检验（Bonferroni校正）
6. **可视化**: 生成箱线图展示能耗分布
7. **报告生成**: 自动生成Markdown格式的分析报告

## 输出文件

### 表格文件 (tables/)
- `energy_model_hypothesis_test_by_task.csv` - 各任务检验结果汇总
- `energy_by_model_<task>_descriptive.csv` - 各任务的描述性统计
- `energy_post_hoc_<task>.csv` - 各任务的事后比较结果

### 图表文件 (figures/)
- `energy_by_model_<task>.png` - 各任务的模型能耗箱线图

### 报告文件 (reports/)
- `GPU_ENERGY_MODEL_HYPOTHESIS_TESTING_REPORT.md` - 完整分析报告

## 使用方法

### 方法1: 直接运行Python脚本
```bash
conda activate bartscore
python analysis/qe_research/scripts/hypothesis_test_metric_tables.py
```

### 方法2: 使用批处理脚本
```bash
analysis/qe_research/scripts/run_hypothesis_test_metric_tables.bat
```

## 统计方法说明

### Kruskal-Wallis H检验
- **用途**: 检验多个独立样本是否来自相同分布
- **优势**: 非参数检验，不要求数据正态分布
- **零假设**: 所有模型的GPU能耗分布相同
- **备择假设**: 至少有一个模型的GPU能耗分布不同

### Mann-Whitney U检验
- **用途**: 两两比较模型间的能耗差异
- **校正**: Bonferroni校正控制多重比较的I类错误率
- **显著性水平**: α = 0.05

## 示例输出

```
任务: code
------------------------------------------------------------

描述性统计:
   任务          模型  样本量      均值     标准差    中位数
0  code  deepseek-r1:8b    10  1234.56   123.45  1200.00
1  code    gemma3:4b      10  1100.23   110.12  1080.00
2  code    qwen3:8b       10  1300.78   130.45  1280.00

Kruskal-Wallis检验: H=15.2345, p=0.0005
  结论: 存在显著差异 (p < 0.05)

  事后比较 (Mann-Whitney U检验):
    deepseek-r1:8b vs gemma3:4b: p=0.0012 (校正后=0.0036) *
    gemma3:4b vs qwen3:8b: p=0.0008 (校正后=0.0024) *
```

## 注意事项

1. 确保 `data/` 目录下有各模型的原始数据文件
2. 原始数据文件命名格式: `<task>_raw.json`
3. 数据必须包含 `monitoring_data` 字段
4. 至少需要2个模型才能进行比较
5. 日志文件保存在 `analysis/qe_research/logs/hypothesis_test_metric_tables.log`

## 依赖包

- pandas
- numpy
- matplotlib
- seaborn
- scipy
- pathlib
- json

## 参考

- 原始数据分析脚本: `raw_data_analysis.py`
- 假设检验功能说明: `analysis/qe_research/假设检验功能说明.md`
- 假设检验指南: `analysis/qe_research/docs/HYPOTHESIS_TESTING_GUIDE.md`
