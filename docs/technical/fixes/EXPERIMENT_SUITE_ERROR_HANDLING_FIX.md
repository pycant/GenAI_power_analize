# 实验套件错误处理修复

## 问题描述

在运行包含多个测试用例的实验套件时，如果某个测试用例执行失败（抛出异常），整个实验套件会停止执行，导致后续的测试用例无法运行。

### 具体表现

在 `data/experiment_test/test_cases.json` 中有 2 个测试用例：
1. Qwen 7B 模型（QA 任务）- 成功执行
2. Phi-3 mini 模型（多轮对话任务）- 执行失败

结果文件中只记录了第一个测试用例的结果，第二个测试用例因为异常而没有被执行。

### 根本原因

在 `experiments/experiment_runner.py` 的 `run_experiment_suite` 方法中，调用 `run_single_experiment` 时没有捕获异常。当某个实验失败时，异常会向上传播到 `main()` 函数，导致整个程序终止。

```python
# 原代码（有问题）
for i, case in enumerate(test_cases, 1):
    # ...
    exp_result = self.run_single_experiment(...)  # 如果这里抛出异常，整个循环终止
    
    if exp_result:
        # 保存结果
        raw_results.append(exp_result.get_raw_data())
        # ...
```

## 解决方案

在 `run_experiment_suite` 方法中添加 try-except 块，捕获单个实验的异常，记录错误信息后继续执行下一个测试用例。

### 修改内容

```python
# 修复后的代码
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
```

## 修复效果

修复后的行为：
1. 第一个测试用例成功执行，结果被保存
2. 第二个测试用例执行失败，打印错误信息和堆栈跟踪
3. 程序继续执行后续的测试用例（如果有）
4. 最终报告显示成功和失败的数量

### 输出示例

```
[1/2] 运行实验
============================================================
开始实验
  模型: HF:Qwen--Qwen2.5-7B-Instruct:4bit
  任务: qa
  ...
  [OK] 结果已保存

[2/2] 运行实验
============================================================
开始实验
  模型: HF:microsoft--phi-3-mini-4k-instruct:4bit
  任务: multi_turn
  ...
  [ERROR] 实验执行失败: HF模型调用失败: ...
Traceback (most recent call last):
  ...
  [INFO] 继续执行下一个测试用例...

======================================================================
所有实验完成
  成功: 1/2
  原始数据: data/experiment_test/experiment_results_20260303_121138_raw.json
  汇总数据: data/experiment_test/experiment_results_20260303_121138_summary.json
======================================================================
```

## 相关文件

- `experiments/experiment_runner.py` - 主要修改文件
- `data/experiment_test/test_cases.json` - 测试用例文件

## 测试建议

修复后，建议重新运行测试：

```bash
conda activate bartscore
python experiments/experiment_runner.py --config data/experiment_test/test_cases.json --output-dir data/experiment_test
```

这样可以验证：
1. 第一个测试用例仍然成功执行
2. 第二个测试用例的错误被正确捕获和记录
3. 如果有更多测试用例，它们会继续执行

## 注意事项

1. 错误信息会完整打印到控制台，包括堆栈跟踪，便于调试
2. 失败的实验不会被记录到结果文件中
3. 最终报告会显示成功/失败的统计信息
4. 每个测试用例之间有 2 秒延迟，避免资源竞争

## 后续改进建议

1. 可以考虑将失败的实验也记录到单独的错误日志文件中
2. 添加重试机制，对于某些临时性错误（如网络问题）可以自动重试
3. 提供 `--fail-fast` 选项，允许用户选择在第一个错误时停止（当前行为）或继续执行（新行为）
