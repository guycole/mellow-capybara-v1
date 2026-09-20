#
# Title: loader.py
# Description: load capybara files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import datetime
import os

from helper.json_helper import JsonHelper

from helper.postgres import PostGres

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("loader")

class Loader:

    def __init__(self, postgres: PostGres):
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/peccary/capybara/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/peccary/capybara/fresh")
 
        self.failure = 0
        self.success = 0

        self.jh = JsonHelper()

    def validate_v2_payload(self, payload: dict[str, any], file_name: str) -> bool:
        if not isinstance(payload, dict):
            logger.warning(f"payload is not dict for {file_name}")
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
                logger.warning(f"missing required key '{key}' for {file_name}")
                return False

        if payload["version"] != 2:
            logger.warning(f"invalid version for {file_name}: {payload['version']}")
            return False

        if payload["fileName"] != file_name:
            logger.warning(f"mismatched file name: {payload['fileName']} vs {file_name}")
            return False

        job = payload["job"]
        if not isinstance(job, dict):
            logger.warning(f"invalid job payload for {file_name}")
            return False
        for key in ["mode", "project", "task"]:
            if key not in job:
                logger.warning(f"missing job.{key} for {file_name}")
                return False

        if job["project"] != "capybara-v1":
            logger.warning(f"invalid project for {file_name}: {job['project']}")
            return False

        if not isinstance(payload["observations"], list):
            logger.warning(f"observations is not list for {file_name}")
            return False

        return True

    def file_failure(self, file_name: str):
        logger.info(f"file failure:{file_name}")

        self.failure += 1
#        os.rename(file_name, self.failure_dir + file_name)

    def file_success(self, file_name: str):
        #logger.info(f"file success:{file_name}")

        self.success += 1
#        os.rename(file_name, self.success_dir + "/" + file_name)

    def load_log_test(self, file_name: str) -> bool:
        try:
            candidate = self.postgres.load_log_select_by_file_name(file_name)
            if candidate is None:
                logger.info(f"processing new file:{file_name}")

                geo_loc = self.postgres.geo_loc_select_by_site(self.jh.raw_json["geoLoc"]["siteName"])
                if len(geo_loc) == 0:
                    logger.error(f"must insert geo_loc for site: {self.jh.raw_json['geoLoc']['siteName']}")
                    return False
           
                load_log = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "epoch_seconds": self.jh.raw_json["timeStamp"]["epochSeconds"],
                    "file_name": file_name,
                    "geo_loc_id": geo_loc[0].id,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "load_time": datetime.datetime.now(),
                    "mode": self.jh.raw_json["job"]["mode"],
                    "obs_quantity": len(self.jh.raw_json["observations"]),
                    "obs_time": self.jh.raw_json["timeStamp"]["iso8601"],
                    "parent_file_name": self.jh.raw_json["sourceFileName"],
                    "site_name": self.jh.raw_json["geoLoc"]["siteName"],
                    "task": self.jh.raw_json["job"]["task"],
                }

                self.postgres.load_log_insert(load_log)

                if "slow" in self.jh.raw_json["job"]["mode"]:
                    quantity_slow = len(self.jh.raw_json["observations"])
                    quantity_fast = 0
                else:
                    quantity_slow = 0
                    quantity_fast = len(self.jh.raw_json["observations"])

                daily_score = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "file_quantity": 1,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "obs_quantity": len(self.jh.raw_json["observations"]),
                    "quantity_slow": quantity_slow,
                    "quantity_fast": quantity_fast,
                    "score_date": datetime.date.fromisoformat(self.jh.raw_json["timeStamp"]["iso8601"][:10]),
                }

                self.postgres.daily_score_insert_or_update(daily_score)
                return True
            else:
                logger.info(f"skippping already processed:{file_name}")
                return False
        except Exception as error:
            logger.error(f"postgres insert failed for {file_name}: {error}")
        
        return False


    def load_frequency(self, obs: dict[str, any]) -> None:
        if type(obs) is not dict:
            logger.error(f"invalid observation type: {type(obs)}")
            return

        acars_type = "unknown"
        frequency = None

        if "vdl2" in obs and type(obs["vdl2"]) is dict and "freq" in obs["vdl2"]:
            acars_type = "fast"
            frequency = int(obs["vdl2"]["freq"])
        elif "freq" in obs:
            acars_type = "slow"
            raw_freq = obs["freq"]
            frequency = int(raw_freq * 1000000) if raw_freq < 1000000 else int(raw_freq)

        if frequency is None:
            logger.warning("skipping observation with no frequency field")
            return

        frequency_obs = {
            "acars_type": acars_type,
            "crate_name": self.jh.raw_json["crateName"],
            "frequency": frequency,
            "host_name": self.jh.raw_json["equipment"]["hostName"],
            "message_quantity": 1,
            "score_date": datetime.date.fromisoformat(self.jh.raw_json["timeStamp"]["iso8601"][:10]),
        }

        self.postgres.frequency_insert_or_update(frequency_obs)

    def load_obs(self, obs: dict[str, any]) -> None:
        if type(obs) is not dict:
            logger.error(f"invalid observation type: {type(obs)}")
            return

        if "vdl2" in obs:
            print(f"vdl2 obs")
            app = obs["vdl2"]["app"]
            t = obs["vdl2"]["t"]
            freq = obs["vdl2"]["freq"]
            avlc = obs["vdl2"]["avlc"]
            print(f"{avlc['src']} {avlc['dst']}")

#            app_name = obs["vdl2"]["name"]
#            time_stamp = obs["vdl2"]["t"]["sec"]
#            hex = obs["vdl2"]["avlc"]["src"]["addr"]
        else:
            print(f"acars obs")
            app_name = obs["app"]["name"]
            flight = obs["flight"]
            frequency = obs["freq"]
            tail = obs["tail"]
            time_stamp = obs["timestamp"]

    def file_processor(self, file_name: str) -> None:
        logger.info(f"processing files: {file_name}")

        if os.path.isfile(file_name) is False:
            logger.warning(f"skipping non-file:{file_name}")
            self.file_failure(file_name)
            return

        if os.path.getsize(file_name) < 1:
            logger.warning(f"skipping empty file:{file_name}")
            self.file_failure(file_name)
            return

        if not self.jh.json_file_reader(file_name, True):
            logger.warning(f"file read failed for {file_name}")
            self.file_failure(file_name)
            return

        if not self.validate_v2_payload(self.jh.raw_json, file_name):
            self.file_failure(file_name)
            return

        if self.load_log_test(file_name):
            print(len(self.jh.raw_json["observations"]))

            for obs in self.jh.raw_json["observations"]:
                self.load_frequency(obs)

#                self.load_obs(obs)

#            self.file_success(file_name)
        else:
            self.file_failure(file_name)

    def execute(self) -> None:
        logger.info(f"loader fresh dir:{self.fresh_dir}")

        os.chdir(self.fresh_dir)
        targets = sorted(os.listdir("."))
        logger.info(f"{len(targets)} files noted")

        for target in targets:
            self.file_processor(target)

        logger.info(f"loader success:{self.success} failure:{self.failure}")

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
