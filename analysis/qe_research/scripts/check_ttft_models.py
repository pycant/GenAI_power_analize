"""检查TTFT数据中的模型数量"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from raw_data_analyzer_complete import RawDataAnalyzer
import pandas as pd

analyzer = RawDataAnalyzer()
analyzer.load_all_data()

# 统计每个模型的TTFT数据
data = []
for exp in analyzer.experiments:
    ttft = analyzer._calc_ttft(exp)
    if ttft:
        data.append({
            'model': exp['model_name'],
            'ttft': ttft
        })

if data:
    df = pd.DataFrame(data)
    print('=' * 60)
    print('TTFT数据统计')
    print('=' * 60)
    print(f'\n每个模型的数据点数量:')
    model_counts = df.groupby('model').size().sort_values(ascending=False)
    for model, count in model_counts.items():
        print(f'  {model}: {count} 个数据点')
    
    print(f'\n总共有 {len(df["model"].unique())} 个不同的模型')
    print(f'\n模型列表:')
    for i, model in enumerate(sorted(df['model'].unique()), 1):
        print(f'  {i}. {model}')
else:
    print('未找到TTFT数据')
