#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成任务-指标对应表
从quality_scores目录中的raw.csv文件提取所有指标信息
"""

import pandas as pd
import os
from pathlib import Path

# 配置路径
QUALITY_SCORES_DIR = Path("analysis/qe_research/results/quality_scores")
OUTPUT_FILE = QUALITY_SCORES_DIR / "TASK_METRICS_MAPPING.md"

# 任务配置
TASKS = {
    "code": {
        "name": "代码生成",
        "english": "Code Generation",
        "file": "code_scores_raw.csv",
        "core_metric": "compilation_rate",
        "core_metric_cn": "编译通过率"
    },
    "creative": {
        "name": "创意写作",
        "english": "Creative Writing",
        "file": "creative_scores_raw.csv",
        "core_metric": "distinct_2",
        "core_metric_cn": "词汇多样性-2"
    },
    "math": {
        "name": "数学推理",
        "english": "Math Reasoning",
        "file": "math_scores_raw.csv",
        "core_metric": "exact_match",
        "core_metric_cn": "精确匹配率"
    },
    "qa": {
        "name": "问答",
        "english": "Question Answering",
        "file": "qa_scores_raw.csv",
        "core_metric": "confidence_score",
        "core_metric_cn": "置信度得分"
    },
    "summary": {
        "name": "摘要生成",
        "english": "Summarization",
        "file": "summary_scores_raw.csv",
        "core_metric": "bartscore_avg",
        "core_metric_cn": "BARTScore平均分"
    },
    "translation": {
        "name": "翻译",
        "english": "Translation",
        "file": "translation_scores_raw.csv",
        "core_metric": "bleu_1",
        "core_metric_cn": "BLEU"
    },
    "reasoning": {
        "name": "推理",
        "english": "Reasoning",
        "file": "reasoning_scores_raw.csv",
        "core_metric": "accuracy",
        "core_metric_cn": "准确率"
    }
}

# 指标中文名称映射
METRIC_NAMES = {
    # 代码生成
    "code_length": "代码长度",
    "compilation_rate": "编译通过率",
    "cyclomatic_complexity": "圈复杂度",
    "has_code": "包含代码",
    
    # 创意写作
    "avg_sentence_length": "平均句长",
    "distinct_1": "词汇多样性-1",
    "distinct_2": "词汇多样性-2",
    "metaphor_count": "隐喻数量",
    
    # 数学推理
    "exact_match": "精确匹配",
    "extracted_answer": "提取答案",
    "extraction_confidence": "提取置信度",
    "has_answer": "包含答案",
    
    # 问答
    "answer_length": "答案长度",
    "avg_paragraph_length": "平均段落长度",
    "certainty_count": "确定性词汇数",
    "confidence_score": "置信度得分",
    
    # 摘要生成
    "bartscore_avg": "BARTScore平均",
    "bartscore_faith": "BARTScore忠实度",
    "bartscore_info": "BARTScore信息量",
    "bertscore_f1": "BERTScore F1",
    "bertscore_precision": "BERTScore精确率",
    "bertscore_recall": "BERTScore召回率",
    
    # 翻译
    "bleu_1": "BLEU-1",
    "bleu_2": "BLEU-2",
    "bleu_3": "BLEU-3",
    "bleu_4": "BLEU-4",
    
    # 推理
    "accuracy": "准确率",
    "reasoning_steps": "推理步骤数",
    "logical_consistency": "逻辑一致性"
}

# 指标说明 - 完整版本
METRIC_DESCRIPTIONS = {
    # 代码生成
    "code_length": "生成代码的平均行数",
    "compilation_rate": "代码能够成功编译的比例",
    "cyclomatic_complexity": "代码的逻辑复杂度（分支数量）",
    "has_code": "输出中是否包含代码块",
    "test_pass_rate": "通过测试用例的比例",
    "tests_passed": "通过的测试用例数量",
    "tests_total": "总测试用例数量",
    
    # 创意写作
    "avg_sentence_length": "每句话的平均词数",
    "distinct_1": "不重复单词（unigram）占比",
    "distinct_2": "不重复二元组（bigram）占比",
    "metaphor_count": "检测到的隐喻修辞数量",
    "parallelism_count": "检测到的排比修辞数量",
    "perplexity": "语言模型困惑度（越低表示文本越流畅）",
    "personification_count": "检测到的拟人修辞数量",
    "repetition_count": "检测到的重复修辞数量",
    "sentence_count": "文本中的句子总数",
    "text_length": "文本的总字符数",
    "token_count": "文本的总词元数",
    "total_rhetorical_devices": "检测到的修辞手法总数",
    "unique_token_ratio": "独特词元占总词元的比例",
    
    # 数学推理
    "exact_match": "答案与标准答案完全一致的比例",
    "extracted_answer": "从输出中提取的数值答案",
    "extraction_confidence": "答案提取的置信度",
    "has_answer": "输出中是否包含答案",
    "has_calculation": "输出中是否包含计算过程",
    "has_reasoning": "输出中是否包含推理步骤",
    "numerical_match": "数值答案的匹配程度",
    "reference_answer": "参考答案的数值",
    "step_count": "推理步骤的数量",
    "text_length": "输出文本的总长度",
    
    # 问答
    "answer_length": "生成答案的字符数",
    "avg_paragraph_length": "每段的平均字符数",
    "certainty_count": "表达确定性的词汇数量",
    "confidence_score": "答案的整体置信度",
    "has_answer": "输出中是否包含答案",
    "has_conclusion": "输出中是否包含结论部分",
    "has_enumeration": "输出中是否包含列举内容",
    "has_examples": "输出中是否包含示例",
    "has_reasoning": "输出中是否包含推理过程",
    "paragraph_count": "输出中的段落数量",
    "reasoning_steps": "推理步骤的数量",
    "technical_term_count": "专业术语的数量",
    "technical_term_density": "专业术语密度（术语数/总词数）",
    "uncertainty_count": "表达不确定性的词汇数量",
    
    # 摘要生成
    "bartscore_avg": "基于BART的语义相似度平均分",
    "bartscore_faith": "摘要对原文的忠实度",
    "bartscore_info": "摘要包含的信息量",
    "bertscore_f1": "基于BERT的语义相似度F1值",
    "bertscore_precision": "基于BERT的精确率",
    "bertscore_recall": "基于BERT的召回率",
    "compliance_score": "摘要长度符合要求的程度",
    "compression_ratio": "摘要长度与原文长度的比值",
    "deviation": "摘要长度与目标长度的偏差",
    "in_range": "摘要长度是否在目标范围内",
    "information_density": "单位长度内包含的信息量",
    "length": "摘要的字符长度",
    "rouge_1_f1": "ROUGE-1的F1分数（unigram重叠）",
    "rouge_1_precision": "ROUGE-1的精确率",
    "rouge_1_recall": "ROUGE-1的召回率",
    "rouge_2_f1": "ROUGE-2的F1分数（bigram重叠）",
    "rouge_2_precision": "ROUGE-2的精确率",
    "rouge_2_recall": "ROUGE-2的召回率",
    "rouge_l_f1": "ROUGE-L的F1分数（最长公共子序列）",
    "rouge_l_precision": "ROUGE-L的精确率",
    "rouge_l_recall": "ROUGE-L的召回率",
    "source_length": "原文的字符长度",
    
    # 翻译
    "bleu_1": "BLEU-1分数（单词级n-gram匹配）",
    "bleu_2": "BLEU-2分数（二元组级n-gram匹配）",
    "bleu_3": "BLEU-3分数（三元组级n-gram匹配）",
    "bleu_4": "BLEU-4分数（四元组级n-gram匹配）",
    "chrf": "字符级F分数（character n-gram F-score）",
    "edit_distance": "编辑距离（需要的最少编辑操作数）",
    "edit_similarity": "编辑相似度（1 - 归一化编辑距离）",
    "length_ratio": "译文长度与原文长度的比值",
    "normalized_edit_distance": "归一化编辑距离（编辑距离/最大长度）",
    
    # 推理
    "coherence_score": "推理过程的逻辑连贯性得分",
    "completeness_score": "推理过程的完整性得分",
    "conclusion_correct": "推理结论的正确性",
    "conclusion_f1": "结论与参考答案的F1分数",
    "connector_density": "逻辑连接词密度",
    "depth_score": "推理深度得分",
    "has_conclusion": "输出中是否包含结论",
    "has_logical_connectors": "输出中是否包含逻辑连接词",
    "has_premise": "输出中是否包含前提",
    "has_reasoning_steps": "输出中是否包含推理步骤",
    "keyword_coverage": "关键词覆盖率",
    "reasoning_keyword_count": "推理关键词数量",
    "sentence_count": "输出中的句子数量",
    "step_count": "推理步骤数量",
    
    # 通用
    "accuracy": "准确率",
    "logical_consistency": "逻辑一致性得分"
}

def load_task_metrics(task_key):
    """加载任务的指标数据"""
    task_info = TASKS[task_key]
    file_path = QUALITY_SCORES_DIR / task_info["file"]
    
    if not file_path.exists():
        print(f"警告: 文件不存在 {file_path}")
        return None
    
    try:
        df = pd.read_csv(file_path, index_col=0)
        metrics = df.index.tolist()
        return metrics
    except Exception as e:
        print(f"错误: 读取文件 {file_path} 失败: {e}")
        return None

def generate_metric_table(task_key, metrics):
    """生成单个任务的指标表格"""
    task_info = TASKS[task_key]
    
    lines = []
    lines.append(f"## {task_info['name']}任务 ({task_info['english']})")
    lines.append("")
    lines.append(f"**数据文件**: `{task_info['file']}`")
    lines.append("")
    lines.append("| 指标名称 | 英文名称 | 指标说明 | 优化方向 |")
    lines.append("|---------|---------|---------|---------|")
    
    for metric in metrics:
        cn_name = METRIC_NAMES.get(metric, metric)
        description = METRIC_DESCRIPTIONS.get(metric, f"[待补充] {metric}")
        
        # 判断优化方向
        if metric in ["compilation_rate", "exact_match", "confidence_score", "accuracy",
                      "distinct_1", "distinct_2", "metaphor_count", "bertscore_f1",
                      "bertscore_precision", "bertscore_recall", "bleu_1", "bleu_2", 
                      "bleu_3", "bleu_4", "extraction_confidence", "logical_consistency",
                      "test_pass_rate", "coherence_score", "completeness_score",
                      "conclusion_correct", "depth_score", "edit_similarity",
                      "chrf", "rouge_1_f1", "rouge_2_f1", "rouge_l_f1",
                      "rouge_1_precision", "rouge_2_precision", "rouge_l_precision",
                      "rouge_1_recall", "rouge_2_recall", "rouge_l_recall",
                      "compliance_score", "information_density", "conclusion_f1",
                      "connector_density", "keyword_coverage", "numerical_match",
                      "unique_token_ratio", "parallelism_count", "personification_count",
                      "total_rhetorical_devices"]:
            direction = "越高越好 ↑"
        elif metric in ["bartscore_avg", "bartscore_faith", "bartscore_info"]:
            direction = "越接近0越好 ↑"
        elif metric in ["perplexity", "edit_distance", "normalized_edit_distance", "deviation"]:
            direction = "越低越好 ↓"
        elif metric in ["has_code", "has_answer", "has_calculation", "has_reasoning",
                       "has_conclusion", "has_enumeration", "has_examples",
                       "has_logical_connectors", "has_premise", "has_reasoning_steps",
                       "in_range"]:
            direction = "1为合格"
        else:
            direction = "适中为佳"
        
        lines.append(f"| {cn_name} | {metric} | {description} | {direction} |")
    
    lines.append("")
    lines.append(f"**核心指标**: {task_info['core_metric_cn']} ({task_info['core_metric']})")
    lines.append(f"**指标数量**: {len(metrics)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)

def generate_summary_table(all_metrics):
    """生成汇总表格"""
    lines = []
    lines.append("## 任务指标汇总")
    lines.append("")
    lines.append("| 任务类型 | 中文名称 | 指标数量 | 核心指标 | 数据文件 |")
    lines.append("|---------|---------|---------|---------|---------|")
    
    for task_key, metrics in all_metrics.items():
        if metrics is None:
            continue
        task_info = TASKS[task_key]
        lines.append(f"| {task_info['english']} | {task_info['name']} | {len(metrics)} | "
                    f"{task_info['core_metric_cn']} | `{task_info['file']}` |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    
    return "\n".join(lines)

def main():
    """主函数"""
    print("开始生成任务-指标对应表...")
    
    # 加载所有任务的指标
    all_metrics = {}
    for task_key in TASKS.keys():
        print(f"处理任务: {TASKS[task_key]['name']}")
        metrics = load_task_metrics(task_key)
        all_metrics[task_key] = metrics
        if metrics:
            print(f"  - 发现 {len(metrics)} 个指标")
    
    # 生成Markdown文档
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 标题
        f.write("# 任务-质量指标对应表\n\n")
        f.write("本文档整理了各任务类型使用的质量评估指标及其说明。\n\n")
        f.write("**自动生成**: 本文档由脚本 `generate_task_metrics_mapping.py` 自动生成\n\n")
        f.write("---\n\n")
        
        # 汇总表
        f.write(generate_summary_table(all_metrics))
        
        # 各任务详细表格
        for task_key in ["code", "creative", "math", "qa", "summary", "translation", "reasoning"]:
            metrics = all_metrics.get(task_key)
            if metrics:
                f.write(generate_metric_table(task_key, metrics))
        
        # 附加说明
        f.write("## 指标分类\n\n")
        f.write("### 按评估维度分类\n\n")
        f.write("#### 1. 准确性指标\n")
        f.write("- **精确匹配类**: exact_match, compilation_rate, accuracy\n")
        f.write("- **相似度类**: BLEU, ROUGE, BERTScore\n")
        f.write("- **语义评分类**: BARTScore\n\n")
        
        f.write("#### 2. 多样性指标\n")
        f.write("- **词汇多样性**: distinct_1, distinct_2\n")
        f.write("- **修辞丰富度**: metaphor_count\n\n")
        
        f.write("#### 3. 结构指标\n")
        f.write("- **长度类**: code_length, answer_length, avg_sentence_length\n")
        f.write("- **复杂度类**: cyclomatic_complexity\n\n")
        
        f.write("#### 4. 置信度指标\n")
        f.write("- **确定性**: confidence_score, certainty_count, extraction_confidence\n\n")
        
        f.write("---\n\n")
        f.write("**生成时间**: 2026-03-09\n")
        f.write("**数据版本**: v3.0\n")
        f.write("**评估模型数量**: 12个主流开源语言模型\n")
    
    print(f"\n✓ 任务-指标对应表已生成: {OUTPUT_FILE}")
    print(f"✓ 共处理 {len([m for m in all_metrics.values() if m])} 个任务")
    print(f"✓ 总指标数: {sum(len(m) for m in all_metrics.values() if m)}")

if __name__ == "__main__":
    main()
