import copy
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from collector import Collector, TimeStamp


REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_ROOT = REPO_ROOT / "samples"


def _make_args(raw_dir: str, fresh_dir: str) -> dict:
    return {
        "crateName": "wombat04",
        "freshDir": fresh_dir,
        "rawDir": raw_dir,
        "equipment": {
            "hostName": "c4g",
            "hostType": "odroid c4",
        },
        "geoLoc": {
            "altitude": 0.0,
            "latitude": 38.108,
            "longitude": -122.268,
            "siteName": "vallejo01",
        },
        "receiver": {
            "antenna": "multicoupler",
            "receiverId": 11,
            "task": "capybara-v1-sf1-slow",
            "type": "rtl-sdr-v3",
        },
    }


def _normalize_wrapper(payload: dict) -> dict:
    normalized = copy.deepcopy(payload)
    normalized.pop("fileName", None)
    normalized.pop("timeStamp", None)

    for observation in normalized.get("observations", []):
        if isinstance(observation, dict):
            observation.pop("uuid", None)

    return normalized


def _run_fixture_case(input_file: Path, expected_wrapper: Path) -> None:
    expected = json.loads(expected_wrapper.read_text(encoding="utf-8"))

    with tempfile.TemporaryDirectory() as tmp_dir:
        raw_dir = Path(tmp_dir) / "raw"
        fresh_dir = Path(tmp_dir) / "fresh"
        raw_dir.mkdir(parents=True)
        fresh_dir.mkdir(parents=True)

        staged_input = raw_dir / input_file.name
        staged_input.write_text(input_file.read_text(encoding="utf-8"), encoding="utf-8")

        collector = Collector(_make_args(str(raw_dir), str(fresh_dir)))
        collector.time_stamp = TimeStamp(
            epochSeconds=expected["timeStamp"]["epochSeconds"]
        )

        observations = collector.read_observations(str(staged_input))
        retflag = collector.write_json_wrapper(observations, input_file.name)
        assert retflag == 0

        produced_files = list(fresh_dir.glob("*.json"))
        assert len(produced_files) == 1

        actual = json.loads(produced_files[0].read_text(encoding="utf-8"))

        assert actual["sourceFileName"] == expected["sourceFileName"]
        assert len(actual["observations"]) == len(expected["observations"])
        assert _normalize_wrapper(actual) == _normalize_wrapper(expected)


def test_matches_acars_sample_output() -> None:
    _run_fixture_case(
        input_file=SAMPLES_ROOT / "acarsdec" / "acars_20260806_21.json",
        expected_wrapper=SAMPLES_ROOT
        / "dffcc4f1-9536-4ada-bbf0-87bbf9e9e18f.json",
    )


def test_matches_vdl2_sample_output() -> None:
    _run_fixture_case(
        input_file=SAMPLES_ROOT / "dumpvdl2" / "vdl2_20260807_23.json",
        expected_wrapper=SAMPLES_ROOT
        / "29faf669-0999-4d35-9279-dba32d3b12d4.json",
    )