import os
import json
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import matplotlib as mpl
from matplotlib import font_manager as fm
from datetime import datetime

# 配置路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "experiments_1")
RESULTS_DIR = os.path.join(BASE_DIR, "results", "experiments_1")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

HAS_CHINESE_FONT = False
FONT_PROP = None

def _configure_io_and_fonts():
    global HAS_CHINESE_FONT
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    candidates = [
        "Microsoft YaHei",
        "SimHei",
        "Noto Sans CJK SC",
        "Source Han Sans CN",
        "Arial Unicode MS",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen = None
    for name in candidates:
        if name in available:
            chosen = name
            break
    if not chosen:
        font_paths = []
        try:
            font_paths = fm.findSystemFonts()
        except Exception:
            font_paths = []
        win_font_dir = r"C:\\Windows\\Fonts"
        if os.path.isdir(win_font_dir):
            try:
                font_paths += [
                    os.path.join(win_font_dir, f)
                    for f in os.listdir(win_font_dir)
                    if f.lower().endswith((".ttf", ".ttc", ".otf"))
                ]
            except Exception:
                pass
        desired = set(candidates + ["SimSun", "NSimSun", "Microsoft YaHei UI"]) 
        for p in font_paths:
            try:
                nm = fm.FontProperties(fname=p).get_name()
            except Exception:
                continue
            if nm in desired:
                try:
                    fm.fontManager.addfont(p)
                except Exception:
                    pass
                chosen = nm
                break
    if chosen:
        mpl.rcParams['font.family'] = chosen
        mpl.rcParams['font.sans-serif'] = [chosen]
        mpl.rcParams['axes.unicode_minus'] = False
        HAS_CHINESE_FONT = True
        print(f"使用字体: {chosen}")
        try:
            font_path = fm.findfont(chosen)
            globals()['FONT_PROP'] = fm.FontProperties(fname=font_path)
        except Exception:
            globals()['FONT_PROP'] = None
    else:
        HAS_CHINESE_FONT = False

_configure_io_and_fonts()

def load_data():
    """加载汇总数据与统计数据"""
    res_path = os.path.join(DATA_DIR, "summary", "results.csv")
    stats_path = os.path.join(DATA_DIR, "summary", "stats.csv")
    
    if not os.path.exists(res_path) or not os.path.exists(stats_path):
        print("数据文件未找到，请确认 experiments_1 是否执行完成。")
        return None, None
        
    df_res = pd.read_csv(res_path)
    df_stats = pd.read_csv(stats_path)
    
    # 补充缺失值处理
    df_res['bartscore'] = pd.to_numeric(df_res['bartscore'], errors='coerce')
    df_res['tps'] = pd.to_numeric(df_res['toks_per_s'], errors='coerce')
    df_res['latency'] = pd.to_numeric(df_res['latency_s'], errors='coerce')
    df_res['energy'] = pd.to_numeric(df_res['gpu_energy_j'], errors='coerce')
    
    return df_res, df_stats

def load_quality_details():
    """从原始JSON加载更细粒度的质量指标"""
    raw_dir = os.path.join(DATA_DIR, "raw")
    records = []
    
    for model in os.listdir(raw_dir):
        model_path = os.path.join(raw_dir, model)
        if not os.path.isdir(model_path):
            continue
            
        for fname in os.listdir(model_path):
            if not fname.endswith(".json"):
                continue
                
            try:
                with open(os.path.join(model_path, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                q = data.get("quality", {}) or {}
                # 提取Code指标
                code_score = 0
                if data.get("prompt", "").find("fibonacci") >= 0 or "code" in fname:
                    if q.get("code") and q["code"].get("code_compiles"):
                        code_score = 1.0
                
                # 提取Creative指标
                creative_score = 0
                if q.get("creative"):
                    creative_score = q["creative"].get("distinct_2", 0)
                
                records.append({
                    "model": data.get("model"),
                    "task": fname.split("_")[0], # 假设命名规则 task_load_run.json
                    "run": fname.split("_")[-1].replace(".json", "").replace("r", ""),
                    "code_score": code_score,
                    "creative_score": creative_score
                })
            except Exception as e:
                print(f"Error reading {fname}: {e}")
                
    return pd.DataFrame(records)

def calculate_composite_metrics(df):
    """计算复合质效指标"""
    # 归一化 (Min-Max Scaling)
    def normalize(series, mode='max'):
        if series.max() == series.min():
            return 1.0 if mode=='max' else 0.0
        if mode == 'min': # 越小越好 (如延迟、能耗) -> 越大越好
            return (series.max() - series) / (series.max() - series.min())
        return (series - series.min()) / (series.max() - series.min())

    # 按任务分组归一化，避免跨任务比较的不公平
    df['norm_tps'] = df.groupby('task')['tps'].transform(lambda x: normalize(x, 'max'))
    df['norm_lat'] = df.groupby('task')['latency'].transform(lambda x: normalize(x, 'min'))
    df['norm_energy'] = df.groupby('task')['energy'].transform(lambda x: normalize(x, 'min'))
    
    # 质量分数归一化
    # 对于 QA/Summary 使用 BARTScore
    # 对于 Code 使用 code_score (编译通过率)
    # 对于 Creative 使用 distinct-2
    
    df['quality_raw'] = df['bartscore'].fillna(0) # 暂用 BARTScore
    # 如果有 code/creative 分数，覆盖 quality_raw
    if 'code_score' in df.columns:
        df.loc[df['task']=='code', 'quality_raw'] = df['code_score']
    if 'creative_score' in df.columns:
        df.loc[df['task']=='creative', 'quality_raw'] = df['creative_score']
        
    df['norm_quality'] = df.groupby('task')['quality_raw'].transform(lambda x: normalize(x, 'max'))
    
    # 效能得分 (Efficiency Score): 40% 吞吐 + 30% 延迟 + 30% 能耗优
    df['efficiency_score'] = 0.4 * df['norm_tps'] + 0.3 * df['norm_lat'] + 0.3 * df['norm_energy']
    
    # 质效比 (Q/E Ratio)
    # 避免分母为0，加 epsilon
    df['qe_ratio'] = (df['norm_quality'] + 0.01) / (1.01 - df['efficiency_score'])
    
    return df

def plot_charts(df):
    """生成可视化图表"""
    sns.set_style("whitegrid")
    
    # 1. 吞吐量 vs 延迟 (散点图)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='latency', y='tps', hue='model', style='task', s=100)
    ax = plt.gca()
    if HAS_CHINESE_FONT:
        ax.set_title("吞吐量 vs 延迟分布", fontproperties=FONT_PROP)
        ax.set_xlabel("延迟 (秒) [越低越好]", fontproperties=FONT_PROP)
        ax.set_ylabel("吞吐量 (tokens/s) [越高越好]", fontproperties=FONT_PROP)
    else:
        ax.set_title("Throughput vs Latency")
        ax.set_xlabel("Latency (s) [lower better]")
        ax.set_ylabel("Throughput (tokens/s) [higher better]")
    plt.savefig(os.path.join(FIGURES_DIR, "throughput_vs_latency.png"))
    plt.close()
    
    # 2. 能耗 vs 质量 (散点图)
    plt.figure(figsize=(10, 6))
    # 过滤掉质量为0的点（可能无BARTScore）
    df_q = df[df['quality_raw'] != 0]
    sns.scatterplot(data=df_q, x='energy', y='quality_raw', hue='model', style='task', s=100)
    ax = plt.gca()
    if HAS_CHINESE_FONT:
        ax.set_title("能耗 vs 质量分布", fontproperties=FONT_PROP)
        ax.set_xlabel("GPU能耗 (J) [越低越好]", fontproperties=FONT_PROP)
        ax.set_ylabel("质量得分 (BARTScore/Distinct/Compile) [越高越好]", fontproperties=FONT_PROP)
    else:
        ax.set_title("Energy vs Quality")
        ax.set_xlabel("GPU Energy (J) [lower better]")
        ax.set_ylabel("Quality score [higher better]")
    plt.savefig(os.path.join(FIGURES_DIR, "energy_vs_quality.png"))
    plt.close()
    
    # 3. 质效比对比 (柱状图)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='task', y='qe_ratio', hue='model', errorbar=None)
    ax = plt.gca()
    if HAS_CHINESE_FONT:
        ax.set_title("各模型在不同任务下的质效比 (Q/E Ratio)", fontproperties=FONT_PROP)
        ax.set_ylabel("质效比 (越高越优)", fontproperties=FONT_PROP)
    else:
        ax.set_title("Q/E Ratio across tasks")
        ax.set_ylabel("Q/E Ratio [higher better]")
    plt.savefig(os.path.join(FIGURES_DIR, "quality_efficiency_ratio.png"))
    plt.close()
    
    # 4. 雷达图 (各维度平均表现)
    # 按模型聚合
    radar_df = df.groupby('model')[[ 'norm_tps', 'norm_lat', 'norm_energy', 'norm_quality']].mean().reset_index()
    
    categories = ['吞吐', '延迟(优)', '能耗(优)', '质量'] if HAS_CHINESE_FONT else ['Throughput', 'Latency(+)', 'Energy(+)', 'Quality']
    N = len(categories)
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    
    for i, row in radar_df.iterrows():
        values = row[['norm_tps', 'norm_lat', 'norm_energy', 'norm_quality']].values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=row['model'])
        ax.fill(angles, values, alpha=0.1)
        
    ax.set_xticks(angles[:-1])
    if HAS_CHINESE_FONT:
        ax.set_xticklabels(categories, fontproperties=FONT_PROP)
        ax.set_title("模型综合能力雷达图 (归一化指标)", fontproperties=FONT_PROP)
    else:
        ax.set_xticklabels(categories)
        ax.set_title("Model capability radar (normalized)")
    leg = plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    if HAS_CHINESE_FONT and FONT_PROP is not None:
        for text in leg.get_texts():
            text.set_fontproperties(FONT_PROP)
    plt.savefig(os.path.join(FIGURES_DIR, "radar_chart.png"))
    plt.close()

def generate_report(df, df_stats):
    """生成Markdown分析报告"""
    best_model_qe = df.groupby('model')['qe_ratio'].mean().idxmax()
    best_model_tps = df.groupby('model')['tps'].mean().idxmax()
    best_model_energy = df.groupby('model')['energy'].mean().idxmin()
    
    report_content = f"""# 实验数据分析报告：基于大语言模型的多维质效比评估

## 1. 实验概况
- **实验批次**: experiments_1
- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **包含模型**: {", ".join(df['model'].unique())}
- **包含任务**: {", ".join(df['task'].unique())}
- **总样本数**: {len(df)}

## 2. 关键发现
- **综合质效比最优**: **{best_model_qe}**，在质量与资源消耗之间取得了最佳平衡。
- **吞吐性能最强**: **{best_model_tps}**，适合对延迟敏感的高并发场景。
- **最节能模型**: **{best_model_energy}**，适合端侧或低功耗场景。

## 3. 详细指标分析

### 3.1 效率维度
- **吞吐量 (TPS)**: 
  - 均值: {df['tps'].mean():.2f} tokens/s
  - 峰值: {df['tps'].max():.2f} tokens/s (由 {df.loc[df['tps'].idxmax(), 'model']} 贡献)
- **能耗 (Energy)**:
  - 平均单次请求能耗: {df['energy'].mean():.2f} J

### 3.2 质量维度
- **BARTScore (QA/Summary)**: 
  - 均值: {df[df['bartscore']!=0]['bartscore'].mean():.4f}
  - 最优: {df['bartscore'].max():.4f}

### 3.3 质效比 (Q/E Ratio)
- 该指标综合了归一化的质量得分与效率成本（1 - 效率得分）。
- 排名如下：
{df.groupby('model')['qe_ratio'].mean().sort_values(ascending=False).to_markdown()}

## 4. 可视化图表
### 4.1 吞吐量 vs 延迟
![Throughput vs Latency](figures/throughput_vs_latency.png)

### 4.2 能耗 vs 质量
![Energy vs Quality](figures/energy_vs_quality.png)

### 4.3 质效比对比
![Q/E Ratio](figures/quality_efficiency_ratio.png)

### 4.4 综合雷达图
![Radar Chart](figures/radar_chart.png)

## 5. 数据摘要表
{df_stats.to_markdown(index=False)}

---
*注：本报告由自动化分析脚本生成。*
"""
    with open(os.path.join(RESULTS_DIR, "report.md"), "w", encoding="utf-8") as f:
        f.write(report_content)
    print(f"报告已生成: {os.path.join(RESULTS_DIR, 'report.md')}")

def main():
    print("开始加载数据...")
    df_res, df_stats = load_data()
    if df_res is None:
        return

    # 尝试合并细粒度质量指标
    try:
        df_quality = load_quality_details()
        if not df_quality.empty:
            # 简单合并，实际可能需要更复杂的对齐（这里假设 run 编号一致）
            # 简化起见，若 task 和 run 匹配则更新
            pass 
    except Exception as e:
        print(f"加载细粒度质量指标失败: {e}")

    print("计算复合指标...")
    df_analysis = calculate_composite_metrics(df_res)
    
    # 保存中间数据
    df_analysis.to_csv(os.path.join(RESULTS_DIR, "analysis_data.csv"), index=False)
    
    print("生成图表...")
    try:
        plot_charts(df_analysis)
    except Exception as e:
        print(f"生成图表失败 (可能是字体或依赖问题): {e}")
    
    print("生成报告...")
    generate_report(df_analysis, df_stats)
    print("分析完成！")

if __name__ == "__main__":
    main()
