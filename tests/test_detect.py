import tempfile
import unittest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dtf_maintenance.detect import last_user_print, print_in_progress
from dtf_maintenance.policy import Action, decide


def _cfg(tmp: Path) -> dict:
    (tmp / "prnlist").mkdir()
    (tmp / "jobs").mkdir()
    (tmp / "log").mkdir()
    return {
        "paths": {
            "inkone_prnlist": str(tmp / "prnlist"),
            "inkone_jobs": str(tmp / "jobs"),
            "printexp_log_dir": str(tmp / "log"),
        }
    }


def _log_name() -> str:
    return f"Log[{datetime.now():%Y_%m_%d}].txt"


class DetectTests(unittest.TestCase):
    def test_utf16_erasmart_is_print_today(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            cfg = _cfg(tmp)
            line = (
                "[15:28:04.602][软件][调试][000000] "
                "作业ERASMART Quality Evaluation.prn\n"
            )
            (tmp / "log" / _log_name()).write_bytes(b"\xff\xfe" + line.encode("utf-16-le"))
            last, src = last_user_print(cfg)
            self.assertIsNotNone(last)
            self.assertEqual(last.hour, 15)
            self.assertEqual(last.minute, 28)
            self.assertIn("ERASMART Quality Evaluation.prn", src)
            self.assertNotIn("作业", src)
            dsn = decide(
                now=datetime.now().replace(hour=20, minute=0, second=0, microsecond=0),
                slot_hour=20,
                slot_minute=0,
                ui_alive=True,
                dry_run=True,
                print_in_progress=False,
                last_user_print=last,
                strong_idle_days=3,
            )
            self.assertEqual(dsn.action, Action.SKIP)

    def test_utf8_still_works(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            cfg = _cfg(tmp)
            (tmp / "log" / _log_name()).write_text(
                "[10:11:12.000] job foo-bar.prn\n", encoding="utf-8"
            )
            last, src = last_user_print(cfg)
            self.assertEqual(last.hour, 10)
            self.assertIn("foo-bar.prn", src)

    def test_section_prn_ignored(self):
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            cfg = _cfg(tmp)
            (tmp / "log" / _log_name()).write_text(
                "[10:11:12.000] ~section0.prn\n", encoding="utf-8"
            )
            last, src = last_user_print(cfg)
            self.assertIsNone(last)
            self.assertEqual(src, "aucune trace")

    def test_latin1_misread_does_not_hide_utf16(self):
        """Régression : lire UTF-16 en latin-1 ne voyait aucun .prn."""
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            cfg = _cfg(tmp)
            body = "[15:28:04.602] ERASMART Quality Evaluation.prn\n"
            (tmp / "log" / _log_name()).write_bytes(b"\xff\xfe" + body.encode("utf-16-le"))
            last, src = last_user_print(cfg)
            self.assertIsNotNone(last)
            self.assertFalse(print_in_progress(cfg))


if __name__ == "__main__":
    unittest.main()
