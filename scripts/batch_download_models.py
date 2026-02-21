#!/usr/bin/env python3
"""
批量下载Hugging Face模型

根据配置文件批量下载模型，支持：
- 按优先级过滤
- 按类别过滤
- 并发控制
- 错误重试
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

try:
    import yaml
except ImportError:
    print("错误: 缺少pyyaml依赖")
    print("请运行: pip install pyyaml")
    sys.exit(1)

# 导入下载器
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.download_hf_model import HuggingFaceModelDownloader


class BatchModelDownloader:
    """批量模型下载器"""
    
    def __init__(self, config_path: str = "configs/models_to_download.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.downloader = HuggingFaceModelDownloader(
            output_dir=self.config.get('download_config', {}).get('output_dir', 'models/huggingface')
        )
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def get_models_by_category(self, category: str) -> List[Dict[str, Any]]:
        """获取指定类别的模型"""
        return self.config.get(category, [])
    
    def get_models_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """获取指定优先级的模型"""
        all_models = []
        
        # 遍历所有类别
        for key, value in self.config.items():
            if key.endswith('_models') and isinstance(value, list):
                all_models.extend(value)
        
        # 过滤优先级
        return [m for m in all_models if m.get('priority') == priority]
    
    def get_all_models(self) -> List[Dict[str, Any]]:
        """获取所有模型"""
        all_models = []
        
        for key, value in self.config.items():
            if key.endswith('_models') and isinstance(value, list):
                all_models.extend(value)
        
        return all_models
    
    def download_models(
        self,
        models: List[Dict[str, Any]],
        skip_existing: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        批量下载模型
        
        Args:
            models: 模型列表
            skip_existing: 跳过已存在的模型
            dry_run: 仅显示将要下载的模型，不实际下载
            
        Returns:
            下载统计信息
        """
        stats = {
            'total': len(models),
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        print(f"\n{'='*80}")
        print(f"批量下载模型")
        print(f"{'='*80}\n")
        print(f"计划下载 {len(models)} 个模型\n")
        
        if dry_run:
            print("🔍 预览模式（不会实际下载）\n")
        
        for idx, model_info in enumerate(models, 1):
            model_name = model_info['name']
            quantize = model_info.get('quantize')
            
            print(f"\n[{idx}/{len(models)}] {model_name}")
            print(f"   描述: {model_info.get('description', 'N/A')}")
            print(f"   预估大小: {model_info.get('size_estimate', 'N/A')}")
            
            if quantize:
                print(f"   量化: {quantize}")
            
            if model_info.get('requires_auth'):
                print(f"   ⚠️  需要授权访问")
            
            if dry_run:
                print(f"   ✓ 将会下载")
                continue
            
            # 检查是否需要授权
            if model_info.get('requires_auth') and not self.downloader.token:
                print(f"   ❌ 跳过: 需要HF_TOKEN环境变量")
                stats['skipped'] += 1
                continue
            
            try:
                # 下载模型
                self.downloader.download_model(
                    model_name=model_name,
                    quantize=quantize,
                    force=not skip_existing
                )
                
                stats['success'] += 1
                print(f"   ✅ 下载成功")
                
                # 短暂延迟，避免请求过快
                time.sleep(2)
                
            except Exception as e:
                error_msg = f"{model_name}: {str(e)}"
                stats['errors'].append(error_msg)
                stats['failed'] += 1
                print(f"   ❌ 下载失败: {str(e)}")
                
                # 询问是否继续
                if idx < len(models):
                    response = input("\n继续下载下一个模型? (yes/no): ")
                    if response.lower() not in ['yes', 'y']:
                        print("\n⚠️  批量下载已取消")
                        break
        
        # 打印统计信息
        print(f"\n{'='*80}")
        print(f"下载完成")
        print(f"{'='*80}\n")
        print(f"总计: {stats['total']}")
        print(f"成功: {stats['success']}")
        print(f"失败: {stats['failed']}")
        print(f"跳过: {stats['skipped']}")
        
        if stats['errors']:
            print(f"\n错误详情:")
            for error in stats['errors']:
                print(f"  - {error}")
        
        print()
        
        return stats


def main():
    parser = argparse.ArgumentParser(
        description="批量下载Hugging Face模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载所有高优先级模型
  python batch_download_models.py --priority high
  
  # 下载小型模型类别
  python batch_download_models.py --category small_models
  
  # 预览将要下载的模型
  python batch_download_models.py --priority high --dry-run
  
  # 下载所有模型
  python batch_download_models.py --all
  
  # 使用自定义配置文件
  python batch_download_models.py --config my_models.yaml --priority high
        """
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="configs/models_to_download.yaml",
        help="配置文件路径"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        choices=["small_models", "medium_models", "large_models", "specialized_models", "multilingual_models"],
        help="按类别过滤模型"
    )
    
    parser.add_argument(
        "--priority",
        type=str,
        choices=["high", "medium", "low"],
        help="按优先级过滤模型"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="下载所有模型"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="预览模式，不实际下载"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新下载已存在的模型"
    )
    
    args = parser.parse_args()
    
    try:
        downloader = BatchModelDownloader(config_path=args.config)
        
        # 确定要下载的模型
        if args.all:
            models = downloader.get_all_models()
        elif args.category:
            models = downloader.get_models_by_category(args.category)
        elif args.priority:
            models = downloader.get_models_by_priority(args.priority)
        else:
            print("错误: 请指定 --category, --priority 或 --all")
            parser.print_help()
            sys.exit(1)
        
        if not models:
            print("⚠️  没有找到符合条件的模型")
            sys.exit(0)
        
        # 下载模型
        stats = downloader.download_models(
            models=models,
            skip_existing=not args.force,
            dry_run=args.dry_run
        )
        
        # 根据结果设置退出码
        if stats['failed'] > 0:
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  批量下载已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
