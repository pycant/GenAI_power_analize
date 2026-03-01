#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 测试qwen3:4b的完整响应
print("测试 qwen3:4b 的完整响应结构...")
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:4b",
        "prompt": "请用一句话解释牛顿第一定律。",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 100
        }
    },
    timeout=60
)

result = response.json()

print("\n所有字段:")
for key, value in result.items():
    if isinstance(value, str):
        print(f"\n{key}:")
        print(f"  长度: {len(value)}")
        if len(value) > 0:
            print(f"  内容: {value[:500]}")
    elif isinstance(value, list):
        print(f"\n{key}: (列表，长度 {len(value)})")
    else:
        print(f"\n{key}: {value}")

# 保存完整响应到文件
with open('data/test/qwen3_full_response.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
    
print("\n\n完整响应已保存到: data/test/qwen3_full_response.json")
