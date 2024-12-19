from pydantic import BaseModel, Field


from .instance_index import RangeQueryBounds


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
