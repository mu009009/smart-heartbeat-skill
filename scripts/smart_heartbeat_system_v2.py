#!/usr/bin/env python3
# 🫀 智能心跳系统 v2.0 - 完全符合Claudius要求
# 规则: 
# 1. 心跳只在我最后一次回复后，超过1小时没有消息的情况下才发出
# 2. 发出后如果还是没有回复，再等待1小时后发出（00:00-6:00期间为再等待3小时）
# 3. 心跳报告之间的间隔至少都在1个小时以上
# 4. 心跳发送时间应随着聊天刷新而刷新

import os
import json
import time
import sys
from datetime import datetime, timedelta
from pathlib import Path

class SmartHeartbeatSystemV2:
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.state_file = self.workspace / "smart_heartbeat_v2_state.json"
        self.memory_dir = self.workspace / "memory"
        
    def get_current_time(self):
        """获取当前时间（UTC）"""
        return datetime.utcnow()
    
    def get_current_hour_shanghai(self):
        """获取上海时区的小时（用于判断深夜模式）"""
        # 简单实现：UTC+8
        utc_hour = datetime.utcnow().hour
        shanghai_hour = (utc_hour + 8) % 24
        return shanghai_hour
    
    def is_nighttime(self):
        """判断是否为深夜（00:00-06:00 上海时间）"""
        hour = self.get_current_hour_shanghai()
        return 0 <= hour < 6
    
    def get_heartbeat_interval(self):
        """获取心跳间隔（秒）"""
        if self.is_nighttime():
            return 3 * 3600  # 3小时
        else:
            return 1 * 3600  # 1小时
    
    def load_state(self):
        """加载心跳状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载状态失败: {e}")
        
        # 默认状态
        return {
            "last_user_message": None,      # 用户最后消息时间
            "last_heartbeat": None,         # 最后心跳时间
            "next_heartbeat": None,         # 下次心跳预测时间
            "heartbeat_count": 0,           # 心跳次数
            "mode": "daytime" if not self.is_nighttime() else "nighttime"
        }
    
    def save_state(self, state):
        """保存心跳状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 保存状态失败: {e}")
            return False
    
    def parse_time(self, time_str):
        """解析时间字符串"""
        if not time_str:
            return None
        
        try:
            if time_str.endswith('Z'):
                time_str = time_str[:-1] + '+00:00'
            return datetime.fromisoformat(time_str)
        except Exception as e:
            print(f"❌ 解析时间失败 {time_str}: {e}")
            return None
    
    def format_time(self, dt):
        """格式化时间为字符串"""
        if dt is None:
            return None
        return dt.isoformat() + 'Z'
    
    def get_last_user_message_time(self):
        """获取用户最后消息时间"""
        # 从OpenClaw会话文件中获取
        session_file = self.workspace / "session.jsonl"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # 从最后开始查找用户消息
            for line in reversed(lines):
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    role = data.get('role', '')
                    timestamp = data.get('timestamp', '')
                    
                    if role == 'user' and timestamp:
                        return self.parse_time(timestamp)
                except:
                    continue
                    
        except Exception as e:
            print(f"❌ 读取会话文件失败: {e}")
        
        return None
    
    def update_on_user_message(self, message_time=None):
        """当用户发送消息时更新状态"""
        current_time = self.get_current_time()
        
        if message_time is None:
            message_time = current_time
        
        state = self.load_state()
        
        # 更新最后用户消息时间
        state['last_user_message'] = self.format_time(message_time)
        
        # 重新计算下次心跳时间（消息时间 + 间隔）
        interval = self.get_heartbeat_interval()
        state['next_heartbeat'] = self.format_time(message_time + timedelta(seconds=interval))
        
        # 更新模式
        state['mode'] = "nighttime" if self.is_nighttime() else "daytime"
        
        self.save_state(state)
        
        print(f"📨 更新用户消息时间: {self.format_time(message_time)}")
        print(f"⏰ 下次心跳预测: {state['next_heartbeat']}")
        
        return True
    
    def should_send_heartbeat(self):
        """判断是否需要发送心跳"""
        state = self.load_state()
        current_time = self.get_current_time()
        
        # 如果没有用户消息记录，需要发送心跳建立基准
        if not state['last_user_message']:
            print("⚠️ 没有用户消息记录，需要发送心跳建立基准")
            return True
        
        last_message_time = self.parse_time(state['last_user_message'])
        next_heartbeat_time = self.parse_time(state['next_heartbeat'])
        
        if not last_message_time:
            print("⚠️ 无法解析最后消息时间")
            return True
        
        # 计算距最后消息的时间
        time_since_last_message = current_time - last_message_time
        
        print(f"📊 状态分析:")
        print(f"  最后用户消息: {self.format_time(last_message_time)}")
        print(f"  距上次消息: {time_since_last_message.total_seconds() // 60}分钟")
        
        if state['last_heartbeat']:
            last_heartbeat_time = self.parse_time(state['last_heartbeat'])
            time_since_last_heartbeat = current_time - last_heartbeat_time
            print(f"  最后心跳: {self.format_time(last_heartbeat_time)}")
            print(f"  距上次心跳: {time_since_last_heartbeat.total_seconds() // 60}分钟")
        
        if next_heartbeat_time:
            print(f"  下次心跳预测: {self.format_time(next_heartbeat_time)}")
        
        # 规则1: 如果正在聊天（最后消息<1小时），不发送心跳
        if time_since_last_message.total_seconds() < 3600:
            print("💬 状态: 正在聊天 (<1小时)，不发送心跳")
            return False
        
        # 规则2: 检查是否到了预测的心跳时间
        if next_heartbeat_time and current_time >= next_heartbeat_time:
            print(f"✅ 状态: 需要发送心跳 (已超过预测时间)")
            return True
        
        # 规则3: 如果还没有预测时间，创建预测
        if not state['next_heartbeat']:
            interval = self.get_heartbeat_interval()
            next_time = last_message_time + timedelta(seconds=interval)
            state['next_heartbeat'] = self.format_time(next_time)
            self.save_state(state)
            print(f"⏰ 创建心跳预测: {state['next_heartbeat']}")
            return False
        
        # 还没到时间
        remaining = next_heartbeat_time - current_time
        minutes = remaining.total_seconds() // 60
        print(f"⏳ 状态: 无需心跳，剩余: {minutes}分钟")
        return False
    
    def send_heartbeat_report(self):
        """发送心跳报告"""
        current_time = self.get_current_time()
        
        print("🫀 发送心跳报告...")
        print(f"  时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  模式: {'深夜' if self.is_nighttime() else '白天'}")
        print(f"  间隔: {self.get_heartbeat_interval() // 3600}小时")
        
        # 更新状态
        state = self.load_state()
        state['last_heartbeat'] = self.format_time(current_time)
        state['heartbeat_count'] = state.get('heartbeat_count', 0) + 1
        
        # 预测下次心跳时间（当前时间 + 间隔）
        interval = self.get_heartbeat_interval()
        state['next_heartbeat'] = self.format_time(current_time + timedelta(seconds=interval))
        
        self.save_state(state)
        
        # 记录到记忆文件
        self.log_to_memory(current_time)
        
        print(f"✅ 心跳报告已发送")
        print(f"📊 下次心跳预测: {state['next_heartbeat']}")
        
        return True
    
    def log_to_memory(self, heartbeat_time):
        """记录心跳到记忆文件"""
        try:
            today_file = self.memory_dir / f"{heartbeat_time.strftime('%Y-%m-%d')}.md"
            
            log_entry = f"\n## 🫀 智能心跳报告 {heartbeat_time.strftime('%H:%M:%S')}\n"
            log_entry += f"- **模式**: {'深夜 (00:00-06:00)' if self.is_nighttime() else '白天 (06:00-24:00)'}\n"
            log_entry += f"- **间隔**: {self.get_heartbeat_interval() // 3600}小时\n"
            log_entry += f"- **原因**: 用户未响应超过{self.get_heartbeat_interval() // 3600}小时\n"
            log_entry += f"- **计数**: {self.load_state().get('heartbeat_count', 0)}\n"
            
            with open(today_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"⚠️ 记录到记忆文件失败: {e}")
    
    def run_check(self):
        """执行完整的心跳检查"""
        print("==========================================")
        print("🫀 智能心跳系统 v2.0 检查")
        print("==========================================")
        
        print(f"🕐 当前时间: {self.get_current_time().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌙 模式: {'深夜 (00:00-06:00)' if self.is_nighttime() else '白天 (06:00-24:00)'}")
        print(f"⏰ 间隔: {self.get_heartbeat_interval() // 3600}小时")
        
        # 检查是否需要发送心跳
        if self.should_send_heartbeat():
            self.send_heartbeat_report()
            return True
        else:
            print("\n⏳ 无需发送心跳")
            return False
    
    def reset_system(self):
        """重置心跳系统"""
        state = {
            "last_user_message": None,
            "last_heartbeat": None,
            "next_heartbeat": None,
            "heartbeat_count": 0,
            "mode": "daytime" if not self.is_nighttime() else "nighttime"
        }
        
        self.save_state(state)
        print("✅ 心跳系统已重置")
        return True

def main():
    """主函数"""
    system = SmartHeartbeatSystemV2()
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            # 执行检查
            system.run_check()
            
        elif command == "update":
            # 更新用户消息时间
            system.update_on_user_message()
            
        elif command == "reset":
            # 重置系统
            system.reset_system()
            
        elif command == "status":
            # 显示状态
            state = system.load_state()
            print("📊 心跳系统状态:")
            print(f"  最后用户消息: {state.get('last_user_message')}")
            print(f"  最后心跳: {state.get('last_heartbeat')}")
            print(f"  下次心跳预测: {state.get('next_heartbeat')}")
            print(f"  心跳次数: {state.get('heartbeat_count', 0)}")
            print(f"  模式: {state.get('mode')}")
            
        elif command == "auto":
            # 自动模式：检查用户消息并运行
            last_message = system.get_last_user_message_time()
            if last_message:
                system.update_on_user_message(last_message)
            system.run_check()
            
        else:
            print(f"❌ 未知命令: {command}")
            print("可用命令: check, update, reset, status, auto")
    else:
        # 默认执行自动模式
        last_message = system.get_last_user_message_time()
        if last_message:
            system.update_on_user_message(last_message)
        system.run_check()

if __name__ == "__main__":
    main()