#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
监控数据可视化工具
用于可视化实验过程中的详细硬件监控数据
"""

import json
import sys
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
import argparse

# 设置中文字体
def setup_chinese_font():
    """设置中文字体支持"""
    try:
        # Windows系统
        matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
        matplotlib.rcParams['axes.unicode_minus'] = False
        print("✓ 中文字体设置成功")
    except:
        print("⚠️  中文字体设置失败，将使用默认字体")


def load_experiment_data(json_file):
    """加载实验数据"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def plot_single_experiment(exp_data, output_dir=None):
    """
    为单个实验绘制详细监控图表
    
    Args:
        exp_data: 单个实验的数据字典
        output_dir: 输出目录，如果为None则显示图表
    """
    # 检查是否有详细监控数据
    if 'system_metrics_full' not in exp_data or exp_data['system_metrics_full'] is None:
        print(f"⚠️  实验 {exp_data.get('model', 'unknown')} 没有详细监控数据")
        return
    
    metrics = exp_data['system_metrics_full']
    model_name = exp_data.get('model_info', {}).get('display_name', exp_data.get('model', 'unknown'))
    task_type = exp_data.get('task_type', 'unknown')
    
    # 检查是否有时间戳
    if 'timestamps' not in metrics or not metrics['timestamps']:
        print(f"⚠️  实验 {model_name} 没有时间戳数据")
        return
    
    # 计算相对时间（秒）
    timestamps = metrics['timestamps']
    start_time = timestamps[0]
    relative_times = [(t - start_time) for t in timestamps]
    
    # 创建图表
    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle(f'硬件监控详情 - {model_name} ({task_type})', fontsize=16, fontweight='bold')
    
    # 1. CPU使用率
    ax = axes[0, 0]
    if 'cpu_percent' in metrics and metrics['cpu_percent']:
        ax.plot(relative_times, metrics['cpu_percent'], 'b-', linewidth=1.5, label='系统CPU')
        if 'cpu_proc_percent' in metrics and metrics['cpu_proc_percent']:
            ax.plot(relative_times, metrics['cpu_proc_percent'], 'r--', linewidth=1.5, label='Ollama进程')
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('CPU使用率 (%)')
        ax.set_title('CPU使用率')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_ylim(0, max(max(metrics['cpu_percent']), 100) * 1.1)
    
    # 2. 内存使用
    ax = axes[0, 1]
    if 'mem_used_mb' in metrics and metrics['mem_used_mb']:
        mem_gb = [m / 1024 for m in metrics['mem_used_mb']]
        ax.plot(relative_times, mem_gb, 'g-', linewidth=1.5)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('内存使用 (GB)')
        ax.set_title('内存使用')
        ax.grid(True, alpha=0.3)
        ax.fill_between(relative_times, mem_gb, alpha=0.3, color='g')
    
    # 3. GPU使用率
    ax = axes[1, 0]
    if 'gpu_util' in metrics and metrics['gpu_util']:
        ax.plot(relative_times, metrics['gpu_util'], 'purple', linewidth=1.5)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('GPU使用率 (%)')
        ax.set_title('GPU使用率')
        ax.grid(True, alpha=0.3)
        ax.fill_between(relative_times, metrics['gpu_util'], alpha=0.3, color='purple')
        ax.set_ylim(0, 105)
    
    # 4. GPU显存
    ax = axes[1, 1]
    if 'gpu_mem_mb' in metrics and metrics['gpu_mem_mb']:
        gpu_mem_gb = [m / 1024 for m in metrics['gpu_mem_mb']]
        ax.plot(relative_times, gpu_mem_gb, 'orange', linewidth=1.5)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('GPU显存 (GB)')
        ax.set_title('GPU显存使用')
        ax.grid(True, alpha=0.3)
        ax.fill_between(relative_times, gpu_mem_gb, alpha=0.3, color='orange')
    
    # 5. GPU功耗
    ax = axes[2, 0]
    if 'gpu_power_w' in metrics and metrics['gpu_power_w']:
        ax.plot(relative_times, metrics['gpu_power_w'], 'red', linewidth=1.5)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('GPU功耗 (W)')
        ax.set_title('GPU功耗')
        ax.grid(True, alpha=0.3)
        ax.fill_between(relative_times, metrics['gpu_power_w'], alpha=0.3, color='red')
        
        # 添加平均功耗线
        avg_power = sum(metrics['gpu_power_w']) / len(metrics['gpu_power_w'])
        ax.axhline(y=avg_power, color='darkred', linestyle='--', linewidth=2, 
                   label=f'平均: {avg_power:.1f}W')
        ax.legend()
    
    # 6. GPU温度
    ax = axes[2, 1]
    if 'gpu_temp_c' in metrics and metrics['gpu_temp_c']:
        ax.plot(relative_times, metrics['gpu_temp_c'], 'darkred', linewidth=1.5)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('GPU温度 (°C)')
        ax.set_title('GPU温度')
        ax.grid(True, alpha=0.3)
        ax.fill_between(relative_times, metrics['gpu_temp_c'], alpha=0.3, color='darkred')
        
        # 添加温度警戒线
        ax.axhline(y=80, color='orange', linestyle='--', linewidth=1, alpha=0.5, label='警戒温度')
        ax.legend()
    
    plt.tight_layout()
    
    # 保存或显示
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        safe_model_name = model_name.replace(':', '_').replace('/', '_')
        filename = f"monitoring_{safe_model_name}_{task_type}.png"
        filepath = output_path / filename
        
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ 图表已保存: {filepath}")
        plt.close()
    else:
        plt.show()


def plot_comparison(experiments, output_dir=None):
    """
    对比多个实验的关键指标
    
    Args:
        experiments: 实验数据列表
        output_dir: 输出目录
    """
    # 提取有详细监控数据的实验
    valid_exps = [exp for exp in experiments 
                  if 'system_metrics_full' in exp and exp['system_metrics_full'] is not None
                  and 'timestamps' in exp['system_metrics_full'] 
                  and exp['system_metrics_full']['timestamps']]
    
    if not valid_exps:
        print("⚠️  没有找到有效的详细监控数据")
        return
    
    # 创建对比图表
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('多实验对比 - 关键指标', fontsize=16, fontweight='bold')
    
    colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'pink', 'gray']
    
    for idx, exp in enumerate(valid_exps):
        metrics = exp['system_metrics_full']
        model_name = exp.get('model_info', {}).get('display_name', exp.get('model', f'Model {idx+1}'))
        color = colors[idx % len(colors)]
        
        # 计算相对时间
        timestamps = metrics['timestamps']
        start_time = timestamps[0]
        relative_times = [(t - start_time) for t in timestamps]
        
        # 1. CPU使用率对比
        ax = axes[0, 0]
        if 'cpu_percent' in metrics and metrics['cpu_percent']:
            ax.plot(relative_times, metrics['cpu_percent'], color=color, 
                   linewidth=1.5, label=model_name, alpha=0.7)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('CPU使用率 (%)')
        ax.set_title('CPU使用率对比')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        
        # 2. GPU使用率对比
        ax = axes[0, 1]
        if 'gpu_util' in metrics and metrics['gpu_util']:
            ax.plot(relative_times, metrics['gpu_util'], color=color, 
                   linewidth=1.5, label=model_name, alpha=0.7)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('GPU使用率 (%)')
        ax.set_title('GPU使用率对比')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        
        # 3. GPU显存对比
        ax = axes[1, 0]
        if 'gpu_mem_mb' in metrics and metrics['gpu_mem_mb']:
            gpu_mem_gb = [m / 1024 for m in metrics['gpu_mem_mb']]
            ax.plot(relative_times, gpu_mem_gb, color=color, 
                   linewidth=1.5, label=model_name, alpha=0.7)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('GPU显存 (GB)')
        ax.set_title('GPU显存对比')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        
        # 4. GPU功耗对比
        ax = axes[1, 1]
        if 'gpu_power_w' in metrics and metrics['gpu_power_w']:
            ax.plot(relative_times, metrics['gpu_power_w'], color=color, 
                   linewidth=1.5, label=model_name, alpha=0.7)
        ax.set_xlabel('时间 (秒)')
        ax.set_ylabel('GPU功耗 (W)')
        ax.set_title('GPU功耗对比')
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    
    plt.tight_layout()
    
    # 保存或显示
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        filepath = output_path / "monitoring_comparison.png"
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"✓ 对比图表已保存: {filepath}")
        plt.close()
    else:
        plt.show()


def print_summary(experiments):
    """打印实验汇总信息"""
    print("\n" + "="*70)
    print("实验监控数据汇总")
    print("="*70)
    
    for idx, exp in enumerate(experiments, 1):
        model_name = exp.get('model_info', {}).get('display_name', exp.get('model', 'unknown'))
        task_type = exp.get('task_type', 'unknown')
        
        print(f"\n[{idx}] {model_name} - {task_type}")
        
        if 'system_metrics_summary' in exp:
            summary = exp['system_metrics_summary']
            print(f"  CPU: 平均 {summary.get('cpu_percent_avg', 0):.1f}%, 峰值 {summary.get('cpu_percent_peak', 0):.1f}%")
            print(f"  内存: 峰值 {summary.get('mem_used_peak_mb', 0):.1f} MB")
            print(f"  GPU使用率: 平均 {summary.get('gpu_util_avg', 0):.1f}%, 峰值 {summary.get('gpu_util_peak', 0):.1f}%")
            print(f"  GPU显存: 峰值 {summary.get('gpu_mem_peak_mb', 0):.1f} MB")
            print(f"  GPU功耗: 平均 {summary.get('gpu_power_avg_w', 0):.1f} W")
            print(f"  GPU能耗: {summary.get('gpu_energy_j', 0):.2f} J")
            print(f"  GPU温度: 峰值 {summary.get('gpu_temp_peak_c', 0):.0f} °C")
        
        if 'system_metrics_full' in exp and exp['system_metrics_full']:
            metrics = exp['system_metrics_full']
            if 'timestamps' in metrics and metrics['timestamps']:
                duration = metrics['timestamps'][-1] - metrics['timestamps'][0]
                sample_count = len(metrics['timestamps'])
                print(f"  监控时长: {duration:.2f} 秒")
                print(f"  采样点数: {sample_count}")
        
        if 'performance' in exp:
            perf = exp['performance']
            print(f"  生成耗时: {perf.get('total_time_seconds', 0):.2f} 秒")
            print(f"  吞吐量: {perf.get('throughput_tokens_per_sec', 0):.2f} tokens/s")
    
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(
        description="可视化实验监控数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 可视化单个实验文件
  python scripts/visualize_monitoring_data.py data/test/experiment_results.json
  
  # 保存图表到指定目录
  python scripts/visualize_monitoring_data.py data/test/experiment_results.json --output results/figures
  
  # 只显示汇总信息
  python scripts/visualize_monitoring_data.py data/test/experiment_results.json --summary-only
  
  # 生成对比图表
  python scripts/visualize_monitoring_data.py data/test/experiment_results.json --comparison
        """
    )
    
    parser.add_argument("json_file", help="实验结果JSON文件路径")
    parser.add_argument("--output", "-o", help="输出目录（如果不指定则显示图表）")
    parser.add_argument("--summary-only", "-s", action="store_true", help="只显示汇总信息，不生成图表")
    parser.add_argument("--comparison", "-c", action="store_true", help="生成对比图表")
    parser.add_argument("--index", "-i", type=int, help="只可视化指定索引的实验（从0开始）")
    
    args = parser.parse_args()
    
    # 设置中文字体
    setup_chinese_font()
    
    # 加载数据
    print(f"加载实验数据: {args.json_file}")
    experiments = load_experiment_data(args.json_file)
    
    # 确保是列表格式
    if isinstance(experiments, dict):
        experiments = [experiments]
    
    print(f"✓ 加载了 {len(experiments)} 个实验")
    
    # 打印汇总信息
    print_summary(experiments)
    
    if args.summary_only:
        return 0
    
    # 生成图表
    if args.index is not None:
        # 只可视化指定的实验
        if 0 <= args.index < len(experiments):
            print(f"\n可视化实验 #{args.index}")
            plot_single_experiment(experiments[args.index], args.output)
        else:
            print(f"❌ 错误: 索引 {args.index} 超出范围 (0-{len(experiments)-1})")
            return 1
    elif args.comparison:
        # 生成对比图表
        print("\n生成对比图表...")
        plot_comparison(experiments, args.output)
    else:
        # 为每个实验生成图表
        print("\n生成详细监控图表...")
        for idx, exp in enumerate(experiments):
            print(f"\n处理实验 {idx+1}/{len(experiments)}")
            plot_single_experiment(exp, args.output)
    
    print("\n✓ 完成!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
