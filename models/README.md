# 模型管理目录

本目录用于存储从Hugging Face下载的大语言模型，作为Ollama的补充方案。

## 目录结构

```
models/
├── huggingface/              # Hugging Face模型存储
│   ├── {model_name}/         # 按模型名称组织
│   │   ├── config.json       # 模型配置
│   │   ├── pytorch_model.bin # 模型权重
│   │   ├── tokenizer.json    # 分词器
│   │   └── ...
│   └── cache/                # 模型缓存
├── onnx/                     # ONNX格式模型（可选）
├── quantized/                # 量化模型（可选）
└── model_registry.json       # 模型注册表

```

## 支持的模型格式

- **PyTorch**: .bin, .pt, .pth
- **Safetensors**: .safetensors (推荐，更安全)
- **ONNX**: .onnx (可选，用于推理优化)
- **量化模型**: GPTQ, AWQ, GGUF等

## 使用方法

### 1. 下载模型

```bash
# 下载单个模型
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-7B-Instruct --output-dir models/huggingface

# 下载并量化
python scripts/download_hf_model.py --model-name meta-llama/Llama-3.2-3B --quantize 4bit

# 批量下载
python scripts/download_hf_model.py --config configs/models_to_download.yaml
```

### 2. 列出已下载模型

```bash
python scripts/manage_models.py --list
```

### 3. 加载模型进行推理

```python
from src.model_deployment.hf_loader import HuggingFaceModelLoader

loader = HuggingFaceModelLoader()
model, tokenizer = loader.load_model("models/huggingface/Qwen2.5-7B-Instruct")
```

## 模型注册表

`model_registry.json` 记录所有已下载模型的元信息：

```json
{
  "models": [
    {
      "name": "Qwen2.5-7B-Instruct",
      "source": "Qwen/Qwen2.5-7B-Instruct",
      "path": "models/huggingface/Qwen2.5-7B-Instruct",
      "size_gb": 14.5,
      "format": "safetensors",
      "quantization": null,
      "downloaded_at": "2024-01-15T10:30:00Z",
      "last_used": "2024-01-20T15:45:00Z"
    }
  ]
}
```

## 存储空间管理

- 建议为模型目录预留至少 **100GB** 空间
- 7B模型约需 **14-28GB** (取决于精度)
- 13B模型约需 **26-52GB**
- 量化模型可节省 **50-75%** 空间

## 注意事项

1. **版本控制**: 模型文件不应提交到Git，已在 `.gitignore` 中排除
2. **访问权限**: 某些模型需要Hugging Face账号授权
3. **许可证**: 使用前请检查模型的许可证要求
4. **缓存清理**: 定期清理 `cache/` 目录释放空间

## 环境变量

```bash
# Hugging Face Token (用于访问受限模型)
export HF_TOKEN="your_huggingface_token"

# 模型缓存目录
export HF_HOME="models/huggingface/cache"

# 离线模式
export HF_HUB_OFFLINE=1
```

## 推荐模型列表

### 小型模型 (适合本地测试)
- `Qwen/Qwen2.5-3B-Instruct` - 3B参数
- `microsoft/phi-3-mini-4k-instruct` - 3.8B参数
- `google/gemma-2b-it` - 2B参数

### 中型模型 (平衡性能)
- `Qwen/Qwen2.5-7B-Instruct` - 7B参数
- `meta-llama/Llama-3.2-7B-Instruct` - 7B参数
- `mistralai/Mistral-7B-Instruct-v0.3` - 7B参数

### 大型模型 (高性能)
- `Qwen/Qwen2.5-14B-Instruct` - 14B参数
- `meta-llama/Llama-3.1-13B-Instruct` - 13B参数

## 故障排除

### 下载失败
- 检查网络连接
- 验证Hugging Face Token
- 尝试使用镜像站点

### 内存不足
- 使用量化模型
- 减小batch size
- 启用CPU offloading

### 模型加载错误
- 检查模型文件完整性
- 更新transformers库版本
- 查看错误日志
