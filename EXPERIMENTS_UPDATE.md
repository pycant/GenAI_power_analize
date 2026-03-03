# 实验框架更新说明

本文档说明对 `experiments/` 目录的更新，现已将 Hugging Face 模型支持整合到主运行器中。

## 📋 更新概述

实验框架现已支持：

- ✅ Ollama 和 Hugging Face 模型的统一调用
- ✅ 4bit/8bit 量化支持
- ✅ 灵活的模型规格配置
- ✅ 向后兼容原有 Ollama 实验
- ✅ 完整的资源监控和质量评估

## 🔄 重要变更

### 合并统一运行器

`unified_runner.py` 的功能已完全整合到 `experiment_runner.py` 中：

- ✅ 单一入口点，简化使用
- ✅ 保持所有功能不变
- ✅ 向后兼容原有配置
- ✅ 删除了冗余文件

### 已删除的文件

```
experiments/
├── unified_runner.py              # 已删除：功能已合并
├── test_cases_mixed.json          # 已删除：使用 data/test/test_cases.json
├── UNIFIED_RUNNER_GUIDE.md        # 已删除：内容已整合到其他文档
└── test_unified_system.py         # 已删除：使用统一的测试脚本
```

## 🗂️ 当前文件结构

```
experiments/
├── experiment_runner.py           # 统一实验运行器（支持 Ollama + HF）
├── config.py                      # 实验配置（包含 HF 模型配置）
├── monitor.py                     # 资源监控
├── quality.py                     # 质量评估（BARTScore）
└── experiment_runner.py.backup    # 原版本备份
```

## 🎯 模型规格格式

### Ollama 模型

```
格式: "model_name" 或 "ollama:model_name"

示例:
- "qwen3:4b"
- "ollama:deepseek-r1:8b"
- "gemma3:4b"
```

### Hugging Face 模型

```
格式: "hf:model_path" 或 "hf:model_path:quantize"

示例:
- "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit"
- "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:8bit"
- "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct"  # 默认fp16
```

### 量化选项

- `4bit`: 4位量化，最省显存（推荐 8GB 显存）
- `8bit`: 8位量化，平衡性能和显存
- 不指定: 使用 fp16（需要更多显存）

## 🚀 使用方法

### 方法1: 运行示例实验

```bash
# 激活环境
conda activate bartscore

# 运行 Ollama 模型示例
python experiments/experiment_runner.py --config data/test/test_cases_ollama.json --output-dir data/test

# 运行混合模型示例
python experiments/experiment_runner.py --config data/test/test_cases.json --output-dir data/test
```

### 方法2: 使用配置文件

```bash
# 使用自定义配置
python experiments/experiment_runner.py --config your_config.json

# 指定输出目录
python experiments/experiment_runner.py --config your_config.json --output-dir results/exp_2
```

### 方法3: 创建自定义配置

创建 `my_experiment.json`:

```json
[
  {
    "model": "qwen3:4b",
    "prompt": "你的提示词",
    "task_type": "qa",
    "max_tokens": 200,
    "temperature": 0.7
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
    "prompt": "你的提示词",
    "task_type": "qa",
    "max_tokens": 200,
    "temperature": 0.7
  }
]
```

运行:

```bash
python experiments/experiment_runner.py --config my_experiment.json
```

## 📊 实验结果格式

结果保存为 JSON 格式，包含：

```json
{
  "model_spec": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
  "model_info": {
    "type": "huggingface",
    "path": "...",
    "quantize": "4bit",
    "display_name": "HF:Qwen2.5-3B-Instruct:4bit"
  },
  "performance": {
    "total_time_seconds": 2.5,
    "token_count": 150,
    "throughput_tokens_per_sec": 60.0,
    "latency_per_token_ms": 16.67
  },
  "resources": {
    "gpu_energy_j": 188.75,
    "gpu_util_avg": 85.3,
    "gpu_mem_peak_mb": 6144.0,
    ...
  },
  "quality": {
    "bartscore": -2.45,
    "has_reference": true
  }
}
```

## 🔄 向后兼容性

### 原有 Ollama 实验

原有的配置文件完全兼容，无需修改：

```bash
# 继续使用原有配置
python experiments/experiment_runner.py --config test_cases.json
```

### 迁移说明

如果你之前使用过 `unified_runner.py`，现在只需：

1. 将所有 `unified_runner.py` 替换为 `experiment_runner.py`
2. 配置文件格式保持不变
3. 所有功能保持一致

**原命令**:

```bash
python experiments/unified_runner.py --config test_cases.json
```

**新命令**:

```bash
python experiments/experiment_runner.py --config test_cases.json
```

## 💡 使用场景

### 场景1: 对比 Ollama 和 HF 相同模型

```json
[
  {
    "model": "qwen3:4b",
    "prompt": "相同提示词",
    "task_type": "qa"
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
    "prompt": "相同提示词",
    "task_type": "qa"
  }
]
```

### 场景2: 对比不同量化方案

```json
[
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
    "prompt": "测试提示",
    "task_type": "qa"
  },
  {
    "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:8bit",
    "prompt": "测试提示",
    "task_type": "qa"
  }
]
```

### 场景3: 多模型多任务评估

```json
[
  {"model": "qwen3:4b", "task_type": "qa", ...},
  {"model": "qwen3:4b", "task_type": "code", ...},
  {"model": "hf:...:4bit", "task_type": "qa", ...},
  {"model": "hf:...:4bit", "task_type": "code", ...}
]
```

## ⚙️ 配置建议

### 基于你的硬件（RTX 4060 8GB）

**推荐配置**:
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit",
  "max_tokens": 512,
  "temperature": 0.7
}
```

**如果显存不足**:
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
  "max_tokens": 256
}
```

**性能优先**（需要更多显存）:
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:8bit",
  "max_tokens": 512
}
```

## 🔧 集成到现有工作流

### 步骤1: 准备 HF 模型

```bash
# 下载推荐模型
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct --quantize 4bit
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-7B-Instruct --quantize 4bit

# 验证模型
python scripts/manage_models.py --list
```

### 步骤2: 创建实验配置

基于 `experiments/test_cases_mixed.json` 创建你的配置文件。

### 步骤3: 运行实验

```bash
python experiments/unified_runner.py --config your_config.json
```

### 步骤4: 分析结果

结果文件与原有格式兼容，可以使用现有的分析脚本：

```bash
# 如果需要，可以转换为原有格式
python scripts/convert_results.py --input results/unified_results_*.json --output data/experiments_N/
```

## 📚 相关文档

- [快速开始指南](QUICK_START_GUIDE.md)
- [迁移指南](MIGRATION_GUIDE.md)
- [HF模型使用指南](docs/experiment/hf_models_guide.md)
- [HF模型快速开始](HUGGINGFACE_SETUP.md)
- [模型下载配置](configs/models_to_download.yaml)
- [故障排除](TROUBLESHOOTING.md)

## ⚠️ 注意事项

1. **首次加载**: HF 模型首次加载需要 30-60 秒，后续会使用缓存
2. **显存管理**: 8GB 显存建议使用 4bit 量化
3. **批量实验**: 建议分批运行，避免显存累积
4. **模型路径**: 确保 HF 模型已下载到正确路径
5. **依赖安装**: 需要安装 `transformers`, `huggingface_hub`, `accelerate`, `bitsandbytes`

## 🐛 故障排除

### 问题1: HF 模型加载失败

```bash
pip install transformers huggingface_hub accelerate bitsandbytes
```

### 问题2: 显存不足

- 使用 4bit 量化
- 减小 max_tokens
- 使用更小的模型（3B 代替 7B）

### 问题3: 量化不生效

```bash
pip install bitsandbytes --prefer-binary
```

### 问题4: 模型路径错误

```bash
python scripts/manage_models.py --list
# 检查模型路径是否正确
```

## 🎯 下一步

1. ✅ 安装 HF 依赖
2. ✅ 下载推荐模型
3. ✅ 运行示例实验
4. ⏭️ 创建自定义配置
5. ⏭️ 对比分析结果
6. ⏭️ 集成到论文实验

## 📞 获取帮助

- 快速开始: `QUICK_START_GUIDE.md`
- 迁移说明: `MIGRATION_GUIDE.md`
- 检查模型状态: `python scripts/manage_models.py --list`
- 验证环境: `python scripts/test_ollama_runner.py`

祝实验顺利！🚀
