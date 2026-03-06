"""
数据管道测试和探索性分析脚本

功能：
1. 测试数据管道系统
2. 加载所有实验数据
3. 进行初步的探索性分析
4. 生成数据概览报告
"""
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data/analize/logs/pipeline_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 确保日志目录存在
Path('data/analize/logs').mkdir(parents=True, exist_ok=True)


def print_section(title):
    """打印章节标题"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_json_loaders():
    """测试JSON加载器"""
    print_section("步骤1: 测试JSON加载器")
    
    try:
        from data.analize.pipeline.converters import SummaryJsonLoader
        
        loader = SummaryJsonLoader()
        
        # 列出可用模型
        available = loader.get_available_models()
        print(f"\n✓ 找到 {len(available)} 个模型目录:")
        for model in available:
            print(f"  - {model}")
        
        if not available:
            print("\n⚠ 警告: 未找到任何模型数据")
            print("  请确保以下目录存在并包含 *_summary.json 文件:")
            print("  - data/deepseek_8b_ol_q4km/")
            print("  - data/qwen_8b_ol_q4km/")
            print("  - data/gemma_4b_ol_q4km/")
            print("  - 等...")
            return False
        
        # 加载数据
        print("\n加载JSON数据...")
        df = loader.load_all_summary_data()
        
        print(f"\n✓ JSON数据加载成功")
        print(f"  - 总记录数: {len(df)}")
        print(f"  - 总列数: {len(df.columns)}")
        
        return True
        
    except Exception as e:
        logger.error(f"JSON加载器测试失败: {e}", exc_info=True)
        print(f"\n✗ JSON加载器测试失败: {e}")
        return False


def initialize_pipeline():
    """初始化数据管道"""
    print_section("步骤2: 初始化数据管道")
    
    try:
        from data.analize.pipeline import ExperimentDataManager
        
        print("\n创建数据管理器...")
        dm = ExperimentDataManager()
        
        # 检查是否已有处理后的数据
        processed_file = Path('data/analize/processed/master_data.parquet')
        
        if processed_file.exists():
            print(f"\n✓ 发现已处理的数据: {processed_file}")
            response = input("是否重新运行数据管道？(y/n，建议首次运行选y): ").lower()
            
            if response == 'y':
                print("\n运行完整数据管道...")
                dm.initialize_pipeline(force=True)
                print("\n✓ 数据管道运行完成")
            else:
                print("\n⊙ 跳过数据管道，使用现有数据")
        else:
            print("\n首次运行，执行完整数据管道...")
            dm.initialize_pipeline()
            print("\n✓ 数据管道运行完成")
        
        return dm
        
    except Exception as e:
        logger.error(f"数据管道初始化失败: {e}", exc_info=True)
        print(f"\n✗ 数据管道初始化失败: {e}")
        return None


def load_and_validate_data(dm):
    """加载和验证数据"""
    print_section("步骤3: 加载和验证数据")
    
    try:
        print("\n加载所有数据...")
        df = dm.load_all_data()
        
        print(f"\n✓ 数据加载成功")
        print(f"  - 数据形状: {df.shape}")
        print(f"  - 内存使用: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
        
        # 验证数据
        print("\n验证数据完整性...")
        is_valid = dm.validate_data()
        
        if is_valid:
            print("✓ 数据验证通过")
        else:
            print("⚠ 数据验证发现问题（详见上方）")
        
        return df
        
    except Exception as e:
        logger.error(f"数据加载失败: {e}", exc_info=True)
        print(f"\n✗ 数据加载失败: {e}")
        return None


def explore_data_overview(df, dm):
    """数据概览"""
    print_section("步骤4: 数据概览")
    
    # 基本信息
    print("\n【基本信息】")
    print(f"  总记录数: {len(df):,}")
    print(f"  总列数: {len(df.columns)}")
    print(f"  数据类型分布:")
    print(f"    - 数值型: {len(df.select_dtypes(include=[np.number]).columns)}")
    print(f"    - 分类型: {len(df.select_dtypes(include=['category']).columns)}")
    print(f"    - 对象型: {len(df.select_dtypes(include=['object']).columns)}")
    
    # 模型信息
    print("\n【模型信息】")
    models = dm.list_models()
    print(f"  模型数量: {len(models)}")
    print(f"  模型列表:")
    for model in models:
        count = len(df[df['model_name'] == model]) if 'model_name' in df.columns else 0
        print(f"    - {model}: {count} 条记录")
    
    # 任务信息
    print("\n【任务类型】")
    tasks = dm.list_tasks()
    print(f"  任务数量: {len(tasks)}")
    print(f"  任务列表:")
    for task in tasks:
        count = len(df[df['task_type'] == task]) if 'task_type' in df.columns else 0
        print(f"    - {task}: {count} 条记录")
    
    # 列名
    print(f"\n【数据列 ({len(df.columns)})】")
    print("  前20列:")
    for i, col in enumerate(df.columns[:20], 1):
        print(f"    {i:2d}. {col}")
    if len(df.columns) > 20:
        print(f"    ... 还有 {len(df.columns) - 20} 列")


def explore_performance_metrics(df):
    """性能指标探索"""
    print_section("步骤5: 性能指标分析")
    
    # 检查关键性能指标
    perf_metrics = {
        'latency_s': '延迟(秒)',
        'toks_per_s': '吞吐量(tokens/s)',
        'gpu_energy_j': 'GPU能耗(焦耳)',
        'ttft_s': '首token时间(秒)',
        'token_count': 'Token总数',
    }
    
    available_metrics = {k: v for k, v in perf_metrics.items() if k in df.columns}
    
    if not available_metrics:
        print("\n⚠ 未找到性能指标列")
        return
    
    print(f"\n【可用性能指标】({len(available_metrics)}个)")
    for metric, desc in available_metrics.items():
        print(f"  ✓ {metric} - {desc}")
    
    # 统计分析
    print("\n【性能指标统计】")
    stats_df = df[list(available_metrics.keys())].describe()
    print(stats_df.to_string())
    
    # 按模型统计
    if 'model_name' in df.columns and 'latency_s' in df.columns:
        print("\n【各模型平均延迟】")
        avg_latency = df.groupby('model_name')['latency_s'].mean().sort_values()
        for model, latency in avg_latency.items():
            print(f"  {model:30s}: {latency:8.2f}秒")
    
    if 'model_name' in df.columns and 'toks_per_s' in df.columns:
        print("\n【各模型平均吞吐量】")
        avg_throughput = df.groupby('model_name')['toks_per_s'].mean().sort_values(ascending=False)
        for model, throughput in avg_throughput.items():
            print(f"  {model:30s}: {throughput:8.2f} tokens/s")
    
    if 'model_name' in df.columns and 'gpu_energy_j' in df.columns:
        print("\n【各模型平均能耗】")
        avg_energy = df.groupby('model_name')['gpu_energy_j'].mean().sort_values()
        for model, energy in avg_energy.items():
            print(f"  {model:30s}: {energy:10.2f}焦耳")


def explore_resource_usage(df):
    """资源使用探索"""
    print_section("步骤6: 资源使用分析")
    
    # 检查资源指标
    resource_metrics = {
        'cpu_usage_avg': 'CPU使用率(%)',
        'memory_used_avg_mb': '内存使用(MB)',
        'gpu_util_avg': 'GPU利用率(%)',
        'gpu_memory_avg_mb': 'GPU显存(MB)',
        'gpu_power_avg_w': 'GPU功耗(W)',
        'gpu_temp_avg_c': 'GPU温度(°C)',
    }
    
    available_metrics = {k: v for k, v in resource_metrics.items() if k in df.columns}
    
    if not available_metrics:
        print("\n⚠ 未找到资源使用指标")
        return
    
    print(f"\n【可用资源指标】({len(available_metrics)}个)")
    for metric, desc in available_metrics.items():
        print(f"  ✓ {metric} - {desc}")
    
    # 统计分析
    print("\n【资源使用统计】")
    stats_df = df[list(available_metrics.keys())].describe()
    print(stats_df.to_string())
    
    # 按模型统计GPU利用率
    if 'model_name' in df.columns and 'gpu_util_avg' in df.columns:
        print("\n【各模型平均GPU利用率】")
        avg_gpu = df.groupby('model_name')['gpu_util_avg'].mean().sort_values(ascending=False)
        for model, util in avg_gpu.items():
            print(f"  {model:30s}: {util:6.2f}%")


def explore_quality_metrics(df):
    """质量指标探索"""
    print_section("步骤7: 质量指标分析")
    
    # 检查质量指标
    quality_metrics = {
        'bartscore': 'BARTScore',
        'generated_text_length': '生成文本长度',
        'avg_response_length': '平均响应长度',
    }
    
    available_metrics = {k: v for k, v in quality_metrics.items() if k in df.columns}
    
    if not available_metrics:
        print("\n⚠ 未找到质量指标")
        return
    
    print(f"\n【可用质量指标】({len(available_metrics)}个)")
    for metric, desc in available_metrics.items():
        print(f"  ✓ {metric} - {desc}")
    
    # 统计分析
    print("\n【质量指标统计】")
    stats_df = df[list(available_metrics.keys())].describe()
    print(stats_df.to_string())


def explore_task_distribution(df):
    """任务分布探索"""
    print_section("步骤8: 任务分布分析")
    
    if 'task_type' not in df.columns or 'model_name' not in df.columns:
        print("\n⚠ 缺少必要的列")
        return
    
    # 任务-模型交叉表
    print("\n【任务-模型分布】")
    cross_tab = pd.crosstab(df['task_type'], df['model_name'])
    print(cross_tab.to_string())
    
    # 按任务统计
    print("\n【各任务平均性能】")
    if 'latency_s' in df.columns:
        print("\n延迟(秒):")
        task_latency = df.groupby('task_type')['latency_s'].mean().sort_values()
        for task, latency in task_latency.items():
            print(f"  {task:15s}: {latency:8.2f}")
    
    if 'gpu_energy_j' in df.columns:
        print("\nGPU能耗(焦耳):")
        task_energy = df.groupby('task_type')['gpu_energy_j'].mean().sort_values()
        for task, energy in task_energy.items():
            print(f"  {task:15s}: {energy:10.2f}")


def explore_data_quality(df):
    """数据质量检查"""
    print_section("步骤9: 数据质量检查")
    
    # 缺失值
    print("\n【缺失值统计】")
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        '缺失数': missing,
        '缺失率(%)': missing_pct
    })
    missing_df = missing_df[missing_df['缺失数'] > 0].sort_values('缺失数', ascending=False)
    
    if len(missing_df) > 0:
        print(f"\n发现 {len(missing_df)} 列有缺失值:")
        print(missing_df.head(20).to_string())
        if len(missing_df) > 20:
            print(f"... 还有 {len(missing_df) - 20} 列")
    else:
        print("\n✓ 无缺失值")
    
    # 重复值
    print("\n【重复值检查】")
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"⚠ 发现 {duplicates} 行重复数据")
    else:
        print("✓ 无重复数据")
    
    # 数据范围异常
    print("\n【数值范围检查】")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    issues = []
    for col in numeric_cols:
        if col.endswith('_avg') or col.endswith('_peak'):
            # 检查负值
            if (df[col] < 0).any():
                issues.append(f"  ⚠ {col}: 存在负值")
        
        # 检查极端值
        if df[col].std() > 0:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers = (z_scores > 3).sum()
            if outliers > len(df) * 0.05:  # 超过5%
                issues.append(f"  ⚠ {col}: {outliers} 个极端值 (>3σ)")
    
    if issues:
        print("\n发现以下问题:")
        for issue in issues[:10]:
            print(issue)
        if len(issues) > 10:
            print(f"... 还有 {len(issues) - 10} 个问题")
    else:
        print("✓ 数值范围正常")


def generate_summary_report(df, dm):
    """生成总结报告"""
    print_section("步骤10: 生成总结报告")
    
    report_path = Path('data/analize/logs/pipeline_test_report.md')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 数据管道测试和探索性分析报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 数据概览\n\n")
        f.write(f"- 总记录数: {len(df):,}\n")
        f.write(f"- 总列数: {len(df.columns)}\n")
        f.write(f"- 模型数量: {len(dm.list_models())}\n")
        f.write(f"- 任务类型: {len(dm.list_tasks())}\n\n")
        
        f.write("## 2. 模型列表\n\n")
        for model in dm.list_models():
            count = len(df[df['model_name'] == model]) if 'model_name' in df.columns else 0
            f.write(f"- {model}: {count} 条记录\n")
        
        f.write("\n## 3. 任务类型\n\n")
        for task in dm.list_tasks():
            count = len(df[df['task_type'] == task]) if 'task_type' in df.columns else 0
            f.write(f"- {task}: {count} 条记录\n")
        
        f.write("\n## 4. 可用指标\n\n")
        f.write(f"### 性能指标\n\n")
        perf_cols = ['latency_s', 'toks_per_s', 'gpu_energy_j', 'ttft_s']
        for col in perf_cols:
            if col in df.columns:
                f.write(f"- ✓ {col}\n")
        
        f.write(f"\n### 资源指标\n\n")
        resource_cols = ['cpu_usage_avg', 'memory_used_avg_mb', 'gpu_util_avg', 'gpu_memory_avg_mb']
        for col in resource_cols:
            if col in df.columns:
                f.write(f"- ✓ {col}\n")
        
        f.write("\n## 5. 数据质量\n\n")
        missing = df.isnull().sum().sum()
        duplicates = df.duplicated().sum()
        f.write(f"- 缺失值总数: {missing}\n")
        f.write(f"- 重复行数: {duplicates}\n")
        
        f.write("\n## 6. 下一步建议\n\n")
        f.write("1. 运行综合分析脚本进行深入分析\n")
        f.write("2. 生成可视化图表\n")
        f.write("3. 计算质效比指标\n")
        f.write("4. 生成模型评估报告\n")
    
    print(f"\n✓ 报告已生成: {report_path}")


def main():
    """主函数"""
    print("="*80)
    print("  数据管道测试和探索性分析")
    print("="*80)
    print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 测试JSON加载器
        if not test_json_loaders():
            print("\n⚠ JSON加载器测试失败，但继续执行...")
        
        input("\n按回车继续...")
        
        # 2. 初始化数据管道
        dm = initialize_pipeline()
        if dm is None:
            print("\n✗ 数据管道初始化失败，无法继续")
            return 1
        
        input("\n按回车继续...")
        
        # 3. 加载和验证数据
        df = load_and_validate_data(dm)
        if df is None:
            print("\n✗ 数据加载失败，无法继续")
            return 1
        
        input("\n按回车继续...")
        
        # 4-9. 探索性分析
        explore_data_overview(df, dm)
        input("\n按回车继续...")
        
        explore_performance_metrics(df)
        input("\n按回车继续...")
        
        explore_resource_usage(df)
        input("\n按回车继续...")
        
        explore_quality_metrics(df)
        input("\n按回车继续...")
        
        explore_task_distribution(df)
        input("\n按回车继续...")
        
        explore_data_quality(df)
        input("\n按回车继续...")
        
        # 10. 生成报告
        generate_summary_report(df, dm)
        
        print_section("完成")
        print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n✓ 所有测试和分析完成！")
        print("\n查看详细报告: data/analize/logs/pipeline_test_report.md")
        print("查看日志: data/analize/logs/pipeline_test.log")
        
        return 0
        
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        print(f"\n✗ 执行失败: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
