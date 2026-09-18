import copy
import json
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

fake_postgres = types.ModuleType("helper.postgres")


class PostGres:  # pragma: no cover - test-only import shim
    pass


fake_postgres.PostGres = PostGres
sys.modules["helper.postgres"] = fake_postgres

from wombat_docker.validator import Validator


class DummyPostGres:
    pass


def _load_sample_v2_payload() -> dict:
    sample_path = (
        Path(__file__).resolve().parents[2]
        / "samples"
        / "dffcc4f1-9536-4ada-bbf0-87bbf9e9e18f.json"
    )
    return json.loads(sample_path.read_text(encoding="utf-8"))


def test_validate_v2_payload_accepts_sample() -> None:
    validator = Validator(DummyPostGres())
    payload = _load_sample_v2_payload()

    assert validator.validate_v2_payload(payload, payload["fileName"])


def test_validate_v2_payload_rejects_v1_shape() -> None:
    validator = Validator(DummyPostGres())
    payload = _load_sample_v2_payload()

    legacy_payload = copy.deepcopy(payload)
    legacy_payload["version"] = 1
    legacy_payload["parentFileName"] = legacy_payload.pop("sourceFileName")

    assert not validator.validate_v2_payload(legacy_payload, legacy_payload["fileName"])
