"""检查为什么某些实验缺少TTFT数据"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from raw_data_analyzer_complete import RawDataAnalyzer
from collections import Counter

analyzer = RawDataAnalyzer()
analyzer.load_all_data()

print('=' * 60)
print('TTFT数据缺失原因分析')
print('=' * 60)

# 统计所有模型
all_models = Counter()
models_with_ttft = Counter()
models_no_monitoring = Counter()
models_no_events = Counter()
models_no_inference_start = Counter()
models_no_first_token = Counter()

for exp in analyzer.experiments:
    model = exp['model_name']
    all_models[model] += 1
    
    # 检查是否有monitoring_data
    if not exp.get('monitoring_data'):
        models_no_monitoring[model] += 1
        continue
    
    # 检查是否有events
    events = exp['monitoring_data'].get('events', [])
    if not events:
        models_no_events[model] += 1
        continue
    
    # 检查是否有inference_start和first_token事件
    has_start = any(e.get('event') == 'inference_start' for e in events)
    has_first = any(e.get('event') == 'first_token' for e in events)
    
    if not has_start:
        models_no_inference_start[model] += 1
    if not has_first:
        models_no_first_token[model] += 1
    
    if has_start and has_first:
        models_with_ttft[model] += 1

print(f'\n总实验数: {len(analyzer.experiments)}')
print(f'总模型数: {len(all_models)}')

print('\n所有模型的实验数量:')
for model, count in sorted(all_models.items()):
    print(f'  {model}: {count} 个实验')

print('\n有TTFT数据的模型:')
for model, count in sorted(models_with_ttft.items()):
    print(f'  {model}: {count}/{all_models[model]} 个实验有TTFT')

print('\n缺失原因统计:')
if models_no_monitoring:
    print('\n  缺少monitoring_data:')
    for model, count in sorted(models_no_monitoring.items()):
        print(f'    {model}: {count} 个实验')

if models_no_events:
    print('\n  缺少events:')
    for model, count in sorted(models_no_events.items()):
        print(f'    {model}: {count} 个实验')

if models_no_inference_start:
    print('\n  缺少inference_start事件:')
    for model, count in sorted(models_no_inference_start.items()):
        print(f'    {model}: {count} 个实验')

if models_no_first_token:
    print('\n  缺少first_token事件:')
    for model, count in sorted(models_no_first_token.items()):
        print(f'    {model}: {count} 个实验')
