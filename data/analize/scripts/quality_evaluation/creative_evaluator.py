"""
创意写作任务质量评估器

评估维度：
1. 多样性 (Diversity): Distinct-1/2/3
2. 流畅性 (Fluency): Perplexity
3. 语义多样性 (Semantic Diversity): 句向量距离（可选）
"""

import jieba
import numpy as np
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class CreativeEvaluator:
    """创意写作任务评估器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.ppl_model = None
        self.tokenizer = None
        self.sentence_model = None
        
        # 配置
        self.use_ppl = self.config.get('use_ppl', True)
        self.use_semantic = self.config.get('use_semantic', False)
        self.ppl_model_name = self.config.get('ppl_model', 'uer/gpt2-chinese-cluecorpussmall')
        self.semantic_model_name = self.config.get('semantic_model', 'paraphrase-multilingual-MiniLM-L12-v2')
    
    def evaluate(self, generated: str, reference: str = None, 
                 context: Dict = None) -> Dict[str, float]:
        """
        评估创意写作质量
        
        Args:
            generated: 生成的文本
            reference: 参考答案（创意写作通常没有）
            context: 额外上下文
        
        Returns:
            Dict[str, float]: 多维度指标
        """
        scores = {}
        
        # 基础检查
        if not generated or len(generated.strip()) == 0:
            return self._get_zero_scores()
        
        # 1. 多样性指标（核心）
        scores['distinct_1'] = self._calculate_distinct_n(generated, n=1)
        scores['distinct_2'] = self._calculate_distinct_n(generated, n=2)
        scores['distinct_3'] = self._calculate_distinct_n(generated, n=3)
        
        # 2. 流畅性指标
        if self.use_ppl:
            scores['perplexity'] = self._calculate_perplexity(generated)
        else:
            scores['perplexity'] = None
        
        # 3. 语义多样性（可选）
        if self.use_semantic:
            scores['semantic_diversity'] = self._calculate_semantic_diversity(generated)
        else:
            scores['semantic_diversity'] = None
        
        # 4. 基础指标
        scores['text_length'] = len(generated)
        scores['word_count'] = len(list(jieba.cut(generated)))
        scores['sentence_count'] = len([s for s in generated.split('。') if s.strip()])
        
        return scores
    
    def _calculate_distinct_n(self, text: str, n: int = 2) -> float:
        """
        计算Distinct-N指标
        
        Args:
            text: 输入文本
            n: N-gram的N
        
        Returns:
            float: Distinct-N分数 [0, 1]
        """
        try:
            # 分词
            tokens = list(jieba.cut(text))
            
            if len(tokens) < n:
                return 0.0
            
            # 生成N-grams
            ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
            
            if len(ngrams) == 0:
                return 0.0
            
            # 计算去重率
            distinct_score = len(set(ngrams)) / len(ngrams)
            
            return distinct_score
        
        except Exception as e:
            print(f"⚠️  Distinct-{n} calculation failed: {e}")
            return 0.0
    
    def _calculate_perplexity(self, text: str) -> Optional[float]:
        """
        计算困惑度（使用GPT-2中文模型）
        
        Args:
            text: 输入文本
        
        Returns:
            float: 困惑度值，越低越好
        """
        try:
            # 延迟加载模型
            if self.ppl_model is None:
                self._load_ppl_model()
            
            import torch
            
            # 编码（限制长度避免显存溢出）
            encodings = self.tokenizer(
                text, 
                return_tensors='pt', 
                max_length=512, 
                truncation=True,
                padding=False
            )
            
            # 移动到设备
            device = next(self.ppl_model.parameters()).device
            encodings = {k: v.to(device) for k, v in encodings.items()}
            
            # 计算困惑度
            with torch.no_grad():
                outputs = self.ppl_model(**encodings, labels=encodings['input_ids'])
                loss = outputs.loss
                perplexity = torch.exp(loss).item()
            
            return perplexity
        
        except Exception as e:
            print(f"⚠️  Perplexity calculation failed: {e}")
            return None
    
    def _calculate_semantic_diversity(self, text: str) -> Optional[float]:
        """
        计算句子间语义多样性
        
        Args:
            text: 输入文本
        
        Returns:
            float: 语义多样性分数 [0, 1]，越高越多样
        """
        try:
            # 延迟加载模型
            if self.sentence_model is None:
                self._load_semantic_model()
            
            # 分句
            sentences = [s.strip() for s in text.split('。') if len(s.strip()) > 5]
            
            if len(sentences) < 2:
                return 0.0
            
            # 计算句向量
            embeddings = self.sentence_model.encode(sentences)
            
            # 计算句子间余弦相似度
            from sklearn.metrics.pairwise import cosine_similarity
            sim_matrix = cosine_similarity(embeddings)
            
            # 提取上三角（不含对角线）
            n = len(sentences)
            similarities = []
            for i in range(n):
                for j in range(i+1, n):
                    similarities.append(sim_matrix[i][j])
            
            if len(similarities) == 0:
                return 0.0
            
            # 多样性 = 1 - 平均相似度
            avg_similarity = sum(similarities) / len(similarities)
            diversity = 1 - avg_similarity
            
            return max(0.0, min(1.0, diversity))
        
        except Exception as e:
            print(f"⚠️  Semantic diversity calculation failed: {e}")
            return None
    
    def _load_ppl_model(self):
        """加载困惑度计算模型"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            print(f"📥 Loading PPL model: {self.ppl_model_name} on {device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(self.ppl_model_name)
            self.ppl_model = AutoModelForCausalLM.from_pretrained(self.ppl_model_name)
            self.ppl_model.to(device)
            self.ppl_model.eval()
            
            print(f"✅ PPL model loaded successfully")
        
        except Exception as e:
            print(f"❌ Failed to load PPL model: {e}")
            print(f"💡 Tip: Install transformers and torch: pip install transformers torch")
            self.use_ppl = False
    
    def _load_semantic_model(self):
        """加载句向量模型"""
        try:
            from sentence_transformers import SentenceTransformer
            
            print(f"📥 Loading semantic model: {self.semantic_model_name}")
            
            self.sentence_model = SentenceTransformer(self.semantic_model_name)
            
            print(f"✅ Semantic model loaded successfully")
        
        except Exception as e:
            print(f"❌ Failed to load semantic model: {e}")
            print(f"💡 Tip: Install sentence-transformers: pip install sentence-transformers")
            self.use_semantic = False
    
    def _get_zero_scores(self) -> Dict[str, float]:
        """返回零分数（用于空文本）"""
        return {
            'distinct_1': 0.0,
            'distinct_2': 0.0,
            'distinct_3': 0.0,
            'perplexity': None,
            'semantic_diversity': None,
            'text_length': 0,
            'word_count': 0,
            'sentence_count': 0
        }
    
    def get_metric_categories(self) -> Dict[str, List[str]]:
        """返回指标分类"""
        return {
            'diversity': ['distinct_1', 'distinct_2', 'distinct_3', 'semantic_diversity'],
            'fluency': ['perplexity'],
            'basic': ['text_length', 'word_count', 'sentence_count']
        }
    
    def get_metric_directions(self) -> Dict[str, bool]:
        """返回指标方向（True=越大越好，False=越小越好）"""
        return {
            'distinct_1': True,
            'distinct_2': True,
            'distinct_3': True,
            'semantic_diversity': True,
            'perplexity': False,  # 越小越好
            'text_length': True,
            'word_count': True,
            'sentence_count': True
        }


if __name__ == '__main__':
    # 测试
    evaluator = CreativeEvaluator(config={'use_ppl': True, 'use_semantic': False})
    
    test_text = """
    春天来了，万物复苏。
    柳树抽出了嫩绿的枝条，花儿绽放出美丽的笑容。
    小鸟在枝头欢快地歌唱，蝴蝶在花丛中翩翩起舞。
    这是一个充满生机和希望的季节。
    """
    
    scores = evaluator.evaluate(test_text)
    
    print("\n📊 Creative Writing Quality Scores:")
    for metric, value in scores.items():
        if value is not None:
            if isinstance(value, float):
                print(f"  {metric}: {value:.4f}")
            else:
                print(f"  {metric}: {value}")
