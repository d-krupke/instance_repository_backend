from pathlib import Path
from typing import Type
from pydantic import BaseModel, Field


class ProblemInfo(BaseModel):
    problem_uid: str = Field(..., description="The unique identifier of the problem")
    uid_attribute: str = Field(
        default="instance_uid",
        description="The attribute of the instance that contains the unique identifier",
    )
    range_filters: list[str] = Field(
        default_factory=list,
        description="The fields that can be used to filter the instances with a range. The corresponding instance model should have a numerical type (int or float) field with the same name.",
    )
    boolean_filters: list[str] = Field(
        default_factory=list,
        description="Boolean fields that can be used to filter the instances. The corresponding instance model should have a boolean type field with the same name.",
    )
    sort_fields: list[str] = Field(
        default_factory=list,
        description="The fields that can be used to sort the instances",
    )
    display_fields: list[str] = Field(
        default_factory=list,
        description="The fields that should be displayed in an overview of the instances and, thus, must be quick to access.",
    )
    instance_model: Type[BaseModel] = Field(
        ..., description="The Pydantic model of the instance"
    )
    solution_model: Type[BaseModel] | None = Field(
        default=None, description="The Pydantic model of the solution"
    )
    assets_root: Path = Field(
        ...,
        description="The path to the directory of the assets for storage.",
    )
    assets_url_root: str = Field(
        ...,
        description="The URL root of the assets via which external users can access the assets.",
    )
    instances_root: Path = Field(
        ...,
        description="The path to the directory of the instances for storage.",
    )
    instances_url_root: str = Field(
        ...,
        description="The URL root of the instances via which external users can access the instances.",
    )
    solutions_root: Path = Field(
        ...,
        description="The path to the directory of the solutions for storage.",
    )
    solutions_url_root: str = Field(
        ...,
        description="The URL root of the solutions via which external users can access the solutions.",
    )
    postfix_query: str = Field(
        default="",
        description="A postfix for the query arguments in the URL. This can be used in case of name clashes with, e.g., the `search` argument.",
    )
    postfix_query_leq: str = Field(
        default="__leq",
        description="The postfix for the less than or equal to query arguments in the URL.",
    )
    postfix_query_geq: str = Field(
        default="__geq",
        description="The postfix for the greater than or equal to query arguments in the URL.",
    )
    assets: dict[str, str] = Field(
        default_factory=dict,
        description="The asset classes and their extensions. The keys are the asset classes, and the values are the extensions, e.g., {'image': 'png'}.",
    )
    solution_index_field: str = Field(
        default="solution_uid",
        description="The attribute of the solution that contains the unique identifier",
    )
    solution_display_fields: list[str] = Field(
        default_factory=list,
        description="The fields that should be displayed in an overview of the solutions and, thus, must be quick to access.",
    )
    solution_sort_by: list[str] = Field(
        default_factory=list,
        description="The fields will be used to sort the solution by quality. Add a `-` in front in case the field should be sorted in descending order.",
    )


def is_valid_postfix(postfix: str) -> bool:
    """
    Check if the postfix is valid.
    """
    return all(c.isalnum() or c in "_" for c in postfix)


def load_problem_info_from_file(path: Path) -> ProblemInfo:
    """
    Load the problem information from a Python file.
    """
    config_path = path / "config.py"
    if not config_path.exists():
        raise ValueError(f"No config.py file found in {path}")
    # Load the content of the file
    with config_path.open("r") as file:
        content = file.read()
    # Execute the content of the file
    problem_vars = {}
    exec(content, problem_vars)

    # The problem uid should be in `PROBLEM_UID`
    problem_uid = problem_vars.get("PROBLEM_UID")
    if problem_uid is None:
        raise ValueError("No PROBLEM_UID found in the file")
    # The instance schema should be in `INSTANCE_SCHEMA`
    instance_schema = problem_vars.get("INSTANCE_SCHEMA")
    if instance_schema is None:
        raise ValueError("No INSTANCE_SCHEMA found in the file")
    solution_schema = problem_vars.get("SOLUTION_SCHEMA", None)
    solution_sort_attributes = problem_vars.get("SOLUTION_SORT_ATTRIBUTE", [])
    solution_display_fields = problem_vars.get("SOLUTION_DISPLAY_FIELDS", [])
    # The range filters should be in `RANGE_FILTERS`
    range_filters = problem_vars.get("RANGE_FILTERS")
    if range_filters is None:
        raise ValueError("No RANGE_FILTERS found in the file")
    # The boolean filters should be in `BOOLEAN_FILTERS`
    boolean_filters = problem_vars.get("BOOLEAN_FILTERS")
    if boolean_filters is None:
        raise ValueError("No BOOLEAN_FILTERS found in the file")
    # The sort fields should be in `SORT_FIELDS`
    sort_fields = problem_vars.get("SORT_FIELDS")
    if sort_fields is None:
        raise ValueError("No SORT_FIELDS found in the file")
    # The display fields should be in `DISPLAY_FIELDS`
    display_fields = problem_vars.get("DISPLAY_FIELDS")
    if display_fields is None:
        raise ValueError("No DISPLAY_FIELDS found in the file")
    assets = problem_vars.get("ASSETS", {})
    # Postfixes
    postfix_query = problem_vars.get("POSTFIX_QUERY", "")
    if not is_valid_postfix(postfix_query):
        raise ValueError(
            "The POSTFIX_QUERY is not valid. It should only contain alphanumeric characters and underscores."
        )
    postfix_query_leq = problem_vars.get("POSTFIX_QUERY_LEQ", "__leq")
    if not is_valid_postfix(postfix_query_leq):
        raise ValueError(
            "The POSTFIX_QUERY_LEQ is not valid. It should only contain alphanumeric characters and underscores."
        )
    postfix_query_geq = problem_vars.get("POSTFIX_QUERY_GEQ", "__geq")
    if not is_valid_postfix(postfix_query_geq):
        raise ValueError(
            "The POSTFIX_QUERY_GEQ is not valid. It should only contain alphanumeric characters and underscores."
        )
    # Create the ProblemInfo instance
    problem_info = ProblemInfo(
        instances_root=path / "instances",
        instances_url_root=f"/{problem_uid}/instances",
        solutions_root=path / "solutions",
        solutions_url_root=f"/{problem_uid}/solutions",
        assets_root=path / "assets",
        assets_url_root=f"/{problem_uid}/assets",
        problem_uid=problem_uid,
        instance_model=instance_schema,
        range_filters=range_filters,
        boolean_filters=boolean_filters,
        sort_fields=sort_fields,
        display_fields=display_fields,
        postfix_query=postfix_query,
        postfix_query_leq=postfix_query_leq,
        postfix_query_geq=postfix_query_geq,
        assets=assets,
        solution_model=solution_schema,
        solution_sort_by=solution_sort_attributes,
        solution_display_fields=solution_display_fields,
    )
    return problem_info
