"""AI 问答引擎 — 基于搜索结果的 AI 合成回答

支持多个 API 提供商：
- DeepSeek — 性价比高，中文优秀（默认）
- Claude (Anthropic) — 中文最优
- OpenAI — 兼容性好
- Ollama — 本地免费（需安装 Ollama）
"""

from __future__ import annotations

import json
import os
from typing import Any

import search_engine as se

# ---------------------------------------------------------------------------
# Prompt 模板
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """你是一位红楼梦研究专家。你的任务是基于提供的资料片段，回答用户的问题。

## 回答要求

1. **基于资料**：所有核心观点必须有资料支撑，在正文中用 [来源：书名] 标注
2. **区分层次**：明确区分"原文记载"、"学者观点"、"你的分析"
3. **多源对读**：如不同资料说法有出入，在回答中呈现分歧而非掩盖
4. **首次出现必定义**：人物第一次出现用全名+身份，概念第一次出现给定义
5. **术语定义**：脂评本、程高本、索隐派等术语首次出现时必须解释
6. **推演标注**：任何推断必须标注（推演）
7. **无资料不编造**：如果资料不足以回答，直接说"资料中未找到相关内容"

## 输出格式

回答应包含：
1. 一句话总结
2. 详细分析（引用资料）
3. 不同学者的观点对比（如有）
4. 待确认点（如有）

用户的问题：{question}

## 相关资料

{context}
"""


def build_context(search_results: list[dict], max_chars: int = 12000) -> str:
    """将搜索结果组装为 AI 上下文文本。"""
    parts = []
    char_count = 0
    for r in search_results:
        text = r.get("text", r.get("line_text", "")).strip()
        if not text:
            continue
        source = r.get("source_pretty", r.get("source", "未知来源"))
        chunk = f"[来源：{source}]\n{text}\n"
        if char_count + len(chunk) > max_chars:
            break
        parts.append(chunk)
        char_count += len(chunk)

    return "\n---\n".join(parts) if parts else "（无可用资料）"


def ask_ai(question: str, context: str, config: dict) -> dict[str, Any]:
    """调用 AI API 生成回答。

    Args:
        question: 用户提问
        context: 搜索到的相关资料文本
        config: API 配置 (provider, api_key, api_base, model)

    Returns:
        {"answer": str, "error": str | None}
    """
    provider = config.get("provider", "claude")
    api_key = config.get("api_key", "")
    api_base = config.get("api_base", "").rstrip("/")
    model = config.get("model", "")

    if provider != "ollama" and not api_key:
        return {"answer": "", "error": "未配置 API Key，请在设置页面填写"}

    prompt = SYSTEM_PROMPT.format(
        question=question,
        context=context,
    )

    try:
        if provider == "deepseek":
            return _ask_openai(prompt, api_key, api_base or "https://api.deepseek.com",
                               model or "deepseek-v4-flash")
        elif provider == "claude":
            return _ask_claude(prompt, api_key, api_base, model)
        elif provider == "openai":
            return _ask_openai(prompt, api_key, api_base, model)
        elif provider == "ollama":
            return _ask_ollama(prompt, api_base, model)
        else:
            return {"answer": "", "error": f"不支持的 AI 提供商: {provider}"}
    except Exception as e:
        return {"answer": "", "error": f"API 调用失败: {str(e)}"}


def _ask_claude(prompt: str, api_key: str, api_base: str, model: str) -> dict:
    """调用 Anthropic Claude API。"""
    import urllib.request
    import urllib.error

    url = f"{api_base}/v1/messages"
    body = json.dumps({
        "model": model or "claude-sonnet-4-20250514",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    answer = ""
    for block in data.get("content", []):
        if block.get("type") == "text":
            answer += block.get("text", "")

    return {"answer": answer.strip(), "error": None}


def _ask_openai(prompt: str, api_key: str, api_base: str, model: str) -> dict:
    """调用 OpenAI 兼容 API。"""
    import urllib.request
    import urllib.error

    url = f"{api_base}/chat/completions"
    body = json.dumps({
        "model": model or "gpt-4o-mini",
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": "你是红楼梦研究专家。"},
            {"role": "user", "content": prompt},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"answer": answer.strip(), "error": None}


def _ask_ollama(prompt: str, api_base: str, model: str) -> dict:
    """调用本地 Ollama。"""
    import urllib.request
    import urllib.error

    url = f"{api_base}/api/generate"
    body = json.dumps({
        "model": model or "qwen2.5:7b",
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 4096},
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    answer = data.get("response", "")
    return {"answer": answer.strip(), "error": None}
