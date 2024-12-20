# Instance Repository Backend

The goal of this project is to provide a simple and maintainable endpoint for
serving benchmark instances (and optionally solutions). There are two main
design goals:

1. The instance repository should be built upon a simple file structure that can
   be easily cloned from a git repository or FTP server. It must be easy to
   create a local archive of the repository or host it independently if we
   decide to no longer maintain a public server.
2. It should be trivial to add new problem classes without rewriting any code. A
   simple copy-and-paste configuration file that can be adapted to the new
   problem class should be sufficient.

A configuration for a problem consists of schemas for the instance and solution
files, as well as the attributes you want for the endpoint. The configuration is
a simple Python file with schemas defined using Pydantic v2. The decision to use
Pydantic is based on its popularity, ability to create fully documented and
easy-to-read schemas, and seamless integration with FastAPI, which provides
documented endpoints for free based on the schema descriptions.

A configuration file could look like this:

```python
from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
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
    integral: bool = Field(
        default=False,
        description="Specifies if the capacity, values, and weights are integral.",
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
BOOLEAN_FILTERS = ["integral"]  # Boolean fields usable for filters
SORT_FIELDS = ["num_items", "weight_capacity_ratio"]  # Fields usable for sorting

# Fields for display purposes in instance overviews
DISPLAY_FIELDS = [
    "instance_uid",
    "num_items",
    "weight_capacity_ratio",
    "integral",
    "origin",
]

# Assets associated with the knapsack problem
ASSETS = {"thumbnail": "png", "image": "png"}

# Solution-specific configurations
SOLUTION_SORT_ATTRIBUTES = [
    "objective"
]  # Fields for sorting solutions. A "-" prefix indicates descending order.
SOLUTION_DISPLAY_FIELDS = ["objective", "authors"]  # Fields to display for solutions
```
