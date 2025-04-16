from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
    conlist,
)
from typing import List, Optional

class JobShopInstance(BaseModel):

    # Metadata
    instance_uid: str = Field(..., description="The unique identifier of the instance")
    origin: str = Field(default="", description="The origin or source of the instance")

    # Instance Statistics
    number_of_jobs: PositiveInt = Field(
        ..., description="The number of jobs available in the instance"
    )
    number_of_machines: PositiveInt = Field(
        ..., description="The number of machines available in the instance"
    )
    time_seed: PositiveInt = Field(
        ..., description="Seed used for generating processing times"
    )
    machine_seed: PositiveInt = Field(
        ..., description="Seed used for assigning machines to operations"
    )
    upper_bound: PositiveInt = Field(
        ..., description="Upper bound on the makespan or objective value"
    )
    lower_bound: PositiveInt = Field(
        ..., description="Lower bound on the makespan or objective value"
    )
    '''
    Times and machine are matrix 
    In times : row corresponds to a job and each column to the processing time for a operation
    In Machines : row corresponds to a job and each column to the machine index on that operation 
    '''
    times: List[conlist(int, min_items=1)]
    machines: List[conlist(int, min_items=1)]

    # can add a validator here to validate that times and machines have the same shape, but cant confirm for now

class JobShopSolution(BaseModel):
    '''Pydantic model representing a solution to a Job Shop problem instance'''
    '''TODO : What exaclty should come inside the solution part?'''
    instance_uid: str = Field(
        ..., description="The unique identifier of the corresponding instance"
    )
    makespan: Optional[int]
    authors: Optional[str]

# Configuration constants for the Job Shop Scheduling Problem

# Unique identifier for the problem
PROBLEM_UID = "job_shop"

# Shared attribute name for instances and solutions
INSTANCE_UID_ATTRIBUTE = "instance_uid"

# Schema definitions

INSTANCE_SCHEMA = JobShopInstance
SOLUTION_SCHEMA = JobShopSolution

# Filtering and sorting configurations
RANGE_FILTERS = [
    "number_of_jobs",
    "number_of_machines",
    "upper_bound",
    "lower_bound",
]  # Numeric fields usable for range filters

BOOLEAN_FILTERS = []  # No explicit boolean flags unless added one

SORT_FIELDS = [
    "number_of_jobs",
    "number_of_machines",
    "upper_bound",
    "lower_bound",
]

# Fields for display purposes in instance overviews
DISPLAY_FIELDS = [
    "instance_uid",
    "number_of_jobs",
    "number_of_machines",
    "time_seed",
    "machine_seed",
    "upper_bound",
    "lower_bound",
]

# Assets associated with the job shop problem
ASSETS = {"thumbnail": "png", "image": "png"}  # Can link to Gantt charts or flow diagrams

# Solution-specific configurations
SOLUTION_SORT_ATTRIBUTES = ["makespan", "authors"]  # Hypothetical field names for now
SOLUTION_DISPLAY_FIELDS = ["makespan", "authors"]  # Show these in the frontend/table
