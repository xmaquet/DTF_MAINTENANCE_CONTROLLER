"""Détection lecture seule d'un print utilisateur (fichiers locaux)."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

# Espaces autorisés (ex. «ERASMART Quality Evaluation.prn»). «:» exclu : timestamps [HH:MM:SS].
_PRN_NAME = re.compile(r"([^\\/:*?\"<>|\r\n\[\]]+\.prn)", re.IGNORECASE)
_JOB_PREFIX = re.compile(r"^作业")


def last_user_print(cfg: dict) -> tuple[datetime | None, str]:
    """Retourne (horodatage, source). Check / ~section ne comptent pas."""
    candidates: list[tuple[datetime, str]] = []
    prnlist = Path(cfg["paths"]["inkone_prnlist"])
    jobs = Path(cfg["paths"]["inkone_jobs"])
    log_dir = Path(cfg["paths"]["printexp_log_dir"])

    if prnlist.is_dir():
        for p in prnlist.glob("*.prn"):
            candidates.append((_from_mtime(p), f"PrnList:{p.name}"))
    if jobs.is_dir():
        for p in jobs.iterdir():
            if p.is_dir() and p.name != ".":
                candidates.append((_from_mtime(p), f"Jobs:{p.name}"))

    log = log_dir / f"Log[{datetime.now():%Y_%m_%d}].txt"
    if log.is_file():
        hit = _latest_named_prn_in_log(log)
        if hit:
            candidates.append(hit)

    if not candidates:
        return None, "aucune trace"
    best = max(candidates, key=lambda x: x[0])
    return best[0], best[1]


def print_in_progress(cfg: dict, window_seconds: int = 90) -> bool:
    """HYPOTHÈSE : Moving récent + ~section ou .prn nommé dans le log du jour."""
    log = Path(cfg["paths"]["printexp_log_dir"]) / f"Log[{datetime.now():%Y_%m_%d}].txt"
    if not log.is_file():
        return False
    try:
        lines = _read_log_text(log).splitlines()[-80:]
    except OSError:
        return False
    text = "\n".join(lines)
    moving = "ReceiveSignal Moving" in text
    ripish = ("~section" in text) or bool(_PRN_NAME.search(text))
    return moving and ripish


def printexp_running() -> bool:
    try:
        import subprocess

        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq PrintExp_X64.exe"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        return "PrintExp_X64.exe" in (r.stdout or "")
    except OSError:
        return False


def _read_log_text(path: Path) -> str:
    """PrintExp Log[YYYY_MM_DD].txt est UTF-16 LE BOM (OBSERVÉ 2026-09-18)."""
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    if raw.startswith(b"\xef\xbb\xbf"):
        return raw.decode("utf-8-sig")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="ignore")


def _from_mtime(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime)


def _clean_prn_name(raw: str) -> str:
    name = Path(raw.strip()).name
    return _JOB_PREFIX.sub("", name)


def _latest_named_prn_in_log(log: Path) -> tuple[datetime, str] | None:
    raw = _read_log_text(log)
    latest: tuple[datetime, str] | None = None
    for line in raw.splitlines():
        if "~section" in line.lower():
            continue
        m = _PRN_NAME.search(line)
        if not m:
            continue
        name = _clean_prn_name(m.group(1))
        if not name or name.lower().startswith("~section"):
            continue
        ts = _timestamp_from_log_line(line)
        if ts is None:
            continue
        if latest is None or ts > latest[0]:
            latest = (ts, f"PrintExp-log:{name}")
    return latest


def _timestamp_from_log_line(line: str) -> datetime | None:
    m = re.search(r"\[(\d{2}):(\d{2}):(\d{2})", line)
    if not m:
        return None
    now = datetime.now()
    return now.replace(
        hour=int(m.group(1)),
        minute=int(m.group(2)),
        second=int(m.group(3)),
        microsecond=0,
    )
