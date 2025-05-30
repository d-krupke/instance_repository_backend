from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
    model_validator,
)


class EuclideanTravelingSalesmanInstance(BaseModel):
    """Pydantic model representing a euclidean TSP instance."""

    # Metadata
    instance_uid: str = Field(..., description="The unique identifier of the instance.")
    origin: str = Field(default="", description="The origin or source of the instance.")
    comment: str = Field(default="", description="Any comments to the instance.")

    # Instance statistics
    num_points: PositiveInt = Field(..., description="The number of points to tour.")
    is_integral: bool = Field(
        default=False,
        description="Specifies if the point coordinates are integral.",
    )

    # Instance data
    points: list[tuple[float | int, float | int]] = Field(
        ...,
        description="List of points as (x,y) tuples.",
    )

    schema_version: int = Field(
        default=0,
        description="Schema version of the instance. If the schema changes, this will be incremented.",
    )

    # ---------------------------------------------
    # Additional validation methods
    @model_validator(mode="after")
    def validate_instance(self) -> "EuclideanTravelingSalesmanInstance":
        if len(self.points) != self.num_points:
            raise ValueError(
                f"Expected {self.num_points} points, got {len(self.points)}"
            )
        if self.is_integral:

            def check_integral(x):
                return isinstance(x, int) or (isinstance(x, float) and x.is_integer())

            if not all(
                check_integral(coord) for point in self.points for coord in point
            ):
                raise ValueError(
                    "All point coordinates must be integers when is_integral is True."
                )
        return self


class EuclideanTravelingSalesmanSolution(BaseModel):
    """Pydantic model representing a solution to a facility location problem instance."""

    # Solution metadata
    instance_uid: str = Field(
        ..., description="The unique identifier of the corresponding instance."
    )
    objective: NonNegativeFloat = Field(
        ...,
        description="The total tour length.",
    )
    authors: str = Field(
        ..., description="The authors or contributors of the solution."
    )

    # Solution data
    order: list[NonNegativeInt] = Field(
        ..., description=("Indices of points in visiting order.")
    )

    schema_version: int = Field(
        default=0,
        description="Schema version of the instance. If the schema changes, this will be incremented.",
    )


# Configuration constants for the multi-knapsack problem

# Unique identifier for the problem
PROBLEM_UID = "euclidean-tsp"

PROBLEM_NAME = "Euclidean Traveling Salesman Problem (2D)"
PROBLEM_DESCRIPTION = "The Euclidean Traveling Salesman Problem is a classic optimization problem where the goal is to find the shortest possible route that visits a set of points (cities) exactly once and returns to the origin point. The distance between points is calculated using the Euclidean distance formula."

# Shared attribute name for instances and solutions
INSTANCE_UID_ATTRIBUTE = "instance_uid"

# Schema definitions
INSTANCE_SCHEMA = EuclideanTravelingSalesmanInstance
SOLUTION_SCHEMA = EuclideanTravelingSalesmanSolution

# Filtering and sorting configurations
RANGE_FILTERS = [
    "num_points",
]  # Fields usable for range filters
BOOLEAN_FILTERS = [
    "is_integral",
]  # Boolean fields usable for filters
SORT_FIELDS = [
    "num_points",
]  # Fields for sorting

# Fields for display purposes in instance overviews
DISPLAY_FIELDS = [
    "instance_uid",
    "num_points",
    "is_integral",
    "origin",
    "comment",
]

# Assets associated with the multi-knapsack problem
ASSETS = {"thumbnail": "png", "image": "png"}

# Solution-specific configurations
SOLUTION_SORT_ATTRIBUTES = ["objective"]  # Fields for sorting solutions
SOLUTION_DISPLAY_FIELDS = ["objective", "authors"]  # Fields to display for solutions
