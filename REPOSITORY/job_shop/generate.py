from config import JobShopInstance

if __name__ == "__main__":

    def write_to_json_xz(data: JobShopInstance):
        # write to `./instances/{instance_uid}.json.xz`
        import lzma
        from pathlib import Path

        instance_uid = data.instance_uid
        path = Path(f"./instances/{instance_uid}.json.xz")
        path.parent.mkdir(parents=True, exist_ok=True)
        with lzma.open(path, "wt") as f:
            f.write(data.model_dump_json())

    # generate random instances for testing
    from random import randint, seed, sample
    from uuid import uuid4

    NUM_INSTANCES = 100
    for _ in range(NUM_INSTANCES):

        number_of_jobs = randint(3, 20)
        number_of_machines = randint(2, 10)
        '''
        Randomly picks the number of jobs (between 3 and 20).
        Randomly picks the number of machines (between 2 and 10).
        Can be changed later!
        '''
        time_seed = randint(0, 1_000_000)
        machine_seed = randint(0, 1_000_000)
        instance_uid = f"js_{number_of_jobs}x{number_of_machines}_{uuid4().hex[:8]}"
        
        # Generate times matrix
        seed(time_seed)
        times = [
            [randint(1, 20) for _ in range(number_of_machines)]
            for _ in range(number_of_jobs)
        ]

        # Generate machines matrix (each job gets a random permutation of all machines)
        seed(machine_seed)
        machines = [
            sample(range(number_of_machines), number_of_machines)
            for _ in range(number_of_jobs)
        ]

        # Very basic heuristics for bounds
        upper_bound = sum(max(row) for row in times) #Sum of the longest task in each job
        lower_bound = sum(min(row) for row in times) #Sum of the shortest task in each job

        instance = JobShopInstance(
            instance_uid=instance_uid,
            origin="synthetic",
            number_of_jobs=number_of_jobs,
            number_of_machines=number_of_machines,
            time_seed=time_seed,
            machine_seed=machine_seed,
            upper_bound=upper_bound,
            lower_bound=lower_bound,
            times=times,
            machines=machines,
        )

        write_to_json_xz(instance)
