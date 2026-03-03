# 数据结构重构实施计划

## 当前状态

✅ **已完成所有核心重构工作！**

完成项：
- ✅ 添加 `ExperimentResult` 类到 `experiments/experiment_runner.py`
- ✅ 创建完整的重构设计文档
- ✅ 修改 `run_single_experiment` 方法使用新数据结构
- ✅ 添加 `measure_idle_baseline_v2` 方法
- ✅ 添加 `_print_experiment_results` 辅助方法
- ✅ 修改 `_run_with_overall_monitoring_v2` 方法
- ✅ 修改 `_run_with_per_turn_monitoring_v2` 方法（完全支持per_turn_monitoring）
- ✅ 修改 `run_experiment_suite` 方法
- ✅ 删除旧的 `_generate_summary_file` 方法
- ✅ 创建测试脚本 `scripts/test_refactored_runner.py`
- ✅ 代码通过语法检查（无错误）

待完成（可选）：
- ⏳ 创建数据转换脚本 `scripts/convert_to_new_format.py`
- ⏳ 创建单元测试 `tests/test_experiment_result.py`
- ⏳ 更新用户文档
- ⏳ 转换历史数据

## 详细实施步骤

### 步骤1: 修改 `run_single_experiment` 方法

**位置**: `experiments/experiment_runner.py` 第1366行

**当前逻辑**:
```python
def run_single_experiment(self, model, prompts, task_type, ...):
    # 1. 测量空闲基线
    baseline_data = self.measure_idle_baseline(...)
    
    # 2. 根据per_turn_monitoring选择执行方式
    if per_turn_monitoring:
        result = self._run_with_per_turn_monitoring(...)
    else:
        result = self._run_with_overall_monitoring(...)
    
    # 3. 添加baseline到result
    if baseline_data:
        result["baseline"] = baseline_data
        # 计算增量指标
        result["resources"]["P_idle"] = ...
        result["resources"]["P_inc"] = ...
    
    return result
```

**新逻辑**:
```python
def run_single_experiment(self, model, prompts, task_type, ...):
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
```

**需要新增的辅助方法**:

```python
def measure_idle_baseline_v2(self, duration=10):
    """
    测量空闲基线，返回ResourceMonitor对象
    
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
    print(f"    - 对话轮数: {performance['turns']}")
    print(f"    - 总生成时间: {performance['total_time_seconds']:.2f}秒")
    print(f"    - 总Token数: {performance['output_tokens']}")
    print(f"    - 吞吐量: {performance['throughput_tokens_per_sec']:.2f} tokens/s")
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
```

### 步骤2: 修改 `_run_with_overall_monitoring` 方法

**位置**: `experiments/experiment_runner.py` 第1168行

**修改要点**:
1. 接收 `ExperimentResult` 对象作为参数
2. 不再返回完整的result字典
3. 直接将数据填充到 `exp_result` 对象中

**新签名**:
```python
def _run_with_overall_monitoring_v2(self, exp_result, model_info, prompts, 
                                    task_type, max_tokens, temperature, 
                                    top_p, keep_context):
    """
    整体监控模式：所有轮次使用同一个监控器
    
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
    monitor = ResourceMonitor(interval=0.2)
    monitor.start()
    monitor.mark_event("experiment_start")
    
    # 执行所有轮次
    all_responses = []
    context_data = None
    
    for i, prompt in enumerate(prompts, 1):
        monitor.mark_event("inference_start", metadata={"turn": i})
        start_time = time.time()
        
        # 调用模型
        if model_info["type"] == "ollama":
            response = self.call_ollama_model(...)
        else:
            response = self.call_hf_model(...)
        
        end_time = time.time()
        monitor.mark_event("inference_end", metadata={
            "turn": i,
            "tokens": response.get("token_count", 0)
        })
        
        # 添加对话轮次到exp_result
        exp_result.add_conversation_turn(
            turn=i,
            prompt=prompt,
            response=response["text"],
            start_time=start_time,
            end_time=end_time,
            turn_monitor=None  # 整体监控模式不传递turn_monitor
        )
        
        all_responses.append(response["text"])
        if keep_context:
            context_data = response.get("context")
    
    # 停止监控
    monitor.mark_event("experiment_end")
    time.sleep(0.5)
    monitor.stop()
    
    # 设置监控数据到exp_result
    exp_result.set_monitoring_data(monitor)
```

### 步骤3: 修改 `_run_with_per_turn_monitoring` 方法

**位置**: `experiments/experiment_runner.py` 第781行

**关键修改**: 适配per_turn_monitoring，为每轮保存独立的监控数据

**新签名**:
```python
def _run_with_per_turn_monitoring_v2(self, exp_result, model_info, prompts,
                                     task_type, max_tokens, temperature,
                                     top_p, keep_context):
    """
    分轮监控模式：每轮对话使用独立的监控器
    
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
    # 创建全局监控器（用于记录整体时间和事件）
    global_monitor = ResourceMonitor(interval=0.2)
    global_monitor.start()
    global_monitor.mark_event("experiment_start")
    
    all_responses = []
    context_data = None
    
    for i, prompt in enumerate(prompts, 1):
        print(f"  --> 轮次 {i}/{len(prompts)}")
        
        # 为该轮创建独立监控器
        turn_monitor = ResourceMonitor(interval=0.2)
        turn_monitor.start()
        turn_monitor.mark_event("inference_start", metadata={"turn": i})
        
        start_time = time.time()
        
        # 调用模型
        if model_info["type"] == "ollama":
            response = self.call_ollama_model(...)
        else:
            response = self.call_hf_model(...)
        
        end_time = time.time()
        
        # 停止该轮监控
        turn_monitor.mark_event("inference_end", metadata={
            "turn": i,
            "tokens": response.get("token_count", 0)
        })
        time.sleep(0.3)
        turn_monitor.stop()
        
        # 同时在全局监控器中记录事件
        global_monitor.mark_event("inference_end", metadata={
            "turn": i,
            "tokens": response.get("token_count", 0)
        })
        
        # 添加对话轮次到exp_result（包含该轮的监控数据）
        exp_result.add_conversation_turn(
            turn=i,
            prompt=prompt,
            response=response["text"],
            start_time=start_time,
            end_time=end_time,
            turn_monitor=turn_monitor  # 传递该轮的监控器
        )
        
        all_responses.append(response["text"])
        if keep_context:
            context_data = response.get("context")
    
    # 停止全局监控
    global_monitor.mark_event("experiment_end")
    time.sleep(0.5)
    global_monitor.stop()
    
    # 设置全局监控数据到exp_result
    exp_result.set_monitoring_data(global_monitor)
```

### 步骤4: 修改 `run_experiment_suite` 方法

**位置**: `experiments/experiment_runner.py` 第1502行

**修改要点**:
1. 分别保存raw和summary文件
2. 使用新的文件命名格式

**新实现**:
```python
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
        
        # 兼容性处理
        prompts = case.get("prompts", case.get("prompt"))
        if prompts is None:
            print(f"  [ERROR] 测试用例缺少 'prompts' 或 'prompt' 字段")
            continue
        
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

### 步骤5: 删除旧的 `_generate_summary_file` 方法

**位置**: `experiments/experiment_runner.py` 第1577行

**操作**: 删除整个方法，因为summary数据现在由 `ExperimentResult.calculate_summary()` 生成

### 步骤6: 创建数据转换脚本

**文件**: `scripts/convert_to_new_format.py`

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
    print(f"读取旧格式文件: {old_file}")
    
    # 读取旧格式数据
    with open(old_file, 'r', encoding='utf-8') as f:
        old_data = json.load(f)
    
    print(f"  找到 {len(old_data)} 个实验结果")
    
    # 准备新格式数据
    raw_results = []
    summary_results = []
    
    for i, old_result in enumerate(old_data, 1):
        print(f"  转换实验 {i}/{len(old_data)}...")
        
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
                "keep_context": old_result.get("keep_context", False),
                "per_turn_monitoring": old_result.get("per_turn_monitoring", False)
            },
            "baseline_summary": old_result.get("baseline"),
            "performance": old_result.get("performance", {}),
            "resources": extract_resources(old_result.get("resources", {})),
            "derived_metrics": extract_derived_metrics(old_result.get("resources", {})),
            "quality": old_result.get("quality", {}),
            "conversation_summary": generate_conversation_summary(
                old_result.get("conversation", []),
                old_result.get("per_turn_monitoring", False)
            ),
            "metadata": old_result.get("metadata", {})
        }
        
        raw_results.append(raw_data)
        summary_results.append(summary_data)
    
    # 保存新格式文件
    base_name = Path(old_file).stem
    output_dir = Path(old_file).parent
    
    # 移除可能的_raw或_summary后缀
    base_name = base_name.replace("_raw", "").replace("_summary", "")
    
    raw_file = output_dir / f"{base_name}_raw.json"
    summary_file = output_dir / f"{base_name}_summary.json"
    
    print(f"\n保存新格式文件...")
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(raw_results, f, ensure_ascii=False, indent=2)
    print(f"  原始数据: {raw_file}")
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_results, f, ensure_ascii=False, indent=2)
    print(f"  汇总数据: {summary_file}")
    
    print(f"\n✅ 转换完成!")

def convert_baseline_to_raw(baseline):
    """转换baseline数据"""
    if not baseline:
        return None
    # 旧格式的baseline已经是汇总数据，保持不变
    return baseline

def extract_resources(resources):
    """提取资源指标（不包含派生指标）"""
    excluded_keys = {"P_idle", "P_inc", "E_inc", "E_token", "PPW", "TPJ"}
    return {k: v for k, v in resources.items() if k not in excluded_keys}

def extract_derived_metrics(resources):
    """提取派生指标"""
    derived_keys = {"P_idle", "P_inc", "E_inc", "E_token", "PPW", "TPJ"}
    return {k: v for k, v in resources.items() if k in derived_keys}

def generate_conversation_summary(conversation, per_turn_monitoring):
    """生成对话摘要"""
    summary = []
    for turn in conversation:
        turn_summary = {
            "turn": turn["turn"],
            "prompt_preview": turn["prompt"][:50] + "..." if len(turn["prompt"]) > 50 else turn["prompt"],
            "response_preview": turn["response"][:100] + "..." if len(turn["response"]) > 100 else turn["response"],
            "response_length": len(turn["response"])
        }
        
        # 如果是分轮监控，添加性能和资源数据
        if per_turn_monitoring and "performance" in turn:
            turn_summary["tokens"] = turn["performance"].get("token_count", 0)
            turn_summary["duration_seconds"] = turn["performance"].get("time_seconds", 0)
            if turn_summary["duration_seconds"] > 0:
                turn_summary["throughput"] = turn_summary["tokens"] / turn_summary["duration_seconds"]
            
            if "resources" in turn:
                turn_summary["gpu_power_avg_w"] = turn["resources"].get("gpu_power_avg_w")
                turn_summary["gpu_energy_j"] = turn["resources"].get("gpu_energy_j")
        
        summary.append(turn_summary)
    
    return summary

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python convert_to_new_format.py <old_result_file.json>")
        print("\n示例:")
        print("  python convert_to_new_format.py data/experiments_4/experiment_results_raw_20260302_165811.json")
        sys.exit(1)
    
    convert_old_to_new(sys.argv[1])
```

## 测试计划

### 1. 单元测试

创建 `tests/test_experiment_result.py`:

```python
import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from experiments.experiment_runner import ExperimentResult

class TestExperimentResult(unittest.TestCase):
    
    def setUp(self):
        self.result = ExperimentResult("test_001")
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.result.experiment_id, "test_001")
        self.assertIsNotNone(self.result.raw_data)
        self.assertIsNotNone(self.result.summary_data)
    
    def test_set_config(self):
        """测试配置设置"""
        self.result.set_config(
            model="test_model",
            model_info={"type": "test"},
            prompts=["test1", "test2"],
            task_type="qa",
            keep_context=True,
            per_turn_monitoring=False
        )
        
        self.assertEqual(self.result.raw_data["config"]["model"], "test_model")
        self.assertEqual(self.result.summary_data["config_ref"]["prompts_count"], 2)
        self.assertTrue(self.result.summary_data["config_ref"]["keep_context"])
    
    def test_add_conversation_turn(self):
        """测试添加对话轮次"""
        self.result.add_conversation_turn(
            turn=1,
            prompt="test prompt",
            response="test response",
            start_time=1000.0,
            end_time=1005.0
        )
        
        self.assertEqual(len(self.result.raw_data["conversation"]), 1)
        self.assertEqual(self.result.raw_data["conversation"][0]["turn"], 1)
        self.assertEqual(self.result.raw_data["conversation"][0]["prompt"], "test prompt")

if __name__ == "__main__":
    unittest.main()
```

### 2. 集成测试

创建简单的测试用例运行完整流程：

```bash
# 创建测试用例
cat > data/test/test_refactoring.json << 'EOF'
[
  {
    "model": "ollama:qwen3:4b",
    "prompts": ["什么是Python？"],
    "task_type": "qa",
    "max_tokens": 100,
    "temperature": 0.7,
    "idle_measurement_duration": 5
  }
]
EOF

# 运行测试
python experiments/experiment_runner.py --config data/test/test_refactoring.json --output-dir data/test

# 检查输出文件
ls -lh data/test/experiment_results_*_raw.json
ls -lh data/test/experiment_results_*_summary.json
```

## 实施顺序建议

1. **第一阶段**（已完成）:
   - ✅ 添加 `ExperimentResult` 类

2. **第二阶段**（核心重构）:
   - 修改 `run_single_experiment`
   - 添加 `measure_idle_baseline_v2`
   - 添加 `_print_experiment_results`

3. **第三阶段**（监控方法）:
   - 修改 `_run_with_overall_monitoring_v2`
   - 修改 `_run_with_per_turn_monitoring_v2`

4. **第四阶段**（套件执行）:
   - 修改 `run_experiment_suite`
   - 删除 `_generate_summary_file`

5. **第五阶段**（工具和测试）:
   - 创建 `convert_to_new_format.py`
   - 创建单元测试
   - 运行集成测试

6. **第六阶段**（文档和清理）:
   - 更新文档
   - 转换历史数据
   - 清理旧代码

## 回滚计划

如果需要回滚：
1. 使用git恢复 `experiments/experiment_runner.py`
2. 删除新创建的测试文件
3. 保留转换脚本以备后用

## 下一步

请确认是否继续实施，我可以：
1. 逐步完成每个阶段的修改
2. 一次性完成所有修改
3. 先完成某个特定阶段

---

**文档版本**: v1.0  
**创建时间**: 2026-03-02  
**状态**: 待实施
