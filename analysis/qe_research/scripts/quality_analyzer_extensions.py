"""
质量分析器扩展 - 各任务类型的专项分析函数
这些函数将被添加到 QualityDataAnalyzer 类中
"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging

logger = logging.getLogger(__name__)


def _task7_creative_analysis(self):
    """任务7: 创意写作任务专项分析"""
    if 'creative' not in self.quality_data:
        return
    
    df = self.quality_data['creative']
    
    # 选择创意写作相关指标
    metrics = ['distinct_2', 'perplexity']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 1:
        logger.warning("创意写作任务缺少必要指标")
        return
    
    fig, axes = plt.subplots(1, len(available_metrics), figsize=(6*len(available_metrics), 6))
    if len(available_metrics) == 1:
        axes = [axes]
    
    for idx, metric in enumerate(available_metrics):
        ax = axes[idx]
        
        # 按指标排序
        df_sorted = df.sort_values(metric, ascending=(metric != 'perplexity'))
        
        x = range(len(df_sorted))
        y = df_sorted[metric]
        
        ax.bar(x, y, color=self.academic_colors[idx], 
               edgecolor='black', alpha=0.7)
        ax.set_xticks(x)
        ax.set_xticklabels(df_sorted['model'], rotation=45, ha='right')
        ax.set_xlabel('模型', fontsize=11)
        ax.set_ylabel(metric, fontsize=11)
        ax.set_title(f'{metric}对比', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
    
    plt.suptitle('任务7: 创意写作任务专项分析', 
                fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    self._save_fig('07_creative_submetrics.png')


def _task7_qa_analysis(self):
    """任务7: 问答任务专项分析"""
    if 'qa' not in self.quality_data:
        return
    
    df = self.quality_data['qa']
    
    # 选择问答相关指标
    metrics = ['has_answer', 'answer_length', 'technical_term_density', 
               'confidence_score', 'has_reasoning']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 2:
        logger.warning("问答任务缺少必要指标")
        return
    
    # 归一化
    df_norm = self._normalize_scores(df, available_metrics)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(df))
    bottom = np.zeros(len(df))
    
    for i, metric in enumerate(available_metrics[:5]):  # 最多5个指标
        ax.bar(x, df_norm[metric], bottom=bottom, label=metric,
              color=self.academic_colors[i], edgecolor='white', linewidth=0.5)
        bottom += df_norm[metric]
    
    ax.set_xticks(x)
    ax.set_xticklabels(df['model'], rotation=45, ha='right')
    ax.set_xlabel('模型', fontsize=11)
    ax.set_ylabel('归一化得分', fontsize=11)
    ax.set_title('任务7: 问答任务子指标构成', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    self._save_fig('07_qa_submetrics.png')


def _task7_summary_analysis(self):
    """任务7: 摘要任务专项分析"""
    if 'summary' not in self.quality_data:
        return
    
    df = self.quality_data['summary']
    
    # 选择摘要相关指标
    metrics = ['rouge_1', 'rouge_2', 'rouge_l', 'bert_score', 
               'compression_ratio', 'information_density']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 2:
        logger.warning("摘要任务缺少必要指标")
        return
    
    # 归一化
    df_norm = self._normalize_scores(df, available_metrics)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(df))
    bottom = np.zeros(len(df))
    
    for i, metric in enumerate(available_metrics[:6]):  # 最多6个指标
        ax.bar(x, df_norm[metric], bottom=bottom, label=metric,
              color=self.academic_colors[i], edgecolor='white', linewidth=0.5)
        bottom += df_norm[metric]
    
    ax.set_xticks(x)
    ax.set_xticklabels(df['model'], rotation=45, ha='right')
    ax.set_xlabel('模型', fontsize=11)
    ax.set_ylabel('归一化得分', fontsize=11)
    ax.set_title('任务7: 摘要任务子指标构成', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    self._save_fig('07_summary_submetrics.png')


def _task7_translation_analysis(self):
    """任务7: 翻译任务专项分析"""
    if 'translation' not in self.quality_data:
        return
    
    df = self.quality_data['translation']
    
    # 选择翻译相关指标
    metrics = ['bleu_score', 'semantic_fidelity', 'fluency', 
               'terminology_accuracy', 'cultural_adaptation']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 2:
        logger.warning("翻译任务缺少必要指标")
        return
    
    # 归一化
    df_norm = self._normalize_scores(df, available_metrics)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(df))
    bottom = np.zeros(len(df))
    
    for i, metric in enumerate(available_metrics):
        ax.bar(x, df_norm[metric], bottom=bottom, label=metric,
              color=self.academic_colors[i], edgecolor='white', linewidth=0.5)
        bottom += df_norm[metric]
    
    ax.set_xticks(x)
    ax.set_xticklabels(df['model'], rotation=45, ha='right')
    ax.set_xlabel('模型', fontsize=11)
    ax.set_ylabel('归一化得分', fontsize=11)
    ax.set_title('任务7: 翻译任务子指标构成', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    self._save_fig('07_translation_submetrics.png')


def _task7_math_analysis(self):
    """任务7: 数学推理任务专项分析"""
    if 'math' not in self.quality_data:
        return
    
    df = self.quality_data['math']
    
    # 选择数学推理相关指标
    metrics = ['answer_correctness', 'reasoning_process', 
               'formula_usage', 'step_clarity']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 2:
        logger.warning("数学推理任务缺少必要指标")
        return
    
    # 归一化
    df_norm = self._normalize_scores(df, available_metrics)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(df))
    bottom = np.zeros(len(df))
    
    for i, metric in enumerate(available_metrics):
        ax.bar(x, df_norm[metric], bottom=bottom, label=metric,
              color=self.academic_colors[i], edgecolor='white', linewidth=0.5)
        bottom += df_norm[metric]
    
    ax.set_xticks(x)
    ax.set_xticklabels(df['model'], rotation=45, ha='right')
    ax.set_xlabel('模型', fontsize=11)
    ax.set_ylabel('归一化得分', fontsize=11)
    ax.set_title('任务7: 数学推理任务子指标构成', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    self._save_fig('07_math_submetrics.png')


def _task7_reasoning_analysis(self):
    """任务7: 逻辑推理任务专项分析"""
    if 'reasoning' not in self.quality_data:
        return
    
    df = self.quality_data['reasoning']
    
    # 选择逻辑推理相关指标
    metrics = ['conclusion_correct', 'completeness_score', 
               'coherence_score', 'depth_score', 'step_count']
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 2:
        logger.warning("逻辑推理任务缺少必要指标")
        return
    
    # 归一化（step_count除外）
    metrics_to_norm = [m for m in available_metrics if m != 'step_count']
    df_norm = self._normalize_scores(df, metrics_to_norm)
    
    # step_count单独处理
    if 'step_count' in available_metrics:
        max_steps = df['step_count'].max()
        if max_steps > 0:
            df_norm['step_count'] = df['step_count'] / max_steps
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    x = range(len(df))
    bottom = np.zeros(len(df))
    
    for i, metric in enumerate(available_metrics):
        ax.bar(x, df_norm[metric], bottom=bottom, label=metric,
              color=self.academic_colors[i], edgecolor='white', linewidth=0.5)
        bottom += df_norm[metric]
    
    ax.set_xticks(x)
    ax.set_xticklabels(df['model'], rotation=45, ha='right')
    ax.set_xlabel('模型', fontsize=11)
    ax.set_ylabel('归一化得分', fontsize=11)
    ax.set_title('任务7: 逻辑推理任务子指标构成', fontsize=13, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    self._save_fig('07_reasoning_submetrics.png')


# 将这些方法添加到 QualityDataAnalyzer 类
def add_task_specific_methods(analyzer_class):
    """将任务专项分析方法添加到分析器类"""
    analyzer_class._task7_creative_analysis = _task7_creative_analysis
    analyzer_class._task7_qa_analysis = _task7_qa_analysis
    analyzer_class._task7_summary_analysis = _task7_summary_analysis
    analyzer_class._task7_translation_analysis = _task7_translation_analysis
    analyzer_class._task7_math_analysis = _task7_math_analysis
    analyzer_class._task7_reasoning_analysis = _task7_reasoning_analysis
