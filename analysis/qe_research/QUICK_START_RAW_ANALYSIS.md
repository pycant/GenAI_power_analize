# Raw Data Analysis 快速开始指南

## 概述

原始数据分析脚本 `raw_data_analyzer_complete.py` 对实验的 raw.json 文件进行深度分析，生成18个可视化任务的图表和综合报告。

## 快速运行

### Windows 环境

```cmd
# 激活conda环境
conda activate bartscore

# 设置UTF-8编码
set PYTHONUTF8=1

# 运行分析
python analysis/qe_research/scripts/raw_data_analyzer_complete.py
```

### 或使用批处理文件

```cmd
analysis\qe_research\scripts\run_raw_analysis.bat
```

## 输出结果

### 报告位置
- **主报告**: `analysis/qe_research/results/raw_analysis/reports/raw_analysis_report.md`
- **图表目录**: `analysis/qe_research/results/raw_analysis/figures/`
- **数据表**: `analysis/qe_research/results/raw_analysis/tables/`

### 18个可视化任务

#### 一、时间序列分析 (2个)
1. **功耗与资源使用曲线** - 双子图展示GPU功率、温度、利用率、显存随时间变化
2. **多轮对话功耗分解** - 堆叠柱状图显示各轮次耗时占比

#### 二、首token延迟分析 (2个)
3. **TTFT分布** - 直方图和箱线图展示首token延迟分布
4. **TTFT与输入长度关系** - 散点图分析输入长度对TTFT的影响

#### 三、逐token生成延迟分析 (2个)
5. **TPOT分布** - 箱线图对比各模型的每token延迟
6. **生成延迟随时间变化** - 折线图展示token生成速度变化

#### 四、能耗分解与效率 (3个)
7. **每轮对话能耗占比** - 饼图显示各轮次能耗分布
8. **能耗与生成token数关系** - 散点图+回归线分析能耗与输出长度关系
9. **空闲功耗与工作功耗对比** - 对比baseline和工作状态功耗

#### 五、资源使用模式 (3个)
10. **显存使用随时间变化** - 折线图展示显存占用动态
11. **GPU利用率与功耗关系** - 散点图分析利用率与功耗相关性
12. **温度对功耗的影响** - 双Y轴图展示温度与功耗关系

#### 六、事件驱动的微观分析 (2个)
13. **事件时间线** - 散点图展示多轮对话中的事件分布
14. **跨轮次时间对比** - 柱状图对比各模型不同轮次的耗时

#### 七、异常检测与数据质量验证 (2个)
15. **功率波动性分析** - 直方图分析功率标准差分布
16. **事件完整性检查** - 饼图和直方图检查事件数据完整性

#### 八、跨实验对比分析 (2个)
17. **多模型同一任务功耗曲线叠加** - 对比不同模型在相同任务下的功耗曲线
18. **任务类型对功耗波形的影响** - 分析不同任务类型的平均功耗模式

## 数据来源

脚本自动扫描以下模型目录下的 `*_raw.json` 文件：

```
data/
├── deepseek_8b_ol_q4km/
├── gemma_2b_hf_4bit/
├── gemma_2b_hf_8bit/
├── gemma_4b_ol_q4km/
├── phi3_4b_hf_4bit/
├── phi3_4b_hf_8bit/
├── qwen_4b_ol_q4km/
├── qwen_8b_ol_q4km/
├── qwen25_3b_hf_4bit/
├── qwen25_3b_hf_8bit/
├── qwen25_7b_hf_4bit/
└── qwen25_7b_hf_8bit/
```

## 数据结构要求

raw.json 文件应包含以下结构：

```json
{
  "experiment_id": "exp_xxx",
  "config": {
    "model": "Ollama:model-name",
    "task_type": "code|creative|qa|summary"
  },
  "conversation": [
    {
      "turn": 1,
      "prompt": "...",
      "response": "...",
      "start_timestamp": 1234567890.123,
      "end_timestamp": 1234567890.456
    }
  ],
  "monitoring_data": {
    "start_timestamp": 1234567890.0,
    "end_timestamp": 1234567890.5,
    "measurements": {
      "timestamps": [...],
      "cpu_percent": [...],
      "gpu_util": [...],
      "gpu_mem_mb": [...],
      "gpu_power_w": [...],
      "gpu_temp_c": [...],
      "mem_used_mb": [...]
    },
    "events": [
      {
        "timestamp": 1234567890.0,
        "event": "inference_start|first_token|inference_end",
        "metadata": {...}
      }
    ]
  }
}
```

## 配置选项

### 学术配色方案

脚本使用学术期刊推荐的配色方案，对比度高，适合打印：

```python
academic_colors = [
    '#0173B2',  # 蓝色
    '#DE8F05',  # 橙色
    '#029E73',  # 绿色
    '#CC78BC',  # 紫色
    '#CA9161',  # 棕色
    '#ECE133',  # 黄色
    '#56B4E9'   # 浅蓝
]
```

### 中文字体

脚本自动检测并使用 Microsoft YaHei 字体，确保中文正常显示。

## 常见问题

### Q1: 为什么某些任务没有生成图片？

**A**: 检查以下几点：
- 数据文件是否存在且格式正确
- 是否有足够的实验数据（某些任务需要多轮对话数据）
- 查看日志文件 `analysis/qe_research/logs/raw_analysis.log` 了解详情

### Q2: 如何只分析特定模型？

**A**: 修改 `raw_data_analyzer_complete.py` 中的 `model_dirs` 列表：

```python
self.model_dirs = [
    'deepseek_8b_ol_q4km',
    'qwen_8b_ol_q4km',
    # 注释掉不需要的模型
]
```

### Q3: 如何调整图表样式？

**A**: 在 `__init__` 方法中修改：

```python
# 修改图表尺寸
plt.rcParams['figure.figsize'] = (12, 6)

# 修改字体大小
plt.rcParams['font.size'] = 11

# 修改DPI
plt.rcParams['figure.dpi'] = 300
```

### Q4: 如何添加新的分析任务？

**A**: 参考现有任务的实现模式：

1. 在相应的分析方法中添加新的 `_taskXX_xxx()` 方法
2. 从 `self.experiments` 中提取数据
3. 使用 matplotlib 创建可视化
4. 调用 `self._save_fig('XX_task_name.png')` 保存
5. 在 `generate_report()` 中添加对应的报告章节

## 性能优化

### 大数据集处理

如果实验数量很大（>1000），考虑：

1. **采样分析**: 随机选择部分实验
```python
import random
sampled_exps = random.sample(self.experiments, 500)
```

2. **并行处理**: 使用多进程加速
```python
from multiprocessing import Pool
with Pool(4) as p:
    results = p.map(process_experiment, experiments)
```

3. **增量分析**: 只分析新增的实验

## 扩展阅读

- [raw_data_analize.md](docs/raw_data_analize.md) - 详细的任务需求文档
- [RAW_ANALYSIS_FIX_SUMMARY.md](docs/RAW_ANALYSIS_FIX_SUMMARY.md) - 最近的修复记录
- [ACADEMIC_VISUALIZATION_STYLE_GUIDE.md](../../data/analize/visualization/ACADEMIC_VISUALIZATION_STYLE_GUIDE.md) - 可视化风格指南

## 技术支持

遇到问题时：

1. 查看日志文件：`analysis/qe_research/logs/raw_analysis.log`
2. 检查数据格式是否符合要求
3. 确认所有依赖包已安装：`pandas`, `numpy`, `matplotlib`, `seaborn`
4. 参考修复记录文档了解已知问题

## 更新日志

### 2026-03-05
- ✅ 修复TTFT分析任务（任务3-4）未生成图片的问题
- ✅ 修复事件完整性检查（任务16）的标签匹配错误
- ✅ 统一事件字段名称从 `type` 改为 `event`
- ✅ 改进饼图标签动态生成逻辑
- ✅ 所有18个任务成功运行并生成图表

### 2026-03-04
- 🎨 更新配色方案为学术配色
- 📊 优化图表布局和标注
- 📝 完善报告生成逻辑
