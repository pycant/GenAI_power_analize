# 数学推理任务质量评估方法设计

## 1. 评估目标

数学推理任务的核心评估维度：
- **准确性 (Accuracy)**: 答案的正确性
- **推理完整性 (Reasoning Completeness)**: 解题步骤的完整性
- **数值精度 (Numerical Precision)**: 数值答案的精确匹配

## 2. 数据特征分析

### 2.1 任务类型

基于提供的数学问题，任务类型为：
- **应用题 (Word Problems)**: 需要理解文字描述并转化为数学问题
- **多步骤计算**: 需要多个计算步骤才能得出最终答案
- **实际场景**: 涉及金钱、数量、百分比等实际应用

### 2.2 答案格式

从样本数据观察到的答案格式：
- **详细推理过程**: 模型会展示完整的思考和计算步骤
- **最终数值答案**: 通常在文本末尾给出
- **单位**: 可能包含货币符号（$）或其他单位

### 2.3 标准答案

| 问题 | 标准答案 | 计算过程 |
|------|----------|----------|
| q01 | $90 | (0.8 - 0.5) × 10 × 30 = 90 |
| q02 | 60 students | 50 × (1 + 20%) = 60 |
| q03 | 5 books | 300 ÷ 15 ÷ 4 = 5 |
| q04 | $21 | 21 × 4 - 63 = 21 |
| q05 | $66 | 3 × 16 + 3 × 6 = 66 |


## 3. 评估方法设计

### 3.1 核心指标

#### 3.1.1 Exact Match (EM) ✅ 高度可行

**定义**：
- 提取的答案与标准答案完全匹配
- 最严格的评估标准

**实现方案**：
```python
def calculate_exact_match(generated: str, reference: str) -> float:
    """
    计算精确匹配
    
    Args:
        generated: 生成的答案文本
        reference: 标准答案
    
    Returns:
        float: 1.0 (匹配) 或 0.0 (不匹配)
    """
    # 提取数值答案
    gen_answer = extract_answer(generated)
    ref_answer = extract_answer(reference)
    
    # 归一化比较
    gen_normalized = normalize_answer(gen_answer)
    ref_normalized = normalize_answer(ref_answer)
    
    return 1.0 if gen_normalized == ref_normalized else 0.0
```

**优势**：
- ✅ 评估标准明确
- ✅ 无需外部模型
- ✅ 计算快速

**挑战**：
- ⚠️ 需要准确提取答案
- ⚠️ 需要处理不同格式（$90, 90 dollars, 90美元）

#### 3.1.2 Numerical Match (数值精度匹配) ✅ 高度可行

**定义**：
- 提取数值并允许一定误差范围
- 适用于浮点数计算

**实现方案**：
```python
def calculate_numerical_match(generated: str, reference: str, 
                              tolerance: float = 0.01) -> float:
    """
    计算数值匹配（允许误差）
    
    Args:
        generated: 生成的答案文本
        reference: 标准答案
        tolerance: 相对误差容忍度（默认1%）
    
    Returns:
        float: 1.0 (匹配) 或 0.0 (不匹配)
    """
    # 提取数值
    gen_num = extract_number(generated)
    ref_num = extract_number(reference)
    
    if gen_num is None or ref_num is None:
        return 0.0
    
    # 计算相对误差
    if ref_num == 0:
        return 1.0 if abs(gen_num) < tolerance else 0.0
    
    relative_error = abs(gen_num - ref_num) / abs(ref_num)
    
    return 1.0 if relative_error < tolerance else 0.0
```

**优势**：
- ✅ 对浮点数友好
- ✅ 允许合理的计算误差
- ✅ 更宽松的评估标准

**配置**：
- 默认容忍度：1% (0.01)
- 可调整为绝对误差或相对误差


### 3.2 辅助指标

#### 3.2.1 Reasoning Completeness (推理完整性) ✅ 可行

**定义**：
- 评估解题步骤的完整性
- 检测是否包含计算过程

**实现方案**：
```python
def calculate_reasoning_completeness(text: str) -> Dict[str, float]:
    """
    评估推理完整性
    
    Returns:
        Dict with:
        - has_reasoning: 是否包含推理过程
        - step_count: 推理步骤数量
        - has_calculation: 是否包含计算式
    """
    scores = {}
    
    # 1. 检测推理关键词
    reasoning_keywords = [
        'first', 'then', 'next', 'finally', 'so', 'therefore',
        '首先', '然后', '接下来', '最后', '所以', '因此'
    ]
    
    has_reasoning = any(kw in text.lower() for kw in reasoning_keywords)
    scores['has_reasoning'] = 1.0 if has_reasoning else 0.0
    
    # 2. 计算步骤数量（基于句子分割）
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    scores['step_count'] = len(sentences)
    
    # 3. 检测计算式
    import re
    calculation_patterns = [
        r'\d+\s*[\+\-\*\/×÷]\s*\d+',  # 基本运算
        r'\d+\s*=\s*\d+',              # 等式
        r'\(\d+.*?\)',                 # 括号表达式
    ]
    
    has_calculation = any(
        re.search(pattern, text) 
        for pattern in calculation_patterns
    )
    scores['has_calculation'] = 1.0 if has_calculation else 0.0
    
    return scores
```

**优势**：
- ✅ 评估解题过程质量
- ✅ 无需外部模型
- ✅ 可解释性强

**应用**：
- 区分"直接给答案"和"展示推理过程"的模型
- 评估模型的可解释性

#### 3.2.2 Answer Extraction Confidence (答案提取置信度) ✅ 可行

**定义**：
- 评估答案提取的可靠性
- 检测答案的明确性

**实现方案**：
```python
def calculate_extraction_confidence(text: str) -> float:
    """
    评估答案提取置信度
    
    Returns:
        float: [0, 1]，越高表示答案越明确
    """
    import re
    
    confidence = 0.0
    
    # 1. 检测明确的答案标记
    answer_markers = [
        r'answer is (\d+)',
        r'= (\d+)$',
        r'total.*?(\d+)',
        r'答案是?\s*(\d+)',
        r'结果是?\s*(\d+)',
    ]
    
    for pattern in answer_markers:
        if re.search(pattern, text, re.IGNORECASE):
            confidence += 0.3
    
    # 2. 检测数值的唯一性
    numbers = re.findall(r'\$?\d+\.?\d*', text)
    if len(numbers) == 1:
        confidence += 0.4  # 唯一数值，高置信度
    elif len(numbers) <= 3:
        confidence += 0.2  # 少量数值，中等置信度
    
    # 3. 检测答案位置（末尾更可靠）
    last_sentence = text.split('.')[-1]
    if re.search(r'\d+', last_sentence):
        confidence += 0.3
    
    return min(confidence, 1.0)
```

**优势**：
- ✅ 量化答案的明确性
- ✅ 辅助判断提取是否可靠


## 4. 答案提取策略

### 4.1 提取规则

答案提取是数学评估的关键步骤，需要处理多种格式：

```python
def extract_answer(text: str) -> Optional[str]:
    """
    从文本中提取答案
    
    策略优先级：
    1. 明确的答案标记
    2. 最后一个数值
    3. 最大/最显著的数值
    """
    import re
    
    # 策略1: 查找明确的答案标记
    answer_patterns = [
        r'(?:answer|result|total|solution)\s*(?:is|=|:)?\s*\$?(\d+\.?\d*)',
        r'(?:答案|结果|总计|共)\s*(?:是|为|：)?\s*\$?(\d+\.?\d*)',
        r'=\s*\$?(\d+\.?\d*)(?:\s|$)',  # 等号后的数值
    ]
    
    for pattern in answer_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # 策略2: 提取最后一个数值
    numbers = re.findall(r'\$?(\d+\.?\d*)', text)
    if numbers:
        return numbers[-1]
    
    return None


def extract_number(text: str) -> Optional[float]:
    """
    从文本中提取数值（浮点数）
    """
    answer_str = extract_answer(text)
    if answer_str is None:
        return None
    
    try:
        # 移除货币符号和逗号
        cleaned = answer_str.replace('$', '').replace(',', '')
        return float(cleaned)
    except ValueError:
        return None


def normalize_answer(answer: str) -> str:
    """
    归一化答案字符串
    
    处理：
    - 移除空格
    - 统一大小写
    - 移除货币符号
    - 移除单位
    """
    if answer is None:
        return ""
    
    # 转小写
    normalized = answer.lower().strip()
    
    # 移除常见符号
    normalized = normalized.replace('$', '').replace(',', '')
    
    # 移除常见单位
    units = ['dollars', 'dollar', 'students', 'student', 'books', 'book', 
             '美元', '学生', '本']
    for unit in units:
        normalized = normalized.replace(unit, '')
    
    return normalized.strip()
```

### 4.2 提取示例

| 原始文本 | 提取结果 | 说明 |
|---------|---------|------|
| "The answer is $90" | "90" | 明确标记 |
| "Total profit is 90 dollars" | "90" | 关键词匹配 |
| "30 × 3 = 90" | "90" | 等号后数值 |
| "...so the result is 60 students" | "60" | 最后数值 |
| "She bought 5 books for each child" | "5" | 最后数值 |


## 5. 推荐评估方案

### 5.1 核心指标（必须实现）

| 维度 | 指标 | 优先级 | 计算成本 | 可行性 |
|------|------|--------|----------|--------|
| 准确性 | Exact Match | ⭐⭐⭐ | 低 | ✅ 高 |
| 准确性 | Numerical Match | ⭐⭐⭐ | 低 | ✅ 高 |
| 推理 | Has Reasoning | ⭐⭐ | 低 | ✅ 高 |
| 推理 | Step Count | ⭐ | 低 | ✅ 高 |

### 5.2 评估流程

```
1. 答案提取
   ├── 使用多种策略提取答案
   ├── 计算提取置信度
   └── 归一化答案格式

2. 准确性评估
   ├── Exact Match（严格）
   └── Numerical Match（宽松）

3. 推理评估
   ├── 检测推理关键词
   ├── 统计步骤数量
   └── 检测计算式

4. 综合评分
   ├── 主指标：Exact Match 或 Numerical Match
   └── 辅助指标：推理完整性
```

### 5.3 评分权重建议

#### 方案1：准确性优先（推荐）
```python
math_quality_score = {
    'exact_match': 0.7,        # 70% - 准确性最重要
    'has_reasoning': 0.2,      # 20% - 推理过程
    'extraction_confidence': 0.1  # 10% - 答案明确性
}
```

#### 方案2：均衡评估
```python
math_quality_score = {
    'numerical_match': 0.5,    # 50% - 数值准确性
    'has_reasoning': 0.3,      # 30% - 推理过程
    'has_calculation': 0.2     # 20% - 计算展示
}
```

#### 方案3：多维度呈现（推荐）
不计算单一综合分数，保留多维度指标：
```python
math_quality_metrics = {
    'accuracy': {
        'exact_match': float,
        'numerical_match': float,
    },
    'reasoning': {
        'has_reasoning': bool,
        'step_count': int,
        'has_calculation': bool,
    },
    'confidence': {
        'extraction_confidence': float,
    }
}
```


## 6. 实现方案

### 6.1 评估器设计

```python
# data/analize/scripts/quality_evaluation/math_evaluator.py

import re
from typing import Dict, Optional
from .base_evaluator import BaseEvaluator


class MathEvaluator(BaseEvaluator):
    """数学推理任务评估器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.tolerance = config.get('tolerance', 0.01) if config else 0.01
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估数学推理质量
        
        Args:
            generated: 生成的答案文本
            reference: 标准答案
            context: 额外上下文（可包含标准答案）
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or len(generated.strip()) == 0:
            return self._get_zero_scores()
        
        # 1. 答案提取
        extracted_answer = self._extract_answer(generated)
        scores['extraction_confidence'] = self._calculate_extraction_confidence(generated)
        
        # 2. 准确性评估（需要标准答案）
        if reference:
            scores['exact_match'] = self._calculate_exact_match(generated, reference)
            scores['numerical_match'] = self._calculate_numerical_match(generated, reference)
        else:
            scores['exact_match'] = None
            scores['numerical_match'] = None
        
        # 3. 推理完整性评估
        reasoning_scores = self._calculate_reasoning_completeness(generated)
        scores.update(reasoning_scores)
        
        # 4. 基础指标
        scores['text_length'] = len(generated)
        scores['has_answer'] = 1.0 if extracted_answer else 0.0
        
        return scores
    
    def _extract_answer(self, text: str) -> Optional[str]:
        """提取答案"""
        # 策略1: 明确的答案标记
        answer_patterns = [
            r'(?:answer|result|total|solution)\s*(?:is|=|:)?\s*\$?(\d+\.?\d*)',
            r'(?:答案|结果|总计|共)\s*(?:是|为|：)?\s*\$?(\d+\.?\d*)',
            r'=\s*\$?(\d+\.?\d*)(?:\s|$|\.)',
        ]
        
        for pattern in answer_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # 策略2: 最后一个数值
        numbers = re.findall(r'\$?(\d+\.?\d*)', text)
        if numbers:
            return numbers[-1]
        
        return None
    
    def _extract_number(self, text: str) -> Optional[float]:
        """提取数值"""
        answer_str = self._extract_answer(text)
        if answer_str is None:
            return None
        
        try:
            cleaned = answer_str.replace('$', '').replace(',', '')
            return float(cleaned)
        except ValueError:
            return None
    
    def _normalize_answer(self, answer: str) -> str:
        """归一化答案"""
        if answer is None:
            return ""
        
        normalized = answer.lower().strip()
        normalized = normalized.replace('$', '').replace(',', '')
        
        # 移除单位
        units = ['dollars', 'dollar', 'students', 'student', 'books', 'book']
        for unit in units:
            normalized = normalized.replace(unit, '')
        
        return normalized.strip()
    
    def _calculate_exact_match(self, generated: str, reference: str) -> float:
        """计算精确匹配"""
        gen_answer = self._extract_answer(generated)
        ref_answer = self._extract_answer(reference)
        
        if gen_answer is None or ref_answer is None:
            return 0.0
        
        gen_norm = self._normalize_answer(gen_answer)
        ref_norm = self._normalize_answer(reference)
        
        return 1.0 if gen_norm == ref_norm else 0.0
    
    def _calculate_numerical_match(self, generated: str, reference: str) -> float:
        """计算数值匹配"""
        gen_num = self._extract_number(generated)
        ref_num = self._extract_number(reference)
        
        if gen_num is None or ref_num is None:
            return 0.0
        
        if ref_num == 0:
            return 1.0 if abs(gen_num) < self.tolerance else 0.0
        
        relative_error = abs(gen_num - ref_num) / abs(ref_num)
        return 1.0 if relative_error < self.tolerance else 0.0
    
    def _calculate_reasoning_completeness(self, text: str) -> Dict[str, float]:
        """计算推理完整性"""
        scores = {}
        
        # 1. 推理关键词
        reasoning_keywords = [
            'first', 'then', 'next', 'finally', 'so', 'therefore',
            '首先', '然后', '接下来', '最后', '所以', '因此'
        ]
        has_reasoning = any(kw in text.lower() for kw in reasoning_keywords)
        scores['has_reasoning'] = 1.0 if has_reasoning else 0.0
        
        # 2. 步骤数量
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        scores['step_count'] = len(sentences)
        
        # 3. 计算式
        calculation_patterns = [
            r'\d+\s*[\+\-\*\/×÷]\s*\d+',
            r'\d+\s*=\s*\d+',
            r'\(\d+.*?\)',
        ]
        has_calculation = any(
            re.search(pattern, text) 
            for pattern in calculation_patterns
        )
        scores['has_calculation'] = 1.0 if has_calculation else 0.0
        
        return scores
    
    def _calculate_extraction_confidence(self, text: str) -> float:
        """计算提取置信度"""
        confidence = 0.0
        
        # 明确的答案标记
        answer_markers = [
            r'answer is (\d+)',
            r'= (\d+)$',
            r'total.*?(\d+)',
        ]
        
        for pattern in answer_markers:
            if re.search(pattern, text, re.IGNORECASE):
                confidence += 0.3
        
        # 数值唯一性
        numbers = re.findall(r'\$?\d+\.?\d*', text)
        if len(numbers) == 1:
            confidence += 0.4
        elif len(numbers) <= 3:
            confidence += 0.2
        
        # 答案位置
        last_sentence = text.split('.')[-1]
        if re.search(r'\d+', last_sentence):
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数"""
        return {
            'exact_match': 0.0,
            'numerical_match': 0.0,
            'has_reasoning': 0.0,
            'step_count': 0,
            'has_calculation': 0.0,
            'extraction_confidence': 0.0,
            'text_length': 0,
            'has_answer': 0.0
        }
    
    def get_metric_categories(self) -> Dict[str, list]:
        """返回指标分类"""
        return {
            'accuracy': ['exact_match', 'numerical_match'],
            'reasoning': ['has_reasoning', 'step_count', 'has_calculation'],
            'confidence': ['extraction_confidence', 'has_answer']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向"""
        return {
            'exact_match': True,
            'numerical_match': True,
            'has_reasoning': True,
            'step_count': True,
            'has_calculation': True,
            'extraction_confidence': True,
            'has_answer': True
        }
```


## 7. 标准答案配置

### 7.1 答案字典

```python
# 标准答案配置
MATH_REFERENCE_ANSWERS = {
    'q01': {
        'answer': '90',
        'unit': 'dollars',
        'explanation': '(0.8 - 0.5) × 10 × 30 = 90'
    },
    'q02': {
        'answer': '60',
        'unit': 'students',
        'explanation': '50 × (1 + 20%) = 60'
    },
    'q03': {
        'answer': '5',
        'unit': 'books',
        'explanation': '300 ÷ 15 ÷ 4 = 5'
    },
    'q04': {
        'answer': '21',
        'unit': 'dollars',
        'explanation': '21 × 4 - 63 = 21'
    },
    'q05': {
        'answer': '66',
        'unit': 'dollars',
        'explanation': '3 × 16 + 3 × 6 = 66'
    }
}
```

### 7.2 使用方式

```python
def evaluate_with_reference(generated: str, question_id: str) -> Dict:
    """使用标准答案评估"""
    reference = MATH_REFERENCE_ANSWERS.get(question_id)
    
    if reference is None:
        raise ValueError(f"No reference answer for {question_id}")
    
    evaluator = MathEvaluator()
    scores = evaluator.evaluate(
        generated=generated,
        reference=reference['answer']
    )
    
    return scores
```

## 8. 批量评估脚本

```python
# data/analize/scripts/evaluate_math_quality.py

import pandas as pd
from pathlib import Path
from tqdm import tqdm
from quality_evaluation.math_evaluator import MathEvaluator

# 标准答案
REFERENCE_ANSWERS = {
    'q01': '90',
    'q02': '60',
    'q03': '5',
    'q04': '21',
    'q05': '66'
}


def evaluate_math_quality(data_dir: Path, output_dir: Path):
    """评估数学推理任务质量"""
    
    print("\n" + "="*60)
    print("🔢 Math Reasoning Quality Evaluation")
    print("="*60)
    
    # 加载数据
    responses_file = data_dir / 'comparison_matrices/math/math_responses.csv'
    df = pd.read_csv(responses_file)
    
    print(f"\n📂 Loaded {len(df)} models")
    print(f"📝 Questions: {len([c for c in df.columns if c != 'model'])}")
    
    # 初始化评估器
    evaluator = MathEvaluator(config={'tolerance': 0.01})
    
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
            
            # 获取标准答案
            reference = REFERENCE_ANSWERS.get(col)
            
            # 评估质量
            scores = evaluator.evaluate(str(response), reference=reference)
            
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
    output_file = output_dir / 'math_quality_scores.csv'
    results_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Evaluation completed!")
    print(f"📊 Results saved to: {output_file}")
    print(f"📈 Total evaluations: {len(results_df)}")
    
    # 生成汇总统计
    generate_summary_stats(results_df, output_dir)
    
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
    summary_file = output_dir / 'math_quality_summary.csv'
    summary.to_csv(summary_file, encoding='utf-8-sig')
    
    print(f"✅ Summary statistics: {summary_file}")
    
    # 打印Top 3模型（按准确率排序）
    if 'exact_match' in df.columns:
        print(f"\n🏆 Top 3 Models by Exact Match:")
        top_models = df.groupby('model')['exact_match'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")
    
    if 'numerical_match' in df.columns:
        print(f"\n🎯 Top 3 Models by Numerical Match:")
        top_models = df.groupby('model')['numerical_match'].mean().sort_values(ascending=False).head(3)
        for rank, (model, score) in enumerate(top_models.items(), 1):
            print(f"  {rank}. {model}: {score:.2%}")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='评估数学推理质量')
    parser.add_argument('--data-dir', type=str, 
                       default='data/analize/pre_data',
                       help='数据目录')
    parser.add_argument('--output-dir', type=str,
                       default='data/analize/results/math_quality',
                       help='输出目录')
    parser.add_argument('--tolerance', type=float, default=0.01,
                       help='数值匹配容忍度（默认1%）')
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    evaluate_math_quality(data_dir, output_dir)
```


## 9. 可视化分析

### 9.1 推荐图表

#### 图表1：准确率对比（柱状图）
```python
def plot_accuracy_comparison(df: pd.DataFrame, output_dir: Path):
    """绘制准确率对比图"""
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Exact Match
    model_em = df.groupby('model')['exact_match'].mean().sort_values(ascending=False)
    axes[0].barh(model_em.index, model_em.values)
    axes[0].set_xlabel('Exact Match Rate')
    axes[0].set_title('Math Accuracy: Exact Match')
    axes[0].grid(True, alpha=0.3, axis='x')
    
    # Numerical Match
    model_nm = df.groupby('model')['numerical_match'].mean().sort_values(ascending=False)
    axes[1].barh(model_nm.index, model_nm.values)
    axes[1].set_xlabel('Numerical Match Rate')
    axes[1].set_title('Math Accuracy: Numerical Match')
    axes[1].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'math_accuracy_comparison.png', dpi=300)
    plt.close()
```

#### 图表2：准确率热力图（模型×问题）
```python
def plot_accuracy_heatmap(df: pd.DataFrame, output_dir: Path):
    """绘制准确率热力图"""
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # 创建透视表
    pivot_data = df.pivot_table(
        values='exact_match',
        index='model',
        columns='question_id',
        aggfunc='mean'
    )
    
    fig, ax = plt.subplots(figsize=(10, 12))
    sns.heatmap(pivot_data, annot=True, fmt='.0%', cmap='RdYlGn',
                vmin=0, vmax=1, cbar_kws={'label': 'Accuracy'},
                linewidths=0.5, ax=ax)
    
    ax.set_title('Math Accuracy Heatmap (Exact Match)', fontsize=14)
    ax.set_xlabel('Question ID')
    ax.set_ylabel('Model')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'math_accuracy_heatmap.png', dpi=300)
    plt.close()
```

#### 图表3：推理完整性分析
```python
def plot_reasoning_analysis(df: pd.DataFrame, output_dir: Path):
    """绘制推理完整性分析图"""
    import matplotlib.pyplot as plt
    import numpy as np
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # 1. 推理关键词比例
    model_reasoning = df.groupby('model')['has_reasoning'].mean().sort_values(ascending=False)
    axes[0].barh(model_reasoning.index, model_reasoning.values)
    axes[0].set_xlabel('Has Reasoning (%)')
    axes[0].set_title('Models with Reasoning Keywords')
    axes[0].grid(True, alpha=0.3, axis='x')
    
    # 2. 平均步骤数
    model_steps = df.groupby('model')['step_count'].mean().sort_values(ascending=False)
    axes[1].barh(model_steps.index, model_steps.values)
    axes[1].set_xlabel('Average Step Count')
    axes[1].set_title('Reasoning Step Count')
    axes[1].grid(True, alpha=0.3, axis='x')
    
    # 3. 计算式比例
    model_calc = df.groupby('model')['has_calculation'].mean().sort_values(ascending=False)
    axes[2].barh(model_calc.index, model_calc.values)
    axes[2].set_xlabel('Has Calculation (%)')
    axes[2].set_title('Models with Calculation Formulas')
    axes[2].grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'math_reasoning_analysis.png', dpi=300)
    plt.close()
```

#### 图表4：准确率 vs 推理完整性（散点图）
```python
def plot_accuracy_vs_reasoning(df: pd.DataFrame, output_dir: Path):
    """绘制准确率与推理完整性的关系"""
    import matplotlib.pyplot as plt
    
    # 按模型汇总
    model_stats = df.groupby('model').agg({
        'exact_match': 'mean',
        'has_reasoning': 'mean',
        'step_count': 'mean'
    })
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 准确率 vs 推理关键词
    axes[0].scatter(model_stats['has_reasoning'], 
                   model_stats['exact_match'],
                   s=100, alpha=0.6)
    
    for model, row in model_stats.iterrows():
        axes[0].annotate(model, 
                        (row['has_reasoning'], row['exact_match']),
                        fontsize=8, alpha=0.7)
    
    axes[0].set_xlabel('Has Reasoning Rate')
    axes[0].set_ylabel('Exact Match Rate')
    axes[0].set_title('Accuracy vs Reasoning Keywords')
    axes[0].grid(True, alpha=0.3)
    
    # 准确率 vs 步骤数
    axes[1].scatter(model_stats['step_count'], 
                   model_stats['exact_match'],
                   s=100, alpha=0.6)
    
    for model, row in model_stats.iterrows():
        axes[1].annotate(model, 
                        (row['step_count'], row['exact_match']),
                        fontsize=8, alpha=0.7)
    
    axes[1].set_xlabel('Average Step Count')
    axes[1].set_ylabel('Exact Match Rate')
    axes[1].set_title('Accuracy vs Step Count')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'math_accuracy_vs_reasoning.png', dpi=300)
    plt.close()
```


## 10. 潜在问题与解决方案

### 10.1 答案提取问题

**问题1：多个数值混淆**
```
示例：文本中包含多个数值，如 "30 students sold 10 lollipops each for $0.8, profit is $90"
挑战：如何准确识别最终答案（90）而非中间数值（30, 10, 0.8）
```

**解决方案**：
1. 优先匹配明确的答案标记（"answer is", "result is"）
2. 使用位置启发式（最后一个数值通常是答案）
3. 使用数值大小启发式（最大数值可能是答案）
4. 结合上下文关键词（"total", "profit", "result"）

**问题2：单位处理**
```
示例：
- "$90" vs "90 dollars" vs "90美元"
- "60 students" vs "60" vs "60个学生"
```

**解决方案**：
- 归一化时移除所有单位
- 保留数值部分进行比较
- 支持多语言单位识别

**问题3：格式多样性**
```
示例：
- "90" vs "90.0" vs "90.00"
- "$90" vs "$ 90" vs "90$"
```

**解决方案**：
- 统一转换为浮点数
- 移除空格和特殊符号
- 使用数值比较而非字符串比较

### 10.2 推理评估问题

**问题1：推理关键词的语言依赖**
```
挑战：中英文混合文本，关键词识别不完整
```

**解决方案**：
- 同时支持中英文关键词
- 使用正则表达式灵活匹配
- 考虑添加更多语言支持

**问题2：步骤计数的准确性**
```
挑战：基于句子分割可能不准确
```

**解决方案**：
- 结合多种分割策略（句号、换行、关键词）
- 过滤过短的句子（< 10字符）
- 可选：使用NLP工具进行更精确的句子分割

### 10.3 评估公平性问题

**问题：不同模型的输出风格差异**
```
- 简洁型：直接给出答案 "90"
- 详细型：展示完整推理过程
- 混合型：部分推理 + 答案
```

**解决方案**：
- 分离准确性和推理完整性评估
- 不惩罚简洁的正确答案
- 推理完整性作为独立维度评估
- 允许用户根据应用场景选择权重


## 11. 评估指标解释

### 11.1 准确性指标

#### Exact Match (精确匹配)
- **含义**: 提取的答案与标准答案完全一致
- **范围**: {0, 1}
- **解释**:
  - 1.0: 完全正确
  - 0.0: 不正确或无法提取
- **应用**: 最严格的评估标准，适用于要求精确答案的场景

#### Numerical Match (数值匹配)
- **含义**: 数值在容忍范围内匹配
- **范围**: {0, 1}
- **容忍度**: 默认1%相对误差
- **解释**:
  - 1.0: 数值正确（在误差范围内）
  - 0.0: 数值错误或无法提取
- **应用**: 更宽松的评估，适用于允许计算误差的场景

### 11.2 推理指标

#### Has Reasoning (包含推理)
- **含义**: 文本中是否包含推理关键词
- **范围**: {0, 1}
- **关键词**: first, then, so, therefore, 首先, 然后, 所以, 因此
- **应用**: 评估模型是否展示思考过程

#### Step Count (步骤数量)
- **含义**: 推理步骤的数量
- **范围**: [0, +∞)
- **计算**: 基于句子分割
- **解释**:
  - 0-2: 简洁回答
  - 3-5: 中等详细
  - 6+: 非常详细
- **应用**: 评估推理的详细程度

#### Has Calculation (包含计算式)
- **含义**: 是否包含数学计算表达式
- **范围**: {0, 1}
- **模式**: 加减乘除、等式、括号表达式
- **应用**: 评估是否展示计算过程

### 11.3 置信度指标

#### Extraction Confidence (提取置信度)
- **含义**: 答案提取的可靠性
- **范围**: [0, 1]
- **因素**:
  - 明确的答案标记 (+0.3)
  - 数值唯一性 (+0.4)
  - 答案位置（末尾）(+0.3)
- **应用**: 辅助判断评估结果的可靠性

#### Has Answer (包含答案)
- **含义**: 是否成功提取到答案
- **范围**: {0, 1}
- **应用**: 检测模型是否给出了答案


## 12. 使用指南

### 12.1 快速开始

```bash
# 1. 激活环境
conda activate bartscore

# 2. 运行评估
python data/analize/scripts/evaluate_math_quality.py

# 3. 查看结果
type data\analize\results\math_quality\math_quality_scores.csv
```

### 12.2 自定义配置

```python
# 调整数值匹配容忍度
python evaluate_math_quality.py --tolerance 0.05  # 5%误差

# 指定输出目录
python evaluate_math_quality.py --output-dir custom/path
```

### 12.3 预期输出

```
data/analize/results/math_quality/
├── math_quality_scores.csv          # 详细评分（55行）
├── math_quality_summary.csv         # 汇总统计（11行）
├── math_quality_report.md           # 分析报告
└── figures/                         # 可视化图表
    ├── math_accuracy_comparison.png
    ├── math_accuracy_heatmap.png
    ├── math_reasoning_analysis.png
    └── math_accuracy_vs_reasoning.png
```

### 12.4 性能估算

- 每个样本评估时间: ~0.01秒（纯规则，无模型）
- 总评估时间: ~1秒（11模型 × 5问题）
- 内存占用: < 100MB
- 无需GPU

## 13. 与其他任务的对比

| 维度 | 代码生成 | 创意写作 | 数学推理 | 问答 | 摘要 |
|------|---------|---------|---------|------|------|
| **核心指标** | 编译率 | Distinct-N | Exact Match | F1 Score | ROUGE |
| **评估难度** | 高 | 中 | 中 | 中 | 高 |
| **需要参考答案** | 否 | 否 | 是 | 是 | 是 |
| **需要外部模型** | 否 | 可选 | 否 | 可选 | 可选 |
| **计算成本** | 低 | 中 | 低 | 中 | 高 |
| **主观性** | 低 | 中 | 低 | 低 | 中 |

### 数学推理的特点

**优势**：
- ✅ 评估标准明确（有标准答案）
- ✅ 计算成本低（无需外部模型）
- ✅ 客观性强（数值比较）
- ✅ 实现简单（基于规则）

**挑战**：
- ⚠️ 答案提取依赖启发式规则
- ⚠️ 需要维护标准答案库
- ⚠️ 对输出格式敏感

## 14. 未来改进方向

### 14.1 短期改进（1-2周）

1. **增强答案提取**
   - 使用NLP工具（spaCy, NLTK）进行更精确的提取
   - 训练简单的分类器识别答案位置
   - 支持更多答案格式

2. **扩展标准答案库**
   - 添加更多数学问题
   - 支持多个正确答案
   - 包含详细的解题步骤作为参考

3. **改进推理评估**
   - 使用依存句法分析识别推理结构
   - 评估推理的逻辑连贯性
   - 检测常见错误模式

### 14.2 中期改进（1-2月）

4. **语义理解评估**
   - 使用BERT等模型评估答案的语义正确性
   - 即使格式不同，语义相同也应得分
   - 评估解题思路的合理性

5. **错误分析**
   - 分类错误类型（计算错误、理解错误、格式错误）
   - 生成错误分析报告
   - 为模型改进提供方向

6. **难度分级**
   - 根据问题难度调整评分权重
   - 识别模型的能力边界
   - 生成难度-准确率曲线

### 14.3 长期改进（3-6月）

7. **自动生成测试用例**
   - 使用模板生成新的数学问题
   - 自动验证答案正确性
   - 扩大评估覆盖面

8. **多模态评估**
   - 支持包含图表的数学问题
   - 评估对图形信息的理解
   - 处理几何、统计图表等

9. **对抗性测试**
   - 生成易混淆的问题
   - 测试模型的鲁棒性
   - 识别系统性弱点

## 15. 总结

### 15.1 方法可行性

| 方法 | 可行性 | 推荐度 | 理由 |
|------|--------|--------|------|
| **Exact Match** | ✅ 高 | ⭐⭐⭐ | 标准明确、实现简单、无需外部依赖 |
| **Numerical Match** | ✅ 高 | ⭐⭐⭐ | 更宽松、适合实际应用 |
| **Reasoning Completeness** | ✅ 高 | ⭐⭐ | 评估可解释性、基于规则 |
| **Extraction Confidence** | ✅ 高 | ⭐⭐ | 辅助判断、提高可靠性 |

### 15.2 最终推荐方案

**核心指标组合**：
```python
math_quality_metrics = {
    'accuracy': {
        'exact_match': float,      # 主指标（严格）
        'numerical_match': float,  # 主指标（宽松）
    },
    'reasoning': {
        'has_reasoning': bool,     # 辅助指标
        'step_count': int,         # 辅助指标
        'has_calculation': bool,   # 辅助指标
    },
    'confidence': {
        'extraction_confidence': float,  # 质量控制
        'has_answer': bool,              # 质量控制
    }
}
```

**评分建议**：
- **准确性优先**: Exact Match 或 Numerical Match 作为主要评分
- **推理作为加分项**: 在准确的基础上，推理完整性可以加分
- **多维度呈现**: 不强制单一综合分数，保留完整信息

### 15.3 实施计划

**阶段1（1天）**: 基础实现 ✅
- 实现MathEvaluator类
- 实现答案提取和匹配
- 实现推理完整性评估

**阶段2（1天）**: 批量评估 ⏳
- 实现批量评估脚本
- 配置标准答案
- 生成评估报告

**阶段3（1天）**: 可视化分析 ⏳
- 生成准确率对比图
- 生成热力图
- 生成推理分析图

**阶段4（可选）**: 高级功能 ⏳
- 错误分析
- 难度分级
- 语义评估

---

**文档版本**: v1.0  
**创建日期**: 2026-03-04  
**作者**: Kiro AI Assistant  
**状态**: 设计完成，待实施
