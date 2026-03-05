"""
快速开始脚本 - 初始化和测试数据管道
"""
import sys
import logging
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from data.analize.pipeline import (
    ExperimentDataManager,
    DataPipeline,
    validate_all,
)


def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('data/analize/logs/pipeline.log', encoding='utf-8')
        ]
    )


def main():
    """主函数"""
    print("="*70)
    print("数据管道系统 - 快速开始")
    print("="*70)
    
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 1. 创建数据管理器
        print("\n[步骤 1/5] 初始化数据管理器...")
        dm = ExperimentDataManager()
        print("✓ 数据管理器创建成功")
        
        # 2. 运行数据管道（首次运行或强制刷新）
        print("\n[步骤 2/5] 运行数据管道...")
        response = input("是否运行完整的数据转换管道？(y/n，首次运行必须选y): ").lower()
        
        if response == 'y':
            dm.initialize_pipeline(force=True)
            print("✓ 数据管道运行完成")
        else:
            print("⊙ 跳过数据管道，使用现有数据")
        
        # 3. 验证数据
        print("\n[步骤 3/5] 验证数据完整性...")
        is_valid = dm.validate_data()
        
        if is_valid:
            print("✓ 数据验证通过")
        else:
            print("⚠ 数据验证发现问题，请查看上方详情")
        
        # 4. 加载和探索数据
        print("\n[步骤 4/5] 加载数据...")
        df = dm.load_all_data()
        print(f"✓ 数据加载完成: {len(df)} 行, {len(df.columns)} 列")
        
        # 显示基本信息
        print("\n数据概览:")
        print(f"  - 模型数量: {len(dm.list_models())}")
        print(f"  - 任务类型: {', '.join(dm.list_tasks())}")
        print(f"  - 数据形状: {df.shape}")
        
        # 显示前几行
        print("\n前5行数据:")
        print(df.head())
        
        # 5. 生成示例分析
        print("\n[步骤 5/5] 生成示例分析...")
        
        # 按任务统计
        print("\n按任务类型统计:")
        task_stats = df.groupby('task_type').size()
        for task, count in task_stats.items():
            print(f"  - {task}: {count} 条记录")
        
        # 按模型统计
        print("\n按模型统计:")
        model_stats = df.groupby('model_name').size()
        for model, count in model_stats.items():
            print(f"  - {model}: {count} 条记录")
        
        # 质量指标示例
        if 'quality_score' in df.columns:
            print("\n质量得分统计:")
            print(df['quality_score'].describe())
        
        # 效率指标示例
        if 'latency_s' in df.columns:
            print("\n延迟统计(秒):")
            print(df['latency_s'].describe())
        
        # 元数据
        print("\n系统元数据:")
        metadata = dm.get_metadata()
        print(f"  - 最后更新: {metadata.get('last_updated', 'N/A')}")
        print(f"  - 总行数: {metadata.get('total_rows', 0)}")
        print(f"  - 总列数: {metadata.get('total_columns', 0)}")
        
        print("\n" + "="*70)
        print("快速开始完成！")
        print("="*70)
        
        # 使用提示
        print("\n接下来你可以:")
        print("  1. 使用 dm.get_by_task('code') 获取特定任务的数据")
        print("  2. 使用 dm.get_by_model('qwen3:8b') 获取特定模型的数据")
        print("  3. 使用 dm.get_quality_metrics() 获取质量指标")
        print("  4. 使用 dm.compute_composite_score() 计算复合得分")
        print("  5. 查看 data/analize/pipeline/README.md 了解更多用法")
        
        # 交互式探索（可选）
        print("\n" + "-"*70)
        response = input("是否进入交互式探索模式？(y/n): ").lower()
        
        if response == 'y':
            interactive_explore(dm)
        
    except Exception as e:
        logger.error(f"快速开始失败: {str(e)}", exc_info=True)
        print(f"\n❌ 错误: {str(e)}")
        print("请检查日志文件: data/analize/logs/pipeline.log")
        return 1
    
    return 0


def interactive_explore(dm: ExperimentDataManager):
    """交互式探索模式"""
    print("\n" + "="*70)
    print("交互式探索模式")
    print("="*70)
    print("输入命令进行数据探索，输入 'help' 查看帮助，输入 'exit' 退出")
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd == 'exit':
                print("退出交互模式")
                break
            
            elif cmd == 'help':
                print("\n可用命令:")
                print("  models          - 列出所有模型")
                print("  tasks           - 列出所有任务类型")
                print("  task <name>     - 查看特定任务的数据")
                print("  model <name>    - 查看特定模型的数据")
                print("  quality         - 查看质量指标")
                print("  efficiency      - 查看效率指标")
                print("  stats           - 查看汇总统计")
                print("  metadata        - 查看元数据")
                print("  exit            - 退出")
            
            elif cmd == 'models':
                models = dm.list_models()
                print(f"\n共 {len(models)} 个模型:")
                for model in models:
                    print(f"  - {model}")
            
            elif cmd == 'tasks':
                tasks = dm.list_tasks()
                print(f"\n共 {len(tasks)} 个任务类型:")
                for task in tasks:
                    print(f"  - {task}")
            
            elif cmd.startswith('task '):
                task_name = cmd.split(' ', 1)[1]
                df = dm.get_by_task(task_name)
                print(f"\n任务 '{task_name}' 数据:")
                print(df.head())
                print(f"\n形状: {df.shape}")
            
            elif cmd.startswith('model '):
                model_name = cmd.split(' ', 1)[1]
                df = dm.get_by_model(model_name)
                print(f"\n模型 '{model_name}' 数据:")
                print(df.head())
                print(f"\n形状: {df.shape}")
            
            elif cmd == 'quality':
                df = dm.get_quality_metrics(normalized=True)
                print("\n质量指标:")
                print(df.describe())
            
            elif cmd == 'efficiency':
                df = dm.get_efficiency_metrics(normalized=True)
                print("\n效率指标:")
                print(df.describe())
            
            elif cmd == 'stats':
                stats = dm.get_summary_stats(by='model_task')
                print("\n汇总统计:")
                print(stats)
            
            elif cmd == 'metadata':
                metadata = dm.get_metadata()
                print("\n元数据:")
                import json
                print(json.dumps(metadata, indent=2, ensure_ascii=False))
            
            else:
                print(f"未知命令: {cmd}. 输入 'help' 查看帮助")
        
        except Exception as e:
            print(f"错误: {str(e)}")


if __name__ == '__main__':
    sys.exit(main())
