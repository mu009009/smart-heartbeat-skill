#!/usr/bin/env python3
# 🫀 智能心跳预测器
# 基于事件的预测式心跳机制

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

class HeartbeatPredictor:
    """智能心跳预测器 - 基于用户消息预测下次心跳时间"""
    
    def __init__(self, state_file=None):
        self.state_file = state_file or "/root/.openclaw/workspace/heartbeat_state.json"
        self.state = self._load_state()
        
    def _load_state(self):
        """加载心跳状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 转换时间字符串为datetime
                    for key in ['last_user_message', 'last_heartbeat', 'next_heartbeat']:
                        if data.get(key):
                            data[key] = datetime.fromisoformat(data[key])
                    return data
            except Exception as e:
                print(f"⚠️ 加载状态失败: {e}")
        
        # 默认状态
        return {
            "last_user_message": None,
            "last_heartbeat": None,
            "next_heartbeat": None,
            "heartbeat_interval": 3600,  # 默认1小时
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
            print(f"⚠️ 保存状态失败: {e}")
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
    
    def on_user_message(self, message_time=None):
        """用户发送消息时调用"""
        if message_time is None:
            message_time = datetime.now()
        
        print(f"📨 用户消息时间: {message_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 更新最后消息时间
        self.state['last_user_message'] = message_time
        
        # 计算当前间隔和模式
        current_interval = self._calculate_interval(message_time)
        current_mode = self._get_mode(message_time.hour)
        
        self.state['heartbeat_interval'] = current_interval
        self.state['mode'] = current_mode
        
        # 预测下次心跳时间
        self.state['next_heartbeat'] = message_time + timedelta(seconds=current_interval)
        
        # 保存状态
        self._save_state()
        
        # 显示预测结果
        next_time = self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')
        interval_hours = current_interval / 3600
        
        print(f"🎯 预测下次心跳: {next_time}")
        print(f"⏰ 间隔: {interval_hours}小时 ({current_mode}模式)")
        print(f"📊 状态已保存: {self.state_file}")
        
        return self.state['next_heartbeat']
    
    def check_and_send_heartbeat(self):
        """检查是否需要发送心跳"""
        current_time = datetime.now()
        
        # 如果没有预测时间，使用当前时间+1小时
        if self.state['next_heartbeat'] is None:
            print("⚠️ 没有预测的心跳时间，使用默认预测")
            self.on_user_message(current_time)
            return False, None
        
        # 检查是否到了心跳时间
        if current_time >= self.state['next_heartbeat']:
            print(f"🫀 需要发送心跳！")
            print(f"  当前时间: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  预测时间: {self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 更新最后心跳时间
            self.state['last_heartbeat'] = current_time
            
            # 重新预测下次心跳
            current_interval = self._calculate_interval(current_time)
            current_mode = self._get_mode(current_time.hour)
            
            self.state['next_heartbeat'] = current_time + timedelta(seconds=current_interval)
            self.state['heartbeat_interval'] = current_interval
            self.state['mode'] = current_mode
            
            self._save_state()
            
            next_time = self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"🔄 已更新下次心跳: {next_time}")
            
            return True, current_time
        
        else:
            # 计算剩余时间
            time_diff = self.state['next_heartbeat'] - current_time
            hours = time_diff.seconds // 3600
            minutes = (time_diff.seconds % 3600) // 60
            
            print(f"⏳ 无需发送心跳")
            print(f"  剩余时间: {hours}小时{minutes}分钟")
            print(f"  下次心跳: {self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            return False, time_diff
    
    def get_status(self):
        """获取当前状态"""
        status = {
            "当前时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "模式": self.state['mode'],
            "当前间隔": f"{self.state['heartbeat_interval'] // 3600}小时",
        }
        
        if self.state['last_user_message']:
            status["最后用户消息"] = self.state['last_user_message'].strftime('%Y-%m-%d %H:%M:%S')
        
        if self.state['last_heartbeat']:
            status["最后心跳"] = self.state['last_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')
        
        if self.state['next_heartbeat']:
            time_diff = self.state['next_heartbeat'] - datetime.now()
            if time_diff.total_seconds() > 0:
                hours = time_diff.seconds // 3600
                minutes = (time_diff.seconds % 3600) // 60
                status["下次心跳"] = f"{self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')} ({hours}小时{minutes}分钟后)"
            else:
                status["下次心跳"] = f"{self.state['next_heartbeat'].strftime('%Y-%m-%d %H:%M:%S')} (已超时)"
        
        return status
    
    def reset_state(self):
        """重置状态"""
        self.state = {
            "last_user_message": None,
            "last_heartbeat": None,
            "next_heartbeat": None,
            "heartbeat_interval": 3600,
            "mode": "daytime"
        }
        self._save_state()
        print("🔄 心跳状态已重置")
        return True

def main():
    """命令行接口"""
    import sys
    
    print("==========================================")
    print("🫀 智能心跳预测器")
    print("==========================================")
    
    predictor = HeartbeatPredictor()
    
    if len(sys.argv) < 2:
        # 显示状态
        status = predictor.get_status()
        print("\n📊 当前状态:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        # 检查是否需要发送心跳
        print("\n🔍 检查心跳状态...")
        need_heartbeat, result = predictor.check_and_send_heartbeat()
        
        if need_heartbeat:
            print(f"\n✅ 需要发送心跳！时间: {result.strftime('%Y-%m-%d %H:%M:%S')}")
            print("请在外部调用中执行实际的心跳发送")
        else:
            if isinstance(result, timedelta):
                hours = result.seconds // 3600
                minutes = (result.seconds % 3600) // 60
                print(f"\n⏳ 无需心跳，剩余时间: {hours}小时{minutes}分钟")
        
    elif sys.argv[1] == "user_message":
        # 模拟用户发送消息
        print("\n📨 模拟用户发送消息...")
        next_heartbeat = predictor.on_user_message()
        print(f"✅ 已记录用户消息，下次心跳预测: {next_heartbeat.strftime('%Y-%m-%d %H:%M:%S')}")
        
    elif sys.argv[1] == "check":
        # 检查心跳
        print("\n🔍 检查是否需要发送心跳...")
        need_heartbeat, result = predictor.check_and_send_heartbeat()
        
        if need_heartbeat:
            print(f"\n✅ 需要发送心跳！")
            # 这里可以集成实际的心跳发送逻辑
        else:
            print(f"\n⏳ 无需发送心跳")
            
    elif sys.argv[1] == "reset":
        # 重置状态
        print("\n🔄 重置心跳状态...")
        predictor.reset_state()
        
    elif sys.argv[1] == "status":
        # 显示详细状态
        status = predictor.get_status()
        print("\n📊 详细状态:")
        for key, value in status.items():
            print(f"  {key}: {value}")
            
    else:
        print(f"❌ 未知命令: {sys.argv[1]}")
        print("\n可用命令:")
        print("  (无参数) 显示状态并检查心跳")
        print("  user_message 模拟用户发送消息")
        print("  check 检查是否需要发送心跳")
        print("  reset 重置状态")
        print("  status 显示详细状态")
    
    print("\n==========================================")
    print("智能心跳预测器完成")
    print("==========================================")

if __name__ == "__main__":
    main()