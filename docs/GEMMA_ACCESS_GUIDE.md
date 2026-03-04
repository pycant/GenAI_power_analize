# Gemma 模型访问指南

## 问题描述

Gemma 是 Google 发布的受限模型（gated model），需要申请访问权限并登录才能下载。

## 错误信息

```
401 Client Error
Access to model google/gemma-2b-it is restricted
You must have access to it and be authenticated to access it
```

## 解决步骤

### 1. 申请访问权限

1. **访问模型页面**:
   - Gemma 2B: https://huggingface.co/google/gemma-2b-it
   - Gemma 7B: https://huggingface.co/google/gemma-7b-it

2. **点击 "Agree and access repository"**

3. **阅读并同意条款**:
   - Google's Gemma Terms of Use
   - Acceptable Use Policy

4. **等待批准**:
   - 通常是即时批准
   - 刷新页面确认访问权限

### 2. 获取 HuggingFace Token

1. **登录 HuggingFace**: https://huggingface.co/

2. **访问 Token 设置**: https://huggingface.co/settings/tokens

3. **创建新 Token**:
   - 点击 "New token"
   - 名称: `gemma-access` 或任意名称
   - 类型: 选择 "Read"
   - 点击 "Generate a token"

4. **复制 Token**:
   - ⚠️ 只显示一次，请妥善保存
   - 格式: `hf_xxxxxxxxxxxxxxxxxxxxx`

### 3. 登录 HuggingFace

#### 方法 1: 使用 CLI（推荐）

```bash
# 激活环境
conda activate bartscore

# 登录
huggingface-cli login

# 粘贴 token 并按回车
# 选择是否将 token 保存为 git credential (y/n)
```

#### 方法 2: 使用 Python

```python
from huggingface_hub import login

# 交互式登录
login()

# 或直接提供 token
login(token="hf_xxxxxxxxxxxxxxxxxxxxx")
```

#### 方法 3: 设置环境变量

```bash
# Windows CMD
set HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Windows PowerShell
$env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"

# 或添加到 .env 文件
echo HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx >> .env
```

### 4. 验证登录

```bash
# 检查登录状态
huggingface-cli whoami

# 应该显示你的用户名
```

### 5. 重新下载模型

```bash
# 使用下载脚本
python scripts/download_hf_model.py

# 或使用批量下载
python scripts/batch_download_models.py
```

## 常见问题

### Q1: Token 保存在哪里？

**A**: Token 保存在：
- Windows: `C:\Users\<username>\.cache\huggingface\token`
- Linux/Mac: `~/.cache/huggingface/token`

### Q2: 如何更新 Token？

**A**: 重新运行 `huggingface-cli login` 并输入新 token

### Q3: Token 权限不足怎么办？

**A**: 
1. 确保 token 类型是 "Read" 或 "Write"
2. 重新生成 token
3. 确认已申请模型访问权限

### Q4: 仍然无法访问？

**A**: 
1. 检查是否已批准访问请求
2. 退出登录重新登录: `huggingface-cli logout` 然后 `huggingface-cli login`
3. 清除缓存: 删除 `~/.cache/huggingface/` 目录
4. 使用浏览器访问模型页面确认可以看到文件列表

## 替代方案

### 使用 Ollama 的 Gemma

如果不想处理 HuggingFace 认证，可以使用 Ollama：

```bash
# 下载 Gemma
ollama pull gemma:2b
ollama pull gemma:7b

# 或使用已有的 gemma3
ollama list  # 查看已安装模型
```

**在实验中使用**:

```json
{
  "model": "ollama:gemma3:4b",
  "task_type": "qa",
  "prompts": "Your prompt here"
}
```

### 使用其他非受限模型

**推荐模型**（无需申请权限）:

1. **Qwen 2.5 系列**:
   - `Qwen/Qwen2.5-3B-Instruct` ✅ 已下载
   - `Qwen/Qwen2.5-7B-Instruct` ✅ 已下载

2. **Phi-3 系列**:
   - `microsoft/Phi-3-mini-4k-instruct` ✅ 已下载

3. **其他开放模型**:
   - `meta-llama/Llama-2-7b-chat-hf` (需要申请)
   - `mistralai/Mistral-7B-Instruct-v0.2`

## 安全提示

⚠️ **保护你的 Token**:
- 不要分享 token
- 不要提交到 Git
- 添加到 `.gitignore`:
  ```
  .env
  *.token
  ```

## 相关文档

- [HuggingFace Token 文档](https://huggingface.co/docs/hub/security-tokens)
- [Gemma 模型卡片](https://huggingface.co/google/gemma-2b-it)
- [模型下载指南](./experiment/hf_models_guide.md)

---

**最后更新**: 2026-03-03  
**维护者**: GenAI Power Analysis Team
