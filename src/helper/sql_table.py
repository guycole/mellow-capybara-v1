#
# Title: sql_table.py
# Description: database table definitions
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, Integer, String

from sqlalchemy.orm import registry
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr

mapper_registry = registry()

class Base(DeclarativeBase):
    pass

class DailyScore(Base):
    __tablename__ = "capybara_daily_score"

    id = Column(Integer, primary_key=True)
    crate_name = Column(String)
    file_quantity = Column(Integer)
    host_name = Column(String)
    quantity_slow = Column(Integer)
    quantity_fast = Column(Integer)
    score_date = Column(Date)

    def __init__(self, args: dict[str, any]):
        self.crate_name = args["crate_name"]
        self.file_quantity = args["file_quantity"]
        self.host_name = args["host_name"]
        self.quantity_slow = args["quantity_slow"]
        self.quantity_fast = args["quantity_fast"]
        self.score_date = args["score_date"]

    def __repr__(self):
        return f"daily_score({self.score_date} {self.host_name})"

class Frequency(Base):
    __tablename__ = "capybara_frequency"

    id = Column(BigInteger, primary_key=True)
    acars_type = Column(String(16), nullable=False)
    crate_name = Column(String(32), nullable=False)
    frequency = Column(Integer, nullable=False)
    host_name = Column(String(16), nullable=False)
    message_quantity = Column(Integer, nullable=False)
    score_date = Column(Date, nullable=False)

    def __init__(self, args: dict[str, any]):
        self.acars_type = args["acars_type"]
        self.crate_name = args["crate_name"]
        self.frequency = args["frequency"]
        self.host_name = args["host_name"]
        self.message_quantity = args["message_quantity"]
        self.score_date = args["score_date"]

    def __repr__(self):
        return f"frequency({self.score_date} {self.host_name})"

class GeoLoc(Base):
    __tablename__ = "capybara_geo_loc"

    id = Column(Integer, primary_key=True)
    altitude = Column(Float)
    course = Column(Float)
    fix_time = Column(DateTime)
    host_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    site_name = Column(String)
    speed = Column(Float)

    def __init__(self, args: dict[str, any]):
        self.altitude = args["altitude"]
        self.course = args["course"]
        self.fix_time = args["fix_time"]
        self.host_name = args["host_name"]
        self.latitude = args["latitude"]
        self.longitude = args["longitude"]
        self.site_name = args["site_name"]
        self.speed = args["speed"]

    def __repr__(self):
        return f"geo_loc({self.site_name} {self.host_name})"

class LoadLog(Base):
    """load_log table definition"""

    __tablename__ = "capybara_load_log"

    id = Column(Integer, primary_key=True)
    crate_name = Column(String)
    epoch_seconds = Column(BigInteger)
    file_name = Column(String)
    geo_loc_id = Column(BigInteger)
    host_name = Column(String)
    load_time = Column(DateTime)
    mode = Column(String)
    obs_quantity = Column(Integer)
    obs_time = Column(DateTime)
    parent_file_name = Column(String)
    site_name = Column(String)
    task = Column(String)

    def __init__(self, args: dict[str, any]):
        self.crate_name = args["crate_name"]
        self.epoch_seconds = args["epoch_seconds"]
        self.file_name = args["file_name"]
        self.geo_loc_id = args["geo_loc_id"]
        self.host_name = args["host_name"]
        self.load_time = args.get("load_time", datetime.now())
        self.mode = args["mode"]
        self.obs_quantity = args["obs_quantity"]
        self.obs_time = args["obs_time"]
        self.parent_file_name = args["parent_file_name"]
        self.site_name = args["site_name"]
        self.task = args["task"]

    def __repr__(self):
        return f"load_log({self.file_name} {self.obs_time} {self.task} {self.host_name})"

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
