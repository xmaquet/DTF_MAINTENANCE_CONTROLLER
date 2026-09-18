"""Chargement de la configuration YAML (stdlib)."""

from __future__ import annotations

from pathlib import Path
from typing import Any


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
            parent[key] = value[1:-1]
        else:
            parent[key] = value
    return root


def load_config(path: Path | None = None) -> dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parents[2] / "config" / "config.yaml"
    return _parse_simple_yaml(path.read_text(encoding="utf-8"))
