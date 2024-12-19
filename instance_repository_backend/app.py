import logging
from pathlib import Path

from fastapi import FastAPI

from .database import create_tables, get_session
from .problem_endpoint import ProblemEndpoint

logging.basicConfig(level=logging.INFO)

knapsack = ProblemEndpoint(Path("./PROBLEMS/knapsack"))
multi_knapsack = ProblemEndpoint(Path("./PROBLEMS/multi_knapsack"))

def create_index():
    create_tables()
    with get_session() as session:
        knapsack.sync(session)
        multi_knapsack.sync(session)


create_index()

app = FastAPI()
knapsack.build_routes(app)
multi_knapsack.build_routes(app)