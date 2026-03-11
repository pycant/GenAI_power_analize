"""
生成第5章成本效益分析报告
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from datetime import datetime
from typing import Dict, List

def generate_section_5_report(results: Dict, output_path: Path):
    """生成第5章完整报告"""
    
    report = []
    report.append("# 第5章: 成本效益分析与选择策略")
    report.append("")
    report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("---")
    report.append("")
    
    # 5.1 成本核算模型与指标定义
    report.append("## 5.1 成本核算模型与指标定义")
    report.append("")
    report.append("### 5.1.1 成本模型")
    report.append("")
    report.append("本研究采用综合成本模型，考虑以下成本组成:")
    report.append("")
    report.append("1. **能耗成本** (Energy Cost):")
    report.append("   - 公式: `C_energy = (E_token × N_tokens) / (3600 × 1000) × P_kwh`")
    report.append("   - E_token: 每token能耗 (焦耳)")
    report.append("   - N_tokens: token数量")
    report.append("   - P_kwh: 电价 (美元/千瓦时)")
    report.append("")
    report.append("2. **时间成本** (Time Cost):")
    report.append("   - 公式: `C_time = (N_tokens / Speed) / 3600 × D_gpu`")
    report.append("   - Speed: 生成速度 (tokens/秒)")
    report.append("   - D_gpu: GPU折旧成本 (美元/小时)")
    report.append("")
    report.append("3. **总成本** (Total Cost):")
    report.append("   - 公式: `C_total = C_energy + C_time`")
    report.append("")
    report.append("### 5.1.2 成本效益指标")
    report.append("")
    report.append("| 指标 | 定义 | 优化方向 | 说明 |")
    report.append("|------|------|----------|------|")
    report.append("| QPC | Quality per Cost = Q / C | 越大越好 | 单位成本的质量产出 |")
    report.append("| CBR | Cost-Benefit Ratio = C / Q | 越小越好 | 单位质量的成本投入 |")
    report.append("| 边际效益 | ΔQ / ΔC | 越大越好 | 成本增加带来的质量提升 |")
    report.append("")
    
    # 5.2 跨任务成本效益比较与模型排序
    report.append("## 5.2 跨任务成本效益比较与模型排序")
    report.append("")
    
    if 'ranked_qpc' in results:
        df_qpc = results['ranked_qpc']
        report.append("### 5.2.1 按质量成本比(QPC)排序")
        report.append("")
        report.append("| 排名 | 模型 | QPC | 质量得分 | 总成本($) | 能耗(J/token) | 速度(tokens/s) |")
        report.append("|------|------|-----|----------|-----------|---------------|----------------|")
        
        for _, row in df_qpc.head(10).iterrows():
            report.append(f"| {int(row['rank'])} | {row['model']} | {row['qpc']:.4f} | "
                         f"{row['quality']:.4f} | {row['total_cost']:.6f} | "
                         f"{row['energy']:.4f} | {row['speed']:.2f} |")
        report.append("")
    
    if 'ranked_cbr' in results:
        df_cbr = results['ranked_cbr']
        report.append("### 5.2.2 按成本效益比(CBR)排序")
        report.append("")
        report.append("CBR越小表示达到相同质量所需成本越低，是成本敏感场景的关键指标。")
        report.append("")
        report.append("| 排名 | 模型 | CBR | 质量得分 | 总成本($) |")
        report.append("|------|------|-----|----------|-----------|")
        
        for _, row in df_cbr.head(10).iterrows():
            if row['cbr'] != float('inf'):
                report.append(f"| {int(row['rank'])} | {row['model']} | {row['cbr']:.6f} | "
                             f"{row['quality']:.4f} | {row['total_cost']:.6f} |")
        report.append("")
    
    # 5.3 任务难度加权的成本效益分析
    report.append("## 5.3 任务难度加权的成本效益分析")
    report.append("")
    report.append("### 5.3.1 任务难度计算")
    report.append("")
    report.append("采用变异系数(CV = σ/μ)衡量任务难度，CV越大表示模型间差异越大，任务区分度越高。")
    report.append("")
    
    if 'cross_task' in results:
        df_cross = results['cross_task']
        tasks = df_cross['task'].unique()
        task_difficulty = {}
        
        report.append("| 任务 | 难度系数(CV) | 平均质量 | 质量标准差 | 难度等级 |")
        report.append("|------|-------------|----------|-----------|----------|")
        
        for task in sorted(tasks):
            task_data = df_cross[df_cross['task'] == task]
            mean_q = task_data['quality'].mean()
            std_q = task_data['quality'].std()
            cv = std_q / abs(mean_q) if abs(mean_q) > 1e-6 else std_q
            task_difficulty[task] = cv
            
            if cv > 0.5:
                level = "高难度 ⭐⭐⭐"
            elif cv > 0.3:
                level = "中等难度 ⭐⭐"
            else:
                level = "低难度 ⭐"
            
            report.append(f"| {task} | {cv:.4f} | {mean_q:.4f} | {std_q:.4f} | {level} |")
        report.append("")
    
    if 'weighted' in results:
        df_weighted = results['weighted']
        report.append("### 5.3.2 难度加权排序结果")
        report.append("")
        report.append("综合权重 = 用户偏好权重 × 任务难度系数")
        report.append("")
        report.append("| 排名 | 模型 | 加权QPC | 加权质量 | 加权成本($) |")
        report.append("|------|------|---------|----------|-------------|")
        
        for _, row in df_weighted.head(10).iterrows():
            report.append(f"| {int(row['rank'])} | {row['model']} | {row['weighted_qpc']:.4f} | "
                         f"{row['weighted_quality']:.4f} | {row['weighted_cost']:.6f} |")
        report.append("")
    
    # 5.4 场景化模型选择策略
    report.append("## 5.4 场景化模型选择策略")
    report.append("")
    report.append("### 5.4.1 场景定义")
    report.append("")
    
    from cost_benefit_analysis import SCENARIO_CONFIGS
    
    report.append("| 场景 | 描述 | 质量权重 | 成本权重 | 速度权重 |")
    report.append("|------|------|----------|----------|----------|")
    
    for scenario, config in SCENARIO_CONFIGS.items():
        q_w = config.get('quality_weight', 0)
        c_w = config.get('cost_weight', 0)
        s_w = config.get('speed_weight', 0)
        report.append(f"| {config['name']} | {config['description']} | "
                     f"{q_w:.1f} | {c_w:.1f} | {s_w:.1f} |")
    report.append("")
    
    if 'scenarios' in results:
        report.append("### 5.4.2 各场景推荐模型")
        report.append("")
        
        for scenario, df_scenario in results['scenarios'].items():
            config = SCENARIO_CONFIGS[scenario]
            report.append(f"#### {config['name']}")
            report.append("")
            report.append(f"**场景描述**: {config['description']}")
            report.append("")
            report.append("| 排名 | 模型 | 场景得分 | 质量 | 成本($) | 速度(tokens/s) |")
            report.append("|------|------|----------|------|---------|----------------|")
            
            for _, row in df_scenario.head(5).iterrows():
                report.append(f"| {int(row['rank'])} | {row['model']} | {row['scenario_score']:.4f} | "
                             f"{row['quality']:.4f} | {row['total_cost']:.6f} | {row['speed']:.2f} |")
            report.append("")
    
    # 5.5 成本-质量权衡的边际效益分析
    report.append("## 5.5 成本-质量权衡的边际效益分析")
    report.append("")
    report.append("### 5.5.1 边际效益理论")
    report.append("")
    report.append("边际效益定义为成本每增加一单位带来的质量提升:")
    report.append("")
    report.append("```")
    report.append("MB = ΔQ / ΔC")
    report.append("```")
    report.append("")
    report.append("其中:")
    report.append("- MB: 边际效益 (Marginal Benefit)")
    report.append("- ΔQ: 质量增量")
    report.append("- ΔC: 成本增量")
    report.append("")
    
    if 'marginal' in results:
        marginal_results = results['marginal']
        
        if marginal_results['fit_params']:
            params = marginal_results['fit_params']
            report.append("### 5.5.2 成本-质量拟合曲线")
            report.append("")
            report.append("采用对数函数拟合成本-质量关系:")
            report.append("")
            report.append(f"```")
            report.append(f"Q = {params['a']:.4f} × log(C) + {params['b']:.4f}")
            report.append(f"R² = {params['r2']:.4f}")
            report.append(f"```")
            report.append("")
            report.append("**解释**: 对数关系表明质量随成本增加呈现边际递减效应，")
            report.append("即初期成本投入带来显著质量提升，后期提升逐渐放缓。")
            report.append("")
        
        if marginal_results['knee_model']:
            report.append("### 5.5.3 拐点识别")
            report.append("")
            report.append(f"**拐点模型**: {marginal_results['knee_model']}")
            report.append("")
            report.append("拐点模型是边际效益最高的模型，代表成本-质量权衡的最优点。")
            report.append("在该点之前，增加成本能显著提升质量；之后质量提升放缓。")
            report.append("")
        
        if 'marginal_df' in marginal_results:
            df_marginal = marginal_results['marginal_df']
            report.append("### 5.5.4 边际效益排序")
            report.append("")
            report.append("| 模型 | 成本($) | 质量 | 成本增量 | 质量增量 | 边际效益 |")
            report.append("|------|---------|------|----------|----------|----------|")
            
            df_sorted = df_marginal.sort_values('marginal_benefit', ascending=False)
            for _, row in df_sorted.head(10).iterrows():
                report.append(f"| {row['model']} | {row['cost']:.6f} | {row['quality']:.4f} | "
                             f"{row['delta_cost']:.6f} | {row['delta_quality']:.4f} | "
                             f"{row['marginal_benefit']:.2f} |")
            report.append("")
    
    # 综合结论
    report.append("## 5.6 综合结论与建议")
    report.append("")
    report.append("### 5.6.1 主要发现")
    report.append("")
    
    if 'ranked_qpc' in results and len(results['ranked_qpc']) > 0:
        best_qpc = results['ranked_qpc'].iloc[0]
        report.append(f"1. **最佳质量成本比模型**: {best_qpc['model']}")
        report.append(f"   - QPC: {best_qpc['qpc']:.4f}")
        report.append(f"   - 质量: {best_qpc['quality']:.4f}")
        report.append(f"   - 成本: ${best_qpc['total_cost']:.6f}")
        report.append("")
    
    if 'marginal' in results and results['marginal']['knee_model']:
        report.append(f"2. **成本-质量拐点模型**: {results['marginal']['knee_model']}")
        report.append("   - 该模型代表边际效益最优点")
        report.append("   - 适合追求性价比的应用场景")
        report.append("")
    
    report.append("3. **场景化选择建议**:")
    if 'scenarios' in results:
        for scenario, df_scenario in results['scenarios'].items():
            if len(df_scenario) > 0:
                config = SCENARIO_CONFIGS[scenario]
                best_model = df_scenario.iloc[0]['model']
                report.append(f"   - {config['name']}: {best_model}")
    report.append("")
    
    report.append("### 5.6.2 决策建议")
    report.append("")
    report.append("1. **预算充足场景**: 选择质量最高的模型，忽略成本差异")
    report.append("2. **预算受限场景**: 选择QPC最高或CBR最低的模型")
    report.append("3. **均衡场景**: 选择拐点模型，获得最佳性价比")
    report.append("4. **实时应用**: 优先考虑速度，在满足延迟要求前提下选择质量最高的模型")
    report.append("")
    
    report.append("### 5.6.3 成本优化策略")
    report.append("")
    report.append("1. **模型量化**: 4-bit量化可显著降低能耗和时间成本，质量损失可控")
    report.append("2. **批处理**: 增大batch size可提高吞吐量，降低单token成本")
    report.append("3. **混合部署**: 根据任务难度动态选择模型，简单任务用小模型")
    report.append("4. **缓存策略**: 对常见查询缓存结果，避免重复推理")
    report.append("")
    
    report.append("---")
    report.append("")
    report.append(f"**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("**数据来源**: 跨任务综合评估实验")
    report.append("")
    report.append("**分析工具**: Python + pandas + scipy + matplotlib")
    report.append("")
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"✓ 第5章报告已生成: {output_path}")


if __name__ == '__main__':
    # 示例: 从已保存的结果生成报告
    from cost_benefit_analysis import run_cost_benefit_analysis, CostModel
    from pareto_core import PROJECT_ROOT
    
    ALL_TASKS = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']
    OUTPUT_DIR = PROJECT_ROOT / 'analysis' / 'qe_research' / 'results'
    
    # 运行分析
    results = run_cost_benefit_analysis(
        tasks=ALL_TASKS,
        output_base_dir=OUTPUT_DIR,
        cost_model=CostModel()
    )
    
    # 生成报告
    report_path = OUTPUT_DIR / 'cost_benefit_analysis' / 'SECTION_5_COST_BENEFIT_ANALYSIS_REPORT.md'
    generate_section_5_report(results, report_path)
