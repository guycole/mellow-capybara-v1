import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from helper.json_helper import JsonHelper


class JsonHelperSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.helper = JsonHelper()

    def test_accepts_acarsdec_wrapper_shape(self) -> None:
        payload = {
            "equipment": {
                "antenna": "multicoupler",
                "receiverId": 11,
                "receiverType": "rtl-sdr-v3",
                "hostName": "c4g",
                "hostType": "odroid c4",
            },
            "geoLoc": {
                "altitude": 0,
                "latitude": 38.108,
                "longitude": -122.268,
                "siteName": "vallejo01",
            },
            "timeStamp": {
                "epochSeconds": 1786310176,
                "iso8601": "2026-08-09T21:16:16+00:00",
            },
            "crate": "wombat04",
            "fileName": "d9ece648-b7e6-426f-a0fd-3d18e73c03e3.json",
            "mode": "acarsdec-sf1",
            "parentFileName": "acars_20260806_23.json",
            "project": "capybara-v1",
            "version": 1,
            "observations": [{"acarsdec": {"app": {"name": "acarsdec"}}}],
        }

        self.assertTrue(self.helper.json_file_writer("/tmp/acars-wrapper.json", payload))

    def test_accepts_vdl2_wrapper_shape(self) -> None:
        payload = {
            "equipment": {
                "antenna": "multicoupler",
                "receiverId": 11,
                "receiverType": "rtl-sdr-v3",
                "hostName": "c4g",
                "hostType": "odroid c4",
            },
            "geoLoc": {
                "altitude": 0,
                "latitude": 38.108,
                "longitude": -122.268,
                "siteName": "vallejo01",
            },
            "timeStamp": {
                "epochSeconds": 1786310176,
                "iso8601": "2026-08-09T21:16:16+00:00",
            },
            "crate": "wombat04",
            "fileName": "d9ece648-b7e6-426f-a0fd-3d18e73c03e3.json",
            "mode": "vdl2-sf-dev01",
            "parentFileName": "vdl2_20260807_23.json",
            "project": "capybara-v1",
            "version": 1,
            "observations": [{"vdl2": {"app": {"name": "dumpvdl2", "ver": "2.6.0"}}}],
        }

        self.assertTrue(self.helper.json_file_writer("/tmp/vdl2-wrapper.json", payload))


if __name__ == "__main__":
    unittest.main()
