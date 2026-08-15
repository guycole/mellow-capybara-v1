import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from collector.bootboy import BootBoy


class BootBoyTests(unittest.TestCase):
    def test_verify_service_active_reports_status_and_journal_on_failure(self) -> None:
        bootboy = BootBoy()
        command_results = [
            (3, "", ""),
            (0, "status output", ""),
            (0, "journal output", ""),
        ]

        with patch.object(bootboy, "run_command", side_effect=command_results), patch("collector.bootboy.time.sleep"):
            with patch("builtins.print") as print_mock:
                bootboy.verify_service_active("vdl2-dev01.service")

        printed = [call.args[0] for call in print_mock.call_args_list]
        self.assertIn("vdl2-dev01.service failed to reach active state.", printed)
        self.assertIn("--- systemctl status: vdl2-dev01.service ---", printed)
        self.assertIn("status output", printed)
        self.assertIn("--- recent journal: vdl2-dev01.service ---", printed)
        self.assertIn("journal output", printed)


if __name__ == "__main__":
    unittest.main()