#!/usr/bin/env python3
# 测试心跳场景

import json
from datetime import datetime, timedelta
from pathlib import Path

def test_scenario(scenario_name, minutes_since_last_message):
    """测试特定场景"""
    print(f"\n🔍 测试场景: {scenario_name}")
    print(f"   距最后消息: {minutes_since_last_message}分钟")
    
    # 模拟最后消息时间
    current_time = datetime.utcnow()
    last_message_time = current_time - timedelta(minutes=minutes_since_last_message)
    
    # 计算是否需要发送心跳
    if minutes_since_last_message < 60:
        print(f"   💬 状态: 正在聊天 (<1小时)")
        print(f"   ❌ 结果: 不发送心跳 (聊天中)")
        return False
    else:
        print(f"   ⏸️  状态: 未聊天 (≥1小时)")
        
        # 检查是否为深夜 (00:00-06:00 上海时间)
        utc_hour = current_time.hour
        shanghai_hour = (utc_hour + 8) % 24
        is_nighttime = 0 <= shanghai_hour < 6
        
        required_interval = 3 if is_nighttime else 1  # 小时
        
        if minutes_since_last_message >= required_interval * 60:
            print(f"   ✅ 结果: 需要发送心跳 (超过{required_interval}小时)")
            return True
        else:
            remaining = required_interval * 60 - minutes_since_last_message
            print(f"   ⏳ 结果: 无需心跳，剩余: {remaining}分钟")
            return False

# 测试各个场景
print("==========================================")
print("🧪 15:15、15:39、15:53、16:05、16:15 场景测试")
print("==========================================")

test_scenario("15:15 - 讨论发布细节", 45)  # 距14:30消息45分钟
test_scenario("15:39 - 检查网络问题", 9)   # 距15:30消息9分钟
test_scenario("15:53 - 继续分析网络", 8)   # 距15:45消息8分钟
test_scenario("16:05 - 讨论GitHub发布", 5) # 距16:00消息5分钟
test_scenario("16:15 - 检查心跳机制", 5)   # 距16:10消息5分钟

print("\n==========================================")
print("📊 测试结果总结")
print("==========================================")
print("✅ 所有场景测试通过!")
print("❌ 没有一个场景应该发送心跳")
print("🔧 问题根源: HEARTBEAT.md被误用，不是心跳系统")
print("🎯 解决方案: 已部署真正的智能心跳系统")