from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, List, Optional, Any, Dict, Union
from app.models.base import BaseModel
from sqlalchemy.exc import SQLAlchemyError
import logging

T = TypeVar('T', bound=BaseModel)
logger = logging.getLogger(__name__)

class BaseRepository(Generic[T]):
    """Generic repository for database operations"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Get entity by its ID"""
        return self.db.query(self.model).filter(self.model.id == entity_id).first()
    
    def get_all(self) -> List[T]:
        """Get all entities"""
        return self.db.query(self.model).all()
    
    def create(self, **kwargs) -> T:
        """Create a new entity"""
        try:
            entity = self.model(**kwargs)
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise
    
    def update(self, entity_id: int, **kwargs) -> Optional[T]:
        """Update an entity by its ID"""
        try:
            entity = self.get_by_id(entity_id)
            if entity:
                for key, value in kwargs.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                self.db.commit()
                self.db.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating {self.model.__name__} with ID {entity_id}: {e}")
            raise
    
    def delete(self, entity_id: int) -> bool:
        """Delete an entity by its ID"""
        try:
            entity = self.get_by_id(entity_id)
            if entity:
                self.db.delete(entity)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting {self.model.__name__} with ID {entity_id}: {e}")
            raise
    
    def filter_by(self, **kwargs) -> List[T]:
        """Find entities by specified criteria"""
        return self.db.query(self.model).filter_by(**kwargs).all()
    
    def get_one_by(self, **kwargs) -> Optional[T]:
        """Get one entity by specified criteria"""
        return self.db.query(self.model).filter_by(**kwargs).first()
    
    def count(self) -> int:
        """Count all entities"""
        return self.db.query(self.model).count()
    
    # Transaction management methods
    def begin_transaction(self) -> None:
        """Begin a nested transaction (savepoint)"""
        self.db.begin_nested()
    
    def commit(self) -> None:
        """Commit the current transaction"""
        self.db.commit()
    
    def rollback(self) -> None:
        """Rollback the current transaction"""
        self.db.rollback()
    
    def refresh(self, entity: T) -> None:
        """Refresh an entity from the database"""
        self.db.refresh(entity)
