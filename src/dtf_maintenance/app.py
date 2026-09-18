"""UI PySide6 obligatoire : fermée = pas de maintenance."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

try:
    from PySide6.QtCore import QTime, Qt, QTimer
    from PySide6.QtGui import QFont, QIcon
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFileDialog,
        QFormLayout,
        QFrame,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QPlainTextEdit,
        QPushButton,
        QSpinBox,
        QTabWidget,
        QTimeEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError as exc:
    raise SystemExit(
        "PySide6 est requis. Sur le PC DTF : py -3 -m pip install -r requirements.txt"
    ) from exc

from dtf_maintenance.config import load_config, save_user_settings
from dtf_maintenance.detect import last_user_print, print_in_progress, printexp_running
from dtf_maintenance.logutil import Logger
from dtf_maintenance.policy import Action, Decision, decide, is_slot
from dtf_maintenance.ui_win32 import describe_printexp_controls

ROOT = Path(__file__).resolve().parents[2]
ICON_PATH = ROOT / "assets" / "dtf-nozzle-drop-icon.png"

STYLESHEET = """
QMainWindow, QWidget#root {
    background: #e7eef4;
    color: #4a5f73;
    font-family: "Segoe UI";
    font-size: 13px;
}
QLabel#title {
    font-size: 20px;
    font-weight: 600;
    color: #4a5f73;
}
QLabel#subtitle {
    color: #7a8fa3;
}
QFrame#card {
    background: #f5f8fb;
    border: 1px solid #c5d3e0;
    border-radius: 14px;
}
QLabel#kicker {
    color: #8aa0b4;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.6px;
}
QLabel#value {
    font-size: 15px;
    font-weight: 600;
    color: #4a5f73;
}
QLabel#decision {
    font-size: 14px;
    color: #4a5f73;
}
QLabel#badge {
    padding: 4px 10px;
    border-radius: 999px;
    font-weight: 600;
    font-size: 12px;
}
QPushButton#decide, QPushButton#save, QPushButton#browse {
    background: #9bb4c8;
    color: #2f4256;
    border: none;
    border-radius: 10px;
    padding: 10px 16px;
    font-weight: 600;
}
QPushButton#decide:hover, QPushButton#save:hover, QPushButton#browse:hover {
    background: #adc3d4;
}
QPushButton#decide:pressed, QPushButton#save:pressed, QPushButton#browse:pressed {
    background: #8aa6bb;
}
QPlainTextEdit#log, QLineEdit, QSpinBox, QTimeEdit, QComboBox {
    background: #eef3f7;
    color: #4a5f73;
    border: 1px solid #c5d3e0;
    border-radius: 10px;
    padding: 6px 8px;
}
QPlainTextEdit#log {
    font-family: "Cascadia Mono", "Consolas", monospace;
    font-size: 12px;
}
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: #d5e0ea;
    color: #4a5f73;
    padding: 8px 18px;
    border-radius: 10px;
    margin-right: 8px;
}
QTabBar::tab:selected {
    background: #f5f8fb;
    font-weight: 600;
}
QCheckBox { color: #7a8fa3; }
"""


class ControllerWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.cfg = load_config()
        self.logger = Logger(ROOT / "logs")
        self.ui_alive = True
        self._fired_minute: str | None = None

        self.setWindowTitle("DTF Maintenance Controller — dry-run")
        self.resize(920, 720)
        self.setStyleSheet(STYLESHEET)
        if ICON_PATH.is_file():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        titles = QVBoxLayout()
        title = QLabel("DTF Maintenance Controller")
        title.setObjectName("title")
        sub = QLabel("Sans cette fenêtre, aucune maintenance n'est lancée.")
        sub.setObjectName("subtitle")
        titles.addWidget(title)
        titles.addWidget(sub)
        header.addLayout(titles, 1)
        self.mode_badge = QLabel("DRY-RUN")
        self.mode_badge.setObjectName("badge")
        self.mode_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_badge(self.mode_badge, "#5a7390", "#d9e3ee")
        header.addWidget(self.mode_badge, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header)

        tabs = QTabWidget()
        tabs.addTab(self._build_control(), "Contrôle")
        tabs.addTab(self._build_settings(), "Paramètres")
        layout.addWidget(tabs, 1)

        self._log("controller UI started dry_run=true require_ui=true toolkit=PySide6")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(5000)
        self._tick()

    def _build_control(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        cards = QHBoxLayout()
        cards.setSpacing(10)
        self.print_exp_value = QLabel("…")
        self.last_print_value = QLabel("…")
        self.idle_value = QLabel("…")
        self.prn_value = QLabel("…")
        cards.addWidget(self._card("PRINTEXP", self.print_exp_value))
        cards.addWidget(self._card("DERNIER PRINT USER", self.last_print_value))
        cards.addWidget(self._card("BANDEAU", self.idle_value))
        cards.addWidget(self._card("PRN MAINTENANCE", self.prn_value))
        layout.addLayout(cards)

        decision_card = QFrame()
        decision_card.setObjectName("card")
        dlay = QVBoxLayout(decision_card)
        kicker = QLabel("DÉCISION")
        kicker.setObjectName("kicker")
        self.decision_label = QLabel("…")
        self.decision_label.setObjectName("decision")
        self.decision_label.setWordWrap(True)
        dlay.addWidget(kicker)
        dlay.addWidget(self.decision_label)
        layout.addWidget(decision_card)

        actions = QHBoxLayout()
        self.decide_btn = QPushButton("Décision maintenant (dry-run)")
        self.decide_btn.setObjectName("decide")
        self.decide_btn.clicked.connect(self._manual_decide)
        lock = QLabel("Clics PrintExp : désactivés")
        lock.setObjectName("subtitle")
        actions.addWidget(self.decide_btn)
        actions.addWidget(lock)
        actions.addStretch(1)
        layout.addLayout(actions)

        self.logbox = QPlainTextEdit()
        self.logbox.setObjectName("log")
        self.logbox.setReadOnly(True)
        layout.addWidget(self.logbox, 1)
        return page

    def _build_settings(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(12)

        card = QFrame()
        card.setObjectName("card")
        form = QFormLayout(card)
        form.setContentsMargins(18, 16, 18, 16)
        form.setSpacing(12)

        note = QLabel(
            "Le fichier .prn d'entretien n'est pas encore défini. "
            "Horaires et niveau de Clean sont réglables ici. Weak n'est jamais automatique."
        )
        note.setObjectName("subtitle")
        note.setWordWrap(True)
        form.addRow(note)

        self.slot_edit = QTimeEdit()
        self.slot_edit.setDisplayFormat("HH:mm")
        self.slot_edit.setTime(
            QTime(
                int(self.cfg["controller"]["slot_hour"]),
                int(self.cfg["controller"]["slot_minute"]),
            )
        )
        form.addRow("Heure quotidienne", self.slot_edit)

        self.idle_spin = QSpinBox()
        self.idle_spin.setRange(1, 14)
        self.idle_spin.setSuffix(" j sans print → Strong")
        self.idle_spin.setValue(int(self.cfg["controller"]["strong_idle_days"]))
        form.addRow("Séquence auto", self.idle_spin)

        self.level_combo = QComboBox()
        self.level_combo.addItem("Auto (Normal, ou Strong si inactivité)", "auto")
        self.level_combo.addItem("Forcer Normal", "normal")
        self.level_combo.addItem("Forcer Strong", "strong")
        current = str(self.cfg["controller"].get("clean_level", "auto"))
        idx = max(0, self.level_combo.findData(current))
        self.level_combo.setCurrentIndex(idx)
        form.addRow("Niveau de Clean", self.level_combo)

        prn_row = QHBoxLayout()
        self.prn_edit = QLineEdit(str(self.cfg["paths"].get("maintenance_prn") or ""))
        self.prn_edit.setPlaceholderText("à définir plus tard — aucun fichier choisi")
        browse = QPushButton("Parcourir…")
        browse.setObjectName("browse")
        browse.clicked.connect(self._browse_prn)
        prn_row.addWidget(self.prn_edit, 1)
        prn_row.addWidget(browse)
        form.addRow("Fichier .prn maintenance", prn_row)

        weak = QCheckBox("Weak (jamais en automatique)")
        weak.setChecked(False)
        weak.setEnabled(False)
        form.addRow("Niveaux exclus", weak)

        dry = QCheckBox("dry-run — aucun clic PrintExp")
        dry.setChecked(True)
        dry.setEnabled(False)
        form.addRow("Sûreté V0", dry)

        layout.addWidget(card)

        save = QPushButton("Enregistrer les paramètres")
        save.setObjectName("save")
        save.clicked.connect(self._save_settings)
        layout.addWidget(save, 0, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        return page

    def _browse_prn(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir le .prn d'entretien (plus tard)",
            str(self.prn_edit.text() or "C:/InkONE"),
            "Fichiers PRN (*.prn);;Tous (*.*)",
        )
        if path:
            self.prn_edit.setText(path)

    def _save_settings(self) -> None:
        t = self.slot_edit.time()
        level = str(self.level_combo.currentData() or "auto")
        prn = self.prn_edit.text().strip()
        save_user_settings(
            slot_hour=t.hour(),
            slot_minute=t.minute(),
            strong_idle_days=int(self.idle_spin.value()),
            clean_level=level,
            maintenance_prn=prn,
        )
        self.cfg = load_config()
        self._log(
            f"settings saved slot={t.hour():02d}:{t.minute():02d} "
            f"strong_idle={self.idle_spin.value()}d level={level} "
            f"prn={prn or '(non défini)'}"
        )
        self._tick()

    def _card(self, kicker: str, value: QLabel) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        box = QVBoxLayout(frame)
        box.setContentsMargins(14, 12, 14, 14)
        k = QLabel(kicker)
        k.setObjectName("kicker")
        value.setObjectName("value")
        value.setWordWrap(True)
        box.addWidget(k)
        box.addWidget(value)
        return frame

    def _set_badge(self, label: QLabel, fg: str, bg: str) -> None:
        label.setStyleSheet(
            f"QLabel#badge {{ color: {fg}; background: {bg}; padding: 4px 10px; "
            f"border-radius: 999px; font-weight: 600; font-size: 12px; }}"
        )

    def closeEvent(self, event) -> None:  # noqa: N802
        self.ui_alive = False
        self.timer.stop()
        self._log("UI fermée — maintenance inhibée")
        event.accept()

    def _log(self, msg: str) -> None:
        line = self.logger.line(msg)
        self.logbox.appendPlainText(line)

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
            clean_level=str(self.cfg["controller"].get("clean_level", "auto")),
        )
        return now, last, src, busy, running, d

    def _refresh_labels(self, now, last, src, busy, running, d: Decision) -> None:
        last_s = last.strftime("%Y-%m-%d %H:%M") if last else "inconnu"
        self.print_exp_value.setText("en cours" if running else "ABSENT — refus V0")
        self.last_print_value.setText(f"{last_s}\n{src}")
        self.idle_value.setText("print en cours" if busy else "pas de print en cours")
        prn = str(self.cfg["paths"].get("maintenance_prn") or "").strip()
        self.prn_value.setText(Path(prn).name if prn else "à définir plus tard")
        slot_h = int(self.cfg["controller"]["slot_hour"])
        slot_m = int(self.cfg["controller"]["slot_minute"])
        level = str(self.cfg["controller"].get("clean_level", "auto"))
        self.decision_label.setText(
            f"{now:%H:%M:%S}  ·  {d.action.value}  ·  créneau {slot_h:02d}:{slot_m:02d}  ·  {level}\n{d.reason}"
        )
        if d.action == Action.SKIP:
            self._set_badge(self.mode_badge, "#4a6f78", "#d4e4ea")
            self.mode_badge.setText("SKIP / DRY-RUN")
        elif d.action in (Action.WOULD_CLEAN_NORMAL, Action.WOULD_CLEAN_STRONG):
            self._set_badge(self.mode_badge, "#5a6e88", "#dde4ed")
            self.mode_badge.setText(d.action.value.upper())
        if not running:
            self._set_badge(self.mode_badge, "#6a7388", "#e2e6ec")
            self.mode_badge.setText("PRINTEXP ABSENT")

    def _manual_decide(self) -> None:
        now, last, src, busy, running, d = self._snapshot()
        self._refresh_labels(now, last, src, busy, running, d)
        self._emit(d, running)

    def _emit(self, d: Decision, running: bool) -> None:
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


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    if ICON_PATH.is_file():
        app.setWindowIcon(QIcon(str(ICON_PATH)))
    win = ControllerWindow()
    win.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "src"))
    main()
