#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一质量评估脚本 - 一键运行所有任务类型的质量评估

功能:
- 自动运行所有7种任务类型的质量评估
- 统一输出路径管理
- 进度跟踪和错误处理
- 生成综合评估报告

作者: Kiro AI Assistant
日期: 2026-03-05
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import argparse

# 确保UTF-8编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 项目路径配置
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "analize" / "pre_data"
RESULTS_DIR = PROJECT_ROOT / "data" / "analize" / "results"
SCRIPTS_DIR = PROJECT_ROOT / "data" / "analize" / "scripts"

# 评估任务配置
EVALUATION_TASKS = {
    'code': {
        'name': '代码生成',
        'script': 'evaluate_code_quality.py',
        'output_dir': RESULTS_DIR / 'code_quality',
        'enabled': True,
        'description': '评估代码生成任务的语法正确性、功能完整性和代码质量'
    },
    'creative': {
        'name': '创意写作',
        'script': 'evaluate_creative_quality.py',
        'output_dir': RESULTS_DIR / 'creative_quality',
        'enabled': True,
        'description': '评估创意写作的多样性、流畅性和创造力'
    },
    'math': {
        'name': '数学推理',
        'script': 'evaluate_math_quality.py',
        'output_dir': RESULTS_DIR / 'math_quality',
        'enabled': True,
        'description': '评估数学推理的准确性和推理完整性'
    },
    'qa': {
        'name': '问答',
        'script': 'evaluate_qa_quality.py',
        'output_dir': RESULTS_DIR / 'qa_quality',
        'enabled': True,
        'description': '评估问答任务的完整性、专业性和置信度'
    },
    'reasoning': {
        'name': '逻辑推理',
        'script': 'evaluate_reasoning_quality.py',
        'output_dir': RESULTS_DIR / 'reasoning_quality',
        'enabled': True,
        'description': '评估逻辑推理的结论正确性、推理完整性和连贯性'
    },
    'summary': {
        'name': '文本摘要',
        'script': 'evaluate_summary_quality.py',
        'output_dir': RESULTS_DIR / 'summary_quality',
        'enabled': True,
        'description': '评估文本摘要的ROUGE、BERTScore和压缩比'
    },
    'translation': {
        'name': '翻译',
        'script': 'evaluate_translation_quality.py',
        'output_dir': RESULTS_DIR / 'translation_quality',
        'enabled': True,
        'description': '评估翻译质量的BLEU、chrF和BERTScore'
    }
}


class EvaluationRunner:
    """评估运行器"""
    
    def __init__(self, verbose=False, skip_errors=False):
        self.verbose = verbose
        self.skip_errors = skip_errors
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def print_header(self):
        """打印标题"""
        print("\n" + "="*80)
        print("🚀 统一质量评估系统")
        print("="*80)
        print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 数据目录: {DATA_DIR}")
        print(f"📊 结果目录: {RESULTS_DIR}")
        print(f"🔧 脚本目录: {SCRIPTS_DIR}")
        print("="*80 + "\n")
    
    def print_task_info(self, task_id, config):
        """打印任务信息"""
        print(f"\n{'='*80}")
        print(f"📋 任务 [{task_id.upper()}]: {config['name']}")
        print(f"{'='*80}")
        print(f"📝 描述: {config['description']}")
        print(f"📜 脚本: {config['script']}")
        print(f"📁 输出: {config['output_dir']}")
        print(f"{'='*80}\n")
    
    def run_evaluation(self, task_id, config):
        """运行单个评估任务"""
        script_path = SCRIPTS_DIR / config['script']
        
        if not script_path.exists():
            print(f"❌ 脚本不存在: {script_path}")
            return False
        
        # 构建命令
        cmd = [
            sys.executable,
            str(script_path),
            '--data-dir', str(DATA_DIR),
            '--output-dir', str(config['output_dir'])
        ]
        
        # 添加任务特定参数
        if task_id == 'code':
            # 代码评估可以选择是否启用执行测试
            pass
        elif task_id == 'summary':
            # 摘要评估默认启用BERTScore
            cmd.extend(['--use-bertscore'])
        elif task_id == 'translation':
            # 翻译评估默认启用BERTScore
            pass
        elif task_id == 'reasoning':
            # 逻辑推理评估可以选择是否启用LLM-as-Judge
            pass
        
        try:
            # 运行评估脚本
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=600  # 10分钟超时
            )
            
            if self.verbose:
                print(result.stdout)
            
            if result.returncode == 0:
                print(f"✅ {config['name']}评估完成")
                return True
            else:
                print(f"❌ {config['name']}评估失败")
                print(f"错误信息: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  {config['name']}评估超时")
            return False
        except Exception as e:
            print(f"❌ {config['name']}评估异常: {e}")
            return False
    
    def run_all(self, tasks=None):
        """运行所有评估任务"""
        self.start_time = datetime.now()
        self.print_header()
        
        # 确定要运行的任务
        if tasks:
            tasks_to_run = {k: v for k, v in EVALUATION_TASKS.items() 
                           if k in tasks and v['enabled']}
        else:
            tasks_to_run = {k: v for k, v in EVALUATION_TASKS.items() 
                           if v['enabled']}
        
        print(f"📊 将运行 {len(tasks_to_run)} 个评估任务\n")
        
        # 运行每个任务
        for task_id, config in tasks_to_run.items():
            self.print_task_info(task_id, config)
            
            success = self.run_evaluation(task_id, config)
            self.results[task_id] = {
                'name': config['name'],
                'success': success,
                'output_dir': config['output_dir']
            }
            
            if not success and not self.skip_errors:
                print(f"\n⚠️  {config['name']}评估失败，停止后续任务")
                break
        
        self.end_time = datetime.now()
        self.print_summary()
    
    def print_summary(self):
        """打印评估摘要"""
        print("\n" + "="*80)
        print("📊 评估摘要")
        print("="*80)
        
        successful = sum(1 for r in self.results.values() if r['success'])
        failed = len(self.results) - successful
        
        print(f"\n✅ 成功: {successful} 个任务")
        print(f"❌ 失败: {failed} 个任务")
        
        print("\n详细结果:")
        print("-" * 80)
        for task_id, result in self.results.items():
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['name']:<15} -> {result['output_dir']}")
        
        duration = (self.end_time - self.start_time).total_seconds()
        print(f"\n⏱️  总耗时: {duration:.1f} 秒")
        print(f"📅 完成时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n" + "="*80)
        if failed == 0:
            print("🎉 所有评估任务完成!")
        else:
            print("⚠️  部分评估任务失败，请检查错误信息")
        print("="*80 + "\n")
        
        # 提示后续步骤
        if successful > 0:
            print("📌 后续步骤:")
            print("   1. 查看各任务的详细结果文件")
            print("   2. 运行可视化脚本生成图表:")
            print("      python data/analize/scripts/visualize_*.py")
            print("   3. 运行聚合脚本生成综合报告:")
            print("      python data/analize/scripts/aggregate_all_quality_results.py")
            print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='统一质量评估脚本 - 一键运行所有任务类型的质量评估',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行所有评估
  python run_all_evaluations.py
  
  # 运行特定任务
  python run_all_evaluations.py --tasks code math qa
  
  # 详细输出模式
  python run_all_evaluations.py --verbose
  
  # 跳过错误继续运行
  python run_all_evaluations.py --skip-errors
  
  # 列出所有可用任务
  python run_all_evaluations.py --list
        """
    )
    
    parser.add_argument('--tasks', nargs='+', 
                       choices=list(EVALUATION_TASKS.keys()),
                       help='指定要运行的任务类型')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='显示详细输出')
    parser.add_argument('--skip-errors', action='store_true',
                       help='遇到错误时继续运行后续任务')
    parser.add_argument('--list', '-l', action='store_true',
                       help='列出所有可用的评估任务')
    
    args = parser.parse_args()
    
    # 列出任务
    if args.list:
        print("\n可用的评估任务:")
        print("="*80)
        for task_id, config in EVALUATION_TASKS.items():
            status = "✅" if config['enabled'] else "❌"
            print(f"{status} {task_id:<12} - {config['name']:<15} - {config['description']}")
        print("="*80 + "\n")
        return
    
    # 运行评估
    runner = EvaluationRunner(
        verbose=args.verbose,
        skip_errors=args.skip_errors
    )
    
    runner.run_all(tasks=args.tasks)


if __name__ == '__main__':
    main()
