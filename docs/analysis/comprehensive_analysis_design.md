# 综合分析方案设计：质量评估 + 性能指标整合

**版本**: 1.0  
**创建时间**: 2026-03-05  
**目标**: 整合质量评估结果与实验性能数据，构建多维度模型评估体系

---

## 1. 方案概述

### 1.1 核心目标

将已完成的7种任务类型质量评估结果与实验性能指标（能耗、延迟、吞吐量）整合，实现：

1. **数据整合**: 合并 `data/analize/results/` 的质量数据和 `data/experiments_N/summary/` 的性能数据
2. **多维分析**: 质量-效率-能耗三维评估框架
3. **复合指标**: 计算质效比(QE_ratio)、能效加权得分(Score_final)、成本效能比(CPQ)
4. **可视化**: 生成多维度对比图表（散点图、雷达图、热力图、帕累托前沿）
5. **自动化报告**: 生成综合分析报告，支持模型选型决策

### 1.2 数据源

**质量评估数据** (`data/analize/results/`)
- 7种任务类型的质量得分
- 每个任务的详细指标和汇总统计
- 已归一化的质量分数

**性能实验数据** (`data/experiments_N/summary/`)
- 能耗指标: gpu_energy_j, e_token_j
- 时间指标: latency_s, ttft_s, tpot_s
- 吞吐指标: toks_per_s
- 资源利用: gpu_util_avg, gpu_mem_peak_mb

### 1.3 输出产物

- 综合数据文件: `data/analysis/comprehensive_results.csv`
- 复合指标文件: `data/analysis/composite_metrics.csv`
- 可视化图表: `data/analysis/figures/`
- 分析报告: `data/analysis/COMPREHENSIVE_ANALYSIS_REPORT.md`

---

## 2. 数据整合方案

### 2.1 数据匹配策略

**匹配键**: `(model, task_type, question_id)`


**数据结构对齐**:

```python
# 质量数据结构 (来自 data/analize/results/{task}_quality/*_summary.csv)
quality_df = {
    'model': str,           # 模型名称
    'task_type': str,       # 任务类型 (code, creative, math, qa, reasoning, summary, translation)
    'quality_score': float, # 综合质量得分 [0, 1]
    'metric_1': float,      # 任务特定指标1
    'metric_2': float,      # 任务特定指标2
    ...
}

# 性能数据结构 (来自 data/experiments_N/summary/results.csv)
performance_df = {
    'model': str,           # 模型名称
    'task': str,            # 任务类型
    'latency_s': float,     # 延迟(秒)
    'toks_per_s': float,    # 吞吐量(tokens/s)
    'gpu_energy_j': float,  # GPU能耗(焦耳)
    'ttft_s': float,        # 首token时间(秒)
    'tpot_s': float,        # 每token时间(秒)
    ...
}
```

### 2.2 数据清洗与预处理

**步骤1: 模型名称标准化**

```python
def standardize_model_name(name: str) -> str:
    """标准化模型名称"""
    # qwen3:8b, qwen3_8b, Qwen3-8B -> qwen3_8b
    name = name.lower()
    name = name.replace(':', '_').replace('-', '_')
    return name
```

**步骤2: 任务类型映射**

```python
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
```

**步骤3: 缺失值处理**

- 质量数据缺失: 使用任务平均值填充
- 性能数据缺失: 标记为 NaN，在分析中排除
- 完全缺失的模型-任务组合: 从分析中排除


### 2.3 数据整合流程

```python
def integrate_quality_and_performance(
    quality_dir: Path,
    performance_file: Path,
    output_file: Path
) -> pd.DataFrame:
    """整合质量和性能数据"""
    
    # 1. 加载所有质量数据
    quality_data = []
    for task in ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']:
        summary_file = quality_dir / f"{task}_quality" / f"{task}_quality_summary.csv"
        if summary_file.exists():
            df = pd.read_csv(summary_file)
            df['task_type'] = task
            quality_data.append(df)
    
    quality_df = pd.concat(quality_data, ignore_index=True)
    
    # 2. 加载性能数据
    performance_df = pd.read_csv(performance_file)
    
    # 3. 标准化模型名称和任务类型
    quality_df['model'] = quality_df['model'].apply(standardize_model_name)
    performance_df['model'] = performance_df['model'].apply(standardize_model_name)
    performance_df['task_type'] = performance_df['task'].map(TASK_MAPPING)
    
    # 4. 合并数据
    merged_df = pd.merge(
        quality_df,
        performance_df,
        on=['model', 'task_type'],
        how='inner',  # 只保留两边都有的数据
        suffixes=('_quality', '_performance')
    )
    
    # 5. 保存整合数据
    merged_df.to_csv(output_file, index=False, encoding='utf-8')
    
    return merged_df
```

---

## 3. 复合指标计算

### 3.1 归一化处理

**按任务分组归一化** (Min-Max Scaling)

```python
def normalize_by_task(df: pd.DataFrame, metrics: list) -> pd.DataFrame:
    """按任务类型归一化指标"""
    df_norm = df.copy()
    
    for task in df['task_type'].unique():
        task_mask = df['task_type'] == task
        
        for metric in metrics:
            if metric in df.columns:
                values = df.loc[task_mask, metric]
                
                # 判断指标方向 (越大越好 vs 越小越好)
                if metric in ['quality_score', 'toks_per_s', 'throughput']:
                    # 越大越好
                    min_val, max_val = values.min(), values.max()
                    if max_val > min_val:
                        df_norm.loc[task_mask, f'{metric}_norm'] = \
                            (values - min_val) / (max_val - min_val)
                else:
                    # 越小越好 (latency, energy)
                    min_val, max_val = values.min(), values.max()
                    if max_val > min_val:
                        df_norm.loc[task_mask, f'{metric}_norm'] = \
                            1 - (values - min_val) / (max_val - min_val)
    
    return df_norm
```


### 3.2 效率得分 (Efficiency Score)

根据实验设计文档的定义:

```python
def calculate_efficiency_score(df: pd.DataFrame) -> pd.DataFrame:
    """计算效率得分"""
    df['efficiency_score'] = (
        0.4 * df['toks_per_s_norm'] +      # 吞吐量权重 40%
        0.3 * df['latency_s_norm'] +        # 延迟权重 30%
        0.3 * df['gpu_energy_j_norm']       # 能耗权重 30%
    )
    return df
```

### 3.3 质效比 (QE Ratio)

```python
def calculate_qe_ratio(df: pd.DataFrame, epsilon=0.01) -> pd.DataFrame:
    """计算质效比"""
    df['qe_ratio'] = (
        (df['quality_score_norm'] + epsilon) / 
        (1.01 - df['efficiency_score'])
    )
    return df
```

### 3.4 能效加权得分 (Score Final)

```python
def calculate_score_final(df: pd.DataFrame) -> pd.DataFrame:
    """计算最终得分"""
    # 方法1: 质量 × 每瓦性能
    df['ppw'] = df['toks_per_s'] / (df['gpu_power_avg_w'] + 1e-6)
    df['score_final_v1'] = df['quality_score'] * df['ppw']
    
    # 方法2: 质量 / 每token能耗
    df['e_token_j'] = df['gpu_energy_j'] / (df['n_tokens'] + 1)
    df['score_final_v2'] = df['quality_score'] / (df['e_token_j'] + 1e-6)
    
    # 使用方法2作为主要指标
    df['score_final'] = df['score_final_v2']
    
    return df
```

### 3.5 成本效能比 (CPQ)

```python
def calculate_cost_metrics(
    df: pd.DataFrame,
    gpu_hourly_rate: float = 0.75,  # $/h (RTX 4060 Laptop等效)
    electricity_price: float = 0.08  # $/kWh (中国平均)
) -> pd.DataFrame:
    """计算成本指标"""
    
    # GPU成本
    df['cost_gpu_usd'] = (df['latency_s'] / 3600) * gpu_hourly_rate
    
    # 能耗成本
    df['cost_energy_usd'] = (df['gpu_energy_j'] / (3.6 * 1e6)) * electricity_price
    
    # 总成本
    df['cost_total_usd'] = df['cost_gpu_usd'] + df['cost_energy_usd']
    
    # 单位成本质量 (Cost Per Quality)
    df['cpq'] = df['quality_score'] / (df['cost_total_usd'] + 1e-6)
    
    return df
```

---

## 4. 多维度分析框架

### 4.1 任务维度分析

**目标**: 评估每个模型在不同任务上的表现

```python
def analyze_by_task(df: pd.DataFrame) -> pd.DataFrame:
    """按任务分析模型表现"""
    
    task_analysis = df.groupby(['model', 'task_type']).agg({
        'quality_score': 'mean',
        'efficiency_score': 'mean',
        'qe_ratio': 'mean',
        'score_final': 'mean',
        'latency_s': 'mean',
        'gpu_energy_j': 'mean'
    }).reset_index()
    
    # 计算每个模型的最佳任务
    best_tasks = task_analysis.loc[
        task_analysis.groupby('model')['qe_ratio'].idxmax()
    ]
    
    return task_analysis, best_tasks
```


### 4.2 模型维度分析

**目标**: 综合评估每个模型的整体表现

```python
def analyze_by_model(df: pd.DataFrame) -> pd.DataFrame:
    """按模型分析综合表现"""
    
    model_analysis = df.groupby('model').agg({
        'quality_score': ['mean', 'std'],
        'efficiency_score': ['mean', 'std'],
        'qe_ratio': ['mean', 'std'],
        'score_final': ['mean', 'std'],
        'latency_s': ['mean', 'std'],
        'gpu_energy_j': ['mean', 'std'],
        'cpq': 'mean'
    }).round(4)
    
    # 展平列名
    model_analysis.columns = ['_'.join(col).strip() for col in model_analysis.columns.values]
    
    # 综合排名
    model_analysis['综合排名'] = model_analysis['qe_ratio_mean'].rank(ascending=False)
    
    return model_analysis.sort_values('综合排名')
```

### 4.3 帕累托前沿分析

**目标**: 识别质量-能效权衡的最优模型集合

```python
def pareto_frontier_analysis(df: pd.DataFrame) -> tuple:
    """帕累托前沿分析"""
    
    # 按任务分组分析
    pareto_models = {}
    
    for task in df['task_type'].unique():
        task_df = df[df['task_type'] == task].copy()
        
        # 计算帕累托前沿
        is_pareto = np.ones(len(task_df), dtype=bool)
        
        for i, row_i in task_df.iterrows():
            for j, row_j in task_df.iterrows():
                if i != j:
                    # 模型j帕累托支配模型i: 质量更高且能耗更低
                    if (row_j['quality_score'] >= row_i['quality_score'] and
                        row_j['gpu_energy_j'] <= row_i['gpu_energy_j'] and
                        (row_j['quality_score'] > row_i['quality_score'] or
                         row_j['gpu_energy_j'] < row_i['gpu_energy_j'])):
                        is_pareto[task_df.index.get_loc(i)] = False
                        break
        
        pareto_models[task] = task_df[is_pareto]['model'].tolist()
    
    return pareto_models, task_df[is_pareto]
```

### 4.4 公平性分析 (基于RLHF文献)

**目标**: 评估模型在不同任务间的公平性

```python
def fairness_analysis(df: pd.DataFrame) -> dict:
    """公平性分析"""
    
    fairness_metrics = {}
    
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        
        # 1. 公平差距 (Fairness Gap)
        task_means = model_df.groupby('task_type')['quality_score'].mean()
        global_mean = model_df['quality_score'].mean()
        fairness_gap = (task_means - global_mean).abs().max()
        
        # 2. 基尼系数 (Gini Coefficient)
        quality_scores = model_df['quality_score'].sort_values().values
        n = len(quality_scores)
        gini = (2 * np.sum((np.arange(1, n+1)) * quality_scores)) / (n * np.sum(quality_scores)) - (n + 1) / n
        
        # 3. 变异系数 (Coefficient of Variation)
        cv = model_df['quality_score'].std() / (model_df['quality_score'].mean() + 1e-6)
        
        fairness_metrics[model] = {
            'fairness_gap': fairness_gap,
            'gini_coefficient': gini,
            'cv': cv,
            'task_quality_range': task_means.max() - task_means.min()
        }
    
    return pd.DataFrame(fairness_metrics).T
```

---

## 5. 可视化方案

### 5.1 核心对比图表

**图表1: 质量-能耗散点图 (Quality vs Energy)**

```python
def plot_quality_vs_energy(df: pd.DataFrame, output_dir: Path):
    """质量-能耗散点图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    for task in df['task_type'].unique():
        task_df = df[df['task_type'] == task]
        ax.scatter(
            task_df['gpu_energy_j'],
            task_df['quality_score'],
            label=task,
            s=100,
            alpha=0.6
        )
    
    ax.set_xlabel('GPU能耗 (J)', fontsize=12)
    ax.set_ylabel('质量得分', fontsize=12)
    ax.set_title('质量-能耗权衡分析', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'quality_vs_energy.png', dpi=300, bbox_inches='tight')
    plt.close()
```


**图表2: 吞吐量-延迟散点图 (Throughput vs Latency)**

```python
def plot_throughput_vs_latency(df: pd.DataFrame, output_dir: Path):
    """吞吐量-延迟散点图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    models = df['model'].unique()
    colors = sns.color_palette('husl', len(models))
    
    for idx, model in enumerate(models):
        model_df = df[df['model'] == model]
        ax.scatter(
            model_df['latency_s'],
            model_df['toks_per_s'],
            label=model,
            s=100,
            alpha=0.6,
            color=colors[idx]
        )
    
    ax.set_xlabel('延迟 (秒)', fontsize=12)
    ax.set_ylabel('吞吐量 (tokens/s)', fontsize=12)
    ax.set_title('吞吐量-延迟权衡分析', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'throughput_vs_latency.png', dpi=300, bbox_inches='tight')
    plt.close()
```

**图表3: 质效比柱状图 (QE Ratio Comparison)**

```python
def plot_qe_ratio_bars(df: pd.DataFrame, output_dir: Path):
    """质效比柱状图"""
    # 按模型和任务计算平均质效比
    qe_data = df.groupby(['model', 'task_type'])['qe_ratio'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    tasks = qe_data['task_type'].unique()
    x = np.arange(len(tasks))
    width = 0.15
    
    models = qe_data['model'].unique()
    for idx, model in enumerate(models):
        model_data = qe_data[qe_data['model'] == model]
        values = [model_data[model_data['task_type'] == task]['qe_ratio'].values[0] 
                  if len(model_data[model_data['task_type'] == task]) > 0 else 0 
                  for task in tasks]
        ax.bar(x + idx * width, values, width, label=model)
    
    ax.set_xlabel('任务类型', fontsize=12)
    ax.set_ylabel('质效比', fontsize=12)
    ax.set_title('各模型在不同任务上的质效比对比', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width * (len(models) - 1) / 2)
    ax.set_xticklabels(tasks, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'qe_ratio_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
```

**图表4: 综合能力雷达图 (Radar Chart)**

```python
def plot_comprehensive_radar(df: pd.DataFrame, output_dir: Path):
    """综合能力雷达图"""
    # 选择Top 5模型
    top_models = df.groupby('model')['qe_ratio'].mean().nlargest(5).index
    
    # 计算各维度归一化得分
    metrics = ['quality_score_norm', 'toks_per_s_norm', 
               'latency_s_norm', 'gpu_energy_j_norm']
    metric_labels = ['质量', '吞吐量', '延迟优化', '能耗优化']
    
    model_scores = df[df['model'].isin(top_models)].groupby('model')[metrics].mean()
    
    # 绘制雷达图
    N = len(metrics)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    colors = sns.color_palette('husl', len(top_models))
    
    for idx, (model, row) in enumerate(model_scores.iterrows()):
        values = row.tolist()
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=model, color=colors[idx])
        ax.fill(angles, values, alpha=0.15, color=colors[idx])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels, size=11)
    ax.set_ylim(0, 1)
    ax.set_title('Top 5 模型综合能力雷达图', size=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'comprehensive_radar.png', dpi=300, bbox_inches='tight')
    plt.close()
```


**图表5: 帕累托前沿图 (Pareto Frontier)**

```python
def plot_pareto_frontier(df: pd.DataFrame, pareto_df: pd.DataFrame, output_dir: Path):
    """帕累托前沿图"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 绘制所有点
    ax.scatter(
        df['gpu_energy_j'],
        df['quality_score'],
        s=80,
        alpha=0.4,
        color='gray',
        label='所有模型'
    )
    
    # 高亮帕累托前沿
    ax.scatter(
        pareto_df['gpu_energy_j'],
        pareto_df['quality_score'],
        s=150,
        alpha=0.8,
        color='red',
        marker='*',
        label='帕累托前沿'
    )
    
    # 标注帕累托前沿模型
    for _, row in pareto_df.iterrows():
        ax.annotate(
            row['model'],
            (row['gpu_energy_j'], row['quality_score']),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=9
        )
    
    ax.set_xlabel('GPU能耗 (J)', fontsize=12)
    ax.set_ylabel('质量得分', fontsize=12)
    ax.set_title('帕累托前沿分析：质量-能耗权衡', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'pareto_frontier.png', dpi=300, bbox_inches='tight')
    plt.close()
```

**图表6: 模型-任务热力图 (Heatmap)**

```python
def plot_model_task_heatmap(df: pd.DataFrame, output_dir: Path):
    """模型-任务质效比热力图"""
    pivot_data = df.pivot_table(
        values='qe_ratio',
        index='model',
        columns='task_type',
        aggfunc='mean'
    )
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt='.3f',
        cmap='RdYlGn',
        ax=ax,
        cbar_kws={'label': '质效比'}
    )
    
    ax.set_title('模型-任务质效比热力图', fontsize=14, fontweight='bold')
    ax.set_xlabel('任务类型', fontsize=12)
    ax.set_ylabel('模型', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'model_task_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
```

**图表7: 公平性分析图 (Fairness Analysis)**

```python
def plot_fairness_analysis(fairness_df: pd.DataFrame, output_dir: Path):
    """公平性分析图"""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. 公平差距对比
    ax1 = axes[0, 0]
    fairness_df['fairness_gap'].sort_values().plot(kind='barh', ax=ax1, color='coral')
    ax1.set_title('公平差距 (Fairness Gap)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('公平差距')
    ax1.grid(axis='x', alpha=0.3)
    
    # 2. 基尼系数对比
    ax2 = axes[0, 1]
    fairness_df['gini_coefficient'].sort_values().plot(kind='barh', ax=ax2, color='steelblue')
    ax2.set_title('基尼系数 (Gini Coefficient)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('基尼系数')
    ax2.grid(axis='x', alpha=0.3)
    
    # 3. 变异系数对比
    ax3 = axes[1, 0]
    fairness_df['cv'].sort_values().plot(kind='barh', ax=ax3, color='seagreen')
    ax3.set_title('变异系数 (CV)', fontsize=12, fontweight='bold')
    ax3.set_xlabel('变异系数')
    ax3.grid(axis='x', alpha=0.3)
    
    # 4. 任务质量范围
    ax4 = axes[1, 1]
    fairness_df['task_quality_range'].sort_values().plot(kind='barh', ax=ax4, color='purple')
    ax4.set_title('任务质量范围', fontsize=12, fontweight='bold')
    ax4.set_xlabel('质量范围')
    ax4.grid(axis='x', alpha=0.3)
    
    plt.suptitle('模型公平性综合分析', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'fairness_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
```

### 5.2 高级分析图表

**图表8: 成本效益分析 (Cost-Benefit Analysis)**

```python
def plot_cost_benefit_analysis(df: pd.DataFrame, output_dir: Path):
    """成本效益分析图"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 1. 成本-质量散点图
    ax1 = axes[0]
    for model in df['model'].unique():
        model_df = df[df['model'] == model]
        ax1.scatter(
            model_df['cost_total_usd'],
            model_df['quality_score'],
            label=model,
            s=100,
            alpha=0.6
        )
    ax1.set_xlabel('总成本 (USD)', fontsize=12)
    ax1.set_ylabel('质量得分', fontsize=12)
    ax1.set_title('成本-质量权衡', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # 2. CPQ对比
    ax2 = axes[1]
    cpq_data = df.groupby('model')['cpq'].mean().sort_values(ascending=False)
    cpq_data.plot(kind='bar', ax=ax2, color='teal')
    ax2.set_title('单位成本质量 (CPQ) 排名', fontsize=12, fontweight='bold')
    ax2.set_xlabel('模型')
    ax2.set_ylabel('CPQ (质量/美元)')
    ax2.grid(axis='y', alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'cost_benefit_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
```

---

## 6. 自动化报告生成

### 6.1 报告结构

```markdown
# 综合分析报告：质量-性能-能耗评估

**生成时间**: {timestamp}
**实验批次**: experiments_{N}
**评估模型数**: {n_models}
**评估任务数**: {n_tasks}

---

## 1. 执行摘要

### 1.1 关键发现
- 综合表现最佳模型: {best_model}
- 能效最优模型: {most_efficient_model}
- 质量最高模型: {highest_quality_model}
- 成本效益最优: {best_cpq_model}

### 1.2 推荐建议
- 实时对话场景: 推荐 {model_for_realtime}
- 批量处理场景: 推荐 {model_for_batch}
- 质量优先场景: 推荐 {model_for_quality}
- 成本敏感场景: 推荐 {model_for_cost}

---

## 2. 模型综合排名

| 排名 | 模型 | 质效比 | 质量得分 | 效率得分 | 能耗(J) | CPQ |
|------|------|--------|----------|----------|---------|-----|
| ... | ... | ... | ... | ... | ... | ... |

---

## 3. 任务维度分析

### 3.1 各任务最佳模型

| 任务类型 | 最佳模型 | 质效比 | 质量 | 延迟(s) | 能耗(J) |
|---------|---------|--------|------|---------|---------|
| ... | ... | ... | ... | ... | ... |

### 3.2 任务难度分析

...

---

## 4. 帕累托前沿分析

### 4.1 最优模型集合

...

### 4.2 应用场景匹配

...

---

## 5. 公平性评估

### 5.1 跨任务公平性

...

### 5.2 公平性指标对比

...

---

## 6. 成本效益分析

### 6.1 TCO模型

...

### 6.2 投资回报建议

...

---

## 7. 详细数据

### 7.1 完整指标表

...

### 7.2 可视化图表

- 质量-能耗散点图: `figures/quality_vs_energy.png`
- 吞吐量-延迟散点图: `figures/throughput_vs_latency.png`
- ...

---

## 附录

### A. 数据文件

- 综合数据: `comprehensive_results.csv`
- 复合指标: `composite_metrics.csv`
- 公平性分析: `fairness_metrics.csv`

### B. 方法论

...
```


### 6.2 报告生成脚本

```python
def generate_comprehensive_report(
    df: pd.DataFrame,
    model_analysis: pd.DataFrame,
    task_analysis: pd.DataFrame,
    pareto_models: dict,
    fairness_df: pd.DataFrame,
    output_file: Path
):
    """生成综合分析报告"""
    
    report = []
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 标题和元数据
    report.append("# 综合分析报告：质量-性能-能耗评估\n\n")
    report.append(f"**生成时间**: {timestamp}\n")
    report.append(f"**评估模型数**: {df['model'].nunique()}\n")
    report.append(f"**评估任务数**: {df['task_type'].nunique()}\n")
    report.append(f"**总样本数**: {len(df)}\n\n")
    report.append("---\n\n")
    
    # 1. 执行摘要
    report.append("## 1. 执行摘要\n\n")
    
    best_model = model_analysis.iloc[0].name
    best_qe = model_analysis.iloc[0]['qe_ratio_mean']
    
    report.append("### 1.1 关键发现\n\n")
    report.append(f"- **综合表现最佳模型**: {best_model} (质效比: {best_qe:.4f})\n")
    
    most_efficient = df.groupby('model')['efficiency_score'].mean().idxmax()
    report.append(f"- **能效最优模型**: {most_efficient}\n")
    
    highest_quality = df.groupby('model')['quality_score'].mean().idxmax()
    report.append(f"- **质量最高模型**: {highest_quality}\n")
    
    best_cpq = df.groupby('model')['cpq'].mean().idxmax()
    report.append(f"- **成本效益最优**: {best_cpq}\n\n")
    
    # 2. 模型综合排名
    report.append("## 2. 模型综合排名\n\n")
    report.append("| 排名 | 模型 | 质效比 | 质量得分 | 效率得分 | 平均能耗(J) | CPQ |\n")
    report.append("|------|------|--------|----------|----------|-------------|-----|\n")
    
    for rank, (model, row) in enumerate(model_analysis.iterrows(), 1):
        report.append(
            f"| {rank} | {model} | {row['qe_ratio_mean']:.4f} | "
            f"{row['quality_score_mean']:.4f} | {row['efficiency_score_mean']:.4f} | "
            f"{row['gpu_energy_j_mean']:.2f} | {row['cpq']:.4f} |\n"
        )
    report.append("\n")
    
    # 3. 任务维度分析
    report.append("## 3. 任务维度分析\n\n")
    report.append("### 3.1 各任务最佳模型\n\n")
    report.append("| 任务类型 | 最佳模型 | 质效比 | 质量 | 延迟(s) | 能耗(J) |\n")
    report.append("|---------|---------|--------|------|---------|----------|\n")
    
    for task in df['task_type'].unique():
        task_df = df[df['task_type'] == task]
        best_idx = task_df['qe_ratio'].idxmax()
        best_row = task_df.loc[best_idx]
        
        report.append(
            f"| {task} | {best_row['model']} | {best_row['qe_ratio']:.4f} | "
            f"{best_row['quality_score']:.4f} | {best_row['latency_s']:.3f} | "
            f"{best_row['gpu_energy_j']:.2f} |\n"
        )
    report.append("\n")
    
    # 4. 帕累托前沿
    report.append("## 4. 帕累托前沿分析\n\n")
    report.append("### 4.1 各任务帕累托最优模型\n\n")
    
    for task, models in pareto_models.items():
        report.append(f"- **{task}**: {', '.join(models)}\n")
    report.append("\n")
    
    # 5. 公平性评估
    report.append("## 5. 公平性评估\n\n")
    report.append("### 5.1 公平性指标对比\n\n")
    report.append("| 模型 | 公平差距 | 基尼系数 | 变异系数 | 质量范围 |\n")
    report.append("|------|----------|----------|----------|----------|\n")
    
    for model, row in fairness_df.iterrows():
        report.append(
            f"| {model} | {row['fairness_gap']:.4f} | {row['gini_coefficient']:.4f} | "
            f"{row['cv']:.4f} | {row['task_quality_range']:.4f} |\n"
        )
    report.append("\n")
    
    most_fair = fairness_df['fairness_gap'].idxmin()
    report.append(f"**最公平模型** (公平差距最小): {most_fair}\n\n")
    
    # 6. 可视化图表
    report.append("## 6. 可视化图表\n\n")
    report.append("- 质量-能耗散点图: `figures/quality_vs_energy.png`\n")
    report.append("- 吞吐量-延迟散点图: `figures/throughput_vs_latency.png`\n")
    report.append("- 质效比对比图: `figures/qe_ratio_comparison.png`\n")
    report.append("- 综合能力雷达图: `figures/comprehensive_radar.png`\n")
    report.append("- 帕累托前沿图: `figures/pareto_frontier.png`\n")
    report.append("- 模型-任务热力图: `figures/model_task_heatmap.png`\n")
    report.append("- 公平性分析图: `figures/fairness_analysis.png`\n")
    report.append("- 成本效益分析图: `figures/cost_benefit_analysis.png`\n\n")
    
    # 7. 数据文件
    report.append("## 7. 详细数据文件\n\n")
    report.append("- 综合数据: `comprehensive_results.csv`\n")
    report.append("- 复合指标: `composite_metrics.csv`\n")
    report.append("- 模型分析: `model_analysis.csv`\n")
    report.append("- 任务分析: `task_analysis.csv`\n")
    report.append("- 公平性指标: `fairness_metrics.csv`\n\n")
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"✅ 报告已保存: {output_file}")
```

---

## 7. 实现脚本

### 7.1 主脚本结构

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合分析脚本：整合质量评估和性能数据
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# 配置
QUALITY_DIR = Path("data/analize/results")
PERFORMANCE_FILE = Path("data/experiments_1/summary/results.csv")
OUTPUT_DIR = Path("data/analysis")
OUTPUT_DIR.mkdir(exist_ok=True)
FIGURES_DIR = OUTPUT_DIR / "figures"
FIGURES_DIR.mkdir(exist_ok=True)

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def main():
    """主函数"""
    print("\n" + "="*60)
    print("📊 综合分析：质量评估 + 性能指标整合")
    print("="*60 + "\n")
    
    # 1. 数据整合
    print("📂 步骤1: 整合质量和性能数据...")
    df = integrate_quality_and_performance(
        QUALITY_DIR,
        PERFORMANCE_FILE,
        OUTPUT_DIR / "comprehensive_results.csv"
    )
    print(f"✅ 整合完成，共 {len(df)} 条记录\n")
    
    # 2. 归一化
    print("🔢 步骤2: 归一化处理...")
    metrics_to_normalize = [
        'quality_score', 'toks_per_s', 'latency_s', 'gpu_energy_j'
    ]
    df_norm = normalize_by_task(df, metrics_to_normalize)
    print("✅ 归一化完成\n")
    
    # 3. 计算复合指标
    print("📈 步骤3: 计算复合指标...")
    df_norm = calculate_efficiency_score(df_norm)
    df_norm = calculate_qe_ratio(df_norm)
    df_norm = calculate_score_final(df_norm)
    df_norm = calculate_cost_metrics(df_norm)
    df_norm.to_csv(OUTPUT_DIR / "composite_metrics.csv", index=False, encoding='utf-8')
    print("✅ 复合指标计算完成\n")
    
    # 4. 多维度分析
    print("🔍 步骤4: 多维度分析...")
    model_analysis = analyze_by_model(df_norm)
    task_analysis, best_tasks = analyze_by_task(df_norm)
    pareto_models, pareto_df = pareto_frontier_analysis(df_norm)
    fairness_df = fairness_analysis(df_norm)
    
    # 保存分析结果
    model_analysis.to_csv(OUTPUT_DIR / "model_analysis.csv", encoding='utf-8')
    task_analysis.to_csv(OUTPUT_DIR / "task_analysis.csv", index=False, encoding='utf-8')
    fairness_df.to_csv(OUTPUT_DIR / "fairness_metrics.csv", encoding='utf-8')
    print("✅ 分析完成\n")
    
    # 5. 生成可视化
    print("📊 步骤5: 生成可视化图表...")
    plot_quality_vs_energy(df_norm, FIGURES_DIR)
    plot_throughput_vs_latency(df_norm, FIGURES_DIR)
    plot_qe_ratio_bars(df_norm, FIGURES_DIR)
    plot_comprehensive_radar(df_norm, FIGURES_DIR)
    plot_pareto_frontier(df_norm, pareto_df, FIGURES_DIR)
    plot_model_task_heatmap(df_norm, FIGURES_DIR)
    plot_fairness_analysis(fairness_df, FIGURES_DIR)
    plot_cost_benefit_analysis(df_norm, FIGURES_DIR)
    print("✅ 可视化完成\n")
    
    # 6. 生成报告
    print("📝 步骤6: 生成综合报告...")
    generate_comprehensive_report(
        df_norm,
        model_analysis,
        task_analysis,
        pareto_models,
        fairness_df,
        OUTPUT_DIR / "COMPREHENSIVE_ANALYSIS_REPORT.md"
    )
    print("✅ 报告生成完成\n")
    
    print("="*60)
    print("✅ 综合分析完成!")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
```

---

## 8. 使用指南

### 8.1 前置条件

1. 已完成质量评估，生成 `data/analize/results/{task}_quality/*_summary.csv`
2. 已完成性能实验，生成 `data/experiments_N/summary/results.csv`
3. 安装依赖: `pandas`, `numpy`, `matplotlib`, `seaborn`

### 8.2 运行步骤

```bash
# 1. 激活环境
conda activate bartscore

# 2. 设置编码
set PYTHONUTF8=1

# 3. 运行综合分析
python scripts/comprehensive_analysis.py

# 4. 查看结果
# - 报告: data/analysis/COMPREHENSIVE_ANALYSIS_REPORT.md
# - 图表: data/analysis/figures/
# - 数据: data/analysis/*.csv
```

### 8.3 自定义配置

```python
# 修改脚本中的配置
QUALITY_DIR = Path("data/analize/results")  # 质量数据目录
PERFORMANCE_FILE = Path("data/experiments_2/summary/results.csv")  # 性能数据文件
OUTPUT_DIR = Path("data/analysis_v2")  # 输出目录

# 调整复合指标权重
def calculate_efficiency_score(df: pd.DataFrame) -> pd.DataFrame:
    df['efficiency_score'] = (
        0.5 * df['toks_per_s_norm'] +      # 调整吞吐量权重为50%
        0.25 * df['latency_s_norm'] +      # 调整延迟权重为25%
        0.25 * df['gpu_energy_j_norm']     # 调整能耗权重为25%
    )
    return df
```

---

## 9. 预期输出

### 9.1 数据文件

- `comprehensive_results.csv`: 整合的原始数据 (质量+性能)
- `composite_metrics.csv`: 包含所有复合指标的完整数据
- `model_analysis.csv`: 按模型汇总的分析结果
- `task_analysis.csv`: 按任务汇总的分析结果
- `fairness_metrics.csv`: 公平性指标

### 9.2 可视化图表

- `quality_vs_energy.png`: 质量-能耗散点图
- `throughput_vs_latency.png`: 吞吐量-延迟散点图
- `qe_ratio_comparison.png`: 质效比柱状图
- `comprehensive_radar.png`: 综合能力雷达图
- `pareto_frontier.png`: 帕累托前沿图
- `model_task_heatmap.png`: 模型-任务热力图
- `fairness_analysis.png`: 公平性分析图
- `cost_benefit_analysis.png`: 成本效益分析图

### 9.3 分析报告

`COMPREHENSIVE_ANALYSIS_REPORT.md`: 包含执行摘要、排名、分析、建议的完整报告

---

## 10. 后续扩展

### 10.1 短期扩展 (1-2周)

- 支持多个实验批次对比
- 添加统计显著性检验
- 支持自定义指标权重
- 添加交互式可视化 (Plotly)

### 10.2 中期扩展 (1-2月)

- Web界面展示
- 实时监控仪表板
- 自动化CI/CD集成
- 支持更多任务类型

### 10.3 长期扩展 (3-6月)

- 机器学习模型预测
- 自动化模型选型推荐
- 多模态评估支持
- 分布式评估框架

---

**文档版本**: 1.0  
**创建时间**: 2026-03-05  
**作者**: AI Assistant  
**状态**: 设计完成，待实现
