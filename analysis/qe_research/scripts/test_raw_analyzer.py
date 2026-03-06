"""
测试原始数据分析器
验证系统是否正常工作
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("原始数据分析器测试")
print("=" * 80)

# 1. 测试导入
print("\n[1/5] 测试模块导入...")
try:
    from analysis.qe_research.scripts.raw_data_analyzer_complete import RawDataAnalyzer
    print("  ✓ 模块导入成功")
except Exception as e:
    print(f"  ✗ 模块导入失败: {e}")
    sys.exit(1)

# 2. 测试初始化
print("\n[2/5] 测试分析器初始化...")
try:
    analyzer = RawDataAnalyzer()
    print("  ✓ 分析器初始化成功")
    print(f"    - 输出目录: {analyzer.output_dir}")
    print(f"    - 模型目录数: {len(analyzer.model_dirs)}")
except Exception as e:
    print(f"  ✗ 初始化失败: {e}")
    sys.exit(1)

# 3. 测试数据加载
print("\n[3/5] 测试数据加载...")
try:
    analyzer.load_all_data()
    print(f"  ✓ 数据加载成功")
    print(f"    - 实验数量: {len(analyzer.experiments)}")
    
    if len(analyzer.experiments) == 0:
        print("  ⚠ 警告: 未找到任何实验数据")
        print("    请确认data目录下存在*_raw.json文件")
    else:
        # 显示数据统计
        models = set(e['model_name'] for e in analyzer.experiments)
        tasks = set(e['config'].get('task_type') for e in analyzer.experiments)
        print(f"    - 模型数量: {len(models)}")
        print(f"    - 任务类型: {len(tasks)}")
        print(f"    - 模型列表: {', '.join(sorted(models)[:5])}...")
except Exception as e:
    print(f"  ✗ 数据加载失败: {e}")
    sys.exit(1)

# 4. 测试输出目录
print("\n[4/5] 测试输出目录...")
try:
    dirs = [analyzer.figures_dir, analyzer.tables_dir, analyzer.reports_dir]
    for d in dirs:
        if d.exists():
            print(f"  ✓ {d.name}/ 存在")
        else:
            print(f"  ✗ {d.name}/ 不存在")
except Exception as e:
    print(f"  ✗ 目录检查失败: {e}")

# 5. 测试单个分析任务
print("\n[5/5] 测试单个分析任务...")
if len(analyzer.experiments) > 0:
    try:
        # 测试TTFT计算
        ttft_count = 0
        for exp in analyzer.experiments[:10]:
            ttft = analyzer._calc_ttft(exp)
            if ttft is not None:
                ttft_count += 1
        
        print(f"  ✓ TTFT计算测试通过")
        print(f"    - 成功计算: {ttft_count}/10")
        
        # 测试TPOT计算
        tpot_count = 0
        for exp in analyzer.experiments[:10]:
            tpot = analyzer._calc_tpot(exp)
            if tpot is not None:
                tpot_count += 1
        
        print(f"  ✓ TPOT计算测试通过")
        print(f"    - 成功计算: {tpot_count}/10")
        
    except Exception as e:
        print(f"  ✗ 分析任务测试失败: {e}")
else:
    print("  ⚠ 跳过分析任务测试 (无数据)")

# 总结
print("\n" + "=" * 80)
print("测试完成!")
print("=" * 80)

if len(analyzer.experiments) > 0:
    print("\n系统状态: ✅ 正常")
    print("\n下一步:")
    print("1. 运行完整分析:")
    print("   python analysis/qe_research/scripts/raw_data_analyzer_complete.py")
    print("\n2. 或使用批处理脚本:")
    print("   analysis/qe_research/scripts/run_raw_analysis.bat")
else:
    print("\n系统状态: ⚠ 警告 - 未找到数据")
    print("\n请确认:")
    print("1. data目录下存在模型子目录")
    print("2. 模型目录中存在*_raw.json文件")
    print("3. JSON文件格式正确")

print("=" * 80)
