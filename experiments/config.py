# 实验配置文件

# ============================================================================
# Ollama模型配置
# ============================================================================
OLLAMA_MODELS = [
    "deepseek-r1:8b",
    "gemma3:4b",
    "qwen3:8b",
    "qwen3:4b"
]

# ============================================================================
# Hugging Face模型配置
# ============================================================================
# 格式: {"name": "显示名称", "path": "模型路径", "quantize": "量化选项"}
HF_MODELS = [
    {
        "name": "Qwen2.5-3B-4bit",
        "path": "models/huggingface/Qwen--Qwen2.5-3B-Instruct",
        "quantize": "4bit"
    },
    {
        "name": "Qwen2.5-7B-4bit",
        "path": "models/huggingface/Qwen--Qwen2.5-7B-Instruct",
        "quantize": "4bit"
    },
    {
        "name": "Phi-3-Mini-4bit",
        "path": "models/huggingface/microsoft--phi-3-mini-4k-instruct",
        "quantize": "4bit"
    }
]

# ============================================================================
# 生成参数
# ============================================================================
TEMPERATURE = 0.7
TOP_P = 0.9
NUM_CTX = 4096
SEED = 1234
MAX_TOKENS = 512

# ============================================================================
# Ollama特定参数
# ============================================================================
KEEPALIVE = "0s"
WARMUP = True

# ============================================================================
# 实验参数
# ============================================================================
RUNS = 1  # 每个测试用例运行次数

# ============================================================================
# 量化选项说明
# ============================================================================
# - "4bit": 4位量化，最省显存，适合8GB显存
# - "8bit": 8位量化，平衡性能和显存
# - None: 不量化，使用fp16，需要更多显存

# ============================================================================
# 模型规格字符串格式
# ============================================================================
# Ollama模型:
#   - "model_name" 或 "ollama:model_name"
#   - 示例: "qwen3:4b", "ollama:deepseek-r1:8b"
#
# Hugging Face模型:
#   - "hf:model_path" 或 "hf:model_path:quantize"
#   - 示例: "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit"
#   - 示例: "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct"  # 默认fp16

# ============================================================================
# 辅助函数
# ============================================================================

def get_all_model_specs():
    """获取所有模型的规格字符串列表"""
    specs = []
    
    # 添加Ollama模型
    for model in OLLAMA_MODELS:
        specs.append(f"ollama:{model}")
    
    # 添加HF模型
    for model in HF_MODELS:
        if model.get("quantize"):
            specs.append(f"hf:{model['path']}:{model['quantize']}")
        else:
            specs.append(f"hf:{model['path']}")
    
    return specs


def get_hf_model_by_name(name):
    """根据名称获取HF模型配置"""
    for model in HF_MODELS:
        if model["name"] == name:
            return model
    return None


def get_model_display_name(model_spec):
    """获取模型的显示名称"""
    if model_spec.startswith("hf:"):
        parts = model_spec[3:].split(":")
        path = parts[0]
        quantize = parts[1] if len(parts) > 1 else "fp16"
        model_name = path.split("/")[-1].replace("--", "/")
        return f"{model_name} ({quantize})"
    elif model_spec.startswith("ollama:"):
        return model_spec[7:]
    else:
        return model_spec
