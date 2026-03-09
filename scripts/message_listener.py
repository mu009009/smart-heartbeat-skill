#!/usr/bin/env python3
# 👂 消息监听器
# 监听用户消息并更新心跳预测

import json
import os
import time
import threading
from datetime import datetime
from pathlib import Path

class MessageListener:
    """消息监听器 - 监听用户消息并触发心跳更新"""
    
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.sessions_dir = Path("/root/.openclaw/agents/main/sessions")
        self.state_file = self.workspace / "heartbeat_state.json"
        
        # 上次检查的时间
        self.last_check_time = None
        self.last_message_count = 0
        
        # 心跳管理器导入
        sys.path.append(str(self.workspace))
        from heartbeat_manager import HeartbeatManager
        self.heartbeat_manager = HeartbeatManager()
    
    def get_latest_session_file(self):
        """获取最新的会话文件"""
        try:
            session_files = list(self.sessions_dir.glob("*.jsonl"))
            if not session_files:
                return None
            
            # 按修改时间排序，获取最新的
            latest_file = max(session_files, key=lambda x: x.stat().st_mtime)
            return latest_file
        except Exception as e:
            print(f"⚠️ 获取会话文件失败: {e}")
            return None
    
    def extract_user_messages(self, session_file):
        """从会话文件中提取用户消息"""
        try:
            if not session_file or not session_file.exists():
                return []
            
            user_messages = []
            
            with open(session_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        message = json.loads(line)
                        
                        # 检查是否是用户消息
                        if message.get('role') == 'user':
                            # 提取时间戳
                            timestamp_str = message.get('timestamp')
                            if timestamp_str:
                                try:
                                    # 解析时间戳
                                    if timestamp_str.endswith('Z'):
                                        timestamp_str = timestamp_str[:-1] + '+00:00'
                                    
                                    timestamp = datetime.fromisoformat(timestamp_str)
                                    user_messages.append({
                                        'time': timestamp,
                                        'content': message.get('content', '')[:100]  # 只取前100字符
                                    })
                                except Exception as e:
                                    print(f"⚠️ 解析时间戳失败: {e}")
                                    continue
                        
                    except json.JSONDecodeError:
                        continue
            
            return user_messages
            
        except Exception as e:
            print(f"⚠️ 提取用户消息失败: {e}")
            return []
    
    def get_last_user_message_time(self):
        """获取最后一条用户消息的时间"""
        session_file = self.get_latest_session_file()
        if not session_file:
            return None
        
        user_messages = self.extract_user_messages(session_file)
        if not user_messages:
            return None
        
        # 获取最新的用户消息
        latest_message = max(user_messages, key=lambda x: x['time'])
        return latest_message['time']
    
    def check_for_new_messages(self):
        """检查是否有新消息"""
        try:
            session_file = self.get_latest_session_file()
            if not session_file:
                return 0
            
            # 检查文件修改时间
            current_mod_time = session_file.stat().st_mtime
            
            if self.last_check_time and current_mod_time <= self.last_check_time:
                # 文件没有修改
                return 0
            
            # 更新检查时间
            self.last_check_time = current_mod_time
            
            # 统计消息数量
            user_messages = self.extract_user_messages(session_file)
            current_count = len(user_messages)
            
            if current_count > self.last_message_count:
                # 有新消息
                new_count = current_count - self.last_message_count
                self.last_message_count = current_count
                
                # 获取最新的消息时间
                if user_messages:
                    latest_message = max(user_messages, key=lambda x: x['time'])
                    return latest_message['time']
            
            return None
            
        except Exception as e:
            print(f"⚠️ 检查新消息失败: {e}")
            return None
    
    def update_heartbeat_on_message(self, message_time):
        """在用户消息时更新心跳预测"""
        print(f"📨 检测到用户消息: {message_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # 更新心跳管理器状态
            self.heartbeat_manager.state['last_user_message'] = message_time
            
            # 计算间隔
            hour = message_time.hour
            if 0 <= hour < 6:
                interval = 3 * 3600
                mode = "nighttime"
            else:
                interval = 1 * 3600
                mode = "daytime"
            
            self.heartbeat_manager.state['heartbeat_interval'] = interval
            self.heartbeat_manager.state['mode'] = mode
            
            # 预测下次心跳
            self.heartbeat_manager.state['next_heartbeat'] = message_time + timedelta(seconds=interval)
            
            # 保存状态
            self.heartbeat_manager._save_state()
            
            # 记录到记忆
            self.heartbeat_manager._log_to_memory("auto_detected_message", message_time)
            
            print(f"✅ 已自动更新心跳预测")
            print(f"   下次预测: {self.heartbeat_manager.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   模式: {mode}")
            print(f"   间隔: {interval // 3600}小时")
            
            return True
            
        except Exception as e:
            print(f"❌ 更新心跳状态失败: {e}")
            return False
    
    def run_monitoring(self, interval_seconds=30):
        """运行消息监控"""
        print("👂 启动消息监听器...")
        print(f"  监控间隔: {interval_seconds}秒")
        print(f"  会话目录: {self.sessions_dir}")
        print(f"  状态文件: {self.state_file}")
        print("\n按 Ctrl+C 停止监控\n")
        
        try:
            # 初始化消息计数
            session_file = self.get_latest_session_file()
            if session_file:
                user_messages = self.extract_user_messages(session_file)
                self.last_message_count = len(user_messages)
                print(f"📊 初始消息数量: {self.last_message_count}")
            
            while True:
                # 检查新消息
                new_message_time = self.check_for_new_messages()
                
                if new_message_time:
                    # 检测到新消息，更新心跳
                    self.update_heartbeat_on_message(new_message_time)
                
                # 等待下一次检查
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n👋 消息监听器已停止")
            return True
        except Exception as e:
            print(f"\n❌ 消息监听器错误: {e}")
            return False

def main():
    """主函数"""
    import sys
    
    print("==========================================")
    print("👂 消息监听器")
    print("==========================================")
    
    listener = MessageListener()
    
    if len(sys.argv) < 2:
        # 交互模式
        print("\n🔍 检查当前状态...")
        
        # 获取最后用户消息
        last_message_time = listener.get_last_user_message_time()
        
        if last_message_time:
            print(f"📨 最后用户消息: {last_message_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 更新心跳
            print("\n🔄 更新心跳预测...")
            listener.update_heartbeat_on_message(last_message_time)
        else:
            print("⚠️ 未找到用户消息")
        
        print("\n可用命令:")
        print("  monitor [interval]  启动监控 (默认30秒)")
        print("  check               检查当前状态")
        print("  update              手动更新心跳状态")
        
    elif sys.argv[1] == "monitor":
        # 启动监控
        interval = 30
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except ValueError:
                print(f"⚠️ 无效的间隔: {sys.argv[2]}，使用默认30秒")
        
        listener.run_monitoring(interval)
        
    elif sys.argv[1] == "check":
        # 检查当前状态
        print("\n🔍 检查当前状态...")
        
        last_message_time = listener.get_last_user_message_time()
        if last_message_time:
            print(f"✅ 最后用户消息: {last_message_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 显示时间差
            time_diff = datetime.now() - last_message_time
            minutes = int(time_diff.total_seconds() // 60)
            print(f"   距现在: {minutes}分钟")
            
            # 检查是否需要更新心跳
            print("\n🔄 检查是否需要更新心跳...")
            listener.update_heartbeat_on_message(last_message_time)
        else:
            print("⚠️ 未找到用户消息")
        
    elif sys.argv[1] == "update":
        # 手动更新
        print("\n🔧 手动更新心跳状态...")
        
        last_message_time = listener.get_last_user_message_time()
        if last_message_time:
            success = listener.update_heartbeat_on_message(last_message_time)
            if success:
                print("✅ 心跳状态已更新")
            else:
                print("❌ 更新失败")
        else:
            print("⚠️ 未找到用户消息，使用当前时间")
            listener.update_heartbeat_on_message(datetime.now())
        
    else:
        print(f"❌ 未知命令: {sys.argv[1]}")
    
    print("\n==========================================")
    print("消息监听器完成")
    print("==========================================")

if __name__ == "__main__":
    import sys
    from datetime import timedelta
    sys.path.append(str(Path(__file__).parent))
    
    exit(main())