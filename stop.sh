#!/bin/bash

# VidVault 停止脚本
# 用于停止前后端服务

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

echo -e "${BLUE}🛑 停止 VidVault 服务...${NC}"

# 函数：停止指定端口的进程
stop_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti :$port >/dev/null 2>&1; then
        echo -e "${YELLOW}停止 $service_name (端口 $port)...${NC}"
        lsof -ti :$port | xargs kill -9 2>/dev/null || true
        sleep 1
        
        if ! lsof -ti :$port >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name 已停止${NC}"
        else
            echo -e "${RED}❌ $service_name 停止失败${NC}"
        fi
    else
        echo -e "${YELLOW}$service_name (端口 $port) 未在运行${NC}"
    fi
}

# 函数：通过PID文件停止进程
stop_by_pid() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "${YELLOW}通过PID停止 $service_name (PID: $pid)...${NC}"
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            
            # 如果进程还在运行，强制杀死
            if kill -0 "$pid" 2>/dev/null; then
                kill -9 "$pid" 2>/dev/null || true
                sleep 1
            fi
            
            if ! kill -0 "$pid" 2>/dev/null; then
                echo -e "${GREEN}✅ $service_name 已停止${NC}"
            else
                echo -e "${RED}❌ $service_name 停止失败${NC}"
            fi
        else
            echo -e "${YELLOW}$service_name PID文件存在但进程不在运行${NC}"
        fi
        rm -f "$pid_file"
    fi
}

# 停止后端服务
echo -e "${BLUE}停止后端服务...${NC}"
stop_by_pid "$BACKEND_DIR/backend.pid" "后端服务"
stop_port 8000 "后端API"

# 停止前端服务
echo -e "${BLUE}停止前端服务...${NC}"
stop_by_pid "$FRONTEND_DIR/frontend.pid" "前端服务"
stop_port 3000 "前端界面"

# 清理其他可能的进程
echo -e "${BLUE}清理相关进程...${NC}"

# 清理可能的 Python 进程
pkill -f "python.*main.py" 2>/dev/null || true

# 清理可能的 Node 进程
pkill -f "node.*react-scripts" 2>/dev/null || true
pkill -f "npm.*start" 2>/dev/null || true

# 等待一段时间让进程完全停止
sleep 2

# 最终检查
echo -e "${BLUE}📊 最终状态检查...${NC}"

if ! lsof -ti :8000 >/dev/null 2>&1; then
    echo -e "  • 后端API (端口 8000): ${GREEN}已停止${NC}"
else
    echo -e "  • 后端API (端口 8000): ${RED}仍在运行${NC}"
fi

if ! lsof -ti :3000 >/dev/null 2>&1; then
    echo -e "  • 前端界面 (端口 3000): ${GREEN}已停止${NC}"
else
    echo -e "  • 前端界面 (端口 3000): ${RED}仍在运行${NC}"
fi

echo ""
echo -e "${GREEN}🎉 VidVault 服务停止完成！${NC}"
echo ""
echo -e "${BLUE}💡 提示:${NC}"
echo -e "  • 重新启动: ${YELLOW}./start.sh${NC}"
echo -e "  • 检查状态: ${YELLOW}./start.sh status${NC}"