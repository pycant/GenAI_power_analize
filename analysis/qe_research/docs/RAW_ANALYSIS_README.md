# 原始数据(raw.json)深度分析说明

## 概述

本分析系统对实验的原始监控数据(raw.json)进行深度分析，实现了18个可视化任务，揭示汇总数据无法呈现的动态行为和微观特征。

## 分析任务列表

### 一、时间序列分析 (2个任务)
1. **功耗与资源使用曲线**: GPU功率、利用率、显存、温度随时间变化，叠加事件标记
2. **多轮对话功耗分解**: 每轮对话的能耗和耗时堆叠图

### 二、首token延迟分析 (2个任务)
3. **TTFT分布**: 直方图和箱线图展示首token延迟分布
4. **TTFT与输入长度关系**: 散点图分析输入长度对TTFT的影响

### 三、逐token生成延迟分析 (2个任务)
5. **TPOT分布**: 箱线图对比不同模型的每token延迟
6. **生成延迟随时间变化**: 观察延迟是否随生成长度增加

### 四、能耗分解与效率 (3个任务)
7. **每轮对话能耗占比**: 饼图显示各轮能耗比例
8. **能耗与生成token数关系**: 散点图+回归线验证线性关系
9. **空闲功耗与工作功耗对比**: 叠加baseline展示增量功耗

### 五、资源使用模式 (3个任务)
10. **显存使用随时间变化**: 观察显存分配模式
11. **GPU利用率与功耗关系**: 散点图分析相关性
12. **温度对功耗的影响**: 双Y轴图观察温度-功耗关系

### 六、事件驱动的微观分析 (2个任务)
13. **事件时间线**: 甘特图展示各阶段持续时间
14. **跨轮次时间对比**: 分组柱状图对比不同轮次的时间

### 七、异常检测与数据质量验证 (2个任务)
15. **功率波动性分析**: 直方图识别波动过大的异常实验
16. **事件完整性检查**: 统计关键事件缺失情况

### 八、跨实验对比分析 (2个任务)
17. **多模型同一任务功耗曲线叠加**: 对齐时间轴对比不同模型
18. **任务类型对功耗波形的影响**: 归一化时间轴展示平均功率曲线

## 快速开始

### 方法1: 使用批处理脚本 (推荐)

```bash
# 双击运行
analysis/qe_research/scripts/run_raw_analysis.bat
```

### 方法2: 命令行运行

```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行分析
python analysis/qe_research/scripts/raw_data_analyzer_complete.py
```

## 输出结果

### 报告
- `analysis/qe_research/results/raw_analysis/reports/raw_analysis_report.md`
  - 完整的分析报告，包含所有18个任务的可视化和说明

### 图表 (18张)
- `analysis/qe_research/results/raw_analysis/figures/`
  - `01_power_resource_curves.png` - 功耗与资源使用曲线
  - `02_multi_turn_energy.png` - 多轮对话功耗分解
  - `03_ttft_distribution.png` - TTFT分布
  - `04_ttft_vs_input_length.png` - TTFT与输入长度关系
  - `05_tpot_distribution.png` - TPOT分布
  - `06_latency_over_time.png` - 生成延迟随时间变化
  - `07_energy_per_turn.png` - 每轮对话能耗占比
  - `08_energy_vs_tokens.png` - 能耗与生成token数关系
  - `09_idle_vs_work_power.png` - 空闲功耗与工作功耗对比
  - `10_memory_over_time.png` - 显存使用随时间变化
  - `11_util_vs_power.png` - GPU利用率与功耗关系
  - `12_temp_vs_power.png` - 温度对功耗的影响
  - `13_event_timeline.png` - 事件时间线
  - `14_cross_turn_comparison.png` - 跨轮次时间对比
  - `15_power_volatility.png` - 功率波动性分析
  - `16_event_completeness.png` - 事件完整性检查
  - `17_multi_model_power_curves.png` - 多模型同一任务功耗曲线叠加
  - `18_task_type_power_patterns.png` - 任务类型对功耗波形的影响

### 数据表
- `analysis/qe_research/results/raw_analysis/tables/`
  - `anomalous_experiments.csv` - 异常实验列表
  - `incomplete_experiments.csv` - 不完整实验列表

## 数据要求

### 输入数据
- 位置: `data/{model_dir}/*_raw.json`
- 格式: JSON文件，包含以下结构:
  ```json
  {
    "experiment_id": "...",
    "config": {...},
    "monitoring_data": {
      "measurements": {
        "timestamps": [...],
        "gpu_power_w": [...],
        "gpu_util": [...],
        "gpu_mem_mb": [...],
        "gpu_temp_c": [...]
      },
      "events": [
        {"type": "inference_start", "timestamp": ...},
        {"type": "first_token", "timestamp": ...},
        {"type": "inference_end", "timestamp": ...}
      ]
    },
    "conversation": [...]
  }
  ```

### 支持的模型目录
- deepseek_8b_ol_q4km
- gemma_2b_hf_4bit, gemma_2b_hf_8bit
- gemma_4b_ol_q4km
- phi3_4b_hf_4bit, phi3_4b_hf_8bit
- qwen_4b_ol_q4km, qwen_8b_ol_q4km
- qwen25_3b_hf_4bit, qwen25_3b_hf_8bit
- qwen25_7b_hf_4bit, qwen25_7b_hf_8bit

## 技术细节

### 依赖包
```bash
pip install pandas numpy matplotlib seaborn
```

### 可视化配置
- 色系: Viridis (可在代码中修改)
- 字体: Microsoft YaHei (中文支持)
- DPI: 300 (高清图表)
- 格式: PNG

### 性能
- 处理时间: 约2-5分钟 (取决于实验数量)
- 内存需求: 约1-2GB
- 输出大小: 约10-20MB (图表+报告)

## 关键洞察

通过这18个可视化任务，可以获得以下洞察:

1. **Prefill vs Decode阶段特征**: 观察计算密集vs访存密集的功耗差异
2. **首token延迟瓶颈**: 识别影响用户体验的关键因素
3. **生成稳定性**: 检测长文本生成时的性能衰减
4. **能效优化机会**: 发现空闲功耗和峰值功耗的优化空间
5. **资源利用模式**: 理解显存分配和GPU利用率特征
6. **温度管理**: 评估散热对性能的影响
7. **数据质量**: 识别异常实验和数据缺失
8. **模型对比**: 直观比较不同模型和任务的能效特征

## 故障排除

### 问题1: 未找到数据
**解决**: 确认data目录下存在*_raw.json文件

### 问题2: 图表中文乱码
**解决**: 确认系统已安装Microsoft YaHei字体

### 问题3: 内存不足
**解决**: 减少同时处理的实验数量，或增加系统内存

### 问题4: 某些图表未生成
**原因**: 数据不完整或不满足特定任务的要求
**解决**: 查看日志了解具体原因

## 扩展开发

### 添加新的分析任务
1. 在`RawDataAnalyzer`类中添加新方法
2. 在`run_all_analyses()`中调用
3. 更新报告生成逻辑

### 自定义可视化样式
修改`_setup_plotting_style()`方法中的配置

### 导出其他格式
修改`_save_fig()`方法支持PDF、SVG等格式

## 参考文档

- [原始数据分析需求](raw_data_analize.md)
- [研究框架](../README.md)
- [数据管道文档](../../../data/analize/pipeline/README.md)

---

**创建时间**: 2026-03-05  
**版本**: v1.0  
**状态**: ✅ 完成
