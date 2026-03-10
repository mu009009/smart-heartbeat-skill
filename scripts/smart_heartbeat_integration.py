#!/usr/bin/env python3
# 🫀 智能心跳集成检查
# 集成智能心跳判断到HEARTBEAT检查中

import sys
from pathlib import Path

def smart_heartbeat_check():
    """智能HEARTBEAT检查 - 集成智能心跳判断"""
    
    # 导入智能心跳判断
    sys.path.append(str(Path("/root/.openclaw/workspace")))
    
    try:
        from fix_heartbeat_sending import HeartbeatSendFixer
        fixer = HeartbeatSendFixer()
        
        # 判断是否应该发送
        should_send = fixer.should_send_heartbeat_manually()
        
        if should_send:
            # 应该发送 - 执行检查并发送简洁报告
            print("执行HEARTBEAT检查并发送简洁报告...")
            return True
        else:
            # 不应该发送 - 只回复HEARTBEAT_OK
            print("HEARTBEAT_OK")
            return False
            
    except Exception as e:
        print(f"❌ 智能心跳检查失败: {e}")
        # 出错时默认执行检查
        return True

def execute_concise_heartbeat_check():
    """执行简洁HEARTBEAT检查（<200字符）"""
    from datetime import datetime
    
    # 获取上海时间
    utc_now = datetime.utcnow()
    shanghai_hour = (utc_now.hour + 8) % 24
    time_str = f"{shanghai_hour:02d}:{utc_now.minute:02d}"
    
    # 检查关键服务（简化版）
    import subprocess
    
    status = {
        "flask": False,
        "http": False,
        "gateway": False
    }
    
    try:
        # 检查Flask服务
        result = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
        status["flask"] = ":18793" in result.stdout
        status["http"] = ":8080" in result.stdout
        
        # 检查OpenClaw gateway
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "openclaw-gateway"],
            capture_output=True,
            text=True
        )
        status["gateway"] = "active" in result.stdout
        
    except:
        pass
    
    # 生成简洁报告
    if all(status.values()):
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
    
    # 确保报告不超过200字符
    if len(report) > 200:
        report = report[:197] + "..."
    
    print(report)
    return True

def main():
    print("🫀 智能心跳集成检查系统")
    print("=" * 40)
    
    # 第一步：智能判断
    print("1. 🤔 智能判断阶段:")
    should_execute = smart_heartbeat_check()
    
    # 第二步：如果需要，执行检查
    if should_execute and should_execute is not True:  # should_execute可能是字符串"HEARTBEAT_OK"
        if should_execute == "HEARTBEAT_OK":
            print("2. ✅ 决策：只回复 HEARTBEAT_OK")
            return
        else:
            print("\n2. 🔍 执行阶段：")
            execute_concise_heartbeat_check()
    elif should_execute:
        print("\n2. 🔍 执行阶段：")
        execute_concise_heartbeat_check()
    else:
        print("2. ✅ 决策：不执行检查，只回复 HEARTBEAT_OK")

if __name__ == "__main__":
    main()