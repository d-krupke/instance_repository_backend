from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    model_validator,
)


class FacilityLocationInstance(BaseModel):
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

    schema_version: int = Field(
        default=0,
        description="Schema version of the instance. If the schema changes, this will be incremented.",
    )

    # The "after" mode is chosen to ensure validation occurs after all fields are populated.
    # This allows cross-field validation, such as checking relationships between multiple fields.
    @model_validator(mode="after")
    def validate_instance(self) -> "FacilityLocationInstance":
        if len(self.path_cost) != self.num_cities:
            raise ValueError(
                f"Expected {self.num_cities} rows in path_cost, got {len(self.path_cost)}"
            )
        if any(len(row) != self.num_facilities for row in self.path_cost):
            raise ValueError("Each row in path_cost must have num_facilities columns.")
        if len(self.opening_cost) != self.num_facilities:
            raise ValueError(
                f"Expected {self.num_facilities} opening costs, got {len(self.opening_cost)}"
            )
        # Returning the class instance itself after validation to indicate successful validation
        # and to allow further processing of the validated instance.
        return self


class FacilityLocationSolution(BaseModel):
    """Pydantic model representing a solution to a facility location problem instance."""

    # Solution metadata
    instance_uid: str = Field(
        ..., description="The unique identifier of the corresponding instance."
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
PROBLEM_UID = "facility-location"

# Shared attribute name for instances and solutions
INSTANCE_UID_ATTRIBUTE = "instance_uid"

# Schema definitions
INSTANCE_SCHEMA = FacilityLocationInstance
SOLUTION_SCHEMA = FacilityLocationSolution

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
