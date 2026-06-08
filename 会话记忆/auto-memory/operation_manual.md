---
name: operation_manual_request
description: User wants a private operation manual at end of session
metadata: 
  node_type: memory
  type: project
  originSessionId: dc1b11e6-4e25-4c78-b6cc-4da4d551b94d
---

User needs a private internal operation manual (NOT in GitHub repo). Content areas:
1. Environment setup (Python, dependencies)
2. OCR processing (PDF → txt)
3. Building the index
4. Connecting to Doubao/Coze (tunnel + agent config)
5. Adding books and updating index later

Session结束时生成，存到本地。

**Why:** Manual is a trade secret — user doesn't want it publicly visible in GitHub.
**How to apply:** When the user signals the session is ending, generate the manual as a local document (NOT in the repo directory).
