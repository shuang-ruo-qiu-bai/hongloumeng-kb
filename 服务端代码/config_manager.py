"""API 配置管理 — 保存/读取用户设置的 API Key 和提供商"""
from __future__ import annotations

import json
import os
from pathlib import Path

# 配置文件存在应用目录下的 config/ 中
_CONFIG_DIR = Path(__file__).resolve().parent / "config"
CONFIG_DIR = Path(os.environ.get("HLM_CONFIG_DIR", str(_CONFIG_DIR)))
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "provider": "deepseek",    # deepseek | claude | openai | ollama
    "api_key": "",
    "api_base": "",
    "model": "",
    "enabled": False,
}

PROVIDER_DEFAULTS = {
    "deepseek": {
        "api_base": "https://api.deepseek.com",
        "model": "deepseek-v4-flash",
    },
    "claude": {
        "api_base": "https://api.anthropic.com",
        "model": "claude-sonnet-4-20250514",
    },
    "openai": {
        "api_base": "https://api.openai.com/v1",
        "model": "gpt-4o-mini",
    },
    "ollama": {
        "api_base": "http://127.0.0.1:11434",
        "model": "qwen2.5:7b",
    },
}


def load_config() -> dict:
    """Load user config, return defaults if not found."""
    cfg = dict(DEFAULT_CONFIG)
    paths = [CONFIG_FILE, Path("/tmp/hlm-config/config.json")]
    for p in paths:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                cfg.update(data)
                return cfg
            except (json.JSONDecodeError, OSError):
                continue
    return cfg


def save_config(config: dict) -> None:
    """Save user config to disk."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        # Fallback to /tmp if primary path is unwritable
        fallback_dir = Path("/tmp/hlm-config")
        fallback_dir.mkdir(parents=True, exist_ok=True)
        (fallback_dir / "config.json").write_text(
            json.dumps(config, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def get_provider_defaults(provider: str) -> dict:
    """Get default API base and model for a provider."""
    return PROVIDER_DEFAULTS.get(provider, {})
