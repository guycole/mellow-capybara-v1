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
            "observations": [
                {
                    "uuid": "e8c34696-7f06-4bd5-bf88-7e08a671d059",
                    "acarsdec": {"app": {"name": "acarsdec"}},
                }
            ],
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
            "observations": [
                {
                    "uuid": "e8c34696-7f06-4bd5-bf88-7e08a671d059",
                    "vdl2": {"app": {"name": "dumpvdl2", "ver": "2.6.0"}},
                }
            ],
        }

        self.assertTrue(self.helper.json_file_writer("/tmp/vdl2-wrapper.json", payload))

    def test_accepts_hybrid_legacy_wrapper_shape(self) -> None:
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
            "job": {
                "mode": "acarsdec-sf1",
                "project": "capybara-v1",
                "task": "heeler-v2-iwlist",
            },
            "timeStamp": {
                "epochSeconds": 1786324005,
                "iso8601": "2026-08-10T01:06:45+00:00",
            },
            "crateName": "wombat04",
            "fileName": "e513bb78-2691-4a76-8fa2-dd4e2e15b7c4.json",
            "parentFileName": "acars-wrapper.json",
            "version": 1,
            "observations": [
                {
                    "uuid": "e8c34696-7f06-4bd5-bf88-7e08a671d059",
                    "equipment": {"antenna": "multicoupler"},
                },
                {
                    "uuid": "8f5eb298-8b31-4ca8-a90c-3151ac87d2d9",
                    "acarsdec": {"app": {"name": "acarsdec"}},
                },
            ],
        }

        self.assertTrue(self.helper.json_file_writer("/tmp/hybrid-wrapper.json", payload))


if __name__ == "__main__":
    unittest.main()
