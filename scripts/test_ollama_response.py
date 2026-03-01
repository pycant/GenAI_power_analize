#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

# 测试qwen3:4b的响应结构
print("测试 qwen3:4b 的响应结构...")
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:4b",
        "prompt": "请解释牛顿第一定律。",
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 200
        }
    },
    timeout=60
)

print(f"状态码: {response.status_code}")
result = response.json()
print(f"\n响应字段:")
for key in result.keys():
    print(f"  - {key}")

print(f"\nresponse字段内容:")
print(f"  类型: {type(result.get('response'))}")
print(f"  长度: {len(result.get('response', ''))}")
print(f"  内容: {result.get('response', '')[:200]}")

print(f"\n完整响应 (格式化):")
print(json.dumps(result, ensure_ascii=False, indent=2)[:1000])
