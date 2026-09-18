"""Lecture seule : montrer ce que last_user_print voit. Pas de clic."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dtf_maintenance.config import load_config
from dtf_maintenance.detect import last_user_print, print_in_progress, printexp_running

cfg = load_config()
last, src = last_user_print(cfg)
print("printexp_running", printexp_running())
print("print_in_progress", print_in_progress(cfg))
print("last_user_print", last, src)

log = Path(cfg["paths"]["printexp_log_dir"]) / "Log[2026_09_18].txt"
print("log_exists", log.is_file(), log)
if log.is_file():
    text = log.read_text(encoding="utf-8", errors="ignore")
    hits = [ln for ln in text.splitlines() if "ERASMART" in ln.upper() or ".prn" in ln.lower()]
    print("prn_or_erasmart_lines", len(hits))
    for ln in hits[:40]:
        print(ln[:240])
