"""
Pareto分析共享函数

包含所有任务脚本共用的核心算法实现
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


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


def identify_pareto_frontier_3d(df, quality_col='quality', energy_col='energy', speed_col='speed'):
    """
    识别3D帕累托前沿（质量最大化，能耗最小化，速度最大化）
    
    Args:
        df: 数据框
        quality_col: 质量列名（最大化）
        energy_col: 能耗列名（最小化）
        speed_col: 速度列名（最大化）
    
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
            
            q_i = df.iloc[i][quality_col]
            e_i = df.iloc[i][energy_col]
            s_i = df.iloc[i][speed_col]
            
            q_j = df.iloc[j][quality_col]
            e_j = df.iloc[j][energy_col]
            s_j = df.iloc[j][speed_col]
            
            # j支配i：质量≥，能耗≤，速度≥，且至少一个严格更好
            quality_better = q_j >= q_i
            energy_better = e_j <= e_i
            speed_better = s_j >= s_i
            
            strictly_better = (q_j > q_i) or (e_j < e_i) or (s_j > s_i)
            
            if quality_better and energy_better and speed_better and strictly_better:
                pareto_mask[i] = False
                break
    
    return pareto_mask


def calculate_hypervolume(df, pareto_mask, quality_col='quality', energy_col='energy', reference_point=None):
    """
    计算超体积指标（质量-能耗平面）
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        quality_col: 质量列名
        energy_col: 能耗列名
        reference_point: 参考点 (quality_ref, energy_ref)，默认为None
    
    Returns:
        hypervolume: 超体积值
    """
    pareto = df[pareto_mask].copy()
    
    if len(pareto) == 0:
        return 0.0
    
    # 归一化到[0,1]（质量最大化，能耗最小化）
    q_min, q_max = df[quality_col].min(), df[quality_col].max()
    e_min, e_max = df[energy_col].min(), df[energy_col].max()
    
    if q_max > q_min:
        pareto['q_norm'] = (pareto[quality_col] - q_min) / (q_max - q_min)
    else:
        pareto['q_norm'] = 0
    
    if e_max > e_min:
        pareto['e_norm'] = 1 - (pareto[energy_col] - e_min) / (e_max - e_min)
    else:
        pareto['e_norm'] = 0
    
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


def calculate_spacing(df, pareto_mask, quality_col='quality', energy_col='energy'):
    """
    计算间距指标（均匀性）
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        quality_col: 质量列名
        energy_col: 能耗列名
    
    Returns:
        spacing: 间距指标值
    """
    pareto = df[pareto_mask]
    
    if len(pareto) < 2:
        return 0
    
    # 归一化
    q_min, q_max = df[quality_col].min(), df[quality_col].max()
    e_min, e_max = df[energy_col].min(), df[energy_col].max()
    
    if q_max > q_min:
        q_norm = (pareto[quality_col] - q_min) / (q_max - q_min)
    else:
        q_norm = pd.Series([0] * len(pareto), index=pareto.index)
    
    if e_max > e_min:
        e_norm = (pareto[energy_col] - e_min) / (e_max - e_min)
    else:
        e_norm = pd.Series([0] * len(pareto), index=pareto.index)
    
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


def find_knee_point(df, pareto_mask, quality_col='quality', energy_col='energy'):
    """
    寻找拐点（膝点）
    
    使用曲率法：找到曲率最大的点
    
    Args:
        df: 数据框
        pareto_mask: 帕累托前沿掩码
        quality_col: 质量列名
        energy_col: 能耗列名
    
    Returns:
        knee_model: 拐点模型名称
    """
    pareto = df[pareto_mask].copy()
    
    if len(pareto) < 3:
        return pareto.iloc[0]['model'] if len(pareto) > 0 else None
    
    # 归一化
    q_min, q_max = df[quality_col].min(), df[quality_col].max()
    e_min, e_max = df[energy_col].min(), df[energy_col].max()
    
    if q_max > q_min:
        pareto['q_norm'] = (pareto[quality_col] - q_min) / (q_max - q_min)
    else:
        pareto['q_norm'] = 0
    
    if e_max > e_min:
        pareto['e_norm'] = (pareto[energy_col] - e_min) / (e_max - e_min)
    else:
        pareto['e_norm'] = 0
    
    # 按质量排序
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


def plot_pareto_2d(df, pareto_mask, x_col, y_col, title, output_path,
                   x_label, y_label, x_minimize=True, y_minimize=True):
    """
    绘制增强版2D帕累托前沿图
    
    优化特性:
    - 渐变色映射显示性能梯度
    - 帕累托前沿连线
    - 智能标注避免重叠
    - 统计信息框
    - 点大小差异化
    - 参考线和区域
    - 专业配色和布局
    
    Args:
        df: 数据框（必须包含 'model' 列）
        pareto_mask: 帕累托前沿掩码（布尔数组）
        x_col: X轴列名
        y_col: Y轴列名
        title: 图表标题
        output_path: 输出文件路径
        x_label: X轴标签
        y_label: Y轴标签
        x_minimize: X轴是否最小化（True表示越小越好）
        y_minimize: Y轴是否最小化（True表示越小越好）
    """
    import numpy as np
    from scipy.spatial.distance import cdist
    
    # 设置中文字体和样式
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建图表，使用浅灰色背景
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('white')
    
    # 分离帕累托点和非帕累托点
    pareto_df = df[pareto_mask].copy()
    non_pareto_df = df[~pareto_mask].copy()
    
    # ============================================================
    # 第一阶段：核心视觉增强
    # ============================================================
    
    # 1. 计算到帕累托前沿的距离（用于渐变色映射）
    if len(non_pareto_df) > 0 and len(pareto_df) > 0:
        # 归一化坐标
        x_range = df[x_col].max() - df[x_col].min()
        y_range = df[y_col].max() - df[y_col].min()
        
        if x_range > 0 and y_range > 0:
            pareto_coords = np.column_stack([
                (pareto_df[x_col] - df[x_col].min()) / x_range,
                (pareto_df[y_col] - df[y_col].min()) / y_range
            ])
            non_pareto_coords = np.column_stack([
                (non_pareto_df[x_col] - df[x_col].min()) / x_range,
                (non_pareto_df[y_col] - df[y_col].min()) / y_range
            ])
            
            # 计算最小距离
            distances = cdist(non_pareto_coords, pareto_coords).min(axis=1)
            # 归一化距离到 [0, 1]
            if distances.max() > 0:
                distances_norm = distances / distances.max()
            else:
                distances_norm = distances
        else:
            distances_norm = np.zeros(len(non_pareto_df))
    else:
        distances_norm = np.zeros(len(non_pareto_df))
    
    # 2. 使用渐变色映射绘制非帕累托点
    if len(non_pareto_df) > 0:
        # 使用 viridis 色系，距离越远颜色越浅
        colors = plt.cm.viridis(0.1 + 1 * (1 - distances_norm))
        scatter_non = ax.scatter(
            non_pareto_df[x_col], 
            non_pareto_df[y_col],
            c=colors, 
            s=150, 
            alpha=0.7, 
            edgecolors='white',
            linewidths=1.5,
            label='非帕累托点',
            zorder=3
        )
    
    # 3. 绘制帕累托点（醒目的金色星形）
    if len(pareto_df) > 0:
        scatter_pareto = ax.scatter(
            pareto_df[x_col], 
            pareto_df[y_col],
            c='#FF6B35',  # 橙红色
            s=400, 
            marker='*', 
            edgecolors='#8B0000',  # 深红色边框
            linewidths=2,
            label='帕累托前沿',
            zorder=6,
            alpha=0.95
        )
        
        # 4. 添加帕累托前沿连线
        if len(pareto_df) > 1:
            # 根据优化方向排序
            if x_minimize:
                pareto_sorted = pareto_df.sort_values(by=x_col)
            else:
                pareto_sorted = pareto_df.sort_values(by=x_col, ascending=False)
            
            ax.plot(
                pareto_sorted[x_col], 
                pareto_sorted[y_col],
                color='#FF6B35',
                linestyle='--',
                linewidth=2.5,
                alpha=0.6,
                zorder=5,
                label='前沿连线'
            )
            
            # 添加前沿区域阴影（填充到边界）
            if x_minimize and y_minimize:
                # 两个都最小化：填充右上角
                x_fill = list(pareto_sorted[x_col]) + [ax.get_xlim()[1], ax.get_xlim()[1]]
                y_fill = list(pareto_sorted[y_col]) + [pareto_sorted[y_col].iloc[-1], ax.get_ylim()[1]]
            elif not x_minimize and not y_minimize:
                # 两个都最大化：填充左下角
                x_fill = list(pareto_sorted[x_col]) + [ax.get_xlim()[0], ax.get_xlim()[0]]
                y_fill = list(pareto_sorted[y_col]) + [pareto_sorted[y_col].iloc[-1], ax.get_ylim()[0]]
            else:
                # 混合情况：不填充
                x_fill, y_fill = None, None
            
            if x_fill and y_fill:
                ax.fill(x_fill, y_fill, color='#FFE5D9', alpha=0.2, zorder=1)
    
    # 5. 智能标注（只标注帕累托点，避免重叠）
    texts = []
    if len(pareto_df) > 0:
        for _, row in pareto_df.iterrows():
            text = ax.text(
                row[x_col]+0.05, 
                row[y_col]+0.05, 
                row['model'],
                fontsize=10,
                fontweight='bold',
                color='#2C3E50',
                bbox=dict(
                    boxstyle='round,pad=0.5',
                    facecolor='white',
                    edgecolor='#FF6B35',
                    alpha=0.9,
                    linewidth=1.5
                ),
                zorder=7
            )
            texts.append(text)
        
        # 尝试使用 adjustText 避免重叠
        try:
            from adjustText import adjust_text
            adjust_text(
                texts,
                arrowprops=dict(
                    arrowstyle='->',
                    color='#95A5A6',
                    lw=1,
                    alpha=0.7
                ),
                expand_points=(1.5, 1.5),
                force_points=(0.5, 0.5),
                ax=ax
            )
        except ImportError:
            # 如果没有 adjustText，使用简单偏移
            for text in texts:
                text.set_position((text.get_position()[0], text.get_position()[1] + 0.02))
    
    # ============================================================
    # 第二阶段：信息增强
    # ============================================================
    
    # 6. 添加统计信息框
    stats_text = f"""统计信息
━━━━━━━━━━━━━━
帕累托点: {len(pareto_df)}/{len(df)}
覆盖率: {len(pareto_df)/len(df)*100:.1f}%
━━━━━━━━━━━━━━
{x_label}
  范围: [{df[x_col].min():.3f}, {df[x_col].max():.3f}]
  均值: {df[x_col].mean():.3f}
━━━━━━━━━━━━━━
{y_label}
  范围: [{df[y_col].min():.3f}, {df[y_col].max():.3f}]
  均值: {df[y_col].mean():.3f}"""
    
    # 最优模型信息
    if len(pareto_df) > 0:
        # 找到综合最优的帕累托点（归一化后距离原点最近）
        x_norm = (pareto_df[x_col] - df[x_col].min()) / (df[x_col].max() - df[x_col].min() + 1e-10)
        y_norm = (pareto_df[y_col] - df[y_col].min()) / (df[y_col].max() - df[y_col].min() + 1e-10)
        
        if x_minimize:
            x_norm = x_norm
        else:
            x_norm = 1 - x_norm
        
        if y_minimize:
            y_norm = y_norm
        else:
            y_norm = 1 - y_norm
        
        distances_to_ideal = np.sqrt(x_norm**2 + y_norm**2)
        best_idx = distances_to_ideal.idxmin()
        best_model = pareto_df.loc[best_idx, 'model']
        
        stats_text += f"\n━━━━━━━━━━━━━━\n最优模型: {best_model}"
    
    # 放置统计信息框（右上角）
    ax.text(
        0.98, 0.98,
        stats_text,
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment='top',
        horizontalalignment='right',
        bbox=dict(
            boxstyle='round,pad=0.8',
            facecolor='white',
            edgecolor='#34495E',
            alpha=0.95,
            linewidth=2
        ),
        zorder=10
    )
    
    # ============================================================
    # 第三阶段：细节优化
    # ============================================================
    
    # 7. 添加参考线（平均值虚线）
    ax.axvline(
        df[x_col].mean(),
        color='#7F8C8D',
        linestyle=':',
        linewidth=1.5,
        alpha=0.5,
        label=f'{x_label}均值',
        zorder=2
    )
    ax.axhline(
        df[y_col].mean(),
        color='#7F8C8D',
        linestyle=':',
        linewidth=1.5,
        alpha=0.5,
        label=f'{y_label}均值',
        zorder=2
    )
    
    # 8. 优化网格
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='#BDC3C7', zorder=0)
    ax.set_axisbelow(True)
    
    # 9. 设置标签和标题
    ax.set_xlabel(x_label, fontsize=13, fontweight='bold', color='#2C3E50')
    ax.set_ylabel(y_label, fontsize=13, fontweight='bold', color='#2C3E50')
    ax.set_title(title, fontsize=16, fontweight='bold', color='#2C3E50', pad=20)
    
    # 10. 优化图例
    legend = ax.legend(
        loc='upper left',
        fontsize=10,
        frameon=True,
        fancybox=True,
        shadow=True,
        framealpha=0.95,
        edgecolor='#34495E',
        facecolor='white',
        borderpad=1
    )
    legend.get_frame().set_linewidth(2)
    
    # 11. 添加优化方向指示
    direction_text = ""
    if x_minimize and y_minimize:
        direction_text = "← 更优\n↓ 更优"
        arrow_x, arrow_y = 0.05, 0.95
    elif not x_minimize and not y_minimize:
        direction_text = "→ 更优\n↑ 更优"
        arrow_x, arrow_y = 0.95, 0.05
    elif x_minimize and not y_minimize:
        direction_text = "← 更优\n↑ 更优"
        arrow_x, arrow_y = 0.05, 0.05
    else:
        direction_text = "→ 更优\n↓ 更优"
        arrow_x, arrow_y = 0.95, 0.95
    
    ax.text(
        arrow_x, arrow_y,
        direction_text,
        transform=ax.transAxes,
        fontsize=11,
        fontweight='bold',
        color='#E74C3C',
        verticalalignment='top' if 'more优' in direction_text and '↓' in direction_text else 'bottom',
        horizontalalignment='left' if '←' in direction_text else 'right',
        bbox=dict(
            boxstyle='round,pad=0.5',
            facecolor='#FADBD8',
            edgecolor='#E74C3C',
            alpha=0.8,
            linewidth=1.5
        ),
        zorder=10
    )
    
    # 12. 调整边距，确保所有元素可见
    plt.tight_layout()
    
    # 保存图表
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ 增强版帕累托图已保存: {output_path}")


def load_energy_speed_data(task_name, energy_file, speed_file):
    """
    加载能耗和速度数据
    
    Args:
        task_name: 任务名称
        energy_file: 能耗文件路径
        speed_file: 速度文件路径
    
    Returns:
        energy_dict: 能耗字典 {model: energy}
        speed_dict: 速度字典 {model: speed}
    """
    # 加载能耗数据（转置）
    energy_df = pd.read_csv(energy_file, index_col=0)
    energy_dict = energy_df.loc[task_name].to_dict()
    
    # 加载速度数据（转置）
    speed_df = pd.read_csv(speed_file, index_col=0)
    speed_dict = speed_df.loc[task_name].to_dict()
    
    return energy_dict, speed_dict


def load_average_energy_speed_data(energy_file, speed_file):
    """
    加载跨任务的平均能耗和速度数据
    
    用于成本效益分析，当质量数据是跨任务聚合时，
    需要使用平均能耗/速度来计算成本
    
    Args:
        energy_file: 能耗文件路径
        speed_file: 速度文件路径
    
    Returns:
        energy_dict: 平均能耗字典 {model: avg_energy}
        speed_dict: 平均速度字典 {model: avg_speed}
    """
    # 加载能耗数据
    energy_df = pd.read_csv(energy_file, index_col=0)
    # 计算每行的平均值（跨所有任务）
    energy_dict = energy_df.mean(axis=0).to_dict()
    
    # 加载速度数据
    speed_df = pd.read_csv(speed_file, index_col=0)
    # 计算每列的平均值（跨所有任务）
    speed_dict = speed_df.mean(axis=0).to_dict()
    
    return energy_dict, speed_dict


def merge_quality_metrics(quality_df, energy_dict, speed_dict, model_mapping, quality_col='quality'):
    """
    合并质量、能耗、速度数据
    
    此函数兼容两种输入格式：
    1. 旧格式：quality_df 包含 'model' 和自定义质量列（需指定 quality_col）
    2. 新格式：quality_df 来自 load_process_quality_data()，包含 'model' 和 'quality' 列
    
    Args:
        quality_df (pd.DataFrame): 质量数据框
            - 必须包含 'model' 列
            - 旧格式：包含自定义质量列（通过 quality_col 指定）
            - 新格式：包含 'quality' 列（load_process_quality_data 的输出）
        energy_dict (dict): 能耗字典 {model_full: energy_value}
        speed_dict (dict): 速度字典 {model_full: speed_value}
        model_mapping (dict): 模型名称映射 {model_short: model_full}
        quality_col (str): 质量列名，默认 'quality'
            - 新格式（load_process_quality_data）：使用默认值 'quality'
            - 旧格式：指定实际的质量列名（如 'compilation_rate_mean'）
    
    Returns:
        pd.DataFrame: 合并后的数据框，包含列：
            - model: 模型短名称
            - model_full: 模型完整名称
            - quality: 质量得分
            - energy: 能耗值
            - speed: 速度值
    
    Examples:
        # 新格式（推荐）：使用 load_process_quality_data()
        quality_df = load_process_quality_data('code', method='entropy')
        merged_df = merge_quality_metrics(quality_df, energy_dict, speed_dict, MODEL_MAPPING)
        
        # 旧格式：手动加载的数据
        quality_df = pd.read_csv('quality_file.csv')
        merged_df = merge_quality_metrics(quality_df, energy_dict, speed_dict, 
                                          MODEL_MAPPING, quality_col='compilation_rate_mean')
    """
    # 验证输入
    if 'model' not in quality_df.columns:
        raise ValueError("quality_df 必须包含 'model' 列")
    
    if quality_col not in quality_df.columns:
        raise ValueError(f"quality_df 中不存在列 '{quality_col}'。"
                        f"可用列: {list(quality_df.columns)}")
    
    # 合并数据
    data = []
    for _, row in quality_df.iterrows():
        model_short = row['model']
        model_full = model_mapping.get(model_short)
        
        if model_full and model_full in energy_dict and model_full in speed_dict:
            data.append({
                'model': model_short,
                'model_full': model_full,
                'quality': row[quality_col],
                'energy': energy_dict[model_full],
                'speed': speed_dict[model_full]
            })
    
    return pd.DataFrame(data)


def generate_pca_report(pca_result, task_name, output_dir, quality_data=None, verbose=True):
    """
    生成PCA分析详细报告
    
    Args:
        pca_result (dict): PCA结果字典，包含：
            - 'transformed': 降维后的数据（DataFrame）
            - 'components': 主成分载荷矩阵（DataFrame）
            - 'explained_variance_ratio': 解释方差比例（array）
            - 'cumulative_variance_ratio': 累积方差比例（array）
            - 'n_components': 实际主成分数量
        task_name (str): 任务名称
        output_dir (Path): 输出目录
        quality_data (pd.DataFrame): 原始质量数据（可选）
        verbose (bool): 是否输出详细信息
    
    Returns:
        Path: 生成的报告文件路径
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_file = output_path / 'PCA_ANALYSIS_REPORT.md'
    
    n_comp = pca_result['n_components']
    explained_var = pca_result['explained_variance_ratio']
    cumulative_var = pca_result['cumulative_variance_ratio']
    components_df = pca_result['components']
    transformed_df = pca_result['transformed']
    
    with open(report_file, 'w', encoding='utf-8') as f:
        # 标题和元数据
        f.write(f"# PCA降维分析报告 - {task_name.upper()}任务\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 1. 分析概览
        f.write("## 1. 分析概览\n\n")
        f.write(f"- **任务类型**: {task_name}\n")
        f.write(f"- **样本数量**: {len(transformed_df)} 个模型\n")
        f.write(f"- **原始特征数**: {len(components_df)} 个指标\n")
        f.write(f"- **主成分数量**: {n_comp}\n")
        f.write(f"- **累积解释方差**: {cumulative_var[-1]:.2%}\n\n")
        
        # 2. 方差解释
        f.write("## 2. 方差解释\n\n")
        f.write("### 2.1 各主成分解释方差\n\n")
        f.write("| 主成分 | 解释方差比例 | 累积解释方差 | 重要性 |\n")
        f.write("|--------|-------------|-------------|--------|\n")
        
        for i in range(n_comp):
            importance = "⭐⭐⭐⭐⭐" if explained_var[i] >= 0.3 else \
                        "⭐⭐⭐⭐" if explained_var[i] >= 0.2 else \
                        "⭐⭐⭐" if explained_var[i] >= 0.1 else "⭐⭐"
            f.write(f"| PC{i+1} | {explained_var[i]:.4f} ({explained_var[i]*100:.2f}%) | "
                   f"{cumulative_var[i]:.4f} ({cumulative_var[i]*100:.2f}%) | {importance} |\n")
        f.write("\n")
        
        # 自动选择的主成分数量说明
        n_selected = int(np.argmax(cumulative_var >= 0.85) + 1)
        n_selected = max(1, n_selected)
        f.write(f"### 2.2 主成分选择策略\n\n")
        f.write(f"**自动选择**: 选择累积解释方差 ≥ 85% 的主成分\n\n")
        f.write(f"- **选择数量**: {n_selected} 个主成分\n")
        f.write(f"- **累积方差**: {cumulative_var[n_selected-1]:.2%}\n")
        f.write(f"- **信息保留**: 保留了原始数据 {cumulative_var[n_selected-1]*100:.1f}% 的信息\n\n")
        
        # 3. 主成分载荷分析
        f.write("## 3. 主成分载荷分析\n\n")
        f.write("主成分载荷表示原始特征对各主成分的贡献程度。载荷绝对值越大，该特征对主成分的影响越大。\n\n")
        
        for i in range(min(3, n_comp)):
            pc_name = f'PC{i+1}'
            f.write(f"### 3.{i+1} {pc_name} 载荷分析\n\n")
            f.write(f"**解释方差**: {explained_var[i]:.2%}\n\n")
            
            # 获取载荷并排序
            loadings = components_df[pc_name].abs().sort_values(ascending=False)
            
            f.write("**主要贡献特征** (|载荷| > 0.3):\n\n")
            f.write("| 特征 | 载荷值 | 方向 | 贡献度 |\n")
            f.write("|------|--------|------|--------|\n")
            
            has_major_features = False
            for feat in loadings.index:
                load_val = components_df.loc[feat, pc_name]
                abs_load = abs(load_val)
                if abs_load > 0.3:
                    has_major_features = True
                    direction = "正向 ↑" if load_val > 0 else "负向 ↓"
                    contribution = "⭐⭐⭐" if abs_load >= 0.5 else "⭐⭐"
                    f.write(f"| {feat} | {load_val:.4f} | {direction} | {contribution} |\n")
            
            if not has_major_features:
                f.write("| - | - | - | 无显著贡献特征 |\n")
            
            f.write("\n")
            
            # 解释主成分含义
            f.write("**主成分解释**:\n\n")
            top_features = loadings.head(3)
            if len(top_features) > 0:
                feature_names = [f"{feat}({components_df.loc[feat, pc_name]:+.3f})" 
                               for feat in top_features.index]
                f.write(f"{pc_name} 主要反映了 {', '.join(feature_names)} 等特征的综合表现。\n\n")
            else:
                f.write(f"{pc_name} 的特征贡献较为分散。\n\n")
        
        # 4. 完整载荷矩阵
        f.write(f"## 4. 完整载荷矩阵\n\n")
        f.write("所有特征在各主成分上的载荷值：\n\n")
        
        # 构建表格
        f.write("| 特征 |")
        for i in range(n_comp):
            f.write(f" PC{i+1} |")
        f.write("\n")
        
        f.write("|------|")
        for i in range(n_comp):
            f.write("------|")
        f.write("\n")
        
        for feat in components_df.index:
            f.write(f"| {feat} |")
            for i in range(n_comp):
                pc_name = f'PC{i+1}'
                load_val = components_df.loc[feat, pc_name]
                f.write(f" {load_val:.4f} |")
            f.write("\n")
        f.write("\n")
        
        # 5. 模型得分排名
        f.write("## 5. 模型主成分得分\n\n")
        
        for i in range(min(3, n_comp)):
            pc_name = f'PC{i+1}'
            f.write(f"### 5.{i+1} {pc_name} 得分排名\n\n")
            f.write(f"**解释方差**: {explained_var[i]:.2%}\n\n")
            
            pc_scores = transformed_df[pc_name].sort_values(ascending=False)
            
            f.write("| 排名 | 模型 | 得分 | 相对表现 |\n")
            f.write("|------|------|------|----------|\n")
            
            for rank, (model, score) in enumerate(pc_scores.items(), 1):
                performance = "优秀 ⭐⭐⭐" if score > 1 else \
                            "良好 ⭐⭐" if score > 0 else \
                            "一般 ⭐" if score > -1 else "较差"
                f.write(f"| {rank} | {model} | {score:.4f} | {performance} |\n")
            f.write("\n")
        
        # 6. 综合质量得分（加权）
        f.write("## 6. 综合质量得分\n\n")
        f.write("基于主成分的解释方差比例进行加权求和，得到综合质量得分。\n\n")
        
        # 计算加权得分
        weights = explained_var[:n_selected] / explained_var[:n_selected].sum()
        quality_score = pd.Series(0.0, index=transformed_df.index)
        for i in range(n_selected):
            pc_name = f'PC{i+1}'
            quality_score += weights[i] * transformed_df[pc_name]
        
        quality_score_sorted = quality_score.sort_values(ascending=False)
        
        f.write(f"**权重分配**:\n\n")
        for i in range(n_selected):
            f.write(f"- PC{i+1}: {weights[i]:.4f} ({weights[i]*100:.2f}%)\n")
        f.write("\n")
        
        f.write("**综合排名**:\n\n")
        f.write("| 排名 | 模型 | 综合得分 | 评级 |\n")
        f.write("|------|------|----------|------|\n")
        
        for rank, (model, score) in enumerate(quality_score_sorted.items(), 1):
            rating = "S级 ⭐⭐⭐⭐⭐" if rank <= 2 else \
                    "A级 ⭐⭐⭐⭐" if rank <= 4 else \
                    "B级 ⭐⭐⭐" if rank <= 6 else "C级 ⭐⭐"
            f.write(f"| {rank} | {model} | {score:.4f} | {rating} |\n")
        f.write("\n")
        
        # 7. 原始数据统计（如果提供）
        if quality_data is not None:
            f.write("## 7. 原始数据统计\n\n")
            f.write("### 7.1 特征描述性统计\n\n")
            
            stats = quality_data.describe()
            f.write("| 特征 | 均值 | 标准差 | 最小值 | 最大值 |\n")
            f.write("|------|------|--------|--------|--------|\n")
            
            for col in quality_data.columns:
                f.write(f"| {col} | {stats.loc['mean', col]:.4f} | "
                       f"{stats.loc['std', col]:.4f} | "
                       f"{stats.loc['min', col]:.4f} | "
                       f"{stats.loc['max', col]:.4f} |\n")
            f.write("\n")
        
        # 8. 可视化图表
        f.write("## 8. 可视化图表\n\n")
        f.write("本次分析生成了以下可视化图表：\n\n")
        f.write("1. **碎石图** (`pca_scree_plot.png`): 展示各主成分的解释方差比例和累积方差\n")
        f.write("2. **载荷热力图** (`pca_loadings_heatmap.png`): 展示特征在主成分上的载荷矩阵\n")
        if n_comp >= 2:
            f.write("3. **双标图** (`pca_biplot.png`): 同时展示样本和特征的二维投影\n")
        f.write("4. **主成分得分图** (`pca_component_scores.png`): 展示各模型在主成分上的得分\n\n")
        
        # 9. 分析结论
        f.write("## 9. 分析结论\n\n")
        
        # 维度降低效果
        reduction_rate = (1 - n_selected / len(components_df)) * 100
        f.write(f"### 9.1 降维效果\n\n")
        f.write(f"- 从 {len(components_df)} 个原始特征降至 {n_selected} 个主成分\n")
        f.write(f"- 维度降低 {reduction_rate:.1f}%\n")
        f.write(f"- 保留信息量 {cumulative_var[n_selected-1]*100:.1f}%\n\n")
        
        # 最佳模型
        best_model = quality_score_sorted.index[0]
        best_score = quality_score_sorted.iloc[0]
        f.write(f"### 9.2 最佳模型\n\n")
        f.write(f"**{best_model}** 在综合质量评估中表现最佳，得分为 {best_score:.4f}。\n\n")
        
        # 主要发现
        f.write(f"### 9.3 主要发现\n\n")
        f.write(f"1. **主导因素**: PC1 解释了 {explained_var[0]*100:.1f}% 的方差，是最主要的质量维度\n")
        
        # 找出PC1的主要特征
        pc1_loadings = components_df['PC1'].abs().sort_values(ascending=False)
        top_feature = pc1_loadings.index[0]
        f.write(f"2. **关键指标**: {top_feature} 对模型质量影响最大\n")
        f.write(f"3. **模型差异**: 模型在主成分空间中呈现明显的性能分层\n\n")
        
        # 页脚
        f.write("---\n\n")
        f.write(f"**分析方法**: 主成分分析 (PCA)\n\n")
        f.write(f"**生成脚本**: `analysis/qe_research/scripts/pareto_core/shared_functions.py`\n")
    
    if verbose:
        print(f"✓ PCA分析报告已生成: {report_file}")
    
    return report_file


def plot_pca_figures(pca_result, task_name, output_dir, verbose=True):
    """
    绘制PCA分析相关图表
    
    Args:
        pca_result (dict): PCA结果字典，包含：
            - 'transformed': 降维后的数据（DataFrame）
            - 'components': 主成分载荷矩阵（DataFrame）
            - 'explained_variance_ratio': 解释方差比例（array）
            - 'cumulative_variance_ratio': 累积方差比例（array）
            - 'n_components': 实际主成分数量
        task_name (str): 任务名称
        output_dir (Path): 输出目录
        verbose (bool): 是否输出详细信息
    
    Returns:
        dict: 生成的图表文件路径字典
    """
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
    plt.rcParams['axes.unicode_minus'] = False
    
    generated_files = {}
    
    # 1. 解释方差比例图（碎石图）
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    n_comp = pca_result['n_components']
    explained_var = pca_result['explained_variance_ratio']
    cumulative_var = pca_result['cumulative_variance_ratio']
    
    x = np.arange(1, n_comp + 1)
    
    # 绘制柱状图和折线图
    ax.bar(x, explained_var, alpha=0.6, color='steelblue', label='Individual Variance')
    ax.plot(x, cumulative_var, 'ro-', linewidth=2, markersize=8, label='Cumulative Variance')
    
    # 添加85%阈值线
    ax.axhline(y=0.85, color='green', linestyle='--', linewidth=1.5, label='85% Threshold')
    
    ax.set_xlabel('Principal Component', fontsize=12)
    ax.set_ylabel('Explained Variance Ratio', fontsize=12)
    ax.set_title(f'PCA Scree Plot - {task_name.upper()}', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels([f'PC{i}' for i in x])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 添加数值标签
    for i, (ev, cv) in enumerate(zip(explained_var, cumulative_var)):
        ax.text(i+1, ev, f'{ev:.2%}', ha='center', va='bottom', fontsize=8)
        ax.text(i+1, cv, f'{cv:.2%}', ha='center', va='bottom', fontsize=8, color='red')
    
    plt.tight_layout()
    scree_path = output_path / 'pca_scree_plot.png'
    plt.savefig(scree_path, dpi=300, bbox_inches='tight')
    plt.close()
    generated_files['scree_plot'] = scree_path
    
    if verbose:
        print(f"✓ 碎石图已保存: {scree_path}")
    
    # 2. 主成分载荷热力图（前3个主成分）
    components_df = pca_result['components']
    n_show = min(3, n_comp)
    
    fig, ax = plt.subplots(figsize=(10, max(6, len(components_df) * 0.4)), dpi=300)
    
    # 选择前n_show个主成分
    loadings = components_df.iloc[:, :n_show]
    
    # 绘制热力图
    im = ax.imshow(loadings.values, cmap='viridis', aspect='auto', vmin=-1, vmax=1)
    
    # 设置坐标轴
    ax.set_xticks(np.arange(n_show))
    ax.set_yticks(np.arange(len(loadings)))
    ax.set_xticklabels([f'PC{i+1}' for i in range(n_show)], fontsize=10)
    ax.set_yticklabels(loadings.index, fontsize=9)
    
    # 添加数值标签
    for i in range(len(loadings)):
        for j in range(n_show):
            text = ax.text(j, i, f'{loadings.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    ax.set_title(f'PCA Component Loadings - {task_name.upper()}', 
                fontsize=14, fontweight='bold')
    
    # 添加颜色条
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Loading', fontsize=10)
    
    plt.tight_layout()
    loadings_path = output_path / 'pca_loadings_heatmap.png'
    plt.savefig(loadings_path, dpi=300, bbox_inches='tight')
    plt.close()
    generated_files['loadings_heatmap'] = loadings_path
    
    if verbose:
        print(f"✓ 载荷热力图已保存: {loadings_path}")
    
    # 3. 双标图（Biplot）- 仅当有至少2个主成分时
    if n_comp >= 2:
        fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
        
        transformed = pca_result['transformed']
        
        # 绘制样本点（模型）
        ax.scatter(transformed['PC1'], transformed['PC2'], 
                  s=100, alpha=0.6, c='steelblue', edgecolors='black', linewidth=0.5)
        
        # 标注模型名称
        for idx, row in transformed.iterrows():
            ax.annotate(idx, (row['PC1'], row['PC2']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=9, alpha=0.8)
        
        # 绘制特征向量（载荷）
        scale_factor = 3  # 缩放因子，使箭头更明显
        for i, feature in enumerate(components_df.index):
            ax.arrow(0, 0, 
                    components_df.loc[feature, 'PC1'] * scale_factor,
                    components_df.loc[feature, 'PC2'] * scale_factor,
                    head_width=0.1, head_length=0.1, fc='red', ec='red', alpha=0.6)
            ax.text(components_df.loc[feature, 'PC1'] * scale_factor * 1.15,
                   components_df.loc[feature, 'PC2'] * scale_factor * 1.15,
                   feature, fontsize=9, color='red', ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        ax.set_xlabel(f'PC1 ({explained_var[0]:.1%})', fontsize=12)
        ax.set_ylabel(f'PC2 ({explained_var[1]:.1%})', fontsize=12)
        ax.set_title(f'PCA Biplot - {task_name.upper()}', fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.3)
        ax.axvline(x=0, color='k', linestyle='--', linewidth=0.5, alpha=0.3)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        biplot_path = output_path / 'pca_biplot.png'
        plt.savefig(biplot_path, dpi=300, bbox_inches='tight')
        plt.close()
        generated_files['biplot'] = biplot_path
        
        if verbose:
            print(f"✓ 双标图已保存: {biplot_path}")
    
    # 4. 主成分得分排名图（前3个主成分）
    if n_comp >= 1:
        fig, axes = plt.subplots(1, min(3, n_comp), figsize=(15, 5), dpi=300)
        if n_comp == 1:
            axes = [axes]
        
        transformed = pca_result['transformed']
        
        for i in range(min(3, n_comp)):
            pc_name = f'PC{i+1}'
            pc_scores = transformed[pc_name].sort_values(ascending=False)
            
            ax = axes[i] if n_comp > 1 else axes[0]
            colors = ['green' if x > 0 else 'red' for x in pc_scores.values]
            ax.barh(range(len(pc_scores)), pc_scores.values, color=colors, alpha=0.7)
            ax.set_yticks(range(len(pc_scores)))
            ax.set_yticklabels(pc_scores.index, fontsize=9)
            ax.set_xlabel('Score', fontsize=10)
            ax.set_title(f'{pc_name} ({explained_var[i]:.1%})', fontsize=12, fontweight='bold')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=0.8)
            ax.grid(True, alpha=0.3, axis='x')
        
        plt.suptitle(f'PCA Component Scores - {task_name.upper()}', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        scores_path = output_path / 'pca_component_scores.png'
        plt.savefig(scores_path, dpi=300, bbox_inches='tight')
        plt.close()
        generated_files['component_scores'] = scores_path
        
        if verbose:
            print(f"✓ 主成分得分图已保存: {scores_path}")
    
    return generated_files


def load_process_quality_data(task_name, method='entropy', normalize_method='minmax', 
                               use_raw=True, verbose=True,output_dir=None, **kwargs):
    """
    加载并处理质量数据（集成 process_quality_data 模块）
    
    此函数提供统一接口，用于加载质量数据并应用不同的处理方法：
    - 'entropy': 熵权法加权
    - 'pca': PCA降维（取第一主成分）
    - 'mean': 简单平均
    - 'single': 使用单一指标（需指定 quality_column 参数）
    
    Args:
        task_name (str): 任务名称（code, creative, math, qa, reasoning, summary, translation）
        method (str): 处理方法
            - 'entropy': 熵权法加权（默认）
            - 'pca': PCA降维取第一主成分
            - 'mean': 简单平均所有指标
            - 'single': 使用单一指标
        normalize_method (str): 归一化方法（'minmax', 'zscore', 'robust', 'maxabs'）
        use_raw (bool): 是否使用原始数据（保留完整精度）
        verbose (bool): 是否输出详细信息
        **kwargs: 额外参数
            - quality_column (str): 当 method='single' 时，指定使用的质量列名
            - n_components (int): 当 method='pca' 时，PCA主成分数量（默认1）
            - weights (dict): 当 method='custom' 时，自定义权重字典
    
    Returns:
        pd.DataFrame: 包含 'model' 和 'quality' 列的数据框
    
    Examples:
        # 使用熵权法
        df = load_process_quality_data('code', method='entropy')
        
        # 使用单一指标
        df = load_process_quality_data('code', method='single', 
                                       quality_column='compilation_rate')
        
        # 使用PCA
        df = load_process_quality_data('reasoning', method='pca', n_components=1)
        
        # 使用简单平均
        df = load_process_quality_data('creative', method='mean')
    """
    from .process_quality_data import QualityDataProcessor
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"加载质量数据: {task_name.upper()}")
        print(f"处理方法: {method.upper()}")
        print(f"{'='*80}")
    
    # 初始化处理器
    processor = QualityDataProcessor(task_name=task_name, use_raw=use_raw, verbose=verbose)
    
    # 加载数据
    data = processor.load_quality_data()
    
    # 根据方法处理数据
    if method == 'entropy':
        # 熵权法
        weights = processor.calculate_entropy_weights()
        quality_score = processor.get_weighted_quality_score(weights, normalize_first=True)
        
        # 绘制各指标的权重
        if output_dir:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            plt.figure(figsize=(8, 6), dpi=300)
            plt.bar(weights.keys(), weights.values(), color='skyblue')
            plt.xlabel('Metrics', fontsize=12)
            plt.ylabel('Weight', fontsize=12)
            plt.title('Entropy Weights', fontsize=14)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig(output_path / 'entropy_weights.png', dpi=300, bbox_inches='tight')
            plt.close()
            print(f"✓ 权重可视化已保存: {output_path / 'entropy_weights.png'}") 
            
            result_df = pd.DataFrame({
                'model': quality_score.index,
                'quality': quality_score.values
            })
            
            if verbose:
                print(f"\n✓ 熵权法处理完成")
                print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
        
    elif method == 'pca':
        # PCA降维 - 自动选择累积解释方差≥85%的主成分
        # 首先用所有主成分进行PCA，以获取完整的解释方差信息
        pca_result_full = processor.apply_pca(n_components=None, normalize_first=True)
        
        # 计算累积解释方差，选择≥85%的主成分数量
        cumulative_var = pca_result_full['cumulative_variance_ratio']
        n_components_selected = int(np.argmax(cumulative_var >= 0.85) + 1)
        
        # 确保至少选择1个主成分
        n_components_selected = max(1, n_components_selected)
        
        if verbose:
            print(f"\n✓ PCA降维完成")
            print(f"  自动选择主成分数: {n_components_selected}")
            print(f"  累积解释方差: {cumulative_var[n_components_selected-1]:.2%}")
            print(f"\n各主成分解释方差:")
            for i in range(n_components_selected):
                print(f"  PC{i+1}: {pca_result_full['explained_variance_ratio'][i]:.4f} ({pca_result_full['explained_variance_ratio'][i]*100:.2f}%)")
        
        # 绘制PCA相关图表和生成报告
        if output_dir:
            from pathlib import Path
            pca_output_dir = Path(output_dir) / 'pca_analysis'
            
            # 生成可视化图表
            pca_figures = plot_pca_figures(pca_result_full, task_name, pca_output_dir, verbose=verbose)
            
            # 生成详细报告
            report_path = generate_pca_report(
                pca_result=pca_result_full,
                task_name=task_name,
                output_dir=pca_output_dir,
                quality_data=data,
                verbose=verbose
            )
            
            if verbose:
                print(f"\n✓ PCA分析完成")
                print(f"  - 生成图表: {len(pca_figures)} 个")
                print(f"  - 分析报告: {report_path.name}")
        
        # 使用选定的主成分按解释方差比例加权求和
        weights = pca_result_full['explained_variance_ratio'][:n_components_selected]
        weights = weights / weights.sum()  # 归一化权重
        
        # 计算加权综合得分
        quality_score = pd.Series(0.0, index=pca_result_full['transformed'].index)
        for i in range(n_components_selected):
            pc_name = f'PC{i+1}'
            quality_score += weights[i] * pca_result_full['transformed'][pc_name]
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n主成分权重:")
            for i in range(n_components_selected):
                print(f"  PC{i+1}: {weights[i]:.4f} ({weights[i]*100:.2f}%)")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    elif method == 'mean':
        # 简单平均
        normalized = processor.normalize(method=normalize_method)
        quality_score = normalized.mean(axis=1)
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ 简单平均完成")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    elif method == 'single':
        # 使用单一指标
        quality_column = kwargs.get('quality_column')
        if quality_column is None:
            raise ValueError("method='single' 时必须指定 quality_column 参数")
        
        if quality_column not in data.columns:
            raise ValueError(f"指标 '{quality_column}' 不存在。可用指标: {list(data.columns)}")
        
        quality_score = data[quality_column]
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ 使用单一指标: {quality_column}")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    elif method == 'custom':
        # 自定义权重
        weights = kwargs.get('weights')
        if weights is None:
            raise ValueError("method='custom' 时必须指定 weights 参数")
        
        quality_score = processor.get_weighted_quality_score(weights, normalize_first=True)
        
        result_df = pd.DataFrame({
            'model': quality_score.index,
            'quality': quality_score.values
        })
        
        if verbose:
            print(f"\n✓ 自定义权重处理完成")
            print(f"  质量得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
    
    else:
        raise ValueError(f"不支持的处理方法: {method}. "
                        f"支持的方法: 'entropy', 'pca', 'mean', 'single', 'custom'")
    
    # 重置索引
    result_df = result_df.reset_index(drop=True)
    
    if verbose:
        print(f"\n✓ 数据加载完成: {len(result_df)} 个模型")
    
    return result_df



# ============================================================================
# 稳健性分析函数
# ============================================================================

def perturbation_analysis(df, x_col, y_col, x_minimize=True, y_minimize=True, 
                         noise_level=0.05, n_iterations=100):
    """
    扰动分析 - 评估帕累托前沿对数据噪声的敏感性
    
    Args:
        df: 数据框
        x_col: X轴列名
        y_col: Y轴列名
        x_minimize: X轴是否最小化
        y_minimize: Y轴是否最小化
        noise_level: 噪声水平（默认5%）
        n_iterations: 迭代次数（默认100）
    
    Returns:
        dict: 包含稳定性得分和一致性指标的字典
    """
    from collections import Counter
    
    # 原始前沿
    original_pareto = identify_pareto_frontier_2d(df, x_col, y_col, x_minimize, y_minimize)
    original_models = set(df[original_pareto]['model'].tolist())
    
    # 扰动分析
    pareto_models_count = Counter()
    pareto_sets = []
    
    np.random.seed(42)
    for i in range(n_iterations):
        # 添加噪声
        noisy_data = df.copy()
        noisy_data[x_col] = noisy_data[x_col] * (1 + np.random.uniform(-noise_level, noise_level, len(noisy_data)))
        noisy_data[y_col] = noisy_data[y_col] * (1 + np.random.uniform(-noise_level, noise_level, len(noisy_data)))
        
        # 识别前沿
        pareto_mask = identify_pareto_frontier_2d(noisy_data, x_col, y_col, x_minimize, y_minimize)
        pareto_models = noisy_data[pareto_mask]['model'].tolist()
        
        pareto_sets.append(set(pareto_models))
        for model in pareto_models:
            pareto_models_count[model] += 1
    
    # 计算稳定性得分
    stability_scores = {model: count / n_iterations for model, count in pareto_models_count.items()}
    
    # 计算前沿一致性（Jaccard相似度）
    consistency_scores = []
    for pareto_set in pareto_sets:
        if len(pareto_set | original_models) > 0:
            jaccard = len(pareto_set & original_models) / len(pareto_set | original_models)
            consistency_scores.append(jaccard)
    
    mean_consistency = np.mean(consistency_scores) if consistency_scores else 0
    std_consistency = np.std(consistency_scores) if consistency_scores else 0
    
    return {
        'original_models': original_models,
        'stability_scores': stability_scores,
        'model_counts': dict(pareto_models_count),
        'mean_consistency': mean_consistency,
        'std_consistency': std_consistency,
        'n_iterations': n_iterations
    }


def cross_validation_pareto(df, x_col, y_col, x_minimize=True, y_minimize=True, n_folds=5):
    """
    交叉验证分析 - 评估帕累托前沿的泛化能力
    
    Args:
        df: 数据框
        x_col: X轴列名
        y_col: Y轴列名
        x_minimize: X轴是否最小化
        y_minimize: Y轴是否最小化
        n_folds: 折数（默认5）
    
    Returns:
        dict: 包含交叉验证结果的字典
    """
    from collections import Counter
    
    n_models = len(df)
    indices = np.arange(n_models)
    np.random.seed(42)
    np.random.shuffle(indices)
    
    fold_size = n_models // n_folds
    pareto_models_per_fold = []
    
    for fold in range(n_folds):
        # 分割数据
        test_indices = indices[fold * fold_size : (fold + 1) * fold_size]
        train_indices = np.concatenate([indices[:fold * fold_size], indices[(fold + 1) * fold_size:]])
        
        train_data = df.iloc[train_indices].reset_index(drop=True)
        
        # 识别前沿
        pareto_mask = identify_pareto_frontier_2d(train_data, x_col, y_col, x_minimize, y_minimize)
        pareto_models = set(train_data[pareto_mask]['model'].tolist())
        pareto_models_per_fold.append(pareto_models)
    
    # 统计模型出现频率
    model_counts = Counter()
    for pareto_set in pareto_models_per_fold:
        for model in pareto_set:
            model_counts[model] += 1
    
    # 计算一致性
    all_models = set()
    for s in pareto_models_per_fold:
        all_models.update(s)
    
    consistency_scores = []
    for model in all_models:
        appearances = sum(1 for s in pareto_models_per_fold if model in s)
        consistency_scores.append(appearances / n_folds)
    
    mean_consistency = np.mean(consistency_scores) if consistency_scores else 0
    
    return {
        'model_counts': dict(model_counts),
        'mean_consistency': mean_consistency,
        'n_folds': n_folds,
        'pareto_per_fold': pareto_models_per_fold
    }


# ============================================================================
# 报告生成函数
# ============================================================================

def generate_pareto_report(df, results, output_dir, task_config):
    """
    生成帕累托分析报告（通用版本）
    
    Args:
        df: 数据框
        results: 分析结果字典，包含：
            - pareto_qe: 质量-能耗前沿掩码
            - pareto_qs: 质量-速度前沿掩码
            - pareto_3d: 三维前沿掩码
            - hypervolume_qe: 超体积
            - spacing_qe: 间距指标
            - knee_point: 拐点模型
            - robustness_qe: 稳健性分析结果（可选）
            - cross_val_qe: 交叉验证结果（可选）
        output_dir: 输出目录（Path对象）
        task_config: 任务配置字典，包含：
            - task_name: 任务名称（如'code', 'creative'等）
            - task_name_cn: 任务中文名称（如'代码生成', '创意写作'等）
            - quality_metric: 质量指标名称（如'编译成功率', 'Distinct-2'等）
            - report_filename: 报告文件名（可选，默认为'{TASK}_PARETO_ANALYSIS_REPORT.md'）
    
    Returns:
        report_path: 生成的报告文件路径
    """
    from pathlib import Path
    
    # 配置参数
    task_name = task_config.get('task_name', 'unknown')
    task_name_cn = task_config.get('task_name_cn', task_name)
    quality_metric = task_config.get('quality_metric', '质量得分')
    report_filename = task_config.get('report_filename', 
                                     f'{task_name.upper()}_PARETO_ANALYSIS_REPORT.md')
    
    report_file = Path(output_dir) / report_filename
    
    with open(report_file, 'w', encoding='utf-8') as f:
        # 标题和元数据
        f.write(f"# {task_name_cn}任务帕累托前沿分析报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 1. 数据概览
        f.write("## 1. 数据概览\n\n")
        f.write(f"- **任务类型**: {task_name_cn}任务（{task_name}）\n")
        f.write(f"- **模型数量**: {len(df)}\n")
        f.write(f"- **质量指标**: {quality_metric}\n\n")
        
        # 2. 帕累托前沿识别
        f.write("## 2. 帕累托前沿识别\n\n")
        
        # 2.1 质量-能耗前沿
        f.write(f"### 2.1 质量-能耗前沿: {results['pareto_qe'].sum()} 个模型\n\n")
        pareto_qe_models = df[results['pareto_qe']].sort_values('quality', ascending=False)
        for _, row in pareto_qe_models.iterrows():
            f.write(f"- {row['model']}: 质量={row['quality']:.3f}, 能耗={row['energy']:.3f} J/token\n")
        
        # 2.2 质量-速度前沿
        f.write(f"\n### 2.2 质量-速度前沿: {results['pareto_qs'].sum()} 个模型\n\n")
        pareto_qs_models = df[results['pareto_qs']].sort_values('quality', ascending=False)
        for _, row in pareto_qs_models.iterrows():
            f.write(f"- {row['model']}: 质量={row['quality']:.3f}, 速度={row['speed']:.2f} tokens/s\n")
        
        # 2.3 三维前沿
        f.write(f"\n### 2.3 三维前沿: {results['pareto_3d'].sum()} 个模型\n\n")
        pareto_3d_models = df[results['pareto_3d']].sort_values('quality', ascending=False)
        for _, row in pareto_3d_models.iterrows():
            f.write(f"- {row['model']}: 质量={row['quality']:.3f}, 能耗={row['energy']:.3f}, 速度={row['speed']:.2f}\n")
        
        # 3. 定量指标
        f.write("\n## 3. 定量指标\n\n")
        f.write(f"- **超体积（质量-能耗）**: {results['hypervolume_qe']:.4f}\n")
        f.write(f"- **间距指标（质量-能耗）**: {results['spacing_qe']:.4f}\n")
        f.write(f"- **拐点模型**: {results['knee_point']}\n\n")
        
        # 4. 稳健性分析（如果有）
        if 'robustness_qe' in results and 'cross_val_qe' in results:
            f.write("## 4. 稳健性分析\n\n")
            
            # 4.1 扰动分析
            f.write("### 4.1 扰动分析（质量-能耗前沿）\n\n")
            rob = results['robustness_qe']
            f.write(f"**分析设置**: 噪声水平 ±{rob.get('noise_level', 0.05)*100:.0f}%, 迭代 {rob['n_iterations']} 次\n\n")
            f.write(f"**前沿一致性**: {rob['mean_consistency']:.2%} (标准差: {rob['std_consistency']:.2%})\n\n")
            
            if rob.get('stability_scores'):
                f.write("**稳定性得分** (模型在扰动中保持在前沿的频率):\n\n")
                f.write("| 模型 | 稳定性得分 | 出现次数 | 评级 |\n")
                f.write("|------|-----------|---------|------|\n")
                
                sorted_scores = sorted(rob['stability_scores'].items(), 
                                     key=lambda x: x[1], reverse=True)
                for model, score in sorted_scores:
                    count = rob['model_counts'].get(model, 0)
                    rating = "⭐⭐⭐⭐⭐" if score >= 0.9 else \
                            "⭐⭐⭐⭐" if score >= 0.7 else \
                            "⭐⭐⭐" if score >= 0.5 else "⭐⭐"
                    f.write(f"| {model} | {score:.2%} | {count}/{rob['n_iterations']} | {rating} |\n")
                f.write("\n")
            
            # 4.2 交叉验证
            f.write("### 4.2 交叉验证分析\n\n")
            cv = results['cross_val_qe']
            f.write(f"**{cv['n_folds']}折交叉验证一致性**: {cv['mean_consistency']:.2%}\n\n")
            
            if cv.get('model_counts'):
                f.write("**模型出现频率**:\n\n")
                f.write("| 模型 | 出现次数 | 频率 |\n")
                f.write("|------|---------|------|\n")
                
                sorted_counts = sorted(cv['model_counts'].items(), 
                                     key=lambda x: x[1], reverse=True)
                for model, count in sorted_counts:
                    freq = count / cv['n_folds']
                    f.write(f"| {model} | {count}/{cv['n_folds']} | {freq:.0%} |\n")
                f.write("\n")
        
        # 5. 推荐配置
        f.write("## 5. 推荐配置\n\n")
        
        # 检查 DataFrame 是否为空
        if len(df) == 0:
            f.write("⚠ **警告**: 没有可用的模型数据，无法生成推荐配置。\n\n")
            f.write("可能原因：\n")
            f.write("- 所有模型都缺少能耗或速度数据\n")
            f.write("- 模型被排除列表过滤\n")
            f.write("- 数据加载失败\n\n")
        else:
            # 找出最佳模型
            best_quality_model = df.loc[df['quality'].idxmax()]
            best_speed_model = df.loc[df['speed'].idxmax()]
            best_energy_model = df.loc[df['energy'].idxmin()]
            knee_model = df[df['model'] == results['knee_point']].iloc[0] if results['knee_point'] else None
            
            if knee_model is not None:
                f.write(f"### 最佳综合配置: {knee_model['model']} ⭐⭐⭐⭐⭐\n\n")
                f.write(f"- **{quality_metric}**: {knee_model['quality']:.3f}\n")
                f.write(f"- **每token能耗**: {knee_model['energy']:.3f} J/token\n")
                f.write(f"- **生成速度**: {knee_model['speed']:.2f} tokens/s\n")
                f.write(f"- **推荐理由**: 拐点模型，质量-能耗权衡最优\n\n")
            
            f.write(f"### 最高质量: {best_quality_model['model']}\n\n")
            f.write(f"- **{quality_metric}**: {best_quality_model['quality']:.3f}\n")
            f.write(f"- **每token能耗**: {best_quality_model['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_quality_model['speed']:.2f} tokens/s\n\n")
        
        f.write(f"### 最低能耗: {best_energy_model['model']}\n\n")
        f.write(f"- **{quality_metric}**: {best_energy_model['quality']:.3f}\n")
        f.write(f"- **每token能耗**: {best_energy_model['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_energy_model['speed']:.2f} tokens/s\n\n")
        
        f.write(f"### 最快速度: {best_speed_model['model']}\n\n")
        f.write(f"- **{quality_metric}**: {best_speed_model['quality']:.3f}\n")
        f.write(f"- **每token能耗**: {best_speed_model['energy']:.3f} J/token\n")
        f.write(f"- **生成速度**: {best_speed_model['speed']:.2f} tokens/s\n\n")
        
        # 6. 完整数据表
        f.write("## 6. 完整数据表\n\n")
        f.write("| 模型 | 质量 | 能耗(J/token) | 速度(tokens/s) | 质量-能耗前沿 | 质量-速度前沿 | 3D前沿 |\n")
        f.write("|------|------|--------------|---------------|-------------|-------------|--------|\n")
        
        for _, row in df.sort_values('quality', ascending=False).iterrows():
            qe_mark = "✓" if results['pareto_qe'][row.name] else ""
            qs_mark = "✓" if results['pareto_qs'][row.name] else ""
            td_mark = "✓" if results['pareto_3d'][row.name] else ""
            
            f.write(f"| {row['model']} | {row['quality']:.3f} | {row['energy']:.3f} | "
                   f"{row['speed']:.2f} | {qe_mark} | {qs_mark} | {td_mark} |\n")
        
        f.write("\n")
        
        # 页脚
        f.write("---\n\n")
        f.write(f"**生成脚本**: `analysis/qe_research/scripts/pareto_analysis_{task_name}.py`\n")
    
    return report_file


def print_analysis_summary(df, results, task_name_cn="任务"):
    """
    打印分析摘要到控制台
    
    Args:
        df: 数据框
        results: 分析结果字典
        task_name_cn: 任务中文名称
    """
    print("\n" + "="*80)
    print(f"{task_name_cn}分析摘要")
    print("="*80)
    
    print(f"\n📊 数据概览:")
    print(f"  - 模型数量: {len(df)}")
    print(f"  - 质量范围: {df['quality'].min():.3f} - {df['quality'].max():.3f}")
    print(f"  - 能耗范围: {df['energy'].min():.3f} - {df['energy'].max():.3f} J/token")
    print(f"  - 速度范围: {df['speed'].min():.2f} - {df['speed'].max():.2f} tokens/s")
    
    print(f"\n🎯 帕累托前沿:")
    print(f"  - 质量-能耗前沿: {results['pareto_qe'].sum()} 个模型")
    print(f"  - 质量-速度前沿: {results['pareto_qs'].sum()} 个模型")
    print(f"  - 三维前沿: {results['pareto_3d'].sum()} 个模型")
    
    print(f"\n📈 定量指标:")
    print(f"  - 超体积: {results['hypervolume_qe']:.4f}")
    print(f"  - 间距指标: {results['spacing_qe']:.4f}")
    print(f"  - 拐点模型: {results['knee_point']}")
    
    if 'robustness_qe' in results:
        print(f"\n🔒 稳健性:")
        print(f"  - 前沿一致性: {results['robustness_qe']['mean_consistency']:.2%}")
        if 'cross_val_qe' in results:
            print(f"  - 交叉验证: {results['cross_val_qe']['mean_consistency']:.2%}")
    
    print("\n" + "="*80)
