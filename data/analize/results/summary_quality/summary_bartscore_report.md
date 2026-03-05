# BARTScore评估报告

## 1. 评估概览

- 有效样本数: 47
- 评估模型数: 11
- 评估问题数: 5

## 2. BARTScore指标说明

BARTScore是基于BART模型的文本生成评估指标：

- **信息性 (Informativeness)**: P(summary|source)
  - 衡量摘要是否来自原文
  - 分数越高（越接近0）表示摘要越符合原文

- **忠实性 (Faithfulness)**: P(source|summary)
  - 衡量原文是否支持摘要
  - 分数越高（越接近0）表示摘要越忠实于原文

- **平均分数**: (信息性 + 忠实性) / 2
  - 综合评估摘要质量

**注意**: BARTScore分数为负值，值越高（越接近0）表示质量越好

## 3. 模型排名

### 3.1 按平均BARTScore排名

1. **gemma_2b_hf_8bit**: -2.4015
2. **qwen25_3b_hf_4bit**: -2.5030
3. **qwen_4b_ol_q4km**: -2.8505
4. **qwen25_3b_hf_8bit**: -2.8910
5. **gemma_4b_ol_q4km**: -3.2416
6. **qwen25_7b_hf_4bit**: -3.2902
7. **qwen_8b_ol_q4km**: -3.3548
8. **deepseek_8b_ol_q4km**: -3.4741
9. **phi3_4b_hf_8bit**: -3.8503
10. **phi3_4b_hf_4bit**: -3.8789
11. **gemma_2b_hf_4bit**: -3.8834

### 3.2 按信息性排名

1. **gemma_2b_hf_8bit**: -2.3156
2. **qwen25_3b_hf_4bit**: -2.6361
3. **qwen25_3b_hf_8bit**: -2.6777
4. **gemma_4b_ol_q4km**: -3.1063
5. **qwen25_7b_hf_4bit**: -3.2611
6. **qwen_4b_ol_q4km**: -3.2908
7. **qwen_8b_ol_q4km**: -3.3912
8. **deepseek_8b_ol_q4km**: -3.6620
9. **phi3_4b_hf_8bit**: -3.9651
10. **gemma_2b_hf_4bit**: -3.9980
11. **phi3_4b_hf_4bit**: -4.0926

### 3.3 按忠实性排名

1. **qwen25_3b_hf_4bit**: -2.3699
2. **qwen_4b_ol_q4km**: -2.4102
3. **gemma_2b_hf_8bit**: -2.4873
4. **qwen25_3b_hf_8bit**: -3.1043
5. **deepseek_8b_ol_q4km**: -3.2861
6. **qwen_8b_ol_q4km**: -3.3184
7. **qwen25_7b_hf_4bit**: -3.3193
8. **gemma_4b_ol_q4km**: -3.3769
9. **phi3_4b_hf_4bit**: -3.6653
10. **phi3_4b_hf_8bit**: -3.7356
11. **gemma_2b_hf_4bit**: -3.7687

## 4. 与其他指标的对比

### 4.1 指标相关性

- BARTScore vs ROUGE-L: 0.5420
- BARTScore vs BERTScore: 0.8239

## 5. 关键发现

- **最佳模型**: gemma_2b_hf_8bit (平均BARTScore: -2.4015)
- **分数范围**: [-4.5479, -1.8217]
- **平均分数**: -3.2544
