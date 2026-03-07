"""
Pareto分析共享配置

包含模型名称映射、路径配置等共享常量
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# 模型名称映射（从summary格式到metrics格式）
MODEL_MAPPING = {
    'deepseek_8b_ol_q4km': 'deepseek-r1:8b',
    'gemma_2b_hf_4bit': 'google--gemma-2b-it:4bit',
    'gemma_2b_hf_8bit': 'google--gemma-2b-it:8bit',
    'gemma_4b_ol_q4km': 'gemma3:4b',
    'phi3_4b_hf_4bit': 'microsoft--phi-3-mini-4k-instruct:4bit',
    'phi3_4b_hf_8bit': 'microsoft--phi-3-mini-4k-instruct:8bit',
    'qwen25_3b_hf_4bit': 'qwen--qwen2.5-3b-instruct:4bit',
    'qwen25_3b_hf_8bit': 'qwen--qwen2.5-3b-instruct:8bit',
    'qwen25_7b_hf_4bit': 'qwen--qwen2.5-7b-instruct:4bit',
    'qwen25_7b_hf_8bit': 'qwen--qwen2.5-7b-instruct:8bit',
    'qwen_4b_ol_q4km': 'qwen3:4b',
    'qwen_8b_ol_q4km': 'qwen3:8b'
}

# 数据路径配置
DATA_PATHS = {
    'energy': PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'derived_metrics' / '08_energy_per_token.csv',
    'speed': PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'derived_metrics' / '07_avg_token_speed.csv',
}

# 输出根目录
OUTPUT_ROOT = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis'
