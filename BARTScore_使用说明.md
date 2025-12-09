# BARTScore 项目部署与使用说明

## 项目概述
BARTScore 是一个基于 BART 模型的文本生成评估指标，将文本评估视为文本生成任务。该项目来自论文《BARTScore: Evaluating Generated Text as Text Generation》。

## 环境部署

### 1. 创建 Conda 环境
```bash
conda create -n bartscore python=3.8 -y
conda activate bartscore
```

### 2. 安装核心依赖
由于原始 requirements.txt 中的某些包版本过旧，建议按以下顺序安装：

```bash
# 安装 PyTorch (CPU版本)
pip install torch==1.13.1 --index-url https://download.pytorch.org/whl/cpu

# 安装 Transformers
pip install transformers==4.36.0

# 安装其他必要依赖
pip install numpy==1.24.4
pip install tqdm
pip install pandas
```

### 3. 验证安装
运行测试脚本验证安装是否成功：
```bash
python test_bartscore.py
```

## 基本使用方法

### 1. 导入 BARTScorer
```python
from bart_score import BARTScorer

# 初始化 BARTScorer
bart_scorer = BARTScorer(device='cpu', checkpoint='facebook/bart-large-cnn')
```

### 2. 单参考评分
```python
srcs = ['This is a very good idea.']
tgts = ['That is an excellent idea.']

scores = bart_scorer.score(srcs, tgts, batch_size=4)
print(scores)  # 输出: [-2.511526584625244]
```

**注意**: 分数为负值，值越高（越接近0）表示质量越好。

### 3. 多参考评分
```python
srcs = ["I'm super happy today."]
tgts = [["I feel good today.", "I feel sad today."]]

# agg 参数可以是 "mean" 或 "max"
scores = bart_scorer.multi_ref_score(srcs, tgts, agg="max", batch_size=4)
print(scores)  # 输出: [-2.5008108615875244]
```

### 4. 使用 ParaBank2 微调的模型
```python
from bart_score import BARTScorer

bart_scorer = BARTScorer(device='cpu', checkpoint='facebook/bart-large-cnn')
bart_scorer.load(path='bart.pth')  # 需要先下载模型文件

scores = bart_scorer.score(['This is interesting.'], ['This is fun.'])
```

## 项目结构

```
BARTScore/
├── README.md                    # 项目主说明文档
├── bart_score.py               # 主要评分接口
├── requirements.txt            # 依赖包列表（部分版本过旧）
├── analysis.py                 # 分析工具
├── analysis.ipynb             # 分析示例
├── utils.py                    # 工具函数
├── D2T/                        # 数据到文本任务
├── SUM/                        # 摘要任务
├── WMT/                        # 机器翻译任务
└── train/                      # 训练自定义模型
```

## 复现实验

### 数据到文本 (D2T) 任务
```bash
cd D2T
python score.py --file BAGEL/data.pkl --device cpu --output BAGEL/scores.pkl --bert_score --mover_score --rouge --bart_score --bart_score_cnn --bart_score_para --prism --prompt bart_para_ref
```

### 摘要 (SUM) 任务
```bash
cd SUM
python score.py --file REALSumm/data.pkl --device cpu --output REALSumm/scores.pkl --bert_score --mover_score --rouge --bart_score --bart_score_cnn --prism --prompt bart_cnn_src
```

### 机器翻译 (WMT) 任务
```bash
cd WMT
python score.py --file kk-en/data.pkl --device cpu --output kk-en/scores.pkl --bleu --chrf --bleurt --prism --comet --bert_score --bart_score --bart_score_cnn --bart_score_para --prompt bart_para_ref
```

## 训练自定义模型

### 1. 准备数据
数据格式应为 JSONL 文件：
```json
{"text": "This is the first text.", "summary": "This is the first summary."}
{"text": "This is the second text.", "summary": "This is the second summary."}
```

### 2. 训练模型
```bash
cd train
python bart.py --train_file train.json --validation_file val.json --output_dir my_bartscore
```

### 3. 使用自定义模型
```python
from bart_score import BARTScorer
bart_scorer = BARTScorer(device='cpu', checkpoint='my_bartscore')
```

## 常见问题

### 1. 依赖版本冲突
原始 requirements.txt 中的某些包版本过旧，建议使用较新的兼容版本。

### 2. 模型下载缓慢
首次运行时会下载 BART 模型（约 1.63GB），请确保网络连接稳定。

### 3. GPU 支持
如需使用 GPU，请安装 CUDA 版本的 PyTorch：
```bash
pip install torch==1.13.1 --index-url https://download.pytorch.org/whl/cu117
```
并将 device 参数改为 'cuda:0'。

### 4. 内存不足
BART 模型较大，CPU 模式下需要约 3-4GB 内存。如果内存不足，可尝试减小 batch_size。

## 性能优化建议

1. **批量处理**: 尽量使用较大的 batch_size 以提高效率
2. **GPU 加速**: 如有 GPU，使用 GPU 可大幅提升速度
3. **模型缓存**: 首次加载后模型会缓存，后续运行速度会更快
4. **内存管理**: 处理大量数据时注意内存使用，可分批处理

## 参考文献

- 论文: [BARTScore: Evaluating Generated Text as Text Generation](https://arxiv.org/abs/2106.11520)
- 代码仓库: https://github.com/neulab/BARTScore

## 许可证
本项目基于 MIT 许可证开源。
