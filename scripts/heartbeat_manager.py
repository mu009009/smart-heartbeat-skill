#!/usr/bin/env python3
# 🫀 智能心跳管理器
# 集成预测式心跳到HEARTBEAT检查系统

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

class HeartbeatManager:
    """心跳管理器 - 将预测式心跳集成到HEARTBEAT系统"""
    
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.state_file = self.workspace / "heartbeat_state.json"
        self.memory_dir = self.workspace / "memory"
        
        # 确保目录存在
        self.memory_dir.mkdir(exist_ok=True)
        
        # 加载状态
        self.state = self._load_state()
    
    def _load_state(self):
        """加载心跳状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 转换时间字符串为datetime
                    for key in ['last_user_message', 'last_heartbeat', 'next_heartbeat']:
                        if data.get(key):
                            data[key] = datetime.fromisoformat(data[key])
                    
                    # 添加缺失的字段
                    if 'heartbeat_interval' not in data:
                        data['heartbeat_interval'] = 3600
                    if 'mode' not in data:
                        data['mode'] = 'daytime'
                    
                    return data
            except Exception as e:
                print(f"⚠️ 加载心跳状态失败: {e}")
        
        # 默认状态
        return {
            "last_user_message": None,
            "last_heartbeat": None,
            "next_heartbeat": None,
            "heartbeat_interval": 3600,
            "mode": "daytime"
        }
    
    def _save_state(self):
        """保存心跳状态"""
        try:
            # 转换datetime为字符串
            state_to_save = self.state.copy()
            for key in ['last_user_message', 'last_heartbeat', 'next_heartbeat']:
                if state_to_save.get(key):
                    state_to_save[key] = state_to_save[key].isoformat()
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state_to_save, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"⚠️ 保存心跳状态失败: {e}")
            return False
    
    def _calculate_interval(self, current_time):
        """根据时间计算心跳间隔"""
        hour = current_time.hour
        if 0 <= hour < 6:  # 深夜 00:00-06:00
            return 3 * 3600  # 3小时
        else:  # 白天 06:00-24:00
            return 1 * 3600  # 1小时
    
    def _get_mode(self, hour):
        """获取当前模式"""
        return "nighttime" if 0 <= hour < 6 else "daytime"
    
    def update_on_user_message(self):
        """在用户发送消息时更新状态"""
        current_time = datetime.now()
        
        print(f"📨 更新用户消息时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 更新最后消息时间
        self.state['last_user_message'] = current_time
        
        # 计算当前间隔和模式
        current_interval = self._calculate_interval(current_time)
        current_mode = self._get_mode(current_time.hour)
        
        self.state['heartbeat_interval'] = current_interval
        self.state['mode'] = current_mode
        
        # 预测下次心跳时间
        self.state['next_heartbeat'] = current_time + timedelta(seconds=current_interval)
        
        # 保存状态
        self._save_state()
        
        # 记录到今日记忆
        self._log_to_memory("user_message", current_time)
        
        next_time = self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')
        print(f"✅ 已更新状态，下次心跳预测: {next_time}")
        
        return self.state['next_heartbeat']
    
    def should_send_heartbeat(self):
        """判断是否需要发送心跳"""
        current_time = datetime.now()
        
        print(f"🕐 当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 如果没有最后用户消息，使用当前时间
        if self.state['last_user_message'] is None:
            print("⚠️ 没有用户消息记录，使用当前时间")
            self.state['last_user_message'] = current_time
            current_interval = self._calculate_interval(current_time)
            self.state['next_heartbeat'] = current_time + timedelta(seconds=current_interval)
            self._save_state()
            return False
        
        # 如果没有预测的心跳时间，预测一个
        if self.state['next_heartbeat'] is None:
            print("⚠️ 没有预测的心跳时间，重新预测")
            current_interval = self._calculate_interval(self.state['last_user_message'])
            self.state['next_heartbeat'] = self.state['last_user_message'] + timedelta(seconds=current_interval)
            self._save_state()
        
        # 计算时间差
        time_since_last_message = current_time - self.state['last_user_message']
        time_since_last_heartbeat = None
        
        if self.state['last_heartbeat']:
            time_since_last_heartbeat = current_time - self.state['last_heartbeat']
        
        # 决策逻辑
        print(f"\n📊 决策分析:")
        print(f"  最后用户消息: {self.state['last_user_message'].strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  距上次消息: {time_since_last_message.total_seconds() // 60}分钟")
        
        if self.state['last_heartbeat']:
            print(f"  最后心跳: {self.state['last_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  距上次心跳: {time_since_last_heartbeat.total_seconds() // 60}分钟")
        
        print(f"  下次预测心跳: {self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 如果距最后消息 < 1小时，说明正在聊天
        if time_since_last_message.total_seconds() < 3600:
            print("  🔄 状态: 正在聊天 (<1小时)")
            return False
        
        # 2. 检查是否到了预测的心跳时间
        current_interval = self._calculate_interval(current_time)
        
        if time_since_last_message.total_seconds() >= current_interval:
            print(f"  ✅ 状态: 需要发送心跳 (≥{current_interval // 3600}小时)")
            return True
        else:
            # 还没到时间
            remaining = self.state['next_heartbeat'] - current_time
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            print(f"  ⏳ 状态: 无需心跳，剩余: {hours}小时{minutes}分钟")
            return False
    
    def send_heartbeat_report(self):
        """发送心跳报告"""
        current_time = datetime.now()
        
        print(f"🫀 发送心跳报告...")
        print(f"  时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 更新最后心跳时间
        self.state['last_heartbeat'] = current_time
        
        # 重新预测下次心跳
        current_interval = self._calculate_interval(current_time)
        current_mode = self._get_mode(current_time.hour)
        
        self.state['next_heartbeat'] = current_time + timedelta(seconds=current_interval)
        self.state['heartbeat_interval'] = current_interval
        self.state['mode'] = current_mode
        
        # 保存状态
        self._save_state()
        
        # 记录到今日记忆
        self._log_to_memory("heartbeat_sent", current_time)
        
        print(f"✅ 心跳报告已发送，更新下次预测时间")
        return True
    
    def _log_to_memory(self, event_type, timestamp):
        """记录到今日记忆文件"""
        today_file = self.memory_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        
        try:
            # 创建或打开今日记忆文件
            if not today_file.exists():
                with open(today_file, 'w', encoding='utf-8') as f:
                    f.write(f"# 🧠 记忆文件 - {datetime.now().strftime('%Y-%m-%d')}\n")
                    f.write(f"创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # 添加记录
            with open(today_file, 'a', encoding='utf-8') as f:
                if event_type == "user_message":
                    f.write("## 📨 用户消息记录\n")
                    f.write(f"- **时间**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"- **模式**: {self.state['mode']}\n")
                    f.write(f"- **间隔**: {self.state['heartbeat_interval'] // 3600}小时\n")
                    f.write(f"- **下次预测**: {self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                elif event_type == "heartbeat_sent":
                    f.write("## 🫀 心跳报告记录\n")
                    f.write(f"- **发送时间**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"- **模式**: {self.state['mode']}\n")
                    f.write(f"- **下次预测**: {self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            return True
            
        except Exception as e:
            print(f"⚠️ 记录到记忆文件失败: {e}")
            return False
    
    def get_heartbeat_summary(self):
        """获取心跳摘要"""
        summary = {
            "预测式心跳系统": "已激活",
            "当前模式": self.state['mode'],
            "心跳间隔": f"{self.state['heartbeat_interval'] // 3600}小时",
        }
        
        if self.state['last_user_message']:
            time_since = datetime.now() - self.state['last_user_message']
            summary["最后用户消息"] = {
                "时间": self.state['last_user_message'].strftime('%Y-%m-%d %H:%M:%S'),
                "距现在": f"{int(time_since.total_seconds() // 60)}分钟"
            }
        
        if self.state['next_heartbeat']:
            remaining = self.state['next_heartbeat'] - datetime.now()
            if remaining.total_seconds() > 0:
                summary["下次心跳预测"] = {
                    "时间": self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S'),
                    "剩余": f"{int(remaining.total_seconds() // 60)}分钟"
                }
        
        return summary
    
    def execute_heartbeat_check(self):
        """执行完整的心跳检查流程"""
        print("\n==========================================")
        print("🫀 智能心跳检查启动")
        print("==========================================")
        
        # 1. 检查是否需要发送心跳
        should_send = self.should_send_heartbeat()
        
        if should_send:
            # 2. 发送心跳报告
            self.send_heartbeat_report()
            
            print("\n✅ 心跳报告已发送")
            print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   模式: {self.state['mode']}")
            print(f"   间隔: {self.state['heartbeat_interval'] // 3600}小时")
            print(f"   下次预测: {self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 3. 记录到记忆
            self._log_to_memory("heartbeat_check_complete", datetime.now())
            
            return True
        else:
            print("\n⏳ 无需发送心跳")
            return False

def main():
    """主函数"""
    print("🫀 智能心跳管理器启动")
    
    manager = HeartbeatManager()
    
    try:
        # 执行心跳检查
        result = manager.execute_heartbeat_check()
        
        # 显示摘要
        print("\n📊 心跳系统摘要:")
        summary = manager.get_heartbeat_summary()
        
        for key, value in summary.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for sub_key, sub_value in value.items():
                    print(f"    {sub_key}: {sub_value}")
            else:
                print(f"  {key}: {value}")
        
        print(f"\n🎯 当前状态: {'心跳已发送' if result else '心跳已暂停'}")
        
    except Exception as e:
        print(f"\n❌ 心跳检查失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())