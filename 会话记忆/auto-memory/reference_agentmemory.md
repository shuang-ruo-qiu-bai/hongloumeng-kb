---
name: agentmemory-installed
description: agentmemory 持久记忆系统已安装并通过 connect 完整接入 Claude Code
metadata: 
  node_type: memory
  type: reference
  originSessionId: 6167c0b4-3112-4d68-8bcb-448dbc280b87
---

agentmemory (rohitg00/agentmemory v0.9.21) 已安装并通过 MCP 完整接入 Claude Code：

- **安装方式**：`npm install -g @agentmemory/agentmemory`
- **服务端口**：REST API http://localhost:3111，Viewer http://localhost:3113
- **MCP 配置**：`agentmemory connect claude-code` 已执行，MCP server 写入 `~/.claude.json`
  - 启动命令：`npx -y @agentmemory/mcp`
  - 环境变量：AGENTMEMORY_URL、AGENTMEMORY_SECRET
- **MCP 工具**：recall、remember、forget、commit-context、session-history、handoff、recap
- **全局 CLAUDE.md**：已写入 agentmemory 使用铁律，每会话必须使用
- **当前限制**：未配置 LLM API key，LLM 压缩/摘要功能关闭（安全默认）
- **启动状态**：用户要求保持运行。如果发现未运行，需自动启动：`/Users/yue/.npm-global/bin/agentmemory`
