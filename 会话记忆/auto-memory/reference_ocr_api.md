---
name: ocr-api
description: AI Studio PaddleOCR API for Chinese book OCR — token stored in ~/.aistudio_token
metadata: 
  node_type: memory
  type: reference
  originSessionId: 1de4503d-07e9-4ad4-8900-793c39e97b9f
---

## OCR API 配置

| 条目 | 内容 |
|------|------|
| 服务商 | 百度 AI Studio PaddleOCR |
| Token 位置 | `~/.aistudio_token` |
| 调用脚本 | `/Users/yue/.claude/skills/zh-book-pipeline/scripts/ocr_aistudio_api.py` |
| 使用方式 | `python3 ocr_aistudio_api.py input.pdf -o output_dir/` |
| 首选模型 | PaddleOCR-VL-1.5 |
| 备选模型 | PP-StructureV3 / PP-OCRv5 / PaddleOCR-VL |
| 上传限制 | 文件上传 ≤50MB；可用 `--file-url` URL模式 ≤200MB |
| 依赖 | `pip install requests` |
| Token 设置 | `echo your_token > ~/.aistudio_token` |

**注意**：Token 已经写入 `~/.aistudio_token`，`ocr_aistudio_api.py` 会自动读取。以后 OCR 任务直接用这个脚本即可，不需要再问用户要 Key。
