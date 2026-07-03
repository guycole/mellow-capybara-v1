#
# Title: capybara_app.py
# Description: driver for capybara application
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from validator import Validator
from postgres import PostGres

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("capybara")

class CapybaraApp:

    def __init__(self, stunt_box: str):
        self.stunt_box = stunt_box

        # wombat docker
        self.db_conn = "postgresql+psycopg2://capybara_client:batabat@172.17.0.1:5432/capybara"

        # mac development
        # self.db_conn = "postgresql+psycopg2://capybara_client:batabat@localhost:5432/capybara"

        db_engine = create_engine(self.db_conn, echo=False)
        self.postgres = PostGres(sessionmaker(bind=db_engine, expire_on_commit=False))

    def execute(self) -> None:
        logger.info(f"capybara execute:{self.stunt_box}")

        if self.stunt_box == "validator":
            validator = Validator(self.postgres)
            validator.execute()
        else:
            logger.error(f"invalid stunt_box option:{self.stunt_box}")
            return

if __name__ == "__main__":
    stunt_box = os.environ.get("stuntbox", "validator")

    app = CapybaraApp(stunt_box)
    app.execute()

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
