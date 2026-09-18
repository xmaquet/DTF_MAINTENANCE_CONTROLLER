"""UI Python obligatoire : fermée = pas de maintenance."""

from __future__ import annotations

import sys
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk

from dtf_maintenance.config import load_config
from dtf_maintenance.detect import last_user_print, print_in_progress, printexp_running
from dtf_maintenance.logutil import Logger
from dtf_maintenance.policy import Action, decide, is_slot
from dtf_maintenance.ui_win32 import describe_printexp_controls

ROOT = Path(__file__).resolve().parents[2]


class ControllerApp:
    def __init__(self) -> None:
        self.cfg = load_config()
        self.logger = Logger(ROOT / "logs")
        self.ui_alive = True
        self._fired_minute: str | None = None
        self.root = tk.Tk()
        self.root.title("DTF Maintenance Controller — dry-run")
        self.root.geometry("720x520")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build()
        self._tick()

    def _build(self) -> None:
        pad = {"padx": 12, "pady": 6}
        ttk.Label(
            self.root,
            text="Sans cette fenêtre, aucune maintenance n'est lancée.",
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", **pad)
        self.status = ttk.Label(self.root, text="…", wraplength=680)
        self.status.pack(anchor="w", **pad)
        self.detail = ttk.Label(self.root, text="", wraplength=680)
        self.detail.pack(anchor="w", **pad)
        btns = ttk.Frame(self.root)
        btns.pack(anchor="w", **pad)
        ttk.Button(btns, text="Décision maintenant (dry-run)", command=self._manual_decide).pack(
            side="left", padx=(0, 8)
        )
        ttk.Label(btns, text="Clics PrintExp : désactivés").pack(side="left")
        self.logbox = tk.Text(self.root, height=18, wrap="word", state="disabled")
        self.logbox.pack(fill="both", expand=True, padx=12, pady=8)
        self._log("controller UI started dry_run=true require_ui=true")

    def _on_close(self) -> None:
        self.ui_alive = False
        self._log("UI fermée — maintenance inhibée")
        self.root.destroy()

    def _log(self, msg: str) -> None:
        line = self.logger.line(msg)
        self.logbox.configure(state="normal")
        self.logbox.insert("end", line + "\n")
        self.logbox.see("end")
        self.logbox.configure(state="disabled")

    def _snapshot(self):
        last, src = last_user_print(self.cfg)
        busy = print_in_progress(self.cfg)
        running = printexp_running()
        now = datetime.now()
        d = decide(
            now=now,
            slot_hour=int(self.cfg["controller"]["slot_hour"]),
            slot_minute=int(self.cfg["controller"]["slot_minute"]),
            ui_alive=self.ui_alive,
            dry_run=bool(self.cfg["controller"]["dry_run"]),
            print_in_progress=busy,
            last_user_print=last,
            strong_idle_days=int(self.cfg["controller"]["strong_idle_days"]),
            printexp_running=running,
        )
        return now, last, src, busy, running, d

    def _refresh_labels(self, now, last, src, busy, running, d) -> None:
        last_s = last.strftime("%Y-%m-%d %H:%M") if last else "inconnu"
        pe = "PrintExp en cours" if running else "PrintExp ABSENT"
        self.status.configure(
            text=f"{now:%H:%M:%S}  |  {pe}  |  dry-run  |  dernier print user : {last_s} ({src})"
        )
        self.detail.configure(text=f"Décision : {d.action.value} — {d.reason}")

    def _manual_decide(self) -> None:
        now, last, src, busy, running, d = self._snapshot()
        self._refresh_labels(now, last, src, busy, running, d)
        self._emit(d, running)

    def _emit(self, d, running: bool) -> None:
        if not running:
            self._log("refus : PrintExp_X64.exe non trouvé — aucun clic")
        self._log(f"{d.action.value} | {d.reason}")
        if running:
            for line in describe_printexp_controls():
                self._log(line)
        if d.action in (Action.WOULD_CLEAN_NORMAL, Action.WOULD_CLEAN_STRONG):
            self._log("would: click Clean -> menu 3 lignes -> wait toolbar -> Check (NOT executed)")

    def _tick(self) -> None:
        if not self.ui_alive:
            return
        now, last, src, busy, running, d = self._snapshot()
        self._refresh_labels(now, last, src, busy, running, d)
        key = now.strftime("%Y-%m-%d %H:%M")
        if is_slot(now, int(self.cfg["controller"]["slot_hour"]), int(self.cfg["controller"]["slot_minute"])):
            if self._fired_minute != key:
                self._fired_minute = key
                self._emit(d, running)
        self.root.after(5000, self._tick)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ControllerApp().run()


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    main()
