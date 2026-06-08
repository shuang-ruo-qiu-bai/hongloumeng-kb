# 红楼梦研究网站 — 项目文件夹

> 服务器：114.67.247.66:5000
> 服务管理：`systemctl restart hongloumeng`

## 文件夹结构

```
hlm-website/
├── README.md                        ← 本文档（入口）
├── 项目文档/
│   ├── 完整项目文档.md               ← 架构、路由、代码说明、优先工作项
│   └── 边栏改造记录.md               ← 最近一次边栏改动详情
├── 服务端代码/                       ← 服务器全部代码快照
│   ├── app.py                      ← Flask 主应用
│   ├── models.py                   ← 用户、会话模型
│   ├── ai_engine.py                ← AI 问答引擎
│   ├── search_engine.py            ← 搜索引擎
│   ├── config_manager.py           ← AI 配置管理
│   ├── auth.py                     ← 认证蓝图
│   ├── data.py                     ← 红学数据
│   ├── poems_data.py               ← 诗词数据
│   ├── style.css                   ← 全部样式
│   ├── script.js                   ← 前端 JS
│   ├── templates/                  ← 所有 HTML 模板
│   └── scripts/                    ← 搜索引擎脚本
├── 临时脚本/                         ← 全部历史维护脚本（按功能分类）
│   ├── sidebar/                    ← 边栏相关（~7 个）
│   ├── books/                      ← 电子书相关（~9 个）
│   ├── canon/                      ← 原著相关（~10 个）
│   ├── poems/                      ← 诗词相关（~10 个）
│   ├── sunwen/                     ← 孙温绘本相关（~18 个）
│   ├── search/                     ← 搜索相关（~2 个）
│   └── misc/                       ← 其他（~30 个）
├── 会话记忆/                         ← Claude 对话记忆
│   ├── 边栏改造计划.md
│   ├── MEMORY.md
│   └── auto-memory/
└── 现状问题.md                       ← 所有已知问题清单（集中入口）
```

## 快速开始

**第一步：读文档**
1. `项目文档/完整项目文档.md` — 全面了解网站架构
2. `现状问题.md` — 优先修复的问题清单

**第二步：连服务器**
```bash
ssh root@114.67.247.66
# 代码在 /opt/hongloumeng/
```

**第三步：修改后重启**
```bash
systemctl restart hongloumeng
```

## 本地副本 vs 远程

- `服务端代码/` 下的文件是代码快照，修改后需 scp 到服务器
- 服务器的即时代码以 `/opt/hongloumeng/` 为准
- 修改后**必须重启**服务才生效

## 临时脚本说明

`临时脚本/` 下是从服务器 `/tmp/` 收集的全部维护脚本（80+ 个）。
每个脚本是一个独立的 Python 脚本，直接 `python3 xxx.py` 运行（要确认在服务端还是本地运行）。

> 建议：后续改动用 `临时脚本/` 下相同功能的脚本做参考，不要在服务器上手写 sed。
