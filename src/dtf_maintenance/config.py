"""Chargement de la configuration YAML (stdlib)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATH = ROOT / "config" / "config.yaml"
USER_PATH = ROOT / "config" / "user.yaml"


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse le YAML plat/indenté de config.yaml sans PyYAML."""
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        key, _, value = line.strip().partition(":")
        key = key.strip()
        value = value.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if not value:
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
            continue
        if value in ("true", "false"):
            parent[key] = value == "true"
        elif value.isdigit():
            parent[key] = int(value)
        elif (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            parent[key] = value[1:-1].replace("\\\\", "\\")
        else:
            parent[key] = value
    return root


def _merge(base: dict[str, Any], over: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = dict(base)
    for key, val in over.items():
        if isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], val)
        else:
            out[key] = val
    return out


def _dump_simple_yaml(data: dict[str, Any], indent: int = 0) -> str:
    lines: list[str] = []
    pad = " " * indent
    for key, val in data.items():
        if isinstance(val, dict):
            lines.append(f"{pad}{key}:")
            dumped = _dump_simple_yaml(val, indent + 2)
            if dumped:
                lines.append(dumped)
        elif isinstance(val, bool):
            lines.append(f"{pad}{key}: {'true' if val else 'false'}")
        elif isinstance(val, str):
            esc = val.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{pad}{key}: "{esc}"')
        else:
            lines.append(f"{pad}{key}: {val}")
    return "\n".join(lines)


def load_config(path: Path | None = None) -> dict[str, Any]:
    cfg_path = path or DEFAULT_PATH
    cfg = _parse_simple_yaml(cfg_path.read_text(encoding="utf-8"))
    if USER_PATH.is_file():
        cfg = _merge(cfg, _parse_simple_yaml(USER_PATH.read_text(encoding="utf-8")))
    cfg.setdefault("controller", {})
    cfg["controller"].setdefault("clean_level", "auto")
    cfg.setdefault("paths", {})
    cfg["paths"].setdefault("maintenance_prn", "")
    return cfg


def save_user_settings(
    *,
    slot_hour: int,
    slot_minute: int,
    strong_idle_days: int,
    clean_level: str,
    maintenance_prn: str,
) -> Path:
    """Persiste les réglages UI. dry_run et allow_weak restent gelés dans config.yaml."""
    level = clean_level if clean_level in ("auto", "normal", "strong") else "auto"
    data = {
        "controller": {
            "slot_hour": int(slot_hour),
            "slot_minute": int(slot_minute),
            "strong_idle_days": int(strong_idle_days),
            "clean_level": level,
        },
        "paths": {
            "maintenance_prn": maintenance_prn,
        },
    }
    USER_PATH.parent.mkdir(parents=True, exist_ok=True)
    USER_PATH.write_text(_dump_simple_yaml(data) + "\n", encoding="utf-8")
    return USER_PATH
