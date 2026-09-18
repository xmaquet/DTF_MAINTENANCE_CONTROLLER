import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dtf_maintenance.ui_win32 import is_minimized_rect


class Win32Helpers(unittest.TestCase):
    def test_minimized_sentinel(self):
        self.assertTrue(is_minimized_rect(-32000, -32000))
        self.assertFalse(is_minimized_rect(100, 80))


if __name__ == "__main__":
    unittest.main()
