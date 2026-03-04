# FLORES-200 数据集

## 下载方法

### 方法 1: 使用 Hugging Face datasets（推荐）

```python
from datasets import load_dataset

# 下载 FLORES-200 devtest
dataset = load_dataset("facebook/flores", "zho_Hans-eng")

# 保存为 JSON
dataset['devtest'].to_json('flores200_zh_en.json')
```

### 方法 2: 从 GitHub 下载

访问: https://github.com/facebookresearch/flores/tree/main/flores200

## 语言对

常用语言对：
- eng_Latn (英语) ↔ zho_Hans (简体中文)
- eng_Latn (英语) ↔ zho_Hant (繁体中文)
- eng_Latn (英语) ↔ jpn_Jpan (日语)
- eng_Latn (英语) ↔ kor_Hang (韩语)

## 数据格式

每个语言对包含约 1,012 个句子对。

## 使用示例

```python
import json

# 加载数据
with open('flores200_zh_en.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 遍历句子对
for item in data:
    source = item['sentence_eng_Latn']
    target = item['sentence_zho_Hans']
    print(f"EN: {source}")
    print(f"ZH: {target}")
```
