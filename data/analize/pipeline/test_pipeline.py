"""
数据管道测试脚本 - 验证系统功能
"""
import sys
from pathlib import Path
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """测试模块导入"""
    print("\n[测试] 模块导入...")
    try:
        from data.analize.pipeline import (
            ExperimentDataManager,
            DataPipeline,
            DataValidator,
            validate_all,
            DataSchema,
            PipelineConfig,
        )
        print("✓ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 模块导入失败: {e}")
        return False


def test_schema():
    """测试数据模式"""
    print("\n[测试] 数据模式...")
    try:
        from data.analize.pipeline import DataSchema
        
        schema = DataSchema()
        
        # 测试任务类型
        assert len(schema.TASK_TYPES) > 0, "任务类型为空"
        print(f"  任务类型: {schema.TASK_TYPES}")
        
        # 测试主键
        assert len(schema.PRIMARY_KEYS) > 0, "主键为空"
        print(f"  主键: {schema.PRIMARY_KEYS}")
        
        # 测试列定义
        columns = schema.get_all_columns()
        assert len(columns) > 0, "列定义为空"
        print(f"  总列数: {len(columns)}")
        
        print("✓ 数据模式测试通过")
        return True
    except Exception as e:
        print(f"✗ 数据模式测试失败: {e}")
        return False


def test_config():
    """测试配置"""
    print("\n[测试] 配置...")
    try:
        from data.analize.pipeline import PipelineConfig
        
        config = PipelineConfig()
        
        # 测试路径配置
        assert config.BASE_PATH, "基础路径为空"
        print(f"  基础路径: {config.BASE_PATH}")
        
        # 测试权重配置
        assert config.DEFAULT_WEIGHTS, "默认权重为空"
        print(f"  默认权重: {config.DEFAULT_WEIGHTS}")
        
        print("✓ 配置测试通过")
        return True
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False


def test_data_manager_init():
    """测试数据管理器初始化"""
    print("\n[测试] 数据管理器初始化...")
    try:
        from data.analize.pipeline import ExperimentDataManager
        
        dm = ExperimentDataManager()
        
        # 检查路径
        assert dm.base_path.exists(), "基础路径不存在"
        assert dm.processed_path.exists(), "处理路径不存在"
        assert dm.cache_path.exists(), "缓存路径不存在"
        
        print(f"  基础路径: {dm.base_path}")
        print(f"  处理路径: {dm.processed_path}")
        print(f"  缓存路径: {dm.cache_path}")
        
        print("✓ 数据管理器初始化测试通过")
        return True
    except Exception as e:
        print(f"✗ 数据管理器初始化测试失败: {e}")
        return False


def test_validator():
    """测试数据验证器"""
    print("\n[测试] 数据验证器...")
    try:
        from data.analize.pipeline import DataValidator
        import pandas as pd
        
        validator = DataValidator()
        
        # 创建测试数据
        test_df = pd.DataFrame({
            'model_name': ['model1', 'model2'],
            'task_type': ['code', 'qa'],
            'prompt_id': [1, 2],
            'run_id': [0, 0],
            'latency_s': [1.5, 2.0],
        })
        
        # 验证
        is_valid, errors, warnings = validator.validate_dataframe(test_df)
        
        print(f"  验证结果: {'通过' if is_valid else '失败'}")
        if errors:
            print(f"  错误数: {len(errors)}")
        if warnings:
            print(f"  警告数: {len(warnings)}")
        
        print("✓ 数据验证器测试通过")
        return True
    except Exception as e:
        print(f"✗ 数据验证器测试失败: {e}")
        return False


def test_cache_manager():
    """测试缓存管理器"""
    print("\n[测试] 缓存管理器...")
    try:
        from data.analize.pipeline.utils import CacheManager
        
        cache = CacheManager(cache_dir='data/analize/cache/test')
        
        # 设置缓存
        test_data = {'key': 'value', 'number': 42}
        cache.set('test_key', test_data)
        
        # 获取缓存
        retrieved = cache.get('test_key')
        assert retrieved == test_data, "缓存数据不匹配"
        
        # 统计
        stats = cache.get_stats()
        assert stats['total_items'] > 0, "缓存统计错误"
        
        # 清理
        cache.clear()
        
        print("✓ 缓存管理器测试通过")
        return True
    except Exception as e:
        print(f"✗ 缓存管理器测试失败: {e}")
        return False


def test_performance_utils():
    """测试性能工具"""
    print("\n[测试] 性能工具...")
    try:
        from data.analize.pipeline.utils import measure_time, optimize_dataframe
        import pandas as pd
        import numpy as np
        
        # 测试时间测量
        @measure_time
        def dummy_function():
            import time
            time.sleep(0.1)
        
        dummy_function()
        
        # 测试DataFrame优化
        test_df = pd.DataFrame({
            'id': range(100),
            'category': np.random.choice(['A', 'B', 'C'], 100),
            'value': np.random.randn(100),
        })
        
        optimized = optimize_dataframe(test_df)
        assert len(optimized) == len(test_df), "优化后行数不匹配"
        
        print("✓ 性能工具测试通过")
        return True
    except Exception as e:
        print(f"✗ 性能工具测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("="*70)
    print("数据管道系统测试")
    print("="*70)
    
    tests = [
        ("模块导入", test_imports),
        ("数据模式", test_schema),
        ("配置", test_config),
        ("数据管理器初始化", test_data_manager_init),
        ("数据验证器", test_validator),
        ("缓存管理器", test_cache_manager),
        ("性能工具", test_performance_utils),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"测试 '{name}' 异常: {e}", exc_info=True)
            results.append((name, False))
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠ {total - passed} 个测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
