#!/usr/bin/env python3
# 🫀 智能心跳检查 - 真正的HEARTBEAT检查脚本
# 静默模式，符合HEARTBEAT规则

import sys
import os
from datetime import datetime, timedelta
import json

# 添加路径
sys.path.append('/root/.openclaw/workspace')
try:
    from heartbeat_manager import HeartbeatManager
    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False

def check_last_user_message_time():
    """检查最后用户消息时间（备用方法）"""
    state_file = "/root/.openclaw/workspace/heartbeat_state.json"
    
    if not os.path.exists(state_file):
        return None
    
    try:
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        last_message_str = state.get('last_user_message')
        if not last_message_str:
            return None
        
        # 解析时间字符串（处理时区）
        if last_message_str.endswith('Z'):
            last_message_str = last_message_str[:-1] + '+00:00'
        
        # 转换为UTC时间，然后转换为naive时间以便比较
        parsed_time = datetime.fromisoformat(last_message_str)
        
        # 如果是aware时间，转换为naive
        if parsed_time.tzinfo is not None:
            parsed_time = parsed_time.replace(tzinfo=None)
        
        return parsed_time
        
    except Exception as e:
        print(f"⚠️ 检查用户消息时间失败: {e}", file=sys.stderr)
        return None

def calculate_interval(current_time):
    """根据时间计算心跳间隔"""
    hour = current_time.hour
    if 0 <= hour < 6:  # 深夜 00:00-06:00
        return 3 * 3600  # 3小时
    else:  # 白天 06:00-24:00
        return 1 * 3600  # 1小时

def main():
    """主函数 - 静默执行HEARTBEAT检查"""
    
    # 1. 检查是否在聊天中（最后消息<1小时）
    last_message_time = check_last_user_message_time()
    current_time = datetime.now()
    
    if last_message_time:
        # 确保两个时间都是naive（无时区）
        if last_message_time.tzinfo is not None:
            last_message_time = last_message_time.replace(tzinfo=None)
        
        time_since_last_message = current_time - last_message_time
        
        # 如果最后消息<1小时，说明正在聊天
        if time_since_last_message.total_seconds() < 3600:
            # 静默返回HEARTBEAT_OK（不打印任何内容）
            sys.exit(0)  # 退出码0表示HEARTBEAT_OK
    
    # 2. 检查是否需要发送心跳（基于最后消息时间）
    if last_message_time:
        # 确保时间是naive（无时区）
        if last_message_time.tzinfo is not None:
            last_message_time = last_message_time.replace(tzinfo=None)
        
        # 计算当前应该使用的间隔
        required_interval = calculate_interval(current_time)
        
        # 如果距最后消息≥所需间隔，需要心跳
        time_since_last_message = current_time - last_message_time
        if time_since_last_message.total_seconds() >= required_interval:
            # 需要发送心跳
            # 更新状态文件
            state_file = "/root/.openclaw/workspace/heartbeat_state.json"
            
            try:
                if os.path.exists(state_file):
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                else:
                    state = {
                        "last_user_message": None,
                        "last_heartbeat": None,
                        "next_heartbeat": None,
                        "heartbeat_interval": 3600,
                        "mode": "daytime"
                    }
                
                # 更新最后心跳时间
                state['last_heartbeat'] = current_time.isoformat() + 'Z'
                
                # 根据时间计算下次心跳
                hour = current_time.hour
                if 0 <= hour < 6:
                    state['heartbeat_interval'] = 10800
                    state['mode'] = 'nighttime'
                    next_interval = 10800
                else:
                    state['heartbeat_interval'] = 3600
                    state['mode'] = 'daytime'
                    next_interval = 3600
                
                state['next_heartbeat'] = (current_time + timedelta(seconds=next_interval)).isoformat() + 'Z'
                
                # 保存状态
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, indent=2, ensure_ascii=False)
                
                # 记录到今日记忆
                today_memory = f"/root/.openclaw/workspace/memory/{current_time.strftime('%Y-%m-%d')}.md"
                if os.path.exists(today_memory):
                    with open(today_memory, 'a', encoding='utf-8') as f:
                        f.write("\n## 🫀 心跳报告记录\n")
                        f.write(f"- **时间**: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"- **模式**: {'nighttime' if 0 <= hour < 6 else 'daytime'}\n")
                        f.write(f"- **间隔**: {next_interval // 3600}小时\n")
                        f.write("\n")
                
                # 需要发送心跳报告
                print("🫀 Smart Heartbeat Check: Reminder needed")
                sys.exit(2)  # 退出码2表示需要发送心跳
                
            except Exception as e:
                print(f"❌ 更新心跳状态失败: {e}", file=sys.stderr)
                sys.exit(1)
    
    # 3. 默认情况：无需心跳
    # 静默返回HEARTBEAT_OK
    sys.exit(0)

if __name__ == "__main__":
    main()