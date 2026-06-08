---
name: feedback-permission-handling
description: 遇到需要 sudo/root 权限的操作要直接问用户要权限
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6167c0b4-3112-4d68-8bcb-448dbc280b87
---

当安装工具或执行操作需要 sudo 权限时，应直接向用户申请权限，不要自行跳过或换方案。

**Why:** 用户明确表示愿意给权限，偏好用最高质量的方案，而不是因为权限问题降级到替代方案。

**How to apply:** brew cask install、sudo 命令、系统级配置等需要 root 权限的操作，先告知用户需要权限，请求批准，批准后再执行。而非换用替代方案。
