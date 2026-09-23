#
# Title: validator.py
# Description: ensure valid capybara files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from helper.json_helper import JsonHelper
from helper.postgres import PostGres

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("capybara")


class Validator(ABC):

    @abstractmethod
    def file_processor(self, file_name: str) -> bool:
        pass

    @abstractmethod
    def execute(self) -> int:
        pass

    @abstractmethod
    def file_failure(self, file_name: str) -> None:
        pass

    @abstractmethod
    def file_success(self, file_name: str) -> None:
        pass

    @abstractmethod
    def load_log_test(self, test_file_name: str) -> bool:
        pass


class CapybaraValidator(Validator):

    def __init__(self, logger: logging.Logger, postgres: PostGres):
        self.logger = logger
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/wombat/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/wombat/fresh/capybara")
        self.success_dir = os.environ.get("SUCCESS_DIR", "/var/wombat/capybara/success")

        self.failure = 0
        self.success = 0

        self.json_helper = JsonHelper()

    def validate_v2_payload(self, payload: dict[str, Any], file_name: str) -> bool:
        if not isinstance(payload, dict):
            self.logger.warning(f"payload is not dict for {file_name}")
            return False

        required_top = [
            "crateName",
            "fileName",
            "sourceFileName",
            "version",
            "equipment",
            "geoLoc",
            "job",
            "receiver",
            "timeStamp",
            "observations",
        ]
        for key in required_top:
            if key not in payload:
                self.logger.warning(f"missing required key '{key}' for {file_name}")
                return False

        if payload["version"] != 2:
            self.logger.warning(
                f"invalid version for {file_name}: {payload['version']}"
            )
            return False

        if payload["fileName"] != file_name:
            self.logger.warning(
                f"mismatched file name: {payload['fileName']} vs {file_name}"
            )
            return False

        equipment = payload["equipment"]
        if (
            not isinstance(equipment, dict)
            or "hostName" not in equipment
            or "hostType" not in equipment
        ):
            self.logger.warning(f"invalid equipment payload for {file_name}")
            return False

        geo_loc = payload["geoLoc"]
        if not isinstance(geo_loc, dict):
            self.logger.warning(f"invalid geoLoc payload for {file_name}")
            return False
        for key in ["altitude", "latitude", "longitude", "siteName"]:
            if key not in geo_loc:
                self.logger.warning(f"missing geoLoc.{key} for {file_name}")
                return False

        job = payload["job"]
        if not isinstance(job, dict):
            self.logger.warning(f"invalid job payload for {file_name}")
            return False
        for key in ["mode", "project", "task"]:
            if key not in job:
                self.logger.warning(f"missing job.{key} for {file_name}")
                return False

        receiver = payload["receiver"]
        if not isinstance(receiver, dict):
            self.logger.warning(f"invalid receiver payload for {file_name}")
            return False
        for key in ["antenna", "receiverId", "task", "type"]:
            if key not in receiver:
                self.logger.warning(f"missing receiver.{key} for {file_name}")
                return False

        time_stamp = payload["timeStamp"]
        if not isinstance(time_stamp, dict):
            self.logger.warning(f"invalid timeStamp payload for {file_name}")
            return False
        for key in ["epochSeconds", "iso8601"]:
            if key not in time_stamp:
                self.logger.warning(f"missing timeStamp.{key} for {file_name}")
                return False

        if not isinstance(payload["observations"], list):
            self.logger.warning(f"observations is not list for {file_name}")
            return False

        if job["project"] != "capybara-v1":
            self.logger.warning(f"invalid project for {file_name}: {job['project']}")
            return False

        return True

    def file_failure(self, file_name: str) -> None:
        self.logger.info(f"file failure:{file_name}")

        self.failure += 1
        failure_target = os.path.join(self.failure_dir, file_name)
        try:
            os.rename(file_name, failure_target)
        except Exception as error:
            self.logger.error(
                f"file move failure for {file_name} -> {failure_target}: {error}"
            )

    def file_success(self, file_name: str) -> None:
        self.logger.info(f"file success:{file_name}")

        self.success += 1
        success_target = os.path.join(self.success_dir, file_name)
        try:
            os.rename(file_name, success_target)
        except Exception as error:
            self.logger.error(
                f"file move failure for {file_name} -> {success_target}: {error}"
            )

    def load_frequency(self, obs: dict[str, Any]) -> None:
        if type(obs) is not dict:
            self.logger.error(f"invalid observation type: {type(obs)}")
            return

        frequency = None

        # Observations can carry frequency as VDL2 Hz or ACARS MHz.
        if "vdl2" in obs and type(obs["vdl2"]) is dict and "freq" in obs["vdl2"]:
            frequency = int(obs["vdl2"]["freq"])
        elif "freq" in obs:
            raw_freq = obs["freq"]
            frequency = int(raw_freq * 1000000) if raw_freq < 1000000 else int(raw_freq)
        elif "frequency" in obs:
            raw_freq = obs["frequency"]
            frequency = int(raw_freq * 1000000) if raw_freq < 1000000 else int(raw_freq)

        if frequency is None:
            self.logger.warning("skipping observation with no frequency field")
            return

        frequency_obs = {
            "crate_name": self.json_helper.raw_json["crateName"],
            "frequency": frequency,
            "host_name": self.json_helper.raw_json["equipment"]["hostName"],
            "message_quantity": 1,
            "mode": self.json_helper.raw_json["job"]["mode"],
            "score_date": datetime.date.fromisoformat(
                self.json_helper.raw_json["timeStamp"]["iso8601"][:10]
            ),
        }

        self.postgres.frequency_insert_or_update(frequency_obs)

    def load_log_test(self, test_file_name: str) -> bool:
        try:
            raw_buffer = self.json_helper.raw_json

            self.logger.info(f"checking load log:{test_file_name}")

            candidate = self.postgres.load_log_select_by_file_name(test_file_name)
            if candidate is None:
                self.logger.info(f"processing new file:{test_file_name}")

                geo_loc = self.postgres.geo_loc_select_by_site(
                    raw_buffer["geoLoc"]["siteName"]
                )
                if len(geo_loc) == 0:
                    site_name = raw_buffer["geoLoc"]["siteName"]
                    self.logger.error(f"must insert geo_loc for site: {site_name}")
                    return False

                load_log = {
                    "crate_name": raw_buffer["crateName"],
                    "epoch_seconds": raw_buffer["timeStamp"]["epochSeconds"],
                    "file_name": test_file_name,
                    "geo_loc_id": geo_loc[0].id,
                    "host_name": raw_buffer["equipment"]["hostName"],
                    "load_time": datetime.datetime.now(),
                    "mode": raw_buffer["job"]["mode"],
                    "obs_quantity": len(raw_buffer["observations"]),
                    "obs_time": raw_buffer["timeStamp"]["iso8601"],
                    "parent_file_name": raw_buffer["sourceFileName"],
                    "site_name": raw_buffer["geoLoc"]["siteName"],
                    "task": raw_buffer["job"]["task"],
                }

                self.postgres.load_log_insert(load_log)
                self.logger.info(f"load log insert complete:{test_file_name}")

                if "slow" in raw_buffer["job"]["mode"]:
                    quantity_slow = len(raw_buffer["observations"])
                    quantity_fast = 0
                else:
                    quantity_slow = 0
                    quantity_fast = len(raw_buffer["observations"])

                daily_score = {
                    "crate_name": raw_buffer["crateName"],
                    "file_quantity": 1,
                    "host_name": raw_buffer["equipment"]["hostName"],
                    "obs_quantity": len(raw_buffer["observations"]),
                    "quantity_slow": quantity_slow,
                    "quantity_fast": quantity_fast,
                    "score_date": datetime.date.fromisoformat(
                        raw_buffer["timeStamp"]["iso8601"][:10]
                    ),
                }

                self.postgres.daily_score_insert_or_update(daily_score)

                for obs in raw_buffer["observations"]:
                    self.load_frequency(obs)

                if len(raw_buffer["observations"]) < 1:
                    self.logger.info("skipping file with no observations")
                    return False

                return True
            else:
                self.logger.info(f"skippping already processed:{test_file_name}")
                return False
        except Exception as error:
            self.logger.error(f"postgres insert failed for {test_file_name}: {error}")

        return False

    def file_processor(self, file_name: str) -> bool:
        self.logger.info(f"processing file:{file_name}")

        if os.path.isfile(file_name) is False:
            self.logger.warning(f"skipping non-file:{file_name}")
            self.file_failure(file_name)
            return False

        if not self.json_helper.json_file_reader(file_name, False):
            self.logger.warning(f"file read failed for {file_name}")
            self.file_failure(file_name)
            return False

        if os.path.getsize(file_name) < 1:
            self.logger.warning(f"skipping empty file:{file_name}")
            self.file_failure(file_name)
            return False

        if not self.validate_v2_payload(self.json_helper.raw_json, file_name):
            self.file_failure(file_name)
            return False

        if self.load_log_test(file_name):
            self.file_success(file_name)
            return True
        else:
            self.file_failure(file_name)
            return False

    def execute(self) -> int:
        self.logger.info(f"validator fresh dir:{self.fresh_dir}")

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        self.logger.info(f"{len(targets)} files noted")

        for target in targets:
            if target.startswith("acars") or target.startswith("vdl2"):
                self.logger.info(f"skipping raw:{target}")
                self.file_success(target)
                continue

            self.file_processor(target)

        self.logger.info(f"validator success:{self.success} failure:{self.failure}")

        return 0


# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
