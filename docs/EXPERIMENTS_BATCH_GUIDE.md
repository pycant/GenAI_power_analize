# 批量实验执行指南

## 实验配置概览

已为 4 个 Ollama 模型生成完整的实验配置，每个模型 40 个平衡任务。

### 模型列表

| 模型 | 参数量 | 量化 | 显存占用 | 配置目录 |
|------|--------|------|----------|----------|
| gemma3:4b | 4B | Q4_K_M | ~3.3 GB | `data/experiments_gemma3/` |
| qwen3:4b | 4B | Q4_K_M | ~2.5 GB | `data/experiments_qwen3_4b/` |
| qwen3:8b | 8B | Q4_K_M | ~5.2 GB | `data/experiments_qwen3_8b/` |
| deepseek-r1:8b | 8B | Q4_K_M | ~5.2 GB | `data/experiments_deepseek_r1_8b/` |

### 任务分布

每个模型的 40 个任务包含：

| 任务类型 | 数量 | 说明 |
|---------|------|------|
| code | 5 | 代码生成（Python） |
| creative | 5 | 创意写作 |
| math | 5 | 数学推理 |
| multi_turn | 5 | 多轮对话 |
| qa | 5 | 问答任务 |
| reasoning | 5 | 逻辑推理 |
| summary | 5 | 文本摘要 |
| translation | 5 | 跨语言翻译 |

**语言分布**:
- 中文任务: 20 个
- 英文任务: 20 个
- 跨语言任务: 5 个（翻译）
- 代码任务: 5 个

### max_tokens 优化

所有配置已使用优化的 max_tokens 值：

| 任务类型 | Easy | Medium | Hard |
|---------|------|--------|------|
| code | 640 | 800 | 1200 |
| creative | 400 | 500 | 750 |
| math | 320 | 400 | 600 |
| multi_turn | 240 | 300 | 450 |
| qa | 160 | 200 | 300 |
| reasoning | 320 | 400 | 600 |
| summary | 200 | 250 | 375 |
| translation | 240 | 300 | 450 |

---

## 运行方式

### 方式 1: 批量运行（推荐）

使用批处理脚本自动运行所有模型：

```bash
scripts\run_all_experiments.bat
```

**特点**:
- 自动依次运行 4 个模型
- 失败时自动停止
- 显示进度和状态
- 预计总时间: 4-6 小时

### 方式 2: 单独运行

分别运行每个模型的实验：

```bash
# 激活环境
conda activate bartscore

# Gemma3 4B
python experiments/experiment_runner.py \
  --config data/experiments_gemma3/test_cases.json \
  --output-dir data/experiments_gemma3 \
  --skip-bartscore

# Qwen3 4B
python experiments/experiment_runner.py \
  --config data/experiments_qwen3_4b/test_cases.json \
  --output-dir data/experiments_qwen3_4b \
  --skip-bartscore

# Qwen3 8B
python experiments/experiment_runner.py \
  --config data/experiments_qwen3_8b/test_cases.json \
  --output-dir data/experiments_qwen3_8b \
  --skip-bartscore

# DeepSeek-R1 8B
python experiments/experiment_runner.py \
  --config data/experiments_deepseek_r1_8b/test_cases.json \
  --output-dir data/experiments_deepseek_r1_8b \
  --skip-bartscore
```

---

## 实验参数说明

### --skip-bartscore

**作用**: 跳过 BARTScore 质量评估

**原因**:
- 避免 HuggingFace 网络超时
- 加快实验速度
- 专注于效率指标收集

**收集的指标**:
- ✅ 吞吐量 (tokens/s)
- ✅ 延迟 (秒)
- ✅ GPU 能耗 (焦耳)
- ✅ GPU 显存使用
- ✅ CPU/内存使用
- ✅ 生成文本内容
- ❌ BARTScore 质量评分

**后续补充**: 可以稍后使用离线模式单独运行 BARTScore 评估

---

## 时间估算

### 单个模型

基于之前的测试数据：

| 任务类型 | 平均时间 | 任务数 | 小计 |
|---------|---------|--------|------|
| code | 30-60s | 5 | 2.5-5 min |
| creative | 20-40s | 5 | 1.7-3.3 min |
| math | 15-30s | 5 | 1.3-2.5 min |
| multi_turn | 60-120s | 5 | 5-10 min |
| qa | 15-25s | 5 | 1.3-2.1 min |
| reasoning | 20-40s | 5 | 1.7-3.3 min |
| summary | 15-30s | 5 | 1.3-2.5 min |
| translation | 15-30s | 5 | 1.3-2.5 min |

**单模型总计**: 约 60-90 分钟

### 全部模型

- **4 个模型**: 4-6 小时
- **包含空闲基线**: 每个任务额外 10 秒
- **模型切换**: 约 5-10 分钟

---

## 输出结果

每个模型的实验完成后，将在对应目录生成：

```
data/experiments_<model>/
├── test_cases.json                          # 实验配置
├── experiment_results_YYYYMMDD_HHMMSS_raw.json    # 原始结果
└── experiment_results_YYYYMMDD_HHMMSS_summary.json # 汇总结果
```

### 原始结果 (raw.json)

包含完整的实验数据：
- 每个任务的详细配置
- 完整的对话历史
- 逐轮的监控数据
- 时间序列资源使用
- 事件标记

### 汇总结果 (summary.json)

包含聚合的性能指标：
- 平均吞吐量
- 平均延迟
- 总能耗
- 资源使用峰值
- 派生指标

---

## 实验监控

### 实时监控

实验运行时，终端会显示：
- 当前任务进度 (X/40)
- 任务类型和 ID
- 生成状态
- 资源使用情况

### GPU 监控

在另一个终端运行：

```bash
# 实时查看 GPU 状态
nvidia-smi -l 1

# 或使用 watch（如果安装）
watch -n 1 nvidia-smi
```

### 系统资源

```bash
# 查看进程资源使用
Get-Process python | Select-Object CPU,WorkingSet,Id
```

---

## 注意事项

### 实验前

1. **确保 Ollama 运行**
   ```bash
   ollama list  # 验证模型可用
   ```

2. **清理 GPU 显存**
   ```bash
   python scripts/clear_gpu_memory.py
   ```

3. **检查磁盘空间**
   - 每个实验约 50-100 MB
   - 4 个模型约 200-400 MB

4. **关闭其他 GPU 应用**
   - 游戏、视频编辑等
   - 浏览器硬件加速

### 实验中

1. **保持系统空闲**
   - 避免运行其他密集任务
   - 不要进入睡眠/休眠

2. **保持电源连接**
   - 笔记本电脑插电运行
   - 避免性能降低

3. **监控温度**
   - GPU 温度 < 85°C
   - 必要时调整风扇

4. **中断恢复**
   - 如果中断，可以单独运行剩余模型
   - 已完成的结果会保留

### 实验后

1. **验证结果**
   ```bash
   # 检查生成的文件
   dir data\experiments_*\experiment_results_*.json
   ```

2. **备份数据**
   - 复制到安全位置
   - 避免意外覆盖

3. **清理显存**
   ```bash
   python scripts/clear_gpu_memory.py
   ```

---

## 故障排除

### Ollama 连接失败

```bash
# 检查 Ollama 状态
curl http://localhost:11434/api/tags

# 重启 Ollama
taskkill /F /IM ollama.exe
ollama serve
```

### 显存不足

```bash
# 清理显存
python scripts/clear_gpu_memory.py

# 或停止 Ollama 重新加载
python scripts/clear_gpu_memory.py --ollama-only
python scripts/clear_gpu_memory.py --start-ollama
```

### 实验中断

单独运行剩余的模型：

```bash
# 例如，如果在 Qwen3 8B 时中断
python experiments/experiment_runner.py \
  --config data/experiments_qwen3_8b/test_cases.json \
  --output-dir data/experiments_qwen3_8b \
  --skip-bartscore
```

### 结果文件损坏

检查 JSON 格式：

```bash
python -m json.tool data/experiments_gemma3/experiment_results_*.json
```

---

## 下一步

实验完成后：

1. **数据分析**
   - 使用 `scripts/analyze_experiments.py` 分析结果
   - 生成对比图表

2. **质量评估**（可选）
   - 在网络稳定时补充 BARTScore 评估
   - 或使用离线模式

3. **报告生成**
   - 自动生成 Markdown 报告
   - 包含图表和统计数据

4. **模型对比**
   - 横向对比 4 个模型
   - 分析质效比差异
   - 识别最优模型

---

## 配置文件详情

所有配置文件使用相同的随机种子 (42)，确保：
- 选择相同的 40 个任务
- 任务顺序一致
- 结果可对比

### 配置一致性

| 参数 | 值 | 说明 |
|------|-----|------|
| 任务数量 | 40 | 从 80 个中选择 |
| 随机种子 | 42 | 可复现 |
| 任务分布 | 平衡 | 每类型 5 个 |
| 语言分布 | 平衡 | 中英各 20 个 |
| max_tokens | 优化 | 按任务类型和难度 |
| temperature | 任务特定 | 0.0-0.9 |
| repeat | 任务特定 | 1-5 次 |

---

## 参考文档

- [实验运行器指南](EXPERIMENT_RUNNER_GUIDE.md)
- [配置参数参考](CONFIG_PARAMETERS_REFERENCE.md)
- [语言标注指南](LANGUAGE_ANNOTATION_GUIDE.md)
- [实验设置完成报告](EXPERIMENT_SETUP_COMPLETE.md)

---

**创建日期**: 2026-03-03  
**状态**: ✅ 就绪  
**下一步**: 运行批量实验
