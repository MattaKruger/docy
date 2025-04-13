from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

import logfire
from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Load
from sqlmodel import SQLModel, func, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

LoadOption = Load


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository implementing common CRUD operations for SQLModel models.
    This class provides generic database operations that can be used by all model repositories
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session
        self.model_name = self.model.__name__

    async def create(self, create_model: CreateSchemaType) -> ModelType:
        """Creates a new record in the database."""
        logfire.debug(f"Creating {self.model_name} instance")

        model_data = create_model.model_dump()
        db_obj = self.model(**model_data)

        self.session.add(db_obj)

        await self.session.commit()
        await self.session.refresh(db_obj)

        logfire.debug(f"Successfully created {self.model_name} with id {getattr(db_obj, 'id', None)}")
        return db_obj

    async def create_all(self, create_models: List[CreateSchemaType]):
        """Creates new records in the database."""
        logfire.debug(f"Creating {self.model_name} instances")

        for model in create_models:
            model = self.model(model.model_dump())

        self.session.add_all(create_models)
        await self.session.commit()

    async def get(self, id: Any, *, load_options: Optional[List[LoadOption]] = None) -> Optional[ModelType]:
        """
        Gets a single record by ID, optionally applying relationship loading strategies.

        Args:
            id: The primary key of the record to fetch.
            load_options: A list of SQLAlchemy loading options (e.g., [joinedload(Model.relationship)]).
        """
        logfire.debug(f"Getting {self.model_name} with id {id}, load_options={load_options}")

        statement = select(self.model).where(self.model.id == id)
        if load_options:
            statement = statement.options(*load_options)

        result = await self.session.execute(statement)

        instance = result.scalar_one_or_none()
        if instance:
            logfire.debug(f"Successfully retrieved {self.model_name} with id {id}")

        logfire.debug(f"{self.model_name} with id {id} found: {'Yes' if instance else 'No'}")
        return instance

    async def get_or_404(self, id: Any, *, load_options: Optional[List[LoadOption]] = None) -> ModelType:
        """
        Gets a single record by ID or raises HTTPException 404,
        optionally applying relationship loading strategies.

        Args:
            id: The primary key of the record to fetch.
            load_options: A list of SQLAlchemy loading options.
        """
        logfire.debug(f"Getting {self.model_name} with id {id} (or 404), load_options={load_options}")

        obj = await self.get(id, load_options=load_options)
        if obj is None:
            logfire.warning(f"{self.model_name} with id {id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model_name} with id {id} not found",
            )
        return obj

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        load_options: Optional[List[LoadOption]] = None,
    ) -> List[ModelType]:
        """
        Gets multiple records with optional filtering, skip, limit,
        and relationship loading strategies.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            filters: A dictionary of field-value pairs for filtering.
            load_options: A list of SQLAlchemy loading options.
        """
        logfire.debug(
            f"Getting multiple {self.model_name} with skip={skip}, limit={limit}, filters={filters}, load_options={load_options}"
        )
        statement = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
                else:
                    logfire.warning(f"Filter field '{field}' not found on model {self.model_name}")

        # Apply loading options *before* offset and limit
        if load_options:
            statement = statement.options(*load_options)

        statement = statement.offset(skip).limit(limit)
        result = await self.session.execute(statement)
        items = result.scalars().all()
        logfire.debug(f"Found {len(items)} {self.model_name} instances")

        return list(items)

    async def update(self, obj_in: UpdateSchemaType, db_obj: ModelType) -> Optional[ModelType]:
        """Updates an existing record by ID."""
        obj_id = getattr(db_obj, "id", "<unknown_id>")
        logfire.info(f"Updating {self.model_name} with id {obj_id}")

        update_data = obj_in.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        logfire.debug(f"Update data for {self.model_name} {obj_id}: {update_data}")

        self.session.add(db_obj)
        try:
            await self.session.commit()
        except Exception as e:
            logfire.error(f"Failed to update {self.model_name} {obj_id}: {e}")
            await self.session.rollback()
            return None

        await self.session.refresh(db_obj)
        logfire.debug(f"Successfully updated and refreshed {self.model_name} {obj_id}")
        return db_obj

    async def delete(self, id: Any) -> ModelType:
        """Deletes a record by ID."""
        logfire.debug(f"Deleting {self.model_name} with id {id}")
        db_obj = await self.get_or_404(id)

        await self.session.delete(db_obj)
        await self.session.commit()
        logfire.info(f"Successfully deleted {self.model_name} with id {id}")
        return db_obj

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Counts records with optional filtering."""
        logfire.debug(f"Counting {self.model_name} with filters={filters}")

        statement = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
                else:
                    logfire.warning(f"Filter field '{field}' not found on model {self.model_name} during count")

        result = await self.session.execute(statement)
        count = result.scalar_one()  # count should always return one row
        logfire.debug(f"Count result for {self.model_name}: {count}")

        return count

    async def _get_one_by_field(
        self, field_name: str, value: Any, *, load_options: Optional[List[LoadOption]] = None
    ) -> Optional[ModelType]:
        """
        Helper to get a single record by an arbitrary field, optionally applying
        relationship loading strategies.

        Returns None if no record is found. Logs an error and returns None
        if multiple records are found.
        Raises ValueError if the field_name does not exist on the model.

        Args:
            field_name: The name of the attribute/column to filter by.
            value: The value to match for the given field.
            load_options: A list of SQLAlchemy loading options.
        """
        logfire.debug(f"Getting one {self.model_name} by {field_name}={value}, load_options={load_options}")

        if not hasattr(self.model, field_name):
            logfire.error(f"Field '{field_name}' does not exist on model {self.model_name}")
            raise ValueError(f"Field '{field_name}' does not exist on model {self.model_name}")

        statement = select(self.model).where(getattr(self.model, field_name) == value)

        if load_options:
            statement = statement.options(*load_options)

        result = await self.session.execute(statement)
        try:
            instance = result.scalar_one_or_none()
            if instance:
                logfire.debug(f"Found one {self.model_name} for {field_name}={value}")
            else:
                logfire.debug(f"No {self.model_name} found for {field_name}={value}")
            return instance
        except MultipleResultsFound:
            logfire.error(
                f"Multiple results found unexpectedly for {self.model_name} with {field_name}={value}. Returning None."
            )
            return None
