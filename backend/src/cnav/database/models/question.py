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
import enum

# Association table for many-to-many relationship between questions and clauses
question_clause_association = Table(
    'question_clause_mapping',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('clause_id', Integer, ForeignKey('clauses.id'), primary_key=True),
)

class AudienceType(enum.Enum):
    """Enum for audience types"""
    HR = "HR"
    IT = "IT"
    OWNER = "Owner"

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    
    # Audience field as enum
    audience = Column(Enum(AudienceType), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Many-to-many relationship with clauses
    clauses = relationship(
        "Clause",
        secondary=question_clause_association,
        back_populates="questions"
    )
    
    # One-to-many relationship with self assessment answers
    self_assessment_answers = relationship("SelfAssessmentAnswer", back_populates="question")
    
    # One-to-many relationship with question evaluations
    question_evaluations = relationship("QuestionEvaluation", back_populates="question")
    
    def __repr__(self):
        return f"<Question(id={self.id}, audience='{self.audience.value}', name='{self.name}')>"
    
    @classmethod
    def get_by_audience(cls, session, audience_type):
        """Get all questions for a specific audience type"""
        if isinstance(audience_type, str):
            audience_type = AudienceType(audience_type)
        return session.query(cls).filter(cls.audience == audience_type).all()
    
    def add_clause(self, clause):
        """Add a clause to this question"""
        if clause not in self.clauses:
            self.clauses.append(clause)
    
    def remove_clause(self, clause):
        """Remove a clause from this question"""
        if clause in self.clauses:
            self.clauses.remove(clause)