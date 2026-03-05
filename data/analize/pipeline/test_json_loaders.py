"""
测试JSON数据加载器
"""
import sys
from pathlib import Path
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_summary_loader():
    """测试Summary JSON加载器"""
    print("\n" + "="*70)
    print("测试 Summary JSON 加载器")
    print("="*70)
    
    try:
        from data.analize.pipeline.converters import SummaryJsonLoader
        
        loader = SummaryJsonLoader()
        
        # 列出可用模型
        print("\n可用模型目录:")
        available = loader.get_available_models()
        for model in available:
            print(f"  ✓ {model}")
        
        if not available:
            print("  ⚠ 未找到任何模型数据")
            return False
        
        # 加载数据
        print("\n加载数据...")
        df = loader.load_all_summary_data()
        
        print(f"\n✓ 数据加载成功")
        print(f"  - 总行数: {len(df)}")
        print(f"  - 总列数: {len(df.columns)}")
        
        # 显示列名
        print(f"\n列名 ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # 模型统计
        if 'model_name' in df.columns:
            print("\n模型统计:")
            model_counts = df['model_name'].value_counts()
            for model, count in model_counts.items():
                print(f"  - {model}: {count} 条记录")
        
        # 任务类型统计
        if 'task_type' in df.columns:
            print("\n任务类型统计:")
            task_counts = df['task_type'].value_counts()
            for task, count in task_counts.items():
                print(f"  - {task}: {count} 条记录")
        
        # 性能指标统计
        print("\n性能指标统计:")
        perf_cols = ['latency_s', 'toks_per_s', 'gpu_energy_j']
        available_cols = [col for col in perf_cols if col in df.columns]
        
        if available_cols:
            print(df[available_cols].describe())
        else:
            print("  ⚠ 未找到性能指标列")
        
        # 显示前几行
        print("\n前3行数据:")
        print(df.head(3))
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


def test_raw_loader():
    """测试Raw JSON加载器"""
    print("\n" + "="*70)
    print("测试 Raw JSON 加载器")
    print("="*70)
    
    try:
        from data.analize.pipeline.converters import RawJsonLoader
        
        loader = RawJsonLoader()
        
        # 列出可用模型
        print("\n可用模型目录:")
        available = loader.get_available_models()
        for model in available:
            print(f"  ✓ {model}")
        
        if not available:
            print("  ⚠ 未找到任何模型数据")
            return False
        
        # 加载数据
        print("\n加载数据...")
        df = loader.load_all_raw_data()
        
        print(f"\n✓ 数据加载成功")
        print(f"  - 总行数: {len(df)}")
        print(f"  - 总列数: {len(df.columns)}")
        
        # 显示列名
        print(f"\n列名 ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        # 模型统计
        if 'model_name' in df.columns:
            print("\n模型统计:")
            model_counts = df['model_name'].value_counts()
            for model, count in model_counts.items():
                print(f"  - {model}: {count} 条记录")
        
        # 任务类型统计
        if 'task_type' in df.columns:
            print("\n任务类型统计:")
            task_counts = df['task_type'].value_counts()
            for task, count in task_counts.items():
                print(f"  - {task}: {count} 条记录")
        
        # 显示前几行
        print("\n前3行数据:")
        print(df.head(3))
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


def test_pipeline_integration():
    """测试管道集成"""
    print("\n" + "="*70)
    print("测试数据管道集成")
    print("="*70)
    
    try:
        from data.analize.pipeline import DataPipeline
        
        print("\n创建数据管道...")
        pipeline = DataPipeline()
        
        print("\n运行完整管道...")
        pipeline.run_full_pipeline()
        
        print("\n✓ 管道运行成功")
        
        # 检查输出文件
        processed_path = Path('data/analize/processed')
        if processed_path.exists():
            print("\n生成的文件:")
            for file in processed_path.glob('*.parquet'):
                size_mb = file.stat().st_size / 1024 / 1024
                print(f"  ✓ {file.name} ({size_mb:.2f} MB)")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        return False


def main():
    """主测试函数"""
    print("="*70)
    print("JSON数据加载器测试套件")
    print("="*70)
    
    tests = [
        ("Summary JSON加载器", test_summary_loader),
        ("Raw JSON加载器", test_raw_loader),
        ("数据管道集成", test_pipeline_integration),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"测试 '{name}' 异常: {e}", exc_info=True)
            results.append((name, False))
        
        input("\n按回车继续下一个测试...")
    
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
    sys.exit(main())
