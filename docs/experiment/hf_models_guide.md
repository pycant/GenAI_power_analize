# Hugging Face模型使用指南

本指南介绍如何在项目中使用Hugging Face模型进行评估实验。

## 目录结构

```
models/
├── huggingface/              # HF模型存储目录
│   ├── Qwen--Qwen2.5-7B-Instruct/
│   ├── microsoft--phi-3-mini-4k-instruct/
│   └── cache/                # 下载缓存
├── model_registry.json       # 模型注册表
└── README.md                 # 模型管理文档
```

## 快速开始

### 1. 安装依赖

```bash
# 激活conda环境
conda activate bartscore

# 安装Hugging Face相关依赖
pip install transformers huggingface_hub accelerate
pip install bitsandbytes  # 用于量化（可选）
pip install pyyaml  # 用于配置文件
```

### 2. 配置Hugging Face Token（可选）

某些模型需要授权访问（如Llama系列）：

```bash
# 访问 https://huggingface.co/settings/tokens 获取token
# 设置环境变量
set HF_TOKEN=your_huggingface_token_here
```

### 3. 下载模型

#### 方法一：下载单个模型

```bash
# 下载Qwen 3B模型（推荐用于快速测试）
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct --quantize 4bit

# 下载Qwen 7B模型（推荐用于正式评估）
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-7B-Instruct --quantize 4bit

# 下载Phi-3模型
python scripts/download_hf_model.py --model-name microsoft/phi-3-mini-4k-instruct --quantize 4bit
```

#### 方法二：批量下载

```bash
# 下载所有高优先级模型
python scripts/batch_download_models.py --priority high

# 下载小型模型类别
python scripts/batch_download_models.py --category small_models

# 预览将要下载的模型（不实际下载）
python scripts/batch_download_models.py --priority high --dry-run
```

### 4. 查看已下载的模型

```bash
# 列出所有模型
python scripts/manage_models.py --list

# 查看模型详情
python scripts/manage_models.py --info Qwen2.5-7B-Instruct

# 验证模型完整性
python scripts/manage_models.py --verify
```

## 在实验中使用模型

### 方法一：使用模型加载器

```python
from src.model_deployment.hf_loader import HuggingFaceModelLoader

# 初始化加载器
loader = HuggingFaceModelLoader()

# 加载模型（支持4bit量化）
model, tokenizer = loader.load_model(
    "models/huggingface/Qwen--Qwen2.5-7B-Instruct",
    quantize="4bit",
    device="auto"
)

# 生成文本
prompt = "请解释什么是人工智能。"
response = loader.generate(
    model, 
    tokenizer, 
    prompt,
    max_new_tokens=256,
    temperature=0.7
)

print(response)
```

### 方法二：批量推理

```python
from src.model_deployment.hf_loader import HuggingFaceModelLoader

loader = HuggingFaceModelLoader()
model, tokenizer = loader.load_model(
    "models/huggingface/Qwen--Qwen2.5-7B-Instruct",
    quantize="4bit"
)

# 批量生成
prompts = [
    "什么是机器学习？",
    "解释深度学习的概念。",
    "什么是神经网络？"
]

responses = loader.batch_generate(
    model,
    tokenizer,
    prompts,
    batch_size=2,
    max_new_tokens=128
)

for prompt, response in zip(prompts, responses):
    print(f"Q: {prompt}")
    print(f"A: {response}\n")
```

### 方法三：集成到实验框架

修改 `experiments/experiment_runner.py` 以支持HF模型：

```python
from src.model_deployment.hf_loader import HuggingFaceModelLoader

class ExperimentRunner:
    def __init__(self):
        self.ollama_client = OllamaClient()
        self.hf_loader = HuggingFaceModelLoader()
        self.hf_models = {}  # 缓存HF模型
    
    def run_hf_model(self, model_name, prompt, **kwargs):
        """运行Hugging Face模型"""
        # 加载模型（首次）
        if model_name not in self.hf_models:
            model_path = f"models/huggingface/{model_name}"
            model, tokenizer = self.hf_loader.load_model(
                model_path,
                quantize="4bit"
            )
            self.hf_models[model_name] = (model, tokenizer)
        
        model, tokenizer = self.hf_models[model_name]
        
        # 生成响应
        response = self.hf_loader.generate(
            model,
            tokenizer,
            prompt,
            **kwargs
        )
        
        return response
```

## 模型管理

### 删除模型

```bash
# 删除指定模型
python scripts/manage_models.py --delete Qwen2.5-3B-Instruct

# 自动确认删除
python scripts/manage_models.py --delete Qwen2.5-3B-Instruct --yes
```

### 清理缓存

```bash
# 清理Hugging Face下载缓存
python scripts/manage_models.py --clean-cache

# 自动确认清理
python scripts/manage_models.py --clean-cache --yes
```

## 性能优化建议

### 1. 量化选择

- **4bit量化**: 推荐用于显存受限环境（8GB显存可运行7B模型）
- **8bit量化**: 平衡性能和质量
- **无量化**: 最佳质量，需要更多显存

```python
# 4bit量化（最省显存）
model, tokenizer = loader.load_model(model_path, quantize="4bit")

# 8bit量化（平衡）
model, tokenizer = loader.load_model(model_path, quantize="8bit")

# 无量化（最佳质量）
model, tokenizer = loader.load_model(model_path, quantize=None)
```

### 2. 设备选择

```python
# 自动选择（推荐）
model, tokenizer = loader.load_model(model_path, device="auto")

# 强制使用GPU
model, tokenizer = loader.load_model(model_path, device="cuda")

# 强制使用CPU
model, tokenizer = loader.load_model(model_path, device="cpu")
```

### 3. 批量处理

```python
# 使用批量生成提高吞吐量
responses = loader.batch_generate(
    model,
    tokenizer,
    prompts,
    batch_size=4,  # 根据显存调整
    max_new_tokens=256
)
```

## 与Ollama模型对比

### Ollama模型
- ✅ 开箱即用，无需下载
- ✅ 统一API接口
- ✅ 自动资源管理
- ❌ 模型选择有限
- ❌ 定制化程度低

### Hugging Face模型
- ✅ 模型选择丰富
- ✅ 高度可定制
- ✅ 支持微调和量化
- ✅ 社区活跃
- ❌ 需要手动下载
- ❌ 显存管理需要注意

### 推荐使用场景

**使用Ollama**:
- 快速原型开发
- 标准化评估
- 资源受限环境

**使用Hugging Face**:
- 需要特定模型
- 需要模型微调
- 深度定制化需求
- 学术研究

## 常见问题

### Q1: 下载速度慢怎么办？

A: 可以使用Hugging Face镜像站点：

```bash
# 设置镜像（中国大陆）
set HF_ENDPOINT=https://hf-mirror.com
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct
```

### Q2: 显存不足怎么办？

A: 尝试以下方法：
1. 使用4bit量化
2. 减小batch_size
3. 使用更小的模型
4. 启用CPU offloading

```python
model, tokenizer = loader.load_model(
    model_path,
    quantize="4bit",
    device_map="auto",  # 自动分配到CPU/GPU
    max_memory={0: "6GB", "cpu": "8GB"}  # 限制显存使用
)
```

### Q3: 如何选择合适的模型？

A: 根据硬件配置选择：

| 显存 | 推荐模型 | 量化 |
|------|---------|------|
| 4GB | Qwen2.5-3B, Gemma-2B | 4bit |
| 6GB | Qwen2.5-3B, Phi-3-Mini | 4bit |
| 8GB | Qwen2.5-7B, Mistral-7B | 4bit |
| 12GB | Qwen2.5-7B, Llama-3.2-7B | 8bit |
| 16GB+ | Qwen2.5-14B, Llama-3.1-13B | 4bit/8bit |

### Q4: 模型加载很慢？

A: 首次加载会较慢，后续会使用缓存。可以：
1. 使用SSD存储模型
2. 预加载常用模型
3. 使用模型缓存机制

## 实验配置示例

在 `data/experiments_N/config.py` 中配置HF模型：

```python
# Ollama模型
OLLAMA_MODELS = [
    "deepseek-r1:8b",
    "gemma3:4b",
    "qwen3:8b"
]

# Hugging Face模型
HF_MODELS = [
    {
        "name": "Qwen2.5-7B-Instruct",
        "path": "models/huggingface/Qwen--Qwen2.5-7B-Instruct",
        "quantize": "4bit"
    },
    {
        "name": "Phi-3-Mini",
        "path": "models/huggingface/microsoft--phi-3-mini-4k-instruct",
        "quantize": "4bit"
    }
]

# 实验参数
TEMPERATURE = 0.7
TOP_P = 0.9
MAX_TOKENS = 512
```

## 参考资源

- [Hugging Face Hub](https://huggingface.co/models)
- [Transformers文档](https://huggingface.co/docs/transformers)
- [BitsAndBytes量化](https://github.com/TimDettmers/bitsandbytes)
- [模型下载配置](../../configs/models_to_download.yaml)
