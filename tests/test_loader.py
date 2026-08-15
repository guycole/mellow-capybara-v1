import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from peccary_docker.loader import Loader


class LoaderObservationTests(unittest.TestCase):
    def test_load_obs_parses_string_payload(self) -> None:
        loader = Loader(postgres=None)
        obs = '{"timestamp":1785981703.2674019,"station_id":"c4g","channel":0,"freq":130.025,"level":-28.7,"noise":-39.1,"error":1,"mode":"2","label":"H1","block_id":"9","ack":false,"tail":"N8514F","flight":"WN2045","msgno":"D47A","text":"#DFB76401\\r\\n02E06KOAKKPDX\\r\\nN37736W12227202000181P017226008G00002300ZGA-P\\r\\n","app":{"name":"acarsdec","ver":"v4.6-1-g0b7ba27"}}'

        # Should not raise and should normalize to a dict for downstream processing.
        normalized = loader._normalize_observation(obs)
        self.assertIsInstance(normalized, dict)
        self.assertEqual(normalized["app"]["name"], "acarsdec")



if __name__ == "__main__":
    unittest.main()
