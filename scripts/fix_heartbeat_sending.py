#!/usr/bin/env python3
# 🔧 修复心跳发送问题
# 问题：手动HEARTBEAT检查时，即使智能心跳判断"不发送"，仍然发送了详细报告

import json
from datetime import datetime, timedelta
from pathlib import Path

class HeartbeatSendFixer:
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.state_file = self.workspace / "smart_heartbeat_v2_state.json"
        
    def load_state(self):
        """加载心跳状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return {}
    
    def parse_time(self, time_str):
        """解析时间字符串"""
        if not time_str:
            return None
        
        try:
            if time_str.endswith('Z'):
                time_str = time_str[:-1] + '+00:00'
            dt = datetime.fromisoformat(time_str)
            return dt.replace(tzinfo=None)
        except:
            return None
    
    def should_send_heartbeat_manually(self):
        """判断手动HEARTBEAT检查时是否应该发送报告"""
        state = self.load_state()
        
        # 如果没有状态信息，需要发送以建立基准
        if not state or 'last_user_message' not in state:
            print("⚠️ 没有心跳状态信息，需要发送建立基准")
            return True
        
        last_message_time = self.parse_time(state['last_user_message'])
        current_time = datetime.utcnow()
        
        if not last_message_time:
            print("⚠️ 无法解析最后消息时间")
            return True
        
        # 计算距最后消息的时间
        time_since_last_message = current_time - last_message_time
        
        # 规则：如果正在聊天（最后消息<1小时），不发送
        if time_since_last_message.total_seconds() < 3600:
            print(f"💬 正在聊天中 ({int(time_since_last_message.total_seconds()/60)}分钟)，不发送心跳报告")
            return False
        
        # 规则：如果空闲超过1小时，发送
        print(f"⏰ 空闲中 ({int(time_since_last_message.total_seconds()/60)}分钟)，需要发送心跳报告")
        return True
    
    def update_user_message_time(self):
        """更新用户消息时间（当用户发送消息时调用）"""
        current_time = datetime.utcnow()
        time_str = current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        state = self.load_state()
        state['last_user_message'] = time_str
        
        # 更新下次心跳预测（当前时间 + 1小时）
        next_heartbeat = current_time + timedelta(hours=1)
        state['next_heartbeat'] = next_heartbeat.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        # 保存状态
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"📨 更新用户消息时间: {time_str}")
        print(f"⏰ 下次心跳预测: {state['next_heartbeat']}")
        
        return True

def main():
    fixer = HeartbeatSendFixer()
    
    print("🔧 心跳发送问题修复工具")
    print("=" * 40)
    
    # 检查当前状态
    state = fixer.load_state()
    print("📊 当前心跳状态:")
    print(f"   最后用户消息: {state.get('last_user_message', '无')}")
    print(f"   下次心跳预测: {state.get('next_heartbeat', '无')}")
    
    # 判断是否应该发送
    should_send = fixer.should_send_heartbeat_manually()
    
    print("\n🎯 手动HEARTBEAT检查决策:")
    if should_send:
        print("   ✅ 应该发送心跳报告")
        print("   💡 建议：发送简洁报告 (<200字符)")
    else:
        print("   ❌ 不应该发送心跳报告")
        print("   💡 建议：只回复 HEARTBEAT_OK")
    
    # 更新用户消息时间（模拟用户发送消息）
    print("\n🔄 更新用户消息时间（模拟用户发送消息）:")
    fixer.update_user_message_time()
    
    # 再次检查
    print("\n🔄 再次检查决策:")
    should_send_now = fixer.should_send_heartbeat_manually()
    if should_send_now:
        print("   ✅ 现在应该发送心跳报告")
    else:
        print("   ❌ 现在不应该发送心跳报告（刚更新了消息时间）")

if __name__ == "__main__":
    main()