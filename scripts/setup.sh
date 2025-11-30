#!/bin/bash

# GenAI模型能效评级体系 - 项目初始化脚本
# 功能：环境准备、依赖安装、数据库初始化等

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    log_info "检测到操作系统: $OS"
}

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [[ $PYTHON_MAJOR -ge 3 ]] && [[ $PYTHON_MINOR -ge 8 ]]; then
            log_success "Python $PYTHON_VERSION 符合要求 (>=3.8)"
            PYTHON_CMD="python3"
        else
            log_error "Python版本过低，需要3.8或更高版本"
            exit 1
        fi
    else
        log_error "未找到Python3，请先安装Python3.8+"
        exit 1
    fi
}

# 检查Node.js版本
check_nodejs() {
    log_info "检查Node.js版本..."
    
    if command_exists node; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1)
        
        if [[ $NODE_MAJOR -ge 18 ]]; then
            log_success "Node.js $NODE_VERSION 符合要求 (>=18)"
        else
            log_error "Node.js版本过低，需要18或更高版本"
            exit 1
        fi
    else
        log_error "未找到Node.js，请先安装Node.js 18+"
        exit 1
    fi
}

# 检查Docker和Docker Compose
check_docker() {
    log_info "检查Docker环境..."
    
    if command_exists docker; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker $DOCKER_VERSION 已安装"
    else
        log_warning "未找到Docker，建议安装Docker以便使用容器化部署"
    fi
    
    if command_exists docker-compose; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        log_success "Docker Compose $COMPOSE_VERSION 已安装"
    else
        log_warning "未找到Docker Compose，建议安装以便使用多容器服务"
    fi
}

# 创建虚拟环境
create_virtual_env() {
    log_info "创建Python虚拟环境..."
    
    if [[ ! -d "venv" ]]; then
        $PYTHON_CMD -m venv venv
        log_success "虚拟环境已创建"
    else
        log_warning "虚拟环境已存在，跳过创建"
    fi
}

# 激活虚拟环境
activate_virtual_env() {
    log_info "激活虚拟环境..."
    
    if [[ "$OS" == "windows" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    log_success "虚拟环境已激活"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    
    log_success "Python依赖安装完成"
}

# 安装前端依赖
install_frontend_deps() {
    log_info "安装前端依赖..."
    
    cd frontend
    
    if command_exists npm; then
        npm install
        log_success "前端依赖安装完成"
    else
        log_error "未找到npm，无法安装前端依赖"
        exit 1
    fi
    
    cd ..
}

# 创建必要的目录
create_directories() {
    log_info "创建项目目录结构..."
    
    directories=(
        "logs"
        "data/raw"
        "data/processed"
        "data/external"
        "results"
        "uploads"
        "cache/models"
        "checkpoints"
        "experiments"
        "notebooks"
        "docs/generated"
        "static"
        "media"
        "temp"
    )
    
    for dir in "${directories[@]}"; do
        if [[ ! -d "$dir" ]]; then
            mkdir -p "$dir"
            log_info "创建目录: $dir"
        fi
    done
    
    # 创建.gitkeep文件
    for dir in "${directories[@]}"; do
        if [[ -d "$dir" ]] && [[ -z "$(ls -A "$dir" 2>/dev/null)" ]]; then
            touch "$dir/.gitkeep"
        fi
    done
    
    log_success "目录结构创建完成"
}

# 初始化Git仓库
init_git_repo() {
    log_info "初始化Git仓库..."
    
    if [[ ! -d ".git" ]]; then
        git init
        log_success "Git仓库已初始化"
        
        # 添加远程仓库（如果提供）
        if [[ -n "$GIT_REMOTE_URL" ]]; then
            git remote add origin "$GIT_REMOTE_URL"
            log_success "远程仓库已添加: $GIT_REMOTE_URL"
        fi
    else
        log_warning "Git仓库已存在，跳过初始化"
    fi
}

# 创建环境配置文件
create_env_files() {
    log_info "创建环境配置文件..."
    
    if [[ ! -f ".env" ]]; then
        cp .env.example .env
        log_success "环境配置文件已创建，请根据需要修改 .env 文件"
    else
        log_warning "环境配置文件已存在，跳过创建"
    fi
    
    if [[ ! -f "frontend/.env" ]]; then
        cp frontend/.env.example frontend/.env
        log_success "前端环境配置文件已创建"
    fi
}

# 安装Git钩子
install_git_hooks() {
    log_info "安装Git钩子..."
    
    if [[ -f ".pre-commit-config.yaml" ]]; then
        if command_exists pre-commit; then
            pre-commit install
            log_success "Pre-commit钩子已安装"
        else
            log_warning "未找到pre-commit，跳过钩子安装"
        fi
    fi
}

# 数据库初始化
init_database() {
    log_info "初始化数据库..."
    
    # 检查数据库连接
    if [[ -f "scripts/init_db.py" ]]; then
        $PYTHON_CMD scripts/init_db.py
        log_success "数据库初始化完成"
    else
        log_warning "数据库初始化脚本不存在，跳过数据库初始化"
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试套件..."
    
    # Python测试
    if command_exists pytest; then
        pytest tests/ -v
        log_success "Python测试通过"
    fi
    
    # 前端测试
    if [[ -d "frontend" ]] && command_exists npm; then
        cd frontend
        npm run test
        cd ..
        log_success "前端测试通过"
    fi
}

# 生成文档
generate_docs() {
    log_info "生成项目文档..."
    
    if [[ -f "docs/Makefile" ]]; then
        cd docs
        make html
        cd ..
        log_success "文档生成完成"
    fi
}

# 显示项目信息
show_project_info() {
    echo ""
    echo "=========================================="
    echo "    GenAI模型能效评级体系项目"
    echo "=========================================="
    echo ""
    echo "项目设置完成！"
    echo ""
    echo "可用命令:"
    echo "  开发环境:"
    echo "    source venv/bin/activate      # 激活虚拟环境"
    echo "    python -m src.backend.main    # 启动后端服务"
    echo "    cd frontend && npm run dev    # 启动前端服务"
    echo ""
    echo "  Docker环境:"
    echo "    docker-compose up -d          # 启动所有服务"
    echo "    docker-compose logs -f        # 查看日志"
    echo "    docker-compose down           # 停止服务"
    echo ""
    echo "  测试:"
    echo "    pytest                        # 运行Python测试"
    echo "    cd frontend && npm test       # 运行前端测试"
    echo ""
    echo "  文档:"
    echo "    cd docs && make html          # 生成文档"
    echo ""
    echo "  代码质量:"
    echo "    black src/                    # 格式化Python代码"
    echo "    flake8 src/                   # 检查Python代码"
    echo "    cd frontend && npm run lint   # 检查前端代码"
    echo ""
    echo "配置文件:"
    echo "  .env                           # 后端环境配置"
    echo "  frontend/.env                  # 前端环境配置"
    echo "  docker-compose.yml             # Docker服务配置"
    echo ""
    echo "服务地址:"
    echo "  前端应用: http://localhost:3000"
    echo "  后端API: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
    echo "  任务监控: http://localhost:5555"
    echo "  Jupyter: http://localhost:8888"
    echo "  实验跟踪: http://localhost:5000"
    echo "  监控面板: http://localhost:3001"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    log_info "开始设置GenAI模型能效评级体系项目..."
    
    # 检查系统环境
    detect_os
    check_python
    check_nodejs
    check_docker
    
    # 创建项目结构
    create_directories
    create_virtual_env
    activate_virtual_env
    
    # 安装依赖
    install_python_deps
    install_frontend_deps
    
    # 初始化项目
    init_git_repo
    create_env_files
    install_git_hooks
    
    # 可选步骤
    if [[ "$SKIP_DB_INIT" != "true" ]]; then
        init_database
    fi
    
    if [[ "$SKIP_TESTS" != "true" ]]; then
        run_tests
    fi
    
    if [[ "$SKIP_DOCS" != "true" ]]; then
        generate_docs
    fi
    
    log_success "项目设置完成！"
    show_project_info
}

# 命令行参数解析
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-db-init)
            SKIP_DB_INIT=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-docs)
            SKIP_DOCS=true
            shift
            ;;
        --git-remote)
            GIT_REMOTE_URL="$2"
            shift 2
            ;;
        --help)
            echo "用法: $0 [选项]"
            echo ""
            echo "选项:"
            echo "  --skip-db-init     跳过数据库初始化"
            echo "  --skip-tests       跳过测试运行"
            echo "  --skip-docs        跳过文档生成"
            echo "  --git-remote URL   设置Git远程仓库地址"
            echo "  --help             显示此帮助信息"
            exit 0
            ;;
        *)
            log_error "未知选项: $1"
            exit 1
            ;;
    esac
done

# 运行主函数
main