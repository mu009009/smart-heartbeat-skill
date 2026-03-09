#!/usr/bin/env python3
# 🔄 立即更新心跳状态 - 修复时间戳问题

import json
from datetime import datetime, timedelta
from pathlib import Path

def main():
    workspace = Path("/root/.openclaw/workspace")
    state_file = workspace / "smart_heartbeat_v2_state.json"
    
    # 获取当前时间（UTC）
    current_time = datetime.utcnow()
    
    # 计算下次心跳时间（假设白天模式，1小时后）
    next_heartbeat = current_time + timedelta(hours=1)
    
    # 更新状态
    state = {
        "last_user_message": current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        "last_heartbeat": None,  # 刚刚更新，还没发送心跳
        "next_heartbeat": next_heartbeat.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
        "heartbeat_count": 0,
        "mode": "daytime"
    }
    
    # 保存状态
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 心跳状态已更新")
    print(f"   最后用户消息: {state['last_user_message']}")
    print(f"   下次心跳预测: {state['next_heartbeat']}")
    print(f"   模式: {state['mode']}")

if __name__ == "__main__":
    main()