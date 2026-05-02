from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: Session):
        self.model = model
        self.db_session = db_session

    def create(self, **kwargs) -> ModelType:
        db_obj = self.model(**kwargs)
        self.db_session.add(db_obj)
        self.db_session.commit()
        self.db_session.refresh(db_obj)
        return db_obj

    def get_by_id(self, obj_id: int) -> Optional[ModelType]:
        return self.db_session.query(self.model).filter(self.model.id == obj_id).first()

    def get_by_workspace(self, workspace_id: int, **filters) -> List[ModelType]:
        query = self.db_session.query(self.model).filter(
            self.model.workspace_id == workspace_id
        )
        if filters:
            query = query.filter_by(**filters)
        return query.all()

    def get_multi(self, **filters) -> List[ModelType]:
        query = self.db_session.query(self.model)
        if filters:
            query = query.filter_by(**filters)
        return query.all()

    def update(self, obj_id: int, **kwargs) -> Optional[ModelType]:
        db_obj = self.get_by_id(obj_id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            self.db_session.commit()
            self.db_session.refresh(db_obj)
        return db_obj

    def delete(self, obj_id: int) -> bool:
        db_obj = self.get_by_id(obj_id)
        if db_obj:
            self.db_session.delete(db_obj)
            self.db_session.commit()
            return True
        return False

    def get_by_field(self, field_name: str, value: any) -> Optional[ModelType]:
        field = getattr(self.model, field_name)
        return self.db_session.query(self.model).filter(field == value).first()
