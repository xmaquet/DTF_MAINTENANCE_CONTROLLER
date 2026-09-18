import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dtf_maintenance.policy import Action, decide


class PolicyTests(unittest.TestCase):
    def _base(self, **kw):
        now = datetime(2026, 9, 18, 20, 0, 0)
        args = dict(
            now=now,
            slot_hour=20,
            slot_minute=0,
            ui_alive=True,
            dry_run=True,
            print_in_progress=False,
            last_user_print=None,
            strong_idle_days=3,
            printexp_running=True,
        )
        args.update(kw)
        return decide(**args)

    def test_no_printexp(self):
        d = self._base(printexp_running=False)
        self.assertEqual(d.action, Action.SKIP)
        self.assertIn("PrintExp absent", d.reason)
        self.assertIn("pas de repli carte", d.reason)

    def test_no_ui(self):
        d = self._base(ui_alive=False)
        self.assertEqual(d.action, Action.SKIP)
        self.assertIn("UI", d.reason)


    def test_print_today(self):
        d = self._base(last_user_print=datetime(2026, 9, 18, 15, 28))
        self.assertEqual(d.action, Action.SKIP)
        self.assertIn("aujourd'hui", d.reason)

    def test_print_in_progress(self):
        d = self._base(print_in_progress=True)
        self.assertEqual(d.action, Action.SKIP)

    def test_normal(self):
        d = self._base(last_user_print=datetime(2026, 9, 17, 21, 13))
        self.assertEqual(d.action, Action.WOULD_CLEAN_NORMAL)

    def test_strong(self):
        d = self._base(last_user_print=datetime(2026, 9, 15, 10, 0))
        self.assertEqual(d.action, Action.WOULD_CLEAN_STRONG)

    def test_strong_idle_boundary(self):
        d = self._base(last_user_print=datetime(2026, 9, 15, 20, 0))
        self.assertEqual((datetime(2026, 9, 18).date() - datetime(2026, 9, 15).date()).days, 3)
        self.assertEqual(d.action, Action.WOULD_CLEAN_STRONG)


if __name__ == "__main__":
    unittest.main()
