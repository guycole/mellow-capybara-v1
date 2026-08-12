import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from utility.acarsdec_freq_test import summarize_acarsdec_frequencies


class AcarsdecFrequencySummaryTests(unittest.TestCase):
    def test_acarsdec_scripts_cover_full_025mhz_grid(self) -> None:
        summary = summarize_acarsdec_frequencies(Path(__file__).resolve().parents[1] / "bin")

        self.assertEqual(summary["count"], 77)
        self.assertEqual(summary["min"], 129.0)
        self.assertEqual(summary["max"], 130.9)
        self.assertEqual(summary["gaps"], [])


if __name__ == "__main__":
    unittest.main()
