#!/usr/bin/env python3
"""
设置 experiments_5 实验配置
从 test_cases_comprehensive.json 创建实验配置文件
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# 配置
SOURCE_TEST_CASES = Path("data/test_cases/test_cases_comprehensive.json")
EXPERIMENT_DIR = Path("data/experiments_5")

# 默认模型列表（可通过命令行参数修改）
DEFAULT_MODELS = [
    "qwen3:4b",
    "qwen3:8b", 
    "deepseek-r1:8b",
    "gemma3:4b"
]

# 实验配置
EXPERIMENT_CONFIG = {
    "TEMPERATURE": 0.7,  # 默认温度，会被测试用例覆盖
    "TOP_P": 0.9,
    "NUM_CTX": 8192,  # 增大上下文窗口以支持更长的输入
    "SEED": 42,
    "KEEPALIVE": "5m",
    "WARMUP": True,
    "RUNS": 1  # 每个测试用例的重复次数会从测试用例本身读取
}


def load_test_cases(filepath):
    """加载测试用例"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def convert_test_case_format(task, model_spec):
    """
    将 comprehensive 格式的测试用例转换为实验运行器格式
    
    Args:
        task: 测试用例字典
        model_spec: 模型规格字符串（如 "qwen3:4b"）
    
    Returns:
        转换后的测试用例字典（符合 EXPERIMENT_RUNNER_GUIDE.md 格式）
    """
    task_type = task.get("task_type", "unknown")
    
    # 基础字段（按照 EXPERIMENT_RUNNER_GUIDE.md 的格式）
    converted = {
        "model": model_spec,
        "task_type": task_type,
        "max_tokens": task.get("max_tokens", 500),
        "temperature": task.get("temperature", 0.7),
        "top_p": 0.9,
        "idle_measurement_duration": 10  # 启用空闲基线测量
    }
    
    # 根据任务类型设置 prompts 和 reference_text
    if task_type == "qa":
        # QA 任务：问题 + 选项
        prompt = task.get("question", "")
        if "choices" in task:
            prompt += "\n\nOptions:\n"
            for i, choice in enumerate(task["choices"]):
                prompt += f"{chr(65+i)}. {choice}\n"
            prompt += "\nPlease select the correct answer."
        converted["prompts"] = prompt
        # 添加 reference_text（如果存在）
        if task.get("expected_answer_text"):
            converted["reference_text"] = task["expected_answer_text"]
        
    elif task_type == "math":
        # 数学任务
        converted["prompts"] = task.get("question", "")
        if task.get("expected_answer"):
            converted["reference_text"] = str(task["expected_answer"])
        
    elif task_type == "code":
        # 代码任务
        converted["prompts"] = task.get("question", "")
        # 代码任务使用 canonical_solution 作为参考
        if task.get("canonical_solution"):
            converted["reference_text"] = task["canonical_solution"]
        
    elif task_type == "translation":
        # 翻译任务
        source_lang_map = {"eng": "English", "zho_Hans": "Chinese"}
        target_lang_map = {"eng": "English", "zho_Hans": "Chinese"}
        source_lang = source_lang_map.get(task.get("source_lang", "eng"), "English")
        target_lang = target_lang_map.get(task.get("target_lang", "zho_Hans"), "Chinese")
        
        prompt = f"Please translate the following {source_lang} text to {target_lang}:\n\n{task.get('source_text', '')}"
        converted["prompts"] = prompt
        if task.get("target_text"):
            converted["reference_text"] = task["target_text"]
        
    elif task_type == "reasoning":
        # 推理任务
        converted["prompts"] = task.get("question", "")
        if task.get("expected_answer"):
            converted["reference_text"] = task["expected_answer"]
            
    elif task_type == "summary":
        # 摘要任务
        instruction = task.get("instruction", "")
        source_text = task.get("source_text", "")
        if instruction and source_text:
            prompt = f"{instruction}\n\n{source_text}"
        else:
            prompt = source_text or instruction
        converted["prompts"] = prompt
        
    elif task_type == "creative":
        # 创意写作任务
        converted["prompts"] = task.get("prompt", "")
        
    elif task_type == "multi_turn":
        # 多轮对话任务 - 提取所有轮次的用户输入
        conversation = task.get("conversation", [])
        if conversation:
            # prompts 应该是一个数组，包含所有轮次的用户输入
            converted["prompts"] = [turn.get("user", "") for turn in conversation]
            converted["keep_context"] = True  # 多轮对话保持上下文
            converted["per_turn_monitoring"] = False  # 不启用分轮监控以节省开销
    
    else:
        # 未知任务类型，使用通用格式
        converted["prompts"] = task.get("question", task.get("prompt", ""))
        if task.get("expected_answer"):
            converted["reference_text"] = task["expected_answer"]
    
    return converted


def create_experiment_structure(models=None):
    """
    创建实验目录结构和配置文件
    
    Args:
        models: 模型列表，如果为 None 则使用默认模型
    """
    if models is None:
        models = DEFAULT_MODELS
    
    print("="*70)
    print("设置 experiments_5 实验配置")
    print("="*70)
    
    # 创建实验目录
    EXPERIMENT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n✓ 创建实验目录: {EXPERIMENT_DIR}")
    
    # 创建子目录
    (EXPERIMENT_DIR / "raw").mkdir(exist_ok=True)
    (EXPERIMENT_DIR / "texts").mkdir(exist_ok=True)
    (EXPERIMENT_DIR / "summary").mkdir(exist_ok=True)
    
    for model in models:
        model_name = model.replace(":", "_")
        (EXPERIMENT_DIR / "raw" / model_name).mkdir(exist_ok=True)
        (EXPERIMENT_DIR / "texts" / model_name).mkdir(exist_ok=True)
    
    print(f"✓ 创建子目录: raw/, texts/, summary/")
    print(f"✓ 为 {len(models)} 个模型创建目录")
    
    # 加载测试用例
    print(f"\n加载测试用例: {SOURCE_TEST_CASES}")
    test_data = load_test_cases(SOURCE_TEST_CASES)
    tasks = test_data.get("tasks", [])
    print(f"✓ 加载 {len(tasks)} 个测试用例")
    
    # 转换测试用例格式 - 为每个模型生成测试用例
    print("\n转换测试用例格式...")
    converted_tasks = []
    
    for model in models:
        for task in tasks:
            # 为每个模型创建一个测试用例
            converted = convert_test_case_format(task, model_spec=model)
            converted_tasks.append(converted)
    
    print(f"✓ 生成 {len(converted_tasks)} 个测试用例（{len(models)} 个模型 × {len(tasks)} 个任务）")
    
    # 保存测试用例
    test_cases_file = EXPERIMENT_DIR / "test_cases.json"
    with open(test_cases_file, 'w', encoding='utf-8') as f:
        json.dump(converted_tasks, f, indent=2, ensure_ascii=False)
    print(f"✓ 保存测试用例: {test_cases_file}")
    
    # 创建 config.py
    config_py = EXPERIMENT_DIR / "config.py"
    config_content = f"""# Experiment 5 Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TEMPERATURE = {EXPERIMENT_CONFIG['TEMPERATURE']}
TOP_P = {EXPERIMENT_CONFIG['TOP_P']}
NUM_CTX = {EXPERIMENT_CONFIG['NUM_CTX']}
SEED = {EXPERIMENT_CONFIG['SEED']}
KEEPALIVE = "{EXPERIMENT_CONFIG['KEEPALIVE']}"
WARMUP = {EXPERIMENT_CONFIG['WARMUP']}
RUNS = {EXPERIMENT_CONFIG['RUNS']}

# Models to evaluate
MODELS = {models}

# Test cases source
TEST_CASES_SOURCE = "data/test_cases/test_cases_comprehensive.json"
"""
    
    with open(config_py, 'w', encoding='utf-8') as f:
        f.write(config_content)
    print(f"✓ 创建配置文件: {config_py}")
    
    # 创建 config.json
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config_json = {
        "timestamp": timestamp,
        "args": {
            "models": models,
            "runs": EXPERIMENT_CONFIG['RUNS'],
            "temperature": EXPERIMENT_CONFIG['TEMPERATURE'],
            "top_p": EXPERIMENT_CONFIG['TOP_P'],
            "num_ctx": EXPERIMENT_CONFIG['NUM_CTX'],
            "max_tokens": 512,  # 默认值，会被测试用例覆盖
            "seed": EXPERIMENT_CONFIG['SEED'],
            "warmup": EXPERIMENT_CONFIG['WARMUP'],
            "keepalive": EXPERIMENT_CONFIG['KEEPALIVE']
        },
        "exp_config_path": str(EXPERIMENT_DIR / "config.py"),
        "cases_file": str(EXPERIMENT_DIR / "test_cases.json"),
        "source_test_cases": str(SOURCE_TEST_CASES),
        "total_tasks": len(converted_tasks),
        "task_distribution": test_data.get("metadata", {}).get("task_distribution", {})
    }
    
    config_json_file = EXPERIMENT_DIR / "config.json"
    with open(config_json_file, 'w', encoding='utf-8') as f:
        json.dump(config_json, f, indent=2, ensure_ascii=False)
    print(f"✓ 创建配置文件: {config_json_file}")
    
    # 创建 README
    readme_content = f"""# Experiment 5

## 概述

本实验使用从标准测试集抽取的 80 个综合测试用例，评估 {len(models)} 个 LLM 模型的质效比。

## 配置

- **创建时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **原始任务数**: {len(tasks)}
- **模型数量**: {len(models)}
- **总测试用例数**: {len(converted_tasks)} ({len(models)} 模型 × {len(tasks)} 任务)
- **模型列表**: {', '.join(models)}

## 任务分布

{json.dumps(test_data.get('metadata', {}).get('task_distribution', {}), indent=2, ensure_ascii=False)}

## 数据来源

{json.dumps(test_data.get('metadata', {}).get('sources', {}), indent=2, ensure_ascii=False)}

## 测试用例格式

每个测试用例包含以下字段：
- `model`: 模型规格（如 "qwen3:4b"）
- `prompts`: 提示词（字符串或数组）
- `task_type`: 任务类型
- `max_tokens`: 最大生成token数
- `temperature`: 温度参数
- `top_p`: Top-p采样参数
- `idle_measurement_duration`: 空闲基线测量时长（秒）
- `reference_text`: 参考文本（可选，用于质量评估）
- `keep_context`: 是否保持上下文（多轮对话）
- `per_turn_monitoring`: 是否分轮监控（多轮对话）

## 目录结构

```
experiments_5/
├── config.py              # Python 配置文件
├── config.json            # JSON 配置文件
├── test_cases.json        # 测试用例（符合 EXPERIMENT_RUNNER_GUIDE.md 格式）
├── raw/                   # 原始实验结果（按模型分类）
├── texts/                 # 文本输出（按模型分类）
└── summary/               # 汇总结果
    ├── results.csv        # 详细结果
    └── stats.csv          # 统计摘要
```

## 运行实验

```bash
# 使用实验运行器
python experiments/experiment_runner.py --config data/experiments_5/test_cases.json --output-dir data/experiments_5

# 或使用快速测试脚本（如果存在）
python scripts/run_experiment_5.py
```

## 分析结果

```bash
# 运行分析脚本
python scripts/analyze_experiments_5.py
```

## 注意事项

1. 测试用例格式遵循 `docs/EXPERIMENT_RUNNER_GUIDE.md` 规范
2. 每个模型会运行所有 {len(tasks)} 个任务
3. 多轮对话任务会自动启用 `keep_context`
4. 所有任务都启用了空闲基线测量（10秒）
5. 运行时间预估：约 {len(converted_tasks) * 2} 分钟（假设每个测试用例平均2分钟）

---

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    readme_file = EXPERIMENT_DIR / "README.md"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ 创建说明文件: {readme_file}")
    
    # 打印摘要
    print("\n" + "="*70)
    print("✅ experiments_5 配置创建完成！")
    print("="*70)
    print(f"\n实验目录: {EXPERIMENT_DIR}")
    print(f"原始任务数: {len(tasks)}")
    print(f"模型数量: {len(models)}")
    print(f"总测试用例数: {len(converted_tasks)} ({len(models)} 模型 × {len(tasks)} 任务)")
    print(f"\n模型列表:")
    for model in models:
        print(f"  - {model}")
    
    print(f"\n任务类型分布:")
    task_dist = test_data.get('metadata', {}).get('task_distribution', {})
    for task_type, count in task_dist.items():
        print(f"  - {task_type}: {count} 题")
    
    print(f"\n下一步:")
    print(f"  1. 检查配置: {config_py}")
    print(f"  2. 检查测试用例: {test_cases_file}")
    print(f"  3. 运行实验: python experiments/experiment_runner.py --config {test_cases_file}")
    print(f"  4. 分析结果: python scripts/analyze_experiments_5.py")
    print("="*70)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="设置 experiments_5 实验配置")
    parser.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help=f"要评估的模型列表（默认: {' '.join(DEFAULT_MODELS)}）"
    )
    
    args = parser.parse_args()
    
    create_experiment_structure(models=args.models)


if __name__ == "__main__":
    main()
