#!/usr/bin/env python3
# ✂️ 心跳内容优化器 - 确保心跳报告简洁高效

import re
from datetime import datetime
from pathlib import Path

class HeartbeatContentOptimizer:
    """心跳内容优化器 - 确保报告简洁、不重复、不啰嗦"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.template_file = self.workspace / "heartbeat_template.md"
        
        # 内容优化规则
        self.rules = {
            "max_length": 200,  # 最大字符数
            "forbidden_patterns": [
                r"回答：",  # 避免"回答："重复
                r"###.*###",  # 避免过多标题
                r"\d+\.\s+✅.*\n",  # 避免编号列表
                r"####.*\n",  # 避免四级标题
            ],
            "required_elements": [
                "📊 HEARTBEAT检查完成",  # 标题
                "系统暴君宣言",  # 签名
                "🔥"  # 表情符号
            ]
        }
    
    def load_template(self, template_name="all_normal"):
        """加载模板"""
        templates = {
            "all_normal": """📊 HEARTBEAT检查完成

✅ 系统状态：全部正常
📅 检查时间：{time}

系统暴君宣言：检查完成！一切正常！🔥""",
            
            "with_warning": """📊 HEARTBEAT检查完成

✅ 主系统：运行中
⚠️ 警告：{warning}需要检查
📅 检查时间：{time}

系统暴君宣言：检查完成！注意警告！🔥""",
            
            "task_progress": """📊 HEARTBEAT检查完成

✅ 主系统：正常
🔄 任务：{task}进行中
📅 检查时间：{time}

系统暴君宣言：检查完成！任务进行中！🔥""",
            
            "multi_server": """📊 HEARTBEAT检查完成

✅ 主服务器：全部正常
🔄 小物服务器：{status}
📅 检查时间：{time}

系统暴君宣言：检查完成！等待任务！🔥"""
        }
        
        return templates.get(template_name, templates["all_normal"])
    
    def format_time(self):
        """格式化时间（上海时间）"""
        utc_now = datetime.utcnow()
        # UTC+8
        shanghai_hour = (utc_now.hour + 8) % 24
        shanghai_time = utc_now.replace(hour=shanghai_hour)
        return shanghai_time.strftime("%H:%M")
    
    def optimize_content(self, content):
        """优化心跳内容"""
        # 检查字符数
        if len(content) > self.rules["max_length"]:
            print(f"⚠️ 内容过长: {len(content)}字符 > {self.rules['max_length']}限制")
            # 简化内容
            content = self.simplify_content(content)
        
        # 检查禁止模式
        for pattern in self.rules["forbidden_patterns"]:
            matches = re.findall(pattern, content, re.MULTILINE)
            if matches:
                print(f"⚠️ 发现禁止模式: {pattern}")
                content = re.sub(pattern, "", content)
        
        # 检查必需元素
        for element in self.rules["required_elements"]:
            if element not in content:
                print(f"⚠️ 缺少必需元素: {element}")
                # 添加缺失元素
                if element == "📊 HEARTBEAT检查完成":
                    content = f"📊 HEARTBEAT检查完成\n\n{content}"
                elif element == "系统暴君宣言":
                    content = f"{content}\n\n系统暴君宣言：优化完成！🔥"
        
        # 清理多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()
    
    def simplify_content(self, content):
        """简化内容"""
        # 移除详细列表
        content = re.sub(r'\d+\.\s+✅[^\n]+\n', '', content)
        
        # 移除过多标题
        content = re.sub(r'#{3,}[^\n]+\n', '', content)
        
        # 移除技术细节
        content = re.sub(r'PID:[^\n]+\n', '', content)
        content = re.sub(r'端口[^\n]+\n', '', content)
        
        # 保留核心信息
        lines = content.split('\n')
        important_lines = []
        
        for line in lines:
            if any(keyword in line for keyword in ["✅", "⚠️", "🔄", "📅", "📊", "系统暴君宣言"]):
                important_lines.append(line)
        
        return '\n'.join(important_lines)
    
    def generate_optimized_report(self, template_name="all_normal", **kwargs):
        """生成优化后的报告"""
        template = self.load_template(template_name)
        time_str = self.format_time()
        
        # 填充模板
        report = template.format(time=time_str, **kwargs)
        
        # 优化内容
        optimized_report = self.optimize_content(report)
        
        # 最终验证
        if len(optimized_report) > self.rules["max_length"]:
            print(f"❌ 优化后仍超长: {len(optimized_report)}字符")
            # 强制截断
            optimized_report = optimized_report[:self.rules["max_length"]] + "..."
        
        print(f"✅ 优化完成: {len(optimized_report)}字符")
        return optimized_report
    
    def check_heartbeat_content(self, content):
        """检查心跳内容质量"""
        print("🔍 心跳内容质量检查:")
        print(f"   字符数: {len(content)}")
        
        issues = []
        
        # 检查长度
        if len(content) > self.rules["max_length"]:
            issues.append(f"内容过长 ({len(content)} > {self.rules['max_length']})")
        
        # 检查禁止模式
        for pattern in self.rules["forbidden_patterns"]:
            if re.search(pattern, content, re.MULTILINE):
                issues.append(f"包含禁止模式: {pattern}")
        
        # 检查必需元素
        for element in self.rules["required_elements"]:
            if element not in content:
                issues.append(f"缺少必需元素: {element}")
        
        # 检查重复
        if "回答：" in content:
            issues.append("包含'回答：'重复模式")
        
        # 输出结果
        if issues:
            print("   ❌ 发现问题:")
            for issue in issues:
                print(f"     - {issue}")
            return False
        else:
            print("   ✅ 内容质量良好")
            return True

def main():
    optimizer = HeartbeatContentOptimizer()
    
    print("🎯 心跳内容优化器 v1.0")
    print("=" * 40)
    
    # 测试模板生成
    print("\n1. 测试模板生成:")
    print("-" * 20)
    
    templates_to_test = ["all_normal", "with_warning", "task_progress", "multi_server"]
    
    for template in templates_to_test:
        report = optimizer.generate_optimized_report(template, warning="Flask服务", task="安装", status="安装中")
        print(f"\n📋 {template}模板:")
        print(report)
        print(f"长度: {len(report)}字符")
    
    # 测试内容检查
    print("\n2. 测试内容检查:")
    print("-" * 20)
    
    # 好的内容
    good_content = """📊 HEARTBEAT检查完成

✅ 系统状态：全部正常
📅 检查时间：07:14

系统暴君宣言：检查完成！一切正常！🔥"""
    
    print("✅ 好的内容检查:")
    optimizer.check_heartbeat_content(good_content)
    
    # 差的内容（冗长）
    bad_content = """回答：📊 HEARTBEAT检查完成 ### ✅ 检查结果： #### 主服务器状态：全部正常 1. ✅ 人设保持 - 100%符合凤丹风格 2. ✅ 系统健康 - 所有服务运行正常 3. ✅ 危机解决 - 上下文307%溢出已处理 4. ✅ 智能系统 - 全部功能正常 5. ✅ 网络状态 - 所有服务可达 #### 小物服务器状态：安装中 - 🔄 OpenClaw重新安装 - npx自动安装openclaw@2026.3.8 - ⏳ 预计完成 - 1-2分钟内 - 📋 下一步 - 安装完成后立即测试飞书连接 #### 唯一待完成项： - [ ] 小物OpenClaw安装完成 - [ ] 测试飞书机器人连接 ### 🔧 建议等待： 1. 等待npx安装完成 (约1-2分钟) 2. 安装完成后立即测试 3. 如果安装失败，采用备用方案 系统暴君宣言：HEARTBEAT检查完成！主服务器一切正常！小物OpenClaw正在重新安装！耐心等待1-2分钟！完成后立即测试！🔥"""
    
    print("\n❌ 差的内容检查:")
    optimizer.check_heartbeat_content(bad_content)
    
    # 优化差的内容
    print("\n3. 优化差的内容:")
    print("-" * 20)
    optimized = optimizer.optimize_content(bad_content)
    print("优化后内容:")
    print(optimized)
    print(f"优化后长度: {len(optimized)}字符")
    
    print("\n🎉 优化器测试完成！")

if __name__ == "__main__":
    main()