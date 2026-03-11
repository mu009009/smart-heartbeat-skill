# Smart Reminder Skill Changelog

## v1.0.0 (2026-03-11) - 重大升级：从Heartbeat到Reminder
### 🚀 新特性
- **项目重命名**: `smart-heartbeat-skill` → `smart-reminder-skill`
- **智能暂停机制**: 聊天活跃时不发送提醒
- **简洁输出**: 不超过200字的系统状态报告
- **新配置文件**: `reminder_config.yaml` 替代旧的heartbeat配置

### 🔧 技术优化
- **触发逻辑优化**: 用户聊天后重置计时器
- **时间策略**: 白天1小时，深夜3小时
- **防打扰设计**: 避免在用户活跃时发送提醒
- **集成友好**: 兼容OpenClaw HEARTBEAT系统

### 📁 文件结构
```
smart-reminder-skill/
├── config/
│   └── reminder_config.yaml      # 主配置文件
├── scripts/
│   └── smart_reminder_executor.py # 主执行脚本
├── tests/                        # 测试文件
├── logs/                         # 日志目录
├── README.md                     # 项目说明
├── SKILL.md                      # OpenClaw技能文档
└── CHANGELOG.md                  # 变更记录
```

### 🐛 Bug修复
- 修复了旧版本中可能出现的重复提醒问题
- 优化了配置文件加载错误处理
- 改进了日志记录机制

### 📝 文档更新
- 更新所有文档反映项目重命名
- 添加新的使用示例
- 完善集成指南

---

## v0.9.0 (2026-03-10) - 最后一次heartbeat版本
### 功能
- 基础心跳检查功能
- 简单的时间间隔配置
- 基础状态报告

### 注意
此版本后项目重命名为smart-reminder-skill，核心概念从"心跳"升级为"智能提醒"
