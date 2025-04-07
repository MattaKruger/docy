from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Sequence

from sqlalchemy.orm import Load, joinedload
from sqlalchemy.engine.base import log
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, func, select

from fastapi import HTTPException, status
from pydantic import BaseModel

import logfire

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

# Define a type hint for loading options
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

        logfire.debug(f"Successfully created {self.model_name} with id {db_obj.id}")
        return db_obj

    async def get(self, id: Any, *, load_options: Optional[List[LoadOption]] = None) -> Optional[ModelType]:
        """
        Gets a single record by ID, optionally applying relationship loading strategies.

        Args:
            id: The primary key of the record to fetch.
            load_options: A list of SQLAlchemy loading options (e.g., [joinedload(Model.relationship)]).
        """
        logfire.debug(f"Getting {self.model_name} with id {id}, load_options={load_options}")

        statement = select(self.model).where(getattr(self.model, "id") == id)
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
    ) -> Sequence[ModelType]:  # Changed List to Sequence for better compatibility with scalars().all()
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
        print(items)
        logfire.debug(f"Found {len(items)} {self.model_name} instances")

        return list(items)

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Updates an existing record by ID."""
        # Note: Update doesn't typically need load_options, as the object is already loaded.
        # Refresh after commit will reload attributes, but relationships depend on session state or prior loading.
        obj_id = getattr(db_obj, "id", "<unknown_id>")  # Get id for logging if possible
        logfire.info(f"Updating {self.model_name} with id {obj_id}")
        update_data = obj_in.model_dump(exclude_unset=True)
        if not update_data:
            return db_obj  # No changes

        for field, value in update_data.items():
            setattr(db_obj, field, value)
        logfire.debug(f"Update data for {self.model_name} {obj_id}: {update_data}")

        self.session.add(db_obj)
        try:
            await self.session.commit()
        except Exception as e:
            logfire.error(f"Failed to update {self.model_name} {obj_id}: {e}")
            await self.session.rollback()
            # Consider re-raising or returning a specific error indicator
            return None  # Indicate failure

        await self.session.refresh(db_obj)
        logfire.debug(f"Successfully updated and refreshed {self.model_name} {obj_id}")
        return db_obj

    async def delete(self, id: Any) -> ModelType:
        """Deletes a record by ID."""
        # Note: Delete doesn't need load_options as we only need the object to delete it.
        logfire.debug(f"Deleting {self.model_name} with id {id}")
        # We call get_or_404 internally, which now supports load_options, but
        # we don't need them for delete itself, so we don't pass them here.
        db_obj = await self.get_or_404(id)

        await self.session.delete(db_obj)
        await self.session.commit()
        logfire.info(f"Successfully deleted {self.model_name} with id {id}")
        # Return the object that was deleted (now detached from session)
        return db_obj

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Counts records with optional filtering."""
        # Note: Count doesn't need load_options.
        logfire.debug(f"Counting {self.model_name} with filters={filters}")

        statement = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
                else:
                    logfire.warning(f"Filter field '{field}' not found on model {self.model_name} during count")

        result = await self.session.execute(statement)
        # Use scalar_one() which is appropriate for count aggregate
        count = result.scalar_one()  # count should always return one row
        # No need for none check here, count(*) returns 0 if no rows match
        logfire.debug(f"Count result for {self.model_name}: {count}")

        return count  # Directly return the count

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

        # Apply loading options
        if load_options:
            statement = statement.options(*load_options)

        result = await self.session.execute(statement)
        try:
            # Use scalar_one_or_none() for potentially zero or one result
            # Or use unique().scalar_one_or_none() if you expect strictly one or none
            instance = result.scalar_one_or_none()  # Allows zero or one result
            if instance:
                logfire.debug(f"Found one {self.model_name} for {field_name}={value}")
            else:
                logfire.debug(f"No {self.model_name} found for {field_name}={value}")
            return instance
        except MultipleResultsFound:
            # This shouldn't happen with scalar_one_or_none unless there's a DB constraint issue
            # or if the unique() variant was used and multiple results existed.
            # Keeping the log message for safety.
            logfire.error(
                f"Multiple results found unexpectedly for {self.model_name} with {field_name}={value}. Returning None."
            )
            return None
        # NoResultFound is handled by scalar_one_or_none returning None
