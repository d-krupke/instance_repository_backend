from pydantic import (
    BaseModel,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveFloat,
    PositiveInt,
)


class KnapsackInstance(BaseModel):
    # Meta data
    instance_uid: str = Field(..., description="The unique identifier of the instance")
    origin: str = Field(default="", description="The origin of the instance")

    # stats
    num_items: PositiveInt = Field(
        ..., description="The number of items in the instance"
    )
    weight_capacity_ratio: PositiveFloat = Field(
        ...,
        description="The ratio of the total weight of the items to the capacity of the knapsack. It is the sum of the weights of the items divided by the capacity of the knapsack.",
    )
    integral: bool = Field(
        default=False,
        description="Whether the capacity, values, and weights are integral.",
    )

    # instance data
    capacity: NonNegativeFloat | NonNegativeInt = Field(
        ..., description="The capacity of the knapsack"
    )
    item_values: list[NonNegativeFloat] | list[NonNegativeInt] = Field(
        ..., description="The values of the items"
    )
    item_weights: list[NonNegativeFloat] | list[NonNegativeInt] = Field(
        ..., description="The weights of the items"
    )


class KnapsackSolution(BaseModel):
    instance_uid: str = Field(..., description="The unique identifier of the instance")
    objective: NonNegativeFloat = Field(
        ..., description="The objective value of the solution"
    )
    authors: str = Field(..., description="The authors of the solution")

    selected_items: list[int] = Field(..., description="The selected items")


# A unique identifier for the problem. It will be used for the URL of the API endpoint as well as for the storage of the instances
PROBLEM_UID = "knapsack"
# This attribute has to be the same for instances and solutions.
INSTANCE_UID_ATTRIBUTE = "instance_uid"
# The Pydantic model of the instance
INSTANCE_SCHEMA = KnapsackInstance
SOLUTION_SCHEMA = KnapsackSolution
# The fields that can be used to filter the instances with a range, i.e., numerical fields
RANGE_FILTERS = ["num_items", "weight_capacity_ratio"]
# Boolean fields that can be used to filter the instances
BOOLEAN_FILTERS = ["integral"]
# The fields that can be used to sort the instances
SORT_FIELDS = ["num_items", "weight_capacity_ratio"]
# The fields that should be displayed in an overview of the instances
DISPLAY_FIELDS = [
    "instance_uid",
    "num_items",
    "weight_capacity_ratio",
    "integral",
    "origin",
]
ASSETS = {"thumbnail": "png", "image": "png"}
# Add a `-` in front in case the field should be sorted in descending order
SOLUTION_SORT_ATTRIBUTES = ["objective"]
SOLUTION_DISPLAY_FIELDS = ["objective", "authors"]

if __name__ == "__main__":

    def write_to_json_xz(data: KnapsackInstance):
        # write to `./instances/{instance_uid}.json.xz`
        import lzma
        from pathlib import Path

        instance_uid = data.instance_uid
        path = Path(f"./instances/{instance_uid}.json.xz")
        path.parent.mkdir(parents=True, exist_ok=True)
        with lzma.open(path, "wt") as f:
            f.write(data.model_dump_json())

    # generate random instances for testing
    from random import randint, random
    from uuid import uuid4

    instances = []
    for _ in range(100):
        num_items = randint(10, 1000)
        weight_capacity_ratio = random()
        integral = random() < 0.5
        capacity = random() * 100
        item_values = [random() * 100 for _ in range(num_items)]
        item_weights = [random() * 100 for _ in range(num_items)]
        if integral:
            item_values = [round(v) for v in item_values]
            item_weights = [round(w) for w in item_weights]
            capacity = round(capacity)
        instance = KnapsackInstance(
            instance_uid=str(uuid4()),
            num_items=num_items,
            weight_capacity_ratio=weight_capacity_ratio,
            integral=integral,
            capacity=capacity,
            item_values=item_values,
            item_weights=item_weights,
        )
        write_to_json_xz(instance)
