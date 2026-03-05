#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quality Results Visualization Script
Generate academic-standard visualizations for all quality evaluation results

Usage:
    python visualize_quality_results.py
    python visualize_quality_results.py --results-dir data/analize/results
    python visualize_quality_results.py --output-dir data/analize/results/figures
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse
import sys

# Import visualization utilities
sys.path.insert(0, str(Path(__file__).parent))
from visualization_utils import (
    setup_academic_style,
    get_academic_colors,
    save_academic_figure,
    get_figure_size,
    SCATTER_CONFIG,
    BAR_CONFIG,
    HEATMAP_CONFIG,
    FONT_SIZES,
    GRID_CONFIG
)


# ============================================================================
# Data Loading Functions
# ============================================================================

def load_quality_results(results_dir: Path) -> dict:
    """Load all quality evaluation results"""
    results = {}
    
    quality_types = [
        'code_quality',
        'creative_quality',
        'math_quality',
        'qa_quality',
        'qa_quality_academic',
        'reasoning_quality',
        'summary_quality',
        'translation_quality'
    ]
    
    for qtype in quality_types:
        qtype_dir = results_dir / qtype
        if not qtype_dir.exists():
            continue
        
        # Find summary CSV file
        summary_files = list(qtype_dir.glob('*summary*.csv'))
        if summary_files:
            try:
                df = pd.read_csv(summary_files[0], encoding='utf-8')
                results[qtype] = df
                print(f"  ✅ Loaded {qtype}: {len(df)} records")
            except Exception as e:
                print(f"  ⚠️  Failed to load {qtype}: {e}")
    
    return results


# ============================================================================
# Visualization Functions
# ============================================================================

def plot_overall_quality_comparison(results: dict, output_dir: Path):
    """Plot overall quality comparison across all task types"""
    print("  📊 Generating: Overall quality comparison...")
    
    # Aggregate data
    all_data = []
    for qtype, df in results.items():
        task_name = qtype.replace('_quality', '').replace('_', ' ').title()
        
        if 'model' in df.columns and 'overall_score' in df.columns:
            for _, row in df.iterrows():
                all_data.append({
                    'task': task_name,
                    'model': row['model'],
                    'score': row['overall_score']
                })
        elif 'model' in df.columns:
            # Try to find any score column
            score_cols = [col for col in df.columns if 'score' in col.lower() and col != 'model']
            if score_cols:
                for _, row in df.iterrows():
                    all_data.append({
                        'task': task_name,
                        'model': row['model'],
                        'score': row[score_cols[0]]
                    })
    
    if not all_data:
        print("    ⚠️  No data available for overall comparison")
        return
    
    df_all = pd.DataFrame(all_data)
    
    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=get_figure_size('double_column'))
    
    tasks = df_all['task'].unique()
    models = df_all['model'].unique()
    
    x = np.arange(len(tasks))
    width = 0.8 / len(models)
    
    colors = get_academic_colors(len(models), 'colorblind')
    
    for idx, (model, color) in enumerate(zip(models, colors)):
        model_data = df_all[df_all['model'] == model]
        values = []
        for task in tasks:
            task_val = model_data[model_data['task'] == task]['score'].values
            values.append(task_val[0] if len(task_val) > 0 else 0)
        
        offset = (idx - len(models)/2 + 0.5) * width
        ax.bar(x + offset, values, width, label=model, color=color,
               edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Task Type', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Quality Score', fontsize=FONT_SIZES['label'])
    ax.set_title('Overall Quality Comparison Across Tasks', 
                 fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(tasks, rotation=45, ha='right')
    ax.legend(loc='best', fontsize=FONT_SIZES['legend']-1, framealpha=0.8, ncol=2)
    ax.grid(axis='y', **GRID_CONFIG)
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'overall_quality_comparison', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: overall_quality_comparison")


def plot_model_performance_heatmap(results: dict, output_dir: Path):
    """Plot heatmap of model performance across tasks"""
    print("  📊 Generating: Model performance heatmap...")
    
    # Aggregate data
    all_data = []
    for qtype, df in results.items():
        task_name = qtype.replace('_quality', '').replace('_', ' ').title()
        
        if 'model' in df.columns and 'overall_score' in df.columns:
            for _, row in df.iterrows():
                all_data.append({
                    'task': task_name,
                    'model': row['model'],
                    'score': row['overall_score']
                })
        elif 'model' in df.columns:
            score_cols = [col for col in df.columns if 'score' in col.lower() and col != 'model']
            if score_cols:
                for _, row in df.iterrows():
                    all_data.append({
                        'task': task_name,
                        'model': row['model'],
                        'score': row[score_cols[0]]
                    })
    
    if not all_data:
        print("    ⚠️  No data available for heatmap")
        return
    
    df_all = pd.DataFrame(all_data)
    
    # Create pivot table
    pivot_data = df_all.pivot_table(
        values='score',
        index='model',
        columns='task',
        aggfunc='mean'
    )
    
    fig, ax = plt.subplots(figsize=get_figure_size('double_column_square'))
    
    sns.heatmap(
        pivot_data,
        annot=True,
        fmt='.3f',
        cmap='RdYlGn',
        ax=ax,
        linewidths=0.5,
        linecolor='gray',
        cbar_kws={'label': 'Quality Score', 'shrink': 0.8}
    )
    
    ax.set_title('Model Performance Heatmap Across Tasks', 
                 fontsize=FONT_SIZES['title'], fontweight='bold', pad=10)
    ax.set_xlabel('Task Type', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Model', fontsize=FONT_SIZES['label'])
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'model_performance_heatmap', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: model_performance_heatmap")


def plot_task_specific_visualizations(results: dict, output_dir: Path):
    """Generate task-specific visualizations"""
    print("  📊 Generating: Task-specific visualizations...")
    
    for qtype, df in results.items():
        task_name = qtype.replace('_quality', '')
        print(f"    - Processing {task_name}...")
        
        task_output_dir = output_dir / qtype
        task_output_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate bar chart for each task
        if 'model' in df.columns and 'overall_score' in df.columns:
            fig, ax = plt.subplots(figsize=get_figure_size('single_column_tall'))
            
            df_sorted = df.sort_values('overall_score', ascending=True)
            colors = get_academic_colors(1, 'colorblind')
            
            ax.barh(df_sorted['model'], df_sorted['overall_score'], 
                   color=colors[0], edgecolor='black', linewidth=0.5)
            
            ax.set_xlabel('Quality Score', fontsize=FONT_SIZES['label'])
            ax.set_ylabel('Model', fontsize=FONT_SIZES['label'])
            ax.set_title(f'{task_name.replace("_", " ").title()} Quality Scores', 
                        fontsize=FONT_SIZES['title'], fontweight='bold')
            ax.grid(axis='x', **GRID_CONFIG)
            
            plt.tight_layout()
            save_academic_figure(fig, task_output_dir / f'{task_name}_scores', ['pdf', 'png'])
            plt.close()


def plot_model_ranking(results: dict, output_dir: Path):
    """Plot overall model ranking"""
    print("  📊 Generating: Model ranking...")
    
    # Calculate average scores across all tasks
    model_scores = {}
    
    for qtype, df in results.items():
        if 'model' in df.columns and 'overall_score' in df.columns:
            for _, row in df.iterrows():
                model = row['model']
                score = row['overall_score']
                if model not in model_scores:
                    model_scores[model] = []
                model_scores[model].append(score)
    
    if not model_scores:
        print("    ⚠️  No data available for ranking")
        return
    
    # Calculate average
    avg_scores = {model: np.mean(scores) for model, scores in model_scores.items()}
    
    # Sort by score
    sorted_models = sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)
    
    fig, ax = plt.subplots(figsize=get_figure_size('single_column_tall'))
    
    models = [m[0] for m in sorted_models]
    scores = [m[1] for m in sorted_models]
    
    colors = get_academic_colors(1, 'colorblind')
    
    ax.barh(models, scores, color=colors[0], edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('Average Quality Score', fontsize=FONT_SIZES['label'])
    ax.set_ylabel('Model', fontsize=FONT_SIZES['label'])
    ax.set_title('Overall Model Ranking', 
                 fontsize=FONT_SIZES['title'], fontweight='bold')
    ax.grid(axis='x', **GRID_CONFIG)
    
    plt.tight_layout()
    save_academic_figure(fig, output_dir / 'model_ranking', ['pdf', 'png'])
    plt.close()
    
    print("    ✅ Saved: model_ranking")


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Generate quality results visualizations')
    parser.add_argument('--results-dir', default='data/analize/results',
                        help='Directory containing quality results')
    parser.add_argument('--output-dir', default='data/analize/visualization/figures',
                        help='Output directory for figures')
    args = parser.parse_args()
    
    # Setup paths
    results_dir = Path(args.results_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print("\n" + "="*60)
    print("📊 Generating Quality Results Visualizations")
    print("="*60 + "\n")
    print(f"Results directory: {results_dir}")
    print(f"Output directory: {output_dir}\n")
    
    # Check if results directory exists
    if not results_dir.exists():
        print(f"❌ Error: Results directory not found: {results_dir}")
        sys.exit(1)
    
    # Load data
    print("📂 Loading quality results...")
    results = load_quality_results(results_dir)
    
    if not results:
        print("❌ Error: No quality results found")
        sys.exit(1)
    
    print(f"\n  ✅ Loaded {len(results)} quality result sets\n")
    
    # Setup academic style
    setup_academic_style()
    
    # Generate visualizations
    print("🎨 Generating visualizations...")
    print("-" * 60)
    
    try:
        plot_overall_quality_comparison(results, output_dir)
        plot_model_performance_heatmap(results, output_dir)
        plot_model_ranking(results, output_dir)
        plot_task_specific_visualizations(results, output_dir)
        
        print("-" * 60)
        print("\n✅ All visualizations generated successfully!")
        print(f"📁 Output directory: {output_dir}")
        
    except Exception as e:
        print(f"\n❌ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()