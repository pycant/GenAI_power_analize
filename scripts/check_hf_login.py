#!/usr/bin/env python3
"""检查 HuggingFace 登录状态"""

import sys

try:
    from huggingface_hub import whoami
    
    print("正在检查 HuggingFace 登录状态...\n")
    
    try:
        user_info = whoami()
        print("✅ 已登录 HuggingFace")
        print(f"   用户名: {user_info.get('name', 'N/A')}")
        print(f"   邮箱: {user_info.get('email', 'N/A')}")
        print(f"   组织: {user_info.get('orgs', [])}")
        print("\n可以开始下载 Gemma 模型了！")
        sys.exit(0)
    except Exception as e:
        print("❌ 未登录 HuggingFace")
        print(f"   错误: {str(e)}")
        print("\n请运行以下命令登录:")
        print("   huggingface-cli login")
        print("   或")
        print("   hf auth login")
        sys.exit(1)
        
except ImportError:
    print("❌ 缺少 huggingface_hub 包")
    print("请运行: pip install huggingface_hub")
    sys.exit(1)
