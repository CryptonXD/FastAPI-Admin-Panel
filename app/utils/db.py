from typing import List, Optional, TypeVar, Generic, Type, Any, Dict, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


def get_by_id(db: Session, model: Type[ModelType], id: Any) -> Optional[ModelType]:
    """
    Get a database object by ID
    """
    return db.query(model).filter(model.id == id).first()


def get_multi(
    db: Session, model: Type[ModelType], *, skip: int = 0, limit: int = 100
) -> List[ModelType]:
    """
    Get multiple database objects
    """
    return db.query(model).offset(skip).limit(limit).all()


def create(
    db: Session, model: Type[ModelType], *, obj_in: Dict[str, Any] 
) -> ModelType:
    """
    Create a new database object
    """
    obj_in_data = obj_in
    db_obj = model(**obj_in_data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update(
    db: Session,
    model: Type[ModelType],
    *,
    db_obj: ModelType,
    obj_in: Union[Dict[str, Any], BaseModel]
) -> ModelType:
    """
    Update a database object
    """
    obj_data = jsonable_encoder(db_obj)
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in obj_data:
        if field in update_data:
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def remove(db: Session, model: Type[ModelType], *, id: int) -> ModelType:
    """
    Remove a database object
    """
    obj = db.query(model).get(id)
    db.delete(obj)
    db.commit()
    return obj
