from typing import Generic, List, Optional, Type, TypeVar, Dict, Any
from sqlmodel import SQLModel, Session, select, func
from fastapi import HTTPException, status


T = TypeVar("T", bound=SQLModel)
C = TypeVar("C", bound=SQLModel)
U = TypeVar("U", bound=SQLModel)


class BaseRepository(Generic[T, C, U]):
    """
    Base repository implementing common CRUD operations for SQLModel models.

    This class provides generic database operations that can be used by
    all model repositories
    """

    def __init__(self, model: Type[T], session: Session):
        self.model = model
        self.session = session

    async def create(self, create_model: C) -> T:
        db_obj = self.model(**create_model.model_dump())
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    async def get(self, id: Any) -> Optional[T]:
        return self.session.get(self.model, id)

    async def get_or_404(self, id: Any) -> T:
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
        statement = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        statement = statement.offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    async def update(self, id: Any, update_model: U) -> Optional[T]:
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
                if hasattr(update_model, field) and getattr(update_model, field) is not None:
                    setattr(db_obj, field, getattr(update_model, field))

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: Any) -> Optional[T]:
        db_obj = await self.get(id)
        if db_obj is None:
            return None

        self.session.delete(db_obj)
        self.session.commit()
        return db_obj

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        statement = select(func.count()).select_from(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)

        return self.session.exec(statement).one()
