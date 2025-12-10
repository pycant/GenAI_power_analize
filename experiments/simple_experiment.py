#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简化版实验脚本
用于绕过BARTScore问题，直接运行实验收集性能和资源数据
"""

import subprocess
import time
import json
import psutil
import threading
from datetime import datetime
import os

def call_ollama_generate(model, prompt, max_tokens=500, temperature=0.7):
    """
    调用Ollama API生成文本
    
    Args:
        model (str): 模型名称
        prompt (str): 输入提示
        max_tokens (int): 最大token数
        temperature (float): 温度参数
        
    Returns:
        dict: 生成结果和性能数据
    """
    print(f"正在调用模型 {model} 生成文本...")
    
    cmd = f'ollama run {model} --max-tokens={max_tokens} --temperature={temperature} "{prompt}"'
    
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        end_time = time.time()
        
        if result.returncode != 0:
            raise Exception(f"Ollama调用失败: {result.stderr}")
        
        return {
            "response": result.stdout.strip(),
            "total_time": end_time - start_time,
            "success": True
        }
    except subprocess.TimeoutExpired:
        end_time = time.time()
        raise Exception(f"Ollama调用超时 ({end_time - start_time:.2f}秒)")
    except Exception as e:
        end_time = time.time()
        raise Exception(f"Ollama调用异常: {str(e)} (耗时: {end_time - start_time:.2f}秒)")

def monitor_resources(duration):
    """
    监控系统资源使用情况
    
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
                # 如果GPU监控不可用，添加默认值
                if resource_data["gpu_utilization"]:  # 非空时才添加
                    resource_data["gpu_utilization"].append(0)
                    resource_data["gpu_memory_used"].append(0)
            
            time.sleep(0.5)
    
    monitor_thread = threading.Thread(target=collect)
    monitor_thread.start()
    return resource_data, monitor_thread

def run_single_experiment(model, prompt, task_type, max_tokens=500, temperature=0.7):
    """
    运行单次实验
    
    Args:
        model (str): 模型名称
        prompt (str): 输入提示
        task_type (str): 任务类型
        max_tokens (int): 最大token数
        temperature (float): 温度参数
        
    Returns:
        dict: 实验结果
    """
    print(f"\n开始实验: 模型={model}, 任务类型={task_type}")
    
    # 开始资源监控（预估30秒完成）
    resource_data, monitor_thread = monitor_resources(30)
    
    # 生成文本
    try:
        response = call_ollama_generate(model, prompt, max_tokens, temperature)
    except Exception as e:
        print(f"生成文本失败: {e}")
        # 确保资源监控线程结束
        monitor_thread.join(timeout=1)
        return None
        
    # 等待资源监控完成
    monitor_thread.join(timeout=1)
    
    # 计算性能指标
    gen_text = response["response"]
    total_time = response["total_time"]
    # 简单的token计数（实际应用中可能需要更精确的方法）
    token_count = len(gen_text.split())
    
    # 计算资源使用统计
    def safe_avg(lst):
        return sum(lst) / len(lst) if lst else 0
        
    def safe_max(lst):
        return max(lst) if lst else 0
    
    # 整理结果
    result = {
        "model": model,
        "prompt": prompt,
        "task_type": task_type,
        "generated_text": gen_text,
        "performance": {
            "total_time_seconds": total_time,
            "token_count": token_count,
            "throughput_tokens_per_sec": token_count / total_time if total_time > 0 else 0
        },
        "resources": {
            "avg_cpu_percent": safe_avg(resource_data["cpu_percent"]),
            "max_cpu_percent": safe_max(resource_data["cpu_percent"]),
            "avg_memory_percent": safe_avg(resource_data["memory_percent"]),
            "max_memory_percent": safe_max(resource_data["memory_percent"]),
            "avg_gpu_utilization": safe_avg(resource_data["gpu_utilization"]) if resource_data["gpu_utilization"] else 0,
            "max_gpu_utilization": safe_max(resource_data["gpu_utilization"]) if resource_data["gpu_utilization"] else 0,
            "avg_gpu_memory_mb": safe_avg(resource_data["gpu_memory_used"]) if resource_data["gpu_memory_used"] else 0,
            "max_gpu_memory_mb": safe_max(resource_data["gpu_memory_used"]) if resource_data["gpu_memory_used"] else 0
        },
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "max_tokens": max_tokens,
            "temperature": temperature
        }
    }
    
    print(f"实验完成: 模型={model}, 任务类型={task_type}")
    return result

def main():
    """主函数"""
    # 创建结果目录
    output_dir = "./results"
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义测试用例
    test_cases = [
        {
            "model": "deepseek-r1:8b",
            "prompt": "请解释牛顿第一定律。",
            "task_type": "knowledge_qa",
            "max_tokens": 200,
            "temperature": 0.7
        },
        {
            "model": "gemma3:4b",
            "prompt": "请解释牛顿第一定律。",
            "task_type": "knowledge_qa",
            "max_tokens": 200,
            "temperature": 0.7
        }
    ]
    
    results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"experiment_results_{timestamp}.json")
    
    print(f"开始执行实验，共 {len(test_cases)} 个测试用例")
    print(f"结果将保存到: {output_file}")
    
    for i, case in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"运行实验 {i+1}/{len(test_cases)}")
        print(f"{'='*50}")
        
        result = run_single_experiment(
            model=case["model"],
            prompt=case["prompt"],
            task_type=case["task_type"],
            max_tokens=case.get("max_tokens", 500),
            temperature=case.get("temperature", 0.7)
        )
        
        if result:
            results.append(result)
            
            # 实时保存结果
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"实验结果已保存到 {output_file}")
        else:
            print(f"实验失败: {case}")
    
    print(f"\n所有实验完成，共获得 {len(results)} 条有效结果")
    return results

if __name__ == "__main__":
    main()
