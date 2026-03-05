#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合分析脚本：整合质量评估和性能数据
生成多维度模型评估报告

使用方法:
    python scripts/comprehensive_analysis.py
    python scripts/comprehensive_analysis.py --experiment experiments_2
    python scripts/comprehensive_analysis.py --output-dir data/analysis_v2
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import argparse
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 任务类型映射
TASK_MAPPING = {
    'qa': 'qa',
    'question_answering': 'qa',
    'math': 'math',
    'mathematical_reasoning': 'math',
    'code': 'code',
    'code_generation': 'code',
    'creative': 'creative',
    'creative_writing': 'creative',
    'reasoning': 'reasoning',
    'logical_reasoning': 'reasoning',
    'summary': 'summary',
    'summarization': 'summary',
    'translation': 'translation'
}

def standardize_model_name(name: str) -> str:
    """标准化模型名称"""
    if pd.isna(name):
        return name
    name = str(name).lower()
    name = name.replace(':', '_').replace('-', '_')
    return name


def integrate_quality_and_performance(
    quality_dir: Path,
    performance_file: Path,
    output_file: Path
) -> pd.DataFrame:
    """整合质量和性能数据"""
    
    print("  📂 加载质量评估数据...")
    quality_data = []
    
    # 加载所有任务的质量数据
    for task in ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']:
        summary_file = quality_dir / f"{task}_quality" / f"{task}_quality_summary.csv"
        if summary_file.exists():
            try:
                df = pd.read_csv(summary_file, encoding='utf-8')
                df['task_type'] = task
                quality_data.append(df)
                print(f"    ✓ {task}: {len(df)} 条记录")
            except Exception as e:
                print(f"    ✗ {task}: 加载失败 - {e}")
        else:
            print(f"    ⚠ {task}: 文件不存在")
    
    if not quality_data:
        raise ValueError("未找到任何质量评估数据")
    
    quality_df = pd.concat(quality_data, ignore_index=True)
    print(f"  ✅ 质量数据加载完成: {len(quality_df)} 条记录\n")
    
    # 加载性能数据
    print("  📂 加载性能实验数据...")
    if not performance_file.exists():
        raise FileNotFoundError(f"性能数据文件不存在: {performance_file}")
    
    performance_df = pd.read_csv(performance_file, encoding='utf-8')
    print(f"  ✅ 性能数据加载完成: {len(performance_df)} 条记录\n")
    
    # 标准化模型名称和任务类型
    print("  🔄 标准化数据...")
    quality_df['model'] = quality_df['model'].apply(standardize_model_name)
    performance_df['model'] = performance_df['model'].apply(standardize_model_name)
    
    # 映射任务类型
    if 'task' in performance_df.columns:
        performance_df['task_type'] = performance_df['task'].map(TASK_MAPPING)
    elif 'task_type' not in performance_df.columns:
        print("  ⚠ 警告: 性能数据缺少task或task_type列")
    
    # 合并数据
    print("  🔗 合并数据...")
    merged_df = pd.merge(
        quality_df,
        performance_df,
        on=['model', 'task_type'],
        how='inner',
        suffixes=('_quality', '_performance')
    )
    
    print(f"  ✅ 数据整合完成: {len(merged_df)} 条记录")
    print(f"     - 模型数: {merged_df['model'].nunique()}")
    print(f"     - 任务数: {merged_df['task_type'].nunique()}\n")
    
    # 保存整合数据
    merged_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"  💾 已保存: {output_file}\n")
    
    return merged_df


def normalize_by_task(df: pd.DataFrame, metrics: list) -> pd.DataFrame:
    """按任务类型归一化指标"""
    df_norm = df.copy()
    
    # 定义指标方向 (True=越大越好, False=越小越好)
    metric_directions = {
        'quality_score': True,
        'toks_per_s': True,
        'throughput': True,
        'latency_s': False,
        'gpu_energy_j': False,
        'e_token_j': False,
        'ttft_s': False,
        'tpot_s': False
    }
    
    for task in df['task_type'].unique():
        task_mask = df['task_type'] == task
        
        for metric in metrics:
            if metric not in df.columns:
                continue
            
            values = df.loc[task_mask, metric]
            if values.isna().all():
                continue
            
            min_val, max_val = values.min(), values.max()
            if max_val == min_val:
                df_norm.loc[task_mask, f'{metric}_norm'] = 0.5
                continue
            
            # 判断指标方向
            is_higher_better = metric_directions.get(metric, True)
            
            if is_higher_better:
                # 越大越好
                df_norm.loc[task_mask, f'{metric}_norm'] = \
                    (values - min_val) / (max_val - min_val)
            else:
                # 越小越好 (反转)
                df_norm.loc[task_mask, f'{metric}_norm'] = \
                    1 - (values - min_val) / (max_val - min_val)
    
    return df_norm


def calculate_efficiency_score(df: pd.DataFrame) -> pd.DataFrame:
    """计算效率得分"""
    required_cols = ['toks_per_s_norm', 'latency_s_norm', 'gpu_energy_j_norm']
    
    if all(col in df.columns for col in required_cols):
        df['efficiency_score'] = (
            0.4 * df['toks_per_s_norm'] +
            0.3 * df['latency_s_norm'] +
            0.3 * df['gpu_energy_j_norm']
        )
    else:
        print("  ⚠ 警告: 缺少计算效率得分所需的列")
        df['efficiency_score'] = np.nan
    
    return df


def calculate_qe_ratio(df: pd.DataFrame, epsilon=0.01) -> pd.DataFrame:
    """计算质效比"""
    if 'quality_score_norm' in df.columns and 'efficiency_score' in df.columns:
        df['qe_ratio'] = (
            (df['quality_score_norm'] + epsilon) / 
            (1.01 - df['efficiency_score'])
        )
    else:
        print("  ⚠ 警告: 缺少计算质效比所需的列")
        df['qe_ratio'] = np.nan
    
    return df


def calculate_score_final(df: pd.DataFrame) -> pd.DataFrame:
    """计算最终得分"""
    # 计算每token能耗
    if 'gpu_energy_j' in df.columns and 'n_tokens' in df.columns:
        df['e_token_j'] = df['gpu_energy_j'] / (df['n_tokens'] + 1)
    
    # 计算每瓦性能
    if 'toks_per_s' in df.columns and 'gpu_power_avg_w' in df.columns:
        df['ppw'] = df['toks_per_s'] / (df['gpu_power_avg_w'] + 1e-6)
    
    # 最终得分: 质量 / 每token能耗
    if 'quality_score' in df.columns and 'e_token_j' in df.columns:
        df['score_final'] = df['quality_score'] / (df['e_token_j'] + 1e-6)
    else:
        df['score_final'] = np.nan
    
    return df


def calculate_cost_metrics(
    df: pd.DataFrame,
    gpu_hourly_rate: float = 0.75,
    electricity_price: float = 0.08
) -> pd.DataFrame:
    """计算成本指标"""
    # GPU成本
    if 'latency_s' in df.columns:
        df['cost_gpu_usd'] = (df['latency_s'] / 3600) * gpu_hourly_rate
    
    # 能耗成本
    if 'gpu_energy_j' in df.columns:
        df['cost_energy_usd'] = (df['gpu_energy_j'] / (3.6 * 1e6)) * electricity_price
    
    # 总成本
    if 'cost_gpu_usd' in df.columns and 'cost_energy_usd' in df.columns:
        df['cost_total_usd'] = df['cost_gpu_usd'] + df['cost_energy_usd']
    
    # 单位成本质量
    if 'quality_score' in df.columns and 'cost_total_usd' in df.columns:
        df['cpq'] = df['quality_score'] / (df['cost_total_usd'] + 1e-6)
    
    return df


def analyze_by_model(df: pd.DataFrame) -> pd.DataFrame:
    """按模型分析综合表现"""
    agg_dict = {}
    
    for col in ['quality_score', 'efficiency_score', 'qe_ratio', 'score_final', 
                'latency_s', 'gpu_energy_j', 'cpq']:
        if col in df.columns:
            agg_dict[col] = ['mean', 'std']
    
    if not agg_dict:
        print("  ⚠ 警告: 没有可用于分析的指标")
        return pd.DataFrame()
    
    model_analysis = df.groupby('model').agg(agg_dict).round(4)
    model_analysis.columns = ['_'.join(col).strip() for col in model_analysis.columns.values]
    
    # 综合排名
    if 'qe_ratio_mean' in model_analysis.columns:
        model_analysis['综合排名'] = model_analysis['qe_ratio_mean'].rank(ascending=False)
        model_analysis = model_analysis.sort_values('综合排名')
    
    return model_analysis


def analyze_by_task(df: pd.DataFrame) -> tuple:
    """按任务分析模型表现"""
    agg_dict = {}
    
    for col in ['quality_score', 'efficiency_score', 'qe_ratio', 'score_final',
                'latency_s', 'gpu_energy_j']:
        if col in df.columns:
            agg_dict[col] = 'mean'
    
    if not agg_dict:
        return pd.DataFrame(), pd.DataFrame()
    
    task_analysis = df.groupby(['model', 'task_type']).agg(agg_dict).reset_index()
    
    # 计算每个模型的最佳任务
    if 'qe_ratio' in task_analysis.columns:
        best_tasks = task_analysis.loc[
            task_analysis.groupby('model')['qe_ratio'].idxmax()
        ]
    else:
        best_tasks = pd.DataFrame()
    
    return task_analysis, best_tasks


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='综合分析：质量评估 + 性能指标整合')
    parser.add_argument('--experiment', default='experiments_1', help='实验批次名称')
    parser.add_argument('--quality-dir', default='data/analize/results', help='质量数据目录')
    parser.add_argument('--output-dir', default='data/analysis', help='输出目录')
    args = parser.parse_args()
    
    # 配置路径
    QUALITY_DIR = Path(args.quality_dir)
    PERFORMANCE_FILE = Path(f"data/{args.experiment}/summary/results.csv")
    OUTPUT_DIR = Path(args.output_dir)
    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)
    FIGURES_DIR = OUTPUT_DIR / "figures"
    FIGURES_DIR.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("📊 综合分析：质量评估 + 性能指标整合")
    print("="*60 + "\n")
    print(f"质量数据目录: {QUALITY_DIR}")
    print(f"性能数据文件: {PERFORMANCE_FILE}")
    print(f"输出目录: {OUTPUT_DIR}\n")
    
    try:
        # 1. 数据整合
        print("📂 步骤1: 整合质量和性能数据")
        print("-" * 60)
        df = integrate_quality_and_performance(
            QUALITY_DIR,
            PERFORMANCE_FILE,
            OUTPUT_DIR / "comprehensive_results.csv"
        )
        
        # 2. 归一化
        print("🔢 步骤2: 归一化处理")
        print("-" * 60)
        metrics_to_normalize = [
            'quality_score', 'toks_per_s', 'latency_s', 'gpu_energy_j'
        ]
        df_norm = normalize_by_task(df, metrics_to_normalize)
        print("  ✅ 归一化完成\n")
        
        # 3. 计算复合指标
        print("📈 步骤3: 计算复合指标")
        print("-" * 60)
        df_norm = calculate_efficiency_score(df_norm)
        print("  ✓ 效率得分")
        df_norm = calculate_qe_ratio(df_norm)
        print("  ✓ 质效比")
        df_norm = calculate_score_final(df_norm)
        print("  ✓ 最终得分")
        df_norm = calculate_cost_metrics(df_norm)
        print("  ✓ 成本指标")
        
        df_norm.to_csv(OUTPUT_DIR / "composite_metrics.csv", index=False, encoding='utf-8')
        print(f"  💾 已保存: {OUTPUT_DIR / 'composite_metrics.csv'}\n")
        
        # 4. 多维度分析
        print("🔍 步骤4: 多维度分析")
        print("-" * 60)
        model_analysis = analyze_by_model(df_norm)
        task_analysis, best_tasks = analyze_by_task(df_norm)
        
        # 保存分析结果
        if not model_analysis.empty:
            model_analysis.to_csv(OUTPUT_DIR / "model_analysis.csv", encoding='utf-8')
            print(f"  💾 模型分析: {OUTPUT_DIR / 'model_analysis.csv'}")
        
        if not task_analysis.empty:
            task_analysis.to_csv(OUTPUT_DIR / "task_analysis.csv", index=False, encoding='utf-8')
            print(f"  💾 任务分析: {OUTPUT_DIR / 'task_analysis.csv'}")
        
        print("  ✅ 分析完成\n")
        
        # 5. 生成简要报告
        print("📝 步骤5: 生成简要报告")
        print("-" * 60)
        
        if not model_analysis.empty and 'qe_ratio_mean' in model_analysis.columns:
            print("\n  🏆 模型综合排名 (Top 5):")
            print("  " + "-" * 56)
            for rank, (model, row) in enumerate(model_analysis.head(5).iterrows(), 1):
                qe = row.get('qe_ratio_mean', 0)
                quality = row.get('quality_score_mean', 0)
                efficiency = row.get('efficiency_score_mean', 0)
                print(f"  {rank}. {model:20s} | QE={qe:.4f} | Q={quality:.4f} | E={efficiency:.4f}")
        
        print("\n" + "="*60)
        print("✅ 综合分析完成!")
        print(f"📁 输出目录: {OUTPUT_DIR}")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
