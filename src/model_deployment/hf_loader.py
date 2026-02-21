"""
Hugging Face模型加载器

提供统一的模型加载接口，支持：
- 本地模型加载
- 动态量化
- 批量推理
- 资源监控
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    GenerationConfig
)


class HuggingFaceModelLoader:
    """Hugging Face模型加载器"""
    
    def __init__(self, models_dir: str = "models/huggingface"):
        self.models_dir = Path(models_dir)
        self.registry_path = Path("models/model_registry.json")
        self.loaded_models = {}  # 缓存已加载的模型
    
    def load_model(
        self,
        model_path: Union[str, Path],
        quantize: Optional[str] = None,
        device: str = "auto",
        trust_remote_code: bool = True,
        **kwargs
    ) -> tuple:
        """
        加载模型和分词器
        
        Args:
            model_path: 模型路径或名称
            quantize: 量化选项 ("4bit", "8bit", None)
            device: 设备 ("auto", "cuda", "cpu")
            trust_remote_code: 是否信任远程代码
            **kwargs: 其他模型加载参数
            
        Returns:
            (model, tokenizer) 元组
        """
        model_path = Path(model_path)
        
        # 检查缓存
        cache_key = f"{model_path}_{quantize}_{device}"
        if cache_key in self.loaded_models:
            print(f"✓ 从缓存加载模型: {model_path.name}")
            return self.loaded_models[cache_key]
        
        print(f"\n{'='*60}")
        print(f"加载模型: {model_path.name}")
        print(f"{'='*60}\n")
        
        # 加载分词器
        print("📝 加载分词器...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            trust_remote_code=trust_remote_code
        )
        
        # 设置pad_token
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        print(f"   ✓ 分词器加载完成 (词表大小: {len(tokenizer)})")
        
        # 配置量化
        quantization_config = None
        if quantize == "4bit":
            print("⚙️  配置4bit量化...")
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4"
            )
        elif quantize == "8bit":
            print("⚙️  配置8bit量化...")
            quantization_config = BitsAndBytesConfig(
                load_in_8bit=True
            )
        
        # 加载模型
        print("🤖 加载模型...")
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            quantization_config=quantization_config,
            device_map=device,
            trust_remote_code=trust_remote_code,
            torch_dtype=torch.float16 if quantize is None else None,
            **kwargs
        )
        
        print(f"   ✓ 模型加载完成")
        
        # 显示模型信息
        self._print_model_info(model, quantize)
        
        # 更新最后使用时间
        self._update_last_used(model_path)
        
        # 缓存模型
        self.loaded_models[cache_key] = (model, tokenizer)
        
        print(f"\n{'='*60}")
        print(f"✨ 模型准备就绪")
        print(f"{'='*60}\n")
        
        return model, tokenizer
    
    def generate(
        self,
        model,
        tokenizer,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True,
        **kwargs
    ) -> str:
        """
        生成文本
        
        Args:
            model: 模型实例
            tokenizer: 分词器实例
            prompt: 输入提示
            max_new_tokens: 最大生成token数
            temperature: 温度参数
            top_p: Top-p采样参数
            do_sample: 是否采样
            **kwargs: 其他生成参数
            
        Returns:
            生成的文本
        """
        # 编码输入
        inputs = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        # 生成
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                **kwargs
            )
        
        # 解码输出
        generated_text = tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )
        
        return generated_text
    
    def batch_generate(
        self,
        model,
        tokenizer,
        prompts: List[str],
        batch_size: int = 4,
        **kwargs
    ) -> List[str]:
        """
        批量生成文本
        
        Args:
            model: 模型实例
            tokenizer: 分词器实例
            prompts: 输入提示列表
            batch_size: 批次大小
            **kwargs: 其他生成参数
            
        Returns:
            生成的文本列表
        """
        results = []
        
        for i in range(0, len(prompts), batch_size):
            batch_prompts = prompts[i:i + batch_size]
            
            # 编码批次
            inputs = tokenizer(
                batch_prompts,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
            inputs = {k: v.to(model.device) for k, v in inputs.items()}
            
            # 生成
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                    **kwargs
                )
            
            # 解码批次输出
            for j, output in enumerate(outputs):
                input_length = inputs['input_ids'][j].shape[0]
                generated_text = tokenizer.decode(
                    output[input_length:],
                    skip_special_tokens=True
                )
                results.append(generated_text)
        
        return results
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """列出所有可用的本地模型"""
        if not self.registry_path.exists():
            return []
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        return registry.get("models", [])
    
    def get_model_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取模型信息"""
        models = self.list_available_models()
        
        for model in models:
            if model['name'] == name or model['source'] == name:
                return model
        
        return None
    
    def _print_model_info(self, model, quantize: Optional[str]) -> None:
        """打印模型信息"""
        # 计算参数量
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        print(f"\n模型信息:")
        print(f"   总参数: {total_params:,}")
        print(f"   可训练参数: {trainable_params:,}")
        
        if quantize:
            print(f"   量化: {quantize}")
        
        # 显示设备信息
        if hasattr(model, 'hf_device_map'):
            print(f"   设备映射: {model.hf_device_map}")
        
        # 估算显存占用
        if torch.cuda.is_available():
            memory_allocated = torch.cuda.memory_allocated() / 1024**3
            memory_reserved = torch.cuda.memory_reserved() / 1024**3
            print(f"   显存占用: {memory_allocated:.2f} GB (已分配)")
            print(f"   显存预留: {memory_reserved:.2f} GB (已预留)")
    
    def _update_last_used(self, model_path: Path) -> None:
        """更新模型最后使用时间"""
        if not self.registry_path.exists():
            return
        
        from datetime import datetime
        
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
        
        model_path_str = str(model_path)
        for model in registry.get("models", []):
            if model['path'] == model_path_str or model_path_str.endswith(model['name']):
                model['last_used'] = datetime.now().isoformat()
                break
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    
    def unload_model(self, model_path: Union[str, Path]) -> None:
        """卸载模型释放内存"""
        model_path = Path(model_path)
        
        # 从缓存中移除
        keys_to_remove = [k for k in self.loaded_models.keys() if str(model_path) in k]
        
        for key in keys_to_remove:
            model, tokenizer = self.loaded_models[key]
            del model
            del tokenizer
            del self.loaded_models[key]
        
        # 清理GPU缓存
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print(f"✓ 已卸载模型: {model_path.name}")


# 使用示例
if __name__ == "__main__":
    # 初始化加载器
    loader = HuggingFaceModelLoader()
    
    # 列出可用模型
    print("可用模型:")
    for model in loader.list_available_models():
        print(f"  - {model['name']} ({model['size_gb']} GB)")
    
    # 加载模型示例
    # model, tokenizer = loader.load_model(
    #     "models/huggingface/Qwen--Qwen2.5-7B-Instruct",
    #     quantize="4bit"
    # )
    
    # 生成文本示例
    # prompt = "请介绍一下人工智能的发展历史。"
    # response = loader.generate(model, tokenizer, prompt, max_new_tokens=256)
    # print(f"\n生成结果:\n{response}")
