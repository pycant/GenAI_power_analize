#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GenAI模型能效评级体系实验执行脚本
此脚本用于自动化执行模型性能和质量评估实验
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

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # 尝试从conda环境导入BARTScore
    import sys
    import os
    # 添加conda环境路径
    conda_env_path = "E:\\ananconda\\Scripts\\conda.exe"
    if os.path.exists(conda_env_path):
        sys.path.append("E:\\ananconda\\lib\\site-packages")
    
    from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
    BARTSCORE_AVAILABLE = True
except ImportError:
    print("警告: BARTScore模块不可用，将跳过质量评估")
    BARTSCORE_AVAILABLE = False
except Exception as e:
    print(f"警告: BARTScore初始化时出错: {e}，将跳过质量评估")
    BARTSCORE_AVAILABLE = False

class ExperimentRunner:
    def __init__(self, output_dir="./results"):
        """
        初始化实验运行器
        
        Args:
            output_dir (str): 结果输出目录
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化BARTScore评估器（如果可用）
        self.bart_scorer = None
        if BARTSCORE_AVAILABLE:
            try:
                self.bart_scorer = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')
                print("BARTScore评估器初始化成功")
            except Exception as e:
                print(f"警告: BARTScore初始化失败: {e}")
                self.bart_scorer = None
    
    def check_ollama_service(self):
        """检查Ollama服务是否运行"""
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"Ollama版本: {result.stdout.strip()}")
                return True
            else:
                print("Ollama服务未运行或不可访问")
                return False
        except Exception as e:
            print(f"检查Ollama服务时出错: {e}")
            return False
    
    def restart_ollama_service(self):
        """重启Ollama服务以确保环境一致性"""
        print("正在重启Ollama服务...")
        try:
            # 停止服务
            subprocess.run(["net", "stop", "ollama"], 
                          shell=True, capture_output=True)
            time.sleep(2)
            
            # 启动服务
            subprocess.run(["net", "start", "ollama"], 
                          shell=True, capture_output=True)
            time.sleep(5)  # 等待服务完全启动
            
            print("Ollama服务重启完成")
            return True
        except Exception as e:
            print(f"重启Ollama服务时出错: {e}")
            return False
    
    def call_ollama_generate(self, model, prompt, max_tokens=500, temperature=0.7):
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
    
    def monitor_resources(self, duration):
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
                # 有参考文本时的评估
                scores = self.bart_scorer.score([reference_text], [generated_text])
                return {
                    "bartscore": scores[0],
                    "has_reference": True
                }
            else:
                # 无参考文本时的基本评估
                return {
                    "bartscore": None,
                    "generated_text_length": len(generated_text),
                    "has_reference": False
                }
        except Exception as e:
            print(f"质量评估时出错: {e}")
            return {
                "bartscore": None,
                "error": str(e),
                "has_reference": reference_text is not None
            }
    
    def run_single_experiment(self, model, prompt, task_type, reference_text=None, 
                            max_tokens=500, temperature=0.7):
        """
        运行单次实验
        
        Args:
            model (str): 模型名称
            prompt (str): 输入提示
            task_type (str): 任务类型
            reference_text (str, optional): 参考文本
            max_tokens (int): 最大token数
            temperature (float): 温度参数
            
        Returns:
            dict: 实验结果
        """
        print(f"\n开始实验: 模型={model}, 任务类型={task_type}")
        
        # 重启Ollama服务（可选，根据需要启用）
        # self.restart_ollama_service()
        
        # 开始资源监控（预估30秒完成）
        resource_data, monitor_thread = self.monitor_resources(30)
        
        # 生成文本
        try:
            response = self.call_ollama_generate(
                model, prompt, max_tokens, temperature)
        except Exception as e:
            print(f"生成文本失败: {e}")
            # 确保资源监控线程结束
            monitor_thread.join(timeout=1)
            return None
            
        # 等待资源监控完成
        monitor_thread.join(timeout=1)
        
        # 评估质量
        quality_scores = self.evaluate_quality(response["response"], reference_text)
        
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
            "quality": quality_scores,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        }
        
        print(f"实验完成: 模型={model}, 任务类型={task_type}")
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
            output_file = os.path.join(self.output_dir, f"experiment_results_{timestamp}.json")
        
        results = []
        
        print(f"开始执行实验套件，共 {len(test_cases)} 个测试用例")
        print(f"结果将保存到: {output_file}")
        
        for i, case in enumerate(test_cases):
            print(f"\n{'='*50}")
            print(f"运行实验 {i+1}/{len(test_cases)}")
            print(f"{'='*50}")
            
            result = self.run_single_experiment(
                model=case["model"],
                prompt=case["prompt"],
                task_type=case["task_type"],
                reference_text=case.get("reference_text"),
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

def create_sample_test_cases():
    """创建示例测试用例"""
    return [
        {
            "model": "llama3.2:3b",
            "prompt": "请解释牛顿第一定律。",
            "task_type": "knowledge_qa",
            "reference_text": "牛顿第一定律，也称为惯性定律，指出：一个物体如果不受外力作用，或者所受合外力为零，那么静止的物体会保持静止状态，运动的物体会保持匀速直线运动状态。",
            "max_tokens": 200,
            "temperature": 0.7
        },
        {
            "model": "llama3.2:11b",
            "prompt": "请解释牛顿第一定律。",
            "task_type": "knowledge_qa",
            "reference_text": "牛顿第一定律，也称为惯性定律，指出：一个物体如果不受外力作用，或者所受合外力为零，那么静止的物体会保持静止状态，运动的物体会保持匀速直线运动状态。",
            "max_tokens": 200,
            "temperature": 0.7
        },
        {
            "model": "gemma2:9b",
            "prompt": "写一篇关于人工智能对未来社会影响的短文。",
            "task_type": "creative_writing",
            "max_tokens": 300,
            "temperature": 0.8
        }
    ]

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GenAI模型能效评级体系实验执行脚本")
    parser.add_argument("--output-dir", default="./results", help="结果输出目录")
    parser.add_argument("--config", help="测试用例配置文件路径（JSON格式）")
    parser.add_argument("--sample", action="store_true", help="运行示例测试用例")
    
    args = parser.parse_args()
    
    # 初始化实验运行器
    runner = ExperimentRunner(output_dir=args.output_dir)
    
    # 检查Ollama服务
    if not runner.check_ollama_service():
        print("错误: Ollama服务不可用，请确保服务已启动")
        return 1
    
    # 确定测试用例
    test_cases = []
    if args.config:
        # 从配置文件加载测试用例
        try:
            with open(args.config, "r", encoding="utf-8") as f:
                test_cases = json.load(f)
            print(f"从配置文件加载了 {len(test_cases)} 个测试用例")
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            return 1
    elif args.sample:
        # 使用示例测试用例
        test_cases = create_sample_test_cases()
        print(f"使用 {len(test_cases)} 个示例测试用例")
    else:
        # 默认示例
        test_cases = create_sample_test_cases()[:1]  # 只运行第一个示例
        print("运行默认示例测试用例")
    
    # 运行实验
    try:
        results = runner.run_experiment_suite(test_cases)
        print(f"\n实验执行完成，共获得 {len(results)} 条结果")
        return 0
    except KeyboardInterrupt:
        print("\n实验被用户中断")
        return 1
    except Exception as e:
        print(f"\n实验执行过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
