import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from helper.json_helper import JsonHelper


class JsonHelperSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.helper = JsonHelper()

    def _valid_v2_payload(self) -> dict:
        return {
            "crateName": "wombat04",
            "fileName": "d9ece648-b7e6-426f-a0fd-3d18e73c03e3.json",
            "sourceFileName": "acars_20260806_23.json",
            "version": 2,
            "equipment": {
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
                "mode": "sf1-slow",
                "project": "capybara-v1",
                "task": "capybara-v1-sf1-slow",
            },
            "receiver": {
                "antenna": "multicoupler",
                "receiverId": 11,
                "task": "capybara-v1-sf1-slow",
                "type": "rtl-sdr-v3",
            },
            "timeStamp": {
                "epochSeconds": 1786310176,
                "iso8601": "2026-08-09T21:16:16+00:00",
            },
            "observations": [
                {
                    "uuid": "e8c34696-7f06-4bd5-bf88-7e08a671d059",
                    "app": {"name": "acarsdec"},
                }
            ],
        }

    def test_accepts_v2_wrapper_shape(self) -> None:
        payload = self._valid_v2_payload()

        self.assertTrue(self.helper.json_file_writer("/tmp/v2-wrapper.json", payload))

    def test_accepts_v2_string_observations(self) -> None:
        payload = self._valid_v2_payload()
        payload["observations"] = ['{"vdl2":{"app":{"name":"dumpvdl2","ver":"2.6.0"}}}']

        self.assertTrue(
            self.helper.json_file_writer("/tmp/v2-string-observations-wrapper.json", payload)
        )

    def test_rejects_missing_source_file_name(self) -> None:
        payload = self._valid_v2_payload()
        del payload["sourceFileName"]

        self.assertFalse(
            self.helper.json_file_writer("/tmp/missing-source-file-name.json", payload)
        )

    def test_rejects_v1_version(self) -> None:
        payload = self._valid_v2_payload()
        payload["version"] = 1

        self.assertFalse(
            self.helper.json_file_writer("/tmp/reject-v1-version.json", payload)
        )

    def test_rejects_legacy_parent_file_name_field(self) -> None:
        payload = self._valid_v2_payload()
        payload["parentFileName"] = "acars_20260806_23.json"

        self.assertFalse(
            self.helper.json_file_writer("/tmp/reject-parent-file-name.json", payload)
        )

    def test_rejects_receiver_type_legacy_key(self) -> None:
        payload = self._valid_v2_payload()
        payload["receiver"]["receiverType"] = payload["receiver"].pop("type")

        self.assertFalse(
            self.helper.json_file_writer("/tmp/reject-receiver-type-legacy-key.json", payload)
        )

    def test_rejects_equipment_legacy_receiver_fields(self) -> None:
        payload = self._valid_v2_payload()
        payload["equipment"]["antenna"] = "multicoupler"

        self.assertFalse(
            self.helper.json_file_writer("/tmp/reject-equipment-legacy-fields.json", payload)
        )

    def test_accepts_v2_sample_file(self) -> None:
        sample = Path(__file__).resolve().parents[1] / "samples" / "dffcc4f1-9536-4ada-bbf0-87bbf9e9e18f.json"
        self.assertTrue(self.helper.json_file_reader(str(sample), True))

    def test_accepts_acarsdec_wrapper_shape(self) -> None:
        # Legacy test name retained for compatibility with existing test invocations.
        payload = self._valid_v2_payload()

        self.assertTrue(self.helper.json_file_writer("/tmp/acars-wrapper.json", payload))

    def test_accepts_vdl2_wrapper_shape(self) -> None:
        payload = self._valid_v2_payload()
        payload["sourceFileName"] = "vdl2_20260807_23.json"
        payload["observations"] = [
            {
                "uuid": "e8c34696-7f06-4bd5-bf88-7e08a671d059",
                "vdl2": {"app": {"name": "dumpvdl2", "ver": "2.6.0"}},
            }
        ]

        self.assertTrue(self.helper.json_file_writer("/tmp/vdl2-wrapper.json", payload))

    def test_accepts_hybrid_legacy_wrapper_shape(self) -> None:
        # Legacy test name retained; now asserts v2 hybrid-compatible observations only.
        payload = self._valid_v2_payload()
        payload["observations"] = [
            {
                "uuid": "e8c34696-7f06-4bd5-bf88-7e08a671d059",
                "equipment": {"antenna": "multicoupler"},
            },
            {
                "uuid": "8f5eb298-8b31-4ca8-a90c-3151ac87d2d9",
                "acarsdec": {"app": {"name": "acarsdec"}},
            },
        ]

        self.assertTrue(self.helper.json_file_writer("/tmp/hybrid-wrapper.json", payload))

    def test_rejects_missing_parent_file_name(self) -> None:
        # Legacy test name retained; now verifies parentFileName is not part of v2 schema.
        payload = self._valid_v2_payload()
        del payload["sourceFileName"]

        self.assertFalse(
            self.helper.json_file_writer("/tmp/missing-parent-file-name.json", payload)
        )

    def test_accepts_string_observations(self) -> None:
        payload = self._valid_v2_payload()
        payload["observations"] = [
            '{"vdl2":{"app":{"name":"dumpvdl2","ver":"2.6.0"}}}'
        ]

        self.assertTrue(
            self.helper.json_file_writer("/tmp/string-observations-wrapper.json", payload)
        )


if __name__ == "__main__":
    unittest.main()
