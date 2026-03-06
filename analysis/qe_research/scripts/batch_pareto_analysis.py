"""
批量帕累托前沿分析脚本

处理剩余任务：qa, summary, creative, translation
"""

import sys
from pathlib import Path
import subprocess

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 任务配置
TASKS = {
    'qa': {
        'quality_file': 'data/analize/results/qa_quality/qa_quality_summary.csv',
        'quality_metric': '综合得分',  # 需要确认实际列名
        'description': '问答任务'
    },
    'summary': {
        'quality_file': 'data/analize/results/summary_quality/summary_quality_summary.csv',
        'quality_metric': 'rouge_l',  # 需要确认实际列名
        'description': '摘要任务'
    },
    'creative': {
        'quality_file': 'data/analize/results/creative_quality/creative_quality_summary.csv',
        'quality_metric': 'distinct_2',  # 需要确认实际列名
        'description': '创意写作任务'
    },
    'translation': {
        'quality_file': 'data/analize/results/translation_quality/translation_quality_summary.csv',
        'quality_metric': 'bleu',  # 需要确认实际列名
        'description': '翻译任务'
    }
}

def check_data_files():
    """检查数据文件是否存在"""
    print("="*80)
    print("检查数据文件")
    print("="*80)
    
    for task, config in TASKS.items():
        quality_file = project_root / config['quality_file']
        exists = quality_file.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {task}: {quality_file}")
        
        if exists:
            import pandas as pd
            df = pd.read_csv(quality_file, nrows=2)
            print(f"  列数: {len(df.columns)}, 行数: {len(df)}")
    
    print()

def run_task_analysis(task):
    """运行单个任务的分析"""
    print(f"\n{'='*80}")
    print(f"分析任务: {task.upper()}")
    print(f"{'='*80}\n")
    
    script_path = project_root / 'analysis' / 'qe_research' / 'scripts' / f'pareto_analysis_{task}.py'
    
    if not script_path.exists():
        print(f"⚠ 脚本不存在: {script_path}")
        print(f"需要先创建脚本")
        return False
    
    # 运行脚本
    try:
        result = subprocess.run(
            ['python', str(script_path)],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✓ {task} 分析完成")
            return True
        else:
            print(f"✗ {task} 分析失败 (返回码: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"✗ 运行失败: {e}")
        return False

def main():
    """主函数"""
    print("\n" + "="*80)
    print("批量帕累托前沿分析")
    print("="*80)
    
    # 检查数据文件
    check_data_files()
    
    # 分析每个任务
    results = {}
    for task in TASKS.keys():
        success = run_task_analysis(task)
        results[task] = success
    
    # 总结
    print("\n" + "="*80)
    print("分析总结")
    print("="*80)
    
    for task, success in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {task}: {'完成' if success else '失败'}")
    
    total = len(results)
    completed = sum(results.values())
    print(f"\n完成: {completed}/{total}")

if __name__ == '__main__':
    main()
