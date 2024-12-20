from config import KnapsackInstance


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
