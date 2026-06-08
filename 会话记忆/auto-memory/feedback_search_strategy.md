---
name: feedback-search-strategy
description: Keyword search and RAG semantic search are parallel first-class methods, not primary/fallback
metadata:
  type: feedback
---

Keyword search and RAG semantic search are co-equal retrieval methods, each suited to different query types.
**Why:** Exact queries (first appearance of a character, specific quote, chapter number) require keyword grep, not semantic fuzzy matching. Treating keyword as "fallback" misses its unique value.
**How to apply:** SKILL.md for any RAG-powered knowledge base must present both methods as parallel options with a decision table. Never relegate keyword search to Step 3 / fallback.
