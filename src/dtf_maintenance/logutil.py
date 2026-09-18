"""Journal fichier + callback UI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path


class Logger:
    def __init__(self, log_dir: Path) -> None:
        log_dir.mkdir(parents=True, exist_ok=True)
        self.path = log_dir / "controller.log"

    def line(self, message: str) -> str:
        stamped = f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}"
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(stamped + "\n")
        return stamped
