#!/bin/bash

# VidVault 启动脚本
# 用于启动前后端服务

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo -e "${BLUE}🚀 启动 VidVault 服务...${NC}"

# 检查必要的目录
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ 后端目录不存在: $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ 前端目录不存在: $FRONTEND_DIR${NC}"
    exit 1
fi

# 函数：清理已存在的进程
cleanup_processes() {
    echo -e "${YELLOW}🧹 清理已存在的进程...${NC}"
    
    # 清理后端进程
    if lsof -ti :8000 >/dev/null 2>&1; then
        echo -e "${YELLOW}停止后端服务 (端口 8000)...${NC}"
        lsof -ti :8000 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # 清理前端进程
    if lsof -ti :3000 >/dev/null 2>&1; then
        echo -e "${YELLOW}停止前端服务 (端口 3000)...${NC}"
        lsof -ti :3000 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# 函数：检查并创建后端虚拟环境
setup_backend() {
    echo -e "${BLUE}🔧 设置后端环境...${NC}"
    
    cd "$BACKEND_DIR"
    
    # 检查虚拟环境
    if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
        echo -e "${YELLOW}创建Python虚拟环境...${NC}"
        python3 -m venv venv
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ 创建虚拟环境失败${NC}"
            exit 1
        fi
    fi
    
    # 激活虚拟环境并安装依赖
    source venv/bin/activate
    
    echo -e "${YELLOW}安装Python依赖...${NC}"
    pip install --quiet fastapi uvicorn yt-dlp
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 安装Python依赖失败${NC}"
        exit 1
    fi
    
    # 检查必要文件
    if [ ! -f "main.py" ]; then
        echo -e "${RED}❌ 后端主文件 main.py 不存在${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 后端环境设置完成${NC}"
}

# 函数：检查前端依赖
setup_frontend() {
    echo -e "${BLUE}🔧 检查前端环境...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 检查 package.json
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ 前端 package.json 不存在${NC}"
        exit 1
    fi
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装前端依赖...${NC}"
        npm install
        if [ $? -ne 0 ]; then
            echo -e "${RED}❌ 安装前端依赖失败${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}✅ 前端环境检查完成${NC}"
}

# 函数：启动后端服务
start_backend() {
    echo -e "${BLUE}🚀 启动后端服务...${NC}"
    
    cd "$BACKEND_DIR"
    source venv/bin/activate
    
    # 在后台启动后端服务
    nohup python main.py > backend.log 2>&1 &
    BACKEND_PID=$!
    
    # 等待后端启动
    echo -e "${YELLOW}等待后端服务启动...${NC}"
    for i in {1..10}; do
        if curl -s http://localhost:8000/ >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 后端服务启动成功 (PID: $BACKEND_PID)${NC}"
            echo $BACKEND_PID > backend.pid
            return 0
        fi
        sleep 2
        echo -n "."
    done
    
    echo -e "${RED}❌ 后端服务启动失败${NC}"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
}

# 函数：启动前端服务
start_frontend() {
    echo -e "${BLUE}🚀 启动前端服务...${NC}"
    
    cd "$FRONTEND_DIR"
    
    # 在后台启动前端服务
    nohup npm start > frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # 等待前端启动
    echo -e "${YELLOW}等待前端服务启动...${NC}"
    for i in {1..20}; do
        if curl -s http://localhost:3000/ >/dev/null 2>&1; then
            echo -e "${GREEN}✅ 前端服务启动成功 (PID: $FRONTEND_PID)${NC}"
            echo $FRONTEND_PID > frontend.pid
            return 0
        fi
        sleep 3
        echo -n "."
    done
    
    echo -e "${YELLOW}⚠️  前端服务可能仍在启动中...${NC}"
    echo $FRONTEND_PID > frontend.pid
}

# 函数：显示状态信息
show_status() {
    echo ""
    echo -e "${GREEN}🎉 VidVault 服务启动完成！${NC}"
    echo ""
    echo -e "${BLUE}📊 服务状态:${NC}"
    echo -e "  • 后端API: ${GREEN}http://localhost:8000${NC}"
    echo -e "  • 前端界面: ${GREEN}http://localhost:3000${NC}"
    echo ""
    echo -e "${BLUE}📁 日志文件:${NC}"
    echo -e "  • 后端日志: ${YELLOW}$BACKEND_DIR/backend.log${NC}"
    echo -e "  • 前端日志: ${YELLOW}$FRONTEND_DIR/frontend.log${NC}"
    echo ""
    echo -e "${BLUE}🛑 停止服务:${NC}"
    echo -e "  • 运行: ${YELLOW}./stop.sh${NC}"
    echo -e "  • 或者: ${YELLOW}kill \$(cat backend/backend.pid) \$(cat frontend/frontend.pid)${NC}"
    echo ""
    echo -e "${BLUE}🔍 实时查看日志:${NC}"
    echo -e "  • 后端: ${YELLOW}tail -f backend/backend.log${NC}"
    echo -e "  • 前端: ${YELLOW}tail -f frontend/frontend.log${NC}"
}

# 主执行流程
main() {
    cleanup_processes
    setup_backend
    setup_frontend
    start_backend
    start_frontend
    show_status
}

# 捕获 Ctrl+C 信号
trap 'echo -e "\n${YELLOW}正在停止服务...${NC}"; cleanup_processes; exit 0' INT

# 检查命令行参数
case "${1:-}" in
    "stop")
        cleanup_processes
        echo -e "${GREEN}✅ 服务已停止${NC}"
        exit 0
        ;;
    "status")
        echo -e "${BLUE}📊 检查服务状态...${NC}"
        if curl -s http://localhost:8000/ >/dev/null 2>&1; then
            echo -e "  • 后端API: ${GREEN}运行中${NC} (http://localhost:8000)"
        else
            echo -e "  • 后端API: ${RED}未运行${NC}"
        fi
        
        if curl -s http://localhost:3000/ >/dev/null 2>&1; then
            echo -e "  • 前端界面: ${GREEN}运行中${NC} (http://localhost:3000)"
        else
            echo -e "  • 前端界面: ${RED}未运行${NC}"
        fi
        exit 0
        ;;
    "help"|"-h"|"--help")
        echo -e "${BLUE}VidVault 启动脚本${NC}"
        echo ""
        echo -e "${YELLOW}用法:${NC}"
        echo -e "  ./start.sh          - 启动所有服务"
        echo -e "  ./start.sh stop     - 停止所有服务"
        echo -e "  ./start.sh status   - 检查服务状态"
        echo -e "  ./start.sh help     - 显示此帮助信息"
        exit 0
        ;;
esac

# 执行主函数
main