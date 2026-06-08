---
name: feedback_use_auto_memory
description: "Must use Claude Code's auto memory system to persist session information — user explicitly demanded this"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6167c0b4-3112-4d68-8bcb-448dbc280b87
---

# Use auto memory system

**Must persist important session information into memory files** (`.claude/projects/*/memory/`) after each session or whenever user instructions change substantially.

**Why:** User was frustrated that I didn't remember the OCR workflow I had built for them in a previous session. They explicitly said "你是不是给你安装了一个最强的记忆功能？你怎么没用啊？" — the auto memory system exists to prevent exactly this kind of knowledge loss.

**How to apply:**
1. After each significant exchange, update memory files if any new non-obvious information was learned
2. Save user preferences, project decisions, feedback corrections, and external reference pointers
3. Do NOT save what's already in code files (README, SKILL.md, scripts) — the code is the source of truth
4. Do NOT save git history, recent changes, or in-progress work states
5. When saving, link related memories via `[[name]]` in the body
6. Update MEMORY.md index when adding new memory files
