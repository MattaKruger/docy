from typing import Generic, List, Optional, Type, TypeVar, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, Session, select, func
from fastapi import HTTPException, status
from sqlalchemy.exc import NoResultFound, MultipleResultsFound


M = TypeVar("M", bound=SQLModel)
C = TypeVar("C", bound=SQLModel)
U = TypeVar("U", bound=SQLModel)


class BaseRepository(Generic[M, C, U]):
    """
    Base repository implementing common CRUD operations for SQLModel models.
    This class provides generic database operations that can be used by all model repositories
    """

    def __init__(self, model: Type[M], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, create_model: C) -> M:
        model_data = create_model.model_dump()
        db_obj = self.model(**model_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, id: Any) -> Optional[M]:
        """Gets a single record by ID"""
        return await self.session.get(self.model, id)

    async def get_or_404(self, id: Any) -> M:
        """Gets a single record by ID or raises HTTPException 404."""
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
    ) -> List[M]:
        """Gets multiple records with optional filtering, skip, and limit."""
        statement = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
                else:
                    print(f"Warning: Filter field '{field}' not found on {self.model.__str__}")
        statement = statement.offset(skip).limit(limit)
        result = await self.session.exec(statement)
        return list(result.all())

    async def update(self, id: Any, update_model: U) -> Optional[M]:
        db_obj = await self.get_or_404(id)

        update_data = update_model.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
            else:
                print(f"Warning: Field '{field}' in update data not found on model {self.model.__name__}")

        self.session.add(db_obj)  # Add modifies the existing object in the session
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> Optional[M]:
        """Deletes a record by ID"""
        db_obj = await self.get_or_404(id)

        await self.session.delete(db_obj)
        await self.session.commit()
        return db_obj

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Counts record with optional filtering"""
        statement = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        result = await self.session.exec(statement)
        count = result.one_or_none()
        return count if count is not None else 0

    async def _get_one_by_field(self, field_name: str, value: Any) -> Optional[M]:
        """Helper to get a single record by an arbitrary field."""
        if not hasattr(self.model, field_name):
            raise ValueError(f"Field '{field_name}' does not exist on model {self.model.__name__}")
        statement = select(self.model).where(getattr(self.model, field_name) == value)
        result = await self.session.exec(statement)
        try:
            return result.one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            print(f"Warning: Multiple results found for {field_name}={value} on {self.model.__name__}")
            return await self.session.exec(statement.limit(1)).first()
