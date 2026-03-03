#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
手动下载 FLORES-200 数据集
从 GitHub 直接下载原始文件
"""

import json
import sys
import urllib.request
from pathlib import Path


def download_file(url, output_path):
    """下载文件"""
    print(f"  下载: {url}")
    try:
        urllib.request.urlretrieve(url, output_path)
        return True
    except Exception as e:
        print(f"  ✗ 下载失败: {e}")
        return False


def download_flores200_manual():
    """
    从 GitHub 手动下载 FLORES-200 devtest 数据
    """
    print("="*70)
    print("FLORES-200 手动下载工具")
    print("="*70)
    
    output_dir = Path("data/benchmarks/flores200")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # FLORES-200 GitHub 仓库的原始文件 URL
    base_url = "https://raw.githubusercontent.com/facebookresearch/flores/main/flores200/devtest"
    
    # 要下载的语言
    languages = {
        "eng_Latn": "英语",
        "zho_Hans": "简体中文",
        "zho_Hant": "繁体中文"
    }
    
    print(f"\n📥 从 GitHub 下载 FLORES-200 devtest 数据...")
    print(f"来源: {base_url}")
    
    # 下载各语言文件
    downloaded_files = {}
    for lang_code, lang_name in languages.items():
        print(f"\n下载 {lang_name} ({lang_code})...")
        
        file_url = f"{base_url}/{lang_code}.devtest"
        output_file = output_dir / f"{lang_code}.devtest"
        
        if download_file(file_url, output_file):
            print(f"  ✓ 已保存: {output_file}")
            downloaded_files[lang_code] = output_file
        else:
            print(f"  ✗ 下载失败")
    
    # 创建语言对 JSON 文件
    if "eng_Latn" in downloaded_files and "zho_Hans" in downloaded_files:
        print("\n创建英语-简体中文语言对...")
        
        # 读取文件
        with open(downloaded_files["eng_Latn"], 'r', encoding='utf-8') as f:
            eng_lines = [line.strip() for line in f.readlines()]
        
        with open(downloaded_files["zho_Hans"], 'r', encoding='utf-8') as f:
            zhs_lines = [line.strip() for line in f.readlines()]
        
        # 创建语言对
        pairs = []
        for i, (eng, zhs) in enumerate(zip(eng_lines, zhs_lines)):
            pairs.append({
                "id": i,
                "source": eng,
                "target": zhs,
                "source_lang": "eng_Latn",
                "target_lang": "zho_Hans"
            })
        
        # 保存
        output_file = output_dir / "flores200_eng_zho_Hans.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pairs, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 已保存: {output_file}")
        print(f"  句子对数量: {len(pairs)}")
    
    # 创建英语-繁体中文语言对
    if "eng_Latn" in downloaded_files and "zho_Hant" in downloaded_files:
        print("\n创建英语-繁体中文语言对...")
        
        with open(downloaded_files["eng_Latn"], 'r', encoding='utf-8') as f:
            eng_lines = [line.strip() for line in f.readlines()]
        
        with open(downloaded_files["zho_Hant"], 'r', encoding='utf-8') as f:
            zht_lines = [line.strip() for line in f.readlines()]
        
        pairs = []
        for i, (eng, zht) in enumerate(zip(eng_lines, zht_lines)):
            pairs.append({
                "id": i,
                "source": eng,
                "target": zht,
                "source_lang": "eng_Latn",
                "target_lang": "zho_Hant"
            })
        
        output_file = output_dir / "flores200_eng_zho_Hant.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(pairs, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 已保存: {output_file}")
        print(f"  句子对数量: {len(pairs)}")
    
    print("\n" + "="*70)
    print("✅ FLORES-200 下载完成！")
    print("="*70)
    print(f"\n数据集位置: {output_dir}")
    print("\n可用文件:")
    for f in sorted(output_dir.glob("*")):
        size = f.stat().st_size / 1024  # KB
        print(f"  - {f.name} ({size:.1f} KB)")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(download_flores200_manual())
    except KeyboardInterrupt:
        print("\n\n⚠️  下载已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
