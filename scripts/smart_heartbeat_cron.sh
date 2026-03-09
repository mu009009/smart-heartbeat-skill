#!/bin/bash
# 🫀 智能心跳系统cron脚本
# 每分钟检查一次，但只在需要时发送心跳

WORKSPACE="/root/.openclaw/workspace"
LOG_FILE="$WORKSPACE/logs/smart_heartbeat.log"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

log "=========================================="
log "🫀 智能心跳系统检查启动"
log "=========================================="

# 运行智能心跳系统
cd "$WORKSPACE"
log "执行智能心跳检查..."

# 运行修复后的心跳系统
python3 fixed_smart_heartbeat.py auto 2>&1 | while read -r line; do
    log "  $line"
done

log "✅ 智能心跳检查完成"
log "=========================================="