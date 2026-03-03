# 数据结构重构实施方案

## 概述

本文档提供数据结构重构的具体实施步骤和代码修改指南。

## 核心修改点

### 1. 修改 experiment_runner.py

#### 1.1 新增数据结构类

```python
class ExperimentResult:
    """实验结果数据结构"""
    
    def __init__(self, experiment_id):
        self.experiment_id = experiment_id
        self.raw_data = {
            "experiment_id": experiment_id,
            "config": {},
            "baseline_raw": None,
            "conversation": [],
            "monitoring_data": {
                "measurements": {},
                "events": []
            },
            "metadata": {}
        }
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
            **kwargs
        }
        self.summary_data["config_ref"] = {
            "model": model,
            "task_type": task_type,
            "prompts_count": len(prompts) if isinstance(prompts, list) else 1,
            "keep_context": kwargs.get("keep_context", False)
        }
    
    def set_baseline_raw(self, baseline_data):
        """设置原始基线数据"""
        if not baseline_data:
            return
        
        self.raw_data["baseline_raw"] = {
            "duration_seconds": baseline_data["duration"],
            "start_timestamp": baseline_data["start_time"],
            "end_timestamp": baseline_data["end_time"],
            "measurements": baseline_data["measurements"]
        }
    
    def set_monitoring_data(self, monitoring_data):
        """设置监控数据"""
        self.raw_data["monitoring_data"] = monitoring_data
    
    def add_conversation_turn(self, turn, prompt, response, start_time, end_time):
        """添加对话轮次"""
        self.raw_data["conversation"].append({
            "turn": turn,
            "prompt": prompt,
            "response": response,
            "start_timestamp": start_time,
            "end_timestamp": end_time
        })
    
    def calculate_summary(self):
        """从原始数据计算汇总指标"""
        # 计算基线汇总
        if self.raw_data["baseline_raw"]:
            self._calculate_baseline_summary()
        
        # 计算性能指标
        self._calculate_performance_metrics()
        
        # 计算资源指标
        self._calculate_resource_metrics()
        
        # 计算派生指标
        self._calculate_derived_metrics()
        
        # 生成对话摘要
        self._generate_conversation_summary()
    
    def _calculate_baseline_summary(self):
        """计算基线汇总统计"""
        baseline_raw = self.raw_data["baseline_raw"]
        measurements = baseline_raw["measurements"]
        
        import numpy as np
        
        self.summary_data["baseline_summary"] = {
            "duration_seconds": baseline_raw["duration_seconds"],
            "gpu_power_avg_w": np.mean(measurements["gpu_power_w"]),
            "gpu_power_peak_w": np.max(measurements["gpu_power_w"]),
            "gpu_power_std_w": np.std(measurements["gpu_power_w"]),
            "gpu_energy_j": self._calculate_energy(
                measurements["timestamps"],
                measurements["gpu_power_w"]
            ),
            "cpu_percent_avg": np.mean(measurements["cpu_percent"]),
            "cpu_percent_peak": np.max(measurements["cpu_percent"]),
            "gpu_util_avg": np.mean(measurements["gpu_util"]),
            "gpu_util_peak": np.max(measurements["gpu_util"]),
            "gpu_mem_avg_mb": np.mean(measurements["gpu_mem_mb"]),
            "gpu_mem_peak_mb": np.max(measurements["gpu_mem_mb"]),
            "gpu_temp_avg_c": np.mean(measurements["gpu_temp_c"]),
            "gpu_temp_peak_c": np.max(measurements["gpu_temp_c"])
        }
    
    def _calculate_performance_metrics(self):
        """计算性能指标"""
        conversation = self.raw_data["conversation"]
        monitoring = self.raw_data["monitoring_data"]
        
        # 计算总时间
        start_time = monitoring["start_timestamp"]
        end_time = monitoring["end_timestamp"]
        total_time = end_time - start_time
        
        # 计算token数（需要从events中提取）
        total_tokens = sum(
            event["metadata"].get("tokens", 0)
            for event in monitoring["events"]
            if event["event"] == "inference_end"
        )
        
        # 计算TTFT（首个token时间）
        first_token_event = next(
            (e for e in monitoring["events"] if e["event"] == "first_token"),
            None
        )
        ttft = (first_token_event["timestamp"] - start_time) if first_token_event else None
        
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
        measurements = self.raw_data["monitoring_data"]["measurements"]
        
        import numpy as np
        
        # 计算GPU能耗
        gpu_energy = self._calculate_energy(
            measurements["timestamps"],
            measurements["gpu_power_w"]
        )
        
        # 估算CPU能耗（基于CPU使用率和TDP）
        cpu_tdp = 45  # 假设TDP为45W
        cpu_energy = self._calculate_energy(
            measurements["timestamps"],
            [cpu_tdp * (p / 100) for p in measurements["cpu_percent"]]
        )
        
        self.summary_data["resources"] = {
            "cpu_percent_avg": np.mean(measurements["cpu_percent"]),
            "cpu_percent_peak": np.max(measurements["cpu_percent"]),
            "cpu_percent_std": np.std(measurements["cpu_percent"]),
            "mem_used_avg_mb": np.mean(measurements["mem_used_mb"]),
            "mem_used_peak_mb": np.max(measurements["mem_used_mb"]),
            "gpu_util_avg": np.mean(measurements["gpu_util"]),
            "gpu_util_peak": np.max(measurements["gpu_util"]),
            "gpu_util_std": np.std(measurements["gpu_util"]),
            "gpu_mem_avg_mb": np.mean(measurements["gpu_mem_mb"]),
            "gpu_mem_peak_mb": np.max(measurements["gpu_mem_mb"]),
            "gpu_power_avg_w": np.mean(measurements["gpu_power_w"]),
            "gpu_power_peak_w": np.max(measurements["gpu_power_w"]),
            "gpu_power_std_w": np.std(measurements["gpu_power_w"]),
            "gpu_energy_j": gpu_energy,
            "gpu_temp_avg_c": np.mean(measurements["gpu_temp_c"]),
            "gpu_temp_peak_c": np.max(measurements["gpu_temp_c"]),
            "cpu_energy_j_approx": cpu_energy
        }
    
    def _calculate_derived_metrics(self):
        """计算派生指标"""
        baseline = self.summary_data.get("baseline_summary")
        resources = self.summary_data["resources"]
        performance = self.summary_data["performance"]
        
        derived = {}
        
        if baseline:
            # 增量功耗和能耗
            P_idle = baseline["gpu_power_avg_w"]
            P_avg = resources["gpu_power_avg_w"]
            E_total = resources["gpu_energy_j"]
            total_time = performance["total_time_seconds"]
            
            derived["P_idle"] = P_idle
            derived["P_inc"] = max(0, P_avg - P_idle)
            derived["E_inc"] = max(0, E_total - P_idle * total_time)
            
            # 每token能耗
            output_tokens = performance["output_tokens"]
            if output_tokens > 0 and derived["E_inc"] > 0:
                derived["E_token"] = derived["E_inc"] / output_tokens
            
            # 能效指标
            throughput = performance["throughput_tokens_per_sec"]
            if P_avg > 0:
                derived["PPW"] = throughput / P_avg
            if E_total > 0:
                derived["TPJ"] = output_tokens / E_total
            
            # 效率得分（归一化后的综合指标）
            # 这里简化处理，实际应该基于多个实验的归一化
            derived["efficiency_score"] = 0.5  # 占位符
            
            # 能效等级（A-F）
            tpj = derived.get("TPJ", 0)
            if tpj > 0.1:
                derived["energy_efficiency_class"] = "A"
            elif tpj > 0.08:
                derived["energy_efficiency_class"] = "B"
            elif tpj > 0.06:
                derived["energy_efficiency_class"] = "C"
            elif tpj > 0.04:
                derived["energy_efficiency_class"] = "D"
            else:
                derived["energy_efficiency_class"] = "E"
        
        self.summary_data["derived_metrics"] = derived
    
    def _generate_conversation_summary(self):
        """生成对话摘要"""
        conversation = self.raw_data["conversation"]
        
        summary = []
        for turn_data in conversation:
            turn_summary = {
                "turn": turn_data["turn"],
                "prompt_preview": turn_data["prompt"][:50] + "..." if len(turn_data["prompt"]) > 50 else turn_data["prompt"],
                "response_preview": turn_data["response"][:100] + "..." if len(turn_data["response"]) > 100 else turn_data["response"],
                "response_length": len(turn_data["response"]),
                "duration_seconds": turn_data["end_timestamp"] - turn_data["start_timestamp"]
            }
            
            # 从events中提取该轮的token数
            turn_events = [
                e for e in self.raw_data["monitoring_data"]["events"]
                if e.get("metadata", {}).get("turn") == turn_data["turn"]
                and e["event"] == "inference_end"
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
        if len(timestamps) < 2:
            return 0
        
        energy = 0
        for i in range(len(timestamps) - 1):
            dt = timestamps[i+1] - timestamps[i]
            avg_power = (power_values[i] + power_values[i+1]) / 2
            energy += avg_power * dt
        
        return energy
    
    def get_raw_data(self):
        """获取原始数据"""
        return self.raw_data
    
    def get_summary_data(self):
        """获取汇总数据"""
        return self.summary_data
```

#### 1.2 修改 run_experiment_suite 方法

```python
def run_experiment_suite(self, test_cases, output_file=None):
    """
    运行完整的实验套件
    
    Args:
        test_cases (list): 测试用例列表
        output_file (str, optional): 输出文件路径（不含扩展名）
            
    Returns:
        list: 实验结果列表
    """
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_base = os.path.join(self.output_dir, f"experiment_results_{timestamp}")
    else:
        output_base = output_file.replace("_raw_", "_").replace("_summary_", "_")
    
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
        
        # 运行实验
        result = self.run_single_experiment_v2(case, experiment_id=f"exp_{i:03d}")
        
        if result:
            raw_results.append(result.get_raw_data())
            summary_results.append(result.get_summary_data())
            
            # 实时保存
            with open(raw_file, "w", encoding="utf-8") as f:
                json.dump(raw_results, f, ensure_ascii=False, indent=2)
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary_results, f, ensure_ascii=False, indent=2)
            
            print(f"  [OK] 结果已保存")
        else:
            print(f"  [ERROR] 实验失败")
        
        # 短暂延迟
        if i < len(test_cases):
            time.sleep(2)
    
    print(f"\n{'='*70}")
    print(f"所有实验完成")
    print(f"  成功: {len(raw_results)}/{len(test_cases)}")
    print(f"  原始数据: {raw_file}")
    print(f"  汇总数据: {summary_file}")
    print(f"{'='*70}\n")
    
    return raw_results, summary_results
```

### 2. 创建数据转换脚本

创建 `scripts/convert_old_format.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将旧格式的实验结果转换为新格式（raw + summary分离）
"""

import json
import sys
from pathlib import Path

def convert_old_to_new(old_file):
    """
    转换旧格式到新格式
    
    Args:
        old_file (str): 旧格式文件路径
    """
    # 读取旧格式数据
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    # 准备新格式数据
    raw_results = []
    summary_results = []
    
    for i, old_result in enumerate(old_data, 1):
        # 构建raw数据
        raw_data = {
            "experiment_id": f"exp_{i:03d}",
            "config": {
                "model": old_result["model"],
                "model_info": old_result["model_info"],
                "prompts": old_result["prompts"],
                "task_type": old_result["task_type"],
                "keep_context": old_result.get("keep_context", False),
                "per_turn_monitoring": old_result.get("per_turn_monitoring", False),
                "max_tokens": old_result["metadata"].get("max_tokens"),
                "temperature": old_result["metadata"].get("temperature"),
                "top_p": old_result["metadata"].get("top_p"),
                "reference_text": None
            },
            "baseline_raw": convert_baseline_to_raw(old_result.get("baseline")),
            "conversation": old_result.get("conversation", []),
            "monitoring_data": old_result.get("system_metrics_full", {}),
            "metadata": old_result.get("metadata", {})
        }
        
        # 构建summary数据
        summary_data = {
            "experiment_id": f"exp_{i:03d}",
            "config_ref": {
                "model": old_result["model"],
                "task_type": old_result["task_type"],
                "prompts_count": len(old_result["prompts"]),
                "keep_context": old_result.get("keep_context", False)
            },
            "baseline_summary": old_result.get("baseline"),
            "performance": old_result.get("performance", {}),
            "resources": old_result.get("resources", {}),
            "derived_metrics": extract_derived_metrics(old_result.get("resources", {})),
            "quality": old_result.get("quality", {}),
            "conversation_summary": generate_conversation_summary(old_result.get("conversation", [])),
            "metadata": old_result.get("metadata", {})
        }
        
        raw_results.append(raw_data)
        summary_results.append(summary_data)
    
    # 保存新格式文件
    base_name = Path(old_file).stem
    output_dir = Path(old_file).parent
    
    raw_file = output_dir / f"{base_name}_raw.json"
    summary_file = output_dir / f"{base_name}_summary.json"
    
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(raw_results, f, ensure_ascii=False, indent=2)
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_results, f, ensure_ascii=False, indent=2)
    
    print(f"转换完成:")
    print(f"  原始数据: {raw_file}")
    print(f"  汇总数据: {summary_file}")

def convert_baseline_to_raw(baseline):
    """转换baseline数据为raw格式"""
    if not baseline:
        return None
    
    # 旧格式的baseline已经是汇总数据，这里保持不变
    # 实际应用中，如果有原始时间序列数据，应该提取出来
    return baseline

def extract_derived_metrics(resources):
    """从resources中提取派生指标"""
    derived = {}
    
    if "P_idle" in resources:
        derived["P_idle"] = resources["P_idle"]
    if "P_inc" in resources:
        derived["P_inc"] = resources["P_inc"]
    if "E_inc" in resources:
        derived["E_inc"] = resources["E_inc"]
    if "E_token" in resources:
        derived["E_token"] = resources["E_token"]
    if "PPW" in resources:
        derived["PPW"] = resources["PPW"]
    if "TPJ" in resources:
        derived["TPJ"] = resources["TPJ"]
    
    return derived

def generate_conversation_summary(conversation):
    """生成对话摘要"""
    summary = []
    for turn in conversation:
        summary.append({
            "turn": turn["turn"],
            "prompt_preview": turn["prompt"][:50] + "..." if len(turn["prompt"]) > 50 else turn["prompt"],
            "response_preview": turn["response"][:100] + "..." if len(turn["response"]) > 100 else turn["response"],
            "response_length": len(turn["response"])
        })
    return summary

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python convert_old_format.py <old_result_file.json>")
        sys.exit(1)
    
    convert_old_to_new(sys.argv[1])
```

## 测试计划

### 1. 单元测试

创建 `tests/test_data_structure.py`:

```python
import unittest
from experiments.experiment_runner import ExperimentResult

class TestExperimentResult(unittest.TestCase):
    
    def setUp(self):
        self.result = ExperimentResult("test_001")
    
    def test_set_config(self):
        self.result.set_config(
            model="test_model",
            model_info={"type": "test"},
            prompts=["test"],
            task_type="qa"
        )
        self.assertEqual(self.result.raw_data["config"]["model"], "test_model")
        self.assertEqual(self.result.summary_data["config_ref"]["prompts_count"], 1)
    
    def test_calculate_baseline_summary(self):
        # 模拟基线数据
        baseline_raw = {
            "duration_seconds": 10,
            "start_timestamp": 0,
            "end_timestamp": 10,
            "measurements": {
                "timestamps": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "gpu_power_w": [15, 16, 15, 17, 16, 15, 16, 15, 16, 15, 16],
                "cpu_percent": [5, 6, 5, 7, 6, 5, 6, 5, 6, 5, 6],
                "gpu_util": [2, 3, 2, 4, 3, 2, 3, 2, 3, 2, 3],
                "gpu_mem_mb": [3000] * 11,
                "gpu_temp_c": [45] * 11
            }
        }
        
        self.result.raw_data["baseline_raw"] = baseline_raw
        self.result._calculate_baseline_summary()
        
        baseline_summary = self.result.summary_data["baseline_summary"]
        self.assertAlmostEqual(baseline_summary["gpu_power_avg_w"], 15.7, places=1)
        self.assertEqual(baseline_summary["gpu_power_peak_w"], 17)

if __name__ == "__main__":
    unittest.main()
```

### 2. 集成测试

运行完整的实验流程，验证：
- Raw文件包含所有原始数据
- Summary文件包含所有计算指标
- 两个文件的experiment_id一致
- 数据可以正确读取和分析

### 3. 性能测试

- 测试大规模实验的文件大小
- 测试读写性能
- 测试内存占用

## 部署步骤

1. **代码审查**: 提交PR，进行代码审查
2. **测试验证**: 运行完整的测试套件
3. **文档更新**: 更新所有相关文档
4. **发布通知**: 通知用户新的数据格式
5. **数据迁移**: 提供迁移工具和指南
6. **监控反馈**: 收集用户反馈，及时修复问题

## 回滚计划

如果出现严重问题，可以：
1. 回退到旧版本代码
2. 使用转换工具将新格式转回旧格式
3. 保留旧格式文件作为备份

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**作者**: Kiro AI Assistant
