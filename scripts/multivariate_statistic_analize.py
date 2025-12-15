import os
import json
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager as fm
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import CCA
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
from statsmodels.multivariate.manova import MANOVA
import warnings

# 忽略一些警告，如字体警告或小样本警告
warnings.filterwarnings("ignore")

# 配置路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "experiments_1")
RESULTS_DIR = os.path.join(BASE_DIR, "results", "experiments_1")
OUTPUT_DIR = os.path.join(RESULTS_DIR, "multivariate_analysis")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# 字体配置 (复用 analyze_experiments_1.py 的逻辑)
HAS_CHINESE_FONT = False
FONT_PROP = None

def _configure_fonts():
    global HAS_CHINESE_FONT, FONT_PROP
    candidates = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans CN", "Arial Unicode MS"]
    available = {f.name for f in fm.fontManager.ttflist}
    chosen = None
    for name in candidates:
        if name in available:
            chosen = name
            break
    
    if not chosen:
        # 尝试从系统查找
        try:
            win_font_dir = r"C:\\Windows\\Fonts"
            if os.path.isdir(win_font_dir):
                font_paths = [os.path.join(win_font_dir, f) for f in os.listdir(win_font_dir) 
                              if f.lower().endswith((".ttf", ".ttc", ".otf"))]
                desired = set(candidates + ["SimSun", "NSimSun", "Microsoft YaHei UI"])
                for p in font_paths:
                    try:
                        nm = fm.FontProperties(fname=p).get_name()
                        if nm in desired:
                            fm.fontManager.addfont(p)
                            chosen = nm
                            break
                    except:
                        continue
        except:
            pass

    if chosen:
        plt.rcParams['font.family'] = chosen
        plt.rcParams['font.sans-serif'] = [chosen]
        plt.rcParams['axes.unicode_minus'] = False
        HAS_CHINESE_FONT = True
        try:
            font_path = fm.findfont(chosen)
            FONT_PROP = fm.FontProperties(fname=font_path)
        except:
            FONT_PROP = None
        print(f"使用字体: {chosen}")
    else:
        print("未找到中文字体，使用默认字体")

_configure_fonts()

def load_and_preprocess_data():
    """加载并预处理数据"""
    print("正在加载数据...")
    res_path = os.path.join(DATA_DIR, "summary", "results.csv")
    if not os.path.exists(res_path):
        print(f"文件未找到: {res_path}")
        return None

    df = pd.read_csv(res_path)
    
    # 数值转换
    numeric_cols = ['latency_s', 'toks_per_s', 'gpu_mem_peak_mb', 'gpu_util_avg', 'gpu_energy_j', 'bartscore']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 补充细粒度质量指标
    raw_dir = os.path.join(DATA_DIR, "raw")
    quality_records = []
    if os.path.exists(raw_dir):
        for model in os.listdir(raw_dir):
            model_path = os.path.join(raw_dir, model)
            if not os.path.isdir(model_path): continue
            for fname in os.listdir(model_path):
                if not fname.endswith(".json"): continue
                try:
                    with open(os.path.join(model_path, fname), "r", encoding="utf-8") as f:
                        data = json.load(f)
                    q = data.get("quality", {}) or {}
                    
                    # 统一提取一个 'quality_score'
                    # 逻辑: code -> code_compiles (0/1), creative -> distinct_2, qa/summary -> bartscore
                    task = fname.split("_")[0]
                    score = None
                    if task == "code":
                        score = 1.0 if q.get("code", {}).get("code_compiles") else 0.0
                    elif task == "creative":
                        score = q.get("creative", {}).get("distinct_2", 0.0)
                    else:
                        score = q.get("bartscore")
                    
                    quality_records.append({
                        "model": data.get("model"),
                        "task": task,
                        "run": str(data.get("metadata", {}).get("run_idx", fname.split("_")[-1].replace(".json", "").replace("r", ""))),
                        "quality_unified": score
                    })
                except:
                    pass
    
    if quality_records:
        df_q = pd.DataFrame(quality_records)
        # 简单的合并尝试，基于索引或顺序可能不准确，这里尝试用 model+task+run
        # results.csv 里的 run 也是数字
        df['run'] = df['run'].astype(str)
        # 注意: results.csv 里的 run 可能是 1, 2, 3... 但 raw json 文件名里的 run 也是对应关系
        # 这里为了简便，直接假设行顺序一致，或者使用 merge
        # 由于 results.csv 是 append 写入的，顺序应该与遍历顺序不一定一致
        # 我们用 merge
        df = pd.merge(df, df_q, on=['model', 'task', 'run'], how='left')
        
        # 优先使用 quality_unified，如果为空则回退到 bartscore
        df['final_quality'] = df['quality_unified'].fillna(df['bartscore'])
    else:
        df['final_quality'] = df['bartscore']

    # 填充缺失值 (BARTScore 可能是 None)
    # 对于质量分，如果实在没有，填 0 (归一化前) 或 最小值
    df['final_quality'] = df['final_quality'].fillna(df['final_quality'].min() if not df['final_quality'].isnull().all() else 0)
    
    # 最终用于分析的列
    # 丢弃含空值的行 (为了多元分析的稳定性)
    analysis_cols = ['model', 'task', 'latency_s', 'toks_per_s', 'gpu_mem_peak_mb', 'gpu_util_avg', 'gpu_energy_j', 'final_quality']
    df_clean = df[analysis_cols].dropna()
    
    print(f"数据加载完成，共 {len(df_clean)} 条有效样本。")
    return df_clean

def analyze_correlation(df, report_file):
    """1. 多元相关性分析"""
    print("执行多元相关性分析...")
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", square=True)
    title = "多元指标相关性热力图" if HAS_CHINESE_FONT else "Multivariate Correlation Heatmap"
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "correlation_heatmap.png"))
    plt.close()
    
    report_file.write("## 1. 多元相关性分析 (Multivariate Correlation)\n\n")
    report_file.write("分析了延迟、吞吐量、显存、利用率、能耗和质量得分之间的线性相关性。\n\n")
    report_file.write(corr_matrix.to_markdown())
    report_file.write("\n\n![Correlation Heatmap](figures/correlation_heatmap.png)\n\n")

def analyze_manova(df, report_file):
    """2. 多元方差分析 (MANOVA)"""
    print("执行多元方差分析 (MANOVA)...")
    report_file.write("## 2. 多元方差分析 (MANOVA)\n\n")
    
    # 确保列名没有特殊字符，statsmodels 公式需要
    df_m = df.copy()
    df_m.columns = [c.replace(":", "_").replace(" ", "_") for c in df_m.columns]
    
    # 因变量
    endog_cols = ['latency_s', 'toks_per_s', 'gpu_energy_j', 'final_quality']
    # 检查样本量是否足够
    if len(df_m) < len(endog_cols) + 5:
        report_file.write("> **警告**: 样本量过小，MANOVA 结果可能不可靠。\n\n")
    
    try:
        # 模型: Y ~ Model + Task
        # 注意: Model 和 Task 是分类变量
        # 使用 + 连接自变量，表示主效应
        formula = ' + '.join(endog_cols) + ' ~ model + task'
        manova = MANOVA.from_formula(formula, data=df_m)
        mv_test = manova.mv_test()
        
        report_file.write(f"检验模型公式: `{formula}`\n\n")
        report_file.write("### 检验结果摘要\n")
        # 提取关键信息写入报告 (Wilks' lambda 等)
        # mv_test.summary() 返回的是一个对象，打印出来是文本
        # 我们将其捕获或手动解析
        # 这里直接保存 summary 的文本形式
        
        # 截取部分输出
        res_str = str(mv_test)
        report_file.write("```text\n")
        report_file.write(res_str)
        report_file.write("\n```\n\n")
        
        report_file.write("**解读**: 查看 `Pr > F` 列。如果值小于 0.05，说明该因子（模型或任务）对整体性能指标有显著影响。\n\n")
        
    except Exception as e:
        report_file.write(f"MANOVA 执行失败: {e}\n\n")
        print(f"MANOVA 失败: {e}")

def analyze_pca(df, report_file):
    """3. 主成分分析 (PCA)"""
    print("执行主成分分析 (PCA)...")
    report_file.write("## 3. 主成分分析 (PCA)\n\n")
    
    features = ['latency_s', 'toks_per_s', 'gpu_mem_peak_mb', 'gpu_util_avg', 'gpu_energy_j', 'final_quality']
    x_df = df[features].copy()
    for c in ['latency_s', 'gpu_energy_j', 'gpu_mem_peak_mb']:
        x_df[c] = np.log1p(x_df[c])
    x = x_df.values
    y_model = df['model'].values
    y_task = df['task'].values
    
    # 标准化
    x = StandardScaler().fit_transform(x)
    
    pca = PCA(n_components=0.8)
    principalComponents = pca.fit_transform(x)
    
    # 解释方差比
    explained_variance = pca.explained_variance_ratio_
    report_file.write(f"- **PC1 解释方差**: {explained_variance[0]:.2%}\n")
    if len(explained_variance) > 1:
        report_file.write(f"- **PC2 解释方差**: {explained_variance[1]:.2%}\n")
    if len(explained_variance) > 2:
        report_file.write(f"- **PC3 解释方差**: {explained_variance[2]:.2%}\n")
    report_file.write(f"- **累计解释方差**: {sum(explained_variance):.2%}\n\n")
    
    # 载荷矩阵 (Loadings) - 查看每个成分由哪些指标构成
    load_cols = [f"PC{i+1}" for i in range(pca.components_.shape[0])]
    loadings = pd.DataFrame(pca.components_.T, columns=load_cols, index=features)
    report_file.write("### 因子载荷 (Factor Loadings)\n")
    report_file.write(loadings.to_markdown())
    report_file.write("\n\n")
    
    # 绘图
    pc_cols = [f"PC{i+1}" for i in range(principalComponents.shape[1])]
    pca_df = pd.DataFrame(data=principalComponents, columns=pc_cols)
    pca_df['model'] = y_model
    pca_df['task'] = y_task
    
    plt.figure(figsize=(10, 8))
    if 'PC2' in pca_df.columns:
        sns.scatterplot(x="PC1", y="PC2", hue="model", style="task", data=pca_df, s=100)
    else:
        sns.scatterplot(x="PC1", y=[0]*len(pca_df), hue="model", style="task", data=pca_df, s=100)
    
    # 绘制特征向量 (Biplot 简化版)
    # 缩放因子，让箭头适应散点图范围
    scale_x = principalComponents[:, 0].max()
    scale_y = principalComponents[:, 1].max() if principalComponents.shape[1] > 1 else principalComponents[:, 0].max()
    scale_factor = max(scale_x, scale_y) * 0.8
    if principalComponents.shape[1] > 1:
        for i, feature in enumerate(features):
            plt.arrow(0, 0, pca.components_[0, i] * scale_factor, pca.components_[1, i] * scale_factor, color='r', alpha=0.5, head_width=0.05)
            plt.text(pca.components_[0, i] * scale_factor * 1.15, pca.components_[1, i] * scale_factor * 1.15, feature, color='r', ha='center', va='center')
        
    title = "PCA 主成分双标图 (Biplot)" if HAS_CHINESE_FONT else "PCA Biplot"
    if len(explained_variance) > 1:
        plt.title(f"{title}\nPC1 ({explained_variance[0]:.1%}) vs PC2 ({explained_variance[1]:.1%})")
    else:
        plt.title(f"{title}\nPC1 ({explained_variance[0]:.1%})")
    plt.xlabel("Principal Component 1")
    plt.ylabel("Principal Component 2")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(FIGURES_DIR, "pca_biplot.png"))
    plt.close()
    
    report_file.write("![PCA Biplot](figures/pca_biplot.png)\n\n")
    if 'PC3' in pca_df.columns:
        plt.figure(figsize=(10, 8))
        sns.scatterplot(x="PC1", y="PC3", hue="model", style="task", data=pca_df, s=100)
        scale_x = principalComponents[:, 0].max()
        scale_y3 = principalComponents[:, 2].max()
        scale_factor3 = max(scale_x, scale_y3) * 0.8
        for i, feature in enumerate(features):
            plt.arrow(0, 0, pca.components_[0, i] * scale_factor3, pca.components_[2, i] * scale_factor3, color='r', alpha=0.5, head_width=0.05)
            plt.text(pca.components_[0, i] * scale_factor3 * 1.15, pca.components_[2, i] * scale_factor3 * 1.15, feature, color='r', ha='center', va='center')
        if len(explained_variance) > 2:
            plt.title(f"{title}\nPC1 ({explained_variance[0]:.1%}) vs PC3 ({explained_variance[2]:.1%})")
        else:
            plt.title(f"{title}\nPC1 ({explained_variance[0]:.1%}) vs PC3")
        plt.xlabel("Principal Component 1")
        plt.ylabel("Principal Component 3")
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.savefig(os.path.join(FIGURES_DIR, "pca_biplot_pc1_pc3.png"))
        plt.close()
        report_file.write("![PCA Biplot PC1-PC3](figures/pca_biplot_pc1_pc3.png)\n\n")
    plt.figure(figsize=(8, 5))
    plt.bar(range(1, len(explained_variance)+1), explained_variance)
    plt.plot(range(1, len(explained_variance)+1), np.cumsum(explained_variance), marker='o')
    plt.xlabel("Principal Components")
    plt.ylabel("Explained Variance Ratio")
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "pca_scree.png"))
    plt.close()
    report_file.write("![PCA Scree](figures/pca_scree.png)\n\n")

def analyze_clustering(df, report_file):
    """4. 层次聚类分析"""
    print("执行层次聚类分析...")
    report_file.write("## 4. 层次聚类分析 (Hierarchical Clustering)\n\n")
    
    features = ['latency_s', 'toks_per_s', 'gpu_mem_peak_mb', 'gpu_util_avg', 'gpu_energy_j', 'final_quality']
    x = df[features].values
    
    # 标准化
    x_scaled = StandardScaler().fit_transform(x)
    
    # 链接矩阵
    linked = linkage(x_scaled, 'ward')
    
    plt.figure(figsize=(12, 7))
    # 创建标签: Model-Task
    labels = [f"{r['model']}-{r['task']}" for _, r in df.iterrows()]
    
    dendrogram(linked,
               orientation='top',
               labels=labels,
               distance_sort='descending',
               show_leaf_counts=True,
               leaf_rotation=90,
               leaf_font_size=10)
    
    title = "实验运行层次聚类树状图" if HAS_CHINESE_FONT else "Hierarchical Clustering Dendrogram"
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(FIGURES_DIR, "clustering_dendrogram.png"))
    plt.close()
    
    report_file.write("使用 Ward 方法和欧氏距离对所有实验运行进行聚类，结果如下：\n\n")
    report_file.write("![Clustering Dendrogram](figures/clustering_dendrogram.png)\n\n")

def analyze_cca(df, report_file):
    """5. 典型相关分析 (CCA)"""
    print("执行典型相关分析 (CCA)...")
    report_file.write("## 5. 典型相关分析 (Canonical Correlation Analysis)\n\n")
    report_file.write("探索**资源消耗** (显存, 能耗, 利用率) 与 **性能产出** (吞吐, 延迟, 质量) 两组变量之间的关系。\n\n")
    
    # 定义两组变量
    X_cols = ['gpu_mem_peak_mb', 'gpu_energy_j', 'gpu_util_avg'] # 投入/资源
    Y_cols = ['toks_per_s', 'latency_s', 'final_quality']        # 产出/性能
    
    X = df[X_cols].values
    Y = df[Y_cols].values
    
    # 标准化
    X_scaled = StandardScaler().fit_transform(X)
    Y_scaled = StandardScaler().fit_transform(Y)
    
    # CCA
    # n_components 不能超过 min(X.shape[1], Y.shape[1])
    n_comps = min(len(X_cols), len(Y_cols))
    cca = CCA(n_components=n_comps)
    try:
        cca.fit(X_scaled, Y_scaled)
        
        # 典型变量
        X_c, Y_c = cca.transform(X_scaled, Y_scaled)
        
        # 计算典型相关系数 (Canonical Correlations)
        # sklearn 的 CCA 没有直接属性 score 给出相关系数，需要手动计算变换后的列的相关性
        corrs = [np.corrcoef(X_c[:, i], Y_c[:, i])[0, 1] for i in range(n_comps)]
        
        report_file.write(f"提取了 {n_comps} 对典型变量，其相关系数分别为：\n")
        for i, r in enumerate(corrs):
            report_file.write(f"- **Pair {i+1}**: {r:.4f}\n")
        report_file.write("\n")
        
        # 载荷 (Loadings) - 原始变量与典型变量的相关性
        # X 载荷
        x_loadings = np.array([np.corrcoef(X_scaled[:, i], X_c[:, 0])[0, 1] for i in range(X.shape[1])])
        y_loadings = np.array([np.corrcoef(Y_scaled[:, i], Y_c[:, 0])[0, 1] for i in range(Y.shape[1])])
        
        report_file.write("### 第一对典型变量的载荷 (Loadings for 1st Pair)\n")
        
        load_df = pd.DataFrame({
            "Variable": X_cols + Y_cols,
            "Type": ["Resource (X)"]*len(X_cols) + ["Performance (Y)"]*len(Y_cols),
            "Loading on CV1": np.concatenate([x_loadings, y_loadings])
        })
        report_file.write(load_df.to_markdown(index=False))
        report_file.write("\n\n")
        
        # 绘图：第一对典型变量的散点图
        plt.figure(figsize=(8, 8))
        sns.scatterplot(x=X_c[:, 0], y=Y_c[:, 0], hue=df['model'], style=df['task'], s=100)
        title = f"典型变量对 1 (r={corrs[0]:.2f})" if HAS_CHINESE_FONT else f"Canonical Variate Pair 1 (r={corrs[0]:.2f})"
        plt.title(title)
        plt.xlabel("Resource Canonical Variate 1")
        plt.ylabel("Performance Canonical Variate 1")
        plt.grid(True)
        plt.savefig(os.path.join(FIGURES_DIR, "cca_pair1.png"))
        plt.close()
        
        report_file.write("![CCA Pair 1](figures/cca_pair1.png)\n\n")
        
    except Exception as e:
        report_file.write(f"CCA 执行失败 (可能是样本量不足或共线性): {e}\n\n")
        print(f"CCA 失败: {e}")

def main():
    df = load_and_preprocess_data()
    if df is None or df.empty:
        print("无数据可分析。")
        return

    report_path = os.path.join(OUTPUT_DIR, "multivariate_report.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"# 实验数据多元统计分析报告\n\n")
        f.write(f"- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **样本数量**: {len(df)}\n")
        f.write(f"- **数据来源**: `data/experiments_1`\n\n")
        
        analyze_correlation(df, f)
        analyze_manova(df, f)
        analyze_pca(df, f)
        analyze_clustering(df, f)
        analyze_cca(df, f)
        
    print(f"\n分析完成！报告已生成: {report_path}")
    print(f"图表已保存至: {FIGURES_DIR}")

if __name__ == "__main__":
    main()
