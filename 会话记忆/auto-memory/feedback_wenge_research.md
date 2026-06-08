---
name: feedback-wenge-research-approach
description: 文革知识库研究必须用检索式方法，不能用全文通读
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6167c0b4-3112-4d68-8bcb-448dbc280b87
---

文革知识库的研究必须使用检索式/搜索式方法，绝不能尝试全文通读《晚年周恩来》等敏感书籍。

**Why:** 尝试全书通读（尤其是读到结尾部分）会触发内容安全风控，模型返回 400 错误。

**How to apply:** 使用 wenge-research skill 的工作流——先用 `search_corpus.py` 搜索相关片段，只定向读取与研究问题直接相关的章节/段落。禁止一次性读取整个书籍文件。回答时用中性学术口吻，不输出大段原文，优先采用苏格拉底式反问引导用户思考。
