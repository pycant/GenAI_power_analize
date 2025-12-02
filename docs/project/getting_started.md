# GenAI模型能效评级体系 - 快速开始指南

欢迎来到GenAI模型能效评级体系项目！本指南将帮助您快速搭建开发环境并开始使用本项目。

## 📋 前置要求

在开始之前，请确保您的系统满足以下要求：

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, 或 Linux (Ubuntu 20.04+)
- **内存**: 最少8GB RAM，推荐16GB或更多
- **存储**: 最少50GB可用磁盘空间
- **网络**: 稳定的互联网连接（用于下载模型和数据）

### 软件依赖
- **Python**: 3.8或更高版本
- **Node.js**: 18.0或更高版本
- **Git**: 2.20或更高版本
- **Docker**: 20.10或更高版本（可选，用于容器化部署）

## 🚀 快速安装

### 方法1：自动安装（推荐）

我们提供了一个自动化的安装脚本，可以帮您完成大部分设置工作：

```bash
# 克隆项目
git clone https://github.com/your-org/genai-power-evaluation.git
cd genai-power-evaluation

# 运行安装脚本
chmod +x scripts/setup.sh
./scripts/setup.sh
```

安装脚本会自动：
- ✅ 检查系统环境和依赖
- ✅ 创建Python虚拟环境
- ✅ 安装Python依赖包
- ✅ 安装前端依赖
- ✅ 创建必要的目录结构
- ✅ 初始化Git仓库
- ✅ 生成配置文件
- ✅ 运行基础测试

### 方法2：手动安装

如果您更喜欢手动控制每个步骤，可以按照以下步骤进行：

#### 1. 克隆项目

```bash
git clone https://github.com/your-org/genai-power-evaluation.git
cd genai-power-evaluation
```

#### 2. 创建Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

#### 3. 安装Python依赖

```bash
# 升级pip
pip install --upgrade pip setuptools wheel

# 安装项目依赖
pip install -r requirements.txt
```

#### 4. 安装前端依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 返回项目根目录
cd ..
```

#### 5. 配置环境变量

```bash
# 复制环境配置模板
cp .env.example .env

# 编辑配置文件（根据您的环境修改）
nano .env
```

#### 6. 初始化数据库

```bash
# 运行数据库初始化脚本
python scripts/init_db.py
```

#### 7. 创建必要目录

```bash
# 创建数据目录
mkdir -p data/{raw,processed,external}
mkdir -p results logs uploads cache/models
```

## 🏃‍♂️ 启动服务

项目支持多种启动方式，您可以根据需要选择：

### 方式1：开发模式启动

#### 启动后端服务

```bash
# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 启动后端服务
python -m src.backend.main
```

后端服务将在 http://localhost:8000 启动，您可以访问：
- 📚 API文档: http://localhost:8000/docs
- 🔍 交互式API测试: http://localhost:8000/redoc

#### 启动前端服务

```bash
# 进入前端目录
cd frontend

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:5173 启动。

### 方式2：Docker Compose启动（推荐）

如果您安装了Docker，可以使用Docker Compose一键启动所有服务：

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f [service_name]
```

这将启动以下服务：
- 🌐 前端应用: http://localhost:3000
- 🔧 后端API: http://localhost:8000
- 📊 任务监控: http://localhost:5555
- 📝 Jupyter Notebook: http://localhost:8888
- 🧪 实验跟踪: http://localhost:5000

### 方式3：生产环境启动

对于生产环境部署，我们提供了专门的配置：

```bash
# 构建前端生产版本
cd frontend
npm run build
cd ..

# 使用生产配置启动
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 验证安装

安装完成后，您可以通过以下方式验证系统是否正常运行：

### 1. 健康检查

```bash
# 检查后端服务状态
curl http://localhost:8000/health

# 预期响应: {"status": "healthy", "timestamp": "..."}
```

### 2. 运行测试

```bash
# 运行Python测试
pytest tests/ -v

# 运行前端测试
cd frontend && npm test
```

### 3. 访问Web界面

打开浏览器访问 http://localhost:3000，您应该能看到项目的主界面。

## 📖 基本使用

### 1. 模型评估流程

1. **上传模型**: 在Web界面上传您的AI模型文件
2. **配置评估**: 选择评估指标和数据集
3. **运行评估**: 启动评估任务
4. **查看结果**: 在仪表板查看评估结果和分析报告

### 2. 数据集管理

- 支持多种数据格式：JSON、CSV、Parquet等
- 提供数据预处理工具
- 支持数据版本控制

### 3. 实验跟踪

- 自动记录实验参数和结果
- 支持实验对比分析
- 生成详细的评估报告

## 🔧 常见问题解决

### 问题1：Python依赖安装失败

**症状**: pip安装时出现编译错误或依赖冲突

**解决方案**:
```bash
# 升级pip和工具
pip install --upgrade pip setuptools wheel

# 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 如果仍然失败，尝试单独安装问题包
pip install package-name --no-cache-dir
```

### 问题2：Node.js依赖安装失败

**症状**: npm install出现网络错误或权限问题

**解决方案**:
```bash
# 清理npm缓存
npm cache clean --force

# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install
```

### 问题3：数据库连接失败

**症状**: 后端启动时报数据库连接错误

**解决方案**:
```bash
# 检查数据库服务是否启动
# 如果使用Docker:
docker-compose logs postgres

# 检查数据库配置
grep DATABASE_URL .env

# 手动初始化数据库
python scripts/init_db.py
```

### 问题4：端口被占用

**症状**: 启动服务时提示端口已被使用

**解决方案**:
```bash
# 查看端口使用情况
# Linux/macOS:
lsof -i :8000
# Windows:
netstat -ano | findstr :8000

# 修改配置文件中的端口
# 编辑 .env 文件，修改相应的端口配置
```

### 问题5：模型下载失败

**症状**: 评估过程中模型下载超时或失败

**解决方案**:
```bash
# 检查网络连接
ping huggingface.co

# 设置代理（如果需要）
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port

# 使用国内镜像源
# 在配置文件中设置Hugging Face镜像
```

## 🎯 下一步

恭喜您成功搭建GenAI模型能效评级体系！接下来您可以：

1. **📚 阅读文档**: 查看详细的[用户手册](user_manual.md)
2. **🔬 运行实验**: 使用提供的示例数据集进行模型评估
3. **⚙️ 自定义配置**: 根据您的需求调整系统配置
4. **🚀 部署生产**: 参考[部署指南](deployment.md)进行生产环境部署
5. **🤝 贡献代码**: 查看[贡献指南](../CONTRIBUTING.md)参与项目开发

## 📞 获取帮助

如果您遇到问题或需要帮助，可以通过以下方式联系我们：

- 📧 **邮箱**: genai-power@university.edu
- 💬 **讨论区**: [GitHub Discussions](https://github.com/your-org/genai-power-evaluation/discussions)
- 🐛 **问题报告**: [GitHub Issues](https://github.com/your-org/genai-power-evaluation/issues)
- 📖 **文档**: [项目Wiki](https://github.com/your-org/genai-power-evaluation/wiki)

## 📄 许可证

本项目采用MIT许可证，详见 [LICENSE](../LICENSE) 文件。

---

**祝您使用愉快！** 🎉