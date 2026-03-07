"""
测试 load_process_quality_data() 函数

验证新的统一质量数据加载接口
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pareto_core import load_process_quality_data
import pandas as pd


def test_entropy_method():
    """测试1: 熵权法"""
    print("\n" + "="*80)
    print("测试1: 熵权法处理")
    print("="*80)
    
    try:
        df = load_process_quality_data(
            task_name='code',
            method='entropy',
            normalize_method='minmax',
            verbose=True
        )
        
        print(f"\n✓ 熵权法测试成功")
        print(f"  数据形状: {df.shape}")
        print(f"  列名: {list(df.columns)}")
        print(f"\n前5行:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_method():
    """测试2: 单一指标"""
    print("\n" + "="*80)
    print("测试2: 单一指标处理")
    print("="*80)
    
    try:
        df = load_process_quality_data(
            task_name='code',
            method='single',
            quality_column='compilation_rate',
            verbose=True
        )
        
        print(f"\n✓ 单一指标测试成功")
        print(f"  数据形状: {df.shape}")
        print(f"\n前5行:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pca_method():
    """测试3: PCA降维"""
    print("\n" + "="*80)
    print("测试3: PCA降维处理")
    print("="*80)
    
    try:
        df = load_process_quality_data(
            task_name='reasoning',
            method='pca',
            n_components=1,
            verbose=True
        )
        
        print(f"\n✓ PCA降维测试成功")
        print(f"  数据形状: {df.shape}")
        print(f"\n前5行:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mean_method():
    """测试4: 简单平均"""
    print("\n" + "="*80)
    print("测试4: 简单平均处理")
    print("="*80)
    
    try:
        df = load_process_quality_data(
            task_name='creative',
            method='mean',
            normalize_method='minmax',
            verbose=True
        )
        
        print(f"\n✓ 简单平均测试成功")
        print(f"  数据形状: {df.shape}")
        print(f"\n前5行:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_weights():
    """测试5: 自定义权重"""
    print("\n" + "="*80)
    print("测试5: 自定义权重处理")
    print("="*80)
    
    try:
        # 自定义权重
        custom_weights = {
            'compilation_rate': 0.5,
            'test_pass_rate': 0.3,
            'code_length': 0.2
        }
        
        df = load_process_quality_data(
            task_name='code',
            method='custom',
            weights=custom_weights,
            verbose=True
        )
        
        print(f"\n✓ 自定义权重测试成功")
        print(f"  数据形状: {df.shape}")
        print(f"\n前5行:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_tasks():
    """测试6: 所有任务类型"""
    print("\n" + "="*80)
    print("测试6: 所有任务类型（熵权法）")
    print("="*80)
    
    tasks = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']
    results = {}
    
    for task in tasks:
        try:
            print(f"\n测试任务: {task.upper()}")
            df = load_process_quality_data(
                task_name=task,
                method='entropy',
                verbose=False
            )
            
            print(f"  ✓ {task}: {len(df)} 模型")
            results[task] = True
            
        except Exception as e:
            print(f"  ✗ {task}: {e}")
            results[task] = False
    
    # 汇总
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n{'='*80}")
    print(f"测试结果: {success_count}/{total_count} 个任务成功")
    print(f"{'='*80}")
    
    return success_count == total_count


def test_comparison():
    """测试7: 方法对比"""
    print("\n" + "="*80)
    print("测试7: 不同方法对比（code任务）")
    print("="*80)
    
    try:
        methods = {
            'entropy': {},
            'mean': {},
            'single': {'quality_column': 'compilation_rate'},
            'pca': {'n_components': 1}
        }
        
        all_results = {}
        
        for method, kwargs in methods.items():
            print(f"\n处理方法: {method.upper()}")
            df = load_process_quality_data(
                task_name='code',
                method=method,
                verbose=False,
                **kwargs
            )
            all_results[method] = df.set_index('model')['quality']
        
        # 合并结果
        comparison_df = pd.DataFrame(all_results)
        
        print(f"\n✓ 方法对比完成")
        print(f"\n不同方法的质量得分对比:")
        print(comparison_df.round(4))
        
        # 计算相关性
        print(f"\n方法间相关性:")
        correlation = comparison_df.corr()
        print(correlation.round(3))
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_pareto():
    """测试8: 与帕累托分析集成"""
    print("\n" + "="*80)
    print("测试8: 与帕累托分析集成")
    print("="*80)
    
    try:
        from pareto_core import (
            load_process_quality_data,
            load_energy_speed_data,
            MODEL_MAPPING,
            DATA_PATHS
        )
        
        # 1. 加载质量数据
        print("\n步骤1: 加载质量数据（熵权法）")
        quality_df = load_process_quality_data(
            task_name='code',
            method='entropy',
            verbose=False
        )
        
        # 2. 加载能耗和速度数据
        print("步骤2: 加载能耗和速度数据")
        energy_dict, speed_dict = load_energy_speed_data(
            'code',
            DATA_PATHS['energy'],
            DATA_PATHS['speed']
        )
        
        # 3. 合并数据
        print("步骤3: 合并数据")
        merged_data = []
        for _, row in quality_df.iterrows():
            model_short = row['model']
            model_full = MODEL_MAPPING.get(model_short)
            
            if model_full and model_full in energy_dict and model_full in speed_dict:
                merged_data.append({
                    'model': model_short,
                    'model_full': model_full,
                    'quality': row['quality'],
                    'energy': energy_dict[model_full],
                    'speed': speed_dict[model_full]
                })
        
        merged_df = pd.DataFrame(merged_data)
        
        print(f"\n✓ 集成测试成功")
        print(f"  合并后数据: {len(merged_df)} 个模型")
        print(f"  列: {list(merged_df.columns)}")
        print(f"\n前5行:")
        print(merged_df.head())
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("load_process_quality_data() 函数测试")
    print("="*80)
    
    tests = [
        ("熵权法", test_entropy_method),
        ("单一指标", test_single_method),
        ("PCA降维", test_pca_method),
        ("简单平均", test_mean_method),
        ("自定义权重", test_custom_weights),
        ("所有任务类型", test_all_tasks),
        ("方法对比", test_comparison),
        ("帕累托集成", test_integration_with_pareto),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ 测试 '{test_name}' 发生异常: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # 打印测试总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{status}: {test_name}")
    
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n{'='*80}")
    print(f"总体结果: {success_count}/{total_count} 个测试通过")
    print(f"{'='*80}")
    
    if success_count == total_count:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total_count - success_count} 个测试失败")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
