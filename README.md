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

# Human-readable name and description of the problem
# This is optional but can help with generic UIs.
PROBLEM_NAME = "Knapsack Problem"
PROBLEM_DESCRIPTION = (
    "The Knapsack Problem involves selecting a subset of items "
    "to maximize total value without exceeding a given weight capacity. "
    "This configuration defines the structure of instances and solutions for the problem."
)

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
`docker-compose.dev.yml` file to fit your requirements, especially regarding
access keys.

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
- **`docker-compose.dev.yml`**: Defines the Docker services. You will likely
  need to edit this for your specific use case (e.g., environment variables,
  access keys, domain).
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
3. **Copy and adjust `docker-compose.dev.yml`** to suit your setup. By default,
   it’s configured for local use only. In particular, update the `environment`
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

> [!WARNING]
>
> You may want to deactivate that mechanism if you build a huge repository, as
> otherwise you could experience long startup times after restarts. We decided
> to implement this feature as a default to make it super easy to repair, in
> case something gets broken because you were to lazy to check the code of your
> student assistant properly (none of us have the time and students make
> mistakes...).

## Routes

The backend exposes several routes for managing instances and solutions.

- `GET /` will list all available problem classes. This is useful for
  discovering the available problems in the repository.
- `GET /{PROBLEM_UID}/instances/{INSTANCE_UID}`: Retrieve a specific instance
  for a problem by its UID.
- `GET /{PROBLEM_UID}/instance_info`: Query instance metadata with pagination
  and filtering support. Use `GET /{PROBLEM_UID}/problem_info` to automatically
  explore the available query parameters. You can also use the Swagger UI to do
  that. ![Swagger UI Screenshot](.assets/swagger_instance_info.png)
- `GET /{PROBLEM_UID}/instance_schema`: Return the JSON schema of the instance
  model.
- `GET /{PROBLEM_UID}/instance_info/{INSTANCE_UID}`: Retrieve metadata for a
  specific instance.
- `GET /{PROBLEM_UID}/problem_info`: Retrieve metadata about the problem,
  including filters and asset information.
  - This can look like this, and tells you which query parameters you can use in
    `GET /{PROBLEM_UID}/instance_info`, where range filters use the `__geq` and
    `__leq` suffixes (e.g., `weight_capacity_ratio__geq=0.1`) for minimum and
    maximum values, respectively, and boolean filters are simply added as query
    parameters:
  ```json
  {
    "problem_uid": "knapsack",
    "range_filters": [
      {
        "field_name": "num_items",
        "min_val": 11.0,
        "max_val": 1000.0,
        "problem_uid": "knapsack"
      },
      {
        "field_name": "weight_capacity_ratio",
        "min_val": 0.001174003923964717,
        "max_val": 0.9983667695638433,
        "problem_uid": "knapsack"
      }
    ],
    "boolean_filters": ["integral"],
    "sort_fields": ["num_items", "weight_capacity_ratio"],
    "display_fields": [
      "instance_uid",
      "num_items",
      "weight_capacity_ratio",
      "integral",
      "origin"
    ],
    "assets": { "thumbnail": "png", "image": "png" }
  }
  ```
- `POST /{PROBLEM_UID}/instances`: Create a new instance and index it for
  querying. This is protected by an API-Key, which needs to be provided in the
  request header as `api-key`.
- `DELETE /{PROBLEM_UID}/instances/{INSTANCE_UID}`: Delete a specific instance
  by its UID. This is protected by an API-Key, which needs to be provided in the
  request header as `api-key`.

### Assets

Instances can have associated assets (e.g., images or thumbnails). The backend
provides endpoints to manage these (optional) assets. Note that the assets will
be served by the nginx server, and these endpoints are just for managing the
assets or getting the asset paths.

- `POST /{PROBLEM_UID}/assets/{ASSET_CLASS}/{INSTANCE_UID}`: Upload an asset
  (e.g., image or thumbnail) for a specific instance. This is protected by an
  API-Key, which needs to be provided in the request.
- `GET /{PROBLEM_UID}/assets/{INSTANCE_UID}`: Retrieve all assets associated
  with a specific instance. The response includes the asset classes and their
  corresponding file paths.
- `DELETE /{PROBLEM_UID}/assets/{ASSET_CLASS}/{INSTANCE_UID}`: Delete a specific
  asset for an instance. This is protected by an API-Key, which needs to be
  provided in the request.

### Solutions (Optional)

If solutions are configured for a problem class, the backend provides endpoints
to manage solutions.

- `GET /{PROBLEM_UID}/solutions/{SOLUTION_UID}`: Retrieve a specific solution by
  its UID.
- `GET /{PROBLEM_UID}/solution_info/{INSTANCE_UID}`: Retrieve paginated solution
  metadata for a specific instance.
- `GET /{PROBLEM_UID}/solution_schema`: Retrieve the JSON schema of the solution
  model.
- `POST /{PROBLEM_UID}/solutions`: Enter a new solution for a specific instance.
  The solution must reference a valid instance UID. This is protected by an
  API-Key, which needs to be provided in the request header as `api-key`.
- `DELETE /{PROBLEM_UID}/solutions/{SOLUTION_UID}`: Delete a specific solution
  by its UID. This operation also removes the solution from the index. This is
  protected by an API-Key, which needs to be provided in the request header as
  `api-key`.

## Rules for UIDs

Unique identifiers (UIDs) are essential for maintaining consistency and avoiding
conflicts across the repository, ensuring smooth operation and data integrity.

- **Problem UIDs**: Must be unique across the entire repository. They can
  contain alphanumeric characters, underscores, and hyphens. E.g., it can be
  `knapsack`, `tsp`, or `my_problem_class`. Slashes are not allowed in problem
  UIDs because the repository organizes problems in a flat structure, ensuring
  simplicity and avoiding hierarchical complexities that could arise from nested
  paths.
- **Instance UIDs**: Must be unique within a problem class, but can be reused
  across different problem classes. They are allowed to contain alphanumeric
  characters, underscores, hyphens, and slashes. E.g., it can be
  `my_instance_1`, `my_instance-2`, or `my/instance/3`. The slash can be used to
  create a hierarchy, e.g., using the benchmark name as a prefix
  (`tsplib/a280`). Instance UIDs are not allowed to start or end with a slash.
- **Solution UIDs**: Will be automatically generated by the backend.

## Swagger UI

You can explore the API using the Swagger UI at
[http://127.0.0.1/docs](http://127.0.0.1/docs) using the example configuration.

![Swagger UI Screenshot](.assets/swagger.png)

## Example API Usage

Here is an example of how to use the API to upload a new instance and retrieve
it:

```python
import logging
from typing import Any
from requests import Session
from pydantic import BaseModel

# Configure root logger – adjust level as needed
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class Connector:
    """
    A simple example connector that logs all HTTP calls made, including the URL, parameters, payload, and responses.
    """

    def __init__(
        self,
        base_url: str,
        problem_uid: str,
        api_key: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.problem_uid = problem_uid
        self.session = Session()
        if api_key:
            # automatically include API key on all requests
            self.session.headers.update({"api-key": api_key})

    def _request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: Any = None,
        files: Any = None,
    ) -> dict[str, Any] | str:
        """
        Internal helper to perform an HTTP request and log details.
        """
        url = f"{self.base_url}/{self.problem_uid}{path}"
        logger.info("--> %s %s", method, url)
        if params:
            logger.info("    params=%s", params)
        if json is not None:
            logger.info("    json_payload=%s", json)
        if files:
            logger.info("    files=%s", files)

        response = self.session.request(
            method,
            url,
            params=params,
            json=json,
            files=files,
        )

        logger.info("<-- [%d] %s", response.status_code, response.url)
        text = response.text
        if len(text) > 500:
            logger.info("    response_text=%s... [truncated]", text[:500])
        else:
            logger.info("    response_text=%s", text)

        response.raise_for_status()
        try:
            return response.json()
        except ValueError:
            return text

    def get_instance_schema(self) -> dict[str, Any]:
        """Returns the schema for problem instances."""
        return self._request("GET", "/instance_schema")  # type: ignore

    def get_instance(self, instance_uid: str) -> dict[str, Any]:
        """Fetches a specific problem instance by its UID."""
        return self._request("GET", f"/instances/{instance_uid}")  # type: ignore

    def get_all_instance_info(
        self,
        offset: int = 0,
        limit: int = 100,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Fetches all problem instances."""
        merged: dict[str, Any] = {"offset": offset, "limit": limit}
        if params:
            merged |= params
        return self._request("GET", "/instance_info", params=merged)  # type: ignore

    def get_instance_info(self, instance_uid: str) -> dict[str, Any]:
        """Fetches information about a specific problem instance."""
        return self._request("GET", f"/instance_info/{instance_uid}")  # type: ignore

    def get_problem_info(self) -> dict[str, Any]:
        """Fetches information about the problem."""
        return self._request("GET", "/problem_info/")  # type: ignore

    def upload_instance(self, instance: BaseModel) -> dict[str, Any]:
        """Uploads a new problem instance."""
        payload = instance.model_dump(mode="json")
        return self._request("POST", "/instances", json=payload)  # type: ignore

    def delete_instance(self, instance_uid: str) -> dict[str, Any]:
        """Deletes a problem instance by its UID."""
        return self._request("DELETE", f"/instances/{instance_uid}")  # type: ignore

    # Assets
    def get_assets(self, instance_uid: str) -> dict[str, Any]:
        """Fetches all assets for a problem instance."""
        return self._request("GET", f"/assets/{instance_uid}")  # type: ignore

    def upload_asset(
        self,
        instance_uid: str,
        asset_class: str,
        asset_path: str,
    ) -> dict[str, Any]:
        """Uploads an asset for a problem instance."""
        with open(asset_path, "rb") as f:
            files_data = {"file": f}
            return self._request("POST", f"/assets/{asset_class}/{instance_uid}", files=files_data)  # type: ignore

    def delete_asset(self, instance_uid: str, asset_class: str) -> dict[str, Any]:
        """Deletes a specific asset for a problem instance."""
        return self._request("DELETE", f"/assets/{asset_class}/{instance_uid}")  # type: ignore

    # Solutions
    def get_solution_schema(self) -> dict[str, Any]:
        """Returns the schema for problem solutions."""
        return self._request("GET", "/solution_schema")  # type: ignore

    def get_solution_info(
        self,
        instance_uid: str,
        offset: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Fetches the solutions for a specific problem instance."""
        params = {"offset": offset, "limit": limit}
        return self._request("GET", f"/solution_info/{instance_uid}", params=params)  # type: ignore

    def upload_solution(self, solution: BaseModel) -> dict[str, Any]:
        """Uploads a new solution for a problem instance."""
        payload = solution.model_dump(mode="json")
        return self._request("POST", "/solutions", json=payload)  # type: ignore

    def get_solution(self, solution_uid: str) -> dict[str, Any]:
        """Fetches a specific solution by its UID."""
        return self._request("GET", f"/solutions/{solution_uid}")  # type: ignore

    def delete_solution(self, solution_uid: str) -> dict[str, Any]:
        """Deletes a specific solution for a problem instance."""
        return self._request("DELETE", f"/solutions/{solution_uid}")  # type: ignore


# For the local example configuration
connector = Connector(
    base_url="http://127.0.0.1", problem_uid=PROBLEM_UID, api_key="3456345-456-456"
)
```

See [./api_example.ipynb](./api_example.ipynb) for a more detailed example of
how to use the API with the above `Connector` class. You can freely copy and
modify this code, like everything else in this repository.

## Changelog

- 2025-05-26: Changed some parameters to follow some conventions, e.g.,
  `api_key` became `api-key` in the request header.
