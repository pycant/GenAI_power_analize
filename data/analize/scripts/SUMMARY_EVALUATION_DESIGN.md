# 文本摘要任务 (Summary) 质量评估方法设计

## 1. 评估目标

评估模型生成摘要在**信息保留程度、简洁性、流畅性与语义正确性**上的表现。

## 2. 数据特征分析

### 2.1 任务类型

基于提供的摘要问题，任务类型为：
- **抽取式摘要**: 从原文中提取关键信息
- **压缩式摘要**: 将长文本压缩为指定字数的简短摘要
- **中文摘要**: 所有原文和摘要均为中文

### 2.2 摘要要求

| 问题ID | 原文主题 | 字数要求 | 原文长度 |
|--------|----------|----------|----------|
| q01 | 云计算 | 50-70字 | ~200字 |
| q02 | 物联网 | 40-60字 | ~150字 |
| q03 | 深度学习 | 40-60字 | ~180字 |
| q04 | 人工智能 | 50-80字 | ~220字 |
| q05 | 区块链 | 40-60字 | ~180字 |

### 2.3 评估挑战

- **无标准参考摘要**: 数据集中没有提供标准摘要答案
- **主观性强**: 摘要质量评估具有一定主观性
- **多样性**: 同一原文可以有多种合理的摘要方式
- **字数约束**: 需要评估是否符合字数要求

## 3. 核心指标

### 3.1 ROUGE-L ✅ 高度可行

**定义**：
- 基于**最长公共子序列（LCS）**计算的 F1 分数
- 衡量生成摘要与原文的结构完整性和信息保留度

**计算方法**：

1. 计算生成摘要与原文的最长公共子序列
2. 计算精确率：`P_lcs = LCS(summary, source) / len(summary)`
3. 计算召回率：`R_lcs = LCS(summary, source) / len(source)`
4. 计算F1分数：`F_lcs = 2 × P_lcs × R_lcs / (P_lcs + R_lcs)`

**数学表达**：
```
R_lcs = LCS(X, Y) / |Y|
P_lcs = LCS(X, Y) / |X|
F_lcs = (1 + β²) × R_lcs × P_lcs / (R_lcs + β² × P_lcs)
```

其中：
- X: 生成摘要
- Y: 原文
- β: 通常设为1

**范围**: [0, 1]，越高越好

**优势**：
- ✅ 关注**语序与结构完整性**
- ✅ 是摘要任务最经典的核心指标
- ✅ 无需参考摘要，可与原文比较
- ✅ 计算成本低，无需外部模型

**实现方案**：
```python
def calculate_rouge_l(summary: str, source: str) -> Dict[str, float]:
    """计算ROUGE-L分数"""
    try:
        from rouge import Rouge
        
        rouge = Rouge()
        scores = rouge.get_scores(summary, source)[0]
        
        return {
            'rouge_l_precision': scores['rouge-l']['p'],
            'rouge_l_recall': scores['rouge-l']['r'],
            'rouge_l_f1': scores['rouge-l']['f']
        }
    except Exception as e:
        print(f"⚠️  ROUGE-L calculation failed: {e}")
        return {
            'rouge_l_precision': None,
            'rouge_l_recall': None,
            'rouge_l_f1': None
        }
```

### 3.2 BERTScore ✅ 高度可行

**定义**：
- 基于预训练语言模型 BERT 的**上下文语义相似度**
- 使用 BERT 得到词向量，计算预测与原文间的余弦相似度

**计算方法**：
1. 使用预训练BERT模型获取token向量表示
2. 计算摘要与原文token间的余弦相似度
3. 通过最大匹配得到语义级别的Precision/Recall/F1

**数学表达**：
```
BERTScore_P = (1/|x|) × Σ_{x_i ∈ x} max_{y_j ∈ y} cos(e_{x_i}, e_{y_j})
BERTScore_R = (1/|y|) × Σ_{y_j ∈ y} max_{x_i ∈ x} cos(e_{x_i}, e_{y_j})
BERTScore_F1 = 2 × P × R / (P + R)
```

**范围**: [0, 1]，越高越好

**优势**：
- ✅ 能识别**同义不同表述**
- ✅ 更贴合人类对摘要的语义理解
- ✅ 对改写和转述友好

**劣势**：
- ⚠️ 需要GPU加速（CPU较慢）
- ⚠️ 首次运行需下载模型（~400MB）

**实现方案**：
```python
def calculate_bertscore(summary: str, source: str, 
                       lang: str = 'zh', device: str = 'cuda') -> Dict[str, float]:
    """计算BERTScore"""
    try:
        from bert_score import score
        
        # 使用中文BERT模型
        P, R, F1 = score(
            [summary], 
            [source], 
            lang=lang,
            device=device,
            verbose=False
        )
        
        return {
            'bertscore_precision': P.item(),
            'bertscore_recall': R.item(),
            'bertscore_f1': F1.item()
        }
    except Exception as e:
        print(f"⚠️  BERTScore calculation failed: {e}")
        return {
            'bertscore_precision': None,
            'bertscore_recall': None,
            'bertscore_f1': None
        }
```

### 3.3 BARTScore ⚠️ 可行但成本高

**定义**：
- 基于 BART 模型的**双向生成概率打分**
- 同时衡量**忠实度与相关性**

**计算方法**：
1. 信息性：`P(summary|source)` - 摘要是否来自原文
2. 忠实性：`P(source|summary)` - 原文是否支持摘要

**范围**: (-∞, 0]，**数值越大表示质量越高**

**优势**：
- ✅ 同时衡量**忠实度与相关性**
- ✅ 是目前最接近人类评分的自动指标之一
- ✅ 项目中已有BARTScore工具

**劣势**：
- ⚠️ 计算成本极高（需要GPU）
- ⚠️ 需要加载大型BART模型（~1.5GB）
- ⚠️ 评估速度慢（每个样本~5-10秒）

**实现方案**：
```python
def calculate_bartscore(summary: str, source: str, 
                       device: str = 'cuda') -> Dict[str, float]:
    """计算BARTScore"""
    try:
        # 使用项目中的BARTScore工具
        from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
        
        # 初始化评分器
        bart_scorer = BARTScorer(
            device=device, 
            checkpoint='facebook/bart-large-cnn'
        )
        
        # 信息性：summary -> source
        info_score = bart_scorer.score([source], [summary])[0]
        
        # 忠实性：source -> summary
        faith_score = bart_scorer.score([summary], [source])[0]
        
        return {
            'bartscore_info': info_score,
            'bartscore_faith': faith_score,
            'bartscore_avg': (info_score + faith_score) / 2
        }
    except Exception as e:
        print(f"⚠️  BARTScore calculation failed: {e}")
        return {
            'bartscore_info': None,
            'bartscore_faith': None,
            'bartscore_avg': None
        }
```

**建议**：
- ⚠️ 作为可选高级指标
- ✅ 优先使用ROUGE-L和BERTScore
- 💡 如果计算资源充足且需要最高质量评估，可以使用

## 4. 辅助指标

### 4.1 压缩比 (Compression Ratio) ✅ 高度可行

**定义**：
- 摘要简洁性的量化指标
- 衡量信息压缩程度

**计算方法**：
```python
compression_ratio = len(summary) / len(source)
```

**范围**: [0, 1]，越小表示压缩越多

**优势**：
- ✅ 直接反映摘要是否**简洁、无冗余**
- ✅ 计算极其简单
- ✅ 可用于检测是否符合字数要求

**实现方案**：
```python
def calculate_compression_ratio(summary: str, source: str) -> float:
    """计算压缩比"""
    if len(source) == 0:
        return 0.0
    
    return len(summary) / len(source)
```

**应用**：
- 检测摘要是否过长或过短
- 评估简洁性
- 对比不同模型的压缩偏好

### 4.2 ROUGE-1、ROUGE-2 ✅ 高度可行

**定义**：
- ROUGE-1: 基于**Unigram（单词）**的重叠度
- ROUGE-2: 基于**Bigram（双词）**的重叠度

**作用**：
- 从**词汇层面**补充衡量信息召回率
- 与 ROUGE-L 共同构成完整 ROUGE 体系

**实现方案**：
```python
def calculate_rouge_1_2(summary: str, source: str) -> Dict[str, float]:
    """计算ROUGE-1和ROUGE-2"""
    try:
        from rouge import Rouge
        
        rouge = Rouge()
        scores = rouge.get_scores(summary, source)[0]
        
        return {
            'rouge_1_precision': scores['rouge-1']['p'],
            'rouge_1_recall': scores['rouge-1']['r'],
            'rouge_1_f1': scores['rouge-1']['f'],
            'rouge_2_precision': scores['rouge-2']['p'],
            'rouge_2_recall': scores['rouge-2']['r'],
            'rouge_2_f1': scores['rouge-2']['f']
        }
    except Exception as e:
        return {
            'rouge_1_f1': None,
            'rouge_2_f1': None
        }
```

### 4.3 字数符合度 ✅ 高度可行

**定义**：
- 评估生成摘要是否符合字数要求
- 检测是否在指定范围内

**实现方案**：
```python
def calculate_length_compliance(summary: str, 
                               min_length: int, 
                               max_length: int) -> Dict[str, float]:
    """计算字数符合度"""
    length = len(summary)
    
    # 是否在范围内
    in_range = 1.0 if min_length <= length <= max_length else 0.0
    
    # 偏离程度
    if length < min_length:
        deviation = (min_length - length) / min_length
    elif length > max_length:
        deviation = (length - max_length) / max_length
    else:
        deviation = 0.0
    
    return {
        'length': length,
        'in_range': in_range,
        'deviation': deviation,
        'compliance_score': max(0.0, 1.0 - deviation)
    }
```

### 4.4 信息密度 ✅ 可行

**定义**：
- 单位长度内包含的信息量
- 衡量摘要的信息效率

**实现方案**：
```python
def calculate_information_density(summary: str, source: str) -> float:
    """计算信息密度"""
    # 使用ROUGE-L召回率作为信息保留度
    rouge_scores = calculate_rouge_l(summary, source)
    recall = rouge_scores.get('rouge_l_recall', 0.0)
    
    # 信息密度 = 信息保留度 / 压缩比
    compression = calculate_compression_ratio(summary, source)
    
    if compression == 0:
        return 0.0
    
    density = recall / compression
    
    return density
```

**解释**：
- 高信息密度 = 用更少的字表达更多的信息
- 理想摘要应该有高信息密度

## 5. 推荐评估方案

### 5.1 核心指标组合

| 维度 | 指标 | 优先级 | 计算成本 | 可行性 |
|------|------|--------|----------|--------|
| 信息保留 | ROUGE-L F1 | ⭐⭐⭐ | 低 | ✅ 高 |
| 语义相似 | BERTScore F1 | ⭐⭐⭐ | 中 | ✅ 高 |
| 简洁性 | 压缩比 | ⭐⭐⭐ | 低 | ✅ 高 |
| 词汇覆盖 | ROUGE-1 F1 | ⭐⭐ | 低 | ✅ 高 |
| 短语覆盖 | ROUGE-2 F1 | ⭐⭐ | 低 | ✅ 高 |
| 字数符合 | Length Compliance | ⭐⭐ | 低 | ✅ 高 |
| 深度评估 | BARTScore | ⭐ | 极高 | ⚠️ 中 |

### 5.2 评估流程

```
1. 基础检查
   ├── 提取生成摘要
   ├── 加载原文
   └── 检查字数要求

2. 核心指标计算
   ├── ROUGE-L（结构完整性）
   ├── ROUGE-1/2（词汇覆盖）
   └── 压缩比（简洁性）

3. 语义指标计算
   ├── BERTScore（语义相似度）
   └── 信息密度（效率）

4. 辅助指标计算
   ├── 字数符合度
   └── 长度偏离度

5. 可选高级指标
   └── BARTScore（如果资源充足）

6. 结果汇总
   ├── 按模型汇总平均分数
   ├── 按问题分析难度
   └── 生成评估报告
```

### 5.3 评分权重建议

#### 方案1：信息保留优先（推荐）
```python
summary_quality_score = {
    'rouge_l_f1': 0.35,          # 35% - 结构完整性
    'bertscore_f1': 0.30,        # 30% - 语义相似度
    'rouge_1_f1': 0.15,          # 15% - 词汇覆盖
    'compression_ratio': 0.10,   # 10% - 简洁性（适中为好）
    'length_compliance': 0.10    # 10% - 字数符合
}
```

**理由**: 摘要的核心是保留关键信息，ROUGE-L和BERTScore最能反映这一点

#### 方案2：均衡评估
```python
summary_quality_score = {
    'rouge_l_f1': 0.25,
    'bertscore_f1': 0.25,
    'rouge_1_f1': 0.15,
    'rouge_2_f1': 0.15,
    'information_density': 0.20
}
```

#### 方案3：多维度呈现（强烈推荐）
不计算单一综合分数，保留所有原始指标：
```python
summary_quality_metrics = {
    'content': {
        'rouge_1_f1': float,
        'rouge_2_f1': float,
        'rouge_l_f1': float
    },
    'semantic': {
        'bertscore_precision': float,
        'bertscore_recall': float,
        'bertscore_f1': float
    },
    'conciseness': {
        'compression_ratio': float,
        'length': int,
        'in_range': bool,
        'information_density': float
    },
    'advanced': {
        'bartscore_info': float,      # 可选
        'bartscore_faith': float,     # 可选
        'bartscore_avg': float        # 可选
    }
}
```

**理由**: 保留完整信息，支持多角度分析，避免主观权重

## 6. 实现方案

### 6.1 评估器设计

```python
# data/analize/scripts/quality_evaluation/summary_evaluator.py

from typing import Dict, Optional
from .base_evaluator import BaseEvaluator


class SummaryEvaluator(BaseEvaluator):
    """文本摘要任务评估器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.use_bertscore = config.get('use_bertscore', True) if config else True
        self.use_bartscore = config.get('use_bartscore', False) if config else False
        self.device = config.get('device', 'cuda') if config else 'cuda'
        self.lang = config.get('lang', 'zh') if config else 'zh'
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估摘要质量
        
        Args:
            generated: 生成的摘要
            reference: 原文（必需）
            context: 额外上下文（可包含字数要求）
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or not reference:
            return self._get_zero_scores()
        
        # 1. ROUGE 分数
        rouge_scores = self._calculate_rouge(generated, reference)
        scores.update(rouge_scores)
        
        # 2. BERTScore（可选）
        if self.use_bertscore:
            bertscore_results = self._calculate_bertscore(generated, reference)
            scores.update(bertscore_results)
        
        # 3. 压缩比
        scores['compression_ratio'] = self._calculate_compression_ratio(
            generated, reference
        )
        
        # 4. 字数符合度
        if context and 'min_length' in context and 'max_length' in context:
            length_scores = self._calculate_length_compliance(
                generated, 
                context['min_length'], 
                context['max_length']
            )
            scores.update(length_scores)
        else:
            scores['length'] = len(generated)
            scores['in_range'] = None
            scores['compliance_score'] = None
        
        # 5. 信息密度
        if 'rouge_l_recall' in scores and scores['compression_ratio'] > 0:
            scores['information_density'] = (
                scores['rouge_l_recall'] / scores['compression_ratio']
            )
        else:
            scores['information_density'] = None
        
        # 6. BARTScore（可选，成本高）
        if self.use_bartscore:
            bartscore_results = self._calculate_bartscore(generated, reference)
            scores.update(bartscore_results)

    def _calculate_rouge(self, summary: str, source: str) -> Dict[str, float]:
        """计算ROUGE分数"""
        try:
            from rouge import Rouge
            
            rouge = Rouge()
            scores = rouge.get_scores(summary, source)[0]
            
            return {
                'rouge_1_precision': scores['rouge-1']['p'],
                'rouge_1_recall': scores['rouge-1']['r'],
                'rouge_1_f1': scores['rouge-1']['f'],
                'rouge_2_precision': scores['rouge-2']['p'],
                'rouge_2_recall': scores['rouge-2']['r'],
                'rouge_2_f1': scores['rouge-2']['f'],
                'rouge_l_precision': scores['rouge-l']['p'],
                'rouge_l_recall': scores['rouge-l']['r'],
                'rouge_l_f1': scores['rouge-l']['f']
            }
        except Exception as e:
            print(f"⚠️  ROUGE calculation failed: {e}")
            return {
                'rouge_1_f1': None,
                'rouge_2_f1': None,
                'rouge_l_f1': None
            }
    
    def _calculate_bertscore(self, summary: str, source: str) -> Dict[str, float]:
        """计算BERTScore"""
        try:
            from bert_score import score
            
            P, R, F1 = score(
                [summary], 
                [source], 
                lang=self.lang,
                device=self.device,
                verbose=False
            )
            
            return {
                'bertscore_precision': P.item(),
                'bertscore_recall': R.item(),
                'bertscore_f1': F1.item()
            }
        except Exception as e:
            print(f"⚠️  BERTScore calculation failed: {e}")
            return {
                'bertscore_precision': None,
                'bertscore_recall': None,
                'bertscore_f1': None
            }
    
    def _calculate_bartscore(self, summary: str, source: str) -> Dict[str, float]:
        """计算BARTScore"""
        try:
            from tools.thesis_reproduction.BARTScore.bart_score import BARTScorer
            
            bart_scorer = BARTScorer(
                device=self.device,
                checkpoint='facebook/bart-large-cnn'
            )
            
            info_score = bart_scorer.score([source], [summary])[0]
            faith_score = bart_scorer.score([summary], [source])[0]
            
            return {
                'bartscore_info': info_score,
                'bartscore_faith': faith_score,
                'bartscore_avg': (info_score + faith_score) / 2
            }
        except Exception as e:
            print(f"⚠️  BARTScore calculation failed: {e}")
            return {
                'bartscore_info': None,
                'bartscore_faith': None,
                'bartscore_avg': None
            }
    
    def _calculate_compression_ratio(self, summary: str, source: str) -> float:
        """计算压缩比"""
        if len(source) == 0:
            return 0.0
        return len(summary) / len(source)
    
    def _calculate_length_compliance(self, summary: str, 
                                    min_length: int, 
                                    max_length: int) -> Dict[str, float]:
        """计算字数符合度"""
        length = len(summary)
        in_range = 1.0 if min_length <= length <= max_length else 0.0
        
        if length < min_length:
            deviation = (min_length - length) / min_length
        elif length > max_length:
            deviation = (length - max_length) / max_length
        else:
            deviation = 0.0
        
        return {
            'length': length,
            'in_range': in_range,
            'deviation': deviation,
            'compliance_score': max(0.0, 1.0 - deviation)
        }
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'rouge_1_f1': 0.0,
            'rouge_2_f1': 0.0,
            'rouge_l_f1': 0.0,
            'bertscore_f1': 0.0,
            'compression_ratio': 0.0,
            'length': 0,
            'in_range': 0.0,
            'information_density': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'content': ['rouge_1_f1', 'rouge_2_f1', 'rouge_l_f1'],
            'semantic': ['bertscore_precision', 'bertscore_recall', 'bertscore_f1'],
            'conciseness': ['compression_ratio', 'length', 'in_range', 'information_density'],
            'advanced': ['bartscore_info', 'bartscore_faith', 'bartscore_avg']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向(True=越大越好)"""
        return {
            'rouge_1_f1': True,
            'rouge_2_f1': True,
            'rouge_l_f1': True,
            'bertscore_precision': True,
            'bertscore_recall': True,
            'bertscore_f1': True,
            'compression_ratio': False,  # 适中为好，但简化为越小越好
            'in_range': True,
            'compliance_score': True,
            'information_density': True,
            'bartscore_info': True,
            'bartscore_faith': True,
            'bartscore_avg': True
        }
```

### 6.2 原文与字数要求配置

```python
# 原文配置
SUMMARY_SOURCE_TEXTS = {
    'q01': """云计算是一种基于互联网的计算方式，通过这种方式，共享的软硬件资源和信息可以按需提供给计算机和其他设备。云计算依赖资源的共享以达成规模经济，类似基础设施（如电力网）。服务提供商整合大量资源供多个用户使用，用户可以轻易地请求（租借）更多资源，并随时调整使用量，将不需要的资源释放回整个架构，因此用户不需要因短暂的需求高峰而购买大量资源，仅需提升租用量，需求降低时便退租。""",
    
    'q02': """物联网（Internet of Things，IoT）是互联网、传统电信网等信息承载体，让所有能行使独立功能的普通物体实现互联互通的网络。物联网将现实世界数字化，应用范围十分广泛。物联网拉近分散的信息，统整物与物的数字信息，物联网的应用领域主要包括运输和物流、工业制造、健康医疗、智能环境（家庭、办公、工厂）等，具有十分广阔的市场和应用前景。""",
    
    'q03': """深度学习是机器学习的一个分支，它基于人工神经网络进行学习。深度学习模型由多层神经网络组成，每一层都会对输入数据进行特征提取和转换。通过大量数据的训练，深度学习模型能够自动学习数据的内在规律和表示层次，从而实现对复杂模式的识别。近年来，深度学习在计算机视觉、自然语言处理、语音识别等领域取得了突破性进展，推动了人工智能技术的快速发展。""",
    
    'q04': """人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。人工智能可以对人的意识、思维的信息过程进行模拟。人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。""",
    
    'q05': """区块链是一个分布式数据库，通过去中心化和去信任的方式集体维护一个可靠数据库。区块链技术是比特币的底层技术，比特币在没有任何中心化机构运营和管理的情况下，多年运行非常稳定，没有出现过任何问题。区块链的核心优势是去中心化，能够通过运用数据加密、时间戳、分布式共识和经济激励等手段，在节点无需互相信任的分布式系统中实现基于去中心化信用的点对点交易、协调与协作。"""
}

# 字数要求配置
SUMMARY_LENGTH_REQUIREMENTS = {
    'q01': {'min': 50, 'max': 70},
    'q02': {'min': 40, 'max': 60},
    'q03': {'min': 40, 'max': 60},
    'q04': {'min': 50, 'max': 80},
    'q05': {'min': 40, 'max': 60}
}
```

### 6.3 批量评估脚本

```python
# data/analize/scripts/evaluate_summary_quality.py

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from datetime import datetime
from quality_evaluation.summary_evaluator import SummaryEvaluator

# 导入配置
from summary_config import SUMMARY_SOURCE_TEXTS, SUMMARY_LENGTH_REQUIREMENTS


def evaluate_summary_quality(data_dir: Path, output_dir: Path, 
                             use_bertscore: bool = True,
                             use_bartscore: bool = False):
    """评估文本摘要任务质量"""
    
    print("\n" + "="*60)
    print("📝 Summary Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/summary/summary_responses.csv'
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    config = {
        'use_bertscore': use_bertscore,
        'use_bartscore': use_bartscore,
        'device': 'cuda',
        'lang': 'zh'
    }
    evaluator = SummaryEvaluator(config)
    
    # 评估每个模型的每个响应
    results = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating models"):
        model = row['model']
        
        for col in df.columns:
            if col == 'model':
                continue
            
            response = row[col]
            
            if pd.isna(response) or len(str(response).strip()) == 0:
                continue
            
            # 获取原文和字数要求
            source_text = SUMMARY_SOURCE_TEXTS.get(col)
            length_req = SUMMARY_LENGTH_REQUIREMENTS.get(col)
            
            if source_text is None:
                print(f"⚠️  No source text for {col}")
                continue
            
            # 构建上下文
            context = {}
            if length_req:
                context['min_length'] = length_req['min']
                context['max_length'] = length_req['max']
            
            # 评估质量
            scores = evaluator.evaluate(
                str(response), 
                reference=source_text,
                context=context
            )
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                'source_length': len(source_text),
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'summary_quality_scores.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
    # 生成报告
    generate_report(results_df, output_dir)
    
    return results_df


def generate_summary_stats(df: pd.DataFrame, output_dir: Path):
    """生成汇总统计"""
    
    print(f"\n📊 Generating summary statistics...")
    
    # 按模型汇总
    metric_cols = [col for col in df.columns 
                   if col not in ['model', 'question_id', 'source_length'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'summary_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'rouge_l_f1' in df.columns:
        print(f"\n🏆 Top 3 Models by ROUGE-L F1:")
        top_models = df.groupby('model')['rouge_l_f1'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")
    
    if 'bertscore_f1' in df.columns:
        print(f"\n🎯 Top 3 Models by BERTScore F1:")
        top_models = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.4f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    
    report_file = output_dir / 'summary_quality_report.md'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 文本摘要质量评估报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 1. 评估概览\n\n")
        f.write(f"- 评估模型数: {df['model'].nunique()}\n")
        f.write(f"- 评估问题数: {df['question_id'].nunique()}\n")
        f.write(f"- 总评估次数: {len(df)}\n\n")
        
        f.write("## 2. 核心指标排名\n\n")
        
        # ROUGE-L排名
        if 'rouge_l_f1' in df.columns:
            f.write("### 2.1 ROUGE-L F1 排名\n\n")
            rouge_ranking = df.groupby('model')['rouge_l_f1'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(rouge_ranking.items(), 1):
                f.write(f"{rank}. **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # BERTScore排名
        if 'bertscore_f1' in df.columns:
            f.write("### 2.2 BERTScore F1 排名\n\n")
            bert_ranking = df.groupby('model')['bertscore_f1'].mean().sort_values(ascending=False)
            for rank, (model, score) in enumerate(bert_ranking.items(), 1):
                f.write(f"{rank}. **{model}**: {score:.4f}\n")
            f.write("\n")
        
        # 压缩比分析
        if 'compression_ratio' in df.columns:
            f.write("### 2.3 压缩比分析\n\n")
            comp_stats = df.groupby('model')['compression_ratio'].mean().sort_values()
            for model, ratio in comp_stats.items():
                f.write(f"- **{model}**: {ratio:.3f}\n")
            f.write("\n")
        
        # 字数符合度
        if 'in_range' in df.columns:
            f.write("### 2.4 字数符合度\n\n")
            compliance = df.groupby('model')['in_range'].mean().sort_values(ascending=False)
            for model, rate in compliance.items():
                f.write(f"- **{model}**: {rate:.1%}\n")
            f.write("\n")
        
        f.write("## 3. 详细分析\n\n")
        f.write("详细数据请参考 `summary_quality_scores.csv` 和 `summary_quality_summary.csv`\n")
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估文本摘要质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/summary_quality',
                       help='输出目录')
    parser.add_argument('--use-bertscore', action='store_true', default=True,
                       help='是否使用BERTScore（默认：是）')
    parser.add_argument('--use-bartscore', action='store_true', default=False,
                       help='是否使用BARTScore（默认：否，成本高）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_summary_quality(
        data_dir, 
        output_dir,
        use_bertscore=args.use_bertscore,
        use_bartscore=args.use_bartscore
    )
```

## 7. 依赖安装

### 7.1 必需依赖

```bash
# 激活环境
conda activate bartscore

# 安装基础依赖
pip install rouge pandas numpy tqdm

# 安装BERTScore（推荐）
pip install bert-score transformers torch
```

### 7.2 可选依赖（BARTScore）

```bash
# 如果需要使用BARTScore
# 确保项目中的BARTScore工具已配置
# 参考：tools/thesis_reproduction/BARTScore/
```

### 7.3 模型下载

首次运行时会自动下载以下模型：

- **BERT中文模型**（用于BERTScore）
  - 模型：`bert-base-chinese`
  - 大小：约400MB
  - 缓存位置：`~/.cache/huggingface/`

- **BART模型**（可选，用于BARTScore）
  - 模型：`facebook/bart-large-cnn`
  - 大小：约1.5GB
  - 需要GPU加速

## 8. 运行指南

### 8.1 快速开始

```bash
# 1. 激活环境
conda activate bartscore
set PYTHONUTF8=1

# 2. 运行评估（仅ROUGE和BERTScore）
cd data/analize/scripts
python evaluate_summary_quality.py

# 3. 运行评估（包含BARTScore，需要GPU）
python evaluate_summary_quality.py --use-bartscore

# 4. 查看结果
type ..\results\summary_quality\summary_quality_scores.csv
```

### 8.2 预期输出

```
data/analize/results/summary_quality/
├── summary_quality_scores.csv       # 详细评分
│   ├── model
│   ├── question_id
│   ├── rouge_1_f1
│   ├── rouge_2_f1
│   ├── rouge_l_f1
│   ├── bertscore_f1
│   ├── compression_ratio
│   ├── length
│   ├── in_range
│   └── information_density
├── summary_quality_summary.csv      # 汇总统计
└── summary_quality_report.md        # 评估报告
```

### 8.3 性能估算

基于当前硬件配置（RTX 4060 8GB）：

**不使用BARTScore（推荐）**：
- 每个响应评估时间：~1-2秒
- 总评估时间：~2-5分钟（12个模型 × 5个问题）
- GPU显存占用：~2GB（BERT模型）

**使用BARTScore（可选）**：
- 每个响应评估时间：~5-10秒
- 总评估时间：~10-20分钟
- GPU显存占用：~4-5GB（BERT + BART模型）

## 9. 指标解释与应用

### 9.1 指标含义

#### ROUGE-L F1
- **含义**：基于最长公共子序列的F1分数
- **范围**：[0, 1]
- **解释**：
  - 0.6-1.0：信息保留完整，结构合理
  - 0.4-0.6：信息保留中等
  - 0.0-0.4：信息丢失严重
- **应用**：评估摘要的结构完整性和信息保留度

#### BERTScore F1
- **含义**：基于BERT的语义相似度
- **范围**：[0, 1]
- **解释**：
  - 0.8-1.0：语义高度相似
  - 0.6-0.8：语义较相似
  - 0.0-0.6：语义差异较大
- **应用**：评估摘要的语义正确性

#### 压缩比
- **含义**：摘要长度/原文长度
- **范围**：[0, 1]
- **解释**：
  - 0.2-0.4：合理压缩
  - <0.2：过度压缩，可能丢失信息
  - >0.4：压缩不足，不够简洁
- **应用**：评估摘要的简洁性

#### 信息密度
- **含义**：单位长度内的信息量
- **计算**：ROUGE-L召回率 / 压缩比
- **解释**：越高表示用更少的字表达更多信息
- **应用**：评估摘要的信息效率

### 9.2 综合评分建议

#### 方案1：加权平均
```python
def calculate_summary_score(metrics):
    """计算摘要综合分数"""
    score = (
        0.35 * metrics['rouge_l_f1'] +
        0.30 * metrics['bertscore_f1'] +
        0.15 * metrics['rouge_1_f1'] +
        0.10 * (1 - abs(metrics['compression_ratio'] - 0.3)) +  # 0.3为理想压缩比
        0.10 * metrics.get('compliance_score', 0.5)
    )
    return score
```

#### 方案2：多维度呈现（推荐）
保留所有原始指标，支持不同应用场景的灵活分析

## 10. 总结

### 10.1 方法可行性总结

| 方法 | 可行性 | 推荐度 | 理由 |
|------|--------|--------|------|
| **ROUGE-L** | ✅ 高 | ⭐⭐⭐ | 经典指标、计算快、效果好 |
| **ROUGE-1/2** | ✅ 高 | ⭐⭐⭐ | 补充词汇覆盖度 |
| **BERTScore** | ✅ 高 | ⭐⭐⭐ | 语义评估、对改写友好 |
| **压缩比** | ✅ 高 | ⭐⭐⭐ | 简单有效、评估简洁性 |
| **字数符合度** | ✅ 高 | ⭐⭐ | 检测任务完成度 |
| **信息密度** | ✅ 高 | ⭐⭐ | 评估信息效率 |
| **BARTScore** | ⚠️ 中 | ⭐ | 效果最好但成本极高 |

### 10.2 最终推荐方案

#### 核心指标组合（必须实现）
- ROUGE-L F1（结构完整性）
- ROUGE-1/2 F1（词汇覆盖）
- BERTScore F1（语义相似度）
- 压缩比（简洁性）
- 字数符合度（任务完成度）

#### 可选扩展（资源充足时）
- BARTScore（最高质量评估）
- 信息密度（效率分析）

### 10.3 实施建议

#### 阶段1：基础实现（1-2天）
1. ✅ 实现ROUGE计算
2. ✅ 实现压缩比和字数符合度
3. ✅ 批量评估脚本
4. ✅ 结果保存和汇总

#### 阶段2：语义评估（1-2天）
1. ⏳ 集成BERTScore
2. ⏳ 模型下载和缓存管理
3. ⏳ GPU加速优化
4. ⏳ 错误处理和日志

#### 阶段3：高级评估（可选，2-3天）
1. ⏳ 集成BARTScore
2. ⏳ 性能优化
3. ⏳ 可视化分析

### 10.4 预期成果

- 识别信息保留最完整的模型
- 发现简洁性与信息保留的权衡关系
- 检测字数符合度问题
- 为模型选择提供数据支持

---

**文档版本**: v1.0  
**创建日期**: 2026-03-05  
**作者**: Kiro AI Assistant  
**状态**: 设计完成，待实施
