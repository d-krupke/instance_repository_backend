from pydantic import BaseModel, HttpUrl
import yaml

class ProblemConfig(BaseModel):
    config_path: str
    instance_path: str
    instance_url: HttpUrl
    assets_path: str
    assets_url: HttpUrl
    solution_path: str
    solution_url: HttpUrl
    api_key: str

class AppConfig(BaseModel):
    problems: list[ProblemConfig]
    database: str
    api_key: str

def load_config(file_path: str) -> AppConfig:
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return AppConfig(**config_data)

