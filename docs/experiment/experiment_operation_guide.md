# GenAI模型能效评级体系实验操作指南

## 🎯 实验目的与目标

本实验旨在围绕"效率"和"质量"两大核心维度，设计可控实验，量化不同模型在不同任务下的表现，从而计算和比较其"效质比"，为构建GenAI模型能效评级体系奠定实证基础。

### 核心目标
- 收集模型在不同任务下的硬件资源消耗数据
- 测量模型的生成性能指标
- 评估模型生成内容的质量
- 记录模型配置信息以分析其对性能的影响

## 📊 数据收集维度与指标

### 1. 硬件资源消耗
| 指标 | 测量工具/方法 | 与研究目标的关联 |
|------|---------------|------------------|
| CPU/GPU利用率 | `nvtop` (GPU), `htop`, `psutil`库 | 核心"效率"指标，直接反映模型运行成本 |
| 内存占用 | 系统监控命令 | |
| 显存占用 | `nvtop` | |
| 功耗（若可测） | 专用功耗监测设备 | |
| 磁盘I/O | 系统监控命令 | |

### 2. 生成性能
| 指标 | 测量工具/方法 | 与研究目标的关联 |
|------|---------------|------------------|
| 吞吐量 (tokens/秒) | 自定义脚本计时 | 衡量模型"速度"，用户体验和商业部署关键 |
| 响应延迟 (首token时间) | Ollama API响应日志 | |
| 总生成时间 | 自定义脚本计时 | |
| 总推理时间 | Ollama API响应日志 | |

### 3. 生成质量
| 指标 | 测量工具/方法 | 与研究目标的关联 |
|------|---------------|------------------|
| 事实性、相关性、流畅性 | BARTScore评估 | 核心"质量"指标，评估模型能力根本 |
| 特定任务指标 (如代码正确率) | 自定义评估函数 | |
| 输出多样性 | 人工抽检 | |

### 4. 模型配置信息
| 信息 | 获取方式 | 与研究目标的关联 |
|------|----------|------------------|
| 模型名称 | 实验记录 | 分析不同配置对效质比的影响 |
| 参数量 | 实验记录 | |
| 上下文长度 | 实验记录 | |
| 量化精度 | 实验记录 | |
| Ollama版本 | 实验记录 | |

## 🧪 试验设计：对照与变量

### 1. 代表性模型选择
- **变量组**：选择2-3个不同系列、不同参数量的模型进行对比
  - 推荐模型组合示例：
    - `llama3.2:3b` vs `llama3.2:11b` vs `gemma2:9b`
    - `phi3:3.8b` vs `mistral:7b` vs `mixtral:8x7b`

### 2. 多样化测试任务设计
#### 任务类型（覆盖研究关注领域）
- **知识问答**：测试事实性与信息性
- **文本摘要**：测试连贯性与覆盖度
- **代码生成**：测试逻辑正确性
- **创意写作**：测试流畅性与多样性

#### 任务负载
- **短输入/输出**：约50-100 tokens
- **中输入/输出**：约200-500 tokens
- **长输入/输出**：约1000+ tokens

### 3. 标准化测试环境与流程
- 每次测试前重启Ollama服务，清空GPU缓存，确保环境一致
- 每个测试用例（模型+任务）运行多次（如5次），取平均值以减少随机误差
- 控制变量：在相同硬件、相同Prompt、相同生成参数（温度、最大token数）下测试

## ⚙️ 数据收集方法：构建自动化管道

### 主控Python脚本逻辑示例

```python
# experiment_runner.py
import subprocess
import time
import json
import psutil
import threading
from datetime import datetime
from bart_score import BARTScorer

class ExperimentRunner:
    def __init__(self):
        # 初始化BARTScore评估器
        self.bart_scorer = BARTScorer(device='cuda:0', checkpoint='facebook/bart-large-cnn')
        
    def restart_ollama_service(self):
        """重启Ollama服务以确保环境一致性"""
        subprocess.run(["net", "stop", "ollama"], shell=True)
        time.sleep(2)
        subprocess.run(["net", "start", "ollama"], shell=True)
        time.sleep(5)  # 等待服务完全启动
        
    def call_ollama_generate(self, model, prompt, max_tokens=500, temperature=0.7):
        """调用Ollama API生成文本"""
        cmd = [
            "ollama", "run", model,
            f"--max-tokens={max_tokens}",
            f"--temperature={temperature}",
            prompt
        ]
        
        start_time = time.time()
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        if process.returncode != 0:
            raise Exception(f"Ollama调用失败: {stderr}")
            
        return {
            "response": stdout.strip(),
            "total_time": end_time - start_time,
            "first_token_time": None  # 如需精确测量，需要更复杂的方法
        }
    
    def monitor_resources(self, duration):
        """监控系统资源使用情况"""
        resource_data = {
            "cpu_percent": [],
            "memory_percent": [],
            "gpu_utilization": [],  # 需要使用nvidia-ml-py库
            "gpu_memory_used": []
        }
        
        def collect():
            for _ in range(int(duration * 10)):  # 每0.1秒采样一次
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory_percent = psutil.virtual_memory().percent
                resource_data["cpu_percent"].append(cpu_percent)
                resource_data["memory_percent"].append(memory_percent)
                
                # GPU监控需要额外库支持
                # 示例使用nvidia-ml-py
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    
                    resource_data["gpu_utilization"].append(util.gpu)
                    resource_data["gpu_memory_used"].append(mem_info.used / 1024 / 1024)  # MB
                except:
                    pass
                    
                time.sleep(0.1)
        
        monitor_thread = threading.Thread(target=collect)
        monitor_thread.start()
        return resource_data, monitor_thread
    
    def evaluate_quality(self, generated_text, reference_text=None):
        """使用BARTScore评估生成质量"""
        if reference_text:
            # 有参考文本时的评估
            scores = self.bart_scorer.score([reference_text], [generated_text])
            return {
                "bartscore": scores[0],
                "has_reference": True
            }
        else:
            # 无参考文本时的评估（使用模型自评估）
            # 这里可以实现其他评估方法
            return {
                "generated_text_length": len(generated_text),
                "has_reference": False
            }
    
    def run_single_experiment(self, model, prompt, task_type, reference_text=None):
        """运行单次实验"""
        print(f"开始实验: 模型={model}, 任务类型={task_type}")
        
        # 重启Ollama服务
        self.restart_ollama_service()
        
        # 开始资源监控
        resource_data, monitor_thread = self.monitor_resources(30)  # 预估30秒完成
        
        # 生成文本
        try:
            response = self.call_ollama_generate(model, prompt)
        except Exception as e:
            print(f"生成文本失败: {e}")
            return None
            
        # 等待资源监控完成
        monitor_thread.join()
        
        # 评估质量
        quality_scores = self.evaluate_quality(response["response"], reference_text)
        
        # 计算性能指标
        gen_text = response["response"]
        total_time = response["total_time"]
        token_count = len(gen_text.split())  # 简易token计数
        
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
                "avg_cpu_percent": sum(resource_data["cpu_percent"]) / len(resource_data["cpu_percent"]),
                "max_cpu_percent": max(resource_data["cpu_percent"]),
                "avg_memory_percent": sum(resource_data["memory_percent"]) / len(resource_data["memory_percent"]),
                "max_memory_percent": max(resource_data["memory_percent"]),
                "avg_gpu_utilization": sum(resource_data["gpu_utilization"]) / len(resource_data["gpu_utilization"]) if resource_data["gpu_utilization"] else 0,
                "max_gpu_utilization": max(resource_data["gpu_utilization"]) if resource_data["gpu_utilization"] else 0,
                "avg_gpu_memory_mb": sum(resource_data["gpu_memory_used"]) / len(resource_data["gpu_memory_used"]) if resource_data["gpu_memory_used"] else 0,
                "max_gpu_memory_mb": max(resource_data["gpu_memory_used"]) if resource_data["gpu_memory_used"] else 0
            },
            "quality": quality_scores,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "ollama_version": subprocess.check_output(["ollama", "--version"]).decode().strip()
            }
        }
        
        return result
    
    def run_experiment_suite(self, test_cases, output_file="experiment_results.json"):
        """运行完整的实验套件"""
        results = []
        
        for i, case in enumerate(test_cases):
            print(f"运行实验 {i+1}/{len(test_cases)}")
            
            result = self.run_single_experiment(
                model=case["model"],
                prompt=case["prompt"],
                task_type=case["task_type"],
                reference_text=case.get("reference_text")
            )
            
            if result:
                results.append(result)
                
                # 实时保存结果
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                print(f"实验完成，结果已保存到 {output_file}")
            else:
                print(f"实验失败: {case}")
        
        return results

# 定义测试套件
test_cases = [
    {
        "model": "llama3.2:3b",
        "prompt": "请解释牛顿第一定律。",
        "task_type": "knowledge_qa",
        "reference_text": "牛顿第一定律，也称为惯性定律，指出：一个物体如果不受外力作用，或者所受合外力为零，那么静止的物体会保持静止状态，运动的物体会保持匀速直线运动状态。"
    },
    {
        "model": "llama3.2:11b",
        "prompt": "请解释牛顿第一定律。",
        "task_type": "knowledge_qa",
        "reference_text": "牛顿第一定律，也称为惯性定律，指出：一个物体如果不受外力作用，或者所受合外力为零，那么静止的物体会保持静止状态，运动的物体会保持匀速直线运动状态。"
    },
    # 可继续添加更多测试用例...
]

# 运行实验
if __name__ == "__main__":
    runner = ExperimentRunner()
    results = runner.run_experiment_suite(test_cases)
    print(f"所有实验完成，共获得 {len(results)} 条结果")
```

## 🔧 实验操作步骤

### 1. 环境准备
1. 确认已安装并配置好以下组件：
   - Ollama服务及所需模型
   - BARTScore的conda环境
   - Python依赖库 (`pip install psutil pynvml`)
   - NVIDIA驱动及nvidia-ml-py库（用于GPU监控）

2. 采集项目目录结构快照（Windows）：
   - 在PowerShell执行：`tree /F /A f:\all_proj\GenAI_power_analize | Select-Object -First 300`
   - 如需完整保存：`tree /F /A f:\all_proj\GenAI_power_analize > f:\all_proj\GenAI_power_analize\docs\project_tree.txt`

2. 验证各组件是否正常工作：
   ```bash
   # 检查Ollama版本
   ollama --version
   
   # 检查可用模型
   ollama list
   
   # 测试模型运行
   ollama run llama3.2:3b "Hello, how are you?"
   ```

3. 通过指定conda路径执行Python（非交互方式）：
   - `E:\ananconda\Scripts\conda.exe run -n bartscore python -V`
   - 安装依赖：`E:\ananconda\Scripts\conda.exe run -n bartscore pip install psutil pynvml requests tqdm`

### 2. 实验配置
1. 根据研究需求调整`test_cases`变量，定义要测试的模型、任务和参考文本
2. 修改脚本中的超参数（如max_tokens, temperature等）
3. 设置输出文件路径

### 3. 执行实验
1. 运行主控脚本：
   ```bash
   # 方案一：使用现有脚本
   python experiment_runner.py
   
   # 方案二：使用HTTP API采集更精确时延与吞吐
   E:\ananconda\Scripts\conda.exe run -n bartscore python experiments\run_experiments.py --models llama3.2:3b llama3.2:11b gemma2:9b --runs 5 --out data --max_tokens 512 --temperature 0.7
   ```

2. 脚本将自动：
   - 依次测试每个模型和任务组合
   - 重启Ollama服务以保证环境一致性
   - 监控系统资源使用情况
   - 记录性能和质量数据
   - 实时保存实验结果

3. 输出目录结构：
   - 原始数据：`data/raw/<date>/<model>/<task_load_run>.json`
   - 文本归档：`data/texts/<date>/<model>/<task_load_run>.txt`
   - 汇总表：`data/summary/<date>/results.csv`

### 4. 数据收集
1. 实验结果将保存为JSON格式文件
2. 每个实验包含以下信息：
   - 模型配置信息
   - 性能指标（吞吐量、延迟等）
   - 资源消耗数据（CPU、GPU、内存等）
   - 质量评估分数
   - 时间戳和元数据

## ⚠️ 注意事项

1. **权限要求**：脚本需要管理员权限以重启Ollama服务
2. **GPU监控**：需要NVIDIA GPU及相关驱动才能获取GPU使用数据
3. **稳定性**：长时间运行可能因系统资源不足或模型崩溃而中断，建议分批运行
4. **数据存储**：大量实验会产生较多数据，注意磁盘空间
5. **网络连接**：首次运行新模型时需要下载，确保网络连接稳定
6. **重复性**：为保证实验可重复，所有环境配置和参数应详细记录

## 📈 后续步骤

1. 收集足够的实验数据后，可进行"效质比"计算和模型比较
2. 分析不同模型在不同任务类型下的表现差异
3. 探索模型参数量、量化精度等因素对性能的影响
4. 构建可视化图表以直观展示实验结果
5. 根据实验结果优化模型选择和部署策略
