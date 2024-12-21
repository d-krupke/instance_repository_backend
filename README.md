# Instance Repository Backend

This project provides a simple, maintainable endpoint for serving benchmark
instances (and optionally solutions). It was designed with two main goals:

1. **Simplicity**: The instance repository is built upon a straightforward file
   structure that can be easily cloned from a Git repository or an FTP server.
   It should be trivial to create a local archive or host it independently, in
   case we ever discontinue the public server.
2. **Extensibility**: Adding a new problem class should require minimal effort.
   Ideally, you can simply copy an existing configuration file and adapt it to
   the new problem class without modifying any code.

## Features

The instance repository backend offers several key features to manage and
interact with benchmark instances:

- **Instance and Solution Management**: Easily upload, download, and delete
  instances and solutions.
- **Filtering and Sorting**: Filter instances by numerical or boolean
  attributes, and sort them by specific fields.
- **Asset Management**: Upload and download assets (e.g., images or thumbnails)
  associated with each instance.

While this repository provides the backend, the user interface is expected to be
served by a separate frontend (not included here). All necessary endpoints and
metadata are exposed, allowing you to build a simple JavaScript frontend that
can be hosted on a static web server. By dynamically exposing query parameters,
the backend helps keep the frontend in sync and facilitates reuse across
different problem classes.

Because research institutes often have changing teams, this system is designed
to be easy to maintain and extend—even for newcomers with minimal web
development experience. Should the institute discontinue the public server,
anyone can simply clone the repository and host the system independently with
minimal effort.

## Limitations

While this project aims to be lightweight, maintainable, and easily extensible,
it comes with a few important limitations:

- **Security**: It uses only basic access control via a single access key,
  making it unsuitable for scenarios where external users need to upload their
  own instances or solutions.
- **Scalability**: Designed primarily for read-only use with occasional updates,
  the system may struggle under heavy write loads or frequent modifications.
- **Performance**: The server is not optimized for high-traffic or large-scale
  deployments. It works best for small to medium-sized repositories within
  research institutes or small communities rather than large public platforms
  like Kaggle.
- **Flexibility**: Because the system relies on Pydantic and follows certain
  conventions (e.g., instance and solution UIDs), you may need to adapt your
  data or code if you plan to host repositories that deviate significantly from
  these models.

## Configuring a New Problem Class

A configuration for a problem class consists of schemas for instance and
solution files, as well as various endpoint attributes. Configurations are
written as simple Python files, using **Pydantic v2**. We chose Pydantic for its
popularity, readability, and tight integration with FastAPI, which automatically
generates documented endpoints based on the schema definitions.

Below is an example configuration file for a knapsack problem:

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
            "Calculated as the sum of item weights divided by the knapsack capacity."
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
    # NOTE: For more complex instances, you can use a hierarchy of models.
    # Just specify the root model below in the INSTANCE_SCHEMA variable.


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
SOLUTION_SCHEMA = KnapsackSolution  # Set to None if solutions are not supported

# Filtering and sorting configurations
RANGE_FILTERS = [
    "num_items",
    "weight_capacity_ratio",
]  # Fields usable for range filters
BOOLEAN_FILTERS = ["integral"]  # Boolean fields usable for filters
SORT_FIELDS = ["num_items", "weight_capacity_ratio"]  # Fields usable for sorting

# Fields for display in instance overviews
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
]  # Fields for sorting solutions; a "-" prefix indicates descending order.
SOLUTION_DISPLAY_FIELDS = ["objective", "authors"]  # Fields to display for solutions
```

## Getting Started

You can start the instance repository backend using Docker:

```bash
docker compose up --build
```

Once the containers are running, open the Swagger UI at
[http://127.0.0.1/docs](http://127.0.0.1/docs) to explore and interact with the
API.

You can also directly browse the repository at
[http://127.0.0.1/static/](http://127.0.0.1/static/). Adapt the
`docker-compose.yml` file to fit your requirements, especially regarding access
keys.

To test the setup, both example problems in this repository include a
`generate.py` script that generates random instances.

## Project Structure

The project is organized as follows:

- **`server/`**: Contains the FastAPI server implementation. You generally do
  **not** need to modify this directory.
- **`REPOSITORY/`**: Contains configuration files and data for the instance
  repository. This directory is mapped directly into the server, so you can
  maintain it via a separate Git repository if desired.
- **`.dockerignore`**: Lists files to ignore when building the Docker image.
- **`.gitignore`**: Lists files to ignore when committing to the Git repository.
- **`.pre-commit-config.yaml`**: Configuration for pre-commit hooks, helping to
  maintain code quality.
- **`docker-compose.yml`**: Defines the Docker services. You will likely need to
  edit this for your specific use case (e.g., environment variables, access
  keys, domain).
- **`Dockerfile`**: Builds the FastAPI server.
- **`entrypoint.py`**: Entrypoint script for the Docker container. It indexes
  all instances and solutions on startup before running the FastAPI server.
- **`LICENSE`**: MIT License.
- **`nginx.conf`**: Configuration for the Nginx server. Edit as needed,
  especially if you plan to enable HTTPS.
- **`README.md`**: This file.
- **`requirements.txt`**: Python requirements for the FastAPI server.

## Setting Up Your Own Instance Repository

1. **Clone this repository**.
2. **Adapt the `REPOSITORY/` directory** to your needs. You can base your work
   on one of the example problem configurations and remove the ones you don’t
   need.
3. **Adjust `docker-compose.yml`** to suit your setup. By default, it’s
   configured for local use only. In particular, update the `environment`
   section:
   - Change the access key to a secure value. This project provides only a very
     basic access key mechanism.
   - Change the URL to your domain if you plan to deploy publicly.
4. **Update `nginx.conf`**. This file is crucial for configuring HTTPS. If you
   only need read-only access and don’t mind using HTTP, you can theoretically
   skip HTTPS—but note that sending an access key over HTTP is insecure.
5. **Start the server** by running:

   ```bash
   docker compose up --build
   ```

## If the Index Gets Corrupted

If the index becomes corrupted, you can reset the database. Upon startup, the
system automatically rebuilds the index from the repository:

1. Identify the database volume with:
   ```bash
   docker volume list
   ```
2. Remove the volume with:
   ```bash
   docker volume rm VOLUME_NAME
   ```
3. If necessary, remove the PostgreSQL container first:
   ```bash
   docker container list
   docker container rm CONTAINER_NAME
   ```

After removing the corrupted volume, restart the services to rebuild the index.
