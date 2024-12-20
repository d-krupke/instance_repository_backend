from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
)


class MultiKnapsackInstance(BaseModel):
    """Pydantic model representing a multi-knapsack problem instance."""

    # Metadata
    instance_uid: str = Field(..., description="The unique identifier of the instance")
    origin: str = Field(default="", description="The origin or source of the instance")

    # Instance statistics
    num_items: PositiveInt = Field(
        ..., description="The number of items available in the instance"
    )
    num_knapsacks: PositiveInt = Field(
        ..., description="The number of knapsacks in the instance"
    )
    weight_capacity_ratio: PositiveFloat = Field(
        ...,
        description=(
            "The ratio of the total weight of all items to the total knapsack capacity. "
            "Calculated as the sum of item weights divided by the sum of knapsack capacities."
        ),
    )
    integral: bool = Field(
        default=False,
        description="Specifies if the capacities, values, and weights are integral.",
    )

    # Instance data
    capacities: list[NonNegativeFloat | NonNegativeInt] = Field(
        ..., description="The capacities of each knapsack"
    )
    item_values: list[NonNegativeFloat | NonNegativeInt] = Field(
        ..., description="The values assigned to each item"
    )
    item_weights: list[NonNegativeFloat | NonNegativeInt] = Field(
        ..., description="The weights assigned to each item"
    )


class MultiKnapsackSolution(BaseModel):
    """Pydantic model representing a solution to a multi-knapsack problem instance."""

    # Solution metadata
    instance_uid: str = Field(
        ..., description="The unique identifier of the corresponding instance"
    )
    objective: NonNegativeFloat = Field(
        ..., description="The total value of selected items across all knapsacks"
    )
    authors: str = Field(..., description="The authors or contributors of the solution")

    # Solution data
    allocations: list[list[int]] = Field(
        ...,
        description=(
            "Lists of item indices for each knapsack. "
            "Each sublist corresponds to the items allocated to one knapsack."
        ),
    )


# Configuration constants for the multi-knapsack problem

# Unique identifier for the problem
PROBLEM_UID = "multi-knapsack"

# Shared attribute name for instances and solutions
INSTANCE_UID_ATTRIBUTE = "instance_uid"

# Schema definitions
INSTANCE_SCHEMA = MultiKnapsackInstance
SOLUTION_SCHEMA = MultiKnapsackSolution

# Filtering and sorting configurations
RANGE_FILTERS = [
    "num_items",
    "num_knapsacks",
    "weight_capacity_ratio",
]  # Fields usable for range filters
BOOLEAN_FILTERS = ["integral"]  # Boolean fields usable for filters
SORT_FIELDS = ["num_items", "num_knapsacks", "weight_capacity_ratio"]  # Fields for sorting

# Fields for display purposes in instance overviews
DISPLAY_FIELDS = [
    "instance_uid",
    "num_items",
    "num_knapsacks",
    "weight_capacity_ratio",
    "integral",
    "origin",
]

# Assets associated with the multi-knapsack problem
ASSETS = {"thumbnail": "png", "image": "png"}

# Solution-specific configurations
SOLUTION_SORT_ATTRIBUTES = ["objective"]  # Fields for sorting solutions
SOLUTION_DISPLAY_FIELDS = ["objective", "authors"]  # Fields to display for solutions