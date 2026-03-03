#!/usr/bin/env python3
"""
模型管理脚本

功能：
- 列出已下载的模型
- 删除模型
- 查看模型详情
- 清理缓存
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class ModelManager:
    """模型管理器"""
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.registry_path = self.models_dir / "model_registry.json"
        self.hf_dir = self.models_dir / "huggingface"
    
    def list_models(self, verbose: bool = False) -> List[Dict[str, Any]]:
        """列出所有已下载的模型"""
        if not self.registry_path.exists():
            print("📭 未找到模型注册表，可能还没有下载任何模型")
            return []
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        models = registry.get("models", [])
        
        if not models:
            print("📭 没有已注册的模型")
            return []
        
        print(f"\n{'='*80}")
        print(f"已下载的模型 (共 {len(models)} 个)")
        print(f"{'='*80}\n")
        
        total_size = 0
        for idx, model in enumerate(models, 1):
            print(f"{idx}. {model['name']}")
            print(f"   源: {model['source']}")
            print(f"   路径: {model['path']}")
            print(f"   大小: {model['size_gb']} GB")
            print(f"   格式: {model['format']}")
            
            if model.get('quantization'):
                print(f"   量化: {model['quantization']}")
            
            if model.get('downloaded_at'):
                print(f"   下载时间: {model['downloaded_at']}")
            
            if verbose and model.get('last_used'):
                print(f"   最后使用: {model['last_used']}")
            
            # 检查路径是否存在
            if not Path(model['path']).exists():
                print(f"   ⚠️  警告: 模型文件不存在")
            
            total_size += model['size_gb']
            print()
        
        print(f"{'='*80}")
        print(f"总占用空间: {total_size:.2f} GB")
        print(f"{'='*80}\n")
        
        return models
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """获取模型详细信息"""
        if not self.registry_path.exists():
            raise FileNotFoundError("模型注册表不存在")
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        for model in registry.get("models", []):
            if model['name'] == model_name or model['source'] == model_name:
                return model
        
        raise ValueError(f"未找到模型: {model_name}")
    
    def delete_model(self, model_name: str, confirm: bool = False) -> None:
        """删除模型"""
        try:
            model_info = self.get_model_info(model_name)
        except ValueError as e:
            print(f"❌ {str(e)}")
            return
        
        model_path = Path(model_info['path'])
        
        if not confirm:
            print(f"\n⚠️  即将删除模型:")
            print(f"   名称: {model_info['name']}")
            print(f"   路径: {model_path}")
            print(f"   大小: {model_info['size_gb']} GB")
            
            response = input("\n确认删除? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ 取消删除")
                return
        
        # 删除模型文件
        if model_path.exists():
            print(f"\n🗑️  正在删除模型文件...")
            shutil.rmtree(model_path)
            print(f"✅ 已删除: {model_path}")
        else:
            print(f"⚠️  模型文件不存在: {model_path}")
        
        # 从注册表中移除
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        registry['models'] = [
            m for m in registry['models']
            if m['name'] != model_info['name'] and m['source'] != model_info['source']
        ]
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已从注册表中移除")
    
    def clean_cache(self, confirm: bool = False) -> None:
        """清理Hugging Face缓存"""
        cache_dir = self.hf_dir / "cache"
        
        if not cache_dir.exists():
            print("📭 缓存目录不存在")
            return
        
        # 计算缓存大小
        cache_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
        cache_size_gb = cache_size / (1024**3)
        
        if cache_size_gb < 0.01:
            print("✨ 缓存已经很干净了")
            return
        
        if not confirm:
            print(f"\n⚠️  即将清理缓存:")
            print(f"   路径: {cache_dir}")
            print(f"   大小: {cache_size_gb:.2f} GB")
            
            response = input("\n确认清理? (yes/no): ")
            if response.lower() not in ['yes', 'y']:
                print("❌ 取消清理")
                return
        
        print(f"\n🧹 正在清理缓存...")
        shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 已清理 {cache_size_gb:.2f} GB 缓存")
    
    def verify_models(self) -> None:
        """验证所有模型的完整性"""
        if not self.registry_path.exists():
            print("📭 未找到模型注册表")
            return
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        models = registry.get("models", [])
        
        if not models:
            print("📭 没有已注册的模型")
            return
        
        print(f"\n{'='*80}")
        print(f"验证模型完整性")
        print(f"{'='*80}\n")
        
        issues = []
        
        for model in models:
            model_path = Path(model['path'])
            print(f"检查: {model['name']}")
            
            if not model_path.exists():
                print(f"   ❌ 模型目录不存在")
                issues.append(f"{model['name']}: 目录不存在")
                continue
            
            # 检查配置文件
            config_file = model_path / "config.json"
            if not config_file.exists():
                print(f"   ❌ 缺少 config.json")
                issues.append(f"{model['name']}: 缺少配置文件")
            else:
                print(f"   ✓ 配置文件存在")
            
            # 检查模型权重
            has_weights = any([
                (model_path / "pytorch_model.bin").exists(),
                (model_path / "model.safetensors").exists(),
                list(model_path.glob("*.safetensors")),
                list(model_path.glob("pytorch_model-*.bin"))
            ])
            
            if not has_weights:
                print(f"   ❌ 缺少模型权重文件")
                issues.append(f"{model['name']}: 缺少权重文件")
            else:
                print(f"   ✓ 模型权重存在")
            
            print()
        
        print(f"{'='*80}")
        if issues:
            print(f"⚠️  发现 {len(issues)} 个问题:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"✅ 所有模型验证通过")
        print(f"{'='*80}\n")
    
    def update_last_used(self, model_name: str) -> None:
        """更新模型最后使用时间"""
        if not self.registry_path.exists():
            return
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        for model in registry.get("models", []):
            if model['name'] == model_name or model['source'] == model_name:
                model['last_used'] = datetime.now().isoformat()
                break
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(
        description="管理已下载的Hugging Face模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 列出所有模型
  python manage_models.py --list
  
  # 查看模型详情
  python manage_models.py --info Qwen2.5-7B-Instruct
  
  # 删除模型
  python manage_models.py --delete Qwen2.5-7B-Instruct
  
  # 清理缓存
  python manage_models.py --clean-cache
  
  # 验证模型完整性
  python manage_models.py --verify
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="列出所有已下载的模型"
    )
    
    parser.add_argument(
        "--info",
        type=str,
        metavar="MODEL_NAME",
        help="查看指定模型的详细信息"
    )
    
    parser.add_argument(
        "--delete",
        type=str,
        metavar="MODEL_NAME",
        help="删除指定模型"
    )
    
    parser.add_argument(
        "--clean-cache",
        action="store_true",
        help="清理Hugging Face缓存"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="验证所有模型的完整性"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    
    parser.add_argument(
        "--yes",
        action="store_true",
        help="自动确认所有操作"
    )
    
    parser.add_argument(
        "--models-dir",
        type=str,
        default="models",
        help="模型目录 (默认: models)"
    )
    
    args = parser.parse_args()
    
    manager = ModelManager(models_dir=args.models_dir)
    
    try:
        if args.list:
            manager.list_models(verbose=args.verbose)
        
        elif args.info:
            model_info = manager.get_model_info(args.info)
            print(f"\n模型详细信息:")
            print(json.dumps(model_info, indent=2, ensure_ascii=False))
            print()
        
        elif args.delete:
            manager.delete_model(args.delete, confirm=args.yes)
        
        elif args.clean_cache:
            manager.clean_cache(confirm=args.yes)
        
        elif args.verify:
            manager.verify_models()
        
        else:
            parser.print_help()
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
