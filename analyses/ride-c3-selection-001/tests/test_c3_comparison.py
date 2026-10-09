import importlib.util
import unittest
from pathlib import Path

import numpy as np


SCRIPT = Path(__file__).resolve().parents[1] / "code" / "generate_c3_comparison.py"
SPEC = importlib.util.spec_from_file_location("c3_comparison", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestC3Comparison(unittest.TestCase):
    def test_confirmed_channel_order(self):
        self.assertEqual(len(MODULE.CHANNELS), 28)
        self.assertEqual(MODULE.CHANNELS.index("C3"), 10)
        self.assertEqual(len(set(MODULE.CHANNELS)), 28)

    def test_all_real_files_validate_without_decimation(self):
        paths = sorted((MODULE.ROOT / "data").glob("*_RIDE_result.mat"))
        self.assertEqual(len(paths), 4)
        for path in paths:
            record = MODULE.load_recording(path)
            self.assertEqual(record["shape"][:2], [1751, 28])
            for key in ("S", "C", "R"):
                self.assertEqual(record["c3_uv"][key].shape, (record["shape"][2], 1751))
                self.assertTrue(np.isfinite(record["c3_uv"][key]).all())


if __name__ == "__main__":
    unittest.main()
