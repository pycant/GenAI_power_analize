#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
统一系统测试脚本
验证Ollama和Hugging Face模型集成是否正常工作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试必要的导入"""
    print("\n" + "="*60)
    print("测试1: 检查依赖导入")
    print("="*60)
    
    tests = []
    
    # 测试基础依赖
    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
        print(f"  CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA版本: {torch.version.cuda}")
            print(f"  GPU数量: {torch.cuda.device_count()}")
            if torch.cuda.device_count() > 0:
                print(f"  GPU名称: {torch.cuda.get_device_name(0)}")
        tests.append(("PyTorch", True))
    except ImportError as e:
        print(f"✗ PyTorch 导入失败: {e}")
        tests.append(("PyTorch", False))
    
    # 测试Transformers
    try:
        import transformers
        print(f"✓ Transformers {transformers.__version__}")
        tests.append(("Transformers", True))
    except ImportError as e:
        print(f"✗ Transformers 导入失败: {e}")
        tests.append(("Transformers", False))
    
    # 测试Hugging Face Hub
    try:
        import huggingface_hub
        print(f"✓ Hugging Face Hub {huggingface_hub.__version__}")
        tests.append(("HF Hub", True))
    except ImportError as e:
        print(f"✗ Hugging Face Hub 导入失败: {e}")
        tests.append(("HF Hub", False))
    
    # 测试Accelerate
    try:
        import accelerate
        print(f"✓ Accelerate {accelerate.__version__}")
        tests.append(("Accelerate", True))
    except ImportError as e:
        print(f"✗ Accelerate 导入失败: {e}")
        tests.append(("Accelerate", False))
    
    # 测试BitsAndBytes（量化）
    try:
        import bitsandbytes
        print(f"✓ BitsAndBytes {bitsandbytes.__version__}")
        tests.append(("BitsAndBytes", True))
    except ImportError as e:
        print(f"⚠️  BitsAndBytes 导入失败: {e}")
        print("   注意: 量化功能将不可用")
        tests.append(("BitsAndBytes", False))
    
    # 测试项目模块
    try:
        from src.model_deployment.hf_loader import HuggingFaceModelLoader
        print(f"✓ HF模型加载器")
        tests.append(("HF Loader", True))
    except ImportError as e:
        print(f"✗ HF模型加载器导入失败: {e}")
        tests.append(("HF Loader", False))
    
    try:
        from experiments.unified_runner import UnifiedExperimentRunner
        print(f"✓ 统一实验运行器")
        tests.append(("Unified Runner", True))
    except ImportError as e:
        print(f"✗ 统一实验运行器导入失败: {e}")
        tests.append(("Unified Runner", False))
    
    # 总结
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    print(f"\n导入测试: {passed}/{total} 通过")
    
    return all(result for _, result in tests[:-1])  # BitsAndBytes可选


def test_ollama_service():
    """测试Ollama服务"""
    print("\n" + "="*60)
    print("测试2: 检查Ollama服务")
    print("="*60)
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✓ Ollama服务运行正常")
            print(f"  可用模型数: {len(models)}")
            for model in models[:5]:  # 只显示前5个
                print(f"    - {model['name']}")
            return True
        else:
            print(f"✗ Ollama服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Ollama服务不可用: {e}")
        print("  请确保Ollama服务已启动")
        return False


def test_hf_models():
    """测试HF模型"""
    print("\n" + "="*60)
    print("测试3: 检查Hugging Face模型")
    print("="*60)
    
    try:
        from src.model_deployment.hf_loader import HuggingFaceModelLoader
        
        loader = HuggingFaceModelLoader()
        models = loader.list_available_models()
        
        if models:
            print(f"✓ 找到 {len(models)} 个已下载的HF模型:")
            for model in models:
                print(f"  - {model['name']} ({model['size_gb']} GB, {model['format']})")
                if model.get('quantization'):
                    print(f"    量化: {model['quantization']}")
            return True
        else:
            print("⚠️  未找到已下载的HF模型")
            print("  请运行: python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct --quantize 4bit")
            return False
            
    except Exception as e:
        print(f"✗ 检查HF模型时出错: {e}")
        return False


def test_model_spec_parsing():
    """测试模型规格解析"""
    print("\n" + "="*60)
    print("测试4: 模型规格解析")
    print("="*60)
    
    try:
        from experiments.unified_runner import UnifiedExperimentRunner
        
        runner = UnifiedExperimentRunner()
        
        test_specs = [
            "qwen3:4b",
            "ollama:deepseek-r1:8b",
            "hf:models/huggingface/Qwen--Qwen2.5-3B-Instruct:4bit",
            "hf:models/huggingface/Qwen--Qwen2.5-7B-Instruct",
        ]
        
        all_passed = True
        for spec in test_specs:
            try:
                info = runner.parse_model_spec(spec)
                print(f"✓ {spec}")
                print(f"  类型: {info['type']}")
                print(f"  显示名: {info['display_name']}")
            except Exception as e:
                print(f"✗ {spec}: {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ 模型规格解析测试失败: {e}")
        return False


def test_config_file():
    """测试配置文件"""
    print("\n" + "="*60)
    print("测试5: 配置文件")
    print("="*60)
    
    try:
        from experiments import config
        
        print(f"✓ 配置文件加载成功")
        print(f"  Ollama模型数: {len(config.OLLAMA_MODELS)}")
        print(f"  HF模型数: {len(config.HF_MODELS)}")
        print(f"  温度: {config.TEMPERATURE}")
        print(f"  Top-P: {config.TOP_P}")
        print(f"  最大Tokens: {config.MAX_TOKENS}")
        
        # 测试辅助函数
        all_specs = config.get_all_model_specs()
        print(f"  总模型规格数: {len(all_specs)}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置文件测试失败: {e}")
        return False


def test_sample_experiment():
    """测试示例实验（可选）"""
    print("\n" + "="*60)
    print("测试6: 运行示例实验（可选）")
    print("="*60)
    
    response = input("是否运行一个快速示例实验？这将调用模型生成文本。(yes/no): ")
    
    if response.lower() not in ['yes', 'y']:
        print("跳过示例实验")
        return True
    
    try:
        from experiments.unified_runner import UnifiedExperimentRunner
        
        runner = UnifiedExperimentRunner()
        
        # 选择一个可用的模型
        print("\n选择测试模型:")
        print("1. Ollama模型 (qwen3:4b)")
        print("2. HF模型 (如果已下载)")
        
        choice = input("请选择 (1/2): ")
        
        if choice == "1":
            model_spec = "qwen3:4b"
        else:
            # 检查可用的HF模型
            from src.model_deployment.hf_loader import HuggingFaceModelLoader
            loader = HuggingFaceModelLoader()
            models = loader.list_available_models()
            
            if not models:
                print("✗ 没有可用的HF模型")
                return False
            
            model = models[0]
            quantize = model.get('quantization', '4bit')
            model_spec = f"hf:{model['path']}:{quantize}" if quantize else f"hf:{model['path']}"
        
        print(f"\n使用模型: {model_spec}")
        print("运行测试...")
        
        result = runner.run_single_experiment(
            model_spec=model_spec,
            prompt="请用一句话解释什么是人工智能。",
            task_type="qa",
            max_tokens=50,
            temperature=0.7
        )
        
        if result:
            print(f"\n✓ 示例实验成功!")
            print(f"  生成时间: {result['performance']['total_time_seconds']:.2f}秒")
            print(f"  Token数: {result['performance']['token_count']}")
            print(f"  吞吐量: {result['performance']['throughput_tokens_per_sec']:.2f} tokens/s")
            print(f"  生成文本: {result['generated_text'][:100]}...")
            return True
        else:
            print("✗ 示例实验失败")
            return False
            
    except Exception as e:
        print(f"✗ 示例实验出错: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("统一系统测试")
    print("="*70)
    
    results = []
    
    # 运行所有测试
    results.append(("依赖导入", test_imports()))
    results.append(("Ollama服务", test_ollama_service()))
    results.append(("HF模型", test_hf_models()))
    results.append(("模型规格解析", test_model_spec_parsing()))
    results.append(("配置文件", test_config_file()))
    results.append(("示例实验", test_sample_experiment()))
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name:20s}: {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n总计: {passed_count}/{total_count} 测试通过")
    
    if passed_count == total_count:
        print("\n🎉 所有测试通过！系统已准备就绪。")
        print("\n下一步:")
        print("  1. 运行示例实验: python experiments/unified_runner.py --sample")
        print("  2. 查看使用指南: experiments/UNIFIED_RUNNER_GUIDE.md")
        return 0
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息。")
        print("\n常见问题:")
        print("  - 依赖缺失: pip install -r requirements-hf.txt")
        print("  - Ollama未启动: 启动Ollama服务")
        print("  - HF模型未下载: python scripts/download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct --quantize 4bit")
        return 1


if __name__ == "__main__":
    sys.exit(main())
