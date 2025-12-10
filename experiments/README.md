# GenAI模型能效评级体系实验框架

## 📋 简介

本实验框架用于自动化执行GenAI模型的性能和质量评估实验，收集模型在不同任务下的硬件资源消耗、生成性能和生成质量数据，为构建"效质比"评级体系奠定实证基础。

## 🚀 快速开始

### 1. 环境准备

确保已安装并配置好以下组件：
- Ollama服务及所需模型
- Python依赖库: `pip install psutil pynvml`
- BARTScore环境（可选，用于质量评估）

### 2. 验证环境

```bash
# 检查Ollama服务
ollama --version
ollama list

# 检查Python依赖
python -c "import psutil; print('psutil available')"
python -c "import pynvml; print('pynvml available')"
```

### 3. 运行示例实验

```bash
# 运行默认示例测试用例
python experiment_runner.py

# 运行所有示例测试用例
python experiment_runner.py --sample

# 使用自定义测试用例配置文件
python experiment_runner.py --config test_cases.json

# 指定结果输出目录
python experiment_runner.py --output-dir ./my_results
```

## 📁 项目结构

```
experiments/
├── experiment_runner.py     # 实验执行主脚本
├── test_cases.json          # 测试用例配置文件
├── README.md               # 本说明文件
└── results/                # 默认结果输出目录
```

## ⚙️ 使用说明

### 测试用例配置

测试用例配置文件采用JSON格式，每个测试用例包含以下字段：

- `model`: 模型名称（必填）
- `prompt`: 输入提示（必填）
- `task_type`: 任务类型（必填）
- `reference_text`: 参考文本（可选，用于质量评估）
- `max_tokens`: 最大token数（可选，默认200）
- `temperature`: 温度参数（可选，默认0.7）

### 实验执行

运行`experiment_runner.py`脚本时，可以使用以下命令行参数：

- `--output-dir DIR`: 指定结果输出目录
- `--config FILE`: 指定测试用例配置文件
- `--sample`: 运行示例测试用例

### 结果输出

实验结果将以JSON格式保存在指定的输出目录中，文件名格式为`experiment_results_YYYYMMDD_HHMMSS.json`。

每个实验结果包含以下信息：
- 模型配置信息
- 性能指标（吞吐量、延迟等）
- 资源消耗数据（CPU、GPU、内存等）
- 质量评估分数
- 时间戳和元数据

## 🧪 实验设计建议

### 模型选择

建议选择2-3个不同系列、不同参数量的模型进行对比：
- `llama3.2:3b` vs `llama3.2:11b` vs `gemma2:9b`
- `phi3:3.8b` vs `mistral:7b` vs `mixtral:8x7b`

### 任务类型

涵盖以下不同类型的任务：
- **知识问答**: 测试事实性与信息性
- **文本摘要**: 测试连贯性与覆盖度
- **代码生成**: 测试逻辑正确性
- **创意写作**: 测试流畅性与多样性

### 任务负载

设计不同长度的输入/输出：
- **短**: 约50-100 tokens
- **中**: 约200-500 tokens
- **长**: 约1000+ tokens

## ⚠️ 注意事项

1. **权限要求**: 脚本可能需要管理员权限以重启Ollama服务
2. **GPU监控**: 需要NVIDIA GPU及相关驱动才能获取GPU使用数据
3. **稳定性**: 长时间运行可能因系统资源不足或模型崩溃而中断，建议分批运行
4. **数据存储**: 大量实验会产生较多数据，注意磁盘空间
5. **网络连接**: 首次运行新模型时需要下载，确保网络连接稳定

## 📈 后续步骤

1. 收集足够的实验数据后，可进行"效质比"计算和模型比较
2. 分析不同模型在不同任务类型下的表现差异
3. 探索模型参数量、量化精度等因素对性能的影响
4. 构建可视化图表以直观展示实验结果
5. 根据实验结果优化模型选择和部署策略
