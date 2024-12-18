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
    problem_uid: str = Field(..., title="The unique identifier of the problem")
    range_filters: list[RangeQueryBounds] = Field(
        default_factory=list,
        title="The fields that can be used to filter the instances with a range. The corresponding instance model should have a numerical type (int or float) field with the same name.",
    )
    boolean_filters: list[str] = Field(
        default_factory=list,
        title="Boolean fields that can be used to filter the instances. The corresponding instance model should have a boolean type field with the same name.",
    )
    sort_fields: list[str] = Field(
        default_factory=list,
        title="The fields that can be used to sort the instances",
    )
    display_fields: list[str] = Field(
        default_factory=list,
        title="The fields that should be displayed in an overview of the instances and, thus, must be quick to access.",
    )
    assets: dict[str, str] = Field(
        default_factory=dict,
        title="The asset classes and their extensions. The keys are the asset classes, and the values are the extensions, e.g., {'image': 'png'}.",
    )

class PaginatedRequest(BaseModel):
    offset: int = Field(default=0, title="The offset of the current page")
    limit: int = Field(default=100, title="The limit of the current page")


def build_routes_for_problem(
    app: FastAPI,
    problem_info: ProblemInfo,
    instance_repository: InstanceRepository,
    instance_index: InstanceIndex,
    solution_repository: SolutionRepository|None,
    solution_index: SolutionIndex|None,
    engine,
):
    def get_session():
        from sqlmodel import Session

        with Session(engine) as session:
            yield session

    router = APIRouter()
    InstanceModel: Type[BaseModel] = problem_info.instance_model
    QuerySchema: Type[BaseModel] = instance_index.QuerySchema
    asset_repository = AssetRepository(problem_info)

    @router.get("/instances/{instance_uid}", response_model=InstanceModel)
    def get_instance(instance_uid: str):
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
        paginated_result = instance_index.query(query, session)
        return paginated_result

    @router.get("/instance_schema")
    def get_instance_schema() -> dict:
        return InstanceModel.model_json_schema()

    @router.get(
        "/instance_info/{instance_uid}", response_model=instance_index.IndexTable
    )
    def get_instance_info(instance_uid: str, session: Session = Depends(get_session)):
        result = instance_index.get_instance_metadata(instance_uid, session)
        if result is None:
            raise HTTPException(status_code=404, detail="Instance not found")
        return result

    @router.get("/problem_info")
    def get_problem_info(
        *, session: Session = Depends(get_session)
    ) -> ProblemInfoResponse:
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
        if api_key != "your_api_key_here":
            raise HTTPException(status_code=403, detail="Invalid API Key")

    @router.post("/instances")
    def create_instance(
        instance: InstanceModel,
        session: Session = Depends(get_session),
        api_key: str = Depends(verify_api_key),
    ):
        instance_repository.write_instance(instance)
        with Session(engine) as session:
            instance_index.index_instance(instance, session)

    @router.delete("/instances/{instance_uid}")
    def delete_instance(
        instance_uid: str,
        session: Session = Depends(get_session),
        api_key: str = Depends(verify_api_key),
    ):
        instance_repository.delete_instance(instance_uid)
        instance_index.deindex_instance(instance_uid, session)
        asset_repository.delete_assets(instance_uid)

    @router.post("/assets/{asset_class}/{instance_uid}")
    def add_asset(
        asset_class: str,
        instance_uid: str,
        asset: bytes,
        api_key: str = Depends(verify_api_key),
    ):
        asset_repository.add(asset_class, instance_uid, asset)



    if solution_repository is not None:
        logging.info("Building routes for solutions")
        SolutionModel: Type[BaseModel] = problem_info.solution_model
        assert solution_index is not None, "The solution index should not be None"

        @router.get("/solutions/{solution_uid}", response_model=SolutionModel)
        def get_solution(solution_uid: str):
            try:
                return solution_repository.read_solution(solution_uid)
            except KeyError as ke:
                raise HTTPException(status_code=404, detail=str(ke))

        @router.get("/solution_info/{instance_uid}", response_model=solution_index.PaginatedResponse)
        def get_solution_info(instance_uid: str, request: PaginatedRequest=Depends() ,session: Session = Depends(get_session)):
            try:
                return solution_index.query(session, instance_uid, offset=request.offset, limit=request.limit)
            except KeyError as ke:
                raise HTTPException(status_code=404, detail=str(ke))

        @router.get("/solution_schema")
        def get_solution_schema() -> dict:
            return SolutionModel.model_json_schema()

        @router.post("/solutions")
        def create_solution(
            solution: SolutionModel,
            session: Session = Depends(get_session),
            api_key: str = Depends(verify_api_key),
        ):
            instance_uid = getattr(solution, problem_info.uid_attribute)
            if not instance_index.exists( instance_uid, session=session):
                raise HTTPException(status_code=404, detail="Instance not found")
            solution_uid, path = solution_repository.write_solution(solution)
            solution_index.index_solution(solution_uid=solution_uid,solution=solution, session=session)

        @router.delete("/solutions/{solution_uid}")
        def delete_solution(
            solution_uid: str,
            session: Session = Depends(get_session),
            api_key: str = Depends(verify_api_key),
        ):
            solution_repository.delete_solution(solution_uid)
            solution_index.deindex_solution(solution_uid, session)
    else:
        logging.info("No solution model found. Skipping the solution routes")

    app.include_router(
        router, prefix=f"/{problem_info.problem_uid}", tags=[problem_info.problem_uid]
    )
