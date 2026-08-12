import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utility.vdl2_freq_test import summarize_vdl2_frequencies


class Vdl2FrequencySummaryTests(unittest.TestCase):
    def test_vdl2_scripts_cover_full_025mhz_grid(self) -> None:
        summary = summarize_vdl2_frequencies(Path(__file__).resolve().parents[1] / "bin")

        self.assertEqual(summary["count"], 37)
        self.assertEqual(summary["min"], 136.1)
        self.assertEqual(summary["max"], 137.0)
        self.assertEqual(summary["gaps"], [])


if __name__ == "__main__":
    unittest.main()
