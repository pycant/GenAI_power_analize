#!/usr/bin/env python3
"""
创建实验配置文件

功能：
- 从综合测试用例中选择指定数量的任务
- 保持任务类型平衡
- 生成指定模型的实验配置
"""

import json
import sys
import random
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def select_balanced_tasks(tasks: List[Dict], target_count: int, seed: int = 42) -> List[Dict]:
    """
    按任务类型平衡选择任务
    
    Args:
        tasks: 所有任务列表
        target_count: 目标任务数量
        seed: 随机种子
        
    Returns:
        选中的任务列表
    """
    random.seed(seed)
    
    # 按任务类型分组
    tasks_by_type = defaultdict(list)
    for task in tasks:
        task_type = task.get('task_type', 'unknown')
        tasks_by_type[task_type].append(task)
    
    # 计算每种类型应该选择的数量
    total_types = len(tasks_by_type)
    base_count = target_count // total_types
    remainder = target_count % total_types
    
    selected = []
    type_counts = {}
    
    # 为每种类型分配数量
    for i, (task_type, type_tasks) in enumerate(sorted(tasks_by_type.items())):
        # 前 remainder 个类型多分配1个
        count = base_count + (1 if i < remainder else 0)
        count = min(count, len(type_tasks))  # 不超过该类型的总数
        type_counts[task_type] = count
    
    # 从每种类型中随机选择
    for task_type, type_tasks in sorted(tasks_by_type.items()):
        count = type_counts[task_type]
        selected_tasks = random.sample(type_tasks, count)
        selected.extend(selected_tasks)
    
    # 打印选择统计
    print(f"\n任务选择统计:")
    print(f"{'='*60}")
    for task_type in sorted(type_counts.keys()):
        total = len(tasks_by_type[task_type])
        selected_count = type_counts[task_type]
        print(f"  {task_type:15s}: {selected_count:2d} / {total:2d}")
    print(f"{'='*60}")
    print(f"  总计: {len(selected)} / {len(tasks)}\n")
    
    return selected


def get_optimized_max_tokens(task_type: str, difficulty: str = 'medium') -> int:
    """
    根据任务类型和难度获取优化的 max_tokens 值
    
    Args:
        task_type: 任务类型
        difficulty: 难度级别
        
    Returns:
        推荐的 max_tokens 值
    """
    # 基础值（按任务类型）
    base_tokens = {
        'code': 800,           # 代码生成需要更多 tokens
        'creative': 500,       # 创意写作需要灵活空间
        'math': 400,           # 数学推理需要展示过程
        'multi_turn': 300,     # 多轮对话每轮
        'qa': 200,             # 问答任务
        'reasoning': 400,      # 推理任务需要详细解释
        'summary': 250,        # 摘要任务
        'translation': 300     # 翻译任务
    }
    
    # 难度调整因子
    difficulty_multiplier = {
        'easy': 0.8,
        'medium': 1.0,
        'hard': 1.5
    }
    
    base = base_tokens.get(task_type, 300)
    multiplier = difficulty_multiplier.get(difficulty, 1.0)
    
    return int(base * multiplier)


def convert_to_experiment_format(task: Dict, model_name: str) -> Dict:
    """
    将测试用例转换为实验配置格式
    
    Args:
        task: 测试用例
        model_name: 模型名称
        
    Returns:
        实验配置字典
    """
    task_type = task.get('task_type', 'qa')
    difficulty = task.get('difficulty', 'medium')
    
    # 使用优化的 max_tokens
    optimized_max_tokens = get_optimized_max_tokens(task_type, difficulty)
    
    # 基础配置
    config = {
        'model': model_name,
        'task_type': task_type,
        'task_id': task.get('id', ''),
        'temperature': task.get('temperature', 0.7),
        'max_tokens': optimized_max_tokens,
        'repeat': task.get('repeat', 1),
        'idle_measurement_duration': 0,
        # 语言信息
        'language': task.get('language', 'en'),
        'language_type': task.get('language_type', 'monolingual'),
        'languages': task.get('languages', ['en'])
    }
    
    # 根据任务类型添加特定字段
    if task_type == 'qa':
        config['prompts'] = task.get('question', '')
        if 'expected_answer_text' in task:
            config['reference_text'] = task['expected_answer_text']
        config['difficulty'] = task.get('difficulty', 'medium')
        
    elif task_type == 'math':
        config['prompts'] = task.get('question', '')
        if 'expected_answer' in task:
            config['reference_text'] = str(task['expected_answer'])
        config['difficulty'] = task.get('difficulty', 'medium')
        
    elif task_type == 'code':
        config['prompts'] = task.get('question', '')
        config['programming_language'] = task.get('programming_language', 'python')
        config['difficulty'] = task.get('difficulty', 'medium')
        if 'canonical_solution' in task:
            config['reference_code'] = task['canonical_solution']
        
    elif task_type == 'translation':
        config['prompts'] = f"Translate the following text from {task.get('source_lang', 'en')} to {task.get('target_lang', 'zh')}:\n\n{task.get('source_text', '')}"
        config['reference_text'] = task.get('target_text', '')
        config['source_lang'] = task.get('source_lang', 'en')
        config['target_lang'] = task.get('target_lang', 'zh')
        config['difficulty'] = task.get('difficulty', 'medium')
        
    elif task_type == 'reasoning':
        config['prompts'] = task.get('question', '')
        if 'expected_answer' in task:
            config['reference_text'] = task['expected_answer']
        config['difficulty'] = task.get('difficulty', 'medium')
        
    elif task_type == 'summary':
        config['prompts'] = f"{task.get('instruction', '')}\n\n{task.get('source_text', '')}"
        config['difficulty'] = task.get('difficulty', 'medium')
        
    elif task_type == 'creative':
        config['prompts'] = task.get('prompt', '')
        config['difficulty'] = task.get('difficulty', 'medium')
        
    elif task_type == 'multi_turn':
        # 多轮对话需要特殊处理
        conversation = task.get('conversation', [])
        config['prompts'] = [turn.get('user', '') for turn in conversation]
        config['keep_context'] = True
        config['per_turn_monitoring'] = False
        config['difficulty'] = task.get('difficulty', 'medium')
    
    return config


def create_experiment_config(
    input_file: str,
    output_file: str,
    model_name: str,
    task_count: int = 40,
    seed: int = 42
):
    """
    创建实验配置文件
    
    Args:
        input_file: 输入的测试用例文件
        output_file: 输出的实验配置文件
        model_name: 模型名称
        task_count: 选择的任务数量
        seed: 随机种子
    """
    print(f"读取测试用例: {input_file}")
    
    # 读取测试用例
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = data.get('tasks', [])
    print(f"总任务数: {len(tasks)}")
    
    # 选择任务
    print(f"\n从 {len(tasks)} 个任务中选择 {task_count} 个...")
    selected_tasks = select_balanced_tasks(tasks, task_count, seed)
    
    # 转换为实验配置格式
    print(f"转换为实验配置格式...")
    experiment_configs = []
    for task in selected_tasks:
        config = convert_to_experiment_format(task, model_name)
        experiment_configs.append(config)
    
    # 统计语言分布
    lang_stats = defaultdict(int)
    lang_type_stats = defaultdict(int)
    for config in experiment_configs:
        lang_type_stats[config.get('language_type', 'unknown')] += 1
        for lang in config.get('languages', []):
            lang_stats[lang] += 1
    
    print(f"\n语言类型分布:")
    print(f"{'='*60}")
    for lang_type, count in sorted(lang_type_stats.items()):
        print(f"  {lang_type:20s}: {count}")
    
    print(f"\n语言分布:")
    print(f"{'='*60}")
    for lang, count in sorted(lang_stats.items(), key=lambda x: x[1], reverse=True):
        lang_name = {
            'en': '英语',
            'zh': '中文',
            'zho_Hans': '中文（简体）',
            'eng': '英语',
            'ja': '日语',
            'ko': '韩语'
        }.get(lang, lang)
        print(f"  {lang_name:15s} ({lang}): {count}")
    print(f"{'='*60}\n")
    
    # 保存配置文件
    print(f"保存实验配置: {output_file}")
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(experiment_configs, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 完成！")
    print(f"   模型: {model_name}")
    print(f"   任务数: {len(experiment_configs)}")
    print(f"   配置文件: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='创建实验配置文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 为 gemma3:4b 创建40个任务的配置
  python create_experiment_config.py \\
    --input data/test_cases/test_cases_comprehensive.json \\
    --output data/experiments_gemma3/test_cases.json \\
    --model "ollama:gemma3:4b" \\
    --count 40
  
  # 为 Qwen 创建配置
  python create_experiment_config.py \\
    --input data/test_cases/test_cases_comprehensive.json \\
    --output data/experiments_qwen/test_cases.json \\
    --model "ollama:qwen3:8b" \\
    --count 40
  
  # 使用不同的随机种子
  python create_experiment_config.py \\
    --input data/test_cases/test_cases_comprehensive.json \\
    --output data/experiments_test/test_cases.json \\
    --model "ollama:gemma3:4b" \\
    --count 20 \\
    --seed 123
        """
    )
    
    parser.add_argument(
        '--input',
        required=True,
        help='输入的测试用例 JSON 文件'
    )
    
    parser.add_argument(
        '--output',
        required=True,
        help='输出的实验配置 JSON 文件'
    )
    
    parser.add_argument(
        '--model',
        required=True,
        help='模型名称（如 "ollama:gemma3:4b" 或 "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct:4bit"）'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        default=40,
        help='选择的任务数量（默认: 40）'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='随机种子（默认: 42）'
    )
    
    args = parser.parse_args()
    
    # 检查输入文件
    if not Path(args.input).exists():
        print(f"❌ 错误: 输入文件不存在: {args.input}")
        sys.exit(1)
    
    try:
        create_experiment_config(
            args.input,
            args.output,
            args.model,
            args.count,
            args.seed
        )
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
