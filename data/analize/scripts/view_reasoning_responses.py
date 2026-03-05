#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看逻辑推理任务的模型响应
用于辅助人工评分

使用方法:
    python view_reasoning_responses.py --model qwen_8b_ol_q4km --question q01
    python view_reasoning_responses.py --question q02  # 查看所有模型对q02的响应
    python view_reasoning_responses.py --model gemma_4b_ol_q4km  # 查看该模型的所有响应
"""

import pandas as pd
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data.analize.scripts.reasoning_config import REASONING_QUESTIONS


def load_responses():
    """加载模型响应数据"""
    responses_path = project_root / "data" / "analize" / "pre_data" / "comparison_matrices" / "reasoning" / "reasoning_responses.csv"
    
    if not responses_path.exists():
        print(f"错误: 找不到响应文件 {responses_path}")
        sys.exit(1)
    
    df = pd.read_csv(responses_path)
    return df


def print_separator(char='=', length=80):
    """打印分隔线"""
    print(char * length)


def print_question_info(question_id):
    """打印问题信息"""
    if question_id not in REASONING_QUESTIONS:
        print(f"错误: 未知的问题ID {question_id}")
        return False
    
    q_info = REASONING_QUESTIONS[question_id]
    print_separator('=')
    print(f"问题 {question_id}: {q_info['description']}")
    print_separator('-')
    print(f"问题内容:\n{q_info['question']}")
    print_separator('-')
    print(f"标准答案: {q_info['reference_answer']}")
    print(f"推理类型: {q_info['reasoning_type']}")
    print_separator('=')
    print()
    return True


def view_single_response(df, model, question):
    """查看单个模型对单个问题的响应"""
    if not print_question_info(question):
        return
    
    if model not in df['model'].values:
        print(f"错误: 未找到模型 {model}")
        print(f"可用模型: {', '.join(df['model'].values)}")
        return
    
    response = df[df['model'] == model][question].values[0]
    
    print(f"模型: {model}")
    print_separator('-')
    print("响应内容:")
    print(response)
    print_separator('=')


def view_all_models_for_question(df, question):
    """查看所有模型对某个问题的响应"""
    if not print_question_info(question):
        return
    
    for idx, row in df.iterrows():
        model = row['model']
        response = row[question]
        
        print(f"\n模型 {idx + 1}/{len(df)}: {model}")
        print_separator('-')
        print(response)
        print_separator('=')
        
        if idx < len(df) - 1:
            input("\n按Enter键查看下一个模型的响应...")
            print("\n")


def view_all_questions_for_model(df, model):
    """查看某个模型对所有问题的响应"""
    if model not in df['model'].values:
        print(f"错误: 未找到模型 {model}")
        print(f"可用模型: {', '.join(df['model'].values)}")
        return
    
    model_data = df[df['model'] == model].iloc[0]
    
    print(f"模型: {model}")
    print_separator('=')
    
    questions = [col for col in df.columns if col.startswith('q')]
    
    for idx, question in enumerate(questions, 1):
        print(f"\n问题 {idx}/{len(questions)}: {question}")
        
        if question in REASONING_QUESTIONS:
            q_info = REASONING_QUESTIONS[question]
            print(f"描述: {q_info['description']}")
            print(f"标准答案: {q_info['reference_answer']}")
        
        print_separator('-')
        print("响应内容:")
        print(model_data[question])
        print_separator('=')
        
        if idx < len(questions):
            input("\n按Enter键查看下一个问题...")
            print("\n")


def list_models(df):
    """列出所有可用的模型"""
    print("可用模型列表:")
    print_separator('-')
    for idx, model in enumerate(df['model'].values, 1):
        print(f"{idx}. {model}")
    print_separator('=')


def list_questions():
    """列出所有问题"""
    print("可用问题列表:")
    print_separator('-')
    for q_id, q_info in REASONING_QUESTIONS.items():
        print(f"{q_id}: {q_info['description']}")
        print(f"   类型: {q_info['reasoning_type']}")
        print()
    print_separator('=')


def main():
    parser = argparse.ArgumentParser(
        description='查看逻辑推理任务的模型响应',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 查看特定模型对特定问题的响应
  python view_reasoning_responses.py --model qwen_8b_ol_q4km --question q01
  
  # 查看所有模型对某个问题的响应
  python view_reasoning_responses.py --question q02
  
  # 查看某个模型对所有问题的响应
  python view_reasoning_responses.py --model gemma_4b_ol_q4km
  
  # 列出所有可用的模型
  python view_reasoning_responses.py --list-models
  
  # 列出所有问题
  python view_reasoning_responses.py --list-questions
        """
    )
    
    parser.add_argument('--model', '-m', type=str, help='模型名称')
    parser.add_argument('--question', '-q', type=str, help='问题ID (如 q01, q02)')
    parser.add_argument('--list-models', action='store_true', help='列出所有可用的模型')
    parser.add_argument('--list-questions', action='store_true', help='列出所有问题')
    
    args = parser.parse_args()
    
    # 加载数据
    df = load_responses()
    
    # 处理命令
    if args.list_models:
        list_models(df)
    elif args.list_questions:
        list_questions()
    elif args.model and args.question:
        view_single_response(df, args.model, args.question)
    elif args.question:
        view_all_models_for_question(df, args.question)
    elif args.model:
        view_all_questions_for_model(df, args.model)
    else:
        parser.print_help()
        print("\n提示: 使用 --list-models 查看可用模型，使用 --list-questions 查看可用问题")


if __name__ == '__main__':
    main()
