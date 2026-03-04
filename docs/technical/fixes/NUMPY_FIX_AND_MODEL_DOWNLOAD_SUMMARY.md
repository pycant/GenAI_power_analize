# NumPy 修复与模型下载总结

## 日期
2026-03-02

## 问题描述

在尝试使用 HuggingFace 下载脚本时遇到 NumPy 兼容性问题：
- NumPy 2.2.6 与为 NumPy 1.x 编译的 PyTorch/Transformers 不兼容
- 导致 `download_hf_model.py` 脚本无法运行
- 错误信息：`ValueError: Unable to compare versions for numpy>=1.17: need=1.17 found=None`

## 解决方案

### 1. NumPy 降级
```bash
# 移除损坏的 NumPy 安装
Remove-Item -Recurse -Force "E:\ananconda\lib\site-packages\numpy*"

# 安装兼容版本
pip install numpy==1.26.4
```

### 2. 验证修复
```bash
python -c "import numpy as np; print('✓ NumPy version:', np.__version__); import torch; print('✓ PyTorch version:', torch.__version__); import transformers; print('✓ Transformers version:', transformers.__version__)"
```

**输出结果：**
- ✓ NumPy version: 1.26.4
- ✓ PyTorch version: 2.2.2
- ✓ Transformers version: 4.57.1

## 模型下载成功

### microsoft/phi-3-mini-4k-instruct
- **大小**: 7.12 GB
- **格式**: safetensors
- **量化**: 4bit
- **下载时间**: 约 3 分钟
- **词表大小**: 32,011 tokens
- **下载日期**: 2026-03-02T19:58:53

## 当前模型库存

### HuggingFace 模型（已下载）

| 模型名称 | 参数量 | 大小 | 量化 | 格式 | 下载日期 |
|---------|--------|------|------|------|---------|
| Qwen2.5-3B-Instruct | 3B | 5.76 GB | 4bit | safetensors | 2026-02-22 |
| Qwen2.5-7B-Instruct | 7B | 14.2 GB | 4bit | safetensors | 2026-02-28 |
| phi-3-mini-4k-instruct | 3.8B | 7.12 GB | 4bit | safetensors | 2026-03-02 |

**总存储占用**: ~27 GB

### Ollama 模型（可用）

根据 AGENTS.md，以下模型已在 Ollama 中可用：

| 模型名称 | 参数量 | 大小 | 量化 |
|---------|--------|------|------|
| qwen3:4b | 4B | ~2.5 GB | Q4_K_M |
| qwen3:8b | 8B | ~5.2 GB | Q4_K_M |
| gemma3:4b | 4B | ~3.3 GB | Q4_K_M |
| deepseek-r1:8b | 8B | ~5.2 GB | Q4_K_M |

**总存储占用**: ~16.2 GB

## 实验覆盖范围

根据 `docs/experiment/experiment_design.md`，当前模型覆盖：

### 3-4B 模型（小型）
- ✅ Qwen2.5-3B-Instruct (HF)
- ✅ phi-3-mini-4k-instruct (HF, 3.8B)
- ✅ qwen3:4b (Ollama)
- ✅ gemma3:4b (Ollama)

### 7-8B 模型（中型）
- ✅ Qwen2.5-7B-Instruct (HF)
- ✅ qwen3:8b (Ollama)
- ✅ deepseek-r1:8b (Ollama)

## 快速测试验证

已使用 `scripts/quick_test_refactoring.py` 验证系统功能：

### 测试结果
- ✅ Raw 和 Summary 文件成功分离
- ✅ 空闲基线数据正确记录
- ✅ 分轮监控功能正常工作
- ✅ 派生指标自动计算
- ✅ 对话摘要正确生成

### 测试模型
- qwen3:4b (Ollama)
- 2 个测试用例（单轮和多轮对话）
- 总耗时：~10 秒

## 后续建议

### 选项 1：继续下载 HuggingFace 模型
如需更多 3-4B 模型用于对比实验：
```bash
python scripts/download_hf_model.py --model-name google/gemma-2b-it --quantize 4bit
```

### 选项 2：使用现有模型开始实验
当前已有 7 个模型（3 个 HF + 4 个 Ollama），足够进行：
- 参数量对比（3-4B vs 7-8B）
- 框架对比（HuggingFace vs Ollama）
- 量化效果评估（均为 4bit/Q4）

### 选项 3：下载额外 Ollama 模型
```bash
ollama pull phi3.5:3.8b
ollama pull smollm3:3b
ollama pull mistral:7b
ollama pull llama3.1:8b
```

## 环境配置

### 关键依赖版本
- Python: 3.10
- NumPy: 1.26.4 ✅
- PyTorch: 2.2.2
- Transformers: 4.57.1
- CUDA: 12.6
- Ollama: 0.13.2

### 硬件环境
- GPU: NVIDIA GeForce RTX 4060 Laptop (8GB VRAM)
- CPU: Intel Core i7-13700H (14核20线程)
- RAM: 16GB DDR5
- 操作系统: Windows

## 注意事项

1. **NumPy 版本锁定**: 保持 NumPy 1.26.4，避免升级到 2.x
2. **存储空间**: 当前已使用 ~43 GB（HF 27GB + Ollama 16GB）
3. **VRAM 限制**: 8GB VRAM 限制了可运行的模型大小
   - 3-4B 模型：可运行 Q4/Q8/FP16
   - 7-8B 模型：仅可运行 Q4
4. **量化说明**: HF 模型标记为 4bit 但实际为 FP16，需在加载时动态量化

## 相关文档

- [实验设计文档](experiment/experiment_design.md)
- [HuggingFace 模型指南](experiment/hf_models_guide.md)
- [快速测试结果](../data/test/quick_test_refactoring_summary.json)
- [模型注册表](../models/model_registry.json)
- [AGENTS 使用指南](../agents.md)

## 问题排查

如果再次遇到 NumPy 问题：
```bash
# 检查版本
python -c "import numpy; print(numpy.__version__)"

# 如果不是 1.26.4，重新安装
pip install --force-reinstall numpy==1.26.4
```

如果 HuggingFace 下载失败：
```bash
# 检查网络连接
curl https://huggingface.co

# 使用镜像（如果需要）
export HF_ENDPOINT=https://hf-mirror.com

# 强制重新下载
python scripts/download_hf_model.py --model-name <model> --force
```
