#!/usr/bin/env python3
# 💓 优化版心跳检查 - 简洁高效
# 符合Claudius要求：不干扰聊天，内容简洁

import os
import sys
import json
from datetime import datetime
from pathlib import Path

class OptimizedHeartbeatCheck:
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        
    def get_shanghai_time(self):
        """获取上海时间"""
        utc_now = datetime.utcnow()
        # UTC+8
        shanghai_hour = (utc_now.hour + 8) % 24
        shanghai_time = utc_now.replace(hour=shanghai_hour)
        return shanghai_time
    
    def format_time(self, dt):
        """格式化时间显示"""
        return dt.strftime("%H:%M")
    
    def should_send_heartbeat(self):
        """判断是否需要发送心跳（简化版）"""
        # 检查是否有心跳触发文件
        heartbeat_file = self.workspace / "trigger_heartbeat.flag"
        if heartbeat_file.exists():
            os.remove(heartbeat_file)
            return True
        
        # 默认返回False，让智能心跳系统决定
        return False
    
    def generate_concise_report(self):
        """生成简洁心跳报告"""
        shanghai_time = self.get_shanghai_time()
        time_str = self.format_time(shanghai_time)
        
        # 检查关键服务状态
        status = self.check_critical_services()
        
        # 构建简洁报告
        if status["all_normal"]:
            report = f"""📊 HEARTBEAT检查完成

✅ 系统状态：全部正常
📅 检查时间：{time_str}

系统暴君宣言：检查完成！一切正常！🔥"""
        else:
            warnings = []
            if not status["flask"]:
                warnings.append("Flask服务")
            if not status["http"]:
                warnings.append("HTTP服务")
            if not status["gateway"]:
                warnings.append("OpenClaw网关")
            
            warning_str = "、".join(warnings)
            report = f"""📊 HEARTBEAT检查完成

✅ 主系统：运行中
⚠️ 警告：{warning_str}需要检查
📅 检查时间：{time_str}

系统暴君宣言：检查完成！注意警告！🔥"""
        
        return report
    
    def check_critical_services(self):
        """检查关键服务状态（简化版）"""
        import subprocess
        
        status = {
            "flask": False,
            "http": False,
            "gateway": False,
            "all_normal": True
        }
        
        try:
            # 检查Flask服务（端口18793）
            result = subprocess.run(
                ["ss", "-tlnp"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if ":18793" in result.stdout:
                status["flask"] = True
            else:
                status["all_normal"] = False
                
            # 检查HTTP服务（端口8080）
            if ":8080" in result.stdout:
                status["http"] = True
            else:
                status["all_normal"] = False
                
            # 检查OpenClaw gateway
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "openclaw-gateway"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "active" in result.stdout:
                status["gateway"] = True
            else:
                status["all_normal"] = False
                
        except Exception as e:
            print(f"⚠️ 服务检查出错: {e}")
            status["all_normal"] = False
        
        return status
    
    def run(self):
        """运行优化心跳检查"""
        if self.should_send_heartbeat():
            report = self.generate_concise_report()
            print(report)
            return True
        else:
            # 不发送心跳，保持安静
            return False

def main():
    checker = OptimizedHeartbeatCheck()
    should_send = checker.run()
    
    if not should_send:
        # 只有在需要时才输出
        shanghai_time = checker.get_shanghai_time()
        time_str = checker.format_time(shanghai_time)
        print(f"💓 心跳检查完成 ({time_str}) - 无需发送")

if __name__ == "__main__":
    main()