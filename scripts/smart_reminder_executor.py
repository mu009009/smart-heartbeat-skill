#!/usr/bin/env python3
"""
Smart Reminder Executor
智能提醒执行器
核心功能：在用户无活动时发送简洁状态提醒
"""

import os
import sys
import json
import time
import yaml
import subprocess
from datetime import datetime, time as dt_time
from pathlib import Path

class SmartReminder:
    def __init__(self, config_path="config/reminder_config.yaml"):
        self.config_path = config_path
        self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ 配置文件加载成功: {self.config_path}")
        except Exception as e:
            print(f"❌ 配置文件加载失败: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self):
        """获取默认配置"""
        return {
            "reminder_strategy": {
                "intervals": {"daytime": 3600, "nighttime": 10800},
                "smart_pause": {"active_chat_threshold": 3600, "reset_on_message": True},
                "output": {"max_length": 200}
            }
        }
    
    def setup_logging(self):
        """设置日志"""
        log_dir = self.config.get("logging", {}).get("log_dir", "./logs")
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"reminder_{datetime.now().strftime('%Y%m%d')}.log")
    
    def is_nighttime(self):
        """判断是否为深夜时段 (00:00-06:00)"""
        now = datetime.now()
        current_time = now.time()
        return dt_time(0, 0) <= current_time < dt_time(6, 0)
    
    def get_reminder_interval(self):
        """获取提醒间隔"""
        if self.is_nighttime():
            return self.config["reminder_strategy"]["intervals"]["nighttime"]
        return self.config["reminder_strategy"]["intervals"]["daytime"]
    
    def should_send_reminder(self, last_message_time):
        """判断是否应该发送提醒"""
        current_time = time.time()
        time_since_last_message = current_time - last_message_time
        
        # 检查是否在活跃聊天期
        if time_since_last_message < self.config["reminder_strategy"]["smart_pause"]["active_chat_threshold"]:
            return False
        
        # 检查是否达到提醒间隔
        reminder_interval = self.get_reminder_interval()
        return time_since_last_message >= reminder_interval
    
    def generate_status_report(self):
        """生成状态报告"""
        report_lines = []
        
        # 执行检查项目
        for item in self.config.get("check_items", []):
            try:
                result = subprocess.run(
                    item["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                output = result.stdout.strip()
                if output:
                    status = "✅" if "正常" in output or "运行" in output else "⚠️"
                    if "异常" in output or "失败" in output:
                        status = "❌"
                    report_lines.append(f"{status} {item['name']}: {output}")
                else:
                    report_lines.append(f"⚠️ {item['name']}: 无输出")
            except Exception as e:
                report_lines.append(f"❌ {item['name']} (检查失败: {str(e)})")
        
        # 构建最终报告
        template = self.config["reminder_strategy"]["output"]["structure_template"]
        status_section = "\n".join(report_lines[:3])  # 最多3条关键状态
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report = template.replace("✅ 关键状态 (1-3条)", status_section)
        report = report.replace("📅 提醒时间", f"📅 提醒时间: {current_time}")
        
        # 确保不超过字数限制
        max_length = self.config["reminder_strategy"]["output"]["max_length"]
        if len(report) > max_length:
            report = report[:max_length-3] + "..."
        
        return report
    
    def run(self, last_message_time=None):
        """运行提醒检查"""
        if last_message_time is None:
            # 如果没有提供最后消息时间，默认1小时前（测试模式）
            last_message_time = time.time() - 3600
        
        if self.should_send_reminder(last_message_time):
            report = self.generate_status_report()
            print("📊 生成状态提醒:")
            print(report)
            return report
        else:
            print("⏰ 未达到提醒间隔，跳过发送")
            return None

if __name__ == "__main__":
    reminder = SmartReminder()
    
    # 测试模式：模拟最后消息时间为2小时前
    test_last_message_time = time.time() - 7200
    reminder.run(test_last_message_time)
