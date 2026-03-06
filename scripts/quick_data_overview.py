"""
快速数据概览脚本

快速查看实验数据的基本情况，无需运行完整测试流程
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_header(title):
    """打印标题"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def check_json_data():
    """检查JSON数据"""
    print_header("1. JSON数据检查")
    
    try:
        from data.analize.pipeline.converters import SummaryJsonLoader
        
        loader = SummaryJsonLoader()
        available = loader.get_available_models()
        
        if not available:
            print("\n⚠ 未找到JSON数据")
            print("  请确保以下目录存在并包含 *_summary.json 文件:")
            print("  - data/deepseek_8b_ol_q4km/")
            print("  - data/qwen_8b_ol_q4km/")
            print("  - 等...")
            return None
        
        print(f"\n✓ 找到 {len(available)} 个模型目录:")
        for model in available:
            print(f"  - {model}")
        
        print("\n加载JSON数据...")
        df = loader.load_all_summary_data()
        
        print(f"✓ 加载成功: {len(df)} 条记录, {len(df.columns)} 列")
        
        return df
        
    except Exception as e:
        print(f"\n✗ 加载失败: {e}")
        return None


def check_processed_data():
    """检查已处理的数据"""
    print_header("2. 已处理数据检查")
    
    processed_file = Path('data/analize/processed/master_data.parquet')
    
    if not processed_file.exists():
        print("\n⚠ 未找到已处理的数据")
        print("  运行以下命令初始化数据管道:")
        print("  python scripts/test_and_explore_pipeline.py")
        return None
    
    try:
        df = pd.read_parquet(processed_file)
        file_size = processed_file.stat().st_size / 1024 / 1024
        
        print(f"\n✓ 找到已处理的数据")
        print(f"  - 文件: {processed_file}")
        print(f"  - 大小: {file_size:.2f} MB")
        print(f"  - 记录数: {len(df):,}")
        print(f"  - 列数: {len(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"\n✗ 读取失败: {e}")
        return None


def show_data_overview(df):
    """显示数据概览"""
    print_header("3. 数据概览")
    
    print("\n【基本信息】")
    print(f"  总记录数: {len(df):,}")
    print(f"  总列数: {len(df.columns)}")
    print(f"  内存使用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    # 数据类型分布
    print(f"\n【数据类型】")
    dtypes = df.dtypes.value_counts()
    for dtype, count in dtypes.items():
        print(f"  - {dtype}: {count} 列")
    
    # 模型信息
    if 'model_name' in df.columns:
        print(f"\n【模型信息】")
        models = df['model_name'].unique()
        print(f"  模型数量: {len(models)}")
        print(f"\n  各模型记录数:")
        model_counts = df['model_name'].value_counts().sort_index()
        for model, count in model_counts.items():
            print(f"    {model:30s}: {count:4d} 条")
    
    # 任务信息
    if 'task_type' in df.columns:
        print(f"\n【任务类型】")
        tasks = df['task_type'].unique()
        print(f"  任务数量: {len(tasks)}")
        print(f"\n  各任务记录数:")
        task_counts = df['task_type'].value_counts().sort_index()
        for task, count in task_counts.items():
            print(f"    {task:15s}: {count:4d} 条")


def show_available_metrics(df):
    """显示可用指标"""
    print_header("4. 可用指标")
    
    # 性能指标
    perf_metrics = {
        'latency_s': '延迟(秒)',
        'toks_per_s': '吞吐量(tokens/s)',
        'gpu_energy_j': 'GPU能耗(焦耳)',
        'ttft_s': '首token时间(秒)',
        'token_count': 'Token总数',
        'output_tokens': '输出Token数',
    }
    
    print("\n【性能指标】")
    found_perf = False
    for metric, desc in perf_metrics.items():
        if metric in df.columns:
            non_null = df[metric].notna().sum()
            print(f"  ✓ {metric:20s} - {desc:25s} ({non_null}/{len(df)} 有效)")
            found_perf = True
    
    if not found_perf:
        print("  ⚠ 未找到性能指标")
    
    # 资源指标
    resource_metrics = {
        'cpu_usage_avg': 'CPU使用率(%)',
        'memory_used_avg_mb': '内存使用(MB)',
        'gpu_util_avg': 'GPU利用率(%)',
        'gpu_memory_avg_mb': 'GPU显存(MB)',
        'gpu_power_avg_w': 'GPU功耗(W)',
        'gpu_temp_avg_c': 'GPU温度(°C)',
    }
    
    print("\n【资源指标】")
    found_resource = False
    for metric, desc in resource_metrics.items():
        if metric in df.columns:
            non_null = df[metric].notna().sum()
            print(f"  ✓ {metric:20s} - {desc:20s} ({non_null}/{len(df)} 有效)")
            found_resource = True
    
    if not found_resource:
        print("  ⚠ 未找到资源指标")
    
    # 质量指标
    quality_metrics = {
        'bartscore': 'BARTScore',
        'generated_text_length': '生成文本长度',
        'avg_response_length': '平均响应长度',
    }
    
    print("\n【质量指标】")
    found_quality = False
    for metric, desc in quality_metrics.items():
        if metric in df.columns:
            non_null = df[metric].notna().sum()
            print(f"  ✓ {metric:25s} - {desc:20s} ({non_null}/{len(df)} 有效)")
            found_quality = True
    
    if not found_quality:
        print("  ⚠ 未找到质量指标")


def show_quick_stats(df):
    """显示快速统计"""
    print_header("5. 快速统计")
    
    # 性能统计
    if 'latency_s' in df.columns:
        print("\n【延迟统计】")
        print(f"  平均: {df['latency_s'].mean():.2f}秒")
        print(f"  中位数: {df['latency_s'].median():.2f}秒")
        print(f"  最小: {df['latency_s'].min():.2f}秒")
        print(f"  最大: {df['latency_s'].max():.2f}秒")
    
    if 'toks_per_s' in df.columns:
        print("\n【吞吐量统计】")
        print(f"  平均: {df['toks_per_s'].mean():.2f} tokens/s")
        print(f"  中位数: {df['toks_per_s'].median():.2f} tokens/s")
        print(f"  最小: {df['toks_per_s'].min():.2f} tokens/s")
        print(f"  最大: {df['toks_per_s'].max():.2f} tokens/s")
    
    if 'gpu_energy_j' in df.columns:
        print("\n【GPU能耗统计】")
        print(f"  平均: {df['gpu_energy_j'].mean():.2f}焦耳")
        print(f"  中位数: {df['gpu_energy_j'].median():.2f}焦耳")
        print(f"  最小: {df['gpu_energy_j'].min():.2f}焦耳")
        print(f"  最大: {df['gpu_energy_j'].max():.2f}焦耳")
    
    # 按模型统计
    if 'model_name' in df.columns and 'latency_s' in df.columns:
        print("\n【各模型平均延迟】(前5名)")
        avg_latency = df.groupby('model_name')['latency_s'].mean().sort_values()
        for i, (model, latency) in enumerate(avg_latency.head(5).items(), 1):
            print(f"  {i}. {model:30s}: {latency:8.2f}秒")


def show_data_quality(df):
    """显示数据质量"""
    print_header("6. 数据质量")
    
    # 缺失值
    print("\n【缺失值】")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        '缺失数': missing,
        '缺失率(%)': missing_pct
    })
    missing_df = missing_df[missing_df['缺失数'] > 0].sort_values('缺失数', ascending=False)
    
    if len(missing_df) > 0:
        print(f"  发现 {len(missing_df)} 列有缺失值 (显示前10列):")
        for col, row in missing_df.head(10).iterrows():
            print(f"    {col:30s}: {int(row['缺失数']):4d} ({row['缺失率(%)']:5.1f}%)")
        if len(missing_df) > 10:
            print(f"    ... 还有 {len(missing_df) - 10} 列")
    else:
        print("  ✓ 无缺失值")
    
    # 重复值
    print("\n【重复值】")
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"  ⚠ 发现 {duplicates} 行重复数据")
    else:
        print("  ✓ 无重复数据")


def show_column_list(df):
    """显示列名列表"""
    print_header("7. 数据列列表")
    
    print(f"\n共 {len(df.columns)} 列:")
    
    # 按类别分组
    perf_cols = [col for col in df.columns if any(x in col for x in ['latency', 'toks', 'token', 'ttft'])]
    resource_cols = [col for col in df.columns if any(x in col for x in ['cpu', 'memory', 'gpu', 'mem'])]
    quality_cols = [col for col in df.columns if any(x in col for x in ['score', 'quality', 'length'])]
    meta_cols = [col for col in df.columns if col in ['model_name', 'task_type', 'experiment_id', 'model_dir', 'prompt_id', 'run_id']]
    other_cols = [col for col in df.columns if col not in perf_cols + resource_cols + quality_cols + meta_cols]
    
    if meta_cols:
        print(f"\n【元数据列】({len(meta_cols)})")
        for col in meta_cols:
            print(f"  - {col}")
    
    if perf_cols:
        print(f"\n【性能指标列】({len(perf_cols)})")
        for col in perf_cols:
            print(f"  - {col}")
    
    if resource_cols:
        print(f"\n【资源指标列】({len(resource_cols)})")
        for col in resource_cols:
            print(f"  - {col}")
    
    if quality_cols:
        print(f"\n【质量指标列】({len(quality_cols)})")
        for col in quality_cols:
            print(f"  - {col}")
    
    if other_cols:
        print(f"\n【其他列】({len(other_cols)})")
        for col in other_cols[:10]:
            print(f"  - {col}")
        if len(other_cols) > 10:
            print(f"  ... 还有 {len(other_cols) - 10} 列")


def main():
    """主函数"""
    print("="*70)
    print("  快速数据概览")
    print("="*70)
    
    # 优先检查已处理的数据
    df = check_processed_data()
    
    # 如果没有已处理的数据，尝试加载JSON
    if df is None:
        df = check_json_data()
    
    if df is None:
        print("\n" + "="*70)
        print("  无可用数据")
        print("="*70)
        print("\n建议:")
        print("  1. 确保实验数据存在于 data/*/ 目录")
        print("  2. 运行数据管道: python scripts/test_and_explore_pipeline.py")
        return 1
    
    # 显示概览
    show_data_overview(df)
    show_available_metrics(df)
    show_quick_stats(df)
    show_data_quality(df)
    show_column_list(df)
    
    print("\n" + "="*70)
    print("  概览完成")
    print("="*70)
    
    print("\n下一步:")
    print("  1. 运行完整测试: python scripts/test_and_explore_pipeline.py")
    print("  2. 进行深入分析: 使用数据管道API")
    print("  3. 生成可视化: cd data/analize/visualization/scripts")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
