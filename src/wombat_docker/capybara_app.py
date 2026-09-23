#
# Title: capybara_app.py
# Description: driver for capybara application
# Development Environment: Ubuntu 22.04.5 LTS/python 3.10.12
# Author: G.S. Cole (guycole at gmail dot com)
#
import logging
import os

from helper.postgres import PostGres
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from validator import CapybaraValidator

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("capybara")


class CapybaraApp:

    def __init__(self, stunt_box: str):
        self.stunt_box = stunt_box

        self.db_conn = os.environ.get(
            "DB_CONN",
            "postgresql+psycopg2://capybara_client:batabat@localhost:5432/capybara",
        )

        connect_timeout = int(os.environ.get("PG_CONNECT_TIMEOUT", "5"))
        statement_timeout_ms = int(os.environ.get("PG_STATEMENT_TIMEOUT_MS", "5000"))

        db_engine = create_engine(
            self.db_conn,
            echo=False,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": connect_timeout,
                "options": f"-c statement_timeout={statement_timeout_ms}",
            },
        )
        self.postgres = PostGres(sessionmaker(bind=db_engine, expire_on_commit=False))

    def execute(self) -> int:
        logger.info(f"capybara execute:{self.stunt_box}")

        if self.stunt_box == "validator":
            validator = CapybaraValidator(logger, self.postgres)
            return validator.execute()
        else:
            logger.error(f"invalid stunt_box option:{self.stunt_box}")
            return 1

        return 0


if __name__ == "__main__":
    stunt_box = os.environ.get("stuntbox", "validator")

    app = CapybaraApp(stunt_box)
    exit(app.execute())

# ;;; Local Variables: ***
# ;;; mode:python ***
# ;;; End: ***
