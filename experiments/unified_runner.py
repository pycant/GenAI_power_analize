#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一模型实验运行器
支持Ollama和Hugging Face模型的统一调用接口
"""

import subprocess
import time
import json
import psutil
import threading
from datetime import datetime
import argparse
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入资源监控器
from experiments.monitor import ResourceMonitor

# 尝试导入HF模型加载器
try:
    from src.model_deployment.hf_loader import HuggingFaceModelLoader
    HF_AVAILABLE = True
except ImportError:
    print("警告: Hugging Face模型加载器不可用")
    HF_AVAILABLE = False

# 尝试导入BARTScore
try:
    from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
    BARTSCORE_AVAILABLE = True
except ImportError:
    print("警告: BARTScore模块不可用，将跳过质量评估")
    BARTSCORE_AVAILABLE = False


class UnifiedExperimentRunner:
    """统一实验运行器，支持Ollama和Hugging Face模型"""
    
    def __init__(self, output_dir="./results"):
        """
        初始化实验运行器
        
        Args:
            output_dir (str): 结果输出目录
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化HF模型加载器
        self.hf_loader = None
        self.hf_models_cache = {}  # 缓存已加载的HF模型
        
        if HF_AVAILABLE:
            try:
                self.hf_loader = HuggingFaceModelLoader()
                print("✓ Hugging Face模型加载器初始化成功")
            except Exception as e:
                print(f"⚠️  Hugging Face模型加载器初始化失败: {e}")
                self.hf_loader = None
        
        # 初始化BARTScore评估器
        self.bart_scorer = None
        if BARTSCORE_AVAILABLE:
            try:
                self.bart_scorer = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')
                print("✓ BARTScore评估器初始化成功")
            except Exception as e:
                print(f"⚠️  BARTScore初始化失败: {e}")
                self.bart_scorer = None
    
    def parse_model_spec(self, model_spec):
        """
        解析模型规格字符串
        
        格式:
        - Ollama模型: "ollama:model_name" 或直接 "model_name"
        - HF模型: "hf:model_path" 或 "hf:model_path:quantize"
        
        Args:
            model_spec (str): 模型规格字符串
            
        Returns:
            dict: 包含模型类型、名称/路径、量化选项的字典
        """
        if model_spec.startswith("hf:"):
            # Hugging Face模型
            parts = model_spec[3:].split(":")
            model_path = parts[0]
            quantize = parts[1] if len(parts) > 1 else None
            
            return {
                "type": "huggingface",
                "path": model_path,
                "quantize": quantize,
                "display_name": f"HF:{Path(model_path).name}:{quantize or 'fp16'}"
            }
        elif model_spec.startswith("ollama:"):
            # 显式指定Ollama模型
            model_name = model_spec[7:]
            return {
                "type": "ollama",
                "name": model_name,
                "display_name": f"Ollama:{model_name}"
            }
        else:
            # 默认为Ollama模型
            return {
                "type": "ollama",
                "name": model_spec,
                "display_name": f"Ollama:{model_spec}"
            }
    
    def check_ollama_service(self):
        """检查Ollama服务是否运行"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"✓ Ollama版本: {result.stdout.strip()}")
                return True
            else:
                print("⚠️  Ollama服务未运行或不可访问")
                return False
        except Exception as e:
            print(f"⚠️  检查Ollama服务时出错: {e}")
            return False
    
    def call_ollama_generate(self, model_name, prompt, max_tokens=500, 
                           temperature=0.7, top_p=0.9):
        """
        调用Ollama API生成文本
        
        Args:
            model_name (str): 模型名称
            prompt (str): 输入提示
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            top_p (float): Top-p采样参数
            
        Returns:
            dict: 生成结果和性能数据
        """
        print(f"  → 调用Ollama模型: {model_name}")
        
        # 使用ollama API
        import requests
        
        start_time = time.time()
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "top_p": top_p,
                        "num_predict": max_tokens
                    }
                },
                timeout=300
            )
            end_time = time.time()
            
            if response.status_code != 200:
                raise Exception(f"Ollama API返回错误: {response.status_code}")
            
            result = response.json()
            generated_text = result.get("response", "")
            
            # 计算token数（简单估算）
            token_count = len(generated_text.split())
            
            return {
                "response": generated_text,
                "total_time": end_time - start_time,
                "token_count": token_count,
                "success": True,
                "metadata": result
            }
            
        except Exception as e:
            end_time = time.time()
            raise Exception(f"Ollama调用失败: {str(e)} (耗时: {end_time - start_time:.2f}秒)")
    
    def call_hf_generate(self, model_path, prompt, max_tokens=500,
                        temperature=0.7, top_p=0.9, quantize=None):
        """
        调用Hugging Face模型生成文本
        
        Args:
            model_path (str): 模型路径
            prompt (str): 输入提示
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            top_p (float): Top-p采样参数
            quantize (str): 量化选项 ("4bit", "8bit", None)
            
        Returns:
            dict: 生成结果和性能数据
        """
        if not HF_AVAILABLE or self.hf_loader is None:
            raise Exception("Hugging Face模型加载器不可用")
        
        print(f"  → 调用HF模型: {model_path} (量化: {quantize or 'fp16'})")
        
        # 构建缓存键
        cache_key = f"{model_path}:{quantize}"
        
        # 加载模型（首次或从缓存）
        if cache_key not in self.hf_models_cache:
            print(f"  → 首次加载模型，可能需要一些时间...")
            model, tokenizer = self.hf_loader.load_model(
                model_path,
                quantize=quantize,
                device="auto"
            )
            self.hf_models_cache[cache_key] = (model, tokenizer)
        else:
            print(f"  → 从缓存加载模型")
            model, tokenizer = self.hf_models_cache[cache_key]
        
        # 生成文本
        start_time = time.time()
        try:
            generated_text = self.hf_loader.generate(
                model,
                tokenizer,
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True
            )
            end_time = time.time()
            
            # 计算token数
            token_count = len(tokenizer.encode(generated_text))
            
            return {
                "response": generated_text,
                "total_time": end_time - start_time,
                "token_count": token_count,
                "success": True,
                "metadata": {
                    "model_path": model_path,
                    "quantize": quantize
                }
            }
            
        except Exception as e:
            end_time = time.time()
            raise Exception(f"HF模型调用失败: {str(e)} (耗时: {end_time - start_time:.2f}秒)")
    
    def evaluate_quality(self, generated_text, reference_text=None):
        """
        使用BARTScore评估生成质量
        
        Args:
            generated_text (str): 生成的文本
            reference_text (str, optional): 参考文本
            
        Returns:
            dict: 质量评估结果
        """
        if not BARTSCORE_AVAILABLE or self.bart_scorer is None:
            return {
                "bartscore": None,
                "has_reference": reference_text is not None,
                "generated_text_length": len(generated_text)
            }
        
        try:
            if reference_text:
                scores = self.bart_scorer.score([reference_text], [generated_text])
                return {
                    "bartscore": float(scores[0]),
                    "has_reference": True
                }
            else:
                return {
                    "bartscore": None,
                    "generated_text_length": len(generated_text),
                    "has_reference": False
                }
        except Exception as e:
            print(f"  ⚠️  质量评估时出错: {e}")
            return {
                "bartscore": None,
                "error": str(e),
                "has_reference": reference_text is not None
            }
    
    def run_single_experiment(self, model_spec, prompt, task_type,
                            reference_text=None, max_tokens=500,
                            temperature=0.7, top_p=0.9):
        """
        运行单次实验
        
        Args:
            model_spec (str): 模型规格字符串
            prompt (str): 输入提示
            task_type (str): 任务类型
            reference_text (str, optional): 参考文本
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            top_p (float): Top-p采样参数
            
        Returns:
            dict: 实验结果
        """
        # 解析模型规格
        model_info = self.parse_model_spec(model_spec)
        
        print(f"\n{'='*60}")
        print(f"开始实验")
        print(f"  模型: {model_info['display_name']}")
        print(f"  任务: {task_type}")
        print(f"{'='*60}")
        
        # 启动资源监控
        monitor = ResourceMonitor(interval=0.2)
        monitor.start()
        
        # 生成文本
        try:
            if model_info["type"] == "ollama":
                response = self.call_ollama_generate(
                    model_info["name"],
                    prompt,
                    max_tokens,
                    temperature,
                    top_p
                )
            elif model_info["type"] == "huggingface":
                response = self.call_hf_generate(
                    model_info["path"],
                    prompt,
                    max_tokens,
                    temperature,
                    top_p,
                    model_info.get("quantize")
                )
            else:
                raise Exception(f"未知的模型类型: {model_info['type']}")
                
        except Exception as e:
            print(f"  ❌ 生成文本失败: {e}")
            monitor.stop()
            return None
        
        # 停止资源监控
        time.sleep(0.5)  # 等待最后的采样
        monitor.stop()
        
        # 评估质量
        print(f"  → 评估生成质量...")
        quality_scores = self.evaluate_quality(response["response"], reference_text)
        
        # 获取资源监控数据
        resource_summary = monitor.summary()
        
        # 计算性能指标
        total_time = response["total_time"]
        token_count = response["token_count"]
        throughput = token_count / total_time if total_time > 0 else 0
        
        # 整理结果
        result = {
            "model_spec": model_spec,
            "model_info": model_info,
            "prompt": prompt,
            "task_type": task_type,
            "generated_text": response["response"],
            "performance": {
                "total_time_seconds": total_time,
                "token_count": token_count,
                "throughput_tokens_per_sec": throughput,
                "latency_per_token_ms": (total_time * 1000) / token_count if token_count > 0 else 0
            },
            "resources": {
                "cpu_percent_avg": resource_summary["cpu_percent_avg"],
                "cpu_percent_peak": resource_summary["cpu_percent_peak"],
                "mem_used_peak_mb": resource_summary["mem_used_peak_mb"],
                "gpu_util_avg": resource_summary["gpu_util_avg"],
                "gpu_util_peak": resource_summary["gpu_util_peak"],
                "gpu_mem_peak_mb": resource_summary["gpu_mem_peak_mb"],
                "gpu_power_avg_w": resource_summary["gpu_power_avg_w"],
                "gpu_energy_j": resource_summary["gpu_energy_j"],
                "gpu_temp_peak_c": resource_summary["gpu_temp_peak_c"],
                "cpu_energy_j_approx": resource_summary["cpu_energy_j_approx"]
            },
            "quality": quality_scores,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "response_metadata": response.get("metadata", {})
            }
        }
        
        print(f"  ✓ 实验完成")
        print(f"    - 生成时间: {total_time:.2f}秒")
        print(f"    - Token数: {token_count}")
        print(f"    - 吞吐量: {throughput:.2f} tokens/s")
        print(f"    - GPU能耗: {resource_summary['gpu_energy_j']:.2f} J")
        
        return result
    
    def run_experiment_suite(self, test_cases, output_file=None):
        """
        运行完整的实验套件
        
        Args:
            test_cases (list): 测试用例列表
            output_file (str, optional): 输出文件路径
            
        Returns:
            list: 实验结果列表
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"unified_results_{timestamp}.json")
        
        results = []
        
        print(f"\n{'='*70}")
        print(f"开始执行实验套件")
        print(f"  测试用例数: {len(test_cases)}")
        print(f"  结果保存到: {output_file}")
        print(f"{'='*70}\n")
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] 运行实验")
            
            result = self.run_single_experiment(
                model_spec=case["model"],
                prompt=case["prompt"],
                task_type=case["task_type"],
                reference_text=case.get("reference_text"),
                max_tokens=case.get("max_tokens", 500),
                temperature=case.get("temperature", 0.7),
                top_p=case.get("top_p", 0.9)
            )
            
            if result:
                results.append(result)
                
                # 实时保存结果
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                print(f"  ✓ 结果已保存")
            else:
                print(f"  ❌ 实验失败")
            
            # 短暂延迟，避免资源竞争
            if i < len(test_cases):
                time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"所有实验完成")
        print(f"  成功: {len(results)}/{len(test_cases)}")
        print(f"  结果文件: {output_file}")
        print(f"{'='*70}\n")
        
        return results
    
    def cleanup(self):
        """清理资源"""
        # 卸载HF模型
        if self.hf_loader and self.hf_models_cache:
            print("\n清理HF模型缓存...")
            for cache_key in list(self.hf_models_cache.keys()):
                del self.hf_models_cache[cache_key]
            
            # 清理GPU缓存
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    print("  ✓ GPU缓存已清理")
            except:
                pass


def create_sample_test_cases():
    """创建示例测试用例（包含Ollama和HF模型）"""
    return [
        # Ollama模型
        {
            "model": "qwen3:4b",
            "prompt": "请用一句话解释什么是人工智能。",
            "task_type": "qa",
            "max_tokens": 128,
            "temperature": 0.7
        },
        # HF模型（4bit量化）
        {
            "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
            "prompt": "请用一句话解释什么是人工智能。",
            "task_type": "qa",
            "max_tokens": 128,
            "temperature": 0.7
        },
        # HF模型（无量化）
        {
            "model": "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct",
            "prompt": "写一首关于春天的短诗。",
            "task_type": "creative",
            "max_tokens": 200,
            "temperature": 0.8
        }
    ]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="统一模型实验运行器（支持Ollama和Hugging Face）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模型规格格式:
  Ollama模型: "model_name" 或 "ollama:model_name"
  HF模型: "hf:model_path" 或 "hf:model_path:quantize"
  
示例:
  python unified_runner.py --sample
  python unified_runner.py --config test_cases.json
        """
    )
    
    parser.add_argument("--output-dir", default="./results", help="结果输出目录")
    parser.add_argument("--config", help="测试用例配置文件路径（JSON格式）")
    parser.add_argument("--sample", action="store_true", help="运行示例测试用例")
    
    args = parser.parse_args()
    
    # 初始化实验运行器
    runner = UnifiedExperimentRunner(output_dir=args.output_dir)
    
    # 确定测试用例
    test_cases = []
    if args.config:
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                test_cases = json.load(f)
            print(f"从配置文件加载了 {len(test_cases)} 个测试用例")
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            return 1
    elif args.sample:
        test_cases = create_sample_test_cases()
        print(f"使用 {len(test_cases)} 个示例测试用例")
    else:
        test_cases = create_sample_test_cases()[:1]
        print("运行默认示例测试用例")
    
    # 运行实验
    try:
        results = runner.run_experiment_suite(test_cases)
        runner.cleanup()
        print(f"\n实验执行完成，共获得 {len(results)} 条结果")
        return 0
    except KeyboardInterrupt:
        print("\n实验被用户中断")
        runner.cleanup()
        return 1
    except Exception as e:
        print(f"\n实验执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        runner.cleanup()
        return 1


if __name__ == "__main__":
    sys.exit(main())
