from typing import Generic, List, Optional, Type, TypeVar, Dict, Any
from sqlmodel import SQLModel, Session, select, func
from fastapi import HTTPException, status

T = TypeVar("T", bound=SQLModel)
I = TypeVar("I", bound=SQLModel)
O = TypeVar("O", bound=SQLModel)


class BaseRepository(Generic[T, I, O]):
    """
    Base repository implementing common CRUD operations for SQLModel models.

    This class provides generic database operations that can be used by
    all model repositories, reducing code duplication and ensuring
    consistent implementation of data access patterns.
    """

    def __init__(self, model: Type[T], session: Session):
        """
        Initialize the repository with a model class and database session.

        Args:
            model: The SQLModel class this repository will operate on
            session: The SQLModel database session
        """
        self.model = model
        self.session = session

    async def create(self, create_model: I) -> T:
        """
        Create a new record in the database.

        Args:
            create_model: The model instance or dictionary of attributes for creation

        Returns:
            The created model instance with database-assigned values
        """
        db_obj = self.model(**create_model.dict())
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    async def get(self, id: Any) -> Optional[T]:
        """
        Retrieve a record by its ID.

        Args:
            id: The primary key value

        Returns:
            The model instance if found, None otherwise
        """
        return self.session.get(self.model, id)

    async def get_or_404(self, id: Any) -> T:
        """
        Retrieve a record by its ID or raise a 404 exception if not found.

        Args:
            id: The primary key value

        Returns:
            The model instance

        Raises:
            HTTPException: 404 error if record not found
        """
        obj = await self.get(id)
        if obj is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{self.model.__name__} with id {id} not found",
            )
        return obj

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[T]:
        """
        Retrieve multiple records with optional pagination and filtering.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            filters: Dictionary of field-value pairs to filter by

        Returns:
            List of model instances
        """
        statement = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    async def update(self, id: Any, update_model: O) -> Optional[T]:
        """
        Update an existing record.

        Args:
            id: The primary key value
            obj_in: Either a model instance or a dictionary of attributes to update

        Returns:
            The updated model instance or None if record not found
        """
        db_obj = await self.get(id)
        if db_obj is None:
            return None

        if isinstance(update_model, dict):
            update_data = update_model
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
        else:
            for field in self.model.__fields__:  # type: ignore
                if (
                    hasattr(update_model, field)
                    and getattr(update_model, field) is not None
                ):
                    setattr(db_obj, field, getattr(update_model, field))

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> Optional[T]:
        """
        Delete a record by its ID.

        Args:
            id: The primary key value

        Returns:
            The deleted model instance or None if record not found
        """
        db_obj = await self.get(id)
        if db_obj is None:
            return None

        self.session.delete(db_obj)
        self.session.commit()
        return db_obj

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records, optionally filtered.

        Args:
            filters: Dictionary of field-value pairs to filter by

        Returns:
            The count of matching records
        """
        statement = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        return self.session.exec(statement).one()
