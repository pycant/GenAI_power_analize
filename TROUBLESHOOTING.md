# 故障排除指南

## 问题：HF 模型路径错误

### 错误信息
```
❌ 生成文本失败: Incorrect path_or_model_id: 'models\huggingface\Qwen--Qwen2.5-7B-Instruct'
```

### 原因
1. 模型文件尚未下载
2. 路径格式不正确（Windows 反斜杠问题）
3. 路径不存在

### 解决步骤

#### 步骤 1: 检查模型是否存在

```bash
# 运行模型检查脚本
python scripts/check_hf_model.py
```

#### 步骤 2: 如果模型不存在，下载模型

```bash
# 方法 1: 使用下载脚本（推荐）
python scripts/download_hf_model.py --model Qwen/Qwen2.5-7B-Instruct --output-dir models/huggingface --quantize 4bit

# 方法 2: 使用批量下载
python scripts/batch_download_models.py --config configs/models_to_download.yaml
```

#### 步骤 3: 验证修复

```bash
# 再次检查模型
python scripts/check_hf_model.py

# 如果模型存在，运行测试
python experiments/unified_runner.py --config data/test/test_cases.json --output-dir data/test
```

## 问题：Ollama 模型调用失败

### 错误信息
```
❌ Ollama调用失败: Error: unknown flag: --max-tokens
```

### 原因
旧版代码使用了不支持的命令行参数

### 解决方案
已在最新代码中修复，使用 HTTP API 调用。更新代码后重新运行。

## 问题：模型不存在

### 错误信息
```
❌ 实验失败: 模型 llama3.2:3b 不存在
```

### 原因
1. 使用了默认示例配置（未指定 --config）
2. 指定的模型未安装

### 解决方案

#### 方案 1: 使用已安装的 Ollama 模型

```bash
# 查看已安装的模型
ollama list

# 使用 Ollama 配置运行
python experiments/experiment_runner.py --config data/test/test_cases_ollama.json --output-dir data/test
```

#### 方案 2: 安装所需的模型

```bash
# 安装模型
ollama pull llama3.2:3b

# 运行实验
python experiments/experiment_runner.py --config your_config.json --output-dir data/test
```

## 问题：内存不足

### 错误信息
```
CUDA out of memory
```

### 原因
模型太大，GPU 显存不足

### 解决方案

#### 方案 1: 使用量化模型

```bash
# 下载 4bit 量化模型（推荐用于 8GB 显存）
python scripts/download_hf_model.py --model Qwen/Qwen2.5-7B-Instruct --quantize 4bit

# 或在配置中指定量化
# "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"
```

#### 方案 2: 使用更小的模型

```bash
# 使用 Ollama 的小模型
# "model": "qwen3:4b"  # 约 2.5GB
# "model": "gemma3:4b"  # 约 3.3GB
```

#### 方案 3: 使用 CPU（慢但可行）

在 HF 模型加载时设置 `device="cpu"`

## 问题：依赖缺失

### 错误信息
```
ModuleNotFoundError: No module named 'transformers'
```

### 解决方案

```bash
# 安装 HF 相关依赖
pip install -r requirements-hf.txt

# 或单独安装
pip install transformers torch accelerate bitsandbytes
```

## 问题：BARTScore 不可用

### 错误信息
```
警告: BARTScore模块不可用，将跳过质量评估
```

### 原因
BARTScore 依赖未安装或路径不正确

### 解决方案

```bash
# 确保在正确的 conda 环境
conda activate bartscore

# 检查 BARTScore 路径
ls tools/thesis_reproduction/BARTScore/

# 如果缺失，需要从原始仓库获取
```

## 快速诊断命令

```bash
# 1. 检查 Python 环境
python --version
pip list | grep -E "transformers|torch|accelerate"

# 2. 检查 Ollama 服务
ollama list
ollama --version

# 3. 检查 HF 模型
python scripts/check_hf_model.py

# 4. 测试系统
python scripts/test_ollama_runner.py

# 5. 检查 GPU
nvidia-smi
```

## 推荐的工作流程

### 首次使用

1. **验证环境**
   ```bash
   conda activate bartscore
   python --version
   ```

2. **检查 Ollama**
   ```bash
   ollama list
   ```

3. **测试 Ollama 运行器**
   ```bash
   python scripts/test_ollama_runner.py
   ```

4. **运行简单实验**
   ```bash
   python experiments/experiment_runner.py --config data/test/test_cases_ollama.json --output-dir data/test
   ```

### 使用 HF 模型

1. **检查模型**
   ```bash
   python scripts/check_hf_model.py
   ```

2. **下载模型（如果需要）**
   ```bash
   python scripts/download_hf_model.py --model Qwen/Qwen2.5-7B-Instruct --quantize 4bit
   ```

3. **运行实验**
   ```bash
   python experiments/unified_runner.py --config data/test/test_cases.json --output-dir data/test
   ```

## 常见配置错误

### 错误 1: 路径使用反斜杠

❌ 错误:
```json
{
  "model": "hf:models\\huggingface\\Qwen--Qwen2.5-7B-Instruct:4bit"
}
```

✓ 正确:
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"
}
```

### 错误 2: 缺少量化参数

❌ 可能导致内存不足:
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct"
}
```

✓ 推荐（8GB 显存）:
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"
}
```

### 错误 3: 模型名称格式错误

❌ 错误:
```json
{
  "model": "Qwen--Qwen2.5-7B-Instruct:4bit"
}
```

✓ 正确:
```json
{
  "model": "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"
}
```

## 获取帮助

如果问题仍未解决：

1. 查看详细日志输出
2. 检查 `QUICK_START_GUIDE.md`
3. 查看 `experiments/UNIFIED_RUNNER_GUIDE.md`
4. 运行诊断脚本收集信息

## 系统要求

### 最低要求
- Python 3.8+
- 8GB RAM
- 4GB GPU 显存（使用 4bit 量化）

### 推荐配置
- Python 3.10
- 16GB RAM
- 8GB+ GPU 显存
- CUDA 11.8+

### 您的配置
- GPU: RTX 4060 Laptop 8GB ✓
- RAM: 16GB ✓
- CUDA: 12.6 ✓
- Python: 3.10 ✓

您的配置满足要求，应该可以运行 4bit 量化的 7B 模型。
