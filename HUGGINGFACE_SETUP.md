# Hugging Face模型集成 - 快速开始

本文档介绍如何在项目中集成和使用Hugging Face模型。

## 📋 概述

项目现已支持从Hugging Face下载和使用大语言模型，作为Ollama的补充方案。新增功能包括：

- ✅ 自动化模型下载和管理
- ✅ 模型注册表和版本跟踪
- ✅ 4bit/8bit量化支持
- ✅ 统一的模型加载接口
- ✅ 批量推理和性能优化
- ✅ 与现有实验框架集成

## 🗂️ 新增文件结构

```
GenAI_power_analize/
├── models/                              # 新增：模型存储目录
│   ├── huggingface/                     # HF模型存储
│   ├── model_registry.json              # 模型注册表
│   └── README.md                        # 模型管理文档
├── scripts/
│   ├── download_hf_model.py             # 新增：单模型下载脚本
│   ├── manage_models.py                 # 新增：模型管理脚本
│   └── batch_download_models.py         # 新增：批量下载脚本
├── src/model_deployment/
│   └── hf_loader.py                     # 新增：HF模型加载器
├── configs/
│   └── models_to_download.yaml          # 新增：模型下载配置
├── docs/experiment/
│   └── hf_models_guide.md               # 新增：详细使用指南
├── requirements-hf.txt                  # 新增：HF依赖包
└── HUGGINGFACE_SETUP.md                 # 本文件
```

## 🚀 快速开始

### 步骤1: 安装依赖

```bash
# 激活conda环境
conda activate bartscore

# 安装Hugging Face依赖
pip install transformers huggingface_hub accelerate pyyaml

# 安装PyTorch (根据你的CUDA版本选择)
# CUDA 12.6 (你的系统)
pip install torch --index-url https://download.pytorch.org/whl/cu121

# 安装量化支持 (可选，需要CUDA)
pip install bitsandbytes
```

或者使用requirements文件：

```bash
pip install -r requirements-hf.txt
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### 步骤2: 下载模型

#### 推荐模型（基于你的硬件配置）

你的配置：RTX 4060 Laptop 8GB显存，16GB内存

```bash
# 方案1: 下载Qwen 3B (快速测试，约6GB)
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct --quantize 4bit

# 方案2: 下载Qwen 7B (推荐用于评估，约7-8GB显存)
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-7B-Instruct --quantize 4bit

# 方案3: 下载Phi-3 Mini (微软模型，约7GB显存)
python scripts/download_hf_model.py --model-name microsoft/phi-3-mini-4k-instruct --quantize 4bit
```

#### 批量下载

```bash
# 下载所有高优先级模型
python scripts/batch_download_models.py --priority high

# 预览将要下载的模型
python scripts/batch_download_models.py --priority high --dry-run
```

### 步骤3: 验证安装

```bash
# 列出已下载的模型
python scripts/manage_models.py --list

# 验证模型完整性
python scripts/manage_models.py --verify
```

### 步骤4: 使用模型

创建测试脚本 `test_hf_model.py`:

```python
from src.model_deployment.hf_loader import HuggingFaceModelLoader

# 初始化加载器
loader = HuggingFaceModelLoader()

# 列出可用模型
print("可用模型:")
for model in loader.list_available_models():
    print(f"  - {model['name']} ({model['size_gb']} GB)")

# 加载模型
model, tokenizer = loader.load_model(
    "models/huggingface/Qwen--Qwen2.5-3B-Instruct",
    quantize="4bit",
    device="auto"
)

# 生成文本
prompt = "请用一句话解释什么是人工智能。"
response = loader.generate(
    model,
    tokenizer,
    prompt,
    max_new_tokens=128,
    temperature=0.7
)

print(f"\n问题: {prompt}")
print(f"回答: {response}")
```

运行测试：

```bash
python test_hf_model.py
```

## 📊 集成到实验框架

### 方法1: 修改现有实验脚本

在 `experiments/experiment_runner.py` 中添加HF模型支持：

```python
from src.model_deployment.hf_loader import HuggingFaceModelLoader

class ExperimentRunner:
    def __init__(self):
        # 现有的Ollama客户端
        self.ollama_client = OllamaClient()
        
        # 新增：HF模型加载器
        self.hf_loader = HuggingFaceModelLoader()
        self.hf_models = {}
    
    def run_experiment(self, model_name, task, **kwargs):
        # 判断是Ollama还是HF模型
        if model_name.startswith("hf:"):
            # HF模型
            hf_model_name = model_name[3:]  # 移除"hf:"前缀
            return self.run_hf_model(hf_model_name, task, **kwargs)
        else:
            # Ollama模型
            return self.run_ollama_model(model_name, task, **kwargs)
    
    def run_hf_model(self, model_name, task, **kwargs):
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
            task['prompt'],
            max_new_tokens=kwargs.get('max_tokens', 512),
            temperature=kwargs.get('temperature', 0.7)
        )
        
        return response
```

### 方法2: 创建新的实验配置

在 `data/experiments_N/config.py` 中：

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
        "name": "hf:Qwen--Qwen2.5-7B-Instruct",
        "path": "models/huggingface/Qwen--Qwen2.5-7B-Instruct",
        "quantize": "4bit"
    },
    {
        "name": "hf:microsoft--phi-3-mini-4k-instruct",
        "path": "models/huggingface/microsoft--phi-3-mini-4k-instruct",
        "quantize": "4bit"
    }
]

# 合并所有模型
ALL_MODELS = OLLAMA_MODELS + [m['name'] for m in HF_MODELS]
```

## 🔧 常用命令

### 模型下载

```bash
# 下载单个模型
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-7B-Instruct --quantize 4bit

# 批量下载
python scripts/batch_download_models.py --priority high

# 使用镜像加速（中国大陆）
set HF_ENDPOINT=https://hf-mirror.com
python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct
```

### 模型管理

```bash
# 列出所有模型
python scripts/manage_models.py --list

# 查看模型详情
python scripts/manage_models.py --info Qwen2.5-7B-Instruct

# 删除模型
python scripts/manage_models.py --delete Qwen2.5-3B-Instruct

# 清理缓存
python scripts/manage_models.py --clean-cache

# 验证模型
python scripts/manage_models.py --verify
```

## 💡 使用建议

### 1. 模型选择

基于你的硬件（RTX 4060 8GB）：

| 模型 | 参数量 | 量化 | 显存占用 | 推荐场景 |
|------|--------|------|----------|----------|
| Qwen2.5-3B | 3B | 4bit | ~3-4GB | 快速测试 |
| Qwen2.5-7B | 7B | 4bit | ~6-7GB | 主要评估 |
| Phi-3-Mini | 3.8B | 4bit | ~4-5GB | 对比基准 |
| Gemma-2B | 2B | 无 | ~4GB | 轻量级任务 |

### 2. 性能优化

```python
# 使用4bit量化节省显存
model, tokenizer = loader.load_model(model_path, quantize="4bit")

# 批量处理提高吞吐量
responses = loader.batch_generate(
    model, tokenizer, prompts,
    batch_size=2  # 根据显存调整
)

# 限制显存使用
model, tokenizer = loader.load_model(
    model_path,
    quantize="4bit",
    max_memory={0: "6GB", "cpu": "8GB"}
)
```

### 3. 与Ollama对比

**何时使用Ollama**:
- 快速原型开发
- 标准化评估
- 不需要特定模型

**何时使用Hugging Face**:
- 需要特定模型（如Qwen2.5系列）
- 需要模型微调
- 深度定制化需求
- 学术研究和论文复现

## 📚 详细文档

- [模型管理README](models/README.md) - 模型目录结构和管理
- [HF模型使用指南](docs/experiment/hf_models_guide.md) - 详细使用教程
- [模型下载配置](configs/models_to_download.yaml) - 推荐模型列表

## ⚠️ 注意事项

1. **显存管理**: 8GB显存建议使用4bit量化，避免同时加载多个大模型
2. **存储空间**: 每个7B模型约需15-20GB磁盘空间（含缓存）
3. **网络连接**: 首次下载需要稳定网络，建议使用镜像站点
4. **版本控制**: 模型文件已在`.gitignore`中排除，不会提交到Git
5. **授权模型**: Llama系列需要HF Token，设置环境变量`HF_TOKEN`

## 🐛 故障排除

### 问题1: 下载速度慢

```bash
# 使用Hugging Face镜像
set HF_ENDPOINT=https://hf-mirror.com
```

### 问题2: 显存不足

```python
# 使用更激进的量化
model, tokenizer = loader.load_model(model_path, quantize="4bit")

# 或使用更小的模型
# Qwen2.5-3B 替代 Qwen2.5-7B
```

### 问题3: bitsandbytes安装失败

```bash
# Windows用户可能需要使用预编译版本
pip install bitsandbytes --prefer-binary

# 或者不使用量化（需要更多显存）
model, tokenizer = loader.load_model(model_path, quantize=None)
```

## 📞 获取帮助

- 查看详细文档: `docs/experiment/hf_models_guide.md`
- 检查模型配置: `configs/models_to_download.yaml`
- 运行验证脚本: `python scripts/manage_models.py --verify`

## 🎯 下一步

1. ✅ 安装依赖
2. ✅ 下载推荐模型
3. ✅ 运行测试脚本
4. ⏭️ 集成到实验框架
5. ⏭️ 运行对比实验
6. ⏭️ 分析评估结果

祝实验顺利！🚀
