## 大语言模型能效评估实验方法（第三版：增强生态效度版）

### 1. 实验目的
本实验旨在**模拟真实生产环境**，系统评估大语言模型在不同**模型属性**（参数量、量化精度、训练方法）和**推理优化框架**下的能效表现与生成质量。通过引入**系统级功耗测量**、**分阶段能耗分析**和**多维度质量评估**，探究模型在不同任务类型上的“能效-性能”权衡规律，为模型选型、硬件配置和成本优化提供实证依据。

### 2. 实验设计：多因素全因子实验

#### 2.1 自变量设计：三个维度 + 两个层次

我们将实验扩展为**4个维度**的组合：

| 维度 | 水平 | 说明 |
|------|------|------|
| **模型参数量** | 小（1B-3B）、中（3B-6B）、大（6B以上） | 覆盖主流开源模型 |
| **量化精度** | FP16、INT8、INT4 | bitsandbytes实现 |
| **训练方法** | 基础版、指令版 | 如基础vsChat |
| **推理框架** | HF原生、vLLM、TensorRT-LLM | **新增维度**，对比优化效果 |
| **K-V缓存** | 开启、关闭 | **新增控制变量**，分析缓存影响 |

**模型选择**（基于 RTX 4060 Laptop 8GB VRAM，2026年最新模型）：

| 模型　　　　　 | 参数量 | 训练方法 | 可用精度　　　 | 推理框架支持 | Ollama可用　　　 | 特点　　　　　　　　 |
| ----------------| --------| ----------| ----------------| --------------| ------------------| ----------------------|
| Qwen3-8B　　　 | 8B　　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| ✓ qwen3:8b　　　 | 119语言，推理模式　　|
| DeepSeek-R1-8B | 8B　　 | 推理增强 | FP16,INT8,INT4 | HF,Ollama　　| ✓ deepseek-r1:8b | 链式推理，数学强　　 |
| Llama-3.1-8B　 | 8B　　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| llama3.1:8b　　　| 生态完善，128K上下文 |
| Gemma3-4B　　　| 4B　　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| ✓ gemma3:4b　　　| 多模态，视觉+文本　　|
| Qwen3-4B　　　 | 4B　　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| ✓ qwen3:4b　　　 | 紧凑多语言　　　　　 |
| Phi-3.5-mini　 | 3.8B　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| phi3.5:3.8b　　　| 推理数学强，MIT许可　|
| SmolLM3-3B　　 | 3B　　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| smollm3:3b　　　 | 透明训练，推理优秀　 |
| Mistral-7B　　 | 7B　　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| mistral:7b　　　 | 经典模型，社区广泛　 |
| GLM-4-9B　　　 | 9B　　 | 指令　　 | FP16,INT8,INT4 | HF,Ollama　　| glm4:9b　　　　　| 代码生成，函数调用　 |

**说明**：
- ✓ 标记表示已在本地 Ollama 中可用
- 所有模型均支持 Q4_K_M 量化（约占原始大小的 25-30%）
- 8GB VRAM 可运行 8B 模型的 Q4 量化版本，4B 模型可运行 FP16
- **推荐测试组合**：
  - 高性能组：Qwen3-8B, DeepSeek-R1-8B, Llama-3.1-8B
  - 平衡组：Gemma3-4B, Qwen3-4B, GLM-4-9B
  - 高效组：Phi-3.5-mini, SmolLM3-3B
- **任务适配**：
  - 数学/推理：DeepSeek-R1-8B, Phi-3.5-mini
  - 多语言：Qwen3-8B/4B（119种语言）
  - 代码生成：GLM-4-9B, DeepSeek-R1-8B
  - 多模态：Gemma3-4B（视觉+文本）

**实验组合数**（基于 RTX 4060 Laptop 8GB VRAM 的可行组合）：

根据 VRAM 计算公式：`VRAM (GB) ≈ 参数量 (B) × 量化系数 × 1.2`（1.2 为 KV cache 和推理开销）

| 量化方式 | 系数 | 说明 |
|---------|------|------|
| Q4_K_M (INT4) | 0.5 | 最常用，质量损失小 |
| Q8_0 (INT8) | 1.0 | 平衡质量和大小 |
| FP16 | 2.0 | 完整精度 |

### 可行的模型-量化组合（8GB VRAM 限制）

| 模型 | 参数量 | Q4 (INT4) | Q8 (INT8) | FP16 | 推荐配置 |
|------|--------|-----------|-----------|------|----------|
| **3-4B 模型** |
| Phi-3.5-mini | 3.8B | ✓ 2.3GB | ✓ 4.6GB | ✓ 9.1GB* | Q4/Q8/FP16 |
| SmolLM3-3B | 3B | ✓ 1.8GB | ✓ 3.6GB | ✓ 7.2GB | Q4/Q8/FP16 |
| Qwen3-4B | 4B | ✓ 2.4GB | ✓ 4.8GB | ✗ 9.6GB | Q4/Q8 |
| Gemma3-4B | 4B | ✓ 2.4GB | ✓ 4.8GB | ✗ 9.6GB | Q4/Q8 |
| **7-8B 模型** |
| Mistral-7B | 7B | ✓ 4.2GB | ✗ 8.4GB | ✗ 16.8GB | Q4 only |
| Qwen3-8B | 8B | ✓ 4.8GB | ✗ 9.6GB | ✗ 19.2GB | Q4 only |
| DeepSeek-R1-8B | 8B | ✓ 4.8GB | ✗ 9.6GB | ✗ 19.2GB | Q4 only |
| Llama-3.1-8B | 8B | ✓ 4.8GB | ✗ 9.6GB | ✗ 19.2GB | Q4 only |
| **9B 模型** |
| GLM-4-9B | 9B | ✓ 5.4GB | ✗ 10.8GB | ✗ 21.6GB | Q4 only |

*注：FP16 需要接近 8GB，可能需要系统内存辅助（CPU offload）

### 存储空间需求计算

**Ollama 模型存储说明**：
- Ollama 将模型存储在 `~/.ollama/models/` (Linux/Mac) 或 `C:\Users\<用户>\.ollama\models\` (Windows)
- 每个模型的每个量化版本单独存储
- 实际磁盘占用 ≈ 模型文件大小 + 10% 元数据开销

#### 方案一：仅下载 Q4 量化版本（推荐）

| 模型类别 | 模型数量 | 单个大小 | 小计 |
|---------|---------|---------|------|
| 3-4B 模型 (Q4) | 4 | 1.8-2.4 GB | ~8.7 GB |
| 7-8B 模型 (Q4) | 4 | 4.2-4.8 GB | ~18.6 GB |
| 9B 模型 (Q4) | 1 | 5.4 GB | ~5.4 GB |
| **总计** | **9 个模型** | - | **~32.7 GB** |
| **含 10% 开销** | - | - | **~36 GB** |

#### 方案二：下载 Q4 + Q8（用于量化对比实验）

| 模型类别 | 模型数量 | Q4 大小 | Q8 大小 | 小计 |
|---------|---------|---------|---------|------|
| 3-4B 模型 (Q4+Q8) | 4 | ~8.7 GB | ~17.4 GB | ~26.1 GB |
| 7-8B 模型 (Q4) | 4 | ~18.6 GB | - | ~18.6 GB |
| 9B 模型 (Q4) | 1 | ~5.4 GB | - | ~5.4 GB |
| **总计** | **13 个模型文件** | - | - | **~50.1 GB** |
| **含 10% 开销** | - | - | - | **~55 GB** |

#### 方案三：完整下载（包含 FP16，需 CPU offload）

| 模型类别 | 模型数量 | Q4 | Q8 | FP16 | 小计 |
|---------|---------|----|----|------|------|
| 3-4B 模型 (全量化) | 4 | ~8.7 GB | ~17.4 GB | ~33 GB | ~59.1 GB |
| 7-8B 模型 (Q4) | 4 | ~18.6 GB | - | - | ~18.6 GB |
| 9B 模型 (Q4) | 1 | ~5.4 GB | - | - | ~5.4 GB |
| **总计** | **17 个模型文件** | - | - | - | **~83.1 GB** |
| **含 10% 开销** | - | - | - | - | **~91 GB** |

### 已下载模型（根据 AGENTS.md）

你已经下载了以下模型（Q4 量化）：
- ✓ deepseek-r1:8b (~5.2 GB)
- ✓ gemma3:4b (~3.3 GB)
- ✓ qwen3:8b (~5.2 GB)
- ✓ qwen3:4b (~2.5 GB)

**已占用空间**：~16.2 GB

### 还需下载的模型

#### 方案一（仅 Q4）还需下载：
- Phi-3.5-mini:3.8b (Q4) - ~2.3 GB
- SmolLM3:3b (Q4) - ~1.8 GB
- Mistral:7b (Q4) - ~4.2 GB
- Llama-3.1:8b (Q4) - ~4.8 GB
- GLM-4:9b (Q4) - ~5.4 GB

**还需空间**：~18.5 GB → 含开销 ~20 GB

#### 方案二（Q4+Q8）还需下载：
- 上述 5 个模型的 Q4 版本：~18.5 GB
- 已有 4 个模型的 Q8 版本：~17.4 GB

**还需空间**：~35.9 GB → 含开销 ~39 GB

### 推荐下载策略

**阶段一：核心模型（优先）**
```bash
# 下载 5 个缺失的 Q4 模型
ollama pull phi3.5:3.8b
ollama pull smollm3:3b  
ollama pull mistral:7b
ollama pull llama3.1:8b
ollama pull glm4:9b
```
**需要空间**：~20 GB

**阶段二：量化对比（可选）**
```bash
# 为已有的 4 个模型下载 Q8 版本
ollama pull qwen3:8b-q8_0
ollama pull qwen3:4b-q8_0
ollama pull gemma3:4b-q8_0
ollama pull deepseek-r1:8b-q8_0
```
**额外需要**：~20 GB

**总存储需求建议**：
- 最小配置（仅 Q4）：40 GB 可用空间
- 推荐配置（Q4 + 部分 Q8）：60 GB 可用空间
- 完整配置（含 FP16）：100 GB 可用空间

### 实验组合统计

**总计可行组合**：
- 3-4B 模型：4 个模型 × 3 种量化 = 12 组合（部分需 CPU offload）
- 7-8B 模型：4 个模型 × 1 种量化 (Q4) = 4 组合
- 9B 模型：1 个模型 × 1 种量化 (Q4) = 1 组合

**推荐实验组合**（无需 CPU offload，纯 GPU 推理）：
- **高优先级**（17 组合）：
  - 3-4B 模型 Q4/Q8：8 组合
  - 7-8B 模型 Q4：4 组合
  - 9B 模型 Q4：1 组合
  
- **扩展测试**（4 组合，需 CPU offload）：
  - 3-4B 模型 FP16：4 组合

**推理框架支持**：
- Ollama：所有组合（推荐，开箱即用）
- HuggingFace Transformers：所有组合（需手动配置量化）
- vLLM：仅支持 FP16/FP8（不推荐用于 8GB VRAM）

**实际测试建议**：
1. **第一阶段**（核心对比）：选择 3 个代表性模型 × Q4 量化 = 3 组合
   - Qwen3-8B (Q4)：多语言基准
   - DeepSeek-R1-8B (Q4)：推理基准
   - Phi-3.5-mini (Q4)：小模型基准

2. **第二阶段**（量化影响）：选择 1 个模型 × 3 种量化 = 3 组合
   - Qwen3-4B (Q4/Q8/FP16)：评估量化对质量的影响

3. **第三阶段**（全面评估）：所有 17 个推荐组合

**注意事项**：
- 长上下文（>4K tokens）会显著增加 VRAM 使用
- 批处理大小固定为 1（单次推理）
- 建议每次实验后清理 GPU 缓存

## 2.2 任务类型自适应生成参数

根据任务类型**动态调整生成策略**和**题目设计**，以模拟真实应用场景并全面评估模型能力：

| 任务类型 | 生成策略 | 温度 | 题目数量 | 上下文要求 | 评估重点 |
|---------|----------|------|---------|-----------|----------|
| **知识问答** | Greedy | 0.0 | 15-20题 | 单轮独立 | 准确率、事实性 |
| **数学计算** | Greedy | 0.0 | 10-15题 | 单轮独立 | 准确率、推理步骤 |
| **代码生成** | 低温度 | 0.1 | 10-12题 | 单轮独立 | 编译率、测试通过率 |
| **逻辑推理** | 低温度 | 0.1 | 8-10题 | 单轮独立 | 推理链完整性 |
| **文本摘要** | 采样 | 0.7 | 5-8题 | 提供长文本 | ROUGE、BERTScore |
| **创意写作** | 采样 | 0.8 | 5-8题 | 提供主题/开头 | 多样性、连贯性 |
| **多轮对话** | 采样 | 0.7 | 5-8组（2-3轮） | 保持上下文 | 上下文理解、连贯性 |
| **上下文检验** | 低温度 | 0.2 | 8-10题 | 多轮依赖 | 信息提取、记忆能力 |

**任务设计原则**：

1. **多题目覆盖**：每个任务类型设计多道题目，覆盖不同难度和场景
   - 简单题（30%）：基础能力验证
   - 中等题（50%）：常见应用场景
   - 困难题（20%）：边界情况测试

2. **上下文检验任务**（新增）：
   - **信息提取型**：先提供长文本，后续提问细节
   - **信息整合型**：分多轮提供信息，最后要求综合回答
   - **指令遵循型**：第一轮给出规则，后续轮次检验是否遵守
   - **记忆测试型**：测试模型对前文信息的记忆能力

3. **重复生成策略**：
   - 确定性任务（温度=0）：每题运行 1 次
   - 低温度任务（温度≤0.2）：每题运行 3 次，取多数投票
   - 采样任务（温度≥0.7）：每题运行 5-10 次，评估多样性和稳定性

4. **实验效率优化**：
   - 总题目数：约 80-100 题（覆盖所有任务类型）
   - 单个模型完整测试时间：预计 2-4 小时
   - 9 个模型完整测试：预计 18-36 小时

**示例：上下文检验任务设计**

```json
{
  "task_type": "context_verification",
  "prompts": [
    "我现在要告诉你三个人的信息。张三：35岁，工程师，喜欢篮球。李四：28岁，教师，喜欢阅读。王五：42岁，医生，喜欢旅游。",
    "请问李四的职业是什么？",
    "谁的年龄最大？",
    "喜欢篮球的人是做什么工作的？"
  ],
  "keep_context": true,
  "temperature": 0.2,
  "expected_answers": ["教师", "王五", "工程师"]
}
```

## 3. 硬件与软件环境

### 3.1 硬件配置（实际测试环境）

- **GPU**：NVIDIA GeForce RTX 4060 Laptop GPU
  - VRAM：8GB GDDR6
  - 架构：Ada Lovelace
  - CUDA 核心：3072
  - 支持：CUDA 12.6, Tensor Cores
  
- **CPU**：Intel Core i7-13700H
  - 核心：14 核 20 线程（6P+8E）
  - 基础频率：2.4 GHz
  - 最大睿频：5.0 GHz（测试时建议固定频率）
  
- **内存**：16GB DDR5
  - 用于 CPU offload 和系统开销
  
- **存储**：NVMe SSD
  - 建议预留 100GB 用于模型存储
  
- **显示**：Intel Iris Xe Graphics 2GB（集成显卡，不用于推理）

- **功率测量**：
  - GPU：通过 `pynvml` 读取板载传感器（精度 ±5W）
  - CPU：通过 `psutil` 估算或 Windows Performance Counter
  - 系统：可选使用外部功率计

**环境控制建议**：
- 关闭后台应用，减少干扰
- 固定 CPU 频率（通过电源计划）
- 保持环境温度稳定（20-25°C）
- 每次实验前清理 GPU 缓存

### 3.2 推理框架配置

| 框架 | 版本 | 关键配置 | 适用场景 |
|------|------|----------|----------|
| **Ollama** | 0.13.2+ | 自动量化管理，batch=1 | 推荐，开箱即用 |
| **HuggingFace Transformers** | 4.35.2+ | 手动量化配置，支持 bitsandbytes | 灵活性高，需配置 |
| **Python** | 3.10 | Conda 环境：bartscore | 统一环境 |

**Ollama 配置**：
- 模型存储：`C:\Users\<用户>\.ollama\models\`
- API 端点：`http://localhost:11434/`
- 量化支持：Q4_K_M, Q8_0（自动）
- 上下文窗口：根据模型自动调整（通常 4K-128K）

**HuggingFace 配置**（可选）：
- 量化库：`bitsandbytes` (INT4/INT8), `auto-gptq` (GPTQ)
- 设备映射：`device_map="auto"` 支持 CPU offload
- 精度：FP16（默认），INT8，INT4
- 批处理：固定 batch_size=1

**监控工具**：
- GPU 监控：`pynvml` (NVIDIA Management Library)
- 系统监控：`psutil` (CPU, Memory)
- 自定义监控脚本：`experiments/monitor.py`


## 4. 系统级功耗测量方法（核心改进）

### 4.1 测量边界定义

我们将功耗测量从"GPU功耗"扩展为**"系统增量功耗"**，即模型推理引起的额外功耗：

\[
P_{incremental} = P_{total} - P_{idle}
\]

其中 \(P_{idle}\) 为系统空闲（无模型加载）时，运行监控脚本但不进行任何推理的稳定功耗。

**Windows 环境特殊说明**：
- 笔记本电脑功耗受电源管理策略影响较大，建议固定为"高性能"模式
- 测量前关闭不必要的后台进程（浏览器、通讯软件等）
- 建议使用电源适配器供电，避免电池模式的动态调频干扰

### 4.2 多组件功耗同步采集

使用**统一的时间戳**同步采集以下数据源（采样率 5Hz，即每 0.2 秒采样一次）：

| 组件 | 测量方法 | 工具/API | 精度 | Windows 可用性 |
|------|----------|----------|------|---------------|
| **GPU** | 板载传感器 | `pynvml` (NVIDIA Management Library) | ±5W | ✅ 完全支持 |
| **CPU** | 利用率估算 | `psutil` + TDP 估算 | ±10W | ✅ 可用（近似） |
| **内存** | 使用量监控 | `psutil` | 仅监控使用量 | ✅ 可用 |
| **系统** | 外部功率计（可选） | USB 功率计 | ±0.5W | ⚠️ 需额外硬件 |

**Windows 环境限制与替代方案**：

1. **CPU 功耗测量**：
   - Windows 不支持 Linux 的 RAPL (Running Average Power Limit) 接口
   - 替代方案：通过 CPU 利用率 × TDP 估算功耗
   - 公式：`CPU_Power ≈ CPU_Utilization% × TDP_W`
   - i7-13700H 的 TDP：基础 45W，最大 115W（建议使用 65W 作为估算基准）

2. **GPU 功耗测量**：
   - RTX 4060 Laptop GPU 支持通过 `pynvml` 读取实时功耗
   - 精度：±5W（板载传感器限制）
   - 采样频率：最高 10Hz（建议 5Hz 避免性能影响）

3. **系统级功耗**（可选）：
   - 如需更精确测量，可使用 USB 功率计（如 ChargerLAB POWER-Z）
   - 测量笔记本电源适配器输入功耗，需手动同步时间戳

**自定义监控脚本**（基于实际实现 `experiments/monitor.py`）：

**使用示例**：

```python
# 初始化监控器
monitor = ResourceMonitor(interval=0.2)  # 5Hz 采样

# 启动监控
monitor.start()

# 执行推理任务
response = ollama_client.generate(model="qwen3:8b", prompt="...")

# 停止监控
monitor.stop()

# 获取摘要
summary = monitor.summary()
print(f"GPU 平均功耗: {summary['gpu_power_avg_w']:.2f} W")
print(f"GPU 总能耗: {summary['gpu_energy_j']:.2f} J")
print(f"CPU 估算能耗: {summary['cpu_energy_j_approx']:.2f} J")
```

### 4.3 分阶段能耗分析

通过在功耗日志中**记录事件时间戳**，实现对不同阶段的能耗拆解：

1. **Prefill 阶段**：从输入传入到第一个 token 生成的时间
   - 功耗特征：高计算负载，GPU 利用率峰值
   - 关键指标：TTFT (Time To First Token)

2. **Decode 阶段**：后续逐个 token 生成
   - 功耗特征：访存密集型，GPU 利用率中等
   - 关键指标：TPOT (Time Per Output Token)

3. **空闲冷却**：任务间间隔
   - 用于区分任务间能耗，验证 \(P_{idle}\) 稳定性

**事件标记方法**：

```python
import time
import json

class EventLogger:
    """事件时间戳记录器"""
    def __init__(self, log_file="event_log.json"):
        self.log_file = log_file
        self.events = []
        
    def log(self, event_name, metadata=None):
        """记录事件"""
        event = {
            "timestamp": time.time(),
            "event": event_name,
            "metadata": metadata or {}
        }
        self.events.append(event)
        
    def save(self):
        """保存到文件"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)

# 使用示例
logger = EventLogger()
monitor = ResourceMonitor()

# 开始推理
logger.log("inference_start", {"model": "qwen3:8b", "task": "qa"})
monitor.start()

# 记录首 token 生成
response_stream = ollama_client.generate(model="qwen3:8b", prompt="...", stream=True)
first_token = True
for chunk in response_stream:
    if first_token:
        logger.log("first_token_generated")
        first_token = False

# 结束推理
logger.log("inference_end")
monitor.stop()
logger.save()
```

**后处理分析**：

```python
import pandas as pd

def analyze_phases(monitor_data, event_log):
    """分析各阶段能耗"""
    df = pd.DataFrame({
        'timestamp': monitor_data['timestamps'],
        'gpu_power_w': monitor_data['gpu_power_w'],
        'cpu_power_w': monitor_data['cpu_power_w_approx']
    })
    
    # 查找事件时间戳
    t_start = next(e['timestamp'] for e in event_log if e['event'] == 'inference_start')
    t_first = next(e['timestamp'] for e in event_log if e['event'] == 'first_token_generated')
    t_end = next(e['timestamp'] for e in event_log if e['event'] == 'inference_end')
    
    # 分阶段统计
    prefill = df[(df['timestamp'] >= t_start) & (df['timestamp'] < t_first)]
    decode = df[(df['timestamp'] >= t_first) & (df['timestamp'] <= t_end)]
    
    return {
        'prefill_energy_j': prefill['gpu_power_w'].sum() * 0.2,  # 0.2s 采样间隔
        'decode_energy_j': decode['gpu_power_w'].sum() * 0.2,
        'prefill_avg_power_w': prefill['gpu_power_w'].mean(),
        'decode_avg_power_w': decode['gpu_power_w'].mean()
    }
```

### 4.4 测量精度与误差分析

| 误差来源 | 影响程度 | 缓解措施 |
|---------|---------|---------|
| **GPU 传感器精度** | ±5W | 多次测量取平均，延长测试时间 |
| **CPU 功耗估算** | ±10W | 固定 CPU 频率，关闭后台进程 |
| **采样频率限制** | 小于 5% | 5Hz 采样足够捕捉推理过程 |
| **后台进程干扰** | 可达 20% | 实验前关闭不必要进程 |
| **温度漂移** | 5-10% | 控制环境温度，任务间冷却 |
| **电源管理策略** | 10-15% | 固定为"高性能"模式 |

**推荐实验流程**：

1. **基线测量**（5 分钟）：
   - 系统空闲，仅运行监控脚本
   - 记录 \(P_{idle}\) 均值和标准差

2. **预热阶段**（1-2 次推理）：
   - 加载模型到 GPU
   - 稳定温度和频率

3. **正式测试**：
   - 每个任务重复 3-10 次
   - 任务间间隔 30 秒冷却

4. **后处理**：
   - 剔除异常值（±3σ）
   - 计算增量功耗：\(P_{inc} = P_{measured} - P_{idle}\)

**数据质量检查**：

```python
def validate_monitoring_data(monitor):
    """验证监控数据质量"""
    issues = []
    
    # 检查采样率
    if len(monitor.timestamps) < 2:
        issues.append("采样点不足")
    else:
        intervals = [monitor.timestamps[i+1] - monitor.timestamps[i] 
                     for i in range(len(monitor.timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals)
        if abs(avg_interval - monitor.interval) > 0.05:
            issues.append(f"采样间隔不稳定: {avg_interval:.3f}s")
    
    # 检查 GPU 功耗合理性
    if monitor.gpu_power_w:
        max_power = max(monitor.gpu_power_w)
        if max_power > 140:  # RTX 4060 Laptop 最大功耗约 140W
            issues.append(f"GPU 功耗异常: {max_power:.1f}W")
    
    # 检查数据完整性
    if not monitor.gpu_power_w or all(p == 0 for p in monitor.gpu_power_w):
        issues.append("GPU 功耗数据缺失，请检查 pynvml 安装")
    
    return issues

# 使用示例
issues = validate_monitoring_data(monitor)
if issues:
    print("⚠️ 数据质量问题:")
    for issue in issues:
        print(f"  - {issue}")
```


## 5. 测试任务集：客观+主观混合设计

### 5.1 任务组成与设计原则

基于实际硬件环境（RTX 4060 Laptop 8GB）和 Ollama 推理框架，设计涵盖多种应用场景的测试任务集：

| 任务大类 | 子类型 | 题目数量 | 评估方法 | 生成策略 | 温度 | 重复次数 |
|---------|--------|---------|----------|----------|------|---------|
| **客观任务** | 知识问答 | 15-20 | 准确率、F1 | Greedy | 0.0 | 1 |
| | 数学计算 | 10-15 | 准确率、步骤完整性 | Greedy | 0.0 | 1 |
| | 代码生成 | 10-12 | 编译率、测试通过率 | 低温度 | 0.1 | 3 |
| | 逻辑推理 | 8-10 | 准确率、推理链 | 低温度 | 0.1 | 3 |
| **主观任务** | 文本摘要 | 5-8 | ROUGE-L、BERTScore | 采样 | 0.7 | 5 |
| | 创意写作 | 5-8 | Distinct-2、流畅度 | 采样 | 0.8 | 5 |
| | 多轮对话 | 5-8 组 | 上下文一致性、BERTScore | 采样 | 0.7 | 3 |
| **上下文检验** | 信息提取 | 3-4 | 准确率 | 低温度 | 0.2 | 3 |
| | 信息整合 | 2-3 | 完整性、准确率 | 低温度 | 0.2 | 3 |
| | 指令遵循 | 2-3 | 遵循率 | 低温度 | 0.2 | 3 |

**总计**：约 80-100 道题目，单个模型完整测试时间约 2-4 小时

**设计原则**：

1. **难度分层**（每个任务类型内部）：
   - 简单题（30%）：基础能力验证，如简单事实问答、基础算术
   - 中等题（50%）：常见应用场景，如多步推理、中等长度代码
   - 困难题（20%）：边界情况测试，如复杂逻辑、长文本处理

2. **真实场景导向**：
   - 知识问答：涵盖科学、历史、常识等多领域
   - 代码生成：Python 为主，包含函数、类、算法实现
   - 文本摘要：新闻、论文摘要、会议纪要等
   - 创意写作：故事续写、诗歌创作、广告文案

3. **中文为主，兼顾英文**：
   - 80% 中文题目（符合目标用户群）
   - 20% 英文题目（评估跨语言能力）

### 5.2 客观任务详细设计

#### 5.2.1 知识问答（15-20 题）

**题目类型**：
- 事实性问答（Who/What/When/Where）：8-10 题
- 概念解释（Why/How）：4-6 题
- 多跳推理（需要组合多个知识点）：3-4 题

**评估方法**：
- 主指标：准确率（与标准答案匹配）
- 辅指标：F1 分数（部分匹配）、答案长度

**示例题目**：

```json
{
  "task_type": "qa",
  "difficulty": "easy",
  "question": "中国的首都是哪里？",
  "expected_answer": "北京",
  "temperature": 0.0,
  "max_tokens": 50
}
```

```json
{
  "task_type": "qa",
  "difficulty": "hard",
  "question": "解释量子纠缠现象，并说明其在量子计算中的应用。",
  "expected_keywords": ["量子态", "关联", "测量", "量子比特", "并行计算"],
  "temperature": 0.0,
  "max_tokens": 300
}
```

#### 5.2.2 数学计算（10-15 题）

**题目类型**：
- 基础算术（加减乘除、百分比）：3-4 题
- 代数问题（方程求解、不等式）：3-4 题
- 应用题（行程、工程、利润）：4-6 题

**评估方法**：
- 主指标：最终答案准确率
- 辅指标：推理步骤完整性（是否展示计算过程）

**示例题目**：

```json
{
  "task_type": "math",
  "difficulty": "medium",
  "question": "一辆汽车以 60 公里/小时的速度行驶了 2.5 小时，然后以 80 公里/小时的速度又行驶了 1.5 小时。请问总共行驶了多少公里？",
  "expected_answer": "270",
  "expected_steps": ["60 × 2.5 = 150", "80 × 1.5 = 120", "150 + 120 = 270"],
  "temperature": 0.0,
  "max_tokens": 200
}
```

#### 5.2.3 代码生成（10-12 题）

**题目类型**：
- 函数实现（单一功能）：4-5 题
- 类设计（面向对象）：2-3 题
- 算法实现（排序、搜索、动态规划）：4-5 题

**评估方法**：
- 主指标：测试用例通过率
- 辅指标：编译成功率、代码风格（PEP8）

**示例题目**：

```json
{
  "task_type": "code",
  "difficulty": "medium",
  "question": "编写一个 Python 函数 `fibonacci(n)`，返回斐波那契数列的第 n 项（n >= 0）。要求使用动态规划优化，时间复杂度 O(n)。",
  "test_cases": [
    {"input": 0, "expected": 0},
    {"input": 1, "expected": 1},
    {"input": 5, "expected": 5},
    {"input": 10, "expected": 55}
  ],
  "temperature": 0.1,
  "max_tokens": 300
}
```

#### 5.2.4 逻辑推理（8-10 题）

**题目类型**：
- 演绎推理（三段论）：2-3 题
- 归纳推理（模式识别）：2-3 题
- 因果推理（原因分析）：4-5 题

**评估方法**：
- 主指标：结论准确率
- 辅指标：推理链完整性（是否展示推理步骤）

**示例题目**：

```json
{
  "task_type": "reasoning",
  "difficulty": "hard",
  "question": "所有的猫都是哺乳动物。所有的哺乳动物都需要呼吸。小花是一只猫。请问：小花需要呼吸吗？请给出推理过程。",
  "expected_answer": "是",
  "expected_reasoning": ["小花是猫", "猫是哺乳动物", "哺乳动物需要呼吸", "因此小花需要呼吸"],
  "temperature": 0.1,
  "max_tokens": 200
}
```

### 5.3 主观任务详细设计

#### 5.3.1 文本摘要（5-8 题）

**题目类型**：
- 新闻摘要（200-500 字原文）：2-3 题
- 论文摘要（500-1000 字原文）：2-3 题
- 会议纪要（300-600 字原文）：1-2 题

**评估方法**：
- 主指标：ROUGE-L（与参考摘要的重叠度）
- 辅指标：BERTScore（语义相似度）、压缩比

**示例题目**：

```json
{
  "task_type": "summary",
  "difficulty": "medium",
  "source_text": "（此处为 300-500 字的新闻文本）",
  "reference_summary": "（此处为 50-100 字的参考摘要）",
  "instruction": "请将以下新闻总结为 50-100 字的摘要，保留关键信息。",
  "temperature": 0.7,
  "max_tokens": 150,
  "repeat": 5
}
```

#### 5.3.2 创意写作（5-8 题）

**题目类型**：
- 故事续写（给定开头）：2-3 题
- 诗歌创作（给定主题）：1-2 题
- 广告文案（给定产品）：2-3 题

**评估方法**：
- 主指标：Distinct-2（词汇多样性，bigram 去重率）
- 辅指标：流畅度（困惑度）、长度适中性

**示例题目**：

```json
{
  "task_type": "creative",
  "difficulty": "medium",
  "prompt": "请续写以下故事开头（100-200 字）：\n\n夜幕降临，小镇的街道上空无一人。突然，一道刺眼的光芒从天而降...",
  "temperature": 0.8,
  "max_tokens": 300,
  "repeat": 5,
  "evaluation": {
    "distinct_2": "计算 bigram 去重率",
    "fluency": "使用语言模型计算困惑度"
  }
}
```

#### 5.3.3 多轮对话（5-8 组，每组 2-3 轮）

**题目类型**：
- 信息咨询（旅游、购物、医疗）：2-3 组
- 任务协作（计划制定、问题解决）：2-3 组
- 闲聊对话（日常交流）：1-2 组

**评估方法**：
- 主指标：上下文一致性（是否记住前文信息）
- 辅指标：BERTScore（与参考回复的语义相似度）

**示例题目**：

```json
{
  "task_type": "multi_turn",
  "difficulty": "medium",
  "conversation": [
    {
      "turn": 1,
      "user": "我想去北京旅游，有什么推荐的景点吗？",
      "expected_topics": ["故宫", "长城", "天安门", "颐和园"]
    },
    {
      "turn": 2,
      "user": "你刚才提到的第一个景点，门票多少钱？",
      "context_check": "需要记住第一轮提到的第一个景点",
      "expected_answer_contains": ["门票", "价格"]
    },
    {
      "turn": 3,
      "user": "那个景点附近有什么好吃的？",
      "context_check": "需要记住前两轮讨论的景点",
      "expected_answer_contains": ["餐厅", "美食", "小吃"]
    }
  ],
  "temperature": 0.7,
  "max_tokens": 200,
  "repeat": 3
}
```

### 5.4 上下文检验任务详细设计

#### 5.4.1 信息提取型（3-4 题）

**设计**：先提供一段包含多个信息点的文本，然后在后续轮次中提问细节。

**示例**：

```json
{
  "task_type": "context_verification",
  "subtype": "information_extraction",
  "prompts": [
    "我现在要告诉你三个人的信息。张三：35岁，工程师，喜欢篮球。李四：28岁，教师，喜欢阅读。王五：42岁，医生，喜欢旅游。",
    "请问李四的职业是什么？",
    "谁的年龄最大？",
    "喜欢篮球的人是做什么工作的？"
  ],
  "expected_answers": ["教师", "王五", "工程师"],
  "temperature": 0.2,
  "repeat": 3
}
```

#### 5.4.2 信息整合型（2-3 题）

**设计**：分多轮提供信息，最后要求综合回答。

**示例**：

```json
{
  "task_type": "context_verification",
  "subtype": "information_integration",
  "prompts": [
    "小明今天早上 8 点出门。",
    "他先去了图书馆，待了 2 小时。",
    "然后去咖啡馆，待了 1.5 小时。",
    "请问小明现在几点了？他去了哪些地方？"
  ],
  "expected_answer": {
    "time": "11:30 或 11点30分",
    "places": ["图书馆", "咖啡馆"]
  },
  "temperature": 0.2,
  "repeat": 3
}
```

#### 5.4.3 指令遵循型（2-3 题）

**设计**：第一轮给出规则，后续轮次检验是否遵守。

**示例**：

```json
{
  "task_type": "context_verification",
  "subtype": "instruction_following",
  "prompts": [
    "从现在开始，你的每个回答都必须以"明白了"开头，并且不超过 50 字。",
    "请介绍一下人工智能。",
    "什么是机器学习？"
  ],
  "evaluation": {
    "starts_with": "明白了",
    "max_length": 50
  },
  "temperature": 0.2,
  "repeat": 3
}
```

### 5.5 重复生成策略与统计方法

| 生成策略 | 温度 | 重复次数 | 统计方法 | 适用任务 |
|---------|------|---------|---------|---------|
| **Greedy** | 0.0 | 1 | 单次结果 | 知识问答、数学计算 |
| **低温度** | 0.1-0.2 | 3 | 多数投票、一致性率 | 代码生成、逻辑推理、上下文检验 |
| **采样** | 0.7-0.8 | 5 | 均值、标准差、多样性 | 文本摘要、创意写作、多轮对话 |

**统计指标**：

1. **确定性任务（Greedy）**：
   - 准确率 = 正确数 / 总题数
   - 平均延迟、平均能耗

2. **低温度任务（3 次重复）**：
   - 多数投票准确率 = 投票正确数 / 总题数
   - 一致性率 = 3 次结果完全一致的题目数 / 总题数
   - 平均延迟、平均能耗（取 3 次平均）

3. **采样任务（5 次重复）**：
   - 质量均值 ± 标准差（ROUGE、BERTScore、Distinct-2）
   - 多样性：5 次生成的平均 Self-BLEU（越低越多样）
   - 平均延迟、平均能耗（取 5 次平均）

### 5.6 自动化评估工具链

#### 5.6.1 客观任务评估

**准确率计算**（知识问答、数学）：

```python
def evaluate_accuracy(generated_answer, expected_answer):
    """
    简单字符串匹配或关键词匹配
    """
    generated = generated_answer.strip().lower()
    expected = expected_answer.strip().lower()
    
    # 精确匹配
    if generated == expected:
        return 1.0
    
    # 包含匹配
    if expected in generated:
        return 0.8
    
    # 关键词匹配（针对长答案）
    keywords = expected.split()
    matched = sum(1 for kw in keywords if kw in generated)
    return matched / len(keywords) if keywords else 0.0
```

**代码评估**（编译率、测试通过率）：

```python
import subprocess
import tempfile
import os

def evaluate_code(generated_code, test_cases, language="python"):
    """
    评估生成的代码
    """
    results = {
        "compiles": False,
        "test_passed": 0,
        "test_total": len(test_cases),
        "errors": []
    }
    
    # 保存代码到临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(generated_code)
        code_file = f.name
    
    try:
        # 检查编译（Python 语法检查）
        result = subprocess.run(
            ['python', '-m', 'py_compile', code_file],
            capture_output=True,
            timeout=5
        )
        
        if result.returncode == 0:
            results["compiles"] = True
            
            # 运行测试用例
            for test in test_cases:
                try:
                    # 执行代码并检查输出
                    # （此处简化，实际需要更复杂的沙箱环境）
                    exec_result = subprocess.run(
                        ['python', code_file],
                        input=str(test['input']),
                        capture_output=True,
                        timeout=5,
                        text=True
                    )
                    
                    if str(test['expected']) in exec_result.stdout:
                        results["test_passed"] += 1
                except Exception as e:
                    results["errors"].append(str(e))
        else:
            results["errors"].append(result.stderr.decode())
            
    except Exception as e:
        results["errors"].append(str(e))
    finally:
        os.unlink(code_file)
    
    return results
```

#### 5.6.2 主观任务评估

**ROUGE 评估**（文本摘要）：

```python
from rouge import Rouge

def evaluate_summary(generated_summary, reference_summary):
    """
    使用 ROUGE 评估摘要质量
    """
    rouge = Rouge()
    scores = rouge.get_scores(generated_summary, reference_summary)[0]
    
    return {
        "rouge_1_f": scores['rouge-1']['f'],
        "rouge_2_f": scores['rouge-2']['f'],
        "rouge_l_f": scores['rouge-l']['f']
    }
```

**Distinct-N 评估**（创意写作）：

```python
def calculate_distinct_n(text, n=2):
    """
    计算 Distinct-N（词汇多样性）
    """
    tokens = text.split()
    if len(tokens) < n:
        return 0.0
    
    ngrams = [tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)]
    unique_ngrams = set(ngrams)
    
    return len(unique_ngrams) / len(ngrams) if ngrams else 0.0

def evaluate_creativity(generated_texts):
    """
    评估多次生成的创意性
    """
    distinct_2_scores = [calculate_distinct_n(text, 2) for text in generated_texts]
    
    # Self-BLEU（多样性）
    from nltk.translate.bleu_score import sentence_bleu
    self_bleu_scores = []
    for i, text in enumerate(generated_texts):
        references = [t.split() for j, t in enumerate(generated_texts) if j != i]
        hypothesis = text.split()
        if references:
            score = sentence_bleu(references, hypothesis)
            self_bleu_scores.append(score)
    
    return {
        "distinct_2_mean": sum(distinct_2_scores) / len(distinct_2_scores),
        "distinct_2_std": np.std(distinct_2_scores),
        "self_bleu_mean": sum(self_bleu_scores) / len(self_bleu_scores) if self_bleu_scores else 0.0
    }
```

**BERTScore 评估**（多轮对话）：

```python
from bert_score import score

def evaluate_dialogue(generated_response, reference_response):
    """
    使用 BERTScore 评估对话质量
    """
    P, R, F1 = score(
        [generated_response],
        [reference_response],
        lang='zh',
        model_type='bert-base-chinese'
    )
    
    return {
        "bertscore_precision": P.item(),
        "bertscore_recall": R.item(),
        "bertscore_f1": F1.item()
    }
```

### 5.7 测试用例文件结构

**文件组织**：

```
data/experiments_N/
├── test_cases.json          # 主测试用例文件
├── test_cases_qa.json       # 知识问答专用
├── test_cases_math.json     # 数学计算专用
├── test_cases_code.json     # 代码生成专用
├── test_cases_summary.json  # 文本摘要专用
├── test_cases_creative.json # 创意写作专用
└── test_cases_dialogue.json # 多轮对话专用
```

**主文件格式**（`test_cases.json`）：

```json
{
  "metadata": {
    "version": "1.0",
    "total_tasks": 85,
    "created_date": "2026-03-01",
    "description": "综合测试用例集，涵盖 8 种任务类型"
  },
  "tasks": [
    {
      "id": "qa_001",
      "task_type": "qa",
      "difficulty": "easy",
      "language": "zh",
      "question": "中国的首都是哪里？",
      "expected_answer": "北京",
      "temperature": 0.0,
      "max_tokens": 50,
      "repeat": 1
    },
    {
      "id": "code_001",
      "task_type": "code",
      "difficulty": "medium",
      "language": "zh",
      "question": "编写一个 Python 函数计算斐波那契数列第 n 项",
      "test_cases": [
        {"input": 0, "expected": 0},
        {"input": 5, "expected": 5}
      ],
      "temperature": 0.1,
      "max_tokens": 300,
      "repeat": 3
    }
  ]
}
```

### 5.8 实验效率优化

**批处理策略**：

1. **任务分组**：
   - 按温度分组（Greedy → 低温度 → 采样）
   - 同温度任务连续执行，减少模型参数切换

2. **并行化**（可选）：
   - 如果硬件允许，可以同时运行多个模型（不同 GPU）
   - 当前环境（单 GPU）不适用

3. **缓存机制**：
   - 对于重复的 prompt（如多次运行同一题目），缓存 prefill 结果
   - Ollama 自动支持 KV cache

4. **冷却时间**：
   - 任务间间隔 30 秒，避免温度累积
   - 每个模型测试完成后，等待 5 分钟冷却

**预计时间**：

| 模型 | 任务数 | 平均每题时间 | 重复次数 | 总时间 |
|------|-------|------------|---------|--------|
| qwen3:4b | 85 | 10-15s | 1-5 次 | 2-3 小时 |
| qwen3:8b | 85 | 15-20s | 1-5 次 | 3-4 小时 |
| deepseek-r1:8b | 85 | 15-25s | 1-5 次 | 3-5 小时 |
| gemma3:4b | 85 | 10-15s | 1-5 次 | 2-3 小时 |

**9 个模型完整测试**：预计 25-35 小时（分多天进行）

### 5.9 与现有实现的对接

**当前已有的测试用例**：
- `data/test/test_cases.json` - 基础测试用例
- `data/test/test_cases_multi_turn.json` - 多轮对话测试
- `data/test/test_cases_ollama.json` - Ollama 专用测试
- `data/experiments_4/test_cases.json` - 实验 4 测试用例

**建议**：
1. 基于现有文件扩展，保持格式一致性
2. 新增字段：`difficulty`、`language`、`expected_answer`、`test_cases`
3. 使用 `experiments/experiment_runner.py` 作为主执行器
4. 监控数据通过 `experiments/monitor.py` 自动收集

**迁移步骤**：
1. 审查现有测试用例，标注难度和语言
2. 补充缺失的任务类型（逻辑推理、上下文检验）
3. 为每个任务添加评估标准（expected_answer、test_cases）
4. 更新 `experiment_runner.py` 以支持新的评估逻辑


## 6. 评估指标体系（重构版）

### 6.0 符号表（统一定义）

为确保全文符号使用一致，以下列出所有关键指标的符号、含义、单位和计算方法：

| 类别 | 符号 | 名称 | 单位 | 计算公式 | 说明 |
|------|------|------|------|----------|------|
| **功耗指标** | $P_{idle}$ | 空闲功耗 | W | 系统空闲时功耗均值 | 基线功耗，每轮实验前测量 |
| | $P_{total}$ | 总功耗 | W | GPU + CPU 功耗之和 | 实时测量值 |
| | $P_{inc}$ | 增量功耗 | W | $P_{total} - P_{idle}$ | 推理引起的额外功耗 |
| | $P_{GPU}$ | GPU 功耗 | W | 通过 pynvml 读取 | RTX 4060 实测值 |
| | $P_{CPU}$ | CPU 功耗 | W | $U_{CPU} \times TDP$ | 估算值，$TDP=65W$ |
| | $P_{prefill}$ | Prefill 阶段功耗 | W | 事件标记分段统计 | 首 token 生成前 |
| | $P_{decode}$ | Decode 阶段功耗 | W | 事件标记分段统计 | 后续 token 生成 |
| **能耗指标** | $E_{total}$ | 总能耗 | J | $\int P_{total}(t) dt$ | 整个推理过程能耗 |
| | $E_{GPU}$ | GPU 能耗 | J | $\int P_{GPU}(t) dt$ | GPU 部分能耗 |
| | $E_{CPU}$ | CPU 能耗 | J | $\int P_{CPU}(t) dt$ | CPU 部分能耗（估算） |
| | $E_{token}$ | 每 token 能耗 | J/token | $E_{total} / N_{tokens}$ | 能耗效率核心指标 |
| **时间指标** | $T_{total}$ | 总推理时间 | s | 从开始到结束的时间 | 包含 prefill + decode |
| | $T_{prefill}$ | Prefill 时间 | s | 首 token 生成前时间 | 即 TTFT |
| | $T_{decode}$ | Decode 时间 | s | 后续 token 生成时间 | $T_{total} - T_{prefill}$ |
| | $TTFT$ | 首 token 延迟 | ms | 从输入到首 token 时间 | Time To First Token |
| | $TPOT$ | 每 token 延迟 | ms/token | $T_{decode} / (N_{tokens} - 1)$ | Time Per Output Token |
| | $Latency$ | 总延迟 | s | $T_{total}$ | 用户感知延迟 |
| **吞吐指标** | $N_{tokens}$ | 生成 token 数 | tokens | 模型输出 token 总数 | 不含输入 tokens |
| | $N_{input}$ | 输入 token 数 | tokens | 输入 prompt token 数 | 用于上下文分析 |
| | $Throughput$ | 吞吐量 | tokens/s | $N_{tokens} / T_{total}$ | 生成速度 |
| | $PPW$ | 每瓦性能 | tokens/s/W | $Throughput / P_{inc}$ | 能效综合指标 |
| **质量指标** | $Q_{task}$ | 任务质量得分 | [0, 1] | 按任务类型计算 | 归一化到 0-1 |
| | $Q_{overall}$ | 综合质量得分 | [0, 1] | $\sum w_i \cdot Q_{task_i}$ | 加权平均，$\sum w_i = 1$ |
| | $Acc$ | 准确率 | [0, 1] | 正确数 / 总数 | 客观任务 |
| | $ROUGE$ | ROUGE 分数 | [0, 1] | ROUGE-L F1 | 文本摘要 |
| | $BERTScore$ | BERTScore | [0, 1] | BERT 语义相似度 | 对话、摘要 |
| | $Distinct$ | Distinct-N | [0, 1] | N-gram 去重率 | 创意写作多样性 |
| **归一化指标** | $Q_{norm}$ | 归一化质量 | [0, 1] | Min-Max Scaling | 按任务分组归一化 |
| | $E_{norm}$ | 归一化能效 | [0, 1] | $1 - \frac{E_{token} - E_{min}}{E_{max} - E_{min}}$ | 越小越好，反转归一化 |
| | $T_{norm}$ | 归一化吞吐 | [0, 1] | $\frac{Throughput - T_{min}}{T_{max} - T_{min}}$ | 越大越好 |
| | $L_{norm}$ | 归一化延迟 | [0, 1] | $1 - \frac{Latency - L_{min}}{L_{max} - L_{min}}$ | 越小越好，反转归一化 |
| **复合指标** | $Eff_{score}$ | 效率得分 | [0, 1] | $0.4 T_{norm} + 0.3 L_{norm} + 0.3 E_{norm}$ | 综合效率评分 |
| | $QE_{ratio}$ | 质效比 | - | $\frac{Q_{norm} + \epsilon}{1.01 - Eff_{score}}$ | $\epsilon=0.01$ 避免除零 |
| | $Score_{final}$ | 最终得分 | - | $Q_{overall} \times PPW$ | 质量×能效 |
| **成本指标** | $Cost_{GPU}$ | GPU 成本 | $ | $C_{GPU/h} \times T_{total}/3600$ | 云服务定价 |
| | $Cost_{energy}$ | 能耗成本 | $ | $E_{total} \times P_{elec} / 3.6 \times 10^6$ | 电价 $P_{elec}$ $/kWh |
| | $Cost_{total}$ | 总成本 | $ | $Cost_{GPU} + Cost_{energy}$ | 简化 TCO |
| | $CPQ$ | 单位成本质量 | 1/$ | $Q_{overall} / Cost_{total}$ | Cost Per Quality |
| **系统指标** | $U_{CPU}$ | CPU 利用率 | % | psutil 测量 | 0-100% |
| | $U_{GPU}$ | GPU 利用率 | % | pynvml 测量 | 0-100% |
| | $M_{GPU}$ | GPU 显存使用 | MB | pynvml 测量 | 峰值显存 |
| | $T_{GPU}$ | GPU 温度 | °C | pynvml 测量 | 热管理参考 |

**符号使用规范**：
1. 所有功耗/能耗相关指标使用 $P$ (Power) 或 $E$ (Energy) 前缀
2. 所有时间相关指标使用 $T$ (Time) 前缀
3. 所有质量相关指标使用 $Q$ (Quality) 前缀
4. 归一化指标统一使用 $_{norm}$ 下标
5. 下标使用 $_{描述}$ 格式，如 $P_{idle}$、$T_{total}$



### 6.1 能效指标详解

基于 Windows/RTX 4060 Laptop 环境的实际测量能力，定义以下能效指标：

| 指标 | 符号 | 计算公式 | 单位 | 测量方法 | 说明 |
|------|------|----------|------|----------|------|
| **空闲功耗** | $P_{idle}$ | 系统空闲时功耗均值 | W | 5 分钟基线测量 | 每轮实验前测量，作为基准 |
| **系统增量功耗** | $P_{inc}$ | $P_{total} - P_{idle}$ | W | 实时计算 | 真正由推理引起的功耗 |
| **分阶段功耗** | $P_{prefill}$, $P_{decode}$ | 事件标记分段统计 | W | 时间戳对齐 | 分析计算 vs 访存阶段 |
| **吞吐量** | $Throughput$ | $N_{tokens} / T_{total}$ | tokens/s | 后处理计算 | 包含输入处理时间 |
| **首 token 延迟** | $TTFT$ | 从输入到首 token 时间 | ms | 事件日志记录 | 影响用户体验的关键指标 |
| **每 token 延迟** | $TPOT$ | $T_{decode} / (N_{tokens} - 1)$ | ms/token | 后处理计算 | Decode 阶段生成速度 |
| **每 token 能耗** | $E_{token}$ | $E_{total} / N_{tokens}$ | J/token | 后处理计算 | 更精确的能耗度量 |
| **每瓦性能** | $PPW$ | $Throughput / P_{inc}$ | tokens/s/W | 后处理计算 | 能效的综合指标 |
| **标准化能效分** | $E_{norm}$ | $1 - \frac{E_{token} - E_{min}}{E_{max} - E_{min}}$ | [0, 1] | 按任务分组归一化 | 1 为最优，便于横向比较 |

**计算示例**（Python 实现）：

```python
def calculate_efficiency_metrics(monitor_data, n_tokens, t_total, t_prefill):
    """
    计算能效指标
    
    Args:
        monitor_data: 监控数据字典（来自 ResourceMonitor.summary()）
        n_tokens: 生成的 token 数量
        t_total: 总推理时间（秒）
        t_prefill: Prefill 时间（秒）
    
    Returns:
        dict: 能效指标字典
    """
    # 基础指标
    p_idle = 50.0  # 假设空闲功耗 50W（需实测）
    p_total_avg = monitor_data['gpu_power_avg_w'] + monitor_data.get('cpu_power_avg_w', 0)
    p_inc = p_total_avg - p_idle
    
    e_total = monitor_data['gpu_energy_j'] + monitor_data.get('cpu_energy_j_approx', 0)
    
    # 计算指标
    throughput = n_tokens / t_total if t_total > 0 else 0
    ttft = t_prefill * 1000  # 转换为毫秒
    tpot = (t_total - t_prefill) / (n_tokens - 1) * 1000 if n_tokens > 1 else 0
    e_token = e_total / n_tokens if n_tokens > 0 else 0
    ppw = throughput / p_inc if p_inc > 0 else 0
    
    return {
        'p_idle_w': p_idle,
        'p_inc_w': p_inc,
        'e_total_j': e_total,
        'throughput_tps': throughput,
        'ttft_ms': ttft,
        'tpot_ms': tpot,
        'e_token_j': e_token,
        'ppw': ppw
    }
```

**归一化方法**（Min-Max Scaling）：

```python
import pandas as pd

def normalize_efficiency_metrics(df, task_col='task_type'):
    """
    按任务类型分组归一化能效指标
    
    Args:
        df: 包含原始指标的 DataFrame
        task_col: 任务类型列名
    
    Returns:
        DataFrame: 添加归一化列的 DataFrame
    """
    # 按任务分组归一化
    for task in df[task_col].unique():
        mask = df[task_col] == task
        
        # 吞吐量：越大越好
        throughput = df.loc[mask, 'throughput_tps']
        df.loc[mask, 't_norm'] = (throughput - throughput.min()) / (throughput.max() - throughput.min() + 1e-9)
        
        # 延迟：越小越好（反转）
        latency = df.loc[mask, 'ttft_ms']
        df.loc[mask, 'l_norm'] = 1 - (latency - latency.min()) / (latency.max() - latency.min() + 1e-9)
        
        # 能耗：越小越好（反转）
        energy = df.loc[mask, 'e_token_j']
        df.loc[mask, 'e_norm'] = 1 - (energy - energy.min()) / (energy.max() - energy.min() + 1e-9)
    
    # 综合效率得分
    df['eff_score'] = 0.4 * df['t_norm'] + 0.3 * df['l_norm'] + 0.3 * df['e_norm']
    
    return df
```



### 6.2 质量指标详解

基于第 5 节定义的任务类型，为每种任务设计相应的质量评估指标：

| 任务类型 | 主指标 | 符号 | 计算方法 | 辅指标 | 统计方法 |
|---------|--------|------|----------|--------|----------|
| **知识问答** | 准确率 | $Acc_{qa}$ | 正确数 / 总数 | F1 分数、答案长度 | 均值 ± 标准差 |
| **数学计算** | 准确率 | $Acc_{math}$ | 正确数 / 总数 | 步骤完整性 | 均值 ± 标准差 |
| **代码生成** | 测试通过率 | $Pass_{code}$ | 通过数 / 总数 | 编译成功率 | 均值（3 次投票） |
| **逻辑推理** | 准确率 | $Acc_{reason}$ | 正确数 / 总数 | 推理链完整性 | 均值（3 次投票） |
| **文本摘要** | ROUGE-L | $ROUGE_L$ | F1 分数 | BERTScore | 均值 ± 标准差（5 次） |
| **创意写作** | Distinct-2 | $Distinct_2$ | Bigram 去重率 | 流畅度（困惑度） | 均值 ± 标准差（5 次） |
| **多轮对话** | BERTScore | $BERT_F1$ | F1 分数 | 上下文一致性 | 均值（3 次） |
| **上下文检验** | 准确率 | $Acc_{context}$ | 正确数 / 总数 | 信息提取完整性 | 均值（3 次投票） |

**综合质量得分计算**：

\[
Q_{overall} = \sum_{i=1}^{8} w_i \cdot Q_{task_i}
\]

其中：
- $w_i$ 为任务权重，$\sum w_i = 1$
- 默认均等权重：$w_i = 1/8 = 0.125$
- 可根据应用场景调整权重（如代码生成场景提高 $w_{code}$）

**质量指标计算示例**：

```python
def calculate_quality_metrics(results_df):
    """
    计算各任务类型的质量指标
    
    Args:
        results_df: 包含任务结果的 DataFrame
            必需列：task_type, correct, total, rouge_l, bertscore_f1, distinct_2
    
    Returns:
        dict: 各任务质量得分
    """
    quality_scores = {}
    
    # 客观任务：准确率
    for task in ['qa', 'math', 'reasoning', 'context']:
        mask = results_df['task_type'] == task
        if mask.sum() > 0:
            acc = results_df.loc[mask, 'correct'].sum() / results_df.loc[mask, 'total'].sum()
            quality_scores[f'q_{task}'] = acc
    
    # 代码生成：测试通过率
    mask = results_df['task_type'] == 'code'
    if mask.sum() > 0:
        pass_rate = results_df.loc[mask, 'tests_passed'].sum() / results_df.loc[mask, 'tests_total'].sum()
        quality_scores['q_code'] = pass_rate
    
    # 文本摘要：ROUGE-L
    mask = results_df['task_type'] == 'summary'
    if mask.sum() > 0:
        rouge_l = results_df.loc[mask, 'rouge_l'].mean()
        quality_scores['q_summary'] = rouge_l
    
    # 创意写作：Distinct-2
    mask = results_df['task_type'] == 'creative'
    if mask.sum() > 0:
        distinct_2 = results_df.loc[mask, 'distinct_2'].mean()
        quality_scores['q_creative'] = distinct_2
    
    # 多轮对话：BERTScore
    mask = results_df['task_type'] == 'dialogue'
    if mask.sum() > 0:
        bertscore = results_df.loc[mask, 'bertscore_f1'].mean()
        quality_scores['q_dialogue'] = bertscore
    
    # 综合质量得分（均等权重）
    quality_scores['q_overall'] = sum(quality_scores.values()) / len(quality_scores)
    
    return quality_scores
```

**归一化质量指标**：

```python
def normalize_quality_metrics(df, task_col='task_type'):
    """
    按任务类型分组归一化质量指标
    
    Args:
        df: 包含原始质量指标的 DataFrame
        task_col: 任务类型列名
    
    Returns:
        DataFrame: 添加归一化质量列的 DataFrame
    """
    # 按任务分组归一化
    for task in df[task_col].unique():
        mask = df[task_col] == task
        
        # 质量指标：越大越好
        quality = df.loc[mask, 'quality_score']
        df.loc[mask, 'q_norm'] = (quality - quality.min()) / (quality.max() - quality.min() + 1e-9)
    
    return df
```

### 6.3 综合效质比与最终评分

结合能效指标和质量指标，计算综合效质比和最终评分：

#### 6.3.1 质效比（Quality-Efficiency Ratio）

\[
QE_{ratio} = \frac{Q_{norm} + \epsilon}{1.01 - Eff_{score}}
\]

其中：
- $Q_{norm}$：归一化质量得分，范围 [0, 1]
- $Eff_{score}$：效率得分，范围 [0, 1]
- $\epsilon = 0.01$：避免分子为零
- $1.01$：避免分母为零

**特点**：
- 质量越高、效率越高，质效比越大
- 平衡质量和效率两个维度
- 适用于模型横向对比

**计算示例**：

```python
def calculate_qe_ratio(df):
    """
    计算质效比
    
    Args:
        df: 包含 q_norm 和 eff_score 的 DataFrame
    
    Returns:
        DataFrame: 添加 qe_ratio 列的 DataFrame
    """
    epsilon = 0.01
    df['qe_ratio'] = (df['q_norm'] + epsilon) / (1.01 - df['eff_score'])
    return df
```

#### 6.3.2 能效加权得分

\[
Score_{final} = Q_{overall} \times PPW
\]

或

\[
Score_{final} = \frac{Q_{overall}}{E_{token}}
\]

**特点**：
- 直接反映"单位能耗的质量产出"
- 适用于能耗敏感场景
- 数值越大越好

**计算示例**：

```python
def calculate_final_score(df, method='ppw'):
    """
    计算最终得分
    
    Args:
        df: 包含质量和能效指标的 DataFrame
        method: 'ppw' 或 'energy'
    
    Returns:
        DataFrame: 添加 score_final 列的 DataFrame
    """
    if method == 'ppw':
        df['score_final'] = df['q_overall'] * df['ppw']
    elif method == 'energy':
        df['score_final'] = df['q_overall'] / (df['e_token_j'] + 1e-9)
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return df
```

#### 6.3.3 成本效能比（Cost-Performance Ratio）

引入简化的 TCO（Total Cost of Ownership）模型：

\[
Cost_{total} = Cost_{GPU} + Cost_{energy}
\]

其中：

\[
Cost_{GPU} = C_{GPU/h} \times \frac{T_{total}}{3600}
\]

\[
Cost_{energy} = E_{total} \times \frac{P_{elec}}{3.6 \times 10^6}
\]

- $C_{GPU/h}$：GPU 小时成本（$/h），参考云服务定价
  - RTX 4060 Laptop 等效成本：约 $0.5-1.0/h（估算）
  - A100 云服务：约 $3-4/h
- $P_{elec}$：电价（$/kWh），中国平均约 $0.08/kWh
- $E_{total}$：总能耗（J）
- $T_{total}$：总时间（s）

**单位成本质量**（Cost Per Quality）：

\[
CPQ = \frac{Q_{overall}}{Cost_{total}}
\]

**计算示例**：

```python
def calculate_cost_metrics(df, gpu_cost_per_hour=0.75, electricity_price=0.08):
    """
    计算成本指标
    
    Args:
        df: 包含时间和能耗指标的 DataFrame
        gpu_cost_per_hour: GPU 小时成本（$/h）
        electricity_price: 电价（$/kWh）
    
    Returns:
        DataFrame: 添加成本列的 DataFrame
    """
    # GPU 成本
    df['cost_gpu_usd'] = gpu_cost_per_hour * df['t_total_s'] / 3600
    
    # 能耗成本（J 转 kWh）
    df['cost_energy_usd'] = df['e_total_j'] * electricity_price / (3.6 * 1e6)
    
    # 总成本
    df['cost_total_usd'] = df['cost_gpu_usd'] + df['cost_energy_usd']
    
    # 单位成本质量
    df['cpq'] = df['q_overall'] / (df['cost_total_usd'] + 1e-9)
    
    return df
```

#### 6.3.4 帕累托前沿分析

在质量-能效二维空间中，识别帕累托最优解：

**定义**：模型 A 帕累托优于模型 B，当且仅当：
- $Q_A \geq Q_B$ 且 $E_A \leq E_B$（至少一个严格不等）

**帕累托前沿**：所有不被其他模型帕累托支配的模型集合

**计算示例**：

```python
def find_pareto_frontier(df, quality_col='q_overall', efficiency_col='e_token_j'):
    """
    识别帕累托前沿
    
    Args:
        df: 包含质量和能效指标的 DataFrame
        quality_col: 质量列名（越大越好）
        efficiency_col: 能效列名（越小越好）
    
    Returns:
        DataFrame: 添加 is_pareto 列的 DataFrame
    """
    df = df.copy()
    df['is_pareto'] = True
    
    for i in df.index:
        for j in df.index:
            if i != j:
                # 如果 j 帕累托优于 i
                if (df.loc[j, quality_col] >= df.loc[i, quality_col] and
                    df.loc[j, efficiency_col] <= df.loc[i, efficiency_col] and
                    (df.loc[j, quality_col] > df.loc[i, quality_col] or
                     df.loc[j, efficiency_col] < df.loc[i, efficiency_col])):
                    df.loc[i, 'is_pareto'] = False
                    break
    
    return df
```

**可视化示例**：

```python
import matplotlib.pyplot as plt

def plot_pareto_frontier(df, quality_col='q_overall', efficiency_col='e_token_j'):
    """
    绘制帕累托前沿图
    """
    plt.figure(figsize=(10, 6))
    
    # 非帕累托点
    non_pareto = df[~df['is_pareto']]
    plt.scatter(non_pareto[efficiency_col], non_pareto[quality_col], 
                c='lightgray', s=100, alpha=0.5, label='Non-Pareto')
    
    # 帕累托前沿点
    pareto = df[df['is_pareto']].sort_values(efficiency_col)
    plt.scatter(pareto[efficiency_col], pareto[quality_col], 
                c='red', s=150, marker='*', label='Pareto Frontier')
    
    # 连接帕累托点
    plt.plot(pareto[efficiency_col], pareto[quality_col], 
             'r--', alpha=0.5, linewidth=2)
    
    # 标注模型名称
    for idx, row in pareto.iterrows():
        plt.annotate(row['model_name'], 
                     (row[efficiency_col], row[quality_col]),
                     xytext=(5, 5), textcoords='offset points')
    
    plt.xlabel('Energy per Token (J/token) - Lower is Better')
    plt.ylabel('Quality Score - Higher is Better')
    plt.title('Pareto Frontier: Quality vs Energy Efficiency')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('pareto_frontier.png', dpi=300)
    plt.show()
```

### 6.4 指标汇总与使用建议

| 应用场景 | 推荐指标 | 说明 |
|---------|---------|------|
| **模型选型** | $QE_{ratio}$、帕累托前沿 | 平衡质量和效率 |
| **能耗敏感** | $E_{token}$、$PPW$ | 关注单位能耗产出 |
| **成本敏感** | $CPQ$、$Cost_{total}$ | 关注经济性 |
| **用户体验** | $TTFT$、$Latency$ | 关注响应速度 |
| **吞吐优化** | $Throughput$、$TPOT$ | 关注生成速度 |
| **综合评估** | $Score_{final}$、$Q_{overall}$ | 全面对比 |

**使用流程**：

1. **数据收集**：运行实验，收集原始指标
2. **归一化**：按任务分组进行 Min-Max Scaling
3. **计算复合指标**：$Eff_{score}$、$QE_{ratio}$、$Score_{final}$
4. **帕累托分析**：识别最优模型集合
5. **可视化**：生成对比图表
6. **报告生成**：自动化 Markdown 报告

**完整计算管线示例**：

```python
def complete_evaluation_pipeline(raw_results_df):
    """
    完整的评估指标计算管线
    
    Args:
        raw_results_df: 原始实验结果 DataFrame
    
    Returns:
        DataFrame: 包含所有指标的完整 DataFrame
    """
    df = raw_results_df.copy()
    
    # 1. 计算质量指标
    quality_metrics = calculate_quality_metrics(df)
    df = df.merge(pd.DataFrame([quality_metrics]), how='cross')
    
    # 2. 归一化质量和效率
    df = normalize_quality_metrics(df)
    df = normalize_efficiency_metrics(df)
    
    # 3. 计算质效比
    df = calculate_qe_ratio(df)
    
    # 4. 计算最终得分
    df = calculate_final_score(df, method='ppw')
    
    # 5. 计算成本指标
    df = calculate_cost_metrics(df)
    
    # 6. 帕累托前沿分析
    df = find_pareto_frontier(df)
    
    return df
```


## 7. 实验流程（针对每个模型-量化组合）

### 7.1 实验前准备

#### 7.1.1 环境配置检查清单

```bash
# 1. 检查 Ollama 服务状态
ollama list

# 2. 检查 GPU 状态
nvidia-smi

# 3. 检查 Python 环境
conda activate bartscore
python --version
pip list | findstr "pynvml psutil pandas"

# 4. 检查磁盘空间
dir C:\Users\<用户>\.ollama\models

# 5. 设置环境变量
set PYTHONUTF8=1
set CPU_TDP_W=65
```

#### 7.1.2 系统优化设置

**Windows 电源设置**：
1. 打开"控制面板" → "电源选项"
2. 选择"高性能"模式
3. 点击"更改计划设置" → "更改高级电源设置"
4. 设置：
   - 处理器电源管理 → 最小处理器状态：100%
   - 处理器电源管理 → 最大处理器状态：100%
   - PCI Express → 链接状态电源管理：关闭

**关闭后台进程**：
```powershell
# 关闭不必要的服务（可选）
Stop-Process -Name "chrome", "firefox", "Teams", "Slack" -ErrorAction SilentlyContinue

# 检查 CPU 和内存使用
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
```

**清理 GPU 缓存**：
```python
import torch
torch.cuda.empty_cache()
```

#### 7.1.3 创建实验目录结构

## 7. 实验流程（针对每个模型-框架-精度组合）

### 7.1 实验前准备

#### 7.1.1 环境配置检查清单

**硬件准备**：
- [ ] 确认 GPU 驱动正常：`nvidia-smi`
- [ ] 确认 CUDA 版本：`nvcc --version`（CUDA 12.6）
- [ ] 确认显存可用：至少 6GB 空闲
- [ ] 确认磁盘空间：至少 50GB 可用
- [ ] 关闭不必要的后台进程（浏览器、通讯软件等）
- [ ] 设置电源模式为"高性能"

**软件准备**：
- [ ] Ollama 服务运行中：`ollama list`
- [ ] Python 环境激活：`conda activate bartscore`
- [ ] 依赖包安装：`pip install pynvml psutil pandas numpy`
- [ ] 测试监控脚本：`python experiments/monitor.py`

**数据准备**：
- [ ] 测试用例文件就绪：`data/experiments_N/test_cases.json`
- [ ] 输出目录创建：`data/experiments_N/raw/`, `data/experiments_N/texts/`
- [ ] 日志目录创建：`logs/experiments_N/`

#### 7.1.2 模型下载与验证

```bash
# 下载所需模型（如果尚未下载）
ollama pull qwen3:4b
ollama pull qwen3:8b
ollama pull deepseek-r1:8b
ollama pull gemma3:4b

# 验证模型可用性
ollama list

# 测试模型推理
ollama run qwen3:4b "你好，请介绍一下自己。"
```

### 7.2 单次实验完整流程

#### 步骤 1：测量空闲功耗（5 分钟）

**目的**：建立功耗基线 $P_{idle}$

```python
import time
from experiments.monitor import ResourceMonitor

# 初始化监控器
monitor = ResourceMonitor(interval=0.2)  # 5Hz 采样

print("开始测量空闲功耗，请保持系统空闲...")
monitor.start()

# 空闲 5 分钟
time.sleep(300)

monitor.stop()
summary = monitor.summary()

# 记录空闲功耗
p_idle = summary['gpu_power_avg_w'] + summary.get('cpu_power_avg_w', 0)
p_idle_std = 0  # 可计算标准差

print(f"空闲功耗: {p_idle:.2f} ± {p_idle_std:.2f} W")

# 保存基线数据
import json
with open('logs/experiments_N/idle_baseline.json', 'w') as f:
    json.dump({
        'p_idle_w': p_idle,
        'p_idle_std_w': p_idle_std,
        'timestamp': time.time(),
        'summary': summary
    }, f, indent=2)
```

#### 步骤 2：加载模型并预热（1-2 分钟）

**目的**：稳定 GPU 温度和频率

```python
import ollama

model_name = "qwen3:8b"

print(f"加载模型: {model_name}")

# 预热：运行 3 次简单推理
warmup_prompts = [
    "你好",
    "1+1=?",
    "请介绍一下Python"
]

for i, prompt in enumerate(warmup_prompts, 1):
    print(f"预热 {i}/3...")
    response = ollama.generate(model=model_name, prompt=prompt)
    print(f"  生成 {len(response['response'])} 字符")

print("预热完成")
```

#### 步骤 3：冷却至空闲（1-2 分钟）

**目的**：确保功耗回落到基线水平

```python
print("等待系统冷却...")

# 启动监控检查功耗
monitor = ResourceMonitor(interval=1.0)
monitor.start()

cooled = False
check_interval = 10  # 每 10 秒检查一次
max_wait = 120  # 最多等待 2 分钟

start_time = time.time()
while not cooled and (time.time() - start_time) < max_wait:
    time.sleep(check_interval)
    
    # 检查最近功耗
    if len(monitor.gpu_power_w) > 5:
        recent_power = sum(monitor.gpu_power_w[-5:]) / 5
        if abs(recent_power - p_idle) < p_idle * 0.05:  # 在 ±5% 范围内
            cooled = True
            print(f"系统已冷却至基线: {recent_power:.2f} W")

monitor.stop()

if not cooled:
    print("警告：系统未完全冷却，但继续实验")
```

#### 步骤 4：启动同步监控（准备阶段）

**目的**：同时启动功耗监控和事件日志

```python
from experiments.monitor import ResourceMonitor
import json
import time

class EventLogger:
    """事件时间戳记录器"""
    def __init__(self, log_file):
        self.log_file = log_file
        self.events = []
        
    def log(self, event_name, metadata=None):
        event = {
            "timestamp": time.time(),
            "event": event_name,
            "metadata": metadata or {}
        }
        self.events.append(event)
        print(f"[Event] {event_name}: {metadata}")
        
    def save(self):
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)

# 初始化
experiment_id = f"exp_{int(time.time())}"
monitor = ResourceMonitor(interval=0.2)
logger = EventLogger(f"logs/experiments_N/{experiment_id}_events.json")

print(f"实验 ID: {experiment_id}")
logger.log("experiment_start", {
    "model": model_name,
    "experiment_id": experiment_id,
    "p_idle_w": p_idle
})
```

#### 步骤 5：执行任务（主实验阶段）

**目的**：遍历所有测试用例，记录详细数据

```python
import json

# 加载测试用例
with open('data/experiments_N/test_cases.json', 'r', encoding='utf-8') as f:
    test_cases = json.load(f)

# 结果存储
results = []

# 启动监控
monitor.start()
logger.log("monitoring_start")

# 遍历任务
for task_idx, task in enumerate(test_cases['tasks'], 1):
    task_id = task['id']
    task_type = task['task_type']
    prompt = task['question']
    temperature = task.get('temperature', 0.0)
    repeat = task.get('repeat', 1)
    
    print(f"\n[{task_idx}/{len(test_cases['tasks'])}] 任务: {task_id} ({task_type})")
    
    # 重复生成
    for run in range(repeat):
        logger.log("task_start", {
            "task_id": task_id,
            "task_type": task_type,
            "run": run + 1,
            "repeat": repeat
        })
        
        # 记录开始时间
        t_start = time.time()
        
        # 流式生成（用于记录首 token 时间）
        response_text = ""
        first_token_time = None
        
        try:
            stream = ollama.generate(
                model=model_name,
                prompt=prompt,
                stream=True,
                options={
                    'temperature': temperature,
                    'num_predict': task.get('max_tokens', 500)
                }
            )
            
            for chunk in stream:
                if first_token_time is None and chunk.get('response'):
                    first_token_time = time.time()
                    logger.log("first_token", {
                        "task_id": task_id,
                        "run": run + 1,
                        "ttft_ms": (first_token_time - t_start) * 1000
                    })
                
                response_text += chunk.get('response', '')
            
            t_end = time.time()
            
            # 记录结束
            logger.log("task_end", {
                "task_id": task_id,
                "run": run + 1,
                "latency_s": t_end - t_start
            })
            
            # 计算指标
            n_tokens = len(response_text.split())  # 简化，实际应用 tokenizer
            latency = t_end - t_start
            ttft = (first_token_time - t_start) if first_token_time else 0
            tpot = (t_end - first_token_time) / (n_tokens - 1) if n_tokens > 1 and first_token_time else 0
            
            # 保存结果
            result = {
                "task_id": task_id,
                "task_type": task_type,
                "run": run + 1,
                "model": model_name,
                "prompt": prompt,
                "response": response_text,
                "n_tokens": n_tokens,
                "latency_s": latency,
                "ttft_s": ttft,
                "tpot_s": tpot,
                "temperature": temperature,
                "timestamp": t_start
            }
            
            results.append(result)
            
            print(f"  Run {run+1}/{repeat}: {n_tokens} tokens, {latency:.2f}s, TTFT={ttft*1000:.0f}ms")
            
        except Exception as e:
            print(f"  错误: {e}")
            logger.log("task_error", {
                "task_id": task_id,
                "run": run + 1,
                "error": str(e)
            })
        
        # 任务间冷却（30 秒）
        if task_idx < len(test_cases['tasks']) or run < repeat - 1:
            print("  冷却 30 秒...")
            time.sleep(30)

# 停止监控
monitor.stop()
logger.log("monitoring_stop")
logger.log("experiment_end")

print("\n实验完成！")
```

#### 步骤 6：停止监控并保存数据

```python
# 保存监控数据
monitor_data = monitor.to_dict()
with open(f"logs/experiments_N/{experiment_id}_monitor.json", 'w') as f:
    json.dump(monitor_data, f, indent=2)

# 保存事件日志
logger.save()

# 保存任务结果
with open(f"data/experiments_N/raw/{model_name}/{experiment_id}_results.json", 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# 保存文本输出
for result in results:
    text_file = f"data/experiments_N/texts/{model_name}/{result['task_id']}_r{result['run']}.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(result['response'])

print(f"数据已保存到: data/experiments_N/raw/{model_name}/")
```

#### 步骤 7：冷却与数据转存

```python
print("等待系统完全冷却（5 分钟）...")
time.sleep(300)

# 生成摘要报告
summary = monitor.summary()
print("\n=== 实验摘要 ===")
print(f"模型: {model_name}")
print(f"任务数: {len(results)}")
print(f"总时间: {sum(r['latency_s'] for r in results):.2f} s")
print(f"平均 GPU 功耗: {summary['gpu_power_avg_w']:.2f} W")
print(f"总 GPU 能耗: {summary['gpu_energy_j']:.2f} J")
print(f"峰值 GPU 温度: {summary['gpu_temp_peak_c']:.1f} °C")
```

#### 步骤 8：重复实验（可选）

**建议**：每个模型至少运行 3 次（不同日期），评估复现性

```python
# 记录实验元数据
metadata = {
    "experiment_id": experiment_id,
    "model": model_name,
    "date": time.strftime("%Y-%m-%d"),
    "time": time.strftime("%H:%M:%S"),
    "n_tasks": len(results),
    "total_time_s": sum(r['latency_s'] for r in results),
    "summary": summary
}

with open(f"logs/experiments_N/{experiment_id}_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)

print("\n实验完成！请在不同日期重复 2 次以评估复现性。")
```

### 7.3 批量实验自动化脚本

**完整的自动化脚本示例**：

```python
#!/usr/bin/env python3
"""
批量实验自动化脚本
运行多个模型的完整评估实验
"""

import os
import time
import json
from experiments.monitor import ResourceMonitor
import ollama

# 配置
MODELS = [
    "qwen3:4b",
    "qwen3:8b",
    "deepseek-r1:8b",
    "gemma3:4b"
]

EXPERIMENT_DIR = "data/experiments_5"
TEST_CASES_FILE = f"{EXPERIMENT_DIR}/test_cases.json"

def measure_idle_power(duration=300):
    """测量空闲功耗"""
    print(f"测量空闲功耗 ({duration}s)...")
    monitor = ResourceMonitor(interval=0.2)
    monitor.start()
    time.sleep(duration)
    monitor.stop()
    
    summary = monitor.summary()
    p_idle = summary['gpu_power_avg_w']
    
    print(f"空闲功耗: {p_idle:.2f} W")
    return p_idle, summary

def warmup_model(model_name, n_runs=3):
    """预热模型"""
    print(f"预热模型: {model_name}")
    prompts = ["你好", "1+1=?", "介绍Python"]
    
    for i, prompt in enumerate(prompts[:n_runs], 1):
        print(f"  预热 {i}/{n_runs}...")
        ollama.generate(model=model_name, prompt=prompt)
    
    print("预热完成")

def wait_for_cooldown(target_power, tolerance=0.05, max_wait=120):
    """等待系统冷却"""
    print("等待系统冷却...")
    monitor = ResourceMonitor(interval=1.0)
    monitor.start()
    
    start_time = time.time()
    cooled = False
    
    while not cooled and (time.time() - start_time) < max_wait:
        time.sleep(10)
        
        if len(monitor.gpu_power_w) > 5:
            recent_power = sum(monitor.gpu_power_w[-5:]) / 5
            if abs(recent_power - target_power) < target_power * tolerance:
                cooled = True
                print(f"系统已冷却: {recent_power:.2f} W")
    
    monitor.stop()
    return cooled

def run_experiment(model_name, test_cases, p_idle):
    """运行单个模型的完整实验"""
    experiment_id = f"{model_name}_{int(time.time())}"
    print(f"\n{'='*60}")
    print(f"开始实验: {experiment_id}")
    print(f"{'='*60}\n")
    
    # 初始化
    monitor = ResourceMonitor(interval=0.2)
    results = []
    
    # 启动监控
    monitor.start()
    
    # 执行任务
    for task_idx, task in enumerate(test_cases['tasks'], 1):
        task_id = task['id']
        print(f"[{task_idx}/{len(test_cases['tasks'])}] {task_id}")
        
        for run in range(task.get('repeat', 1)):
            try:
                t_start = time.time()
                
                response = ollama.generate(
                    model=model_name,
                    prompt=task['question'],
                    options={
                        'temperature': task.get('temperature', 0.0),
                        'num_predict': task.get('max_tokens', 500)
                    }
                )
                
                t_end = time.time()
                
                result = {
                    "task_id": task_id,
                    "run": run + 1,
                    "response": response['response'],
                    "latency_s": t_end - t_start,
                    "n_tokens": len(response['response'].split())
                }
                
                results.append(result)
                print(f"  Run {run+1}: {result['latency_s']:.2f}s")
                
            except Exception as e:
                print(f"  错误: {e}")
            
            time.sleep(30)  # 冷却
    
    # 停止监控
    monitor.stop()
    
    # 保存数据
    os.makedirs(f"{EXPERIMENT_DIR}/raw/{model_name}", exist_ok=True)
    
    with open(f"{EXPERIMENT_DIR}/raw/{model_name}/{experiment_id}.json", 'w', encoding='utf-8') as f:
        json.dump({
            "experiment_id": experiment_id,
            "model": model_name,
            "results": results,
            "monitor": monitor.to_dict()
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n实验完成: {experiment_id}")
    return experiment_id

def main():
    """主函数"""
    print("=" * 60)
    print("批量实验自动化脚本")
    print("=" * 60)
    
    # 加载测试用例
    with open(TEST_CASES_FILE, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)
    
    print(f"测试用例数: {len(test_cases['tasks'])}")
    
    # 测量空闲功耗
    p_idle, _ = measure_idle_power(duration=300)
    
    # 遍历模型
    for model_idx, model_name in enumerate(MODELS, 1):
        print(f"\n{'#'*60}")
        print(f"模型 {model_idx}/{len(MODELS)}: {model_name}")
        print(f"{'#'*60}")
        
        # 预热
        warmup_model(model_name)
        
        # 冷却
        wait_for_cooldown(p_idle)
        
        # 运行实验
        run_experiment(model_name, test_cases, p_idle)
        
        # 模型间冷却
        if model_idx < len(MODELS):
            print("\n模型间冷却 10 分钟...")
            time.sleep(600)
    
    print("\n" + "=" * 60)
    print("所有实验完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

**运行方式**：

```bash
# 激活环境
conda activate bartscore

# 设置 UTF-8 编码
set PYTHONUTF8=1

# 运行批量实验
python scripts/run_batch_experiments.py
```

### 7.4 实验质量控制

#### 7.4.1 数据质量检查

```python
def validate_experiment_data(experiment_dir):
    """验证实验数据完整性"""
    issues = []
    
    # 检查文件存在性
    required_files = [
        'test_cases.json',
        'raw/',
        'texts/',
        'summary/'
    ]
    
    for file in required_files:
        path = os.path.join(experiment_dir, file)
        if not os.path.exists(path):
            issues.append(f"缺失: {file}")
    
    # 检查监控数据
    for model_dir in os.listdir(f"{experiment_dir}/raw"):
        for result_file in os.listdir(f"{experiment_dir}/raw/{model_dir}"):
            with open(f"{experiment_dir}/raw/{model_dir}/{result_file}") as f:
                data = json.load(f)
                
                # 检查监控数据完整性
                if 'monitor' in data:
                    monitor = data['monitor']
                    if not monitor.get('gpu_power_w'):
                        issues.append(f"GPU 功耗数据缺失: {result_file}")
                    
                    if len(monitor.get('timestamps', [])) < 10:
                        issues.append(f"采样点不足: {result_file}")
    
    return issues

# 使用示例
issues = validate_experiment_data("data/experiments_5")
if issues:
    print("数据质量问题:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("数据质量检查通过")
```

#### 7.4.2 异常值检测

```python
import numpy as np

def detect_outliers(values, method='iqr', threshold=1.5):
    """检测异常值"""
    values = np.array(values)
    
    if method == 'iqr':
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        iqr = q3 - q1
        lower = q1 - threshold * iqr
        upper = q3 + threshold * iqr
        outliers = (values < lower) | (values > upper)
    
    elif method == 'zscore':
        mean = np.mean(values)
        std = np.std(values)
        z_scores = np.abs((values - mean) / std)
        outliers = z_scores > threshold
    
    return outliers

# 使用示例
latencies = [2.1, 2.3, 2.2, 15.0, 2.4, 2.1]  # 15.0 是异常值
outliers = detect_outliers(latencies, method='iqr')
print(f"异常值索引: {np.where(outliers)[0]}")
```



## 8. 数据分析与可视化

### 8.1 数据预处理与汇总

#### 8.1.1 原始数据加载

```python
import pandas as pd
import json
import os
from pathlib import Path

def load_experiment_results(experiment_dir):
    """
    加载实验结果数据
    
    Args:
        experiment_dir: 实验目录路径
    
    Returns:
        DataFrame: 包含所有实验结果的数据框
    """
    all_results = []
    
    raw_dir = Path(experiment_dir) / 'raw'
    
    for model_dir in raw_dir.iterdir():
        if not model_dir.is_dir():
            continue
        
        model_name = model_dir.name
        
        for result_file in model_dir.glob('*.json'):
            with open(result_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取结果
            for result in data.get('results', []):
                result['model'] = model_name
                result['experiment_id'] = data.get('experiment_id')
                
                # 提取监控数据摘要
                if 'monitor' in data:
                    monitor = data['monitor']
                    summary = monitor.get('summary', {})
                    
                    result['gpu_power_avg_w'] = summary.get('gpu_power_avg_w', 0)
                    result['gpu_energy_j'] = summary.get('gpu_energy_j', 0)
                    result['gpu_util_avg'] = summary.get('gpu_util_avg', 0)
                    result['gpu_mem_peak_mb'] = summary.get('gpu_mem_peak_mb', 0)
                    result['cpu_energy_j_approx'] = summary.get('cpu_energy_j_approx', 0)
                
                all_results.append(result)
    
    df = pd.DataFrame(all_results)
    return df

# 使用示例
df = load_experiment_results('data/experiments_5')
print(f"加载 {len(df)} 条结果")
print(df.head())
```

#### 8.1.2 数据清洗与验证

```python
def clean_experiment_data(df):
    """
    清洗实验数据
    
    Args:
        df: 原始数据框
    
    Returns:
        DataFrame: 清洗后的数据框
    """
    df_clean = df.copy()
    
    # 1. 删除缺失关键字段的行
    required_cols = ['task_id', 'model', 'latency_s', 'n_tokens']
    df_clean = df_clean.dropna(subset=required_cols)
    
    # 2. 删除异常值
    # 延迟异常（> 60s 或 < 0.1s）
    df_clean = df_clean[(df_clean['latency_s'] > 0.1) & (df_clean['latency_s'] < 60)]
    
    # token 数异常（< 5 或 > 2000）
    df_clean = df_clean[(df_clean['n_tokens'] > 5) & (df_clean['n_tokens'] < 2000)]
    
    # 3. 计算派生指标
    df_clean['throughput_tps'] = df_clean['n_tokens'] / df_clean['latency_s']
    df_clean['e_token_j'] = df_clean['gpu_energy_j'] / df_clean['n_tokens']
    
    # 4. 提取任务类型
    df_clean['task_type'] = df_clean['task_id'].str.split('_').str[0]
    
    print(f"清洗前: {len(df)} 条")
    print(f"清洗后: {len(df_clean)} 条")
    print(f"删除: {len(df) - len(df_clean)} 条")
    
    return df_clean

# 使用示例
df_clean = clean_experiment_data(df)
```



#### 8.1.3 汇总统计

```python
def generate_summary_statistics(df):
    """
    生成汇总统计
    
    Args:
        df: 清洗后的数据框
    
    Returns:
        DataFrame: 汇总统计表
    """
    # 按模型和任务类型分组
    summary = df.groupby(['model', 'task_type']).agg({
        'latency_s': ['mean', 'std', 'min', 'max'],
        'throughput_tps': ['mean', 'std'],
        'e_token_j': ['mean', 'std'],
        'gpu_power_avg_w': ['mean'],
        'n_tokens': ['mean', 'count']
    }).round(3)
    
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    
    return summary

# 使用示例
summary_stats = generate_summary_statistics(df_clean)
print(summary_stats)

# 保存到 CSV
summary_stats.to_csv('data/experiments_5/summary/stats.csv', index=False)
```

### 8.2 功耗-时间曲线分析

#### 8.2.1 单次推理功耗曲线

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def plot_power_trace(monitor_data, events, save_path=None):
    """
    绘制功耗-时间曲线
    
    Args:
        monitor_data: 监控数据字典
        events: 事件日志列表
        save_path: 保存路径
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    
    # 时间轴（相对时间）
    timestamps = monitor_data['timestamps']
    t_start = timestamps[0]
    time_rel = [(t - t_start) for t in timestamps]
    
    # 上图：功耗曲线
    ax1.plot(time_rel, monitor_data['gpu_power_w'], 
             label='GPU 功耗', color='#2E86AB', linewidth=1.5)
    ax1.plot(time_rel, monitor_data['cpu_power_w_approx'], 
             label='CPU 功耗（估算）', color='#A23B72', linewidth=1.5, alpha=0.7)
    
    # 标记事件
    for event in events:
        t_event = event['timestamp'] - t_start
        event_name = event['event']
        
        if 'start' in event_name:
            ax1.axvline(t_event, color='green', linestyle='--', alpha=0.6, linewidth=1)
            ax1.text(t_event, ax1.get_ylim()[1] * 0.95, event_name, 
                    rotation=90, va='top', fontsize=8)
        elif 'first_token' in event_name:
            ax1.axvline(t_event, color='orange', linestyle='--', alpha=0.6, linewidth=1)
            ax1.text(t_event, ax1.get_ylim()[1] * 0.95, 'First Token', 
                    rotation=90, va='top', fontsize=8)
        elif 'end' in event_name:
            ax1.axvline(t_event, color='red', linestyle='--', alpha=0.6, linewidth=1)
            ax1.text(t_event, ax1.get_ylim()[1] * 0.95, event_name, 
                    rotation=90, va='top', fontsize=8)
    
    ax1.set_ylabel('功耗 (W)', fontsize=12)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_title('推理过程功耗曲线', fontsize=14, fontweight='bold')
    
    # 下图：GPU 利用率
    ax2.plot(time_rel, monitor_data['gpu_util'], 
             label='GPU 利用率', color='#F18F01', linewidth=1.5)
    ax2.fill_between(time_rel, 0, monitor_data['gpu_util'], 
                      color='#F18F01', alpha=0.3)
    
    ax2.set_xlabel('时间 (s)', fontsize=12)
    ax2.set_ylabel('GPU 利用率 (%)', fontsize=12)
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 100])
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存: {save_path}")
    
    plt.show()

# 使用示例
with open('logs/experiments_5/exp_123_monitor.json') as f:
    monitor_data = json.load(f)

with open('logs/experiments_5/exp_123_events.json') as f:
    events = json.load(f)

plot_power_trace(monitor_data, events, 
                 save_path='results/experiments_5/figures/power_trace.png')
```



### 8.3 核心对比图表

#### 8.3.1 吞吐量 vs 延迟散点图

```python
import seaborn as sns

def plot_throughput_vs_latency(df, save_path=None):
    """
    绘制吞吐量 vs 延迟散点图
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # 按模型分组绘制
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        ax.scatter(model_data['latency_s'], 
                  model_data['throughput_tps'],
                  label=model, s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('延迟 (s) - 越小越好', fontsize=12)
    ax.set_ylabel('吞吐量 (tokens/s) - 越大越好', fontsize=12)
    ax.set_title('吞吐量 vs 延迟对比', fontsize=14, fontweight='bold')
    ax.legend(title='模型', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 添加理想区域标注（左上角）
    ax.axvspan(ax.get_xlim()[0], ax.get_xlim()[0] + (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.3, 
               alpha=0.1, color='green', label='理想区域')
    ax.axhspan(ax.get_ylim()[1] * 0.7, ax.get_ylim()[1], 
               alpha=0.1, color='green')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# 使用示例
plot_throughput_vs_latency(df_clean, 
                           save_path='results/experiments_5/figures/throughput_vs_latency.png')
```

#### 8.3.2 能耗 vs 质量散点图

```python
def plot_energy_vs_quality(df, quality_col='quality_score', save_path=None):
    """
    绘制能耗 vs 质量散点图
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # 按任务类型分组
    for task_type in df['task_type'].unique():
        task_data = df[df['task_type'] == task_type]
        
        ax.scatter(task_data['e_token_j'], 
                  task_data[quality_col],
                  label=task_type, s=100, alpha=0.6, edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('每 Token 能耗 (J/token) - 越小越好', fontsize=12)
    ax.set_ylabel('质量得分 - 越大越好', fontsize=12)
    ax.set_title('能耗 vs 质量对比', fontsize=14, fontweight='bold')
    ax.legend(title='任务类型', fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # 添加帕累托前沿线（简化）
    # 找到每个能耗水平的最高质量
    df_sorted = df.sort_values('e_token_j')
    pareto_points = []
    max_quality = 0
    
    for _, row in df_sorted.iterrows():
        if row[quality_col] > max_quality:
            max_quality = row[quality_col]
            pareto_points.append((row['e_token_j'], row[quality_col]))
    
    if pareto_points:
        pareto_x, pareto_y = zip(*pareto_points)
        ax.plot(pareto_x, pareto_y, 'r--', linewidth=2, alpha=0.5, label='帕累托前沿')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# 使用示例
plot_energy_vs_quality(df_clean, 
                       save_path='results/experiments_5/figures/energy_vs_quality.png')
```

#### 8.3.3 质效比柱状图

```python
def plot_qe_ratio_bars(df, save_path=None):
    """
    绘制质效比柱状图（按任务和模型分组）
    """
    # 计算平均质效比
    qe_summary = df.groupby(['model', 'task_type'])['qe_ratio'].mean().reset_index()
    
    # 透视表
    qe_pivot = qe_summary.pivot(index='task_type', columns='model', values='qe_ratio')
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    qe_pivot.plot(kind='bar', ax=ax, width=0.8, edgecolor='black', linewidth=0.5)
    
    ax.set_xlabel('任务类型', fontsize=12)
    ax.set_ylabel('质效比 (QE Ratio)', fontsize=12)
    ax.set_title('质效比对比（按任务类型）', fontsize=14, fontweight='bold')
    ax.legend(title='模型', fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    
    # 旋转 x 轴标签
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# 使用示例
plot_qe_ratio_bars(df_clean, 
                   save_path='results/experiments_5/figures/qe_ratio_bars.png')
```

#### 8.3.4 综合能力雷达图

```python
from math import pi

def plot_radar_chart(df, save_path=None):
    """
    绘制综合能力雷达图
    """
    # 计算各模型的归一化指标
    metrics = ['throughput_tps', 'latency_s', 'e_token_j', 'quality_score']
    metric_labels = ['吞吐量', '延迟优', '能耗优', '质量']
    
    model_scores = {}
    
    for model in df['model'].unique():
        model_data = df[df['model'] == model]
        
        scores = []
        for metric in metrics:
            values = model_data[metric].values
            
            # 归一化（延迟和能耗需要反转）
            if metric in ['latency_s', 'e_token_j']:
                # 越小越好，反转归一化
                norm_value = 1 - (values.mean() - df[metric].min()) / (df[metric].max() - df[metric].min() + 1e-9)
            else:
                # 越大越好
                norm_value = (values.mean() - df[metric].min()) / (df[metric].max() - df[metric].min() + 1e-9)
            
            scores.append(norm_value)
        
        model_scores[model] = scores
    
    # 绘制雷达图
    angles = [n / len(metric_labels) * 2 * pi for n in range(len(metric_labels))]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    for model, scores in model_scores.items():
        scores += scores[:1]  # 闭合
        ax.plot(angles, scores, 'o-', linewidth=2, label=model)
        ax.fill(angles, scores, alpha=0.15)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels, fontsize=12)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=10)
    ax.grid(True)
    
    ax.set_title('综合能力雷达图', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# 使用示例
plot_radar_chart(df_clean, 
                 save_path='results/experiments_5/figures/radar_chart.png')
```



### 8.4 高级分析图表

#### 8.4.1 热力图（模型 × 任务性能）

```python
def plot_performance_heatmap(df, metric='qe_ratio', save_path=None):
    """
    绘制性能热力图
    """
    # 计算平均指标
    heatmap_data = df.groupby(['model', 'task_type'])[metric].mean().reset_index()
    heatmap_pivot = heatmap_data.pivot(index='model', columns='task_type', values=metric)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(heatmap_pivot, annot=True, fmt='.3f', cmap='YlGnBu', 
                linewidths=0.5, cbar_kws={'label': metric}, ax=ax)
    
    ax.set_xlabel('任务类型', fontsize=12)
    ax.set_ylabel('模型', fontsize=12)
    ax.set_title(f'{metric} 热力图', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# 使用示例
plot_performance_heatmap(df_clean, metric='qe_ratio',
                         save_path='results/experiments_5/figures/heatmap_qe_ratio.png')
```

#### 8.4.2 箱线图（稳定性分析）

```python
def plot_stability_boxplot(df, metric='latency_s', save_path=None):
    """
    绘制稳定性箱线图
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 按模型分组
    df_sorted = df.sort_values('model')
    
    sns.boxplot(data=df_sorted, x='model', y=metric, hue='task_type', ax=ax)
    
    ax.set_xlabel('模型', fontsize=12)
    ax.set_ylabel(metric, fontsize=12)
    ax.set_title(f'{metric} 稳定性分析（箱线图）', fontsize=14, fontweight='bold')
    ax.legend(title='任务类型', fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# 使用示例
plot_stability_boxplot(df_clean, metric='latency_s',
                       save_path='results/experiments_5/figures/boxplot_latency.png')
```

#### 8.4.3 相关性矩阵

```python
def plot_correlation_matrix(df, save_path=None):
    """
    绘制指标相关性矩阵
    """
    # 选择数值列
    numeric_cols = ['latency_s', 'throughput_tps', 'e_token_j', 
                    'gpu_power_avg_w', 'quality_score', 'qe_ratio']
    
    corr_matrix = df[numeric_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                center=0, linewidths=0.5, cbar_kws={'label': '相关系数'}, ax=ax)
    
    ax.set_title('指标相关性矩阵', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
    
    plt.show()

# 使用示例
plot_correlation_matrix(df_clean,
                        save_path='results/experiments_5/figures/correlation_matrix.png')
```

### 8.5 自动化报告生成

#### 8.5.1 Markdown 报告模板

```python
def generate_markdown_report(df, summary_stats, output_path):
    """
    生成自动化 Markdown 报告
    
    Args:
        df: 完整数据框
        summary_stats: 汇总统计
        output_path: 输出路径
    """
    report = []
    
    # 标题
    report.append("# 实验结果分析报告\n")
    report.append(f"**生成时间**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report.append("---\n")
    
    # 1. 实验概览
    report.append("## 1. 实验概览\n")
    report.append(f"- **模型数量**: {df['model'].nunique()}\n")
    report.append(f"- **任务类型**: {df['task_type'].nunique()}\n")
    report.append(f"- **总测试数**: {len(df)}\n")
    report.append(f"- **测试模型**: {', '.join(df['model'].unique())}\n")
    report.append("\n")
    
    # 2. 关键指标汇总
    report.append("## 2. 关键指标汇总\n")
    report.append("### 2.1 按模型汇总\n")
    
    model_summary = df.groupby('model').agg({
        'latency_s': 'mean',
        'throughput_tps': 'mean',
        'e_token_j': 'mean',
        'qe_ratio': 'mean'
    }).round(3)
    
    report.append(model_summary.to_markdown())
    report.append("\n")
    
    # 3. 性能排名
    report.append("## 3. 性能排名\n")
    
    # 质效比排名
    report.append("### 3.1 质效比排名（Top 5）\n")
    top_qe = df.nlargest(5, 'qe_ratio')[['model', 'task_type', 'qe_ratio']]
    report.append(top_qe.to_markdown(index=False))
    report.append("\n")
    
    # 能效排名
    report.append("### 3.2 能效排名（Top 5，能耗最低）\n")
    top_energy = df.nsmallest(5, 'e_token_j')[['model', 'task_type', 'e_token_j']]
    report.append(top_energy.to_markdown(index=False))
    report.append("\n")
    
    # 4. 可视化图表
    report.append("## 4. 可视化图表\n")
    report.append("### 4.1 吞吐量 vs 延迟\n")
    report.append("![吞吐量 vs 延迟](figures/throughput_vs_latency.png)\n")
    report.append("\n")
    
    report.append("### 4.2 能耗 vs 质量\n")
    report.append("![能耗 vs 质量](figures/energy_vs_quality.png)\n")
    report.append("\n")
    
    report.append("### 4.3 质效比对比\n")
    report.append("![质效比对比](figures/qe_ratio_bars.png)\n")
    report.append("\n")
    
    report.append("### 4.4 综合能力雷达图\n")
    report.append("![综合能力雷达图](figures/radar_chart.png)\n")
    report.append("\n")
    
    # 5. 结论与建议
    report.append("## 5. 结论与建议\n")
    
    # 找出最佳模型
    best_qe_model = df.groupby('model')['qe_ratio'].mean().idxmax()
    best_energy_model = df.groupby('model')['e_token_j'].mean().idxmin()
    best_speed_model = df.groupby('model')['throughput_tps'].mean().idxmax()
    
    report.append(f"- **最佳质效比模型**: {best_qe_model}\n")
    report.append(f"- **最佳能效模型**: {best_energy_model}\n")
    report.append(f"- **最快速度模型**: {best_speed_model}\n")
    report.append("\n")
    
    report.append("### 5.1 应用场景推荐\n")
    report.append(f"- **能耗敏感场景**（边缘设备）: 推荐 {best_energy_model}\n")
    report.append(f"- **吞吐优先场景**（批处理）: 推荐 {best_speed_model}\n")
    report.append(f"- **综合平衡场景**: 推荐 {best_qe_model}\n")
    report.append("\n")
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    print(f"报告已生成: {output_path}")

# 使用示例
generate_markdown_report(df_clean, summary_stats, 
                         'results/experiments_5/report.md')
```

### 8.6 完整分析管线

```python
def complete_analysis_pipeline(experiment_dir):
    """
    完整的数据分析管线
    
    Args:
        experiment_dir: 实验目录路径
    """
    print("=" * 60)
    print("开始数据分析管线")
    print("=" * 60)
    
    # 1. 加载数据
    print("\n[1/7] 加载实验数据...")
    df = load_experiment_results(experiment_dir)
    print(f"  加载 {len(df)} 条结果")
    
    # 2. 数据清洗
    print("\n[2/7] 数据清洗...")
    df_clean = clean_experiment_data(df)
    
    # 3. 生成汇总统计
    print("\n[3/7] 生成汇总统计...")
    summary_stats = generate_summary_statistics(df_clean)
    summary_stats.to_csv(f'{experiment_dir}/summary/stats.csv', index=False)
    print(f"  汇总统计已保存")
    
    # 4. 计算评估指标
    print("\n[4/7] 计算评估指标...")
    from section_6_metrics import complete_evaluation_pipeline
    df_eval = complete_evaluation_pipeline(df_clean)
    df_eval.to_csv(f'{experiment_dir}/summary/results.csv', index=False)
    print(f"  评估结果已保存")
    
    # 5. 生成可视化图表
    print("\n[5/7] 生成可视化图表...")
    figures_dir = f'{experiment_dir}/figures'
    os.makedirs(figures_dir, exist_ok=True)
    
    plot_throughput_vs_latency(df_eval, f'{figures_dir}/throughput_vs_latency.png')
    plot_energy_vs_quality(df_eval, f'{figures_dir}/energy_vs_quality.png')
    plot_qe_ratio_bars(df_eval, f'{figures_dir}/qe_ratio_bars.png')
    plot_radar_chart(df_eval, f'{figures_dir}/radar_chart.png')
    plot_performance_heatmap(df_eval, f'{figures_dir}/heatmap_qe_ratio.png')
    plot_stability_boxplot(df_eval, f'{figures_dir}/boxplot_latency.png')
    plot_correlation_matrix(df_eval, f'{figures_dir}/correlation_matrix.png')
    
    print(f"  生成 7 张图表")
    
    # 6. 生成报告
    print("\n[6/7] 生成分析报告...")
    generate_markdown_report(df_eval, summary_stats, f'{experiment_dir}/report.md')
    
    # 7. 数据质量检查
    print("\n[7/7] 数据质量检查...")
    issues = validate_experiment_data(experiment_dir)
    if issues:
        print("  发现问题:")
        for issue in issues:
            print(f"    - {issue}")
    else:
        print("  数据质量检查通过")
    
    print("\n" + "=" * 60)
    print("分析管线完成！")
    print("=" * 60)
    print(f"\n结果位置:")
    print(f"  - 汇总统计: {experiment_dir}/summary/stats.csv")
    print(f"  - 评估结果: {experiment_dir}/summary/results.csv")
    print(f"  - 可视化图表: {experiment_dir}/figures/")
    print(f"  - 分析报告: {experiment_dir}/report.md")

# 使用示例
complete_analysis_pipeline('data/experiments_5')
```

### 8.7 使用说明

**运行完整分析**：

```bash
# 激活环境
conda activate bartscore

# 设置编码
set PYTHONUTF8=1

# 运行分析脚本
python scripts/analyze_experiments.py --experiment-dir data/experiments_5
```

**输出文件结构**：

```
data/experiments_5/
├── summary/
│   ├── stats.csv          # 汇总统计
│   └── results.csv        # 完整评估结果
├── figures/
│   ├── throughput_vs_latency.png
│   ├── energy_vs_quality.png
│   ├── qe_ratio_bars.png
│   ├── radar_chart.png
│   ├── heatmap_qe_ratio.png
│   ├── boxplot_latency.png
│   └── correlation_matrix.png
└── report.md              # 自动化分析报告
```

**自定义分析**：

```python
# 加载数据
df = pd.read_csv('data/experiments_5/summary/results.csv')

# 自定义筛选
df_qwen = df[df['model'].str.contains('qwen')]

# 自定义可视化
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_qwen, x='e_token_j', y='quality_score', hue='task_type')
plt.title('Qwen 模型能耗 vs 质量')
plt.show()
```


## 9. 实验注意事项

### 9.1 硬件环境控制

#### 9.1.1 Windows 电源管理

**关键设置**：

1. **电源模式设置**：
   - 打开"控制面板" → "电源选项"
   - 选择"高性能"模式
   - 点击"更改计划设置" → "更改高级电源设置"
   - 关键配置：
     - 处理器电源管理 → 最小处理器状态：100%
     - 处理器电源管理 → 最大处理器状态：100%
     - 处理器电源管理 → 系统散热方式：主动
     - PCI Express → 链接状态电源管理：关闭
     - USB 设置 → USB 选择性暂停设置：已禁用

2. **禁用睿频（可选）**：
   - 在 BIOS 中禁用 Intel Turbo Boost
   - 或通过 ThrottleStop 工具固定 CPU 频率
   - 注意：笔记本可能无法完全禁用睿频

3. **GPU 性能模式**：
   - NVIDIA 控制面板 → 管理 3D 设置
   - 电源管理模式：最高性能优先
   - 关闭 NVIDIA Whisper Mode（如有）

**验证命令**：

```powershell
# 检查当前电源方案
powercfg /getactivescheme

# 查看 GPU 状态
nvidia-smi

# 查看 CPU 频率
Get-WmiObject Win32_Processor | Select-Object Name, CurrentClockSpeed, MaxClockSpeed
```

#### 9.1.2 环境温度与散热

**笔记本特殊考虑**：

1. **散热优化**：
   - 使用散热底座或支架，确保底部通风
   - 清理散热孔灰尘
   - 环境温度保持在 20-25°C
   - 避免阳光直射

2. **温度监控**：
   - 实验前检查 GPU 温度 < 50°C
   - 实验中监控温度不超过 85°C
   - 如温度过高，延长冷却时间

3. **热节流预防**：
   - 避免连续长时间运行
   - 任务间冷却至少 30 秒
   - 模型间冷却至少 5 分钟

**温度检查脚本**：

```python
import pynvml

pynvml.nvmlInit()
handle = pynvml.nvmlDeviceGetHandleByIndex(0)

temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
print(f"当前 GPU 温度: {temp}°C")

if temp > 50:
    print("警告：GPU 温度过高，建议等待冷却")
elif temp > 85:
    print("严重警告：GPU 温度过高，立即停止实验")
else:
    print("温度正常，可以开始实验")

pynvml.nvmlShutdown()
```


### 9.2 软件环境控制

#### 9.2.1 后台进程管理

**实验前清理**：

```powershell
# 关闭常见后台应用
Stop-Process -Name "chrome", "firefox", "msedge", "Teams", "Slack", "Discord" -ErrorAction SilentlyContinue

# 检查 CPU 占用高的进程
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet

# 检查内存占用
Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 Name, @{Name="Memory(MB)";Expression={[math]::Round($_.WorkingSet / 1MB, 2)}}
```

**必须保留的进程**：
- `ollama` 或 `ollama_llama_server`（Ollama 服务）
- `python`（实验脚本）
- `explorer`（Windows 资源管理器）
- 系统关键进程

**可选：创建清理脚本**：

```powershell
# cleanup_for_experiment.ps1
Write-Host "清理实验环境..."

# 关闭浏览器
$browsers = @("chrome", "firefox", "msedge", "brave", "opera")
foreach ($browser in $browsers) {
    Stop-Process -Name $browser -ErrorAction SilentlyContinue
}

# 关闭通讯软件
$comms = @("Teams", "Slack", "Discord", "WeChat", "QQ")
foreach ($comm in $comms) {
    Stop-Process -Name $comm -ErrorAction SilentlyContinue
}

# 清理 GPU 缓存
python -c "import torch; torch.cuda.empty_cache()" 2>$null

Write-Host "清理完成！"
Write-Host "当前 CPU 占用前 5："
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 Name, CPU
```

#### 9.2.2 Ollama 服务管理

**服务状态检查**：

```bash
# 检查 Ollama 服务
ollama list

# 测试 API 连接
curl http://localhost:11434/api/tags

# 重启 Ollama 服务（如需要）
# Windows: 在任务管理器中结束 ollama 进程，然后重新启动
```

**服务优化**：

```bash
# 设置环境变量（在实验脚本中）
set OLLAMA_NUM_PARALLEL=1
set OLLAMA_MAX_LOADED_MODELS=1
set OLLAMA_FLASH_ATTENTION=1
```

#### 9.2.3 Python 环境隔离

**确保环境纯净**：

```bash
# 激活专用环境
conda activate bartscore

# 验证关键包版本
python -c "import pynvml; print(f'pynvml: {pynvml.__version__}')"
python -c "import psutil; print(f'psutil: {psutil.__version__}')"
python -c "import pandas; print(f'pandas: {pandas.__version__}')"

# 检查 CUDA 可用性
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```


### 9.3 数据同步与时间戳对齐

#### 9.3.1 时间戳系统

**统一时间源**：

所有组件使用 `time.time()` 获取 UNIX 时间戳，确保：
- 监控数据（`ResourceMonitor`）
- 事件日志（`EventLogger`）
- 任务结果（实验脚本）

使用相同的系统时钟。

**时间同步验证**：

```python
import time
import json

# 记录事件
event_time = time.time()
print(f"事件时间戳: {event_time}")

# 验证监控数据时间戳
monitor_time = monitor.timestamps[-1] if monitor.timestamps else 0
print(f"监控时间戳: {monitor_time}")

# 时间差应小于 1 秒
time_diff = abs(event_time - monitor_time)
if time_diff > 1.0:
    print(f"警告：时间戳不同步，差异 {time_diff:.3f} 秒")
```

#### 9.3.2 数据完整性检查

**实验后验证**：

```python
def validate_experiment_data(experiment_id):
    """验证实验数据完整性"""
    issues = []
    
    # 1. 检查文件存在
    required_files = [
        f"logs/experiments_N/{experiment_id}_monitor.json",
        f"logs/experiments_N/{experiment_id}_events.json",
        f"data/experiments_N/raw/{model_name}/{experiment_id}_results.json"
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            issues.append(f"缺失文件: {file}")
    
    # 2. 检查监控数据
    with open(f"logs/experiments_N/{experiment_id}_monitor.json") as f:
        monitor_data = json.load(f)
    
    if len(monitor_data['timestamps']) < 10:
        issues.append("监控采样点不足")
    
    if not monitor_data.get('gpu_power_w'):
        issues.append("GPU 功耗数据缺失")
    
    # 3. 检查事件日志
    with open(f"logs/experiments_N/{experiment_id}_events.json") as f:
        events = json.load(f)
    
    required_events = ['experiment_start', 'monitoring_start', 'experiment_end']
    for event_name in required_events:
        if not any(e['event'] == event_name for e in events):
            issues.append(f"缺失事件: {event_name}")
    
    # 4. 检查时间戳对齐
    t_start = next(e['timestamp'] for e in events if e['event'] == 'experiment_start')
    t_monitor_start = monitor_data['timestamps'][0]
    
    if abs(t_start - t_monitor_start) > 5.0:
        issues.append(f"时间戳不对齐: 差异 {abs(t_start - t_monitor_start):.2f} 秒")
    
    return issues

# 使用示例
issues = validate_experiment_data(experiment_id)
if issues:
    print("数据完整性问题:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("数据完整性检查通过")
```


### 9.4 异常处理与质量控制

#### 9.4.1 功耗异常检测

**3σ 原则**：

```python
import numpy as np

def detect_power_anomalies(monitor_data, threshold=3):
    """检测功耗异常值"""
    gpu_power = np.array(monitor_data['gpu_power_w'])
    
    mean_power = np.mean(gpu_power)
    std_power = np.std(gpu_power)
    
    # 3σ 阈值
    lower_bound = mean_power - threshold * std_power
    upper_bound = mean_power + threshold * std_power
    
    anomalies = (gpu_power < lower_bound) | (gpu_power > upper_bound)
    anomaly_ratio = np.sum(anomalies) / len(gpu_power)
    
    print(f"平均功耗: {mean_power:.2f} W")
    print(f"标准差: {std_power:.2f} W")
    print(f"异常点比例: {anomaly_ratio*100:.2f}%")
    
    if anomaly_ratio > 0.05:  # 超过 5% 异常
        print("警告：功耗波动异常，建议重新运行实验")
        return True
    
    return False

# 使用示例
with open(f"logs/experiments_N/{experiment_id}_monitor.json") as f:
    monitor_data = json.load(f)

is_anomalous = detect_power_anomalies(monitor_data)
```

#### 9.4.2 实验重跑策略

**重跑条件**：

1. **功耗异常**：异常点比例 > 5%
2. **温度过高**：峰值温度 > 90°C
3. **数据缺失**：关键字段缺失或采样点不足
4. **时间戳错误**：时间戳不对齐 > 5 秒
5. **推理失败**：模型返回错误或空响应

**重跑脚本**：

```python
def should_rerun_experiment(experiment_id, model_name):
    """判断是否需要重跑实验"""
    reasons = []
    
    # 加载数据
    with open(f"logs/experiments_N/{experiment_id}_monitor.json") as f:
        monitor_data = json.load(f)
    
    # 检查功耗异常
    if detect_power_anomalies(monitor_data):
        reasons.append("功耗波动异常")
    
    # 检查温度
    summary = monitor_data.get('summary', {})
    if summary.get('gpu_temp_peak_c', 0) > 90:
        reasons.append(f"温度过高: {summary['gpu_temp_peak_c']:.1f}°C")
    
    # 检查数据完整性
    issues = validate_experiment_data(experiment_id)
    if issues:
        reasons.extend(issues)
    
    if reasons:
        print(f"\n实验 {experiment_id} 需要重跑:")
        for reason in reasons:
            print(f"  - {reason}")
        return True
    
    print(f"\n实验 {experiment_id} 质量合格")
    return False
```

#### 9.4.3 实验日志记录

**详细日志**：

```python
import logging
from datetime import datetime

# 配置日志
log_file = f"logs/experiments_N/experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 记录实验信息
logger.info(f"开始实验: {experiment_id}")
logger.info(f"模型: {model_name}")
logger.info(f"GPU 温度: {initial_temp}°C")
logger.info(f"空闲功耗: {p_idle:.2f} W")

# 记录异常
try:
    # 实验代码
    pass
except Exception as e:
    logger.error(f"实验失败: {str(e)}", exc_info=True)
    raise

# 记录完成
logger.info(f"实验完成: {experiment_id}")
logger.info(f"总时间: {total_time:.2f} s")
logger.info(f"平均功耗: {avg_power:.2f} W")
```


### 9.5 资源优化与实验规划

#### 9.5.1 分阶段实验策略

**针对 RTX 4060 Laptop 的优化方案**：

由于硬件限制，建议采用**分阶段筛选**策略，而非全因子实验：

**阶段 1：基线实验**（4 个模型 × 1 量化 = 4 组）
- 目标：建立性能基线
- 模型：qwen3:4b, qwen3:8b, deepseek-r1:8b, gemma3:4b
- 量化：Q4_K_M（已下载）
- 任务：全部 8 种任务类型
- 重复：每个任务 3 次

**阶段 2：扩展实验**（可选，2-3 个模型 × 2 量化 = 4-6 组）
- 目标：评估量化影响
- 模型：选择阶段 1 中表现最好的 2-3 个模型
- 量化：Q4_K_M + Q8_0
- 任务：重点任务（如 qa, summary）
- 重复：每个任务 3 次

**阶段 3：深度分析**（可选，1 个模型 × 多配置）
- 目标：细粒度参数调优
- 模型：综合表现最优的 1 个模型
- 配置：不同 temperature, top_p, num_ctx
- 任务：全部任务
- 重复：每个任务 5 次

**时间估算**：

```python
def estimate_experiment_time(n_models, n_tasks, n_repeats, avg_latency_s=5):
    """估算实验总时间"""
    # 任务时间
    task_time = n_models * n_tasks * n_repeats * avg_latency_s
    
    # 冷却时间（任务间 30s，模型间 300s）
    cooldown_time = n_models * n_tasks * n_repeats * 30 + n_models * 300
    
    # 预热和基线测量（每个模型 5 分钟）
    warmup_time = n_models * 300
    
    total_time_s = task_time + cooldown_time + warmup_time
    total_time_h = total_time_s / 3600
    
    print(f"估算实验时间:")
    print(f"  任务执行: {task_time/3600:.2f} 小时")
    print(f"  冷却等待: {cooldown_time/3600:.2f} 小时")
    print(f"  预热基线: {warmup_time/3600:.2f} 小时")
    print(f"  总计: {total_time_h:.2f} 小时 ({total_time_h/24:.2f} 天)")
    
    return total_time_h

# 阶段 1 估算
print("=== 阶段 1：基线实验 ===")
estimate_experiment_time(n_models=4, n_tasks=8, n_repeats=3, avg_latency_s=5)

# 阶段 2 估算
print("\n=== 阶段 2：扩展实验 ===")
estimate_experiment_time(n_models=3, n_tasks=4, n_repeats=3, avg_latency_s=5)
```

#### 9.5.2 磁盘空间管理

**数据存储规划**：

```python
def estimate_storage_requirements(n_experiments, avg_response_tokens=200):
    """估算存储需求"""
    # 每个实验的数据量
    monitor_json = 0.5  # MB（5Hz × 300s × 多字段）
    events_json = 0.01  # MB
    results_json = avg_response_tokens * 4 / 1024 / 1024  # MB（UTF-8 编码）
    texts = avg_response_tokens * 4 / 1024 / 1024  # MB
    
    per_experiment_mb = monitor_json + events_json + results_json + texts
    total_mb = per_experiment_mb * n_experiments
    
    print(f"单次实验数据量: {per_experiment_mb:.2f} MB")
    print(f"总数据量（{n_experiments} 次实验）: {total_mb:.2f} MB ({total_mb/1024:.2f} GB)")
    
    # 加上汇总和图表
    summary_mb = 10  # CSV + 图表
    total_with_summary = total_mb + summary_mb
    
    print(f"包含汇总和图表: {total_with_summary:.2f} MB ({total_with_summary/1024:.2f} GB)")
    
    return total_with_summary

# 估算阶段 1
print("=== 阶段 1 存储需求 ===")
estimate_storage_requirements(n_experiments=4*8*3)  # 96 次实验
```

**清理策略**：

```bash
# 定期清理旧实验数据（保留最近 N 次）
python scripts/cleanup_old_experiments.py --keep 10

# 压缩历史数据
tar -czf experiments_archive_$(date +%Y%m%d).tar.gz data/experiments_*/

# 删除中间文件
rm -rf data/experiments_*/texts/*.txt  # 保留 JSON 即可
```


### 9.6 笔记本特殊注意事项

#### 9.6.1 电池与电源管理

**强制使用交流电源**：

1. **插入电源适配器**：实验期间必须使用交流电
2. **禁用电池优化**：
   - Windows 设置 → 系统 → 电源 → 电池
   - 关闭"电池保护模式"
   - 关闭"智能充电"

3. **验证电源状态**：

```python
import psutil

battery = psutil.sensors_battery()
if battery:
    if not battery.power_plugged:
        print("错误：未连接电源适配器！")
        print("请插入电源后再运行实验")
        exit(1)
    else:
        print(f"电源已连接，电池电量: {battery.percent}%")
else:
    print("无法检测电池状态（可能是台式机）")
```

#### 9.6.2 显卡切换（双显卡笔记本）

**确保使用独立显卡**：

1. **NVIDIA 控制面板设置**：
   - 右键桌面 → NVIDIA 控制面板
   - 管理 3D 设置 → 程序设置
   - 添加 `python.exe` 和 `ollama.exe`
   - 选择"高性能 NVIDIA 处理器"

2. **验证当前 GPU**：

```python
import torch

if torch.cuda.is_available():
    print(f"CUDA 设备: {torch.cuda.get_device_name(0)}")
    print(f"CUDA 版本: {torch.version.cuda}")
else:
    print("警告：CUDA 不可用，可能使用集成显卡")
```

#### 9.6.3 散热与节流监控

**实时监控温度和频率**：

```python
import pynvml
import time

def monitor_thermal_throttling(duration=60):
    """监控热节流"""
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    
    print("监控热节流（60 秒）...")
    throttle_detected = False
    
    for i in range(duration):
        temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
        clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
        
        # 检测降频（假设基础频率 1500 MHz）
        if clock < 1200:
            print(f"[{i}s] 警告：GPU 降频 {clock} MHz，温度 {temp}°C")
            throttle_detected = True
        
        time.sleep(1)
    
    pynvml.nvmlShutdown()
    
    if throttle_detected:
        print("\n检测到热节流，建议：")
        print("  1. 改善散热（使用散热底座）")
        print("  2. 降低环境温度")
        print("  3. 延长任务间冷却时间")
    else:
        print("\n未检测到热节流，散热良好")

# 实验前运行
monitor_thermal_throttling(duration=60)
```

#### 9.6.4 内存管理

**避免内存不足**：

```python
import psutil

def check_memory_availability(required_gb=4):
    """检查可用内存"""
    mem = psutil.virtual_memory()
    available_gb = mem.available / (1024**3)
    
    print(f"总内存: {mem.total / (1024**3):.2f} GB")
    print(f"可用内存: {available_gb:.2f} GB")
    print(f"内存使用率: {mem.percent}%")
    
    if available_gb < required_gb:
        print(f"\n警告：可用内存不足 {required_gb} GB")
        print("建议关闭其他应用程序")
        return False
    
    return True

# 实验前检查
if not check_memory_availability(required_gb=4):
    print("请释放内存后再运行实验")
    exit(1)
```



## 10. 预期输出与价值

### 10.1 核心数据产出

#### 10.1.1 精细化实验数据集

**数据结构**：

```
data/experiments_N/
├── raw/                          # 原始实验数据
│   ├── qwen3_4b/
│   │   ├── exp_1234567890.json   # 完整实验结果
│   │   └── ...
│   ├── qwen3_8b/
│   ├── deepseek-r1_8b/
│   └── gemma3_4b/
├── texts/                        # 文本输出
│   ├── qwen3_4b/
│   │   ├── qa_task1_r1.txt
│   │   └── ...
├── summary/                      # 汇总数据
│   ├── results.csv               # 所有实验结果汇总
│   ├── stats.csv                 # 统计摘要
│   └── analysis_data.csv         # 分析中间数据
├── monitoring/                   # 监控数据
│   ├── exp_1234567890_monitor.json
│   ├── exp_1234567890_events.json
│   └── idle_baseline.json
└── test_cases.json               # 测试用例定义
```

**数据字段完整性**：

每个实验记录包含：

1. **基础信息**：
   - `experiment_id`：实验唯一标识
   - `model`：模型名称和量化方式
   - `task_id`, `task_type`：任务标识和类型
   - `timestamp`：时间戳

2. **性能指标**：
   - `latency_s`：端到端延迟
   - `ttft_s`：首 token 时间
   - `tpot_s`：每 token 时间
   - `throughput_tps`：吞吐量
   - `n_tokens`：生成 token 数

3. **能耗指标**：
   - `gpu_power_avg_w`：平均 GPU 功耗
   - `gpu_energy_j`：总 GPU 能耗
   - `cpu_energy_j_approx`：估算 CPU 能耗
   - `e_token_j`：每 token 能耗
   - `ppw`：性能功耗比

4. **资源利用**：
   - `gpu_util_avg`：平均 GPU 利用率
   - `gpu_mem_peak_mb`：峰值显存占用
   - `gpu_temp_peak_c`：峰值温度

5. **质量指标**：
   - `quality_score`：综合质量得分
   - 任务特定指标（BARTScore, distinct-2, 编译通过率等）

6. **功耗轨迹**（时间序列）：
   - `timestamps[]`：采样时间点
   - `gpu_power_w[]`：GPU 功耗序列
   - `gpu_util[]`：GPU 利用率序列
   - `gpu_temp_c[]`：GPU 温度序列

**数据量估算**：

- 单次实验：约 0.5-1 MB
- 完整阶段 1（96 次实验）：约 50-100 MB
- 包含汇总和图表：约 150 MB


#### 10.1.2 多维度分析报告

**自动化报告生成**：

```
results/experiments_N/
├── report.md                     # 主报告（Markdown）
├── figures/                      # 可视化图表
│   ├── throughput_vs_latency.png
│   ├── energy_vs_quality.png
│   ├── qe_ratio_bars.png
│   ├── radar_chart.png
│   ├── power_trace_sample.png
│   ├── pareto_frontier.png
│   ├── cost_analysis.png
│   ├── task_comparison.png
│   ├── model_heatmap.png
│   └── correlation_matrix.png
├── tables/                       # 数据表格
│   ├── model_ranking.csv
│   ├── task_performance.csv
│   └── efficiency_metrics.csv
└── metadata.json                 # 报告元数据
```

**报告内容结构**：

1. **执行摘要**
   - 实验概况（模型数、任务数、总时间）
   - 关键发现（Top 3 模型、最优配置）
   - 推荐建议

2. **模型性能对比**
   - 延迟和吞吐量对比
   - 能耗效率对比
   - 质量得分对比
   - 综合排名

3. **任务维度分析**
   - 各任务类型的模型表现
   - 任务难度分析
   - 最适模型推荐

4. **能效深度分析**
   - 功耗轨迹分析
   - 分阶段能耗（Prefill vs Decode）
   - 能效优化建议

5. **帕累托前沿**
   - 质量-能效权衡
   - 最优模型集合
   - 应用场景匹配

6. **成本效益分析**
   - TCO 模型
   - 单位成本质量（CPQ）
   - 投资回报建议

7. **统计显著性检验**
   - 模型间差异显著性
   - 置信区间
   - 效应量（Effect Size）

8. **附录**
   - 完整数据表
   - 实验配置
   - 异常记录


### 10.2 学术价值

#### 10.2.1 方法论贡献

1. **系统级能耗测量方法**
   - 适用于 Windows + Ollama 环境的标准化测量流程
   - 5Hz 高频采样 + 事件同步的精确测量
   - 分阶段能耗分析（Prefill/Decode）
   - 可复现的实验协议

2. **多维效质比评估框架**
   - 统一的符号体系和指标定义
   - 归一化和复合指标计算方法
   - 帕累托前沿分析
   - 公平性评估扩展（基于 RLHF 文献）

3. **任务自适应评估**
   - 8 种任务类型的差异化参数配置
   - 多轮对话支持
   - 上下文验证任务
   - 任务特定质量指标

**预期论文产出**：

- 会议论文：方法论和实验结果（如 ACL, EMNLP, NeurIPS Workshop）
- 期刊论文：完整的评估框架和深度分析（如 TACL, JMLR）
- 技术报告：详细的实验协议和数据集描述

#### 10.2.2 实证数据贡献

**数据集特点**：

- **规模**：4 个模型 × 8 种任务 × 3 次重复 = 96 个数据点（阶段 1）
- **粒度**：5Hz 功耗采样，毫秒级事件记录
- **完整性**：性能 + 能耗 + 质量 + 资源利用
- **可复现**：完整的配置和代码开源

**潜在引用价值**：

- 为其他研究者提供基准数据
- 支持元分析（Meta-analysis）
- 验证新方法的对比基线

#### 10.2.3 理论洞察

**预期发现**：

1. **量化精度 vs 能效权衡**
   - Q4 vs Q8 的质量损失和能耗节省
   - 不同任务对量化的敏感度

2. **模型规模 vs 效率**
   - 4B vs 8B 模型的质效比
   - 小模型在特定任务的优势

3. **任务特性影响**
   - 生成长度对能耗的影响
   - 推理复杂度（CoT）的能耗代价

4. **硬件瓶颈分析**
   - RTX 4060 Laptop 的性能上限
   - 显存限制对模型选择的影响


### 10.3 工业应用价值

#### 10.3.1 模型选型决策支持

**实用工具**：

1. **模型选型矩阵**

| 应用场景 | 推荐模型 | 理由 | 预期性能 |
|---------|---------|------|---------|
| **实时对话** | qwen3:4b | 低延迟，TTFT < 500ms | 中等质量，高响应速度 |
| **文档摘要** | qwen3:8b | 质量优先，能耗可接受 | 高质量，中等能耗 |
| **代码生成** | deepseek-r1:8b | 专业能力强 | 高质量，较高能耗 |
| **批量处理** | gemma3:4b | 高吞吐，低能耗 | 中等质量，最低能耗 |

2. **成本计算器**

```python
def estimate_deployment_cost(model_name, daily_requests, avg_tokens=200):
    """估算部署成本"""
    # 从实验数据中获取指标
    latency_s = get_metric(model_name, 'latency_s')
    e_token_j = get_metric(model_name, 'e_token_j')
    
    # 计算每日成本
    total_time_h = (daily_requests * latency_s) / 3600
    total_energy_kwh = (daily_requests * avg_tokens * e_token_j) / (3.6 * 1e6)
    
    gpu_cost = total_time_h * GPU_HOURLY_RATE
    energy_cost = total_energy_kwh * ELECTRICITY_PRICE
    
    return {
        'gpu_cost_usd': gpu_cost,
        'energy_cost_usd': energy_cost,
        'total_cost_usd': gpu_cost + energy_cost,
        'cost_per_request_usd': (gpu_cost + energy_cost) / daily_requests
    }

# 示例
print(estimate_deployment_cost('qwen3:8b', daily_requests=10000))
```

3. **配置优化建议**

基于实验数据，为不同场景提供：
- 最优 temperature 设置
- 最优 max_tokens 限制
- 批处理大小建议
- 缓存策略建议

#### 10.3.2 能效评级体系

**分级标准**（基于实证数据）：

| 等级 | 质效比范围 | 能耗水平 | 适用场景 |
|-----|-----------|---------|---------|
| **A+** | QE > 2.0 | E < 0.5 J/token | 生产环境，大规模部署 |
| **A** | 1.5 < QE ≤ 2.0 | 0.5 ≤ E < 1.0 | 通用应用 |
| **B** | 1.0 < QE ≤ 1.5 | 1.0 ≤ E < 2.0 | 质量优先场景 |
| **C** | 0.5 < QE ≤ 1.0 | 2.0 ≤ E < 4.0 | 特定任务 |
| **D** | QE ≤ 0.5 | E ≥ 4.0 | 不推荐 |

**评级工具**：

```python
def rate_model(model_name, task_type):
    """为模型-任务组合评级"""
    qe_ratio = get_metric(model_name, task_type, 'qe_ratio')
    e_token = get_metric(model_name, task_type, 'e_token_j')
    
    if qe_ratio > 2.0 and e_token < 0.5:
        return 'A+'
    elif qe_ratio > 1.5 and e_token < 1.0:
        return 'A'
    elif qe_ratio > 1.0 and e_token < 2.0:
        return 'B'
    elif qe_ratio > 0.5 and e_token < 4.0:
        return 'C'
    else:
        return 'D'

# 生成评级报告
for model in MODELS:
    for task in TASKS:
        rating = rate_model(model, task)
        print(f"{model} - {task}: {rating}")
```

#### 10.3.3 优化路线图

**基于实验结果的优化建议**：

1. **短期优化**（0-3 个月）
   - 切换到最优模型-量化组合
   - 调整生成参数（temperature, max_tokens）
   - 实施请求批处理

2. **中期优化**（3-6 个月）
   - 部署模型缓存
   - 实施负载均衡
   - 优化提示词工程

3. **长期优化**（6-12 个月）
   - 考虑模型微调
   - 评估新模型版本
   - 硬件升级规划


### 10.4 环境与可持续发展价值

#### 10.4.1 碳排放量化

**碳足迹计算**：

```python
def calculate_carbon_footprint(energy_j, carbon_intensity=0.5):
    """
    计算碳排放
    
    Args:
        energy_j: 能耗（焦耳）
        carbon_intensity: 碳强度（kg CO2/kWh），中国平均约 0.5
    
    Returns:
        float: 碳排放（kg CO2）
    """
    energy_kwh = energy_j / (3.6 * 1e6)
    carbon_kg = energy_kwh * carbon_intensity
    return carbon_kg

# 示例：计算单次推理的碳排放
energy_per_inference = 100  # J
carbon = calculate_carbon_footprint(energy_per_inference)
print(f"单次推理碳排放: {carbon*1000:.2f} g CO2")

# 年度碳排放估算
annual_requests = 1e6
annual_carbon = carbon * annual_requests
print(f"年度碳排放: {annual_carbon:.2f} kg CO2")
print(f"相当于: {annual_carbon/10:.2f} 棵树一年的吸收量")
```

**环境影响对比**：

| 模型 | 单次推理能耗 (J) | 单次碳排放 (g CO2) | 百万次请求碳排放 (kg CO2) |
|-----|----------------|-------------------|------------------------|
| qwen3:4b | 80 | 0.011 | 11 |
| qwen3:8b | 150 | 0.021 | 21 |
| deepseek-r1:8b | 180 | 0.025 | 25 |
| gemma3:4b | 70 | 0.010 | 10 |

#### 10.4.2 可持续性建议

**绿色 AI 实践**：

1. **模型选择**
   - 优先选择能效比高的模型
   - 在质量可接受的前提下选择小模型
   - 使用量化模型（Q4 vs FP16 可节省 60% 能耗）

2. **部署优化**
   - 批处理请求以提高 GPU 利用率
   - 使用模型缓存减少重复加载
   - 在低碳时段运行批量任务

3. **监控与报告**
   - 持续监控能耗指标
   - 定期生成碳排放报告
   - 设置能耗预算和告警

**ESG 报告支持**：

本实验数据可直接用于企业 ESG（环境、社会、治理）报告：

- **环境维度**：AI 系统的能耗和碳排放数据
- **社会维度**：负责任 AI 的实践证明
- **治理维度**：技术决策的数据支持


### 10.5 开源与社区价值

#### 10.5.1 开源资产

**计划开源内容**：

1. **完整代码库**
   - 实验执行脚本（`experiments/experiment_runner.py`）
   - 监控工具（`experiments/monitor.py`）
   - 数据分析脚本（`scripts/analyze_experiments.py`）
   - 可视化工具（`scripts/visualize_*.py`）

2. **实验数据集**
   - 原始实验结果（JSON 格式）
   - 汇总数据（CSV 格式）
   - 监控数据（时间序列）
   - 测试用例（`test_cases.json`）

3. **文档与教程**
   - 实验设计文档（本文档）
   - 操作指南（`experiment_operation_guide.md`）
   - API 文档
   - 最佳实践指南

4. **可复现配置**
   - Docker 配置（可选）
   - 环境配置文件（`requirements.txt`, `environment.yml`）
   - 模型下载脚本
   - 自动化测试脚本

**开源许可**：

- 代码：MIT License
- 数据：CC BY 4.0
- 文档：CC BY-SA 4.0

#### 10.5.2 社区贡献

**预期影响**：

1. **研究社区**
   - 为 LLM 能效研究提供标准化方法
   - 促进可复现研究
   - 支持元分析和综述论文

2. **开发者社区**
   - 提供模型选型参考
   - 分享优化经验
   - 降低评估门槛

3. **产业界**
   - 支持技术决策
   - 提供成本估算工具
   - 促进绿色 AI 实践

**社区参与方式**：

- GitHub Issues：问题反馈和功能请求
- Pull Requests：代码贡献
- Discussions：经验分享和讨论
- Wiki：社区维护的知识库

#### 10.5.3 持续更新计划

**版本迭代**：

- **v1.0**（当前）：基础框架 + 4 个模型
- **v1.1**（3 个月后）：新增 3-5 个模型，扩展任务类型
- **v2.0**（6 个月后）：支持多 GPU，分布式评估
- **v3.0**（12 个月后）：支持多模态模型（视觉 + 语言）

**数据更新**：

- 季度更新：新模型评估
- 年度更新：完整重新评估（考虑硬件和软件更新）
- 按需更新：重大模型发布时


### 10.6 总结与展望

#### 10.6.1 核心价值总结

本实验设计通过系统化的方法论和精细化的测量，将产出：

1. **数据价值**
   - 高质量、可复现的实验数据集
   - 完整的功耗轨迹和性能指标
   - 多维度的质效比评估结果

2. **方法价值**
   - 标准化的能效评估协议
   - 适用于 Windows + Ollama 的测量方案
   - 可扩展的评估框架

3. **应用价值**
   - 模型选型决策支持
   - 成本效益分析工具
   - 能效评级体系

4. **社会价值**
   - 促进绿色 AI 发展
   - 支持可持续技术决策
   - 推动行业标准建立

#### 10.6.2 局限性与未来工作

**当前局限**：

1. **硬件限制**
   - 仅测试 RTX 4060 Laptop（8GB）
   - 无法评估更大模型（> 10B）
   - 单 GPU 环境

2. **模型覆盖**
   - 主要关注 Ollama 支持的开源模型
   - 未包含闭源 API（GPT-4, Claude 等）
   - 量化方式有限（Q4, Q8）

3. **任务范围**
   - 8 种任务类型，可能不全面
   - 缺少多模态任务
   - 缺少长文本任务（> 4K tokens）

4. **测量精度**
   - CPU 功耗为估算值
   - 无法测量内存功耗
   - 采样频率受限（5Hz）

**未来扩展方向**：

1. **硬件扩展**
   - 支持多 GPU 评估
   - 支持不同 GPU 型号对比
   - 支持 CPU 推理评估

2. **模型扩展**
   - 评估更多开源模型
   - 支持 API 模型评估（通过代理测量）
   - 支持多模态模型

3. **任务扩展**
   - 增加领域特定任务（医疗、法律等）
   - 支持长文本任务
   - 支持多轮复杂对话

4. **方法改进**
   - 更精确的 CPU 功耗测量
   - 支持分布式评估
   - 实时监控和告警

5. **工具完善**
   - Web 界面
   - 实时仪表板
   - 自动化报告生成

#### 10.6.3 行动建议

**对于研究者**：

1. 使用本框架进行可复现研究
2. 贡献新的评估方法和指标
3. 分享实验数据和发现

**对于开发者**：

1. 参考实验结果进行模型选型
2. 使用工具评估自己的模型
3. 贡献代码和改进建议

**对于企业**：

1. 基于数据制定技术决策
2. 建立内部能效评估流程
3. 将能效纳入 KPI 考核

**对于政策制定者**：

1. 参考评级体系制定标准
2. 推动绿色 AI 政策
3. 支持可持续技术发展

---

## 附录

### A. 快速开始指南

**5 分钟快速开始**：

```bash
# 1. 克隆仓库
git clone https://github.com/your-repo/GenAI_power_analyze.git
cd GenAI_power_analyze

# 2. 安装依赖
conda create -n bartscore python=3.10
conda activate bartscore
pip install -r requirements.txt

# 3. 下载模型
ollama pull qwen3:4b

# 4. 运行单次实验
python experiments/experiment_runner.py --model qwen3:4b --tasks qa,summary

# 5. 查看结果
python scripts/analyze_experiments.py --experiment experiments_N
```

### B. 常见问题 (FAQ)

**Q1: 为什么选择 Ollama 而不是 vLLM 或 TGI？**

A: Ollama 在 Windows 上安装简单，对笔记本友好，适合快速原型和教学。未来版本会支持其他框架。

**Q2: 如何处理 CUDA Out of Memory 错误？**

A: 尝试：(1) 使用更小的模型或更低的量化；(2) 减少 `num_ctx`；(3) 关闭其他 GPU 应用。

**Q3: 实验需要多长时间？**

A: 阶段 1（4 模型 × 8 任务 × 3 重复）约需 6-8 小时，包括冷却时间。

**Q4: 数据可以商用吗？**

A: 数据采用 CC BY 4.0 许可，可商用，需注明出处。

**Q5: 如何贡献新模型的评估结果？**

A: 提交 Pull Request，包含原始数据和简要说明。

### C. 联系方式

- **GitHub**: https://github.com/your-repo/GenAI_power_analyze
- **Email**: your-email@example.com
- **论文**: [待发布]

---

**文档版本**: v2.0  
**最后更新**: 2026-03-01  
**作者**: [Your Name]  
**许可**: CC BY-SA 4.0