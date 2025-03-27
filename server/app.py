import logging
import os

from fastapi import FastAPI

from server.app_config import PROBLEMS


logging.basicConfig(level=logging.INFO)

# read from environment variable
IRB_ROOT = os.getenv("IRB_ROOT", "/")
app = FastAPI(root_path=IRB_ROOT)
for problem in PROBLEMS:
    problem.build_routes(app)
