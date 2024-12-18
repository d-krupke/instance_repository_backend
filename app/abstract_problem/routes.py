import logging
from typing import Type
from pydantic import BaseModel, Field
from sqlmodel import Session

from .solution_index import SolutionIndex
from .solution_repository import SolutionRepository

from .asset_repository import AssetRepository
from .problem_info import ProblemInfo
from .instance_index import InstanceIndex, RangeQueryBounds
from .instance_repository import InstanceRepository
from fastapi import APIRouter, Depends, FastAPI, HTTPException


class ProblemInfoResponse(BaseModel):
    """
    Response model for providing metadata about a problem.
    Includes filterable fields, sortable fields, display fields, and asset information.
    """

    problem_uid: str = Field(..., title="The unique identifier of the problem")
    range_filters: list[RangeQueryBounds] = Field(
        default_factory=list,
        title="Range fields that can filter instances with numeric values.",
    )
    boolean_filters: list[str] = Field(
        default_factory=list, title="Boolean fields for filtering instances."
    )
    sort_fields: list[str] = Field(
        default_factory=list, title="Fields used for sorting instances."
    )
    display_fields: list[str] = Field(
        default_factory=list, title="Fields displayed in instance overviews."
    )
    assets: dict[str, str] = Field(
        default_factory=dict,
        title="Asset classes and their extensions (e.g., {'image': 'png'}).",
    )


class PaginatedRequest(BaseModel):
    """
    Request model for paginated queries.
    """

    offset: int = Field(default=0, title="Offset for pagination")
    limit: int = Field(default=100, title="Limit for pagination")


class BatchedAssetsRequest(BaseModel):
    """
    Request model for querying assets for multiple instances.
    """

    instance_uids: list[str] = Field(..., title="Unique identifiers of instances")


def build_routes_for_problem(
    app: FastAPI,
    problem_info: ProblemInfo,
    instance_repository: InstanceRepository,
    instance_index: InstanceIndex,
    solution_repository: SolutionRepository | None,
    solution_index: SolutionIndex | None,
    engine,
):
    """
    Build API routes for a specific problem.

    Routes include:
    - CRUD operations for instances.
    - Metadata endpoints for instance filtering and schema.
    - Asset management endpoints.
    - Optional solution-specific routes if a solution repository is provided.
    """

    def get_session():
        """
        Dependency for obtaining a database session.
        """
        from sqlmodel import Session

        with Session(engine) as session:
            yield session

    router = APIRouter()
    InstanceModel: Type[BaseModel] = problem_info.instance_model
    QuerySchema: Type[BaseModel] = instance_index.QuerySchema
    asset_repository = AssetRepository(problem_info)

    @router.get("/instances/{instance_uid}", response_model=InstanceModel)
    def get_instance(instance_uid: str):
        """
        Retrieve a specific instance by its UID.
        """
        try:
            return instance_repository.read_instance(instance_uid)
        except KeyError as ke:
            raise HTTPException(status_code=404, detail=str(ke))

    @router.get("/instance_info", response_model=instance_index.PaginatedResponse)
    def get_instance_infos(
        *,
        session: Session = Depends(get_session),
        query: QuerySchema = Depends(),
    ):
        """
        Query instance metadata with pagination and filtering support.
        """
        return instance_index.query(query, session)

    @router.get("/instance_schema")
    def get_instance_schema() -> dict:
        """
        Return the JSON schema of the instance model.
        """
        return InstanceModel.model_json_schema()

    @router.get(
        "/instance_info/{instance_uid}", response_model=instance_index.IndexTable
    )
    def get_instance_info(instance_uid: str, session: Session = Depends(get_session)):
        """
        Retrieve metadata for a specific instance by UID.
        """
        result = instance_index.get_instance_metadata(instance_uid, session)
        if result is None:
            raise HTTPException(status_code=404, detail="Instance not found")
        return result

    @router.get("/problem_info")
    def get_problem_info(
        *, session: Session = Depends(get_session)
    ) -> ProblemInfoResponse:
        """
        Retrieve metadata about the problem, including filters and asset information.
        """
        range_filters = instance_index.get_range_query_bounds(session)
        return ProblemInfoResponse(
            problem_uid=problem_info.problem_uid,
            range_filters=range_filters,
            boolean_filters=problem_info.boolean_filters,
            sort_fields=problem_info.sort_fields,
            display_fields=problem_info.display_fields,
            assets=problem_info.assets,
        )

    def verify_api_key(api_key: str):
        """
        Verify the provided API key. Raise an error if invalid.
        """
        if api_key != "your_api_key_here":
            raise HTTPException(status_code=403, detail="Invalid API Key")

    @router.post("/instances")
    def create_instance(
        instance: InstanceModel,
        session: Session = Depends(get_session),
        api_key: str = Depends(verify_api_key),
    ):
        """
        Create a new instance and index it for querying.
        """
        instance_repository.write_instance(instance)
        with Session(engine) as session:
            instance_index.index_instance(instance, session)

    @router.delete("/instances/{instance_uid}")
    def delete_instance(
        instance_uid: str,
        session: Session = Depends(get_session),
        api_key: str = Depends(verify_api_key),
    ):
        """
        Delete an instance and its associated data from indices and assets.
        Will also delete associated solutions if a solution repository is available.
        """
        instance_repository.delete_instance(instance_uid)
        instance_index.deindex_instance(instance_uid, session)
        asset_repository.delete_assets(instance_uid)
        if solution_index is not None:
            solution_index.deindex_solutions_for_instance(instance_uid, session)
        if solution_repository is not None:
            for solution_uid in solution_repository.list_solution_uids_of_instance(
                instance_uid
            ):
                solution_repository.delete_solution(solution_uid)

    @router.post("/assets/{asset_class}/{instance_uid}")
    def add_asset(
        asset_class: str,
        instance_uid: str,
        asset: bytes,
        api_key: str = Depends(verify_api_key),
    ):
        """
        Add an asset for a specific instance.

        Parameters:
        - asset_class: The type of asset (e.g., 'image', 'thumbnail').
        - instance_uid: The unique identifier of the instance.
        - asset: The binary content of the asset to store.
        """
        asset_repository.add(asset_class, instance_uid, asset)

    @router.get("/assets/{instance_uid}", response_model=dict[str, str])
    def get_assets(instance_uid: str):
        """
        Retrieve all assets associated with a specific instance.

        The keys in the response represent asset classes, and the values represent the corresponding file paths.
        """
        available = asset_repository.available_assets_for_instance(instance_uid)
        return {
            asset_class: f"{problem_info.assets_url_root}{path}"
            for asset_class, path in available.items()
        }

    @router.delete("/assets/{asset_class}/{instance_uid}")
    def delete_assets(
        asset_class: str,
        instance_uid: str,
        api_key: str = Depends(verify_api_key),
    ):
        """
        Delete a specific asset for an instance.

        Example:
        To delete a thumbnail for an instance:
        /assets/thumbnail/instance123
        """
        asset_repository.delete_assets(instance_uid, asset_class=asset_class)

    @router.get("/assets", response_model=dict[str, dict[str, str]])
    def get_all_assets(request: BatchedAssetsRequest):
        """
        Retrieve all assets for a batch of instances.

        The response is a dictionary where keys are instance UIDs, and values are dictionaries
        mapping asset classes to their file paths.
        """
        result = {}
        for instance_uid in request.instance_uids:
            available = asset_repository.available_assets_for_instance(instance_uid)
            result[instance_uid] = {
                asset_class: f"{problem_info.assets_url_root}{path}"
                for asset_class, path in available.items()
            }
        return result

    if solution_repository is not None:
        logging.info("Building routes for solutions")
        SolutionModel: Type[BaseModel] = problem_info.solution_model
        assert solution_index is not None, "The solution index should not be None"

        @router.get("/solutions/{solution_uid}", response_model=SolutionModel)
        def get_solution(solution_uid: str):
            """
            Retrieve a specific solution by its UID.
            """
            try:
                return solution_repository.read_solution(solution_uid)
            except KeyError as ke:
                raise HTTPException(status_code=404, detail=str(ke))

        @router.get(
            "/solution_info/{instance_uid}",
            response_model=solution_index.PaginatedResponse,
        )
        def get_solution_info(
            instance_uid: str,
            request: PaginatedRequest = Depends(),
            session: Session = Depends(get_session),
        ):
            """
            Retrieve paginated solution metadata for a specific instance.

            Parameters:
            - instance_uid: The unique identifier of the instance.
            - request: Pagination parameters (offset and limit).
            """
            try:
                return solution_index.query(
                    session, instance_uid, offset=request.offset, limit=request.limit
                )
            except KeyError as ke:
                raise HTTPException(status_code=404, detail=str(ke))

        @router.get("/solution_schema")
        def get_solution_schema() -> dict:
            """
            Retrieve the JSON schema of the solution model.
            """
            return SolutionModel.model_json_schema()

        @router.post("/solutions")
        def create_solution(
            solution: SolutionModel,
            session: Session = Depends(get_session),
            api_key: str = Depends(verify_api_key),
        ):
            """
            Enter a new solution for a specific instance.

            The solution must reference to a valid instance UID.
            """
            instance_uid = getattr(solution, problem_info.uid_attribute)
            if not instance_index.exists(instance_uid, session=session):
                raise HTTPException(status_code=404, detail="Instance not found")
            solution_uid, path = solution_repository.write_solution(solution)
            solution_index.index_solution(
                solution_uid=solution_uid, solution=solution, session=session
            )

        @router.delete("/solutions/{solution_uid}")
        def delete_solution(
            solution_uid: str,
            session: Session = Depends(get_session),
            api_key: str = Depends(verify_api_key),
        ):
            """
            Delete a specific solution by its UID.

            This operation also removes the solution from the index.
            """
            solution_repository.delete_solution(solution_uid)
            solution_index.deindex_solution(solution_uid, session)

    else:
        logging.info("No solution model found. Skipping the solution routes")

    app.include_router(
        router,
        prefix=f"/{problem_info.problem_uid}",
        tags=[problem_info.problem_uid],
    )
