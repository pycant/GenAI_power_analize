#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建模型回答对比矩阵

功能：
1. 为每个任务类型创建独立的对比表
2. 行：模型名称
3. 列：题号（question_1, question_2, ...）
4. 单元格：模型的回答文本
5. 便于横向对比不同模型在相同题目上的表现
"""

import pandas as pd
from pathlib import Path
import sys

# 确保输出使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ComparisonMatrixCreator:
    """对比矩阵创建器"""
    
    def __init__(self, input_file: str = "data/analize/pre_data/responses_raw.csv",
                 output_dir: str = "data/analize/pre_data/comparison_matrices"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self) -> pd.DataFrame:
        """加载原始数据"""
        print(f"📂 加载数据: {self.input_file}")
        df = pd.read_csv(self.input_file, encoding='utf-8-sig')
        print(f"✅ 加载 {len(df)} 条数据\n")
        return df
    
    def assign_question_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        为每个任务类型的题目分配题号
        
        策略：按 timestamp 排序，相同 timestamp 的题目认为是同一题
        """
        df = df.copy()
        df['question_id'] = None
        
        for task_type in df['task_type'].unique():
            task_mask = df['task_type'] == task_type
            task_df = df[task_mask].copy()
            
            # 按 timestamp 和 prompt 分组，分配题号
            # 相同的 prompt 认为是同一题
            unique_prompts = task_df['prompt'].unique()
            prompt_to_qid = {prompt: f"q{i+1:02d}" for i, prompt in enumerate(unique_prompts)}
            
            df.loc[task_mask, 'question_id'] = task_df['prompt'].map(prompt_to_qid)
        
        return df
    
    def create_response_matrix(self, df: pd.DataFrame, task_type: str) -> pd.DataFrame:
        """
        创建回答对比矩阵（完整回答）
        
        Args:
            df: 数据框
            task_type: 任务类型
            
        Returns:
            透视表，行=模型，列=题号，值=回答
        """
        task_df = df[df['task_type'] == task_type].copy()
        
        if len(task_df) == 0:
            return None
        
        # 创建透视表
        pivot = task_df.pivot_table(
            index='model',
            columns='question_id',
            values='response',
            aggfunc='first'  # 如果有重复，取第一个
        )
        
        # 按题号排序列
        pivot = pivot.reindex(sorted(pivot.columns), axis=1)
        
        # 按模型名称排序行
        pivot = pivot.sort_index()
        
        return pivot
    
    def create_metadata_matrix(self, df: pd.DataFrame, task_type: str, 
                               metric: str) -> pd.DataFrame:
        """
        创建元数据对比矩阵（性能指标）
        
        Args:
            df: 数据框
            task_type: 任务类型
            metric: 指标名称（如 'throughput_tps', 'latency_s'）
            
        Returns:
            透视表，行=模型，列=题号，值=指标值
        """
        task_df = df[df['task_type'] == task_type].copy()
        
        if len(task_df) == 0:
            return None
        
        # 创建透视表
        pivot = task_df.pivot_table(
            index='model',
            columns='question_id',
            values=metric,
            aggfunc='first'
        )
        
        # 按题号排序列
        pivot = pivot.reindex(sorted(pivot.columns), axis=1)
        
        # 按模型名称排序行
        pivot = pivot.sort_index()
        
        return pivot
    
    def create_prompt_reference(self, df: pd.DataFrame, task_type: str) -> pd.DataFrame:
        """
        创建题目参考表（题号 -> 完整 prompt）
        
        Args:
            df: 数据框
            task_type: 任务类型
            
        Returns:
            题号和对应的 prompt
        """
        task_df = df[df['task_type'] == task_type].copy()
        
        if len(task_df) == 0:
            return None
        
        # 获取每个题号的第一个 prompt
        prompt_ref = task_df.groupby('question_id')['prompt'].first().reset_index()
        prompt_ref.columns = ['question_id', 'prompt']
        
        # 按题号排序
        prompt_ref = prompt_ref.sort_values('question_id')
        
        return prompt_ref
    
    def save_matrices(self, df: pd.DataFrame):
        """保存所有对比矩阵"""
        
        print("="*60)
        print("开始创建对比矩阵")
        print("="*60 + "\n")
        
        task_types = sorted(df['task_type'].unique())
        
        for task_type in task_types:
            print(f"处理任务类型: {task_type}")
            
            # 创建任务专属目录
            task_dir = self.output_dir / task_type
            task_dir.mkdir(exist_ok=True)
            
            # 1. 回答对比矩阵
            response_matrix = self.create_response_matrix(df, task_type)
            if response_matrix is not None:
                output_file = task_dir / f"{task_type}_responses.csv"
                response_matrix.to_csv(output_file, encoding='utf-8-sig')
                print(f"  ✅ 回答矩阵: {output_file}")
                print(f"     尺寸: {response_matrix.shape[0]} 模型 × {response_matrix.shape[1]} 题目")
            
            # 2. 性能指标矩阵
            metrics = ['throughput_tps', 'latency_s', 'gpu_energy_j', 
                      'gpu_power_avg_w', 'response_length', 'token_count']
            
            for metric in metrics:
                metric_matrix = self.create_metadata_matrix(df, task_type, metric)
                if metric_matrix is not None:
                    output_file = task_dir / f"{task_type}_{metric}.csv"
                    metric_matrix.to_csv(output_file, encoding='utf-8-sig')
            
            print(f"  ✅ 性能指标: {len(metrics)} 个矩阵")
            
            # 3. 题目参考表
            prompt_ref = self.create_prompt_reference(df, task_type)
            if prompt_ref is not None:
                output_file = task_dir / f"{task_type}_prompts.csv"
                prompt_ref.to_csv(output_file, index=False, encoding='utf-8-sig')
                print(f"  ✅ 题目参考: {output_file}")
            
            print()
        
        # 创建总览文件
        self.create_overview(df)
    
    def create_overview(self, df: pd.DataFrame):
        """创建总览文件"""
        print("="*60)
        print("创建总览文件")
        print("="*60 + "\n")
        
        # 统计信息
        overview = []
        
        for task_type in sorted(df['task_type'].unique()):
            task_df = df[df['task_type'] == task_type]
            
            overview.append({
                'task_type': task_type,
                'total_samples': len(task_df),
                'num_models': task_df['model'].nunique(),
                'num_questions': task_df['question_id'].nunique(),
                'avg_response_length': task_df['response_length'].mean(),
                'avg_throughput': task_df['throughput_tps'].mean(),
                'avg_latency': task_df['latency_s'].mean(),
                'avg_energy': task_df['gpu_energy_j'].mean()
            })
        
        overview_df = pd.DataFrame(overview)
        overview_file = self.output_dir / 'overview.csv'
        overview_df.to_csv(overview_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ 总览文件: {overview_file}\n")
        print(overview_df.to_string(index=False))
        print()
    
    def run(self):
        """运行完整流程"""
        try:
            # 加载数据
            df = self.load_data()
            
            # 分配题号
            print("🔢 分配题号...")
            df = self.assign_question_numbers(df)
            print(f"✅ 题号分配完成\n")
            
            # 保存矩阵
            self.save_matrices(df)
            
            print("="*60)
            print("✅ 对比矩阵创建完成！")
            print("="*60)
            print(f"\n输出目录: {self.output_dir}")
            print("\n文件结构:")
            print("  comparison_matrices/")
            print("  ├── overview.csv                    # 总览")
            print("  ├── code/")
            print("  │   ├── code_responses.csv          # 回答对比")
            print("  │   ├── code_prompts.csv            # 题目参考")
            print("  │   ├── code_throughput_tps.csv     # 吞吐量")
            print("  │   ├── code_latency_s.csv          # 延迟")
            print("  │   ├── code_gpu_energy_j.csv       # 能耗")
            print("  │   └── ...                         # 其他指标")
            print("  ├── creative/")
            print("  ├── math/")
            print("  └── ...")
            
        except Exception as e:
            print(f"\n❌ 创建过程出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    creator = ComparisonMatrixCreator()
    creator.run()


if __name__ == '__main__':
    main()
