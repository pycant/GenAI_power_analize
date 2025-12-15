# 技术栈与构建系统

## 核心技术

### 后端技术栈
- **框架**: FastAPI (Python 3.8+) - 高性能异步Web框架
- **数据库**: PostgreSQL 15+ 配合 SQLAlchemy ORM 和 Alembic 迁移
- **缓存/队列**: Redis 7+ 用于缓存和 Celery 任务队列
- **机器学习/AI**: PyTorch 2.1+, Transformers 4.36+, scikit-learn
- **评估工具**: BARTScore 用于文本生成质量评估
- **监控**: MLflow 实验跟踪, Prometheus + Grafana

### 前端技术栈
- **框架**: React 18+ 配合 TypeScript
- **构建工具**: Vite 5+ 用于快速开发和构建
- **UI组件**: Radix UI 原语配合 Tailwind CSS
- **状态管理**: Zustand 管理客户端状态, TanStack Query 管理服务端状态
- **可视化**: Recharts 用于图表和数据可视化
- **测试**: Vitest 单元测试, Playwright E2E测试

### 基础设施
- **容器化**: Docker 配合 docker-compose 本地开发
- **反向代理**: Nginx 生产环境部署
- **模型服务**: Ollama 本地LLM推理
- **日志**: ELK Stack (Elasticsearch, Logstash, Kibana) 可选
- **开发**: Jupyter notebooks 数据分析和实验

## 常用命令

### 开发环境搭建
```bash
# 后端设置
pip install -r requirements.txt
python scripts/setup_database.py
uvicorn src.backend.main:app --reload --host 0.0.0.0 --port 8000

# 前端设置
cd frontend
npm install
npm run dev

# Docker全栈启动
docker-compose up -d
```

### 测试
```bash
# 后端测试
pytest tests/ --cov=src
python -m pytest tests/unit/ -v

# 前端测试
cd frontend
npm run test
npm run test:coverage
npm run e2e

# 集成测试
python tests/integration/test_api_integration.py
```

### 实验执行
```bash
# 运行评估实验
python experiments/experiment_runner.py
python experiments/run_experiments.py --config experiments/configs/baseline_config.yaml

# 分析结果
python scripts/analyze_experiments_1.py
jupyter lab experiments/notebooks/
```

### 代码质量
```bash
# Python格式化和检查
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# 前端格式化和检查
cd frontend
npm run lint:fix
npm run format
npm run type-check
```

### 数据库操作
```bash
# 数据库迁移
alembic upgrade head
alembic revision --autogenerate -m "description"

# 数据库备份/恢复
python scripts/backup_database.py
python scripts/setup_database.py --restore backup.sql
```

### 部署
```bash
# 生产构建
npm run build:production
docker-compose --profile production up -d

# 包含监控
docker-compose --profile production --profile monitoring up -d

# 健康检查
curl http://localhost:8000/health
docker-compose ps
```

## 开发工作流

1. **本地开发**: 使用 `docker-compose up -d` 启动全栈或单独运行服务
2. **代码修改**: 后端通过uvicorn自动重载，前端通过Vite HMR热更新
3. **测试**: 提交前运行测试，CI/CD运行完整测试套件
4. **实验**: 使用Jupyter notebooks探索，Python脚本自动化运行
5. **部署**: Docker容器配合环境特定配置

## 关键依赖

### Python (requirements.txt)
- `fastapi==0.104.1` - Web框架
- `torch==2.1.1` - 深度学习框架
- `transformers==4.36.0` - Hugging Face transformers
- `sqlalchemy==2.0.23` - 数据库ORM
- `celery==5.3.4` - 异步任务队列
- `pandas==2.1.3` - 数据处理
- `scikit-learn==1.3.2` - 机器学习工具

### Node.js (package.json)
- `react@^18.2.0` - UI框架
- `typescript@^5.3.2` - 类型安全
- `vite@^5.0.4` - 构建工具
- `@tanstack/react-query@^5.8.4` - 服务端状态管理
- `recharts@^2.8.0` - 数据可视化
- `tailwindcss@^3.3.6` - CSS框架

## 性能考虑

- 使用Redis缓存频繁访问的数据
- 实现数据库连接池
- 通过缓存优化ML模型加载
- 生产环境使用CDN处理静态资源
- 使用Prometheus指标监控资源使用
- 实现适当的错误处理和日志记录