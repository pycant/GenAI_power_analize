#!/usr/bin/env python3
"""
清理 GPU 显存
功能：
1. 释放 Python 进程占用的 GPU 内存
2. 停止 Ollama 服务
3. 清理 GPU 缓存
"""

import subprocess
import sys
import os


def clear_gpu_memory():
    """清理 GPU 显存"""
    print("🧹 开始清理 GPU 显存...\n")
    
    # 1. 清理 Python GPU 进程
    print("1️⃣ 查找并终止占用 GPU 的 Python 进程...")
    try:
        result = subprocess.run(
            ['powershell', '-Command', 
             'Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.MainWindowTitle -like "*GPU* -ErrorAction SilentlyContinue}'],
            capture_output=True,
            text=True
        )
        
        # 使用 nvidia-smi 查找 GPU 进程
        result = subprocess.run(
            ['nvidia-smi', '--query-compute-apps=pid,process_name,used_memory', '--format=csv,noheader,nounits'],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("   找到以下 GPU 进程:")
            for line in result.stdout.strip().split('\n'):
                print(f"   - {line}")
            
            # 提取 PID 并终止
            pids = []
            for line in result.stdout.strip().split('\n'):
                parts = line.split(',')
                if len(parts) >= 1:
                    try:
                        pid = int(parts[0].strip())
                        pids.append(pid)
                    except:
                        pass
            
            for pid in pids:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], capture_output=True)
                    print(f"   ✅ 已终止进程 PID: {pid}")
                except:
                    pass
        else:
            print("   ✅ 没有发现占用 GPU 的 Python 进程")
            
    except Exception as e:
        print(f"   ⚠️ 检查 GPU 进程时出错: {e}")
    
    # 2. 清理 PyTorch 缓存
    print("\n2️⃣ 清理 PyTorch GPU 缓存...")
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print(f"   ✅ CUDA 缓存已清理")
            print(f"   📊 当前 GPU 显存: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")
        else:
            print("   ⚠️ CUDA 不可用")
    except ImportError:
        print("   ⚠️ PyTorch 未安装")
    
    # 3. 停止 Ollama 服务
    print("\n3️⃣ 停止 Ollama 服务...")
    try:
        # 检查 Ollama 是否在运行
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Process ollama -ErrorAction SilentlyContinue'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], capture_output=True)
            print("   ✅ Ollama 服务已停止")
        else:
            print("   ✅ Ollama 服务未运行")
            
    except Exception as e:
        print(f"   ⚠️ 停止 Ollama 时出错: {e}")
    
    # 4. 显示 GPU 状态
    print("\n4️⃣ 当前 GPU 状态:")
    try:
        result = subprocess.run(
            ['nvidia-smi'],
            capture_output=True,
            text=True
        )
        print(result.stdout)
    except:
        print("   ⚠️ 无法获取 GPU 状态")
    
    print("\n✨ GPU 显存清理完成！")


def stop_ollama_only():
    """仅停止 Ollama 服务"""
    print("🛑 停止 Ollama 服务...")
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], capture_output=True)
        print("✅ Ollama 服务已停止")
    except Exception as e:
        print(f"⚠️ 停止 Ollama 时出错: {e}")


def start_ollama():
    """启动 Ollama 服务"""
    print("🚀 启动 Ollama 服务...")
    try:
        subprocess.Popen(['ollama', 'serve'], 
                         creationflags=subprocess.CREATE_NO_WINDOW)
        print("✅ Ollama 服务已启动")
        print("   模型加载可能需要一些时间...")
    except Exception as e:
        print(f"⚠️ 启动 Ollama 时出错: {e}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == '--ollama-only':
            stop_ollama_only()
        elif command == '--start-ollama':
            start_ollama()
        else:
            print("用法:")
            print("  python clear_gpu_memory.py          # 清理所有 GPU 显存")
            print("  python clear_gpu_memory.py --ollama-only  # 仅停止 Ollama")
            print("  python clear_gpu_memory.py --start-ollama # 启动 Ollama")
    else:
        clear_gpu_memory()