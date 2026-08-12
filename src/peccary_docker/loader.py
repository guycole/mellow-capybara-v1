#
# Title: loader.py
# Description: load capybara files
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import datetime
import json
import os

from helper.json_helper import JsonHelper, schema

from helper.postgres import PostGres

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("loader")

class Loader:

    def __init__(self, postgres: PostGres):
        self.postgres = postgres

        self.failure_dir = os.environ.get("FAILURE_DIR", "/var/peccary/capybara/failure")
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/peccary/capybara/fresh")

        #temporary
        self.fresh_dir = os.environ.get("FRESH_DIR", "/var/wombat/fresh/capybara")
 
        self.failure = 0
        self.success = 0

        self.jh = JsonHelper()

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
                    "parent_file_name": self.jh.raw_json["parentFileName"],
                    "site_name": self.jh.raw_json["geoLoc"]["siteName"],
                    "task": self.jh.raw_json["job"]["task"],
                }

                self.postgres.load_log_insert(load_log)

                if "slow" in self.jh.raw_json["job"]["mode"]:
                    quantity_acars = len(self.jh.raw_json["observations"])
                    quantity_vdl2 = 0
                else:
                    quantity_acars = 0
                    quantity_vdl2 = len(self.jh.raw_json["observations"])

                daily_score = {
                    "crate_name": self.jh.raw_json["crateName"],
                    "file_quantity": 1,
                    "host_name": self.jh.raw_json["equipment"]["hostName"],
                    "obs_quantity": len(self.jh.raw_json["observations"]),
                    "quantity_acars": quantity_acars,
                    "quantity_vdl2": quantity_vdl2,
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

        if self.jh.raw_json["fileName"] != file_name:
            logger.warning(f"mismatched file name: {self.jh.raw_json['fileName']} vs {file_name}")
            self.file_failure(file_name)
            return

        if (self.jh.raw_json["version"] == 1 and self.jh.raw_json["job"]["project"] == "capybara-v1"):
            pass
        else:
            logger.warning(f"invalid version or project for {file_name}")
            self.file_failure(file_name)
            return

        if self.load_log_test(file_name):
            print(len(self.jh.raw_json["observations"]))

            for obs in self.jh.raw_json["observations"]:
                self.load_obs(obs)

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
