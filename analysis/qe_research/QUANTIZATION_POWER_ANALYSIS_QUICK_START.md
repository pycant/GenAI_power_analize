# 量化功率分析快速入门

## 概述

量化功率分析工具用于比较同一模型的不同量化版本（4bit vs 8bit）在相同任务下的GPU功率消耗特征。

## 快速运行

### Windows 命令行
```cmd
conda activate bartscore
set PYTHONUTF8=1
python analysis/qe_research/scripts/quantization_power_analysis.py
```

### PowerShell
```powershell
conda activate bartscore
$env:PYTHONUTF8=1
python analysis/qe_research/scripts/quantization_power_analysis.py
```

## 输出结果

### 图表位置
`analysis/qe_research/results/quantization_analysis/figures/`

### 生成的图表类型

#### 1. GPU功率时间序列曲线 (4个)
- `power_curves_google_gemma-2b-it.png`
- `power_curves_microsoft_phi-3-mini-4k-instruct.png`
- `power_curves_qwen_qwen2.5-3b-instruct.png`
- `power_curves_qwen_qwen2.5-7b-instruct.png`

**内容**：
- 按任务类型分组的子图（code, creative, math, qa, reasoning, summary, translation）
- 4bit和8bit量化版本的实时功率曲线
- 平均功率虚线标注
- 学术配色方案，300 DPI高清输出

#### 2. 平均功率对比柱状图 (4个)
- `avg_power_comparison_google_gemma-2b-it.png`
- `avg_power_comparison_microsoft_phi-3-mini-4k-instruct.png`
- `avg_power_comparison_qwen_qwen2.5-3b-instruct.png`
- `avg_power_comparison_qwen_qwen2.5-7b-instruct.png`

**内容**：
- 按任务类型分组的柱状图
- 4bit vs 8bit平均功率对比
- 便于快速识别量化对功率的影响

### 报告位置
`analysis/qe_research/results/quantization_analysis/reports/quantization_power_analysis_report.md`

## 分析的模型

### 有多个量化版本的模型（4个）
1. **google--gemma-2b-it** (4bit, 8bit) - 80个实验
2. **microsoft--phi-3-mini-4k-instruct** (4bit, 8bit) - 80个实验
3. **qwen--qwen2.5-3b-instruct** (4bit, 8bit) - 80个实验
4. **qwen--qwen2.5-7b-instruct** (4bit, 8bit) - 46个实验

### 单一量化版本的模型（4个）
- deepseek-r1:8b (Ollama Q4_K_M)
- gemma3:4b (Ollama Q4_K_M)
- qwen3:4b (Ollama Q4_K_M)
- qwen3:8b (Ollama Q4_K_M)

## 分析维度

### 1. GPU功率时间序列
- 展示推理过程中的实时功率变化
- 识别功率峰值和稳态功率
- 对比不同量化精度的功率模式

### 2. 平均功率对比
- 按任务类型统计平均功率
- 量化不同量化精度的功率差异
- 识别对功率敏感的任务类型

### 3. 功率效率（待补充数据）
- 功率 vs 吞吐量散点图
- 计算能效比（tokens/s/W）
- 需要补充 `tokens_per_second` 数据

## 数据来源

### 数据路径
`data/` 目录下的各模型子目录

### 数据格式
- 原始JSON文件：`*_raw.json`
- 监控数据结构：
  ```python
  {
    "monitoring_data": {
      "start_timestamp": 1234567890.0,
      "measurements": {
        "timestamps": [1.0, 2.0, 3.0, ...],
        "gpu_power_w": [45.2, 46.1, 47.3, ...],
        "gpu_util": [85, 87, 89, ...],
        "gpu_mem_mb": [2048, 2100, 2150, ...]
      }
    }
  }
  ```

## 关键发现

### 量化对功率的影响
- **4bit量化**：通常功率消耗较低，但可能影响推理质量
- **8bit量化**：功率消耗较高，但保持更好的模型精度
- **任务差异**：不同任务类型对量化的敏感度不同

### 模型差异
- 小型模型（2-3B）：量化对功率影响相对较小
- 中型模型（7B）：量化对功率影响更明显
- 任务复杂度：复杂任务（reasoning, code）功率消耗更高

## 技术细节

### 使用的工具
- **数据加载**：`data/analize/pipeline/converters/raw_json_loader.py`
- **可视化**：matplotlib + seaborn
- **配色方案**：学术标准配色（8色）
- **字体**：Microsoft YaHei（中文）

### 图表规格
- **分辨率**：300 DPI（出版质量）
- **格式**：PNG
- **尺寸**：功率曲线 14×(5×任务数) 英寸，柱状图 12×6 英寸

## 常见问题

### Q: 为什么只有4个模型有对比图？
A: 只有这4个模型有多个量化版本（4bit和8bit）的实验数据。Ollama模型只有单一量化版本。

### Q: 功率效率分析为什么没有生成？
A: 当前数据中缺少 `tokens_per_second` 字段，需要补充吞吐量数据。

### Q: 如何添加新的量化版本？
A: 运行新的实验，确保模型名称包含量化标识（如 `:4bit`, `:8bit`），数据会自动被识别和分析。

### Q: 图表中没有数据曲线怎么办？
A: 这个问题已经修复。如果仍然出现，请检查：
1. 数据文件是否包含 `monitoring_data.measurements` 字段
2. `measurements` 是否为字典格式（包含 `timestamps` 和 `gpu_power_w` 键）
3. 查看日志文件 `analysis/qe_research/logs/quantization_power_analysis.log`

## 扩展分析

### 添加新的分析维度
编辑 `analysis/qe_research/scripts/quantization_power_analysis.py`：

```python
def analyze_custom_metric(self):
    """自定义分析方法"""
    # 添加你的分析逻辑
    pass

# 在 run_all_analyses() 中调用
def run_all_analyses(self):
    self.analyze_power_curves_by_task()
    self.analyze_average_power_comparison()
    self.analyze_power_efficiency()
    self.analyze_custom_metric()  # 添加新方法
    self.generate_summary_report()
```

### 修改图表样式
```python
# 修改配色方案
self.academic_colors = ['#0173B2', '#DE8F05', ...]

# 修改字体
plt.rcParams['font.sans-serif'] = ['Your Font']

# 修改DPI
plt.savefig(path, dpi=300)  # 改为其他值
```

## 相关文档

- **修复总结**：`analysis/qe_research/results/quantization_analysis/QUANTIZATION_ANALYSIS_FIX_SUMMARY.md`
- **原始数据分析**：`analysis/qe_research/docs/raw_data_analize.md`
- **质量数据分析**：`analysis/qe_research/docs/quality_data_analize.md`
- **项目总览**：`AGENTS.md`

## 日志和调试

### 日志位置
`analysis/qe_research/logs/quantization_power_analysis.log`

### 调试脚本
`analysis/qe_research/scripts/debug_quantization_data.py`

### 常用调试命令
```python
# 检查数据结构
python analysis/qe_research/scripts/debug_quantization_data.py

# 查看日志
type analysis\qe_research\logs\quantization_power_analysis.log
```

---

**最后更新**：2026-03-06  
**版本**：1.0  
**状态**：✅ 可用
