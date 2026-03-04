# 实验配置就绪报告

## 完成时间
2026-03-03

## 状态
✅ 所有实验配置已生成并就绪

---

## 配置概览

已为 4 个 Ollama 模型生成完整的实验配置，每个模型包含 40 个平衡任务。

### 生成的配置目录

```
data/
├── experiments_gemma3/
│   └── test_cases.json          # Gemma3 4B (40 tasks)
├── experiments_qwen3_4b/
│   └── test_cases.json          # Qwen3 4B (40 tasks)
├── experiments_qwen3_8b/
│   └── test_cases.json          # Qwen3 8B (40 tasks)
└── experiments_deepseek_r1_8b/
    └── test_cases.json          # DeepSeek-R1 8B (40 tasks)
```

---

## 模型对比

| 模型 | 参数量 | 量化 | 显存 | 配置路径 |
|------|--------|------|------|----------|
| **gemma3:4b** | 4B | Q4_K_M | ~3.3GB | `data/experiments_gemma3/` |
| **qwen3:4b** | 4B | Q4_K_M | ~2.5GB | `data/experiments_qwen3_4b/` |
| **qwen3:8b** | 8B | Q4_K_M | ~5.2GB | `data/experiments_qwen3_8b/` |
| **deepseek-r1:8b** | 8B | Q4_K_M | ~5.2GB | `data/experiments_deepseek_r1_8b/` |

---

## 任务配置

### 任务类型分布（每个模型）

所有模型使用相同的任务选择（随机种子 42）：

| 任务类型 | 数量 | 占比 |
|---------|------|------|
| code | 5 | 12.5% |
| creative | 5 | 12.5% |
| math | 5 | 12.5% |
| multi_turn | 5 | 12.5% |
| qa | 5 | 12.5% |
| reasoning | 5 | 12.5% |
| summary | 5 | 12.5% |
| translation | 5 | 12.5% |
| **总计** | **40** | **100%** |

### 语言分布

| 语言类型 | 数量 | 占比 |
|---------|------|------|
| 单语言 (monolingual) | 30 | 75% |
| 跨语言 (cross-lingual) | 5 | 12.5% |
| 代码 (code) | 5 | 12.5% |

**具体语言**:
- 中文 (zh): 20 个任务
- 英文 (en): 15 个任务
- 英文 (eng): 5 个任务（翻译）
- 中文简体 (zho_Hans): 5 个任务（翻译）

---

## 优化的 max_tokens

所有配置使用优化的 max_tokens 值，根据任务类型和难度动态调整：

### 基础值（Medium 难度）

| 任务类型 | max_tokens | 说明 |
|---------|-----------|------|
| code | 800 | 完整代码实现 |
| creative | 500 | 创意写作空间 |
| math | 400 | 推理步骤展示 |
| multi_turn | 300 | 每轮对话 |
| qa | 200 | 详细回答 |
| reasoning | 400 | 逻辑推理过程 |
| summary | 250 | 全面摘要 |
| translation | 300 | 复杂翻译 |

### 难度调整

- **Easy**: 基础值 × 0.8
- **Medium**: 基础值 × 1.0
- **Hard**: 基础值 × 1.5

---

## 运行方式

### 方式 1: 批量运行（推荐）

```bash
scripts\run_all_experiments.bat
```

**特点**:
- 自动依次运行 4 个模型
- 失败时自动停止
- 显示进度和状态
- 预计总时间: 4-6 小时

### 方式 2: 单独运行

```bash
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

## 关键改进

### 1. 跳过 BARTScore 评估

使用 `--skip-bartscore` 参数：
- ✅ 避免 HuggingFace 网络超时
- ✅ 加快实验速度
- ✅ 专注于效率指标收集
- ❌ 暂不收集质量评分（可后续补充）

### 2. 优化的 max_tokens

- 代码任务: 640-1200 tokens（之前 500）
- 创意任务: 400-750 tokens（之前 100-300）
- 推理任务: 320-600 tokens（之前 150-400）
- 其他任务: 相应提升

### 3. 统一的任务选择

- 所有模型使用相同的随机种子 (42)
- 确保选择相同的 40 个任务
- 结果可直接对比

---

## 预期输出

每个模型实验完成后生成：

```
data/experiments_<model>/
├── test_cases.json                                    # 配置文件
├── experiment_results_YYYYMMDD_HHMMSS_raw.json       # 原始结果
└── experiment_results_YYYYMMDD_HHMMSS_summary.json   # 汇总结果
```

### 收集的指标

**效率指标**:
- ✅ 吞吐量 (tokens/s)
- ✅ 延迟 (秒)
- ✅ GPU 能耗 (焦耳)
- ✅ GPU 显存使用 (MB)
- ✅ CPU 使用率 (%)
- ✅ 内存使用 (MB)

**内容指标**:
- ✅ 生成文本完整内容
- ✅ 生成文本长度
- ✅ 对话历史（多轮任务）

**质量指标**:
- ❌ BARTScore（已跳过）
- ℹ️ 可后续使用离线模式补充

---

## 时间估算

### 单个模型

| 阶段 | 时间 |
|------|------|
| 空闲基线测量 | 10s × 40 = 6.7 min |
| 任务执行 | 30-60s × 40 = 20-40 min |
| 数据保存 | 2-5 min |
| **总计** | **30-50 分钟** |

### 全部模型

- **4 个模型**: 2-3.5 小时
- **包含切换时间**: 2.5-4 小时
- **保守估计**: 4-6 小时

---

## 实验前检查清单

### 系统准备

- [ ] Ollama 服务运行中
  ```bash
  ollama list
  ```

- [ ] GPU 显存已清理
  ```bash
  python scripts/clear_gpu_memory.py
  ```

- [ ] Conda 环境已激活
  ```bash
  conda activate bartscore
  ```

- [ ] 磁盘空间充足（至少 500 MB）

### 环境检查

- [ ] 关闭其他 GPU 应用
- [ ] 笔记本电脑已插电
- [ ] 系统保持唤醒状态
- [ ] 网络连接稳定（虽然跳过 BARTScore）

---

## 实验监控

### 终端输出

实验运行时会显示：
```
[1/40] 任务: code_011 (code)
  提示: def multiply(a, b):...
  [OK] 生成完成 (耗时: 25.3秒)
  吞吐量: 15.2 tokens/s
  GPU 能耗: 450.2 J
```

### GPU 监控

在另一个终端：
```bash
nvidia-smi -l 1
```

---

## 故障处理

### Ollama 连接失败

```bash
# 检查状态
curl http://localhost:11434/api/tags

# 重启服务
taskkill /F /IM ollama.exe
ollama serve
```

### 显存不足

```bash
python scripts/clear_gpu_memory.py
```

### 实验中断

单独运行剩余模型即可，已完成的结果会保留。

---

## 下一步

### 1. 运行实验

```bash
# 批量运行
scripts\run_all_experiments.bat

# 或单独运行
python experiments/experiment_runner.py \
  --config data/experiments_gemma3/test_cases.json \
  --output-dir data/experiments_gemma3 \
  --skip-bartscore
```

### 2. 验证结果

```bash
# 检查生成的文件
dir data\experiments_*\experiment_results_*.json
```

### 3. 数据分析

实验完成后：
- 使用分析脚本处理结果
- 生成对比图表
- 撰写分析报告

### 4. 质量评估（可选）

网络稳定后补充 BARTScore 评估：
```bash
# 使用离线模式
set HF_HUB_OFFLINE=1
set TRANSFORMERS_OFFLINE=1
python experiments/experiment_runner.py \
  --config data/experiments_gemma3/test_cases.json \
  --output-dir data/experiments_gemma3
```

---

## 相关文档

- [批量实验指南](EXPERIMENTS_BATCH_GUIDE.md) - 详细的批量运行指南
- [实验运行器指南](EXPERIMENT_RUNNER_GUIDE.md) - 运行器使用说明
- [配置参数参考](CONFIG_PARAMETERS_REFERENCE.md) - 参数详解
- [语言标注指南](LANGUAGE_ANNOTATION_GUIDE.md) - 语言标注说明

---

## 工具脚本

| 脚本 | 功能 |
|------|------|
| `scripts/run_all_experiments.bat` | 批量运行所有实验 |
| `scripts/clear_gpu_memory.py` | 清理 GPU 显存 |
| `scripts/create_experiment_config.py` | 生成实验配置 |

---

## 配置一致性验证

所有配置文件已验证：
- ✅ 使用相同的随机种子 (42)
- ✅ 选择相同的 40 个任务
- ✅ 任务顺序一致
- ✅ 参数设置合理
- ✅ max_tokens 已优化
- ✅ 语言分布平衡

---

**创建日期**: 2026-03-03  
**状态**: ✅ 就绪  
**下一步**: 运行实验

**命令**:
```bash
scripts\run_all_experiments.bat
```
