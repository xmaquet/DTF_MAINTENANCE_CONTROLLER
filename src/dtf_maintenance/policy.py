"""Décision d'entretien — aucune commande machine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum


class Action(str, Enum):
    SKIP = "skip"
    WOULD_CLEAN_NORMAL = "would_clean_normal"
    WOULD_CLEAN_STRONG = "would_clean_strong"


@dataclass(frozen=True)
class Decision:
    action: Action
    reason: str
    at: datetime


def decide(
    *,
    now: datetime,
    slot_hour: int,
    slot_minute: int,
    ui_alive: bool,
    dry_run: bool,
    print_in_progress: bool,
    last_user_print: datetime | None,
    strong_idle_days: int,
    printexp_running: bool = True,
    clean_level: str = "auto",
) -> Decision:
    if not ui_alive:
        return Decision(Action.SKIP, "pas d'UI controller = pas de maintenance", now)
    if not printexp_running:
        return Decision(
            Action.SKIP,
            "PrintExp absent = pas de maintenance (V0, pas de repli carte)",
            now,
        )
    if print_in_progress:
        return Decision(Action.SKIP, "print en cours", now)
    if last_user_print is not None and last_user_print.date() == now.date():
        return Decision(
            Action.SKIP,
            f"print utilisateur aujourd'hui ({last_user_print.strftime('%H:%M')})",
            now,
        )
    idle_days = _idle_days(now.date(), last_user_print)
    level = (clean_level or "auto").lower()
    if level == "strong":
        action = Action.WOULD_CLEAN_STRONG
        reason = "niveau forcé STRONG puis Check"
    elif level == "normal":
        action = Action.WOULD_CLEAN_NORMAL
        reason = "niveau forcé NORMAL puis Check"
    elif idle_days >= strong_idle_days:
        action = Action.WOULD_CLEAN_STRONG
        reason = f"{idle_days} j sans print utilisateur → Clean STRONG puis Check"
    else:
        action = Action.WOULD_CLEAN_NORMAL
        reason = "pas de print aujourd'hui → Clean NORMAL puis Check"
    if dry_run:
        reason = "dry-run: " + reason + " (aucun clic)"
    return Decision(action, reason, now)


def is_slot(now: datetime, hour: int, minute: int) -> bool:
    return now.hour == hour and now.minute == minute


def _idle_days(today: date, last_user_print: datetime | None) -> int:
    if last_user_print is None:
        return 999
    return (today - last_user_print.date()).days
