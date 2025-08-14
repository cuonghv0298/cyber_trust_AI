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

# Association table for many-to-many relationship between self_assessment_answers and clauses
self_assessment_answer_clause_mapping = Table(
    'self_assessment_answer_clause_mapping',
    Base.metadata,
    Column('self_assessment_answer_id', Integer, ForeignKey('self_assessment_answers.id'), primary_key=True),
    Column('clause_id', Integer, ForeignKey('clauses.id'), primary_key=True),
)

class SelfAssessmentAnswer(Base):
    __tablename__ = "self_assessment_answers"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Many-to-many relationship to the Clause
    clauses = relationship("Clause", secondary=self_assessment_answer_clause_mapping, back_populates="self_assessment_answers")

    # Many-to-one relationship to the Organization
    organization = relationship("Organization", back_populates="self_assessment_answers")

    # Many-to-one relationship to the Question
    question = relationship("Question", back_populates="self_assessment_answers")
    
    # One-to-many relationship with question evaluations
    question_evaluations = relationship("QuestionEvaluation", back_populates="self_assessment_answer")