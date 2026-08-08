#
# Title: collector.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#

import datetime
import json
import logging
import os
import sys
import time
import uuid
import zoneinfo

from helper.json_helper import JsonHelper

import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("capybara")


class Collector:

    def __init__(self, args: dict[str, any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]

        self.host_name = args["equipment"]["hostName"]
        self.host_type = args["equipment"]["hostType"]

        self.altitude = args["geoLoc"]["altitude"]
        self.latitude = args["geoLoc"]["latitude"]
        self.longitude = args["geoLoc"]["longitude"]
        self.site_name = args["geoLoc"]["siteName"]

        self.antenna = args["receiver"]["antenna"]
        self.receiver_id = args["receiver"]["receiverId"]
        self.receiver_mode = args["receiver"]["mode"]
        self.receiver_task = args["receiver"]["task"]
        self.receiver_type = args["receiver"]["type"]

        self.raw_dir = args["rawDir"]

        self.frequencies = args["receiver"]["frequencies"]

        self.jh = JsonHelper()

    def acars_file_discovery(self):
        gmt_now = datetime.datetime.now(datetime.timezone.utc)

        year = gmt_now.year
        month = gmt_now.month
        day = gmt_now.day
        hour = gmt_now.hour

        # dumpvdl2 output filenames have the form  vdl12_YYYYMMDD_HH.json
        dumpvdl2_current = f"vdl2_{year}{month:02d}{day:02d}_{hour:02d}.json"

        # acarsdec output filenames have the form  acars_YYYYMMDD_HH.json
        acars_current = f"acars_{year}{month:02d}{day:02d}_{hour:02d}.json"

        results = []
        
        os.chdir(self.raw_dir)
        targets = sorted(os.listdir("."))
        logger.info(f"{len(targets)} files noted")

        for target in targets:
            if target.startswith("acars"):
                if target == acars_current:
                    print(f"skipping {target}")
                else:
                    results.append(f"{self.raw_dir}/{target}")

            if target.startswith("vdl2"):
                if target == dumpvdl2_current:
                    print(f"skipping {target}")
                else:
                    results.append(f"{self.raw_dir}/{target}")

        return results

    def read_observations(self, file_name:str):
        print(file_name)

        observations = []

        # dumpvdl2 must be read line by line because invalid json
        with open(file_name, "r") as acars_file:
            try:
                buffer = acars_file.readlines()
                for row in buffer:
                    observations.append(row.strip())
            except Exception as error:
                logger.exception("file read error: %s", error)
                adsbex_key = None

        return observations

    def write_json_wrapper(self, base_file_name:str, observations) -> None:
        epoch_seconds = int(time.time())
        dt_object_utc = datetime.datetime.fromtimestamp(
            epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        )

        results = {
            "equipment": {
                "antenna": self.antenna,
                "receiverId": self.receiver_id,
                "receiverType": self.receiver_type,
                "hostName": self.host_name,
                "hostType": self.host_type,
            },
            "geoLoc": {
                "altitude": self.altitude,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "siteName": self.site_name,
            },
            "timeStamp": {
                "epochSeconds": epoch_seconds,
                "iso8601": dt_object_utc.isoformat(),
            },
            "crate": self.crate_name,
            "fileName": f"{base_file_name}.json",
            "mode": self.receiver_mode,
            "project": self.receiver_task,
            "version": 1,
            "observations": observations,
        }

        outfile_json = f"{self.fresh_dir}/{base_file_name}.json"
        JsonHelper().json_file_writer(outfile_json, results)


    def execute(self) -> None:
        print(f"collector execute: {self.receiver_task}")

        candidates = self.acars_file_discovery()
        for candidate in candidates:
            observations = self.read_observations(candidate)

            base_file_name = str(uuid.uuid4())
            print(f"base filename: {base_file_name}")

            self.write_json_wrapper(base_file_name, observations)
            os.remove(candidate)

#
# argv[1] = configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "config.yaml"

    with open(file_name, "r") as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = Collector(configuration)
            collector.execute()
        except yaml.YAMLError as error:
            print(error)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
