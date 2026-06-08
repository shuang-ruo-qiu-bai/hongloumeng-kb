"""/opt/hongloumeng/app/app.py — 红楼梦研究主应用"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))

from flask import (
    Flask, jsonify, render_template, request, send_from_directory, url_for,
)
from flask_login import (
    LoginManager, current_user, login_required, login_user, logout_user,
)

import ai_engine as ai
import config_manager as cfg
import data as site_data
import search_engine as se
from auth import auth_bp
from models import (
    User, create_chat_session, list_chat_sessions,
    rename_chat_session, delete_chat_session, delete_chat_sessions,
    get_chat_messages, add_chat_message, auto_title_session,
    session_exists,
)

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "hongloumeng-dev-secret-key")
app.config["JSON_AS_ASCII"] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

app.register_blueprint(auth_bp, url_prefix="")

@app.context_processor
def inject_active_page():
    from flask import request as _req
    endpoint = _req.endpoint or ''
    page_map = {
        'index': 'home',
        'canon': 'canon',
        'poems': 'poems',
        'editions': 'editions',
        'customs': 'customs',
        'history': 'history',
        'paintings': 'paintings',
        'scholars': 'scholars',
        'library': 'library',
    }
    return {'active_page': page_map.get(endpoint, '')}


@login_manager.user_loader
def load_user(user_id):
    return User.get(int(user_id))


# ---------------------------------------------------------------------------
# Template routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Main search page."""
    return render_template("index.html",
                           query=request.args.get("q", ""),
                           mode=request.args.get("mode", "hybrid"))

@app.route("/promo")
def promo():
    """Promotional landing page for WeChat sharing."""
    return render_template("promo.html")


@app.route("/history")
def history():
    from data import HISTORY_PERIODS
    return render_template("history.html", periods=HISTORY_PERIODS)


@app.route("/scholars")
def scholars():
    from data import SCHOLARS
    from data import SCHOLAR_ORDER
    return render_template("scholars.html", scholars=SCHOLARS, order=SCHOLAR_ORDER)


@app.route("/scholar/<slug>")
def scholar_detail(slug):
    info = site_data.SCHOLARS.get(slug)
    return render_template("scholar_detail.html", slug=slug, info=info)


@app.route("/library")
def library():
    import os, glob, re as _re
    books_dir = "/opt/hongloumeng/books/红楼梦"

    def _parse_book(fn):
        """Parse filename into (book_name, author)."""
        name = fn.strip()
        # Handle OCR suffix
        if name.endswith('.md'):
            name = _re.sub(r'_by_PaddleOCR.*', '', name)
        # Remove extension
        if '.' in name:
            parts = name.rsplit('.', 1)
            name = parts[0].strip()
        book_name = name
        author = ''
        # Known specific books
        known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦脂评汇校本': '曹雪芹、脂砚斋'}
        # Direct name → (book_name, author) overrides (matched before parentheses)
        named_books = {
            '红楼风俗名物谭：邓云乡论红楼梦': ('红楼风俗名物谭', '邓云乡'),
            '不惑之获：《红楼梦学刊》40年精选文集（全三卷） (《红楼梦学刊》编辑部)': ('《红楼梦学刊》选集', '《红楼梦学刊》编辑部'),
        }
        if name in named_books:
            return named_books[name]
        # Pattern: last (...) as author
        matches = list(_re.finditer(r'\(([^()]+?)(?:著)?\)\s*$', name))
        if not matches:
            matches = list(_re.finditer(r'（([^（）]+?)）\s*$', name))
        if matches:
            m = matches[-1]
            candidate = m.group(1).strip()
            if len(candidate) <= 50 and '卷' not in candidate:
                author = _re.sub(r'\s+', ' ', candidate).strip()
                book_name = name[:m.start()].strip()
                # Special case: 原著 first book
                if book_name == '红楼梦' and name.endswith(')'):
                    author = '曹雪芹著，无名氏续，程伟元、高鹗整理'

                return book_name, author
        # Known books
        for k, v in known.items():
            if k in name:
                return name, v
        # Name at start pattern: author + space + book
        m = _re.match(r'^([一-鿿]{2,4})\s+', name)
        if m:
            known_authors = {'吴世昌','胡适','俞平伯','周汝昌','张爱玲','王昆仑','何其芳','李希凡','冯其庸','余英时','林冠夫','梁归智','蔡元培','潘重规','柯岚','俞晓红','胡適','陈维昭'}
            if m.group(1) in known_authors:
                return name[m.end():].strip(), m.group(1)
        # Colon format: 作者：书名
        m = _re.match(r'^([一-鿿]{2,4})[：:](.+)$', name)
        if m and _re.match(r'^[一-鿿]{2,4}$', m.group(1)):
            return m.group(2).strip(), m.group(1).strip()
        # Space-separated author at end
        if ' ' in name:
            parts = name.rsplit(' ', 1)
            if _re.match(r'^[一-鿿·]{2,4}$', parts[1].strip()):
                return parts[0].strip(), parts[1].strip()
        # Author:book-title format at start
        m = _re.match(r'^([一-鿿]{2,4})[：:]\s*(.+)$', name)
        if m:
            return m.group(2).strip(), m.group(1).strip()
        return book_name, author

    # Publication years for 论著 chronological sorting
    BOOK_YEARS = {
        '王国维《红楼梦评论》': 1904,
        '石头记索隐': 1916,
        '红楼梦考证': 1921,
        '红楼梦辨': 1923,
        '红楼梦新证': 1953,
        '红楼梦探源': 1961,
        '红楼梦新解': 1963,
        '红楼梦魇': 1977,
        '红楼梦的两个世界': 1978,
        '红楼风俗名物谭': 1982,
        '独上红楼': 1992,
        '红楼梦研究稀见资料汇编': 2000,
        '胡适红楼研究论述全编': 2000,
        '红楼梦诗词曲赋全解': 2001,
        '红楼梦大辞典': 2005,
        '红学通史': 2005,
        '红楼梦版本论': 2006,
        '红楼梦的法律世界': 2009,
        '红楼碎墨': 2010,
        '命若朝霜': 2024,
        '不惑之获': 2019,
        '《红楼梦学刊》选集': 2019,
    }

    categories = []
    for subdir in sorted(os.listdir(books_dir)):
        subpath = os.path.join(books_dir, subdir)
        if not os.path.isdir(subpath) or subdir.startswith("."):
            continue
        books = []
        for f in sorted(glob.glob(os.path.join(subpath, "*"))):
            fn = os.path.basename(f)
            if fn.startswith("._") or fn.startswith("."):
                continue
            ext = os.path.splitext(fn)[1].upper().replace(".", "")
            if ext in ('MD', 'TXT', 'PY', 'JSON'):
                continue
            size_kb = os.path.getsize(f) // 1024
            size_str = "%dKB" % size_kb if size_kb < 1024 else "%.1fMB" % (size_kb/1024.0)
            book_name, author = _parse_book(fn)
            books.append({"path": subdir + "/" + fn, "book_name": book_name, "author": author, "format": ext, "size": size_str})
        # Sort 论著 chronologically by year, unknown years at end
        if subdir == "论著":
            def _sort_year(b):
                name = b['book_name']
                for key, year in BOOK_YEARS.items():
                    if key in name:
                        return year
                return 9999
            books.sort(key=_sort_year)
        categories.append({"name": subdir, "books": books})
    return render_template("library.html", categories=categories)


@app.route("/canon")
def canon():
    import json, os
    novel_path = os.path.join(os.path.dirname(__file__), "novel_data.json")
    with open(novel_path) as f:
        data = json.load(f)
    return render_template("canon.html", chapters=data["chapters"])



@app.route("/api/canon/chapter/<int:num>")
def api_canon_chapter(num):
    import json, os, re
    novel_path = os.path.join(os.path.dirname(__file__), "novel_data.json")
    with open(novel_path) as f:
        data = json.load(f)
    for ch in data["chapters"]:
        if ch["num"] == num:
            content = ch["content"]
            lines = content.split("\n")
            body_lines = []
            notes_lines = []
            in_notes = False
            for line in lines:
                stripped = line.strip()
                if not in_notes and re.match(r"^(?:\[\d+\]|[〔\[]([一二三四五六七八九十百零〇]+)[〕\]])", stripped):
                    in_notes = True
                if in_notes:
                    notes_lines.append(line)
                else:
                    body_lines.append(line)
            body_text = "\n".join(body_lines).strip()
            # Strip leading duplicated chapter title lines
            title_val = ch["title"]
            blines = body_text.split("\n")
            annotated_title = None
            while blines and (blines[0].strip() == title_val or not blines[0].strip() or re.sub(r"\[\d+\]|[〔\[]([一二三四五六七八九十百零〇]+)[〕\]]", "", blines[0].strip()) == title_val):
                if re.search(r"\[\d+\]|[〔\[]([一二三四五六七八九十百零〇]+)[〕\]]", blines[0].strip()):
                    annotated_title = blines[0].strip()
                blines = blines[1:]
            body_text = "\n".join(blines).strip()

            arabic_notes = []
            aidx = 1
            chinese_notes = []
            for line in notes_lines:
                stripped = line.strip()
                m = re.match(r"^\[(\d+)\](.+)", stripped)
                if m:
                    arabic_notes.append({"num": aidx, "text": m.group(2).strip()})
                    aidx += 1
                m = re.match(r"^[〔\[]([一二三四五六七八九十百零〇]+)[〕\]](.+)", stripped)
                if m:
                    chinese_notes.append({"num": m.group(1), "text": m.group(2).strip()})

            # Renumber inline [N] markers in body_text to match renumbered arabic_notes
            markers_in_body = re.findall(r"\[(\d+)\]", body_text)
            if markers_in_body:
                old_to_new = {}
                counter = 0
                for m in markers_in_body:
                    if m not in old_to_new:
                        counter += 1
                        old_to_new[m] = str(counter)
                def _renumber_inline(m):
                    old = m.group(1)
                    return "[" + old_to_new.get(old, old) + "]"
                body_text = re.sub(r"\[(\d+)\]", _renumber_inline, body_text)

            return jsonify({"title": ch["title"], "content": body_text, "arabic_notes": arabic_notes, "chinese_notes": chinese_notes, "annotated_title": annotated_title})
    return jsonify({"error": "章节不存在"}), 404


@app.route("/api/customs/chapter")
def api_customs_chapter():
    title = request.args.get("title", "")
    if not title:
        return jsonify({"error": "missing title"}), 400
    curated_path = os.path.join(os.path.dirname(__file__), "curated_customs.json")
    with open(curated_path) as f:
        all_chapters = json.load(f)
    for group in all_chapters:
        for item in group:
            if item.get("title") == title:
                return jsonify({"content": item.get("content", "")})
    return jsonify({"error": "章节不存在"}), 404

@app.route("/editions")
def editions():
    return render_template("editions.html")


@app.route("/customs")
def customs():
    return render_template("customs.html", customs_book=site_data.CUSTOMS_BOOK)


@app.route("/paintings")
def paintings():
    return render_template("paintings.html")


@app.route("/poems")
def poems():
    from poems_data import POEM_CATEGORIES
    return render_template("poems.html", categories=POEM_CATEGORIES)


@app.route("/source/<path:source_path>")
def source_view(source_path):
    text = se.read_source_file(source_path)
    return render_template("source.html", source=source_path, text=text)


@app.route("/status")
def status():
    return render_template("status.html")


@app.route("/recharge")
@login_required
def recharge():
    return render_template("recharge.html")


@app.route("/settings")
@login_required
def settings():
    if not current_user.is_admin:
        return render_template("error.html", code=403), 403
    return render_template("settings.html")


# ---------------------------------------------------------------------------
# Search API
# ---------------------------------------------------------------------------

@app.route("/api/search")
def api_search():
    """Search API — returns JSON results."""
    _t0 = time.time()
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
        rag_results = se.rag_search(q, top_k=top_k, mode=mode, original_only=False)
        if rag_results and "error" in rag_results[0]:
            errors.append(rag_results[0]["error"])
        else:
            results.extend(rag_results)

    if mode in ("hybrid", "keyword_only"):
        kw_results = se.keyword_search(q.split(), limit=top_k)
        results.extend(kw_results)

    seen = set()
    deduped = []
    for r in results:
        key = r.get("text", r.get("line_text", ""))[:100]
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    return jsonify({
        "results": deduped,
        "mode": mode,
        "query": q,
        "time": round(time.time() - _t0, 3),
    })


@app.route("/api/expand")
def api_expand():
    chunk_id = request.args.get("chunk_id", "")
    if not chunk_id:
        return jsonify({"error": "missing chunk_id"})
    result = se.expand_chunk(chunk_id)
    return jsonify(result or {"error": "not found"})


@app.route("/api/status")
def api_status():
    return jsonify(se.get_rag_status())


# ---------------------------------------------------------------------------
# AI Chat API
# ---------------------------------------------------------------------------

@app.route("/api/balance")
def api_balance():
    if not current_user.is_authenticated:
        return jsonify({"authenticated": False})
    return jsonify({
        "authenticated": True,
        "can_use_ai": current_user.can_use_ai,
        "balance": current_user.balance,
        "is_lifetime": current_user.is_lifetime,
        "is_admin": current_user.is_admin,
    })


@app.route("/api/ai-chat", methods=["POST"])
def api_ai_chat():
    """AI chat with multi-turn conversation support."""
    data = request.get_json(force=True)
    q = (data.get("message") or "").strip()
    session_id = (data.get("session_id") or "").strip()

    if not q:
        return jsonify({"answer": "", "error": "请输入问题"})

    # 余额检查
    if not current_user.is_authenticated:
        return jsonify({
            "answer": "", "error": "请先登录后再使用 AI 问答",
            "needs_login": True,
        })

    if not current_user.can_use_ai:
        return jsonify({
            "answer": "", "error": f"AI 问答次数已用尽（余额：{current_user.balance} 次），请充值",
            "needs_recharge": True,
            "balance": current_user.balance,
        })

    config = cfg.load_config()
    if not config.get("enabled"):
        return jsonify({"answer": "", "error": "AI 问答未启用，请联系管理员配置 API"})

    # Session management
    is_new = False
    if not session_id or not session_exists(session_id, current_user.id):
        session_id = create_chat_session(current_user.id)
        is_new = True

    # Get conversation history
    history = get_chat_messages(session_id)

    # Save user message
    add_chat_message(session_id, "user", q)

    # RAG search
    top_k = 60
    rag_results = se.rag_search(q, top_k=top_k, mode="hybrid", original_only=False)
    if rag_results and "error" in rag_results[0]:
        return jsonify({"answer": "", "error": rag_results[0]["error"]})

    context = ai.build_context(rag_results)
    result = ai.ask_ai(q, context, config, conversation_history=history)

    # AI 的原始编号已经自洽，body 和 footnotes 的 ID 一一对应，无需重编号

    # 扣除次数
    if result["answer"]:
        current_user.deduct_ai()

    # Save AI response
    if result["answer"]:
        add_chat_message(session_id, "assistant", result["answer"])

    # Auto-title on first turn
    if is_new and result["answer"]:
        auto_title_session(session_id, q)

    return jsonify({
        "answer": result["answer"],
        "error": result["error"],
        "session_id": session_id,
        "is_new": is_new,
        "balance": current_user.balance if current_user.is_authenticated else None,
        "sources": [{
            "source": r["source"],
            "source_pretty": r["source_pretty"],
        } for r in rag_results[:5]],
    })


@app.route("/api/chat/sessions", methods=["GET", "POST", "DELETE"])
@login_required
def api_chat_sessions():
    if request.method == "GET":
        sessions = list_chat_sessions(current_user.id)
        return jsonify({"sessions": sessions})

    if request.method == "DELETE":
        data = request.get_json(force=True) or {}
        ids = data.get("ids", [])
        count = delete_chat_sessions(ids, current_user.id)
        return jsonify({"deleted": count})

    data = request.get_json(force=True) or {}
    title = (data.get("title") or "新对话").strip()
    sid = create_chat_session(current_user.id, title)
    return jsonify({"session_id": sid})


@app.route("/api/chat/sessions/<session_id>/messages", methods=["GET", "POST"])
@login_required
def api_chat_session_messages(session_id):
    if request.method == "GET":
        msgs = get_chat_messages(session_id)
        return jsonify({"messages": msgs})

    data = request.get_json(force=True) or {}
    content = data.get("content", "").strip()
    if content:
        add_chat_message(session_id, "user", content)
    return jsonify({"ok": True})


@app.route("/api/chat/sessions/<session_id>", methods=["PATCH", "DELETE"])
@login_required
def api_chat_session(session_id):
    if request.method == "PATCH":
        data = request.get_json(force=True) or {}
        title = data.get("title", "").strip()
        if title:
            rename_chat_session(session_id, title, current_user.id)
        return jsonify({"ok": True})
    if request.method == "DELETE":
        delete_chat_session(session_id, current_user.id)
        return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

@app.route("/api/admin/lifetime", methods=["POST"])
@login_required
def api_admin_lifetime():
    if not current_user.is_admin:
        return jsonify({"error": "无权限"}), 403
    data = request.get_json(force=True) or {}
    uid = data.get("user_id")
    if not uid:
        return jsonify({"error": "missing user_id"}), 400
    User.toggle_lifetime(uid, True)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _renumber_citations(text):
    """Renumber [N] citation markers — body only, leave footnotes section untouched."""
    parts = re.split(r"(注释[：:])", text, maxsplit=1)
    body = parts[0]
    markers = [(m.start(), m.end(), int(m.group(1))) for m in re.finditer(r"\[(\d+)\]", body)]
    if not markers:
        return text
    old_to_new = {}
    counter = 0
    for _, _, old_num in markers:
        if old_num not in old_to_new:
            counter += 1
            old_to_new[old_num] = counter
    body_list = list(body)
    for pos, end, old_num in reversed(markers):
        new_text = "[%d]" % old_to_new[old_num]
        body_list[pos:end] = list(new_text)
    body = "".join(body_list)
    if len(parts) > 1:
        return body + "".join(parts[1:])
    return body


# ---------------------------------------------------------------------------
# Static file serving
# ---------------------------------------------------------------------------

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)


@app.route("/books/<path:filename>")
def download_book(filename):
    """Download e-book files from /opt/hongloumeng/books/红楼梦/"""
    books_dir = "/opt/hongloumeng/books/红楼梦"
    return send_from_directory(books_dir, filename, as_attachment=True)


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500), 500

@app.route("/admin")
@login_required
def admin_page():
    if not current_user.is_admin:
        return render_template("error.html", code=403), 403
    return render_template("admin.html")
