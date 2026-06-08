---
name: desktop-organization-2026-05-22
description: 桌面整理结果：文档归类、文件夹结构、约束条件
metadata: 
  node_type: memory
  type: project
  originSessionId: 3fcad793-2c28-4da6-803e-6725d639345f
---

# 桌面整理记录（2026-05-22）

## 最终桌面结构
```
桌面/
├── RAG工具/          ← 不动
├── 文档/             ← 新建，收纳了以下内容
│   ├── 电子书/       ← 文言尺牍入门.epub
│   ├── 内部操作手册/  ← 含 mac/ win/（重要：Claude 引用了此路径）
│   ├── 二维码/       ← 6 个二维码图片
│   ├── 公众号文章_知识库检索.md
│   ├── 小龙虾快捷键.md
│   ├── 朋友圈文案.md
│   ├── 个人简历.pdf
│   └── index.html
└── 桌面/             ← ⚠️ 绝对不动！AE 项目引用此文件夹内路径
```

## ⚠️ 重要约束（不可违反）
1. **`桌面/桌面/` 文件夹绝对不能动** — 用户用 BuhoNTFS 挂载，内部文件被 After Effects 等项目引用路径
2. 桌面根目录的 .aep/.psd/.png/.mp4 等设计文件也不能动

## Claude 引用的路径（整理后仍然有效）
- `/Users/yue/Desktop/文档/内部操作手册/mac`
- `/Users/yue/Desktop/文档/内部操作手册/win`
- `/Users/yue/Downloads/03_工程项目/读书工具/知识库`（主工作目录）

## 外接硬盘
- EXTERNAL_USB（1.8TB）通过 BuhoNTFS 挂载，桌面文件夹已拷贝一份到其中
- 路径：`/private/tmp/com.drbuho.disktool.BuhoNTFS/70E63EA0E63E668E/EXTERNAL_USB/桌面/`
