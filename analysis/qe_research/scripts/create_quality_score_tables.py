"""
创建质量评分表格
生成以模型为列、评分指标为行的表格，每个任务类型对应一个CSV文件
保留原始评分指标，不进行赋权处理
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

# 配置日志
log_dir = Path('analysis/qe_research/logs')
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'create_quality_score_tables.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class QualityScoreTableCreator:
    """质量评分表格创建器"""
    
    def __init__(self):
        self.quality_data_root = Path('data/analize/results')
        self.output_dir = Path('analysis/qe_research/results/quality_scores')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 任务类型配置（只指定目录和文件，指标将自动检测）
        self.task_configs = {
            'code': {
                'dir': 'code_quality',
                'score_file': 'quality_scores_code_v2.csv'
            },
            'creative': {
                'dir': 'creative_quality',
                'score_file': 'creative_quality_scores_with_perplexity.csv'
            },
            'math': {
                'dir': 'math_quality',
                'score_file': 'math_quality_scores.csv'
            },
            'qa': {
                'dir': 'qa_quality',
                'score_file': 'qa_quality_scores.csv'
            },
            'reasoning': {
                'dir': 'reasoning_quality',
                'score_file': 'reasoning_quality_scores.csv'
            },
            'summary': {
                'dir': 'summary_quality',
                'score_file': 'summary_quality_scores_with_bartscore.csv'
            },
            'translation': {
                'dir': 'translation_quality',
                'score_file': 'translation_quality_scores.csv'
            }
        }
        
        # 需要排除的列（非指标列）
        self.exclude_columns = [
            'model', 'question_id', 'experiment_id', 'task_type', 'prompt',
            'response', 'text', 'timestamp', 'language_pair', 'domain',
            'reasoning_type', 'answer', 'reference', 'source', 'target'
        ]
        
        logger.info("质量评分表格创建器初始化完成")
    
    def load_quality_scores(self, task_type: str) -> pd.DataFrame:
        """加载指定任务类型的质量评分数据"""
        config = self.task_configs.get(task_type)
        if not config:
            logger.warning(f"未知任务类型: {task_type}")
            return None
        
        score_file = self.quality_data_root / config['dir'] / config['score_file']
        
        if not score_file.exists():
            logger.warning(f"质量评分文件不存在: {score_file}")
            return None
        
        try:
            df = pd.read_csv(score_file, encoding='utf-8')
            logger.info(f"✓ 加载 {task_type}: {len(df)} 条记录")
            return df
        except Exception as e:
            logger.error(f"✗ 加载 {task_type} 失败: {e}")
            return None
    
    def get_metric_columns(self, df: pd.DataFrame) -> list:
        """自动检测数据中的指标列（排除元数据列）"""
        # 获取所有数值型列
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # 排除非指标列
        metric_cols = [col for col in numeric_cols if col not in self.exclude_columns]
        
        return metric_cols
    
    def create_score_table(self, task_type: str) -> pd.DataFrame:
        """为指定任务创建评分表格（模型为列，指标为行）"""
        logger.info(f"\n处理任务: {task_type}")
        
        # 加载数据
        df = self.load_quality_scores(task_type)
        if df is None or df.empty:
            return None
        
        # 检查数据中是否有model列
        if 'model' not in df.columns:
            logger.error(f"数据中缺少 'model' 列")
            return None
        
        # 自动检测指标列
        available_metrics = self.get_metric_columns(df)
        
        if not available_metrics:
            logger.error(f"没有可用的数值型指标列")
            logger.info(f"可用列: {df.columns.tolist()}")
            return None
        
        logger.info(f"  检测到 {len(available_metrics)} 个指标: {available_metrics}")
        
        # 按模型分组，计算每个指标的平均值
        result_data = {}
        
        for model in df['model'].unique():
            model_df = df[df['model'] == model]
            model_scores = {}
            
            for metric in available_metrics:
                # 计算平均值，忽略NaN
                values = model_df[metric].dropna()
                if len(values) > 0:
                    model_scores[metric] = values.mean()
                else:
                    model_scores[metric] = np.nan
            
            result_data[model] = model_scores
        
        # 转换为DataFrame（指标为行，模型为列）
        result_df = pd.DataFrame(result_data)
        
        # 排序
        result_df = result_df.sort_index()  # 按指标名排序
        result_df = result_df[sorted(result_df.columns)]  # 按模型名排序
        
        # 设置索引名称
        result_df.index.name = '评分指标 \\ 模型'
        
        logger.info(f"  生成表格: {len(result_df)} 指标 × {len(result_df.columns)} 模型")
        
        return result_df
    
    def format_table(self, df: pd.DataFrame, task_type: str) -> pd.DataFrame:
        """格式化表格数值"""
        if df is None or df.empty:
            return df
        
        # 根据指标类型决定保留小数位数
        formatted_df = df.copy()
        
        for metric in formatted_df.index:
            if 'count' in metric.lower():
                # 计数类指标保留整数
                formatted_df.loc[metric] = formatted_df.loc[metric].round(0)
            elif 'perplexity' in metric.lower():
                # 困惑度保留2位小数
                formatted_df.loc[metric] = formatted_df.loc[metric].round(2)
            else:
                # 其他评分指标保留4位小数
                formatted_df.loc[metric] = formatted_df.loc[metric].round(4)
        
        return formatted_df
    
    def save_table(self, df: pd.DataFrame, task_type: str):
        """保存表格"""
        if df is None or df.empty:
            logger.warning(f"跳过保存 {task_type}（无数据）")
            return
        
        # 格式化表格
        formatted_df = self.format_table(df, task_type)
        
        # 保存格式化版本
        output_file = self.output_dir / f'{task_type}_scores.csv'
        formatted_df.to_csv(output_file, encoding='utf-8-sig')
        logger.info(f"  ✓ 保存格式化版本: {output_file}")
        
        # 保存原始数值版本（用于后续计算）
        raw_output_file = self.output_dir / f'{task_type}_scores_raw.csv'
        df.to_csv(raw_output_file, encoding='utf-8-sig')
        logger.info(f"  ✓ 保存原始版本: {raw_output_file}")
        
        # 打印预览
        print(f"\n{'='*80}")
        print(f"{task_type.upper()} 任务质量评分")
        print(f"{'='*80}")
        print(formatted_df.to_string())
        print()
    
    def create_aggregated_table(self):
        """创建跨任务的聚合表格（使用所有数值指标的平均值）"""
        logger.info("\n创建跨任务聚合表格...")
        
        all_scores = {}
        
        for task_type in self.task_configs.keys():
            df = self.load_quality_scores(task_type)
            if df is None or df.empty:
                continue
            
            if 'model' not in df.columns:
                continue
            
            # 获取所有数值型指标
            metric_cols = self.get_metric_columns(df)
            
            if not metric_cols:
                continue
            
            # 计算每个模型的平均得分（所有指标的平均）
            for model in df['model'].unique():
                model_df = df[df['model'] == model]
                
                # 计算所有指标的平均值
                all_values = []
                for metric in metric_cols:
                    values = model_df[metric].dropna()
                    if len(values) > 0:
                        all_values.extend(values.tolist())
                
                if all_values:
                    avg_score = np.mean(all_values)
                    
                    if model not in all_scores:
                        all_scores[model] = {}
                    
                    all_scores[model][task_type] = avg_score
        
        if not all_scores:
            logger.warning("没有可用的聚合数据")
            return None
        
        # 转换为DataFrame
        agg_df = pd.DataFrame(all_scores)
        agg_df = agg_df.sort_index()  # 按任务排序
        agg_df = agg_df[sorted(agg_df.columns)]  # 按模型排序
        agg_df.index.name = '任务类型 \\ 模型'
        
        # 格式化
        agg_df = agg_df.round(4)
        
        # 保存
        output_file = self.output_dir / 'aggregated_scores_by_task.csv'
        agg_df.to_csv(output_file, encoding='utf-8-sig')
        logger.info(f"✓ 保存聚合表格: {output_file}")
        
        # 打印预览
        print(f"\n{'='*80}")
        print("跨任务聚合评分 (所有指标平均)")
        print(f"{'='*80}")
        print(agg_df.to_string())
        print()
        
        return agg_df
    
    def generate_all_tables(self):
        """生成所有表格"""
        logger.info("\n" + "=" * 80)
        logger.info("开始生成质量评分表格")
        logger.info("=" * 80)
        
        # 生成各任务的表格
        for task_type in self.task_configs.keys():
            try:
                df = self.create_score_table(task_type)
                self.save_table(df, task_type)
            except Exception as e:
                logger.error(f"处理 {task_type} 时出错: {e}")
                import traceback
                traceback.print_exc()
        
        # 生成聚合表格
        try:
            self.create_aggregated_table()
        except Exception as e:
            logger.error(f"创建聚合表格时出错: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("\n" + "=" * 80)
        logger.info("表格生成完成!")
        logger.info(f"输出目录: {self.output_dir}/")
        logger.info("=" * 80)
    
    def generate_summary_report(self):
        """生成汇总报告"""
        report_path = self.output_dir / 'README.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 质量评分表格\n\n")
            f.write("**生成时间**: " + pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') + "\n\n")
            f.write("---\n\n")
            
            f.write("## 表格说明\n\n")
            f.write("本目录包含各任务类型的质量评分表格，以模型为列、评分指标为行的矩阵格式展示。\n\n")
            f.write("所有评分均为原始指标值，未进行赋权处理。\n\n")
            
            f.write("### 表格列表\n\n")
            for i, (task_type, config) in enumerate(self.task_configs.items(), 1):
                f.write(f"{i}. **{task_type}_scores.csv** - {task_type.upper()}任务质量评分\n")
                f.write(f"   - 数据源: `{config['dir']}/{config['score_file']}`\n")
                f.write(f"   - 指标: 自动检测所有数值型指标\n")
            
            f.write(f"\n{len(self.task_configs)+1}. **aggregated_scores_by_task.csv** - 跨任务聚合评分汇总\n")
            f.write("   - 每个任务的所有指标平均值\n\n")
            
            f.write("### 数据来源\n\n")
            f.write("- 数据源: `data/analize/results/*/quality_*_scores*.csv`\n")
            f.write("- 各任务类型的详细质量评估结果\n\n")
            
            f.write("### 文件版本\n\n")
            f.write("每个任务有两个版本的文件：\n")
            f.write("- **格式化版本** (如 `code_scores.csv`): 数值已格式化，便于阅读\n")
            f.write("- **原始版本** (如 `code_scores_raw.csv`): 保留完整精度，便于后续计算\n\n")
            
            f.write("### 使用方法\n\n")
            f.write("```python\n")
            f.write("import pandas as pd\n\n")
            f.write("# 读取某个任务的评分表格\n")
            f.write("df = pd.read_csv('code_scores.csv', index_col=0)\n\n")
            f.write("# 查看特定指标的所有模型得分\n")
            f.write("print(df.loc['compilation_rate'])  # 示例指标\n\n")
            f.write("# 查看特定模型的所有指标得分\n")
            f.write("print(df['qwen3:8b'])\n\n")
            f.write("# 读取跨任务聚合表格\n")
            f.write("agg_df = pd.read_csv('aggregated_scores_by_task.csv', index_col=0)\n")
            f.write("print(agg_df)\n")
            f.write("```\n\n")
            
            f.write("### 指标说明\n\n")
            f.write("详细的指标说明请参考：\n")
            f.write("- [METRICS_GUIDE.md](../../METRICS_GUIDE.md) - 完整指标说明文档\n")
            f.write("- [data/analize/results/README.md](../../../data/analize/results/README.md) - 质量评估结果说明\n\n")
            
            f.write("### 注意事项\n\n")
            f.write("- 表格中的NaN值表示该模型在该指标上没有数据\n")
            f.write("- 所有数值均为该模型在该任务下多个问题的平均值\n")
            f.write("- 指标自动从原始数据中检测，包含所有数值型列\n")
            f.write("- 不同任务的指标含义和取值范围可能不同，详见指标说明文档\n")
            f.write("- 评分未进行归一化或赋权，保留原始评估结果\n\n")
            
            f.write("---\n\n")
            f.write("**生成脚本**: `analysis/qe_research/scripts/create_quality_score_tables.py`\n")
        
        logger.info(f"汇总报告已生成: {report_path}")


def main():
    """主函数"""
    print("\n" + "=" * 80)
    print("创建质量评分表格")
    print("=" * 80 + "\n")
    
    creator = QualityScoreTableCreator()
    
    # 生成所有表格
    creator.generate_all_tables()
    
    # 生成报告
    creator.generate_summary_report()
    
    print("\n完成!")


if __name__ == '__main__':
    main()
