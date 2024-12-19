from pathlib import Path

from fastapi import FastAPI

from abstract_problem.database import create_tables, get_session
from abstract_problem.problem_endpoint import ProblemEndpoint

app = FastAPI()
knapsack = ProblemEndpoint(Path("../PROBLEMS/knapsack"))
create_tables()
knapsack.build_routes(app)
with get_session() as session:
    knapsack.sync(session)
