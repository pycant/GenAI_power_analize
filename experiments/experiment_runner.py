#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GenAI模型能效评级体系实验执行脚本
支持 Ollama 和 Hugging Face 模型的统一调用接口
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

# 尝试导入资源监控器
try:
    from experiments.monitor import ResourceMonitor
    MONITOR_AVAILABLE = True
except ImportError:
    print("警告: ResourceMonitor不可用，将使用基础监控")
    MONITOR_AVAILABLE = False

# 延迟导入 HF 和 BARTScore，避免在不需要时导入失败
HF_AVAILABLE = False
BARTSCORE_AVAILABLE = False


class ExperimentRunner:
    """实验运行器，支持Ollama和Hugging Face模型"""
    
    def __init__(self, output_dir="./results"):
        """
        初始化实验运行器
        
        Args:
            output_dir (str): 结果输出目录
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化HF模型加载器（延迟导入）
        self.hf_loader = None
        self.hf_models_cache = {}
        
        # 尝试导入和初始化 HF
        global HF_AVAILABLE
        if not HF_AVAILABLE:
            try:
                from src.model_deployment.hf_loader import HuggingFaceModelLoader
                self.hf_loader = HuggingFaceModelLoader()
                HF_AVAILABLE = True
                print("[OK] Hugging Face模型加载器初始化成功")
            except Exception as e:
                print(f"[WARNING] Hugging Face模型加载器不可用: {e}")
                HF_AVAILABLE = False
        
        # 初始化BARTScore评估器（延迟导入）
        self.bart_scorer = None
        global BARTSCORE_AVAILABLE
        if not BARTSCORE_AVAILABLE:
            try:
                from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
                self.bart_scorer = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')
                BARTSCORE_AVAILABLE = True
                print("[OK] BARTScore评估器初始化成功")
            except Exception as e:
                print(f"[WARNING] BARTScore不可用: {e}")
                BARTSCORE_AVAILABLE = False
    
    def parse_model_spec(self, model_spec):
        """
        解析模型规格字符串
        
        格式:
        - Ollama模型: "model_name" 或 "ollama:model_name"
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
            
            # 规范化路径：转换为绝对路径并使用正斜杠
            model_path_obj = Path(model_path)
            if not model_path_obj.is_absolute():
                # 相对路径，转换为相对于项目根目录的绝对路径
                model_path_obj = project_root / model_path
            
            # 转换为字符串，使用正斜杠（跨平台兼容）
            normalized_path = str(model_path_obj.resolve()).replace('\\', '/')
            
            return {
                "type": "huggingface",
                "path": normalized_path,
                "quantize": quantize,
                "display_name": f"HF:{model_path_obj.name}:{quantize or 'fp16'}"
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
            # 默认为Ollama模型（向后兼容）
            return {
                "type": "ollama",
                "name": model_spec,
                "display_name": f"Ollama:{model_spec}"
            }
    
    def check_ollama_service(self):
        """检查Ollama服务是否运行"""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"[OK] Ollama版本: {result.stdout.strip()}")
                return True
            else:
                print("[WARNING]  Ollama服务未运行或不可访问")
                return False
        except Exception as e:
            print(f"[WARNING]  检查Ollama服务时出错: {e}")
            return False
    
    def call_ollama_generate(self, model_name, prompt, max_tokens=500, 
                           temperature=0.7, top_p=0.9, context=None):
        """
        调用Ollama API生成文本
        
        Args:
            model_name (str): 模型名称
            prompt (str): 输入提示
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            top_p (float): Top-p采样参数
            context (list, optional): 对话上下文（用于多轮对话）
            
        Returns:
            dict: 生成结果和性能数据
        """
        print(f"  --> 调用Ollama模型: {model_name}")
        
        import requests
        
        start_time = time.time()
        try:
            request_data = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "num_predict": max_tokens
                }
            }
            
            # 如果有上下文，添加到请求中
            if context is not None:
                request_data["context"] = context
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=request_data,
                timeout=300
            )
            end_time = time.time()
            
            if response.status_code != 200:
                raise Exception(f"Ollama API返回错误: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # 处理响应：某些模型（如qwen3、deepseek-r1）将回复放在thinking字段
            generated_text = result.get("response", "")
            thinking_text = result.get("thinking", "")
            
            # 如果response为空但thinking有内容，使用thinking
            if not generated_text and thinking_text:
                generated_text = thinking_text
                print(f"  [INFO]  注意: 该模型将回复放在thinking字段中")
            
            # 计算token数（简单估算）
            token_count = len(generated_text.split())
            
            return {
                "response": generated_text,
                "thinking": thinking_text,  # 保存thinking字段
                "total_time": end_time - start_time,
                "token_count": token_count,
                "success": True,
                "context": result.get("context"),  # 保存context用于下一轮
                "metadata": result
            }
        except requests.Timeout:
            end_time = time.time()
            raise Exception(f"Ollama调用超时 ({end_time - start_time:.2f}秒)")
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
        
        print(f"  --> 调用HF模型: {Path(model_path).name} (量化: {quantize or 'fp16'})")
        
        # 构建缓存键
        cache_key = f"{model_path}:{quantize}"
        
        # 加载模型（首次或从缓存）
        if cache_key not in self.hf_models_cache:
            print(f"  --> 首次加载模型，可能需要一些时间...")
            model, tokenizer = self.hf_loader.load_model(
                model_path,
                quantize=quantize,
                device="auto"
            )
            self.hf_models_cache[cache_key] = (model, tokenizer)
        else:
            print(f"  --> 从缓存加载模型")
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
    
    def _run_with_per_turn_monitoring(self, model_info, prompts, task_type, reference_text,
                                      max_tokens, temperature, top_p, keep_context):
        """
        使用每轮独立监控的方式运行实验
        
        Returns:
            dict: 实验结果（包含每轮的详细监控数据）
        """
        conversation = []
        context = None  # Ollama的对话上下文
        total_time = 0
        total_tokens = 0
        
        # 收集每轮的汇总数据
        per_turn_summary = []
        
        try:
            for turn_idx, prompt in enumerate(prompts, 1):
                print(f"\n  [轮次 {turn_idx}/{len(prompts)}]")
                print(f"  提示: {prompt[:50]}..." if len(prompt) > 50 else f"  提示: {prompt}")
                
                # 为该轮启动独立监控
                if MONITOR_AVAILABLE:
                    turn_monitor = ResourceMonitor(interval=0.2)
                    turn_monitor.start()
                    use_advanced_monitor = True
                else:
                    turn_resource_data, turn_monitor_thread = self.monitor_resources_basic(30)
                    use_advanced_monitor = False
                
                # 调用模型生成
                turn_start_time = time.time()
                
                if model_info["type"] == "ollama":
                    response = self.call_ollama_generate(
                        model_info["name"],
                        prompt,
                        max_tokens,
                        temperature,
                        top_p,
                        context=context if keep_context else None
                    )
                    if keep_context and "context" in response:
                        context = response["context"]
                        
                elif model_info["type"] == "huggingface":
                    if keep_context and turn_idx > 1:
                        history_prompt = ""
                        for i, turn_data in enumerate(conversation, 1):
                            history_prompt += f"用户: {turn_data['prompt']}\n助手: {turn_data['response']}\n\n"
                        history_prompt += f"用户: {prompt}\n助手: "
                        actual_prompt = history_prompt
                    else:
                        actual_prompt = prompt
                    
                    response = self.call_hf_generate(
                        model_info["path"],
                        actual_prompt,
                        max_tokens,
                        temperature,
                        top_p,
                        model_info.get("quantize")
                    )
                else:
                    raise Exception(f"未知的模型类型: {model_info['type']}")
                
                turn_end_time = time.time()
                turn_time = turn_end_time - turn_start_time
                
                # 停止该轮的监控
                if use_advanced_monitor:
                    time.sleep(0.5)
                    turn_monitor.stop()
                    turn_resources = turn_monitor.summary()
                    turn_metrics_full = turn_monitor.to_dict()
                else:
                    turn_monitor_thread.join(timeout=1)
                    # 计算基础资源统计
                    def safe_avg(lst):
                        return sum(lst) / len(lst) if lst else 0
                    def safe_max(lst):
                        return max(lst) if lst else 0
                    
                    turn_resources = {
                        "cpu_percent_avg": safe_avg(turn_resource_data["cpu_percent"]),
                        "cpu_percent_peak": safe_max(turn_resource_data["cpu_percent"]),
                        "mem_used_peak_mb": safe_max(turn_resource_data["memory_percent"]) * psutil.virtual_memory().total / (1024 * 1024 * 100),
                        "gpu_util_avg": safe_avg(turn_resource_data["gpu_utilization"]) if turn_resource_data["gpu_utilization"] else 0,
                        "gpu_util_peak": safe_max(turn_resource_data["gpu_utilization"]) if turn_resource_data["gpu_utilization"] else 0,
                        "gpu_mem_peak_mb": safe_max(turn_resource_data["gpu_memory_used"]) if turn_resource_data["gpu_memory_used"] else 0,
                        "gpu_power_avg_w": 0,
                        "gpu_energy_j": 0,
                        "gpu_temp_peak_c": 0,
                        "cpu_energy_j_approx": 0
                    }
                    turn_metrics_full = {
                        "timestamps": [],
                        "cpu_percent": turn_resource_data["cpu_percent"],
                        "memory_percent": turn_resource_data["memory_percent"],
                        "gpu_utilization": turn_resource_data["gpu_utilization"],
                        "gpu_memory_used": turn_resource_data["gpu_memory_used"],
                        "summary": turn_resources
                    }
                
                # 计算该轮的性能指标
                turn_throughput = response["token_count"] / turn_time if turn_time > 0 else 0
                
                # 保存该轮的完整数据
                turn_data = {
                    "turn": turn_idx,
                    "prompt": prompt,
                    "response": response["response"],
                    "thinking": response.get("thinking", ""),  # 保存thinking字段（如果有）
                    "performance": {
                        "time_seconds": turn_time,
                        "token_count": response["token_count"],
                        "throughput_tokens_per_sec": turn_throughput,
                        "latency_per_token_ms": (turn_time * 1000) / response["token_count"] if response["token_count"] > 0 else 0
                    },
                    "resources": turn_resources,
                    "system_metrics_full": turn_metrics_full
                }
                
                conversation.append(turn_data)
                total_time += turn_time
                total_tokens += response["token_count"]
                
                # 收集汇总数据
                per_turn_summary.append({
                    "turn": turn_idx,
                    "time_seconds": turn_time,
                    "token_count": response["token_count"],
                    "throughput": turn_throughput,
                    "gpu_energy_j": turn_resources.get("gpu_energy_j", 0),
                    "gpu_power_avg_w": turn_resources.get("gpu_power_avg_w", 0)
                })
                
                print(f"  [OK] 生成完成 (耗时: {turn_time:.2f}秒, Tokens: {response['token_count']})")
                if turn_resources.get("gpu_energy_j", 0) > 0:
                    print(f"    GPU能耗: {turn_resources['gpu_energy_j']:.2f} J")
                
        except Exception as e:
            print(f"  [ERROR] 生成文本失败: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        # 评估质量（使用最后一轮的回复）
        print(f"  --> 评估生成质量...")
        final_response = conversation[-1]["response"] if conversation else ""
        quality_scores = self.evaluate_quality(final_response, reference_text)
        
        # 计算整体性能指标
        overall_throughput = total_tokens / total_time if total_time > 0 else 0
        
        # 计算整体资源汇总
        total_gpu_energy = sum(turn["gpu_energy_j"] for turn in per_turn_summary)
        avg_gpu_power = sum(turn["gpu_power_avg_w"] for turn in per_turn_summary) / len(per_turn_summary) if per_turn_summary else 0
        peak_gpu_util = max((turn_data["resources"].get("gpu_util_peak", 0) for turn_data in conversation), default=0)
        peak_gpu_mem = max((turn_data["resources"].get("gpu_mem_peak_mb", 0) for turn_data in conversation), default=0)
        
        # 整理结果
        result = {
            "model": model_info["display_name"],
            "model_info": model_info,
            "prompts": [turn_data["prompt"] for turn_data in conversation],
            "task_type": task_type,
            "keep_context": keep_context,
            "per_turn_monitoring": True,
            "conversation": conversation,  # 包含每轮的详细数据
            "generated_text": final_response,
            "all_responses": [turn_data["response"] for turn_data in conversation],
            "performance": {
                "total_time_seconds": total_time,
                "token_count": total_tokens,
                "throughput_tokens_per_sec": overall_throughput,
                "latency_per_token_ms": (total_time * 1000) / total_tokens if total_tokens > 0 else 0,
                "turns": len(prompts),
                "avg_time_per_turn": total_time / len(prompts) if len(prompts) > 0 else 0,
                "per_turn_summary": per_turn_summary
            },
            "resources": {
                "total_gpu_energy_j": total_gpu_energy,
                "avg_gpu_power_w": avg_gpu_power,
                "peak_gpu_util": peak_gpu_util,
                "peak_gpu_mem_mb": peak_gpu_mem
            },
            "quality": quality_scores,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
        }
        
        print(f"  [OK] 实验完成")
        print(f"    - 对话轮数: {len(prompts)}")
        print(f"    - 总生成时间: {total_time:.2f}秒")
        print(f"    - 平均每轮: {total_time/len(prompts):.2f}秒")
        print(f"    - 总Token数: {total_tokens}")
        print(f"    - 吞吐量: {overall_throughput:.2f} tokens/s")
        if total_gpu_energy > 0:
            print(f"    - 总GPU能耗: {total_gpu_energy:.2f} J")
        
        return result
    
    def _run_with_overall_monitoring(self, model_info, prompts, task_type, reference_text,
                                     max_tokens, temperature, top_p, keep_context):
        """
        使用整体监控的方式运行实验（原有逻辑）
        
        Returns:
            dict: 实验结果（包含整体监控数据）
        """
        # 启动资源监控
        if MONITOR_AVAILABLE:
            monitor = ResourceMonitor(interval=0.2)
            monitor.start()
            use_advanced_monitor = True
        else:
            resource_data, monitor_thread = self.monitor_resources_basic(30)
            use_advanced_monitor = False
        
        # 多轮对话
        all_responses = []
        all_prompts = []
        context = None  # Ollama的对话上下文
        total_time = 0
        total_tokens = 0
        
        try:
            for turn_idx, prompt in enumerate(prompts, 1):
                print(f"\n  [轮次 {turn_idx}/{len(prompts)}]")
                print(f"  提示: {prompt[:50]}..." if len(prompt) > 50 else f"  提示: {prompt}")
                
                all_prompts.append(prompt)
                
                if model_info["type"] == "ollama":
                    response = self.call_ollama_generate(
                        model_info["name"],
                        prompt,
                        max_tokens,
                        temperature,
                        top_p,
                        context=context if keep_context else None
                    )
                    if keep_context and "context" in response:
                        context = response["context"]
                    
                elif model_info["type"] == "huggingface":
                    if keep_context and turn_idx > 1:
                        history_prompt = ""
                        for i, (p, r) in enumerate(zip(all_prompts[:-1], all_responses), 1):
                            history_prompt += f"用户: {p}\n助手: {r}\n\n"
                        history_prompt += f"用户: {prompt}\n助手: "
                        actual_prompt = history_prompt
                    else:
                        actual_prompt = prompt
                    
                    response = self.call_hf_generate(
                        model_info["path"],
                        actual_prompt,
                        max_tokens,
                        temperature,
                        top_p,
                        model_info.get("quantize")
                    )
                else:
                    raise Exception(f"未知的模型类型: {model_info['type']}")
                
                all_responses.append(response["response"])
                total_time += response["total_time"]
                total_tokens += response["token_count"]
                
                print(f"  [OK] 生成完成 (耗时: {response['total_time']:.2f}秒, Tokens: {response['token_count']})")
                
        except Exception as e:
            print(f"  [ERROR] 生成文本失败: {e}")
            if use_advanced_monitor:
                monitor.stop()
            else:
                monitor_thread.join(timeout=1)
            return None
        
        # 停止资源监控
        resource_full = None
        if use_advanced_monitor:
            time.sleep(0.5)
            monitor.stop()
            resource_summary = monitor.summary()
            resource_full = monitor.to_dict()
        else:
            monitor_thread.join(timeout=1)
            def safe_avg(lst):
                return sum(lst) / len(lst) if lst else 0
            def safe_max(lst):
                return max(lst) if lst else 0
            
            resource_summary = {
                "cpu_percent_avg": safe_avg(resource_data["cpu_percent"]),
                "cpu_percent_peak": safe_max(resource_data["cpu_percent"]),
                "mem_used_peak_mb": safe_max(resource_data["memory_percent"]) * psutil.virtual_memory().total / (1024 * 1024 * 100),
                "gpu_util_avg": safe_avg(resource_data["gpu_utilization"]) if resource_data["gpu_utilization"] else 0,
                "gpu_util_peak": safe_max(resource_data["gpu_utilization"]) if resource_data["gpu_utilization"] else 0,
                "gpu_mem_peak_mb": safe_max(resource_data["gpu_memory_used"]) if resource_data["gpu_memory_used"] else 0,
                "gpu_power_avg_w": 0,
                "gpu_energy_j": 0,
                "gpu_temp_peak_c": 0,
                "cpu_energy_j_approx": 0
            }
            resource_full = {
                "timestamps": [],
                "cpu_percent": resource_data["cpu_percent"],
                "memory_percent": resource_data["memory_percent"],
                "gpu_utilization": resource_data["gpu_utilization"],
                "gpu_memory_used": resource_data["gpu_memory_used"],
                "summary": resource_summary
            }
        
        # 评估质量
        print(f"  --> 评估生成质量...")
        final_response = all_responses[-1] if all_responses else ""
        quality_scores = self.evaluate_quality(final_response, reference_text)
        
        # 计算性能指标
        throughput = total_tokens / total_time if total_time > 0 else 0
        
        # 整理结果
        result = {
            "model": model_info["display_name"],
            "model_info": model_info,
            "prompts": all_prompts,
            "task_type": task_type,
            "keep_context": keep_context,
            "per_turn_monitoring": False,
            "conversation": [
                {"turn": i+1, "prompt": p, "response": r}
                for i, (p, r) in enumerate(zip(all_prompts, all_responses))
            ],
            "generated_text": final_response,
            "all_responses": all_responses,
            "performance": {
                "total_time_seconds": total_time,
                "token_count": total_tokens,
                "throughput_tokens_per_sec": throughput,
                "latency_per_token_ms": (total_time * 1000) / total_tokens if total_tokens > 0 else 0,
                "turns": len(prompts),
                "avg_time_per_turn": total_time / len(prompts) if len(prompts) > 0 else 0
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
            "system_metrics_summary": resource_summary,
            "system_metrics_full": resource_full,
            "quality": quality_scores,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p
            }
        }
        
        print(f"  [OK] 实验完成")
        print(f"    - 对话轮数: {len(prompts)}")
        print(f"    - 总生成时间: {total_time:.2f}秒")
        print(f"    - 平均每轮: {total_time/len(prompts):.2f}秒")
        print(f"    - 总Token数: {total_tokens}")
        print(f"    - 吞吐量: {throughput:.2f} tokens/s")
        if resource_summary["gpu_energy_j"] > 0:
            print(f"    - GPU能耗: {resource_summary['gpu_energy_j']:.2f} J")
        
        return result
    
    def monitor_resources_basic(self, duration):
        """
        基础资源监控（使用threading和psutil）
        
        Args:
            duration (float): 监控持续时间（秒）
            
        Returns:
            tuple: (资源数据字典, 监控线程)
        """
        resource_data = {
            "cpu_percent": [],
            "memory_percent": [],
            "gpu_utilization": [],
            "gpu_memory_used": []
        }
        
        def collect():
            """资源收集函数"""
            for _ in range(int(duration * 2)):  # 每0.5秒采样一次
                # CPU和内存使用率
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent
                resource_data["cpu_percent"].append(cpu_percent)
                resource_data["memory_percent"].append(memory_percent)
                
                # GPU监控（如果可用）
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    resource_data["gpu_utilization"].append(util.gpu)
                    resource_data["gpu_memory_used"].append(mem_info.used / 1024 / 1024)  # MB
                except:
                    if resource_data["gpu_utilization"]:
                        resource_data["gpu_utilization"].append(0)
                        resource_data["gpu_memory_used"].append(0)
                
                time.sleep(0.5)
        
        monitor_thread = threading.Thread(target=collect)
        monitor_thread.start()
        return resource_data, monitor_thread
    
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
            print(f"  [WARNING]  质量评估时出错: {e}")
            return {
                "bartscore": None,
                "error": str(e),
                "has_reference": reference_text is not None
            }
    
    def run_single_experiment(self, model, prompts, task_type, reference_text=None, 
                            max_tokens=500, temperature=0.7, top_p=0.9, 
                            keep_context=False, per_turn_monitoring=False):
        """
        运行单次实验（支持多轮对话）
        
        Args:
            model (str): 模型规格字符串
            prompts (str or list): 输入提示（单个字符串或多个提示的列表）
            task_type (str): 任务类型
            reference_text (str, optional): 参考文本
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            top_p (float): Top-p采样参数
            keep_context (bool): 是否保持对话上下文（多轮对话）
            per_turn_monitoring (bool): 是否为每轮对话独立监控资源（默认False）
            
        Returns:
            dict: 实验结果
        """
        # 兼容性处理：如果prompts是字符串，转换为列表
        if isinstance(prompts, str):
            prompts = [prompts]
        
        # 解析模型规格
        model_info = self.parse_model_spec(model)
        
        print(f"\n{'='*60}")
        print(f"开始实验")
        print(f"  模型: {model_info['display_name']}")
        print(f"  任务: {task_type}")
        print(f"  对话轮数: {len(prompts)}")
        print(f"  保持上下文: {'是' if keep_context else '否'}")
        print(f"  分轮监控: {'是' if per_turn_monitoring else '否'}")
        print(f"{'='*60}")
        
        # 根据 per_turn_monitoring 参数选择执行方式
        if per_turn_monitoring and len(prompts) > 1:
            # 多轮对话且启用分轮监控：使用独立监控方式
            return self._run_with_per_turn_monitoring(
                model_info, prompts, task_type, reference_text,
                max_tokens, temperature, top_p, keep_context
            )
        else:
            # 单轮对话或未启用分轮监控：使用整体监控方式
            return self._run_with_overall_monitoring(
                model_info, prompts, task_type, reference_text,
                max_tokens, temperature, top_p, keep_context
            )
        
    
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
            output_file = os.path.join(self.output_dir, f"experiment_results_raw_{timestamp}.json")
        
        results = []
        
        print(f"\n{'='*70}")
        print(f"开始执行实验套件")
        print(f"  测试用例数: {len(test_cases)}")
        print(f"  原始数据保存到: {output_file}")
        print(f"{'='*70}\n")
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] 运行实验")
            
            # 兼容性处理：支持 "prompt" 或 "prompts"
            prompts = case.get("prompts", case.get("prompt"))
            if prompts is None:
                print(f"  [ERROR] 测试用例缺少 'prompts' 或 'prompt' 字段")
                continue
            
            result = self.run_single_experiment(
                model=case["model"],
                prompts=prompts,
                task_type=case["task_type"],
                reference_text=case.get("reference_text"),
                max_tokens=case.get("max_tokens", 500),
                temperature=case.get("temperature", 0.7),
                top_p=case.get("top_p", 0.9),
                keep_context=case.get("keep_context", False),
                per_turn_monitoring=case.get("per_turn_monitoring", False)
            )
            
            if result:
                results.append(result)
                
                # 实时保存原始结果
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                print(f"  [OK] 结果已保存")
            else:
                print(f"  [ERROR] 实验失败")
            
            # 短暂延迟，避免资源竞争
            if i < len(test_cases):
                time.sleep(2)
        
        # 生成汇总文件
        summary_file = output_file.replace("_raw_", "_summary_")
        self._generate_summary_file(results, summary_file)
        
        print(f"\n{'='*70}")
        print(f"所有实验完成")
        print(f"  成功: {len(results)}/{len(test_cases)}")
        print(f"  原始数据: {output_file}")
        print(f"  汇总数据: {summary_file}")
        print(f"{'='*70}\n")
        
        return results
    
    def _generate_summary_file(self, results, summary_file):
        """
        生成汇总文件（不包含详细监控数据）
        
        Args:
            results (list): 实验结果列表
            summary_file (str): 汇总文件路径
        """
        summary_results = []
        
        for result in results:
            # 提取汇总数据
            summary = {
                "model": result["model"],
                "model_info": result["model_info"],
                "prompts": result["prompts"],
                "task_type": result["task_type"],
                "keep_context": result["keep_context"],
                "per_turn_monitoring": result.get("per_turn_monitoring", False),
                "performance": result["performance"],
                "resources": result["resources"],
                "quality": result["quality"],
                "metadata": result["metadata"]
            }
            
            # 如果是分轮监控，添加每轮的汇总（不包含详细监控数据）
            if result.get("per_turn_monitoring", False):
                summary["conversation_summary"] = [
                    {
                        "turn": turn["turn"],
                        "prompt": turn["prompt"][:100] + "..." if len(turn["prompt"]) > 100 else turn["prompt"],
                        "response": turn["response"][:200] + "..." if len(turn["response"]) > 200 else turn["response"],
                        "performance": turn["performance"],
                        "resources": turn["resources"]
                    }
                    for turn in result["conversation"]
                ]
            else:
                # 整体监控模式，保留简化的对话记录
                summary["conversation"] = result["conversation"]
            
            summary_results.append(summary)
        
        # 保存汇总文件
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_results, f, ensure_ascii=False, indent=2)
        
        print(f"  [OK] 汇总数据已保存到: {summary_file}")
    
    def cleanup(self):
        """清理资源"""
        if self.hf_loader and self.hf_models_cache:
            print("\n清理HF模型缓存...")
            for cache_key in list(self.hf_models_cache.keys()):
                del self.hf_models_cache[cache_key]
            
            # 清理GPU缓存
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    print("  [OK] GPU缓存已清理")
            except:
                pass


def create_sample_test_cases():
    """创建示例测试用例"""
    return [
        {
            "model": "qwen3:4b",
            "prompt": "请解释牛顿第一定律。",
            "task_type": "knowledge_qa",
            "reference_text": "牛顿第一定律，也称为惯性定律，指出：一个物体如果不受外力作用，或者所受合外力为零，那么静止的物体会保持静止状态，运动的物体会保持匀速直线运动状态。",
            "max_tokens": 200,
            "temperature": 0.7
        },
        {
            "model": "gemma3:4b",
            "prompt": "写一篇关于人工智能对未来社会影响的短文。",
            "task_type": "creative_writing",
            "max_tokens": 300,
            "temperature": 0.8
        }
    ]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="GenAI模型能效评级体系实验执行脚本（支持Ollama和Hugging Face）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模型规格格式:
  Ollama模型: "model_name" 或 "ollama:model_name"
  HF模型: "hf:model_path" 或 "hf:model_path:quantize"
  
示例:
  python experiment_runner.py --sample
  python experiment_runner.py --config test_cases.json --output-dir ./results
        """
    )
    
    parser.add_argument("--output-dir", default="./results", help="结果输出目录")
    parser.add_argument("--config", help="测试用例配置文件路径（JSON格式）")
    parser.add_argument("--sample", action="store_true", help="运行示例测试用例")
    
    args = parser.parse_args()
    
    # 初始化实验运行器
    runner = ExperimentRunner(output_dir=args.output_dir)
    
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

