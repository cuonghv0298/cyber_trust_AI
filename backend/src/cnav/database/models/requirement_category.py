from cnav.database.models import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime,
    ForeignKey,
    Table,
    Enum,
    func
)
from sqlalchemy.orm import relationship

class RequirementCategory(Base):
    __tablename__ = "requirement_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationship to clauses
    # one-to-many relationship to Clause
    clauses = relationship("Clause", back_populates="category", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<RequirementCategory(id={self.id}, name='{self.name}')>"