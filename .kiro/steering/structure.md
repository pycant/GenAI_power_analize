# 项目结构与组织

## 根目录布局

```
GenAI_power_analize/
├── src/                    # 源代码 - 核心应用逻辑
├── experiments/            # 实验框架和执行
├── data/                   # 实验数据和结果存储
├── docs/                   # 文档（学术、技术、协作）
├── tools/                  # 开发工具和实用程序
├── scripts/                # 自动化和设置脚本
├── frontend/               # React前端应用
├── results/                # 分析结果和报告
├── configs/                # 配置文件
├── tests/                  # 测试套件（单元、集成、端到端）
└── logs/                   # 应用和系统日志
```

## 关键目录用途

### `/src` - 核心应用代码
- `backend/` - FastAPI后端服务和API
- `evaluation/` - 核心评估引擎和指标
- `data_collection/` - 数据收集和处理
- `model_deployment/` - 模型服务和管理
- `utils/` - 共享工具和辅助函数

### `/experiments` - 评估框架
- **主要入口**: `experiment_runner.py` - 主实验执行脚本
- **配置**: `config.py` - 实验参数和设置
- **测试用例**: `test_cases.json` - 评估场景和提示
- **监控**: `monitor.py` - 资源使用跟踪
- **质量评估**: `quality.py` - 使用BARTScore进行文本质量评估

### `/data` - 实验数据管理
- `experiments_N/` - 带时间戳的单个实验运行数据
  - `raw/` - 按模型名称分类的原始模型输出
  - `texts/` - 处理后的文本输出
  - `summary/` - 聚合结果（CSV格式）
  - `config.json` - 实验配置快照

### `/docs` - 文档结构
- `academic/` - 研究论文和学术文档
- `technical/` - API文档、架构、部署指南
- `project/` - 项目管理和协作文档
- `reference/` - 文献综述和研究参考

### `/tools` - 专用工具
- `thesis_reproduction/BARTScore/` - BARTScore评估实现
- 开发工具和分析工具

## 文件命名约定

### 实验数据文件
- **原始输出**: `{task_type}_custom_r{run_number}.json`
- **文本输出**: `{task_type}_custom_r{run_number}.txt`
- **结果**: `results.csv`, `stats.csv`
- **配置**: `config.json`, `config.py`

### 模型命名
- 使用小写字母和连字符: `deepseek-r1_8b`, `gemma3_4b`, `qwen3_8b`
- 在模型目录名中包含参数数量

### 文档文件
- 使用描述性名称和下划线: `technical_architecture.md`
- 学术论文编号: `01_introduction.md`, `02_methodology.md`

## 代码组织模式

### 后端结构
```
src/backend/
├── api/routes/           # API端点定义
├── core/                 # 配置和数据库设置
├── models/               # SQLAlchemy数据模型
├── services/             # 业务逻辑层
└── utils/                # 后端工具
```

### 前端结构
```
frontend/src/
├── components/           # 可复用UI组件
├── pages/                # 路由级页面组件
├── services/             # API调用和外部服务
├── store/                # 状态管理（Zustand）
├── utils/                # 前端工具
└── types/                # TypeScript类型定义
```

### 实验结构
```
experiments/
├── configs/              # YAML配置文件
├── notebooks/            # Jupyter分析笔记本
├── scripts/              # 自动化脚本
└── results/              # 生成的输出和报告
```

## 配置管理

### 环境特定配置
- `.env.example` - 环境变量模板
- `docker-compose.yml` - 容器编排
- `configs/` - 应用特定配置文件

### 实验配置
- `experiments/config.py` - 默认实验参数
- `data/experiments_N/config.json` - 每个实验的配置快照
- YAML文件用于复杂实验设置

## 数据流模式

### 实验执行流程
1. **输入**: 来自 `test_cases.json` 的测试用例
2. **处理**: 通过Ollama集成执行模型
3. **监控**: 实时跟踪资源使用情况
4. **输出**: 原始结果保存到 `data/experiments_N/raw/`
5. **分析**: 结果在 `summary/` 中处理和汇总

### 开发工作流
1. **后端**: FastAPI提供评估API
2. **前端**: React应用消费后端API
3. **实验**: 独立执行框架
4. **集成**: 结果流入主应用数据库

## 导入和模块模式

### Python导入
- 使用项目根目录的绝对导入: `from src.backend.core import config`
- 实验模块: `from experiments.quality import evaluate_with_bartscore`
- 工具: `from src.utils.logger import get_logger`

### 前端导入
- 组件: `import { Button } from '@/components/ui/button'`
- 服务: `import { apiClient } from '@/services/api'`
- 类型: `import type { ExperimentResult } from '@/types/experiments'`

## 最佳实践

### 文件组织
- 将相关文件保持在逻辑目录中
- 在整个项目中使用一致的命名约定
- 分离关注点：数据、代码、配置、文档

### 实验管理
- 每个实验运行都有自己的时间戳目录
- 保留原始配置和结果
- 使用描述性任务类型和模型名称

### 文档
- 将文档与相关代码放在一起
- 维护技术和学术文档
- 使用markdown保持一致性和版本控制

### 版本控制
- 排除大型数据文件和模型权重
- 包含配置文件和模式
- 使用 `.gitignore` 管理临时和生成的文件