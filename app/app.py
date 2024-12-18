from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session
from fastapi import FastAPI
import logging

from abstract_problem.problem_info import load_problem_info_from_file
from abstract_problem.instance_index import InstanceIndex
from abstract_problem.instance_repository import InstanceRepository
from abstract_problem.routes import build_routes_for_problem
from abstract_problem.solution_repository import SolutionRepository
from abstract_problem.solution_index import SolutionIndex

logging.basicConfig(level=logging.INFO)

app = FastAPI()


def sync_instance_index(instance_index, instance_repository, session):
    instance_uids_in_db = instance_index.get_instance_uids(session)
    instance_uids_in_repo = instance_repository.get_all_instance_uids()

    for instance_uid in set(instance_uids_in_db) - set(instance_uids_in_repo):
        instance_index.deindex_instance(instance_uid, session)

    for instance_uid in set(instance_uids_in_repo) - set(instance_uids_in_db):
        instance = instance_repository.read_instance(instance_uid)
        instance_index.index_instance(instance, session)


def sync_solution_index(solution_index, solution_repository, session):
    solution_uids = solution_repository.list_all_solution_uids()

    for solution_uid in solution_uids:
        if solution_index.exists(solution_uid, session=session):
            continue
        solution = solution_repository.read_solution(solution_uid)
        solution_index.index_solution(
            solution_uid=solution_uid, solution=solution, session=session
        )


def load_problem(app: FastAPI, path: Path):
    problem_info = load_problem_info_from_file(path)
    instance_repository = InstanceRepository(problem_info)
    instance_index = InstanceIndex(problem_info)
    solution_repository = (
        SolutionRepository(problem_info) if problem_info.solution_model else None
    )
    solution_index = (
        SolutionIndex(problem_info) if problem_info.solution_model else None
    )
    engine = create_engine("sqlite:///test.db")
    SQLModel.metadata.create_all(engine)

    build_routes_for_problem(
        app,
        problem_info,
        instance_repository,
        instance_index,
        solution_index=solution_index,
        solution_repository=solution_repository,
        engine=engine,
    )

    with Session(engine) as session:
        sync_instance_index(instance_index, instance_repository, session)

        if solution_index and solution_repository:
            sync_solution_index(solution_index, solution_repository, session)


load_problem(app, Path("./PROBLEMS/knapsack"))
