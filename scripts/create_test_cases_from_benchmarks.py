#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
从标准测试集中抽取和选择问题，创建完整的测试用例集

根据 docs/experiment/experiment_design.md 中的任务安排：
- 知识问答 (QA): 15-20 题
- 数学计算 (Math): 10-15 题
- 代码生成 (Code): 10-12 题
- 翻译 (Translation): 8-10 题
- 逻辑推理 (Reasoning): 8-10 题
- 文本摘要 (Summary): 5-8 题
- 创意写作 (Creative): 5-8 题
- 多轮对话 (Multi-turn): 5-8 组
"""

import json
import random
import re
from pathlib import Path
from typing import List, Dict, Any

# 设置随机种子以确保可复现
random.seed(42)

# 数据路径
BENCHMARK_DIR = Path("data/benchmarks")
OUTPUT_DIR = Path("data/test_cases")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 任务配置
TASK_CONFIG = {
    "qa": {"count": 18, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
    "math": {"count": 12, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
    "code": {"count": 12, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
    "translation": {"count": 10, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
    "reasoning": {"count": 10, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
    "summary": {"count": 6, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
    "creative": {"count": 6, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
    "multi_turn": {"count": 6, "difficulty": {"easy": 0.3, "medium": 0.5, "hard": 0.2}},
}


def load_mmlu_questions(subject: str, count: int) -> List[Dict]:
    """从 MMLU 加载知识问答题目"""
    file_path = BENCHMARK_DIR / "mmlu" / f"mmlu_{subject}_test.json"
    
    if not file_path.exists():
        print(f"警告: {file_path} 不存在")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 随机采样
    sampled = random.sample(data, min(count, len(data)))
    
    questions = []
    for idx, item in enumerate(sampled):
        questions.append({
            "id": f"qa_{subject}_{idx+1:03d}",
            "task_type": "qa",
            "difficulty": "medium",  # MMLU 题目默认为中等难度
            "language": "en",
            "question": item["question"],
            "choices": item["choices"],
            "expected_answer": item["answer"],  # 0-3 的索引
            "expected_answer_text": item["choices"][item["answer"]],
            "temperature": 0.0,
            "max_tokens": 100,
            "repeat": 1,
            "source": f"MMLU-{subject}"
        })
    
    return questions


def load_gsm8k_questions(count: int) -> List[Dict]:
    """从 GSM8K 加载数学计算题目"""
    file_path = BENCHMARK_DIR / "gsm8k" / "test.jsonl"
    
    if not file_path.exists():
        print(f"警告: {file_path} 不存在")
        return []
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    # 随机采样
    sampled = random.sample(data, min(count, len(data)))
    
    questions = []
    for idx, item in enumerate(sampled):
        # 提取最终答案
        answer_text = item["answer"]
        match = re.search(r'####\s*(\d+)', answer_text)
        expected_answer = match.group(1) if match else ""
        
        questions.append({
            "id": f"math_{idx+1:03d}",
            "task_type": "math",
            "difficulty": "medium",
            "language": "en",
            "question": item["question"],
            "expected_answer": expected_answer,
            "expected_steps": answer_text.split("####")[0].strip() if "####" in answer_text else "",
            "temperature": 0.0,
            "max_tokens": 300,
            "repeat": 1,
            "source": "GSM8K"
        })
    
    return questions


def load_humaneval_questions(count: int) -> List[Dict]:
    """从 HumanEval 加载代码生成题目"""
    file_path = BENCHMARK_DIR / "humaneval" / "HumanEval.jsonl"
    
    if not file_path.exists():
        print(f"警告: {file_path} 不存在")
        return []
    
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    
    # 随机采样
    sampled = random.sample(data, min(count, len(data)))
    
    questions = []
    for idx, item in enumerate(sampled):
        questions.append({
            "id": f"code_{idx+1:03d}",
            "task_type": "code",
            "difficulty": "medium",
            "language": "en",
            "question": item["prompt"],
            "entry_point": item["entry_point"],
            "canonical_solution": item["canonical_solution"],
            "test": item["test"],
            "temperature": 0.1,
            "max_tokens": 500,
            "repeat": 3,
            "source": "HumanEval"
        })
    
    return questions


def load_translation_questions(count: int) -> List[Dict]:
    """从翻译测试集加载翻译题目"""
    file_path = BENCHMARK_DIR / "flores200" / "translation_test_set.json"
    
    if not file_path.exists():
        print(f"警告: {file_path} 不存在")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 使用所有可用的翻译对
    sampled = data[:count] if len(data) >= count else data
    
    questions = []
    for idx, item in enumerate(sampled):
        questions.append({
            "id": f"translation_{idx+1:03d}",
            "task_type": "translation",
            "difficulty": item.get("difficulty", "medium"),
            "language": "mixed",  # 双语
            "source_text": item["source"],
            "target_text": item["target"],
            "source_lang": item["source_lang"],
            "target_lang": item["target_lang"],
            "domain": item.get("domain", "general"),
            "temperature": 0.2,
            "max_tokens": 200,
            "repeat": 3,
            "source": "FLORES-200-curated"
        })
    
    return questions


def create_reasoning_questions() -> List[Dict]:
    """创建逻辑推理题目（手动设计）"""
    questions = [
        {
            "id": "reasoning_001",
            "task_type": "reasoning",
            "difficulty": "easy",
            "language": "zh",
            "question": "所有的猫都是哺乳动物。所有的哺乳动物都需要呼吸。小花是一只猫。请问：小花需要呼吸吗？请给出推理过程。",
            "expected_answer": "是",
            "expected_reasoning": ["小花是猫", "猫是哺乳动物", "哺乳动物需要呼吸", "因此小花需要呼吸"],
            "temperature": 0.1,
            "max_tokens": 200,
            "repeat": 3
        },
        {
            "id": "reasoning_002",
            "task_type": "reasoning",
            "difficulty": "medium",
            "language": "zh",
            "question": "如果今天下雨，小明就不去公园。今天小明去了公园。请问今天下雨了吗？",
            "expected_answer": "没有",
            "expected_reasoning": ["如果下雨→不去公园", "去了公园", "因此没有下雨（逆否命题）"],
            "temperature": 0.1,
            "max_tokens": 200,
            "repeat": 3
        },
        {
            "id": "reasoning_003",
            "task_type": "reasoning",
            "difficulty": "medium",
            "language": "zh",
            "question": "在一个房间里有三个开关，分别控制三个灯泡，但你只能进入房间一次。如何确定哪个开关控制哪个灯泡？",
            "expected_answer_contains": ["打开", "时间", "温度", "热"],
            "temperature": 0.1,
            "max_tokens": 300,
            "repeat": 3
        },
        {
            "id": "reasoning_004",
            "task_type": "reasoning",
            "difficulty": "medium",
            "language": "zh",
            "question": "有5个海盗抢到了100颗宝石，他们按照以下规则分配：最凶的海盗提出分配方案，所有海盗投票，如果半数或以上同意就按此方案分配，否则提出方案的海盗被扔进海里，由次凶的海盗继续提案。假设每个海盗都足够聪明且理性，最凶的海盗应该提出什么方案？",
            "expected_answer_contains": ["97", "0", "1", "0", "2"],
            "temperature": 0.1,
            "max_tokens": 400,
            "repeat": 3
        },
        {
            "id": "reasoning_005",
            "task_type": "reasoning",
            "difficulty": "hard",
            "language": "zh",
            "question": "有三个盒子，一个装有两个金币，一个装有两个银币，一个装有一金一银。盒子上的标签都是错的。你只能从一个盒子中取出一枚硬币，如何确定每个盒子的真实内容？",
            "expected_answer_contains": ["一金一银", "标签", "取出"],
            "temperature": 0.1,
            "max_tokens": 300,
            "repeat": 3
        },
        {
            "id": "reasoning_006",
            "task_type": "reasoning",
            "difficulty": "easy",
            "language": "zh",
            "question": "小红比小明高，小明比小刚高。请问：小红和小刚谁更高？",
            "expected_answer": "小红",
            "expected_reasoning": ["小红>小明", "小明>小刚", "因此小红>小刚"],
            "temperature": 0.1,
            "max_tokens": 150,
            "repeat": 3
        },
        {
            "id": "reasoning_007",
            "task_type": "reasoning",
            "difficulty": "medium",
            "language": "zh",
            "question": "一个农夫带着一只狼、一只羊和一棵白菜要过河，船只能载农夫和其中一样东西。如果农夫不在场，狼会吃羊，羊会吃白菜。农夫应该如何安排才能让所有东西都安全过河？",
            "expected_answer_contains": ["羊", "先", "回来", "顺序"],
            "temperature": 0.1,
            "max_tokens": 300,
            "repeat": 3
        },
        {
            "id": "reasoning_008",
            "task_type": "reasoning",
            "difficulty": "hard",
            "language": "zh",
            "question": "有12个外观相同的球，其中11个重量相同，1个重量不同（可能更重或更轻）。用天平称3次，如何找出这个球并确定它是更重还是更轻？",
            "expected_answer_contains": ["分组", "4", "称", "对比"],
            "temperature": 0.1,
            "max_tokens": 500,
            "repeat": 3
        },
        {
            "id": "reasoning_009",
            "task_type": "reasoning",
            "difficulty": "easy",
            "language": "zh",
            "question": "如果所有A都是B，所有B都是C，那么所有A都是C吗？",
            "expected_answer": "是",
            "expected_reasoning": ["三段论", "传递性"],
            "temperature": 0.1,
            "max_tokens": 150,
            "repeat": 3
        },
        {
            "id": "reasoning_010",
            "task_type": "reasoning",
            "difficulty": "medium",
            "language": "zh",
            "question": "在一个岛上，有两种人：说真话的人（总是说真话）和说谎的人（总是说谎）。你遇到两个人A和B，A说：'我们两个都是说谎的人。'请问A和B分别是什么人？",
            "expected_answer": "A是说谎的人，B是说真话的人",
            "expected_reasoning": ["如果A说真话，则矛盾", "因此A说谎", "A的话为假，所以至少一个说真话", "因此B说真话"],
            "temperature": 0.1,
            "max_tokens": 300,
            "repeat": 3
        },
    ]
    
    return questions


def create_summary_questions() -> List[Dict]:
    """创建文本摘要题目（手动设计）"""
    questions = [
        {
            "id": "summary_001",
            "task_type": "summary",
            "difficulty": "medium",
            "language": "zh",
            "source_text": """人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，它企图了解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。人工智能从诞生以来，理论和技术日益成熟，应用领域也不断扩大。可以设想，未来人工智能带来的科技产品，将会是人类智慧的"容器"。人工智能可以对人的意识、思维的信息过程进行模拟。人工智能不是人的智能，但能像人那样思考、也可能超过人的智能。""",
            "instruction": "请将以上文本总结为 50-80 字的摘要，保留关键信息。",
            "temperature": 0.7,
            "max_tokens": 150,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "summary_002",
            "task_type": "summary",
            "difficulty": "medium",
            "language": "zh",
            "source_text": """深度学习是机器学习的一个分支，它基于人工神经网络进行学习。深度学习模型由多层神经网络组成，每一层都会对输入数据进行特征提取和转换。通过大量数据的训练，深度学习模型能够自动学习数据的内在规律和表示层次，从而实现对复杂模式的识别。近年来，深度学习在计算机视觉、自然语言处理、语音识别等领域取得了突破性进展，推动了人工智能技术的快速发展。""",
            "instruction": "请将以上文本总结为 40-60 字的摘要。",
            "temperature": 0.7,
            "max_tokens": 120,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "summary_003",
            "task_type": "summary",
            "difficulty": "medium",
            "language": "zh",
            "source_text": """云计算是一种基于互联网的计算方式，通过这种方式，共享的软硬件资源和信息可以按需提供给计算机和其他设备。云计算依赖资源的共享以达成规模经济，类似基础设施（如电力网）。服务提供商整合大量资源供多个用户使用，用户可以轻易地请求（租借）更多资源，并随时调整使用量，将不需要的资源释放回整个架构，因此用户不需要因短暂的需求高峰而购买大量资源，仅需提升租用量，需求降低时便退租。""",
            "instruction": "请将以上文本总结为 50-70 字的摘要。",
            "temperature": 0.7,
            "max_tokens": 130,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "summary_004",
            "task_type": "summary",
            "difficulty": "easy",
            "language": "zh",
            "source_text": """区块链是一个分布式数据库，通过去中心化和去信任的方式集体维护一个可靠数据库。区块链技术是比特币的底层技术，比特币在没有任何中心化机构运营和管理的情况下，多年运行非常稳定，没有出现过任何问题。区块链的核心优势是去中心化，能够通过运用数据加密、时间戳、分布式共识和经济激励等手段，在节点无需互相信任的分布式系统中实现基于去中心化信用的点对点交易、协调与协作。""",
            "instruction": "请将以上文本总结为 40-60 字的摘要。",
            "temperature": 0.7,
            "max_tokens": 120,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "summary_005",
            "task_type": "summary",
            "difficulty": "hard",
            "language": "zh",
            "source_text": """量子计算是一种遵循量子力学规律调控量子信息单元进行计算的新型计算模式。对照于传统的通用计算机，其理论模型是通用图灵机；通用的量子计算机，其理论模型是用量子力学规律重新诠释的通用图灵机。从可计算的问题来看，量子计算机只能解决传统计算机所能解决的问题，但是从计算的效率上，由于量子力学叠加性的存在，某些已知的量子算法在处理问题时速度要快于传统的通用计算机。量子计算的研究对密码学、优化问题、数据库搜索等领域具有重要意义。""",
            "instruction": "请将以上文本总结为 60-90 字的摘要，保留技术细节。",
            "temperature": 0.7,
            "max_tokens": 150,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "summary_006",
            "task_type": "summary",
            "difficulty": "easy",
            "language": "zh",
            "source_text": """物联网（Internet of Things，IoT）是互联网、传统电信网等信息承载体，让所有能行使独立功能的普通物体实现互联互通的网络。物联网将现实世界数字化，应用范围十分广泛。物联网拉近分散的信息，统整物与物的数字信息，物联网的应用领域主要包括运输和物流、工业制造、健康医疗、智能环境（家庭、办公、工厂）等，具有十分广阔的市场和应用前景。""",
            "instruction": "请将以上文本总结为 40-60 字的摘要。",
            "temperature": 0.7,
            "max_tokens": 120,
            "repeat": 5,
            "source": "manual"
        },
    ]
    
    return questions


def create_creative_questions() -> List[Dict]:
    """创建创意写作题目（手动设计）"""
    questions = [
        {
            "id": "creative_001",
            "task_type": "creative",
            "difficulty": "medium",
            "language": "zh",
            "prompt": "请续写以下故事开头（100-200 字）：\n\n夜幕降临，小镇的街道上空无一人。突然，一道刺眼的光芒从天而降...",
            "temperature": 0.8,
            "max_tokens": 300,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "creative_002",
            "task_type": "creative",
            "difficulty": "medium",
            "language": "zh",
            "prompt": "请以\"春天\"为主题，创作一首现代诗（4-8 行）。",
            "temperature": 0.8,
            "max_tokens": 200,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "creative_003",
            "task_type": "creative",
            "difficulty": "medium",
            "language": "zh",
            "prompt": "为一款新型智能手表撰写广告文案（50-100 字），突出其健康监测功能。",
            "temperature": 0.8,
            "max_tokens": 150,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "creative_004",
            "task_type": "creative",
            "difficulty": "easy",
            "language": "zh",
            "prompt": "用拟人的手法描写一朵花的一天（80-150 字）。",
            "temperature": 0.8,
            "max_tokens": 250,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "creative_005",
            "task_type": "creative",
            "difficulty": "hard",
            "language": "zh",
            "prompt": "以\"时间旅行者的困境\"为题，写一个微型科幻故事（150-250 字）。",
            "temperature": 0.9,
            "max_tokens": 400,
            "repeat": 5,
            "source": "manual"
        },
        {
            "id": "creative_006",
            "task_type": "creative",
            "difficulty": "medium",
            "language": "zh",
            "prompt": "为一家咖啡店设计一句朗朗上口的宣传标语（10-20 字）。",
            "temperature": 0.8,
            "max_tokens": 100,
            "repeat": 5,
            "source": "manual"
        },
    ]
    
    return questions


def create_multi_turn_questions() -> List[Dict]:
    """创建多轮对话题目（手动设计）"""
    questions = [
        {
            "id": "multi_turn_001",
            "task_type": "multi_turn",
            "difficulty": "medium",
            "language": "zh",
            "conversation": [
                {
                    "turn": 1,
                    "user": "我想去北京旅游，有什么推荐的景点吗？",
                    "expected_topics": ["故宫", "长城", "天安门", "颐和园"]
                },
                {
                    "turn": 2,
                    "user": "你刚才提到的第一个景点，门票多少钱？",
                    "context_check": "需要记住第一轮提到的第一个景点"
                },
                {
                    "turn": 3,
                    "user": "那个景点附近有什么好吃的？",
                    "context_check": "需要记住前两轮讨论的景点"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "repeat": 3,
            "source": "manual"
        },
        {
            "id": "multi_turn_002",
            "task_type": "multi_turn",
            "difficulty": "medium",
            "language": "zh",
            "conversation": [
                {
                    "turn": 1,
                    "user": "我现在要告诉你三个人的信息。张三：35岁，工程师，喜欢篮球。李四：28岁，教师，喜欢阅读。王五：42岁，医生，喜欢旅游。"
                },
                {
                    "turn": 2,
                    "user": "请问李四的职业是什么？",
                    "expected_answer": "教师"
                },
                {
                    "turn": 3,
                    "user": "谁的年龄最大？",
                    "expected_answer": "王五"
                },
                {
                    "turn": 4,
                    "user": "喜欢篮球的人是做什么工作的？",
                    "expected_answer": "工程师"
                }
            ],
            "temperature": 0.2,
            "max_tokens": 100,
            "repeat": 3,
            "source": "manual"
        },
        {
            "id": "multi_turn_003",
            "task_type": "multi_turn",
            "difficulty": "easy",
            "language": "zh",
            "conversation": [
                {
                    "turn": 1,
                    "user": "什么是机器学习？",
                    "expected_topics": ["算法", "数据", "模型", "训练"]
                },
                {
                    "turn": 2,
                    "user": "它和深度学习有什么区别？",
                    "context_check": "需要记住第一轮讨论的机器学习概念"
                },
                {
                    "turn": 3,
                    "user": "能举个实际应用的例子吗？",
                    "context_check": "需要结合前两轮的讨论内容"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "repeat": 3,
            "source": "manual"
        },
        {
            "id": "multi_turn_004",
            "task_type": "multi_turn",
            "difficulty": "hard",
            "language": "zh",
            "conversation": [
                {
                    "turn": 1,
                    "user": "我有一个Python列表 [3, 1, 4, 1, 5, 9, 2, 6]，请帮我排序。"
                },
                {
                    "turn": 2,
                    "user": "现在请找出排序后列表中的中位数。",
                    "context_check": "需要记住排序后的列表"
                },
                {
                    "turn": 3,
                    "user": "如果我在原列表末尾添加数字7，中位数会变成多少？",
                    "context_check": "需要基于之前的列表进行计算"
                }
            ],
            "temperature": 0.2,
            "max_tokens": 150,
            "repeat": 3,
            "source": "manual"
        },
        {
            "id": "multi_turn_005",
            "task_type": "multi_turn",
            "difficulty": "medium",
            "language": "zh",
            "conversation": [
                {
                    "turn": 1,
                    "user": "请推荐三本关于人工智能的入门书籍。",
                    "expected_topics": ["机器学习", "深度学习", "AI"]
                },
                {
                    "turn": 2,
                    "user": "第二本书的作者是谁？",
                    "context_check": "需要记住第一轮推荐的第二本书"
                },
                {
                    "turn": 3,
                    "user": "这位作者还写过其他什么书吗？",
                    "context_check": "需要记住第二轮提到的作者"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200,
            "repeat": 3,
            "source": "manual"
        },
        {
            "id": "multi_turn_006",
            "task_type": "multi_turn",
            "difficulty": "easy",
            "language": "zh",
            "conversation": [
                {
                    "turn": 1,
                    "user": "今天天气怎么样？",
                    "expected_topics": ["天气", "温度", "状况"]
                },
                {
                    "turn": 2,
                    "user": "适合户外运动吗？",
                    "context_check": "需要基于第一轮的天气信息判断"
                },
                {
                    "turn": 3,
                    "user": "那我应该穿什么衣服？",
                    "context_check": "需要结合前两轮的天气和活动信息"
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150,
            "repeat": 3,
            "source": "manual"
        },
    ]
    
    return questions


def assign_difficulty(questions: List[Dict], task_type: str) -> List[Dict]:
    """根据配置为题目分配难度等级"""
    config = TASK_CONFIG.get(task_type, {})
    difficulty_dist = config.get("difficulty", {"easy": 0.3, "medium": 0.5, "hard": 0.2})
    
    n_easy = int(len(questions) * difficulty_dist["easy"])
    n_hard = int(len(questions) * difficulty_dist["hard"])
    n_medium = len(questions) - n_easy - n_hard
    
    # 分配难度
    for i, q in enumerate(questions):
        if i < n_easy:
            q["difficulty"] = "easy"
        elif i < n_easy + n_medium:
            q["difficulty"] = "medium"
        else:
            q["difficulty"] = "hard"
    
    return questions


def main():
    """主函数：生成完整的测试用例集"""
    print("="*70)
    print("从标准测试集创建测试用例")
    print("="*70)
    
    all_questions = []
    
    # 1. 知识问答 (QA) - 从 MMLU 抽取
    print("\n1. 加载知识问答题目 (MMLU)...")
    qa_subjects = ["machine_learning", "computer_security", "college_computer_science"]
    qa_questions = []
    per_subject = TASK_CONFIG["qa"]["count"] // len(qa_subjects)
    
    for subject in qa_subjects:
        questions = load_mmlu_questions(subject, per_subject)
        qa_questions.extend(questions)
    
    qa_questions = assign_difficulty(qa_questions[:TASK_CONFIG["qa"]["count"]], "qa")
    all_questions.extend(qa_questions)
    print(f"   ✓ 已加载 {len(qa_questions)} 道知识问答题")
    
    # 2. 数学计算 (Math) - 从 GSM8K 抽取
    print("\n2. 加载数学计算题目 (GSM8K)...")
    math_questions = load_gsm8k_questions(TASK_CONFIG["math"]["count"])
    math_questions = assign_difficulty(math_questions, "math")
    all_questions.extend(math_questions)
    print(f"   ✓ 已加载 {len(math_questions)} 道数学计算题")
    
    # 3. 代码生成 (Code) - 从 HumanEval 抽取
    print("\n3. 加载代码生成题目 (HumanEval)...")
    code_questions = load_humaneval_questions(TASK_CONFIG["code"]["count"])
    code_questions = assign_difficulty(code_questions, "code")
    all_questions.extend(code_questions)
    print(f"   ✓ 已加载 {len(code_questions)} 道代码生成题")
    
    # 4. 翻译 (Translation) - 从 FLORES-200 抽取
    print("\n4. 加载翻译题目 (FLORES-200)...")
    translation_questions = load_translation_questions(TASK_CONFIG["translation"]["count"])
    all_questions.extend(translation_questions)
    print(f"   ✓ 已加载 {len(translation_questions)} 道翻译题")
    
    # 5. 逻辑推理 (Reasoning) - 手动创建
    print("\n5. 创建逻辑推理题目...")
    reasoning_questions = create_reasoning_questions()
    # 扩展到目标数量，修改ID避免重复
    base_questions = reasoning_questions.copy()
    while len(reasoning_questions) < TASK_CONFIG["reasoning"]["count"]:
        for q in base_questions:
            if len(reasoning_questions) >= TASK_CONFIG["reasoning"]["count"]:
                break
            new_q = q.copy()
            new_q["id"] = f"{q['id'].rsplit('_', 1)[0]}_{len(reasoning_questions) + 1:03d}"
            reasoning_questions.append(new_q)
    reasoning_questions = reasoning_questions[:TASK_CONFIG["reasoning"]["count"]]
    all_questions.extend(reasoning_questions)
    print(f"   ✓ 已创建 {len(reasoning_questions)} 道逻辑推理题")
    
    # 6. 文本摘要 (Summary) - 手动创建
    print("\n6. 创建文本摘要题目...")
    summary_questions = create_summary_questions()
    base_questions = summary_questions.copy()
    while len(summary_questions) < TASK_CONFIG["summary"]["count"]:
        for q in base_questions:
            if len(summary_questions) >= TASK_CONFIG["summary"]["count"]:
                break
            new_q = q.copy()
            new_q["id"] = f"{q['id'].rsplit('_', 1)[0]}_{len(summary_questions) + 1:03d}"
            summary_questions.append(new_q)
    summary_questions = summary_questions[:TASK_CONFIG["summary"]["count"]]
    all_questions.extend(summary_questions)
    print(f"   ✓ 已创建 {len(summary_questions)} 道文本摘要题")
    
    # 7. 创意写作 (Creative) - 手动创建
    print("\n7. 创建创意写作题目...")
    creative_questions = create_creative_questions()
    base_questions = creative_questions.copy()
    while len(creative_questions) < TASK_CONFIG["creative"]["count"]:
        for q in base_questions:
            if len(creative_questions) >= TASK_CONFIG["creative"]["count"]:
                break
            new_q = q.copy()
            new_q["id"] = f"{q['id'].rsplit('_', 1)[0]}_{len(creative_questions) + 1:03d}"
            creative_questions.append(new_q)
    creative_questions = creative_questions[:TASK_CONFIG["creative"]["count"]]
    all_questions.extend(creative_questions)
    print(f"   ✓ 已创建 {len(creative_questions)} 道创意写作题")
    
    # 8. 多轮对话 (Multi-turn) - 手动创建
    print("\n8. 创建多轮对话题目...")
    multi_turn_questions = create_multi_turn_questions()
    base_questions = multi_turn_questions.copy()
    while len(multi_turn_questions) < TASK_CONFIG["multi_turn"]["count"]:
        for q in base_questions:
            if len(multi_turn_questions) >= TASK_CONFIG["multi_turn"]["count"]:
                break
            new_q = q.copy()
            new_q["id"] = f"{q['id'].rsplit('_', 1)[0]}_{len(multi_turn_questions) + 1:03d}"
            multi_turn_questions.append(new_q)
    multi_turn_questions = multi_turn_questions[:TASK_CONFIG["multi_turn"]["count"]]
    all_questions.extend(multi_turn_questions)
    print(f"   ✓ 已创建 {len(multi_turn_questions)} 组多轮对话")
    
    # 生成元数据
    metadata = {
        "version": "1.0",
        "created_date": "2026-03-02",
        "description": "综合测试用例集，涵盖 8 种任务类型，从标准测试集抽取",
        "total_tasks": len(all_questions),
        "task_distribution": {
            "qa": len(qa_questions),
            "math": len(math_questions),
            "code": len(code_questions),
            "translation": len(translation_questions),
            "reasoning": len(reasoning_questions),
            "summary": len(summary_questions),
            "creative": len(creative_questions),
            "multi_turn": len(multi_turn_questions)
        },
        "sources": {
            "MMLU": len(qa_questions),
            "GSM8K": len(math_questions),
            "HumanEval": len(code_questions),
            "FLORES-200": len(translation_questions),
            "Manual": len(reasoning_questions) + len(summary_questions) + len(creative_questions) + len(multi_turn_questions)
        }
    }
    
    # 保存完整测试用例集
    output_file = OUTPUT_DIR / "test_cases_comprehensive.json"
    output_data = {
        "metadata": metadata,
        "tasks": all_questions
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("✅ 测试用例创建完成！")
    print("="*70)
    print(f"\n输出文件: {output_file}")
    print(f"总题目数: {len(all_questions)}")
    print("\n任务分布:")
    for task_type, count in metadata["task_distribution"].items():
        print(f"  - {task_type}: {count} 题")
    
    print("\n数据来源:")
    for source, count in metadata["sources"].items():
        print(f"  - {source}: {count} 题")
    
    # 按任务类型分别保存
    print("\n按任务类型保存...")
    for task_type in ["qa", "math", "code", "translation", "reasoning", "summary", "creative", "multi_turn"]:
        task_questions = [q for q in all_questions if q["task_type"] == task_type]
        if task_questions:
            task_file = OUTPUT_DIR / f"test_cases_{task_type}.json"
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "task_type": task_type,
                        "count": len(task_questions),
                        "created_date": "2026-03-02"
                    },
                    "tasks": task_questions
                }, f, indent=2, ensure_ascii=False)
            print(f"  ✓ {task_file.name}")
    
    print("\n" + "="*70)
    print("所有文件已保存到:", OUTPUT_DIR)
    print("="*70)


if __name__ == "__main__":
    main()
