# 困惑度计算环境安装指南

## 📋 概述

本指南帮助你安装必要的依赖，以启用创意写作任务的困惑度（Perplexity）评估。

## 🎯 为什么需要困惑度？

- **流畅性评估**: 客观量化文本的语言流畅度
- **语法质量**: 间接反映语法正确性
- **补充维度**: 与多样性指标（Distinct-N）形成互补

## 📦 依赖要求

### 必需包
- `torch`: PyTorch 深度学习框架
- `transformers`: Hugging Face Transformers 库

### 模型下载
- 模型名称: `uer/gpt2-chinese-cluecorpussmall`
- 模型大小: ~300MB
- 首次运行时自动下载

## 🚀 安装步骤

### 方案 1: CPU 版本（推荐用于测试）

```bash
# 激活环境
conda activate bartscore

# 安装 CPU 版本
pip install torch torchvision torchaudio
pip install transformers
```

### 方案 2: GPU 版本（推荐用于生产）

```bash
# 激活环境
conda activate bartscore

# 安装 CUDA 12.6 版本（匹配你的系统）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装 transformers
pip install transformers
```

**注意**: 根据你的 CUDA 版本选择对应的 torch 版本
- CUDA 12.1: `cu121`
- CUDA 11.8: `cu118`
- CPU only: 不需要 `--index-url` 参数

### 方案 3: 使用清华镜像（国内用户）

```bash
# 激活环境
conda activate bartscore

# 使用清华镜像加速
pip install torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install transformers -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## ✅ 验证安装

运行以下命令验证安装是否成功：

```bash
python -c "import torch; import transformers; print(f'torch: {torch.__version__}'); print(f'transformers: {transformers.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

**预期输出**:
```
torch: 2.x.x
transformers: 4.x.x
CUDA available: True  # 如果安装了 GPU 版本
```

## 🔧 配置模型缓存

### 设置缓存目录（可选）

```bash
# Windows
set HF_HOME=D:\models\huggingface_cache

# Linux/Mac
export HF_HOME=/path/to/cache
```

### 使用国内镜像（可选）

```bash
# Windows
set HF_ENDPOINT=https://hf-mirror.com

# Linux/Mac
export HF_ENDPOINT=https://hf-mirror.com
```

## 🎮 运行完整评估

安装完成后，运行完整评估（含困惑度）：

```bash
# 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 运行评估（启用困惑度计算）
python data/analize/scripts/evaluate_creative_quality.py
```

**首次运行**会自动下载模型（~300MB），请耐心等待。

## 📊 预期性能

基于你的硬件配置（RTX 4060 8GB）：

| 指标 | CPU 模式 | GPU 模式 |
|------|----------|----------|
| 每个样本评估时间 | ~2-3秒 | ~0.5-1秒 |
| 总评估时间（55样本） | ~2-3分钟 | ~30-60秒 |
| 显存占用 | 0GB | ~2GB |

## ⚠️ 常见问题

### 问题 1: CUDA 版本不匹配

**错误信息**:
```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

**解决方案**:
```bash
# 检查 CUDA 版本
nvcc --version

# 安装匹配的 torch 版本
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 问题 2: 显存不足

**错误信息**:
```
RuntimeError: CUDA out of memory
```

**解决方案**:
```bash
# 使用 CPU 模式
python data/analize/scripts/evaluate_creative_quality.py
```

或在代码中设置：
```python
config = {
    'use_ppl': True,
    'device': 'cpu'  # 强制使用 CPU
}
```

### 问题 3: 模型下载失败

**错误信息**:
```
OSError: Can't load model
```

**解决方案**:
```bash
# 使用国内镜像
set HF_ENDPOINT=https://hf-mirror.com

# 或手动下载模型
# 访问: https://hf-mirror.com/uer/gpt2-chinese-cluecorpussmall
```

### 问题 4: 文本过长导致截断

**警告信息**:
```
Token indices sequence length is longer than the specified maximum sequence length
```

**说明**: 这是正常的，评估器会自动截断到 512 tokens。不影响评估结果。

## 🔄 卸载（如果需要）

```bash
pip uninstall torch torchvision torchaudio transformers
```

## 📚 更多资源

- [PyTorch 官方文档](https://pytorch.org/get-started/locally/)
- [Transformers 文档](https://huggingface.co/docs/transformers)
- [GPT-2 中文模型](https://huggingface.co/uer/gpt2-chinese-cluecorpussmall)

## 💡 提示

1. **首次运行较慢**: 需要下载模型，后续运行会使用缓存
2. **GPU 加速显著**: 如果有 GPU，强烈建议安装 GPU 版本
3. **批量处理**: 评估器已优化，会自动批量处理以提高效率
4. **内存管理**: 评估器会在评估完成后自动释放显存

---

**文档版本**: v1.0  
**最后更新**: 2026-03-04  
**适用系统**: Windows (CUDA 12.6)
