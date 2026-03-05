# -*- coding: utf-8 -*-
"""
逻辑推理任务配置文件

包含标准答案和关键推理要点
"""

# 标准答案配置
REASONING_REFERENCE_ANSWERS = {
    'q01': {
        'answer': '从标签"一金一银"的盒子中取硬币',
        'key_points': ['标签错误', '一金一银', '推断其他盒子'],
        'reasoning_type': 'logic_puzzle',
        'explanation': '因为所有标签都是错的，标签"一金一银"的盒子实际不是一金一银，取出一枚硬币后可以确定该盒子内容，进而推断其他盒子'
    },
    'q02': {
        'answer': '是，小花需要呼吸',
        'key_points': ['三段论', '猫是哺乳动物', '哺乳动物需要呼吸'],
        'reasoning_type': 'deductive',
        'explanation': '三段论推理：所有猫都是哺乳动物，所有哺乳动物都需要呼吸，小花是猫，因此小花需要呼吸'
    },
    'q03': {
        'answer': '利用灯泡的温度状态：开关1开后关(热)，开关2开(亮)，开关3不动(冷)',
        'key_points': ['温度', '开关1热', '开关2亮', '开关3冷'],
        'reasoning_type': 'logic_puzzle',
        'explanation': '打开开关1等待后关闭，打开开关2，进入房间：亮的是开关2，热的是开关1，冷的是开关3'
    },
    'q04': {
        'answer': '小红更高',
        'key_points': ['传递性', '小红>小明', '小明>小刚', '小红>小刚'],
        'reasoning_type': 'deductive',
        'explanation': '根据传递性：小红>小明，小明>小刚，因此小红>小刚'
    },
    'q05': {
        'answer': '1号海盗提案：97,0,1,0,2 或 97,0,1,2,0',
        'key_points': ['逆向归纳', '博弈论', '最小化分配', '保证通过'],
        'reasoning_type': 'game_theory',
        'explanation': '使用逆向归纳法，从最后一个海盗开始推理，1号海盗需要至少3票（包括自己），给3号和5号各1-2颗宝石即可'
    }
}
