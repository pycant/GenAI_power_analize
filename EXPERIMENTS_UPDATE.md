# 实验框架更新说明

本文档说明对 `experiments/` 目录的更新，以支持 Hugging Face 模型和量化参数。

## 📋 更新概述

实验框架现已支持：
- ✅ Ollama 和 Hugging Face 模型的统一调用
- ✅ 4bit/8bit 量化支持
- ✅ 灵活的模型规格配置
- ✅ 向后兼容原有 Ollama 实验
- ✅ 完整的资源监控和质量评估

## 🗂️ 新增和修改的文件

### 新增文件

```
experiments/
├── unified_runner.py              # 新增：统一实验运行器
├── test_cases_mixed.json          # 新增：混合模型测试用例示例
├── UNIFIED_RUNNER_GUIDE.md        # 新增：使用指南
└── config.py                      # 修改：增加HF模型配置
```

### 文件说明

#### 1. `unified_runner.py` - 统一实验运行器

**功能**:
- 统一接口调用 Ollama 和 HF 模型
- 自动解析模型规格字符串
- 支持量化参数配置
- 完整的资源监控
- BARTScore 质量评估
- 模型缓存管理

**核心类**:
```python
class UnifiedExperimentRunner:
    def parse_model_spec(self, model_spec)  # 解析模型规格
    def call_ollama_generate(...)           # 调用Ollama模型
    def call_hf_generate(...)               # 调用HF模型
    def run_single_experiment(...)          # 运行单次实验
    def run_experiment_suite(...)           # 运行实验套件
```

#### 2. `test_cases_mixed.json` - 混合模型测试用例

包含 Ollama 和 HF 模型的对比测试用例：
- QA 任务对比
- 代码生成对比
- 创意写作对比
- 文本摘要对比

#### 3. `config.py` - 增强配置文件

新增内容:
```python
# Ollama模型列表
OLLAMA_MODELS = [...]

# HF模型配置
HF_MODELS = [
    {
        "name": "Qwen2.5-3B-4bit",
        "path": "models/huggingface/Qwen--Qwen2.5-3B-Instruct",
        "quantize": "4bit"
    },
    ...
]

# 辅助函数
def get_all_model_specs()
def get_hf_model_by_name(name)
def get_model_display_name(model_spec)
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

# 运行示例（包含Ollama和HF模型）
python experiments/unified_runner.py --sample
```

### 方法2: 使用配置文件

```bash
# 使用混合模型配置
python experiments/unified_runner.py --config experiments/test_cases_mixed.json

# 指定输出目录
python experiments/unified_runner.py --config experiments/test_cases_mixed.json --output-dir results/exp_2
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
python experiments/unified_runner.py --config my_experiment.json
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

原有的 `experiment_runner.py` 仍然可用：

```bash
# 继续使用原有脚本
python experiments/experiment_runner.py --config test_cases.json
```

### 迁移到统一运行器

只需修改模型名称格式：

**原配置**:
```json
{
  "model": "qwen3:4b",
  "prompt": "...",
  ...
}
```

**新配置**（兼容）:
```json
{
  "model": "qwen3:4b",  # 或 "ollama:qwen3:4b"
  "prompt": "...",
  ...
}
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

- [统一运行器使用指南](experiments/UNIFIED_RUNNER_GUIDE.md)
- [HF模型使用指南](docs/experiment/hf_models_guide.md)
- [HF模型快速开始](HUGGINGFACE_SETUP.md)
- [模型下载配置](configs/models_to_download.yaml)

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

- 查看详细指南: `experiments/UNIFIED_RUNNER_GUIDE.md`
- 检查模型状态: `python scripts/manage_models.py --list`
- 验证环境: `python experiments/unified_runner.py --sample`

祝实验顺利！🚀
