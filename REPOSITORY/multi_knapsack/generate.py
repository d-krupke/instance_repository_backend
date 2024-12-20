from config import MultiKnapsackInstance


if __name__ == "__main__":

    def write_to_json_xz(data: MultiKnapsackInstance):
        # Write to `./instances/{instance_uid}.json.xz`
        import lzma
        from pathlib import Path

        instance_uid = data.instance_uid
        path = Path(f"./instances/{instance_uid}.json.xz")
        path.parent.mkdir(parents=True, exist_ok=True)
        with lzma.open(path, "wt") as f:
            f.write(data.model_dump_json())

    # Generate random instances for testing
    from random import randint, random
    from uuid import uuid4

    instances = []
    for _ in range(100):
        # Randomize instance parameters
        num_items = randint(10, 1000)
        num_knapsacks = randint(2, 10)
        weight_capacity_ratio = random()
        integral = random() < 0.5

        # Generate knapsack capacities
        capacities = [random() * 100 for _ in range(num_knapsacks)]

        # Generate item values and weights
        item_values = [random() * 100 for _ in range(num_items)]
        item_weights = [random() * 100 for _ in range(num_items)]

        # Ensure integral values if required
        if integral:
            capacities = [round(cap) for cap in capacities]
            item_values = [round(v) for v in item_values]
            item_weights = [round(w) for w in item_weights]

        # Calculate weight_capacity_ratio as total weights / total capacities
        total_capacity = sum(capacities)
        total_weight = sum(item_weights)
        weight_capacity_ratio = (
            total_weight / total_capacity if total_capacity > 0 else 0
        )

        # Create instance
        instance = MultiKnapsackInstance(
            instance_uid=str(uuid4()),
            num_items=num_items,
            num_knapsacks=num_knapsacks,
            weight_capacity_ratio=weight_capacity_ratio,
            integral=integral,
            capacities=capacities,
            item_values=item_values,
            item_weights=item_weights,
        )

        # Write instance to JSON.xz file
        write_to_json_xz(instance)
