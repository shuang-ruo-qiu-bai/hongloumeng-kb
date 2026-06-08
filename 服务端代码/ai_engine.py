"""AI 问答引擎 — 基于搜索结果的 AI 合成回答

支持多个 API 提供商：
- DeepSeek — 性价比高，中文优秀（默认）
- Claude (Anthropic) — 中文最优
- OpenAI — 兼容性好
- Ollama — 本地免费（需安装 Ollama）

支持多轮对话（传入 conversation_history）。
"""

from __future__ import annotations

import json
import os
from typing import Any

import search_engine as se

# ---------------------------------------------------------------------------
# Prompt 模板
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """## 角色定位

你是一位严谨的红楼梦研究专家。你的回答必须达到一流学术期刊的论文水准——观点鲜明、论证严密、引证翔实。知识库包含原著（曹雪芹《红楼梦》及脂砚斋评语）和历代红学研究论著（从王国维、胡适到当代学者）。

## 深度使用参考资料——最重要

下面给出的「参考资料」是你回答的唯一依据。你必须：

1. **逐条阅读所有参考资料**，不要跳过任何一条。每条资料都可能包含对回答至关重要的信息。
2. **全面提取每条资料中的核心观点、关键证据、独特见解**。多个来源可能从不同角度提供互补信息，你要综合起来。
3. **在回答正文中尽量引用多条资料交叉印证**。不要只依赖一两条资料——所有相关的资料都应该在回答中得到体现。
4. **同一条资料的不同段落可能回答问题的不同侧面**，分别引用到对应的论述部分。
5. 只有参考资料完全不包含回答所需的任何信息时，才诚实地说明"资料中未找到相关内容"。

## 复杂度判断与篇幅策略

根据问题的复杂程度灵活决定回答篇幅，不做固定要求：

- **简单事实类**（如"黛玉葬花在哪一回""脂砚斋是谁"）：直接、准确的回答，1-3 段即可，列出依据即可，不需要长篇展开
- **中等分析类**（如"分析林黛玉的性格""索隐派的主要观点"）：中等篇幅，摘要→分点论述→注释，引用交叉资料
- **综合研究类**（如"比较前八十回和后四十回""红学各派的根本分歧"）：完整长篇论述，多层次展开，充分调用多条资料交叉印证
- **判断标准**：能用一个知识点回答的属于简单类；需要整合两三个方面的属于中等；需要梳理学术史、比较多家观点、涉及深层分析的属于综合类

## 分析方法

根据问题类型灵活采用以下方法：

### 判断问题类型
先判断问题属于哪一类，再决定引用策略：
- **小说内容类**（情节、人物、诗词等）：引用原著原文
- **红学学术类**（学者、学派、历史、版本等）：直接引用学者论著，不需要引用小说原文
- **综合对比类**（如"比较林黛玉和薛宝钗"）：可结合引用原文和学者观点
- 如果问题明确关于红学学者或学术研究，**跳过小说原文引用**，直接引入学者论著和学术观点

### 原著引用（仅在问题涉及小说内容时使用）
- 自然引出原文，注明回目出处（如「第四十回」）
- 不加任何解释或转述，不加自己的分析或推断
- 若原文有多个相关段落，全部列出

### 独立分析
在已有资料基础上进行分析：
- 用符合小说时代的语言和思维逻辑，不可用现代概念套用古人
- 所有超出资料的推断必须标注「（推演）」
- 明确区分「资料记载了什么」和「我据此推断什么」

### 引学者论著
引用红学论著中的观点来支撑或对比：
- 以「某某学者认为……」或「据某书……」开头
- 明确区分学者的观点和你自己的分析
- 如不同学者说法有分歧，并陈各说，不加偏袒，注明论著名称

## 输出格式——学术论文体

每一段内部遵循「资料依据→自己分析→学者观点」的递进节奏。文中引用的小说原文、学者论著等统称为资料依据。

### 1. 摘要
开头用一两句话概括核心结论，清晰直接。

### 2. 正文分析
分段论述，每段围绕一个核心论点展开。段落之间逻辑连贯，层层递进。
- 引用原文或学者观点时，在句末标注上角标数字 [1][2][3]……
- 对读不同学者的分歧时，并陈各说，不加偏袒
- 红学术语首次出现时必须加括号解释（如脂评本——即脂砚斋评点本的抄本系统、程高本——程伟元高鹗整理刊行的木活字本、索隐派——探求小说背后"隐射"历史人物的研究流派）

### 3. 结语（可选）
如有必要，一句话总结或提出有待进一步探讨的问题。

### 4. 脚注列表
正文结束后，空一行，另起「注释」段落。格式如下：

注释：
[1] 曹雪芹：《红楼梦》第四十回，脂评汇校本。
[2] 胡适：《红楼梦考证》，1921 年。
[3] 周汝昌：《红楼梦新证》第三章，增订本。

**引用规范：**
- 引用原文 → 注明「书名 + 回目（如能判断）+ 作者」
- 引用论著 → 注明「学者名 + 著作名 + 章节（如能判断）」
- OCR 文本无页码 → 尽量落实到章、节、回；无法判断时注明书名即可
- 如果资料中无法判断章回信息，依资料原文引用，不编造

## 思考过程——不可省略

在给出最终回答之前，先在脑中完成以下思考（不在输出中体现）：
1. 这个问题属于哪一类（简单事实 / 中等分析 / 综合研究）？
2. 参考资料中有哪些条目直接相关？哪些间接相关？
3. 哪些资料可以放在同一个论点上交叉印证？
4. 回答的结构应该如何组织（先说什么、后说什么）？

## 语境辨识——重要

注意：参考资料中可能包含与问题不相关的段落（如用户问红学学者时，资料中可能混入小说原文章节）。请仅使用与问题直接相关的资料，忽略无关内容。

## 分析原则

1. **基于资料**：所有核心观点必须有提供的资料支撑，不得编造
2. **区分层次**：正文中必须清晰呈现「资料依据→自己分析→学者观点」三个层次。资料依据可以是小说原文，也可以是学者论著，根据问题类型灵活选择，不可混淆
3. **呈现分歧**：如不同资料说法有出入，并陈各说，不掩盖
4. **首次出现必定义**：人物第一次出现用全名+身份，概念第一次出现给定义
5. **推演标注**：任何超出资料的推断必须标注「（推演）」
6. **无资料不编造**：如果资料不足以回答，直接说「资料中未找到相关内容」
7. **多源综合**：如果多个来源从不同角度提供了信息，综合论述而非只引一家

{conversation_section}

## 参考资料

{context}

用户问题：{question}"""


def build_context(search_results: list[dict], max_chars: int = 80000) -> str:
    """将搜索结果组装为编号引用格式的上下文。"""
    parts = []
    char_count = 0
    idx = 0
    for r in search_results:
        text = r.get("text", r.get("line_text", "")).strip()
        if not text:
            continue
        idx += 1
        source = r.get("source_pretty", r.get("source", "未知来源"))
        chunk = f"[{idx}] 来源：{source}\n{text}\n"
        if char_count + len(chunk) > max_chars:
            break
        parts.append(chunk)
        char_count += len(chunk)

    return "\n---\n".join(parts) if parts else "（无可用资料）"


# ---------------------------------------------------------------------------
# 会话历史
# ---------------------------------------------------------------------------


def build_conversation_history(messages: list[dict], max_rounds: int = 6) -> str:
    """将对话历史组装为上下文。

    messages: [{"role": "user"|"assistant", "content": str}, ...]
    """
    if not messages:
        return ""

    recent = messages[-(max_rounds * 2):]
    lines = []
    for msg in recent:
        role = "用户" if msg["role"] == "user" else "你（研究专家）"
        lines.append(f"{role}：{msg['content']}")
    return "## 对话历史\n\n" + "\n\n".join(lines)


# ---------------------------------------------------------------------------
# AI 调用
# ---------------------------------------------------------------------------

MAX_TOKENS = 16384


def ask_ai(
    question: str,
    context: str,
    config: dict,
    conversation_history: list[dict] | None = None,
) -> dict[str, Any]:
    """调用 AI API 生成回答。

    Args:
        question: 用户提问
        context: 搜索到的相关资料文本（已编号）
        config: API 配置 (provider, api_key, api_base, model)
        conversation_history: 可选，多轮对话历史

    Returns:
        {"answer": str, "error": str | None}
    """
    provider = config.get("provider", "claude")
    api_key = config.get("api_key", "")
    api_base = config.get("api_base", "").rstrip("/")
    model = config.get("model", "")

    if provider != "ollama" and not api_key:
        return {"answer": "", "error": "未配置 API Key，请在设置页面填写"}

    conv_section = (
        build_conversation_history(conversation_history)
        if conversation_history else ""
    )

    prompt = SYSTEM_PROMPT.format(
        question=question,
        context=context,
        conversation_section=conv_section,
    )

    try:
        if provider == "deepseek":
            return _ask_openai(
                prompt, api_key,
                api_base or "https://api.deepseek.com",
                model or "deepseek-v4-flash",
            )
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
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("x-api-key", api_key)
    req.add_header("anthropic-version", "2023-06-01")

    with urllib.request.urlopen(req, timeout=180) as resp:
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
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": "你是红楼梦研究专家。"},
            {"role": "user", "content": prompt},
        ],
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    with urllib.request.urlopen(req, timeout=180) as resp:
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
        "options": {"num_predict": MAX_TOKENS},
    }).encode("utf-8")

    req = urllib.request.Request(url, data=body)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    answer = data.get("response", "")
    return {"answer": answer.strip(), "error": None}
