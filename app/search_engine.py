"""Search engine wrapper — combines keyword search + RAG hybrid search."""

from __future__ import annotations

import os
import sqlite3
import sys
from pathlib import Path
from typing import Any

# Paths — auto-detect KB root relative to this file's location
_THIS_DIR = Path(__file__).resolve().parent
KB_ROOT = Path(os.environ.get(
    "HLM_KB_ROOT",
    str(_THIS_DIR.parent)  # default: parent of windows-app/
)).expanduser().resolve()

CHROMA_DIR = KB_ROOT / "chroma"
SCRIPTS_DIR = _THIS_DIR / "scripts"  # bundled scripts directory

sys.path.insert(0, str(SCRIPTS_DIR))

# ---------------------------------------------------------------------------
# Source metadata
# ---------------------------------------------------------------------------

SOURCE_INFO: dict[str, str] = {
    "红楼梦脂评汇校本-cleaned.txt": "曹雪芹 著 · 脂砚斋 评 · 红楼梦原著（脂评汇校本）",
    "红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所)-cleaned.txt": "红楼梦原著 · 中国艺术研究院校注本",
    "红楼梦辨 (俞平伯)-cleaned.txt": "俞平伯 · 新红学开山之作 · 1923",
    "陈维昭：红学通史.md": "陈维昭 · 红学史通览 · 上海人民出版社 2005",
    "红楼梦新证 (增订本) (周汝昌)-cleaned.txt": "周汝昌 · 红学考证里程碑 · 增订本",
    "红楼梦魇 (张爱玲)-cleaned.txt": "张爱玲 · 红楼梦研究随笔 · 1977",
    "红楼梦探源 (吴世昌).pdf_by_PaddleOCR-VL-1.6.md": "吴世昌 · 红楼梦英文研究 · 牛津大学出版社",
    "胡适红楼研究论述全编 (胡適).pdf_by_PaddleOCR-VL-1.5.md": "胡适 · 新红学奠基人 · 考证文集",
    "红楼梦诗词曲赋全解-cleaned.txt": "红楼梦诗词注释解析",
    "石头记索隐 蔡元培-cleaned.txt": "蔡元培 · 索隐派代表作 · 1917",
    "红楼梦的两个世界 (余英时).pdf_by_PaddleOCR-VL-1.6.md": "余英时 · 红学文学批评典范 · 1970年代",
    "不惑之获：《红楼梦学刊》40年精选文集（全三卷） (《红楼梦学刊》编辑部)-cleaned.txt": "《红楼梦学刊》40周年精选 · 三卷本",
    "王国维《红楼梦评论》笺说 (俞晓红).pdf_by_PaddleOCR-VL-1.6.md": "王国维 原著 / 俞晓红 笺说 · 1904 美学批评",
    "独上红楼 (梁归智).pdf_by_PaddleOCR-VL-1.5.md": "梁归智 · 探佚学 · 红楼梦后四十回研究",
    "红楼梦研究稀见资料汇编.pdf_by_PaddleOCR-VL-1.6.md": "稀见红学资料汇编 · 早期红学文献",
    "吴世昌 红楼碎墨 .pdf_by_PaddleOCR-VL-1.6.md": "吴世昌 · 红学论文随笔集",
    "红楼梦考证 (胡适)-cleaned.txt": "胡适 · 《红楼梦考证》单行本 · 1921",
    "红楼梦新解 (潘重规).pdf_by_PaddleOCR-VL-1.6.md": "潘重规 · 香港红学代表 · 新解",
    "林黛玉家产与贾家谋夺说.md": "红学话题笔记 · 林黛玉家产争议",
    "红楼梦藏书目录.txt": "红学藏书目录",
    "《红楼梦的法律世界》 (尹伊君著) -cleaned.txt": "尹伊君 · 从法律视角解读红楼梦",
    "命若朝霜：《红楼梦》里的法律、社会与女性 (柯岚) -cleaned.txt": "柯岚 · 法律社会史视野下的红楼梦",
    "红楼梦大辞典 增订本.pdf_by_PaddleOCR-VL-1.5.md": "红楼梦大辞典 · 增订本",
}

# ---------------------------------------------------------------------------
# RAG search (import from existing scripts)
# ---------------------------------------------------------------------------

_rag_search_module = None


def _get_rag_module():
    global _rag_search_module
    if _rag_search_module is not None:
        return _rag_search_module
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "rag_search",
            str(SCRIPTS_DIR / "rag_search.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _rag_search_module = mod
        return mod
    except Exception as e:
        return None


# ---------------------------------------------------------------------------
# Keyword search (adapted from search_corpus.py)
# ---------------------------------------------------------------------------


def get_source_files():
    """Return list of indexed source files with metadata."""
    files = []
    for rel_dir in ["raw/红楼梦", "notes", "topics"]:
        base = KB_ROOT / rel_dir
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".txt", ".md", ".json"}:
                continue
            rel = str(path.relative_to(KB_ROOT))
            info = SOURCE_INFO.get(path.name, "")
            file_size = path.stat().st_size
            files.append({
                "path": rel,
                "name": path.name,
                "info": info,
                "size": file_size,
                "human_size": _human_size(file_size),
            })
    return files


def _human_size(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def keyword_search(terms: list[str], root: Path | None = None,
                   any_term: bool = False, limit: int = 80) -> list[dict[str, Any]]:
    """Simple line-based keyword search."""
    root = root or KB_ROOT
    results: list[dict[str, Any]] = []
    search_dirs = [
        root / "raw" / "红楼梦",
        root / "notes",
        root / "topics",
    ]

    for base in search_dirs:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in {".txt", ".md", ".json"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            rel = str(path.relative_to(root))
            lines = text.split("\n")
            for i, line in enumerate(lines):
                folded = line.casefold()
                hits = [t.casefold() in folded for t in terms]
                match = any(hits) if any_term else all(hits)
                if match:
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context_lines = []
                    for j in range(start, end):
                        context_lines.append({
                            "line_num": j + 1,
                            "text": lines[j],
                            "is_match": j == i,
                        })
                    results.append({
                        "source": rel,
                        "source_pretty": SOURCE_INFO.get(path.name, path.name),
                        "line": i + 1,
                        "line_text": line[:200],
                        "context": context_lines,
                        "type": "keyword",
                    })
                    if len(results) >= limit:
                        return results
    return results


# ---------------------------------------------------------------------------
# RAG / hybrid search
# ---------------------------------------------------------------------------


def rag_search(query: str, top_k: int = 12, mode: str = "hybrid",
               json_output: bool = False) -> list[dict[str, Any]]:
    """Hybrid RAG search returning structured results."""
    rag = _get_rag_module()
    if rag is None:
        return [{"error": "RAG engine not available. Is sentence-transformers installed?"}]

    # Re-run with module's root set
    rag.ROOT = KB_ROOT

    chroma_path = KB_ROOT / CHROMA_DIR.name
    if not chroma_path.exists():
        return [{"error": f"Chroma index not found at {chroma_path}"}]

    import chromadb
    client = chromadb.PersistentClient(path=str(chroma_path))
    try:
        coll = client.get_collection("hongloumeng")
    except Exception:
        return [{"error": "Collection 'hongloumeng' not found. Run rag_index.py first."}]

    results = rag.hybrid_search(coll, query, k=top_k * 2)

    if mode == "keyword_only":
        results.sort(key=lambda x: x["score_bm25"], reverse=True)
    elif mode == "semantic_only":
        results.sort(key=lambda x: x["score_vector"], reverse=True)

    out = []
    for r in results[:top_k]:
        source_path = r["source"]
        fname = Path(source_path).name
        out.append({
            "text": r["text"][:2000],
            "source": source_path,
            "source_pretty": SOURCE_INFO.get(fname, fname),
            "chunk_id": r["chunk_id"],
            "score_hybrid": r["score_hybrid"],
            "score_vector": r["score_vector"],
            "score_bm25": r["score_bm25"],
            "type": "rag",
        })

    return out


def expand_chunk(chunk_id: str, context_lines: int = 80) -> dict[str, Any] | None:
    """Expand context around a chunk."""
    rag = _get_rag_module()
    if rag is None:
        return None

    rag.ROOT = KB_ROOT
    chroma_path = KB_ROOT / CHROMA_DIR.name
    import chromadb
    client = chromadb.PersistentClient(path=str(chroma_path))
    coll = client.get_collection("hongloumeng")

    parts = chunk_id.rsplit("#", 1)
    if len(parts) < 2:
        return None

    results = coll.get(ids=[chunk_id], include=["documents", "metadatas"])
    if not results["ids"]:
        return None

    meta = results["metadatas"][0]
    expanded = rag.expand_chunk(meta["source"], meta["chunk_start"],
                                meta["chunk_end"], context_lines)

    fname = Path(meta["source"]).name
    return {
        "text": expanded,
        "source": meta["source"],
        "source_pretty": SOURCE_INFO.get(fname, fname),
        "chunk_id": chunk_id,
    }


def get_rag_status() -> dict[str, Any]:
    """Get index status as a dict."""
    chroma_path = KB_ROOT / CHROMA_DIR.name
    track_db = KB_ROOT / CHROMA_DIR.name / "track_hongloumeng.db"

    status = {
        "chroma_exists": chroma_path.exists(),
        "chroma_size": "",
    }

    if chroma_path.exists():
        # Size
        total = sum(
            f.stat().st_size for f in chroma_path.rglob("*") if f.is_file()
        )
        status["chroma_size"] = _human_size(total)

    if track_db.exists():
        conn = sqlite3.connect(str(track_db))
        row = conn.execute(
            "SELECT count(*), sum(num_chunks) FROM files"
        ).fetchone()
        conn.close()
        status["total_files"] = row[0] or 0
        status["total_chunks"] = row[1] or 0
    else:
        status["total_files"] = 0
        status["total_chunks"] = 0

    # Model info
    embed_model = os.environ.get("HLM_EMBED_MODEL", "shibing624/text2vec-base-chinese")
    status["embed_model"] = embed_model

    return status


def read_source_file(source_path: str, max_chars: int = 500_000) -> str | None:
    """Read content from a source file."""
    full = (KB_ROOT / source_path).resolve()
    # Prevent path traversal outside knowledge base
    if not str(full).startswith(str(KB_ROOT.resolve())):
        return None
    if not full.exists() or not full.is_file():
        return None
    try:
        text = full.read_text(encoding="utf-8", errors="replace")
        return text[:max_chars]
    except OSError:
        return None


