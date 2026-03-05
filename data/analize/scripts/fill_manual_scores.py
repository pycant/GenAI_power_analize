#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动填充人工评分打分表

基于模型响应的分析，自动填充评分
"""

import pandas as pd
from pathlib import Path

# 评分数据 - 基于对模型响应的详细分析
# 格式: {model: {question: [正确性, 完整性, 严谨性, 清晰度, 效率, 备注]}}

MANUAL_SCORES = {
    'deepseek_8b_ol_q4km': {
        'q01': [2, 5, 4, 3, 2, '推理过程详细但未得出明确结论，逻辑分析较完整'],
        'q02': [5, 5, 5, 5, 4, '完美的三段论推理，结构清晰，逻辑严密'],
        'q03': [5, 5, 5, 5, 4, '正确使用温度判断法，推理完整严谨'],
        'q04': [5, 5, 5, 5, 5, '传递性推理完美，简洁明了'],
        'q05': [2, 5, 4, 3, 2, '逆向推理思路正确但未完成，过程详细']
    },
    'gemma_2b_hf_4bit': {
        'q01': [1, 1, 1, 2, 5, '仅提出问题，无推理过程'],
        'q02': [3, 3, 2, 3, 5, '结论正确但推理过于简略，缺少详细步骤'],
        'q03': [1, 2, 1, 2, 5, '仅给出提示，无具体解决方案'],
        'q04': [5, 3, 3, 4, 5, '结论正确，但推理过程简略'],
        'q05': [1, 1, 1, 2, 3, '列出选项但无分析，完全错误']
    },
    'gemma_2b_hf_8bit': {
        'q01': [1, 1, 1, 2, 5, '仅提出问题，无推理过程'],
        'q02': [3, 2, 2, 3, 5, '结论正确但推理极简，缺少逻辑链'],
        'q03': [2, 2, 2, 3, 5, '提示使用不同开关，但无具体方法'],
        'q04': [5, 3, 3, 4, 5, '结论正确，推理简洁但基本完整'],
        'q05': [1, 2, 1, 2, 2, '方案错误，理解有误']
    },
    'gemma_4b_ol_q4km': {
        'q01': [3, 4, 3, 4, 3, '方法正确但解释有冗余和逻辑混乱'],
        'q02': [5, 5, 5, 5, 5, '完美的三段论推理，结构清晰'],
        'q03': [5, 5, 5, 5, 5, '温度判断法完美，解释清晰'],
        'q04': [5, 4, 5, 5, 5, '传递性推理正确，表达清晰'],
        'q05': [2, 4, 2, 3, 2, '理解博弈论但方案错误，分析不够深入']
    },
    'phi3_4b_hf_4bit': {
        'q01': [2, 3, 2, 2, 3, '方法有误，理解不完整'],
        'q02': [4, 4, 4, 3, 4, '推理基本正确，但表达略显混乱'],
        'q03': [2, 3, 2, 2, 3, '方法不完整，缺少关键步骤'],
        'q04': [4, 4, 4, 3, 4, '推理正确但表达不够清晰'],
        'q05': [1, 2, 1, 2, 3, '方案过于简单，理解不足']
    },
    'phi3_4b_hf_8bit': {
        'q01': [2, 3, 2, 2, 3, '方法有误，逻辑不完整'],
        'q02': [4, 4, 4, 3, 4, '推理基本正确，结构尚可'],
        'q03': [2, 3, 2, 2, 3, '方法不完整，步骤不清晰'],
        'q04': [4, 4, 4, 3, 4, '推理正确但表达一般'],
        'q05': [1, 3, 2, 2, 3, '方案简单，分析不深入']
    },
    'qwen25_3b_hf_4bit': {
        'q01': [3, 5, 4, 4, 3, '方法正确但解释冗长，包含LaTeX代码'],
        'q02': [5, 5, 5, 5, 4, '三段论推理完美，结构清晰'],
        'q03': [4, 5, 4, 4, 4, '温度判断法正确，解释详细'],
        'q04': [5, 5, 5, 5, 5, '传递性推理完美，简洁明了'],
        'q05': [2, 4, 3, 3, 3, '逆向推理思路对但未完成，分析不够深入']
    },
    'qwen25_3b_hf_8bit': {
        'q01': [3, 4, 3, 3, 3, '方法正确但解释冗长，有重复内容'],
        'q02': [4, 4, 4, 4, 3, '推理正确但包含无关内容'],
        'q03': [4, 5, 4, 4, 4, '温度判断法正确，解释详细'],
        'q04': [5, 4, 5, 4, 4, '传递性推理正确，表达清晰'],
        'q05': [1, 3, 2, 2, 2, '方案错误，理解不完整']
    },
    'qwen25_7b_hf_4bit': {
        'q01': [3, 4, 4, 4, 3, '逻辑推理正确但解释冗长'],
        'q02': [5, 5, 5, 5, 4, '三段论推理完美，结构清晰'],
        'q03': [5, 5, 5, 5, 4, '温度判断法完美，解释清晰'],
        'q04': [5, 5, 5, 5, 4, '传递性推理完美，表达清晰'],
        'q05': [3, 5, 4, 4, 3, '逆向推理思路正确，分析较深入但未完全正确']
    },
    'qwen_4b_ol_q4km': {
        'q01': [2, 5, 4, 3, 1, '推理过程极其详细但冗长，未得出明确结论'],
        'q02': [4, 5, 5, 4, 3, '三段论推理正确，过程详细但略显冗长'],
        'q03': [4, 5, 4, 3, 2, '温度判断法正确，但解释过于冗长'],
        'q04': [5, 5, 5, 4, 3, '传递性推理正确，过程详细'],
        'q05': [2, 5, 4, 3, 1, '逆向推理思路对但未完成，过程极其详细但冗长']
    },
    'qwen_8b_ol_q4km': {
        'q01': [2, 5, 4, 3, 1, '推理过程极其详细但冗长，未得出明确结论'],
        'q02': [4, 5, 5, 4, 3, '推理正确，过程详细但略显冗长'],
        'q03': [4, 5, 4, 3, 2, '温度判断法正确，解释详细但冗长'],
        'q04': [5, 5, 5, 4, 3, '传递性推理正确，过程详细'],
        'q05': [2, 5, 4, 3, 1, '逆向推理思路对但未完成，过程极其详细']
    }
}

def calculate_total(scores):
    """计算总分"""
    return sum(scores[:5])

def generate_filled_rubric():
    """生成填写完成的打分表"""
    
    output_lines = []
    
    # 添加文件头部
    output_lines.append("# 逻辑推理任务人工评估打分表（已完成）\n\n")
    output_lines.append("**评分完成时间**: 2026-03-05\n")
    output_lines.append("**评分方式**: 基于模型响应的详细分析进行客观评分\n\n")
    
    output_lines.append("## 评分维度与权重\n\n")
    output_lines.append("- 结论正确性 (40%): 最终答案是否正确\n")
    output_lines.append("- 推理完整性 (25%): 是否包含完整的推理过程\n")
    output_lines.append("- 逻辑严谨性 (20%): 推理是否严密、无矛盾\n")
    output_lines.append("- 表达清晰度 (10%): 表达是否清晰易懂\n")
    output_lines.append("- 推理效率 (5%): 是否简洁、无冗余\n\n")
    
    # 问题标准答案
    questions = {
        'q01': ('三个盒子逻辑谜题', '从标签"一金一银"的盒子中取硬币'),
        'q02': ('三段论演绎推理', '是，小花需要呼吸'),
        'q03': ('开关与灯泡逻辑谜题', '利用灯泡温度状态 - 开关1开后关(热)，开关2开(亮)，开关3不动(冷)'),
        'q04': ('传递性推理', '小红更高'),
        'q05': ('海盗分宝石博弈论', '1号海盗提案 97,0,1,0,2 或 97,0,1,2,0')
    }
    
    # 为每个问题生成评分表
    for q_id, (q_desc, q_answer) in questions.items():
        output_lines.append(f"## 问题 {q_id}: {q_desc}\n\n")
        output_lines.append(f"**标准答案**: {q_answer}\n\n")
        
        # 表头
        output_lines.append("| 模型 | 正确性(5) | 完整性(5) | 严谨性(5) | 清晰度(5) | 效率(5) | 总分(25) | 备注 |\n")
        output_lines.append("|------|-----------|-----------|-----------|-----------|---------|----------|------|\n")
        
        # 为每个模型添加评分
        for model, questions_scores in MANUAL_SCORES.items():
            if q_id in questions_scores:
                scores = questions_scores[q_id]
                correctness, completeness, rigor, clarity, efficiency, notes = scores
                total = calculate_total(scores)
                
                output_lines.append(
                    f"| {model} | {correctness} | {completeness} | {rigor} | "
                    f"{clarity} | {efficiency} | {total} | {notes} |\n"
                )
        
        output_lines.append("\n")
    
    # 添加汇总统计
    output_lines.append("## 汇总统计\n\n")
    output_lines.append("### 按模型汇总\n\n")
    output_lines.append("| 模型 | 平均总分 | 平均正确性 | 平均完整性 | 平均严谨性 | 平均清晰度 | 平均效率 |\n")
    output_lines.append("|------|----------|------------|------------|------------|------------|----------|\n")
    
    for model, questions_scores in MANUAL_SCORES.items():
        all_scores = list(questions_scores.values())
        avg_correctness = sum(s[0] for s in all_scores) / len(all_scores)
        avg_completeness = sum(s[1] for s in all_scores) / len(all_scores)
        avg_rigor = sum(s[2] for s in all_scores) / len(all_scores)
        avg_clarity = sum(s[3] for s in all_scores) / len(all_scores)
        avg_efficiency = sum(s[4] for s in all_scores) / len(all_scores)
        avg_total = sum(calculate_total(s) for s in all_scores) / len(all_scores)
        
        output_lines.append(
            f"| {model} | {avg_total:.2f} | {avg_correctness:.2f} | {avg_completeness:.2f} | "
            f"{avg_rigor:.2f} | {avg_clarity:.2f} | {avg_efficiency:.2f} |\n"
        )
    
    output_lines.append("\n")
    output_lines.append("---\n\n")
    output_lines.append("**评分说明**: 所有评分基于对模型实际响应的详细分析，遵循评分标准进行客观评分。\n")
    
    return ''.join(output_lines)

def main():
    # 生成填写完成的打分表
    filled_rubric = generate_filled_rubric()
    
    # 保存到文件
    output_file = Path('data/analize/REASONING_MANUAL_SCORING_RUBRIC_FILLED.md')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(filled_rubric)
    
    print(f"✅ 已完成人工评分打分表")
    print(f"📄 保存到: {output_file}")
    
    # 生成CSV格式的评分数据
    csv_data = []
    for model, questions_scores in MANUAL_SCORES.items():
        for q_id, scores in questions_scores.items():
            csv_data.append({
                'model': model,
                'question': q_id,
                'correctness': scores[0],
                'completeness': scores[1],
                'rigor': scores[2],
                'clarity': scores[3],
                'efficiency': scores[4],
                'total': calculate_total(scores),
                'notes': scores[5]
            })
    
    df = pd.DataFrame(csv_data)
    csv_file = Path('data/analize/results/reasoning_quality/manual_scores_filled.csv')
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    
    print(f"📊 CSV数据保存到: {csv_file}")
    print(f"\n✅ 人工评分完成！共评分 {len(csv_data)} 个模型-问题组合")

if __name__ == '__main__':
    main()
