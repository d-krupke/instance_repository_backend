import logging

from fastapi import FastAPI

from instance_repository_backend.app_config import PROBLEMS


logging.basicConfig(level=logging.INFO)

app = FastAPI()
for problem in PROBLEMS:
    problem.build_routes(app)
