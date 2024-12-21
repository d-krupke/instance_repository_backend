from pathlib import Path
from sqlmodel import Session
from fastapi import FastAPI
import logging

from .problem_info import load_problem_info_from_file
from .instance_index import InstanceIndex
from .instance_repository import InstanceRepository
from .routes import build_routes_for_problem
from .solution_repository import SolutionRepository
from .solution_index import SolutionIndex

logging.basicConfig(level=logging.INFO)


class ProblemEndpoint:
    def __init__(self, path: Path):
        self.path = path
        self.problem_info = load_problem_info_from_file(path)
        self.instance_repository = InstanceRepository(self.problem_info)
        self.instance_index = InstanceIndex(self.problem_info)
        self.solution_repository = (
            SolutionRepository(self.problem_info)
            if self.problem_info.solution_model
            else None
        )
        self.solution_index = (
            SolutionIndex(self.problem_info)
            if self.problem_info.solution_model
            else None
        )

    def build_routes(self, app: FastAPI):
        logging.info(f"Building routes for {self.problem_info.problem_uid}")
        build_routes_for_problem(
            app,
            self.problem_info,
            self.instance_repository,
            self.instance_index,
            solution_index=self.solution_index,
            solution_repository=self.solution_repository,
        )

    def sync_instance_index(self, session: Session):
        logging.info(f"Syncing instance index for {self.problem_info.problem_uid}")
        instance_uids_in_db = self.instance_index.get_instance_uids(session)
        instance_uids_in_repo = self.instance_repository.get_all_instance_uids()

        for instance_uid in set(instance_uids_in_db) - set(instance_uids_in_repo):
            self.instance_index.deindex_instance(instance_uid, session)

        for instance_uid in set(instance_uids_in_repo) - set(instance_uids_in_db):
            instance = self.instance_repository.read_instance(instance_uid)
            self.instance_index.index_instance(instance, session)

    def sync_solution_index(self, session: Session):
        if not self.solution_index:
            logging.info(f"No solution index for {self.problem_info.problem_uid}")
            return
        if not self.solution_repository:
            logging.info(f"No solution repository for {self.problem_info.problem_uid}")
            return

        logging.info(f"Syncing solution index for {self.problem_info.problem_uid}")
        solution_uids = self.solution_repository.list_all_solution_uids()

        for solution_uid in solution_uids:
            if self.solution_index.exists(solution_uid, session=session):
                continue
            logging.info("Indexing solution %s", solution_uid)
            solution = self.solution_repository.read_solution(solution_uid)
            self.solution_index.index_solution(
                solution_uid=solution_uid, solution=solution, session=session
            )

    def sync(self, session: Session):
        self.sync_instance_index(session)
        self.sync_solution_index(session)
