"""
修复质量数据格式的工具脚本

将统计格式的CSV转换为标准格式（model列 + 质量指标列）
"""

import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 任务配置
TASKS = {
    'qa': {
        'input': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'qa_quality' / 'qa_quality_summary.csv',
        'output': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'qa_quality' / 'qa_quality_processed.csv',
        'quality_metric': 'has_answer'  # 使用has_answer的mean值作为质量指标
    },
    'summary': {
        'input': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'summary_quality' / 'summary_quality_summary.csv',
        'output': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'summary_quality' / 'summary_quality_processed.csv',
        'quality_metric': 'rouge_l_f1'  # 使用ROUGE-L F1作为质量指标
    },
    'translation': {
        'input': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'translation_quality' / 'translation_quality_summary.csv',
        'output': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'translation_quality' / 'translation_quality_processed.csv',
        'quality_metric': 'bleu_1'  # 使用BLEU-1作为质量指标
    },
    'math': {
        'input': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'math_quality' / 'math_quality_summary.csv',
        'output': PROJECT_ROOT / 'data' / 'analize' / 'results' / 'math_quality' / 'math_quality_processed.csv',
        'quality_metric': 'numerical_match'  # 使用数值匹配作为质量指标
    }
}


def process_quality_file(input_file, output_file, quality_metric):
    """
    处理质量数据文件
    
    输入格式：
    - 第一行：统计类型（mean, std, min, max）
    - 第二行开始：模型数据
    - 'Unnamed: 0'列包含模型名称
    
    输出格式：
    - model列：模型名称
    - quality列：质量得分（使用指定指标的mean值）
    """
    print(f"\n处理文件: {input_file.name}")
    
    # 读取原始数据
    df = pd.read_csv(input_file)
    
    # 跳过第一行（统计类型行），从第二行开始读取
    df = df.iloc[1:].reset_index(drop=True)
    
    # 提取模型名称
    models = df['Unnamed: 0'].values
    
    # 提取质量指标（mean值）
    if quality_metric not in df.columns:
        print(f"  ⚠️ 警告: 找不到列 '{quality_metric}'")
        print(f"  可用列: {df.columns.tolist()[:10]}")
        # 尝试找到第一个数值列
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            quality_metric = numeric_cols[0]
            print(f"  使用替代列: {quality_metric}")
    
    quality_values = pd.to_numeric(df[quality_metric], errors='coerce').values
    
    # 创建标准格式的DataFrame
    processed_df = pd.DataFrame({
        'model': models,
        'quality': quality_values
    })
    
    # 移除NaN值
    processed_df = processed_df.dropna()
    
    # 保存处理后的数据
    output_file.parent.mkdir(parents=True, exist_ok=True)
    processed_df.to_csv(output_file, index=False)
    
    print(f"  ✓ 处理完成: {len(processed_df)} 个模型")
    print(f"  ✓ 质量范围: {processed_df['quality'].min():.4f} - {processed_df['quality'].max():.4f}")
    print(f"  ✓ 输出文件: {output_file}")
    
    return processed_df


def main():
    """处理所有任务的质量数据"""
    print("="*80)
    print("质量数据格式修复工具")
    print("="*80)
    
    results = {}
    
    for task_name, config in TASKS.items():
        try:
            if not config['input'].exists():
                print(f"\n❌ {task_name}: 输入文件不存在 - {config['input']}")
                continue
            
            df = process_quality_file(
                config['input'],
                config['output'],
                config['quality_metric']
            )
            results[task_name] = df
            
        except Exception as e:
            print(f"\n❌ {task_name}: 处理失败 - {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("处理完成")
    print("="*80)
    
    print(f"\n成功处理: {len(results)}/{len(TASKS)} 个任务")
    for task_name in results:
        print(f"  ✓ {task_name}")
    
    failed = set(TASKS.keys()) - set(results.keys())
    if failed:
        print(f"\n失败任务: {len(failed)}")
        for task_name in failed:
            print(f"  ❌ {task_name}")


if __name__ == '__main__':
    main()
