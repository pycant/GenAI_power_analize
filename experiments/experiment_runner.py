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


class ExperimentResult:
    """
    实验结果数据结构
    分离原始数据(raw)和汇总数据(summary)
    """
    
    def __init__(self, experiment_id):
        """
        初始化实验结果
        
        Args:
            experiment_id (str): 实验唯一标识符
        """
        self.experiment_id = experiment_id
        
        # 原始数据结构
        self.raw_data = {
            "experiment_id": experiment_id,
            "config": {},
            "baseline_raw": None,
            "conversation": [],
            "monitoring_data": {
                "start_timestamp": None,
                "end_timestamp": None,
                "measurements": {},
                "events": []
            },
            "metadata": {}
        }
        
        # 汇总数据结构
        self.summary_data = {
            "experiment_id": experiment_id,
            "config_ref": {},
            "baseline_summary": None,
            "performance": {},
            "resources": {},
            "derived_metrics": {},
            "quality": {},
            "conversation_summary": [],
            "metadata": {}
        }
    
    def set_config(self, model, model_info, prompts, task_type, **kwargs):
        """设置配置信息"""
        self.raw_data["config"] = {
            "model": model,
            "model_info": model_info,
            "prompts": prompts,
            "task_type": task_type,
            "keep_context": kwargs.get("keep_context", False),
            "per_turn_monitoring": kwargs.get("per_turn_monitoring", False),
            "max_tokens": kwargs.get("max_tokens"),
            "temperature": kwargs.get("temperature"),
            "top_p": kwargs.get("top_p"),
            "reference_text": kwargs.get("reference_text")
        }
        
        self.summary_data["config_ref"] = {
            "model": model,
            "task_type": task_type,
            "prompts_count": len(prompts) if isinstance(prompts, list) else 1,
            "keep_context": kwargs.get("keep_context", False),
            "per_turn_monitoring": kwargs.get("per_turn_monitoring", False)
        }
    
    def set_baseline_raw(self, baseline_monitor):
        """
        设置原始基线数据
        
        Args:
            baseline_monitor: ResourceMonitor实例
        """
        if not baseline_monitor:
            return
        
        full_data = baseline_monitor.to_dict()
        
        self.raw_data["baseline_raw"] = {
            "duration_seconds": full_data.get("duration_seconds", 0),
            "start_timestamp": full_data["timestamps"][0] if full_data.get("timestamps") else None,
            "end_timestamp": full_data["timestamps"][-1] if full_data.get("timestamps") else None,
            "measurements": {
                "timestamps": full_data.get("timestamps", []),
                "cpu_percent": full_data.get("cpu_percent", []),
                "mem_used_mb": full_data.get("mem_used_mb", []),
                "gpu_util": full_data.get("gpu_util", []),
                "gpu_mem_mb": full_data.get("gpu_mem_mb", []),
                "gpu_power_w": full_data.get("gpu_power_w", []),
                "gpu_temp_c": full_data.get("gpu_temp_c", [])
            }
        }
    
    def set_monitoring_data(self, monitor):
        """
        设置监控数据
        
        Args:
            monitor: ResourceMonitor实例
        """
        if not monitor:
            return
        
        full_data = monitor.to_dict()
        
        self.raw_data["monitoring_data"] = {
            "start_timestamp": full_data["timestamps"][0] if full_data.get("timestamps") else None,
            "end_timestamp": full_data["timestamps"][-1] if full_data.get("timestamps") else None,
            "measurements": {
                "timestamps": full_data.get("timestamps", []),
                "cpu_percent": full_data.get("cpu_percent", []),
                "mem_used_mb": full_data.get("mem_used_mb", []),
                "gpu_util": full_data.get("gpu_util", []),
                "gpu_mem_mb": full_data.get("gpu_mem_mb", []),
                "gpu_power_w": full_data.get("gpu_power_w", []),
                "gpu_temp_c": full_data.get("gpu_temp_c", [])
            },
            "events": full_data.get("events", [])
        }
    
    def add_conversation_turn(self, turn, prompt, response, start_time, end_time, turn_monitor=None):
        """
        添加对话轮次
        
        Args:
            turn (int): 轮次编号
            prompt (str): 输入提示
            response (str): 模型回答
            start_time (float): 开始时间戳
            end_time (float): 结束时间戳
            turn_monitor: 该轮的ResourceMonitor实例（如果启用per_turn_monitoring）
        """
        turn_data = {
            "turn": turn,
            "prompt": prompt,
            "response": response,
            "start_timestamp": start_time,
            "end_timestamp": end_time
        }
        
        # 如果有分轮监控数据，添加到该轮
        if turn_monitor:
            turn_full_data = turn_monitor.to_dict()
            turn_data["monitoring_data"] = {
                "measurements": {
                    "timestamps": turn_full_data.get("timestamps", []),
                    "cpu_percent": turn_full_data.get("cpu_percent", []),
                    "mem_used_mb": turn_full_data.get("mem_used_mb", []),
                    "gpu_util": turn_full_data.get("gpu_util", []),
                    "gpu_mem_mb": turn_full_data.get("gpu_mem_mb", []),
                    "gpu_power_w": turn_full_data.get("gpu_power_w", []),
                    "gpu_temp_c": turn_full_data.get("gpu_temp_c", [])
                },
                "events": turn_full_data.get("events", [])
            }
        
        self.raw_data["conversation"].append(turn_data)
    
    def calculate_summary(self, bart_scorer=None):
        """从原始数据计算汇总指标"""
        import numpy as np
        
        # 计算基线汇总
        if self.raw_data["baseline_raw"]:
            self._calculate_baseline_summary()
        
        # 计算性能指标
        self._calculate_performance_metrics()
        
        # 计算资源指标
        self._calculate_resource_metrics()
        
        # 计算派生指标
        self._calculate_derived_metrics()
        
        # 计算质量指标
        self._calculate_quality_metrics(bart_scorer)
        
        # 生成对话摘要
        self._generate_conversation_summary()
    
    def _calculate_baseline_summary(self):
        """计算基线汇总统计"""
        import numpy as np
        
        baseline_raw = self.raw_data["baseline_raw"]
        measurements = baseline_raw["measurements"]
        
        if not measurements.get("gpu_power_w"):
            return
        
        # 计算能耗（梯形积分）
        energy = self._calculate_energy(
            measurements["timestamps"],
            measurements["gpu_power_w"]
        )
        
        self.summary_data["baseline_summary"] = {
            "duration_seconds": baseline_raw["duration_seconds"],
            "gpu_power_avg_w": float(np.mean(measurements["gpu_power_w"])),
            "gpu_power_peak_w": float(np.max(measurements["gpu_power_w"])),
            "gpu_power_std_w": float(np.std(measurements["gpu_power_w"])),
            "gpu_energy_j": energy,
            "cpu_percent_avg": float(np.mean(measurements["cpu_percent"])),
            "cpu_percent_peak": float(np.max(measurements["cpu_percent"])),
            "gpu_util_avg": float(np.mean(measurements["gpu_util"])),
            "gpu_util_peak": int(np.max(measurements["gpu_util"])),
            "gpu_mem_avg_mb": float(np.mean(measurements["gpu_mem_mb"])),
            "gpu_mem_peak_mb": float(np.max(measurements["gpu_mem_mb"])),
            "gpu_temp_avg_c": float(np.mean(measurements["gpu_temp_c"])),
            "gpu_temp_peak_c": int(np.max(measurements["gpu_temp_c"]))
        }
    
    def _calculate_performance_metrics(self):
        """计算性能指标"""
        monitoring = self.raw_data["monitoring_data"]
        conversation = self.raw_data["conversation"]
        
        if not monitoring.get("start_timestamp") or not monitoring.get("end_timestamp"):
            return
        
        # 计算总时间
        total_time = monitoring["end_timestamp"] - monitoring["start_timestamp"]
        
        # 计算token数（从events中提取）
        total_tokens = sum(
            event["metadata"].get("tokens", 0)
            for event in monitoring.get("events", [])
            if event.get("event") == "inference_end"
        )
        
        # 计算TTFT（首个token时间）
        first_token_event = next(
            (e for e in monitoring.get("events", []) if e.get("event") == "first_token"),
            None
        )
        ttft = (first_token_event["timestamp"] - monitoring["start_timestamp"]) if first_token_event else None
        
        self.summary_data["performance"] = {
            "total_time_seconds": total_time,
            "token_count": total_tokens,
            "output_tokens": total_tokens,
            "throughput_tokens_per_sec": total_tokens / total_time if total_time > 0 else 0,
            "latency_per_token_ms": (total_time * 1000) / total_tokens if total_tokens > 0 else 0,
            "turns": len(conversation),
            "avg_time_per_turn": total_time / len(conversation) if conversation else 0,
            "ttft_seconds": ttft
        }
    
    def _calculate_resource_metrics(self):
        """计算资源指标"""
        import numpy as np
        
        measurements = self.raw_data["monitoring_data"]["measurements"]
        
        if not measurements.get("gpu_power_w"):
            return
        
        # 计算GPU能耗
        gpu_energy = self._calculate_energy(
            measurements["timestamps"],
            measurements["gpu_power_w"]
        )
        
        # 估算CPU能耗（基于CPU使用率和TDP）
        cpu_tdp = 45  # 假设TDP为45W
        cpu_energy = self._calculate_energy(
            measurements["timestamps"],
            [cpu_tdp * (p / 100) for p in measurements.get("cpu_percent", [])]
        )
        
        self.summary_data["resources"] = {
            "cpu_percent_avg": float(np.mean(measurements.get("cpu_percent", [0]))),
            "cpu_percent_peak": float(np.max(measurements.get("cpu_percent", [0]))),
            "cpu_percent_std": float(np.std(measurements.get("cpu_percent", [0]))),
            "mem_used_avg_mb": float(np.mean(measurements.get("mem_used_mb", [0]))),
            "mem_used_peak_mb": float(np.max(measurements.get("mem_used_mb", [0]))),
            "gpu_util_avg": float(np.mean(measurements.get("gpu_util", [0]))),
            "gpu_util_peak": int(np.max(measurements.get("gpu_util", [0]))),
            "gpu_util_std": float(np.std(measurements.get("gpu_util", [0]))),
            "gpu_mem_avg_mb": float(np.mean(measurements.get("gpu_mem_mb", [0]))),
            "gpu_mem_peak_mb": float(np.max(measurements.get("gpu_mem_mb", [0]))),
            "gpu_power_avg_w": float(np.mean(measurements.get("gpu_power_w", [0]))),
            "gpu_power_peak_w": float(np.max(measurements.get("gpu_power_w", [0]))),
            "gpu_power_std_w": float(np.std(measurements.get("gpu_power_w", [0]))),
            "gpu_energy_j": gpu_energy,
            "gpu_temp_avg_c": float(np.mean(measurements.get("gpu_temp_c", [0]))),
            "gpu_temp_peak_c": int(np.max(measurements.get("gpu_temp_c", [0]))),
            "cpu_energy_j_approx": cpu_energy
        }
    
    def _calculate_derived_metrics(self):
        """计算派生指标（增量和能效指标）"""
        baseline = self.summary_data.get("baseline_summary")
        resources = self.summary_data.get("resources", {})
        performance = self.summary_data.get("performance", {})
        
        derived = {}
        
        if baseline and resources:
            # 增量功耗和能耗
            P_idle = baseline["gpu_power_avg_w"]
            P_avg = resources.get("gpu_power_avg_w", 0)
            E_total = resources.get("gpu_energy_j", 0)
            total_time = performance.get("total_time_seconds", 0)
            
            derived["P_idle"] = P_idle
            derived["P_inc"] = max(0, P_avg - P_idle)
            derived["E_inc"] = max(0, E_total - P_idle * total_time)
            
            # 每token能耗
            output_tokens = performance.get("output_tokens", 0)
            if output_tokens > 0 and derived["E_inc"] > 0:
                derived["E_token"] = derived["E_inc"] / output_tokens
            
            # 能效指标
            throughput = performance.get("throughput_tokens_per_sec", 0)
            if P_avg > 0:
                derived["PPW"] = throughput / P_avg
            if E_total > 0:
                derived["TPJ"] = output_tokens / E_total
        
        self.summary_data["derived_metrics"] = derived
    
    def _calculate_quality_metrics(self, bart_scorer=None):
        """计算质量指标"""
        conversation = self.raw_data["conversation"]
        reference_text = self.raw_data["config"].get("reference_text")
        
        if not conversation:
            return
        
        # 获取最后一轮的回答
        final_response = conversation[-1]["response"] if conversation else ""
        
        quality = {
            "bartscore": None,
            "generated_text_length": len(final_response),
            "has_reference": reference_text is not None
        }
        
        # 如果有参考文本且BARTScore可用，计算评分
        if reference_text and bart_scorer:
            try:
                scores = bart_scorer.score([reference_text], [final_response])
                quality["bartscore"] = float(scores[0])
            except Exception as e:
                print(f"  [WARNING] BARTScore计算失败: {e}")
        
        # 计算平均回答长度
        if conversation:
            quality["avg_response_length"] = sum(len(turn["response"]) for turn in conversation) / len(conversation)
        
        self.summary_data["quality"] = quality
    
    def _generate_conversation_summary(self):
        """生成对话摘要"""
        conversation = self.raw_data["conversation"]
        per_turn_monitoring = self.raw_data["config"].get("per_turn_monitoring", False)
        
        summary = []
        for turn_data in conversation:
            turn_summary = {
                "turn": turn_data["turn"],
                "prompt_preview": turn_data["prompt"][:50] + "..." if len(turn_data["prompt"]) > 50 else turn_data["prompt"],
                "response_preview": turn_data["response"][:100] + "..." if len(turn_data["response"]) > 100 else turn_data["response"],
                "response_length": len(turn_data["response"]),
                "duration_seconds": turn_data["end_timestamp"] - turn_data["start_timestamp"]
            }
            
            # 如果启用了分轮监控，计算该轮的资源指标
            if per_turn_monitoring and "monitoring_data" in turn_data:
                turn_measurements = turn_data["monitoring_data"]["measurements"]
                if turn_measurements.get("gpu_power_w"):
                    import numpy as np
                    turn_summary["gpu_power_avg_w"] = float(np.mean(turn_measurements["gpu_power_w"]))
                    turn_summary["gpu_energy_j"] = self._calculate_energy(
                        turn_measurements["timestamps"],
                        turn_measurements["gpu_power_w"]
                    )
            
            # 从events中提取该轮的token数
            turn_events = [
                e for e in self.raw_data["monitoring_data"].get("events", [])
                if e.get("metadata", {}).get("turn") == turn_data["turn"]
                and e.get("event") == "inference_end"
            ]
            if turn_events:
                tokens = turn_events[0]["metadata"].get("tokens", 0)
                turn_summary["tokens"] = tokens
                if turn_summary["duration_seconds"] > 0:
                    turn_summary["throughput"] = tokens / turn_summary["duration_seconds"]
            
            summary.append(turn_summary)
        
        self.summary_data["conversation_summary"] = summary
    
    def _calculate_energy(self, timestamps, power_values):
        """计算能耗（梯形积分）"""
        if len(timestamps) < 2 or len(power_values) < 2:
            return 0
        
        energy = 0
        for i in range(len(timestamps) - 1):
            dt = timestamps[i+1] - timestamps[i]
            avg_power = (power_values[i] + power_values[i+1]) / 2
            energy += avg_power * dt
        
        return energy
    
    def set_metadata(self, **kwargs):
        """设置元数据"""
        self.raw_data["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "runner_version": "2.0",
            **kwargs
        }
        self.summary_data["metadata"] = {
            "timestamp": datetime.now().isoformat(),
            "analysis_version": "1.0",
            **kwargs
        }
    
    def get_raw_data(self):
        """获取原始数据"""
        return self.raw_data
    
    def get_summary_data(self):
        """获取汇总数据"""
        return self.summary_data


class ExperimentRunner:
    """实验运行器，支持Ollama和Hugging Face模型"""
    
    def __init__(self, output_dir="./results", skip_bartscore=False):
        """
        初始化实验运行器
        
        Args:
            output_dir (str): 结果输出目录
            skip_bartscore (bool): 是否跳过 BARTScore 评估
        """
        self.output_dir = output_dir
        self.skip_bartscore = skip_bartscore
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
        
        if skip_bartscore:
            print("[INFO] 跳过 BARTScore 评估器初始化（--skip-bartscore 已启用）")
            BARTSCORE_AVAILABLE = False
        elif not BARTSCORE_AVAILABLE:
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
            dict: 生成结果和性能数据，包含 TTFT、token 统计等
        """
        print(f"  --> 调用Ollama模型: {model_name}")
        
        import requests
        
        start_time = time.time()
        first_token_time = None
        
        try:
            request_data = {
                "model": model_name,
                "prompt": prompt,
                "stream": True,  # 启用流式以捕获首token时间
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
                stream=True,
                timeout=300
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API返回错误: {response.status_code} - {response.text}")
            
            # 流式接收响应
            generated_text = ""
            thinking_text = ""
            context_data = None
            final_result = {}
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    
                    # 记录首token时间
                    if chunk.get("response") and first_token_time is None:
                        first_token_time = time.time()
                    
                    # 累积生成的文本
                    if chunk.get("response"):
                        generated_text += chunk["response"]
                    
                    # 保存thinking字段（某些模型使用）
                    if chunk.get("thinking"):
                        thinking_text += chunk["thinking"]
                    
                    # 保存上下文和最终结果
                    if chunk.get("done"):
                        context_data = chunk.get("context")
                        final_result = chunk
                        break
            
            end_time = time.time()
            
            # 如果response为空但thinking有内容，使用thinking
            if not generated_text and thinking_text:
                generated_text = thinking_text
                print(f"  [INFO]  注意: 该模型将回复放在thinking字段中")
            
            # 统计token数
            # 方法1：使用API返回的精确值（如果有）
            output_tokens = final_result.get("eval_count", 0)
            prompt_tokens = final_result.get("prompt_eval_count", 0)
            
            # 方法2：如果API没有返回，使用简单估算
            if output_tokens == 0:
                output_tokens = len(generated_text.split())
            if prompt_tokens == 0:
                prompt_tokens = len(prompt.split())
            
            total_tokens = prompt_tokens + output_tokens
            
            # 计算TTFT和TPOT
            ttft = (first_token_time - start_time) if first_token_time else None
            total_time = end_time - start_time
            decode_time = (end_time - first_token_time) if first_token_time else total_time
            tpot = (decode_time / (output_tokens - 1)) if output_tokens > 1 else None
            
            return {
                "response": generated_text,
                "thinking": thinking_text,
                "total_time": total_time,
                "first_token_time": ttft,  # TTFT (Time To First Token)
                "decode_time": decode_time,  # Decode阶段时间
                "prompt_tokens": prompt_tokens,  # 输入token数
                "output_tokens": output_tokens,  # 输出token数
                "total_tokens": total_tokens,  # 总token数
                "token_count": output_tokens,  # 保持向后兼容
                "tpot": tpot,  # Time Per Output Token
                "success": True,
                "context": context_data,
                "metadata": final_result
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
            dict: 生成结果和性能数据，包含 TTFT、token 统计等
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
        
        # 统计输入token数
        prompt_tokens = len(tokenizer.encode(prompt))
        
        # 生成文本（使用流式生成以捕获首token时间）
        start_time = time.time()
        first_token_time = None
        
        try:
            # 使用 hf_loader 的流式生成方法
            generated_text = ""
            token_count = 0
            
            # 如果 hf_loader 支持流式生成
            if hasattr(self.hf_loader, 'generate_stream'):
                for token_text in self.hf_loader.generate_stream(
                    model,
                    tokenizer,
                    prompt,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True
                ):
                    if first_token_time is None:
                        first_token_time = time.time()
                    generated_text += token_text
                    token_count += 1
            else:
                # 回退到非流式生成
                generated_text = self.hf_loader.generate(
                    model,
                    tokenizer,
                    prompt,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True
                )
                # 无法获取首token时间
                first_token_time = None
            
            end_time = time.time()
            
            # 精确统计输出token数
            output_tokens = len(tokenizer.encode(generated_text))
            total_tokens = prompt_tokens + output_tokens
            
            # 计算TTFT和TPOT
            total_time = end_time - start_time
            ttft = (first_token_time - start_time) if first_token_time else None
            decode_time = (end_time - first_token_time) if first_token_time else total_time
            tpot = (decode_time / (output_tokens - 1)) if output_tokens > 1 else None
            
            return {
                "response": generated_text,
                "total_time": total_time,
                "first_token_time": ttft,  # TTFT (Time To First Token)
                "decode_time": decode_time,  # Decode阶段时间
                "prompt_tokens": prompt_tokens,  # 输入token数
                "output_tokens": output_tokens,  # 输出token数
                "total_tokens": total_tokens,  # 总token数
                "token_count": output_tokens,  # 保持向后兼容
                "tpot": tpot,  # Time Per Output Token
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
            dict: 实验结果（包含整体监控数据和事件标记）
        """
        # 启动资源监控
        if MONITOR_AVAILABLE:
            monitor = ResourceMonitor(interval=0.2)
            monitor.start()
            monitor.mark_event("experiment_start", {"task_type": task_type})  # 标记实验开始
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
                
                # 标记推理开始
                if use_advanced_monitor:
                    monitor.mark_event("inference_start", {"turn": turn_idx})
                
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
                    
                    # 标记首token（如果有）
                    if use_advanced_monitor and response.get("first_token_time"):
                        # 计算首token的绝对时间
                        inference_start_time = monitor.events[-1]["timestamp"]
                        first_token_abs_time = inference_start_time + response["first_token_time"]
                        monitor.events.append({
                            "timestamp": first_token_abs_time,
                            "event": "first_token",
                            "metadata": {"turn": turn_idx}
                        })
                    
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
                    
                    # 标记首token（如果有）
                    if use_advanced_monitor and response.get("first_token_time"):
                        inference_start_time = monitor.events[-1]["timestamp"]
                        first_token_abs_time = inference_start_time + response["first_token_time"]
                        monitor.events.append({
                            "timestamp": first_token_abs_time,
                            "event": "first_token",
                            "metadata": {"turn": turn_idx}
                        })
                else:
                    raise Exception(f"未知的模型类型: {model_info['type']}")
                
                # 标记推理结束
                if use_advanced_monitor:
                    monitor.mark_event("inference_end", {"turn": turn_idx})
                
                all_responses.append(response["response"])
                total_time += response["total_time"]
                total_tokens += response.get("output_tokens", response.get("token_count", 0))
                
                print(f"  [OK] 生成完成 (耗时: {response['total_time']:.2f}秒, Tokens: {response.get('output_tokens', response.get('token_count', 0))})")
                if response.get("first_token_time"):
                    print(f"    TTFT: {response['first_token_time']*1000:.1f}ms, TPOT: {response.get('tpot', 0)*1000:.1f}ms")
                
        except Exception as e:
            print(f"  [ERROR] 生成文本失败: {e}")
            if use_advanced_monitor:
                monitor.mark_event("experiment_error", {"error": str(e)})
                monitor.stop()
            else:
                monitor_thread.join(timeout=1)
            return None
        
        # 停止资源监控
        resource_full = None
        if use_advanced_monitor:
            monitor.mark_event("experiment_end")  # 标记实验结束
            time.sleep(0.5)
            monitor.stop()
            resource_summary = monitor.summary()
            resource_full = monitor.to_dict()
            
            # 计算分阶段能耗（如果有事件标记）
            phase_analysis = {}
            if len(monitor.events) >= 2:
                # 分析每轮的 prefill 和 decode 阶段
                for turn_idx in range(1, len(prompts) + 1):
                    prefill_data = monitor.get_phase_data(
                        f"inference_start",
                        f"first_token"
                    )
                    decode_data = monitor.get_phase_data(
                        f"first_token",
                        f"inference_end"
                    )
                    if prefill_data or decode_data:
                        phase_analysis[f"turn_{turn_idx}"] = {
                            "prefill": prefill_data,
                            "decode": decode_data
                        }
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
                "summary": resource_summary,
                "events": [],  # 基础监控没有事件
                "phase_analysis": {}  # 基础监控没有分阶段分析
            }
            phase_analysis = {}
        
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
                "token_count": total_tokens,  # 输出token数（向后兼容）
                "output_tokens": total_tokens,  # 明确的输出token数
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
            "phase_analysis": phase_analysis,  # 新增：分阶段能耗分析
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
    
    def _run_with_overall_monitoring_v2(self, exp_result, model_info, prompts, 
                                        task_type, max_tokens, temperature, 
                                        top_p, keep_context):
        """
        整体监控模式：所有轮次使用同一个监控器（新版本，填充ExperimentResult对象）
        
        Args:
            exp_result (ExperimentResult): 实验结果对象
            model_info (dict): 模型信息
            prompts (list): 提示词列表
            task_type (str): 任务类型
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            top_p (float): Top-p采样
            keep_context (bool): 是否保持上下文
        """
        # 启动整体监控
        if not MONITOR_AVAILABLE:
            print(f"  [WARNING] 高级监控不可用，使用基础监控")
            # 基础监控模式下，无法提供完整的时间序列数据
            # 这里简化处理，仅记录对话内容
            context = None
            for i, prompt in enumerate(prompts, 1):
                print(f"\n  [轮次 {i}/{len(prompts)}]")
                start_time = time.time()
                
                if model_info["type"] == "ollama":
                    response = self.call_ollama_generate(
                        model_info["name"], prompt, max_tokens,
                        temperature, top_p, context=context if keep_context else None
                    )
                    if keep_context and "context" in response:
                        context = response["context"]
                elif model_info["type"] == "huggingface":
                    response = self.call_hf_generate(
                        model_info["path"], prompt, max_tokens,
                        temperature, top_p, model_info.get("quantize")
                    )
                else:
                    raise Exception(f"未知的模型类型: {model_info['type']}")
                
                end_time = time.time()
                
                # 添加对话轮次（无监控数据）
                exp_result.add_conversation_turn(
                    turn=i,
                    prompt=prompt,
                    response=response["response"],
                    start_time=start_time,
                    end_time=end_time,
                    turn_monitor=None
                )
                
                print(f"  [OK] 生成完成 (耗时: {response['total_time']:.2f}秒)")
            
            return
        
        # 高级监控模式
        monitor = ResourceMonitor(interval=0.2)
        monitor.start()
        monitor.mark_event("experiment_start", {"task_type": task_type})
        
        # 执行所有轮次
        context = None  # Ollama的对话上下文
        
        try:
            for i, prompt in enumerate(prompts, 1):
                print(f"\n  [轮次 {i}/{len(prompts)}]")
                print(f"  提示: {prompt[:50]}..." if len(prompt) > 50 else f"  提示: {prompt}")
                
                monitor.mark_event("inference_start", {"turn": i})
                start_time = time.time()
                
                # 调用模型
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
                    
                    # 标记首token（如果有）
                    if response.get("first_token_time"):
                        inference_start_time = monitor.events[-1]["timestamp"]
                        first_token_abs_time = inference_start_time + response["first_token_time"]
                        monitor.events.append({
                            "timestamp": first_token_abs_time,
                            "event": "first_token",
                            "metadata": {"turn": i}
                        })
                
                elif model_info["type"] == "huggingface":
                    response = self.call_hf_generate(
                        model_info["path"],
                        prompt,
                        max_tokens,
                        temperature,
                        top_p,
                        model_info.get("quantize")
                    )
                    
                    # 标记首token（如果有）
                    if response.get("first_token_time"):
                        inference_start_time = monitor.events[-1]["timestamp"]
                        first_token_abs_time = inference_start_time + response["first_token_time"]
                        monitor.events.append({
                            "timestamp": first_token_abs_time,
                            "event": "first_token",
                            "metadata": {"turn": i}
                        })
                else:
                    raise Exception(f"未知的模型类型: {model_info['type']}")
                
                end_time = time.time()
                monitor.mark_event("inference_end", {
                    "turn": i,
                    "tokens": response.get("output_tokens", response.get("token_count", 0))
                })
                
                # 添加对话轮次到exp_result
                exp_result.add_conversation_turn(
                    turn=i,
                    prompt=prompt,
                    response=response["response"],
                    start_time=start_time,
                    end_time=end_time,
                    turn_monitor=None  # 整体监控模式不传递turn_monitor
                )
                
                print(f"  [OK] 生成完成 (耗时: {response['total_time']:.2f}秒, Tokens: {response.get('output_tokens', response.get('token_count', 0))})")
                if response.get("first_token_time"):
                    print(f"    TTFT: {response['first_token_time']*1000:.1f}ms, TPOT: {response.get('tpot', 0)*1000:.1f}ms")
        
        except Exception as e:
            print(f"  [ERROR] 生成文本失败: {e}")
            monitor.mark_event("experiment_error", {"error": str(e)})
            monitor.stop()
            raise
        
        # 停止监控
        monitor.mark_event("experiment_end")
        time.sleep(0.5)
        monitor.stop()
        
        # 设置监控数据到exp_result
        exp_result.set_monitoring_data(monitor)
    
    def _run_with_per_turn_monitoring_v2(self, exp_result, model_info, prompts,
                                         task_type, max_tokens, temperature,
                                         top_p, keep_context):
        """
        分轮监控模式：每轮对话使用独立的监控器（新版本，填充ExperimentResult对象）
        
        Args:
            exp_result (ExperimentResult): 实验结果对象
            model_info (dict): 模型信息
            prompts (list): 提示词列表
            task_type (str): 任务类型
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            top_p (float): Top-p采样
            keep_context (bool): 是否保持上下文
        """
        if not MONITOR_AVAILABLE:
            print(f"  [WARNING] 高级监控不可用，使用基础监控")
            # 基础监控模式下，无法提供分轮监控数据
            # 回退到整体监控模式
            self._run_with_overall_monitoring_v2(
                exp_result, model_info, prompts, task_type,
                max_tokens, temperature, top_p, keep_context
            )
            return
        
        # 创建全局监控器（用于记录整体时间和事件）
        global_monitor = ResourceMonitor(interval=0.2)
        global_monitor.start()
        global_monitor.mark_event("experiment_start", {"task_type": task_type})
        
        context = None  # Ollama的对话上下文
        
        try:
            for i, prompt in enumerate(prompts, 1):
                print(f"\n  [轮次 {i}/{len(prompts)}]")
                print(f"  提示: {prompt[:50]}..." if len(prompt) > 50 else f"  提示: {prompt}")
                
                # 为该轮创建独立监控器
                turn_monitor = ResourceMonitor(interval=0.2)
                turn_monitor.start()
                turn_monitor.mark_event("inference_start", {"turn": i})
                
                start_time = time.time()
                
                # 调用模型
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
                    
                    # 标记首token（如果有）
                    if response.get("first_token_time"):
                        inference_start_time = turn_monitor.events[-1]["timestamp"]
                        first_token_abs_time = inference_start_time + response["first_token_time"]
                        turn_monitor.events.append({
                            "timestamp": first_token_abs_time,
                            "event": "first_token",
                            "metadata": {"turn": i}
                        })
                
                elif model_info["type"] == "huggingface":
                    response = self.call_hf_generate(
                        model_info["path"],
                        prompt,
                        max_tokens,
                        temperature,
                        top_p,
                        model_info.get("quantize")
                    )
                    
                    # 标记首token（如果有）
                    if response.get("first_token_time"):
                        inference_start_time = turn_monitor.events[-1]["timestamp"]
                        first_token_abs_time = inference_start_time + response["first_token_time"]
                        turn_monitor.events.append({
                            "timestamp": first_token_abs_time,
                            "event": "first_token",
                            "metadata": {"turn": i}
                        })
                else:
                    raise Exception(f"未知的模型类型: {model_info['type']}")
                
                end_time = time.time()
                
                # 停止该轮监控
                turn_monitor.mark_event("inference_end", {
                    "turn": i,
                    "tokens": response.get("output_tokens", response.get("token_count", 0))
                })
                time.sleep(0.3)
                turn_monitor.stop()
                
                # 同时在全局监控器中记录事件
                global_monitor.mark_event("inference_end", {
                    "turn": i,
                    "tokens": response.get("output_tokens", response.get("token_count", 0))
                })
                
                # 添加对话轮次到exp_result（包含该轮的监控数据）
                exp_result.add_conversation_turn(
                    turn=i,
                    prompt=prompt,
                    response=response["response"],
                    start_time=start_time,
                    end_time=end_time,
                    turn_monitor=turn_monitor  # 传递该轮的监控器
                )
                
                print(f"  [OK] 生成完成 (耗时: {response['total_time']:.2f}秒, Tokens: {response.get('output_tokens', response.get('token_count', 0))})")
                if response.get("first_token_time"):
                    print(f"    TTFT: {response['first_token_time']*1000:.1f}ms, TPOT: {response.get('tpot', 0)*1000:.1f}ms")
        
        except Exception as e:
            print(f"  [ERROR] 生成文本失败: {e}")
            global_monitor.mark_event("experiment_error", {"error": str(e)})
            global_monitor.stop()
            raise
        
        # 停止全局监控
        global_monitor.mark_event("experiment_end")
        time.sleep(0.5)
        global_monitor.stop()
        
        # 设置全局监控数据到exp_result
        exp_result.set_monitoring_data(global_monitor)
    
    def measure_idle_baseline(self, duration=10):
        """
        测量系统空闲状态的基线功耗
        
        Args:
            duration (int): 测量持续时间（秒）
            
        Returns:
            dict: 空闲基线数据，包含平均功耗、CPU利用率等
        """
        if not MONITOR_AVAILABLE:
            print(f"  [WARNING] 高级监控不可用，跳过空闲基线测量")
            return None
        
        print(f"  --> 测量空闲基线功耗 (持续 {duration} 秒)...")
        print(f"      请保持系统空闲，不要运行其他程序...")
        
        # 启动监控
        monitor = ResourceMonitor(interval=0.2)
        monitor.start()
        monitor.mark_event("baseline_start")
        
        # 等待指定时间
        time.sleep(duration)
        
        # 停止监控
        monitor.mark_event("baseline_end")
        time.sleep(0.5)
        monitor.stop()
        
        # 获取基线数据
        baseline_data = monitor.get_phase_data("baseline_start", "baseline_end")
        summary = monitor.summary()
        
        if baseline_data:
            baseline_result = {
                "duration_seconds": duration,
                "gpu_power_avg_w": baseline_data["gpu_power_avg_w"],
                "gpu_power_peak_w": baseline_data["gpu_power_peak_w"],
                "gpu_energy_j": baseline_data["gpu_energy_j"],
                "cpu_percent_avg": summary["cpu_percent_avg"],
                "gpu_util_avg": summary["gpu_util_avg"],
                "gpu_mem_peak_mb": summary["gpu_mem_peak_mb"],
                "timestamp": time.time()
            }
            
            print(f"  [OK] 空闲基线测量完成")
            print(f"      平均GPU功耗: {baseline_result['gpu_power_avg_w']:.2f} W")
            print(f"      平均CPU利用率: {baseline_result['cpu_percent_avg']:.1f}%")
            print(f"      平均GPU利用率: {baseline_result['gpu_util_avg']:.1f}%")
            
            return baseline_result
        else:
            print(f"  [WARNING] 无法获取空闲基线数据")
            return None
    
    def measure_idle_baseline_v2(self, duration=10):
        """
        测量空闲基线，返回ResourceMonitor对象
        
        Args:
            duration (int): 测量持续时间（秒）
            
        Returns:
            ResourceMonitor: 监控器对象（包含完整时间序列数据）
        """
        if not MONITOR_AVAILABLE:
            print(f"  [WARNING] 高级监控不可用，跳过空闲基线测量")
            return None
        
        print(f"  --> 测量空闲基线功耗 (持续 {duration} 秒)...")
        print(f"      请保持系统空闲，不要运行其他程序...")
        
        # 启动监控
        monitor = ResourceMonitor(interval=0.2)
        monitor.start()
        monitor.mark_event("baseline_start")
        
        # 等待指定时间
        time.sleep(duration)
        
        # 停止监控
        monitor.mark_event("baseline_end")
        time.sleep(0.5)
        monitor.stop()
        
        # 打印基线信息
        summary = monitor.summary()
        print(f"  [OK] 空闲基线测量完成")
        print(f"      平均GPU功耗: {summary['gpu_power_avg_w']:.2f} W")
        print(f"      平均CPU利用率: {summary['cpu_percent_avg']:.1f}%")
        
        return monitor
    
    def _print_experiment_results(self, exp_result):
        """打印实验结果摘要"""
        performance = exp_result.summary_data["performance"]
        resources = exp_result.summary_data["resources"]
        derived = exp_result.summary_data["derived_metrics"]
        
        print(f"  [OK] 实验完成")
        print(f"    - 对话轮数: {performance.get('turns', 0)}")
        print(f"    - 总生成时间: {performance.get('total_time_seconds', 0):.2f}秒")
        print(f"    - 总Token数: {performance.get('output_tokens', 0)}")
        print(f"    - 吞吐量: {performance.get('throughput_tokens_per_sec', 0):.2f} tokens/s")
        if resources.get("gpu_energy_j", 0) > 0:
            print(f"    - GPU能耗: {resources['gpu_energy_j']:.2f} J")
        
        if derived:
            print(f"\n  [增量指标]")
            if "P_idle" in derived:
                print(f"    空闲功耗 (P_idle): {derived['P_idle']:.2f} W")
            if "P_inc" in derived:
                print(f"    增量功耗 (P_inc): {derived['P_inc']:.2f} W")
            if "E_inc" in derived:
                print(f"    增量能耗 (E_inc): {derived['E_inc']:.2f} J")
            if "E_token" in derived:
                print(f"    每token能耗 (E_token): {derived['E_token']:.4f} J/token")
            if "PPW" in derived:
                print(f"    每瓦性能 (PPW): {derived['PPW']:.2f} tokens/s/W")
            if "TPJ" in derived:
                print(f"    能效比 (TPJ): {derived['TPJ']:.2f} tokens/J")
    
    def run_single_experiment(self, model, prompts, task_type, reference_text=None, 
                            max_tokens=500, temperature=0.7, top_p=0.9, 
                            keep_context=False, per_turn_monitoring=False,
                            idle_measurement_duration=0):
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
            idle_measurement_duration (int): 空闲基线测量时间（秒），0表示不测量（默认0）
            
        Returns:
            ExperimentResult: 实验结果对象
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
        if idle_measurement_duration > 0:
            print(f"  空闲基线测量: {idle_measurement_duration} 秒")
        print(f"{'='*60}")
        
        # 1. 创建ExperimentResult对象
        experiment_id = f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(self)}"
        exp_result = ExperimentResult(experiment_id)
        
        # 2. 设置配置
        exp_result.set_config(
            model=model_info["display_name"],
            model_info=model_info,
            prompts=prompts,
            task_type=task_type,
            keep_context=keep_context,
            per_turn_monitoring=per_turn_monitoring,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            reference_text=reference_text
        )
        
        # 3. 测量空闲基线（返回monitor对象而非汇总数据）
        baseline_monitor = None
        if idle_measurement_duration > 0:
            baseline_monitor = self.measure_idle_baseline_v2(idle_measurement_duration)
            exp_result.set_baseline_raw(baseline_monitor)
        
        # 4. 根据per_turn_monitoring选择执行方式
        if per_turn_monitoring and len(prompts) > 1:
            self._run_with_per_turn_monitoring_v2(
                exp_result, model_info, prompts, task_type,
                max_tokens, temperature, top_p, keep_context
            )
        else:
            self._run_with_overall_monitoring_v2(
                exp_result, model_info, prompts, task_type,
                max_tokens, temperature, top_p, keep_context
            )
        
        # 5. 设置元数据
        exp_result.set_metadata(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        
        # 6. 计算汇总数据
        exp_result.calculate_summary(bart_scorer=self.bart_scorer)
        
        # 7. 打印结果
        self._print_experiment_results(exp_result)
        
        return exp_result
        
    
    def run_experiment_suite(self, test_cases, output_file=None):
        """
        运行完整的实验套件
        
        Args:
            test_cases (list): 测试用例列表
            output_file (str, optional): 输出文件基础路径（不含_raw或_summary后缀）
            
        Returns:
            tuple: (raw_results, summary_results)
        """
        # 确定输出文件路径
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_base = os.path.join(self.output_dir, f"experiment_results_{timestamp}")
        else:
            # 移除可能存在的_raw或_summary后缀
            output_base = output_file.replace("_raw", "").replace("_summary", "")
            if output_base.endswith(".json"):
                output_base = output_base[:-5]
        
        raw_file = f"{output_base}_raw.json"
        summary_file = f"{output_base}_summary.json"
        
        raw_results = []
        summary_results = []
        
        print(f"\n{'='*70}")
        print(f"开始执行实验套件")
        print(f"  测试用例数: {len(test_cases)}")
        print(f"  原始数据: {raw_file}")
        print(f"  汇总数据: {summary_file}")
        print(f"{'='*70}\n")
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}] 运行实验")
            
            # 兼容性处理：支持 "prompt" 或 "prompts"
            prompts = case.get("prompts", case.get("prompt"))
            if prompts is None:
                print(f"  [ERROR] 测试用例缺少 'prompts' 或 'prompt' 字段")
                continue
            
            try:
                # 运行实验（返回ExperimentResult对象）
                exp_result = self.run_single_experiment(
                    model=case["model"],
                    prompts=prompts,
                    task_type=case["task_type"],
                    reference_text=case.get("reference_text"),
                    max_tokens=case.get("max_tokens", 500),
                    temperature=case.get("temperature", 0.7),
                    top_p=case.get("top_p", 0.9),
                    keep_context=case.get("keep_context", False),
                    per_turn_monitoring=case.get("per_turn_monitoring", False),
                    idle_measurement_duration=case.get("idle_measurement_duration", 0)
                )
                
                if exp_result:
                    # 获取raw和summary数据
                    raw_results.append(exp_result.get_raw_data())
                    summary_results.append(exp_result.get_summary_data())
                    
                    # 实时保存两个文件
                    with open(raw_file, "w", encoding="utf-8") as f:
                        json.dump(raw_results, f, ensure_ascii=False, indent=2)
                    
                    with open(summary_file, "w", encoding="utf-8") as f:
                        json.dump(summary_results, f, ensure_ascii=False, indent=2)
                    
                    print(f"  [OK] 结果已保存")
                else:
                    print(f"  [ERROR] 实验失败")
            
            except Exception as e:
                print(f"  [ERROR] 实验执行失败: {e}")
                import traceback
                traceback.print_exc()
                print(f"  [INFO] 继续执行下一个测试用例...")
            
            # 短暂延迟，避免资源竞争
            if i < len(test_cases):
                time.sleep(2)
        
        print(f"\n{'='*70}")
        print(f"所有实验完成")
        print(f"  成功: {len(raw_results)}/{len(test_cases)}")
        print(f"  原始数据: {raw_file}")
        print(f"  汇总数据: {summary_file}")
        print(f"{'='*70}\n")
        
        return raw_results, summary_results
    
    
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
    parser.add_argument("--skip-bartscore", action="store_true", help="跳过 BARTScore 质量评估（仅收集效率指标）")
    
    args = parser.parse_args()
    
    # 初始化实验运行器
    runner = ExperimentRunner(output_dir=args.output_dir, skip_bartscore=args.skip_bartscore)
    
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

