from pydantic import BaseModel, Field
from sqlmodel import Session

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


def build_routes_for_problem(app: FastAPI, problem_info: ProblemInfo, instance_repository: InstanceRepository, instance_index: InstanceIndex, engine):
    def get_session():
        from sqlmodel import Session
        with Session(engine) as session:
            yield session
    router = APIRouter()
    InstanceModel = problem_info.instance_model
    asset_repository = AssetRepository(problem_info)

    @router.get("/instances/{instance_uid}")
    def get_instance(instance_uid: str) -> InstanceModel:
        try:
            return instance_repository.read_instance(instance_uid)
        except KeyError as ke:
            raise HTTPException(status_code=404, detail=str(ke))
    
    @router.get("/instance_info")
    def get_instance_infos(*, session: Session =Depends(get_session), query: instance_index.QuerySchema= Depends()) -> instance_index.PaginatedResponse:
        paginated_result = instance_index.query(query, session)
        return paginated_result
    
    @router.get("/instance_schema")
    def get_instance_schema() -> dict:
        return InstanceModel.model_json_schema()
    
    @router.get("/instance_info/{instance_uid}")
    def get_instance_info(instance_uid: str, session: Session = Depends(get_session)) -> instance_index.IndexTable:
        result = instance_index.get_instance_info(instance_uid, session)
        if result is None:
            raise HTTPException(status_code=404, detail="Instance not found")
        return result
    
    @router.get("/problem_info")
    def get_problem_info(*, session: Session = Depends(get_session)) -> ProblemInfoResponse:
        range_filters = instance_index.get_range_query_bounds(session)
        return ProblemInfoResponse(
            problem_uid=problem_info.problem_uid,
            range_filters=range_filters,
            boolean_filters=problem_info.boolean_filters,
            sort_fields=problem_info.sort_fields,
            display_fields=problem_info.display_fields,
            assets=problem_info.assets
        )
    
    def verify_api_key(api_key: str):
        if api_key != "your_api_key_here":
            raise HTTPException(status_code=403, detail="Invalid API Key")

    @router.post("/instances")
    def create_instance(instance: InstanceModel, session: Session = Depends(get_session), api_key: str = Depends(verify_api_key)):
        instance_repository.write_instance(instance)
        with Session(engine) as session:
            instance_index.index_instance(instance, session)

    @router.delete("/instances/{instance_uid}")
    def delete_instance(instance_uid: str, session: Session = Depends(get_session), api_key: str = Depends(verify_api_key)):
        instance_repository.delete_instance(instance_uid)
        instance_index.deindex_instance(instance_uid, session)
        asset_repository.delete_assets(instance_uid)

    @router.post("/assets/{asset_class}/{instance_uid}")
    def add_asset(asset_class: str, instance_uid: str, asset: bytes, api_key: str = Depends(verify_api_key)):
        asset_repository.add(asset_class, instance_uid, asset)

    app.include_router(router, prefix=f"/{problem_info.problem_uid}", tags=[problem_info.problem_uid])

