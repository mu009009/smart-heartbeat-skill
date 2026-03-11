# Smart Reminder Skill

> **⚠️ 项目重命名通知**: 本项目已从 `smart-heartbeat-skill` 重命名为 `smart-reminder-skill`
> 
> **核心优化**: 从传统"心跳"升级为"智能提醒"，更符合实际使用场景

## 🎯 项目概述
Smart Reminder Skill 是一个智能系统状态提醒工具，专为AI Agent设计。它在用户无活动时发送简洁的状态报告，避免在聊天活跃期间打扰用户。

## 🔄 与Heartbeat的区别
1. **改名定位**: 从"心跳"改为"智能提醒"
2. **触发逻辑**: 用户聊天后刷新延后，智能暂停机制
3. **输出简洁**: 不超过200字的纯粹状态报告
4. **功能专注**: 只做状态提醒，不涉及其他功能

## ⏰ 提醒策略
### 时间间隔
- **白天 (06:00-00:00)**: 1小时
- **深夜 (00:00-06:00)**: 3小时

### 智能暂停机制
- 用户发送消息 → 重置计时器
- 聊天活跃期 (最后消息<1小时) → 暂停提醒
- 无活动超过间隔 → 发送提醒

## 📋 配置文件
- `config/reminder_config.yaml` - 主配置文件
- 可自定义检查项目、提醒间隔、输出格式

## 🛠️ 执行脚本
- `scripts/smart_reminder_executor.py` - 主执行器
- 支持测试模式和集成调用

## 📊 输出格式
```
📊 系统状态提醒

✅ 关键状态 (1-3条)
🔄 进行中任务 (如有)
📅 提醒时间

简洁提醒，避免冗余！🔥
```

## 🔧 集成方式
1. 在HEARTBEAT.md中调用
2. 通过cron定时任务
3. 集成到OpenClaw工作流

## 📦 安装
```bash
# 克隆仓库
git clone https://github.com/mu009009/smart-reminder-skill.git

# 安装依赖
pip install -r requirements.txt
```

## 📝 版本历史
### v1.0.0 (2026-03-11)
- **重大更新**: 从smart-heartbeat-skill重命名为smart-reminder-skill
- **核心优化**: 智能暂停机制，聊天活跃时不发送提醒
- **输出优化**: 简洁提醒格式，不超过200字
- **配置优化**: 新的reminder_config.yaml配置文件

### v0.x.x (历史版本)
- v0.9.x: 作为smart-heartbeat-skill的历史版本
- 详细变更记录见CHANGELOG.md

## 🤝 贡献
欢迎提交Issue和Pull Request！

## 📄 许可证
MIT License
