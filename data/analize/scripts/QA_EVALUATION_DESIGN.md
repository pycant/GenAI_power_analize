# 问答任务质量评估方法设计

## 1. 评估目标

问答任务的核心评估维度:
- **响应完整性 (Response Completeness)**: 是否给出了答案
- **响应质量 (Response Quality)**: 答案的详细程度和结构
- **技术准确性 (Technical Accuracy)**: 技术术语使用的合理性
- **置信度 (Confidence)**: 答案的确定性程度

## 2. 数据特征分析

### 2.1 任务类型

基于提供的QA问题,任务类型为:
- **技术问答**: 计算机科学、算法、网络安全等专业问题
- **概念解释**: 需要解释技术概念和工具
- **选择题**: 部分问题可能有多个选项

### 2.2 答案格式

从样本数据观察到的答案格式:
- **详细推理过程**: 模型展示思考过程
- **逐步分析**: 分步骤解答问题
- **技术术语**: 包含专业术语和概念
- **不确定性表达**: 部分答案包含"I think", "probably"等

### 2.3 评估挑战

**核心挑战**: 没有标准答案
- 无法使用Exact Match或F1 Score
- 需要基于响应质量本身进行评估
- 需要评估技术内容的合理性


## 3. 评估方法设计

### 3.1 核心指标

#### 3.1.1 Response Completeness (响应完整性) ✅ 高度可行

**定义**:
- 评估响应是否包含实质性答案
- 检测是否完整回答了问题

**实现方案**:
```python
def calculate_response_completeness(text: str) -> Dict[str, float]:
    """
    计算响应完整性
    
    Returns:
        Dict with:
        - has_answer: 是否包含答案
        - answer_length: 答案长度
        - has_conclusion: 是否有结论
    """
    scores = {}
    
    # 1. 基础检查
    scores['has_answer'] = 1.0 if len(text.strip()) > 50 else 0.0
    scores['answer_length'] = len(text)
    
    # 2. 检测结论性语句
    conclusion_patterns = [
        r'(?:answer|result|conclusion|therefore|thus|so)\s+is',
        r'(?:答案|结论|因此|所以)\s*(?:是|为)',
        r'the correct answer',
        r'in summary',
        r'to summarize'
    ]
    
    has_conclusion = any(
        re.search(pattern, text, re.IGNORECASE) 
        for pattern in conclusion_patterns
    )
    scores['has_conclusion'] = 1.0 if has_conclusion else 0.0
    
    return scores
```

**优势**:
- ✅ 无需外部模型
- ✅ 计算快速
- ✅ 客观可量化



#### 3.1.2 Technical Term Density (技术术语密度) ✅ 高度可行

**定义**:
- 评估响应中技术术语的使用频率
- 反映答案的专业性

**实现方案**:
```python
def calculate_technical_term_density(text: str, domain: str = 'cs') -> float:
    """
    计算技术术语密度
    
    Args:
        text: 响应文本
        domain: 领域 ('cs' for computer science)
    
    Returns:
        float: 技术术语密度 [0, 1]
    """
    # 计算机科学相关技术术语
    cs_terms = {
        'algorithm', 'complexity', 'runtime', 'worst-case', 'average-case',
        'hash', 'table', 'array', 'linked', 'list', 'tree', 'graph',
        'sort', 'search', 'binary', 'quicksort', 'mergesort',
        'network', 'protocol', 'packet', 'encryption', 'authentication',
        'security', 'vulnerability', 'firewall', 'port', 'scan',
        'boolean', 'operator', 'logic', 'gate', 'circuit',
        'nand', 'nor', 'xor', 'and', 'or', 'not',
        'ipsec', 'vpn', 'ssl', 'tls', 'tcp', 'udp', 'ip'
    }
    
    # 转小写并分词
    words = text.lower().split()
    
    # 统计技术术语
    term_count = sum(1 for word in words if word in cs_terms)
    
    # 计算密度
    if len(words) == 0:
        return 0.0
    
    density = term_count / len(words)
    
    # 归一化到合理范围 (0-0.3为正常范围)
    normalized_density = min(density / 0.3, 1.0)
    
    return normalized_density
```

**优势**:
- ✅ 反映专业性
- ✅ 无需外部模型
- ✅ 可扩展术语库



#### 3.1.3 Confidence Score (置信度评分) ✅ 高度可行

**定义**:
- 评估答案的确定性程度
- 检测不确定性表达

**实现方案**:
```python
def calculate_confidence_score(text: str) -> float:
    """
    计算答案置信度
    
    Returns:
        float: [0, 1]，越高表示越确定
    """
    # 不确定性关键词
    uncertainty_keywords = [
        'i think', 'probably', 'maybe', 'perhaps', 'might',
        'could be', 'not sure', 'unclear', 'uncertain',
        'i believe', 'seems like', 'appears to'
    ]
    
    # 确定性关键词
    certainty_keywords = [
        'definitely', 'certainly', 'clearly', 'obviously',
        'the answer is', 'the correct answer', 'must be',
        'always', 'never', 'exactly'
    ]
    
    text_lower = text.lower()
    
    # 统计不确定性表达
    uncertainty_count = sum(
        1 for keyword in uncertainty_keywords 
        if keyword in text_lower
    )
    
    # 统计确定性表达
    certainty_count = sum(
        1 for keyword in certainty_keywords 
        if keyword in text_lower
    )
    
    # 计算置信度
    # 基础分数: 0.5
    # 每个确定性表达 +0.1
    # 每个不确定性表达 -0.1
    confidence = 0.5 + (certainty_count * 0.1) - (uncertainty_count * 0.1)
    
    # 限制在 [0, 1]
    confidence = max(0.0, min(1.0, confidence))
    
    return confidence
```

**优势**:
- ✅ 反映答案质量
- ✅ 简单直观
- ✅ 无需外部模型



### 3.2 辅助指标

#### 3.2.1 Structure Quality (结构质量) ✅ 可行

**定义**:
- 评估答案的组织结构
- 检测是否有清晰的段落和逻辑

**实现方案**:
```python
def calculate_structure_quality(text: str) -> Dict[str, float]:
    """
    评估答案结构质量
    
    Returns:
        Dict with:
        - paragraph_count: 段落数量
        - avg_paragraph_length: 平均段落长度
        - has_enumeration: 是否有列举
    """
    scores = {}
    
    # 1. 段落分析
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
    scores['paragraph_count'] = len(paragraphs)
    
    if paragraphs:
        avg_length = sum(len(p) for p in paragraphs) / len(paragraphs)
        scores['avg_paragraph_length'] = avg_length
    else:
        scores['avg_paragraph_length'] = 0
    
    # 2. 检测列举/编号
    enumeration_patterns = [
        r'(?:first|second|third|finally)',
        r'(?:1\.|2\.|3\.)',
        r'(?:a\)|b\)|c\))',
        r'(?:首先|其次|最后)'
    ]
    
    has_enumeration = any(
        re.search(pattern, text, re.IGNORECASE) 
        for pattern in enumeration_patterns
    )
    scores['has_enumeration'] = 1.0 if has_enumeration else 0.0
    
    return scores
```

#### 3.2.2 Reasoning Depth (推理深度) ✅ 可行

**定义**:
- 评估推理过程的深度
- 检测是否有逐步分析

**实现方案**:
```python
def calculate_reasoning_depth(text: str) -> Dict[str, float]:
    """
    评估推理深度
    
    Returns:
        Dict with:
        - has_reasoning: 是否包含推理
        - reasoning_steps: 推理步骤数
        - has_examples: 是否有例子
    """
    scores = {}
    
    # 1. 推理关键词
    reasoning_keywords = [
        'because', 'since', 'therefore', 'thus', 'so',
        'if', 'then', 'when', 'however', 'but',
        '因为', '所以', '因此', '如果', '那么'
    ]
    
    has_reasoning = any(
        keyword in text.lower() 
        for keyword in reasoning_keywords
    )
    scores['has_reasoning'] = 1.0 if has_reasoning else 0.0
    
    # 2. 推理步骤数 (基于句子)
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    scores['reasoning_steps'] = len(sentences)
    
    # 3. 检测例子
    example_patterns = [
        r'for example', r'for instance', r'such as',
        r'例如', r'比如', r'举例'
    ]
    
    has_examples = any(
        re.search(pattern, text, re.IGNORECASE) 
        for pattern in example_patterns
    )
    scores['has_examples'] = 1.0 if has_examples else 0.0
    
    return scores
```



## 4. 推荐评估方案

### 4.1 核心指标(必须实现)

| 维度 | 指标 | 优先级 | 计算成本 | 可行性 |
|------|------|--------|----------|--------|
| 完整性 | Has Answer | ⭐⭐⭐ | 低 | ✅ 高 |
| 完整性 | Has Conclusion | ⭐⭐⭐ | 低 | ✅ 高 |
| 专业性 | Technical Term Density | ⭐⭐⭐ | 低 | ✅ 高 |
| 置信度 | Confidence Score | ⭐⭐ | 低 | ✅ 高 |
| 结构 | Has Enumeration | ⭐⭐ | 低 | ✅ 高 |
| 推理 | Has Reasoning | ⭐⭐ | 低 | ✅ 高 |

### 4.2 评估流程

```
1. 基础检查
   ├── 检测是否有答案
   ├── 计算答案长度
   └── 检测结论性语句

2. 专业性评估
   ├── 统计技术术语
   ├── 计算术语密度
   └── 评估专业程度

3. 置信度评估
   ├── 检测不确定性表达
   ├── 检测确定性表达
   └── 计算置信度分数

4. 结构与推理评估
   ├── 分析段落结构
   ├── 检测推理关键词
   └── 统计推理步骤
```

### 4.3 评分方案

#### 方案1: 多维度呈现(推荐)
不计算单一综合分数,保留多维度指标:
```python
qa_quality_metrics = {
    'completeness': {
        'has_answer': bool,
        'answer_length': int,
        'has_conclusion': bool,
    },
    'professionalism': {
        'technical_term_density': float,
        'technical_term_count': int,
    },
    'confidence': {
        'confidence_score': float,
        'uncertainty_count': int,
        'certainty_count': int,
    },
    'structure': {
        'paragraph_count': int,
        'has_enumeration': bool,
    },
    'reasoning': {
        'has_reasoning': bool,
        'reasoning_steps': int,
        'has_examples': bool,
    }
}
```

#### 方案2: 综合评分(可选)
```python
qa_quality_score = {
    'completeness': 0.3,        # 30% - 是否完整回答
    'technical_density': 0.3,   # 30% - 专业性
    'confidence': 0.2,          # 20% - 置信度
    'structure': 0.2            # 20% - 结构质量
}
```



## 5. 实现方案

### 5.1 评估器设计

```python
# data/analize/scripts/quality_evaluation/qa_evaluator.py

import re
from typing import Dict, Set
from .base_evaluator import BaseEvaluator


class QAEvaluator(BaseEvaluator):
    """问答任务评估器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.domain = config.get('domain', 'cs') if config else 'cs'
        self._load_technical_terms()
    
    def _load_technical_terms(self):
        """加载技术术语库"""
        # 计算机科学术语
        self.cs_terms = {
            'algorithm', 'complexity', 'runtime', 'worst-case', 'average-case',
            'hash', 'table', 'array', 'linked', 'list', 'tree', 'graph',
            'sort', 'search', 'binary', 'quicksort', 'mergesort', 'heapsort',
            'network', 'protocol', 'packet', 'encryption', 'authentication',
            'security', 'vulnerability', 'firewall', 'port', 'scan', 'nmap',
            'boolean', 'operator', 'logic', 'gate', 'circuit',
            'nand', 'nor', 'xor', 'and', 'or', 'not',
            'ipsec', 'vpn', 'ssl', 'tls', 'tcp', 'udp', 'ip', 'http',
            'data', 'structure', 'pointer', 'memory', 'stack', 'queue',
            'recursion', 'iteration', 'loop', 'function', 'class', 'object'
        }
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估问答质量
        
        Args:
            generated: 生成的答案文本
            reference: 标准答案(可选,QA任务通常没有)
            context: 额外上下文
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or len(generated.strip()) == 0:
            return self._get_zero_scores()
        
        # 1. 响应完整性
        completeness_scores = self._calculate_completeness(generated)
        scores.update(completeness_scores)
        
        # 2. 技术术语密度
        scores['technical_term_density'] = self._calculate_technical_density(generated)
        scores['technical_term_count'] = self._count_technical_terms(generated)
        
        # 3. 置信度
        scores['confidence_score'] = self._calculate_confidence(generated)
        scores['uncertainty_count'] = self._count_uncertainty(generated)
        scores['certainty_count'] = self._count_certainty(generated)
        
        # 4. 结构质量
        structure_scores = self._calculate_structure(generated)
        scores.update(structure_scores)
        
        # 5. 推理深度
        reasoning_scores = self._calculate_reasoning(generated)
        scores.update(reasoning_scores)
        
        return scores
    
    def _calculate_completeness(self, text: str) -> Dict[str, float]:
        """计算响应完整性"""
        scores = {}
        
        # 是否有答案
        scores['has_answer'] = 1.0 if len(text.strip()) > 50 else 0.0
        scores['answer_length'] = len(text)
        
        # 检测结论
        conclusion_patterns = [
            r'(?:answer|result|conclusion|therefore|thus|so)\s+is',
            r'(?:答案|结论|因此|所以)\s*(?:是|为)',
            r'the correct answer',
            r'in summary',
            r'to summarize'
        ]
        
        has_conclusion = any(
            re.search(pattern, text, re.IGNORECASE) 
            for pattern in conclusion_patterns
        )
        scores['has_conclusion'] = 1.0 if has_conclusion else 0.0
        
        return scores
    
    def _calculate_technical_density(self, text: str) -> float:
        """计算技术术语密度"""
        words = text.lower().split()
        
        if len(words) == 0:
            return 0.0
        
        term_count = sum(1 for word in words if word in self.cs_terms)
        density = term_count / len(words)
        
        # 归一化 (0-0.3为正常范围)
        normalized_density = min(density / 0.3, 1.0)
        
        return normalized_density
    
    def _count_technical_terms(self, text: str) -> int:
        """统计技术术语数量"""
        words = text.lower().split()
        return sum(1 for word in words if word in self.cs_terms)
    
    def _calculate_confidence(self, text: str) -> float:
        """计算置信度"""
        text_lower = text.lower()
        
        uncertainty_count = self._count_uncertainty(text_lower)
        certainty_count = self._count_certainty(text_lower)
        
        # 基础分数0.5 + 确定性0.1 - 不确定性0.1
        confidence = 0.5 + (certainty_count * 0.1) - (uncertainty_count * 0.1)
        
        return max(0.0, min(1.0, confidence))
    
    def _count_uncertainty(self, text: str) -> int:
        """统计不确定性表达"""
        uncertainty_keywords = [
            'i think', 'probably', 'maybe', 'perhaps', 'might',
            'could be', 'not sure', 'unclear', 'uncertain',
            'i believe', 'seems like', 'appears to'
        ]
        
        return sum(1 for keyword in uncertainty_keywords if keyword in text)
    
    def _count_certainty(self, text: str) -> int:
        """统计确定性表达"""
        certainty_keywords = [
            'definitely', 'certainly', 'clearly', 'obviously',
            'the answer is', 'the correct answer', 'must be',
            'always', 'never', 'exactly'
        ]
        
        return sum(1 for keyword in certainty_keywords if keyword in text)
    
    def _calculate_structure(self, text: str) -> Dict[str, float]:
        """计算结构质量"""
        scores = {}
        
        # 段落分析
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
        scores['paragraph_count'] = len(paragraphs)
        
        if paragraphs:
            avg_length = sum(len(p) for p in paragraphs) / len(paragraphs)
            scores['avg_paragraph_length'] = avg_length
        else:
            scores['avg_paragraph_length'] = 0
        
        # 检测列举
        enumeration_patterns = [
            r'(?:first|second|third|finally)',
            r'(?:1\.|2\.|3\.)',
            r'(?:a\)|b\)|c\))',
            r'(?:首先|其次|最后)'
        ]
        
        has_enumeration = any(
            re.search(pattern, text, re.IGNORECASE) 
            for pattern in enumeration_patterns
        )
        scores['has_enumeration'] = 1.0 if has_enumeration else 0.0
        
        return scores
    
    def _calculate_reasoning(self, text: str) -> Dict[str, float]:
        """计算推理深度"""
        scores = {}
        
        # 推理关键词
        reasoning_keywords = [
            'because', 'since', 'therefore', 'thus', 'so',
            'if', 'then', 'when', 'however', 'but',
            '因为', '所以', '因此', '如果', '那么'
        ]
        
        has_reasoning = any(
            keyword in text.lower() 
            for keyword in reasoning_keywords
        )
        scores['has_reasoning'] = 1.0 if has_reasoning else 0.0
        
        # 推理步骤数
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        scores['reasoning_steps'] = len(sentences)
        
        # 检测例子
        example_patterns = [
            r'for example', r'for instance', r'such as',
            r'例如', r'比如', r'举例'
        ]
        
        has_examples = any(
            re.search(pattern, text, re.IGNORECASE) 
            for pattern in example_patterns
        )
        scores['has_examples'] = 1.0 if has_examples else 0.0
        
        return scores
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'has_answer': 0.0,
            'answer_length': 0,
            'has_conclusion': 0.0,
            'technical_term_density': 0.0,
            'technical_term_count': 0,
            'confidence_score': 0.0,
            'uncertainty_count': 0,
            'certainty_count': 0,
            'paragraph_count': 0,
            'avg_paragraph_length': 0,
            'has_enumeration': 0.0,
            'has_reasoning': 0.0,
            'reasoning_steps': 0,
            'has_examples': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'completeness': ['has_answer', 'answer_length', 'has_conclusion'],
            'professionalism': ['technical_term_density', 'technical_term_count'],
            'confidence': ['confidence_score', 'uncertainty_count', 'certainty_count'],
            'structure': ['paragraph_count', 'avg_paragraph_length', 'has_enumeration'],
            'reasoning': ['has_reasoning', 'reasoning_steps', 'has_examples']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向"""
        return {
            'has_answer': True,
            'answer_length': True,
            'has_conclusion': True,
            'technical_term_density': True,
            'technical_term_count': True,
            'confidence_score': True,
            'uncertainty_count': False,  # 越少越好
            'certainty_count': True,
            'paragraph_count': True,
            'has_enumeration': True,
            'has_reasoning': True,
            'reasoning_steps': True,
            'has_examples': True
        }
```



## 6. 批量评估脚本

```python
# data/analize/scripts/evaluate_qa_quality.py

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from quality_evaluation.qa_evaluator import QAEvaluator


def evaluate_qa_quality(data_dir: Path, output_dir: Path):
    """评估问答任务质量"""
    
    print("\n" + "="*60)
    print("❓ Question Answering Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/qa/qa_responses.csv'
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    evaluator = QAEvaluator(config={'domain': 'cs'})
    
    # 评估每个模型的每个响应
    results = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Models"):
        model = row['model']
        
        for col in df.columns:
            if col == 'model':
                continue
            
            response = row[col]
            
            if pd.isna(response) or len(str(response).strip()) == 0:
                continue
            
            # 评估质量
            scores = evaluator.evaluate(str(response))
            
            # 保存结果
            result = {
                'model': model,
                'question_id': col,
                **scores
            }
            results.append(result)
    
    # 转换为DataFrame
    results_df = pd.DataFrame(results)
    
    # 保存结果
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'qa_quality_scores.csv'
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
                   if col not in ['model', 'question_id'] 
                   and df[col].dtype in ['float64', 'int64']]
    
    summary = df.groupby('model')[metric_cols].agg(['mean', 'std', 'min', 'max'])
    
    # 保存汇总统计
    summary_file = output_dir / 'qa_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型
    if 'confidence_score' in df.columns:
        print(f"\n🏆 Top 3 Models by Confidence Score:")
        top_models = df.groupby('model')['confidence_score'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.3f}")
    
    if 'technical_term_density' in df.columns:
        print(f"\n🎯 Top 3 Models by Technical Term Density:")
        top_models = df.groupby('model')['technical_term_density'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.3f}")


def generate_report(df: pd.DataFrame, output_dir: Path):
    """生成评估报告"""
    from datetime import datetime
    
    report_lines = []
    report_lines.append("# 问答任务质量评估报告")
    report_lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**评估模型数**: {df['model'].nunique()}")
    report_lines.append(f"**评估样本数**: {len(df)}")
    report_lines.append("")
    
    # 评估指标说明
    report_lines.append("## 评估指标说明")
    report_lines.append("### 完整性指标")
    report_lines.append("- **Has Answer**: 是否包含答案")
    report_lines.append("- **Has Conclusion**: 是否有结论性语句")
    report_lines.append("")
    report_lines.append("### 专业性指标")
    report_lines.append("- **Technical Term Density**: 技术术语密度")
    report_lines.append("- **Technical Term Count**: 技术术语数量")
    report_lines.append("")
    report_lines.append("### 置信度指标")
    report_lines.append("- **Confidence Score**: 答案置信度")
    report_lines.append("- **Uncertainty Count**: 不确定性表达数量")
    report_lines.append("- **Certainty Count**: 确定性表达数量")
    report_lines.append("")
    report_lines.append("### 结构与推理指标")
    report_lines.append("- **Has Enumeration**: 是否有列举")
    report_lines.append("- **Has Reasoning**: 是否包含推理")
    report_lines.append("- **Reasoning Steps**: 推理步骤数")
    report_lines.append("")
    
    # 整体统计
    report_lines.append("## 整体统计")
    report_lines.append("| 指标 | 均值 | 标准差 | 最小值 | 最大值 |")
    report_lines.append("|------|------|--------|--------|--------|")
    
    key_metrics = ['confidence_score', 'technical_term_density', 'has_reasoning', 'has_conclusion']
    for metric in key_metrics:
        if metric in df.columns:
            mean_val = df[metric].mean()
            std_val = df[metric].std()
            min_val = df[metric].min()
            max_val = df[metric].max()
            
            if df[metric].dtype == 'float64':
                report_lines.append(f"| {metric} | {mean_val:.2%} | {std_val:.2%} | {min_val:.2%} | {max_val:.2%} |")
            else:
                report_lines.append(f"| {metric} | {mean_val:.2f} | {std_val:.2f} | {min_val:.2f} | {max_val:.2f} |")
    
    report_lines.append("")
    
    # 模型排名
    report_lines.append("## 模型排名")
    report_lines.append("")
    report_lines.append("### 按置信度排名")
    report_lines.append("| 排名 | 模型 | 置信度 | 技术密度 | 推理率 |")
    report_lines.append("|------|------|--------|----------|--------|")
    
    model_stats = df.groupby('model').agg({
        'confidence_score': 'mean',
        'technical_term_density': 'mean',
        'has_reasoning': 'mean'
    }).sort_values('confidence_score', ascending=False)
    
    for rank, (model, row) in enumerate(model_stats.iterrows(), 1):
        report_lines.append(
            f"| {rank} | {model} | {row['confidence_score']:.2%} | "
            f"{row['technical_term_density']:.2%} | {row['has_reasoning']:.2%} |"
        )
    
    report_lines.append("")
    
    # 保存报告
    report_file = output_dir / 'qa_quality_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"📄 Report generated: {report_file}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估问答质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/qa_quality',
                       help='输出目录')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_qa_quality(data_dir, output_dir)
```

---

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**作者**: Kiro AI Assistant  
**状态**: 设计完成,待实施

