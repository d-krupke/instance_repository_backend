import logging
import lzma
import math
from typing import Type
from pydantic import BaseModel, Field
from typing import Any, Dict, Type
import sqlmodel
from sqlmodel.main import SQLModelMetaclass

from .problem_info import ProblemInfo

class RangeQueryBounds(sqlmodel.SQLModel, table=True):
    """
    Saves the bounds for the range queries such that the interface
    can show some meaningful default values.
    """

    problem_uid: str = sqlmodel.Field(..., primary_key=True)
    field_name: str = sqlmodel.Field(..., primary_key=True)
    min_val: float|None = sqlmodel.Field(default=None)
    max_val: float|None = sqlmodel.Field(default=None)

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
    
class InstanceIndex:
    def __init__(self, problem_info: ProblemInfo):
        self.problem_info = problem_info
        self.IndexTable = self._generate_problem_instance_index_table(problem_info)
        self.QuerySchema = self._generate_query_schema(problem_info)
        self.PaginatedResponse = self._generate_paginated_response_model()

    def _generate_problem_instance_index_table(
        self,
        problem_info: ProblemInfo,
    ) -> Type[sqlmodel.SQLModel]:
        """
        Creates a SQLModel class that represents the index table for the instances of the problem.
        It is automatically generated based on the information provided in the problem_info parameter.
        """
        annotations = {}
        class_name = f"{problem_info.problem_uid}_instances"
        class_dict = {
            "__tablename__": class_name,
        }
        # create index field
        annotations[problem_info.uid_attribute] = (
            problem_info.instance_model.__annotations__[problem_info.uid_attribute]
        )
        class_dict[problem_info.uid_attribute] = sqlmodel.Field(
            ..., primary_key=True, description="The unique identifier of the instance"
        )
        logging.info(f"Added field '{problem_info.uid_attribute}' as primary key to the index table")
        # Create other fields
        for field_name in set(
            problem_info.range_filters
            + problem_info.boolean_filters
            + problem_info.sort_fields
            + problem_info.display_fields
        )-{problem_info.uid_attribute}:
            annotations[field_name] = problem_info.instance_model.__annotations__[
                field_name
            ]
            class_dict[field_name] = sqlmodel.Field(
                ...,
                description=problem_info.instance_model.model_fields[
                    field_name
                ].description,
            )
            logging.info(f"Added field '{field_name}' to the index table")
        class_dict["__annotations__"] = annotations  # type: ignore

        # Use the SQLModel metaclass to create the class and pass table=True
        model_class = SQLModelMetaclass(
            class_name, (sqlmodel.SQLModel,), class_dict, table=True
        )
        return model_class  # type: ignore
    
    def exists(self, instance_uid: str, session: sqlmodel.Session) -> bool:
        """
        Check if an instance with the given instance_uid exists.
        """
        return session.get(self.IndexTable, instance_uid) is not None
    
    def _generate_paginated_response_model(self) -> Type[BaseModel]:
        """
        Generate a response model for paginated responses.
        """
        class_name = f"{self.problem_info.problem_uid}_paginated_response"
        class_dict = {
            "items": Field(..., description="The items in the current page"),
            "offset": Field(..., description="The offset of the current page"),
            "limit": Field(..., description="The limit of the current page"),
            "total": Field(..., description="The total number of items"),
        }
        class_annotations = {
            "items": list[self.IndexTable],
            "offset": int,
            "limit": int,
            "total": int,
        }
        class_dict["__annotations__"] = class_annotations
        return type(class_name, (BaseModel,), class_dict)  # type: ignore

    
    def get_instance_metadata(self, instance_uid: str, session: sqlmodel.Session) -> sqlmodel.SQLModel|None:
        """
        Get the instance info from the index table.
        """
        return session.get(self.IndexTable, instance_uid)

    def _generate_query_schema(self, problem_info: ProblemInfo) -> Type[BaseModel]:
        """
        Generate a query model for the instances of the problem.
        This model can then be used to validate the query parameters of the API endpoint,
        as well as to automatically build the SQL query.
        """
        annotations = {}
        class_name = f"{problem_info.problem_uid}_query"
        class_dict = {}
        # Add the range filters
        for field_name in problem_info.range_filters:
            min_field_name = f"{field_name}{problem_info.postfix_query}{problem_info.postfix_query_geq}"
            class_dict[min_field_name] = Field(  # type: ignore
                default=None,
                description=problem_info.instance_model.model_fields[
                    field_name
                ].description,
            )
            annotations[min_field_name] = float|None
            max_field_name = f"{field_name}{problem_info.postfix_query}{problem_info.postfix_query_leq}"
            class_dict[max_field_name] = Field(  # type: ignore
                default=None,
                description=problem_info.instance_model.model_fields[
                    field_name
                ].description,
            )
            annotations[max_field_name] = float|None

        # Add the boolean filters
        for field_name in problem_info.boolean_filters:
            field_name_ = f"{field_name}{problem_info.postfix_query}"
            class_dict[field_name_] = Field(  # type: ignore
                default=None,
                description=problem_info.instance_model.model_fields[
                    field_name
                ].description,
            )
            annotations[field_name] = bool | None

        # Add the sort fields
        assert "sort_by" not in annotations, "`sort_by` is a reserved field name"
        annotations["sort_by"] = str | None
        class_dict["sort_by"] = Field(  # type: ignore
            None,
            description=f"The field to sort the instances by. Allowed values: {', '.join(problem_info.sort_fields)}, {', '.join(["-"+f for f in problem_info.sort_fields])}",
        )

        # Add the search field
        assert "search" not in annotations, "`search` is a reserved field name"
        class_dict["search"] = Field(  # type: ignore
            None, description="A keyword to search for in the instances"
        )
        annotations["search"] = str | None

        # pagination
        assert "offset" not in annotations, "`offset` is a reserved field name"
        class_dict["offset"] = Field(  # type: ignore
            0, description="The offset of the current page"
        )
        annotations["offset"] = int
        assert "limit" not in annotations, "`limit` is a reserved field name"
        class_dict["limit"] = Field(  # type: ignore
            100, description="The limit of the current page"
        )
        annotations["limit"] = int

        # Use the Pydantic BaseModel metaclass to create the class
        class_dict["__annotations__"] = annotations
        model_class = type(class_name, (BaseModel,), class_dict)
        return model_class

    def get_instance_info_from_data(
        self, instance_data: BaseModel
    ) -> sqlmodel.SQLModel:
        """
        Create an instance of the instance model from the data.
        """
        instance_info = self.IndexTable(**instance_data.model_dump())
        return instance_info

    def deindex_instance(self, instance_uid: str, session: sqlmodel.Session):
        """
        Remove the instance with the given instance_uid from the index.
        Note that the file is not deleted as it is not a responsibility of the index.
        """
        # Find the instance in the index table\
        instance_index = session.get(self.IndexTable, instance_uid)
        if instance_index:
            # Delete the instance from the index table
            session.delete(instance_index)
            session.commit()

    def index_instance(
        self, instance: BaseModel, session: sqlmodel.Session
    ) -> sqlmodel.SQLModel:
        """
        Index the instance with the given instance_uid.
        It will be in problem_info.path/instances/instance_uid.json.xz
        """
        instance_index = self.get_instance_info_from_data(instance)

        # Check if the instance already exists in the index
        existing_instance = session.get(
            self.IndexTable, getattr(instance, self.problem_info.uid_attribute)
        )
        if existing_instance:
            for key, value in instance_index.model_dump().items():
                if key != self.problem_info.uid_attribute:
                    setattr(existing_instance, key, value)
            session.refresh(existing_instance)
        else:
            session.add(instance_index)

        # update range query bounds
        for field_name in self.problem_info.range_filters:
            value = getattr(instance, field_name)
            bounds = session.get(
                RangeQueryBounds, (self.problem_info.problem_uid, field_name)
            )
            if bounds is None:
                bounds = RangeQueryBounds(
                    problem_uid=self.problem_info.problem_uid, field_name=field_name
                )
                session.add(bounds)
            if bounds.update(value):
                session.add(bounds)

        session.commit()
        return instance_index
    
    def get_instance_uids(self, session: sqlmodel.Session) -> list[str]:
        """
        Get the unique identifiers of all instances.
        """
        statement = sqlmodel.select(getattr(self.IndexTable, self.problem_info.uid_attribute))
        return list(session.exec(statement).all())
    

    def get_range_query_bounds(
        self, session: sqlmodel.Session
    ) -> list[RangeQueryBounds]:
        """
        Get the range query bounds for the problem.
        """
        statement = sqlmodel.select(RangeQueryBounds).where(
            RangeQueryBounds.problem_uid == self.problem_info.problem_uid
        )
        return list(session.exec(statement).all())

    def query(self, query_schema, session: sqlmodel.Session) -> Any:
        """
        Build a SQLAlchemy query based on the query_schema.
        """
        statement = sqlmodel.select(self.IndexTable)
        # Add the range filters
        for field_name in self.problem_info.range_filters:
            min_field_name = f"{field_name}{self.problem_info.postfix_query}{self.problem_info.postfix_query_geq}"
            max_field_name = f"{field_name}{self.problem_info.postfix_query}{self.problem_info.postfix_query_leq}"
            min_val = getattr(query_schema, min_field_name)
            max_val = getattr(query_schema, max_field_name)
            if min_val is not None:
                statement = statement.filter(getattr(self.IndexTable, field_name) >= min_val)
            if max_val is not None:
                statement = statement.filter(getattr(self.IndexTable, field_name) <= max_val)

        # Add the boolean filters
        for field_name in self.problem_info.boolean_filters:
            field_name_ = f"{field_name}{self.problem_info.postfix_query}"
            if getattr(query_schema, field_name_) is not None:
                statement = statement.filter(
                    getattr(self.IndexTable, field_name)
                    == getattr(query_schema, field_name_)
                )

        # Add the search field
        if query_schema.search is not None:
            statement = statement.filter(
                getattr(self.IndexTable, self.problem_info.uid_attribute).contains(query_schema.search)
            )

        # Add the sort field
        if query_schema.sort_by is not None:
            if query_schema.sort_by[0] == "-":
                field_name = query_schema.sort_by[1:]
                statement = statement.order_by(getattr(self.IndexTable, field_name).desc())
            else:
                statement = statement.order_by(getattr(self.IndexTable, query_schema.sort_by))

        # Add the pagination
        count_statement = sqlmodel.select(sqlmodel.func.count()).select_from(statement.alias())
        statement = statement.offset(query_schema.offset).limit(query_schema.limit)

        total = session.exec(count_statement).first()
        items = session.exec(statement).all()

        return self.PaginatedResponse(
            items=items, offset=query_schema.offset, limit=query_schema.limit, total=total
        )
