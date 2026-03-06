import json

with open('data/deepseek_8b_ol_q4km/experiment_results_20260303_203028_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    exp = data[0]
    print('监控数据结构:')
    if 'monitoring_data' in exp:
        mon = exp['monitoring_data']
        print(f'  keys: {list(mon.keys())}')
        if 'measurements' in mon:
            meas = mon['measurements']
            print(f'  measurements type: {type(meas)}')
            if isinstance(meas, dict):
                print(f'  measurements keys: {list(meas.keys())[:10]}')
                first_key = list(meas.keys())[0]
                print(f'  first measurement ({first_key}): {meas[first_key]}')
