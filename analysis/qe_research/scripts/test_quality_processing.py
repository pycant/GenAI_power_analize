"""
质量数据处理模块测试脚本

测试 process_quality_data.py 的所有功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from pareto_core.process_quality_data import QualityDataProcessor, quick_process
import pandas as pd


def test_basic_loading():
    """测试1: 基础数据加载"""
    print("\n" + "="*80)
    print("测试1: 基础数据加载")
    print("="*80)
    
    try:
        processor = QualityDataProcessor(task_name='code', verbose=True)
        data = processor.load_quality_data()
        
        print(f"\n✓ 数据加载成功")
        print(f"  形状: {data.shape}")
        print(f"  模型: {list(data.index)}")
        print(f"  指标: {list(data.columns)}")
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        return False


def test_normalization():
    """测试2: 归一化方法"""
    print("\n" + "="*80)
    print("测试2: 归一化方法")
    print("="*80)
    
    try:
        processor = QualityDataProcessor(task_name='code', verbose=False)
        data = processor.load_quality_data()
        
        methods = ['minmax', 'zscore', 'robust', 'maxabs']
        
        for method in methods:
            print(f"\n测试 {method.upper()} 归一化...")
            normalized = processor.normalize(method=method)
            
            print(f"  ✓ {method} 归一化成功")
            print(f"    均值范围: [{normalized.mean().min():.3f}, {normalized.mean().max():.3f}]")
            print(f"    标准差范围: [{normalized.std().min():.3f}, {normalized.std().max():.3f}]")
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        return False


def test_entropy_weights():
    """测试3: 熵权法"""
    print("\n" + "="*80)
    print("测试3: 熵权法计算权重")
    print("="*80)
    
    try:
        processor = QualityDataProcessor(task_name='reasoning', verbose=True)
        data = processor.load_quality_data()
        
        # 计算权重
        weights = processor.calculate_entropy_weights()
        
        # 验证权重和为1
        total_weight = sum(weights.values())
        print(f"\n权重总和: {total_weight:.6f}")
        
        if abs(total_weight - 1.0) < 1e-6:
            print("✓ 权重归一化正确")
        else:
            print("✗ 权重归一化错误")
            return False
        
        # 计算加权得分
        quality_score = processor.get_weighted_quality_score(weights)
        print(f"\n✓ 加权得分计算成功")
        print(f"  得分范围: [{quality_score.min():.4f}, {quality_score.max():.4f}]")
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pca():
    """测试4: PCA降维"""
    print("\n" + "="*80)
    print("测试4: PCA降维")
    print("="*80)
    
    try:
        processor = QualityDataProcessor(task_name='reasoning', verbose=True)
        data = processor.load_quality_data()
        
        # 测试固定主成分数量
        print("\n测试1: 固定主成分数量（n=2）")
        pca_result = processor.apply_pca(n_components=2)
        
        print(f"✓ PCA降维成功")
        print(f"  降维后形状: {pca_result['transformed'].shape}")
        print(f"  累积方差: {pca_result['cumulative_variance_ratio'][-1]:.2%}")
        
        # 测试方差比例
        print("\n测试2: 保留90%方差")
        pca_result2 = processor.apply_pca(n_components=0.9)
        
        print(f"✓ PCA降维成功")
        print(f"  实际主成分数: {pca_result2['n_components']}")
        print(f"  累积方差: {pca_result2['cumulative_variance_ratio'][-1]:.2%}")
        
        return True
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export():
    """测试5: 结果导出"""
    print("\n" + "="*80)
    print("测试5: 结果导出")
    print("="*80)
    
    try:
        processor = QualityDataProcessor(task_name='code', verbose=False)
        
        # 执行完整流程
        data = processor.load_quality_data()
        normalized = processor.normalize(method='minmax')
        weights = processor.calculate_entropy_weights()
        quality_score = processor.get_weighted_quality_score(weights)
        pca_result = processor.apply_pca(n_components=2)
        
        # 导出结果
        output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'test_quality_processing'
        processor.export_results(output_dir, prefix='test')
        
        # 验证文件是否生成
        expected_files = [
            'test_quality_data.csv',
            'test_normalized_data.csv',
            'test_entropy_weights.csv',
            'test_pca_transformed.csv',
            'test_pca_components.csv',
            'test_pca_variance.csv'
        ]
        
        print(f"\n检查导出文件:")
        all_exist = True
        for filename in expected_files:
            filepath = output_dir / filename
            exists = filepath.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {filename}")
            if not exists:
                all_exist = False
        
        if all_exist:
            print(f"\n✓ 所有文件导出成功")
            print(f"  输出目录: {output_dir}")
            return True
        else:
            print(f"\n✗ 部分文件导出失败")
            return False
            
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quick_process():
    """测试6: 一键处理"""
    print("\n" + "="*80)
    print("测试6: 一键处理流程")
    print("="*80)
    
    try:
        output_dir = project_root / 'analysis' / 'qe_research' / 'results' / 'test_quick_process'
        
        results = quick_process(
            task_name='qa',
            normalize_method='minmax',
            use_entropy=True,
            use_pca=True,
            n_components=2,
            output_dir=output_dir
        )
        
        # 验证结果
        required_keys = ['raw_data', 'normalized_data', 'entropy_weights', 
                        'weighted_quality_score', 'pca_result']
        
        print(f"\n检查返回结果:")
        all_present = True
        for key in required_keys:
            present = key in results
            status = "✓" if present else "✗"
            print(f"  {status} {key}")
            if not present:
                all_present = False
        
        if all_present:
            print(f"\n✓ 一键处理成功")
            return True
        else:
            print(f"\n✗ 部分结果缺失")
            return False
            
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_tasks():
    """测试7: 所有任务类型"""
    print("\n" + "="*80)
    print("测试7: 所有任务类型")
    print("="*80)
    
    tasks = ['code', 'creative', 'math', 'qa', 'reasoning', 'summary', 'translation']
    results = {}
    
    for task in tasks:
        try:
            print(f"\n测试任务: {task.upper()}")
            processor = QualityDataProcessor(task_name=task, verbose=False)
            data = processor.load_quality_data()
            
            print(f"  ✓ {task}: {data.shape[0]} 模型, {data.shape[1]} 指标")
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


def main():
    """运行所有测试"""
    print("\n" + "="*80)
    print("质量数据处理模块测试")
    print("="*80)
    
    tests = [
        ("基础数据加载", test_basic_loading),
        ("归一化方法", test_normalization),
        ("熵权法", test_entropy_weights),
        ("PCA降维", test_pca),
        ("结果导出", test_export),
        ("一键处理", test_quick_process),
        ("所有任务类型", test_all_tasks),
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
