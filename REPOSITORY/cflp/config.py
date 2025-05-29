from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
)


class CapacitatedFacilityLocationInstance(BaseModel):
    """Pydantic model representing a facility location problem instance."""

    # Metadata
    instance_uid: str = Field(..., description="The unique identifier of the instance.")
    origin: str = Field(default="", description="The origin or source of the instance.")
    comment: str = Field(default="", description="Any comments to the instance.")

    # Instance statistics
    num_cities: PositiveInt = Field(
        ..., description="The number of cities to allocate."
    )
    num_facilities: PositiveInt = Field(
        ..., description="The number of potential facility locations."
    )
    is_integral: bool = Field(
        default=False,
        description="Specifies if the facility opening and connection costs are integral.",
    )

    # Instance data
    capacities: list[NonNegativeFloat | NonNegativeInt] = Field(
        ...,
        description="Maximum capacity of each facility in the capacitated variant.",
    )
    opening_cost: list[NonNegativeFloat | NonNegativeInt] = Field(
        ...,
        description="Opening cost of each facility.",
    )
    path_cost: list[list[NonNegativeFloat | NonNegativeInt]] = Field(
        ...,
        description=(
            "Cost to to travel from each city (outer) to each facility (inner). "
            "`path_cost[i][k]` is the cost from city *i* to facility *k*."
        ),
    )
    demand: list[NonNegativeFloat | NonNegativeInt] = Field(
        ...,
        description="Demand of each city in capacitated variant.",
    )

    schema_version: int = Field(
        default=0,
        description="Schema version of the instance. If the schema changes, this will be incremented.",
    )


class CapacitatedFacilityLocationSolution(BaseModel):
    """Pydantic model representing a solution to a facility location problem instance."""

    # Solution metadata
    instance_uid: str = Field(
        ..., description="The unique identifier of the corresponding instance"
    )
    objective: NonNegativeFloat = Field(
        ..., description="The total cost of opened facilities and city paths."
    )
    authors: str = Field(
        ..., description="The authors or contributors of the solution."
    )

    # Solution data
    allocations: list[NonNegativeInt] = Field(
        ...,
        description=(
            "Facility index for every instance City. "
            "If list[*k*] = *l*, then city *k* is connected to facility *l*."
        ),
    )

    schema_version: int = Field(
        default=0,
        description="Schema version of the instance. If the schema changes, this will be incremented.",
    )


# Configuration constants for the multi-knapsack problem

# Unique identifier for the problem
PROBLEM_UID = "capacitated-facility-location"

# Shared attribute name for instances and solutions
INSTANCE_UID_ATTRIBUTE = "instance_uid"

# Schema definitions
INSTANCE_SCHEMA = CapacitatedFacilityLocationInstance
SOLUTION_SCHEMA = CapacitatedFacilityLocationSolution

# Filtering and sorting configurations
RANGE_FILTERS = [
    "num_cities",
    "num_facilities",
]  # Fields usable for range filters
BOOLEAN_FILTERS = [
    "is_integral",
]  # Boolean fields usable for filters
SORT_FIELDS = [
    "num_cities",
    "num_facilities",
]  # Fields for sorting

# Fields for display purposes in instance overviews
DISPLAY_FIELDS = [
    "instance_uid",
    "num_cities",
    "num_facilities",
    "is_integral",
    "origin",
    "comment",
]

# Assets associated with the multi-knapsack problem
ASSETS = {"thumbnail": "png", "image": "png"}

# Solution-specific configurations
SOLUTION_SORT_ATTRIBUTES = ["objective"]  # Fields for sorting solutions
SOLUTION_DISPLAY_FIELDS = ["objective", "authors"]  # Fields to display for solutions
