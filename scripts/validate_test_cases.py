#!/usr/bin/env python3
"""验证测试用例文件的完整性和唯一性"""

import json
from pathlib import Path

def validate_test_cases(filepath):
    """验证测试用例文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tasks = data.get('tasks', [])
    ids = [t['id'] for t in tasks]
    
    print(f"文件: {filepath}")
    print(f"总任务数: {len(ids)}")
    print(f"唯一ID数: {len(set(ids))}")
    
    # 检查重复ID
    duplicates = [id for id in ids if ids.count(id) > 1]
    if duplicates:
        print(f"⚠️  发现重复ID: {set(duplicates)}")
        for dup_id in set(duplicates):
            print(f"   - {dup_id}: 出现 {ids.count(dup_id)} 次")
        return False
    else:
        print("✅ 所有ID唯一")
        return True

if __name__ == "__main__":
    filepath = Path("data/test_cases/test_cases_comprehensive.json")
    validate_test_cases(filepath)
