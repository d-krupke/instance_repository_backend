from pathlib import Path

from sqlmodel import SQLModel
from abstract_problem.problem_info import load_problem_info_from_file
from abstract_problem.instance_index import InstanceIndex
from abstract_problem.instance_repository import InstanceRepository
from fastapi import FastAPI
from abstract_problem.routes import build_routes_for_problem
from sqlmodel import create_engine, Session

app = FastAPI()

def load_problem(app: FastAPI, path: Path):
    problem_info = load_problem_info_from_file(path)
    instance_repository = InstanceRepository(problem_info)
    instance_index = InstanceIndex(problem_info)
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)
    build_routes_for_problem(app, problem_info, instance_repository, instance_index, engine)

    with Session(engine) as session:
        instance_uids_in_db = instance_index.get_instance_uids(session)
        instance_uids_in_repo = instance_repository.get_all_instance_uids()
        for instance_uid in set(instance_uids_in_db) - set(instance_uids_in_repo):
            instance_index.deindex_instance(instance_uid, session)
        for instance_uid in set(instance_uids_in_repo) - set(instance_uids_in_db):
            instance = instance_repository.read_instance(instance_uid)
            instance_index.index_instance(instance, session)
        query = instance_index.query(instance_index.QuerySchema(), session)
        print(query)
        print(instance_index.get_range_query_bounds(session))



load_problem(app, Path("./PROBLEMS/knapsack"))