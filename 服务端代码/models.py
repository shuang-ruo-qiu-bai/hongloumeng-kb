"""用户 / 额度数据模型（sqlite3 + Flask-Login）"""
from __future__ import annotations

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

_DB_DIR = Path(__file__).resolve().parent / "data"
_DB_PATH = _DB_DIR / "hongloumeng.db"

_local = threading.local()


def _get_db() -> sqlite3.Connection:
    """线程安全的数据库连接。"""
    if not hasattr(_local, "conn") or _local.conn is None:
        _DB_DIR.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        _local.conn = conn
    return _local.conn


def init_db():
    """初始化数据库表。"""
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    UNIQUE NOT NULL,
            password_hash TEXT  NOT NULL,
            balance     INTEGER NOT NULL DEFAULT 5,
            is_admin    INTEGER NOT NULL DEFAULT 0,
            is_lifetime INTEGER NOT NULL DEFAULT 0,
            subscription_end TEXT DEFAULT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id          TEXT PRIMARY KEY,
            user_id     INTEGER NOT NULL,
            title       TEXT NOT NULL DEFAULT '\u65b0\u5bf9\u8bdd',
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS chat_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    _ensure_admin()


def _ensure_admin():
    """如果尚无管理员，创建一个默认管理员账号。"""
    conn = _get_db()
    cur = conn.execute("SELECT COUNT(*) FROM users WHERE is_admin=1")
    if cur.fetchone()[0] == 0:
        pw = generate_password_hash("admin888")
        conn.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, is_admin, balance, is_lifetime) VALUES (?, ?, 1, 999999, 1)",
            ("admin", pw),
        )
        conn.commit()


# ---------------------------------------------------------------------------
# User 类（Flask-Login）
# ---------------------------------------------------------------------------

class User(UserMixin):
    """映射 users 表的一行。"""

    def __init__(self, row: sqlite3.Row):
        self.id = row["id"]
        self.username = row["username"]
        self.password_hash = row["password_hash"]
        self.balance = row["balance"]
        self.is_admin = bool(row["is_admin"])
        self.is_lifetime = bool(row["is_lifetime"])
        self.subscription_end = row["subscription_end"]

    # -- 余额相关 --

    @property
    def can_use_ai(self) -> bool:
        """是否有权使用 AI 问答。"""
        if self.is_admin or self.is_lifetime:
            return True
        if self.balance > 0:
            return True
        if self.subscription_end:
            try:
                end = datetime.strptime(self.subscription_end, "%Y-%m-%d")
                if end >= datetime.today():
                    return True
            except ValueError:
                pass
        return False

    def deduct_ai(self) -> bool:
        """扣除一次 AI 问答次数。返回是否扣成功。"""
        if self.is_admin or self.is_lifetime:
            return True  # 管理员和终身会员不扣
        if self.subscription_end:
            try:
                end = datetime.strptime(self.subscription_end, "%Y-%m-%d")
                if end >= datetime.today():
                    return True  # 订阅期内不扣
            except ValueError:
                pass
        conn = _get_db()
        conn.execute("UPDATE users SET balance = balance - 1 WHERE id=? AND balance > 0", (self.id,))
        conn.commit()
        if conn.total_changes == 0:
            return False
        self.balance -= 1
        return True

    # -- 工厂方法 --

    @classmethod
    def get(cls, user_id: int) -> User | None:
        conn = _get_db()
        cur = conn.execute("SELECT * FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        return cls(row) if row else None

    @classmethod
    def find_by_username(cls, username: str) -> User | None:
        conn = _get_db()
        cur = conn.execute("SELECT * FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        return cls(row) if row else None

    @classmethod
    def create(cls, username: str, password: str) -> User:
        conn = _get_db()
        pw_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, password_hash, balance) VALUES (?, ?, 5)",
            (username, pw_hash),
        )
        conn.commit()
        cur = conn.execute("SELECT * FROM users WHERE username=?", (username,))
        return cls(cur.fetchone())

    @classmethod
    def update_balance(cls, user_id: int, amount: int):
        """增加或减少用户余额（amount 可正可负）。"""
        conn = _get_db()
        conn.execute("UPDATE users SET balance = MAX(0, balance + ?) WHERE id=?", (amount, user_id))
        conn.commit()

    @classmethod
    def toggle_lifetime(cls, user_id: int, value: bool):
        conn = _get_db()
        conn.execute("UPDATE users SET is_lifetime=? WHERE id=?", (1 if value else 0, user_id))
        conn.commit()

    @classmethod
    def set_admin(cls, user_id: int, value: bool):
        conn = _get_db()
        conn.execute("UPDATE users SET is_admin=? WHERE id=?", (1 if value else 0, user_id))
        conn.commit()

    @classmethod
    def get_all_users(cls) -> list[dict]:
        conn = _get_db()
        cur = conn.execute("SELECT id, username, balance, is_admin, is_lifetime, subscription_end, created_at FROM users ORDER BY id")
        return [dict(r) for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# Chat session helpers
# ---------------------------------------------------------------------------

def create_chat_session(user_id: int, title: str = "新对话") -> str:
    import uuid
    conn = _get_db()
    sid = uuid.uuid4().hex[:16]
    conn.execute(
        "INSERT INTO chat_sessions (id, user_id, title) VALUES (?, ?, ?)",
        (sid, user_id, title),
    )
    conn.commit()
    return sid


def list_chat_sessions(user_id: int) -> list[dict]:
    conn = _get_db()
    cur = conn.execute(
        """SELECT s.id, s.title, s.created_at, s.updated_at,
                  (SELECT content FROM chat_messages WHERE session_id=s.id
                   AND role='user' ORDER BY id DESC LIMIT 1) AS last_query
           FROM chat_sessions s
           WHERE s.user_id = ?
           ORDER BY s.updated_at DESC""",
        (user_id,),
    )
    return [dict(r) for r in cur.fetchall()]


def rename_chat_session(session_id: str, title: str, user_id: int) -> bool:
    conn = _get_db()
    cur = conn.execute(
        "UPDATE chat_sessions SET title=?, updated_at=datetime('now') WHERE id=? AND user_id=?",
        (title, session_id, user_id),
    )
    conn.commit()
    return cur.rowcount > 0


def delete_chat_session(session_id: str, user_id: int) -> bool:
    conn = _get_db()
    conn.execute("DELETE FROM chat_messages WHERE session_id=?", (session_id,))
    cur = conn.execute(
        "DELETE FROM chat_sessions WHERE id=? AND user_id=?",
        (session_id, user_id),
    )
    conn.commit()
    return cur.rowcount > 0


def delete_chat_sessions(session_ids: list[str], user_id: int) -> int:
    """批量删除多个对话（仅删除属于该用户的）。返回实际删除数。"""
    if not session_ids:
        return 0
    conn = _get_db()
    placeholders = ",".join("?" * len(session_ids))
    params = session_ids + [user_id]
    # CASCADE 会自动删除关联的 chat_messages
    cur = conn.execute(
        f"DELETE FROM chat_sessions WHERE id IN ({placeholders}) AND user_id=?",
        params,
    )
    conn.commit()
    return cur.rowcount


def get_chat_messages(session_id: str) -> list[dict]:
    conn = _get_db()
    cur = conn.execute(
        "SELECT role, content, created_at FROM chat_messages WHERE session_id=? ORDER BY id",
        (session_id,),
    )
    return [dict(r) for r in cur.fetchall()]


def add_chat_message(session_id: str, role: str, content: str):
    conn = _get_db()
    conn.execute(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content),
    )
    conn.execute(
        "UPDATE chat_sessions SET updated_at=datetime('now') WHERE id=?",
        (session_id,),
    )
    conn.commit()


def auto_title_session(session_id: str, first_query: str):
    """Use first query as session title (truncated)."""
    title = first_query.strip()[:30]
    if len(first_query) > 30:
        title += "..."
    conn = _get_db()
    conn.execute("UPDATE chat_sessions SET title=? WHERE id=?", (title, session_id))
    conn.commit()


def session_exists(session_id, user_id):
    conn = _get_db()
    cur = conn.execute("SELECT 1 FROM chat_sessions WHERE id=? AND user_id=?", (session_id, user_id))
    return cur.fetchone() is not None
