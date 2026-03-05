# 翻译质量评估报告

**生成时间**: 2026-03-05 14:15:52

## 1. 评估概览

- 评估模型数: 11
- 评估问题数: 5
- 总评估次数: 55
- 语言对: 英→中 (4题), 中→英 (1题)

## 2. 核心指标排名

### 2.1 BLEU-4 排名

BLEU-4 是机器翻译最经典的评估指标，衡量词汇级别的匹配度。

1. ✅ **deepseek_8b_ol_q4km**: 0.5407
2. ❌ **phi3_4b_hf_4bit**: 0.1008
3. ❌ **gemma_4b_ol_q4km**: 0.0230
4. ❌ **qwen25_7b_hf_4bit**: 0.0216
5. ❌ **phi3_4b_hf_8bit**: 0.0197
6. ❌ **qwen25_3b_hf_4bit**: 0.0171
7. ❌ **qwen25_3b_hf_8bit**: 0.0167
8. ❌ **qwen_8b_ol_q4km**: 0.0128
9. ❌ **qwen_4b_ol_q4km**: 0.0107
10. ❌ **gemma_2b_hf_4bit**: 0.0000
11. ❌ **gemma_2b_hf_8bit**: 0.0000

### 2.2 chrF 排名

chrF 基于字符级别匹配，对中文等字符级语言更友好。

1. ✅ **deepseek_8b_ol_q4km**: 0.5173
2. ❌ **gemma_4b_ol_q4km**: 0.1376
3. ❌ **phi3_4b_hf_4bit**: 0.1206
4. ❌ **qwen25_7b_hf_4bit**: 0.1093
5. ❌ **phi3_4b_hf_8bit**: 0.1015
6. ❌ **qwen25_3b_hf_4bit**: 0.0872
7. ❌ **qwen_8b_ol_q4km**: 0.0865
8. ❌ **qwen_4b_ol_q4km**: 0.0824
9. ❌ **qwen25_3b_hf_8bit**: 0.0776
10. ❌ **gemma_2b_hf_4bit**: 0.0000
11. ❌ **gemma_2b_hf_8bit**: 0.0000

### 2.3 BERTScore F1 排名

BERTScore 基于语义相似度，能识别同义词和改写。

1. ✅ **deepseek_8b_ol_q4km**: 0.8845
2. ⚠️ **phi3_4b_hf_4bit**: 0.6452
3. ⚠️ **phi3_4b_hf_8bit**: 0.6319
4. ⚠️ **qwen25_3b_hf_8bit**: 0.6164
5. ⚠️ **gemma_2b_hf_4bit**: 0.6080
6. ⚠️ **gemma_2b_hf_8bit**: 0.6037
7. ❌ **qwen25_3b_hf_4bit**: 0.5856
8. ❌ **qwen_8b_ol_q4km**: 0.5627
9. ❌ **qwen_4b_ol_q4km**: 0.5518
10. ❌ **qwen25_7b_hf_4bit**: 0.5510
11. ❌ **gemma_4b_ol_q4km**: 0.5302

### 2.4 按语言对分析

各模型在不同语言对上的BLEU-4分数：

**英译中 (eng → zho_Hans)**:

1. deepseek_8b_ol_q4km: 0.4259
2. gemma_4b_ol_q4km: 0.0178
3. qwen25_7b_hf_4bit: 0.0161
4. phi3_4b_hf_8bit: 0.0141
5. qwen25_3b_hf_4bit: 0.0139

**中译英 (zho_Hans → eng)**:

1. deepseek_8b_ol_q4km: 1.0000
2. phi3_4b_hf_4bit: 0.4661
3. gemma_4b_ol_q4km: 0.0440
4. qwen25_7b_hf_4bit: 0.0437
5. phi3_4b_hf_8bit: 0.0421

## 3. 指标说明

### 3.1 BLEU-4
- **范围**: [0, 1]
- **含义**: 4-gram词汇匹配度
- **解释**: 0.4+ 优秀，0.2-0.4 良好，<0.2 需改进

### 3.2 chrF
- **范围**: [0, 1]
- **含义**: 字符级F分数
- **解释**: 0.5+ 优秀，0.3-0.5 良好，<0.3 需改进

### 3.3 BERTScore F1
- **范围**: [0, 1]
- **含义**: 语义相似度
- **解释**: 0.8+ 优秀，0.6-0.8 良好，<0.6 需改进

## 4. 详细数据

详细评分数据请参考:
- `translation_quality_scores.csv` - 每个模型每个问题的详细评分
- `translation_quality_summary.csv` - 按模型汇总的统计数据
