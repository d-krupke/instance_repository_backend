import logging

from .app_config import PROBLEMS

from .database import create_tables, get_session

logging.basicConfig(level=logging.INFO)


def sync():
    create_tables()
    with get_session() as session:
        for problem in PROBLEMS:
            problem.sync(session)


if __name__ == "__main__":
    sync()
