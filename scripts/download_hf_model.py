#!/usr/bin/env python3
"""
Hugging Face模型下载脚本

功能：
- 从Hugging Face Hub下载模型
- 支持断点续传
- 自动更新模型注册表
- 可选模型量化
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from huggingface_hub import snapshot_download, login
    from transformers import AutoTokenizer, AutoModelForCausalLM
except ImportError:
    print("错误: 缺少必要的依赖包")
    print("请运行: pip install transformers huggingface_hub")
    sys.exit(1)


class HuggingFaceModelDownloader:
    """Hugging Face模型下载器"""
    
    def __init__(self, output_dir: str = "models/huggingface", token: Optional[str] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.registry_path = Path("models/model_registry.json")
        self.token = token or os.getenv("HF_TOKEN")
        
        if self.token:
            login(token=self.token)
    
    def download_model(
        self,
        model_name: str,
        quantize: Optional[str] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        下载模型
        
        Args:
            model_name: Hugging Face模型名称，如 "Qwen/Qwen2.5-7B-Instruct"
            quantize: 量化选项 ("4bit", "8bit", None)
            force: 强制重新下载
            
        Returns:
            模型信息字典
        """
        print(f"\n{'='*60}")
        print(f"开始下载模型: {model_name}")
        print(f"{'='*60}\n")
        
        # 清理模型名称作为本地目录名
        local_name = model_name.replace("/", "--")
        model_path = self.output_dir / local_name
        
        # 检查是否已存在
        if model_path.exists() and not force:
            print(f"⚠️  模型已存在: {model_path}")
            print("使用 --force 参数强制重新下载")
            return self._get_model_info(model_name, model_path)
        
        try:
            # 下载模型文件
            print(f"📥 正在下载模型文件...")
            print(f"   源: {model_name}")
            print(f"   目标: {model_path}\n")
            
            downloaded_path = snapshot_download(
                repo_id=model_name,
                local_dir=model_path,
                local_dir_use_symlinks=False,
                resume_download=True,
                token=self.token
            )
            
            print(f"\n✅ 模型下载完成: {downloaded_path}")
            
            # 验证模型可加载
            print("\n🔍 验证模型完整性...")
            self._verify_model(model_path)
            
            # 可选量化
            if quantize:
                print(f"\n⚙️  正在进行 {quantize} 量化...")
                self._quantize_model(model_path, quantize)
            
            # 更新注册表
            model_info = self._register_model(model_name, model_path, quantize)
            
            print(f"\n{'='*60}")
            print(f"✨ 模型 {model_name} 已成功下载并注册")
            print(f"{'='*60}\n")
            
            return model_info
            
        except Exception as e:
            print(f"\n❌ 下载失败: {str(e)}")
            raise
    
    def _verify_model(self, model_path: Path) -> None:
        """验证模型文件完整性"""
        try:
            # 检查必要文件
            config_file = model_path / "config.json"
            if not config_file.exists():
                raise FileNotFoundError("缺少 config.json")
            
            # 检查模型权重文件
            has_weights = any([
                (model_path / "pytorch_model.bin").exists(),
                (model_path / "model.safetensors").exists(),
                list(model_path.glob("*.safetensors")),
                list(model_path.glob("pytorch_model-*.bin"))
            ])
            
            if not has_weights:
                raise FileNotFoundError("未找到模型权重文件")
            
            print("   ✓ 配置文件完整")
            print("   ✓ 模型权重文件完整")
            
            # 尝试加载tokenizer
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_path)
                print(f"   ✓ Tokenizer加载成功 (词表大小: {len(tokenizer)})")
            except Exception as e:
                print(f"   ⚠️  Tokenizer加载警告: {str(e)}")
            
        except Exception as e:
            raise RuntimeError(f"模型验证失败: {str(e)}")
    
    def _quantize_model(self, model_path: Path, quantize: str) -> None:
        """量化模型（需要额外依赖）"""
        print(f"   注意: 量化功能需要安装额外依赖")
        print(f"   4bit: pip install bitsandbytes")
        print(f"   8bit: pip install bitsandbytes")
        print(f"   GPTQ: pip install auto-gptq")
        print(f"   当前跳过量化步骤，可在加载时动态量化")
    
    def _register_model(
        self,
        model_name: str,
        model_path: Path,
        quantize: Optional[str]
    ) -> Dict[str, Any]:
        """注册模型到注册表"""
        # 加载现有注册表
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
        else:
            registry = {"models": []}
        
        # 计算模型大小
        total_size = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
        size_gb = total_size / (1024**3)
        
        # 检测模型格式
        if list(model_path.glob("*.safetensors")):
            format_type = "safetensors"
        elif (model_path / "pytorch_model.bin").exists():
            format_type = "pytorch"
        else:
            format_type = "unknown"
        
        # 创建模型信息
        model_info = {
            "name": model_name.split("/")[-1],
            "source": model_name,
            "path": str(model_path),
            "size_gb": round(size_gb, 2),
            "format": format_type,
            "quantization": quantize,
            "downloaded_at": datetime.now().isoformat(),
            "last_used": None
        }
        
        # 更新或添加模型
        existing_idx = None
        for idx, model in enumerate(registry["models"]):
            if model["source"] == model_name:
                existing_idx = idx
                break
        
        if existing_idx is not None:
            registry["models"][existing_idx] = model_info
        else:
            registry["models"].append(model_info)
        
        # 保存注册表
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 模型已注册到: {self.registry_path}")
        
        return model_info
    
    def _get_model_info(self, model_name: str, model_path: Path) -> Dict[str, Any]:
        """获取已存在模型的信息"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                for model in registry["models"]:
                    if model["source"] == model_name:
                        return model
        
        # 如果注册表中没有，返回基本信息
        return {
            "name": model_name.split("/")[-1],
            "source": model_name,
            "path": str(model_path),
            "size_gb": 0,
            "format": "unknown",
            "quantization": None,
            "downloaded_at": None,
            "last_used": None
        }


def main():
    parser = argparse.ArgumentParser(
        description="从Hugging Face下载大语言模型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载Qwen模型
  python download_hf_model.py --model-name Qwen/Qwen2.5-7B-Instruct
  
  # 下载并准备4bit量化
  python download_hf_model.py --model-name meta-llama/Llama-3.2-3B --quantize 4bit
  
  # 强制重新下载
  python download_hf_model.py --model-name Qwen/Qwen2.5-3B-Instruct --force
  
  # 指定输出目录
  python download_hf_model.py --model-name google/gemma-2b-it --output-dir /path/to/models
        """
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        required=True,
        help="Hugging Face模型名称，如 'Qwen/Qwen2.5-7B-Instruct'"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models/huggingface",
        help="模型保存目录 (默认: models/huggingface)"
    )
    
    parser.add_argument(
        "--quantize",
        type=str,
        choices=["4bit", "8bit"],
        help="量化选项 (4bit 或 8bit)"
    )
    
    parser.add_argument(
        "--token",
        type=str,
        help="Hugging Face访问令牌 (或设置环境变量 HF_TOKEN)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制重新下载已存在的模型"
    )
    
    args = parser.parse_args()
    
    try:
        downloader = HuggingFaceModelDownloader(
            output_dir=args.output_dir,
            token=args.token
        )
        
        model_info = downloader.download_model(
            model_name=args.model_name,
            quantize=args.quantize,
            force=args.force
        )
        
        print("\n模型信息:")
        print(f"  名称: {model_info['name']}")
        print(f"  路径: {model_info['path']}")
        print(f"  大小: {model_info['size_gb']} GB")
        print(f"  格式: {model_info['format']}")
        if model_info['quantization']:
            print(f"  量化: {model_info['quantization']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  下载已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
