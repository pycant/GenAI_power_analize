import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def vram_gb():
    if torch.cuda.is_available():
        m = torch.cuda.get_device_properties(0).total_memory
        return round(m/1024/1024/1024, 2)
    return 0.0

def select_model(vram):
    if torch.cuda.is_available() and vram >= 7.5:
        return "Qwen/Qwen2.5-3B-Instruct"
    if torch.cuda.is_available() and vram >= 3.0:
        return "Qwen/Qwen2.5-1.5B-Instruct"
    return "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

def build_prompt(tokenizer, system, user):
    msgs = [{"role":"system","content":system},{"role":"user","content":user}]
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template is not None:
        return tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True)
    return system + "\n" + user

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prompt", default="你是一个科研助手，用中文回答。请简述Transformer的注意力机制。")
    p.add_argument("--max_new_tokens", type=int, default=256)
    p.add_argument("--dry", action="store_true")
    p.add_argument("--model", default=None)
    args = p.parse_args()
    cuda = torch.cuda.is_available()
    vram = vram_gb()
    model_id = args.model if args.model else select_model(vram)
    dtype = torch.float16 if cuda else torch.float32
    print("cuda", cuda)
    print("vram_gb", vram)
    print("model", model_id)
    print("dtype", "fp16" if dtype==torch.float16 else "fp32")
    if args.dry:
        return
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto" if cuda else None, torch_dtype=dtype, trust_remote_code=True)
    text = build_prompt(tok, "你是一个科研助手。", args.prompt)
    ids = tok(text, return_tensors="pt").to(model.device)
    out = model.generate(**ids, max_new_tokens=args.max_new_tokens, do_sample=True, temperature=0.7, top_p=0.9)
    s = tok.decode(out[0], skip_special_tokens=True)
    print(s)

if __name__ == "__main__":
    main()
