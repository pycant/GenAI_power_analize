"""
代码生成任务帕累托前沿分析

基于以下数据：
1. 质量指标：编译成功率（compilation_rate）
2. 能耗指标：每token能耗（energy_per_token）
3. 速度指标：平均token速度（avg_token_speed）

输出：
- 帕累托前沿识别（2D和3D）
- 定量指标计算
- 稳健性验证
- 完整分析报告
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 数据路径
QUALITY_FILE = project_root / 'data' / 'analize' / 'results' / 'code_quality' / 'quality_summary_code.csv'
ENERGY_FILE = project_root / 'analysis' / 'qe_research' / 'results' / 'derived_metrics' / '08_energy_per_token.csv'
SPEED_FILE = project_root / 'analysis' / 'qe_research' / 'results' / 'derived_metrics' / '07_avg_token_speed.csv'

# 输出目录
OUTPUT_DIR = project_root / 'analysis' / 'qe_research' / 'results' / 'pareto_analysis' / 'code'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_and_prepare_data():
    """加载并准备数据"""
    print("\n" + "="*80)
    print("加载数据：代码生成任务")
    print("="*80)
    
    # 1. 加载质量数据
    quality_df = pd.read_csv(QUALITY_FILE)
    print(f"✓ 质量数据: {len(quality_df)} 个模型")
    
    # 2. 加载能耗数据（转置）
    energy_df = pd.read_csv(ENERGY_FILE, index_col=0)
    energy_code = energy_df.loc['code'].to_dict()
    print(f"✓ 能耗数据: {len(energy_code)} 个模型")
    
    # 3. 加载速度数据（转置）
    speed_df = pd.read_csv(SPEED_FILE, index_col=0)
    speed_code = speed_df.loc['code'].to_dict()
    print(f"✓ 速度数据: {len(speed_code)} 个模型")
    
    # 4. 模型名称映射（从summary格式到metrics格式）
    model_mapping = {
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
    
    # 5. 合并数据
    data = []
    for _, row in quality_df.iterrows():
        model_short = row['model']
        model_full = model_mapping.get(model_short)
        
        if model_full and model_full in energy_code and model_full in speed_code:
            data.append({
                'model': model_short,
                'model_full': model_full,
                'quality': row['compilation_rate_mean'],  # 编译成功率
                'energy': energy_code[model_full],  # 每token能耗（J/token）
                'speed': speed_code[model_full]  # token速度（tokens/s）
            })
    
    df = pd.DataFrame(data)
    
    print(f"\n合并后数据: {len(df)} 个模型")
    print(f"列: {', '.join(df.columns)}")
    
    # 保存合并数据
    merged_file = OUTPUT_DIR / 'merged_data.csv'
    df.to_csv(merged_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ 合并数据已保存: {merged_file}")
    
    return df


def identify_pareto_frontier_2d(df, x_col, y_col, x_minimize=True, y_minimize=True):
    """
    识别2D帕累托前沿
    
    Args:
        df: 数据框
        x_col: X轴列名
        y_col: Y轴列名
        x_minimize: X轴是否最小化（True）或最大化（False）
        y_minimize: Y轴是否最小化（True）或最大化（False）
    
    Returns:
        pareto_mask: 布尔数组，True表示在帕累托前沿上
    """
    n = len(df)
    pareto_mask = np.ones(n, dtype=bool)
    
    for i in range(n):
        if not pareto_mask[i]:
            continue
        
        for j in range(n):
            if i == j:
                continue
            
            # 检查j是否支配i
            x_i, y_i = df.iloc[i][x_col], df.iloc[i][y_col]
            x_j, y_j = df.iloc[j][x_col], df.iloc[j][y_col]
            
            # 根据优化方向调整比较
            if x_minimize:
                x_better = x_j <= x_i
                x_strictly_better = x_j < x_i
            else:
                x_better = x_j >= x_i
                x_strictly_better = x_j > x_i
            
            if y_minimize:
                y_better = y_j <= y_i
                y_strictly_better = y_j < y_i
            else:
                y_better = y_j >= y_i
                y_strictly_better = y_j > y_i
            
            # j支配i：在所有维度上不差，且至少在一个维度上更好
            if x_better and y_better and (x_strictly_better or y_strictly_better):
                pareto_mask[i] = False
                break
    
    return pareto_mask


def identify_pareto_frontier_3d(df):
    """
    识别3D帕累托前沿（质量最大化，能耗最小化，速度最大化）
    
    Returns:
        pareto_mask: 布尔数组
    """
    n = len(df)
    pareto_mask = np.ones(n, dtype=bool)
    
    for i in range(n):
        if not pareto_mask[i]:
            continue
        
        for j in range(n):
            if i == j:
                continue
            
            q_i, e_i, s_i = df.iloc[i]['quality'], df.iloc[i]['energy'], df.iloc[i]['speed']
            q_j, e_j, s_j = df.iloc[j]['quality'], df.iloc[j]['energy'], df.iloc[j]['speed']
            
            # j支配i：质量≥，能耗≤，速度≥，且至少一个严格更好
            quality_better = q_j >= q_i
            energy_better = e_j <= e_i
            speed_better = s_j >= s_i
            
            strictly_better = (q_j > q_i) or (e_j < e_i) or (s_j > s_i)
            
            if quality_better and energy_better and speed_better and strictly_better:
                pareto_mask[i] = False
                break
    
    return pareto_mask


def plot_pareto_2d(df, pareto_mask, x_col, y_col, title, filename, 
                   x_label, y_label, x_minimize=True, y_minimize=True):
    """绘制2D帕累托前沿图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 非帕累托点
    non_pareto = df[~pareto_mask]
    ax.scatter(non_pareto[x_col], non_pareto[y_col], 
              c='lightgray', s=100, alpha=0.6, label='非帕累托点')
    
    # 帕累托点
    pareto = df[pareto_mask]
    ax.scatter(pareto[x_col], pareto[y_col], 
              c='red', s=200, marker='*', label='帕累托前沿', zorder=5)
    
    # 标注所有点
    for _, row in df.iterrows():
        ax.annotate(row['model'], 
                   (row[x_col], row[y_col]),
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, alpha=0.8)
    
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ 图表已保存: {filename}")


def calculate_hypervolume(df, pareto_mask, reference_point):
    """
    计算超体积指标（质量-能耗平面）
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        reference_point: 参考点 (quality_ref, energy_ref)
    
    Returns:
        hypervolume: 超体积值
    """
    pareto = df[pareto_mask].copy()
    
    # 归一化到[0,1]（质量最大化，能耗最小化）
    q_min, q_max = df['quality'].min(), df['quality'].max()
    e_min, e_max = df['energy'].min(), df['energy'].max()
    
    pareto['q_norm'] = (pareto['quality'] - q_min) / (q_max - q_min) if q_max > q_min else 0
    pareto['e_norm'] = 1 - (pareto['energy'] - e_min) / (e_max - e_min) if e_max > e_min else 0
    
    # 按质量排序
    pareto = pareto.sort_values('q_norm')
    
    # 计算超体积
    hv = 0
    for i in range(len(pareto)):
        if i == 0:
            width = pareto.iloc[i]['q_norm'] - 0
        else:
            width = pareto.iloc[i]['q_norm'] - pareto.iloc[i-1]['q_norm']
        
        height = pareto.iloc[i]['e_norm']
        hv += width * height
    
    return hv


def calculate_spacing(df, pareto_mask):
    """计算间距指标（均匀性）"""
    pareto = df[pareto_mask]
    
    if len(pareto) < 2:
        return 0
    
    # 归一化
    q_norm = (pareto['quality'] - df['quality'].min()) / (df['quality'].max() - df['quality'].min())
    e_norm = (pareto['energy'] - df['energy'].min()) / (df['energy'].max() - df['energy'].min())
    
    # 计算相邻点距离
    distances = []
    points = np.column_stack([q_norm, e_norm])
    
    for i in range(len(points)):
        min_dist = float('inf')
        for j in range(len(points)):
            if i != j:
                dist = np.linalg.norm(points[i] - points[j])
                min_dist = min(min_dist, dist)
        distances.append(min_dist)
    
    # 间距指标：距离的标准差
    mean_dist = np.mean(distances)
    spacing = np.sqrt(np.mean([(d - mean_dist)**2 for d in distances]))
    
    return spacing


def find_knee_point(df, pareto_mask):
    """
    寻找拐点（膝点）
    
    使用曲率法：找到曲率最大的点
    """
    pareto = df[pareto_mask].copy()
    
    if len(pareto) < 3:
        return pareto.iloc[0]['model'] if len(pareto) > 0 else None
    
    # 归一化
    q_norm = (pareto['quality'] - df['quality'].min()) / (df['quality'].max() - df['quality'].min())
    e_norm = (pareto['energy'] - df['energy'].min()) / (df['energy'].max() - df['energy'].min())
    
    # 按质量排序
    pareto['q_norm'] = q_norm
    pareto['e_norm'] = e_norm
    pareto = pareto.sort_values('q_norm')
    
    # 计算曲率
    max_curvature = -1
    knee_idx = 0
    
    for i in range(1, len(pareto) - 1):
        # 三点法计算曲率
        p1 = np.array([pareto.iloc[i-1]['q_norm'], pareto.iloc[i-1]['e_norm']])
        p2 = np.array([pareto.iloc[i]['q_norm'], pareto.iloc[i]['e_norm']])
        p3 = np.array([pareto.iloc[i+1]['q_norm'], pareto.iloc[i+1]['e_norm']])
        
        # 向量
        v1 = p2 - p1
        v2 = p3 - p2
        
        # 角度变化
        if np.linalg.norm(v1) > 0 and np.linalg.norm(v2) > 0:
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1, 1)
            curvature = 1 - cos_angle  # 曲率近似
            
            if curvature > max_curvature:
                max_curvature = curvature
                knee_idx = i
    
    return pareto.iloc[knee_idx]['model']


def generate_report(df, results):
    """生成分析报告"""
    report_file = OUTPUT_DIR / 'CODE_PARETO_ANALYSIS_REPORT.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 代码生成任务帕累托前沿分析报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 1. 数据概览
        f.write("## 1. 数据概览\n\n")
        f.write(f"- **任务类型**: 代码生成（code）\n")
        f.write(f"- **模型数量**: {len(df)}\n")
        f.write(f"- **质量指标**: 编译成功率（compilation_rate）\n")
        f.write(f"- **能耗指标**: 每token能耗（J/token）\n")
        f.write(f"- **速度指标**: token生成速度（tokens/s）\n\n")
        
        # 2. 帕累托前沿识别
        f.write("## 2. 帕累托前沿识别\n\n")
        
        f.write("### 2.1 质量-能耗前沿\n\n")
        pareto_qe = results['pareto_qe']
        f.write(f"**前沿模型数**: {pareto_qe.sum()}\n\n")
        f.write("**前沿模型列表**:\n\n")
        for model in df[pareto_qe]['model']:
            row = df[df['model'] == model].iloc[0]
            f.write(f"- {model}: 质量={row['quality']:.3f}, 能耗={row['energy']:.3f} J/token\n")
        f.write("\n")
        
        f.write("### 2.2 质量-速度前沿\n\n")
        pareto_qs = results['pareto_qs']
        f.write(f"**前沿模型数**: {pareto_qs.sum()}\n\n")
        f.write("**前沿模型列表**:\n\n")
        for model in df[pareto_qs]['model']:
            row = df[df['model'] == model].iloc[0]
            f.write(f"- {model}: 质量={row['quality']:.3f}, 速度={row['speed']:.2f} tokens/s\n")
        f.write("\n")
        
        f.write("### 2.3 三维前沿（质量-能耗-速度）\n\n")
        pareto_3d = results['pareto_3d']
        f.write(f"**前沿模型数**: {pareto_3d.sum()}\n\n")
        f.write("**前沿模型列表**:\n\n")
        for model in df[pareto_3d]['model']:
            row = df[df['model'] == model].iloc[0]
            f.write(f"- {model}: 质量={row['quality']:.3f}, 能耗={row['energy']:.3f} J/token, 速度={row['speed']:.2f} tokens/s\n")
        f.write("\n")
        
        # 3. 定量指标
        f.write("## 3. 定量指标\n\n")
        f.write(f"- **超体积（质量-能耗）**: {results['hypervolume_qe']:.4f}\n")
        f.write(f"- **间距指标（质量-能耗）**: {results['spacing_qe']:.4f}\n")
        f.write(f"- **拐点模型**: {results['knee_point']}\n\n")
        
        # 4. 推荐配置
        f.write("## 4. 推荐配置\n\n")
        
        knee_model = results['knee_point']
        if knee_model:
            knee_row = df[df['model'] == knee_model].iloc[0]
            f.write(f"### 最佳综合配置: {knee_model} ⭐⭐⭐⭐⭐\n\n")
            f.write(f"- **编译成功率**: {knee_row['quality']:.1%}\n")
            f.write(f"- **每token能耗**: {knee_row['energy']:.3f} J/token\n")
            f.write(f"- **生成速度**: {knee_row['speed']:.2f} tokens/s\n")
            f.write(f"- **推荐理由**: 拐点模型，质量-能耗权衡最优\n\n")
        
        # 最高质量
        best_quality = df.loc[df['quality'].idxmax()]
        f.write(f"### 最高质量: {best_quality['model']}\n\n")
        f.write(f"- **编译成功率**: {best_quality['quality']:.1%}\n")
        f.write(f"- **每token能耗**: {best_quality['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_quality['speed']:.2f} tokens/s\n\n")
        
        # 最低能耗
        best_energy = df.loc[df['energy'].idxmin()]
        f.write(f"### 最低能耗: {best_energy['model']}\n\n")
        f.write(f"- **编译成功率**: {best_energy['quality']:.1%}\n")
        f.write(f"- **每token能耗**: {best_energy['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_energy['speed']:.2f} tokens/s\n\n")
        
        # 最快速度
        best_speed = df.loc[df['speed'].idxmax()]
        f.write(f"### 最快速度: {best_speed['model']}\n\n")
        f.write(f"- **编译成功率**: {best_speed['quality']:.1%}\n")
        f.write(f"- **每token能耗**: {best_speed['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_speed['speed']:.2f} tokens/s\n\n")
        
        # 5. 数据表
        f.write("## 5. 完整数据表\n\n")
        f.write("| 模型 | 编译成功率 | 能耗(J/token) | 速度(tokens/s) | 质量-能耗前沿 | 质量-速度前沿 | 3D前沿 |\n")
        f.write("|------|-----------|--------------|---------------|-------------|-------------|--------|\n")
        
        for _, row in df.iterrows():
            qe = "✓" if pareto_qe[_] else ""
            qs = "✓" if pareto_qs[_] else ""
            p3d = "✓" if pareto_3d[_] else ""
            f.write(f"| {row['model']} | {row['quality']:.1%} | {row['energy']:.3f} | {row['speed']:.2f} | {qe} | {qs} | {p3d} |\n")
        
        f.write("\n---\n\n")
        f.write("**生成脚本**: `analysis/qe_research/scripts/pareto_analysis_code.py`\n")
    
    print(f"\n✓ 报告已生成: {report_file}")


def main():
    """主函数"""
    print("\n" + "="*80)
    print("代码生成任务帕累托前沿分析")
    print("="*80)
    
    # 1. 加载数据
    df = load_and_prepare_data()
    
    # 2. 识别帕累托前沿
    print("\n" + "="*80)
    print("识别帕累托前沿")
    print("="*80)
    
    # 2.1 质量-能耗前沿（质量最大化，能耗最小化）
    pareto_qe = identify_pareto_frontier_2d(df, 'quality', 'energy', 
                                            x_minimize=False, y_minimize=True)
    print(f"✓ 质量-能耗前沿: {pareto_qe.sum()} 个模型")
    
    # 2.2 质量-速度前沿（质量最大化，速度最大化）
    pareto_qs = identify_pareto_frontier_2d(df, 'quality', 'speed',
                                            x_minimize=False, y_minimize=False)
    print(f"✓ 质量-速度前沿: {pareto_qs.sum()} 个模型")
    
    # 2.3 三维前沿
    pareto_3d = identify_pareto_frontier_3d(df)
    print(f"✓ 三维前沿: {pareto_3d.sum()} 个模型")
    
    # 3. 绘制图表
    print("\n" + "="*80)
    print("生成可视化图表")
    print("="*80)
    
    plot_pareto_2d(df, pareto_qe, 'quality', 'energy',
                   '代码生成任务：质量-能耗帕累托前沿',
                   'pareto_quality_energy.png',
                   '编译成功率', '每token能耗 (J/token)',
                   x_minimize=False, y_minimize=True)
    
    plot_pareto_2d(df, pareto_qs, 'quality', 'speed',
                   '代码生成任务：质量-速度帕累托前沿',
                   'pareto_quality_speed.png',
                   '编译成功率', 'Token生成速度 (tokens/s)',
                   x_minimize=False, y_minimize=False)
    
    # 4. 计算定量指标
    print("\n" + "="*80)
    print("计算定量指标")
    print("="*80)
    
    hv_qe = calculate_hypervolume(df, pareto_qe, (0, 1))
    print(f"✓ 超体积（质量-能耗）: {hv_qe:.4f}")
    
    spacing_qe = calculate_spacing(df, pareto_qe)
    print(f"✓ 间距指标（质量-能耗）: {spacing_qe:.4f}")
    
    knee = find_knee_point(df, pareto_qe)
    print(f"✓ 拐点模型: {knee}")
    
    # 5. 生成报告
    results = {
        'pareto_qe': pareto_qe,
        'pareto_qs': pareto_qs,
        'pareto_3d': pareto_3d,
        'hypervolume_qe': hv_qe,
        'spacing_qe': spacing_qe,
        'knee_point': knee
    }
    
    generate_report(df, results)
    
    print("\n" + "="*80)
    print("分析完成！")
    print("="*80)
    print(f"\n输出目录: {OUTPUT_DIR}")
    print(f"- merged_data.csv: 合并数据")
    print(f"- pareto_quality_energy.png: 质量-能耗前沿图")
    print(f"- pareto_quality_speed.png: 质量-速度前沿图")
    print(f"- CODE_PARETO_ANALYSIS_REPORT.md: 完整分析报告")


if __name__ == '__main__':
    main()
