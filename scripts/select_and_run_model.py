import argparse
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
import json
import requests
from datetime import datetime

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

def select_ollama_model(vram):
    if vram >= 7.5:
        return "qwen2.5:3b"
    if vram >= 3.0:
        return "qwen2.5:1.5b"
    return "llama3.2:1b"

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
    p.add_argument("--backend", choices=["hf","ollama"], default="hf")
    p.add_argument("--server", default=os.environ.get("OLLAMA_HOST","http://localhost:11434"))
    p.add_argument("--show_meta", action="store_true")
    p.add_argument("--save_jsonl", default=None)
    p.add_argument("--use_context", action="store_true")
    p.add_argument("--context_file", default=".ollama_context.json")
    args = p.parse_args()
    cuda = torch.cuda.is_available()
    vram = vram_gb()
    print("cuda", cuda)
    print("vram_gb", vram)
    if args.backend == "ollama":
        om = args.model if args.model else select_ollama_model(vram)
        print("backend", "ollama")
        print("model", om)
        if args.dry:
            return
        url = args.server.rstrip("/") + "/api/generate"
        ctx = None
        if args.use_context and os.path.exists(args.context_file):
            try:
                ctx = json.load(open(args.context_file, "r", encoding="utf-8"))
            except Exception:
                ctx = None
        payload = {"model": om, "prompt": args.prompt, "stream": False}
        if ctx:
            payload["context"] = ctx
        payload["options"] = {"num_predict": args.max_new_tokens, "temperature": 0.7, "top_p": 0.9}
        r = requests.post(url, json=payload, timeout=600)
        resp = r.json()
        if args.show_meta:
            print(json.dumps({
                "model": resp.get("model"),
                "created_at": resp.get("created_at"),
                "done_reason": resp.get("done_reason"),
                "total_duration": resp.get("total_duration"),
                "load_duration": resp.get("load_duration"),
                "prompt_eval_count": resp.get("prompt_eval_count"),
                "prompt_eval_duration": resp.get("prompt_eval_duration"),
                "eval_count": resp.get("eval_count"),
                "eval_duration": resp.get("eval_duration"),
                "context_len": len(resp.get("context", []))
            }, ensure_ascii=False))
        print(resp.get("response",""))
        if resp.get("context") is not None:
            try:
                json.dump(resp.get("context"), open(args.context_file, "w", encoding="utf-8"))
            except Exception:
                pass
        if args.save_jsonl:
            rec = {
                "ts": datetime.now().isoformat(),
                "backend": "ollama",
                "model": om,
                "prompt": args.prompt,
                "response": resp.get("response",""),
                "meta": {k: resp.get(k) for k in ["model","created_at","done_reason","total_duration","load_duration","prompt_eval_count","prompt_eval_duration","eval_count","eval_duration"]}
            }
            try:
                with open(args.save_jsonl, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            except Exception:
                pass
        return
    model_id = args.model if args.model else select_model(vram)
    dtype = torch.float16 if cuda else torch.float32
    print("backend", "hf")
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
