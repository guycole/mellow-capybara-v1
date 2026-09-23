#
# Title: collector.py
# Description:
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import datetime
import json
import logging
import shutil
import sys
import time
import uuid
import zoneinfo
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pydantic
import yaml
from yaml.loader import SafeLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("capybara")


class Equipment(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    host_name: str = pydantic.Field(alias="hostName")
    host_type: str = pydantic.Field(alias="hostType")


class GeoLoc(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    altitude: float
    latitude: float
    longitude: float
    site_name: str = pydantic.Field(alias="siteName")


class Job(pydantic.BaseModel):
    mode: str
    project: str
    task: str


class Receiver(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    antenna: str
    receiver_id: int = pydantic.Field(alias="receiverId")
    task: str
    type: str


class TimeStamp(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    epoch_seconds: int = pydantic.Field(
        default_factory=lambda: int(time.time()), alias="epochSeconds"
    )
    iso8601: str = ""

    @pydantic.model_validator(mode="after")
    def sync_iso8601_from_epoch(self) -> "TimeStamp":
        self.iso8601 = datetime.datetime.fromtimestamp(
            self.epoch_seconds, tz=zoneinfo.ZoneInfo("UTC")
        ).isoformat()
        return self


class CapybaraModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(populate_by_name=True)

    crate_name: str = pydantic.Field(alias="crateName")
    file_name: str = pydantic.Field(alias="fileName")
    source_file_name: str = pydantic.Field(alias="sourceFileName")
    version: int = 2
    equipment: Equipment
    geo_loc: GeoLoc = pydantic.Field(alias="geoLoc")
    job: Job
    receiver: Receiver
    time_stamp: TimeStamp = pydantic.Field(alias="timeStamp")
    observations: list[dict[str, Any]]


class CollectorBase(ABC):

    @abstractmethod
    def discover_candidates(self) -> list[Path]:
        pass

    @abstractmethod
    def execute(self) -> int:
        pass


class Collector(CollectorBase):

    def __init__(self, args: dict[str, Any]):
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

    def discover_candidates(self) -> list[Path]:
        gmt_now = datetime.datetime.now(datetime.timezone.utc)

        year = gmt_now.year
        month = gmt_now.month
        day = gmt_now.day
        hour = gmt_now.hour

        # dumpvdl2 output filenames have the form  vdl12_YYYYMMDD_HH.json
        dumpvdl2_current = f"vdl2_{year}{month:02d}{day:02d}_{hour:02d}.json"

        # acarsdec output filenames have the form  acars_YYYYMMDD_HH.json
        acars_current = f"acars_{year}{month:02d}{day:02d}_{hour:02d}.json"

        results: list[Path] = []
        raw_dir = Path(self.raw_dir)
        targets = sorted(raw_dir.iterdir())
        logger.info("%s files noted", len(targets))

        for target in targets:
            if target.name.startswith("acars"):
                if target.name == acars_current:
                    logger.info("skipping %s", target.name)
                else:
                    logger.info("adding %s to acars", target.name)
                    results.append(target)

            if target.name.startswith("vdl2"):
                if target.name == dumpvdl2_current:
                    logger.info("skipping %s", target.name)
                else:
                    logger.info("adding %s to vdl2", target.name)
                    results.append(target)

        return results

    def read_observations(self, file_name: str) -> list[dict[str, Any]]:
        observations: list[dict[str, Any]] = []

        with open(file_name) as acars_file:
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
        self, observations: list[dict[str, Any]], source_file_name: str
    ) -> int:
        file_name = f"{str(uuid.uuid4())}.json"

        capybara_model = CapybaraModel(
            crate_name=self.crate_name,
            file_name=file_name,
            source_file_name=source_file_name,
            equipment=self.equipment,
            geo_loc=self.geo_loc,
            job=self.job,
            receiver=self.receiver,
            time_stamp=self.time_stamp,
            observations=observations,
        )

        outfile_json = f"{self.fresh_dir}/{file_name}"
        with open(outfile_json, "w", encoding="utf-8") as out_file:
            out_file.write(capybara_model.model_dump_json(indent=4, by_alias=True))

        return 0

    def execute(self) -> int:
        logger.info("collector execute")

        candidates = self.discover_candidates()
        logger.info("%s files to process", len(candidates))

        for candidate in candidates:
            observations = self.read_observations(str(candidate))
            source_file_name = candidate.name
            retflag = self.write_json_wrapper(observations, source_file_name)
            if retflag == 0:
                logger.info("successfully wrote wrapper for %s", source_file_name)
            else:
                logger.error("failed to write wrapper for %s", source_file_name)

            dest_file = f"{self.fresh_dir}/{source_file_name}"
            shutil.move(str(candidate), dest_file)

        return 0


#
# argv[1] = configuration filename
#
if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "config.yaml"

    with open(file_name) as in_file:
        try:
            configuration = yaml.load(in_file, Loader=SafeLoader)
            collector = Collector(configuration)
            exit(collector.execute())
        except yaml.YAMLError as error:
            logger.error("YAML parse error: %s", error)

    exit(1)

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
