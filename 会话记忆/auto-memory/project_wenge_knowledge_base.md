---
name: project_wenge_knowledge_base
description: "文革研究 RAG system — full-stack local retrieval with ChromaDB, ready for GitHub"
metadata: 
  node_type: memory
  type: project
  originSessionId: 6167c0b4-3112-4d68-8bcb-448dbc280b87
---

# 文革研究知识库项目

RAG-based local retrieval system for Cultural Revolution research, using ChromaDB + sentence-transformers + BM25 hybrid search.

**Status:** System built, RAG index populated (17499 embeddings from 32 files), GitHub README written, OCR workflow documented.

**Key decisions:**
- Naming: "文革研究" (not "文海" which was rejected)
- Embedding model: `shibing624/text2vec-base-chinese` (768-dim), configurable via `WENGE_EMBED_MODEL` env var
- Hybrid search: vector (0.6) + BM25 (0.4) with RRF fusion
- Chunking: 800 chars/chunk, 120 overlap, sentence-boundary aware
- Incremental indexing via SQLite (mtime + size + md5)
- Two OCR engines: pytesseract (default, simplified Chinese) and PaddleOCR (traditional/vertical text)

**Why:** User wanted a tool to search through hundreds of scattered books about the Cultural Revolution — memoirs, academic works, archives — without manually flipping through pages.

**How to apply:** When asked to add books, use the OCR workflow in SKILL.md. The RAG indexing is incremental — only newly added/modified files get processed. Run `rag_index.py` after adding files.
