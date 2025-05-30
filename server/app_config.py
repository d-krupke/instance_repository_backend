import logging
from pathlib import Path

from .problem_endpoint import ProblemEndpoint

logging.basicConfig(level=logging.INFO)

# load all problems in `../REPOSITORY` with a `config.py` file
PROBLEMS: list[ProblemEndpoint] = []
for problem_path in (Path(__file__).parent.parent / "REPOSITORY").iterdir():
    if problem_path.is_dir() and (config := problem_path / "config.py").exists():
        PROBLEMS.append(ProblemEndpoint(problem_path))
