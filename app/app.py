"""红楼梦研究 · RAG 搜索应用

部署说明：
- 生产环境：Zeabur 自动使用 gunicorn 启动（见 Procfile）
- 开发环境：python app/app.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

# 生产环境 Zeabur 通过 PORT 环境变量指定端口
PORT = int(os.environ.get("PORT", 5000))

# ---------------------------------------------------------------------------
# Initialize search engine
# ---------------------------------------------------------------------------

# Auto-detect knowledge base root relative to this app's location
_APP_DIR = Path(__file__).resolve().parent
KB_ROOT = Path(os.environ.get(
    "HLM_KB_ROOT",
    str(_APP_DIR.parent)  # default: knowledge base root = parent of windows-app/
))

sys.path.insert(0, str(_APP_DIR))

import search_engine as se
import config_manager as cfg
import ai_engine as ai

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    """Main search page."""
    return render_template("index.html",
                           sources=se.get_source_files())


@app.route("/api/search")
def api_search():
    """Search API — returns JSON results."""
    q = request.args.get("q", "").strip()
    mode = request.args.get("mode", "hybrid")
    try:
        top_k = int(request.args.get("top_k", 12))
        top_k = max(1, min(100, top_k))
    except (ValueError, TypeError):
        top_k = 12

    if not q:
        return jsonify({"results": [], "error": "请输入搜索词"})

    results = []
    errors = []

    if mode in ("hybrid", "semantic_only"):
        rag_results = se.rag_search(q, top_k=top_k, mode=mode)
        if rag_results and "error" in rag_results[0]:
            errors.append(rag_results[0]["error"])
        else:
            results.extend(rag_results)

    if mode in ("hybrid", "keyword_only"):
        kw_results = se.keyword_search(q.split(), limit=top_k)
        results.extend(kw_results)

    # Deduplicate by text
    seen = set()
    deduped = []
    for r in results:
        key = r.get("text", r.get("line_text", ""))[:100]
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    # Sort: RAG results by score, keyword by line
    deduped.sort(key=lambda x: x.get("score_hybrid", 0) if x.get("type") == "rag" else 0,
                 reverse=True)

    return jsonify({
        "results": deduped[:top_k],
        "total": len(deduped),
        "query": q,
        "mode": mode,
        "errors": errors,
    })


@app.route("/api/status")
def api_status():
    """Index status API."""
    return jsonify(se.get_rag_status())


@app.route("/api/expand")
def api_expand():
    """Expand context around a chunk."""
    chunk_id = request.args.get("chunk_id", "")
    if not chunk_id:
        return jsonify({"error": "Missing chunk_id"}), 400
    result = se.expand_chunk(chunk_id)
    if result is None:
        return jsonify({"error": "Chunk not found"}), 404
    return jsonify(result)


@app.route("/api/sources")
def api_sources():
    """List all source files."""
    return jsonify(se.get_source_files())


@app.route("/source/<path:source_path>")
def view_source(source_path):
    """Read and display a source file."""
    content = se.read_source_file(source_path)
    if content is None:
        return render_template("error.html", message="文件未找到"), 404

    fname = Path(source_path).name
    info = se.SOURCE_INFO.get(fname, "")
    return render_template("source.html",
                           source_path=source_path,
                           source_name=fname,
                           source_info=info,
                           content=content)


@app.route("/status")
def status_page():
    """Index status page."""
    return render_template("status.html")


# ---------------------------------------------------------------------------
# AI 问答
# ---------------------------------------------------------------------------


@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    """Get or save API configuration."""
    if request.method == "POST":
        data = request.get_json(force=True)
        cfg.save_config({
            "provider": data.get("provider", "claude"),
            "api_key": data.get("api_key", ""),
            "api_base": data.get("api_base", ""),
            "model": data.get("model", ""),
            "enabled": data.get("enabled", False),
        })
        return jsonify({"status": "ok"})

    config = cfg.load_config()
    # Never send full key back — mask it
    masked = dict(config)
    if masked["api_key"]:
        k = masked["api_key"]
        masked["api_key"] = k[:4] + "****" + k[-4:] if len(k) > 8 else "****"
    return jsonify(masked)


@app.route("/api/ai-search")
def api_ai_search():
    """AI search: RAG search → AI synthesis."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"answer": "", "error": "请输入问题"})

    config = cfg.load_config()
    if not config.get("enabled"):
        return jsonify({"answer": "", "error": "AI 问答未启用，请在设置页面配置 API"})

    # Step 1: RAG search
    top_k = 15
    rag_results = se.rag_search(q, top_k=top_k, mode="hybrid")
    if rag_results and "error" in rag_results[0]:
        return jsonify({"answer": "", "error": rag_results[0]["error"]})

    # Step 2: Build context
    context = ai.build_context(rag_results)

    # Step 3: AI synthesis
    result = ai.ask_ai(q, context, config)
    return jsonify({
        "answer": result["answer"],
        "error": result["error"],
        "sources": [{
            "source": r["source"],
            "source_pretty": r["source_pretty"],
        } for r in rag_results[:5]],
    })


@app.route("/settings")
def settings_page():
    """API settings page."""
    return render_template("settings.html")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════╗
║    红楼梦研究 · RAG 搜索                 ║
║    http://0.0.0.0:{PORT}                 ║
║                                           ║
╚══════════════════════════════════════════╝
""", file=sys.stderr)

    app.run(host="0.0.0.0", port=PORT, debug=False)
