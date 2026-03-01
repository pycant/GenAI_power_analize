#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试旧版 experiment_runner.py 是否能正常工作
"""

import subprocess
import sys
import os
import json
import time

def test_ollama_service():
    """测试 Ollama 服务是否可用"""
    print("=" * 60)
    print("测试 1: 检查 Ollama 服务")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✓ Ollama 服务正常运行")
            print("\n可用模型:")
            print(result.stdout)
            return True
        else:
            print("✗ Ollama 服务异常")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ 检查 Ollama 服务时出错: {e}")
        return False

def test_ollama_api():
    """测试 Ollama HTTP API"""
    print("\n" + "=" * 60)
    print("测试 2: 测试 Ollama HTTP API")
    print("=" * 60)
    
    try:
        import requests
        
        # 测试简单的生成请求
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:4b",
                "prompt": "你好",
                "stream": False,
                "options": {
                    "num_predict": 10
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ Ollama HTTP API 正常工作")
            print(f"  响应: {result.get('response', '')[:50]}...")
            return True
        else:
            print(f"✗ Ollama HTTP API 返回错误: {response.status_code}")
            print(f"  {response.text}")
            return False
            
    except ImportError:
        print("✗ 缺少 requests 库，请安装: pip install requests")
        return False
    except Exception as e:
        print(f"✗ 测试 Ollama HTTP API 时出错: {e}")
        return False

def test_experiment_runner():
    """测试 experiment_runner.py"""
    print("\n" + "=" * 60)
    print("测试 3: 运行 experiment_runner.py")
    print("=" * 60)
    
    # 创建临时测试配置
    test_config = [{
        "model": "qwen3:4b",
        "prompt": "请用一句话介绍人工智能。",
        "task_type": "qa",
        "max_tokens": 50,
        "temperature": 0.7
    }]
    
    test_config_path = "data/test/temp_test.json"
    os.makedirs("data/test", exist_ok=True)
    
    try:
        with open(test_config_path, "w", encoding="utf-8") as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
        
        print(f"创建测试配置: {test_config_path}")
        print(f"测试模型: qwen3:4b")
        print("开始运行实验...\n")
        
        # 运行实验
        result = subprocess.run(
            [
                sys.executable,
                "experiments/experiment_runner.py",
                "--config", test_config_path,
                "--output-dir", "data/test"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print("运行器输出:")
        print("-" * 60)
        print(result.stdout)
        
        if result.stderr:
            print("\n错误输出:")
            print("-" * 60)
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✓ experiment_runner.py 运行成功")
            
            # 检查输出文件
            import glob
            output_files = glob.glob("data/test/experiment_results_*.json")
            if output_files:
                latest_file = max(output_files, key=os.path.getctime)
                print(f"  结果文件: {latest_file}")
                
                with open(latest_file, "r", encoding="utf-8") as f:
                    results = json.load(f)
                    print(f"  实验结果数: {len(results)}")
                    if results:
                        print(f"  生成文本长度: {len(results[0].get('generated_text', ''))}")
            
            return True
        else:
            print(f"\n✗ experiment_runner.py 运行失败 (返回码: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ 实验运行超时")
        return False
    except Exception as e:
        print(f"✗ 测试 experiment_runner.py 时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 清理临时文件
        if os.path.exists(test_config_path):
            os.remove(test_config_path)

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("Ollama 实验运行器测试套件")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("Ollama 服务", test_ollama_service()))
    results.append(("Ollama HTTP API", test_ollama_api()))
    results.append(("experiment_runner.py", test_experiment_runner()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ 所有测试通过！旧版运行器可以正常使用。")
        print("\n使用方法:")
        print("  python experiments/experiment_runner.py --config data/test/test_cases_ollama.json --output-dir data/test")
        return 0
    else:
        print("\n✗ 部分测试失败，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
