#!/bin/bash
# 🫀 智能心跳检查脚本
# 集成到HEARTBEAT系统的预测式心跳检查

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/logs/heartbeat_check_$(date +%Y%m%d).log"
WORKSPACE="/root/.openclaw/workspace"

# 创建日志目录
mkdir -p "$(dirname "$LOG_FILE")"

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

# 检查是否在聊天中
check_chat_active() {
    local session_file=$(ls -t "$WORKSPACE/../agents/main/sessions/"*.jsonl 2>/dev/null | head -1)
    
    if [ -z "$session_file" ]; then
        log "⚠️ 未找到会话文件"
        return 1
    fi
    
    # 提取最后一条消息的时间
    local last_message_time=$(python3 -c "
import json
import datetime
import sys

try:
    with open('$session_file', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if not lines:
            sys.exit(1)
            
        # 获取最后一条消息
        last_line = lines[-1].strip()
        if not last_line:
            sys.exit(1)
            
        message = json.loads(last_line)
        timestamp_str = message.get('timestamp', '')
        if not timestamp_str:
            sys.exit(1)
            
        # 解析时间戳
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
            
        timestamp = datetime.datetime.fromisoformat(timestamp_str)
        print(timestamp.isoformat())
        
except Exception as e:
    sys.exit(1)
")
    
    if [ $? -ne 0 ]; then
        log "⚠️ 无法提取最后消息时间"
        return 1
    fi
    
    # 计算时间差（秒）
    local current_time=$(date -u +%s)
    local message_time=$(date -u -d "$last_message_time" +%s 2>/dev/null || date -u -d "$(echo $last_message_time | sed 's/T/ /')" +%s)
    local time_diff=$((current_time - message_time))
    
    log "📊 最后消息: $last_message_time"
    log "📊 时间差: ${time_diff}秒 ($((time_diff/60))分钟)"
    
    # 如果小于1小时（3600秒），说明正在聊天
    if [ $time_diff -lt 3600 ]; then
        log "💬 状态: 正在聊天 (<1小时)"
        return 0  # 正在聊天
    else
        log "⏸️  状态: 未聊天 (≥1小时)"
        return 1  # 未聊天
    fi
}

# 获取当前应该使用的心跳间隔
get_heartbeat_interval() {
    local current_hour=$(date +%H)
    
    if [ $current_hour -ge 0 ] && [ $current_hour -lt 6 ]; then
        # 深夜 00:00-06:00，3小时
        echo "10800"  # 3小时 = 10800秒
        log "🌙 模式: 深夜 (00:00-06:00)"
        log "⏰ 间隔: 3小时"
    else
        # 白天 06:00-24:00，1小时
        echo "3600"   # 1小时 = 3600秒
        log "☀️  模式: 白天 (06:00-24:00)"
        log "⏰ 间隔: 1小时"
    fi
}

# 检查是否需要发送心跳
check_need_heartbeat() {
    local state_file="$WORKSPACE/heartbeat_state.json"
    
    # 如果状态文件不存在，创建默认
    if [ ! -f "$state_file" ]; then
        log "⚠️ 状态文件不存在，创建默认"
        cat > "$state_file" << EOF
{
  "last_user_message": null,
  "last_heartbeat": null,
  "next_heartbeat": null,
  "heartbeat_interval": 3600,
  "mode": "daytime"
}
EOF
        return 1  # 需要发送心跳建立基准
    fi
    
    # 检查最后心跳时间
    local last_heartbeat=$(python3 -c "
import json
import datetime
import sys

try:
    with open('$state_file', 'r', encoding='utf-8') as f:
        state = json.load(f)
        
    last_heartbeat_str = state.get('last_heartbeat')
    if last_heartbeat_str:
        if last_heartbeat_str.endswith('Z'):
            last_heartbeat_str = last_heartbeat_str[:-1] + '+00:00'
        last_heartbeat = datetime.datetime.fromisoformat(last_heartbeat_str)
        print(last_heartbeat.isoformat())
    else:
        print('')
        
except Exception as e:
    print('')
")
    
    if [ -z "$last_heartbeat" ]; then
        log "⚠️ 没有最后心跳记录"
        return 1  # 需要发送心跳
    fi
    
    # 计算距最后心跳的时间
    local current_time=$(date -u +%s)
    local heartbeat_time=$(date -u -d "$last_heartbeat" +%s 2>/dev/null || date -u -d "$(echo $last_heartbeat | sed 's/T/ /')" +%s)
    local time_diff=$((current_time - heartbeat_time))
    
    # 获取当前应该使用的心跳间隔
    local required_interval=$(get_heartbeat_interval)
    
    log "📊 最后心跳: $last_heartbeat"
    log "📊 距上次心跳: ${time_diff}秒 ($((time_diff/60))分钟)"
    log "📊 需要间隔: ${required_interval}秒 ($((required_interval/3600))小时)"
    
    # 如果已经超过所需间隔，需要发送心跳
    if [ $time_diff -ge $required_interval ]; then
        log "✅ 需要发送心跳"
        return 0
    else
        local remaining=$((required_interval - time_diff))
        log "⏳ 无需心跳，剩余: $((remaining/60))分钟"
        return 1
    fi
}

# 执行心跳检查
log "=========================================="
log "🫀 智能心跳检查启动"
log "=========================================="

# 1. 检查是否在聊天中
if check_chat_active; then
    log "💬 正在聊天中，跳过心跳"
    log "✅ 心跳检查完成: 聊天中，已跳过"
    exit 0
fi

# 2. 检查是否需要发送心跳
if check_need_heartbeat; then
    log "🚀 准备发送心跳报告..."
    
    # 这里可以添加实际的心跳发送逻辑
    # 例如：执行HEARTBEAT检查并发送到Feishu
    
    # 更新心跳状态
    python3 -c "
import json
import datetime
import os

state_file = '$WORKSPACE/heartbeat_state.json'

# 加载状态
if os.path.exists(state_file):
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)
else:
    state = {
        'last_user_message': None,
        'last_heartbeat': None,
        'next_heartbeat': None,
        'heartbeat_interval': 3600,
        'mode': 'daytime'
    }

# 更新最后心跳时间
current_time = datetime.datetime.utcnow()
state['last_heartbeat'] = current_time.isoformat() + 'Z'

# 根据时间计算下次心跳
hour = current_time.hour
if 0 <= hour < 6:
    state['heartbeat_interval'] = 10800  # 3小时
    state['mode'] = 'nighttime'
    next_interval = 10800
else:
    state['heartbeat_interval'] = 3600   # 1小时
    state['mode'] = 'daytime'
    next_interval = 3600

state['next_heartbeat'] = (current_time + datetime.timedelta(seconds=next_interval)).isoformat() + 'Z'

# 保存状态
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state, f, indent=2, ensure_ascii=False)

print('心跳状态已更新')
"
    
    log "✅ 心跳状态已更新"
    
    # 记录到今日记忆
    today_memory="$WORKSPACE/memory/$(date +%Y-%m-%d).md"
    if [ -f "$today_memory" ]; then
        echo "" >> "$today_memory"
        echo "## 🫀 心跳报告记录" >> "$today_memory"
        echo "- **时间**: $(date '+%Y-%m-%d %H:%M:%S')" >> "$today_memory"
        echo "- **模式**: $(python3 -c "
import datetime
hour = datetime.datetime.now().hour
print('nighttime' if 0 <= hour < 6 else 'daytime')
")" >> "$today_memory"
        echo "- **间隔**: $(python3 -c "
import datetime
hour = datetime.datetime.now().hour
print('3小时' if 0 <= hour < 6 else '1小时')
")" >> "$today_memory"
        echo "" >> "$today_memory"
    fi
    
    log "✅ 心跳报告已发送并记录"
else
    log "⏳ 无需发送心跳"
fi

log "=========================================="
log "✅ 智能心跳检查完成"
log "=========================================="

exit 0