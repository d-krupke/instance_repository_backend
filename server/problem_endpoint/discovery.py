import logging
from fastapi import FastAPI
from pydantic import BaseModel, Field

from .problem_endpoint import ProblemEndpoint

from .problem_info import ProblemInfo


class ServerOverview(BaseModel):
    available_problems: list[ProblemInfo] = Field(
        default_factory=list,
        description="A list of all available problems with their metadata.",
    )


def build_discovery_route(app: FastAPI, problems: list[ProblemEndpoint]):
    """
    Build a route for discovering available problems.
    """

    router = app.router
    logging.info(
        "Building discovery route for available problems: %s",
        [problem.problem_info.problem_uid for problem in problems],
    )

    @router.get("/", response_model=ServerOverview)
    def discover_problems() -> ServerOverview:
        """
        Discover all available problems with their metadata.
        """
        return ServerOverview(
            available_problems=[
                problem.problem_info.get_serializable_base() for problem in problems
            ]
        )
