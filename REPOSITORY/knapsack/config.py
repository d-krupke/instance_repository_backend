from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
    model_validator,
)


class KnapsackInstance(BaseModel):
    """Pydantic model representing a knapsack problem instance."""

    # Metadata
    instance_uid: str = Field(..., description="The unique identifier of the instance")
    origin: str = Field(default="", description="The origin or source of the instance")

    # Instance statistics
    num_items: PositiveInt = Field(
        ..., description="The number of items available in the instance"
    )
    weight_capacity_ratio: PositiveFloat = Field(
        ...,
        description=(
            "The ratio of the total weight of all items to the knapsack capacity. "
            "Calculated as the sum of item weights divided by knapsack capacity."
        ),
    )

    @staticmethod
    def calculate_weight_capacity_ratio(
        item_weights: list[NonNegativeFloat | NonNegativeInt],
        capacity: NonNegativeFloat | NonNegativeInt,
    ) -> PositiveFloat:
        """Calculate the weight to capacity ratio."""
        if capacity == 0:
            return float(
                "inf"
            )  # Avoid division by zero, return infinity if capacity is zero
        total_weight = sum(item_weights)
        return total_weight / capacity

    is_integral: bool = Field(
        default=False,
        description="Specifies if the capacity, values, and weights are integral. "
        "When set to True, all item values, weights, and the capacity must be integers, "
        "and validation will enforce this constraint. Defaults to False.",
    )

    # Instance data
    capacity: NonNegativeFloat | NonNegativeInt = Field(
        ..., description="The total capacity of the knapsack"
    )
    item_values: list[NonNegativeFloat | NonNegativeInt] = Field(
        ..., description="The values assigned to each item"
    )
    item_weights: list[NonNegativeFloat | NonNegativeInt] = Field(
        ..., description="The weights assigned to each item"
    )

    schema_version: int = Field(
        default=0,
        description="Schema version of the instance. If the schema changes, this will be incremented.",
    )

    # --------------------------------------------
    # Additional validation methods
    # --------------------------------------------

    @model_validator(mode="after")
    def validate_instance(self) -> "KnapsackInstance":
        if len(self.item_values) != self.num_items:
            raise ValueError(
                f"Expected {self.num_items} item values, got {len(self.item_values)}"
            )
        if len(self.item_weights) != self.num_items:
            raise ValueError(
                f"Expected {self.num_items} item weights, got {len(self.item_weights)}"
            )
        if self.is_integral:

            def check_integral(value):
                return isinstance(value, int) or (
                    isinstance(value, float) and value.is_integer()
                )

            if not all(
                check_integral(v)
                for v in self.item_values + self.item_weights + [self.capacity]
            ):
                raise ValueError(
                    "All item values, weights, and capacity must be integers when integral is True."
                )
        return self


class KnapsackSolution(BaseModel):
    """Pydantic model representing a solution to a knapsack problem instance."""

    # Solution metadata
    instance_uid: str = Field(
        ..., description="The unique identifier of the corresponding instance"
    )
    objective: NonNegativeFloat = Field(
        ..., description="The objective value of the solution (e.g., total value)"
    )
    authors: str = Field(..., description="The authors or contributors of the solution")

    # Solution data
    selected_items: list[int] = Field(
        ..., description="Indices of the selected items in the solution"
    )

    schema_version: int = Field(
        default=0,
        description="Schema version of the instance. If the schema changes, this will be incremented.",
    )


# Configuration constants for the knapsack problem

# Unique identifier for the problem
PROBLEM_UID = "knapsack"

# Shared attribute name for instances and solutions
INSTANCE_UID_ATTRIBUTE = "instance_uid"

# Schema definitions
INSTANCE_SCHEMA = KnapsackInstance
SOLUTION_SCHEMA = (
    KnapsackSolution  # Optional: Set to None if solutions are not supported
)

# Filtering and sorting configurations
RANGE_FILTERS = [
    "num_items",
    "weight_capacity_ratio",
]  # Fields usable for range filters
BOOLEAN_FILTERS = ["is_integral"]  # Boolean fields usable for filters
SORT_FIELDS = ["num_items", "weight_capacity_ratio"]  # Fields usable for sorting

# Fields for display purposes in instance overviews
DISPLAY_FIELDS = [
    "instance_uid",
    "num_items",
    "weight_capacity_ratio",
    "is_integral",
    "origin",
]

# Assets associated with the knapsack problem
ASSETS = {"thumbnail": "png", "image": "png"}

# Solution-specific configurations
SOLUTION_SORT_ATTRIBUTES = [
    "objective"
]  # Fields for sorting solutions. A "-" prefix indicates descending order.
SOLUTION_DISPLAY_FIELDS = ["objective", "authors"]  # Fields to display for solutions
