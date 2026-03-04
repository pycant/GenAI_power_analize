#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取所有模型的生成回答数据

功能：
1. 遍历所有模型目录，加载实验结果
2. 提取生成的回答文本和元数据
3. 保存为 CSV 格式（自动处理换行符和特殊字符）
4. 生成数据统计报告

输出：
- data/analize/pre_data/responses_raw.csv: 原始回答数据
- data/analize/pre_data/responses_summary.csv: 统计摘要
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import sys

# 确保输出使用 UTF-8 编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ResponseExtractor:
    """回答数据提取器"""
    
    def __init__(self, data_dir: str = "data", output_dir: str = "data/analize/pre_data"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 模型列表
        self.models = [
            'deepseek_8b_ol_q4km',
            'gemma_2b_hf_4bit',
            'gemma_2b_hf_8bit',
            'gemma_4b_ol_q4km',
            'phi3_4b_hf_4bit',
            'phi3_4b_hf_8bit',
            'qwen_4b_ol_q4km',
            'qwen_8b_ol_q4km',
            'qwen25_3b_hf_4bit',
            'qwen25_3b_hf_8bit',
            'qwen25_7b_hf_4bit',
            'qwen25_7b_hf_8bit'
        ]
    
    def load_experiment_results(self, model_name: str) -> tuple:
        """
        加载单个模型的实验结果（raw 和 summary）
        
        Args:
            model_name: 模型名称
            
        Returns:
            (raw_data, summary_data) 元组
        """
        model_dir = self.data_dir / model_name
        
        if not model_dir.exists():
            print(f"⚠️  模型目录不存在: {model_dir}")
            return [], []
        
        # 查找 raw 和 summary 文件
        raw_files = list(model_dir.glob("*_raw.json"))
        summary_files = list(model_dir.glob("*_summary.json"))
        
        if not raw_files or not summary_files:
            print(f"⚠️  未找到完整实验结果: {model_dir}")
            return [], []
        
        # 加载最新的实验结果
        latest_raw = max(raw_files, key=lambda p: p.stat().st_mtime)
        latest_summary = max(summary_files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_raw, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            with open(latest_summary, 'r', encoding='utf-8') as f:
                summary_data = json.load(f)
            
            print(f"✅ 加载 {model_name}: {len(summary_data)} 个实验 (raw + summary)")
            return raw_data, summary_data
        except Exception as e:
            print(f"❌ 加载失败 {model_name}: {e}")
            return [], []
    
    def extract_response_data(self, raw_exp: Dict[str, Any], summary_exp: Dict[str, Any], 
                            model_name: str) -> Dict[str, Any]:
        """
        从 raw 和 summary 数据中提取回答数据
        
        Args:
            raw_exp: raw.json 中的实验数据（包含完整回答）
            summary_exp: summary.json 中的实验数据（包含性能指标）
            model_name: 模型名称
            
        Returns:
            提取的数据字典
        """
        # 基础信息
        exp_id = summary_exp.get('experiment_id', '')
        config = summary_exp.get('config_ref', {})
        task_type = config.get('task_type', 'unknown')
        
        # 从 raw 中提取完整的 prompt 和 response
        raw_conversation = raw_exp.get('conversation', [])
        
        if not raw_conversation:
            return None
        
        # 获取第一轮对话
        first_turn = raw_conversation[0]
        prompt = first_turn.get('prompt', '')
        response = first_turn.get('response', '')
        
        # 从 summary 中获取性能指标
        performance = summary_exp.get('performance', {})
        throughput = performance.get('throughput_tokens_per_sec', 0)
        latency = performance.get('total_time_seconds', 0)
        token_count = performance.get('token_count', 0)
        
        # 资源指标
        resources = summary_exp.get('resources', {})
        gpu_energy = resources.get('gpu_energy_j', 0)
        gpu_power_avg = resources.get('gpu_power_avg_w', 0)
        
        # 质量指标（如果有）
        quality = summary_exp.get('quality', {})
        bartscore = quality.get('bartscore', None)
        has_reference = quality.get('has_reference', False)
        
        # 元数据
        metadata = summary_exp.get('metadata', {})
        timestamp = metadata.get('timestamp', '')
        temperature = metadata.get('temperature', 0)
        max_tokens = metadata.get('max_tokens', 0)
        
        # 计算实际回答长度
        response_length = len(response) if response else 0
        
        return {
            'experiment_id': exp_id,
            'model': model_name,
            'task_type': task_type,
            'timestamp': timestamp,
            'prompt': prompt,
            'response': response,
            'response_length': response_length,
            'token_count': token_count,
            'throughput_tps': throughput,
            'latency_s': latency,
            'gpu_energy_j': gpu_energy,
            'gpu_power_avg_w': gpu_power_avg,
            'bartscore': bartscore,
            'has_reference': has_reference,
            'temperature': temperature,
            'max_tokens': max_tokens
        }
    
    def extract_all_responses(self) -> pd.DataFrame:
        """
        提取所有模型的回答数据（从 raw.json 获取完整回答）
        
        Returns:
            包含所有回答的 DataFrame
        """
        all_responses = []
        
        print("\n" + "="*60)
        print("开始提取模型回答数据（从 raw.json）")
        print("="*60 + "\n")
        
        for model in self.models:
            print(f"处理模型: {model}")
            
            # 加载 raw 和 summary 数据
            raw_data, summary_data = self.load_experiment_results(model)
            
            if not raw_data or not summary_data:
                print()
                continue
            
            # 创建 experiment_id 到 raw 数据的映射
            raw_map = {}
            for raw_exp in raw_data:
                exp_id = raw_exp.get('experiment_id', '')
                if exp_id:
                    raw_map[exp_id] = raw_exp
            
            # 提取每个实验的回答
            for summary_exp in summary_data:
                exp_id = summary_exp.get('experiment_id', '')
                
                # 从 raw_map 中找到对应的 raw 数据
                raw_exp = raw_map.get(exp_id)
                
                if raw_exp:
                    response_data = self.extract_response_data(raw_exp, summary_exp, model)
                    if response_data:
                        all_responses.append(response_data)
                else:
                    print(f"  ⚠️  未找到 raw 数据: {exp_id}")
            
            print()
        
        # 转换为 DataFrame
        df = pd.DataFrame(all_responses)
        
        print(f"✅ 总共提取 {len(df)} 条回答数据")
        print(f"📊 模型数量: {df['model'].nunique()}")
        print(f"📊 任务类型: {df['task_type'].unique().tolist()}")
        
        return df
    
    def generate_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        生成统计摘要
        
        Args:
            df: 原始数据 DataFrame
            
        Returns:
            统计摘要 DataFrame
        """
        summary = df.groupby(['model', 'task_type']).agg({
            'experiment_id': 'count',
            'response_length': ['mean', 'std', 'min', 'max'],
            'token_count': ['mean', 'std'],
            'throughput_tps': ['mean', 'std'],
            'latency_s': ['mean', 'std'],
            'gpu_energy_j': ['mean', 'std'],
            'gpu_power_avg_w': ['mean', 'std']
        }).round(2)
        
        # 重命名列
        summary.columns = ['_'.join(col).strip('_') for col in summary.columns.values]
        summary = summary.reset_index()
        summary.rename(columns={'experiment_id_count': 'sample_count'}, inplace=True)
        
        return summary
    
    def save_data(self, df: pd.DataFrame):
        """
        保存数据到文件
        
        Args:
            df: 要保存的 DataFrame
        """
        # 保存原始数据（CSV 会自动处理换行符和特殊字符）
        output_file = self.output_dir / 'responses_raw.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 原始数据已保存: {output_file}")
        print(f"   文件大小: {output_file.stat().st_size / 1024:.2f} KB")
        
        # 生成并保存统计摘要
        summary = self.generate_summary(df)
        summary_file = self.output_dir / 'responses_summary.csv'
        summary.to_csv(summary_file, index=False, encoding='utf-8-sig')
        print(f"💾 统计摘要已保存: {summary_file}")
        
        # 打印数据预览
        print("\n" + "="*60)
        print("数据预览（前 3 行）")
        print("="*60)
        print(df[['model', 'task_type', 'response_length', 'token_count']].head(3))
        
        print("\n" + "="*60)
        print("统计摘要预览")
        print("="*60)
        print(summary.head(10))
    
    def run(self):
        """运行完整的提取流程"""
        try:
            # 提取数据
            df = self.extract_all_responses()
            
            if df.empty:
                print("\n❌ 未提取到任何数据")
                return
            
            # 保存数据
            self.save_data(df)
            
            print("\n" + "="*60)
            print("✅ 数据提取完成！")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ 提取过程出错: {e}")
            import traceback
            traceback.print_exc()


def main():
    """主函数"""
    extractor = ResponseExtractor()
    extractor.run()


if __name__ == '__main__':
    main()
