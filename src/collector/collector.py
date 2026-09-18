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
import pydantic
import shutil
import sys
import time
import uuid
import zoneinfo
from typing import Any

import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("capybara")

class Equipment(pydantic.BaseModel):
    hostName: str
    hostType: str

class GeoLoc(pydantic.BaseModel):
    altitude: float
    latitude: float
    longitude: float
    siteName: str

class Job(pydantic.BaseModel):
    mode: str
    project: str
    task: str

class Receiver(pydantic.BaseModel):
    antenna: str
    receiverId: int
    task: str
    type: str

class TimeStamp(pydantic.BaseModel):
    epochSeconds: int = pydantic.Field(default_factory=lambda: int(time.time()))
    iso8601: str = ""

    @pydantic.model_validator(mode="after")
    def sync_iso8601_from_epoch(self) -> "TimeStamp":
        self.iso8601 = datetime.datetime.fromtimestamp(
            self.epochSeconds, tz=zoneinfo.ZoneInfo("UTC")
        ).isoformat()
        return self

class CapybaraModel(pydantic.BaseModel):
    crateName: str
    fileName: str
    sourceFileName: str
    version: int = 2
    equipment: Equipment
    geoLoc: GeoLoc
    job: Job
    receiver: Receiver
    timeStamp: TimeStamp
    observations: list[dict[str, Any]]

class Collector:

    def __init__(self, args: dict[str, any]):
        self.crate_name = args["crateName"]
        self.fresh_dir = args["freshDir"]
        self.raw_dir = args["rawDir"]

        self.equipment = Equipment(**args["equipment"])
        self.geo_loc = GeoLoc(**args["geoLoc"])
        self.receiver = Receiver(**args["receiver"])

        # capybara-v1-sf1-slow
        task = args["receiver"]["task"]
        tokens = task.split("-")
        mode = "-".join(tokens[2:])
        project = "-".join(tokens[:-2])
        self.job = Job(mode=mode, project=project, task=task)

        self.time_stamp = TimeStamp()

    def file_discovery(self):
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
                    print(f"adding {target} to acars")
                    results.append(f"{self.raw_dir}/{target}")

            if target.startswith("vdl2"):
                if target == dumpvdl2_current:
                    print(f"skipping {target}")
                else:
                    print(f"adding {target} to vdl2")
                    results.append(f"{self.raw_dir}/{target}")

        return results

    def read_observations(self, file_name: str):
        observations = []

        with open(file_name, "r") as acars_file:
            # must be read line by line because file is not valid json list
            try:
                buffer = acars_file.readlines()
                for row in buffer:
                    temp = json.loads(row)
                    temp["uuid"] = str(uuid.uuid4())
                    observations.append(temp)
            except Exception as error:
                logger.exception("file read error: %s", error)

        return observations

    def write_json_wrapper(
        self, observations: list[str], source_file_name: str
    ) -> bool:
        file_name = f"{str(uuid.uuid4())}.json"

        capybara_model = CapybaraModel(
            crateName = self.crate_name,
            fileName = file_name,
            sourceFileName = source_file_name,
            equipment = self.equipment,
            geoLoc = self.geo_loc,
            job = self.job,
            receiver = self.receiver,
            timeStamp = self.time_stamp,
            observations = observations
        )

        outfile_json = f"{self.fresh_dir}/{file_name}"
        with open(outfile_json, "w", encoding="utf-8") as out_file:
            out_file.write(capybara_model.model_dump_json(indent=4))

        return 0

    def execute(self) -> None:
        logger.info(f"collector execute")

        candidates = self.file_discovery()
        logger.info(f"{len(candidates)} files to process")

        for candidate in candidates:
            observations = self.read_observations(candidate)
            source_file_name = os.path.basename(candidate)
            retflag = self.write_json_wrapper(observations, source_file_name)
            if retflag == 0:
                logger.info(f"successfully wrote wrapper for {source_file_name}")
            else:
                logger.error(f"failed to write wrapper for {source_file_name}")

            dest_file = f"{self.fresh_dir}/{source_file_name}"
            shutil.move(candidate, dest_file)

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
