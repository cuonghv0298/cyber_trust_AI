from cnav.database.models import Base
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    DateTime,
    ForeignKey,
    Table,
    Enum,
    Numeric,
    Date,
    func
)
from sqlalchemy.orm import relationship

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Additional organization fields
    organisation_name = Column(String, nullable=False)
    acra_number_uen = Column(String, nullable=True)
    annual_turnover = Column(Numeric(precision=15, scale=2), nullable=True)
    number_of_employees = Column(Integer, nullable=True)
    date_of_self_assessment = Column(Date, nullable=True)
    scope_of_certification = Column(String, nullable=True)

    # one-to-many relationship to SelfAssessmentAnswer
    self_assessment_answers = relationship("SelfAssessmentAnswer", back_populates="organization")
    
    # One-to-many relationship with clause evaluations
    clause_evaluations = relationship("ClauseEvaluation", back_populates="organization")
    
    # One-to-many relationship with question evaluations  
    question_evaluations = relationship("QuestionEvaluation", back_populates="organization")