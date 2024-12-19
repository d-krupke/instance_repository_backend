from pydantic import BaseModel, Field
import sqlmodel
import math


class PaginatedInstanceResponse(BaseModel):
    sorted_uids: list[str] = Field(
        ...,
        description="The sorted unique identifiers of the items in the current page",
    )
    data: dict[str, dict[str, int | str | float | None]] = Field(
        ..., description="The data of the items in the current page"
    )
    assets: dict[str, dict[str, str]] = Field(
        ..., description="The assets of the items in the current page"
    )
    offset: int = Field(..., description="The offset of the current page")
    limit: int = Field(..., description="The limit of the current page")
    total: int = Field(..., description="The total number of items")


class RangeQueryBounds(sqlmodel.SQLModel, table=True):
    """
    Saves the bounds for the range queries such that the interface
    can show some meaningful default values.
    """

    problem_uid: str = sqlmodel.Field(..., primary_key=True)
    field_name: str = sqlmodel.Field(..., primary_key=True)
    min_val: float | None = sqlmodel.Field(default=None)
    max_val: float | None = sqlmodel.Field(default=None)

    def update(self, val: float) -> bool:
        """
        Update the bounds based on the new value.
        """

        # don't do anything if it is not a number
        if not math.isfinite(val):
            return False

        if self.min_val is None or self.max_val is None:
            self.min_val = val
            self.max_val = val
            return True

        changed = False
        if val < self.min_val:
            self.min_val = val
            changed = True
        if val > self.max_val:
            self.max_val = val
            changed = True
        return changed


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
